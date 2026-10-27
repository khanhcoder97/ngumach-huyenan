using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Teleport;

public static class TeleportErrorCodes
{
    public const string InvalidMap = "invalid_map";
    public const string OutOfBounds = "out_of_bounds";
    public const string InvalidReason = "invalid_reason";
    public const string InvalidCondition = "invalid_condition";
}

public sealed class TeleportOutcome
{
    public required bool IsSuccess { get; init; }
    public WorldSnapshot? Snapshot { get; init; }
    public string? ErrorCode { get; init; }
    public bool Retryable { get; init; }
    public string? Field { get; init; }

    public static TeleportOutcome Success(WorldSnapshot snapshot) =>
        new() { IsSuccess = true, Snapshot = snapshot };

    public static TeleportOutcome Rejected(
        string errorCode,
        bool retryable,
        string field,
        WorldSnapshot? snapshot = null) =>
        new()
        {
            IsSuccess = false,
            ErrorCode = errorCode,
            Retryable = retryable,
            Field = field,
            Snapshot = snapshot
        };

    public static TeleportOutcome Invalid(string field, WorldSnapshot? snapshot = null) =>
        Rejected(P1ErrorCodes.InvalidPayload, retryable: false, field, snapshot);
}
