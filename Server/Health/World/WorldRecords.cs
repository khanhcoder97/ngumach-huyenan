using System.Text.Json;
using System.Text.RegularExpressions;

namespace Server.Health.World;

public sealed record WorldGatherRecord(
    string Profession,
    string ItemId,
    int YieldMin,
    int YieldMax,
    int ProfessionLevelRequired,
    string ToolId);

public sealed record WorldRecord(
    string RecordId,
    string MapId,
    string RecordType,
    string DesignState,
    string EntityId,
    double X,
    double Y,
    int RespawnSeconds,
    string RespawnPolicy,
    string Condition,
    WorldGatherRecord? Gather);

public sealed class WorldRecordCatalog
{
    private readonly IReadOnlyDictionary<string, WorldRecord> _records;
    private readonly IReadOnlyDictionary<string, IReadOnlyList<WorldRecord>> _byEntityId;

    public WorldRecordCatalog(IReadOnlyList<WorldRecord> records)
    {
        _records = records.ToDictionary(record => record.RecordId, record => record);
        _byEntityId = records
            .GroupBy(record => record.EntityId, StringComparer.Ordinal)
            .ToDictionary(
                group => group.Key,
                group => (IReadOnlyList<WorldRecord>)group.ToArray(),
                StringComparer.Ordinal);
    }

    public int Count => _records.Count;

    public bool TryGet(string recordId, out WorldRecord record) =>
        _records.TryGetValue(recordId, out record!);

    // Quest objective targetIds use canonical manifest entity_id values (which may
    // repeat across maps), so resolution is by entityId on the objective's map.
    public bool TryResolveTarget(string targetId, string mapId, out WorldRecord record)
    {
        if (_records.TryGetValue(targetId, out record!))
        {
            return true;
        }

        if (!_byEntityId.TryGetValue(targetId, out var candidates))
        {
            record = null!;
            return false;
        }

        foreach (var candidate in candidates)
        {
            if (string.Equals(candidate.MapId, mapId, StringComparison.Ordinal))
            {
                record = candidate;
                return true;
            }
        }

        record = null!;
        return false;
    }
}

public static class WorldRecordLoader
{
    private const string RelativePath = "Implementation/Content/Runtime/world_records.json";
    private const int MaxSearchDepth = 12;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly Regex RecordIdPattern =
        new(@"^MAN-[A-Z0-9_-]+$", RegexOptions.CultureInvariant);

    private static readonly Regex EntityIdPattern =
        new(@"^[A-Z][A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex MapIdPattern =
        new(@"^MAP_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex ItemIdPattern =
        new(@"^[A-Z][A-Z0-9-]+$", RegexOptions.CultureInvariant);

    public static string DiscoverPath(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:WorldRecordsPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:WorldRecordsPath points to '{resolved}', which does not exist.");
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
            $"Could not locate {RelativePath}. Set Content:WorldRecordsPath or run from the repository.");
    }

    public static WorldRecordCatalog Load(string path, MapBoundsCatalog maps)
    {
        WorldRecordsFile? file;
        try
        {
            using var stream = File.OpenRead(path);
            file = JsonSerializer.Deserialize<WorldRecordsFile>(stream, JsonOptions);
        }
        catch (JsonException exception)
        {
            throw new InvalidOperationException(
                $"{path}: invalid JSON ({exception.Message})", exception);
        }

        if (file is null)
        {
            throw new InvalidOperationException($"{path}: file is empty.");
        }

        if (file.SchemaVersion != 1)
        {
            throw new InvalidOperationException(
                $"{path}: unsupported schemaVersion '{file.SchemaVersion}'.");
        }

        var records = new List<WorldRecord>(file.Records?.Count ?? 0);
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var source in file.Records ?? [])
        {
            if (source.RecordId is null || !RecordIdPattern.IsMatch(source.RecordId))
            {
                throw new InvalidOperationException(
                    $"{path}: invalid recordId '{source.RecordId}'.");
            }

            if (!seen.Add(source.RecordId))
            {
                throw new InvalidOperationException(
                    $"{path}: duplicate recordId '{source.RecordId}'.");
            }

            if (!IsKnownRecordType(source.RecordType))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.RecordId} has invalid recordType '{source.RecordType}'.");
            }

