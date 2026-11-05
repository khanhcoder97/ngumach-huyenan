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

Art staging ART_BM_STAGING_A2 là 128×96 WU, 113 placement/14 tuyến, sông cong và cầu tàu có collision offline. **Canonical MAP_BEN_MUA hiện vẫn x0..360, y−12..72 (360×84 WU)**. Bản online dùng transform render=(560+20*x,896−20*y), server quyết định vị trí/nav; ngoài district authored chỉ mở rộng grass backdrop. Không coi staging hay backdrop là migration map 2D đã nghiệm thu. Toàn bản đồ/nav đang chờ packet Qoder.

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

## Tiếp nối — nhật ký và phần khám phá

J hoặc nhấp bảng nhiệm vụ để mở nhật ký. Giao diện hỗ trợ source P00-01..05 nhưng chỉ hiển thị trạng thái/counter server gửi; chặng LOCKED không lộ nội dung. Nhiệm vụ đã hoàn thành dùng đúng phần thoại sau giao nhận, không lặp lời nhắc còn thiếu đồ. Trong baseline hiện tại P00-02..05 vẫn chưa mở: PR106/109 đang được sửa sau review, không tự giả completion.

--quest-ui-self-test kiểm UI bằng source/DTO fixture, không HTTP/grant; --quest-art-review là gallery hình gợn nước/cứu dân. -UiTest đã mở rộng kiểm J và nhật ký trong tuyến P00-01 thực. Log chơi tay nay tách vào NGUMACHHUYENAN-tools/play-sessions/<timestamp-id>, không ghi đè bằng chứng kiểm thử đã lưu.

Khi chơi tay, launcher giảm log HTTP polling xuống Warning trong đúng tiến trình server nó tạo, để tránh log tăng liên tục và giảm tải máy. Các phiên đã mở trước thay đổi này vẫn giữ cấu hình cũ; launcher không dừng hoặc sửa tiến trình của người chơi đang chạy.

## Giao diện MoonGlass

Màu xanh tím than/tím khói bán trong suốt theo ảnh tham khảo2–3, viền bạc, nhấn champagne. Avatar/HP/MP, bảng nhiệm vụ, minimap và sáu kỹ năng vòng cung đã đổi cùng theme13mục. Mở panel ẩn HUD phía sau; sidebar và nội dung cuộn riêng. C mở nhân vật, K kỹ năng, M bản đồ, F10 cài đặt; J và I như cũ. Cài đặt camera/VFX/âm lượng lưu tại user://moonglass_ui.cfg. Các mục chưa có backend hiện empty/disabled state, không giả giao dịch.

Run_Playable_Alpha.ps1 -UiGallery chạy kiểm UI nhiệm vụ thật và xuất ảnh HUD+13mục. --ui-screen Inventory (hoặc Character/Settings/...) --capture <absolute.png> chụp giao diện offline, không có dữ liệu server. Quy chuẩn trong docs/production/MoonGlass_UI_UX_vi.md; ảnh nguồn/avatar mới và prompt ở Art_Source/MoonGlass_UI_20261105.
