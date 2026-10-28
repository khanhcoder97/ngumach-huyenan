# BỘ TÀI LIỆU SẢN XUẤT
## Ngũ Mạch: Huyền Ấn — Production Index v1.2

### 1. Mục đích

Bộ tài liệu chuyển ý tưởng MMORPG 2D nhìn từ trên thành đặc tả có thể chia việc cho đội gameplay, narrative, UI/UX, 2D art, level design, backend và QA. Tên Ngũ Mạch: Huyền Ấn hiện là tên làm việc, chưa tra cứu hoặc đăng ký thương hiệu.

Đây là game mới, chỉ dùng KPAH làm tham chiếu ở mức thể loại/vòng lặp MMORPG 2D cổ điển. JAR đã phân tích chứa bytecode Java và tài nguyên đóng gói, không chứa mã nguồn Java gốc đầy đủ hay nội dung máy chủ để xác thực toàn bộ cốt truyện/cân bằng. Tên phái, truyện, nhân vật, nhiệm vụ, map, UI, con số và asset trong các tài liệu này là thiết kế mới. Không chép tên nhân vật, thoại, bản đồ, hình, âm thanh hoặc dữ liệu độc quyền của KPAH.

### 2. Danh mục tài liệu

| Tài liệu | Dùng cho | Độ ưu tiên |
|---|---|---|
| GDD_Ngu_Mach_Huyen_An_vi.md | tầm nhìn, game loop, hệ thống tổng, tiến trình, phạm vi, kiến trúc | nguồn chuẩn tổng |
| Quest_and_Narrative_Production_Spec_vi.md | 36 quest chính, 40 quest phụ, thoại, trigger, checkpoint, reward/unlock | narrative/quest |
| Content_Bible_Ngu_Mach_Huyen_An_vi.md | cốt truyện tóm tắt, 30 kỹ năng và số cấp 1, item mẫu, recipe, hoạt động | content data |
| Combat_Skills_VFX_Animation_Spec_vi.md | 30 skill, thời gian hoạt ảnh, hitbox, telegraph, VFX, audio, giảm hiệu ứng | combat/animation/VFX |
| UI_UX_Spec_vi.md | layout HUD, mobile/PC, panel, bag, character, flow và accessibility | UI/UX |
| Gameplay_HUD_Overlay_Spec_vi.md | HUD gameplay chi tiết: status bars, minimap, quest tracker, joystick, skill arc, responsive states, data contract và DOM layer | gameplay UI/client |
| Settings_Overlay_Spec_vi.md | modal cài đặt: responsive grid, input/graphics/audio/HUD, tài khoản, preview/rollback, accessibility và HTML structure | UI/client/account |
| Forge_Crafting_Overlay_Spec_vi.md | modal lò rèn: catalog/recipe, cường hóa +0…+15, khảm, tinh luyện, sửa chữa, phân giải, nguyên liệu và giao dịch | item UX/gameplay/client/backend |
| Compendium_Encyclopedia_Overlay_Spec_vi.md | Bách khoa Lạc Châu: catalog 2.532 record dự kiến, search/filter, khám phá/spoiler, inspector, nguồn sở hữu, điều hướng và sync | UI/content/client/backend |
| Thang_Long_Thanh_Capital_Map_Spec_vi.md | thủ phủ 900×96 WU, 9 khu phố, 17 NPC dịch vụ, portal route, story C1-06, giải PvP Long Môn | level design/world/economy/PvP/UI |
| Appearance_Buff_NPC_Service_Overlay_Spec_vi.md | phòng thay đồ 2D, ngoại trang, chỉnh diện mạo, buff/auto-use, lệnh boss giới hạn và mạng dịch vụ NPC | UI/item/content/client/backend |
| Character_Equipment_Inventory_Spec_vi.md | class/character, stat, gear slots, quality, item schema, inventory/craft | gameplay/economy |
| Map_Production_Atlas_vi.md | 9 map, tọa độ blockout, props, NPC, spawn groups, portals, respawn | level design/world art |
| World_Spawn_Gathering_Manifest_Spec_vi.md | schema và quy ước cho 349 vị trí NPC/quái/boss/node/object/activity trên 46 map ID | level design/gameplay/data |
| World_Spawn_Gathering_Manifest_vi.csv | 349 hàng import-ready; mỗi hàng có tọa độ, điều kiện, respawn, drop hoặc sản lượng node/điểm câu cá | world/content data import |
| World_Spawn_Gathering_Manifest_vi.xlsx | bản bảng tính để lọc, rà soát và duyệt manifest | world/content review |
| Production_Readiness_Audit_vi.md | mức sẵn sàng, điểm mâu thuẫn, khoảng trống P0/P1/P2 và thứ tự hoàn thiện trước content lock | producer/design/engineering |
| Production_Decision_Register_vi.md | nguồn chuẩn DEC-001…014 cho engine, pixel art, raid, PvP, reset, reconnect, nội tại, boss tuần và quyền nội dung | tất cả domain |
| Production_Technical_Contracts_vi.md | API/event envelopes, schema dữ liệu, idempotency, errors, persistence, security và SLO baseline | client/backend/integration |
| Production_QA_Release_Gates_vi.md | test matrix, tiêu chí nghiệm thu P0–P6, load/chaos/security/accessibility và release gates | QA/producer/ops |
| Class_Passive_Production_Data_vi.csv | 40 node nội tại có ID, nhánh, cấp, prereq, effect key/value và cap PvP/boss | gameplay/data import |
| Battleground_10v10_Production_Spec_vi.md | luật chiến trường Trấn Sơn 10v10, flow trận, map zone, spawn/objective, queue, score, reward và anti-AFK | PvP/backend/level design |
| Weekly_Boss_Rotation_Data_vi.csv | cấu hình boss Tháp tuần trỏ tới boss canonical, không tạo entity placeholder | encounter/live ops |
| Elite_Variant_Data_vi.csv | override prefab/stat/AI/telegraph/loot cho quái tinh anh | gameplay/art/data import |
| NPC_Actor_Production_Registry_vi.csv | 83 NPC canonical: archetype sprite-set refs, costume palette, animation, portrait/dialogue refs và service routing | art/narrative/world data |
| Pet_Mount_Production_Data_vi.csv | roster companion/mount, kỹ năng, tiến triển, hành vi và quyền lợi chiến đấu | systems/art/data import |
| Life_Sim_Content_Data_vi.csv | seed/crop/fish/bait/location/yield/timing/cap cho nông trại và câu cá | economy/content import |
| Life_Sim_Production_Spec_vi.md | farm pocket 5 luống, câu cá 6 vị trí, minigame, quota, persistence, anti-exploit, pet/mount rules | systems/economy/world |
| Quest_Dialogue_Production_Data_vi.csv | dialogue key, graph node, điều kiện, text, lựa chọn và cờ cho 76 quest | narrative/localization import |
| Loot_Recipe_Reward_Production_Data_vi.csv | 221 loot/recipe/reward rows có xác suất, guarantee, cap, sink và refs dữ liệu | economy/data import |
| Currency_Production_Data_vi.csv | 16 ID ví tiền tệ, ownership/trade policy, cap, reset, faucet/sink và nguồn phát hành; vé Mạch Triều giữ đúng dạng item | economy/backend/live ops |
| Guild_Social_Spec_vi.md | guild lifecycle/roles, treasury, quests, party/chat, 20v20 siege | social/PvP |
| Activities_Economy_PvP_Production_Spec_vi.md | 4 dungeon, 2 raid, 6 boss thế giới + raid boss cuối, 30 tầng, PvP, chợ, nghề, nông trại, lịch hoạt động | PvE/kinh tế/live ops |
| Art_Entity_Weather_UI_Visual_Bible_vi.md | tạo hình NPC/quái/boss, stat/AI baseline, weather FX, UI visual tokens và ngân sách asset | art/animation/VFX |
| Art_Production_Queue_P1_vi.md | queue asset P1 Bến Mưa: hero, NPC, mobs, Mãng Cốt, map kit, weather, VFX/UI; có ID, kỹ thuật, nghiệm thu và design blocker | art producer/character/environment/VFX/animation |
| Art_Brief_P1_Minh_Kiem_vi.md | brief pixel sprite sheet, turnaround, palette, clip và VFX binding Minh Kiếm P1; phân biệt proposal mỹ thuật với luật gameplay | character art/sprite animation/VFX |
| Pixel_Art_Production_Standard_vi.md | chuẩn pixel art toàn dự án: logical canvas, PPU, camera/import, spritesheets, VFX/UI và acceptance | art pipeline/client integration |
| MMORPG_Functional_Spec_vi.md | ma trận chức năng account, world, combat, quest, economy, social, PvP, safety/ops | gameplay/backend/product |
| Item_Catalog_and_Set_Bible_vi.md | rarity, stat pools, 35 bộ giáp, dòng ẩn, công thức scaling và quy tắc item | item design/balance |
| Item_Master_Catalog_vi.csv | 555 item template rows, trong đó 420 gear base templates và 135 item cố định | data import |
| Item_Rarity_Variant_Catalog_vi.csv | 2.235 dòng, trong đó 2.100 gear rarity variants có ID riêng | data import/content QA |
| AI_Agent_Implementation_Plan_vi.md | milestones, module boundaries, handoff prompt, integration gates | engineering |
| Development_Execution_Board_vi.md | phân vai Codex/OpenCode, thứ tự P0–P6, phụ thuộc art/code, trạng thái và blockers | production/engineering/art |

