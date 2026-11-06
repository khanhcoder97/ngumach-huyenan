# Chuẩn sản xuất đồ họa pixel art hiện hành

Cập nhật 07/11/2026 theo quyết định trực tiếp của chủ dự án. Chuẩn này áp dụng cho asset mới và thay mới, cùng [Chuẩn animation 16–20 khung / 60 FPS](Actor_Animation_16_20F_60FPS_20261107_vi.md). Các mức idle4–6, walk6–8, hit2–4, skill5–10 khung trước đây đã hết hiệu lực nghiệm thu. File cũ trong Git vẫn là lịch sử, không tự trở thành asset đạt chuẩn.

## Engine, góc nhìn và tỷ lệ

- Godot4.7.2 .NET, .NET8, renderer Compatibility; Unity/URP là hướng lịch sử.
- Gameplay2D orthographic north-up, XY là mặt đất,8hướng di chuyển. Kiến trúc gần nhìn từ trên theo [quyết định camera rộng](TopDown_Wide_Camera_20261105_vi.md).
- Viewport1280×720,20pixel/WU, mặc định64×36WU; F2 chọn48×27WU. HUD tách CanvasLayer và giữ cỡ chữ/nút. Không tự quay lại640×360/32×18WU hoặc chỉ mở góc rộng trong hub.
- Renderer nearest, không mipmap; integer viewport/letterbox khi phù hợp. Không đổi tọa độ, footprint, collision hoặc kích thước world của server để khớp hình.
- Hero runtime hiện hiển thị cao36pixel; mỗi atlas khai báo referenceHeight để chuyển từ kích thước nguồn sang cỡ hiển thị. Cell48×64 cũ là quy cách export tham khảo, không phải lý do phóng mọi actor lên64pixel trong runtime góc rộng.
- Không tự scale các bounds WU lịch sử trong Art Bible thành collider mới.

## Tạo hình và chất lượng ảnh

Pixel art sắc nét, silhouette dễ đọc, cụm màu có chủ ý, bề mặt3tone+1highlight khi phù hợp. Không dùng concept như nền map hoặc cắt tranh concept thành actor. Tạo hình class lấy catalogue hiện hành; Minh Kiếm runtime tóc đen búi cao, áo ngà/teal, kiếm thẳng. Concept tóc xanh/choàng đỏ trước đây là tham khảo lịch sử.

Nguồn PNG lossless có alpha thật; không nền caro giả, không crop chân/vũ khí, không noisy fringe/halo hoặc gradient phủ kín silhouette. Mục tiêu24–40màu cho hero,12–24cho quái thường; kiểm bằng mắt ở cỡ chơi trên nền sáng/tối. Một ảnh được sinh thành công chưa đồng nghĩa đạt pixel art production.

UI hiện dùng MoonGlass xanh tím bán trong suốt, viền bạc/champagne theo [MoonGlass UI/UX](MoonGlass_UI_UX_vi.md). Theme UI này thay hướng toàn bộ panel gỗ nâu/viền vàng cũ. Typography tiếng Việt phải đủ dấu và dễ đọc; không ép bitmap-font mờ hoặc icon thiếu nét chỉ để giữ phong cách pixel.

## Animation bắt buộc

