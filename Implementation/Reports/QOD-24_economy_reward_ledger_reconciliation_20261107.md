# QOD-24 — Đối chiếu kinh tế: reward ledger, chợ, giao dịch, thư (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc lần đầu dưới góc độ server `Activities_Economy_PvP_Production_Spec_vi.md` §7
cùng các row `REWARD`/`CURRENCY_REWARD` của `Loot_Recipe_Reward_Production_Data_vi.csv`; đối chiếu
`Currency_Production_Data_vi.csv`, `Thang_Long_Thanh_Capital_Map_Spec_vi.md` §6.3,
`Battleground_10v10_Production_Spec_vi.md` và `Character_Equipment_Inventory_Spec_vi.md`.
Không mở route/gate/wire, không sửa `docs/production/**`.

## 1. Trạng thái runtime đo được

- Loot CSV có 221 row: 184 `LOOT_ENTRY` + 7 `RECIPE` + **3 `REWARD` + 27 `CURRENCY_REWARD`**.
  Sau delta forge (96016f1) builder đặt tên 7 RECIPE; **30 row reward vẫn bị bỏ silently** —
  grep toàn repo: không file `Server/` hay `Implementation/Tools/` nào đọc `CURRENCY_REWARD`,
  `cap_scope`, `BG10_PARTICIPATION` hay `TOWER_WEEKLY_SCORE` (chỉ CSV, một proposal cũ và một
  audit JSON cũ khớp chuỗi).
- 27 row CURRENCY_REWARD phủ 15/16 currency của registry; currency duy nhất không có row reward
  là `COIN` — đúng blocker đã pin `COIN_BAND_MISSING`.
- Không có reward-ledger service, không có market/trade/mailbox service, không route nào.
  `Server/Health/README.md:428`: 19 NPC mang 14 service token (gồm `SERVICE_MARKET`,
  `SERVICE_SHOP`, `SERVICE_BANK`) nhưng "none of them has a route".
- Delta lượt này data-only: builder đặt tên cả 30 row trong `unsupported.activityRewards` (3)
  và `unsupported.currencyRewards` (27), count/ids suy từ CSV; guard mới refuse khi trùng
  `entry_id`, thiếu `item_or_currency_id` hoặc thiếu `cap_scope` (ba ca mutation trên bản CSV
  tạm đều exit 1, không ghi output). Loader không đọc `unsupported` nên runtime không đổi;
  self-check vẫn 615/0/615.

## 2. Mâu thuẫn đo được giữa các nguồn (chưa nguồn nào được quyền ghi đè nguồn nào)

### TOWER_MERIT — cap ngày vs cap tuần

- `Currency_Production_Data_vi.csv` dòng 15: `daily_cap=60`, `storage_scope=account`.
  `CurrencyCatalogLoader.ReadDailyCap` parse thành `Amount=60` **theo ngày**.
- Cả 4 row reward (`TOWER_WEEKLY_PARTICIPATION/SCORE_BRONZE/SILVER/GOLD`) ghi
  `cap_scope=60/account/week`; notes của chính registry dòng 15 ghi "60/week";
  Activities §7 ghi "trần 60/tuần/tài khoản".
- Nếu enforce cột `daily_cap` như tên cột, một account được 60/ngày = 420/tuần, gấp 7 lần
  trần mà ba nguồn còn lại cùng ghi. Đây là mâu thuẫn cấp cột, không phải diễn giải.

### LONG_MON_PLACEMENT — phẳng 5 vs phân bậc theo hạng

- Loot CSV `LONG_MON_PLACEMENT_CURRENCY_LONG_MON_MEDAL`: `quantity_min=5, quantity_max=5`,
  cap `30/account/week placement`, condition "best placement per account per scheduled round".
- `Thang_Long_Thanh_Capital_Map_Spec_vi.md:117–121`: hạng 9–16 +5, hạng 4–8 +10, hạng 3 +20,
  á quân +25, vô địch +30 (chỉ nhận khoản cao nhất).
- Theo CSV phẳng, vô địch tuần nhận 5 thay vì 30; cap tuần 30 thì khớp nhưng lượng mỗi sự
  kiện lệch cho mọi hạng trên 9–16. Hàng `LONG_MON_MATCH_COMPLETE` (5/trận, 30/tuần) khớp
  cả map spec dòng 116 lẫn Activities §7.

### Khoảng trống cấu trúc của registry (không phải mâu thuẫn số)

- Registry không có cột `weekly_cap`: cap tuần của DG (10), RD (2), TOWER (60), LONG_MON
  (30+30) chỉ tồn tại trong prose `notes` và `cap_scope` của loot CSV. `weekly_reset` có cột
  riêng nhưng không chở lượng cap.
