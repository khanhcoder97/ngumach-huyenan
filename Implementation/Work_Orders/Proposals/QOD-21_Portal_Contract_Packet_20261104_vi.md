# Packet hợp đồng Portal / đổi map (QOD-21 Q4) — **CHỜ DUYỆT — chưa wire, chưa handler, và thiếu nguồn toạ độ**

Gửi Codex (review) + owner (#87) + Antigravity #85 / Muse #1 (client).
Lý do packet này tồn tại: E2E `alpha-p00` (head `61b96a2`) đi hết `P00-01 → P00-05` qua HTTP rồi dừng ở `TALK` (packet `QOD-21_TalkDialogue_Contract_Packet_20261104_vi.md`), và **ngay cả khi TALK được duyệt thì `C1-01` vẫn bất khả thi về vật lý**: hai khách quan của nó ở `MAP_THANH_LAC`, còn server không có route nào được phép đổi map của một actor.

## 1. Sự thật hiện trạng (kiểm tra trong code, không suy đoán)

| sự thật | chỗ nào |
|---|---|
| Session luôn sinh ra ở `P1World:DefaultMapId` = `MAP_BEN_MUA`; body `POST /p1/sessions` **không** nhận `mapId` | `Server/Health/World/P1WorldOptions.cs:7`, `P1Endpoints.cs` (CreateSessionAsync) |
| `ITeleportService` là đường đổi map duy nhất và **không có route**: chỉ được DI, chưa từng được gọi từ HTTP | `Program.cs` (`AddSingleton<ITeleportService, …>`), `Server/Health/README.md` mục Teleport |
| Server **đã ghi** quyền vào chương 1: `CHAPTER_C1_UNLOCKED` + portal `MAP_THANH_LAC`, cấp trong transaction turn-in P00-05 | `Gameplay/Alpha/AlphaChapterUnlocks.cs`, `77bc3a6` |
| `MAP_THANH_LAC` đã có trong `map_bounds.json` (`knownMapIds`, không có override nên dùng `defaultBounds`) | `Implementation/Content/map_bounds.json:61` |
| `questRules.C1-01` đặt hai khách quan ở `MAP_THANH_LAC` với `NPC_LYAN/NPC_GUARD_CAPTAIN/NPC_HA_MAC/NPC_MASTER_MINH_KIEM` và `trialRegistrationNpcId: NPC_CLASS_TRIAL` (anchor ở (186,0) `MAP_THANH_LAC`) | `Implementation/Content/Examples/QuestDefinitionAlpha/C1-01.json`, `Runtime/npc_anchors.json` |

## 2. Contract đề xuất — một verb, toạ độ do server sở hữu

`POST /p1/world/portal`, header `X-Session-ID`:

```jsonc
// request
{ "schemaVersion": 1, "requestId": "<32 hex>", "idempotencyKey": "<32 hex>",
  "sentAtUtc": "…", "characterId": "CHR_…",
  "payload": { "portalId": "MAN-TL-PORTAL_C1" } }   // KHÔNG có mapId, KHÔNG có xWu/yWu
```

Client chỉ được chọn **portal record id** do server phát hành. Server tự quyết điểm đến và chỗ đứng:

1. `portalId` phải tồn tại trong registry portal (mục 4 — **thiếu nguồn**).
2. Actor phải đứng trong tầm tương tác của portal phía map hiện tại (≤ `MaxInteractionDistanceWu` = 5 WU, DEC-016) — ngoài tầm là `409 out_of_range`, giống accept/turn-in/interact.
3. **Quyền vào map**: `ChapterUnlockStore.AllowsPortal(characterId, destinationMap)` — đúng record server đã ghi ở `77bc3a6`; chưa có quyền là `409 portal_locked` (`retryable: false`, field `portalId`). Không có đường nào để client tự "xin" quyền.
4. Di chuyển thật đi qua `ITeleportService.Teleport(reason: QUEST)` (đã validate map tồn tại, bounds, `hp > 0`, `Revision++`, reset `LastMoveAtUtc`) — **không** viết đường ghi map mới, **không** cho `reason: ADMIN`, **không** cho `DEATH_RETURN` (đó là packet death-return riêng, chưa duyệt).
5. Idempotency per-character: same key + same `portalId` → replay cùng snapshot, không dịch lần hai; same key khác payload → `409 idempotency_conflict` (cùng mẫu ledger 256 entry các route khác đang dùng).

```jsonc
// response
{ "schemaVersion": 1, "requestId": "…", "sessionId": "…", "serverTimeUtc": "…",
  "result": { "portalId": "MAN-TL-PORTAL_C1", "fromMapId": "MAP_BEN_MUA",
              "toMapId": "MAP_THANH_LAC", "xWu": 30.0, "yWu": 0.0,
              "floorId": "OVERWORLD", "revision": 12, "serverTick": 240 } }
```

## 3. Bảng status (dùng lại khung P1 hiện có, không chế code mới tùy tiện)

| HTTP | code | khi |
|---|---|---|
| 200 | — | dịch map thành công, snapshot là vị trí sau dịch |
| 400 | `invalid_payload` | body/`schemaVersion ≠ 1`/member lạ/`portalId` sai mẫu/thiếu `X-Session-ID` |
| 404 | `session_not_found` | session không tồn tại |
| 404 | `portal_not_found` | `portalId` không có trong registry |
| 409 | `out_of_range` | actor chưa đứng gần portal nguồn |
| 409 | `portal_locked` | server chưa ghi quyền vào map đó (đề xuất — xem Q2) |
| 409 | `idempotency_conflict` | cùng key, payload khác |
| 422 | `invalid_condition` | actor `hp <= 0` (đang chết thì không đi được; để dành cho death-return) |

## 4. Thứ **thiếu nguồn** — tôi không tự bịa

Design chỉ nói một câu: `questRules.P00-05.unlock` = "P00-05 turn-in commits CHAPTER_C1_UNLOCKED and MAP_THANH_LAC portal access". Nó **không** cung cấp:

1. **Tọa độ portal hai đầu.** `map_bounds.json` không có override cho `MAP_THANH_LAC` (dùng `defaultBounds`), và `world_records.json` không có record portal nào. Không có nguồn thì không có `portalId` hợp lệ nào để map.
2. **Cặp map nào được đi** (Bến Mưa → Thanh Lạc một chiều? hai chiều? có mở tiếp map khác không).
3. **Điều kiện ngoài quyền**: level? quest đang `ACTIVE`? party solo scale 1–3 như boss ring?
4. **Chi phí/ cooldown / thời gianLoading**: P1 không có khái niệm travel time; nếu client cần animation thì server phải trả gì.
5. **Điểm đến có phải anchor cứng không** — `NPC_LYAN` ở Thanh Lạc là (30,0), nhưng đứng ở (30,0) có phải chỗ an toàn không thì không nguồn nào nói.

Vì vậy packet này **chưa thể thành handler** kể cả khi owner gật về hình thức: cần owner ( hoặc design) bổ sung mục 4.1–4.5 vào baseline alpha, đúng kiểu `boss` block đã phải bổ sung số cho Mãng Cốt ở Q2.

## 5. Câu hỏi cần trả lời

- **Q1** — xác nhận hướng: portal là **registry record** (`portalId`) chứ không phải `(mapId, x, y)` do client gửi? (Đề xuất: record.)
- **Q2** — `portal_locked` có phải tên mã chủ trương không, hay owner muốn `404 portal_not_found` cho trường hợp chưa mở khoá (để không lộ tồn tại của map)?
- **Q3** — có cho phép quay lại Bến Mưa từ Thanh Lạc không?
- **Q4** — `questRules.C1-01.mapViewedAction` (MAP_VIEWED credit) gắn vào response của portal call, hay chờ một verb riêng?
- **Q5** — thứ tự duyệt: portal **trước** TALK (để client vào được map rồi mới nói chuyện), hay cả hai một lượt? E2E hiện tại sẽ báo `c1_01=LOCKED` cho tới khi cả hai tồn tại.

## 6. Packet này KHÔNG đề xuất

- Không `POST /p1/teleport` chung, không cho client chọn map/tọa độ, không "world map fast travel" cho mọi map.
- Không đụng `P1:DeathReturn`, không đụng v1 inventory schema, không đụng `CombatEventV2`, không bật gate nào trong `appsettings.json`, không đánh dấu topology `REVIEWED`.
- Không viết handler/schema/DTO/route cho tới khi owner trả lời §4 và §5.
