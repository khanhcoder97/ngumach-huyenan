using Server.Health.Contracts;

namespace Server.Health.Gameplay.Inventory;

public static class InventoryErrorCodes
{
    public const string RevisionConflict = "revision_conflict";
    public const string ItemNotFound = "item_not_found";
    public const string InsufficientItems = "insufficient_items";
    public const string InsufficientCurrency = "insufficient_currency";
    public const string SlotOccupied = "slot_occupied";
}

public sealed class InventoryOutcome
{
    public required bool IsSuccess { get; init; }
    public InventorySnapshot? Snapshot { get; init; }
    public string? ErrorCode { get; init; }
    public bool Retryable { get; init; }
    public string? Field { get; init; }

    public static InventoryOutcome Success(InventorySnapshot snapshot) =>
        new() { IsSuccess = true, Snapshot = snapshot };

    public static InventoryOutcome Rejected(
        string errorCode,
        bool retryable,
        string field,
        InventorySnapshot? snapshot = null) =>
        new()
        {
            IsSuccess = false,
            ErrorCode = errorCode,
            Retryable = retryable,
            Field = field,
            Snapshot = snapshot
        };

    public static InventoryOutcome Invalid(string field, InventorySnapshot? snapshot = null) =>
        Rejected(P1ErrorCodes.InvalidPayload, retryable: false, field, snapshot);
}
