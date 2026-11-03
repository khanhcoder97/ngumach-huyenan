# Packet hợp đồng Encounter Snapshot (QOD-21 Q2) — CHỜ DUYỆT, CHƯA CÓ ROUTE NÀO

Gửi Codex (review) + Antigravity #85 (client). Nguồn quyết định: `DESIGN-BM-ALPHA-20261103` (`Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json`), nhánh `boss` + `boss.eventProtocol` + `questRules.P00-05`. Packet này **chưa** áp dụng schema nào; `GET /p1/encounters/{encounterId}` chưa được map. Toàn bộ máy encounter phía domain đã chạy trên `WorldTickBackgroundService` sau gate `P1:AlphaProfile:Enabled` (mặc định OFF) mà không cần wire — wire chỉ là **đọc**.

## 1. boss.eventProtocol nói gì (verbatim, không tự ý thêm)

> keep CombatEventV2 closed types; expose phase/wipe state in new GET /p1/encounters/{encounterId} snapshot schema1 + entity revision; publish accepted existing cast/impact/death events only

Suy ra ba ràng buộc hợp đồng:
1. **Không** thêm event type mới (`PHASE_CHANGE`/`WIPE`/`RESET` không tồn tại trong `CombatEventV2` và sẽ không được thêm).
2. Trạng thái phase/wipe đi vào **một snapshot read-only mới**, schemaVersion 1.
3. Client vẫn nhận damage/hit/death qua các event v2 **đã có**; snapshot không thay thế chúng.

## 2. Contract đề xuất

### 2.1 Request

`GET /p1/encounters/{encounterId}` với header `X-Session-ID` (đọc, không idempotencyKey, không payload).

`encounterId` là **opaque id server cấp**, pattern `^ENC-[A-Z0-9]{8,32}$`; server sinh khi mở encounter (`ENC-` + 24 ký tự hex hoa của instanceId). Client **không** tự chọn và **không** gửi toạ độ nào cả.

### 2.2 Response `EncounterSnapshotV1` (additionalProperties:false)

```jsonc
{
  "schemaVersion": 1,
  "encounterId": "ENC-…",
  "questId": "P00-05",
  "bossRecordId": "MAN-BM-SPAWN_BM_05_QUEST",
  "bossEntityId": "ENT_MAN_BM_SPAWN_BM_05_QUEST",
  "bossLifeId": 1,
  "bossRevision": 7,
  "status": "OPEN",                       // OPEN | DEFEATED | RESET
  "phase": 2,                             // 1 | 2 | 3
  "bossHp": 700,
  "bossMaxHp": 1200,
  "serverTick": 1840,
  "registeredCharacterIds": ["CHR_…"],    // owner đăng ký lúc mở encounter
  "activeMove": {                          // null khi không có đòn nào đang resolve
    "moveId": "C",                         // A | B | C
    "state": "TELEGRAPH",                  // TELEGRAPH | IMPACT | RECOVERY
    "ticksRemaining": 12,                  // còn lại của state hiện tại, đơn vị tick 20 Hz
    "shape": {
      "kind": "ANNULUS",                   // CONE | CIRCLE | ANNULUS
      "centerXWu": 178.0, "centerYWu": 0.0,
      "angleDegrees": null, "rangeWu": null,
      "radiusWu": null, "innerRadiusWu": 3.0, "outerRadiusWu": 7.0
    },
    "targetLock": "BOSS_POSITION"          // TELEGRAPH_START_FACING | TELEGRAPH_START_TARGET_POSITION | BOSS_POSITION
  },
  "moveCooldownRemainingTicks": { "A": 0, "B": 30, "C": 18 },
  "phaseGuardRemainingTicks": 0,           // phaseGuardSeconds 1.0 = 20 tick
  "wipeCountdownTicks": 200,               // 10 s không mục tiêu sống = 200 tick; null khi chưa đếm
  "arena": { "shape": "CIRCLE", "centerXWu": 178.0, "centerYWu": 0.0, "radiusWu": 11.0 },
  "safePads": [                            // design.safePads; chỉ áp dụng phase 3
    { "centerXWu": 168.0, "centerYWu": 0.0, "radiusWu": 0.75, "applies": false },
    { "centerXWu": 188.0, "centerYWu": 0.0, "radiusWu": 0.75, "applies": false }
  ],
  "phaseNpc": {                            // questRules.P00-05.phaseNpcOverride: same actor, không clone thứ hai
    "npcId": "NPC_TA_VAN_KHANH",
    "xWu": 182.0, "yWu": 4.0,
    "active": true
  },
  "trialNpcVisible": false                 // boss dead AND fragment AND chưa COMPLETED
}
```

Mọi con số trên wire lấy từ **state server**, không từ request: HP/phase/tick do `ServerClock` và `BossEncounter` sở hữu; `arena`/`safePads`/`phaseNpc` là dữ liệu design đã validate lúc boot.

