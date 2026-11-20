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

## Chơi thử tại Bến Mưa

Chạy `ClientGodot/Run_Preview.ps1 -LinhCungPractice`. Nhấn **5** hoặc bấm ô hình mũi tên có hai dấu lá. Chọn bia để khóa hướng trước khi giương cung, hoặc bỏ chọn bằng chuột phải để dùng hướng hiện tại.

Phi Diệp lùi tối đa 5 m trong 280 ms. Chuyển động tăng tốc rồi giảm tốc. Tường hoặc bờ sông dừng bước lùi tại va chạm đầu tiên. Tên vẫn rời cung theo hướng đã khóa, sau mốc bắt đầu lùi 120 ms. Trong khu tập, tên bay tối đa 8 m và báo hệ số 80% khi chạm bia. Vật cản phía trước chặn tên riêng. Hai dấu lá đứng yên tại điểm đặt cho đến khi tan.

Chạy `ClientGodot/Run_Preview.ps1 -LinhCungPractice -Test` để kiểm quãng lùi, tường trước và sau, bờ sông, mốc bắn, phím 5 và nút HUD. Ảnh và kết quả được lưu ở `Implementation/Reports/Evidence/Phi_Diep_Practice_20261118e`.

Sát thương trực tuyến, tiêu hao 12 MP, hồi chiêu 9 giây và tín hiệu `RETREAT_ARROW_STATE` còn cần nối với máy chủ.

## Kiểm hình

Godot Movie Maker ghi ở nhịp cố định 60 FPS. Bài kiểm đọc đủ 1.800 frame nguồn và 960 frame ghép, gồm tám hướng lùi đủ cùng hai ví dụ lùi ngắn Đông và Tây Bắc. Mỗi bản phát đủ các pha thân, hai dấu lá và mũi tên. `native_audit.json` ghim nguồn và bản ghi theo mã băm.

1. Chạy `python Tools/ArtProduction/prepare_linh_cung_phi_diep.py` để đo điểm neo và tạo project.
2. Chạy `Tools/ArtProduction/review_actor_candidates_20261116c.ps1 -Batch 20261118e` để ghi atlas nguồn.
3. Trong Movie Maker ở 60 FPS, ghi 96 frame trong `ArtStudio.tscn` với project tương ứng. Dùng `--studio-clip 0` cho lùi đủ hoặc `--studio-clip 1` cho lùi ngắn. Thêm `--studio-play --studio-clean-view --studio-trace-layers`.
4. Chạy `python Tools/ArtProduction/audit_linh_cung_phi_diep.py` để đối chiếu mốc, pha và video.
