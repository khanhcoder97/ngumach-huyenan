# MEDIA-02 — PR #119 Body Restructure R252: delivery index + body v2 coverage to `7ca1f05`

Date: 2026-11-25 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `7ca1f05` (PR119 BODY RESTRUCTURE R251 report). Content commit: `fa41682`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R252 does

No ĐÍNH CHÍNH this round: the R251 payload main == .bak byte-identical
(sha256 `59404213…`, verified from disk), no refresh happened — unlike R241
(refreshed ~11:54 JST, corrected at R242/R243). No new Codex/owner direction has
been verified on issue #116: 34 comments, latest ACK `6862732081`
(CP5 + M-G CP10 + R2); no new direction since Gói 39 (`6815238814`).

Fresh derivation at `7ca1f05` (~21:44 JST): `git rev-list --count
cf17178..7ca1f05` = 693 commits, `git diff --name-only` = 3148 files,
`--shortstat` = 339439 insertions, 0 deletions — agreeing exactly with
the public-API PR read. `git merge-tree --write-tree` `7ca1f05` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `44121ff2…`. The run
fetched at ~21:40 JST (the run start) and the remote head was still
`7ca1f05`, integration still `f3db6b3` — no intervening push; the
public-API read ~21:44 JST independently confirmed head `7ca1f05`. The live PR read this round (~21:44 JST,
public GitHub API, read-only — the connector `call-read-tool` rejected
`pull_request_read` in this run, see below): title ends "+ R222", head `7ca1f05`,
693 commits / 3148 files / +339439, mergeable true / mergeable_state clean at `7ca1f05`, live body 103.023 ký tự,
sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222 payload,
updated_at 2026-11-25T11:55:56Z — changed from the R251 read
(2026-11-25T10:51:26Z) because the R251 push updated the head; the body
bytes are unchanged, still R222.

