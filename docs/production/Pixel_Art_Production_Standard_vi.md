# CHUẨN SẢN XUẤT PIXEL ART — NGŨ MẠCH: HUYỀN ẤN

**Trạng thái:** art direction hiện hành theo quyết định chủ dự án ngày 2026-10-26; thay toàn bộ định hướng HD vẽ tay/rig của tài liệu cũ.  
**Phạm vi:** nhân vật, quái, boss, map, VFX, thời tiết, icon, HUD, menu, portrait, preview ngoại trang và mọi hình runtime.  
**Nguồn chuẩn:** tài liệu này khóa cách dựng/render; các spec domain giữ nguyên ID, gameplay, tọa độ WU, thời gian server và nội dung.

## 1. Ngôn ngữ hình ảnh

- Pixel art 2D ngang, vẽ pixel thủ công theo cụm màu có chủ ý; silhouette lớn, tương phản rõ, chi tiết trang phục/kiến trúc gợi chất fantasy võ hiệp Lạc Châu nguyên bản.
- Tham chiếu hình ảnh người chơi cung cấp ngày 2026-10-26: tỉ lệ chibi kiếm sĩ, tóc nâu, giáp bạc viền vàng, áo choàng xanh và kiếm. Dùng như hướng mỹ thuật tổng quát; không sao chép nhân vật/tên/huy hiệu cụ thể trong ảnh.
- Không vector line art, tranh raster HD được thu nhỏ, AI upscale, blur, anti-aliasing, gradient mượt, normal-map lighting hoặc skeletal deformation làm biến dạng cụm pixel. Ánh sáng/gradient chỉ được vẽ thành dải pixel/banding hoặc dithering có kiểm soát.
- Màu là một phần tín hiệu nhưng không phải tín hiệu duy nhất. Telegraph, đội, rarity và trạng thái luôn khác nhau cả về silhouette, pattern, icon hoặc motion.
- Giữ rào chắn nguyên bản: không lấy hoặc tái dựng sprite, UI, tên riêng, âm thanh hay hình nhận diện từ KPAH/JAR.

## 2. Pixel grid và world scale

| Thiết lập | Giá trị chuẩn |
|---|---:|
| Logical render | 640×360 pixel, landscape 16:9 |
| Pixels Per Unit | 20 px/WU; 1 WU vẫn bằng 0,5 m |
| Base camera view | 32×18 WU ở 16:9 |
| World pixel step | 0,05 WU; render origin/camera/sprite pivot snap vào lưới này |
| Hero | actor bounds cao 5 WU; sprite thường 96–112 source px có trim/pivot; target khoảng 300 screen px ở output 1920×1080 |
| Tile art | tile nền chuẩn 16×16 source px (0,8 WU); module lớn là bội nguyên của tile, placement gameplay tiếp tục dùng WU |

Unity dùng URP 2D + Pixel Perfect Camera, Reference Resolution 640×360, Assets Pixels Per Unit 20, integer upscale; đầu ra 720p/1080p/1440p lần lượt dùng scale 2×/3×/4×. Tỉ lệ không chia hết dùng integer viewport có letterbox/pillarbox; không kéo scale phân số lên sprite. Với 20:9 landscape giữ 360 logical pixel chiều cao và mở rộng chiều ngang; vùng gameplay/camera không được cấp lợi thế đối kháng riêng cho thiết bị. Portrait dùng layout UI riêng, không ép xoay/scale sprite.

## 3. Import và đóng gói

- Sprite Filter Mode `Point (no filter)`, Compression `None` hoặc định dạng lossless, Mip Maps `Off`, anti-aliasing `Off`; Sprite Atlas padding tối thiểu 2 source pixels để bleed không lộ khi pack. Giữ metadata import/atlas trong version control.
- Runtime chỉ dùng pixel source đúng grid; không resample bằng bilinear/bicubic, không upscale ảnh tham chiếu thành texture production. UI canvas có thể bố trí responsive nhưng icon, chữ và viền raster theo logical grid; khi scale phải giữ integer scale.
- Texture: actor/prop pack 512² hoặc 1024²; boss/environment sheet tối đa 2048² mỗi trang theo nhóm animation/layer; icon/item 32²–64²; skill/UI icon 32²–48²; portrait 64²–96². Mọi frame có trim/pivot guide và kích thước cell khai báo rõ; atlas không buộc mọi frame cùng kích thước nếu dùng trim metadata.
- Tile palette và sprite sheet dùng palette role cố định. Mục tiêu khoảng 24–40 màu cho hero outfit hoàn chỉnh, 12–24 màu quái thường, tối đa 64 màu cho boss/biome hero sheet; tái dùng ramp màu trong cùng khu vực.
- NPC, mob và người chơi có thể dùng shared silhouette base nhưng animation/runtime character là frame-based sprite sheets, không bone-warp. Thiết bị/ngoại trang tách layer chỉ khi layer vẫn snap cùng pixel grid và pose; ưu tiên sprite variant đã vẽ thay material recolor không kiểm soát.

