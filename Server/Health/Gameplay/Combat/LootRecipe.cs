using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace Server.Health.Gameplay.Combat;

// QOD-17 loot (owner decision Q4): the canonical loot CSV is exported as a
// versioned, design-only bundle. One roll per group, then SELECT_ONE by
// weight; the server owns the RNG and retries return the same receipt. The
// mob coin band has no executable source yet, so grants stay OFF — receipts
// are dry-run only until the reward bundle is complete and reviewed.
public sealed record LootRecipeBundle(
    int SchemaVersion,
    string BundleId,
    string Activation,
    bool GrantEnabled,
    string GrantBlockedReason,
    string SeedVersion,
    IReadOnlyDictionary<string, string> MobTemplateToSource,
    IReadOnlyDictionary<string, LootSource> Sources);

public sealed record LootSource(string SourceId, IReadOnlyList<LootGroup> Groups);

public sealed record LootGroup(
    string GroupId,
    string Mode,
    int ChanceBps,
    IReadOnlyList<LootEntry> Entries);

public sealed record LootEntry(
    string EntryId,
    string ItemId,
    int QuantityMin,
    int QuantityMax,
    int Weight);

public sealed record LootGroupResult(
    string GroupId,
    double ChanceRoll,
    bool Passed,
    string? EntryId,
    string? ItemId,
    int Quantity);

public sealed record LootReceipt(
    string KillKey,
    string MobTemplateId,
    string? SourceId,
    bool Granted,
    string? BlockedReason,
    IReadOnlyList<LootGroupResult> Groups);

public static class LootGroupModes
{
    public const string SelectOne = "SELECT_ONE";
    public const string All = "ALL";
}

public interface ILootRollSource
{
    double Uniform01(string seed);
}

public static class LootRng
{
    public const string SeedVersion = "loot-rng-v1";

    public static double Uniform01(string seed)
    {
        var digest = SHA256.HashData(Encoding.UTF8.GetBytes($"{SeedVersion}|{seed}"));
        var value = BitConverter.ToUInt64(digest, 0);
        return value / (ulong.MaxValue + 1.0);
    }
}

public sealed class LootRngRollSource : ILootRollSource
{
    public double Uniform01(string seed) => LootRng.Uniform01(seed);
}

public sealed class LootRoller
{
    private readonly LootRecipeBundle _bundle;
    private readonly ILootRollSource _rolls;

    public LootRoller(LootRecipeBundle bundle, ILootRollSource rolls)
    {
        _bundle = bundle;
        _rolls = rolls;
    }

    public LootReceipt Roll(string mobTemplateId, string killKey)
    {
        if (!_bundle.MobTemplateToSource.TryGetValue(mobTemplateId, out var sourceId) ||
            !_bundle.Sources.TryGetValue(sourceId, out var source))
        {
            return new LootReceipt(killKey, mobTemplateId, null, false, "NO_SOURCE", []);
        }

        var results = new List<LootGroupResult>();
        foreach (var group in source.Groups)
        {
            var chanceRoll = _rolls.Uniform01($"{killKey}|{group.GroupId}|chance");
            var passed = chanceRoll * 10000 < group.ChanceBps;
            if (!passed)
            {
                results.Add(new LootGroupResult(group.GroupId, chanceRoll, false, null, null, 0));
                continue;
            }

            if (string.Equals(group.Mode, LootGroupModes.All, StringComparison.Ordinal))
            {
                foreach (var entry in group.Entries)
                {
                    results.Add(new LootGroupResult(
                        group.GroupId, chanceRoll, true, entry.EntryId, entry.ItemId,
                        RollQuantity(entry, killKey)));
                }

                continue;
            }

            var picked = PickWeighted(group, killKey);
            results.Add(new LootGroupResult(
                group.GroupId, chanceRoll, true, picked.EntryId, picked.ItemId,
                RollQuantity(picked, killKey)));
        }

        return new LootReceipt(
            killKey,
            mobTemplateId,
            sourceId,
            Granted: false,
            _bundle.GrantEnabled ? null : _bundle.GrantBlockedReason,
            results);
    }

    private LootEntry PickWeighted(LootGroup group, string killKey)
    {
        var totalWeight = 0;
        foreach (var entry in group.Entries)
        {
            totalWeight += entry.Weight;
        }

        var target = _rolls.Uniform01($"{killKey}|{group.GroupId}|select") * totalWeight;
        var cumulative = 0;
        foreach (var entry in group.Entries)
        {
            cumulative += entry.Weight;
            if (target < cumulative)
            {
                return entry;
            }
        }

        return group.Entries[^1];
    }

