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

Tạo prototype nhân vật gốc `CLASS_MINH_KIEM` (asset prefix `minh_kiem`):

- Sheet 8 hướng, frame 48×64 px, 20 PPU.
- Idle: 4 frame/hướng, walk: 6 frame/hướng, run: 8 frame/hướng.
- Combat: attack_01 6 frame, hurt 3 frame, cast 6 frame, death 6 frame; tối thiểu hướng S/E/N/W trong đợt đầu, sau đó hoàn thiện 8 hướng.
- Tạo hình đúng DEC-015: tóc xanh gai, áo choàng đỏ, áo teal và kiếm vàng; tuyệt đối không mô phỏng sprite hay thiết kế cụ thể từ ảnh tham khảo.
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


## Cập nhật 2026-10-28

Đã có walk Minh Kiếm (PR #17). Ưu tiên tiếp theo: blockout Bến Mưa theo DEC-016/top-down XY; bổ sung idle/combat sau khi chốt timing server. Được duy trì builder/demo hiện có trên máy ảo Unity, bàn giao log exact SHA và video; không tự đổi server/network contract. Thăng Long tiếp tục trong backlog art, áp dụng topology nhìn từ trên.

## CINEMA-01 — Video fantasy narrative (2026-10-28)

Muse phụ trách storyboard và sản xuất video theo DEC-018. Đọc Narrative_Depth_and_Discovery_vi.md, Cinema_Muse_Directors_Pack_vi.md và Cinema_Production_Pack_v1.json. Thêm phạm vi được ghi: Art_Source/Cinematics/, Client/Assets/Cinematics/, Implementation/Content/Narrative/Deliveries/. Dùng manifest video sidecar riêng, không sửa manifest sprite v1. Bắt đầu CIN_001/002/004: contact sheets và animatic trước render final; kèm prompt/reference/model metadata, preview/stems/subtitle và log engine nếu đã chạy. Không tạo avatar Minh Kiếm cố định cho mọi người chơi; dùng offscreen/POV hoặc composite từ avatar được chọn. Không sửa server quest/reward state từ video callback. Branch muse/cinema-opening-ben-mua, PR liên kết issue cinema mới; báo tool limitations ngay, không nhận video chưa được tạo là done.

## ART-REV-01 — Native quality gate trước nhân rộng (2026-10-29)

Đọc docs/production/Art_Concept_References/v1/README_vi.md và Art_Completion_Plan_20261029_vi.md; kéo Git LFS để có5PNG. Dùng reference/invariants và sửa sai ảnh sinh được ghi cụ thể; không crop/resize board thành runtime sprite. Ưu tiên3pose Minh Kiếm S/SE/N native48×64 + preview4×, sau review mới8hướng/walk/attack. Board chưa là owner approval hoặc engine proof. Tách cinema #29 khỏi pose fix; dùng mẫu Ly An/Bến Mưa cho storyboard. Giao một bước đạt trước khi render128clip. Art/source master được lưu ở Art_Source/, PNG export runtime vào Client Assets và manifest hiện hành; không đưa board docs vào runtime manifest.
