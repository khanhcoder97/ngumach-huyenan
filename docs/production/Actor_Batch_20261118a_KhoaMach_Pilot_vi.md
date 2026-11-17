# Khóa Mạch của Linh Cung

Ngày 18/11/2026. Đã có năm sheet nhân vật cho các hướng Đông, Nam, Đông Nam, Bắc và Đông Bắc. Mỗi sheet có 16 tư thế nguyên khối, từ hạ cung ở thế chờ đến kéo dây, bắn một lần và hạ cung. Giữ tạo hình tóc đuôi ngựa, áo xanh ô liu, choàng ngắn và ống tên của atlas idle. Mũi tên lá và vệt lá vỡ tan có 16 pha riêng. Toàn bộ PNG nguồn được lưu cùng prompt ImageGen và mã băm.

## Mở và chỉnh trong Sprite & VFX Studio

Các thư mục `KhoaMach_E`, `KhoaMach_S`, `KhoaMach_SE`, `KhoaMach_N` và `KhoaMach_NE` nằm trong `Implementation/Reports/Evidence/Actor_Assembly_20261117a/`. Mở `project.json` của hướng cần chỉnh. Chọn **Play** để xem chuỗi động tác hoặc kéo timeline đến dấu `bow_release` và `confirmed_contact_preview`. Mỗi project có năm lớp chỉnh độc lập gồm Linh Cung, Thủy Căn, mũi tên bay, lá tan và dấu rễ. Có thể đổi vị trí, góc, tốc độ từng đoạn và điểm neo trong Studio.

| Hướng | Góc bay trên màn hình | Bắt đầu hiệu ứng bay trong Studio | Điểm cần chú ý |
| --- | ---: | ---: | --- |
| Đông | 0° | 480 ms | Mũi tên bám theo trục nằm ngang qua đầu cung. |
| Nam | 90° | 480 ms | Chỉ giữ một đầu tên chĩa xuống. |
| Đông Nam | 44° | 480 ms | Neo dưới hai chân, loại đầu tên thấp ra khỏi vùng lấy đế giày. |
| Bắc | −90° | 480 ms | Khi nhìn từ sau lưng, cung nằm bên trái và ống tên ở vai phải. |
| Đông Bắc | −39° | 540 ms | Sprite còn giữ tên ở frame 8, tính từ 0. Hiệu ứng bay xuất hiện khi tên rời cung ở frame 9. |

Góc xoay áp dụng cho mũi tên lá và vệt lá tan. Dấu rễ giữ hướng của mục tiêu và dùng lại PNG `sk_lc_01_mark_component` đã được đánh giá nguồn. Vệt lá và dấu bắt đầu cùng điểm chạm trong demo. Khung nhìn tự vừa toàn bộ clip cho bốn hướng mới để giữ trọn người bắn và mục tiêu trong video.

## Kiểm tra và tích hợp

Đã xem 64 mẫu khung hình của bốn hướng mới và chuỗi giương cung, bay, chạm trên cả năm hướng. Toàn gói có 112 tư thế hoặc pha nguồn. Godot Movie Maker ghi ở 60 FPS. Bảy video nguồn giải mã đủ 1.260 frame, năm video ghép đủ 600 frame. Xem kết quả theo hướng trong `native_audit.json` và bản tổng hợp `Implementation/Reports/Evidence/Actor_Batch_20261118a/native_audit.current.json`.

Các khoảng cách, nhịp bắn và thời điểm chạm trong bảng là giá trị để xem hoạt ảnh trong Studio. Để đưa vào gameplay cần ba hướng Tây, Tây Bắc, Tây Nam có cùng tay cầm cung, chuyển tiếp từ và về idle, kiểm tra ở camera rộng, và nối dấu rễ với xác nhận trúng của hệ thống chiến đấu. Dữ liệu catalog và sprite hiện hành của client vẫn ở phiên bản trước.
