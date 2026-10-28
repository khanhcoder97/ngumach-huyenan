# ART PRODUCTION QUEUE — VERTICAL SLICE BẾN MƯA


> DEC-016 (2026-10-28): áp dụng `Top_Down_Gameplay_World_Spec_vi.md`. Các bảng kích thước/placement cũ là blockout chưa nghiệm thu top-down. Y luôn là Bắc–Nam trên mặt đất. “Platform” là bệ/cầu/vùng an toàn có đường đi hoặc floor link, không yêu cầu nhảy; chiều cao silhouette/capsule cũ không dùng làm collider. ID được giữ; không tự chuyển tọa độ cũ thành độ cao.

## 1. Mục đích và nguồn chuẩn

Tài liệu này chuyển art bible thành một gói sản xuất có thứ tự cho P1. Đây là queue quản lý và nghiệm thu, không thay thế source art, sprite atlas hay animation clip. Quyết định màu sắc, tỷ lệ, layer, budget và naming lấy từ `Art_Entity_Weather_UI_Visual_Bible_vi.md`; gameplay cue lấy từ `Combat_Skills_VFX_Animation_Spec_vi.md`; ID/map/placement lấy từ Map Atlas và `World_Spawn_Gathering_Manifest_vi.csv`.

**Art lock:** pixel-art 2D frame-based cho fantasy võ hiệp huyền thuật Lạc Châu nguyên bản; dùng logical 640×360, 20 PPU, integer scale, point filtering, lossless sprite import và pixel-snapped camera. Tham chiếu chibi kiếm sĩ người dùng gửi ngày 2026-10-26; không sao chép cụ thể nhân vật/huy hiệu. Không trích xuất/tái tạo asset nhận diện từ KPAH/JAR. UI và telegraph không dùng màu làm tín hiệu duy nhất. Chi tiết ở `Pixel_Art_Production_Standard_vi.md`.

**Đơn vị:** 1 WU = 0,5 m; hero cell 48×64 px, footprint capsule ngang 1,2×0,6 WU; sprite nguồn cao tối đa 64 px ở 20 PPU, hiển thị tối đa 192 px ở 1080p scale 3×. Tile nền 16×16 px; placement data tiếp tục ghi WU. NPC/actor dùng pivot chân tại XY trên mặt đất; floorId riêng nếu cầu chồng đường. Animation không điều khiển vị trí authoritative của server.

**Open design issue:** tiêu chí P1 yêu cầu boss có tối thiểu 3 đòn telegraph; hồ sơ Mãng Cốt hiện mô tả quét thân và lặn/trồi nhưng chưa định nghĩa rõ đòn thứ ba. Phương án art/gameplay đề xuất để duyệt là quét đuôi thấp thành cung ngang, cue hình vòng/cung + tiếng rít trước 0,9s, không hất người chơi khỏi arena. Đây chỉ là đề xuất; animation/VFX cho đòn này giữ `BLOCKED_DESIGN_APPROVAL`, không coi là cơ chế đã khóa.

## 2. Phạm vi ưu tiên

Thứ tự khóa phụ thuộc P1: (1) camera/scale test và hero Minh Kiếm; (2) map Bến Mưa cùng rain states; (3) Cá Linh, Rễ Nước và Mãng Cốt; (4) cue ba kỹ năng và boss telegraph; (5) NPC/quest cast, item art và HUD presentation. Có thể dùng shape/debug actor trong code để kiểm cơ chế, nhưng phải gắn `DEBUG_ONLY`; không được trình bày chúng như art đã duyệt.

