// AG3 — NpcDialoguePresenter: wraps InteractAsync/TurnInQuestAsync for dialogue panel.
// No Unity dependency. Builds NpcDialogueViewState from interaction results.
// Rules:
//   - Retry uncertain goes back to same pending command, never re-sends a different one.
//   - Choosing an option never writes story flags or rewards locally.
//   - UnavailableReason shown with correlationId when applicable.
//   - Invalidate presentation generation on Clear/interact to drop late completions (AGR2-02).
//   - Canonical NPC ID used for quest wire commands; entity ID preserved for interact (AGR2-01).
// Owner: Antigravity Remote — Issue #80, #85.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class NpcDialoguePresenter
    {
        private readonly IP1UIAdapter _adapter;
        private AsyncState<NpcDialogueViewState> _state = AsyncState<NpcDialogueViewState>.Idle;
        private int _generation;

        public AsyncState<NpcDialogueViewState> State => _state;
        public event Action OnChanged;

        public NpcDialoguePresenter(IP1UIAdapter adapter)
            => _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));

        /// <summary>Interact with a target (NPC, node). Builds dialogue view from result.</summary>
        public async Task<AsyncState<NpcDialogueViewState>> InteractAsync(string targetId, CancellationToken ct)
        {
            if (_adapter.HasPendingMutation)
            {
                _state = _state.WithError("pending_mutation");
                NotifyChanged();
                return _state;
            }

            int curGen = Interlocked.Increment(ref _generation);
            _state = _state.WithLoading();
            NotifyChanged();

            try
            {
                var result = await _adapter.InteractAsync(targetId, ct);
                if (curGen != _generation) return _state;

                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    NotifyChanged();
                    return _state;
                }

                var context = NpcContextMapping.Resolve(targetId);
                string canonicalNpcId = context.TemplateId;
                var choices = BuildChoicesFromQuestState(canonicalNpcId);

                var view = new NpcDialogueViewState(
                    npcId: canonicalNpcId,
                    recordId: context.RecordId,
                    kind: "NPC",
                    greetingText: context.DisplayName,
                    choices: choices,
                    unavailableReason: null,
                    correlationId: null,
                    interactionTargetEntityId: context.EntityId);

                if (curGen != _generation) return _state;
                _state = _state.WithValue(view);
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                if (curGen != _generation) return _state;
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<NpcDialogueViewState>.Idle;
                NotifyChanged();
                throw;
            }
            catch (Exception ex)
            {
                if (curGen != _generation) return _state;
                _state = _state.WithError(ex.Message);
                NotifyChanged();
                throw;
            }
        }

        /// <summary>Accept quest via dialogue.</summary>
        public async Task<AsyncState<NpcDialogueViewState>> AcceptQuestAsync(string questId, string npcId, CancellationToken ct)
        {
            if (_adapter.HasPendingMutation)
            {
                _state = _state.WithError("pending_mutation");
                NotifyChanged();
                return _state;
            }

            int curGen = Interlocked.Increment(ref _generation);
            _state = _state.WithLoading();
            NotifyChanged();

            try
            {
                var context = NpcContextMapping.Resolve(npcId);
                string canonicalNpcId = context.TemplateId;

                var result = await _adapter.AcceptQuestAsync(questId, canonicalNpcId, ct);
                if (curGen != _generation) return _state;

                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    NotifyChanged();
                    return _state;
                }

                var choices = BuildChoicesFromQuestState(canonicalNpcId);
                var current = _state.Value;
                _state = _state.WithValue(new NpcDialogueViewState(
                    canonicalNpcId,
                    current?.RecordId ?? context.RecordId,
                    current?.Kind ?? "NPC",
                    current?.GreetingText ?? context.DisplayName,
                    choices,
                    interactionTargetEntityId: current?.InteractionTargetEntityId ?? context.EntityId));
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                if (curGen != _generation) return _state;
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<NpcDialogueViewState>.Idle;
                NotifyChanged();
                throw;
            }
            catch (Exception ex)
            {
                if (curGen != _generation) return _state;
                _state = _state.WithError(ex.Message);
                NotifyChanged();
                throw;
            }
        }

        /// <summary>Turn in quest via dialogue.</summary>
        public async Task<AsyncState<NpcDialogueViewState>> TurnInQuestAsync(string questId, string npcId, CancellationToken ct)
        {
            if (_adapter.HasPendingMutation)
            {
                _state = _state.WithError("pending_mutation");
                NotifyChanged();
                return _state;
            }

            int curGen = Interlocked.Increment(ref _generation);
            _state = _state.WithLoading();
            NotifyChanged();

            try
            {
                var context = NpcContextMapping.Resolve(npcId);
                string canonicalNpcId = context.TemplateId;

                var result = await _adapter.TurnInQuestAsync(questId, canonicalNpcId, ct);
                if (curGen != _generation) return _state;

                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    NotifyChanged();
                    return _state;
                }

                var choices = BuildChoicesFromQuestState(canonicalNpcId);
                var current = _state.Value;
                _state = _state.WithValue(new NpcDialogueViewState(
                    canonicalNpcId,
                    current?.RecordId ?? context.RecordId,
                    current?.Kind ?? "NPC",
                    current?.GreetingText ?? context.DisplayName,
                    choices,
                    interactionTargetEntityId: current?.InteractionTargetEntityId ?? context.EntityId));
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                if (curGen != _generation) return _state;
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<NpcDialogueViewState>.Idle;
                NotifyChanged();
                throw;
            }
            catch (Exception ex)
            {
                if (curGen != _generation) return _state;
                _state = _state.WithError(ex.Message);
                NotifyChanged();
                throw;
            }
        }

        public void Clear()
        {
            Interlocked.Increment(ref _generation);
            _state = AsyncState<NpcDialogueViewState>.Idle;
            NotifyChanged();
        }

        private List<DialogueChoice> BuildChoicesFromQuestState(string npcTemplateId)
        {
            var choices = new List<DialogueChoice>();
            var quests = _adapter.Quests ?? Array.Empty<P1Quest>();
            int idx = 0;

            foreach (var q in quests)
            {
                if (q == null) continue;

                if (QuestNpcCatalog.IsQuestStartNpc(q.questId, npcTemplateId) && q.state == "AVAILABLE")
                {
                    choices.Add(new DialogueChoice(
                        idx++,
                        "[Nhận nhiệm vụ] " + q.questId,
                        enabled: true,
                        actionType: DialogueActionType.AcceptQuest,
                        questId: q.questId,
                        npcId: npcTemplateId));
                }
                else if (QuestNpcCatalog.IsQuestTurnInNpc(q.questId, npcTemplateId) && q.state == "READY_TO_TURN_IN")
                {
                    choices.Add(new DialogueChoice(
                        idx++,
                        "[Nộp nhiệm vụ] " + q.questId,
                        enabled: true,
                        actionType: DialogueActionType.TurnInQuest,
                        questId: q.questId,
                        npcId: npcTemplateId));
                }
                else if (QuestNpcCatalog.IsQuestStartNpc(q.questId, npcTemplateId) || QuestNpcCatalog.IsQuestTurnInNpc(q.questId, npcTemplateId))
                {
                    if (q.state == "ACTIVE")
                    {
                        choices.Add(new DialogueChoice(
                            idx++,
                            "[Đang làm] " + q.questId,
                            enabled: false,
                            disabledReason: "Chưa hoàn thành mục tiêu",
                            actionType: DialogueActionType.Interact,
                            questId: q.questId,
                            npcId: npcTemplateId));
                    }
                }
            }

            choices.Add(new DialogueChoice(idx, "Tạm biệt", enabled: true, actionType: DialogueActionType.Close, npcId: npcTemplateId));
            return choices;
        }

        private void NotifyChanged() => OnChanged?.Invoke();
    }
}
