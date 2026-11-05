# Nghiệm thu chuyển động, địa hình và combat HUD — 06/11/2026

## Kết quả và phạm vi

Sửa trực tiếp client Godot .NET và server local của tuyến Bến Mưa P00-01. Launcher Choi_Ben_Mua.cmd trong ClientGodot gọi cấu hình mới. Giữ tọa độ canonical, hợp đồng combat, phần thưởng và camera rộng 64×36 WU. Không xem báo cáo này là nghiệm thu toàn MMORPG, mọi map, mọi lớp nhân vật hoặc chiến dịch đã hoàn thiện.

## Nguyên nhân và thay đổi

1. Trước đây client gán vị trí server trực tiếp theo từng gói, online tắt collision mask, tốc độ server local 6 WU/s. Nay launcher đặt 3,2 WU/s (64 pixel/s), mỗi bước tối đa 0,10 giây; pump gửi tối đa 20Hz tùy RTT. Snapshot mang timestamp đơn điệu tại worker, client nội suy vị trí đã xác nhận với đệm 100ms. Không ngoại suy qua địa hình hay dự đoán sát thương. Sau idle/network gap giữ điểm cũ rồi nội suy vào bước mới; teleport reset nội suy physics/camera. Physics chạy 60Hz, camera xử lý cùng physics. Animation đi dựa trên dịch chuyển thực qua collision.
2. Client và server cùng đọc terrain.json xuất từ layout authored: 155 vùng cứng, polygon mặt nước và 3 mặt cầu tàu. Nhà, gốc cây, đá bờ, nền vườn, chum, hàng rào chặn bước; nước chỉ được đi trong vùng sàn cầu tàu. Server quét cả đoạn với bán kính chân, từ chối bước xuyên thay vì chỉ kiểm điểm cuối. Cầu tàu vẽ dưới nhân vật, không che chân người chơi. Bóng/nền/đá tĩnh được bake lúc chạy, công trình và cây vẫn Y-sort/occlusion.
3. Skill tự thân từng gửi target rỗng, bị client core từ chối; nay gửi null theo hợp đồng. Mọi ô skill và tấn công có press flash ngay, vùng bấm bao gồm viền và badge phím; phản hồi xác nhận/từ chối và cooldown đọc từ server. Thiếu mục tiêu, hết MP, ngoài tầm, chưa mở hoặc đang hồi đều có thông báo. Phản Quang cast chỉ hiện cue phòng thủ; hiệu ứng phản kích đợi COUNTER_CONFIRMED. Retry kết quả chưa rõ giữ liên kết với hành động gốc, không bịa damage/grant.
4. HUD trước đây dựng lại nhiều text/draw mỗi frame. Nay cache TextLine có giới hạn, vẽ vào SubViewport khi thay đổi, composite vùng có nội dung, minimap cập nhật 5Hz. Nền tĩnh bake một lần. Renderer mục tiêu 60FPS; màn hình 60Hz dùng VSync làm limiter duy nhất để tránh hai bộ sleep gây jitter trên driver cũ.

## Bộ khung nhân vật mới

Imagegen tích hợp tạo 20 sheet được chấp nhận (4×4 ô/sheet), với prompt thực tế và SHA/ánh xạ nguồn-runtime. Minh Kiếm hiện có idle/walk/attack/cast, mỗi hành động 16 frame cho 8 hướng. N/NE/E/SE/S có hình riêng; SW/W/NW lật SE/E/NE, khai báo trong manifest. Tổng 320 pose nguồn và 512 tham chiếu frame. Không lặp 4 frame cũ để giả thành 16.

Timeline: idle 1,6s, walk 0,8s, attack 0,6s, cast 0,64s; tốc độ render độc lập số pose. Căn chân theo pivot từng ô, giữ chiều cao thân cố định mỗi clip. Bộ này áp dụng nhân vật playable hiện tại, chưa áp dụng quái/NPC/các lớp khác hay các hành động chưa triển khai như chết, thu thập, cưỡi thú.

