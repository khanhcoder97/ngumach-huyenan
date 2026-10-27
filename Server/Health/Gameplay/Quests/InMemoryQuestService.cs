using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

public sealed class InMemoryQuestService : IQuestService
{
    private readonly IQuestCatalog _quests;
    private readonly IQuestStateStore _states;
    private readonly ServerClock _clock;

    public InMemoryQuestService(IQuestCatalog quests, IQuestStateStore states, ServerClock clock)
    {
        _quests = quests;
        _states = states;
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

    public QuestOutcome RecordObjective(
        PlayerSession actor,
        string questId,
        string objectiveId,
        int amount)
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

        if (!P1Validation.IsObjectiveId(objectiveId))
        {
            return QuestOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, "objectiveId");
        }

        if (amount < 1)
        {
            return QuestOutcome.Rejected(
                QuestErrorCodes.InvalidAmount, retryable: false, "amount");
        }

        QuestObjectiveDefinition? objective = null;
        foreach (var candidate in definition.Objectives)
        {
            if (string.Equals(candidate.ObjectiveId, objectiveId, StringComparison.Ordinal))
            {
                objective = candidate;
                break;
            }
        }

        if (objective is null)
        {
            return QuestOutcome.Rejected(
                QuestErrorCodes.UnknownObjective, retryable: false, "objectiveId");
        }

        var state = _states.Find(actor.CharacterId, definition.QuestId);
        if (state is null)
        {
            return QuestOutcome.Rejected(
                QuestErrorCodes.QuestNotFound, retryable: false, "questId");
        }

        lock (state.SyncRoot)
        {
            if (!string.Equals(state.State, QuestStates.Active, StringComparison.Ordinal))
            {
                return QuestOutcome.InvalidTransition(state.ToContract());
            }

            var current = state.ObjectiveCounters.GetValueOrDefault(objective.ObjectiveId);
            var next = (int)Math.Min(objective.Count, (long)current + amount);
            if (next > current)
            {
                state.ObjectiveCounters[objective.ObjectiveId] = next;
                if (AllObjectivesComplete(definition, state))
                {
                    state.State = QuestStates.ReadyToTurnIn;
                }

                state.Revision++;
                state.UpdatedAtUtc = _clock.UtcNow;
            }

            return QuestOutcome.Success(state.ToContract());
        }
    }

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
            var initialState = PrerequisitesMet(characterId, definition)
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
        if (string.Equals(state.State, QuestStates.Locked, StringComparison.Ordinal) &&
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