## 4. Animation, camera và combat readability

- Animation vẽ frame-by-frame. Idle 4–6 frame ở 6–8 fps; walk/run 6–8 frame ở 8–12 fps; hit/reaction 2–4 frame; kỹ năng chủ lực 5–10 frame cho từng pha. Giữ thời gian gameplay theo spec và server tick; không đổi thời lượng/collision theo số frame vẽ.
- Gameplay camera là side-on; di chuyển/trận chiến có sprite trái/phải. Có pose front/back/side bổ sung cho menu, preview, hội thoại khi content cần; không bắt buộc 8-way sheet.
- Gameplay collider, attack shape, range, movement, hit result và reward không được lấy từ opaque sprite bounds/frame event. Chỉ vẽ cue; server xác nhận kết quả. Pivot/foot contact ổn định giữa frame để nhân vật không rung.
- Hạn chế shake theo pixel step và thời lượng trong Combat spec. Không subpixel-scroll nền gameplay: camera snap theo pixel; parallax dùng hệ số di chuyển nhưng vị trí render cuối vẫn lượng tử hóa.

## 5. VFX, weather và giảm hiệu ứng

- VFX là sprite/pixel-particle theo cùng grid, palette và outline; tia, cung kiếm, nước, khói và bụi tạo bằng shape pixel dễ đọc. Không dùng bloom, blur hậu kỳ, glow mượt hoặc hạt dưới 1 source pixel. Parallax/weather có thể dùng các pattern tileable.
- Giữ nguyên cue shape, thời lượng và vùng nguy hiểm ở LowFX. LowFX giảm số particle, layer weather phụ và shake; không xóa telegraph, hit-confirm icon hoặc tương phản mục tiêu.
- Pixel burst theo hướng dẫn Art Bible/Combat: mobile ≤40 hạt chính mỗi burst, HighFX ≤120; hạt có kích thước cụm 1–4 source px, cap theo actor và vùng.

## 6. UI, chữ và layout

- Frame, icon, button, badge, avatar và map/minimap dùng pixel-art assets cùng palette; viền/panel dùng 9-slice theo biên pixel rõ. Bitmap font tiếng Việt phải có đầy đủ dấu/hoa/thường/số/ký tự chat; test không rơi dấu ở 640×360 logical.
- Scale UI theo safe area và grid; không làm mờ raster khi hover, focus hoặc disabled. Trạng thái dùng frame/icon/pattern/shape khác nhau, không chỉ đổi hue.
- Menu lớn có thể chi tiết hơn gameplay nhưng vẫn vẽ ở logical scale có chủ ý và scale nguyên; không pha icon HD/vector vào cùng bộ pixel art.

## 7. Bàn giao và nghiệm thu

Mỗi asset ghi `asset_id`, entity/map/skill link, source PNG/layer, cell/frame table, pixel size, PPU, pivot, palette, atlas page, compression/import preset, animation FPS, LowFX variant nếu có, provenance/license, trạng thái (`CONCEPT`, `APPROVED`, `INTEGRATED`, `DEVICE_QA`). Preview tại 640×360 logical và output 1280×720, 1920×1080, 2560×1440 phải giữ cạnh pixel sắc, không shimmer, không bleed/halo và silhouette/telegraph còn đọc được trên nền sáng/tối.

## 8. Phạm vi migration và phần chờ

- Giữ nguyên schema, ID, map WU, spawn/gather placement, quest, combat balance, network/server contracts và nội dung. Thay visual export, animation representation, camera render, import preset, UI art và tiêu chí nghiệm thu.
- Các concept SVG cũ của Minh Kiếm chỉ là hồ sơ ý tưởng lịch sử, không phải art source/runtime; thay bằng sprite concept pixel-art trước bước model/animation production.
- Trình tạo ảnh tích hợp chưa khả dụng trong phiên này. Chưa tạo/gán sprite raster production; dùng CLI image generation chỉ khi được chủ dự án xác nhận rõ phương án CLI và máy đã có `OPENAI_API_KEY`. Nghệ sĩ có thể tạo source pixel art thủ công theo chuẩn này.
