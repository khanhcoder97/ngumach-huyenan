# QOD-24 — Đối chiếu Bách Khoa Lạc Châu / Compendium overlay (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `Compendium_Encyclopedia_Overlay_Spec_vi.md`
(251 dòng) dưới góc độ server; đối chiếu counter snapshot §2 với các CSV production đã ship.
Báo cáo-only: không mở route/gate/wire, không sửa nguồn, không dựng index.

## 1. Trạng thái runtime đo được

- Không có compendium/encyclopedia service hay index nào. Vocabulary §11–§12
  (`compendium`/`Compendium`/`catalogManifestVersion`/`discoveryRule`/`spoilerLevel`/
  `EntryRemoved`/`DiscoveryDenied`/`CursorExpired`) grep = **0 file** trong Server/Health.
- Compendium là lớp tra cứu/điều hướng đọc từ content registry + player discovery overlay
  (§1, §11). Server hiện có các catalog rời (item, quest, NPC, skill, pet/mount, life-sim)
  nhưng chưa có manifest chung `entryId/canonicalId/category/discoveryState` nào, chưa có
  paging cursor / local search index / discovery delta, chưa lọc spoiler phía server (§11
  "Server lọc dữ liệu spoiler trước khi trả về"). Đây là read-model + wire contract chưa duyệt.

## 2. Counter snapshot §2 — đối chiếu từng danh mục với CSV (đo bằng script)

Spec §2 dự kiến **2.532 record duy nhất**. Đo từng danh mục từ nguồn đã ship:

| Danh mục | Spec §2 | Đo từ CSV/bundle | Kết quả |
| --- | ---: | --- | --- |
| Vật phẩm & nguyên liệu | 2.235 | Rarity variant CSV = **2.235** row (= 2.100 gear variant + 135 item cố định) | khớp |
| — Vũ khí (filter con) | 175 | variant category "Trang bị / vũ khí" = **175** (5 lớp × 7 tier × 5 phẩm) | khớp |
| — Pháp bảo & trang bị (filter con) | 1.925 | variant giáp 875 + phụ kiện 1.050 = **1.925** | khớp |
| Nhiệm vụ & công việc | 76 | Quest_Dialogue CSV distinct quest_id = **76** | khớp |
| NPC & dịch vụ | 83 | NPC_Actor registry = **83**; npc_anchors.json 104 placement / **83** distinct npcId | khớp |
| Thú đồng hành, thú cưỡi & cá | 16 | Pet_Mount CSV 10 (5 PET + 5 MOUNT) + Life_Sim 6 FISH = **16** | khớp |
| Bí tịch & kỹ năng | 70 | passive CSV **40** + active spec **30** = 70 (nhưng active mới ship 7 — xem §3.1) | khớp dự kiến / thiếu data |
| Trùm | 12 | 6 world + 4 dungeon + 2 raid canonical (manifest có 14 entity_id gồm add/altar — xem §3.2) | khớp canonical |
| Quái vật & linh thú | 21 | base monster/boss-add template (chưa đối chiếu đủ — xem §3.3) | chưa chốt |
| Bản đồ & bí cảnh | 19 | 9 world + siege + 4 DG + 2 RD + Tháp + 2 activity (manifest 46 map_id gồm 30 tầng tháp con) | khớp khi gộp tầng |

**Item 2.235 phân rã đúng:** master CSV 556 row, variant CSV 2.235 row; 135 item_id master
trùng variant (toàn bộ item cố định: Tiêu hao 14, Nguyên liệu 32, Ngọc 25, Quest item 20,
Mỹ phẩm 18, Công thức 10, Vé 2, Pet 6, Mount 5, Công cụ nghề 3 = 135). 2.100 gear variant
(35 vũ khí master × 5 + 385 template không phải vũ khí × 5) + 135 cố định = 2.235. Khớp
cách spec đếm "2.100 biến thể + 135 cố định", không cộng chồng master gear (420 row master
gear là template, không phải record độc lập trong counter). Vũ khí/pháp bảo là filter con,
không thêm vào Tổng — khớp §2 dòng 35.

## 3. Khoảng trống / sắc thái đo được

### 3.1 Active skill: spec 30, mới ship 7

