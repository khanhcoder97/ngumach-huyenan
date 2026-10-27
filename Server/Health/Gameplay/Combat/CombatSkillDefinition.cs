namespace Server.Health.Gameplay.Combat;

public static class CombatTargetingTypes
{
    public const string Self = "SELF";
    public const string Dash = "DASH";
    public const string Cone = "CONE";
}

public sealed record CombatSkillDefinition(
    string SkillId,
    string ClassId,
    int CooldownSeconds,
    string Resource,
    int ResourceCost,
    string TargetingType,
    double? RangeWu,
    int MaxTargets);
