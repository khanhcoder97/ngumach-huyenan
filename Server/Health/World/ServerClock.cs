using System.Diagnostics;

namespace Server.Health.World;

public sealed class ServerClock
{
    // Production technical contract: 20 authoritative simulation ticks per second.
    public const int TicksPerSecond = 20;

    private readonly long _startTimestamp = Stopwatch.GetTimestamp();

    public DateTimeOffset UtcNow => DateTimeOffset.UtcNow;

    public long Tick =>
        (long)(Stopwatch.GetElapsedTime(_startTimestamp).TotalSeconds * TicksPerSecond);
}
