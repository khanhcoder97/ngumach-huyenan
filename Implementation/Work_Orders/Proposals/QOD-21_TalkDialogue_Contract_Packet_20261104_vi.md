# Packet hợp đồng TALK / dialogue route (QOD-21 Q4) — **CHỜ DUYỆT — chưa wire, chưa handler**

Gửi Codex (review) + owner (#87) + Antigravity #85 / Muse #1 (client).
Nguồn: `DESIGN-BM-ALPHA-20261103` (`questRules.P00-05`, `questRules.C1-01`), `Character_Equipment_Inventory_Spec_vi.md` (chuỗi chương 1), và máy domain **đã có** trong server: `NarrativeService` / `NarrativeFlagStore` (`Server/Health/Gameplay/Quests/NarrativeNodes.cs`).

Packet này được sinh ra bởi E2E `alpha-p00` (head `61b96a2`), không phải bởi suy đoán. Chuỗi tutorial đi hết `P00-01 → P00-05` qua HTTP thật và **dừng lại ở khách quan cuối của P00-05**: `OBJ_P00_05_CLASS_CONFIRM` là loại `TALK` với `NPC_CLASS_TRIAL`. Server ghi nhận `talk=NO_HTTP_ROUTE` — đó là phát hiện, không phải lỗ hổng của test.

## 1. Vì sao hiện không đi được (bằng chứng trong code)

| sự thật | chỗ nào |
|---|---|
| `TALK` objective chỉ nhận event `QuestProgressEventTypes.Talk` | `InMemoryQuestService.cs:223` |
| Event `Talk` **chỉ** được phát trong `NarrativeService.Enter(...)` | `NarrativeNodes.cs:478` |
| `NarrativeService` **không có route nào** — `P1Endpoints.cs:21-86` không map gì cho narrative | đã đối chiếu toàn bộ endpoint map |
| Hệ quả: `P00-05` không bao giờ `READY_TO_TURN_IN`; `C1-01` (2 khách quan, tất cả là `TALK` ở `MAP_THANH_LAC`) cũng bất khả thi | `alpha-p00` assert điều này mỗi lần chạy |

Nghĩa là **chương 1 không thể vào được bằng HTTP hôm nay**, độc lập với death-return. Đây là khoảng wire, không phải khoảng data: quest pack đã đủ, NPC anchor đã có (`NPC_CLASS_TRIAL` ở (188,0) `MAP_BEN_MUA` và (186,0) `MAP_THANH_LAC`), flag `CHAPTER_C1_UNLOCKED` đã được ghi từ `77bc3a6`.

## 1b. Số liệu hội thoại đã đo (2026-11-05, `112dc61`) — phần này **thay thế** một mặc định tôi từng chọn

| cái gì | số đo |
|---|---|
| `docs/production/Quest_Dialogue_Production_Data_vi.csv` | **230 dòng** = 76 quest × 3 node (`OFFER`/`CLUE`/`TURN_IN`) + 2 dòng `CHOICE` **cùng** `node_id` `DLG_C3_05_CHOICE` |
| bundle runtime `narrative_nodes_v1.json` | **229 node** ⇒ builder gộp đúng hai dòng choice thành một node có `choices[]`; **không mất dòng thoại nào** (đối chiếu id hai chiều: rỗng cả hai phía) |
| vocabulary | `condition_key` = `QUEST_AVAILABLE` / `QUEST_ACTIVE` / `QUEST_READY_TO_TURN_IN` — đúng ba state quest server đã có; `on_enter_event` = `ACCEPT_QUEST` / `OBJECTIVE_PROGRESS` / `COMMIT_REWARD` / `CHOICE_REQUIRED` |
| speaker | **17 NPC**, không NPC nào chỉ có 1 node; `NPC_LYAN` nói **44** node, `NPC_TA_VAN_KHANH` 19 |
| **độ mơ hồ** | cặp `(speaker, condition_key)` có **51** tổ hợp, trong đó **33 tổ hợp map tới nhiều hơn một node** ⇒ không thể resolve node chỉ từ `npcId` + state |
| `CHOICE` | đúng **1** node trên cả campaign (`DLG_C3_05_CHOICE`, group `CHOICE_C3_05_EVIDENCE`, 2 lựa chọn, set flag `C3_05_PUBLISHED` / `C3_05_COUNCIL_ONLY`) |
| thoại đã biên tập | `localization_status`: **15** dòng `VI_EDITED_P1`, **215** `VI_BASELINE`. 15 dòng đó nằm trọn ở **P00-01..P00-05** (5 quest × 3 node, không quest nào trộn hai trạng thái); **C1-01 vẫn là `VI_BASELINE`** |
| node của P00-05 / C1-01 | `DLG_P00_05_CLUE` (order 2, `QUEST_ACTIVE`, `OBJECTIVE_PROGRESS`, speaker `NPC_TA_VAN_KHANH`) và `DLG_C1_01_CLUE` (cùng dạng, speaker `NPC_LYAN`) |

**Sửa lại mặc định của chính tôi ở Q2:** bản packet này từng chọn "`nodeId` optional, server resolve theo `npcId`". Số liệu ở trên bác bỏ lựa chọn đó: 33/51 cặp `(speaker, condition)` là mơ hồ, nên resolve theo NPC sẽ **đoán**. Mặc định mới: **`nodeId` bắt buộc**, và server kiểm node đó có `conditionKey` khớp state hiện tại của quest + `speakerNpcId` khớp NPC đang nói; không khớp thì `409 invalid_transition` (mang field `nodeId`).

**Một lỗi tôi vừa sửa trong chính data:** export đặt `known - next_ids` vào field `terminalNodeIds` — tập đó là **node vào (76 `OFFER`)**, không phải node cuối (76 `TURN_IN`). Field này không loader nào đọc nên chưa gây hỏng hành vi; `112dc61` tách thành `rootNodeIds` + `terminalNodeIds` đúng nghĩa và thêm ràng buộc build fail nếu quest nào không có đúng một root `OFFER` hoặc có terminal không phải `TURN_IN`/`CHOICE`.

**Hệ quả cho Q6 của packet (thoại đã biên tập):** nếu owner muốn P00-05 đóng chuỗi bằng thoại **đã duyệt**, dữ liệu đã sẵn (`VI_EDITED_P1`). Riêng `C1-01` vẫn là baseline — route TALK không nên làm người chơi tin rằng đó là bản thoại cuối; packet sẽ không tự sửa text (docs là phạm vi tôi không được đụng).

## 2. Phương án — tôi đề xuất (A), và nêu (B) để owner chọn

### A. Một verb mới, tối thiểu: `POST /p1/quests/talk`
Chỉ làm đúng những gì nguồn mô tả: **đứng gần NPC, nói chuyện một lần, credit objective `TALK`, và cho phép server áp flag của node**. Không dựng cây hội thoại.

```jsonc
// request
{
  "schemaVersion": 1, "requestId": "<32 hex>", "idempotencyKey": "<32 hex>",
  "sentAtUtc": "…", "characterId": "CHR_…",
  "payload": { "npcId": "NPC_CLASS_TRIAL", "nodeId": null }   // nodeId optional, xem Q2
}

// response
{
  "schemaVersion": 1, "requestId": "…", "sessionId": "…", "serverTimeUtc": "…",
  "result": {
    "npcId": "NPC_CLASS_TRIAL",
    "questUpdates": [ { "questId": "P00-05", "state": "READY_TO_TURN_IN",
                        "stepId": "STEP_P00_05_CONFIRM",
                        "objectiveCounters": { "OBJ_P00_05_CLASS_CONFIRM": 1 },
                        "revision": 7 } ],
    "appliedFlag": null          // flag của node, nếu có; NOT the unlock flag
  },
  "error": { "code": "…", "messageKey": "P1.ERROR.<CODE>", "retryable": false,
             "fieldErrors": [], "correlationId": "…" }
}
```

`nodeId`: khi **không** gửi, server resolve node bằng `npcId` theo catalog narrative hiện có (một node một NPC nếu catalog không mơ hồ); khi catalog có nhiều node cho cùng NPC, request **phải** có `nodeId`, nếu không trả `400 invalid_payload ["payload.nodeId"]`. Tôi chọn hành vi này vì nó không cho client đoán bừa node.

Ràng buộc server-side, tái dùng máy đã có thay vì viết mới:
1. **Distance + floor**: khoảng cách tới `NpcAnchorCatalog` ≤ `MaxInteractionDistanceWu` (5 WU, DEC-016) — giống accept/turn-in; ngoài tầm là `409 out_of_range`.
2. **Reveal gate**: node phải `QUEST_AVAILABLE|QUEST_ACTIVE|QUEST_READY_TO_TURN_IN` đúng như `NarrativeConditions` hôm nay; gate không thoả là `403`-được-đổi-thành… **tôi đề xuất `409 invalid_transition`** để đồng bộ bảng status P1 hiện có (Q3).
3. **Idempotency**: per-character, same key + same payload → replay kết quả đã ghi; same key + payload khác → `409 idempotency_conflict`. Event id cho `Talk` dẫn xuất từ `(characterId, questId, npcId, idempotencyKey)` — **không mint Guid**, đúng nguyên tắc owner đã chốt ở Q2 (escort credit).
4. **Một credit mỗi NPC mỗi quest**: dedupe theo `E:`/`R:` key sẵn có của `InMemoryQuestService` (`objectiveCounters` không tăng lần hai cho cùng node).
5. **Không** đổi quest state ngoài khách quan; **không** tự turn-in; **không** cộng XP; **không** mở portal (portal là `77bc3a6`).

### B. Không thêm route: cho phép `/p1/world/interact` nhận `npcId`
Ít surface hơn, nhưng lạm dụng `interact` (hiện là claim `INTERACTABLE`/`GATHER_NODE`, có `targetState`, claim window, share policy — toàn thứ của node tương tác vật lý, không của hội thoại). Tôi **không** đề xuất B; nêu ra để owner khỏi hiểu là tôi bỏ quên.

## 3. Những gì packet này KHÔNG tự quyết (câu hỏi cho owner)

- **Q1** — `NPC_CLASS_TRIAL` có thuộc tính khả kiến là điều kiện finale (boss down **và** fragment claimed). Route có phải **từ chối** khi điều kiện chưa mở (`409 invalid_transition` + field `revealGate`), hay coi như node chưa tồn tại (`404 quest_not_found`)? Nguồn không nói. Mặc định tôi chọn vế đầu.
- **Q2** — ~~optional hay bắt buộc~~ — **đã có câu trả lời bằng số liệu ở §1b: bắt buộc `nodeId`** (33/51 cặp `(speaker, condition)` mơ hồ). Câu hỏi còn lại cho owner chỉ là: client lấy `nodeId` từ đâu — catalog narrative mà client đang có, hay một read route (`GET /p1/quests/{sessionId}/dialogue`) mà packet này **chưa** mở rộng.
- **Q3** — cây lựa chọn (`CHOICE` nodes trong `narrative_nodes_v1.json`) có được đưa vào verb này không? Mặc định: **không**, ở lại ngoài; chỉ `TALK` để mở khoá chuỗi chương.
- **Q4** — flag vocabulary: `narrative_nodes_v1.json` chỉ có `C3_05_COUNCIL_ONLY`/`C3_05_PUBLISHED`, còn `CHAPTER_C1_UNLOCKED` không thuộc bundle nào — nó do `AlphaDesign` sở hữu (đã pin ở `77bc3a6`). Xác nhận: `appliedFlag` của response **chỉ** mang flag của node narrative, không mang unlock flag của chương.
- **Q5** — `questRules.C1-01.mapViewedAction` ("MAP_VIEWED intent acknowledged by server only while quest ACTIVE and actor in MAP_THANH_LAC, one credit per quest; no reward on open-map read") có cần verb riêng (`POST /p1/quests/map-viewed`) không, hay thuộc về packet death-return/portal? Tôi nghiêng: **một verb duy nhất sau này cho cả hai**, không thêm route thứ hai bây giờ.
- **Q6** — `C1-01` yêu cầu actor đứng ở `MAP_THANH_LAC`, nhưng P1 không có route di chuyển map nào (teleport DI-only, death-return chưa duyệt). Nếu owner muốn C1-01 chơi được qua HTTP, thứ tự duyệt bắt buộc là: **portal/teleport route → rồi TALK route**, hoặc cả hai trong một packet. Tôi cần owner xác nhận thứ tự; nếu không, TALK chỉ cứu được `P00-05`, còn C1-01 vẫn bất khả thi về vật lý.

## 4. Việc sẽ làm sau khi được duyệt (không làm trước)

1. `TalkRequest` / `TalkResponse` schema + examples dưới `Implementation/Contracts/P1/`.
2. `QuestTalkService` nối `NarrativeService` (đã có) + guard khoảng cách/floor/gate + ledger idempotency per-character (cùng mẫu 256 entry với các ledger khác).
3. Route `POST /p1/quests/talk` sau gate `P1:QuestTurnIn` (dùng chung gate vì cùng bản chất "tương tác NPC có thưởng state") — hoặc gate riêng nếu owner muốn.
4. Self-check: gate-off 404 thật, ngoài tầm, sai NPC, replay same-key, same-key-different-payload, dedupe một credit mỗi node, reveal-gate từ chối, và `P00-05` đi tới `READY_TO_TURN_IN` **chỉ** sau TALK hợp lệ.
5. Mở rộng `alpha-p00`: sau fragment, gọi TALK → `READY_TO_TURN_IN` → turn-in → `CHAPTER_C1_UNLOCKED` (đã ghi ở `77bc3a6`) → `C1-01` `AVAILABLE`; in thêm `talk=OK` và giữ `c1_01=` phản chiếu mức tiến bộ thật. Check total vẫn phải cấu trúc cố định.

## 5. Trạng thái hiện tại

Chưa có schema, DTO, route, handler hay gate nào cho TALK. Không có gì trong `appsettings.json` bị bật. Chuỗi `P00-01 → P00-05` hiện đã chạy được tới bước cuối trong CI (`e2e-alpha-p00`, 95 checks), và profile assert đúng điểm dừng này thay vì giả bộ hoàn thành.

## Bổ sung 2026-11-06 (head `1d2d2be`): packet này thiếu một chặn thật, và nó không phải chuyện wire

Khi kiểm tra lại các nguồn mà server chưa đọc, tôi tìm ra rằng câu hỏi "TALK route hình
dạng thế nào" **chưa phải** thứ chặn item 4. Chặn trước đó là dữ liệu spawn tự mâu thuẫn:

- `World_Spawn_Gathering_Manifest_vi.csv` dòng `MAN-BM-NPC_CLASS_TRIAL`: `NPC_CLASS_TRIAL`
  ở `(188,0)` `MAP_BEN_MUA`, điều kiện hiện **"Hiện sau khi hoàn tất P00-05"**, persistent,
  spawn theo map/quest state.
- `Map_Production_Atlas_vi.md:68`: `NPC_CLASS_TRIAL | (188,0) | xuất hiện sau boss, menu chọn lớp`.
- `World_Spawn_Gathering_Manifest_vi.csv` dòng `MAN-TL-NPC_CLASS_TRIAL`: cùng NPC ở
  `(186,0)` `MAP_THANH_LAC`, **"Sau P00-05; xác nhận lựa chọn môn phái"**.
- `NPC_Actor_Production_Registry_vi.csv`: `NPC_CLASS_TRIAL` mang
  `interaction_service_id = SERVICE_CLASS_SELECTION` và `dialogue_bank_id = DLG_NPC_CLASS_TRIAL`
  (toàn bộ 64 NPC khác là `NONE`; chỉ 15 NPC có service token).
- `Production_Rules_Complete_v1_vi.md:66` giữ `TALK` trong danh sách step type được duyệt;
  `Development_Execution_Board_vi.md:39` nêu `talk` trong exit slice `P00-01..05`.

Mâu thuẫn: khách quan cuối của `P00-05` là `OBJ_P00_05_CLASS_CONFIRM`, loại `TALK`, đích
`NPC_CLASS_TRIAL` — nhưng theo cả hai dòng manifest và atlas, NPC đó **chỉ xuất hiện sau khi
`P00-05` hoàn tất**. Không có cách nào hoàn tất khách quan bằng đúng NPC mà điều kiện hiện của
nó là khách quan đã xong. Server hiện ghi `talk=NO_HTTP_ROUTE`; phát hiện chính xác hơn phải là
`talk=NPC_NOT_YET_PRESENT`.

Tôi **không** tự sửa: docs/production không thuộc quyền của tôi, và đây là quyết định thứ tự
quest, không phải tuning. Ba lựa chọn, chủ dự án chốt:

1. Sửa điều kiện hiện của `MAN-BM-NPC_CLASS_TRIAL` thành "xuất hiện sau khi boss Mãng Cốt bị
   hạ (objective `DEFEND`/`BOSS_PHASE` xong)" — lúc đó `TALK` nằm ngoài chu kỳ và server chỉ
   cần đọc quest state, không đổi wire shape nào khác.
2. Giữ điều kiện hiện, đổi khách quan `CLASS_CONFIRM` sang một NPC đã có mặt (ví dụ `NPC_LYAN`
   hoặc `NPC_TA_VAN_KHANH`) — nhưng hai NPC này mang `interaction_service_id = NONE`, nên cần
   cấp token cho họ trong registry, tức sửa dữ liệu NPC.
3. Cho phép `CLASS_CONFIRM` hoàn thành qua menu chọn lớp (không qua TALK) — hợp với chữ
   "menu chọn lớp" trong atlas, nhưng đổi loại step so với `Production_Rules_Complete_v1_vi.md:66`
   nên cần ghi quyết định mới vào register.

Wire packet (schema/`P1:Dialogue` gate OFF/idempotency) vẫn còn nguyên và vẫn chờ **duyệt**;
chỉ có điều là dù được duyệt, nó cũng chưa chạy được cho tới khi một trong ba lựa chọn trên
được chốt.
