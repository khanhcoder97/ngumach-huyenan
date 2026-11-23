# MEDIA-02 — PR #119 Body Restructure R207: delivery index + body v2 coverage to `5a1ec4c`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `5a1ec4c` (PR119 BODY RESTRUCTURE R206 report). Content commit: `0db08af`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R207 does

R206 left the disclosed gap: the delivery index covered 601 commits to
`c31c7ec`; R206's own 2 commits were to fold in at R207. The R206 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API read ~21:44 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T11:45:24Z — bumped by the R206 push updating the PR head, body bytes
unchanged). The R206 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read via the MCP read
path (~21:42–21:44 JST, read-only — `issue_read get_comments` pages 1+2 and
`pull_request_read get` via `call-read-tool`, no stall this round, so no
browser fallback was needed): issue #116 34 comments, PR #119 head
`5a1ec4c`, 603 commits / 3013 files / +287,162, mergeable_state clean at
`5a1ec4c`, live body R140 92.520 ký tự sha `ddbe32ff`. Note: the API
`mergeable` field itself returned null at read time — mergeable_state
clean is the operative field (see Verification).

Fresh derivation at `5a1ec4c` (~21:40 JST): `git rev-list --count
cf17178..5a1ec4c` = 603 commits, `git diff --name-only` = 3013 files,
`--shortstat` = 287162 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `5a1ec4c` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `53c5035a…`. No re-fetch was needed before applying: the run fetched at ~21:40 JST
(the run start) and the remote head was still `5a1ec4c`, integration still `f3db6b3` — no
intervening push; the API read ~21:44 JST independently confirmed head `5a1ec4c`.

R207 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `5a1ec4c` (603 commits / 3013 files /
  287162 additions; the fresh git derivation at `5a1ec4c`, the fresh API
  read ~21:44 JST, and the merge-tree cross-check at `5a1ec4c` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `c31c7ec..5a1ec4c`: 5 paths, 552 insertions, 10
  deletions); one row appended — PR119 BODY RESTRUCTURE R206
  (`004cf47`/`5a1ec4c`), recording that its payload was prepared after
  push ~20:47 JST (104.907 ký tự, sha `7a64adf1`; JSON 121.442 byte < trần 131.072 — còn 9.630 byte, bản giữ tại
  `.bak-prepost-20261123` — thư mục tồn tại, bản R206 lưu tại đó,
  byte-identical với `pr_comments/` — sha256 `9bca5752…` cả hai, kiểm chứng lại lượt R206),
  that it was NOT posted
  — live body still R140 (verified by this round's API read: description
  structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này, 0 U+FFFD, updated_at 2026-11-23T11:45:24Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~21:44 JST).
  The index now covers every block through `5a1ec4c`; R207's
  own 2 commits fold in at the next index update (R208), disclosed in the
  index itself. The R207 note was appended after the R206 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `5a1ec4c` · 603 · 3013 (with the fresh git derivation at `5a1ec4c`,
  the fresh API read ~21:44 JST, and the fresh merge-tree cross-check at
  `5a1ec4c`), plus the R206 paragraph in "Khối mới nhất" (320 ký tự,
  marked chưa đăng — live body is R140) and the R207 note. The stale index
  reference in "Về bản mô tả này" (head `c31c7ec`) is also fixed to
  `5a1ec4c`, and the title line is extended to R206 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R206 warning —
  applied with a measured correction): the R99 paragraph (570 ký tự — measured this
  round) is
  collapsed to one 237-ký-tự compact line (full detail stays in the
  delivery index) — the new R206 paragraph was 320 ký tự, so
  the body is 104.977 ký tự — net +50 vs R206 despite the new R206
  paragraph, headroom 23 ký tự. The dry-run first projected 105.007 ký tự
  (7 over the 105.000 ceiling) with the R206 paragraph at 350 ký tự; the
  paragraph was tightened by 30 ký tự (dropping the mergeable clause already
  carried by the head line) before any write — measure, then trim, then apply.
  Paragraph order: the R206 paragraph sits directly after R205
  (ascending full-paragraph order R166..R206), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R207 (owner tap) — the R140 body v2 now live
  is the base; only the R206 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r207_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R206 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R206 and R207 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R206 (67 compact lines R99–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.977 ký tự),
  a check that the R206 paragraph sits directly after R205
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R206 note clean).
  New this round: the R205-row regression guard (cumulative must be 3011,
  see Đính chính R206 below), the body "Ghi chú" line correction guard
  (R158/R206, range R99–R165, list complete through R206, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 30/30**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R207_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R206) with the full COVER
  SHA verified intact (definition + docstring, both
  `5a1ec4c929abc91289f00e8d738474a96ff3e0ea` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `c31c7ec` references in the checker — the one `c31c7ec` hit is the
  docstring explaining the R205-row derivation, intentional — the R206 cover value)
  before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 105.007 ký tự and the apply wrote on
  the first attempt at 104.977 ký tự with 23 ký tự of headroom after the
  paragraph was tightened (see above); the idempotency re-run
  after apply initially CRASHED on its OLD-state pre-condition assert
  (body head-line replace — R203 lesson recurring) and
  was FIXED this round: the script now checks the NEW state first, and
  the re-run after the fix reported already-applied changed: 0 — verified.
  Correction caught before the report commit (see Lesson 2 below): the
  R206 row's cumulative figure was drafted as 3014 (3013 at
  `5a1ec4c` + 1 new checker) and the true diff at the R207 content
  commit is 3014 — verified by `git diff --name-only cf17178..0db08af` = 3014
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).

