# QOD-24 — Đối chiếu HUD gameplay / data model (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `Gameplay_HUD_Overlay_Spec_vi.md` (209 dòng)
dưới góc độ server; đối chiếu data model §10 với `PlayerSession`/snapshot hiện có. Phần lớn
spec là client UI (bố cục neo, token, pixel art, responsive, accessibility); báo cáo chỉ pin
những field server phải cung cấp. Báo cáo-only: không mở route/gate/wire, không sửa nguồn.

## 1. Trạng thái runtime đo được

- HUD §10 "subscribe một snapshot đã xác thực cùng delta sự kiện; animation nội suy, không
  giữ logic game". Server có `WorldSnapshotFactory` + AOI projection + event store v2, nhưng
  **không có HUD vitals DTO/endpoint** riêng (`vitals`/`classResource`/`hudSnapshot`/
  `PlayerVitals` grep = 0 file).
- Vocabulary §10 đo trong Server/Health: `classResource`=0, `realmLabel`=0, `expiresAt`=0,
  `tinhNgoc`=0, `serverTime`=0, `hpMax`=0, `mpMax`=0, `toNext`=0; `shield`=1 (không phải HUD
  shield DTO), `cooldownEndsAt`=2 (combat status), `worldTarget`=1 (quest).

## 2. Data model §10 — đối chiếu từng field với PlayerSession

`PlayerSession.cs` hiện có: SessionId/CharacterId/ClassId/FloorId/Level/MapId/X/Y/Hp/MaxHp/
Mp/MaxMp/**SwordIntent**/Revision/TotalXp/UnspentPoints/LastInputSequence/LastMoveAtUtc.

| Field HUD §10 | Nguồn server hiện có | Kết quả |
| --- | --- | --- |
| player.classId/level | PlayerSession.ClassId/Level | có |
| vitals.hp/hpMax/mp/mpMax | PlayerSession.Hp/MaxHp/Mp/MaxMp | có (tên wire khác: MaxHp≠hpMax) |
| world.mapId/x/y | PlayerSession.MapId/X/Y | có |
| vitals.classResource {name,value,max} | chỉ **SwordIntent** (Kiếm Ý, Minh Kiếm) | thiếu tổng quát 5 lớp |
| vitals.shield {value,max,expiresAt} | không field shield/Hộ Thể trong PlayerSession | thiếu |
| player.realmLabel | không field realm/cảnh giới | thiếu (optional, null được) |
| wallet.tinhNgoc (Ngọc Tịnh) | không wallet/premium currency trong session | thiếu |
| vitals.exp {value,toNext} | TotalXp có, **toNext** không (chưa công thức level curve) | thiếu một phần |
| world.serverTime/channel | IServerClock có, chưa đưa vào HUD snapshot | thiếu field snapshot |
| skills[].cooldownEndsAt/mpCost/state | CombatStatus có cooldown + SwordIntent | có một phần (combat read model) |
| quests[].objectives worldTargetId | quest progress có worldTarget | có |

### 2.1 classResource: chỉ Minh Kiếm, chưa tổng quát 5 lớp

HUD §4 dòng 67: tài nguyên lớp 5 nấc, tên theo môn phái **Kiếm Ý / Nhiệt / Thủy Ấn / Thế /
Mộc Tiêu**. Server chỉ có `SwordIntent` (Kiếm Ý) với cap 5 (`GuardPrecision.cs:174-175`:
SwordIntentGain=2, SwordIntentCap=5) — đúng cho CLASS_MINH_KIEM nhưng **chưa có field tổng
quát** cho Nhiệt (Hỏa), Thủy Ấn (Huyền Bút), Thế (Thạch Chùy), Mộc Tiêu (lớp còn lại).
`classResource.name` phải lấy từ class config (§10 dòng 166), không hardcode; hiện chưa
class config nào trả tên/value/max cho 4 lớp kia. Đây là gap combat resource chưa duyệt.

