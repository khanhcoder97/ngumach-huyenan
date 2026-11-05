using System.Globalization;
using Server.Health.Contracts;
using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Quests;
using Server.Health.World;

namespace Server.Health.Gameplay.Alpha;

public static class EscortOutcomes
{
    public const string Started = "STARTED";
    public const string CheckpointCommitted = "CHECKPOINT_COMMITTED";
    public const string WaveActivated = "WAVE_ACTIVATED";
    public const string WaveCleared = "WAVE_CLEARED";
    public const string WaveActivationFailed = "WAVE_ACTIVATION_FAILED";
    public const string Wiped = "WIPED";
    public const string Completed = "COMPLETED";
    public const string Ended = "ENDED";
}

public sealed record EscortResolution(
    string CharacterId,
    string Outcome,
    string? Detail,
    double NpcX,
    double NpcY);

// QOD-21 Q1c/Q2: the P00-04 escort (DESIGN-BM-ALPHA-20261103 questRules.P00-04)
// as a 20 Hz tickable machine behind P1:AlphaProfile:Enabled. There is no
// approved wire surface for the escort NPC or the wave lifecycle, so the
// machine is domain-only: the NPC position, the checkpoint commits and the
// wave holds live server-side and the self-check exercises them
// deterministically.
//
// Sourced values (never defaulted): actor NPC_LYAN, owner-specific instance
// (one canonical NPC per owner, no second clone), speed 3 wu/s, followRange
// 12 wu, waypoints (42,0)->(80,0)->(120,0), checkpoint x=80 with
// MAN-BM-WAVE_BM_ESCORT_A (MOB_CARPLING x3) and x=120 with
// MAN-BM-WAVE_BM_ESCORT_B (MOB_WATERROOT x3), creditKey
// [instanceId, questAttemptId, waveId, entityLifeId, deathEventId], wipe
// restores the last committed checkpoint.
//
// Interpretation of the sourced rules (no invented numbers): the NPC walks the
// waypoint path at 3 wu/s only while the owner is alive, on the map and within
// 12 wu of the NPC. Reaching a checkpoint commits it and activates that
// checkpoint's wave; the NPC waits while the wave is active and resumes on the
// tick that observes it cleared. Clearing every required wave of every
// committed checkpoint is the only path to completion: a checkpoint whose wave
// cannot be activated — the bundle ships fewer than the sourced 3+3 actors, or
// the group is mid-fight for another owner — fails activation with a diagnostic
// and holds the NPC at the checkpoint instead of walking on. An owner death
// restores the NPC to the last committed checkpoint and re-activates an
// in-progress wave (new life IDs, re-fight); a cleared wave is never re-opened
// for the same instance, so it cannot be farmed.
//
// Kill credit is push-based, not polled. The tick engine hands each death it
// resolves to `OnMobKilled` — entity, life, killer and the DEATH event id it
// wrote to the killer's combat stream — and the credit key is exactly the
// sourced five-tuple. A replayed event therefore cannot double-count, and
// another owner's kills cannot fill this instance's wave. The P1 quest runtime
// has no attempt lifecycle, so the questAttemptId component stays at its first
// value. A wave cleared inside the sink is reported on the machine's next tick:
// the sink runs in the combat loop and has no combat stream to write into.
//
// Wave members are shared world spawns — the content ships one group per wave —
// so a group is only re-spawned when no other instance holds that wave active:
// one owner's wipe or late arrival must not reset another owner's generation.
public sealed class AlphaEscortService : ICombatKillSink, INpcEscortPositionSource
{
    private const string QuestId = "P00-04";

    private readonly string _mapId;
    private readonly string _actorId;
    private readonly double _speedPerTick;
    private readonly double _followRange;
    private readonly IReadOnlyList<AlphaPoint> _waypoints;
    private readonly IReadOnlyList<AlphaWaveRule> _waves;
    private readonly IQuestService _quests;
    private readonly WorldEntityRegistry _entities;
    private readonly object _sync = new();
    private readonly Dictionary<string, List<WorldEntityInstance>> _waveMembers =
        new(StringComparer.Ordinal);
    private readonly Dictionary<string, string> _waveByEntityId =
        new(StringComparer.Ordinal);
    private readonly Dictionary<string, EscortInstance> _instances =
        new(StringComparer.Ordinal);
    private readonly List<EscortResolution> _deferred = [];

