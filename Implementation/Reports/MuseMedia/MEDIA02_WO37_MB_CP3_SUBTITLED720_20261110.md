# MEDIA-02 Checkpoint — WO37 M-B CP3: standard 720p version of the CIN_000 subtitled viewing variant

Date: 2026-11-10 (JST). Branch: `muse/media-production-20261104`.
Baseline: `c0caf22` (M-B CP2 head). PR #119 stays HOLD; Muse does not self-merge.
Production OFF.

## What was delivered

Closes the gap named in the M-B CP2 report ("CIN_000's subtitled variant
is not part of the playback set and has no standard version here"): the
prologue's subtitled viewing variant now has a standard 720p version,
built with the same measured CP2 recipe.

**Source (verified real bytes):**
`ClientGodot/assets/cinematics/CIN_000/CIN_000_640x360_30fps_sub_vi.mp4`
— sha256 `2aae25e418c5c264efc494ac117a1416c555e8bb09efe0f55a4fb63f9d0ba25b`
(matches the CP28 record `2aae25e4…` and the git LFS oid), 11,918,592 B,
87.381 s, 640×360 @30fps, H.264 + AAC + mov_text subtitle track (vie).
CP28 content: burned-in Vietnamese subtitles (26 readable chunks) +
embedded mov_text track + narration +5.0 dB (−15.83 LUFS).

**Output:**
`Art_Source/Cinematics/Standard720/CIN_000_subtitled/CIN_000_1280x720_30fps_sub_vi.mp4`
— sha256 `a3c1f16d3cbb50b01c44bbc1ef082999457dcb70c229d3b257c24e3d78b8348b`,
32,072,843 B (**2.69×** the 640 source — in line with the CP2 set's
2.77× for CIN_000), 87.381 s, 1280×720 @30fps, H.264 crf26.

**Method — disclosed, not hidden:** integer 2× nearest-neighbour upscale
(`scale=1280:720:flags=neighbor`, H.264 crf26 preset medium, the CP2
measured choice). It is **not** a native 720p capture and is labelled as
such in the manifest. Audio stream-copied bit-exact (checker proves the
AAC elementary stream identical, so the −15.83 LUFS narration mix carries
over unchanged); the embedded mov_text subtitle track is also
stream-copied (`-map 0 -c:s copy`), so the review variant keeps its
soft-subtitle companion. No OGV sample: CP28 records "no OGV subtitled
variant" (in-engine subtitle display belongs to the film files), so
there is no 640 OGV subtitled source to upscale.

The file lives in its own `CIN_000_subtitled/` folder so the CP2 playback
set stays exactly 21 entries. The ClientGodot runtime tree is **not
modified**; adoption stays Codex's decision (same pattern as M38-B / CP2).

## Validation

Checker `check_standard720_subtitled_mb_cp3_v1.py`: **PASS 18/18, 0 failures**
(`MEDIA02_WO37_MB_CP3_VALIDATION_20261110.json`). Per check: manifest
sha/bytes match disk; source sha equals manifest, the CP28 record and the
git LFS oid; output probes 1280×720 @30fps with audio + mov_text (vie);
duration delta 0.000 s; audio bit-identical (stream copy); frames at
1.0 / 43.7 / 86.4 s downscale back to 640×360 with worst mean|diff|
**3.538** and worst 2×2 intra-block range **5.67** (both inside the CP2
checker thresholds 6.0 / 24, and better than CP2's worst 4.215 / 6.08);
budget re-derived; git status clean under `ClientGodot/`.

## Limits / notes

- DRAFT standard version of a DRAFT viewing variant; final picture remains
  character-lock-blocked for the locked shots — this file will be
  re-rendered from the final master if the prologue picture changes.
- The subtitled variant is a review variant, not a playback entry; this
  720p file is likewise review/standard, not runtime.
- Nothing was listened to or watched by ear/eye beyond the numeric frame
  checks; audio is a bit-exact copy, so no new audition state.

## Scope audit

- Content commit `d2bff1253684261cea8202603d944c8269c753af`:
  **4 paths / 0 violations** (base `9ac73dc`).
- Cumulative from merge-base `cf17178` at the content commit:
  2195 paths / 1 known `.gitattributes` merge-base artifact
  (byte-identical with integration `9ac73dc`, not a real divergence).
  The report commit adds exactly 2 files (this report + validation
  JSON), so the head count is 2197 paths.

## Files

- Tools: `Tools/MediaProduction/Muse/build_standard720_subtitled_mb_cp3.py`,
  `Tools/MediaProduction/Muse/check_standard720_subtitled_mb_cp3_v1.py`.
- Media: `Art_Source/Cinematics/Standard720/CIN_000_subtitled/` — 1 MP4
  (32,072,843 B).
- Manifest + this report + validation JSON.

## Next block (per Gói 38 + issue #116)

M-F CP2 (palette-adoption re-mix) and M-E CP2 (composed SFX) still await a
director/Codex decision — not started. 32 motion shots still wait for
character lock. Full 720p OGV set still waits for the Codex budget
decision. No fresh-clone/hash checkpoint on unchanged bytes.
