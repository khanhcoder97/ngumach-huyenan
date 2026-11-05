# Combat visual batch — 05/11/2026

Codex sản xuất bằng **trình tạo ảnh tích hợp (image_gen)**; toàn bộ prompt ở Prompts/. PNG runtime là bản sao byte-identical của source, alpha nguyên gốc. Tools/ArtProduction/inspect_combat.py chỉ đọc pixel để kiểm separation/bounds và ghi JSON rect/pivot; không sửa bitmap.

- minh_kiem_walk_v1: 1536×1024, tám hướng × bốn pha, 32 whole-body frames. Source khoảng 208px/body, runtime36px. Chưa phải layered equipment.
- minh_kiem_attack_v1: **REJECTED**, một số sword vượt cell; giữ source lịch sử, không ship runtime.
- minh_kiem_attack_v2: replacement1536×1024, bốn pha ngang × tám hướng dọc,32whole-bodyframes.112px/body, runtime36px; sword cầm cùng tay theo hướng.
- minh_kiem_vfx_v1:1254×1254, sáu kỹ năng × sáu phase,209px/cell. Runtime Phản Quang/Tầm Long/Kiếm Trận/Thiết Y/Bạch Hồng/Vạn Tượng Quy Nhất; server quyết định hit, không VFX.
- ben_mua_questkit_v1: Ly An, Tạ Vân Khanh, thầy thuốc; kiện hàng, áo thưởng, túi tiền. Các người thực cao quá hàng512 theo prompt nên metadata dùng top608px, đồ ởy608..1024; giữ nguyên chân, không cắt theo grid giả.
- ben_mua_mobs_v1: Cá Linh và Rễ Nước, mỗi loại idle/attack/dead;512px/cell. Bind homogeneous runtime spawn01/02/03 theo catalog; mixed04 vẫn chưa resolved.
- ben_mua_nodes_v1: hai mạch quặng sắt, dược thảo, gốc gỗ, lá dược nổi, mảnh ấn decorative. Runtime chỉ bind exact node types có source; shard prop chưa tạo gameplay object/grant.
- minh_kiem_skill_icons_v1: sáu silhouette từ skill_vfx_art_v1, không dùng ảnh effect làm icon. HUD giữ vòng cung, glyph32px có hotkey riêng; hover tên và trạng thái chưa hỗ trợ online. Rect content tính từ alpha để dùng Atlas-region khi render, không sửa PNG.

source_manifest.json và runtime manifest.json chứa kích thước/SHA256/rect/pivot thực. Asset vẫn NATIVE_REVIEW_CANDIDATE: structural pass không chứng minh gait đẹp, tất cả direction đồng nhất hay art đã final. Native gallery và regression báo cáo riêng; chưa có đủ đồ họa năm class/30skill/boss/campaign.

Các reference NPC chỉ dùng làm character lock cho video; Muse không được sửa graphics/runtime. Nguồn canon câu thoại và quest vẫn tại repo, không lấy text trong bitmap.

- ben_mua_quest_markers_v1: bốn pha gợn nước và hai người dân với pose chờ/đứng. PNG tạo bằng image_gen tích hợp, prompt riêng; rect/pivot từ ảnh thật. Runtime chỉ bind exact ALPHA ripple/rescue IDs đã có trong snapshot; không tạo actor, không cộng tiến độ. Pose đứng hiện mới để review, không tự coi là đã cứu. Gallery có nhãn rõ, không phải vị trí spawn.
