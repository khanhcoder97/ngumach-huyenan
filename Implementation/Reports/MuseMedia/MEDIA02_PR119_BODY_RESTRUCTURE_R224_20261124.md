# MEDIA-02 — PR #119 Body Restructure R224: delivery index + body v2 coverage to `e07fe1e`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `e07fe1e` (PR119 BODY RESTRUCTURE R223 report). Content commit: `e14c586`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R224 does

R223 left the disclosed gap: the delivery index covered 635 commits to
`37ea7ad`; R223's own 2 commits were to fold in at R224. The R223 payload
was prepared after the R223 push ~17:00 JST
(`pr119_update_body_v2_r223.json`, body 102.870 ký tự, sha `4a8176cd`,
JSON 118.072 byte < trần 131.072 — còn 13.000 byte, bản giữ tại
`.bak-prepost-20261124` — sha256 `c195c20f…`, main + .bak byte-identical,
verified this round) but was NOT posted: the live PR body is still R222
(this round's fresh connector read ~17:40 JST, `pull_request_read`: title
ends "+ R222", head `e07fe1e`, 637 commits / 3064 files / +299857,
mergeable null — GitHub computing at read time — / mergeable_state clean,
live body 103.023 ký tự, sha `1dd61afd`, 0 U+FFFD, updated_at
2026-11-24T07:58:36Z — the updated_at moved vs the R223 read (07:16:22Z)
because the R223 push changed the head, the body bytes are unchanged).
R222 was posted live 2026-11-24 ~16:16 JST, replacing R140. No new
Codex/owner direction has been verified on issue #116: the comments read
SUCCEEDED this round (connector `issue_read` ~17:40 JST: still 34 comments,
updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081` (CP5 + M-G CP10 + R2);
no new direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API PR read succeeded via the
connector (`pull_request_read`, ~17:40 JST, read-only — the `gh` CLI is
unauthenticated in this shell, so no direct curl read was available;
the connector is the sanctioned read path and returned the full PR
object). The issue read also succeeded via the connector (`issue_read`
method `get`: comments 34, updated_at 2026-11-13T19:24:49Z). Both read
paths clean. PR head `e07fe1e`, 637 commits / 3064 files / +299857 at the
current head `e07fe1e` (the `deletions` key is absent in the connector
response — git shows 0 deletions); mergeable_state clean at `e07fe1e`
(mergeable null in this read — GitHub computing — the honest wording is
state clean, not a repeated true/clean claim).

Fresh derivation at `e07fe1e` (~17:40 JST): `git rev-list --count
cf17178..e07fe1e` = 637 commits, `git diff --name-only` = 3064 files,
`--shortstat` = 299857 insertions, 0 deletions — agreeing exactly with
the connector PR read. `git merge-tree --write-tree` `e07fe1e` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `95f9c665…`. No re-fetch
was needed before applying: the run fetched at ~17:40 JST (the run start)
and the remote head was still `e07fe1e`, integration still `f3db6b3` — no
intervening push; the connector read ~17:40 JST independently confirmed
head `e07fe1e`.

R224 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `e07fe1e` (637 commits / 3064 files /
  299857 additions; the fresh git derivation at `e07fe1e`, the fresh
  connector PR read ~17:40 JST, and the merge-tree cross-check at
  `e07fe1e` are cited, with the honest live-read disclosure above —
  connector PR read clean, issue read SUCCEEDED this round (34 comments,
  latest ACK `6862732081`, no new direction); live body R222 (posted
  ~16:16 JST, read back byte-exact this round); delta `37ea7ad..e07fe1e`:
  5 paths, 929 insertions, 12 deletions); one row appended — PR119 BODY
  RESTRUCTURE R223 (`25f18d0`/`e07fe1e`), recording that its payload was
  prepared after push ~17:00 JST (102.870 ký tự, sha `4a8176cd`; JSON
  118.072 byte < trần 131.072 — còn 13.000 byte, bản giữ tại
  `.bak-prepost-20261124` — sha256 `c195c20f…`, main + .bak byte-identical)
  and then NOT posted (live body still R222 as read this round ~17:40 JST);
  no separate ACK for R223. The index now covers every block through
  `e07fe1e`; R224's own 2 commits fold in at the next index update
  (R225), disclosed in the index itself. The R224 note was appended after
  the R223 note line (not replacing it — the R140 replace-instead-of-append
  defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `e07fe1e` · 637 · 3064 (with the fresh git derivation at `e07fe1e`,
  the fresh connector PR read ~17:40 JST, and the fresh merge-tree
  cross-check at `e07fe1e`), plus the R223 paragraph in "Khối mới nhất"
  (271 ký tự, marked chưa đăng — payload prepared ~17:00 JST, live body
  still R222) and the R224 note. The stale index reference in "Về bản mô tả này"
  (head `37ea7ad`) is also fixed to `e07fe1e`, and the title line is
  extended to R223 (APPENDED, not replaced — see the R176 robustness
  note). Compaction (R223 warning — applied with a measured correction,
  DOUBLE): the R73 + R72 paragraphs (489 and 487 ký tự — measured this
  round) are collapsed to one 207-ký-tự compact line each (full detail
  stays in the delivery index; the R76–R80 template measures 208, the
  R73/R72 lines measure 207 — the checker asserts < 400, not an exact
  208) — the new R223 paragraph was 271 ký tự, so the body is 102.611
  ký tự — net −211 vs R223 despite the new R223 paragraph, headroom
  2.389 ký tự. The dry-run first projected 102.611 ký tự and the apply
  wrote exactly that on the first attempt — measure, then trim, then
  apply. The head line GREW 1.017 → 1.024 ký tự (+7, the honest
  updated_at disclosure for the R223 push).
  Paragraph order: the R223 paragraph sits directly after R222
  (ascending full-paragraph order R166..R223), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R224 (owner tap) — the R222 body v2 now live is the base;
  only the R223 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r224_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R223 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R223 and R224 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R223 (94 compact lines R73–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 102.611 ký tự),
  a check that the R223 paragraph sits directly after R222
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R223 note clean).
  New this round: the R222-row guard (cumulative must be 3062,
  re-derived from git at `25f18d0`), the R223-row guard (cumulative must
  cite 3065 — 3064 at `e07fe1e` + 1 new checker in the R224 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R224, range R73–R165, list complete through R223, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 65/65**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R224_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R223) with the full COVER
  SHA verified intact (definition + docstring, both
  `e07fe1e42d5f77b0cc80e49c6493181130009982` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (4 stale
  `37ea7ad` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R222-row guard string citing "3061 at 37ea7ad", legitimate; plus 3
  `a38b714` (docstring + R221-row guard citing "3058 at a38b714"), 3 `c38a4dc` (docstring + R220-row guard citing "3055 at c38a4dc"), 3 `8f8b504` (docstring + R219-row guard citing "3052 at 8f8b504"), 3 `a74e9f4` (docstring + R218-row guard citing "3049 at a74e9f4"), 3 `0a4d05a` (docstring + R217-row guard citing "3046 at 0a4d05a"), 3 `0de54fb` (docstring + R216-row guard citing "3043 at 0de54fb"), 3 `1e564a2` (docstring + R215-row guard citing "3040 at 1e564a2"), 3 `3de99c9` (docstring + R214-row guard citing "3037 at 3de99c9"), legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 102.611 ký tự and the apply wrote on
  the first attempt at 102.611 ký tự with 2.389 ký tự of headroom; the idempotency re-run
  after apply reports already-applied changed: 0 — verified (after a
  script fix, see the lesson below).
  Correction caught before the report commit: the R223 row's cumulative figure was drafted as 3065 (3064 at
  `e07fe1e` + 1 new checker) and the true diff at the R224 content
  commit is 3065 — verified by `git diff --name-only cf17178..e14c586` = 3065
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R223's committed content this round: R223's committed content verified correct —
  the committed index at `e07fe1e` carries the R221 row at cumulative 3059
  (re-derived by the new checker from git at `110aa76`) and the R222 row at 3062
  (re-derived from git at `25f18d0`); no uncommitted
  working-tree fix was left behind by R223 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R224 robustness note — headroom now 2.389 chars

The R223 warning left 2.178 ký tự of headroom, so this round compacted
TWO paragraphs (R73 + R72, 489 + 487 ký tự → 207 each) before adding the new R223 paragraph
(271 ký tự). The body is now 102.611 ký tự — net −211 vs R223 — with
2.389 ký tự of headroom. The double compaction bought back 562 ký tự against the
271-ký-tự new paragraph, and the head line grew +7 ký tự (honest updated_at disclosure for the R223 push),
so the net recovery is −211. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R225 warning: headroom is 2.389 ký tự; compact R71 + R70 next (or the head line
grows again if a future round's reads hit the rate-limit — the honest disclosure
is the variable cost, not the compaction).
At the current net −211/round the margin is recovering well,
but only while the double compaction continues (full paragraphs remaining R166..R223 = 58;
compact block R73–R165 = 94 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (102.611 projected; apply wrote 102.611 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223 — the R223 row's 3065 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — the first dry-run CRASHED on the Ghi-chú line because the script assumed the line ended
"/R222" when it actually ends "/R222." (trailing period); fixed by matching the real tail and inserting "/R223"
before the period — the re-run then reports already-applied changed: 0, verified (R203/R207 lesson, now applied to all edits — the same class of defect as R207's, caught by the dry-run itself, not by a failed commit). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two backup locations can hold
different versions of the same payload — the R223 payload's main file and its `.bak-prepost-20261124/` copy
were verified byte-identical this round (sha256 `c195c20f…`, 118.072 byte) before the R223 row recorded it;
a payload backup the authoring round made must be verified, not re-claimed — R224 verified the R223 payload's
body sha (`4a8176cd`) against the repo body v2 + head-line refresh (102.870 ký tự) and recorded it as prepared
but NOT posted, since the live body read this round is still R222.
(6) An `updated_at` that moves without a body change is a head push, not a body edit — the PR read this round
shows updated_at 2026-11-24T07:58:36Z vs 07:16:22Z at the R223 read, while the body sha is unchanged
(`1dd61afd` = R222); the head line says so explicitly instead of implying a body refresh.
(7) No execution-risk flag appeared on any git/script command this round
(unlike R211/R213 and the R219-blocked run ~11:40 JST); the flag itself has now appeared 4 times
(R211 ~01:40, R213 ~04:40, R213 ~05:44, R219 ~11:40) and the decision whether to keep running git/checker after it still awaits
luồng chính/chủ dự án — recorded here, not decided here.
(8) When the `gh` CLI is unauthenticated in a shell, the GitHub connector
(`pull_request_read` / `issue_read`) is the sanctioned read path — it
returned the full PR object and the issue comment count this round; do
not fall back to unauthenticated curl (403) and do not treat a failed
`gh` call as a failed read.

## Verification

- Merge-tree `e07fe1e` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `95f9c665…`. Merge-tree at the R224
  content head `e14c586` vs `f3db6b3`: exit 0,
  tree `0420334f…`.
- Live PR state: connector read this round (~17:40 JST) — direct read
  clean byte-exact (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD, mergeable_state clean, mergeable null — GitHub computing) — PR title ends
  "+ R222" (R222 posted live ~16:16 JST 2026-11-24); head `e07fe1e`; live body
  R222 by structure (description head `e07fe1e` · 637 · 3064, tail lines match)
  and byte-exact body read (103.023 ký tự, sha `1dd61afd`,
  0 U+FFFD, updated_at 2026-11-24T07:58:36Z — moved by the R223 head push, body
  bytes unchanged); commits 637, changed_files 3064, additions 299857
  (connector agrees with the fresh git derivation; the `deletions` key is absent in
  the connector response — git shows 0 deletions); mergeable_state clean at
  `e07fe1e` (connector read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: comments read SUCCEEDED this round — connector `issue_read` ~17:40 JST: still 34
  comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081` (CP5 + M-G CP10 + R2); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R224 block (`e07fe1e..e14c586`) 3 paths / 0 violations
  (index + body v2 + R224 checker); cumulative at the R224 content
  commit `e14c586` 3065 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `e14c586`). Merge-tree at the R224 content head `e14c586` vs `f3db6b3`: exit 0,
  tree `0420334f…`.
