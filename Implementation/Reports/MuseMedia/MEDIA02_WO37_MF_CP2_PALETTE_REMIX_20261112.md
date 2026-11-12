# MEDIA-02 WO37 M-F CP2 — Palette re-mix (draft v2 mixes, Art_Source only)

Date: 2026-11-12 · Branch: `muse/media-production-20261104` ·
Baseline: `129b363` · Content commit: `2d7f02a387faf50b4ffd7e293c60a4f0e9c0466e`
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — review material for
Codex; adoption (runtime re-embed) is Codex's adapter decision.

## 1. Decision applied

The project owner delegated the voice choice to Muse (main chat,
2026-11-12 18:30 JST, "bạn tự chọn đi"). **Muse's decision: apply
the M-F CP1 palette (side B of the WO39 M39-B CP1 level-matched
A/B review) to every role that has a distinct pickup take.** This
fixes the draft casting defect: every male speaker shared
`avocado_v2:MAI_03` (Helio) and the letter recipient shared Ly
An's `avocado_v2:MAI_01`. Ly An keeps Aria (no pickup exists).
The player pickup (miles) and the letter-recipient pickup
(ElvenWizard) are used but **keep their PLACEHOLDER flags** in the
manifests — they are not casting decisions. Final casting remains
Codex's review decision.

## 2. Form — Art_Source only, runtime untouched

14 draft mixes were built as master WAV + manifest pairs under
`Art_Source/Audio/Muse/MIX/`. **No runtime delivery was run, no
file under `ClientGodot/` was written, no video was re-embedded.**
Evidence: `git status --porcelain -- ClientGodot/` is empty at
every step (the checker asserts it), and
`git diff 129b363..2d7f02a -- ClientGodot/` is 0 files. The
runtime still embeds the v1 mixes (P0 scenes: v3), and the
runtime audio count stays **783**.

Method: each v1 builder was cloned to a v2 builder; a strip-diff
(docstrings and appended palette record removed) confirms the
mixing code is byte-for-byte identical — the only changed lines
are the VO source, output paths, checkpoint/status/mixVersion
prose. Same stems, same gain targets, same sidechain ducking
(threshold 0.03 / ratio 4 / attack 15 ms / release 350 ms), same
peak guard (−1.0 dBTP), VO at unity. Each v2 manifest follows the
v1 schema plus `decisionRef`, `auditionStatus: NOT_AUDITIONED`,
`status: DRAFT_NOT_FINAL` and a `paletteRemix` record per take.

## 3. The 14 mixes (measured from the real bytes)

| Scene | File | Dur (s) | LUFS | dBTP | Bytes | sha256 |
|---|---|---|---|---|---|---|
| CIN_002 | `Art_Source/Audio/Muse/MIX/P0_DRAFT_V4/CIN_002_mix_draft_v4.wav` | 18.000 | -26.28 | -2.93 | 3,456,100 | `27d4259f4a458dab…` |
| CIN_006 | `Art_Source/Audio/Muse/MIX/CIN006_DRAFT_V2/CIN_006_mix_draft_v2.wav` | 18.000 | -23.69 | -6.71 | 3,456,100 | `ca35b80711c5145f…` |
| CIN_008 | `Art_Source/Audio/Muse/MIX/CIN008_DRAFT_V2/CIN_008_mix_draft_v2.wav` | 18.000 | -26.07 | -4.88 | 3,456,100 | `f804bde118bd8aa7…` |
| CIN_010 | `Art_Source/Audio/Muse/MIX/CIN010_DRAFT_V2/CIN_010_mix_draft_v2.wav` | 18.000 | -26.20 | -8.70 | 3,456,100 | `5db32b7ca714acf2…` |
| CIN_011 | `Art_Source/Audio/Muse/MIX/CIN011_DRAFT_V2/CIN_011_mix_draft_v2.wav` | 18.000 | -24.32 | -6.54 | 3,456,100 | `2ab6719f6b8cf0d4…` |
| CIN_012 | `Art_Source/Audio/Muse/MIX/CIN012_DRAFT_V2/CIN_012_mix_draft_v2.wav` | 18.000 | -26.00 | -5.83 | 3,456,100 | `003176859e26f01b…` |
| CIN_013 | `Art_Source/Audio/Muse/MIX/CIN013_DRAFT_V2/CIN_013_mix_draft_v2.wav` | 18.000 | -24.51 | -3.68 | 3,456,100 | `51f4eefba4898a76…` |
| CIN_014 | `Art_Source/Audio/Muse/MIX/CIN014_DRAFT_V2/CIN_014_mix_draft_v2.wav` | 18.000 | -26.16 | -5.65 | 3,456,100 | `ea44770389feb0b5…` |
| CIN_015 | `Art_Source/Audio/Muse/MIX/CIN015_DRAFT_V2/CIN_015_mix_draft_v2.wav` | 18.000 | -25.33 | -5.81 | 3,456,100 | `21ff97589b50a040…` |
| CIN_016 | `Art_Source/Audio/Muse/MIX/CIN016_DRAFT_V2/CIN_016_mix_draft_v2.wav` | 18.000 | -25.40 | -6.54 | 3,456,100 | `63f47babb580105b…` |
| CIN_017 | `Art_Source/Audio/Muse/MIX/CIN017_DRAFT_V2/CIN_017_mix_draft_v2.wav` | 18.000 | -25.95 | -5.92 | 3,456,100 | `a364c9823a95a328…` |
| CIN_018 | `Art_Source/Audio/Muse/MIX/CIN018_DRAFT_V2/CIN_018_mix_draft_v2.wav` | 18.000 | -22.97 | -4.71 | 3,456,100 | `58cead03dc644e1a…` |
| CIN_020 | `Art_Source/Audio/Muse/MIX/CIN020_DRAFT_V2/CIN_020_mix_draft_v2.wav` | 18.000 | -25.97 | -9.61 | 3,456,100 | `e8afd307d20a2d59…` |
| CIN_000 | `Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2/CIN_000_mix_draft_v2.wav` | 87.367 | -21.75 | -1.98 | 16,774,542 | `5d405505ab17a51d…` |

