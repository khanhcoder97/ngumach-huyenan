using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Inventory;

public sealed class InMemoryInventoryService : IInventoryService
{
    private readonly IInventoryStateStore _states;

    public InMemoryInventoryService(IInventoryStateStore states)
    {
        _states = states;
    }

    public InventorySnapshot GetSnapshot(string characterId)
    {
        if (!P1Validation.IsCharacterId(characterId))
        {
            return EmptySnapshot();
        }

        var state = _states.Find(characterId);
        if (state is null)
        {
            return EmptySnapshot();
        }

        lock (state.SyncRoot)
        {
            return state.ToContract();
        }
    }

    public InventoryOutcome Apply(PlayerSession actor, InventoryMutation? mutation)
    {
        ArgumentNullException.ThrowIfNull(actor);

        if (!P1Validation.IsCharacterId(actor.CharacterId))
        {
            return InventoryOutcome.Invalid("characterId");
        }

        var invalidField = InventoryValidation.Validate(
            mutation, out var adds, out var removes, out var deltas);
        if (invalidField is not null)
        {
            return InventoryOutcome.Invalid(invalidField);
        }

        var state = _states.GetOrAdd(actor.CharacterId);
        lock (state.SyncRoot)
        {
            var current = state.ToContract();
            if (mutation!.ExpectedRevision is { } expected && expected != state.Revision)
            {
                return InventoryOutcome.Rejected(
                    InventoryErrorCodes.RevisionConflict, retryable: true,
                    "expectedRevision", current);
            }

            var removalTotals = new Dictionary<string, long>(StringComparer.Ordinal);
            for (var index = 0; index < removes.Count; index++)
            {
                var removal = removes[index];
                var item = state.FindItem(removal.InstanceId);
                if (item is null)
                {
                    return InventoryOutcome.Rejected(
                        InventoryErrorCodes.ItemNotFound, retryable: false,
                        $"removeItems[{index}].instanceId", current);
                }

                var total = removalTotals.GetValueOrDefault(removal.InstanceId) + removal.Stack;
                if (total > item.Stack)
                {
                    return InventoryOutcome.Rejected(
                        InventoryErrorCodes.InsufficientItems, retryable: false,
                        $"removeItems[{index}].stack", current);
                }

                removalTotals[removal.InstanceId] = total;
            }

            var currencyAfter = new Dictionary<string, long>(StringComparer.Ordinal);
            try
            {
                var currencyUpdates = new Dictionary<string, long>(StringComparer.Ordinal);
                foreach (var delta in deltas)
                {
                    var total = checked(
                        currencyUpdates.GetValueOrDefault(delta.CurrencyId) + delta.Amount);
                    currencyUpdates[delta.CurrencyId] = total;
                }

                foreach (var pair in currencyUpdates)
                {
                    var next = checked(state.GetCurrency(pair.Key) + pair.Value);
                    if (next < 0)
                    {
                        return InventoryOutcome.Rejected(
                            InventoryErrorCodes.InsufficientCurrency, retryable: false,
                            $"currencyDeltas.{pair.Key}", current);
                    }

                    currencyAfter[pair.Key] = next;
                }
            }
            catch (OverflowException)
            {
                return InventoryOutcome.Invalid("currencyDeltas", current);
            }

            var occupiedSlots = new HashSet<string>(StringComparer.Ordinal);
            foreach (var item in state.Items)
            {
                if (string.Equals(item.Location, InventoryLocations.Equipped, StringComparison.Ordinal) &&
                    item.Slot is not null)
                {
                    occupiedSlots.Add(item.Slot);
                }
            }

            for (var index = 0; index < adds.Count; index++)
            {
                var add = adds[index];
                if (!string.Equals(add.Location, InventoryLocations.Equipped, StringComparison.Ordinal) ||
                    add.Slot is null)
                {
                    continue;
                }

                if (!occupiedSlots.Add(add.Slot))
                {
                    return InventoryOutcome.Rejected(
                        InventoryErrorCodes.SlotOccupied, retryable: false,
                        $"addItems[{index}].slot", current);
                }
            }

            foreach (var add in adds)
            {
                state.Items.Add(new InventoryItemEntry
                {
                    InstanceId = $"ITM_{Guid.NewGuid():N}".ToUpperInvariant(),
                    TemplateId = add.TemplateId,
                    Stack = add.Stack,
                    Location = add.Location,
                    Slot = add.Slot,
                    Durability = add.Durability
                });
            }

            foreach (var removal in removes)
            {
                var item = state.FindItem(removal.InstanceId);
                if (item is null)
                {
                    continue;
                }

                item.Stack -= removal.Stack;
                if (item.Stack == 0)
                {
                    state.Items.Remove(item);
                }
                else
                {
                    item.Version++;
                }
            }

            foreach (var pair in currencyAfter)
            {
                if (pair.Value == 0)
                {
                    state.Currencies.Remove(pair.Key);
                }
                else
                {
                    state.Currencies[pair.Key] = pair.Value;
                }
            }

            state.AdvanceRevision();
            return InventoryOutcome.Success(state.ToContract());
        }
    }

    private static InventorySnapshot EmptySnapshot() =>
        new()
        {
            InventoryRevision = 0,
            Items = Array.Empty<InventoryItem>(),
            Currencies = Array.Empty<InventoryCurrency>()
        };
}