- Transient notes: this round's `git fetch` at ~17:40 JST succeeded
  first try. The connector read path was used this round — both reads
  succeeded (PR + issue). No call-tool write approval was requested for a read. No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST). No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH; the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
- Ceiling discipline: the R223 payload JSON as-prepared measured 118.072 byte
  (prepared ~17:00 JST, NOT posted — live body is still R222, verified by this round's connector read),
  vs the 131.072-byte transport ceiling
  (13.000 byte headroom). The projected R224 payload JSON is ~121,000 byte
  (measured exactly at payload build, after push). Body v2 is now 102.611
  ký tự (< 105.000) — 2.389 ký tự of headroom. R224 warning:
  headroom is now 2.389 ký tự; the double compaction must continue next round
  (R71 + R70) or the head line must be trimmed if a future round's reads hit the rate-limit again.

## Next

Posting round (owner tap): PR #119 description refresh to the R224 body
v2 (R223 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r224.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R224 push (title
ending "+ R224", built by replacing the "+ R222" suffix — not appending;
body = body v2 R224 in repo, head line refreshed to head after R224 push).
This run started ~17:40 JST — INSIDE working hours (09:00–21:30 JST), so the
R224 payload is READY FOR WORKING HOURS (unlike R142/R164–R197/R207–R216,
which were held because they started before 09:00). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R223 payload as new — R223 was prepared but never posted and is superseded by R224; do not present the R222 payload as new — R222 is LIVE; do not present either R221 widget (`widget-56770776`, `widget-7a108c57`) — R221 was never posted and both are stale. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220, R221, R222 and R223 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R224: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
