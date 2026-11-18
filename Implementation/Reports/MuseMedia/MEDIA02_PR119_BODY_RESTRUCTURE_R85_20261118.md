# MEDIA-02 — PR #119 Body Restructure R85: delivery index + body v2 coverage to `5f0a468`

Date: 2026-11-18 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `5f0a468` (PR119 BODY RESTRUCTURE R84 report). Content commit: `48fe92e`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R85 does

R84 left a disclosed gap: the delivery index covered 357 commits to
`de37312`; R84's own 2 commits were to fold in at R85. Since then the
R84 body v2 was NOT POSTED — the first posting attempt 2026-11-18
~14:29 JST failed because the approval card expired (connector
confirmed not performed; live body still R78). No new Codex/owner
direction has landed on issue #116 as of the fresh verified read
closest to this round (public API ~13:11 JST, R83 round: 34 comments,
latest ACK `6862732081`, 2026-11-13T19:24:48Z); this round's own
comments-endpoint reads were blocked by a 403 rate limit (tried twice
~14:43–14:46 JST, shared egress IP), so issue #116 was not re-read
this round — see the transient note below. Note: this is a detached
scheduled run (started ~14:40 JST, in-hours 09:00–21:30), so
presentation belongs to the main agent — the owner should tap while
still at the machine, since the approval card lives about 30 minutes.
The R84 payload is SUPERSEDED by R85 and must NOT be tapped.

Fresh derivation at `5f0a468` (~14:42 JST): `git rev-list --count
cf17178..5f0a468` = 359 commits, `git diff --name-only` = 2647 files,
`--shortstat` = 245542 insertions, 0 deletions. `git merge-tree
--write-tree` `5f0a468` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `978db1659bc1ccb61e1a0a6100cd07301acbd03c`. The public API
single-PR endpoint read fresh this round (~14:42 JST): head_sha
`5f0a468`, commits 359, changed_files 2647, additions 245542,
deletions 0, mergeable true, mergeable_state clean, body_len 47.708 —
git and the fresh API read agree absolutely, and the live body is
still the posted R78 body (sha256 `4f4e87fb`).

R85 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `5f0a468` (359 commits / 2647 files /
  245542 additions; API figures cited are the FRESH API read at
  `5f0a468` ~14:42 JST — mergeable true/clean, live body R78; delta
  `de37312..5f0a468`: 5 paths, 302 insertions, 9 deletions); one row
  appended — PR119 BODY RESTRUCTURE R84 (`544b9f7`/`5f0a468`), including
  the note that its body v2 was NOT posted (first attempt ~14:29 JST,
  approval card expired, superseded by R85); issue line still 34
  comments (last verified read ~13:11 JST, disclosed in the index
  itself). The index now covers every block through `5f0a468`; R85's
  own 2 commits fold in at the next index update (R86), disclosed in
  the index itself.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `5f0a468` · 359 · 2647 (with the fresh git derivation at `5f0a468`,
  the fresh API read at `5f0a468`, and the fresh merge-tree cross-check
  at `5f0a468`), plus the R84 paragraph in "Khối mới nhất" and the R85
  note. The stale index reference in "Về bản mô tả này" (head
  `de37312`) is also fixed to `5f0a468`. The live PR description is
  refreshed from this file in the posting round that follows R85 (owner
  tap) — the R78 body v2 already live is the base; only the R83 + R84
  paragraphs + new head line are new.
- **Checker** `check_pr119_restructure_r85_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims. **PASS 17/17**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R85_VALIDATION_20261118.json`).
  First run PASS 17/17 (no amend needed this round). The checker was
  written fresh (not sed-copied from R84) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale `de37312`/`357`/
  `2644`/`245249` references in the checker — the only `de37312` hits in
  the index/body are the legitimate delta range `de37312..5f0a468` and
  the R83/R84 historical rows) before the run — the R69 sed-order copy
  defect (mangled full COVER SHA) was avoided by construction.

## Verification

- Merge-tree `5f0a468` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `978db1659bc1ccb61e1a0a6100cd07301acbd03c`. Merge-tree at the R85
  content head `48fe92e` vs `f3db6b3`: exit 0, tree
  `13d47bc0dea39332f92e4033e8b2bcb188096662`.
- PR API single-PR read: FRESH this round (~14:42 JST): head `5f0a468`,
  359 commits, 2647 changed files, 245542 additions, 0 deletions,
  mergeable true, mergeable_state clean, body_len 47.708 (R78 body,
  sha256 `4f4e87fb`). The very first PR-endpoint call this round
  returned a rate-limit error dict (shared egress IP); the retry read
  clean — no stale figure was recorded.
- Issue #116: NOT re-read this round (comments endpoint 403 rate limit,
  twice ~14:43–14:46 JST on two egress IPs; the issue page read fresh
  via browser.open ~14:44 JST shows only the issue body, not the
  comment list; connector `issue_read` is outside the read-only set
  approved for detached runs, so it was not used). Last verified read
  ~13:11 JST (R83 round): 34 comments, latest ACK `6862732081` (CP5 +
  M-G CP10 + R2, posted 2026-11-14 ~04:24 JST); no new Codex/owner
  direction since Gói 39 (`6815238814`). The GitHub connector's live
  tool catalog no longer advertises `get_pull_request` (it now lists
  `pull_request_read` / `issue_read`, which are outside the connector
  doc's reviewed read-only set for detached runs), so no connector read
  was used this round either.
- Scope audit: R85 block 3 paths / 0 violations; cumulative at the R85
  content commit 2648 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4cfa38` on both sides, re-verified at `48fe92e`).
  Merge-tree at the R85 content head `48fe92e` vs `f3db6b3`: exit 0,
  tree `13d47bc0…`.
- Transient transport note: the first PR-endpoint call returned a
  rate-limit error on the shared egress IP; a retry on a different
  egress IP read clean. The comments endpoint stayed rate-limited on
  both retries. `ls-remote` this round succeeded first try
  (integration `f3db6b3`, media `5f0a468`, both unchanged).

## Next

Posting round (owner tap): PR #119 description refresh to the R85 body
v2 (R83 + R84 paragraphs + new head line are the only new parts vs the
live R78 body). Payload `pr119_update_body_v2_r85.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R85 push (title 764
ký tự, kết thúc "+ R85"; body = body v2 R85 trong repo, head line làm
tươi tới head sau khi R85 push). This run is in-hours (~14:40 JST) so
presentation belongs to the main agent — the owner should tap promptly,
since the approval card lives about 30 minutes; or R86 will supersede
it. The R84 widget is SUPERSEDED — do not tap it. No separate ACK
comment for R85: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
