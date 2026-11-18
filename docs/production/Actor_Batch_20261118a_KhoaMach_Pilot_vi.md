# Khóa Mạch của Linh Cung

Ngày 18/11/2026. Khóa Mạch có đủ tám hướng vẽ riêng. Mỗi sheet có 16 tư thế nguyên khối, từ thế chờ đến kéo dây, bắn một lần và hạ cung. Giữ tạo hình tóc đuôi ngựa, áo xanh ô liu, choàng ngắn và ống tên của atlas idle. Mũi tên lá và vệt lá vỡ tan có 16 pha riêng. Toàn bộ PNG nguồn được lưu cùng prompt ImageGen và mã băm.

## Mở và chỉnh trong Sprite & VFX Studio

Các thư mục `KhoaMach_<hướng>` nằm trong `Implementation/Reports/Evidence/Actor_Assembly_20261117a/`. Mở `project.json` của hướng cần chỉnh. Chọn **Play** để xem chuỗi động tác hoặc kéo timeline đến dấu `bow_release` và `confirmed_contact_preview`. Mỗi project có năm lớp chỉnh độc lập gồm Linh Cung, Thủy Căn, mũi tên bay, lá tan và dấu rễ. Có thể đổi vị trí, góc, tốc độ từng đoạn và điểm neo trong Studio.

| Hướng | Góc bay trên màn hình | Bắt đầu hiệu ứng bay trong Studio | Điểm cần chú ý |
| --- | ---: | ---: | --- |
| Đông | 0° | 480 ms | Mũi tên bám theo trục nằm ngang qua đầu cung. |
| Nam | 90° | 480 ms | Chỉ giữ một đầu tên chĩa xuống. |
| Đông Nam | 44° | 480 ms | Neo dưới hai chân, loại đầu tên thấp ra khỏi vùng lấy đế giày. |
| Bắc | −90° | 480 ms | Khi nhìn từ sau lưng, cung nằm bên trái và ống tên ở vai phải. |
| Đông Bắc | −39° | 540 ms | Sprite còn giữ tên ở frame 8, tính từ 0. Hiệu ứng bay xuất hiện khi tên rời cung ở frame 9. |
| Tây | 180° | 480 ms | Mũi tên ngang sang trái. Tay thả dây lùi về cạnh má. |
| Tây Nam | 146° | 480 ms | Trục đi xuống trái theo mũi tên ở pha kéo. |
| Tây Bắc | −147° | 480 ms | Chỉ còn một cánh cung trên và một cánh dưới trong pha nhả. |

Góc xoay áp dụng cho mũi tên lá và vệt lá tan. Dấu rễ giữ hướng của mục tiêu và dùng lại PNG `sk_lc_01_mark_component` đã được đánh giá nguồn. Vệt lá và dấu bắt đầu cùng điểm chạm trong demo. Khung nhìn tự vừa toàn bộ clip ở các hướng mới để giữ trọn người bắn và mục tiêu trong video.

## Kiểm tra và tích hợp

Toàn gói có 128 tư thế nhân vật và 32 pha VFX nguồn. Godot Movie Maker ghi ở 60 FPS. Mười video nguồn giải mã đủ 1.800 frame, tám video ghép đủ 960 frame. Xem kết quả theo hướng trong `native_audit.json` và bản tổng hợp `Implementation/Reports/Evidence/Actor_Batch_20261118a/native_audit.current.json`.

## Thử Khóa Mạch tại Bến Mưa

Trên Windows, mở PowerShell tại thư mục dự án và chạy:

```powershell
& .\ClientGodot\Run_Preview.ps1 -LinhCungPractice
```

Rễ Nước tập luyện được chọn lúc vào khu tập. Nhấn **1** hoặc bấm ô Khóa Mạch để giương cung và bắn. Dùng **WASD** để đổi hướng hoặc vị trí. Bấm vào bia để khóa lại mục tiêu, bấm chuột phải để nhắm theo hướng đứng. **F2** đổi giữa camera rộng và camera gần.

Ở cảnh này, mũi tên xuất phát từ đầu tên ở tư thế kéo dây cuối. Mũi tên dừng ở va chạm đầu tiên với bia hoặc địa hình. Chạm bia mới kích hoạt lá tan và dấu rễ. Phần thử đã có tư thế chờ trước và sau chiêu. Dấu rễ ở khu tập dùng thời lượng hiển thị 0,96 giây để xem animation. Kỹ năng online còn cần hợp đồng cast, xác nhận trúng và trạng thái dấu từ server.

Chạy lại bài kiểm bằng `Run_Preview.ps1 -LinhCungPractice -Test`. Lệnh `python Tools/ArtProduction/export_linh_cung_practice.py --check` đối chiếu pack ở `ClientGodot/assets/linh_cung_practice` với nguồn và biên bản Studio.

Bài chạy Godot đã kiểm tra đủ 128 tư thế nhân vật, nhận nút HUD và phím 1, chặn lần bấm lặp khi đang giương cung, xử lý bia và tường, rồi trở lại thế chờ. Các ảnh trong `Implementation/Reports/Evidence/Linh_Cung_Practice_20261118a/` chụp tại camera rộng. Bài đo riêng khi di chuyển với GeForce 820M đạt trung bình 60,06 FPS trên 722 frame, p95 16,94 ms.
