// InventoryPanel — MonoBehaviour điều khiển panel Túi đồ (100 ô / 4 trang, DEC-023).
// Pure UI Toolkit (UIDocument). Không dùng UGUI.
// Tách biệt hoàn toàn logic (InventoryPresenter) và presentation.
// Owner: Antigravity Remote — Issue #80.

using System;
using System.Threading;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class InventoryPanel : MonoBehaviour
    {
        private IP1UIAdapter _adapter;
        private PanelRouter _router;
        private CancellationToken _ct;
        private InventoryPresenter _presenter;

        private VisualElement _root;
        private VisualElement _grid;
        private Label _statusLabel;
        private Label _detailLabel;
        private readonly Button[] _tabButtons = new Button[InventoryViewState.PagesCount];
        private readonly VisualElement[] _slots = new VisualElement[InventoryViewState.SlotsPerPage];
        private bool _visible;

        // ── Init ─────────────────────────────────────────────────────────────

        public void Initialize(IP1UIAdapter adapter, PanelRouter router, CancellationToken ct)
        {
            _adapter = adapter;
            _router = router;
            _ct = ct;
            _presenter = new InventoryPresenter(adapter);
            _presenter.OnChanged += Render;
            BuildUI();
            Hide();
        }

        public void Show()
        {
            _visible = true;
            _root.style.display = DisplayStyle.Flex;
            _ = _presenter.LoadAsync(_ct);
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
            _root.style.left = 40; _root.style.top = 40;
            _root.style.width = 320; _root.style.minHeight = 400;

            // Header
            var header = new VisualElement { style = { flexDirection = FlexDirection.Row, justifyContent = Justify.SpaceBetween } };
            header.Add(new Label("Túi đồ (100 ô)") { style = { unityFontStyleAndWeight = FontStyle.Bold } });
            var closeBtn = new Button(() => _router.CloseTop()) { text = "✕" };
            closeBtn.style.minHeight = 32; closeBtn.style.minWidth = 32;
            header.Add(closeBtn);
            _root.Add(header);

            // Tabs
            var tabBar = new VisualElement { style = { flexDirection = FlexDirection.Row, marginTop = 4 } };
            for (int i = 0; i < InventoryViewState.PagesCount; i++)
            {
                int page = i;
                var tab = new Button(() => OnTabClicked(page)) { text = (i + 1).ToString() };
                tab.style.minHeight = 36; tab.style.flexGrow = 1;
                _tabButtons[i] = tab;
                tabBar.Add(tab);
            }
            _root.Add(tabBar);

            // Status label (loading / error / uncertain)
            _statusLabel = new Label { style = { display = DisplayStyle.None, whiteSpace = WhiteSpace.Normal, marginTop = 4 } };
            _root.Add(_statusLabel);

            // 5×5 grid
            _grid = new VisualElement { style = { flexDirection = FlexDirection.Row, flexWrap = Wrap.Wrap, marginTop = 4 } };
            for (int i = 0; i < InventoryViewState.SlotsPerPage; i++)
            {
                int cellIndex = i;
                var cell = new VisualElement();
                cell.style.width = 56; cell.style.height = 56;
                cell.style.borderTopWidth = cell.style.borderRightWidth = cell.style.borderBottomWidth = cell.style.borderLeftWidth = 1;
                cell.style.borderTopColor = cell.style.borderRightColor = cell.style.borderBottomColor = cell.style.borderLeftColor = new Color(0.3f, 0.3f, 0.3f);
                cell.style.marginTop = cell.style.marginBottom = cell.style.marginLeft = cell.style.marginRight = 1;
                cell.style.justifyContent = Justify.Center;
                cell.style.alignItems = Align.Center;
                cell.Add(new Label("") { style = { whiteSpace = WhiteSpace.Normal, fontSize = 10 } });
                cell.RegisterCallback<ClickEvent>(_ => OnCellClicked(cellIndex));
                _slots[i] = cell;
                _grid.Add(cell);
            }
            _root.Add(_grid);

            // Detail / selection label
            _detailLabel = new Label { style = { whiteSpace = WhiteSpace.Normal, marginTop = 6, minHeight = 30, fontSize = 11, opacity = 0.9f } };
            _root.Add(_detailLabel);

            // Attach to scene's UIDocument if available
            AttachToDocument();
        }

        private void AttachToDocument()
        {
            var doc = FindFirstObjectByType<UIDocument>();
            if (doc == null) { Debug.LogError("[InventoryPanel] No UIDocument found in scene."); return; }
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
            if (state.IsLoading)
            {
                _statusLabel.text = "Đang tải dữ liệu...";
                _statusLabel.style.display = DisplayStyle.Flex;
            }
            else if (state.IsError)
            {
                _statusLabel.text = "Lỗi: " + state.ErrorCode;
                _statusLabel.style.display = DisplayStyle.Flex;
            }
            else if (uncertain)
            {
                _statusLabel.text = "Đang đồng bộ thay đổi...";
                _statusLabel.style.display = DisplayStyle.Flex;
            }
            else
            {
                _statusLabel.style.display = DisplayStyle.None;
            }

            // Tab highlight
            int activePage = state.Value?.ActivePage ?? 0;
            for (int t = 0; t < InventoryViewState.PagesCount; t++)
            {
                if (_tabButtons[t] == null) continue;
                _tabButtons[t].SetEnabled(!uncertain);
                _tabButtons[t].style.backgroundColor = (t == activePage)
                    ? new Color(0.2f, 0.5f, 0.8f, 1f)
                    : new Color(0.15f, 0.15f, 0.15f, 1f);
            }

            // Slots
            string selectedId = state.Value?.SelectedInstanceId;
            ItemSlotView selectedItem = null;

            if (state.Value != null)
            {
                foreach (var (localIndex, item) in state.Value.PageSlots())
                {
                    var cell = _slots[localIndex];
                    if (cell == null) continue;
                    var lbl = cell.Q<Label>();
                    if (lbl == null) continue;

                    bool isSelected = item != null && !string.IsNullOrEmpty(selectedId) && item.InstanceId == selectedId;
                    if (isSelected) selectedItem = item;

                    if (item != null)
                    {
                        lbl.text = item.DisplayName + (item.Stack > 1 ? "\n×" + item.Stack : "");
                        cell.style.backgroundColor = isSelected
                            ? new Color(0.25f, 0.35f, 0.50f, 1f)
                            : new Color(0.18f, 0.22f, 0.28f, 1f);
                        cell.style.borderTopColor = cell.style.borderRightColor = cell.style.borderBottomColor = cell.style.borderLeftColor = isSelected
                            ? new Color(0.95f, 0.75f, 0.20f, 1f)
                            : new Color(0.3f, 0.3f, 0.3f);
                    }
                    else
                    {
                        lbl.text = "";
                        cell.style.backgroundColor = new Color(0.08f, 0.08f, 0.08f, 0.5f);
                        cell.style.borderTopColor = cell.style.borderRightColor = cell.style.borderBottomColor = cell.style.borderLeftColor = new Color(0.2f, 0.2f, 0.2f);
                    }
                }
            }

            if (selectedItem != null)
            {
                _detailLabel.text = "Đã chọn: " + selectedItem.DisplayName + " (Số lượng: " + selectedItem.Stack + ")";
            }
            else
            {
                _detailLabel.text = "";
            }
        }

        // ── Callbacks ────────────────────────────────────────────────────────

        private void OnTabClicked(int page)
        {
            if (_adapter.HasPendingMutation || _adapter.ConnectionState == UIConnectionState.UncertainMutation) return;
            _presenter.SetPage(page);
        }

        private void OnCellClicked(int localIndex)
        {
            var state = _presenter.State;
            if (state.Value == null) return;
            int globalIndex = state.Value.ActivePage * InventoryViewState.SlotsPerPage + localIndex;
            if (state.Value.Slots.TryGetValue(globalIndex, out var item) && item != null)
            {
                _presenter.SetSelection(item.InstanceId);
            }
            else
            {
                _presenter.SetSelection(null);
            }
        }

        private void OnDestroy()
        {
            if (_presenter != null) _presenter.OnChanged -= Render;
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
