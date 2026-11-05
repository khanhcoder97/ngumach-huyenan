# Packet hợp đồng Death-Return (QOD-21 Q4) — **ĐÃ DUYỆT: DEC-DEATH-RETURN-20261105** (#87, 2026-11-04T20:57:58Z; nguồn máy đọc `Implementation/Content/DesignBaselines/death_return_decisions_20261105.json` — file đó do nhán integration tạo và **chưa có trong nhán này**, nên packet trích nội dung đã đăng trên #87; không copy file content sang để tránh xứng độ baseline khi owner merge)

Sáu câu hỏi §5 đã có trả lời và được implement theo đúng quyết định, không hỏi lại:

- **Q1 = option 2**: `PlayerLifeLedger` (internal, không thêm `CombatEventV2` type/field). `lifeVersion` bắt đầu 1; `deathEventId = PDEATH_ + sha256 lowercase của canonical JSON `[characterId, lifeVersion, deathRevision]`; một transition dương→0 sinh đúng một record; mọi đường damage (mob, boss encounter, training wave) commit qua cùng một lock/revision; mỗi lần 0→dương đã commit nâng lifeVersion đúng một lần, replay không nâng; state theo character, không theo session nên sống qua reconnect.
- **Q2**: replay trả 200 kèm đúng snapshot đã commit (`applied: false`, `replayed: true`), không hồi/không dịch chuyển/không gia hạn cooldown; thứ tự là validate request+owner → receipt lookup → committed replay → rồi mới `not_downed`/cooldown; key mới khi đang sống vẫn là 409 `not_downed`.
- **Q3**: cooldown 3 s = 60 tick @20 Hz, tính từ tick apply thành công; từ chối/replay không kéo dài; 422 `death_return_cooldown`, `retryable: true`, và `nextReturnAllowedAtTick` được đóng băng vị trí trong schema (`result.nextReturnAllowedAtTick` luôn có, `error.nextReturnAllowedAtTick` mang deadline cho chính lỗi 422 này).
- **Q4**: đúng hai gate — route chỉ map khi `P1:AlphaProfile:Enabled` **và** `P1:DeathReturn:Enabled`; OFF thì 404 vì không có route; `AlphaProfile` on + `RestoreHpFixture > 0` là startup failure; `hp = max(1, ceil(effectiveMaxHp*0.5))`, MP giữ absolute rồi clamp, anchor `[18,0]` đọc từ design (không mượn `P1World`), ba penalty bằng 0.
- **Q5**: **không** chặn return khi actor đang có encounter ACTIVE; không reset boss, không ảnh hưởng owner khác, không grant/abandon/re-register, `attemptId` giữ nguyên, vẫn chạy các quy tắc wipe/no-target owner-scoped sẵn có, và không teleport vào arena.
- **Q6**: client dùng HP authoritative `<= 0`; không thêm field `downed` vào world đã đóng băng.

Phần còn lại của packet (§1, §2, §3) là contract đã được duyệt và giờ là spec của `DeathReturnRequest`/`DeathReturnResponse` + handler.

Gửi Codex (review) + owner (#87) + Antigravity #85 / Muse #1 (client).
Nguồn duy nhất: `DESIGN-BM-ALPHA-20261103` (`Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json`), nhánh `deathReturn`. Packet này **không** áp dụng schema nào và **không** map route nào; handler chỉ land sau khi owner trả lời đủ §5.

Trạng thái server hôm nay (đã có, không phải đề xuất): `Server/Health/Gameplay/Combat/DeathReturn.cs` là máy domain Q-B3 — chỉ trả actor đang `Hp <= 0`, chỉ tới anchor server tự sở hữu, đóng guard window + cancel cast/counter đang chờ, ledger idempotency 256 entry, chạy sau gate `P1:DeathReturn:Enabled` (mặc định **OFF**, `appsettings.json:57-60`) và **không có route HTTP**. Restore HP hiện là `P1:DeathReturn:RestoreHpFixture` (DEV FIXTURE, `0` = không hồi). `ITeleportService` cũng không có route. Không có "generic client teleport" ở bất kỳ đâu.

## 1. `design.deathReturn` nói gì (verbatim, không tự ý thêm)

```json
{
  "mapId": "MAP_BEN_MUA",
  "safeAnchorWu": [18, 0],
  "anchorSource": "existing P1World SpawnX18/SpawnY0 in appsettings; new alpha safe-return approval",
  "route": "POST /p1/actor/death-return",
  "schemaVersion": 1,
  "payload": "empty intent only, never client-supplied coordinates",
  "aliveNewRequest": "reject not_downed; matched committed replay returns same result",
  "restoreHp": "max(1,ceil(currentEffectiveMaxHp*0.5))",
  "restoreMp": "keep current absolute then clamp to effective maxMp",
  "xpPenalty": 0, "currencyPenalty": 0, "durabilityPenalty": 0,
  "newDeathReturnCooldownSeconds": 3,
  "clear": ["inflight casts", "reserved counters", "guard window", "movement held intent"],
  "creditKey": ["characterId", "deathEventId", "lifeId", "idempotencyKey"],
  "defaultEnabled": false,
  "scope": "private alpha; reject unknown-map anchor, no generic client teleport; adapter/native UI handoff required"
}
```

## 2. Contract đề xuất

### 2.1 Request

`POST /p1/actor/death-return`, header `X-Session-ID` (bắt buộc). Body:

```jsonc
{
  "schemaVersion": 1,
  "requestId": "<32 hex>",
  "idempotencyKey": "<32 hex>",
  "sentAtUtc": "2026-11-04T09:00:00Z",
  "characterId": "CHR_…",
  "payload": {}                       // object rỗng, additionalProperties:false
}
```

`payload` **không** có field nào: không `mapId`, không `xWu/yWu`, không `anchorRecordId`. Client chỉ được nói "tôi muốn dựng lên". `characterId` phải khớp session (400 `invalid_payload ["characterId"]` như mọi route P1 khác).

### 2.2 Response `DeathReturnResponseV1` (`additionalProperties: false`)

```jsonc
{
  "schemaVersion": 1, "requestId": "…", "sessionId": "…", "serverTimeUtc": "…",
  "result": {
    "applied": true,            // false khi replay; replay trả cùng snapshot
    "replayed": false,
    "mapId": "MAP_BEN_MUA",
    "xWu": 18.0, "yWu": 0.0,    // anchor server tự sở hữu, không phải input
    "hp": 50, "maxHp": 100,
    "mp": 50, "maxMp": 50,
    "serverTick": 1840,
    "revision": 12,             // revision aggregate của session, +1 đúng một lần
    "cleared": {                // design.clear; số kiện đã hủy thật, không phải có/không
      "inflightCasts": 1,
      "reservedCounters": 0,
      "guardWindowClosed": true,
      "movementWindowReset": true
    },
    "penalties": { "xp": 0, "currency": 0, "durability": 0 },  // design nói 0 → echo, không phải chỗ để cấu hình
    "nextReturnAllowedAtTick": 1900              // null khi chưa từng return; 3 s = 60 tick @20 Hz
  },
  "error": { "code": "…", "messageKey": "P1.ERROR.<CODE>", "retryable": false,
             "fieldErrors": [], "correlationId": "…" }   // error null khi 2xx
}
```

### 2.3 Mã lỗi và HTTP status (dùng lại bảng status của các route P1 hiện có)

| HTTP | `error.code` | khi |
|---|---|---|
| 200 | — | return áp dụng, hoặc replay khớp (`replayed: true`, cùng snapshot, không dịch chuyển lần hai) |
| 400 | `invalid_payload` | body/`schemaVersion ≠ 1`/`idempotencyKey` không phải 32 hex/member lạ trong `payload`/thiếu `X-Session-ID` |
| 404 | `session_not_found` | session không tồn tại |
| 409 | `not_downed` | `hp > 0` và **key mới** (`aliveNewRequest`); key đã từng commit thì là replay 200, không phải 409 |
| 409 | `unknown_map` | actor đang ở map không có trong `map_bounds.json` (`reject unknown-map anchor`) |
| 409 | `idempotency_conflict` | cùng key, `characterId` khác (đây đã là hành vi Q-B3) |
| 422 | `death_return_cooldown` | lần return thứ hai trong `newDeathReturnCooldownSeconds` — **tên mã và retryable là đề xuất của tôi, design không đặt tên (câu hỏi Q3 §5)** |
| 503 | `death_return_disabled` | gate OFF. **Không**: route không được map khi gate off nên thành 404 thật (đã đo với `/p1/encounters/*` và `/p1/inventory/v2/*`); tôi ghi 404 nếu owner muốn đồng nhất, đừng dùng 503 |

## 3. Mapping từng dòng design sang code hiện có (để reviewer khỏi đoán)

| design | `DeathReturn.cs` hôm nay | việc phải làm |
|---|---|---|
| `safeAnchorWu [18,0]` + `anchorSource` | `Math.Clamp(P1World.SpawnX/SpawnY, bounds)` — `P1World:SpawnX=18`, `SpawnY=0` | **khớp số, lệch nguồn**: design gọi đây là "new alpha safe-return approval". Đề xuất: khi chạy dưới `P1:AlphaProfile`, anchor phải được validate là đúng `[18,0]` *từ design*, không mượn `P1World` options; `P1:DeathReturn:RestoreHpFixture` bị vô hiệu vì `restoreHp` là công thức (mục dưới) |
| `payload: empty intent` | `ReturnToAnchor(sessionId, idempotencyKey)` — không có coordinate nào | khớp, không đổi |
| `aliveNewRequest` | `actor.Hp > 0 → NotDowned`, refusal **không** ghi ledger nên key còn hạn dùng | khớp |
| `matched committed replay returns same result` | ledger trả `prior.Result with { Replayed = true }` | khớp |
| `restoreHp: max(1,ceil(currentEffectiveMaxHp*0.5))` | chỉ restore nếu fixture > 0, và fixture bị chặn `> StartingMaxHp` | **thay bằng công thức**; `currentEffectiveMaxHp` hiện `== actor.MaxHp` vì **chưa có đường nào cộng stat từ trang bị vào maxHp** (DEC-023 chưa định nghĩa, equipment vẫn metadata-only). Với fixture `100` → `50` |
| `restoreMp: keep current absolute then clamp` | không đụng MP | thêm `actor.Mp = Math.Min(actor.Mp, actor.MaxMp)` — MP không hồi, chỉ bị chặn; không có nguồn nào nói hồi MP |
| `xp/currency/durability penalty = 0` | không trừ gì | khớp; `penalties` trong response là echo để client không tự đoán |
| `clear: inflight casts, reserved counters, guard window` | `_windows.Close(...)` + `_engine.CancelPendingFor(...)` (đã đếm số event `CANCEL`/`END`) | khớp |
| `clear: movement held intent` | **không có** | server không có hàng đợi intent: `/p1/move` tính `elapsed` từ `session.LastMoveAtUtc` (clamped `MaxStepSeconds`) rồi commit ngay. Tương đương duy nhất có nguồn là **reset `LastMoveAtUtc`** (teleport đã làm `/p1/inMemoryTeleportService.cs:84`). Đề xuất: `DeathReturnService.Apply` set `actor.LastMoveAtUtc = clock.UtcNow` — domain only, không wire |
| `creditKey: [characterId, deathEventId, lifeId, idempotencyKey]` | ledger chỉ key theo `idempotencyKey` (+ character) | **không dựng được hôm nay** — xem §4 |
| `newDeathReturnCooldownSeconds: 3` | không có | thêm cooldown per-character trên `ServerClock` (60 tick); cần owner chốt mã lỗi + cách tính từ lần nào (Q3 §5) |
| `defaultEnabled: false` | `P1:DeathReturn:Enabled=false` | giữ OFF trong `appsettings.json`; không bật production flag nào |

## 4. Hai khoảng trống có thật, tôi không tự vá bằng số bịa

**(a) `deathEventId` / `lifeId` của người chơi không tồn tại trong server.**
Entity mob/boss có `LifeId` (life 2 sau respawn) và mỗi kill sinh một death event id (`ICombatKillSink` báo `[killer, entityId, recordId, lifeId, deathEventId]`). **Player thì không**: `PlayerSession` không có `LifeId`/`DeathEventId` (World/PlayerSession.cs:33-56), và đường gây sát thương lên player (`MobAttackService.cs:189-193`, boss encounter, training wave) chỉ ghi `Hp = max(0, Hp - damage)` + `Revision++` — **không phát hành DEATH event nào cho phía player**. Nên `creditKey [characterId, deathEventId, lifeId, idempotencyKey]` hôm nay không dựng được từ dữ kiện authoritative.
Tôi **không** mint `Guid` để thay: đây chính xác là loại "chìa tự sinh" owner đã bác ở Q2 (escort credit). Ba lựa chọn, cần owner chọn một:
1. **`[characterId, idempotencyKey]`** — bỏ `deathEventId`/`lifeId` khỏi credit key cho tới khi player có vòng đời thật; ledger Q-B3 đã đúng như vậy. (Tối thiểu, không thêm state.)
2. **Counter life dẫn xuất từ transition**: server đếm số lần actor đi từ `Hp > 0` → `Hp = 0` (state có nguồn, không random), và `deathEventId = SHA-256(characterId|life|zeroRevision)` — deterministic, dẫn xuất hoàn toàn từ revision aggregate. Vẫn không phải "event" theo nghĩa combat stream.
3. **Player death event hóa hẳn**: phát `CombatEventV2 DEATH` cho actor trong mọi đường gây sát thương (mob/boss/hazard) rồi mới wire — hợp nhất model player/entity, nhưng chạm vào đường event đã đóng băng (`boss.eventProtocol` nói *keep CombatEventV2 closed types*) nên cần quyết định riêng, không ăn theo packet này.

**(b) `P1:AlphaProfile` vs `P1:DeathReturn` — gate nào bật route?**
Design nhét death-return vào alpha profile nhưng gate hiện tại là `P1:DeathReturn:Enabled` (DEV fixture). Đề xuất: route chỉ map khi **cả hai** bật, và `AlphaProfile` on + `DeathReturn.RestoreHpFixture > 0` là **startup failure** (đôi bên cùng quyết định HP, giống tiền lệ `P1:AlphaLoot:GrantEnabled` không cho bật một mình). Cần owner xác nhận (Q4 §5).

## 5. Câu hỏi cần trả lời trước khi tôi viết handler

- **Q1** — credit key: chọn (1)/(2)/(3) ở §4a? (Tôi nghiêng (1) cho private alpha, (2) nếu owner muốn key "khóa theo cái chết" thật sự.)
- **Q2** — `not_downed` khi actor **sống trở lại bằng đường khác** (fixture heal) rồi gửi key đã commit: replay 200 hay 409? Thiết kế chỉ nói "matched committed replay returns same result".
- **Q3** — cooldown 3 s: mã lỗi (`death_return_cooldown`?), `retryable: true`?, tính từ lần **apply** hay từ lần **request cuối** (kể cả request bị từ chối)? `nextReturnAllowedAtTick` có được trả về không?
- **Q4** — gate: đồng ý "map route khi `AlphaProfile` **và** `DeathReturn` cùng bật, và fixture HP > 0 dưới alpha là startup failure"?
- **Q5** — có **cấm** return khi actor đang trong encounter boss/escort ACTIVE không (design không nói; encounter là owner-scoped và wipe là 10 s không mục tiêu)? Tôi mặc định **không chặn** và ghi rõ "unsupported-by-source" nếu owner không trả lời.
- **Q6** — client cần thấy "an toàn để bấm nút Return" không? Hiện `/p1/world` không có field `downed`; muốn expose thì cần wire field (packet này **không** đề xuất).

## 6. Packet này KHÔNG đề xuất

- Không `POST /p1/teleport`, không cho client chọn map/tọa độ, không "portal" chung (`scope`: *no generic client teleport*).
- Không đụng `ITeleportService`/route, không đụng v1 inventory schema, không đụng `CombatEventV2`.
- Không bật `P1:DeathReturn:Enabled` hay `P1:AlphaProfile:Enabled` trong `appsettings.json`; không đánh dấu topology nào `REVIEWED`.
- Không tự ý nối server state `CHAPTER_C1_UNLOCKED` vào response death-return — chuỗi unlock C1 thuộc `questRules.P00-05.unlock`, đi ở nhánh việc khác (#95) và không có field wire.
