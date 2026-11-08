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

    public QuestOutcome GetState(PlayerSession actor, string questId)
    {
        ArgumentNullException.ThrowIfNull(actor);
        lock (actor.SyncRoot)
        {
            return ReadState(actor.CharacterId, questId, actor.Level);
        }
    }

    // Character-only reads cannot establish authoritative level eligibility.
    public QuestOutcome GetState(string characterId, string questId) =>
        ReadState(characterId, questId, level: null);

    private QuestOutcome ReadState(string characterId, string questId, int? level)
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

        var state = GetOrCreate(characterId, definition, level);
        lock (state.SyncRoot)
        {
            if (level is { } authoritativeLevel)
            {
                RefreshAvailability(characterId, definition, state, authoritativeLevel);
            }
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
            if (!_quests.TryGet(state.QuestId, out _))
            {
                continue;
            }

            lock (state.SyncRoot)
            {
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

        lock (actor.SyncRoot)
        {
            var state = GetOrCreate(actor.CharacterId, definition, actor.Level);
            lock (state.SyncRoot)
            {
                RefreshAvailability(actor.CharacterId, definition, state, actor.Level);
                if (actor.Level < definition.MinLevel || actor.Level > definition.MaxLevel)
                {
                    return new QuestOutcome(state.ToContract(), new QuestFailure(
                        QuestAcceptErrorCodes.PrerequisiteNotMet, false, ["level"]));
                }

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
                // Alpha orderedObjectives (DESIGN-BM-ALPHA-20261103 P00-05):
                // only the first incomplete objective accepts progress, so the
                // boss must be down before the fragment can be collected.
                QuestObjectiveDefinition? orderedGate = null;
                if (definition.OrderedObjectives)
                {
                    foreach (var candidate in definition.Objectives)
                    {
                        if (state.ObjectiveCounters.GetValueOrDefault(candidate.ObjectiveId) <
                            candidate.Count)
                        {
                            orderedGate = candidate;
                            break;
                        }
                    }
                }

                foreach (var objective in definition.Objectives)
                {
                    if (orderedGate is not null &&
                        !string.Equals(
                            orderedGate.ObjectiveId, objective.ObjectiveId, StringComparison.Ordinal))
                    {
                        continue;
                    }

                    if (!ObjectiveAcceptsEvent(objective, eventType, recordId, mapId))
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
            QuestObjectiveTypes.Boss => eventType == QuestProgressEventTypes.Kill,
            QuestObjectiveTypes.MapViewed => eventType == QuestProgressEventTypes.MapEnter,
            _ => false
        };

        if (!accepts)
        {
            return false;
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
            // Kill and boss objectives count deaths; dedupe by event so a
            // replay of the same death never double-counts the same life.
            QuestObjectiveTypes.Kill or QuestObjectiveTypes.Boss =>
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

    private PlayerQuestState GetOrCreate(
        string characterId, QuestDefinition definition, int? level)
    {
        return _states.GetOrAdd(characterId, definition.QuestId, () =>
        {
            var initialState = level is { } authoritativeLevel &&
                               IsAvailable(characterId, definition, authoritativeLevel)
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
        PlayerQuestState state,
        int level)
    {
        if (state.State is not (QuestStates.Locked or QuestStates.Available))
        {
            return;
        }

        var next = IsAvailable(characterId, definition, level)
            ? QuestStates.Available
            : QuestStates.Locked;
        if (!string.Equals(state.State, next, StringComparison.Ordinal))
        {
            state.State = next;
            state.Revision++;
            state.UpdatedAtUtc = _clock.UtcNow;
        }
    }

    private bool IsAvailable(string characterId, QuestDefinition definition, int level) =>
        !definition.IsBlocked && level >= definition.MinLevel && level <= definition.MaxLevel &&
        PrerequisitesMet(characterId, definition);

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