    public AlphaEscortService(
        AlphaDesign design,
        IQuestService quests,
        WorldEntityRegistry entities)
    {
        ArgumentNullException.ThrowIfNull(design);
        ArgumentNullException.ThrowIfNull(quests);
        ArgumentNullException.ThrowIfNull(entities);
        var rules = design.QuestRules;
        _mapId = design.Scope.MapId;
        _actorId = rules.P00_04_ActorId;
        _speedPerTick = rules.P00_04_SpeedWuPerSecond / ServerClock.TicksPerSecond;
        _followRange = rules.P00_04_FollowRangeWu;
        _waypoints = rules.P00_04_Waypoints;
        _waves = [rules.P00_04_WaveA, rules.P00_04_WaveB];
        _quests = quests;
        _entities = entities;
        foreach (var wave in _waves)
        {
            var members = entities.All
                .Where(entity =>
                    string.Equals(entity.GroupId, wave.RecordId, StringComparison.Ordinal) &&
                    string.Equals(entity.Kind, WorldEntityKinds.Mob, StringComparison.Ordinal))
                .OrderBy(entity => entity.MemberIndex)
                .ToList();
            _waveMembers[wave.RecordId] = members;
            foreach (var member in members)
            {
                _waveByEntityId[member.EntityId] = wave.RecordId;
            }
        }
    }

    public IReadOnlyList<EscortResolution> Tick(
        IReadOnlyList<PlayerSession> players,
        long tick)
    {
        var resolutions = new List<EscortResolution>();
        lock (_sync)
        {
            // Kill-driven transitions are reported here: the sink is called from
            // the combat loop and has nowhere else to hand them.
            resolutions.AddRange(_deferred);
            _deferred.Clear();

            if (_waypoints.Count < 2)
            {
                return resolutions;
            }

            var targets = new Dictionary<string, PlayerSession>(StringComparer.Ordinal);
            foreach (var player in players)
            {
                targets[player.CharacterId] = player;
            }

            foreach (var characterId in _instances.Keys.ToArray())
            {
                var instance = _instances[characterId];
                if (!targets.TryGetValue(characterId, out var owner))
                {
                    continue;
                }

                var questOutcome = _quests.GetState(characterId, QuestId);
                if (questOutcome.State is not { } questState ||
                    !string.Equals(questState.State, QuestStates.Active, StringComparison.Ordinal))
                {
                    _instances.Remove(characterId);
                    resolutions.Add(new EscortResolution(
                        characterId,
                        EscortOutcomes.Ended,
                        questOutcome.State?.State,
                        instance.NpcX,
                        instance.NpcY));
                    continue;
                }

                var onMap = string.Equals(owner.MapId, _mapId, StringComparison.Ordinal);
                if (onMap && owner.Hp <= 0 && instance.OwnerAlive)
                {
                    instance.OwnerAlive = false;
                    Wipe(instance, resolutions);
                    continue;
                }

                if (onMap && owner.Hp > 0 && !instance.OwnerAlive)
                {
                    instance.OwnerAlive = true;
                }

                if (!onMap || owner.Hp <= 0)
                {
                    continue;
                }

                Advance(instance, owner, resolutions);
            }

            foreach (var player in players)
            {
                if (_instances.ContainsKey(player.CharacterId) ||
                    !string.Equals(player.MapId, _mapId, StringComparison.Ordinal) ||
                    player.Hp <= 0)
                {
                    continue;
                }

                var questOutcome = _quests.GetState(player.CharacterId, QuestId);
                if (questOutcome.State is not { } questState ||
                    !string.Equals(questState.State, QuestStates.Active, StringComparison.Ordinal))
                {
                    continue;
                }

                var instance = new EscortInstance(_waves, player.CharacterId);
                var start = _waypoints[0];
                instance.NpcX = start.X;
                instance.NpcY = start.Y;
                _instances.Add(player.CharacterId, instance);
                resolutions.Add(new EscortResolution(
                    player.CharacterId,
                    EscortOutcomes.Started,
                    null,
                    instance.NpcX,
                    instance.NpcY));
                Advance(instance, player, resolutions);
            }

            HoldWaves();
        }

        return resolutions;
    }

