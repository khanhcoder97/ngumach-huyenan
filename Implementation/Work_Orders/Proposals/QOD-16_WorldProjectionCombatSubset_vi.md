# QOD-16 — World projection entity read model + combat subset (QOD-B)

**Trạng thái:** ĐỀ XUẤT, chờ owner duyệt trước khi đổi wire/schema hoặc bật gate runtime.
**Issue:** #41. **Nguồn số:** `P1_Design_Resolution_20261029_vi.md`, `Production_Rules_Complete_v1_vi.md` §1–3, `Art_Entity_Weather_UI_Visual_Bible_vi.md` §12, `Implementation/Content/DesignBaselines/completion_v1.json`, `World_Spawn_Gathering_Manifest_vi.csv`.

## 1. Audience và hiện trạng

- **Audience:** client adapter (Codex PR #51) cần entity read model để target/display; `WorldSnapshotFactory` hiện trả `Entities = Array.Empty` dù registry đã có 27 instance (8 NPC, 8 MOB, 2 BOSS, 5 GATHER_NODE, 4 INTERACTABLE). Client không được tự dựng quái/NPC từ tên sprite hoặc placement.
- **Combat hiện tại** chỉ phát `combat.effect` (lifecycle gating + cooldown), không có HP/damage/death. `CombatEventTypes` đã định nghĩa `combat.hit`/`combat.death` nhưng chưa dùng. Nguồn số đã khóa theo design resolution → đây là lúc đóng khoảng trống QOD-11/12.

## 2. World projection (đóng QOD-11)

Projection từ `WorldEntityRegistry` cho map của session, mỗi instance một entity read model:

| Field | Nguồn | Ghi chú |
|---|---|---|
| `entityId` | registry | ổn định theo spawn record |
| `kind` | registry | MOB/BOSS/NPC (+GATHER_NODE/INTERACTABLE nếu owner chọn Q6) |
| `mapId`/`floorId` | registry | `floorId` là field mới trong schema (hiện chỉ có ở registry) |
| `x`/`y` | registry | vị trí hiện tại (mob di chuyển theo tick) |
| `state` | registry + MobLifecycleService brain | ánh xạ registry state + brain state sang enum wire |
| `hp`/`maxHp` | mob stat bundle (mục 3) | NPC invulnerable: hp=0, maxHp=0 |
| `revision` | `WorldEntityInstance.Revision` | field mới trong schema; bump khi state/position đổi |
| `lifeId` | mới, tăng đơn điệu mỗi respawn | field mới; để phân biệt instance qua death/respawn |

**NPC invulnerable:** NPC không vào damage pipeline, không bị target bởi combat, không phát death; hp/maxHp=0 trong projection (theo Art Bible §13). `TryResolveTarget` từ chối kind NPC.

**Visibility policy:** full-map projection (map nhỏ, 27 entity); culling theo khoảng cách để sau khi có yêu cầu client, không nằm trong PR này.

## 3. Numeric export có version và gate (không copy thẳng vào production config)

- **Bundle mới:** `Implementation/Content/Runtime/combat_mob_stats_v1.json`, sinh bởi `Implementation/Tools/build_combat_mob_stats.py` deterministic (cùng input → cùng digest) từ Art Bible §12 (HP/ATK/DEF multiplier, hệ số đòn) + `completion_v1.json` (base level formula) + spawn manifest (level band, respawn, loot table). Mỗi field có `sourceRef`/`version`.
- **Base cấp L:** HP=120+24L, Attack=10+2L, Defense=2+0,8L (Art Bible §12). Archetype multiplier áp **một lần**; elite ×6/×1,6/×1,8; boss Mãng Cốt HP×35/ATK×2,0.
- **Quantization:** HP là integer (bảng design resolution đã chọn số nguyên ở cấp 5); ATK/DEF giữ số thập phân suốt công thức, chỉ floor một lần ở Final damage.
- **Activation:** `DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION`; loader đọc bundle chỉ khi gate `P1:CombatDamage:Enabled=true` (OFF mặc định). Startup log `DEV STUB` khi bật, giống các gate hiện có.

### Vấn đề cần quyết định (Q1 — mob level theo spawn)

Manifest chỉ có `character_level_min/max` (band 1–10), **không có level cho từng spawn**. Theo design resolution "dùng level của spawn, không đoán từ sprite"; không lấp bằng số tùy ý. Đề xuất: prototype dùng bảng tham chiếu **cấp 5** chính owner đã chốt trong design resolution (CARPLING 192/15/4,2; WATERROOT 264/20/6,6; SHORE_STALKER 216/23/4,8; elite 1152/24/7,56) gắn nhãn `REFERENCE_L5` trong bundle — không gọi là cân bằng final. Nếu owner có nguồn level/spawn khác, Qoder thay nguồn.

### Actor stats

Profile baseline `completion_v1` (STR/INT/AGI/VIT/LUK=5 → ATK20/Armor10, crit 0,0525, accuracy 0,0025, dodge 0,0015) dùng **chỉ cho phép tính damage** trong subset. HP/MP session giữ fixture hiện tại (HP100/MP50) — migration refill là proposal riêng theo design resolution §4, không đổi snapshot im lặng.

## 4. Combat subset (đóng QOD-12b)

Gate `P1:CombatDamage:Enabled` (OFF mặc định). Pipeline theo Production_Rules §2, test oracle bắt buộc phải tái tạo đúng ví dụ design resolution: attack20/coeff1,5/rank1/armor10 → raw30 → `floor(30×100/110)=27`; crit `floor(…×1,5)=40`.

1. **Guard** (đã có): session/owner, alive, class/loadout/rank, target/floor/range/LOS, MP, cooldown. Rejected không trừ cost/revision/sequence.
2. **Hit roll:** `clamp(0,90 + accuracy − dodge, 0,05, 0,98)`; **crit roll:** `clamp(0,05 + 0,0005×LUK − critResist, 0, critCap)`; RNG seeded `castId|targetId|hitIndex`, seed version lưu để audit.
3. **Raw** = (attack + flat) × coefficient × rankMultiplier × (1 + sumDamageBonus). Mode coefficient thay thế nhau: PvE dùng 1,8/1,5/1,9; không nhân thêm PvP 0,65.
4. **Mitigation** = 100/(100 + max(0, armor)); element = 1 − clamp(resist, 0, 0,5); crit ×1,5; DR bucket cap 0,8.
5. **Final** = max(1, floor(raw × mitigation × element × crit × (1 − DR))). Shield hấp thụ trước HP (subset hiện không có shield nào; bước giữ identity và có sẵn cho status registry sau).
6. **Death:** một lần cho mỗi `lifeId`; death event tham chiếu `deathEventId`; kill credit = threat cao nhất (HPDamage + 0,5×heal + 0,3×shieldAbsorb, tie-break entityId).

### Phạm vi skill (đúng supported subset 3 skill)

- **SK-MK-01** (SELF, Phản Quang): design resolution §4 ghi rõ counter/giảm sát thương "thiếu precision" → **giữ nguyên không gây damage** trong subset; gửi case cần quyết định, không bịa số. Phần còn lại của combat subset không phụ thuộc vào nó.
- **SK-MK-02** (DASH): di chuyển; endpoint không được đảm bảo nếu sweep chặn (đã chốt ở design resolution §3.2); không gây damage theo definition hiện có.
- **SK-MK-03** (CONE 4,4WU/100°/cap5): multi-hit **0,45/0,55/0,90** từng nhát (tổng = 1,9 = coefficient PvE; không áp 1,90 ba lần). Cần origin/facing snapshot từ cast start (design resolution §3.2). Target selection trong cone thay `targetId` hiện tại → đây là thay đổi domain, không đổi wire command.
- **Đánh thường:** 3 nhát ×100% attack, melee 4WU/quạt90°/1 target, windup0,15/hit0,10/recovery0,25 (Rules §2). Cần cho vòng lặp săn quái hoàn chỉnh; nếu owner muốn skills-only thì cắt.

### Mob gây damage lên player

Mob attack = Attack × hệ số đòn trong Art Bible §12 (đớp 0,8×, nhảy 1,1×, roi rễ 1,0×, chồi đất 1,5×…), telegraph ≥0,45s thường/≥0,7s nặng. Player armor theo baseline (10). Player HP clamp 0; HP0 → hiện hành: mob AI bỏ qua player chết, hồi máu nằm ngoài subset (death-return teleport đã có).

### Boss — blocked trong subset này

Mãng Cốt có windup/shape/distance/hit/recovery/CD (Rules §4) nhưng thiếu `phaseGuard`/`interruptible` → theo Rules §4 "trường thiếu làm export fail, không dùng hồ sơ khác thay". Boss giữ invulnerable (như NPC) trong subset; HP×35/ATK×2,0 vẫn export có nhãn `BOSSDATA_BLOCKED` để không chặn bundle.

### Loot/kill reward — blocked, câu hỏi riêng

Manifest ghi "100% Đồng theo band; 12% rơi 1 vật liệu trong pool" nhưng **quy tắc band tiền** và **roll seed cho 12%** chưa có nguồn → không grant loot trong subset; kill credit + death event đã đủ để quest KILL objective (QOD-C) hoạt động sau này. Case gửi owner (Q4).

## 5. Wire delta (chỉ áp dụng sau khi proposal được duyệt)

> **Cập nhật 2026-10-30:** owner đã duyệt hướng v2 tách biệt tại work order 08 §2 (Q3) — phần dưới giữ làm bối cảnh, thiết kế đã duyệt nằm ở §9.

1. **`WorldSnapshot.schema.json` v2:** entity thêm `revision` (≥1), `floorId`, `lifeId`; enum `kind`/`state` mở rộng theo chính sách visibility (Q6).
2. **Damage evidence:** design resolution cấm dùng `combat.effect` làm bằng chứng damage. Đề xuất **`CombatCastEvent.schema.json` v2**: `CAST_IMPACT` thêm `hitIndex`, `amount`, `absorbed`, `hpDamage`, `hit`/`miss`, `targetRevision`, `sourceRevision` (revision ghi rõ chủ aggregate — design resolution §3). Transport: mở trong response `/p1/combat` (field `hits[]` mới, legacy `combat.effect` giữ nguyên) — Q3 hỏi owner chọn phương án.
3. `CombatEvent`/`CombatInput`/`Envelope` không đổi; `CombatEventPayload.Damage/Hit` (đang optional, chưa dùng) **không** được điền như bằng chứng damage.

## 6. Non-goals

Status/buff/shield registry (Rules §3), Phản Quang counter, boss encounter (telegraph/phases), XP/level (chưa có hệ XP — không giả XP), loot grant, player respawn semantics, transport realtime. Mỗi phần thiếu precision ghi `unsupported`/`blocked` có case, không điền số giả.

## 7. Kế hoạch rollout

- **Pha 1 (chờ duyệt, không đổi wire):** skill loader nạp coefficients/angle (domain); `combat_mob_stats_v1.json` + builder + loader có gate OFF; `DamageFormula` domain thuần + self-check tái tạo oracle 27/40 và các case mitigation/elite/boss scaling; projection entity read model internal (factory đã có shape) — fixture ghi rõ `REFERENCE_L5`.
- **Pha 2 (sau duyệt):** wire delta mục 5 + bật gate trong smoke dev profile + e2e dev scenario (giết mob, death/respawn, snapshot entities) + docs/README.
- CI: self-check/smoke bổ sung chạy kể cả khi gate OFF (domain tests), smoke dev chạy khi ON.

## 8. Câu hỏi gửi owner

> **Đã được owner trả lời 2026-10-30** — xem §9. Giữ nguyên câu hỏi để tra cứu.

1. **Mob level theo spawn:** dùng bảng REFERENCE_L5 của design resolution làm baseline prototype, hay owner có nguồn level/spawn khác?
2. **Đánh thường:** đưa basic attack 3×100% vào subset (cần cho vòng săn quái) hay giữ skills-only?
3. **Transport damage:** mở `hits[]` trong response `/p1/combat` (đề xuất) hay chỉ qua snapshot entity hp polling, hay mở transport `CombatCastEvent` riêng?
4. **Loot:** nguồn quy tắc "Đồng theo band" và roll 12% material (seed/rounding) lấy từ đâu, hay để QOD-C/D?
5. **Phản Quang:** case counter/DR còn thiếu — chờ owner quyết định hay Qoder soạn proposal con riêng?
6. **Snapshot visibility:** entities gồm cả GATHER_NODE/INTERACTABLE (27 instance đầy đủ) hay chỉ MOB/BOSS/NPC?

## 9. Pha 2 — quyết định owner (2026-10-30) và thiết kế v2 đã duyệt

Owner trả lời 6 câu hỏi tại `08_QODER_PLAYABLE_SLICE_20261030.md` §2. Tóm tắt quyết định và thay đổi so với đề xuất đầu:

- **Q1:** REFERENCE_L5 chỉ là DEV fixture cho 3 archetype hiện có; không gán cấp 5 cho mọi spawn/46 map. HP sau multiplier không nguyên → ghi unresolved quantization hoặc proposal riêng trước khi rollout ngoài fixture; ATK/DEF giữ thập phân, floor một lần ở Final. Migration actor stats/HP/MP là milestone riêng. Không gọi fixture HP100/MP50 + công thức tham chiếu là cân bằng đã duyệt.
- **Q2:** Có basic attack trong subset Minh Kiếm: mỗi nhát 100% attack, range 4 WU/quạt 90°/cap 1, windup 0.15s/hit 0.10s/recovery 0.25s, combo timeout 1.5s sau recovery, ceil theo tick 20 Hz. Một lệnh = một nhát; `BASIC_ATTACK` tách khỏi active skill trong DTO, không tạo `SK-MK-07` giả.
- **Q3:** Typed combat events có version + snapshot reconciliation, namespace v2 opt-in: `/p1/v2/world/{sessionId}`, `/p1/v2/combat`, endpoint đọc event có cursor. Không chèn `hits[]` vào v1 (`additionalProperties=false`); response chỉ trả event **đã xảy ra**; impact chạy ở tick thật; cursor monotonic, gap/overflow báo resync; replay không tạo cast/event/death mới.
- **Q4:** Loot: một roll 12% (`group_chance_bps=1200`) mỗi group rồi SELECT_ONE theo weight từ `Loot_Recipe_Reward_Production_Data_vi.csv`; coin band chưa có giá trị executable → mob-loot grant OFF, chỉ làm exporter/RNG/eligibility/ledger tests + proposal phần thiếu. XP đã có nguồn (`level_progression_v1.json` + Production Rules §1; oracle L1: 175/43/96/21; mob L5 = 20 trước modifier), triển khai phải transaction reward/level/ledger, chỉ `applied=true` khi commit thật.
- **Q5:** Phản Quang tách proposal con (guard 0.4s, hướng, một counter/cửa, +2 Kiếm Ý, source chết cùng tick, câu DR hụt 20% còn thiếu); counter/DR giữ `unsupported`, chỉ emit `COUNTER_CONFIRMED` sau khi duyệt. Basic/MK03/mob pipeline và quest tests chạy độc lập.
- **Q6:** Snapshot v2 gồm MOB/BOSS/NPC/GATHER_NODE/INTERACTABLE **sau audience filter**: AOI PvE enter 40 WU, leave 48 WU (hysteresis 8, nguồn Online_Persistence_Release_Complete §2), cùng instance/map/floor/phase trước AOI; boss blocked có `healthState: BLOCKED` + `targetable: false` (không hiển thị như đã chết); NPC `INVULNERABLE`; availability node theo người gọi, không lộ quest flag/inventory/claim của người khác; v1 không đổi.

### 9.1 Contracts v2 (đã thêm)

- `WorldSnapshotV2.schema.json` + example: `schemaVersion: 2`, `mapInstanceId` (`MAP_X#n`), `floorId`, `phase` (DEV `OPEN_WORLD` cho tới encounter phase của QOD-19), `audience {aoiEnterWu: 40, aoiLeaveWu: 48}`, entity read model đầy đủ (kind/state/healthState/targetable/availability/revision/lifeId/hp/maxHp).
- `CombatInputV2.schema.json` + example: `actionKind` `BASIC_ATTACK | SKILL`; `skillId` chỉ cho SKILL; `targetId` tuỳ chọn (auto-select trong cone theo design).
- `CombatEventV2.schema.json` + example: `CAST_START | IMPACT | MISS | CANCEL | END | DEATH` với `castId`/`targetId`/`targetLifeId`/`hitIndex`/`mapInstanceId`/`floorId`/`sourceRevision`/`targetRevision`/`cursor`/`result{hit,crit,immune,amount,absorbed,hpDamage}`.
- `CombatEventPageV2.schema.json` + example: `nextCursor`, `resyncRequired` + `resyncReason` (`CURSOR_TOO_OLD | BUFFER_OVERFLOW`), cursor tăng nghiêm ngặt.
- `validate_contracts.py` mở rộng: `entityId` dạng `ENT_...` resolve theo runtime bundle (27 instance) thay vì cột template manifest; semantic checks cho 4 schema mới (AOI constants, NPC/boss policy, actionKind↔skillId, IMPACT/MISS/DEATH fields, cursor/resync). v1 giữ nguyên.

### 9.2 DEC-022 — Phản Quang đã chốt (2026-10-30)

Owner/Codex chốt precision còn thiếu của SK-MK-01 tại `docs/production/P1_Guard_Precision_20261030_vi.md` + bundle máy đọc `Implementation/Content/DesignBaselines/p1_guard_precision_v1.json` (`DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION`, DEC-022) — không cần hỏi lại hướng/thời lượng 20%. Phạm vi P1 PvE Minh Kiếm; không đổi wire v1.

- **Guard:** cast accepted tại tick T → guard active `[T, T+8)`; hit T+7 đỡ được, T+8 không. 70% DR cho direct damage từ vùng trước; vùng gắn chân defender hiện tại + facing snapshot cast start, cone 120°/4.4 WU, mép inclusive, hai chân trùng tọa độ tính trong vùng. Một confirmation/guard (`guardCastId`), `+2` Kiếm Ý cap 5; hit sau vẫn DR nhưng không thêm resource/counter.
- **Whiff:** hết tự nhiên `[T+8, T+28)` (20 tick), defender còn sống, chưa confirmation → DR 0,20 theo bucket thường; không áp khi chết/đổi map/session end/hard-control/dodge-cancel; cùng skill refresh không cộng dồn.
- **Counter:** impact ở tick kế tiếp, target duy nhất = nguồn hit đã confirmation (không retarget), attack snapshot lúc guard accepted, coefficient theo `SkillDefinition` mode, roll hit/crit riêng, recheck sống/instance/floor/hostile/range/cone/LOS/invulnerability; `NO_COUNTER_TRIGGER` chặn vòng phản, không tốn thêm MP/CD/resource, không refund, không hard-control boss.
- **Ordering:** impact sắp theo `(scheduledTick, castStartTick, castIdOrdinal, hitIndex, targetIdOrdinal)`; confirmation sau damage/survival trước impact kế; source chết trước lượt direct melee → cancel impact còn lại (P1 direct melee).
- **Wire v2:** `COUNTER_CONFIRMED` là semantic "đỡ thành công + reserve đúng một counter", **không** phải counter damage (không mang `result`); counter impact/miss/cancel là IMPACT/MISS riêng. Reconcilation từ snapshot là silent, không replay audio/VFX. v1 không đổi.
- **Oracle khóa:** raw30/armor10 → thường 27, guard70% 8, whiff20% 21, DR cap80% 5; counter 20×1,8 → 32, crit 49.
- **Đã thêm trong nhánh này:** `GuardPrecisionLoader` (đọc/gate/validate bundle, fail-fast cả oracle arithmetic), `GuardTimeline` (window/whiff/cone/DR bucket/ordering thuần), `CombatDamageFeature.GuardPrecision` (cùng gate `P1:CombatDamage`, OFF mặc định), self-check 11 test mới, enum `COUNTER_CONFIRMED` trong 2 schema v2. **Chưa** có state machine/HTTP runtime — thuộc QOD-17; gate chỉ bật sau khi có test state machine/concurrency/HTTP và exact SHA.

### 9.3 Event store v2 — thiết kế reliable event read

Theo Q3: response command chỉ trả event **đã xảy ra**; impact tương lai append ở tick thật. Store nội bộ (chưa nối HTTP):

- **Cursor:** mỗi session một stream, cursor bắt đầu 1 và tăng đơn điệu theo thứ tự append; event lưu kèm cursor. `nextCursor` = cursor cuối đã cấp (0 nếu chưa có). Client đọc `?cursor=n` nhận các event `> n` theo thứ tự, tối đa `MaxPageSize`.
- **Bounded buffer:** `P1:CombatEventStream { CapacityPerSession = 512, MaxPageSize = 200 }` — DEV budget, validate `1 ≤ MaxPageSize ≤ CapacityPerSession`. Vượt capacity thì evict cũ nhất và **báo resync thay vì drop im lặng**.
- **Resync:** `afterCursor < oldest-1` → `BUFFER_OVERFLOW`; `afterCursor > lastCursor` (client cũ hoặc stream đã reset sau reconnect) → `CURSOR_TOO_OLD`; cả hai trả `events: []`, `nextCursor = lastCursor`, client reconcile snapshot rồi đọc tiếp. `RemoveSession` giải phóng buffer và reset cursor cho lifetime mới.
- **Idempotent append:** cùng `eventId` append lại là no-op trả bản đã lưu (replay command không tạo event mới); idempotency command-level vẫn là guard chính.
- **Typed invariants:** `eventId`/`castId` hex32, `actorId` CHR_*, `mapInstanceId` `MAP_X#n`; `IMPACT` cần target/lifeId/hitIndex + `hit:true`, `MISS` + `hit:false`, `DEATH` cần target/lifeId, `COUNTER_CONFIRMED` không mang `result`; result damage không âm và `absorbed + hpDamage ≤ amount`.
- **Concurrency:** lock theo stream khi append/đọc — cursor không trùng, đọc không thấy event chen giữa; self-check barrier 4 thread × 25 append → 100 cursor 1..100 liên tục.
- **Không thuộc phạm vi:** endpoint `/p1/v2/events` (chờ QOD-17 tick engine), replay audio/VFX (reconcile silent), persistence (PostgreSQL proposal QOD-20).

### 9.4 AOI projection — thiết kế audience v2

Theo Q6: snapshot v2 chỉ gửi entity sau filter audience; internal candidate vẫn đủ map (fixture 27), client không nhận 27.

- **Phạm vi:** cùng `mapInstanceId` (`MAP_X#1`, DEV placeholder tới khi có multi-instance), `floorId`, `phase` (`OPEN_WORLD` DEV placeholder tới encounter phase của QOD-19) — kiểm trước AOI.
- **AOI + hysteresis:** enter ≤ 40 WU, leave ≤ 48 WU (8 WU, nguồn Online_Persistence_Release_Complete §2); session giữ tập visible của lần đọc trước nên entity đã thấy chỉ rơi khi vượt 48, entity mới cần ≤ 40. `RemoveSession` quên hysteresis để reconnect vào lại theo bán kính 40.
- **Policy từng kind:** NPC `INVULNERABLE`/`targetable:false`/hp0; boss blocked `BLOCKED` (không hiển thị `DEAD`) và không targetable; MOB hp theo `REFERENCE_L5` (elite suffix áp multiplier), `ALIVE`/`DEAD` từ registry+brain, targetable khi còn sống; GATHER_NODE/INTERACTABLE chỉ lộ `availability` theo người gọi (`AVAILABLE`/`COOLDOWN`, claim window per-character; shared interactable theo state chung), không lộ quest flag/inventory/claim người khác.
- **Không thuộc phạm vi:** endpoint snapshot v2 (đi cùng QOD-17), culling theo tầm nhìn/che khuất, multi-instance/phase thật, reconcile audio/VFX (silent), persistence.

### 9.5 Endpoint wiring — v2 opt-in (world, combat, events)

- Gate `P1:CombatV2:Enabled` (OFF mặc định); khi bật map `GET /p1/v2/world/{sessionId}`, `POST /p1/v2/combat`, `GET /p1/v2/events/{sessionId}?cursor&max`. Khi tắt route không tồn tại; v1 giữ nguyên. Bật log `DEV STUB`.
- **World:** `WorldSnapshotV2` từ session + `WorldAoiProjectionService` (audience 40/48, entity read model đúng policy Q6); revision/serverTick theo session và clock 20 Hz.
- **Combat:** envelope v2 (`schemaVersion: 2`, requestId/idempotencyKey hex32, characterId khớp session qua `X-Session-ID`); payload `BASIC_ATTACK|SKILL` + aim; **accept-only**: guard class/sequence/cooldown/MP + idempotency, trả castId/cost-CD/events đã xảy ra (`CAST_START`), **không** trả impact tương lai và chưa gây damage (QOD-17). BASIC_ATTACK chỉ Minh Kiếm, 0 MP, cooldown recovery 0.25s (Rules §2); skill dùng CD/MP từ `SkillDefinition`.
- **Events:** page `{nextCursor, resyncRequired, resyncReason?, events}` từ `CombatEventStore`; cursor lỗi → 400; cursor cũ/buffer overflow → resync không kèm event (client reconcile snapshot, silent).
- **Bằng chứng:** self-check 10 test combat v2; smoke HTTP (server-smoke gate ON) kiểm world/AOI/NPC/mob hp192, basic accept + replay + conflict, skill MP38, cooldown/stale, events 1..2, cursor=1, resync `CURSOR_TOO_OLD`, cursor âm 400. Chưa có impact/damage/kill; không đổi v1.

### 9.6 Tick engine lõi (QOD-17)

- Accepted cast → schedule trên 20 Hz (`WorldTickBackgroundService`), impact ở tick thật: basic windup 0.15s (tick+3), coefficient 1.0, range4/quạt90°/1 target; MK03 3 nhát tick+2/+5/+8, hệ số 0.45/0.55/0.90, cone4.4×100°, cap5; MK02 không damage; MK01 giữ guard window (counter runtime increment sau).
- Damage: baseline completion_v1 nhãn DEV (attack20/armor10/acc0.0025/crit0.0525) + defense mob REFERENCE_L5 qua `DamageFormula`; oracle basic 19 (CARPLING), MK03 8/10/17; RNG có kênh `hit`/`crit` riêng để không dùng chung một uniform; replay schedule theo castId không resolve hai lần.
- Mob HP theo `lifeId` (`MobCombatStateStore`); chết ×1/life, `DEATH` event, kill credit = nguồn HPDamage kết liễu (DEV policy) gửi KILL quest event keyed deathEventId; respawn bump lifeId + HP mới; impact recheck alive/target.
- **Spawn groups:** `build_world_entities.py` mở đủ thành phần manifest — 8 nhóm/25 mob member (member 1 giữ entityId cũ, member sau `_M2..`), `groupId`/`memberIndex`/`groupRespawnSeconds`, composition round-robin là DEV fixture có nhãn; `MobSpawnGroupService` chỉ respawn cả nhóm sau khi clear (partial death giữ nguyên), mỗi member bump lifeId; bundle 44 entity/22 template, world record vẫn 352 (record theo manifest row).
- **Chưa làm (increment kế):** XP. Mob AI telegraph/attack/recovery + mob damage: xem §9.8; guard/whiff/counter DEC-022 runtime: xem §9.9.

### 9.7 Loot system (QOD-17, dry-run)

- Exporter deterministic từ `Loot_Recipe_Reward_Production_Data_vi.csv` (LOOT_ENTRY) → `Implementation/Content/Runtime/loot_recipe_v1.json`: 57 source / 184 entry, `grantEnabled=false`, `grantBlockedReason=COIN_BAND_MISSING` (CSV chỉ có currency cho PvP/dungeon/raid/tower/guild, **không có band Đồng cho mob**), CI drift-check.
- Luật roll đúng Q4: **một roll 12% mỗi group** (`group_chance_bps=1200`), sau đó `SELECT_ONE` theo weight; RNG server versioned `loot-rng-v1`; cùng `killKey` cho cùng receipt; `LootReceiptLedger` dedupe retry; quantity trong `[min,max]` (P1 hiện 1..1).
- Mapping P1 có provenance: `MOB_CARPLING`→`LT_MOB_CARPLING`, `MOB_WATERROOT`→`LT_MOB_WATERROOT`, `MOB_SHORE_STALKER`→`LT_MOB_SHORE_STALKER`, elite→`LT_MOB_SHORE_STALKER_ELITE`, `BOSS_MANG_COT`→`LT_BOSS_MANG_COT_QUEST` (QUEST placement, boss vẫn BOSSDATA_BLOCKED).
- **Grant OFF:** receipt chỉ dry-run, không chạm inventory/currency; kill progress độc lập. Mở grant cần reward bundle đầy đủ + review (proposal riêng khi coin band có nguồn).

### 9.8 Mob AI telegraph/attack/recovery + mob damage lên player (QOD-17)

- **State machine theo Art Bible §6:** `MobLifecycleService` thêm `TELEGRAPH`/`RECOVER` (chu trình IDLE→AGGRO→CHASE→TELEGRAPH→ATTACK→RECOVER→RETURN/DEAD). Trong tầm `AttackRangeWu`: CHASE (hết cooldown) mở TELEGRAPH đặt `ImpactAtUtc = now + TelegraphSeconds`; tới `ImpactAtUtc` phát `TELEGRAPH→ATTACK` (frame va chạm) rồi `ATTACK→RECOVER` ngay cùng tick, đặt `RecoverUntilUtc` và `NextAttackAtUtc = impact + AttackCooldownSeconds`; hết recovery về CHASE. Mất target hoặc vượt leash → RETURN và **hủy pending impact** (không có ATTACK event → không damage, không kill credit). Không di chuyển trong TELEGRAPH/RECOVER — cửa đọc đòn là phần chính của telegraph.
- **Wire delta (chỉ v2, chưa merge):** `WorldSnapshotV2.entities[].state` thêm `TELEGRAPH`/`RECOVER`; `validate_contracts.py` ràng buộc MOB/BOSS chỉ dùng state chu trình quái (và alive→targetable, dead→không targetable), kind khác chỉ `ACTIVE/AVAILABLE/DEPLETED`; example thêm một CARPLING `TELEGRAPH` hp192 để client (Codex) có hình thái cue. **Không** có event type mới: `CombatEventV2` bắt buộc `actorId ^CHR_` + `castId` hex32 nên mob→player damage không đủ điều kiện — bằng chứng là snapshot `self.hp` + `self.revision` (Q3 đã chốt reconcile-by-snapshot). Event `ENEMY_CAST` là proposal contract riêng.
- **Damage:** `MobAttackService.ApplyImpacts(events, players)` chỉ chạy khi `P1:CombatDamage:Enabled=true`; chọn đòn **đầu tiên** của archetype (= cột "Đòn thường" Art Bible §12), attack `REFERENCE_L5` (elite áp ×1,6 ATK), raw = attack × hệ số đòn, mitigation = 100/(100+armor10 baseline completion_v1), không element/crit/DR. Oracle: CARPLING 15×0,8=12 → **10**; WATERROOT 20×1,0 → **18**; SHORE_STALKER_ELITE 23×1,6×1,0=36,8 → **33**. Impact recheck tại frame: mob còn ALIVE, target còn session, `Hp>0`, cùng map/floor, còn trong `AttackRangeWu` → outrun telegraph là `TARGET_OUT_OF_RANGE_AT_IMPACT` (không damage). HP clamp 0 và `PlayerSession.Revision++` trong `lock(SyncRoot)` (revision là aggregate version của session, theo design resolution §3).
- **Nhãn DEV fixture / nguồn thiếu:** `TelegraphSeconds=0.45` và `RecoverySeconds=0.5` là fixture (mặc định lấy từ CARPLING "báo 0,45s; hồi 0,5s" §6 và sàn 0,45s §12) — **một cặp duy nhất cho mọi archetype** vì mob AI chạy được khi bundle gate OFF nên brain không đọc bundle; bundle hiện chỉ export `telegraphSeconds` từng đòn và `recoverySeconds` cho boss. Case gửi owner: (a) export `recoverySeconds` cho từng đòn quái để brain đọc theo archetype/đòn, (b) mob accuracy/crit không có nguồn nên mob impact **không roll** (connect trừ khi ngoài tầm lúc va chạm), (c) quy tắc chọn đòn thường/nặng chưa có nguồn nên luôn dùng đòn thường, (d) player HP0 chưa có hệ thống hồi sinh/đứng dậy (chỉ `death-return` teleport condition, chưa có endpoint).
- **Bằng chứng:** self-check 280 assertions (+15 so với #78): `mob.aggro`/`mob.telegraph_opens`/`mob.telegraph_holds`/`mob.recovery_holds`/`mob.attack` (đúng thứ tự `TELEGRAPH>ATTACK`,`ATTACK>RECOVER`)/`mob.damage_lands` (10, 100→90)/`mob.damage_revision_bumps`/`mob.recovery_ends_to_chase`/`mob.attack_cooldown`/`mob.telegraph_repeats_after_cooldown`/`mob.damage_second_impact`/`mob.impact_whiffs_out_of_range`/`mob.telegraph_cancel_on_lost_target`/`mob.damage_gate_off`/`mob.damage_waterroot_basic_move`/`mob.damage_elite_scaling`/`mob.damage_unknown_template`/`mob.downed_target_untouched`; cộng `mob.los_blocks_aggro`/`mob.leash_return`/`mob.floor_ignored` giữ nguyên. Smoke/e2e chưa bật `P1:MobBehavior` (mob AI theo tick thật cần clock, self-check dùng `ManualServerClock` để deterministic).

### 9.9 DEC-022 guard/whiff/counter runtime (QOD-17)

- **Cửa sổ guard:** `GuardWindowStore` giữ **một window mỗi nhân vật**. `CombatTickEngine.Schedule` mở window khi cast `SK-MK-01` được chấp nhận (tick accept + aim snapshot đã normalize làm facing, attack snapshot = baseline completion_v1 20, hệ số counter = `SkillDefinition.Coefficients.Pve` 1.8) theo `[T, T+8)`; re-cast **refresh** (thay window, không cộng DR) đúng `SAME_SKILL_REFRESH_NO_ADD`.
- **DR chiều nhận (`GuardDefenseService.EvaluateIncoming`):** mob impact trong `[T,T+8)` và trong vùng trước (4.4 WU / 120°, mép inclusive, origin = chân defender **hiện tại**, facing = snapshot accept) → reduction 0.70; đòn sau lưng → 0 và không được confirmation. Đòn trong `[T+8,T+28)` khi window hết **tự nhiên** mà chưa confirmation và defender còn sống → whiff 0.20 cho **mọi** incoming damage, không counter. `END` của guard cast (start+2) không xóa whiff. Chết/đổi map/floor → window đóng, **không** cấp whiff, Kiếm Ý về 0.
- **Confirmation (§3):** resolve damage trước (DR → floor → HP), rồi mới xét sống. Hit trước hợp lệ đầu tiên commit **một** confirmation theo `guardCastId`: append `COUNTER_CONFIRMED` (không có `result`), `SwordIntent = min(5, current+2)`, reserve counter `tick + 1` vào **đúng nguồn đã confirm**. Hit sau trong cửa vẫn DR 0.70 nhưng không nhận resource/counter. Hit kết liễu → không confirmation, không +2, không counter.
- **Counter (§3–4):** `CombatTickEngine.Tick` quét `PendingCounters(tick)`; recheck lại toàn bộ (defender còn sống, window đang mở, source ALIVE + cùng `lifeId`, kind MOB/hostile, cùng map/floor, 4.4 WU/120° từ chân hiện tại, LOS, invulnerability), roll trên kênh RNG riêng `guardCastId|counter` (hit + crit), damage = `floor(attackSnapshot 20 × 1.8 × 100/(100+defense mob))` → oracle 34 với CARPLING def 4.2; emit `IMPACT`/`MISS`/`CANCEL` (CANCEL giữ `CounterOutcome` có lý do trong domain, **không** thêm field wire), dùng chung đường death/kill-credit với cast. Không retarget, không refund MP/CD, không +2 thêm, `NO_COUNTER_TRIGGER` (không vòng counter), không hard-control boss.
- **Không hỗ trợ / cần decision:** P1 chưa có damage từ người chơi khác nên nhánh "counter gặp guard khác" không chạy được thật (chỉ bất biến NO_COUNTER_TRIGGER); DoT/projectile/elemental chưa có content; `WHIFF_GUARD`/guard window **chưa** là field trong `WorldSnapshotV2.self` → client reconnect chỉ reconcile được qua event stream còn trong buffer. Nếu owner muốn status khả kiến qua snapshot, đó là proposal contract v2 riêng (không tự thêm).
- **Bằng chứng:** self-check 298 assertions (+18): `guard.window_opens_on_accept`, `guard.front_hit_inside_window`, `guard.back_hit_gets_no_reduction`, `guard.range_edge_is_inclusive`, `guard.angle_edge_is_inclusive`, `guard.window_end_is_exclusive_whiff_starts`, `guard.cast_end_keeps_whiff`, `guard.whiff_expires_full_damage`, `guard.two_hits_one_confirmation_one_counter`, `guard.counter_reserved_for_next_tick`, `guard.counter_impact_next_tick`, `guard.counter_pays_no_extra_resource_and_resolves_once`, `guard.counter_cancelled_keeps_cost_no_retarget`, `guard.counter_miss_no_refund_no_damage`, `guard.defender_death_clears_resource_no_confirmation`, `guard.refresh_replaces_window_without_stacking`, `guard.counter_lethal_hit_death_once`, `guard.gate_off_never_opens_window`, `guard.counter_source_death_after_confirm_cancels`, `guard.counter_los_block_cancels` — deterministic bằng `ManualServerClock`, không sleep. Đã phủ các dòng §6 của DEC-022 có nội dung P1: hit T+7/T+8, mép 4.4 WU/60°, hai hit cùng tick một confirmation, đòn sau lưng, defender chết vì hit gốc, nguồn chết sau confirmation, counter rời range/LOS blocked, hết tự nhiên → whiff 20%, CAST_END không xóa whiff, refresh không stack. **Chưa phủ (không có content P1):** ranged trong cone / DoT (DR70 không counter), shield hấp thụ hết / immune, PvP counter qua guard khác — ghi `unsupported` thay vì bỏ qua im lặng. Smoke/e2e không bật `P1:MobBehavior` nên chưa có tác động mob thật qua HTTP; production flags vẫn OFF.

### 9.10 Q-A checkpoint — sửa regression theo report `Qoder_Progress_Review_20261030` (QOD-18)

Report của Codex (branch `codex/qoder-review-next-epic-20261030`) xác nhận CI 6/6 và 301/440 có thật nhưng **hai negative probe ngoài suite vẫn FAIL**; work order 13 giao Q-A→Q-G qua issue #87. Checkpoint này đóng QREV-01..05 trên chính nhánh #84 (`qoder/qod-17-guard-runtime`), **không** tự coi #76 đã merge:

- **QREV-01 (probe replay FAIL):** cherry-pick `514c3f2` (#76) và resolve conflict theo hướng giữ nguyên code guard #84 — endpoint check `outcome.Replayed` trước khi `engine.Schedule`, nên retry sau `END` trả đúng receipt cũ, không thêm `END`/hit/death/kill, không refresh window, không +2 Kiếm Ý. `InMemoryCombatV2Service` bản #76 (toàn bộ decision under `actor.SyncRoot` + reject actor `Hp<=0`) được giữ nguyên; `CombatTickEngine` thêm cancel khi actor chết/đổi map/floor vào loop của tôi và **đóng window guard tương ứng** (`Close(DefenderDown)`, resource về 0 theo §3; map/floor change không reset resource đã nhận).
- **QREV-02 (probe queue FAIL):** `PendingCounters(tick)` nhận mọi counter `due <= tick` và trả theo thứ tự (due tick, characterId) — work overdue còn eligible cho tới khi resolve **đúng một lần** (`CounterResolved` claim trong engine). Không backdate: event mang `ServerTick` của tick thực sự xử lý, provenance deadline vẫn ở `CounterTick`. `WorldTickBackgroundService` sample `ServerClock.Tick` **một lần mỗi iteration** cho casts, mob AI và mob impacts (trước đây sample hai lần → một phần thế giới có thể đi trước một tick). Test: 2 window due 2 và 3, gọi `Tick(10)` → cả hai resolve theo thứ tự, `Tick(10)` lần hai không phát sinh impact, queue rỗng.
- **QREV-03:** accept path của #76 đã gộp cache/hash/cost/CD/sequence/revision/receipt vào cùng một actor critical section; self-check dùng `CombatCommandRaceChecks` (barrier + catalog entry probe) cho cả same-payload (`concurrent_replay`: một fresh charge, hai outcome cùng reference, MP trừ một lần) và different-payload (`concurrent_conflict`: một fresh, một `idempotency_conflict`, stream đúng một event).
- **QREV-04:** `SelectTargets` gọi lại `CheckLineOfSight` tại impact cho basic/MK03 (trước chỉ cone+range+alive+instance). Test dùng **bundle REVIEWED tổng hợp** của self-check: caster 43.5, mob phía sau tường 46.5 → không impact; mob phía thoáng 42.5 → impact 19 (đúng oracle). Bundle production `SYNTHETIC_TEST_ONLY` vẫn trả `NotEnforced` → không được dùng làm bằng chứng chặn tường, và tôi **không** đổi review state.
- **QREV-05:** một impact giờ chạy trong **một** lock của defender: `EvaluateIncoming` → damage/floor → commit HP+revision → `CommitConfirmation`. `GuardIncoming` mang `WindowCastId` làm token; `CommitConfirmation` từ chối nếu window hiện tại khác token, và `Open` đóng window cũ bằng `REFRESHED` dưới cùng lock → không còn khả năng "DR của castA nhưng confirm cho castB". Barrier test 8 thread (4 refresh + 4 impact) bất biến: mỗi damage ∈ {3 khi DR 0.7, 10 khi không}, confirmation chỉ thuộc đúng window đã trả DR, `#confirmations == #COUNTER_CONFIRMED events`, `intent == min(5, 2×#confirmations)`, `hp == 100 − Σdamage`. Đây là proof **integrity** dưới race, không phải measurement của một race đã tái hiện.
- Probe của report được giữ nguyên (`Tools/ProducerReview/**` thuộc Codex, report baseline không sửa); 2 probe đó phải PASS ở head mới và được dẫn chứng trong report bàn giao. Self-check 311 assertions; smoke/e2e số liệu lấy từ CI run ở checkpoint này.

### 9.11 Q-B1: SK-MK-02 là dash thật trên tick (QOD-18)

- **Timeline theo nguồn:** Art Brief P1 (`SK-MK-02 Tầm Long`: prep 0,15s → dash 0,20s → recovery 0,24s) ở 20 Hz cho tick resolve = **startTick + 7**; `SkillDefinition` canonical (CD 8s, 16 MP, rangeWu 11, targeting DASH, coefficient pve 1.5) là nguồn số, 1 WU = 0,5 m theo DEC-016 nên 11 WU chính là 5,5 m.
- **Sweep:** đi từ **chân hiện tại** của actor theo facing đã snapshot lúc accept, bước dò 0,25 WU rồi nhị phân 12 lần để lấy xa nhất an toàn; dùng `CheckWalkSegment(..., footprintRadiusWu = P1World:ActorFootprintRadiusWu)` **giống hệt** `POST /p1/move` (P1 chưa có dash volume riêng — design resolution §4 nêu rõ "attack/collision volumes của dash cần field riêng", nên không tự đặt radius). Clamp theo map bounds. Không teleport ngược về snapshot origin nếu actor đã đi bộ trong lúc chờ tick.
- **Không damage, không resource:** Content Bible §103 ghi "gây 150% lên mục tiêu đầu; +1 Kiếm Ý", nhưng (a) design resolution §4 nói hit shape của dash chưa có field, (b) Production_Rules §2 cần shape để resolve damage, (c) work order 08/13 chốt subset P1 là dash di chuyển. Vậy dash **không** gây damage và **không** cộng Kiếm Ý — hai chỗ này là **case mở** cho owner, không phải tính năng đã hủy.
- **Stop reason / ledger:** `DashResolution(CastId, AppliedTick, RequestedWu, AchievedWu, X, Y, StopReason ∈ COMPLETE|BLOCKED_BY_GEOMETRY|ZERO_DISTANCE, ActorRevision)` vào `DashLedger` bounded 512 (FIFO). Không tự ý thêm field wire: `CombatEventV2` không có type movement, `WorldSnapshotV2.self` không có stop reason, schema đang `additionalProperties=false` và design resolution §3.2 cấm nhét field lạ — bằng chứng client dùng được hôm nay là `self.x/y` + `revision` (reconcile-by-snapshot) cho tới khi contract được duyệt.
- **Không refund:** MP/CD/sequence commit một lần tại accept; dashBlocked-at-start, actor chết trước tick (cancel `CANCEL`+`END` một lần, không di chuyển, không ledger entry), hay retry sau đó đều **không** hoàn cost (design resolution §3). Revision của actor chỉ đổi khi vị trí thực sự đổi.
- **Bằng chứng:** self-check `dash.unenforced_geometry_runs_full_range` (11 WU, không event damage), `dash_resolves_after_prep_and_ends_next_tick` (END @7), `dash_stops_short_of_reviewed_wall` (bundle REVIEWED tổng hợp: dừng < 44.5, achieved 0,2–1,1, không xuyên tường), `dash_blocked_at_start_reports_no_travel` (không bump revision), `dash_cancelled_when_actor_down_before_movement`, `dash_ledger_is_bounded`; HTTP smoke mới: cast `SK-MK-02` rồi bounded wait (3 s) thấy `self.x` dịch đúng 11 WU, MP vẫn 34, HP 100, revision tăng → chứng minh "dash là movement" chứ không phải label của cast accepted. Production map vẫn `SYNTHETIC_TEST_ONLY` → full range ở đó là `NotEnforced`, **không** được đọc là "tường không hoạt động".

### 9.12 Q-B2: combat status read model + đề xuất contract (chưa đụng wire)

Vấn đề: toàn bộ trạng thái chiến đấu (guard còn bao nhiêu tick, whiff đang bật, counter đã reserve hay chưa, cooldown còn lại, dash vừa đáp ở đâu) hiện chỉ suy ra được từ event stream **còn trong buffer** (512/session). Reconnect sau khi buffer rolling, hoặc client cursor trễ, không reconstruct được "tôi đang đỡ hay không" — vi phạm đúng điều design resolution §3.2 yêu cầu (snapshot reconcile, không bắt client đoán từ event cũ).

**Đã làm (domain-only, không đổi contract):** `CombatStatusProjection.Project(session, tick, nowUtc)` trả `CombatStatusSnapshot`:
- `Hp/MaxHp/Mp/MaxMp/SwordIntent/ActorRevision` của actor aggregate.
- `GuardPhase ∈ NONE|GUARD|WHIFF|EXPIRED`, `GuardCastId`, `GuardEndExclusiveTick`, `WhiffEndExclusiveTick` — từ `GuardWindowStore` (window đã đóng → NONE, không suy ra từ event).
- `CounterReserved`, `CounterTick`, `CounterOutcome`, `CounterSourceEntityId` — cho client biết còn phải chờ một counter hay đã resolve (presentation parry/hit/miss khác nhau).
- `Cooldowns[] { actionKey, endsAtUtc, active }` — chỉ liệt kê action còn bị chặn, key là skillId hoặc `BASIC_ATTACK`.
- `LastDash` — `DashResolution` gần nhất của chính nhân vật (tick, requested/achieved WU, toạ độ, stop reason), bounded 512 ledger.
Bằng chứng self-check: `status.guard_phase_counter_and_cooldown` (GUARD + counter reserved + cooldown + MP 50→38 + Hp 97 vì DR 0,7), `status_reports_resolved_counter_and_keeps_cooldown`, `status_carries_last_dash_outcome_without_events`, `status_tracks_whiff_expiry_and_closed_window` (WHIFF→EXPIRED, window đóng vì chết → NONE/intent 0).

**Đề xuất contract (CHỜ owner/Codex duyệt — chưa áp dụng):** thêm field **optional** vào `WorldSnapshotV2` để không phá client hiện tại:
```jsonc
"combat": {                       // optional object, chỉ có khi P1:CombatV2 ON
  "schemaVersion": 1,             // version hoá riêng, không tăng schemaVersion snapshot
  "revision": 12,                 // status aggregate revision = actor revision tại thời điểm sample
  "serverTick": 4820,
  "guard": { "phase": "GUARD", "castId": "<hex32>", "endsAtTick": 4827, "whiffEndsAtTick": 4847 },
  "counter": { "reserved": true, "dueTick": 4828, "sourceEntityId": "ENT_…" },
  "swordIntent": 2,
  "cooldowns": [ { "actionKey": "SK-MK-01", "endsAtUtc": "…Z" } ],
  "lastMovement": { "castId": "<hex32>", "achievedWu": 4.4, "requestedWu": 11,
                    "stopReason": "BLOCKED_BY_GEOMETRY", "x": 44.4, "y": 0, "appliedTick": 4820 }
}
```
Quy tắc: (1) `phase`/`stopReason` là enum đóng, thêm giá trị mới = bump `schemaVersion` của `combat`; (2) mọi tick là **server tick** 20 Hz, client chỉ được suy hết hạn bằng `serverTick` + delta đã đo, không dùng đồng hồ máy mình; (3) `counter` chỉ nói "đã reserve/đã resolve", không phải bằng chứng counter trúng damage (DEC-022 presentation rule); (4) field optional nghĩa là client cũ bỏ qua vẫn hợp lệ — không đổi shape response hiện có, không đụng v1; (5) capability: thêm `capabilities: ["combat-status-v1"]` trong `/p1/sessions` response (cũng optional) để client biết có được đọc hay không; (6) dash **không** có event riêng cho tới khi đồng ý `DASH_RESOLVED` trong `CombatEventV2` (hiện enum không có movement type) — `lastMovement` trong snapshot là đường đi được đề xuất trước.
Nếu owner duyệt, PR contract sẽ gồm: schema + example + `validate_contracts.py` checks (optional field, enum đóng, revision/tick integer ≥ 0) + README mục v2 + smoke assert shape; nếu chưa duyệt, P1 vẫn chỉ có `self.x/y/hp/mp/swordIntent` + event cursor và read model này phục vụ test/probe nội bộ.

**Chưa phủ (ghi rõ, không giả đã xong):** PvP counter thật (cần damage từ người chơi khác), DoT/projectile/elemental incoming (chưa có content), `WHIFF_GUARD` như status registry chính thức (Rules §3 status registry chưa có dữ liệu), và mob telegraph metadata qua wire (client hiện mới thấy `state: TELEGRAPH`, chưa có timing/shape — Q-B còn lại sẽ để xuất read model riêng).

### 9.13 Q-B3: dọn state lúc chết + return về safe anchor (DEV fixture, gate OFF, chưa có endpoint)

**Đã làm (domain-only):** `DeathReturnService.ReturnToAnchor(sessionId, idempotencyKey)` — server chỉ nhận "cho tôi về", **không nhận toạ độ**: mọi attempt truyền toạ độ client tự chọn đều không có đường vào, vì API không có tham số đó.
- **Điều kiện áp dụng:** gate `P1:DeathReturn` ON + `idempotencyKey` hex32 + session tồn tại + `MapId` resolve được trong `map_bounds.json` + actor **đã down** (`Hp <= 0`). Sai một trong năm thứ → từ chối, không đổi state, không bump revision.
- **Anchor:** `P1World:SpawnX/SpawnY` clamp vào bounds của **chính map actor đang đứng** — đây là toạ độ server-owned duy nhất P1 có hôm nay, nên là **DEV fixture có nhãn**, không phải "safe anchor đã duyệt". `map_bounds.json` là bounding box, không phải walkability: về vị trí spawn chưa bảo đảm ô đó `is_a_star_walkable` trên topology REVIEWED (bundle production vẫn `SYNTHETIC_TEST_ONLY`), và `CheckWalkSegment` của `POST /p1/move` không được dùng ở đây vì return không đi bộ theo đường thẳng.
- **Dọn state (bounded, có event):** `GuardWindowStore.Close(DEFENDER_DOWN)` (window ngừng giảm damage, mất whiff, Kiếm Ý về 0 theo DEC-022 §3) + `CombatTickEngine.CancelPendingFor(characterId)` → mỗi cast đang bay emit `CANCEL` rồi `END` **đúng một lần**, không damage không kill credit; counter đã reserve mà chưa tới tick vẫn bị cancel (`CounterOutcome = RETURNED_TO_ANCHOR`) chứ không để nó swing vào nguồn mà actor không còn thấy. Aggro không cần ledger riêng: `FindTarget` chạy lại mỗi tick và bỏ qua player `Hp <= 0`, nên mob giữa telegraph tự `ResetAttackWindow()` khi mất target.
- **Idempotency:** ledger bounded 256 theo **key**, lưu kết quả đã áp dụng; same key + same character → trả đúng kết quả cũ (`Replayed=true`, không move lần hai, không thêm event); same key nhưng **khác character** → `idempotency_key_conflict` (không cho key của client này kéo actor khác); **refusal không được ghi ledger** để retry bằng chính key đó vẫn hợp lệ sau khi actor thật sự down. Bốn thread cùng key → đúng một lần áp dụng (barrier test, không sleep chờ race).
- **Cost/penalty: chưa áp dụng gì** — không có nguồn. `RestoreHpFixture` mặc định **0** nghĩa là return **không** tự hồi HP; chỉ khi operator cấu hình (validator chặn giá trị > `P1World:StartingMaxHp`) thì mới refill tới mức đó, và log startup in rõ "DEV FIXTURE".
- **Bằng chứng self-check:** `death_return.gate_off_and_refuses_alive_and_bad_key` (cả gate ON qua DI thật), `death_return.unknown_session_and_map_do_not_move_anyone`, `death_return.clears_cast_window_and_counter_once` (3 event cancel, `ScheduledCastCount → 0`, window đóng, intent 0, tick sau đó emit 0 event), `death_return_replays_the_recorded_answer`, `death_return.one_key_applies_once_under_contention`, `death_return.restores_only_the_configured_fixture_value`, `death_return_ledger_is_bounded`.

**Thiếu nguồn — cần owner/Codex chốt trước khi mở wire (case cụ thể, không tự đặt số):**
1. **Safe anchor theo map/floor.** Canonical content chưa có trường "điểm hồi sinh an toàn" nào (`world_records.json`/`map_bounds.json` chỉ có spawn region + bounding box). Cần: một mục per `(mapId, floorId)` (tên propose `safe_anchor` với `x,y` + `requiresWalkable: true`) do content producer duyệt, kèm quyền kiểm tra walkability bằng topology REVIEWED. Nếu chủ trương là *không* dịch chuyển qua map thì nói rõ, vì P1 hiện không có teleport đã duyệt (`ITeleportService` vẫn skeleton).
2. **HP/MP sau return.** Production_Rules §3 không có giá trị "hồi sinh được bao nhiêu HP"; Content Bible chỉ nói về potion/MP skill. Cần hoặc (a) `%` MaxHp theo quy tắc đã duyệt, (b) về ở 1 HP + người chơi tự hồi, hay (c) dùng `P1World:StartingHp` (fixture hiện tại). Chọn xong mới bỏ nhãn DEV.
3. **Penalty.** Không có nguồn cho XP loss, độ bền trang bị, tiền, hay thời gian chịu phạt (decimation/death timer). Mọi con số hôm nay đều là bịa → server **không** áp penalty nào. Nếu cần penalty, cần field trong `Production_Rules` (tỉ lệ %, đơn vị, áp trước hay sau `applied:false` transaction của XP — Q-D) và cách hiển thị cho client.
4. **Transition/lease.** "Về safe anchor" có phải một lần dịch chuyển tức thời (không LOS, không AOI enter/leave event) hay một quá trình có state `RETURNING` (khống chế input bao lâu)? P1 chưa có khái niệm transition; cần quyết định để biết `revision`/`WorldSnapshotV2` phải lộ gì giữa đường.
5. **Session refs lúc logout.** `InMemorySessionStore` không có API remove và P1 **không có endpoint logout**, nên `CombatEventStore` (512 event/session) và `WorldEntityAoiProjection` (hysteresis per character) giữ state tới hết process. Đây là giới hạn đã ghi, không phải tính năng đã dọn: cần hoặc chính sách TTL (số phút do owner chốt) hoặc hợp đồng logout — và chỉ cleanup được khi session store có remove; persistence dài hạn thuộc QOD-20/Remote #79, không phải chỗ này.

**Đề xuất endpoint (CHỜ duyệt contract — chưa đăng ký route):** `POST /p1/v2/death-return`, request `{ requestId, idempotencyKey, sessionId }` (envelope v1 hiện có, **không** field toạ độ), response `{ ok, data: { x, y, hp, revision, serverTick, cancelledEventIds[] }, error? }` với error code đóng `death_return_disabled | unknown_session | invalid_idempotency_key | unknown_map | not_downed | idempotency_key_conflict`. Kèm capability flag trong `/p1/sessions` (ví dụ `death-return-v1`) để client biết có đường nào. PR đồng ý contract sẽ gồm schema + example + `validate_contracts.py` (no additionalProperties, enum đóng) + README + smoke; bao giờ owner duyệt mới bật gate.

**Trùng lặp cần owner xử lý một lần:** `ITeleportService` (skeleton từ QOD-06, **chưa map route nào**) đã có `TeleportReasons.DeathReturn` và check `actor.Hp <= 0`, nhưng shape của nó bắt client gửi `mapId/xWu/yWu` — đúng cái "revive tại toạ độ client tự chọn" mà work order 13 cấm, và nó đổi `MapId` tuỳ ý mà không đi qua map-travel policy. `DeathReturnService` là phần server-owned của cùng quy tắc. Xin chốt một trong hai: (a) route `death-return` mới và `ITeleportService` ở lại skeleton (teleport không có `DEATH_RETURN` reason, hoặc gate riêng), hay (b) giữ một đường teleport nhưng `DEATH_RETURN` không nhận toạ độ mà server tự resolve anchor. Hôm nay **không có route** cho cả hai nên chưa lộ rủi ro — ghi ở đây để không ai map nhầm cái skeleton.

### 9.14 Q-B4: profile `mob-combat` — MobBehavior + CombatDamage nối nhau qua HTTP

Work order 13 yêu cầu "Nối MobBehavior+CombatDamage trong **test profile riêng** và HTTP scenario conditional waits". Đã làm: job CI mới `e2e-mob-combat` chạy `bash Server/Health/Smoke/run_e2e_p1.sh mob-combat`, server bật **đúng ba gate** `P1:CombatV2`, `P1:CombatDamage`, `P1:MobBehavior` (quest gates OFF — đây là fixture tách biệt, không phải profile `dev` bật thêm flag), scenario trong `e2e_p1.py:mob_combat_profile()`:

- **Tiếp cận bằng lane, không bằng đường:** mọi group trên map này đứng ở `y=0`, nên hành lang `y=7,5` nằm ngoài `AggroRadiusWu` 6 bất kể `x`. Scenario đi trục **y trước rồi x** (`walk_to(..., axes=("y","x"))`), assert lane không aggro ai và không mất HP, rồi mới hạ xuống `y=0` tại `x=87` — chỗ đó chỉ `ENT_MAN_BM_SPAWN_BM_01*` (3 CARPLING tại 84) vào aggro, group escort ở 80 cách 7 WU vẫn ngoài. Bài học từ chính 2 CI run đầu: đi dọc `y=0` thì **hai group cùng bu bám** (log: 6 mob CHASE), và nếu `walk_to` chạy trục x trước thì lane chẳng còn tác dụng. Đây là lý do giữ assertion "tập mob đang engaged ⊆ MOB_GROUP" thay vì tin vào bố cục.
- **Đủ 4 chân của work order:** đọc `TELEGRAPH` → `POST /p1/move` bước ra ngoài `AttackRangeWu` 1,2 trước frame impact → HP **không đổi** (impact đã commit vẫn resolve, chỉ là `OutOfRangeAtImpact` — đúng fix "committed telegraph không được đóng băng khi target rời tầm"); đứng lại → damage vào đúng **bội số của 10** (attack 15 × BITE 0,8, mitigation 100/110, một floor cuối theo Production_Rules §2) → cast `SK-MK-01` hướng `-x` (mặt vào mob) cho tới khi `COUNTER_CONFIRMED` xuất hiện trong event stream → counter của chính guard đó resolve `IMPACT`/`MISS`, **không đổi target**, và `maxHp - hp` của mob trên snapshot **bằng đúng** `result.hpDamage` của event (bằng chứng read model và event stream cùng nói một số, qua HTTP thật, không phải fixture).
- **Chết là chết:** đứng yên tới khi HP về 0, rồi assert server không che: cast mới bị `409 actor_not_alive`, HP vẫn 0 sau 3 s (không tự heal — đúng điều work order cấm "tự heal khi chỉ reconnect/equip"), và cả ba mob `RETURN`/`IDLE` (aggro tính lại mỗi tick và bỏ qua `Hp <= 0`) nên không có hit nào vào xác; snapshot vẫn serve và `serverTick` vẫn tăng.
- **Conditional waits, không đoán race:** `wait_for(deadline, probe)` chỉ poll và **không ghi check mỗi vòng lặp**; assert diễn ra một lần sau loop → tổng số check của profile không đổi theo timing (đúng nguyên tắc đã rút ra ở Q-B3).
- **Endurance fixture, ghi rõ:** profile đặt `P1World__StartingHp/StartingMaxHp=400`, `StartingMp/StartingMaxMp=200` *chỉ* để một actor sống sót qua toàn bộ các pha trong một run (MP không regen nên 8 attempt guard cần nhiều hơn 50 MP). Đây là kích thước pool, không phải cân bằng: mọi số damage vẫn do công thức và `P1:MobBehavior` đã ship quyết định. Scenario assert `hp_start > 200` để không ai đọc nhầm kết quả khi chạy với config khác.
- **Số đo CI (head `9871318`, in lại at `f3210a3`):** job `e2e-mob-combat` pass ~1m20s, **85 checks**, summary `telegraph=OK escape_whiff=OK mob_damage=30 guard_confirm=OK counter=IMPACT death_stays_down=OK mob_states=RETURN` và `counter=IMPACT counter_damage=34 on ENT_MAN_BM_SPAWN_BM_01`. `mob_damage=30` là ba đòn CARPLING thô (3 × 10 theo Production_Rules §2 với armor 10), 34 là đúng oracle counter DEC-022, và snapshot HP của mob khớp từng point với `result.hpDamage` của event — đó là hai đường đọc khác nhau trên cùng một server thật, không phải fixture.
- **Chưa phủ (giữ ở self-check):** các interleave dưới 50 ms mà client không thể canh đúng nhịp — source chết giữa confirmation và counter tick, counter overdue sau callback bị nhảy, hai hit cùng tick chỉ một confirmation, guard refresh đua với impact. Boss (`BOSSDATA_BLOCKED`) và DoT/projectile/PvP vẫn `unsupported` vì không có content.

### 9.15 Q-B5: mob telegraph read model (timing/target/reach) — domain-only, chưa đụng wire

Work order 13 Q-B: "Mob telegraph metadata/read projection phải có enough timing/target/shape để client đọc đòn khi có contract". `state: TELEGRAPH` trong snapshot chỉ nói *loại* state, không phải read window — client không thể biết né lúc nào nếu phải tự đếm 0,45 s bằng đồng hồ máy mình.

**Đã làm:** `MobLifecycleService.GetAttackWindow(entityId)` (read-only, không đụng AI) + `MobTelegraphProjection.Project(entities)` trả `MobTelegraphReading` cho **chỉ** entity đang engaged (IDLE bị loại để client không vẽ warning cả map):

- `state`, `targetCharacterId` — đòn đang commit vào ai.
- `impactInTicks` / `recoverInTicks` / `nextAttackInTicks` — đếm ngược theo **server tick 20 Hz**, cộng `impactAtUtc` tuyệt đối để client ghép với `serverTimeUtc` của snapshot; đơn vị tick là bắt buộc vì mọi timing khác của combat (guard window, counter, dash) cũng theo tick.
- `rangeWu` = `P1:MobBehavior:AttackRangeWu`; **`angleDegrees` để `null` có chủ đích**: chưa có nguồn nào export shape per-move (width/length/arc) cho mob, và 120° của DEC-022 là cone của *người đỡ*, không phải của đòn mob → mượn nó là bịa số.
- Số học timing dùng **integer ceiling trên tick 100 ns**, không phải `TotalSeconds`: 0,45 s nhân 20 ra 9,0000000000000002 nên `Math.Ceiling` float biến read window thành 10 tick — self-check case `telegraph.reading_carries_target_timing_and_reach` chốt đúng con số 9.
- Hành vi đã khoá bằng test: `telegraph.idle_has_nothing_to_read`, `telegraph.countdown_moves_with_the_server_clock` (9 → 7 sau 0,1 s), `telegraph.stays_committed_when_the_target_leaves_range` (ra khỏi tầm *đánh* mà vẫn trong aggro → đòn đã commit vẫn còn, vì frame impact vẫn xảy ra và chỉ damage check mới biết nó whiff — Q-A fix được đọc được từ phía client), `telegraph_after_impact_reads_recovery_and_cooldown` (`impactInTicks` thành null, `recoverInTicks` 10, `nextAttackInTicks` 40), `telegraph_lost_target_reports_no_committed_frame` (mất target → `ResetAttackWindow` + RETURN, không còn frame nào).

**Đề xuất contract (CHỜ duyệt — chưa áp dụng):** thêm block **optional** vào mỗi entity mob của `WorldSnapshotV2` (không đổi shape các field cũ, không đụng v1):
```jsonc
{ "entityId": "ENT_…", "kind": "MOB", "state": "TELEGRAPH", "hp": 192, …,
  "telegraph": {                      // optional, chỉ có khi mob đang engaged
    "schemaVersion": 1,
    "targetCharacterId": "CHR_…",     // null nếu AI chưa chốt mục tiêu
    "impactInTicks": 9,               // server tick 20 Hz, không dùng đồng hồ client
    "recoverInTicks": null,
    "nextAttackInTicks": 40,
    "rangeWu": 1.2,
    "angleDegrees": null              // null = chưa có source shape per-move
  } }
```
Quy tắc: enum `state` đóng như hiện tại; thêm field mới vào `telegraph` = bump `schemaVersion` của block chứ không của snapshot; `null` là "server không biết", client **không** được tự điền số; capability `mob-telegraph-v1` trong `/p1/sessions` để client biết có được đọc hay không. Nếu owner duyệt: schema + example + `validate_contracts.py` (optional, integer ≥ 0, null được phép) + README + assert trong `e2e-mob-combat`. Chưa duyệt thì read model này phục vụ test/probe nội bộ, đúng like Q-B2.

**Đo được ở CI head `f3210a3`:** self-check **338 PASS / 0 FAIL** (6 case `telegraph.*` mới), HTTP smoke **453 checks**, `e2e-mob-combat` **85 checks** (`mob_damage=30`, `counter=IMPACT counter_damage=34`), e2e default 9 / dev 176, hai probe của report vẫn PASS. **Đính chính cho chính report của tôi:** run `0f0eea7` ra **84** chứ không phải 85 — không phải server đổi hành vi mà là check của tôi phụ thuộc nhánh (`maxHp-hp == hpDamage` chỉ chạy khi counter trúng) và loop retry guard ghi một check mỗi attempt. Cả hai đã sửa (`301dee6`, `f3210a3`): thu kết quả rồi assert một lần, và nhánh MISS giờ cũng assert (mob phải còn nguyên HP) thay vì không nói gì. Trước đó tôi viết "identical across three runs" — đúng cho 3 run được trích nhưng suy thành "total đã ổn định" là sai; bài học đã ghi: **không check nào trong loop có trip-count thay đổi, và không check nào được quyết định bởi dice roll.** Q-B đóng ở đây (B1 dash, B2 status, B3 death-return + cleanup, B4 profile mob combat live, B5 telegraph read model); phần wire của B2/B5 vẫn chờ owner duyệt contract.

### 9.16 Q-C1: quest graph P00-01..05 từ source, blocked-activation thay vì default 0

**Nguồn dùng để dựng graph:** `docs/production/Quest_and_Narrative_Production_Spec_vi.md` §2 bảng "Mở đầu — Bến Mưa (cấp 1–10)" (từng dòng cho ra start NPC, các bước chính, thưởng, mở khóa; tiêu đề mục cho ra level band 1–10), `Item_Master_Catalog_vi.csv` cho id vật phẩm, `Quest_Dialogue_Production_Data_vi.csv` cho `quest_id`/`graph_id`, và `world_records.json` cho target id. `Narrative_Quest_Beats_v2.json` **không** dùng để dựng objective: chính file đó ghi `scope: PRESENTATION_EXTENSION_NO_COUNT_OR_REWARD_CHANGE`, và work order cấm biến text/dialogue thành objective graph.

**Đã thêm:** 4 runtime record `P00-02..05` + `activation`/`blockedSteps` cho cả 5. Bảng map, kèm phần nào là suy ra và phần nào là thiếu:

| Quest | Nguồn (bước) | Objective runtime | Trạng thái |
|---|---|---|---|
| P00-02 | "hạ 4 Cá Linh" | `KILL` `MOB_CARPLING` ×4 | có target thật |
| P00-02 | "kiểm 3 gợn nước" | — | **BLOCKED**: không có record interactable cho gợn nước |
| P00-03 | "phá 3 Rễ Nước" | `KILL` `MOB_WATERROOT` ×3 | có target thật |
| P00-03 | "tương tác 2 dân mắc kẹt", "né một đợt sóng" | — | **BLOCKED**: không có record dân; P1 không có wave/dodge |
| P00-04 | "hạ 2 đợt 3 quái" | `KILL` `MOB_CARPLING` ×3 + `MOB_WATERROOT` ×3 | có target thật, nhưng đếm theo loài (targetIds pattern không mang được record id của group) → ghi thêm gap `waveAttribution` |
| P00-04 | "hộ tống Ly An qua checkpoint x=80/120" | — | **BLOCKED**: P1 chưa có escort/checkpoint runtime (toạ độ đã có trong nguồn, cơ chế thì chưa) |
| P00-05 | "hạ Mãng Cốt" | `BOSS` `BOSS_MANG_COT` ×1 | có target thật nhưng stat boss là `BOSSDATA_BLOCKED` → gap `bossStats` |
| P00-05 | "tương tác mảnh ấn" | — | **BLOCKED**: không có record mảnh ấn |
| P00-05 | "xác nhận môn phái ở NPC_CLASS_TRIAL" | `TALK` `NPC_CLASS_TRIAL` ×1 | có anchor thật |

Ngoài ra mỗi quest 03/04/05 thiếu **NPC nhận báo cáo** (nguồn chỉ ghi NPC bắt đầu) → `turnInNpcId` để trống và được khai báo đúng là một blocked step; P00-05 thiếu id quest mở khóa (`C1-01` chưa có runtime record) → gap `unlockQuestIds`. Thưởng lấy từ nguồn: P00-02 `POT-HP-01` ("thuốc" = Dược Bến Mưa), P00-03 thêm `EQ-MK-BOOTS-T1-R-COMMON` ("giày", chỉ lớp MK có trong catalog P1), P00-04 thêm 30 Đồng, P00-05 `EQ-MK-WEAPON-T1-R-COMMON` (nguồn ghi `EQ-[CLASS]-WEAPON-T1-R-COMMON`; P1 chỉ ship lớp MK nên id được viết cho lớp đó và **ghi rõ** đây là giới hạn của slice, không phải bản dịch đầy đủ).

**Luật đã khoá bằng code:** `activation` là **bắt buộc** trong file (không mặc định ACTIVE); BLOCKED phải có ≥1 blocked step, ACTIVE không được có; mỗi blocked step phải có `designStep` + `missingField` + `source` trỏ tới `.md`/`.csv`; `turnInNpcId` được phép null **chỉ khi** có blocked step tên đúng `turnInNpcId`. Runtime: quest BLOCKED luôn `LOCKED` kể cả khi prerequisite đã xong, và accept trả `prerequisite_not_met` + fieldErrors `activation.blocked.<DESIGN_STEP>` (tái dùng enum hiện có — **không đổi wire**; một code riêng `quest_blocked` là đề xuất contract cho lần version sau). Startup validator: prerequisite/unlock tồn tại, **hai chiều khớp nhau**, graph prerequisite **không cycle**, `KILL`/`BOSS`/`ESCORT` target resolve về record thật, `TALK` resolve về NPC anchor, và blocked step phải khai báo đủ. Content schema (`QuestDefinition.schema.json`) + `validate_content.py` được mở rộng tương ứng (chạy local: `OK: all content validation checks passed`, 5 QuestDefinition example).

**Ghi nhận cho content owner (không tự sửa):** (1) manifest Bến Mưa có **hai** record boss cùng toạ độ (178,0) — `MAN-BM-EVENT_BOSS_BM_MANG_COT` (`ACTIVITY_BOSS`) và `MAN-BM-SPAWN_BM_05_QUEST` (`ATLAS_BOSS`) — cùng trỏ `BOSS_MANG_COT`; quest chọn record ACTIVITY_BOSS, nhưng nếu cả hai được spawn cùng lúc thì đó là trùng lặp cần chốt. (2) Mọi gap ở trên là điều kiện **mở khóa** P00-02..05; danh sách nằm ngay trong file runtime nên không ai phải đoán lại.

### 9.17 Q-C2: narrative nodes, reveal gate, flags — domain-only, chưa có route

Nguồn: `docs/production/Quest_Dialogue_Production_Data_vi.csv` (230 dòng → **229 node**; hai dòng của `DLG_C3_05_CHOICE` là hai lựa chọn của cùng một node). `build_narrative_nodes.py` xuất `narrative_nodes_v1.json` (questId/graphId/nodeId/order/type/speaker/condition/textKey/nextNode/onEnterEvent/setFlag/choices) và CI rebuild + `git diff --exit-code` như 4 bundle khác, nên sửa CSV mà quên runtime record là đỏ ngay.

**Reveal gate** là server-side: node chỉ tồn tại với nhân vật khi `conditionKey` khớp state quest của **chính** nhân vật (`QUEST_AVAILABLE`/`QUEST_ACTIVE`/`QUEST_READY_TO_TURN_IN`). `NarrativeService.Offer` chọn node theo state; `Enter` từ chối `narrative_not_revealed` nếu lệch, `narrative_wrong_speaker` nếu sai NPC, `narrative_unknown_node` nếu node không thuộc quest. Text **không** rời server dưới dạng prose — chỉ `textKey`.

**Flag**: vocabulary đóng lấy từ bundle (hiện `C3_05_PUBLISHED`, `C3_05_COUNCIL_ONLY`); mỗi lần vào node set tối đa một flag, lưu per character trong store bounded 128 (FIFO). Node `CHOICE` bắt buộc trả về một option của chính nó, và option quyết định flag — không đoán.

**Talk → objective**: node có `onEnterEvent: OBJECTIVE_PROGRESS` ghi một verified event `TALK` (eventId = SHA-256 của `nodeId|characterId`, nên replay cùng node không cộng hai lần) để objective `TALK` tiến từ hội thoại, không cần endpoint riêng.

**Party**: `PartyPolicies.SoloOnly` — P1 chưa có party runtime nên tiến độ được dán nhãn solo, không ngụ ý chia credit.

**Đề xuất contract (chờ duyệt, chưa áp dụng):** `POST /p1/narrative/enter` với `{requestId, idempotencyKey, questId, npcId, nodeId, choiceId?}` → `{ nodeId, textKey, nextNodeId?, choices[], appliedFlag?, progressedQuestIds[], partyPolicy: "SOLO_ONLY" }`, error enum đóng (`narrative_unknown_node|narrative_not_revealed|narrative_wrong_speaker|narrative_choice_required|narrative_unknown_choice`), cộng `GET /p1/narrative/flags/{sessionId}` để client biết đã set gì. Không có route nào được map hôm nay.

### 9.18 Q-E bước 1: kiểm coin band trong nguồn loot — không có, grant vẫn OFF

Quét `docs/production/Loot_Recipe_Reward_Production_Data_vi.csv` (221 dòng): `row_type` = `LOOT_ENTRY` 184, `RECIPE` 7, `REWARD` 3, `CURRENCY_REWARD` 27; **0 dòng `item_or_currency_id = COIN`**. `Currency_Production_Data_vi.csv` có `COIN` nhưng chỉ định nghĩa balance cap/nguồn/sink, không có band theo `source_id`. Vậy `COIN_BAND_MISSING` trong `loot_recipe_v1.json` là **đúng**, `grantEnabled` phải tiếp tục `false`, và builder không được nới điều kiện — thay đổi duy nhất là ghi lại bằng chứng này. Gear roll vector cũng chưa có bảng riêng (`Item_Rarity_Variant_Catalog` chỉ cho pool độ hiếm), nên ứng viên gear vẫn blocked với field riêng; fullbag policy không có trong `Currency_Production_Data` nên cũng là blocked case.

### 9.19 Triển khai tiếp

Q-C objective graph P00-01..05 (runtime records từ source, loader/adapter/validator phía Qoder, không compiler cạnh tranh), Q-D XP/level + stat transaction một khối, Q-E loot grant + equipment cho cơ chế đã có data, Q-F Mãng Cốt encounter proposal + state machine, Q-G E2E nhiều client + handoff + proposal PostgreSQL (`Server/Persistence*` thuộc Remote #79).