CIN_002 was built with the P0 v3 recipe (fully composed stems)
into `P0_DRAFT_V4/` as mix v4; CIN_001 / CIN_004 were NOT rebuilt
— their lines are Ly An's and v3 stands.

## 4. VO fit — recomputed from the timing files + real pickup bytes

All 14 dialogue takes start exactly at their locked window start
and FITS, 0 overruns:

| Take | Voice change | Window (s) | Take span (s) | Slack (s) | Fit |
|---|---|---|---|---|---|
| CIN002_S02 | avocado_v2:MAI_03 → avocado_v2:conor (Polished Coin (fictional system voice)) | [7.0, 11.0] | 7.0–10.312 | 0.688 | FITS |
| CIN006_S03 | avocado_v2:MAI_03 → avocado_v2:vincent (Gruff Brick (fictional system voice)) | [12.5, 17.5] | 12.5–17.348 | 0.152 | FITS |
| CIN008_S03 | avocado_v2:MAI_03 → avocado_v2:conor (Polished Coin (fictional system voice)) | [12.5, 17.5] | 12.5–15.668 | 1.832 | FITS |
| CIN010_S03 | avocado_v2:MAI_03 → avocado_v2:hubert (Loud Gravel (fictional system voice)) | [12.5, 17.5] | 12.5–15.860 | 1.640 | FITS |
| CIN011_S03 | avocado_v2:MAI_03 → avocado_v2:vincent (Gruff Brick (fictional system voice)) | [12.2, 17.8] | 12.2–16.592 | 1.208 | FITS |
| CIN012_S03 | avocado_v2:MAI_03 → avocado_v2:vincent (Gruff Brick (fictional system voice)) | [12.5, 17.5] | 12.5–16.292 | 1.208 | FITS |
| CIN013_S03 | avocado_v2:MAI_03 → avocado_v2:magnus (Boomy Mountain (fictional system voice)) | [12.5, 17.5] | 12.5–15.092 | 2.408 | FITS |
| CIN014_S03 | avocado_v2:MAI_03 → avocado_v2:ronan (Fluid Hammock (fictional system voice)) | [12.5, 17.5] | 12.5–15.212 | 2.288 | FITS |
| CIN015_S03 | avocado_v2:MAI_03 → avocado_v2:briggs (Husky Campfire (fictional system voice)) | [12.5, 17.5] | 12.5–15.548 | 1.952 | FITS |
| CIN016_S03 | avocado_v2:MAI_03 → avocado_v2:vincent (Gruff Brick (fictional system voice)) | [12.5, 17.5] | 12.5–14.972 | 2.528 | FITS |
| CIN017_S03 | avocado_v2:MAI_03 → avocado_v2:briggs (Husky Campfire (fictional system voice)) | [12.5, 17.5] | 12.5–15.380 | 2.120 | FITS |
| CIN018_S02 | avocado_v2:MAI_03 → avocado_v2:atlas (Burnished Trophy (fictional system voice)) | [6.5, 11.5] | 6.5–9.068 | 2.432 | FITS |
| CIN018_S03 | avocado_v2:MAI_03 → avocado_v2:miles (Satiny Moon (fictional system voice)) | [12.5, 17.5] | 12.5–17.012 | 0.488 | FITS |
| CIN020_S03 | avocado_v2:MAI_01 → avocado_v2:ElvenWizard (Ethereal Star (fictional system voice)) | [12.5, 17.5] | 12.5–15.572 | 1.928 | FITS |

