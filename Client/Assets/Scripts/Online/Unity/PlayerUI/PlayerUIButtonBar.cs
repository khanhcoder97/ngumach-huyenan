// PlayerUIButtonBar — thanh nút mở panel (Character, Inventory, QuestJournal, Settings, Map).
// Click gọi PlayerUIRoot.OpenPanel(PlayerPanel.X).
// Hiện/ẩn dựa trên connection state.
// Owner: Antigravity Remote — Issue #80, #85.

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
        private UIDocument _doc;
        private UIConnectionState _connectionState = UIConnectionState.Disconnected;

        // ── UIElements refs ──────────────────────────────────────────────────
        private VisualElement _bar;
        private Button _characterBtn;
        private Button _inventoryBtn;
        private Button _questBtn;
        private Button _settingsBtn;
        private Button _mapBtn;
        private VisualElement _trackerBox;
        private Label _trackerTitleLabel;
        private Label _trackerDescLabel;

        // ── Init ─────────────────────────────────────────────────────────────

        public void Initialize(IP1UIAdapter adapter, PlayerUIRoot root, UIDocument doc = null)
        {
            _adapter = adapter;
            _root = root;
            _doc = doc ?? _doc;
            // OPC-14 M0 / OPCREV-03: rebind must re-evaluate visibility from scratch
            // (cached safe-area decision must not survive a document swap).
            _hudDecisionInit = false;
            if (_bar == null) BuildUI();
            else AttachToDocument();
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

            _characterBtn = MakeButton("Nhân vật", () => _root.OpenPanel(PlayerPanel.Character));
            _inventoryBtn = MakeButton("Túi", () => _root.OpenPanel(PlayerPanel.Inventory));
            _questBtn     = MakeButton("Nhiệm vụ", () => _root.OpenPanel(PlayerPanel.QuestJournal));
            _settingsBtn  = MakeButton("Cài đặt", () => _root.OpenPanel(PlayerPanel.Settings));
            _mapBtn       = MakeButton("Bản đồ", () => _root.OpenPanel(PlayerPanel.Map));

            _bar.Add(_characterBtn);
            _bar.Add(_inventoryBtn);
            _bar.Add(_questBtn);
            _bar.Add(_settingsBtn);
            _bar.Add(_mapBtn);

            // HUD Quest Tracker
            _trackerBox = new VisualElement();
            _trackerBox.style.backgroundColor = new Color(0.05f, 0.08f, 0.10f, 0.88f);
            _trackerBox.style.borderTopWidth = _trackerBox.style.borderBottomWidth = _trackerBox.style.borderLeftWidth = _trackerBox.style.borderRightWidth = 1;
            _trackerBox.style.borderTopColor = _trackerBox.style.borderBottomColor = _trackerBox.style.borderLeftColor = _trackerBox.style.borderRightColor = new Color(0.24f, 0.36f, 0.44f);
            _trackerBox.style.paddingLeft = _trackerBox.style.paddingRight = 8;
            _trackerBox.style.paddingTop = _trackerBox.style.paddingBottom = 4;
            _trackerBox.style.marginTop = 6;
            _trackerBox.style.minWidth = 180;
            _trackerBox.style.maxWidth = 300;
            _trackerBox.style.display = DisplayStyle.None;

            _trackerTitleLabel = new Label();
            _trackerTitleLabel.style.fontSize = 11;
            _trackerTitleLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            _trackerTitleLabel.style.color = new Color(1f, 0.85f, 0.2f);
            _trackerBox.Add(_trackerTitleLabel);

            _trackerDescLabel = new Label();
            _trackerDescLabel.style.fontSize = 10;
            _trackerDescLabel.style.color = Color.white;
            _trackerDescLabel.style.whiteSpace = WhiteSpace.Normal;
            _trackerBox.Add(_trackerDescLabel);

            _trackerBox.RegisterCallback<ClickEvent>(_ => _root?.OpenPanel(PlayerPanel.QuestJournal));
            _bar.Add(_trackerBox);

            AttachToDocument();
        }

        private void AttachToDocument()
        {
            if (_doc == null || _bar == null) return;
            if (_bar.parent != _doc.rootVisualElement)
            {
                _bar.RemoveFromHierarchy();
                _doc.rootVisualElement.Add(_bar);
            }
        }

        // ── Visibility ───────────────────────────────────────────────────────


        public void SetPinnedQuest(string title, string objectiveDesc)
        {
            if (_trackerBox == null) return;
            if (string.IsNullOrEmpty(title))
            {
                _trackerBoxVisibleByQuest = DisplayStyle.None;
            }
            else
            {
                _trackerBoxVisibleByQuest = DisplayStyle.Flex;
                if (_trackerTitleLabel != null) _trackerTitleLabel.text = "★ " + title;
                if (_trackerDescLabel != null) _trackerDescLabel.text = objectiveDesc ?? "";
            }
            // OPC-14 M0 / OPCREV-03: re-apply the single visibility writer so tracker
            // transitions (pin/unpin) respect the current safe-area decision.
            ApplySafeAreaPolicy();
        }

        public void RefreshVisibility(UIConnectionState cs)
        {
            if (_bar == null) return;

            _connectionState = cs;

            bool connected = cs == UIConnectionState.Ready
                          || cs == UIConnectionState.NeedsResync
                          || cs == UIConnectionState.UncertainMutation;

            bool canClick = cs == UIConnectionState.Ready || cs == UIConnectionState.NeedsResync;
            // OPC-14 M0 / OPCREV-03: visibility is written by ApplySafeAreaPolicy only
            // (single writer) so a cached Hidden decision is not overwritten by Flex.
            ApplySafeAreaPolicy();
            _characterBtn?.SetEnabled(canClick);
            _inventoryBtn?.SetEnabled(canClick);
            _questBtn?.SetEnabled(canClick);
            _settingsBtn?.SetEnabled(canClick);
            _mapBtn?.SetEnabled(canClick);
        }

        // ── OPC-13 C — safe-area overload (compact/hide, never spill over notch) ──

        private HudDecision _lastHudDecision;
        private bool _hudDecisionInit;

        /// <summary>
        /// OPC-13 C: evaluate the pure safe-area policy and apply its controlled
        /// scale/hide tiers to this HUD. Degenerate inputs (zero-size screens in
        /// editor/tool contexts) must degrade sanely instead of hiding the only
        /// panel access on a playable viewport.
        /// </summary>
        internal void ApplySafeAreaPolicy()
        {
            if (_bar == null) return;

            var vp = new HudViewport(
                Screen.width, Screen.height,
                Screen.safeArea.xMin, Screen.safeArea.yMin,
                Screen.width - Screen.safeArea.xMax, Screen.height - Screen.safeArea.yMax);

            var decision = HudSafeAreaPolicy.Decide(vp, 5); // 5 menu controls
            bool changed = !_hudDecisionInit || !decision.Equals(_lastHudDecision);
            _lastHudDecision = decision;
            _hudDecisionInit = true;

            bool connected = _connectionState == UIConnectionState.Ready
                          || _connectionState == UIConnectionState.NeedsResync
                          || _connectionState == UIConnectionState.UncertainMutation;

            // OPC-14 M0 / OPCREV-03: single writer for display — connection AND safe-area decision.
            // Hidden stays hidden across frames (no RefreshVisibility Flex override).
            if (decision.Mode == HudMode.Hidden || !connected)
                _bar.style.display = DisplayStyle.None;
            else
                _bar.style.display = DisplayStyle.Flex;

            if (_trackerBox != null)
                _trackerBox.style.display = (decision.TrackerHidden || !connected)
                    ? DisplayStyle.None
                    : _trackerBoxVisibleByQuest;

            // Scale only re-applied on decision change (avoid per-frame churn).
            if (changed && decision.Mode != HudMode.Hidden)
            {
                float s = Math.Clamp(decision.Scale, 0.6f, 1f);
                _bar.style.scale = new Scale(new Vector2(s, s));
            }
        }

        private DisplayStyle _trackerBoxVisibleByQuest = DisplayStyle.None;

        // ── Teardown ─────────────────────────────────────────────────────────

        /// <summary>OPC-13 C: safe area/orientation can change mid-session; the policy no-ops when the decision is unchanged.</summary>
        private void Update() => ApplySafeAreaPolicy();

        public void Teardown()
        {
            if (_bar != null && _bar.parent != null)
            {
                _bar.RemoveFromHierarchy();
            }
            _adapter = null;
            _root = null;
            _doc = null;
            _connectionState = UIConnectionState.Disconnected;
            _hudDecisionInit = false;
            _lastHudDecision = default;
        }

        private void OnDestroy() => Teardown();

        // ── Helpers ──────────────────────────────────────────────────────────

        private static Button MakeButton(string label, System.Action action)
        {
            var b = new Button(action) { text = label };
            b.style.minHeight = 44; b.style.minWidth = 72; b.style.marginLeft = 2; b.style.marginRight = 2;
            return b;
        }
    }
}
