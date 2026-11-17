# Thạch Chùy — 50 sheet nguồn của sáu kỹ năng

Cập nhật 18/11/2026. Gói này bao phủ sáu kỹ năng Thạch Chùy. Các bản xem và chỉnh sửa chạy trong Sprite & VFX Studio.

| Thành phần hiện có | Sheet | Pose nguồn |
| --- | ---: | ---: |
| Trấn Sơn — N, NE, E, SE, S | 5 | 80 |
| Chấn Địa — N, NE, E, SE, S | 5 | 80 |
| Thiết Bích — N, NE, E, SE, S | 5 | 80 |
| Khiêu Chiến — N, NE, E, SE, S, chưa nghiệm thu | 5 | 80 |
| Phá Nham — N, NE, E, SE, S, còn hold hướng/root | 5 | 80 |
| Sơn Thần Giáng Thế — N, NE, E, SE, S | 5 | 80 |
| VFX Trấn Sơn: chuẩn bị, vết nứt, bụi lắng | 3 | 48 |
| VFX Chấn Địa: vòng chuẩn bị, sóng chấn động, bụi tan | 3 | 48 |
| VFX Thiết Bích: hình thành, duy trì, lớp nứt, tan vỡ | 4 | 64 |
| VFX Khiêu Chiến: sóng âm, chevron mục tiêu, trạng thái | 3 | 48 |
| VFX Phá Nham: bụi kéo, va trúng, bụi dừng | 3 | 48 |
| VFX Sơn Thần Giáng Thế: báo vùng, phiến dựng, duy trì, tan | 4 | 64 |
| Tổng nguồn được chọn | **50** | **800** |

`candidate_manifest.json` xác định 50 nguồn hiện hành và giữ chín phiên bản cũ trong `history`. Mỗi PNG có prompt `.txt` đi kèm. Nguồn được tạo bằng công cụ ImageGen tích hợp và lưu nguyên byte. `Jobs/` và `production_job_plan.json` chứa thông số cho từng sheet. Khiêu Chiến E/SE v2 đã sửa biểu cảm gọi và xem lại trong Studio. Phá Nham cần sửa trục hướng Bắc và kiểm tra điểm đặt chân khi lao.

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

- 50 bản quay Godot, đủ 16 pose mỗi nguồn và 9.000 frame video giải mã được.
- Đã xem đoạn nối 14 → 15 → 0 → 1 của vòng lặp Thiết Bích, Khiêu Chiến và Sơn Thần Giáng Thế.
- 119 test công cụ đã chạy qua. Báo cáo và ghi chú hình ảnh nằm trong `Implementation/Reports/Evidence/Actor_Batch_20261116c/`.
- Chưa áp dụng phê duyệt nguồn C; catalogue và PNG runtime hiện hành giữ nguyên.

Mở `Implementation/Reports/Evidence/Actor_Assembly_20261117a/Sanctuary_TC06_v2/project.json` để xem năm hướng của Sơn Thần Giáng Thế ở cùng tỷ lệ. Ba phiến đá xuất hiện theo ba neo riêng rồi hòa vào vùng duy trì. Tâm vùng và khoảng mở phía trước dùng cùng tọa độ qua các hướng. Trục Bắc tại một số pose vẫn cần căn lại khi so với idle.

`native_media_audit.current.json` và `capture_sample_plan.current.json` ghi kết quả hiện tại. Công việc tích hợp còn phần chuyển về idle, hướng đối diện, tỷ lệ camera rộng, lớp che khuất và cue ở gameplay. Video Studio dùng đồng hồ xuất 60 FPS. Đo FPS trên map và xử lý cue máy chủ là các bước kiểm tra riêng.
