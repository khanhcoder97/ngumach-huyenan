// QuestJournalPanel — hiển thị QuestJournalViewState từ QuestJournalPresenter.
// Hai section: Active và Completed. Click vào quest entry set selection. Nút đóng.
// Khi UncertainMutation: disable tất cả action buttons, hiện "Đang xử lý..."
// Owner: Antigravity Remote — Issue #80.

using System.Threading;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class QuestJournalPanel : MonoBehaviour
    {
        // ── State ────────────────────────────────────────────────────────────
        private IP1UIAdapter _adapter;
        private PanelRouter _router;
        private CancellationToken _ct;
        private QuestJournalPresenter _presenter;
        private bool _visible;

        // ── UIElements refs ──────────────────────────────────────────────────
        private VisualElement _root;
        private VisualElement _activeList;
        private VisualElement _completedList;
        private Label _statusLabel;
        private Label _detailLabel;

        // ── Init ─────────────────────────────────────────────────────────────

        public void Initialize(IP1UIAdapter adapter, PanelRouter router, CancellationToken ct)
        {
            _adapter = adapter;
            _router = router;
            _ct = ct;
            _presenter = new QuestJournalPresenter(adapter);
            _presenter.OnChanged += Render;
            BuildUI();
            Hide();
        }

        public void Show()
        {
            _visible = true;
            _root.style.display = DisplayStyle.Flex;
            _ = _presenter.LoadAsync(_ct);
        }

        public void Hide()
        {
            _visible = false;
            if (_root != null) _root.style.display = DisplayStyle.None;
        }

        // ── UI Build ─────────────────────────────────────────────────────────

        private void BuildUI()
        {
            _root = MakePanel();
            _root.style.position = Position.Absolute;
            _root.style.left = 50; _root.style.top = 50;
            _root.style.width = 340; _root.style.maxHeight = 480;

            // Header
            var header = new VisualElement { style = { flexDirection = FlexDirection.Row, justifyContent = Justify.SpaceBetween } };
            header.Add(new Label("Nhật ký nhiệm vụ") { style = { unityFontStyleAndWeight = FontStyle.Bold } });
            var closeBtn = new Button(() => _router.CloseTop()) { text = "✕" };
            closeBtn.style.minHeight = 32; closeBtn.style.minWidth = 32;
            header.Add(closeBtn);
            _root.Add(header);

            // Status
            _statusLabel = new Label { style = { display = DisplayStyle.None, whiteSpace = WhiteSpace.Normal, marginTop = 4 } };
            _root.Add(_statusLabel);

            // Scroll view
            var scroll = new ScrollView();
            scroll.style.flexGrow = 1;

            // Active section
            scroll.Add(new Label("— Đang thực hiện —") { style = { unityFontStyleAndWeight = FontStyle.Bold, marginTop = 6 } });
            _activeList = new VisualElement();
            scroll.Add(_activeList);

            // Completed section
            scroll.Add(new Label("— Đã hoàn thành —") { style = { unityFontStyleAndWeight = FontStyle.Bold, marginTop = 8 } });
            _completedList = new VisualElement();
            scroll.Add(_completedList);

            // Detail label
            _detailLabel = new Label { style = { whiteSpace = WhiteSpace.Normal, marginTop = 6, fontSize = 11 } };
            scroll.Add(_detailLabel);

            _root.Add(scroll);

            AttachToDocument();
        }

        private void AttachToDocument()
        {
            var doc = FindFirstObjectByType<UIDocument>();
            if (doc == null) { Debug.LogError("[QuestJournalPanel] No UIDocument found in scene."); return; }
            doc.rootVisualElement.Add(_root);
        }

        // ── Render ───────────────────────────────────────────────────────────

        private void Render()
        {
            if (!_visible || _root == null) return;

            var cs = _adapter.ConnectionState;
            if (cs == UIConnectionState.Expired || cs == UIConnectionState.Disconnected)
            { Hide(); return; }

            bool uncertain = cs == UIConnectionState.UncertainMutation || _adapter.HasPendingMutation;

            var state = _presenter.State;

            // Status label
            if (uncertain)
            {
                _statusLabel.text = "Đang xử lý...";
                _statusLabel.style.display = DisplayStyle.Flex;
            }
            else if (state.IsLoading)
            {
                _statusLabel.text = "Đang tải...";
                _statusLabel.style.display = DisplayStyle.Flex;
            }
            else if (state.IsError)
            {
                _statusLabel.text = "Lỗi: " + state.ErrorCode;
                _statusLabel.style.display = DisplayStyle.Flex;
            }
            else
            {
                _statusLabel.style.display = DisplayStyle.None;
            }

            if (state.Value == null) { _activeList.Clear(); _completedList.Clear(); _detailLabel.text = ""; return; }

            var journal = state.Value;
            string selectedId = journal.SelectedQuestId;

            // Active
            _activeList.Clear();
            foreach (var q in journal.Active)
            {
                var q_ = q;
                var btn = new Button(() => OnQuestClicked(q_.QuestId)) { text = q.DisplayName + " [" + q.State + "]" };
                btn.style.minHeight = 36; btn.SetEnabled(!uncertain);
                if (q.QuestId == selectedId)
                    btn.style.backgroundColor = new Color(0.2f, 0.45f, 0.7f, 1f);
                _activeList.Add(btn);
            }
            if (journal.Active.Count == 0)
                _activeList.Add(new Label("(trống)") { style = { opacity = 0.6f } });

            // Completed
            _completedList.Clear();
            foreach (var q in journal.Completed)
            {
                var q_ = q;
                var btn = new Button(() => OnQuestClicked(q_.QuestId)) { text = q.DisplayName };
                btn.style.minHeight = 36; btn.SetEnabled(!uncertain);
                btn.style.opacity = 0.65f;
                if (q.QuestId == selectedId)
                    btn.style.backgroundColor = new Color(0.2f, 0.45f, 0.7f, 1f);
                _completedList.Add(btn);
            }
            if (journal.Completed.Count == 0)
                _completedList.Add(new Label("(trống)") { style = { opacity = 0.6f } });

            // Detail
            if (selectedId != null)
            {
                QuestEntryView sel = null;
                foreach (var q in journal.Active) if (q.QuestId == selectedId) { sel = q; break; }
                if (sel == null) foreach (var q in journal.Completed) if (q.QuestId == selectedId) { sel = q; break; }
                _detailLabel.text = sel != null
                    ? sel.DisplayName + "\n" + (sel.StepDescription ?? "") + "\nBước: " + (sel.StepId ?? "-")
                    : "";
            }
            else
            {
                _detailLabel.text = "";
            }
        }

        private void OnQuestClicked(string questId)
        {
            if (_adapter.HasPendingMutation || _adapter.ConnectionState == UIConnectionState.UncertainMutation) return;
            _presenter.SetSelection(questId);
        }

        private void OnDestroy()
        {
            if (_presenter != null) _presenter.OnChanged -= Render;
        }

        private static VisualElement MakePanel()
        {
            var p = new VisualElement();
            p.style.backgroundColor = new Color(0.07f, 0.10f, 0.12f, 0.92f);
            p.style.paddingLeft = p.style.paddingRight = p.style.paddingTop = p.style.paddingBottom = 8;
            return p;
        }
    }
}
