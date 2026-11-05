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
// phase machine. Its approved read model is `EncounterSnapshotV1`, served by
// `GET /p1/encounters/current` and `GET /p1/encounters/{encounterId}`; the
// per-owner HP, move timeline, phase transitions, wipe countdown and P00-05
// quest-instance overrides all live here and nowhere else.
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
// - Player damage reaches the boss through `ApplyBossDamage`, which the combat
//   tick engine calls when one of the acting character's casts lands on the
//   encounter boss (see `ICombatBossBridge`); the v2 audience read model marks
//   that same boss targetable for its owner and only for its owner. Phase
//   transitions are evaluated at the boss's own impact
//   frames, which is the Q-F contract (damage first, phase second, one
//   transition per frame), while HP reaching zero ends the fight inside the
//   tick it lands — DEFEATED is therefore emitted once, from whichever of the
//   two paths observes it first.
public sealed class AlphaBossEncounterService : ICombatBossBridge
{
    private const string QuestId = "P00-05";
    private const string FragmentObjectiveId = "OBJ_P00_05_FRAGMENT";

    private readonly string _mapId;
    private readonly string _bossRecordId;
    private readonly string _worldEventRecordId;
    private readonly int _maxHp;
    private readonly int _attack;
    private readonly int _bossDefense;
    private readonly double _centerX;
    private readonly double _centerY;
    private readonly double _arenaRadius;
    private readonly string _arenaShape;
    private readonly IReadOnlyList<AlphaPoint> _safePads;
    private readonly double _safePadRadius;
    private readonly bool _safePadsPhase3Only;
    private readonly int _phaseGuardTicks;
    private readonly double _phase2RecoveryMultiplier;
    private readonly double _phase3DamageMultiplier;
    private readonly long _wipeTicks;
    private readonly IReadOnlyList<AlphaBossMove> _moves;
    private readonly IQuestService _quests;
    private readonly WorldEntityRegistry _entities;
    private readonly CombatDamageFeature _combat;
    private readonly GuardDefenseService _guards;
    private readonly PlayerLifeLedger _lives;
    private readonly double _phaseNpcX;
    private readonly double _phaseNpcY;
    private readonly string _phaseNpcId;
    private readonly string? _bossEntityId;
    private readonly object _sync = new();
    private readonly Dictionary<string, EncounterInstance> _instances =
        new(StringComparer.Ordinal);

    public AlphaBossEncounterService(
        AlphaDesign design,
        IQuestService quests,
        WorldEntityRegistry entities,
        CombatDamageFeature combat,
        GuardDefenseService guards,
        PlayerLifeLedger lives)
    {
        ArgumentNullException.ThrowIfNull(design);
        ArgumentNullException.ThrowIfNull(quests);
        ArgumentNullException.ThrowIfNull(entities);
        ArgumentNullException.ThrowIfNull(combat);
        ArgumentNullException.ThrowIfNull(guards);
        ArgumentNullException.ThrowIfNull(lives);
        _lives = lives;
        var boss = design.Boss;
        _mapId = design.Scope.MapId;
        _bossRecordId = design.QuestRules.P00_05_BossRecordId;
        _worldEventRecordId = design.QuestRules.P00_05_WorldEventRecordIdDisabled;
        // The two (178,0) records must stay distinct or "which boss is this cast
        // hitting" stops being answerable per instance.
        if (string.Equals(_bossRecordId, _worldEventRecordId, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                "Alpha quest boss and world-event boss must be different records.");
        }
        _maxHp = boss.MaxHp;
        _attack = boss.Attack;
        _bossDefense = boss.Armor;
        _centerX = boss.CenterX;
        _centerY = boss.CenterY;
        _arenaRadius = boss.RadiusWu;
        _arenaShape = boss.ArenaShape;
        _safePads = boss.SafePads;
        _safePadRadius = boss.SafePadRadiusWu;
        _safePadsPhase3Only = boss.SafePadsPhase3Only;
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
        _phaseNpcId = design.QuestRules.P00_05_PhaseNpcId;
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
                    // The instance leaves with its owner. The shared world entity
                    // is deliberately untouched: another owner may be fighting the
                    // same record, and one attempt ending must not change anyone
                    // else's boss (owner/attempt state lives in the instance).
                    _instances.Remove(characterId);
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
        }