- `LONG_MON_MEDAL`: registry `daily_cap="per scheduled match"` (loader giữ Unscheduled),
  `weekly_reset="event season config"` — không nêu mốc reset tuần cho cap 30+30; row reward
  và map spec nói cap theo tuần nhưng không ai định nghĩa giờ reset của ledger này.
- Registry không có cột daily-reset: 5 row REP có `daily_cap=200` với `weekly_reset="none"`;
  giờ reset hàng ngày không nằm trong CSV (spec chỉ chốt reset tuần thứ Hai 05:00).

## 3. Các cặp đối chiếu KHỚP (đo bằng script, không ước lượng)

| Nguồn | Đối chiếu | Kết quả |
| --- | --- | --- |
| REP ×5 vùng | quest +5 / boss +10, `200/account/day` | khớp registry `daily_cap=200, scope=account` và Activities §7 |
| DG01–04 | 1/clear, `10/character/week` | khớp notes registry + Activities §2/§7 |
| RD01/02 | 1/clear, `2/character/week` | khớp notes registry + Activities §3/§7 |
| TSS_MERIT | 10 tham gia + 10 thắng + 5 objective, `60/account/day` | khớp registry `daily_cap=60` + Activities §7; Battleground spec dòng 60 "thưởng thắng ×20" là tổng 10+10, không phải mâu thuẫn |
| GUILD_CONTRIBUTION | 50/quest; donation 1000 COIN:1; `5000/character/day` | khớp registry + Activities §7 |
| Chợ | phí niêm yết 2%, phí giao dịch 5%, 10 listing/nhân vật, 30/tài khoản | Thang_Long map spec dòng 76 lặp lại đúng số "như Economy spec"; inventory spec §87/150 nhất quán (tradeable, durability>0, không protected, atomic purchase) |
| Thư | TTL 30 ngày, chỉ tiền chợ/hoàn giao dịch/quest overflow | Activities §7 + inventory spec dòng 101/151 + map spec `NPC_TL_BANKER` nhất quán; không dùng mailbox tạo item |

Ba row REWARD (TOWER_WEEKLY_CLEAR `MAT-CORE-01` 1/character/week; RAID_RD01_CLEAR
`MAT-CORE-01` 2 clears/week; RAID_RD02_CLEAR `MAT-RELIC-01` 2 clears/week) không có nguồn
đối chiếu số lượng nào khác trong spec — Activities §3 chỉ nói "MAT-CORE-01 tuần đầu tiên"
cho RD-01 (không rõ là giới hạn tuần đầu hay bảo đảm sàn), ghi nhận để owner xác nhận.

## 4. Phần spec chưa có bất kỳ runtime nào

