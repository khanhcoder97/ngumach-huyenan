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

1. **Mob level theo spawn:** dùng bảng REFERENCE_L5 của design resolution làm baseline prototype, hay owner có nguồn level/spawn khác?
2. **Đánh thường:** đưa basic attack 3×100% vào subset (cần cho vòng săn quái) hay giữ skills-only?
3. **Transport damage:** mở `hits[]` trong response `/p1/combat` (đề xuất) hay chỉ qua snapshot entity hp polling, hay mở transport `CombatCastEvent` riêng?
4. **Loot:** nguồn quy tắc "Đồng theo band" và roll 12% material (seed/rounding) lấy từ đâu, hay để QOD-C/D?
5. **Phản Quang:** case counter/DR còn thiếu — chờ owner quyết định hay Qoder soạn proposal con riêng?
6. **Snapshot visibility:** entities gồm cả GATHER_NODE/INTERACTABLE (27 instance đầy đủ) hay chỉ MOB/BOSS/NPC?
