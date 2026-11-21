# MEDIA-02 Checkpoint — WO37 M-G CP7: fresh-checkout QA at head 9cd5808 (pure network LFS pull + 2 real defects found and fixed)

Date: 2026-11-09 (JST). Branch: `muse/media-production-20261104`.
Integration baseline: `9ac73dc`. PR #119 stays HOLD; Muse does not
self-merge. Production OFF.

## What was delivered

WO37 M-G checkpoint 7 is the sixth full fresh-checkout verification
of the media branch, re-baselined to the current head **9cd5808**
(the M-G CP7 timing-sync fix commit). A plain `git clone` of
`muse/media-production-20261104` was made into scratch
(`~/workspace/projects/media02-scratch/mg_cp7_fresh`, kept for
re-checks, not part of the repo), then verified byte-for-byte
against the working clone:

- Fresh HEAD = `9cd58082c55172f5f2e465a1da5f428de1af8d5d`, branch
  `mg_cp7_fix_check` (local branch tracking the media branch at the
  fix commit; the media branch itself was at `8f8282c` when the
  clone was made, and the fix commit `9cd5808` was fetched into the
  fresh checkout from the local working clone path — no second
  network clone). The validator was run with `--expected-head
  9cd5808…` after the fix; the pre-fix run used `--expected-head
  8f8282c…` (see § Defects).
- **Pure network LFS pull:** after `git lfs install --local`, a
  single `git lfs pull` over the live network completed with
  **exit 0 in 13m47s**, fetching all objects from
  `https://github.com/khanhcoder97/ngumach-huyenan.git/info/lfs`
  with **no local seeding, no re-pull, no repair**. The proxy
  recovered after one transient `Connection reset by peer` on the
  first `git fetch` of this run (retry succeeded immediately).
- `git lfs ls-files`: 2717 tracked files / **2021 distinct OIDs**
  (was 2709 / 2013 at CP6 — the +8 are the M38-A/B + M-B CP1
  binaries: 3 candidate-B OGVs, 1 review MP4, 3 soundtrack A/B
  MP4s, 1 contact-sheet PNG); **2021 objects on disk** —
  complete, no missing object. `git lfs fsck`: **OK, exit 0**
  (run on the fresh clone after the pure network pull).
- **0 LFS pointer files** under the 7 media roots (header-checked,
  first 64 bytes; 2059 files checked).
- Per-root file counts + byte totals match the working clone exactly:
  Cinematics 460 files / 240,078,549 B; Audio/Muse 315 /
  1,626,163,856 B; cinematics runtime 174 / 107,757,837 B; audio
  runtime 784 / 304,098,533 B; Narrative Deliveries 54 / 594,849 B;
  Audio Deliveries 18 / 1,450,104 B; Reports/MuseMedia 254 /
  2,889,413 B (measured before this checkpoint's own report files
  were written).
- OGV: 25/25 real Theora bytes (`OggS` magic), 0 pointers (was
  22 at CP6 — the +3 are the M38-B candidate-B OGVs).
- Runtime manifest: 783 entries, sha256 identical on both sides
  (`f0e3a015…9806c` — same hash as CP5/CP6, manifest unchanged).
- Text endings: 393 JSON/SRT files checked, 0 CR bytes (was 380
  at CP6 — the +13 are the M38-A/B, M-C CP4/CP5 and M-B CP1
  report/manifest JSONs).
- Gói 31 item-5 verifier re-run on the fresh checkout with the
  reference policy extracted from integration `9ac73dc`
  (`mg_cp7_ref.gitattributes`, md5
  `f8376604708a8b9e695a0b4a191191d2`, identical to the CP6
  extraction — the integration policy is unchanged from `6f79853`
  to `9ac73dc`; `agent_scope_v2.json` likewise byte-identical):
  **PASS** — OGV LFS rule present, all 7 LF rules present, all 29
  reference rules present, 0 missing. The item-5 policy gap stays
  closed at this head (closed by the owner's PR #127 merge on
  2026-11-08; this run re-confirms it, it does not re-close it).
