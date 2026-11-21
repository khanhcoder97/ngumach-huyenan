# MEDIA-02 WO37 M-G CP10 — Fresh-checkout verification of the M-B CP5 binary delta

Date: 2026-11-13 (JST) · Branch: `muse/media-production-20261104` ·
Baseline: `443d3e4` (M-G CP9 verified head) · Verified head: `8f7120a` ·
Content commit under test: `257c985` (M-B CP5, 7 files)
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — QA evidence for Codex
review; no mix, runtime file, or casting decision is changed here.
PR #119 stays HOLD; Muse does not self-merge.

> SEQUENCE NOTE — this verification was prepared as a draft in the
> goal hidden-files (evidence complete at head `8f7120a`) and held
> uncommitted so the pending CP5-only ACK payload (head `8f7120a`,
> 191 commits / 2394 files) would not go stale. On 2026-11-13
> ~15:00 JST the owner ordered the blocks to continue ("tiếp tục các
> khối mới"), so the main thread committed this checkpoint directly;
> the pending CP5-only ACK is superseded by a folded CP5 + M-G CP10
> ACK at the new head. Evidence below is unchanged from the draft.

## 1. Why this checkpoint exists

Gói 38 rule 1 stops repeat fresh-clone/hash checkpoints over the same
bytes without a binary, policy, or tool delta. The delta `443d3e4..8f7120a`
contains a real binary delta that has never had a fresh-checkout
verification: M-B CP5 content `257c985` adds two new subtitled prologue
films (640 + 720p MP4, 11.9 MB + 32.3 MB) plus a re-timed readable SRT
and manifest entries. The CP5 checker (55/55) and the full validator ran
in the working clone — the same place where M-G CP7 found defect D1
(LFS pointers masquerading as real files). A working-clone check cannot
catch that defect class for new files; only a fresh checkout with a
pure-network LFS pull can. This checkpoint verifies exactly the 7-file
CP5 content delta and nothing else: it does NOT re-verify the PR119
body-restructure R1 files in the same range (already validated 9/9 and
read back byte-exact after posting), and it does NOT re-run the full
CP7 fresh-checkout suite over unchanged bytes.

## 2. Method

- Fresh clone of `muse/media-production-20261104` into scratch
  (`~/workspace/projects/media02-scratch/mg_cp10_fresh`, kept for
  re-checks, not part of the repo) with `GIT_LFS_SKIP_SMUDGE=1`.
  Fresh HEAD = `8f7120a34d92bee816ce163e6ea6213a1a916e24`, clean tree.
- Pre-pull state: both CP5 MP4s were 133 B LFS pointers, as expected
  under skip-smudge (640 OID `f8d6ac32…`, 720p OID `472c1167…`).
- `git lfs install --local`, then a pure-network `git lfs pull -I`
  for the 2 delta MP4s — exit 0, no local seeding — followed by the
  8 reference paths the CP5 checker needs to run verbatim: canonical
  MP4 `ClientGodot/assets/cinematics/CIN_000/CIN_000_640x360_30fps.mp4`,
  v2 mix WAV `Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2/CIN_000_mix_draft_v2.wav`,
  the 5 History take WAVs `Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1/VO_CIN000_SEG0{1..5}_NARRATOR_palette_v1.wav`,
  Ly An take `Art_Source/Audio/Muse/VO/P0_DRAFT/VO_CIN001_S05_LYAN_draft_v1.wav`.
  All 5 History takes sha-verified against the v2 manifest before use.
- The CP5 checker `check_prologue_subtitled_v2_v1.py` re-run verbatim
  in the fresh clone, plus a new independent validator
  `check_fresh_delta_mg_cp10_v1.py` (own SRT parser, own ffprobe
  reads, own manifest arithmetic, own git-scope reads).

Two in-run fixes, recorded per standing rule (both in this
checkpoint's own validator, no repo bytes affected):
- First checker run crashed: I had pulled the `_palette_tts_raw.mp3`
  sources instead of the `VO_CIN000_SEG0{1..5}_NARRATOR_palette_v1.wav`
  takes the v2 manifest actually references — ffmpeg exit 183 on a
  132 B pointer. Pulled the 5 WAV takes; the 5 MP3s remain an
  unnecessary scratch-only pull (recorded here, no repo impact).
  The first, vacuous "55/55 identical" comparison (the checker had
  crashed before writing, so the file compared was the committed
  original) is discarded; the real re-run below is the evidence.
- The validator's first run failed on `git` commands (`git-lfs:
  not found`) because the exec PATH lacked `~/workspace/tools-bin`;
  the validator now prepends it itself. Its SRT expectation was also
  corrected: the last chunk is the Ly An final line (ends 83.475 s),
  not the SEG05 narration end — chunk 24 ends 77.839 s.

## 3. Results

### 3a. Delta files: real bytes from the network, hashes exact

| File | sha256 (fresh pull) | size | expected |
|---|---|---|---|
| 640 subtitled v2 MP4 | `f8d6ac32…ca0be` (full match) | 11,927,191 B | CP5 record |
| 720p subtitled v2 MP4 | `472c1167…e760` (full match) | 32,342,539 B | CP5 record |
| readable v2 SRT | `b4495c25…b0d0` (full match) | 2,526 B | CP5 record |

### 3b. CP5 checker, re-run verbatim in the fresh clone: 55/55 PASS

Exit 0. The re-run validation JSON is identical to the committed one
in every detail (0 detail diffs, files block equal, presentation gain
0.9 dB == 0.9 dB) — the CP5 checker is fully reproducible from a fresh
checkout. Saved as `MEDIA02_WO37_MG_CP10_CP5_RERUN_20261113.json`.

### 3c. Independent validator: 40/40 PASS

`check_fresh_delta_mg_cp10_v1.py` — `MEDIA02_WO37_MG_CP10_VALIDATION_20261113.json`.
Covers: fresh HEAD == `8f7120a`, clean tree, content delta == exactly
the 7 expected paths, all 7 under policy roots, 0 `ClientGodot/`
paths in the delta and in range `443d3e4..8f7120a` (14 files), the
sha/size table above, both MP4s > 1 MB (not pointers), film-manifest
`subtitledVariantV2` sha + readable-SRT sha == disk, CP5 manifest
entries sha/size == disk, budget arithmetic, `runtimeTreeModified ==
false`, ffprobe both films ([video, audio, subtitle], h264
640×360 / 1280×720 @30, AAC stereo 48 kHz, duration 87.2667 s both,
equal within 0.01 s), SRT 26 chunks / no CR / monotonic /
min duration ≥ 1.0 s / text == canonical text (normalized) /
chunk 24 ends 77.839 s / chunk 25 starts 80.907 s (Ly An final line) /
last chunk ends 83.475 s, checker re-run reproducibility (3 checks),
runtime tree untouched (`git status ClientGodot/` clean, v1 export
manifest `mp4SubVi` sha still `50ec6a98…`).

### 3d. No defects found

Zero failures across the checker re-run (55/55) and the independent
validator (40/40). The CP5 delta is confirmed from a fresh checkout
with pure-network LFS: real bytes, correct hashes, correct streams,
correct subtitles, runtime untouched.

## 4. Limits

- DRAFT_NOT_FINAL / NOT_AUDITIONED: this verifies bytes, hashes,
  streams and subtitle timing only. No ear audition, no mix PASS.
- Does not re-verify the R1 body/index files or the full CP7 suite
  (out of scope by design, see §1).
- GitHub public API was rate-limited (403) during this run, so PR
  #119 mergeable was NOT re-read here; last verified true/clean at
  13:40 JST, and neither branch has moved since (media head still
  `8f7120a`, integration still `f3db6b3`, verified by fetch).
- Issue #116 re-checked this run (public API, before the rate
  limit): still 33 comments, latest Muse ACK 6833806995
  (SCENE-CLIPS FIX + M-G CP9). No new Codex/owner direction since
  Gói 39 (6815238814). At verification time the CP5 ACK was still
  NOT posted (approval card expired, `permissions.list_pending`
  EMPTY); per the sequence note above it is superseded by a folded
  CP5 + M-G CP10 ACK at the new head.

## 5. Files

- Validator: `Tools/MediaProduction/Muse/check_fresh_delta_mg_cp10_v1.py`
  (content commit).
- This report + `MEDIA02_WO37_MG_CP10_VALIDATION_20261113.json` +
  `MEDIA02_WO37_MG_CP10_CP5_RERUN_20261113.json` in
  `Implementation/Reports/MuseMedia/` (report commit).
- Scratch fresh clone: `~/workspace/projects/media02-scratch/mg_cp10_fresh`
  (HEAD `8f7120a`, kept for re-checks).
- Working clone untouched this run: HEAD `8f7120a`, clean tree,
  no commit, no push.

## 6. Next

1. Folded CP5 + M-G CP10 ACK + PR #119 body refresh at the new
   head (owner tap, main thread).
2. R2: PR #119 body v2 refresh + delivery index rows for R1/CP5/
   M-G CP10.
3. Standing blocks unchanged: 32 shots await character lock; ear
   audition of the fixed prologue + subtitled v2 is the owner's ears;
   SFX has no new composition approval (18/18 drafts done); full
   OGV 720p set deferred per Gói 39. PR #119 stays HOLD.
