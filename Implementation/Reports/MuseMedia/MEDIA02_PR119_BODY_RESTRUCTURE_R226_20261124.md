# MEDIA-02 — PR #119 Body Restructure R226: delivery index + body v2 coverage to `2861100`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `2861100` (PR119 BODY RESTRUCTURE R225 report). Content commit: `8a5f422`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R226 does

R225 left the disclosed gap: the delivery index covered 639 commits to
`1700859`; R225's own 2 commits were to fold in at R226. The R225 payload
was prepared after the R225 push ~18:47 JST
(`pr119_update_body_v2_r225.json`, body 102.404 ký tự, sha `a5a4100d`,
JSON 117.377 byte < trần 131.072 — còn 13.695 byte, bản giữ tại
`.bak-prepost-20261124` — sha256 `63a794fe…`, main + .bak byte-identical,
verified this round) but was NOT posted: the live PR body is still R222
(this round's fresh connector read ~19:43 JST, `pull_request_read`: title
ends "+ R222", head `2861100`, 641 commits / 3070 files / +301726,
mergeable null — GitHub computing at read time — / mergeable_state clean,
live body 103.023 ký tự, sha `1dd61afd`, 0 U+FFFD, updated_at
2026-11-24T09:46:45Z — changed vs the R225 read because the R225 push
updated the head; the body bytes are unchanged).
R222 was posted live 2026-11-24 ~16:16 JST, replacing R140. No new
Codex/owner direction has been verified on issue #116: the comments read
SUCCEEDED this round (connector `issue_read` ~19:43 JST, paginated 30 + 4:
still 34 comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081`
(CP5 + M-G CP10 + R2); no new direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API PR read succeeded via the
connector (`pull_request_read`, ~19:43 JST, read-only — the `gh` CLI is
unauthenticated in this shell, so no direct curl read was available;
the connector is the sanctioned read path and returned the full PR
object). The issue read also succeeded via the connector (`issue_read`
method `get_comments` with `issue_number` — the first attempt at
`pull_request_read` used `pull_number` and the MCP rejected it as a
missing required parameter `pullNumber`; the retry with the correct name
succeeded — a wrong parameter name is not a failed read; the issue read
came back paginated at 30 comments per page, so a second call with
`page: 2` returned the remaining 4). Both read paths clean. PR head
`2861100`, 641 commits / 3070 files / +301726 at the current head
`2861100` (the `deletions` key is absent in the connector
response — git shows 0 deletions); mergeable_state clean at `2861100`
(mergeable null in this read — GitHub computing — the honest wording is
state clean, not a repeated true/clean claim).

Fresh derivation at `2861100` (~19:43 JST): `git rev-list --count
cf17178..2861100` = 641 commits, `git diff --name-only` = 3070 files,
`--shortstat` = 301726 insertions, 0 deletions — agreeing exactly with
the connector PR read. `git merge-tree --write-tree` `2861100` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `27f3d2db…`. No re-fetch
was needed before applying: the run fetched at ~19:40 JST (the run start)
and the remote head was still `2861100`, integration still `f3db6b3` — no
intervening push; the connector read ~19:43 JST independently confirmed
head `2861100`.

R226 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `2861100` (641 commits / 3070 files /
  301726 additions; the fresh git derivation at `2861100`, the fresh
  connector PR read ~19:43 JST, and the merge-tree cross-check at
  `2861100` are cited, with the honest live-read disclosure above —
  connector PR read clean, issue read SUCCEEDED this round (34 comments,
  latest ACK `6862732081`, no new direction); live body R222 (posted
  ~16:16 JST, read back byte-exact this round); delta `1700859..2861100`:
  5 paths, 958 insertions, 12 deletions); one row appended — PR119 BODY
  RESTRUCTURE R225 (`8678714`/`2861100`), recording that its payload was
  prepared after push ~18:47 JST (102.404 ký tự, sha `a5a4100d`; JSON
  117.377 byte < trần 131.072 — còn 13.695 byte, bản giữ tại
  `.bak-prepost-20261124` — sha256 `63a794fe…`, main + .bak byte-identical)
  and then NOT posted (live body still R222 as read this round ~19:43 JST);
  no separate ACK for R225. The index now covers every block through
  `2861100`; R226's own 2 commits fold in at the next index update
  (R227), disclosed in the index itself. The R226 note was appended after
  the R225 note line (not replacing it — the R140 replace-instead-of-append
  defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `2861100` · 641 · 3070 (with the fresh git derivation at `2861100`,
  the fresh connector PR read ~19:43 JST, and the fresh merge-tree
  cross-check at `2861100`), plus the R225 paragraph in "Khối mới nhất"
  (271 ký tự, marked chưa đăng — payload prepared ~18:47 JST, live body
  still R222) and the R226 note. The stale index reference in "Về bản mô tả này"
  (head `1700859`) is also fixed to `2861100`, and the title line is
  extended to R225 (APPENDED, not replaced — see the R176 robustness
  note). Compaction (R225 warning — applied with a measured correction,
  DOUBLE): the R69 + R68 paragraphs (487 and 487 ký tự — measured this
  round) are collapsed to one 207-ký-tự compact line each (full detail
  stays in the delivery index; the R76–R80 template measures 208, the
  R69/R68 lines measure 207 — the checker asserts < 400, not an exact
  208) — the new R225 paragraph was 271 ký tự, so the body is 102.179
  ký tự — net −216 vs R225 despite the new R225 paragraph, headroom
  2.821 ký tự. The dry-run first projected 102.179 ký tự and the apply
  wrote exactly that on the first attempt — measure, then trim, then
  apply. The head line stayed 1.024 ký tự (every substituted value kept
  its digit length, and the updated_at move cost no extra chars).
  Paragraph order: the R225 paragraph sits directly after R224
  (ascending full-paragraph order R166..R225), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R226 (owner tap) — the R222 body v2 now live is the base;
  only the R225 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r226_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R225 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R225 and R226 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R225 (98 compact lines R68–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 102.179 ký tự),
  a check that the R225 paragraph sits directly after R224
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R225 note clean).
  New this round: the R224-row guard (cumulative must be 3068,
  re-derived from git at `8678714`), the R225-row guard (cumulative must
  cite 3071 — 3070 at `2861100` + 1 new checker in the R226 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R226, range R69–R165, list complete through R225, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 69/69**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R226_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R225) with the full COVER
  SHA verified intact (definition + docstring, both
  `2861100aeaa94e96c5bf1b1a0e4fc0d2b99ce3a6` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (4 stale
  `1700859` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R224-row guard string citing "3067 at 1700859", legitimate; plus 4
  `e07fe1e` (docstring + R223-row guard citing "3064 at e07fe1e"), 4 `37ea7ad` (docstring + R222-row guard citing "3061 at 37ea7ad"), 3
  `a38b714` (docstring + R221-row guard citing "3058 at a38b714"), 3 `c38a4dc` (docstring + R220-row guard citing "3055 at c38a4dc"), 3 `8f8b504` (docstring + R219-row guard citing "3052 at 8f8b504"), 3 `a74e9f4` (docstring + R218-row guard citing "3049 at a74e9f4"), 3 `0a4d05a` (docstring + R217-row guard citing "3046 at 0a4d05a"), 3 `0de54fb` (docstring + R216-row guard citing "3043 at 0de54fb"), 3 `1e564a2` (docstring + R215-row guard citing "3040 at 1e564a2"), 3 `3de99c9` (docstring + R214-row guard citing "3037 at 3de99c9"), legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 102.179 ký tự and the apply wrote on
  the first attempt at 102.179 ký tự with 2.821 ký tự of headroom; the idempotency re-run
  after apply reports already-applied changed: 0 — verified (after one script fix, see the lesson below).
  Correction caught before the report commit: the R225 row's cumulative figure was drafted as 3071 (3070 at
  `2861100` + 1 new checker) and the true diff at the R226 content
  commit is 3071 — verified by `git diff --name-only cf17178..8a5f422` = 3071
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R225's committed content this round: R225's committed content verified correct —
  the committed index at `2861100` carries the R223 row at cumulative 3065
  (re-derived by the new checker from git at `e14c586`) and the R224 row at 3068
  (re-derived from git at `8678714`); no uncommitted
  working-tree fix was left behind by R225 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R226 robustness note — headroom now 2.821 chars

The R225 warning left 2.605 ký tự of headroom, so this round compacted
TWO paragraphs (R69 + R68, 487 + 487 ký tự → 207 each) before adding the new R225 paragraph
(271 ký tự). The body is now 102.179 ký tự — net −216 vs R225 — with
2.821 ký tự of headroom. The double compaction bought back 560 ký tự against the
271-ký-tự new paragraph, and the head line stayed 1.024 ký tự (every substituted value kept
its digit length), so the net recovery is −216. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R227 warning: headroom is 2.821 ký tự; compact R67 + R66 next (or the head line
grows again if a future round's reads hit the rate-limit — the honest disclosure
is the variable cost, not the compaction).
At the current net −216/round the margin is recovering well,
but only while the double compaction continues (full paragraphs remaining R166..R225 = 60;
compact block R68–R165 = 98 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (102.179 projected; apply wrote 102.179 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225 — the R225 row's 3071 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — this round the first re-run CRASHED on the head-line edit because its predicate matched only the
old "**Head: `1700859`" text (StopIteration: the old line no longer existed after apply); fixed by checking
`NEW_HEAD in lines` first — the re-run then reports already-applied changed: 0, verified (R203/R207 lesson, now applied to all edits — the same class of defect as R207's, caught by the re-run itself, not by a failed commit; the first apply had already written the files correctly, so no content was lost or duplicated).
(4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two backup locations can hold
different versions of the same payload — the R225 payload's main file and its `.bak-prepost-20261124/` copy
were verified byte-identical this round (sha256 `63a794fe…`, 117.377 byte) before the R225 row recorded it;
a payload backup the authoring round made must be verified, not re-claimed — R226 verified the R225 payload's
body sha (`a5a4100d`) against the repo body v2 + head-line refresh (102.404 ký tự) and recorded it as prepared
but NOT posted, since the live body read this round is still R222.
(6) An `updated_at` that DOES move while the body sha stays means a push updated the head only — the PR read this round
shows updated_at 2026-11-24T09:46:45Z, changed from the R225 read's 08:45:20Z, while the body sha is unchanged
(`1dd61afd` = R222); the head line says so explicitly instead of implying a body refresh.
(7) No execution-risk flag appeared on any git/script command this round
(unlike R211/R213 and the R219-blocked run ~11:40 JST); the flag itself has now appeared 4 times
(R211 ~01:40, R213 ~04:40, R213 ~05:44, R219 ~11:40) and the decision whether to keep running git/checker after it still awaits
luồng chính/chủ dự án — recorded here, not decided here.
(8) A connector call that fails on a wrong parameter name is not a failed read — this round's first
`pull_request_read` used `pull_number` and the MCP rejected it (missing required parameter `pullNumber`); the retry
with the correct name succeeded and returned the full PR object. Record the parameter name in the report;
do not treat the first failure as missing direction, and do not fall back to unauthenticated curl.
(9) `issue_read` `get_comments` is paginated at 30 comments per page — this round the first call returned
30 comments (through `6819808977`) and page 2 returned the remaining 4 (through `6862732081`), total 34; a
single-page read is not the full issue, and the latest comment lives on the last page.

## Verification

- Merge-tree `2861100` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `27f3d2db…`. Merge-tree at the R226
  content head `8a5f422` vs `f3db6b3`: exit 0,
  tree `a15b74cf…`.
- Live PR state: connector read this round (~19:43 JST) — direct read
  clean byte-exact (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD, mergeable_state clean, mergeable null — GitHub computing) — PR title ends
  "+ R222" (R222 posted live ~16:16 JST 2026-11-24); head `2861100`; live body
  R222 by structure (description head `37ea7ad` · 635 · 3061, tail lines match)
  and byte-exact body read (103.023 ký tự, sha `1dd61afd`,
  0 U+FFFD, updated_at 2026-11-24T09:46:45Z — changed vs the R225 read, body
  bytes unchanged); commits 641, changed_files 3070, additions 301726
  (connector agrees with the fresh git derivation; the `deletions` key is absent in
  the connector response — git shows 0 deletions); mergeable_state clean at
  `2861100` (connector read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: comments read SUCCEEDED this round — connector `issue_read` ~19:43 JST (paginated 30 + 4): still 34
  comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081` (CP5 + M-G CP10 + R2); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R226 block (`2861100..8a5f422`) 3 paths / 0 violations
  (index + body v2 + R226 checker); cumulative at the R226 content
  commit `8a5f422` 3071 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `8a5f422`). Merge-tree at the R226 content head `8a5f422` vs `f3db6b3`: exit 0,
  tree `a15b74cf…`.
