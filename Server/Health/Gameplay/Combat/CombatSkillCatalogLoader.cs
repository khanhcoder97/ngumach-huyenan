using System.Text.Json;
using System.Text.RegularExpressions;
using Server.Health.Contracts;

namespace Server.Health.Gameplay.Combat;

public static class CombatSkillCatalogLoader
{
    private const string RelativeDirectory = "Implementation/Content/Examples/SkillDefinition";
    private const int MaxSearchDepth = 12;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly Regex ClassIdPattern =
        new(@"^CLASS_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex TargetingTypePattern =
        new(@"^[A-Z_]+$", RegexOptions.CultureInvariant);

    public static string DiscoverDirectory(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:SkillsPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!Directory.Exists(resolved))
            {
                throw new DirectoryNotFoundException(
                    $"Content:SkillsPath points to '{resolved}', which does not exist.");
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
                var candidate = Path.Combine(directory.FullName, RelativeDirectory);
                if (Directory.Exists(candidate))
                {
                    return candidate;
                }

                directory = directory.Parent;
            }
        }

        throw new DirectoryNotFoundException(
            $"Could not locate {RelativeDirectory}. Set Content:SkillsPath or run from the repository.");
    }

    public static CombatSkillCatalog Load(string directory)
    {
        var files = Directory
            .EnumerateFiles(directory, "*.json", SearchOption.TopDirectoryOnly)
            .OrderBy(path => path, StringComparer.Ordinal)
            .ToList();

        if (files.Count == 0)
        {
            throw new InvalidOperationException($"{directory}: no SkillDefinition JSON files found.");
        }

        var skills = new Dictionary<string, CombatSkillDefinition>(StringComparer.Ordinal);
        foreach (var path in files)
        {
            SkillFile? file;
            try
            {
                using var stream = File.OpenRead(path);
                file = JsonSerializer.Deserialize<SkillFile>(stream, JsonOptions);
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

            if (!P1Validation.IsSkillId(file.SkillId))
            {
                throw new InvalidOperationException($"{path}: invalid skillId '{file.SkillId}'.");
            }

            if (file.ClassId is null || !ClassIdPattern.IsMatch(file.ClassId))
            {
                throw new InvalidOperationException($"{path}: invalid classId '{file.ClassId}'.");
            }

            if (file.CooldownSeconds is null || file.CooldownSeconds < 1)
            {
                throw new InvalidOperationException($"{path}: cooldownSeconds must be at least 1.");
            }

            var resourceCost = file.ResourceCost;
            if (resourceCost?.Resource is null ||
                string.IsNullOrWhiteSpace(resourceCost.Resource) ||
                resourceCost.Amount is null ||
                resourceCost.Amount < 0)
            {
                throw new InvalidOperationException(
                    $"{path}: resourceCost.resource and a non-negative resourceCost.amount are required.");
            }

            var targeting = file.Targeting;
            if (targeting?.Type is null || !TargetingTypePattern.IsMatch(targeting.Type))
            {
                throw new InvalidOperationException($"{path}: invalid targeting.type.");
            }

            if (targeting.MaxTargets is null || targeting.MaxTargets < 1)
            {
                throw new InvalidOperationException($"{path}: targeting.maxTargets must be at least 1.");
            }

            if (targeting.RangeWu is { } range && (!double.IsFinite(range) || range < 0))
            {
                throw new InvalidOperationException(
                    $"{path}: targeting.rangeWu must be a non-negative finite number.");
            }

            if (targeting.AngleDegrees is { } angle &&
                (!double.IsFinite(angle) || angle < 0 || angle > 360))
            {
                throw new InvalidOperationException(
                    $"{path}: targeting.angleDegrees must be between 0 and 360.");
            }

            var coefficients = file.Coefficients;
            if (coefficients is null ||
                !IsFiniteNonNegative(coefficients.Pve) ||
                !IsFiniteNonNegative(coefficients.Boss) ||
                !IsFiniteNonNegative(coefficients.Pvp))
            {
                throw new InvalidOperationException(
                    $"{path}: coefficients.pve/boss/pvp must be finite non-negative numbers.");
            }

            if (coefficients.Pvp is { } pvp && pvp > 1)
            {
                throw new InvalidOperationException(
                    $"{path}: coefficients.pvp must not exceed 1.");
            }

            if (file.TelegraphSeconds is not { } telegraph ||
                !double.IsFinite(telegraph) || telegraph < 0)
            {
                throw new InvalidOperationException(
                    $"{path}: telegraphSeconds must be a non-negative finite number.");
            }

            if (string.IsNullOrWhiteSpace(file.VfxKey))
            {
                throw new InvalidOperationException($"{path}: vfxKey is required.");
            }

            var skill = new CombatSkillDefinition(
                file.SkillId!,
                file.ClassId,
                file.CooldownSeconds.Value,
                resourceCost.Resource,
                resourceCost.Amount.Value,
                targeting.Type,
                targeting.RangeWu,
                targeting.AngleDegrees,
                targeting.MaxTargets.Value,
                new SkillCoefficients(
                    coefficients.Pve!.Value,
                    coefficients.Boss!.Value,
                    coefficients.Pvp!.Value),
                telegraph,
                file.VfxKey);

            if (!skills.TryAdd(skill.SkillId, skill))
            {
                throw new InvalidOperationException($"{path}: duplicate skillId '{skill.SkillId}'.");
            }
        }

        return new CombatSkillCatalog(skills);
    }

    private static bool IsFiniteNonNegative(double? value) =>
        value is { } v && double.IsFinite(v) && v >= 0;

    private sealed class SkillFile
    {
        public int SchemaVersion { get; init; }
        public string? SkillId { get; init; }
        public string? ClassId { get; init; }
        public int? CooldownSeconds { get; init; }
        public ResourceCostFile? ResourceCost { get; init; }
        public TargetingFile? Targeting { get; init; }
        public CoefficientsFile? Coefficients { get; init; }
        public double? TelegraphSeconds { get; init; }
        public string? VfxKey { get; init; }
    }

    private sealed class CoefficientsFile
    {
        public double? Pve { get; init; }
        public double? Boss { get; init; }
        public double? Pvp { get; init; }
    }

    private sealed class ResourceCostFile
    {
        public string? Resource { get; init; }
        public int? Amount { get; init; }
    }

    private sealed class TargetingFile
    {
        public string? Type { get; init; }
        public double? RangeWu { get; init; }
        public double? AngleDegrees { get; init; }
        public int? MaxTargets { get; init; }
    }
}
