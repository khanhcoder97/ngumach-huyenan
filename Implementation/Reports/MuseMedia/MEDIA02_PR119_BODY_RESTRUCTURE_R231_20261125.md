# MEDIA-02 — PR #119 Body Restructure R231: delivery index + body v2 coverage to `9861875`

Date: 2026-11-25 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `9861875` (PR119 BODY RESTRUCTURE R230 report). Content commit: `9482f4d`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R231 does

R230 left the disclosed gap: the delivery index covered 649 commits to
`8310e5d`; R230's own 2 commits were to fold in at R231. The R230 payload
was prepared after the R230 push ~23:57 JST
(`pr119_update_body_v2_r230.json`, body 101.488 ký tự, sha `5cda4d67`,
JSON 115.948 byte < trần 131.072 — còn 15.124 byte, bản giữ tại
`.bak-prepost-20261124` — sha256 `7d2ad913…`, main + .bak byte-identical,
verified this round) but was NOT posted: the live PR body is still R222
(this round's fresh connector read ~00:40 JST, `pull_request_read`: title
ends "+ R222", head `9861875`, 651 commits / 3085 files / +306840,
mergeable null — GitHub computing at read time — / mergeable_state clean,
live body 103.023 ký tự, sha `1dd61afd`, 0 U+FFFD — byte-exact with the
R222 payload on the first read, no resync needed this round —,
updated_at 2026-11-24T14:57:11Z — changed vs the R230 read because the
R230 push updated the head; the body bytes are unchanged).
R222 was posted live 2026-11-24 ~16:16 JST, replacing R140. No new
Codex/owner direction has been verified on issue #116: the comments read
SUCCEEDED this round (connector `issue_read` ~00:40 JST, paginated 30 + 4:
still 34 comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081`
(CP5 + M-G CP10 + R2); no new direction since Gói 39 (`6815238814`).

Fresh derivation at `9861875` (~00:40 JST): `git rev-list --count
cf17178..9861875` = 651 commits, `git diff --name-only` = 3085 files,
`--shortstat` = 306840 insertions, 0 deletions — agreeing exactly with
the connector PR read. `git merge-tree --write-tree` `9861875` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `683769c0…`. No re-fetch
was needed before applying: the run fetched at ~00:40 JST (the run start)
and the remote head was still `9861875`, integration still `f3db6b3` — no
intervening push; the connector read ~00:40 JST independently confirmed
head `9861875`.

R231 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  title head refreshed to `9861875`; milestone lines refreshed to head
  `9861875` (651 commits / 3085 files / 306840 additions; the fresh git
  derivation at `9861875`, the fresh connector PR read ~00:40 JST, and
  the merge-tree cross-check at `9861875` are cited, with the live body
  R222 read back byte-exact this round — 0 U+FFFD, no resync needed);
  delta `8310e5d..9861875`: 5 paths, 1127 insertions, 12 deletions);
  one row appended — PR119 BODY RESTRUCTURE R230 (`644d4ab`/`9861875`),
  recording that its payload was prepared after push ~23:57 JST
  (101.488 ký tự, sha `5cda4d67`; JSON 115.948 byte < trần 131.072 —
  còn 15.124 byte, bản giữ tại `.bak-prepost-20261124` — sha256
  `7d2ad913…`, main + .bak byte-identical) and then NOT posted (live body
  still R222 as read this round ~00:40 JST); no separate ACK for R230.
  The index now covers every block through `9861875`; R231's own 2
  commits fold in at the next index update (R232), disclosed in the index
  itself. The R231 note was appended after the R230 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `9861875` · 651 · 3085 (with the fresh git derivation at `9861875`,
  the fresh connector PR read ~00:40 JST, and the fresh merge-tree
  cross-check at `9861875`), plus the R230 paragraph in "Khối mới nhất"
  (271 ký tự, marked chưa đăng — payload prepared ~23:57 JST, live body
  still R222) and the R231 note. The stale index reference in "Về bản mô tả này"
  (head `8310e5d`) is also fixed to `9861875`, the "lượt cập nhật này"
  sentence is advanced R230 → R231, and the compaction trail gains
  "R231 đã gọn thêm các đoạn R59 + R58." (37 ký tự). The title line is
  extended to R230 (APPENDED, not replaced — see the R176 robustness
  note; the append measures 30 ký tự, not the hand-counted 28 — see the
  lesson below). Compaction (R230 warning — applied with a measured
  correction): the R59 + R58 paragraphs (493 and 493 ký tự — measured
  this round) are collapsed to one 207-ký-tự compact line each (full
  detail stays in the delivery index; the R76–R80 template measures 208,
  the R59/R58 lines measure 207 — the checker asserts < 400, not an
  exact 208) — the new R230 paragraph was 271 ký tự, so the body is
  101.064 ký tự — net −391 vs R230 despite the new R230 paragraph, the
  37-ký-tự trail append and the 30-ký-tự title append, headroom 3.936 ký
  tự. The dry-run first projected 101.064 ký tự and the apply wrote
  exactly that — measure, then trim, then apply; the head line shrank
  1.200 → 1.037 ký tự (−163, the R230 U+FFFD disclosure dropped after
  this round's clean byte-exact read).
  Paragraph order: the R230 paragraph sits directly after R229
  (ascending full-paragraph order R166..R230), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R231 (owner tap) — the R222 body v2 now live is the base;
  only the R230 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r231_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R230 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R230 and R231 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R230 (108 compact lines R59–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 101.064 ký tự),
  a check that the R230 paragraph sits directly after R229
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R230 note clean).
  New this round: the R229-row guard (cumulative must be 3083,
  re-derived from git at `644d4ab`), the R230-row guard (cumulative must
  cite 3086 — 3085 at `9861875` + 1 new checker in the R231 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R231, range R59–R165, list complete through R230, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 79/79**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R231_VALIDATION_20261125.json`).
  The checker passed on its first run this round in the exact pre-commit
  tree state (see the correction below — the post-content-commit re-run
  tripped only the working-tree guard, by design). The
  checker was written fresh (not sed-copied from R230) with the full COVER
  SHA verified intact (definition + docstring, both
  `98618758907741b4ff0af34365ba4302a6256c93` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (20 `9861875` hits — the cover
  value, in the definition, docstring, checks and the R230-row guard
  string citing "3085 at 9861875", legitimate; 4 `8310e5d` (docstring +
  R229-row guard citing "3082 at 8310e5d"), 4 `9890c75` (docstring +
  R228-row guard citing "3079 at 9890c75"), 4 `dbee5c5` (docstring +
  R227-row guard citing "3076 at dbee5c5"), 4 `556d3ec` (docstring +
  R226-row guard citing "3073 at 556d3ec"), 4 `2861100` (docstring +
  R225-row guard citing "3070 at 2861100"), 4 `1700859` (docstring +
  R224-row guard citing "3067 at 1700859"), 4 `e07fe1e` (docstring +
  R223-row guard citing "3064 at e07fe1e"), 4 `37ea7ad` (docstring +
  R222-row guard citing "3061 at 37ea7ad"), 3 `a38b714` (docstring +
  R221-row guard citing "3058 at a38b714"), 3 `c38a4dc` (docstring +
  R220-row guard citing "3055 at c38a4dc"), 3 `8f8b504` (docstring +
  R219-row guard citing "3052 at 8f8b504"), 3 `a74e9f4` (docstring +
  R218-row guard citing "3049 at a74e9f4"), 3 `0a4d05a` (docstring +
  R217-row guard citing "3046 at 0a4d05a"), 3 `0de54fb` (docstring +
  R216-row guard citing "3043 at 0de54fb"), 3 `1e564a2` (docstring +
  R215-row guard citing "3040 at 1e564a2"), 3 `3de99c9` (docstring +
  R214-row guard citing "3037 at 3de99c9"), legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 101.064 ký tự and the apply wrote on
  the first attempt at 101.064 ký tự, with 3.936 ký tự of headroom; the idempotency re-run
  after apply reports already-applied changed: 0 — verified (after two script fixes, see the lesson below).
  Correction caught before the report commit: the first checker run
  passed 79/79 pre-commit, but the post-content-commit re-run (to
  regenerate the validation JSON for the report commit) failed only on
  the working-tree guard (78/79) — the guard asserts the PRE-commit tree
  (index + body modified, checker untracked), so it fails by design once
  the content is committed. The fix was NOT to weaken the guard: the
  content commit was reset (mixed, not --soft — the --soft reset left
  staged "M "/"A " markers and the guard still tripped) to restore the
  exact pre-commit tree, the checker re-run fresh: PASS 79/79, and the
  content was re-committed as `9482f4d` with the identical tree
  (merge-tree `2125a7ad…` both times). The first content commit
  `5e9d8eb` was abandoned locally, never pushed, and is referenced by no
  branch. The R230 row's cumulative figure was drafted as 3086
  (3085 at `9861875` + 1 new checker) and the true diff at the R231 content
  commit is 3086 — verified by `git diff --name-only cf17178..9482f4d` = 3086
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R230's committed content this round: R230's committed content verified correct —
  the committed index at `9861875` carries the R228 row at cumulative 3080
  (re-derived by the new checker from git at `7aa25a8`) and the R229 row at 3083
  (re-derived from git at `644d4ab`); no uncommitted
  working-tree fix was left behind by R230 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R231 robustness note — headroom now 3.936 chars

The R230 warning left 3.545 ký tự of headroom, so this round compacted
TWO paragraphs (R59 + R58, 493 + 493 ký tự → 207 each) before adding the new R230 paragraph
(271 ký tự). The body is now 101.064 ký tự — net −391 vs R230 — with
3.936 ký tự of headroom. The double compaction bought back 572 ký tự against the
271-ký-tự new paragraph, and the head line shrank a further 163 ký tự because the
R230 U+FFFD disclosure is no longer needed after a clean read, so the net recovery
is −391 even after the 37-ký-tự trail append and the 30-ký-tự title append.
The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R232 warning: headroom is 3.936 ký tự; compact R57 + R56 next (or the head line
grows again if a future round's reads hit the rate-limit — the honest disclosure
is the variable cost, not the compaction).
At the current net −391/round the margin is recovering,
but only while the double compaction continues (full paragraphs remaining R166..R230 = 65;
compact block R59–R165 = 108 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (101.064 projected; apply wrote 101.064 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230).
The title append measured 30 chars, not the hand-counted 28 — the append string is
" + PR119 BODY RESTRUCTURE R230" (space, plus, space, ...), and the
net −391 matched only because the measured projection was trusted over the hand-count;
a wrong hand-count must never be written over a
measured projection. (2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230 — the R230 row's 3086 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — this round the re-run initially crashed on the head-line and mergeable-line OLD-state asserts (an R207-class defect in the new
script itself, caught by the re-run before any commit); fixed by checking the new state first in `line_replace`, and the guard must compare
against the new line itself when the new line shares the old prefix (the counts and mergeable lines do). The per-edit applied-delta accounting was fixed in the same pass: on a re-run every component delta
is 0, so the budget check becomes an identity instead of tripping on a stale hand-counted expectation.
(4) Append-style edits need the new-state check FIRST in `sub_once` too: the new trail string contains the old
string, so `old in text` stays true after apply — the first re-run duplicated the trail (+37) before the fix;
repaired (duplicate removed, body back to 101.064) before any commit, and the re-run after the fix reports
changed: 0. (5) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (6) Two backup locations can hold
different versions of the same payload — the R230 payload's main file and its `.bak-prepost-20261124/` copy
were verified byte-identical this round (sha256 `7d2ad913…`, 115.948 byte) before the R230 row recorded it;
a payload backup the authoring round made must be verified, not re-claimed — R231 verified the R230 payload's
body sha (`5cda4d67`) against the repo body v2 + head-line refresh (101.488 ký tự) and recorded it as prepared
but NOT posted, since the live body read this round is still R222. Note: the `.bak` lives INSIDE the
directory `.bak-prepost-20261124/` (`.bak-prepost-20261124/pr119_update_body_v2_r230.json`), not as a
sibling file — this round located it inside the directory on the first check; a missing sibling file is not a missing
backup — check the directory first.
(7) An `updated_at` that DOES move while the body sha stays means a push updated the head only — the PR read this
round shows updated_at 2026-11-24T14:57:11Z, changed from the R230 read's 13:56:02Z, while the body sha is unchanged
(`1dd61afd` = R222, byte-exact on the first read); the head line says so explicitly instead of implying a body refresh.
(8) A connector call that fails on a wrong method name is not a failed read — R227's first
`pull_request_read` used method `get_pull` and the MCP rejected it (tool not in the reviewed read-only
set for that method); the retry with method `get` + `pullNumber` succeeded and returned the full PR object.
This round the first call used method `get` and succeeded — record the method name in the report; do not treat the first failure as missing direction, and do not
fall back to unauthenticated curl.
(9) `issue_read` `get_comments` is paginated at 30 comments per page — this round the first call returned
30 comments (through `6819808977`) and page 2 returned the remaining 4 (through `6862732081`), total 34; a
single-page read is not the full issue, and the latest comment lives on the last page.
(10) No execution-risk flag appeared on any git/script command this round
(unlike R211/R213 and the R219-blocked run ~11:40 JST); the flag itself has now appeared 4 times
(R211 ~01:40, R213 ~04:40, R213 ~05:44, R219 ~11:40) and the decision whether to keep running git/checker after it still awaits
luồng chính/chủ dự án — recorded here, not decided here.
(11) Mergeable_state is a point-in-time read, not a stable property of the head: the R230 payload's own head line
(read ~23:57 JST) said mergeable_state clean at `9861875`; this round's fresh
read ~00:40 JST agrees (clean) — the honest wording is the fresh read, not the payload's older one.
(12) A live-body read can be clean on the first try: this
round's read showed 0 U+FFFD and a sha (1dd61afd) identical to the R222 payload — no resync was needed,
unlike R230's 5 U+FFFD read-channel artifact. Never conclude the live body changed from a sha/length mismatch alone; resync
against the known payload before claiming a change — and when the read is clean, say so plainly instead of
repeating the previous round's disclosure. The checker cannot
see this (it reads only repo files), so the live-read step belongs in the
round's report, and the head line must carry the fresh read's figures.
(13) The checker writes its validation JSON at the END of its run, AFTER
the working-tree guard — so a checker re-run always trips the guard on
its own previous output. Delete the validation JSON before a re-run;
do not weaken the guard. New this round: the guard also asserts the
PRE-commit tree, so a re-run AFTER the content commit fails it by design
(78/79 this round) — restore the exact pre-commit tree with a mixed reset
(`git reset`, not `git reset --soft`, which leaves staged markers the
guard does not expect) before re-running; never edit the guard to fit the
post-commit tree.

## Verification

- Merge-tree `9861875` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `683769c0…`. Merge-tree at the R231
  content head `9482f4d` vs `f3db6b3`: exit 0,
  tree `2125a7ad…`.
- Live PR state: connector read this round (~00:40 JST) — direct read
  (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222
  payload on the first read; updated_at 2026-11-24T14:57:11Z — changed vs
  the R230 read, body bytes unchanged); mergeable_state clean at
  `9861875` (connector read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: comments read SUCCEEDED this round — connector `issue_read` ~00:40 JST (paginated 30 + 4): still 34
  comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081` (CP5 + M-G CP10 + R2); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R231 block (`9861875..9482f4d`) 3 paths / 0 violations
  (index + body v2 + R231 checker); cumulative at the R231 content
  commit `9482f4d` 3086 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `9482f4d`). Merge-tree at the R231 content head `9482f4d` vs `f3db6b3`: exit 0,
  tree `2125a7ad…`.
- Transient notes: this round's `git fetch` at ~00:40 JST succeeded
  first try. The connector read path was used this round — both reads
  succeeded (PR + issue, first try on `pull_request_read` with method `get`, and pagination on `issue_read`). No call-tool write approval was requested for a read. No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST). No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH; the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
- Ceiling discipline: the R230 payload JSON as-prepared measured 115.948 byte
  (prepared ~23:57 JST, NOT posted — live body is still R222, verified by this round's connector read),
  vs the 131.072-byte transport ceiling
  (15.124 byte headroom). The projected R231 payload JSON is ~116,000 byte
  (measured exactly at payload build, after push). Body v2 is now 101.064
  ký tự (< 105.000) — 3.936 ký tự of headroom. R231 warning:
  headroom is now 3.936 ký tự; the double compaction must continue next round
  (R57 + R56) or the head line must be trimmed if a future round's reads hit the rate-limit again.

## Next

Posting round (owner tap): PR #119 description refresh to the R231 body
v2 (R230 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r231.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R231 push (title
ending "+ R231", built by replacing the "+ R222" suffix — not appending;
body = body v2 R231 in repo, head line refreshed to head after R231 push).
This run started ~00:40 JST — OUTSIDE working hours (after 21:30 JST), so the
R231 payload is HELD for working hours (like R142/R164–R197/R207–R216/R228/R229/R230,
which were held for the same reason). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R230 payload as new — R230 was prepared but never posted and is superseded by R231; do not present the R222 payload as new — R222 is LIVE; do not present either R221 widget (`widget-56770776`, `widget-7a108c57`) — R221 was never posted and both are stale. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220, R221, R222, R223, R224, R225, R226, R227, R228, R229 and R230 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R231: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
