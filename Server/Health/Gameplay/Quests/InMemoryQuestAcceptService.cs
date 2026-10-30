using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

public sealed class InMemoryQuestAcceptService : IQuestAcceptService
{
    private const string GroundFloor = "OVERWORLD";

    private readonly IQuestCatalog _catalog;
    private readonly IQuestService _quests;
    private readonly NpcAnchorCatalog _anchors;
    private readonly IWorldGeometryService _geometry;
    private readonly QuestAcceptOptions _options;
    private readonly ConcurrentDictionary<(string CharacterId, string Key), IdempotencyEntry>
        _entries = new();

    public InMemoryQuestAcceptService(
        IQuestCatalog catalog,
        IQuestService quests,
        NpcAnchorCatalog anchors,
        IWorldGeometryService geometry,
        QuestAcceptOptions options)
    {
        _catalog = catalog;
        _quests = quests;
        _anchors = anchors;
        _geometry = geometry;
        _options = options;
    }

    public QuestAcceptOutcome Accept(
        PlayerSession actor,
        string questId,
        string npcId,
        string idempotencyKey)
    {
        ArgumentNullException.ThrowIfNull(actor);

        var requestHash = Hash(questId, npcId);
        var key = (actor.CharacterId, idempotencyKey);
        if (_entries.TryGetValue(key, out var entry))
        {
            if (!string.Equals(entry.RequestHash, requestHash, StringComparison.Ordinal))
            {
                return QuestAcceptOutcome.Rejected(
                    QuestAcceptErrorCodes.IdempotencyConflict,
                    retryable: false,
                    state: null,
                    "idempotencyKey");
            }

            return QuestAcceptOutcome.Success(entry.State);
        }

        if (!_catalog.TryGet(questId, out var definition))
        {
            return QuestAcceptOutcome.Rejected(
                QuestErrorCodes.QuestNotFound,
                retryable: false,
                state: null,
                "payload.questId");
        }

        var current = CurrentState(actor.CharacterId, questId);

        if (!string.Equals(definition.StartNpcId, npcId, StringComparison.Ordinal))
        {
            return QuestAcceptOutcome.Rejected(
                QuestAcceptErrorCodes.NpcMismatch,
                retryable: false,
                current,
                "payload.npcId");
        }

        // A quest whose source is still incomplete is refused for that reason
        // rather than for a prerequisite the player may already meet: the field
        // errors name the design steps waiting on content, so "walk closer" is
        // never the advice for a quest that cannot open yet.
        if (definition.IsBlocked)
        {
            return QuestAcceptOutcome.Rejected(
                QuestAcceptErrorCodes.PrerequisiteNotMet,
                retryable: false,
                current,
                [.. definition.Blocked.Select(step => $"activation.blocked.{step.DesignStep}")]);
        }

        if (!_anchors.TryResolve(npcId, actor.MapId, out var anchor) ||
            !string.Equals(anchor.FloorId, GroundFloor, StringComparison.Ordinal))
        {
            return QuestAcceptOutcome.Rejected(
                QuestAcceptErrorCodes.OutOfRange, retryable: true, current);
        }

        var deltaX = actor.X - anchor.X;
        var deltaY = actor.Y - anchor.Y;
        var distance = Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY));
        if (distance > _options.MaxInteractionDistanceWu + 1e-9)
        {
            return QuestAcceptOutcome.Rejected(
                QuestAcceptErrorCodes.OutOfRange, retryable: true, current);
        }

        var lineOfSight = _geometry.CheckLineOfSight(
            actor.MapId, GroundFloor, actor.X, actor.Y, anchor.X, anchor.Y);
        if (lineOfSight.IsBlocked)
        {
            return QuestAcceptOutcome.Rejected(
                QuestAcceptErrorCodes.OutOfRange, retryable: true, current);
        }

        if (!PrerequisitesMet(actor.CharacterId, definition))
        {
            return QuestAcceptOutcome.Rejected(
                QuestAcceptErrorCodes.PrerequisiteNotMet, retryable: false, current);
        }

        if (actor.Level < definition.MinLevel || actor.Level > definition.MaxLevel)
        {
            return QuestAcceptOutcome.Rejected(
                QuestAcceptErrorCodes.PrerequisiteNotMet, retryable: false, current);
        }

        if (current is null)
        {
            return QuestAcceptOutcome.Rejected(
                QuestErrorCodes.QuestNotFound,
                retryable: false,
                state: null,
                "payload.questId");
        }

        if (!string.Equals(current.State, QuestStates.Available, StringComparison.Ordinal))
        {
            var code = string.Equals(current.State, QuestStates.Locked, StringComparison.Ordinal)
                ? QuestAcceptErrorCodes.PrerequisiteNotMet
                : QuestErrorCodes.InvalidTransition;

            return QuestAcceptOutcome.Rejected(code, retryable: false, current, "state");
        }

        var accepted = _quests.Accept(actor, questId);
        if (!accepted.Accepted || accepted.State is null)
        {
            return QuestAcceptOutcome.Rejected(
                QuestErrorCodes.InvalidTransition,
                retryable: false,
                accepted.State,
                "state");
        }

        _entries[key] = new IdempotencyEntry(requestHash, accepted.State);
        return QuestAcceptOutcome.Success(accepted.State);
    }

    private QuestState? CurrentState(string characterId, string questId) =>
        _quests.GetState(characterId, questId).State;

    private bool PrerequisitesMet(string characterId, QuestDefinition definition)
    {
        foreach (var prerequisiteId in definition.PrerequisiteQuestIds)
        {
            var prerequisite = _quests.GetState(characterId, prerequisiteId);
            if (!prerequisite.Accepted || prerequisite.State is null ||
                !string.Equals(
                    prerequisite.State.State, QuestStates.Completed, StringComparison.Ordinal))
            {
                return false;
            }
        }

        return true;
    }

    private static string Hash(string questId, string npcId) =>
        Convert.ToHexString(
            SHA256.HashData(Encoding.UTF8.GetBytes($"{questId}|{npcId}")));

    private sealed record IdempotencyEntry(string RequestHash, QuestState State);
}
