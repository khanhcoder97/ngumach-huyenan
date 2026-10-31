using System.Collections.Concurrent;
using Server.Health.Contracts;

namespace Server.Health.Gameplay.Quests;

public sealed class PlayerQuestState
{
    public PlayerQuestState(
        string characterId,
        string questId,
        string state,
        string stepId,
        IEnumerable<string> objectiveIds,
        DateTimeOffset updatedAtUtc)
    {
        CharacterId = characterId;
        QuestId = questId;
        State = state;
        StepId = stepId;
        UpdatedAtUtc = updatedAtUtc;
        Revision = 1;

        foreach (var objectiveId in objectiveIds)
        {
            ObjectiveCounters[objectiveId] = 0;
        }
    }

    public string CharacterId { get; }
    public string QuestId { get; }
    public object SyncRoot { get; } = new();

    public string State { get; set; }
    public string StepId { get; set; }
    public Dictionary<string, int> ObjectiveCounters { get; } = new(StringComparer.Ordinal);

    // Internal dedupe keys for server-verified progress. Distinct-record rules use
    // "R:{recordId}", kill-style per-event rules use "E:{eventId}". Not exposed on
    // the wire; progress is read back through ObjectiveCounters.
    public HashSet<string> Contributions { get; } = new(StringComparer.Ordinal);

    public long Revision { get; set; }
    public DateTimeOffset UpdatedAtUtc { get; set; }

    public QuestState ToContract() => new()
    {
        QuestId = QuestId,
        State = State,
        StepId = StepId,
        ObjectiveCounters = new Dictionary<string, int>(ObjectiveCounters, StringComparer.Ordinal),
        Revision = Revision
    };
}

public interface IQuestStateStore
{
    PlayerQuestState? Find(string characterId, string questId);

    PlayerQuestState GetOrAdd(string characterId, string questId, Func<PlayerQuestState> factory);

    IReadOnlyList<PlayerQuestState> GetForCharacter(string characterId);
}

public sealed class InMemoryQuestStateStore : IQuestStateStore
{
    private readonly ConcurrentDictionary<string, PlayerQuestState> _states =
        new(StringComparer.Ordinal);

    public PlayerQuestState? Find(string characterId, string questId) =>
        _states.TryGetValue(Key(characterId, questId), out var state) ? state : null;

    public PlayerQuestState GetOrAdd(
        string characterId,
        string questId,
        Func<PlayerQuestState> factory) =>
        _states.GetOrAdd(Key(characterId, questId), _ => factory());

    public IReadOnlyList<PlayerQuestState> GetForCharacter(string characterId) =>
        _states.Values
            .Where(state => string.Equals(state.CharacterId, characterId, StringComparison.Ordinal))
            .OrderBy(state => state.QuestId, StringComparer.Ordinal)
            .ToList();

    private static string Key(string characterId, string questId) =>
        string.Concat(characterId, "|", questId);
}
