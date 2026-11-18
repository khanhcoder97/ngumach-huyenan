# Dây Gai của Linh Cung

Ngày 18/11/2026. Gói nguồn gồm tám hướng vẽ riêng của động tác đặt hạt và bốn atlas hiệu ứng nền trong suốt. Mỗi atlas có 16 tư thế hoặc pha nguồn. Nhân vật giữ tạo hình Linh Cung đã chọn, giữ cung ở tay trái và dùng tay phải đặt hạt. Các bản lỗi được giữ cùng prompt để tiện đối chiếu.

## Hoạt ảnh và hiệu ứng

| Lớp | Chuyển động | Thời lượng xem thử |
| --- | --- | ---: |
| Linh Cung | Hạ thấp người, mở tay, đứng dậy | 1,12 giây |
| Hạt | Rời tay, chạm đất, hai đốm nhỏ tắt | 0,48 giây |
| Mọc | Hạt mở, dây lan trên đất và ba gai nhô lên | 0,64 giây |
| Chờ | Giữ hình bẫy, nhịp sáng nhẹ chạy quanh vòng | 1,12 giây mỗi vòng |
| Thu | Gai gập, dây cuộn về hạt rồi mờ dần | 0,64 giây |

Hạt bắt đầu tại điểm đo trên tay và đáp xuống tâm chung của bẫy. Các lớp mọc, chờ và thu giữ tâm đó. Hướng Đông Bắc và Tây Bắc đặt hạt ở frame 7, các hướng còn lại ở frame 8, tính từ 0. Điểm neo chân được đo riêng để loại tay đặt hạt khỏi vùng lấy đế giày. Với hướng nhìn từ sau, lớp bẫy nằm dưới lớp nhân vật để giữ thứ tự che khuất.

## Mở trong Sprite & VFX Studio

Mở `Implementation/Reports/Evidence/Actor_Batch_20261118b/DayGai/<hướng>/project.json`. Mỗi project có năm lớp chỉnh độc lập và hai clip. Clip đầu, `trigger`, chuyển sang thu khi bẫy được kích hoạt sớm. Clip thứ hai, `expire`, phát đủ hai vòng chờ rồi thu. Có thể kéo mốc timeline tới `seed_release`, `trap_growth`, `trap_armed` hoặc mốc kết thúc.

Các mốc chờ của clip kiểm hình là 0,98 giây và 2,24 giây. Trong khu luyện tập, bẫy đổi trạng thái theo va chạm và thời gian của cảnh. Khi triển khai online, tín hiệu `TRAP_STATE` từ máy chủ sẽ quyết định lúc đổi trạng thái.

## Thử tại Bến Mưa

Mở PowerShell tại thư mục dự án và chạy.

```powershell
& .\ClientGodot\Run_Preview.ps1 -LinhCungPractice
```

Nhấn **2** hoặc bấm ô **Dây Gai**, rồi bấm chuột trái vào mặt đất. Vòng xanh cho biết có thể đặt. Vòng đỏ báo ngoài tầm, có địa hình chắn hoặc nằm trên nước. Nhấn **Esc** hoặc chuột phải để hủy chọn điểm. Phím **1** tiếp tục bắn Khóa Mạch.

Rễ Nước đi tuần dọc đường phía tây chỗ xuất phát. Đặt bẫy trên đường đi để thử kích hoạt hoặc đặt ở khoảng đất trống để thử hết hạn. Mỗi lần đặt phát hoạt ảnh thả hạt theo hướng đã chọn. Vòng báo mọc sáng trong 0,45 giây, rồi bẫy chờ tối đa 4 giây trong phạm vi 2 m. Bẫy thu lại sau lần kích hoạt đầu tiên và làm chậm bia 40% trong 2,5 giây. Nếu hết hạn, dây tự thu. Khu tập dùng tầm đặt 6 m và cho phép thử lại sau khi bẫy thu xong.

Phần sát thương, linh lực, hồi chiêu và trạng thái online cần nối với máy chủ. Khu tập hiện xác nhận thao tác đặt đất, pha chạm và chuyển động chậm của bia.

Chạy `Run_Preview.ps1 -LinhCungPractice -Test` để làm lại bài kiểm. Godot đã kiểm đủ 128 khung nhân vật khi đặt bẫy, chặn điểm đặt trong công trình và trên nước, xác nhận bia bước từ ngoài vào trong vòng bẫy, và xác nhận bẫy trên đất trống tự thu sau 4 giây. Ảnh gameplay và số liệu nằm trong `Implementation/Reports/Evidence/Day_Gai_Practice_20261118b/`. Đo khi di chuyển ở camera rộng trên GeForce 820M đạt 59,89 FPS trung bình trên 720 frame, p95 16,88 ms.

## Kết quả kiểm hình

Mười hai video nguồn giải mã đủ 2.160 frame. Ba video ghép ở 60 FPS giải mã đủ 720 frame, gồm Đông và Tây Bắc kích hoạt sớm, Nam hết hạn. Đã xem đủ 192 tư thế hoặc pha nguồn, chuỗi ghép của ba bản ghi và điểm nối 14 → 15 → 0 → 1 của vòng chờ. Vòng thu thu nhỏ quanh cùng một tâm, rồi mờ trên các frame cuối.

Các bản đã loại gồm nền mờ ở pha mọc và Đông Bắc, thao tác đặt ngược ở hướng Bắc và chồng tay gần chuôi cung ở Tây Bắc. `native_audit.json` và `manual_review.json` ghim báo cáo với PNG, project và video tương ứng.

## Tái lập

1. Chạy `python Tools/ArtProduction/prepare_linh_cung_day_gai.py` để đọc atlas và tạo project từ nguồn đã ghim.
2. Chạy `Tools/ArtProduction/review_actor_candidates_20261116c.ps1 -Batch 20261118b` để ghi 12 video nguồn.
3. Trong Godot Movie Maker, dùng `--studio-project` với project đã chọn, `--studio-clip 0` cho kích hoạt sớm hoặc `--studio-clip 1` cho hết hạn. Thêm `--studio-play --studio-clean-view --studio-trace-layers`. Ví dụ ghi hình đi kèm gồm hướng Đông và Tây Bắc kích hoạt sớm, hướng Nam hết hạn.
4. Chạy `python Tools/ArtProduction/audit_linh_cung_day_gai.py` để đối chiếu video, nhịp nguồn và mã băm của các project.
