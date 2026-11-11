# Hướng nhân vật và Sprite/VFX Studio — 12/11/2026

## Quyết định hiện hành của chủ dự án

Hủy hướng vẽ nhân vật base/paper-doll mới. Quay lại **sprite sheet chibi nguyên khối đã tạo trước đây**, theo mẫu Lý An do chủ dự án gửi. Giữ và phát triển studio để xem, chỉnh tay, phát lại animation/VFX từ ảnh nguồn có sẵn.

Quyết định này thay hướng mỹ thuật tại `Restored_Pixel_Style_20261110_vi.md` và hướng production modular trong các tài liệu ngày 07–10/11. Các prototype/nguồn cũ được giữ làm lịch sử, không còn là màn mặc định. Không xóa inventory slot, item hay chỉ số equipment. Chưa triển khai thay đồ trực tiếp bằng layer quần áo; sprite nguyên khối mang ngoại hình đã vẽ sẵn.

Chuẩn **16–20 pose vẽ thực/hành động/hướng**, 8 hướng theo policy, và renderer mục tiêu **60 FPS** vẫn giữ. Hướng lật ngang trong nguồn cũ được ghi rõ trên màn xem; đây không phải hướng vẽ mới. Việc quay lại phong cách cũ không tự nghiệm thu toàn bộ sheet hoặc gỡ visual HOLD của các clip đang lỗi.

## Mở studio

Từ thư mục repo/worktree chứa thay đổi:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\ClientGodot\Run_Art_Studio.ps1
```

Lần đầu script build .NET 8 và import Godot. Sau đó có thể dùng `-SkipBuild`. Portable Godot/.NET mặc định ở thư mục anh em `NGUMACHHUYENAN-tools`; có thể chỉ định `-GodotPath`, `-DotnetPath`.

`Run_PaperDoll_Lab.ps1` cũng mở studio mới mặc định. Scene `PaperDollLab.tscn` và `PaperDollArtReview.tscn` vào trực tiếp sẽ chuyển sang studio. Các cờ self-test hoặc `-FitTools`, `-ArchivedArtReview` chỉ mở prototype lịch sử khi yêu cầu rõ.

Mặc định: `npc_lyan_idle`, hướng S, nguồn `actor_library_v1/sheets/npc_lyan_idle_v2.png`, đúng phong cách sheet tham chiếu. Thư viện có 36 mục hiện có: các page actor/VFX đã xuất và 4 bộ Minh Kiếm `motion16`. Đây là phạm vi ảnh sẵn có, **không phải đã có đủ mọi NPC/quái/hành động của toàn game**.

## Quy trình chỉnh tay

1. Chọn sheet trong **Thư viện sprite cũ** → **Mở mẫu đã chọn**. Chọn clip/hướng bên dưới. Sheet đang chỉnh có thay đổi chưa lưu sẽ hiện cảnh báo trước khi thay nguồn.
2. Nhấn **Phát**, Space, hoặc kéo timeline. Dải thumbnail có thể cuộn và nhấp từng frame; chấm vàng là key, vạch hồng là mốc. ←/→ đi từng frame. Tốc độ ×0.1–4 chỉ thay tốc độ xem; 60/30 FPS giới hạn renderer. Muốn lưu tốc độ, chỉnh `ms/frame` ở tab Anim.
3. Tab **Layer**: bật/tắt, khóa, Z, X/Y, pivot, scale X/Y độc lập (âm để lật), góc, opacity, source frame. Bật **Chỉnh KEY** để sửa riêng frame; tắt để sửa pose nền. Clip đã có key dùng key thay vì pose nền.
4. Trên sân khấu: chuột trái kéo layer, pivot, socket hoặc mốc theo chế độ đang chọn; giữ Ctrl căn delta theo đơn vị; cuộn để zoom theo con trỏ, chuột giữa để pan, Fit để đặt lại. Grid, gốc bàn chân, biên ảnh và onion trước/sau giúp đối chiếu.
5. Tab **Sheet**: xem ảnh gốc; sửa crop của vùng hiện tại; nhập/thay PNG; tạo grid mới cho sheet ô bằng nhau; gán dãy vùng ảnh vào clip. Sheet cũ dùng crop không đều đã đo, không tự cắt lại bằng grid mới khi mở.
6. Tab **Anim**: tên/hướng, số ô timeline, ms từng frame hoặc toàn clip, loop/one-shot, nội suy transform hay step, đặt/xóa/copy/paste key, nhân/xóa clip. Nhân clip chỉ tạo bản để chỉnh, không sinh pose hoặc góc nhìn mới.
7. Tab **Neo**: đặt socket vào layer hoặc không gian nhân vật. Socket layer dùng pixel trong vùng crop, theo pivot/transform/key của layer đó. Layer con gắn qua tab Layer. Không cho phép chu trình neo. Chỉnh điểm cầm kiếm/VFX chỉ có tác dụng với layer riêng được nhập vào; không thể dời kiếm đã vẽ liền trong sprite.
8. Tab **VFX/Mốc**: thêm VFX cũ ở cột trái hoặc nhập PNG và đánh dấu layer là VFX; chỉnh vị trí/góc/scale như layer; đặt frame bắt đầu/kết thúc và số vòng chạy sheet, gán thành key. Mốc `sfx`, `footstep`, `vfx`, `hitbox` ghi frame, tọa độ, bán kính để preview/log. Mốc không gây damage, không phát file âm thanh ở phiên bản này.
9. **Lưu / Lưu thành** giữ JSON riêng. **Xuất bundle** tạo JSON cùng `textures/<sha256>.png` byte-identical với nguồn để chuyển máy. **Mở JSON** nạp được bundle; `-Project <path>` mở từ launcher. Tab Xuất có báo cáo nguồn và mở thư mục bản lưu.

## Dữ liệu và khả năng dùng trong game

Format v1: `ArtStudioDocument`, `scope=PRESENTATION_AUTHORING_ONLY`, `productionApproved=false`. Các lớp định nghĩa trong `ArtStudioModel.cs`; `ArtStudioSampler` dùng chung để đọc frame theo thời gian, key, pivot, transform, attachment và mốc. `ArtStudioCanvas` đang dùng chính sampler đó để preview. Không có một sampler giả riêng chỉ phục vụ demo.

Mỗi layer tham chiếu PNG gốc + danh sách rect, pose nền, Z, visibility và socket. Mỗi clip có direction, duration từng frame, track key theo layer, mốc và provenance (`SourceNote`). Ảnh nguồn đổi theo key bằng index; bitmap không bị warp, vẽ lại hay ghi đè. Nội suy chỉ dành cho transform; đổi ảnh source và đổi dấu scale dùng step để tránh đảo qua scale=0. Source index dùng 0-based; label timeline hiển thị 1-based.

Tọa độ nhân vật: X sang phải, Y xuống; pose X/Y là actor space hoặc không gian socket cha. Pivot là pixel trong vùng crop. Socket layer là pixel trong vùng crop trước khi trừ pivot. Marker là actor space. Canvas zoom/pan không ghi vào pose và không làm đổi vị trí runtime.

PNG người dùng nhập được chép vào `user://art_studio/imports/<sha256>.png`; bản lưu mặc định `user://art_studio/projects/current.json`. Có backup `.bak`, ghi file tạm trước khi thay JSON. Import/export không chỉnh byte ảnh. Bộ nguồn trong repo không bị ghi đè.

