// AG3 — QuestJournalPresenter: builds QuestJournalViewState from P1Client quests.
// No Unity dependency.
// Rules:
//   - Only show quests server has confirmed; no local guesses on unlock/playable.
//   - Text display names come from catalog; if unavailable, show questId (UNRESOLVED).
//   - Retry uncertain returns to same pending command, never accepts a different quest.
// Owner: Antigravity Remote — Issue #80.

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

        private static QuestJournalViewState BuildViewState(P1Quest[] quests, QuestJournalViewState prev)
        {
            var active = new List<QuestEntryView>();
            var completed = new List<QuestEntryView>();

            foreach (var q in quests ?? Array.Empty<P1Quest>())
            {
                if (q == null) continue;
                var entry = new QuestEntryView(q); // displayName=null → UNRESOLVED
                if (q.state == "COMPLETED") completed.Add(entry);
                else active.Add(entry);
            }

            string selectedId = prev?.SelectedQuestId;
            return new QuestJournalViewState(active, completed, selectedId, prev?.HasPinnedTracker ?? false);
        }

        private void NotifyChanged() => OnChanged?.Invoke();
    }
}
