// MapPanel — hiển thị MapViewState từ MapPresenter.
// IMGUIContainer vẽ markers đơn giản. Player position, entity markers.
// Warning label nếu TopologyIsCandidate. Slider zoom (0.25-4). Nút đóng.
// Khi UncertainMutation: disable zoom slider.
// Owner: Antigravity Remote — Issue #80.

using System.Threading;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class MapPanel : MonoBehaviour
    {
        // ── Constants ────────────────────────────────────────────────────────
        private const float MapDisplaySize = 280f;

        // ── State ────────────────────────────────────────────────────────────
        private IP1UIAdapter _adapter;
        private PanelRouter _router;
        private CancellationToken _ct;
        private MapPresenter _presenter;
        private bool _visible;

        // ── UIElements refs ──────────────────────────────────────────────────
        private VisualElement _root;
        private Label _positionLabel;
        private Label _warningLabel;
        private Label _statusLabel;
        private Slider _zoomSlider;
        private IMGUIContainer _mapContainer;

        // ── Init ─────────────────────────────────────────────────────────────

        public void Initialize(IP1UIAdapter adapter, PanelRouter router, CancellationToken ct)
        {
            _adapter = adapter;
            _router = router;
            _ct = ct;
            _presenter = new MapPresenter(adapter);
            _presenter.OnChanged += Render;
            BuildUI();
            Hide();
        }

        public void Show()
        {
            _visible = true;
            _root.style.display = DisplayStyle.Flex;
            _presenter.Refresh();
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
            _root.style.left = 60; _root.style.top = 40;
            _root.style.width = MapDisplaySize + 20;

            // Header
            var header = new VisualElement { style = { flexDirection = FlexDirection.Row, justifyContent = Justify.SpaceBetween } };
            header.Add(new Label("Bản đồ") { style = { unityFontStyleAndWeight = FontStyle.Bold } });
            var closeBtn = new Button(() => _router.CloseTop()) { text = "✕" };
            closeBtn.style.minHeight = 32; closeBtn.style.minWidth = 32;
            header.Add(closeBtn);
            _root.Add(header);

            // Status / uncertain
            _statusLabel = new Label { style = { display = DisplayStyle.None, whiteSpace = WhiteSpace.Normal, marginTop = 2 } };
            _root.Add(_statusLabel);

            // Topology candidate warning
            _warningLabel = new Label("⚠ Topology chưa được xét duyệt")
            {
                style = { display = DisplayStyle.None, color = new Color(1f, 0.75f, 0.1f), whiteSpace = WhiteSpace.Normal, marginBottom = 4 }
            };
            _root.Add(_warningLabel);

            // Position label
            _positionLabel = new Label { style = { fontSize = 11, marginBottom = 4 } };
            _root.Add(_positionLabel);

            // IMGUI map canvas
            _mapContainer = new IMGUIContainer(DrawMap);
            _mapContainer.style.width = MapDisplaySize;
            _mapContainer.style.height = MapDisplaySize;
            _mapContainer.style.backgroundColor = new Color(0.05f, 0.08f, 0.10f, 1f);
            _root.Add(_mapContainer);

            // Zoom slider
            _zoomSlider = new Slider("Phóng to", 0.25f, 4f) { showInputField = true };
            _zoomSlider.SetValueWithoutNotify(1f);
            _zoomSlider.style.minHeight = 44; _zoomSlider.style.marginTop = 4;
            _zoomSlider.RegisterValueChangedCallback(ev => OnZoomChanged(ev.newValue));
            _root.Add(_zoomSlider);

            AttachToDocument();
        }

        private void AttachToDocument()
        {
            var doc = FindFirstObjectByType<UIDocument>();
            if (doc == null) { Debug.LogError("[MapPanel] No UIDocument found in scene."); return; }
            doc.rootVisualElement.Add(_root);
        }

        // ── IMGUI Draw ───────────────────────────────────────────────────────

        private void DrawMap()
        {
            var state = _presenter?.State;
            if (state == null) { GUI.Label(new Rect(10, 10, 200, 20), "Không có dữ liệu bản đồ."); return; }

            float zoom = state.ZoomLevel;
            float cx = MapDisplaySize * 0.5f;
            float cy = MapDisplaySize * 0.5f;
            float playerX = (float)state.PlayerX;
            float playerY = (float)state.PlayerY;

            // Draw markers
            foreach (var m in state.Markers)
            {
                float wx = (float)(m.X - playerX) * zoom * 4f + cx;
                float wy = -(float)(m.Y - playerY) * zoom * 4f + cy; // Y flipped for screen

                Color color;
                switch (m.Kind)
                {
                    case "PLAYER": color = new Color(0.2f, 0.9f, 0.3f); break;
                    case "NPC": color = new Color(0.3f, 0.6f, 1f); break;
                    case "QUEST": color = new Color(1f, 0.85f, 0.1f); break;
                    default: color = new Color(0.8f, 0.4f, 0.4f); break;
                }

                var prevColor = GUI.color;
                GUI.color = color;
                float dotSize = m.Kind == "PLAYER" ? 10f : 7f;
                GUI.DrawTexture(new Rect(wx - dotSize * 0.5f, wy - dotSize * 0.5f, dotSize, dotSize), Texture2D.whiteTexture);
                GUI.color = prevColor;

                if (!string.IsNullOrEmpty(m.Label))
                    GUI.Label(new Rect(wx + 6, wy - 8, 80, 16), m.Label);
            }

            // Player crosshair
            GUI.color = new Color(1f, 1f, 1f, 0.4f);
            GUI.DrawTexture(new Rect(cx - 1, cy - 8, 2, 16), Texture2D.whiteTexture);
            GUI.DrawTexture(new Rect(cx - 8, cy - 1, 16, 2), Texture2D.whiteTexture);
            GUI.color = Color.white;
        }

        // ── Render ───────────────────────────────────────────────────────────

        private void Render()
        {
            if (!_visible || _root == null) return;

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

            _zoomSlider.SetEnabled(!uncertain);

            var state = _presenter.State;
            if (state == null)
            {
                _positionLabel.text = "Vị trí: không rõ";
                _warningLabel.style.display = DisplayStyle.None;
            }
            else
            {
                _positionLabel.text = $"Vị trí: ({state.PlayerX:F1}, {state.PlayerY:F1})  Bản đồ: {state.MapId ?? "?"}";
                _warningLabel.style.display = state.TopologyIsCandidate ? DisplayStyle.Flex : DisplayStyle.None;

                // Sync slider without triggering callback
                _zoomSlider.SetValueWithoutNotify(state.ZoomLevel);
            }

            _mapContainer?.MarkDirtyRepaint();
        }

        private void OnZoomChanged(float value)
        {
            if (_adapter.HasPendingMutation || _adapter.ConnectionState == UIConnectionState.UncertainMutation) return;
            _presenter?.SetZoom(value);
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
