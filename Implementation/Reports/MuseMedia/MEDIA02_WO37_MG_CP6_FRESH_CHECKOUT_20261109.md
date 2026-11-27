# MEDIA-02 Checkpoint — WO37 M-G CP6: fresh-checkout QA at head 14b588c (pure network LFS pull)

Date: 2026-11-09 (JST). Branch: `muse/media-production-20261104`.
Integration baseline: `6f79853`. PR #119 stays HOLD; Muse does not
self-merge. Production OFF.

## What was delivered

WO37 M-G checkpoint 6 is the fifth full fresh-checkout verification
of the media branch, re-baselined to the current head **14b588c**
(the M-G CP5 report commit). A plain `git clone` of
`muse/media-production-20261104` was made into scratch
(`~/workspace/projects/media02-scratch/mg_cp6_fresh`, kept for
re-checks, not part of the repo), then verified byte-for-byte
against the working clone:

- Fresh HEAD = `14b588c663a6d53295b34f1d632e84c48c7f5ca9`, branch
  `muse/media-production-20261104` — matches the remote media
  branch. The M-G CP6 validator tool itself was committed first
  (`8c66712`, outside the media roots), so the validator was run
  with `--expected-head 14b588c…`; the only tree difference between
  the fresh clone and the reference is that one tool file.
- **Pure network LFS pull — this run's headline, and the reason CP6
  exists:** after `git lfs install --local`, a single
  `git lfs pull` over the live network completed with **exit 0 in
  13m06s**, fetching all objects from
  `https://github.com/khanhcoder97/ngumach-huyenan.git/info/lfs`
  with **no local seeding, no re-pull, no repair**. This re-proves
  the live network LFS pull path that M-G CP5 could not prove (its
  batch API was closed by the proxy mid-pull at 1138/2013 objects).
  The proxy has recovered; no workaround was needed this run.
- `git lfs ls-files`: 2709 tracked files / **2013 distinct OIDs**;
  **2013 objects on disk** — complete, no missing object.
  `git lfs fsck`: **OK, exit 0** (run on the fresh clone after the
  pure network pull; no repair step preceded it).
- **0 LFS pointer files** under the 7 media roots (header-checked,
  first 64 bytes).
- Per-root file counts + byte totals match the working clone exactly
  (measured before this checkpoint's own report files were written):
  Cinematics 451 files / 219,733,487 B; Audio/Muse 315 /
  1,626,163,856 B; cinematics runtime 174 / 107,755,934 B; audio
  runtime 784 / 304,098,533 B; Narrative Deliveries 50 / 343,200 B;
  Audio Deliveries 18 / 1,450,104 B; Reports/MuseMedia 239 /
  2,737,010 B (was 235 / 2,710,654 B at CP5 — the +4 files are the
  M-G CP5 report files themselves).
- OGV: 22/22 real Theora bytes (`OggS` magic), 0 pointers.
- Runtime manifest: 783 entries, sha256 identical on both sides
  (`f0e3a015…500b` — same hash as CP5, manifest unchanged).
- Text endings: 380 JSON/SRT files checked, 0 CR bytes (was 377 at
  CP5 — the +3 are the M-G CP5 report JSONs).
- Gói 31 item-5 verifier re-run on the fresh checkout with the
  reference policy extracted from integration `6f79853` (36 lines,
  md5 `f8376604708a8b9e695a0b4a191191d2`, identical to the CP5
  extraction): **PASS** — OGV LFS rule present, all 7 LF rules
  present, all 29 reference rules present, 0 missing. The item-5
  policy gap stays closed at this head (closed by the owner's PR
  #127 merge on 2026-11-08; this run re-confirms it, it does not
  re-close it).
- Runtime re-verify run **inside the fresh checkout**: **PASS, 0
  mismatches** — 783 runtime audio files, 7 prologue files, 3
  animatic files, 20 scenes / 20 timing / 20 SRT / 20 scene clips /
  100 clip files. Manifest counts: music/ambience 22, SFX/UI 519,
  VO 50, mix 30, composed 162. Campaign totals unchanged: 20 scenes
  / 63 shots / 378 s / 21 dialogue cues.

## Scope audit

- Content commit of this checkpoint (`8c66712`, the validator tool
  only): **1 path / 0 violations** (base `14b588c`).
- Cumulative from merge-base `cf17178` at the content commit:
  **2119 paths / 1 violation** — the single `.gitattributes`
  violation is the known merge-base artifact (byte-identical with
  integration `6f79853`), not a real divergence. Per the count
  lesson, the report commit adds exactly 4 files (this report + 3
  JSONs), so the head count after the report commit is 2123 paths.

## Stale labels found (cosmetic, no check affected)

- `verify_runtime_delivery.py` still carries the cumulative
  checkpoint string ending at M-D CP7 (M-E CP1 / M-G CP1–CP6 not
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
- The M-G CP6 validator reports its own tool name correctly
  (`check_fresh_checkout_mg_cp6_v1.py`).

## Tables and runtime state

- Runtime audio unchanged: **783** (composed 162, ported 541
  unchanged, music/ambience 22, SFX/UI 519, VO 50, mix 30).
  Campaign totals unchanged: 20/63/378/21. Playback metadata
  unchanged (21 embedded / 0 silent); pronunciation table
  unchanged. Prologue unchanged.
- PR #119 at the pre-push head: open, head `14b588c`, 142 commits /
  2118 files (API read 2026-11-09 ~15:00 JST; mergeable read
  `None` / state `unknown` on that call — GitHub was still
  computing it, not a merge conflict; last verified mergeable
  true / clean ~14:10 JST at the same head).

## Files

- Tool: `Tools/MediaProduction/Muse/check_fresh_checkout_mg_cp6_v1.py`
  (CP5 validator logic, checkpoint label updated to M-G CP6).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP6_VALIDATION_20261109.json`
  (validator PASS, 0 mismatches).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP6_ITEM5_20261109.json`
  (item-5 verifier PASS 5/5).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP6_RUNTIME_REVERIFY_20261109.json`
  (runtime re-verify inside the fresh checkout, PASS 0 mismatches).

## Next

M-F CP2 (palette-adoption re-mixes — blocked on the director/Codex
voice choice) or M-E CP2 (composed SFX — blocked on the Codex
decision) or M-G CP7 (next fresh-checkout QA at the new head, or a
live Windows checkout — needs a Windows machine). Nothing in this
checkpoint unblocks them; the next run re-checks issue #116 first.
The network-pull question from CP5 is now closed: the pure network
LFS pull works again.
