namespace Server.Health.Gameplay.Quests;

public interface IQuestCatalog
{
    int Count { get; }

    bool TryGet(string questId, out QuestDefinition definition);
}

public sealed class QuestCatalog : IQuestCatalog
{
    private readonly IReadOnlyDictionary<string, QuestDefinition> _quests;

    public QuestCatalog(IReadOnlyDictionary<string, QuestDefinition> quests)
    {
        _quests = quests;
    }

    public int Count => _quests.Count;

    public bool TryGet(string questId, out QuestDefinition definition)
    {
        if (_quests.TryGetValue(questId, out var found))
        {
            definition = found;
            return true;
        }

        definition = null!;
        return false;
    }
}
