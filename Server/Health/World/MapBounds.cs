namespace Server.Health.World;

public readonly record struct MapBounds(double XMin, double XMax, double YMin, double YMax)
{
    public bool Contains(double x, double y) =>
        x >= XMin && x <= XMax && y >= YMin && y <= YMax;
}

public sealed class MapBoundsCatalog
{
    private readonly IReadOnlyDictionary<string, MapBounds> _maps;

    public MapBoundsCatalog(IReadOnlyDictionary<string, MapBounds> maps)
    {
        _maps = maps;
    }

    public int Count => _maps.Count;

    public bool TryResolve(string mapId, out MapBounds bounds) =>
        _maps.TryGetValue(mapId, out bounds);
}
