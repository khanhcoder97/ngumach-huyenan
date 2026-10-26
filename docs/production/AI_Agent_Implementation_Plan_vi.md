# Ngũ Mạch: Huyền Ấn — kế hoạch giao việc cho AI agent

Tài liệu đi kèm GDD: GDD_Ngu_Mach_Huyen_An_vi.md. Production_Index_vi.md là danh mục tài liệu/nguồn chuẩn theo domain; mỗi agent phải đọc đặc tả chuyên ngành liên quan trước khi sửa schema hoặc nội dung. Kế hoạch này chuyển GDD thành các giai đoạn, ranh giới module và điều kiện nghiệm thu để nhiều agent có thể làm việc song song mà không tự suy diễn luật game.

## 1. Chốt kỹ thuật trước khi tạo project

- Client: Unity 6.3 LTS, C#, URP 2D và Pixel Perfect Camera; khóa editor/package bằng cấu hình version control. Animator nhân vật dùng sprite sheet frame-based.
- Server: C# backend trên runtime LTS đang được hỗ trợ tại lúc khởi dự án; máy chủ zone tách tiến trình, nhưng backend bản đầu là modular monolith.
- Lưu dữ liệu: PostgreSQL; Redis/cache tương đương cho session, tìm nhóm và dữ liệu tạm.
- Client-target: Windows, Android, iOS; xử lý input/UI theo nền tảng nhưng dùng chung gameplay/data schema.
- Hình ảnh: pixel art 2D. Tuân thủ `Pixel_Art_Production_Standard_vi.md`: logical 640×360, 20 PPU, integer scale, point filter, lossless/no mipmaps, pixel-snapped camera/sprites, sprite sheet frame-based. UI cũng pixel art.
- Mọi công thức thưởng/loot/sát thương/giao dịch do server quyết định.
- Tiếp tục scaffold hiện có, hoàn thiện hợp đồng kỹ thuật và pixel-art render/import pipeline; không kết nối tới server KPAH cũ.

## 2. Ranh giới module và chủ sở hữu

| Module | Trách nhiệm | Không được tự làm |
|---|---|---|
| Client Core | boot, login UI, input, camera, scene/map loader, UI navigation, localization | Không tính sát thương/loot/tiền |
| World/Art | map data, placement manifest, NPC/mob/node prefabs, colliders, tile/parallax layers, pixel sprite sheets/skins, VFX/audio hooks | Gameplay state không phụ thuộc frame art; không nhúng logic quest/skill vào animation |
| Game Server | session, zone instance, movement validation, combat state, monster AI, quest authority | Không nhận số liệu cuối do client tự tính |
| Content/Data | schema/ID/version, class/skill/item/map/quest/monster/loot tables, spawn group và gathering-node import/validation | Không dùng tên hiển thị làm ID |
| Progression/Inventory | character stats, XP, skill loadout, equipment, inventory, storage | Không thay API kinh tế mà chưa phối hợp |
| Economy | currency ledger, item binding, trade, marketplace, crafting transaction | Không commit đồng thời ở client và server |
| Social | party, friends/block, chat, guild, roles, guild quests | Không tin quyền do client gửi |
| Release/Ops | build platforms, logs, configuration, observability, moderation, support tools | Không đưa secret vào repository/client |

Mỗi module có thư mục, API public và dữ liệu sở hữu rõ. Thay đổi liên module phải cập nhật schema/API trước khi merge.

## 3. Giai đoạn triển khai và điều kiện nghiệm thu

### P0 — Khởi tạo nền (đầu tiên, không song song)

**Việc cần làm**
1. Tạo repo, branch policy, Unity project khóa phiên bản, cấu trúc Client/Server/Docs/Content/Tools.
2. Tạo quy ước ID, JSON/ScriptableObject schemas, versioning, localization key và config môi trường local/staging.
3. Tạo client mở được màn hình title và server health endpoint; logging có correlation ID.
4. Dùng Pixel Perfect Camera có sẵn trong URP 17.3 (không cài package Pixel Perfect riêng của Built-in RP); đặt reference 640×360, 20 PPU, point filter, no mipmaps, lossless sprites, grid snapping; thêm tilemap/frame-sprite smoke scene.
5. Tạo tài liệu API và bảng lỗi chuẩn; tạo nội dung giả lập hoàn toàn mới.

