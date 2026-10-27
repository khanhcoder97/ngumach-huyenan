# Muse — Pixel Art, Map, VFX và UI Asset

## Phạm vi sở hữu

Bạn sở hữu toàn bộ nội dung hình ảnh pixel art và chỉ ghi trong:

- `Client/Assets/Art/`
- `Client/Assets/UI/Art/`
- `Client/Assets/Tilemaps/`
- `Client/Assets/VFX/`
- `Client/Assets/Animation/`
- `Client/Assets/ArtManifests/`

Không sửa C# runtime, server, contracts, schema hoặc `docs/production/`.

## Chuẩn kỹ thuật bắt buộc

- 640×360 logical render, 20 PPU; pixel vuông sắc nét, Point filter, không blur/anti-alias.
- Master source giữ ngoài Unity hoặc trong `Art_Source/`, xuất PNG lossless vào Unity.
- Sprite nhân vật và quái theo 8 hướng: `N, NE, E, SE, S, SW, W, NW`.
- Hướng nhìn: dùng `S` làm hướng camera thấy mặt nhân vật; mọi sheet phải nhất quán pivot chân giữa.
- Mọi sheet có file manifest JSON gồm `id`, `frameWidth`, `frameHeight`, `directions`, `animations`, `fps`, `loop`, `pivot`.

## Backlog ưu tiên

### MUSE-01: Bộ chuẩn hình ảnh

1. Thiết lập palette nền: `core_32`, `environment_48`, `character_skin_hair`, `fx_24`.
2. Tạo style board: viền, bóng, nguồn sáng, tỉ lệ chibi, ví dụ nền đất/đá/nước/cây/nhà và UI khung đồng.
3. Tạo manifest `pixel_art_catalog.json` ghi trạng thái từng asset: `placeholder`, `draft`, `approved`.

### MUSE-02: Nhân vật chơi được

Tạo prototype nhân vật gốc `hero_vanguard`:

- Sheet 8 hướng, frame 48×64 px, 20 PPU.
- Idle: 4 frame/hướng, walk: 6 frame/hướng, run: 8 frame/hướng.
- Combat: attack_01 6 frame, hurt 3 frame, cast 6 frame, death 6 frame; tối thiểu hướng S/E/N/W trong đợt đầu, sau đó hoàn thiện 8 hướng.
- Bộ áo giáp lam than, viền vàng cũ, áo choàng ngắn; tuyệt đối không mô phỏng sprite hay thiết kế cụ thể từ ảnh tham khảo.
- Tạo animation event sheet: frame đánh trúng, frame bật VFX, frame kết thúc recovery.

### MUSE-03: Thăng Long Thành

Tạo `MAP_THANG_LONG` theo bản đồ thiết kế hiện có:

- Tile 16×16 px: đá lát, lối đất, bậc thềm, tường thành, mái ngói, cổng, cầu gỗ, nước, cỏ, cây, đá trang trí.
- 3 tileset: `thang_long_ground`, `thang_long_architecture`, `thang_long_props`.
- Tile palette và 3 map chunk minh họa: cổng nam, quảng trường/khán đài PvP, khu chợ và lò rèn.
- Tạo minimap icon pixel cho cổng dịch chuyển, NPC, lò rèn, chợ, bang hội, nhiệm vụ, PvP.
- Mỗi chunk có PNG overview, layer list và placement manifest để tích hợp Tilemap khi Unity workstream tiếp tục.

### MUSE-04: Quái, boss, thu thập

Theo ID canonical trong content, tạo roster theo thứ tự map đầu game:

- 5 quái thường, 2 quái tinh anh, 1 boss prototype; mỗi đối tượng có idle, move, attack, hurt, death.
- 3 node hái lượm và 3 khoáng mạch với trạng thái available/harvested/respawn.
- Boss có telegraph pixel rõ ràng: vòng vùng nguy hiểm, đường chém, vùng nổ.

### MUSE-05: VFX và UI art

- VFX prototype: chém vật lý, đạn phép, hồi máu, sát thương chí mạng, nhặt vật phẩm, dịch chuyển, nâng cấp thành công/thất bại.
- HUD/UI art: frame status, minimap frame, skill slot, hotbar, inventory slot, equipment slot, button normal/hover/disabled, tooltip, modal panel.
- UI chỉ cung cấp texture/9-slice/icon; OpenCode chịu trách nhiệm layout và xử lý tương tác.

## Bàn giao qua GitHub

Tuân thủ `Implementation/Asset_Handoff/GITHUB_COLLABORATION.md`: làm trên branch `muse/<scope>`, commit asset qua Git LFS, cập nhật manifest và mở Asset Handoff PR. Không gửi ZIP hay asset rời cho agent khác. CI kiểm tra manifest/PNG; engine import được ghi `unverified` cho đến khi có Unity-capable machine.

## Bàn giao cho các agent khác

- `Client/Assets/ArtManifests/muse_delivery_manifest.json` liệt kê đường dẫn, kích thước, PPU, pivot, animation state và trạng thái.
- `Client/Assets/ArtManifests/muse_integration_notes.md` ghi asset nào thay thế placeholder nào.
- Không ghi đè prefab/scene của Unity client workstream.

