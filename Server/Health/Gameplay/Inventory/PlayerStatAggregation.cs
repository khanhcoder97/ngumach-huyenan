namespace Server.Health.Gameplay.Inventory;

// DEC-023 (`Runtime_State_and_Catalog_Precision_vi.md`, §2 and §3) is the source for
// every rule here. That decision labels itself a design baseline that has *not* yet
// changed "runtime schema/loader hoặc migration save", so nothing in this file is wired
// into combat, a snapshot, or the wire: an accepted equip still moves only the
// inventory, exactly as before. What lands now is the resolution stat effects will use
// - alias collapsing, conflict reporting, the §3 clamp - pinned by the oracle numbers
// the decision publishes, so the day gear does apply cannot quietly count
// `weapon_power` twice, round a percentage nobody has ruled on, or heal somebody by
// changing a maximum.
public static class StatLabels
{
    // The overlap §2 names: these two columns describe the same base number.
    public const string WeaponPowerPhysical = "Công vật lý";
    public const string WeaponPowerMagical = "Công phép";
    public const string ArmorLabel = "Giáp";

    public const string MaxHpLabel = "HP tối đa";
    public const string MaxMpLabel = "MP tối đa";

    // §2's oracle proves these two: the sword row carries `Sức mạnh` 2 and its
    // arithmetic is 12 + 3 x 7 + 5 = 38 (5 base + 2), the hat row carries `Thể chất` 1
    // and its result is HP 212. Read off the decision's own numbers, not guessed.
    public const string StrengthLabel = "Sức mạnh";
    public const string VitalityLabel = "Thể chất";
}

public sealed record GearStatContribution(
    int WeaponAttack,
    int Armor,
    int FlatMaxHp,
    int FlatMaxMp,
    int Strength,
    int Vitality,
    // Names the row carries that the versioned map does not cover ("Chí mạng",
    // "Tốc chạy", "Độ bền", ...). §2 requires the exporter to report unknown names
    // rather than invent keys.
    IReadOnlyList<string> UnsupportedLabels,
    // Cells whose value is not a whole count: 90 variant rows hold a fractional
    // `weapon_power`, 635 a fractional `armor`, and thousands hold a modifier string
    // ("0.5%", "+10% / 20 phút", "+100 XP"). §6 leaves the rounding rule open, so they
    // are refused with itemId/field/raw, never coerced.
    IReadOnlyList<string> UnsupportedValues,
    // Both columns present with different values. §2: "Nếu hai giá trị khác nhau, fail
    // export với itemId/field/source; không tự cộng, lấy max hoặc bỏ cột tùy tiện."
    IReadOnlyList<string> Conflicts)
{
    public bool IsEmpty =>
        WeaponAttack == 0 && Armor == 0 && FlatMaxHp == 0 && FlatMaxMp == 0 &&
        Strength == 0 && Vitality == 0;
}

public sealed record DerivedStats(int HpMax, int MpMax, int PhysicalAttack, int Armor);

public static class PlayerStatAggregation
{
    // "Oracle cấp1 không gear: STR/INT/AGI/VIT/LUK=5 -> HP198, MP102,
    // PhysicalAttack20, Armor10" (§2). Every formula below is the linear form through
    // exactly the points §2 and §3 publish; nothing extrapolates past them.
    public const int BaseAbilityPoints = 5;
    public const int LevelOneHpMax = 198;
    public const int LevelOneMpMax = 102;
    public const int LevelOnePhysicalAttack = 20;
    public const int LevelOneArmor = 10;

    // 198 -> 212 across VIT 5 -> 6 in the hat oracle; armor 10 -> 12 for the same point.
    public const int HpPerVitality = 14;
    public const int ArmorPerVitality = 2;

    // §2 writes the attack line out: "12+3x7+5=38".
    public const int AttackPerStrength = 3;
    public const int UnarmedBase = 5;

    public static int HpMaxForVitality(int totalVitality) =>
        LevelOneHpMax + (totalVitality - BaseAbilityPoints) * HpPerVitality;

    public static int ArmorForVitality(int totalVitality) =>
        LevelOneArmor + (totalVitality - BaseAbilityPoints) * ArmorPerVitality;

    public static GearStatContribution Resolve(ItemCatalogEntry item)
    {
        ArgumentNullException.ThrowIfNull(item);

        var buckets = new Bucket();
        var weapon = new List<(string Field, int Value)>();
        var armor = new List<(string Field, int Value)>();

        ReadColumn(item.ItemId, "weapon_power", item.WeaponPower, buckets, weapon, armor);
        ReadColumn(item.ItemId, "armor", item.Armor, buckets, weapon, armor);
        ApplyLabel(item.ItemId, "primary_stat", item.PrimaryStat, item.PrimaryValue, buckets, weapon, armor);
        ApplyLabel(item.ItemId, "secondary_stat", item.SecondaryStat, item.SecondaryValue, buckets, weapon, armor);

        var conflicts = new List<string>();
        var weaponAttack = Collapse(weapon, "weapon_power/primary_stat", item.ItemId, conflicts);
        var armorValue = Collapse(armor, "armor/primary_stat", item.ItemId, conflicts);

        return new GearStatContribution(
            weaponAttack,
            armorValue,
            buckets.MaxHp,
            buckets.MaxMp,
            buckets.Strength,
            buckets.Vitality,
            buckets.UnsupportedLabels,
            buckets.UnsupportedValues,
            conflicts);
    }

