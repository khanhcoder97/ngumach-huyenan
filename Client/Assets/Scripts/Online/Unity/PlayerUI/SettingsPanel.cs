// SettingsPanel — MonoBehaviour điều khiển panel Cài đặt.
// Tỷ lệ giao diện, âm lượng chính, cỡ chữ, reduced motion, reduced flash, input hints.
// Phù hợp DEC-019 (Settings: versioned local PlayerPrefs).
// Owner: Antigravity Remote — Issue #80.

using System;
using System.Threading;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class SettingsPanel : MonoBehaviour
    {
        [SerializeField] private bool usePlayerPrefsStore = true;

        private IP1UIAdapter _adapter;
        private PanelRouter _router;
        private CancellationToken _ct;
        private SettingsPresenter _presenter;

        private VisualElement _root;
        private bool _visible;
        private bool _suppressCallbacks;
        private UIDocument _doc;

        private Slider _uiScaleSlider;
        private Slider _masterVolumeSlider;
        private Slider _textSizeSlider;
        private Toggle _reducedMotionToggle;
        private Toggle _reducedFlashToggle;
        private Toggle _showInputHintsToggle;
        private Label _statusLabel;

        // ── Init ─────────────────────────────────────────────────────────────

        public void Initialize(IP1UIAdapter adapter, PanelRouter router, CancellationToken ct, ISettingsStore store = null, UIDocument doc = null)
        {
            if (_presenter != null) _presenter.OnChanged -= Render;
            _adapter = adapter;
            _router = router;
            _ct = ct;
            _doc = doc ?? _doc;

            if (store == null && usePlayerPrefsStore)
            {
                store = GetComponent<PlayerPrefsSettingsStore>() ?? GetComponentInParent<PlayerPrefsSettingsStore>();
                if (store == null)
                {
                    var go = new GameObject("PlayerPrefsSettingsStore");
                    go.transform.SetParent(transform, false);
                    store = go.AddComponent<PlayerPrefsSettingsStore>();
                }
            }

            _presenter = new SettingsPresenter(store ?? new MemorySettingsStore());
            _presenter.OnChanged += Render;
            if (_root == null) BuildUI();
            else AttachToDocument(_doc);
            ApplySettings(_presenter.Current);
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
            _root.style.left = 80; _root.style.top = 40;
            _root.style.width = 380; _root.style.maxHeight = 440;

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
            _uiScaleSlider.RegisterValueChangedCallback(ev =>
            {
                if (!_suppressCallbacks)
                {
                    _presenter?.SetUiScale(ev.newValue);
                    ApplySettings(_presenter?.Current);
                }
            });
            scroll.Add(_uiScaleSlider);

            _masterVolumeSlider = MakeSlider("Âm lượng chính", 0f, 1f);
            _masterVolumeSlider.RegisterValueChangedCallback(ev =>
            {
                if (!_suppressCallbacks)
                {
                    _presenter?.SetMasterVolume(ev.newValue);
                    ApplySettings(_presenter?.Current);
                }
            });
            scroll.Add(_masterVolumeSlider);

            _textSizeSlider = MakeSlider("Cỡ chữ", 0.75f, 1.5f);
            _textSizeSlider.RegisterValueChangedCallback(ev =>
            {
                if (!_suppressCallbacks)
                {
                    _presenter?.SetTextSize(ev.newValue);
                    ApplySettings(_presenter?.Current);
                }
            });
            scroll.Add(_textSizeSlider);

            // Toggles
            _reducedMotionToggle = MakeToggle("Giảm chuyển động (Lưu cục bộ - preview)");
            _reducedMotionToggle.RegisterValueChangedCallback(ev => { if (!_suppressCallbacks) _presenter?.SetReducedMotion(ev.newValue); });
            scroll.Add(_reducedMotionToggle);

            _reducedFlashToggle = MakeToggle("Giảm hiệu ứng nhấp nháy (Lưu cục bộ - preview)");
            _reducedFlashToggle.RegisterValueChangedCallback(ev => { if (!_suppressCallbacks) _presenter?.SetReducedFlash(ev.newValue); });
            scroll.Add(_reducedFlashToggle);

            _showInputHintsToggle = MakeToggle("Hiển thị gợi ý phím");
            _showInputHintsToggle.RegisterValueChangedCallback(ev => { if (!_suppressCallbacks) _presenter?.SetInputHints(ev.newValue); });
            scroll.Add(_showInputHintsToggle);

            // Reset button
            var resetBtn = new Button(() => { _presenter?.Reset(); ApplySettings(_presenter?.Current); }) { text = "Khôi phục mặc định" };
            resetBtn.style.minHeight = 42; resetBtn.style.marginTop = 8;
            scroll.Add(resetBtn);

            _root.Add(scroll);
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
            if (!_visible || _presenter == null) return;

            var cs = _adapter.ConnectionState;
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

            ApplySettings(s);
        }

        private void ApplySettings(SettingsViewState s)
        {
            if (s == null) return;
            // Apply volume via Unity AudioListener
            AudioListener.volume = s.MasterVolume;
            // Apply UI scale to root visual element (scales entire UI per WO-14)
            if (_doc != null && _doc.rootVisualElement != null)
            {
                _doc.rootVisualElement.transform.scale = new Vector3(s.UiScale, s.UiScale, 1f);
            }
            else if (_root != null)
            {
                _root.transform.scale = new Vector3(s.UiScale, s.UiScale, 1f);
            }
        }

        public void Teardown()
        {
            Hide();
            if (_presenter != null)
            {
                _presenter.OnChanged -= Render;
                _presenter = null;
            }
            if (_root != null && _root.parent != null)
            {
                _root.RemoveFromHierarchy();
            }
            _adapter = null;
            _router = null;
            _doc = null;
        }

        private void OnDestroy() => Teardown();

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

        private sealed class MemorySettingsStore : ISettingsStore
        {
            private SettingsViewState _state = SettingsViewState.Default;
            public SettingsViewState Load() => _state;
            public void Save(SettingsViewState s) => _state = s;
        }
    }
}
