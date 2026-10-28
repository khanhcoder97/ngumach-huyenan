using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

public static class QuestAcceptErrorCodes
{
    public const string NpcMismatch = "npc_mismatch";
    public const string OutOfRange = "out_of_range";
    public const string PrerequisiteNotMet = "prerequisite_not_met";
    public const string IdempotencyConflict = "idempotency_conflict";
    public const string RevisionConflict = "revision_conflict";
}

public sealed record QuestAcceptFailure(
    string Code,
    bool Retryable,
    IReadOnlyList<string> FieldErrors);

public sealed record QuestAcceptOutcome(QuestState? State, QuestAcceptFailure? Failure)
{
    public bool Accepted => Failure is null;

    public static QuestAcceptOutcome Success(QuestState state) => new(state, null);

    public static QuestAcceptOutcome Rejected(
        string code,
        bool retryable,
        QuestState? state,
        params string[] fieldErrors) =>
        new(state, new QuestAcceptFailure(code, retryable, fieldErrors));
}

public interface IQuestAcceptService
{
    QuestAcceptOutcome Accept(
        PlayerSession actor,
        string questId,
        string npcId,
        string idempotencyKey);
}
