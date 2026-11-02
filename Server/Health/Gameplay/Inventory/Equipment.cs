using System.Security.Cryptography;
using System.Text;
using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Inventory;

// Q-E: metadata-only equipping for the P1 slice. There is deliberately no stat
// application here: Production_Rules §2 / DEC-023 do not yet define how
// weapon_power, armor and primary stats enter DamageFormula, so equipping moves
// an item between BAG and EQUIPPED and nothing else. The catalog gates (slot,
// class, level) are the only rules with canonical sources.
public static class EquipmentSlots
{
    public const string Hat = "HAT";
    public const string Chest = "CHEST";
    public const string Boots = "BOOTS";
    public const string Weapon = "WEAPON";
    public const string Accessory = "ACCESSORY";

    public static bool IsValid(string? value) =>
        value is Hat or Chest or Boots or Weapon or Accessory;
}

public sealed record EquipmentOptions
{
    public const string SectionName = "P1:Equipment";

    // OFF by default: the routes are only a wire surface when an operator opts
    // in, matching every other P1 mutation gate.
    public bool Enabled { get; set; }
}

public static class EquipmentErrorCodes
{
    public const string ItemNotFound = "item_not_found";
    public const string WrongLocation = "wrong_location";
    public const string SlotOccupied = "slot_occupied";
    public const string ClassRestricted = "class_restricted";
    public const string LevelRequired = "level_required";
    public const string NotEquippable = "not_equippable";
    public const string RevisionConflict = "revision_conflict";
    public const string IdempotencyConflict = "idempotency_conflict";
}

public sealed record EquipmentFailure(
    string Code,
    bool Retryable,
    IReadOnlyList<string> FieldErrors);

public sealed record EquipmentOutcome(
    InventorySnapshot? Snapshot,
    EquipmentFailure? Failure)
{
    public bool Accepted => Failure is null;

    public static EquipmentOutcome Success(InventorySnapshot snapshot) =>
        new(snapshot, null);

    public static EquipmentOutcome Rejected(
        string code,
        bool retryable,
        InventorySnapshot? snapshot,
        params string[] fieldErrors) =>
        new(snapshot, new EquipmentFailure(code, retryable, fieldErrors));
}

public interface IEquipmentService
{
    EquipmentOutcome Equip(
        PlayerSession actor,
        string itemInstanceId,
        long expectedRevision,
        string idempotencyKey);

    EquipmentOutcome Unequip(
        PlayerSession actor,
        string slot,
        long expectedRevision,
        string idempotencyKey);
}

public sealed class EquipmentService : IEquipmentService
{
    // Bounded like the death-return ledger; a long-lived process cannot grow it
    // one entry per idle client key.
    public const int LedgerCapacity = 256;

    private readonly IInventoryService _inventory;
    private readonly ItemCatalog _catalog;
    private readonly object _ledgerSync = new();
    private readonly Dictionary<(string CharacterId, string Key), EquipmentLedgerEntry> _ledger =
        new();
    private readonly Queue<(string CharacterId, string Key)> _ledgerOrder = new();