    // The only credit source: a death the combat engine actually resolved.
    void ICombatKillSink.OnMobKilled(CombatMobKill kill)
    {
        lock (_sync)
        {
            if (!_waveByEntityId.TryGetValue(kill.EntityId, out var recordId) ||
                !_instances.TryGetValue(kill.KillerCharacterId, out var instance))
            {
                return;
            }

            var wave = _waves.First(candidate =>
                string.Equals(candidate.RecordId, recordId, StringComparison.Ordinal));
            var state = instance.Waves[recordId];
            if (state.Status != WaveStatuses.Active ||
                !state.MemberLives.TryGetValue(kill.EntityId, out var generation) ||
                generation != kill.LifeId)
            {
                // Not this instance's fight: a wave it has not activated or has
                // already cleared, or a life other than the one it is fighting.
                return;
            }

            // The sourced credit key — every component authoritative server-side,
            // so claiming the same death twice is a no-op, not a new credit.
            var key = string.Concat(
                instance.InstanceId,
                "|",
                EscortInstance.QuestAttemptId,
                "|",
                wave.RecordId,
                "|",
                kill.LifeId.ToString(CultureInfo.InvariantCulture),
                "|",
                kill.DeathEventId);
            if (!instance.CreditKeys.Add(key))
            {
                return;
            }

            state.CreditedMembers.Add(kill.EntityId);
            if (state.CreditedMembers.Count < wave.Count)
            {
                return;
            }

            state.Status = WaveStatuses.Cleared;
            _deferred.Add(new EscortResolution(
                instance.CharacterId,
                EscortOutcomes.WaveCleared,
                wave.RecordId,
                instance.NpcX,
                instance.NpcY));
            CompleteIfAtEnd(instance, _deferred);
        }
    }

    public bool TryGetNpcPosition(string characterId, out double x, out double y)
    {
        lock (_sync)
        {
            if (_instances.TryGetValue(characterId, out var instance))
            {
                x = instance.NpcX;
                y = instance.NpcY;
                return true;
            }
        }

        x = 0;
        y = 0;
        return false;
    }

    // The read-model half of the same state (work order 30 item 3). The design names the
    // escorted actor by NPC id (`P00_04_ActorId`), not by world entity id, so the entity is
    // resolved from the shipped registry by the record that carries that id: a hardcoded
    // ENT_ string here would be a number nobody approved. Anything but exactly one match
    // answers false, which leaves the anchor canonical instead of moving the wrong actor.
    public bool TryGetEscortPosition(
        string characterId, out string npcEntityId, out double x, out double y)
    {
        if (!TryGetNpcPosition(characterId, out x, out y))
        {
            npcEntityId = string.Empty;
            return false;
        }

        var matches = _entities.All
            .Where(entity => string.Equals(entity.Kind, "NPC", StringComparison.Ordinal) &&
                             entity.RecordId.EndsWith(_actorId, StringComparison.Ordinal))
            .Select(entity => entity.EntityId)
            .Distinct(StringComparer.Ordinal)
            .ToArray();
        if (matches.Length != 1)
        {
            npcEntityId = string.Empty;
            return false;
        }

        npcEntityId = matches[0];
        return true;
    }

