using System.Globalization;

namespace Server.Health.Gameplay.Combat;

// Work order 29 Q7 names weekly arena, rank and reward. The rotation itself is already a
// production table - docs/production/Weekly_Boss_Rotation_Data_vi.csv, six weekly slots on
// one tower floor - and the server had never read it. Two things follow from loading it:
// the rotation's own shape is checked instead of being prose, and the cross-reference
// failures (below) stop being invisible until a player reaches the tower.
//
// Nothing here schedules anything. There is no weekly scheduler, no account/season config,
// and no rank/reward contract on the wire, so this is data plus the structural checks that
// a future scheduler has to rely on anyway.
public sealed record WeeklyBossRotationEntry(
    string RotationSlotId,
    int CycleIndex,
    string SourceBossId,
    string DisplayNameVi,
    string SpawnMapId,
    string SpawnZoneId,
    double SpawnXWu,
    double SpawnYWu,
    string ArenaProfileId,
    double HpMultiplier,
    double DamageMultiplier,
    string WeeklyModifierId,
    string ModifierParameters,
    string RewardTableId,
    string WeeklyRewardCap,
    string ScoreRule,
    string RotationRule,
    string SchedulerSnapshotFields,
    string ValidFromConfig);

public sealed class WeeklyBossRotationCatalog(
    IReadOnlyDictionary<string, WeeklyBossRotationEntry> slots)
{
    private readonly IReadOnlyDictionary<string, WeeklyBossRotationEntry> _slots = slots;

    public int Count => _slots.Count;

    public IEnumerable<WeeklyBossRotationEntry> Rows => _slots.Values;

    public bool TryGet(string slotId, out WeeklyBossRotationEntry entry) =>
        _slots.TryGetValue(slotId, out entry!);
}

public static class WeeklyBossRotationCatalogLoader
{
    public const string RelativePath = "docs/production/Weekly_Boss_Rotation_Data_vi.csv";

    private static readonly string[] ExpectedHeader =
    [
        "rotation_slot_id", "cycle_index", "source_boss_id", "display_name_vi", "spawn_map_id",
        "spawn_zone_id", "spawn_x_wu", "spawn_y_wu", "arena_profile_id", "hp_multiplier",
        "damage_multiplier", "weekly_modifier_id", "modifier_parameters", "reward_table_id",
        "weekly_reward_cap", "score_rule", "rotation_rule", "scheduler_snapshot_fields",
        "valid_from_config"
    ];

    private static readonly System.Text.RegularExpressions.Regex SlotIdPattern =
        new(@"^[A-Z][A-Z0-9_]*_\d{2}$", System.Text.RegularExpressions.RegexOptions.CultureInvariant);

    private static readonly System.Text.RegularExpressions.Regex BossIdPattern =
        new(@"^BOSS_[A-Z][A-Z0-9_]*$", System.Text.RegularExpressions.RegexOptions.CultureInvariant);

    public static string DiscoverDirectory(string contentRoot)
    {
        var starts = new[] { contentRoot, Directory.GetCurrentDirectory(), AppContext.BaseDirectory }
            .Where(path => !string.IsNullOrWhiteSpace(path))
            .Distinct(StringComparer.OrdinalIgnoreCase);

        foreach (var start in starts)
        {
            DirectoryInfo? directory = new(Path.GetFullPath(start));
            for (var depth = 0; depth < 12 && directory is not null; depth++)
            {
                if (File.Exists(Path.Combine(directory.FullName, RelativePath)))
                {
                    return directory.FullName;
                }

                directory = directory.Parent;
            }
        }

        throw new FileNotFoundException($"Could not locate {RelativePath}. Run from the repository.");
    }

