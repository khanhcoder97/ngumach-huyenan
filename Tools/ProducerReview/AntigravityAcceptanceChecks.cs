using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace ProducerAcceptance
{
    // Expected catalog values are copied from canonical rarity CSV, not the resolver.
    // Fake read completion isolates UI lifetime; this is not live HTTP or Unity.
    public sealed class AcceptanceChecks
    {
        [Theory]
        [InlineData("REFINED", "Tinh Kiếm Mưa Khởi Minh Kiếm", "Tinh")]
        [InlineData("SPIRIT", "Linh Kiếm Mưa Khởi Minh Kiếm", "Linh")]
        [InlineData("ARCANE", "Huyền Kiếm Mưa Khởi Minh Kiếm", "Huyền")]
        [InlineData("RELIC", "Cổ Vật Kiếm Mưa Khởi Minh Kiếm", "Cổ Vật")]
        public void CanonicalRarityVariantKeepsItsOwnMetadata(string suffix,string name,string rarity)
        {
            var meta=ItemMetadataResolver.Resolve("EQ-MK-WEAPON-T1-R-"+suffix);
            Assert.Equal(name,meta.DisplayName);
            Assert.Equal(rarity,meta.Rarity);
        }
        [Fact]
        public void CommonVariantControl()
        {
            var meta=ItemMetadataResolver.Resolve("EQ-MK-WEAPON-T1-R-COMMON");
            Assert.Equal("Thường Kiếm Mưa Khởi Minh Kiếm",meta.DisplayName);
            Assert.Equal("Thường",meta.Rarity);
        }
        [Fact]
        public void UnknownPrefixCannotInheritKnownItemClassAndSlot()
        {
            var meta=ItemMetadataResolver.Resolve("EQ-MK-WEAPON-T1-NOT_A_CATALOG_RECORD");
            Assert.Null(meta.ClassId);
            Assert.Null(meta.Slot);
        }
        private sealed class Adapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState=>UIConnectionState.Ready;
            public bool HasPendingMutation=>false;
            public string LastErrorCode=>null;
            public string LastCorrelationId=>null;
            public P1Self Self {get;set;}=new P1Self {characterId="PLAYER_FIXTURE",classId="CLASS_MINH_KIEM"};
            public P1World World=>null;
            public P1WorldV2 WorldV2=>null;
            public P1Inventory Inventory {get;set;}
            public P1Quest[] Quests {get;set;}
            public TaskCompletionSource<P1Result> DelayedRead;
            public Task<P1Result> ReadInventoryAsync(CancellationToken ct)=>DelayedRead?.Task??Task.FromResult(P1Result.Ok());
            public Task<P1Result> ReadQuestsAsync(CancellationToken ct)=>DelayedRead?.Task??Task.FromResult(P1Result.Ok());
            public Task<P1Result> AcceptQuestAsync(string q,string n,CancellationToken ct)=>Task.FromResult(P1Result.Ok());
            public Task<P1Result> TurnInQuestAsync(string q,string n,CancellationToken ct)=>Task.FromResult(P1Result.Ok());
            public Task<P1Result> InteractAsync(string n,CancellationToken ct)=>Task.FromResult(P1Result.Ok());
            public Task<P1Result> RetryPendingAsync(CancellationToken ct)=>Task.FromResult(P1Result.Ok());
        }
        [Theory]
        [InlineData("BANK")]
        [InlineData("BAG")]
        public void LocationIsAuthoritativeForEquippedItems(string location)
        {
            var adapter=new Adapter {Inventory=new P1Inventory {items=new[] {
                new P1Item {instanceId="INSTANCE_FIXTURE",templateId="EQ-MK-WEAPON-T1-R-COMMON",location=location,slot="MAIN_HAND",stack=1}}}};
            var p=new CharacterPresenter(adapter);p.Refresh();
            Assert.Null(p.State.Value.GetEquippedItem("MAIN_HAND"));
        }
        [Fact]
        public void EquippedLocationControl()
        {
            var adapter=new Adapter {Inventory=new P1Inventory {items=new[] {
                new P1Item {instanceId="INSTANCE_FIXTURE",templateId="EQ-MK-WEAPON-T1-R-COMMON",location="EQUIPPED",slot="MAIN_HAND",stack=1}}}};
            var p=new CharacterPresenter(adapter);p.Refresh();
            Assert.NotNull(p.State.Value.GetEquippedItem("MAIN_HAND"));
        }
        [Fact]
        public async Task CancelledInventoryLifetimeIgnoresSuccessfulLateRead()
        {
            var completion=new TaskCompletionSource<P1Result>(TaskCreationOptions.RunContinuationsAsynchronously);
            var adapter=new Adapter {DelayedRead=completion,Inventory=new P1Inventory {inventoryRevision=1,items=Array.Empty<P1Item>()}};
            var p=new InventoryPresenter(adapter);using var life=new CancellationTokenSource();
            var task=p.LoadAsync(life.Token);life.Cancel();completion.SetResult(P1Result.Ok());
            try {await task;} catch(OperationCanceledException) {}
            Assert.Null(p.State.Value);
            Assert.False(p.State.IsLoading);
        }
        [Fact]
        public async Task CancelledJournalLifetimeIgnoresSuccessfulLateRead()
        {
            var completion=new TaskCompletionSource<P1Result>(TaskCreationOptions.RunContinuationsAsynchronously);
            var adapter=new Adapter {DelayedRead=completion,Quests=new[] {new P1Quest {questId="P00-01",state="ACTIVE",revision=1}}};
            var p=new QuestJournalPresenter(adapter);using var life=new CancellationTokenSource();
            var task=p.LoadAsync(life.Token);life.Cancel();completion.SetResult(P1Result.Ok());
            try {await task;} catch(OperationCanceledException) {}
            Assert.Null(p.State.Value);
            Assert.False(p.State.IsLoading);
        }
        [Fact]
        public void UnknownNpcDoesNotForgeCanonicalTemplateIdentity()
        {
            var context=NpcContextMapping.Resolve("ENT_UNKNOWN_UNREGISTERED");
            Assert.NotEqual("ENT_UNKNOWN_UNREGISTERED",context?.TemplateId);
        }
        [Fact]
        public void TestQuestIsNotInProductionAssociationCatalog()
        {
            Assert.False(QuestNpcCatalog.IsQuestStartNpc("Q1","NPC_TEST"));
            Assert.False(QuestNpcCatalog.IsQuestTurnInNpc("QUEST_TEST","NPC_TEST"));
        }
    }
}
