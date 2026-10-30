# QOD-15 — Headless E2E, hai profile và bàn giao client

**Issue:** #41. **Gói:** QOD-11 → QOD-15 theo `06_QODER_GAMEPLAY_LOOP_EPIC.md`. Mốc cuối của gói: một command chạy server + scenario headless, hai profile gate, CI, và bàn giao cho OpenCode/Muse.

**PR stacked:** PR QOD-15 base là `qoder/qod-14-turnin-reward` (PR #54 đang chờ merge; không tự merge).

## 1. SHA và kết quả kiểm tra thật

| Nhánh | SHA | Nội dung |
|---|---|---|
| `qoder/qod-14-turnin-reward` | `8802a3b` | Turn-in endpoint + reward nguyên tử (QOD-14) |
| | `f6149d9`, `ed1fe91` | Fix build: using + object initializers + biến trùng self-check |
| | `006e2cd` | Chống double-grant khi turn-in song song + failure-injection/concurrency self-check |
| `qoder/qod-15-headless-e2e` | `8a565e7` | E2E runner hai profile, `server-e2e.yml`, README |

CI trên `006e2cd` (QOD-14): `server-build` SUCCESS, `server-smoke` SUCCESS (136 self-check + smoke HTTP), `contract-validation` SUCCESS, `content-validation` SUCCESS. CI QOD-15 chạy khi mở PR stacked.

Lệnh kiểm tra (từ clone mới, cần dotnet SDK 10 + python3):

```bash
dotnet build Server/Health/Health.csproj --configuration Release
dotnet Server/Health/bin/Release/net10.0/Health.dll --self-check          # 136 checks, exit 0
bash Server/Health/Smoke/run_e2e_p1.sh default                            # profile mặc định: expected blocked
bash Server/Health/Smoke/run_e2e_p1.sh dev                                # dev synthetic: golden loop
python3 Implementation/Tools/validate_contracts.py                        # schemas + examples
python3 Implementation/Tools/validate_content.py
```

Smoke HTTP đầy đủ (session/move/combat/quest/interact/gather/turn-in) chạy bằng server có 3 flag bật + `python3 Server/Health/Smoke/smoke_p1.py http://127.0.0.1:5080` (workflow `server-smoke`).

## 2. Hai profile (chưa có topology REVIEWED)

**Default (production gate OFF)** — server không set flag. Expected blocked output là chính assertion của profile: `POST /p1/quests/accept`, `POST /p1/world/interact`, `POST /p1/quests/turnin` không được map handler; request rơi xuống template route GET read (`GET /p1/quests/{sessionId}`, `GET /p1/world/{sessionId}`) → HTTP 405 (minimal API trả 405 khi method khớp template nhưng không có handler, không phải 404); session/move/read vẫn chạy bình thường. Không sửa `reviewState` hay tự bật gate để demo.

**Dev synthetic (3 flag ON)** — `P1__QuestAccept__Enabled`, `P1__Interact__Enabled`, `P1__QuestTurnIn__Enabled` = true. Golden loop:

```
tạo session (18,0) → move hợp lệ (revision tăng) → bước qua tường x=45..46
→ accept P00-01 tại NPC_LYAN (ACTIVE, rev 2) → collect 3 kiện Atlas
(revision 3,4,5, counters 1..3, READY_TO_TURN_IN) → turn-in tại
NPC_TA_VAN_KHANH (COMPLETED rev 6; COIN 20 + EQ-MK-CHEST-T1-R-COMMON;
XP applied=false; unlock P00-02) → replay cùng key trả kết quả đã lưu
→ key mới 409 invalid_transition → inventory/quest readback đúng một
phần thưởng → hai turn-in song song khác key: đúng một winner →
guard sai characterId (400) và session lạ (404)
```

**Bước tường (wall-crossing)**: fixture topology `SYNTHETIC_TEST_ONLY` → server trả `NotEnforced`, move thành công và script ghi `wall_enforcement=not_enforced`. Khi có bundle `REVIEWED`, move đó phải trả 422 `movement_blocked`; script chấp nhận **đúng hai** kết quả này và fail với mọi kết quả khác (khi REVIEWED xuất hiện, script phải được cập nhật lộ trình đi vòng). Logic chặn tường thật đã được self-check kiểm deterministic bằng bundle REVIEWED synthetic in-memory (`los.wall`, `sweep.wall`, `sweep.corner`, `sweep.footprint`...).

## 3. Bàn giao OpenCode/Muse — event lifecycle → VFX semantic

| Sự kiện (wire) | Trường dùng | VFX/UI semantic |
|---|---|---|
| Combat `combat.effect` (`CombatEvent`) | `eventId`, `eventType`, `aggregateId`/`aggregateRevision`, `emittedAtUtc`, `payload.sourceId`, `payload.targetId`, `payload.skillId`, `payload.cooldownEndsAtUtc` | Key animation theo `eventId`; cast pose theo `skillId` từ `sourceId`; bộ đếm CD theo `cooldownEndsAtUtc`. `payload.damage`/`hit` **không được phát trong P1** (chưa có numeric canonical) — client không được vẽ damage số |
| Combat `combat.death` | (dự kiến, chưa emit) | Death anim + despawn entity theo `payload.targetId` — hiện chỉ có ở mob lifecycle service-level, không lên wire |
| Interact collect (`InteractResult`) | `interactionId`, `targetId`, `recordId`, `kind=INTERACTABLE`, `outcome=collected`, `targetState=DEPLETED`, `claimedAtUtc`, `respawnAtUtc` | Play collect VFX trên `targetId`; ẩn target tới `respawnAtUtc` |
| Interact gather (`InteractResult`) | `kind=GATHER_NODE`, `outcome=gathered`, `targetState=AVAILABLE`, `yield.itemId`, `yield.quantity`, `respawnAtUtc` | Loot fly + badge inventory theo `yield`; cooldown theo nhân vật (node vẫn AVAILABLE cho người khác) |
| Quest update (`QuestState` trong `questUpdates`) | `questId`, `state`, `stepId`, `objectiveCounters`, `revision` | Quest tracker UI; transition `AVAILABLE → ACTIVE → READY_TO_TURN_IN → COMPLETED`; `revision` cho optimistic concurrency |
| Turn-in (`TurnInResult`) | `questState`, `rewards.currency[]`, `rewards.items[]`, `rewards.xp.xpRule` + `applied`, `unlocks[]` | Reward fanfare theo từng currency/item; **XP `applied=false` → không tăng XP bar**; `unlocks` mở quest kế tiếp |
| Move/world (`P1Response` + `WorldSnapshot`) | `self.x/y/hp/mp`, `entities[].state`, `revision`, `serverTick` | Interpolation vị trí; đồng bộ trạng thái entity (`WorldEntity.state`) |
| Lỗi (`P1Error`) | `code`, `messageKey`, `retryable`, `fieldErrors` | Toast/handling theo `code`; `retryable` quyết định nút thử lại |

Request/response mẫu turn-in: `Implementation/Contracts/P1/Examples/TurnInRequest.example.json` và `TurnInResponse.example.json` (đã qua `validate_contracts.py`). Các endpoint còn lại có example tương ứng trong cùng thư mục.

## 4. Feature matrix — implemented / fixture-only / missing

**Implemented (chạy được, dev profile):**
- Session/move với sequence, distance cap, sweep kiểm cả đoạn đường (wall chặn khi topology REVIEWED — đã kiểm in-memory).
- Combat gate (class/sequence/cooldown/MP/target/range) + `combat.effect`; mob lifecycle tick 20 Hz (IDLE→…→DEAD→respawn) với LOS/leash/cooldown.
- Quest accept + interact collect/gather với claim/respawn per character, profession gate; progress **chỉ từ event server-verified**, mỗi event đóng góp một lần (dedupe theo record).
- Turn-in nguyên tử (grant → flip → ledger) dưới lock + re-check state trong lock: song song/retry chỉ thưởng một lần; replay cùng key trả kết quả đã lưu; failure-injection không commit phần nào.
- Readback quest/inventory; teleport validation (service-level, chưa có endpoint HTTP).

**Fixture-only (có nhãn DEV):**
- Topology Bến Mưa `SYNTHETIC_TEST_ONLY` (walls không enforced qua HTTP).
- Mob radius/speed fixture `P1:MobBehavior`; `AssumedProfessionLevel=1`; respawn giây của node/package trong entity fixture.
- Reward số của P00-01 lấy từ dữ liệu quest canonical (COIN 20 + chest), không phải số tự bịa.

**Missing (không giả vờ):**
- Damage/HP/ATK/DEF numeric canonical → combat không phát damage/hit/death/loot trên wire.
- XP system → `xp.applied=false`; ledger/quest/inventory/session in-memory mất sau restart; không auth, không durable exactly-once.
- Inventory capacity → không có lỗi "túi đầy" (P1 không giới hạn túi).
- Topology `REVIEWED` → production gate còn OFF; teleport endpoint; 30 skill/46 map là backlog.

## 5. Gate và giới hạn

- Gate `P1:QuestAccept`, `P1:Interact`, `P1:QuestTurnIn` mặc định `false`; chỉ bật cho dev scenario/fixture. Không tự nới gate khi chưa có topology REVIEWED.
- HTTP move dùng `ServerClock` thật; fake clock (`ManualServerClock`) chỉ dùng trong self-check (respawn, mob lifecycle) — không cần sleep.
- Trạng thái toàn bộ là in-memory P1: **không gọi đây là durable hay production MMORPG**.

## 6. Checklist gói QOD-11 → QOD-15

- [x] QOD-10 (đã merge trước) — topology validation
- [x] QOD-11 → PR world/tick/move + topology (đã merge)
- [x] QOD-12 → combat subset + mob lifecycle (đã merge)
- [x] QOD-13 → quest progress + interact/gather (PR #53 chờ merge)
- [x] QOD-14 → turn-in + reward nguyên tử (PR #54 chờ merge; CI xanh trên `006e2cd`)
- [x] QOD-15 → E2E hai profile + CI + bàn giao (PR stacked chờ merge)
- [ ] Khi Muse giao bundle `REVIEWED`: bật production gate theo proposal riêng, cập nhật bước tường của E2E
