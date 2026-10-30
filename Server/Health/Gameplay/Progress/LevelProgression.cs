using System.Text.Json;
using System.Text.RegularExpressions;
using Server.Health.World;

namespace Server.Health.Gameplay.Progress;

// Q-D: the level curve is source data (`level_progression_v1.json`, 100 rows
// with cumulative thresholds and allocatable points), but *how much XP a quest
// hands out* is not defined anywhere yet: quest records only name a rule
// (`LEVEL_BAND_BASE`). So the transaction is real and tested, and the amount
// resolver is an explicit dependency whose default answers "no source" rather
// than a number somebody made up.
public sealed record LevelStep(int Level, long XpFromPreviousLevels, int XpToNext, int AllocatablePointsTotal);

public sealed class LevelProgressionTable
{
    public const string RelativePath = "Implementation/Content/DesignBaselines/level_progression_v1.json";

    private readonly IReadOnlyList<LevelStep> _steps;

    private LevelProgressionTable(IReadOnlyList<LevelStep> steps)
    {
        _steps = steps;
    }

    public int MaxLevel => _steps[^1].Level;

    public LevelStep At(int level) => _steps[level - 1];

    // Highest level whose cumulative threshold the total XP reaches, capped by
    // the table itself: XP past the last step accumulates but cannot level.
    public int LevelFor(long totalXp)
    {
        var level = 1;
        foreach (var step in _steps)
        {
            if (totalXp < step.XpFromPreviousLevels)
            {
                break;
            }

            level = step.Level;
        }

        return level;
    }

    public static string Discover(string contentRoot)
    {
        var starts = new[] { contentRoot, Directory.GetCurrentDirectory(), AppContext.BaseDirectory }
            .Where(path => !string.IsNullOrWhiteSpace(path))
            .Distinct(StringComparer.OrdinalIgnoreCase);
        foreach (var start in starts)
        {
            DirectoryInfo? directory = new(Path.GetFullPath(start));
            for (var depth = 0; depth < 12 && directory is not null; depth++)
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
            $"Could not locate {RelativePath}. Run from the repository.");
    }

    public static LevelProgressionTable Load(string path)
    {
        using var stream = File.OpenRead(path);
        var file = JsonSerializer.Deserialize<FileShape>(stream, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        }) ?? throw new InvalidOperationException($"{path}: file is empty.");

        var levels = file.Levels ?? [];
        if (levels.Count == 0)
        {
            throw new InvalidOperationException($"{path}: no levels.");
        }

        var steps = new List<LevelStep>(levels.Count);
        long previousThreshold = -1;
        for (var index = 0; index < levels.Count; index++)
        {
            var level = levels[index];
            if (level.Level != index + 1)
            {
                throw new InvalidOperationException(
                    $"{path}: expected level {index + 1}, found {level.Level}.");
            }

            if (level.XpFromPreviousLevels < previousThreshold || level.XpToNext < 0)
            {
                throw new InvalidOperationException(
                    $"{path}: level {level.Level} has non-monotonic XP thresholds.");
            }

            previousThreshold = level.XpFromPreviousLevels;
            steps.Add(new LevelStep(
                level.Level, level.XpFromPreviousLevels, level.XpToNext,
                level.AllocatablePointsTotal));
        }

        return new LevelProgressionTable(steps);
    }
}

public sealed class ExperienceGrant
{
    public required long TotalXpBefore { get; init; }
    public required long TotalXpAfter { get; init; }
    public required int LevelBefore { get; init; }
    public required int LevelAfter { get; init; }
    public required int LevelCap { get; init; }

    public int LevelsGained => LevelAfter - LevelBefore;

    public required LevelProgressionTable Table { get; init; }
}

public interface IQuestXpRule
{
    // Null means the source does not define this rule's amount yet; the caller
    // must not guess and must leave the reward unapplied.
    long? Resolve(string ruleId);
}

// The shipped resolver: no canonical document states how much XP
// LEVEL_BAND_BASE is worth, so it resolves nothing until that lands.
public sealed class UnresolvedQuestXpRules : IQuestXpRule
{
    public long? Resolve(string ruleId) => null;
}

public sealed class ExperienceService
{
    private readonly LevelProgressionTable _table;
    private readonly IQuestXpRule _rules;

    public ExperienceService(LevelProgressionTable table, IQuestXpRule rules)
    {
        _table = table;
        _rules = rules;
    }

    public LevelProgressionTable Table => _table;

    public bool TryApply(PlayerSession actor, string ruleId, out ExperienceGrant? grant, out string? unresolvedRule)
    {
        ArgumentNullException.ThrowIfNull(actor);

        var amount = _rules.Resolve(ruleId);
        if (amount is not { } xp || xp < 0)
        {
            grant = null;
            unresolvedRule = ruleId;
            return false;
        }

        lock (actor.SyncRoot)
        {
            var before = actor.TotalXp;
            var levelBefore = actor.Level;
            var after = before + xp;
            var levelAfter = _table.LevelFor(after);
            actor.TotalXp = after;
            actor.Level = levelAfter;
            actor.UnspentPoints = _table.At(levelAfter).AllocatablePointsTotal;
            grant = new ExperienceGrant
            {
                TotalXpBefore = before,
                TotalXpAfter = after,
                LevelBefore = levelBefore,
                LevelAfter = levelAfter,
                LevelCap = _table.MaxLevel,
                Table = _table
            };
            unresolvedRule = null;
            return true;
        }
    }

    // Rollback path: the turn-in transaction restores the exact prior numbers if
    // a later step (ledger) fails, so XP is never granted by a failed turn-in.
    public void Restore(PlayerSession actor, ExperienceGrant grant)
    {
        lock (actor.SyncRoot)
        {
            actor.TotalXp = grant.TotalXpBefore;
            actor.Level = grant.LevelBefore;
            actor.UnspentPoints = grant.Table.At(grant.LevelBefore).AllocatablePointsTotal;
        }
    }

    private sealed class FileShape
    {
        public List<LevelShape>? Levels { get; init; }
    }

    private sealed class LevelShape
    {
        public int Level { get; init; }
        public long XpFromPreviousLevels { get; init; }
        public int XpToNext { get; init; }
        public int AllocatablePointsTotal { get; init; }
    }
}
