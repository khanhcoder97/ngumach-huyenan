# Antigravity Player UI — Handoff Document (vi)

**Epic**: AG-01 Player UI  
**Issue**: https://github.com/khanhcoder97/ngumach-huyenan/issues/80  
**Branch**: `antigravity/ag-01-player-ui-20261030`  
**Agent**: Antigravity Remote  
**Date**: 2026-10-30, Asia/Tokyo

---

## 1. Kiến trúc tổng quan

```
P1Client (Core) ←── IP1UIAdapter ──→ Presenters (pure C#9)
                                           ↓
                                    Unity MonoBehaviours (PlayerUI/)
                                           ↓
                                    UIDocument (UI Toolkit)
```

**Tầng Presentation** (`Client/Assets/Scripts/Online/Presentation/`): pure C#9, không phụ thuộc Unity. Có thể test bằng `dotnet test` từ clone sạch.

**Tầng Unity** (`Client/Assets/Scripts/Online/Unity/PlayerUI/`): MonoBehaviour và UIElement panels. Phụ thuộc UnityEngine + UIElements.

---

## 2. Danh sách file

### Presentation layer (pure C#9)

| File | Mô tả |
|---|---|
| `P1UIState.cs` | Tất cả immutable view state types, `AsyncState<T>`, enums |
| `IP1UIAdapter.cs` | Interface bọc P1Client cho UI |
| `P1ClientAdapter.cs` | Concrete adapter |
| `PanelRouter.cs` | Modal stack, focus return |
| `InventoryPresenter.cs` | AG2: 100 ô túi, 4 trang |
| `QuestJournalPresenter.cs` | AG3: nhóm active/completed |
| `NpcDialoguePresenter.cs` | AG3: interact/accept/turnin |
| `SettingsPresenter.cs` | AG4: preferences local |
| `MapPresenter.cs` | AG5: map view state |

### Unity layer (`Unity/PlayerUI/`)

| File | Mô tả |
|---|---|
| `PlayerUIRoot.cs` | Root MonoBehaviour, khởi tạo tất cả presenters |
| `InventoryPanel.cs` | AG2 panel Unity |
| `QuestJournalPanel.cs` | AG3 panel Unity |
| `NpcDialoguePanel.cs` | AG3 NPC dialogue panel |
| `SettingsPanel.cs` | AG4 panel Unity |
| `MapPanel.cs` | AG5 map panel Unity |
| `PlayerUIButtonBar.cs` | Thanh nút mở panel |
| `PlayerPrefsSettingsStore.cs` | ISettingsStore → PlayerPrefs |
| `P1PlayerUIHook.cs` | Composition hook nối vào P1OnlinePanel |

### Tests

| File | Mô tả |
|---|---|
| `PlayerUIChecksTests.cs` | 17 synthetic tests (AG1-AG4) |
| `PlayerUIChecksTests2.cs` | 12+ synthetic tests (AG3-AG6 scenarios) |

---

## 3. Cách chạy test

```sh
# Yêu cầu .NET 10
git switch antigravity/ag-01-player-ui-20261030
dotnet test Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj
```

---

## 4. Integration cho Codex / Qoder local

### Bước 1 — Assembly Definition
Tạo `Presentation.asmdef` tham chiếu `NguMach.Client.P1` asmdef. `PlayerUI.asmdef` tham chiếu cả `Presentation.asmdef` và Unity assemblies.

### Bước 2 — Wire P1OnlinePanel
Thêm `P1PlayerUIHook` component cạnh `P1OnlinePanel`. Trong `P1OnlinePanel.Open()`, sau khi client sẵn sàng:
```csharp
var hook = GetComponent<P1PlayerUIHook>();
if (hook != null)
{
    var adapter = new P1ClientAdapter(client);
    hook.Initialize(adapter);
}
```

Trong `P1OnlinePanel.ModalOpen`, thêm check:
```csharp
private bool ModalOpen =>
    (details != null && details.style.display.value == DisplayStyle.Flex) ||
    (audioPanel != null && audioPanel.style.display.value == DisplayStyle.Flex) ||
    (GetComponent<P1PlayerUIHook>()?.IsAnyPanelOpen ?? false);
```

Trong `P1OnlinePanel.Close()`, thêm:
```csharp
GetComponent<P1PlayerUIHook>()?.CloseAllPanels();
```

### Bước 3 — Gán HUD buttons
Trong `P1OnlinePanel.Build()`, sau khi build buttons `journalButton`/`bagButton`, gọi:
```csharp
journalButton.clicked += () => GetComponent<P1PlayerUIHook>()?.OpenPanel(PlayerPanel.QuestJournal);
bagButton.clicked += () => GetComponent<P1PlayerUIHook>()?.OpenPanel(PlayerPanel.Inventory);
```

---

## 5. Constraints và quyết định design

| Constraint | Giải pháp |
|---|---|
| DEC-023: 100 ô = 4 trang × 25 | `InventoryViewState.TotalSlots = 100`, `PagesCount = 4` |
| Filter không đổi slot index | `FilterText` là view field, presenter không reindex |
| Revision cũ không ghi đè mới | Guard trong `InventoryPresenter.LoadAsync` |
| Map zoom tách world camera | `MapViewState.ZoomLevel` chỉ affect UI rendering |
| Topology candidate | `TopologyIsCandidate = true` hard-coded cho đến khi review |
| Settings persistence | `PlayerPrefsSettingsStore` version-aware; schema bump = reset |
| UncertainMutation | Tất cả action buttons disabled khi `HasPendingMutation = true` |

---

## 6. UNVERIFIED items

- **Unity compile/import**: không có Unity trên máy này
- **UIDocument prefab/UXML**: cần tạo trong Unity Editor
- **Catalog resolver**: display name / rarity từ template catalog chưa connected → hiện `(UNRESOLVED)`
- **NPC record/choice contract**: chưa có endpoint → dialogue choices từ quest state server

---

## 7. Feature matrix

| Feature | Status |
|---|---|
| Panel router + modal stack | ✅ Live (tested) |
| Inventory 100ô/4 trang | ✅ Live (tested) |
| Inventory filter (view projection) | ✅ Live (tested) |
| Quest journal active/completed | ✅ Live (tested) |
| NPC dialogue (quest state based) | ✅ Live (tested) |
| Settings local preferences | ✅ Live (tested) |
| Settings PlayerPrefs persistence | ✅ Code done, Unity UNVERIFIED |
| Map view state | ✅ Live (tested) |
| Unity panels (UIToolkit) | ✅ Code done, Unity compile UNVERIFIED |
| P1OnlinePanel hook | ✅ Code done, needs Codex wire-up |
| Catalog display names | ⚠️ UNRESOLVED placeholder |
| Unity scene/prefab | ⛔ UNVERIFIED — no Unity |
| Device keyboard/touch tests | ⛔ UNVERIFIED — no Unity |
