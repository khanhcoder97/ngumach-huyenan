using System.Globalization;
using Server.Health.Gameplay.Combat;

namespace Server.Health.Gameplay.Pets;

// QOD-24: `Pet_Mount_Production_Data_vi.csv` is the last approved production table this
// server had never read. It stays data-only: there is no companion route, no gate and no
// wire field, because neither Production_Rules nor Production_Technical_Contracts says how
// a pet enters the damage formula, the leash tick or the bag. Loading it exists so that a
// disagreement with the shipped item catalogue becomes a named number in CI instead of a
// sentence in a report.
public sealed record CompanionEntry(
    string EntityId,
    string ItemTemplateId,
    string EntityType,
    string DisplayNameVi,
    string Element,
    string Rarity,
    int LevelCap,
    string UnlockSource,
    string ActiveSkillId,
    string ActiveSkillEffect,
    string PassiveSkillId,
    string PassiveEffect,
    string SkillUnlockLevels,
    string ExperienceSource,
    string EquipmentSlots,
    string CombatRule,
    int OwnerRangeWu,
    string LeashBehavior,
    string FeedItemId,
    int FeedCooldownHours,
    string FeedStat,
    string RigId)
{
    public bool IsCompanion =>
        string.Equals(EntityType, CompanionCatalog.CompanionType, StringComparison.Ordinal);
}

public static class CompanionCatalog
{
    public const string RelativePath = "docs/production/Pet_Mount_Production_Data_vi.csv";

    public const string CompanionType = "COMPANION";
    public const string MountType = "MOUNT";

    private static readonly string[] ExpectedHeader =
    [
        "entity_id", "item_template_id", "entity_type", "display_name_vi", "element",
        "rarity", "level_cap", "unlock_source", "active_skill_id", "active_skill_effect",
        "passive_skill_id", "passive_effect", "skill_unlock_levels", "xp_source",
        "equipment_slots", "combat_rule", "owner_range_wu", "leash_behavior",
        "feed_item_id", "feed_cooldown_hours", "feed_stat", "animation_spec", "rig_id"
    ];

    // The five elements the source gives companions. Mounts carry the literal COSMETIC in
    // the same column, which is not an element, so the two type sets are validated apart.
    private static readonly HashSet<string> KnownElements = new(StringComparer.Ordinal)
    {
        "Mộc", "Thủy", "Thổ", "Hỏa", "Kim"
    };

    private static readonly HashSet<string> KnownRarities = new(StringComparer.Ordinal)
    {
        "COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"
    };

    // Closed sets, not prefixes: each of these is the whole sentence the source states, so
    // a third combat rule or a stat-bearing pet slot fails startup instead of being
    // silently reinterpreted by whoever notices it first.
    public const string CompanionCombatRule =
        "PvE normal mobs only; no pet damage/heal in PvP, raid boss, world boss or siege objective";

    public const string MountCombatRule =
        "no combat; overworld out-of-combat travel speed +10%; disabled in combat/PvP/instance objective";

    public const string CompanionSlots =
        "PET_HEAD;PET_ARMOR;PET_COLLAR;PET_SADDLE (appearance slots only; no stat item in baseline)";

    public const string MountSlots = "MOUNT_SADDLE cosmetic only";

    public const string CompanionLeash =
        "teleport to owner after 5s out of range; despawn in cutscene";

    public const string MountLeash =
        "dismount on combat, dialogue, indoor hub and all instanced activities";

    public const string CompanionExperience =
        "daily activity participation; no AFK XP; cap 1 level/day to L20, 2/day after";

    public const string MountExperience = "none";

