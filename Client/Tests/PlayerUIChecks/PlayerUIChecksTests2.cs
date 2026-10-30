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
                Quests = new[] { MakeQuest("Q1", "AVAILABLE") }
            };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new NpcDialoguePresenter(adapter);
            var state = await presenter.InteractAsync("NPC_TEST", CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.Contains(state.Value.Choices, c => c.Label.Contains("Nhận nhiệm vụ") && c.Enabled);
        }

        [Fact]
        public async Task Interact_BlockedWhenPendingMutation()
        {
            var adapter = new FakeAdapter { HasPendingMutation = true };
            var presenter = new NpcDialoguePresenter(adapter);
            var state = await presenter.InteractAsync("NPC_TEST", CancellationToken.None);

            Assert.True(state.IsError);
            Assert.Equal("pending_mutation", state.ErrorCode);
        }

        [Fact]
        public async Task Interact_NoQuests_ShowsGoodbye()
        {
            var adapter = new FakeAdapter { Quests = Array.Empty<P1Quest>() };
            var presenter = new NpcDialoguePresenter(adapter);
            var state = await presenter.InteractAsync("NPC_TEST", CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.Single(state.Value.Choices);
            Assert.Contains("Tạm biệt", state.Value.Choices[0].Label);
        }

        [Fact]
        public async Task ActiveQuest_ShowsDisabledChoice()
        {
            var adapter = new FakeAdapter
            {
                Quests = new[] { MakeQuest("Q1", "ACTIVE") }
            };
            var presenter = new NpcDialoguePresenter(adapter);
            var state = await presenter.InteractAsync("NPC_TEST", CancellationToken.None);

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
}
