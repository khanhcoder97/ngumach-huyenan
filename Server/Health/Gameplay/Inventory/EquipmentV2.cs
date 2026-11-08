using System.Security.Cryptography;
using System.Text;
using Server.Health.Contracts;
using Server.Health.Gameplay.Alpha;
using Server.Health.World;

namespace Server.Health.Gameplay.Inventory;

// QOD-21 Q3: the v2 equip/unequip handler for the twelve-slot read model
// (DESIGN-BM-Q3-20261104 `inventory`, V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT).
//
// It runs against the same authoritative store and the same aggregate revision as
// v1, so a client cannot be looking at one inventory in one vocabulary and a second
// in another; what differs is the slot vocabulary it writes. The stored slot is the
// v2 token the catalog label resolves to, which is what makes two accessories (a
// necklace and a left ring) two slots instead of one shared `ACCESSORY`. v1's own
// routes, its five tokens and its rules are not modified at all: with the alpha
// profile off nothing here is even reachable.
//
// Rules that are the same as v1 on purpose: bag-only source, stack of one, class
// gate, level gate, expected-revision conflict, idempotent replay with a
// same-key-different-payload conflict, and one mutation per request under the
// actor lock. Rules that differ, and why:
// - the slot is never taken from the request; `ItemCatalogEntry.SlotLabel` decides
//   it, so a client cannot place an item in a slot the source does not name;
// - occupancy is counted over resolved v2 slots, so an accessory equipped through
//   v1 occupies its own v2 slot (NECK, RING_L, ...) and a v2 equip into a different
//   accessory slot is not blocked by it. The reverse asymmetry is real and is left
//   alone deliberately: v1 still enforces "one item in ACCESSORY" over its own
//   token, and tightening that would change the frozen v1 contract.
public sealed record EquipmentV2Failure(
    string Code,
    bool Retryable,
    IReadOnlyList<string> FieldErrors);

public sealed record EquipmentV2Outcome(
    InventorySnapshotV2? Snapshot,
    EquipmentV2Failure? Failure)
{
    public bool Accepted => Failure is null;

    public static EquipmentV2Outcome Success(InventorySnapshotV2 snapshot) =>
        new(snapshot, null);

    public static EquipmentV2Outcome Rejected(
        string code,
        bool retryable,
        InventorySnapshotV2? snapshot,
        params string[] fieldErrors) =>
        new(snapshot, new EquipmentV2Failure(code, retryable, fieldErrors));
}

public interface IEquipmentV2Service
{
    EquipmentV2Outcome Read(PlayerSession actor);

    EquipmentV2Outcome Equip(
        PlayerSession actor,
        string itemInstanceId,
        long expectedRevision,
        string idempotencyKey);

    EquipmentV2Outcome Unequip(
        PlayerSession actor,
        string slotId,
        long expectedRevision,
        string idempotencyKey);
}

public sealed class EquipmentV2Service : IEquipmentV2Service
{
    public const int LedgerCapacity = 256;

    private readonly IInventoryService _inventory;
    private readonly IInventoryStateStore _states;
    private readonly ItemCatalog _catalog;
    private readonly AlphaInventoryRules _rules;
    private readonly object _ledgerSync = new();
    private readonly Dictionary<(string CharacterId, string Key), EquipmentV2LedgerEntry> _ledger =
        new();
    private readonly Queue<(string CharacterId, string Key)> _ledgerOrder = new();

    public EquipmentV2Service(
        IInventoryService inventory,
        IInventoryStateStore states,
        ItemCatalog catalog,
        AlphaDesign design)
    {
        ArgumentNullException.ThrowIfNull(inventory);
        ArgumentNullException.ThrowIfNull(states);
        ArgumentNullException.ThrowIfNull(catalog);
        ArgumentNullException.ThrowIfNull(design);
        _inventory = inventory;
        _states = states;
        _catalog = catalog;
        _rules = design.Inventory;
    }

    public int LedgerCount
    {
        get
        {
            lock (_ledgerSync)
            {
                return _ledger.Count;
            }
        }
    }

