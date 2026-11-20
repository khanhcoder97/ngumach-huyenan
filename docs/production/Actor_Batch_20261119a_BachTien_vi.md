# Bách Tiễn Quy Tông của Linh Cung

Tuyệt kỹ dùng ô 6. Linh Cung giữ chân trên đất, nâng cung lên cao, mở tay nhả ở khung 9 rồi hạ cung. Tám hướng dùng sprite riêng, mỗi hướng 16 tư thế pixel chibi. Ba atlas hiệu ứng riêng gồm vòng rêu viền vàng có ba ký hiệu mũi tên, tên rơi thẳng xuống và mảnh lá chạm đất. PNG gốc và prompt ImageGen lưu cạnh manifest.

## Mốc hoạt ảnh

| Mốc | Từ lúc chốt tâm |
| --- | ---: |
| Vòng báo mở | 0 ms |
| Nhả cung lên cao | 640 ms |
| Bốn đợt bắt đầu rơi | 1.200, 1.400, 1.600, 1.800 ms |
| Bốn đợt chạm đất | 1.340, 1.540, 1.740, 1.940 ms |

Vòng báo giữ nguyên tâm và khẩu độ trong 1,2 giây. Mỗi đợt có sáu tên, với ba tên chính để giữ nhịp ở chế độ VFX nhẹ. Mảnh lá có điểm neo riêng tại chỗ chạm và tan dần sau đợt cuối. Pha tiếp xúc của tên là ô 7, đếm từ 0.

## Chỉnh tay trong Sprite & VFX Studio

Mở `Implementation/Reports/Evidence/Actor_Batch_20261119a/BachTien/<hướng>/project.json`. Mỗi project có 35 lớp. Chọn lớp vòng, tên hoặc mảnh lá để chỉnh điểm neo, độ cao và vị trí điểm rơi. Dùng mốc `wave_1_drop` đến `wave_4_contact` để soát timing. Vùng và bia trong Studio phục vụ kiểm hình.

## Chơi thử tại Bến Mưa

Chạy `ClientGodot/Run_Preview.ps1 -LinhCungPractice`. Nhấn **6** hoặc bấm ô vòng ba mũi tên. Chọn tâm trên đất trong tầm 12 m. Nhấn **Esc** hoặc chuột phải để hủy. Vòng báo chốt tại vị trí đó với bán kính 6 m.

Vật cản và mặt nước có thể khiến điểm đặt bị từ chối. Mỗi đợt ghi nhận tối đa tám mục tiêu thường trong vòng, ưu tiên các mục tiêu gần tâm. Hệ số thử 75% mỗi đợt, tổng 300% nếu bia đứng trong vòng đủ bốn đợt. Bài kiểm gia cường nạp sẵn ba Mộc Tiêu cho cảnh cục bộ. Sau khi chốt tâm, cảnh kiểm tiêu ba điểm, thêm ba vạch sáng tại tâm và ghi hệ số 90% mỗi đợt. Bán kính và lịch mưa giữ nguyên. Chế độ VFX nhẹ giữ vòng và bốn đợt, giảm tên phụ và mảnh lá.

Bản hiện tại là khu luyện ngoại tuyến. Tích Mộc Tiêu qua đánh thường, sát thương trực tuyến, chi phí 40 MP, hồi chiêu 65 giây và tín hiệu `ARROW_RAIN_STATE` còn cần nối với máy chủ.

Godot đã qua 58 xác nhận Bách Tiễn trong cảnh có giao diện. Ảnh và dữ liệu đo lưu ở `Implementation/Reports/Evidence/Bach_Tien_Practice_20261119a`. Kiểm hình ở khung đầu cũng xác nhận nhân vật giữ đúng kích thước khi chuyển từ atlas đứng sang atlas giương cung.

## Tái lập kiểm hình

1. Chạy `python Tools/ArtProduction/prepare_linh_cung_bach_tien.py` để tạo project từ PNG gốc. Các hướng Đông, Tây Nam và Tây Bắc dùng đường chia ô đo từ khe trong suốt.
2. Chạy `Tools/ArtProduction/review_actor_candidates_20261116c.ps1 -Batch 20261119a` để ghi 11 atlas nguồn.
3. Ghi 156 frame mỗi hướng ở 60 FPS trong `ArtStudio.tscn`. Dùng `--studio-project`, `--studio-direction`, `--studio-play --studio-clean-view --studio-trace-layers`. Lưu `preview.mp4` và `preview.godot.log` cạnh project.
4. Chạy `python Tools/ArtProduction/audit_linh_cung_bach_tien.py` để kiểm 176 tư thế hoặc pha nguồn, thứ tự bốn đợt, điểm chạm và mã băm.
5. Chạy `ClientGodot/Run_Preview.ps1 -LinhCungPractice -Test` để kiểm nút HUD, hủy chọn vùng, tầm chọn, nước, mốc mưa, giới hạn mục tiêu và hình ảnh gia cường.
