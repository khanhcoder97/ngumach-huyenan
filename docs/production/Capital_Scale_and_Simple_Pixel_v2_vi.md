# Thăng Long rộng lớn và pixel art dễ sản xuất — 2026-10-29

Chủ dự án muốn kinh thành rộng nhiều khu và đồ họa pixel đơn giản nhưng nét. Game tiếp tục Unity/top-down XY; thay độ phức tạp mỹ thuật và quy hoạch thành, không đổi engine ở đây. Concept cũ chỉ là một góc chợ, không thể hiện tổng thể. Mẫu mới ở Art_Concept_References/v2/ gồm bản đồ tổng thể và một góc phố gameplay; hai ảnh có tỷ lệ khác nhau.

## Quy mô thiết kế mới

MAP_THANG_LONG mục tiêu quy hoạch **2048×1536 WU** (1024×768m theo1WU=0,5m), mặt phẳngXY, gồm12phường theo lưới4×3, mỗi vùng quy hoạch512×512WU. Đây là footprint tổng thể gồm phố/kênh/sân/vườn, không đồng nghĩa toàn bộ diện tích đều có nhà hoặc walkable. Đủ lớn để khám phá, không cố tạo đường dài vô nghĩa.

Camera cơ sở32×18WU chỉ thấy khoảng1/5461 diện tích tổng thể tại một thời điểm. Với tốc độ config P1 hiện tại6WU/s, chạy đường thẳng hết chiều ngang là341,3s (~5phút41giây); đường thực vòng1,5lần là~8phút32giây, chưa tính dừng. Đi tham quan nhiều khu có thể20–30phút theo mục tiêu playtest. Đây là ước tính có công thức, không hứa “vô tận”. Không tăng tốc/quãng đường skill để giả độ rộng.

Các cửa hàng thường dùng tập trung trong service core, người chơi đi khám phá tùy ý ngoài core. Sau khi tự khám phá các trạm, mở tuyến dẫn lộ nội thành miễn phí theo rule cũ; không buộc chạy5phút mỗi lần sửa đồ. Tuyến phải có khoảng nghỉ, hồ/sân/điểm nhìn và hoạt động truyện thay vì lấp nhà liên tục.

## 12 phường quy hoạch

Các mã CAP_Dxx là ID quy hoạch, chưa đăng ký NPC/map runtime mới. Rectangle dùng [min,max) để không đè vùng, outer boundary cuối được bao trong map.

| Khu | Bounds X,Y WU | Vai trò |
|---|---|---|
|CAP_D01|0..512,0..512|Cửa Tây Nam, ngoại phố và vườn dân|
|CAP_D02|512..1024,0..512|Phường Bang Hội, sân sinh hoạt và thú|
|CAP_D03|1024..1536,0..512|Bách Công, lò rèn và phố nghề|
|CAP_D04|1536..2048,0..512|Cửa Đông Nam, trạm xe và kho tiếp tế|
|CAP_D05|0..512,512..1024|Bến Sông Ngự, kênh và bến hàng|
|CAP_D06|512..1024,512..1024|Phường Giao Dịch, kho/thư và service core|
|CAP_D07|1024..1536,512..1024|Quảng trường, khán đài Long Môn, lối instance PvP|
|CAP_D08|1536..2048,512..1024|Đại Chợ Ngũ Mạch, chợ phiên và sân hàng|
|CAP_D09|0..512,1024..1536|Hồ/vườn, miếu nhỏ và điểm khám phá|
|CAP_D10|512..1024,1024..1536|Công Văn, lưu trữ và điều tra C1-06|
|CAP_D11|1024..1536,1024..1536|Hoàng thành fantasy, sân nghi lễ; không tái dựng di tích thật|
|CAP_D12|1536..2048,1024..1536|Phố ở, thư quán và cửa Đông Bắc|

Trục Bắc–Nam/Đông–Tây nối các khu, cửa theo compass có route đã mở; vị trí chính xác sẽ có topology review, không đo tọa độ từ ảnh AI. Quảng trường là một landmark của toàn kinh thành, không phải toàn thành. Đấu sĩ/khán giả tách vùng như spec cũ; nội thành không spawn boss/quái để lấp khoảng trống.

## Chunk và cách làm phù hợp người mới

Một chunk quy hoạch64×64WU =80×80tile16px ở20PPU. Toàn extent có32×24=768chunk slots; đây là các ô tiềm năng, không tạo768scene hoặc768bức tranh riêng. Mỗi chunk chỉ lưu tile/prop cần, tái dùng tileset và module nhà; nước/vườn/trống có thể dùng ít data. Stream quanh actor, giữ tối đa vùng3×3chunk ở prototype; terrain/entity budgets phải đo, không coi9chunk luôn đủ FPS.