`Mở JSON` là thao tác tường minh; studio không tự nạp bản lưu không rõ nguồn khi khởi động. Chỉ chấp nhận PNG trong `res://assets/`, vùng import của studio hoặc `textures/` tương đối trong bundle. Kiểm schema, số lượng layer/clip/frame, số hữu hạn, rect, source index, references, chu trình socket và kích thước ảnh trước khi nạp. Giới hạn 64 layer, 64 clip, 120 frame/clip, 512 rect/layer, 8192 px/cạnh PNG, 64 MB/file PNG.

Các JSON này **chưa tự gắn vào client gameplay**. Để dùng bản chỉnh cho một entity phải ánh xạ actorId/clip/direction đến bundle đã review rồi dùng sampler trong renderer; không được âm thầm áp file chỉnh NPC lên player hay sửa damage, collision, tốc độ di chuyển, inventory và slot trang bị. Export hiện vẫn `productionApproved=false`. Bộ tool này phục vụ authoring, chưa phải map editor, pixel painting app, skeletal animator hoặc hệ thống gameplay đầy đủ.

## Nghiệm thu

```powershell
.\ClientGodot\Run_Art_Studio.ps1 -SelfTest
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Capture D:\studio-preview.png
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Project D:\bundle\actor.json
```

Test kiểm đủ thư viện hiện có, crop/texture bindings, frame/time, inspector signals, drag, undo/redo, khóa/visibility, interpolation/step, socket/attachment, malformed input, resize, save/backup/import và portable export. Số vùng ảnh khác nhau chỉ là dữ liệu nguồn, không chứng nhận mọi pose đều đẹp/đúng giải phẫu. Không dùng test kỹ thuật để tự gỡ HOLD của sheet cũ.
