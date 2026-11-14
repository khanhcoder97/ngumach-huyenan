# MEDIA-02 — Prologue v1 plumbing fix (CIN_000)

Date: 2026-11-13 · Branch: `muse/media-production-20261104`
Content commit: `58185dd` (base `7f461da`; rebased onto the
M-B CP4 head before push — final head in the delivery ACK)
Owner approval: main chat 2026-11-13 02:58 JST ("vá luôn đi"),
answering the decision widget left pending on 2026-11-12.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — a defect
correction of the CP27 draft mix, not a final mix. No content,
casting, timeline or level decision is changed.

## 1. The defect (found at WO37 M-F CP2, 2026-11-12)

`build_prologue_film.py` (CP27) fed the single ffmpeg label
`[vo]` to **both** the sidechaincompress key input and the final
amix. ffmpeg steals frames between two consumers of one label,
so the narration in the shipped v1 mix was dropped / shifted and
renders were non-reproducible (−20.30 vs −20.51 LUFS on two
renders of the same graph). Measured on the shipped bytes
(sha256 `f026ed3e…`, Art_Source copy byte-identical to the
runtime copy): SEG01 take vs mix max|corr| **0.020**, SEG03
**0.017**, final Ly An line **−0.063** — the whole VO chain was
effectively absent, while integrated loudness read a healthy
−20.81 LUFS, so loudness QA could not catch it and nobody had
listened (NOT_AUDITIONED). Blast radius: the runtime CIN_000
MP4/OGV, the CP28 subtitled variant and its M-B CP3 720p version
all derived from the broken mix.

## 2. The fix

`build_prologue_mix_v1_fixed.py` re-renders the CP27 mix with
**only the graph plumbing corrected** — the VO bus is `apad`'ed
to the full timeline and `asplit` so each consumer gets its own
copy (the same fix the M-F CP2 prologue v2 render proved).
Everything else is CP27 byte-for-recipe: the same five draft
narration takes (Helio) at unity gain, the same timeline derived
from the CP27 narration manifest, the composed `ben_mua` bed
(−9.07 dB) + ported `rain_light` / `river_shore` ambience
(−8.52 / −8.47 dB), the same sidechain ducking
(0.03 / 4 / 15 ms / 350 ms), Ly An's CP04 final line at −5 dB,
the `resolve` stinger at −2 dB, the same fades and peak guard.
The render was run twice and the two outputs are **byte
identical** (the broken graph was non-reproducible).

Fixed mix: `Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT_V1_FIXED/
PROLOGUE_mix_v1_fixed.wav`, sha256 `4f8224e1…`, 87.367 s,
**−22.37 LUFS / −3.11 dBTP**, peak trim 0.00 dB. (Loudness
differs from the broken file's −20.81 because the ducking key is
now the real VO bus for the full narration span.)

`build_prologue_v1_fix_delivery.py` then, under strict
preconditions (it refuses to run over any bytes other than the
known broken ones):

1. installs the fixed render at the canonical v1 paths
   (Art_Source `PROLOGUE_DRAFT/PROLOGUE_mix_v1.wav` + the
   runtime copy) and updates `PROLOGUE_mix_manifest_v1.json`
   with a `plumbingFix` record naming the superseded sha;
2. re-muxes the runtime film — MP4 video stream **bit-identical**
   to the pre-fix file (stream-hash verified), audio = fixed mix
   AAC 192k (CP27 recipe); OGV re-encoded from the new MP4
   (libtheora q:v 7, libvorbis q:a 5);
3. re-renders the CP28 subtitled variant (burned-in readable
   subtitles + embedded mov_text, subtitle content unchanged)
   and its M-B CP3 720p version (new registration manifest
   `STANDARD720_SUBTITLED_PROLOGUE_FIX_v1.json`; the CP3
   manifest stays as the historical record);
4. updates every registration: film manifest, scene export
   manifest, `RUNTIME_AUDIO_manifest` (mix entry; total stays
   783), `RUNTIME_CINEMATICS_manifest` (prologue entries),
   `PLAYBACK_METADATA` (CIN_000 measured loudness / durations /
   source mix sha — measured fields only; the `mixVersion` ID
   string is shared with the playback pack and the
   pronunciation-table fallback chain and is deliberately left
   as `prologue_mix_v1 (checkpoint 27)`).

### One measured adjustment: subtitled presentation gain +2.0 dB

