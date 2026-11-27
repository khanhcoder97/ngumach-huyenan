namespace Server.Health.Gameplay.Combat;

public static class CombatTargetingTypes
{
    public const string Self = "SELF";
    public const string Dash = "DASH";
    public const string Cone = "CONE";
}

public sealed record SkillCoefficients(double Pve, double Boss, double Pvp)
{
    public double For(string mode) => mode switch
    {
        CombatSkillModes.Pve => Pve,
        CombatSkillModes.Boss => Boss,
        CombatSkillModes.Pvp => Pvp,
        _ => throw new ArgumentOutOfRangeException(nameof(mode), mode, "Unknown skill mode.")
    };
}

public static class CombatSkillModes
{
    public const string Pve = "PVE";
    public const string Boss = "BOSS";
    public const string Pvp = "PVP";
}

public sealed record CombatSkillDefinition(
    string SkillId,
    string ClassId,
    int CooldownSeconds,
    string Resource,
    int ResourceCost,
    string TargetingType,
    double? RangeWu,
    double? AngleDegrees,
    int MaxTargets,
    SkillCoefficients Coefficients,
    double TelegraphSeconds,
    string VfxKey);
