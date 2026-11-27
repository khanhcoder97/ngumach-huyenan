# MEDIA-02 — PR #119 Body Restructure R253: delivery index + body v2 coverage to `8e4d8ac`

Date: 2026-11-25 (JST; lượt chạy bắt đầu ~23:40 JST, content commit ~00:16 JST 2026-11-26). Branch: `muse/media-production-20261104`.
Coverage head: `8e4d8ac` (PR119 BODY RESTRUCTURE R252 report). Content commit: `cec686f`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R253 does

No ĐÍNH CHÍNH lớn this round, except the payload-size projection note below:
the R252 report projected the R252 payload JSON at ~112.000 byte
"measured exactly at payload build", but the file on disk is 108.402 byte
(sha256 `b597575d…`, main == .bak byte-identical) — the R252 index row now
cites the disk-measured figure. No new Codex/owner direction has
been verified on issue #116: 34 comments, latest ACK `6862732081`
(CP5 + M-G CP10 + R2); no new direction since Gói 39 (`6815238814`).

Fresh derivation at `8e4d8ac` (~23:47 JST): `git rev-list --count
cf17178..8e4d8ac` = 695 commits, `git diff --name-only` = 3151 files,
`--shortstat` = 341534 insertions, 0 deletions — agreeing exactly with
the connector PR read. `git merge-tree --write-tree` `8e4d8ac` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `19b0d4af…`. The run
fetched at ~23:40 JST (the run start) and the remote head was still
`8e4d8ac`, integration still `f3db6b3` — no intervening push; the
connector PR read ~23:47 JST independently confirmed head `8e4d8ac`. The live PR read this round (~23:47 JST,
connector `pull_request_read`, read-only — the connector ACCEPTED the read
this round, unlike R252 where it rejected it and the reads fell back to
the public API via curl): title ends "+ R222", head `8e4d8ac`,
695 commits / 3151 files / +341534, mergeable null (GitHub computing at
read time), mergeable_state clean at `8e4d8ac`, live body 103.023 ký tự,
sha `1dd61afd`, 0 U+FFFD — byte-exact with the R222 payload,
updated_at 2026-11-25T13:10:44Z — changed from the R252 read
(2026-11-25T11:55:56Z) because the R252 push updated the head; the body
bytes are unchanged, still R222.

