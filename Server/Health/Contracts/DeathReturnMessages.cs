using System.Text.Json.Serialization;

namespace Server.Health.Contracts;

// POST /p1/actor/death-return (DEC-DEATH-RETURN-20261105).
//
// Every request member is nullable so a malformed body answers with the exact
// field names that failed, the way the other P1 envelopes do; the schema decides
// what is legal.

public sealed class DeathReturnEnvelope
{
    public int? SchemaVersion { get; init; }
    public string? RequestId { get; init; }
    public string? IdempotencyKey { get; init; }
    public string? SentAtUtc { get; init; }
    public string? CharacterId { get; init; }
    public DeathReturnIntent? Payload { get; init; }
}

// The approved payload carries no members at all: the caller expresses only the
// intent to return, and an unknown member in the request is refused before this
// type is ever read (P1Json disallows unmapped members). Adding a map, a
// coordinate or an anchor record here would be the generic client teleport every
// source forbids, so there is deliberately nothing to add.
public sealed class DeathReturnIntent
{
}

public sealed class DeathReturnClearedV1
{
    public required int InflightCasts { get; init; }
    public required int ReservedCounters { get; init; }
    public required bool GuardWindowClosed { get; init; }
    public required bool MovementWindowReset { get; init; }
}

public sealed class DeathReturnPenaltiesV1
{
    // Echoed as zero because the approved design sets them to zero, not because
    // this is a knob: the schema pins each member at const 0.
    public int Xp { get; init; }
    public int Currency { get; init; }
    public int Durability { get; init; }
}

public sealed class DeathReturnResultV1
{
    public required bool Applied { get; init; }
    public required bool Replayed { get; init; }
    public required string MapId { get; init; }
    public required double XWu { get; init; }
    public required double YWu { get; init; }
    public required int Hp { get; init; }
    public required int MaxHp { get; init; }
    public required int Mp { get; init; }
    public required int MaxMp { get; init; }
    public required long ServerTick { get; init; }
    public required long Revision { get; init; }
    public required DeathReturnClearedV1 Cleared { get; init; }
    public required DeathReturnPenaltiesV1 Penalties { get; init; }

    // Required and nullable: an apply always carries the deadline it started, a
    // refusal of a second return inside the window carries the same number, and
    // only the pre-alpha fixture shape - which has no source for a cooldown at
    // all - answers null.
    public required long? NextReturnAllowedAtTick { get; init; }
}

public sealed class DeathReturnErrorV1
{
    public required string Code { get; init; }
    public required string MessageKey { get; init; }
    public required bool Retryable { get; init; }
    public required IReadOnlyList<string> FieldErrors { get; init; }
    public required string CorrelationId { get; init; }

    // Only death_return_cooldown carries it, so a client schedules its retry from
    // the server's tick instead of inferring how long a retryable refusal meant.
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public long? NextReturnAllowedAtTick { get; init; }
}

public sealed class P1DeathReturnResponse
{
    public int SchemaVersion { get; init; } = 1;
    public required string RequestId { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? SessionId { get; init; }

    public required string ServerTimeUtc { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public DeathReturnResultV1? Result { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public DeathReturnErrorV1? Error { get; init; }
}
