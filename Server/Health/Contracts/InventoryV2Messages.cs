using System.Text.Json.Serialization;

namespace Server.Health.Contracts;

// QOD-21 Q3: the approved v2 inventory read model, from DESIGN-BM-Q3-20261104
// `inventory` (decision `V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT`) and
// DESIGN-BM-ALPHA-20261103 `inventory`. It sits **beside** the frozen v1 snapshot
// the v1 five-token contract and its routes do not change, and this one carries the
// twelve closed slots plus the 100-slot bag the alpha design states.
//
// The projection rule is the decision's `incompatibleV1Projection`: an equipped item
// that cannot be named in the twelve slots is reported explicitly in `unsupported`,
// never quietly dropped. `slots` always holds all twelve entries in design order so
// a client can bind positions without inferring them from what happens to be worn.
public sealed class InventorySnapshotV2
{
    public int SchemaVersion { get; init; } = 2;

    // The migration the decision chose, carried verbatim so a client can tell which
    // slot vocabulary it is reading without consulting a second document.
    public required string SlotSpec { get; init; }

    public required long InventoryRevision { get; init; }

    public required int BagSlots { get; init; }

    public required IReadOnlyList<InventoryV2SlotEntry> Slots { get; init; }

    public required IReadOnlyList<InventoryItemV2> Bag { get; init; }

    public required IReadOnlyList<InventoryV2UnsupportedItem> Unsupported { get; init; }

    public required IReadOnlyList<InventoryCurrency> Currencies { get; init; }
}

public sealed class InventoryV2SlotEntry
{
    // One of the twelve approved tokens, in design order.
    public required string SlotId { get; init; }

    // Null means the slot is empty. The field is always written so an empty slot and
    // a missing slot cannot be confused by a client parser.
    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public InventoryItemV2? Item { get; init; }
}

public sealed class InventoryItemV2
{
    public required string InstanceId { get; init; }
    public required string TemplateId { get; init; }
    public required int Stack { get; init; }
    public required string Location { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public string? SlotId { get; init; }

    public required int Durability { get; init; }
    public required int Version { get; init; }
}

// An equipped item the twelve-slot vocabulary cannot name. `reason` is a closed code;
// `sourceSlot` repeats whatever the store holds so the gap is diagnosable from the
// response alone. The item itself stays present here — dropping it would hide a
// piece of gear the player is wearing.
public sealed class InventoryV2UnsupportedItem
{
    public required string InstanceId { get; init; }
    public required string TemplateId { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public string? SourceSlot { get; init; }

    public required string Reason { get; init; }
}

public static class InventoryV2UnsupportedReasons
{
    // The stored slot is not one of the twelve tokens and the catalog cannot resolve
    // the item to one.
    public const string UnmappedSlot = "UNMAPPED_SLOT";

    public static bool IsKnown(string? value) => value is UnmappedSlot;
}

// Request envelopes. Every member is nullable so a malformed request answers with
// the exact field names that failed, the same way the v1 envelopes do; the schemas
// decide what is legal.
public sealed class EquipV2Envelope
{
    public int? SchemaVersion { get; init; }
    public string? RequestId { get; init; }
    public string? IdempotencyKey { get; init; }
    public string? SentAtUtc { get; init; }
    public string? CharacterId { get; init; }
    public EquipV2Intent? Payload { get; init; }
}

public sealed class EquipV2Intent
{
    public string? ItemInstanceId { get; init; }
    public long? ExpectedRevision { get; init; }
}

public sealed class UnequipV2Envelope
{
    public int? SchemaVersion { get; init; }
    public string? RequestId { get; init; }
    public string? IdempotencyKey { get; init; }
    public string? SentAtUtc { get; init; }
    public string? CharacterId { get; init; }
    public UnequipV2Intent? Payload { get; init; }
}

public sealed class UnequipV2Intent
{
    // The token to empty, from the twelve.
    public string? SlotId { get; init; }
    public long? ExpectedRevision { get; init; }
}

public sealed class P1InventoryV2Response
{
    public int SchemaVersion { get; init; } = 2;
    public required string RequestId { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? SessionId { get; init; }

    public required string ServerTimeUtc { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public InventorySnapshotV2? Result { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public P1Error? Error { get; init; }
}