Prologue narration (History pickups at the exact CP27 cue
starts; per-segment gain = CP27 in-mix segment LUFS − pickup
LUFS, both measured fresh — no hard-coded numbers):

| Take | Voice change | Placement | Gain | Slot check |
|---|---|---|---|---|
| CIN000_SEG01 | avocado_v2:MAI_03 → avocado_v2:History | CP27 start 1.400 | gain +10.46 dB | audible end 14.177 ≤ slot 19.033 | file-tail overlap 0.000 s (silence) |
| CIN000_SEG02 | avocado_v2:MAI_03 → avocado_v2:History | CP27 start 19.033 | gain +5.19 dB | audible end 35.475 ≤ slot 35.667 | file-tail overlap 0.118 s (silence) |
| CIN000_SEG03 | avocado_v2:MAI_03 → avocado_v2:History | CP27 start 35.667 | gain +8.02 dB | audible end 51.644 ≤ slot 55.133 | file-tail overlap 0.000 s (silence) |
| CIN000_SEG04 | avocado_v2:MAI_03 → avocado_v2:History | CP27 start 55.133 | gain +7.23 dB | audible end 67.662 ≤ slot 71.167 | file-tail overlap 0.000 s (silence) |
| CIN000_SEG05 | avocado_v2:MAI_03 → avocado_v2:History | CP27 start 71.167 | gain +8.24 dB | audible end 77.576 ≤ slot 80.907 | file-tail overlap 0.000 s (silence) |

SEG02's pickup FILE is 0.118 s longer than its slot; only
trailing padding silence below −50 dBFS crosses into SEG03's
leading silence — the audible narration ends 0.193 s early
(measured from the bytes; recorded per segment in the manifest).

Note on CIN_011: the v1 mix's 8 ms VO margin (WO37 priority-QA
item) belongs to the old take; the palette take leaves 1.208 s of
slack in v2. That is a property of the new voice's timing,
recorded as data — v1 is untouched.

## 5. DEFECT FOUND in the CP27 prologue mix (v1) — fixed in v2 only

While verifying v2, waveform correlation exposed a real defect
in CP27's one-graph render (`build_prologue_film.py`), which v2
was cloned from: the graph feeds the single `[vo]` label to BOTH
`sidechaincompress` (as key) and the final `amix`. ffmpeg steals
frames between the two consumers, so the narration reaching the
final mix is **partially dropped and time-shifted**, and the
render is not even reproducible (two identical renders of the
shared-label graph measured −20.30 and −20.51 LUFS).

Measured on the shipped CP27 mix
(`PROLOGUE_DRAFT/PROLOGUE_mix_v1.wav`), SEG01: the canonical take
correlates **≈ 0.01** with its own mix span at every lag in
±300 ms; the take's −1.12 dBFS peak (expected at 11.603 s) never
reaches the mix (span max −10.93 dBFS); the 0.25 s RMS envelope
tracks the take for ~5 s, then falls to bed level while the take
is still speaking. Span LUFS still measured plausibly (−19.67),
which is why loudness-only QA never caught it; nobody has
listened yet (NOT_AUDITIONED). The scene/P0 builders are NOT
affected: they run separate file-based stages, and this
checkpoint's correlation checks on all 13 other mixes pass at
lag 0 (0.813–0.997).

