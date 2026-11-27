using System.Collections.Concurrent;
using System.Text.RegularExpressions;
using Server.Health.Contracts;

namespace Server.Health.Gameplay.Combat;

// QOD-16 phase 2 reliable event read (owner decision Q3): typed, versioned
// combat events with a monotonic per-session cursor, a bounded buffer and an
// explicit resync signal instead of silently dropping events. Internal domain
// only — the v2 HTTP surface lands with the combat tick engine (QOD-17).
public static class CombatEventTypesV2
{
    public const string CastStart = "CAST_START";
    public const string CounterConfirmed = "COUNTER_CONFIRMED";
    public const string Impact = "IMPACT";
    public const string Miss = "MISS";
    public const string Cancel = "CANCEL";
    public const string End = "END";
    public const string Death = "DEATH";

    public static bool IsKnown(string? value) => value is
        CastStart or CounterConfirmed or Impact or Miss or Cancel or End or Death;
}

public static class CombatEventResyncReasons
{
    // Requested cursor is ahead of the stream (stale client or a stream that
    // restarted after reconnect): reconcile from a snapshot.
    public const string CursorTooOld = "CURSOR_TOO_OLD";

    // The requested range was evicted by the bounded buffer: the client missed
    // events and must reconcile from a snapshot instead of guessing.
    public const string BufferOverflow = "BUFFER_OVERFLOW";
}

public sealed record CombatEventResultV2(
    bool Hit,
    bool Crit,
    bool Immune,
    int Amount,
    int Absorbed,
    int HpDamage);

public sealed record CombatEventV2(
    string EventId,
    string Type,
    string CastId,
    string ActorId,
    string? TargetId,
    long? TargetLifeId,
    int? HitIndex,
    string MapInstanceId,
    string FloorId,
    long SourceRevision,
    long? TargetRevision,
    long ServerTick,
    DateTimeOffset EmittedAtUtc,
    CombatEventResultV2? Result)
{
    public long Cursor { get; init; }
}

public sealed record CombatEventReadResult(
    long NextCursor,
    bool ResyncRequired,
    string? ResyncReason,
    IReadOnlyList<CombatEventV2> Events);

public sealed class CombatEventStreamOptions
{
    public const string SectionName = "P1:CombatEventStream";

    // DEV budget per session, not a production capacity decision; overflow is
    // reported to clients (BUFFER_OVERFLOW) rather than silently dropped.
    public int CapacityPerSession { get; set; } = 512;

    public int MaxPageSize { get; set; } = 200;
}

public static class CombatEventStreamOptionsValidator
{
    public static void Validate(CombatEventStreamOptions options)
    {
        if (options.CapacityPerSession < 1)
        {
            throw new InvalidOperationException(
                "P1:CombatEventStream:CapacityPerSession must be at least 1.");
        }

        if (options.MaxPageSize < 1 || options.MaxPageSize > options.CapacityPerSession)
        {
            throw new InvalidOperationException(
                "P1:CombatEventStream:MaxPageSize must be within 1..CapacityPerSession.");
        }
    }
}

public sealed class CombatEventStore
{
    private static readonly Regex MapInstanceIdPattern =
        new(@"^MAP_[A-Z0-9_]+#[0-9]+$", RegexOptions.CultureInvariant);

    private readonly ConcurrentDictionary<string, SessionStream> _streams =
        new(StringComparer.Ordinal);

    private readonly CombatEventStreamOptions _options;

    public CombatEventStore(CombatEventStreamOptions options)
    {
        CombatEventStreamOptionsValidator.Validate(options);
        _options = options;
    }

    public int SessionCount => _streams.Count;

    // Append validates the typed-event invariants, assigns the next monotonic
    // cursor and returns the stored event. Re-appending the same eventId is a
    // no-op that returns the stored copy (replay safe inside the retained
    // window; command-level idempotency remains the primary replay guard).
    public CombatEventV2 Append(string sessionId, CombatEventV2 input)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(sessionId);
        ArgumentNullException.ThrowIfNull(input);
        ValidateEvent(input);

