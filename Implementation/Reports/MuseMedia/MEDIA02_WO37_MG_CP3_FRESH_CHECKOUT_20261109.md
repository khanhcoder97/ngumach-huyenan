# MEDIA-02 Checkpoint — WO37 M-G CP3: fresh-checkout QA at head 14504fb

Date: 2026-11-09 (JST). Branch: `muse/media-production-20261104`.
Integration baseline: `6f79853`. PR #119 stays HOLD; Muse does not
self-merge. Production OFF.

## What was delivered

WO37 M-G checkpoint 3 is the third full fresh-checkout verification
of the media branch, re-baselined to the current head **14504fb**
(the M-G CP2 report commit — this is the first fresh-checkout
verification of the head that itself contains the M-G CP2 validator
tool and report; M-G CP2 only verified head `c60088c`). A plain
`git clone` of `muse/media-production-20261104` was made into scratch
(`~/workspace/projects/media02-scratch/mg_cp3_fresh`, kept for
re-checks, not part of the repo), then verified byte-for-byte
against the working clone at the same HEAD:

- Fresh HEAD = `14504fb3047a6fca2de322d24242bdb63bcfc067`, branch
  `muse/media-production-20261104` — matches the working clone.
- `git lfs ls-files`: 2709 tracked files / **2013 distinct OIDs**;
  **2013 objects on disk** after pull — complete, no missing object.
- **0 LFS pointer files** under the 7 media roots (2013 files
  header-checked). `git lfs fsck`: OK (run separately after the
  validator; the validator itself does not invoke fsck).
- Per-root file counts + byte totals match the working clone exactly
  (measured before this checkpoint's own report files were written):
  Cinematics 451 files / 219,733,487 B; Audio/Muse 315 /
  1,626,163,856 B; cinematics runtime 174 / 107,755,934 B; audio
  runtime 784 / 304,098,533 B; Narrative Deliveries 50 / 343,200 B;
  Audio Deliveries 18 / 1,450,104 B; Reports/MuseMedia 229 /
  2,678,646 B.
- OGV: 22/22 real Theora bytes (`OggS` magic), 0 pointers.
- Runtime manifest: 783 entries, sha256 identical on both sides
  (`f0e3a015…9806c`).
- Text endings: 373 JSON/SRT files checked, 0 CR bytes.
- Gói 31 item-5 verifier re-run on the fresh checkout with the
  reference policy extracted from integration `6f79853`: **PASS** —
  OGV LFS rule present, all 7 LF rules present, all 29 reference
  rules present, 0 missing. The item-5 policy gap stays closed at
  this head (it was closed by the owner's PR #127 merge on
  2026-11-08; this run re-confirms it, it does not re-close it).
- Runtime re-verify run **inside the fresh checkout**: **PASS, 0
  mismatches** — 783 runtime audio files, 7 prologue files, 3
  animatic files, 20 scenes / 20 timing / 20 SRT / 20 scene clips /
  100 clip files. Manifest counts: music/ambience 22, SFX/UI 519,
  VO 50, mix 30, composed 162. Campaign totals unchanged: 20 scenes
  / 63 shots / 378 s / 21 dialogue cues.

## Clone note

The clone was made with `GIT_LFS_SKIP_SMUDGE=1`, then repaired with
`git lfs install --local` + `git lfs pull` (2709 files, ~4.6 GB,
exit 0) — the same onboarding gap M-G CP1 found: this machine has
no global `git lfs install`, so a plain clone leaves pointers. The
pointer count before the pull was not counted this run (smudge was
skipped by environment, so pointers were present by construction);
the post-pull validator checks are the evidence: 0 pointers,
2013/2013 objects on disk, fsck OK.

## Run notes — two failed validator attempts before the PASS

The final PASS is the third validator run; the first two failed on
the invocation, not on the branch, and both causes are recorded
here so the PASS is not read as a re-run-until-green:

1. First run: `lfs_objects_complete` failed with `git: 'lfs' is not
   a git command` — that invocation ran without
   `~/workspace/tools-bin` on PATH, so `git lfs` was unavailable.
   Every other check passed. The checkout itself was fine: a
   direct check immediately before had already shown 2013/2013
   objects on disk and `git lfs fsck` OK.
2. Second run (PATH fixed): `root_counts_match` failed on
   `Implementation/Reports/MuseMedia` only — fresh 229 files /
   2,678,646 B vs reference 230 files / 2,681,902 B. The 1-file /
   3,256 B difference was the first run's own FAIL output JSON,
   already written into the working clone's Reports directory
   before the second run measured the reference. The stale file
   was deleted and the validator re-run; the third run measured
   the reference clean (229 files, matching fresh) and then wrote
   the PASS JSON. All 8 checks PASS, 0 mismatches.

## Stale labels found (cosmetic, no check affected)

- `verify_runtime_delivery.py` still carries the cumulative
  checkpoint string ending at M-F CP1 (M-E CP1 / M-G CP1 / M-G CP2
  not folded in). The runtime re-verify JSON for this checkpoint
  therefore repeats that stale string; the counts and the PASS are
  from real bytes at this head and are unaffected.
- `verify_fresh_checkout_item5.py` labels its policy source
  `integration … @ 6f2b465`. The reference file this run was
  extracted from integration `6f79853` (36 lines). The two files
  differ by exactly 2 lines: `6f79853` adds the PR #127 LF rules
  for `Implementation/Content/Audio/Deliveries/**/*.json` and
  `Implementation/Reports/MuseMedia/**/*.json`. The check passed
  29/29 against the current file; the tool label is stale, the
  evidence is current.
- The M-G CP3 validator itself corrects one stale label it
  inherited: its `tool` string said
  `check_fresh_checkout_mg_cp1_v1.py` in v2 (copy-paste artifact);
  v3 reports its own name.

## Tables and runtime state

- Runtime audio unchanged: **783** (composed 162, ported 541
  unchanged, music/ambience 22, SFX/UI 519, VO 50, mix 30).
  Campaign totals unchanged: 20/63/378/21. Playback metadata
  unchanged (21 embedded / 0 silent); pronunciation table
  unchanged. Prologue unchanged.
- PR #119 at this head: open, head `14504fb`, mergeable True /
  clean (API read 2026-11-09 ~11:40 JST; head verified
  independently by `git ls-remote` = `14504fb`, 136 commits /
  2105 files from merge-base `cf17178`).

## Files

- Tool: `Tools/MediaProduction/Muse/check_fresh_checkout_mg_cp3_v1.py`
  (CP2 validator logic, checkpoint label updated to M-G CP3, stale
  tool-name string corrected).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP3_VALIDATION_20261109.json`
  (validator PASS, 0 mismatches).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP3_ITEM5_20261109.json`
  (item-5 verifier PASS 5/5).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP3_RUNTIME_REVERIFY_20261109.json`
  (runtime re-verify inside the fresh checkout, PASS 0 mismatches).

## Next

M-F CP2 (palette-adoption re-mixes — blocked on the director/Codex
voice choice) or M-E CP2 (composed SFX — blocked on the Codex
decision) or M-G CP4 (Windows/device pack — needs a Windows
checkout). Nothing in this checkpoint unblocks them; the next run
re-checks issue #116 first.
