# MEDIA-02 Checkpoint — WO37 M-G CP5: fresh-checkout QA at head b09d718

Date: 2026-11-09 (JST). Branch: `muse/media-production-20261104`.
Integration baseline: `6f79853`. PR #119 stays HOLD; Muse does not
self-merge. Production OFF.

## What was delivered

WO37 M-G checkpoint 5 is the fourth full fresh-checkout verification
of the media branch, re-baselined to the current head **b09d718**
(the M-G CP4 report commit — this is the first fresh-checkout
verification of the head that itself contains the M-G CP4 validator
tool and report; M-G CP4 only did a static Windows-compatibility
audit, no fresh clone). A plain `git clone` of
`muse/media-production-20261104` was made into scratch
(`~/workspace/projects/media02-scratch/mg_cp5_fresh`, kept for
re-checks, not part of the repo), then verified byte-for-byte
against the working clone:

- Fresh HEAD = `b09d718c632536aa17d7372cca99973df460c492`, branch
  `muse/media-production-20261104` — matches the remote media
  branch. The M-G CP5 validator tool itself was committed first
  (`a764b7d`, outside the media roots), so the validator was run
  with `--expected-head b09d718…`; the only tree difference between
  the fresh clone and the reference is that one tool file.
- `git lfs ls-files`: 2709 tracked files / **2013 distinct OIDs**;
  **2088 objects on disk** after repair (see the network incident
  below) — complete, no missing object. `git lfs fsck`: **0
  openError, exit 0** (run after the repair; the validator itself
  does not invoke fsck).
- **0 LFS pointer files** under the 7 media roots (header-checked,
  first 64 bytes).
- Per-root file counts + byte totals match the working clone exactly
  (measured before this checkpoint's own report files were written):
  Cinematics 451 files / 219,733,487 B; Audio/Muse 315 /
  1,626,163,856 B; cinematics runtime 174 / 107,755,934 B; audio
  runtime 784 / 304,098,533 B; Narrative Deliveries 50 / 343,200 B;
  Audio Deliveries 18 / 1,450,104 B; Reports/MuseMedia 235 /
  2,710,654 B.
- OGV: 22/22 real Theora bytes (`OggS` magic), 0 pointers.
- Runtime manifest: 783 entries, sha256 identical on both sides
  (`f0e3a015…500b`).
- Text endings: 377 JSON/SRT files checked, 0 CR bytes.
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

## Network incident — LFS batch API failing at the proxy (this run)

The live network LFS pull did **not** complete this run, and this
checkpoint does not pretend otherwise:

- The first `git lfs pull` fetched 1138/2013 objects over ~11
  minutes, then its session ended with the pull incomplete (873
  files still pointers at that point — the count came from an
  ad-hoc `grep -rl` that also matches the pointer-header string
  inside `.py` tool sources, so it is an upper bound, not the
  validator's authoritative header count).
- Four re-pull attempts (including a single-object
  `git lfs fetch -I`) failed immediately, exit 2: `batch request:
  Connection closed by 198.19.0.1 port 3128: exit status 255`
  / `Failed to fetch some objects from
  'https://github.com/khanhcoder97/ngumach-huyenan.git/info/lfs'`.
  General GitHub HTTPS works (batch endpoint answers 405 to a bare
  GET, api.github.com answers 200) — only the LFS batch POST is
  being closed by the proxy right now.
- Repair, all from local content-addressed stores, verified by
  hash: the remaining objects were seeded from the working clone
  (2041 objects), then the 41 objects missing from both the fresh
  clone and the working clone were copied from the earlier fresh
  clones (`mg_cp1/2/3_fresh`, complete network pulls; 41/41 found,
  0 not found anywhere local). `git lfs checkout` then smudged
  2709/2709 files. `git lfs fsck` after the repair: 0 openError.
  Two of the 41 were `docs/production/Art_Concept_References`
  images outside the media roots
  (`02_simple_pixel_street.png`, `03_hub_wide_camera_comparison.png`);
  both are real PNGs now (1672×941, 1983×793). The working clone
  itself fails fsck on those two objects — a pre-existing gap in
  the reference clone, not introduced by this checkpoint.
- What this means: this checkpoint proves fresh-checkout
  byte-completeness at `b09d718` (every object hash-verified by
  fsck, every media-root check from real bytes). It does **not**
  re-prove the live network LFS pull path, which is currently
  failing at the proxy. When the proxy recovers, a later run
  should re-run a pure network pull (M-G CP6 candidate) rather
  than assuming the path is healthy.

## Run notes — two invocation failures before the PASS

1. First item-5 run: `FileNotFoundError:
   /tmp/mg_cp5_ref.gitattributes` — the reference policy file
   extracted earlier in this run had been cleaned from `/tmp`
   between steps. Re-extracted from integration `6f79853` (36
   lines, md5 `f8376604708a8b9e695a0b4a191191d2`, identical to the
   first extraction) and re-ran: PASS 5/5. The failure was the
   invocation, not the branch.
2. The validator itself passed on the first run (exit 0, 8/8).

## Stale labels found (cosmetic, no check affected)

- `verify_runtime_delivery.py` still carries the cumulative
  checkpoint string ending at M-D CP7 (M-E CP1 / M-G CP1–CP5 not
  folded in). The runtime re-verify JSON for this checkpoint
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
- The M-G CP5 validator reports its own tool name correctly
  (`check_fresh_checkout_mg_cp5_v1.py`).

## Tables and runtime state

- Runtime audio unchanged: **783** (composed 162, ported 541
  unchanged, music/ambience 22, SFX/UI 519, VO 50, mix 30).
  Campaign totals unchanged: 20/63/378/21. Playback metadata
  unchanged (21 embedded / 0 silent); pronunciation table
  unchanged. Prologue unchanged.
- PR #119 at this head: open, head `b09d718`, mergeable True /
  clean (API read 2026-11-09 ~13:40 JST; head verified
  independently by `git ls-remote` = `b09d718`, 140 commits /
  2113 files from merge-base `cf17178` — before this checkpoint's
  commits).

## Files

- Tool: `Tools/MediaProduction/Muse/check_fresh_checkout_mg_cp5_v1.py`
  (CP3 validator logic, checkpoint label updated to M-G CP5).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP5_VALIDATION_20261109.json`
  (validator PASS, 0 mismatches).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP5_ITEM5_20261109.json`
  (item-5 verifier PASS 5/5).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP5_RUNTIME_REVERIFY_20261109.json`
  (runtime re-verify inside the fresh checkout, PASS 0 mismatches).

## Next

M-F CP2 (palette-adoption re-mixes — blocked on the director/Codex
voice choice) or M-E CP2 (composed SFX — blocked on the Codex
decision) or M-G CP6 (live Windows checkout — needs a Windows
machine; or a pure network LFS re-pull when the proxy recovers).
Nothing in this checkpoint unblocks them; the next run re-checks
issue #116 first.
