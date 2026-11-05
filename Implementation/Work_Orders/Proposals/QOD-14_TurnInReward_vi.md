# QOD-14 — Turn-in và thưởng nguyên tử (proposal)

Phạm vi: mốc QOD-14 của `06_QODER_GAMEPLAY_LOOP_EPIC.md` (issue #41). Tài liệu này là contract delta trước code; chỉ implement sau khi proposal được review. Không sửa wire cũ (`QuestState`/`Envelope`/`InventorySnapshot`) — chỉ thêm message mới và mở rộng loader nội bộ.

## 1. Mục tiêu

1. Đóng vòng quest bằng `POST /p1/quests/turnin`: `READY_TO_TURN_IN → COMPLETED` kèm thưởng được cấp **đúng một lần** trong một transaction in-memory.
2. P00-01 "Thư qua bến" là acceptance slice: sau khi nhặt 3 kiện (QOD-13), giao tại `NPC_TA_VAN_KHANH` (anchor x=64 Bến Mưa) → nhận 20 `COIN` + `EQ-MK-CHEST-T1-R-COMMON`, quest `COMPLETED`, mở `P00-02` (chưa có trong catalog — chỉ đánh dấu).
3. Reward dùng **số liệu canonical đã có** trong `rewards` của QuestDefinition — không phát minh con số mới. Phần XP chưa có hệ thống → đề xuất rõ ở mục 7, không tự điền.
4. Retry/parallel turn-in chỉ thưởng một lần; replay trả kết quả ổn định; fail giữa chừng không commit một phần (có failure injection trong self-check).

## 2. Nguồn canonical tham chiếu

| Dữ liệu | Nguồn |
|---|---|
| P00-01: "giao NPC_TA_VAN_KHANH; thưởng XP, 20 Đồng, áo Thường; mở P00-02" | `docs/production/Quest_and_Narrative_Production_Spec_vi.md` bảng P00-01 |
| Block `rewards` (currency/itemIds/xpRule), `turnInNpcId`, `unlocks` | `Implementation/Content/Examples/QuestDefinition/P00-01.json` (đã được `QuestDefinition.schema.json` + `validate_content.py` duyệt) |
| `EQ-MK-CHEST-T1-R-COMMON` | `docs/production/Item_Rarity_Variant_Catalog_vi.csv` |
| `COIN` | `docs/production/Currency_Production_Data_vi.csv` |
| Anchor `NPC_TA_VAN_KHANH` Bến Mưa tại (64, 0) | `Implementation/Content/Runtime/npc_anchors.json` |
| Khoảng tương tác ≤ 5 WU, LOS như accept | `docs/production/Top_Down_Gameplay_World_Spec_vi.md` dòng 30 |

## 3. Contract delta — `POST /p1/quests/turnin`

Endpoint mới, gate `P1:QuestTurnIn:Enabled` (mặc định **false**; smoke CI bật như QuestAccept/Interact). Không đổi endpoint/schema cũ.

### 3.1 Request

Envelope giữ nguyên shape; payload là `TurnInIntent`:

```json
{
  "schemaVersion": 1,
  "requestId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "idempotencyKey": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "sentAtUtc": "2026-10-29T00:00:00Z",
  "characterId": "CHR_DEMO_01",
  "payload": { "questId": "P00-01", "npcId": "NPC_TA_VAN_KHANH" }
}
```

- `questId` pattern P1 hiện có; `npcId` pattern `^NPC_[A-Z0-9_]+$`.
- Session qua `X-Session-ID` như accept/combat/interact.
- Idempotency scope `(characterId, idempotencyKey)`, request hash = SHA256(`questId` + `|` + `npcId`); replay trả đúng outcome đầu (kể cả snapshot thưởng), payload khác cùng key → `idempotency_conflict` (409).

### 3.2 Response thành công

`TurnInResponse.result`:

| Field | Ý nghĩa |
|---|---|
| `questState` | `QuestState` đầy đủ sau turn-in (`state: COMPLETED`, `revision` +1) |
| `rewards` | `{ "currency": [{ "currencyId": "COIN", "amount": 20 }], "items": [{ "templateId": "EQ-MK-CHEST-T1-R-COMMON", "stack": 1, "location": "BAG" }], "xp": { "xpRule": "LEVEL_BAND_BASE", "applied": false } }` |
| `unlocks` | mảng questId vừa được mở (`["P00-02"]`) — chỉ thông tin, chuyển state unlock theo cơ chế lazy có sẵn |

Ví dụ:

```json
{
  "schemaVersion": 1,
  "requestId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "sessionId": "0123456789abcdef0123456789abcdef",
  "serverTimeUtc": "2026-10-29T00:05:00Z",
  "result": {
    "questState": {
      "questId": "P00-01",
      "state": "COMPLETED",
      "stepId": "STEP_P00_01_PACKAGES",
      "objectiveCounters": { "OBJ_P00_01_PACKAGES": 3 },
      "revision": 6
    },
    "rewards": {
      "currency": [{ "currencyId": "COIN", "amount": 20 }],
      "items": [{ "templateId": "EQ-MK-CHEST-T1-R-COMMON", "stack": 1, "location": "BAG" }],
      "xp": { "xpRule": "LEVEL_BAND_BASE", "applied": false }
    },
    "unlocks": ["P00-02"]
  }
}
```

### 3.3 Error codes

| Code | HTTP | Khi nào |
|---|---|---|
| `invalid_payload` | 400 | body/envelope/X-Session-ID sai |
| `session_not_found` | 404 | session không tồn tại |
| `quest_not_found` | 404 | `questId` không có trong catalog |
| `npc_mismatch` | 422 | `npcId` không phải `turnInNpcId` canonical của quest |
| `out_of_range` | 422 | khác map/floor, khoảng cách > 5 WU, hoặc LOS bị chặn (retryable) |
| `invalid_transition` | 409 | quest chưa `READY_TO_TURN_IN` (đã `COMPLETED`/`FAILED`/mới `ACTIVE`) |
| `idempotency_conflict` | 409 | cùng key, payload khác |

Code nằm trong enum `error.code` của `TurnInResponse.schema.json`; không thêm vào enum của accept/combat/interact. Không có endpoint grant tùy ý cho public client — thưởng chỉ tồn tại bên trong turn-in.

## 4. Transaction nguyên tử (in-memory)

Service mới `QuestTurnInService` (orchestrator), dùng các service sẵn có. Mọi bước của một character chạy dưới **một khóa per-character** để retry/parallel cùng lúc không xen nhau.

Thứ tự commit:

1. **Idempotency replay**: `(characterId, idempotencyKey)` đã có → trả `TurnInResult` đã lưu (kể cả khi quest đã COMPLETED — replay luôn ổn định). Hash khác → `idempotency_conflict`.
2. **Validate (không đổi gì)**: catalog → `npcId == turnInNpcId` → anchor NPC tồn tại, cùng map/floor → khoảng cách ≤ 5 WU → LOS (bundle chưa REVIEWED → `not_enforced`, giống accept) → state `READY_TO_TURN_IN`.
3. **Grant trước, flip sau**: `IInventoryService.Apply` với `AddItems` (mỗi `itemIds` → 1 instance, `Stack 1`, `BAG`) + `CurrencyDeltas` (mỗi `currency` → amount). `Apply` vốn all-or-nothing và tăng `inventoryRevision` đúng một lần. Apply fail (chỉ xảy ra khi data hỏng hoặc failure injection) → **abort, quest vẫn READY_TO_TURN_IN**, không có phần thưởng nào.
4. **Flip state**: `IQuestService.TurnIn` (đã có) → `COMPLETED`, `revision` +1. Bước này không thể fail vì state đã được kiểm ở bước 2 và khóa đang giữ.
5. **Ledger**: `RewardLedgerStore` ghi `(characterId, questId) → { eventId, grantedAtUtc, currency, items }` — bằng chứng "đã thưởng", dùng để replay sau này. Ghi trong-memory, **mất sau restart** — ghi rõ, không gọi là durable/exactly-once production (issue #41 yêu cầu nhãn này).

Rollback/failure injection trong self-check: decorator `IInventoryService` fail ở lần Apply đầu → assert quest còn `READY_TO_TURN_IN`, inventory/currency không đổi, ledger rỗng; lần hai (service thật) thành công và thưởng đúng một lần. Thêm test turn-in hai lần (key mới sau COMPLETED) → `invalid_transition` và inventory không tăng thêm; replay cùng key → trả đúng kết quả đầu.

## 5. Quy tắc thưởng

- Currency: cộng dồn `CurrencyDeltas`; amount canonical `>= 0` (schema đã chặn âm); loader chặn amount > `10^9` để tránh overflow khi cộng dồn nhiều quest. Balance 0 bị omit khỏi snapshot (hành vi có sẵn).
- Items: mỗi `itemIds` thành 1 instance mới (`ITM_<hex32>`), `Stack 1`, location `BAG`. **Chưa có item catalog/stack merge** — nếu sau này một quest thưởng cùng template 2 lần sẽ là 2 instance; ghi rõ là hạn chế, QOD-15 trở đi bổ sung stack rules từ runtime definitions.
- XP: `xpRule` canonical là `LEVEL_BAND_BASE` nhưng **chưa có hệ thống XP/level** (`PlayerSession` không có XP) và chưa có công thức XP canonical cho quest → `xp.applied = false`, server không cộng XP. Response vẫn echo `xpRule` để client biết thưởng XP sẽ đến khi hệ thống tồn tại. **Câu hỏi owner:** nên giữ `applied: false` hay tạm cộng vào một trường XP fixture có nhãn? Đề xuất mặc định là giữ `false` (không bịa số).
- Unlocks: `unlocks` chỉ echo trong response; cơ chế `LOCKED → AVAILABLE` hiện có (refresh prerequisite lười khi đọc state) tự mở quest sau khi prerequisite `COMPLETED`. P00-02 chưa có file trong catalog nên không có hành vi thêm.
- Multi-player: thưởng gắn với character của session turn-in; không có cơ chế party/share kill nào trong P1 — không biến kill chung thành quyền nhận vô hạn.

## 6. Thay đổi nội bộ (không wire)

- `QuestDefinition` mở rộng: `TurnInNpcId`, `Rewards` (`IReadOnlyList<QuestRewardCurrency>`, `IReadOnlyList<string> ItemIds`, `XpRule`), `Unlocks`. `QuestCatalogLoader` parse + validate: `turnInNpcId` pattern NPC, reward currency `>= 0` và ≤ `10^9`, `itemIds` pattern item, `xpRule` không rỗng, `unlocks` pattern questId, không tự unlock chính nó. Startup validation: `turnInNpcId` phải có anchor trong `npc_anchors.json` (giống `startNpcId` đang có).
- `QuestTurnInService` + `RewardLedgerStore` + config `P1:QuestTurnIn { Enabled=false, MaxInteractionDistanceWu=5 }`; log `DEV STUB/FIXTURE` khi bật (LOS `not_enforced` khi chưa có bundle REVIEWED — cùng cơ chế accept/interact).
- `IQuestService.TurnIn(actor, questId)` giữ nguyên làm primitive flip state; orchestrator gọi sau khi grant thành công. Không thêm API rollback cho quest store (không cần với thứ tự commit trên).

## 7. Fixture/dev có nhãn

- Gate `P1:QuestTurnIn:Enabled` mặc định OFF; smoke CI bật. Khi bật có log DEV như accept/interact.
- XP `applied: false` — không có số XP nào được bịa.
- Ledger in-memory mất sau restart — đã ghi ở mục 4.
- "Túi đầy" (bag full): P1 inventory chưa có capacity → không có case này; ghi rõ là giới hạn, không gọi production.

## 8. Validator & ví dụ

- Schema mới: `Implementation/Contracts/P1/TurnInRequest.schema.json`, `TurnInResponse.schema.json` + ví dụ `Examples/` (validator `validate_contracts.py` tự nhặt). Ví dụ dùng P00-01 thật.
- Self-check: flow đầy đủ accept (nếu cần) → progress → turn-in → kiểm currency/items/inventory revision/quest revision; replay; conflict; turn-in lần hai bị `invalid_transition`; failure injection rollback; NPC sai/ngoài tầm/LOS blocked (geometry reviewed fixture); level band không liên quan turn-in.
- `smoke_p1.py`: sau mốc nhặt 3 kiện, walk tới gần `NPC_TA_VAN_KHANH` (x=64) → turn-in → GET quests thấy `COMPLETED` → GET inventory thấy COIN 20 + 1 item chest → replay cùng key → kết quả y hệt → key mới → `409 invalid_transition`, inventory không đổi. Workflow bật `P1__QuestTurnIn__Enabled=true`.

## 9. Ngoài phạm vi (ghi rõ)

- Hệ thống XP/level, công thức XP canonical, multi-step reward graph, quest chain thật (P00-02 file), item stack/unique rules, persistence/DB, endpoint grant tùy ý, sửa `reviewState` topology.

## 10. Checklist thực thi

1. PR gồm proposal + schema + ví dụ + code server + tests. Contract delta nằm ở commit đầu để review riêng được.
2. Không sửa `docs/production/`, không sửa file của agent khác, không bật gate production, không sửa state enum wire cũ.
3. Report SHA/lệnh/output lên issue #41 sau khi PR xanh.
