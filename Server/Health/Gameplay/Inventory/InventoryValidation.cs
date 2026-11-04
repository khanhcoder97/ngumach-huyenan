using System.Text.RegularExpressions;
using Server.Health.Contracts;

namespace Server.Health.Gameplay.Inventory;

public static class InventoryValidation
{
    private const long MaxCurrencyDelta = 1_000_000_000_000L;

    // Underscores are allowed because the canonical catalogue names two slots
    // RING_L and RING_R, and their item ids carry them (EQ-MK-RING_L-T1-...). The
    // old pattern silently made those items ungrantable.
    private static readonly Regex TemplateIdPattern =
        new(@"^[A-Z0-9_]+(?:-[A-Z0-9_]+)*$", RegexOptions.CultureInvariant);

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
        out List<ItemMove> moves,
        out List<CurrencyDelta> deltas)
    {
        adds = new List<ItemGrant>();
        removes = new List<ItemRemoval>();
        moves = new List<ItemMove>();
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

        if (mutation.MoveItems is { } moveItems)
        {
            for (var index = 0; index < moveItems.Count; index++)
            {
                if (moveItems[index] is not { } move)
                {
                    return $"moveItems[{index}]";
                }

                if (move.InstanceId is null || !InstanceIdPattern.IsMatch(move.InstanceId))
                {
                    return $"moveItems[{index}].instanceId";
                }

                if (!InventoryLocations.IsValid(move.FromLocation))
                {
                    return $"moveItems[{index}].fromLocation";
                }

                if (!InventoryLocations.IsValid(move.ToLocation))
                {
                    return $"moveItems[{index}].toLocation";
                }

                if (string.Equals(move.FromLocation, move.ToLocation, StringComparison.Ordinal))
                {
                    return $"moveItems[{index}].toLocation";
                }

                if (string.Equals(move.ToLocation, InventoryLocations.Equipped, StringComparison.Ordinal))
                {
                    // A v2 write carries the twelve-slot token plus, when v1 has a
                    // word for it, the collapsed v1 token. Requiring the two to agree
                    // is what keeps the two vocabularies from ever disagreeing about
                    // who is wearing what; LEGS and GLOVES legitimately carry no v1
                    // token at all.
                    if (move.SlotV2 is { } precise)
                    {
                        if (!InventoryV2Slots.IsValid(precise))
                        {
                            return $"moveItems[{index}].slotV2";
                        }

                        var collapsed = InventoryV2Slots.CollapseToV1(precise, out var v1Token)
                            ? v1Token
                            : null;
                        if (!string.Equals(move.Slot, collapsed, StringComparison.Ordinal))
                        {
                            return $"moveItems[{index}].slot";
                        }
                    }
                    else if (move.Slot is null || !SlotPattern.IsMatch(move.Slot))
                    {
                        return $"moveItems[{index}].slot";
                    }
                }
                else if (move.Slot is not null || move.SlotV2 is not null)
                {
                    return $"moveItems[{index}].slot";
                }

                moves.Add(move);
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

        return adds.Count == 0 && removes.Count == 0 && moves.Count == 0 && deltas.Count == 0
            ? "mutation"
            : null;
    }
}
