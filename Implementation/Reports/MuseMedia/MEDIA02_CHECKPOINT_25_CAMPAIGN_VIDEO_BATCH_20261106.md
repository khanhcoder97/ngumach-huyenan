# MEDIA-02 Checkpoint 25 — Campaign video batch (Gói 30 item 7)

Date: 2026-11-06 (JST) · Branch: `muse/media-production-20261104` · Base: integration `f0859d0`
Tool: `Tools/MediaProduction/Muse/build_campaign_batch_video.py` (new, generic successor to the per-scene builders of checkpoints 21–24)

## What was delivered

Animated takes for the **remaining 13 campaign scenes** — CIN_003, CIN_007, CIN_008, CIN_010, CIN_011, CIN_012, CIN_013, CIN_014, CIN_015, CIN_016, CIN_017, CIN_018, CIN_019 — produced in **one batch** at the owner's order ("làm hết trong một lượt gói này"). Keyframes were generated in 13 parallel staging runs from the `Cinema_Production_Pack_v1.json` shot prompts **verbatim** (pack SHA `09e8685f…`), 3 per scene, 39/39 succeeded with no HTTP 429 and no content refusal. Each scene now has, in `ClientGodot/assets/cinematics/<SCENE>/`:

- `<SCENE>_640x360_30fps.mp4` (H.264, 540 frames) + `<SCENE>_640x360_30fps.ogv` (Theora) — 18.0 s Ken Burns animated take, **no audio track, no baked subtitles**
- `<SCENE>_poster.png` (byte-identical to the S01 keyframe)
- `<SCENE>_timing_v1.json` + `<SCENE>_vi.srt` (copies SHA-verified against the campaign manifest)
- `scene_export_manifest_v1.json` (`videoStatus: VIDEO_ANIMATED_TAKE_KEN_BURNS`, `reelOffsetSeconds: null`)

Source keyframes + per-scene keyframe manifests live in `Art_Source/Cinematics/Campaign/<SCENE>/keyframes_16x9/` and `<SCENE-numeric>_keyframes_manifest_v1.json`. Staging records (WebP 2048×1152, SHA + snapshot IDs) are in the goal `hidden_files/cin<NNN>_keyframes_staging/` with `cin<NNN>_keyframes_handover_20261106.md` notes.

**All 20 campaign scenes now carry video** (3 P0 panel-hold exports + 17 Ken Burns animated takes). Runtime cinematics manifest: `sceneClips` 7 → **20**; scene-clip files verified 100 (20 × 5). Runtime audio is unchanged: 570 files (22 music/ambience + 519 SFX/UI + 25 VO + 4 mixes).

## Per-scene results (frame checks: mean abs channel diff vs keyframe, 0–255)

| Scene | MP4 SHA (8) | OGV SHA (8) | OGV stored | Identity S01/S02/S03 | Motion S01/S02/S03 |
|---|---|---|---|---|---|
| CIN_003 | 0c4cb618 | a05b370e | 502 | 4.11 / 3.28 / 4.21 | 25.10 / 23.90 / 37.48 |
| CIN_007 | 773aefec | 37cddc83 | 497 | 4.49 / 3.68 / 4.31 | — (see export manifest) |
| CIN_008 | 443b449f | e65ae3c7 | 516 | 3.61 / 3.40 / 2.39 | — |
| CIN_010 | 86d7a349 | 9a78ccf3 | 484 | 6.86 / 2.62 / 2.32 | — |
| CIN_011 | 436fbe13 | 68330a7d | 498 | 5.39 / 6.19 / 5.02 | — |
| CIN_012 | 60356490 | eee8f68f | 497 | 5.59 / 3.21 / 2.61 | — |
| CIN_013 | 1b8729ab | b9952023 | 494 | 2.94 / 3.07 / 3.44 | — |
| CIN_014 | 6576f608 | 9c6fec45 | 496 | 4.70 / 4.33 / 5.59 | — |
| CIN_015 | 1709e996 | 30428e19 | 501 | 3.58 / 5.72 / 8.82 | — |
| CIN_016 | bc50ec67 | 8c358873 | 504 | 3.87 / 4.04 / 5.69 | — |
| CIN_017 | c485b9f4 | 42efd261 | 502 | 2.53 / 5.85 / 4.08 | — |
| CIN_018 | 2a2db26e | e31980bf | 492 | 3.83 / 3.94 / 3.56 | — |
| CIN_019 | d54c8f62 | 937de22e | 501 | 5.35 / 2.66 / 3.27 | — |

