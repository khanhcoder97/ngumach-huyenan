// CharacterPanel — UI Toolkit panel displaying Character Sheet and 12 Equipment Slots.
// Rules:
//   - Authoritative vitals from P1Self; missing combat stats explicitly labeled.
//   - 12 canonical slots mapped per Character_Equipment_Inventory_Spec_vi.md.
//   - Action buttons disabled with explanation (no client-side mutation).
// Owner: Antigravity Remote — Issue #85.

using System;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class CharacterPanel : MonoBehaviour
    {
        private IP1UIAdapter _adapter;
        private PanelRouter _router;
        private CharacterPresenter _presenter;
        private UIDocument _doc;

        private VisualElement _root;
        private Label _characterNameLabel;
        private Label _classLabel;
        private Label _hpLabel;
        private Label _mpLabel;
        private Label _positionLabel;
        private Label _statsNoteLabel;
        private VisualElement _slotsGrid;
        private Label _itemDetailLabel;
        private Button _unequipBtn;

        private readonly Dictionary<string, Button> _slotButtons =
            new Dictionary<string, Button>(StringComparer.OrdinalIgnoreCase);

        private string _selectedSlot;

        public void Initialize(IP1UIAdapter adapter, PanelRouter router, CancellationToken ct, UIDocument doc = null)
        {
            if (_presenter != null) _presenter.OnChanged -= Render;
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            _router = router ?? throw new ArgumentNullException(nameof(router));
            _doc = doc ?? _doc;
            _presenter = new CharacterPresenter(_adapter);
            _presenter.OnChanged += Render;

            if (_root == null) BuildUI();
            else AttachToDocument(_doc);
            Hide();
        }

        private void BuildUI()
        {
            _root = new VisualElement();
            _root.style.position = Position.Absolute;
            _root.style.left = 120;
            _root.style.top = 40;
            _root.style.width = 620;
            _root.style.backgroundColor = new Color(0.06f, 0.08f, 0.10f, 0.95f);
            _root.style.borderTopWidth = _root.style.borderBottomWidth = _root.style.borderLeftWidth = _root.style.borderRightWidth = 2;
            _root.style.borderTopColor = _root.style.borderBottomColor = _root.style.borderLeftColor = _root.style.borderRightColor = new Color(0.24f, 0.36f, 0.44f);
            _root.style.paddingLeft = _root.style.paddingRight = _root.style.paddingTop = _root.style.paddingBottom = 12;
            _root.style.display = DisplayStyle.None;

            // Header
            var header = new VisualElement();
            header.style.flexDirection = FlexDirection.Row;
            header.style.justifyContent = Justify.SpaceBetween;
            header.style.marginBottom = 10;

            var title = new Label("NHÂN VẬT & TRANG BỊ");
            title.style.fontSize = 18;
            title.style.color = new Color(0.92f, 0.85f, 0.55f);
            title.style.unityFontStyleAndWeight = FontStyle.Bold;
            header.Add(title);

            var closeBtn = new Button(() => _router?.CloseTop()) { text = "Đóng [Esc]" };
            closeBtn.style.minWidth = 80;
            closeBtn.style.minHeight = 32;
            header.Add(closeBtn);
            _root.Add(header);

            // Vitals section
            var vitalsBox = new VisualElement();
            vitalsBox.style.backgroundColor = new Color(0.10f, 0.13f, 0.16f);
            vitalsBox.style.paddingLeft = vitalsBox.style.paddingRight = vitalsBox.style.paddingTop = vitalsBox.style.paddingBottom = 8;
            vitalsBox.style.marginBottom = 10;

            _characterNameLabel = new Label();
            _characterNameLabel.style.fontSize = 15;
            _characterNameLabel.style.color = Color.white;
            _characterNameLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            vitalsBox.Add(_characterNameLabel);

            _classLabel = new Label();
            _classLabel.style.fontSize = 13;
            _classLabel.style.color = new Color(0.7f, 0.85f, 1f);
            vitalsBox.Add(_classLabel);

            var barsRow = new VisualElement();
            barsRow.style.flexDirection = FlexDirection.Row;
            barsRow.style.marginTop = 4;

            _hpLabel = new Label();
            _hpLabel.style.color = new Color(0.95f, 0.35f, 0.35f);
            _hpLabel.style.marginRight = 16;
            barsRow.Add(_hpLabel);

            _mpLabel = new Label();
            _mpLabel.style.color = new Color(0.35f, 0.65f, 0.95f);
            barsRow.Add(_mpLabel);
            vitalsBox.Add(barsRow);

            _positionLabel = new Label();
            _positionLabel.style.fontSize = 11;
            _positionLabel.style.color = Color.gray;
            _positionLabel.style.marginTop = 2;
            vitalsBox.Add(_positionLabel);

            _root.Add(vitalsBox);

            // Middle section: Equipment Grid (left) + Detail Panel (right)
            var midSection = new VisualElement();
            midSection.style.flexDirection = FlexDirection.Row;
            midSection.style.marginBottom = 10;

            _slotsGrid = new VisualElement();
            _slotsGrid.style.width = 300;
            _slotsGrid.style.flexDirection = FlexDirection.Row;
            _slotsGrid.style.flexWrap = Wrap.Wrap;

            var slotLabels = new (string id, string name)[]
            {
                (CharacterViewState.SlotHat, "Nón"),
                (CharacterViewState.SlotChest, "Áo"),
                (CharacterViewState.SlotLegs, "Quần"),
                (CharacterViewState.SlotWeapon, "Vũ khí"),
                (CharacterViewState.SlotGloves, "Găng"),
                (CharacterViewState.SlotBoots, "Giày"),
                (CharacterViewState.SlotNeck, "Dây chuyền"),
                (CharacterViewState.SlotRingL, "Nhẫn T"),
                (CharacterViewState.SlotRingR, "Nhẫn P"),
                (CharacterViewState.SlotPendant, "Ngọc bội"),
                (CharacterViewState.SlotCloak, "Phi phong"),
                (CharacterViewState.SlotSeal, "Ấn hộ mệnh")
            };

            foreach (var slot in slotLabels)
            {
                string slotId = slot.id;
                var btn = new Button(() => SelectSlot(slotId));
                btn.text = slot.name + "\n[Trống]";
                btn.style.width = 90;
                btn.style.height = 54;
                btn.style.marginTop = btn.style.marginBottom = btn.style.marginLeft = btn.style.marginRight = 3;
                btn.style.fontSize = 11;
                btn.style.whiteSpace = WhiteSpace.Normal;
                _slotButtons[slotId] = btn;
                _slotsGrid.Add(btn);
            }
            midSection.Add(_slotsGrid);

            // Detail card
            var detailBox = new VisualElement();
            detailBox.style.flexGrow = 1;
            detailBox.style.marginLeft = 10;
            detailBox.style.backgroundColor = new Color(0.10f, 0.13f, 0.16f);
            detailBox.style.paddingLeft = detailBox.style.paddingRight = detailBox.style.paddingTop = detailBox.style.paddingBottom = 8;

            var detailTitle = new Label("Chi tiết trang bị:");
            detailTitle.style.color = new Color(0.85f, 0.85f, 0.85f);
            detailTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            detailBox.Add(detailTitle);

            _itemDetailLabel = new Label("Chọn một ô trang bị để xem chi tiết");
            _itemDetailLabel.style.fontSize = 12;
            _itemDetailLabel.style.whiteSpace = WhiteSpace.Normal;
            _itemDetailLabel.style.marginTop = 6;
            detailBox.Add(_itemDetailLabel);

            _unequipBtn = new Button();
            _unequipBtn.text = "Tháo trang bị (Chưa có endpoint server)";
            _unequipBtn.style.minHeight = 32;
            _unequipBtn.style.marginTop = 12;
            _unequipBtn.SetEnabled(false);
            detailBox.Add(_unequipBtn);

            midSection.Add(detailBox);
            _root.Add(midSection);

            // Combat Stats Note
            var noteBox = new VisualElement();
            noteBox.style.backgroundColor = new Color(0.12f, 0.10f, 0.08f);
            noteBox.style.paddingLeft = noteBox.style.paddingRight = noteBox.style.paddingTop = noteBox.style.paddingBottom = 6;
            noteBox.style.borderLeftWidth = 3;
            noteBox.style.borderLeftColor = new Color(0.85f, 0.65f, 0.25f);

            _statsNoteLabel = new Label("Chỉ số chiến đấu (Công/Giáp/Chí mạng): " + CharacterViewState.MissingStatReason);
            _statsNoteLabel.style.fontSize = 11;
            _statsNoteLabel.style.color = new Color(0.85f, 0.75f, 0.55f);
            _statsNoteLabel.style.whiteSpace = WhiteSpace.Normal;
            noteBox.Add(_statsNoteLabel);
            _root.Add(noteBox);

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

        public void Show()
        {
            if (_root == null) return;
            _root.style.display = DisplayStyle.Flex;
            _presenter?.Refresh();
        }

        public void Hide()
        {
            if (_root == null) return;
            _root.style.display = DisplayStyle.None;
            _selectedSlot = null;
        }

        private void SelectSlot(string slotId)
        {
            _selectedSlot = slotId;
            Render();
        }

        private void Render()
        {
            if (_presenter == null || !_presenter.State.IsLoaded || _presenter.State.Value == null)
            {
                if (_characterNameLabel != null) _characterNameLabel.text = "Đang tải dữ liệu nhân vật...";
                return;
            }

            var view = _presenter.State.Value;
            _characterNameLabel.text = "Nhân vật: " + (string.IsNullOrEmpty(view.CharacterId) ? "(Chưa rõ)" : view.CharacterId);
            _classLabel.text = "Môn phái: " + (string.IsNullOrEmpty(view.ClassId) ? "(Chưa rõ)" : view.ClassId);
            _hpLabel.text = $"HP: {view.Hp} / {view.MaxHp}";
            _mpLabel.text = $"MP: {view.Mp} / {view.MaxMp}";
            _positionLabel.text = $"Vị trí: ({view.X:F1}, {view.Y:F1})";

            // Update slots
            foreach (var kvp in _slotButtons)
            {
                string slotId = kvp.Key;
                var btn = kvp.Value;
                var item = view.GetEquippedItem(slotId);
                string slotName = GetSlotShortName(slotId);

                if (item != null)
                {
                    btn.text = $"{slotName}\n{item.DisplayName}";
                    btn.style.backgroundColor = new Color(0.16f, 0.24f, 0.32f);
                }
                else
                {
                    btn.text = $"{slotName}\n[Trống]";
                    btn.style.backgroundColor = new Color(0.12f, 0.15f, 0.18f);
                }

                if (string.Equals(_selectedSlot, slotId, StringComparison.OrdinalIgnoreCase))
                {
                    btn.style.borderTopWidth = btn.style.borderBottomWidth = btn.style.borderLeftWidth = btn.style.borderRightWidth = 2;
                    btn.style.borderTopColor = btn.style.borderBottomColor = btn.style.borderLeftColor = btn.style.borderRightColor = Color.yellow;
                }
                else
                {
                    btn.style.borderTopWidth = btn.style.borderBottomWidth = btn.style.borderLeftWidth = btn.style.borderRightWidth = 1;
                    btn.style.borderTopColor = btn.style.borderBottomColor = btn.style.borderLeftColor = btn.style.borderRightColor = new Color(0.3f, 0.35f, 0.4f);
                }
            }

            // Update item detail
            if (!string.IsNullOrEmpty(_selectedSlot))
            {
                var selectedItem = view.GetEquippedItem(_selectedSlot);
                if (selectedItem != null)
                {
                    var meta = ItemMetadataResolver.Resolve(selectedItem.TemplateId);
                    _itemDetailLabel.text =
                        $"Tên: {selectedItem.DisplayName}\n" +
                        $"Phẩm chất: {meta.Rarity}\n" +
                        $"Loại: {meta.Category}\n" +
                        $"Cấp yêu cầu: {meta.RequiredLevel}\n" +
                        $"Độ bền: {selectedItem.Durability}/100\n" +
                        $"Phiên bản: v{selectedItem.Version}\n" +
                        $"Mô tả: {meta.Description}";
                    _unequipBtn.SetEnabled(false);
                }
                else
                {
                    _itemDetailLabel.text = $"Ô {GetSlotShortName(_selectedSlot)}: Hiện đang trống.";
                    _unequipBtn.SetEnabled(false);
                }
            }
            else
            {
                _itemDetailLabel.text = "Chọn một ô trang bị để xem chi tiết";
                _unequipBtn.SetEnabled(false);
            }
        }

        private static string GetSlotShortName(string slotId)
        {
            switch (slotId)
            {
                case CharacterViewState.SlotHat: return "Nón";
                case CharacterViewState.SlotChest: return "Áo";
                case CharacterViewState.SlotLegs: return "Quần";
                case CharacterViewState.SlotWeapon: return "Vũ khí";
                case CharacterViewState.SlotGloves: return "Găng";
                case CharacterViewState.SlotBoots: return "Giày";
                case CharacterViewState.SlotNeck: return "Dây chuyền";
                case CharacterViewState.SlotRingL: return "Nhẫn T";
                case CharacterViewState.SlotRingR: return "Nhẫn P";
                case CharacterViewState.SlotPendant: return "Ngọc bội";
                case CharacterViewState.SlotCloak: return "Phi phong";
                case CharacterViewState.SlotSeal: return "Ấn hộ mệnh";
                default: return slotId;
            }
        }

        public void Teardown()
        {
            Hide();
            if (_presenter != null)
            {
                _presenter.OnChanged -= Render;
                _presenter.Clear();
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
    }
}