**v2 fix (plumbing only, recipe unchanged):** the VO bus is
`apad`ed to the full timeline and `asplit` into `[vokey]` /
`[vomix]`, so the sidechain key and the final amix each receive
a complete copy. (Without the `apad`, the sidechain ends the
ducked bed when the key stream EOFs at ~82.8 s and the mix comes
out 0.45 s short — measured.) All gains, ducking parameters,
fades and the peak guard are CP27's. Result: all 5 narration
segments correlate 0.971–0.989 with the gain-scaled pickups at
lag 0 in v2, take energy fraction 0.78–0.81 of each span.

**The v1 mix file was NOT modified** — re-rendering v1 (and the
CIN_000 runtime audio derived from it) is a Codex/owner
follow-up decision, flagged here and in the ACK. The v2 whole-
file loudness (−21.75 LUFS) differs from v1's −20.81 for
traceable reasons: the ducking key is now intact (the bed is
actually ducked under narration) and the narration energy is
confined to its spans instead of being smeared by frame loss;
per-segment narration levels match CP27's in-mix segment levels
by construction of the gain rule.

## 6. Verification

Checker `Tools/MediaProduction/Muse/check_palette_mix_mf_cp2_v1.py`
— **PASS 369/369, 0 failures** (verdict JSON:
`MEDIA02_WO37_MF_CP2_VALIDATION_20261112.json`). Per mix: file
exists, sha256 vs manifest, ffprobe format/duration, loudnorm
LUFS/TP re-measured vs manifest (±0.2), status/decisionRef
fields; per take: pickup sha + duration from bytes, fit
recomputed from the delivery timing windows, waveform integrity
(lag-0 correlation ≥ 0.75, lag-0 peak margin ≥ 0.35 over a
±100 ms scan, take energy fraction ≥ 0.5 — CIN_010's quiet Sầm
take measures corr 0.813 with a ~0 off-lag floor, the sharpest
possible placement proof); placeholder flags present in the
CIN_018 / CIN_020 manifests; `git status --porcelain --
ClientGodot/` empty.

Scope audit: block (129b363 → content) **43 paths, 0
violations**; cumulative vs merge-base `cf17178`: 2350 paths, 1
violation = the known `.gitattributes` merge-base artifact, not
a new breach.

In-build errors fixed and re-run (recorded per standing rule):
(a) first builder run: `augment_manifest()` was appended after
the `__main__` block (NameError) — the call was moved after the
appended definitions; mixes re-rendered cleanly. (b) Prologue
slot assertion used the pickup FILE end; SEG02's file is
0.118 s longer than its slot in trailing silence only — the
assertion now uses the measured audible end (−50 dBFS), with
the file-tail overlap recorded in the manifest. (c) Checker
calibration: CIN_010 corr 0.813 and CIN_002 off-lag corr 0.263
(a periodic voice at a 10 ms shift) — the integrity rule was
re-based on the lag scan + absolute margin above, with the
evidence measured, not assumed. (d) A mid-run `/tmp` exhaustion
(512 MB tmpfs, test renders) was cleaned; no repo bytes lost.

## 7. Limits and honest notes

- Scenes NOT re-mixed (no changed take in scope): CIN_001,
  CIN_004 (Ly An — P0 v3 stands), CIN_003, CIN_005, CIN_007,
  CIN_009, CIN_019 (their dialogue is Ly An's or has no palette
  pickup change).
- CIN_006 and CIN_018 v2 have **no overrun** because the palette
  takes fit their windows (slack 0.152 s / S02 2.432 s + S03
  0.488 s). Data only: the three owner-kept v1 overruns
  (CIN_005_S03 +0.160 s, CIN_018_S03 +0.280 s, CIN_006_S03
  +0.520 s) stay exactly as decided on 2026-11-06; the v1 mixes
  are untouched.
- The narration voice change Helio → History is deliberately
  audible — that difference IS the palette decision; per-segment
  gains (measured, §4) keep the narration at CP27's relative
  level, but timbre and pacing differ.
- All 14 mixes are DRAFT_NOT_FINAL and NOT_AUDITIONED. Nothing
  here is a mix PASS; the ear verdict belongs to the listener,
  and runtime adoption to Codex.
- Follow-up flagged for Codex/owner: the CP27 v1 prologue mix
  defect in §5 (re-render decision), and final casting.

Commits: content `2d7f02a387faf50b4ffd7e293c60a4f0e9c0466e`
(43 files) + this report commit. PR #119 stays HOLD; Muse does
not self-merge.