**Nghiệm thu**
- Máy mới có thể checkout và mở project theo README.
- Client vào được môi trường local, thấy thông báo server online/offline.
- Pixel test scene hiển thị đúng tại 720p/1080p/1440p bằng integer scale; tỉ lệ khác dùng viewport bars, không shimmer/blur/bleed.
- Schema ClassDefinition, SkillDefinition, ItemDefinition, MapDefinition, SpawnDefinition, GatheringNodeDefinition và QuestDefinition có ví dụ hợp lệ; importer kiểm tra manifest 349 hàng, ID resolve và giới hạn map.
- Không có URL/IP/token của KPAH cũ trong project mới.

### P1 — Vertical slice chơi được (ưu tiên cao nhất)

**Phạm vi cố định**
- Map Bến Mưa, một nhân vật Minh Kiếm, ba kỹ năng đầu, một quái thường, một quái tinh anh, boss Mãng Cốt.
- Một quest giao thư → điều tra đầm → boss → nhận thưởng.
- Một vũ khí, một món áo, thuốc HP, túi và trang bị; một điểm dịch chuyển.
- Môi trường local có server-authoritative movement/combat và lưu nhân vật.
- Asset mẫu là pixel art: nhân vật chạy/đánh/né, 2 địch, 1 boss, map tile/parallax; tất cả khớp grid 20 PPU và được xem ở 640×360 logical.

**Nghiệm thu**
- Người chơi tạo nhân vật, vào map, chạy/né, đánh trúng mục tiêu, hoàn quest, nhận vật phẩm, trang bị đồ, thoát và vào lại mà tiến độ còn.
- Boss có tối thiểu 3 đòn báo hiệu và một cơ chế môi trường; người chơi có thể né bằng thao tác hợp lệ.
- Hai client nhìn thấy cùng vị trí/kết quả chiến đấu; client sửa sát thương hoặc loot request không được server chấp nhận.
- Ở màn 720p/1080p/1440p sprite giữ cạnh sắc nhờ scale nguyên; viewport tỉ lệ lẻ letterbox, không resample phân số. UI pixel art hoạt động ở PC và landscape mobile safe area.

### P2 — Nền MMO và chiến đấu đủ năm lớp

**Việc cần làm**
- Login/character selection, session, zone routing, reconnect 120 giây; tournament reconnect một lần/90 giây.
- Hoàn thiện di chuyển, va chạm, quái thường/tinh anh, trạng thái buff/debuff, loot, map transition.
- Thêm đủ 5 môn phái, lựa chọn 4 active + mobility + ultimate, 2 loadout, 8 passive nodes/class và tối đa 2 passive đang trang bị.
- Party 5 người; EXP/loot cá nhân; status và invite.
- Data import/validation để thêm kỹ năng/quái mà không sửa code gameplay.

**Nghiệm thu**
- Lớp khác biệt về combo, phạm vi và vai trò nhưng cùng vượt được nội dung solo; không có lớp bắt buộc duy nhất.
- Combat resolve ở server; cooldown/MP/target/range và PvP coefficients đọc từ data.
- Disconnect/reconnect không nhân bản nhân vật, item hay quest rewards.
- Instance giới hạn sức chứa theo config; server có thể khởi chạy nhiều instance cùng vùng.

### P3 — Nhiệm vụ, tiến trình, đồ và chế tác

**Việc cần làm**
- Campaign quest state machine, hội thoại, tracker, daily/weekly reset.
- Level 1–100, XP, điểm chỉ số, học/nâng skill, mastery.
- 12 slot đồ, 4 slot pet, túi/kho, binding, độ bền.
- NPC shop; sửa đồ, phân giải, công thức, khảm, tinh luyện, cường hóa.
- Pet/mount, thu thập nghề, nông trại.

**Nghiệm thu**
- Quest state lưu đúng qua map/phiên; phần thưởng idempotent.
- Mọi thao tác đồ có preview chi phí và xác nhận; item khóa không rơi vào giao dịch/chợ.
- Cường hóa thất bại đúng thiết kế, không phá đồ/đổi cấp trái luật.
- Nội dung 6 chương có thể khai báo từ data; text không nằm rải trong code.

### P4 — Xã hội, kinh tế và PvP

**Việc cần làm**
- Friends/block/chat moderation; guild roles/quỹ/quest.
- Trade hai bên xác nhận; marketplace có escrow/thuế/tìm kiếm/lịch sử.
- Đấu tay đôi, đấu trường 3v3, Chiến Trường Trấn Sơn 10v10 (spec riêng), công thành guild 20v20.
- Công thành guild 20v20 và lịch đăng ký.
- Sổ ledger cho tiền/vật phẩm; logs hỗ trợ CS kiểm tra.

