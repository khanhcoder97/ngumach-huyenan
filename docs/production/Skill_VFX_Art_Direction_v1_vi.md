# Bộ kỹ năng và hiệu ứng pixel cho năm môn phái — 2026-10-29

Gói này gồm5board concept (6kỹ năng×3pha mỗi board),30thẻ art chi tiết và dữ liệu handoff Muse. Dùng thiết kế gameplay đang có trong Combat_Skills_VFX_Animation_Spec_vi.md/Content Bible/decision; không đổi damage, cooldown, MP hoặc thêm summon để giống ảnh tham khảo. Source images người dùng chỉ tham khảo ngôn ngữ chuyển động; không cắt sprite từ sheet có dấu ripped/credit.

## Mỗi lớp có một ngôn ngữ riêng

| Lớp | Cơ chế | Hình dáng/nhịp | Bốn active + cơ động + tuyệt kỹ |
|---|---|---|---|
|Minh Kiếm/Kim|Kiếm Ý0–5|thẳng/thoi/lục giác, nhát sắc có khoảng nghỉ, trắng-vàng-bạc|Phản Quang, Tầm Long, Kiếm Trận, Thiết Y, Bạch Hồng, Vạn Tượng Quy Nhất|
|Ảnh Đao/Hỏa|Nhiệt0–5|cung cong/vệt than/tam giác, hai nhịp thấp nhanh, đỏ than-cam|Huyết Nguyệt, Tàn Hỏa, Xích Ảnh, Tước Mạch, Ảnh Bộ, Tử Diệm|
|Huyền Bút/Thủy|Thủy Ấn0–5|nét mực/dấu chấm/gợn, đưa-buông-ngừng, xanh mực-cyan|Mực Triều, Hàn Châm, Thủy Kính, Mưa Tinh, Lưu Thủy Bộ, Long Mạch Hồi Nguyên|
|Thạch Chùy/Thổ|Thế0–5|khối vuông/nứt/phiến thấp, có trọng lượng nhưng không che, xám-ochre|Trấn Sơn, Chấn Địa, Thiết Bích, Khiêu Chiến, Phá Nham, Sơn Thần Giáng Thế|
|Linh Cung/Mộc|Mộc Tiêu0–5|nhánh/lá/mũi tên, chuyển động mở tán và rơi, rêu-jade-ngà|Khóa Mạch, Dây Gai, Liên Châu, Tán Hoa, Phi Diệp, Bách Tiễn Quy Tông|

Không mọi đòn của Hỏa là fireball, mọi Thủy là bong bóng, mọi Mộc là rồng xanh. Spell mạnh hơn không đồng nghĩa lớn/đặc hơn vô hạn. Seed palette trong JSON là đề xuất art; source native nên8–12màu/VFX component,4tone chính, outline tối riêng. Sprite actor giữ bảng màu của nó.

## Nguồn để Muse làm

- `Art_Concept_References/skill_vfx_v1/01..05_*.png`: mood/shape/ba pha, đã xem bằng mắt; không phải spritesheet cắt sẵn.
- `Skill_VFX_Cards_v1_vi.md`: đủ30skill, prep/release/fade, attach point, cue, icon, sound, LowFX.
- `Implementation/Content/DesignBaselines/skill_vfx_art_v1.json`: cùng thẻ dạng dữ liệu, activation design-only; không vào loader gameplay hiện có.
- `Art_Concept_References/skill_vfx_v1/generation_prompts.json`: prompt gốc và tool built-in.

Các bảng cân bằng/decision thắng hình. Board là trình diễn pose từ góc dễ đọc, không thay top-down gameplay; không copy tư thế mannequin làm skeleton nhân vật8hướng.

## Những sai lệch ảnh sinh phải sửa trước asset

1. MK04 board dựng vòng lớn quanh toàn người: runtime chỉ viền khiên mỏng theo spec, không bít thân. MK01 có counter trong cột RELEASE chỉ dùng khi đỡ thành công, không phát mọi lần cast.
2. AD02 board có dấu quanh caster: phải đặt dấu tại TARGET và chờ đòn trigger; expire bình thường không nổ. AD04 có các dấu dưới đất rộng: thu về chân target, không tự thêm AoE.
3. HB05 nhìn giống sóng đánh: chỉ trail lùi, không projectile/collider/hit spark. HB03 là shield ally; HB06 không hồi sinh hoặc cleanse mọi status.
4. TC04 debris nhiều như đòn damage: taunt mặc định không damage, đổi thành ripple/chevron. TC06 phiến trên board cao: runtime slab thấp0,55m=1,1WU, lối camera mở, không collision chặn ally/projectile/telegraph.
5. LC03 board trình diễn tên đồng thời: runtime5phát cách0,11s, tối đa3hit cùng mục tiêu. LC06 board không chứng minh4đợt,3glyph hay radius; phải làm timeline và ground cue thật theo server.
6. Vòng đất nhìn ellipse trong concept chỉ là trình bày. Ground telegraph/hit shape thực phải theo XY server và camera projection, không lấy ellipse trong board làm bounds.

## Sprite sheet và module dễ sản xuất

Mỗi component riêng: cast/travel/impact/buff/status/miss/end. Không bake actor hoặc nền than vào PNG hiệu ứng. Master PNG RGBA trong suốt thật; RGB vùng alpha0 không có black matte/halo; point/no mipmap/lossless,20PPU khi là world sprite. Kiểm PNG ở nền sáng/tối.