    public static WeeklyBossRotationCatalog Load(string docsDirectory)
    {
        var path = Path.Combine(docsDirectory, RelativePath);
        var lines = File.ReadAllLines(path);
        if (lines.Length < 2)
        {
            throw new InvalidOperationException($"{path}: weekly boss rotation has no data rows.");
        }

        var header = SplitCsvLine(lines[0]);
        if (!header.SequenceEqual(ExpectedHeader, StringComparer.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: unexpected header; expected {string.Join(",", ExpectedHeader)}.");
        }

        var indexes = new Dictionary<string, int>(StringComparer.Ordinal);
        for (var column = 0; column < header.Count; column++)
        {
            indexes[header[column]] = column;
        }

        var slots = new Dictionary<string, WeeklyBossRotationEntry>(StringComparer.Ordinal);
        var cycles = new HashSet<int>();
        for (var row = 1; row < lines.Length; row++)
        {
            if (string.IsNullOrWhiteSpace(lines[row]))
            {
                continue;
            }

            var cells = SplitCsvLine(lines[row]);
            if (cells.Count != ExpectedHeader.Length)
            {
                throw new InvalidOperationException(
                    $"{path}:{row + 1}: expected {ExpectedHeader.Length} cells, found {cells.Count}.");
            }

            string Cell(string column) => cells[indexes[column]].Trim();

            var slotId = Cell("rotation_slot_id");
            if (!SlotIdPattern.IsMatch(slotId))
            {
                throw new InvalidOperationException($"{path}:{row + 1}: invalid rotation_slot_id '{slotId}'.");
            }

            var bossId = Cell("source_boss_id");
            if (!BossIdPattern.IsMatch(bossId))
            {
                throw new InvalidOperationException($"{path}:{row + 1}: invalid source_boss_id '{bossId}'.");
            }

            var cycle = int.Parse(Cell("cycle_index"), CultureInfo.InvariantCulture);
            if (cycle < 1 || !cycles.Add(cycle))
            {
                throw new InvalidOperationException(
                    $"{path}:{row + 1}: cycle_index {cycle} must be positive and unique per rotation.");
            }

            foreach (var column in new[]
                     {
                         "display_name_vi", "spawn_map_id", "spawn_zone_id", "arena_profile_id",
                         "weekly_modifier_id", "modifier_parameters", "reward_table_id",
                         "weekly_reward_cap", "score_rule", "rotation_rule",
                         "scheduler_snapshot_fields", "valid_from_config"
                     })
            {
                if (Cell(column).Length == 0)
                {
                    throw new InvalidOperationException(
                        $"{path}:{row + 1}: {column} is required for '{slotId}'.");
                }
            }

            // The modifier is a sentence, not a switch: it says telegraph is unchanged and
            // that an add-count applies "only where arena allows". A scheduler that read
            // this as a boolean would invent which arenas allow it.
            var entry = new WeeklyBossRotationEntry(
                slotId,
                cycle,
                bossId,
                Cell("display_name_vi"),
                Cell("spawn_map_id"),
                Cell("spawn_zone_id"),
                ParseNumber(path, row, "spawn_x_wu", Cell("spawn_x_wu")),
                ParseNumber(path, row, "spawn_y_wu", Cell("spawn_y_wu")),
                Cell("arena_profile_id"),
                ParsePositive(path, row, "hp_multiplier", Cell("hp_multiplier")),
                ParsePositive(path, row, "damage_multiplier", Cell("damage_multiplier")),
                Cell("weekly_modifier_id"),
                Cell("modifier_parameters"),
                Cell("reward_table_id"),
                Cell("weekly_reward_cap"),
                Cell("score_rule"),
                Cell("rotation_rule"),
                Cell("scheduler_snapshot_fields"),
                Cell("valid_from_config"));

            if (!slots.TryAdd(slotId, entry))
            {
                throw new InvalidOperationException($"{path}:{row + 1}: duplicate rotation_slot_id '{slotId}'.");
            }
        }

        return new WeeklyBossRotationCatalog(slots);
    }

    private static double ParseNumber(string path, int row, string column, string raw) =>
        double.TryParse(raw, NumberStyles.Float, CultureInfo.InvariantCulture, out var value) &&
        double.IsFinite(value)
            ? value
            : throw new InvalidOperationException(
                $"{path}:{row + 1}: {column} must be a finite number, found '{raw}'.");

    private static double ParsePositive(string path, int row, string column, string raw)
    {
        var value = ParseNumber(path, row, column, raw);
        if (value <= 0)
        {
            throw new InvalidOperationException(
                $"{path}:{row + 1}: {column} must be positive, found '{raw}'.");
        }

        return value;
    }

    private static List<string> SplitCsvLine(string line)
    {
        var cells = new List<string>();
        var current = new System.Text.StringBuilder();
        var quoted = false;

        foreach (var character in line)
        {
            if (character == '"')
            {
                quoted = !quoted;
                continue;
            }

            if (character == ',' && !quoted)
            {
                cells.Add(current.ToString());
                current.Clear();
                continue;
            }

            current.Append(character);
        }

        cells.Add(current.ToString());
        return cells;
    }
}
