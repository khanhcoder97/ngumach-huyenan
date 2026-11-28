## Current outcome
The owner locked the existing whole-body chibi sprite-sheet style. This draft includes the Sprite/VFX Studio and two continued art batches: 27 selected source PNGs, 768 bound source cells (48 sixteen-frame sequences), and eight explicitly unused boatkeeper cells. All 46 owner-selected earlier PNGs remain byte-identical against the recorded baseline. Source/runtime copies, exact prompts, references and SHA256 inventories are committed.

The latest batch adds four idle angles each for Rễ Nước and Kẻ Rình Bờ, alongside their existing SOUTH sources, plus SOUTH-only Cá Linh telegraph/attack/recovery/hurt/death. Native review caught an over-stretched fish attack; attack/recovery v2 replace those bindings and rejected originals remain in history. The shore-stalker now uses long-axis scale calibration so horizontal views do not enlarge its body. Invalid older idle atlases are retired from active records without changing the old PNGs. These are review candidates, not blanket live-art approval.

The earlier batch adds Minh Kiếm hurt/dodge/death, a repaired Thạch Chùy attack, Cá Linh locomotion, Người Giữ Thuyền idle and separate VFX components. Kiếm Trận uses the approved 16-frame arc component in SkillVfxPlayer, with visual peaks at .10/.22/.36 seconds, exact-source hash gating, token deduplication, cancellation and sprite budgets. Damage/CD/MP/server contracts are unchanged.

Studio now offers 102 entries/groups, separate directional PNG references, per-frame transforms/pivots/layers/timing/VFX editing, one-shot defaults and original-byte bundle export. Raw and grouped Cá Linh previews agree on timing. Telegraph .45 s and recovery .50 s follow the visual bible; attack .30 s is explicitly an editable presentation assumption, never an authoritative damage window. A new native CarplingCombatReview scene exposes five actions and their three-phase join. Earlier paper-doll experiments in the draft history are superseded by the owner's baked-sprite direction.

## Validation
- .NET 8 build: zero warnings/errors; Godot import succeeds.
- Latest native Studio: 44,154 assertions across 102 entries/groups.
- Latest native actor library: 11,472 frame/texture/gate/timing assertions, including all sixteen source poses at a 60-step clock and one-shot final-frame holds.
- Eleven Python regressions cover directional completeness, mirrors, component scope and overhead-creature scaling.
- Original audit: 46/46 baseline PNG hashes unchanged; 59/59 currently selected runtime source copies match bytes.
- Both batch inventories, catalogue and metadata/export reproducibility checks pass.
- Latest native PNG captures, logs and a two-second offline movie are under Implementation/Reports/Evidence/Actor_Batch_20261112b. Earlier VFX-component and visual-regression evidence remains under the first batch.

## Remaining scope
40/1008 required jobs have all structurally required source angles; 968 still lack sources. Only three full jobs are production-approved legacy clips; 28 pages retain visual HOLDs. Rễ Nước NE is too close to NORTH, rear creature anatomy needs further motion review, and the five new Cá Linh combat actions still lack four authored angles and final idle/combat continuity acceptance. One older full-skill VFX atlas remains structure-rejected, separate from the approved arc component. Source cell counts and hashes do not certify anatomical pose uniqueness.

The fixed-60-FPS movie is an offline art review, not a gameplay benchmark. This draft does not accept the complete actor/skill/NPC libraries or a shipping/PCK export. The source-client VFX hash gate still requires raw PNG preservation or an exported-resource verification path before release acceptance.

See docs/production/Actor_Batch_20261112_vi.md, docs/production/Actor_Batch_20261112b_vi.md, their batch JSON inventories and implementation reports for exact files, review limits and next work.
