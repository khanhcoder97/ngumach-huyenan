# QOD-18 — Bàn giao P1 Bến Mưa (Codex / OpenCode / Muse)

**Head bàn giao:** `20e98bf` trên `qoder/qod-18-ben-mua-completion-20261030` (PR #91 → #84, stack chưa merge).
**Ngày đo:** 01/11/2026. **Trạng thái:** toàn bộ gate production **OFF**; không tự merge; không có số liệu nào được bịa thêm.

Tài liệu này là bản bàn giao Q-G: chỗ nào chạy được qua HTTP, chỗ nào chỉ là domain/fixture, chỗ nào bị chặn và **cần đúng nguồn nào**. Các con số dưới đây đo tại đúng head trên; CI chạy lại cùng bộ lệnh.

## 1. Kiểm chứng tại head

```bash
dotnet build Server/Health/Health.csproj --configuration Release
dotnet Server/Health/bin/Release/net10.0/Health.dll --self-check
bash Server/Health/Smoke/run_e2e_p1.sh default      # expected blocked output
bash Server/Health/Smoke/run_e2e_p1.sh dev          # golden loop P00-01 + equip
bash Server/Health/Smoke/run_e2e_p1.sh mob-combat   # combat gates only
bash Server/Health/Smoke/run_e2e_p1.sh two-client   # isolation + campaign stop
python Implementation/Tools/validate_contracts.py
python Implementation/Tools/validate_content.py
```

| Kiểm tra | Kết quả tại `20e98bf` |
|---|---|
| Build | 0 error |
| Self-check | **392 passed / 0 failed** |
| Smoke HTTP | **454 checks** |
| E2E default / dev / mob-combat / two-client | **11 / 185 / 85 / 151 checks** |
| Contracts | **23 schema + 23 example**, reference sets OK |
| Content / topology / narrative + 5 runtime rebuild | clean, no drift |

CI tại head: [e2e 4 job](https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41295932281) · [build](https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41295932387) · [smoke](https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41295932316) · [contract](https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41295932282) · [content](https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41295932235) — tất cả success.

**Phiên bản nội dung đang nạp:** 46 map bounds · 5 QuestDefinition · 3 combat skill · 352 world record · 44 world entity / 22 template · 57 loot source / 184 entry · 229 narrative node · 2.656 item id (556 catalogue gốc + 2.235 rarity variant − 135 dòng trùng giống hệt) · 16 currency id.

## 2. Bề mặt HTTP và gate

Công khai (không gate): `/health`, `POST /p1/sessions`, `POST /p1/move`, `POST /p1/combat` (v1 chỉ trả `combat.effect`), `GET /p1/world|quests|inventory/{sessionId}`.

Gate OFF mặc định (route không được map; POST rơi xuống template GET cùng path nên trả **405**, trừ v2 trả 404):

| Gate | Route | Vai trò |
|---|---|---|
| `P1:QuestAccept:Enabled` | `POST /p1/quests/accept` | nhận quest, khoảng cách/LOS theo anchor |
| `P1:Interact:Enabled` | `POST /p1/world/interact` | collect package / gather node, per-character claim |
| `P1:QuestTurnIn:Enabled` | `POST /p1/quests/turnin` | transaction grant → flip → ledger |
| `P1:Equipment:Enabled` | `POST /p1/inventory/equip`, `/unequip` | metadata equip, **không áp stat** |
| `P1:CombatV2:Enabled` | `GET /p1/v2/world/{id}`, `POST /p1/v2/combat`, `GET /p1/v2/events/{id}` | prototype tick engine + event stream |
| `P1:CombatDamage:Enabled` | (không route riêng) | bật damage số học REFERENCE_L5 (DEV) |
| `P1:MobBehavior:Enabled` | (không route riêng) | mob AI tick 20 Hz (DEV fixture) |
| `P1:DeathReturn:Enabled` | không có route | domain-only, chưa lên wire |

Không có route cho teleport, dialogue/narrative, boss encounter hay death-return. Mọi lỗi theo `P1Error` (`code`, `messageKey = P1.ERROR.<CODE>`, `retryable`, `fieldErrors`, `correlationId`); request lỗi shape luôn là `invalid_payload` + field cụ thể.

## 3. Event v2 và timing cho client

`CombatEventV2` (chỉ đọc qua `/p1/v2/events`, gate `CombatV2`):

| Trường | Ý nghĩa |
|---|---|
| `eventId`, `cursor` | cursor tăng đơn điệu **trong một session**; client giữ cursor cuối |
| `type` | `CAST_START`, `COUNTER_CONFIRMED`, `IMPACT`, `MISS`, `CANCEL`, `END`, `DEATH` |
| `castId` | nối toàn bộ vòng đời một cast (start → impact/miss → end/cancel); counter dùng `castId` của guard |
| `actorId`, `targetId`, `targetLifeId` | nguồn/đích và life của đích (lifeId đổi khi respawn) |
| `hitIndex` | thứ tự hit trong cùng cast (đòn nhiều hit) |
| `mapInstanceId`, `floorId` | lọc theo instance/tầng |
| `sourceRevision`, `targetRevision` | revision của actor/target tại thời điểm event |
| `serverTick`, `emittedAtUtc` | tick 20 Hz và mốc UTC |
| `result` | `{ hit, crit, immune, amount, absorbed, hpDamage }`; `hpDamage` là số HP thực mất, có thể 0 khi bị chặn/immune |

Quy tắc đọc: page tối đa **200**, buffer **512 event/session** (DEV budget). Cursor quá cũ hoặc vượt stream → `resyncRequired` + `resyncReason` `CURSOR_TOO_OLD` / `BUFFER_OVERFLOW`; client phải đối chiếu lại từ `GET /p1/v2/world` thay vì đoán. Không có event nào bị bỏ im lặng.

Timing: tick cố định **20 Hz (50 ms)**, `serverTick` là thời gian chuẩn. Các con số sau là luật/DEV fixture đã ghi trong README:
- telegraph mob **0,45 s = 9 tick** (fixture, Art Bible §12); impact nằm ở tick cuối telegraph và **vẫn xảy ra** nếu target rời tầm, chỉ damage recheck mới whiff.
- guard window `[T, T+8)` (8 tick), whiff `[T+8, T+28)` (20 tick), counter resolve ở **tick kế tiếp**; giảm 0,70 khi đỡ đúng mặt, 0,20 trong whiff, góc 120° và tầm 4,4 WU inclusive (DEC-022).
- attack cooldown 2 s, recovery 0,5 s (DEV fixture).
- `MISS` không kèm damage; `COUNTER_CONFIRMED` chỉ là xác nhận mở counter, kết quả counter là `IMPACT`/`MISS` riêng cùng `castId`.
- telegraph read model có `impactInTicks`/`recoverInTicks`/`nextAttackInTicks` nhưng **chưa lên wire**; `angleDegrees` cố ý `null` vì chưa có shape nguồn.

VFX/UI tối thiểu: `TELEGRAPH` → vòng cảnh báo (không có góc); `IMPACT` → hit VFX + số `hpDamage`; `MISS` → whiff; `COUNTER_CONFIRMED` → flash; `DEATH` → death anim/despawn theo `targetId` + `targetLifeId`; `CANCEL`/`END` → ngắt cast. HP về 0 không tự hồi; death-return chưa có wire.

## 4. Feature matrix Bến Mưa

| Hạng mục | Trạng thái | Bằng chứng / chặn |
|---|---|---|
| Session, move, world/quest/inventory read | **Chạy** | smoke + e2e |
| `P00-01` accept → 3 package → turn-in → reward | **Chạy, gate OFF** | dev E2E 185; COIN 20 + `EQ-MK-CHEST-T1-R-COMMON`, XP `applied=false` |
| Equip/unequip metadata | **Chạy, gate OFF** | dev + two-client; BAG↔EQUIPPED, revision +1/call |
| `P00-02` | **BLOCKED** | `P00_02_RIPPLES` (`objectiveTargets`) — không có record gợn nước |
| `P00-03` | **BLOCKED** | `P00_03_TURN_IN_NPC`, `P00_03_VILLAGERS`, `P00_03_WAVE` |
| `P00-04` | **BLOCKED** | `P00_04_TURN_IN_NPC`, `P00_04_ESCORT` (checkpoint), `P00_04_WAVE_ATTRIBUTION` |
| `P00-05` | **BLOCKED** | `P00_05_BOSS_DATA`, `P00_05_FRAGMENT`, `P00_05_TURN_IN_NPC`, `P00_05_CHAPTER_UNLOCK` |
| Mãng Cốt encounter | **Domain-only** | state machine + 23 test fixture; không route/DI; 9 field nguồn còn thiếu |
| Fragment → class-confirm → portal | **BLOCKED** | phụ thuộc `P00-05_FRAGMENT` và `C1-01` chưa có record runtime |
| XP/level | **Transaction chạy, số lượng chưa có** | `level_progression_v1.json` 100 row; rule trả unresolved ⇒ `applied=false` |
| Loot grant | **Service + ledger + kill hook chạy; bundle grant OFF** | `COIN_BAND_MISSING`; chưa có coin band/gear roll vector |
| Inventory | **Chạy** | revision/slot/currency guard; equip metadata |
| Fullbag / durability / binding / tradeable | **Không có nguồn** | xem §5 |
| Two-client | **Isolation chạy** | package/node `PER_CHARACTER`; không có nội dung tranh chấp shared |
| Narrative | **Domain-only** | 229 node, reveal gate + flag; chưa có route |
| Teleport | **Domain-only** | chưa có route |
| Death return | **Domain-only, gate OFF** | anchor là spawn clamp, không phải safe anchor; không penalty |
| Topology / LOS | **Synthetic** | `not_enforced`; chờ bundle `REVIEWED` của Muse |
| Persistence | **In-memory** | PostgreSQL thuộc QODER Remote #79 |
| Party | **Solo-only** | `PartyPolicies.SoloOnly`; chưa có party runtime |

## 5. Field còn thiếu — cần đúng nguồn nào

| Field | Ảnh hưởng | Nguồn cần |
|---|---|---|
| `P00-02..05` objective record id / NPC / checkpoint / fragment | 4 quest không mở được | `Quest_and_Narrative_Production_Spec_vi.md#P00-0x` + Map Atlas: record id cụ thể |
| `bossStats`, 3 move (damage/telegraph/shape), `phaseGuard`, interruptibility | Mãng Cốt không đánh được | `Content_Bible`/Rules §4 + `combat_mob_stats` bundle thay `BOSSDATA_BLOCKED` |
| Arena polygon / `safePad` | không có hình học encounter | Map Atlas §Đầm Chuông; record có "boss ring Ø22" nhưng chưa phải polygon |
| Record boss trùng `MAN-BM-EVENT_BOSS_BM_MANG_COT` và `MAN-BM-SPAWN_BM_05_QUEST` cùng (178,0) | không chốt được instance | owner chọn record/identity |
| Wipe/attempt reset policy | chưa mô hình hoá | Rules §4 chi tiết |
| Boss event type (phase/wipe/reset) | không nhét field lạ vào v2 | contract v2 proposal được duyệt |
| Coin band + gear roll vector | loot không grant được | economy/loot source |
| Sức chứa túi + policy đầy | không có `bag_full` | Rules §5 hoặc owner |
| Durability/binding/tradeable rule | chưa mutate | rules tương ứng |
| Công thức áp `weapon_power/armor/primary_stat` | equip chỉ metadata | Production_Rules §2 + DEC-023 |
| XP amount (`LEVEL_BAND_BASE`) | `applied=false` | Production_Rules |
| 12 slot trang bị (spec §3) vs enum 5 token đã duyệt | Quần/Găng bị từ chối, 6 phụ kiện gộp 1 slot | contract v2 cho slot enum |
| `C1-01` runtime record | portal/chapter không mở | Map Atlas/quest source |
| Party runtime + shared loot/credit | `SOLO_ONLY` | design + contract mới |
| Safe anchor/death penalty | death return chỉ là fixture | Rules/Map Atlas |

## 6. Bất biến vận hành

- Không bật gate trong `appsettings.json`; không tự đặt topology `REVIEWED`.
- Không đổi wire/schema khi chưa có proposal được duyệt; mọi response mới phải có schema + example + validation.
- Không bịa số: field thiếu ghi `blocked` kèm nguồn cụ thể (đúng như các bảng trên).
- `Server/Persistence*` thuộc QODER Remote #79; không ghi chồng.
- Không tự merge; Codex review. Branch stack PR #91 → #84 giữ nguyên.

## 7. Nơi tra cứu nhanh

- Hợp đồng: `Implementation/Contracts/P1/*.schema.json` + `Examples/`.
- Quest graph + blocked steps: `Implementation/Content/Examples/QuestDefinition/P00-0*.json`.
- Encounter proposal: `Implementation/Work_Orders/Proposals/QOD-18_Boss_MangCot_Encounter_vi.md`.
- Equip packet + đính chính slot: `Implementation/Work_Orders/Proposals/QOD-18_Equipment_Contract_vi.md` §6–§7.
- Tính năng/gate/limit chi tiết: `Server/Health/README.md`.
- Bàn giao E2E cũ (QOD-15) vẫn đúng phần profile default/dev; các phần damage/equip đã được cập nhật trong tài liệu này và README.
