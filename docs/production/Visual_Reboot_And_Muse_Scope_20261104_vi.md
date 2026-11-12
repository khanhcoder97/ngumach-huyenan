# Thu hồi phạm vi Muse và làm lại toàn bộ hình ảnh

Quyết định theo lệnh trực tiếp mới nhất của chủ dự án, ID OWNER-MUSE-MEDIA-ONLY-20261104. Batch khởi tạo Visual_Reboot_20261104 được tiếp tục xuyên ngày; đây là change request đang có hiệu lực, không phải bản game đã làm lại hoàn tất.

## Quyền làm việc mới

| Phần việc | Chủ sở hữu |
|---|---|
| Toàn bộ mỹ thuật game, thiết kế nhân vật/NPC/quái, sprites/animation, map/tile, UI/UX/icons/fonts, VFX | Codex |
| Godot scenes, renderer, animation playback, input, camera, asset import và tích hợp video/audio | Codex |
| Lõi client C# độc lập engine, transport/presenters/contracts consumer/tests | OpenCode |
| Gameplay server và wire schema | Qoder local |
| Persistence/transaction/recovery | Qoder remote |
| Chỉ video/cinematic/âm thanh, source media, VO/music/SFX/ambience/stems/subtitles/manifests | Muse |

Muse phải dừng R1..R5 của work27 và mọi lệnh cũ giao graphics/runtime/UI/VFX/engine docs. Không commit tiếp111/112/22, không sửa asset/gameplay/source của Codex. Những PR đó đã đóng, branch giữ để đối chiếu. Các report/narrative/canonical IDs/game rules/map anchors vẫn là nguồn dữ liệu, không bị xóa vì thay hình ảnh. Antigravity vẫn thu hồi.

Repo hiện chỉ có admin chung khanhcoder97; không có collaborator Muse riêng để xóa mà không ảnh hưởng tài khoản của chủ dự án. Thu hồi này áp dụng phân công, PR acceptance và scope audit CI, **không phải** thay credential hay cam kết phân quyền tài khoản tuyệt đối. Policy máy đọc `Implementation/Coordination/agent_scope_v2.json`, guard dùng code/policy ở base branch và chỉ kiểm diff, không chạy code Muse từ PR.

## Làm lại hình ảnh có kiểm soát

Đồ họa cũ của Muse không là nguồn để crop/ghép thành bộ mới. Giữ như lịch sử, không đưa vào danh sách hình ảnh mới đã nghiệm thu. Không xóa worktree hoặc source gốc của người khác. Concept mới chỉ làm chuẩn màu/kiến trúc/tỷ lệ, **không cắt concept thành sprite hoặc map runtime**.

Hướng mới: pixel art top-down có chủ ý, nhân vật chibi gọn, sắc nét, cùng độ dày viền/ánh sáng/bảng màu; kiến trúc gỗ/ngói Việt fantasy, màu ngọc lam/xanh lúa/ochre/ngà/đồng tiết chế, khoảng đi bộ thoáng. Không dùng nền ảnh khổng lồ thay tilemap/collision. UI mới dựng từ thành phần sống, nhãn tiếng Việt/localization, skill6ô theo vòng cung quanh attack; không bake text vào art. Theo CAM-TOPDOWN-WIDE-20261105: default world1280×720/20PPU =64×36WU, gần nhìn thẳng từ trên, north-up; HUD CanvasLayer độc lập. Quy chuẩn32×18WU và hub48×27WU cũ bị thay thế. Camera mới đã có art staging, online AOI/PvP integration chưa nghiệm thu.

Nguồn mới ở `Art_Source/Visual_Reboot_20261104/`, prompt và output được lưu đầy đủ; dùng built-in imagegen. Từng PNG/sheet phải có trạng thái CANDIDATE→STRUCTURE_CHECKED→NATIVE_REVIEWED→ACCEPTED, không tự coi ảnh sinh đẹp là asset đã chạy đúng. Concept và một số candidate không đạt ràng buộc vẫn lưu để trace, không nạp runtime.

Sprite cần metadata explicit từng frame/direction/rect/pivot/foot anchor; không đoán cell48/64 từ tên file, không cắt qua người, không lật gương để giả đủ hướng, không reuse animation bằng cách đổi tên cùng một pose. Base body và equipment attachment có layer/anchor rõ, không ghép đầu/thân/chân từ ảnh khác để cứu lỗi. AI output không đúng kích thước phải được phát hiện; không chia nguyên chiều rộng bất chấp gutter hoặc rounding. Các phép đọc ảnh kiểm cấu trúc không được sửa bitmap âm thầm.

## Phạm vi thay thế toàn game

Tạo inventory coverage theo canonical ID:5class/8hướng/action set, mọi NPC/quái/boss, môi trường từng biome/map, gear/item icons, HUD/screens, VFX30skill và boss moves, weather. Mỗi entry có source/prompt/hash/rect/anchor/timing/scale/status/preview và dependency. Ưu tiên một Bến Mưa hoàn chỉnh đạt chất lượng, rồi áp dụng pipeline vào phần còn lại; không gọi cả game hoàn tất vì có một concept hoặc một sheet.

Giữ server-authoritative: animation/VFX không tự tính hit/cooldown/loot; hình học telegraph/timing theo contract đã chốt. Map mới vẫn đối chiếu tọa độ/nav version/hash với Qoder. Decision chặn306ô nước/giữ37ô bờ còn hiệu lực ở dữ liệu, không dùng art reboot để thay map geometry.

## Media của Muse

Muse làm trên muse/media-*; chỉ media/source/manifest/subtitle và công cụ encode/kiểm media trong phạm vi policy. Poster/still/storyboard chỉ phục vụ cinema, không biến thành sprites/UI/game map. Không sửa C#/Godot scenes/audio mixer/video player; Codex tích hợp engine. Không tự thay diện mạo nhân vật hoặc thế giới trong video; dùng reference mới do Codex cấp. Khi reference chưa khóa, tiếp timing/animatic/VO/music/SFX/subtitle/source pipeline, không dừng cả gói.

Runtime video OGV/Theora + poster, MP4 review/master; giữ narrative/cadence đã duyệt, SRT/voice/stems/license/actual files. Audio theo cue IDs và ngân sách đã có; không viết lại gameplay schema. Mọi asset âm thanh/video vẫn cần Codex review nghe/xem và engine QA; metadata không thay bằng chứng.
