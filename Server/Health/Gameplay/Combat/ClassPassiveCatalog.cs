using System.Globalization;

namespace Server.Health.Gameplay.Combat;

// Work order 29 Q4 names "passive" as part of the five-class coverage, and
// docs/production/Class_Passive_Production_Data_vi.csv is the only machine-readable
// source for it: 40 rows, five classes x two branches x four tiers, every row carrying
// an effect key, a value, a unit and a PvP/boss cap string. The server did not read
// this file at all before this loader existed (only validate_content.py checked that
// the columns parse), so a passive could be quoted from prose while the actual shipped
// numbers sat unused.
//
// Loading is not applying. Nothing here changes combat resolution, a snapshot, or the
// wire: the catalogue is inert data plus the structural checks below, so that the day a
// passive is implemented there is a validated source to read instead of a re-derivation
// from a spec sentence.
public enum PassiveCapKind
{
    PercentPvp,
    PercentBoss,
    PercentPvpBoss,
    ProcRate,
    HardCap,
    PveOnly,
    PvpZero,
    Unparsed
}

public sealed record PassiveCapToken(PassiveCapKind Kind, decimal Amount, string Raw);

public sealed record ClassPassiveDefinition(
    string PassiveId,
    string ClassId,
    string BranchId,
    int NodeTier,
    int UnlockLevel,
    string? PrerequisitePassiveId,
    string UnlockRule,
    string EffectKey,
    decimal EffectValue,
    string EffectUnit,
    IReadOnlyList<PassiveCapToken> Caps,
    IReadOnlyList<string> UnparsedCaps,
    string EquipChangePolicy,
    string Status);

public sealed class ClassPassiveCatalog(
    IReadOnlyDictionary<string, ClassPassiveDefinition> passives)
{
    private static readonly string[] ClassIds =
    [
        "CLASS_MINH_KIEM",
        "CLASS_ANH_DAO",
        "CLASS_HUYEN_BUT",
        "CLASS_THACH_CHUY",
        "CLASS_LINH_CUNG"
    ];

    private readonly IReadOnlyDictionary<string, ClassPassiveDefinition> _passives = passives;

    public int Count => _passives.Count;

    public IEnumerable<ClassPassiveDefinition> Rows => _passives.Values;

    public IReadOnlyList<string> SupportedClassIds => ClassIds;

    public bool TryGet(string passiveId, out ClassPassiveDefinition passive) =>
        _passives.TryGetValue(passiveId, out passive!);

    public int CountForClass(string classId) =>
        _passives.Values.Count(passive => string.Equals(passive.ClassId, classId, StringComparison.Ordinal));
}

public static class ClassPassiveCatalogLoader
{
    public const string RelativePath = "docs/production/Class_Passive_Production_Data_vi.csv";

    private const string ExpectedUnlockRule =
        "automatic at level gate after previous node in same branch";

    private const int LevelsPerTier = 20;

    private static readonly string[] ExpectedHeader =
    [
        "passive_id", "class_id", "class_name_vi", "branch_id", "branch_name_vi",
        "node_tier", "unlock_level", "prerequisite_passive_id", "unlock_rule",
        "display_name_vi", "description_vi", "effect_key", "effect_value", "effect_unit",
        "pvp_boss_cap", "equip_change_policy", "icon_key", "status"
    ];

    private static readonly string[] KnownUnits = ["percent", "seconds", "stack", "mp", "target"];

    private static readonly string[] KnownStatuses = ["BASELINE"];

    private static readonly System.Text.RegularExpressions.Regex PassiveIdPattern =
        new(@"^PAS-[A-Z][A-Z0-9_]*-[A-Z][A-Z0-9_]*-T[1-4]$",
            System.Text.RegularExpressions.RegexOptions.CultureInvariant);

    private static readonly System.Text.RegularExpressions.Regex EffectKeyPattern =
        new(@"^[a-z][a-z0-9_]*$", System.Text.RegularExpressions.RegexOptions.CultureInvariant);

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

