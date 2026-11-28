# Bàn giao asset/animation/VFX — 12/11/2026

Đã tiếp tục hướng sprite sheet chibi nguyên khối được chủ dự án chốt, tạo/chọn **14 PNG mới** và lưu prompt thực bằng image_gen tích hợp. 46 PNG cũ giữ nguyên byte. Nguồn mới: 568 ô, trong đó 560 ô gắn vào 35 chuỗi × 16 khung; 8 ô dư không dùng. Hai bản thử mới bị thay nằm ở Rejections, không lẫn danh sách đang nạp.

Minh Kiếm có thêm hurt/dodge/death đủ tham chiếu 8 hướng (5 góc vẽ + 3 lật hợp policy); Thạch Chùy sửa đánh thường bị cắt; Cá Linh thêm locomotion; Rễ Nước và Kẻ Rình Bờ thêm pilot S; Người Giữ Thuyền có idle đủ hướng ghép từ 2 sheet; ba thành phần VFX là cung kiếm, mũi tên lá và decal vết nứt. `batch_20261112.json` là danh mục chi tiết/hash/prompt/nguồn/runtime của toàn bộ đợt.

## Client và công cụ

- Kiếm Trận của SkillVfxPlayer dùng cung nguồn 16 khung đã kiểm native, ba nhịp đỉnh 0,10/0,22/0,36 giây; giữ cast token, cancel, budget và toàn bộ gameplay/server decisions. Chỉ approve component cung, gắn với hash đúng PNG đã xem. Đổi ảnh nguồn sẽ không tự kế thừa phê duyệt; runtime cũng kiểm hash trước khi chọn mới và có fallback cũ.
- Studio có 84 entry/group sau khi thêm nhóm actor/action; các sheet hướng riêng được tham chiếu, không ghép/vẽ lại PNG. Có demo 3 cung, clip one-shot mặc định cho hurt/death/dodge/attack, source VFX nhận đúng loại và pivot tâm ô.
- Pipeline phản ánh direction thiếu và các ô dư thật; không tính mirror thành góc vẽ mới hoặc component thành full skill. Audit gốc pin vào snapshot 46 PNG đã chốt để lần thêm ảnh sau không làm thay baseline.
- Gallery đứng khung ghi không đo FPS; video là preview offline có time step cố định, không phải benchmark gameplay.

## Kiểm tra

| Kiểm tra | Kết quả |
|---|---:|
| .NET 8 build | 0 warning / 0 error |
| Studio native — 84 entry/group | 41.676 assertions đạt |
| Actor library native, texture/frame/reference/gate | 11.253 assertions đạt |
| Runtime VFX component, timing/duplicate/rotation/budget/cancel | 14 assertions đạt |
| Client visual regression | 15 assertions đạt |
| Directional coverage regressions | 8 test đạt |
| PNG gốc theo snapshot | 46/46 hash không đổi |
| PNG runtime được chọn | 46/46 khớp nguồn |

Native screenshot và video đặt tại `Evidence/Actor_Batch_20261112`. Build/capture trên Godot .NET 4.7.2, .NET 8, Compatibility/OpenGL 3.3, GeForce 820M. Video 2 giây do Movie Maker xuất 120 khung và ffmpeg chuyển H.264; không dùng encoder để sửa ảnh nguồn. Không lấy concept làm screenshot.

## Phần chưa khép

Job đủ source directions tăng **32 → 38/1008**, còn **970 job**. Có 3 atlas cũ lỗi cấu trúc, 15 HOLD chất lượng và nhiều pose/motion cần biên tập. Ngoài cung kiếm, nguồn mới vẫn là candidate đang review, không tự approve full actor hoặc full skill. Nguồn trúng đòn/né/gục mới chưa tự thay toàn bộ renderer nhân vật gameplay; Studio/batch chuẩn bị dữ liệu để review/gắn theo ID khi đủ acceptance. Skill body choreography cho sáu kỹ năng Minh Kiếm còn thiếu.

VFX runtime và hash gate được kiểm trên client chạy từ source hiện hành. Export đóng gói shipping phải giữ file PNG component để xác minh hash, hoặc bổ sung cách xác minh resource đã import rồi test export; chưa nghiệm thu PCK/release trong đợt này. Những phần này nằm ngoài kết quả asset batch hiện tại, không được ghi game production-ready.

Hướng dẫn mở các nhóm/nguồn: `docs/production/Actor_Batch_20261112_vi.md`.
