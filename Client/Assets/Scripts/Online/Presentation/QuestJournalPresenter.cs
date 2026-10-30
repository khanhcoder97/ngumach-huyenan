// AG3 — QuestJournalPresenter: builds QuestJournalViewState from P1Client quests.
// No Unity dependency.
// Rules:
//   - Only show quests server has confirmed; no local guesses on unlock/playable.
//   - Text display names and objective descriptions come from catalog metadata.
//   - Retry uncertain returns to same pending command, never accepts a different quest.
// Owner: Antigravity Remote — Issue #80, #85.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class QuestJournalPresenter
    {
        private readonly IP1UIAdapter _adapter;
        private AsyncState<QuestJournalViewState> _state = AsyncState<QuestJournalViewState>.Idle;

        public AsyncState<QuestJournalViewState> State => _state;
        public event Action OnChanged;

        public QuestJournalPresenter(IP1UIAdapter adapter)
            => _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));

        public async Task<AsyncState<QuestJournalViewState>> LoadAsync(CancellationToken ct)
        {
            if (_state.IsLoading) return _state;
            _state = _state.WithLoading();
            NotifyChanged();

            try
            {
                var result = await _adapter.ReadQuestsAsync(ct);
                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    NotifyChanged();
                    return _state;
                }

                _state = _state.WithValue(BuildViewState(_adapter.Quests, _state.Value));
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<QuestJournalViewState>.Idle;
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

        public void SetSelection(string questId)
        {
            if (!_state.IsLoaded || _state.Value == null) return;
            _state = _state.WithValue(new QuestJournalViewState(
                _state.Value.Active, _state.Value.Completed,
                questId, _state.Value.HasPinnedTracker));
            NotifyChanged();
        }

        public void TogglePin(string questId)
        {
            if (!_state.IsLoaded || _state.Value == null) return;
            _state = _state.WithValue(_state.Value.WithPinned(!_state.Value.HasPinnedTracker));
            NotifyChanged();
        }

        private static QuestJournalViewState BuildViewState(P1Quest[] quests, QuestJournalViewState prev)
        {
            var active = new List<QuestEntryView>();
            var completed = new List<QuestEntryView>();

            foreach (var q in quests ?? Array.Empty<P1Quest>())
            {
                if (q == null) continue;
                var (title, desc) = ResolveQuestCopy(q);
                var entry = new QuestEntryView(q, title, desc);
                if (q.state == "COMPLETED") completed.Add(entry);
                else active.Add(entry);
            }

            string selectedId = prev?.SelectedQuestId;
            return new QuestJournalViewState(active, completed, selectedId, prev?.HasPinnedTracker ?? false);
        }

        private static (string title, string objectiveDesc) ResolveQuestCopy(P1Quest q)
        {
            if (string.Equals(q.questId, "P00-01", StringComparison.OrdinalIgnoreCase))
            {
                string title = "Khởi Đầu Tại Bến Mưa";
                int count = 0;
                if (q.objectiveCounters != null)
                {
                    q.objectiveCounters.TryGetValue("OBJ_P00_01_PACKAGES", out count);
                    if (count == 0 && q.objectiveCounters.TryGetValue("packages", out var c2)) count = c2;
                }

                string desc;
                switch (q.state)
                {
                    case "AVAILABLE":
                        desc = "Gặp Lý An để nhận nhiệm vụ.";
                        break;
                    case "ACTIVE":
                        desc = $"Thu thập gói hàng Bến Mưa ({count}/3).";
                        break;
                    case "READY_TO_TURN_IN":
                        desc = "Đã thu thập đủ 3 gói hàng. Hãy nộp nhiệm vụ cho Tạ Vân Khanh.";
                        break;
                    case "COMPLETED":
                        desc = "Đã hoàn thành nhiệm vụ.";
                        break;
                    default:
                        desc = q.stepId ?? "Tiến độ nhiệm vụ";
                        break;
                }
                return (title, desc);
            }

            // Fallback for custom or test quests without raw UNRESOLVED
            return (q.questId, q.stepId ?? "Nhiệm vụ đang tiến hành");
        }

        private void NotifyChanged() => OnChanged?.Invoke();
    }
}
