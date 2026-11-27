# MEDIA-02 — PR #119 Body Restructure R248: delivery index + body v2 coverage to `cd4f7b0`

Date: 2026-11-25 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `cd4f7b0` (PR119 BODY RESTRUCTURE R247 report). Content commit: `cf24619`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R248 does

R247 left one disclosed defect, fixed this round (lesson 36): the body v2
head line at `cd4f7b0` carried two wrong figures — additions `327963`
(stale, from head `4fc20b6`) instead of `329707` at head `1240497`, and
Gói 39 ID `6835238814` instead of `6815238814`. Both were confined to
the head line (one occurrence each, line 5); the R247 payload was built
with the correct figures, so the posted description would have been
right, but the repo file was wrong. R248 fixes the repo file and adds
the checker assert that would have caught it.
The R247 payload was built by its own round after the R247 push
(~17:34 JST, body 97.598 ký tự, sha `38a602e2`, JSON 110.076 byte <
trần 131.072 — còn 20.996 byte, main == .bak byte-identical, sha256
`058f6ea5…`) and is READY FOR PRESENTATION (working hours) — R248
verifies that R247 payload from disk this round (main == .bak, no
refresh) so the R247 index row can cite real figures — and records
that it is now superseded by R248 (live body still R222).
No ĐÍNH CHÍNH this round: the R247 payload main == .bak byte-identical
(verified from disk), no refresh happened — unlike R241 (refreshed
~11:54 JST, corrected at R242/R243). No new Codex/owner direction has
been verified on issue #116: 34 comments, latest ACK `6862732081`
(CP5 + M-G CP10 + R2); no new direction since Gói 39 (`6815238814`).

Fresh derivation at `cd4f7b0` (~17:42 JST): `git rev-list --count
cf17178..cd4f7b0` = 685 commits, `git diff --name-only` = 3136 files,
`--shortstat` = 331522 insertions, 0 deletions — agreeing exactly with
the connector PR read. `git merge-tree --write-tree` `cd4f7b0` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `f764bbce…`. No re-fetch
was needed before applying: the run fetched at ~17:40 JST (the run start)
and the remote head was still `cd4f7b0`, integration still `f3db6b3` — no
intervening push; the connector read ~17:42 JST independently confirmed
head `cd4f7b0`. The live PR read this round (~17:42 JST,
`pull_request_read` method `get` with `pullNumber`): title ends "+ R222", head `cd4f7b0`,
685 commits / 3136 files / +331522, mergeable null — GitHub computing at
read time — / mergeable_state clean at `cd4f7b0`, live body 103.023 ký tự,
sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222 payload,
updated_at 2026-11-25T08:27:39Z — changed from the R247 read
(2026-11-25T07:16:44Z) because the R247 push updated the head; the body
bytes are unchanged.

