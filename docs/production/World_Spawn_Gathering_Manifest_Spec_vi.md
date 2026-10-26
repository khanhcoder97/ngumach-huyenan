# MANIFEST VỊ TRÍ NPC, QUÁI VÀ TÀI NGUYÊN
## Ngũ Mạch: Huyền Ấn — đặc tả dữ liệu world placement v1.0

### 1. Mục đích và phạm vi

Manifest là bảng bàn giao vị trí theo map cho level design, gameplay, narrative, art và backend. Mỗi hàng mô tả một NPC, một nhóm quái/boss, một node thu thập hoặc một vật thể tương tác có quy tắc xuất hiện. CSV là bản import; XLSX có cùng dữ liệu để rà soát thủ công.

| Tài sản | Vai trò |
|---|---|
| `World_Spawn_Gathering_Manifest_vi.csv` | Bảng chuẩn để import/đối chiếu data |
| `World_Spawn_Gathering_Manifest_vi.xlsx` | Bảng xem, lọc và kiểm duyệt theo cột |
| `Map_Production_Atlas_vi.md` | Hình học map, props, đường đi, điểm dịch chuyển và nguồn tọa độ thế giới |
| `Activities_Economy_PvP_Production_Spec_vi.md` | Encounter, giới hạn hoạt động, loot và quy tắc nghề |
| `Item_Master_Catalog_vi.csv` | Registry chuẩn cho item, vật liệu, công cụ và ID loot |

Phiên bản này có **349 hàng trên 46 map ID**: 9 map thế giới, biến thể công thành, 4 dungeon, 2 raid và 30 tầng Tháp Lạc Ấn. Phân loại gồm 104 hàng NPC, 163 nhóm quái, 29 vị trí encounter boss, 35 node thu thập và 18 hàng INTERACTABLE: hình nhân huấn luyện, đài triệu hồi boss tuần, 6 điểm câu cá và 10 anchor Trấn Sơn 10v10. Số hàng boss là số lần bố trí/phiên bản encounter, không phải số boss canonical duy nhất. BG10 dùng MAP_TRAN_SON_SIEGE/zone_id=BG10; không trộn với công thành 20v20.

### 2. Phạm vi theo map

| Map ID | Tên hiển thị | Hàng | Ghi chú |
|---|---|---:|---|
| `MAP_BEN_MUA` | Bến Mưa | 23 | Vùng tân thủ, nhiệm vụ, Mãng Cốt; 5 node nghề |
| `MAP_THANH_LAC` | Thành Thanh Lạc | 24 | Hub an toàn; quái chỉ trong encounter/nhiệm vụ riêng; 0 node khai thác nội thành |
| `MAP_THANG_LONG` | Thăng Long Thành | 25 | 17 anchor dịch vụ cố định + 8 anchor đám đông theo ngân sách; không có combat spawn/node |
| `MAP_LAM_TRIEU` | Rừng Lâm Triều | 23 | Campaign, Cổ Thụ Trăm Mắt và 5 node nghề |
| `MAP_SA_HOA` | Sa Hỏa | 28 | Campaign, Lò Trời và 5 node nghề |
| `MAP_TRAN_SON` | Trấn Sơn | 24 | Campaign, Tống Bành và 5 node nghề |
| `MAP_BACH_UYEN` | Bạch Uyên | 27 | Campaign, Mẫu Xà Thủy và 5 node nghề |
| `MAP_VUC_NGHICH_MACH` | Vực Nghịch Mạch | 25 | Endgame, campaign/raid lobby và 5 node nghề |
| `MAP_DAI_NGU_MACH` | Đại Ngũ Mạch / Mạch Triều | 32 | Event pool theo năm cánh, mini-boss và 5 node event |
| `MAP_TRAN_SON_SIEGE` | Trấn Sơn — Công Thành | 6 | Instance PvP 20v20; hàng nhóm spawn theo phe/phase |
| `MAP_DG_01`…`MAP_DG_04` | 4 dungeon | 21 | Encounter riêng; vị trí là placement proposal theo spec hoạt động |
| `MAP_RD_01`…`MAP_RD_02` | 2 raid | 9 | Nhóm objective/add và boss; instance 10 người |
| `MAP_LAC_AN_TOWER_F01`…`F30` | Tháp Lạc Ấn tầng 1–30 | 66 | 2 nhóm mỗi tầng; thêm 1 boss ở tầng 5/10/15/20/25/30 |

