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
    private readonly ConcurrentDictionary<(string CharacterId, string Key), TurnInIdempotencyEntry>
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

        // Fast-path replay: a stored result is always replayed without
        // revalidation (proposal step 1), even after the quest is COMPLETED.
        if (_entries.TryGetValue(key, out var stored))
        {
            return Replay(stored, requestHash);
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

        // Atomic transaction: replay → position/LOS → state → grant → flip →
        // ledger → idempotency entry, all under the actor lock. Failure at any
        // step rolls back every earlier step so nothing commits partially, and
        // parallel requests for the same character serialise on the same lock.
        lock (actor.SyncRoot)
        {
            // Authoritative replay re-check: a parallel same-key request must
            // replay the winner's stored result instead of granting twice.
            if (_entries.TryGetValue(key, out var winner))
            {
                return Replay(winner, requestHash);
            }

            // Position re-check at the transaction snapshot: the actor may have
            // moved between the fast-path validations and lock acquisition.
            if (!_anchors.TryResolve(npcId, actor.MapId, out var anchor) ||
                !string.Equals(anchor.FloorId, GroundFloor, StringComparison.Ordinal) ||
                !string.Equals(actor.FloorId, anchor.FloorId, StringComparison.Ordinal))
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
                actor.MapId, actor.FloorId, actor.X, actor.Y, anchor.X, anchor.Y);
            if (lineOfSight.IsBlocked)
            {
                return TurnInOutcome.Rejected(
                    QuestTurnInErrorCodes.OutOfRange, retryable: true);
            }

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

            var mutation = BuildGrantMutation(definition);
            var inventoryBefore = _inventory.GetSnapshot(actor.CharacterId);
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
                RollbackInventoryGrant(actor, inventoryBefore, grant.Snapshot!);
                return TurnInOutcome.Rejected(
                    flipped.Failure?.Code ?? QuestErrorCodes.InvalidTransition,
                    flipped.Failure?.Retryable ?? false,
                    flipped.Failure?.FieldErrors.ToArray() ?? ["state"]);
            }

            var rewardSnapshot = BuildRewards(definition, mutation);
            var result = new TurnInResult
            {
                QuestState = flipped.State,
                Rewards = rewardSnapshot,
                Unlocks = definition.Unlocks,
            };

            if (!_ledger.TryRecord(actor.CharacterId, questId, result))
            {
                RollbackInventoryGrant(actor, inventoryBefore, grant.Snapshot!);
                var reverted = _quests.RevertTurnIn(actor, questId);
                if (!reverted.Accepted)
                {
                    throw new InvalidOperationException(
                        $"Turn-in rollback failed for {actor.CharacterId}/{questId}: " +
                        reverted.Failure?.Code);
                }

                return TurnInOutcome.Rejected(
                    QuestTurnInErrorCodes.IdempotencyConflict,
                    retryable: true);
            }

            _entries[key] = new TurnInIdempotencyEntry(requestHash, result);
            return TurnInOutcome.Success(result);
        }
    }

    private static TurnInOutcome Replay(TurnInIdempotencyEntry entry, string requestHash) =>
        string.Equals(entry.RequestHash, requestHash, StringComparison.Ordinal)
            ? TurnInOutcome.Success(entry.Result)
            : TurnInOutcome.Rejected(
                QuestTurnInErrorCodes.IdempotencyConflict,
                retryable: false,
                "idempotencyKey");

    private static InventoryMutation BuildGrantMutation(QuestDefinition definition)
    {
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

        return new InventoryMutation
        {
            AddItems = itemGrants,
            CurrencyDeltas = currencyDeltas
        };
    }

    private void RollbackInventoryGrant(
        PlayerSession actor,
        InventorySnapshot before,
        InventorySnapshot after)
    {
        var removals = new List<ItemRemoval>();
        foreach (var item in after.Items)
        {
            var existed = before.Items.Any(existing =>
                string.Equals(existing.InstanceId, item.InstanceId, StringComparison.Ordinal));
            if (!existed)
            {
                removals.Add(new ItemRemoval { InstanceId = item.InstanceId, Stack = item.Stack });
            }
        }

        var deltas = new List<CurrencyDelta>();
        foreach (var currency in after.Currencies)
        {
            var beforeAmount = before.Currencies
                .FirstOrDefault(existing =>
                    string.Equals(existing.CurrencyId, currency.CurrencyId, StringComparison.Ordinal))
                ?.Amount ?? 0;
            var granted = currency.Amount - beforeAmount;
            if (granted != 0)
            {
                deltas.Add(new CurrencyDelta { CurrencyId = currency.CurrencyId, Amount = -granted });
            }
        }

        if (removals.Count == 0 && deltas.Count == 0)
        {
            return;
        }

        var rollback = _inventory.Apply(actor, new InventoryMutation
        {
            RemoveItems = removals,
            CurrencyDeltas = deltas
        });
        if (!rollback.IsSuccess)
        {
            throw new InvalidOperationException(
                $"Turn-in inventory rollback failed for {actor.CharacterId}: {rollback.ErrorCode}");
        }
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

    private sealed record TurnInIdempotencyEntry(string RequestHash, TurnInResult Result);
}
