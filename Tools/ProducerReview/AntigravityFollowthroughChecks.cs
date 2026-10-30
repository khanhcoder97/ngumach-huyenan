using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace ProducerFollowthrough
{
    // Synthetic transport outcome; IDs below come from world_entities_bm.json.
    // These checks exercise real presenters, not native Unity or live HTTP.
    public sealed class DialogueIdentityAndLifetimeChecks
    {
        private sealed class Adapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState => UIConnectionState.Ready;
            public bool HasPendingMutation => false;
            public string LastErrorCode => null;
            public string LastCorrelationId => null;
            public P1Self Self => null;
            public P1World World => null;
            public P1WorldV2 WorldV2 => null;
            public P1Inventory Inventory => null;
            public P1Quest[] Quests { get; set; }
            public Func<Task<P1Result>> OnInteract;
            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> AcceptQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> InteractAsync(string id, CancellationToken ct) => OnInteract?.Invoke() ?? Task.FromResult(P1Result.Ok());
            public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
        }

        private static Adapter WithQuest(string state) => new Adapter { Quests = new[] {
            new P1Quest {questId="P00-01",state=state,stepId="STEP_FIXTURE",revision=1,
                         objectiveCounters=new Dictionary<string,int>()} } };

        [Theory]
        [InlineData("NPC_LYAN", "AVAILABLE", DialogueActionType.AcceptQuest)]
        [InlineData("NPC_TA_VAN_KHANH", "READY_TO_TURN_IN", DialogueActionType.TurnInQuest)]
        public async Task TemplateIdentityControl(string id, string state, DialogueActionType action)
        {
            var presenter = new NpcDialoguePresenter(WithQuest(state));
            await presenter.InteractAsync(id, CancellationToken.None);
            Assert.Contains(presenter.State.Value.Choices, c => c.Enabled && c.ActionType == action);
        }

        [Theory]
        [InlineData("ENT_MAN_BM_NPC_LYAN", "AVAILABLE", DialogueActionType.AcceptQuest)]
        [InlineData("ENT_MAN_BM_NPC_TA_VAN_KHANH", "READY_TO_TURN_IN", DialogueActionType.TurnInQuest)]
        public async Task WorldEntityIdentityMustResolveQuestAction(string entityId, string state, DialogueActionType action)
        {
            var presenter = new NpcDialoguePresenter(WithQuest(state));
            await presenter.InteractAsync(entityId, CancellationToken.None);
            Assert.Contains(presenter.State.Value.Choices, c => c.Enabled && c.ActionType == action);
        }

        [Fact]
        public async Task ClearedDialogueMustIgnoreLateCompletion()
        {
            var response = new TaskCompletionSource<P1Result>(TaskCreationOptions.RunContinuationsAsynchronously);
            var adapter = WithQuest("AVAILABLE");
            adapter.OnInteract = () => response.Task; // models response arriving after UI reset
            var presenter = new NpcDialoguePresenter(adapter);
            var request = presenter.InteractAsync("NPC_LYAN", CancellationToken.None);
            Assert.True(presenter.State.IsLoading);
            presenter.Clear();
            response.SetResult(P1Result.Ok());
            await request;
            Assert.Equal(LoadPhase.Idle, presenter.State.Phase);
            Assert.Null(presenter.State.Value);
        }
    }
}