### 3. Quyết định thiết kế đã khóa cho bản tiền sản xuất

| Hạng mục | Quyết định |
|---|---|
| Thể loại/hình ảnh | MMORPG hành động 2D nhìn từ trên pixel art; frame-based sprites, tilemap và UI raster theo `Pixel_Art_Production_Standard_vi.md` |
| Nền tảng | PC + Android/iOS, dùng chung tài khoản/máy chủ; mobile chơi ngang |
| Engine baseline | Unity 6.3 LTS/C#, backend authoritative; thay engine cần cập nhật kiến trúc |
| Camera/world | camera orthographic nhìn từ trên; 1 WU=0,5m; vùng chuẩn 360×72 WU; Thăng Long Thành 900×96 WU; Y=0 là trục đường tham chiếu trên mặt đất |
| Môn phái | Minh Kiếm/Kim, Ảnh Đao/Hỏa, Huyền Bút/Thủy, Thạch Chùy/Thổ, Linh Cung/Mộc |
| Campaign | 6 chương, cấp 1–100; 36 quest chính và 40 quest phụ trong bản tài liệu |
| Endgame | 4 dungeon 5 người, 2 raid 10 người × 3 encounter, 6 boss thế giới + 1 raid boss cuối, Tháp Lạc Ấn 30 tầng |
| World map | Bến Mưa, Thanh Lạc, Thăng Long Thành, Lâm Triều, Sa Hỏa, Trấn Sơn, Bạch Uyên, Vực Nghịch Mạch, Đại Ngũ Mạch |
| Gear | 12 slot nhân vật theo GDD; 4 slot thú; túi 100 ô; kho cá nhân 120 ô |
| Multiplayer | party 5, raid 10, Trấn Sơn battleground 10v10, công thành 20v20; server mô phỏng authoritative 20 tick/s |
| Art/performance | 60 FPS PC/máy cao, 30 FPS ổn định ở máy mobile thấp; tùy chọn giảm hạt/lóe/rung |
| Content ID | ID machine-safe ASCII; tên hiển thị/localization tách khỏi ID; mọi reward transaction idempotent |