Nguồn: Art_Source/Motion_16F_20261106/README_vi.md, generation_records.json, source_history.json và Prompts/*.txt. Runtime byte-identical với nguồn được chấp nhận; Python chỉ kiểm ảnh/xuất metadata, không sửa bitmap. Các bản nguồn bị loại được giữ để truy nguyên, không nạp runtime.

## Kết quả kiểm tra

| Kiểm tra | Kết quả | Bằng chứng |
|---|---|---|
| Client .NET build locked restore | PASS, 0 warning/error | client_build.log |
| Engine physics/pointer/pose | PASS 538 assertion | motion_regression.log |
| Camera / scene / visual / quest presentation | PASS 48 / 9 / 15 / 30 | client_self_checks.log |
| Server self-check baseline | PASS, exit 0; 258 dòng PASS | server_self_check.log |
| Shared authored terrain | PASS 211 assertion | terrain_self_check.log |
| HTTP thật, server riêng | PASS 22 assertion | terrain_http.json |
| Native UI + HTTP P00-01 + combat pointer injection | PASS 134 assertion | ui.godot.stdout.log, ui.run.json |
| Gallery HUD + 13 panel | PASS | ui.godot.stdout.log, moonglass_*.png |
| Art / terrain / catalog / scope validation | PASS | structure_checks.log |

HTTP test chạy session riêng: tới chân nhà bị chặn, tới bờ sông bị chặn, xuống mặt cầu được, ra mép và cuối cầu bị chặn; bước bị từ chối không đổi vị trí. Guard không cần target được chấp nhận, MP từ 50 xuống 38, có CAST_START, không giả counter. Bấm lại nhận 409 cooldown_active và MP vẫn 38. Native test đi nhận/làm/trả nhiệm vụ, giữ phần thưởng 20 đồng + 1 áo; sự kiện chuột được bơm qua Viewport vào handler thật, không phải robot chuột phần cứng.

## Hiệu năng đo trên máy hiện tại

Godot 4.7.2 .NET, Compatibility/OpenGL 3.3, GeForce 820M, viewport 1280×720, camera rộng, HUD bật. Đo native bằng Stopwatch: warmup 3 giây, lấy mẫu 12 giây; nhân vật đi thực 919.5 pixel.

- 713 frame / 12.0216 giây: trung bình **59.31 FPS**.
- Median **16.649ms**, p95 **16.939ms**.
- Khoảng 161.4 draw call/frame, texture 304.8 MiB.
- Mục tiêu 60FPS, không cam kết mọi frame/mọi máy luôn đạt 60. Đây là đo render + di chuyển local/offline, không phải benchmark tải đông người hoặc độ trễ Internet.

performance_walk.json là số đo gốc; ảnh performance_walk.json.png chụp sau đo. Các ảnh gallery lưu PNG liên tiếp có thể hiện FPS thấp do thao tác encode/lưu ảnh đồng bộ; không dùng con số góc HUD trong gallery thay benchmark. Ảnh motion16_*.png là bảng kiểm tư thế tĩnh, không phải timeline hay phim FPS.

## Chạy và tái kiểm

Từ repo, dùng ClientGodot/Choi_Ben_Mua.cmd để chơi. Đóng phiên game cũ và mở bằng launcher mới để server của phiên mới nhận cấu hình; launcher không dừng các server hoặc editor của người khác.

- ClientGodot/Run_Playable_Alpha.ps1 -MotionTest -UiGallery -EvidenceDirectory <thư mục riêng>
- Godot --headless --path ClientGodot -- --motion-self-test
- Godot --path ClientGodot -- --motion-art-review --capture <đường dẫn ảnh tuyệt đối>
- Godot --path ClientGodot -- --performance-profile <đường dẫn JSON tuyệt đối> --profile-walk
- python Tools/ArtProduction/export_ben_mua_terrain.py --check
- python Tools/ArtProduction/inspect_motion16.py
- dotnet Server/Health/bin/Release/net10.0/Health.dll --terrain-self-check Implementation/Content/Maps/BenMua/terrain.json
- python Tools/Coordination/verify_authored_terrain_http.py --dotnet <dotnet10> --output <thư mục riêng>

Server host ngoài launcher phải truyền Content:BenMuaTerrainPath đến file xuất tương ứng và P1World:MoveSpeedWuPerSecond=3.2 / MaxStepSeconds=0.10 để dùng cùng địa hình/tốc độ; server legacy mặc định giữ topology hiện hữu. Map khác dùng fallback geometry, chưa được nghiệm thu bởi bộ kiểm Bến Mưa này. Bounds vẫn canonical 360×84, không tự mở map rộng hơn hoặc dời spawn NPC.

Online hiện mở 3 skill Minh Kiếm; ô 4–6 có phản hồi chưa mở, không giả thành chức năng đã có backend. Sáu ô vẫn có hit/press feedback và preview offline. Không thay đổi hợp đồng inventory, XP/loot hay phần thưởng để vượt kiểm.
