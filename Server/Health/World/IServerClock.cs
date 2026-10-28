namespace Server.Health.World;

public interface IServerClock
{
    DateTimeOffset UtcNow { get; }

    long Tick { get; }
}

// Deterministic clock for headless tests and self-checks; production uses ServerClock.
public sealed class ManualServerClock : IServerClock
{
    private DateTimeOffset _now;

    public ManualServerClock(DateTimeOffset start)
    {
        _now = start;
    }

    public DateTimeOffset UtcNow => _now;

    public long Tick { get; private set; }

    public void Advance(TimeSpan delta)
    {
        if (delta < TimeSpan.Zero)
        {
            throw new ArgumentOutOfRangeException(nameof(delta));
        }

        _now += delta;
        Tick += (long)(delta.TotalSeconds * ServerClock.TicksPerSecond);
    }
}