        var stream = _streams.GetOrAdd(sessionId, _ => new SessionStream());
        lock (stream.SyncRoot)
        {
            if (stream.ByEventId.TryGetValue(input.EventId, out var existing))
            {
                return existing;
            }

            var stored = input with { Cursor = stream.NextCursor };
            stream.NextCursor++;
            stream.Events.Enqueue(stored);
            stream.ByEventId[input.EventId] = stored;
            while (stream.Events.Count > _options.CapacityPerSession)
            {
                var evicted = stream.Events.Dequeue();
                stream.ByEventId.Remove(evicted.EventId);
            }

            return stored;
        }
    }

    // Read returns events with cursor > afterCursor in stream order. Readers
    // that fell behind the bounded buffer, or that present a cursor from a
    // previous stream lifetime, get ResyncRequired with a reason and no
    // events — they reconcile from the next snapshot and continue.
    public CombatEventReadResult Read(string sessionId, long afterCursor, int maxItems)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(sessionId);
        afterCursor = Math.Max(0, afterCursor);
        var limit = maxItems <= 0
            ? _options.MaxPageSize
            : Math.Min(maxItems, _options.MaxPageSize);

        if (!_streams.TryGetValue(sessionId, out var stream))
        {
            return new CombatEventReadResult(0, false, null, []);
        }

        lock (stream.SyncRoot)
        {
            var lastCursor = stream.NextCursor - 1;
            if (afterCursor > lastCursor)
            {
                return new CombatEventReadResult(
                    lastCursor, true, CombatEventResyncReasons.CursorTooOld, []);
            }

            var oldestCursor = stream.Events.Count == 0
                ? lastCursor + 1
                : stream.Events.Peek().Cursor;
            if (afterCursor < oldestCursor - 1)
            {
                return new CombatEventReadResult(
                    lastCursor, true, CombatEventResyncReasons.BufferOverflow, []);
            }

            var events = new List<CombatEventV2>(Math.Min(limit, stream.Events.Count));
            foreach (var stored in stream.Events)
            {
                if (stored.Cursor <= afterCursor)
                {
                    continue;
                }

                events.Add(stored);
                if (events.Count == limit)
                {
                    break;
                }
            }

            var nextCursor = events.Count > 0 ? events[^1].Cursor : lastCursor;
            return new CombatEventReadResult(nextCursor, false, null, events);
        }
    }

    // Reconnect cleanup: dropping the stream frees the budget and resets the
    // cursor for the next lifetime; stale clients then resync via
    // CURSOR_TOO_OLD instead of reading another lifetime's events.
    public bool RemoveSession(string sessionId) =>
        _streams.TryRemove(sessionId, out _);

    private static void ValidateEvent(CombatEventV2 input)
    {
        if (!P1Validation.IsHex32(input.EventId))
        {
            throw new InvalidOperationException(
                $"Combat event '{input.EventId}' must be a 32-char hex id.");
        }

        if (!CombatEventTypesV2.IsKnown(input.Type))
        {
            throw new InvalidOperationException(
                $"Combat event '{input.EventId}' has unknown type '{input.Type}'.");
        }

        if (!P1Validation.IsHex32(input.CastId))
        {
            throw new InvalidOperationException(
                $"Combat event '{input.EventId}' must carry a 32-char hex castId.");
        }

        if (!P1Validation.IsCharacterId(input.ActorId))
        {
            throw new InvalidOperationException(
                $"Combat event '{input.EventId}' has invalid actorId '{input.ActorId}'.");
        }

        if (!MapInstanceIdPattern.IsMatch(input.MapInstanceId))
        {
            throw new InvalidOperationException(
                $"Combat event '{input.EventId}' has invalid mapInstanceId '{input.MapInstanceId}'.");
        }

        if (string.IsNullOrWhiteSpace(input.FloorId))
        {
            throw new InvalidOperationException(
                $"Combat event '{input.EventId}' requires a floorId.");
        }

        if (input.Result is { } result &&
            (result.Amount < 0 || result.Absorbed < 0 || result.HpDamage < 0 ||
             result.Absorbed + result.HpDamage > result.Amount))
        {
            throw new InvalidOperationException(
                $"Combat event '{input.EventId}' has an inconsistent damage result.");
        }

        switch (input.Type)
        {
            case CombatEventTypesV2.Impact:
                if (input.TargetId is null || input.TargetLifeId is null ||
                    input.HitIndex is null || input.Result is not { Hit: true })
                {
                    throw new InvalidOperationException(
                        $"Combat event '{input.EventId}': IMPACT requires a target, " +
                        "lifeId, hitIndex and a hit result.");
                }

                break;
            case CombatEventTypesV2.Miss:
                if (input.TargetId is null || input.TargetLifeId is null ||
                    input.HitIndex is null || input.Result is not { Hit: false })
                {
                    throw new InvalidOperationException(
                        $"Combat event '{input.EventId}': MISS requires a target, " +
                        "lifeId, hitIndex and a miss result.");
                }

                break;
            case CombatEventTypesV2.Death:
                if (input.TargetId is null || input.TargetLifeId is null)
                {
                    throw new InvalidOperationException(
                        $"Combat event '{input.EventId}': DEATH requires a target and lifeId.");
                }

                break;
            case CombatEventTypesV2.CounterConfirmed:
                if (input.Result is not null)
                {
                    throw new InvalidOperationException(
                        $"Combat event '{input.EventId}': COUNTER_CONFIRMED is a guard " +
                        "confirmation, not counter damage.");
                }

                break;
        }
    }

    private sealed class SessionStream
    {
        public object SyncRoot { get; } = new();
        public Queue<CombatEventV2> Events { get; } = new();
        public Dictionary<string, CombatEventV2> ByEventId { get; } =
            new(StringComparer.Ordinal);
        public long NextCursor { get; set; } = 1;
    }
}
