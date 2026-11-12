using Server.Health.Contracts;

namespace Server.Health.Gameplay.Combat;

public sealed class CombatCommand
{
    public int? InputSequence { get; init; }
    public string? SkillId { get; init; }
    public string? TargetId { get; init; }
    public double? AimX { get; init; }
    public double? AimY { get; init; }
    public string? ClientTimeUtc { get; init; }
}

public sealed record CombatFailure(string Code, bool Retryable, IReadOnlyList<string> FieldErrors);

public sealed record CombatOutcome(CombatEvent? Event, CombatFailure? Failure)
{
    public bool Accepted => Failure is null;

    public static CombatOutcome Success(CombatEvent combatEvent) => new(combatEvent, null);

    public static CombatOutcome Rejected(string code, bool retryable, params string[] fieldErrors) =>
        new(null, new CombatFailure(code, retryable, fieldErrors));
}

public static class CombatErrorCodes
{
    public const string UnknownSkill = "unknown_skill";
    public const string SkillNotAvailable = "skill_not_available";
    public const string InvalidTarget = "invalid_target";
    public const string TargetNotFound = "target_not_found";
    public const string TargetNotAlive = "target_not_alive";
    public const string ActorNotAlive = "actor_not_alive";
    public const string OutOfRange = "out_of_range";
    public const string CooldownActive = "cooldown_active";
    public const string InsufficientResource = "insufficient_resource";
    public const string UnsupportedResource = "unsupported_resource";
    public const string IdempotencyConflict = "idempotency_conflict";
}