    private void Advance(
        EscortInstance instance,
        PlayerSession owner,
        List<EscortResolution> resolutions)
    {
        // The final waypoint's wave still fights after the last commit, so the
        // wave check has to come before the path-complete guard.
        var blockingWave = WaveAt(instance.LastCommittedIndex);
        if (blockingWave is not null)
        {
            var state = instance.Waves[blockingWave.RecordId];
            if (state.Status == WaveStatuses.Pending)
            {
                // Retry a deferred activation: the group may have respawned, or
                // the other owner's fight may have ended.
                TryActivate(instance, blockingWave, resolutions);
            }

            if (state.Status == WaveStatuses.Active)
            {
                AdoptRespawns(instance, blockingWave);
            }

            // Still fighting, or activation failed and is being retried: either
            // way the NPC stays at the checkpoint. Nothing else completes it.
            if (state.Status != WaveStatuses.Cleared)
            {
                return;
            }
        }

        if (instance.WaypointIndex >= _waypoints.Count)
        {
            return;
        }

        if (DistanceToNpc(owner) > _followRange + 1e-9)
        {
            return;
        }

        var target = _waypoints[instance.WaypointIndex];
        var deltaX = target.X - instance.NpcX;
        var deltaY = target.Y - instance.NpcY;
        var distance = Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY));
        if (distance <= _speedPerTick + 1e-9)
        {
            instance.NpcX = target.X;
            instance.NpcY = target.Y;
            CommitWaypoint(instance, resolutions);
            return;
        }

        instance.NpcX += deltaX / distance * _speedPerTick;
        instance.NpcY += deltaY / distance * _speedPerTick;
    }

    private void CommitWaypoint(EscortInstance instance, List<EscortResolution> resolutions)
    {
        var checkpointX = FormatWu(instance.NpcX);
        instance.LastCommittedIndex = instance.WaypointIndex;
        instance.WaypointIndex++;
        resolutions.Add(new EscortResolution(
            instance.CharacterId,
            EscortOutcomes.CheckpointCommitted,
            checkpointX,
            instance.NpcX,
            instance.NpcY));

        var wave = WaveAt(instance.LastCommittedIndex);
        if (wave is null)
        {
            // The approved decision pairs one wave with every checkpoint after the
            // start, so a checkpoint with no wave rule is a data fault — never a
            // free pass to the next waypoint.
            resolutions.Add(new EscortResolution(
                instance.CharacterId,
                EscortOutcomes.WaveActivationFailed,
                $"checkpoint {checkpointX} has no wave rule",
                instance.NpcX,
                instance.NpcY));
            return;
        }

        if (instance.Waves[wave.RecordId].Status == WaveStatuses.Cleared)
        {
            CompleteIfAtEnd(instance, resolutions);
            return;
        }

        TryActivate(instance, wave, resolutions);
    }

    // Brings the checkpoint's wave up for this instance and makes it what stands
    // between the NPC and the next waypoint.
    private bool TryActivate(
        EscortInstance instance,
        AlphaWaveRule wave,
        List<EscortResolution> resolutions)
    {
        var state = instance.Waves[wave.RecordId];
        var members = _waveMembers[wave.RecordId];
        if (members.Count != wave.Count)
        {
            FailActivation(instance, state, resolutions,
                $"wave {wave.RecordId} ships {members.Count} of {wave.Count} " +
                $"required {wave.MobId} actors");
            return false;
        }

        if (!IsHeldByOtherInstance(instance, wave.RecordId))
        {
            foreach (var member in members)
            {
                if (!IsAlive(member))
                {
                    member.ForceRespawn();
                }
            }
        }
        else if (members.Any(member => !IsAlive(member)))
        {
            // Another owner is fighting this shared group now. Re-spawning its
            // dead members would reset their generation and their credit.
            FailActivation(instance, state, resolutions,
                $"wave {wave.RecordId} is held by another owner's active fight");
            return false;
        }

        state.MemberLives.Clear();
        foreach (var member in members)
        {
            state.MemberLives[member.EntityId] = member.LifeId;
        }

        state.CreditedMembers.Clear();
        state.Status = WaveStatuses.Active;
        state.ActivationFailure = null;
        resolutions.Add(new EscortResolution(
            instance.CharacterId,
            EscortOutcomes.WaveActivated,
            wave.RecordId,
            instance.NpcX,
            instance.NpcY));
        return true;
    }

    private static void FailActivation(
        EscortInstance instance,
        WaveState state,
        List<EscortResolution> resolutions,
        string reason)
    {
        state.Status = WaveStatuses.Pending;
        if (string.Equals(state.ActivationFailure, reason, StringComparison.Ordinal))
        {
            // Already reported once; the NPC just stays at the checkpoint.
            return;
        }

        state.ActivationFailure = reason;
        resolutions.Add(new EscortResolution(
            instance.CharacterId,
            EscortOutcomes.WaveActivationFailed,
            reason,
            instance.NpcX,
            instance.NpcY));
    }

    // A member the content respawned under this instance starts a fresh life for
    // the wave: its old death stops counting and it has to be killed again.
    private void AdoptRespawns(EscortInstance instance, AlphaWaveRule wave)
    {
        var state = instance.Waves[wave.RecordId];
        foreach (var member in _waveMembers[wave.RecordId])
        {
            if (state.MemberLives.TryGetValue(member.EntityId, out var generation) &&
                generation == member.LifeId)
            {
                continue;
            }

            state.MemberLives[member.EntityId] = member.LifeId;
            state.CreditedMembers.Remove(member.EntityId);
        }
    }

    private void CompleteIfAtEnd(EscortInstance instance, List<EscortResolution> resolutions)
    {
        if (instance.WaypointIndex < _waypoints.Count || instance.Completed)
        {
            return;
        }

        var lastWave = WaveAt(instance.LastCommittedIndex);
        if (lastWave is null ||
            instance.Waves[lastWave.RecordId].Status != WaveStatuses.Cleared)
        {
            return;
        }

        instance.Completed = true;
        resolutions.Add(new EscortResolution(
            instance.CharacterId,
            EscortOutcomes.Completed,
            null,
            instance.NpcX,
            instance.NpcY));
    }

    private void Wipe(EscortInstance instance, List<EscortResolution> resolutions)
    {
        var restore = _waypoints[instance.LastCommittedIndex];
        instance.NpcX = restore.X;
        instance.NpcY = restore.Y;
        instance.WaypointIndex = instance.LastCommittedIndex + 1;

        var wave = WaveAt(instance.LastCommittedIndex);
        if (wave is not null && instance.Waves[wave.RecordId].Status == WaveStatuses.Active)
        {
            // "pending wave resets with new life IDs": the re-spawn itself is
            // TryActivate's job, and it refuses to touch a group another owner is
            // fighting. A cleared wave is never re-opened.
            instance.Waves[wave.RecordId].Status = WaveStatuses.Pending;
            TryActivate(instance, wave, resolutions);
        }

        resolutions.Add(new EscortResolution(
            instance.CharacterId,
            EscortOutcomes.Wiped,
            $"checkpoint={FormatWu(restore.X)}",
            instance.NpcX,
            instance.NpcY));
    }

    private bool IsHeldByOtherInstance(EscortInstance self, string recordId) =>
        _instances.Values.Any(other =>
            !ReferenceEquals(other, self) &&
            other.Waves[recordId].Status == WaveStatuses.Active);

    private void HoldWaves()
    {
        foreach (var wave in _waves)
        {
            var anyActive = false;
            foreach (var instance in _instances.Values)
            {
                if (instance.Waves[wave.RecordId].Status == WaveStatuses.Active)
                {
                    anyActive = true;
                    break;
                }
            }

            if (anyActive)
            {
                continue;
            }

            foreach (var member in _waveMembers[wave.RecordId])
            {
                if (!IsAlive(member))
                {
                    continue;
                }

                // The world records gate these spawns on the escort passing
                // x=80/120, so the wave only exists while an instance holds it.
                _entities.Despawn(member.EntityId);
            }
        }
    }

    private AlphaWaveRule? WaveAt(int waypointIndex)
    {
        var waveIndex = waypointIndex - 1;
        return waveIndex >= 0 && waveIndex < _waves.Count ? _waves[waveIndex] : null;
    }

    private double DistanceToNpc(PlayerSession owner)
    {
        if (!_instances.TryGetValue(owner.CharacterId, out var instance))
        {
            return double.PositiveInfinity;
        }

        var deltaX = owner.X - instance.NpcX;
        var deltaY = owner.Y - instance.NpcY;
        return Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY));
    }

    private static bool IsAlive(WorldEntityInstance member) =>
        string.Equals(member.State, WorldEntityStates.Alive, StringComparison.Ordinal);

    private static string FormatWu(double value) =>
        value.ToString("0.#", CultureInfo.InvariantCulture);

    private static class WaveStatuses
    {
        public const int Pending = 0;
        public const int Active = 1;
        public const int Cleared = 2;
    }

    private sealed class EscortInstance
    {
        // P1 has no quest-attempt lifecycle, so the attempt component of the
        // sourced credit key stays at its first value.
        public const string QuestAttemptId = "1";

        public EscortInstance(IReadOnlyList<AlphaWaveRule> waves, string characterId)
        {
            CharacterId = characterId;
            foreach (var wave in waves)
            {
                Waves[wave.RecordId] = new WaveState();
            }
        }

        // Derived from (quest, attempt, character) rather than minted per process,
        // so a credit key is reproducible for the same evidence.
        public string InstanceId =>
            $"ESCORT-{QuestId}-{QuestAttemptId}-{CharacterId}";

        public string CharacterId { get; }
        public double NpcX;
        public double NpcY;
        public int WaypointIndex = 1;
        public int LastCommittedIndex;
        public bool OwnerAlive = true;
        public bool Completed;
        public HashSet<string> CreditKeys { get; } = new(StringComparer.Ordinal);
        public Dictionary<string, WaveState> Waves { get; } = new(StringComparer.Ordinal);
    }

    private sealed class WaveState
    {
        public int Status;
        public string? ActivationFailure;
        public Dictionary<string, long> MemberLives { get; } = new(StringComparer.Ordinal);
        public HashSet<string> CreditedMembers { get; } = new(StringComparer.Ordinal);
    }
}
