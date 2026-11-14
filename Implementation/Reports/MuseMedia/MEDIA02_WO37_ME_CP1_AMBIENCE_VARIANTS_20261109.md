# MEDIA-02 Checkpoint — WO37 M-E CP1: real variants for composed ambience

Date: 2026-11-09 (JST). Branch: `muse/media-production-20261104`.
Integration baseline: `6f79853`. PR #119 stays HOLD; Muse does not
self-merge. Production OFF.

## What was delivered

WO37 M-E checkpoint 1 closes the "one render per cue" gap left by
checkpoint 30: all 13 AMBIENCE/* cues shipped exactly one 16.0 s
master (v01), so a looping bed would repeat identically forever in
game. This checkpoint renders **two REAL variants per cue (v02, v03)
— 26 new renders**, same recipe as v01 with new deterministic seeds,
not copies and not gain/pitch re-prints of v01:

- Same `piece_*` builder and structure as checkpoint 30 (imported
  from `build_composed_ambience.py`, untouched), new seeds
  `32000 + idx*100 + variant` (v01 used `3000 + idx`).
- Same duration 16.0 s, same loudness target (the ported cue's
  checkpoint-07 measured LUFS), same loop construction (1.5 s tail
  wrap + 0.25 s end landing), same TP ceiling −7 dB.
- `rift` only: the CP30 recipe is almost fully deterministic (fixed
  D drone + fixed shimmer partials), so a new seed alone would change
  only the low bed. The variant recipe detunes the drone/shimmer
  partials by +0.4 Hz (v02) / −0.4 Hz (v03) — same character,
  genuinely different beating. All other cues carry enough stochastic
  content (noise beds, random event times/pitches) that a new seed is
  a real variant.

New tools: `Tools/MediaProduction/Muse/build_composed_ambience_variants_me_cp1.py`
(builder; v01 entries are cross-referenced from the checkpoint-30 pack
and re-hashed from the real bytes on disk, never re-rendered) and
`Tools/MediaProduction/Muse/check_composed_ambience_variants_me_cp1_v1.py`
(independent re-verification: re-hash + re-measure + v01 cross-ref +
distinctness + seam + runtime-manifest check).

## Variant measurements (from the real rendered bytes)

All 26 masters measure within **0.01 LUFS** of their cue target
(max deviation: forge v02 −29.51 vs −29.50; thang_long_crowd v02
−30.33 vs −30.34). Master true peak range −11.28…−20.04 dBTP (all
≤ −6 dBTP). Waveform difference vs v01 (decoded from real bytes):
**1.2658–1.4264** — fully different renders (1.0 ≈ uncorrelated).
Seam wrap jump ≤ 6e-06 (loop construction, indicator only).

| Cue | Var | Master LUFS / dBTP | Runtime LUFS / dBTP | Diff vs v01 | Wrap |
|---|---|---|---|---|---|
| rain_light | v02 | −27.48 / −15.46 | −27.79 / −15.73 | 1.4142 | 0.0 |
| rain_light | v03 | −27.48 / −16.41 | −27.80 / −16.82 | 1.4103 | 0.0 |
| rain_heavy | v02 | −27.47 / −16.54 | −27.85 / −17.22 | 1.4112 | 3e-06 |
| rain_heavy | v03 | −27.47 / −15.13 | −27.85 / −15.43 | 1.4081 | 3e-06 |
| river_shore | v02 | −29.53 / −17.13 | −29.68 / −17.41 | 1.4099 | 6e-06 |
| river_shore | v03 | −29.53 / −15.96 | −29.69 / −16.28 | 1.4132 | 3e-06 |
| underwater | v02 | −33.02 / −19.89 | −33.10 / −19.91 | 1.3830 | 2e-06 |
| underwater | v03 | −33.02 / −20.04 | −33.10 / −20.31 | 1.3957 | 0.0 |
| waterfall | v02 | −29.31 / −17.07 | −29.51 / −17.29 | 1.4193 | 6e-06 |
| waterfall | v03 | −29.31 / −16.83 | −29.52 / −17.10 | 1.4175 | 4e-06 |
| wind_canopy | v02 | −29.55 / −16.87 | −29.70 / −17.19 | 1.4109 | 0.0 |
| wind_canopy | v03 | −29.55 / −16.69 | −29.69 / −16.86 | 1.4077 | 0.0 |
| desert_wind | v02 | −29.57 / −18.32 | −29.94 / −18.64 | 1.4122 | 3e-06 |
| desert_wind | v03 | −29.57 / −18.03 | −29.94 / −18.28 | 1.4101 | 1e-06 |
| mountain_wind | v02 | −29.56 / −18.00 | −29.55 / −17.94 | 1.3412 | 1e-06 |
| mountain_wind | v03 | −29.56 / −17.63 | −29.54 / −17.52 | 1.3449 | 0.0 |
| cave_drips | v02 | −29.54 / −11.28 | −29.55 / −11.19 | 1.3893 | 1e-06 |
| cave_drips | v03 | −29.54 / −12.75 | −29.56 / −12.84 | 1.3741 | 3e-06 |
| forge | v02 | −29.51 / −15.40 | −29.50 / −15.34 | 1.4100 | 5e-06 |
| forge | v03 | −29.50 / −15.85 | −29.49 / −15.64 | 1.4230 | 4e-06 |
| thang_long_crowd | v02 | −30.33 / −18.43 | −30.57 / −18.54 | 1.4232 | 0.0 |
| thang_long_crowd | v03 | −30.34 / −18.50 | −30.54 / −18.27 | 1.4095 | 1e-06 |
| city_night | v02 | −30.34 / −17.86 | −30.39 / −17.82 | 1.2840 | 1e-06 |
| city_night | v03 | −30.34 / −17.78 | −30.40 / −17.71 | 1.2658 | 4e-06 |
| rift | v02 | −30.48 / −20.03 | −30.45 / −19.95 | 1.4185 | 2e-06 |
| rift | v03 | −30.48 / −19.77 | −30.47 / −19.69 | 1.4264 | 0.0 |

## Tables and runtime state

- `AMBIENCE_COMPOSED_VARIANTS_pack_v1.json`: 13 cues × 3 variants
  (v01 cross-referenced + v02/v03 new), 39 total variants; all 39
  master SHAs distinct, all 39 runtime SHAs distinct.
- Runtime delivery (§3i in `build_runtime_delivery.py`): 26 variant
  OGGs verified in place and registered as
  `composed_ambience_variant` entries (cueKey + variantId, so an
  adapter can pick v01/v02/v03 per cue). Runtime audio **757 → 783**
  (composed 136 → 162; music/ambience 22, SFX/UI 519, VO 50, mix 30
  unchanged). Campaign totals unchanged: 20 scenes / 63 shots / 378 s
  / 21 cues. Playback metadata unchanged (21 embedded / 0 silent);
  pronunciation table unchanged. Prologue unchanged.
- Validators: ME CP1 validator **PASS, 0 mismatches**
  (`MEDIA02_WO37_ME_CP1_VALIDATION_20261109.json` — 52 variant
  files re-hashed + re-measured, 13 v01 cross-refs re-hashed against
  the checkpoint-30 pack, 39/39 distinct SHAs both sides, seam
  indicators recomputed from decoded masters) + source re-validation
  **PASS, 0 mismatches** + runtime re-verify **PASS, 0 mismatches**
  (26/26 variant entries found in the manifest with matching
  sha/size/duration).
- Scope audit: content-only **57 paths / 0 violations** (base
  f2cff6e → head 48474c3); cumulative **2091 paths / 1 known
  `.gitattributes` merge-base artifact** (base integration 6f79853 →
  head 48474c3; the 1 violation is the checker diffing from cf17178,
  NOT a real divergence — same artifact as all prior checkpoints).

## SFX side of M-E (no new SFX in this checkpoint)

The 173 ported SFX/UI cues already carry 3 measured variants each
(checkpoint 08, `SFX_UI_pack_v1.json`: 519 files, distinct SHAs), so
no new SFX variants were composed here. Composed SFX replacements
for the ported set remain a separate Codex decision, not silently
assumed. The remaining M-E work is therefore: M-E CP2 (if Codex
wants composed SFX variants) or M-F CP2 (palette-adoption re-mixes,
blocked on a director/Codex voice choice) or M-G QA.

## Limits

- COMPOSED_CANDIDATE, no ear audition: loudness/true-peak/difference
  are measured from real bytes only; the diff-RMS ratio is a
  waveform-difference measure, not a listening verdict. A variant can
  measure fully different and still sound similar in character — that
  is the point of a variant (same cue, different render), and the
  listening verdict belongs to the ear-audition step (M-D CP9 pack).
- Seam values are indicators, not a seamlessness PASS.
- The variants do NOT replace the v01 masters or the ported PackV1
  files; adoption and any rotation policy (e.g. NO_IMMEDIATE_REPEAT
  across v01/v02/v03) are Codex's presentation-adapter decision.
- PR #119 description + ACK for ME CP1 are prepared for the main
  thread (GitHub writes need the owner's approval card) — NOT posted
  by this run.
