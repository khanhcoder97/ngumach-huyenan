# Proposal Q-F — Mãng Cốt encounter (QOD-19 nối tiếp QOD-18)

Trạng thái: **proposal, chưa có code encounter nào**. Boss vẫn `BOSSDATA_BLOCKED` trong `combat_mob_stats_v1.json`, P00-05 giữ `BLOCKED` ở đúng step `bossStats`.

## 1. Nguồn đang có

| Nguồn | Cho biết gì |
|---|---|
| `Production_Rules_Complete_v1_vi.md` §4 | 3 phase; **3 đòn**; ưu tiên chọn đòn **C → B → A**; ngưỡng chuyển phase **60% / 30%**; **không overlap** hai đòn |
| `Quest_and_Narrative_Production_Spec_vi.md#P00-05` | vào boss ring; hạ Mãng Cốt; tương tác mảnh ấn; xác nhận môn phái tại `NPC_CLASS_TRIAL`; boss reset khi cả đội rời; thưởng vũ khí lớp + mở Thanh Lạc/Chương I |
| `world_records.json` | `MAN-BM-EVENT_BOSS_BM_MANG_COT` (ACTIVITY_BOSS) và `MAN-BM-SPAWN_BM_05_QUEST` (ATLAS_BOSS), cùng toạ độ **(178, 0)**, cùng `BOSS_MANG_COT` → trùng lặp cần chốt |
| packet `3a01b14` (`docs/narrative/gameplay`) | prose P00-05: Mãng Cốt trồi giữa cọc, nước dồn theo thân, lối phía kho còn cao (gợi ý safe pad), “giữ khoảng trống để lui”, mảnh sáng dưới đầm để sau |
| `combat_mob_stats_v1.json` | `BOSS_MANG_COT` = **BOSSDATA_BLOCKED** (không HP/ATK/armor) |

## 2. Thiếu nguồn — blocked case (không tự đặt số)

| Field | Vì sao chặn | Cần từ |
|---|---|---|
| `arena` polygon + `safePad` toạ độ/bán kính | prose nói “lối phía kho còn cao”, không có hình học | Map Atlas §Đầm Chuông hoặc owner |
| `maxHp / attack / armor / defense` | bundle đánh dấu BOSSDATA_BLOCKED | `REFERENCE_L5`-tương đương cho boss (nguồn số, không phải balance) |
| Danh sách 3 đòn A/B/C: tên, telegraph, damage, shape | Rules nêu thứ tự ưu tiên, **không** nêu số | bảng move boss trong Content Bible |
| Phase threshold đã có (60/30) nhưng **đổi gì** ở mỗi phase (thêm đòn? speed?) | Rules chỉ nêu ngưỡng | Rules §4 chi tiết / owner |
| `phaseGuard` (miễn nhiễm khi chuyển phase, bao lâu) | chưa có | design |
| `interruptibility` (đòn nào ngắt được, bằng gì) | chưa có | design |
| Loot band boss + gear roll vector | loot bundle đang grant OFF; gear vector không tồn tại | như Q-E đã ghi |
| Attempt/reset policy (số attempt, wipe về phase 1 hay checkpoint) | source chỉ nói “reset khi cả đội rời” | Rules §4 |
| Contribution/kill-ledger (ai nhận credit) | chưa có luật | owner |

## 3. State machine đề xuất (chỉ dựng khi có số)

```
IDLE → ENGAGED(phase 1) → [hp ≤ 60%] PHASE_GUARD(2) → phase 2
                        → [hp ≤ 30%] PHASE_GUARD(3) → phase 3 → DEAD → (reset theo policy)
         ↘ WIPE/RETREAT (cả đội rời ring) → IDLE, boss hồi đầy theo policy
```

Bất biến (đã có nguồn, sẽ khoá bằng test):
1. **Không overlap**: tại một tick, tối đa một đòn boss đang resolve; đòn mới chỉ mở sau khi đòn trước vào RECOVER.
2. **Ưu tiên C→B→A** khi nhiều đòn cùng thoả điều kiện; tie-break theo thứ tự cố định, không random.
3. **Ngưỡng 60%/30%** đánh giá **sau** damage của impact (giống DEC-022: damage trước, survival/phase sau) và chỉ chuyển **một** phase mỗi lần vượt ngưỡng.
4. Trong `PHASE_GUARD` boss không nhận damage mới (hoặc theo field `phaseGuard` khi có), không đổi mục tiêu, không phát loot.
5. Wipe/leave ring: không loot, không unlock portal, `lifeId` không bump cho tới khi policy reset chạy.
6. Boss death chỉ một lần mỗi `lifeId`; late event sau reset không cộng reward lần hai.

## 4. Điểm nối vào server hiện tại

- `CombatTickEngine` đã có: cast scheduling, `MobCombatStateStore` theo lifeId, DEATH một lần/life, kill credit qua event `KILL`, guard/counter DEC-022, loot grant hook (hiện grant OFF).
- Boss cần thêm: `BossEncounterService` (phase + attack schedule) chạy trên cùng `WorldTickBackgroundService`; event boss (phase change, wipe, reset) **chưa có type trong `CombatEventV2`** → phải đề xuất contract mới, không nhét field lạ.
- P00-05 objective `BOSS` đã có target `BOSS_MANG_COT`; chỉ mở khi `bossStats` + `arena` có nguồn.
- Portal/Chapter unlock: `unlocks` của P00-05 hiện rỗng + blocked step `P00_05_CHAPTER_UNLOCK` (`C1-01` chưa có runtime record).

## 5. Test plan (khi có số)

- Fixture deterministic (`ManualServerClock`): HP đi qua 60% → đúng một lần PHASE_GUARD → phase 2; 30% → phase 3; không nhảy 1→3.
- Ưu tiên C→B→A: fixture 3 đòn cùng ready → chọn C; sau C vào cooldown → B.
- Không overlap: hai đòn “ready” cùng tick → chỉ một impact frame.
- Wipe: cả đội rời ring → boss reset, không loot, không unlock; quay lại → phase 1 (hoặc theo policy chốt).
- Death: một DEATH/life, loot hook một lần/death, replay event không cộng hai.
- E2E: P00-04 xong → vào ring → hạ boss → tương tác mảnh ấn (khi có record) → TALK `NPC_CLASS_TRIAL` → turn-in, chỉ khi tất cả nguồn đã có.

## 6. Câu hỏi cho owner (trước khi code encounter)

1. Hai record boss cùng toạ độ (178,0) — chốt dùng `ACTIVITY_BOSS`, bỏ/đổi record còn lại?
2. Cho số boss: HP/ATK/armor + 3 đòn (tên, damage, telegraph, shape) và phase-guard duration.
3. Wipe reset về phase 1 hay checkpoint gần nhất? Có giới hạn attempt không?
4. Có mở event type mới cho boss phase/wipe/reset trong `CombatEventV2` (cần version) hay chỉ dùng snapshot + `state` như hiện tại?