CP28's +5.0 dB presentation gain was calibrated against the
broken mix (true peak −9.08 dBTP, narration absent). Applied to
the fixed mix (TP −3.11 dBTP) it pushes the variant past full
scale — the first delivery run measured the +5 dB render at
−17.4 LUFS / **−0.42 dBTP** and the delivery tool rejected it.
The gain is therefore **+2.0 dB** (variant measures −20.39 LUFS
/ −1.19 dBTP): still a pure gain with no dynamics change,
exactly CP28's method, with the constant corrected for the
repaired source. That first run was rolled back from backups
and the delivery re-run cleanly; the incident and the rollback
are part of this checkpoint's working record.

## 3. Verification (real bytes only)

`check_prologue_v1_fix_v1.py` — **50/50 PASS**:

| Take | Start | Fixed mix corr | Broken mix corr (control) |
|---|---|---|---|
| SEG01 narration | 1.400 s | **+0.982** @ lag 0.000 | −0.011 |
| SEG02 narration | 19.033 s | **+0.989** @ lag 0.000 | +0.011 |
| SEG03 narration | 35.667 s | **+0.980** @ lag 0.000 | −0.009 |
| SEG04 narration | 55.133 s | **+0.986** @ lag 0.000 | +0.010 |
| SEG05 narration | 71.167 s | **+0.975** @ lag 0.000 | −0.012 |
| Ly An final line | 80.907 s | **+0.986** @ lag 0.000 | −0.020 |

(Controls read the broken bytes back from the git LFS object
store, sha-verified.) Embedded audio: MP4 corr **1.000**
(−22.39 LUFS), OGV corr **0.998** (−22.41), subtitled variant
corr **1.000**. New file hashes: MP4 `86b7cdd9…` (12,248,889 B),
OGV `50e6ca45…` (25,245,216 B), subtitled `50ec6a98…`
(11,917,676 B), 720p subtitled `086d48b5…` (32,071,927 B).
Canonical SRT, readable SRT, timing and poster are untouched
(sha-verified against their manifests).

Repo validators:

- `verify_runtime_delivery.py` — **PASS, 0 mismatches**
  (783 runtime audio files, 7 prologue files).
- `validate_media_deliveries.py` — prologue section clean
  (45 files checked); overall verdict MISMATCHES_FOUND with
  exactly **8 mismatches, all pre-existing and out of this
  checkpoint's scope**: SCENE-CLIPS timing-sha / manifest drift
  for CIN_005, CIN_009, CIN_017, CIN_020, dating from the
  M-C CP5 / M-G CP7 timing syncs (present at base `7f461da` in
  files this checkpoint does not touch). Flagged here for a
  follow-up bookkeeping block; not silently fixed inside the
  prologue fix. Validation JSON:
  `MEDIA02_PROLOGUE_V1_FIX_VALIDATION_20261113.json`.
- One validator correction IS included: `check_prologue()`'s
  hardcoded runtime-audio total (757, written at M-F CP1) was
  stale since M-E CP1 raised the total to 783 and flagged every
  full run since; corrected to 783 with the reason in a comment.
- Scope audit: block 19 paths / **0 violations**; cumulative
  2368 paths / 1 known `.gitattributes` merge-base artifact.

## 4. Limits and follow-ups

- Still **NOT_AUDITIONED**: the fix is proven by correlation
  and loudness, not by ear. The corrected prologue is now the
  reference listen (canonical runtime files or the subtitled
  variant); the ear-audition packs' prologue entries predate
  the fix (CP9 MIX-030 cites the broken sha as a historical
  measurement record — packs are not rewritten).
- Historical records that cite the broken mix sha (M-B CP3
  manifest + its checker, the M-F CP2 manifest's `sourceMixV1`
  record, CP9/CP33 packs) are left as written; they describe
  the bytes as they were when measured. The CP3 checker will
  flag the superseded subtitled source sha by design — the
  successor registration is
  `STANDARD720_SUBTITLED_PROLOGUE_FIX_v1.json`.
- The M-F CP2 palette v2 prologue (History narration) is a
  separate alternate in `CIN000_DRAFT_V2/` and is **not**
  touched; which narration casting is canonical remains a
  Codex / director decision at review. This fix restores the
  v1 (Helio) mix to what CP27 intended.
- Runtime audio total unchanged (783); campaign totals
  unchanged (20 scenes / 63 shots / 378 s / 21 cues).
- PR #119 stays HOLD; Muse does not self-merge.
