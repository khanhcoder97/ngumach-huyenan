using System.Globalization;
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
    IReadOnlyList<string> GrantedTemplateIds,
    long Coin = 0);

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

public static class LootGrantPolicies
{
    // The shipped bundle is grant-off because no document states the mob coin
    // band; the reason is recorded on every death so the gap is visible.
    public const string SourceShortReason = "COIN_BAND_MISSING";

    // The alpha profile does state the band, so a death with the payout switch
    // still off is not "no source" — it is a roll that is deliberately not paid.
    public const string DryRunReason = "DRY_RUN_NON_PAYABLE";
}

// Whether a resolved death may pay anything, decided by the profile that owns the
// reward data (see `AlphaLootGrantPolicy`). CoinMin/CoinMax are the sourced band
// for the mob level the caller resolved.
public readonly record struct LootGrantDecision(
    bool GrantEnabled,
    string? BlockedReason,
    int CoinMin,
    int CoinMax);

public interface ILootGrantPolicy
{
    // The level is asked for lazily: reading it means touching the mob-stat bundle,
    // which a disabled combat gate does not load. A policy that is not going to pay
    // must answer without forcing that read.
    LootGrantDecision Decide(Func<int> mobLevel);

    // A policy that pays nothing and says why; also what every profile without an
    // alpha design gets, so the shipped behaviour does not move.
    public static ILootGrantPolicy Never(LootGrantDecision blocked) => new NeverGrantPolicy(blocked);

    private sealed class NeverGrantPolicy(LootGrantDecision blocked) : ILootGrantPolicy
    {
        public LootGrantDecision Decide(Func<int> mobLevel) => blocked;
    }
}

public sealed class LootGrantService
{
    private readonly IInventoryService _inventory;
    private readonly LootGrantLedger _ledger;
    private readonly ILootGrantPolicy _policy;
    private readonly CombatDamageFeature? _combat;
    private readonly LootReceiptLedger? _receipts;
    private LootRoller? _roller;

    public LootGrantService(
        IInventoryService inventory,
        LootGrantLedger ledger,
        ILootGrantPolicy? policy = null,
        CombatDamageFeature? combat = null,
        LootReceiptLedger? receipts = null)
    {
        _inventory = inventory;
        _ledger = ledger;
        _policy = policy ?? ILootGrantPolicy.Never(
            new LootGrantDecision(false, LootGrantPolicies.SourceShortReason, 0, 0));
        _combat = combat;
        _receipts = receipts;
    }

    // The kill-side entry point: decide, roll once per death, then pay (or record
    // the dry run) under the sourced roll-once key. A death recorded while the
    // switch was off keeps its recorded answer, so turning the flag on later cannot
    // back-fill payouts for deaths that already happened (`noBackfill`).
    public LootGrantOutcome OnMobDeath(
        PlayerSession? actor,
        WorldEntityInstance target,
        string mobTemplateId,
        Func<int> mobLevel,
        string deathEventId,
        long lifeId)
    {
        ArgumentNullException.ThrowIfNull(target);

        var decision = _policy.Decide(mobLevel);
        if (!decision.GrantEnabled || _combat is null)
        {
            return Grant(
                actor,
                deathEventId,
                lifeId,
                grantEnabled: false,
                blockedReason: decision.BlockedReason,
                items: [],
                coin: 0);
        }

        // Built here, not at composition time: the recipe bundle is only readable
        // while the damage gate is on, and paying a kill is the only reason to read
        // it.
        _roller ??= new LootRoller(_combat.LootRecipes, new LootRngRollSource());
        // The sourced roll-once key: [profileVersion, characterId, deathEventId,
        // lifeId, groupId]. A solo mob has no group, so its own record identifies
        // the group the kill belongs to.
        var killKey = LootRollKeys.For(
            _roller.ProfileVersion,
            actor?.CharacterId,
            deathEventId,
            lifeId,
            target.GroupId ?? target.RecordId);
        var receipt = _roller.Roll(mobTemplateId, killKey);
        _receipts?.Record(receipt);
        var items = receipt.Groups
            .Where(group => group.Passed && group.ItemId is not null)
            .Select(group => new LootGrantItem(group.ItemId!, group.Quantity))
            .ToList();

        return Grant(
            actor,
            deathEventId,
            lifeId,
            grantEnabled: true,
            blockedReason: null,
            items: items,
            coin: _roller.RollCoinInclusive(killKey, decision.CoinMin, decision.CoinMax));
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
        IReadOnlyList<LootGrantItem> items,
        long coin = 0)
    {
        ArgumentNullException.ThrowIfNull(deathEventId);
        ArgumentOutOfRangeException.ThrowIfNegative(coin);

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

        if (actor is null || (items.Count == 0 && coin == 0))
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

        // Items and coin move in the one inventory mutation, so a receipt can never
        // describe money the actor does not have (`grantAndReceiptAtomic`).
        var mutation = new InventoryMutation
        {
            AddItems = items
                .Select(item => new ItemGrant
                {
                    TemplateId = item.TemplateId,
                    Stack = item.Stack,
                    Location = InventoryLocations.Bag
                })
                .ToList(),
            CurrencyDeltas = coin > 0
                ? [new CurrencyDelta { CurrencyId = LootCurrencyIds.Coin, Amount = coin }]
                : []
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
            GrantedTemplateIds: items.Select(item => item.TemplateId).ToArray(),
            Coin: coin));
    }
}

// The currency the alpha mob band pays in: `lootAlphaOnly` states a coin band, and
// COIN is that currency in the canonical catalog (the same id the quest rewards and
// the alpha chapter reward use).
public static class LootCurrencyIds
{
    public const string Coin = "COIN";
}

// The sourced roll-once identity of a kill:
// [profileVersion, characterId, deathEventId, lifeId, groupId]
// (DESIGN-BM-ALPHA-20261103 `lootAlphaOnly.rollOnceKey`). Every component is
// server-owned, so a retry of the same death rolls the same receipt and a different
// death never reuses one.
public static class LootRollKeys
{
    public static string For(
        string profileVersion,
        string? characterId,
        string deathEventId,
        long lifeId,
        string groupId) =>
        string.Join(
            '|',
            profileVersion,
            characterId ?? "UNOWNED",
            deathEventId,
            lifeId.ToString(CultureInfo.InvariantCulture),
            groupId);
}

public static class LootGrantErrorCodes
{
    public const string NothingToGrant = "loot_nothing_to_grant";
}
