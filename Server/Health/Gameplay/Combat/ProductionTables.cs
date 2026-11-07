using System.Globalization;

namespace Server.Health.Gameplay.Combat;

// Two production tables the shipped source set contains and this server had never read.
// Both are pure data today: nothing here changes a damage number or a route. The point of
// loading them is that a discrepancy against what the runtime *does* use becomes a CI
// failure with named numbers instead of a claim in a report.

public sealed record MobEliteVariant(
    string EntityId,
    string BaseEntityId,
    string VariantProfileId,
    double HpMultiplier,
    double DamageMultiplier,
    double MoveSpeedMultiplier,
    int LevelDelta,
    string BehaviorOverride,
    string LootTableId,
    string LootDelta,
    int RespawnDeltaSeconds,
    bool PvpAllowed);

public static class MobEliteVariantCatalog
{
    public const string RelativePath = "docs/production/Elite_Variant_Data_vi.csv";

    private static readonly string[] ExpectedHeader =
    [
        "entity_id", "base_entity_id", "base_prefab_id", "variant_profile_id",
        "hp_multiplier", "damage_multiplier", "move_speed_multiplier", "level_delta",
        "behavior_override", "telegraph_color_rule", "loot_table_id", "loot_delta",
        "respawn_delta_seconds", "art_delta", "pvp_allowed"
    ];

    // The three profiles the shipped table uses. Each one is a distinct multiplier set, so
    // a "uniform elite multiplier" cannot be derived from this source.
    private static readonly HashSet<string> KnownProfiles = new(StringComparer.Ordinal)
    {
        "elite_v1", "elite_v2", "elite_v3"
    };

