# QOD-24 — Đối chiếu Narrative Depth / Discovery v2 với runtime (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `Narrative_Depth_and_Discovery_vi.md` (89 dòng)
dưới góc độ server; đối chiếu §3 reveal/guard, §7 discovery beats, §8 cinema authority với
`Narrative_Quest_Beats_v2.json`, `Cinema_Production_Pack_v1.json`, `validate_narrative.py`,
`build_narrative_nodes.py`, `NarrativeNodes.cs`/`NarrativeFlagStore`. Báo cáo-only: không mở
route/gate/wire, không sửa nguồn, không thêm anchor vào manifest 349.

## 1. Trạng thái runtime + CI đo được

- **Beats layer là DESIGN_HANDOFF, không runtime-load**: `Narrative_Quest_Beats_v2.json`
  có `schemaVersion=1`, `activation=DESIGN_HANDOFF`, `quests` 76 phần tử, mỗi phần tử
  questId/title/clue/dramaticQuestion/playerAgency/payoff/scope/newAnchorPolicy. Server grep
  `QuestBeats`/`Beats_v2`/`newAnchorPolicy`/`dramaticQuestion` = 0 → không loader runtime.
- **CI-gated ở build time**: `content-validation.yml:23–24` chạy `validate_narrative.py`;
  `:49/55` chạy `build_narrative_nodes.py` sinh `narrative_nodes_v1.json` và gate drift
  (`git diff --exit-code`). Đo chạy validator: **PASS 76/76 quest beats, 20 scenes, 63 shots,
  378 seconds** (exit 0); "Video generation and runtime guards unverified".
- **Runtime reveal/flag có thật**: `NarrativeNodes.cs` condition-gate (reveal gate) +
  `NarrativeErrorCodes.NotRevealed="narrative_not_revealed"`; `NarrativeFlagStore`
  `Capacity=128`/character, FIFO eviction, flag ngoài vocabulary bundle không thể ghi
  (validate lúc load). Đây là hiện thực "guard quest" phía server.

## 2. Phần khớp (đo từ nguồn)

- **Coverage 76/76 enforced**: `validate_narrative.py:19` bắt `set(beats.questId) ==
  set(dialogue CSV quest_id)` và không duplicate. Đo: beats_ids = csv_ids = 76,
  `beats_minus_csv` = `csv_minus_beats` = rỗng.
- **Scope/policy đồng nhất khớp spec §7**: cả 76 beat `scope=
  PRESENTATION_EXTENSION_NO_COUNT_OR_REWARD_CHANGE` và `newAnchorPolicy=
  PROPOSAL_REQUIRED_IF_NEW_WORLD_PLACEMENT` — đúng "giữ count/reward/quest IDs; beat đòi
  anchor/flag mới phải mở proposal trước khi sửa runtime; không ghi tọa độ suy đoán vào 349".
  Beats là file handoff riêng, không đổi manifest.
- **Cinema handoff validated**: `validate_narrative.py` bắt scene có sceneId duy nhất,
  questId ∈ dialogue set, characters ∈ manifest entities, `durationSeconds == tổng shot`,
  5 field non-empty (triggerDescription/**revealTier**/purpose/fallback/**serverAuthority**);
  shot duy nhất, duration==6, prompt≥400 ký tự. 20 scene/63 shot/378s đều PASS.
- **Server-authoritative reward**: turn-in commit phía server, không phụ thuộc client video
  (README idempotency) — khớp nguyên tắc §8 "server commit objective/reward độc lập, không
  tin video ended". Flag per-character + vocabulary-lock khớp "không ghi suy đoán thành sự
  thật server" (§3).

## 3. Khoảng trống (field cụ thể, đo được)

1. **revealTier/serverAuthority là metadata cinema, không field server**: chúng nằm trong
   `Cinema_Production_Pack_v1.json` và được validator bắt non-empty, nhưng Server grep
   `revealTier`/`RevealTier` = 0. Validator nói rõ "runtime guards unverified". Runtime gate
   bằng condition-key + flag, **không** có reveal-tier số phân tầng cho codex/video.
2. **Presentation receipt (§8) vắng**: "một lần trigger ghi presentation receipt; xem lại
   không phát thưởng" — Server grep `presentationReceipt`/`PresentationReceipt` = 0. Ledger
   idempotency reward có (bounded 256) nhưng không receipt riêng cho cinema trigger; chưa
   phân biệt "đã xem presentation" với "đã nhận reward".
3. **Trust policy (§7) vắng**: choice C3-05 set flag `C3_05_PUBLISHED`/`C3_05_COUNCIL_ONLY`
   nhưng Server grep `Trust` = 0 (hit "trusted" là comment client-timestamp, không liên quan).
   Không policy mapping nào tiêu thụ flag choice thành điểm Trust/Danh Vọng. Spec nói "Trust
   chỉ đổi khi policy cũ có mapping, không tự phát thêm điểm" — không auto-score là đúng,
   nhưng không tồn tại Trust policy nào.
4. **Journal 3 trạng thái (§3) vắng**: "quan sát / giả thuyết / đã đối chiếu" — flag runtime
   là binary set/unset (`NarrativeFlagStore`), không phân loại chứng cứ 3 mức; không field
   journal-state server.
5. **Hint timer 30s/60s (§7) + choice-phase/world-state (§8)**: marker 30s gợi ý / 60s chỉ
   đường là client presentation, không field server; flag per-character nhưng không cơ chế
   phase riêng tách world-state khỏi lựa chọn cá nhân đo được (spec §8 "không giả toàn server
   đã chọn cùng người chơi").

## 4. Câu hỏi owner (chưa tự quyết, chưa mở wire)

1. **Cinema authority/receipt**: revealTier + serverAuthority + presentation receipt thuộc
   làn server (cần service/receipt mới) hay client/Muse presentation? Validator đã disclaimer
   "runtime guards unverified" — ai sở hữu guard runtime cho cinema trigger?
2. **Trust mapping**: C3-05 choice (PUBLISH/COUNCIL) có policy Trust/Danh Vọng cũ để mapping
   không, hay Trust là post-P1? Nếu có, nguồn policy ở đâu (không tự phát điểm)?
3. **Journal evidence 3 mức**: mở rộng flag server thành quan sát/giả thuyết/đã-đối-chiếu
   hay để client journal suy ra từ flag hiện có? (Liên quan §3 "không ghi suy đoán thành sự thật".)
4. **Beats newAnchorPolicy**: cả 76 khai `PROPOSAL_REQUIRED_IF_NEW_WORLD_PLACEMENT` — xác nhận
   chưa beat nào đòi anchor mới (manifest không đổi); mọi placement tương lai đi qua proposal
   + review 349 trước khi sửa runtime. Có beat nào playerAgency ám chỉ placement mới cần duyệt sớm?

## 5. Nguồn đối chiếu

- `docs/production/Narrative_Depth_and_Discovery_vi.md` (§3/§7/§8).
- `Implementation/Content/Narrative/Narrative_Quest_Beats_v2.json` (76 beat, DESIGN_HANDOFF),
  `Cinema_Production_Pack_v1.json` (20 scene/63 shot/378s).
- `Implementation/Tools/validate_narrative.py` (PASS 76/76), `build_narrative_nodes.py`;
  `.github/workflows/content-validation.yml:23–24/49/55`.
- `Server/Health/Gameplay/Quests/NarrativeNodes.cs` (condition-gate, NarrativeFlagStore
  Capacity=128, NarrativeErrorCodes.NotRevealed); `Server/Health/README.md` (idempotency).