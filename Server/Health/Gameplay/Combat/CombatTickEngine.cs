using System.Collections.Concurrent;
using Server.Health.Contracts;
using Server.Health.Gameplay.Quests;
using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// QOD-17 tick combat: accepted casts resolve on the real 20 Hz tick. One
// command is one hit (basic attack combo = three commands, not three hits per
// press); MK03 resolves its three authored hits on their own ticks. The
// P1 actor stats are the labelled completion_v1 baseline (attack 20, armor 10,
// accuracy 0.0025, crit 0.0525) — not playtest balance.
public static class CombatActorBaseline
{
    public const double Attack = 20;
    public const double Armor = 10;
    public const double Accuracy = 0.0025;
    public const double Dodge = 0.0015;
    public const double CritChance = 0.0525;
    public const int MobReferenceLevel = 5;
}

public enum CombatRollKind
{
    Hit,
    Crit
}

public interface ICombatRollSource
{
    bool Roll(string castId, string targetId, int hitIndex, CombatRollKind kind, double probability);
}

public sealed class CombatRngRollSource : ICombatRollSource
{
    public bool Roll(string castId, string targetId, int hitIndex, CombatRollKind kind, double probability)
    {
        // Separate RNG channel per roll kind so a hit roll and its crit roll do
        // not share the same uniform value for the same (cast, target, hit).
        var seed = kind == CombatRollKind.Crit ? castId + "|crit" : castId;
        return CombatRng.Roll(seed, targetId, hitIndex, probability);
    }
}

public sealed record MobCombatState(int Hp, long LifeId, string? LastDamagerId);

// Per-entity life-scoped HP. A respawn bumps WorldEntityInstance.LifeId and the
// state resets on first use with the new life; dead lives never carry HP over.
public sealed class MobCombatStateStore
{
    private readonly ConcurrentDictionary<string, MobCombatState> _states =
        new(StringComparer.Ordinal);

    public MobCombatState Ensure(string entityId, long lifeId, int maxHp)
    {
        var candidate = new MobCombatState(maxHp, lifeId, null);
        var current = _states.AddOrUpdate(
            entityId,
            candidate,
            (_, existing) => existing.LifeId == lifeId ? existing : candidate);
        return current;
    }

    public MobCombatState? TryGet(string entityId, long lifeId)
    {
        return _states.TryGetValue(entityId, out var state) && state.LifeId == lifeId
            ? state
            : null;
    }

    public (int RemainingHp, bool Died, string ActorId) ApplyDamage(
        string entityId, long lifeId, int maxHp, int damage, string actorId)
    {
        var state = Ensure(entityId, lifeId, maxHp);
        var remaining = Math.Max(0, state.Hp - Math.Max(0, damage));
        var died = remaining == 0;
        _states[entityId] = new MobCombatState(remaining, lifeId, actorId);
        return (remaining, died, actorId);
    }

    public bool Remove(string entityId) => _states.TryRemove(entityId, out _);
}

public sealed class CombatTickEngine
{
    public const int BasicAttackRangeWu = 4;
    public const int BasicAttackAngleDegrees = 90;
    public const string SkMk01 = "SK-MK-01";
    public const string SkMk03 = "SK-MK-03";

    private static readonly int[] BasicHitTicks = [3];
    private static readonly double[] BasicCoefficients = [1.0];
    private static readonly int[] Mk03HitTicks = [2, 5, 8];
    private static readonly double[] Mk03Coefficients = [0.45, 0.55, 0.90];

    private readonly WorldEntityRegistry _entities;
    private readonly CombatDamageFeature _combat;
    private readonly ICombatSkillCatalog _skills;
    private readonly CombatEventStore _events;
    private readonly MobCombatStateStore _states;
    private readonly IQuestService _quests;
    private readonly ICombatRollSource _rolls;
    private readonly GuardWindowStore _guards;
    private readonly IWorldGeometryService _geometry;
    private readonly ServerClock _clock;
    private readonly object _sync = new();
    private readonly Dictionary<string, ScheduledCast> _casts = new(StringComparer.Ordinal);