Chợ (listing/settlement/fee), giao dịch trực tiếp (offer→review→confirm→commit, đổi một bên
hủy confirm), mailbox (TTL 30 ngày, chỉ ba loại nội dung), shop NPC, kho cá nhân/account —
không service, không route, không schema wire. Số phí 2%/5% và cap 10/30 chỉ nằm trong prose
spec, không có CSV data. Đây là các hệ thuộc lane persistence/ledger (Remote #79) và cần
packet duyệt riêng; báo cáo này không mở gì.

## 5. Câu hỏi owner (trả lời trước khi viết schema/handler)

1. `TOWER_MERIT`: `daily_cap=60` trong registry là cap tuần bị đặt nhầm cột, hay chủ ý
   60/ngày + 60/tuần? Nguồn nào thắng khi enforce?
2. `LONG_MON_PLACEMENT`: lượng theo hạng của map spec (5/10/20/25/30) hay phẳng 5 của CSV?
   Nếu theo hạng, CSV cần thêm cột/bậc — ai sửa nguồn?
3. Cap tuần (DG/RD/TOWER/LONG_MON) nên thành cột `weekly_cap` có cấu trúc trong registry,
   hay enforce từ `cap_scope` của loot CSV? Mốc reset cho ledger LONG_MON ("event season
   config") và mốc reset hàng ngày cho REP là giờ nào?
4. Có duyệt packet reward-ledger (đọc 30 row này, enforce cap theo scope, idempotent theo
   requestId) và packet chợ/giao dịch/thư không? Wire/schema mới qua cổng duyệt riêng?

## 6. Kiểm chứng lượt này

```bash
python Implementation/Tools/build_loot_recipe.py   # 57 sources/184 entries; 7 RECIPE + 3 REWARD + 27 CURRENCY_REWARD named
python Implementation/Tools/build_loot_recipe.py   # lặp lại: sha256 identical, git diff --exit-code sạch
dotnet Server/Health/bin/Release/net10.0/Health.dll --self-check   # 615/0/615
python Implementation/Tools/validate_contracts.py  # all passed
```

Ba ca refusal (mutation trên CSV tạm, không đụng nguồn production): trùng entry_id
CURRENCY_REWARD → exit 1; REWARD thiếu cap_scope → exit 1; CURRENCY_REWARD thiếu
item_or_currency_id → exit 1; cả ba không ghi output. Bundle tái sinh byte-stable
sha256 `1790ef911a43d538c81aac21fef75c820aa8a85ce0ad27ab5bdac541fa7f584d` hai lần liên tiếp.
Kết quả và CI đúng commit được công bố trên #87/#41/PR106. Delta chỉ gồm builder + bundle
tái sinh + báo cáo này; không đổi hành vi loader, không đổi gate, không merge.

## 7. Phụ lục — đọc trọn Activities_Economy_PvP_Production_Spec_vi.md (207 dòng)

Sau khi công bố §1–6 ở commit `c744464`, đọc trọn spec master lần đầu dưới góc độ server
(không tool/server nào tham chiếu file này — grep `Activities_Economy_PvP` trong
`Implementation/Tools` + `Server` = 0). Ba mục bổ sung/cải chính, giữ nguyên claim cũ:

### 7.1 Cải chính §2: mốc reset hàng NGÀY có trong spec, chỉ thiếu trong CSV

§2 dòng 57–58 viết "spec chỉ chốt reset tuần thứ Hai 05:00" — **chưa đủ**. Mục §9 của
spec master (dòng 188) chốt rõ hàng ngày: "3 nhiệm vụ vùng, 3 lượt mini game, 2 cache
dungeon; 3 reward cache BG10 | **05:00 Asia/Ho_Chi_Minh**". Vậy mốc reset ngày cho REP
(`daily_cap=200`) tồn tại trong prose §9; khoảng trống đúng là **CSV không có cột
daily-reset có cấu trúc**, không phải spec thiếu mốc. Cải chính này không đổi kết luận: cap ngày
REP vẫn chưa enforce được vì loader không có mốc reset ngày để neo.

### 7.2 Mâu thuẫn ủy quyền ngay trong chuỗi canonical (dòng 160)

Dòng 160 spec master: "Registry chuẩn, ownership, **cap/reset** và faucet/sink nằm trong
`Currency_Production_Data_vi.csv`". Nhưng chính cột `daily_cap=60` của registry cho
TOWER_MERIT mâu thuẫn với prose §7 dòng 156 của spec master ("trần **60/tuần**/tài khoản").
Nghĩa là nguồn được spec ủy quyền làm canonical (registry CSV) lại disagree với spec ủy
quyền. Đây là gốc của mâu thuẫn TOWER_MERIT §2: không thể chọn nguồn thắng bằng cách đọc
thêm — owner phải quyết định cột `daily_cap` là cap tuần đặt nhầm cột, hay prose §7 sai.
Bốn nguồn cùng ghi "tuần" (master §7 dòng 156, notes registry, 4 row reward `cap_scope`,
Tower spec) chỉ chống lại một cột `daily_cap`; cán cân nghiêng về tuần nhưng quyền ghi đè
nguồn vẫn là quyết định owner, server không tự sửa.

### 7.3 Lệnh Truy Mạch / Thí Luyện Hồi Ức (§4 dòng 95–103): data có, service không

Subsystem vé đánh lại boss tính điểm. Đo bằng grep trên data ship:
- `TICKET-BOSS-01` **có** trong `Item_Master_Catalog_vi.csv` + `Item_Rarity_Variant_Catalog_vi.csv`
  (item data tồn tại: account-bound, không giao dịch, stack 3).
- `NPC_RAID_KEEPER` **có** trong `NPC_Actor_Production_Registry_vi.csv`, manifest, và đã
  load vào `Implementation/Content/Runtime/npc_anchors.json` + `world_records.json`.
- `TICKET-BOSS-01` trong `Server/` = **0 file**: không runtime nào tiêu vé, tạo arena ký
  ức 20 phút, scale HP/damage nhóm 1–5, hay reuse quota cache. Cap 3 vé/account/tuần,
  reset thứ Hai 05:00, điều kiện cấp 81+ / đã mở `MAP_VUC_NGHICH_MACH` / đã gặp boss —
  không ledger nào enforce. Cùng pattern guild: data/anchor có, service vắng.
- `TICKET-TIDE-01` là **item vé**, không phải currency ví (dòng 158) — đúng khi không có
  row trong currency registry; không phải khoảng trống.

Bốn boss dungeon/raid có canonical ID riêng (§2 dòng 57, §3 dòng 69): `BOSS_YOUNG_TREE`,
`BOSS_ASH_FURNACE`, `BOSS_SIEGE_ENGINE`, `BOSS_YOUNG_SERPENT`, `BOSS_PRESSURE_HEART` —
không dùng chung ID với boss thế giới cùng họ hình ảnh. Đây là encounter lane (QOD-19/20),
không thuộc economy delta; ghi nhận để không nhầm khi đối chiếu manifest sau này.

Không mở route/gate/wire; phụ lục chỉ đọc nguồn và đo grep, không sửa `docs/production/**`.