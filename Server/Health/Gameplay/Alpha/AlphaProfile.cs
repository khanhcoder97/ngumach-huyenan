using System.Text.Json;
using Microsoft.Extensions.Configuration;
using Server.Health.World;

namespace Server.Health.Gameplay.Alpha;

// QOD-21 Q1: the approved private-alpha design (DESIGN-BM-ALPHA-20261103) is
// machine-readable content, so the server parses and validates it instead of
// hardcoding a copy. This type is the ingest seam: every later alpha runtime
// (overlay world records, quest pack, boss encounter, v2 inventory, loot and
// death-return) reads these values rather than inventing its own.
//
// Default behaviour is unchanged: the profile is validated at startup and the
// gate is OFF. Only an explicitly enabled private profile may consume it.
public sealed record AlphaProfileOptions
{
    public const string SectionName = "P1:AlphaProfile";

    public bool Enabled { get; set; }
}

public sealed record AlphaPoint(double X, double Y);

public sealed record AlphaScope(
    IReadOnlyList<string> ClassIds,
    string MapId,
    bool WorldBossEnabled,
    bool CanonicalPlacementCsvEdited,
    bool TopologyReviewed,
    bool RequiresExplicitPrivateProfile);

public sealed record AlphaOverlayRecord(
    string RecordId,
    string EntityId,
    string Kind,
    double X,
    double Y,
    string QuestId,
    int? CountPerCharacter,
    string? Condition);

public sealed record AlphaInventoryRules(
    int BagSlots,
    IReadOnlyList<string> EquipmentSlots,
    bool AutoSwap,
    string Revision,
    string MaxResourceChange,
    string WireMigration,
    string ReadRoute,
    string EquipRoute,
    string UnequipRoute,
    int SchemaVersion);

public sealed record AlphaProgressionRules(
    bool AcceptSnapshot,
    int NormalQuestXpNumerator,
    int BossQuestXpNumerator,
    int Denominator,
    string XpToNext,
    bool AbsoluteSourceRewardWins,
    string MobXp,
    string Migration);

public sealed record AlphaBossMove(
    string Id,
    string NameVi,
    string Shape,
    double WindupSeconds,
    double Coefficient,
    double RecoverySeconds,
    double CooldownSeconds,
    string TargetLock,
    string InterruptibleBy,
    double? AngleDegrees,
    double? RangeWu,
    double? RadiusWu,
    double? TargetRangeWu,
    double? InnerRadiusWu,
    double? OuterRadiusWu,
    bool Dodgeable,
    bool SubmergeIsCosmetic);

public sealed record AlphaBossRules(
    string ProfileId,
    string EntityId,
    int Level,
    int MaxHp,
    int Attack,
    int Armor,
    string ArenaShape,
    double CenterX,
    double CenterY,
    double RadiusWu,
    IReadOnlyList<AlphaPoint> SafePads,
    double SafePadRadiusWu,
    bool SafePadsPhase3Only,
    double Phase2Threshold,
    double Phase3Threshold,
    int MaxTransitionsPerImpact,
    double PhaseGuardSeconds,
    double Phase2RecoveryMultiplier,
    double Phase3AdditionalDamageMultiplier,
    IReadOnlyList<string> Priority,
    bool OverlapAllowed,
    IReadOnlyList<AlphaBossMove> Moves,
    double WipeNoAliveTargetSeconds,
    bool ResetHp,
    int ResetPhase,
    bool QuestCheckpointPersists,
    bool InvalidateOldCastGeneration,
    bool NoLootOnReset);

public sealed record AlphaLootRules(
    string CoinMinExpression,
    string CoinMaxExpression,
    bool InclusiveIntegers,
    IReadOnlyDictionary<string, int> GearRarityWeights,
    string EligibleGear,
    IReadOnlyList<string> RollOnceKey,
    bool NoLiveRerollOnRetry,
    bool DefaultGrantEnabled,
    bool BossQuestRewardSeparateFromLoot);

public sealed record AlphaDeathReturnRules(
    string MapId,
    double AnchorX,
    double AnchorY,
    string Route,
    int SchemaVersion,
    string Payload,
    string RestoreHp,
    string RestoreMp,
    int XpPenalty,
    int CurrencyPenalty,
    int DurabilityPenalty,
    int NewDeathReturnCooldownSeconds,
    IReadOnlyList<string> Clear,
    IReadOnlyList<string> CreditKey,
    bool DefaultEnabled);

