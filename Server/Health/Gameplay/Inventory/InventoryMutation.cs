namespace Server.Health.Gameplay.Inventory;

public sealed class InventoryMutation
{
    public long? ExpectedRevision { get; init; }
    public IReadOnlyList<ItemGrant>? AddItems { get; init; }
    public IReadOnlyList<ItemRemoval>? RemoveItems { get; init; }
    public IReadOnlyList<ItemMove>? MoveItems { get; init; }
    public IReadOnlyList<CurrencyDelta>? CurrencyDeltas { get; init; }
}

// A move is server-internal: it relocates one existing instance and requires
// the caller to state the location it expects to find, so a stale plan cannot
// quietly move an item that something else already moved.
public sealed class ItemMove
{
    public required string InstanceId { get; init; }
    public required string FromLocation { get; init; }
    public required string ToLocation { get; init; }
    public string? Slot { get; init; }

    // The twelve-slot token a v2 equip is placing this item into, when the write came
    // from that vocabulary. Occupancy is counted on it when present, which is what
    // lets v2 hold two accessories at once while v1 keeps seeing one ACCESSORY.
    public string? SlotV2 { get; init; }
}

public sealed class ItemGrant
{
    public required string TemplateId { get; init; }
    public int Stack { get; init; }
    public required string Location { get; init; }
    public string? Slot { get; init; }

    // Null means "the caller did not say", which is not the same statement as 0:
    // an unspecified grant takes the canonical catalog's durability, while an
    // explicit number is honored as given.
    public int? Durability { get; init; }
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