    public static DerivedStats Derive(IReadOnlyList<GearStatContribution> gear)
    {
        ArgumentNullException.ThrowIfNull(gear);

        var strength = BaseAbilityPoints;
        var vitality = BaseAbilityPoints;
        var weaponAttack = 0;
        var armor = 0;
        var flatMaxHp = 0;
        var flatMaxMp = 0;

        foreach (var piece in gear)
        {
            strength += piece.Strength;
            vitality += piece.Vitality;
            weaponAttack += piece.WeaponAttack;
            armor += piece.Armor;
            flatMaxHp += piece.FlatMaxHp;
            flatMaxMp += piece.FlatMaxMp;
        }

        return new DerivedStats(
            HpMaxForVitality(vitality) + flatMaxHp,
            LevelOneMpMax + flatMaxMp,
            weaponAttack + AttackPerStrength * strength + UnarmedBase,
            ArmorForVitality(vitality) + armor);
    }

    // §3: recalculating a maximum - level, point spend, equip/unequip, an expiring buff
    // or a loadout swap - never heals and never revives. The current value stays
    // absolute and clamps into the new maximum, so re-equipping the +18 HP hat after
    // taking it off at 210/216 leaves the actor at 198 and does not hand back 12 HP.
    public static int ClampAfterMaxChange(int current, int newMaximum)
    {
        if (newMaximum < 0)
        {
            throw new ArgumentOutOfRangeException(
                nameof(newMaximum), newMaximum, "A maximum cannot be negative.");
        }

        return Math.Clamp(current, 0, newMaximum);
    }

    // The two standalone columns are not labels, so they enter the same candidate lists
    // the `primary_stat` alias would, which is what makes the double-count visible.
    private static void ReadColumn(
        string itemId,
        string field,
        string? raw,
        Bucket buckets,
        List<(string Field, int Value)> weapon,
        List<(string Field, int Value)> armor)
    {
        if (raw is null)
        {
            return;
        }

        // §2: each column is its own source, and the alias only bites when
        // `primary_stat` names the same number - which Collapse decides. A row whose
        // primary column describes something else (a haste label, say) still keeps its
        // armor or power value: "Nếu một cột trống, dùng giá trị ở cột có nguồn."
        if (TryWholeCount(raw, out var value))
        {
            if (field == "weapon_power")
            {
                weapon.Add((field, value));
            }
            else
            {
                armor.Add((field, value));
            }
        }
        else
        {
            buckets.UnsupportedValues.Add($"{itemId}: {field}='{raw}' is not a whole count");
        }
    }

    private static void ApplyLabel(
        string itemId,
        string field,
        string? label,
        string? raw,
        Bucket buckets,
        List<(string Field, int Value)> weapon,
        List<(string Field, int Value)> armor)
    {
        if (label is null)
        {
            return;
        }

        if (raw is null)
        {
            buckets.UnsupportedValues.Add($"{itemId}: {field}='{label}' has no value cell");
            return;
        }

        if (label is not (StatLabels.WeaponPowerPhysical or StatLabels.WeaponPowerMagical
            or StatLabels.ArmorLabel or StatLabels.MaxHpLabel or StatLabels.MaxMpLabel
            or StatLabels.StrengthLabel or StatLabels.VitalityLabel))
        {
            buckets.UnsupportedLabels.Add(label);
            return;
        }

        if (!TryWholeCount(raw, out var value))
        {
            buckets.UnsupportedValues.Add($"{itemId}: {field}='{label}' value '{raw}' is not a whole count");
            return;
        }

        switch (label)
        {
            case StatLabels.WeaponPowerPhysical:
            case StatLabels.WeaponPowerMagical:
                weapon.Add(($"{field}={label}", value));
                break;
            case StatLabels.ArmorLabel:
                armor.Add(($"{field}={label}", value));
                break;
            case StatLabels.MaxHpLabel:
                buckets.MaxHp += value;
                break;
            case StatLabels.MaxMpLabel:
                buckets.MaxMp += value;
                break;
            case StatLabels.StrengthLabel:
                buckets.Strength += value;
                break;
            default:
                buckets.Vitality += value;
                break;
        }
    }

    private static bool TryWholeCount(string raw, out int value) =>
        int.TryParse(raw.AsSpan().Trim(), System.Globalization.NumberStyles.AllowLeadingSign,
            System.Globalization.CultureInfo.InvariantCulture, out value) && value >= 0;

    private static int Collapse(
        List<(string Field, int Value)> candidates,
        string fieldPair,
        string itemId,
        List<string> conflicts)
    {
        if (candidates.Count == 0)
        {
            return 0;
        }

        var agreed = candidates[0].Value;
        if (candidates.TrueForAll(candidate => candidate.Value == agreed))
        {
            return agreed;
        }

        conflicts.Add(
            $"{itemId}: {fieldPair} disagree ({string.Join(" vs ", candidates.Select(c => $"{c.Field}={c.Value}"))}); " +
            "DEC-023 §2 forbids summing, taking max or dropping a column arbitrarily.");
        return 0;
    }

    private sealed class Bucket
    {
        public int MaxHp;
        public int MaxMp;
        public int Strength;
        public int Vitality;
        public readonly List<string> UnsupportedLabels = [];
        public readonly List<string> UnsupportedValues = [];
    }
}
