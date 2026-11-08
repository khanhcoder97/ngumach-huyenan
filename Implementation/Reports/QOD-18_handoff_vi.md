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

## 8. Bổ sung work order 31 — đo ngày 2026-11-07

Mục 1–7 là lịch sử tại `20e98bf`; không dùng các tổng/claim route của ngày 01/11 làm hiện trạng. Delta này được build trên parent `1af85783b13fc8508a4744078168f72bc5a70830`, trong worktree `NGUMACHHUYENAN-qod21`, branch `qoder/qod-21-ben-mua-playable-alpha-20261103`, PR106. ExactSHA là commit chứa phần bổ sung này và được nêu trong comment checkpoint; CI của parent không chứng minh delta chưa commit. Work order đọc từ dispatch `2fc895d9495cb73b0f1b7cdd02e77dd7ea58ad69`, gói31 và `Tutorial_Transport_Review_Decisions_20261106_vi.md`. Không tự merge.

### 8.1 Delta đã kiểm và giới hạn

- Life ledger đã giữ đời/identity qua alive-returned/downed/reconnect churn ở checkpoint trước. Delta này sửa nghĩa vụ receipt: superseded life không là expiry; key đời đầu khi đang downed đời ba sau 303 return khác chỉ replay receipt cũ, không heal/move/revision/life mutation. Khác owner vẫn conflict. Cooldown 60 tick không mất vì churn; chỉ dọn deadline đã qua. Threshold 256 không là quota/retention guarantee; mọi receipt chưa có expiry được giữ. Đây không là durability 30 ngày hoặc 10.000-replay production proof.
- TALK receipt/conflict đứng trước node/reveal/range guards, kể cả khi chính credit trước đã đóng reveal gate. Fresh guards và narrative writer nằm dưới actor lock; `credited` đo counter delta, `appliedFlag` lấy từ kết quả domain. Không có reward/turn-in/chapter/teleport side effect. Các check same-key concurrency, changed-body unknown node, rejected Enter và replay sau READY/turn-in giữ assertion thực.
- C1 actor-aware read kiểm level authoritative + prerequisite; passive character read không tự mở AVAILABLE. Chỉ LOCKED/AVAILABLE đổi khi eligibility đổi; giữ revision/time nếu không đổi, giữ ACTIVE/READY/COMPLETED/FAILED. Core/HTTP accept đều có level guard. Level 10 sau completed tutorial vẫn LOCKED/refused, 11 vẫn cần prerequisite; upper band cũng enforced. Không thêm reason vào QuestState: reason chỉ có ở accept error hiện có.
- Portal route hai chiều dùng registry server-owned đã giao; receipt/conflict trước lookup, fresh map/floor/range/alive/chapter guards + teleport dưới actor lock. Cleanup chỉ sau successful teleport, **actor lock được thả trước engine cancellation**. Failed teleport giữ guard/counter/cast/event/position/revision và không ghi receipt. Same-key concurrent success chỉ một transition/cleanup. Không gọi transition+cleanup atomic với tick/new cast; HTTP alpha hiện chỉ đo refusal, không giả chapter grant để tạo positive journey.
- V2 world read chuyển vào `WorldSnapshotFactory.CreateV2`: capture self/viewer/map/floor/revision dưới actor lock rồi project AOI/boss sau khi thả lock. Probe chứng minh actor lock không giữ qua boss audience; worker thật đổi live actor nhưng response vẫn giữ captured view. Hai task đồng thời đọc 200 snapshot và tick boss có damage thực kết thúc trong watchdog 10s. Không gọi self+entities globally atomic, không đổi wire. Vòng lock cụ thể trước đó là actor→visibility→boss đối nghịch boss→actor; log timeout lịch sử không có dump monitor nên nguyên nhân chính xác vẫn unattributable, không quy lỗi C1 actor-aware read.
- Logging self-check trước đây có thể exit 0 nhưng thiếu aggregate vì async console logger chưa drain. `await app.DisposeAsync()` trong nhánh self-check khép logging trước exit. Không suy tổng từ những log cũ bị cắt, không hạ assertion/timeout để xanh.

### 8.2 Kết quả local của restored candidate

