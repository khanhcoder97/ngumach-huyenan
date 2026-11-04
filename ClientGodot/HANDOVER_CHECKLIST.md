# Handover checklist — M-A checkpoint (Work Order 24)

Delivery form: **partial handover** (Work Order 24 §"Tổ chức source và giao
nhận" item 3): source complete; asset completeness listed explicitly below.
Nothing in this file is marked APPROVED/REVIEWED by Muse — review and
merge belong to Codex, release approval to the project owner.

## Missing SOURCE — none for the current client scope

- [x] project.godot, csproj/sln, packages.lock.json, nuget.config
- [x] All C# scripts + scenes (Main + 8 test scenes)
- [x] Export presets (keystore paths emptied — no secrets in repo)
- [x] Build / test / Windows-export scripts; Android CI workflow
- [x] Art-data pipeline tools (converters, detail/portrait builders)
- [x] DEC-024 proposed patch: `docs/DEC-024_proposed_patch.md`

## Missing / pending ASSET (release-grade)

- [ ] **Vietnamese pixel font** — does not exist yet (full diacritics/NFC/
      line-height/license requirements per M-C). HUD currently falls back
      to the engine default font.
- [ ] **Linh Cung formal closure** — sprite set is audit-clean (496 cells,
      ART_REVIEW 2026-11-03) but the owner has not formally closed it.
- [ ] **Style-2 map presentation + new tiledata (5,375 blocked)** —
      owner-approved 2026-11-03; runtime integration pending: converter and
      main-scene asserts still pin the old 5,069 count, the detail builder
      still reads the round-13 source, the minimap needs a style-2 render,
      and boats have no runtime position/layer yet. For the 306 water
      cells specifically, Work Order 24 M-C requires an evidence pack for
      Codex's decision in deliveries — the local draft blocked them, this
      checkpoint ships the pre-change tiledata unchanged. Owner decision
      2026-11-04 (option B): the shipped tilemap was reverted to exactly
      that pre-change state (blocked 5,069; converter assert and the
      FullMapMain check pinned back to 5,069), and the M-C evidence pack
      ships with this checkpoint at `docs/evidence_water_block_20261104/`
      for Codex's decision.
- [ ] **Placeholder NPC art** — excluded (no license, prototype-only).
- [ ] **Production Android keystore** — owner's; CI uses a generated
      debug keystore.
- [ ] **Monster/boss/NPC/VFX production art wiring** — M-B scope.

## Pending integration (later work-order packages)

- [ ] M-B: full chain menu→session→map→quest/NPC/inventory/equip/
      target/attack/skill/cinema→death-return→boss→turn-in→portal, on
      OPC-15 interfaces (PR #109) + QOD-21 server alpha (PR #106);
      pending routes stay fixtures with a DRAFT/OFFLINE banner.
  - [x] HUD board-06 attached to Main.tscn (M-B checkpoint 2026-11-04):
        attack/skill wiring, minimap tracking, joystick feed; vitals
        stay at HUD defaults offline (online scene uses snapshots).
        Proven by SELFTEST additions.
  - [x] Class cards for server-unsupported classes are **disabled
        with a reason** (M-B checkpoint 2026-11-04): preview kept
        (dimmed portrait), reason on the card + notice line, choosing
        refused at the menu; the gate mirrors OPC-15 ClientCapability
        (alpha: CLASS_MINH_KIEM only) and binds to
        ClientCapability.IsClassSupported when Shared/ClientCore merges
        into this branch. Proven by the rewritten SELECTTEST.
- [ ] M-C: 48×64→64×64 via versioned manifest; boss-move mapping
      ART-P1-013; telegraph/reduced-flash checks.
- [ ] M-D: Windows-first verification (cold-import timeout/log ✓ in
      export_windows.sh; low-preset FPS measurement — alpha target
      30 FPS on the owner's machine class, TO MEASURE; SDK-less machine
      check). Android: CI only, real APK artifact required for PASS.