    private int RollQuantity(LootEntry entry, string killKey)
    {
        var span = entry.QuantityMax - entry.QuantityMin + 1;
        if (span <= 1)
        {
            return entry.QuantityMin;
        }

        var roll = _rolls.Uniform01($"{killKey}|{entry.EntryId}|qty");
        var index = entry.QuantityMin + (int)Math.Floor(roll * span);
        return Math.Clamp(index, entry.QuantityMin, entry.QuantityMax);
    }
}

// Dry-run receipts are stable across retries: the same kill key + source
// returns the stored receipt without re-rolling.
public sealed class LootReceiptLedger
{
    private readonly ConcurrentDictionary<(string KillKey, string SourceId), LootReceipt>
        _receipts = new();

    public LootReceipt Record(LootReceipt receipt)
    {
        if (receipt.SourceId is null)
        {
            return receipt;
        }

        return _receipts.GetOrAdd((receipt.KillKey, receipt.SourceId), receipt);
    }

    public bool TryGet(string killKey, string sourceId, out LootReceipt receipt)
    {
        if (_receipts.TryGetValue((killKey, sourceId), out var stored))
        {
            receipt = stored;
            return true;
        }

        receipt = null!;
        return false;
    }

    public int Count => _receipts.Count;
}

public static class LootRecipeLoader
{
    public const string DesignOnlyActivation = "DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION";
    public const string ExpectedBundleId = "LOOT_RECIPE_V1";
    public const string CoinBandBlockedReason = "COIN_BAND_MISSING";
    private const string RelativePath = "Implementation/Content/Runtime/loot_recipe_v1.json";
    private const int MaxSearchDepth = 12;

    private static readonly System.Text.RegularExpressions.Regex IdPattern =
        new(@"^[A-Z][A-Z0-9_-]+$",
            System.Text.RegularExpressions.RegexOptions.CultureInvariant);

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public static string DiscoverPath(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:LootRecipePath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:LootRecipePath points to '{resolved}', which does not exist.");
            }

