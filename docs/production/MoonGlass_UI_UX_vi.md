# MoonGlass — giao diện gameplay xanh tím bán trong suốt

Bảng màu theo ảnh tham khảo 2 và 3 của người chơi. Đây là giao diện chạy trong Godot .NET, dùng đường nét vector cho HUD/panel, giữ pixel art của thế giới và nhân vật. Không ghép nguyên hình concept vào game.

## Màu và vật liệu

| Vai trò | Giá trị |
| --- | --- |
| Chữ chính | #F3F3FF |
| Chữ phụ | #BDC5E5 |
| Viền bạc ánh tím | #AAB6EB |
| Điểm nhấn tím | #B3A5FF |
| Điểm nhấn champagne | #E5CDA9 |
| HP | #B84478 → #FF829A |
| MP | #4265B8 → #80C9FF |
| Panel chính | RGB(.17,.18,.31), alpha .84 |
| Bề mặt thẻ | RGB(.25,.26,.42), alpha .65 |
| Lớp phủ ngoài modal | RGB(.055,.065,.15), alpha .22 |

Bo góc 6–12 px; viền 1 px; bóng 6 px nhẹ. Không chạy blur toàn màn hình trên GPU yếu. Theme cache StyleBoxFlat dùng lại, không tạo resource mỗi khung hình. Các trạng thái nút có normal/hover/pressed/focus/disabled riêng. Biểu tượng được vẽ bằng SVG nguồn trong MoonGlassIcons.cs, không lấy từ ảnh mẫu. Avatar mới dùng built-in image_gen; prompt và ảnh nguồn lưu cùng đợt art.

## HUD ở viewport thiết kế 1280 × 720

- Khung nhân vật (22,22), 348×100: avatar tròn 86 px, tên lớp, HP/MP có số, tiền và Kiếm ý từ snapshot. Nhấp khung mở nhân vật. Không hiển thị level/EXP/premium khi server chưa cung cấp.
- Sáu nút tiện ích ở y134: nhân vật, túi, kỹ năng, nhiệm vụ, tương tác và thử lại.
- Bảng nhiệm vụ (22,192), 278×154: ba tab Chính tuyến/Hằng ngày/Sự kiện; chính tuyến dùng trạng thái và counter server, hai tab còn lại có empty state.
- Minimap (1050,22), 208×160: sơ đồ đường, sông và nhà từ layout authored; người chơi/NPC/điểm tương tác/mục tiêu từ world snapshot. Nhấp mở bản đồ. Sơ đồ art không được dùng làm server navigation.
- Nút đánh tâm (1172,624), bán kính52; sáu kỹ năng trên cung bán kính114, góc176°+26°×i. Cả sáu ô không đè nhau và giữ cách xa dock. Online chỉ ba kỹ năng đã hỗ trợ có thể gọi server; ba ô sau có trạng thái khóa rõ ràng. Offline có thể xem sáu VFX.
- Dock ở (385,658), 501×49 gồm mười lối tắt; các mục bang hội/hoạt động/thư ở hàng trên phải. Tooltip tên mục thay cho chữ viết tắt.
- Nhật ký hệ thống thu gọn dưới trái; tọa độ và FPS đọc thời gian chạy.

Camera vẫn top-down 64 × 36 WU mặc định, tùy chọn48 × 27. HUD nằm trên CanvasLayer tách camera; mở bảng sẽ ẩn HUD phía sau và ngừng di chuyển. H ẩn/hiện HUD khi chơi.

## Cửa sổ và điều hướng

Cửa sổ chức năng tối đa1120 × 620, hội thoại880 × 510, chừa24 px mép viewport. Thanh đầu có biểu tượng, tiêu đề, trạng thái và nút ×. Sidebar cuộn rộng157 px chứa13 mục; mục được chọn tự cuộn vào tầm nhìn. Nội dung cuộn riêng, chân cửa sổ giữ nút làm mới/thử lại/rời đi. Thanh lật trang chỉ xuất hiện trong hội thoại.

