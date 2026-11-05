# Báo cáo triển khai AG-02 — Cột mốc 3 (M3): Bản đồ, Nhật ký nhiệm vụ, Phân cảnh Điện ảnh & Tỉ lệ Giao diện

**Dự án**: Ngũ Mạch: Huyền Ấn
**Đặc tả kỹ thuật**: DEC-019, DEC-020, DEC-022, Work Order 12 & 14
**Nhánh thực hiện**: `antigravity/ag-02-playable-ui-20261030`
**PR liên quan**: #89 (Refs #85, #80)
**Tác giả**: khanhcoder97 (Antigravity Remote Agent)

---

## 1. Tổng quan mục tiêu Cột mốc 3 (M3)

Thực hiện các yêu cầu trong Work Order 14 (AG2-D và AG2-E):
1. **AG2-D (Nhật ký Nhiệm vụ & Bản đồ Khám phá)**:
   - **Bản đồ (MapPresenter)**: Phân giải nhãn hiển thị cho các điểm đánh dấu NPC trên bản đồ thông qua `NpcContextMapping` (hiển thị "Lý An", "Tạ Vân Khanh" thay vì entity ID thô). Giữ nguyên ràng buộc DEC-019: thu phóng bản đồ chỉ ảnh hưởng tới tầng UI, không can thiệp camera thế giới thực; tô-pô giữ nhãn ứng viên.
   - **Nhật ký Nhiệm vụ (QuestJournalPresenter)**: Tích hợp phương thức phân giải nội dung nhiệm vụ `ResolveQuestCopy` cho chuỗi `P00-01` ("Khởi Đầu Tại Bến Mưa"), tự động định dạng tiến độ đếm gói hàng `(x/3)` và hướng dẫn nộp nhiệm vụ cho Tạ Vân Khanh khi hoàn tất; hỗ trợ ghim/bỏ ghim (`TogglePin`).
2. **AG2-E (Trình chiếu Phân cảnh Điện ảnh Muse & Thiết lập Tỉ lệ Giao diện)**:
   - **Trạng thái & Bộ điều phối Điện ảnh (CinemaViewState & CinemaPresenter)**: Máy trạng thái quản lý phân cảnh điện ảnh (`Idle`, `Playing`, `Ended`, `Fallback`). Cấu hình phân cảnh mẫu `CIN_001` ("Nước không soi bóng") thời lượng 36 giây, 4 mốc phụ đề bám sát kịch bản Bến Mưa. Tuân thủ tuyệt đối quy tắc: không tạm dừng thế giới dùng chung (DEC-019), tua/bỏ qua không tự ý phát sinh phần thưởng giả lập ngoại tuyến.
   - **Lớp phủ Điện ảnh (CinemaOverlay)**: Thành phần UI Toolkit toàn màn hình với khung chuẩn an toàn 16:9 / 20:9, thanh tiến trình, hộp phụ đề và nhãn cảnh báo rõ ràng `Preview Harness` khi chưa tích hợp stream video Muse.
   - **Tỉ lệ Giao diện (SettingsPanel)**: Cập nhật hàm `ApplySettings` áp dụng `UiScale` lên `_doc.rootVisualElement` để thu phóng toàn bộ giao diện game một cách nhất quán theo Work Order 14, thay vì chỉ thu phóng riêng cửa sổ thiết lập.
   - **Tích hợp Kiến trúc (PlayerUIFactory & PlayerUIRoot)**: Kết nối `CinemaOverlay` vào cây thành phần do factory khởi tạo và cung cấp phương thức kích hoạt `PlayCinema(sceneId)` từ root điều phối.

---

## 2. Chi tiết các tệp thay đổi và bổ sung

| Tệp | Trạng thái | Mục đích |
|---|---|---|
| `Client/Assets/Scripts/Online/Presentation/CinemaViewState.cs` | Thêm mới | Trạng thái bất biến hiển thị phân cảnh điện ảnh, thời lượng, tiến độ và phụ đề |
| `Client/Assets/Scripts/Online/Presentation/CinemaPresenter.cs` | Thêm mới | Bộ điều phối phân cảnh điện ảnh, xử lý tua/bỏ qua và cập nhật phụ đề theo thời gian |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/CinemaOverlay.cs` | Thêm mới | Giao diện UI Toolkit toàn màn hình hiển thị khung an toàn 16:9, phụ đề và nút bỏ qua |
| `Client/Assets/Scripts/Online/Presentation/QuestJournalPresenter.cs` | Cập nhật | Phân giải tiêu đề và mô tả tiến độ cho P00-01 ("Khởi Đầu Tại Bến Mưa"), ghim nhiệm vụ |
| `Client/Assets/Scripts/Online/Presentation/MapPresenter.cs` | Cập nhật | Phân giải nhãn hiển thị điểm đánh dấu NPC qua `NpcContextMapping` |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/SettingsPanel.cs` | Cập nhật | Áp dụng `UiScale` lên `rootVisualElement` của UIDocument |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/PlayerUIFactory.cs` | Cập nhật | Thêm thành phần `CinemaOverlay` vào quá trình khởi tạo cấu trúc PlayerUI |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/PlayerUIRoot.cs` | Cập nhật | Tích hợp tham chiếu `CinemaOverlay` và phương thức kích hoạt `PlayCinema` |
| `Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj` | Cập nhật | Bổ sung `CinemaViewState.cs` và `CinemaPresenter.cs` vào project kiểm thử |
| `Client/Tests/PlayerUIChecks/PlayerUIChecksTests3.cs` | Cập nhật | Bổ sung các bộ kiểm thử cho Cinema, Quest Journal Copy, Map Markers |

---

## 3. Kết quả kiểm thử

Đã bổ sung 12 ca kiểm thử mới:
- `CinemaPresenterTests`:
  - `Cinema_StartsInIdle`: Khởi động ở trạng thái `Idle`, không phát sinh lỗi.
  - `Cinema_PlaySceneLoadsSceneMetadata`: Nạp đúng tiêu đề "Nước không soi bóng", thời lượng 36 giây cho `CIN_001`.
  - `Cinema_UpdateAdvancesProgressAndSubtitles`: Tiến trình thời gian cập nhật đúng các mốc phụ đề.
  - `Cinema_SkipEndsPlaybackWithoutReward`: Bỏ qua phân cảnh kết thúc ngay lập tức mà không cấp vật phẩm giả lập.
  - `Cinema_UnknownSceneFallsBackToHarness`: Phân cảnh chưa có rơi về chế độ fallback an toàn.
  - `Cinema_CloseResetsToIdle`: Đóng phân cảnh đưa trạng thái về `Idle`.
- `QuestJournalCopyTests`:
  - `Journal_ResolvesP0001Copy`: Phân giải đúng tiêu đề và số đếm tiến độ `(2/3)`.
  - `Journal_PinTogglesPinnedTracker`: Bật/tắt ghim nhiệm vụ hoạt động chính xác.
  - `Journal_SeparatesActiveAndCompletedQuests`: Tách biệt chính xác nhiệm vụ đang làm và đã hoàn thành.
- `MapMarkerResolutionTests`:
  - `Map_ResolvesNpcMarkerLabels`: Ánh xạ đúng tên "Lý An" và "Tạ Vân Khanh" cho marker NPC.
  - `Map_ZoomClampsBetweenBounds`: Giới hạn mức thu phóng trong khoảng 0.25x đến 4.0x.
  - `Map_HandlesNullWorldGracefully`: Xử lý an toàn khi thế giới chưa có dữ liệu.
