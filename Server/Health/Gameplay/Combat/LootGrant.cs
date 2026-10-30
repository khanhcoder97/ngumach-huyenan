using Server.Health.Contracts;
using Server.Health.Gameplay.Inventory;
using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// Q-E: grant orchestration for a mob death, kept separate from the roll. The
// roll answers "what could drop"; this answers "may anything be granted, once,
// for this exact death". It is keyed by the death identity, so a replay, a
// late event or a second reader of the same death cannot grant twice, and a
// bundle whose source is not complete (`grantEnabled: false`) grants nothing
// and says why instead of shipping an invented amount.
public sealed record LootGrantItem(string TemplateId, int Stack);

public sealed record LootGrantOutcome(
    bool Granted,
    bool Replayed,
    string? BlockedReason,
    string? ErrorCode,
    string? DeathEventId,
    long LifeId,
    IReadOnlyList<string> GrantedTemplateIds);

public sealed class LootGrantLedger
{
    public const int Capacity = 512;

    private readonly Dictionary<string, LootGrantOutcome> _byDeath =
        new(StringComparer.Ordinal);
    private readonly Queue<string> _order = new();
    private readonly object _sync = new();

    public int Count
    {
        get
        {
            lock (_sync)
            {
                return _byDeath.Count;
            }
        }
    }

    public bool TryGet(string key, out LootGrantOutcome outcome)
    {
        lock (_sync)
        {
            return _byDeath.TryGetValue(key, out outcome!);
        }
    }

    public LootGrantOutcome Record(string key, LootGrantOutcome outcome)
    {
        lock (_sync)
        {
            if (!_byDeath.ContainsKey(key))
            {
                _order.Enqueue(key);
            }

            _byDeath[key] = outcome;
            while (_order.Count > Capacity && _order.TryDequeue(out var oldest))
            {
                _byDeath.Remove(oldest);
            }

            return outcome;
        }
    }

    public static string KeyFor(string deathEventId, long lifeId) =>
        $"{deathEventId}|{lifeId}";
}

public sealed class LootGrantService
{
    private readonly IInventoryService _inventory;
    private readonly LootGrantLedger _ledger;

    public LootGrantService(IInventoryService inventory, LootGrantLedger ledger)
    {
        _inventory = inventory;
        _ledger = ledger;
    }

    // Items are granted in one inventory mutation with the death identity as the
    // idempotency boundary; a failure leaves no ledger entry, so a retry can run
    // again instead of being reported as already granted.
    public LootGrantOutcome Grant(
        PlayerSession? actor,
        string deathEventId,
        long lifeId,
        bool grantEnabled,
        string? blockedReason,
        IReadOnlyList<LootGrantItem> items)
    {
        ArgumentNullException.ThrowIfNull(deathEventId);

        var key = LootGrantLedger.KeyFor(deathEventId, lifeId);
        if (_ledger.TryGet(key, out var prior))
        {
            return prior with { Replayed = true };
        }

        if (!grantEnabled)
        {
            return _ledger.Record(key, new LootGrantOutcome(
                Granted: false,
                Replayed: false,
                BlockedReason: blockedReason,
                ErrorCode: null,
                DeathEventId: deathEventId,
                LifeId: lifeId,
                GrantedTemplateIds: []));
        }

        if (actor is null || items.Count == 0)
        {
            return _ledger.Record(key, new LootGrantOutcome(
                Granted: false,
                Replayed: false,
                BlockedReason: null,
                ErrorCode: LootGrantErrorCodes.NothingToGrant,
                DeathEventId: deathEventId,
                LifeId: lifeId,
                GrantedTemplateIds: []));
        }

        var mutation = new InventoryMutation
        {
            AddItems = items
                .Select(item => new ItemGrant
                {
                    TemplateId = item.TemplateId,
                    Stack = item.Stack,
                    Location = InventoryLocations.Bag
                })
                .ToList()
        };
        var result = _inventory.Apply(actor, mutation);
        if (!result.IsSuccess)
        {
            // Not recorded: a failed grant must be retryable, not replayable.
            return new LootGrantOutcome(
                Granted: false,
                Replayed: false,
                BlockedReason: null,
                ErrorCode: result.ErrorCode,
                DeathEventId: deathEventId,
                LifeId: lifeId,
                GrantedTemplateIds: []);
        }

        return _ledger.Record(key, new LootGrantOutcome(
            Granted: true,
            Replayed: false,
            BlockedReason: null,
            ErrorCode: null,
            DeathEventId: deathEventId,
            LifeId: lifeId,
            GrantedTemplateIds: items.Select(item => item.TemplateId).ToArray()));
    }
}

public static class LootGrantErrorCodes
{
    public const string NothingToGrant = "loot_nothing_to_grant";
}
