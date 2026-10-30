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

            var result = await _adapter.InteractAsync(targetId, ct);
            if (!result.Success)
            {
                _state = _state.WithError(result.Code, result.CorrelationId);
                NotifyChanged();
                return _state;
            }

            // Build a minimal dialogue view. Full NPC record/choice data requires catalog;
            // until catalog API is available, show targetId and available quest actions.
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

            var result = await _adapter.AcceptQuestAsync(questId, npcId, ct);
            if (!result.Success)
            {
                _state = _state.WithError(result.Code, result.CorrelationId);
                NotifyChanged();
                return _state;
            }

            // After accept, rebuild choices to reflect new quest state
            var choices = BuildChoicesFromQuestState(npcId);
            var current = _state.Value;
            _state = _state.WithValue(new NpcDialogueViewState(
                current?.NpcId ?? npcId, current?.RecordId ?? npcId, current?.Kind ?? "NPC",
                current?.GreetingText ?? npcId, choices));
            NotifyChanged();
            return _state;
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

        public void Clear()
        {
            _state = AsyncState<NpcDialogueViewState>.Idle;
            NotifyChanged();
        }

        private List<DialogueChoice> BuildChoicesFromQuestState(string npcId)
        {
            // Build choices based on actual server quest state.
            // All logic is authoritative — no local guessing of quest progression.
            var choices = new List<DialogueChoice>();
            var quests = _adapter.Quests ?? Array.Empty<P1Quest>();
            int idx = 0;
            foreach (var q in quests)
            {
                if (q == null) continue;
                if (q.state == "AVAILABLE")
                    choices.Add(new DialogueChoice(idx++, "[Nhận nhiệm vụ] " + q.questId + " (UNRESOLVED)", enabled: true));
                else if (q.state == "READY_TO_TURN_IN")
                    choices.Add(new DialogueChoice(idx++, "[Nộp nhiệm vụ] " + q.questId + " (UNRESOLVED)", enabled: true));
                else if (q.state == "ACTIVE")
                    choices.Add(new DialogueChoice(idx++, "[Đang làm] " + q.questId, enabled: false, disabledReason: "Chưa hoàn thành mục tiêu"));
            }
            if (choices.Count == 0)
                choices.Add(new DialogueChoice(0, "Tạm biệt", enabled: true));
            return choices;
        }

        private void NotifyChanged() => OnChanged?.Invoke();
    }
}
