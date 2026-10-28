# QOD-08 — Hợp đồng nhận quest (`QuestAcceptRequest` / `QuestAcceptResponse`)

**Trạng thái:** hợp đồng hoàn chỉnh; endpoint đã implement trong PR #27 và **mặc định tắt** bằng `P1:QuestAccept:Enabled`. NPC anchor registry và level profile đã có, nên các guard 1–7 chạy thật trừ line-of-sight (chưa có walkability bundle — server log `DEV STUB` khi bật). Production chỉ bật flag sau khi có bundle này.
**Issue:** #20. **Canonical IDs:** `P00-01`, `NPC_LYAN`, `GRAPH_P00_01`, `STEP_P00_01_PACKAGES`, `OBJ_P00_01_PACKAGES`, `MAP_BEN_MUA`.

## 1. Phạm vi

Chỉ `AVAILABLE → ACTIVE`. Không turn-in, không reward, không dialogue playback, không tiến độ objective. Input/output theo schema mới trong `Implementation/Contracts/P1/`:

- `QuestAcceptRequest.schema.json` — payload.
- `QuestAcceptResponse.schema.json` — response (kể cả khi bị từ chối sau khi đã resolve session/quest).

## 2. Request

```
POST /p1/quests/accept
Content-Type: application/json
X-Session-ID: <SESSION_ID>
X-Correlation-ID: <tuỳ chọn, echo nếu hợp lệ>
```

Body là `Envelope` hiện hành (không đổi) với payload:

```json
{ "questId": "P00-01", "npcId": "NPC_LYAN" }
```

Payload giữ đúng hai trường đã chốt trong Addendum §2; **không** thêm `expectedQuestRevision` hay `inputSequence`. Xung đột revision do server phát hiện nội bộ (mục 5).

## 3. Thứ tự guard (bắt buộc, đúng Addendum §2)

1. `X-Session-ID` có mặt (thiếu → `400 invalid_payload`); session tồn tại (không có → `404 session_not_found`); `characterId` trong envelope khớp session (không khớp → `400 invalid_payload`).
2. `questId` có trong canonical quest catalog → sai format: `400 invalid_payload`; không có: `404 quest_not_found`.
3. `npcId` bằng `startNpcId` canonical của quest (đọc từ file `QuestDefinition`, không hard-code; loader server cần bổ sung field — mục 7) → sai: `422 npc_mismatch`.
4. Actor và NPC cùng `mapId` và cùng `floorId`. P1 chỉ có floor `OVERWORLD` theo DEC-016; không có floor link.
5. Khoảng cách đo từ chân ≤ **5 WU** (DEC-016 §3) và đường tương tác không bị tường/polygon blocked chắn → sai: `422 out_of_range`.
6. Prerequisites đã `COMPLETED` và level trong `levelBand` của quest → sai: `422 prerequisite_not_met`.
7. State hiện tại là `AVAILABLE` → sai: `409 invalid_transition`.

Guard 4–6 cần dữ liệu server chưa có (NPC registry có toạ độ/floor, level profile, walkable/blocked polygons). Vì vậy endpoint **không được** map khi thiếu các guard này; xem mục 7.

## 4. Thành công

`AVAILABLE → ACTIVE`, `stepId` = `InitialStepId`, quest `revision` tăng **đúng một lần**, `objectiveCounters` giữ nguyên (0 cho `P00-01`). Không đổi `WorldSnapshot.revision`, HP/MP, vị trí; không cấp thưởng; không tiêu `inputSequence` của movement/combat.

```json
{
  "schemaVersion": 1,
  "requestId": "66666666666666666666666666666666",
  "sessionId": "0123456789abcdef0123456789abcdef",
  "serverTimeUtc": "2026-10-28T07:00:00Z",
  "result": {
    "questId": "P00-01",
    "state": "ACTIVE",
    "stepId": "STEP_P00_01_PACKAGES",
    "objectiveCounters": { "OBJ_P00_01_PACKAGES": 0 },
    "revision": 2
  }
}
```

## 5. Lỗi và response schema

`result` luôn chứa `QuestState` hiện hành khi session và quest đã resolve — kể cả khi bị từ chối — nên client không cần đọc state từ field không định nghĩa. Request hỏng trước bước resolve (sai envelope, thiếu session) không có `sessionId` lẫn `result`.

| HTTP | `error.code` | Nguyên nhân | `retryable` |
|---|---|---|---|
| 400 | `invalid_payload` | Envelope/payload sai shape, thiếu `X-Session-ID`, `characterId` không khớp | false |
| 413 | `invalid_payload` | Body > 8 KB (giữ hành vi của `/p1/move` và `/p1/combat`) | false |
| 404 | `session_not_found` | Session không tồn tại | false |
| 404 | `quest_not_found` | `questId` không có trong catalog | false |
| 422 | `npc_mismatch` | `npcId` ≠ `startNpcId` | false |
| 422 | `out_of_range` | Khác map/floor hoặc khoảng cách > 5 WU hoặc đường bị chắn | true |
| 422 | `prerequisite_not_met` | Prerequisite chưa xong hoặc level ngoài band | false |
| 409 | `invalid_transition` | State không phải `AVAILABLE` | false |
| 409 | `revision_conflict` | Quest state đổi giữa lúc đọc guard và lúc commit (double accept đồng thời) | true |
| 409 | `idempotency_conflict` | Cùng `idempotencyKey` nhưng payload khác | false |

