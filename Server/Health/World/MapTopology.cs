using System.Text.Json;
using System.Text.RegularExpressions;

namespace Server.Health.World;

public static class TopologyReviewStates
{
    public const string Reviewed = "REVIEWED";
    public const string SyntheticTestOnly = "SYNTHETIC_TEST_ONLY";

    public static bool IsValid(string? value) =>
        string.Equals(value, Reviewed, StringComparison.Ordinal) ||
        string.Equals(value, SyntheticTestOnly, StringComparison.Ordinal);
}

public sealed record TopologyPoint(double X, double Y);

public sealed record MapPolygon(string FloorId, IReadOnlyList<TopologyPoint> Points);

public sealed record TopologyPlacement(
    string RecordId,
    string NpcId,
    string FloorId,
    double X,
    double Y);

public sealed class MapTopologyBundle
{
    public required string MapId { get; init; }
    public required int LayoutVersion { get; init; }
    public required int BundleVersion { get; init; }
    public required string ReviewState { get; init; }
    public required bool IsReviewed { get; init; }
    public required MapBounds Bounds { get; init; }
    public required IReadOnlyList<string> FloorIds { get; init; }
    public required IReadOnlyList<MapPolygon> WalkablePolygons { get; init; }
    public required IReadOnlyList<MapPolygon> BlockedPolygons { get; init; }
    public required IReadOnlyList<TopologyPlacement> Placements { get; init; }
}

public sealed class WorldGeometryCatalog
{
    private readonly IReadOnlyDictionary<string, MapTopologyBundle> _bundles;

    public WorldGeometryCatalog(IEnumerable<MapTopologyBundle> bundles)
    {
        _bundles = bundles.ToDictionary(bundle => bundle.MapId, bundle => bundle);
    }

    public int Count => _bundles.Count;

    public int ReviewedCount => _bundles.Values.Count(bundle => bundle.IsReviewed);

    public IEnumerable<MapTopologyBundle> All => _bundles.Values;

    public bool TryGet(string mapId, out MapTopologyBundle bundle)
    {
        if (_bundles.TryGetValue(mapId, out var found))
        {
            bundle = found;
            return true;
        }

        bundle = null!;
        return false;
    }
}

public static class MapTopologyLoader
{
    private const string RelativeDirectory = "Implementation/Content/Examples/MapTopology";
    private const int MaxSearchDepth = 12;
    private const int SupportedBundleVersion = 2;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly Regex MapIdPattern =
        new(@"^MAP_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex FloorIdPattern =
        new(@"^[A-Z][A-Z0-9_]*$", RegexOptions.CultureInvariant);

    private static readonly Regex NpcIdPattern =
        new(@"^NPC_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex RecordIdPattern =
        new(@"^MAN-[A-Z0-9_-]+$", RegexOptions.CultureInvariant);

    public static string DiscoverDirectory(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:TopologyPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!Directory.Exists(resolved))
            {
                throw new DirectoryNotFoundException(
                    $"Content:TopologyPath points to '{resolved}', which does not exist.");
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
                var candidate = Path.Combine(directory.FullName, RelativeDirectory);
                if (Directory.Exists(candidate))
                {
                    return candidate;
                }

                directory = directory.Parent;
            }
        }

        throw new DirectoryNotFoundException(
            $"Could not locate {RelativeDirectory}. Set Content:TopologyPath or run from the repository.");
    }

    public static WorldGeometryCatalog Load(string directory, MapBoundsCatalog maps)
    {
        var files = Directory
            .EnumerateFiles(directory, "*.json", SearchOption.TopDirectoryOnly)
            .OrderBy(path => path, StringComparer.Ordinal)
            .ToList();

        if (files.Count == 0)
        {
            throw new InvalidOperationException(
                $"{directory}: no MapTopology JSON files found.");
        }

        var bundles = new List<MapTopologyBundle>(files.Count);
        foreach (var path in files)
        {
            MapTopologyFile? file;
            try
            {
                using var stream = File.OpenRead(path);
                file = JsonSerializer.Deserialize<MapTopologyFile>(stream, JsonOptions);
            }
            catch (JsonException exception)
            {
                throw new InvalidOperationException(
                    $"{path}: invalid JSON ({exception.Message})", exception);
            }

            bundles.Add(ToBundle(path, file, maps));
        }

        return new WorldGeometryCatalog(bundles);
    }

