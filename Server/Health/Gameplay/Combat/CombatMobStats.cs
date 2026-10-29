using System.Text.Json;
using Server.Health.Contracts;

namespace Server.Health.Gameplay.Combat;

// Runtime projection of Implementation/Content/Runtime/combat_mob_stats_v1.json,
// built deterministically by Implementation/Tools/build_combat_mob_stats.py
// from Art Bible §12 + Production_Rules §4. The bundle is
// DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION and is only read when
// P1:CombatDamage:Enabled=true (OFF by default). REFERENCE_L5 values are the
// owner-locked level-5 table from P1_Design_Resolution_20261029_vi.md, not
// final balance.
public sealed record MobStatBundle(
    int SchemaVersion,
    string BundleId,
    string Activation,
    int ReferenceLevel,
    string LevelPolicy,
    double MetersPerWu,
    MobBaseFormulas BaseFormulas,
    EliteMultipliers Elite,
    IReadOnlyList<MobArchetypeStats> Archetypes,
    IReadOnlyList<MobBossStats> Bosses);

public sealed record MobBaseFormulas(
    MobLevelFormula Hp,
    MobLevelFormula Attack,
    MobLevelFormula Defense);

public sealed record MobLevelFormula(double Base, double PerLevel)
{
    public double At(int level) => Base + (PerLevel * level);
}

public sealed record EliteMultipliers(double Hp, double Attack, double Defense);

public sealed record MobArchetypeStats(
    string MobId,
    MobMultipliers Multipliers,
    double MoveSpeedMetersPerSecond,
    double AggroRadiusMeters,
    IReadOnlyList<MobAttackMove> Attacks,
    MobEffectiveStats ReferenceLevel5);

public sealed record MobMultipliers(double Hp, double Attack, double Defense);

public sealed record MobEffectiveStats(int Hp, double Attack, double Defense);

public sealed record MobAttackMove(
    string AttackId,
    string NameVi,
    double AttackMultiplier,
    double? RangeMeters,
    double? LineMeters,
    double TelegraphSeconds);

public sealed record MobBossStats(
    string BossId,
    double HpMultiplier,
    double AttackMultiplier,
    double PartyHpMultiplierPerAdditionalPlayer,
    int ReferenceLevel,
    MobEffectiveStats ReferenceStats,
    IReadOnlyList<MobBossAttack> Attacks,
    string Activation,
    string BlockedReason);

public sealed record MobBossAttack(
    string AttackId,
    string Shape,
    double? AngleDegrees,
    double? RangeWu,
    double? RadiusWu,
    double? InnerRadiusWu,
    double? OuterRadiusWu,
    bool AtLockedTarget,
    double TelegraphSeconds,
    double AttackMultiplier,
    double RecoverySeconds,
    double CooldownSeconds);

public static class CombatMobStatLoader
{
    public const string DesignOnlyActivation = "DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION";
    private const string RelativePath =
        "Implementation/Content/Runtime/combat_mob_stats_v1.json";
    private const int MaxSearchDepth = 12;

    private static readonly System.Text.RegularExpressions.Regex TemplateIdPattern =
        new(@"^[A-Z][A-Z0-9_]+$",
            System.Text.RegularExpressions.RegexOptions.CultureInvariant);

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public static string DiscoverPath(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:CombatMobStatsPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:CombatMobStatsPath points to '{resolved}', which does not exist.");
            }

