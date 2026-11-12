using Server.Health.Contracts;

namespace Server.Health.Gameplay.Quests;

public sealed record QuestFailure(string Code, bool Retryable, IReadOnlyList<string> FieldErrors);

public sealed record QuestOutcome(QuestState? State, QuestFailure? Failure)
{
    public bool Accepted => Failure is null;

    public static QuestOutcome Success(QuestState state) => new(state, null);

    public static QuestOutcome Rejected(string code, bool retryable, params string[] fieldErrors) =>
        new(null, new QuestFailure(code, retryable, fieldErrors));

    public static QuestOutcome InvalidTransition(QuestState state) =>
        new(state, new QuestFailure(QuestErrorCodes.InvalidTransition, false, ["state"]));
}

public static class QuestErrorCodes
{
    public const string UnknownQuest = "unknown_quest";
    public const string QuestNotFound = "quest_not_found";
    public const string InvalidTransition = "invalid_transition";
}