    public CombatTickEngine(
        WorldEntityRegistry entities,
        CombatDamageFeature combat,
        ICombatSkillCatalog skills,
        CombatEventStore events,
        MobCombatStateStore states,
        IQuestService quests,
        ICombatRollSource rolls,
        GuardWindowStore guards,
        IWorldGeometryService geometry,
        ServerClock clock)
    {
        _entities = entities;
        _combat = combat;
        _skills = skills;
        _events = events;
        _states = states;
        _quests = quests;
        _rolls = rolls;
        _guards = guards;
        _geometry = geometry;
        _clock = clock;
    }

    public int ScheduledCastCount
    {
        get
        {
            lock (_sync)
            {
                return _casts.Count;
            }
        }
    }

    // Schedules an accepted cast. Returns false when the same castId is
    // already scheduled (idempotent replay must never double-resolve).
    public bool Schedule(
        PlayerSession actor,
        string sessionId,
        string castId,
        string actionKind,
        string? skillId,
        double aimX,
        double aimY,
        long startTick)
    {
        int[] hitTicks;
        double[] coefficients;
        double rangeWu;
        double angleDegrees;
        var maxTargets = 0;
        CombatSkillDefinition? skill = null;

        if (string.Equals(actionKind, CombatV2Actions.BasicAttack, StringComparison.Ordinal))
        {
            hitTicks = BasicHitTicks;
            coefficients = BasicCoefficients;
            rangeWu = BasicAttackRangeWu;
            angleDegrees = BasicAttackAngleDegrees;
            maxTargets = 1;
        }
        else
        {
            if (skillId is null || !_skills.TryGet(skillId, out skill))
            {
                return false;
            }

            switch (skill.SkillId)
            {
                case SkMk03:
                    hitTicks = Mk03HitTicks;
                    coefficients = Mk03Coefficients;
                    rangeWu = skill.RangeWu ?? 4.4;
                    angleDegrees = skill.AngleDegrees ?? 100;
                    maxTargets = skill.MaxTargets;
                    break;
                case "SK-MK-02":
                    // Dash movement carries no damage in the supported subset.
                    hitTicks = [];
                    coefficients = [];
                    rangeWu = skill.RangeWu ?? 11;
                    angleDegrees = skill.AngleDegrees ?? 0;
                    break;
                default:
                    // SK-MK-01 keeps its DEC-022 guard window; the window itself
                    // opens below, the counter resolves on the tick engine.
                    hitTicks = [];
                    coefficients = [];
                    rangeWu = skill.RangeWu ?? 4.4;
                    angleDegrees = skill.AngleDegrees ?? 120;
                    break;
            }
        }

        var (facingX, facingY) = Normalize(aimX, aimY);
        lock (_sync)
        {
            if (_casts.ContainsKey(castId))
            {
                return false;
            }

            _casts[castId] = new ScheduledCast(
                castId,
                sessionId,
                actor,
                actor.CharacterId,
                actor.MapId,
                actor.FloorId,
                actor.X,
                actor.Y,
                facingX,
                facingY,
                actor.Revision,
                startTick,
                hitTicks,
                coefficients,
                rangeWu,
                angleDegrees,
                maxTargets,
                skill?.SkillId);

            if (skill is { SkillId: SkMk01 })
            {
                OpenGuardWindow(actor, sessionId, castId, skill, facingX, facingY, startTick);
            }

            return true;
        }
    }

    // DEC-022 §2: the window attaches to the cast tick with the accepted facing
    // snapshot. A re-cast refreshes the single window instead of stacking a
    // second reduction source (SKILL_REFRESH_NO_ADD).
    private void OpenGuardWindow(
        PlayerSession actor,
        string sessionId,
        string castId,
        CombatSkillDefinition skill,
        double facingX,
        double facingY,
        long startTick)
    {
        if (!_combat.Enabled)
        {
            return;
        }

        var bundle = _combat.GuardPrecision;
        _guards.Open(new GuardWindowState
        {
            Defender = actor,
            SessionId = sessionId,
            GuardCastId = castId,
            CastStartTick = startTick,
            FacingX = facingX,
            FacingY = facingY,
            AttackSnapshot = CombatActorBaseline.Attack,
            CounterCoefficient = skill.Coefficients.Pve,
            MapId = actor.MapId,
            FloorId = actor.FloorId,
            GuardDurationTicks = bundle.Guard.DurationTicks,
            WhiffDurationTicks = bundle.Whiff.DurationTicks
        });
    }

