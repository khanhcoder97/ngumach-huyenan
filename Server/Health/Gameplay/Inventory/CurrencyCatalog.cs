using System.Globalization;

namespace Server.Health.Gameplay.Inventory;

// Work order 29 Q5 names currency, and docs/production/Currency_Production_Data_vi.csv is
// the canonical table: 16 currencies, each with a balance cap, a daily cap, a reset
// schedule, a storage scope, and tradeability. The server had never read it - it hard-codes
// the one id it grants (`LootCurrencyIds.Coin`) and only guards against arithmetic
// overflow - so the caps and the character/account split existed on paper only.
//
// This catalogue is inert on purpose. Enforcing `balance_cap` or `daily_cap` turns a grant
// that succeeds today into a refusal and needs a wire error code, which is a contract change
// to be approved, not assumed. What is safe now is to load the table, refuse to load a row
// whose vocabulary the server cannot interpret, and cross-check the ids the shipped content
// actually pays out.
public enum DailyCapKind
{
    None,
    Amount,
    Unscheduled
}

public sealed record DailyCapLimit(DailyCapKind Kind, long Amount, string Raw);

public sealed record CurrencyCatalogEntry(
    string CurrencyId,
    string DisplayNameVi,
    string CurrencyType,
    bool Tradeable,
    string StorageScope,
    long BalanceCap,
    DailyCapLimit DailyCap,
    string WeeklyReset,
    string Sources,
    string Sinks,
    string Notes);

public sealed class CurrencyCatalog(
    IReadOnlyDictionary<string, CurrencyCatalogEntry> currencies)
{
    private readonly IReadOnlyDictionary<string, CurrencyCatalogEntry> _currencies = currencies;

    public int Count => _currencies.Count;

    public IEnumerable<CurrencyCatalogEntry> Rows => _currencies.Values;

    public bool TryGet(string currencyId, out CurrencyCatalogEntry currency) =>
        _currencies.TryGetValue(currencyId, out currency!);

    public int CountWhere(Func<CurrencyCatalogEntry, bool> predicate) =>
        _currencies.Values.Count(predicate);
}

public static class CurrencyCatalogLoader
{
    public const string RelativePath = "docs/production/Currency_Production_Data_vi.csv";

    private static readonly string[] ExpectedHeader =
    [
        "currency_id", "display_name_vi", "currency_type", "tradeable", "storage_scope",
        "balance_cap", "daily_cap", "weekly_reset", "sources", "sinks", "notes"
    ];

    private static readonly string[] KnownTypes =
    [
        "SOFT", "REGIONAL_REPUTATION", "DUNGEON_TOKEN", "RAID_TOKEN",
        "PVP_COSMETIC", "PVE_COSMETIC", "SOCIAL"
    ];

    private static readonly string[] KnownScopes = ["character", "account"];

    private static readonly System.Text.RegularExpressions.Regex CurrencyIdPattern =
        new(@"^[A-Z][A-Z0-9_]{1,63}$", System.Text.RegularExpressions.RegexOptions.CultureInvariant);

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

    public static CurrencyCatalog Load(string docsDirectory)
    {
        var path = Path.Combine(docsDirectory, RelativePath);
        var lines = File.ReadAllLines(path);
        if (lines.Length < 2)
        {
            throw new InvalidOperationException($"{path}: currency catalog has no data rows.");
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

        var currencies = new Dictionary<string, CurrencyCatalogEntry>(StringComparer.Ordinal);
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

            var currencyId = Cell("currency_id");
            if (!CurrencyIdPattern.IsMatch(currencyId))
            {
                throw new InvalidOperationException($"{path}:{row + 1}: invalid currency_id '{currencyId}'.");
            }

            var currencyType = Cell("currency_type");
            if (!KnownTypes.Contains(currencyType, StringComparer.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{path}:{row + 1}: unknown currency_type '{currencyType}'.");
            }

            var scope = Cell("storage_scope");
            if (!KnownScopes.Contains(scope, StringComparer.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{path}:{row + 1}: unknown storage_scope '{scope}'.");
            }

            if (!bool.TryParse(Cell("tradeable"), out var tradeable))
            {
                throw new InvalidOperationException(
                    $"{path}:{row + 1}: tradeable must be true or false, " +
                    $"found '{Cell("tradeable")}'.");
            }

            if (!long.TryParse(Cell("balance_cap"), NumberStyles.None, CultureInfo.InvariantCulture,
                    out var balanceCap) || balanceCap < 1)
            {
                throw new InvalidOperationException(
                    $"{path}:{row + 1}: balance_cap must be a positive integer, " +
                    $"found '{Cell("balance_cap")}'.");
            }

            var dailyCap = ReadDailyCap(Cell("daily_cap"));

            foreach (var column in new[] { "display_name_vi", "sources", "sinks", "notes" })
            {
                if (Cell(column).Length == 0)
                {
                    throw new InvalidOperationException(
                        $"{path}:{row + 1}: {column} is required (the source leaves no currency undocumented).");
                }
            }

            var entry = new CurrencyCatalogEntry(
                currencyId,
                Cell("display_name_vi"),
                currencyType,
                tradeable,
                scope,
                balanceCap,
                dailyCap,
                Cell("weekly_reset"),
                Cell("sources"),
                Cell("sinks"),
                Cell("notes"));

            if (!currencies.TryAdd(currencyId, entry))
            {
                throw new InvalidOperationException($"{path}:{row + 1}: duplicate currency_id '{currencyId}'.");
            }
        }

        return new CurrencyCatalog(currencies);
    }

    // `daily_cap` is closed for seven rows ("none") and numeric for eight, and one row
    // genuinely says "per scheduled match" - a cap that exists but is not a number the
    // server could enforce. It is kept as Unscheduled with its raw text rather than being
    // rounded to zero or to a made-up limit.
    private static DailyCapLimit ReadDailyCap(string raw)
    {
        if (string.Equals(raw, "none", StringComparison.Ordinal))
        {
            return new DailyCapLimit(DailyCapKind.None, 0, raw);
        }

        if (long.TryParse(raw, NumberStyles.None, CultureInfo.InvariantCulture, out var amount) && amount > 0)
        {
            return new DailyCapLimit(DailyCapKind.Amount, amount, raw);
        }

        return new DailyCapLimit(DailyCapKind.Unscheduled, 0, raw);
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