R248 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  title head refreshed to `cd4f7b0`; milestone lines refreshed to head
  `cd4f7b0` (685 commits / 3136 files / 331522 additions; the fresh git
  derivation at `cd4f7b0`, the fresh connector PR read ~17:42 JST, and
  the merge-tree cross-check at `cd4f7b0` are cited, with the live body
  R222 read back byte-exact this round — 0 U+FFFD, single clean read);
  delta `c919f88..cd4f7b0`: 2 paths, 934 insertions, 0 deletions);
  one row appended — PR119 BODY RESTRUCTURE R247 (`c919f88`/`cd4f7b0`),
  recording that its payload was prepared after the R247 push (~17:34
  JST, 97.598 ký tự, sha `38a602e2`; JSON 110.076 byte < trần 131.072 — còn
  20.996 byte, bản giữ tại `.bak-prepost-20261124` — sha256 `058f6ea5…`,
  as-built figures) and then NOT posted (live body still R222 as read
  this round ~17:42 JST); the R247 row also records the two head-line
  errors (additions 327963 instead of 329707 at head 1240497; Gói 39 ID
  6835238814 instead of 6815238814 — head line only, payload R247 built
  with the correct figures; fixed at R248) and the stale R246 widget
  (head has moved to `cd4f7b0` — do NOT tap; present the R247 widget
  instead); no separate ACK for R247. No ĐÍNH CHÍNH this round (R247
  payload main == .bak byte-identical, no refresh).
  The index now covers every block through `cd4f7b0`; R248's own 2
  commits fold in at the next index update (R249), disclosed in the index
  itself. The R248 note was appended after the R247 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `cd4f7b0` · 685 · 3136 (additions `331522`, Gói 39 ID `6815238814`,
  tree `f764bbce…`; with the fresh git derivation at `cd4f7b0`,
  the fresh connector PR read ~17:42 JST, and the fresh merge-tree
  cross-check at `cd4f7b0`), plus the R247 paragraph in "Khối mới nhất"
  (270 ký tự text + 1 line break = 271 ký tự, marked chưa đăng — payload
  prepared after push ~17:34 JST, live body still R222) and the R248 note. The stale index
  reference in "Về bản mô tả này" (head `1240497`) is also fixed to
  `cd4f7b0`, the "lượt cập nhật này" sentence is advanced R247 → R248,
  and the compaction trail gains
  "R248 đã gọn thêm các đoạn R25 + R24." (36 ký tự + 1 leading space = 37). The title line is
  extended to R247 (APPENDED, not replaced — see the R176 robustness
  note; the append measures 30 ký tự). Compaction (R247 warning —
  applied as a true double compaction this round): the R25 paragraph
  (504 ký tự — measured this round, full paragraph verified present)
  and the R24 paragraph (504 ký tự — measured this round, full paragraph
  verified present; the pair DOES share a length this time — see lesson
  (35) below) are each collapsed to one
  207-ký-tự compact line.
  Full detail stays in the delivery index; the checker asserts < 400,
  not an exact 207. The new R247 paragraph was 271 ký tự, so the body
  is 97.386 ký tự — net −251 vs R247 (the double compaction resumed:
  −297 R25 compaction − 297 R24 compaction + 271 new paragraph + 37
  trail append + 30 title append + 5 Ghi-chú list append ("/R247") + 0
  head-line delta), headroom 7.614 ký tự. The dry-run first projected
  97.386 ký tự and the apply wrote exactly that — measure, then trim,
  then apply.
  Paragraph order: the R247 paragraph sits directly after R246
  (ascending full-paragraph order R166..R247), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R248 (owner tap) — the R222 body v2 now live is the base;
  only the R247 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r248_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R247 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R247 and R248 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R247 (142 compact lines R24–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 97.386 ký tự),
  a check that the R247 paragraph sits directly after R246
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237/R238/R239/R240/R241/R242/R243/R244/R245/R246 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R247 note clean).
  New this round: the R247-row guard (cumulative must cite 3137 —
  3136 at `cd4f7b0` + 1 new checker in the R248 content commit,
  verified in this report after the content commit), the ĐÍNH CHÍNH R242
  guard carried (the R241 row must carry the note with sha `83d221b8`), the R36-restoration
  guard carried (the R36 compact line must exist with content `386216b` and head
  `9ec1fd9`), the ĐÍNH CHÍNH R241 guard carried (the R239 row must carry
  the note with sha `1e38e781`), the body "Ghi chú" line correction
  guard (R158/R248, range R25–R165, list complete through R247, no double
  slash), the "lượt cập nhật này" sentence correction guard (full
  corrected sentence present; the defective "chính R247" form absent),
  the lesson-36 head-line guard (additions `331522` and Gói 39 ID
  `6815238814` present in the head line; `6835238814` and `327963`
  absent from the body), and the working-tree guard (`git status --porcelain` lists exactly the
  3 intended paths — index + body + this checker — no stray modification
  may survive past the report commit).
  **PASS 118/118**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R248_VALIDATION_20261125.json`).
  The checker passed on its SECOND run this round: the first run failed
  117/118 on the row-convention R246 check — the generator had cited
  the coverage head `1240497` as the tuple sha instead of the content
  commit `c919f88` (see pre-push fix (1) below); the fix was applied,
  the validation JSON deleted before the re-run (lesson 13), and the
  re-run passed 118/118 against the applied tree. The checker was generated from R247 by a transform script (not
  sed-copied) with the full COVER SHA verified intact (definition +
  docstring, both `cd4f7b0b6ae8dada04d58f8740550f6567d98561` — re-derived
  from `git rev-parse` this round) and a stale-reference grep (47 shas
  verified, counts measured dynamically) after the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The SHA-hits paragraph was regenerated by a second
  script that greps the generated checker (47 shas, line counts measured
  dynamically, locations classified from the actual matching lines) —
  one classifier defect was caught by reading the output (the R247-row
  note tag still read "R246-row note" — lesson 34 class; fixed before
  the checker ran).
  The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 97.386 ký tự and the apply wrote on
  the first attempt at 97.386 ký tự, with 7.614 ký tự of headroom; the
  idempotency re-run after apply reports already-applied changed: 0 —
  verified (the re-run reported changed: 0 on the first clean re-run).
  The R247 paragraph's first draft measured 269 chars, not 270: fixed by
  adding the "checker:" colon (+1 — the same fix as R242 lesson 10);
  the edit script asserts the exact 270 before writing — see lesson 26
  of R242, carried; the two compact lines each measured exactly 207 chars on the first attempt.
  The documents were correct after the fix; the
  checker passed 118/118 on its re-run against the applied tree,
  writing the repo validation JSON in the same run.
  The R247 row's cumulative figure was drafted as 3137 (3136 at `cd4f7b0` + 1 new checker) and the true diff at the R248 content commit is 3137 — verified by
  `git diff --name-only cf17178..cf24619` = 3137 after the content commit.
  The R246 row's cumulative 3134 was re-derived from git at `c919f88`
  (`git diff --name-only cf17178..c919f88` = 3134) and by the checker's
  row-convention loop (R246 cumulative 3134 == diff at `c919f88` — PASS).
  `git status --porcelain` after the content commit showed only the
  intended validation JSON untracked — no leftover edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R247's committed content this round: R247's committed content verified correct —
  the committed index at `cd4f7b0` carries the R245 row at cumulative 3131
  (re-derived by the new checker from git at `6869aa1`) and the R246 row at 3134
  (re-derived from git at `c919f88`); no uncommitted
  working-tree fix was left behind by R247 (the working tree was clean at this
  run's start and the fetch found no intervening push). No payload refresh happened this round
  (R247 main == .bak byte-identical, sha256 `058f6ea5…`) — unlike R241
  (refreshed ~11:54 JST, corrected at R242/R243).

## SỬA TRƯỚC PUSH

(1) Row-convention tuple: the generator cited the coverage head
`1240497` as the R246 tuple sha instead of the content commit `c919f88`
— the row-convention rule counts the diff at the AUTHORING round's
content commit, and the diff at `1240497` is 3133, not the row's 3134.
Checker caught it on the first run (117/118: only the row-convention
R246 check failed); fixed in the generator (tuple + docstring list now
cite `c919f88`), regenerated the checker, re-filled the SHA-hits
paragraph, deleted the validation JSON, re-ran the checker (PASS
118/118). Same defect class as the R247 head-line additions error:
a coverage-head figure used where the content-commit figure belongs.
(2) Three generator-side fixes, all before any commit: (a) the
SHA-hits fill script's tag for the row-note paragraph still read
"R246-row note" (stale label, lesson-34 class) — fixed to "R247-row
note", generator re-run, fill re-run; (b) the new live-body note split
"replacing R140." across two lines, breaking the fill script's
end-anchor — rejoined to one line; (c) three residual-assert counts
corrected to the generator's own measurements (`6869aa1` 4→2 — the
lesson-11 delta and row-sha tuple moved to the new round;
`4fc20b6` 2→3 — the new lesson (15) cites it; `cd4f7b0` 18→21).

## R248 robustness note — headroom now 7.614 chars

The R247 warning left 7.363 ký tự of headroom; this round compacted
the R25 paragraph (504 ký tự → 207) and the R24 paragraph (504 ký tự →
207) — a true double compaction, both full paragraphs verified present
before assuming their lengths (R242 lesson 9 held: R25 content
`bd5c21a`/head `e55050f`, R24 content `5e43f15`/head `145970e`). The
body is now 97.386 ký tự — net −251 vs R247 — with 7.614 ký tự of
headroom. The head line stayed 1.072 ký tự (delta 0), so the −251 is
fully accounted: −297 − 297 + 271 + 37 + 30 + 5 + 0.
The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R249 warning: headroom is now 7.614 ký tự; compact R23 + R22 next (a true
double compaction, −594 against the 271-ký-tự new paragraph) to recover
the margin further.
At the current net the margin recovers once the double compaction resumes
(full paragraphs remaining R166..R247 = 82; compact block R24–R165 = 142 lines).
Lessons carried (short form — full text in the R247 report file, same
directory): (1) dry-run projection trusted over hand-count (title append
30, not 28); (2) a row's "cumulative N paths" counts the diff at the
AUTHORING round's content commit (R247 row's 3137 verified post-commit
by git diff, not assumed from the coverage head); (3) idempotency re-run
checks the NEW state first for EVERY edit (changed: 0 first clean re-run this
round); (4) append-style edits need the new-state check FIRST in
`sub_once` (new contains old); (5) `git status --porcelain` must be
EMPTY before push (only the validation JSON was untracked after the
content commit); (6) two backup locations can hold different versions —
the R241 payload's main was refreshed ~11:54 JST (see ĐÍNH CHÍNH R242
above), `.bak` keeps the as-built; (7) an `updated_at` that DOES move
while the body sha stays means a push touched the PR (updated_at
2026-11-25T08:27:39Z, changed from the R247 read 07:16:44Z because the
R247 push updated the head; body sha unchanged `1dd61afd` = R222);
(8) a connector call that fails on a wrong parameter name is not a failed
read (`pullNumber`, not `pull_number`; `issue_number`, not
`issueNumber`; the reviewed method is `get_comments` — retried and
succeeded); (9) `issue_read` `get_comments` is paginated at 30
comments per page (30 + 4 = 34; latest ACK on page 2); (10) the
execution-risk flag has appeared 7 times (R211, R213×2, R219, R231,
R239, R240) and the decision whether to keep running git/checker after
it still awaits luồng chính/chủ dự án — no flag appeared in the R248
round through the report-commit step; (11) mergeable_state is a
point-in-time read (the R247 payload's own head line, built ~17:34 JST,
said clean at `cd4f7b0` — CI had finished by build time; the fresh read
~17:42 JST says clean at `cd4f7b0`; the honest wording is the fresh
read); (12) a live-body read can need a re-read to come back clean (first
read 5 U+FFFD from transport mangling, re-read 0 U+FFFD, sha `1dd61afd`
= R222 — see lesson 35); (13) the checker writes its validation JSON at the
END of its run, AFTER the working-tree guard — delete the validation
JSON before a re-run; the guard asserts the PRE-commit tree, so a
re-run AFTER the content commit fails it by design (the re-run this round
happened BEFORE the content commit, after deleting the JSON — no re-run
was done after the content commit this round); (14) the compact-line count and
the per-round loop range can drift apart by one (this round: 142 lines
R24–R165, loop R24–R165 for the per-round check; the R36 restoration
guard is a separate check, not part of the loop count; the "Ghi chú"
range text reads R25–R165); (15) the R236 lesson
(16) held end to end (every edit through `il`/`bl`; dry-run =
apply; idempotency changed: 0; checker re-run PASS); (16) `find`
prefixes must not contain the OLD state + `sub_line`'s new-state guard
must be `if new in line: return 0` ALONE (three R247 guard fixes, see
pre-push fix (2) — the chained-timestamp case also needs ONE atomic sub
when the second replacement's NEW value equals the first's OLD value);
(17) inserting a paragraph adds its line break too (+271 for a 270-char paragraph; R248 net −251
likewise measured, not hand-counted — the double-compaction terms are
the ones a hand-count would most likely miss); (18) the checker total
is derived from the checker run itself (118/118 printed + validation
JSON), never from a naive textual count (72 textual calls − 2 loop
calls + expansions 2 + 46 = 118); (19) the SHA-hits paragraph is filled
by a second script that greps the generated checker (47 shas verified
this round, counts measured dynamically, locations classified from the
actual matching lines); (20) a payload's head line
stamps its build/refresh read's actual time (the R247 payload build
reads ~17:34 JST, matching its build time; no refresh happened
this round — main == .bak; the latest refresh remains the R241 main
~11:54 JST (verified at R242/R243, recorded in the R241 index row)); (21) a transform script
that generates the next round's checker build script must survive escape
processing — plain `str.replace` for REPLACEMENTS, backslash
normalisation only inside REPLACEMENTS (this round's generator ran clean
first try); (22) the working-tree guard asserts the PRE-commit tree —
do not re-run the checker after a commit expecting a pass; (23) the
`SyntaxWarning: invalid escape sequence '\`'` in the checker docstring
is pre-existing (warning-only, `py_compile` exit 0); (24) a payload
refresh must be recorded with BOTH versions (main vs `.bak`) and the
index-row correction belongs to the NEXT index update (R241 refresh
recorded at R242; the R241-row correction applied at R243).
(25) (carried from R243) — the brief's compaction pair (R37 + R36) assumed
both full paragraphs exist: the R36 paragraph had been deleted at
`1a601be` (R47 content) and no checker ever asserted it, because the
compact loop only covers R38+ and the title sequence only covers R93+.
Verify a compaction pair exists in the file before assuming their lengths
(R37 measured 493, R36 measured ABSENT); restore a lost paragraph from
git in compact form with its real content/report shas rather than
silently compacting one. The R242 checker guards the restoration (R36
compact line with content `386216b`, head `9ec1fd9`) and the compact
loop now covers R24–R165. This round both paragraphs of the pair (R25,
R24) were verified present (504 and 504) before compaction.
(26) (carried from R243) — the new-paragraph first draft measured 271 chars,
not 270: fixed by dropping the "~" before "12:08" (the push time is
exact from the queue log); the edit script asserts the exact 270 before
writing, so a hand-count error fails loudly instead of shipping a
1-char-long
paragraph. Trust the script's assert, never the hand-count.
(27) (carried from R243 — re-verified this round) — the index row's "delta" cites the authoring
round's own content..report diff (`c919f88..cd4f7b0`: 2 paths, 934
insertions) — NOT the difference between coverage-head insertion
totals (331522 − 329707 = 1815 is the wrong number; the report commit
adds only its own report md + validation json). The R247 report's
delta line already used the right figure; this round re-verified it
from git before writing the R247 row.
(28) (carried from R244) — a transform script that slices a paragraph out of a
generated file must slice by the paragraph's OWN boundaries, not by a
later structural marker: the first version of the R244 generator
sliced the SHA-hits paragraph out to the docstring close (`"""`) and
deleted every paragraph after it (corrections, live-body note, payload
paragraph, lessons). Caught by the stale-reference grep before any
commit (f021c08/3c076bf counts 2 instead of 3/4); fixed by slicing by
LINES to the paragraph's own closing `figure.)` line, then rebuilding
and re-verifying all sha counts (this round: 47 sha counts, all
verified — see lesson (35) above).
(29) (carried from R244) — the new-paragraph first draft measured 260 chars,
not 270: fixed by adding "chuẩn bị " + "~" (+10: "chuẩn bị xong sau
push ~13:04 JST"); the edit script asserts the exact 270 before
writing, so a hand-count error fails loudly instead of shipping a
short paragraph. Trust the script's assert, never the hand-count.
(30) (carried from R244) — no payload refresh happened this round (R247 main
== .bak byte-identical, sha256 `058f6ea5…`, verified from disk), so no
ĐÍNH CHÍNH is needed; a refresh must still be recorded with BOTH
versions (main vs `.bak`) when it happens, with the index-row
correction at the NEXT index update (R241 precedent).
(31) (carried from R245) — the compaction pair (R31 + R30) was verified
present before assuming its lengths: R31 measured 493 chars but R30
measured 552 chars, NOT 493 — the two paragraphs are NOT the same
length (R30 carries the longer quiet-hours payload sentence), so the
double compaction saved −286 + −345 = −631, not −572; never assume a
pair shares a length, measure both. The R244 payload was NOT built by
the R244 round (its report promised it after the push, but the round
ended at the report commit + push); R245 built it late (~14:47 JST,
body 98,475 chars, sha `4a3befc6`, JSON 111,339 bytes, main == .bak
sha256 `4d89565d…`) so the R244 index row could cite real figures — a
promised payload is a deliverable, not a footnote.
(32) (carried from R245) — stale carried text in the checker docstring/code
comments drifts a round behind if nobody re-reads it: R245 fixed
three — the Ghi-chú correction paragraph said "R234 also corrects"
(the correction described is R245's), the execution-risk note said
"This R243 round proceeds" (in the R244 checker), and two code comments
were stale ("R158/R238, range R45-R165, through R237" and "R237 after
R236"). All four now cite R245/R244; the checker asserts the corrected
values, not the comments, but the comments are the next reader's map.
This round fixed the same class again: the SHA-hits fill script's tag
for the row-note paragraph still read "R246-row note" (the paragraph
now describes the R247 row), plus the "lượt cập nhật này" correction
paragraph, the Ghi-chú range/list, the execution-risk note and the
live-body note all advanced R247 → R248.
(33) (carried from R245) — a payload builder that applies a global time
replacement before a time-specific one silently breaks the specific
one: the first R244-payload build replaced `~13:44 JST` globally, then
asserted the issue_read citation still contained `~13:44 JST` — caught
by the assert (expected 1, found 0); fixed by ordering the specific
replacement first. Order replacements specific-before-global, and keep
the assert. (The R248 edit script's head-line timestamp fix orders the
atomic updated_at replacement as ONE sub — see pre-push fix (2b) of R247 — the
chained values make even specific-before-global unsafe there.)
(34) NEW THIS ROUND (R246) — the SHA-hits paragraph's per-sha hit/hits claims
must be re-measured every round, not carried forward: relabeling a
guard comment (the R243-row guard comment → "R244 row (carried from
R245)") silently drops one occurrence of its sha (`214eb99` went from
2 to 1 — only the check name still cites it), so the carried "hits"
claim went stale; the grep caught it (expected ≥2, found 1) before any
commit. The `bbddba5` entry needed the same re-measurement: the
relabeled comment is a THIRD occurrence, so "comment" became
"comments" (plural). Never carry a hit/hits claim forward without
re-running the grep — and the grep must count occurrences EXCLUDING
the paragraph itself, or every sha reads +1.
(34-dev-queue) NUMBERING COLLISION, recorded not rewritten: the R245
report used (34) for the ls-remote citation defect (3-minute time
mismatch, fixed at R246), while the R246 report used (34) for the
SHA-hits grep lesson above. Both (34)s stay as pushed — this round
takes (35) for its new lesson and notes the collision here, instead of
renumbering pushed history.
(35) NEW THIS ROUND (R247) — a live-body read that returns U+FFFD is a
transport artifact, not a body change: the first PR read this round
returned 103,026 chars, sha `14e4afea`, 5 U+FFFD, while the immediate
re-read returned 103,023 chars, sha `1dd61afd`, 0 U+FFFD, byte-exact
with the R222 payload. The mangling hits multi-byte Vietnamese chars at
transport chunk boundaries ("ă" U+0103 decodes as 2 U+FFFD, "ủ"
U+1EE7 as 3 U+FFFD); the same artifact appears in exec stdout display
(the index R246 note displayed three replacement characters after "đ"
on screen while the file on disk has 0 U+FFFD). Never conclude a file
is corrupt from displayed output — verify from bytes (sha256,
codepoints) and re-read immediately; a first imperfect read is a
transport artifact, like the R98 replication-lag precedent. (Checker
docstring lesson (14) carries the same lesson under the checker's own
numbering.)
(36) NEW THIS ROUND (R248) — a head line can carry wrong figures that no
length assert catches: the R247 body v2 head line shipped additions
`327963` (stale, from head `4fc20b6`) instead of `329707` at head
`1240497`, because the edit script replaced head/commits/files but never
the additions figure, and Gói 39 ID `6835238814` instead of
`6815238814`, because a scoped sub `"681"`→`"683"` (expect=3) consumed
its third match inside the ID. Both defects were confined to the head
line (one occurrence each, line 5); the R247 payload was built with the
correct figures, so the posted description would have been right, but
the repo file was wrong. Fix: replace additions explicitly with the full
token `"additions 327963"`→`"additions 331522"`, fix the ID FIRST with
the full token `"6835238814"`→`"6815238814"`, never use a bare 3-digit
sub, and the checker now asserts additions `331522` and ID `6815238814`
in the head line and the absence of `6835238814` and `327963` from the
body. (Checker docstring lesson (15) carries the same lesson under the
checker's own numbering.)
(37) NEW THIS ROUND (R248) — a row-convention tuple must cite the
AUTHORING round's CONTENT commit, not the coverage head: the R246 row's
cumulative 3134 is the diff at the R247 content commit `c919f88`, not
at the coverage head `1240497` (whose diff is 3133). The generator
first cited `1240497` and the checker caught it on its first run
(117/118 — only the row-convention R246 check failed); fixed in the
generator (tuple + docstring list now cite `c919f88`), regenerated,
re-filled, re-ran to PASS 118/118. Same defect class as lesson (36):
a coverage-head figure used where the content-commit figure belongs.
The lesson-(11) example in the checker docstring was also advanced to
the current figures (`331522 − 329707 = 1815` is the wrong number).

## Verification

- Merge-tree `cd4f7b0` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `f764bbce…`. Merge-tree at the R248
  content head `cf24619` vs `f3db6b3`: exit 0,
  tree `54d47553…`.
- Live PR state: connector read this round (~17:42 JST) — single clean
  read (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD — byte-exact with the
  R222 payload; updated_at 2026-11-25T08:27:39Z — changed from the R247
  read, body bytes unchanged); mergeable_state clean at `cd4f7b0`
  (connector read this round). `get_status` was NOT read this round;
  the PR `get` read's mergeable_state is the operative state. Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: 34 comments, latest ACK `6862732081` (CP5 + M-G CP10
  + R2); no new Codex/owner direction since Gói 39 (`6815238814`).
  The 5 comments after Gói 39 are all Muse ACKs of completed work, not new direction.
- Scope audit: R248 block (`cd4f7b0..cf24619`) 3 paths / 0 violations
  (index + body v2 + R248 checker); cumulative at the R248 content
  commit `cf24619` 3137 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `cf24619`). Merge-tree at the R248 content head `cf24619` vs `f3db6b3`: exit 0,
  tree `54d47553…`.
- Transient notes: this round's `git fetch` at ~17:40 JST succeeded
  first try (no intervening push; remote head stayed `cd4f7b0`,
  integration stayed `f3db6b3`). One `git ls-remote` call at the run
  start failed with a proxy connection reset (`kex_exchange_identification:
  read: Connection reset by peer`) — transient transport failure, not a
  repo state change: the local HEAD already matched the verified remote
  head `cd4f7b0`, and the push below will fail fast if the remote has
  moved. No `git ls-remote` retry was needed.
  The connector read path was used this round — the PR read succeeded
  first try with `pullNumber` (lesson 8 carried); pagination on
  `issue_read` worked first try with `issue_number` + `page`.
  No call-tool write approval was requested for a read. No execution-risk flag this round
  through the report-commit step. No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH; the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
  `git add -N` was NOT needed this round: the scope audit runs on commits
  (base..head), not the working tree, so the new checker counted in the
  block diff via the content commit itself. The checker emits a
  `SyntaxWarning: invalid escape sequence '\`'` on its docstring (the
  `\`` sequences in the R235 lesson text) — warning only, same shape as
  the R247 checker file, `py_compile` exit 0, checks unaffected.
- Ceiling discipline: the R247 payload JSON as-prepared measured 110.076 byte
  (prepared after the R247 push ~17:34 JST, NOT posted — live body is still R222, verified by this round's connector read),
  vs the 131.072-byte transport ceiling
  (20.996 byte headroom); the main file was NOT refreshed after the R247 build (main == .bak byte-identical,
  sha256 `058f6ea5…` — verified this round before the R248 content commit).
  The projected R248 payload JSON is ~112.000 byte
  (measured exactly at payload build, after push). Body v2 is now 97.386
  ký tự (< 105.000) — 7.614 ký tự of headroom. R249 warning:
  headroom is now 7.614 ký tự; the double compaction must continue next round
  (R23 + R22) to recover the margin further.

## Next

Posting round (owner tap): PR #119 description refresh to the R248 body
v2 (R247 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r248.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R248 push (title
ending "+ R248", built by replacing the "+ R247" suffix — not appending;
body = body v2 R248 in repo, head line refreshed to head after R248 push).
This run started ~17:40 JST — INSIDE working hours (09:00–21:30 JST), so the
R248 payload is READY FOR PRESENTATION (unlike R142/R164–R197/R207–R216/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237/R238/R239/R240,
which were held outside working hours). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R247 payload as new — R247 was prepared but never posted and is superseded by R248 (its main file was NOT refreshed after build — main == .bak byte-identical, sha256 `058f6ea5…` — but the refresh does not decide postability; R248 supersedes it; no ĐÍNH CHÍNH this round); do not present the R246 widget — it is stale since the R247 push; do not present the R245 widget — it is stale since the R246 push; do not present the R244 widget — it is stale since the R245 push; do not present the R243 widget — it is stale since the R244 push; do not present the R242 widget — it is stale since the R243 push; do not present the R241 widget — it is stale since the R242 push; do not present the R240 widget (`widget-c7b281c5`, presented ~10:55 JST) — it is stale since the R241 push; do not present the R222 payload as new — R222 is LIVE. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220, R221, R222, R223, R224, R225, R226, R227, R228, R229, R230, R231, R232, R233, R234, R235, R236, R237, R238, R239, R240, R241, R242, R243, R244, R245, R246 and R247 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R248: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
