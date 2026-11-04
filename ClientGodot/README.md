# Godot client — Bến Mưa local alpha

Godot 4.7.2 .NET, .NET SDK 8; Compatibility renderer. Có hai chế độ riêng:

- **Chơi online local:** nhấp đôi Choi_Ben_Mua.cmd, hoặc chạy Run_Playable_Alpha.ps1. Script build client SDK8/server SDK10, khởi động server loopback riêng, kiểm health + PID, mở game và dừng đúng server mình tạo khi đóng game. Chưa có gói export độc lập SDK.
- **Xem art offline:** chạy Run_Preview.ps1. Không cấp quest, tiền, damage hoặc vật phẩm. F2 đổi tầm nhìn; phím 1–6 thử sáu VFX Minh Kiếm, Space thử animation tấn công.

## Điều khiển bản online local

WASD/mũi tên di chuyển; E nói chuyện/nhặt đồ gần; I mở/đóng túi; Tab chọn mục tiêu; Space đánh; 1–3 gọi kỹ năng thực mà client/server hiện hỗ trợ. Phím 4–6 trong online trả trạng thái chưa hỗ trợ. R thử lại thao tác chưa rõ kết quả. Esc đóng panel rồi đóng game. F6 giảm số hiệu ứng. Hội thoại chặn di chuyển. Lật trang/lựa chọn hỏi thêm không nhận quest hoặc thưởng; phải nhấn hành động cuối và đợi server xác nhận.

Tuyến đã kiểm: P00-01, gặp Ly An, nhận nhiệm vụ, nhặt ba kiện hàng, trả Tạ Vân Khanh, đọc túi với đúng 20 COIN + một EQ-MK-CHEST-T1-R-COMMON. Tên, thoại, inventory/HP/MP/quest lấy nguồn thực; không giả level/XP hoặc cấp thưởng ở client. Mất reply sau turn-in giữ cùng body/key để retry, không thưởng lần hai. Đây là **slice mở đầu**, chưa chứng nhận toàn tutorial/campaign/MMORPG.

MobBehavior và DeathReturn OFF trong launcher hiện tại; enemy không tự đuổi/đánh lại. Server damage/combat/quest routes bật chỉ trong tiến trình local của launcher. Chưa có online death-return/equip12slot/trading/guild/campaign hoàn chỉnh. Không đổi appsettings production.

## Camera, map và art

Camera top-down orthographic, mặc định 64×36 WU; F2 chọn 48×27 WU. Viewport 1280×720, 20 px/WU, nearest + integer scaling/letterbox. HUD ngoài camera, sáu ô kỹ năng theo vòng cung quanh ĐÁNH. Phím H ẩn HUD.

Art staging ART_BM_STAGING_A2 là 128×96 WU, 113 placement/14 tuyến, sông cong và cầu tàu có collision offline. **Canonical MAP_BEN_MUA hiện vẫn x0..360, y−12..72 (360×84 WU)**. Bản online dùng transform render=(920+20*x,896−20*y), server quyết định vị trí/nav; ngoài district authored chỉ mở rộng grass backdrop. Không coi staging hay backdrop là migration map 2D đã nghiệm thu. Toàn bản đồ/nav đang chờ packet Qoder.

Nguồn mới: Art_Source/Visual_Reboot_20261104, BenMua_Concept_Rebuild_20261105, Combat_Visuals_20261105. Không dùng concept làm nền hoặc cắt concept thành sprite. Whole-body walk/attack tám hướng có metadata riêng; vũ khí hiện chỉ xuất hiện trong attack, chưa là equipment-layer system. Sáu VFX Minh Kiếm là presentation candidate; các lớp khác chưa có đủ animation/VFX. CARPLING/WATERROOT có idle/attack/dead, chưa eight-direction creature animation. NPC khác ngoài ba người được vẽ mới còn archetype tạm; nhóm quái mixed không tự gán sai species.

## Kiểm chứng

- Run_Playable_Alpha.ps1 -Test: native Godot + HTTP P00-01, mất reply/retry/owner isolation, screenshot inventory.
- Run_Playable_Alpha.ps1 -UiTest: native hội thoại/button signals + HTTP nhận/làm/trả nhiệm vụ; không phải physical pointer automation.
- dotnet restore VisualReboot.csproj --locked-mode; dotnet build VisualReboot.csproj --no-restore.
- godot --headless --editor --path . --quit
- godot --headless --path . -- --camera-self-test
- godot --headless --path . -- --scene-self-test
- godot --headless --path . -- --visual-self-test
- godot --path . -- --vfx-review --capture <absolute.png>: gallery đóng băng keyframe để review, không phải timeline chơi thật.

Bằng chứng native, source prompt và báo cáo trong Implementation/Reports/Evidence/Playable_Alpha_20261105. Máy hiện tại có Godot/SDK portable ở thư mục NGUMACHHUYENAN-tools cạnh repo; máy khác truyền -GodotPath/-Dotnet8Path/-Dotnet10Path. Không cần Unity.