**Bản đầu chỉ sản xuất một chunk service street64×64WU ở CAP_D06**. Có đường đi, một cầu/kênh, nhà modular, quầy chợ và ba điểm dịch vụ mẫu. Actor/demo chỉ được vào chunk đã có nav và collider hợp lệ; ngoài đó dùng closed gate/construction marker rõ ràng, không giả thành phố hoàn thiện. Chunk kế tiếp nối sang quảng trường rồi chợ. Không nhân hàng trăm nhà unique ở bước đầu.

Mục tiêu kit đầu: ground/edge/decor tối đa48tile;12module kiến trúc (tường/mái/cửa/góc),12props dùng lại,2cây,1cầu,1biến thể nước4frame. Đây là cap scope mẫu, không catalogue launch. Mỗi5–10nhà đổi palette/hiên/cửa/prop để tránh lặp cứng; chỉ landmark cần vẽ riêng.

## Pixel đơn giản nhưng sắc nét

- Runtime giữ640×360logical,20PPU,tile16×16,hero cell48×64. Không đổi runtime thành320×180 chỉ vì prompt tham chiếu dùng khái niệm low-res. Sprite có thể vẽ ít chi tiết trong cell hiện có.
- Mỗi vật liệu3tone chính+1highlight; character mục tiêu16–24màu, tối đa40khi cần variant. Không pixel noise, không vẽ từng viên ngói khác nhau, không texture cỏ chấm trắng khắp nền. Biên silhouette quan trọng hơn chi tiết mặt.
- Tường/mái/nhà dùng khối vuông và góc bậc, outline1sourcepx, bóng cứng2tone; không HD painterly, normal map hay bloom. Nước4frame loop, lá cây2frame nhẹ là đủ cho prototype; không cần mọi prop động.
- Export PNG native; scale2×/3×/4× bằng nearest/point, camera pixel snap, mipmap off. Không nén lossy source, không AI-upscale ảnh lớn rồi thu nhỏ thành sprite production. Encode video là delivery riêng, cần giữ master lossless.
- Giữ8hướng character theo DEC-015; làm một pose đạt rồi đủ8pose, sau đó walk6frame. Có thể tái dùng hướng khi đối xứng thật, nhưng không flip tay/đạo cụ sai. Không bắt vẽ16action cho mọi NPC ngay.
- Mẫu phố mới là đích về ít chi tiết và độ đọc. Ảnh sinh chưa chắc đúng palette hoặc lưới320/640, phải dựng lại native. Bản đồ tổng thể dùng quy hoạch/mood, không dùng độ dày chi tiết macro cho tile gameplay.

## Migration bảo toàn dữ liệu hiện có

Bounds runtime v1 vẫn900×96WU (yMin−12 trong registry), NPC/C1-06/route cũ còn theo trục900WU. **Chưa tự sửa map_bounds.json hoặc transform toàn349placement.** Quy hoạch v2 lưu DesignBaselines/thang_long_layout_v2.json với activation DESIGN_ONLY_REQUIRES_MIGRATION. Chuyển runtime cần một bundle đồng bộ bounds+topology+placements+portals+routes+quest triggers+camera+arrival.

Mỗi record ghi canonical recordId, oldXY, newXY, floorId, newDistrict, sourceVersion và review evidence. Spawn/portal/merchant không còn giữ tọa độ ngoài extent sau activation; chạy foreign-key/path/distance và quest flow kiểm tra trước đổi version. Client/server phải cùng hỗ trợ layoutVersion, session cũ đưa về safe arrival reviewed khi migrate. Không thêm NPC bản sao hoặc di chuyển người đang trade bằng ảnh concept.

## Bàn giao và điều phối

Muse: một chunk phố pixel đơn giản và top-down overview có12phường; cung cấp tile modules/native previews, không tạo toàn thành bằng một ảnh. OpenCode: contact sheet/coverage kiểm counts và source metadata, không cần Unity máy local. Qoder: proposal migration layout v2 sau khi nhận geometry, giữ flag content v1 khi chưa có nav thật. Codex review độ đọc ở native trước khi nhân rộng.

Art proof trước: pose, tile kit, mockup640×360. Gameplay proof sau: actor di chuyển qua ranh chunk, collision không seam, mái không che target, không tải toàn thành vào camera, route/quest không hỏng. Quy mô quy hoạch lớn không thay nghiệm thu những chunk thực sự chơi được.
