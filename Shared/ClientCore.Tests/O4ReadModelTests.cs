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

        private static MediaMetadata SampleMedia()
        {
            return new MediaMetadata(
                "CIN_001",
                new[] { "Assets/Media/CIN_001.mp4" },
                true,
                new[]
                {
                    new MediaSubtitleCue(0, 10, "Bến Mưa lúc rạng đông..."),
                    new MediaSubtitleCue(10, 20, "Một phong thư lạ lạc giữa bến trúc.")
                });
        }

        [Fact]
        public void Media_PlayingSeekCueSeenAndSkipArePresentationOnly()
        {
            var p = new MediaPlaybackPresenter(reducedMotion: true);
            Assert.True(p.Load(SampleMedia(), 36));
            Assert.Equal(MediaPlaybackPhase.Playing, p.View.Phase);
            Assert.True(p.View.ReducedMotion);
            Assert.Equal("Bến Mưa lúc rạng đông...", p.View.CurrentSubtitle);
            p.Seek(12);
            Assert.Equal("Một phong thư lạ lạc giữa bến trúc.", p.View.CurrentSubtitle);
            Assert.Equal(12.0, p.View.ElapsedSeconds);
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

        [Fact]
        public void Media_FallbackOnUnsupportedCodecEmbeddedMixAndBadPath()
        {
            var notAllowed = new MediaPlaybackPresenter();
            Assert.False(notAllowed.Load(SampleMedia(), 36, codecSupported: true, requestedPath: "Assets/Media/other.mp4"));
            Assert.Equal(MediaPlaybackPhase.Fallback, notAllowed.View.Phase);
            Assert.Equal("path_not_allowed", notAllowed.View.FallbackReason);

            var vo = new MediaPlaybackPresenter();
            Assert.False(vo.Load(SampleMedia(), 36, codecSupported: true, requestedPath: "Assets/Media/vo_001.mp4"));
            Assert.Equal("embedded_soundtrack_only", vo.View.FallbackReason);

            var codec = new MediaPlaybackPresenter();
            Assert.False(codec.Load(SampleMedia(), 36, codecSupported: false, requestedPath: "Assets/Media/CIN_001.mp4"));
            Assert.Equal("unsupported_codec", codec.View.FallbackReason);
        }
    }
}