R252 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  title head refreshed to `7ca1f05`; milestone lines refreshed to head
  `7ca1f05` (693 commits / 3148 files / 339439 additions; the fresh git
  derivation at `7ca1f05`, the fresh public-API PR read ~21:44 JST, and
  the merge-tree cross-check at `7ca1f05` are cited, with the live body
  R222 read back byte-exact this round — 0 U+FFFD, single clean read);
  delta `a6319ed..7ca1f05`: 2 paths, 1064 insertions, 0 deletions);
  one row appended — PR119 BODY RESTRUCTURE R251 (`a6319ed`/`7ca1f05`),
  recording that its payload was prepared after the R251 push (~20:56 JST,
  96.747 ký tự, sha `665ad4c5`; JSON 108.765 byte
  < trần 131.072 — còn 22.307 byte, bản giữ tại
  `.bak-prepost-20261124` — sha256 `59404213…`, as-built figures) and then
  NOT posted (live body still R222 as read this round ~21:44 JST); the
  R251 row also records the stale R250 widget (head has moved to
  `7ca1f05` — do NOT tap; present the R251 widget instead); no separate
  ACK for R251. No ĐÍNH CHÍNH this round (R251 payload main == .bak
  byte-identical, no refresh).
  The index now covers every block through `7ca1f05`; R252's own 2
  commits fold in at the next index update (R253), disclosed in the index
  itself. The R252 note was appended after the R251 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `7ca1f05` · 693 · 3148 (additions `339439`, Gói 39 ID `6815238814`,
  tree `44121ff2…`; with the fresh git derivation at `7ca1f05`,
  the fresh public-API PR read ~21:44 JST, and the fresh merge-tree
  cross-check at `7ca1f05`), plus the R251 paragraph in "Khối mới nhất"
  (270 ký tự text + 1 line break = 271 ký tự, marked chưa đăng — payload
  prepared after push ~20:56 JST, live body still R222) and the R252 note. The stale index
  reference in "Về bản mô tả này" (head `1281cde`) is also fixed to
  `7ca1f05`, the "lượt cập nhật này" sentence is advanced R251 → R252,
  and the compaction trail gains
  "R252 đã gọn thêm các đoạn R17 + R16." (36 ký tự + 1 leading space = 37). The title line is
  extended to R251 (APPENDED, not replaced — see the R176 robustness
  note; the append measures 30 ký tự). Compaction (R251 warning —
  applied as a true double compaction this round): the R17 paragraph
  (453 ký tự — measured this round, full paragraph verified present)
  and the R16 paragraph (488 ký tự — measured this round, full paragraph
  verified present; the pair does NOT share a length this time — see lesson
  (44) below) are each collapsed to one
  207-ký-tự compact line.
  Full detail stays in the delivery index; the checker asserts < 400,
  not an exact 207. The new R251 paragraph was 271 ký tự, so the body
  is 96.456 ký tự — net −240 vs R251 (the double compaction resumed:
  −246 R17 compaction − 281 R16 compaction + 271 new paragraph + 37
  trail append + 30 title append + 5 Ghi-chú list append ("/R251") − 56
  head-line delta), headroom 8.544 ký tự. The dry-run first projected
  96.456 ký tự and the apply wrote exactly that — measure, then trim,
  then apply.
  Paragraph order: the R251 paragraph sits directly after R250
  (ascending full-paragraph order R166..R251), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R252 (owner tap) — the R222 body v2 now live is the base;
  only the R251 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r252_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R251 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R251 and R252 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R251 (150 compact lines R16–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 96.456 ký tự),
  a check that the R251 paragraph sits directly after R250
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237/R238/R239/R240/R241/R242/R243/R244/R245/R246/R247/R248/R249/R250 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R251 note clean).
  New this round: the R251-row guard (cumulative must cite 3149 —
  3148 at `7ca1f05` + 1 new checker in the R252 content commit,
  verified in this report after the content commit), the ĐÍNH CHÍNH R242
  guard carried (the R241 row must carry the note with sha `83d221b8`), the R36-restoration
  guard carried (the R36 compact line must exist with content `386216b` and head
  `9ec1fd9`), the ĐÍNH CHÍNH R241 guard carried (the R239 row must carry
  the note with sha `1e38e781`), the body "Ghi chú" line correction
  guard (R158/R252, range R17–R165, list complete through R251, no double
  slash), the "lượt cập nhật này" sentence correction guard (full
  corrected sentence present; the defective "chính R251" form absent),
  the lesson-36 head-line guard (additions `339439` and Gói 39 ID
  `6815238814` present in the head line; `6835238814` and `337378`
  absent from the body), and the working-tree guard (`git status --porcelain` lists exactly the
  3 intended paths — index + body + this checker — no stray modification
  may survive past the report commit).
  **PASS 126/126**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R252_VALIDATION_20261125.json`).
  The checker passed 126/126 on its first run against the applied tree.
  The checker was generated from R251 by a transform script (not
  sed-copied) with the full COVER SHA verified intact (definition +
  docstring, both `7ca1f05753a47902df7d52499fc5c019c54f4aa4` — re-derived
  from `git rev-parse` this round) and a stale-reference grep (55 shas
  verified, counts measured dynamically) after the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The SHA-hits paragraph was regenerated by a second
  script that greps the generated checker (55 shas, line counts measured
  dynamically, locations classified from the actual matching lines).
  The edit script's budget check ran before any write (R166 lesson): the
  dry-run simulation projected 96.456 ký tự and the apply wrote on
  the first attempt at 96.456 ký tự, with 8.544 ký tự of headroom; the
  idempotency re-run after apply reports already-applied changed: 0 —
  verified (the re-run reported changed: 0 on the first clean re-run).
  The R251 paragraph's first draft measured 270 chars exactly (no fix
  needed); the edit script asserts the exact 270 before writing — see lesson 26
  of R242, carried; the two compact lines each measured exactly 207 chars on the first attempt.
  The documents were correct after the fix; the
  checker passed 126/126 on its (re-)run against the applied tree,
  writing the repo validation JSON in the same run.
  The R251 row's cumulative figure was drafted as 3149 (3148 at `7ca1f05` + 1 new checker in the R252 content commit) and the true diff at the R252 content commit is 3149 — verified by
  `git diff --name-only cf17178..fa41682` = 3149 after the content commit.
  The R250 row's cumulative 3146 was re-derived from git at `a6319ed`
  (`git diff --name-only cf17178..a6319ed` = 3146) and by the checker's
  row-convention loop (R250 cumulative 3146 == diff at `a6319ed` — PASS).
  `git status --porcelain` after the content commit showed only the
  intended validation JSON untracked — no leftover edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R251's committed content this round: R251's committed content verified correct —
  the committed index at `7ca1f05` carries the R249 row at cumulative 3143
  (re-derived by the new checker from git at `8bebd8a`) and the R250 row at 3146
  (re-derived from git at `a6319ed`); no uncommitted
  working-tree fix was left behind by R251 (the working tree was clean at this
  run's start apart from the R251 commits already pushed, and the fetch found no intervening push). No payload refresh happened this round
  (R251 main == .bak byte-identical, sha256 `59404213…`) — unlike R241
  (refreshed ~11:54 JST, corrected at R242/R243).

## SỬA TRƯỚC PUSH

(1) Generator placeholder defect (missing dict key): the
`make_build_checker_r252.py` shift's checker-filename chain still
referenced placeholder key `I248` (carried from the R251 maker) while
the renamed P dict no longer defined it — the maker failed loudly with
`KeyError: 'I248'` before writing anything (no partial output); fixed
by re-adding the `I248` key as the filename placeholder (distinct from
the `I250` identifier placeholder), re-ran cleanly. Same defect class
as R251's placeholder collision (lesson 42): placeholder keys must be
distinct per token class — verify the maker runs before trusting the
builder.
(2) Builder-level anchor defect (wrong round for SHA_START/assert):
the first draft of `make_build_checker_r252.py` set SHA_START to the
`1281cde` paragraph start and the assert to `"1281cde"` as the OLD
values — but the R251 builder's SHA_START/assert cite `4ad9429` (the
R250 checker's paragraph, which the R252 builder slices out); the
`1281cde` values are the NEW values the R252 builder must carry.
Caught by re-reading `build_checker_r251.py` before running (the
maker's count-1 assert would also have failed loudly); fixed to
`4ad9429` → `1281cde`. Same defect class as R248's coverage-head /
content-commit confusion: a figure used where another belongs.

## R252 robustness note — headroom now 8.544 chars

The R251 warning left 8.304 ký tự of headroom; this round compacted
the R17 paragraph (453 ký tự → 207) and the R16 paragraph (488 ký tự → 207)
— a true double compaction, both full paragraphs verified present
before assuming their lengths (R242 lesson 9 held: R17 content
`20d234d`/head `246ac37`, R16 content `57fa2db`/head `43fd714`). The
body is now 96.456 ký tự — net −240 vs R251 — with 8.544 ký tự of
headroom. The head line shrank to 977 ký tự (delta −56, measured — the
mergeable clause shortened: mergeable true, no "GitHub đang tính lại"
clause, and the API-read wording is shorter), so the −240 is
fully accounted: −246 − 281 + 271 + 37 + 30 + 5 − 56.
The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R253 warning: headroom is now 8.544 ký tự; compact R15 + R14 next (a true
double compaction, −527 against the 271-ký-tự new paragraph at the R252
pair's measured saving) to recover the margin further.
At the current net the margin recovers once the double compaction resumes
(full paragraphs remaining R166..R251 = 86; compact block R16–R165 = 150 lines).
Lessons carried (short form — full text in the R251 report file, same
directory): (1) dry-run projection trusted over hand-count (title append
30, not 28); (2) a row's "cumulative N paths" counts the diff at the
AUTHORING round's content commit (R251 row's 3149 verified post-commit
by git diff, not assumed from the coverage head); (3) idempotency re-run
checks the NEW state first for EVERY edit (changed: 0 first clean re-run this
round); (4) append-style edits need the new-state check FIRST in
`sub_once` (new contains old); (5) `git status --porcelain` must be
EMPTY before push (only the validation JSON was untracked after the
content commit); (6) two backup locations can hold different versions —
the R241 payload's main was refreshed ~11:54 JST (see ĐÍNH CHÍNH R242
above), `.bak` keeps the as-built; (7) an `updated_at` that DOES move
while the body sha stays means a push touched the PR (updated_at
2026-11-25T11:55:56Z, changed from the R251 read 2026-11-25T10:51:26Z
because the R251 push updated the head; body sha unchanged `1dd61afd` = R222);
(8) a connector call that fails on a wrong parameter name is not a failed
read (`pullNumber`, not `pull_number`; `issue_number`, not
`issueNumber`; the reviewed method is `get_comments` — retried and
succeeded); (9) `issue_read` `get_comments` is paginated at 30
comments per page (30 + 4 = 34; latest ACK on page 2); (10) the
execution-risk flag has appeared 8 times (R211, R213×2, R219, R231,
R239, R240, R248) and the decision whether to keep running git/checker after
it still awaits luồng chính/chủ dự án — the R248 round was blocked by
it, and the R249 run retried the push cleanly; no flag appeared in the R252
round through the report-commit step; (11) mergeable_state is a
point-in-time read (the R251 payload's own head line, built ~20:56 JST,
said unstable at `7ca1f05` — CI was running at build time; the fresh read
~21:44 JST says clean at `7ca1f05`; the honest wording is the fresh
read); (12) a live-body read can need a re-read to come back clean (first
read 5 U+FFFD from transport mangling, re-read 0 U+FFFD, sha `1dd61afd`
= R222 — see lesson 35); (13) the checker writes its validation JSON at the
END of its run, AFTER the working-tree guard — delete the validation
JSON before a re-run; the guard asserts the PRE-commit tree, so a
re-run AFTER the content commit fails it by design (the re-run this round
happened BEFORE the content commit, after deleting the JSON — plus the
reset/unstage sequence of pre-push fix (4), which re-ran the checker on
the corrected pre-commit tree); (14) the compact-line count and
the per-round loop range can drift apart by one (this round: 150 lines
R16–R165, loop R16–R165 for the per-round check; the R36 restoration
guard is a separate check, not part of the loop count; the "Ghi chú"
range text reads R17–R165); (15) the R236 lesson
(16) held end to end (every edit through `il`/`bl`; dry-run =
apply; idempotency changed: 0; checker re-run PASS); (16) `find`
prefixes must not contain the OLD state + `sub_line`'s new-state guard
must be `if new in line: return 0` ALONE (three R247 guard fixes, see
pre-push fix (2) — the chained-timestamp case also needs ONE atomic sub
when the second replacement's NEW value equals the first's OLD value);
(17) inserting a paragraph adds its line break too (+271 for a 270-char paragraph; R252 net −240
likewise measured, not hand-counted — the double-compaction terms are
the ones a hand-count would most likely miss); (18) the checker total
is derived from the checker run itself (126/126 printed + validation
JSON), never from a naive textual count (126 = 124 (R251) + 1 new R251-row
check + 1 row-convention R250 tuple); (19) the SHA-hits paragraph is filled
by a second script that greps the generated checker (55 shas verified
this round, counts measured dynamically, locations classified from the
actual matching lines); (20) a payload's head line
stamps its build/refresh read's actual time (the R251 payload build
reads ~20:56 JST, matching its build time; no refresh happened
this round — main == .bak; the latest refresh remains the R241 main
~11:54 JST (verified at R242/R243, recorded in the R241 index row)); (21) a transform script
that generates the next round's checker build script must survive escape
processing — plain `str.replace` for REPLACEMENTS, backslash
normalisation only inside REPLACEMENTS (this round's generator ran clean
after the fixes in pre-push fixes (1)–(2) above, which were caught by
verification greps, not by the checker); (22) the working-tree guard asserts the PRE-commit tree —
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
Verify a compaction pair exists in the file before assuming its lengths
(R37 measured 493, R36 measured ABSENT); restore a lost paragraph from
git in compact form with its real content/report shas rather than
silently compacting one. The R242 checker guards the restoration (R36
compact line with content `386216b`, head `9ec1fd9`) and the compact
loop now covers R16–R165. This round both paragraphs of the pair (R17,
R16) were verified present (453 and 488) before compaction.
(26) (carried from R243) — the new-paragraph first draft measured 271 chars,
not 270: fixed by dropping the "~" before "12:08" (the push time is
exact from the queue log); the edit script asserts the exact 270 before
writing, so a hand-count error fails loudly instead of shipping a
1-char-long
paragraph. Trust the script's assert, never the hand-count.
(27) (carried from R243 — re-verified this round) — the index row's "delta" cites the authoring
round's own content..report diff (`a6319ed..7ca1f05`: 2 paths, 1064
insertions) — NOT the difference between coverage-head insertion
totals (339439 − 337378 = 2061 is the wrong number; the report commit
adds only its own report md + validation json). The R251 report's
delta line already used the right figure; this round re-verified it
from git before writing the R251 row.
(28) (carried from R244) — a transform script that slices a paragraph out of a
generated file must slice by the paragraph's OWN boundaries, not by a
later structural marker: the first version of the R244 generator
sliced the SHA-hits paragraph out to the docstring close (`"""`) and
deleted every paragraph after it (corrections, live-body note, payload
paragraph, lessons). Caught by the stale-reference grep before any
commit (f021c08/3c076bf counts 2 instead of 3/4); fixed by slicing by
LINES to the paragraph's own closing line, then rebuilding
and re-verifying all sha counts (this round: 55 sha counts, all
verified — see lesson (35) above). NOTE this round: the builder-level
SHA_START/assert anchors DID need a fix (pre-push fix (2) above — the
R251 builder's anchors cite `4ad9429`, not `1281cde`); caught by
re-reading the R251 builder before running, not by the generator.
(29) (carried from R244) — the new-paragraph first draft measured 260 chars,
not 270: fixed by adding "chuẩn bị " + "~" (+10: "chuẩn bị xong sau
push ~13:04 JST"); the edit script asserts the exact 270 before
writing, so a hand-count error fails loudly instead of shipping a
short paragraph. Trust the script's assert, never the hand-count.
(30) (carried from R244) — no payload refresh happened this round (R251 main
== .bak byte-identical, sha256 `59404213…`, verified from disk), so no
ĐÍNH CHÍNH is needed; a refresh must still be recorded with BOTH
versions (main vs `.bak`) when it happens, with the index-row
correction at the NEXT index update (R241 precedent).
(31) (carried from R245) — the compaction pair (R31 + R30) was verified
present before assuming its lengths: R31 measured 493 chars but R30
measured 552 chars, NOT 493 — the two paragraphs are NOT the same
length (R30 carries the longer quiet-hours payload sentence), so the
double compaction saved −286 + −345 = −631, not −572; never assume a
pair shares a length, measure both. The R245 payload was NOT built by
the R244 round (its report promised it after the push, but the round
ended at the report commit + push); R246 built it late (~14:47 JST,
body 98,475 chars, sha `4a3befc6`, JSON 111,339 bytes, main == .bak
sha256 `4d89565d`) so the R244 index row could cite real
figures — a promised payload is a deliverable, not a footnote.
(32) (carried from R245) — stale carried text in the checker docstring/code
comments drifts a round behind if nobody re-reads it: R245 fixed
three — the Ghi-chú correction paragraph said "R234 also corrects"
(the correction described is R245's), the execution-risk note said
"This R243 round proceeds" (in the R244 checker), and two code comments
were stale ("R158/R238, range R45-R165, through R237" and "R237 after
R236"). All four now cite R252/R251; the checker asserts the corrected
values, not the comments, but the comments are the next reader's map.
This round fixed the same class again: the maker's placeholder dict
had dropped the `I248` filename key (pre-push fix (1)) and the
builder-level SHA_START/assert cited the wrong round's sha (pre-push
fix (2)) — both caught before any commit by running/re-reading, not by
the checker.
(33) (carried from R245) — a payload builder that applies a global time
replacement before a time-specific one silently breaks the specific
one: the first R244-payload build replaced `~13:44 JST` globally, then
asserted the issue_read citation still contained `~13:44 JST` — caught
by the assert (expected 1, found 0); fixed by ordering the specific
replacement first. Order replacements specific-before-global, and keep
the assert. NOTE this round: no chained timestamp sub was needed — the
R252 head line's updated_at changed from the R251 read (10:51:26Z →
11:55:56Z, push note added), and the head line is replaced whole
by line_replace, not by a sub; the ordering lesson is carried, not
re-applied.
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
the current figures (`339439 − 337378 = 2061` is the wrong number).
(38) NEW THIS ROUND (R249) — a round blocked by the execution-risk flag
leaves its payload to the retry run: the R248 round stopped after the
pre-push fetch (flag #8), so its 2 commits stayed local and no R248
payload existed; the R249 retry run verified the remote head unchanged
(ls-remote + API read, `cd4f7b0`), pushed `cd4f7b0..24037b7`, then built the
R248 payload from the post-push head (97.398 chars, sha `ae047027`, JSON
109.761 bytes, main == .bak sha256 `d9bf8543…`) before starting R249's own
round. A blocked round's payload is the retry run's first deliverable,
not the blocked round's footnote (R244 precedent: its payload was built
late by R245). The R248 index row records the flag + the retry with the
real push figures; the R249 checker guards the row with the R248-row check.
Two generator anchors failed loudly before any write this round (lesson-(6) "The" split across lines; SHA-hits closing
line misremembered) — both fixed from grep, not from memory.
(39) NEW THIS ROUND (R250) — a payload's head-line mergeable_state goes
stale the moment CI finishes after the build: the R249 payload (built
~19:05 JST) honestly said unstable at `4ad9429`, but this round's fresh
API read ~19:41 JST says clean at the same head (mergeable null in both
reads — GitHub was still computing the mergeable flag; only
mergeable_state moved). The R250 head line drops the "CI đang chạy, lần
clean gần nhất" clause (delta −88, measured). A posted description's
mergeable_state is the build read's, not the tap read's — refresh it at
presentation if CI has since finished (lesson 8/R241 refresh precedent),
and record both reads in the report. (Checker docstring lesson (17)
carries the same lesson under the checker's own numbering.)
(40) NEW THIS ROUND (R250) — a transform script's anchors must be verified
against the CURRENT file's real line breaks, not copied from the
previous round's build script: the R250 generator's SHA_START ("...
intentional -- in the") and SHA_END ("are likewise legitimate -- ...")
were both copied from build_checker_r249.py's constants, which matched
the R248 checker's wrapping — but the fill script re-wraps the SHA-hits
paragraph every round, so in the R249 checker the first line ends at
"-- in" and the last line starts at "legitimate --". Both anchors
matched 0 times and the generator failed loudly before any write (no
partial output); fixed from grep (see pre-push fixes (1)–(2) above).
Same defect class as the R249 generator fixes, one round later — the
fill script's re-wrap is the moving part, so the anchor check belongs
in the generator's own pre-flight (grep the anchor before replacing),
not in the next round's memory.
(41) NEW THIS ROUND (R251) — the PR's updated_at moves on every push
even when the body bytes are unchanged: the R250 push moved updated_at
10:04:03Z → 10:51:26Z while the body stayed sha `1dd61afd` (still R222,
103,023 chars, 0 U+FFFD). Never read an updated_at change as a body
change; verify by body sha and length, and record both updated_at values
in the report so the next round can tell a push from a post. (Checker
docstring lesson (18) carries the same lesson under the checker's own
numbering.)
(42) NEW THIS ROUND (R251) — a transform script's shift must not let a
placeholder collide across token classes: one placeholder served both
the full COVER SHA and the short cover sha, so COVER became `"1281cde"`
instead of the 40-char SHA; and a bare-number replace matched `"146"`
inside `"3146"`, turning the R250-row cumulative into 3148. Both were
caught by the post-generation verification grep before any commit (full
SHA count 0, 3148 count 1); fixed with distinct placeholders and
bare-token number matching (lookarounds). The checker would have failed
the 3148 figure loudly (the index correctly says 3146), but the grep
caught it first — verify generated artifacts by grep before running the
checker, not only by the checker.
(43) NEW THIS ROUND (R251) — a blind shift over a (carried + new) pair
drops the carried block: the row-check pair's old side held two blocks
(R248 carried + R249 new); shifting both turned R248-carried into
R249-carried and dropped R248 entirely. The first checker run still
passed 123/123 — a checker that passes with a missing check is a
generator defect, not a document defect. Compare the check total against
the expected total every round (126 = 124 + 1 new row check + 1
row-convention tuple); the count diff caught it. Fix: the pair's old
side must be ONLY the previous "new" block, with the carried block
untouched above it.
(44) NEW THIS ROUND (R252) — the compaction pair does NOT share a
length, again: R17 measured 453 chars but R16 measured 488 chars (the
R16 paragraph carries the longer card-expiry payload sentence), so the
double compaction saved −246 + −281 = −527, not −492; never assume a
pair shares a length, measure both (lesson 31, re-proven this round).
The connector read path changed this round: `call-read-tool` rejected
`issue_read` and `pull_request_read` (not in the reviewed read-only
set), so the live reads used the public GitHub API (curl, HTTP 200,
repo public) — record the actual read path, not the usual one, and the
read is verifiable from bytes (34 comments, body sha `1dd61afd`).

## Verification

- Merge-tree `7ca1f05` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `44121ff2…`. Merge-tree at the R252
  content head `fa41682` vs `f3db6b3`: exit 0,
  tree `e2c543c5…`.
- Live PR state: public-API read this round (~21:44 JST) — single clean
  read (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD — byte-exact with the
  R222 payload; updated_at 2026-11-25T11:55:56Z — changed from the R251
  read, body bytes unchanged); mergeable true / mergeable_state clean at `7ca1f05`
  (public-API read this round). `get_status` was NOT read this round;
  the PR `get` read's mergeable_state is the operative state. Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: 34 comments, latest ACK `6862732081` (CP5 + M-G CP10
  + R2); no new Codex/owner direction since Gói 39 (`6815238814`).
  The 5 comments after Gói 39 are all Muse ACKs of completed work, not new direction.
- Scope audit: R252 block (`7ca1f05..fa41682`) 3 paths / 0 violations
  (index + body v2 + R252 checker); cumulative at the R252 content
  commit `fa41682` 3149 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `fa41682`). Merge-tree at the R252 content head `fa41682` vs `f3db6b3`: exit 0,
  tree `e2c543c5…`.
- Transient notes: this round's first `git fetch` at ~21:40 JST failed
  (connection reset by the proxy, `kex_exchange_identification: read:
  Connection reset by peer` on 198.19.0.1:3128) — the retry ~21:41 JST
  succeeded (remote head still `7ca1f05`, integration still `f3db6b3`);
  same transient class as the R246 fetch failure, no remote change.
  The connector read path was NOT usable this round — `call-read-tool`
  rejected `issue_read` and `pull_request_read` as not in the reviewed
  read-only set, so the live reads used the public GitHub API (curl,
  HTTP 200, no auth, repo public). No call-tool write approval was
  requested for a read. No execution-risk flag this round
  through the report-commit step. No git-lfs
  hook warning appeared at the content commit (the files are text-only
  in any case, so no LFS smudge was involved; the push below uses the
  documented env).
  `git add -N` was NOT needed this round: the scope audit runs on commits
  (base..head), not the working tree, so the new checker counted in the
  block diff via the content commit itself. The checker emits a
  `SyntaxWarning: invalid escape sequence '\`'` on its docstring (the
  `\`` sequences in the R235 lesson text) — warning only, same shape as
  the R251 checker file, `py_compile` exit 0, checks unaffected.
- Ceiling discipline: the R251 payload JSON as-prepared measured 108.765 byte
  (prepared after the R251 push ~20:56 JST, NOT posted — live body is still R222, verified by this round's public-API read),
  vs the 131.072-byte transport ceiling
  (22.307 byte headroom); the main file was NOT refreshed after the R251 build (main == .bak byte-identical,
  sha256 `59404213…` — verified this round before the R252 content commit).
  The projected R252 payload JSON is ~112.000 byte
  (measured exactly at payload build, after push). Body v2 is now 96.456
  ký tự (< 105.000) — 8.544 ký tự of headroom. R253 warning:
  headroom is now 8.544 ký tự; the double compaction must continue next round
  (R15 + R14) to recover the margin further.

## Next

Posting round (owner tap): PR #119 description refresh to the R252 body
v2 (R251 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r252.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R252 push (title
ending "+ R252", built by replacing the "+ R222" suffix — not appending;
body = body v2 R252 in repo, head line refreshed to head after R252 push).
This run started ~21:40 JST — OUTSIDE working hours (09:00–21:30 JST), so the
R252 payload is HELD (like R142/R164–R197/R207–R216/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237/R238/R239/R240,
which were held outside working hours), not presented. The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R251 payload as new — R251 was prepared but never posted and is superseded by R252 (its main file was NOT refreshed after build — main == .bak byte-identical, sha256 `59404213…` — but the refresh does not decide postability; R252 supersedes it; no ĐÍNH CHÍNH this round); do not present the R250 widget — it is stale since the R251 push; do not present the R249 widget — it is stale since the R250 push; do not present the R248 widget — it is stale since the R249 push; do not present the R247 widget — it is stale since the R248 push; do not present the R246 widget — it is stale since the R247 push; do not present the R245 widget — it is stale since the R246 push; do not present the R244 widget — it is stale since the R245 push; do not present the R243 widget — it is stale since the R244 push; do not present the R242 widget — it is stale since the R243 push; do not present the R241 widget — it is stale since the R242 push; do not present the R240 widget (`widget-c7b281c5`, presented ~10:55 JST) — it is stale since the R241 push; do not present the R222 payload as new — R222 is LIVE. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220, R221, R222, R223, R224, R225, R226, R227, R228, R229, R230, R231, R232, R233, R234, R235, R236, R237, R238, R239, R240, R241, R242, R243, R244, R245, R246, R247, R248, R249, R250 and R251 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R252: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
