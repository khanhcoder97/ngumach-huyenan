using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

public interface IQuestService
{
    QuestOutcome GetState(string characterId, string questId);

    IReadOnlyList<QuestState> GetStates(string characterId);

    QuestOutcome Accept(PlayerSession actor, string questId);

    QuestOutcome RecordObjective(
        PlayerSession actor,
        string questId,
        string objectiveId,
        int amount);

    QuestOutcome TurnIn(PlayerSession actor, string questId);

    QuestOutcome Fail(PlayerSession actor, string questId);
}