### 2.2 shield / Hộ Thể (§4 dòng 68)

HUD: thanh Hộ Thể chỉ hiện khi có khiên hoạt động, số `còn/lúc nhận` + thời gian còn lại;
không có shield thì ẩn, **không giả lập giáp cơ bản thành tài nguyên tiêu hao**. PlayerSession
không field shield/value/expiresAt. Shield runtime (khiên tạm từ skill/buff) chưa có service;
`shield` grep=1 không phải HUD DTO. Cần shield state + expiresAt trong snapshot khi duyệt.

### 2.3 realmLabel / wallet / exp-toNext / serverTime

- `realmLabel` optional (§10 dòng 166: null thì chỉ hiện cấp; HUD **không tự suy diễn cảnh
  giới từ cấp**). Server chưa progression service trả realm_label — để null đúng spec, không bịa.
- `wallet.tinhNgoc` (Ngọc Tịnh, premium currency §4 dòng 64): chưa wallet service trong
  session; currency registry có Đồng/REP/token nhưng Ngọc Tịnh premium chưa row/service.
- `exp.toNext`: TotalXp có nhưng chưa level curve để tính EXP cần lên cấp; không suy ra số.
- `world.serverTime`/`channel`: IServerClock tồn tại nhưng chưa field trong HUD snapshot;
  channel/shard chưa có service.

## 3. Điểm khớp / ràng buộc pin lại

- **Cooldown server-authoritative** (§8 dòng 128): "Cooldown là kết quả từ server; sweep vẽ
  theo thời gian còn lại đã đồng bộ, không xác nhận skill kích hoạt trước ACK. Damage/cost/
  target/resource do server authoritative." Khớp combat read model hiện có (CombatStatus
  cooldown + SwordIntent); HUD không tự roll.
- **LowFX giữ telegraph** (§8/§12): VFX skill không biến mất trong LowFX, chỉ giảm hạt phụ;
  khớp rule weather/LowFX đã reconcile.
- **Camera hub DEC-021** (dòng 209): hub 48×27 WU, canvas UI độc lập world render 960×540,
  giữ 6 skill arc — khớp wide-camera/hub reconcile (#116); client-only.
- **Mất kết nối chặn cast/giao dịch** (§9 dòng 146): khớp server-authoritative + idempotent
  requestId hiện có; không tự xóa thao tác pending.

## 4. Câu hỏi owner

1. HUD vitals snapshot dựng từ WorldSnapshot hiện có hay cần DTO/endpoint riêng (§10)? Ai
   duyệt wire `vitals/classResource/shield/wallet/serverTime`?
2. `classResource` tổng quát 5 lớp (Kiếm Ý/Nhiệt/Thủy Ấn/Thế/Mộc Tiêu) — class config nào trả
   name/value/max? Hiện chỉ SwordIntent (Minh Kiếm) có runtime.
3. Shield/Hộ Thể state + expiresAt, realmLabel (progression), wallet Ngọc Tịnh (premium),
   exp.toNext (level curve) — packet nào mở? Hiện chưa field/service; không bịa số.
4. `serverTime`/`channel` đưa vào HUD snapshot từ IServerClock/shard service nào?

## 5. Kiểm chứng lượt này

```bash
# PlayerSession: Hp/MaxHp/Mp/MaxMp/Level/MapId/X/Y/SwordIntent/TotalXp present
# classResource/realmLabel/tinhNgoc/serverTime/hpMax/mpMax/toNext/expiresAt grep = 0 in Server
# SwordIntent cap 5 (GuardPrecision.cs:174-175) = Minh Kiem only; no generalized 5-class resource
# no HUD vitals DTO/endpoint (vitals/PlayerVitals/hudSnapshot grep = 0)
```

Báo cáo-only, không đổi code/runtime/bundle; kết quả công bố trên #87/#41/PR106. Không mở
route/gate/wire, không sửa `docs/production/**`, không merge.