    // Advances every scheduled cast up to (and including) the given tick and
    // returns the authoritative events emitted on this call.
    public IReadOnlyList<CombatEventV2> Tick(long tick)
    {
        var emitted = new List<CombatEventV2>();
        lock (_sync)
        {
            if (_casts.Count > 0)
            {
                var finished = new List<string>();
                foreach (var cast in _casts.Values)
                {
                    while (cast.NextHitIndex < cast.HitTicks.Length &&
                           cast.StartTick + cast.HitTicks[cast.NextHitIndex] <= tick)
                    {
                        var hitIndex = cast.NextHitIndex;
                        var impactTick = cast.StartTick + cast.HitTicks[hitIndex];
                        cast.NextHitIndex++;
                        emitted.AddRange(ResolveHit(cast, hitIndex, impactTick));
                    }

                    if (cast.NextHitIndex >= cast.HitTicks.Length && tick >= cast.EndTick())
                    {
                        emitted.Add(AppendEnd(cast, tick));
                        finished.Add(cast.CastId);
                    }
                }

                foreach (var castId in finished)
                {
                    _casts.Remove(castId);
                }
            }

            // A reserved counter resolves on its own tick even when no player
            // cast is in flight (DEC-022 §3: counter at the tick after the
            // confirmation, never inside the hit stack that produced it).
            foreach (var window in _guards.PendingCounters(tick)
                         .OrderBy(state => state.Defender.CharacterId, StringComparer.Ordinal)
                         .ToArray())
            {
                window.CounterResolved = true;
                emitted.AddRange(ResolveCounter(window, tick));
            }
        }

        return emitted;
    }

    // DEC-022 §3 counter resolution: one reserved swing at the confirmed source,
    // with every recheck re-run at the counter tick. No retarget, no refund, no
    // new confirmation and no recursive counter.
    private IEnumerable<CombatEventV2> ResolveCounter(GuardWindowState window, long tick)
    {
        if (!_combat.Enabled)
        {
            yield break;
        }

        var defender = window.Defender;
        var counter = _combat.GuardPrecision.Counter;
        var sourceId = window.CounterSourceEntityId!;
        var sourceLifeId = window.CounterSourceLifeId ?? 0;

        if (defender.Hp <= 0)
        {
            yield return CancelCounter(window, tick, sourceId, sourceLifeId, "DEFENDER_DOWN");
            yield break;
        }

        if (!window.IsOpen)
        {
            yield return CancelCounter(
                window, tick, sourceId, sourceLifeId, "WINDOW_CLOSED_" + window.EndReason);
            yield break;
        }

        if (!_entities.TryGet(sourceId, out var source) ||
            !string.Equals(source.State, WorldEntityStates.Alive, StringComparison.Ordinal))
        {
            yield return CancelCounter(window, tick, sourceId, sourceLifeId, "SOURCE_NOT_ALIVE");
            yield break;
        }

        if (source.LifeId != sourceLifeId)
        {
            yield return CancelCounter(window, tick, sourceId, sourceLifeId, "SOURCE_NEW_LIFE");
            yield break;
        }

        if (!string.Equals(source.Kind, WorldEntityKinds.Mob, StringComparison.Ordinal))
        {
            yield return CancelCounter(window, tick, sourceId, source.LifeId, "SOURCE_NOT_HOSTILE");
            yield break;
        }

        if (!string.Equals(source.MapId, defender.MapId, StringComparison.Ordinal) ||
            !string.Equals(source.FloorId, defender.FloorId, StringComparison.Ordinal))
        {
            yield return CancelCounter(window, tick, sourceId, source.LifeId, "SOURCE_LEFT_INSTANCE");
            yield break;
        }

        if (!GuardTimeline.InFront(
                defender.X, defender.Y,
                window.FacingX, window.FacingY,
                source.X, source.Y,
                counter.RangeWu, counter.AngleDegrees))
        {
            yield return CancelCounter(window, tick, sourceId, source.LifeId, "OUT_OF_RANGE_OR_CONE");
            yield break;
        }

        if (_geometry.CheckLineOfSight(
                defender.MapId, defender.FloorId,
                defender.X, defender.Y, source.X, source.Y).IsBlocked)
        {
            yield return CancelCounter(window, tick, sourceId, source.LifeId, "LOS_BLOCKED");
            yield break;
        }

        var stats = ResolveMobStats(source);
        if (stats is not { Hp: > 0 })
        {
            yield return CancelCounter(window, tick, sourceId, source.LifeId, "SOURCE_INVULNERABLE");
            yield break;
        }

        // Counter rolls use their own RNG channel so a guard never inherits the
        // roll outcome of the hit that confirmed it (DEC-022 §3).
        var counterSeed = window.GuardCastId + "|counter";
        var hitProbability = DamageFormula.HitProbability(
            CombatActorBaseline.Accuracy, CombatActorBaseline.Dodge);
        if (!_rolls.Roll(counterSeed, source.EntityId, 0, CombatRollKind.Hit, hitProbability))
        {
            window.CounterOutcome = "MISS";
            yield return AppendGuardEvent(
                window, tick, CombatEventTypesV2.Miss, source,
                new CombatEventResultV2(false, false, false, 0, 0, 0));
            yield break;
        }

        var critProbability = DamageFormula.AttributeCritChance(luk: 5, gearCrit: 0, cap: 0.5);
        var crit = _rolls.Roll(
            counterSeed, source.EntityId, 0, CombatRollKind.Crit, critProbability);
        var raw = DamageFormula.RawDamage(
            window.AttackSnapshot, 0, window.CounterCoefficient, 1, 0);
        var amount = (int)DamageFormula.FinalDamage(
            raw,
            DamageFormula.MitigationMultiplier(stats.Defense),
            1,
            crit ? DamageFormula.CritMultiplier : 1,
            1);

        var current = _states.Ensure(source.EntityId, source.LifeId, stats.Hp);
        if (current.Hp <= 0)
        {
            yield return CancelCounter(
                window, tick, sourceId, source.LifeId, "SOURCE_DEAD_THIS_TICK");
            yield break;
        }

        var hpBefore = current.Hp;
        var (remaining, died, _) = _states.ApplyDamage(
            source.EntityId, source.LifeId, stats.Hp, amount, defender.CharacterId);
        window.CounterOutcome = "DAMAGE";

        yield return AppendGuardEvent(
            window, tick, CombatEventTypesV2.Impact, source,
            new CombatEventResultV2(true, crit, false, amount, 0, Math.Min(amount, hpBefore)));

        if (!died)
        {
            yield break;
        }

        _entities.Despawn(source.EntityId);
        var death = AppendGuardEvent(
            window, tick, CombatEventTypesV2.Death, source, result: null);
        yield return death;

        _quests.RecordVerifiedEvent(
            defender, death.EventId, QuestProgressEventTypes.Kill, source.RecordId, source.MapId);
    }