- Runtime re-verify run **inside the fresh checkout**: **PASS, 0
  mismatches** — 783 runtime audio files, 7 prologue files, 3
  animatic files, 20 scenes / 20 timing / 20 SRT / 20 scene clips /
  100 clip files. Manifest counts: music/ambience 22, SFX/UI 519,
  VO 50, mix 30, composed 162. Campaign totals unchanged: 20 scenes
  / 63 shots / 378 s / 21 dialogue cues.

## Defects found by this checkpoint (both fixed in this run)

### D1 — 4 working-clone files were LFS pointers, not real bytes

The validator's FIRST run (expected head `8f8282c…`) returned
**FAIL**: `root_counts_match: diffs in ['Art_Source/Cinematics']`
— same file count (460) but the fresh clone was 8,358,762 B
larger. The other 7 checks passed. Cause, proven by a byte diff:

- `Art_Source/Cinematics/P0_Motion/candidate_m38a/CIN_001_candidateB_640x360_30fps.ogv`
  (132 B pointer; real 3,319,028 B)
- `.../CIN_002_candidateB_640x360_30fps.ogv`
  (132 B pointer; real 1,635,327 B)
- `.../CIN_004_candidateB_640x360_30fps.ogv`
  (132 B pointer; real 2,538,804 B)
- `.../P0_candidate_contact_all12.png`
  (131 B pointer; real 866,130 B)

A precise header-scan of the working clone's 7 media roots found
exactly these 4 pointer files (a naive repo-wide `grep` for the
LFS spec URL also matches source files that merely mention the URL
in code/comments — those are not pointers and were not touched).
The objects were never lost: the fresh clone pulled all 4 from the
remote with correct sizes, and the repair restored them from the
working clone's own local LFS objects (`git lfs install --local`
+ `git lfs checkout -- <4 paths>`, 8.4 MB, 0 B/s network).
Restored bytes verified two ways: sha256 identical to the fresh
clone AND identical to the hashes recorded in the M38-A/B subset
manifests (`P0_CANDIDATE_M38A_SUBSET_v1.json`,
`P0_INGEST_M38B_SUBSET_v1.json`). `git status` stayed clean — the
repair changed no tracked content, only the working-tree smudge
state. Likely cause: a checkout/reset in an earlier run ran while
the working clone's `filter.lfs.smudge` was unset, rewriting these
4 files as pointer text; the M38-A/B checkers had verified the
files when they were real at build time, and no later checkpoint
re-checked them until this fresh-checkout QA. The first-run FAIL
JSON is preserved at
`~/workspace/projects/media02-scratch/mg_cp7_validation_FAIL_first_run.json`.

### D2 — M-C CP5 missed the third timing mirror (4 per-scene copies stale)

The runtime re-verify's FIRST run (inside the fresh checkout, at
the pre-fix head) returned **MISMATCHES_FOUND** — 8 mismatches,
all in the 4 scenes M-C CP5 edited:

- `SCENE-CLIP CIN_005/timing: size 2377 != manifest 2850` (+ sha)
- `SCENE-CLIP CIN_009/timing: size 2381 != manifest 2836` (+ sha)
- `SCENE-CLIP CIN_020/timing: size 2345 != manifest 2972` (+ sha)
- `SCENE-CLIP CIN_017/timing: size 2397 != manifest 2745` (+ sha)