All identity diffs < 10 and all motion diffs > 1.5 as required; full per-shot values (incl. continuous-motion diffs) are in each scene's export manifest. CIN_015_S03 (TOPDOWN_MATCH) zooms out 1.08→1.00 with identity taken at exact frame 539 (8.82). Motion model is uniform for the batch: push-in centered 1.00→1.08 / 1.00→1.10 / 1.00→1.08.

## Validation

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** — `MEDIA02_CHECKPOINT_25_SOURCE_REVALIDATION_20261106.json`. Per-scene clips checked 20/20 (20 with video); reel still tiles 0–72 exactly.
- Runtime re-verification (`verify_runtime_delivery.py`): **PASS, 0 mismatches** — `MEDIA02_CHECKPOINT_25_RUNTIME_REVERIFY_20261106.json`; scene-clip files checked: 100.
- New in the validator: `check_campaign_keyframes_batch()` — one generic checker for all 13 batch scenes (files, dims, SHAs, staging SHAs, framing/defect notes, shot-set vs timing) **plus a keyframe-manifest title cross-check against the timing JSON for all 17 campaign keyframe scenes**, closing the validation gap recorded at checkpoint 24 (the CIN_009/CIN_006 title slip).
- Two defects were caught and fixed during integration before delivery: the first builder draft used wrong source paths (timing/SRT live per-scene under `Deliveries/<SCENE>/`, export folders are uppercase scene IDs) — fixed against the checkpoint-21 template before any scene was built; the new validator initially derived staging dir names with underscores (`cin_015_…` vs actual `cin015_…`) — fixed and re-run to PASS.
- Scene-count expectations updated in all three tools (runtime builder `== 20`, runtime verifier `!= 20`, validator `len(runtime_clips) != 20` + scene tuple), per the checkpoint-24 lesson.

## Limits and headline defects (storyboard level — full per-shot records in the keyframe manifests)

Every batch scene has named characters on screen with **no approved cinematic character lock**; all faces/costumes are storyboard placeholders and final picture per shot stays blocked on the lock. Motion is animatic-level Ken Burns, not final pose animation. Headline defects for the final-picture revision pass:

- **CIN_012_S03** — baked-in game choice UI bar with two legible English buttons ("WAIT IN SILENCE" / "OFFER THE PAPERS"); hard violation of the prompt's clean-frame rule. First revision item.
- **CIN_017_S02** — major subject miss: neither the crystal core nor the serpent appears; the core reads as a bamboo pipe machine with glowing orbs; an invented robed man stands at frame left.
- **CIN_015_S02** — setting failure: dry above-water courtyard instead of the drowned ruin; invented pale mascot figure; modern buckled wrist strap. The same white hooded mascot-like intrusion also appears in **CIN_012_S01**.
- **CIN_011** — an unnamed teal-robed woman, in no prompt, appears design-consistently in S01 and S03.
- **CIN_010** — environment continuity collapses after S01 (desert → bamboo grove → rocky scrub); Sầm renders as a slim young man, not the stocky middle-aged merchant of the brief.
- **CIN_008_S03** — the bandage reads on the character's right forearm; canon places it on the character's LEFT forearm — check against the lock at final picture.
- Cross-shot drift is widespread (lighting, costume, gate design in CIN_013, Tống Bành's identity in CIN_014_S03, relief material in CIN_011). CIN_018 remains the only two-cue scene; its S03 VO overrun (+0.280 s) stands per the owner's 2026-11-06 decision (window kept, Codex decides at PR review). CIN_011's VO fits its wide window with only 0.008 s margin.

## Still open after this checkpoint

- Actually composed/remixed music/SFX (rest of Gói 30 item 7) — the CP07/CP08 packs remain measured Codex PackV1 ports with provenance, not new audio. This is the next block.
- PR #119 description rewrite (Gói 30 item 8) and ACKs for checkpoints 08–25 on issue #116 — both need the owner's approval card (GitHub connector write).
- Ear audition / pronunciation / native playback reporting for VO and mixes.
- Final-picture revision pass for all recorded keyframe defects (blocked on character locks / art-direction decisions).