| Queue | Gói art | Deliverable cần bàn giao | Phụ thuộc / nghiệm thu |
|---|---|---|---|
| ART-P1-001 | Pixel scale/camera calibration | scene test 640×360 logical; hero cell 3,2 WU/64px, enemy 4 WU/80px, boss 15 WU/300px; output 720p/1080p/1440p | integer scale, no blur/bleed/shimmer; gameplay không lộ pixel crop bất công |
| ART-P1-002 | Hero Minh Kiếm | pixel character sheet front/side/back, palette/face/hair/weapon; sprite layers/variants, pixel anchors; source + atlas page tối đa 1024² | idle silhouette, team/target outline pixel overlay; dễ đọc nền sáng/tối; concept art pixel được duyệt |
| ART-P1-003 | Hero combat clips | sprite sheets idle/run/jump/fall/land/hurt/death/interact/combo 3 hit/dodge/SK-MK-01/02/03 | frame art khớp timing spec; event không gây damage; pivot ổn định; né giữ silhouette suốt clip |
| ART-P1-004 | Vũ khí/ngoại hình starter | `EQ-MK-WEAPON-T1`, `EQ-MK-CHEST-T1`, `COS-CLOAK-01`, `COS-WP-01` | thay được weapon/body layer; icon item tách actor render; không đổi hitbox/animation |
| ART-P1-005 | NPC cốt truyện | `NPC_LYAN`, `NPC_TA_VAN_KHANH`, `NPC_CLASS_TRIAL`, `NPC_BM_RESCUE_01`, `NPC_BM_RESCUE_02` | portrait/key đúng registry; idle 2–5s, talk/quest states; rescue before/after; không sinh bản sao Ly An khi escort |
| ART-P1-006 | NPC chức năng Bến Mưa | `NPC_MEDIC_BEN`, `NPC_FISHER_01`, `NPC_BOAT_KEEPER` | silhouette/prop/service icon riêng; 3 biến thể crowd không dùng cho named actor |
| ART-P1-007 | Cá Linh | `MOB_CARPLING`, pixel spritesheet frame-based, 8 clip: idle/turn/walk/run/telegraph/attack/hit/death | page 512²; đớp line cue ≥0,45s; hitbox nhỏ khớp art; point-filter preview |
| ART-P1-008 | Rễ Nước | `MOB_WATERROOT`, sprite sheets thân/rễ; 8 clip | vòng gợn pixel cue 0,7s; phần rễ lộ để phản công; collider không phủ vùng tương tác |
| ART-P1-009 | Kẻ Rình Bờ tinh anh | `MOB_SHORE_STALKER` + variant `MOB_SHORE_STALKER_ELITE` | palette/silhouette chung; elite có giáp vai/mắt tương phản; 11 clip; lao ngang cue rõ 0,6s |
| ART-P1-010 | Boss Mãng Cốt | `BOSS_MANG_COT`, pixel sheet nhiều góc/đốt thân, atlas pages 1024–2048², bounds 15 WU | 16–24 clip gồm phase/break; đầu/sừng gãy nhận diện; shape không che telegraph |
| ART-P1-011 | Boss cue: quét thân | cone/fan danger shape + tell animation/audio marker | báo 0,8–0,9s; pattern/edge icon dùng được với mù màu; layer trên weather/player FX |
| ART-P1-012 | Boss cue: lặn/trồi | vũng lặn, marker bọt theo điểm trồi, water burst thấp | lặn 1,2s; vị trí trồi báo trước; không che chân/lối né; cùng seed trên client |
| ART-P1-013 | Boss cue: đòn thứ ba chưa khóa | phương án đề xuất: quét đuôi thấp theo cung ngang; phase transition, hit/armor break | `BLOCKED_DESIGN_APPROVAL`; nếu được duyệt, cue ≥0,9s, không camera cut, giữ arena geometry |
| ART-P1-014 | Map Bến Mưa nền | 5 layer parallax: sky/rain distance, shoreline, playfield, foreground reeds/roof, near-water FX | 360×72 WU; cổng x=348, boss ring x=178; foreground không che NPC, interaction, telegraph |
| ART-P1-015 | Prop kit Bến Mưa | kho 18×12; cầu gỗ, bè, chuông/cọc, kiện hàng, đèn lồng, lau/cỏ/cây/đá; 3 biến thể mỗi họ nền lặp | pivot/collider rõ; nước trang trí non-collision; props quest có state riêng |
| ART-P1-016 | Weather Bến Mưa | pixel rain sheets, foreground/background emitters, mái nhỏ giọt, puddle ripple, palette/audio hook | transition sprite/palette step 8s; high 60/120 foreground/background; LowFX giảm 70% hạt trang trí |
| ART-P1-017 | Skill VFX Minh Kiếm | `SK-MK-01` lục giác đỡ chuẩn; `SK-MK-02` vệt trắng bạc lõi vàng; `SK-MK-03` ba cung kiếm | vfx tách cast/travel/impact/miss; 3 cung <0,22s; player silhouette và boss warning luôn đọc được |
| ART-P1-018 | FX hit/resource | hit sparks nhẹ, damage/crit marks, Kiếm Ý 5 vạch, buff/debuff icon | density cap; không flash màn hình; merge damage numbers >8 target |
| ART-P1-019 | HUD frame art | portrait frame, HP/MP/Thanh Mạch/EXP, quest marker, minimap frame, skill slot states | 16:9 + 20:9 + mobile safe area; normal/focus/cooldown/disabled/error; scale chữ 200% |
| ART-P1-020 | Item icon starter | `EQ-MK-WEAPON-T1`, `EQ-MK-CHEST-T1`, `POT-HP-01`, quest seal/package/potion materials dùng trong P00 | source 32²–64² pixel; rarity shape+color; icon pack lossless đúng pixel grid |
| ART-P1-021 | Boss/audio cue sheet | cue cast, warning, hit, successful dodge, phase, weak point; ambience rain/water/wood | cue chiến đấu không phụ thuộc audio; không quá tải khi party; có mute và LowFX equivalent |

