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
        ServerClock clock)
    {
        _entities = entities;
        _combat = combat;
        _skills = skills;
        _events = events;
        _states = states;
        _quests = quests;
        _rolls = rolls;
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
                    // SK-MK-01 keeps its DEC-022 guard window; counter runtime
                    // (with mob attacks) is a separate increment.
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
            return true;
        }
    }

    // Advances every scheduled cast up to (and including) the given tick and
    // returns the authoritative events emitted on this call.
    public IReadOnlyList<CombatEventV2> Tick(long tick)
    {
        var emitted = new List<CombatEventV2>();
        lock (_sync)
        {
            if (_casts.Count == 0)
            {
                return emitted;
            }

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

        return emitted;
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
