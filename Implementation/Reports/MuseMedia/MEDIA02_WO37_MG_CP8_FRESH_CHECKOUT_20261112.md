# MEDIA-02 WO37 M-G CP8 — Fresh-checkout verification of the M-F CP2 binary delta (scoped)

Date: 2026-11-12 · Branch: `muse/media-production-20261104` ·
Baseline: `81f33e6` (M-F CP2 report) · Content commit:
`5550d61c94b14ae2fd87076b990355d25a26af7f`
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — QA evidence for Codex
review; no mix, runtime file, or casting decision is changed here.

## 1. Why this checkpoint exists (and why it is scoped)

Gói 38 rule 1 stops repeat fresh-clone/hash checkpoints over the
same 783 runtime bytes without a binary, policy, or tool delta.
M-F CP2 (content `2d7f02a`) IS a real binary delta: 14 new draft v2
mix WAVs in `Art_Source/Audio/Muse/MIX/`. Its own checker
(369/369 PASS) ran in the working clone — the same place where
M-G CP7 found defect D1 (4 files that were LFS pointers, not real
bytes, in the working clone). A working-clone check cannot catch
that defect class for new files; only a fresh checkout with a
pure-network LFS pull can. This checkpoint verifies exactly that
delta and nothing else: it does NOT re-run the full CP7
fresh-checkout suite (runtime re-verify, item-5 policy, OGV census)
over unchanged bytes.

## 2. Method

- Fresh clone of `muse/media-production-20261104` into scratch
  (`~/workspace/projects/media02-scratch/mg_cp8_fresh`, kept for
  re-checks, not part of the repo) with `GIT_LFS_SKIP_SMUDGE=1`.
  Fresh HEAD = `81f33e6e061e79ca10778b8961680e7c4b043245`, clean.
- Pre-pull state: all 14 mix WAVs were 132/133 B LFS pointers, as
  expected under skip-smudge.
- `git lfs install --local`, then a pure-network
  `git lfs pull -I 'Art_Source/Audio/Muse/MIX/*_DRAFT_V2/*,Art_Source/Audio/Muse/MIX/P0_DRAFT_V4/*'`
  — exit 0, no local seeding, no re-pull, no repair. (First
  attempt was skipped with "Git LFS is not installed for this
  repository" until `install --local` — same step M-G CP7 took;
  the pull itself then fetched all 14 objects.)
- Validator `Tools/MediaProduction/Muse/check_fresh_delta_mg_cp8_v1.py`
  (measurement conventions copied from the M-F CP2 checker:
  ffprobe + single-pass `loudnorm=print_format=json`, ±0.2
  tolerance; duration tol 0.01 s scenes / 0.05 s prologue):
  **PASS 117/117, 0 failures** (verdict JSON:
  `MEDIA02_WO37_MG_CP8_VALIDATION_20261112.json`).
  One in-build fix, recorded per standing rule: the validator's
  first run crashed parsing loudnorm output because it passed
  `-v error` to ffmpeg, which suppresses the JSON summary; the
  extraction now matches the CP2 checker (default verbosity,
  parse from the last `{`). No repo bytes were affected.

## 3. The 14 mixes — verified from the fresh clone's real bytes

All 14 are RIFF WAVs (not pointers) after the network pull, with
sha256 byte-identical to the M-F CP2 validation JSON, sizes
identical, and LUFS / true peak re-measured identical to the CP2
values at 2-decimal precision:

| Scene | File | Dur (s) | LUFS | dBTP | Bytes |
|---|---|---|---|---|---|
| CIN_006 | `CIN006_DRAFT_V2/CIN_006_mix_draft_v2.wav` | 18.000 | -23.69 | -6.71 | 3,456,100 |
| CIN_008 | `CIN008_DRAFT_V2/CIN_008_mix_draft_v2.wav` | 18.000 | -26.07 | -4.88 | 3,456,100 |
| CIN_010 | `CIN010_DRAFT_V2/CIN_010_mix_draft_v2.wav` | 18.000 | -26.20 | -8.70 | 3,456,100 |
| CIN_011 | `CIN011_DRAFT_V2/CIN_011_mix_draft_v2.wav` | 18.000 | -24.32 | -6.54 | 3,456,100 |
| CIN_012 | `CIN012_DRAFT_V2/CIN_012_mix_draft_v2.wav` | 18.000 | -26.00 | -5.83 | 3,456,100 |
| CIN_013 | `CIN013_DRAFT_V2/CIN_013_mix_draft_v2.wav` | 18.000 | -24.51 | -3.68 | 3,456,100 |
| CIN_014 | `CIN014_DRAFT_V2/CIN_014_mix_draft_v2.wav` | 18.000 | -26.16 | -5.65 | 3,456,100 |
| CIN_015 | `CIN015_DRAFT_V2/CIN_015_mix_draft_v2.wav` | 18.000 | -25.33 | -5.81 | 3,456,100 |
| CIN_016 | `CIN016_DRAFT_V2/CIN_016_mix_draft_v2.wav` | 18.000 | -25.40 | -6.54 | 3,456,100 |
| CIN_017 | `CIN017_DRAFT_V2/CIN_017_mix_draft_v2.wav` | 18.000 | -25.95 | -5.92 | 3,456,100 |
| CIN_018 | `CIN018_DRAFT_V2/CIN_018_mix_draft_v2.wav` | 18.000 | -22.97 | -4.71 | 3,456,100 |
| CIN_020 | `CIN020_DRAFT_V2/CIN_020_mix_draft_v2.wav` | 18.000 | -25.97 | -9.61 | 3,456,100 |
| CIN_002 | `P0_DRAFT_V4/CIN_002_mix_draft_v4.wav` | 18.000 | -26.28 | -2.93 | 3,456,100 |
| CIN_000 | `CIN000_DRAFT_V2/CIN_000_mix_draft_v2.wav` | 87.367 | -21.75 | -1.98 | 16,774,542 |

Per-mix ffprobe: pcm_s16le / 48 kHz / stereo on all 14.

## 4. Global checks (fresh vs working clone)

- Fresh HEAD == `81f33e6e061e79ca10778b8961680e7c4b043245`.
- Runtime audio file count: **784 in both clones**
  (599 WAV + 184 OGG + 1 JSON = 783 audio files + manifest JSON)
  — runtime untouched by the M-F CP2 delta.
- Delta `129b363..81f33e6`: **45 files, 0 under `ClientGodot/`**.
- `git lfs ls-files`: **2831 tracked files / 2135 distinct OIDs,
  identical on both sides** (was 2717 / 2021 at CP7 — the +114 /
  +114 is the M39-A/B, M-C CP3c and M-F CP2 binary deltas since;
  recorded as data, not a pass/fail against CP7).

## 5. Defects: none found

The D1 defect class (LFS pointer masquerading as a real file) is
**absent** from the M-F CP2 delta: all 14 objects exist on the
remote, pull cleanly over the network, and hash identically to the
build-time measurements. No repair was needed and no file was
modified by this checkpoint. The working clone needed no restore
(`git status` clean before and after).

## 6. Scope audit

- Block (81f33e6 → content 5550d61): **2 paths, 0 violations**.
- Cumulative vs merge-base `cf17178` at the content commit:
  **2354 paths, 1 violation** — the single `.gitattributes`
  violation is the known merge-base artifact (byte-identical with
  integration), not a new breach. Per the count lesson, this
  report commit adds exactly 1 file, so the head count after the
  report commit is 2355 paths.

## 7. Limits and honest notes

- Scoped delta QA only: the full CP7 fresh-checkout suite (runtime
  re-verify, item-5 policy, OGV census) was NOT re-run — no
  runtime, policy, or tool delta justifies it under Gói 38 rule 1.
  The CP7 baseline (fresh-checkout QA at 9cd5808) still stands.
- All 14 mixes remain DRAFT_NOT_FINAL and NOT_AUDITIONED. This
  checkpoint verifies bytes and measurements, not sound; the ear
  verdict belongs to the listener, runtime adoption to Codex.
- Issue #116 re-checked this run (public API): still 30 comments,
  latest Muse ACK 6819808977 (M39-C handoff, 2026-11-12 09:25
  UTC). No new Codex/owner direction since Gói 39 (6815238814).
  The M-F CP2 PR/ACK payload (PR 108,360 chars / ACK 3,318 chars)
  remains built but NOT posted — posting needs the owner's
  approval card and is the main thread's job, not this run's.

## Files

- Tool: `Tools/MediaProduction/Muse/check_fresh_delta_mg_cp8_v1.py`
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP8_VALIDATION_20261112.json`
  (validator PASS 117/117 at head 81f33e6, fresh clone).
- This report.

## Next

M-F CP2 payload posting (owner tap) and any Codex direction that
follows it; otherwise the next media block per WO37/Gói 39
(M-F CP3 pronunciation follow-up, M-B 720p v2 re-render, or the
next M-G delta QA when a new binary delta lands). PR #119 stays
HOLD; Muse does not self-merge.
