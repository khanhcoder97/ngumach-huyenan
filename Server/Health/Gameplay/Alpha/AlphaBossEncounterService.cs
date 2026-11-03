using Server.Health.Contracts;
using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Quests;
using Server.Health.World;

namespace Server.Health.Gameplay.Alpha;

public static class BossEncounterOutcomeCodes
{
    public const string Registered = "REGISTERED";
    public const string Telegraph = "TELEGRAPH";
    public const string Impact = "IMPACT";
    public const string ImpactBlocked = "IMPACT_BLOCKED";
    public const string PhaseChanged = "PHASE_CHANGED";
    public const string Wiped = "WIPED";
    public const string Defeated = "DEFEATED";
    public const string Ended = "ENDED";
}

public sealed record BossEncounterResolution(
    string CharacterId,
    string Outcome,
    string? Detail,
    int Phase,
    int BossHp,
    int Damage,
    int HpBefore,
    int HpAfter);

// QOD-21 Q2: the real Mãng Cốt encounter (DESIGN-BM-ALPHA-20261103 `boss`) as a
// 20 Hz tickable machine behind P1:AlphaProfile:Enabled, running on the Q-F
// phase machine. There is no approved wire surface yet — the read-only
// snapshot is proposed in
// Implementation/Work_Orders/Proposals/QOD-21_EncounterSnapshot_Contract_Packet_20261103_vi.md
// — so this is domain-only: the boss HP, the move timeline, the phase
// transitions, the wipe countdown and the P00-05 quest-instance overrides live
// server-side and the self-check exercises them deterministically.
//
// Sourced values (never defaulted): profile BOSS_MANG_COT_QUEST_ALPHA_1 on
// entity BOSS_MANG_COT (level 5, HP 1200, attack 24, armor 6), arena CIRCLE
// center (178,0) radius 11, phase thresholds 0.6/0.3 with at most one
// transition per impact, phase guard 1.0 s, phase-2 recovery multiplier 0.8,
// phase-3 additional damage multiplier 1.0, priority C→B→A, no overlap, moves
// A "Quật Thân" CONE 120°/8 WU windup 0.9 coeff 1.2 recovery 0.8 cooldown 4
// (locked to the telegraph-start facing), B "Lặn Trồi" CIRCLE r4 around the
// telegraph-start target position, windup 1.2 coeff 1.5 recovery 1 cooldown 9
// (submerge is cosmetic, not invulnerability), C "Vòng Bọt" ANNULUS 3–7 WU
// around the boss, windup 1.0 coeff 1.3 recovery 1 cooldown 12, uninterruptible
// and dodgeable; wipe after 10 s with no alive target resets HP and phase 1,
// persists the quest checkpoint, invalidates the old cast generation, starts a
// fresh life and pays no loot. Credit: only the owner registered at encounter
// start who is still eligible at death; late join and prior-life events give
// none, and party scaling stays off until a roster authority exists.
//
// Interpretations recorded rather than invented:
// - P1 has no party and no separate instance runtime, so an encounter is
//   owner-specific (one canonical boss per registering owner, the same rule the
//   escort uses) and "in the quest instance" means "this machine holds a live
//   instance for that owner". While any instance is held, the other record at
//   (178,0) — `worldEventRecordIdDisabledInQuestInstance` =
//   MAN-BM-EVENT_BOSS_BM_MANG_COT — is held despawned, so the duplicate the Q-F
//   proposal filed never coexists with the quest boss for that player.
// - Move B's `targetRangeWu` 11 gate is satisfied by construction: an owner
//   only keeps the encounter while inside the arena (radius 11) with the boss at
//   the arena centre, so no extra range rejection is invented here.
// - `safePads` (168,0)/(188,0) r 0.75, `phase3Only`, `noInvulnerability` are
//   snapshot data: no source states a mechanical effect for them, so the
//   machine applies nothing (the packet exposes them for the client to draw).
// - Player damage reaches the boss through `ApplyBossDamage`, the single entry
//   point the combat path will call once the quest boss is targetable (the tick
//   engine still only targets `MOB` kinds); until then the self-check is the
//   damage source. Phase transitions are evaluated at the boss's own impact
//   frames, which is the Q-F contract (damage first, phase second, one
//   transition per frame), while HP reaching zero ends the fight inside the
//   tick it lands — DEFEATED is therefore emitted once, from whichever of the
//   two paths observes it first.
public sealed class AlphaBossEncounterService
{
    private const string QuestId = "P00-05";
    private const string FragmentObjectiveId = "OBJ_P00_05_FRAGMENT";

