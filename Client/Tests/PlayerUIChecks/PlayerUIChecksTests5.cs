// OPC-13 Package A — ModalOrchestrator tests: single Escape/Space owner across
// narrative, cinema, player panels and HUD modals. All fixtures SYNTHETIC; they
// probe the pure-C# orchestrator contract, NOT native VisualElement input
// (native remains UNVERIFIED until the Muse VM packet runs).
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 20).

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace PlayerUIChecks
{
    public class ModalOrchestratorTests
    {
        private sealed class SpyLayer
        {
            public bool Open;
            public int EscapeCalls;
            public int SpaceCalls;
            public Func<bool> ProbeOverride;
            public Func<bool> Probe() => ProbeOverride ?? (() => Open);
        }

        private static (ModalOrchestrator orchestrator, SpyLayer narrative, SpyLayer cinema, SpyLayer panels, SpyLayer audio, SpyLayer details) Build()
        {
            var narrative = new SpyLayer();
            var cinema = new SpyLayer();
            var panels = new SpyLayer();
            var audio = new SpyLayer();
            var details = new SpyLayer();
            var orchestrator = new ModalOrchestrator();
            // Same visual registration order as P1OnlinePanel.RegisterModalLayers().
            orchestrator.Register(
                narrative.Probe(), () => { if (narrative.Open) narrative.EscapeCalls++; }, false);
            orchestrator.Register(
                cinema.Probe(), () => { if (cinema.Open) cinema.EscapeCalls++; }, true,
                () => { if (cinema.Open) cinema.SpaceCalls++; });
            orchestrator.Register(
                panels.Probe(), () => { if (panels.Open) panels.EscapeCalls++; }, false);
            orchestrator.Register(
                audio.Probe(), () => { if (audio.Open) audio.EscapeCalls++; }, false);
            orchestrator.Register(
                details.Probe(), () => { if (details.Open) details.EscapeCalls++; }, false);
            return (orchestrator, narrative, cinema, panels, audio, details);
        }

        [Fact]
        public void Escape_ClosedEverything_RunsNoFallback()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            Assert.Equal(ModalLayer.None, orchestrator.DispatchEscape());
            Assert.Equal(0, narrative.EscapeCalls);
            Assert.Equal(0, cinema.EscapeCalls);
            Assert.Equal(0, panels.EscapeCalls);
            Assert.Equal(0, audio.EscapeCalls);
            Assert.Equal(0, details.EscapeCalls);
        }

        [Fact]
        public void Escape_CinemaOverPanel_OnePressSkipsCinemaOnly()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            cinema.Open = true;
            panels.Open = true;

            Assert.Equal(ModalLayer.Cinema, orchestrator.DispatchEscape());
            Assert.Equal(1, cinema.EscapeCalls);
            Assert.Equal(0, panels.EscapeCalls); // panel below must not close from the same press

            cinema.Open = false;
            Assert.Equal(ModalLayer.PlayerPanel, orchestrator.DispatchEscape());
            Assert.Equal(1, panels.EscapeCalls);
        }

        [Fact]
        public void Escape_NarrativeAboveCinema_OnePressOneBehavior()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            narrative.Open = true;
            cinema.Open = true;

            Assert.Equal(ModalLayer.Narrative, orchestrator.DispatchEscape());
            Assert.Equal(1, narrative.EscapeCalls);
            Assert.Equal(0, cinema.EscapeCalls); // AG89 finding: previously cinema also skipped on the same press
        }

        [Fact]
        public void Escape_PriorityChain_AudioThenDetails()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            details.Open = true;
            audio.Open = true;
            panels.Open = true;

            Assert.Equal(ModalLayer.PlayerPanel, orchestrator.DispatchEscape());
            panels.Open = false;
            Assert.Equal(ModalLayer.AudioPanel, orchestrator.DispatchEscape());
            audio.Open = false;
            Assert.Equal(ModalLayer.HudDetails, orchestrator.DispatchEscape());
            details.Open = false;
            Assert.Equal(ModalLayer.None, orchestrator.DispatchEscape());
        }

        [Fact]
        public void Space_CinemaSkips_GameplayFallthroughOtherwise()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();

            // No modal → fall through to gameplay attack.
            Assert.Equal(ModalLayer.None, orchestrator.DispatchSpace());
            Assert.Equal(0, cinema.SpaceCalls);

            // Panel-only open: the topmost open layer (PlayerPanel) does not consume
            // Space, so it BLOCKS Space from reaching any lower layer — no fall-through
            // to gameplay/cinema behind it. (OPC-14 M0 / OPCREV-01: blocked ≠ consumed.)
            panels.Open = true;
            Assert.Equal(ModalLayer.PlayerPanel, orchestrator.DispatchSpace());
            Assert.Equal(0, cinema.SpaceCalls);

            // Cinematic playing → one Space skips cinema.
            cinema.Open = true;
            Assert.Equal(ModalLayer.Cinema, orchestrator.DispatchSpace());
            Assert.Equal(1, cinema.SpaceCalls);
        }

        [Fact]
        public void Space_TopmostOpenLayer_BlocksLowerConsumingLayer()
        {
            // OPC-14 M0 / OPCREV-01 regression: a topmost open layer that does NOT
            // consume Space must block Space from reaching a consuming layer behind it
            // (no fall-through, no skip of cinema behind a narrative modal).
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            narrative.Open = true;
            cinema.Open = true;

            Assert.Equal(ModalLayer.Narrative, orchestrator.DispatchSpace());
            Assert.Equal(0, cinema.SpaceCalls); // cinema behind a narrative modal must not skip
            Assert.Equal(0, narrative.SpaceCalls); // narrative does not consume Space

            // When the topmost layer is removed, Space reaches cinema.
            narrative.Open = false;
            Assert.Equal(ModalLayer.Cinema, orchestrator.DispatchSpace());
            Assert.Equal(1, cinema.SpaceCalls);
        }

        [Fact]
        public void Space_NoOpenLayer_FallsThroughToGameplay()
        {
            // OPC-14 M0: no modal open → None (fall-through to gameplay attack gate).
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            Assert.Equal(ModalLayer.None, orchestrator.DispatchSpace());
            Assert.Equal(0, cinema.SpaceCalls);
        }

        [Fact]
        public void BrokenProbe_DispatchesPastIt_WithoutThrowing()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            cinema.ProbeOverride = () => throw new InvalidOperationException("broken probe (synthetic)");
            panels.Open = true;
            Assert.Equal(ModalLayer.PlayerPanel, orchestrator.DispatchEscape());
            Assert.Equal(1, panels.EscapeCalls);
        }

        [Fact]
        public void IsAnyOpen_ReflectsLiveProbes()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            Assert.False(orchestrator.IsAnyOpen);
            audio.Open = true;
            Assert.True(orchestrator.IsAnyOpen);
        }

        [Fact]
        public void Lifecycle_200Cycles_EachPressConsumesExactlyOneLayer()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            for (int cycle = 0; cycle < 200; cycle++)
            {
                // A cinematic starts over an open panel (story flow timing is out of scope here).
                panels.Open = true;
                cinema.Open = true;
                Assert.Equal(ModalLayer.Cinema, orchestrator.DispatchEscape());
                cinema.Open = false;

                Assert.Equal(ModalLayer.PlayerPanel, orchestrator.DispatchEscape());
                panels.Open = false;

                // A one-off HUD details panel above.
                details.Open = true;
                Assert.Equal(ModalLayer.HudDetails, orchestrator.DispatchEscape());
                details.Open = false;

                // Nothing open → falls through, no handler runs.
                Assert.Equal(ModalLayer.None, orchestrator.DispatchEscape());
                Assert.Equal(ModalLayer.None, orchestrator.LastConsumedEscape);
                Assert.True(cinema.EscapeCalls >= cycle);
            }
            Assert.Equal(200, panels.EscapeCalls);
            Assert.Equal(200, cinema.EscapeCalls);
            Assert.Equal(200, details.EscapeCalls);
            Assert.Equal(0, narrative.EscapeCalls);
            Assert.Equal(0, audio.EscapeCalls);
        }

        [Fact]
        public void Register_RequiresSpaceBehavior_WhenConsumingSpace()
        {
            var orchestrator = new ModalOrchestrator();
            Assert.Throws<ArgumentException>(() => orchestrator.Register(() => false, () => { }, consumesSpace: true));
            Assert.Throws<ArgumentNullException>(() => orchestrator.Register(null, () => { }, false));
            Assert.Throws<ArgumentNullException>(() => orchestrator.Register(() => false, null, false));
        }
    }

    // ── OPC-13 Package B — NPC dialogue snapshot-only route ───────────────────
    // SYNTHETIC fixtures: the closed /p1/world/interact contract must never receive
    // an NPC; dialogue composes from the world/quest snapshot; canonical accept/
    // turn-in commands keep their NPC template IDs.

    public class NpcSnapshotRouteTests
    {
        private sealed class SpyAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState { get; set; } = UIConnectionState.Ready;
            public bool HasPendingMutation { get; set; }
            public string LastErrorCode => null;
            public string LastCorrelationId => null;
            public P1Self Self => new P1Self { characterId = "CHAR_1", classId = "CLASS_MINH_KIEM", x = 1, y = 2, hp = 100, maxHp = 100, mp = 20, maxMp = 20 };
            public bool UseV2 { get; set; } = true;

            private P1Entity[] _entities;
            private P1EntityV2[] _v2Entities;
            private static P1EntityV2 ToV2(P1Entity e) => new P1EntityV2
            {
                entityId = e.entityId,
                kind = e.kind,
                state = "ALIVE",
                mapInstanceId = "MI_1",
                floorId = "F_1",
                phase = "OPEN",
                healthState = "OK",
                targetable = true,
                x = e.x,
                y = e.y,
                hp = 100,
                maxHp = 100,
                revision = 1,
                lifeId = 1
            };

            /// <summary>SYNTHETIC world entity list; projects the same entity IDs into both the v1 and v2 views.</summary>
            public P1Entity[] WorldEntities
            {
                get => _entities;
                set
                {
                    _entities = value;
                    _v2Entities = value == null ? null : Array.ConvertAll(value, ToV2);
                }
            }

            public P1World World
            {
                get
                {
                    if (_entities == null || UseV2) return null;
                    return new P1World { mapId = "MAP_BEN_MUA", entities = _entities };
                }
            }
            public P1WorldV2 WorldV2
            {
                get
                {
                    if (_v2Entities == null || !UseV2) return null;
                    return new P1WorldV2
                    {
                        mapId = "MAP_BEN_MUA",
                        entities = _v2Entities
                    };
                }
            }
            public P1Quest[] Quests { get; set; } = Array.Empty<P1Quest>();
            public P1Inventory Inventory { get; set; }

            public int InteractCalls { get; private set; }
            public int AcceptCalls { get; private set; }
            public int TurnInCalls { get; private set; }
            public string LastAcceptedNpcId { get; private set; }
            public string LastTurnInNpcId { get; private set; }

            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> AcceptQuestAsync(string q, string n, CancellationToken ct)
            { AcceptCalls++; LastAcceptedNpcId = n; return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> InteractAsync(string t, CancellationToken ct)
            { InteractCalls++; return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct)
            { TurnInCalls++; LastTurnInNpcId = n; return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
        }

        private static P1Quest Quest(string state, int counters) => new P1Quest
        {
            questId = "P00-01",
            state = state,
            stepId = "STEP_BEN_MUA",
            revision = 1,
            objectiveCounters = new Dictionary<string, int> { ["OBJ_P00_01_PACKAGES"] = counters }
        };

        [Fact]
        public async Task OpenSnapshot_RegisteredNpc_NoWirePost_BuildsChoices()
        {
            var adapter = new SpyAdapter
            {
                WorldEntities = new[] { new P1Entity { entityId = "ENT_MAN_BM_NPC_LYAN", kind = "NPC", x = 5, y = 5 } },
                Quests = new[] { Quest("AVAILABLE", 0) }
            };
            var presenter = new NpcDialoguePresenter(adapter);

            var state = await presenter.OpenSnapshotAsync("ENT_MAN_BM_NPC_LYAN", CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.True(state.Value.IsAvailable);
            Assert.Equal("NPC_LYAN", state.Value.NpcTemplateId);
            Assert.Equal("ENT_MAN_BM_NPC_LYAN", state.Value.InteractionTargetEntityId);
            Assert.Contains(state.Value.Choices, c => c.ActionType == DialogueActionType.AcceptQuest && c.Enabled);
            Assert.Equal(0, adapter.InteractCalls); // ĐÓNG băng: NPC không đi qua world/interact.
        }

        [Fact]
        public async Task OpenSnapshot_UnregisteredNpc_MarksUnresolved_NoForcedDialogue()
        {
            var adapter = new SpyAdapter();
            var presenter = new NpcDialoguePresenter(adapter);

            var state = await presenter.OpenSnapshotAsync("ENT_MAN_BM_NPC_UNKNOWN_X", CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.False(state.Value.IsAvailable);
            Assert.Contains("UNRESOLVED", state.Value.UnavailableReason);
            Assert.Empty(state.Value.Choices);
            Assert.Equal(0, adapter.InteractCalls);
        }

        [Fact]
        public async Task OpenSnapshot_EntityMissingFromWorld_MarksUnavailable()
        {
            var adapter = new SpyAdapter
            {
                WorldEntities = new[] { new P1Entity { entityId = "ENT_OTHER", kind = "NPC", x = 1, y = 1 } },
                Quests = new[] { Quest("AVAILABLE", 0) }
            };
            var presenter = new NpcDialoguePresenter(adapter);

            var state = await presenter.OpenSnapshotAsync("ENT_MAN_BM_NPC_LYAN", CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.False(state.Value.IsAvailable);
            Assert.DoesNotContain(state.Value.Choices, c => c.Enabled && c.ActionType == DialogueActionType.AcceptQuest);
            Assert.Equal(0, adapter.InteractCalls);
        }

        [Fact]
        public async Task SnapshotChoices_KeepCanonicalWireCommands()
        {
            var adapter = new SpyAdapter { Quests = new[] { Quest("READY_TO_TURN_IN", 3) } };
            var presenter = new NpcDialoguePresenter(adapter);

            await presenter.OpenSnapshotAsync("ENT_MAN_BM_NPC_TA_VAN_KHANH", CancellationToken.None);
            Assert.Contains(presenter.State.Value.Choices, c => c.ActionType == DialogueActionType.TurnInQuest && c.Enabled);

            await presenter.TurnInQuestAsync("P00-01", "ENT_MAN_BM_NPC_TA_VAN_KHANH", CancellationToken.None);
            Assert.Equal("NPC_TA_VAN_KHANH", adapter.LastTurnInNpcId); // canonical, không phải entity ID
            Assert.Equal(0, adapter.InteractCalls);
            Assert.Equal(1, adapter.TurnInCalls);
        }

        [Fact]
        public async Task WireInteract_RemainsValidForNodes_RejectsNpcIds()
        {
            var adapter = new SpyAdapter
            {
                WorldEntities = new[] { new P1Entity { entityId = "ENT_MAN_BM_NODE_FLOWER", kind = "GATHER_NODE", x = 2, y = 2 } }
            };
            var presenter = new NpcDialoguePresenter(adapter);

            await presenter.InteractAsync("ENT_MAN_BM_NODE_FLOWER", CancellationToken.None);
            Assert.Equal(1, adapter.InteractCalls);

            await Assert.ThrowsAsync<InvalidOperationException>(
                () => presenter.InteractAsync("ENT_MAN_BM_NPC_LYAN", CancellationToken.None));
        }
    }

    // ── OPC-13 Package B2 — journal tracker pin/unpin + live objective wiring ──
    // SYNTHETIC fixtures: pure-C# presenter contract — HUD Tracker update logic
    // (signature detection) runs in PlayerUIRoot and is only syntax-verified.

    public class QuestTrackerLiveWiringTests
    {
        private static P1Quest Quest(string state, long revision, int packages) => new P1Quest
        {
            questId = "P00-01",
            state = state,
            stepId = "STEP_BEN_MUA",
            revision = revision,
            objectiveCounters = new Dictionary<string, int> { ["OBJ_P00_01_PACKAGES"] = packages }
        };

        [Fact]
        public async Task TogglePin_PinThenUnpin_Roundtrip()
        {
            var adapter = new FakeAdapter { Quests = new[] { Quest("ACTIVE", 1, 1) } };
            var presenter = new QuestJournalPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            presenter.TogglePin("P00-01");
            Assert.True(presenter.State.Value.HasPinnedTracker);
            Assert.Equal("P00-01", presenter.State.Value.PinnedQuestId);
            Assert.NotNull(presenter.State.Value.PinnedQuest);

            presenter.TogglePin("P00-01");
            Assert.False(presenter.State.Value.HasPinnedTracker);
            Assert.Null(presenter.State.Value.PinnedQuestId);
        }

        [Fact]
        public async Task RefreshFromSnapshot_LiveObjective_RebuiltWithoutWire()
        {
            var adapter = new FakeAdapter { Quests = new[] { Quest("ACTIVE", 1, 0) } };
            var presenter = new QuestJournalPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);
            presenter.TogglePin("P00-01");

            // Session advances the objective server-side; the client snapshot arrives via poll.
            adapter.Quests = new[] { Quest("ACTIVE", 2, 2) };
            var readCalls = 0;
            adapter.OnReadQuests = () => { readCalls++; return Task.FromResult(P1Result.Ok()); };

            presenter.RefreshFromSnapshot();

            Assert.Equal(0, readCalls); // refresh is local-only: no wire round trip
            var pinned = presenter.State.Value.PinnedQuest;
            Assert.NotNull(pinned);
            Assert.Contains("2/3", pinned.ObjectiveDesc);
            Assert.Equal("P00-01", presenter.State.Value.PinnedQuestId); // pin survives refresh
        }

        [Fact]
        public async Task RefreshFromSnapshot_PinCompletes_TrackerDropsStalePinnedQuest()
        {
            var adapter = new FakeAdapter { Quests = new[] { Quest("ACTIVE", 1, 3) } };
            var presenter = new QuestJournalPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);
            presenter.TogglePin("P00-01");
            Assert.NotNull(presenter.State.Value.PinnedQuest);

            // The pinned quest completes; server snapshot no longer lists it as active.
            adapter.Quests = new[] { Quest("COMPLETED", 3, 3) };
            presenter.RefreshFromSnapshot();

            // Tracker must not render stale objectives for a finished quest; the pin id is
            // retained so re-loading the journal still remembers the last tracked quest.
            Assert.Null(presenter.State.Value.PinnedQuest);
            Assert.Equal("P00-01", presenter.State.Value.PinnedQuestId);
        }

        [Fact]
        public void RefreshFromSnapshot_BeforeAnyJournalLoad_IsNoop()
        {
            var adapter = new FakeAdapter { Quests = new[] { Quest("ACTIVE", 1, 1) } };
            var presenter = new QuestJournalPresenter(adapter);

            // No journal state yet — refresh must not force a phantom load.
            presenter.RefreshFromSnapshot();
            Assert.Equal(LoadPhase.Idle, presenter.State.Phase);
            Assert.Null(presenter.State.Value);
        }

        [Fact]
        public async Task TogglePin_AllowedWhilePendingMutation_LocalOnly()
        {
            var adapter = new FakeAdapter { Quests = new[] { Quest("ACTIVE", 1, 1) }, HasPendingMutation = true };
            var presenter = new QuestJournalPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            // Pin persists a pure local view toggle (no wire command), so a pending server
            // mutation must not block or alter it.
            presenter.TogglePin("P00-01");
            Assert.True(presenter.State.Value.HasPinnedTracker);
            Assert.Equal("P00-01", presenter.State.Value.PinnedQuestId);
        }
    }

    // ── OPC-13 Package B3 — bag/character tooltip metadata via the real catalog ──

    public class BagTooltipMetadataTests
    {
        private static ItemSlotView Slot(string templateId, int stack = 1, int durability = 100, int version = 1, string location = "BAG") =>
            Slot(v => { v.templateId = templateId; v.stack = stack; v.durability = durability; v.version = version; v.location = location; });

        private static ItemSlotView Slot(Action<P1Item> mut)
        {
            var item = new P1Item { instanceId = "iid_1", templateId = "X", stack = 1, location = "BAG", durability = 100, version = 1 };
            mut(item);
            return new ItemSlotView(item);
        }

        [Fact]
        public void Format_KnownTemplate_ShowsCatalogMetadataAndProvenance()
        {
            var item = Slot(v => { v.templateId = "EQ-MK-WEAPON-T1"; v.stack = 2; v.durability = 77; });
            var tooltip = ItemTooltipFormatter.Format(item, ItemMetadataResolver.Resolve("EQ-MK-WEAPON-T1"));

            Assert.Contains("Kiếm Mưa Khởi Minh Kiếm", tooltip);
            Assert.Contains("Phẩm chất: Thường", tooltip);
            Assert.Contains("Loại: Trang bị / vũ khí", tooltip);
            Assert.Contains("Cấp yêu cầu: 1", tooltip);
            Assert.Contains("Số lượng: ×2", tooltip);
            Assert.Contains("Độ bền: 77/100", tooltip);
            Assert.Contains("Item_Master_Catalog_vi.csv", tooltip); // provenance line present
        }

        [Fact]
        public void Format_RarityVariant_CarriesVariantRarityAndVariantProvenance()
        {
            var item = Slot(v => { v.templateId = "EQ-MK-WEAPON-T1-R-REFINED"; });
            var meta = ItemMetadataResolver.Resolve("EQ-MK-WEAPON-T1-R-REFINED");

            Assert.Equal("Tinh Kiếm Mưa Khởi Minh Kiếm", meta.DisplayName);
            Assert.Equal("Tinh", meta.Rarity);

            var tooltip = ItemTooltipFormatter.Format(item, meta);
            Assert.Contains("Tinh Kiếm Mưa Khởi Minh Kiếm", tooltip);
            Assert.Contains("Item_Rarity_Variant_Catalog_vi.csv", tooltip); // variant source recorded
        }

        [Fact]
        public void Format_UnknownTemplate_CleanFallback_NoRawUnresolvedLeak()
        {
            var item = Slot(v => { v.templateId = "TPL_UNKNOWN_XYZ"; });
            var meta = ItemMetadataResolver.Resolve("TPL_UNKNOWN_XYZ");

            // Unknown templates never inherit a known slot or class.
            Assert.Null(meta.Slot);
            Assert.Null(meta.ClassId);
            Assert.Equal("TPL_UNKNOWN_XYZ", meta.DisplayName);

            var tooltip = ItemTooltipFormatter.Format(item, meta);
            Assert.DoesNotContain("UNRESOLVED", tooltip);
            Assert.Contains("TPL_UNKNOWN_XYZ", tooltip);
        }

        [Fact]
        public void Format_NullSlotItem_Throws()
        {
            Assert.Throws<ArgumentNullException>(() => ItemTooltipFormatter.Format(null, ItemMetadataResolver.Resolve("EQ-MK-WEAPON-T1")));
        }

        [Fact]
        public void SlotLabel_Stacking_SuffixOnlyWhenStacked()
        {
            var single = Slot(v => { v.templateId = "EQ-MK-WEAPON-T1"; });
            var stacked = Slot(v => { v.templateId = "EQ-MK-WEAPON-T1"; v.stack = 12; });

            Assert.Equal("Kiếm Mưa Khởi Minh Kiếm", ItemTooltipFormatter.SlotLabel(single, ItemMetadataResolver.Resolve("EQ-MK-WEAPON-T1")));
            Assert.Equal("Kiếm Mưa Khởi Minh Kiếm ×12", ItemTooltipFormatter.SlotLabel(stacked, ItemMetadataResolver.Resolve("EQ-MK-WEAPON-T1")));
        }
    }

    public class ItemCatalogParityTests
    {
        /// <summary>Locates the canonical production CSV by walking up from the test binary —
        /// the only file source allowed here; the running game client keeps using the
        /// embedded resolver snapshot (no runtime file IO in Unity).
        /// </summary>
        private static string FindCatalogCsv()
        {
            var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
            for (int i = 0; i < 12 && dir != null; i++, dir = dir.Parent)
            {
                var candidate = System.IO.Path.Combine(dir.FullName, "docs", "production", "Item_Master_Catalog_vi.csv");
                if (System.IO.File.Exists(candidate)) return candidate;
            }
            return null;
        }

        /// <summary>Parity check: the embedded resolver snapshot must never drift from the canonical production CSV.</summary>
        [Fact]
        public void EmbeddedCatalog_MatchesCanonicalMasterCsv()
        {
            string csvPath = FindCatalogCsv();
            if (csvPath == null)
            {
                throw new InvalidOperationException("canonical Item_Master_Catalog_vi.csv not found from test base dir — environment SYNTHETIC check failed");
            }

            var rows = new Dictionary<string, (string name, string category, string level)>(StringComparer.OrdinalIgnoreCase);
            foreach (var line in System.IO.File.ReadAllLines(csvPath))
            {
                if (string.IsNullOrWhiteSpace(line) || line.StartsWith("\"item_id\"", StringComparison.OrdinalIgnoreCase)) continue;
                var fields = ParseLineQuoted(line);
                if (fields == null || fields.Count < 7) continue;
                rows[fields[0]] = (fields[1], fields[2], fields[6].Trim());
            }

            Assert.True(rows.Count > 0, "master catalog CSV parsed empty");

            // Every embedded resolver entry must exist in the canonical CSV with the same
            // display name and required level — drift in either direction fails this check.
            foreach (var meta in ItemMetadataResolver.Registered)
            {
                Assert.True(rows.TryGetValue(meta.TemplateId, out var row),
                    $"embedded catalog entry {meta.TemplateId} is missing from Item_Master_Catalog_vi.csv");
                Assert.Equal(row.name, meta.DisplayName);
                Assert.Equal(row.level, meta.RequiredLevel.ToString());
            }
        }

        private static List<string> ParseLineQuoted(string line)
        {
            var fields = new List<string>();
            var f = new System.Text.StringBuilder();
            bool inQuotes = false;
            for (int i = 0; i < line.Length; i++)
            {
                char c = line[i];
                if (inQuotes)
                {
                    if (c == '"')
                    {
                        if (i + 1 < line.Length && line[i + 1] == '"') { f.Append('"'); i++; }
                        else inQuotes = false;
                    }
                    else f.Append(c);
                }
                else if (c == '"') inQuotes = true;
                else if (c == ',') { fields.Add(f.ToString()); f.Clear(); }
                else f.Append(c);
            }
            fields.Add(f.ToString());
            return fields;
        }
    }

    // ── OPC-13 Package C — map pan/zoom/clamp, HUD safe-area, settings reopen ──
    // SYNTHETIC fixtures: pure-C# presenter/policy contracts. Native drag gesture,
    // safe-area readings and UIDocument scale application are UNVERIFIED_NATIVE.

    public class MapPanZoomTests
    {
        private sealed class MapSpyAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState { get; set; } = UIConnectionState.Ready;
            public bool HasPendingMutation { get; set; }
            public string LastErrorCode => null;
            public string LastCorrelationId => null;
            public P1Self Self { get; set; }
            public P1World World { get; set; }
            public P1WorldV2 WorldV2 { get; set; }
            public P1Inventory Inventory { get; set; }
            public P1Quest[] Quests { get; set; } = Array.Empty<P1Quest>();
            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> AcceptQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> InteractAsync(string target, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
        }

        private static IP1UIAdapter V2Adapter(double x, double y, string mapId = "MAP_BEN_MUA") => new MapSpyAdapter
        {
            WorldV2 = new P1WorldV2
            {
                mapId = mapId,
                self = new P1Self { characterId = "P1", classId = "CLASS_MINH_KIEM", x = x, y = y, hp = 100, maxHp = 100, mp = 50, maxMp = 50 },
                entities = Array.Empty<P1EntityV2>()
            }
        };

        [Fact]
        public void Refresh_PrefersWorldV2_OverV1()
        {
            var adapter = new MapSpyAdapter
            {
                World = new P1World
                {
                    mapId = "MAP_V1_OLD",
                    self = new P1Self { characterId = "P1", x = 1, y = 1 },
                    entities = Array.Empty<P1Entity>()
                },
                WorldV2 = new P1WorldV2
                {
                    mapId = "MAP_BEN_MUA",
                    self = new P1Self { characterId = "P1", x = 5, y = 5 },
                    entities = Array.Empty<P1EntityV2>()
                }
            };
            var presenter = new MapPresenter(adapter);
            presenter.Refresh();

            Assert.Equal("MAP_BEN_MUA", presenter.State.MapId); // v2 live snapshot wins
            Assert.Equal(5, presenter.State.PlayerX);
            Assert.True(presenter.State.TopologyIsCandidate); // never self-approve topology
        }

        [Fact]
        public void Refresh_V1Only_FallsBackToV1Snapshot()
        {
            var adapter = new MapSpyAdapter
            {
                World = new P1World
                {
                    mapId = "MAP_BEN_MUA",
                    self = new P1Self { characterId = "P1", x = 7, y = 8 },
                    entities = new[] { new P1Entity { entityId = "ENT_MAN_BM_NPC_LYAN", kind = "NPC", x = 9, y = 9 } }
                }
            };
            var presenter = new MapPresenter(adapter);
            presenter.Refresh();

            Assert.Equal("MAP_BEN_MUA", presenter.State.MapId);
            Assert.Equal(2, presenter.State.Markers.Count); // self + entity marker
        }

        [Fact]
        public void Bounds_FollowCanonicalMapBoundsJson()
        {
            var presenter = new MapPresenter(V2Adapter(10, 10, "MAP_BEN_MUA"));
            presenter.Refresh();
            Assert.Equal(360, presenter.State.Bounds.XMax); // default from map_bounds.json
            Assert.Equal(-12, presenter.State.Bounds.YMin);

            var thangLong = new MapPresenter(V2Adapter(10, 10, "MAP_THANG_LONG"));
            thangLong.Refresh();
            Assert.Equal(900, thangLong.State.Bounds.XMax); // override from map_bounds.json
            Assert.Equal(96, thangLong.State.Bounds.YMax);
        }

        [Fact]
        public void PanBy_ClampsViewWindowInsideMapBounds()
        {
            var presenter = new MapPresenter(V2Adapter(10, 20));
            presenter.Refresh();
            presenter.SetZoom(3f); // window 120x28 WU — smaller than the map on both axes

            // Drag far east/south: view center clamps inside bounds, never past the edge.
            presenter.PanBy(5000, -5000);
            Assert.Equal(300, presenter.State.ViewCenterX, 3); // mid 180 + travel 120
            Assert.Equal(30, presenter.State.ViewCenterY, 3);  // Y visible 120 > height 84 -> whole map visible -> lock center 30

            // Drag far back west/north: clamped at the other edge.
            presenter.PanBy(-99999, 99999);
            Assert.Equal(60, presenter.State.ViewCenterX, 3);
            Assert.Equal(30, presenter.State.ViewCenterY, 3);
        }

        [Fact]
        public void Zoom_ClampedToSupportedRange_AndPanKeepsClamped()
        {
            var presenter = new MapPresenter(V2Adapter(10, 20));
            presenter.Refresh();

            presenter.SetZoom(10f);
            Assert.Equal(4f, presenter.State.ZoomLevel);
            presenter.SetZoom(0.01f);
            Assert.Equal(0.25f, presenter.State.ZoomLevel);

            // At 0.25 the window (1440x336 WU) exceeds the map per axis → both axes
            // lock to the map center (whole-map view; panning is meaningless there).
            presenter.PanBy(100, 100);
            Assert.Equal(180, presenter.State.ViewCenterX, 3); // map horizontal center
            Assert.Equal(30, presenter.State.ViewCenterY, 3); // map vertical center ((-12+72)/2)
        }

        [Fact]
        public void CenterOnPlayer_DropsPan_KeepsZoom()
        {
            var presenter = new MapPresenter(V2Adapter(100, 40));
            presenter.Refresh();      // zoom 1: window == map width → view centers on mid map
            presenter.SetZoom(2f);    // zoom 2: travel 90/21 on x/y — center 100,40 kept

            presenter.PanBy(100, -30); // x target 180+100=280 -> clamped 270; Y visible 180 > height 84 -> lock center 30
            Assert.Equal(270, presenter.State.ViewCenterX, 3);
            Assert.Equal(30, presenter.State.ViewCenterY, 3);

            presenter.CenterOnPlayer(); // drops the accumulated view offset (Y stays locked to map center 30 at zoom2)
            Assert.Equal(100, presenter.State.ViewCenterX, 3);
            Assert.Equal(30, presenter.State.ViewCenterY, 3);
            Assert.Equal(2f, presenter.State.ZoomLevel);
        }

        [Fact]
        public void Refresh_PreservesPanAndZoom_FollowsMovingPlayer()
        {
            var adapter = new MapSpyAdapter { WorldV2 = V2World(100, 40) };
            var presenter = new MapPresenter(adapter);
            presenter.Refresh();
            presenter.SetZoom(2f);
            presenter.PanBy(50, 0); // view center = player + 50/…

            double centerAfterPan = presenter.State.ViewCenterX;

            // Server snapshot advances player position; UI-local pan/zoom survive rebuild.
            adapter.WorldV2 = V2World(110, 40);
            presenter.Refresh();

            Assert.Equal(2f, presenter.State.ZoomLevel);
            Assert.Equal(presenter.State.PlayerX + (centerAfterPan - 100), presenter.State.ViewCenterX, 3);
        }

        [Fact]
        public void Refresh_MapSwitch_ResetsStalePan()
        {
            var adapter = new MapSpyAdapter { WorldV2 = V2World(10, 20, "MAP_BEN_MUA") };
            var presenter = new MapPresenter(adapter);
            presenter.Refresh();
            presenter.SetZoom(2f);
            presenter.PanBy(600, 0); // clamped to the east edge of BEN_MUA
            Assert.Equal(270, presenter.State.ViewCenterX, 3);

            adapter.WorldV2 = V2World(10, 10, "MAP_THANG_LONG");
            presenter.Refresh();

            // Stale pan (600) was dropped on the switch; the remaining center position
            // comes only from the fresh bounds clamp (zoom-2 window on a 900-wide map,
            // horizontal travel ±225 — no player-anchored offset survives).
            Assert.Equal(225, presenter.State.ViewCenterX, 3);
            Assert.Equal(900, presenter.State.Bounds.XMax);
        }

        private static P1WorldV2 V2World(double x, double y, string mapId = "MAP_BEN_MUA") => new P1WorldV2
        {
            mapId = mapId,
            self = new P1Self { characterId = "P1", classId = "CLASS_MINH_KIEM", x = x, y = y, hp = 100, maxHp = 100, mp = 50, maxMp = 50 },
            entities = Array.Empty<P1EntityV2>()
        };
    }

    public class HudSafeAreaPolicyTests
    {
        [Fact]
        public void DesktopLandscape_NoInsets_FullHudWithTracker()
        {
            var d = HudSafeAreaPolicy.Decide(new HudViewport(1920, 1080, 0, 0, 0, 0), 5);
            Assert.Equal(HudMode.Full, d.Mode);
            Assert.Equal(1f, d.Scale);
            Assert.False(d.TrackerHidden);
        }

        [Fact]
        public void NotchedLandscapePhone_TrackerDropped_BarCompacted()
        {
            // iPhone-class landscape: 812x375 with 44px side notches and 24/20 bars.
            var d = HudSafeAreaPolicy.Decide(new HudViewport(812, 375, 44, 24, 44, 20), 5);
            Assert.Equal(HudMode.Compact, d.Mode); // usable 724w < bar 450 + tracker 310
            Assert.True(d.TrackerHidden);
            Assert.InRange(d.Scale, 0.6f, 0.85f);
        }

        [Fact]
        public void PortraitMobile_HidesTracker_CompactScale()
        {
            var d = HudSafeAreaPolicy.Decide(new HudViewport(360, 640, 0, 0, 0, 0), 5);
            Assert.Equal(HudMode.Compact, d.Mode);
            Assert.True(d.TrackerHidden);
            Assert.InRange(d.Scale, 0.6f, 0.85f);
        }

        [Fact]
        public void TinyViewport_HudsHiddenAsControlledFallback()
        {
            var d = HudSafeAreaPolicy.Decide(new HudViewport(200, 160, 20, 100, 20, 10), 5);
            Assert.Equal(HudMode.Hidden, d.Mode); // usable height 50 < 72 legibility floor
            Assert.True(d.TrackerHidden);
        }

        [Fact]
        public void HugeSideInsets_ShinkUsableSpaceToHidden()
        {
            var d = HudSafeAreaPolicy.Decide(new HudViewport(400, 700, 180, 0, 180, 0), 5);
            Assert.Equal(HudMode.Hidden, d.Mode); // usable width 40 < 225 (barW*0.5)
        }

        [Fact]
        public void TablewideViewport_FullHud()
        {
            var d = HudSafeAreaPolicy.Decide(new HudViewport(1280, 720, 0, 0, 0, 0), 5);
            Assert.Equal(HudMode.Full, d.Mode);
            Assert.False(d.TrackerHidden);
        }
    }

    public class SettingsLifecycleTests
    {
        private sealed class TestSettingsStore : ISettingsStore
        {
            public SettingsViewState Saved;
            public int SaveCount;
            public SettingsViewState Load() => Saved;
            public void Save(SettingsViewState settings) { Saved = settings; SaveCount++; }
        }

        [Fact]
        public void Setters_PersistThroughStore()
        {
            var store = new TestSettingsStore();
            var presenter = new SettingsPresenter(store);

            presenter.SetUiScale(1.5f);
            presenter.SetMasterVolume(0.3f);
            presenter.SetTextSize(1.25f);
            presenter.SetReducedMotion(true);
            presenter.SetReducedFlash(true);
            presenter.SetInputHints(false);

            Assert.Equal(6, store.SaveCount); // every setter persisted
            Assert.Same(store.Saved, presenter.Current);
            Assert.Equal(1.5f, store.Saved.UiScale);
            Assert.Equal(0.3f, store.Saved.MasterVolume);
            Assert.Equal(1.25f, store.Saved.TextSize);
            Assert.True(store.Saved.ReducedMotion);
            Assert.True(store.Saved.ReducedFlash);
            Assert.False(store.Saved.ShowInputHints);
        }

        [Fact]
        public void Reopen_LoadsPersistedValues_FromSameStore()
        {
            var store = new TestSettingsStore();
            var first = new SettingsPresenter(store);
            first.SetUiScale(1.4f);
            first.SetReducedMotion(true);

            // Reopen (new over the same versioned store): settings must survive.
            var reopened = new SettingsPresenter(store);
            Assert.Equal(1.4f, reopened.Current.UiScale);
            Assert.True(reopened.Current.ReducedMotion);
            Assert.True(reopened.Current.ShowInputHints); // untouched default
        }

        [Fact]
        public void Reset_RestoresDefault_AndPersists()
        {
            var store = new TestSettingsStore();
            var presenter = new SettingsPresenter(store);
            presenter.SetUiScale(2f);
            presenter.SetReducedFlash(true);

            presenter.Reset();

            var d = SettingsViewState.Default;
            Assert.Equal(d.UiScale, presenter.Current.UiScale);
            Assert.Equal(d.MasterVolume, presenter.Current.MasterVolume);
            Assert.Equal(d.TextSize, presenter.Current.TextSize);
            Assert.False(presenter.Current.ReducedMotion);
            Assert.False(presenter.Current.ReducedFlash);
            Assert.True(presenter.Current.ShowInputHints);
            Assert.Same(store.Saved, presenter.Current); // reset also persisted
        }

        [Fact]
        public void Clamps_OutOfRangeValues()
        {
            var presenter = new SettingsPresenter(new TestSettingsStore());
            presenter.SetUiScale(5f);   // → 2.0
            Assert.Equal(2f, presenter.Current.UiScale);
            presenter.SetUiScale(0.1f); // → 0.5
            Assert.Equal(0.5f, presenter.Current.UiScale);
            presenter.SetTextSize(9f);  // → 1.5
            Assert.Equal(1.5f, presenter.Current.TextSize);
            presenter.SetMasterVolume(-1f); // → 0
            Assert.Equal(0f, presenter.Current.MasterVolume);
        }
    }

    public class CinemaSafetyTests
    {
        [Fact]
        public void Play_KnownScene_EntersPlayingState_PreviewLabeled()
        {
            var presenter = new CinemaPresenter();
            presenter.Play("CIN_001");

            Assert.Equal(CinemaPlaybackPhase.Playing, presenter.State.Phase);
            Assert.True(presenter.State.IsPlaying);
            Assert.True(presenter.State.CanSkip);
            Assert.Equal("P00-01", presenter.State.QuestId);
            Assert.True(presenter.State.IsPreviewHarness); // media contract still preview until Muse VM
            Assert.NotNull(presenter.State.FallbackNote);  // honest preview labeling present
        }

        [Fact]
        public void Play_MissingScene_FallsBackWithoutGrant()
        {
            var presenter = new CinemaPresenter();
            presenter.Play("CIN_XXX_MISSING");

            Assert.Equal(CinemaPlaybackPhase.Fallback, presenter.State.Phase);
            Assert.Contains("Preview Harness", presenter.State.FallbackNote);
            // Fallback carries no quest attachment — no story flags, no rewards.
            Assert.Null(presenter.State.QuestId);
        }

        [Fact]
        public void Skip_EndsPlayback_CannotGrantAnything()
        {
            var presenter = new CinemaPresenter();
            presenter.Play("CIN_001");
            presenter.Skip();

            Assert.Equal(CinemaPlaybackPhase.Ended, presenter.State.Phase);
            Assert.True(presenter.State.IsEnded);
            Assert.False(presenter.State.CanSkip);
            // The view state has no flag/counter/reward surface at all:
            Assert.Equal("P00-01", presenter.State.QuestId); // identity preserved, nothing granted
        }

        [Fact]
        public void TimeRanOut_AutoEndsAtDuration()
        {
            var presenter = new CinemaPresenter();
            presenter.Play("CIN_001"); // 36s duration
            presenter.Update(10f);
            Assert.True(presenter.State.IsPlaying);

            presenter.Update(30f); // crosses duration → timeout path
            Assert.Equal(CinemaPlaybackPhase.Ended, presenter.State.Phase);
        }

        [Fact]
        public void Close_ReturnsToIdle()
        {
            var presenter = new CinemaPresenter();
            presenter.Play("CIN_001");
            presenter.Close();
            Assert.Equal(CinemaPlaybackPhase.Idle, presenter.State.Phase);
            Assert.False(presenter.State.IsPlaying);
        }
    }
    // ── OPC-14 M1 — accessibility / focus / overflow policies ──
    public class AccessibilityPolicyTests
    {
        [Fact] public void ReducedMotion_DisablesMotion() { Assert.False(AccessibilityPolicy.MotionEnabled(true)); Assert.True(AccessibilityPolicy.MotionEnabled(false)); }
        [Fact] public void ReducedFlash_DisablesFlash() { Assert.False(AccessibilityPolicy.FlashEnabled(true)); Assert.True(AccessibilityPolicy.FlashEnabled(false)); }
        [Fact] public void ShowInputHints_ControlsHotkeyLabels() { Assert.False(AccessibilityPolicy.HotkeyLabelsVisible(false)); Assert.True(AccessibilityPolicy.HotkeyLabelsVisible(true)); }
        [Fact] public void TextScale_ClampsToBand() { Assert.Equal(0.75f, AccessibilityPolicy.TextScale(0.1f)); Assert.Equal(1.5f, AccessibilityPolicy.TextScale(9f)); Assert.Equal(1.2f, AccessibilityPolicy.TextScale(1.2f)); }
        [Fact] public void FitsVertically_RespectsScale() { Assert.True(AccessibilityPolicy.FitsVertically(10f, 20f, 1f)); Assert.False(AccessibilityPolicy.FitsVertically(10f, 9f, 1.5f)); }
    }

    public class FocusNavigationPolicyTests
    {
        private static readonly FocusElement[] E = new[]
        {
            new FocusElement("a", "global", 10),
            new FocusElement("b", "modal", 20, true),
            new FocusElement("c", "modal", 30),
            new FocusElement("d", "global", 40),
        };

        [Fact] public void Tab_TrapsInsideModal() { Assert.Equal("c", FocusNavigationPolicy.Next("b", E, "modal")); Assert.Equal("b", FocusNavigationPolicy.Previous("c", E, "modal")); }
        [Fact] public void Tab_WrapsWithinModal() { Assert.Equal("b", FocusNavigationPolicy.Next("c", E, "modal")); }
        [Fact] public void Restore_PrefersRemembered_OrFirstGlobal() { Assert.Equal("a", FocusNavigationPolicy.Restore("zzz", E)); Assert.Equal("d", FocusNavigationPolicy.Restore("d", E)); }
        [Fact] public void IsEditorFocused_DetectsEditor() { Assert.True(FocusNavigationPolicy.IsEditorFocused(E, "b")); Assert.False(FocusNavigationPolicy.IsEditorFocused(E, "a")); }
        [Fact] public void EmptyScope_ReturnsNull() { Assert.Null(FocusNavigationPolicy.Next("a", E, "nope")); }
    }

    public class HudOverflowPolicyTests
    {
        [Fact] public void AllFit_NoOverflow() { var d = HudOverflowPolicy.Decide(3, 400f); Assert.Equal(3, d.VisibleCount); Assert.False(d.HasOverflow); }
        [Fact] public void Tight_FitsSubset_WithOverflow() { var d = HudOverflowPolicy.Decide(5, 120f); Assert.True(d.HasOverflow); Assert.True(d.VisibleCount < 5); }
        [Fact] public void NoSpace_KeepsOverflowButton() { var d = HudOverflowPolicy.Decide(5, 10f); Assert.Equal(0, d.VisibleCount); Assert.True(d.HasOverflow); }
        [Fact] public void Empty_Zero() { var d = HudOverflowPolicy.Decide(0, 400f); Assert.Equal(0, d.VisibleCount); Assert.False(d.HasOverflow); }
    }

    // ── OPC-14 A — settings consumer binding ──
    public class SettingsConsumerBinderTests
    {
        private sealed class TestSettingsStore : ISettingsStore
        {
            public SettingsViewState Saved;
            public SettingsViewState Load() => Saved;
            public void Save(SettingsViewState settings) { Saved = settings; }
        }

        private sealed class FakeConsumer : IUiAccessibilityConsumer
        {
            public int Calls;
            public SettingsViewState Last;
            public void ApplyAccessibility(SettingsViewState settings) { Calls++; Last = settings; }
        }

        [Fact]
        public void Register_AppliesImmediately()
        {
            var store = new TestSettingsStore();
            var presenter = new SettingsPresenter(store);
            var binder = new SettingsConsumerBinder(presenter);
            var c = new FakeConsumer();
            binder.Register(c);
            Assert.Equal(1, c.Calls); // initial apply on register (plus binder ctor notify already fired before register? ctor notifies before consumers)
            Assert.Same(presenter.Current, c.Last);
        }

        [Fact]
        public void Change_NotifiesAllConsumers()
        {
            var store = new TestSettingsStore();
            var presenter = new SettingsPresenter(store);
            var binder = new SettingsConsumerBinder(presenter);
            var c1 = new FakeConsumer(); var c2 = new FakeConsumer();
            binder.Register(c1); binder.Register(c2);
            int before1 = c1.Calls, before2 = c2.Calls;
            presenter.SetReducedMotion(true);
            Assert.True(c1.Calls > before1);
            Assert.True(c2.Calls > before2);
            Assert.True(c1.Last.ReducedMotion);
            Assert.True(c2.Last.ReducedMotion);
        }

        [Fact]
        public void Unregister_StopsNotifications()
        {
            var store = new TestSettingsStore();
            var presenter = new SettingsPresenter(store);
            var binder = new SettingsConsumerBinder(presenter);
            var c = new FakeConsumer();
            binder.Register(c);
            int before = c.Calls;
            binder.Unregister(c);
            presenter.SetReducedFlash(true);
            Assert.Equal(before, c.Calls);
        }

        [Fact]
        public void Rebind_PropagatesNewPresenterSettings()
        {
            var store1 = new TestSettingsStore();
            var p1 = new SettingsPresenter(store1);
            p1.SetReducedMotion(true);
            var binder = new SettingsConsumerBinder(p1);
            var c = new FakeConsumer();
            binder.Register(c);

            var store2 = new TestSettingsStore();
            store2.Saved = new SettingsViewState(1f, 1f, 1f, false, false, true);
            var p2 = new SettingsPresenter(store2);
            binder.Rebind(p2);
            Assert.False(c.Last.ReducedMotion); // from p2
        }

        [Fact]
        public void BrokenConsumer_DoesNotBreakPump()
        {
            var store = new TestSettingsStore();
            var presenter = new SettingsPresenter(store);
            var binder = new SettingsConsumerBinder(presenter);
            var broken = new ThrowingConsumer();
            var ok = new FakeConsumer();
            binder.Register(broken);
            binder.Register(ok);
            presenter.SetInputHints(false); // must not throw
            Assert.True(ok.Calls > 0);
        }

        private sealed class ThrowingConsumer : IUiAccessibilityConsumer
        {
            public void ApplyAccessibility(SettingsViewState settings) { throw new InvalidOperationException("boom"); }
        }
    }

    // ── OPC-14 B — catalog loader + resolver end-to-end ──
    public class UiCatalogLoaderResolverTests
    {
        private static string CatalogPath => System.IO.Path.Combine(
            System.AppDomain.CurrentDomain.BaseDirectory, "..", "..", "Assets", "Resources", "PlayerUI", "ui_item_catalog.json");

        private static string LoadCatalogText()
        {
            // Try a few relative locations (test runner cwd varies).
            var candidates = new[]
            {
                System.IO.Path.Combine("..", "..", "Assets", "Resources", "PlayerUI", "ui_item_catalog.json"),
                System.IO.Path.Combine("Assets", "Resources", "PlayerUI", "ui_item_catalog.json"),
                @"D:\Project\NGUMACHHUYENAN-opencode-player-ui-20261101\Client\Assets\Resources\PlayerUI\ui_item_catalog.json",
            };
            foreach (var c in candidates)
                if (System.IO.File.Exists(c)) return System.IO.File.ReadAllText(c);
            // fallback: search upward
            var dir = new System.IO.DirectoryInfo(System.AppDomain.CurrentDomain.BaseDirectory);
            while (dir != null)
            {
                var cand = System.IO.Path.Combine(dir.FullName, "Client", "Assets", "Resources", "PlayerUI", "ui_item_catalog.json");
                if (System.IO.File.Exists(cand)) return System.IO.File.ReadAllText(cand);
                dir = dir.Parent;
            }
            throw new System.IO.FileNotFoundException("ui_item_catalog.json not found");
        }

        [Fact]
        public void Loader_ParsesGeneratedCatalog()
        {
            var ok = UiCatalogLoader.TryLoad(LoadCatalogText(), out var cat, out var err);
            Assert.True(ok, err);
            Assert.NotNull(cat);
            Assert.Equal(2656, cat.Count);
            Assert.Equal(cat.Count, cat.Entries.Count);
        }

        [Fact]
        public void Loader_RejectsMalformed()
        {
            Assert.False(UiCatalogLoader.TryLoad("{not json", out _, out var e1));
            Assert.False(UiCatalogLoader.TryLoad("", out _, out var e2));
            Assert.False(UiCatalogLoader.TryLoad("{\"schemaVersion\":99,\"entries\":[]}", out _, out var e3));
        }

        [Fact]
        public void Resolver_FullCatalogCoverage()
        {
            var ok = UiCatalogLoader.TryLoad(LoadCatalogText(), out var cat, out var err);
            Assert.True(ok, err);
            UiItemResolver.SetCatalog(cat);
            // every entry resolves to a non-null metadata with display name
            foreach (var e in cat.Entries)
            {
                var m = UiItemResolver.Resolve(e.ItemId);
                Assert.NotNull(m);
                Assert.False(string.IsNullOrEmpty(m.DisplayName));
            }
            UiItemResolver.SetCatalog(null);
        }

        [Fact]
        public void Resolver_BaseAndVariant()
        {
            var ok = UiCatalogLoader.TryLoad(LoadCatalogText(), out var cat, out var err);
            Assert.True(ok, err);
            UiItemResolver.SetCatalog(cat);
            // find a variant entry
            var variant = cat.Entries.Find(e => e.ItemId != null && e.ItemId.Contains("-R-"));
            Assert.NotNull(variant);
            var m = UiItemResolver.Resolve(variant.ItemId);
            Assert.NotNull(m);
            Assert.False(string.IsNullOrEmpty(m.DisplayName));
            // unknown template
            var u = UiItemResolver.Resolve("ZZZ-DOES-NOT-EXIST");
            Assert.NotNull(u);
            Assert.Null(u.Slot);
            Assert.Null(u.ClassId);
            UiItemResolver.SetCatalog(null);
        }

        [Fact]
        public void Resolver_MissingCatalog_FallsBackToEmbedded()
        {
            UiItemResolver.SetCatalog(null);
            var m = UiItemResolver.Resolve("POT-HP-01");
            Assert.NotNull(m);
            Assert.Equal("Dược Bến Mưa", m.DisplayName);
        }

        [Fact]
        public void Resolver_PreservesExtendedFields()
        {
            var ok = UiCatalogLoader.TryLoad(LoadCatalogText(), out var cat, out var err);
            Assert.True(ok, err);
            UiItemResolver.SetCatalog(cat);
            // find an entry with set info
            var withSet = cat.Entries.Find(e => !string.IsNullOrEmpty(e.SetId));
            Assert.NotNull(withSet);
            var m = UiItemResolver.Resolve(withSet.ItemId);
            Assert.Equal(withSet.SetId, m.SetId);
            UiItemResolver.SetCatalog(null);
        }
    }

}
