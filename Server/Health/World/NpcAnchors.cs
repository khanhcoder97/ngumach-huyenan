using System.Text.Json;
using System.Text.RegularExpressions;

namespace Server.Health.World;

public sealed record NpcAnchor(
    string NpcId,
    string MapId,
    double X,
    double Y,
    string FloorId);

public sealed class NpcAnchorCatalog
{
    private readonly IReadOnlyDictionary<(string NpcId, string MapId), NpcAnchor> _anchors;

    public NpcAnchorCatalog(IEnumerable<NpcAnchor> anchors)
    {
        _anchors = anchors.ToDictionary(
            anchor => (anchor.NpcId, anchor.MapId),
            anchor => anchor);
    }

    public int Count => _anchors.Count;

    public IEnumerable<NpcAnchor> All => _anchors.Values;

    public bool TryResolve(string npcId, string mapId, out NpcAnchor anchor) =>
        _anchors.TryGetValue((npcId, mapId), out anchor!);

    public bool HasAnchorFor(string npcId)
    {
        foreach (var key in _anchors.Keys)
        {
            if (string.Equals(key.NpcId, npcId, StringComparison.Ordinal))
            {
                return true;
            }
        }

        return false;
    }
}

public static class NpcAnchorLoader
{
    private const string RelativePath = "Implementation/Content/Runtime/npc_anchors.json";
    private const int MaxSearchDepth = 12;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly Regex NpcIdPattern =
        new(@"^NPC_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex MapIdPattern =
        new(@"^MAP_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    public static string DiscoverPath(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:NpcAnchorsPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:NpcAnchorsPath points to '{resolved}', which does not exist.");
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
            $"Could not locate {RelativePath}. Set Content:NpcAnchorsPath or run from the repository.");
    }

    public static NpcAnchorCatalog Load(string path)
    {
        NpcAnchorsFile? file;
        try
        {
            using var stream = File.OpenRead(path);
            file = JsonSerializer.Deserialize<NpcAnchorsFile>(stream, JsonOptions);
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

        if (file.Anchors is null || file.Anchors.Count == 0)
        {
            throw new InvalidOperationException($"{path}: anchors must not be empty.");
        }

        var anchors = new List<NpcAnchor>(file.Anchors.Count);
        var seen = new HashSet<(string, string)>();
        foreach (var anchor in file.Anchors)
        {
            var npcId = anchor.NpcId;
            var mapId = anchor.MapId;
            if (npcId is null || !NpcIdPattern.IsMatch(npcId))
            {
                throw new InvalidOperationException($"{path}: invalid npcId '{npcId}'.");
            }

            if (mapId is null || !MapIdPattern.IsMatch(mapId))
            {
                throw new InvalidOperationException($"{path}: invalid mapId '{mapId}'.");
            }

            if (anchor.XWu is not { } x || !double.IsFinite(x) ||
                anchor.YWu is not { } y || !double.IsFinite(y))
            {
                throw new InvalidOperationException(
                    $"{path}: {npcId} on {mapId} needs finite xWu/yWu.");
            }

            if (!string.Equals(anchor.FloorId, "OVERWORLD", StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{path}: {npcId} on {mapId} uses unsupported floor '{anchor.FloorId}'.");
            }

            if (!seen.Add((npcId, mapId)))
            {
                throw new InvalidOperationException(
                    $"{path}: duplicate anchor for {npcId} on {mapId}.");
            }

            anchors.Add(new NpcAnchor(npcId, mapId, x, y, anchor.FloorId!));
        }

        return new NpcAnchorCatalog(anchors);
    }

    private sealed class NpcAnchorsFile
    {
        public int SchemaVersion { get; init; }
        public List<NpcAnchorFile>? Anchors { get; init; }
    }

    private sealed class NpcAnchorFile
    {
        public string? NpcId { get; init; }
        public string? MapId { get; init; }
        public double? XWu { get; init; }
        public double? YWu { get; init; }
        public string? FloorId { get; init; }
    }
}

public static class NpcAnchorValidator
{
    public static void Validate(NpcAnchorCatalog anchors, MapBoundsCatalog maps)
    {
        if (anchors.Count == 0)
        {
            throw new InvalidOperationException("NPC anchor registry is empty.");
        }

        foreach (var anchor in anchors.All)
        {
            if (!maps.TryResolve(anchor.MapId, out var bounds))
            {
                throw new InvalidOperationException(
                    $"NPC anchor {anchor.NpcId} references unknown map {anchor.MapId}.");
            }

            if (!bounds.Contains(anchor.X, anchor.Y))
            {
                throw new InvalidOperationException(
                    $"NPC anchor {anchor.NpcId} ({anchor.X},{anchor.Y}) is outside " +
                    $"{anchor.MapId} bounds.");
            }
        }
    }
}