    public EquipmentService(IInventoryService inventory, ItemCatalog catalog)
    {
        _inventory = inventory;
        _catalog = catalog;
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

    public EquipmentOutcome Equip(
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
            // A parallel same-key request must replay the winner's answer
            // instead of moving an item a second time.
            if (TryReplay(key, requestHash, out replay))
            {
                return replay;
            }

            var snapshot = _inventory.GetSnapshot(actor.CharacterId);
            if (snapshot.InventoryRevision != expectedRevision)
            {
                return EquipmentOutcome.Rejected(
                    EquipmentErrorCodes.RevisionConflict, retryable: true, snapshot,
                    "payload.expectedRevision");
            }

            var item = FindItem(snapshot, itemInstanceId);
            if (item is null)
            {
                return EquipmentOutcome.Rejected(
                    EquipmentErrorCodes.ItemNotFound, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            if (!string.Equals(item.Location, InventoryLocations.Bag, StringComparison.Ordinal))
            {
                return EquipmentOutcome.Rejected(
                    EquipmentErrorCodes.WrongLocation, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            if (item.Stack != 1)
            {
                return EquipmentOutcome.Rejected(
                    EquipmentErrorCodes.NotEquippable, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            if (!_catalog.TryGet(item.TemplateId, out var entry) ||
                !ItemCatalog.IsEquipmentCategory(entry.Category) ||
                entry.SlotToken is null)
            {
                return EquipmentOutcome.Rejected(
                    EquipmentErrorCodes.NotEquippable, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            if (!string.Equals(entry.ClassId, actor.ClassId, StringComparison.Ordinal))
            {
                return EquipmentOutcome.Rejected(
                    EquipmentErrorCodes.ClassRestricted, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            if (actor.Level < entry.RequiredLevel)
            {
                return EquipmentOutcome.Rejected(
                    EquipmentErrorCodes.LevelRequired, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            var occupant = FindEquipped(snapshot, entry.SlotToken);
            if (occupant is not null &&
                !string.Equals(occupant.InstanceId, item.InstanceId, StringComparison.Ordinal))
            {
                return EquipmentOutcome.Rejected(
                    EquipmentErrorCodes.SlotOccupied, retryable: false, snapshot,
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
                        Slot = entry.SlotToken
                    }
                ]
            });
            if (!applied.IsSuccess)
            {
                return MapInventoryFailure(applied, snapshot);
            }

            Record(key, requestHash, applied.Snapshot!);
            return EquipmentOutcome.Success(applied.Snapshot!);
        }
    }

    public EquipmentOutcome Unequip(
        PlayerSession actor,
        string slot,
        long expectedRevision,
        string idempotencyKey)
    {
        ArgumentNullException.ThrowIfNull(actor);

        var requestHash = Hash("unequip", slot, expectedRevision);
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

            var snapshot = _inventory.GetSnapshot(actor.CharacterId);
            if (snapshot.InventoryRevision != expectedRevision)
            {
                return EquipmentOutcome.Rejected(
                    EquipmentErrorCodes.RevisionConflict, retryable: true, snapshot,
                    "payload.expectedRevision");
            }

            var item = FindEquipped(snapshot, slot);
            if (item is null)
            {
                return EquipmentOutcome.Rejected(
                    EquipmentErrorCodes.ItemNotFound, retryable: false, snapshot,
                    "payload.slot");
            }

            var applied = _inventory.Apply(actor, new InventoryMutation
            {
                ExpectedRevision = expectedRevision,
                MoveItems =
                [
                    new ItemMove
                    {
                        InstanceId = item.InstanceId,
                        FromLocation = InventoryLocations.Equipped,
                        ToLocation = InventoryLocations.Bag
                    }
                ]
            });
            if (!applied.IsSuccess)
            {
                return MapInventoryFailure(applied, snapshot);
            }

            Record(key, requestHash, applied.Snapshot!);
            return EquipmentOutcome.Success(applied.Snapshot!);
        }
    }

    private static InventoryItem? FindItem(InventorySnapshot snapshot, string instanceId) =>
        snapshot.Items.FirstOrDefault(item =>
            string.Equals(item.InstanceId, instanceId, StringComparison.Ordinal));

    private static InventoryItem? FindEquipped(InventorySnapshot snapshot, string slot) =>
        snapshot.Items.FirstOrDefault(item =>
            string.Equals(item.Location, InventoryLocations.Equipped, StringComparison.Ordinal) &&
            string.Equals(item.Slot, slot, StringComparison.Ordinal));

    private static EquipmentOutcome MapInventoryFailure(
        InventoryOutcome applied, InventorySnapshot snapshot)
    {
        var field = applied.Field ?? "payload";
        var rejection = applied.ErrorCode switch
        {
            InventoryErrorCodes.RevisionConflict => (
                EquipmentErrorCodes.RevisionConflict, true),
            InventoryErrorCodes.SlotOccupied => (
                EquipmentErrorCodes.SlotOccupied, false),
            InventoryErrorCodes.ItemNotFound => (
                EquipmentErrorCodes.ItemNotFound, false),
            InventoryErrorCodes.WrongLocation => (
                EquipmentErrorCodes.WrongLocation, false),
            _ => (P1ErrorCodes.InvalidPayload, false)
        };

        return EquipmentOutcome.Rejected(
            rejection.Item1, rejection.Item2, applied.Snapshot ?? snapshot,
            field.Replace("moveItems[0].", "payload."));
    }

    private bool TryReplay(
        (string CharacterId, string Key) key,
        string requestHash,
        out EquipmentOutcome outcome)
    {
        lock (_ledgerSync)
        {
            if (_ledger.TryGetValue(key, out var entry))
            {
                outcome = string.Equals(entry.RequestHash, requestHash, StringComparison.Ordinal)
                    ? EquipmentOutcome.Success(entry.Snapshot)
                    : EquipmentOutcome.Rejected(
                        EquipmentErrorCodes.IdempotencyConflict, retryable: false, null,
                        "idempotencyKey");
                return true;
            }
        }

        outcome = null!;
        return false;
    }

    private void Record(
        (string CharacterId, string Key) key, string requestHash, InventorySnapshot snapshot)
    {
        lock (_ledgerSync)
        {
            if (_ledger.ContainsKey(key))
            {
                return;
            }

            _ledger[key] = new EquipmentLedgerEntry(requestHash, snapshot);
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

    private sealed record EquipmentLedgerEntry(string RequestHash, InventorySnapshot Snapshot);
}
