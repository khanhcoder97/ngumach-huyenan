# QOD-10 — Hợp đồng top-down topology và LOS tương tác

**Trạng thái:** Bước 1 (contract + fixture + validator) đã merge qua PR #34. Bước 2 (geometry service + LOS guard) implement trong PR #35. Chưa có bundle `REVIEWED` của Bến Mưa nên production vẫn `P1:QuestAccept:Enabled=false`, query trả `not_enforced` và server log `DEV STUB`.
**Issue:** #32. **Nguồn:** `docs/production/Top_Down_Gameplay_World_Spec_vi.md` (DEC-016), `Production_Rules_Complete_v1_vi.md`, `Production_Completion_Addendum_vi.md` §2. **Canonical IDs:** `MAP_BEN_MUA`, `NPC_LYAN`, record `MAN-BM-NPC_LYAN`.

## 1. Phạm vi

Bundle mô tả vùng đi được/chặn cho một map trên mặt phẳng XY và trả lời câu hỏi tương tác: actor có đứng cùng tầng, trong 5 WU và nhìn thấy NPC không.

Trong phạm vi: schema `MapTopology`, fixture synthetic, validator/round-trip, semantics để service dùng ở bước 2.

Ngoài phạm vi: damage/combat LOS, portal, teleport client, persistence, floor links (để `bundleVersion` sau), layout Bến Mưa thật (Muse bàn giao + review).

## 2. Bundle

File: `Implementation/Content/Examples/MapTopology/<name>.json`; schema `Implementation/Content/Schemas/MapTopology.schema.json`.

| Trường | Ý nghĩa | Ràng buộc |
|---|---|---|
| `schemaVersion` | phiên bản schema | `1` |
| `mapId` | map canonical | `^MAP_[A-Z0-9_]+$`, phải có bounds trong `map_bounds.json` |
| `layoutVersion` | version layout do content owner tăng | ≥ 1 |
| `bundleVersion` | version bundle engine | hiện `2` (khớp DEC-016); v1 cũ không dùng để chặn LOS |
| `coordinateSystem` | hệ toạ độ | `TOP_DOWN_XY` |
| `reviewState` | trạng thái duyệt | `REVIEWED` hoặc `SYNTHETIC_TEST_ONLY` |
| `bounds` | biên tổng thể của map | phải bằng đúng registry `map_bounds.json` |
| `floorIds` | các tầng có trong bundle | không rỗng, không trùng; P1 chỉ `OVERWORLD` |
| `walkablePolygons[]` | vùng đi được (không rỗng) | `{floorId, points[]}` |
| `blockedPolygons[]` | vùng chặn | `{floorId, points[]}` |
| `placements[]` | anchor NPC theo record canonical | `{recordId, npcId, floorId, xWu, yWu}` |
| `sourceRefs[]` | nguồn/ghi chú | không rỗng |

`floorLinks` cố ý chưa có trong schema này: chỉ thêm ở `bundleVersion` sau, không tự cho client teleport.

## 3. Semantics hình học

- Mặt phẳng XY, +Y hướng Bắc; `bounds` chỉ là giới hạn ngoài, **không** chứng minh vùng bên trong đi được.
- Một điểm đi được khi: nằm trong ít nhất một `walkablePolygons` cùng `floorId` **và** nằm ngoài mọi `blockedPolygons` cùng floor. Blocked thắng walkable khi chồng lấn.
- Điểm dùng **foot pivot** của actor theo DEC-016; không dùng art bounds, không dùng đỉnh sprite.
- Mép tường chặn LOS: đoạn từ chân actor tới anchor NPC không được cắt phần trong của bất kỳ blocked polygon nào, và mọi điểm trên đoạn phải còn trong vùng walkable cùng floor.
- Chạm góc: tiếp xúc chỉ tại một điểm ở tham số nội của đoạn được coi là **chặn** (conservative), để không xuyên góc hai tường. Tiếp xúc đúng tại đầu/cuối đoạn với chính biên vùng walkable không bị coi là chặn.
- Cùng floor là điều kiện bắt buộc; P1 chỉ có `OVERWORLD`, nên khác floor hiện không xảy ra nhưng query vẫn kiểm.
- Khoảng cách tương tác ≤ **5 WU** đo từ chân (DEC-016 §3), không phải tâm sprite.
- Không có walkable polygon ⇒ không có LOS hợp lệ ⇒ mọi accept bị từ chối khi bật enforcement.