            return resolved;
        }

        var starts = new[] { contentRoot, Directory.GetCurrentDirectory(), AppContext.BaseDirectory }
            .Where(path => !string.IsNullOrWhiteSpace(path))
            .Distinct(StringComparer.OrdinalIgnoreCase);

        foreach (var start in starts)
        {
            DirectoryInfo? directory = new(Path.GetFullPath(start));
            for (var depth = 0; depth < MaxSearchDepth && directory is not null; depth++)
            {
                var candidate = Path.Combine(directory.FullName, RelativePath);
                if (File.Exists(candidate))
                {
                    return candidate;
                }

                directory = directory.Parent;
            }
        }

        throw new FileNotFoundException(
            $"Could not locate {RelativePath}. Set Content:CombatMobStatsPath or run from the repository.");
    }

    public static MobStatBundle Load(string path)
    {
        MobStatsFile? file;
        try
        {
            using var stream = File.OpenRead(path);
            file = JsonSerializer.Deserialize<MobStatsFile>(stream, JsonOptions);
        }
        catch (JsonException exception)
        {
            throw new InvalidOperationException(
                $"{path}: invalid JSON ({exception.Message})", exception);
        }

        if (file is null)
        {
            throw new InvalidOperationException($"{path}: file is empty.");
        }

        if (file.SchemaVersion != 1)
        {
            throw new InvalidOperationException(
                $"{path}: unsupported schemaVersion '{file.SchemaVersion}'.");
        }

        if (!string.Equals(file.Activation, DesignOnlyActivation, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: activation must be '{DesignOnlyActivation}'.");
        }

        if (file.ReferenceLevel is not { } referenceLevel || referenceLevel < 1)
        {
            throw new InvalidOperationException($"{path}: referenceLevel must be at least 1.");
        }

        var formulas = LoadFormulas(path, file.BaseFormulas);
        var elite = LoadElite(path, file.Elite);

        var archetypes = new List<MobArchetypeStats>();
        var archetypeIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var source in file.Archetypes ?? [])
        {
            if (source.MobId is null ||
                !TemplateIdPattern.IsMatch(source.MobId))
            {
                throw new InvalidOperationException(
                    $"{path}: invalid archetype mobId '{source.MobId}'.");
            }

            if (!archetypeIds.Add(source.MobId))
            {
                throw new InvalidOperationException(
                    $"{path}: duplicate archetype mobId '{source.MobId}'.");
            }

            var multipliers = LoadMultipliers(path, source.MobId, source.Multipliers);
            if (!IsFinitePositive(source.MoveSpeedMetersPerSecond))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.MobId} moveSpeedMetersPerSecond must be positive.");
            }

            if (!IsFinitePositive(source.AggroRadiusMeters))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.MobId} aggroRadiusMeters must be positive.");
            }

            var attacks = LoadMobAttacks(path, source.MobId, source.Attacks);
            var l5 = LoadEffective(path, $"{source.MobId} referenceLevel5", source.ReferenceLevel5);
            archetypes.Add(new MobArchetypeStats(
                source.MobId,
                multipliers,
                source.MoveSpeedMetersPerSecond!.Value,
                source.AggroRadiusMeters!.Value,
                attacks,
                l5));
        }

        if (archetypes.Count == 0)
        {
            throw new InvalidOperationException($"{path}: archetypes must not be empty.");
        }

        var bosses = new List<MobBossStats>();
        var bossIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var source in file.Bosses ?? [])
        {
            if (source.BossId is null ||
                !TemplateIdPattern.IsMatch(source.BossId))
            {
                throw new InvalidOperationException(
                    $"{path}: invalid boss bossId '{source.BossId}'.");
            }

            if (!bossIds.Add(source.BossId))
            {
                throw new InvalidOperationException(
                    $"{path}: duplicate boss bossId '{source.BossId}'.");
            }

            if (!IsFinitePositive(source.HpMultiplier) ||
                !IsFinitePositive(source.AttackMultiplier))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.BossId} hp/attack multipliers must be positive.");
            }

            if (source.ReferenceLevel is not { } bossLevel || bossLevel < 1)
            {
                throw new InvalidOperationException(
                    $"{path}: {source.BossId} referenceLevel must be at least 1.");
            }

            var bossAttacks = new List<MobBossAttack>();
            var attackIds = new HashSet<string>(StringComparer.Ordinal);
            foreach (var attack in source.Attacks ?? [])
            {
                if (string.IsNullOrWhiteSpace(attack.AttackId) ||
                    !attackIds.Add(attack.AttackId))
                {
                    throw new InvalidOperationException(
                        $"{path}: {source.BossId} has invalid or duplicate attackId.");
                }

                if (string.IsNullOrWhiteSpace(attack.Shape) ||
                    !IsFinitePositive(attack.TelegraphSeconds) ||
                    !IsFinitePositive(attack.AttackMultiplier) ||
                    !IsFinitePositive(attack.RecoverySeconds) ||
                    !IsFinitePositive(attack.CooldownSeconds))
                {
                    throw new InvalidOperationException(
                        $"{path}: {source.BossId} attack {attack.AttackId} fields must be positive.");
                }

                bossAttacks.Add(new MobBossAttack(
                    attack.AttackId!,
                    attack.Shape,
                    attack.AngleDegrees,
                    attack.RangeWu,
                    attack.RadiusWu,
                    attack.InnerRadiusWu,
                    attack.OuterRadiusWu,
                    attack.AtLockedTarget,
                    attack.TelegraphSeconds!.Value,
                    attack.AttackMultiplier!.Value,
                    attack.RecoverySeconds!.Value,
                    attack.CooldownSeconds!.Value));
            }

            if (bossAttacks.Count == 0)
            {
                throw new InvalidOperationException(
                    $"{path}: {source.BossId} attacks must not be empty.");
            }

            if (!string.Equals(
                    source.Activation, "BOSSDATA_BLOCKED", StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.BossId} activation must be BOSSDATA_BLOCKED " +
                    "until phaseGuard/interruptible data exists.");
            }

            if (string.IsNullOrWhiteSpace(source.BlockedReason))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.BossId} blockedReason is required.");
            }

            var bossStats = LoadEffective(
                path, $"{source.BossId} referenceStats", source.ReferenceStats);
            bosses.Add(new MobBossStats(
                source.BossId,
                source.HpMultiplier!.Value,
                source.AttackMultiplier!.Value,
                source.PartyHpMultiplierPerAdditionalPlayer ?? 0,
                bossLevel,
                bossStats,
                bossAttacks,
                source.Activation!,
                source.BlockedReason));
        }

        return new MobStatBundle(
            1,
            file.BundleId ?? string.Empty,
            file.Activation!,
            referenceLevel,
            file.LevelPolicy ?? string.Empty,
            file.Units?.MetersPerWu ?? 0.5,
            formulas,
            elite,
            archetypes,
            bosses);
    }

    public static MobEffectiveStats EffectiveAt(MobStatBundle bundle, string mobId, int level)
    {
        var archetype = bundle.Archetypes.FirstOrDefault(
            stats => string.Equals(stats.MobId, mobId, StringComparison.Ordinal))
            ?? throw new InvalidOperationException(
                $"Combat mob stats: unknown archetype '{mobId}'.");

        if (level < 1)
        {
            throw new InvalidOperationException(
                $"Combat mob stats: level must be at least 1, got {level}.");
        }

        return new MobEffectiveStats(
            checked((int)Math.Round(
                bundle.BaseFormulas.Hp.At(level) * archetype.Multipliers.Hp)),
            bundle.BaseFormulas.Attack.At(level) * archetype.Multipliers.Attack,
            bundle.BaseFormulas.Defense.At(level) * archetype.Multipliers.Defense);
    }

    private static MobBaseFormulas LoadFormulas(
        string path, BaseFormulasFile? source)
    {
        if (source is null ||
            !IsFiniteNonNegative(source.Hp?.Base) ||
            !IsFiniteNonNegative(source.Hp?.PerLevel) ||
            !IsFiniteNonNegative(source.Attack?.Base) ||
            !IsFiniteNonNegative(source.Attack?.PerLevel) ||
            !IsFiniteNonNegative(source.Defense?.Base) ||
            !IsFiniteNonNegative(source.Defense?.PerLevel))
        {
            throw new InvalidOperationException(
                $"{path}: baseFormulas hp/attack/defense base and perLevel must be finite non-negative.");
        }

        return new MobBaseFormulas(
            new MobLevelFormula(source.Hp!.Base!.Value, source.Hp.PerLevel!.Value),
            new MobLevelFormula(source.Attack!.Base!.Value, source.Attack.PerLevel!.Value),
            new MobLevelFormula(source.Defense!.Base!.Value, source.Defense.PerLevel!.Value));
    }

    private static EliteMultipliers LoadElite(string path, EliteFile? source)
    {
        if (source is null ||
            !IsFinitePositive(source.HpMultiplier) ||
            !IsFinitePositive(source.AttackMultiplier) ||
            !IsFinitePositive(source.DefenseMultiplier))
        {
            throw new InvalidOperationException(
                $"{path}: elite hp/attack/defense multipliers must be positive.");
        }

        return new EliteMultipliers(
            source.HpMultiplier!.Value,
            source.AttackMultiplier!.Value,
            source.DefenseMultiplier!.Value);
    }

    private static MobMultipliers LoadMultipliers(
        string path, string mobId, MultipliersFile? source)
    {
        if (source is null ||
            !IsFinitePositive(source.Hp) ||
            !IsFinitePositive(source.Attack) ||
            !IsFinitePositive(source.Defense))
        {
            throw new InvalidOperationException(
                $"{path}: {mobId} multipliers hp/attack/defense must be positive.");
        }

        return new MobMultipliers(
            source.Hp!.Value, source.Attack!.Value, source.Defense!.Value);
    }

    private static IReadOnlyList<MobAttackMove> LoadMobAttacks(
        string path, string mobId, List<MobAttackFile>? sources)
    {
        var attacks = new List<MobAttackMove>();
        var attackIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var attack in sources ?? [])
        {
            if (string.IsNullOrWhiteSpace(attack.AttackId) ||
                !attackIds.Add(attack.AttackId))
            {
                throw new InvalidOperationException(
                    $"{path}: {mobId} has invalid or duplicate attackId.");
            }

            if (string.IsNullOrWhiteSpace(attack.NameVi) ||
                !IsFinitePositive(attack.AttackMultiplier) ||
                !IsFiniteNonNegative(attack.TelegraphSeconds))
            {
                throw new InvalidOperationException(
                    $"{path}: {mobId} attack {attack.AttackId} fields are invalid.");
            }

            if (attack.RangeMeters is { } rangeMeters && !IsFiniteNonNegative(rangeMeters))
            {
                throw new InvalidOperationException(
                    $"{path}: {mobId} attack {attack.AttackId} rangeMeters is invalid.");
            }

            if (attack.LineMeters is { } lineMeters && !IsFiniteNonNegative(lineMeters))
            {
                throw new InvalidOperationException(
                    $"{path}: {mobId} attack {attack.AttackId} lineMeters is invalid.");
            }

            attacks.Add(new MobAttackMove(
                attack.AttackId!,
                attack.NameVi!,
                attack.AttackMultiplier!.Value,
                attack.RangeMeters,
                attack.LineMeters,
                attack.TelegraphSeconds!.Value));
        }

        if (attacks.Count == 0)
        {
            throw new InvalidOperationException(
                $"{path}: {mobId} attacks must not be empty.");
        }

        return attacks;
    }

    private static MobEffectiveStats LoadEffective(
        string path, string label, EffectiveStatsFile? source)
    {
        if (source is null ||
            source.Hp is not { } hp || hp < 1 ||
            !IsFiniteNonNegative(source.Attack) ||
            !IsFiniteNonNegative(source.Defense))
        {
            throw new InvalidOperationException(
                $"{path}: {label} must have positive hp and finite attack/defense.");
        }

        return new MobEffectiveStats(hp, source.Attack!.Value, source.Defense!.Value);
    }

    private static bool IsFinitePositive(double? value) =>
        value is { } v && double.IsFinite(v) && v > 0;

    private static bool IsFiniteNonNegative(double? value) =>
        value is { } v && double.IsFinite(v) && v >= 0;

    private sealed class MobStatsFile
    {
        public int SchemaVersion { get; init; }
        public string? BundleId { get; init; }
        public string? Activation { get; init; }
        public int? ReferenceLevel { get; init; }
        public string? LevelPolicy { get; init; }
        public UnitsFile? Units { get; init; }
        public BaseFormulasFile? BaseFormulas { get; init; }
        public EliteFile? Elite { get; init; }
        public List<ArchetypeFile>? Archetypes { get; init; }
        public List<BossFile>? Bosses { get; init; }
    }

    private sealed class UnitsFile
    {
        public double MetersPerWu { get; init; }
    }

    private sealed class BaseFormulasFile
    {
        public FormulaFile? Hp { get; init; }
        public FormulaFile? Attack { get; init; }
        public FormulaFile? Defense { get; init; }
    }

    private sealed class FormulaFile
    {
        public double? Base { get; init; }
        public double? PerLevel { get; init; }
    }

    private sealed class EliteFile
    {
        public double? HpMultiplier { get; init; }
        public double? AttackMultiplier { get; init; }
        public double? DefenseMultiplier { get; init; }
    }

    private sealed class ArchetypeFile
    {
        public string? MobId { get; init; }
        public MultipliersFile? Multipliers { get; init; }
        public double? MoveSpeedMetersPerSecond { get; init; }
        public double? AggroRadiusMeters { get; init; }
        public List<MobAttackFile>? Attacks { get; init; }
        public EffectiveStatsFile? ReferenceLevel5 { get; init; }
    }

    private sealed class MultipliersFile
    {
        public double? Hp { get; init; }
        public double? Attack { get; init; }
        public double? Defense { get; init; }
    }

    private sealed class MobAttackFile
    {
        public string? AttackId { get; init; }
        public string? NameVi { get; init; }
        public double? AttackMultiplier { get; init; }
        public double? RangeMeters { get; init; }
        public double? LineMeters { get; init; }
        public double? TelegraphSeconds { get; init; }
    }

    private sealed class EffectiveStatsFile
    {
        public int? Hp { get; init; }
        public double? Attack { get; init; }
        public double? Defense { get; init; }
    }

    private sealed class BossFile
    {
        public string? BossId { get; init; }
        public double? HpMultiplier { get; init; }
        public double? AttackMultiplier { get; init; }
        public double? PartyHpMultiplierPerAdditionalPlayer { get; init; }
        public int? ReferenceLevel { get; init; }
        public EffectiveStatsFile? ReferenceStats { get; init; }
        public List<BossAttackFile>? Attacks { get; init; }
        public string? Activation { get; init; }
        public string? BlockedReason { get; init; }
    }

    private sealed class BossAttackFile
    {
        public string? AttackId { get; init; }
        public string? Shape { get; init; }
        public double? AngleDegrees { get; init; }
        public double? RangeWu { get; init; }
        public double? RadiusWu { get; init; }
        public double? InnerRadiusWu { get; init; }
        public double? OuterRadiusWu { get; init; }
        public bool AtLockedTarget { get; init; }
        public double? TelegraphSeconds { get; init; }
        public double? AttackMultiplier { get; init; }
        public double? RecoverySeconds { get; init; }
        public double? CooldownSeconds { get; init; }
    }
}
