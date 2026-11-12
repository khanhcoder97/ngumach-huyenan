// AG6 — Additional synthetic fixture tests: NpcDialoguePresenter, settings persistence,
// modal stack edge cases, map view state construction, stale/uncertain scenarios.
// All fixtures labelled SYNTHETIC — not production data.
// DOTNET UNVERIFIED on this machine.
// Owner: Antigravity Remote — Issue #80.

using System;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace PlayerUIChecks
{
    // ── NpcDialoguePresenter tests ─────────────────────────────────────────

    public class NpcDialoguePresenterTests
    {
        static P1Quest MakeQuest(string id, string state) => new P1Quest
        {
            questId = id, state = state, stepId = "S1",
            objectiveCounters = new System.Collections.Generic.Dictionary<string, int>(),
            revision = 1
        };

        [Fact]
        public async Task Interact_BuildsDialogueWithAvailableQuest()
        {
            // SYNTHETIC
            var adapter = new FakeAdapter
            {
                Quests = new[] { MakeQuest("P00-01", "AVAILABLE") }
            };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new NpcDialoguePresenter(adapter);
            var state = await presenter.InteractAsync("NPC_LYAN", CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.Contains(state.Value.Choices, c => c.Label.Contains("Nhận nhiệm vụ") && c.Enabled);
        }

        [Fact]
        public async Task Interact_BlockedWhenPendingMutation()
        {
            var adapter = new FakeAdapter { HasPendingMutation = true };
            var presenter = new NpcDialoguePresenter(adapter);
            var state = await presenter.InteractAsync("NPC_LYAN", CancellationToken.None);

            Assert.True(state.IsError);
            Assert.Equal("pending_mutation", state.ErrorCode);
        }

        [Fact]
        public async Task Interact_NoQuests_ShowsGoodbye()
        {
            var adapter = new FakeAdapter { Quests = Array.Empty<P1Quest>() };
            var presenter = new NpcDialoguePresenter(adapter);
            var state = await presenter.InteractAsync("NPC_LYAN", CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.Single(state.Value.Choices);
            Assert.Contains("Tạm biệt", state.Value.Choices[0].Label);
        }

        [Fact]
        public async Task ActiveQuest_ShowsDisabledChoice()
        {
            var adapter = new FakeAdapter
            {
                Quests = new[] { MakeQuest("P00-01", "ACTIVE") }
            };
            var presenter = new NpcDialoguePresenter(adapter);
            var state = await presenter.InteractAsync("NPC_LYAN", CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.Contains(state.Value.Choices, c => !c.Enabled && c.DisabledReason != null);
        }
    }

    // ── MapPresenter tests ─────────────────────────────────────────────────

    public class MapPresenterTests
    {
        static P1World MakeWorld(string mapId = "MAP_TEST") => new P1World
        {
            mapId = mapId,
            revision = 1, serverTick = 1,
            self = new P1Self { characterId = "CHAR_1", classId = "CLS_1", x = 10, y = 20, hp = 100, maxHp = 100, mp = 50, maxMp = 50 },
            entities = new P1Entity[]
            {
                new P1Entity { entityId = "E1", kind = "NPC", x = 15, y = 25 }
            }
        };

        [Fact]
        public void Refresh_BuildsMarkersFromV1World()
        {
            var adapter = new FakeAdapter { World = MakeWorld() };
            var presenter = new MapPresenter(adapter);
            presenter.Refresh();

            Assert.NotNull(presenter.State);
            Assert.Equal("MAP_TEST", presenter.State.MapId);
            Assert.Equal(10, presenter.State.PlayerX);
            // Player + 1 entity = 2 markers
            Assert.Equal(2, presenter.State.Markers.Count);
        }

        [Fact]
        public void Zoom_Clamps_ToRange()
        {
            var adapter = new FakeAdapter { World = MakeWorld() };
            var presenter = new MapPresenter(adapter);
            presenter.Refresh();
            presenter.SetZoom(99f);
            Assert.Equal(4f, presenter.State.ZoomLevel);
            presenter.SetZoom(0f);
            Assert.Equal(0.25f, presenter.State.ZoomLevel);
        }

        [Fact]
        public void Topology_MarkedCandidate()
        {
            var adapter = new FakeAdapter { World = MakeWorld() };
            var presenter = new MapPresenter(adapter);
            presenter.Refresh();
            Assert.True(presenter.State.TopologyIsCandidate);
        }
    }

    // ── AsyncState tests ──────────────────────────────────────────────────

    public class AsyncStateTests
    {
        [Fact]
        public void Idle_PhaseIsIdle()
        {
            var s = AsyncState<int>.Idle;
            Assert.Equal(LoadPhase.Idle, s.Phase);
            Assert.False(s.IsLoading);
        }

        [Fact]
        public void WithLoading_PreservesLastValue()
        {
            var s = new AsyncState<int>(LoadPhase.Loaded, 42, null);
            var loading = s.WithLoading();
            Assert.Equal(LoadPhase.Loading, loading.Phase);
            Assert.Equal(42, loading.Value); // last known value preserved
        }

        [Fact]
        public void WithError_PreservesLastValue()
        {
            var s = new AsyncState<string>(LoadPhase.Loaded, "data", null);
            var err = s.WithError("net_err", "corr-1");
            Assert.True(err.IsError);
            Assert.Equal("data", err.Value);
            Assert.Equal("net_err", err.ErrorCode);
            Assert.Equal("corr-1", err.CorrelationId);
        }
    }

    // ── InventoryViewState tests ───────────────────────────────────────────

    public class InventoryViewStateTests
    {
        [Fact]
        public void PageSlots_Returns25Slots_PerPage()
        {
            var slots = new System.Collections.Generic.Dictionary<int, ItemSlotView>();
            var inv = new InventoryViewState(1, slots, new CurrencyView[0]);
            int count = 0;
            foreach (var (i, s) in inv.PageSlots()) count++;
            Assert.Equal(25, count);
        }

        [Fact]
        public void WithPage_ClampsToRange()
        {
            var inv = new InventoryViewState(1, null, null, activePage: 0);
            Assert.Equal(0, inv.WithPage(-1).ActivePage);
            Assert.Equal(3, inv.WithPage(99).ActivePage);
        }

        [Fact]
        public void TotalSlots_Is100()
        {
            Assert.Equal(100, InventoryViewState.TotalSlots);
        }
    }

    // ── Session expired scenario ───────────────────────────────────────────

    public class SessionExpiredTests
    {
        [Fact]
        public async Task InventoryLoad_WhenExpired_ReturnsError()
        {
            var adapter = new FakeAdapter
            {
                ConnectionState = UIConnectionState.Expired
            };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Fail("session_not_found", "corr-exp"));

            var presenter = new InventoryPresenter(adapter);
            var state = await presenter.LoadAsync(CancellationToken.None);

            Assert.True(state.IsError);
            Assert.Equal("session_not_found", state.ErrorCode);
        }
    }

    // ── Producer Regression Negative Checks (AGREV-04, 05, 06, 07) ───────────

    public class ProducerNegativeChecks
    {
        // Synthetic fixtures matching optional-slot BAG wire shape; no balance values.
        [Fact]
        public async Task ValidBagItemWithoutSlotMustBeVisible()
        {
            var adapter = new FakeAdapter { Inventory = new P1Inventory {
                inventoryRevision = 1,
                items = new[] { new P1Item { instanceId = "ITM_REVIEW_A", templateId = "TOOL-ROD-01", location = "BAG", stack = 1, durability = 100, version = 1 } },
                currencies = Array.Empty<P1Currency>() } };
            var presenter = new InventoryPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);
            Assert.Single(presenter.State.Value.Slots);
        }

        [Fact]
        public async Task EquipmentMustNotOccupyBagCell()
        {
            var adapter = new FakeAdapter { Inventory = new P1Inventory {
                inventoryRevision = 1,
                items = new[] { new P1Item { instanceId = "ITM_REVIEW_E", templateId = "TOOL-ROD-01", location = "EQUIPPED", slot = "MAIN_HAND", stack = 1, durability = 100, version = 1 } },
                currencies = Array.Empty<P1Currency>() } };
            var presenter = new InventoryPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);
            Assert.DoesNotContain(presenter.State.Value.DiagnosticWarnings, x => x.StartsWith("out_of_range_slot"));
        }

        [Fact]
        public async Task CancelledReadMustNotLeaveLoadingForever()
        {
            var adapter = new FakeAdapter { OnReadInventory = () => Task.FromException<P1Result>(new OperationCanceledException()) };
            var presenter = new InventoryPresenter(adapter);
            try { await presenter.LoadAsync(CancellationToken.None); } catch (OperationCanceledException) { }
            Assert.False(presenter.State.IsLoading);
        }

        [Fact]
        public async Task QuestReadyMustNotOfferTurnInAtEveryNpc()
        {
            var adapter = new FakeAdapter { Quests = new[] { new P1Quest {
                questId = "P00-01", state = "READY_TO_TURN_IN", stepId = "STEP_REVIEW",
                objectiveCounters = new System.Collections.Generic.Dictionary<string, int>(), revision = 1 } } };
            var presenter = new NpcDialoguePresenter(adapter);
            await presenter.InteractAsync("NPC_UNRELATED_REVIEW", CancellationToken.None);
            Assert.DoesNotContain(presenter.State.Value.Choices, c => c.Enabled && c.Label.StartsWith("[Nộp nhiệm vụ]"));
        }
    }

    // ── Concrete P1ClientAdapter coverage (AGREV-01) ─────────────────────────

    public class P1ClientAdapterTests
    {
        private sealed class DummyTransport : IP1Transport
        {
            public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken cancellation)
                => Task.FromResult(new P1HttpReply { StatusCode = 200, Body = "{}" });
        }

        [Fact]
        public void Adapter_ThrowsOnNullClient()
        {
            Assert.Throws<ArgumentNullException>(() => new P1ClientAdapter(null));
        }

        [Fact]
        public void Adapter_ExposesClientProperties()
        {
            var client = new P1Client(new DummyTransport());
            var adapter = new P1ClientAdapter(client);

            Assert.Equal(UIConnectionState.Disconnected, adapter.ConnectionState);
            Assert.False(adapter.HasPendingMutation);
            Assert.Null(adapter.LastErrorCode);
            Assert.Null(adapter.LastCorrelationId);
            Assert.Null(adapter.Self);
            Assert.Null(adapter.World);
            Assert.Null(adapter.WorldV2);
            Assert.Empty(adapter.Quests);
            Assert.Null(adapter.Inventory);
        }
    }
}
