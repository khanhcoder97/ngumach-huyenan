// MapPanel — hiển thị MapViewState từ MapPresenter.
// IMGUIContainer vẽ markers đơn giản. Player position, entity markers.
// Warning label nếu TopologyIsCandidate. Slider zoom (0.25-4). Nút đóng.
// OPC-13 C: drag-to-pan cửa sổ nhìn (clamp theo map_bounds.json), nút về vị trí
// người chơi; camera rectangle/waypoint ghi UNSUPPORTED (chưa có authority contract).
// Khi UncertainMutation: disable zoom slider (pan vẫn là gesture view thuần).
// Owner: Antigravity Remote — Issue #80; Package C OPC-13 — Issue #85.

using System;
using System.Threading;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class MapPanel : MonoBehaviour, IUiAccessibilityConsumer
    {
        // ── Constants ────────────────────────────────────────────────────────
        private const float MapDisplaySize = 280f;

        // ── State ────────────────────────────────────────────────────────────
        private IP1UIAdapter _adapter;
        private PanelRouter _router;
        private CancellationToken _ct;
        private MapPresenter _presenter;
        private bool _visible;
        private UIDocument _doc;

        // ── UIElements refs ──────────────────────────────────────────────────
        private VisualElement _root;
        private Label _positionLabel;
        private Label _warningLabel;
        private Label _statusLabel;
        private Label _unsupportedLabel;
        private Slider _zoomSlider;
        private IMGUIContainer _mapContainer;

        // OPC-13 C: drag-to-pan gesture state (pure local view, no authority).
        private bool _panning;
        private float _lastPanPointerX, _lastPanPointerY;

        // ── Init ─────────────────────────────────────────────────────────────

        public void Initialize(IP1UIAdapter adapter, PanelRouter router, CancellationToken ct, UIDocument doc = null)
        {
            if (_presenter != null) _presenter.OnChanged -= Render;
            _adapter = adapter;
            _router = router;
            _ct = ct;
            _doc = doc ?? _doc;
            _presenter = new MapPresenter(adapter);
            _presenter.OnChanged += Render;
            if (_root == null) BuildUI();
            else AttachToDocument(_doc);
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

            // IMGUI map canvas — drag-to-pan (OPC-13 C)
            _mapContainer = new IMGUIContainer(DrawMap);
            _mapContainer.style.width = MapDisplaySize;
            _mapContainer.style.height = MapDisplaySize;
            _mapContainer.style.backgroundColor = new Color(0.05f, 0.08f, 0.10f, 1f);
            _mapContainer.RegisterCallback<PointerDownEvent>(OnMapPointerDown);
            _mapContainer.RegisterCallback<PointerMoveEvent>(OnMapPointerMove);
            _mapContainer.RegisterCallback<PointerUpEvent>(OnMapPointerUp);
            _mapContainer.RegisterCallback<PointerLeaveEvent>(OnMapPointerLeave);
            _root.Add(_mapContainer);

            // Zoom slider
            _zoomSlider = new Slider("Phóng to", 0.25f, 4f) { showInputField = true };
            _zoomSlider.SetValueWithoutNotify(1f);
            _zoomSlider.style.minHeight = 44; _zoomSlider.style.marginTop = 4;
            _zoomSlider.RegisterValueChangedCallback(ev => OnZoomChanged(ev.newValue));
            _root.Add(_zoomSlider);

            // OPC-13 C: re-center helper — drops the pan offset (zoom preserved).
            var centerBtn = new Button(() => _presenter?.CenterOnPlayer()) { text = "Về vị trí của bạn" };
            centerBtn.style.minHeight = 36; centerBtn.style.marginTop = 2;
            _root.Add(centerBtn);

            // OPC-13 C: camera gameplay rectangle / waypoint UI is UNSUPPORTED — no
            // server authority contract exists (no approved camera fields, no waypoint
            // endpoints). The panel states this instead of inventing coordinates.
            _unsupportedLabel = new Label("Ô quay gameplay / waypoint: UNSUPPORTED — chưa có authority contract (hiển thị read-only)")
            {
                style = { whiteSpace = WhiteSpace.Normal, fontSize = 10, opacity = 0.75f, marginTop = 2 }
            };
            _root.Add(_unsupportedLabel);

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

        // ── IMGUI Draw ───────────────────────────────────────────────────────

        private void DrawMap()
        {
            var state = _presenter?.State;
            if (state == null) { GUI.Label(new Rect(10, 10, 200, 20), "Không có dữ liệu bản đồ."); return; }

            float zoom = state.ZoomLevel;
            float cx = MapDisplaySize * 0.5f;
            float cy = MapDisplaySize * 0.5f;
            float centerX = (float)state.ViewCenterX; // player + UI-only pan (clamped)
            float centerY = (float)state.ViewCenterY;
            float playerX = (float)state.PlayerX;
            float playerY = (float)state.PlayerY;

            var bounds = state.Bounds ?? MapBounds.ForMap(state.MapId);
            // Projection scale derived from canonical map bounds (map_bounds.json), replacing arbitrary 4px/WU
            float baseScale = (float)(MapDisplaySize / Math.Max(1.0, bounds.Width));
            float scale = baseScale * zoom;

            // Draw markers relative to the pan-clamped view center
            foreach (var m in state.Markers)
            {
                float wx = (float)(m.X - centerX) * scale + cx;
                float wy = -(float)(m.Y - centerY) * scale + cy; // Y flipped for screen

                // Bounds clipping within map display container
                if (wx < 0 || wx > MapDisplaySize || wy < 0 || wy > MapDisplaySize) continue;

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

            // Player crosshair at the player's projected position (may leave center when panning)
            float px = (playerX - centerX) * scale + cx;
            float py = -(playerY - centerY) * scale + cy;
            GUI.color = new Color(1f, 1f, 1f, 0.4f);
            GUI.DrawTexture(new Rect(px - 1, py - 8, 2, 16), Texture2D.whiteTexture);
            GUI.DrawTexture(new Rect(px - 8, py - 1, 16, 2), Texture2D.whiteTexture);
            GUI.color = Color.white;
        }

        // ── Pan gesture handlers (OPC-13 C, UI-only) ─────────────────────────

        private void OnMapPointerDown(PointerDownEvent e)
        {
            // Pan is a pure local view gesture: no wire command, so it also stays
            // available while a mutation is pending (same stance as pin/unpin).
            if (e.button != 0 || _presenter?.State == null) return;
            _panning = true;
            _lastPanPointerX = e.position.x;
            _lastPanPointerY = e.position.y;
        }

        private void OnMapPointerMove(PointerMoveEvent e)
        {
            if (!_panning) return;
            float dx = e.position.x - _lastPanPointerX;
            float dy = e.position.y - _lastPanPointerY;
            _lastPanPointerX = e.position.x;
            _lastPanPointerY = e.position.y;

            var state = _presenter?.State;
            if (state == null) return;
            // px → world: scale = (MapDisplaySize / bounds.Width) * zoom.
            var bounds = state.Bounds ?? MapBounds.ForMap(state.MapId);
            float scale = (float)((MapDisplaySize / Math.Max(1.0, bounds.Width)) * state.ZoomLevel);
            if (scale <= 0f) return;
            // Drag right pulls the map right → view center moves −X; drag down moves +Y (Y flipped).
            _presenter.PanBy(-dx / scale, dy / scale);
        }

        private void OnMapPointerUp(PointerUpEvent e) => _panning = false;
        private void OnMapPointerLeave(PointerLeaveEvent e) => _panning = false;

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

        private void Update()
        {
            if (_visible && _presenter != null)
            {
                _presenter.Refresh();
            }
        }

        public void ApplyAccessibility(SettingsViewState s)
        {
            // OPC-14 O1: hook for reduced motion / text scale; map view keeps its own
            // logical render/PPU/zoom. Stored for future consumer wiring.
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

        private static VisualElement MakePanel()
        {
            var p = new VisualElement();
            p.style.backgroundColor = new Color(0.07f, 0.10f, 0.12f, 0.92f);
            p.style.paddingLeft = p.style.paddingRight = p.style.paddingTop = p.style.paddingBottom = 8;
            return p;
        }
    }
}
