# Liên Châu của Linh Cung

Liên Châu dùng ô kỹ năng 3 của Linh Cung. Gói nguồn có tám sprite sheet nhân vật vẽ riêng theo tám hướng nhìn từ trên xuống, một atlas đốm tích tên và một atlas mũi tên Mộc. Mỗi atlas có 16 khung nguồn. Nhân vật giữ nguyên tạo hình, trang phục và cung trong sprite đã chốt.

## Diễn biến động tác

Linh Cung đặt chân, nâng cung và kéo dây. Năm đốm sáng báo trước năm lần nhả. Mỗi lần nhả có một tư thế thân riêng, một điểm xuất phát đo trên tay cầm cung và một mũi tên riêng. Mũi tên có đầu sáng và vệt lá rời dần khi đi xa. Sau lần nhả cuối, tay hạ về tư thế giữ cung.

| Lần nhả | Thời điểm từ đầu động tác | Khung thân, đếm từ 0 | Lệch so với hướng ngắm |
| --- | ---: | ---: | ---: |
| 1 | 180 ms | 3 | 0° |
| 2 | 290 ms | 6 | −6° |
| 3 | 400 ms | 9 | +6° |
| 4 | 510 ms | 11 | −3° |
| 5 | 620 ms | 13 | +3° |

Trong Studio, phần thân chạy 810 ms. Năm đốm hiện cùng lúc ở mốc 70 ms, mỗi đốm tắt khi mũi tên tương ứng rời cung. Mũi tên bay thử 320 ms với 16 pha ảnh, qua quãng đường 182 px của sân kiểm hình. Các số đo này phục vụ chỉnh hoạt ảnh. Quy tắc trận đấu nằm trong đặc tả Liên Châu.

## Chỉnh tay trong Sprite & VFX Studio

Mở `Implementation/Reports/Evidence/Actor_Batch_20261118c/LienChau/<hướng>/project.json`. Thư mục hướng dùng mã `N`, `NE`, `E`, `SE`, `S`, `SW`, `W` và `NW`. Chọn clip **Liên Châu** rồi kéo mốc `arrow_release_1` đến `arrow_release_5` để xem điểm bắt đầu từng mũi.

Mỗi project có 12 lớp gồm thân, bia thử, năm đốm và năm mũi tên. Chọn lớp tương ứng để chỉnh điểm neo, vị trí, góc, độ hiển thị và thứ tự vẽ. Có thể đổi thời lượng từng đoạn trên timeline để xem tốc độ bay khác. Bia Rễ Nước chỉ giúp đọc hướng bay trên sân kiểm hình.

## Kiểm hình

Godot Movie Maker ghi đủ tám hướng ghép tại 60 FPS. Bài kiểm đã đọc 1.800 frame từ mười video nguồn và 768 frame từ tám video ghép. Mỗi hướng phát đủ 16 khung thân và mỗi mũi tên phát đủ 16 pha. Bản hướng Bắc đầu tiên có đầu tên lặp trên khung nhả. Bản đã chọn loại phần dư đó, với tóc đuôi ngựa che một phần tay nhả cuối. Các tệp `native_audit.json` và `manual_review.json` ghim kết quả vào nguồn, project và video tương ứng.

## Tái lập bản kiểm hình

1. Chạy `python Tools/ArtProduction/prepare_linh_cung_lien_chau.py` để đo điểm neo và tạo lại tám dự án Studio từ PNG gốc.
2. Chạy `Tools/ArtProduction/review_actor_candidates_20261116c.ps1 -Batch 20261118c` để ghi mười video nguồn.
3. Chạy Godot Movie Maker ở 60 FPS và 96 frame cho mỗi hướng. Mở `ArtStudio.tscn` với `--studio-project` trỏ tới project tương ứng, `--studio-direction` trùng mã thư mục và thêm `--studio-play --studio-clean-view --studio-trace-layers`. Xuất video thành `preview.mp4` và lưu log thành `preview.godot.log` cạnh project.
4. Chạy `python Tools/ArtProduction/audit_linh_cung_lien_chau.py` để đối chiếu SHA-256, nhịp nhả, các pha nguồn và bản ghi Studio.

Hợp đồng `VOLLEY_PROJECTILE_STATE`, sát thương, chi phí linh lực, hồi chiêu và giới hạn ba mũi trúng mỗi mục tiêu sẽ được kiểm khi nối gameplay. Bản này bàn giao hoạt ảnh và VFX Liên Châu trong Studio.