## R207 robustness note — headroom now 23 chars

The R206 warning left 73 ký tự of headroom, so this round compacted
the R99 paragraph (570 ký tự → 237) before adding the new R206 paragraph
(320 ký tự). The body is now 104.977 ký tự — net +50 vs R206 — with
23 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R208 warning: headroom is 23 ký tự; the next round must collapse R98
(609 ký tự → ~240) and keep the new paragraph tight (≤ ~330 ký tự) — the
R98 compaction alone frees ~370 ký tự, restoring comfortable headroom.
At the current net +50/round the margin holds with compaction; one full-paragraph compaction per round (~−370) keeps
the discipline sustainable (full paragraphs remaining R166..R206 = 41;
compact block R99–R165 = 67 lines).
ĐÍNH CHÍNH R206 (carried here as R206 instructed — with a correction to
what R206 claimed): the R206 report stated the R205 row's cumulative was
"fixed to 3011 and verified by git before the report commit" — that is
NOT what the committed index shows. The committed index at `5a1ec4c`
still cites 3009 for the R205 row; the 3011 fix existed only as an
uncommitted working-tree edit when this round started (the R206 report
commit staged only its 2 new files and never picked the edit up). The
R206 checker's own docstring carried the same wrong derivation
("therefore cites 3009 paths: 3008 at df30756 + 1 new checker") — it
forgot the 2 R205 report files that landed in coverage head `c31c7ec`.
R207 folds the fix into its content commit (diff `cf17178..0db08af` =
3014 confirms the R206 row; the R205 row now reads 3011, guarded by the
new checker check). No content was lost — the fix was a 1-line numeric
correction, now committed.
Lesson this round: (1) the dry-run projection caught a 7-char ceiling
overrun BEFORE any write (105.007 projected; paragraph tightened to 320
chars, apply wrote 104.977 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206 — recurred in the R206 docstring, fixed here with the
checker guard). (3) An edit script's idempotency re-run must check the NEW state first, not only
assert the OLD state — otherwise the re-run crashes on its own
pre-condition after a successful apply (R203 lesson — recurred this
round on the body head line, FIXED: re-run reports already-applied
changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked).

## Verification

- Merge-tree `5a1ec4c` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `53c5035a…`. Merge-tree at the R207
  content head `0db08af` vs `f3db6b3`: exit 0, tree
  `f786e351…`.
- Live PR state: API read via MCP ~21:44 JST (read path
  healthy — `call-read-tool` accepted `issue_read`/`pull_request_read`
  this round) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `5a1ec4c`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T11:45:24Z — bumped by the R206 push updating the PR head, body
  bytes unchanged); commits 603, changed_files 3013, additions 287162
  (API agrees with the fresh git derivation; the `deletions` key is absent
  in this API response — git shows 0 deletions; the raw API payload also
  returns `mergeable: null` — mergeable_state clean is the operative
  field); mergeable_state clean at
  `5a1ec4c` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R207 block (`5a1ec4c..0db08af`) 3 paths / 0 violations
  (index + body v2 + R207 checker); cumulative at the R207 content
  commit `0db08af` 3014 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `0db08af`).
  Merge-tree at the R207 content head `0db08af` vs `f3db6b3`: exit 0,
  tree `f786e351…`.
- Transient notes: this round's `git fetch` at ~21:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round.
  The R206 payload's own head line recorded
  mergeable clean at `c31c7ec` at its preparation and clean at
  `5a1ec4c`; this round's API read confirms clean at `5a1ec4c`.
- Ceiling discipline: the R206 payload JSON measured 121.442 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.630 byte headroom). The projected R207 payload JSON is ~121,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.977
  ký tự (< 105.000) — 23 ký tự of headroom. R207 warning:
  headroom is now 23 ký tự; the next round must collapse R98 (609 ký tự
  → ~240) and keep the new paragraph tight (≤ ~330 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R207 body
v2 (R206 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r207.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R207 push (title
ending "+ R207", built by replacing the "+ R140" suffix — not appending;
body = body v2 R207 in repo, head line refreshed to head after R207 push).
This run started ~21:40 JST — AFTER working hours (09:00–21:30 JST), so the
R207 payload is HELD FOR WORKING HOURS (not presented tonight, like R142/R164–R197). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R206 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205 and R206 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R207: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