- **16–20 khung nguồn thực cho mỗi clip, mỗi hướng; mặc định16.** Áp dụng idle, walk/run, attack/combo, sáu skill riêng, hurt, death, dodge, interact/work và hành động nhiệm vụ có trong gameplay.
- Không nhân bản4/8pose để báo16, không lấy cùng một cast chung và báo hoàn thành sáu skill riêng. Frame hash khác nhau chỉ là kiểm cấu trúc, không chứng minh pose khác nhau hoặc chuyển động đúng.
- Actor di chuyển cần8hướng. Khi được phép,5hướng N/NE/E/SE/S có thể cung cấp3hướng lật; manifest ghi rõ source/flip. Băng tay, sừng gãy, mặt nạ hoặc chi tiết bất đối xứng có ý nghĩa cần góc vẽ riêng.
- Atlas80pose có8cột×10hàng, mỗi hướng2hàng liên tiếp8khung. Atlas16pose4×4 một hướng là phương án thay/sửa từng góc. Không đoán ô theo kích thước chia đều khi nguồn có padding không đều; frame rect/pivot phải được nghiệm thu.
- Idle/walk loop không nhảy ở15→0. Hurt là một lần recoil rồi phục hồi, không hai vòng8khung. Death là một lần ngã liên tục; khung cuối nằm xuống; runtime one-shot giữ khung cuối.
- Pose không điều khiển vị trí hoặc sát thương. Giữ ground anchor; dùng referenceHeight được hiệu chỉnh theo trang/hướng vì các ảnh nguồn có thể khác độ phân giải. Không lấy chiều cao pose nằm để phóng người ngã thành người khổng lồ.
- Render mục tiêu60FPS, physics60Hz. Timeline theo giây độc lập số frame nguồn và server tick. Không ép16khung phát trong16/60giây. Dùng timeline server cho cue/hit; animation không tự cấp damage/heal/loot/credit.
- Mặc định xem thử: idle1,0s, walk0,8s, basic0,6s, hurt0,3s, death1,2s. Đây là nhịp review; cast/telegraph/attack/recovery production phải khớp kỹ năng và encounter được duyệt.

## VFX và weather

VFX tách cast/projectile/impact/loop/end khi cơ chế cần; mỗi thành phần được bàn giao dưới dạng clip cần16–20khung. Một atlas timeline mẫu không tự hoàn thành toàn bộ chuỗi thành phần. Hướng đạn, tâm vùng và thời gian nguy hiểm lấy từ gameplay; không bake đường đi thế giới vào từng cell.

LowFX giảm hạt/layer phụ, giữ shape/timing/outline bắt buộc. Telegraph boss luôn đọc được dưới skill, weather và UI. Không dùng flash toàn màn, bloom hoặc blur che mục tiêu. Vật thể môi trường có animation riêng được ghi phạm vi rõ; vòng nước trang trí4frame lịch sử không được báo là VFX chiến đấu16frame.

## Export, import và bộ nhớ

PNG gốc giữ nguyên; sửa raster bằng imagegen tích hợp, lưu phiên bản mới và prompt. Công cụ phân tích chỉ đọc ảnh, xác định gutters/bounds/rect/hash và xuất JSON; không vẽ hoặc resample bitmap để cứu ảnh sinh lỗi.

Mỗi clip có asset/entity/skill ID, nguồn, SHA256, frame order/rect/bounds, pivot, referenceHeight theo hướng, flip, duration, timeline type loop/one-shot, trạng thái nghiệm thu và provenance. Runtime dùng lossless + nearest, không mipmap; margin/gutter ít nhất2pixel nhìn thấy quanh frame. Chia page/lazy load và giới hạn cache; không nạp toàn thư viện cùng lúc.

## Cổng nghiệm thu và người phụ trách

REQUESTED → GENERATED → STRUCTURE_PASS → VISUAL_REVIEW → ENGINE_IMPORTED → DEVICE_QA. Thiếu bất kỳ bước cần thiết nào thì chưa production-approved. Ảnh đủ ô nhưng sai hướng, đảo tay, trượt chân, đổi khuôn mặt hoặc lặp nửa chu kỳ phải sửa. Nghiệm thu60FPS bằng mẫu đo native có GPU/viewport/warmup/median/p95, không bằng ảnh chụp FPS hoặc số frame nguồn.

Codex phụ trách asset, UI/UX, VFX, sprite và animation. Muse chỉ làm video/cinematic/âm thanh theo quyết định hiện hành; quy trình giao Muse làm sprite/ghép atlas trước đây hết hiệu lực.

Catalogue và hàng đợi đầy đủ ở Art_Source/Actor_Library_20261107; ảnh sinh có thể chỉ là ứng viên. Công cụ Godot ActorLibrary là scene review riêng, không chứng nhận toàn bộ game hoặc mở khóa class/skill backend chưa triển khai.