Standard cell64×64/128×128; module lớn256×256/512×512 theo thẻ, atlas page<=2048². Dòng thẳng/ring lớn dùng module đoạn/corner và UV/tile được pixel-snap; đừng scale một vụ nổ64px lên đường kính32WU làm pixel khổng lồ, cũng không vẽ một full-frame4096px. Module size là texture budget, **không** radius/range skill. HB06 radius16WU/LC06 radius12WU phải có biên đúng nhưng có thể dùng ring segments thay ảnh đặc toàn vùng.

Mỗi skill có budget keyframe2prep+3release+3fade ở12fps để bắt đầu art; các pha hold/loop/tick theo gameplay timeline, không lấy8/12s thay thời gian hiệu lực. Buff4s giữ loop/state đến end; mark5s hết theo server; trap4s giữ rồi retract; ultimate sanctuary5–7s theo tài nguyên. Không tắt status vì animation one-shot hết sớm.

Directional slash/projectile làm orientation mẫu E trước, sau đó đủ8direction nếu art không giữ pixel khi xoay góc45°. Đối xứng có thể reuse khi thực sự đúng; spell position theo vector server không bắt actor aim vào8hướng để tiện vẽ. Camera/render snap, không lượng tử hóa gameplay hitbox.

Asset convention: `VFX_SK_MK_01_CAST`, `_COUNTER`, `_END`... file `sk_mk_01_cast.png`; mỗi component có cell size, frame list, fps, pivot, anchors, attach, lifetime policy, palette/source/license, alpha proof, LowFX variant. Không đưa board vào runtime manifest. Icon32×32native (preview64/96), không vẽ icon128 rồi downsample tự do; cooldown overlay do client, không bake số vào icon. Mọi skill name vẫn localization key.

## Mapping sự kiện và kết quả

Cue semantic trong JSON là tên thiết kế nội bộ, chưa phải enum event trên wire. Hiện P1 chỉ có contract hạn chế; integration adapter/proposal cần ánh xạ castAccepted, counterSuccess, shieldState, projectileHit, healTick... khi backend thực sự phát được. Không nhét tên mới vào CombatEvent enum mà không migration.

| Tình huống | Hiển thị đúng |
|---|---|
|Input dự đoán|chỉ animation chuẩn bị không xác nhận trúng; không tiêu số MP/CD trên UI như đã commit|
|Cast accepted|phát release phù hợp castId, attach đúng caster/target/ground|
|Rejected|cancel prep ngắn, không impact/damage popup; trả actor về state server|
|Miss/target chết trước hit|travel có thể tan tại điểm server, không giả spark trúng hay mark|
|Parry không có đòn chạm|guard end thường, không counter flash hoặc tăng Kiếm Ý giả|
|Status refresh|update expiry/strength, không spawn thêm nhiều cùng vòng|
|Reconnect|query state, recreate buff/zone còn active, không replay hit/explosion cũ|
|Duplicate/out-of-order|dedupe castId+eventId, state revision thắng, không nhân sound/VFX|
|Map transition/despawn|dọn pool instance cũ, không để ring theo actor sang map mới|

VFX không có Physics collider để tự gây damage. Projectile gameplay position/impact đến từ server; client trail không quyết định xuyên tường. CastId/sourceId/targetId/mapInstanceId/generation là keys pool; end/unsubscribe phải trả pool.

## Thứ tự layer và khả năng đọc

Ground decorative→ground skill outline→foot shadow→actors/weapon→impact fragments→critical warning overlay. Cụm particle có khoảng trống ở mặt và vùng chạm chân actor. Ally skill không dùng cùng solid red fill của enemy danger; phân biệt bằng pattern/outline/icon, không chỉ hue. PvP team palettes đổi accent viền, vẫn giữ shape của lớp.

LowFX bỏ debris/extra sparks/secondary layers, giữ đủ cue shape và hit/status indicator. Không giảm phạm vi hoặc giấu vùng boss. Mức đầu P1: tối đa8pooled skill instances hiển thị chính trong một camera, tick VFX12fps riêng gameplay60fps; khi vượt ưu tiên boss warning→self→party→other. Đây là budget thử nghiệm, đo trên thiết bị trước launch; không xóa gameplay entities để giảm GPU.

Rung0..2logical pixel, <=0,12s cho ultimate nếu bật; không full-screen flash, không bloom. Lớp không chia sẻ âm y hệt: Kim khô/ngắn, Hỏa cinders thấp, Thủy mực/giọt, Thổ trầm có đuôi ngắn, Mộc dây cung/lá. SoundKey là request chưa có clip; silence fallback được ghi thiếu asset, không lấy audio từ game tham khảo.

## Gate Muse và backlog

1. MK01 một guard/counter prototype và HB04 một heal-zone: mỗi component native PNG+palette+timeline, contact sheet3pha, preview nền sáng/tối. Hai ví dụ kiểm cả hit và support trước làm full30.
2. Review silhouette/size/alpha và event semantics; sửa ảnh sinh lệch theo danh sách trên. Sau đó3skill đầu Minh Kiếm và1quái target.
3. Làm các slot5mobility cho cả5lớp, xác minh movement-only không impact trừ Phá Nham/Phi Diệp có hit riêng. Tiếp tục shields/marks rồi ultimates cuối.
4. Mỗi batch1–3skill, manifest/preview/defects; chưa tự vẽ toàn bộ8hướng×30spell×8frame khi mẫu đầu chưa duyệt.
5. Trước done: show cùng một skill trong top-down640×360 combat và hub wide nếu được preview, trên light/dark terrain, hai actor chồng hiệu ứng và LowFX. Hub thật vẫn không cho dùng combat skill trái safe-zone policy; preview là test scene riêng.

Giao artwork/prompt v1 không đồng nghĩa30skill đã code, có animation runtime hoặc balance pass. Asset chỉ được lên ART_APPROVED/ENGINE_IMPORTED khi có bằng chứng đúng giai đoạn.