Counter "Bí tịch & kỹ năng 70 = 30 active + 40 passive". Passive CSV đủ **40** row. Nhưng
active skill mới chỉ có **7** file JSON ship (`Implementation/Content/Examples/SkillDefinition/`:
SK-MK-01/02/03, SK-HB-02/04, SK-TC-01/05) — 23/30 chưa có vì `telegraphSeconds` bắt buộc
không null mà nguồn chỉ cho dải theo nhóm (đã pin ở skill coverage report 2026-11-05, task
#106). Compendium counter 70 là **dự kiến thiết kế**, không phải số record có thể load hôm
nay; nếu index dựng từ file ship thì category skill chỉ có 47 (7 active + 40 passive).

### 3.2 Boss: 12 canonical vs 14 entity_id manifest

Spec §2 "Trùm 12 = 6 world + 4 dungeon + 2 raid; bản quest/world dùng chung một hồ sơ
canonical". Manifest có 14 entity_id chứa BOSS: 12 canonical (BOSS_MANG_COT, FLAME_SENTINEL,
ANCIENT_TREE, FURNACE, TONG_BANH, TIDE_SERPENT = 6 world; YOUNG_TREE, ASH_FURNACE,
SIEGE_ENGINE, YOUNG_SERPENT = 4 dungeon; PRESSURE_HEART, COSM = 2 raid) **cộng** MOB_BOSS_ADD
và OBJ_TOWER_BOSS_ALTAR (không phải boss độc lập). Counter 12 khớp canonical; index phải gộp
quest/world variant và loại add/altar, nếu không sẽ đếm 14.

### 3.3 Bestiary 21 và map 19 chưa có nguồn đếm cấu trúc

"Quái vật & linh thú 21 base monster/boss-add template" và "Bản đồ & bí cảnh 19" không có
CSV riêng liệt kê đúng 21 template hay 19 record cha. Manifest có 46 map_id (gồm 30 tầng
tháp MAP_LAC_AN_TOWER_Fnn phải gộp dưới 1 record cha Tháp Lạc Ấn theo §2 dòng 33). Counter
đúng khi gộp, nhưng chưa có bảng mapping `map_id → compendium entry` để enforce; không suy
ra số record từ số map_id thô.

### 3.4 Discovery/spoiler overlay chưa có field

§3 bốn state `unknown/rumor/discovered/recorded`, §11 `discoveryRule/spoilerLevel/
discoveryState/recordedAt`, §12 error `ManifestUnavailable/EntryRemoved/DiscoveryDenied/
CursorExpired/StalePlayerState` — không field/wire nào trong Server. Account state (sở hữu,
quest progress, seen) là overlay riêng theo nhân vật (§11 dòng 195); server phải lọc spoiler
trước khi trả, không gửi tất cả lore rồi dựa UI giấu. Cần packet read-model + discovery
ledger riêng.

## 4. Câu hỏi owner

1. Compendium index dựng từ catalog rời hiện có hay cần manifest chung `entryId/canonicalId/
   category` mới (§11)? Ai duyệt schema manifest + paging cursor + discovery delta?
2. Counter skill 70 (30 active) giữ là dự kiến thiết kế hay index chỉ đếm record đã ship
   (47 hiện nay)? 23 active thiếu telegraph có chặn compendium category không?
3. Boss index gộp quest/world canonical + loại MOB_BOSS_ADD/OBJ_TOWER_BOSS_ALTAR theo quy tắc
   nào — có bảng mapping hay suy từ record_type? Bestiary 21 / map 19 lấy nguồn đếm nào?
4. Discovery/spoiler overlay (4 state, server-side filter, error codes §12) vào packet
   read-model riêng hay chung lane persistence? Hiện chưa field/wire.

## 5. Kiểm chứng lượt này

```bash
# Item: master 556 / variant 2235; overlap 135 (item cố định); gear variant 2100 = 175 weapon + 1925 non-weapon
# NPC registry 83 == 83 distinct npcId trong 104 anchor placement
# Quest distinct quest_id 76; pet/mount 10 + fish 6 = 16; passive 40
# Active skill ship 7/30 (SkillDefinition/*.json); boss canonical 12 (manifest 14 entity_id gồm add/altar)
# Server compendium/catalogManifestVersion/discoveryRule/spoilerLevel grep = 0
```

Báo cáo-only, không đổi code/runtime/bundle; kết quả công bố trên #87/#41/PR106. Không mở
route/gate/wire, không sửa `docs/production/**`, không merge.