    public static IReadOnlyList<MobEliteVariant> Load(string directory)
    {
        var path = Path.Combine(directory, RelativePath);
        var lines = File.ReadAllLines(path);
        if (lines.Length == 0)
        {
            throw new InvalidOperationException($"{path}: empty.");
        }

        var header = SplitCsvLine(lines[0]);
        if (!header.SequenceEqual(ExpectedHeader, StringComparer.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: header changed from the approved 15 columns.");
        }

        var rows = new List<MobEliteVariant>();
        for (var index = 1; index < lines.Length; index++)
        {
            if (string.IsNullOrWhiteSpace(lines[index]))
            {
                continue;
            }

            var cells = SplitCsvLine(lines[index]);
            var row = cells.Count >= ExpectedHeader.Length
                ? cells.GetRange(0, ExpectedHeader.Length)
                : cells.Concat(Enumerable.Repeat("", ExpectedHeader.Length - cells.Count)).ToList();
            var where = $"{path} line {index + 1}";

            var entityId = row[0];
            var baseEntityId = row[1];
            if (!entityId.StartsWith("MOB_", StringComparison.Ordinal) ||
                !entityId.EndsWith("_ELITE", StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{where}: elite entity id '{entityId}' is not MOB_*_ELITE.");
            }

            if (!string.Equals(entityId, baseEntityId + "_ELITE", StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{where}: {entityId} names base '{baseEntityId}', which cannot form it.");
            }

            if (!KnownProfiles.Contains(row[3]))
            {
                throw new InvalidOperationException(
                    $"{where}: unknown variant profile '{row[3]}'.");
            }

            var hp = ParseMultiplier(row[4], "hp_multiplier", where);
            var damage = ParseMultiplier(row[5], "damage_multiplier", where);
            var speed = ParseMultiplier(row[6], "move_speed_multiplier", where);
            if (!int.TryParse(row[7], NumberStyles.Integer, CultureInfo.InvariantCulture, out var levelDelta) ||
                levelDelta < 0)
            {
                throw new InvalidOperationException(
                    $"{where}: level_delta '{row[7]}' is not a non-negative integer.");
            }

            if (!bool.TryParse(row[14], out var pvpAllowed))
            {
                throw new InvalidOperationException(
                    $"{where}: pvp_allowed '{row[14]}' is not true/false.");
            }

            if (!int.TryParse(row[12], NumberStyles.Integer, CultureInfo.InvariantCulture,
                    out var respawnDelta) || respawnDelta < 0)
            {
                throw new InvalidOperationException(
                    $"{where}: respawn_delta_seconds '{row[12]}' is not a non-negative integer.");
            }

            if (row[10].Length == 0 || !row[10].StartsWith("LT_", StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{where}: loot_table_id '{row[10]}' is not an LT_ id.");
            }

            rows.Add(new MobEliteVariant(
                entityId, baseEntityId, row[3], hp, damage, speed, levelDelta,
                row[8], row[10], row[11], respawnDelta, pvpAllowed));
        }

        if (rows.Count == 0)
        {
            throw new InvalidOperationException($"{path}: no elite variant rows parsed.");
        }

        return rows;
    }

    private static double ParseMultiplier(string cell, string column, string where) =>
        double.TryParse(cell, NumberStyles.Float, CultureInfo.InvariantCulture, out var value) &&
        value > 0 && double.IsFinite(value)
            ? value
            : throw new InvalidOperationException(
                $"{where}: {column} '{cell}' is not a positive finite number.");

    internal static List<string> SplitCsvLine(string line)
    {
        var cells = new List<string>();
        var current = new System.Text.StringBuilder();
        var quoted = false;
        for (var index = 0; index < line.Length; index++)
        {
            var character = line[index];
            if (character == '"')
            {
                if (quoted && index + 1 < line.Length && line[index + 1] == '"')
                {
                    current.Append('"');
                    index++;
                }
                else
                {
                    quoted = !quoted;
                }

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

public sealed record NpcActorDefinition(
    string NpcId,
    string DisplayNameVi,
    string RoleProfile,
    string InteractionServiceId,
    string DialogueBankId,
    string VoiceBankId,
    bool CombatTargetable,
    string SourceMapId);

public static class NpcActorRegistry
{
    public const string RelativePath = "docs/production/NPC_Actor_Production_Registry_vi.csv";

    private static readonly string[] ExpectedHeader =
    [
        "npc_id", "display_name_vi", "role_profile", "base_prefab_id", "rig_id",
        "animation_set_id", "costume_set_id", "palette_id", "visual_delta", "unique_face",
        "portrait_asset_id", "dialogue_bank_id", "voice_bank_id", "interaction_service_id",
        "combat_targetable", "default_scale", "collision_profile", "art_state",
        "source_map_id"
    ];

    private static readonly HashSet<string> KnownRoles = new(StringComparer.Ordinal)
    {
        "QUEST_GIVER", "QUEST_ACTOR", "SERVICE", "GUARD", "CIVILIAN", "WORKER", "SECT_MASTER"
    };

    public static IReadOnlyList<NpcActorDefinition> Load(string directory)
    {
        var path = Path.Combine(directory, RelativePath);
        var lines = File.ReadAllLines(path);
        var header = SplitCsvLines(lines[0]);
        if (!header.SequenceEqual(ExpectedHeader, StringComparer.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: header changed from the approved 19 columns.");
        }

        var rows = new List<NpcActorDefinition>();
        for (var index = 1; index < lines.Length; index++)
        {
            if (string.IsNullOrWhiteSpace(lines[index]))
            {
                continue;
            }

            var cells = SplitCsvLines(lines[index]);
            var row = cells.Count >= ExpectedHeader.Length
                ? cells.GetRange(0, ExpectedHeader.Length)
                : cells.Concat(Enumerable.Repeat("", ExpectedHeader.Length - cells.Count)).ToList();
            var where = $"{path} line {index + 1}";

            var npcId = row[0];
            if (!npcId.StartsWith("NPC_", StringComparison.Ordinal))
            {
                throw new InvalidOperationException($"{where}: npc id '{npcId}' is not NPC_*.");
            }

            if (!KnownRoles.Contains(row[2]))
            {
                throw new InvalidOperationException($"{where}: unknown role profile '{row[2]}'.");
            }

            if (!bool.TryParse(row[14], out var combatTargetable))
            {
                throw new InvalidOperationException(
                    $"{where}: combat_targetable '{row[14]}' is not true/false.");
            }

            // `WorldAoiProjection` publishes every NPC as INVULNERABLE / not targetable,
            // and the cast path refuses a NPC target on purpose. A row that says an actor
            // is a combat target is a contradiction the server cannot represent, so it
            // fails here rather than becoming the #96 shape: an advertised target nothing
            // can resolve.
            if (combatTargetable)
            {
                throw new InvalidOperationException(
                    $"{where}: {npcId} is combat_targetable=true, which the audience " +
                    "policy (NPC = INVULNERABLE, never targetable) cannot express.");
            }

            if (row[13].Length == 0 ||
                !(row[13].StartsWith("SERVICE", StringComparison.Ordinal) ||
                  string.Equals(row[13], "NONE", StringComparison.Ordinal)))
            {
                throw new InvalidOperationException(
                    $"{where}: interaction_service_id '{row[13]}' is neither NONE nor a " +
                    "SERVICE_* token.");
            }

            rows.Add(new NpcActorDefinition(
                npcId, row[1], row[2], row[13], row[11], row[12],
                combatTargetable, row[18]));
        }

        return rows;
    }

    private static List<string> SplitCsvLines(string line) =>
        MobEliteVariantCatalog.SplitCsvLine(line);
}

// Both tables live in the same docs/production folder as every other approved data
// bundle, so one discovery walk serves them instead of a third copy of the search.
public static class ProductionTableDiscovery
{
    public static string DiscoverDirectory(string contentRoot, string relativePath)
    {
        var starts = new[] { contentRoot, Directory.GetCurrentDirectory(), AppContext.BaseDirectory }
            .Where(path => !string.IsNullOrWhiteSpace(path))
            .Distinct(StringComparer.OrdinalIgnoreCase);

        foreach (var start in starts)
        {
            DirectoryInfo? directory = new(Path.GetFullPath(start));
            for (var depth = 0; depth < 12 && directory is not null; depth++)
            {
                if (File.Exists(Path.Combine(directory.FullName, relativePath)))
                {
                    return directory.FullName;
                }

                directory = directory.Parent;
            }
        }

        throw new FileNotFoundException($"Could not locate {relativePath}. Run from the repository.");
    }
}
