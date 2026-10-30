// NpcDialoguePanel — hiển thị NpcDialogueViewState.
// Hiển thị greetingText, danh sách choices (button per choice). Disabled choice show lý do.
// Khi unavailableReason != null: hiện lý do, ẩn choices. Nút đóng gọi PanelRouter.CloseTop().
// Khi UncertainMutation: disable all actions.
// Owner: Antigravity Remote — Issue #80.

using System.Threading;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class NpcDialoguePanel : MonoBehaviour
    {
        // ── State ────────────────────────────────────────────────────────────
        private IP1UIAdapter _adapter;
        private PanelRouter _router;
        private CancellationToken _ct;
        private bool _visible;

        // ── View state injected externally (set by coordinator) ───────────────
        private NpcDialogueViewState _current;

        // ── UIElements refs ──────────────────────────────────────────────────
        private VisualElement _root;
        private Label _greetingLabel;
        private Label _unavailableLabel;
        private VisualElement _choiceList;
        private Label _statusLabel;

        // ── Init ─────────────────────────────────────────────────────────────

        public void Initialize(IP1UIAdapter adapter, PanelRouter router, CancellationToken ct)
        {
            _adapter = adapter;
            _router = router;
            _ct = ct;
            BuildUI();
            Hide();
        }

        /// <summary>Call before Show() to supply the NPC dialogue state.</summary>
        public void SetDialogue(NpcDialogueViewState state)
        {
            _current = state;
            if (_visible) Render();
        }

        public void Show()
        {
            _visible = true;
            _root.style.display = DisplayStyle.Flex;
            Render();
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
            _root.style.left = 80; _root.style.top = 80;
            _root.style.width = 360; _root.style.maxHeight = 500;

            // Header
            var header = new VisualElement { style = { flexDirection = FlexDirection.Row, justifyContent = Justify.SpaceBetween } };
            header.Add(new Label("Hội thoại NPC") { style = { unityFontStyleAndWeight = FontStyle.Bold } });
            var closeBtn = new Button(() => _router.CloseTop()) { text = "✕" };
            closeBtn.style.minHeight = 32; closeBtn.style.minWidth = 32;
            header.Add(closeBtn);
            _root.Add(header);

            // Status (uncertain/loading)
            _statusLabel = new Label { style = { display = DisplayStyle.None, whiteSpace = WhiteSpace.Normal, marginTop = 4 } };
            _root.Add(_statusLabel);

            // Greeting text
            _greetingLabel = new Label { style = { whiteSpace = WhiteSpace.Normal, marginTop = 8, marginBottom = 8 } };
            _root.Add(_greetingLabel);

            // Unavailable reason (shown instead of choices)
            _unavailableLabel = new Label { style = { whiteSpace = WhiteSpace.Normal, display = DisplayStyle.None, color = new Color(1f, 0.6f, 0.2f) } };
            _root.Add(_unavailableLabel);

            // Choice list
            _choiceList = new VisualElement { style = { marginTop = 4 } };
            _root.Add(_choiceList);

            AttachToDocument();
        }

        private void AttachToDocument()
        {
            var doc = FindFirstObjectByType<UIDocument>();
            if (doc == null) { Debug.LogError("[NpcDialoguePanel] No UIDocument found in scene."); return; }
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

            // Status label
            if (uncertain)
            {
                _statusLabel.text = "Đang xử lý...";
                _statusLabel.style.display = DisplayStyle.Flex;
            }
            else
            {
                _statusLabel.style.display = DisplayStyle.None;
            }

            if (_current == null)
            {
                _greetingLabel.text = "";
                _unavailableLabel.style.display = DisplayStyle.None;
                _choiceList.Clear();
                return;
            }

            _greetingLabel.text = _current.GreetingText ?? "";

            if (!_current.IsAvailable)
            {
                // Show reason, hide choices
                _unavailableLabel.text = _current.UnavailableReason;
                _unavailableLabel.style.display = DisplayStyle.Flex;
                _choiceList.style.display = DisplayStyle.None;
                _choiceList.Clear();
            }
            else
            {
                _unavailableLabel.style.display = DisplayStyle.None;
                _choiceList.style.display = DisplayStyle.Flex;
                _choiceList.Clear();

                foreach (var choice in _current.Choices)
                {
                    var choice_ = choice;
                    if (choice.Enabled)
                    {
                        var btn = new Button(() => OnChoiceClicked(choice_)) { text = choice.Label };
                        btn.style.minHeight = 40; btn.SetEnabled(!uncertain);
                        _choiceList.Add(btn);
                    }
                    else
                    {
                        // Disabled choice: show as label with reason
                        var row = new VisualElement { style = { flexDirection = FlexDirection.Row, alignItems = Align.Center, marginTop = 2 } };
                        var disabledBtn = new Button { text = choice.Label };
                        disabledBtn.style.minHeight = 40; disabledBtn.SetEnabled(false); disabledBtn.style.flexGrow = 1;
                        row.Add(disabledBtn);
                        if (!string.IsNullOrEmpty(choice.DisabledReason))
                        {
                            var reason = new Label(choice.DisabledReason) { style = { fontSize = 10, opacity = 0.7f, marginLeft = 4, whiteSpace = WhiteSpace.Normal, flexShrink = 1 } };
                            row.Add(reason);
                        }
                        _choiceList.Add(row);
                    }
                }
            }
        }

        private void OnChoiceClicked(DialogueChoice choice)
        {
            if (_adapter.HasPendingMutation || _adapter.ConnectionState == UIConnectionState.UncertainMutation) return;
            // Choice action: interact with NPC — delegate to adapter.
            // The coordinator (PlayerUIRoot) handles resulting dialogue state changes.
            _ = _adapter.InteractAsync(_current?.NpcId ?? "", _ct);
        }

        // ── Helpers ──────────────────────────────────────────────────────────

        private static VisualElement MakePanel()
        {
            var p = new VisualElement();
            p.style.backgroundColor = new Color(0.07f, 0.10f, 0.12f, 0.92f);
            p.style.paddingLeft = p.style.paddingRight = p.style.paddingTop = p.style.paddingBottom = 8;
            return p;
        }
    }
}