            return resolved;
        }

        var starts = new[] { contentRoot, Directory.GetCurrentDirectory(), AppContext.BaseDirectory }
            .Where(path => !string.IsNullOrWhiteSpace(path))
            .Distinct(StringComparer.OrdinalIgnoreCase);

        foreach (var start in starts)
        {
            DirectoryInfo? directory = new(Path.GetFullPath(start));
            for (var depth = 0; depth < MaxSearchDepth && directory is not null; depth++)
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
            $"Could not locate {RelativePath}. Set Content:LootRecipePath or run from the repository.");
    }

    public static LootRecipeBundle Load(string path)
    {
        LootFile? file;
        try
        {
            using var stream = File.OpenRead(path);
            file = JsonSerializer.Deserialize<LootFile>(stream, JsonOptions);
        }
        catch (JsonException exception)
        {
            throw new InvalidOperationException(
                $"{path}: invalid JSON ({exception.Message})", exception);
        }

        if (file is null ||
            file.SchemaVersion != 1 ||
            !string.Equals(file.BundleId, ExpectedBundleId, StringComparison.Ordinal) ||
            !string.Equals(file.Activation, DesignOnlyActivation, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: expected schemaVersion 1, bundleId {ExpectedBundleId} and " +
                $"activation {DesignOnlyActivation}.");
        }

        if (file.GrantEnabled != false)
        {
            throw new InvalidOperationException(
                $"{path}: loot grants must stay OFF until the coin band source exists.");
        }

        if (!string.Equals(file.GrantBlockedReason, CoinBandBlockedReason, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: grantBlockedReason must be {CoinBandBlockedReason}.");
        }

        var rng = file.Rng;
        if (rng is null ||
            !string.Equals(rng.SeedVersion, LootRng.SeedVersion, StringComparison.Ordinal) ||
            !string.Equals(rng.GroupRoll, "ONE_ROLL_PER_GROUP", StringComparison.Ordinal) ||
            !string.Equals(rng.Selection, "WEIGHTED_SELECT_ONE", StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: rng must be {LootRng.SeedVersion}, ONE_ROLL_PER_GROUP + WEIGHTED_SELECT_ONE.");
        }

        var sources = new Dictionary<string, LootSource>(StringComparer.Ordinal);
        foreach (var sourceFile in file.Sources ?? [])
        {
            if (sourceFile.SourceId is null || !IdPattern.IsMatch(sourceFile.SourceId))
            {
                throw new InvalidOperationException($"{path}: invalid sourceId.");
            }

            if (sources.ContainsKey(sourceFile.SourceId))
            {
                throw new InvalidOperationException(
                    $"{path}: duplicate sourceId '{sourceFile.SourceId}'.");
            }

            var groups = new List<LootGroup>();
            var groupIds = new HashSet<string>(StringComparer.Ordinal);
            foreach (var groupFile in sourceFile.Groups ?? [])
            {
                if (string.IsNullOrWhiteSpace(groupFile.GroupId) ||
                    !groupIds.Add(groupFile.GroupId))
                {
                    throw new InvalidOperationException(
                        $"{path}: {sourceFile.SourceId} has invalid or duplicate groupId.");
                }

                if (groupFile.Mode is not (LootGroupModes.SelectOne or LootGroupModes.All) ||
                    groupFile.ChanceBps is < 0 or > 10000)
                {
                    throw new InvalidOperationException(
                        $"{path}: {sourceFile.SourceId}/{groupFile.GroupId} has invalid mode/chance.");
                }

                var entries = new List<LootEntry>();
                var entryIds = new HashSet<string>(StringComparer.Ordinal);
                foreach (var entryFile in groupFile.Entries ?? [])
                {
                    if (entryFile.EntryId is null || !entryIds.Add(entryFile.EntryId))
                    {
                        throw new InvalidOperationException(
                            $"{path}: {sourceFile.SourceId}/{groupFile.GroupId} has invalid or " +
                            "duplicate entryId.");
                    }

                    if (entryFile.ItemId is null || !IdPattern.IsMatch(entryFile.ItemId) ||
                        entryFile.QuantityMin is not { } min || entryFile.QuantityMax is not { } max ||
                        min < 1 || max < min || entryFile.Weight is not { } weight || weight < 1)
                    {
                        throw new InvalidOperationException(
                            $"{path}: entry '{entryFile.EntryId}' has invalid item/quantity/weight.");
                    }

                    entries.Add(new LootEntry(
                        entryFile.EntryId, entryFile.ItemId, min, max, weight));
                }

                if (entries.Count == 0)
                {
                    throw new InvalidOperationException(
                        $"{path}: {sourceFile.SourceId}/{groupFile.GroupId} has no entries.");
                }

                groups.Add(new LootGroup(
                    groupFile.GroupId, groupFile.Mode, groupFile.ChanceBps, entries));
            }

            if (groups.Count == 0)
            {
                throw new InvalidOperationException(
                    $"{path}: source '{sourceFile.SourceId}' has no groups.");
            }

            sources[sourceFile.SourceId] = new LootSource(sourceFile.SourceId, groups);
        }

        if (sources.Count == 0)
        {
            throw new InvalidOperationException($"{path}: sources must not be empty.");
        }

        var mapping = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var mapFile in file.MobTemplateToSource ?? [])
        {
            if (mapFile.MobTemplateId is null || !IdPattern.IsMatch(mapFile.MobTemplateId) ||
                mapFile.SourceId is null || !sources.ContainsKey(mapFile.SourceId))
            {
                throw new InvalidOperationException(
                    $"{path}: mobTemplateToSource entry is invalid or points to a missing source.");
            }

            if (!mapping.TryAdd(mapFile.MobTemplateId, mapFile.SourceId))
            {
                throw new InvalidOperationException(
                    $"{path}: duplicate mob template '{mapFile.MobTemplateId}'.");
            }
        }

        return new LootRecipeBundle(
            1,
            file.BundleId!,
            file.Activation!,
            file.GrantEnabled,
            file.GrantBlockedReason!,
            rng.SeedVersion!,
            mapping,
            sources);
    }

    private sealed class LootFile
    {
        public int SchemaVersion { get; init; }
        public string? BundleId { get; init; }
        public string? Activation { get; init; }
        public bool GrantEnabled { get; init; }
        public string? GrantBlockedReason { get; init; }
        public RngFile? Rng { get; init; }
        public List<MappingFile>? MobTemplateToSource { get; init; }
        public List<SourceFile>? Sources { get; init; }
    }

    private sealed class RngFile
    {
        public string? SeedVersion { get; init; }
        public string? GroupRoll { get; init; }
        public string? Selection { get; init; }
    }

    private sealed class MappingFile
    {
        public string? MobTemplateId { get; init; }
        public string? SourceId { get; init; }
    }

    private sealed class SourceFile
    {
        public string? SourceId { get; init; }
        public List<GroupFile>? Groups { get; init; }
    }

    private sealed class GroupFile
    {
        public string? GroupId { get; init; }
        public string? Mode { get; init; }
        public int ChanceBps { get; init; }
        public List<EntryFile>? Entries { get; init; }
    }

    private sealed class EntryFile
    {
        public string? EntryId { get; init; }
        public string? ItemId { get; init; }
        public int? QuantityMin { get; init; }
        public int? QuantityMax { get; init; }
        public int? Weight { get; init; }
    }
}