    public EquipmentV2Outcome Read(PlayerSession actor)
    {
        ArgumentNullException.ThrowIfNull(actor);
        lock (actor.SyncRoot)
        {
            return EquipmentV2Outcome.Success(Project(actor));
        }
    }

    public EquipmentV2Outcome Equip(
        PlayerSession actor,
        string itemInstanceId,
        long expectedRevision,
        string idempotencyKey)
    {
        ArgumentNullException.ThrowIfNull(actor);

        var requestHash = Hash("equip", itemInstanceId, expectedRevision);
        var key = (actor.CharacterId, idempotencyKey);
        if (TryReplay(key, requestHash, out var replay))
        {
            return replay;
        }

        lock (actor.SyncRoot)
        {
            if (TryReplay(key, requestHash, out replay))
            {
                return replay;
            }

            var current = Project(actor);
            if (current.InventoryRevision != expectedRevision)
            {
                return EquipmentV2Outcome.Rejected(
                    EquipmentErrorCodes.RevisionConflict, retryable: true, current,
                    "payload.expectedRevision");
            }

            var item = current.Bag.FirstOrDefault(candidate =>
                string.Equals(candidate.InstanceId, itemInstanceId, StringComparison.Ordinal));
            if (item is null)
            {
                // The v2 bag is everything that is not equipped, so an unknown id
                // and an already-worn id are different answers.
                var wornElsewhere = current.Slots.Any(candidate =>
                    candidate.Item is not null && string.Equals(
                        candidate.Item.InstanceId, itemInstanceId, StringComparison.Ordinal));
                return EquipmentV2Outcome.Rejected(
                    wornElsewhere
                        ? EquipmentErrorCodes.WrongLocation
                        : EquipmentErrorCodes.ItemNotFound,
                    retryable: false, current, "payload.itemInstanceId");
            }

            if (item.Stack != 1)
            {
                return EquipmentV2Outcome.Rejected(
                    EquipmentErrorCodes.NotEquippable, retryable: false, current,
                    "payload.itemInstanceId");
            }

            if (!_catalog.TryGet(item.TemplateId, out var entry) ||
                !ItemCatalog.IsEquipmentCategory(entry.Category) ||
                !InventoryV2Slots.TryResolveEntry(entry, out var slot))
            {
                // Not equipment, or an equipment label the twelve do not name: there
                // is no slot to write, so nothing moves.
                return EquipmentV2Outcome.Rejected(
                    EquipmentErrorCodes.NotEquippable, retryable: false, current,
                    "payload.itemInstanceId");
            }

            if (!string.Equals(entry.ClassId, actor.ClassId, StringComparison.Ordinal))
            {
                return EquipmentV2Outcome.Rejected(
                    EquipmentErrorCodes.ClassRestricted, retryable: false, current,
                    "payload.itemInstanceId");
            }

            if (actor.Level < entry.RequiredLevel)
            {
                return EquipmentV2Outcome.Rejected(
                    EquipmentErrorCodes.LevelRequired, retryable: false, current,
                    "payload.itemInstanceId");
            }

            var occupant = current.Slots
                .First(candidate => string.Equals(candidate.SlotId, slot, StringComparison.Ordinal))
                .Item;
            if (occupant is not null &&
                !string.Equals(occupant.InstanceId, item.InstanceId, StringComparison.Ordinal))
            {
                return EquipmentV2Outcome.Rejected(
                    EquipmentErrorCodes.SlotOccupied, retryable: false, current,
                    "payload.itemInstanceId");
            }

            var applied = _inventory.Apply(actor, new InventoryMutation
            {
                ExpectedRevision = expectedRevision,
                MoveItems =
                [
                    new ItemMove
                    {
                        InstanceId = item.InstanceId,
                        FromLocation = InventoryLocations.Bag,
                        ToLocation = InventoryLocations.Equipped,
                        // v1 keeps seeing its own five tokens (or no token at all for
                        // LEGS/GLOVES), while SlotV2 carries the precise slot.
                        Slot = InventoryV2Slots.CollapseToV1(slot, out var v1Slot)
                            ? v1Slot
                            : null,
                        SlotV2 = slot
                    }
                ]
            });
            if (!applied.IsSuccess)
            {
                return MapInventoryFailure(applied, current);
            }

            var committed = Project(actor);
            Record(key, requestHash, committed);
            return EquipmentV2Outcome.Success(committed);
        }
    }

