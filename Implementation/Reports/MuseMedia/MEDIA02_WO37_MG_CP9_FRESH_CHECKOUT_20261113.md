# MEDIA-02 WO37 M-G CP9 — Fresh-checkout verification of the M-B CP4 + PROLOGUE V1 FIX binary delta

Date: 2026-11-13 (JST) · Branch: `muse/media-production-20261104` ·
Baseline: `be9ccb8` (M-B CP4 + PROLOGUE V1 FIX, already posted) ·
Content commit: `923b5ba` (rebased onto `6df7e24`, see §1)
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — QA evidence for Codex
review; no mix, runtime file, or casting decision is changed here.
PR #119 stays HOLD; Muse does not self-merge.

## 1. Why this checkpoint exists

Gói 38 rule 1 stops repeat fresh-clone/hash checkpoints over the
same bytes without a binary, policy, or tool delta. The delta
`7f461da..be9ccb8` IS a real binary delta: M-B CP4 re-rendered 14
standard-720p MP4s with the v2 mixes, and the prologue fix
re-rendered the v1 mix and re-derived the runtime CIN_000 film
and its variants. M-G CP8 verified the M-F CP2 delta only; the
two blocks since then were checked in the working clone (CP4
checker 271/271, fix checker 50/50) — the same place where M-G
CP7 found defect D1 (LFS pointers masquerading as real files).
A working-clone check cannot catch that defect class for new
files; only a fresh checkout with a pure-network LFS pull can.
This checkpoint verifies exactly that delta and nothing else:
it does NOT re-run the full CP7 fresh-checkout suite over
unchanged bytes, and it does NOT re-count the 8 pre-existing
SCENE-CLIPS mismatches — no file in that set is in the 40-file
delta (verified from the diff list), so the set was unchanged
by this delta at the verified head. While this run was in
progress, the main thread closed those 8 mismatches in a
separate bookkeeping block (content `53472cf`, head
`6df7e24`, dedicated checker 92/92, full
`validate_media_deliveries` now PASS with 0 mismatches,
owner order "làm tiếp khối kia đi"). That block touched only
the 4 CIN_005/009/017/020 scene export manifests plus its own
checker/report — zero overlap with the 40-file delta or with
this checkpoint's files — so M-G CP9's evidence stands as
measured at `be9ccb8`, and this checkpoint was rebased onto
`6df7e24` before delivery (content commit `923b5ba`).

Note on timing: the M-B CP4 + PROLOGUE V1 FIX payload pair was
already POSTED at this head (PR body 114,929 chars, ACK
6832706291, issue #116 now 32 comments) before this run
started, so this verification confirms the posted claims
rather than gating them.

## 2. Method

- Fresh clone of `muse/media-production-20261104` into scratch
  (`~/workspace/projects/media02-scratch/mg_cp9_fresh`, kept for
  re-checks, not part of the repo) with `GIT_LFS_SKIP_SMUDGE=1`.
  Fresh HEAD = `be9ccb8af8fea2ae5632952cc2b94ad4148d40fa`, clean.
- Pre-pull state: all delta LFS files were 131–133 B pointers,
  as expected under skip-smudge.
- `git lfs install --local`, then a pure-network
  `git lfs pull -I` for the delta paths — 21 Standard720 MP4s,
  14 v2 mix WAVs, 21 runtime 640×360 masters, the prologue
  mix/takes/runtime-film paths — exit 0, no local seeding.
- The two superseded objects the fix checker uses as controls
  (broken mix `f026ed3e…`, old MP4 `88049317…`) were fetched
  with `git lfs fetch -I '<both paths>' origin 7f461da` and
  sha-verified in the local object store.
- Both original checkers re-run verbatim in the fresh clone,
  plus a new independent validator
  `check_fresh_delta_mg_cp9_v1.py` (measurement conventions
  copied from the two checkers: sha256, ffprobe, single-pass
  loudnorm with brace matching, normalized cross-correlation):
  **PASS 126/126, 0 failures**
  (`MEDIA02_WO37_MG_CP9_VALIDATION_20261113.json`).
  Two in-build fixes, recorded per standing rule: the
  validator's `is_pointer` used `Path.read_bytes(132)` (no such
  signature — now reads 132 bytes from an open handle), and
  the LFS census took field 1 of `git lfs ls-files` output
  (`*`/`-`) instead of the OID in field 0. No repo bytes were
  affected by either fix.

