using System.Text.Json.Serialization;

namespace Server.Health.Contracts;

public sealed class SessionCreateRequest
{
    public string? CharacterId { get; init; }
    public string? ClassId { get; init; }
}

public sealed class MoveEnvelope
{
    public int? SchemaVersion { get; init; }
    public string? RequestId { get; init; }
    public string? IdempotencyKey { get; init; }
    public string? SentAtUtc { get; init; }
    public string? CharacterId { get; init; }
    public MoveIntent? Payload { get; init; }
}

public sealed class MoveIntent
{
    public int? InputSequence { get; init; }
    public double? MoveX { get; init; }
    public double? MoveY { get; init; }
    public string? ClientTimeUtc { get; init; }
}

public sealed class CombatEnvelope
{
    public int? SchemaVersion { get; init; }
    public string? RequestId { get; init; }
    public string? IdempotencyKey { get; init; }
    public string? SentAtUtc { get; init; }
    public string? CharacterId { get; init; }
    public CombatIntent? Payload { get; init; }
}

public sealed class CombatIntent
{
    public int? InputSequence { get; init; }
    public string? SkillId { get; init; }
    public string? TargetId { get; init; }
    public double? AimX { get; init; }
    public double? AimY { get; init; }
    public string? ClientTimeUtc { get; init; }
}

public sealed class WorldSnapshot
{
    public required string MapId { get; init; }
    public required long ServerTick { get; init; }
    public required long Revision { get; init; }
    public required string ServerTimeUtc { get; init; }
    public required WorldSelf Self { get; init; }
    public required IReadOnlyList<WorldEntity> Entities { get; init; }
}

public sealed class WorldSelf
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

public sealed class WorldEntity
{
    public required string EntityId { get; init; }
    public required string Kind { get; init; }
    public required double X { get; init; }
    public required double Y { get; init; }
    public required int Hp { get; init; }
    public required int MaxHp { get; init; }
    public required string State { get; init; }
    public string? TelegraphId { get; init; }
}

public sealed class P1Response
{
    public int SchemaVersion { get; init; } = 1;
    public required string RequestId { get; init; }
    public required string ServerTimeUtc { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? SessionId { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public long? Revision { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public WorldSnapshot? Result { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public P1Error? Error { get; init; }
}

public sealed class P1Error
{
    public required string Code { get; init; }
    public required string MessageKey { get; init; }
    public required bool Retryable { get; init; }
    public required IReadOnlyList<string> FieldErrors { get; init; }
    public required string CorrelationId { get; init; }
}

public sealed class P1CombatResponse
{
    public int SchemaVersion { get; init; } = 1;
    public required string RequestId { get; init; }
    public required string SessionId { get; init; }
    public required string ServerTimeUtc { get; init; }
    public required long Revision { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public CombatEvent? Result { get; init; }
}

public sealed class P1QuestListResponse
{
    public int SchemaVersion { get; init; } = 1;
    public required string RequestId { get; init; }
    public required string SessionId { get; init; }
    public required string ServerTimeUtc { get; init; }
    public required IReadOnlyList<QuestState> Result { get; init; }
}

public sealed class P1InventoryResponse
{
    public int SchemaVersion { get; init; } = 1;
    public required string RequestId { get; init; }
    public required string SessionId { get; init; }
    public required string ServerTimeUtc { get; init; }
    public required InventorySnapshot Result { get; init; }
}