Mapping nội bộ cần giữ khi implement: service trả `unknown_quest` khi ID không có trong catalog và `quest_not_found` khi thiếu state row; HTTP map **cả hai** về `404 quest_not_found` để client chỉ thấy một mã cho "quest không dùng được". Riêng `LOCKED` (thiếu prerequisite) phải map thành `422 prerequisite_not_met` ở guard 6, **không** dùng `invalid_transition`; chỉ `ACTIVE`/`READY_TO_TURN_IN`/`COMPLETED`/`FAILED` mới là `409 invalid_transition`.

Ví dụ từ chối sau resolve (state nằm trong `result`, không nằm trong `error.data`):

```json
{
  "schemaVersion": 1,
  "requestId": "66666666666666666666666666666666",
  "sessionId": "0123456789abcdef0123456789abcdef",
  "serverTimeUtc": "2026-10-28T07:00:01Z",
  "result": {
    "questId": "P00-01",
    "state": "LOCKED",
    "stepId": "STEP_P00_01_PACKAGES",
    "objectiveCounters": { "OBJ_P00_01_PACKAGES": 0 },
    "revision": 1
  },
  "error": {
    "code": "prerequisite_not_met",
    "messageKey": "P1.ERROR.PREREQUISITE_NOT_MET",
    "retryable": false,
    "fieldErrors": [],
    "correlationId": "demo-accept"
  }
}
```

## 6. Idempotency

- Scope: `actor + operation("quest_accept") + idempotencyKey`; lưu request hash và response gốc.
- Retry cùng key + cùng payload → trả lại kết quả đầu tiên, không chạy lại transition.
- Cùng key + payload khác → `409 idempotency_conflict`.
- Accept **không** dùng `inputSequence` thay dedupe; sequence của movement/combat không bị tiêu.
- Double-tap hợp lệ về dữ liệu: nếu không trùng key, lần hai rơi vào `409 invalid_transition` (hoặc `revision_conflict` khi đua), state không tăng revision lần hai.

## 7. Feature flag và điều kiện mở endpoint

Endpoint giữ **off** cho tới khi server có đủ:

1. NPC world registry: `npcId → mapId, floorId, x, y` lấy từ manifest canonical (hiện chỉ có CSV trong `docs/production/`, chưa load vào server).
2. `startNpcId` trong `QuestDefinition` server: `QuestCatalogLoader` hiện chỉ đọc `questId`, `questType`, `levelBand`, prerequisites, objectives và `initialStepId`; chưa mang `startNpcId`/`turnInNpcId` dù file content có. Guard 3 chưa thể chạy nếu thiếu field này.
3. Level profile trong `PlayerSession` (hiện không có trường level); `levelBand` thì `QuestDefinition` đã có (`MinLevel`/`MaxLevel`).
4. Floor/walkability contract: `floorId`, walkable/blocked polygons, floor links (DEC-016 yêu cầu bundle v2; P1 chỉ có `OVERWORLD`).

Cho phép dev stub có flag (ví dụ `P1:QuestAccept:Enabled=true`) chỉ khi log rõ `DEV STUB: proximity/level guards disabled`, không map endpoint khi flag off (client nhận 404 như endpoint chưa tồn tại), và không tuyên bố P1 đạt gate vì stub này.

## 8. Điều kiện nghiệm thu (PR implementation sau này)

- Happy path: `P00-01` `AVAILABLE → ACTIVE`, `result.revision +1`; `GET /p1/quests/{sessionId}` đọc lại thấy `ACTIVE`; `GET /p1/world/{sessionId}` có `revision`, `x`, `y`, `mp` không đổi.
- `npcId = NPC_TA_VAN_KHANH` → `422 npc_mismatch`.
- Đứng ngoài 5 WU (khi registry có) → `422 out_of_range`, `retryable: true`.
- Quest prerequisite chưa xong / level ngoài band → `422 prerequisite_not_met`.
- Accept lần hai (key mới) → `409 invalid_transition`, `revision` không tăng thêm.
- Retry cùng key+payload → cùng body như lần đầu; cùng key khác payload → `409 idempotency_conflict`.
- Session lạ → `404 session_not_found`; quest không tồn tại → `404 quest_not_found`.
- Flag off → endpoint không map; bật flag trong dev vẫn phải log stub rõ ràng.
- Mọi response có `X-Correlation-ID`.

## 9. Ngoài phạm vi

Turn-in/reward (Addendum §2 nửa sau), objective event ingestion có `sourceEventId`, party progress, dialogue state, UI states (`SUBMITTING`/`STALE`) — client dùng schema này nhưng không được tự chế state.