public sealed record AlphaWaveRule(string RecordId, string MobId, int Count);

public sealed record AlphaQuestRules(
    string P00_02_TurnInNpcId,
    int P00_02_RipplesRequired,
    int P00_02_CarplingKillsRequired,
    string P00_02_SharePolicy,
    int P00_02_InteractionRangeWu,
    string P00_03_TurnInNpcId,
    int P00_03_VillagersRequired,
    int P00_03_WaterrootKillsRequired,
    AlphaPoint P00_03_WaveMin,
    AlphaPoint P00_03_WaveMax,
    double P00_03_WaveWindupSeconds,
    double P00_03_WaveRepeatCooldownSeconds,
    int P00_03_WaveRawDamage,
    string P00_04_TurnInNpcId,
    string P00_04_ActorId,
    double P00_04_SpeedWuPerSecond,
    double P00_04_FollowRangeWu,
    IReadOnlyList<int> P00_04_CheckpointXs,
    IReadOnlyList<AlphaPoint> P00_04_Waypoints,
    AlphaWaveRule P00_04_WaveA,
    AlphaWaveRule P00_04_WaveB,
    IReadOnlyList<string> P00_04_CreditKey,
    string P00_05_TurnInNpcId,
    string P00_05_BossRecordId,
    string P00_05_WorldEventRecordIdDisabled,
    string P00_05_PhaseNpcId,
    double P00_05_PhaseNpcX,
    double P00_05_PhaseNpcY,
    IReadOnlyList<string> P00_05_OrderedObjectives,
    string P00_05_UnlockText,
    string P00_05_TrialNpcConditionOverride,
    int C1_01_MinLevel,
    string C1_01_StartNpcId,
    string C1_01_TurnInNpcId,
    string C1_01_MapId,
    IReadOnlyList<string> C1_01_PrerequisiteQuestIds,
    IReadOnlyList<string> C1_01_Representatives,
    string C1_01_TrialRegistrationNpcId,
    string C1_01_CurrencyId,
    long C1_01_CurrencyAmount,
    bool C1_01_NoLevelBypass);

public sealed record AlphaDesign(
    int SchemaVersion,
    string DecisionId,
    string Status,
    bool DefaultEnabled,
    AlphaScope Scope,
    IReadOnlyList<string> Sources,
    AlphaInventoryRules Inventory,
    AlphaProgressionRules Progression,
    IReadOnlyList<AlphaOverlayRecord> OverlayRecords,
    AlphaQuestRules QuestRules,
    AlphaBossRules Boss,
    AlphaLootRules Loot,
    AlphaDeathReturnRules DeathReturn,
    bool ProductionGatesRemainOff,
    bool DevProfileMustBeExplicit,
    bool NoReadDialogueReward,
    bool NoDuplicateBoss,
    bool FullBagKeepsReady,
    bool UnknownFieldMustFailExport,
    bool NoTopologySelfCertification);

public sealed class AlphaProfileLoader
{
    public const string RelativePath =
        "Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json";

    public static string Discover(
        IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:AlphaProfilePath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:AlphaProfilePath points to '{resolved}', which does not exist.");
            }

