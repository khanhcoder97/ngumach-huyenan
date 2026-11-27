namespace Server.Health.World;

// QOD-17 manifest groups: members respawn together only after the whole group
// is cleared (manifest respawn_seconds), never individually. Partial deaths
// keep the remaining members dead until the group is cleared; a respawn bumps
// every member's lifeId with fresh HP.
public sealed class MobSpawnGroupService
{
    private readonly WorldEntityRegistry _entities;
    private readonly IServerClock _clock;
    private readonly Dictionary<string, GroupState> _groups = new(StringComparer.Ordinal);

    public MobSpawnGroupService(WorldEntityRegistry entities, IServerClock clock)
    {
        _entities = entities;
        _clock = clock;
        foreach (var entity in entities.All)
        {
            if (entity.GroupId is not { } groupId)
            {
                continue;
            }

            if (!_groups.TryGetValue(groupId, out var state))
            {
                state = new GroupState(entity.GroupRespawnSeconds);
                _groups[groupId] = state;
            }

            state.MemberIds.Add(entity.EntityId);
        }
    }

    public int GroupCount => _groups.Count;

    public int MemberCount(string groupId) =>
        _groups.TryGetValue(groupId, out var state) ? state.MemberIds.Count : 0;

    public int Tick()
    {
        var now = _clock.UtcNow;
        var respawned = 0;
        foreach (var state in _groups.Values)
        {
            var allDead = true;
            foreach (var memberId in state.MemberIds)
            {
                if (!_entities.TryGet(memberId, out var member) ||
                    !string.Equals(member.State, WorldEntityStates.Dead, StringComparison.Ordinal))
                {
                    allDead = false;
                    break;
                }
            }

            if (!allDead)
            {
                state.ClearedAt = null;
                continue;
            }

            state.ClearedAt ??= now;
            if (now < state.ClearedAt.Value.AddSeconds(state.RespawnSeconds))
            {
                continue;
            }

            foreach (var memberId in state.MemberIds)
            {
                if (_entities.TryGet(memberId, out var member))
                {
                    member.ForceRespawn();
                    respawned++;
                }
            }

            state.ClearedAt = null;
        }

        return respawned;
    }

    private sealed class GroupState
    {
        public GroupState(int respawnSeconds)
        {
            RespawnSeconds = respawnSeconds;
        }

        public int RespawnSeconds { get; }
        public List<string> MemberIds { get; } = [];
        public DateTimeOffset? ClearedAt { get; set; }
    }
}
