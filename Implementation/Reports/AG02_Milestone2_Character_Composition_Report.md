# Báo cáo triển khai AG-02 — Cột mốc 2 (M2): Định danh, Vòng đời, Kiến trúc & Trang bị nhân vật

**Dự án**: Ngũ Mạch: Huyền Ấn
**Đặc tả kỹ thuật**: DEC-021, DEC-023, Work Order 12 & 14
**Nhánh thực hiện**: `antigravity/ag-02-playable-ui-20261030`
**PR liên quan**: #89 (Refs #85, #80)
**Tác giả**: khanhcoder97 (Antigravity Remote Agent)

---

## 1. Tổng quan mục tiêu Cột mốc 2 (M2)

Thực hiện toàn diện các yêu cầu trong Work Order 14 và giải quyết dứt điểm các phát hiện AGR2-01 đến AGR2-06:
1. **AGR2-01 (Định danh NPC wire & context mapping)**: Phân tách rõ `entityId`, `recordId`, `templateId`. Tương tác thế giới gửi entity ID thật (`ENT_MAN_BM_NPC_LYAN`, `ENT_MAN_BM_NPC_TA_VAN_KHANH`), lệnh nhận/trả nhiệm vụ gửi canonical template ID (`NPC_LYAN`, `NPC_TA_VAN_KHANH`).
2. **AGR2-02 (Vòng đời & Generation Token)**: Thêm cơ chế view generation token (`_generation`) trong `NpcDialoguePresenter`. Mọi kết quả bất đồng bộ đến muộn sau khi gọi `Clear()` hoặc đổi tương tác bị hủy bỏ, giữ trạng thái `Idle` và `Value == null`.
3. **AGR2-03 (Chủ quyền phím Escape)**: Đảm bảo phím Escape chỉ đóng đúng 1 modal panel trên một lần nhấn. `PlayerUIRoot.HandleEscapeInput` được đặt `false` khi hoạt động dưới sự điều phối của `P1PlayerUIHook` / `P1OnlinePanel`.
4. **AGR2-04 (Composition Root & Factory)**: Bổ sung `PlayerUIFactory` và `PlayerUIBuilder` cho phép khởi tạo toàn bộ phân hệ PlayerUI bằng mã nguồn hoặc một thao tác menu Editor mà không cần kéo thả thủ công.
5. **AGR2-05 (Giải phóng tài nguyên & Hủy lắng nghe)**: Bổ sung phương thức `Dispose()` trên `P1PlayerUIHook` và giải phóng triệt để visual tree và callbacks khi session kết thúc.
6. **AGR2-06 (Bảng Nhân vật & 12 Slot Trang bị)**:
   - Triển khai `CharacterViewState` và `CharacterPresenter` đọc dữ liệu sinh mệnh từ `P1Self` và trang bị từ `P1Inventory` (`location == "EQUIPPED"`).
   - Chuẩn hóa 12 slot trang bị theo `Character_Equipment_Inventory_Spec_vi.md` và ánh xạ alias từ DEC-023.
   - Gắn nhãn minh bạch các chỉ số chiến đấu chưa có: `"Chưa có trong snapshot authoritative - missing server field"`.
   - Vô hiệu hóa nút thao tác kèm lý do: `"Chưa có endpoint server (authoritative action unavailable in baseline)"`.
   - Triển khai `ItemMetadataResolver` tra cứu tên hiển thị, phẩm chất, mô tả theo `Item_Master_Catalog_vi.csv`, loại bỏ chuỗi `UNRESOLVED`.
   - Triển khai giao diện UI Toolkit `CharacterPanel.cs` và nút "Nhân vật" trên `PlayerUIButtonBar.cs`, hỗ trợ phím tắt `C`.

---

## 2. Chi tiết các tệp thay đổi và bổ sung

