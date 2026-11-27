# Antigravity — Báo cáo Nghiệm thu Hoàn tất AG-02 (Work Order 16)

- **Ngày**: 2026-10-31
- **Tác giả**: Antigravity Remote
- **Nhánh**: `antigravity/ag-02-playable-ui-20261030`
- **PR**: #89 (Refs #85, #80, #94)
- **Base**: `antigravity/ag-01-player-ui-20261030` (#83)

---

## 1. Tổng quan & Mục tiêu

Giải quyết dứt điểm 11 findings (AGR3-01 đến AGR3-11) được Codex báo cáo trong review PR #94 (`Implementation/Reports/Antigravity_AG02_Review_20261031.md`), hoàn tất toàn bộ các hạng mục R0 đến R6 theo Work Order 16.

---

## 2. Chi tiết xử lý Findings (AGR3-01 đến AGR3-11)

| Finding | Gói | Thành phần | Mô tả xử lý | Trạng thái |
|---|---|---|---|---|
| **AGR3-01** | R0 | `PlayerUIRoot.cs`, `PlayerUIFactory.cs` | Cập nhật signature `SetPanelReferences` nhận đủ 8 tham số khớp chuẩn `r'\w+\s+\w+'` (bao gồm `CinemaOverlay cinema`). Factory gán `cinemaOverlay` thực. Bổ sung `using NguMach.Client.Presentation;` trong factory. | Resolved |
| **AGR3-02** | R0 | `PlayerUIBuilder.cs`, `PlayerUIFactory.cs` | Thêm menu kép `Tools/Ngu Mach/Setup PlayerUI in Scene` & `Ngu Mach/UI/Setup PlayerUI in Scene`. Tự động tìm host chứa `P1OnlinePanel` để nối root/hook/document đồng bộ. Idempotency qua `GetComponentInChildren<PlayerUIRoot>()`. | Resolved |
| **AGR3-03** | R1 | `P1OnlinePanel.cs`, `P1PlayerUIHook.cs`, `PlayerUIRoot.cs` | `Interact()` định tuyến qua `playerUIHook.OpenWithNpc(id)` khi có hook, gửi Entity ID khi interact và Template ID khi accept/turn-in qua cùng `P1Client`. Loại bỏ gửi trùng lặp. | Resolved |
| **AGR3-04** | R1 | `InventoryPresenter.cs`, `QuestJournalPresenter.cs` | Thêm guard `ct.IsCancellationRequested` ngay sau `ReadInventoryAsync` và `ReadQuestsAsync` để hủy kết quả đến muộn sau khi lifetime bị hủy, khôi phục trạng thái không bị kẹt `IsLoading`. | Resolved |
| **AGR3-05** | R2 | `ItemMetadataResolver.cs` | Bỏ greedy prefix matching. Triển khai phân giải hậu tố canonical `-R-<RARITY>` (`COMMON`, `REFINED`, `SPIRIT`, `ARCANE`, `RELIC`), ánh xạ tiền tố tiếng Việt chuẩn. Prefix lạ không kế thừa slot/class. | Resolved |
| **AGR3-06** | R2 | `CharacterPresenter.cs` | Kiểm tra vị trí trang bị Authoritative: chỉ vật phẩm có `item.location == "EQUIPPED"` mới được hiển thị trên ô trang bị nhân vật. Vật phẩm tại `BANK` hoặc `BAG` bị loại bỏ. | Resolved |
| **AGR3-07** | R2 | `NpcContextMapping.cs` | Gỡ bỏ toàn bộ test entity/quest ID (`ENT_MAN_BM_NPC_TEST`, `Q1`, `QUEST_TEST`, `NPC_TEST`) khỏi catalog production. Entity lạ không giả mạo ID canonical. | Resolved |
| **AGR3-08** | R2 | `P1UIState.cs` | `PageSlots()` lọc danh sách túi đồ theo `FilterText` mà không làm thay đổi slot index gốc của vật phẩm. | Resolved |
| **AGR3-09** | R4 | `QuestJournalPresenter.cs`, `P1UIState.cs` | Ghim nhiệm vụ (`TogglePin`) gắn đúng ID nhiệm vụ cụ thể (`PinnedQuestId`), tracker hiển thị trên HUD. | Resolved |
| **AGR3-10** | R5 | `CinemaViewState.cs`, `PlayerUIRoot.cs` | Cập nhật `IsPlaying` bao gồm cả `CinemaPlaybackPhase.Fallback`, cho phép phân cảnh fallback tiến độ và bỏ qua bình thường mà không bị kẹt. | Resolved |
| **AGR3-11** | R5 | `SettingsPanel.cs` | Gọi `ApplySettings(_presenter.Current)` ngay trong `Initialize()` để kích hoạt âm lượng và UI scale từ khi khởi động mà không cần mở bảng cài đặt. | Resolved |

---

## 3. Ma trận Tính năng (Feature Matrix)

| Tính năng | Phân loại Trạng thái | Ghi chú & Bằng chứng |
|---|---|---|
| Inventory Presentation & Tooltip | Source Implemented | `InventoryPresenter`, `ItemMetadataResolver` (xử lý exact catalog + rarity variant) |
| Character Sheet & Equipment Slots | Source Implemented | `CharacterPresenter` (authoritative `location == "EQUIPPED"`) |
| Quest Journal & Tracking | Source Implemented | `QuestJournalPresenter` (cancellation guard, pinned quest ID) |
| NPC Dialogue & Interaction | Source Implemented | `NpcDialoguePresenter`, `NpcContextMapping` (entity vs template canonical mapping) |
| Settings & Audio/Scale Persistence | Source Implemented | `SettingsPresenter`, `PlayerPrefsSettingsStore`, init bootstrap |
| Map View & HUD Markers | Source Implemented | `MapPresenter`, `P1UIState` (normalized bounds) |
| Cinema Overlay & Cutscene Fallback | Source Implemented | `CinemaPresenter`, `CinemaOverlay` (fallback phase playable/skippable) |
| PlayerUI Factory & Builder Harness | Source Implemented | `PlayerUIFactory`, `PlayerUIBuilder` (dual menu, host auto-discovery) |
| Test Suite & Regressions | Pure Fake / Scripted | 13 acceptance regression tests trong `PlayerUIChecksTests3.cs` |
| Live Network Transport | Unverified locally | Yêu cầu backend server cluster đang chạy |
| Native Unity Engine Import / PlayMode | Native Unverified | Cần Unity 6000.3.17f1 trên Muse VM |

---

## 4. Test & Regression Coverage

- Cập nhật `Client/Tests/PlayerUIChecks/PlayerUIChecksTests2.cs`:
  - Thay thế `NPC_TEST` và `Q1` bằng `NPC_LYAN` và `P00-01` để test hoạt động với canonical catalog.
- Bổ sung `ProducerAcceptanceRegressionTests` vào `Client/Tests/PlayerUIChecks/PlayerUIChecksTests3.cs`:
  - `CanonicalRarityVariantKeepsItsOwnMetadata` (4 cases: REFINED, SPIRIT, ARCANE, RELIC).
  - `CommonVariantControl`.
  - `UnknownPrefixCannotInheritKnownItemClassAndSlot`.
  - `LocationIsAuthoritativeForEquippedItems` (2 cases: BANK, BAG).
  - `EquippedLocationControl`.
  - `CancelledInventoryLifetimeIgnoresSuccessfulLateRead`.
  - `CancelledJournalLifetimeIgnoresSuccessfulLateRead`.
  - `UnknownNpcDoesNotForgeCanonicalTemplateIdentity`.
  - `TestQuestIsNotInProductionAssociationCatalog`.
