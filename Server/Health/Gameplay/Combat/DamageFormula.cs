using System.Globalization;
using System.Security.Cryptography;
using System.Text;

namespace Server.Health.Gameplay.Combat;

// Production_Rules_Complete_v1_vi.md §2 order of operations. Buckets are
// multiplied in the documented order; only the final damage floors once.
// The 27/40 oracle from P1_Design_Resolution_20261029_vi.md §2 must hold:
// attack20, flat0, coefficient1.5, rank1, bonus0, armor10, resist0, no crit
// -> floor(30 * 100/110) = 27; crit -> floor(27.27... * 1.5) = 40.
public static class DamageFormula
{
    public const double CritMultiplier = 1.5;
    public const double HitFloor = 0.05;
    public const double HitCeiling = 0.98;
    public const double BaseHitChance = 0.90;
    public const double PveResistCap = 0.5;
    public const double PvpResistCap = 0.3;
    public const double DamageReductionCap = 0.8;

    public static double RawDamage(
        double attack, double flatSkill, double coefficient,
        double rankMultiplier, double damageBonus) =>
        (attack + flatSkill) * coefficient * rankMultiplier * (1 + damageBonus);

    public static double MitigationMultiplier(double armor) =>
        100.0 / (100.0 + Math.Max(0, armor));

    public static double ElementMultiplier(double resist, bool pvp) =>
        1.0 - Math.Clamp(resist, 0, pvp ? PvpResistCap : PveResistCap);

    public static double DamageReductionMultiplier(double reduction) =>
        1.0 - Math.Clamp(reduction, 0, DamageReductionCap);

    public static long FinalDamage(
        double raw, double mitigation, double element,
        double critMultiplier, double reduction) =>
        Math.Max(1, (long)Math.Floor(
            raw * mitigation * element * critMultiplier * reduction));

    public static double HitProbability(double accuracy, double dodge) =>
        Math.Clamp(BaseHitChance + accuracy - dodge, HitFloor, HitCeiling);

    // Crit stat itself is capped when derived from attributes (Rules §1);
    // the roll clamps crit - critResist into [0, cap] (Rules §2 step 3).
    public static double CritProbability(double crit, double critResist, double cap) =>
        Math.Clamp(Math.Clamp(crit, 0, cap) - critResist, 0, cap);

    public static double AttributeCritChance(double luk, double gearCrit, double cap) =>
        Math.Clamp(0.05 + (0.0005 * luk) + gearCrit, 0, cap);

    public static double AttributeAccuracy(double agi, double gearAccuracy) =>
        (0.0005 * agi) + gearAccuracy;

    public static double AttributeDodge(double agi, double gearDodge, double cap) =>
        Math.Min(cap, (0.0003 * agi) + gearDodge);
}

// Server RNG is seeded per (seedVersion, castId, targetId, hitIndex) so a
// given cast is reproducible for audit (Rules §2 step 3). Uniform [0,1).
public static class CombatRng
{
    public const string SeedVersion = "combat-rng-v1";

    public static double Uniform01(string castId, string targetId, int hitIndex)
    {
        var seed = string.Join(
            '|',
            SeedVersion,
            castId,
            targetId,
            hitIndex.ToString(CultureInfo.InvariantCulture));
        var digest = SHA256.HashData(Encoding.UTF8.GetBytes(seed));
        var value = BitConverter.ToUInt64(digest, 0);
        return value / (ulong.MaxValue + 1.0);
    }

    public static bool Roll(string castId, string targetId, int hitIndex, double probability) =>
        Uniform01(castId, targetId, hitIndex) < probability;
}