    private readonly string _mapId;
    private readonly string _bossRecordId;
    private readonly string _worldEventRecordId;
    private readonly int _maxHp;
    private readonly int _attack;
    private readonly double _centerX;
    private readonly double _centerY;
    private readonly double _arenaRadius;
    private readonly int _phaseGuardTicks;
    private readonly double _phase2RecoveryMultiplier;
    private readonly double _phase3DamageMultiplier;
    private readonly long _wipeTicks;
    private readonly IReadOnlyList<AlphaBossMove> _moves;
    private readonly IQuestService _quests;
    private readonly WorldEntityRegistry _entities;
    private readonly CombatDamageFeature _combat;
    private readonly GuardDefenseService _guards;
    private readonly double _phaseNpcX;
    private readonly double _phaseNpcY;
    private readonly string? _bossEntityId;
    private readonly object _sync = new();
    private readonly Dictionary<string, EncounterInstance> _instances =
        new(StringComparer.Ordinal);

    public AlphaBossEncounterService(
        AlphaDesign design,
        IQuestService quests,
        WorldEntityRegistry entities,
        CombatDamageFeature combat,
        GuardDefenseService guards)
    {
        ArgumentNullException.ThrowIfNull(design);
        ArgumentNullException.ThrowIfNull(quests);
        ArgumentNullException.ThrowIfNull(entities);
        ArgumentNullException.ThrowIfNull(combat);
        ArgumentNullException.ThrowIfNull(guards);
        var boss = design.Boss;
        _mapId = design.Scope.MapId;
        _bossRecordId = design.QuestRules.P00_05_BossRecordId;
        _worldEventRecordId = design.QuestRules.P00_05_WorldEventRecordIdDisabled;
        _maxHp = boss.MaxHp;
        _attack = boss.Attack;
        _centerX = boss.CenterX;
        _centerY = boss.CenterY;
        _arenaRadius = boss.RadiusWu;
        // Integer ceilings on the source seconds, the same policy as the mob
        // telegraph projection: 1.0 s at 20 Hz is 20 ticks and 10 s is 200.
        _phaseGuardTicks = (int)Math.Ceiling(boss.PhaseGuardSeconds * ServerClock.TicksPerSecond);
        _wipeTicks = (long)Math.Ceiling(
            boss.WipeNoAliveTargetSeconds * ServerClock.TicksPerSecond);
        _phase2RecoveryMultiplier = boss.Phase2RecoveryMultiplier;
        _phase3DamageMultiplier = boss.Phase3AdditionalDamageMultiplier;
        _moves = boss.Moves;
        _phaseNpcX = design.QuestRules.P00_05_PhaseNpcX;
        _phaseNpcY = design.QuestRules.P00_05_PhaseNpcY;
        _quests = quests;
        _entities = entities;
        _combat = combat;
        _guards = guards;
        _bossEntityId = entities.All
            .FirstOrDefault(entity =>
                string.Equals(entity.RecordId, _bossRecordId, StringComparison.Ordinal) &&
                string.Equals(entity.Kind, WorldEntityKinds.Boss, StringComparison.Ordinal))
            ?.EntityId;
    }

