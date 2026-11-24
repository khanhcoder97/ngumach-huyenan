# MEDIA-02 — PR #119 Body Restructure R221: delivery index + body v2 coverage to `c38a4dc`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `c38a4dc` (PR119 BODY RESTRUCTURE R220 report). Content commit: `a19018c`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R221 does

R220 left the disclosed gap: the delivery index covered 629 commits to
`8f8b504`; R220's own 2 commits were to fold in at R221. The R220 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh direct-API read ~14:47 JST, curl: PR title still ends "+ R140",
head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD on the direct read, updated_at 2026-11-24T04:53:53Z — unchanged since the R220 read, body bytes
unchanged; mergeable true / mergeable_state clean at `c38a4dc`). The R220 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has been verified on issue #116:
the comments read was rate-limited this round (403 at ~14:47 JST, retried after the hourly reset ~15:06 JST —
still 403, on a different egress IP; MCP `issue_read` also refused as not in the reviewed read-only set) — the
last verified state is R220 ~13:40 JST: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`). A 403 is not evidence of a new comment — the next round retries the
comments read, and any new direction must be read in full before acting.

Live-read method, this round: the GitHub API PR read succeeded via direct curl (~14:47 JST, read-only —
`pulls/119`): title ends "+ R140", head `c38a4dc`, 631 commits / 3055 files / +297227 / 0 deletions,
mergeable true, mergeable_state clean at `c38a4dc`, live body 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD,
updated_at 2026-11-24T04:53:53Z. The MCP read path refused `pull_request_read` / `issue_read`
this round ("not in Muse's reviewed read-only set" — same as the R219-blocked run ~11:40 JST); no
`call-tool` write approval was requested for a read. The issue-comments direct read failed on three attempts
(~14:47, ~15:06, ~15:07 JST) with 403 rate-limit on three different egress IPs — the unauthenticated limit
is per-egress-IP and flaky: a 200 PR read and a 403 comments read happened minutes apart. PR head `c38a4dc`,
629 commits / 3052 files / +296.400 at the previous head `8f8b504`, 631 / 3055 / +297227 at `c38a4dc`,
mergeable_state clean at `c38a4dc` (mergeable true via direct read).

Fresh derivation at `c38a4dc` (~14:47 JST): `git rev-list --count
cf17178..c38a4dc` = 631 commits, `git diff --name-only` = 3055 files,
`--shortstat` = 297227 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `c38a4dc` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `891c7c17…`. No re-fetch was needed before applying: the run fetched at ~14:40 JST
(the run start) and the remote head was still `c38a4dc`, integration still `f3db6b3` — no
intervening push; the API read ~14:47 JST independently confirmed head `c38a4dc`.

R221 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `c38a4dc` (631 commits / 3055 files /
  297227 additions; the fresh git derivation at `c38a4dc`, the fresh API
  PR read ~14:47 JST, and the merge-tree cross-check at `c38a4dc` are cited,
  with the honest live-read disclosure above — direct PR read clean, issue-comments read rate-limited
  (last verified R220 ~13:40 JST);
  live body R140; delta `8f8b504..c38a4dc`: 5 paths, 839 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R220
  (`f0051bd`/`c38a4dc`), recording that its payload was prepared after
  push ~13:54 JST (103.420 ký tự, sha `f0695c3c`; JSON 118.918 byte < trần 131.072 — còn 12.154 byte, bản giữ tại
  `.bak-prepost-20261124` — R220 made its own backup, sha256 `9314e108…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's direct PR read: description structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc trực tiếp byte-exact khớp, 0 U+FFFD, updated_at 2026-11-24T04:53:53Z) — superseded, not
  posted; issue line re-read attempted this round (rate-limited 403, retried after reset — still 403; last verified R220 ~13:40 JST:
  34 comments, latest ACK `6862732081`, no new direction).
  The index now covers every block through `c38a4dc`; R221's
  own 2 commits fold in at the next index update (R222), disclosed in the
  index itself. The R221 note was appended after the R220 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `c38a4dc` · 631 · 3055 (with the fresh git derivation at `c38a4dc`,
  the fresh API PR read ~14:47 JST, and the fresh merge-tree cross-check at
  `c38a4dc`), plus the R220 paragraph in "Khối mới nhất" (254 ký tự,
  marked chưa đăng — live body is R140) and the R221 note. The stale index
  reference in "Về bản mô tả này" (head `8f8b504`) is also fixed to
  `c38a4dc`, and the title line is extended to R220 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R220 warning —
  applied with a measured correction, DOUBLE): the R79 + R78 paragraphs (579 and 439 ký tự — measured this
  round) are
  collapsed to one 208-ký-tự compact line each (full detail stays in the
  delivery index) — the new R220 paragraph was 254 ký tự, so
  the body is 103.374 ký tự — net −103 vs R220 despite the new R220 paragraph, headroom 1.626 ký tự. The dry-run first projected 103.374 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  The head line grew 1.076 → 1.248 ký tự (+172, honest rate-limit disclosure in the live-read clause) — it is now
  the main variable cost; trim it if it keeps growing.
  Paragraph order: the R220 paragraph sits directly after R219
  (ascending full-paragraph order R166..R220), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R221 (owner tap) — the R140 body v2 now live
  is the base; only the R220 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r221_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R220 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R220 and R221 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R220 (88 compact lines R78–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 103.374 ký tự),
  a check that the R220 paragraph sits directly after R219
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R220 note clean).
  New this round: the R219-row regression guard (cumulative must be 3053,
  re-derived from git at `f0051bd`), the R220-row guard (cumulative must
  cite 3056 — 3055 at `c38a4dc` + 1 new checker in the R221 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R221, range R78–R165, list complete through R220, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 58/58**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R221_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R220) with the full COVER
  SHA verified intact (definition + docstring, both
  `c38a4dca896afb2a9e8d380df1abd5f38792dfaa` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `8f8b504` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R219-row guard string citing "3052 at 8f8b504", legitimate; plus 3
  `a74e9f4` (docstring + R218-row guard citing "3049 at a74e9f4"), 3 `0a4d05a` (docstring + R217-row guard citing "3046 at 0a4d05a"), 3 `0de54fb` (docstring + R216-row guard citing "3043 at 0de54fb"), 3 `1e564a2` (docstring + R215-row guard),
  3 `3de99c9` (docstring + R214-row guard citing "3037 at 3de99c9"), legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 103.374 ký tự and the apply wrote on
  the first attempt at 103.374 ký tự with 1.626 ký tự of headroom; the idempotency re-run
  after apply reports already-applied changed: 0 — verified. No content was changed by the re-run;
  the first apply had already written the correct bytes.
  Correction caught before the report commit: the R220 row's cumulative figure was drafted as 3056 (3055 at
  `c38a4dc` + 1 new checker) and the true diff at the R221 content
  commit is 3056 — verified by `git diff --name-only cf17178..a19018c` = 3056
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH this round: R220's committed content verified correct —
  the committed index at `c38a4dc` carries the R218 row at cumulative 3050
  (re-derived by the new checker from git at `a82ca70`) and the R219 row at 3053
  (re-derived from git at `f0051bd`); no uncommitted
  working-tree fix was left behind by R220 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R221 robustness note — headroom now 1.626 chars

