# Khiêu Chiến E/SE v2 — sửa biểu cảm gọi và giữ đúng bằng chứng

Sau mốc 41 nguồn ngày 17/11/2026, hai sheet Khiêu Chiến hướng E và SE được sửa bằng trình tạo ảnh tích hợp. Bản v2 giữ động tác gõ chùy nhẹ, thế nâng đầu/ngực và hồi thế; thêm miệng mở đọc được ở pha gọi. E thể hiện ở pha 7–10; SE ở pha 7–9 rồi khép lại ở pha 10. Đây là mô tả hình đã quan sát, không suy ra kết quả từ prompt.

Đã xem PNG gốc và đủ 16 tư thế native của mỗi bản v2. Quan sát cũ “miệng đóng ở pha gọi” được giải quyết cho đúng hai phiên bản này; chưa phê duyệt nguồn cho gameplay. Hướng chính xác, root/idle, tỷ lệ camera rộng và cue trạng thái vẫn còn mở. SE v2 dùng gutter riêng và đề xuất viền giày tối 10 px gắn đúng SHA.

Ảnh, prompt và lịch sử cũ vẫn được giữ. Mốc hiện hành vẫn là 41 nguồn / 656 pose-pha được chọn; tổng phiên bản tăng từ 47 lên 49, gồm tám bản cũ. Hai bộ native trước thay thế được lưu riêng tại máy trong `TaE1` và `TaSE1`; commit mốc 41 trên GitHub cũng giữ nguồn và bằng chứng trước sửa.

Các gói `manual_view_bindings.*.json` khóa PNG, project, movie và montage đã xem. Công cụ ghi chú cũ từ chối khi một trong các artifact đổi, thay vì lấy ghi chú cũ gán cho ảnh mới. Đã chạy thử việc phát lại ghi chú v1 trên v2: bị từ chối đúng lý do và tệp quan sát hiện hành giữ nguyên mã băm. Đoạn nối loop chỉ giữ trạng thái đã xem khi PNG/project/movie, ảnh trích và chỉ số frame của đoạn nối cùng không đổi.

Kiểm tra lại 41 video: 7.380 frame giải mã, đủ 16 source phase mỗi nguồn. 119 test ArtProduction chạy lại đều đạt. Client C# không thay sau mốc 33 đã build/self-test; các native mới dùng cùng binary đó. Chưa thay catalogue hay PNG runtime gameplay. Còn chín nguồn Sơn Thần Giáng Thế trong gói 50 và toàn bộ các hold/ghép gameplay khác đã ghi.