    public IReadOnlyList<BossEncounterResolution> Tick(
        IReadOnlyList<PlayerSession> players,
        long tick)
    {
        var resolutions = new List<BossEncounterResolution>();
        lock (_sync)
        {
            var byCharacter = new Dictionary<string, PlayerSession>(StringComparer.Ordinal);
            foreach (var player in players)
            {
                byCharacter[player.CharacterId] = player;
            }

            foreach (var characterId in _instances.Keys.ToArray())
            {
                var instance = _instances[characterId];
                byCharacter.TryGetValue(characterId, out var owner);
                var questOutcome = _quests.GetState(characterId, QuestId);

                if (owner is null ||
                    questOutcome.State is not { } questState ||
                    !string.Equals(questState.State, QuestStates.Active, StringComparison.Ordinal))
                {
                    // The instance leaves with its owner; the boss goes back
                    // under despawn hold so no half-fought encounter is left
                    // alive in the world.
                    _instances.Remove(characterId);
                    DespawnBoss();
                    resolutions.Add(new BossEncounterResolution(
                        characterId,
                        BossEncounterOutcomeCodes.Ended,
                        questOutcome.State?.State ?? "SESSION_GONE",
                        (int)instance.Machine.Phase,
                        instance.BossHp,
                        0,
                        0,
                        0));
                    continue;
                }

                if (instance.Defeated)
                {
                    continue;
                }

                // "boss reset khi cả đội rời": down, off the map or outside the
                // ring stops being a live target, and the sourced 10 s
                // countdown decides the wipe.
                if (!IsLiveTarget(owner))
                {
                    instance.NoTargetSinceTick ??= tick;
                    if (tick - instance.NoTargetSinceTick.Value >= _wipeTicks)
                    {
                        Wipe(instance, resolutions);
                    }

                    continue;
                }

                instance.NoTargetSinceTick = null;
                if (instance.AwaitingFreshAttempt)
                {
                    StartAttempt(instance, tick, resolutions);
                }

                Step(instance, owner, tick, resolutions);
            }

            foreach (var player in players)
            {
                if (_instances.ContainsKey(player.CharacterId) || !IsLiveTarget(player))
                {
                    continue;
                }

                var questOutcome = _quests.GetState(player.CharacterId, QuestId);
                if (questOutcome.State is not { } questState ||
                    !string.Equals(questState.State, QuestStates.Active, StringComparison.Ordinal))
                {
                    continue;
                }

                var instance = new EncounterInstance(
                    Guid.NewGuid().ToString("N"),
                    player.CharacterId,
                    _maxHp,
                    tick,
                    NewMachine());
                _instances.Add(player.CharacterId, instance);
                StartAttempt(instance, tick, resolutions);
                Step(instance, player, tick, resolutions);
            }

            HoldWorldEventBoss();
        }

        return resolutions;
    }

