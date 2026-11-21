# MEDIA-02 Checkpoint — WO37 M-G CP2: fresh-checkout QA at head c60088c

Date: 2026-11-09 (JST). Branch: `muse/media-production-20261104`.
Integration baseline: `6f79853`. PR #119 stays HOLD; Muse does not
self-merge. Production OFF.

## What was delivered

WO37 M-G checkpoint 2 is the second full fresh-checkout verification
of the media branch, re-baselined to the current head **c60088c**
(the M-G CP1 report commit — this is the first fresh-checkout
verification of the head that itself contains the M-G CP1 validator
tool and report; M-G CP1 only verified head `41a6faa`). A plain
`git clone` of `muse/media-production-20261104` was made into scratch
(`~/workspace/projects/media02-scratch/mg_cp2_fresh`, kept for
re-checks, not part of the repo), then verified byte-for-byte
against the working clone at the same HEAD:

- Fresh HEAD = `c60088ca0f0d90f69a7553dae6d7241120adf27d`, branch
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
  Audio Deliveries 18 / 1,450,104 B; Reports/MuseMedia 225 /
  2,655,459 B.
- OGV: 22/22 real Theora bytes (`OggS` magic), 0 pointers.
- Runtime manifest: 783 entries, sha256 identical on both sides
  (`f0e3a015…9806c`).
- Text endings: 370 JSON/SRT files checked, 0 CR bytes.
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

## Tables and runtime state

- Runtime audio unchanged: **783** (composed 162, ported 541
  unchanged, music/ambience 22, SFX/UI 519, VO 50, mix 30).
  Campaign totals unchanged: 20/63/378/21. Playback metadata
  unchanged (21 embedded / 0 silent); pronunciation table
  unchanged. Prologue unchanged.
- PR #119 at this head: open, head `c60088c`, mergeable True /
  clean (API read via browser ~11:03 JST; head verified
  independently by `git ls-remote` = `c60088c`, 134 commits /
  2100 files from merge-base `cf17178`). Note: the browser's
  transcribed head sha differed by one character (`c60888c…` vs
  `c60088c…`) and its `updated_at` fell in the future relative to
  the run clock, so both are treated as transcription errors and
  the ls-remote value is authoritative; mergeable true / clean is
  consistent with the 10:19 JST verified read at the same head and
  no commit has landed since.

## Files

- Tool: `Tools/MediaProduction/Muse/check_fresh_checkout_mg_cp2_v1.py`
  (CP1 validator logic, checkpoint label updated to M-G CP2).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP2_VALIDATION_20261109.json`
  (validator PASS, 0 mismatches).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP2_ITEM5_20261109.json`
  (item-5 verifier PASS 5/5).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP2_RUNTIME_REVERIFY_20261109.json`
  (runtime re-verify inside the fresh checkout, PASS 0 mismatches).

## Next

M-F CP2 (palette-adoption re-mixes — blocked on the director/Codex
voice choice) or M-E CP2 (composed SFX — blocked on the Codex
decision) or M-G CP3 (Windows/device pack — needs a Windows
checkout). Nothing in this checkpoint unblocks them; the next run
re-checks issue #116 first.
