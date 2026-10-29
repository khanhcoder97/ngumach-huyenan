# QOD-12 — Đề xuất `CombatCastEvent` (lifecycle cho VFX adapter)

**Trạng thái:** ĐỀ XUẤT, chưa emit. Legacy `CombatEvent` (`combat.effect`) giữ nguyên cho client hiện tại; event mới chỉ phát khi có implementation lifecycle và client khai báo hỗ trợ `schemaVersion=1`.
**Issue:** #41. **Schema:** `Implementation/Contracts/P1/CombatCastEvent.schema.json`. **Example:** `Implementation/Contracts/P1/Examples/CombatCastEvent.example.json`.

## 1. Vì sao event mới thay vì nhét vào `CombatEvent`

`CombatEvent` hiện là kết quả cast một bước (`combat.effect`), không đủ cho adapter VFX cần phân biệt bắt đầu/impact/kết thúc/huỷ. Thêm enum tự do vào `CombatEvent` sẽ phá client cũ và trộn semantic. Event mới tách version, giữ `CombatEvent` làm compatibility path.

## 2. Lifecycle

| `eventType` | Khi phát | Field bắt buộc thêm |
|---|---|---|
| `CAST_START` | server chấp nhận command, bắt đầu cast | `groundXWu/groundYWu` nếu skill ground-target |
| `CAST_IMPACT` | hit/miss được resolve | `targetId` (hoặc ground point), `outcome` (`hit`/`miss`/`blocked`) |
| `CAST_END` | cast kết thúc bình thường | — |
| `CAST_CANCEL` | bị huỷ do chết/despawn/đổi state | lý do nằm ở event phía server khác, không thêm field tự do |

Bất biến: cùng `castId`, `serverTick` không giảm trong một cast; `revision` là revision aggregate của actor/target tại thời điểm phát.

## 3. Field

- `eventId`, `castId`: hex32; castId ổn định cho toàn lifecycle.
- `mapId`, `floorId`, `sourceId` (`CHR_`/`ENT_`), `targetId` optional cùng pattern.
- `skillId` theo 3 definition hiện có.
- `serverTick` (20 Hz), `emittedAtUtc` UTC giây, `revision` ≥ 0.
- `outcome` optional (`hit`/`miss`/`blocked`); không có `damage` trong v1 — damage đi kèm khi numeric canonical được khóa.
- `vfxKey` optional để adapter tra asset; server lấy từ SkillDefinition, không nhận từ client.

## 4. Versioning / migration

- `schemaVersion=1`; client cũ **không** nhận event này qua endpoint hiện tại (không đổi response `/p1/combat`).
- Khi mở transport mới: server từ chối client không khai báo version hỗ trợ; không tự down-convert event.
- Không đổi `CombatInput`, `CombatEvent`, `Envelope` trong PR này.

## 5. Non-goals

Damage/heal/status/shield/counter, mob AI, loot/reward, persistence, transport realtime. Các phần này theo QOD-12b/QOD-13/QOD-14.

## 6. Câu hỏi mở

1. OpenCode cần `CAST_START` cho mọi skill hay chỉ skill có telegraph? (đề xuất: mọi skill, vì client cần lock animation).
2. Ground point cho CONE/DASH lấy tại impact hay tại cast start? (đề xuất: `CAST_START` = vị trí aim, `CAST_IMPACT` = điểm resolve).
3. Client có cần `vfxKey` hay tự map từ `skillId`? (đề xuất: giữ `vfxKey` để tránh hard-code path trong client).
