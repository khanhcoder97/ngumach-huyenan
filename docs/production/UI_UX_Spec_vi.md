# ĐẶC TẢ UI/UX
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.0

### 1. Mục tiêu trải nghiệm và nền tảng

- Game 2D ngang pixel art; UI dùng cùng ngôn ngữ pixel art với panel sơn mài/giấy dó/đồng chạm được vẽ thành cụm pixel. Theo `Pixel_Art_Production_Standard_vi.md`; không blur, vector icon hoặc fractional scaling.
- Điện thoại: ngang, vùng render tối thiểu 1280×720 tương đương; hỗ trợ tỷ lệ 16:9 đến 20:9. Safe area theo notch/cạnh bo. Không xoay UI theo dọc.
- PC: 16:9/16:10, chuột + bàn phím, tay cầm là tùy chọn. Chuẩn tham chiếu 1920×1080. UI scale 80–125%, chọn trong cài đặt.
- Thiết kế ưu tiên 3 thao tác: đọc mục tiêu, chiến đấu, nhặt/nhận nhiệm vụ. Các màn quản lý sâu mở bằng panel lớn; không khóa di chuyển quá lâu ngoài combat.
- Cỡ chữ dùng bitmap font tiếng Việt theo logical canvas; cỡ hiển thị tương ứng 18–22px ở 1080p cho thân bài, 28–36px tiêu đề, 20px số combat. Điện thoại giữ integer asset scaling và reflow panel, không làm mờ font.
- Màu sắc không là tín hiệu duy nhất: trạng thái cần icon/hình dạng/chữ. Nền panel đục đủ tương phản; nền mờ tối đa 30% để vẫn thấy nhân vật.

### 2. Lưới và vùng an toàn

Mọi tọa độ UI tính theo phần trăm vùng an toàn, gốc (0,0) trên góc trái trên. HUD luôn neo theo vùng, không theo pixel tuyệt đối.

| Vùng | Điện thoại ngang | PC 1080p | Chứa |
|---|---|---|---|
| Cụm nhân vật | trái trên; rộng tối đa 46% | trái trên; 360–410 px | avatar, tên, cấp/cảnh giới, tiền, 4 thanh |
| Bản đồ nhỏ | phải trên; 176–208 dp | phải trên; 210–240 px | pixel minimap, mục tiêu, khu vực |
| Theo dõi nhiệm vụ | trái giữa, dưới cụm nhân vật | trái giữa, rộng 300–360 px | chương và objective |
| Di chuyển | trái dưới; joystick mobile | ẩn; phím/tay cầm | joystick, đi/chạy/nước rút |
| Kỹ năng/hành động | phải dưới; vòng cung mobile | phải dưới; phím tắt | đánh thường, 6 kỹ năng, khóa mục tiêu |
| Telemetry | sát mép dưới trái, thu gọn | sát mép dưới trái | tọa độ, giờ máy chủ, FPS/ping |
| Quick access | dưới cụm nhân vật | dưới cụm nhân vật | chat, thư, bang, cài đặt |

HUD có thể kéo thả bố cục và lưu 3 preset: mặc định, ít che màn hình, tay trái thuận. Tối thiểu vùng chạm 48×48dp; nút thường xuyên dùng cách nhau ít nhất 8dp. Đặc tả chi tiết từng widget, dữ liệu và trạng thái xem `Gameplay_HUD_Overlay_Spec_vi.md`.

### 3. HUD trong bản đồ khám phá

**Cụm nhân vật góc trái:** portrait tròn/lục giác, tên, lớp và pill cấp/cảnh giới; HP crimson, MP azure, tài nguyên lớp amethyst, Hộ Thể amber khi có khiên, EXP gold mảnh dưới cùng. Hộ Thể là shield tạm thời, không phải stat giáp. Xem `Gameplay_HUD_Overlay_Spec_vi.md` để biết thứ tự, số liệu và state.

**Header khu vực:** tên map + kênh + ping. Chạm map nhỏ mở bản đồ đầy đủ. Nút Menu mở panel 3 cột: Nhân vật, Túi đồ, Kỹ năng, Nhiệm vụ, Bản đồ, Xã hội, Thú, Nghề, Cài đặt.

**Quest tracker:** panel Ink-900 pixel frame neo trái giữa, dưới status; tối đa 3 nhiệm vụ ghim PC/2 mobile, mỗi quest tối đa 2 objective. Có nút thu gọn và nhấn vào dòng mở chi tiết. Dòng objective dùng số tiến độ (ví dụ 3/6), khoảng cách chỉ khi có tọa độ đích; không dựng mũi tên che nhân vật. Objective boss có marker mép màn hình khi ngoài khung camera.