### 2.3 Lỗi (enum đóng, theo pattern `P1.ERROR.[A-Z_]+`)

`invalid_payload`, `session_not_found`, `encounter_not_found`, `character_not_registered`.

Quy tắc **isolation** (bất biến Q-G đã chứng minh ở two-client E2E): `encounterId` chỉ đọc được bởi session của character **đã đăng ký** trong `registeredCharacterIds`; người khác nhận `encounter_not_found` (không phải `forbidden`) để không lộ sự tồn tại của encounter thuộc người khác.

### 2.4 Gate

`P1:AlphaProfile:Enabled` (đang OFF trong `appsettings.json`). Gate OFF → route **không được map** (405 như các handler gated hiện tại), không phải 500. **Không** bật gate production; chỉ CI/buổi kiểm thử alpha cụ bộ mới bật.

## 3. Việc ĐÃ làm mà không cần packet (domain-only, không wire)

- `AlphaBossEncounterService`: mở encounter khi P00-05 `ACTIVE` + owner vào arena CIRCLE (178,0) r11; giữ `ENT_MAN_BM_EVENT_BOSS_BM_MANG_COT` dead suốt encounter (`worldEventRecordIdDisabledInQuestInstance`); timeline TELEGRAPH→IMPACT→RECOVERY theo `windupSeconds`/`recoverySeconds` của từng đòn, `phaseGuardSeconds` 1.0, recovery nhân `phase2RecoveryMultiplier` 0.8, damage nhân `phase3AdditionalDamageMultiplier` 1.0, ưu tiên C→B→A, không overlap; damage chỉ áp khi `P1:CombatDamage` ON; wipe sau 10 s không mục tiêu sống: `resetHp`, phase 1, episode mới vô hiệu hoá token cũ, `lifeId` mới, `questCheckpointPersists`, `noLootOnReset`.
- Credit theo `boss.credit`: chỉ owner đăng ký lúc mở và còn đủ điều kiện lúc chết; late join / event của life cũ không credit; party scaling tắt cho tới khi có roster authority.
- `phaseNpcOverride` và `trialNpcConditionOverride` là **state domain**; P1 không có wire vị trí NPC nên client chưa đọc được — đúng lý do packet này tồn tại.

## 4. Việc CHƯA làm, chờ duyệt packet này

1. `Implementation/Content/Schemas/EncounterSnapshotV1.json` + example (chỉ khi packet được duyệt).
2. `validate_contracts.py` thêm khoá semantic: `bossMaxHp == 1200` từ design, `phase ∈ {1,2,3}`, `status` ↔ `phase` nhất quán, `safePads` chỉ `applies` khi `phase == 3`, `activeMove.shape.kind` khớp move, `registeredCharacterIds` matches `^CHR_`, toạ độ finite và trong bounds `MAP_BEN_MUA`.
3. `GET /p1/encounters/{encounterId}` handler sau gate + DTO `EncounterSnapshotV1` (`P1Json` `JsonUnmappedMemberHandling.Disallow`).
4. smoke + e2e: một flow HTTP thật đọc snapshot, chứng minh isolation (client B nhận `encounter_not_found`), phase 2/3 xuất hiện đúng ngưỡng, wipe trả `status=RESET` với `bossHp` đầy và `bossLifeId` tăng.

## 5. Không nằm trong packet (ghi rõ để khỏi hiểu lầm)

- **Không** thêm `CombatEventV2` type nào (`boss.eventProtocol` cấm).
- **Không** expose `attack`/`armor` của boss như stat tổng quát; chỉ số damage đã đi qua event IMPACT hiện có.
- **Không** tự nối `MAP_THANH_LAC` portal hay flag `CHAPTER_C1_UNLOCKED` — đó là Q4 (`questRules.P00-05.unlock`), cần route/flag contract riêng.
- **Không** bật `P1:AlphaProfile` trong production, không tự đặt topology `REVIEWED`, không tự merge PR #106.

## 6. Câu hỏi cho owner

1. `encounterId` cấp theo **attempt** (mỗi `lifeId` một id) hay theo **quest attempt của character** (một id xuyên suốt, `status`/`bossLifeId` tự phản ánh reset)? Đề xuất: một id per (character, P00-05 attempt) để client không phải xin id mới sau wipe.
2. `registeredCharacterIds` có cho phép **muộn** không? Nguồn nói "late join and prior life events give no credit" → đề xuất: cho phép join sau khi mở (nhận credit từ life hiện tại), nhưng snapshot chỉ trả danh sách đang đăng ký.
3. Snapshot có cần cho **hai client cùng xem một encounter** (party) không, hay chỉ owner? P1 chưa có roster authority (`party scaling disabled`) → đề xuất: chỉ owner, và `registeredCharacterIds` giữ kích thước 1 cho tới khi có nguồn party.
