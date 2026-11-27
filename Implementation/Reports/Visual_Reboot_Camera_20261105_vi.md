# Bàn giao camera từ trên và visual reboot —05/11/2026

## Đã thực hiện

Theo lệnh chủ dự án: Muse dừng graphics/UIUX/VFX/animation/map/Godot runtime, Codex tiếp quản và làm nguồn hình mới. PR22/111/112 đã đóng, lịch sử/source giữ nguyên. Chỉ có một admin chung trong repo nên không xóa credential của chủ dự án; agent_scope_v2 và scope audit là ràng buộc giao việc/nhận PR, không là account isolation. Muse chỉ MEDIA-01 video/cinematic/âm thanh theo work28.

CAM-TOPDOWN-WIDE-20261105 thay default32×18WU và hub48×27WU bằng64×36WU toàn thế giới; optional48×27WU. Camera2D không xoay, world viewport1280×720/20PPU, HUD CanvasLayer độc lập. Cập nhật entrypoints Godot/pixel/capital/camera để không giao tiếp đồ họa cho Muse hoặc lặp default cũ.

Scene mới ClientGodot/Preview.tscn dùng TileMapLayer160×120cells, map thử128×96WU, sprite độc lập và body8hướng nguyên người, props alpha. Không dùng hình Muse hay conceptPNG làm nền runtime. F2 đổi rộng/gọn, H ẩnHUD, WASD/mũi tên đi8hướng. HUD6skill theo vòng cung quanh attack, nằm trong safe margin và không chồng slot. Đây là art staging, chưa nối server/quest/combat.

## Kiểm chứng đã chạy trên Windows

- .NET SDK8.0.404, Godot4.7.2.NET: locked restore/build thành công,0warning/0error.
- Headless engine: CAMERA_SELF_TEST PASS40assertions: default/compact/bounds/small-map/atlasbounds/HUDCanvasLayer và6slot safe area/pair separation.
- PNG inspector:8sourcePNG,3runtimePNG hash trùng byte với source,8frame rect nguyên với padding≥20sourcepx; gridterrain/props1536×1024. Không sửa bitmap bằng script.
- Scope guard:4test cases gồm allowedmedia, graphics/runtime rejection, frozen/traversal và git rename/delete cannot hide old path.
- Render native thực: Compatibility/OpenGL3.3, NVIDIA GeForce820M, hai ảnh1280×720 cùng vị trí nhân vật64,44.8WU: native_wide_hud.png và native_compact_hud.png. HUD cùng kích thước; wide thấy thêm hàng nhà phía bắc và nhiều bờ sông. Có6skill đầy đủ, không cắt mép. Không gọi đây là benchmarkFPS hoặc test mouse/touch/input hoàn chỉnh.

## Giới hạn và phần tiếp

Art candidate chưa final: grass repetition, chuyển tiếpterrain, density, mái/cây che nhân vật, foot placement chi tiết, full animation/equipment/mob/VFX/UI behavior còn phải làm. Hero hiện chỉ idle8hướng, không giả walk/attack bằng đổi tên cùng frame. Minimap/sốHP trong HUD là staging presentation, chưa bindsnapshot.

Map staging không phải migration củaMAP_BEN_MUA, không đổi navhash/canonicalNPC/portal/node/loot. Thăng Long giữ mục tiêu2048×1536WU/12phường, chưa dựng đầy đủ. AOI visibility/PvPprofile/serverbinding/chunk streaming/performance thật là việc nối tiếp của Codex với các gói OpenCode/Qoder; chưa nới AOI hay bật production.

Source/prompt/hashes/manifest và ảnh render đi kèm để review. Không tuyên bố toàn game đã làm lại hình ảnh xong.