| Lệnh/profile | Kết quả đã đọc từ log hoàn chỉnh |
|---|---|
| Release build | 0 warning / 0 error |
| `Health.dll --self-check`, ba lượt | **608 passed / 0 failed / 608 total** mỗi lượt |
| E2E `default` / `dev` / `death-return` | **22 / 110 / 17**, mỗi profile một lượt |
| E2E `mob-combat` / `two-client` / `audience-gateoff` | **33 / 99 / 14**, mỗi profile một lượt |
| E2E `alpha-p00` | **132**, một lượt, campaign stop được assert |
| Smoke HTTP đúng workflow `server-smoke` | **358**, một lượt, boot từ Server/Health với QuestAccept/Interact/QuestTurnIn/CombatV2/CombatDamage ON |
| Contracts | **35 schema / 35 example**, PASS |
| Combat/social reconciliation | **21 independent refusal mutations**, PASS; source-only |
| Technical reconciliation | **64 constants / 18 files**, **5/13** canonical name matches; semantic/quota/retention gaps vẫn mở |
| Content/topology/narrative và runtime rebuild | PASS; synthetic 1 / reviewed 0; 76 beat / 20 scene / 63 shot / 378s chỉ là data |
| Map atlas | 56 rows / 37 agree / 6 known deltas / 13 absent / 0 problems |
| Placement migration | **349 records / 349 manifest / 46 maps / 349 shipped / 349 review-required / 0 approved XY / 0 runtime conflicts** |
| Python compile + `git diff --check` | PASS |

Negative controls đã build/run rồi **restore trước final build**:

```text
actor lock reintroduced around AOI projection:
FAIL world.snapshot_releases_actor_before_boss_audience_and_keeps_captured_viewer: held=True committed=False snapshot=MAP_BEN_MUA/181 live=MAP_BEN_MUA/181
FAIL world.concurrent_boss_impacts_and_snapshot_reads_terminate: finished=False reads=0 damagingImpacts=0
Service self-check: 606 passed, 2 failed, 608 total.

portal guard closed before a failing real teleport:
FAIL alpha.portal_failed_teleport_preserves_guard_cast_counter_and_position: code=invalid_map casts=1 window=False counter=False
FAIL alpha.portal_refusals_do_not_record_a_receipt: code=out_of_range
FAIL alpha.portal_concurrent_key_transitions_and_cleans_up_once: revision=2 cancels=3 casts=0
Service self-check: 605 passed, 3 failed, 608 total.
```

Commands đã chạy trên source candidate; Python shim + local .NET10 được thêm vào PATH trên Windows. CI dùng các lệnh tương ứng với SDK10/Python3.12:

```bash
dotnet build Server/Health/Health.csproj --configuration Release
dotnet Server/Health/bin/Release/net10.0/Health.dll --self-check
E2E_PORT=5101 bash Server/Health/Smoke/run_e2e_p1.sh alpha-p00
E2E_PORT=5102 bash Server/Health/Smoke/run_e2e_p1.sh default
E2E_PORT=5103 bash Server/Health/Smoke/run_e2e_p1.sh dev
E2E_PORT=5104 bash Server/Health/Smoke/run_e2e_p1.sh death-return
E2E_PORT=5105 bash Server/Health/Smoke/run_e2e_p1.sh mob-combat
E2E_PORT=5106 bash Server/Health/Smoke/run_e2e_p1.sh two-client
E2E_PORT=5107 bash Server/Health/Smoke/run_e2e_p1.sh audience-gateoff
python Implementation/Tools/validate_contracts.py
python Implementation/Tools/reconcile_combat_social_sources.py
python Implementation/Tools/reconcile_combat_social_sources.py --self-test
python Implementation/Tools/reconcile_technical_contract.py
python Implementation/Tools/validate_content.py
python Implementation/Tools/validate_topology.py
python Implementation/Tools/validate_narrative.py
python Implementation/Tools/reconcile_map_atlas.py
python Implementation/Tools/reconcile_placement_migration.py
python Implementation/Tools/build_world_records.py
python Implementation/Tools/build_world_entities.py
python Implementation/Tools/build_combat_mob_stats.py
python Implementation/Tools/build_loot_recipe.py
python Implementation/Tools/build_narrative_nodes.py
python -m py_compile Server/Health/Smoke/e2e_p1.py Server/Health/Smoke/smoke_p1.py Implementation/Tools/reconcile_combat_social_sources.py Implementation/Tools/reconcile_technical_contract.py
git diff --exit-code -- Implementation/Content/Runtime/world_records.json Implementation/Content/Runtime/world_entities_bm.json Implementation/Content/Runtime/combat_mob_stats_v1.json Implementation/Content/Runtime/loot_recipe_v1.json Implementation/Content/Runtime/narrative_nodes_v1.json
git diff --check
```