    private CombatEventV2 CancelCounter(
        GuardWindowState window, long tick, string sourceId, long sourceLifeId, string reason)
    {
        window.CounterOutcome = reason;
        var known = _entities.TryGet(sourceId, out var entity);
        return AppendGuardEvent(
            window,
            tick,
            CombatEventTypesV2.Cancel,
            known ? entity.EntityId : sourceId,
            known ? entity.LifeId : sourceLifeId,
            hitIndex: null,
            known ? entity.Revision : null,
            result: null);
    }

    private CombatEventV2 AppendGuardEvent(
        GuardWindowState window,
        long tick,
        string type,
        WorldEntityInstance source,
        CombatEventResultV2? result) =>
        AppendGuardEvent(
            window,
            tick,
            type,
            source.EntityId,
            source.LifeId,
            type == CombatEventTypesV2.Impact || type == CombatEventTypesV2.Miss ? 0 : null,
            source.Revision,
            result);

    private CombatEventV2 AppendGuardEvent(
        GuardWindowState window,
        long tick,
        string type,
        string targetId,
        long targetLifeId,
        int? hitIndex,
        long? targetRevision,
        CombatEventResultV2? result)
    {
        var defender = window.Defender;
        return _events.Append(
            window.SessionId,
            new CombatEventV2(
                Guid.NewGuid().ToString("N"),
                type,
                window.GuardCastId,
                defender.CharacterId,
                targetId,
                targetLifeId,
                hitIndex,
                defender.MapId + WorldAudience.MapInstanceSuffix,
                defender.FloorId,
                defender.Revision,
                targetRevision,
                tick,
                _clock.UtcNow,
                result));
    }

