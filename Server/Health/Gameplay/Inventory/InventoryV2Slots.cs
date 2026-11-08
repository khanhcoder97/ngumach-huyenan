namespace Server.Health.Gameplay.Inventory;

// QOD-21 Q3: the approved v2 vocabulary (DESIGN-BM-ALPHA-20261103 `inventory` and
// DESIGN-BM-Q3-20261104 `inventory` = V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT).
// The twelve tokens come from the design; the label column next to each one is the
// canonical `slot` value in docs/production/Item_Rarity_Variant_Catalog_vi.csv, and
// the sixteen equipment labels in that file partition onto these twelve exactly
// (five armor, six accessories, five weapon forms that all share WEAPON). That
// partition is asserted at startup, not assumed: a catalog label that lands outside
// the twelve, or a design token no label covers, is reported rather than papered
// over with a guessed bucket.
//
// v1 keeps its own five-token contract untouched (`EquipmentSlots`). This class only
// projects: `CollapseToV1` answers what a v2 slot means in v1's vocabulary, and
// armor pieces v1 cannot name (LEGS, GLOVES — the two labels v1 deliberately left
// unmap-able) answer false so the v1 snapshot can still show the item, just with no
// `slot` field. An equipped item is never dropped from either view.
public static class InventoryV2Slots
{
    public const string Hat = "HAT";
    public const string Chest = "CHEST";
    public const string Legs = "LEGS";
    public const string Weapon = "WEAPON";
    public const string Gloves = "GLOVES";
    public const string Boots = "BOOTS";
    public const string Neck = "NECK";
    public const string RingLeft = "RING_L";
    public const string RingRight = "RING_R";
    public const string Pendant = "PENDANT";
    public const string Cloak = "CLOAK";
    public const string Seal = "SEAL";

    public static IReadOnlyList<string> All { get; } =
    [
        Hat, Chest, Legs, Weapon, Gloves, Boots,
        Neck, RingLeft, RingRight, Pendant, Cloak, Seal
    ];

