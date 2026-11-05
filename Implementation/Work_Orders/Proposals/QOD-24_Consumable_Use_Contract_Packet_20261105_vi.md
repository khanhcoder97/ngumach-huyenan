# Packet hợp đồng consumable-use (QOD-24 Q5) — **CHỜ DUYỆT — chưa wire, chưa route**

Gửi Codex (review) + owner (#87). Nguồn: `docs/production/Item_Master_Catalog_vi.csv` (14 hàng `Tiêu hao`), `docs/production/Production_Rules_Complete_v1_vi.md:21,28` (clamp `0..maxHP`, quy ước làm tròn), `Implementation/Work_Orders/29_ALL_STAFF_FULL_GAMEPLAY_EPICS_20261105.md` (Q5: "HP/MP clamp, buff stack, consumable… Transaction/revision/capacity/receipt chống âm và double grant").

Máy domain **đã có** và đã được đo: `Server/Health/Gameplay/Inventory/ConsumableCatalog.cs` (`ConsumableCatalog.Load` + `ConsumableService.Consume`). Packet này chỉ xin phần **wire**: client được gọi gì, lỗi nào trả status nào.

## 1. Đã ship (data + domain, không đổi hành vi production)

- Phân loại **14/14** hàng `Tiêu hao` ngay lúc boot (`Program.cs` đăng ký singleton, log counts). Không có trạng thái "không đọc": mỗi hàng hoặc là một luật % hoặc bị ghi nhận là hiệu ứng server này chưa làm được, kèm **đúng nguyên văn** ô nguồn.
- **7 luật** tính được: `POT-HP-01/02/03` = 25/35/45% HP tối đa, `POT-MP-01/02/03` = 20/30/40% MP tối đa, `POT-REVIVE-01` = 15% HP tối đa nhưng slot ghi "Hồi sinh" → **cờ revive**, không thành một vết hồi miễn phí cho nhân vật còn sống.
- **7 hiệu ứng từ chối** vì subsystem chưa tồn tại, giữ nguyên nhãn: `Giải trạng thái` (Xóa Chậm hoặc Độc), `Sửa chữa` (25 điểm độ bền), `Dịch chuyển` (Niệm 10 giây), `Thức ăn PvE` ×2 (+2%/20 phút), `Thức ăn nghề` (+10% tốc thu thập/20 phút), `Bảo vệ phân giải` (1 lần dùng).
- `Consume` đi theo đúng khuôn giao dịch cả nhà đã chốt: revision tường thắng (`revision_conflict` retryable), idempotency per-character, **hash request** để same-key-khác-payload thành `idempotency_conflict`, ledger bounded 256, và commit dưới `actor.SyncRoot` với replay kiểm lại trong lock.
- HP/MP clamp đúng `Production_Rules §2.6`: cộng **không bao giờ vượt max**, và không bao giờ trừ. `InventoryV2Slots.TryResolveLabel` vẫn đòi category equipment, nên việc `ItemCatalog` giữ nhãn `slot` cho mọi hàng không làm potion thành trang bị mặc định.
- 14 self-check mới, **550 passed / 0 failed**, đo ba lần liên tiếp tại head này. Tên check: `consumable.catalog_shape_is_fourteen_rows_seven_rules_and_seven_effects_this_server_cannot_perform`, `...catalog_percents_are_exactly_the_source_cells`, `...catalog_refuses_a_cell_it_cannot_parse_and_a_slot_label_it_does_not_know`, `...hp_drink_restores_a_quarter_of_max_and_spends_one_stack`, `...mp_drink_moves_only_its_own_pool_and_empties_the_instance`, `...replayed_key_returns_the_recorded_result_without_a_second_spend`, `...same_key_with_a_different_payload_is_a_conflict`, `...heal_clamps_at_max_hp_and_reports_only_the_points_gained`, `...a_drink_with_nothing_to_restore_is_refused_and_the_stack_survives`, `...floor_rounding_at_a_three_point_maximum_spends_nothing`, `...floor_is_the_ruleset_value_convention_not_round_half_up`, `...level_revive_effect_and_category_refusals_all_name_their_row`, `...stale_revision_and_unknown_instance_move_nothing`, `...four_threads_on_one_key_spend_exactly_one_stack`.

**Chưa có gì trên wire:** không DTO, không schema, không route, không gate, không đổi `appsettings.json`. Server này chỉ trả lời `Consume(...)` cho code trong process.

## 2. Đề xuất (A) — một verb, tối thiểu

`POST /p1/inventory/consume`, sau gate `P1:InventoryConsume` (mặc định **OFF**):

```jsonc
// request payload
{ "itemInstanceId": "ITM_…", "expectedRevision": 7 }

// result
{
  "inventory": { /* InventorySnapshot — cùng hình với read route */ },
  "hpRestored": 10, "mpRestored": 0,
  "hpAfter": 100, "mpAfter": 50,
  "effectItemId": "POT-HP-01"
}
```

`hpRestored`/`mpRestored` là **số điểm thực sự vào**, không phải % nguồn: client không cần biết 25% là bao nhiêu và không được tự tính (đó là lý do death-return cũng trả `hp` thay vì công thức). `expectedRevision` bắt buộc, `idempotencyKey` bắt buộc — chống double grant.

Bảng status tôi đề xuất cho domain đã có:

| domain code | HTTP | ghi chú |
|---|---|---|
| `revision_conflict` | 409, retryable | kèm snapshot hiện tại, giống equipment |
| `idempotency_conflict` | 409 | same key khác payload |
| `item_not_found` | 404 | instance không có trong bag |
| `wrong_location` | 409 | item không ở `BAG` |
| `not_consumable` | 422 | **code mới** — hàng không thuộc `Tiêu hao` |
| `level_required` | 422 | từ `required_level` của chính hàng đó |
| `effect_unsupported` | 422 | **code mới** — hiệu ứng cần subsystem chưa có; messageKey trỏ tên hàng |
| `revive_not_modelled` | 422 | **code mới** — hàng revival, chưa có luật revive |
| `no_effect` | 409 | **code mới** — không có điểm nào để hồi; stack còn nguyên |

`effect_unsupported` khác `not_consumable`: một bên là "đây không phải đồ ăn được", một bên là "đây là đồ ăn được nhưng máy này chưa làm được hiệu ứng đó". Gộp lại thì client không thể biết mình nên hiện thông báo nào.

## 3. Những gì packet này KHÔNG tự quyết

- **Q1 — làm tròn.** Nguồn không nói cho hồi máu. Ruleset dùng `floor` cho **magnitude** (damage `§2.6` `max(1,floor(...))`, EXP `§4 floor(10+2×lvl)`), còn death-return đã duyệt dùng `ceil` kèm `max(1,...)`. Tôi đang dùng **floor** vì đó là quy ước magnitude của bộ luật này, và đo: `101 × 25% = 25,25 → 25`; `3 × 25% = 0,75 → 0`. Phương án khác: `ceil`, hoặc `max(1, floor(...))` (mượn luật death-return — tôi **không** tự mượn). Hệ quả của floor ở max nhỏ: ở `MaxHp = 3` thì **mọi** liều HP đều thành 0 → bị từ chối `no_effect` chứ không mất item. Owner chọn một, tôi pin số đó.
- **Q2 — uống khi đã đầy.** Nguồn không nói. Mặc định tôi đang làm: **từ chối** (`no_effect`) và **không mất stack**, vì cho phép uống để mất một item mà không thay đổi gì là áp một hình phạt không có nguồn. Nếu owner muốn "vẫn mất item" (anti-macro), đó là một quyết định cân bằng, không phải suy ra từ dữ liệu.
- **Q3 — revive.** `POT-REVIVE-01` là % HP nhưng framed là hồi sinh: cần luật "ai được dùng cho ai (mình / đồng đội), mục tiêu phải `DOWNED` không, có phá `movementWindowReset`/penalty của death-return không, có reset cooldown return không". Server chưa có nguồn cho bất kỳ vế nào → đang từ chối `revive_not_modelled`.
- **Q4 — cooldown khi dùng.** `GDD` giới hạn spam cho **chat**, không có cooldown cho consumable; `Production_Rules §2` có "action keys still inside cooldown" cho combat. Không tự đặt cooldown cho item. Nếu owner muốn giới hạn frequency, cần một con số + phạm vi (per-item / per-category / global).
- **Q5 — route vocabulary.** Đây là v1 `InventorySnapshot` hay v2 `InventorySnapshotV2`? Potion không chiếm slot nên v1 là đủ; nhưng nếu sau này hiệu ứng ghi vào 12-slot (ví dụ `Seal` tiêu hao), thì nên đi vocabulary v2 ngay. Mặc định tôi chọn **v1 snapshot** vì domain chỉ đụng bag.
- **Q6 — gate.** Dùng chung `P1:Equipment` (cùng bản chất "mutation có revision trên inventory") hay gate riêng `P1:InventoryConsume`? Mặc định: **riêng**, để bật alpha không tự mở thêm bề mặt.
- **Q7 — buff duration.** Ba hàng `Thức ăn` là buff có thời hạn (20 phút) — thuộc phần "buff stack" của Q5 và cần nơi lưu trạng thái theo tick. Server đã có `CombatStatusProjection` (read model, chưa wire) và chưa có store buff per-character. Đây là một packet riêng; tôi không nhét buff vào verb này.
- **Q8 — `KIT-REPAIR-01`.** Độ bền đã có trên item (`durability`, nguồn là `Item_Master_Catalog_vi.csv`), nên "25 điểm" **áp được** mà không cần subsystem mới — nhưng nó sửa `Durability` của một instance khác, tức là một transaction hai chiều (tiêu 1 kit + tăng 1 độ bền, có cap). Cần owner xác nhận cap (`min(max_durability, current + 25)`?) và cách chọn target (`payload.targetInstanceId`), rồi tôi làm thành một packet nhỏ riêng vì nó đụng semantics của `durability`.

## 4. Việc sẽ làm sau khi được duyệt (không làm trước)

1. `ConsumeRequest`/`ConsumeResponse` schema + examples dưới `Implementation/Contracts/P1/`.
2. Route `POST /p1/inventory/consume` sau gate đã chọn, handler gọi thẳng `IConsumableService` (không viết lại logic nào).
3. Map `messageKey` cho các code mới (`P1.ERROR.NOT_CONSUMABLE`, `P1.ERROR.EFFECT_UNSUPPORTED`, `P1.ERROR.REVIVE_NOT_MODELLED`, `P1.ERROR.NO_EFFECT`) — thêm code mới vào `P1ErrorCodes` là **wire change**, nên nằm sau bước duyệt này.
4. Self-check + smoke: gate-off 405/404 đúng hình hiện hành, ngoài tầm (không có guard khoảng cách cho item — xác nhận lại), stale revision, stack cuối cùng hết instance, replay, conflict, và **một proof chống double-grant qua HTTP** (four parallel same key → một stack mất).
5. Chỉ sau đó mới tính buff/repair/revive, mỗi cái một packet.

## 5. Trạng thái hiện tại

Domain + classification đã chạy và đã đo (550 checks). Không có gì trong `appsettings.json` bật. Không có route nào cho consumable, nên client hôm nay **không** tự uống được thuốc — và server cũng không bao giờ tự hồi máu bằng metadata của item.
