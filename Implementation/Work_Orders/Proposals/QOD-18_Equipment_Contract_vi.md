# Packet hợp đồng Equip/Unequip (QOD-18 Q-E) — REQUEST ĐÃ DUYỆT, HANDLER SAU GATE OFF

Gửi Antigravity #85 (client) + Codex (review). Hai request schema đã được duyệt và áp dụng (`EquipRequest`/`UnequipRequest`); endpoint handler đã viết nhưng `P1:Equipment:Enabled=false`. Xem §7 cho sai lệch slot set phát hiện khi implement.

## 1. Hiện trạng server (đã có, không phải đề xuất)

- Inventory domain: item instance (`instanceId`, `templateId`, `stack`, `location = BAG`), currency, `InventoryMutation` (add/remove/currency deltas), grants/equips/removals có **revision + slot guard**, đã có test self-check và turn-in transaction dùng lại.
- Item catalog: `docs/production/Item_Master_Catalog_vi.csv` có `item_id, category, slot, class_id, required_level, rarity_pool, weapon_power, armor, primary/secondary_stat, stack_limit, durability, binding, tradeable`.
- HTTP hiện chỉ **read-only**: `GET /p1/inventory/{sessionId}`. Không có endpoint mutate nào.

## 2. Phạm vi có thể mở ngay (có đủ dữ liệu)

`POST /p1/inventory/equip` và `POST /p1/inventory/unequip` chỉ làm **metadata + ràng buộc**, chưa áp stat vào combat:

Yêu cầu (envelope v1 hiện có + `X-Session-ID`):
```jsonc
{ "schemaVersion": 1, "requestId": "<hex32>", "idempotencyKey": "<hex32>",
  "sentAtUtc": "…Z", "characterId": "CHR_…",
  "payload": { "itemInstanceId": "<hex32>", "expectedRevision": 12 } }
```
Trả về: `InventorySnapshot` hiện có + `equipment: [{ slot, itemInstanceId, templateId }]` + `revision` (revision của inventory aggregate, không phải session revision).

Lỗi (enum đóng, đúng pattern `P1.ERROR.[A-Z_]+`):
`invalid_payload`, `session_not_found`, `item_not_found`, `wrong_location`, `slot_occupied`, `class_restricted`, `level_required`, `not_equippable`, `revision_conflict`, `idempotency_conflict`.

Quy tắc:
1. Equip chỉ nhận item **đang ở BAG**; unequip trả item về BAG; không tự đổi `location` ngoài 2 chiều này.
2. Một slot một item (từ `slot` của template). `slot_occupied` khi equip đè; client phải unequip trước (không auto-swap trong v1).
3. `class_id` của template phải khớp class nhân vật (`CLASS_MINH_KIEM` là lớp duy nhất P1 hỗ trợ); `required_level <= PlayerSession.Level`.
4. `expectedRevision` bắt buộc để tránh lost update; sai revision → `409 revision_conflict` + snapshot mới.
5. `idempotencyKey` theo (character, key) như turn-in: replay trả đúng kết quả cũ, payload khác cùng key → `idempotency_conflict`.
6. **Không** đụng quest/receipt/cooldown; equip/unequip không cấp XP, không phát loot.

## 3. Phạm vi CHƯA mở (thiếu nguồn — ghi đúng field)

| Field thiếu | Ảnh hưởng | Nguồn cần |
|---|---|---|
| Công thức áp `weapon_power/armor/primary_stat` vào `DamageFormula` | Equip chỉ là metadata, combat vẫn dùng baseline 20/10 | `Production_Rules` §2 + DEC-023 (alias armor/weapon_power/primary không cộng đôi) |
| Số slot trang bị theo class + rule 2 tay/1 tay | Chưa chặn được tổ hợp slot | `Class_Passive_Production_Data_vi.csv` / class doc |
| Sức chứa túi (100 slot?) + policy khi đầy | Không thể trả lỗi `bag_full` có cơ sở | Rules §5 hoặc owner decision |
| Durability tiêu hao / binding / tradeable khi equip | Chưa mutate durability | catalog có cột nhưng chưa có quy tắc |
| `use` item (potion) | Chưa mở endpoint `use` | cần rule hồi HP/MP % + cooldown |

## 4. Bằng chứng cần có khi mở (test plan)

- self-check: equip/unequip round-trip giữ revision tăng đúng 1 mỗi lần; `slot_occupied`; `class_restricted` (CLASS_ANH_DAO); `level_required`; `revision_conflict`; replay same key; hai request song song cùng key → một thắng.
- smoke: sau equip, `GET /p1/inventory` thấy `equipment[]` đúng slot/templateId; unequip trả item về BAG, không mất stack.
- e2e: equip → turn-in quest → inventory vẫn giữ item đã equip; turn-in rollback không làm mất equipment.

## 5. Câu hỏi cho owner

1. Slot set chuẩn của `CLASS_MINH_KIEM` (Nón/Áo/Giày/Vũ khí/Phụ kiện?) — catalog có `slot` nhưng chưa có danh sách slot hợp lệ theo class.
2. Có cho auto-swap khi slot đang có item không, hay bắt buộc unequip trước (đề xuất của tôi: bắt buộc, đơn giản và không mất dữ liệu)?
3. `expectedRevision` dùng revision inventory (đề xuất) hay revision session?
4. Khi equip làm đổi `maxHP/maxMP` (nếu sau này stat áp), current HP giữ tuyệt đối rồi clamp — đúng ý Q-D chứ?