    public static IReadOnlyList<CompanionEntry> Load(string directory)
    {
        var path = Path.Combine(directory, RelativePath);
        var lines = File.ReadAllLines(path);
        if (lines.Length == 0)
        {
            throw new InvalidOperationException($"{path}: empty.");
        }

        var header = MobEliteVariantCatalog.SplitCsvLine(lines[0]);
        if (!header.SequenceEqual(ExpectedHeader, StringComparer.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: header changed from the approved 23 columns.");
        }

        var rows = new List<CompanionEntry>();
        var rigs = new HashSet<string>(StringComparer.Ordinal);
        for (var index = 1; index < lines.Length; index++)
        {
            if (string.IsNullOrWhiteSpace(lines[index]))
            {
                continue;
            }

            var cells = MobEliteVariantCatalog.SplitCsvLine(lines[index]);
            var row = cells.Count >= ExpectedHeader.Length
                ? cells.GetRange(0, ExpectedHeader.Length)
                : cells.Concat(Enumerable.Repeat("", ExpectedHeader.Length - cells.Count)).ToList();
            var where = $"{path} line {index + 1}";
            var isCompanion = string.Equals(row[2], CompanionType, StringComparison.Ordinal);

            if (!isCompanion && !string.Equals(row[2], MountType, StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{where}: entity_type '{row[2]}' is neither COMPANION nor MOUNT.");
            }

            var entityPrefix = isCompanion ? "PET_" : "MOUNT_";
            var templatePrefix = isCompanion ? "PET-" : "MOUNT-";
            if (!row[0].StartsWith(entityPrefix, StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{where}: {row[2]} entity id '{row[0]}' is not {entityPrefix}*.");
            }

            if (!row[1].StartsWith(templatePrefix, StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{where}: {row[2]} names item template '{row[1]}', not {templatePrefix}*.");
            }

            // A companion is the only row with an element; a mount that grows one would
            // mean elemental damage on travel, which no source describes.
            if (isCompanion ? !KnownElements.Contains(row[4]) : row[4] != "COSMETIC")
            {
                throw new InvalidOperationException(
                    $"{where}: element '{row[4]}' is not valid for {row[2]}.");
            }

            if (!KnownRarities.Contains(row[5]))
            {
                throw new InvalidOperationException($"{where}: unknown rarity '{row[5]}'.");
            }

            if (!int.TryParse(row[6], NumberStyles.Integer, CultureInfo.InvariantCulture,
                    out var levelCap) || levelCap < 1)
            {
                throw new InvalidOperationException(
                    $"{where}: level_cap '{row[6]}' is not a positive integer.");
            }

            if (row[7].Length == 0)
            {
                throw new InvalidOperationException($"{where}: unlock_source is blank.");
            }

            if (isCompanion)
            {
                if (!row[8].StartsWith("PET_SKILL_", StringComparison.Ordinal) ||
                    row[9].Length == 0 ||
                    !row[10].StartsWith("PET_PASSIVE_", StringComparison.Ordinal) ||
                    row[11].Length == 0)
                {
                    throw new InvalidOperationException(
                        $"{where}: a companion must carry one PET_SKILL_*/PET_PASSIVE_* " +
                        $"pair with effects (got '{row[8]}'/'{row[10]}').");
                }

                if (!SkillUnlockLevels.IsMatch(row[12]))
                {
                    throw new InvalidOperationException(
                        $"{where}: skill_unlock_levels '{row[12]}' is not a semicolon level list.");
                }
            }
            else if (row[8].Length > 0 || row[10].Length > 0 || row[12].Length > 0)
            {
                throw new InvalidOperationException(
                    $"{where}: a mount carries skill columns, which the source reserves " +
                    "for companions.");
            }

            if (!string.Equals(row[13], isCompanion ? CompanionExperience : MountExperience,
                    StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{where}: xp_source '{row[13]}' is not the one rule the source states " +
                    $"for {row[2]}.");
            }

            if (!string.Equals(row[14], isCompanion ? CompanionSlots : MountSlots,
                    StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{where}: equipment_slots '{row[14]}' is not the sourced {row[2]} set.");
            }

            if (!string.Equals(row[15], isCompanion ? CompanionCombatRule : MountCombatRule,
                    StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{where}: combat_rule '{row[15]}' is not the sourced {row[2]} rule.");
            }

            if (!int.TryParse(row[16], NumberStyles.Integer, CultureInfo.InvariantCulture,
                    out var ownerRange) || ownerRange < 0)
            {
                throw new InvalidOperationException(
                    $"{where}: owner_range_wu '{row[16]}' is not a non-negative integer.");
            }

            // The mount table states range 0 with a dismount rule, and the companion table
            // states a positive range with a teleport leash. Either pairing flipping is a
            // behaviour change, not a typo.
            if (isCompanion ? ownerRange == 0 : ownerRange != 0)
            {
                throw new InvalidOperationException(
                    $"{where}: owner_range_wu {ownerRange} contradicts the {row[2]} leash.");
            }

            if (!string.Equals(row[17], isCompanion ? CompanionLeash : MountLeash,
                    StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{where}: leash_behavior '{row[17]}' is not the sourced {row[2]} leash.");
            }

            if (!int.TryParse(row[19], NumberStyles.Integer, CultureInfo.InvariantCulture,
                    out var feedHours) || feedHours < 0)
            {
                throw new InvalidOperationException(
                    $"{where}: feed_cooldown_hours '{row[19]}' is not a non-negative integer.");
            }

            if (isCompanion ? (!row[18].StartsWith("PET-FEED-", StringComparison.Ordinal) ||
                               feedHours < 1) : row[18].Length > 0 || feedHours != 0)
            {
                throw new InvalidOperationException(
                    $"{where}: feed columns '{row[18]}'/'{row[19]}' contradict {row[2]}.");
            }

            // Both types state feeding as cosmetic-only. A row that names a stat would be
            // an item that changes combat power through a table no route reads.
            if (!row[20].Contains("cosmetic", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException(
                    $"{where}: feed_stat '{row[20]}' grants something other than cosmetics.");
            }

            if (!row[22].StartsWith("RIG_", StringComparison.Ordinal) || !rigs.Add(row[22]))
            {
                throw new InvalidOperationException(
                    $"{where}: rig_id '{row[22]}' is missing or reused.");
            }

            rows.Add(new CompanionEntry(
                row[0], row[1], row[2], row[3], row[4], row[5], levelCap, row[7],
                row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                ownerRange, row[17], row[18], feedHours, row[20], row[22]));
        }

        if (rows.Count(row => row.IsCompanion) == 0 || rows.Count(row => !row.IsCompanion) == 0)
        {
            throw new InvalidOperationException(
                $"{path}: expected both companion and mount rows.");
        }

        return rows;
    }

    private static readonly System.Text.RegularExpressions.Regex SkillUnlockLevels =
        new(@"^\d+(;\d+)*$", System.Text.RegularExpressions.RegexOptions.Compiled);
}