- Transient notes: this round's `git fetch` at ~19:40 JST succeeded
  first try. The connector read path was used this round — both reads
  succeeded (PR + issue, after one parameter-name retry on `pull_request_read` and pagination on `issue_read`). No call-tool write approval was requested for a read. No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST). No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH; the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
- Ceiling discipline: the R225 payload JSON as-prepared measured 117.377 byte
  (prepared ~18:47 JST, NOT posted — live body is still R222, verified by this round's connector read),
  vs the 131.072-byte transport ceiling
  (13.695 byte headroom). The projected R226 payload JSON is ~117,300 byte
  (measured exactly at payload build, after push). Body v2 is now 102.179
  ký tự (< 105.000) — 2.821 ký tự of headroom. R226 warning:
  headroom is now 2.821 ký tự; the double compaction must continue next round
  (R67 + R66) or the head line must be trimmed if a future round's reads hit the rate-limit again.

## Next

Posting round (owner tap): PR #119 description refresh to the R226 body
v2 (R225 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r226.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R226 push (title
ending "+ R226", built by replacing the "+ R222" suffix — not appending;
body = body v2 R226 in repo, head line refreshed to head after R226 push).
This run started ~19:40 JST — INSIDE working hours (09:00–21:30 JST), so the
R226 payload is READY FOR WORKING HOURS (unlike R142/R164–R197/R207–R216,
which were held because they started before 09:00). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R225 payload as new — R225 was prepared but never posted and is superseded by R226; do not present the R222 payload as new — R222 is LIVE; do not present either R221 widget (`widget-56770776`, `widget-7a108c57`) — R221 was never posted and both are stale. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220, R221, R222, R223, R224 and R225 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R226: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
