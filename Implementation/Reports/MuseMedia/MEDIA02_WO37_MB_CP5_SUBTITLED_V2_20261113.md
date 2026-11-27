# MEDIA-02 Checkpoint — WO37 M-B CP5: subtitled prologue v2 (History narration)

Date: 2026-11-13 (JST). Branch: `muse/media-production-20261104`.
Baseline: `5dece1f` (PR119 body restructure R1). Content commit: `257c98538c91a9d42c208300ab9a8e0e51a5fc90`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — review masters for Codex;
no runtime file, mix, or casting decision is changed here.

## What was delivered

Closes the follow-up named in the M-B CP4 report: the CP28 / M-B CP3
subtitled variant is timed to the v1 (Helio) narration, so re-muxing
the v2 audio under it would misalign subtitles vs narration. This
checkpoint re-times the subtitles to the M-F CP2 draft v2 narration
(History) and renders a parallel viewing variant. **The canonical v1
files are unchanged and the ClientGodot runtime tree is untouched**
(v2 is an Art_Source-only alternate, same discipline as M-F CP2 /
M-B CP4); the runtime still carries the v1 subtitled variant
(mp4SubVi, fixed mix).

**Method — same rule CP28 used for v1:** each canonical cue window
is the narration take's file span placed at its CP27 slot start.
Verified first that the v1 windows are exactly the Helio take
durations (16.512 / 15.528 / 19.752 / 14.928 / 8.040 s + Ly An
2.568 s, from `PROLOGUE_VO_manifest_v1.json`). The v2 windows are
the History take durations at the same starts; the Ly An line is
unchanged (the same take is reused in v2 at −5 dB):

| Cue | Segment | v1 window | v2 window |
|---|---|---|---|
| 1 | SEG01 | 1.400–17.912 | 1.400–14.408 |
| 2 | SEG02 | 19.033–34.561 | 19.033–35.785 |
| 3 | SEG03 | 35.667–55.419 | 35.667–51.915 |
| 4 | SEG04 | 55.133–70.061 | 55.133–67.901 |
| 5 | SEG05 | 71.167–79.207 | 71.167–77.839 |
| 6 | Ly An | 80.907–83.475 | 80.907–83.475 (unchanged) |

Chunk split + proportional allocation + 1.2 s minimum display are
CP28's exact algorithm, so the **26 chunk texts are identical to
the v1 readable SRT — only timings move** (verified by the checker
from an independent re-implementation). The one window overlap
(SEG02 file end 35.785 s vs SEG03 start 35.667 s; the 0.118 s tail
is silence below −50 dBFS per the v2 manifest) is resolved by
CP28's monotonic rule: SEG03 chunks shift **+0.168 s** (0.118
overlap + 0.05 gap).

**Presentation gain re-measured on the v2 mix:** the v2 mix is
−21.75 LUFS / −1.98 dBTP (fresh measurement matches the manifest
exactly). The gain rule is min(+2.0 dB, headroom to −1.0 dBTP),
rounded down to 0.1 dB → **+0.9 dB** (the v2 mix is hotter than the
fixed v1 mix, so the gain is true-peak-limited, not the +2.0 dB of
the v1 variant). Predicted variant −20.85 LUFS / −1.08 dBTP.

**Files:**

| File | sha256 | Size | Measured |
|---|---|---|---|
| `Art_Source/Cinematics/Prologue/CIN_000_640x360_30fps_sub_vi_v2.mp4` | `f8d6ac32…` | 11,927,191 B | −20.87 LUFS / −1.24 dBTP |
| `Art_Source/Cinematics/Standard720/CIN_000_subtitled_v2/CIN_000_1280x720_30fps_sub_vi_v2.mp4` | `472c1167…` | 32,342,539 B | 1280×720, audio + subtitle stream-copied |
| `Implementation/Content/Narrative/Deliveries/CIN_000/CIN_000_vi_readable_v2.srt` | `b4495c25…` | 2,526 B | 26 chunks |

