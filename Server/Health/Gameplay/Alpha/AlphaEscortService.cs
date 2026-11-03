using System.Globalization;
using Server.Health.Contracts;
using Server.Health.Gameplay.Quests;
using Server.Health.World;

namespace Server.Health.Gameplay.Alpha;

public static class EscortOutcomes
{
    public const string Started = "STARTED";
    public const string CheckpointCommitted = "CHECKPOINT_COMMITTED";
    public const string WaveActivated = "WAVE_ACTIVATED";
    public const string WaveCleared = "WAVE_CLEARED";
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

// QOD-21 Q1c: the P00-04 escort (DESIGN-BM-ALPHA-20261103 questRules.P00-04)
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
// Interpretation of the sourced rules (no invented numbers): the NPC walks
// the waypoint path at 3 wu/s only while the owner is alive, on the map and
// within 12 wu of the NPC. Arriving at a checkpoint commits it and spawns its
// wave with fresh life IDs; the NPC waits at the checkpoint until every wave
// member is dead (the wave is cleared), then resumes on the same tick.
// Committing the final waypoint with no pending wave completes the escort
// (so a bundle without the wave entities still walks the path and finishes).
// An owner death restores
// the NPC to the last committed checkpoint, resets an in-progress wave with
// new life IDs (re-fight) and never respawns a cleared wave (not farmable).
// The P1 quest runtime has no attempt lifecycle, so the questAttemptId
// component of the credit key is constant; the combat engine's deathEventId
// is not observable domain-side, so the machine mints its own per
// (member, life) key when it observes the registry death. Wave members are
// shared world spawns (the content ships one group per wave), so two owners
// fighting the same wave share the fight; a wipe reset re-lives the shared
// members. The machine holds every wave member dead unless an instance has
// the wave active, which also cancels the MobSpawnGroupService respawn of a
// cleared wave.
public sealed class AlphaEscortService
{
    private const string QuestId = "P00-04";

    private readonly string _mapId;
    private readonly double _speedPerTick;
    private readonly double _followRange;
    private readonly IReadOnlyList<AlphaPoint> _waypoints;
    private readonly IReadOnlyList<AlphaWaveRule> _waves;
    private readonly IQuestService _quests;
    private readonly WorldEntityRegistry _entities;
    private readonly object _sync = new();
    private readonly Dictionary<string, List<WorldEntityInstance>> _waveMembers =
        new(StringComparer.Ordinal);
    private readonly Dictionary<string, EscortInstance> _instances =
        new(StringComparer.Ordinal);

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
        _speedPerTick = rules.P00_04_SpeedWuPerSecond / ServerClock.TicksPerSecond;
        _followRange = rules.P00_04_FollowRangeWu;
        _waypoints = rules.P00_04_Waypoints;
        _waves = [rules.P00_04_WaveA, rules.P00_04_WaveB];
        _quests = quests;
        _entities = entities;
        foreach (var wave in _waves)
        {
            _waveMembers[wave.RecordId] = entities.All
                .Where(entity =>
                    string.Equals(entity.GroupId, wave.RecordId, StringComparison.Ordinal) &&
                    string.Equals(entity.Kind, WorldEntityKinds.Mob, StringComparison.Ordinal))
                .OrderBy(entity => entity.MemberIndex)
                .ToList();
        }
    }

