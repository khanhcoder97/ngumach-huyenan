# Báo cáo bàn giao AG-02 — Cột mốc 4 (M4): Bàn giao Phân hệ Giao diện Người chơi (Playable UI Handoff)

**Dự án**: Ngũ Mạch: Huyền Ấn
**Mục tiêu**: Hoàn tất Epic AG-02 (Issue #85, PR #89, Work Orders 12 & 14)
**Nhánh thực hiện**: `antigravity/ag-02-playable-ui-20261030`
**PR liên quan**: #89 (Target: `antigravity/ag-01-player-ui-20261030`, Refs #85, #80)
**Tác giả**: khanhcoder97 (Antigravity Remote Agent)

---

## 1. Tóm tắt kết quả chuyển giao

Toàn bộ các cột mốc từ M1 đến M4 của Epic AG-02 đã được hoàn thiện, kiểm thử tự động toàn diện và sẵn sàng tích hợp:

1. **Cột mốc 1 (M1 — Kiến trúc & Nền tảng)**:
   - Kế hoạch thực hiện chi tiết tại `Implementation/Plans/AG02_Playable_UI_Architecture_Plan.md`.
   - Phân tích hiện trạng và đối chiếu kỹ thuật tại `Implementation/Reports/AG02_Milestone1_Architecture_Report.md`.
2. **Cột mốc 2 (M2 — Định danh, Vòng đời, Bảng Nhân vật & Túi đồ)**:
   - Giải quyết dứt điểm các phát hiện AGR2-01 đến AGR2-06.
   - Bảng nhân vật và 12 ô trang bị (`CharacterPanel.cs`, `CharacterPresenter.cs`, `CharacterViewState.cs`).
   - Tra cứu vật phẩm theo catalog v1.0 (`ItemMetadataResolver.cs`).
   - Factory tự động dựng UI (`PlayerUIFactory.cs`, `PlayerUIBuilder.cs`).
   - Báo cáo chi tiết tại `Implementation/Reports/AG02_Milestone2_Character_Composition_Report.md`.
3. **Cột mốc 3 (M3 — Khám phá, Bản đồ, Điện ảnh & Tỉ lệ Giao diện)**:
   - Nhật ký nhiệm vụ phân giải tiến độ P00-01 (`QuestJournalPresenter.cs`).
   - Bản đồ hiển thị nhãn NPC canonical (`MapPresenter.cs`).
   - Phân cảnh điện ảnh 36 giây `CIN_001` có phụ đề và tua an toàn (`CinemaPresenter.cs`, `CinemaOverlay.cs`).
   - Thu phóng tỉ lệ toàn giao diện qua `UiScale` (`SettingsPanel.cs`).
   - Báo cáo chi tiết tại `Implementation/Reports/AG02_Milestone3_Exploration_Map_Cinema_Report.md`.
4. **Cột mốc 4 (M4 — Kiểm thử Hành trình Trọn vẹn & Hướng dẫn Native Handoff)**:
   - Ca kiểm thử tích hợp xuyên suốt `Journey_FullP0001ProgressionFlow` kiểm chứng dòng sự kiện từ gặp Lý An, nhận nhiệm vụ, cập nhật tiến độ, trả nhiệm vụ cho Tạ Vân Khanh đến kích hoạt phân cảnh điện ảnh.

---

## 2. Hướng dẫn kiểm thử và nghiệm thu trong Unity Editor

### 2.1 Cài đặt nhanh trong Scene
1. Mở Unity Editor với dự án Client.
2. Mở scene trò chơi chính (hoặc một test scene có sẵn `UIDocument`).
3. Nếu scene chưa có thành phần PlayerUI:
   - Trên thanh menu của Unity, chọn: `Tools` -> `Ngu Mach` -> `Setup PlayerUI in Scene`.
   - Script `PlayerUIBuilder` sẽ tự động tìm kiếm `UIDocument`, tạo GameObject `PlayerUI_Root` và gắn đầy đủ các panel, router, button bar và settings store.
4. Nhấn **Play**:
   - Khi `P1OnlinePanel` kết nối thành công, thanh điều hướng `PlayerUIButtonBar` xuất hiện ở góc phải dưới.

### 2.2 Kiểm tra các chức năng chính
| Chức năng | Phím tắt | Thao tác kiểm tra | Kỳ vọng hiển thị |
|---|---|---|---|
| **Nhân vật & Trang bị** | `C` | Nhấn phím `C` hoặc nút "Nhân vật" | Bảng mở ra, hiển thị ID nhân vật, phái, HP/MP thật từ máy chủ; 12 ô trang bị hiển thị tên vật phẩm hoặc (Trống); chỉ số chiến đấu gắn nhãn chờ snapshot từ server. |
| **Túi đồ** | `B` hoặc `I` | Nhấn phím `B`/`I` hoặc nút "Túi đồ" | Bảng mở ra, 4 tab chuyển trang mượt mà; rê chuột vào vật phẩm hiển thị tooltip tên tiếng Việt chuẩn theo catalog v1.0, không có chuỗi UNRESOLVED. |
| **Nhật ký Nhiệm vụ** | `J` | Nhấn phím `J` hoặc nút "Nhiệm vụ" | Bảng mở ra, hiển thị nhiệm vụ "Khởi Đầu Tại Bến Mưa", tiến độ đếm gói hàng `(x/3)` và hướng dẫn nộp nhiệm vụ cho Tạ Vân Khanh. |
| **Bản đồ** | `M` | Nhấn phím `M` hoặc nút "Bản đồ" | Bảng mở ra, hiển thị điểm người chơi và các NPC có nhãn "Lý An", "Tạ Vân Khanh". Thu phóng hoạt động trong dải 0.25x - 4.0x. |
| **Thiết lập** | Nút bánh răng | Nhấn nút thiết lập trên thanh điều hướng | Điều chỉnh thanh trượt Tỉ lệ Giao diện (UI Scale) -> toàn bộ kích thước giao diện UI Toolkit co giãn tương ứng. |
| **Đóng bảng (Escape)** | `Escape` | Mở 2 modal lồng nhau rồi nhấn Escape | Lần nhấn đầu chỉ đóng modal trên cùng; lần nhấn thứ hai đóng modal nền. Không bị đóng đúp hoặc đóng panel cha khi đang thao tác. |

---

## 3. Các giới hạn đã được tài liệu hóa và ghi nhận (Known Gaps)

Tuân thủ nghiêm ngặt nguyên tắc cốt lõi của dự án (DEC-021, DEC-023, Work Order 14):
1. **Chỉ số chiến đấu bổ sung (Công vật lý, Giáp, Bạo kích)**: Máy chủ hiện tại chưa cung cấp các trường này trong authoritative snapshot. Giao diện gắn nhãn thông báo rõ ràng `"Chưa có trong snapshot authoritative - missing server field"`, tuyệt đối không tự tính toán hoặc hiển thị số liệu giả.
2. **Thao tác Trang bị / Tháo đồ / Phân tách**: Chưa có endpoint mạng chính thức hỗ trợ. Các nút bấm được vô hiệu hóa có chủ đích kèm chú thích `"Chưa có endpoint server (authoritative action unavailable in baseline)"`.
3. **Phân cảnh Điện ảnh Video Muse**: Stream video Muse chưa có hợp đồng runtime trong client baseline. Phân cảnh đang hoạt động qua khung hiển thị an toàn tỉ lệ 16:9 (Preview Harness) với phụ đề và thanh tiến trình đồng bộ, đảm bảo không làm gián đoạn thế giới chung và không cấp thưởng ngoại tuyến khi bỏ qua.
4. **Tô-pô Tọa độ Bản đồ**: Đánh dấu trạng thái ứng viên (candidate), giữ nguyên dữ liệu gốc không chỉnh sửa tọa độ 349 điểm của thế giới.
