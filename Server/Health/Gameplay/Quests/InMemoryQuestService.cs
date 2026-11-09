using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

public static class QuestProgressEventTypes
{
    public const string InteractClaim = "INTERACT_CLAIM";
    public const string GatherClaim = "GATHER_CLAIM";
    public const string Talk = "TALK";
    public const string Kill = "KILL";
    public const string MapEnter = "MAP_ENTER";
}

public sealed class InMemoryQuestService : IQuestService
{
    private readonly IQuestCatalog _quests;
    private readonly IQuestStateStore _states;
    private readonly WorldRecordCatalog _records;
    private readonly IServerClock _clock;

    public InMemoryQuestService(
        IQuestCatalog quests,
        IQuestStateStore states,
        WorldRecordCatalog records,
        IServerClock clock)
    {
        _quests = quests;
        _states = states;
        _records = records;
        _clock = clock;
    }

    public QuestOutcome GetState(string characterId, string questId)
    {
        if (!P1Validation.IsCharacterId(characterId))
        {
            return QuestOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, "characterId");
        }

        if (!TryGetDefinition(questId, out var definition, out var definitionFailure))
        {
            return definitionFailure!;
        }

        var state = GetOrCreate(characterId, definition);
        lock (state.SyncRoot)
        {
            RefreshAvailability(characterId, definition, state);
            return QuestOutcome.Success(state.ToContract());
        }
    }

    public IReadOnlyList<QuestState> GetStates(string characterId)
    {
        if (!P1Validation.IsCharacterId(characterId))
        {
            return Array.Empty<QuestState>();
        }

        var snapshots = new List<QuestState>();
        foreach (var state in _states.GetForCharacter(characterId))
        {
            if (!_quests.TryGet(state.QuestId, out var definition))
            {
                continue;
            }

            lock (state.SyncRoot)
            {
                RefreshAvailability(characterId, definition, state);
                snapshots.Add(state.ToContract());
            }
        }

        return snapshots;
    }

    public QuestOutcome Accept(PlayerSession actor, string questId)
    {
        ArgumentNullException.ThrowIfNull(actor);

        if (!P1Validation.IsCharacterId(actor.CharacterId))
        {
            return QuestOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, "characterId");
        }

        if (!TryGetDefinition(questId, out var definition, out var definitionFailure))
        {
            return definitionFailure!;
        }

        var state = GetOrCreate(actor.CharacterId, definition);
        lock (state.SyncRoot)
        {
            RefreshAvailability(actor.CharacterId, definition, state);
            if (!string.Equals(state.State, QuestStates.Available, StringComparison.Ordinal))
            {
                return QuestOutcome.InvalidTransition(state.ToContract());
            }

            state.State = QuestStates.Active;
            state.StepId = definition.InitialStepId;
            state.Revision++;
            state.UpdatedAtUtc = _clock.UtcNow;
            return QuestOutcome.Success(state.ToContract());
        }
    }

    public IReadOnlyList<QuestState> RecordVerifiedEvent(
        PlayerSession actor,
        string eventId,
        string eventType,
        string recordId,
        string mapId)
    {
        ArgumentNullException.ThrowIfNull(actor);

        var changed = new List<QuestState>();
        if (!P1Validation.IsCharacterId(actor.CharacterId) ||
            !P1Validation.IsHex32(eventId) ||
            string.IsNullOrWhiteSpace(eventType) ||
            string.IsNullOrWhiteSpace(recordId))
        {
            return changed;
        }

        foreach (var state in _states.GetForCharacter(actor.CharacterId))
        {
            if (!_quests.TryGet(state.QuestId, out var definition))
            {
                continue;
            }

            lock (state.SyncRoot)
            {
                if (!string.Equals(state.State, QuestStates.Active, StringComparison.Ordinal))
                {
                    continue;
                }

                var revisionBefore = state.Revision;
                foreach (var objective in definition.Objectives)
                {
                    if (!ObjectiveAcceptsEvent(objective, eventType, recordId, mapId))
                    {
                        continue;
                    }

                    // Skip one-shot objectives that are already complete
                    if (objective.AttemptOneShot == true &&
                        state.ObjectiveCounters.GetValueOrDefault(objective.ObjectiveId) >= objective.Count)
                    {
                        continue;
                    }

                    var key = ContributionKey(objective, eventId, recordId);
                    if (!state.Contributions.Add(key))
                    {
                        continue;
                    }

                    var current = state.ObjectiveCounters.GetValueOrDefault(objective.ObjectiveId);
                    var next = Math.Min(objective.Count, current + 1);
                    if (next == current)
                    {
                        continue;
                    }

                    state.ObjectiveCounters[objective.ObjectiveId] = next;
                    if (AllObjectivesComplete(definition, state))
                    {
                        state.State = QuestStates.ReadyToTurnIn;
                    }

                    state.Revision++;
                    state.UpdatedAtUtc = _clock.UtcNow;
                }

                if (state.Revision != revisionBefore)
                {
                    changed.Add(state.ToContract());
                }
            }
        }

        return changed;
    }

    public IReadOnlyList<QuestState> CreditMapEnter(
        string characterId,
        string mapId,
        string? floorId = null)
    {
        ArgumentNullException.ThrowIfNull(characterId);
        ArgumentNullException.ThrowIfNull(mapId);

        var changed = new List<QuestState>();

        if (!P1Validation.IsCharacterId(characterId) ||
            !P1Validation.IsMapId(mapId))
        {
            return changed;
        }

        foreach (var state in _states.GetForCharacter(characterId))
        {
            if (!_quests.TryGet(state.QuestId, out var definition))
            {
                continue;
            }

            lock (state.SyncRoot)
            {
                if (!string.Equals(state.State, QuestStates.Active, StringComparison.Ordinal))
                {
                    continue;
                }

                var eventId = Guid.NewGuid().ToString("X").PadLeft(32, '0');
                var revisionBefore = state.Revision;

                foreach (var objective in definition.Objectives)
                {
                    if (!string.Equals(objective.Type, QuestObjectiveTypes.MapViewed, StringComparison.Ordinal))
                    {
                        continue;
                    }

                    if (!string.Equals(objective.MapId, mapId, StringComparison.Ordinal))
                    {
                        continue;
                    }

                    // Floor-level specificity check
                    if (floorId is not null && objective.FloorId is not null &&
                        !string.Equals(objective.FloorId, floorId, StringComparison.Ordinal))
                    {
                        continue;
                    }

                    // Check prerequisites before crediting MAP_VIEWED
                    if (objective.RequiredCompletedObjectiveIds is { Count: > 0 } prereqs)
                    {
                        var prereqsMet = true;
                        foreach (var prereqId in prereqs)
                        {
                            var prereqCount = state.ObjectiveCounters.GetValueOrDefault(prereqId);
                            if (prereqCount < 1)
                            {
                                prereqsMet = false;
                                break;
                            }
                        }

                        if (!prereqsMet)
                        {
                            continue;
                        }
                    }

                    // Skip one-shot objectives that are already complete
                    if (objective.AttemptOneShot == true &&
                        state.ObjectiveCounters.GetValueOrDefault(objective.ObjectiveId) >= objective.Count)
                    {
                        continue;
                    }

                    // Use a synthetic contribution key for map entry events
                    var key = string.Concat("M:", objective.ObjectiveId, ":", mapId);
                    if (!state.Contributions.Contains(key))
                    {
                        state.Contributions.Add(key);

                        var current = state.ObjectiveCounters.GetValueOrDefault(objective.ObjectiveId);
                        var next = Math.Min(objective.Count, current + 1);
                        if (next > current)
                        {
                            state.ObjectiveCounters[objective.ObjectiveId] = next;
                        }
                    }

                    if (AllObjectivesComplete(definition, state))
                    {
                        state.State = QuestStates.ReadyToTurnIn;
                    }

                    state.Revision++;
                    state.UpdatedAtUtc = _clock.UtcNow;
                }

                if (state.Revision != revisionBefore)
                {
                    changed.Add(state.ToContract());
                }
            }
        }

        return changed;
    }

    private bool ObjectiveAcceptsEvent(
        QuestObjectiveDefinition objective,
        string eventType,
        string recordId,
        string mapId)
    {
        if (!string.Equals(objective.MapId, mapId, StringComparison.Ordinal))
        {
            return false;
        }

        var accepts = objective.Type switch
        {
            QuestObjectiveTypes.Collect =>
                eventType is QuestProgressEventTypes.InteractClaim or QuestProgressEventTypes.GatherClaim,
            QuestObjectiveTypes.Interact => eventType == QuestProgressEventTypes.InteractClaim,
            QuestObjectiveTypes.Talk => eventType == QuestProgressEventTypes.Talk,
            QuestObjectiveTypes.Kill => eventType == QuestProgressEventTypes.Kill,
            QuestObjectiveTypes.MapViewed => eventType == QuestProgressEventTypes.MapEnter,
            _ => false
        };

        if (!accepts)
        {
            return false;
        }

        // For MAP_VIEWED, check prerequisites first
        if (string.Equals(objective.Type, QuestObjectiveTypes.MapViewed, StringComparison.Ordinal) &&
            objective.RequiredCompletedObjectiveIds is { Count: > 0 } prereqs)
        {
            // Prerequisites are validated at accept time via the quest state
            // We don't re-check here; instead, we rely on the fact that only
            // active quests with completed prerequisites can reach this point.
        }

        foreach (var targetId in objective.TargetIds)
        {
            if (string.Equals(targetId, recordId, StringComparison.Ordinal))
            {
                return true;
            }

            // Quest definitions reference canonical entity_id values; the event
            // carries the recordId, so resolve and compare the entityId.
            if (_records.TryGet(recordId, out var record) &&
                record.EntityIds.Contains(targetId, StringComparer.Ordinal))
            {
                return true;
            }
        }

        return false;
    }

    private static string ContributionKey(
        QuestObjectiveDefinition objective,
        string eventId,
        string recordId) =>
        objective.Type switch
        {
            // Kill counts repeat kills of the same record; dedupe by event instead.
            QuestObjectiveTypes.Kill =>
                string.Concat("E:", objective.ObjectiveId, ":", eventId),
            // Production Rules §5: unique(actor, quest, objective, record).
            // State is already per character + quest; the objective scope keeps
            // two valid objectives that reference the same record independent.
            _ => string.Concat("R:", objective.ObjectiveId, ":", recordId)
        };

    public QuestOutcome TurnIn(PlayerSession actor, string questId)
    {
        ArgumentNullException.ThrowIfNull(actor);

        if (!P1Validation.IsCharacterId(actor.CharacterId))
        {
            return QuestOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, "characterId");
        }

        if (!TryGetDefinition(questId, out var definition, out var definitionFailure))
        {
            return definitionFailure!;
        }

        var state = _states.Find(actor.CharacterId, definition.QuestId);
        if (state is null)
        {
            return QuestOutcome.Rejected(
                QuestErrorCodes.QuestNotFound, retryable: false, "questId");
        }

        lock (state.SyncRoot)
        {
            if (!string.Equals(state.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal))
            {
                return QuestOutcome.InvalidTransition(state.ToContract());
            }

            state.State = QuestStates.Completed;
            state.Revision++;
            state.UpdatedAtUtc = _clock.UtcNow;
            return QuestOutcome.Success(state.ToContract());
        }
    }

    public QuestOutcome RevertTurnIn(PlayerSession actor, string questId)
    {
        ArgumentNullException.ThrowIfNull(actor);

        if (!P1Validation.IsCharacterId(actor.CharacterId))
        {
            return QuestOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, "characterId");
        }

        if (!TryGetDefinition(questId, out var definition, out var definitionFailure))
        {
            return definitionFailure!;
        }

        var state = _states.Find(actor.CharacterId, definition.QuestId);
        if (state is null)
        {
            return QuestOutcome.Rejected(
                QuestErrorCodes.QuestNotFound, retryable: false, "questId");
        }

        lock (state.SyncRoot)
        {
            if (!string.Equals(state.State, QuestStates.Completed, StringComparison.Ordinal))
            {
                return QuestOutcome.InvalidTransition(state.ToContract());
            }

            state.State = QuestStates.ReadyToTurnIn;
            state.Revision--;
            state.UpdatedAtUtc = _clock.UtcNow;
            return QuestOutcome.Success(state.ToContract());
        }
    }

    public QuestOutcome Fail(PlayerSession actor, string questId)
    {
        ArgumentNullException.ThrowIfNull(actor);

        if (!P1Validation.IsCharacterId(actor.CharacterId))
        {
            return QuestOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, "characterId");
        }

        if (!TryGetDefinition(questId, out var definition, out var definitionFailure))
        {
            return definitionFailure!;
        }

        var state = _states.Find(actor.CharacterId, definition.QuestId);
        if (state is null)
        {
            return QuestOutcome.Rejected(
                QuestErrorCodes.QuestNotFound, retryable: false, "questId");
        }

        lock (state.SyncRoot)
        {
            if (!string.Equals(state.State, QuestStates.Active, StringComparison.Ordinal) &&
                !string.Equals(state.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal))
            {
                return QuestOutcome.InvalidTransition(state.ToContract());
            }

            state.State = QuestStates.Failed;
            state.Revision++;
            state.UpdatedAtUtc = _clock.UtcNow;
            return QuestOutcome.Success(state.ToContract());
        }
    }

    private PlayerQuestState GetOrCreate(string characterId, QuestDefinition definition)
    {
        return _states.GetOrAdd(characterId, definition.QuestId, () =>
        {
            // A blocked quest is not a playable quest: it keeps its place in the
            // graph but never becomes available, however complete the player's
            // prerequisites are.
            var initialState = !definition.IsBlocked &&
                               PrerequisitesMet(characterId, definition)
                ? QuestStates.Available
                : QuestStates.Locked;

            return new PlayerQuestState(
                characterId,
                definition.QuestId,
                initialState,
                definition.InitialStepId,
                definition.Objectives.Select(objective => objective.ObjectiveId),
                _clock.UtcNow);
        });
    }

    private void RefreshAvailability(
        string characterId,
        QuestDefinition definition,
        PlayerQuestState state)
    {
        if (!definition.IsBlocked &&
            string.Equals(state.State, QuestStates.Locked, StringComparison.Ordinal) &&
            PrerequisitesMet(characterId, definition))
        {
            state.State = QuestStates.Available;
            state.Revision++;
            state.UpdatedAtUtc = _clock.UtcNow;
        }
    }

    private bool PrerequisitesMet(string characterId, QuestDefinition definition)
    {
        foreach (var prerequisiteQuestId in definition.PrerequisiteQuestIds)
        {
            var prerequisite = _states.Find(characterId, prerequisiteQuestId);
            if (prerequisite is null ||
                !string.Equals(prerequisite.State, QuestStates.Completed, StringComparison.Ordinal))
            {
                return false;
            }
        }

        return true;
    }

    private static bool AllObjectivesComplete(
        QuestDefinition definition,
        PlayerQuestState state)
    {
        foreach (var objective in definition.Objectives)
        {
            if (state.ObjectiveCounters.GetValueOrDefault(objective.ObjectiveId) < objective.Count)
            {
                return false;
            }
        }

        return true;
    }

    private bool TryGetDefinition(
        string? questId,
        out QuestDefinition definition,
        out QuestOutcome? failure)
    {
        definition = null!;
        if (!P1Validation.IsQuestId(questId))
        {
            failure = QuestOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, "questId");
            return false;
        }

        if (!_quests.TryGet(questId!, out definition))
        {
            failure = QuestOutcome.Rejected(
                QuestErrorCodes.UnknownQuest, retryable: false, "questId");
            return false;
        }

        failure = null;
        return true;
    }
}
