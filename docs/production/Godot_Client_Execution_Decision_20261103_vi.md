# Hướng triển khai client Godot .NET — 03/11/2026

**Cập nhật quyền sở hữu05/11:** work28 và CAM-TOPDOWN-WIDE-20261105 thay phân công Muse và camera cũ. Codex nhận toàn graphics/UIUX/VFX/animation/map và Godot runtime; Muse chỉ video/cinematic/audio. PR22/111/112 đã đóng theo lệnh chủ dự án. Các mục báo cáo tình trạng03/11 bên dưới giữ để tra cứu.

Trạng thái: quyết định điều phối hiện hành, chưa phải chứng nhận bản game đã chạy trên máy chủ dự án. Thay thế yêu cầu phát triển client Unity trong các work order cũ khi chúng mâu thuẫn với tài liệu này. Giữ lịch sử và source Unity; không xóa, di chuyển hoặc tự đóng PR #22/#51.

## Căn cứ và lựa chọn

Chủ dự án xác nhận trong chat ngày 03/11: đang giao Muse dùng Godot .NET và yêu cầu đánh giá lựa chọn thay Unity do máy yếu. Codex đã kiểm tra máy hiện tại: i3-4030U 2 nhân, khoảng 7,9 GiB RAM, Intel HD Graphics và NVIDIA GeForce 820M. Khuyến nghị tiếp tục Godot .NET cho game 2D pixel nhìn từ trên, ưu tiên bản Windows. Chưa benchmark nên không cam kết FPS hoặc dung lượng RAM thực tế.

Godot công bố native editor tối thiểu 4 GB RAM và GPU OpenGL 3.3 với Compatibility renderer. Dùng C# cần editor bản .NET cùng SDK tương thích. Tài liệu hiện hành ghi desktop được hỗ trợ; Android và iOS C# còn experimental, C# Godot 4 chưa có xuất web chính thức. Không hứa một bản web từ client này. Defold là phương án 2D dùng Lua, nhưng đổi tiếp sẽ tăng chi phí viết lại client; không mở tuyến thay engine thứ ba lúc này.

Nguồn chính thức, kiểm tra 03/11/2026:

- https://docs.godotengine.org/en/stable/about/system_requirements.html
- https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/index.html
- https://godotengine.org/download/archive/4.7.2-stable/
- https://defold.com/manuals/introduction/

Godot **4.7.2 stable .NET** là baseline giao nhận theo PR #107; đây là phiên bản engine, không phải .NET Framework 4.7.2. Muse phải commit project/SDK target thực tế, nguồn package và lockfile để chứng minh tương thích. Không nâng 4.8 beta hoặc chuyển target SDK chỉ vì máy reviewer có .NET 10.

## Ranh giới và phân vai

| Chủ sở hữu | Phạm vi hiện hành |
|---|---|
| Muse | Chỉ video/cinematic/âm thanh, source media/subtitles/stems; không Godot code/graphics |
| OpenCode | Lõi C# độc lập engine, DTO/transport/presenter/policy/catalog và kiểm thử protocol/HTTP; giao adapter interface để Codex nối Godot |
| Qoder local | Authoritative gameplay/server, contract và profile alpha |
| Qoder remote | Persistence library, transaction, identity/fencing, outbox và phục hồi; chưa được nối Health trước nghiệm thu |
| Codex | Toàn bộ art mới và Godot runtime/scene/HUD/camera/input/render/import/tích hợp; review và quản lý quyết định |

Work order 24 là phân công mới; work order 23 giữ hiệu lực phần server và design alpha. Antigravity vẫn không được giao lại việc.

## Tổ chức source và giao nhận

