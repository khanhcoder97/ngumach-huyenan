namespace Server.Health.Gameplay.Combat;

public sealed record CombatTarget(
    string EntityId,
    string MapId,
    string FloorId,
    double X,
    double Y,
    bool Alive)
{
    public bool IsAlive => Alive;
}

public interface ICombatTargetProvider
{
    bool TryResolve(string targetId, out CombatTarget? target);
}

public sealed class InMemoryCombatTargetProvider : ICombatTargetProvider
{
    private readonly System.Collections.Concurrent.ConcurrentDictionary<string, CombatTarget> _targets =
        new(StringComparer.Ordinal);

    public void Upsert(CombatTarget target) => _targets[target.EntityId] = target;

    public bool Remove(string targetId) => _targets.TryRemove(targetId, out _);

    public bool TryResolve(string targetId, out CombatTarget? target) =>
        _targets.TryGetValue(targetId, out target);
}

public sealed class WorldEntityTargetProvider : ICombatTargetProvider
{
    private readonly World.WorldEntityRegistry _entities;

    public WorldEntityTargetProvider(World.WorldEntityRegistry entities)
    {
        _entities = entities;
    }

    public bool TryResolve(string targetId, out CombatTarget? target)
    {
        if (_entities.TryGet(targetId, out var entity) &&
            (string.Equals(entity.Kind, World.WorldEntityKinds.Mob, StringComparison.Ordinal) ||
             string.Equals(entity.Kind, World.WorldEntityKinds.Boss, StringComparison.Ordinal)))
        {
            target = new CombatTarget(
                entity.EntityId,
                entity.MapId,
                entity.FloorId,
                entity.X,
                entity.Y,
                Alive: string.Equals(
                    entity.State, World.WorldEntityStates.Alive, StringComparison.Ordinal));
            return true;
        }

        target = null;
        return false;
    }
}

public sealed class CompositeCombatTargetProvider : ICombatTargetProvider
{
    private readonly IReadOnlyList<ICombatTargetProvider> _providers;

    public CompositeCombatTargetProvider(params ICombatTargetProvider[] providers)
    {
        _providers = providers;
    }

    public bool TryResolve(string targetId, out CombatTarget? target)
    {
        foreach (var provider in _providers)
        {
            if (provider.TryResolve(targetId, out target))
            {
                return true;
            }
        }

        target = null;
        return false;
    }
}
