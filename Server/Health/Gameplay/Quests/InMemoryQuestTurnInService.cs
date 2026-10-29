using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using Server.Health.Contracts;
using Server.Health.Gameplay.Inventory;
using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

public sealed class InMemoryQuestTurnInService : IQuestTurnInService
{
    private const string GroundFloor = "OVERWORLD";

    private readonly IQuestCatalog _catalog;
    private readonly IQuestService _quests;
    private readonly IInventoryService _inventory;
    private readonly NpcAnchorCatalog _anchors;
    private readonly IWorldGeometryService _geometry;
    private readonly RewardLedgerStore _ledger;
    private readonly QuestTurnInOptions _options;
    private readonly ConcurrentDictionary<(string CharacterId, string Key), TurnInResult>
        _entries = new();

    public InMemoryQuestTurnInService(
        IQuestCatalog catalog,
        IQuestService quests,
        IInventoryService inventory,
        NpcAnchorCatalog anchors,
        IWorldGeometryService geometry,
        RewardLedgerStore ledger,
        QuestTurnInOptions options)
    {
        _catalog = catalog;
        _quests = quests;
        _inventory = inventory;
        _anchors = anchors;
        _geometry = geometry;
        _ledger = ledger;
        _options = options;
    }

    public TurnInOutcome TurnIn(
        PlayerSession actor,
        string questId,
        string npcId,
        string idempotencyKey)
    {
        ArgumentNullException.ThrowIfNull(actor);

        var requestHash = Hash(questId, npcId);
        var key = (actor.CharacterId, idempotencyKey);
        if (_entries.TryGetValue(key, out var replayed))
        {
            if (!string.Equals(replayed.QuestState.QuestId, questId, StringComparison.Ordinal))
            {
                return TurnInOutcome.Rejected(
                    QuestTurnInErrorCodes.IdempotencyConflict,
                    retryable: false,
                    "idempotencyKey");
            }

            return TurnInOutcome.Success(replayed);
        }

        if (!_catalog.TryGet(questId, out var definition))
        {
            return TurnInOutcome.Rejected(
                QuestErrorCodes.QuestNotFound,
                retryable: false,
                "payload.questId");
        }

        if (!string.Equals(definition.TurnInNpcId, npcId, StringComparison.Ordinal))
        {
            return TurnInOutcome.Rejected(
                QuestTurnInErrorCodes.NpcMismatch,
                retryable: false,
                "payload.npcId");
        }

        if (!_anchors.TryResolve(npcId, actor.MapId, out var anchor) ||
            !string.Equals(anchor.FloorId, GroundFloor, StringComparison.Ordinal))
        {
            return TurnInOutcome.Rejected(
                QuestTurnInErrorCodes.OutOfRange, retryable: true);
        }

        var deltaX = actor.X - anchor.X;
        var deltaY = actor.Y - anchor.Y;
        var distance = Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY));
        if (distance > _options.MaxInteractionDistanceWu + 1e-9)
        {
            return TurnInOutcome.Rejected(
                QuestTurnInErrorCodes.OutOfRange, retryable: true);
        }

        var lineOfSight = _geometry.CheckLineOfSight(
            actor.MapId, GroundFloor, actor.X, actor.Y, anchor.X, anchor.Y);
        if (lineOfSight.IsBlocked)
        {
            return TurnInOutcome.Rejected(
                QuestTurnInErrorCodes.OutOfRange, retryable: true);
        }

        var current = _quests.GetState(actor.CharacterId, questId);
        if (!current.Accepted || current.State is null)
        {
            return TurnInOutcome.Rejected(
                QuestErrorCodes.QuestNotFound,
                retryable: false,
                "payload.questId");
        }

        if (!string.Equals(
                current.State.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal))
        {
            return TurnInOutcome.Rejected(
                QuestErrorCodes.InvalidTransition,
                retryable: false,
                "state");
        }

        // Atomic transaction: grant → flip → ledger, under actor lock. The state
        // check above is a fast path only; the authoritative re-check inside the
        // lock prevents a parallel turn-in from granting twice.
        TurnInResult result;
        lock (actor.SyncRoot)
        {
            var authoritative = _quests.GetState(actor.CharacterId, questId);
            if (!authoritative.Accepted || authoritative.State is null)
            {
                return TurnInOutcome.Rejected(
                    QuestErrorCodes.QuestNotFound,
                    retryable: false,
                    "payload.questId");
            }

            if (!string.Equals(
                    authoritative.State.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal))
            {
                return TurnInOutcome.Rejected(
                    QuestErrorCodes.InvalidTransition,
                    retryable: false,
                    "state");
            }

            var currencyDeltas = definition.Rewards.Currency
                .Select(c => new CurrencyDelta { CurrencyId = c.CurrencyId, Amount = c.Amount })
                .ToList();

            var itemGrants = definition.Rewards.ItemIds
                .Select(itemId => new ItemGrant
                {
                    TemplateId = itemId,
                    Stack = 1,
                    Location = InventoryLocations.Bag
                })
                .ToList();

            var mutation = new InventoryMutation
            {
                AddItems = itemGrants,
                CurrencyDeltas = currencyDeltas
            };

            var grant = _inventory.Apply(actor, mutation);
            if (!grant.IsSuccess)
            {
                return TurnInOutcome.Rejected(
                    grant.ErrorCode ?? P1ErrorCodes.InvalidPayload,
                    grant.Retryable,
                    grant.Field ?? "rewards");
            }

            var flipped = _quests.TurnIn(actor, questId);
            if (!flipped.Accepted || flipped.State is null)
            {
                return TurnInOutcome.Rejected(
                    QuestErrorCodes.InvalidTransition,
                    retryable: false,
                    "state");
            }

            var rewardSnapshot = BuildRewards(definition, mutation);
            result = new TurnInResult
            {
                QuestState = flipped.State,
                Rewards = rewardSnapshot,
                Unlocks = definition.Unlocks,
            };

            _ledger.TryRecord(actor.CharacterId, questId, result);
        }

        _entries[key] = result;
        return TurnInOutcome.Success(result);
    }

    private static TurnInRewards BuildRewards(
        QuestDefinition definition,
        InventoryMutation mutation)
    {
        var currency = mutation.CurrencyDeltas?
            .Select(d => new TurnInCurrencyReward { CurrencyId = d.CurrencyId, Amount = d.Amount })
            .ToList()
            ?? new List<TurnInCurrencyReward>();

        var items = mutation.AddItems?
            .Select(i => new TurnInItemReward { TemplateId = i.TemplateId, Stack = i.Stack, Location = i.Location })
            .ToList()
            ?? new List<TurnInItemReward>();

        var xp = new TurnInXpReward { XpRule = definition.Rewards.XpRule, Applied = false };

        return new TurnInRewards
        {
            Currency = currency.AsReadOnly(),
            Items = items.AsReadOnly(),
            Xp = xp,
        };
    }

    private static string Hash(string questId, string npcId) =>
        Convert.ToHexString(
            SHA256.HashData(Encoding.UTF8.GetBytes($"{questId}|{npcId}")));
}