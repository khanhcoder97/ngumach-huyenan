// NpcDialoguePanel — MonoBehaviour điều khiển panel hội thoại NPC.
// Hiển thị lời thoại, choices tương tác (nhận/nộp quest, tạm biệt).
// Tôn trọng state server authoritative; không tự sinh thưởng hoặc cờ cốt truyện.
// Owner: Antigravity Remote — Issue #80.

using System;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class NpcDialoguePanel : MonoBehaviour
    {
        private IP1UIAdapter _adapter;
        private PanelRouter _router;
        private CancellationToken _ct;
        private NpcDialoguePresenter _presenter;

        private VisualElement _root;
        private bool _visible;
        private UIDocument _doc;
        private Action _onPresenterChanged;
        private NpcDialogueViewState _current;

        private Label _npcNameLabel;
        private Label _greetingLabel;
        private Label _unavailableLabel;
        private VisualElement _choiceList;
        private Label _statusLabel;

        // ── Init ─────────────────────────────────────────────────────────────

        public void Initialize(IP1UIAdapter adapter, PanelRouter router, CancellationToken ct, NpcDialoguePresenter presenter = null, UIDocument doc = null)
        {
            if (_presenter != null && _onPresenterChanged != null)
            {
                _presenter.OnChanged -= _onPresenterChanged;
            }
            _adapter = adapter;
            _router = router;
            _ct = ct;
            _doc = doc ?? _doc;
            _presenter = presenter ?? new NpcDialoguePresenter(adapter);
            _onPresenterChanged = () => SetDialogue(_presenter.State.Value);
            _presenter.OnChanged += _onPresenterChanged;
            if (_root == null) BuildUI();
            else AttachToDocument(_doc);
            Hide();
        }

        /// <summary>Call before Show() to supply the NPC dialogue state.</summary>
        public void SetDialogue(NpcDialogueViewState state)
        {
            _current = state;
            if (_visible) Render();
        }

        /// <summary>Open dialogue with specific NPC.</summary>
        public async Task OpenWithNpcAsync(string npcId)
        {
            Show();
            if (_presenter != null && !string.IsNullOrEmpty(npcId))
            {
                await _presenter.InteractAsync(npcId, _ct);
            }
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
            _presenter?.Clear();
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

            // NPC Name
            _npcNameLabel = new Label { style = { unityFontStyleAndWeight = FontStyle.Bold, marginTop = 6, fontSize = 14 } };
            _root.Add(_npcNameLabel);

            // Greeting text
            _greetingLabel = new Label { style = { whiteSpace = WhiteSpace.Normal, marginTop = 6, opacity = 0.9f } };
            _root.Add(_greetingLabel);

            // Unavailable label
            _unavailableLabel = new Label { style = { whiteSpace = WhiteSpace.Normal, marginTop = 6, color = new Color(1f, 0.4f, 0.4f), display = DisplayStyle.None } };
            _root.Add(_unavailableLabel);

            // Status label
            _statusLabel = new Label { style = { display = DisplayStyle.None, whiteSpace = WhiteSpace.Normal, marginTop = 4 } };
            _root.Add(_statusLabel);

            // Choice list
            _choiceList = new VisualElement { style = { marginTop = 8 } };
            _root.Add(_choiceList);

            AttachToDocument();
        }

        private void AttachToDocument(UIDocument doc = null)
        {
            _doc = doc ?? _doc;
            if (_doc == null || _root == null) return;
            if (_root.parent != _doc.rootVisualElement)
            {
                _root.RemoveFromHierarchy();
                _doc.rootVisualElement.Add(_root);
            }
        }

        // ── Render ───────────────────────────────────────────────────────────

        private void Render()
        {
            if (!_visible || _root == null) return;

            var cs = _adapter.ConnectionState;
            if (cs == UIConnectionState.Expired || cs == UIConnectionState.Disconnected)
            { Hide(); return; }

            bool uncertain = cs == UIConnectionState.UncertainMutation || _adapter.HasPendingMutation;

            if (_presenter != null && _presenter.State.IsLoading)
            {
                _statusLabel.text = "Đang tải dữ liệu thoại...";
                _statusLabel.style.display = DisplayStyle.Flex;
            }
            else if (uncertain)
            {
                _statusLabel.text = "Đang thực hiện hành động...";
                _statusLabel.style.display = DisplayStyle.Flex;
            }
            else
            {
                _statusLabel.style.display = DisplayStyle.None;
            }

            if (_current == null)
            {
                _npcNameLabel.text = "";
                _greetingLabel.text = "Không có tương tác.";
                _choiceList.Clear();
                return;
            }

            _npcNameLabel.text = _current.NpcId ?? "";

            if (!_current.IsAvailable)
            {
                _greetingLabel.text = "";
                _unavailableLabel.text = "Không thể tương tác: " + (_current.UnavailableReason ?? "Không khả dụng");
                _unavailableLabel.style.display = DisplayStyle.Flex;
                _choiceList.style.display = DisplayStyle.None;
            }
            else
            {
                _greetingLabel.text = _current.GreetingText ?? "";
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

        private async void OnChoiceClicked(DialogueChoice choice)
        {
            if (_adapter.HasPendingMutation || _adapter.ConnectionState == UIConnectionState.UncertainMutation) return;

            switch (choice.ActionType)
            {
                case DialogueActionType.AcceptQuest:
                    if (!string.IsNullOrEmpty(choice.QuestId) && !string.IsNullOrEmpty(choice.NpcId))
                    {
                        await _presenter.AcceptQuestAsync(choice.QuestId, choice.NpcId, _ct);
                    }
                    break;
                case DialogueActionType.TurnInQuest:
                    if (!string.IsNullOrEmpty(choice.QuestId) && !string.IsNullOrEmpty(choice.NpcId))
                    {
                        await _presenter.TurnInQuestAsync(choice.QuestId, choice.NpcId, _ct);
                    }
                    break;
                case DialogueActionType.Close:
                    _router.CloseTop();
                    break;
                default:
                    await _presenter.InteractAsync(_current?.NpcId ?? "", _ct);
                    break;
            }
        }

        // ── Helpers ──────────────────────────────────────────────────────────

        public void Teardown()
        {
            Hide();
            if (_presenter != null)
            {
                if (_onPresenterChanged != null)
                {
                    _presenter.OnChanged -= _onPresenterChanged;
                }
                _presenter.Clear();
                _presenter = null;
            }
            if (_root != null && _root.parent != null)
            {
                _root.RemoveFromHierarchy();
            }
            _current = null;
            _adapter = null;
            _router = null;
            _doc = null;
        }

        private void OnDestroy() => Teardown();

        private static VisualElement MakePanel()
        {
            var p = new VisualElement();
            p.style.backgroundColor = new Color(0.07f, 0.10f, 0.12f, 0.92f);
            p.style.paddingLeft = p.style.paddingRight = p.style.paddingTop = p.style.paddingBottom = 8;
            return p;
        }
    }
}