**Nghiệm thu**
- Race condition/timeout/cancel không tạo hoặc làm mất tiền/vật phẩm.
- Role/permission kiểm tra server-side.
- PvP dùng hệ số riêng; đồ/cấp không tạo chênh lệch vượt mục tiêu cân bằng.
- Báo cáo/mute/block có hiệu lực ở tất cả kênh chat tương ứng.

### P5 — Sản xuất nội dung bản đầu

**Việc cần làm**
- Đủ 7 vùng chiến đấu + Thanh Lạc nhập môn + Thăng Long Thành thủ phủ; 36 quest chính/40 quest phụ.
- Đủ quái, boss vùng, 4 dungeon, 2 raid, tháp thử thách.
- Tất cả bộ hình nhân vật, trang bị, thú, hiệu ứng và UI; bản mobile atlas.
- Sự kiện Mạch Triều và bảng lịch.
- Localize tiếng Việt, quản lý font/dấu, phụ đề và cỡ chữ.

**Nghiệm thu**
- Mỗi vùng có đủ danh sách nội dung trong GDD; không có placeholder UI/quest trong luồng người chơi.
- Quest dẫn đúng map/NPC/mục tiêu; không có soft-lock ở main campaign.
- Nội dung được đóng gói và version hóa; asset thiếu/mismatch ID được phát hiện trước build.

### P6 — Beta, phát hành và vận hành

**Việc cần làm**
- Tối ưu thời gian tải, RAM/texture mobile, FPS, reconnect, capacity.
- Staging/production config, backup/restore dữ liệu, dashboards/logging, moderation/reporting.
- Store cosmetics, event config, lịch reset, quy trình rollback và support.
- Tutorial onboarding, accessibility, privacy/data retention, thông báo bảo trì.

**Nghiệm thu**
- Có thể khôi phục account/character từ backup; có dashboard theo dõi login, disconnect, zone load, lỗi giao dịch.
- Có thể tắt một event/market listing bằng config mà không build lại client.
- Build PC/mobile đọc cùng version data và xử lý nâng cấp client/server tương thích.
- Các luồng login, tạo nhân vật, quest, item, party, chợ và PvP hoàn tất mà không cần tool nội bộ.

## 4. Hướng dẫn cho các agent

Mọi agent nhận các nguyên tắc sau:

1. Đọc GDD trước khi sửa code; nếu GDD thiếu một chi tiết quan trọng, ghi câu hỏi/đề xuất trong decision log thay vì tự đặt luật.
2. Chỉ sửa module được giao; không đổi public API/schema của module khác âm thầm.
3. Data content phải có ID cố định, localization key, validation và ví dụ.
4. Không đưa quyền quyết định sát thương/loot/tiền vào client.
5. UI không được che telegraph; toàn bộ art runtime phải là pixel art đúng logical grid, không blur/bleed/shimmer hoặc upscale ảnh raster không chuẩn.
6. Không copy asset, thoại, endpoint, logo, tên nhân vật hay nội dung độc quyền từ JAR KPAH.
7. Mỗi bàn giao gồm: tệp đã đổi, API/data schema liên quan, cách chạy ở local, trạng thái còn thiếu, ảnh/video màn hình nếu có UI.
8. Dùng các điều kiện nghiệm thu của phase; không coi “compile được” là hoàn thành gameplay.

## 5. Prompt khởi động cho agent điều phối

> Bạn là agent điều phối dự án Ngũ Mạch: Huyền Ấn. Hãy đọc Production_Index_vi.md, Production_Decision_Register_vi.md, GDD_Ngu_Mach_Huyen_An_vi.md, Production_Technical_Contracts_vi.md và đặc tả domain trước khi làm. Bắt đầu P0, sau đó triển khai P1 vertical slice; không xây toàn bộ MMORPG trước khi slice được nghiệm thu. Dùng manifest và các CSV production data làm đầu vào import; giữ nguyên record/entity/map/item IDs. Giữ Unity 6.3 LTS/C#, server-authoritative gameplay, pixel-art 2D theo `Pixel_Art_Production_Standard_vi.md` (640×360 logical, 20 PPU, integer scale và point filtering). Nội dung, tên, hình ảnh và server phải là nội dung mới; JAR KPAH chỉ dùng làm tham khảo thể loại/hệ thống đã phân tích. Tạo decision log cho điểm chưa quy định, giữ module boundary, không tự ý thêm monetization tăng sức mạnh. Bàn giao từng phase theo Production_QA_Release_Gates_vi.md.

