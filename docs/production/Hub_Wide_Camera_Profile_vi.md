# Camera Hub Rộng — 2026-10-29

Theo yêu cầu chủ dự án, tăng tầm nhìn trong hub để bao quát phố và công trình tốt hơn. Phạm vi là world camera, không thu nhỏ HUD. Profile runtime cần được tích hợp theo map metadata; tài liệu này chưa tự đổi camera C# hiện tại.

| Profile | Logical world render | PPU | Tầm nhìn16:9 WU | Orthographic half-height |
|---|---|---:|---|---:|
|STANDARD|640×360|20|32×18|9|
|HUB_WIDE|960×540|20|48×27|13,5|

HUB_WIDE tăng1,5lần chiều ngang/dọc và2,25lần diện tích. Hero64sourcepx vẫn giữ64sourcepx, không xóa chi tiết ảnh; khi cùng output1080p, scale world đổi3×→2× nên chiều cao cell màn hình192→128px. Không scale riêng actor lên lại vì sẽ sai tỷ lệ nhà/collision. Selector outline nhẹ giúp tìm mình giữa crowd.

## Profile theo khu vực

- Hub an toàn: MAP_THANG_LONG và khu safe của MAP_THANH_LAC được default HUB_WIDE khi client/map flow đã tích hợp. Người chơi có tùy chọn Chuẩn/Rộng trong Settings→Camera. Không có zoom tự do vô hạn.
- Combat field/dungeon/boss/PvP dùng STANDARD theo rule mode. Cùng map asset được dùng cho PvP instance vẫn phải STANDARD. Permission profile lấy mode/instance metadata server, không chỉ map name.
- Unknown map/mode về STANDARD. Chuyển hub→arena chọn camera trước khi trả input, không mang Hub Rộng vào trận. Trong hub nhìn rộng không làm tương tác xa hơn5WU hoặc mở NPC/quest marker chưa khám phá.

## Pixel sắc và khả năng đọc

Giữ Assets PPU20 và source cell48×64/tile16×16. Pixel Perfect Camera ref resolution960×540 cho wide; không hạ texture resolution hay đổi assetsPPU để fake zoom. Không chỉ gán orthographicSize nếu PixelPerfect đang override nó. Render world snap0,05WU, gameplay simulation giữ số thực.

Output1920×1080 dùng scale2× nguyên cho HUB_WIDE. 1280×720 dùng960×540 scale1× centered có padding160px ngang/90px dọc nếu fixed16:9 pixel viewport; không stretch fractional4/3. Device viewport nhỏ hơn960×540 dùng STANDARD và thông báo ngắn “Thiết bị hiện dùng tầm nhìn chuẩn”. Viewport fitting cần test trên thiết bị, không đánh đổi pixel grid âm thầm. Các tỷ lệ20:9 giữ chiều cao logical của profile và giới hạn theo safe area/mode; competitive luôn cùng vùng nhìn.

HUD layout và hitbox được vẽ bằng canvas riêng theo device/safe area, không phụ thuộc world ref resolution. Nút skill vẫn6ô vòng cung DEC-019; min hit target48dp và text scale hiện hành. Wide chỉ thay camera vùng world; minimap/icon/NPC label không co theo hero. Mái/cây dùng occlusion và nameplates có giới hạn mật độ, không phủ tên tất cả NPC trong vùng rộng.

Transition dùng bước profile rồi fade150ms nếu cần; không lerp orthographic liên tục tạo fractional pixel/shimmer. Tùy chọn reduced motion dùng đổi ngay ở frame boundary. Save camera preference per-device, server mode thắng preference trong instance.

## Performance và streaming

Diện tích world visible tăng2,25lần có thể tăng draw calls/actors/weather, nên culling theo frustum+prefetch margin8WU, chunk streaming quanh camera. Không tải2048×1536WU toàn thành chỉ vì camera rộng. Camera48×27WU vẫn nhỏ hơn một chunk64WU, nhưng ở ranh chunk cần các chunk lân cận;3×3 là budget thử nghiệm, phải đo CPU/GPU/memory.

Giảm crowd ambient, hạt weather, animation decorative xa trước khi giảm chi tiết hero/telegraph. NPC service/quest phải giữ khả năng đọc; không làm ẩn server actors vì cả client lag và mất interact. Target PC60/mobile30FPS cần evidence real device; ảnh so sánh không chứng minh performance.

## Acceptance

1. Từ cùng world position thấy48×27 thay32×18, actor foot và collision không đổi.
2. HUD/skill arc/joystick giữ kích thước vật lý và không overlap sau đổi profile.
3. Pixel edges sắc ở1080p/720p và tỷ lệ20:9; không texture fractional resize.
4. Vào PvP/boss instance trở vềSTANDARD; không lộ NPC/players ngoài visibility policy.
5. Qua ranh chunk, map edge và mái nhà không thấy void/camera jump; hình và input cùng anchor.

Ảnh `Art_Concept_References/v2/03_hub_wide_camera_comparison.png` chỉ minh họa zoom-out và giữ HUD. Geometry/camera ratio và icon trong ảnh sinh không được đo làm dữ liệu: ảnh có thể đổi cảnh/thiếu glyph, không thay concept06 sáu slot hoặc tọa độ DEC-019. Muse cần dựng lại từ đúng scene và chụp hai profile cùng vị trí khi engine có sẵn.
