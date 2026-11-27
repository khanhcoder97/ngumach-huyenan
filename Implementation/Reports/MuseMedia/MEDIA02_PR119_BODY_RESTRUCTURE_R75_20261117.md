# MEDIA-02 — PR #119 Body Restructure R75: delivery index + body v2 coverage to `2ae76b3`

Date: 2026-11-17 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `2ae76b3` (PR119 BODY RESTRUCTURE R74 report). Content commit: `cd0a56a`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R75 does

R74 left a disclosed gap: the delivery index covered 337 commits to
`d0e67f5`; R74's own 2 commits were to fold in at R75. Since then the
R74 body v2 was NOT posted — the live PR description is still the R8 body
(head `f2ba478` · 207 · 2419, verified by a FRESH public API read of the
single-PR endpoint this round 2026-11-17 ~06:48 JST via curl (quota core
remaining 48 after the comments read): `head_sha` `2ae76b3`, mergeable true,
mergeable_state unstable, commits 339, changed_files 2617, additions 242780,
deletions 0; live body text is the R8 body — head line `f2ba478` · 207 ·
2419, title ending "refs #116 + R8" (763 ký tự); live title is the R8
title). The R74 payload (`pr119_update_body_v2_r74.json`, 45.578 ký tự)
is now SUPERSEDED by the R75 body v2 before any tap, following the same
pattern as R3/R4/R5/R7/R9–R74. No new Codex/owner direction has landed
on issue #116 as of the fresh verified read this round (public API,
comments endpoint, 2026-11-17 ~06:48 JST via curl: 34 comments, latest
ACK `6862732081`, 2026-11-13T19:24:48Z). Note: this is a detached
scheduled run (~06:50 JST, before the 09:00 quiet-hours start), so the
R75 payload is prepared here but NOT presented — presentation belongs to
the main agent in-hours (09:00–21:30), or R76 will supersede it.

Fresh derivation at `2ae76b3` (~06:48 JST): `git rev-list --count
cf17178..2ae76b3` = 339 commits, `git diff --name-only` = 2617 files,
`--shortstat` = 242780 insertions, 0 deletions — git and the fresh public
API read agree exactly. `git merge-tree --write-tree` `2ae76b3` vs
integration `f3db6b3` exit 0, 0 conflicts, tree
`b7f54ddc5d1d9770460f6a27c163c5834d286ddd`.

R75 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `2ae76b3` (339 commits / 2617 files /
  242780 additions; API figures cited are the FRESH API read at `2ae76b3`
  ~06:48 JST this round — mergeable true/unstable, live body still R8 —
  plus the fresh git derivation at `2ae76b3`; delta `d0e67f5..2ae76b3`:
  5 paths, 282 insertions, 9 deletions); one row appended — PR119 BODY
  RESTRUCTURE R74 (`c722662`/`2ae76b3`), including the note that its body
  payload was superseded by the R75 body v2 before posting; issue line
  still 34 comments (fresh verified read ~06:48 JST this round, disclosed
  in the index itself). The index now covers every block through
  `2ae76b3`; R75's own 2 commits fold in at the next index update (R76),
  disclosed in the index itself.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `2ae76b3` · 339 · 2617 (with the fresh git derivation at `2ae76b3`,
  the fresh API read at `2ae76b3`, and the fresh merge-tree cross-check
  at `2ae76b3`), plus the R74 paragraph in "Khối mới nhất" and the R75
  note. The stale index reference in "Về bản mô tả này" (head `d0e67f5`)
  is also fixed to `2ae76b3`. The live PR description is refreshed from
  this file in the posting round that follows R75 (owner tap) — the R8
  body v2 already live is the base; only the R74 paragraph + new head
  line are new.
- **Checker** `check_pr119_restructure_r75_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims. **PASS 17/17**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R75_VALIDATION_20261117.json`).
  First run PASS 17/17 (no amend needed this round). The checker was
  written fresh (not sed-copied from R74) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale `d0e67f5`/`337`/
  `2614`/`242507` references on the head/milestone lines) before
  the run — the R69 sed-order copy defect (mangled full COVER SHA) was
  avoided by construction.

## Verification

- Merge-tree `2ae76b3` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `b7f54ddc5d1d9770460f6a27c163c5834d286ddd`. Merge-tree at the R75
  content head `cd0a56a` vs `f3db6b3`: exit 0, tree
  `3dee074176173c215a017686fc3ebf121c8db9e4`.
- PR API single-PR read: FRESH this round (public API, core quota
  remaining 48 after the comments read) 2026-11-17 ~06:48 JST (via curl):
  `head_sha` `2ae76b3`, mergeable true, mergeable_state unstable, commits
  339, changed_files 2617, additions 242780, deletions 0, body_len
  11.793. Fresh git derivation at `2ae76b3` this round: commits 339,
  changed_files 2617, additions 242780, deletions 0 — identical to the
  API. Live body text is the R8 body per the read (head line `f2ba478` ·
  207 · 2419, body_len 11.793; R61 verified it byte-exact against the R8
  payload on disk at ~16:26 JST 2026-11-16, and the body is unchanged
  since). Note: mergeable_state unstable only means CI is still running
  on the new head — normal right after a push, as at R68/R69/R72/R73.
- Issue #116: 34 comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2,
  posted 2026-11-14 ~04:24 JST); no new Codex/owner direction since
  Gói 39 (`6815238814`). Fresh read via public API ~06:48 JST (comments
  endpoint, curl, per_page=100; list ends at `6862732081`
  2026-11-13T19:24:48Z, no mention of Gói 40 or R74/R75).
- Scope audit: R75 block 3 paths / 0 violations; cumulative at the R75
  content commit 2618 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4cfa38` on both sides, re-verified at `cd0a56a`).
  Merge-tree at the R75 content head `cd0a56a` vs `f3db6b3`: exit 0,
  tree `3dee0741…`.

## Next

Posting round (owner tap, in-hours): PR #119 description refresh to the
R75 body v2 (R74 paragraph + new head line are the only new parts vs the
live R8 body). Payload `pr119_update_body_v2_r75.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R75 push
(title 764 ký tự, kết thúc "+ R75"; body = body v2 R75 trong repo, head
line làm tươi tới head sau khi R75 push). NOT presented this run — the
run is detached and before the 09:00 quiet-hours start; presentation
belongs to the main agent in-hours (09:00–21:30), or R76 will supersede
it. No R74 widget was ever presented — the R74 payload was superseded
by R75 before any presentation; do not tap any R74 widget. No separate
ACK comment for R75: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