        throw new FileNotFoundException(
            $"Could not locate {RelativePath}. Run from the repository.");
    }

    public static ClassPassiveCatalog Load(string docsDirectory)
    {
        var path = Path.Combine(docsDirectory, RelativePath);
        var lines = File.ReadAllLines(path);
        if (lines.Length < 2)
        {
            throw new InvalidOperationException($"{path}: passive catalog has no data rows.");
        }

        var header = ClassPassiveContract.SplitCsvLine(lines[0]);
        if (!header.SequenceEqual(ExpectedHeader, StringComparer.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: unexpected header. Expected {ExpectedHeader.Length} columns in the " +
                "published order: " + string.Join(",", ExpectedHeader));
        }

        var columnIndexes = new Dictionary<string, int>(StringComparer.Ordinal);
        for (var column = 0; column < header.Count; column++)
        {
            columnIndexes[header[column]] = column;
        }

        var passives = new Dictionary<string, ClassPassiveDefinition>(StringComparer.Ordinal);
        for (var index = 1; index < lines.Length; index++)
        {
            if (string.IsNullOrWhiteSpace(lines[index]))
            {
                continue;
            }

            var cells = ClassPassiveContract.SplitCsvLine(lines[index]);
            if (cells.Count != ExpectedHeader.Length)
            {
                throw new InvalidOperationException(
                    $"{path}:{index + 1}: expected {ExpectedHeader.Length} cells, found {cells.Count}.");
            }

            string? Cell(string column)
            {
                var raw = cells[columnIndexes[column]];
                return string.IsNullOrWhiteSpace(raw) ? null : raw.Trim();
            }

            var passiveId = Cell("passive_id");
            if (passiveId is null || !PassiveIdPattern.IsMatch(passiveId))
            {
                throw new InvalidOperationException($"{path}:{index + 1}: invalid passive_id '{passiveId}'.");
            }

            var classId = Cell("class_id");
            if (classId is null || !ClassPassiveContract.SupportedClassIds.Contains(classId))
            {
                throw new InvalidOperationException(
                    $"{path}:{index + 1}: passive '{passiveId}' names class '{classId}', which is not " +
                    "one of the five classes the catalog is scoped to.");
            }

            var branchId = Cell("branch_id");
            if (branchId is null || !ClassPassiveContract.IsBranch(branchId))
            {
                throw new InvalidOperationException($"{path}:{index + 1}: invalid branch_id '{branchId}'.");
            }

            if (!int.TryParse(Cell("node_tier"), out var tier) || tier is < 1 or > 4)
            {
                throw new InvalidOperationException($"{path}:{index + 1}: node_tier must be 1..4.");
            }

            if (!int.TryParse(Cell("unlock_level"), out var unlockLevel))
            {
                throw new InvalidOperationException($"{path}:{index + 1}: unlock_level must be an integer.");
            }

            // The shipped rows make the gate exactly 20 x tier. Asserting it turns a
            // coincidence in the current data into something a future edit cannot break
            // silently.
            if (unlockLevel != tier * LevelsPerTier)
            {
                throw new InvalidOperationException(
                    $"{path}:{index + 1}: unlock_level {unlockLevel} does not match tier {tier} " +
                    $"(expected {tier * LevelsPerTier}).");
            }

            var unlockRule = Cell("unlock_rule");
            if (unlockRule is null ||
                !string.Equals(unlockRule, ExpectedUnlockRule, StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{path}:{index + 1}: unlock_rule '{unlockRule}' is not the one rule the source " +
                    $"publishes ({ExpectedUnlockRule}).");
            }

            var prerequisite = Cell("prerequisite_passive_id");
            if (tier == 1
                    ? prerequisite is not null
                    : prerequisite is null ||
                      !passives.TryGetValue(prerequisite, out var parent) ||
                      !string.Equals(parent.ClassId, classId, StringComparison.Ordinal) ||
                      !string.Equals(parent.BranchId, branchId, StringComparison.Ordinal) ||
                      parent.NodeTier != tier - 1)
            {
                throw new InvalidOperationException(
                    $"{path}:{index + 1}: tier {tier} prerequisite '{prerequisite}' is not the " +
                    $"tier {tier - 1} node of the same class and branch.");
            }

            var effectKey = Cell("effect_key");
            if (effectKey is null || !EffectKeyPattern.IsMatch(effectKey))
            {
                throw new InvalidOperationException($"{path}:{index + 1}: invalid effect_key '{effectKey}'.");
            }

            var rawValue = Cell("effect_value");
            if (rawValue is null ||
                !decimal.TryParse(rawValue, NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture,
                    out var effectValue) ||
                effectValue < 0)
            {
                throw new InvalidOperationException(
                    $"{path}:{index + 1}: effect_value '{rawValue}' is not a non-negative number.");
            }

            var unit = Cell("effect_unit");
            if (unit is null || !KnownUnits.Contains(unit, StringComparer.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{path}:{index + 1}: unknown effect_unit '{unit}'.");
            }

            var status = Cell("status");
            if (status is null || !KnownStatuses.Contains(status, StringComparer.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{path}:{index + 1}: unknown status '{status}'; a passive whose approval state " +
                    "is not BASELINE must not load into the shipped server.");
            }

            var equipChangePolicy = Cell("equip_change_policy");
            if (equipChangePolicy is null)
            {
                throw new InvalidOperationException($"{path}:{index + 1}: equip_change_policy is required.");
            }

            var rawCap = Cell("pvp_boss_cap") ?? string.Empty;
            var (caps, unparsed) = ClassPassiveContract.ParseCaps(rawCap);

            var definition = new ClassPassiveDefinition(
                passiveId,
                classId,
                branchId,
                tier,
                unlockLevel,
                prerequisite,
                unlockRule,
                effectKey,
                effectValue,
                unit,
                caps,
                unparsed,
                equipChangePolicy,
                status);

            if (!passives.TryAdd(passiveId, definition))
            {
                throw new InvalidOperationException($"{path}:{index + 1}: duplicate passive_id '{passiveId}'.");
            }
        }

        foreach (var classId in ClassPassiveContract.SupportedClassIds)
        {
            var branches = passives.Values
                .Where(passive => passive.ClassId == classId)
                .GroupBy(passive => passive.BranchId)
                .ToList();
            if (branches.Count != 2 || branches.Any(branch => branch.Count() != 4))
            {
                throw new InvalidOperationException(
                    $"{path}: class '{classId}' must carry exactly two branches of four tiers; " +
                    $"found {branches.Count} branches.");
            }
        }

        return new ClassPassiveCatalog(passives);
    }
}

