namespace Server.Health.World;

public sealed class P1WorldOptions
{
    public const string SectionName = "P1World";

    public string DefaultMapId { get; set; } = "MAP_BEN_MUA";
    public double SpawnX { get; set; } = 18;
    public double SpawnY { get; set; }
    public double MoveSpeedWuPerSecond { get; set; } = 6;
    public double MaxStepSeconds { get; set; } = 0.25;
    public double MaxStepDistanceWu { get; set; } = 1.5;
    public int StartingHp { get; set; } = 100;
    public int StartingMaxHp { get; set; } = 100;
    public int StartingMp { get; set; } = 50;
    public int StartingMaxMp { get; set; } = 50;
    public int StartingLevel { get; set; } = 1;

    // DEC-016 hero footprint 1.2x0.6 WU: half-width used as the swept radius.
    public double ActorFootprintRadiusWu { get; set; } = 0.6;
}

public static class P1WorldOptionsValidator
{
    public static void Validate(P1WorldOptions options, MapBoundsCatalog maps)
    {
        if (string.IsNullOrWhiteSpace(options.DefaultMapId))
        {
            throw new InvalidOperationException("P1World:DefaultMapId must be set.");
        }

        if (!maps.TryResolve(options.DefaultMapId, out var bounds))
        {
            throw new InvalidOperationException(
                $"P1World:DefaultMapId '{options.DefaultMapId}' is not listed in map_bounds.json.");
        }

        if (!double.IsFinite(options.SpawnX) ||
            !double.IsFinite(options.SpawnY) ||
            !bounds.Contains(options.SpawnX, options.SpawnY))
        {
            throw new InvalidOperationException(
                $"P1World spawn ({options.SpawnX}, {options.SpawnY}) is outside " +
                $"{options.DefaultMapId} bounds x={bounds.XMin}..{bounds.XMax} " +
                $"y={bounds.YMin}..{bounds.YMax}.");
        }

        if (!double.IsFinite(options.MoveSpeedWuPerSecond) || options.MoveSpeedWuPerSecond <= 0)
        {
            throw new InvalidOperationException("P1World:MoveSpeedWuPerSecond must be greater than zero.");
        }

        if (!double.IsFinite(options.MaxStepSeconds) || options.MaxStepSeconds <= 0)
        {
            throw new InvalidOperationException("P1World:MaxStepSeconds must be greater than zero.");
        }

        if (!double.IsFinite(options.MaxStepDistanceWu) || options.MaxStepDistanceWu <= 0)
        {
            throw new InvalidOperationException("P1World:MaxStepDistanceWu must be greater than zero.");
        }

        if (!double.IsFinite(options.ActorFootprintRadiusWu) ||
            options.ActorFootprintRadiusWu < 0)
        {
            throw new InvalidOperationException(
                "P1World:ActorFootprintRadiusWu must be zero or greater.");
        }

        if (options.MoveSpeedWuPerSecond * options.MaxStepSeconds > options.MaxStepDistanceWu + 1e-9)
        {
            throw new InvalidOperationException(
                "P1World:MaxStepDistanceWu must be at least " +
                "MoveSpeedWuPerSecond * MaxStepSeconds.");
        }

        if (options.StartingMaxHp <= 0 ||
            options.StartingHp < 0 ||
            options.StartingHp > options.StartingMaxHp)
        {
            throw new InvalidOperationException(
                "P1World starting HP must satisfy 0 <= StartingHp <= StartingMaxHp and StartingMaxHp > 0.");
        }

        if (options.StartingLevel < 1 || options.StartingLevel > 100)
        {
            throw new InvalidOperationException("P1World:StartingLevel must be within 1..100.");
        }

        if (options.StartingMaxMp < 0 ||
            options.StartingMp < 0 ||
            options.StartingMp > options.StartingMaxMp)
        {
            throw new InvalidOperationException(
                "P1World starting MP must satisfy 0 <= StartingMp <= StartingMaxMp.");
        }
    }
}
