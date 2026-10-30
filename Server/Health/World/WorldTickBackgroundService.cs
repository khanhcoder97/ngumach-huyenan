using Microsoft.Extensions.Options;
using Server.Health.Gameplay.Combat;

namespace Server.Health.World;

// 20 Hz background tick per ServerClock.TicksPerSecond. Respawns shared
// DEPLETED interactables/mobs, resolves scheduled player casts, drives mob AI
// (telegraph -> impact -> recovery) only when the fixture gate is on, and lands
// mob damage only when P1:CombatDamage is on. Per-character gather shard claims
// are lazy (UtcNow-based), no tick needed.
public sealed class WorldTickBackgroundService : BackgroundService
{
    private static readonly TimeSpan TickPeriod = TimeSpan.FromSeconds(
        1.0 / ServerClock.TicksPerSecond);

    private readonly WorldEntityRegistry _entities;
    private readonly MobLifecycleService _mobs;
    private readonly MobAttackService _mobAttacks;
    private readonly MobBehaviorOptions _mobOptions;
    private readonly ISessionStore _sessions;
    private readonly CombatTickEngine _combat;
    private readonly MobSpawnGroupService _groups;
    private readonly ServerClock _clock;
    private readonly ILogger<WorldTickBackgroundService> _logger;

    public WorldTickBackgroundService(
        WorldEntityRegistry entities,
        MobLifecycleService mobs,
        MobAttackService mobAttacks,
        IOptions<MobBehaviorOptions> mobOptions,
        ISessionStore sessions,
        CombatTickEngine combat,
        MobSpawnGroupService groups,
        ServerClock clock,
        ILogger<WorldTickBackgroundService> logger)
    {
        _entities = entities;
        _mobs = mobs;
        _mobAttacks = mobAttacks;
        _mobOptions = mobOptions.Value;
        _sessions = sessions;
        _combat = combat;
        _groups = groups;
        _clock = clock;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var timer = new PeriodicTimer(TickPeriod);
        while (await timer.WaitForNextTickAsync(stoppingToken))
        {
            _entities.Update();
            _combat.Tick(_clock.Tick);
            _groups.Tick();

            if (_mobOptions.Enabled)
            {
                var players = _sessions.All();
                var impacts = _mobAttacks.ApplyImpacts(_mobs.Tick(players), players);
                foreach (var impact in impacts)
                {
                    if (impact.BlockedReason != MobAttackBlockedReasons.None)
                    {
                        _logger.LogInformation(
                            "DEV FIXTURE mob impact {EntityId} on {TargetCharacterId} " +
                            "did not land: {BlockedReason}",
                            impact.EntityId, impact.TargetCharacterId, impact.BlockedReason);
                        continue;
                    }

                    _logger.LogInformation(
                        "DEV FIXTURE mob impact {EntityId} attack {AttackId} on " +
                        "{TargetCharacterId}: {Damage} ({HpBefore} -> {HpAfter})",
                        impact.EntityId, impact.AttackId, impact.TargetCharacterId,
                        impact.Damage, impact.HpBefore, impact.HpAfter);
                }
            }
        }
    }
}
