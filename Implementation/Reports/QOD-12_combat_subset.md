# QOD-12a — Supported subset combat và kế hoạch mob lifecycle

**Issue:** #41. **Trạng thái:** inventory/contract proposal trước khi code wire (theo `06_QODER_GAMEPLAY_LOOP_EPIC.md`, QOD-12). Không có thay đổi runtime combat trong PR này; `P1:QuestAccept` và các gate production giữ nguyên.

## 1. Skill hiện có vs mechanics canonical

Canonical: `Implementation/Content/Examples/SkillDefinition/SK-MK-0{1,2,3}.json`, `Top_Down_Gameplay_World_Spec_vi.md` §4 (range WU), `Production_Rules_Complete_v1_vi.md` (damage/status là tuning v1, chưa khóa content).

| Skill | Targeting | Range | MP/CD | Hỗ trợ hiện tại | Chưa hỗ trợ (blocked) |
|---|---|---|---|---|---|
| `SK-MK-01` | SELF | không dùng range | 12 / 10s | Gate class/sequence/target self/cooldown/MP; phát `combat.effect` (không damage) | Damage, status, self-damage — không suy từ SELF |
| `SK-MK-02` | DASH | 11 WU | 16 / 8s | Gate + range + target alive/map/floor; LOS khi có topology `REVIEWED` | Dịch chuyển nhân vật (dash movement), damage, knockback |
| `SK-MK-03` | CONE | **chưa có** `rangeWu` | 22 / 10s | Gate + target resolve (khi registry có target) | Range/angle chính xác, damage — **không đoán số** |

`Phản Quang` (counter), shield/heal/status: **không có** trong 3 definition hiện tại → unsupported, không tự thêm.

## 2. Damage/HP policy

- Không có HP/ATK/DEF canonical cho mob trong content. Mọi số HP/damage dùng cho test phải nằm trong **dev fixture có nhãn** (ví dụ `P1:Combat:DevFixtureMobHp` + report ghi rõ "DEV FIXTURE, NOT CANONICAL"), mặc định **không bật** trên production path.
- Damage formula theo `Production_Rules_Complete_v1_vi.md` chỉ được implement khi có bảng numeric được version hóa; trước đó endpoint chỉ chứng minh gate và lifecycle, không phát damage giả.
- Client không bao giờ gửi amount/reward; mọi HP/MP/cooldown do server quyết định.

## 3. Mob lifecycle (kế hoạch QOD-12b)

- State: `IDLE → PATROL → AGGRO → CHASE → ATTACK → RETURN → DEAD → RESPAWN` (map với `WorldEntityRegistry` hiện có: `ALIVE`/`DEAD` + respawn timer).
- Gate: target alive/cùng map/floor, home/leash radius, LOS theo `WorldGeometryService`, cooldown attack; reset rõ khi mất aggro hoặc về home.
- Hành vi/thuật toán chưa có dữ liệu canonical dùng config fixture có nhãn; không ghi vào content canonical.
- Chống double kill/loot: chuyển state `DEAD` một lần theo revision; loot/reward thuộc QOD-14.

## 4. Idempotency & race (kế hoạch)

- Replay cùng `idempotencyKey` + payload của một command đã accepted trả đúng kết quả trước, trước cả stale-sequence guard; payload khác cùng key → `idempotency_conflict`.
- Race hai request cùng actor không trừ MP hai lần, không phát hai impact; hai người đánh cùng target chỉ một death event.
- Rejected cast không phát impact/loot trong bất kỳ event bus nào.

## 5. Test matrix deterministic (QOD-12b)

| Case | Kỳ vọng |
|---|---|
| Cast hợp lệ `SK-MK-01`, `SK-MK-02` có target | accepted, MP/CD/revision đúng một lần |
| Sai class/sequence/cooldown/MP | reject đúng code, state không đổi |
| Target chết/khác map/khác floor/ngoài leash | `target_not_found`/`out_of_range` |
| Wall chặn LOS (topology `REVIEWED` fixture) | reject, không phát impact |
| Replay cùng key+payload | cùng kết quả, không trừ MP lần hai |
| Cùng key khác payload | `idempotency_conflict` |
| Hai request đua cùng target | một death, một reject |
| Cancel/death giữa cast | `CAST_CANCEL`, không impact |

## 6. Cast event contract

Xem proposal `Implementation/Work_Orders/Proposals/QOD-12_CombatCastEvent_vi.md` và schema `Implementation/Contracts/P1/CombatCastEvent.schema.json` (mới, versioned, **chưa emit**). Legacy `CombatEvent` giữ nguyên cho client hiện tại.

## 7. Blockers

1. Chưa có numeric HP/ATK/DEF canonical → damage chỉ chạy bằng fixture có nhãn.
2. `SK-MK-03` thiếu `rangeWu` → chưa thể kiểm range/angle.
3. Chưa có bundle topology `REVIEWED` → LOS trong combat chỉ chạy khi có fixture review; production gate OFF.
4. VFX 30 skill là design-only, không dùng làm nguồn damage/range.

## 8. QOD-12b một phần — world targets (đã implement)

- `WorldEntityTargetProvider` resolve mob/boss instance `ENT_*` từ `WorldEntityRegistry`; chỉ trả target khi `State = ALIVE`; map/floor/position lấy từ spawn canonical.
- `CombatTarget` đổi sang `(EntityId, MapId, FloorId, X, Y, Alive)`; combat service reject `target_not_found` khi khác map **hoặc** khác floor; `PlayerSession.FloorId` mặc định `OVERWORLD`.
- DI: `ICombatTargetProvider` là composite (world registry + in-memory test registry), nên self-check/dev vẫn upsert target giả được.
- Test mới: resolve mob 84,0; NPC bị từ chối; `SK-MK-02` ngoài 11 WU → `out_of_range`; `SK-MK-03` (chưa có range) resolve target thật và trừ MP 22; target khác floor → `target_not_found`. Tổng self-check 80.
- Vẫn **không** có damage/HP: mob chết/aggro/leash/respawn AI là phần tiếp theo của QOD-12b, dùng config fixture có nhãn.

## 9. QOD-12c — idempotency cast (đã implement)

- `ICombatService.Resolve` nhận `idempotencyKey`; store theo `(characterId, key)` giữ request hash + `CombatOutcome`.
- Replay cùng key + cùng payload trả lại đúng outcome đã lưu **trước** stale-sequence guard (không trừ MP/cooldown/revision lần hai); cùng key khác payload → `409 idempotency_conflict`.
- Chỉ accepted outcome được lưu; cast bị từ chối không tạo entry và không phát impact giả.
- Test mới: replay giữ nguyên MP 38/revision 2 và cùng event; conflict khi đổi `inputSequence` với cùng key. Tổng self-check 82.
