# QOD-27 — Packet lựa chọn: pet/mount, elite, class-passive (kèm test migration)

Ngày 07/11/2026. Work order 31 Q6 yêu cầu: "Các bảng pet/elite/passive còn xung đột: một
packet chọn lựa với exact source/ảnh hưởng/test migration, không code cân bằng tự đoán,
không gọi catalog là service đã bật." Packet QOD-24 (pet/mount) đã nêu sáu câu hỏi nhưng
thiếu cột thứ ba — **test migration** — và không phủ elite/passive. Bổ sung ở đây, ghi
thêm chứ không xoá cái cũ.

Mọi số dưới đây đọc trực tiếp từ file nguồn đang ship, không lấy từ trí nhớ:

- `docs/production/Pet_Mount_Production_Data_vi.csv` — 10 dòng, cột gồm
  `entity_id, item_template_id, entity_type, display_name_vi, element, rarity, level_cap,
  unlock_source, active_skill_id, active_skill_effect, passive_skill_id, passive_effect,
  skill_unlock_levels, xp_source, equipment_slots, combat_rule, owner_range_wu,
  leash_behavior, feed_item_id, feed_cooldown_hours, feed_stat, animation_spec, rig_id`.
  Ví dụ dòng thật: `PET_MOC_LINH` / `PET-01` / `COMPANION` / "Mộc Linh" / `level_cap=30` /
  `active_skill_effect="owner 5% max HP heal; 45s ICD"`.
- `docs/production/Elite_Variant_Data_vi.csv` — 9 dòng elite, mỗi dòng có
  `variant_profile_id` (`elite_v1|v2|v3`) và `hp_multiplier` **1,8 / 1,65 / 2,0**,
  `damage_multiplier` 1,25 / 1,3 / 1,2, `move_speed_multiplier` 1,05 / 1,08 / 1,0,
  `level_delta=2`.
- `Implementation/Content/Runtime/combat_mob_stats_v1.json` — khối `elite` có
  `hpMultiplier: 6.0`, `attackMultiplier: 1.6`, `defenseMultiplier: 1.8`, và hàng reference
  `eliteReferenceLevel5 = {attack: 24.0, defense: 7.56, hp: 1152}`. Tức xung đột **không chỉ
  ở HP**: CSV nói damage 1,25/1,3/1,2 trong khi bundle nói attack 1,6 / defense 1,8 cho cùng
  khái niệm elite. Nếu chọn A1, phải sửa cả ba số, không chỉ `hpMultiplier`.
- `docs/production/Class_Passive_Production_Data_vi.csv` — 40 dòng, `node_tier` 1..4 với
  `unlock_level = 20 x tier`; cột `pvp_boss_cap` là **văn xuôi**, đo được **24 chuỗi khác
  nhau** trên 40 dòng, ví dụ `1 proc/30s`, `1 proc/3s`, `4% PvP; 2s`, `4% boss; PvP = 0`,
  `5%; boss 2%`, `6% PvP/boss`. Bộ phân loại của server là check
  `passive.catalog_cap_tokens_classify_and_report_the_rest` — nó phân loại theo bảy kind và
  **in ra những token nó không parse được** thay vì đoán. Con số "37/47 token parse được"
  tôi từng viết ở packet trước lấy từ văn liệu chứ không đo lại ở head này, nên bỏ khỏi
  packet này; số cần thiết ở đây là 24 dạng văn xuôi và sự tồn tại của các token chưa phân
  loại, và cả hai đều đã đo.

Trạng thái hiện tại của server với ba bảng này: **đã nạp thành data + đã pin bằng
self-check; chưa áp dụng vào đường đánh, chưa có route, chưa có gate nào bật.** Không dòng
nào trong packet này là "đã làm".

---

## A. elite — xung đột số nhân HP (2 lựa chọn)

