using System.Text.RegularExpressions;

namespace Server.Health.Gameplay.Inventory;

public static class InventoryValidation
{
    private const long MaxCurrencyDelta = 1_000_000_000_000L;

    private static readonly Regex TemplateIdPattern =
        new(@"^[A-Z0-9]+(?:-[A-Z0-9]+)*$", RegexOptions.CultureInvariant);

    private static readonly Regex InstanceIdPattern =
        new(@"^ITM_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex SlotPattern =
        new(@"^[A-Z_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex CurrencyIdPattern =
        new(@"^[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    public static string? Validate(
        InventoryMutation? mutation,
        out List<ItemGrant> adds,
        out List<ItemRemoval> removes,
        out List<CurrencyDelta> deltas)
    {
        adds = new List<ItemGrant>();
        removes = new List<ItemRemoval>();
        deltas = new List<CurrencyDelta>();

        if (mutation is null)
        {
            return "mutation";
        }

        if (mutation.ExpectedRevision is { } expected && expected < 0)
        {
            return "expectedRevision";
        }

        if (mutation.AddItems is { } addItems)
        {
            for (var index = 0; index < addItems.Count; index++)
            {
                if (addItems[index] is not { } add)
                {
                    return $"addItems[{index}]";
                }

                if (add.TemplateId is null || !TemplateIdPattern.IsMatch(add.TemplateId))
                {
                    return $"addItems[{index}].templateId";
                }

                if (add.Stack < 1)
                {
                    return $"addItems[{index}].stack";
                }

                if (!InventoryLocations.IsValid(add.Location))
                {
                    return $"addItems[{index}].location";
                }

                if (add.Slot is not null && !SlotPattern.IsMatch(add.Slot))
                {
                    return $"addItems[{index}].slot";
                }

                if (add.Durability < 0)
                {
                    return $"addItems[{index}].durability";
                }

                adds.Add(add);
            }
        }

        if (mutation.RemoveItems is { } removeItems)
        {
            for (var index = 0; index < removeItems.Count; index++)
            {
                if (removeItems[index] is not { } remove)
                {
                    return $"removeItems[{index}]";
                }

                if (remove.InstanceId is null || !InstanceIdPattern.IsMatch(remove.InstanceId))
                {
                    return $"removeItems[{index}].instanceId";
                }

                if (remove.Stack < 1)
                {
                    return $"removeItems[{index}].stack";
                }

                removes.Add(remove);
            }
        }

        if (mutation.CurrencyDeltas is { } currencyDeltas)
        {
            for (var index = 0; index < currencyDeltas.Count; index++)
            {
                if (currencyDeltas[index] is not { } delta)
                {
                    return $"currencyDeltas[{index}]";
                }

                if (delta.CurrencyId is null || !CurrencyIdPattern.IsMatch(delta.CurrencyId))
                {
                    return $"currencyDeltas[{index}].currencyId";
                }

                if (delta.Amount is < -MaxCurrencyDelta or > MaxCurrencyDelta)
                {
                    return $"currencyDeltas[{index}].amount";
                }

                deltas.Add(delta);
            }
        }

        return adds.Count == 0 && removes.Count == 0 && deltas.Count == 0
            ? "mutation"
            : null;
    }
}