| Tệp | Trạng thái | Mục đích |
|---|---|---|
| `Client/Assets/Scripts/Online/Presentation/NpcContextMapping.cs` | Thêm mới | Định danh đối chiếu entity ID, record ID, template ID và danh mục nhiệm vụ NPC |
| `Client/Assets/Scripts/Online/Presentation/ItemMetadataResolver.cs` | Thêm mới | Tra cứu siêu dữ liệu hiển thị vật phẩm theo Master Catalog v1.0 |
| `Client/Assets/Scripts/Online/Presentation/CharacterViewState.cs` | Thêm mới | Trạng thái bất biến hiển thị sinh mệnh, 12 slot trang bị và cờ server field |
| `Client/Assets/Scripts/Online/Presentation/CharacterPresenter.cs` | Thêm mới | Điều phối đọc `Self`, ánh xạ slot trang bị và xử lý thao tác trang bị |
| `Client/Assets/Scripts/Online/Presentation/P1UIState.cs` | Cập nhật | Bổ sung `InteractionTargetEntityId`, `NpcTemplateId`, `SourceRecordId` vào `NpcDialogueViewState` |
| `Client/Assets/Scripts/Online/Presentation/NpcDialoguePresenter.cs` | Cập nhật | Quản lý generation token chống late completion và ánh xạ định danh canonical NPC |
| `Client/Assets/Scripts/Online/Presentation/InventoryPresenter.cs` | Cập nhật | Tích hợp `ItemMetadataResolver` tra cứu tên và phẩm chất cho ô túi đồ |
| `Client/Assets/Scripts/Online/Unity/P1OnlinePanel.cs` | Cập nhật | Truyền `UIDocument` vào hook và gọi `Dispose()` khi đóng panel |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/CharacterPanel.cs` | Thêm mới | Giao diện UI Toolkit hiển thị nhân vật, sinh mệnh, 12 ô trang bị và thẻ chi tiết |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/PlayerUIFactory.cs` | Thêm mới | Factory khởi tạo runtime cho phân hệ PlayerUI |
| `Client/Assets/Scripts/Online/Editor/PlayerUIBuilder.cs` | Thêm mới | Menu Editor `Tools -> Ngu Mach -> Setup PlayerUI in Scene` |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/P1PlayerUIHook.cs` | Cập nhật | Hỗ trợ inject `UIDocument`, quản lý Escape ownership và `Dispose()` |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/PlayerUIButtonBar.cs` | Cập nhật | Bổ sung nút mở bảng "Nhân vật" |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/PlayerUIRoot.cs` | Cập nhật | Định tuyến `PlayerPanel.Character`, xử lý phím tắt `C`, `B`, `J`, `M`, chặn double Escape |
| `Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj` | Cập nhật | Bổ sung 4 tệp Presentation mới vào project kiểm thử C# thuần |
| `Client/Tests/PlayerUIChecks/PlayerUIChecksTests3.cs` | Thêm mới | 11 ca kiểm thử cho entity mapping, generation lifetime, character sheet và modal stack |

---

## 3. Kết quả kiểm thử

- **PlayerUIChecks**: Bổ sung bộ kiểm thử `PlayerUIChecksTests3.cs` bao gồm:
  1. `TemplateIdentityControl`: Xác nhận tương tác với canonical template ID mở đúng lựa chọn nhiệm vụ.
  2. `WorldEntityIdentityMustResolveQuestAction`: Xác nhận `ENT_MAN_BM_NPC_LYAN` và `ENT_MAN_BM_NPC_TA_VAN_KHANH` giữ nguyên entity ID trên wire nhưng ánh xạ đúng action nhận/nộp nhiệm vụ.
  3. `ClearedDialogueMustIgnoreLateCompletion`: Xác nhận tương tác hoàn tất muộn sau `Clear()` không làm sống lại view state.
  4. `AcceptQuest_SendsCanonicalNpcId`: Xác nhận nhận nhiệm vụ gửi canonical template ID.
  5. `TurnInQuest_SendsCanonicalNpcId`: Xác nhận nộp nhiệm vụ gửi canonical template ID.
  6. `Presenter_IdleWhenSelfNull`: Xác nhận khi chưa có `Self`, presenter giữ trạng thái `Idle`.
  7. `Presenter_LoadsAuthoritativeVitals`: Xác nhận sinh mệnh HP/MP/tọa độ đọc chính xác từ snapshot authoritative.
  8. `Presenter_MapsEquipmentSlotsCorrectly`: Xác nhận ánh xạ slot `MAIN_HAND`, `HEAD` vào canonical slot và tra cứu tên vật phẩm.
  9. `Presenter_MarksMissingCombatStatsAndDisablesActions`: Xác nhận cờ chỉ số thiếu và vô hiệu hóa nút hành động.
  10. `Presenter_UnequipReturnsUnsupportedEndpoint`: Xác nhận từ chối tháo đồ khi chưa có endpoint server.
  11. `Resolver_ResolvesCatalogMetadata` & `Resolver_ProvidesCleanFallbackWithoutUnresolvedString`: Xác nhận phân giải tên và fallback an toàn.
  12. `Router_SingleCloseTopPopsOnlyOneModal`: Xác nhận 1 phím Escape chỉ đóng 1 modal trên stack.
