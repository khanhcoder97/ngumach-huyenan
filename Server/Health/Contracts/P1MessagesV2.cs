using System.Text.Json.Serialization;

namespace Server.Health.Contracts;

// QOD-16 phase 2 v2 wire DTOs (see Implementation/Contracts/P1/*V2.schema.json).
// v1 messages stay unchanged; these types are only reachable behind the
// P1:CombatV2 gate.

public sealed class CombatV2Envelope
{
    public int? SchemaVersion { get; init; }
    public string? RequestId { get; init; }
    public string? IdempotencyKey { get; init; }
    public string? SentAtUtc { get; init; }
    public string? CharacterId { get; init; }
    public CombatV2IntentPayload? Payload { get; init; }
}

public sealed class CombatV2IntentPayload
{
    public string? ActionKind { get; init; }
    public string? SkillId { get; init; }
    public string? TargetId { get; init; }
    public int? InputSequence { get; init; }
    public double? AimX { get; init; }
    public double? AimY { get; init; }
    public string? ClientTimeUtc { get; init; }
}

public sealed class P1CombatV2Response
{
    public int SchemaVersion { get; init; } = 2;
    public required string RequestId { get; init; }
    public required string SessionId { get; init; }
    public required string ServerTimeUtc { get; init; }
    public required long Revision { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public CombatV2ResultDto? Result { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public P1Error? Error { get; init; }
}

public sealed class CombatV2ResultDto
{
    public required string CastId { get; init; }
    public required string ActionKind { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? SkillId { get; init; }

    public required int Mp { get; init; }
    public required int MpCost { get; init; }
    public required string CooldownEndUtc { get; init; }
    public required int NextInputSequence { get; init; }
    public required IReadOnlyList<CombatEventV2Dto> Events { get; init; }
}

public sealed class CombatEventV2Dto
{
    public required string EventId { get; init; }
    public required long Cursor { get; init; }
    public required string Type { get; init; }
    public required string CastId { get; init; }
    public required string ActorId { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? TargetId { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public long? TargetLifeId { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public int? HitIndex { get; init; }

    public required string MapInstanceId { get; init; }
    public required string FloorId { get; init; }
    public required long SourceRevision { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public long? TargetRevision { get; init; }

    public required long ServerTick { get; init; }
    public required string EmittedAtUtc { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public CombatEventResultV2Dto? Result { get; init; }
}

public sealed class CombatEventResultV2Dto
{
    public required bool Hit { get; init; }
    public required bool Crit { get; init; }
    public required bool Immune { get; init; }
    public required int Amount { get; init; }
    public required int Absorbed { get; init; }
    public required int HpDamage { get; init; }
}

public sealed class P1WorldV2Response
{
    public int SchemaVersion { get; init; } = 2;
    public required string RequestId { get; init; }
    public required string SessionId { get; init; }
    public required string ServerTimeUtc { get; init; }
    public required long Revision { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public WorldSnapshotV2? Result { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public P1Error? Error { get; init; }
}

public sealed class WorldSnapshotV2
{
    public int SchemaVersion { get; init; } = 2;
    public required string MapId { get; init; }
    public required string MapInstanceId { get; init; }
    public required string FloorId { get; init; }
    public required string Phase { get; init; }
    public required long ServerTick { get; init; }
    public required long Revision { get; init; }
    public required string ServerTimeUtc { get; init; }
    public required WorldAudienceV2 Audience { get; init; }
    public required WorldSnapshotV2Self Self { get; init; }
    public required IReadOnlyList<WorldEntityV2> Entities { get; init; }
}

public sealed class WorldAudienceV2
{
    public double AoiEnterWu { get; init; } = 40;
    public double AoiLeaveWu { get; init; } = 48;
}

public sealed class WorldSnapshotV2Self
{
    public required string CharacterId { get; init; }
    public required string ClassId { get; init; }
    public required double X { get; init; }
    public required double Y { get; init; }
    public required int Hp { get; init; }
    public required int MaxHp { get; init; }
    public required int Mp { get; init; }
    public required int MaxMp { get; init; }
    public required int SwordIntent { get; init; }
}

public sealed class WorldEntityV2
{
    public required string EntityId { get; init; }
    public required string Kind { get; init; }
    public required string MapInstanceId { get; init; }
    public required string FloorId { get; init; }
    public required string Phase { get; init; }
    public required double X { get; init; }
    public required double Y { get; init; }
    public required string State { get; init; }
    public required string HealthState { get; init; }
    public required bool Targetable { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? Availability { get; init; }

    public required int Hp { get; init; }
    public required int MaxHp { get; init; }
    public required long Revision { get; init; }
    public required long LifeId { get; init; }
}

public sealed class P1CombatEventPageV2Response
{
    public int SchemaVersion { get; init; } = 2;
    public required string RequestId { get; init; }
    public required string SessionId { get; init; }
    public required string ServerTimeUtc { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public CombatEventPageV2Dto? Result { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public P1Error? Error { get; init; }
}

public sealed class CombatEventPageV2Dto
{
    public int SchemaVersion { get; init; } = 2;
    public required string SessionId { get; init; }
    public required long NextCursor { get; init; }
    public required bool ResyncRequired { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? ResyncReason { get; init; }

    public required IReadOnlyList<CombatEventV2Dto> Events { get; init; }
}
