# QOD-08 — Đề xuất hợp đồng nhận quest (`QuestAcceptRequest`)

**Trạng thái:** ĐỀ XUẤT, chờ OpenCode và content owner duyệt. Chưa implement endpoint; server vẫn chỉ có `GET /p1/quests/{sessionId}` (QOD-07).
**Người đề xuất:** Qoder. **Issue:** #20. **Canonical IDs:** `P00-01`, `NPC_LYAN`, `GRAPH_P00_01`, `STEP_P00_01_PACKAGES`, `OBJ_P00_01_PACKAGES`.

## 1. Mục tiêu

Cho client một đường duy nhất để chuyển quest từ `AVAILABLE` sang `ACTIVE` theo đúng narrative graph canonical (`Quest_Dialogue_Production_Data_vi.csv`: node `OFFER` ở `NPC_LYAN`, điều kiện `QUEST_AVAILABLE`, action `ACCEPT_QUEST`). Server giữ toàn quyền quyết định; client chỉ khai báo ý định.

Ngoài phạm vi: nộp quest (`turn-in`), thưởng (currency/item/XP), dialogue playback, kiểm tra khoảng cách tới NPC.

## 2. Payload

Schema mới: `Implementation/Contracts/P1/QuestAcceptRequest.schema.json` (đã thêm kèm example, `contract-validation` kiểm tra tham chiếu).

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ngumach.local/contracts/p1/QuestAcceptRequest.schema.json",
  "title": "P1 quest accept request payload",
  "type": "object",
  "additionalProperties": false,
  "required": ["questId", "npcId"],
  "properties": {
    "questId": { "type": "string", "pattern": "^[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]{2}$" },
    "npcId": { "type": "string", "pattern": "^NPC_[A-Z0-9_]+$" }
  }
}
```

`npcId` bắt buộc ngay từ đầu dù P1 chưa dùng để kiểm tra vị trí: nó chốt rằng quest accept luôn gắn với NPC canonical, để sau này server thêm rule khoảng cách/khu vực mà **không phải đổi hợp đồng**.

## 3. Cách gọi

```
POST /p1/quests/accept
Content-Type: application/json
X-Session-ID: <SESSION_ID>
X-Correlation-ID: <tuỳ chọn, được echo nếu hợp lệ>
```

Body là `Envelope` hiện có (`schemaVersion`, `requestId`, `idempotencyKey`, `sentAtUtc`, `characterId`, `payload`), payload theo mục 2:

```json
{
  "schemaVersion": 1,
  "requestId": "66666666666666666666666666666666",
  "idempotencyKey": "77777777777777777777777777777777",
  "sentAtUtc": "2026-10-28T07:00:00Z",
  "characterId": "CHR_MINH_KIEM_01",
  "payload": { "questId": "P00-01", "npcId": "NPC_LYAN" }
}
```

Phương án `POST /p1/quests/{sessionId}/accept` đã cân nhắc và bỏ: mọi command trong P1 (`/p1/move`, `/p1/combat`) đều mang session qua `X-Session-ID`, chỉ endpoint đọc mới đặt session trên path.

## 4. Quy tắc server

Thứ tự kiểm tra và mã lỗi (dùng lại code đã có, **không thêm code mới**):

| Kết quả | HTTP | `error.code` | `fieldErrors` | Ghi chú |
|---|---|---|---|---|
| Envelope/payload sai shape, thiếu `X-Session-ID` | 400 | `invalid_payload` | `schemaVersion`, `requestId`, `idempotencyKey`, `sentAtUtc`, `characterId`, `payload.questId`, `payload.npcId`, `X-Session-ID` |body quá 8 KB → 413 |
| `characterId` không khớp session | 400 | `invalid_payload` | `characterId` | |
| Session không tồn tại | 404 | `session_not_found` | `X-Session-ID` | |
| `questId` hợp lệ về format nhưng không có trong canonical catalog | 404 | `unknown_quest` | `questId` | |
| `npcId` ≠ `startNpcId` canonical của quest | 400 | `invalid_payload` | `payload.npcId` | Server đọc `QuestDefinition`, không hard-code |
| State không phải `AVAILABLE` (LOCKED, ACTIVE, READY_TO_TURN_IN, COMPLETED, FAILED) | 409 | `invalid_transition` | `state` | Kèm `QuestState` hiện tại để client đồng bộ lại |

Thành công (`AVAILABLE → ACTIVE`) trả `200`:

```json
{
  "schemaVersion": 1,
  "requestId": "66666666666666666666666666666666",
  "sessionId": "<SESSION_ID>",
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

Bị từ chối vẫn trả state hiện hành trong `result`, song song với `error`:

```json
{
  "schemaVersion": 1,
  "requestId": "66666666666666666666666666666666",
  "sessionId": "<SESSION_ID>",
  "serverTimeUtc": "2026-10-28T07:00:01Z",
  "result": { "questId": "P00-01", "state": "LOCKED", "stepId": "STEP_P00_01_PACKAGES", "objectiveCounters": { "OBJ_P00_01_PACKAGES": 0 }, "revision": 1 },
  "error": {
    "code": "invalid_transition",
    "messageKey": "P1.ERROR.INVALID_TRANSITION",
    "retryable": false,
    "fieldErrors": ["state"],
    "correlationId": "demo-accept"
  }
}
```

Wrapper là envelope P1 quen thuộc (`schemaVersion`, `requestId`, `sessionId`, `serverTimeUtc`, `result`, `error`), khác chỗ **không có** trường `revision` cấp cao nhất: accept không đụng `WorldSnapshot`.

## 5. Bất biến client phải tuân theo

1. **Accept không tiêu `inputSequence`.** Counter monotonic vẫn chỉ dành cho `/p1/move` và `/p1/combat`. Accept không tăng `WorldSnapshot.revision`, không đổi vị trí, HP hay MP.
2. `revision` trong `result` là aggregate revision của *quest state*, không phải của world.
3. Nhận quest **không** cấp thưởng. `objectiveCounters` bắt đầu ở `0`; mọi tiến độ do sự kiện server sinh ra, client không được tự gửi counter.
4. Double-tap accept là vô hại về mặt dữ liệu: lần thứ hai rơi vào `409 invalid_transition`. `idempotencyKey` vẫn bắt buộc theo `Envelope` nhưng P1 **chưa** suy ra bản ghi idempotency — chỉ khi có turn-in/reward (thao tác kinh tế) mới cần dedupe thật.
5. Client chỉ được phép gửi accept cho quest đang `AVAILABLE` trong `GET /p1/quests/{sessionId}` vừa đọc; không được suy diễn từ dialogue local.

## 6. Điều kiện nghiệm thu (cho PR implementation)

- `POST /p1/quests/accept` trả `200` với `P00-01` `AVAILABLE → ACTIVE`, `result.revision` tăng 1; `GET /p1/quests/{sessionId}` đọc lại thấy `ACTIVE`.
- `GET /p1/world/{sessionId}` trước và sau accept có `revision`, `x`, `y`, `mp` **không đổi**.
- Gửi `npcId = NPC_TA_VAN_KHANH` cho `P00-01` → `400 invalid_payload` với `payload.npcId`.
- Accept lần hai → `409 invalid_transition`, state vẫn `ACTIVE`, `revision` không tăng thêm.
- Session lạ → `404 session_not_found`; quest `P99-99` → `404 unknown_quest`.
- `--self-check` thêm assertion cho luồng accept; `smoke_p1.py` phủ đủ các nhánh trên; mọi response có `X-Correlation-ID`.

## 7. Câu hỏi mở

1. OpenCode: format path `POST /p1/quests/accept` (header session) có ổn cho UI dialogue hiện tại không?
2. Content owner: `P00-01` chấp nhận cho accept khi nhân vật chưa tới `x=42` của `NPC_LYAN` (P1 bỏ qua khoảng cách), hay bắt buộc phải có rule vị trí ngay từ endpoint đầu tiên?
3. Owner: turn-in + reward sẽ cần request contract riêng (`expectedQuestRevision`, idempotency record) — tách thành QOD-09 sau khi accept ổn định?