    public static IReadOnlyDictionary<string, string> LabelToSlot { get; } =
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["Nón"] = Hat,
            ["Áo"] = Chest,
            ["Quần"] = Legs,
            ["Giày"] = Boots,
            ["Găng"] = Gloves,
            ["Kiếm"] = Weapon,
            ["Đao"] = Weapon,
            ["Bút"] = Weapon,
            ["Chùy"] = Weapon,
            ["Cung"] = Weapon,
            ["Dây chuyền"] = Neck,
            ["Nhẫn trái"] = RingLeft,
            ["Nhẫn phải"] = RingRight,
            ["Ngọc bội"] = Pendant,
            ["Phi phong"] = Cloak,
            ["Ấn hộ mệnh"] = Seal
        };

    public static bool IsValid(string? value) =>
        value is Hat or Chest or Legs or Weapon or Gloves or Boots
            or Neck or RingLeft or RingRight or Pendant or Cloak or Seal;

    public static bool TryResolveLabel(string? category, string slotLabel, out string slot)
    {
        slot = "";
        if (!ItemCatalog.IsEquipmentCategory(category) ||
            !LabelToSlot.TryGetValue(slotLabel, out var resolved))
        {
            return false;
        }

        slot = resolved;
        return true;
    }

    // What a v2 slot looks like to a v1 consumer. LEGS and GLOVES have no v1 token
    // (v1 left those two labels unmap-able on purpose), so they answer false and the
    // caller emits the item without a slot instead of inventing one.
    public static bool CollapseToV1(string slot, out string v1Slot)
    {
        v1Slot = slot switch
        {
            Hat or Chest or Boots or Weapon => slot,
            Neck or RingLeft or RingRight or Pendant or Cloak or Seal =>
                EquipmentSlots.Accessory,
            _ => ""
        };
        return v1Slot.Length > 0;
    }

    // The v2 slot an item belongs to, from its canonical catalog label. This is the
    // only place that decides it, so an equip request cannot be steered by a client
    // and a read cannot disagree with the write.
    public static bool TryResolveEntry(ItemCatalogEntry entry, out string slot)
    {
        ArgumentNullException.ThrowIfNull(entry);
        slot = "";
        return entry.SlotLabel is { } label &&
            TryResolveLabel(entry.Category, label, out var resolved) &&
            (slot = resolved).Length > 0;
    }

    // The slot an equipped item is worn in, for the v2 read model, in the order the
    // truth is known: a token a v2 write stored is authoritative; otherwise the
    // canonical catalogue names it (which is how an accessory equipped through v1's
    // lumped ACCESSORY token still lands in its own one of the six); otherwise a
    // stored string that already is one of the twelve; otherwise nothing, and the
    // caller reports the item in `unsupported` instead of dropping it.
    public static bool TryResolveWorn(
        ItemCatalogEntry? entry,
        string? storedV2,
        string? storedV1,
        out string slot)
    {
        if (IsValid(storedV2))
        {
            slot = storedV2!;
            return true;
        }

        if (entry is not null && TryResolveEntry(entry, out var resolved))
        {
            slot = resolved;
            return true;
        }

        if (IsValid(storedV1))
        {
            slot = storedV1!;
            return true;
        }

        slot = "";
        return false;
    }

    // The design names the twelve slots and their order; the implementation must
    // agree exactly, so a design edit cannot be served by the old vocabulary.
    public static void ValidateAgainstDesign(IReadOnlyList<string> designSlots)
    {
        ArgumentNullException.ThrowIfNull(designSlots);

        if (!designSlots.SequenceEqual(All, StringComparer.Ordinal))
        {
            throw new InvalidOperationException(
                "v2 inventory slots do not match the approved design: expected " +
                $"{string.Join(',', All)} in that order, found {string.Join(',', designSlots)}.");
        }
    }

    // Every implemented token must be reachable from some canonical label, and no
    // label may point outside the twelve. The catalog-side half of the same check
    // (every equipment *label* in the CSV lands on one token) runs with the v2
    // handler, because the loaded entry keeps the mapped token rather than the raw
    // label; until then this partition is stated and asserted only in this
    // direction, not claimed for the whole catalog.
    public static void ValidateLabelMap()
    {
        var covered = new HashSet<string>(StringComparer.Ordinal);
        foreach (var (label, slot) in LabelToSlot)
        {
            if (!IsValid(slot))
            {
                throw new InvalidOperationException(
                    $"Canonical slot label '{label}' maps outside the approved twelve: {slot}.");
            }

            covered.Add(slot);
        }

        var uncovered = All.Where(slot => !covered.Contains(slot)).ToArray();
        if (uncovered.Length > 0)
        {
            throw new InvalidOperationException(
                $"No canonical slot label reaches {string.Join(',', uncovered)}.");
        }
    }

    // The other direction, over the real catalogue: every equipment row's label has
    // to land on one of the twelve and every token has to be reachable from some
    // row. A label that appears in the CSV and not here means v2 would refuse to
    // equip an item the source clearly names, which is a data fault to fail on at
    // startup rather than a runtime `not_equippable` surprise.
    public static void ValidateCatalogLabels(ItemCatalog catalog)
    {
        ArgumentNullException.ThrowIfNull(catalog);

        var unmapped = new SortedSet<string>(StringComparer.Ordinal);
        var covered = new HashSet<string>(StringComparer.Ordinal);
        foreach (var entry in catalog.EquipmentEntries)
        {
            if (TryResolveEntry(entry, out var slot))
            {
                covered.Add(slot);
                continue;
            }

            unmapped.Add($"{entry.Category}/{entry.SlotLabel ?? "(none)"}");
        }

        var unreachable = All.Where(slot => !covered.Contains(slot)).ToArray();
        if (unmapped.Count > 0 || unreachable.Length > 0)
        {
            throw new InvalidOperationException(
                "Canonical equipment slots do not partition onto the approved twelve: " +
                $"labels with no token [{string.Join(';', unmapped)}], " +
                $"tokens no catalogue row reaches [{string.Join(',', unreachable)}].");
        }
    }
}
