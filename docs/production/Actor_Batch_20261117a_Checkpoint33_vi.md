# Mốc 33 nguồn Thạch Chùy và bản ghép Thiết Bích hướng Nam

Ngày 17/11/2026. Mốc này bổ sung tám nguồn vào gói 50 sheet: năm hướng Khiêu Chiến và ba component sóng âm, chevron, trạng thái mục tiêu. Tổng hiện hành 33 sheet, 528 pose/pha nguồn, 39 phiên bản kể cả sáu nguồn đã thay thế. Mọi nguồn mới vẫn là candidate; chưa áp dụng phê duyệt hoặc thay catalogue/runtime gameplay.

## Artwork và các điểm cần sửa

Nhân vật dùng sprite nguyên khối với 16 hình trong bố cục 4×4. Ảnh gốc và prompt được lưu nguyên vẹn. Khiêu Chiến có một lần gõ chùy nhẹ, nâng đầu/ngực gọi rồi trở lại tư thế sẵn sàng. Biểu cảm gọi ở E và SE hiện còn yếu, miệng đóng; hai hướng này được giữ trạng thái chờ sửa. Hướng N cần kiểm tra yaw chính xác; NE có pivot gắn SHA riêng vì bộ dò màu bỏ sót viền giày tối. Các pivot này là đề xuất đăng ký để xem thử, chưa chứng minh root ổn định trong gameplay.

Sóng âm v1 bị loại vì trông như bệ đá; v2 dùng vòng nét mỏng, tâm rỗng, vỡ thành vài nét ngắn rồi tan. Chevron v1 bị loại vì có đá vụn và nhiều mũi tên; v2 dùng một dấu chỉ hướng sạch. Hai v1 vẫn được giữ trong lịch sử. Biểu tượng trạng thái là chùy nhỏ và dấu nhấn, chuyển sáng nhẹ theo vòng lặp. Tâm hình từng pha đã được đăng ký để không trôi giữa các hàng nguồn.

## Bản ghép Thiết Bích để chỉnh tay

Mở `Implementation/Reports/Evidence/Actor_Assembly_20261117a/ThietBich_S_trial1/project.json` trong Studio. Project có 13 layer: một nhân vật và bốn pha VFX tại ba socket `guard_shoulder`, `back`, `guard_knee`. Có thể chỉnh tọa độ, pivot, tỷ lệ, góc, Z và thời gian từng layer bằng tool hiện hữu.

Clock xem thử dài 3,04 giây, gồm 75 đoạn để đồng bộ các layer. Nhân vật vẫn chỉ có 16 pose nguồn, sau đó giữ pose cuối để xem giáp; 75 đoạn không phải 75 frame vẽ nhân vật. Gain nối sustain, lớp nứt chạy trên sustain rồi end làm lộ giáp kim loại bên dưới. Crack/end dùng footprint của phiến cha thay vì tâm vệt nứt đang lớn dần. 12 ảnh trích native đã được xem; vai/gối bám được bề mặt phía trước, phiến lưng bị thân che trong hướng Nam.

Tùy chọn Studio `--studio-fixed-view` giữ zoom 1× và gốc thống nhất; `--studio-clean-view` tắt lưới; `--studio-trace-layers` ghi source frame của layer đang hoạt động khi xuất movie. Trace không chứng minh layer lưng bị che có pixel nhìn thấy, và không thay cho kiểm tra hình ảnh.

## Bằng chứng và giới hạn

| Kiểm tra | Mốc hiện tại |
| --- | ---: |
| Source / pose-pha nguồn | 33 / 528 |
| Project / native video nguồn | 33 / 33 |
| Frame video nguồn giải mã | 5.940 |
| Loop đã xem 14 → 15 → 0 → 1 | 2 nguồn |
| Test công cụ | 119 qua |
| Build Godot .NET | 0 lỗi, 0 cảnh báo |
| Source C đã phê duyệt cho runtime | 0 |

`native_media_audit.current.json` đối chiếu receipt, mã băm PNG/project/movie, trace đủ 16 phase và giải mã từng video. `manual_review_observations.json` ghi nhận xét gắn đúng PNG, project, movie và montage. `manual_visual_review.json` bên bản ghép Thiết Bích giới hạn kết luận ở 12 mẫu hướng Nam. Báo cáo pilot/Checkpoint25 vẫn là bằng chứng lịch sử của mốc trước.

Còn 17 nguồn của Phá Nham và Sơn Thần Giáng Thế; còn sửa các hold đã ghi, kiểm tra idle–action, tám hướng, che khuất tay/mặt, tỷ lệ camera rộng và cue trạng thái từ server. Clock video cố định 60 FPS không đo FPS gameplay trên máy yếu. Thời gian demo, vòng lặp glyph và giữ pose cuối không quyết định thời gian buff, sát thương, va chạm hoặc AI quái.

Gói 50 nguồn này là một phần của thư viện game. Các lớp khác, quái, boss, NPC, hành động, biến thể, map và UI vẫn thuộc phạm vi công việc đang tiếp tục.
