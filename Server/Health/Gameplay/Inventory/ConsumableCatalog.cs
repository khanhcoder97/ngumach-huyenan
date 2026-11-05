using System.Text.RegularExpressions;
using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Inventory;

// Work order 29 Q5 lists "consumable" and "HP/MP clamp" among the economy pieces this
// slice owns, and `Item_Master_Catalog_vi.csv` is the only source that states what a
// consumable does. Seven of its fourteen `Tiêu hao` rows give a percentage of a maximum
// ("25% HP tối đa"); the other seven name effects whose subsystems the server does not
// model at all (cleanse, repair, teleport cast, timed food buffs, a one-use protection).
// This file classifies every row and applies only the sourced percentage restores. It
// deliberately has no route and no gate: what a client may *ask* for is a contract
// decision (QOD-24 packet), while loading and refusing is data work.
//
// Rounding is the one number no source gives for healing. Production_Rules §2 rule 6
// floors damage values and §4 floors XP, while the approved death-return rule ceils its
// half-max HP; there is no heal-specific statement. This machine floors, matching the
// value convention the ruleset actually uses for magnitudes, and the open question is
// recorded next to the check that pins it rather than hidden inside a constant.
public enum ConsumableEffectKind
{
    // `primary_stat` is "HP hồi"/"MP hồi" and the cell is a percentage of that maximum.
    RestorePercent,

    // The source states an effect this server cannot perform yet. Kept verbatim so a
    // refusal can name the row instead of inventing a generic "unsupported".
    Unsupported
}

public sealed record ConsumableEntry(
    string ItemId,
    string SlotLabel,
    int RequiredLevel,
    int StackLimit,
    ConsumableEffectKind Kind,
    string? Restores,
    int? Percent,
    // The revive row is a percentage restore too, but its slot says the target is a
    // downed character, which no sourced flow in this slice opens. Flagged, not dropped.
    bool ReviveRequired,
    string EffectStatLabel,
    string EffectValueCell);

public static class ConsumableCatalog
{
    public const string Hp = "HP";
    public const string Mp = "MP";

    // The slot labels the shipped source actually uses. A new label means a new rule,
    // which is the loader's business to complain about, not a consumer's to guess at.
    private static readonly HashSet<string> KnownSlotLabels = new(StringComparer.Ordinal)
    {
        "Potion HP", "Potion MP", "Giải trạng thái", "Hồi sinh", "Sửa chữa",
        "Dịch chuyển", "Thức ăn PvE", "Thức ăn nghề", "Bảo vệ phân giải"
    };

    private static readonly Dictionary<string, string> RestoreStatToTarget =
        new(StringComparer.Ordinal) { ["HP hồi"] = Hp, ["MP hồi"] = Mp };

    private static readonly Regex RestoreCell =
        new(
            @"^(?<percent>[1-9][0-9]{0,2})% (?<stat>HP|MP) tối đa$",
            RegexOptions.CultureInvariant);

    public static IReadOnlyList<ConsumableEntry> Load(ItemCatalog items)
    {
        var entries = new List<ConsumableEntry>();
        foreach (var item in items.ConsumableEntries)
        {
            if (item.SlotLabel is not { Length: > 0 } slotLabel)
            {
                throw new InvalidOperationException(
                    $"consumable {item.ItemId} has no slot label");
            }

            if (!KnownSlotLabels.Contains(slotLabel))
            {
                throw new InvalidOperationException(
                    $"consumable {item.ItemId} names an unknown slot label '{slotLabel}'");
            }

            if (item.RequiredLevel is < 1 or > 100)
            {
                throw new InvalidOperationException(
                    $"consumable {item.ItemId} requires level {item.RequiredLevel}, " +
                    "outside the 1..100 band the level curve ships");
            }

            if (item.StackLimit <= 0)
            {
                throw new InvalidOperationException(
                    $"consumable {item.ItemId} states stack_limit {item.StackLimit}");
            }

            var effectStat = item.PrimaryStat ?? string.Empty;
            var effectCell = item.PrimaryValue ?? string.Empty;

            if (!RestoreStatToTarget.TryGetValue(effectStat, out var restoreTarget))
            {
                entries.Add(new ConsumableEntry(
                    item.ItemId, slotLabel, item.RequiredLevel, item.StackLimit,
                    ConsumableEffectKind.Unsupported, null, null, false,
                    effectStat, effectCell));
                continue;
            }

            var match = RestoreCell.Match(effectCell);
            if (!match.Success)
            {
                throw new InvalidOperationException(
                    $"consumable {item.ItemId} says '{effectStat}' but its value cell " +
                    $"'{effectCell}' is not '<percent>% HP|MP tối đa'; refusing to " +
                    "invent a restore amount");
            }

            var percent = int.Parse(match.Groups["percent"].Value);
            if (percent > 100)
            {
                throw new InvalidOperationException(
                    $"consumable {item.ItemId} restores {percent}% of a maximum");
            }

            if (match.Groups["stat"].Value != restoreTarget)
            {
                throw new InvalidOperationException(
                    $"consumable {item.ItemId} pairs stat label '{effectStat}' with a " +
                    $"{match.Groups["stat"].Value} percentage");
            }

            entries.Add(new ConsumableEntry(
                item.ItemId, slotLabel, item.RequiredLevel, item.StackLimit,
                ConsumableEffectKind.RestorePercent, restoreTarget, percent,
                ReviveRequired: string.Equals(slotLabel, "Hồi sinh", StringComparison.Ordinal),
                effectStat, effectCell));
        }

        return entries;
    }
}