## 3. Kỹ thuật giao asset

Root theo art bible: `Art/Characters/CLASS_MINH_KIEM`, `Art/Characters/NPC_ID`, `Art/Enemies/MOB_ID`, `Art/Bosses/BOSS_ID`, `Art/Environment/MAP_BEN_MUA`, `Art/UI/ComponentName`, `VFX/Skill/SKILL_ID`. Nếu Unity scaffold chuẩn hóa thành `Assets/Art/...`, giữ các leaf ID y nguyên và thêm `assetKey` trong registry; không đổi ID dữ liệu để khớp tên tệp.

Mỗi gói bàn giao gồm source pixel PNG/layer, export sprite sheet/atlas, cell/frame timing table, palette, PPU, pixel pivot/anchor, scale WU, collision guide, import preset desktop/mobile, thumbnail nền sáng/tối, LowFX variant và provenance/license. Không bone-warp actor runtime. File chưa có source/owner/permission không được đánh dấu `APPROVED`.

## 4. Rào chắn VFX/animation

- Boss telegraph render trên actor VFX và weather; off-screen line attack có edge cue.
- Max 2 persistent FX/actor; burst ≤40 hạt chính trên mobile, ≤120 trên high; hạt lặp bị giảm khi quá 12 combat FX trong vùng 8m.
- Weather high ≤120 foreground + 400 background pixel sprites; mobile ≤35 foreground + 150 background; không blur/post-processing.
- LowFX giữ nguyên silhouette, hình/pattern, thời lượng và vùng nguy hiểm; tắt spark pixel nhỏ, persistent pet trail và camera shake.
- Shake tối đa 0,12s; giảm hiệu ứng không làm mất cue gameplay; animation không tự bật/hủy hit.
- Không thay geometry, scale, pose hoặc VFX shape theo client để tạo lợi thế PvP; P1 là PvE nhưng dùng đúng chuẩn runtime về sau.

## 5. Trạng thái và cổng duyệt

Queue item vẫn chờ nghiệm thu. Hai SVG concept Minh Kiếm là hồ sơ cũ, không pixel art; không dùng làm texture, atlas hay upscale. Chưa item nào qua `CONCEPT_APPROVED`; `ART-P1-002` cần sprite concept pixel art mới. Cổng: `CONCEPT_APPROVED` → `SPRITE_APPROVED` → `ANIM_APPROVED` → `INTEGRATED` → `DEVICE_QA`. Người duyệt kiểm ID link, silhouette, pivot, 20 PPU, palette, frame cadence, telegraph readability, mobile memory/FPS, license/provenance và preview scale nguyên.

**Giới hạn công cụ hiện tại:** phiên làm việc này không cung cấp built-in image generation. Vì vậy chưa tạo concept raster hoặc sprite final; queue ghi rõ đầu ra cần làm để nghệ sĩ/phiên có ImageGen xử lý sau. Không dùng API/CLI image generator nếu chưa được người dùng chọn phương thức đó.

## Cơ chế Mãng Cốt bổ sung

Thiết kế ba đòn đã được cụ thể hóa tại Production_Rules_Complete_v1_vi.md mục4: cone quét thân, circle lặn/trồi và annulus vòng bọt. Dòng BLOCKED_DESIGN_APPROVAL cũ cho đề xuất đòn thứ ba là lịch sử; dùng baseline mới để tạo art prototype, chưa coi là cân bằng đã playtest.