### 4. Thứ tự nguồn dữ liệu khi có mâu thuẫn

1. Production Decision Register khóa các giá trị cross-domain và thắng dữ liệu cũ mâu thuẫn.
2. GDD giữ phạm vi, thuật ngữ và quan hệ hệ thống.
3. Đặc tả chuyên ngành giữ chi tiết triển khai thuộc domain.
4. Content Bible giữ số chiến đấu/cost/cooldown cấp 1; CSV runtime-data có ID cụ thể thắng ví dụ văn bản.
5. Bảng config/data đã version trong engine/server mới là runtime source; không hardcode gameplay vào animation hoặc UI.

Nếu phát hiện hai tài liệu khác nhau, tạo change note gồm: ID/field, giá trị cũ, giá trị mới, tài liệu bị ảnh hưởng, migration khi có save data. Không tự đổi ID đã đi vào client/server hoặc lưu trữ.

### 5. Phân chia việc cho AI agent

| Nhóm/agent | Đầu vào bắt buộc | Sản phẩm bàn giao |
|---|---|---|
| Core/gameplay | GDD, Character spec, Content Bible | class/data definitions, movement/combat commands, inventory transaction |
| Narrative/quest | Quest spec, Map Atlas | quest graph, dialogue keys, event triggers, reward IDs |
| UI/UX | UI spec, GDD | responsive mockups, UI states, localization-ready text keys |
| Combat/animation | Combat spec, Content Bible | sprite sheets/markers, frame tables, VFX, SFX, skill presentation |
| World/level | Map Atlas, Quest spec | 8 graybox scenes, prefab placements, collision, spawn/portal config |
| Social/backend | Guild spec, GDD | guild/party/chat/siege services, permissions, ledger/audit |
| Integration | toàn bộ docs | schema checks, ID registry, scene/data linking, release notes |

