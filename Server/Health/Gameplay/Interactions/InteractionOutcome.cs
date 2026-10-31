using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Interactions;

public static class InteractionErrorCodes
{
    public const string TargetNotFound = "target_not_found";
    public const string InvalidTarget = "invalid_target";
    public const string OutOfRange = "out_of_range";
    public const string TargetNotAvailable = "target_not_available";
    public const string ProfessionLevelInsufficient = "profession_level_insufficient";
    public const string IdempotencyConflict = "idempotency_conflict";
}

public sealed record InteractionFailure(
    string Code,
    bool Retryable,
    IReadOnlyList<string> FieldErrors);

public sealed record InteractionOutcome(InteractResult? Result, InteractionFailure? Failure)
{
    public bool Accepted => Failure is null;

    public static InteractionOutcome Success(InteractResult result) => new(result, null);

    public static InteractionOutcome Rejected(
        string code,
        bool retryable,
        params string[] fieldErrors) =>
        new(null, new InteractionFailure(code, retryable, fieldErrors));
}

public interface IInteractionService
{
    InteractionOutcome Interact(
        PlayerSession actor,
        string targetId,
        string idempotencyKey);
}