## 4. Validation bắt buộc (đã có tool)

`Implementation/Tools/validate_topology.py` kiểm:

1. `schemaVersion=1`, `coordinateSystem=TOP_DOWN_XY`, `bundleVersion=2`.
2. `mapId` có bounds registry; `bounds` khớp chính xác 4 giá trị.
3. `floorIds` không rỗng/không trùng; mọi polygon và placement dùng floor đã khai báo.
4. Mỗi polygon ≥ 3 điểm, toạ độ hữu hạn, nằm trong bounds, **không tự cắt** (kể cả chồng cạnh collinear).
5. `walkablePolygons` không rỗng.
6. Mỗi placement: `recordId` tồn tại trong manifest, là dòng `NPC`, `npcId` khớp `entity_id`, `map_id` khớp bundle, toạ độ hữu hạn/trong bounds, không trùng `(npcId, floorId)`.
7. `sourceRefs` không rỗng.
8. Bundle hỏng ⇒ validator fail; loader server (bước 2) sẽ fail startup thay vì bỏ qua im lặng.

## 5. Fixture synthetic

`Implementation/Content/Examples/MapTopology/SYNTHETIC_TEST_ROOM_MAP_BEN_MUA.json`, `reviewState: SYNTHETIC_TEST_ONLY`, `layoutVersion: 1`.

- Phòng walkable `(30,-10)-(60,10)`, NPC `NPC_LYAN` tại `(42,0)` (record `MAN-BM-NPC_LYAN`).
- Tường chặn `x=45..46` chia đôi phòng → test “clear line” phía Tây và “blocked wall” phía Đông.
- Trụ/lỗ `(52..54, 2..4)` → test “endpoint inside wall” và “segment xuyên lỗ không walkable”.
- Khối chạm góc `(60,10)` → test “corner touch”.
- Điểm ngoài phòng `(20,0)` → test “outside walkable”.

Fixture này **không phải** layout Bến Mưa và không được dùng làm nav canonical; nó chỉ chứng minh shape + validator + (bước 2) thuật toán.

## 6. Tích hợp quest accept (bước 2, đã implement)

- Thêm `IWorldGeometryCatalog` + loader; chỉ bundle `REVIEWED` mới được dùng để chặn LOS.
- Query: cùng `mapId`+`floorId`, khoảng cách chân ≤ 5 WU, đoạn không cắt blocked/ra ngoài walkable.
- Khi chưa có bundle `REVIEWED`: giữ `P1:QuestAccept:Enabled=false` (route không map) và `DEV STUB` như hiện tại; không bỏ guard để gọi production.
- Geometry service triển khai trong `Server/Health/World/WorldGeometry.cs` (+ loader `MapTopology.cs`); self-check phủ 12 case geometry/LOS, gồm accept bị chặn bởi tường và accept hợp lệ phía Tây.
- Không đổi idempotency, `inputSequence`, revision hay reward.

## 7. Bằng chứng (chạy thật)

Xem `Implementation/Reports/QOD-10_topology_validation.md` để có command + output đầy đủ. Tóm tắt:

- `python Implementation/Tools/validate_topology.py` → 1 bundle synthetic, pass.
- `python Implementation/Tools/validate_content.py` → 8 definition schema (gồm `MapTopology`) pass.
- `python Implementation/Tools/validate_contracts.py` → pass.
- 7 case tiêu cực (bowtie, 2 điểm, floor trùng, record lạ, bounds lệch, điểm ngoài bounds, bundleVersion sai) đều fail đúng thông báo.

## 8. Câu hỏi mở cho Muse/owner

1. Biên vùng walkable có được phép chạm mép tường (đi sát tường) hay phải inset để tránh kẹt collider 1,2×0,6 WU?
2. “Corner touch = blocked” có đúng ý đồ không, hay cho phép tiếp xúc điểm khi đoạn không đi vào phần trong?
3. Bundle Bến Mưa `REVIEWED` đầu tiên cần polygon nào tối thiểu (spawn, NPC_LYAN, NPC_TA_VAN_KHANH, tuyến chính) để bật enforcement?