    public EquipmentV2Outcome Unequip(
        PlayerSession actor,
        string slotId,
        long expectedRevision,
        string idempotencyKey)
    {
        ArgumentNullException.ThrowIfNull(actor);

        if (!InventoryV2Slots.IsValid(slotId))
        {
            return EquipmentV2Outcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, null,
                "payload.slotId");
        }

        var requestHash = Hash("unequip", slotId, expectedRevision);
        var key = (actor.CharacterId, idempotencyKey);
        if (TryReplay(key, requestHash, out var replay))
        {
            return replay;
        }

        lock (actor.SyncRoot)
        {
            if (TryReplay(key, requestHash, out replay))
            {
                return replay;
            }

            var current = Project(actor);
            if (current.InventoryRevision != expectedRevision)
            {
                return EquipmentV2Outcome.Rejected(
                    EquipmentErrorCodes.RevisionConflict, retryable: true, current,
                    "payload.expectedRevision");
            }

            var entry = current.Slots.FirstOrDefault(candidate =>
                string.Equals(candidate.SlotId, slotId, StringComparison.Ordinal));
            if (entry?.Item is not { } worn)
            {
                return EquipmentV2Outcome.Rejected(
                    EquipmentErrorCodes.WrongLocation, retryable: false, current,
                    "payload.slotId");
            }

            var applied = _inventory.Apply(actor, new InventoryMutation
            {
                ExpectedRevision = expectedRevision,
                MoveItems =
                [
                    new ItemMove
                    {
                        InstanceId = worn.InstanceId,
                        FromLocation = InventoryLocations.Equipped,
                        ToLocation = InventoryLocations.Bag
                    }
                ]
            });
            if (!applied.IsSuccess)
            {
                return MapInventoryFailure(applied, current);
            }

            var committed = Project(actor);
            Record(key, requestHash, committed);
            return EquipmentV2Outcome.Success(committed);
        }
    }

    // The twelve-slot view of one player's inventory. An equipped item's slot is
    // whatever its canonical label names; when nothing names it (an item whose
    // catalogue row is gone, or a slot string that is neither vocabulary) the item
    // is listed in unsupported rather than lost.
    // Called with the actor lock held, so the v1 snapshot and the store's v2 slot
    // column are read from one moment in time and cannot disagree.
    private InventorySnapshotV2 Project(PlayerSession actor)
    {
        var snapshot = _inventory.GetSnapshot(actor.CharacterId);
        var wornV2 = new Dictionary<string, string?>(StringComparer.Ordinal);
        if (_states.Find(actor.CharacterId) is { } state)
        {
            foreach (var entry in state.Items)
            {
                wornV2[entry.InstanceId] = entry.SlotV2;
            }
        }

        var bySlot = new Dictionary<string, InventoryItemV2>(StringComparer.Ordinal);
        var unsupported = new List<InventoryV2UnsupportedItem>();
        foreach (var item in snapshot.Items)
        {
            if (!string.Equals(item.Location, InventoryLocations.Equipped,
                    StringComparison.Ordinal))
            {
                continue;
            }

            var known = _catalog.TryGet(item.TemplateId, out var entry) ? entry : null;
            wornV2.TryGetValue(item.InstanceId, out var precise);
            if (!InventoryV2Slots.TryResolveWorn(
                    known, precise ?? item.Slot, item.Slot, out var slot))
            {
                unsupported.Add(new InventoryV2UnsupportedItem
                {
                    InstanceId = item.InstanceId,
                    TemplateId = item.TemplateId,
                    SourceSlot = item.Slot,
                    Reason = InventoryV2UnsupportedReasons.UnmappedSlot
                });
                continue;
            }

            // Two items claiming one slot is a store fault, not something to hide:
            // the first keeps the slot and the second is reported.
            if (bySlot.ContainsKey(slot))
            {
                unsupported.Add(new InventoryV2UnsupportedItem
                {
                    InstanceId = item.InstanceId,
                    TemplateId = item.TemplateId,
                    SourceSlot = item.Slot,
                    Reason = InventoryV2UnsupportedReasons.UnmappedSlot
                });
                continue;
            }

            bySlot[slot] = ToItem(item, slot);
        }

        return new InventorySnapshotV2
        {
            SlotSpec = _rules.WireMigration,
            InventoryRevision = snapshot.InventoryRevision,
            BagSlots = _rules.BagSlots,
            Slots = InventoryV2Slots.All.Select(slot => new InventoryV2SlotEntry
            {
                SlotId = slot,
                Item = bySlot.TryGetValue(slot, out var worn) ? worn : null
            }).ToList(),
            Bag = snapshot.Items
                .Where(item => !string.Equals(
                    item.Location, InventoryLocations.Equipped, StringComparison.Ordinal))
                .Select(item => ToItem(item, null))
                .ToList(),
            Unsupported = unsupported,
            Currencies = snapshot.Currencies
        };
    }

    private static InventoryItemV2 ToItem(InventoryItem item, string? slot) => new()
    {
        InstanceId = item.InstanceId,
        TemplateId = item.TemplateId,
        Stack = item.Stack,
        Location = item.Location,
        SlotId = slot,
        Durability = item.Durability,
        Version = item.Version
    };

    private static EquipmentV2Outcome MapInventoryFailure(
        InventoryOutcome applied, InventorySnapshotV2 current)
    {
        var field = applied.Field ?? "payload";
        var rejection = applied.ErrorCode switch
        {
            InventoryErrorCodes.RevisionConflict => (EquipmentErrorCodes.RevisionConflict, true),
            InventoryErrorCodes.SlotOccupied => (EquipmentErrorCodes.SlotOccupied, false),
            InventoryErrorCodes.ItemNotFound => (EquipmentErrorCodes.ItemNotFound, false),
            InventoryErrorCodes.WrongLocation => (EquipmentErrorCodes.WrongLocation, false),
            _ => (P1ErrorCodes.InvalidPayload, false)
        };

        return EquipmentV2Outcome.Rejected(
            rejection.Item1, rejection.Item2, current,
            field.Replace("moveItems[0].", "payload."));
    }

    private bool TryReplay(
        (string CharacterId, string Key) key,
        string requestHash,
        out EquipmentV2Outcome outcome)
    {
        lock (_ledgerSync)
        {
            if (_ledger.TryGetValue(key, out var entry))
            {
                outcome = string.Equals(entry.RequestHash, requestHash, StringComparison.Ordinal)
                    ? EquipmentV2Outcome.Success(entry.Snapshot)
                    : EquipmentV2Outcome.Rejected(
                        EquipmentErrorCodes.IdempotencyConflict, retryable: false, null,
                        "idempotencyKey");
                return true;
            }
        }

        outcome = null!;
        return false;
    }

    private void Record(
        (string CharacterId, string Key) key, string requestHash, InventorySnapshotV2 snapshot)
    {
        lock (_ledgerSync)
        {
            if (_ledger.ContainsKey(key))
            {
                return;
            }

            _ledger[key] = new EquipmentV2LedgerEntry(requestHash, snapshot);
            _ledgerOrder.Enqueue(key);
            while (_ledgerOrder.Count > LedgerCapacity && _ledgerOrder.TryDequeue(out var oldest))
            {
                _ledger.Remove(oldest);
            }
        }
    }

    private static string Hash(string operation, string argument, long expectedRevision) =>
        Convert.ToHexString(
            SHA256.HashData(
                Encoding.UTF8.GetBytes($"{operation}|{argument}|{expectedRevision}")));

    private sealed record EquipmentV2LedgerEntry(string RequestHash, InventorySnapshotV2 Snapshot);
}