    private static MapTopologyBundle ToBundle(
        string path, MapTopologyFile? file, MapBoundsCatalog maps)
    {
        if (file is null)
        {
            throw new InvalidOperationException($"{path}: file is empty.");
        }

        if (file.SchemaVersion != 1)
        {
            throw new InvalidOperationException(
                $"{path}: unsupported schemaVersion '{file.SchemaVersion}'.");
        }

        if (file.MapId is null || !MapIdPattern.IsMatch(file.MapId))
        {
            throw new InvalidOperationException($"{path}: invalid mapId '{file.MapId}'.");
        }

        if (file.LayoutVersion is not { } layoutVersion || layoutVersion < 1)
        {
            throw new InvalidOperationException($"{path}: layoutVersion must be >= 1.");
        }

        if (file.BundleVersion != SupportedBundleVersion)
        {
            throw new InvalidOperationException(
                $"{path}: bundleVersion {file.BundleVersion} is not {SupportedBundleVersion}.");
        }

        if (!string.Equals(file.CoordinateSystem, "TOP_DOWN_XY", StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: coordinateSystem '{file.CoordinateSystem}' is not TOP_DOWN_XY.");
        }

        if (!TopologyReviewStates.IsValid(file.ReviewState))
        {
            throw new InvalidOperationException(
                $"{path}: reviewState '{file.ReviewState}' is invalid.");
        }

        if (!maps.TryResolve(file.MapId, out var registryBounds))
        {
            throw new InvalidOperationException(
                $"{path}: mapId '{file.MapId}' has no registry bounds.");
        }

        if (file.Bounds is null ||
            file.Bounds.XMin != registryBounds.XMin ||
            file.Bounds.XMax != registryBounds.XMax ||
            file.Bounds.YMin != registryBounds.YMin ||
            file.Bounds.YMax != registryBounds.YMax)
        {
            throw new InvalidOperationException(
                $"{path}: bounds do not match {file.MapId} registry bounds.");
        }

        var floorIds = file.FloorIds ?? [];
        if (floorIds.Count == 0)
        {
            throw new InvalidOperationException($"{path}: floorIds must not be empty.");
        }

        if (floorIds.Distinct(StringComparer.Ordinal).Count() != floorIds.Count)
        {
            throw new InvalidOperationException($"{path}: floorIds contains duplicates.");
        }

        foreach (var floorId in floorIds)
        {
            if (floorId is null || !FloorIdPattern.IsMatch(floorId))
            {
                throw new InvalidOperationException($"{path}: invalid floorId '{floorId}'.");
            }
        }

        var walkable = ConvertPolygons(path, "walkablePolygons", file.WalkablePolygons,
            floorIds, registryBounds);
        if (walkable.Count == 0)
        {
            throw new InvalidOperationException(
                $"{path}: walkablePolygons must not be empty.");
        }

        var blocked = ConvertPolygons(path, "blockedPolygons", file.BlockedPolygons,
            floorIds, registryBounds);
        var placements = ConvertPlacements(path, file.Placements, file.MapId, floorIds,
            registryBounds);

        if (file.SourceRefs is null || file.SourceRefs.Count == 0 ||
            file.SourceRefs.Any(reference => string.IsNullOrWhiteSpace(reference)))
        {
            throw new InvalidOperationException($"{path}: sourceRefs must not be empty.");
        }

        return new MapTopologyBundle
        {
            MapId = file.MapId,
            LayoutVersion = layoutVersion,
            BundleVersion = file.BundleVersion.Value,
            ReviewState = file.ReviewState!,
            IsReviewed = string.Equals(
                file.ReviewState, TopologyReviewStates.Reviewed, StringComparison.Ordinal),
            Bounds = registryBounds,
            FloorIds = floorIds,
            WalkablePolygons = walkable,
            BlockedPolygons = blocked,
            Placements = placements
        };
    }

    private static List<MapPolygon> ConvertPolygons(
        string path,
        string field,
        List<PolygonFile>? polygons,
        IReadOnlyList<string> floorIds,
        MapBounds bounds)
    {
        var result = new List<MapPolygon>(polygons?.Count ?? 0);
        for (var index = 0; index < (polygons?.Count ?? 0); index++)
        {
            var polygon = polygons![index];
            if (polygon.FloorId is null || !floorIds.Contains(polygon.FloorId, StringComparer.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{path}: {field}[{index}] floorId '{polygon.FloorId}' is not declared.");
            }

            var points = new List<TopologyPoint>(polygon.Points?.Count ?? 0);
            for (var pointIndex = 0; pointIndex < (polygon.Points?.Count ?? 0); pointIndex++)
            {
                var point = polygon.Points![pointIndex];
                if (point.XWu is not { } x || !double.IsFinite(x) ||
                    point.YWu is not { } y || !double.IsFinite(y))
                {
                    throw new InvalidOperationException(
                        $"{path}: {field}[{index}].points[{pointIndex}] is not finite.");
                }

                if (!bounds.Contains(x, y))
                {
                    throw new InvalidOperationException(
                        $"{path}: {field}[{index}].points[{pointIndex}] ({x},{y}) is outside bounds.");
                }

                points.Add(new TopologyPoint(x, y));
            }

            if (points.Count < 3)
            {
                throw new InvalidOperationException(
                    $"{path}: {field}[{index}] needs at least 3 points.");
            }

            if (GeometryMath.PolygonSelfIntersects(points))
            {
                throw new InvalidOperationException(
                    $"{path}: {field}[{index}] self-intersects.");
            }

            result.Add(new MapPolygon(polygon.FloorId, points));
        }

        return result;
    }

    private static List<TopologyPlacement> ConvertPlacements(
        string path,
        List<PlacementFile>? placements,
        string mapId,
        IReadOnlyList<string> floorIds,
        MapBounds bounds)
    {
        var result = new List<TopologyPlacement>(placements?.Count ?? 0);
        var seen = new HashSet<(string, string)>();
        for (var index = 0; index < (placements?.Count ?? 0); index++)
        {
            var placement = placements![index];
            if (placement.RecordId is null || !RecordIdPattern.IsMatch(placement.RecordId))
            {
                throw new InvalidOperationException(
                    $"{path}: placements[{index}].recordId '{placement.RecordId}' is invalid.");
            }

            if (placement.NpcId is null || !NpcIdPattern.IsMatch(placement.NpcId))
            {
                throw new InvalidOperationException(
                    $"{path}: placements[{index}].npcId '{placement.NpcId}' is invalid.");
            }

            if (placement.FloorId is null ||
                !floorIds.Contains(placement.FloorId, StringComparer.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{path}: placements[{index}] floorId '{placement.FloorId}' is not declared.");
            }

            if (placement.XWu is not { } x || !double.IsFinite(x) ||
                placement.YWu is not { } y || !double.IsFinite(y))
            {
                throw new InvalidOperationException(
                    $"{path}: placements[{index}] xWu/yWu is not finite.");
            }

            if (!bounds.Contains(x, y))
            {
                throw new InvalidOperationException(
                    $"{path}: placements[{index}] ({x},{y}) is outside {mapId} bounds.");
            }

            if (!seen.Add((placement.NpcId, placement.FloorId)))
            {
                throw new InvalidOperationException(
                    $"{path}: duplicate placement for {placement.NpcId} on {placement.FloorId}.");
            }

            result.Add(new TopologyPlacement(
                placement.RecordId, placement.NpcId, placement.FloorId, x, y));
        }

        return result;
    }

    private sealed class MapTopologyFile
    {
        public int SchemaVersion { get; init; }
        public string? MapId { get; init; }
        public int? LayoutVersion { get; init; }
        public int? BundleVersion { get; init; }
        public string? CoordinateSystem { get; init; }
        public string? ReviewState { get; init; }
        public BoundsFile? Bounds { get; init; }
        public List<string>? FloorIds { get; init; }
        public List<PolygonFile>? WalkablePolygons { get; init; }
        public List<PolygonFile>? BlockedPolygons { get; init; }
        public List<PlacementFile>? Placements { get; init; }
        public List<string>? SourceRefs { get; init; }
    }

    private sealed class BoundsFile
    {
        public double XMin { get; init; }
        public double XMax { get; init; }
        public double YMin { get; init; }
        public double YMax { get; init; }
    }

    private sealed class PolygonFile
    {
        public string? FloorId { get; init; }
        public List<PointFile>? Points { get; init; }
    }

    private sealed class PointFile
    {
        public double? XWu { get; init; }
        public double? YWu { get; init; }
    }

    private sealed class PlacementFile
    {
        public string? RecordId { get; init; }
        public string? NpcId { get; init; }
        public string? FloorId { get; init; }
        public double? XWu { get; init; }
        public double? YWu { get; init; }
    }
}
