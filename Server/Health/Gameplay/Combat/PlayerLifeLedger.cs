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
    // Retention rule, replacing the arrival-order bound the progress review filed as a
    // live-character loss. An entry may be reclaimed only when that character's life is
    // CLOSED: it is standing with no death recorded here, or it has already been returned,
    // so the death on file belongs to an earlier life than the one it is living now. A
    // character that is downed and not yet returned is pinned, because evicting it restarts
    // its life numbering at 1 and lets the next death of what is really the same life mint
    // a fresh identity - the double-pay the receipt exists to prevent.
    //
    // If every entry is pinned the ledger grows past this number and says so, instead of
    // discarding a receipt to keep a round figure. Reclaiming under a real expiry rule
    // needs persistence, which is the published scope of the QODER Remote Server/Persistence
    // track; this type does not get to invent one.
    public const int Capacity = 256;

    public const string DeathEventIdPrefix = "PDEATH_";

    private readonly object _sync = new();
    private readonly Dictionary<string, LifeState> _states = new(StringComparer.Ordinal);
    private long _touchClock;
    private int _exceededBy;

    // Observability for the rule above, so growth is a reported consequence instead of an
    // invisible leak: how many characters are tracked, how many are pinned by an
    // unredeemed death, and how many times the bound had to be exceeded.
    public int TrackedCharacters
    {
        get
        {
            lock (_sync)
            {
                return _states.Count;
            }
        }
    }

    public int PinnedCharacters
    {
        get
        {
            lock (_sync)
            {
                return _states.Values.Count(state => !IsClosable(state));
            }
        }
    }

    public int CapacityExceededBy
    {
        get
        {
            lock (_sync)
            {
                return _exceededBy;
            }
        }
    }

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
            existing.LastTouched = ++_touchClock;
            return existing;
        }

        if (_states.Count >= Capacity)
        {
            var reclaimable = _states
                .Where(pair => IsClosable(pair.Value))
                .OrderBy(pair => pair.Value.LastTouched)
                .Select(pair => pair.Key)
                .ToList();
            if (reclaimable.Count == 0)
            {
                // Every tracked character is downed and unreturned. Growing is the only
                // honest option: dropping one would renumber a life still owed a return.
                _exceededBy++;
            }
            else
            {
                _states.Remove(reclaimable[0]);
            }
        }

        var state = new LifeState { LastTouched = ++_touchClock };
        _states[characterId] = state;
        return state;
    }

    // A life is reclaimable when nothing is owed on it: either the character never died in
    // this ledger, or the death on record belongs to a life it has already left.
    private static bool IsClosable(LifeState state) =>
        state.LastDeath is not { } death || death.LifeVersion < state.LifeVersion;

    private sealed class LifeState
    {
        public int LifeVersion = 1;
        public PlayerDeathRecord? LastDeath;
        public long LastTouched;
    }
}
