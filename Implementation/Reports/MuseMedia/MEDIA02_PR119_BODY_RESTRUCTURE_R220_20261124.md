# MEDIA-02 — PR #119 Body Restructure R220: delivery index + body v2 coverage to `8f8b504`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `8f8b504` (PR119 BODY RESTRUCTURE R219 report). Content commit: `f0051bd`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R220 does

R219 left the disclosed gap: the delivery index covered 627 commits to
`a74e9f4`; R219's own 2 commits were to fold in at R220. The R219 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API reads ~13:40 JST, MCP + direct curl: PR title still ends \"+ R140\", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD on the direct read, updated_at 2026-11-24T03:53:53Z — bumped by the R219 push updating the PR head, body bytes
unchanged). The R219 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh reads agree: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~13:40 JST, read-only —
`issue_read get_comments` page 1 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read of the issue comments and of the PR with curl as cross-check): the MCP read
agreed on the PR title (ends "+ R140") and the visible head of the body; the direct read returned the
CLEAN body (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — the direct
read is authoritative for the byte-exact body, since the MCP output was truncated by the tool's own
display limit this round (NOT a body change and NOT the "Ă" → U+FFFD mangle of R209/R215/R218). The issue-comments direct read also
succeeded (34 comments, latest `6862732081`) and agrees with the MCP read
(MCP returns page 1 only, 30 comments — the remaining 4 are paginated, as
in earlier rounds). PR head `8f8b504`,
629 commits / 3052 files / +296.400, mergeable_state clean at `8f8b504` (mergeable true via direct read).

Fresh derivation at `8f8b504` (~13:40 JST): `git rev-list --count
cf17178..8f8b504` = 629 commits, `git diff --name-only` = 3052 files,
`--shortstat` = 296400 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `8f8b504` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `eca7b560…`. No re-fetch was needed before applying: the run fetched at ~13:40 JST
(the run start) and the remote head was still `8f8b504`, integration still `f3db6b3` — no
intervening push; the API read ~13:40 JST independently confirmed head `8f8b504`.

R220 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `8f8b504` (629 commits / 3052 files /
  296400 additions; the fresh git derivation at `8f8b504`, the fresh API
  reads ~13:40 JST, and the merge-tree cross-check at `8f8b504` are cited,
  with the honest mergeable reading disclosed above — MCP agreed on title + visible head, direct read clean;
  live body R140; delta `a74e9f4..8f8b504`: 5 paths, 827 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R219
  (`a82ca70`/`8f8b504`), recording that its payload was prepared after
  push ~12:53 JST (103.763 ký tự, sha `d03b637d`; JSON 119.381 byte < trần 131.072 — còn 11.691 byte, bản giữ tại
  `.bak-prepost-20261124` — R219 made its own backup, sha256 `8fe1eb4f…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's MCP + direct reads: description structure matches R140, PR title ends \"+ R140\", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc trực tiếp byte-exact khớp, 0 U+FFFD, updated_at 2026-11-24T03:53:53Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API reads ~13:40 JST).
  The index now covers every block through `8f8b504`; R220's
  own 2 commits fold in at the next index update (R221), disclosed in the
  index itself. The R220 note was appended after the R219 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `8f8b504` · 629 · 3052 (with the fresh git derivation at `8f8b504`,
  the fresh API reads ~13:40 JST, and the fresh merge-tree cross-check at
  `8f8b504`), plus the R219 paragraph in "Khối mới nhất" (254 ký tự,
  marked chưa đăng — live body is R140) and the R220 note. The stale index
  reference in "Về bản mô tả này" (head `a74e9f4`) is also fixed to
  `8f8b504`, and the title line is extended to R219 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R219 warning —
  applied with a measured correction, DOUBLE): the R81 + R80 paragraphs (569 and 569 ký tự — measured this
  round) are
  collapsed to one 208-ký-tự compact line each (full detail stays in the
  delivery index) — the new R219 paragraph was 254 ký tự, so
  the body is 103.477 ký tự — net −395 vs R219 despite the new R219 paragraph, headroom 1.523 ký tự. The dry-run first projected 103.477 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  Paragraph order: the R219 paragraph sits directly after R218
  (ascending full-paragraph order R166..R219), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R220 (owner tap) — the R140 body v2 now live
  is the base; only the R219 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r220_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R219 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R219 and R220 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R219 (86 compact lines R80–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 103.477 ký tự),
  a check that the R219 paragraph sits directly after R218
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R219 note clean).
  New this round: the R218-row regression guard (cumulative must be 3050,
  re-derived from git at `a82ca70`), the R219-row guard (cumulative must
  cite 3053 — 3052 at `8f8b504` + 1 new checker in the R220 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R219, range R80–R165, list complete through R219, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 56/56**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R220_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R219) with the full COVER
  SHA verified intact (definition + docstring, both
  `8f8b50440a67ee186217eb22f0fcfbdfb31918e3` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `a74e9f4` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R218-row guard string citing "3049 at a74e9f4", legitimate; plus 3
  `0a4d05a` (docstring + R217-row guard citing "3046 at 0a4d05a"), 3 `0de54fb` (docstring + R216-row guard citing "3043 at 0de54fb"), 3 `1e564a2` (docstring + R215-row guard),
  3 `3de99c9` (docstring + R214-row guard citing "3037 at 3de99c9"), legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 103.477 ký tự and the apply wrote on
  the first attempt at 103.477 ký tự with 1.523 ký tự of headroom; the idempotency re-run
  after apply reports already-applied changed: 0 — verified. No content was changed by the re-run;
  the first apply had already written the correct bytes.
  Correction caught before the report commit: the R219 row's cumulative figure was drafted as 3053 (3052 at
  `8f8b504` + 1 new checker) and the true diff at the R220 content
  commit is 3053 — verified by `git diff --name-only cf17178..f0051bd` = 3053
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH this round: R219's committed content verified correct —
  the committed index at `8f8b504` carries the R217 row at cumulative 3047
  (re-derived by the new checker from git at `a24895e`) and the R218 row at 3050
  (re-derived from git at `a82ca70`); no uncommitted
  working-tree fix was left behind by R219 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R220 robustness note — headroom now 1.523 chars

The R219 warning left 1.128 ký tự of headroom, so this round compacted
TWO paragraphs (R81 + R80, 569 + 569 ký tự → 208 each) before adding the new R219 paragraph
(254 ký tự). The body is now 103.477 ký tự — net −395 vs R219 — with
1.523 ký tự of headroom. The double compaction bought back 722 ký tự against the
254-ký-tự new paragraph, so the margin now holds while two paragraphs are
compacted per round; the head line stayed at 1.076 ký tự this round
(same as R219) — trim it again if it keeps growing. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R221 warning: headroom is 1.523 ký tự; compact R79 + R78 next (or trim the
head line hard). At the current net −395/round the margin is recovering,
but only while the double compaction continues (full paragraphs remaining R166..R219 = 54;
compact block R80–R165 = 86 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (103.477 projected; apply wrote 103.477 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219 — the R219 row's 3053 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — the replace_line prefix crashed because its lookup prefix itself carried the OLD value,
and the Ghi-chú label edit crashed the same way (R203/R207 lesson, now applied to all edits; re-run reports
already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two read paths settle
the live body faster than one mangled read did in R209 — the MCP path agreed on title + visible head
this round while the direct curl read returned the clean byte-exact body (92.520, sha `ddbe32ff`) — the direct
read is authoritative for the byte count; record both, not one.
(6) A payload backup the authoring
round made must be verified, not re-claimed — R219's payload `.bak` copy
existed when R220 started; R220 verified sha256 identical
(`8fe1eb4f…` both) and the R219 row records the copy as R219's, not R220's.
(7) No execution-risk flag appeared on any git/script command this round
(unlike R211/R213 and the R219-blocked run ~11:40 JST); the flag itself has now appeared 4 times
(R211 ~01:40, R213 ~04:40, R213 ~05:44, R219 ~11:40) and the decision whether to keep running git/checker after it still awaits
luồng chính/chủ dự án — recorded here, not decided here.

## Verification

- Merge-tree `8f8b504` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `eca7b560…`. Merge-tree at the R220
  content head `f0051bd` vs `f3db6b3`: exit 0,
  tree `9c1ad632…`.
- Live PR state: API read twice this round (~13:40 JST) — MCP read
  agreed on title + visible head (body not fully counted via MCP this round — output truncated by the tool's
  display limit, NOT a mangle) and direct curl read
  clean byte-exact (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — PR title ends
  \"+ R140\" (R140 posted live ~22:22 JST 2026-11-20); head `8f8b504`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-24T03:53:53Z — bumped by the R219 push updating the PR head, body
  bytes unchanged); commits 629, changed_files 3052, additions 296400
  (API agrees with the fresh git derivation; the `deletions` key is 0 in
  the direct API response — git shows 0 deletions); mergeable_state clean at
  `8f8b504` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API + direct curl of comments — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R220 block (`8f8b504..f0051bd`) 3 paths / 0 violations
  (index + body v2 + R220 checker); cumulative at the R220 content
  commit `f0051bd` 3053 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `f0051bd`). Merge-tree at the R220 content head `f0051bd` vs `f3db6b3`: exit 0,
  tree `9c1ad632…`.
- Transient notes: this round's `git fetch` at ~13:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (PR read body truncated by the tool's display limit — see live-read note; `pull_request_read` takes `pullNumber`, not
  `pull_number` — parameter-name lesson carried from R211; `issue_read`
  takes `issue_number`, not `issueNumber`). No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST). The R219 payload's own head line recorded
  mergeable clean at `a74e9f4` at its preparation and clean at
  `8f8b504`; this round's API read confirms clean at `8f8b504`. No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH, unlike R218 — the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
- Ceiling discipline: the R219 payload JSON measured 119.381 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API reads)
  vs the 131.072-byte transport ceiling
  (11.691 byte headroom). The projected R220 payload JSON is ~121,000 byte
  (measured exactly at payload build, after push). Body v2 is now 103.477
  ký tự (< 105.000) — 1.523 ký tự of headroom. R220 warning:
  headroom is now 1.523 ký tự; the double compaction must continue next round
  (R79 + R78) or the head line must be trimmed.

## Next

Posting round (owner tap): PR #119 description refresh to the R220 body
v2 (R219 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r220.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R220 push (title
ending \"+ R220\", built by replacing the \"+ R140\" suffix — not appending;
body = body v2 R220 in repo, head line refreshed to head after R220 push).
This run started ~13:40 JST — INSIDE working hours (09:00–21:30 JST), so the
R220 payload is READY FOR WORKING HOURS (unlike R142/R164–R197/R207–R216,
which were held because they started before 09:00). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R219 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218 and R219 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R220: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
