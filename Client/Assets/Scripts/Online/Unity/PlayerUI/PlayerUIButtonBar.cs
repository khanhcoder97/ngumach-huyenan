// PlayerUIButtonBar — thanh nút mở panel (Inventory, QuestJournal, Settings, Map).
// Click gọi PlayerUIRoot.OpenPanel(PlayerPanel.X).
// Hiện/ẩn dựa trên connection state.
// Owner: Antigravity Remote — Issue #80.

using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class PlayerUIButtonBar : MonoBehaviour
    {
        // ── State ────────────────────────────────────────────────────────────
        private IP1UIAdapter _adapter;
        private PlayerUIRoot _root;

        // ── UIElements refs ──────────────────────────────────────────────────
        private VisualElement _bar;
        private Button _inventoryBtn;
        private Button _questBtn;
        private Button _settingsBtn;
        private Button _mapBtn;

        // ── Init ─────────────────────────────────────────────────────────────

        public void Initialize(IP1UIAdapter adapter, PlayerUIRoot root)
        {
            _adapter = adapter;
            _root = root;
            BuildUI();
        }

        // ── UI Build ─────────────────────────────────────────────────────────

        private void BuildUI()
        {
            _bar = new VisualElement();
            _bar.style.position = Position.Absolute;
            _bar.style.right = 10; _bar.style.top = 10;
            _bar.style.flexDirection = FlexDirection.Row;
            _bar.style.backgroundColor = new Color(0.07f, 0.10f, 0.12f, 0.88f);
            _bar.style.paddingLeft = _bar.style.paddingRight = 4;
            _bar.style.paddingTop = _bar.style.paddingBottom = 4;

            _inventoryBtn = MakeButton("Túi", () => _root.OpenPanel(PlayerPanel.Inventory));
            _questBtn     = MakeButton("Nhiệm vụ", () => _root.OpenPanel(PlayerPanel.QuestJournal));
            _settingsBtn  = MakeButton("Cài đặt", () => _root.OpenPanel(PlayerPanel.Settings));
            _mapBtn       = MakeButton("Bản đồ", () => _root.OpenPanel(PlayerPanel.Map));

            _bar.Add(_inventoryBtn);
            _bar.Add(_questBtn);
            _bar.Add(_settingsBtn);
            _bar.Add(_mapBtn);

            AttachToDocument();
        }

        private void AttachToDocument()
        {
            var doc = FindFirstObjectByType<UIDocument>();
            if (doc == null) { Debug.LogError("[PlayerUIButtonBar] No UIDocument found in scene."); return; }
            doc.rootVisualElement.Add(_bar);
        }

        // ── Visibility ───────────────────────────────────────────────────────

        public void RefreshVisibility(UIConnectionState cs)
        {
            if (_bar == null) return;

            bool connected = cs == UIConnectionState.Ready
                          || cs == UIConnectionState.NeedsResync
                          || cs == UIConnectionState.UncertainMutation;

            _bar.style.display = connected ? DisplayStyle.Flex : DisplayStyle.None;

            bool canClick = cs == UIConnectionState.Ready || cs == UIConnectionState.NeedsResync;
            _inventoryBtn?.SetEnabled(canClick);
            _questBtn?.SetEnabled(canClick);
            _settingsBtn?.SetEnabled(canClick);
            _mapBtn?.SetEnabled(canClick);
        }

        // ── Helpers ──────────────────────────────────────────────────────────

        private static Button MakeButton(string label, System.Action action)
        {
            var b = new Button(action) { text = label };
            b.style.minHeight = 44; b.style.minWidth = 72; b.style.marginLeft = 2; b.style.marginRight = 2;
            return b;
        }
    }
}