640 render: CP28 recipe (libx264 medium crf19, burned-in libass
subtitles in CP28 style, AAC 192k, embedded mov_text track),
video from the canonical MP4, audio from the v2 mix WAV, trimmed
to the video duration 87.2667 s. 720p: CP3 recipe — integer 2×
nearest-neighbour upscale of the 640 v2 variant, H.264 crf26,
audio + subtitle tracks stream-copied; NOT a native 720p capture.
Total 44,269,730 B (720/640 ratio 2.712×). Registration: film
manifest `subtitledVariantV2` + new delivery manifest
`STANDARD720_SUBTITLED_V2_MB_CP5_v1.json` (both files).

## Validation

Checker `check_prologue_subtitled_v2_v1.py`: **PASS 55/55, 0 failures**
(`MEDIA02_WO37_MB_CP5_VALIDATION_20261113.json`). Highlights,
all from real bytes:

- Sources: canonical MP4 `86b7cdd9…`, canonical SRT, v2 mix
  `5d405505…`, all 5 History takes and the Ly An take — shas ==
  their manifests. V1 method check (SRT windows == Helio take
  durations) re-derived and passing.
- Subtitle derivation: independent re-implementation of the CP28
  split/allocation reproduces the delivered readable v2 SRT
  cue-by-cue (26 chunks, texts identical to v1, timings ≤0.002 s);
  monotonic, min chunk 1.200 s, SEG03 shift +0.168 s confirmed.
- Narration presence in the v2 mix: History takes correlate
  **0.971–0.989 at lag 0** (best-lag scan 0.990–1.000 at lag
  0.000 s); Ly An line 0.983 at 80.907 s. Audible ends re-measured
  from the takes match the manifest within 0.021 s; every cue's
  last chunk ends ≤0.50 s after its audible end.
- 640 variant: streams [video, audio, subtitle], 87.2667 s,
  loudness −20.87 LUFS (predicted −20.85 ± 0.15), TP −1.24 dBTP
  (predicted −1.08 ± 0.25 — AAC re-encoding shifts intersample
  peaks, same effect as the v1 variant's −1.19 vs −1.11), TP
  under the −1.0 dBTP ceiling; embedded mov_text round-trips
  26/26; audio correlates 0.9998 with the v2 mix WAV at lag 0;
  picture vs the canonical film (subtitle band masked) worst
  mean|diff| 2.178.
- 720p variant: streams [video, audio, subtitle], 1280×720@30,
  audio stream hash identical to the 640 variant (bit-copied),
  embedded mov_text 26/26, downscale mean|diff| 3.543 (CP2
  threshold ≤ 6.0), mean 2×2 intra-block range 5.18 (CP2
  threshold ≤ 24).
- Registration: film manifest + CP5 manifest entries match disk;
  `git status ClientGodot/` clean; v1 export manifest mp4SubVi
  sha unchanged (`50ec6a98…`).
- Frame grabs inspected by eye: 6.0 s (cue 1 chunk 2, two lines,
  correct diacritics), 45.0 s ("Một phần thành phố chìm xuống
  nước —"), 82.2 s ("Giữ giúp tôi đầu kia!" over the arrival
  shot), 85.8 s (title card — correctly no subtitle). The 6.0 s
  and 45.0 s frames show the expected effect of the re-timing:
  the History narration runs faster, so later chunks appear
  earlier than in the v1 variant.

Full `validate_media_deliveries.py` re-run after the build:
**verdict PASS, 0 mismatches** (1411 audio files checked;
prologue section 45 files).

Scope audit: block **7 paths / 0 violations**; cumulative vs
merge-base `cf17178` at the content commit: **2392 paths /
1 violation** — the single `.gitattributes` violation is the
known merge-base artifact (sha `23352e4c…`, byte-identical with
integration `f3db6b3`, verified this run), not a new breach.

## Calibration notes (checker fixes during this run, no repo bytes affected)

- The 640 render's true peak measured −1.24 dBTP vs −1.08
  predicted: AAC re-encoding shifts intersample peaks. The
  builder/checker TP tolerance is ±0.25 dBTP (LUFS stays ±0.15);
  the hard gate remains the −1.0 dBTP ceiling. The first build
  run stopped on the old ±0.15 TP window; after the fix the
  640 re-render was byte-identical (sha `f8d6ac32…` unchanged),
  confirming a deterministic render.
- Correlation lag scans first ran on each take's opening 0.25 s,
  which is lead-in silence for SEG02–05 and returned spurious
  best lags (0.246–0.249 s, low corr). The scan now runs on the
  take's loudest 0.25 s window: best lag 0.000 s on all 6 takes.
- The 720p 2×2 check first used the wrong metric (max range of
  the DIFF image, 35.00) — the CP2/CP4 metric is the MEAN
  intra-block range of the 1280×720 frame itself (5.18 ≤ 24).
- Working-clone LFS state (D1 class, no defect in the delivered
  bytes): the canonical MP4, subtitled v1 MP4, fixed v1 mix WAV
  and OGV were 133-byte LFS pointers in the working clone at run
  start. They were pulled selectively (`git lfs pull --include`)
  before building and verified against their manifests; the
  v2 mix WAV and History takes were already real bytes.

## Limits / notes

- DRAFT_NOT_FINAL / NOT_AUDITIONED: draft v2 mix with draft
  narration; no ear audition, no mix PASS. The v2 subtitled
  variant is a review alternate — adoption into the runtime is
  Codex's decision, same as the v2 mixes.
- Burned-in subtitle font is DejaVu Sans (same placeholder
  status as CP28 / the CP27 title card).
- No OGV subtitled v2 variant: CP28 records "no OGV subtitled
  variant" (in-engine subtitle display belongs to the
  presentation adapter); the readable v2 SRT ships beside the
  film files for that use.
