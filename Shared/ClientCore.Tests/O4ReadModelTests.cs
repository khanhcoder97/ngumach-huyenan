// OPC-16 O4 — read model tests for combat HUD, TALK, portal, MAP_VIEWED and
// system messages. Fake adapters implement only the public adapter surface;
// no test helper mutates domain state or fabricates a server success.
// Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class O4ReadModelTests
    {
        private sealed class FakeCombatAdapter : IP1CombatHudAdapter
        {
            public UIConnectionState ConnectionState { get; set; } = UIConnectionState.Ready;
            public P1Self Self { get; set; }
            public P1World World { get; set; }
            public P1WorldV2 WorldV2 { get; set; }
            public bool UseWorldV2 { get; set; } = true;
            public IReadOnlyDictionary<string, string> CooldownEndsAtUtc { get; set; } =
                new Dictionary<string, string>(StringComparer.Ordinal);
            public bool HasPendingMutation { get; set; }
            public string LastErrorCode { get; set; }
            public P1Result BasicResult = P1Result.Ok();
            public P1Result CastResult = P1Result.Ok();
            public readonly List<(string target, double x, double y)> BasicCalls = new();
            public readonly List<(string skill, string target, double x, double y)> CastCalls = new();

            public Task<P1Result> BasicAttackAsync(string targetId, double aimX, double aimY, CancellationToken ct)
            {
                BasicCalls.Add((targetId, aimX, aimY));
                return Task.FromResult(BasicResult);
            }

            public Task<P1Result> CastAsync(string skillId, string targetId, double aimX, double aimY, CancellationToken ct)
            {
                CastCalls.Add((skillId, targetId, aimX, aimY));
                return Task.FromResult(CastResult);
            }
        }

        private sealed class FakeTalkAdapter : IP1TalkAdapter
        {
            public UIConnectionState ConnectionState { get; set; } = UIConnectionState.Ready;
            public bool HasPendingMutation { get; set; }
            public string LastErrorCode { get; set; }
            public P1QuestTalkResult LastTalk { get; set; }
            public P1WorldPortalResult LastPortal { get; set; }
            public P1QuestMapViewedResult LastMapViewed { get; set; }
            public P1Result TalkResult = P1Result.Ok();
            public P1Result PortalResult = P1Result.Ok();
            public P1Result MapViewedResult = P1Result.Ok();
            public bool NeedsResyncAfterSuccess { get; set; }
            public readonly List<(string npc, string node)> TalkCalls = new();
            public readonly List<string> PortalCalls = new();
            public readonly List<string> MapViewedCalls = new();

            public Task<P1Result> TalkAsync(string npcId, string nodeId, CancellationToken ct)
            {
                TalkCalls.Add((npcId, nodeId));
                if (TalkResult.Success && NeedsResyncAfterSuccess) ConnectionState = UIConnectionState.NeedsResync;
                return Task.FromResult(TalkResult);
            }

            public Task<P1Result> PortalAsync(string portalId, CancellationToken ct)
            {
                PortalCalls.Add(portalId);
                if (PortalResult.Success && NeedsResyncAfterSuccess) ConnectionState = UIConnectionState.NeedsResync;
                return Task.FromResult(PortalResult);
            }

            public Task<P1Result> MapViewedAsync(string questId, CancellationToken ct)
            {
                MapViewedCalls.Add(questId);
                if (MapViewedResult.Success && NeedsResyncAfterSuccess) ConnectionState = UIConnectionState.NeedsResync;
                return Task.FromResult(MapViewedResult);
            }
        }

        private static P1WorldV2 WorldV2(
            string targetHealth = "ALIVE", int targetHp = 1200, bool targetable = true, string targetKind = "BOSS")
        {
            return new P1WorldV2
            {
                schemaVersion = 2,
                mapId = "MAP_BEN_MUA",
                mapInstanceId = "MI_BEN_MUA_01",
                floorId = "F1",
                phase = "PVE",
                serverTimeUtc = "2026-11-07T00:00:00Z",
                serverTick = 500,
                revision = 9,
                audience = new P1Audience { aoiEnterWu = 40, aoiLeaveWu = 50 },
                self = new P1Self
                {
                    characterId = "CHR_TEST_A", classId = "CLASS_MINH_KIEM",
                    x = 18, y = 0, hp = 70, maxHp = 100, mp = 30, maxMp = 50, swordIntent = 2
                },
                entities = new[]
                {
                    new P1EntityV2
                    {
                        entityId = "ENT_BOSS_BM_05", kind = targetKind,
                        mapInstanceId = "MI_BEN_MUA_01", floorId = "F1", phase = "PVE",
                        state = targetHealth == "ALIVE" ? "ATTACK" : "DEAD",
                        healthState = targetHealth, targetable = targetable,
                        x = 10, y = 20, hp = targetHp, maxHp = 1200,
                        revision = 5, lifeId = 1, availability = "AVAILABLE"
                    }
                }
            };
        }

        private static P1QuestTalkResult TalkReceipt()
        {
            return new P1QuestTalkResult
            {
                questId = "P00-05",
                objectiveId = "OBJ_P00_05_CLASS_CONFIRM",
                npcId = "NPC_LYAN",
                nodeId = "DLG_P00_05_CLUE",
                credited = true,
                replayed = false,
                appliedFlag = "FLAG_TALK_01",
                eventId = "PQTALK_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                revision = 12
            };
        }

        private static P1WorldPortalResult PortalReceipt()
        {
            return new P1WorldPortalResult
            {
                portalId = "TP_BM_THANH_LAC",
                mapId = "MAP_THANH_LAC",
                xWu = 8,
                yWu = 0,
                applied = true,
                replayed = false,
                revision = 3,
                eventId = "P1PORTAL_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                inflightCastsCancelled = 1,
                reservedCountersCancelled = 0,
                guardWindowClosed = true
            };
        }

        private static P1QuestMapViewedResult MapViewedReceipt()
        {
            return new P1QuestMapViewedResult
            {
                questId = "P00-01",
                acknowledged = true,
                serverTick = 101,
                revision = 4
            };
        }

        [Fact]
        public void CombatHud_BuildsTargetAndServerIssuedCooldowns()
        {
            var adapter = new FakeCombatAdapter
            {
                WorldV2 = WorldV2(),
                CooldownEndsAtUtc = new Dictionary<string, string>(StringComparer.Ordinal)
                {
                    { "SK-MK-01", "2026-11-07T00:00:10Z" },
                    { "BASIC_ATTACK", "2026-11-06T23:59:00Z" }
                }
            };
            var presenter = new CombatHudPresenter(adapter);

            var view = presenter.SelectTarget("ENT_BOSS_BM_05");

            Assert.Equal(9, view.Revision);
            Assert.Equal(500, view.ServerTick);
            Assert.Equal(70, view.Hp);
            Assert.Equal(30, view.Mp);
            Assert.Equal(2, view.SwordIntent);
            Assert.NotNull(view.Target);
            Assert.Equal("ENT_BOSS_BM_05", view.Target.EntityId);
            Assert.True(view.Target.CanAttack);
            Assert.Equal(1.0, view.Target.HealthRatio, 3);
            Assert.True(view.CanBasicAttack);
            Assert.False(view.GetSkill("BASIC_ATTACK").IsOnCooldown);
            Assert.True(view.GetSkill("SK-MK-01").IsOnCooldown);
            Assert.Equal(10, view.GetSkill("SK-MK-01").RemainingSeconds);
            Assert.Contains("giây hồi chiêu", view.GetSkill("SK-MK-01").HintVi);
        }

        [Fact]
        public async Task CombatHud_RejectsDeadTargetAndUnsupportedSkillWithoutSending()
        {
            var adapter = new FakeCombatAdapter
            {
                WorldV2 = WorldV2("DEAD", 0, false)
            };
            var presenter = new CombatHudPresenter(adapter);

            var selected = presenter.SelectTarget("ENT_BOSS_BM_05");
            Assert.Null(selected.Target);
            Assert.Equal("invalid_target", selected.ErrorCode);

            var cast = await presenter.CastAsync("SK-MK-99", 0, 1, CancellationToken.None);
            Assert.Equal("unsupported_skill", cast.ErrorCode);

            var basic = await presenter.BasicAttackAsync(0, 1, CancellationToken.None);
            Assert.Equal("target_required", basic.ErrorCode);
            Assert.Empty(adapter.CastCalls);
            Assert.Empty(adapter.BasicCalls);
        }

        [Fact]
        public async Task CombatHud_CommandsUseSelectedTargetAndSurfaceServerResult()
        {
            var adapter = new FakeCombatAdapter
            {
                WorldV2 = WorldV2(),
                BasicResult = P1Result.Fail("feature_unavailable"),
                CastResult = P1Result.Ok()
            };
            var presenter = new CombatHudPresenter(adapter);
            presenter.SelectTarget("ENT_BOSS_BM_05");

            var basic = await presenter.BasicAttackAsync(0.25, 0.5, CancellationToken.None);

            Assert.Single(adapter.BasicCalls);
            Assert.Equal("ENT_BOSS_BM_05", adapter.BasicCalls[0].target);
            Assert.Equal(0.25, adapter.BasicCalls[0].x);
            Assert.Equal(0.5, adapter.BasicCalls[0].y);
            Assert.Equal("feature_unavailable", basic.ErrorCode);
            Assert.Contains("chưa được bật", basic.HintVi);

            var cast = await presenter.CastAsync("SK-MK-02", 0, 1, CancellationToken.None);

            Assert.Null(cast.ErrorCode);
            Assert.Single(adapter.CastCalls);
            Assert.Equal("SK-MK-02", adapter.CastCalls[0].skill);
            Assert.Equal("ENT_BOSS_BM_05", adapter.CastCalls[0].target);
        }

        [Fact]
        public async Task CombatHud_NoV2WorldDoesNotPretendBasicAttackIsAvailable()
        {
            var adapter = new FakeCombatAdapter
            {
                UseWorldV2 = false,
                Self = new P1Self { hp = 100, maxHp = 100, mp = 50, maxMp = 50 }
            };
            var presenter = new CombatHudPresenter(adapter);

            Assert.False(presenter.View.CanBasicAttack);
            var view = await presenter.BasicAttackAsync(0, 1, CancellationToken.None);
            Assert.Equal("feature_unavailable", view.ErrorCode);
            Assert.Empty(adapter.BasicCalls);
        }

        [Fact]
        public void TalkPresenter_ShowsServerReceiptAndNoRewardClaim()
        {
            var adapter = new FakeTalkAdapter { LastTalk = TalkReceipt() };
            var presenter = new TalkPresenter(adapter);

            Assert.True(presenter.View.HasReceipt);
            Assert.True(presenter.View.Credited);
            Assert.False(presenter.View.Replayed);
            Assert.Equal("P00-05", presenter.View.QuestId);
            Assert.Equal("OBJ_P00_05_CLASS_CONFIRM", presenter.View.ObjectiveId);
            Assert.Equal("FLAG_TALK_01", presenter.View.AppliedFlag);
            Assert.Equal("DLG_P00_05_CLUE", presenter.View.NodeId);
            Assert.Contains("không tự cấp thưởng", presenter.View.HintVi);
        }

        [Fact]
        public async Task TalkPresenter_UsesExplicitNpcAndNodeAndSurfacesDisabledRoute()
        {
            var adapter = new FakeTalkAdapter { TalkResult = P1Result.Fail("feature_unavailable", "corr-1") };
            var presenter = new TalkPresenter(adapter);

            var view = await presenter.TalkAsync("NPC_LYAN", "NODE_GREETING_01", CancellationToken.None);

            Assert.Single(adapter.TalkCalls);
            Assert.Equal(("NPC_LYAN", "NODE_GREETING_01"), adapter.TalkCalls[0]);
            Assert.Equal("feature_unavailable", view.ErrorCode);
            Assert.Equal("corr-1", view.CorrelationId);
            Assert.False(view.HasReceipt);
            Assert.Contains("chưa được bật", view.HintVi);

            var invalid = await presenter.TalkAsync(null, "NODE_GREETING_01", CancellationToken.None);
            Assert.Equal("invalid_input", invalid.ErrorCode);
            Assert.Single(adapter.TalkCalls);
        }

        [Fact]
        public async Task PortalPresenter_ShowsServerDestinationAndRequiresFreshWorld()
        {
            var adapter = new FakeTalkAdapter
            {
                LastPortal = PortalReceipt(),
                NeedsResyncAfterSuccess = true
            };
            var presenter = new PortalPresenter(adapter);

            var view = await presenter.RequestAsync("TP_BM_THANH_LAC", CancellationToken.None);

            Assert.Single(adapter.PortalCalls);
            Assert.Equal("TP_BM_THANH_LAC", view.PortalId);
            Assert.Equal("MAP_THANH_LAC", view.MapId);
            Assert.Equal(8, view.XWu);
            Assert.True(view.Applied);
            Assert.False(view.Replayed);
            Assert.Equal(1, view.InflightCastsCancelled);
            Assert.True(view.GuardWindowClosed);
            Assert.True(view.HasReceipt);
            Assert.True(view.RequiresWorldRefresh);
            Assert.False(view.CanRequest);
            Assert.Contains("không tự dịch chuyển", view.HintVi);

            adapter.ConnectionState = UIConnectionState.Ready; // fresh world read completed
            var ready = presenter.Refresh();
            Assert.False(ready.RequiresWorldRefresh);
            Assert.True(ready.CanRequest);
        }

        [Fact]
        public async Task MapViewedPresenter_AcknowledgesQuestAndSurfacesDisabledRoute()
        {
            var adapter = new FakeTalkAdapter { LastMapViewed = MapViewedReceipt() };
            var presenter = new MapViewedPresenter(adapter);

            var view = await presenter.AcknowledgeAsync("P00-01", CancellationToken.None);

            Assert.Single(adapter.MapViewedCalls);
            Assert.Equal("P00-01", view.QuestId);
            Assert.True(view.Acknowledged);
            Assert.True(view.HasReceipt);
            Assert.Contains("đã ghi nhận", view.HintVi);

            var disabledAdapter = new FakeTalkAdapter
            {
                MapViewedResult = P1Result.Fail("feature_unavailable", "corr-2")
            };
            var disabled = await new MapViewedPresenter(disabledAdapter)
                .AcknowledgeAsync("P00-01", CancellationToken.None);
            Assert.Equal("feature_unavailable", disabled.ErrorCode);
            Assert.Contains("chưa được bật", disabled.HintVi);
        }

        [Fact]
        public void SystemMessage_LocalizesDedupesAndBlocksCritical()
        {
            var presenter = new SystemMessagePresenter();

            var first = presenter.Push(SystemMessageSeverity.Error, "feature_unavailable");
            var duplicate = presenter.Push(SystemMessageSeverity.Error, "feature_unavailable");
            Assert.Same(first, duplicate);
            Assert.Single(presenter.Messages);
            Assert.Contains("chưa được bật", first.TextVi);

            var critical = presenter.PushResult(P1Result.Fail("session_expired", "corr-3"), "nói chuyện");
            Assert.Equal(SystemMessageSeverity.Critical, critical.Severity);
            Assert.True(critical.IsBlocking);
            Assert.True(presenter.HasBlocking);
            Assert.Contains("Không thể nói chuyện", critical.TextVi);
            Assert.Contains("đăng nhập lại", critical.TextVi);

            Assert.True(presenter.Dismiss(critical.Sequence));
            Assert.False(presenter.HasBlocking);
        }

        [Fact]
        public void SystemMessage_SuccessNoticeAndUnknownCodeStayExplicit()
        {
            var presenter = new SystemMessagePresenter();

            var ok = presenter.PushResult(P1Result.Ok(), "trang bị");
            Assert.Equal(SystemMessageSeverity.Info, ok.Severity);
            Assert.Contains("đã được máy chủ xác nhận", ok.TextVi);

            var unknown = presenter.PushResult(P1Result.Fail("new_server_error"), "mở túi");
            Assert.Contains("new_server_error", unknown.TextVi);
        }

        [Fact]
        public void SystemMessage_CapacityRemovesOldestAndBlockingCount()
        {
            var presenter = new SystemMessagePresenter(capacity: 2);
            presenter.Push(SystemMessageSeverity.Info, "one");
            presenter.Push(SystemMessageSeverity.Info, "two");
            var critical = presenter.Push(SystemMessageSeverity.Critical, "session_expired");
            presenter.Push(SystemMessageSeverity.Info, "four");
            presenter.Push(SystemMessageSeverity.Info, "five");

            Assert.Equal(2, presenter.Messages.Count);
            Assert.False(presenter.HasBlocking);
            Assert.DoesNotContain(presenter.Messages, m => m.Sequence == critical.Sequence);
        }
    }
}