    private IEnumerable<CombatEventV2> ResolveHit(
        ScheduledCast cast, int hitIndex, long impactTick)
    {
        var targets = SelectTargets(cast);
        if (targets.Count == 0)
        {
            yield break;
        }

        var maybeBundle = _combat.Enabled;
        foreach (var target in targets)
        {
            var lifeId = target.LifeId;
            if (!string.Equals(target.State, WorldEntityStates.Alive, StringComparison.Ordinal))
            {
                continue;
            }

            var stats = maybeBundle ? ResolveMobStats(target) : null;
            var maxHp = stats?.Hp ?? 0;
            if (maxHp <= 0)
            {
                continue;
            }

            var defense = stats?.Defense ?? 0;
            var state = _states.Ensure(target.EntityId, lifeId, maxHp);
            if (state.Hp <= 0)
            {
                continue;
            }

            var hitProbability = DamageFormula.HitProbability(
                CombatActorBaseline.Accuracy, CombatActorBaseline.Dodge);
            if (!_rolls.Roll(cast.CastId, target.EntityId, hitIndex, CombatRollKind.Hit, hitProbability))
            {
                yield return AppendEvent(
                    cast, impactTick, CombatEventTypesV2.Miss, target.EntityId, lifeId,
                    hitIndex, target.Revision,
                    new CombatEventResultV2(false, false, false, 0, 0, 0));
                continue;
            }

            var critProbability = DamageFormula.AttributeCritChance(
                luk: 5, gearCrit: 0, cap: 0.5);
            var crit = _rolls.Roll(
                cast.CastId, target.EntityId, hitIndex, CombatRollKind.Crit, critProbability);
            var raw = DamageFormula.RawDamage(
                CombatActorBaseline.Attack, 0, cast.Coefficients[hitIndex], 1, 0);
            var amount = (int)DamageFormula.FinalDamage(
                raw,
                DamageFormula.MitigationMultiplier(defense),
                1,
                crit ? DamageFormula.CritMultiplier : 1,
                1);

            var hpBefore = state.Hp;
            var (remaining, died, _) = _states.ApplyDamage(
                target.EntityId, lifeId, maxHp, amount, cast.Actor.CharacterId);
            var hpDamage = Math.Min(amount, hpBefore);

            yield return AppendEvent(
                cast, impactTick, CombatEventTypesV2.Impact, target.EntityId, lifeId,
                hitIndex, target.Revision,
                new CombatEventResultV2(true, crit, false, amount, 0, hpDamage));

            if (!died)
            {
                continue;
            }

            _entities.Despawn(target.EntityId);
            var deathEvent = AppendEvent(
                cast, impactTick + 1, CombatEventTypesV2.Death, target.EntityId, lifeId,
                hitIndex: null, target.Revision, result: null);
            yield return deathEvent;

            // QOD-17 DEV kill-credit policy: the source that lands the killing
            // HP damage gets the kill, keyed by the death event id so a replay
            // never double-counts the same life.
            _quests.RecordVerifiedEvent(
                cast.Actor,
                deathEvent.EventId,
                QuestProgressEventTypes.Kill,
                target.RecordId,
                target.MapId);
        }
    }

