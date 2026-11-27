# Bộ nguồn hình mới — lô04/11, cập nhật05/11

Toàn bộ PNG mới được tạo bằng công cụ image_gen tích hợp. Prompt đầy đủ trong Prompts; source_inventory.json lưu kích thước thực/mode/SHA256. Đây là lô khởi đầu, chưa phải bộ art toàn game hoàn tất.

| Nguồn | Kết luận |
|---|---|
| Concepts/ben_mua_visual_target_v1.png | Concept màu; góc quá thấp, superseded |
| Concepts/ben_mua_topdown_wide_v2.png | Reference gần nhìn từ trên, rộng hơn; không dùng làm map runtime |
| Characters/MinhKiem/idle_8dir_candidate_v1.png | Loại khỏi runtime: kiếm/cầm tay không nhất quán |
| Characters/MinhKiem/idle_body_8dir_candidate_v2.png | Base body8hướng rỗng tay, structure checked/native preview; chưa animation |
| Terrain/ben_mua_terrain_16_candidate_v1.png | Không nạp runtime: grid1254không chia đều4, có đường phân ô |
| Terrain/terrain_24_candidate_v2.png | Atlas1536×1024,6×4cells256, structure checked/native preview; chưa seam-proof tất cả chuyển tiếp |
| Props/props_6_candidate_v1.png | Góc mặt tiền cũ, không nạp runtime |
| Props/props_6_topdown_candidate_v2.png | Mái chiếm ưu thế hơn, alpha thật; structure checked/native preview, chưa art final |

PNG1774×887 của hero không là sheet64px/cell. Runtime manifest dùng rect nguyên từng frame và chân neo từ alpha body. Không crop bitmap/source hoặc ghép đầu/thân/chân; renderer chỉ dùng regions hợp lệ. Equipment layer chưa sản xuất, không tự vẽ kiếm giả. Alpha props có fringe mức thấp và bodymax254, cần dọn bằng công cụ ảnh ở lượt art polish; native render đã xem, không giả định PNG background chỉ từ preview unpremultiplied.

ClientGodot/assets/reboot là copy byte-identical ba ảnh candidate đã chọn; validator chỉ đọc ảnh/ghiJSON, không chỉnh bitmap. AtlasTexture/TileMapLayer là cơ chế render, không cắt concept thành assets. Concept không được load vào scene.

Coverage còn phải làm: hoàn thiện8hướng×action thật của5class, equipment anchors, mọiNPC/quái/boss, từng biome/map/Thăng Long, itemicons, UI screens/interactive behavior/accessibility, toànVFX/weather. Giữ đúng canonical IDs, story/map placements. Mọi hình hiện tại vẫn candidate; cần quality review/native interaction/performance và production integration trước ACCEPTED.
