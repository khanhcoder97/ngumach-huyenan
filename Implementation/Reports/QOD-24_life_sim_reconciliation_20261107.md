# QOD-24 — Đối chiếu nông trại / câu cá / thu thập (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `Life_Sim_Production_Spec_vi.md` (54 dòng)
dưới góc độ server; đối chiếu `Life_Sim_Content_Data_vi.csv` (11 row: 5 CROP + 6 FISH),
`World_Spawn_Gathering_Manifest_vi.csv` (6 anchor FISHING), và `LifeSimCatalog.cs` (292 dòng).
Spec prose không tool/server nào tham chiếu (grep = 0); CSV thì `LifeSimCatalogLoader` đã
load. Báo cáo-only: không mở route/gate/wire, không sửa nguồn, không đổi tọa độ.

## 1. Trạng thái runtime đo được

- `LifeSimCatalog.cs` load 11 row làm **data inert** (comment dòng 12–15: "loads as data and
  enforces nothing"). `DailyCap` lưu per-entry (dòng 208), không enforce; farm/fishing là
  state machine + wire contract chưa ai duyệt. Gathering hiện tại chỉ là đường
  INTERACTABLE/GATHER_NODE claim, chưa có farm plot hay fishing minigame service.
- Loader đọc y signed (comment dòng 167–169: LIFE_FISH_CA_RE tại 158,-3) — không giả định
  một làn; quality_weights phải tổng 10000 bps (guard dòng 243).

## 2. Cặp đối chiếu KHỚP (đo bằng script)

| Hạng mục | Spec | CSV / manifest | Kết quả |
| --- | --- | --- | --- |
| Farm 5 luống | §1 (10,0),(26,0),(42,0),(58,0),(74,0), zone FARM_PRIVATE_POCKET | 5 CROP đúng tọa độ + zone + MAP_THANG_LONG | khớp |
| Farm quality | §1 Common 80 / Rare 18 / Epic 2 | COMMON:8000;RARE:1800;EPIC:200 (bps) | khớp |
| Farm growth | §1 1–6 giờ | process_seconds 3600/7200/10800/14400/21600 | khớp (1–6h) |
| Seed | §1 MAT-SEED-01 | input_item_id MAT-SEED-01 ×1 cả 5 CROP | khớp |
| Farm tool | §1 TOOL-SICKLE-01 | tool_id TOOL-SICKLE-01 | khớp |
| Fish quality | §2 Common 85 / Rare 14 / Epic 1 | COMMON:8500;RARE:1400;EPIC:100 | khớp |
| Fish level | §2 1/5/12/8/20/30 | level_required đúng 6 bãi | khớp |
| Fish tool | rod | TOOL-ROD-01 cả 6 FISH + manifest | khớp |
| Fish tọa độ | §2 6 bãi | 5/6 khớp manifest + CSV (xem §3.1 ngoại lệ) | 5/6 |

## 3. Khoảng trống / mâu thuẫn đo được

### 3.1 Bến Mưa fishing y: prose -1 vs data 0

Spec §2 dòng 22 ghi "Bến Mưa (132,**-1**)". Nhưng **cả hai** nguồn data đều y=0:
`MAN-BM-FISHING-LINH` manifest (132,0) và `LIFE_FISH_CA_LINH` CSV (132,0). Prose -1 là
outlier so với hai nguồn data đồng thuận — nhiều khả năng giá trị pre-top-down cũ (DEC-016).
Lâm Triều (158,-3) thì cả spec lẫn manifest + CSV đều khớp. Báo cáo pin chênh lệch, không
tự sửa tọa độ (lane topology đang chờ authority).

### 3.2 daily_cap: account-wide total vs per-row

Spec §3: "Daily cap dùng ledger **account-wide**"; farm "tổng tối đa **12** item output/ngày/
account", fish "quota **20** cá/ngày/account". Manifest FISHING notes ghi rõ "**Per-account**
daily quota 20". Nhưng CSV lặp `daily_cap=12` trên **mỗi** trong 5 CROP row và `daily_cap=20`
trên **mỗi** trong 6 FISH row. Loader lưu per-entry, không diễn giải scope. Nếu ledger tương
lai cộng cap theo row thì farm = 5×12 = 60/ngày, fish = 6×20 = 120/ngày — gấp 5×/6× trần
account-wide mà spec + manifest cùng ghi. Scope của `daily_cap` (tổng account hay mỗi row)
phải được owner chốt trước khi enforce; data hiện không tự phân giải.

### 3.3 Fishing flow: thiếu cột cấu trúc

Spec §2: cast 4s → tension sequence → client gửi **3 input có sequence number trong tổng
8s** → quality/yield; RTT tolerance **±180ms**; bait chỉ tiêu sau cast hợp lệ; đứt dây sau
3 input sai; cast_id/seed/nonce, replay bị từ chối, đổi map/hop shard hủy cast. CSV có
`interaction_seconds=4` (cast) và `process_seconds=30–90` (tổng thời gian), nhưng **không
cột** cho cửa sổ input 8s, số input 3, RTT ±180ms, hay nonce/chống replay. Đây là chi tiết
wire/state-machine chưa có trường data — cần packet riêng, không suy từ process_seconds.

### 3.4 Seed shop cap prose-only

Spec §1: seed giá đề xuất 10 Đồng, giới hạn shop **20/day/account**. CSV không có cột cap
mua seed (`daily_cap=12` là cap output thu hoạch, không phải cap mua seed). Giá 10 Đồng và
cap mua 20/ngày chỉ nằm trong prose.

## 4. Câu hỏi owner

1. `daily_cap` trong Life_Sim_Content_Data_vi.csv là trần **account-wide tổng** (12 farm /
   20 fish, lặp lại mỗi row) hay cap **mỗi row**? Spec §3 + manifest nói account-wide;
   enforce per-row sẽ over-grant 5×/6×. Nguồn nào thắng?
2. Bến Mưa fishing y: chốt (132,0) của manifest + CSV hay (132,-1) của prose §2? (không tự
   sửa; chờ topology authority)
3. Fishing flow (cửa sổ 8s / 3 input / RTT ±180ms / nonce chống replay) vào cột CSV mới hay
   vào wire contract của packet fishing minigame? Ai duyệt schema?
4. Có duyệt packet farm/fishing service (plot state machine, cast_id ledger, cap account-wide,
   inbox 24h khi inventory đầy) không? Hiện catalog inert, không service/route.

## 5. Kiểm chứng lượt này

```bash
# 11 row CSV (5 CROP + 6 FISH); farm coords/quality/growth/seed khớp spec; fish quality/level khớp
# 6 manifest FISHING anchor: Bến Mưa (132,0), Lâm Triều (158,-3) — đối chiếu spec §2
# LifeSimCatalog.cs: DailyCap per-entry, enforce nothing; quality total 10000 guard
```

Báo cáo-only, không đổi code/runtime/bundle; kết quả công bố trên #87/#41/PR106. Không mở
route/gate/wire, không sửa `docs/production/**`, không merge.