**Controls mobile:** joystick trái 136–152dp; đánh thường 94–104dp; 6 kỹ năng trên cung bán kính 142–166dp, ô 48–58dp. Bốn skill chủ động, skill cơ động/phòng thủ và tuyệt kỹ theo loadout. Tất cả có thể kéo bố cục/đảo tay trái; Auto-combat không xuất hiện trong PvP, siege, boss raid; nếu tính năng auto PvE được đưa vào sau thì tắt kỹ năng tốn tài nguyên/né boss theo mặc định.

**Controls PC:** di chuyển A/D, nhảy Space, tương tác E, đánh thường J/chuột trái; skill Q/W/E/R/1/2, né Shift, potion 3/4. Rebind tất cả. Có thể dùng chuột trái click hướng đánh, nhưng không click-to-move mặc định để tránh xung đột combat side-scroll.

### 4. Màn hình đăng nhập, tạo nhân vật và chọn nhân vật

**Đăng nhập:** nền minh họa Bến Mưa tĩnh, logo ở góc trên trái, nút tiếp tục lớn dưới giữa, lựa chọn khu vực máy chủ, ngôn ngữ, hỗ trợ. Không đặt gacha/vật phẩm bán hàng trên màn đầu.

**Tạo nhân vật:** bước 1 chọn tên (3–16 ký tự, lọc ký tự điều khiển, cấm tên trùng, kiểm duyệt); bước 2 chọn một trong năm môn phái; bước 3 chỉnh khuôn mặt/tóc/da/phụ kiện; bước 4 xem tóm tắt vai trò rồi xác nhận. Sân khấu preview sprite pixel art chiếm 55% khung, có các frame/góc quay đã vẽ và pose idle. Môn phái mô tả rõ vai trò, độ khó và loại vũ khí; không gắn vai trò “healer bắt buộc” cho Huyền Bút. Không khóa ngoại hình/phái theo giới tính. Xác nhận phái là lựa chọn lưu lâu dài; cho phép đổi sau bằng vật phẩm/chi phí công khai, không biến thành paywall.

**Chọn nhân vật:** tối đa 4 slot tài khoản theo cấu hình; hiện tên, lớp, cấp, khu vực cuối đăng nhập, thời gian chơi. Nút Tạo mới, Vào game, Xóa nhân vật có xác nhận hai bước và thời gian chờ 7 ngày; màn này không có vật phẩm tiêu hao.

### 5. Nhân vật và trang bị

**Tab Tổng quan:** bên trái preview nhân vật toàn thân; giữa là 12 ô trang bị quanh silhouette; bên phải chỉ số chính, chiến lực không được dùng làm chỉ số duy nhất; dưới có tab Thuộc tính, Ngoại hình, Danh hiệu. Chạm stat hiện tooltip có công thức, nguồn cộng và giới hạn PvP/PvE.

12 ô thiết bị theo GDD: nón, áo, quần, vũ khí, găng, giày, dây chuyền, nhẫn trái, nhẫn phải, ngọc bội, phi phong, ấn hộ mệnh. Ô trống có outline theo loại; vật phẩm không đúng lớp bị mờ và nêu lý do. Hành động trang bị một chạm, đổi với món đang mặc; popup so sánh hai cột ghi tăng/giảm từng stat, nguồn số màu kèm dấu +/− và không chỉ tổng điểm.

**Tab Ngoại hình:** bộ trang phục/skin, hiệu ứng vũ khí, thú theo sau, danh hiệu. Trang phục ngoại hình có thể che phần lớn áo/quần nhưng không che silhouette, biểu cảm combat, cảnh báo trạng thái. Có nút xem trước, so sánh màu, mặc thử 30s trong phòng preview; chỉ lưu khi nhấn áp dụng.

Quản lý ngoại trang, chỉnh diện mạo gốc, buff/auto-use và routing dịch vụ qua NPC theo đặc tả `Appearance_Buff_NPC_Service_Overlay_Spec_vi.md`. Preview dùng sprite sheets pixel art của game, tách ledger mở khóa ngoại trang khỏi trang bị có chỉ số; lệnh boss chỉ mở Thí Luyện Hồi Ức và không khóa boss/dungeon/raid tiến trình thường.

### 6. Thiết kế túi đồ

**Bố cục:** panel 2 cột lớn. Trái 67% là grid 5 cột × 5 hàng (25 ô/trang, 4 trang cho 100 ô), phải 33% là chi tiết món đang chọn. Đầu panel: số ô dùng/tổng, bộ lọc, tìm kiếm, sort. Máy tính hỗ trợ hover tooltip; mobile chạm một lần chọn, chạm lần hai mở hành động.

