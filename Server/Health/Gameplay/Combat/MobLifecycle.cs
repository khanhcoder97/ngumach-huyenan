using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

public static class MobBehaviorStates
{
    public const string Idle = "IDLE";
    public const string Aggro = "AGGRO";
    public const string Chase = "CHASE";
    public const string Attack = "ATTACK";
    public const string Return = "RETURN";
    public const string Dead = "DEAD";
}

// DEV FIXTURE values only: canonical mob HP/ATK/range numbers are not locked in
// content, so these knobs must stay labelled and must not be treated as balance.
public sealed class MobBehaviorOptions
{
    public const string SectionName = "P1:MobBehavior";

    public bool Enabled { get; set; }

    public double AggroRadiusWu { get; set; } = 6;

    public double LeashRadiusWu { get; set; } = 12;

    public double AttackRangeWu { get; set; } = 1.2;

    public double AttackCooldownSeconds { get; set; } = 2;

    public double MoveSpeedWuPerSecond { get; set; } = 2;
}

public static class MobBehaviorOptionsValidator
{
    public static void Validate(MobBehaviorOptions options)
    {
        if (!double.IsFinite(options.AggroRadiusWu) || options.AggroRadiusWu <= 0 ||
            !double.IsFinite(options.LeashRadiusWu) || options.LeashRadiusWu <= 0 ||
            !double.IsFinite(options.AttackRangeWu) || options.AttackRangeWu <= 0 ||
            !double.IsFinite(options.AttackCooldownSeconds) || options.AttackCooldownSeconds <= 0 ||
            !double.IsFinite(options.MoveSpeedWuPerSecond) || options.MoveSpeedWuPerSecond <= 0)
        {
            throw new InvalidOperationException(
                "P1:MobBehavior radii, cooldown and speed must be greater than zero.");
        }
    }
}

public sealed record MobLifecycleEvent(
    string EntityId,
    string FromState,
    string ToState,
    DateTimeOffset AtUtc,
    string? TargetCharacterId);

public sealed class MobLifecycleService
{
    private const string GroundFloor = "OVERWORLD";

    private readonly WorldEntityRegistry _entities;
    private readonly IWorldGeometryService _geometry;
    private readonly MobBehaviorOptions _options;
    private readonly IServerClock _clock;
    private readonly Dictionary<string, MobBrain> _brains = new(StringComparer.Ordinal);
    private DateTimeOffset? _lastTickAtUtc;

    public MobLifecycleService(
        WorldEntityRegistry entities,
        IWorldGeometryService geometry,
        MobBehaviorOptions options,
        IServerClock clock)
    {
        _entities = entities;
        _geometry = geometry;
        _options = options;
        _clock = clock;
    }

    public string GetState(string entityId) =>
        _brains.TryGetValue(entityId, out var brain)
            ? brain.State
            : MobBehaviorStates.Idle;

    public IReadOnlyList<MobLifecycleEvent> Tick(IReadOnlyList<PlayerSession> players)
    {
        var now = _clock.UtcNow;
        var deltaSeconds = _lastTickAtUtc is { } last
            ? Math.Clamp((now - last).TotalSeconds, 0, 1)
            : 0;
        _lastTickAtUtc = now;

        _entities.Update();

        var events = new List<MobLifecycleEvent>();
        foreach (var entity in _entities.All)
        {
            if (!string.Equals(entity.Kind, WorldEntityKinds.Mob, StringComparison.Ordinal) &&
                !string.Equals(entity.Kind, WorldEntityKinds.Boss, StringComparison.Ordinal))
            {
                continue;
            }

            var brain = GetBrain(entity);
            if (!string.Equals(entity.State, WorldEntityStates.Alive, StringComparison.Ordinal))
            {
                Transition(entity, brain, MobBehaviorStates.Dead, now, null, events);
                continue;
            }

            if (string.Equals(brain.State, MobBehaviorStates.Dead, StringComparison.Ordinal))
            {
                Transition(entity, brain, MobBehaviorStates.Idle, now, null, events);
                brain.TargetCharacterId = null;
            }

            var target = FindTarget(entity, players);
            if (target is null)
            {
                brain.TargetCharacterId = null;
                if (string.Equals(brain.State, MobBehaviorStates.Return, StringComparison.Ordinal))
                {
                    if (MoveToward(entity, brain.HomeX, brain.HomeY, deltaSeconds, brain))
                    {
                        Transition(entity, brain, MobBehaviorStates.Idle, now, null, events);
                    }

                    continue;
                }

                if (string.Equals(brain.State, MobBehaviorStates.Attack, StringComparison.Ordinal) ||
                    string.Equals(brain.State, MobBehaviorStates.Chase, StringComparison.Ordinal) ||
                    string.Equals(brain.State, MobBehaviorStates.Aggro, StringComparison.Ordinal))
                {
                    Transition(entity, brain, MobBehaviorStates.Return, now, null, events);
                }

                continue;
            }

            brain.TargetCharacterId = target.CharacterId;
            var targetDistanceFromHome =
                Distance(target.X, target.Y, brain.HomeX, brain.HomeY);
            if (targetDistanceFromHome > _options.LeashRadiusWu)
            {
                Transition(entity, brain, MobBehaviorStates.Return, now, target.CharacterId, events);
                continue;
            }

            var distanceToTarget = Distance(entity.X, entity.Y, target.X, target.Y);
            if (string.Equals(brain.State, MobBehaviorStates.Idle, StringComparison.Ordinal))
            {
                Transition(entity, brain, MobBehaviorStates.Aggro, now, target.CharacterId, events);
            }
            else if (string.Equals(brain.State, MobBehaviorStates.Aggro, StringComparison.Ordinal) ||
                     string.Equals(brain.State, MobBehaviorStates.Return, StringComparison.Ordinal))
            {
                Transition(entity, brain, MobBehaviorStates.Chase, now, target.CharacterId, events);
            }

            if (distanceToTarget <= _options.AttackRangeWu)
            {
                if (string.Equals(brain.State, MobBehaviorStates.Chase, StringComparison.Ordinal))
                {
                    Transition(entity, brain, MobBehaviorStates.Attack, now, target.CharacterId, events);
                }

                if (string.Equals(brain.State, MobBehaviorStates.Attack, StringComparison.Ordinal) &&
                    (brain.NextAttackAtUtc is null || now >= brain.NextAttackAtUtc))
                {
                    brain.NextAttackAtUtc = now.AddSeconds(_options.AttackCooldownSeconds);
                    events.Add(new MobLifecycleEvent(
                        entity.EntityId,
                        MobBehaviorStates.Attack,
                        MobBehaviorStates.Attack,
                        now,
                        target.CharacterId));
                }

                continue;
            }

            if (string.Equals(brain.State, MobBehaviorStates.Chase, StringComparison.Ordinal))
            {
                MoveToward(entity, target.X, target.Y, deltaSeconds, brain);
            }
        }

        return events;
    }

