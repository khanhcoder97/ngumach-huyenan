using Microsoft.Extensions.Options;
using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// Q-B5: the mob side of "can a client read the attack". The v2 snapshot already
// carries a mob's `state`, so TELEGRAPH is visible — but a state name is not a
// read window: to lean back, block at the right tick, or flash a warning ring a
// client needs which swing is committed, at whom, when it lands and how far it
// reaches. That is what this projects, from the AI's own brain, in the same
// server-tick units the rest of the combat read model uses.
//
// Nothing here is on the wire. Publishing it means the optional versioned
// `telegraph` block in the QOD-18 proposal; until that is approved this serves
// tests, probes and any internal caller that must not guess from `state` alone.
public sealed record MobTelegraphReading(
    string EntityId,
    long LifeId,
    double X,
    double Y,
    string State,
    string? TargetCharacterId,
    long? ImpactInTicks,
    DateTimeOffset? ImpactAtUtc,
    long? RecoverInTicks,
    long? NextAttackInTicks,
    double RangeWu,
    double? AngleDegrees);

public sealed class MobTelegraphProjection
{
    private const long TickLengthTicks = TimeSpan.TicksPerSecond / ServerClock.TicksPerSecond;

    private readonly MobLifecycleService _mobs;
    private readonly MobBehaviorOptions _options;
    private readonly IServerClock _clock;

    public MobTelegraphProjection(
        MobLifecycleService mobs,
        IOptions<MobBehaviorOptions> options,
        IServerClock clock)
    {
        _mobs = mobs;
        _options = options.Value;
        _clock = clock;
    }

    // Only engaged entities are reported: an idle mob has nothing to read, and a
    // long list of them would make a client draw warnings for the whole map.
    public IReadOnlyList<MobTelegraphReading> Project(IEnumerable<WorldEntityInstance> entities)
    {
        var now = _clock.UtcNow;
        var readings = new List<MobTelegraphReading>();
        foreach (var entity in entities)
        {
            if (!string.Equals(entity.Kind, WorldEntityKinds.Mob, StringComparison.Ordinal) &&
                !string.Equals(entity.Kind, WorldEntityKinds.Boss, StringComparison.Ordinal))
            {
                continue;
            }

            if (_mobs.GetAttackWindow(entity.EntityId) is not { } window ||
                string.Equals(window.State, MobBehaviorStates.Idle, StringComparison.Ordinal))
            {
                continue;
            }

            readings.Add(new MobTelegraphReading(
                entity.EntityId,
                entity.LifeId,
                entity.X,
                entity.Y,
                window.State,
                window.TargetCharacterId,
                TicksUntil(window.ImpactAtUtc, now),
                window.ImpactAtUtc,
                TicksUntil(window.RecoverUntilUtc, now),
                TicksUntil(window.NextAttackAtUtc, now),
                _options.AttackRangeWu,
                // A per-move telegraph shape (width, length, arc) is not exported
                // by any canonical content yet, so this stays null rather than
                // borrowing the defender-side 120 degrees from DEC-022.
                AngleDegrees: null));
        }

        return readings;
    }

    private static long? TicksUntil(DateTimeOffset? at, DateTimeOffset now)
    {
        if (at is not { } moment)
        {
            return null;
        }

        // Integer ceiling on 100-nanosecond ticks: the AI's windows are exact
        // multiples like 0,45 s, and double arithmetic on TotalSeconds turns that
        // into 9,0000000000000002, which a floating ceil would round up to 10.
        var remaining = (moment - now).Ticks;
        return remaining <= 0
            ? 0
            : (remaining + TickLengthTicks - 1) / TickLengthTicks;
    }
}