    private List<WorldEntityInstance> SelectTargets(ScheduledCast cast)
    {
        var targets = new List<(WorldEntityInstance Entity, double Distance)>();
        foreach (var entity in _entities.All)
        {
            if (!string.Equals(entity.Kind, WorldEntityKinds.Mob, StringComparison.Ordinal) ||
                !string.Equals(entity.State, WorldEntityStates.Alive, StringComparison.Ordinal) ||
                !string.Equals(entity.MapId, cast.MapId, StringComparison.Ordinal) ||
                !string.Equals(entity.FloorId, cast.FloorId, StringComparison.Ordinal))
            {
                continue;
            }

            if (!GuardTimeline.InFront(
                    cast.OriginX, cast.OriginY,
                    cast.FacingX, cast.FacingY,
                    entity.X, entity.Y,
                    cast.RangeWu, cast.AngleDegrees))
            {
                continue;
            }

            var deltaX = entity.X - cast.OriginX;
            var deltaY = entity.Y - cast.OriginY;
            targets.Add((entity, Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY))));
        }

        return targets
            .OrderBy(item => item.Distance)
            .ThenBy(item => item.Entity.EntityId, StringComparer.Ordinal)
            .Take(cast.MaxTargets)
            .Select(item => item.Entity)
            .ToList();
    }

    private MobEffectiveStats? ResolveMobStats(WorldEntityInstance entity)
    {
        var templateId = entity.TemplateIds.FirstOrDefault();
        if (templateId is null)
        {
            return null;
        }

        var bundle = _combat.MobStats;
        var archetypeId = templateId.EndsWith("_ELITE", StringComparison.Ordinal)
            ? templateId[..^"_ELITE".Length]
            : templateId;
        var archetype = bundle.Archetypes.FirstOrDefault(
            stats => string.Equals(stats.MobId, archetypeId, StringComparison.Ordinal));
        if (archetype is null)
        {
            return null;
        }

        var statsAtLevel = CombatMobStatLoader.EffectiveAt(
            bundle, archetypeId, CombatActorBaseline.MobReferenceLevel);
        if (!templateId.EndsWith("_ELITE", StringComparison.Ordinal))
        {
            return statsAtLevel;
        }

        return new MobEffectiveStats(
            checked((int)Math.Round(statsAtLevel.Hp * bundle.Elite.Hp)),
            statsAtLevel.Attack * bundle.Elite.Attack,
            statsAtLevel.Defense * bundle.Elite.Defense);
    }

    private CombatEventV2 AppendEnd(ScheduledCast cast, long tick) =>
        AppendEvent(
            cast, tick, CombatEventTypesV2.End, targetId: null, targetLifeId: null,
            hitIndex: null, targetRevision: null, result: null);

    private CombatEventV2 AppendEvent(
        ScheduledCast cast,
        long tick,
        string type,
        string? targetId,
        long? targetLifeId,
        int? hitIndex,
        long? targetRevision,
        CombatEventResultV2? result) =>
        _events.Append(
            cast.SessionId,
            new CombatEventV2(
                Guid.NewGuid().ToString("N"),
                type,
                cast.CastId,
                cast.ActorId,
                targetId,
                targetLifeId,
                hitIndex,
                cast.MapId + WorldAudience.MapInstanceSuffix,
                cast.FloorId,
                cast.SourceRevision,
                targetRevision,
                tick,
                _clock.UtcNow,
                result));

    private static (double X, double Y) Normalize(double x, double y)
    {
        var length = Math.Sqrt((x * x) + (y * y));
        return length <= 1e-9 ? (1, 0) : (x / length, y / length);
    }

    private sealed class ScheduledCast
    {
        public ScheduledCast(
            string castId,
            string sessionId,
            PlayerSession actor,
            string actorId,
            string mapId,
            string floorId,
            double originX,
            double originY,
            double facingX,
            double facingY,
            long sourceRevision,
            long startTick,
            int[] hitTicks,
            double[] coefficients,
            double rangeWu,
            double angleDegrees,
            int maxTargets,
            string? skillId)
        {
            CastId = castId;
            SessionId = sessionId;
            Actor = actor;
            ActorId = actorId;
            MapId = mapId;
            FloorId = floorId;
            OriginX = originX;
            OriginY = originY;
            FacingX = facingX;
            FacingY = facingY;
            SourceRevision = sourceRevision;
            StartTick = startTick;
            HitTicks = hitTicks;
            Coefficients = coefficients;
            RangeWu = rangeWu;
            AngleDegrees = angleDegrees;
            MaxTargets = maxTargets;
            SkillId = skillId;
        }

        public string CastId { get; }
        public string SessionId { get; }
        public PlayerSession Actor { get; }
        public string ActorId { get; }
        public string MapId { get; }
        public string FloorId { get; }
        public double OriginX { get; }
        public double OriginY { get; }
        public double FacingX { get; }
        public double FacingY { get; }
        public long SourceRevision { get; }
        public long StartTick { get; }
        public int[] HitTicks { get; }
        public double[] Coefficients { get; }
        public double RangeWu { get; }
        public double AngleDegrees { get; }
        public int MaxTargets { get; }
        public string? SkillId { get; }
        public int NextHitIndex { get; set; }

        public long EndTick() => HitTicks.Length > 0
            ? StartTick + HitTicks[^1] + 1
            : StartTick + 2;
    }
}
