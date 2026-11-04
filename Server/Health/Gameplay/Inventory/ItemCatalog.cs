using System.Text.RegularExpressions;
using Server.Health.Contracts;

namespace Server.Health.Gameplay.Inventory;

// Q-E: the source of truth for what an item *is* when a player tries to equip
// it. The CSV is Vietnamese-labelled; wire slots are fixed ASCII tokens, so the
// mapping lives here instead of leaking catalogue labels into a contract.
//
// The approved v1 wire enum has five slots (EquipRequest/UnequipRequest). The
// catalogue and Character_Equipment_Inventory_Spec §3 define twelve player
// slots, so the five tokens cover what they can and the two armour labels with
// no token (Quần, Găng) stay explicitly unmapped: those items are refused as
// `not_equippable` rather than guessed into a neighbouring slot. Any *other*
// equipment label without a token fails the loader, so a new source slot can
// never slip through silently.
//
// The v2 contract (QOD-21 Q3) does name all twelve, so the raw canonical label
// is kept on the entry next to the v1 token: `InventoryV2Slots` resolves it
// without any consumer having to re-read the CSV or guess from an item id. The
// v1 token stays exactly as it was, so v1 behaviour is untouched.
public sealed record ItemCatalogEntry(
    string ItemId,
    string Category,
    string? SlotToken,
    string? SlotLabel,
    string? ClassId,
    int RequiredLevel,
    string RarityPool,
    int StackLimit);

public sealed class ItemCatalog
{
    public const string RelativePath = "docs/production/Item_Master_Catalog_vi.csv";
    public const string VariantRelativePath =
        "docs/production/Item_Rarity_Variant_Catalog_vi.csv";
    public const string ArmorCategory = "Trang bị / giáp";
    public const string WeaponCategory = "Trang bị / vũ khí";
    public const string AccessoryCategory = "Trang bị / phụ kiện";

    private static readonly Dictionary<string, string> SlotTokens = new(StringComparer.Ordinal)
    {
        ["Nón"] = "HAT",
        ["Áo"] = "CHEST",
        ["Giày"] = "BOOTS",
        ["Kiếm"] = "WEAPON",
        ["Đao"] = "WEAPON",
        ["Bút"] = "WEAPON",
        ["Chùy"] = "WEAPON",
        ["Cung"] = "WEAPON",
        ["Dây chuyền"] = "ACCESSORY",
        ["Nhẫn trái"] = "ACCESSORY",
        ["Nhẫn phải"] = "ACCESSORY",
        ["Ngọc bội"] = "ACCESSORY",
        ["Phi phong"] = "ACCESSORY",
        ["Ấn hộ mệnh"] = "ACCESSORY",
    };

    // Sourced labels with no approved wire token. They stay in the catalogue
    // (other systems may reference the items) but cannot be equipped in v1.
    private static readonly HashSet<string> UnmappedEquipmentSlots =
        new(StringComparer.Ordinal) { "Quần", "Găng" };

    private readonly IReadOnlyDictionary<string, ItemCatalogEntry> _items;

    private ItemCatalog(IReadOnlyDictionary<string, ItemCatalogEntry> items)
    {
        _items = items;
    }

    public int Count => _items.Count;

    public bool TryGet(string itemId, out ItemCatalogEntry entry) =>
        _items.TryGetValue(itemId, out entry!);

    // Equipment rows only, so a vocabulary check can walk every gear label without
    // any consumer re-reading the CSV or guessing from item ids.
    public IEnumerable<ItemCatalogEntry> EquipmentEntries =>
        _items.Values.Where(entry => IsEquipmentCategory(entry.Category));

    public static bool IsEquipmentCategory(string? category) =>
        string.Equals(category, ArmorCategory, StringComparison.Ordinal) ||
        string.Equals(category, WeaponCategory, StringComparison.Ordinal) ||
        string.Equals(category, AccessoryCategory, StringComparison.Ordinal);

    public static string? SlotTokenFor(string? category, string slotLabel)
    {
        if (!IsEquipmentCategory(category))
        {
            return null;
        }

        return SlotTokens.TryGetValue(slotLabel, out var token) ? token : null;
    }

    public static ItemCatalog Load(string directory)
    {
        var items = new Dictionary<string, ItemCatalogEntry>(StringComparer.Ordinal);
        LoadFile(Path.Combine(directory, RelativePath), items);
        LoadFile(Path.Combine(directory, VariantRelativePath), items);
        return new ItemCatalog(items);
    }

    private static void LoadFile(
        string path, Dictionary<string, ItemCatalogEntry> items)
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
        foreach (var required in new[]
                 {
                     "item_id", "category", "slot", "class_id", "required_level",
                     "rarity_pool", "stack_limit"
                 })
        {
            if (!index.ContainsKey(required))
            {
                throw new InvalidOperationException($"{path}: missing column '{required}'.");
            }
        }

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

            var category = Cell("category");
            var slotLabel = Cell("slot");
            string? slotToken = null;
            if (IsEquipmentCategory(category))
            {
                slotToken = SlotTokenFor(category, slotLabel);
                if (slotToken is null && !UnmappedEquipmentSlots.Contains(slotLabel))
                {
                    throw new InvalidOperationException(
                        $"{path}:{line + 1}: equipment item '{itemId}' has slot " +
                        $"'{slotLabel}' with no approved wire token; extend the " +
                        "EquipRequest/UnequipRequest slot enum first. If the label is " +
                        "one of the v2 twelve, add it to InventoryV2Slots.LabelToSlot.");
                }

                if (string.IsNullOrEmpty(Cell("class_id")))
                {
                    throw new InvalidOperationException(
                        $"{path}:{line + 1}: equipment item '{itemId}' has no class_id.");
                }
            }

            var entry = new ItemCatalogEntry(
                itemId,
                category,
                slotToken,
                IsEquipmentCategory(category) ? slotLabel : null,
                string.IsNullOrEmpty(Cell("class_id")) ? null : Cell("class_id"),
                requiredLevel,
                Cell("rarity_pool"),
                stackLimit);

            // The variant file repeats the 135 non-equipment rows verbatim;
            // identical duplicates are fine, but two different definitions of
            // one id would make the slot/class gate ambiguous.
            if (items.TryGetValue(itemId, out var existing))
            {
                if (existing != entry)
                {
                    throw new InvalidOperationException(
                        $"{path}: item_id '{itemId}' is defined twice with different data.");
                }

                continue;
            }

            items.Add(itemId, entry);
        }
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
                var candidate = Path.Combine(directory.FullName, ItemCatalog.RelativePath);
                if (File.Exists(candidate))
                {
                    return directory.FullName;
                }

                directory = directory.Parent;
            }
        }

        throw new FileNotFoundException(
            $"Could not locate {ItemCatalog.RelativePath}. Run from the repository.");
    }
}
