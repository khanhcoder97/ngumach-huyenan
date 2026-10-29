using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using Server.Health.Contracts;
using Server.Health.Gameplay.Inventory;
using Server.Health.Gameplay.Quests;
using Server.Health.World;

namespace Server.Health.Gameplay.Interactions;

public sealed class InMemoryInteractionService : IInteractionService
{
    private readonly WorldEntityRegistry _entities;
    private readonly WorldRecordCatalog _records;
    private readonly IQuestService _quests;
    private readonly IInventoryService _inventory;
    private readonly IWorldGeometryService _geometry;
    private readonly IServerClock _clock;
    private readonly IYieldRoller _rolls;
    private readonly GatherClaimStore _claims;
    private readonly InteractionOptions _options;
    private readonly ConcurrentDictionary<(string CharacterId, string Key), IdempotencyEntry>
        _entries = new();

    public InMemoryInteractionService(
        WorldEntityRegistry entities,
        WorldRecordCatalog records,
        IQuestService quests,
        IInventoryService inventory,
        IWorldGeometryService geometry,
        IServerClock clock,
        IYieldRoller rolls,
        GatherClaimStore claims,
        InteractionOptions options)
    {
        _entities = entities;
        _records = records;
        _quests = quests;
        _inventory = inventory;
        _geometry = geometry;
        _clock = clock;
        _rolls = rolls;
        _claims = claims;
        _options = options;
    }

    public InteractionOutcome Interact(
        PlayerSession actor,
        string targetId,
        string idempotencyKey)
    {
        ArgumentNullException.ThrowIfNull(actor);

        if (!P1Validation.IsCharacterId(actor.CharacterId))
        {
            return InteractionOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, "characterId");
        }