| # | Lựa chọn | exact source | ảnh hưởng | test migration |
|---|---|---|---|---|
| A1 | **CSV đúng, bundle sai** → elite dùng 1,8/1,65/2,0 HP và 1,25/1,3/1,2 damage | `Elite_Variant_Data_vi.csv` cột `hp_multiplier`/`damage_multiplier`; bundle `combat_mob_stats_v1.json` khối `elite` (`hpMultiplier 6.0`, `attackMultiplier 1.6`, `defenseMultiplier 1.8`, `eliteReferenceLevel5.hp 1152`) | Số nhân elite HP giảm từ 6,0x về tối đa 2,0x (base 192: 1152 → 384) **và** damage/defense phải sửa theo; nếu chỉ sửa HP thì A1 chưa hoàn thành | `elite_the_runtime_bundle_and_the_approved_table_disagree_named` (ServiceSelfCheck.cs:9375) phải **đổi thành check đồng ý**, và `REFERENCE_L5` bundle cần sửa khối `elite` + `eliteReferenceLevel5`; các oracle DEC-022 (27/8/21/5, counter 32/49) và `mob-combat` (`mob_damage=30`, `counter_damage=34`) giữ nguyên vì chúng đánh vào hàng **không** elite — nếu một trong hai số đó đổi thì migration sai, đó là lý do tôi nói rõ ràng nào không được đụng |
| A2 | **Bundle đúng, CSV là tài liệu tham khảo** → giữ 6,0x | bundle `elite` | CSV production trở thành nguồn không có hiệu lực cho elite; mọi báo cáo sau này phải ghi "CSV elite multipliers are advisory" | Check hiện tại đã in cả hai số trên cùng một dòng nên **không cần sửa**; thay vào đó thêm một ghi chú `source-authority` vào report và vào README mục mob stats, để không ai "sửa CSV cho khớp" rồi tưởng đã cân bằng |

Mặc định tôi đề xuất: **không chọn**. Đây là quyết định cân bằng, không phải quyết định kỹ
thuật; A1 làm thay đổi sức mạnh elite mà chủ dự án chưa từng duyệt ở mức 2,0x.

## B. class-passive — `pvp_boss_cap` và "nạp chưa nghĩa là áp" (3 lựa chọn)

| # | Lựa chọn | exact source | ảnh hưởng | test migration |
|---|---|---|---|---|
| B1 | **Cấu trúc hoá chuỗi cap thành trường có kiểu** (`percent`, `procPerInterval`, `scope`) rồi mới áp | 24 chuỗi `pvp_boss_cap` khác nhau trên 40 dòng; check `passive.catalog_cap_tokens_classify_and_report_the_rest` phân loại theo bảy kind và in ra phần không parse được | Passive trở thành dữ liệu máy đọc được; các token chưa phân loại vẫn phải được báo cáo chứ không đoán | Bỏ hẳn các check so khớp chuỗi với văn xuôi; thay bằng một check cho mỗi kind đã cấu trúc, **và** một refusal test: một `pvp_boss_cap` không phân loại được phải làm startup fail. Không có phần refusal thì bộ check chỉ là decorative — đây là quy tắc tôi đã áp dụng cho validator TALK/portal |
| B2 | **Giữ văn xuôi, chỉ hiển thị** (client đọc `description_vi`) | `description_vi`, `icon_key`, `status` | Không có hiệu lực combat nào; server chỉ phục vụ dữ liệu trình bày | Không đổi oracle nào. Cần một check mới kiểu `passive_is_display_only` để nếu ai đó sau này áp passive vào damage path mà không có packet, check hiện tại (`19` cho basic, `8/10/17` cho MK-03) sẽ fail — thực tế check đó **đã tồn tại** và chính là lý do tôi nói "nạp không đồng nghĩa áp" |
| B3 | **Chọn một nhánh để áp trước** (ví dụ chỉ `effect_unit` đã đóng trong 5 đơn vị hiện có) | `effect_key`, `effect_value`, `effect_unit`, `equip_change_policy` | Một subset nhỏ có hiệu lực thật; phần còn lại vẫn chờ | Ngoài việc giữ nguyên oracle, mọi test áp dụng cần **thêm** chứ không sửa số cũ; và cần test refusal: passive thuộc kind chưa parse bị từ chối áp, không âm thầm coi là 0 |

Mặc định tôi đề xuất: B2 hôm nay, B1 khi có bản cấu trúc từ nguồn; B3 là quyết định cân bằng.

## C. pet/mount — sáu câu của packet QOD-24, thêm cột test migration

