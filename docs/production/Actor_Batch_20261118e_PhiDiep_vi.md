# Phi Diệp của Linh Cung

Phi Diệp dùng ô 5. Linh Cung chùng gối, bước lùi trong lúc giương cung, nhả một mũi tên về hướng ngắm ban đầu rồi lấy lại thăng bằng. Cung giữ nguyên trên tay trái. Tám hướng dùng tám sprite sheet riêng, mỗi hướng 16 tư thế pixel chibi.

## Mốc động tác

| Mốc | Từ đầu động tác | Hình ảnh |
| --- | ---: | --- |
| `retreat_start` | 200 ms | Bắt đầu lùi, đặt dấu lá thứ nhất. |
| `arrow_release` | 320 ms | Nhả tên ở khung 8 và đặt dấu lá thứ hai. |
| `retreat_stop` | 480 ms trên đường đủ | Chân lấy lại thăng bằng. Mốc có thể đến sớm khi đường lùi bị chặn. |

Tên phản kích có 16 pha trong 400 ms. Vệt lá ngắn tan dần sau đầu tên. Atlas dấu lá có 16 pha trong 400 ms, dùng hai lần với điểm neo mặt đất riêng. Sheet hướng Đông có đường chia ô theo khe trong suốt để giữ đủ phần tóc và cung. Tất cả PNG là tệp ImageGen nguyên bản.

## Chỉnh tay trong Sprite & VFX Studio

Mở `Implementation/Reports/Evidence/Actor_Batch_20261118e/PhiDiep/<hướng>/project.json`. Mỗi hướng có năm lớp gồm thân, bia Rễ Nước, hai dấu lá và tên. Clip **Lùi đủ** cho xem cả quãng di chuyển. Clip **Lùi ngắn** dừng chuyển động gốc sớm, giữ cùng nhịp nhả. Có thể sửa quãng lùi, tốc độ bay, mốc nhả và vị trí từng dấu lá trên timeline. Bia chỉ giúp đọc phương của mũi tên khi soát hình.

## Kiểm hình

Godot Movie Maker ghi ở nhịp cố định 60 FPS. Bài kiểm đọc đủ 1.800 frame nguồn và 960 frame ghép, gồm tám hướng lùi đủ cùng hai ví dụ lùi ngắn Đông và Tây Bắc. Mỗi bản phát đủ các pha thân, hai dấu lá và mũi tên. `native_audit.json` ghim nguồn và bản ghi theo mã băm.

1. Chạy `python Tools/ArtProduction/prepare_linh_cung_phi_diep.py` để đo điểm neo và tạo project.
2. Chạy `Tools/ArtProduction/review_actor_candidates_20261116c.ps1 -Batch 20261118e` để ghi atlas nguồn.
3. Trong Movie Maker ở 60 FPS, ghi 96 frame trong `ArtStudio.tscn` với project tương ứng. Dùng `--studio-clip 0` cho lùi đủ hoặc `--studio-clip 1` cho lùi ngắn. Thêm `--studio-play --studio-clean-view --studio-trace-layers`.
4. Chạy `python Tools/ArtProduction/audit_linh_cung_phi_diep.py` để đối chiếu mốc, pha và video.