        if (!P1Validation.IsEntityId(targetId))
        {
            return InteractionOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, "payload.targetId");
        }

        var key = (actor.CharacterId, idempotencyKey);
        var requestHash = Hash(targetId);

        // Fast-path replay: a stored result is returned without revalidation.
        if (_entries.TryGetValue(key, out var stored))
        {
            return Replay(stored, requestHash);
        }

        // Transaction boundary: replay → guards → claim → grant → quest event →
        // idempotency entry, all under the actor lock. Parallel requests for
        // the same character serialise here; the shared entity registry and the
        // per-character claim store each add their own atomic check-and-set for
        // cross-character races.
        lock (actor.SyncRoot)
        {
            // Authoritative replay re-check: a parallel same-key request must
            // replay the winner's stored result instead of claiming twice.
            if (_entries.TryGetValue(key, out var winner))
            {
                return Replay(winner, requestHash);
            }

            if (!_entities.TryGet(targetId, out var entity))
            {
                return InteractionOutcome.Rejected(
                    InteractionErrorCodes.TargetNotFound, retryable: false, "payload.targetId");
            }

            if (entity.Kind is not (WorldEntityKinds.Interactable or WorldEntityKinds.GatherNode))
            {
                return InteractionOutcome.Rejected(
                    InteractionErrorCodes.InvalidTarget, retryable: false, "payload.targetId");
            }

            if (!string.Equals(entity.MapId, actor.MapId, StringComparison.Ordinal) ||
                !string.Equals(entity.FloorId, actor.FloorId, StringComparison.Ordinal))
            {
                return InteractionOutcome.Rejected(
                    InteractionErrorCodes.OutOfRange, retryable: true, "payload.targetId");
            }

            var deltaX = actor.X - entity.X;
            var deltaY = actor.Y - entity.Y;
            var distance = Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY));
            if (distance > _options.MaxInteractionDistanceWu + 1e-9)
            {
                return InteractionOutcome.Rejected(
                    InteractionErrorCodes.OutOfRange, retryable: true, "payload.targetId");
            }

            var lineOfSight = _geometry.CheckLineOfSight(
                actor.MapId, entity.FloorId, actor.X, actor.Y, entity.X, entity.Y);
            if (lineOfSight.IsBlocked)
            {
                return InteractionOutcome.Rejected(
                    InteractionErrorCodes.OutOfRange, retryable: true, "payload.targetId");
            }

            var claimedAt = _clock.UtcNow;
            var eventId = Guid.NewGuid().ToString("N");
            var eventType = entity.Kind == WorldEntityKinds.GatherNode
                ? QuestProgressEventTypes.GatherClaim
                : QuestProgressEventTypes.InteractClaim;

            string? respawnAtUtc = null;
            InteractYield? yield = null;

            if (entity.Kind == WorldEntityKinds.Interactable)
            {
                if (!_entities.Despawn(entity.EntityId))
                {
                    return InteractionOutcome.Rejected(
                        InteractionErrorCodes.TargetNotAvailable, retryable: false, "payload.targetId");
                }

                if (entity.RespawnSeconds > 0)
                {
                    respawnAtUtc = P1Time.ToUtcString(claimedAt.AddSeconds(entity.RespawnSeconds));
                }
            }
            else
            {
                if (!_records.TryGet(entity.RecordId, out var record) || record.Gather is null)
                {
                    throw new InvalidOperationException(
                        $"Gather node '{entity.EntityId}' has no gather metadata for " +
                        $"record '{entity.RecordId}'.");
                }

                if (record.Gather.ProfessionLevelRequired > _options.AssumedProfessionLevel)
                {
                    return InteractionOutcome.Rejected(
                        InteractionErrorCodes.ProfessionLevelInsufficient,
                        retryable: false,
                        "payload.targetId");
                }

                // Claim before granting: a cooldown rejection must not grant items.
                if (!_claims.TryClaim(
                        actor.CharacterId, entity.EntityId, entity.RespawnSeconds,
                        out var respawnAt, out var claimToken))
                {
                    return InteractionOutcome.Rejected(
                        InteractionErrorCodes.TargetNotAvailable, retryable: false, "payload.targetId");
                }

                var quantity = _rolls.Roll(record.Gather.YieldMin, record.Gather.YieldMax);
                var granted = _inventory.Apply(actor, new InventoryMutation
                {
                    AddItems =
                    [
                        new ItemGrant
                        {
                            TemplateId = record.Gather.ItemId,
                            Stack = quantity,
                            Location = InventoryLocations.Bag
                        }
                    ]
                });
                if (!granted.IsSuccess)
                {
                    // Failed requests must not consume the node's availability
                    // window; release only this request's own reservation.
                    _claims.Release(actor.CharacterId, entity.EntityId, claimToken);
                    return InteractionOutcome.Rejected(
                        InteractionErrorCodes.TargetNotAvailable, retryable: true, "payload.targetId");
                }

                if (entity.RespawnSeconds > 0)
                {
                    respawnAtUtc = P1Time.ToUtcString(respawnAt);
                }

                yield = new InteractYield { ItemId = record.Gather.ItemId, Quantity = quantity };
            }

            var questUpdates = _quests.RecordVerifiedEvent(
                actor, eventId, eventType, entity.RecordId, entity.MapId);

            var result = new InteractResult
            {
                InteractionId = eventId,
                TargetId = entity.EntityId,
                RecordId = entity.RecordId,
                Kind = entity.Kind,
                Outcome = entity.Kind == WorldEntityKinds.GatherNode ? "gathered" : "collected",
                TargetState = entity.State,
                ClaimedAtUtc = P1Time.ToUtcString(claimedAt),
                RespawnAtUtc = respawnAtUtc,
                Yield = yield,
                QuestUpdates = questUpdates
            };

            _entries[key] = new IdempotencyEntry(requestHash, result);
            return InteractionOutcome.Success(result);
        }
    }

    private static InteractionOutcome Replay(IdempotencyEntry entry, string requestHash) =>
        string.Equals(entry.RequestHash, requestHash, StringComparison.Ordinal)
            ? InteractionOutcome.Success(entry.Result)
            : InteractionOutcome.Rejected(
                InteractionErrorCodes.IdempotencyConflict,
                retryable: false,
                "idempotencyKey");

    private static string Hash(string targetId) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(targetId)));

    private sealed record IdempotencyEntry(string RequestHash, InteractResult Result);
}

public static class InteractionContentValidator
{
    public static void Validate(WorldEntityRegistry entities, WorldRecordCatalog records)
    {
        foreach (var entity in entities.All)
        {
            if (entity.Kind is not (WorldEntityKinds.Interactable or WorldEntityKinds.GatherNode))
            {
                continue;
            }

            if (!records.TryGet(entity.RecordId, out var record))
            {
                throw new InvalidOperationException(
                    $"Entity '{entity.EntityId}' recordId '{entity.RecordId}' has no world record.");
            }

            if (!string.Equals(record.MapId, entity.MapId, StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"Entity '{entity.EntityId}' mapId does not match record '{entity.RecordId}'.");
            }

            if (entity.Kind == WorldEntityKinds.GatherNode && record.Gather is null)
            {
                throw new InvalidOperationException(
                    $"Gather node '{entity.EntityId}' record '{entity.RecordId}' has no gather metadata.");
            }
        }
    }
}
