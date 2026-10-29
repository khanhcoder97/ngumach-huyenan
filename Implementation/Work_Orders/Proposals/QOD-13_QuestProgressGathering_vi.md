# QOD-13 — Quest progress server-owned, tương tác world và thu thập (proposal)

Phạm vi: mốc QOD-13 của `06_QODER_GAMEPLAY_LOOP_EPIC.md` (issue #41). Tài liệu này là contract delta trước code; chỉ implement sau khi proposal được review. Không sửa wire cũ (QuestState/CombatEvent/Envelope) — chỉ thêm message mới.

## 1. Mục tiêu

1. Hoàn thiện vòng `AVAILABLE → ACTIVE → (objective progress) → READY_TO_TURN_IN → COMPLETED` bằng **event do server xác minh** — client không gửi counter/amount.
2. P00-01 "Thư qua bến" là acceptance slice: nhận quest từ NPC_LYAN (đã có endpoint accept), nhặt 3 kiện `OBJ_BM_PACKAGE_01/02/03`, về trạng thái READY_TO_TURN_IN. Turn-in thuộc QOD-14.
3. Gathering node: kiểm available/range/LOS, claim theo **shard riêng từng người chơi** (canonical), respawn theo giờ server, không tạo vật phẩm hai lần nhờ idempotency.
4. Bảng mapping objective → event → recordId rõ ràng, startup validation bắt ID treo (dangling).

## 2. Nguồn canonical tham chiếu

| Dữ liệu | Nguồn |
|---|---|
| P00-01: nhặt 3 kiện tại x=36/44/52, giao NPC_TA_VAN_KHANH, "kiện respawn" | `docs/production/Quest_and_Narrative_Production_Spec_vi.md` bảng P00-01 |
| OBJ_BM_PACKAGE_01/02/03 tại (36,0)/(44,0)/(52,0) | `docs/production/Map_Production_Atlas_vi.md` mục "Tương tác/trigger nhiệm vụ" |
| Khoảng tương tác ≤ 5 WU đo từ chân, cùng tầng, LOS không bị tường chặn | `docs/production/Top_Down_Gameplay_World_Spec_vi.md` dòng 30 |
| Node nghề: `gather_item_id`, yield 1–2 / 2–3, `profession_level_required` 1/4, tool, "Hồi riêng theo người chơi sau 60/120s", "Node riêng theo shard", design_state `NEW_PROPOSED` | `docs/production/World_Spawn_Gathering_Manifest_vi.csv` dòng MAN-BM-NODE_* |
| Item quest nằm trong quest pouch, không chiếm túi | `Quest_and_Narrative_Production_Spec_vi.md` §5 |

Ghi chú trung thực: 5 node nghề Bến Mưa có `design_state = NEW_PROPOSED` (chưa được review vị trí). P1 vẫn import vị trí manifest nhưng **gate gathering mặc định OFF**, chỉ bật trong scenario fixture có nhãn — không coi đó là vị trí đã duyệt.

## 3. Bảng mapping objective → event → recordId

| Objective type (quest def) | Event type (server-owned) | Nguồn recordId | Quy tắc cộng tiến độ | Trạng thái P1 |
|---|---|---|---|---|
| `COLLECT` | `INTERACT_CLAIM` (quest object) hoặc `GATHER_CLAIM` (node nghề) | `targetIds` của objective, khớp `mapId` | mỗi **recordId** đóng góp tối đa 1 lần | ✅ implement |
| `INTERACT` | `INTERACT_CLAIM` | `targetIds`, khớp `mapId` | mỗi recordId tối đa 1 lần | ✅ mapping sẵn; chưa có quest dùng |
| `TALK` | `TALK` (dialogue endpoint tương lai) | `targetIds` là NPC id | mỗi recordId tối đa 1 lần | ❌ unsupported; startup validation kiểm targetIds là NPC có anchor |
| `KILL` | `KILL` (sát thương server xác nhận) | `targetIds` | mỗi **event** +1 (cùng record có thể giết nhiều lần) | ❌ chờ damage subset (QOD-12 để lại) |
| `ESCORT`, `BOSS` | — | — | — | ❌ unsupported |

Quy tắc chung:

- **Chỉ event đã kiểm chứng mới tạo tiến độ**: service tương tác xác minh entity tồn tại, claim thành công, cùng map/floor, khoảng cách ≤ 5 WU, LOS không bị chặn (bundle chưa REVIEWED → không enforce, giống accept). Không có đường client gửi counter.
- **Mỗi event chỉ đóng góp một lần** (idempotency của chính request claim; replay trả kết quả cũ, không cộng lại).
- COLLECT/INTERACT/TALK dùng **distinct-record**: nhặt lại cùng kiện sau respawn không cộng lần 2 — với P00-01 điều này khớp narrative "nhặt 3 kiện ở 3 chỗ".
- Tiến độ tăng → `revision` của quest tăng; đủ tất cả objective → `READY_TO_TURN_IN`. Không thêm state mới vào wire `QuestState` (đã có đủ 6 state).
- Tiến độ hiển thị qua `objectiveCounters` có sẵn trong `QuestState`; readback qua `GET /p1/quests/{sessionId}` không đổi.

Startup validation (bắt dangling IDs, fail khi boot):

- Objective `COLLECT`/`INTERACT`: mỗi `targetId` phải resolve trong **world record catalog** (mục 6) và `mapId` của record phải khớp objective.
- Objective `TALK`: mỗi `targetId` phải là NPC có anchor trong `npc_anchors.json`.
- Objective `KILL`/`ESCORT`/`BOSS`: chỉ kiểm format (chưa resolve vì chưa có source sát thương).

## 4. Contract delta — `POST /p1/world/interact`

Endpoint mới, gate `P1:Interact:Enabled` (mặc định **false**; smoke CI bật như QuestAccept). Không đổi endpoint/schema cũ.

### 4.1 Request

Envelope giữ nguyên shape `Envelope.schema.json`; payload là `InteractIntent`:

```json
{
  "schemaVersion": 1,
  "requestId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "idempotencyKey": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "sentAtUtc": "2026-10-29T00:00:00Z",
  "characterId": "CHR_DEMO_01",
  "payload": { "targetId": "ENT_MAN_BM_OBJ_BM_PACKAGE_01" }
}
```

- `targetId`: entity instance id, pattern `^ENT_[A-Z0-9_]+$`. Chỉ nhận target loại `INTERACTABLE` hoặc `GATHER_NODE`.
- Session qua header `X-Session-ID` như accept/combat.
- Idempotency: scope `(characterId, idempotencyKey)`; replay trả đúng outcome đầu (kể cả questUpdates snapshot), payload khác cùng key → `idempotency_conflict` (409).

### 4.2 Response thành công

`P1InteractResponse.result`:

| Field | Ý nghĩa |
|---|---|
| `interactionId` | hex32, id event server-generated (dùng để dedupe KILL sau này) |
| `targetId` / `recordId` / `kind` | entity đã tương tác |
| `outcome` | enum `collected` (quest object) \| `gathered` (node nghề) |
| `targetState` | state sau claim: `DEPLETED` (object chung) hoặc `AVAILABLE` (node shard — state registry không đổi) |
| `claimedAtUtc` / `respawnAtUtc` | `respawnAtUtc` null khi `respawnSeconds = 0`; với node shard là thời điểm riêng cho character đó |
| `yield` | `{ "itemId": "MAT-ORE-01", "quantity": 2 }` — chỉ với `gathered` |
| `questUpdates` | mảng `QuestState` đầy đủ của các quest có revision thay đổi (thường rỗng hoặc 1 phần tử) |

Ví dụ (nhặt kiện, có tiến độ):

```json
{
  "schemaVersion": 1,
  "requestId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "sessionId": "0123456789abcdef0123456789abcdef",
  "serverTimeUtc": "2026-10-29T00:00:01Z",
  "result": {
    "interactionId": "cccccccccccccccccccccccccccccccc",
    "targetId": "ENT_MAN_BM_OBJ_BM_PACKAGE_01",
    "recordId": "MAN-BM-OBJ_BM_PACKAGE_01",
    "kind": "INTERACTABLE",
    "outcome": "collected",
    "targetState": "DEPLETED",
    "claimedAtUtc": "2026-10-29T00:00:01Z",
    "respawnAtUtc": "2026-10-29T00:00:21Z",
    "questUpdates": [
      {
        "questId": "P00-01",
        "state": "ACTIVE",
        "stepId": "STEP_P00_01_PACKAGES",
        "objectiveCounters": { "OBJ_P00_01_PACKAGES": 1 },
        "revision": 3
      }
    ]
  }
}
```

### 4.3 Error codes

| Code | HTTP | Khi nào |
|---|---|---|
| `invalid_payload` | 400 | body/envelope/X-Session-ID sai |
| `session_not_found` | 404 | session không tồn tại |
| `target_not_found` | 404 | targetId không có trong registry |
| `invalid_target` | 400 | kind không tương tác được (NPC/MOB/BOSS) |
| `out_of_range` | 422 | khác map/floor, khoảng cách > 5 WU, hoặc LOS bị chặn (retryable) |
| `target_not_available` | 409 | object đã DEPLETED / node shard đang cooldown cho character này |
| `profession_level_insufficient` | 422 | `profession_level_required` > level nghề giả định của fixture (mục 7) |
| `idempotency_conflict` | 409 | cùng key, payload khác |

Code mới chỉ nằm trong `InteractionErrorCodes` (server) + enum `error.code` của `InteractResponse.schema.json` — không thêm vào error enum của accept/combat.

## 5. Claim models

| Loại target | Claim | Respawn |
|---|---|---|
| `INTERACTABLE` policy `SHARED` | registry **chung**: `Despawn` → `DEPLETED` (hiện trong `GET /p1/world`), revision entity tăng | `respawnSeconds` qua tick host; respawn thật khi hết giờ |
| `INTERACTABLE` policy `PER_CHARACTER` (3 kiện P00-01) | **shard riêng từng character** theo `Production_Rules_Complete_v1_vi.md` §5 ("mỗi ID tính tối đa 1/character", "không trừ item world cho người khác"): claim store `(characterId, entityId)`; registry chung **giữ `AVAILABLE`**, character khác claim ngay được, không chờ respawn toàn cục | cùng `respawnSeconds` của entity nhưng tính riêng từng người chơi, lazy theo `UtcNow`; 20s là DEV fixture |
| `GATHER_NODE` | **shard riêng từng character** (canonical "Hồi riêng theo người chơi", "Node riêng theo shard"): claim store `(characterId, entityId)` ghi `claimedAtUtc`; character khác vẫn claim được | cùng `respawnSeconds` của entity nhưng tính riêng từng người chơi, lazy theo `UtcNow` (không cần tick) |

- Policy ghi trong data: `world_entities_bm.json` mỗi entity claimable có `claimPolicy` (`SHARED`/`PER_CHARACTER`) do `build_world_entities.py` sinh; loader `WorldEntityLoader` validate (gather node luôn `PER_CHARACTER`, kind không claimable không được khai policy).
- Claim chỉ xảy ra khi toàn bộ guard pass; request fail **không** tiêu claim (giống "rejection không tiêu sequence" của move/combat).
- Disconnect/cancel: không có endpoint hủy; claim là atomic tại thời điểm request thành công, nên không thể tạo vật phẩm hai lần — replay idempotency trả kết quả cũ, request mới khi claim đã bị tiêu → `target_not_available`.
- Vật phẩm quest (kiện) **không** ghi vào inventory — tiến độ nằm trong `objectiveCounters` (tương đương quest pouch ở P1; hạn chế được ghi rõ).
- Dedupe tiến độ theo `Production_Rules` §5: `COLLECT event unique(actor, quest, objective, packageId)` — state đã per character+quest, key contribution thêm `objectiveId` (`R:{objectiveId}:{recordId}`, KILL `E:{objectiveId}:{eventId}`) để hai objective hợp lệ cùng record không nuốt tiến triển của nhau.

## 6. Content mới

### 6.1 `Implementation/Content/Runtime/world_records.json` (mới)

Tool mới `Implementation/Tools/build_world_records.py` sinh từ `World_Spawn_Gathering_Manifest_vi.csv` (toàn bộ 349 dòng: `recordId, mapId, xWu, yWu, recordType, designState, entityId, respawnSeconds, respawnPolicy, condition`) + phần bổ sung nguồn Atlas (supplements):

| recordId | mapId | x | y | recordType | ghi chú |
|---|---|---|---|---|---|
| MAN-BM-OBJ_BM_PACKAGE_01 | MAP_BEN_MUA | 36 | 0 | INTERACTABLE | Atlas "Tương tác/trigger nhiệm vụ" |
| MAN-BM-OBJ_BM_PACKAGE_02 | MAP_BEN_MUA | 44 | 0 | INTERACTABLE | nt |
| MAN-BM-OBJ_BM_PACKAGE_03 | MAP_BEN_MUA | 52 | 0 | INTERACTABLE | nt |

Riêng node nghề, generator chép thêm cột `gatherProfession, gatherItemId, yieldMin, yieldMax, professionLevelRequired, toolId` (canonical, không phát minh). Server nạp bằng `WorldRecordCatalog`/`WorldRecordLoader` với validation fail-fast (map bounds, kiểu record, ID pattern, không trùng recordId).

### 6.2 `world_entities_bm.json` +27 entity

`build_world_entities.py` nhận danh sách supplement Atlas-sourced (3 kiện: kind `INTERACTABLE`, templateIds `OBJ_BM_PACKAGE_0X`, floor OVERWORLD, quantity 1, `respawnSeconds` fixture 20, `claimPolicy` `PER_CHARACTER` + `claimPolicySource` Production Rules §5). File sinh lại: 24 → **27 entity** (self-check `world.registry` cập nhật). Package không nằm trong manifest CSV nên không phát sinh template giả trong CSV.

## 7. Fixture/dev có nhãn

- `respawnSeconds: 20` cho 3 kiện: canonical chỉ nói "kiện respawn" không có số → giá trị fixture, ghi `sourceRef`/nhãn `DEV FIXTURE` trong content, không gọi là canonical.
- Level nghề: P1 chưa có hệ nghề → config `P1:Interact:AssumedProfessionLevel` (mặc định 1, nhãn DEV) dùng để so với `profession_level_required` canonical của node. Node tier II (level 4) sẽ trả `profession_level_insufficient`.
- Yield roll: canonical là khoảng 1–2 / 2–3. Roll qua interface `IYieldRoller` (production `System.Random`; self-check inject roller cố định) — không đổi khoảng, không ép yield min.
- Gate: `P1:Interact { Enabled=false, MaxInteractionDistanceWu=5, AssumedProfessionLevel=1 }`. Khi bật có log `DEV STUB/FIXTURE` như QuestAccept/MobBehavior.
- LOS: dùng chung `IWorldGeometryService`; bundle `SYNTHETIC_TEST_ONLY` → `not_enforced` (cho qua), `REVIEWED` → enforce. Không đổi reviewState để demo chạy.
- Item grant vào inventory qua `IInventoryService.Apply` (internal, không endpoint mới): mỗi claim tạo instance `MAT-*` ở location BAG. **Stack/unique rules và item catalog chưa có** → mỗi lần nhặt là một instance; QOD-14 bổ sung quy tắc stack từ runtime definitions (ghi rõ là hạn chế, không gọi production).

## 8. Tick host (respawn thật khi server chạy)

Thêm `WorldTickBackgroundService : BackgroundService`: mỗi 50 ms (chu kỳ 20 Hz theo `ServerClock.TicksPerSecond`) gọi `WorldEntityRegistry.Update()` (respawn object chung đã DEPLETED) và — khi `P1:MobBehavior:Enabled` — `MobLifecycleService.Tick(sessions)` với danh sách session (`ISessionStore` bổ sung `All`). Trước QOD-13, respawn chỉ chạy trong self-check; đây là mảnh "tick loop nền" còn thiếu của QOD-12. Claim shard lazy, không cần tick.

## 9. Thay đổi service domain (không wire)

- `IQuestService`: bỏ `RecordObjective(actor, questId, objectiveId, amount)` (client-trusted counter, chưa từng expose) → thay bằng `RecordVerifiedEvent(PlayerSession actor, string eventId, string eventType, string recordId, string mapId)` trả `IReadOnlyList<QuestState>` các quest đổi revision. Dùng `IServerClock` thay `ServerClock` concrete để test deterministic.
- `PlayerQuestState`: thêm set `Contributions` (key `R:{recordId}` cho distinct-record, `E:{eventId}` cho kill) — internal, không vào wire.
- `IInteractionService` mới (`InMemoryInteractionService`): guard thứ tự idempotency → target tồn tại → kind → map/floor → khoảng cách → LOS → claim → yield/inventory → quest progress.

## 10. Validator & ví dụ

- Schema mới: `Implementation/Contracts/P1/InteractRequest.schema.json`, `InteractResponse.schema.json` + ví dụ trong `Examples/` (validator `validate_contracts.py` tự nhặt `*.schema.json` — không sửa file của agent khác). Ví dụ dùng recordId/entityId thật; không đặt ID mới vào cột entity_id của manifest.
- `build_world_records.py` tự kiểm đầu ra (trùng ID, bounds, kiểu) và được gọi trong `content-validation.yml`; `validate_content.py` không đổi.
- Self-check mở rộng: progress distinct-record, claim/respawn chung (ManualServerClock), shard 2 character, cooldown shard, profession gate, yield grant không double, idempotency replay/conflict, LOS blocked, ngoài tầm, invalid target, quest đạt READY_TO_TURN_IN sau 3 kiện.
- `smoke_p1.py`: bật `P1__Interact__Enabled` trong workflow; nhặt 3 kiện → GET quests thấy 3/3 READY_TO_TURN_IN → nhặt lại kiện thứ nhất → 409 target_not_available; gather node → GET inventory thấy MAT-*.

## 11. Ngoài phạm vi (ghi rõ)

- Turn-in endpoint + thưởng (QOD-14), damage/KILL event, dialogue endpoint (TALK), hệ nghề thật (level nghề từng character), item stack/unique rules, endpoint grant tùy ý cho public client, sửa `reviewState`.

## 12. Checklist thực thi

1. PR này gồm proposal + schema + ví dụ + content (records, 3 kiện) + code server + tests. Contract delta nằm ở commit đầu để review riêng được.
2. Không sửa `docs/production/`, không sửa file của agent khác, không bật gate production, không sửa state enum wire cũ.
3. Report SHA/lệnh/output lên issue #41 sau khi PR xanh.