## 3. Results

### 3a. The CP4 checker, re-run in the fresh clone: 270/271

One failure, expected and explained — not a defect:

| Check | Result |
|---|---|
| `CIN_000 video source sha == manifest + CP2` | **FAIL** (sole failure) |
| All other 270 checks (13 other sources, 14 outputs, 7 carried-over, budget, runtime-tree clean) | PASS, worst values identical to the build run: frame downscale mean\|diff\| 4.215, 2×2 range 6.07, audio corr 0.9998, \|dLUFS\| 0.04, \|dTP\| 0.10 |

Why the single failure is expected: the CP4 checker was written
against the pre-fix runtime master (`88049317…`, 12,249,759 B).
The prologue fix re-muxed that file (audio only) to
`86b7cdd9…` (12,248,889 B). The file sha therefore differs from
the CP4 manifest while the delivered CP4 720p outputs are
untouched — their shas still match the manifest, and the frame
comparisons against the new master still pass because the video
stream is bit-identical (stream-hash proof in §3c). The CP4
checker is stale for this one source-sha check at head
`be9ccb8`; the deliverables are not.

### 3b. The prologue fix checker, re-run in the fresh clone: 50/50 PASS

Every value reproduces the build run exactly: takes in the
fixed mix SEG01 +0.982 / SEG02 +0.989 / SEG03 +0.980 /
SEG04 +0.986 / SEG05 +0.975 / Ly An +0.986, all lag 0.000 s;
broken-mix controls −0.020…+0.011; fixed mix −22.37 LUFS /
−3.11 dBTP; MP4 embedded corr 1.000 (−22.39 LUFS), OGV 0.998
(−22.41 LUFS), subtitled −20.39 LUFS / −1.19 dBTP (+2.0 dB
presentation gain).

### 3c. The M-G CP9 validator: 126/126 PASS

- Delta `7f461da..be9ccb8` is exactly the 40 known files
  (CP4 content 17 + CP4 report 2 + fix content 19 + fix
  report 2); CP4 block 17, fix block 19 — both re-derived.
- All 21 Standard720 MP4s are real bytes (not pointers),
  sha/bytes == CP4 manifest, probe 1280×720@30 + AAC,
  duration == manifest; set total **148,002,469 B**.
- Fixed mix sha `4f8224e1…` byte-identical at all three paths
  (fixed render, Art_Source canonical, runtime copy);
  loudnorm re-measured **−22.37 LUFS / −3.11 dBTP**.
- Runtime CIN_000 MP4/OGV/subtitled/720p-subtitled shas ==
  export/FIX720 manifests; embedded audio is the fixed mix
  (MP4 corr 1.000, OGV 0.998, subtitled 1.000).
- **Stream-hash proof:** current runtime MP4 video stream ==
  pre-fix MP4 video stream — the re-mux changed audio only.
- Runtime audio manifest total **783** (784 files under
  `ClientGodot/assets/audio` including the manifest itself).
- LFS census: **2832 tracked / 2135 distinct OIDs, identical
  in the fresh and working clones** (CP8 recorded 2831/2135;
  +1 tracked file is the new fixed-mix render path).

## 4. Two number discrepancies found and resolved

Both were found by re-deriving counts from disk; neither
affects any delivered byte, and the posted payload already
carries the corrected numbers:

