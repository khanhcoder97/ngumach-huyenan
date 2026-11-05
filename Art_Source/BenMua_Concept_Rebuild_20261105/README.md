# Bến Mưa — dựng lại theo concept,05/11/2026

Nguồn chuẩn: Art_Source/Visual_Reboot_20261104/Concepts/ben_mua_topdown_wide_v2.png. Concept là reference về bố cục, màu và kiến trúc; không được dùng làm một nền lớn hoặc crop thành đồ vật.

Năm atlas mới được tạo riêng bằng built-in image_gen; prompt nguyên văn trong Prompts. PNG source và ClientGodot/assets/ben_mua_v3 trùng byte. Script inspect_environment.py chỉ đọc pixels và ghi metadataJSON, không crop/mask/resize/chỉnh ảnh. Ba object willow/bamboo/dock và workshop/stall dùng nguồn mới của Codex từ lôVisualReboot trước, không dùng artMuse.

| Atlas | Nội dung |
|---|---|
| village.png | nhà nhỏ, nhà vừa, đình, vườn rau,3mái chợ,thuyền mui |
| nature.png | đa,tán cây,đá bờ sông,bụi hoa,lau sậy,sen |
| ground.png | cỏ,đất,đá lát,nước,cỏ ẩm,lúa |
| details.png | xuồng,giếng,chum/giỏ,đá bước,hàng rào,bụi cỏ |
| villagers.png |6người dân hư cấu đứng yên; decor của scene, chưa là NPCdịch vụ |

Mỗi ảnh1536×1024. Manifest có29region alpha có padding và pivot chân. Region đình/chợ được khai báo riêng theo hình thực tế, không giả định mọi hình đều đúng512px/cell; không cắt mất đầu mái. Hero tiếp dùng basebody8hướng riêng của Codex; chưawalk/attack.

Đường, sân và sông là polygon2D có texture rời; cỏ nền dùng TileMapLayer. Texture lặp ở chu kỳ128–160pixel thế giới, không ép512xuống16 gây nhiễu như bản trước. Mirrored sampling chia sẻ mẫu ở mép và nearestfilter; chưa gọi đây là tileset artist-authored seamless hoàn tất mọibiome.

Bố cục ở ClientGodot/assets/ben_mua_v3/layout.json:113placementID độc lập,14tuyến,hai bờ sông,bridge/pierfootprints. Đây là ART_BM_STAGING_A2, không thay canonicalMAP_BEN_MUA/servernav/NPC/quest. Bản đồ128×96WU bao quanh khu concept64×36WU, camera chỉ thấy một phần. Đá/lau bờ sông được bố trí theo cùng đường cong bờ, có seed deterministic và bỏ vị trí cầu tàu.

Trạng thái: sourcecandidates đã kiểm cấu trúc và xem native; chưa là art toàngame đã nghiệm thu. NPCambient chưa có dịch vụ/animation. Chưa migration bản đồ online, không cấp EXP/loot/quest và không dùng source ảnhMuse. Hoạt ảnh nhân vật, nước sống, questNPC và mật độ crowd còn là gói tiếp sau.
