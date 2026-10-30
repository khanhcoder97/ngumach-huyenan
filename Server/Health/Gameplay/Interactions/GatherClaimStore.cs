using System.Collections.Concurrent;
using Server.Health.World;

namespace Server.Health.Gameplay.Interactions;

// Per-character claims: gather nodes (manifest shard rule "Node riêng theo
// shard; hồi riêng theo người chơi") and per-character interactables
// (Production Rules §5 P00-01 packages). Each character has its own
// availability window; other characters can still claim the same entity.
public sealed class GatherClaimStore
{
    private readonly ConcurrentDictionary<(string CharacterId, string EntityId), GatherClaim>
        _claims = new();

    private readonly IServerClock _clock;

    public GatherClaimStore(IServerClock clock)
    {
        _clock = clock;
    }

    // Atomic check-and-set: two parallel claims for the same key cannot both
    // observe an expired window and both win. Each winning claim is tagged with
    // a reservation token so a later rollback only releases its own reservation.
    public bool TryClaim(
        string characterId,
        string entityId,
        int respawnSeconds,
        out DateTimeOffset respawnAtUtc,
        out string token)
    {
        var key = (characterId, entityId);
        var now = _clock.UtcNow;
        token = Guid.NewGuid().ToString("N");
        var candidate = new GatherClaim(now, token);

        var current = _claims.AddOrUpdate(
            key,
            addValue: candidate,
            updateValueFactory: (_, existing) =>
                respawnSeconds > 0 && now >= existing.ClaimedAt.AddSeconds(respawnSeconds)
                    ? candidate
                    : existing);

        if (!ReferenceEquals(current, candidate))
        {
            token = current.Token;
            respawnAtUtc = respawnSeconds > 0
                ? current.ClaimedAt.AddSeconds(respawnSeconds)
                : DateTimeOffset.MinValue;
            return false;
        }

        respawnAtUtc = respawnSeconds > 0
            ? now.AddSeconds(respawnSeconds)
            : DateTimeOffset.MinValue;
        return true;
    }

    // Read-only availability probe for the audience projection: true when the
    // character has no active claim window on the entity. Mutates nothing.
    public bool IsAvailable(string characterId, string entityId, int respawnSeconds)
    {
        if (!_claims.TryGetValue((characterId, entityId), out var stored))
        {
            return true;
        }

        return respawnSeconds > 0 &&
               _clock.UtcNow >= stored.ClaimedAt.AddSeconds(respawnSeconds);
    }

    // Undo a claim made by TryClaim; used when a later step of the interaction
    // (e.g. the inventory grant) fails so the failed request does not consume
    // the node's availability window. Compare-and-remove by reservation token:
    // a failed request can never delete another request's claim.
    public void Release(string characterId, string entityId, string token)
    {
        var key = (characterId, entityId);
        if (!_claims.TryGetValue(key, out var stored) ||
            !string.Equals(stored.Token, token, StringComparison.Ordinal))
        {
            return;
        }

        _claims.TryRemove(new KeyValuePair<(string, string), GatherClaim>(key, stored));
    }

    private sealed record GatherClaim(DateTimeOffset ClaimedAt, string Token);
}

public interface IYieldRoller
{
    int Roll(int minInclusive, int maxInclusive);
}

public sealed class SystemYieldRoller : IYieldRoller
{
    public int Roll(int minInclusive, int maxInclusive) =>
        Random.Shared.Next(minInclusive, maxInclusive + 1);
}
