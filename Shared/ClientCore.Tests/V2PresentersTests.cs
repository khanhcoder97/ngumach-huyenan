// OPC-16 O4 — presenter tests for inventory v2 and death-return.
// Verifies immutable view state, server-authoritative commands and Vietnamese
// user-facing hints. No Unity dependency. Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class V2PresentersTests
    {
        private sealed class FakeInventoryAdapter : IP1InventoryV2Adapter
        {
            public P1InventorySnapshotV2 Snapshot;
            public P1Result ReadResult = P1Result.Ok();
            public P1Result CommandResult = P1Result.Ok();
            public bool HasPendingMutation { get; set; }
            public string LastErrorCode { get; set; }
            public readonly List<(string item, long revision)> EquipCalls = new();
            public readonly List<(string slot, long revision)> UnequipCalls = new();

            public P1InventorySnapshotV2 InventoryV2 => Snapshot;

            public Task<P1Result> ReadInventoryV2Async(CancellationToken ct) => Task.FromResult(ReadResult);

            public Task<P1Result> EquipV2Async(string itemInstanceId, long expectedRevision, CancellationToken ct)
            {
                EquipCalls.Add((itemInstanceId, expectedRevision));
                return Task.FromResult(CommandResult);
            }

            public Task<P1Result> UnequipV2Async(string slotId, long expectedRevision, CancellationToken ct)
            {
                UnequipCalls.Add((slotId, expectedRevision));
                return Task.FromResult(CommandResult);
            }
        }

        private sealed class FakeDeathAdapter : IP1DeathReturnAdapter
        {
            public UIConnectionState ConnectionState { get; set; } = UIConnectionState.Ready;
            public bool HasPendingMutation { get; set; }
            public P1Self Self { get; set; } = new P1Self { hp = 0, maxHp = 100 };
            public P1DeathReturnResultV1 LastDeathReturn { get; set; }
            public long? NextReturnAllowedAtTick { get; set; }
            public P1Result Result = P1Result.Ok();
            public int Calls;

            public Task<P1Result> ReturnFromDeathAsync(CancellationToken ct)
            {
                Calls++;
                return Task.FromResult(Result);
            }
        }

        private static P1ItemV2 Item(string instanceId, string templateId, string location, string slotId)
        {
            return new P1ItemV2
            {
                instanceId = instanceId, templateId = templateId, stack = 1, location = location,
                slotId = slotId, durability = 0, version = 1
            };
        }

        private static P1InventorySnapshotV2 Snapshot(long revision, P1ItemV2 hat = null,
            bool withUnsupported = true)
        {
            var slots = new List<P1EquipmentSlotV2>();
            foreach (var slotId in InventoryV2ViewState.SlotOrder)
                slots.Add(new P1EquipmentSlotV2
                {
                    slotId = slotId,
                    item = slotId == "HAT" ? hat : null
                });
            var unsupported = new List<P1UnsupportedEquipV2>();
            if (withUnsupported)
                unsupported.Add(new P1UnsupportedEquipV2
                {
                    instanceId = "ITM_UNMAPPED", templateId = "EQ_OLD_T1",
                    sourceSlot = "MAIN_HAND", reason = "UNMAPPED_SLOT"
                });
            return new P1InventorySnapshotV2
            {
                schemaVersion = 2,
                slotSpec = "V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT",
                inventoryRevision = revision,
                bagSlots = 100,
                slots = slots.ToArray(),
                bag = new[] { Item("ITM_POTION", "POT-HP-01", "BAG", null) },
                unsupported = unsupported.ToArray(),
                currencies = new[] { new P1Currency { currencyId = "COIN", amount = 80 } }
            };
        }

        [Fact]
        public async Task InventoryLoad_BuildsTwelveSlotsBudgetAndVietnameseWarning()
        {
            var adapter = new FakeInventoryAdapter { Snapshot = Snapshot(4, Item("ITM_HAT", "EQ_MK_HAT_T1", "EQUIPPED", "HAT")) };
            var presenter = new InventoryV2Presenter(adapter);

            var state = await presenter.LoadAsync(CancellationToken.None);

            Assert.True(state.IsLoaded, state.ErrorCode);
            Assert.Equal(4, state.Value.InventoryRevision);
            Assert.Equal("ITM_HAT", state.Value.GetEquipped("HAT").InstanceId);
            Assert.Single(state.Value.Bag);
            Assert.Single(state.Value.Unsupported);
            Assert.Contains("không có ô", state.Value.Unsupported[0].ReasonVi);
            Assert.Equal(80, state.Value.Currencies[0].Amount);
        }

        [Fact]
        public async Task Selection_OnlyKeepsExistingInstance()
        {
            var adapter = new FakeInventoryAdapter { Snapshot = Snapshot(4) };
            var presenter = new InventoryV2Presenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            presenter.Select("ITM_MISSING");
            Assert.Null(presenter.State.Value.SelectedInstanceId);
            presenter.Select("ITM_POTION");
            Assert.Equal("ITM_POTION", presenter.State.Value.SelectedInstanceId);
        }

        [Fact]
        public async Task Equip_UsesCurrentRevisionAndAppliesServerSnapshot()
        {
            var adapter = new FakeInventoryAdapter { Snapshot = Snapshot(4) };
            var presenter = new InventoryV2Presenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);
            adapter.CommandResult = P1Result.Ok();
            adapter.Snapshot = Snapshot(5, Item("ITM_POTION", "EQ_MK_HAT_T1", "EQUIPPED", "HAT"));

            var state = await presenter.EquipAsync("ITM_POTION", CancellationToken.None);

            Assert.True(state.IsLoaded, state.ErrorCode);
            Assert.Equal(5, state.Value.InventoryRevision);
            Assert.Equal("ITM_POTION", state.Value.GetEquipped("HAT").InstanceId);
            Assert.Single(adapter.EquipCalls);
            Assert.Equal(("ITM_POTION", 4L), adapter.EquipCalls[0]);
        }

        [Fact]
        public async Task Equip_UnknownOrEquippedItemSendsNothing()
        {
            var adapter = new FakeInventoryAdapter { Snapshot = Snapshot(4, Item("ITM_HAT", "EQ_MK_HAT", "EQUIPPED", "HAT")) };
            var presenter = new InventoryV2Presenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            var unknown = await presenter.EquipAsync("ITM_NOPE", CancellationToken.None);
            var equipped = await presenter.EquipAsync("ITM_HAT", CancellationToken.None);

            Assert.Equal("not_equippable", unknown.ErrorCode);
            Assert.Equal("not_equippable", equipped.ErrorCode);
            Assert.Empty(adapter.EquipCalls);
        }

        [Fact]
        public async Task Unequip_EmptySlotSendsNothing()
        {
            var adapter = new FakeInventoryAdapter { Snapshot = Snapshot(4) };
            var presenter = new InventoryV2Presenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            var state = await presenter.UnequipAsync("CHEST", CancellationToken.None);

            Assert.Equal("wrong_location", state.ErrorCode);
            Assert.Empty(adapter.UnequipCalls);
        }

        [Fact]
        public async Task RevisionConflict_ShowsNewerSnapshotAndTheError()
        {
            var adapter = new FakeInventoryAdapter { Snapshot = Snapshot(4) };
            var presenter = new InventoryV2Presenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);
            adapter.CommandResult = P1Result.Fail("revision_conflict", "corr");
            adapter.Snapshot = Snapshot(7, Item("ITM_POTION", "EQ_MK_HAT_T1", "EQUIPPED", "HAT"));

            var state = await presenter.EquipAsync("ITM_POTION", CancellationToken.None);

            Assert.True(state.IsError);
            Assert.Equal("revision_conflict", state.ErrorCode);
            Assert.Equal(7, state.Value.InventoryRevision);
            Assert.Equal("ITM_POTION", state.Value.GetEquipped("HAT").InstanceId);
        }

        [Fact]
        public async Task PendingMutation_BlocksNewInventoryCommand()
        {
            var adapter = new FakeInventoryAdapter { Snapshot = Snapshot(4), HasPendingMutation = true };
            var presenter = new InventoryV2Presenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            var state = await presenter.EquipAsync("ITM_POTION", CancellationToken.None);

            Assert.Equal("pending_mutation", state.ErrorCode);
            Assert.Empty(adapter.EquipCalls);
        }

        [Fact]
        public void Death_DownedActorCanRequestWithVietnameseHint()
        {
            var adapter = new FakeDeathAdapter { Self = new P1Self { hp = 0, maxHp = 100 } };
            var presenter = new DeathReturnPresenter(adapter);

            Assert.True(presenter.View.IsDowned);
            Assert.True(presenter.View.CanRequest);
            Assert.Contains("Hồi sinh", presenter.View.HintVi);
        }

        [Fact]
        public async Task Death_AliveActorCannotRequest()
        {
            var adapter = new FakeDeathAdapter { Self = new P1Self { hp = 50, maxHp = 100 } };
            var presenter = new DeathReturnPresenter(adapter);

            var view = await presenter.RequestReturnAsync(CancellationToken.None);

            Assert.False(view.IsDowned);
            Assert.False(view.CanRequest);
            Assert.Equal("not_downed", view.ErrorCode);
            Assert.Equal(0, adapter.Calls);
        }

        [Fact]
        public void Death_CooldownUsesServerTick()
        {
            var adapter = new FakeDeathAdapter
            {
                Self = new P1Self { hp = 0, maxHp = 100 },
                NextReturnAllowedAtTick = 1900
            };
            var presenter = new DeathReturnPresenter(adapter);

            var waiting = presenter.Refresh(1899);
            Assert.False(waiting.CanRequest);
            Assert.Contains("1900", waiting.HintVi);

            var allowed = presenter.Refresh(1900);
            Assert.True(allowed.CanRequest);
        }

        [Fact]
        public async Task Death_CommitRefreshesAuthoritativeHpAndReceipt()
        {
            var adapter = new FakeDeathAdapter { Self = new P1Self { hp = 0, maxHp = 100 } };
            var presenter = new DeathReturnPresenter(adapter);
            adapter.Result = P1Result.Ok();
            adapter.LastDeathReturn = new P1DeathReturnResultV1
            {
                applied = true, replayed = false, mapId = "MAP_BEN_MUA", xWu = 18, yWu = 0,
                hp = 50, maxHp = 100, mp = 50, maxMp = 50, serverTick = 1840, revision = 12,
                cleared = new P1DeathReturnCleared(), penalties = new P1DeathReturnPenalties(),
                nextReturnAllowedAtTick = 1900
            };
            adapter.Self = new P1Self { hp = 50, maxHp = 100 }; // fresh world read after receipt
            adapter.NextReturnAllowedAtTick = 1900;

            var view = await presenter.RequestReturnAsync(CancellationToken.None);

            Assert.Equal(1, adapter.Calls);
            Assert.False(view.IsDowned);
            Assert.True(view.LastApplied);
            Assert.False(view.LastReplayed);
            Assert.Equal(50, view.Hp);
        }

        [Fact]
        public async Task Death_ReplayShowsReplayHintWithoutLocalMove()
        {
            var adapter = new FakeDeathAdapter { Self = new P1Self { hp = 0, maxHp = 100 } };
            var presenter = new DeathReturnPresenter(adapter);
            adapter.LastDeathReturn = new P1DeathReturnResultV1
            {
                applied = false, replayed = true, mapId = "MAP_BEN_MUA", xWu = 18, yWu = 0,
                hp = 50, maxHp = 100, mp = 50, maxMp = 50, serverTick = 1840, revision = 12,
                cleared = new P1DeathReturnCleared(), penalties = new P1DeathReturnPenalties(),
                nextReturnAllowedAtTick = 1900
            };
            adapter.Self = new P1Self { hp = 50, maxHp = 100 };
            adapter.NextReturnAllowedAtTick = 1900;

            var view = await presenter.RequestReturnAsync(CancellationToken.None);

            Assert.True(view.LastReplayed);
            Assert.False(view.LastApplied);
            Assert.Contains("không dịch chuyển lần hai", view.HintVi);
            Assert.Equal(50, view.Hp);
        }

        [Fact]
        public async Task Death_CooldownErrorSurfacesDeadline()
        {
            var adapter = new FakeDeathAdapter
            {
                Self = new P1Self { hp = 0, maxHp = 100 },
                Result = P1Result.Fail("death_return_cooldown"),
                NextReturnAllowedAtTick = 1960
            };
            var presenter = new DeathReturnPresenter(adapter);

            var view = await presenter.RequestReturnAsync(CancellationToken.None);

            Assert.Equal("death_return_cooldown", view.ErrorCode);
            Assert.Equal(1960, view.NextReturnAllowedAtTick);
            Assert.Contains("1960", view.HintVi);
        }

        [Fact]
        public async Task Death_PendingMutationBlocksIntent()
        {
            var adapter = new FakeDeathAdapter
            {
                Self = new P1Self { hp = 0, maxHp = 100 },
                HasPendingMutation = true
            };
            var presenter = new DeathReturnPresenter(adapter);

            var view = await presenter.RequestReturnAsync(CancellationToken.None);

            Assert.False(view.CanRequest);
            Assert.Equal("mutation_outcome_unknown", view.ErrorCode);
            Assert.Equal(0, adapter.Calls);
        }

        [Fact]
        public void InventoryViewState_CopiesSourceCollectionsOnConstruction()
        {
            var slot = new ItemSlotView(new P1Item
            {
                instanceId = "ITEM_1", templateId = "TPL_1", stack = 1,
                location = "BAG", durability = 0, version = 1
            });
            var slots = new Dictionary<int, ItemSlotView> { { 0, slot } };
            var warnings = new[] { "duplicate_slot_index:0:ITEM_DUP" };
            var view = new InventoryViewState(7, slots,
                new[] { new CurrencyView(new P1Currency { currencyId = "COIN", amount = 5 }) },
                diagnosticWarnings: warnings);

            // A caller that reuses its collections after construction cannot
            // change an already-published view.
            slots.Clear();
            warnings[0] = "tampered";
            Assert.Single(view.Slots);
            Assert.Equal("duplicate_slot_index:0:ITEM_DUP", view.DiagnosticWarnings[0]);

            // The exposed collections reject mutation even through a downcast.
            var mutableSlots = view.Slots as IDictionary<int, ItemSlotView>;
            Assert.NotNull(mutableSlots);
            Assert.Throws<NotSupportedException>(() => mutableSlots[9] = slot);
            var mutableCurrencies = view.Currencies as IList<CurrencyView>;
            Assert.NotNull(mutableCurrencies);
            Assert.Throws<NotSupportedException>(() => mutableCurrencies.Add(view.Currencies[0]));
        }

        [Fact]
        public void InventoryV2ViewState_CopiesSourceCollectionsOnConstruction()
        {
            var bagItem = new InventoryV2ItemView(Item("ITEM_BAG", "TPL_BAG", "BAG", null));
            var bag = new List<InventoryV2ItemView> { bagItem };
            var equipment = new Dictionary<string, InventoryV2ItemView> { { "HAT", bagItem } };
            var currencies = new List<CurrencyView>
            {
                new CurrencyView(new P1Currency { currencyId = "COIN", amount = 1 })
            };
            var unsupported = new List<UnsupportedEquipView>();
            var view = new InventoryV2ViewState(3, equipment, bag, unsupported, currencies);

            equipment.Clear();
            bag.Clear();
            currencies.Clear();

            Assert.Single(view.Equipment);
            Assert.Single(view.Bag);
            Assert.Single(view.Currencies);
            Assert.Equal(3, view.InventoryRevision);

            var mutableBag = view.Bag as IList<InventoryV2ItemView>;
            Assert.NotNull(mutableBag);
            Assert.Throws<NotSupportedException>(() => mutableBag.Add(bagItem));
            var mutableEquipment = view.Equipment as IDictionary<string, InventoryV2ItemView>;
            Assert.NotNull(mutableEquipment);
            Assert.Throws<NotSupportedException>(() => mutableEquipment["WEAPON"] = bagItem);
        }
    }
}