1. **Fix report cumulative 2368 vs posted 2373.** The
   in-repo fix report measured the cumulative diff at its
   pre-rebase content commit `58185dd` (base `7f461da`):
   2362 + 6 new paths = 2368. After the rebase onto the CP4
   head `41bfbae`, the cumulative at content `962b6df` is
   **2373** (2368 + the CP4 report's 2 files + CP4's 3 new
   paths), and **2375 at head `be9ccb8`** (+2 report files).
   Re-derived here: `cf17178..962b6df` = 2373,
   `cf17178..be9ccb8` = 2375 — matching the posted PR body
   and ACK. The fix report's 2368 is a stale pre-rebase
   figure, left as written (historical record).
2. **Fix block "21 paths" vs "19 paths".** The fix content
   block is **19 paths** (`41bfbae..962b6df`); the ACK's 21
   counts content + the 2 report files (`41bfbae..be9ccb8`).
   This report uses the CP8 convention (content block only)
   and states the definition explicitly.

## 5. Defects: none found

The D1 defect class (LFS pointer masquerading as a real file)
is **absent** from the M-B CP4 + prologue-fix delta: every
binary object exists on the remote, pulls cleanly over the
network, and hashes identically to the build-time
measurements. No repair was needed and no file was modified
by this checkpoint. The working clone needed no restore
(`git status` clean before and after).

## 6. Scope audit

- Block (`6df7e24` → content `923b5ba`): **2 paths, 0 violations**
  (validator + validation JSON).
- Cumulative vs merge-base `cf17178` at the content commit:
  **2380 paths, 1 violation** — the single `.gitattributes`
  violation is the known merge-base artifact (sha256
  `23352e4c…`, byte-identical with integration `f3db6b3`,
  re-verified this run), not a new breach. Count chain for
  the record: 2375 at `be9ccb8` → 2376 at bookkeeping content
  `53472cf` → 2378 at its head `6df7e24` (+2 report files) →
  2380 at this content commit (+2). Per the count lesson,
  this report commit adds exactly 1 file, so the head count
  after the report commit is 2381 paths.
- Integration HEAD re-verified by explicit fetch + ls-remote:
  `f3db6b3`, unchanged.

## 7. Limits and honest notes

- Scoped delta QA only: the full CP7 fresh-checkout suite
  (runtime re-verify, item-5 policy, OGV census) was NOT
  re-run — no runtime, policy, or tool delta justifies it
  under Gói 38 rule 1. The CP7 baseline (fresh-checkout QA
  at 9cd5808) still stands.
- The 8 pre-existing SCENE-CLIPS mismatches (CIN_005/009/
  017/020) were not re-counted here: they were closed by the
  separate bookkeeping block (`6df7e24`, checker 92/92, full
  validator PASS 0 mismatches) while this run was in progress,
  and the file sets do not overlap (§1).
- All mixes remain DRAFT_NOT_FINAL and NOT_AUDITIONED. This
  checkpoint verifies bytes and measurements, not sound; the
  ear verdict belongs to the listener, runtime adoption to
  Codex.
- Issue #116 re-checked this run (public API): 32 comments,
  latest Muse ACK 6832706291 (M-B CP4 + PROLOGUE V1 FIX,
  posted 2026-11-13 ~03:40 JST). No new Codex/owner
  direction since Gói 39 (6815238814).

## Files

- Tool: `Tools/MediaProduction/Muse/check_fresh_delta_mg_cp9_v1.py`
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP9_VALIDATION_20261113.json`
  (validator PASS 126/126 at head be9ccb8, fresh clone).
- Evidence (scratch, not in repo):
  `~/workspace/projects/media02-scratch/mg_cp9_cp4_rerun.json`
  (CP4 checker re-run 270/271), fresh clone
  `~/workspace/projects/media02-scratch/mg_cp9_fresh`.
- This report.

## Next

The posted M-B CP4 + PROLOGUE V1 FIX payload now has
independent fresh-checkout verification behind it, and the 8
pre-existing SCENE-CLIPS mismatches are closed by the
bookkeeping block (`6df7e24`). Remaining standing blocks per
the posted ACK: ear-audition of the fixed prologue (priority
listen — canonical runtime or subtitled variant); 32 shots
motion wait on character lock; full OGV 720p set deferred per
Gói 39. PR #119 stays HOLD; Muse does not self-merge.
