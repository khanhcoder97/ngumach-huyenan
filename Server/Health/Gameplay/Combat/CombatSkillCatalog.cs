namespace Server.Health.Gameplay.Combat;

public interface ICombatSkillCatalog
{
    int Count { get; }

    bool TryGet(string skillId, out CombatSkillDefinition skill);
}

public sealed class CombatSkillCatalog : ICombatSkillCatalog
{
    private readonly IReadOnlyDictionary<string, CombatSkillDefinition> _skills;

    public CombatSkillCatalog(IReadOnlyDictionary<string, CombatSkillDefinition> skills)
    {
        _skills = skills;
    }

    public int Count => _skills.Count;

    public bool TryGet(string skillId, out CombatSkillDefinition skill)
    {
        if (_skills.TryGetValue(skillId, out var found))
        {
            skill = found;
            return true;
        }

        skill = null!;
        return false;
    }
}