    public IReadOnlyList<EscortResolution> Tick(
        IReadOnlyList<PlayerSession> players,
        long tick)
    {
        if (_waypoints.Count < 2)
        {
            return Array.Empty<EscortResolution>();
        }

        var targets = new Dictionary<string, PlayerSession>(StringComparer.Ordinal);
        foreach (var player in players)
        {
            targets[player.CharacterId] = player;
        }

        var resolutions = new List<EscortResolution>();
        lock (_sync)
        {
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

    private void Advance(
        EscortInstance instance,
        PlayerSession owner,
        List<EscortResolution> resolutions)
    {
        // The final waypoint's wave still fights after the last commit, so
        // the wave check must come before the path-complete guard.
        var blockingWave = WaveAt(instance.LastCommittedIndex);
        if (blockingWave is not null && instance.Waves[blockingWave.RecordId].Status == WaveStatuses.Active)
        {
            ObserveWave(instance, blockingWave, resolutions);
            if (instance.Waves[blockingWave.RecordId].Status == WaveStatuses.Active)
            {
                return;
            }

            // The wave cleared this tick: the NPC resumes on the same tick,
            // unless that was the final waypoint.
            if (instance.WaypointIndex >= _waypoints.Count)
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
        if (wave is null || instance.Waves[wave.RecordId].Status == WaveStatuses.Cleared)
        {
            CompleteIfAtEnd(instance, resolutions);
            return;
        }

        var members = _waveMembers[wave.RecordId];
        if (members.Count == 0)
        {
            CompleteIfAtEnd(instance, resolutions);
            return;
        }

        var state = instance.Waves[wave.RecordId];
        var alive = members.FirstOrDefault(member =>
            string.Equals(member.State, WorldEntityStates.Alive, StringComparison.Ordinal));
        if (alive is null)
        {
            foreach (var member in members)
            {
                member.ForceRespawn();
            }

            state.Generation = members[0].LifeId;
        }
        else
        {
            state.Generation = alive.LifeId;
        }

        state.Status = WaveStatuses.Active;
        resolutions.Add(new EscortResolution(
            instance.CharacterId,
            EscortOutcomes.WaveActivated,
            wave.RecordId,
            instance.NpcX,
            instance.NpcY));
    }

    private void ObserveWave(
        EscortInstance instance,
        AlphaWaveRule wave,
        List<EscortResolution> resolutions)
    {
        var members = _waveMembers[wave.RecordId];
        if (members.Count == 0)
        {
            return;
        }

        var state = instance.Waves[wave.RecordId];
        var alive = members.FirstOrDefault(member =>
            string.Equals(member.State, WorldEntityStates.Alive, StringComparison.Ordinal));
        if (alive is not null && alive.LifeId != state.Generation)
        {
            state.Generation = alive.LifeId;
            state.Credits = 0;
        }

        foreach (var member in members)
        {
            if (member.LifeId != state.Generation ||
                !string.Equals(member.State, WorldEntityStates.Dead, StringComparison.Ordinal))
            {
                continue;
            }

            if (instance.CreditedLives.TryGetValue(member.EntityId, out var credited) &&
                credited == member.LifeId)
            {
                continue;
            }

            var key = string.Concat(
                instance.InstanceId,
                "|",
                EscortInstance.QuestAttemptId,
                "|",
                wave.RecordId,
                "|",
                member.LifeId.ToString(CultureInfo.InvariantCulture),
                "|",
                Guid.NewGuid().ToString("N"));
            if (!instance.CreditKeys.Add(key))
            {
                continue;
            }

            instance.CreditedLives[member.EntityId] = member.LifeId;
            state.Credits++;
        }

        if (state.Credits < members.Count)
        {
            return;
        }

        state.Status = WaveStatuses.Cleared;
        resolutions.Add(new EscortResolution(
            instance.CharacterId,
            EscortOutcomes.WaveCleared,
            wave.RecordId,
            instance.NpcX,
            instance.NpcY));
        CompleteIfAtEnd(instance, resolutions);
    }

    private void CompleteIfAtEnd(EscortInstance instance, List<EscortResolution> resolutions)
    {
        if (instance.WaypointIndex >= _waypoints.Count && !instance.Completed)
        {
            instance.Completed = true;
            resolutions.Add(new EscortResolution(
                instance.CharacterId,
                EscortOutcomes.Completed,
                null,
                instance.NpcX,
                instance.NpcY));
        }
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
            var members = _waveMembers[wave.RecordId];
            foreach (var member in members)
            {
                member.ForceRespawn();
            }

            var state = instance.Waves[wave.RecordId];
            state.Generation = members[0].LifeId;
            state.Credits = 0;
        }

        resolutions.Add(new EscortResolution(
            instance.CharacterId,
            EscortOutcomes.Wiped,
            $"checkpoint={FormatWu(restore.X)}",
            instance.NpcX,
            instance.NpcY));
    }

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
                if (!string.Equals(member.State, WorldEntityStates.Dead, StringComparison.Ordinal))
                {
                    _entities.Despawn(member.EntityId);
                }
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
        public const string QuestAttemptId = "1";

        public EscortInstance(IReadOnlyList<AlphaWaveRule> waves, string characterId)
        {
            CharacterId = characterId;
            foreach (var wave in waves)
            {
                Waves[wave.RecordId] = new WaveState();
            }
        }

        public string InstanceId { get; } = Guid.NewGuid().ToString("N");
        public string CharacterId { get; }
        public double NpcX;
        public double NpcY;
        public int WaypointIndex = 1;
        public int LastCommittedIndex;
        public bool OwnerAlive = true;
        public bool Completed;
        public HashSet<string> CreditKeys { get; } = new(StringComparer.Ordinal);
        public Dictionary<string, long> CreditedLives { get; } = new(StringComparer.Ordinal);
        public Dictionary<string, WaveState> Waves { get; } = new(StringComparer.Ordinal);
    }

    private sealed class WaveState
    {
        public int Status;
        public long Generation;
        public int Credits;
    }
}
