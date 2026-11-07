# Packet QOD-24 Q8 — endpoint `capability` và schema packet — **CHỜ DUYỆT — chưa code, chưa route, chưa đổi schema nào**

Gửi owner (#87, #41) + Codex (review) + OpenCode #85 / Muse #1.
Lệnh gốc: work order 29 mục Q8 — *"Launcher private Windows/health identity/stop owned PID, regression HTTP, **capability/schema packet**."* Work order 13 dòng 31 cũng đã yêu cầu *"versioned proposal/examples/**capability** thay vì dựa vào event đã trôi khỏi buffer"*. OpenCode O1 trong work order 29 liệt kê **"capability"** trong số các schema phải theo — tức client đã được giao việc tiêu thụ một contract mà server **chưa có**.

Packet này không sửa file nào khác ngoài chính nó. Không route mới, không DTO mới, không đụng schema đã đóng băng, không bật gate.

## 1. Vấn đề, kê bằng chứng đo được

Hiện tại client biết một tính năng có bật hay không **bằng cách thử và đọc status code**:

| gate (tên section trong code) | route bị nó chặn | hành vi khi OFF |
|---|---|---|
| `P1:QuestAccept` | `POST /p1/quests/accept` | 404 |
| `P1:Interact` | `POST /p1/world/interact` | 404 |
| `P1:QuestTurnIn` | `POST /p1/quests/turnin` | 404 |
| `P1:Equipment` | `POST /p1/inventory/equip`, `/unequip` | 404 |
| `P1:CombatV2` | `GET /p1/v2/world`, `POST /p1/v2/combat`, `GET /p1/v2/events` | 404 |
| `P1:AlphaProfile` | `GET /p1/encounters/current`, `/p1/encounters/{id}`, `GET/POST /p1/inventory/v2*` | 404 |
| `P1:DeathReturn` **+** `P1:AlphaProfile` | `POST /p1/actor/death-return` | 404 (hai gate AND nhau) |

(`Server/Health/Endpoints/P1Endpoints.cs`, `MapP1Endpoints`; danh sách section lấy từ `grep 'SectionName = "P1'` — 11 section, chưa kể `P1World`.)

Hệ quả đã xảy ra thật trong dự án, không phải lý thuyết:
- Issue #96: client cast vào một MOB mà engine **không** resolve, vì audience báo `ALIVE/targetable:true`. Server đã sửa cách báo, nhưng **không có chỗ nào để client hỏi** "damage gate đang bật không".
- Tôi từng phải viết "P1 **không có** capability endpoint" trong một checkpoint gửi #85, vì client hỏi endpoint đó.
- `P1:CombatDamage` **không có mặt trong `appsettings.json`** (mặc định off theo code) → một client đọc file cấu hình cũng không biết nó bật hay tắt; chỉ có server process mới biết.
- Cùng một họ lỗi tôi vừa sửa ở Q4: `P1Validation.IsSkillId` (`^SK-MK-0[1-3]$`) hẹp hơn `SkillDefinition.schema.json` (`^SK-[A-Z0-9]{2}-[0-9]{2}$`). Client đọc schema published thì tin có 30 skill, gọi thật thì ăn 400. **Đây chính là thứ một capability response phải trả lời được.**

## 2. Hợp đồng đề xuất

`GET /p1/capability` — read-only, **không** cần session header, **luôn** được map (không đặt sau gate: một endpoint phải hỏi được kể cả khi mọi gate OFF, nếu không nó vô nghĩa).

```jsonc
{
  "schemaVersion": 1,                       // version của CHÍNH payload này
  "serverTimeUtc": "...",
  "contracts": {
    "schemaSet": "P1",                       // nguồn: Implementation/Contracts/P1/
    "schemaCount": 31,                       // đếm từ repo lúc build, không hard-code
    "contentHash": "<sha256 canonical>"      // để client biết mình đang theo bản nào
  },
  "gates": [                                 // đúng 11 section P1:* + P1World
    { "id": "P1:CombatV2", "enabled": false, "routes": ["POST /p1/v2/combat", "GET /p1/v2/world", "GET /p1/v2/events"] },
    { "id": "P1:DeathReturn", "enabled": false, "routes": ["POST /p1/deathreturn"],
      "requires": ["P1:AlphaProfile"] }      // gate AND nhau phải nói ra, client không được suy đoán
  ],
  "vocabularies": {
    "skillIds": ["SK-MK-01", "SK-MK-02", "SK-MK-03"],   // lấy từ P1Validation, TỪ pattern, không phải từ catalogue
    "interactTargetIds": {
      "pattern": "^ENT_[A-Z0-9_]+$",
      "exactIds": ["ALPHA_OBJ_BM_FRAGMENT",
                  "ALPHA_OBJ_BM_RIPPLE_01", "ALPHA_OBJ_BM_RIPPLE_02", "ALPHA_OBJ_BM_RIPPLE_03",
                  "ALPHA_OBJ_BM_VILLAGER_01", "ALPHA_OBJ_BM_VILLAGER_02"]  // đúng sáu id trong P1Validation.AlphaInteractEntityIds
    },
    "inventorySlotsV1": ["HAT", "CHEST", "BOOTS", "WEAPON", "ACCESSORY"],
    "inventorySlotsV2": ["HAT", "CHEST", "LEGS", "WEAPON", "GLOVES", "BOOTS", "NECK", "RING_L", "RING_R", "PENDANT", "CLOAK", "SEAL"]
  },
  "limits": {
    "maxRequestBytes": 8192,                 // MaxBodyBytes trong P1Endpoints
    "aoi": { "enterWu": 40, "leaveWu": 48 },
    "combatEventStream": { "capacityPerSession": 512, "maxPageSize": 200 },
    "bagSlots": 100,
    "deathReturnCooldownTicks": 60,
    "serverTickHz": 20
  },
  "profile": {
    "alphaProfileVersion": null,             // null khi gate OFF; không bao giờ giả có profile
    "alphaStatus": null                      // "PRIVATE_ALPHA"… lấy từ design đã nạp, không hard-code
  },
  "unsupported": [                           // thứ client KHÔNG được giả định là chạy được
    { "id": "PARTY_ROUTING", "reason": "NO_SOURCE_APPROVED" },
    { "id": "SKILL_NON_MINH_KIEM", "reason": "NOT_IN_WIRE_VOCABULARY" },
    { "id": "TOPOLOGY_GEOMETRY", "reason": "NO_REVIEWED_BUNDLE" }
  ]
}
```

Nguồn từng field khi code: `vocabularies.skillIds` ← `P1Validation.SkillIdPattern`; `interactTargetIds` ← `P1Validation.EntityIdPattern` + `AlphaInteractEntityIds` (`:71-80`); `inventorySlotsV1` ← `EquipmentSlots` (`Server/Health/Gameplay/Inventory/Equipment.cs:15-19`); `inventorySlotsV2` ← `InventoryV2Slots.All`; `limits.maxRequestBytes` ← `P1Endpoints.MaxBodyBytes` (`P1Endpoints.cs:16`); `limits.combatEventStream` ← `P1:CombatEventStream` trong `appsettings.json`; `limits.serverTickHz` ← `ServerClock.TicksPerSecond`; `limits.deathReturnCooldownTicks` ← `DeathReturn.CooldownTicks`; `limits.aoi` ← `WorldAudience.AoiEnterWu`/`AoiLeaveWu` (`WorldAudience`, khai báo tại `Server/Health/World/WorldEntityAoiProjection.cs:16-17`).

**Mọi field phải do runtime tự dựng** từ chính các hằng/pattern/`IOptions` mà route đang dùng — không có bảng echo nào. Lý do: một bảng echo là một chỗ nữa để stale, và lesson của #96 đúng là "projection nói khác engine". Test khoá điều này: mỗi giá trị trong response phải so được với hằng nguồn (`P1Validation.IsSkillId` với `vocabularies.skillIds`, `MapP1Endpoints` với `gates[].routes`).

## 3. Luật validate (tôi sẽ viết trong `validate_contracts.py` nếu được duyệt)

1. `gates[].routes` phải bằng đúng tập route mà `MapP1Endpoints` map khi gate đó ON/off — kiểm bằng self-check, không kiểm bằng mắt.
2. `vocabularies.skillIds` chỉ được chứa id mà `P1Validation.IsSkillId` trả `true`; một id có trong catalogue mà không có trong wire vocabulary **phải** xuất hiện ở `unsupported[]`, không được im lặng.
3. `profile.alphaProfileVersion` null ⇔ `P1:AlphaProfile` OFF.
4. Response không được chứa: bí mật, connection string, đường dẫn tuyệt đối, `characterId`/`sessionId` của người khác, tình trạng encounter của người khác, hay bất kỳ thứ gì suy ra được ai đang online. Capability là **cấu hình**, không phải trạng thái.
5. Envelope dùng `P1Json` hiện hành (`JsonUnmappedMemberHandling.Disallow`), `messageKey` vẫn theo `^P1\.ERROR\.[A-Z_]+$`; lỗi duy nhất dự kiến là `capability_unavailable` (503) nếu composition root lỗi — còn lại 200.
6. `GET`, không idempotency key, không revision bump, không ghi ledger, không đụng session. Cache: `Cache-Control: no-store` ở phase đầu (chưa quyết ETag — xem §5 câu 5).

## 4. Ví dụ (examples) tôi sẽ ship kèm

- `CapabilityResponse.example.json` — production-defaults: 11 gate OFF, `skillIds` ba id, `inventorySlotsV2` vẫn liệt kê 12 token **kèm** `unsupported[]` nói rõ các route v2 cần `P1:AlphaProfile`. Điểm này quan trọng: capability phải trả lời "schema tồn tại nhưng route không map", vì đó chính xác là chỗ OpenCode vấp.
- `CapabilityResponse.example.alpha.json` — private alpha: `AlphaProfile`/`DeathReturn`/`CombatDamage` ON, `unsupported[]` còn `PARTY_ROUTING`.
- Negative fixture: response có `gates` thiếu `requires` khi hai gate AND nhau → validator fail; response tiết lộ `sessionId` → fail.

## 5. Câu hỏi cần trả lời trước khi tôi code (mặc định = không làm)

1. **Đường dẫn.** `GET /p1/capability` hay `GET /p1/meta` / `/p1/schema`? Mặc định: `/p1/capability`.
2. **Có cần session không?** Mặc định: không. Hệ quả: thông tin trả lời là **cấu hình chung**, không phải theo người. Nếu owner muốn per-session (ví dụ node availability phụ thuộc caller như AOI), đó là endpoint khác.
3. **Có được liệt kê gate không bật không?** Đây là disclosure vận hành (một người ngoài biết được profile nào đang chạy). Mặc định của tôi: **chỉ liệt kê id + enabled boolean**, không kèm tên profile/version nếu gate OFF. Nếu Codex muốn ẩn toàn bộ `gates[]` với request không có session, tôi làm được, nhưng khi đó client vẫn phải thử — tức mất một nửa giá trị.
4. **`contentHash` tính trên gì?** Mặc định: canonical JSON của toàn bộ `Implementation/Contracts/P1/*.schema.json` đã sort key, không white-space — cùng quy tắc tôi đã dùng cho `nav_ben_mua_v1` trong packet Q3.
5. **ETag / cache?** Mặc định phase 1: `no-store`, không ETag. Thêm sau nếu cần.
6. **`unsupported[]` là wire hay docs?** Mặc định: wire, vì đó là phần client dễ đoán sai nhất. Mỗi mục phải có `reason` thuộc enum đóng, không free-text.
7. **Endpoint có được map khi server đang fail-fast validation không?** Mặc định: có, nhưng trả 503 `capability_unavailable` với lý do không chi tiết.

## 6. Việc làm được ngay sau khi duyệt (không đụng contract nào khác)

1. `Implementation/Contracts/P1/CapabilityResponse.schema.json` (schema **mới**, không sửa schema cũ) + hai example + validation rules §3.
2. `Server/Health/Contracts/CapabilityMessages.cs` (DTO) + `P1Endpoints.MapGet("/p1/capability", ...)` **luôn map**, đọc từ `IOptions` + pattern thật.
3. Capability builder **tự dựng từ chính predicate**: `P1Validation` expose một danh sách read-only các id hợp lệ (không đổi predicate), `MapP1Endpoints` ghi lại bảng route→gate vào một registry dùng chung để endpoint và router không lệch nhau.
4. Self-check: response dựng được với mọi gate OFF; mỗi gate ON thêm đúng một route xuất hiện; `unsupported[]` luôn chứa skill ngoài wire vocabulary.
5. e2e profile `capability` + job CI (chạy với production defaults, assert 11 gate OFF và không có route nào sau gate được map).

Không mục nào trong §6 bật gate production, đổi schema cũ, hay sửa hành vi route hiện có.
