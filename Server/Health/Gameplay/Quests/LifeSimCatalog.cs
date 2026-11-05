using System.Globalization;

namespace Server.Health.Gameplay.Quests;

// Work order 29 Q5 names gather and craft. docs/production/Life_Sim_Content_Data_vi.csv is
// the table for it - 11 rows (5 CROP, 6 FISH) carrying the plot or water body each content
// sits on, the seed or bait it consumes, the yield range, the grow or fish time, a daily
// cap, a season window, a tool, a quality weight set, a failure rule, and the minigame
// the client has to present. The server had never read it: gathering today is only the
// INTERACTABLE/GATHER_NODE claim path.
//
// Like the currency and passive tables, this loads as data and enforces nothing. Running a
// farm plot or a fishing minigame is a state machine plus wire contract that nobody has
// approved; the value of loading the table now is that the ids, the weights and the timings
// are validated against the rest of the shipped content instead of living only in a CSV.
public sealed record LifeSimQualityWeight(string Rarity, int Weight);

public sealed record LifeSimContentEntry(
    string ContentId,
    string ContentType,
    string DisplayNameVi,
    string MapId,
    string ZoneId,
    double XWu,
    double YWu,
    int LevelRequired,
    string InputItemId,
    int InputQuantity,
    string OutputItemId,
    int OutputMin,
    int OutputMax,
    int ProcessSeconds,
    int InteractionSeconds,
    string ToolId,
    string? BaitItemId,
    IReadOnlyList<LifeSimQualityWeight> QualityWeights,
    int DailyCap,
    string SeasonOrWindow,
    string Minigame,
    string FailureRule,
    string Notes);

public sealed class LifeSimCatalog(IReadOnlyDictionary<string, LifeSimContentEntry> content)
{
    private readonly IReadOnlyDictionary<string, LifeSimContentEntry> _content = content;

    public int Count => _content.Count;

    public IEnumerable<LifeSimContentEntry> Rows => _content.Values;

    public bool TryGet(string contentId, out LifeSimContentEntry entry) =>
        _content.TryGetValue(contentId, out entry!);

    public int CountOfType(string contentType) =>
        _content.Values.Count(entry => string.Equals(entry.ContentType, contentType, StringComparison.Ordinal));
}

public static class LifeSimCatalogLoader
{
    public const string RelativePath = "docs/production/Life_Sim_Content_Data_vi.csv";

    private const int QualityWeightTotal = 10000;

    private static readonly string[] ExpectedHeader =
    [
        "content_id", "content_type", "display_name_vi", "map_id", "zone_id", "x_wu", "y_wu",
        "level_required", "input_item_id", "input_quantity", "output_item_id", "output_min",
        "output_max", "process_seconds", "interaction_seconds", "tool_id", "bait_item_id",
        "quality_weights", "daily_cap", "season_or_window", "minigame", "failure_rule", "notes"
    ];

    private static readonly string[] KnownTypes = ["CROP", "FISH"];

    private static readonly System.Text.RegularExpressions.Regex ContentIdPattern =
        new(@"^LIFE_[A-Z][A-Z0-9_]*$", System.Text.RegularExpressions.RegexOptions.CultureInvariant);

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

