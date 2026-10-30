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

### 9.12 Triển khai tiếp

Guard/whiff/counter DEC-022 runtime (mob impact đi qua guard window của player), QOD-18 quest chain P00-01..05 + XP transaction, QOD-19 Mãng Cốt encounter, QOD-20 E2E/handoff + proposal PostgreSQL.
