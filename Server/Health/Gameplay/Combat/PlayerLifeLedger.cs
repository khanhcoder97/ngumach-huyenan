using System.Security.Cryptography;
using System.Text.Json;

namespace Server.Health.Gameplay.Combat;

// DEC-DEATH-RETURN-20261105 (option 2): the player's own death and life
// bookkeeping, kept inside the server.
//
// It is not a CombatEventV2 and cannot become one: the frozen event contract
// requires actorId ^CHR_ together with a castId, and the decision says
// explicitly "internal domain record; do not add CombatEventV2 type or fields to
// existing frozen wire". A player death has no cast of its own — a mob, the boss
// encounter or the training wave ends the life.
//
// The event id is derived, never minted: SHA-256 over the canonical JSON array
// [characterId, lifeVersion, deathRevision], so two commits of the same
// transition produce the same id and nothing about it is random. State is keyed
// by character, never by session, because the decision requires it to survive a
// reconnect.
public sealed record PlayerDeathRecord(
    string CharacterId,
    int LifeVersion,
    long DeathRevision,
    string DeathEventId,
    DateTimeOffset AtUtc);

public sealed class PlayerLifeLedger
{
    // Bounded the same way the death-return ledger is: a long-lived process
    // cannot grow with actor count, and an evicted character simply starts its
    // life numbering again at 1 — which only ever renumbers a life whose death
    // was never returned, so no receipt can be double-paid by an eviction.
    public const int Capacity = 256;

    public const string DeathEventIdPrefix = "PDEATH_";

    private readonly object _sync = new();
    private readonly Dictionary<string, LifeState> _states = new(StringComparer.Ordinal);
    private readonly Queue<string> _order = new();

    public int LifeVersion(string characterId)
    {
        lock (_sync)
        {
            return _states.TryGetValue(characterId, out var state) ? state.LifeVersion : 1;
        }
    }

    public PlayerDeathRecord? LatestDeath(string characterId)
    {
        lock (_sync)
        {
            return _states.TryGetValue(characterId, out var state) ? state.LastDeath : null;
        }
    }

    // Called by every damage path, inside the actor lock, right after the HP and
    // the aggregate revision are committed. Only a positive-to-zero transition
    // records, so a second hit on an already-downed actor cannot create a second
    // death for the same life. Returns the record this commit produced, or null
    // when the commit did not end a life.
    public PlayerDeathRecord? RecordDamageCommit(
        string characterId,
        int hpBefore,
        int hpAfter,
        long deathRevision,
        DateTimeOffset atUtc)
    {
        if (hpBefore <= 0 || hpAfter != 0)
        {
            return null;
        }

        lock (_sync)
        {
            var state = Track(characterId);
            if (state.LastDeath is { } prior && prior.DeathRevision == deathRevision)
            {
                // The same commit reaching the ledger twice (a retry inside one
                // tick) is the same death, not a new one.
                return prior;
            }

            var record = new PlayerDeathRecord(
                characterId,
                state.LifeVersion,
                deathRevision,
                DeathEventIdFor(characterId, state.LifeVersion, deathRevision),
                atUtc);
            state.LastDeath = record;
            return record;
        }
    }

    // The other half of the pair: a committed resurrection (zero to positive)
    // advances the life exactly once. A replayed return never reaches this, and
    // neither does any refusal, so the counter cannot drift ahead of the deaths
    // it numbers.
    public int RecordResurrectionCommit(string characterId, int hpBefore, int hpAfter)
    {
        if (hpBefore != 0 || hpAfter <= 0)
        {
            return LifeVersion(characterId);
        }

        lock (_sync)
        {
            var state = Track(characterId);
            state.LifeVersion++;
            return state.LifeVersion;
        }
    }

    public static string DeathEventIdFor(string characterId, int lifeVersion, long deathRevision)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream))
        {
            writer.WriteStartArray();
            writer.WriteStringValue(characterId);
            writer.WriteNumberValue(lifeVersion);
            writer.WriteNumberValue(deathRevision);
            writer.WriteEndArray();
        }

        return DeathEventIdPrefix +
               Convert.ToHexString(SHA256.HashData(stream.ToArray())).ToLowerInvariant();
    }

    private LifeState Track(string characterId)
    {
        if (_states.TryGetValue(characterId, out var existing))
        {
            return existing;
        }

        if (_states.Count >= Capacity && _order.TryDequeue(out var oldest))
        {
            _states.Remove(oldest!);
        }

        var state = new LifeState();
        _states[characterId] = state;
        _order.Enqueue(characterId);
        return state;
    }

    private sealed class LifeState
    {
        public int LifeVersion = 1;
        public PlayerDeathRecord? LastDeath;
    }
}