Map an toàn hoặc instance không có khai thác được ghi rõ trong ghi chú coverage. Không tạo node giả để làm đủ số lượng. Thăng Long, Thanh Lạc và các instance hoạt động dùng cấu hình sinh riêng nếu game design sau này mở tính năng tương ứng.

### 3. Nguồn dữ liệu và mức chốt

`design_state` phân biệt tọa độ/actor có trong tài liệu nguồn với phần đề xuất mới. Đây là field bắt buộc khi import; không gộp các trạng thái thành một loại “đã duyệt”.

| design_state | Ý nghĩa và cách dùng |
|---|---|
| `ATLAS_ANCHOR` | NPC/map anchor đã được ghi trong Atlas hoặc đặc tả map; giữ ID và điều kiện quest/service |
| `ATLAS_SPAWN` | Nhóm quái có ID, điểm hoặc vùng spawn đã ghi trong Atlas |
| `ATLAS_QUEST_WAVE` | Quái/wave gắn nhiệm vụ hoặc event quest trong Atlas |
| `ATLAS_QUEST_ACTOR` | Actor tương tác của quest, ví dụ hình nhân; không coi là quái nếu `record_type` khác |
| `ATLAS_BOSS` | Vị trí boss đã được ghi trong Atlas; phiên bản quest không đồng nghĩa world boss |
| `ATLAS_EVENT_POOL` | Spawn pool event Mạch Triều theo cánh và scheduler |
| `ACTIVITY_PLACEMENT` | Điểm đặt cho encounter dungeon/raid/tháp/công thành được xác định để thực thi, nhưng tọa độ cụ thể là proposal |
| `ACTIVITY_BOSS` | Bản ghi boss hoạt động hoặc world event; lịch/loot theo activity spec |
| `NEW_PROPOSED` | Tọa độ/resource/actor mới đề xuất trong manifest; cần duyệt khi blockout nhưng đã có cấu hình đầy đủ để tạo scene thử |

Trong bản này có 176 hàng `ATLAS_*`, 27 hàng `ACTIVITY_*` và 130 hàng `NEW_PROPOSED`. Tọa độ dungeon/raid/tháp là tọa độ local của instance; không dùng làm tọa độ trong map thế giới. Những điểm được đề xuất không được xem là dữ liệu đã có trong JAR hay nguồn lịch sử.

### 4. Quy ước tọa độ và nhóm

- Đơn vị không gian là **WU**; 1 WU = 0,5 m. `x_wu`,`y_wu` là tọa độ local của `map_id`. Trục X chạy theo hướng tiến của map ngang; Y là độ cao mặt đứng/platform, không phải tâm sprite. Chiều sâu layer dùng Z riêng ngoài manifest.
- Actor NPC/quái/node được neo tại tâm gameplay hoặc socket ghi trong `position_details`. Với NPC có tuần tra, `x_wu`,`y_wu` là điểm neo đầu tiên; `patrol_path` ghi các waypoint và thứ tự.
- `quantity` là tổng số actor/node trong bản ghi khi nhóm đầy đủ. `composition` nêu từng ID và số lượng; tổng số trong composition phải bằng `quantity`. Ví dụ: `MOB_DREAM_ROOT×3 + MOB_MOSS_BEAST×2` có `quantity=5`.
- Một hàng nhóm có thể chứa nhiều loại quái. `entity_id` giữ danh sách ID duy nhất, phân cách bằng `|`; `spawn_group_id` là khóa instance của nhóm. Các lần xuất hiện của cùng boss có thể chia sẻ `entity_id` nhưng phải khác `spawn_group_id` hoặc `map_id`.
- `patrol_radius_wu=0` nghĩa là đứng yên/giữ arena; để trống chỉ dùng khi không áp dụng. Đường escort/patrol có thứ tự rõ trong `patrol_path`; checkpoint và quest state được ghi tại `condition`/`notes`.
- Thang Long Thành có chiều dài 900 WU; map tiêu chuẩn và các activity arena dùng biên theo Map Atlas/activity spec. Trước khi dựng scene, kiểm tra tọa độ với vùng map, platform, collision và camera.

### 5. Từ điển cột CSV