**Tab và lọc:** Tất cả, Trang bị, Nguyên liệu, Tiêu hao, Nhiệm vụ, Thú/khác. Sort: phẩm chất, cấp yêu cầu, mới nhất, loại, số lượng. Bộ lọc theo môn phái, slot, phẩm chất, khóa/giao dịch. Nút “Mới” biến mất sau khi xem. Trang bị có viền màu phẩm chất cộng biểu tượng hình thoi/sao; màu hiếm không dùng làm mã độc nhất.

**Chi tiết món:** icon 96dp, tên, phẩm chất, cấp, lớp/slot, binding, level yêu cầu, chỉ số, dòng ngẫu nhiên, socket, độ bền, mô tả lore, nguồn thu được. Nút chính Trang bị/Dùng/Mở khóa socket; phụ Khóa, So sánh, Tách, Bán hoặc Bỏ. Không cho bán/bỏ vật phẩm nhiệm vụ, vật phẩm đang mặc, đồ có khóa giao dịch, hoặc món được gắn cờ bảo vệ. Vật phẩm Huyền/Cổ Vật cần xác nhận nhập tên khi phân giải.

**Túi đầy:** hiển thị “Túi gần đầy” ở 80%; khi đủ chặn loot thường, nhưng vật phẩm nhiệm vụ/key item đi vào tab riêng có giới hạn dung lượng server. Loot hiển thị rơi trên đất tối đa 60s; chủ loot thấy nút nhặt nếu còn quyền. Không tự xóa vật phẩm hiếm. Nút “Dọn nhanh” chỉ chọn nguyên liệu dư đã whitelist và vật phẩm thường không khóa, luôn hiển thị danh sách trước thao tác.

### 7. Các panel hệ thống

| Panel | Bố cục và chức năng |
|---|---|
| Kỹ năng | cây kỹ năng trái theo cấp mở, giữa preview/tooltip, phải 6 ô trang bị nhanh; 2 preset đổi tại hub; tab Nội tại, PvP, PvE; thử trong phòng tập; reset miễn phí lần đầu |
| Nhiệm vụ | cột danh mục Chính/Phụ/Ngày/Tuần/Guild; giữa danh sách; phải chi tiết, NPC nhận/trả, bước hiện tại, phần thưởng và nút định vị |
| Bản đồ | bản đồ khu vực lớn, legend theo icon, tầng/platform switch nếu có; danh sách NPC/mob chỉ hiện khi đã khám phá hoặc quest liên quan; Thăng Long Thành có bản đồ 900 WU theo khu phố, route selector chỉ hiện map đã mở |
| Bách khoa | 3 cột: danh mục, search/grid, inspector; tra item/quest/boss/quái/kỹ năng/map, source guide, discovery state và spoiler policy; chi tiết trong `Compendium_Encyclopedia_Overlay_Spec_vi.md` |
| Nghề | nghề, cấp, thanh tiến trình, công thức; khi chế tạo hiện nguyên liệu đủ/thiếu, xác nhận và thời gian; chế tạo hàng loạt có giới hạn 10 lượt |
| Thú | portrait thú, level/loyalty, 4 slot trang bị thú theo GDD, kỹ năng tự động/bật tắt, nút gọi/thu; không cho thú che telegraph |
| Cửa hàng NPC | tab bán/mua, filter, giá và phí; xác nhận giao dịch trước khi server thực hiện; đơn vị tiền và số dư luôn nhìn thấy |
| Phòng thay đồ & buff | `Appearance_Buff_NPC_Service_Overlay_Spec_vi.md`: preview sprite 2D, vanity, salon/nhuộm, trạng thái buff, auto-use và dịch vụ theo NPC/map; lệnh boss có quota account |
| Rèn/nâng cấp | mở `Forge_Crafting_Overlay_Spec_vi.md`: catalog/recipe, preview trước→sau, nguyên liệu realtime và quote; có cường hóa +0…+15, khảm, tinh luyện, sửa chữa, phân giải; thao tác xác nhận rõ kết quả và không tiêu nguyên liệu khi quote đã hết hạn |
| Xã hội | nhóm, bạn, guild, thư; tìm bằng tên chính xác hoặc ID nhân vật; chặn/báo cáo ở menu người chơi |

### 8. Bang hội, party và chat trong UI

