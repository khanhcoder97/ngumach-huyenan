namespace Server.Health.Gameplay.Inventory;

public sealed class InventoryMutation
{
    public long? ExpectedRevision { get; init; }
    public IReadOnlyList<ItemGrant>? AddItems { get; init; }
    public IReadOnlyList<ItemRemoval>? RemoveItems { get; init; }
    public IReadOnlyList<CurrencyDelta>? CurrencyDeltas { get; init; }
}

public sealed class ItemGrant
{
    public required string TemplateId { get; init; }
    public int Stack { get; init; }
    public required string Location { get; init; }
    public string? Slot { get; init; }
    public int Durability { get; init; }
}

public sealed class ItemRemoval
{
    public required string InstanceId { get; init; }
    public int Stack { get; init; }
}

public sealed class CurrencyDelta
{
    public required string CurrencyId { get; init; }
    public long Amount { get; init; }
}
