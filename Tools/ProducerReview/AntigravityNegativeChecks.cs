using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace PlayerUIChecks
{
    public class ProducerNegativeChecks
    {
        // Synthetic fixtures matching optional-slot BAG wire shape; no balance values.
        [Fact]
        public async Task ValidBagItemWithoutSlotMustBeVisible()
        {
            var adapter = new FakeAdapter { Inventory = new P1Inventory {
                inventoryRevision = 1,
                items = new[] { new P1Item { instanceId="ITM_REVIEW_A", templateId="TOOL-ROD-01", location="BAG", stack=1, durability=100, version=1 } },
                currencies = Array.Empty<P1Currency>() } };
            var presenter = new InventoryPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);
            Assert.Single(presenter.State.Value.Slots);
        }

        [Fact]
        public async Task EquipmentMustNotOccupyBagCell()
        {
            var adapter = new FakeAdapter { Inventory = new P1Inventory {
                inventoryRevision=1,
                items=new[] {new P1Item {instanceId="ITM_REVIEW_E",templateId="TOOL-ROD-01",location="EQUIPPED",slot="MAIN_HAND",stack=1,durability=100,version=1}},
                currencies=Array.Empty<P1Currency>() } };
            var presenter=new InventoryPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);
            Assert.DoesNotContain(presenter.State.Value.DiagnosticWarnings,x=>x.StartsWith("out_of_range_slot"));
        }

        [Fact]
        public async Task CancelledReadMustNotLeaveLoadingForever()
        {
            var adapter=new FakeAdapter {OnReadInventory=()=>Task.FromException<P1Result>(new OperationCanceledException())};
            var presenter=new InventoryPresenter(adapter);
            try { await presenter.LoadAsync(CancellationToken.None); } catch(OperationCanceledException) { }
            Assert.False(presenter.State.IsLoading);
        }

        [Fact]
        public async Task QuestReadyMustNotOfferTurnInAtEveryNpc()
        {
            var adapter=new FakeAdapter {Quests=new[] {new P1Quest {
                questId="P00-01",state="READY_TO_TURN_IN",stepId="STEP_REVIEW",
                objectiveCounters=new Dictionary<string,int>(),revision=1 }}};
            var presenter=new NpcDialoguePresenter(adapter);
            await presenter.InteractAsync("NPC_UNRELATED_REVIEW",CancellationToken.None);
            Assert.DoesNotContain(presenter.State.Value.Choices,c=>c.Enabled && c.Label.StartsWith("[Nộp nhiệm vụ]"));
        }
    }
}
