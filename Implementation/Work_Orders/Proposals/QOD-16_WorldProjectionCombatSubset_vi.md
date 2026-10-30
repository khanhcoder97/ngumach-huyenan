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
- **Chưa làm (increment kế):** mob AI telegraph/attack/recovery damage, guard/whiff/counter DEC-022 runtime, spawn group expansion theo manifest (nhiều member/group ID/generation, clear-group respawn), loot/XP.

### 9.7 Triển khai tiếp

Event store (bounded buffer, cursor, resync) + AOI projection có hysteresis + endpoint v2 opt-in (`P1:CombatV2:Enabled` OFF mặc định; dev profile bật) + e2e dev mở rộng; sau đó QOD-17 tick combat (basic + MK03 damage, guard/counter state machine theo DEC-022, mob telegraph/death/respawn, kill credit theo entityLifeId/deathEventId).
