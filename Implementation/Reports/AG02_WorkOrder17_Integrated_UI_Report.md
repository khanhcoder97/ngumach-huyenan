# Antigravity — Báo cáo Tích hợp & Vòng chơi Hoàn chỉnh AG-02 (Work Order 17)

- **Ngày**: 2026-10-31
- **Tác giả**: Antigravity Remote
- **Nhánh**: `antigravity/ag-02-playable-ui-20261030`
- **PR**: #89 (Refs #85, #80, #94)
- **Base**: `antigravity/ag-01-player-ui-20261030` (#83)

---

## 1. Tổng quan & Mục tiêu

Thực hiện trọn gói các hạng mục A đến E theo Work Order 17 (`Implementation/Work_Orders/17_ANTIGRAVITY_INTEGRATED_UI_EPIC_20261031.md`), chuyển đổi từ các panel UI riêng lẻ sang vòng chơi tích hợp hoàn chỉnh:
1. **Composition & Lifecycle** (Mục A): Xóa bỏ toàn bộ tìm kiếm toàn cục (`FindFirstObjectByType`), inject trực tiếp `UIDocument` và `ISettingsStore` vào từng panel. Triển khai `Teardown()` dọn dẹp triệt để visual tree và callbacks, bảo đảm vòng lặp mở/đóng 200 chu kỳ an toàn, không rò rỉ bộ nhớ.
2. **Concrete Transport Journey** (Mục B): Tích hợp harness kiểm thử P00-01 qua `P1ClientAdapter` và `P1Client` với scripted wire transport thật, kiểm chứng luồng nhận nhiệm vụ, cập nhật tiến độ, nộp nhiệm vụ và nhận phần thưởng authoritative.
3. **Diagnostics, Map Bounds & HUD Tracker** (Mục C): Không làm mất dữ liệu khi gặp slot trùng hoặc ngoài dải (tự động phân bổ lại vào ô trống và ghi nhận cảnh báo), chuẩn hóa tọa độ bản đồ theo `map_bounds.json`, kết nối `PinnedQuestId` với HUD Quest Tracker trực quan trên màn hình.
4. **Input Dispatcher & Settings Bootstrap** (Mục D): Điều phối phím Escape / Space tập trung qua modal stack (ưu tiên bỏ qua phân cảnh điện ảnh trước khi đóng modal hoặc rơi xuống gameplay). Kích hoạt âm lượng và scale UI ngay khi khởi động.
5. **Gói Bàn giao & Muse VM Packet** (Mục E): Lập ma trận tính năng chi tiết và hướng dẫn kiểm thử Unity PlayMode cho Muse VM.

---

## 2. Chi tiết Triển khai Theo Từng Hạng Mục

### Hạng mục A: Composition & Lifecycle Hoàn chỉnh
- **PlayerUIFactory & Document Ownership**:
  - `PlayerUIFactory.Create(host, document)` tiếp nhận và bảo toàn tham số `document`, gắn kết với `host.GetComponent<UIDocument>()` nếu không được truyền trực tiếp.
  - Loại bỏ hoàn toàn 100% các lệnh `FindFirstObjectByType<UIDocument>` và `FindFirstObjectByType<PlayerPrefsSettingsStore>` trên toàn bộ các panel (`InventoryPanel`, `CharacterPanel`, `QuestJournalPanel`, `NpcDialoguePanel`, `MapPanel`, `SettingsPanel`, `PlayerUIButtonBar`, `CinemaOverlay`).
  - `PlayerUIRoot.Open(adapter, doc)` truyền trực tiếp `_doc` và `store` vào hàm `Initialize` của toàn bộ 8 panel con.
- **Teardown & Tránh Trùng lặp Giao diện**:
  - Mỗi panel con được bổ sung phương thức `Teardown()`: gỡ bỏ `_root` khỏi visual hierarchy (`_root.RemoveFromHierarchy()`), hủy đăng ký sự kiện của presenter (`OnChanged -= ...`), gọi `_presenter.Clear()`.
  - Hàm `Initialize` của mỗi panel có cơ chế kiểm tra idempotent: nếu `_root` đã được khởi tạo, tái sử dụng visual element thay vì tạo mới trùng lặp, chỉ re-attach vào document mới.
- **PlayerUIBuilder**:
  - Tự động kiểm tra và gán `PanelSettings` hợp lệ từ `Resources/PlayerUI/DefaultPanelSettings` hoặc `AssetDatabase` khi tạo `UIDocument`.

### Hạng mục B: Hành trình qua Concrete Adapter (`P1ClientAdapter`)
- Xây dựng `ScriptedP1Transport` triển khai `IP1Transport` thực hiện mã hóa / giải mã JSON theo wire contract.
- Thử nghiệm toàn diện hành trình P00-01 (`Journey_FullP0001_ThroughConcreteClientAndAdapter`) kết nối `P1Client` -> `P1ClientAdapter` -> `NpcDialoguePresenter`, `QuestJournalPresenter`, `InventoryPresenter`:
  - `POST /p1/sessions`: Kết nối phiên ban đầu tại Bến Mưa.
  - Tương tác NPC Lý An bằng Entity ID (`ENT_MAN_BM_NPC_LYAN`) -> Presentation map sang Canonical Template ID (`NPC_LYAN`).
  - Nhận nhiệm vụ `P00-01` -> Cập nhật nhật ký hiển thị "Thu thập gói hàng Bến Mưa (0/3)".
  - Tiến độ thu thập 3/3 gói hàng -> Trạng thái chuyển `READY_TO_TURN_IN`.
  - Tương tác Tạ Vân Khanh (`ENT_MAN_BM_NPC_TA_VAN_KHANH`) -> Nộp nhiệm vụ qua wire với `NPC_TA_VAN_KHANH`.
  - Nhận phần thưởng trang bị `EQ-MK-WEAPON-T1-R-COMMON` ("Thường Kiếm Mưa Khởi Minh Kiếm") vào túi đồ và chuyển trạng thái nhiệm vụ sang `COMPLETED`.

### Hạng mục C: Diagnostics Túi đồ, Map Bounds & HUD Tracker
- **Bảo toàn dữ liệu túi đồ**: Khi gặp vật phẩm có slot trùng (`duplicate_slot_index`) hoặc slot ngoài dải (`out_of_range_slot`), `InventoryPresenter` ghi nhận cảnh báo chẩn đoán và tự động phân bổ vật phẩm vào ô túi đồ trống kế tiếp. Không có bất kỳ vật phẩm nào bị biến mất khỏi giao diện người chơi.
- **Chuẩn hóa Map Bounds**: Thay thế hệ số phóng đại `4f/WU` cố định bằng lớp `MapBounds` định nghĩa chuẩn từ `map_bounds.json` (bản đồ chuẩn 360×84, Thăng Long 900×108). Tỷ lệ hiển thị trên mini-canvas được suy ra chính xác từ độ rộng bounds thực tế.
- **HUD Quest Tracker**: Bổ sung `_trackerBox` trên thanh công cụ `PlayerUIButtonBar` hiển thị nhiệm vụ được ghim (`PinnedQuestId`). Tự động đồng bộ với `QuestJournalPresenter`, cho phép người chơi click vào tracker để mở nhanh bảng nhật ký nhiệm vụ.

### Hạng mục D: Cinema, Settings & Input Dispatcher
- **Điều phối Input tập trung**:
  - `PlayerUIRoot.CloseTop()` ưu tiên bỏ qua (`Skip()`) phân cảnh điện ảnh đang phát (`CinemaOverlay`) trước khi đóng các modal bên dưới.
  - Phím Escape và Space được định tuyến qua `P1PlayerUIHook` / `P1OnlinePanel.ModalOpen`, vô hiệu hóa di chuyển và tung chiêu trong gameplay khi bất kỳ panel UI nào đang mở.
- **Khởi động Cài đặt**: `SettingsPanel` nạp cấu hình và áp dụng ngay lập tức âm lượng tổng và tỷ lệ co giãn giao diện (`UiScale`) trên chính `UIDocument` được inject.

---

## 3. Ma trận Tính năng (Feature Matrix)

| Tính năng | Phân loại Trạng thái | Ghi chú & Bằng chứng |
|---|---|---|
| Injected Document Composition | Source Implemented | 0 cuộc gọi `FindFirstObjectByType<UIDocument>`, inject từ Factory/Root |
| UI Lifecycle & Teardown | Source Implemented | Hủy visual tree, hủy đăng ký sự kiện, kiểm chứng qua 200 chu kỳ mở/đóng |
| Concrete P1Client Journey | Concrete Transport Verified | Chạy qua `P1Client` + `P1ClientAdapter` + `ScriptedP1Transport` |
| Inventory Data Retention | Source Implemented | Relocation ô trùng/ngoài dải vào ô trống, giữ đủ 100 slot |
| Canonical Map Bounds | Source Implemented | Tọa độ chuẩn hóa theo `map_bounds.json` (thay thế 4px/WU) |
| HUD Quest Tracker | Source Implemented | Gắn tracker trực tiếp trên `PlayerUIButtonBar`, liên kết `PinnedQuestId` |
| Unified Escape/Space Dispatcher | Source Implemented | `CloseTop` xử lý Cinema Skip trước modal router; modal chặn combat |
| Settings Direct Bootstrap | Source Implemented | Áp dụng âm lượng và UI scale trực tiếp lên document được inject |
| Native Unity Import / PlayMode | Native Unverified | Cung cấp test packet chi tiết bên dưới cho Muse VM |
| Live Cluster HTTP Network | Unverified locally | Cần cụm máy chủ backend live hoạt động |

---

## 4. Gói Bàn giao Nghiệm thu Unity (Muse VM Packet)

- **Môi trường yêu cầu**: Unity Editor 6000.3.17f1.
- **Thao tác thiết lập tự động**:
  1. Mở Scene gameplay client (hoặc Scene chứa `P1OnlinePanel`).
  2. Chọn menu: `Tools` → `Ngu Mach` → `Setup PlayerUI in Scene` (hoặc `Ngu Mach/UI/Setup PlayerUI in Scene`).
  3. Kiểm tra Hierarchy: GameObject `PlayerUI_Host` (hoặc host chứa `P1OnlinePanel`) được gắn `UIDocument` với `PanelSettings` hợp lệ, `P1PlayerUIHook` và GameObject con `PlayerUI_Root`.
- **Kịch bản kiểm thử PlayMode**:
  1. Nhấn **Play**.
  2. Bấm phím **C**: Mở bảng Nhân vật (12 ô trang bị hiển thị trạng thái chuẩn). Bấm **Esc**: Đóng bảng Nhân vật.
  3. Bấm phím **B** hoặc **I**: Mở Túi đồ (100 ô / 4 trang).
  4. Bấm phím **J**: Mở Nhật ký nhiệm vụ. Ghim nhiệm vụ `P00-01` -> Kiểm tra tracker xuất hiện trên HUD.
  5. Bấm phím **M**: Mở Bản đồ mini (kiểm tra bounds co dãn theo `map_bounds.json`).
  6. Mở Bảng Cài đặt: Kéo thanh Tỷ lệ giao diện -> Toàn bộ `UIDocument` co dãn mượt mà.
  7. Kích hoạt phân cảnh `CIN_001` -> Bấm **Space** hoặc **Esc** -> Phân cảnh kết thúc mà không gây kích hoạt tung chiêu hay di chuyển nhân vật.
