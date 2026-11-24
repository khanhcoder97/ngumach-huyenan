# MEDIA-02 — PR #119 Body Restructure R237: delivery index + body v2 coverage to `6db62e0`

Date: 2026-11-25 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `6db62e0` (PR119 BODY RESTRUCTURE R236 report). Content commit: `5b80666`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R237 does

R236 left two disclosed gaps: the delivery index covered 661 commits to
`d5f1db3`; R236's own 2 commits were to fold in at R237 — and the R236
payload was prepared but NOT posted (live body still R222). The R236
payload (`pr119_update_body_v2_r236.json`, body 99.880 ký tự, sha
`ddbd03d1`, JSON 113.600 byte < trần 131.072 — còn 17.472 byte, bản giữ tại
`.bak-prepost-20261124` — sha256 `8c36f72d…`, main + .bak byte-identical,
verified this round: the payload body differs from the repo body v2 at
`6db62e0` in exactly the head line (line 5) only, as designed) was
prepared after the R236 push ~06:01 JST and is HELD for working hours
(run started outside working hours, before 09:00 JST); it is superseded by
R237. R222 was posted live 2026-11-24 ~16:16 JST, replacing R140. No new
Codex/owner direction has been verified on issue #116: the comments read
SUCCEEDED this round (connector `issue_read` ~06:40 JST, paginated 30 + 4:
still 34 comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081`
(CP5 + M-G CP10 + R2); no new direction since Gói 39 (`6815238814`).

Fresh derivation at `6db62e0` (~06:40 JST): `git rev-list --count
cf17178..6db62e0` = 663 commits, `git diff --name-only` = 3103 files,
`--shortstat` = 314028 insertions, 0 deletions — agreeing exactly with
the connector PR read. `git merge-tree --write-tree` `6db62e0` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `3500a876…`. No re-fetch
was needed before applying: the run fetched at ~06:40 JST (the run start)
and the remote head was still `6db62e0`, integration still `f3db6b3` — no
intervening push; the connector read ~06:40 JST independently confirmed
head `6db62e0`. The live PR read this round (~06:40 JST,
`pull_request_read` method `get`): title ends "+ R222", head `6db62e0`,
663 commits / 3103 files / +314028, mergeable null — GitHub computing at
read time — / mergeable_state clean at `6db62e0`, live body 103.023 ký tự,
sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222 payload on the first
read, no resync needed this round —, updated_at 2026-11-24T21:00:21Z —
changed from the R236 read (19:58:36Z) because the R236 push updated the
head; the body bytes are unchanged.

R237 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  title head refreshed to `6db62e0`; milestone lines refreshed to head
  `6db62e0` (663 commits / 3103 files / 314028 additions; the fresh git
  derivation at `6db62e0`, the fresh connector PR read ~06:40 JST, and
  the merge-tree cross-check at `6db62e0` are cited, with the live body
  R222 read back byte-exact this round — 0 U+FFFD, no resync needed);
  delta `539feb0..6db62e0`: 2 paths, 708 insertions, 0 deletions);
  one row appended — PR119 BODY RESTRUCTURE R236 (`539feb0`/`6db62e0`),
  recording that its payload was prepared after the R236 push (99.880 ký
  tự, sha `ddbd03d1`; JSON 113.600 byte < trần 131.072 — còn 17.472 byte,
  bản giữ tại `.bak-prepost-20261124` — sha256 `8c36f72d…`) and then NOT
  posted (live body still R222 as read this round ~06:40 JST);
  no separate ACK for R236.
  The index now covers every block through `6db62e0`; R237's own 2
  commits fold in at the next index update (R238), disclosed in the index
  itself. The R237 note was appended after the R236 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `6db62e0` · 663 · 3103 (with the fresh git derivation at `6db62e0`,
  the fresh connector PR read ~06:40 JST, and the fresh merge-tree
  cross-check at `6db62e0`), plus the R236 paragraph in "Khối mới nhất"
  (270 ký tự text + 1 line break = 271 ký tự, marked chưa đăng — payload
  prepared, live body still R222) and the R237 note. The stale index
  reference in "Về bản mô tả này" (head `d5f1db3`) is also fixed to
  `6db62e0`, the "lượt cập nhật này" sentence is advanced R236 → R237
  AND corrected (see ĐÍNH CHÍNH below), and the compaction trail gains
  "R237 đã gọn thêm các đoạn R47 + R46." (37 ký tự). The title line is
  extended to R236 (APPENDED, not replaced — see the R176 robustness
  note; the append measures 30 ký tự). Compaction (R236 warning —
  applied with a measured correction): the R47 + R46 paragraphs (504 and
  504 ký tự — measured this round) are collapsed to one 207-ký-tự compact
  line each (full detail stays in the delivery index; the R76–R80 template
  measures 208, the R47/R46 lines measure 207 — the checker asserts
  < 400, not an exact 208) — the new R236 paragraph was 271 ký tự, so the
  body is 99.606 ký tự — net −218 vs R236 despite the new R236 paragraph,
  the 37-ký-tự trail append and the 30-ký-tự title append, headroom 5.394
  ký tự. The dry-run first projected 99.606 ký tự and the apply wrote
  exactly that — measure, then trim, then apply; the head line grew
  1.028 → 1.061 ký tự (+33, measured — see lesson 17).
  Paragraph order: the R236 paragraph sits directly after R235
  (ascending full-paragraph order R166..R236), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R237 (owner tap) — the R222 body v2 now live is the base;
  only the R236 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r237_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R236 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R236 and R237 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R236 (120 compact lines R46–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 99.606 ký tự),
  a check that the R236 paragraph sits directly after R235
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R236 note clean).
  New this round: the R235-row guard (cumulative must be 3101,
  re-derived from git at `539feb0`), the R236-row guard (cumulative must
  cite 3104 — 3103 at `6db62e0` + 1 new checker in the R237 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R237, range R47–R165, list complete through R236, no double slash),
  the "lượt cập nhật này" sentence correction guard (full corrected
  sentence present; the defective "chính R235"/"chính R236" forms absent),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 92/92**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R237_VALIDATION_20261125.json`).
  The checker passed on its FIRST run this round in the exact pre-commit
  tree state (no correction needed — like R236's first-run 89/89 pass). The
  checker was written fresh (not sed-copied from R236) with the full COVER
  SHA verified intact (definition + docstring, both
  `6db62e048ecf0cae3951a02dc63453ed7dfa181b` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (19 `6db62e0` hits — the cover
  value, in the definition, docstring, checks and the R236-row guard
  string citing "3103 at 6db62e0", legitimate; 4 `d5f1db3` (docstring +
  R235-row guard citing "3100 at d5f1db3"), 4 `539feb0` (docstring +
  row-convention tuple R235 + "index has row sha" check), 3 `db681a3` (docstring +
  row-convention tuple R234), 3 `b50891a` (docstring +
  row-convention tuple R233 + R233-row guard citing "3094 at 33962fd"),
  6 `233f0b5` (docstring + row-convention tuple R232 + R232-row guard
  citing "3092 at 233f0b5"), 5 `33962fd` (docstring + R233-row guard),
  5 `29727d4` (docstring + R231-row guard citing "3088 at 29727d4"),
  all legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 99.606 ký tự and the apply wrote on
  the first attempt at 99.606 ký tự, with 5.394 ký tự of headroom; the idempotency re-run
  after apply reports already-applied changed: 0 — verified (the re-run
  reported changed: 0 on the first re-run; no file was touched twice, no
  duplication).
  No correction was needed before the content commit this round: the edit
  script applied cleanly on its first run (dry-run 99.606 = apply
  99.606; idempotency re-run changed: 0 on the first re-run), unlike R233's lost title-head edit — the R233 lesson (15) held, every edit
  routes through the line lists `il`/`bl`. The documents were
  correct after the fix; the checker passed 92/92 on its first run
  against the applied tree (and again on a second invocation in the same
  pre-commit tree to write the repo validation JSON — same 92/92 result,
  no correction in between). The R236 row's cumulative figure was drafted
  as 3104 (3103 at `6db62e0` + 1 new checker) and the true diff at the
  R237 content commit is 3104 — verified by
  `git diff --name-only cf17178..5b80666` = 3104 after the content commit.
  `git status --porcelain` after the content commit showed only the
  intended validation JSON untracked — no leftover edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R236's committed content this round other than the
  sentence correction below: R236's committed content verified correct —
  the committed index at `6db62e0` carries the R234 row at cumulative 3098
  (re-derived by the new checker from git at `db681a3`) and the R235 row at 3101
  (re-derived from git at `539feb0`); no uncommitted
  working-tree fix was left behind by R236 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## ĐÍNH CHÍNH R237 — câu "lượt cập nhật này" trong body v2 bản R236

The R236 body v2 file (committed at `539feb0`) wrote: "R236 (lượt cập
nhật này) đã gộp 2 commit của R235 vào index; 2 commit của chính R235
sẽ gộp ở lần cập nhật index tiếp theo." The second clause is wrong:
R235's 2 commits were already folded into the index BY R236 itself, so
"2 commit của chính R235 sẽ gộp ở lần cập nhật index tiếp theo" can
never be true after R236. The R236 checker only asserted the presence
of "R236 (lượt cập nhật này)", so the second clause slipped through
unchecked — the same partial-advance shape as the R233 lost title-head
edit (an edit that advances only the first occurrence). R237 advances
the sentence properly: "R237 (lượt cập nhật này) đã gộp 2 commit của
R236 vào index; 2 commit của chính R237 sẽ gộp ở lần cập nhật index
tiếp theo." The correction is recorded here, in the R236 index row, and
in the R237 note line; the new checker asserts the full corrected
sentence and the absence of the defective "chính R235"/"chính R236"
forms, so the defect class is now guarded. (History check: the sentence
at R233/R234/R235 heads was correct in the same shape — "chính R233",
"chính R234", "chính R235" each naming the round itself — so the defect
was introduced by R236's advance, not inherited.)

## R237 robustness note — headroom now 5.394 chars

The R236 warning left 5.176 ký tự of headroom, so this round compacted
TWO paragraphs (R47 + R46, 504 + 504 ký tự → 207 each) before adding the new R236 paragraph
(271 ký tự). The body is now 99.606 ký tự — net −218 vs R236 — with
5.394 ký tự of headroom. The double compaction bought back 594 ký tự against
the 271-ký-tự new paragraph, and the head line grew 33 ký tự, so the net recovery
is −218 even after the 37-ký-tự trail append and the 30-ký-tự title append.
The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R238 warning: headroom is 5.394 ký tự; compact R45 + R44 next (or the head line
grows again if a future round's reads hit the rate-limit — the honest disclosure
is the variable cost, not the compaction).
At the current net −218/round the margin is recovering,
but only while the double compaction continues (full paragraphs remaining R166..R236 = 71;
compact block R46–R165 = 120 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (99.606 projected; apply wrote 99.606 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236).
The title append measured 30 chars, not the hand-counted 28 — the append string is
" + PR119 BODY RESTRUCTURE R236" (space, plus, space, ...), and the
net −218 matched only because the measured projection was trusted over the hand-count;
a wrong hand-count must never be written over a
measured projection. (2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236 — the R236 row's 3104 was verified post-commit by git
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
different versions of the same payload — the R236 payload's main file and its `.bak-prepost-20261124/` copy
were verified byte-identical this round (sha256 `8c36f72d…`, 113.600 byte) right after the late build;
a payload backup the authoring round made must be verified, not re-claimed — R237 verified the R236 payload's
body sha (`ddbd03d1`) against the repo body v2 + head-line refresh (99.880 ký tự) and recorded it as prepared
but NOT posted, since the live body read this round is still R222. Note: the `.bak` lives INSIDE the
directory `.bak-prepost-20261124/` (`.bak-prepost-20261124/pr119_update_body_v2_r236.json`), not as a
sibling file — this round located it inside the directory on the first check; a missing sibling file is not a missing
backup — check the directory first.
(7) An `updated_at` that DOES NOT move while the body sha stays means no push touched the PR since the last read — the PR read this
round shows updated_at 2026-11-24T21:00:21Z, changed from the R236 read (19:58:36Z) because the R236 push updated the head; the body sha is unchanged
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
assignment (R237) and the R219-blocked precedent (a blocked run stops; the next scheduled run retries cleanly).
No execution-risk flag on any git/script command this round.
(11) Mergeable_state is a point-in-time read, not a stable property of the head: the R236 payload's own head line
(read ~06:01 JST) said mergeable_state unstable at `6db62e0`; this round's fresh
read ~06:40 JST says mergeable_state clean at `6db62e0` — the honest wording is the fresh read, not the payload's older one.
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
(the checker ran once this round, pre-commit, and passed 92/92, writing
the validation JSON to the repo path; no re-run was done after the
content commit, and none is needed — the report commit below adds the
validation JSON as its second file).
(14) The compact-line count and the per-round loop range can drift apart
by one: the "Ghi chú" range text and the loop range name the block's
upper rounds (R47–R165), but the block itself extends one round lower
(R46–R165 = 120 lines) because each round compacts TWO paragraphs while
the range text advances by the pair's upper round only — R236 had the
same shape (118 lines, loop R48–R165). The checker must assert the TRUE
block count (120) and loop the TRUE block range (R46–R165), not the
range text; the range text follows its own convention and is asserted
separately as "R47–R165".
(15) The R236 lesson (16) held end to
end. The R237 edit script was written with every edit routed through
the line lists `il`/`bl` (no discarded-string edit exists by
construction), the dry-run projection matched the apply exactly
(99.606 = 99.606), the idempotency re-run reported changed: 0 on the
first re-run after apply, and the checker passed 92/92 on its first run. A round
with no correction is still recorded here so the next round does not
re-litigate whether the R236 fix was applied.
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
(17) NEW THIS ROUND — the hand-count of the body delta was off by one
(−219 hand-counted vs −218 measured): inserting a paragraph adds its
line break too, so a 270-char paragraph adds 271 chars to the file.
The R236 report's "271 ký tự" paragraph figure already counts the line
break the same way, so the convention is consistent — the paragraph is
recorded as 271 ký tự and the line-break accounting is stated here, not
treated as a defect. The head-line delta was measured +33 chars (1.028
→ 1.061), not hand-counted: the old updated_at parenthetical
("không đổi từ lần đọc R235, body không đổi") is 33 chars shorter than
the new one ("đổi từ lần đọc R236 (19:58:36Z) do push R236 cập nhật
head, body không đổi") — trust the measured projection (dry-run 99.606 =
apply 99.606), never the hand-count. The R236 checker was also re-run
once after the R237 content commit as a cross-check and failed 80/89 BY
DESIGN — it asserts the pre-commit tree and the old cover head (the 9
failures are exactly the cover-dependent checks: index header, milestone
sha, counts, body head line, body index reference, R236 update note, and
3 more); that failure is expected, not a defect, and no action follows
from it.

## Verification

- Merge-tree `6db62e0` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `3500a876…`. Merge-tree at the R237
  content head `5b80666` vs `f3db6b3`: exit 0,
  tree `708775b7…`.
- Live PR state: connector read this round (~06:40 JST) — direct read
  (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222
  payload on the first read; updated_at 2026-11-24T21:00:21Z — changed from
  the R236 read, body bytes unchanged); mergeable_state clean at
  `6db62e0` (connector read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: comments read SUCCEEDED this round — connector `issue_read` ~06:40 JST (paginated 30 + 4): still 34
  comments, updated_at 2026-11-13T19:24:49Z (issue-level; latest comment `6862732081` updated_at 2026-11-13T19:24:48Z —
  1 second apart, same ACK comment), latest ACK `6862732081` (CP5 + M-G CP10 + R2); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R237 block (`6db62e0..5b80666`) 3 paths / 0 violations
  (index + body v2 + R237 checker); cumulative at the R237 content
  commit `5b80666` 3104 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `5b80666`). Merge-tree at the R237 content head `5b80666` vs `f3db6b3`: exit 0,
  tree `708775b7…`.
- Transient notes: this round's `git fetch` at ~06:40 JST succeeded
  first try (no intervening push; remote head stayed `6db62e0`,
  integration stayed `f3db6b3`). The connector read path was used this round — the PR read
  succeeded first try with `pullNumber` (lesson 8 carried: no `pull_number` retry needed this round);
  pagination on `issue_read` worked first try with `issue_number` + `page`.
  No call-tool write approval was requested for a read. No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST and the R231-flagged run ~01:02 JST). No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH; the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
  `git add -N` was NOT needed this round: the scope audit runs on commits
  (base..head), not the working tree, so the new checker counted in the
  block diff via the content commit itself.
- Ceiling discipline: the R236 payload JSON as-prepared measured 113.600 byte
  (prepared after the R236 push ~06:01 JST, NOT posted — live body is still R222, verified by this round's connector read),
  vs the 131.072-byte transport ceiling
  (17.472 byte headroom). The projected R237 payload JSON is ~115,000 byte
  (measured exactly at payload build, after push). Body v2 is now 99.606
  ký tự (< 105.000) — 5.394 ký tự of headroom. R237 warning:
  headroom is now 5.394 ký tự; the double compaction must continue next round
  (R45 + R44) or the head line must be trimmed if a future round's reads hit the rate-limit again.

## Next

Posting round (owner tap): PR #119 description refresh to the R237 body
v2 (R236 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r237.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R237 push (title
ending "+ R237", built by replacing the "+ R236" suffix — not appending;
body = body v2 R237 in repo, head line refreshed to head after R237 push).
This run started ~06:40 JST — OUTSIDE working hours (before 09:00 JST), so the
R237 payload is HELD for working hours (like R142/R164–R197/R207–R216/R228/R229/R230/R231/R232/R233/R234/R235/R236,
which were held for the same reason). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R236 payload as new — R236 was prepared but never posted and is superseded by R237; do not present the R222 payload as new — R222 is LIVE; do not present either R221 widget (`widget-56770776`, `widget-7a108c57`) — R221 was never posted and both are stale. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220, R221, R222, R223, R224, R225, R226, R227, R228, R229, R230, R231, R232, R233, R234, R235 and R236 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R237: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
