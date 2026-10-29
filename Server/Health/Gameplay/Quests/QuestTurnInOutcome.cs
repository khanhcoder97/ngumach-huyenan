using Server.Health.Contracts;

namespace Server.Health.Gameplay.Quests;

public static class QuestTurnInErrorCodes
{
    public const string NpcMismatch = "npc_mismatch";
    public const string OutOfRange = "out_of_range";
    public const string IdempotencyConflict = "idempotency_conflict";
}

public sealed record TurnInFailure(
    string Code,
    bool Retryable,
    IReadOnlyList<string> FieldErrors);

public sealed record TurnInOutcome(TurnInResult? Result, TurnInFailure? Failure)
{
    public bool Accepted => Failure is null;

    public static TurnInOutcome Success(TurnInResult result) => new(result, null);

    public static TurnInOutcome Rejected(
        string code,
        bool retryable,
        params string[] fieldErrors) =>
        new(null, new TurnInFailure(code, retryable, fieldErrors));
}

public interface IQuestTurnInService
{
    TurnInOutcome TurnIn(
        PlayerSession actor,
        string questId,
        string npcId,
        string idempotencyKey);
}