            return resolved;
        }

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

    public static AlphaDesign Load(string path)
    {
        using var document = JsonDocument.Parse(
            File.ReadAllText(path),
            new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip });
        var root = document.RootElement;
        var acceptance = RequireObject(root, "acceptance", path);
        var acceptancePath = $"{path}.acceptance";
        return new AlphaDesign(
            RequireInt(root, "schemaVersion", path),
            RequireString(root, "decisionId", path),
            RequireString(root, "status", path),
            RequireBool(root, "defaultEnabled", path),
            ParseScope(RequireObject(root, "scope", path), $"{path}.scope"),
            RequireStringArray(root, "sources", path),
            ParseInventory(RequireObject(root, "inventory", path), $"{path}.inventory"),
            ParseProgression(
                RequireObject(root, "progression", path), $"{path}.progression"),
            ParseOverlay(
                RequireArray(root, "newOverlayRecords", path),
                $"{path}.newOverlayRecords"),
            ParseQuestRules(
                RequireObject(root, "questRules", path), $"{path}.questRules"),
            ParseBoss(RequireObject(root, "boss", path), $"{path}.boss"),
            ParseLoot(RequireObject(root, "lootAlphaOnly", path), $"{path}.lootAlphaOnly"),
            ParseDeathReturn(
                RequireObject(root, "deathReturn", path), $"{path}.deathReturn"),
            RequireBool(acceptance, "productionGatesRemainOff", acceptancePath),
            RequireBool(acceptance, "devProfileMustBeExplicit", acceptancePath),
            RequireBool(acceptance, "noReadDialogueReward", acceptancePath),
            RequireBool(acceptance, "noDuplicateBoss", acceptancePath),
            RequireBool(acceptance, "fullBagKeepsReady", acceptancePath),
            RequireBool(acceptance, "unknownFieldMustFailExport", acceptancePath),
            RequireBool(acceptance, "noTopologySelfCertification", acceptancePath));
    }

    private static AlphaScope ParseScope(JsonElement element, string path) =>
        new(
            RequireStringArray(element, "classIds", path),
            RequireString(element, "mapId", path),
            RequireBool(element, "worldBossEnabled", path),
            RequireBool(element, "canonicalPlacementCsvEdited", path),
            RequireBool(element, "topologyReviewed", path),
            RequireBool(element, "requiresExplicitPrivateProfile", path));

    private static AlphaInventoryRules ParseInventory(JsonElement element, string path)
    {
        var routes = RequireObject(element, "routes", path);
        return new AlphaInventoryRules(
            RequireInt(element, "bagSlots", path),
            RequireStringArray(element, "equipmentSlots", path),
            RequireBool(element, "autoSwap", path),
            RequireString(element, "revision", path),
            RequireString(element, "maxResourceChange", path),
            RequireString(element, "wireMigration", path),
            RequireString(routes, "read", $"{path}.routes"),
            RequireString(routes, "equip", $"{path}.routes"),
            RequireString(routes, "unequip", $"{path}.routes"),
            RequireInt(element, "schemaVersion", path));
    }

    private static AlphaProgressionRules ParseProgression(JsonElement element, string path) =>
        new(
            RequireBool(element, "acceptSnapshot", path),
            RequireInt(element, "normalQuestXpNumerator", path),
            RequireInt(element, "bossQuestXpNumerator", path),
            RequireInt(element, "denominator", path),
            RequireString(element, "xpToNext", path),
            RequireBool(element, "absoluteSourceRewardWins", path),
            RequireString(element, "mobXp", path),
            RequireString(element, "migration", path));

    private static IReadOnlyList<AlphaOverlayRecord> ParseOverlay(
        JsonElement element, string path)
    {
        var records = new List<AlphaOverlayRecord>();
        var index = 0;
        foreach (var item in element.EnumerateArray())
        {
            var itemPath = $"{path}[{index++}]";
            records.Add(new AlphaOverlayRecord(
                RequireString(item, "recordId", itemPath),
                RequireString(item, "entityId", itemPath),
                RequireString(item, "kind", itemPath),
                RequireNumber(item, "xWu", itemPath),
                RequireNumber(item, "yWu", itemPath),
                RequireString(item, "questId", itemPath),
                OptionalInt(item, "countPerCharacter"),
                OptionalString(item, "condition")));
        }

        return records;
    }

    private static AlphaQuestRules ParseQuestRules(JsonElement element, string path)
    {
        var p2 = RequireObject(element, "P00-02", path);
        var p2Path = $"{path}.P00-02";
        var p3 = RequireObject(element, "P00-03", path);
        var p3Path = $"{path}.P00-03";
        var trial = RequireObject(p3, "waveTrial", p3Path);
        var trialPath = $"{p3Path}.waveTrial";
        var rectangle = RequireObject(trial, "rectangleWu", trialPath);
        var rectanglePath = $"{trialPath}.rectangleWu";
        var p4 = RequireObject(element, "P00-04", path);
        var p4Path = $"{path}.P00-04";
        var waveA = RequireObject(p4, "waveA", p4Path);
        var waveB = RequireObject(p4, "waveB", p4Path);
        var waveAPath = $"{p4Path}.waveA";
        var waveBPath = $"{p4Path}.waveB";
        var p5 = RequireObject(element, "P00-05", path);
        var p5Path = $"{path}.P00-05";
        var phaseNpc = RequireObject(p5, "phaseNpcOverride", p5Path);
        var phaseNpcPath = $"{p5Path}.phaseNpcOverride";
        var c1 = RequireObject(element, "C1-01", path);
        var c1Path = $"{path}.C1-01";
        var currency = RequireObject(c1, "currencyReward", c1Path);
        var currencyPath = $"{c1Path}.currencyReward";

        return new AlphaQuestRules(
            RequireString(p2, "turnInNpcId", p2Path),
            RequireInt(p2, "ripplesRequired", p2Path),
            RequireInt(p2, "carplingKillsRequired", p2Path),
            RequireString(p2, "sharePolicy", p2Path),
            RequireInt(p2, "interactionRangeWu", p2Path),
            RequireString(p3, "turnInNpcId", p3Path),
            RequireInt(p3, "villagersRequired", p3Path),
            RequireInt(p3, "waterrootKillsRequired", p3Path),
            new AlphaPoint(
                RequireNumber(rectangle, "minX", rectanglePath),
                RequireNumber(rectangle, "minY", rectanglePath)),
            new AlphaPoint(
                RequireNumber(rectangle, "maxX", rectanglePath),
                RequireNumber(rectangle, "maxY", rectanglePath)),
            RequireNumber(trial, "windupSeconds", trialPath),
            RequireNumber(trial, "repeatCooldownSeconds", trialPath),
            RequireInt(trial, "rawDamage", trialPath),
            RequireString(p4, "turnInNpcId", p4Path),
            RequireString(p4, "actorId", p4Path),
            RequireNumber(p4, "speedWuPerSecond", p4Path),
            RequireNumber(p4, "followRangeWu", p4Path),
            RequireIntArray(p4, "checkpointXs", p4Path),
            ParsePoints(RequireArray(p4, "waypointsWu", p4Path), $"{p4Path}.waypointsWu"),
            new AlphaWaveRule(
                RequireString(waveA, "recordId", waveAPath),
                RequireString(waveA, "mobId", waveAPath),
                RequireInt(waveA, "count", waveAPath)),
            new AlphaWaveRule(
                RequireString(waveB, "recordId", waveBPath),
                RequireString(waveB, "mobId", waveBPath),
                RequireInt(waveB, "count", waveBPath)),
            RequireStringArray(p4, "creditKey", p4Path),
            RequireString(p5, "turnInNpcId", p5Path),
            RequireString(p5, "bossRecordId", p5Path),
            RequireString(p5, "worldEventRecordIdDisabledInQuestInstance", p5Path),
            RequireString(phaseNpc, "entityId", phaseNpcPath),
            RequireNumber(phaseNpc, "xWu", phaseNpcPath),
            RequireNumber(phaseNpc, "yWu", phaseNpcPath),
            RequireStringArray(p5, "orderedObjectives", p5Path),
            RequireString(p5, "unlock", p5Path),
            RequireString(p5, "trialNpcConditionOverride", p5Path),
            RequireInt(c1, "minLevel", c1Path),
            RequireString(c1, "startNpcId", c1Path),
            RequireString(c1, "turnInNpcId", c1Path),
            RequireString(c1, "mapId", c1Path),
            RequireStringArray(c1, "prerequisiteQuestIds", c1Path),
            RequireStringArray(c1, "representatives", c1Path),
            RequireString(c1, "trialRegistrationNpcId", c1Path),
            RequireString(currency, "currencyId", currencyPath),
            RequireLong(currency, "amount", currencyPath),
            RequireBool(c1, "noLevelBypass", c1Path));
    }

    private static AlphaBossRules ParseBoss(JsonElement element, string path)
    {
        var arena = RequireObject(element, "arena", path);
        var arenaPath = $"{path}.arena";
        var center = RequireArray(arena, "centerWu", arenaPath);
        var centerPath = $"{arenaPath}.centerWu";
        var pads = RequireObject(element, "safePads", path);
        var padsPath = $"{path}.safePads";
        var phases = RequireObject(element, "phases", path);
        var phasesPath = $"{path}.phases";
        var thresholds = RequireArray(phases, "thresholds", phasesPath);
        var moves = new List<AlphaBossMove>();
        var moveIndex = 0;
        foreach (var move in RequireArray(element, "moves", path).EnumerateArray())
        {
            var movePath = $"{path}.moves[{moveIndex++}]";
            moves.Add(new AlphaBossMove(
                RequireString(move, "id", movePath),
                RequireString(move, "nameVi", movePath),
                RequireString(move, "shape", movePath),
                RequireNumber(move, "windupSeconds", movePath),
                RequireNumber(move, "coefficient", movePath),
                RequireNumber(move, "recoverySeconds", movePath),
                RequireNumber(move, "cooldownSeconds", movePath),
                RequireString(move, "targetLock", movePath),
                RequireString(move, "interruptibleBy", movePath),
                OptionalNumber(move, "angleDegrees"),
                OptionalNumber(move, "rangeWu"),
                OptionalNumber(move, "radiusWu"),
                OptionalNumber(move, "targetRangeWu"),
                OptionalNumber(move, "innerRadiusWu"),
                OptionalNumber(move, "outerRadiusWu"),
                OptionalBool(move, "dodgeable"),
                OptionalBool(move, "submergeIsCosmeticNotImplicitInvulnerability")));
        }

        var wipe = RequireObject(element, "wipe", path);
        var wipePath = $"{path}.wipe";
        return new AlphaBossRules(
            RequireString(element, "profileId", path),
            RequireString(element, "entityId", path),
            RequireInt(element, "level", path),
            RequireInt(element, "maxHp", path),
            RequireInt(element, "attack", path),
            RequireInt(element, "armor", path),
            RequireString(arena, "shape", arenaPath),
            NumberAt(center, 0, centerPath),
            NumberAt(center, 1, centerPath),
            RequireNumber(arena, "radiusWu", arenaPath),
            ParsePoints(RequireArray(pads, "centersWu", padsPath), $"{padsPath}.centersWu"),
            RequireNumber(pads, "radiusWu", padsPath),
            RequireBool(pads, "phase3Only", padsPath),
            NumberAt(thresholds, 0, $"{phasesPath}.thresholds"),
            NumberAt(thresholds, 1, $"{phasesPath}.thresholds"),
            RequireInt(phases, "maxTransitionsPerImpact", phasesPath),
            RequireNumber(phases, "phaseGuardSeconds", phasesPath),
            RequireNumber(phases, "phase2RecoveryMultiplier", phasesPath),
            RequireNumber(phases, "phase3AdditionalDamageMultiplier", phasesPath),
            RequireStringArray(element, "priority", path),
            RequireBool(element, "overlapAllowed", path),
            moves,
            RequireNumber(wipe, "noAliveTargetSeconds", wipePath),
            RequireBool(wipe, "resetHp", wipePath),
            RequireInt(wipe, "resetPhase", wipePath),
            RequireBool(wipe, "questCheckpointPersists", wipePath),
            RequireBool(wipe, "invalidateOldCastGeneration", wipePath),
            RequireBool(wipe, "noLootOnReset", wipePath));
    }

    private static AlphaLootRules ParseLoot(JsonElement element, string path)
    {
        var weights = new Dictionary<string, int>(StringComparer.Ordinal);
        foreach (var property in RequireObject(element, "gearRarityWeights", path)
                     .EnumerateObject())
        {
            weights[property.Name] = property.Value.GetInt32();
        }

        return new AlphaLootRules(
            RequireString(element, "coinMin", path),
            RequireString(element, "coinMax", path),
            RequireBool(element, "inclusiveIntegers", path),
            weights,
            RequireString(element, "eligibleGear", path),
            RequireStringArray(element, "rollOnceKey", path),
            RequireBool(element, "noLiveRerollOnRetry", path),
            RequireBool(element, "defaultGrantEnabled", path),
            RequireBool(element, "bossQuestRewardSeparateFromLoot", path));
    }

    private static AlphaDeathReturnRules ParseDeathReturn(JsonElement element, string path)
    {
        var anchor = RequireArray(element, "safeAnchorWu", path);
        var anchorPath = $"{path}.safeAnchorWu";
        return new AlphaDeathReturnRules(
            RequireString(element, "mapId", path),
            NumberAt(anchor, 0, anchorPath),
            NumberAt(anchor, 1, anchorPath),
            RequireString(element, "route", path),
            RequireInt(element, "schemaVersion", path),
            RequireString(element, "payload", path),
            RequireString(element, "restoreHp", path),
            RequireString(element, "restoreMp", path),
            RequireInt(element, "xpPenalty", path),
            RequireInt(element, "currencyPenalty", path),
            RequireInt(element, "durabilityPenalty", path),
            RequireInt(element, "newDeathReturnCooldownSeconds", path),
            RequireStringArray(element, "clear", path),
            RequireStringArray(element, "creditKey", path),
            RequireBool(element, "defaultEnabled", path));
    }

    private static IReadOnlyList<AlphaPoint> ParsePoints(
        JsonElement array, string path)
    {
        var points = new List<AlphaPoint>();
        var index = 0;
        foreach (var item in array.EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.Array || item.GetArrayLength() != 2)
            {
                throw new InvalidOperationException(
                    $"{path}[{index}]: expected a two-number array.");
            }

            points.Add(new AlphaPoint(
                item[0].GetDouble(), item[1].GetDouble()));
            index++;
        }

        return points;
    }

    private static JsonElement RequireObject(JsonElement parent, string name, string path) =>
        Require(parent, name, path, JsonValueKind.Object);

    private static JsonElement RequireArray(JsonElement parent, string name, string path) =>
        Require(parent, name, path, JsonValueKind.Array);

    private static JsonElement Require(
        JsonElement parent, string name, string path, JsonValueKind kind)
    {
        if (!parent.TryGetProperty(name, out var value) || value.ValueKind != kind)
        {
            throw new InvalidOperationException($"{path}.{name}: missing or not {kind}.");
        }

        return value;
    }

    private static string RequireString(JsonElement parent, string name, string path)
    {
        var value = Require(parent, name, path, JsonValueKind.String).GetString();
        return value ?? throw new InvalidOperationException($"{path}.{name}: null string.");
    }

    private static string? OptionalString(JsonElement parent, string name) =>
        parent.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;

    private static int RequireInt(JsonElement parent, string name, string path)
    {
        var value = Require(parent, name, path, JsonValueKind.Number);
        if (!value.TryGetInt32(out var number))
        {
            throw new InvalidOperationException($"{path}.{name}: not an int32.");
        }

        return number;
    }

    private static long RequireLong(JsonElement parent, string name, string path)
    {
        var value = Require(parent, name, path, JsonValueKind.Number);
        if (!value.TryGetInt64(out var number))
        {
            throw new InvalidOperationException($"{path}.{name}: not an int64.");
        }

        return number;
    }

    private static int? OptionalInt(JsonElement parent, string name) =>
        parent.TryGetProperty(name, out var value) &&
        value.ValueKind == JsonValueKind.Number &&
        value.TryGetInt32(out var number)
            ? number
            : null;

    private static double RequireNumber(JsonElement parent, string name, string path)
    {
        var value = Require(parent, name, path, JsonValueKind.Number);
        return value.GetDouble();
    }

    private static double? OptionalNumber(JsonElement parent, string name) =>
        parent.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.Number
            ? value.GetDouble()
            : null;

    private static bool OptionalBool(JsonElement parent, string name) =>
        parent.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.True;

    private static double NumberAt(JsonElement array, int index, string path)
    {
        if (index >= array.GetArrayLength() ||
            array[index].ValueKind != JsonValueKind.Number)
        {
            throw new InvalidOperationException($"{path}[{index}]: missing number.");
        }

        return array[index].GetDouble();
    }

    private static bool RequireBool(JsonElement parent, string name, string path)
    {
        if (!parent.TryGetProperty(name, out var value) ||
            value.ValueKind is not (JsonValueKind.True or JsonValueKind.False))
        {
            throw new InvalidOperationException($"{path}.{name}: missing or not boolean.");
        }

        return value.GetBoolean();
    }

    private static IReadOnlyList<string> RequireStringArray(
        JsonElement parent, string name, string path)
    {
        var items = new List<string>();
        foreach (var item in RequireArray(parent, name, path).EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.String)
            {
                throw new InvalidOperationException($"{path}.{name}: non-string item.");
            }

            items.Add(item.GetString()!);
        }

        return items;
    }

    private static IReadOnlyList<int> RequireIntArray(
        JsonElement parent, string name, string path)
    {
        var items = new List<int>();
        foreach (var item in RequireArray(parent, name, path).EnumerateArray())
        {
            if (!item.TryGetInt32(out var number))
            {
                throw new InvalidOperationException($"{path}.{name}: non-int item.");
            }

            items.Add(number);
        }

        return items;
    }
}
