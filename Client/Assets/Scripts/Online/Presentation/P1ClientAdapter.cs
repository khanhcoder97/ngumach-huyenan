// AG1 — Concrete adapter wrapping the live P1Client.
// Translates P1ConnectionState → UIConnectionState; exposes read-only view.
// Owner: Antigravity Remote — Issue #80.

using System;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    /// <summary>
    /// Wraps a live <see cref="P1Client"/> and exposes the UI surface.
    /// Does NOT cache inventory/quest data locally beyond what P1Client already holds.
    /// </summary>
    public sealed class P1ClientAdapter : IP1UIAdapter
    {
        private readonly P1Client _client;

        public P1ClientAdapter(P1Client client)
            => _client = client ?? throw new ArgumentNullException(nameof(client));

        public UIConnectionState ConnectionState => Map(_client.State);
        public bool HasPendingMutation => _client.HasPendingMutation;
        public string LastErrorCode => _client.LastError;
        public string LastCorrelationId => _client.LastCorrelationId;

        public P1Self Self => _client.World?.self;
        public P1World World => _client.UseWorldV2 ? null : _client.World;
        public P1WorldV2 WorldV2 => _client.UseWorldV2 ? _client.WorldV2 : null;

        public P1Quest[] Quests => _client.Quests;
        public P1Inventory Inventory => _client.Inventory;

        public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => _client.ReadQuestsAsync(ct);
        public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => _client.ReadInventoryAsync(ct);
        public Task<P1Result> AcceptQuestAsync(string questId, string npcId, CancellationToken ct) => _client.AcceptQuestAsync(questId, npcId, ct);
        public Task<P1Result> RetryPendingAsync(CancellationToken ct) => _client.RetryPendingAsync(ct);

        public Task<P1Result> InteractAsync(string targetId, CancellationToken ct)
            => _client.InteractAsync(targetId, ct);

        public Task<P1Result> TurnInQuestAsync(string questId, string npcId, CancellationToken ct)
            => _client.TurnInQuestAsync(questId, npcId, ct);

        private static UIConnectionState Map(P1ConnectionState s) => s switch
        {
            P1ConnectionState.Disconnected      => UIConnectionState.Disconnected,
            P1ConnectionState.Connecting        => UIConnectionState.Connecting,
            P1ConnectionState.Ready             => UIConnectionState.Ready,
            P1ConnectionState.NeedsResync       => UIConnectionState.NeedsResync,
            P1ConnectionState.UncertainMutation => UIConnectionState.UncertainMutation,
            P1ConnectionState.Expired           => UIConnectionState.Expired,
            _                                   => UIConnectionState.Error
        };
    }
}
