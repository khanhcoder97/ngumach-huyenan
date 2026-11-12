// OPC-16 O4 — read model tests for combat HUD, TALK, portal, MAP_VIEWED and
// system messages. Fake adapters implement only the public adapter surface;
// no test helper mutates domain state or fabricates a server success.
// Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.IO;
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

        private sealed class FakeUiAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState { get; set; } = UIConnectionState.Ready;
            public bool HasPendingMutation { get; set; }
            public string LastErrorCode { get; set; }
            public string LastCorrelationId { get; set; }
            public P1Self Self { get; set; }
            public P1World World { get; set; }
            public P1WorldV2 WorldV2 { get; set; }
            public P1Quest[] Quests { get; set; } = new P1Quest[0];
            public P1Inventory Inventory { get; set; }
            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> ReadWorldAsync(CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> AcceptQuestAsync(string questId, string npcId, CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> InteractAsync(string targetId, CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> TurnInQuestAsync(string questId, string npcId, CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> RetryPendingAsync(CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
        }

        private static P1WorldV2 EscortWorld(double npcX, bool includeNpc)
        {
            var self = new P1Self { characterId = "CHR_TEST_A", classId = "CLASS_MINH_KIEM", x = 82, y = 0, hp = 100, maxHp = 100, mp = 50, maxMp = 50, swordIntent = 0 };
            var entities = new List<P1EntityV2>();
            if (includeNpc)
                entities.Add(new P1EntityV2
                {
                    entityId = "ENT_NPC_LYAN_ESCORT", kind = "NPC",
                    mapInstanceId = "MI_BEN_MUA_01", floorId = "F1", phase = "PVE",
                    state = "ACTIVE", healthState = "INVULNERABLE", targetable = false,
                    x = npcX, y = 0, hp = 1, maxHp = 1, revision = 1, lifeId = 1, availability = "AVAILABLE"
                });
            return new P1WorldV2
            {
                schemaVersion = 2, mapId = "MAP_BEN_MUA", mapInstanceId = "MI_BEN_MUA_01",
                floorId = "F1", phase = "PVE", serverTimeUtc = "2026-11-07T00:00:00Z",
                serverTick = 500, revision = 9,
                audience = new P1Audience { aoiEnterWu = 40, aoiLeaveWu = 48 },
                self = self, entities = entities.ToArray()
            };
        }

        private static EscortPacket BoundEscortPacket(
            string owner = "CHR_TEST_A", string actor = "ENT_NPC_LYAN_ESCORT",
            string life = "ACTIVE", long attempt = 7, string instance = "MI_BEN_MUA_01",
            string floor = "F1", long sampleTick = 500, string mapId = "MAP_BEN_MUA",
            bool onRoad = true, string questId = "P00-04", string questStatus = "IN_PROGRESS")
        {
            return new EscortPacket(owner, actor, life, attempt, instance, floor, sampleTick,
                mapId, onRoad, questId, questStatus);
        }

        [Fact]
        public void Escort_NoPacketServesNothingEvenWithAudienceRow()
        {
            // gói39 O39-A: without an approved escort packet, a generic or
            // static audience NPC is never promoted to an escorted owner NPC
            // by substring or coordinate inference.
            var world = EscortWorld(90, true);
            var a = new FakeUiAdapter { WorldV2 = world, Self = world.self };
            var v = new EscortPresenter(a).Refresh();
            Assert.False(v.InAudience);
            Assert.False(v.IsOnRoad);
            Assert.Null(v.EntityId);
            Assert.Null(v.OwnerCharacterId);
            Assert.Equal(EscortProvenance.NotServed, v.Provenance);
            Assert.Equal("escort_packet_not_bound", v.NotServedReason);
            Assert.Equal("worldv2", v.SourceSnapshot);
            Assert.Equal("MAP_BEN_MUA", v.MapId);
            Assert.Equal(500, v.ServerTick);
        }

        [Fact]
        public void Escort_PacketBoundProjectsAudienceRowAsImmutableView()
        {
            var world = EscortWorld(90, true);
            var a = new FakeUiAdapter { WorldV2 = world, Self = world.self };
            var p = new EscortPresenter(a);
            p.BindEscortPacket(BoundEscortPacket());
            var v = p.Refresh();
            Assert.True(v.InAudience);
            Assert.Equal("ENT_NPC_LYAN_ESCORT", v.EntityId);
            Assert.Equal(90, v.X);
            Assert.True(v.IsOnRoad);
            Assert.Equal(8, v.DistanceToSelfWu);
            Assert.Equal(EscortProvenance.PacketBound, v.Provenance);
            Assert.Null(v.NotServedReason);
            Assert.Equal("worldv2", v.SourceSnapshot);
            Assert.Equal("CHR_TEST_A", v.OwnerCharacterId);
            Assert.Equal("ENT_NPC_LYAN_ESCORT", v.ActorEntityId);
            Assert.Equal("ACTIVE", v.LifeState);
            Assert.True(v.AttemptId == 7);
            Assert.Equal("MI_BEN_MUA_01", v.InstanceId);
            Assert.Equal("F1", v.FloorId);
            Assert.True(v.SampleTick == 500);
            Assert.Equal("P00-04", v.QuestId);
            Assert.Equal("IN_PROGRESS", v.QuestStatus);
            // Immutable snapshot: mutating the audience row afterwards does
            // not rewrite the published view.
            world.entities[0].x = 42;
            Assert.Equal(90, v.X);
        }

        [Fact]
        public void Escort_AbsentActorRowIsRejectedNotServed()
        {
            var world = EscortWorld(90, false);
            var a = new FakeUiAdapter { WorldV2 = world, Self = world.self };
            var p = new EscortPresenter(a);
            p.BindEscortPacket(BoundEscortPacket());
            var v = p.Refresh();
            Assert.False(v.InAudience);
            Assert.False(v.IsOnRoad);
            Assert.Equal(EscortProvenance.PacketRejected, v.Provenance);
            Assert.Equal("packet_actor_absent_in_audience", v.NotServedReason);
        }

        [Fact]
        public void Escort_V2AuthoritativeNeverMixesV1Row()
        {
            // gói39 O39-A probe: v2 ThanhLac/tick500 with no entities plus a
            // v1 BenMua/tick10 static LYAN row must never surface as an
            // escorted owner NPC under the v2 epoch. v1 rows are ignored
            // entirely while v2 is live.
            var v2 = new P1WorldV2
            {
                schemaVersion = 2, mapId = "MAP_THANH_LAC", mapInstanceId = "MI_THANH_LAC_01",
                floorId = "F1", phase = "PVE", serverTimeUtc = "2026-11-12T00:00:00Z",
                serverTick = 500, revision = 1,
                audience = new P1Audience { aoiEnterWu = 40, aoiLeaveWu = 48 },
                self = new P1Self { characterId = "CHR_TEST_A", classId = "CLASS_MINH_KIEM", x = 8, y = 0, hp = 100, maxHp = 100, mp = 50, maxMp = 50, swordIntent = 0 },
                entities = new P1EntityV2[0]
            };
            var v1 = new P1World
            {
                mapId = "MAP_BEN_MUA", serverTick = 10, revision = 1,
                self = new P1Self { characterId = "CHR_TEST_A", classId = "CLASS_MINH_KIEM", x = 82, y = 0, hp = 100, maxHp = 100, mp = 50, maxMp = 50, swordIntent = 0 },
                entities = new[] { new P1Entity { entityId = "ENT_NPC_LYAN_STATIC", kind = "NPC", x = 90, y = 0 } }
            };
            var a = new FakeUiAdapter { WorldV2 = v2, World = v1, Self = v2.self };
            var p = new EscortPresenter(a);
            var noPacket = p.Refresh();
            Assert.False(noPacket.InAudience);
            Assert.False(noPacket.IsOnRoad);
            Assert.Equal("MAP_THANH_LAC", noPacket.MapId);
            Assert.Equal(500, noPacket.ServerTick);
            Assert.Equal("worldv2", noPacket.SourceSnapshot);
            Assert.Equal(EscortProvenance.NotServed, noPacket.Provenance);

            // A packet forged for the old v1 row is rejected: wrong map and
            // stale sample tick against the live v2 epoch.
            p.BindEscortPacket(BoundEscortPacket(actor: "ENT_NPC_LYAN_STATIC", sampleTick: 10, mapId: "MAP_BEN_MUA"));
            var rejected = p.Refresh();
            Assert.False(rejected.InAudience);
            Assert.Equal("MAP_THANH_LAC", rejected.MapId);
            Assert.Equal(EscortProvenance.PacketRejected, rejected.Provenance);
            Assert.Equal("packet_map_mismatch", rejected.NotServedReason);
        }

        [Fact]
        public void Escort_V1LegacyEpochNeverBindsPacket()
        {
            // WorldV1 is a single legacy epoch used only when no v2 exists;
            // every field comes from that same epoch and escort packets
            // (a v2 route) never bind to it.
            var v1 = new P1World
            {
                mapId = "MAP_BEN_MUA", serverTick = 10, revision = 1,
                self = new P1Self { characterId = "CHR_TEST_A", classId = "CLASS_MINH_KIEM", x = 82, y = 0, hp = 100, maxHp = 100, mp = 50, maxMp = 50, swordIntent = 0 },
                entities = new[] { new P1Entity { entityId = "ENT_NPC_LYAN_ESCORT", kind = "NPC", x = 90, y = 0 } }
            };
            var a = new FakeUiAdapter { World = v1, Self = v1.self };
            var p = new EscortPresenter(a);
            var noPacket = p.Refresh();
            Assert.Equal("worldv1_legacy", noPacket.SourceSnapshot);
            Assert.Equal("MAP_BEN_MUA", noPacket.MapId);
            Assert.Equal(10, noPacket.ServerTick);
            Assert.False(noPacket.InAudience);
            Assert.Equal(EscortProvenance.NotServed, noPacket.Provenance);

            p.BindEscortPacket(BoundEscortPacket(sampleTick: 10));
            var rejected = p.Refresh();
            Assert.False(rejected.InAudience);
            Assert.Equal("worldv1_legacy", rejected.SourceSnapshot);
            Assert.Equal(EscortProvenance.PacketRejected, rejected.Provenance);
            Assert.Equal("packet_requires_worldv2", rejected.NotServedReason);
        }

        [Fact]
        public void Escort_PacketGuardsRejectStaleOwnerInstanceAndFloor()
        {
            var world = EscortWorld(90, true);
            var a = new FakeUiAdapter { WorldV2 = world, Self = world.self };
            var p = new EscortPresenter(a);

            p.BindEscortPacket(BoundEscortPacket(sampleTick: 499));
            var stale = p.Refresh();
            Assert.Equal(EscortProvenance.PacketRejected, stale.Provenance);
            Assert.Equal("packet_stale_sample", stale.NotServedReason);

            p.BindEscortPacket(BoundEscortPacket(owner: "CHR_FOREIGN"));
            var foreign = p.Refresh();
            Assert.Equal(EscortProvenance.PacketRejected, foreign.Provenance);
            Assert.Equal("packet_owner_mismatch", foreign.NotServedReason);

            p.BindEscortPacket(BoundEscortPacket(instance: "MI_OTHER"));
            var instance = p.Refresh();
            Assert.Equal(EscortProvenance.PacketRejected, instance.Provenance);
            Assert.Equal("packet_instance_mismatch", instance.NotServedReason);

            p.BindEscortPacket(BoundEscortPacket(floor: "F2"));
            var floor = p.Refresh();
            Assert.Equal(EscortProvenance.PacketRejected, floor.Provenance);
            Assert.Equal("packet_floor_mismatch", floor.NotServedReason);

            p.BindEscortPacket(BoundEscortPacket());
            var bound = p.Refresh();
            Assert.Equal(EscortProvenance.PacketBound, bound.Provenance);
            Assert.True(bound.InAudience);
        }

        private static bool Hex32(string s)
        {
            if (s == null || s.Length != 32) return false;
            foreach (char c in s) if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return false;
            return true;
        }

        private static void AssertTraceShape(P1EventV2[] trace, long firstCursor)
        {
            var ids = new HashSet<string>(StringComparer.Ordinal);
            long cursor = firstCursor - 1;
            foreach (var e in trace)
            {
                Assert.True(Hex32(e.eventId));
                Assert.True(Hex32(e.castId));
                Assert.True(ids.Add(e.eventId));
                Assert.True(e.cursor > cursor);
                Assert.True(e.serverTick >= 0);
                Assert.False(string.IsNullOrWhiteSpace(e.actorId));
                cursor = e.cursor;
            }
        }

        [Fact]
        public void Trace_HitDeathIsFullLifecycleAndDeterministic()
        {
            var trace = CombatTraceFactory.HitDeathTrace(
                CombatTraceFactory.Id(101), "CHR_TEST_A", "ENT_BOSS_BM_05");
            Assert.Equal(5, trace.Length);
            Assert.Equal(
                new[] { "CAST_START", "COUNTER_CONFIRMED", "IMPACT", "DEATH", "END" },
                Array.ConvertAll(trace, e => e.type));
            AssertTraceShape(trace, 1);
            Assert.True(trace[2].result != null && trace[2].result.hit);
            Assert.Equal(trace[2].result.amount, trace[2].result.absorbed + trace[2].result.hpDamage);
            var again = CombatTraceFactory.HitDeathTrace(
                CombatTraceFactory.Id(101), "CHR_TEST_A", "ENT_BOSS_BM_05");
            Assert.Equal(trace[0].eventId, again[0].eventId);
        }

        [Fact]
        public void Trace_MissTwoOwnersGapAndLateAreDistinct()
        {
            var miss = CombatTraceFactory.MissTrace(CombatTraceFactory.Id(201), "CHR_TEST_A", "ENT_BOSS_BM_05");
            Assert.Equal(3, miss.Length);
            Assert.False(miss[1].result.hit);
            Assert.Equal(0, miss[1].result.amount);
            AssertTraceShape(miss, 1);

            var two = CombatTraceFactory.TwoOwnersTrace();
            Assert.Equal(6, two.Length);
            AssertTraceShape(two, 1);
            Assert.Equal(2, new HashSet<string>(Array.ConvertAll(two, e => e.castId)).Count);

            var gap = CombatTraceFactory.GapTrace(CombatTraceFactory.Id(301), "CHR_TEST_A", "ENT_BOSS_BM_05");
            Assert.Equal(new long[] { 1, 5 }, Array.ConvertAll(gap, e => e.cursor));

            var late = CombatTraceFactory.LateImpactTrace(CombatTraceFactory.Id(401), "CHR_TEST_A", "ENT_BOSS_BM_05");
            AssertTraceShape(late, 1);
            Assert.True(late[1].serverTick < late[0].serverTick);

            var basic = CombatTraceFactory.BasicAttackSample();
            Assert.Equal("BASIC_ATTACK", basic.actionKind);
            Assert.Null(basic.skillId);
            var skill = CombatTraceFactory.SkillSample("SK-MK-02", "ENT_BOSS_BM_05");
            Assert.Equal("SK-MK-02", skill.skillId);
        }

        // ── gói39 O39-B: media bridge over the REAL Muse delivery ──
        // Fixtures under Fixtures/MuseMedia/ are byte copies from the Muse
        // branch (muse/media-production-20261104, pin b1472f2):
        // PLAYBACK_METADATA_v1.json (21 scenes) + CIN_000/CIN_001 SRT.

        private static string MuseMediaFixturePath(string name)
        {
            var relative = Path.Combine("Shared", "ClientCore.Tests", "Fixtures", "MuseMedia", name);
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            for (int depth = 0; dir != null && depth < 12; depth++, dir = dir.Parent)
            {
                var candidate = Path.Combine(dir.FullName, relative);
                if (File.Exists(candidate)) return candidate;
            }
            throw new FileNotFoundException("fixture not found: " + name);
        }

        /// <summary>The repo root doubles as the content root: canonical path
        /// containment is validated against it, exactly like a deployment.</summary>
        private static string MuseContentRoot()
        {
            var fixture = MuseMediaFixturePath("PLAYBACK_METADATA_v1.json");
            return Path.GetFullPath(Path.Combine(Path.GetDirectoryName(fixture), "..", "..", "..", ".."));
        }

        private static MediaMetadata MuseScene(string sceneId)
        {
            var doc = MediaMetadataLoader.LoadDocument(
                MuseContentRoot(),
                Path.Combine("Shared", "ClientCore.Tests", "Fixtures", "MuseMedia", "PLAYBACK_METADATA_v1.json"));
            Assert.True(doc.Success, doc.Error);
            for (int i = 0; i < doc.Scenes.Count; i++)
                if (doc.Scenes[i].SceneId == sceneId) return doc.Scenes[i];
            throw new InvalidOperationException("scene missing from fixture: " + sceneId);
        }

        /// <summary>Content root with the manifest's own directory layout:
        /// ClientGodot/assets/cinematics/CIN_00x/ hosts the real SRT bytes so
        /// the loader canonicalizes exactly like a deployment. Caller deletes.</summary>
        private static string MuseSrtContentRoot()
        {
            var root = Path.Combine(MuseContentRoot(), "TestResults",
                "MediaTests-" + Guid.NewGuid().ToString("N"));
            var cin000 = Path.Combine(root, "ClientGodot", "assets", "cinematics", "CIN_000");
            var cin001 = Path.Combine(root, "ClientGodot", "assets", "cinematics", "CIN_001");
            Directory.CreateDirectory(cin000);
            Directory.CreateDirectory(cin001);
            File.Copy(MuseMediaFixturePath("CIN_000_vi.srt"), Path.Combine(cin000, "CIN_000_vi.srt"));
            File.Copy(MuseMediaFixturePath("CIN_001_vi.srt"), Path.Combine(cin001, "CIN_001_vi.srt"));
            return root;
        }

        [Fact]
        public void MediaParser_LoadsActualMuseMetadata21Scenes()
        {
            var doc = MediaMetadataLoader.LoadDocument(
                MuseContentRoot(),
                Path.Combine("Shared", "ClientCore.Tests", "Fixtures", "MuseMedia", "PLAYBACK_METADATA_v1.json"));
            Assert.True(doc.Success, doc.Error);
            Assert.Equal(21, doc.Scenes.Count);
            Assert.Equal(21, doc.WithEmbeddedSoundtrack);
            Assert.Equal(0, doc.Silent);
            Assert.StartsWith("sha256:", doc.Provenance);
            Assert.Equal(64 + "sha256:".Length, doc.Provenance.IndexOf(" manifest=", StringComparison.Ordinal));
            Assert.Equal("NGM_PLAYBACK_METADATA_V1", doc.ManifestId);

            var cin000 = MuseScene("CIN_000");
            Assert.Equal("prologue", cin000.Kind);
            Assert.Equal(87.367, cin000.DurationSeconds, 3);
            Assert.True(cin000.HasEmbeddedSoundtrack);
            Assert.Equal("EMBEDDED_SOUNDTRACK_ONLY", cin000.AudioOwnership);
            Assert.Equal("vorbis", cin000.VideoOgv.AudioCodec);
            Assert.Equal(48000, cin000.VideoOgv.SampleRateHz);
            Assert.Equal(2, cin000.VideoOgv.Channels);
            Assert.Equal("aac", cin000.VideoMp4.AudioCodec);
            Assert.Equal(0, cin000.VideoOgv.SubtitleStreamsEmbedded);
            Assert.Equal("OVERLAY_SRT", cin000.Subtitle.Mode);
            Assert.False(cin000.Subtitle.BurnedIntoRuntimeVideo);
            Assert.Equal(6, cin000.Subtitle.CuesMeasured);
            Assert.Equal("ClientGodot/assets/cinematics/CIN_000/CIN_000_vi.srt", cin000.Subtitle.SrtPath);
            Assert.Equal("REVIEW_ONLY_NOT_RUNTIME", cin000.Subtitle.ReviewOnly.Status);
            Assert.EndsWith("_sub_vi.mp4", cin000.Subtitle.ReviewOnly.Mp4SubVi);
            Assert.Equal(3, cin000.RuntimeDeliveryPaths.Count);
            Assert.Contains("ClientGodot/assets/cinematics/CIN_000/CIN_000_640x360_30fps.mp4", cin000.RuntimeDeliveryPaths);

            var cin001 = MuseScene("CIN_001");
            Assert.Equal(36.0, cin001.DurationSeconds, 3);
            Assert.Null(cin001.Subtitle.ReviewOnly);
            Assert.NotNull(cin001.EmbeddedMixSourceWavPath);
            Assert.Equal("1463ce02d64fa35ba785c0911afdd6193fdafb697b6a3c4d52552516aa1e3320",
                cin001.EmbeddedMixSourceSha256);
            Assert.True(cin001.ExternalMixAlternates.Count > 0);
        }

        [Fact]
        public void MediaParser_RejectsBadManifestWithoutWidening()
        {
            Assert.Equal("invalid_json", MediaPlaybackMetadataParser.Parse(null).Error);
            Assert.Equal("invalid_json", MediaPlaybackMetadataParser.Parse("not json").Error);
            Assert.Equal("unsupported_manifest", MediaPlaybackMetadataParser.Parse("{}").Error);

            var raw = File.ReadAllText(MuseMediaFixturePath("PLAYBACK_METADATA_v1.json"));
            Assert.Equal("unsupported_manifest",
                MediaPlaybackMetadataParser.Parse(raw.Replace("NGM_PLAYBACK_METADATA_V1", "NGM_PLAYBACK_METADATA_V9")).Error);
            Assert.Equal("missing_scenes",
                MediaPlaybackMetadataParser.Parse("{\"manifestId\":\"NGM_PLAYBACK_METADATA_V1\"}").Error);
            Assert.Equal("counts_mismatch_scenesTotal",
                MediaPlaybackMetadataParser.Parse(raw.Replace("\"scenesTotal\": 21", "\"scenesTotal\": 22")).Error);
        }

        [Fact]
        public void MediaPathPolicy_RejectsTraversalAbsoluteAndUri()
        {
            var root = MuseContentRoot();
            Assert.Null(MediaPathPolicy.CanonicalizeRoot(null));
            Assert.Null(MediaPathPolicy.CanonicalizeRoot(""));
            Assert.Null(MediaPathPolicy.CanonicalizeRoot("file:///x"));
            Assert.Equal(Path.GetFullPath(root), MediaPathPolicy.CanonicalizeRoot(root));

            Assert.Null(MediaPathPolicy.TryCanonicalize(root, null));
            Assert.Null(MediaPathPolicy.TryCanonicalize(root, ""));
            Assert.Null(MediaPathPolicy.TryCanonicalize(root, "../../private.mp4"));
            Assert.Null(MediaPathPolicy.TryCanonicalize(root, "C:\\Windows\\system32\\evil.mp4"));
            Assert.Null(MediaPathPolicy.TryCanonicalize(root, "/absolute/evil.mp4"));
            Assert.Null(MediaPathPolicy.TryCanonicalize(root, "file:///etc/passwd"));
            Assert.Null(MediaPathPolicy.TryCanonicalize(root, "http://evil.example/x.mp4"));
            Assert.NotNull(MediaPathPolicy.TryCanonicalize(
                root, "ClientGodot/assets/cinematics/CIN_000/CIN_000_640x360_30fps.mp4"));
        }

        [Fact]
        public void Media_LoadActualSceneRejectsTraversalExternalMixAndReviewVariant()
        {
            // gói39 O39-B probe regressions: the old presenter accepted a
            // traversal path because a caller had allowlisted it, and accepted
            // a WAV mix file under EMBEDDED_SOUNDTRACK_ONLY. The typed rules
            // reject both without any substring matching.
            var root = MuseContentRoot();
            var p = new MediaPlaybackPresenter(root);
            var cin001 = MuseScene("CIN_001");

            Assert.False(p.Load(cin001, 36, codecSupported: true, requestedPath: "../../private.mp4"));
            Assert.Equal(MediaPlaybackPhase.Fallback, p.View.Phase);
            Assert.Equal("path_outside_content_root", p.View.FallbackReason);

            Assert.False(p.Load(cin001, 36, codecSupported: true,
                requestedPath: cin001.EmbeddedMixSourceWavPath));
            Assert.Equal("embedded_soundtrack_only", p.View.FallbackReason);

            Assert.False(p.Load(cin001, 36, codecSupported: true,
                requestedPath: cin001.ExternalMixAlternates[0].RuntimeCopyPath));
            Assert.Equal("embedded_soundtrack_only", p.View.FallbackReason);

            // Burned-subtitle review variant of CIN_000 never plays.
            var cin000 = MuseScene("CIN_000");
            Assert.False(p.Load(cin000, 87.367, codecSupported: true,
                requestedPath: cin000.Subtitle.ReviewOnly.Mp4SubVi));
            Assert.Equal("burned_subtitle_review_not_runtime", p.View.FallbackReason);

            // Default delivery (clean mp4 video) plays.
            Assert.True(p.Load(cin001, 36));
            Assert.Equal(MediaPlaybackPhase.Playing, p.View.Phase);
            Assert.Equal("CIN_001", p.View.SceneId);
        }

        [Fact]
        public void Media_CleanVideoSrtOverlayNoDoubleCaption()
        {
            var root = MuseSrtContentRoot();
            try
            {
                var cin000 = MuseScene("CIN_000");
                var srt = MediaMetadataLoader.LoadSrtCues(root, cin000);
                Assert.True(srt.Success, srt.Error);
                Assert.Equal(6, srt.Cues.Count);
                Assert.Equal(6, cin000.SubtitleCues.Count);

                var p = new MediaPlaybackPresenter(root);
                Assert.True(p.Load(cin000, 87.367));
                p.Seek(5.0);
                Assert.Contains("Xưa, Lạc Châu", p.View.CurrentSubtitle);
                p.Seek(20.0);
                Assert.Contains("Ba trăm năm trước", p.View.CurrentSubtitle);
                p.Seek(82.0);
                Assert.Contains("Đầu kia", p.View.CurrentSubtitle);

                // A burned subtitle track would double the captions: overlay off.
                var burnedJson = "{\"manifestId\":\"NGM_PLAYBACK_METADATA_V1\",\"scenes\":[{" +
                    "\"sceneId\":\"CIN_TEST\",\"kind\":\"campaign\",\"durationSeconds\":10," +
                    "\"hasEmbeddedSoundtrack\":true,\"audioOwnership\":\"EMBEDDED_SOUNDTRACK_ONLY\"," +
                    "\"video\":{\"ogv\":{\"path\":\"a.ogv\",\"durationSecondsMeasured\":10," +
                    "\"audioStream\":{\"codec\":\"vorbis\",\"sampleRateHz\":48000,\"channels\":2},\"subtitleStreamsEmbedded\":0}," +
                    "\"mp4\":{\"path\":\"a.mp4\",\"durationSecondsMeasured\":10," +
                    "\"audioStream\":{\"codec\":\"aac\",\"sampleRateHz\":48000,\"channels\":2},\"subtitleStreamsEmbedded\":0}}," +
                    "\"subtitle\":{\"mode\":\"OVERLAY_SRT\",\"burnedIntoRuntimeVideo\":true,\"srtPath\":\"a.srt\",\"cuesMeasured\":1}}]}";
                var burned = MediaPlaybackMetadataParser.Parse(burnedJson);
                Assert.True(burned.Success, burned.Error);
                var burnedScene = burned.Scenes[0];
                burnedScene.AttachCues(new[] { new MediaSubtitleCue(0, 5, "captions would double") });
                Assert.True(burnedScene.Subtitle.BurnedIntoRuntimeVideo);
                Assert.True(p.Load(burnedScene, 10));
                Assert.Equal("", p.View.CurrentSubtitle);
            }
            finally
            {
                Directory.Delete(root, true);
            }
        }

        [Fact]
        public void Media_PlayingSeekCueSeenAndSkipArePresentationOnly()
        {
            var root = MuseSrtContentRoot();
            try
            {
                var cin001 = MuseScene("CIN_001");
                var srt = MediaMetadataLoader.LoadSrtCues(root, cin001);
                Assert.True(srt.Success, srt.Error);
                Assert.Single(cin001.SubtitleCues);

                var p = new MediaPlaybackPresenter(root, reducedMotion: true);
                Assert.True(p.Load(cin001, 36));
                Assert.Equal(MediaPlaybackPhase.Playing, p.View.Phase);
                Assert.True(p.View.ReducedMotion);
                Assert.Equal("", p.View.CurrentSubtitle);
                p.Seek(25.0);
                Assert.Contains("Đầu kia", p.View.CurrentSubtitle);
                Assert.Equal(25.0, p.View.ElapsedSeconds);
                Assert.Equal(36.0, p.Seek(999));
                Assert.Equal(36.0, p.View.ElapsedSeconds);
                Assert.Equal(1.0, p.View.ProgressNormalized);
                p.Seek(5);
                p.End(skipped: true);
                Assert.True(p.View.HasSeen);
                Assert.True(p.View.WasSkipped);
                Assert.Equal(MediaPlaybackPhase.Ended, p.View.Phase);
                p.Rewatch();
                Assert.Equal(1, p.View.RewatchCount);
                Assert.False(p.View.WasSkipped);
                Assert.Equal(0.0, p.View.ElapsedSeconds);
            }
            finally
            {
                Directory.Delete(root, true);
            }
        }

        [Fact]
        public void Media_FallbackOnUnsupportedCodecAndBadPath()
        {
            var root = MuseContentRoot();
            var cin001 = MuseScene("CIN_001");

            var notAllowed = new MediaPlaybackPresenter(root);
            Assert.False(notAllowed.Load(cin001, 36, codecSupported: true,
                requestedPath: "ClientGodot/assets/cinematics/CIN_002/CIN_002_640x360_30fps.mp4"));
            Assert.Equal(MediaPlaybackPhase.Fallback, notAllowed.View.Phase);
            Assert.Equal("path_not_allowed", notAllowed.View.FallbackReason);

            // A VO take outside the manifest delivery set is not special: it
            // is just a path that never plays. No substring rule needed.
            var vo = new MediaPlaybackPresenter(root);
            Assert.False(vo.Load(cin001, 36, codecSupported: true,
                requestedPath: "ClientGodot/assets/audio/vo/VO_CIN001_S05_LYAN_draft_v1.wav"));
            Assert.Equal("path_not_allowed", vo.View.FallbackReason);

            var codec = new MediaPlaybackPresenter(root);
            Assert.False(codec.Load(cin001, 36, codecSupported: false,
                requestedPath: "ClientGodot/assets/cinematics/CIN_001/CIN_001_640x360_30fps.mp4"));
            Assert.Equal("unsupported_codec", codec.View.FallbackReason);
        }

        [Fact]
        public void MediaSrtParser_ParsesActualSrtAndRejectsMalformed()
        {
            var text = File.ReadAllText(MuseMediaFixturePath("CIN_000_vi.srt"));
            var parsed = MediaSrtParser.Parse(text);
            Assert.True(parsed.Success, parsed.Error);
            Assert.Equal(6, parsed.Cues.Count);
            Assert.Equal(1.4, parsed.Cues[0].StartSeconds, 3);
            Assert.Equal(17.912, parsed.Cues[0].EndSeconds, 3);
            Assert.Contains("Xưa, Lạc Châu", parsed.Cues[0].Text);
            for (int i = 1; i < parsed.Cues.Count; i++)
                Assert.True(parsed.Cues[i].StartSeconds >= parsed.Cues[i - 1].StartSeconds);

            Assert.Equal("srt_block_too_short", MediaSrtParser.Parse("hello").Error);
            Assert.Equal("srt_missing_index", MediaSrtParser.Parse("no index\n0 --> 1\ntext").Error);
            Assert.Equal("srt_bad_timestamp_line", MediaSrtParser.Parse("1\n00:00:00,000 extra\ntext").Error);
            Assert.Equal("srt_bad_timestamp", MediaSrtParser.Parse("1\nxx:00:00,000 --> 00:00:01,000\ntext").Error);
            Assert.Equal("srt_bad_range", MediaSrtParser.Parse("1\n00:00:05,000 --> 00:00:04,000\ntext").Error);
            Assert.Equal("srt_not_monotonic",
                MediaSrtParser.Parse("1\n00:00:10,000 --> 00:00:12,000\na\n\n2\n00:00:09,000 --> 00:00:11,000\nb").Error);
        }

        [Fact]
        public void MediaLoader_RejectsOutsideRootAndMissing()
        {
            var root = MuseContentRoot();
            Assert.Equal("metadata_path_outside_content_root",
                MediaMetadataLoader.LoadDocument(root, "../../outside.json").Error);
            Assert.Equal("metadata_file_missing",
                MediaMetadataLoader.LoadDocument(
                    root, Path.Combine("Shared", "ClientCore.Tests", "Fixtures", "MuseMedia", "missing.json")).Error);

            // Scenes for SRT-edge cases are built through the strict parser,
            // exactly like a real host would.
            string sceneJson(string srtPath) => "{\"manifestId\":\"NGM_PLAYBACK_METADATA_V1\",\"scenes\":[{" +
                "\"sceneId\":\"CIN_TEST\",\"kind\":\"campaign\",\"durationSeconds\":10," +
                "\"hasEmbeddedSoundtrack\":true,\"audioOwnership\":\"EMBEDDED_SOUNDTRACK_ONLY\"," +
                "\"video\":{\"ogv\":{\"path\":\"a.ogv\",\"durationSecondsMeasured\":10," +
                "\"audioStream\":{\"codec\":\"vorbis\",\"sampleRateHz\":48000,\"channels\":2},\"subtitleStreamsEmbedded\":0}," +
                "\"mp4\":{\"path\":\"a.mp4\",\"durationSecondsMeasured\":10," +
                "\"audioStream\":{\"codec\":\"aac\",\"sampleRateHz\":48000,\"channels\":2},\"subtitleStreamsEmbedded\":0}}," +
                "\"subtitle\":{\"mode\":\"OVERLAY_SRT\",\"burnedIntoRuntimeVideo\":false,\"srtPath\":\"" + srtPath +
                "\",\"cuesMeasured\":1}}]}";

            var outside = MediaPlaybackMetadataParser.Parse(sceneJson("../../outside.srt"));
            Assert.True(outside.Success, outside.Error);
            Assert.Equal("srt_path_outside_content_root",
                MediaMetadataLoader.LoadSrtCues(root, outside.Scenes[0]).Error);

            var missing = MediaPlaybackMetadataParser.Parse(
                sceneJson("Shared/ClientCore.Tests/Fixtures/MuseMedia/missing.srt"));
            Assert.True(missing.Success, missing.Error);
            Assert.Equal("srt_file_missing",
                MediaMetadataLoader.LoadSrtCues(root, missing.Scenes[0]).Error);
        }

        [Fact]
        public void MediaPresenter_RequiresCanonicalContentRoot()
        {
            Assert.Throws<ArgumentException>(() => new MediaPlaybackPresenter(null));
            Assert.Throws<ArgumentException>(() => new MediaPlaybackPresenter("file:///x"));
        }
    }
}
