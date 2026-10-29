# QOD-11 — Inventory, dependency graph và contract delta

**Issue:** #41. **Branch:** `qoder/qod-11-world-core` (base `main` @ `5301d7e`). **Ngày:** 2026-10-29.
Không có thay đổi wire/contract trong PR này; đây là phần world core + tài liệu để review trước khi mở rộng.

## 1. Hiện trạng server (không viết lại)

| Miền | Thành phần | Trạng thái |
|---|---|---|
| Session | `ISessionStore` in-memory, `/p1/sessions` | Đạt P1, không auth |
| Movement | `/p1/move`, clamp bounds, sequence monotonic | Đạt P1; **chưa swept**, chưa kiểm topology |
| World snapshot | `WorldSnapshotFactory`, `/p1/world/{id}` | `entities` luôn rỗng |
| Combat | `ICombatService`, `/p1/combat`, skill catalog 3 skill | Cast gate đạt; **chưa damage**, target registry rỗng |
| Quest | `IQuestService`, `/p1/quests/{id}`, accept (flag off) | `P00-01` chạy; turn-in/reward chưa |
| Inventory | `IInventoryService`, `/p1/inventory/{id}` | Đọc/ghi nội bộ đạt; chưa có item catalog/stack rules |
| Teleport | `ITeleportService` | Domain only, chưa mở endpoint |
| Geometry | `WorldGeometryService` + `MapTopology` loader | LOS đạt; **chưa swept movement**, chưa footprint |
| NPC anchors | `npc_anchors.json` (104) | Dùng cho accept; chưa hợp nhất với world registry |
| World entities | **(mới trong PR này)** | 24 placement Bến Mưa, chưa HP/stat |

## 2. Dependency graph

```text
manifest canonical (CSV)
  ├─ build_npc_anchors.py ──> npc_anchors.json ──> NpcAnchorCatalog ──> QuestAccept (guard 3–5)
  └─ build_world_entities.py ─> world_entities_bm.json ─> WorldEntityCatalog ─> WorldEntityRegistry
                                                                                  └─> (QOD-12) combat targets, aggro
MapTopology bundle ──> WorldGeometryCatalog ──> WorldGeometryService ──> QuestAccept LOS
                                                     └─> (QOD-11b) swept movement
ServerClock ──IServerClock──> WorldEntityRegistry (respawn/despawn)
                           └─> (QOD-11b) tick driver
```

## 3. Contract delta

Không đổi response/request nào trong PR này.

Đề xuất cho các PR tiếp theo (chưa code wire):

1. **Movement** — khi có bundle `REVIEWED`: từ chối bước đi cắt blocked/rời walkable, kiểm cả đoạn (swept) với footprint explicit (`P1World:ActorFootprintRadiusWu`, lấy từ DEC-016 half-width 0.6 WU, không tự co map). Rejected không tiêu sequence/revision. Không đổi shape `MoveIntent`/`WorldSnapshot`.
2. **World snapshot `entities`** — chỉ populate khi có entity registry ổn định; cần proposal trước vì `WorldSnapshot.schema.json` đang cố định `entities[]` shape.
3. **Tick** — 20 Hz theo production spec; snapshot cadence hiện tại giữ nguyên, không tự đổi wire.
4. **Combat target** — QOD-12 sẽ nối registry vào `ICombatTargetProvider`, vẫn không thêm damage khi chưa có numeric canonical.

## 4. Dữ liệu canonical vs fixture

- `world_entities_bm.json` sinh từ manifest: 8 NPC, 8 MOB_GROUP, 5 GATHER_NODE, 2 BOSS, 1 INTERACTABLE (24 entity). Mỗi entity là một **spawn instance** theo `record_id`; `templateIds` tách khỏi instance; `quantity`/`respawnSeconds`/`condition` giữ nguyên từ manifest.
- **Không** có HP/ATK/DEF: numeric combat chưa được khóa trong content, nên registry ghi rõ `hpRule` và không bịa số.
- Điều kiện spawn (`condition`) chỉ được lưu, chưa thực thi — QOD-12/13 sẽ bật theo quest state.
- Bundle topology duy nhất vẫn là `SYNTHETIC_TEST_ONLY`; không gọi là Bến Mưa đã duyệt.

## 5. Thay đổi trong PR này

- `Implementation/Tools/build_world_entities.py` → `Implementation/Content/Runtime/world_entities_bm.json` (24 entity, 19 template).
- `Server/Health/World/IServerClock.cs`: interface + `ManualServerClock` để test không sleep; `ServerClock` implement interface.
- `Server/Health/World/WorldEntities.cs`: catalog/loader (validate map/floor/bounds/template refs/duplicate) + registry (despawn/respawn, state revision, `Update()` theo clock).
- Program: load registry, fail startup nếu file hỏng, log số lượng theo kind.
- Self-check thêm 7 assertion: registry 24 entity, NPC/mob placement canonical, despawn/respawn với clock thủ công, NPC không despawn được, node chuyển `DEPLETED`.

## 6. Kế hoạch test QOD-11 (phần còn lại)

- Swept movement với topology `REVIEWED` dựng trong bộ nhớ: bước lớn xuyên tường, góc tường, lỗ, khác floor, non-finite, stale sequence.
- Reject không đổi vị trí/revision/sequence.
- Despawn/respawn đã có; thêm test session hết hạn dọn entity/cooldown (QOD-12 lifecycle).
- Tick driver 20 Hz với clock thủ công, không sleep.

## 7. QOD-11b — swept movement (PR tiếp theo)

- `WorldGeometryService.CheckWalkSegment(map, floor, from, to, footprintRadiusWu)`: centerline phải walkable, không cắt blocked, và mọi điểm lấy mẫu ≤0,25 WU phải cách mép blocked ≥ radius; trả `Allowed`/`Blocked`/`NotEnforced`.
- `MoveAsync` tính vị trí đích rồi kiểm sweep **trước khi** ghi state; `Blocked` → `422 movement_blocked` (code mới, không đổi shape request/response), không tiêu sequence/revision/position. Không có bundle `REVIEWED` → `NotEnforced`, giữ hành vi P1 và log dev stub.
- Footprint là tham số explicit `P1World:ActorFootprintRadiusWu` (0,6 WU = nửa bề rộng hero DEC-016), không inset map bằng số đoán; radius 0 tắt clearance.
- Test: 9 assertion mới trong self-check (clear, wall, big step, hole, corner, floor, non-finite radius, footprint 0,6 chặn / 0,1 cho qua), tổng 75. Nhánh reject của endpoint không chạy được trên HTTP smoke vì CI chỉ có bundle synthetic; geometry + guard đã test in-process, wiring được review qua PR.

## 8. Checklist gói QOD-11→15

- [x] QOD-11a: inventory/contract delta + world entity registry + clock injectable.
- [x] QOD-11b: swept movement theo topology + footprint + tests (PR tiếp theo).
- [ ] QOD-12: combat/mob lifecycle + cast event proposal.
- [ ] QOD-13: quest/exploration/gathering.
- [ ] QOD-14: turn-in/reward atomic.
- [ ] QOD-15: headless E2E + handoff.
