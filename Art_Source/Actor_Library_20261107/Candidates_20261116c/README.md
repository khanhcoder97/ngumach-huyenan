# Thạch Chùy — bản lưu tiến độ 41/50 sheet

Cập nhật 17/11/2026. Đây là gói nguồn đang dựng và kiểm tra trong Studio. Toàn bộ thư viện asset game tiếp tục phát triển; 50 sheet của gói này chỉ bao phủ sáu kỹ năng Thạch Chùy.

| Thành phần hiện có | Sheet | Pose nguồn |
| --- | ---: | ---: |
| Trấn Sơn — N, NE, E, SE, S | 5 | 80 |
| Chấn Địa — N, NE, E, SE, S | 5 | 80 |
| Thiết Bích — N, NE, E, SE, S | 5 | 80 |
| Khiêu Chiến — N, NE, E, SE, S, chưa nghiệm thu | 5 | 80 |
| Phá Nham — N, NE, E, SE, S, còn hold hướng/root | 5 | 80 |
| VFX Trấn Sơn: chuẩn bị, vết nứt, bụi lắng | 3 | 48 |
| VFX Chấn Địa: vòng chuẩn bị, sóng chấn động, bụi tan | 3 | 48 |
| VFX Thiết Bích: hình thành, duy trì, lớp nứt, tan vỡ | 4 | 64 |
| VFX Khiêu Chiến: sóng âm, chevron mục tiêu, trạng thái | 3 | 48 |
| VFX Phá Nham: bụi kéo, va trúng, bụi dừng | 3 | 48 |
| Tổng nguồn được chọn | **41** | **656** |

`candidate_manifest.json` xác định 41 nguồn hiện hành và giữ sáu phiên bản cũ trong `history`. Mỗi PNG có prompt `.txt` đi kèm. Nguồn được tạo bằng công cụ image_gen tích hợp; PNG được sao chép nguyên byte. `Jobs/` và `production_job_plan.json` chứa đủ 50 tác vụ, phân biệt rõ nguồn đã tạo với nguồn chưa tạo. Khiêu Chiến E/SE còn chờ sửa biểu cảm gọi; Phá Nham cần kiểm tra/sửa trục hướng Bắc và root pha lao. Đủ ô nguồn không có nghĩa là nguồn đã đạt yêu cầu.

## Xem và chỉnh trong Studio

Mở Sprite & VFX Studio, chọn **Mở JSON**, rồi chọn một project trong:

`Implementation/Reports/Evidence/Actor_Batch_20261116c/Candidate_Studio/<ID>/project.json`

Ví dụ: `class_thach_chuy_skill_03_s` để xem thế trụ Thiết Bích; `sk_tc_03_plate_sustain_component` để xem vòng lặp phiến giáp. Các project dùng đường dẫn texture tương đối và PNG gốc trong `textures/`. Khi lấy repo trên máy khác, chạy `git lfs pull` để nhận đủ ảnh/video.

Có thể chỉnh tọa độ, pivot, lớp Z, góc, tỷ lệ và thời lượng từng key trong Studio. Các chỉnh sửa này phục vụ bản xem trước; bản lưu hiện tại chưa đưa nguồn C vào catalogue gameplay. Các nguồn nhân vật vẫn là sprite nguyên khối theo lựa chọn đã chốt.

## Quy tắc giáp đá Thiết Bích

Mỗi sheet VFX giáp chứa **một phiến**. Prefab cần ba instance độc lập tại `guard_shoulder`, `back`, `guard_knee`, với tọa độ và thứ tự trước/sau điều chỉnh theo hướng nhìn và pose. Phiến ở phía lưng có thể bị thân người che khuất. Ưu tiên giữ mặt, tay cầm chùy và dấu báo nguy hiểm đọc được.

Gain nối sang sustain; sustain chỉ lặp khi trạng thái buff còn hiệu lực; lớp nứt và end nối theo trạng thái kết thúc. Các thời lượng nguồn 0,48 / 1,28 / 0,40 / 0,40 giây là thời lượng xem artwork. Thời gian buff và giảm sát thương vẫn theo thiết kế/server. Giới hạn module 96 px tại 20 PPU phải kiểm tra khi ghép thực tế.

Đã có bản ghép thử hướng Nam tại `Implementation/Reports/Evidence/Actor_Assembly_20261117a/ThietBich_S_trial1/project.json`: 13 layer, ba socket, bốn pha VFX. Bản thử dùng gốc footprint cố định cho lớp nứt/end; 12 ảnh trích native đã được xem. Bản thử giữ pose cuối sau khi kích hoạt để xem hiệu ứng; cần thay bằng idle thật khi tích hợp. Tám hướng, toàn bộ pha theo từng socket và camera gameplay vẫn chưa được nghiệm thu.

## Bằng chứng và phần tiếp theo

- 41 bản quay Godot, đủ 16 pose mỗi nguồn; 7.380 frame video giải mã được.
- Vòng lặp sustain Thiết Bích và trạng thái Khiêu Chiến đã xem mối nối thực tế 14 → 15 → 0 → 1.
- 119 test công cụ đã chạy qua. Báo cáo và ghi chú hình ảnh nằm trong `Implementation/Reports/Evidence/Actor_Batch_20261116c/`.
- Chưa áp dụng phê duyệt nguồn C; catalogue và PNG runtime hiện hành giữ nguyên.

Còn chín nguồn Sơn Thần Giáng Thế: năm sheet nhân vật, bốn VFX. Tiếp tục sửa các hold đã ghi và kiểm tra root/neutral ở camera cố định. `native_media_audit.current.json` và `capture_sample_plan.current.json` phản ánh mốc mới; báo cáo pilot và các tài liệu Checkpoint25/33 giữ bằng chứng của mốc trước. Tiếp tục kiểm tra đủ tám hướng, chuyển về idle, tỷ lệ ở camera gameplay rộng, lớp che khuất và cue từ gameplay. Frame nguồn và video xuất theo clock 60 FPS chưa chứng minh FPS thực tế của game trên máy người chơi.
