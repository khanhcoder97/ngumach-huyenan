using System.Text.Json.Serialization;

namespace Server.Health.Contracts;

public static class InventoryLocations
{
    public const string Bag = "BAG";
    public const string Equipped = "EQUIPPED";
    public const string Bank = "BANK";

    public static bool IsValid(string? value) =>
        string.Equals(value, Bag, StringComparison.Ordinal) ||
        string.Equals(value, Equipped, StringComparison.Ordinal) ||
        string.Equals(value, Bank, StringComparison.Ordinal);
}

public sealed class InventorySnapshot
{
    public required long InventoryRevision { get; init; }
    public required IReadOnlyList<InventoryItem> Items { get; init; }
    public required IReadOnlyList<InventoryCurrency> Currencies { get; init; }
}

public sealed class InventoryItem
{
    public required string InstanceId { get; init; }
    public required string TemplateId { get; init; }
    public required int Stack { get; init; }
    public required string Location { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? Slot { get; init; }

    public required int Durability { get; init; }
    public required int Version { get; init; }
}

public sealed class InventoryCurrency
{
    public required string CurrencyId { get; init; }
    public required long Amount { get; init; }
}
