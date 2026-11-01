using System.Text.RegularExpressions;
using Server.Health.Contracts;

namespace Server.Health.Gameplay.Inventory;

// Q-E: the source of truth for what an item *is* when a player tries to equip
// it. The CSV is Vietnamese-labelled; wire slots are fixed ASCII tokens, so the
// mapping lives here instead of leaking catalogue labels into a contract. A
// label this map does not know is not guessed: the item simply cannot be
// equipped (`not_equippable`) until someone extends the map with a source.
public sealed record ItemCatalogEntry(
    string ItemId,
    string Category,
    string? SlotToken,
    string? ClassId,
    int RequiredLevel,
    string RarityPool,
    int StackLimit);

public sealed class ItemCatalog
{
    public const string RelativePath = "docs/production/Item_Master_Catalog_vi.csv";
    public const string EquipmentCategory = "Trang bị / giáp";

    private static readonly Dictionary<string, string> SlotTokens = new(StringComparer.Ordinal)
    {
        ["Nón"] = "HAT",
        ["Áo"] = "CHEST",
        ["Giày"] = "BOOTS",
        ["Kiếm"] = "WEAPON",
    };

    private readonly IReadOnlyDictionary<string, ItemCatalogEntry> _items;

    private ItemCatalog(IReadOnlyDictionary<string, ItemCatalogEntry> items)
    {
        _items = items;
    }

    public int Count => _items.Count;

    public bool TryGet(string itemId, out ItemCatalogEntry entry) =>
        _items.TryGetValue(itemId, out entry!);

    public static string? SlotTokenFor(string slotLabel) =>
        SlotTokens.TryGetValue(slotLabel, out var token) ? token : null;

    public static ItemCatalog Load(string path)
    {
        if (!File.Exists(path))
        {
            throw new FileNotFoundException($"{path}: item catalogue not found.");
        }

        var lines = File.ReadAllLines(path);
        if (lines.Length < 2)
        {
            throw new InvalidOperationException($"{path}: item catalogue is empty.");
        }

        var headers = SplitCsvLine(lines[0]);
        var index = headers
            .Select((name, position) => (name, position))
            .ToDictionary(pair => pair.name, pair => pair.position, StringComparer.Ordinal);
        foreach (var required in new[] { "item_id", "category", "slot", "class_id", "required_level", "rarity_pool", "stack_limit" })
        {
            if (!index.ContainsKey(required))
            {
                throw new InvalidOperationException($"{path}: missing column '{required}'.");
            }
        }

        var items = new Dictionary<string, ItemCatalogEntry>(StringComparer.Ordinal);
        for (var line = 1; line < lines.Length; line++)
        {
            if (string.IsNullOrWhiteSpace(lines[line]))
            {
                continue;
            }

            var cells = SplitCsvLine(lines[line]);
            string Cell(string column) =>
                index[column] < cells.Count ? cells[index[column]].Trim() : string.Empty;

            var itemId = Cell("item_id");
            if (!Regex.IsMatch(itemId, @"^[A-Z0-9][A-Z0-9_-]+$"))
            {
                throw new InvalidOperationException(
                    $"{path}:{line + 1}: invalid item_id '{itemId}'.");
            }

            if (!int.TryParse(Cell("required_level"), out var requiredLevel) || requiredLevel < 0)
            {
                throw new InvalidOperationException(
                    $"{path}:{line + 1}: invalid required_level for '{itemId}'.");
            }

            if (!int.TryParse(Cell("stack_limit"), out var stackLimit) || stackLimit < 1)
            {
                throw new InvalidOperationException(
                    $"{path}:{line + 1}: invalid stack_limit for '{itemId}'.");
            }

            var entry = new ItemCatalogEntry(
                itemId,
                Cell("category"),
                SlotTokenFor(Cell("slot")),
                string.IsNullOrEmpty(Cell("class_id")) ? null : Cell("class_id"),
                requiredLevel,
                Cell("rarity_pool"),
                stackLimit);
            if (!items.TryAdd(itemId, entry))
            {
                throw new InvalidOperationException($"{path}: duplicate item_id '{itemId}'.");
            }
        }

        return new ItemCatalog(items);
    }

    // The catalogue is quoted CSV; a minimal splitter keeps this loader free of
    // a dependency while still honouring quoted commas.
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

public static class ItemCatalogDiscovery
{
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
                var candidate = Path.Combine(directory.FullName, ItemCatalog.RelativePath);
                if (File.Exists(candidate))
                {
                    return candidate;
                }

                directory = directory.Parent;
            }
        }

        throw new FileNotFoundException(
            $"Could not locate {ItemCatalog.RelativePath}. Run from the repository.");
    }
}
