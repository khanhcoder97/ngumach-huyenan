using Microsoft.Extensions.Options;
using Server.Health.Gameplay.Combat;

namespace Server.Health.World;

// 20 Hz background tick per ServerClock.TicksPerSecond. Respawns shared
// DEPLETED interactables/mobs; drives mob AI only when the fixture gate is on.
// Per-character gather shard claims are lazy (UtcNow-based), no tick needed.
public sealed class WorldTickBackgroundService : BackgroundService
{
    private static readonly TimeSpan TickPeriod = TimeSpan.FromSeconds(
        1.0 / ServerClock.TicksPerSecond);

    private readonly WorldEntityRegistry _entities;
    private readonly MobLifecycleService _mobs;
    private readonly MobBehaviorOptions _mobOptions;
    private readonly ISessionStore _sessions;
    private readonly ILogger<WorldTickBackgroundService> _logger;

    public WorldTickBackgroundService(
        WorldEntityRegistry entities,
        MobLifecycleService mobs,
        IOptions<MobBehaviorOptions> mobOptions,
        ISessionStore sessions,
        ILogger<WorldTickBackgroundService> logger)
    {
        _entities = entities;
        _mobs = mobs;
        _mobOptions = mobOptions.Value;
        _sessions = sessions;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var timer = new PeriodicTimer(TickPeriod);
        while (await timer.WaitForNextTickAsync(stoppingToken))
        {
            _entities.Update();

            if (_mobOptions.Enabled)
            {
                _mobs.Tick(_sessions.All());
            }
        }
    }
}