            if (source.MapId is null || !MapIdPattern.IsMatch(source.MapId))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.RecordId} has invalid mapId '{source.MapId}'.");
            }

            if (!maps.TryResolve(source.MapId, out _))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.RecordId} mapId '{source.MapId}' has no registry bounds.");
            }

            if (source.X is not { } x || !double.IsFinite(x) ||
                source.Y is not { } y || !double.IsFinite(y))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.RecordId} position is invalid or not finite.");
            }

            if (source.RespawnSeconds is not { } respawn || respawn < 0)
            {
                throw new InvalidOperationException(
                    $"{path}: {source.RecordId} respawnSeconds must be >= 0.");
            }

            if (source.EntityId is null || !EntityIdPattern.IsMatch(source.EntityId))
            {
                throw new InvalidOperationException(
                    $"{path}: {source.RecordId} has invalid entityId '{source.EntityId}'.");
            }

            WorldGatherRecord? gather = null;
            if (string.Equals(source.RecordType, WorldEntityKinds.GatherNode, StringComparison.Ordinal))
            {
                var gatherFile = source.Gather;
                if (gatherFile is null ||
                    string.IsNullOrWhiteSpace(gatherFile.ItemId) ||
                    !ItemIdPattern.IsMatch(gatherFile.ItemId) ||
                    gatherFile.YieldMin is not { } yieldMin || yieldMin < 1 ||
                    gatherFile.YieldMax is not { } yieldMax || yieldMax < yieldMin ||
                    gatherFile.ProfessionLevelRequired is not { } level || level < 1)
                {
                    throw new InvalidOperationException(
                        $"{path}: {source.RecordId} gather node needs itemId, " +
                        "1 <= yieldMin <= yieldMax and professionLevelRequired >= 1.");
                }

                gather = new WorldGatherRecord(
                    gatherFile.Profession ?? string.Empty,
                    gatherFile.ItemId,
                    yieldMin,
                    yieldMax,
                    level,
                    gatherFile.ToolId ?? string.Empty);
            }

            records.Add(new WorldRecord(
                source.RecordId,
                source.MapId,
                source.RecordType!,
                source.DesignState ?? string.Empty,
                source.EntityId,
                x,
                y,
                respawn,
                source.RespawnPolicy ?? string.Empty,
                source.Condition ?? string.Empty,
                gather));
        }

        if (records.Count == 0)
        {
            throw new InvalidOperationException($"{path}: no world records found.");
        }

        return new WorldRecordCatalog(records);
    }

    private static bool IsKnownRecordType(string? value) => value is
        "NPC" or "MOB_GROUP" or "BOSS" or "GATHER_NODE" or "INTERACTABLE";

    private sealed class WorldRecordsFile
    {
        public int SchemaVersion { get; init; }
        public List<WorldRecordFile>? Records { get; init; }
    }

    private sealed class WorldRecordFile
    {
        public string? RecordId { get; init; }
        public string? MapId { get; init; }
        public string? RecordType { get; init; }
        public string? DesignState { get; init; }
        public string? EntityId { get; init; }
        public double? XWu { get; init; }
        public double? YWu { get; init; }
        public int? RespawnSeconds { get; init; }
        public string? RespawnPolicy { get; init; }
        public string? Condition { get; init; }
        public GatherFile? Gather { get; init; }
    }

    private sealed class GatherFile
    {
        public string? Profession { get; init; }
        public string? ItemId { get; init; }
        public int? YieldMin { get; init; }
        public int? YieldMax { get; init; }
        public int? ProfessionLevelRequired { get; init; }
        public string? ToolId { get; init; }
    }
}
