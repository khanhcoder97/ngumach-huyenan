## Current outcome
The active art route uses the owner-selected whole-body chibi sprite sheets and Sprite/VFX Studio. Three rolling batches currently select 49 source PNGs with 1,120 bound source cells (70 sixteen-frame sequences) and eight explicitly unused boatkeeper cells. All 46 baseline PNGs remain unchanged. Exact prompts, source references, hashes, original-byte runtime copies and native review media are committed.

The latest batch selects 23 sheets / 368 cells: twenty N/NE/E/SE combat pages for Cá Linh, a clearer rear-diagonal Rễ Nước revision, and SOUTH walk/interact for Người Giữ Thuyền. Together with existing SOUTH sources, Cá Linh now has five authored angles / eight permitted viewing directions for telegraph_01, attack_01, recovery_01, hurt and death. Wrong-compass/opening-attack atlases, an incorrect hurt start, a tail-coil transition and same-foot NPC walk attempts are excluded from active bindings and retained in rejection history. NPC walk/interact still lack four authored angles each.

Fish registration now reads the silver torso centroid instead of anchoring on a flexible tail, and normalizes by the neutral long axis. PNGs are never warped or repainted by code. Original foot registration remains for other actors. Thirty-two source pages have explicit visual clip reviews pinned to both PNG SHA256 and rect/pivot/scale/direction binding SHA256. These are source-clip decisions, not whole-actor, encounter or shipping acceptance. A changed source or registration invalidates its pipeline approval.

Studio has 126 entries/groups, directional source references, timing/pivot/layer editing, original-byte bundle export and one-shot interaction defaults. The native combat review can select all eight directions. The library counts complete direction sets, labels offline movies honestly and rejects Movie Maker as a real-time benchmark. Telegraph .45 s / recovery .50 s follow the bible; attack .30 s remains an editable presentation assumption.

The earlier batches retain Minh Kiếm hurt/dodge/death, Thạch Chùy attack, Cá Linh locomotion, boatkeeper idle and separate VFX components. Kiếm Trận uses the native-reviewed 16-frame arc component with three visual peaks at .10/.22/.36 seconds, exact-source hash gating, cancellation, deduplication and sprite budgets. Gameplay/server contracts are unchanged.

## Validation
- .NET 8: zero warnings/errors; Godot import succeeds.
- Native actor library: 11,934 assertions, including sixteen-frame sampling at a 60-step clock for all eight directions of five combat actions and one-shot holds.
- Native Studio: 49,990 assertions across 126 entries/groups; NPC walk loops and interaction holds the final frame.
- Twenty Python regressions cover authored-direction completeness, scale, fish registration and source/binding approval invalidation.
- VFX component regression: fourteen assertions; offline benchmark rejection verified natively.
- All 46 baseline PNG hashes remain unchanged; all 81 currently selected runtime source copies match original bytes.
- Catalogue, all three batch inventories and metadata/export reproducibility checks pass.
- Native source sheets, eight-angle PNGs, five-direction combat videos, hurt/death, root idle and NPC media/logs are under Implementation/Reports/Evidence/Actor_Batch_20261112c.

## Remaining scope
The actor/skill catalogue has 84 structure-passed pages, 45/1008 required jobs with all source angles, and nine complete-angle jobs with visual source acceptance. 963 jobs still lack sources; nineteen active pages retain HOLDs, and an older full-skill VFX atlas remains structure-rejected. The approved sword arc remains a component, not a full-skill job. These counts do not include every map/tile/UI/icon/audio deliverable in the broader asset library.

The complete asset-library objective remains active. Remaining work includes NPC angles, creature locomotion/turn/secondary attacks, class skill-body choreography and VFX, plus broader art-plan deliverables. Offline 60 FPS encoding is not a gameplay benchmark. The draft does not accept complete actors, all gameplay integration or shipping/PCK export; the existing source-client VFX hash gate still needs raw PNG preservation or a tested exported-resource verification path for release.

See docs/production/Actor_Batch_20261112c_vi.md and its implementation report, inventory and pinned visual decisions for exact files and acceptance limits. Earlier batch reports describe their original deliveries; rolling inventories reflect current selections, including the moved root NE revision.
