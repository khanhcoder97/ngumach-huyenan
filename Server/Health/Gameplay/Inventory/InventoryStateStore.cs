using System.Collections.Concurrent;
using Server.Health.Contracts;

namespace Server.Health.Gameplay.Inventory;

public sealed class PlayerInventoryState
{
    internal PlayerInventoryState(string characterId)
    {
        CharacterId = characterId;
    }

    public string CharacterId { get; }
    public object SyncRoot { get; } = new();
    public long Revision { get; private set; }

    internal List<InventoryItemEntry> Items { get; } = new();
    internal Dictionary<string, long> Currencies { get; } = new(StringComparer.Ordinal);

    internal void AdvanceRevision() => Revision++;

    internal InventoryItemEntry? FindItem(string instanceId)
    {
        foreach (var item in Items)
        {
            if (string.Equals(item.InstanceId, instanceId, StringComparison.Ordinal))
            {
                return item;
            }
        }

        return null;
    }

    internal long GetCurrency(string currencyId) =>
        Currencies.GetValueOrDefault(currencyId);

    internal InventorySnapshot ToContract()
    {
        var items = new List<InventoryItem>(Items.Count);
        foreach (var item in Items)
        {
            items.Add(new InventoryItem
            {
                InstanceId = item.InstanceId,
                TemplateId = item.TemplateId,
                Stack = item.Stack,
                Location = item.Location,
                Slot = item.Slot,
                Durability = item.Durability,
                Version = item.Version
            });
        }

        var currencies = new List<InventoryCurrency>(Currencies.Count);
        foreach (var pair in Currencies.OrderBy(currency => currency.Key, StringComparer.Ordinal))
        {
            currencies.Add(new InventoryCurrency
            {
                CurrencyId = pair.Key,
                Amount = pair.Value
            });
        }

        return new InventorySnapshot
        {
            InventoryRevision = Revision,
            Items = items,
            Currencies = currencies
        };
    }
}

internal sealed class InventoryItemEntry
{
    public required string InstanceId { get; init; }
    public required string TemplateId { get; init; }
    public required string Location { get; set; }
    public required int Durability { get; init; }
    public int Stack { get; set; }

    // The slot in the vocabulary the write used: a v1 equip names one of the five
    // frozen tokens, a v2 equip names the collapsed v1 token of its twelve-slot pair
    // (or nothing, for LEGS and GLOVES, which v1 has no word for). Kept separate from
    // SlotV2 so the v1 wire payload stays exactly the five-token document it is.
    public string? Slot { get; set; }

    // Server-side only: the precise twelve-slot token a v2 write placed this item in.
    // It is never part of the v1 snapshot, so no v1 payload grows a field, and it is
    // what makes two accessories (a necklace and a left ring) two occupants instead
    // of one fighting over ACCESSORY.
    public string? SlotV2 { get; set; }
    public int Version { get; set; } = 1;
}

public interface IInventoryStateStore
{
    PlayerInventoryState? Find(string characterId);

    PlayerInventoryState GetOrAdd(string characterId);
}

public sealed class InMemoryInventoryStateStore : IInventoryStateStore
{
    private readonly ConcurrentDictionary<string, PlayerInventoryState> _states =
        new(StringComparer.Ordinal);

    public PlayerInventoryState? Find(string characterId) =>
        _states.TryGetValue(characterId, out var state) ? state : null;

    public PlayerInventoryState GetOrAdd(string characterId) =>
        _states.GetOrAdd(characterId, id => new PlayerInventoryState(id));
}
