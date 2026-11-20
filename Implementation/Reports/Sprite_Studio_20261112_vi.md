# Trả về sprite cũ và công cụ chỉnh tay — 12/11/2026

Chủ dự án hủy hướng nhân vật paper-doll mới trong lúc đang triển khai. Kết quả cuối cùng dùng sprite sheet nguyên khối cũ, mặc định Lý An. Không đưa ảnh base/trang phục/kiếm mới vào runtime hoặc commit đợt này. Nguồn thử đã sinh được lưu riêng tại `D:\Project\NGUMACHHUYENAN-tools\archive\Cancelled_Scholar_Chibi_20261112` cùng prompt, không được dùng làm mỹ thuật hiện hành.

## Kiểm tra nguồn cũ

`Tools/ArtProduction/audit_sprite_restore.py` so sánh PNG hiện tại với Git LFS SHA256 của các file có sẵn trong HEAD, decode ảnh và đối chiếu bản runtime với nguồn đã chọn:

| Hạng mục | Kết quả |
|---|---:|
| PNG có sẵn trong Sheets | 46/46 |
| Khớp hash nguồn gốc trong Git | 46/46 |
| PNG thật đọc được | 46/46 |
| File chỉ là LFS pointer | 0 |
| Nguồn generation_records bị thiếu | 0 |
| Runtime PNG đang được manifest chọn, khớp nguồn | 32/32 |
| Class / quái / NPC / VFX (gồm bản cũ và biến thể) | 24 / 7 / 5 / 10 |

Đây là xác nhận không mất các file cũ trong thư mục, không phải 46 sheet đều đã được duyệt. Có cả phiên bản đã bị thay thế. Bộ Minh Kiếm legacy nằm ở `Art_Source/Motion_16F_20261106` và runtime `assets/motion16`, được studio liên kết riêng.

## Phần đã làm

- `Run_Art_Studio.ps1` mở studio native Godot; launcher paper-doll cũ mặc định cũng chuyển sang studio này. Các prototype vẫn truy cập được bằng cờ rõ ràng để hồi quy, không là art mặc định.
- Adapter nạp crop không đều, pivot, nguồn frame và mirror từ metadata cũ. 36 mục mở được (actor/VFX pages và 4 action Minh Kiếm motion16); không bịa sheet cho entity chưa có.
- Xem/phát từng clip và hướng, timeline thumbnail, key và marker, scrub/step, speed, renderer 30/60, onion, grid, zoom/pan/fit.
- Chỉnh layer, crop, X/Y, pivot, scale hai trục, góc, alpha, Z, lật bằng dấu scale; import PNG, nhân/xóa/ẩn/khóa; undo/redo có nhóm kéo thả.
- Animation có duration từng frame, loop/one-shot, key theo layer, step/interpolate, copy/paste key, nhân/xóa/resize clip.
- Socket actor/layer, attach đồ/VFX, chống cycle. VFX preset hoặc PNG nhập tay, range bắt đầu/kết thúc và số vòng sheet. Marker vị trí/radius/frame cho cue SFX, footstep, VFX, hitbox.
- JSON v1 có validate và backup. Export bundle chép PNG nguyên byte theo SHA256; mở lại được với root tương đối. Dùng chung sampler cho preview và bundle; chưa tự áp vào gameplay.
- Catalogue/job trở lại baked sprite; bỏ trạng thái reference-only do chuyển modular, giữ các HOLD về chất lượng có thật. Không tự approve class candidate.

## Kiểm chứng và giới hạn

Build .NET 8: **0 warning / 0 error**. Launcher thật `Run_Art_Studio.ps1 -SelfTest`: **7.582 kiểm tra đạt**, nạp/kiểm texture 36 mục và test inspector/drag/undo, frame-time, key, socket, input không hợp lệ, import/save/backup/portable export. Capture trực tiếp Godot Compatibility trên GeForce 820M; ảnh bằng chứng ở thư mục Evidence, không phải concept.

Kế hoạch/metadata actor được tái sinh và check; kiểm tra nguồn xác nhận 46 PNG không đổi. Renderer giới hạn 60 FPS là mục tiêu xem; chưa dùng kết quả này để chứng nhận FPS client MMO nhiều người.

Các source cũ vẫn còn 4 trang bị loại về cấu trúc và 15 trang HOLD chất lượng. Coverage toàn game vẫn 1008 page cần làm, 976 pending, 3 page legacy production-approved. Studio không vẽ pose mới, sửa giải phẫu bên trong PNG, dựng map, phát file SFX hoặc tạo ra equipment layering từ sprite đã vẽ liền. Các mốc hitbox chỉ là trình bày, không đổi gameplay/server damage. Chuẩn 16–20 pose nguồn/8 hướng/render 60 FPS giữ nguyên.

Hướng dẫn thao tác và format: `docs/production/Sprite_Studio_20261112_vi.md`.
