using System.Collections.Concurrent;
using Server.Health.World;

namespace Server.Health.Gameplay.Interactions;

// Per-character gather claims. Canonical manifest rule: "Node riêng theo shard;
// hồi riêng theo người chơi" — each character has its own availability window,
// other characters can still claim the same node.
public sealed class GatherClaimStore
{
    private readonly ConcurrentDictionary<(string CharacterId, string EntityId), DateTimeOffset>
        _claims = new();

    private readonly IServerClock _clock;

    public GatherClaimStore(IServerClock clock)
    {
        _clock = clock;
    }

    public bool TryClaim(
        string characterId,
        string entityId,
        int respawnSeconds,
        out DateTimeOffset respawnAtUtc)
    {
        var key = (characterId, entityId);
        var now = _clock.UtcNow;

        if (respawnSeconds <= 0)
        {
            respawnAtUtc = DateTimeOffset.MinValue;
            return _claims.TryAdd(key, now);
        }

        if (_claims.TryGetValue(key, out var claimedAt) &&
            now < claimedAt.AddSeconds(respawnSeconds))
        {
            respawnAtUtc = claimedAt.AddSeconds(respawnSeconds);
            return false;
        }

        _claims[key] = now;
        respawnAtUtc = now.AddSeconds(respawnSeconds);
        return true;
    }

    // Undo a claim made by TryClaim; used when a later step of the interaction
    // (e.g. the inventory grant) fails so the failed request does not consume
    // the node's availability window.
    public void Release(string characterId, string entityId)
    {
        _claims.TryRemove((characterId, entityId), out _);
    }
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