| Mục | Nội dung và tương tác |
| --- | --- |
| Nhân vật | Preview toàn thân xoay 8 hướng; tab thông tin/trang bị/thuộc tính. HP, MP, Kiếm ý, tọa độ và số đồ đang mặc đọc snapshot. 12 ô là bố cục hiển thị; không bổ sung token wire hay tự cho phép equip. |
| Túi đồ | Preview trái, tìm kiếm và bộ lọc giữa, lưới 5 cột, chi tiết phải. Các ô trống chỉ là ô trình bày, không phải số slot server đã mở. Chọn vật phẩm hiển thị tên/stack/vị trí/độ bền thực. Nút trang bị khóa khi route chưa hỗ trợ. |
| Kỹ năng | Sáu tên/icon hiện có; tab chủ động/nội tại/bộ kỹ năng; thông tin unavailable rõ ràng, không bịa damage/cooldown. |
| Nhiệm vụ | Nhật ký từ catalog nguồn + server counters; chặng chưa mở giấu tiêu đề/nội dung tương lai; chặng hoàn thành dùng đoạn truyện sau giao nhận. |
| Bản đồ | Sơ đồ khu authored, ký hiệu live actors và tọa độ; chưa có auto-path/teleport. |
| Lò rèn | Tab rèn/cường hóa/chế tạo, trạng thái dịch vụ và các hành động khóa; chưa có công thức/route giao dịch đã nghiệm thu. |
| Bang hội | Tab tổng quan/thành viên/hoạt động, empty state; không tạo số thành viên hay thưởng mẫu. |
| Hoạt động | Tab lịch/đấu trường/phần thưởng; chờ lịch và quyền nhận thưởng từ server. |
| Bách khoa | Tra cứu tên vật phẩm nguồn, danh sách NPC Bến Mưa và sáu kỹ năng; tìm kiếm tên bằng Enter. |
| Ngoại trang | Preview xoay 8 hướng, tab ngoại trang/vật phẩm hỗ trợ/lệnh bài; empty state khi chưa có collection. Không áp dụng buff từ giao diện. |
| Bạn bè | Tab bạn bè/tổ đội/gần đây; chờ dữ liệu social. |
| Thư tín | Tab hộp thư/đã nhận; chờ dữ liệu mailbox. |
| Cài đặt | Giảm VFX và camera gọn tác động thật; slider âm lượng Master; hướng dẫn phím. Lưu user://moonglass_ui.cfg. |

Túi đồ/bách khoa dùng Enter để gửi tìm kiếm; không dựng lại cây control mỗi ký tự để tránh mất focus. Nút không khả dụng có tooltip. Dữ liệu chưa kết nối dùng dấu— hoặc thông báo; không dùng mẫu số giả làm dữ liệu chơi.

## Hội thoại và trạng thái giao dịch

Chân dung NPC toàn thân, nội dung18px, lựa chọn hỏi thêm và nút lật trang. Chỉ trang cuối mới hiện nhận/trả nhiệm vụ; phải chờ server xác nhận. Reading, preview, tìm kiếm và đổi tab không cấp thưởng. Mất phản hồi giữ retry của phiên cũ; không tạo mutation mới. Modal giữ focus và chặn click xuyên xuống game.

## Phạm vi và bàn giao

Hiện nhắm desktop landscape với viewport 1280×720, integer scaling/letterbox giữ hình pixel sắc nét. Bố cục panel dùng Container và cuộn. Chưa chứng nhận portrait/mobile safe-area/touch/controller; không gọi đây là bản responsive mobile hoàn chỉnh.

Phần này hoàn thiện lớp trình bày và điều hướng, không chứng nhận guild/forge/equip12 slot/mail/trading đã có backend. P00-01 là tuyến gameplay thật đã kiểm; các chặng khác còn phụ thuộc packet đang review. Bảng màu này thay thế hướng xanh rêu/khung đồng cũ cho ClientGodot; tài liệu UI lịch sử dùng làm nguồn tính năng, không làm chuẩn màu.

Kiểm tra bằng Run_Playable_Alpha.ps1 -UiGallery: native HTTP quest + signal nút Godot (không phải physical mouse automation), sau đó chụp HUD và13 mục thật. Ảnh native và log ở Implementation/Reports/Evidence/MoonGlass_UI_20261106.