Log local `%TEMP%/wo31-final-selfcheck-{1,2,3}.out` có aggregate ở dòng1256; `%TEMP%/wo31-final-{alpha,default,dev,death,mob,two,audience}-http.out` đều có `E2E PASS`. Log không thay CI; CI exactSHA được công bố sau push. Smoke dùng đúng working-directory `Server/Health`, bật năm gate của workflow `server-smoke`, boot ReleaseDLL trên private port5108 rồi chạy `python3 Smoke/smoke_p1.py http://127.0.0.1:5108`; log `%TEMP%/wo31-final-smoke-http.out` ghi `PASS: 358 smoke checks`. Test chỉ dừng process do chính nó start; không đổi appsettings. Không dùng số453 từ root-working-directory để thay kết quả CI-shaped358.

### 8.3 Raw HTTP alpha, không dùng fixture grant

Từ run ở port5101, session `b9ec5df7f127498b91f43104d094bc31`. C1 accept tại NPC trả HTTP422; đọc QuestState trước/sau không đổi. Schema GET không có field reason:

```json
{"error":{"code":"prerequisite_not_met","correlationId":"aba89267-fbef-445e-9754-be2cd592ee5f","fieldErrors":["level"],"messageKey":"P1.ERROR.PREREQUISITE_NOT_MET","retryable":false},"requestId":"a1000000000000000000000000000001","result":{"objectiveCounters":{"OBJ_C1_01_REPRESENTATIVES":0,"OBJ_C1_01_TRIAL_REGISTRATION":0},"questId":"C1-01","revision":1,"state":"LOCKED","stepId":"STEP_C1_01_REPRESENTATIVES"},"schemaVersion":1,"serverTimeUtc":"2026-11-07T00:13:22Z","sessionId":"b9ec5df7f127498b91f43104d094bc31"}
```

TALK original HTTP200, replay sau rời NPC HTTP200, changed body cùng key HTTP409. Envelope hiện tại khác request/time; historical result giữ nguyên ngoài replayed. Quest revision giữ3, clue không credit class-confirm:

```json
{"requestId":"ea863c3ce49c4bc9b1480fad65d1cad3","result":{"appliedFlag":null,"credited":false,"eventId":null,"nodeId":"DLG_P00_05_CLUE","npcId":"NPC_TA_VAN_KHANH","objectiveId":null,"questId":"P00-05","replayed":false,"revision":3},"schemaVersion":1,"serverTimeUtc":"2026-11-07T00:16:48Z","sessionId":"b9ec5df7f127498b91f43104d094bc31"}
{"requestId":"977103084c5942fea53e5604781b1537","result":{"appliedFlag":null,"credited":false,"eventId":null,"nodeId":"DLG_P00_05_CLUE","npcId":"NPC_TA_VAN_KHANH","objectiveId":null,"questId":"P00-05","replayed":true,"revision":3},"schemaVersion":1,"serverTimeUtc":"2026-11-07T00:17:11Z","sessionId":"b9ec5df7f127498b91f43104d094bc31"}
{"error":{"code":"idempotency_conflict","correlationId":"10c3dfc4-97ef-454d-8871-ec97268ab9d5","fieldErrors":["idempotencyKey"],"messageKey":"P1.ERROR.IDEMPOTENCY_CONFLICT","retryable":false},"requestId":"03a5168eb088496ab3a8dfc05241caac","schemaVersion":1,"serverTimeUtc":"2026-11-07T00:17:11Z","sessionId":"b9ec5df7f127498b91f43104d094bc31"}
```

Measured narrative/escort/campaign output:

```text
P00-03 wave trial credited after 1 ticks of the 400 allowed (one windup is 24 ticks) over 1 in/out attempts, each followed by [24] ticks of windup waited for
P00-04 wave A activated after 0 ticks of the 1200 allowed (sourced traverse: 38 WU at 3 wu/s = 254 ticks)
P00-04 AOI: row left at x=92.60000000000048, absent at 92.5530138,60.2744346, returned x=104.15000000000092
P00-04 wave B activated after 0 ticks of the 1500 allowed (sourced traverse: 40 WU at 3 wu/s = 267 ticks)
portal: 422 out_of_range naming [] from 282.5 WU away from TP_BM_THANH_LAC at (348,0)
profile=alpha-p00 chain=P00-01..P00-05 boss=KILLED fragment=OK wave_trial=OK escort=A+B loot=PAID v2_inventory=OK talk=ROUTE_LIVE_NO_NODE_FOR_TRIAL_NPC c1_01=LOCKED second_client=ISOLATED
PASS: e2e_p1 (alpha-p00) 132 checks against http://127.0.0.1:5101
```