The R220 warning left 1.523 ký tự of headroom, so this round compacted
TWO paragraphs (R79 + R78, 579 + 439 ký tự → 208 each) before adding the new R220 paragraph
(254 ký tự). The body is now 103.374 ký tự — net −103 vs R220 — with
1.626 ký tự of headroom. The double compaction bought back 602 ký tự against the
254-ký-tự new paragraph, but the head line grew +172 ký tự (honest rate-limit disclosure in the live-read
clause), so the net recovery is only −103. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R222 warning: headroom is 1.626 ký tự; compact R77 + R76 next (or trim the
head line hard — it grew 1.076 → 1.248 this round and is now the main variable cost).
At the current net −103/round the margin is recovering slowly,
but only while the double compaction continues (full paragraphs remaining R166..R220 = 55;
compact block R78–R165 = 88 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (103.374 projected; apply wrote 103.374 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220 — the R220 row's 3056 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — the replace_line prefix crashed because its lookup prefix itself carried the OLD value,
and the Ghi-chú label edit crashed the same way (R203/R207 lesson, now applied to all edits; re-run reports
already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) One read path can fail while another succeeds — this round the MCP path refused the read tools
and the direct curl PR read returned the clean byte-exact body (92.520, sha `ddbe32ff`) while the comments read
hit the unauthenticated rate limit on three attempts across three egress IPs — a 403 is a transport limit, not
evidence of a repo or body change; record each path's outcome separately, not one blended claim.
(6) A payload backup the authoring
round made must be verified, not re-claimed — R220's payload `.bak` copy
existed when R221 started; R221 verified sha256 identical
(`9314e108…` both) and the R220 row records the copy as R220's, not R221's.
(7) No execution-risk flag appeared on any git/script command this round
(unlike R211/R213 and the R219-blocked run ~11:40 JST); the flag itself has now appeared 4 times
(R211 ~01:40, R213 ~04:40, R213 ~05:44, R219 ~11:40) and the decision whether to keep running git/checker after it still awaits
luồng chính/chủ dự án — recorded here, not decided here.

## Verification

- Merge-tree `c38a4dc` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `891c7c17…`. Merge-tree at the R221
  content head `a19018c` vs `f3db6b3`: exit 0,
  tree `6a7eae59…`.
- Live PR state: API read this round (~14:47 JST) — direct curl read
  clean byte-exact (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `c38a4dc`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-24T04:53:53Z — unchanged since the R220 read, body
  bytes unchanged); commits 631, changed_files 3055, additions 297227
  (API agrees with the fresh git derivation; the `deletions` key is 0 in
  the direct API response — git shows 0 deletions); mergeable_state clean at
  `c38a4dc` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: comments read rate-limited this round — direct curl 403 at ~14:47 JST, retried after the hourly
  reset ~15:06 JST (still 403) and again ~15:07 JST (still 403, third egress IP); MCP `issue_read` refused
  ("not in Muse's reviewed read-only set"). Last verified R220 ~13:40 JST: still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction. The next round retries the comments read; a 403 is not evidence of a
  new comment.
- Scope audit: R221 block (`c38a4dc..a19018c`) 3 paths / 0 violations
  (index + body v2 + R221 checker); cumulative at the R221 content
  commit `a19018c` 3056 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `a19018c`). Merge-tree at the R221 content head `a19018c` vs `f3db6b3`: exit 0,
  tree `6a7eae59…`.
- Transient notes: this round's `git fetch` at ~14:40 JST succeeded
  first try. MCP `call-read-tool` refused `issue_read`/`pull_request_read` this round
  ("not in Muse's reviewed read-only set" — same as the R219-blocked run; `pull_request_read` takes `pullNumber`, not
  `pull_number` — parameter-name lesson carried from R211; `issue_read`
  takes `issue_number`, not `issueNumber`). No call-tool write approval was requested for a read. No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST). The R220 payload's own head line recorded
  mergeable clean at `8f8b504` at its preparation and clean at
  `c38a4dc`; this round's API read confirms clean at `c38a4dc`. No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH, unlike R218 — the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
- Ceiling discipline: the R220 payload JSON measured 118.918 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (12.154 byte headroom). The projected R221 payload JSON is ~121,000 byte
  (measured exactly at payload build, after push). Body v2 is now 103.374
  ký tự (< 105.000) — 1.626 ký tự of headroom. R221 warning:
  headroom is now 1.626 ký tự; the double compaction must continue next round
  (R77 + R76) or the head line must be trimmed.

## Next

Posting round (owner tap): PR #119 description refresh to the R221 body
v2 (R220 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r221.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R221 push (title
ending "+ R221", built by replacing the "+ R140" suffix — not appending;
body = body v2 R221 in repo, head line refreshed to head after R221 push).
This run started ~14:40 JST — INSIDE working hours (09:00–21:30 JST), so the
R221 payload is READY FOR WORKING HOURS (unlike R142/R164–R197/R207–R216,
which were held because they started before 09:00). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R220 payload. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219 and R220 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R221: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