public static class ConsumableErrorCodes
{
    // Reused semantics from the equipment surface, with the same strings, so a future
    // route does not have to invent a second vocabulary for the same refusal.
    public const string ItemNotFound = InventoryErrorCodes.ItemNotFound;
    public const string WrongLocation = EquipmentErrorCodes.WrongLocation;
    public const string LevelRequired = EquipmentErrorCodes.LevelRequired;
    public const string RevisionConflict = EquipmentErrorCodes.RevisionConflict;
    public const string IdempotencyConflict = EquipmentErrorCodes.IdempotencyConflict;

    // New, and only meaningful in the domain until a packet approves them on the wire.
    public const string NotConsumable = "not_consumable";
    public const string EffectUnsupported = "effect_unsupported";
    public const string ReviveNotModelled = "revive_not_modelled";
    public const string NoEffect = "no_effect";
}

public sealed record ConsumableFailure(string Code, bool Retryable, IReadOnlyList<string> FieldErrors);

public sealed record ConsumableOutcome
{
    public required InventorySnapshot? Snapshot { get; init; }
    public ConsumableFailure? Failure { get; init; }

    // What the accepted consume moved, so a receipt can state the number rather than
    // have a client recompute it from a percentage it does not know.
    public int HpRestored { get; init; }
    public int MpRestored { get; init; }
    public int HpAfter { get; init; }
    public int MpAfter { get; init; }
    public string? EffectItemId { get; init; }

    public bool Accepted => Failure is null;

    public static ConsumableOutcome Success(
        InventorySnapshot snapshot, ConsumableEntry entry,
        int hpRestored, int mpRestored, PlayerSession actor) =>
        new()
        {
            Snapshot = snapshot,
            HpRestored = hpRestored,
            MpRestored = mpRestored,
            HpAfter = actor.Hp,
            MpAfter = actor.Mp,
            EffectItemId = entry.ItemId
        };

    public static ConsumableOutcome Rejected(
        string code, bool retryable, InventorySnapshot? snapshot,
        params string[] fieldErrors) =>
        new()
        {
            Snapshot = snapshot,
            Failure = new ConsumableFailure(code, retryable, fieldErrors)
        };
}

public interface IConsumableService
{
    ConsumableOutcome Consume(
        PlayerSession actor,
        string itemInstanceId,
        long expectedRevision,
        string idempotencyKey);
}

public sealed class ConsumableService : IConsumableService
{
    public const int LedgerCapacity = 256;

    private readonly IInventoryService _inventory;
    private readonly IReadOnlyDictionary<string, ConsumableEntry> _consumables;
    private readonly object _ledgerSync = new();
    private readonly Dictionary<(string, string), ConsumableLedgerEntry> _ledger = new();
    private readonly Queue<(string, string)> _ledgerOrder = new();