    private CombatTarget? FindTarget(WorldEntityInstance entity, IReadOnlyList<PlayerSession> players)
    {
        PlayerSession? best = null;
        var bestDistance = double.MaxValue;
        foreach (var player in players)
        {
            if (player.Hp <= 0 ||
                !string.Equals(player.MapId, entity.MapId, StringComparison.Ordinal) ||
                !string.Equals(player.FloorId, entity.FloorId, StringComparison.Ordinal))
            {
                continue;
            }

            var distance = Distance(entity.X, entity.Y, player.X, player.Y);
            if (distance > _options.AggroRadiusWu || distance >= bestDistance)
            {
                continue;
            }

            var line = _geometry.CheckLineOfSight(
                entity.MapId, entity.FloorId, entity.X, entity.Y, player.X, player.Y);
            if (line.IsBlocked)
            {
                continue;
            }

            best = player;
            bestDistance = distance;
        }

        return best is null
            ? null
            : new CombatTarget(best.CharacterId, best.MapId, best.FloorId, best.X, best.Y, Alive: true);
    }

    private bool MoveToward(
        WorldEntityInstance entity, double toX, double toY, double deltaSeconds, MobBrain brain)
    {
        var distance = Distance(entity.X, entity.Y, toX, toY);
        if (distance <= 1e-6)
        {
            return true;
        }

        var step = Math.Min(_options.MoveSpeedWuPerSecond * deltaSeconds, distance);
        if (step <= 0)
        {
            return false;
        }

        var nextX = entity.X + ((toX - entity.X) / distance * step);
        var nextY = entity.Y + ((toY - entity.Y) / distance * step);
        var sweep = _geometry.CheckWalkSegment(
            entity.MapId, entity.FloorId, entity.X, entity.Y, nextX, nextY, footprintRadiusWu: 0);
        if (sweep.IsBlocked)
        {
            return false;
        }

        if (Distance(nextX, nextY, brain.HomeX, brain.HomeY) > _options.LeashRadiusWu)
        {
            return false;
        }

        entity.MoveTo(nextX, nextY);
        return Distance(entity.X, entity.Y, toX, toY) <= 1e-6;
    }

    private MobBrain GetBrain(WorldEntityInstance entity)
    {
        if (!_brains.TryGetValue(entity.EntityId, out var brain))
        {
            brain = new MobBrain(entity.X, entity.Y);
            _brains[entity.EntityId] = brain;
        }

        return brain;
    }

    private static void Transition(
        WorldEntityInstance entity,
        MobBrain brain,
        string toState,
        DateTimeOffset now,
        string? targetCharacterId,
        List<MobLifecycleEvent> events)
    {
        if (string.Equals(brain.State, toState, StringComparison.Ordinal))
        {
            return;
        }

        var fromState = brain.State;
        brain.State = toState;
        events.Add(new MobLifecycleEvent(
            entity.EntityId, fromState, toState, now, targetCharacterId));
    }

    private static double Distance(double ax, double ay, double bx, double by) =>
        Math.Sqrt(((bx - ax) * (bx - ax)) + ((by - ay) * (by - ay)));

    private sealed class MobBrain
    {
        public MobBrain(double homeX, double homeY)
        {
            HomeX = homeX;
            HomeY = homeY;
        }

        public double HomeX { get; }
        public double HomeY { get; }
        public string State { get; set; } = MobBehaviorStates.Idle;
        public string? TargetCharacterId { get; set; }
        public DateTimeOffset? NextAttackAtUtc { get; set; }
    }
}