| Cột | Bắt buộc | Định nghĩa |
|---|---|---|
| `record_id` | Có | Khóa duy nhất của hàng manifest; ổn định qua chỉnh sửa vị trí |
| `map_id`,`map_name` | Có | ID runtime và tên hiển thị/localized của map |
| `zone_id`,`zone_name` | Có | Khu/encounter con trong map; `OVERWORLD` dùng cho vùng chung |
| `record_type` | Có | `NPC`, `MOB_GROUP`, `BOSS`, `GATHER_NODE` hoặc `INTERACTABLE` |
| `design_state` | Có | Trạng thái nguồn/chốt theo bảng tại mục 3 |
| `entity_id`,`display_name_vi` | Có | ID một hoặc nhiều entity; tên hiển thị tiếng Việt, tên bản địa không phải khóa |
| `spawn_group_id` | Với nhóm | Khóa nhóm spawn/wave; không dùng thay entity ID |
| `composition`,`quantity` | Với nhóm | Thành phần nhóm và tổng actor; NPC đơn có số lượng mặc định 1 |
| `x_wu`,`y_wu`,`position_details` | Có | Điểm neo local và chú giải vùng/anchor/waypoint |
| `patrol_radius_wu`,`patrol_path` | Theo actor | Bán kính tuần tra và chuỗi waypoint; số 0 có nghĩa đứng yên |
| `character_level_min`,`character_level_max` | Có | Dải cấp khu vực/encounter. Với NPC và node đây là band của map, không phải cấp chiến đấu của actor |
| `condition` | Có | Điều kiện quest, unlock, scheduler, shard, party/phase hoặc trạng thái map |
| `respawn_seconds`,`respawn_policy` | Có | Timer dạng số giây; 0 không tự diễn giải là “respawn ngay”, phải đọc policy |
| `loot_table_id`,`drop_item_ids`,`drop_rule` | Quái/boss | ID loot table, pool ID item phân cách bằng `|`, cách rơi/giới hạn |
| `gather_profession`,`gather_item_id` | Node | Nghề `MINING`, `HERBALISM`, `LOGGING` và item đầu ra trong Item Master |
| `yield_min`,`yield_max`,`yield_spec` | Node | Sản lượng mỗi lần thu hoạch và xác suất bonus nếu có |
| `quality_tier`,`profession_level_required`,`tool_id` | Node | Tier I/II/III, level nghề tối thiểu và công cụ bắt buộc |
| `active_window` | Theo lịch | Cửa sổ event/giờ hoạt động; trống nếu spawn thường/quest-triggered |
| `art_ref`,`source_ref`,`notes` | Có | Prefab/sprite-set reference, tài liệu nguồn và ghi chú triển khai/kiểm tra |

### 6. Quy tắc xuất hiện, hồi sinh và tuần tra

1. **NPC:** actor bền vững theo quest/map state; không hồi sinh theo timer (`respawn_seconds=0`). `condition` quyết định actor hoặc chức năng dịch vụ có hiển thị không. Mỗi NPC có một anchor; escort dùng tuyến waypoint, không clone thêm actor ngoài khi quest yêu cầu.
2. **Mob thông thường:** spawn group xuất hiện khi map/quest/event cho phép; sau khi clear, hồi theo `respawn_seconds` và chính sách ghi trong `respawn_policy`. Nhóm thường tránh bán kính 18 WU quanh NPC/cổng/điểm nghỉ theo Atlas. Tọa độ 0 không có nghĩa nhóm luôn bật; ưu tiên điều kiện.
3. **Boss:** quest boss, instance boss và world boss là các lifecycle khác nhau. Quest/dungeon/raid reset theo wipe, checkpoint hoặc instance; world boss theo lịch 4 giờ, tối đa 12 phút; event có active window và contribution ledger. Không áp timer world boss cho bản quest cùng entity.
4. **Mạch Triều:** pool event theo cánh; nhóm N, elite và mini-boss được bật bởi scheduler/phase, tuân ngưỡng số actor đồng thời và contribution rule trong Map Atlas/Activities spec.
5. **Dungeon/raid/tháp/công thành:** placement row mô tả encounter group; timer farm không áp dụng nếu policy là reset encounter. Khi wipe, server khôi phục checkpoint và spawn lại theo ledger, không tạo thêm reward.
6. **Patrol:** bán kính tính quanh anchor; đường tuần tra phải nằm trong navmesh, không xuyên NPC/cổng/quest objective. Escort checkpoint thuộc `patrol_path`/`condition`, không được suy ra chỉ từ radius.

### 7. Quy tắc node và sản lượng thu thập