## 6. Câu trả lời đề xuất cho §5 (Qoder) — cần owner xác nhận trước khi mở wire

1. **Slot set của `CLASS_MINH_KIEM`:** `Nón, Áo, Giày, Vũ khí, Phụ kiện` — đúng 5 giá trị `slot` đang xuất hiện trong `Item_Master_Catalog_vi.csv` cho lớp MK; không thêm slot nào khác, danh sách này lấy từ cột `slot` chứ không tự đặt. Nếu catalog có slot thứ 6, loader phải fail-fast chứ không lặng lẽ chấp nhận.
2. **Auto-swap:** **không** auto-swap. Equip khi slot đang có item → `409 slot_occupied` + snapshot; client gọi `unequip` trước. Lý do: turn-in đã chứng minh nguyên tắc “một thay đổi một transaction”, và auto-swap sẽ mất item nếu response rơi.
3. **`expectedRevision`:** dùng **inventory aggregate revision** (cùng con số `GET /p1/inventory` trả), không dùng session revision — vì thao tác này chỉ mutate inventory; session revision tăng theo move/HP nên sẽ tạo 409 giả.
4. **Đổi `maxHP/maxMP`:** giữ **current tuyệt đối rồi clamp** (đúng Q-D): `hp = min(hp, newMax)`, không tự heal, không hồi khi chỉ equip/unequip.

Bốn câu trả lời này **chưa phải quyết định owner** — packet vẫn ở trạng thái chờ duyệt; khi được xác nhận, schema `EquipRequest/UnequipRequest` + example + `validate_contracts.py` + endpoint sẽ được viết trong một PR riêng (route mới, gate `P1:Equipment:Enabled` mặc định OFF).

## 7. Đính chính khi implement: catalogue có 12 slot, không phải 5

Câu trả lời §6.1 dựa trên một kiểm tra sai: `Item_Master_Catalog_vi.csv` **không** chỉ có 5 giá trị `slot` cho lớp MK. Đo lại trên hai catalogue nguồn:

| Nguồn | Kết quả đo |
|---|---|
| `Item_Master_Catalog_vi.csv` | 12 nhãn trang bị/lớp: Nón, Áo, Quần, Găng, Giày, Kiếm, Dây chuyền, Nhẫn trái, Nhẫn phải, Ngọc bội, Phi phong, Ấn hộ mệnh |
| `Item_Rarity_Variant_Catalog_vi.csv` | cùng 12 nhãn, 35 item mỗi nhãn cho lớp MK; đây là nơi chứa các id quest thực cấp (`EQ-MK-BOOTS-T1-R-COMMON`) |
| `Character_Equipment_Inventory_Spec_vi.md` §3 | bảng **12 slot người chơi** với ID `EQUIP_HAT`, `EQUIP_CHEST`, `EQUIP_LEGS`, `EQUIP_WEAPON`, `EQUIP_GLOVES`, `EQUIP_BOOTS`, `EQUIP_NECK`, `EQUIP_RING_L`, `EQUIP_RING_R`, `EQUIP_PENDANT`, `EQUIP_CLOAK`, `EQUIP_SEAL` |

Vì enum 5 token đã được owner duyệt và không thể tự mở rộng, handler v1 làm đúng phần biểu diễn được và **từ chối phần còn lại thay vì đoán slot**:

| Nhãn catalogue | Token v1 | Ghi chú |
|---|---|---|
| Nón / Áo / Giày | `HAT` / `CHEST` / `BOOTS` | trực tiếp |
| Kiếm (và Đao/Bút/Chùy/Cung ở lớp khác) | `WEAPON` | theo category `Trang bị / vũ khí`; class gate vẫn chặn lớp khác |
| Dây chuyền, Nhẫn trái, Nhẫn phải, Ngọc bội, Phi phong, Ấn hộ mệnh | `ACCESSORY` | 6 slot nguồn gộp vào 1 token đã duyệt ⇒ chỉ đeo được 1 phụ kiện/lúc |
| Quần / Găng | — | `not_equippable`; không có token trong enum đã duyệt |

Loader **fail-fast** nếu gặp một nhãn trang bị khác không có token (trừ hai nhãn đã ghi ở trên), nên một slot mới trong nguồn không thể lọt qua im lặng.

**Cần owner quyết định trước khi mở rộng:** có đổi `UnequipRequest.slot` (và `InventorySnapshot.slot`) sang đủ 12 token theo ID của spec (`HAT, CHEST, LEGS, GLOVES, BOOTS, WEAPON, NECK, RING_L, RING_R, PENDANT, CLOAK, SEAL`) hay không. Đây là thay đổi wire nên phải có packet/duyệt riêng; cho đến lúc đó Quần/Găng và phụ kiện thứ hai là unsupported có nguồn, không phải bug.

Response đã chốt khi implement: `EquipmentResponse.schema.json` với `result` = `InventorySnapshot` (đúng như §2 mô tả "InventorySnapshot hiện có"); phía client tự lọc `location == "EQUIPPED"` thay vì thêm mảng `equipment[]` chưa có schema.