public static class ClassPassiveContract
{
    public static readonly IReadOnlyList<string> SupportedClassIds =
        new[]
        {
            "CLASS_MINH_KIEM",
            "CLASS_ANH_DAO",
            "CLASS_HUYEN_BUT",
            "CLASS_THACH_CHUY",
            "CLASS_LINH_CUNG"
        };

    private static readonly string[] BranchIds =
    [
        "KIEM_Y", "PHAN_CONG", "NHIET", "ANH_SAT", "THUY_AN", "HOI_DONG",
        "THE", "GIU_TRAN", "MOC_TIEU", "ANH_NHAN"
    ];

    public static bool IsBranch(string branchId) => BranchIds.Contains(branchId, StringComparer.Ordinal);

    // `pvp_boss_cap` is one free-text column holding up to three constraints ("8% PvP;
    // 4s; ICD90"). The shapes the source actually uses are classified; the leftovers stay
    // visible in PassiveCapKind.Unparsed because guessing a cap is how a balance number
    // gets invented. 37 of the 47 shipped tokens classify today.
    public static (IReadOnlyList<PassiveCapToken> Caps, IReadOnlyList<string> Unparsed) ParseCaps(
        string rawCap)
    {
        var caps = new List<PassiveCapToken>();
        var unparsed = new List<string>();

        foreach (var fragment in rawCap.Split(';', StringSplitOptions.RemoveEmptyEntries))
        {
            var token = fragment.Trim();
            if (token.Length == 0)
            {
                continue;
            }

            var kind = Classify(token, out var amount);
            if (kind == PassiveCapKind.Unparsed)
            {
                unparsed.Add(token);
            }
            else
            {
                caps.Add(new PassiveCapToken(kind, amount, token));
            }
        }

        return (caps, unparsed);
    }

    private static PassiveCapKind Classify(string token, out decimal amount)
    {
        amount = 0;

        if (TryPercentage(token, out var percent))
        {
            amount = percent;
            if (token.EndsWith("PvP/boss", StringComparison.Ordinal))
            {
                return PassiveCapKind.PercentPvpBoss;
            }

            if (token.EndsWith("PvP", StringComparison.Ordinal))
            {
                return PassiveCapKind.PercentPvp;
            }

            if (token.EndsWith("boss", StringComparison.Ordinal))
            {
                return PassiveCapKind.PercentBoss;
            }

            // A bare "5%" states a magnitude with no scope. Reading it as a boss cap -
            // the shape that would otherwise be assumed - would invent a rule the source
            // does not carry, so it stays unparsed and visible.
            amount = 0;
            return PassiveCapKind.Unparsed;
        }

        if (token.StartsWith("1 proc/", StringComparison.Ordinal) &&
            token.EndsWith('s') &&
            decimal.TryParse(token[7..^1], NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture,
                out var period))
        {
            amount = period;
            return PassiveCapKind.ProcRate;
        }

        if (token.StartsWith("hard cap ", StringComparison.Ordinal) &&
            decimal.TryParse(token["hard cap ".Length..], CultureInfo.InvariantCulture, out var hardCap))
        {
            amount = hardCap;
            return PassiveCapKind.HardCap;
        }

        switch (token)
        {
            case "PvE only":
                return PassiveCapKind.PveOnly;
            case "PvP = 0" or "PvP không áp dụng":
                amount = 0;
                return PassiveCapKind.PvpZero;
            default:
                return PassiveCapKind.Unparsed;
        }
    }

    private static bool TryPercentage(string token, out decimal value)
    {
        value = 0;
        var percentIndex = token.IndexOf('%');
        if (percentIndex <= 0)
        {
            return false;
        }

        var number = token[..percentIndex].Trim();
        return decimal.TryParse(number, NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture,
                   out value) &&
               value >= 0;
    }

    internal static List<string> SplitCsvLine(string line)
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
