// AG1 — Concrete adapter wrapping the live P1Client.
// Translates P1ConnectionState → UIConnectionState; exposes read-only view.
// Owner: Antigravity Remote — Issue #80.
// OPC-17 O-B: the adapter can be bound to a *provider* instead of one fixed
// P1Client so a presenters-held reference follows the composition root across
// relogin and never talks to a dead epoch. Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    /// <summary>
    /// Wraps a live <see cref="P1Client"/> and exposes the UI surface.
    /// Does NOT cache inventory/quest data locally beyond what P1Client already holds.
    /// </summary>
    public sealed class P1ClientAdapter : IP1UIAdapter, IP1InventoryV2Adapter, IP1DeathReturnAdapter, IP1TalkAdapter, IP1CombatHudAdapter
    {
        private static readonly IReadOnlyDictionary<string, string> EmptyCooldowns =
            new Dictionary<string, string>(StringComparer.Ordinal);

        private readonly P1Client _client;
        private readonly Func<P1Client> _provider;

        public P1ClientAdapter(P1Client client)
            => _client = client ?? throw new ArgumentNullException(nameof(client));

        // Lifetime-guarded binding: the provider returns null once the owning
        // ClientSession is disposed, so a presenter that outlives the session
        // reads an empty projection and its commands fail typed instead of
        // touching a dead transport or the previous session's state.
        internal P1ClientAdapter(Func<P1Client> provider)
            => _provider = provider ?? throw new ArgumentNullException(nameof(provider));

        // Null only for a provider-bound adapter whose session was disposed.
        private P1Client Current => _provider != null ? _provider() : _client;

        public UIConnectionState ConnectionState
        {
            get
            {
                var client = Current;
                return client == null ? UIConnectionState.Disconnected : Map(client.State);
            }
        }

        public bool HasPendingMutation => Current?.HasPendingMutation ?? false;
        public string LastErrorCode => Current?.LastError;
        public string LastCorrelationId => Current?.LastCorrelationId;

        public P1Self Self => Current?.World?.self;
        public P1World World
        {
            get
            {
                var client = Current;
                if (client == null || client.UseWorldV2) return null;
                return client.World;
            }
        }
        public P1WorldV2 WorldV2
        {
            get
            {
                var client = Current;
                if (client == null || !client.UseWorldV2) return null;
                return client.WorldV2;
            }
        }
        public bool UseWorldV2 => Current?.UseWorldV2 ?? false;

        public P1Quest[] Quests => Current?.Quests ?? Array.Empty<P1Quest>();
        public P1Inventory Inventory => Current?.Inventory;

        // V2 surface kept off IP1UIAdapter so existing fake adapters stay valid.
        public P1InventorySnapshotV2 InventoryV2 => Current?.InventoryV2;
        public P1DeathReturnResultV1 LastDeathReturn => Current?.LastDeathReturn;
        public long? NextReturnAllowedAtTick => Current?.NextReturnAllowedAtTick;

        public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => Guard(Current, c => c.ReadQuestsAsync(ct));
        public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => Guard(Current, c => c.ReadInventoryAsync(ct));
        public Task<P1Result> ReadWorldAsync(CancellationToken ct) => Guard(Current, c => c.ReadWorldAsync(ct));
        public Task<P1Result> ReadInventoryV2Async(CancellationToken ct) => Guard(Current, c => c.ReadInventoryV2Async(ct));
        public Task<P1Result> EquipV2Async(string itemInstanceId, long expectedRevision, CancellationToken ct)
            => Guard(Current, c => c.EquipV2Async(itemInstanceId, expectedRevision, ct));
        public Task<P1Result> UnequipV2Async(string slotId, long expectedRevision, CancellationToken ct)
            => Guard(Current, c => c.UnequipV2Async(slotId, expectedRevision, ct));
        public Task<P1Result> ReturnFromDeathAsync(CancellationToken ct) => Guard(Current, c => c.ReturnFromDeathAsync(ct));
        public Task<P1Result> AcceptQuestAsync(string questId, string npcId, CancellationToken ct)
            => Guard(Current, c => c.AcceptQuestAsync(questId, npcId, ct));
        public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Guard(Current, c => c.RetryPendingAsync(ct));
        public Task<P1Result> TalkAsync(string npcId, string nodeId, CancellationToken ct)
            => Guard(Current, c => c.TalkAsync(npcId, nodeId, ct));
        public Task<P1Result> PortalAsync(string portalId, CancellationToken ct)
            => Guard(Current, c => c.PortalAsync(portalId, ct));
        public Task<P1Result> MapViewedAsync(string questId, CancellationToken ct)
            => Guard(Current, c => c.MapViewedAsync(questId, ct));
        public P1QuestTalkResult LastTalk => Current?.LastTalk;
        public P1WorldPortalResult LastPortal => Current?.LastPortal;
        public P1QuestMapViewedResult LastMapViewed => Current?.LastMapViewed;

        public IReadOnlyDictionary<string, string> CooldownEndsAtUtc => Current?.CooldownEndsAtUtc ?? EmptyCooldowns;
        public Task<P1Result> BasicAttackAsync(string targetId, double aimX, double aimY, CancellationToken ct)
            => Guard(Current, c => c.BasicAttackAsync(targetId, aimX, aimY, ct));
        public Task<P1Result> CastAsync(string skillId, string targetId, double aimX, double aimY, CancellationToken ct)
            => Guard(Current, c => c.CastAsync(skillId, targetId, aimX, aimY, ct));

        public Task<P1Result> InteractAsync(string targetId, CancellationToken ct)
            => Guard(Current, c => c.InteractAsync(targetId, ct));

        public Task<P1Result> TurnInQuestAsync(string questId, string npcId, CancellationToken ct)
            => Guard(Current, c => c.TurnInQuestAsync(questId, npcId, ct));

        private static Task<P1Result> Guard(P1Client client, Func<P1Client, Task<P1Result>> call)
        {
            // Disposed composition root: fail typed, never touch the transport.
            if (client == null) return Task.FromResult(P1Result.Fail("disposed"));
            return call(client);
        }

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