    // The one entry point for damage on the boss. Today only the self-check
    // drives it; the combat path calls it once the quest boss is targetable.
    // HP hitting zero ends the fight inside this tick rather than waiting for
    // the next impact frame.
    public IReadOnlyList<BossEncounterResolution> ApplyBossDamage(
        string characterId,
        int damage,
        long tick)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(damage);
        lock (_sync)
        {
            if (!_instances.TryGetValue(characterId, out var instance) ||
                instance.Defeated ||
                instance.AwaitingFreshAttempt)
            {
                return Array.Empty<BossEncounterResolution>();
            }

            instance.BossHp = Math.Max(0, instance.BossHp - damage);
            var resolutions = new List<BossEncounterResolution>();
            ResolveDefeat(instance, resolutions);
            return resolutions;
        }
    }

    public bool TryGetState(string characterId, out EncounterSnapshot snapshot)
    {
        lock (_sync)
        {
            if (_instances.TryGetValue(characterId, out var instance))
            {
                snapshot = new EncounterSnapshot(
                    instance.InstanceId,
                    QuestId,
                    (int)instance.Machine.Phase,
                    instance.BossHp,
                    _maxHp,
                    instance.BossLifeId,
                    instance.Active?.Move.Id,
                    instance.Active is null
                        ? null
                        : instance.Active.InRecovery ? "RECOVERY" : "TELEGRAPH",
                    instance.Defeated
                        ? "DEFEATED"
                        : instance.AwaitingFreshAttempt ? "RESET" : "OPEN",
                    _centerX,
                    _centerY,
                    _arenaRadius);
                return true;
            }
        }

        snapshot = default;
        return false;
    }

    // NPC_CLASS_TRIAL becomes visible after the boss is down AND the fragment
    // is claimed, and only while P00-05 has not been turned in: the sourced fix
    // for the circular dependency. P1 has no wire for NPC visibility, so this
    // is the domain answer the encounter snapshot packet would expose.
    public bool IsTrialNpcVisible(string characterId)
    {
        lock (_sync)
        {
            if (!_instances.TryGetValue(characterId, out var instance) || !instance.Defeated)
            {
                return false;
            }

            var outcome = _quests.GetState(characterId, QuestId);
            if (outcome.State is not { } state ||
                string.Equals(state.State, QuestStates.Completed, StringComparison.Ordinal))
            {
                return false;
            }

            return state.ObjectiveCounters.TryGetValue(FragmentObjectiveId, out var claimed) &&
                   claimed > 0;
        }
    }

    // questRules.P00-05.phaseNpcOverride: after P00-05 is accepted in the quest
    // instance the same actor moves to (182,4) — never a second copy of them.
    public bool TryGetPhaseNpcPosition(string characterId, out double x, out double y)
    {
        lock (_sync)
        {
            if (_instances.TryGetValue(characterId, out _))
            {
                x = _phaseNpcX;
                y = _phaseNpcY;
                return true;
            }
        }

        x = 0;
        y = 0;
        return false;
    }

    private void StartAttempt(EncounterInstance instance, long tick,
        List<BossEncounterResolution> resolutions)
    {
        // The entity life is synced first so the machine engages against the
        // same lifeId the world carries (a wipe's ForceRespawn bumps it).
        var entity = BossEntity;
        if (entity is not null)
        {
            if (!string.Equals(entity.State, WorldEntityStates.Alive, StringComparison.Ordinal))
            {
                entity.ForceRespawn();
            }

            instance.BossLifeId = entity.LifeId;
        }

        instance.Machine.Engage(instance.BossLifeId, LocalTick(instance, tick));
        instance.BossHp = _maxHp;
        instance.Active = null;
        instance.AwaitingFreshAttempt = false;
        resolutions.Add(new BossEncounterResolution(
            instance.CharacterId,
            BossEncounterOutcomeCodes.Registered,
            $"life={instance.BossLifeId}",
            (int)instance.Machine.Phase,
            instance.BossHp,
            0,
            0,
            0));
    }

    private void Step(
        EncounterInstance instance,
        PlayerSession owner,
        long tick,
        List<BossEncounterResolution> resolutions)
    {
        if (instance.Defeated)
        {
            return;
        }

        var local = LocalTick(instance, tick);
        if (instance.Active is null)
        {
            var begin = instance.Machine.TryBeginMove(local);
            if (!begin.Started)
            {
                return;
            }

            var opening = _moves.Single(candidate =>
                string.Equals(candidate.Id, begin.Token!.MoveId, StringComparison.Ordinal));
            instance.Active = new MoveTimeline(
                begin.Token!,
                opening,
                tick + Ticks(opening.WindupSeconds),
                owner.X - BossX,
                owner.Y - BossY,
                owner.X,
                owner.Y);
            resolutions.Add(new BossEncounterResolution(
                instance.CharacterId,
                BossEncounterOutcomeCodes.Telegraph,
                opening.Id,
                (int)instance.Machine.Phase,
                instance.BossHp,
                0,
                0,
                0));
            return;
        }

        var timeline = instance.Active;
        if (timeline.InRecovery)
        {
            if (tick < timeline.RecoveryUntilTick)
            {
                return;
            }

            instance.Active = null;
            return;
        }

        if (tick < timeline.ImpactTick)
        {
            return;
        }

        var move = timeline.Move;
        instance.Active = null;
        var hit = Hits(timeline, owner);
        var damage = 0;
        var hpBefore = owner.Hp;
        var hpAfter = owner.Hp;
        string outcome;
        string? detail;

        if (!hit)
        {
            outcome = BossEncounterOutcomeCodes.ImpactBlocked;
            detail = $"{move.Id}:DODGED";
        }
        else if (!_combat.Enabled)
        {
            outcome = BossEncounterOutcomeCodes.ImpactBlocked;
            detail = $"{move.Id}:{MobAttackBlockedReasons.GateOff}";
        }
        else
        {
            var raw = DamageFormula.RawDamage(_attack, 0, move.Coefficient, 1, 0);
            var incoming = _guards.EvaluateIncoming(owner.CharacterId, tick, BossX, BossY);
            var mitigation = DamageFormula.MitigationMultiplier(CombatActorBaseline.Armor);
            var reduction = DamageFormula.DamageReductionMultiplier(
                GuardTimeline.CombineReduction(incoming.DamageReduction));
            // The phase-3 additional damage multiplier rides the general
            // multiplicative damage slot (not the resistance slot, which is
            // capped at 0.5); the approved profile carries 1.0, so today it is
            // a no-op that a later source change reuses without a code edit.
            var additionalDamage = PhaseOf(instance) == 3 ? _phase3DamageMultiplier : 1.0;
            var final = DamageFormula.FinalDamage(
                raw, mitigation, 1.0, additionalDamage, reduction);
            outcome = BossEncounterOutcomeCodes.Impact;
            detail = move.Id;
            var boss = BossEntity;
            lock (owner.SyncRoot)
            {
                if (owner.Hp > 0 && boss is not null &&
                    string.Equals(owner.MapId, _mapId, StringComparison.Ordinal))
                {
                    hpBefore = owner.Hp;
                    damage = (int)final;
                    hpAfter = Math.Max(0, hpBefore - damage);
                    owner.Hp = hpAfter;
                    owner.Revision++;
                    _guards.CommitConfirmation(
                        owner.CharacterId, incoming.WindowCastId, boss, tick,
                        DateTimeOffset.UtcNow, hpAfter > 0);
                    if (hpAfter == 0)
                    {
                        detail = $"{move.Id}:DOWN";
                    }
                }
                else
                {
                    outcome = BossEncounterOutcomeCodes.ImpactBlocked;
                    detail = boss is null
                        ? $"{move.Id}:{MobAttackBlockedReasons.EntityMissing}"
                        : $"{move.Id}:{MobAttackBlockedReasons.TargetDown}";
                }
            }
        }

        resolutions.Add(new BossEncounterResolution(
            instance.CharacterId, outcome, detail,
            PhaseOf(instance), instance.BossHp, damage, hpBefore, hpAfter));

        if (instance.Defeated)
        {
            return;
        }

        // Damage-before-phase at the frame, one transition per frame: the Q-F
        // contract, with the HP the boss actually has now.
        var impact = instance.Machine.ResolveImpact(timeline.Token, instance.BossHp, _maxHp, local);
        if (impact.Accepted && impact.PhaseChanged)
        {
            resolutions.Add(new BossEncounterResolution(
                instance.CharacterId,
                BossEncounterOutcomeCodes.PhaseChanged,
                impact.Phase.ToString(),
                PhaseOf(instance),
                instance.BossHp,
                0,
                0,
                0));
        }

        ResolveDefeat(instance, resolutions);
        if (instance.Defeated)
        {
            return;
        }

        // No overlap: the next move only opens after this one's recovery, and
        // phase 2 shortens that recovery by the sourced multiplier.
        timeline.InRecovery = true;
        timeline.RecoveryUntilTick = tick + Ticks(
            move.RecoverySeconds * (PhaseOf(instance) == 2 ? _phase2RecoveryMultiplier : 1.0));
        instance.Active = timeline;
    }

    private void Wipe(EncounterInstance instance, List<BossEncounterResolution> resolutions)
    {
        // Wiped: HP refills, phase returns to 1, the episode bumps so every
        // token issued before the reset is stale, the quest checkpoint stays
        // where it is and nothing pays loot. The boss waits despawned until the
        // owner re-enters the ring, which is a fresh attempt on a new life.
        instance.Machine.Reset();
        instance.Active = null;
        instance.BossHp = _maxHp;
        instance.NoTargetSinceTick = null;
        instance.AwaitingFreshAttempt = true;
        instance.BossLifeId++;
        DespawnBoss();
        resolutions.Add(new BossEncounterResolution(
            instance.CharacterId,
            BossEncounterOutcomeCodes.Wiped,
            $"life={instance.BossLifeId}",
            1,
            instance.BossHp,
            0,
            0,
            0));
    }

    private void ResolveDefeat(EncounterInstance instance,
        List<BossEncounterResolution> resolutions)
    {
        if (instance.Defeated || instance.BossHp > 0)
        {
            return;
        }

        instance.Defeated = true;
        instance.Active = null;
        DespawnBoss();
        resolutions.Add(new BossEncounterResolution(
            instance.CharacterId,
            BossEncounterOutcomeCodes.Defeated,
            $"life={instance.BossLifeId}",
            PhaseOf(instance),
            0,
            0,
            0,
            0));
    }

    private bool Hits(MoveTimeline timeline, PlayerSession owner)
    {
        var move = timeline.Move;
        var dx = owner.X - BossX;
        var dy = owner.Y - BossY;
        var distance = Math.Sqrt((dx * dx) + (dy * dy));
        switch (move.Shape)
        {
            case "CONE":
            {
                if (distance > move.RangeWu!.Value + 1e-9)
                {
                    return false;
                }

                var facingLength = Math.Sqrt(
                    (timeline.BossFacingX * timeline.BossFacingX) +
                    (timeline.BossFacingY * timeline.BossFacingY));
                if (facingLength <= 1e-9 || distance <= 1e-9)
                {
                    // The owner was standing on the boss at the telegraph
                    // start: the cone keeps its own origin, so they are hit.
                    return true;
                }

                var dot = ((dx * timeline.BossFacingX) + (dy * timeline.BossFacingY)) /
                    (facingLength * distance);
                var halfAngleCos = Math.Cos(move.AngleDegrees!.Value * Math.PI / 360.0);
                // Inclusive edges, the same convention as the DEC-022 cone.
                return dot >= halfAngleCos - 1e-9;
            }

            case "CIRCLE":
            {
                var tdx = owner.X - timeline.TargetLockX;
                var tdy = owner.Y - timeline.TargetLockY;
                return Math.Sqrt((tdx * tdx) + (tdy * tdy)) <= move.RadiusWu!.Value + 1e-9;
            }

            case "ANNULUS":
            {
                return distance >= move.InnerRadiusWu!.Value - 1e-9 &&
                       distance <= move.OuterRadiusWu!.Value + 1e-9;
            }

            default:
                return false;
        }
    }

    private long Ticks(double seconds) =>
        (long)Math.Ceiling(seconds * ServerClock.TicksPerSecond);

    // The Q-F machine counts in ints; the encounter counts from its own
    // registration tick so a long-lived server clock never overflows it.
    private static int LocalTick(EncounterInstance instance, long tick) =>
        (int)Math.Clamp(tick - instance.StartTick, 0, int.MaxValue);

    private static int PhaseOf(EncounterInstance instance) => (int)instance.Machine.Phase;

    private WorldEntityInstance? BossEntity =>
        _bossEntityId is null
            ? null
            : _entities.All.FirstOrDefault(entity =>
                string.Equals(entity.EntityId, _bossEntityId, StringComparison.Ordinal));

    private double BossX => BossEntity?.X ?? _centerX;

    private double BossY => BossEntity?.Y ?? _centerY;

    private void DespawnBoss()
    {
        var entity = BossEntity;
        if (entity is not null &&
            !string.Equals(entity.State, WorldEntityStates.Dead, StringComparison.Ordinal))
        {
            _entities.Despawn(entity.EntityId);
        }
    }

    private bool IsLiveTarget(PlayerSession player) =>
        string.Equals(player.MapId, _mapId, StringComparison.Ordinal) &&
        player.Hp > 0 &&
        InsideArena(player.X, player.Y);

    private bool InsideArena(double x, double y)
    {
        var dx = x - _centerX;
        var dy = y - _centerY;
        return Math.Sqrt((dx * dx) + (dy * dy)) <= _arenaRadius + 1e-9;
    }

    private BossEncounter NewMachine() =>
        new(
            new BossEncounterRules(_phaseGuardTicks),
            _moves
                .Select(move => new BossMoveDefinition(
                    move.Id,
                    (int)Math.Ceiling(move.CooldownSeconds * ServerClock.TicksPerSecond)))
                .ToList());

    // The design names exactly one of the two (178,0) boss records for the
    // quest, so while an owner holds an instance the world-event record is held
    // despawned rather than coexisting with it.
    private void HoldWorldEventBoss()
    {
        if (_instances.Count == 0)
        {
            return;
        }

        foreach (var entity in _entities.All.Where(candidate =>
                     string.Equals(candidate.RecordId, _worldEventRecordId, StringComparison.Ordinal)))
        {
            if (!string.Equals(entity.State, WorldEntityStates.Dead, StringComparison.Ordinal))
            {
                _entities.Despawn(entity.EntityId);
            }
        }
    }

    private sealed class EncounterInstance
    {
        public EncounterInstance(
            string instanceId,
            string characterId,
            int bossHp,
            long startTick,
            BossEncounter machine)
        {
            InstanceId = instanceId;
            CharacterId = characterId;
            BossHp = bossHp;
            StartTick = startTick;
            Machine = machine;
        }

        public string InstanceId { get; }
        public string CharacterId { get; }
        public long StartTick { get; }
        public BossEncounter Machine { get; }
        public int BossHp;
        public long BossLifeId = 1;
        public MoveTimeline? Active;
        public long? NoTargetSinceTick;
        public bool Defeated;
        public bool AwaitingFreshAttempt = true;
    }

    private sealed class MoveTimeline
    {
        public MoveTimeline(
            BossMoveToken token,
            AlphaBossMove move,
            long impactTick,
            double bossFacingX,
            double bossFacingY,
            double targetLockX,
            double targetLockY)
        {
            Token = token;
            Move = move;
            ImpactTick = impactTick;
            BossFacingX = bossFacingX;
            BossFacingY = bossFacingY;
            TargetLockX = targetLockX;
            TargetLockY = targetLockY;
        }

        public BossMoveToken Token { get; }
        public AlphaBossMove Move { get; }
        public long ImpactTick { get; }
        public double BossFacingX { get; }
        public double BossFacingY { get; }
        public double TargetLockX { get; }
        public double TargetLockY { get; }
        public bool InRecovery;
        public long RecoveryUntilTick;
    }
}

public readonly record struct EncounterSnapshot(
    string EncounterId,
    string QuestId,
    int Phase,
    int BossHp,
    int BossMaxHp,
    long BossLifeId,
    string? ActiveMoveId,
    string? ActiveMoveState,
    string Status,
    double ArenaCenterXWu,
    double ArenaCenterYWu,
    double ArenaRadiusWu);