| # | Câu hỏi | exact source | ảnh hưởng | test migration |
|---|---|---|---|---|
| C1 | File nào sở hữu tên hiển thị cho 10 id chung? | cột `display_name_vi` của `Pet_Mount_Production_Data_vi.csv` vs catalogue canonical (bảng so sánh §2 report QOD-24) | Nếu CSV thắng thì một file `docs/production/**` phải sửa — **không thuộc quyền tôi** | Check đối chiếu id/tên hiện đang pin cả hai phía; migration = sửa một phía **có chủ đích**, không phải để nó im. Cần thêm refusal: tên rỗng hoặc id lạ phải fail startup |
| C2 | `level_cap` hay `required_level` thắng cho mount, và `level_cap` nghĩa là gì khi `xp_source: none`? | cột `level_cap`, `xp_source`, `skill_unlock_levels` | Quyết định có tồn tại "trần cấp độ" hay không; không có XP thì trần chỉ là nhãn | Check đang giữ nguyên hai cột; nếu chọn "trần vô nghĩa" thì xoá assertion về `level_cap` **kèm ghi chú lý do**, không lặng lẽ nới assert |
| C3 | 4 slot pet/mount có vào vocabulary wire không? | cột `equipment_slots` | v1 đóng băng 5 token, v2 có 12 slot người chơi; `PET_*`/`MOUNT_*` không thuộc cả hai. Đây là **đổi contract**, cần packet schema mới | `InventoryV2Slots.All` hiện bằng đúng 12 theo design; thêm slot mới sẽ làm fail cả `InventoryV2Slots` lẫn validate_contracts, nên migration phải gồm: schema mới + example + negative fixture **trước**, rồi mới tới array. Đó là thứ tự decision đã duyệt cho TALK/portal, tôi làm theo |
| C4 | Định nghĩa 10 skill id của companion (hệ số, target, ICD) | `active_skill_effect="owner 5% max HP heal; 45s ICD"`, `passive_effect="+3% gather speed"` | "0,35x owner attack" kiểu này cần một số hạng trong Production Rules §2 mà hiện **không có** → không thể áp mà không bịa | Thêm hàng vào skill catalogue thì `combat.catalog` (7 rows) fail có chủ đích; migration phải ghi số dòng mới **và** oracle cũ không được đổi. Nếu 8/10/17 dịch chuyển, nghĩa là đã đụng damage path mà chưa duyệt |
| C5 | Subsystem XP/level cho companion | `xp_source` (daily-activity, "cap 1 level/day to L20, 2/day after"), `feed_cooldown_hours` (12h) | Server này **không có daily reset**; cooldown hàng giờ cần đồng hồ thật + persistence, không phải ledger in-memory | Cùng nhóm gap đã ghi cho currency daily caps và pet feed cooldown; migration = khi có subsystem reset thì thêm test "reset不发生 hai lần trong một ngày" chứ không sửa check cũ cho pass |
| C6 | Quyền cho leash | `owner_range_wu` (8) + `leash_behavior` ("teleport to owner after 5s out of range") | Chưa nguồn nào nói companion là world entity, audience member, hay art client-only → không thể quyết định chỗ nó xuất hiện | Nếu companion vào audience thì phải qua cùng đường với AOI (enter 40 / leave 48, `ProjectedEntityV2`) và sẽ cần check vị trí per-owner giống `alpha.escort_audience_position_is_per_owner`; đó là chỗ dựa sẵn có, không phải code mới cần nghĩ từ đầu |

---

## D. Ràng buộc áp dụng cho mọi lựa chọn ở trên

1. Không gate nào bật trong `appsettings.json`; không topology bundle nào bị đánh dấu
   `REVIEWED`; tôi không sửa `docs/production/**`.
2. Không số cân bằng nào được tự đặt. Nếu chủ dự án chọn A1/B3/C-số-học, tôi xin **số**
   của decision, không suy ra từ "có vẻ hợp lý".
3. Thứ tự bắt buộc với mọi thay đổi wire: decision → schema + example + negative fixture
   + validator rule (có mutation chứng minh) → rồi mới tới handler. Tôi đã làm đúng thứ tự
   này cho TALK và portal và đã caught ba defect của chính mình nhờ nó.
4. "Migration" ở đây nghĩa là: check nào đổi, check nào **phải fail có chủ đích** khi đổi,
   và oracle nào cấm đụng (`19`, `8/10/17`, DEC-022 `27/8/21/5`, counter `32/49`,
   `mob_damage=30`, `counter_damage=34`). Nếu một migration làm chúng dịch chuyển, migration
   đó sai.
