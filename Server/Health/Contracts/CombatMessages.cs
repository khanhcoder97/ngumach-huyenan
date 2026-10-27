using System.Text.Json.Serialization;

namespace Server.Health.Contracts;

public static class CombatEventTypes
{
    public const string Hit = "combat.hit";
    public const string Effect = "combat.effect";
    public const string Cooldown = "combat.cooldown";
    public const string Death = "combat.death";
}

public sealed class CombatEvent
{
    public required string EventId { get; init; }
    public required string EventType { get; init; }
    public required string AggregateId { get; init; }
    public required long AggregateRevision { get; init; }
    public required string EmittedAtUtc { get; init; }
    public int SchemaVersion { get; init; } = 1;
    public required CombatEventPayload Payload { get; init; }
}

public sealed class CombatEventPayload
{
    public required string SourceId { get; init; }
    public required string TargetId { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? SkillId { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public int? Damage { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public bool? Hit { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? TelegraphId { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? CooldownEndsAtUtc { get; init; }
}