Each scene's timing exists in THREE mirrors: `ClientGodot/
assets/cinematics/timing/`, `Implementation/Content/Narrative/
Deliveries/CIN_xxx/`, and the per-scene copy `ClientGodot/assets/
cinematics/CIN_xxx/CIN_xxx_timing_v1.json`. M-C CP5 edited the
first two and refreshed the runtime manifest to the new hashes, but
never touched the per-scene copies. Provenance by git history: at
`9ab006f` (pre-CP5) all three mirrors were byte-identical for all
4 scenes; at `ed1691d` (CP5 content) the per-scene copies still
carried the old hashes (`b82b2582…`, `0f49fc20…`, `64a630bd…`,
`064ac181…`). The diff is exactly the CP5 S03 edit (`onscreen:
null` → `false` + `stagingNote`). The campaign manifest was NOT
affected (its scene entries point at the Deliveries mirror and
record no timing hash). Fix (`9cd5808`, 4 files, 0 violations):
copied the `timing/` mirror over the 4 per-scene copies — no new
content, only propagation of the already-approved CP5 edit.
After the fix, all three mirrors are byte-identical, the
`sceneClips` timing entries match size + sha256, and the re-verify
re-run inside the fresh checkout (updated to the fix commit) is
**PASS, 0 mismatches**. The pre-fix FAIL re-verify JSON is
preserved at
`~/workspace/projects/media02-scratch/mg_cp7_intermediate/MEDIA02_WO37_MG_CP7_RUNTIME_REVERIFY_20261109.json`.

## Scope audit

- Content commit 1 (`27b4bcf`, the CP7 validator tool only):
  **1 path / 0 violations** (base `8f8282c`).
- Content commit 2 (`9cd5808`, the 4-file timing sync):
  **4 paths / 0 violations** (base `27b4bcf`).
- Cumulative from merge-base `cf17178` at the fix commit:
  **2158 paths / 1 violation** — the single `.gitattributes`
  violation is the known merge-base artifact (byte-identical with
  integration `9ac73dc`), not a real divergence. Per the count
  lesson, the report commit adds exactly 4 files (this report + 3
  JSONs), so the head count after the report commit is 2162 paths.

## Stale labels found (cosmetic, no check affected)

- `verify_fresh_checkout_item5.py` still labels its policy source
  `integration … @ 6f2b465`. The reference file this run was
  extracted from integration `9ac73dc` (md5 `f8376604…`, identical
  to the CP6 extraction). The check passed 29/29 against the
  current file; the tool label is stale, the evidence is current.
- `verify_runtime_delivery.py` still carries the cumulative
  checkpoint string ending at M-F CP1 (M-E CP1 / M-G CP1–CP7 not
  folded in). The counts and the PASS are from real bytes at this
  head and are unaffected.
- Validator re-run caveat (found this run): the validator writes
  its `--out` JSON into `Implementation/Reports/MuseMedia/`, a
  counted root — so a second run against the same reference sees
  the first run's output file as a root diff (`Reports/MuseMedia`
  FAIL on the second run here). Re-runs must use `--out` to scratch
  and copy the PASS JSON in afterwards. The second run's FAIL JSON
  was not separately preserved (superseded by the third run's PASS);
  the first run's FAIL JSON (the D1 evidence) is preserved in
  scratch.

## Tables and runtime state

- Runtime audio unchanged: **783** (composed 162, ported 541
  unchanged, music/ambience 22, SFX/UI 519, VO 50, mix 30).
  Campaign totals unchanged: 20/63/378/21. Playback metadata
  unchanged (21 embedded / 0 silent); pronunciation table
  unchanged. Prologue unchanged.
- PR #119 at the pre-push head: open, head `8f8282c`, 154 commits /
  2157 files (API read 2026-11-09 ~20:40 JST; mergeable read
  `None` on the list endpoint — GitHub had not computed it in that
  view, not a merge conflict; last verified mergeable true / clean
  ~20:27 JST at the same head). Issue #116 still 26 comments, no
  new direction since the Gói 38 ACK (~16:09 JST).

## Files

- Tool: `Tools/MediaProduction/Muse/check_fresh_checkout_mg_cp7_v1.py`
  (CP6 validator logic, checkpoint label updated to M-G CP7).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP7_VALIDATION_20261109.json`
  (validator PASS, 0 mismatches, at fix head `9cd5808`).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP7_ITEM5_20261109.json`
  (item-5 verifier PASS 5/5).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP7_RUNTIME_REVERIFY_20261109.json`
  (runtime re-verify inside the fresh checkout, PASS 0 mismatches).

## Next

M-F CP2 (palette-adoption re-mixes — blocked on the director/Codex
voice choice) or M-E CP2 (composed SFX — blocked on the Codex
decision). Nothing in this checkpoint unblocks them; the next run
re-checks issue #116 first. The PR #119 description + ACK payloads
prepared for CP5 + M-B CP1 (`pr119_update_cp5_mb_cp1.json` /
`ack_cp5_mb_cp1_issue116.json`) are now STALE — this checkpoint
moved the head — and must be regenerated to cover CP5 + M-B CP1 +
CP7 at the new head before posting (main thread, owner approval
card for GitHub writes).
