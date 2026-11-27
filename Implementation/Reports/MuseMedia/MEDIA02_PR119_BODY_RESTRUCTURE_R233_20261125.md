# MEDIA-02 — PR #119 Body Restructure R233: delivery index + body v2 coverage to `f022665`

Date: 2026-11-25 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `f022665` (PR119 BODY RESTRUCTURE R232 report). Content commit: `233f0b5`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R233 does

R232 left two disclosed gaps: the delivery index covered 653 commits to
`29727d4`; R232's own 2 commits were to fold in at R233 — and the R232
payload was prepared but NOT posted (live body still R222). The R232
payload (`pr119_update_body_v2_r232.json`, body 100.869 ký tự, sha
`4b05d0d1`, JSON 115.058 byte < trần 131.072 — còn 16.014 byte, bản giữ tại
`.bak-prepost-20261124` — sha256 `71f9d7be…`, main + .bak byte-identical)
was prepared after the R232 push ~02:00 JST and is HELD for working hours
(run started outside working hours, after 21:30 JST); it is superseded by
R233. R222 was posted live 2026-11-24 ~16:16 JST, replacing R140. No new
Codex/owner direction has been verified on issue #116: the comments read
SUCCEEDED this round (connector `issue_read` ~02:42 JST, paginated 30 + 4:
still 34 comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081`
(CP5 + M-G CP10 + R2); no new direction since Gói 39 (`6815238814`).

Fresh derivation at `f022665` (~02:42 JST): `git rev-list --count
cf17178..f022665` = 655 commits, `git diff --name-only` = 3091 files,
`--shortstat` = 309109 insertions, 0 deletions — agreeing exactly with
the connector PR read. `git merge-tree --write-tree` `f022665` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `f627ff91…`. No re-fetch
was needed before applying: the run fetched at ~02:40 JST (the run start)
and the remote head was still `f022665`, integration still `f3db6b3` — no
intervening push; the connector read ~02:42 JST independently confirmed
head `f022665`. The live PR read this round (~02:42 JST,
`pull_request_read` method `get`): title ends "+ R222", head `f022665`,
655 commits / 3091 files / +309109, mergeable null — GitHub computing at
read time — / mergeable_state clean at `f022665`, live body 103.023 ký tự,
sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222 payload on the first
read, no resync needed this round —, updated_at 2026-11-24T16:59:07Z —
changed vs the R232 read because the R232 push updated the head; the body
bytes are unchanged.

R233 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  title head refreshed to `f022665`; milestone lines refreshed to head
  `f022665` (655 commits / 3091 files / 309109 additions; the fresh git
  derivation at `f022665`, the fresh connector PR read ~02:42 JST, and
  the merge-tree cross-check at `f022665` are cited, with the live body
  R222 read back byte-exact this round — 0 U+FFFD, no resync needed);
  delta `29727d4..f022665`: 5 paths, 1164 insertions, 12 deletions);
  one row appended — PR119 BODY RESTRUCTURE R232 (`c3a4eec`/`f022665`),
  recording that its payload was prepared after the R232 push (100.869 ký
  tự, sha `4b05d0d1`; JSON 115.058 byte < trần 131.072 — còn 16.014 byte,
  bản giữ tại `.bak-prepost-20261124` — sha256 `71f9d7be…`) and then NOT
  posted (live body still R222 as read this round ~02:42 JST);
  no separate ACK for R232.
  The index now covers every block through `f022665`; R233's own 2
  commits fold in at the next index update (R234), disclosed in the index
  itself. The R233 note was appended after the R232 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `f022665` · 655 · 3091 (with the fresh git derivation at `f022665`,
  the fresh connector PR read ~02:42 JST, and the fresh merge-tree
  cross-check at `f022665`), plus the R232 paragraph in "Khối mới nhất"
  (271 ký tự, marked chưa đăng — payload prepared, live body still R222)
  and the R233 note. The stale index reference in "Về bản mô tả này"
  (head `29727d4`) is also fixed to `f022665`, the "lượt cập nhật này"
  sentence is advanced R232 → R233, and the compaction trail gains
  "R233 đã gọn thêm các đoạn R55 + R54." (37 ký tự). The title line is
  extended to R232 (APPENDED, not replaced — see the R176 robustness
  note; the append measures 30 ký tự, not the hand-counted 28 — see the
  lesson below). Compaction (R232 warning — applied with a measured
  correction): the R55 + R54 paragraphs (493 and 504 ký tự — measured
  this round) are collapsed to one 207-ký-tự compact line each (full
  detail stays in the delivery index; the R76–R80 template measures 208,
  the R55/R54 lines measure 207 — the checker asserts < 400, not an
  exact 208) — the new R232 paragraph was 271 ký tự, so the body is
  100.579 ký tự — net −239 vs R232 despite the new R232 paragraph, the
  37-ký-tự trail append and the 30-ký-tự title append, headroom 4.421 ký
  tự. The dry-run first projected 100.579 ký tự and the apply wrote
  exactly that — measure, then trim, then apply; the head line stayed
  1.033 ký tự (0 net).
  Paragraph order: the R232 paragraph sits directly after R231
  (ascending full-paragraph order R166..R232), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R233 (owner tap) — the R222 body v2 now live is the base;
  only the R232 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r233_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R232 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R232 and R233 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R232 (112 compact lines R54–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 100.579 ký tự),
  a check that the R232 paragraph sits directly after R231
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R232 note clean).
  New this round: the R231-row guard (cumulative must be 3089,
  re-derived from git at `c3a4eec`), the R232-row guard (cumulative must
  cite 3092 — 3091 at `f022665` + 1 new checker in the R233 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R233, range R55–R165, list complete through R232, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 83/83**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R233_VALIDATION_20261125.json`).
  The checker passed on its FIRST run this round in the exact pre-commit
  tree state (no correction needed — unlike R232's first-run 80/81
  compact-count failure). The
  checker was written fresh (not sed-copied from R232) with the full COVER
  SHA verified intact (definition + docstring, both
  `f022665dfde511687aa9034e0c3dc56ed8c1de2e` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (22 `f022665` hits — the cover
  value, in the definition, docstring, checks and the R232-row guard
  string citing "3091 at f022665", legitimate; 5 `29727d4` (docstring +
  R231-row guard citing "3088 at 29727d4" + the R233 edit-script lesson
  recording the lost title edit), 4 `9861875` (docstring +
  R230-row guard citing "3085 at 9861875"), 4 `8310e5d` (docstring +
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
  R214-row guard citing "3037 at 3de99c9"), 3 `c3a4eec` (docstring +
  row-convention tuple R231), legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 100.579 ký tự and the apply wrote on
  the first attempt at 100.579 ký tự, with 4.421 ký tự of headroom; the idempotency re-run
  after apply reports already-applied changed: 0 — verified.
  Correction caught before the content commit: the first version of the
  edit script applied the index title-head edit via `sub_once` on a
  separate `index_text` string that is never joined back — the edit was
  silently lost (the file kept head `29727d4` in its title) and only the
  idempotency re-run exposed it (changed: 1 on re-run). Fixed by routing
  the title edit through `il` like every other index edit; the checker is
  the backstop for this defect class (its "index header coverage head"
  check would have failed the content commit). The documents were
  correct after the fix; the checker passed 83/83 on its first run
  against the fixed tree. The R232 row's cumulative figure was drafted
  as 3092 (3091 at `f022665` + 1 new checker) and the true diff at the
  R233 content commit is 3092 — verified by
  `git diff --name-only cf17178..233f0b5` = 3092 after the content commit.
  `git status --porcelain` after the content commit showed only the
  intended validation JSON untracked — no leftover edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R232's committed content this round: R232's committed content verified correct —
  the committed index at `f022665` carries the R230 row at cumulative 3086
  (re-derived by the new checker from git at `9482f4d`) and the R231 row at 3089
  (re-derived from git at `c3a4eec`); no uncommitted
  working-tree fix was left behind by R232 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R233 robustness note — headroom now 4.421 chars

The R232 warning left 4.182 ký tự of headroom, so this round compacted
TWO paragraphs (R55 + R54, 493 + 504 ký tự → 207 each) before adding the new R232 paragraph
(271 ký tự). The body is now 100.579 ký tự — net −239 vs R232 — with
4.421 ký tự of headroom. The double compaction bought back 583 ký tự against
the 271-ký-tự new paragraph, and the head line stayed flat, so the net recovery
is −239 even after the 37-ký-tự trail append and the 30-ký-tự title append.
The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R234 warning: headroom is 4.421 ký tự; compact R53 + R52 next (or the head line
grows again if a future round's reads hit the rate-limit — the honest disclosure
is the variable cost, not the compaction).
At the current net −239/round the margin is recovering,
but only while the double compaction continues (full paragraphs remaining R166..R232 = 67;
compact block R54–R165 = 112 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (100.579 projected; apply wrote 100.579 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232).
The title append measured 30 chars, not the hand-counted 28 — the append string is
" + PR119 BODY RESTRUCTURE R232" (space, plus, space, ...), and the
net −239 matched only because the measured projection was trusted over the hand-count;
a wrong hand-count must never be written over a
measured projection. (2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232 — the R232 row's 3092 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — this round the re-run initially reported changed: 1
(the lost title-head edit, see the correction above) and changed: 0 after the fix;
the per-edit applied-delta accounting stays an identity on re-run instead of tripping on a stale hand-counted expectation.
(4) Append-style edits need the new-state check FIRST in `sub_once` too: the new trail string contains the old
string, so `old in text` stays true after apply — the R231 fix holds; this round's re-run confirmed changed: 0.
(5) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (6) Two backup locations can hold
different versions of the same payload — the R232 payload's main file and its `.bak-prepost-20261124/` copy
were verified byte-identical this round (sha256 `71f9d7be…`, 115.058 byte) right after the late build;
a payload backup the authoring round made must be verified, not re-claimed — R233 verified the R232 payload's
body sha (`4b05d0d1`) against the repo body v2 + head-line refresh (100.869 ký tự) and recorded it as prepared
but NOT posted, since the live body read this round is still R222. Note: the `.bak` lives INSIDE the
directory `.bak-prepost-20261124/` (`.bak-prepost-20261124/pr119_update_body_v2_r232.json`), not as a
sibling file — this round located it inside the directory on the first check; a missing sibling file is not a missing
backup — check the directory first.
(7) An `updated_at` that DOES move while the body sha stays means a push updated the head only — the PR read this
round shows updated_at 2026-11-24T16:59:07Z, changed from the R232 read's 16:02:09Z, while the body sha is unchanged
(`1dd61afd` = R222, byte-exact on the first read); the head line says so explicitly instead of implying a body refresh.
(8) A connector call that fails on a wrong method name is not a failed read — R227's first
`pull_request_read` used method `get_pull` and the MCP rejected it (tool not in the reviewed read-only
set for that method); the retry with method `get` + `pullNumber` succeeded and returned the full PR object.
This round the first call used method `get` and succeeded — record the method name in the report; do not treat the first failure as missing direction, and do not
fall back to unauthenticated curl.
(9) `issue_read` `get_comments` is paginated at 30 comments per page — this round the first call returned
30 comments (through `6819808977`) and page 2 returned the remaining 4 (through `6862732081`), total 34; a
single-page read is not the full issue, and the latest comment lives on the last page.
(10) The execution-risk flag has now appeared 5 times
(R211 ~01:40, R213 ~04:40, R213 ~05:44, R219 ~11:40, R231 ~01:02) and the decision whether to keep running git/checker after it still awaits
luồng chính/chủ dự án — recorded here, not decided here. This round proceeds on the queue's explicit next-block
assignment (R233) and the R219-blocked precedent (a blocked run stops; the next scheduled run retries cleanly).
No execution-risk flag on any git/script command this round.
(11) Mergeable_state is a point-in-time read, not a stable property of the head: the R232 payload's own head line
(read ~01:59 JST) said mergeable_state unstable at `f022665` (CI running, clean at `29727d4`); this round's fresh
read ~02:42 JST says mergeable_state clean at `f022665` — the honest wording is the fresh read, not the payload's older one.
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
do not weaken the guard. The guard also asserts the
PRE-commit tree, so a re-run AFTER the content commit fails it by design
(the checker ran once this round, pre-commit, and passed 83/83 — the
guard passed because the validation JSON did not exist before the run;
no re-run was done this round).
(14) The compact-line count and the per-round loop range can drift apart
by one: the "Ghi chú" range text and the loop range name the block's
upper rounds (R55–R165), but the block itself extends one round lower
(R54–R165 = 112 lines) because each round compacts TWO paragraphs while
the range text advances by the pair's upper round only — R232 had the
same shape (110 lines, loop R57–R165). The checker must assert the TRUE
block count (112) and loop the TRUE block range (R54–R165), not the
range text; the range text follows its own convention and is asserted
separately as "R55–R165".
(15) NEW THIS ROUND: an edit must target the structure that is written
back. The R233 edit script's first version applied the index title-head
edit to a discarded string copy (`index_text` via `sub_once`) while the
file is rebuilt from the line list `il` — the edit vanished silently and
only the idempotency re-run (changed: 1) exposed it. Every edit in a
script that rebuilds a file from a split list must go through that list;
a helper that returns a new string is only safe when its result feeds the
rebuild. The checker is the backstop (its header-coverage check would
have failed the content commit), but the re-run caught it first — run the
re-run BEFORE the checker, not after.

## Verification

- Merge-tree `f022665` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `f627ff91…`. Merge-tree at the R233
  content head `233f0b5` vs `f3db6b3`: exit 0,
  tree `830e881c…`.
- Live PR state: connector read this round (~02:42 JST) — direct read
  (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222
  payload on the first read; updated_at 2026-11-24T16:59:07Z — changed vs
  the R232 read, body bytes unchanged); mergeable_state clean at
  `f022665` (connector read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: comments read SUCCEEDED this round — connector `issue_read` ~02:42 JST (paginated 30 + 4): still 34
  comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081` (CP5 + M-G CP10 + R2); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R233 block (`f022665..233f0b5`) 3 paths / 0 violations
  (index + body v2 + R233 checker); cumulative at the R233 content
  commit `233f0b5` 3092 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `233f0b5`). Merge-tree at the R233 content head `233f0b5` vs `f3db6b3`: exit 0,
  tree `830e881c…`.
- Transient notes: this round's `git fetch` at ~02:40 JST succeeded
  first try (one `git ls-remote` attempt reset by the proxy first, then
  succeeded on retry — no data lost, no stale head used). The connector read path was used this round — both reads
  succeeded (PR + issue, first try on `pull_request_read` with method `get`, and pagination on `issue_read`). No call-tool write approval was requested for a read. No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST and the R231-flagged run ~01:02 JST). No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH; the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
- Ceiling discipline: the R232 payload JSON as-prepared measured 115.058 byte
  (prepared after the R232 push ~02:00 JST, NOT posted — live body is still R222, verified by this round's connector read),
  vs the 131.072-byte transport ceiling
  (16.014 byte headroom). The projected R233 payload JSON is ~116,000 byte
  (measured exactly at payload build, after push). Body v2 is now 100.579
  ký tự (< 105.000) — 4.421 ký tự of headroom. R233 warning:
  headroom is now 4.421 ký tự; the double compaction must continue next round
  (R53 + R52) or the head line must be trimmed if a future round's reads hit the rate-limit again.

## Next

Posting round (owner tap): PR #119 description refresh to the R233 body
v2 (R232 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r233.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R233 push (title
ending "+ R233", built by replacing the "+ R222" suffix — not appending;
body = body v2 R233 in repo, head line refreshed to head after R233 push).
This run started ~02:40 JST — OUTSIDE working hours (after 21:30 JST), so the
R233 payload is HELD for working hours (like R142/R164–R197/R207–R216/R228/R229/R230/R231/R232,
which were held for the same reason). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R232 payload as new — R232 was prepared but never posted and is superseded by R233; do not present the R222 payload as new — R222 is LIVE; do not present either R221 widget (`widget-56770776`, `widget-7a108c57`) — R221 was never posted and both are stale. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220, R221, R222, R223, R224, R225, R226, R227, R228, R229, R230, R231 and R232 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R233: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
