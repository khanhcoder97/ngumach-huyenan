# QOD-24 — Đối chiếu Chiến Trường Trấn Sơn 10v10 (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `Battleground_10v10_Production_Spec_vi.md`
(70 dòng) dưới góc độ server; đối chiếu `World_Spawn_Gathering_Manifest_vi.csv` (10 row
BG10), bundle `Implementation/Content/Runtime/world_records.json`, `Currency_Production_Data_vi.csv`
và `Loot_Recipe_Reward_Production_Data_vi.csv`. Báo cáo-only: không mở route/gate/wire,
không sửa nguồn, không đổi tọa độ.

## 1. Trạng thái runtime đo được

- Không có BG10/battleground service nào. `grep -rl 'BG10|Battleground|TSS_MERIT' Server/Health
  --include=*.cs` = **0 file**. Các vocabulary `BG10_CAPTURE`/`BG10_RELIC`/`bg10.`/`CURRENCY_TSS_MERIT`/
  `capture_point`/`relic_pickup`/`match_id` đều grep = 0 trong Server.
- `SERVICE_PVP_QUEUE` là một trong 14 service token routeless (README:428) — token tồn tại
  trong data NPC, không route nào gắn. Queue/ready-room/capture/relic/score/anti-AFK/reconnect
  của spec §3–§4 chưa có state machine hay wire contract.
- 10 anchor BG10 **đã load** vào `world_records.json` (đo: `grep -c MAN-BG10` = 10; mỗi entity_id
  BG10_* xuất hiện đúng 1 lần) dưới dạng INTERACTABLE/ACTIVITY_PLACEMENT, zone_id=BG10.

## 2. Cặp đối chiếu KHỚP (đo bằng script)

10/10 anchor spec §2 khớp **cả** manifest lẫn bundle, từng tọa độ:

| ID | Spec §2 (X,Y) | Manifest / bundle | Kết quả |
| --- | --- | --- | --- |
| BG10_SPAWN_BLUE | 28,0 | 28,0 | khớp |
| BG10_SPAWN_RED | 332,0 | 332,0 | khớp |
| BG10_POINT_W | 92,0 | 92,0 | khớp |
| BG10_POINT_M | 180,0 | 180,0 | khớp |
| BG10_POINT_E | 268,0 | 268,0 | khớp |
| BG10_RELIC_NEUTRAL | 180,7 | 180,7 | khớp |
| BG10_RELIC_HOME_BLUE | 40,0 | 40,0 | khớp |
| BG10_RELIC_HOME_RED | 320,0 | 320,0 | khớp |
| BG10_JUMP_W | 132,0 | 132,0 | khớp |
| BG10_JUMP_E | 228,0 | 228,0 | khớp |

Composition/radius cũng khớp: spawn "10 player anchors spread ±5 WU" quantity=10; POINT_W/E
"capture radius 8 WU; capture 8s", POINT_M "radius 9 WU; neutral capture 10s"; RELIC altar
"pickup 1.2s; respawn 90s then 150s cycle"; home socket "channel 2s"; flank "one-way 6s route;
disabled while carrying relic". Tất cả row BG10 ghi condition "10v10 queue instance only; not
loaded by 20v20 siege; 12-minute match" và notes "Shares MAP_TRAN_SON_SIEGE geometry only;
isolated BG10 zone, score, roster and reward" — khớp cách ly hai chiều spec §1 (không dùng
siege objective/ledger công thành). Đây là 10 INTERACTABLE đã nêu trong guild report §3; phần
còn thiếu của MAP_TRAN_SON_SIEGE là objective anchor 20v20 (spec §7 Guild), không phải BG10.

**Reward TSS_MERIT — phân rã khớp ba nguồn:** spec §5 dòng 60 "thắng ×20; tham gia ×10;
objective ≥100: +5; cap 60/ngày/account". Activities §7 dòng 155 "10 tham gia +10 thắng +5
objective, trần 60/ngày". Loot CSV ba row `RT_BG10_PARTICIPATION` (10), `RT_BG10_WIN_BONUS`
(10, notes "additive win merit; total 20 before objective bonus"), `RT_BG10_OBJECTIVE_BONUS`
(5, "objective score >=100; once per match"), cả ba `cap_scope=60/account/day`. Currency
registry `CURRENCY_TSS_MERIT` `daily_cap=60, storage_scope=account`. Cách hiểu "thắng ×20" =
10 participation + 10 win bonus (không phải 20 riêng) nhất quán cả bốn nguồn — **không mâu
thuẫn**, xác nhận lại ghi chú economy report §3.

