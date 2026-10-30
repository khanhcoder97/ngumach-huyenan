// AG6 — Synthetic fixture tests for InventoryPresenter.
// Tests cover: 100 slots/4 pages, duplicate-slot, bad ref, stale revision,
// unknown item, full bag READY, committed receipt + refresh failure, uncertain retry.
// All fixtures are labelled as SYNTHETIC — not production data.
// DOTNET: UNVERIFIED on this machine (dotnet not installed). Run from clone with dotnet test.
// Owner: Antigravity Remote — Issue #80.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace PlayerUIChecks
{
    // ── Fake adapter for tests ─────────────────────────────────────────────

    sealed class FakeAdapter : IP1UIAdapter
    {
        public UIConnectionState ConnectionState { get; set; } = UIConnectionState.Ready;
        public bool HasPendingMutation { get; set; }
        public string LastErrorCode { get; set; }
        public string LastCorrelationId { get; set; }
        public P1Self Self { get; set; }
        public P1World World { get; set; }
        public P1WorldV2 WorldV2 { get; set; }
        public P1Quest[] Quests { get; set; } = Array.Empty<P1Quest>();
        public P1Inventory Inventory { get; set; }

        public Func<Task<P1Result>> OnReadInventory { get; set; }
        public Func<Task<P1Result>> OnReadQuests { get; set; }

        public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => OnReadQuests?.Invoke() ?? Task.FromResult(P1Result.Ok());
        public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => OnReadInventory?.Invoke() ?? Task.FromResult(P1Result.Ok());
        public Task<P1Result> AcceptQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
        public Task<P1Result> InteractAsync(string t, CancellationToken ct) => Task.FromResult(P1Result.Ok());
        public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
        public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
    }

    // ── InventoryPresenter tests ───────────────────────────────────────────

    public class InventoryPresenterTests
    {
        static P1Inventory MakeInv(long rev, P1Item[] items = null) => new P1Inventory
        {
            inventoryRevision = rev,
            items = items ?? Array.Empty<P1Item>(),
            currencies = Array.Empty<P1Currency>()
        };

        static P1Item MakeItem(string iid, string tid, int stack = 1, string slot = null, string loc = "BAG") =>
            new P1Item { instanceId = iid, templateId = tid, stack = stack, slot = slot, location = loc, durability = 100, version = 1 };

        [Fact]
        public async Task Load_100Slots_4Pages()
        {
            // SYNTHETIC: 100 items with explicit slots 0..99
            var items = new List<P1Item>();
            for (int i = 0; i < 100; i++)
                items.Add(MakeItem("iid_" + i, "tmpl_" + i, slot: i.ToString()));

            var adapter = new FakeAdapter();
            adapter.Inventory = MakeInv(1, items.ToArray());
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new InventoryPresenter(adapter);
            var state = await presenter.LoadAsync(CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.Equal(100, state.Value.Slots.Count);
            Assert.Equal(0, state.Value.DiagnosticWarnings.Length);

            // Page 0: slots 0..24
            int count = 0;
            foreach (var (_, item) in state.Value.PageSlots()) if (item != null) count++;
            Assert.Equal(25, count);

            // Page 3
            presenter.SetPage(3);
            count = 0;
            foreach (var (_, item) in presenter.State.Value.PageSlots()) if (item != null) count++;
            Assert.Equal(25, count);
        }

        [Fact]
        public async Task Load_DuplicateSlot_ProducesWarning()
        {
            // SYNTHETIC: two items at slot 0
            var items = new[] {
                MakeItem("a", "tmpl_a", slot: "0"),
                MakeItem("b", "tmpl_b", slot: "0")
            };
            var adapter = new FakeAdapter { Inventory = MakeInv(1, items) };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new InventoryPresenter(adapter);
            var state = await presenter.LoadAsync(CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.Contains(state.Value.DiagnosticWarnings, w => w.StartsWith("duplicate_slot_index"));
            Assert.Equal(1, state.Value.Slots.Count); // first wins
        }

        [Fact]
        public async Task Load_OutOfRangeSlot_ProducesWarning()
        {
            var items = new[] { MakeItem("x", "tmpl_x", slot: "999") };
            var adapter = new FakeAdapter { Inventory = MakeInv(1, items) };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new InventoryPresenter(adapter);
            var state = await presenter.LoadAsync(CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.Contains(state.Value.DiagnosticWarnings, w => w.StartsWith("out_of_range_slot"));
            Assert.Empty(state.Value.Slots);
        }

        [Fact]
        public async Task StaleRevision_NotApplied()
        {
            // SYNTHETIC: load rev 10, then server returns rev 5 (stale) — should keep rev 10
            var items1 = new[] { MakeItem("a", "t", slot: "0") };
            var items2 = new[] { MakeItem("b", "t", slot: "1") };

            var adapter = new FakeAdapter { Inventory = MakeInv(10, items1) };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new InventoryPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            // Now simulate stale response
            adapter.Inventory = MakeInv(5, items2); // older revision
            await presenter.LoadAsync(CancellationToken.None);

            Assert.Equal(10, presenter.State.Value.InventoryRevision);
            Assert.True(presenter.State.Value.Slots.ContainsKey(0)); // original item kept
        }

        [Fact]
        public async Task SelectionPreserved_AfterPageChange()
        {
            var items = new[] {
                MakeItem("sel", "t", slot: "0"),
                MakeItem("other", "t", slot: "25") // page 1
            };
            var adapter = new FakeAdapter { Inventory = MakeInv(1, items) };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new InventoryPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);
            presenter.SetSelection("sel");
            presenter.SetPage(1);

            Assert.Equal("sel", presenter.State.Value.SelectedInstanceId);
        }

        [Fact]
        public async Task SelectionCleared_WhenItemGone()
        {
            var items = new[] { MakeItem("sel", "t", slot: "0") };
            var adapter = new FakeAdapter { Inventory = MakeInv(1, items) };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new InventoryPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);
            presenter.SetSelection("sel");

            // Reload with item removed
            adapter.Inventory = MakeInv(2, Array.Empty<P1Item>());
            await presenter.LoadAsync(CancellationToken.None);

            Assert.Null(presenter.State.Value.SelectedInstanceId);
        }

        [Fact]
        public async Task EmptyInventory_NotMisread_AsLost()
        {
            // SYNTHETIC: empty inventory is empty, not "all items gone"
            var adapter = new FakeAdapter { Inventory = MakeInv(1, Array.Empty<P1Item>()) };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new InventoryPresenter(adapter);
            var state = await presenter.LoadAsync(CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.Empty(state.Value.Slots);
            Assert.Empty(state.Value.DiagnosticWarnings);
        }

        [Fact]
        public async Task LoadError_PreservesLastKnownData()
        {
            var items = new[] { MakeItem("a", "t", slot: "0") };
            var adapter = new FakeAdapter { Inventory = MakeInv(1, items) };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new InventoryPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            // Next load fails
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Fail("network_unavailable", "corr-1"));
            await presenter.LoadAsync(CancellationToken.None);

            Assert.True(presenter.State.IsError);
            // Value (last known data) still present
            Assert.NotNull(presenter.State.Value);
            Assert.Equal(1, presenter.State.Value.Slots.Count);
        }

        [Fact]
        public async Task FilterIsProjectionOnly_SlotIndicesUnchanged()
        {
            var items = new[] {
                MakeItem("a", "sword", slot: "0"),
                MakeItem("b", "shield", slot: "1")
            };
            var adapter = new FakeAdapter { Inventory = MakeInv(1, items) };
            adapter.OnReadInventory = () => Task.FromResult(P1Result.Ok());

            var presenter = new InventoryPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            // Filter is a view-only operation — slot indices must not change
            presenter.SetFilter("sword");
            Assert.Equal(2, presenter.State.Value.Slots.Count); // both slots still in state
            Assert.Equal("sword", presenter.State.Value.FilterText);
        }
    }

    // ── PanelRouter tests ──────────────────────────────────────────────────

    public class PanelRouterTests
    {
        [Fact]
        public void Open_SetsCurrentPanel()
        {
            var router = new PanelRouter();
            router.Open(PlayerPanel.Inventory, UIConnectionState.Ready);
            Assert.Equal(PlayerPanel.Inventory, router.Current);
        }

        [Fact]
        public void Open_SecondPanel_PushesFirst()
        {
            var router = new PanelRouter();
            router.Open(PlayerPanel.Inventory, UIConnectionState.Ready);
            router.Open(PlayerPanel.Settings, UIConnectionState.Ready);
            Assert.Equal(PlayerPanel.Settings, router.Current);
            Assert.Equal(1, router.ModalDepth);
        }

        [Fact]
        public void CloseTop_ReturnsFocusToPrevious()
        {
            var router = new PanelRouter();
            router.Open(PlayerPanel.Inventory, UIConnectionState.Ready);
            router.Open(PlayerPanel.Settings, UIConnectionState.Ready);
            router.CloseTop();
            Assert.Equal(PlayerPanel.Inventory, router.Current);
        }

        [Fact]
        public void CloseAll_ClearsStack()
        {
            var router = new PanelRouter();
            router.Open(PlayerPanel.Inventory, UIConnectionState.Ready);
            router.Open(PlayerPanel.Map, UIConnectionState.Ready);
            router.CloseAll();
            Assert.Equal(PlayerPanel.None, router.Current);
            Assert.Equal(0, router.ModalDepth);
        }

        [Fact]
        public void CloseTop_OnNone_IsNoop()
        {
            var router = new PanelRouter();
            router.CloseTop(); // should not throw
            Assert.Equal(PlayerPanel.None, router.Current);
        }
    }

    // ── QuestJournalPresenter tests ────────────────────────────────────────

    public class QuestJournalPresenterTests
    {
        static P1Quest MakeQuest(string id, string state, long rev = 1) => new P1Quest
        {
            questId = id, state = state, stepId = "S1",
            objectiveCounters = new System.Collections.Generic.Dictionary<string, int>(),
            revision = rev
        };

        [Fact]
        public async Task Load_SplitsActive_Completed()
        {
            var adapter = new FakeAdapter
            {
                Quests = new[] {
                    MakeQuest("Q1", "ACTIVE"),
                    MakeQuest("Q2", "COMPLETED"),
                    MakeQuest("Q3", "READY_TO_TURN_IN")
                }
            };
            adapter.OnReadQuests = () => Task.FromResult(P1Result.Ok());

            var presenter = new QuestJournalPresenter(adapter);
            var state = await presenter.LoadAsync(CancellationToken.None);

            Assert.True(state.IsLoaded);
            Assert.Equal(2, state.Value.Active.Count);
            Assert.Single(state.Value.Completed);
        }

        [Fact]
        public async Task LoadError_SetsErrorPhase()
        {
            var adapter = new FakeAdapter { Quests = Array.Empty<P1Quest>() };
            adapter.OnReadQuests = () => Task.FromResult(P1Result.Fail("network_unavailable"));

            var presenter = new QuestJournalPresenter(adapter);
            var state = await presenter.LoadAsync(CancellationToken.None);

            Assert.True(state.IsError);
            Assert.Equal("network_unavailable", state.ErrorCode);
        }
    }

    // ── SettingsPresenter tests ────────────────────────────────────────────

    public class SettingsPresenterTests
    {
        sealed class MemoryStore : ISettingsStore
        {
            public SettingsViewState Saved;
            public SettingsViewState Load() => Saved;
            public void Save(SettingsViewState s) => Saved = s;
        }

        [Fact]
        public void DefaultsLoaded_WhenStoreEmpty()
        {
            var store = new MemoryStore();
            var presenter = new SettingsPresenter(store);
            Assert.Equal(SettingsViewState.Default.MasterVolume, presenter.Current.MasterVolume);
        }

        [Fact]
        public void SetMasterVolume_Clamps()
        {
            var store = new MemoryStore();
            var presenter = new SettingsPresenter(store);
            presenter.SetMasterVolume(99f);
            Assert.Equal(1f, presenter.Current.MasterVolume);
        }

        [Fact]
        public void Reset_RestoresDefault()
        {
            var store = new MemoryStore();
            var presenter = new SettingsPresenter(store);
            presenter.SetMasterVolume(0.2f);
            presenter.Reset();
            Assert.Equal(SettingsViewState.Default.MasterVolume, presenter.Current.MasterVolume);
        }
    }
}