        return resolutions;
    }

    // The one entry point for damage on the boss. The combat tick engine routes
    // a cast that lands on the quest boss here, and the self-check drives it
    // directly. HP hitting zero ends the fight inside this tick rather than
    // waiting for the next impact frame.
    public IReadOnlyList<BossEncounterResolution> ApplyBossDamage(
        string characterId,
        int damage,
        long tick)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(damage);
        lock (_sync)
        {
            var resolutions = new List<BossEncounterResolution>();
            DamageBossLocked(characterId, damage, resolutions);
            return resolutions;
        }
    }

    // Shared damage path; the caller already holds _sync. Returns HP before and
    // after, and whether this hit killed the boss.
    private (int HpBefore, int HpAfter, bool Died) DamageBossLocked(
        string characterId, int damage, List<BossEncounterResolution> resolutions)
    {
        if (!_instances.TryGetValue(characterId, out var instance) ||
            instance.Defeated ||
            instance.AwaitingFreshAttempt)
        {
            return (0, 0, false);
        }

        var hpBefore = instance.BossHp;
        instance.BossHp = Math.Max(0, instance.BossHp - damage);
        instance.BossRevision++;
        ResolveDefeat(instance, resolutions);
        return (hpBefore, instance.BossHp, instance.Defeated);
    }

    // The tick engine casts at the quest boss through this bridge; the encounter
    // stays the single owner of the boss HP and phase bookkeeping.
    int ICombatBossBridge.BossDefense => _bossDefense;

    bool ICombatBossBridge.IsLiveBossTarget(string characterId, WorldEntityInstance entity)
    {
        lock (_sync)
        {
            return IsLiveBossTargetLocked(characterId, entity);
        }
    }

    // The same predicate the cast path uses, so the audience read model can
    // never advertise a boss the engine would refuse to hit.
    private bool IsLiveBossTargetLocked(string characterId, WorldEntityInstance entity) =>
        _bossEntityId is not null &&
        string.Equals(entity.EntityId, _bossEntityId, StringComparison.Ordinal) &&
        _instances.TryGetValue(characterId, out var instance) &&
        !instance.Defeated &&
        !instance.AwaitingFreshAttempt &&
        string.Equals(entity.State, WorldEntityStates.Alive, StringComparison.Ordinal);

    bool ICombatBossBridge.TryGetAudience(
        string characterId,
        WorldEntityInstance entity,
        out BossEncounterAudience audience)
    {
        lock (_sync)
        {
            if (_bossEntityId is not null &&
                string.Equals(entity.EntityId, _bossEntityId, StringComparison.Ordinal) &&
                _instances.TryGetValue(characterId, out var instance))
            {
                audience = new BossEncounterAudience(
                    IsLiveBossTargetLocked(characterId, entity),
                    instance.Defeated,
                    instance.Defeated ? 0 : instance.BossHp,
                    _maxHp);
                return true;
            }
        }

        audience = default;
        return false;
    }

    (int HpBefore, int HpAfter, bool Died) ICombatBossBridge.ApplyDamage(
        string characterId, int damage, long tick)
    {
        lock (_sync)
        {
            var resolutions = new List<BossEncounterResolution>();
            return DamageBossLocked(characterId, damage, resolutions);
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

    // The approved wire read: one atomic copy of a single generation, taken under
    // the same lock that mutates it, so HP, phase, life, revision, active move and
    // its deadline can never come from different ticks. `tick` is the authoritative
    // server tick the caller is reading at, so every countdown agrees with it.
    public bool TryGetSnapshot(string characterId, long tick, out EncounterSnapshotV1 snapshot)
    {
        lock (_sync)
        {
            if (_instances.TryGetValue(characterId, out var instance) &&
                _bossEntityId is not null)
            {
                snapshot = BuildSnapshot(instance, tick);
                return true;
            }
        }

        snapshot = null!;
        return false;
    }

    private EncounterSnapshotV1 BuildSnapshot(EncounterInstance instance, long tick)
    {
        var local = LocalTick(instance, tick);
        var phase = PhaseOf(instance);
        var move = instance.Active;
        var bossX = BossX;
        var bossY = BossY;
        EncounterMoveShapeV1? shape = null;
        EncounterActiveMoveV1? activeMove = null;
        if (move is not null)
        {
            // Cone keeps the direction locked at the telegraph; circle centres on
            // the position locked at the telegraph; annulus rides the boss itself.
            var coneCenterX = bossX;
            var coneCenterY = bossY;
            double facingX = 0;
            double facingY = 0;
            switch (move.Move.Shape)
            {
                case "CONE":
                {
                    var length = Math.Sqrt(
                        (move.BossFacingX * move.BossFacingX) +
                        (move.BossFacingY * move.BossFacingY));
                    // A zero-length facing (the owner was standing on the boss at
                    // the telegraph) has no direction; the +X fallback keeps the
                    // vector normalized and is display-only, because the hit test
                    // already treats that case as "the cone covers its origin".
                    facingX = length <= 1e-9 ? 1 : move.BossFacingX / length;
                    facingY = length <= 1e-9 ? 0 : move.BossFacingY / length;
                    break;
                }
                case "CIRCLE":
                {
                    coneCenterX = move.TargetLockX;
                    coneCenterY = move.TargetLockY;
                    break;
                }
            }

            shape = new EncounterMoveShapeV1
            {
                Kind = move.Move.Shape,
                CenterXWu = coneCenterX,
                CenterYWu = coneCenterY,
                AngleDegrees = move.Move.Shape == "CONE" ? move.Move.AngleDegrees : null,
                RangeWu = move.Move.Shape == "CONE" ? move.Move.RangeWu : null,
                FacingX = move.Move.Shape == "CONE" ? facingX : null,
                FacingY = move.Move.Shape == "CONE" ? facingY : null,
                RadiusWu = move.Move.Shape == "CIRCLE" ? move.Move.RadiusWu : null,
                InnerRadiusWu = move.Move.Shape == "ANNULUS" ? move.Move.InnerRadiusWu : null,
                OuterRadiusWu = move.Move.Shape == "ANNULUS" ? move.Move.OuterRadiusWu : null
            };
            activeMove = new EncounterActiveMoveV1
            {
                MoveId = move.Move.Id,
                CastId = move.CastId,
                State = move.InRecovery
                    ? EncounterMoveStates.Recovery
                    : EncounterMoveStates.Telegraph,
                TicksRemaining = move.TicksRemaining(tick),
                StateEndsAtTick = move.StateEndsAtTick,
                Shape = shape,
                TargetLock = move.Move.TargetLock switch
                {
                    "telegraph start facing" => EncounterTargetLocks.TelegraphStartFacing,
                    "target position at telegraph start" =>
                        EncounterTargetLocks.TelegraphStartTargetPosition,
                    _ => EncounterTargetLocks.BossPosition
                }
            };
        }

        var padsApply = !_safePadsPhase3Only || phase >= 3;
        return new EncounterSnapshotV1
        {
            EncounterId = instance.EncounterId,
            QuestId = QuestId,
            BossRecordId = _bossRecordId,
            BossEntityId = _bossEntityId!,
            BossLifeId = instance.BossLifeId,
            BossRevision = instance.BossRevision,
            Status = instance.Defeated
                ? EncounterSnapshotStatuses.Defeated
                : instance.AwaitingFreshAttempt
                    ? EncounterSnapshotStatuses.Reset
                    : EncounterSnapshotStatuses.Open,
            Phase = phase,
            BossHp = instance.BossHp,
            BossMaxHp = _maxHp,
            ServerTick = tick,
            RegisteredCharacterIds = new[] { instance.CharacterId },
            ActiveMove = activeMove,
            MoveCooldownRemainingTicks = new EncounterMoveCooldownsV1
            {
                A = instance.Machine.CooldownRemainingTicks("A", local),
                B = instance.Machine.CooldownRemainingTicks("B", local),
                C = instance.Machine.CooldownRemainingTicks("C", local)
            },
            PhaseGuardRemainingTicks = instance.Machine.PhaseGuardRemainingTicks(local),
            WipeCountdownTicks = instance.NoTargetSinceTick is { } since
                ? (int)Math.Clamp(_wipeTicks - (tick - since), 0, int.MaxValue)
                : null,
            Arena = new EncounterArenaV1
            {
                Shape = _arenaShape,
                CenterXWu = _centerX,
                CenterYWu = _centerY,
                RadiusWu = _arenaRadius
            },
            SafePads = _safePads
                .Select(pad => new EncounterSafePadV1
                {
                    CenterXWu = pad.X,
                    CenterYWu = pad.Y,
                    RadiusWu = _safePadRadius,
                    Applies = padsApply
                })
                .ToArray(),
            PhaseNpc = new EncounterPhaseNpcV1
            {
                NpcId = _phaseNpcId,
                XWu = _phaseNpcX,
                YWu = _phaseNpcY,
                Active = true
            },
            TrialNpcVisible = TrialVisibleLocked(instance)
        };
    }

    // NPC_CLASS_TRIAL becomes visible after the boss is down AND the fragment
    // is claimed, and only while P00-05 has not been turned in: the sourced fix
    // for the circular dependency.
    public bool IsTrialNpcVisible(string characterId)
    {
        lock (_sync)
        {
            return _instances.TryGetValue(characterId, out var instance) &&
                TrialVisibleLocked(instance);
        }
    }

    // Assumes _sync is held (the snapshot reads it in the same lock as the rest of
    // the generation, so visibility cannot disagree with HP or phase).
    private bool TrialVisibleLocked(EncounterInstance instance)
    {
        if (!instance.Defeated)
        {
            return false;
        }

        var outcome = _quests.GetState(instance.CharacterId, QuestId);
        if (outcome.State is not { } state ||
            string.Equals(state.State, QuestStates.Completed, StringComparison.Ordinal))
        {
            return false;
        }

        return state.ObjectiveCounters.TryGetValue(FragmentObjectiveId, out var claimed) &&
               claimed > 0;
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
        // The life/attempt generation is owned by this instance, not by the
        // shared world entity: a fresh attempt bumps the instance life while
        // every other owner's fight on the same record keeps its own state.
        instance.Machine.Engage(instance.BossLifeId, LocalTick(instance, tick));
        instance.BossHp = _maxHp;
        instance.Active = null;
        instance.AwaitingFreshAttempt = false;
        instance.BossRevision++;
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
                owner.Y)
            {
                CastId = $"CAST-{instance.InstanceId[..12].ToUpperInvariant()}-" +
                    $"{++instance.MoveSequence:x4}"
            };
            instance.BossRevision++;
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
                    _lives.RecordDamageCommit(
                        owner.CharacterId, hpBefore, hpAfter, owner.Revision,
                        DateTimeOffset.UtcNow);
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
        instance.BossRevision++;
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
        // where it is and nothing pays loot. The instance waits in RESET until
        // the owner re-enters the ring, which is a fresh attempt on a new life.
        // The shared world entity is not despawned: another owner's fight on the
        // same record must not change because this attempt wiped.
        instance.Machine.Reset();
        instance.Active = null;
        instance.BossHp = _maxHp;
        instance.NoTargetSinceTick = null;
        instance.AwaitingFreshAttempt = true;
        instance.BossLifeId++;
        instance.BossRevision++;
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
        instance.BossRevision++;
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

        // Opaque identity of this (character, quest attempt): a wipe keeps it and a
        // finished attempt never re-issues it, so clients can poll one id.
        public string EncounterId => $"ENC-{InstanceId[..24].ToUpperInvariant()}";

        // Bumped whenever snapshot-relevant state moves, so two polls can tell a
        // real change from an identical-looking frame.
        public long BossRevision = 1;
        public int MoveSequence;
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

        // Stable for the whole cast of this move, and derived from the instance so
        // another owner's identical swing can never collide with it.
        public string CastId { get; init; } = string.Empty;

        public long StateEndsAtTick => InRecovery ? RecoveryUntilTick : ImpactTick;
        public int TicksRemaining(long tick) =>
            (int)Math.Max(0, StateEndsAtTick - tick);
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