    public static LifeSimCatalog Load(string docsDirectory)
    {
        var path = Path.Combine(docsDirectory, RelativePath);
        var lines = File.ReadAllLines(path);
        if (lines.Length < 2)
        {
            throw new InvalidOperationException($"{path}: life sim catalog has no data rows.");
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

        var content = new Dictionary<string, LifeSimContentEntry>(StringComparer.Ordinal);
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
            int Int(string column) => ParseInt(path, row, column, Cell(column));

            var contentId = Cell("content_id");
            if (!ContentIdPattern.IsMatch(contentId))
            {
                throw new InvalidOperationException($"{path}:{row + 1}: invalid content_id '{contentId}'.");
            }

            var contentType = Cell("content_type");
            if (!KnownTypes.Contains(contentType, StringComparer.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{path}:{row + 1}: unknown content_type '{contentType}'.");
            }

            foreach (var column in new[]
                     {
                         "display_name_vi", "map_id", "zone_id", "input_item_id", "output_item_id",
                         "tool_id", "season_or_window", "minigame", "failure_rule", "notes"
                     })
            {
                if (Cell(column).Length == 0)
                {
                    throw new InvalidOperationException(
                        $"{path}:{row + 1}: {column} is required for '{contentId}'.");
                }
            }

            var x = ParseCoordinate(path, row, "x_wu", Cell("x_wu"));
            // y_wu is genuinely negative in the shipped table (LIFE_FISH_CA_RE sits at
            // 158,-3), so coordinates are read as signed finite numbers rather than the
            // single-lane assumption the runtime registries still make.
            var y = ParseCoordinate(path, row, "y_wu", Cell("y_wu"));

            var outputMin = Int("output_min");
            var outputMax = Int("output_max");
            if (outputMin < 1 || outputMax < outputMin)
            {
                throw new InvalidOperationException(
                    $"{path}:{row + 1}: {contentId} yield range {outputMin}..{outputMax} is not usable.");
            }

            var levelRequired = Int("level_required");
            if (levelRequired is < 1 or > 100)
            {
                throw new InvalidOperationException(
                    $"{path}:{row + 1}: {contentId} level_required {levelRequired} is outside 1..100.");
            }

            var weights = ParseQualityWeights(path, row, contentId, Cell("quality_weights"));

            var entry = new LifeSimContentEntry(
                contentId,
                contentType,
                Cell("display_name_vi"),
                Cell("map_id"),
                Cell("zone_id"),
                x,
                y,
                levelRequired,
                Cell("input_item_id"),
                Int("input_quantity"),
                Cell("output_item_id"),
                outputMin,
                outputMax,
                Int("process_seconds"),
                Int("interaction_seconds"),
                Cell("tool_id"),
                string.IsNullOrEmpty(Cell("bait_item_id")) ? null : Cell("bait_item_id"),
                weights,
                Int("daily_cap"),
                Cell("season_or_window"),
                Cell("minigame"),
                Cell("failure_rule"),
                Cell("notes"));

            if (!content.TryAdd(contentId, entry))
            {
                throw new InvalidOperationException($"{path}:{row + 1}: duplicate content_id '{contentId}'.");
            }
        }

        return new LifeSimCatalog(content);
    }

    private static IReadOnlyList<LifeSimQualityWeight> ParseQualityWeights(
        string path, int row, string contentId, string raw)
    {
        var weights = new List<LifeSimQualityWeight>();
        var total = 0;
        foreach (var fragment in raw.Split(';', StringSplitOptions.RemoveEmptyEntries))
        {
            var parts = fragment.Split(':', 2);
            if (parts.Length != 2 ||
                !int.TryParse(parts[1].Trim(), NumberStyles.None, CultureInfo.InvariantCulture, out var weight) ||
                weight < 0)
            {
                throw new InvalidOperationException(
                    $"{path}:{row + 1}: {contentId} quality weight '{fragment}' is not RARITY:int.");
            }

            weights.Add(new LifeSimQualityWeight(parts[0].Trim(), weight));
            total += weight;
        }

        if (weights.Count == 0 || total != QualityWeightTotal)
        {
            throw new InvalidOperationException(
                $"{path}:{row + 1}: {contentId} quality_weights total {total}, expected {QualityWeightTotal}.");
        }

        return weights;
    }

    private static int ParseInt(string path, int row, string column, string raw) =>
        int.TryParse(raw, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out var value)
            ? value
            : throw new InvalidOperationException(
                $"{path}:{row + 1}: {column} must be an integer, found '{raw}'.");

    private static double ParseCoordinate(string path, int row, string column, string raw) =>
        double.TryParse(raw, NumberStyles.Float, CultureInfo.InvariantCulture, out var value) &&
        double.IsFinite(value)
            ? value
            : throw new InvalidOperationException(
                $"{path}:{row + 1}: {column} must be a finite number, found '{raw}'.");

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