Bang hội có panel Tóm tắt, Thành viên, Nhiệm vụ, Kho, Công trình, Công thành, Nhật ký, Cài đặt. Dòng thành viên hiển thị trạng thái, cấp, lớp, map, đóng góp tuần; quyền nhạy cảm chỉ leader/officer và có log. Kho guild có phân trang, người gửi, thời gian, lịch sử gửi/rút; mobile yêu cầu giữ 0,6s ở nút rút vật phẩm hiếm. Xem đặc tả đầy đủ tại Guild_Social_Spec_vi.md.

Party tối đa 5 người; thanh thành viên xếp dọc cạnh trái dưới portrait, HP/MP và class icon; leader có vương miện nhỏ, mục tiêu focus có viền. Nút ping vị trí, mời, rời, đề cử leader. Raid 10 người chia hai nhóm 5, hiện 10 thanh nhỏ; không chiếm quá 18% chiều rộng màn hình.

Chat có tab Khu vực, Nhóm, Bang, Thì thầm, Hệ thống. Mặc định thu gọn, mở rộng khi nhập; filter lời mời/thương mại. Link vật phẩm hiện thẻ preview không tự gửi giao dịch. Chặn người chơi không chặn cảnh báo hệ thống. Chức năng báo cáo nằm trong menu tin nhắn, lý do chọn nhanh, không bắt người dùng viết văn bản.

### 9. Luồng thao tác quan trọng

**Trang bị loot vừa nhận:** toast tên món và phẩm chất → chạm toast mở detail → so sánh → trang bị → cập nhật số stat bằng animation dưới 0,25s. Không lấy quyền tự động thay đồ.

**Nhận/trả nhiệm vụ:** NPC có marker khác nhau cho sẵn sàng nhận, đang tiến hành, có thể hoàn thành; biểu tượng đồng nhất với quest journal. Chạm tương tác mở hội thoại; lựa chọn có thể đọc tiếp hoặc nhận; phần thưởng hiện trước nút Nhận. Nếu bag đầy, cho hoàn thành quest và gửi reward vào mailbox/vault theo loại; không mất tiến độ.

**Vào boss raid:** panel hiện đề xuất cấp, người trong đội, vai trò tự chọn, thiết bị khuyến nghị, cơ chế quan trọng; có nút sẵn sàng và rời. Khi combat bắt đầu, panel đóng; telegraph boss theo mô tả map/raid. Không giấu cơ chế trong tooltip.

**Rèn món:** chọn item → chọn công thức → kiểm tra nguyên liệu/chi phí/khóa → hiện cơ hội thành công và kết quả có thể có → nút Rèn → nhận kết quả và log. Có thể bật khóa bảo vệ để giữ item không đem rèn nhầm.

### 10. Cài đặt, khả năng tiếp cận và thông báo

Modal gameplay dùng bố cục 2 cột trên desktop, 1 cột cuộn trên mobile ngang. Có preset Đồ họa/Âm thanh/Input/HUD, account card, Tiếp Tục Hành Trình, tutorial, góp ý và thoát kẹt. Chi tiết responsive, control states, preview/rollback, safe area và DOM tham chiếu nằm trong `Settings_Overlay_Spec_vi.md`.

Preset hiệu ứng: Đầy đủ, Giảm hiệu ứng, Tắt hạt phụ. Thanh riêng cho rung, lóe, chuyển động camera, độ mờ, cỡ chữ, cỡ HUD. Hỗ trợ colorblind palette: không đổi màu telegraph một mình; thay thêm pattern (sọc, chấm, gạch chéo). Cỡ subtitle chỉnh được; tên người chơi có thể ẩn; âm thanh cảnh báo boss có slider riêng. Thời tiết trang trí có thể tắt, telegraph luôn giữ.

Thông báo loot, quest, guild invite được gom hàng đợi, không hơn 3 toast cùng lúc. Toast đóng sau 4s hoặc người chơi xóa; thông tin quan trọng được ghi vào nhật ký. Push notification ngoài game mặc định tắt và cần opt-in.

### 11. Danh sách kiểm tra bàn giao UI

- Có mockup 16:9, 16:10, 20:9 và vùng safe area thật của notch.
- Mọi popup có Esc/Back, nút đóng và trạng thái focus; thao tác gamepad có thứ tự focus.
- Mọi giao dịch có giá, loại tiền, số lượng, trạng thái binding, nút xác nhận.
- Tất cả màn hình túi/nhân vật/bang hội thể hiện dữ liệu server; client không báo thành công trước xác nhận server.
- Thử UI ở màn hình nhỏ nhất hỗ trợ, chữ 200%, VFX thấp, mù màu mô phỏng, thao tác một tay.
- Không dùng thành phần giao diện, icon, typography, logo hoặc minh họa trích xuất từ tài sản KPAH.
