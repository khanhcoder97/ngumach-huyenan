namespace Server.Health.Gameplay.Combat;

public sealed record CombatTarget(string EntityId, string MapId, double X, double Y, int Hp)
{
    public bool IsAlive => Hp > 0;
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