Không giao hai agent sửa cùng một schema hay ID registry song song. Mọi agent phải nêu phần tài liệu mình thực hiện, thay đổi ID nào, thay đổi số liệu nào, và những giả định chưa chốt.

### 6. Vertical slice bắt buộc trước sản xuất nội dung hàng loạt

Xây Bến Mưa từ x=0 đến x=202, bao gồm:
- Tạo nhân vật, chọn một phái, spawn tại x=18; di chuyển 8 hướng/đánh thường/né.
- HUD mobile + PC; portrait/HP/MP/quest tracker/minimap/6 skill slots.
- P00-01 đến P00-05; NPC Ly An/Tạ Vân Khanh/class trial; 3 kiện hàng, dân mắc kẹt, escort checkpoint và Mãng Cốt.
- 3 cụm quái thường, loot, túi 100 ô, trang bị EQ-[CLASS]-WEAPON-T1-R-COMMON, potion, quest reward idempotent.
- Cổng teleport sang Thanh Lạc; đổi scene vẫn giữ nhân vật và quest state.
- Pixel spritesheets frame-based, 5 vũ khí có thể thay, 6 animation combat mẫu, một VFX LowFX.
- Server-authoritative movement/combat tối thiểu; client không tự quyết hit/reward.

**Điều kiện qua slice:** cả PC và mobile hoàn thành chuỗi từ tạo nhân vật tới teleport mà không mất quest progress; telegraph boss đọc được với VFX thấp; UI không che nút/nhân vật ở 16:9/20:9; mọi ID map/NPC/quest/item resolve thành dữ liệu; mất kết nối trong nhận thưởng không nhân đôi hoặc mất item.

### 7. Quy tắc bàn giao nội dung

- Tên hiện trên UI nằm trong localization key, không nhúng trong code.
- Mỗi quest/objective/NPC/item/skill/map/spawn/portal có ID; map coordinates dùng WU.
- Kịch bản dialogue có key, người nói, bối cảnh, điều kiện, text ngắn/dài và lựa chọn nếu có.
- Mọi skill phải ghi PvE, boss, PvP coefficient; hit shape, range, duration, target cap, telegraph, VFX toggle.
- Item cần ghi stack, binding, source, sink, sell/trade/salvage, expiry, durability, rarity.
- Bất kỳ nội dung random nào phải có nguồn, tỷ lệ/giới hạn và pity/tiến độ đổi chắc chắn nếu ảnh hưởng reward.
- Teleport/quest checkpoints cần idempotent event để reconnect không mở cổng sai trạng thái.
- UI/state phải có loading, empty, error, disabled, offline, confirm, success/failure states.

### 8. Việc cần khóa trước production alpha

