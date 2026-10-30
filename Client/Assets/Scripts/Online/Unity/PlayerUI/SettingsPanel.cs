// SettingsPanel — hiển thị SettingsViewState từ SettingsPresenter.
// Slider: UiScale (0.5-2.0), MasterVolume (0-1), TextSize (0.75-1.5).
// Toggle: ReducedMotion, ReducedFlash, ShowInputHints.
// Nút Reset Default. Áp dụng chỉ qua SettingsPresenter setter.
// Owner: Antigravity Remote — Issue #80.

using System.Threading;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class SettingsPanel : MonoBehaviour
    {
        // ── Inspector ────────────────────────────────────────────────────────
        [SerializeField] private bool usePlayerPrefsStore = true;

        // ── State ────────────────────────────────────────────────────────────
        private IP1UIAdapter _adapter;
        private PanelRouter _router;
        private CancellationToken _ct;
        private SettingsPresenter _presenter;
        private bool _visible;
        private bool _suppressCallbacks;

        // ── UIElements refs ──────────────────────────────────────────────────
        private VisualElement _root;
        private Slider _uiScaleSlider;
        private Slider _masterVolumeSlider;
        private Slider _textSizeSlider;
        private Toggle _reducedMotionToggle;
        private Toggle _reducedFlashToggle;
        private Toggle _showInputHintsToggle;
        private Label _statusLabel;

        // ── Init ─────────────────────────────────────────────────────────────

        public void Initialize(IP1UIAdapter adapter, PanelRouter router, CancellationToken ct)
        {
            _adapter = adapter;
            _router = router;
            _ct = ct;

            ISettingsStore store = usePlayerPrefsStore
                ? (ISettingsStore)FindFirstObjectByType<PlayerPrefsSettingsStore>()
                : null;
            if (store == null)
            {
                // Fallback: use PlayerPrefsSettingsStore if available, else log error and skip.
                var storeGo = FindFirstObjectByType<PlayerPrefsSettingsStore>();
                if (storeGo != null) store = storeGo;
                else { Debug.LogError("[SettingsPanel] No ISettingsStore found. Attach PlayerPrefsSettingsStore to scene."); return; }
            }

            _presenter = new SettingsPresenter(store);
            _presenter.OnChanged += Render;
            BuildUI();
            Hide();
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
            _root.style.left = 60; _root.style.top = 60;
            _root.style.width = 340;

            // Header
            var header = new VisualElement { style = { flexDirection = FlexDirection.Row, justifyContent = Justify.SpaceBetween } };
            header.Add(new Label("Cài đặt") { style = { unityFontStyleAndWeight = FontStyle.Bold } });
            var closeBtn = new Button(() => _router.CloseTop()) { text = "✕" };
            closeBtn.style.minHeight = 32; closeBtn.style.minWidth = 32;
            header.Add(closeBtn);
            _root.Add(header);

            _statusLabel = new Label { style = { display = DisplayStyle.None, whiteSpace = WhiteSpace.Normal, marginTop = 4 } };
            _root.Add(_statusLabel);

            var scroll = new ScrollView();

            // Sliders
            _uiScaleSlider = MakeSlider("Tỷ lệ giao diện", 0.5f, 2.0f);
            _uiScaleSlider.RegisterValueChangedCallback(ev => { if (!_suppressCallbacks) _presenter?.SetUiScale(ev.newValue); });
            scroll.Add(_uiScaleSlider);

            _masterVolumeSlider = MakeSlider("Âm lượng chính", 0f, 1f);
            _masterVolumeSlider.RegisterValueChangedCallback(ev => { if (!_suppressCallbacks) _presenter?.SetMasterVolume(ev.newValue); });
            scroll.Add(_masterVolumeSlider);

            _textSizeSlider = MakeSlider("Cỡ chữ", 0.75f, 1.5f);
            _textSizeSlider.RegisterValueChangedCallback(ev => { if (!_suppressCallbacks) _presenter?.SetTextSize(ev.newValue); });
            scroll.Add(_textSizeSlider);

            // Toggles
            _reducedMotionToggle = MakeToggle("Giảm chuyển động");
            _reducedMotionToggle.RegisterValueChangedCallback(ev => { if (!_suppressCallbacks) _presenter?.SetReducedMotion(ev.newValue); });
            scroll.Add(_reducedMotionToggle);

            _reducedFlashToggle = MakeToggle("Giảm hiệu ứng nhấp nháy");
            _reducedFlashToggle.RegisterValueChangedCallback(ev => { if (!_suppressCallbacks) _presenter?.SetReducedFlash(ev.newValue); });
            scroll.Add(_reducedFlashToggle);

            _showInputHintsToggle = MakeToggle("Hiển thị gợi ý phím");
            _showInputHintsToggle.RegisterValueChangedCallback(ev => { if (!_suppressCallbacks) _presenter?.SetInputHints(ev.newValue); });
            scroll.Add(_showInputHintsToggle);

            // Reset button
            var resetBtn = new Button(() => _presenter?.Reset()) { text = "Khôi phục mặc định" };
            resetBtn.style.minHeight = 42; resetBtn.style.marginTop = 8;
            scroll.Add(resetBtn);

            _root.Add(scroll);
            AttachToDocument();
        }

        private void AttachToDocument()
        {
            var doc = FindFirstObjectByType<UIDocument>();
            if (doc == null) { Debug.LogError("[SettingsPanel] No UIDocument found in scene."); return; }
            doc.rootVisualElement.Add(_root);
        }

        // ── Render ───────────────────────────────────────────────────────────

        private void Render()
        {
            if (!_visible || _root == null || _presenter == null) return;

            var cs = _adapter.ConnectionState;
            if (cs == UIConnectionState.Expired || cs == UIConnectionState.Disconnected)
            { Hide(); return; }

            bool uncertain = cs == UIConnectionState.UncertainMutation || _adapter.HasPendingMutation;

            if (uncertain)
            {
                _statusLabel.text = "Đang xử lý...";
                _statusLabel.style.display = DisplayStyle.Flex;
            }
            else
            {
                _statusLabel.style.display = DisplayStyle.None;
            }

            var s = _presenter.Current;

            // Suppress callbacks while programmatically setting values
            _suppressCallbacks = true;
            _uiScaleSlider.SetValueWithoutNotify(s.UiScale);
            _masterVolumeSlider.SetValueWithoutNotify(s.MasterVolume);
            _textSizeSlider.SetValueWithoutNotify(s.TextSize);
            _reducedMotionToggle.SetValueWithoutNotify(s.ReducedMotion);
            _reducedFlashToggle.SetValueWithoutNotify(s.ReducedFlash);
            _showInputHintsToggle.SetValueWithoutNotify(s.ShowInputHints);
            _suppressCallbacks = false;

            // Disable controls during uncertain mutation
            _uiScaleSlider.SetEnabled(!uncertain);
            _masterVolumeSlider.SetEnabled(!uncertain);
            _textSizeSlider.SetEnabled(!uncertain);
            _reducedMotionToggle.SetEnabled(!uncertain);
            _reducedFlashToggle.SetEnabled(!uncertain);
            _showInputHintsToggle.SetEnabled(!uncertain);
        }

        private void OnDestroy()
        {
            if (_presenter != null) _presenter.OnChanged -= Render;
        }

        // ── Helpers ──────────────────────────────────────────────────────────

        private static Slider MakeSlider(string label, float low, float high)
        {
            var s = new Slider(label, low, high) { showInputField = true };
            s.style.minHeight = 44; s.style.marginTop = 4;
            return s;
        }

        private static Toggle MakeToggle(string label)
        {
            var t = new Toggle(label);
            t.style.minHeight = 40; t.style.marginTop = 4;
            return t;
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
