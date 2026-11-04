# Camera / art staging của Codex

Godot 4.7.2 .NET, .NET SDK 8; Compatibility renderer. Đây là scene kiểm camera/map/art mới, **chưa phải client gameplay online hoàn chỉnh**. Không dùng lại hình Muse. Không dùng concept làm nền map hoặc cắt concept làm sprite.

- Mở project.godot bằng Godot .NET, Build, Run.
- WASD/mũi tên: di chuyển 8 hướng. F2: 64×36 WU (mặc định) / 48×27 WU. H: ẩn HUD. Esc: đóng.
- Character hiện chỉ là 8 hướng idle; chưa giả lập walk/attack bằng đổi tên frame. Preview không cấp quest/EXP/loot hoặc gọi server.
- Map ART_BM_STAGING_A1: 128×96 WU, TileMapLayer 160×120 cell ×0,8 WU, footprint riêng để thử. Không thay manifest/nav/quest coordinates của MAP_BEN_MUA.
- Viewport nội bộ1280×720,20px/WU; HUD CanvasLayer độc lập camera. Integer scaling + nearest; giữ16:9, letterbox thay vì kéo giãn. Nên xem1:1/2:1; màn nhỏ cần profile compact do người chơi chọn, không lén đổi tầm nhìn.
- Nguồn art, prompt, SHA256 và trạng thái ở Art_Source/Visual_Reboot_20261104. PNG trong assets/reboot là bản copy đúng byte; manifest có từng rect/pivot thực, không giả kích thước sheet.
- Build: dotnet restore VisualReboot.csproj --locked-mode; dotnet build VisualReboot.csproj --no-restore.
- Import: godot --headless --editor --path . --quit. Test: godot --headless --path . -- --camera-self-test.
- Native capture: godot --path . -- --capture <absolute.png> (chạy render thật, tự đóng sau capture). Thêm --clean-capture để ẩn HUD.
- Các slot HUD chỉ trình bày bố cục vòng cung để review, chưa có combat/tooltip/cooldown binding. Không gọi là UI gameplay đã nghiệm thu.

Máy hiện tại có thể chạy Run_Preview.ps1; script tự tìm bộGodot/.NET portable trong thư mục tools cạnh repo, hoặc dùng tham số -GodotPath/-DotnetPath. -Test chạy camera selftest. Không chạy server hoặc kill tiến trình khác.
