# MEDIA-02 — PR #119 Body Restructure R87: delivery index + body v2 coverage to `81492b5`

Date: 2026-11-18 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `81492b5` (PR119 BODY RESTRUCTURE R86 report). Content commit: `34e9492`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R87 does

R86 left a disclosed gap: the delivery index covered 361 commits to
`4feb993`; R86's own 2 commits were to fold in at R87. Since then the
R86 body v2 was NOT POSTED — the payload was prepared 2026-11-18
~15:40–16:13 JST and the live body is still R78 (verified fresh this
round, see below). No new Codex/owner direction has landed on issue
#116: this round's fresh read of the comments endpoint (~16:41 JST)
shows still 34 comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2,
2026-11-13T19:24:48Z); no new direction since Gói 39 (`6815238814`).
Note: this is a detached scheduled run (started ~16:40 JST, in-hours
09:00–21:30), so presentation belongs to the main agent — the owner
should tap while still at the machine, since the approval card lives
about 30 minutes. The R86 payload is SUPERSEDED by R87 and must NOT be
tapped.

Fresh derivation at `81492b5` (~16:41 JST): `git rev-list --count
cf17178..81492b5` = 363 commits, `git diff --name-only` = 2653 files,
`--shortstat` = 246098 insertions, 0 deletions. `git merge-tree
--write-tree` `81492b5` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `853ceeccd98bd4f490850fdf7f4c2eadd8a58d4f`. The public API
single-PR endpoint read fresh this round (~16:41 JST): head_sha
`81492b5`, commits 363, changed_files 2653, additions 246098,
deletions 0, mergeable true, mergeable_state clean, body_len 47.708 —
git and the fresh API read agree absolutely, and the live body is
still the posted R78 body (sha256 `4f4e87fb`).

R87 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `81492b5` (363 commits / 2653 files /
  246098 additions; API figures cited are the FRESH API read at
  `81492b5` ~16:41 JST — mergeable true/clean, live body R78; delta
  `4feb993..81492b5`: 5 paths, 283 insertions, 9 deletions); one row
  appended — PR119 BODY RESTRUCTURE R86 (`44c8c34`/`81492b5`), including
  the note that its body v2 was NOT posted (payload prepared, live still
  R78, superseded by R87); issue line re-read fresh this round (34
  comments, latest ACK `6862732081`, no new direction). The index now
  covers every block through `81492b5`; R87's own 2 commits fold in at
  the next index update (R88), disclosed in the index itself.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `81492b5` · 363 · 2653 (with the fresh git derivation at `81492b5`,
  the fresh API read at `81492b5`, and the fresh merge-tree cross-check
  at `81492b5`), plus the R86 paragraph in "Khối mới nhất" and the R87
  note. The stale index reference in "Về bản mô tả này" (head
  `4feb993`) is also fixed to `81492b5`. The live PR description is
  refreshed from this file in the posting round that follows R87 (owner
  tap) — the R78 body v2 already live is the base; only the R85 + R86
  paragraphs + new head line are new.
- **Checker** `check_pr119_restructure_r87_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims. **PASS 17/17**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R87_VALIDATION_20261118.json`).
  First run PASS 17/17 (no amend needed this round). The checker was
  written fresh (not sed-copied from R86) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale `4feb993`/`361`/
  `2650`/`245824` references in the checker — the only `4feb993` hits in
  the index/body are the legitimate delta range `4feb993..81492b5` and
  the R85/R86 historical rows) before the run — the R69 sed-order copy
  defect (mangled full COVER SHA) was avoided by construction.

## Verification

- Merge-tree `81492b5` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `853ceeccd98bd4f490850fdf7f4c2eadd8a58d4f`. Merge-tree at the R87
  content head `34e9492` vs `f3db6b3`: exit 0, tree
  `f1e929c6c80912895b6b5df92308fe4c8a52b4f0`.
- PR API single-PR read: FRESH this round (~16:41 JST): head `81492b5`,
  363 commits, 2653 changed files, 246098 additions, 0 deletions,
  mergeable true, mergeable_state clean, body_len 47.708 (R78 body,
  sha256 `4f4e87fb`). The public API read clean on the first call this
  round — no rate-limit error on either the PR endpoint or the
  comments endpoint.
- Issue #116: RE-READ this round via the public API comments endpoint
  (~16:41 JST): still 34 comments, latest ACK `6862732081` (CP5 +
  M-G CP10 + R2, posted 2026-11-14 ~04:24 JST); no new Codex/owner
  direction since Gói 39 (`6815238814`). The GitHub connector's live
  tool catalog no longer advertises `get_pull_request` / `get_issue`
  (it now lists `pull_request_read` / `issue_read`, which are outside
  the connector doc's reviewed read-only set for detached runs), so no
  connector read was used this round either.
- Scope audit: R87 block 3 paths / 0 violations; cumulative at the R87
  content commit 2654 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4cfa38` on both sides, re-verified at `34e9492`).
  Merge-tree at the R87 content head `34e9492` vs `f3db6b3`: exit 0,
  tree `f1e929c6…`.
- Transient transport note: none this round — `git fetch` and
  `ls-remote` succeeded on the first call (integration `f3db6b3`,
  media `81492b5`, both unchanged), and both public API reads were
  clean on the first call. No figure in this round depends on a
  retried call.

## Next

Posting round (owner tap): PR #119 description refresh to the R87 body
v2 (R85 + R86 paragraphs + new head line are the only new parts vs the
live R78 body). Payload `pr119_update_body_v2_r87.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R87 push (title 764
ký tự, kết thúc "+ R87"; body = body v2 R87 trong repo, head line làm
tươi tới head sau khi R87 push). This run is in-hours (~16:40 JST) so
presentation belongs to the main agent — the owner should tap promptly,
since the approval card lives about 30 minutes; or R88 will supersede
it. The R86 widget is SUPERSEDED — do not tap it. No separate ACK
comment for R87: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