## 3. Khoảng trống / sắc thái đo được

### 3.1 Level vào 36 vs band manifest 30–100

Spec §1: "Cấp vào 36+, mở sau C3-01". Manifest BG10 ghi `character_level_min=30,
character_level_max=100` cho mọi row. 30 là sàn band của map (Activities §6 normalized level
40), không phải điều kiện queue 36+/C3-01. Điều kiện mở (level 36, quest C3-01, penalty account,
party max 5, latency region) chỉ nằm prose §3.1 — không cột CSV nào chở `unlock_quest` hay
`min_level_queue=36`. Không suy từ band map.

### 3.2 Reset daily vs weekly trong cùng row currency

BG10 spec §5 dòng 62: "Daily reward ledger reset 05:00 Asia/Ho_Chi_Minh; season/ranked reset
theo config". Currency registry `CURRENCY_TSS_MERIT` có `daily_cap=60` nhưng cột `weekly_reset`
= "Monday 05:00 Asia/Ho_Chi_Minh **season board**" — tức reset tuần của season board, không
phải mốc reset của daily cap 60. Mốc reset hàng ngày 05:00 cho ledger merit nằm ở spec prose,
không cột cấu trúc (cùng dạng gap daily-reset đã pin ở economy addendum §7.1). Không mâu thuẫn
số, nhưng nguồn enforce daily reset phải chỉ định rõ.

### 3.3 Match/state machine chưa có trường data

Spec §3–§4: 12 phút + overtime ≤90s; capture 1/3/5 điểm/giây theo số điểm giữ; relic +100 điểm
+ boost ×2 10s; respawn 8s (+≤4s chuỗi chết); reconnect giữ slot 120s; anti-AFK tín hiệu 60s,
cảnh báo 90s, loại reward 120s, penalty queue 5/15/60 phút; void nếu crash <3 phút hoặc đội <5
người do lỗi hệ thống. Result payload `match_id/season_id/team_result/per-player score/
objective score/reconnect-AFK flags/rewards/ruleset hash` (§5 dòng 63). Không cột CSV/wire nào
chở các tham số này — cần packet activity-server riêng (lane persistence/ledger), không suy từ
manifest placement.

## 4. Câu hỏi owner

1. Điều kiện queue BG10 (level 36+, C3-01, party ≤5, penalty) vào cột CSV mới hay wire contract
   của packet activity queue? Band manifest 30–100 có phải chỉ là sàn map không?
2. Mốc reset **hàng ngày** 05:00 cho ledger `CURRENCY_TSS_MERIT` (cap 60/ngày) lấy nguồn nào
   enforce — spec §5 prose hay thêm cột daily-reset vào currency registry? (`weekly_reset`
   hiện là season board, không phải daily.)
3. Có duyệt packet BG10 activity-server (queue/ready-room/capture/relic/score/anti-AFK/reconnect/
   void, result payload §5) không? Hiện 10 anchor inert trong world_records, không service/route.
4. `SERVICE_PVP_QUEUE` routeless có phải cửa vào BG10 + arena 3v3 + Long Môn không, hay mỗi mode
   một serviceId riêng? (routing vocabulary chưa có — xem overlay report §3.)

## 5. Kiểm chứng lượt này

```bash
# 10/10 BG10 anchor: spec §2 coords == manifest == world_records.json (đo từng ID)
# grep -c MAN-BG10 world_records.json = 10; mỗi BG10_* entity_id đúng 1 lần
# Server BG10/Battleground/TSS_MERIT vocabulary grep = 0 (no service/route)
# TSS reward 10+10+5 cap 60/day: spec §5 == Activities §7 == 3 loot rows == currency daily_cap
```

Báo cáo-only, không đổi code/runtime/bundle; kết quả công bố trên #87/#41/PR106. Không mở
route/gate/wire, không sửa `docs/production/**`, không merge.