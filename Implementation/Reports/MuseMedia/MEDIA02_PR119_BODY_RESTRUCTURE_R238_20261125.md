# MEDIA-02 — PR #119 Body Restructure R238: delivery index + body v2 coverage to `7bf9212`

Date: 2026-11-25 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `7bf9212` (PR119 BODY RESTRUCTURE R237 report). Content commit: `e79db7b` (amended from `3e80d80` before push — see below).
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R238 does

R237 left two disclosed gaps: the delivery index covered 663 commits to
`6db62e0`; R237's own 2 commits were to fold in at R238 — and the R237
payload was prepared but NOT posted (live body still R222). The R237
payload (`pr119_update_body_v2_r237.json`, body 99.629 ký tự, sha
`48304f99`, JSON 113.223 byte < trần 131.072 — còn 17.849 byte, bản giữ tại
`.bak-prepost-20261124` — sha256 `80582585…`, main + .bak byte-identical,
verified this round: the payload body differs from the repo body v2 at
`7bf9212` in exactly the head line (line 5) only, as designed) was
prepared after the R237 push ~06:53 JST and is HELD for working hours
(run started outside working hours, before 09:00 JST); it is superseded by
R238. R222 was posted live 2026-11-24 ~16:16 JST, replacing R140. No new
Codex/owner direction has been verified on issue #116: the comments read
SUCCEEDED this round (connector `issue_read` ~07:40 JST, paginated 30 + 4:
still 34 comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081`
(CP5 + M-G CP10 + R2); no new direction since Gói 39 (`6815238814`).

Fresh derivation at `7bf9212` (~07:40 JST): `git rev-list --count
cf17178..7bf9212` = 665 commits, `git diff --name-only` = 3106 files,
`--shortstat` = 315400 insertions, 0 deletions — agreeing exactly with
the connector PR read. `git merge-tree --write-tree` `7bf9212` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `1fb3e6a4…`. No re-fetch
was needed before applying: the run fetched at ~07:40 JST (the run start)
and the remote head was still `7bf9212`, integration still `f3db6b3` — no
intervening push; the connector read ~07:40 JST independently confirmed
head `7bf9212`. The live PR read this round (~07:40 JST,
`pull_request_read` method `get`): title ends "+ R222", head `7bf9212`,
665 commits / 3106 files / +315400, mergeable null — GitHub computing at
read time — / mergeable_state clean at `7bf9212`, live body 103.023 ký tự,
sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222 payload on the first
read, no resync needed this round —, updated_at 2026-11-24T21:52:50Z —
changed from the R237 read (21:00:21Z) because the R237 push updated the
head; the body bytes are unchanged.

R238 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  title head refreshed to `7bf9212`; milestone lines refreshed to head
  `7bf9212` (665 commits / 3106 files / 315400 additions; the fresh git
  derivation at `7bf9212`, the fresh connector PR read ~07:40 JST, and
  the merge-tree cross-check at `7bf9212` are cited, with the live body
  R222 read back byte-exact this round — 0 U+FFFD, no resync needed);
  delta `5b80666..7bf9212`: 2 paths, 755 insertions, 0 deletions);
  one row appended — PR119 BODY RESTRUCTURE R237 (`5b80666`/`7bf9212`),
  recording that its payload was prepared after the R237 push (99.629 ký
  tự, sha `48304f99`; JSON 113.223 byte < trần 131.072 — còn 17.849 byte,
  bản giữ tại `.bak-prepost-20261124` — sha256 `80582585…`) and then NOT
  posted (live body still R222 as read this round ~07:40 JST);
  no separate ACK for R237.
  The index now covers every block through `7bf9212`; R238's own 2
  commits fold in at the next index update (R239), disclosed in the index
  itself. The R238 note was appended after the R237 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `7bf9212` · 665 · 3106 (with the fresh git derivation at `7bf9212`,
  the fresh connector PR read ~07:40 JST, and the fresh merge-tree
  cross-check at `7bf9212`), plus the R237 paragraph in "Khối mới nhất"
  (270 ký tự text + 1 line break = 271 ký tự, marked chưa đăng — payload
  prepared, live body still R222) and the R238 note. The stale index
  reference in "Về bản mô tả này" (head `6db62e0`) is also fixed to
  `7bf9212`, the "lượt cập nhật này" sentence is advanced R237 → R238,
  and the compaction trail gains
  "R238 đã gọn thêm các đoạn R45 + R44." (37 ký tự). The title line is
  extended to R237 (APPENDED, not replaced — see the R176 robustness
  note; the append measures 30 ký tự). Compaction (R237 warning —
  applied with a measured correction): the R45 + R44 paragraphs (504 and
  504 ký tự — measured this round) are collapsed to one 207-ký-tự compact
  line each (full detail stays in the delivery index; the R76–R80 template
  measures 208, the R45/R44 lines measure 207 — the checker asserts
  < 400, not an exact 208) — the new R237 paragraph was 271 ký tự, so the
  body is 99.355 ký tự — net −251 vs R237 despite the new R237 paragraph,
  the 37-ký-tự trail append, the 30-ký-tự title append and the 5-ký-tự
  Ghi-chú list append ("/R237"), headroom 5.645
  ký tự. The dry-run first projected 99.355 ký tự and the apply wrote
  exactly that — measure, then trim, then apply; the head line stayed
  1.061 ký tự (delta 0, measured — see lesson 18).
  Paragraph order: the R237 paragraph sits directly after R236
  (ascending full-paragraph order R166..R237), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R238 (owner tap) — the R222 body v2 now live is the base;
  only the R237 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r238_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R237 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R237 and R238 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R237 (122 compact lines R44–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 99.355 ký tự),
  a check that the R237 paragraph sits directly after R236
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R237 note clean).
  New this round: the R236-row guard (cumulative must be 3104,
  re-derived from git at `5b80666`), the R237-row guard (cumulative must
  cite 3107 — 3106 at `7bf9212` + 1 new checker in the R238 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R238, range R45–R165, list complete through R237, no double slash),
  the "lượt cập nhật này" sentence correction guard (full corrected
  sentence present; the defective "chính R236"/"chính R237" forms absent),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 94/94**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R238_VALIDATION_20261125.json`).
  The checker passed on its FIRST run this round in the exact pre-commit
  tree state (no correction needed — like R237's first-run 92/92 pass). The
  checker was generated from R237 by a transform script (not sed-copied)
  with the full COVER SHA verified intact (definition + docstring, both
  `7bf9212b404f394a40237c103b88352f592901dd` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (18 `7bf9212` hits — the cover
  value, in the definition, docstring, checks and the R237-row guard
  string citing "3106 at 7bf9212", legitimate; 3 `6db62e0` (R237-row guard
  comment + check name citing "3103 at 6db62e0"), 4 `5b80666` (docstring +
  row-convention tuple R236 + "index has row sha" check), 3 `d5f1db3`
  (docstring + R235-row guard citing "3100 at d5f1db3"), 3 `539feb0`
  (docstring + row-convention tuple R235), 3 `db681a3` (docstring +
  row-convention tuple R234), 3 `b50891a` (docstring +
  row-convention tuple R233), 5 `233f0b5` (docstring + row-convention
  tuple R232 + R232-row guard citing "3092 at 233f0b5"), 5 `33962fd`
  (docstring + R233-row guard citing "3094 at 33962fd"), 4 `29727d4`
  (docstring + R231-row guard citing "3088 at 29727d4"), 3 `9861875`
  (docstring + R230-row guard citing "3085 at 9861875"), 3 `8310e5d`
  (docstring + R229-row guard citing "3082 at 8310e5d"), 3 `9890c75`
  (docstring + R228-row guard citing "3079 at 9890c75"), 3 `dbee5c5`
  (docstring + R227-row guard citing "3076 at dbee5c5"), 3 `556d3ec`
  (docstring + R226-row guard citing "3073 at 556d3ec"), 3 `2861100`
  (docstring + R225-row guard citing "3070 at 2861100"), 3 `1700859`
  (docstring + R224-row guard citing "3067 at 1700859"), 3 `e07fe1e`
  (docstring + R223-row guard citing "3064 at e07fe1e"), 3 `37ea7ad`
  (docstring + R222-row guard citing "3061 at 37ea7ad"), 2 `a38b714`
  (docstring + R221-row guard citing "3058 at a38b714"), 2 `c38a4dc`
  (docstring + R220-row guard citing "3055 at c38a4dc"), 2 `8f8b504`
  (docstring + R219-row guard citing "3052 at 8f8b504"), 2 `a74e9f4`
  (docstring + R218-row guard citing "3049 at a74e9f4"), 2 `0a4d05a`
  (docstring + R217-row guard citing "3046 at 0a4d05a"), 2 `0de54fb`
  (docstring + R216-row guard citing "3043 at 0de54fb"), 2 `1e564a2`
  (docstring + R215-row guard citing "3040 at 1e564a2"), 2 `3de99c9`
  (docstring + R214-row guard citing "3037 at 3de99c9"), all legitimate)
  after the run — the R69 sed-order copy defect (mangled full COVER SHA)
  was avoided by construction. The edit script's budget check ran before
  any write (R166 lesson): the dry-run simulation projected 99.355 ký tự
  and the apply wrote on the first attempt at 99.355 ký tự, with 5.645 ký
  tự of headroom; the idempotency re-run after apply reports
  already-applied changed: 0 — verified (the re-run reported changed: 0
  on the first re-run; no file was touched twice, no duplication).
  No correction was needed before the content commit this round except the
  pre-push amend below: the edit script applied cleanly on its first run
  (dry-run 99.355 = apply 99.355; idempotency re-run changed: 0 on the
  first re-run), unlike R233's lost title-head edit — the R233 lesson (15)
  held, every edit routes through the line lists `il`/`bl`. The documents
  were correct after the fix; the checker passed 94/94 on its first run
  against the applied tree, writing the repo validation JSON in the same run
  (no second invocation was needed). The R237 row's cumulative figure was drafted
  as 3107 (3106 at `7bf9212` + 1 new checker) and the true diff at the
  R238 content commit is 3107 — verified by
  `git diff --name-only cf17178..e79db7b` = 3107 after the content commit.
  `git status --porcelain` after the content commit showed only the
  intended validation JSON untracked — no leftover edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R237's committed content this round: R237's committed content verified correct —
  the committed index at `7bf9212` carries the R235 row at cumulative 3101
  (re-derived by the new checker from git at `539feb0`) and the R236 row at 3104
  (re-derived from git at `5b80666`); no uncommitted
  working-tree fix was left behind by R237 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## Sửa trước push — content commit được amend (`3e80d80` → `e79db7b`)

Re-reading the generated checker before push found 3 comment/docstring-only
defects (no check logic affected): the docstring claimed the checker "passed
95/95" — wrong, the run is 94/94 (R238 adds a row guard + a loop entry =
+2 over R237's 92, not +3; the carried R236-row guard is not new — see
lesson 18); and two stale code comments (the Ghi-chú comment still said
"R158/R237, range R47-R165, list complete through R236" and the paragraph-order
comment still said "R236 after R235" — both R237 text, while the checks
themselves already assert R238/R45–R165/R237-after-R236 and passed). The
content commit was amended before push (same message, same 3 files); the
amend diff is exactly those 3 lines, the check names are byte-identical
before/after, the cumulative diff stays 3107, and the merge-tree was
re-run at the amended head. The validation JSON (94/94) was generated by
the pre-amend checker run; the amend changed no check logic, so the
validation output is unaffected — and the checker was NOT re-run after the
amend (by design: the working-tree guard fails post-commit runs). This is
the pre-push correction the R237 "lượt cập nhật này" defect did NOT get —
that one shipped and needed a ĐÍNH CHÍNH in the next round.

## R238 robustness note — headroom now 5.645 chars

The R237 warning left 5.394 ký tự of headroom, so this round compacted
TWO paragraphs (R45 + R44, 504 + 504 ký tự → 207 each) before adding the new R237 paragraph
(271 ký tự). The body is now 99.355 ký tự — net −251 vs R237 — with
5.645 ký tự of headroom. The double compaction bought back 594 ký tự against
the 271-ký-tự new paragraph, and the head line stayed flat (delta 0), so the net recovery
is −251 even after the 37-ký-tự trail append, the 30-ký-tự title append and
the 5-ký-tự Ghi-chú list append.
The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R239 warning: headroom is 5.645 ký tự; compact R43 + R42 next (or the head line
grows again if a future round's reads hit the rate-limit — the honest disclosure
is the variable cost, not the compaction).
At the current net −251/round the margin is recovering,
but only while the double compaction continues (full paragraphs remaining R166..R237 = 72;
compact block R44–R165 = 122 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (99.355 projected; apply wrote 99.355 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237).
The title append measured 30 chars, not the hand-counted 28 — the append string is
" + PR119 BODY RESTRUCTURE R237" (space, plus, space, ...), and the
net −251 matched only because the measured projection was trusted over the hand-count;
a wrong hand-count must never be written over a
measured projection. (2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237 — the R237 row's 3107 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — this round the re-run reported changed: 0 on the
first re-run after apply (no lost edit, unlike R233); the per-edit applied-delta accounting stays an identity on re-run instead of tripping on a stale hand-counted expectation.
(4) Append-style edits need the new-state check FIRST in `sub_once` too: the new trail string contains the old
string, so `old in text` stays true after apply — the R231 fix holds; this round's re-run confirmed changed: 0.
(5) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (6) Two backup locations can hold
different versions of the same payload — the R237 payload's main file and its `.bak-prepost-20261124/` copy
were verified byte-identical this round (sha256 `80582585…`, 113.223 byte) right after the late build;
a payload backup the authoring round made must be verified, not re-claimed — R238 verified the R237 payload's
body sha (`48304f99`) against the repo body v2 + head-line refresh (99.629 ký tự) and recorded it as prepared
but NOT posted, since the live body read this round is still R222. Note: the `.bak` lives INSIDE the
directory `.bak-prepost-20261124/` (`.bak-prepost-20261124/pr119_update_body_v2_r237.json`), not as a
sibling file — this round located it inside the directory on the first check; a missing sibling file is not a missing
backup — check the directory first.
(7) An `updated_at` that DOES NOT move while the body sha stays means no push touched the PR since the last read — the PR read this
round shows updated_at 2026-11-24T21:52:50Z, changed from the R237 read (21:00:21Z) because the R237 push updated the head; the body sha is unchanged
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
assignment (R238) and the R219-blocked precedent (a blocked run stops; the next scheduled run retries cleanly).
No execution-risk flag on any git/script command this round.
(11) Mergeable_state is a point-in-time read, not a stable property of the head: the R237 payload's own head line
(read ~06:53 JST) said mergeable_state unstable at `7bf9212`; this round's fresh
read ~07:40 JST says mergeable_state clean at `7bf9212` — the honest wording is the fresh read, not the payload's older one.
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
(the checker ran once this round, pre-commit, and passed 94/94, writing
the validation JSON to the repo path; no re-run was done after the
content commit, and none is needed — the report commit below adds the
validation JSON as its second file).
(14) The compact-line count and the per-round loop range can drift apart
by one: the "Ghi chú" range text and the loop range name the block's
upper rounds (R45–R165), but the block itself extends one round lower
(R44–R165 = 122 lines) because each round compacts TWO paragraphs while
the range text advances by the pair's upper round only — R237 had the
same shape (120 lines, loop R47–R165). The checker must assert the TRUE
block count (122) and loop the TRUE block range (R44–R165), not the
range text; the range text follows its own convention and is asserted
separately as "R45–R165".
(15) The R236 lesson (16) held end to
end. The R238 edit script was written with every edit routed through
the line lists `il`/`bl` (no discarded-string edit exists by
construction), the dry-run projection matched the apply exactly
(99.355 = 99.355), the idempotency re-run reported changed: 0 on the
first re-run after apply, and the checker passed 94/94 on its first run. A round
with no correction is still recorded here so the next round does not
re-litigate whether the R237 fix was applied.
(16) Carried from R235 — idempotency re-run defects, both fixed that round
before any re-apply could happen: (a) `find` prefixes must not contain the OLD
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
(17) Carried from R237 — the hand-count of the body delta was off by one
(−219 hand-counted vs −218 measured): inserting a paragraph adds its
line break too (+271 for a 270-char paragraph). The R237 report's "271
ký tự" paragraph figure already counts the line break the same way, so
the convention is consistent — record the paragraph as 271 ký tự and
the line-break accounting in the report, not as a defect. The R238 net
−251 was likewise measured, not hand-counted: the +5 Ghi-chú list
append ("/R237") is the term a hand-count would most likely miss.
(18) NEW THIS ROUND — the checker total is NOT the previous round's total
plus the number of new guards: R238 adds one row guard (R237 row) and one
row-convention loop entry (R236) = +2 over R237's 92, total 94/94 — the
generator's docstring first wrote 95/95 by counting the carried R236-row
guard as new. The carried guard existed in the R237 checker as "new this
round" and merely changes label in R238; re-derive the total from the
checker run itself (94/94 printed + validation JSON), never from an
assumed delta. The defect was caught by re-reading the generated checker
before push and fixed by amending the unpushed content commit (see "Sửa
trước push" above) — the same re-read that caught the two stale code
comments. A generator that writes the docstring must print the measured
total into it AFTER the run, or leave the total out of the docstring.
(19) NEW THIS ROUND — a connector call that fails on a wrong METHOD name
is not a failed read either: this round's first `issue_read` used method
`get_issue_comments` and the first `pull_request_read` used
`get_pull_request` — both rejected ("not in Muse's reviewed read-only
set"). The live tool catalog (`list-tools`) lists the read methods:
`issue_read` takes `get` / `get_comments` / `get_labels` / `get_parent` /
`get_sub_issues`; `pull_request_read` takes `get` / `get_diff` /
`get_status` / `get_files` / `get_commits` / `get_review_comments` /
`get_reviews` / `get_comments` / `get_check_runs`. Retries with
`get_comments` and `get` succeeded first try. Check the catalog before
assuming a read path is gone.

## Verification

- Merge-tree `7bf9212` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `1fb3e6a4…`. Merge-tree at the R238
  content head `e79db7b` vs `f3db6b3`: exit 0,
  tree `08bfd2f1…`.
- Live PR state: connector read this round (~07:40 JST) — direct read
  (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222
  payload on the first read; updated_at 2026-11-24T21:52:50Z — changed from
  the R237 read, body bytes unchanged); mergeable_state clean at
  `7bf9212` (connector read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: comments read SUCCEEDED this round — connector `issue_read` ~07:40 JST (paginated 30 + 4): still 34
  comments, updated_at 2026-11-13T19:24:49Z (issue-level; latest comment `6862732081` updated_at 2026-11-13T19:24:48Z —
  1 second apart, same ACK comment), latest ACK `6862732081` (CP5 + M-G CP10 + R2); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R238 block (`7bf9212..e79db7b`) 3 paths / 0 violations
  (index + body v2 + R238 checker); cumulative at the R238 content
  commit `e79db7b` 3107 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `e79db7b`). Merge-tree at the R238 content head `e79db7b` vs `f3db6b3`: exit 0,
  tree `08bfd2f1…`.
- Transient notes: this round's `git fetch` at ~07:40 JST succeeded
  first try (no intervening push; remote head stayed `7bf9212`,
  integration stayed `f3db6b3`). The connector read path was used this round — the PR read
  succeeded first try with `pullNumber` (lesson 8 carried: no `pull_number` retry needed this round);
  pagination on `issue_read` worked first try with `issue_number` + `page`.
  The first `issue_read`/`pull_request_read` calls used wrong method names
  (`get_issue_comments`/`get_pull_request`) and were rejected; retries with
  the catalog methods `get_comments`/`get` succeeded (lesson 19). No
  call-tool write approval was requested for a read. No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST and the R231-flagged run ~01:02 JST). No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH; the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
  `git add -N` was NOT needed this round: the scope audit runs on commits
  (base..head), not the working tree, so the new checker counted in the
  block diff via the content commit itself. The checker emits a
  `SyntaxWarning: invalid escape sequence '\`'` on its docstring (the
  `\`` sequences in the R235 lesson text) — warning only, same shape as
  the R237 checker file, `py_compile` exit 0, checks unaffected.
  The alignment synthesis file was refreshed by the nightly loop during
  this run (R221 lost to an expired card, R222 posted live 24 Nov) —
  consistent with the queue; no new direction.
- Ceiling discipline: the R237 payload JSON as-prepared measured 113.223 byte
  (prepared after the R237 push ~06:53 JST, NOT posted — live body is still R222, verified by this round's connector read),
  vs the 131.072-byte transport ceiling
  (17.849 byte headroom). The projected R238 payload JSON is ~115,000 byte
  (measured exactly at payload build, after push). Body v2 is now 99.355
  ký tự (< 105.000) — 5.645 ký tự of headroom. R238 warning:
  headroom is now 5.645 ký tự; the double compaction must continue next round
  (R43 + R42) or the head line must be trimmed if a future round's reads hit the rate-limit again.

## Next

Posting round (owner tap): PR #119 description refresh to the R238 body
v2 (R237 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r238.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R238 push (title
ending "+ R238", built by replacing the "+ R237" suffix — not appending;
body = body v2 R238 in repo, head line refreshed to head after R238 push).
This run started ~07:40 JST — OUTSIDE working hours (before 09:00 JST), so the
R238 payload is HELD for working hours (like R142/R164–R197/R207–R216/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237,
which were held for the same reason). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R237 payload as new — R237 was prepared but never posted and is superseded by R238; do not present the R222 payload as new — R222 is LIVE; do not present either R221 widget (`widget-56770776`, `widget-7a108c57`) — R221 was never posted and both are stale. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220, R221, R222, R223, R224, R225, R226, R227, R228, R229, R230, R231, R232, R233, R234, R235, R236 and R237 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R238: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