Zero wait ticks ở checkpoint nghĩa state đã đạt khi bắt đầu đợi, không chứng minh travel tức thời. Không nới bound/sửa assertion. Không suy từ boss+fragment sang đã class-confirm/turn-in/chapter/portal thành công.

### 8.4 Nguồn độc lập và artifact còn cần quyết định

`reconcile_combat_social_sources.py` đọc Content Bible, Production Rules, Guild Social Spec, Currency CSV, Character/Equipment spec và các ClassDefinition examples. Output derived: resources5, resource-skill-cells9, selected-status-rows4, treasury-ledgers2, class-examples1; bốn example lớp còn thiếu được nêu tên. Resources0–5; death/map reset0; đổi target chỉ reset Mộc Tiêu. Bible slow boss10%/PvP25% đối nghịch Rules boss immune/PvP30%/global50%; shield Bible strongest-global đối nghịch Rules same-skill strongest + sources coexist + total30%HP/PvP20%. Script ghi divergence, không tự chọn luật.

Guild create source ghi level10/20.000COIN/10huy hiệu nhưng chưa có badge ID. Donation5.000COIN/member/day và30materialunits/day là giới hạn eligible guild XP; contribution currency có daily cap5.000 **points** và exchange1.000COIN:1point, không cùng đơn vị/phạm vi. Hai treasury ledger names chưa có currencyId mapping. Currency/ClassPassive loaders hiện có, không gọi catalog là caps/passive/stat/social service đã áp. Checkout đúng có bảy SkillDefinition examples; design-only VFX metadata không là approval mechanics. Không dùng kết quả search trỏ checkout gốc để bịa thiếu loader hoặc số skill.

Artifact được giao theo work order, không tạo việc tự đề xuất:

- `Implementation/Work_Orders/Proposals/QOD-25_Error_Semantics_Capacity_RateLimit_Packet_20261107.md` §7: full historical DeathReturnResult + before/after life + global key owner/hash + Committed/Tombstoned semantics; Remote thiết kế CAS/fencing/atomic state+revision+receipt+ledger/outbox, không writer thứ hai hoặc write-after-mutation crash-safe claim. Sketch bool ở mục4 là lịch sử đã bị đính chính.
- `QOD-28_MapViewed_Acknowledgement_Packet_20261107.md`: separate questId-only acknowledgement, không GET/portal/TALK credit. C1 pack hiện chỉ hai TALK objectives, thiếu canonical MAP_VIEWED ID/type/order/floor/migration; chưa schema/gate/handler.
- `QOD-29_Escort_Provenance_Packet_20261107.md`: additive owner-only sample với life/attempt/instance/floor/actor identity cùng coordinates. Canonical entity life/revision không giả owner life/movement revision; attempt hiện chỉ"1". Packet chờ approval, không đổi frozen WorldSnapshotV2.
- `QOD-27_Pet_Elite_Passive_Decision_Packet_20261107.md` đã giao trước: source conflict/ảnh hưởng/test migration, không tự chọn cân bằng. Các dependency stats/economy/capability/attempt/durability còn mở.

Blocker thực của tutorial: production narrative không có node cho `NPC_CLASS_TRIAL`; không edit docs/production hoặc mint node. Full HTTP finale/target-map TALK/C1 arrival còn chưa nghiệm thu. Shared two-owner P00-02 capacity đã đo 2/4 mỗi owner trên một nhóm chung ba body; không tự đổi spawn/credit. Portal lifecycle cleanup chưa globally atomic, escort provenance/MAP_VIEWED chưa duyệt, Health không durable. Scope diff giữ mọi production gate OFF, old schemas frozen, canonical XY/topology không đổi; không đụng Shared/ClientCore/ClientGodot/art/Tools/ProducerReview/docs/production/Server-Persistence. Không gọi toàn gói31 hoặc MMO đã hoàn tất từ checkpoint này.