Các mục sau có giá trị đề xuất để xây slice; nhà sản xuất cần quyết định trước khi content lock:
1. Mô hình máy chủ theo khu vực, số người tối đa mỗi shard và lịch season.
2. Chính sách tên nhân vật, lọc chat, retention log và công cụ moderation.
3. Kinh tế: tốc độ sinh/tiêu Đồng, thuế chợ, cap bán/ngày, reset tuần.
4. Monetization. Khuyến nghị bán mỹ phẩm/tiện ích có giới hạn; không bán vé quay chiến đấu hoặc chỉ số mạnh.
5. Ranh giới PvP mở thế giới, vùng an toàn, level scaling và rule ghép siege.
6. Danh sách ngôn ngữ/voiceover; hiện tài liệu chỉ viết thoại tiếng Việt và localization-ready UI.
7. Bản quyền tên game, nhãn hiệu, font, âm nhạc, hình và asset; title hiện chưa cleared.




### Cập nhật bắt buộc 2026-10-28

- `Top_Down_Gameplay_World_Spec_vi.md`: DEC-016, trục XY, camera, footprint, input, collision, migration toàn bộ map.
- `Production_Completion_Addendum_vi.md`: điều kiện content lock, quest accept/reward, transaction, persistence, UI states và nghiệm thu.
- `Production_Audit_20261028_vi.md`: kết quả kiểm tra và phần bàn giao thực tế của agents.
- `../../Implementation/Reports/TopDown_Placement_Migration_20261028.json`: hàng đợi review 349 placement, chưa có tọa độ approved.

### Gói đặc tả bổ sung DEC-017

1. Production_Rules_Complete_v1_vi.md — baseline numeric và state rules cho progression/combat/AI/quest/item/social/UI.
2. Online_Persistence_Release_Complete_vi.md — account ownership, network, persistence/migration, rollout, monitoring/recovery và release evidence.
3. Content_Export_and_Asset_Completion_vi.md — field coverage, topology map, pixel/animation handoff và gate đủ nội dung.
4. ../../Implementation/Content/DesignBaselines/completion_v1.json — số liệu mới, trạng thái DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION.
5. ../../Implementation/Content/DesignBaselines/level_progression_v1.json — bảng100 cấp, EXP và point budget.

Các tài liệu mới xác định hành vi cần xây dựng; audit runtime vẫn chưa đạt full game. Chỉ cập nhật trạng thái đó khi có record/asset/implementation và evidence tương ứng.

### Narrative v2 / cinema (DEC-018)

- Narrative_Depth_and_Discovery_vi.md: canon/timeline/reveal gates, character arcs, chapter story, exploration và cinematic policy.
- Cinema_Muse_Directors_Pack_vi.md: đạo diễn, storyboard opening, audio/subtitle/continuity, prompt workflow và nghiệm thu.
- ../../Implementation/Content/Narrative/Narrative_Quest_Beats_v2.json: 76/76 quest có clue, câu hỏi, player agency và payoff riêng.
- ../../Implementation/Content/Narrative/Cinema_Production_Pack_v1.json: 20 cảnh/63 prompt shot6giây, dialogue, trigger, spoiler guard, fallback và delivery owner Muse.
- ../../Implementation/Tools/validate_narrative.py: kiểm coverage, refs, scene/shot IDs và duration; không chứng nhận chất lượng video hoặc canon bằng máy.

### Mẫu mỹ thuật và kế hoạch sửa chất lượng (2026-10-29)

- Art_Concept_References/v1/README_vi.md: năm board PNG, phạm vi reference, lỗi ảnh sinh cần sửa và gate native pose trước full animation.
- Art_Concept_References/v1/generation_prompts.json: prompt thực tế và công cụ built-in đã dùng.
- Art_Concept_References/v1/reference_manifest.json: kích thước/SHA256/status của từng board, không phải runtime asset manifest.
- Art_Completion_Plan_20261029_vi.md: thứ tự hoàn thiện slice, environment/UI/cinema/roster còn lại và phân công review.

- HUD_Skill_Arc_Layout_vi.md: cập nhật2026-10-29 theo chủ dự án,6slot tròn vòng cung quanh attack; concept06 thay layout grid của04.

### Thăng Long v2 và pixel giản lược

Capital_Scale_and_Simple_Pixel_v2_vi.md quy định extent12phường/chunk/migration và kit đơn giản. DesignBaselines/thang_long_layout_v2.json giữ target thiết kế chưa active; Art_Concept_References/v2 phân biệt macro overview và gameplay street corner.
