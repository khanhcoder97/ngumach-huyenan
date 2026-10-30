using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

public interface IQuestService
{
    QuestOutcome GetState(string characterId, string questId);

    IReadOnlyList<QuestState> GetStates(string characterId);

    QuestOutcome Accept(PlayerSession actor, string questId);

    // Server-owned progress: the caller has already verified the event (map, floor,
    // range, LOS, claim). Each event may contribute at most once; returns the full
    // QuestState of every quest whose revision changed.
    IReadOnlyList<QuestState> RecordVerifiedEvent(
        PlayerSession actor,
        string eventId,
        string eventType,
        string recordId,
        string mapId);

    QuestOutcome TurnIn(PlayerSession actor, string questId);

    // Internal rollback primitive for the turn-in orchestrator: COMPLETED →
    // READY_TO_TURN_IN, revision restored. Only valid as the compensating step
    // of a turn-in transaction that already holds the actor lock.
    QuestOutcome RevertTurnIn(PlayerSession actor, string questId);

    QuestOutcome Fail(PlayerSession actor, string questId);
}
