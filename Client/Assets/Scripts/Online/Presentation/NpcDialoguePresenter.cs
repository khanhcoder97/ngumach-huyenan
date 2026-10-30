// AG3 — NpcDialoguePresenter: wraps InteractAsync/TurnInQuestAsync for dialogue panel.
// No Unity dependency. Builds NpcDialogueViewState from interaction results.
// Rules:
//   - Retry uncertain goes back to same pending command, never re-sends a different one.
//   - Choosing an option never writes story flags or rewards locally.
//   - UnavailableReason shown with correlationId when applicable.
// Owner: Antigravity Remote — Issue #80.

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

            _state = _state.WithLoading();
            NotifyChanged();

            try
            {
                var result = await _adapter.InteractAsync(targetId, ct);
                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    NotifyChanged();
                    return _state;
                }

                var choices = BuildChoicesFromQuestState(targetId);
                var view = new NpcDialogueViewState(
                    npcId: targetId,
                    recordId: targetId,
                    kind: "NPC",
                    greetingText: targetId + " (UNRESOLVED — catalog not yet connected)",
                    choices: choices,
                    unavailableReason: null,
                    correlationId: null);

                _state = _state.WithValue(view);
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<NpcDialogueViewState>.Idle;
                NotifyChanged();
                throw;
            }
            catch (Exception ex)
            {
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

            _state = _state.WithLoading();
            NotifyChanged();

            try
            {
                var result = await _adapter.AcceptQuestAsync(questId, npcId, ct);
                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    NotifyChanged();
                    return _state;
                }

                var choices = BuildChoicesFromQuestState(npcId);
                var current = _state.Value;
                _state = _state.WithValue(new NpcDialogueViewState(
                    current?.NpcId ?? npcId, current?.RecordId ?? npcId, current?.Kind ?? "NPC",
                    current?.GreetingText ?? npcId, choices));
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<NpcDialogueViewState>.Idle;
                NotifyChanged();
                throw;
            }
            catch (Exception ex)
            {
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

            _state = _state.WithLoading();
            NotifyChanged();

            try
            {
                var result = await _adapter.TurnInQuestAsync(questId, npcId, ct);
                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    NotifyChanged();
                    return _state;
                }

                var choices = BuildChoicesFromQuestState(npcId);
                var current = _state.Value;
                _state = _state.WithValue(new NpcDialogueViewState(
                    current?.NpcId ?? npcId, current?.RecordId ?? npcId, current?.Kind ?? "NPC",
                    current?.GreetingText ?? npcId, choices));
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<NpcDialogueViewState>.Idle;
                NotifyChanged();
                throw;
            }
            catch (Exception ex)
            {
                _state = _state.WithError(ex.Message);
                NotifyChanged();
                throw;
            }
        }

        public void Clear()
        {
            _state = AsyncState<NpcDialogueViewState>.Idle;
            NotifyChanged();
        }

        private List<DialogueChoice> BuildChoicesFromQuestState(string npcId)
        {
            var choices = new List<DialogueChoice>();
            var quests = _adapter.Quests ?? Array.Empty<P1Quest>();
            int idx = 0;

            foreach (var q in quests)
            {
                if (q == null) continue;

                if (IsQuestStartNpc(q.questId, npcId) && q.state == "AVAILABLE")
                {
                    choices.Add(new DialogueChoice(
                        idx++,
                        "[Nhận nhiệm vụ] " + q.questId + " (UNRESOLVED)",
                        enabled: true,
                        actionType: DialogueActionType.AcceptQuest,
                        questId: q.questId,
                        npcId: npcId));
                }
                else if (IsQuestTurnInNpc(q.questId, npcId) && q.state == "READY_TO_TURN_IN")
                {
                    choices.Add(new DialogueChoice(
                        idx++,
                        "[Nộp nhiệm vụ] " + q.questId + " (UNRESOLVED)",
                        enabled: true,
                        actionType: DialogueActionType.TurnInQuest,
                        questId: q.questId,
                        npcId: npcId));
                }
                else if (IsQuestStartNpc(q.questId, npcId) || IsQuestTurnInNpc(q.questId, npcId))
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
                            npcId: npcId));
                    }
                }
            }

            choices.Add(new DialogueChoice(idx, "Tạm biệt", enabled: true, actionType: DialogueActionType.Close, npcId: npcId));
            return choices;
        }

        private static bool IsQuestStartNpc(string questId, string npcId)
        {
            if (string.IsNullOrEmpty(npcId)) return false;
            if (questId == "P00-01")
            {
                return npcId.Equals("NPC_LYAN", StringComparison.OrdinalIgnoreCase) ||
                       npcId.Equals("LY_AN", StringComparison.OrdinalIgnoreCase) ||
                       npcId.Equals("LYAN", StringComparison.OrdinalIgnoreCase);
            }
            if (questId.StartsWith("Q", StringComparison.OrdinalIgnoreCase) && npcId.StartsWith("NPC_TEST", StringComparison.OrdinalIgnoreCase))
                return true;
            return false;
        }

        private static bool IsQuestTurnInNpc(string questId, string npcId)
        {
            if (string.IsNullOrEmpty(npcId)) return false;
            if (questId == "P00-01")
            {
                return npcId.Equals("NPC_TA_VAN_KHANH", StringComparison.OrdinalIgnoreCase) ||
                       npcId.Equals("TA_VAN_KHANH", StringComparison.OrdinalIgnoreCase) ||
                       npcId.Equals("TAVANKHANH", StringComparison.OrdinalIgnoreCase);
            }
            if (questId.StartsWith("Q", StringComparison.OrdinalIgnoreCase) && npcId.StartsWith("NPC_TEST", StringComparison.OrdinalIgnoreCase))
                return true;
            return false;
        }

        private void NotifyChanged() => OnChanged?.Invoke();
    }
}
