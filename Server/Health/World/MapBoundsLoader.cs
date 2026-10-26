using System.Text.Json;
using System.Text.RegularExpressions;

namespace Server.Health.World;

public static class MapBoundsLoader
{
    private const string RelativePath = "Implementation/Content/map_bounds.json";
    private const int MaxSearchDepth = 12;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private static readonly Regex MapIdPattern =
        new(@"^MAP_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    public static string DiscoverPath(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:MapBoundsPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:MapBoundsPath points to '{resolved}', which does not exist.");
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
            $"Could not locate {RelativePath}. Set Content:MapBoundsPath or run from the repository.");
    }

    public static MapBoundsCatalog Load(string path)
    {
        MapBoundsFile? file;
        try
        {
            using var stream = File.OpenRead(path);
            file = JsonSerializer.Deserialize<MapBoundsFile>(stream, JsonOptions);
        }
        catch (JsonException exception)
        {
            throw new InvalidOperationException($"{path}: invalid JSON ({exception.Message})", exception);
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

        var defaultBounds = ToBounds(file.DefaultBounds, $"{path}: defaultBounds");
        var knownMapIds = file.KnownMapIds;
        if (knownMapIds is null || knownMapIds.Count == 0)
        {
            throw new InvalidOperationException($"{path}: knownMapIds must be a non-empty array.");
        }

        var overrides = file.Overrides;
        var maps = new Dictionary<string, MapBounds>(StringComparer.Ordinal);
        foreach (var mapId in knownMapIds)
        {
            if (string.IsNullOrWhiteSpace(mapId) || !MapIdPattern.IsMatch(mapId))
            {
                throw new InvalidOperationException($"{path}: invalid map ID '{mapId}'.");
            }

            var bounds = defaultBounds;
            if (overrides is not null && overrides.TryGetValue(mapId, out var overrideBounds))
            {
                bounds = ToBounds(overrideBounds, $"{path}: overrides.{mapId}");
            }

            if (!maps.TryAdd(mapId, bounds))
            {
                throw new InvalidOperationException($"{path}: duplicate map ID '{mapId}'.");
            }
        }

        if (overrides is not null)
        {
            foreach (var mapId in overrides.Keys)
            {
                if (!maps.ContainsKey(mapId))
                {
                    throw new InvalidOperationException(
                        $"{path}: overrides.{mapId} does not match any known map ID.");
                }
            }
        }

        return new MapBoundsCatalog(maps);
    }

    private static MapBounds ToBounds(BoundsFile? bounds, string label)
    {
        if (bounds is null ||
            bounds.XMin is null ||
            bounds.XMax is null ||
            bounds.YMin is null ||
            bounds.YMax is null)
        {
            throw new InvalidOperationException(
                $"{label}: xMin, xMax, yMin and yMax are required numbers.");
        }

        var xMin = bounds.XMin.Value;
        var xMax = bounds.XMax.Value;
        var yMin = bounds.YMin.Value;
        var yMax = bounds.YMax.Value;

        if (!double.IsFinite(xMin) || !double.IsFinite(xMax) ||
            !double.IsFinite(yMin) || !double.IsFinite(yMax))
        {
            throw new InvalidOperationException($"{label}: bounds must be finite numbers.");
        }

        if (xMin >= xMax || yMin >= yMax)
        {
            throw new InvalidOperationException($"{label}: min bounds must be smaller than max bounds.");
        }

        return new MapBounds(xMin, xMax, yMin, yMax);
    }

    private sealed class MapBoundsFile
    {
        public int SchemaVersion { get; init; }
        public BoundsFile? DefaultBounds { get; init; }
        public Dictionary<string, BoundsFile>? Overrides { get; init; }
        public List<string>? KnownMapIds { get; init; }
    }

    private sealed class BoundsFile
    {
        public double? XMin { get; init; }
        public double? XMax { get; init; }
        public double? YMin { get; init; }
        public double? YMax { get; init; }
    }
}