    public ConsumableService(
        IInventoryService inventory, IReadOnlyList<ConsumableEntry> catalog)
    {
        _inventory = inventory;
        _consumables = catalog.ToDictionary(entry => entry.ItemId, StringComparer.Ordinal);
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

    public ConsumableOutcome Consume(
        PlayerSession actor,
        string itemInstanceId,
        long expectedRevision,
        string idempotencyKey)
    {
        ArgumentNullException.ThrowIfNull(actor);
        ArgumentNullException.ThrowIfNull(idempotencyKey);

        var requestHash = Hash(itemInstanceId, expectedRevision);
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
                return ConsumableOutcome.Rejected(
                    ConsumableErrorCodes.RevisionConflict, retryable: true, snapshot,
                    "payload.expectedRevision");
            }

            var item = snapshot.Items.FirstOrDefault(candidate =>
                string.Equals(candidate.InstanceId, itemInstanceId, StringComparison.Ordinal));
            if (item is null)
            {
                return ConsumableOutcome.Rejected(
                    ConsumableErrorCodes.ItemNotFound, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            // An equipped consumable is a fixture mistake, not a use: the item has to be
            // reachable from the bag for a use to make sense.
            if (!string.Equals(item.Location, InventoryLocations.Bag, StringComparison.Ordinal))
            {
                return ConsumableOutcome.Rejected(
                    ConsumableErrorCodes.WrongLocation, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            if (!_consumables.TryGetValue(item.TemplateId, out var entry))
            {
                return ConsumableOutcome.Rejected(
                    ConsumableErrorCodes.NotConsumable, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            if (entry.Kind == ConsumableEffectKind.Unsupported)
            {
                return ConsumableOutcome.Rejected(
                    ConsumableErrorCodes.EffectUnsupported, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            // The row restores a percentage but frames itself as a revival; the slice has
            // no sourced revive flow, so it must not quietly become a free 15% heal.
            if (entry.ReviveRequired)
            {
                return ConsumableOutcome.Rejected(
                    ConsumableErrorCodes.ReviveNotModelled, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            if (actor.Level < entry.RequiredLevel)
            {
                return ConsumableOutcome.Rejected(
                    ConsumableErrorCodes.LevelRequired, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            // Production_Rules §2 rule 6 clamps HP to 0..maxHP; a use that could not move
            // either pool by at least one point is refused rather than spending a stack,
            // because no source says a player loses an item for drinking at full HP.
            var hpRestore = entry.Restores == ConsumableCatalog.Hp
                ? RestoreAmount(actor.MaxHp, entry.Percent!.Value)
                : 0;
            var mpRestore = entry.Restores == ConsumableCatalog.Mp
                ? RestoreAmount(actor.MaxMp, entry.Percent!.Value)
                : 0;
            var hpGain = Math.Max(0, Math.Min(actor.MaxHp, actor.Hp + hpRestore) - actor.Hp);
            var mpGain = Math.Max(0, Math.Min(actor.MaxMp, actor.Mp + mpRestore) - actor.Mp);
            if (hpGain == 0 && mpGain == 0)
            {
                return ConsumableOutcome.Rejected(
                    ConsumableErrorCodes.NoEffect, retryable: false, snapshot,
                    "payload.itemInstanceId");
            }

            var after = _inventory.Apply(actor, new InventoryMutation
            {
                ExpectedRevision = expectedRevision,
                RemoveItems = [new ItemRemoval
                {
                    InstanceId = item.InstanceId,
                    Stack = 1
                }]
            });
            if (!after.IsSuccess || after.Snapshot is null)
            {
                return ConsumableOutcome.Rejected(
                    after.ErrorCode ?? InventoryErrorCodes.ItemNotFound,
                    retryable: false,
                    _inventory.GetSnapshot(actor.CharacterId),
                    "payload.itemInstanceId");
            }

            // The ruleset's clamp is `0..maxHP`, and a restore never runs the other way:
            // both pools move up, and only up.
            actor.Hp = Math.Min(actor.MaxHp, actor.Hp + hpGain);
            actor.Mp = Math.Min(actor.MaxMp, actor.Mp + mpGain);

            var outcome = ConsumableOutcome.Success(
                after.Snapshot, entry, hpGain, mpGain, actor);
            Record(key, requestHash, outcome);
            return outcome;
        }
    }

    // floor, per the value convention in Production_Rules §2/§4. See the file header for
    // why this is the choice and what is still open.
    private static int RestoreAmount(int maximum, int percent) =>
        (int)Math.Floor((double)maximum * percent / 100);

    private static string Hash(string itemInstanceId, long expectedRevision) =>
        $"{itemInstanceId}|{expectedRevision}";

    private bool TryReplay(
        (string, string) key, string requestHash, out ConsumableOutcome outcome)
    {
        lock (_ledgerSync)
        {
            if (_ledger.TryGetValue(key, out var stored))
            {
                if (!string.Equals(stored.Hash, requestHash, StringComparison.Ordinal))
                {
                    outcome = ConsumableOutcome.Rejected(
                        ConsumableErrorCodes.IdempotencyConflict, retryable: false,
                        stored.Outcome.Snapshot, "idempotencyKey");
                    return true;
                }

                outcome = stored.Outcome;
                return true;
            }
        }

        outcome = null!;
        return false;
    }

    private void Record((string, string) key, string requestHash, ConsumableOutcome outcome)
    {
        lock (_ledgerSync)
        {
            if (!_ledger.ContainsKey(key))
            {
                _ledger[key] = new ConsumableLedgerEntry(requestHash, outcome);
                _ledgerOrder.Enqueue(key);
            }

            while (_ledgerOrder.Count > LedgerCapacity)
            {
                _ledger.Remove(_ledgerOrder.Dequeue());
            }
        }
    }

    private sealed record ConsumableLedgerEntry(string Hash, ConsumableOutcome Outcome);
}
