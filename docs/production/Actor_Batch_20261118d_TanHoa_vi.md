# Tán Hoa của Linh Cung

Tán Hoa dùng ô 4. Linh Cung hạ trọng tâm, đưa cung ngang thân rồi quét cung về phía trước. Tay trái giữ chuôi cung, tay phải mở ở nhịp xả. Tám hướng dùng sprite riêng theo tạo hình Linh Cung đã chọn. Mỗi hướng có 16 tư thế gốc và điểm neo chân đo từ PNG.

## Hoạt ảnh và VFX

| Mốc | Từ đầu động tác | Hình ảnh |
| --- | ---: | --- |
| `fan_release` | 335 ms | Cụm cánh gỗ khép rời tay cầm cung ở khung 6, đếm từ 0. |
| `fan_full` | 580 ms | Năm cánh dài mở thành quạt 100°. Màu ngà trên đầu cánh và viền rêu giữ nét khi zoom xa. |
| `leaves_fall` | 755 ms | Mảnh lá tách thành ba cụm nhỏ và rơi khi quạt chính mờ dần. |

Quạt mở phát 16 pha trong 560 ms. Mảnh lá phát 16 pha trong 400 ms. Quạt hướng lên nằm dưới lớp thân ở phần tiếp giáp tay để giữ thứ tự che khuất. Hướng Đông và Tây Nam dùng đường chia ô đo tại khe trong suốt. Tất cả PNG giữ nguyên từng byte từ ImageGen.

## Chỉnh tay trong Sprite & VFX Studio

Mở `Implementation/Reports/Evidence/Actor_Batch_20261118d/TanHoa/<hướng>/project.json`. Mỗi project có bốn lớp gồm nhân vật, quạt, mảnh rơi và bia Rễ Nước. Chọn clip **Tán Hoa**. Kéo các mốc trong bảng để chỉnh điểm xuất phát, góc, kích thước, thứ tự vẽ và nhịp chuyển pha cho từng hướng. Biến đổi tỉ lệ và góc trên canvas đưa khẩu độ pha mở về 100° quanh chuôi cung.

## Kiểm hình

Godot phát 10 atlas nguồn và 8 bản ghép ở mức cố định 60 FPS. Bài kiểm đọc đủ 1.800 frame nguồn, 768 frame ghép và 160 khung hoặc pha nguồn riêng. `native_audit.json` ghi mã băm của project, video và ảnh chuỗi. `manual_review.json` ghi kết quả soát hình theo hướng.

1. Chạy `python Tools/ArtProduction/prepare_linh_cung_tan_hoa.py` để tạo tám project từ PNG nguyên bản.
2. Chạy `Tools/ArtProduction/review_actor_candidates_20261116c.ps1 -Batch 20261118d` để ghi nguồn.
3. Mở `ArtStudio.tscn` trong Movie Maker, chọn 60 FPS và 96 frame. Dùng `--studio-project` với project của hướng cần ghi và thêm `--studio-direction`, `--studio-play --studio-clean-view --studio-trace-layers`. Lưu `preview.mp4` và `preview.godot.log` cạnh project.
4. Chạy `python Tools/ArtProduction/audit_linh_cung_tan_hoa.py` để xác minh mốc, pha và mã băm.
