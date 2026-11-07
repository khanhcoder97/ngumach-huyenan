# QOD-24 — Đối chiếu guild/social và công thành (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `Guild_Social_Spec_vi.md` (133 dòng) dưới góc độ
server; đối chiếu `World_Spawn_Gathering_Manifest_vi.csv`, `NPC_Actor_Production_Registry_vi.csv`,
`Currency_Production_Data_vi.csv`, `Battleground_10v10_Production_Spec_vi.md` và output của
`reconcile_combat_social_sources.py`. Báo cáo-only: không có builder nào drop row guild (không
tồn tại CSV guild trong 12 CSV production), không sửa nguồn, không mở route/gate/wire.

## 1. Trạng thái runtime đo được

- Không guild service, không route. `SERVICE_GUILD` là token trên `NPC_GUILD_CLERK`
  (README:428 — 14 service token, "none of them has a route"). Runtime chỉ nhắc "guild"
  trong quest enum (`QuestDefinition.cs`) và self-check.
- `reconcile_combat_social_sources.py` đã pin và CI-gate các rule đọc được: creation
  (cấp 10+, 20.000 Đồng, 10 huy hiệu), donation (5.000 Đồng + 30 vật liệu bang/ngày),
  treasury (hai sổ cái), contribution (50/quest, 1000 COIN:1, cap 5000/ngày/character).
  Self-test tại head: **364 drift case bị chặn, nguồn hiện tại pass**.
- Tool đã tự ghi nhận divergence `guild.cap-units`: donation 5000 **COIN**/member/day ≠
  currency 5000 **contribution points**/character/day — hai đơn vị khác nhau, không được
  đánh đồng. Đây là pin đúng, không phải lỗi.

## 2. Các cặp đối chiếu KHỚP

- `NPC_GUILD_CLERK` có mặt ở cả hai map đúng tọa độ spec §1: Thanh Lạc (309,0)
  `MAN-TL-NPC_GUILD_CLERK` và Thăng Long (636,0) `MAN-TH-NPC_GUILD_CLERK`; manifest ghi
  "counter dùng chung guild ledger" — khớp chủ ý một ledger hai counter. Anchor Thăng Long
  gate theo C1-05, khớp map spec. Cả hai đã vào `npc_anchors.json`.
- BG10 tách khỏi siege 20v20: 10 row BG10 đều ghi "not loaded by 20v20 siege", Battleground
  spec §1 cấm dùng roster/siege objective/ledger của công thành — nhất quán hai chiều.

## 3. Khoảng trống đo được (grep/python trên data ship, không ước lượng)

### GQ-01..06 không có nguồn data

Spec §6 định nghĩa 6 quest bang tuần (GQ-01 Đoàn xe Mưa … GQ-06 Hướng dẫn tân binh) kèm
contribution/thưởng. grep `GQ-0` trên toàn bộ CSV/JSON của `docs/production`,
`Implementation/Content`, `Server`: **0 kết quả**. Pool quest bang chưa tồn tại dưới dạng
data — cùng loại blocker content như `NPC_CLASS_TRIAL` của tutorial.

### Siege 20v20 không có anchor objective

`MAP_TRAN_SON_SIEGE` có 16 row manifest: 6 `MOB_GROUP` siege (engine/guard, design_state
`NEW_PROPOSED`) + 10 `INTERACTABLE` BG10. **Không row nào** cho layout §7: spawn phe 18/342,
cổng 94/266, trạm supply 180 radius 8, hai ụ nỏ 132/228, cờ ấn (180,12). BG10 có đủ anchor
còn siege 20v20 chỉ có prose. Ngoài ra y=12/y=5/y=9 của §7 là ngữ nghĩa độ cao pre-top-down
(DEC-016); báo cáo không tự chuyển tọa độ — lane topology đang chờ authority.

### Quỹ bang: sổ cái thứ hai không có currency

Spec §5 tách "Đồng thường" và "Điểm Công Trình". Registry currency có 16 row, **không row
nào** chứa "Công Trình" (grep = 0). Tool reconcile để `currencyIdMapping=null` cho cả hai
sổ cái — đúng mực không đoán. "Điểm Công Trình" cũng là thưởng của GQ-03 nhưng chưa có
currency ID. Tương tự `badgeId=null`: spec ghi "Huy hiệu Thanh Lạc", registry display là
"Huy Hiệu Danh Vọng Thanh Lạc" (`CURRENCY_REP_THANH_LAC`) — gần khớp nhưng không phải chuỗi
identical, cần owner xác nhận mapping thay vì server tự suy.

### Sinks của registry thiếu guild

- `COIN` sinks = "shop;repair;forge;market tax" — thiếu ba sink đã có nguồn số: tạo bang
  20.000 (spec §2), donation ≤5.000/ngày (spec §4), đổi contribution 1000:1 (spec §7
  Activities + currency notes).
- `CURRENCY_REP_THANH_LAC` sinks = "regional recipe;basic material;cosmetic vendor" — thiếu
  sink tạo bang 10 huy hiệu (spec §2).
Đây là khoảng trống provenance trong prose sinks, không phải mâu thuẫn số; chưa sửa nguồn.

### Prose-only, chưa runtime/config

Cap thành viên 40→60 theo cấp bang, kho 40→80 ô, bảng role/permission (§3), audit log
30/180 ngày, chat rate 1/8s thế giới + 1/1.5s guild, mời party 10/10 phút, bạn bè/LFG (§8),
siege schedule/scoring (§7) — không CSV, không config, không service. Tất cả cần packet
duyệt riêng; báo cáo này không mở gì.

## 4. Câu hỏi owner

1. Ai tạo data cho pool GQ-01..06 (quest CSV riêng hay mở rộng Quest_Dialogue)? Contribution
   "tối đa 10 kill/người" (GQ-02) và các ngưỡng khác cần cột cấu trúc.
2. Siege 20v20: anchor objective vào manifest theo layout §7 sau khi topology authority
   chốt, hay §7 được viết lại top-down trước? (không tự chuyển y cũ)
3. "Điểm Công Trình" có currency ID mới hay là field riêng của guild ledger? "Huy hiệu
   Thanh Lạc" có đúng là `CURRENCY_REP_THANH_LAC` không?
4. Bổ sung sinks guild vào registry (COIN ×3, REP_THANH_LAC ×1) — owner sửa nguồn hay
   chấp nhận sai lệch provenance hiện tại?
5. Có duyệt packet guild service (ledger/kho/quyền) và packet chat/party/friends không?
   Wire/schema mới qua cổng duyệt riêng.

## 5. Kiểm chứng lượt này

```bash
python Implementation/Tools/reconcile_combat_social_sources.py --self-test  # 364 case, OK
python Implementation/Tools/reconcile_combat_social_sources.py            # guild pins + cap-units divergence
```

Số đo grep/python: GQ-0 = 0 kết quả trong data; MAP_TRAN_SON_SIEGE = 16 row (6 siege mob +
10 BG10, 0 siege objective anchor); "Công Trình" trong currency CSV = 0; NPC_GUILD_CLERK
khớp 2 map. Báo cáo-only, không đổi code/runtime; kết quả công bố trên #87/#41/PR106.