R253 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  title head refreshed to `8e4d8ac`; milestone lines refreshed to head
  `8e4d8ac` (695 commits / 3151 files / 341534 additions; the fresh git
  derivation at `8e4d8ac`, the fresh connector PR read ~23:47 JST, and
  the merge-tree cross-check at `8e4d8ac` are cited, with the live body
  R222 read back byte-exact this round — 0 U+FFFD, single clean read);
  delta `fa41682..8e4d8ac`: 2 paths, 1074 insertions, 0 deletions);
  one row appended — PR119 BODY RESTRUCTURE R252 (`fa41682`/`8e4d8ac`),
  recording that its payload was prepared after the R252 push (~22:11 JST,
  96.507 ký tự, sha `adf301cd`; JSON 108.402 byte
  < trần 131.072 — còn 22.670 byte, bản giữ tại
  `.bak-prepost-20261124/` — sha256 `b597575d…`, as-built figures
  measured from disk this round, NOT the R252 report's ~112.000-byte
  projection) and then
  NOT posted (live body still R222 as read this round ~23:47 JST); the
  R252 row also records the stale R251 widget (head has moved to
  `8e4d8ac` — do NOT tap; present the R252 widget instead); no separate
  ACK for R252. ĐÍNH CHÍNH nhỏ (see above): the R252 report's projected
  payload JSON size (~112.000 byte) is corrected to the disk-measured
  108.402 byte in the R252 row.
  The index now covers every block through `8e4d8ac`; R253's own 2
  commits fold in at the next index update (R254), disclosed in the index
  itself. The R253 note was appended after the R252 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `8e4d8ac` · 695 · 3151 (additions `341534`, Gói 39 ID `6815238814`,
  tree `19b0d4af…`; with the fresh git derivation at `8e4d8ac`,
  the fresh connector PR read ~23:47 JST, and the fresh merge-tree
  cross-check at `8e4d8ac`), plus the R252 paragraph in "Khối mới nhất"
  (270 ký tự text + 1 line break = 271 ký tự, marked chưa đăng — payload
  prepared after push ~22:11 JST, live body still R222) and the R253 note. The stale index
  reference in "Về bản mô tả này" (head `7ca1f05`) is also fixed to
  `8e4d8ac`, the "lượt cập nhật này" sentence is advanced R252 → R253,
  and the compaction trail gains
  "R253 đã gọn thêm các đoạn R15 + R14." (36 ký tự + 1 leading space = 37). The title line is
  extended to R252 (APPENDED, not replaced — see the R176 robustness
  note; the append measures 30 ký tự). Compaction (R252 warning —
  applied as a true double compaction this round): the R15 paragraph
  (412 ký tự — measured this round, full paragraph verified present)
  and the R14 paragraph (412 ký tự — measured this round, full paragraph
  verified present; the pair DOES share a length this time — 412/412)
  are each collapsed to one
  207-ký-tự compact line.
  Full detail stays in the delivery index; the checker asserts < 400,
  not an exact 207. The new R252 paragraph was 271 ký tự, so the body
  is 96.441 ký tự — net −15 vs R252 (the double compaction resumed:
  −205 R15 compaction − 205 R14 compaction + 271 new paragraph + 37
  trail append + 30 title append + 5 Ghi-chú list append ("/R252") + 52
  head-line delta), headroom 8.559 ký tự. The dry-run first projected
  96.441 ký tự and the apply wrote exactly that — measure, then trim,
  then apply.
  Paragraph order: the R252 paragraph sits directly after R251
  (ascending full-paragraph order R166..R252), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R253 (owner tap) — the R222 body v2 now live is the base;
  only the R252 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r253_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R252 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R252 and R253 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R252 (152 compact lines R14–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 96.441 ký tự),
  a check that the R252 paragraph sits directly after R251
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237/R238/R239/R240/R241/R242/R243/R244/R245/R246/R247/R248/R249/R250/R251 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R252 note clean).
  New this round: the R252-row guard (cumulative must cite 3152 —
  3151 at `8e4d8ac` + 1 new checker in the R253 content commit,
  verified in this report after the content commit), the ĐÍNH CHÍNH R242
  guard carried (the R241 row must carry the note with sha `83d221b8`), the R36-restoration
  guard carried (the R36 compact line must exist with content `386216b` and head
  `9ec1fd9`), the ĐÍNH CHÍNH R241 guard carried (the R239 row must carry
  the note with sha `1e38e781`), the body "Ghi chú" line correction
  guard (R158/R253, range R15–R165, list complete through R252, no double
  slash), the "lượt cập nhật này" sentence correction guard (full
  corrected sentence present; the defective "chính R252" form absent),
  the lesson-36 head-line guard (additions `341534` and Gói 39 ID
  `6815238814` present in the head line; `6835238814` and `339439`
  absent from the body), and the working-tree guard (`git status --porcelain` lists exactly the
  3 intended paths — index + body + this checker — no stray modification
  may survive past the report commit).
  **PASS 128/128**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R253_VALIDATION_20261125.json`).
  The checker passed 128/128 on its first run against the applied tree.
  The checker was generated from R252 by a transform script (not
  sed-copied) with the full COVER SHA verified intact (definition +
  docstring, both `8e4d8ac3d63ce31503468c2937a846c2bd938476` — re-derived
  from `git rev-parse` this round) and a stale-reference grep (57 shas
  verified, counts measured dynamically) after the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The SHA-hits paragraph was regenerated by a second
  script that greps the generated checker (57 shas, line counts measured
  dynamically, locations classified from the actual matching lines).
  The edit script's budget check ran before any write (R166 lesson): the
  dry-run simulation projected 96.441 ký tự and the apply wrote on
  the first attempt at 96.441 ký tự, with 8.559 ký tự of headroom; the
  idempotency re-run after apply reports already-applied changed: 0 —
  verified (the re-run reported changed: 0 on the first clean re-run).
  The R252 paragraph's first draft measured 270 chars exactly (no fix
  needed); the edit script asserts the exact 270 before writing — see lesson 26
  of R242, carried; the two compact lines each measured exactly 207 chars on the first attempt.
  The documents were correct after the fix; the
  checker passed 128/128 on its (re-)run against the applied tree,
  writing the repo validation JSON in the same run.
  The R252 row's cumulative figure was drafted as 3152 (3151 at `8e4d8ac` + 1 new checker in the R253 content commit) and the true diff at the R253 content commit is 3152 — verified by
  `git diff --name-only cf17178..cec686f` = 3152 after the content commit.
  The R251 row's cumulative 3149 was re-derived from git at `fa41682`
  (`git diff --name-only cf17178..fa41682` = 3149) and by the checker's
  row-convention loop (R251 cumulative 3149 == diff at `fa41682` — PASS).
  `git status --porcelain` after the content commit showed only the
  intended validation JSON untracked — no leftover edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R252's committed content this round apart from the
  payload-size projection note above: R252's committed content verified correct —
  the committed index at `8e4d8ac` carries the R250 row at cumulative 3146
  (re-derived by the new checker from git at `a6319ed`) and the R251 row at 3149
  (re-derived from git at `fa41682`); no uncommitted
  working-tree fix was left behind by R252 (the working tree was clean at this
  run's start apart from the R252 commits already pushed, and the fetch found no intervening push). No payload refresh happened this round
  (R252 main == .bak byte-identical, sha256 `b597575d…`) — unlike R241
  (refreshed ~11:54 JST, corrected at R242/R243).

## SỬA TRƯỚC PUSH

Không có sửa trước push lượt này: the maker (`make_build_checker_r253.py`),
the builder (`build_checker_r253.py`), the fill script
(`fill_sha_hits_r253.py`) and the edit script (`edit_pr119_r253.py`) all
ran cleanly on their first attempt — no placeholder defect (unlike R252
pre-push fix (1)), no builder-anchor defect (unlike R252 pre-push fix
(2)). The checker passed 128/128 on its first run; no regeneration,
no re-fill, no re-run was needed.

## R253 robustness note — headroom now 8.559 chars

The R252 warning left 8.544 ký tự of headroom; this round compacted
the R15 paragraph (412 ký tự → 207) and the R14 paragraph (412 ký tự → 207)
— a true double compaction, both full paragraphs verified present
before assuming their lengths (R242 lesson 9 held: R15 content
`92daf95`/head `406bc86`, R14 content `10b6a70`/head `18a8e6f`; the pair
DOES share a length this time, 412/412 — the R252 warning's "−527"
expectation did NOT carry: the R15+R14 pair saves −410, not −527).
The body is now 96.441 ký tự — net −15 vs R252 — with 8.559 ký tự of
headroom. The head line grew to 1.029 ký tự (delta +52, measured — the
connector-read wording is longer than the public-API wording, and the
mergeable-null clause is added), so the −15 is
fully accounted: −205 − 205 + 271 + 37 + 30 + 5 + 52.
The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R254 warning: headroom is now 8.559 ký tự; compact R13 + R12 next (a true
double compaction, −410 against the 271-ký-tự new paragraph at the R253
pair's measured saving) to recover the margin further.
At the current net the margin recovers once the double compaction resumes
(full paragraphs remaining R166..R252 = 87; compact block R14–R165 = 152 lines).
Lessons carried (short form — full text in the R252 report file, same
directory): (1) dry-run projection trusted over hand-count (title append
30, not 28); (2) a row's "cumulative N paths" counts the diff at the
AUTHORING round's content commit (R252 row's 3152 verified post-commit
by git diff, not assumed from the coverage head); (3) idempotency re-run
checks the NEW state first for EVERY edit (changed: 0 first clean re-run this
round); (4) append-style edits need the new-state check FIRST in
`sub_once` (new contains old); (5) `git status --porcelain` must be
EMPTY before push (only the validation JSON was untracked after the
content commit); (6) two backup locations can hold different versions —
the R241 payload's main was refreshed ~11:54 JST (see ĐÍNH CHÍNH R242
above), `.bak` keeps the as-built; (7) an `updated_at` that DOES move
while the body sha stays means a push touched the PR (updated_at
2026-11-25T13:10:44Z, changed from the R252 read 2026-11-25T11:55:56Z
because the R252 push updated the head; body sha unchanged `1dd61afd` = R222);
(8) a connector call that fails on a wrong parameter name is not a failed
read (`pullNumber`, not `pull_number`; `issue_number`, not
`issueNumber`; the reviewed method is `get_comments` — retried and
succeeded); (9) `issue_read` `get_comments` is paginated at 30
comments per page (30 + 4 = 34; latest ACK on page 2); (10) the
execution-risk flag has appeared 8 times (R211, R213×2, R219, R231,
R239, R240, R248) and the decision whether to keep running git/checker after
it still awaits luồng chính/chủ dự án — the R248 round was blocked by
it, and the R249 run retried the push cleanly; no flag appeared in the R253
round through the report-commit step; (11) mergeable_state is a
point-in-time read (the R252 payload's own head line, built ~22:11 JST,
honestly said unstable at `8e4d8ac` — CI was running on the new head,
last clean at `7ca1f05`; the fresh read ~23:47 JST says clean at
`8e4d8ac` (mergeable null, GitHub computing); the honest wording is the fresh
read); (12) a live-body read can need a re-read to come back clean (first
read 5 U+FFFD from transport mangling, re-read 0 U+FFFD, sha `1dd61afd`
= R222 — see lesson 35); (13) the checker writes its validation JSON at the
END of its run, AFTER the working-tree guard — delete the validation
JSON before a re-run; the guard asserts the PRE-commit tree, so a
re-run AFTER the content commit fails it by design (no re-run was needed
this round — the checker passed 128/128 on its first run, writing the
JSON once in the same run); (14) the compact-line count and
the per-round loop range can drift apart by one (this round: 152 lines
R14–R165, loop R14–R165 for the per-round check; the R36 restoration
guard is a separate check, not part of the loop count; the "Ghi chú"
range text reads R15–R165); (15) the R236 lesson
(16) held end to end (every edit through `il`/`bl`; dry-run =
apply; idempotency changed: 0; checker re-run PASS); (16) `find`
prefixes must not contain the OLD state + `sub_line`'s new-state guard
must be `if new in line: return 0` ALONE (three R247 guard fixes, see
pre-push fix (2) — the chained-timestamp case also needs ONE atomic sub
when the second replacement's NEW value equals the first's OLD value);
(17) inserting a paragraph adds its line break too (+271 for a 270-char paragraph; R253 net −15
likewise measured, not hand-counted — the double-compaction terms are
the ones a hand-count would most likely miss); (18) the checker total
is derived from the checker run itself (128/128 printed + validation
JSON), never from a naive textual count (128 = 126 (R252) + 1 new R252-row
check + 1 row-convention R251 tuple); (19) the SHA-hits paragraph is filled
by a second script that greps the generated checker (57 shas verified
this round, counts measured dynamically, locations classified from the
actual matching lines); (20) a payload's head line
stamps its build/refresh read's actual time (the R252 payload build
reads ~22:11 JST, matching its build time; no refresh happened
this round — main == .bak; the latest refresh remains the R241 main
~11:54 JST (verified at R242/R243, recorded in the R241 index row)); (21) a transform script
that generates the next round's checker build script must survive escape
processing — plain `str.replace` for REPLACEMENTS, backslash
normalisation only inside REPLACEMENTS (this round's generator ran clean
on its first attempt with no pre-push fixes; the R252 round's fixes
(1)–(2) did not recur); (22) the working-tree guard asserts the PRE-commit tree —
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
loop now covers R14–R165. This round both paragraphs of the pair (R15,
R14) were verified present (412 and 412) before compaction.
(26) (carried from R243) — the new-paragraph first draft measured 271 chars,
not 270: fixed by dropping the "~" before "12:08" (the push time is
exact from the queue log); the edit script asserts the exact 270 before
writing, so a hand-count error fails loudly instead of shipping a
1-char-long
paragraph. Trust the script's assert, never the hand-count.
(27) (carried from R243 — re-verified this round) — the index row's "delta" cites the authoring
round's own content..report diff (`fa41682..8e4d8ac`: 2 paths, 1074
insertions) — NOT the difference between coverage-head insertion
totals (341534 − 339439 = 2095 is the wrong number; the report commit
adds only its own report md + validation json). The R252 report's
delta line already used the right figure; this round re-verified it
from git before writing the R252 row.
(28) (carried from R244) — a transform script that slices a paragraph out of a
generated file must slice by the paragraph's OWN boundaries, not by a
later structural marker: the first version of the R244 generator
sliced the SHA-hits paragraph out to the docstring close (`"""`) and
deleted every paragraph after it (corrections, live-body note, payload
paragraph, lessons). Caught by the stale-reference grep before any
commit (f021c08/3c076bf counts 2 instead of 3/4); fixed by slicing by
LINES to the paragraph's own closing line, then rebuilding
and re-verifying all sha counts (this round: 57 sha counts, all
verified — see lesson (35) above). NOTE this round: the builder-level
SHA_START/assert anchors needed NO fix (the R252 builder's anchors cite
`1281cde`, the R253 builder's cite `7ca1f05` — the shift is mechanical);
the R252 round's anchor fixes (pre-push fixes (1)–(2)) did not recur.
(29) (carried from R244) — the new-paragraph first draft measured 260 chars,
not 270: fixed by adding "chuẩn bị " + "~" (+10: "chuẩn bị xong sau
push ~13:04 JST"); the edit script asserts the exact 270 before
writing, so a hand-count error fails loudly instead of shipping a
short paragraph. Trust the script's assert, never the hand-count.
(30) (carried from R245) — no payload refresh happened this round (R252 main
== .bak byte-identical, sha256 `b597575d…`, verified from disk), so no
ĐÍNH CHÍNH is needed beyond the projection note above; a refresh must still be recorded with BOTH
versions (main vs `.bak`) when it happens, with the index-row
correction at the NEXT index update (R241 precedent).
(31) (carried from R245) — the compaction pair (R31 + R30) was verified
present before assuming its lengths: R31 measured 493 chars but R30
measured 552 chars, NOT 493 — the two paragraphs are NOT the same
length (R30 carries the longer quiet-hours payload sentence), so the
double compaction saved −286 + −345 = −631, not −572; never assume a
pair shares a length, measure both. The R246 payload was NOT built by
the R245 round (its report promised it after the push, but the round
ended at the report commit + push); R247 built it late (~14:47 JST,
body 98,475 chars, sha `4a3befc6`, JSON 111,339 bytes, main == .bak
sha256 `4d89565d`) so the R245 index row could cite real
figures — a promised payload is a deliverable, not a footnote.
(32) (carried from R245) — stale carried text in the checker docstring/code
comments drifts a round behind if nobody re-reads it: R245 fixed
three — the Ghi-chú correction paragraph said "R234 also corrects"
(the correction described is R245's), the execution-risk note said
"This R243 round proceeds" (in the R244 checker), and two code comments
were stale ("R158/R238, range R45-R165, through R237" and "R237 after
R236"). All four now cite R253/R252; the checker asserts the corrected
values, not the comments, but the comments are the next reader's map.
This round the same class was checked again: the maker's placeholder dict
carries distinct keys per token class (lesson 42) and the builder-level
SHA_START/assert cite the current round's shas — both verified by the
post-generation grep before any commit.
(33) (carried from R245) — a payload builder that applies a global time
replacement before a time-specific one silently breaks the specific
one: the first R244-payload build replaced `~13:44 JST` globally, then
asserted the issue_read citation still contained `~13:44 JST` — caught
by the assert (expected 1, found 0); fixed by ordering the specific
replacement first. Order replacements specific-before-global, and keep
the assert. NOTE this round: no chained timestamp sub was needed — the
R253 head line's updated_at changed from the R252 read (11:55:56Z →
13:10:44Z, push note added), and the head line is replaced whole
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
sub, and the checker now asserts additions `341534` and ID `6815238814`
in the head line and the absence of `6835238814` and `339439` from the
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
the current figures (`341534 − 339439 = 2095` is the wrong number).
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
the expected total every round (128 = 126 + 1 new row check + 1
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
(45) NEW THIS ROUND (R253) — a report's payload-size projection is not a
measurement: the R252 report wrote the R252 payload JSON as "~112.000
byte (measured exactly at payload build)", but the file on disk is
108.402 byte (sha256 `b597575d…`, main == .bak byte-identical) — the
projection was ~3.600 byte high. The R252 index row now cites the
disk-measured 108.402 byte. The payload JSON is written after the
report commit, so the report can only project it — the next round's
row must re-measure from disk, never carry the projection as fact.
The connector read path worked again this round (`call-read-tool`
accepted `issue_read` and `pull_request_read`, unlike R252 where it
rejected them) — record the actual read path each round, not the
previous round's. The R15 + R14 compaction pair DOES share a length
(412/412, saving −410) — the R252 warning's "−527" expectation did not
carry; a pair's saving is measured each round, never inherited.

## Verification

- Merge-tree `8e4d8ac` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `19b0d4af…`. Merge-tree at the R253
  content head `cec686f` vs `f3db6b3`: exit 0,
  tree `93214a50…`.
- Live PR state: connector read this round (~23:47 JST) — single clean
  read (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD — byte-exact with the
  R222 payload; updated_at 2026-11-25T13:10:44Z — changed from the R252
  read, body bytes unchanged); mergeable null / mergeable_state clean at `8e4d8ac`
  (connector read this round). `get_status` was NOT read this round;
  the PR `get` read's mergeable_state is the operative state. Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: 34 comments, latest ACK `6862732081` (CP5 + M-G CP10
  + R2); no new Codex/owner direction since Gói 39 (`6815238814`).
  The 5 comments after Gói 39 are all Muse ACKs of completed work, not new direction.
- Scope audit: R253 block (`8e4d8ac..cec686f`) 3 paths / 0 violations
  (index + body v2 + R253 checker); cumulative at the R253 content
  commit `cec686f` 3152 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `cec686f`). Merge-tree at the R253 content head `cec686f` vs `f3db6b3`: exit 0,
  tree `93214a50…`.
- Transient notes: this round's `git fetch` at ~23:40 JST succeeded on
  the first try (remote head still `8e4d8ac`, integration still `f3db6b3`);
  no transient fetch failure this round (unlike R246/R252). The
  connector read path WORKED this round — `call-read-tool` accepted
  `issue_read` and `pull_request_read` (read-only, no write approval
  requested for a read). No execution-risk flag this round
  through the report-commit step. No git-lfs
  hook warning appeared at the content commit (the files are text-only
  in any case, so no LFS smudge was involved; the push below uses the
  documented env).
  `git add -N` was NOT needed this round: the scope audit runs on commits
  (base..head), not the working tree, so the new checker counted in the
  block diff via the content commit itself. The checker emits a
  `SyntaxWarning: invalid escape sequence '\`'` on its docstring (the
  `\`` sequences in the R235 lesson text) — warning only, same shape as
  the R252 checker file, `py_compile` exit 0, checks unaffected.
- Ceiling discipline: the R252 payload JSON as-built measured 108.402 byte
  (prepared after the R252 push ~22:11 JST, NOT posted — live body is still R222, verified by this round's connector read),
  vs the 131.072-byte transport ceiling
  (22.670 byte headroom); the main file was NOT refreshed after the R252 build (main == .bak byte-identical,
  sha256 `b597575d…` — verified this round before the R253 content commit).
  The projected R253 payload JSON is ~108.000 byte
  (measured exactly at payload build, after push). Body v2 is now 96.441
  ký tự (< 105.000) — 8.559 ký tự of headroom. R254 warning:
  headroom is now 8.559 ký tự; the double compaction must continue next round
  (R13 + R12) to recover the margin further.

## Next

Posting round (owner tap): PR #119 description refresh to the R253 body
v2 (R252 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r253.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R253 push (title
ending "+ R253", built by replacing the "+ R222" suffix — not appending;
body = body v2 R253 in repo, head line refreshed to head after R253 push).
This run started ~23:40 JST — OUTSIDE working hours (09:00–21:30 JST), so the
R253 payload is HELD (like R142/R164–R197/R207–R216/R228–R252,
which were held outside working hours), not presented. The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R252 payload as new — R252 was prepared but never posted and is superseded by R253 (its main file was NOT refreshed after build — main == .bak byte-identical, sha256 `b597575d…` — but the refresh does not decide postability; R253 supersedes it; the ĐÍNH CHÍNH this round is only the payload-size projection note above); do not present the R251 widget — it is stale since the R252 push; do not present the R250 widget — it is stale since the R251 push; do not present the R249 widget — it is stale since the R250 push; do not present the R248 widget — it is stale since the R249 push; do not present the R247 widget — it is stale since the R248 push; do not present the R246 widget — it is stale since the R247 push; do not present the R245 widget — it is stale since the R246 push; do not present the R244 widget — it is stale since the R245 push; do not present the R243 widget — it is stale since the R244 push; do not present the R242 widget — it is stale since the R243 push; do not present the R241 widget — it is stale since the R242 push; do not present the R240 widget (`widget-c7b281c5`, presented ~10:55 JST) — it is stale since the R241 push; do not present the R222 payload as new — R222 is LIVE. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220, R221, R222, R223, R224, R225, R226, R227, R228, R229, R230, R231, R232, R233, R234, R235, R236, R237, R238, R239, R240, R241, R242, R243, R244, R245, R246, R247, R248, R249, R250, R251 and R252 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R253: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