- Có **35 node**: 5 node tại mỗi map `MAP_BEN_MUA`, `MAP_LAM_TRIEU`, `MAP_SA_HOA`, `MAP_TRAN_SON`, `MAP_BACH_UYEN`, `MAP_VUC_NGHICH_MACH`, `MAP_DAI_NGU_MACH`. Map đô thị/thủ phủ và instance không đặt node trong phiên bản này.
- Sáu fishing interactable đặt tại Bến Mưa, Lâm Triều, Bạch Uyên, Vực Nghịch Mạch và hai bãi Đại Ngũ Mạch. Species/output/cap nằm trong Life_Sim_Content_Data_vi.csv; manifest ghi anchor, level, season/window và tool.
- Mỗi node thuộc một nghề và yêu cầu tool: khai khoáng → `TOOL-PICK-01`; hái dược → `TOOL-SICKLE-01`; đốn gỗ → `TOOL-HATCHET-01`. Item đầu ra phải resolve trong `Item_Master_Catalog_vi.csv`.
- Node hiển thị theo shard/người chơi để tránh tranh chấp last-hit. Khi đủ điều kiện, prompt tương tác; thời gian cơ sở 1,2 giây; bị đánh ngắt. `respawn_seconds` là hồi node riêng sau khi thu hoạch.
- Tier I cho 1–2, Tier II 2–3 và 15% cơ hội +1, Tier III 3–4 và 25% cơ hội +1. `yield_min/max` là khung cơ bản; `yield_spec` giữ xác suất thưởng phụ. Không nhân đôi output khi batch hoặc reconnect.
- Chất lượng node, level nghề, tool và sản lượng đều là proposal có thể cân bằng bằng config; không gắn lượng thu hoạch với FPS/client frame.

### 8. Drop và liên kết item

- `drop_item_ids` là **pool khả dụng**, không mặc định tất cả vật phẩm rơi cùng lúc. `drop_rule` ghi vật phẩm đảm bảo, xác suất/chọn pool, cache cá nhân, contribution, quest binding hoặc token.
- Boss cache phải cấp qua server-authoritative reward ledger; cùng `record_id` không thể cấp thưởng hai lần cho cùng event/run/account cap. Quest item được instanced; world boss dùng contribution, không last-hit.
- Tất cả ID trong `drop_item_ids`, `gather_item_id` và `tool_id` đã được kiểm tra có mặt trong Item Master. Phiên bản này bổ sung 7 vật liệu node và 3 công cụ nghề để bảng vị trí không tham chiếu ID mồ côi.
- Tỷ lệ loot thực tế phải là cột config runtime hoặc loot table riêng; nội dung `drop_rule` là giải thích đọc được cho designer. Khi cân bằng, cập nhật loot table và Compendium cùng change note, không viết tỷ lệ riêng vào code client.

### 9. Quy tắc import và kiểm tra trước khi build

- UTF-8 CSV, header đúng chính tả, một hàng cho một `record_id`; không thay ID do đổi tên hiển thị.
- Import theo thứ tự registry map/entity/item/tool → manifest placement → loot/activity. Lỗi ID phải chặn build data, không fallback thành tên text.
- Kiểm tra tự động: ID hàng không trùng; map/entity/name/coordinate/condition/policy không rỗng; `quantity` dương; tổng composition bằng quantity; level min ≤ max; tọa độ nằm trong boundary; reference item resolve; node có profession/tier/yield/tool; boss group có loot table hoặc lý do `NONE`.
- Kiểm tra trong editor: overlay tọa độ 20 WU; route navmesh; khoảng cách spawn-NPC/portal; không overlap quest wave với regular group; số NPC đám đông theo camera budget; mọi active window/condition có trigger; boss arena và exit an toàn.
- Thay tọa độ không đổi entity ID hoặc record ID. Nếu chia/tách nhóm, lưu migration note cho `spawn_group_id`, wave quest và loot ledger.

### 10. Các giới hạn cần chốt trước content lock

Các tọa độ/điểm đặt được gắn `NEW_PROPOSED` hoặc `ACTIVITY_PLACEMENT` là blockout có thể triển khai ngay nhưng vẫn cần level designer duyệt đường đi và camera. `respawn_seconds`, tỉ lệ drop/yield, shard cap và lịch event là giá trị thiết kế ban đầu, cần xác nhận trong playtest; server config là runtime source cuối cùng. Manifest không thay thế quest graph, pathfinding, loot-table balance hoặc thiết kế mesh/props chi tiết trong editor.


