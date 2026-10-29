using System.Text.Json;

namespace Server.Health.Gameplay.Combat;

// P1_Design_Resolution_20261029_vi.md §1: SK-MK-03 range comes from
// completion_v1 combat.skillRangeMigrationWu (4.4 WU, cone 100°, cap 5) as
// its own migration example/schema/loader — the SkillDefinition example
// intentionally stays without rangeWu. This migration is applied only when
// P1:CombatDamage:Enabled=true.
public sealed record SkillRangeMigration(
    IReadOnlyDictionary<string, double> RangeWuBySkillId);

public static class SkillRangeMigrationLoader
{
    private const string RelativePath =
        "Implementation/Content/DesignBaselines/completion_v1.json";
    private const int MaxSearchDepth = 12;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public static string DiscoverPath(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:DesignBaselinesPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:DesignBaselinesPath points to '{resolved}', which does not exist.");
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
            $"Could not locate {RelativePath}. Set Content:DesignBaselinesPath or run from the repository.");
    }

    public static SkillRangeMigration Load(string path)
    {
        CompletionFile? file;
        try
        {
            using var stream = File.OpenRead(path);
            file = JsonSerializer.Deserialize<CompletionFile>(stream, JsonOptions);
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

        if (!string.Equals(
                file.Activation,
                "DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION",
                StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: activation must be DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION.");
        }

        var ranges = new Dictionary<string, double>(StringComparer.Ordinal);
        foreach (var (skillId, rangeWu) in file.Combat?.SkillRangeMigrationWu ?? [])
        {
            if (skillId is null || !P1Validation.IsSkillId(skillId))
            {
                throw new InvalidOperationException(
                    $"{path}: invalid skillRangeMigrationWu key '{skillId}'.");
            }

            if (!double.IsFinite(rangeWu) || rangeWu <= 0)
            {
                throw new InvalidOperationException(
                    $"{path}: skillRangeMigrationWu['{skillId}'] must be a positive finite number.");
            }

            ranges[skillId] = rangeWu;
        }

        return new SkillRangeMigration(ranges);
    }

    private sealed class CompletionFile
    {
        public int SchemaVersion { get; init; }
        public string? Activation { get; init; }
        public CombatFile? Combat { get; init; }
    }

    private sealed class CombatFile
    {
        public Dictionary<string, double>? SkillRangeMigrationWu { get; init; }
    }
}