1. Dự án Godot mới đặt tại `ClientGodot/` ở root, trừ khi Muse đã có đường dẫn được chủ dự án duyệt và gửi bằng chứng. Không chép lên `Client/` Unity. Thư viện độc lập mới đặt `Shared/ClientCore/`, tests tại `Shared/ClientCore.Tests/`; OpenCode không di chuyển hàng loạt file cũ để tránh phá stack PR.
2. Bàn giao project.godot, csproj, source, scene/resource, import settings, export preset không chứa secret, package lock, giấy phép/dependency, manifest và script build. Không commit `.godot/`, bin/obj, thông tin đăng nhập hoặc private export credential. Source và các asset đã duyệt phải có đủ bytes trên Git/LFS để clone sạch chạy được.
3. Asset chưa được chủ dự án duyệt giữ DRAFT, ghi rõ dependency chưa phát hành và cung cấp review packet theo phạm vi được phép. Không tự đổi DRAFT thành production hoặc yêu cầu publish toàn bộ bản vẽ chưa duyệt. Tách source PR và asset PR khi cần. Bản thiếu dependency chỉ được gọi là bàn giao từng phần.
4. Muse gửi dự thảo DEC-024 và bảng sửa từng dòng đã nhắc trong #107. Đối chiếu với quyết định này; không thay hàng loạt mọi chữ Unity trong tài liệu lịch sử. Các câu quy định runtime mới phải trỏ Godot và giữ contract/server độc lập engine.
5. `Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json` vẫn là nguồn alpha. Không đổi tọa độ canonical, collision hoặc gắn REVIEWED vì đổi engine. Công thức đổi trục Y/đơn vị và round-trip phải có test từ map bounds thực tế, không hard-code một công thức cho mọi map.

## Hồ sơ chạy máy yếu và cửa nghiệm thu

- Renderer mặc định Compatibility; nearest/Point, không mipmap cho pixel sprites, không postprocess hoặc đèn động nặng mặc định. Giữ logical viewport/camera hiện hành; không thu nhỏ tầm nhìn để che vấn đề hiệu năng.
- TileMapLayer/chunk và culling thay cho load một ảnh khổng lồ cho mọi vùng. Giới hạn số actor render/VFX đồng thời, pooling và tùy chọn giảm hiệu ứng; không giấu telegraph sát thương. Đo FPS/frame-time, RAM/VRAM, thời gian import lạnh/ấm và startup; ghi đúng máy, build, scene, số actor. Mục tiêu alpha Windows 30 FPS ổn định ở preset thấp là mục tiêu cần đo, chưa phải kết quả.
- Build/export nặng và Android thực hiện trên VM/CI của Muse. Máy chủ dự án chỉ cần gói Windows portable cùng hướng dẫn ngắn và server riêng; không bắt cài Unity hoặc toàn bộ Android toolchain. Bản phát hành test cần .NET runtime hay self-contained phải được ghi rõ và kiểm trên máy không có SDK.
- Windows ưu tiên: clone sạch → restore/import có timeout → build → headless tests → export → chạy bản export có cửa sổ và thao tác thật. Headless pass không thay cho kiểm GPU, input, âm thanh hoặc đọc chữ tiếng Việt.
- Android chỉ ghi PASS sau khi CI tạo APK thật và có bằng chứng khởi động/thao tác trên thiết bị hoặc emulator; build thành công chưa chứng minh trải nghiệm. Không tắt test để chữa OOM. Web/iOS chưa nằm trong cam kết alpha.
- C# portable tests/HTTP pass không chứng minh scene Godot đã nối. Tương tự các job server/content xanh ở #107 không chứng minh source Godot đã bàn giao.

## Các điểm chưa được nghiệm thu

PR #107 hiện chỉ có một báo cáo, không có source Godot, scene, asset mới hay export để Codex chạy. Các số 10/10, 13/13, 31/31 và export Linux/Windows là kết quả Muse báo cáo, chưa kiểm độc lập. HUD đang ở scene test, chưa nối Main.tscn. Client 64×64, font Việt, collision nước, Android và luồng toàn chương cần hoàn thiện theo work order 24. Không gọi BM-D hoặc client alpha hoàn tất ở thời điểm này.
