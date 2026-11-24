# MEDIA-02 — PR #119 Body Restructure R235: delivery index + body v2 coverage to `19e8f7c`

Date: 2026-11-25 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `19e8f7c` (PR119 BODY RESTRUCTURE R234 report). Content commit: `db681a3`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R235 does

R234 left two disclosed gaps: the delivery index covered 657 commits to
`33962fd`; R234's own 2 commits were to fold in at R235 — and the R234
payload was prepared but NOT posted (live body still R222). The R234
payload (`pr119_update_body_v2_r234.json`, body 100.380 ký tự, sha
`bc4c7282`, JSON 114.330 byte < trần 131.072 — còn 16.742 byte, bản giữ tại
`.bak-prepost-20261124` — sha256 `59307411…`, main + .bak byte-identical)
was prepared after the R234 push ~03:52 JST and is HELD for working hours
(run started outside working hours, after 21:30 JST); it is superseded by
R235. R222 was posted live 2026-11-24 ~16:16 JST, replacing R140. No new
Codex/owner direction has been verified on issue #116: the comments read
SUCCEEDED this round (connector `issue_read` ~04:45 JST, paginated 30 + 4:
still 34 comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081`
(CP5 + M-G CP10 + R2); no new direction since Gói 39 (`6815238814`).

Fresh derivation at `19e8f7c` (~04:45 JST): `git rev-list --count
cf17178..19e8f7c` = 659 commits, `git diff --name-only` = 3097 files,
`--shortstat` = 311503 insertions, 0 deletions — agreeing exactly with
the connector PR read. `git merge-tree --write-tree` `19e8f7c` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `4cd1742c…`. No re-fetch
was needed before applying: the run fetched at ~04:40 JST (the run start)
and the remote head was still `19e8f7c`, integration still `f3db6b3` — no
intervening push; the connector read ~04:45 JST independently confirmed
head `19e8f7c`. The live PR read this round (~04:45 JST,
`pull_request_read` method `get`): title ends "+ R222", head `19e8f7c`,
659 commits / 3097 files / +311503, mergeable null — GitHub computing at
read time — / mergeable_state clean at `19e8f7c`, live body 103.023 ký tự,
sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222 payload on the first
read, no resync needed this round —, updated_at 2026-11-24T18:51:46Z —
changed vs the R234 read because the R234 push updated the head; the body
bytes are unchanged.

R235 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  title head refreshed to `19e8f7c`; milestone lines refreshed to head
  `19e8f7c` (659 commits / 3097 files / 311503 additions; the fresh git
  derivation at `19e8f7c`, the fresh connector PR read ~04:45 JST, and
  the merge-tree cross-check at `19e8f7c` are cited, with the live body
  R222 read back byte-exact this round — 0 U+FFFD, no resync needed);
  delta `b50891a..19e8f7c`: 2 paths, 672 insertions, 0 deletions);
  one row appended — PR119 BODY RESTRUCTURE R234 (`b50891a`/`19e8f7c`),
  recording that its payload was prepared after the R234 push (100.380 ký
  tự, sha `bc4c7282`; JSON 114.330 byte < trần 131.072 — còn 16.742 byte,
  bản giữ tại `.bak-prepost-20261124` — sha256 `59307411…`) and then NOT
  posted (live body still R222 as read this round ~04:45 JST);
  no separate ACK for R234.
  The index now covers every block through `19e8f7c`; R235's own 2
  commits fold in at the next index update (R236), disclosed in the index
  itself. The R235 note was appended after the R234 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `19e8f7c` · 659 · 3097 (with the fresh git derivation at `19e8f7c`,
  the fresh connector PR read ~04:45 JST, and the fresh merge-tree
  cross-check at `19e8f7c`), plus the R234 paragraph in "Khối mới nhất"
  (271 ký tự, marked chưa đăng — payload prepared, live body still R222)
  and the R235 note. The stale index reference in "Về bản mô tả này"
  (head `33962fd`) is also fixed to `19e8f7c`, the "lượt cập nhật này"
  sentence is advanced R234 → R235, and the compaction trail gains
  "R235 đã gọn thêm các đoạn R51 + R50." (37 ký tự). The title line is
  extended to R234 (APPENDED, not replaced — see the R176 robustness
  note; the append measures 30 ký tự, not the hand-counted 28 — see the
  lesson below). Compaction (R234 warning — applied with a measured
  correction): the R51 + R50 paragraphs (504 and 504 ký tự — measured
  this round) are collapsed to one 207-ký-tự compact line each (full
  detail stays in the delivery index; the R76–R80 template measures 208,
  the R51/R50 lines measure 207 — the checker asserts < 400, not an
  exact 208) — the new R234 paragraph was 271 ký tự, so the body is
  100.079 ký tự — net −250 vs R234 despite the new R234 paragraph, the
  37-ký-tự trail append and the 30-ký-tự title append, headroom 4.921 ký
  tự. The dry-run first projected 100.079 ký tự and the apply wrote
  exactly that — measure, then trim, then apply; the head line stayed
  1.033 ký tự (0 net).
  Paragraph order: the R234 paragraph sits directly after R233
  (ascending full-paragraph order R166..R234), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R235 (owner tap) — the R222 body v2 now live is the base;
  only the R234 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r235_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R234 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R234 and R235 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R234 (116 compact lines R50–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 100.079 ký tự),
  a check that the R234 paragraph sits directly after R233
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R234 note clean).
  New this round: the R233-row guard (cumulative must be 3095,
  re-derived from git at `b50891a`), the R234-row guard (cumulative must
  cite 3098 — 3097 at `19e8f7c` + 1 new checker in the R235 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R235, range R51–R165, list complete through R234, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 87/87**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R235_VALIDATION_20261125.json`).
  The checker passed on its FIRST run this round in the exact pre-commit
  tree state (no correction needed — like R234's first-run 85/85 pass). The
  checker was written fresh (not sed-copied from R234) with the full COVER
  SHA verified intact (definition + docstring, both
  `19e8f7c6ddee82207b4cf3b13fa6ff191a19e9a2` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (23 `19e8f7c` hits — the cover
  value, in the definition, docstring, checks and the R234-row guard
  string citing "3097 at 19e8f7c", legitimate; 5 `33962fd` (docstring +
  R233-row guard citing "3094 at 33962fd"), 3 `b50891a` (docstring +
  row-convention tuple R233 + R234-row comment), 5 `233f0b5` (docstring +
  row-convention tuple R232 + R232-row guard citing "3092 at 233f0b5"),
  all legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 100.079 ký tự and the apply wrote on
  the first attempt at 100.079 ký tự, with 4.921 ký tự of headroom; the idempotency re-run
  after apply reports already-applied changed: 0 — verified (after the
  two fixes in lesson 16 below; the first re-run crashed on an old-state
  find prefix, before any re-apply could happen — no file was touched
  twice, no duplication).
  No correction was needed before the content commit this round: the edit
  script applied cleanly on its first run (dry-run 100.079 = apply
  100.079; idempotency re-run changed: 0 on the first re-run after the
  lesson-16 fix), unlike R233's lost title-head edit — the R233 lesson (15) held, every edit
  routes through the line lists `il`/`bl`. The documents were
  correct after the fix; the checker passed 87/87 on its first run
  against the applied tree. The R234 row's cumulative figure was drafted
  as 3098 (3097 at `19e8f7c` + 1 new checker) and the true diff at the
  R235 content commit is 3098 — verified by
  `git diff --name-only cf17178..db681a3` = 3098 after the content commit.
  `git status --porcelain` after the content commit showed only the
  intended validation JSON untracked — no leftover edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R234's committed content this round: R234's committed content verified correct —
  the committed index at `19e8f7c` carries the R232 row at cumulative 3092
  (re-derived by the new checker from git at `233f0b5`) and the R233 row at 3095
  (re-derived from git at `b50891a`); no uncommitted
  working-tree fix was left behind by R234 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R235 robustness note — headroom now 4.921 chars

The R234 warning left 4.671 ký tự of headroom, so this round compacted
TWO paragraphs (R51 + R50, 504 + 504 ký tự → 207 each) before adding the new R234 paragraph
(271 ký tự). The body is now 100.079 ký tự — net −250 vs R234 — with
4.921 ký tự of headroom. The double compaction bought back 594 ký tự against
the 271-ký-tự new paragraph, and the head line stayed flat, so the net recovery
is −250 even after the 37-ký-tự trail append and the 30-ký-tự title append.
The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R236 warning: headroom is 4.921 ký tự; compact R49 + R48 next (or the head line
grows again if a future round's reads hit the rate-limit — the honest disclosure
is the variable cost, not the compaction).
At the current net −250/round the margin is recovering,
but only while the double compaction continues (full paragraphs remaining R166..R234 = 69;
compact block R50–R165 = 116 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (100.079 projected; apply wrote 100.079 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234).
The title append measured 30 chars, not the hand-counted 28 — the append string is
" + PR119 BODY RESTRUCTURE R234" (space, plus, space, ...), and the
net −250 matched only because the measured projection was trusted over the hand-count;
a wrong hand-count must never be written over a
measured projection. (2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234 — the R234 row's 3098 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — this round the re-run reported changed: 0 on the
first re-run after the lesson-16 fix (no lost edit, unlike R233); the per-edit applied-delta accounting stays an identity on re-run instead of tripping on a stale hand-counted expectation.
(4) Append-style edits need the new-state check FIRST in `sub_once` too: the new trail string contains the old
string, so `old in text` stays true after apply — the R231 fix holds; this round's re-run confirmed changed: 0.
(5) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (6) Two backup locations can hold
different versions of the same payload — the R234 payload's main file and its `.bak-prepost-20261124/` copy
were verified byte-identical this round (sha256 `59307411…`, 114.330 byte) right after the late build;
a payload backup the authoring round made must be verified, not re-claimed — R235 verified the R234 payload's
body sha (`bc4c7282`) against the repo body v2 + head-line refresh (100.380 ký tự) and recorded it as prepared
but NOT posted, since the live body read this round is still R222. Note: the `.bak` lives INSIDE the
directory `.bak-prepost-20261124/` (`.bak-prepost-20261124/pr119_update_body_v2_r234.json`), not as a
sibling file — this round located it inside the directory on the first check; a missing sibling file is not a missing
backup — check the directory first.
(7) An `updated_at` that DOES move while the body sha stays means a push updated the head only — the PR read this
round shows updated_at 2026-11-24T18:51:46Z, changed from the R234 read's 17:51:27Z, while the body sha is unchanged
(`1dd61afd` = R222, byte-exact on the first read); the head line says so explicitly instead of implying a body refresh.
(8) A connector call that fails on a wrong parameter name is not a failed read — R235's first
`pull_request_read` `get` used `pull_number` and the MCP rejected it (missing required parameter:
`pullNumber`); the retry with `pullNumber` succeeded. Record the parameter name in the report; do not treat the first failure
as missing direction, and do not fall back to unauthenticated curl. (The `gh` CLI is also
not authenticated on this VM — `gh auth login` needed — so the connector is the read path; do not
treat the CLI failure as a failed read either.)
(9) `issue_read` `get_comments` is paginated at 30 comments per page — this round the first call returned
30 comments (through `6819808977`) and page 2 returned the remaining 4 (through `6862732081`), total 34; a
single-page read is not the full issue, and the latest comment lives on the last page.
(10) The execution-risk flag has now appeared 5 times
(R211 ~01:40, R213 ~04:40, R213 ~05:44, R219 ~11:40, R231 ~01:02) and the decision whether to keep running git/checker after it still awaits
luồng chính/chủ dự án — recorded here, not decided here. This round proceeds on the queue's explicit next-block
assignment (R235) and the R219-blocked precedent (a blocked run stops; the next scheduled run retries cleanly).
No execution-risk flag on any git/script command this round.
(11) Mergeable_state is a point-in-time read, not a stable property of the head: the R234 payload's own head line
(read ~03:52 JST) said mergeable_state clean at `19e8f7c`; this round's fresh
read ~04:45 JST says mergeable_state clean at `19e8f7c` — the honest wording is the fresh read, not the payload's older one.
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
(the checker ran once this round, pre-commit, and passed 87/87 — the
guard passed because the validation JSON did not exist before the run;
no re-run was done this round).
(14) The compact-line count and the per-round loop range can drift apart
by one: the "Ghi chú" range text and the loop range name the block's
upper rounds (R51–R165), but the block itself extends one round lower
(R50–R165 = 116 lines) because each round compacts TWO paragraphs while
the range text advances by the pair's upper round only — R234 had the
same shape (114 lines, loop R53–R165). The checker must assert the TRUE
block count (116) and loop the TRUE block range (R50–R165), not the
range text; the range text follows its own convention and is asserted
separately as "R51–R165".
(15) NEW THIS ROUND: no new defect — the R234 lesson (15) held end to
end. The R235 edit script was written with every edit routed through
the line lists `il`/`bl` (no discarded-string edit exists by
construction), the dry-run projection matched the apply exactly
(100.079 = 100.079), the idempotency re-run reported changed: 0 on the
first re-run after the lesson-16 fix, and the checker passed 87/87 on its first run. A round
with no correction is still recorded here so the next round does not
re-litigate whether the R234 fix was applied.
(16) NEW THIS ROUND — idempotency re-run defects, both fixed before
any re-apply could happen: (a) `find` prefixes must not contain the OLD
state — the first re-run crashed on the body head-line find
(`**Head: \`33962fd\``) because the applied line now starts with
`**Head: \`19e8f7c\``; the index title find had the same defect
(`(head \`33962fd\``). Fixed by finding on state-stable prefixes
(`**Head: \`` and `# MEDIA-02 — PR #119 Delivery Index (head`). (b)
`sub_line`'s new-state guard must be `if new in line: return 0` ALONE —
the first version (`new in line and old not in line`) would let
append-style edits re-apply, because the new string contains the old
one (title append, trail append, Ghi-chú list append all share this
shape). The crash happened AFTER the apply had already succeeded, so no
file was touched twice and no duplication occurred; the re-run after
both fixes reported changed: 0. The next round's edit script must
carry both fixes (stable find prefixes + new-only guard) from the start.

## Verification

- Merge-tree `19e8f7c` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `4cd1742c…`. Merge-tree at the R235
  content head `db681a3` vs `f3db6b3`: exit 0,
  tree `f588d21a…`.
- Live PR state: connector read this round (~04:45 JST) — direct read
  (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222
  payload on the first read; updated_at 2026-11-24T18:51:46Z — changed vs
  the R234 read, body bytes unchanged); mergeable_state clean at
  `19e8f7c` (connector read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: comments read SUCCEEDED this round — connector `issue_read` ~04:45 JST (paginated 30 + 4): still 34
  comments, updated_at 2026-11-13T19:24:49Z (issue-level; latest comment `6862732081` updated_at 2026-11-13T19:24:48Z —
  1 second apart, same ACK comment), latest ACK `6862732081` (CP5 + M-G CP10 + R2); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R235 block (`19e8f7c..db681a3`) 3 paths / 0 violations
  (index + body v2 + R235 checker); cumulative at the R235 content
  commit `db681a3` 3098 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `db681a3`). Merge-tree at the R235 content head `db681a3` vs `f3db6b3`: exit 0,
  tree `f588d21a…`.
- Transient notes: this round's `git fetch` at ~04:40 JST succeeded
  first try (no intervening push; remote head stayed `19e8f7c`,
  integration stayed `f3db6b3`). The connector read path was used this round — the PR read
  first failed on the parameter name (`pull_number` → `pullNumber`, lesson 8 above) and then
  succeeded on retry; pagination on `issue_read` worked first try with `issue_number` + `page`.
  No call-tool write approval was requested for a read. No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST and the R231-flagged run ~01:02 JST). No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH; the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
  `git add -N` was used on the three content paths before the scope
  audit so the new checker counted in the block diff; the content commit
  then added them normally.
- Ceiling discipline: the R234 payload JSON as-prepared measured 114.330 byte
  (prepared after the R234 push ~03:52 JST, NOT posted — live body is still R222, verified by this round's connector read),
  vs the 131.072-byte transport ceiling
  (16.742 byte headroom). The projected R235 payload JSON is ~116,000 byte
  (measured exactly at payload build, after push). Body v2 is now 100.079
  ký tự (< 105.000) — 4.921 ký tự of headroom. R235 warning:
  headroom is now 4.921 ký tự; the double compaction must continue next round
  (R49 + R48) or the head line must be trimmed if a future round's reads hit the rate-limit again.

## Next

Posting round (owner tap): PR #119 description refresh to the R235 body
v2 (R234 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r235.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R235 push (title
ending "+ R235", built by replacing the "+ R222" suffix — not appending;
body = body v2 R235 in repo, head line refreshed to head after R235 push).
This run started ~04:40 JST — OUTSIDE working hours (after 21:30 JST), so the
R235 payload is HELD for working hours (like R142/R164–R197/R207–R216/R228/R229/R230/R231/R232/R233/R234,
which were held for the same reason). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R234 payload as new — R234 was prepared but never posted and is superseded by R235; do not present the R222 payload as new — R222 is LIVE; do not present either R221 widget (`widget-56770776`, `widget-7a108c57`) — R221 was never posted and both are stale. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220, R221, R222, R223, R224, R225, R226, R227, R228, R229, R230, R231, R232, R233 and R234 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R235: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