- Issue #116 re-checked this run (connector read): still
  33 comments, latest Muse ACK 6833806995 (SCENE-CLIPS FIX +
  M-G CP9, posted 2026-11-13 ~04:31 JST). No new Codex/owner
  direction since Gói 39 (6815238814). The PR #119 body v2 was
  posted by the main thread ~05:50 JST (read back BYTE-EXACT
  at head `5dece1f`); this checkpoint's payload is NOT posted
  here — the main thread owns posting.

## Files

- Tools: `Tools/MediaProduction/Muse/build_prologue_subtitled_v2.py`,
  `Tools/MediaProduction/Muse/check_prologue_subtitled_v2_v1.py`.
- Media: `Art_Source/Cinematics/Prologue/CIN_000_640x360_30fps_sub_vi_v2.mp4`,
  `Art_Source/Cinematics/Standard720/CIN_000_subtitled_v2/CIN_000_1280x720_30fps_sub_vi_v2.mp4`.
- Deliveries: `Implementation/Content/Narrative/Deliveries/CIN_000/CIN_000_vi_readable_v2.srt`,
  `Implementation/Content/Narrative/Deliveries/STANDARD720_SUBTITLED_V2_MB_CP5_v1.json`.
- Manifest: `Art_Source/Cinematics/Prologue/CIN000_film_manifest_v1.json`
  (`subtitledVariantV2` added, 11 insertions).
- This report + `MEDIA02_WO37_MB_CP5_VALIDATION_20261113.json`.

## Next

Post the CP5 delta with the next PR #119 / issue #116 handoff
(owner tap; the main thread owns posting — this run does not
post; body v2 now has room: refresh the head lines + append a
row to the delivery index per the R1 note). Otherwise the
standing blocks remain: 32 shots motion wait on character lock;
ear-audition of the fixed prologue (owner's ears); SFX has no
new composition approval (18/18 drafts done); full OGV 720p set
deferred per Gói 39. PR #119 stays HOLD; Muse does not self-merge.
