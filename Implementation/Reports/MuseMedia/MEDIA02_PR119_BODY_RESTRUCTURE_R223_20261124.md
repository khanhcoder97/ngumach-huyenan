# MEDIA-02 — PR #119 Body Restructure R223: delivery index + body v2 coverage to `37ea7ad`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `37ea7ad` (PR119 BODY RESTRUCTURE R222 report). Content commit: `25f18d0`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R223 does

R222 left the disclosed gap: the delivery index covered 633 commits to
`a38b714`; R222's own 2 commits were to fold in at R223. The R222 body v2
was POSTED LIVE 2026-11-24 ~16:16 JST (owner tapped widget `widget-d6b92d01`
~16:12 JST, approved the card at once, connector returned ok; read back
byte-exact: body 103.023 ký tự, sha `1dd61afd`, title 765 ký tự kết thúc
"+ R222", head `37ea7ad` · 635 · 3061, mergeable true/clean, 0 U+FFFD,
updated_at 2026-11-24T07:16:22Z) — replacing R140, which had stood live
since 2026-11-20. The live PR body is now R222 (this round's fresh
connector read ~16:40 JST, `pull_request_read`: title ends "+ R222",
head `37ea7ad`, 635 commits / 3061 files / +298940, mergeable null —
GitHub computing at read time — / mergeable_state clean, live body
103.023 ký tự, sha `1dd61afd`, 0 U+FFFD, updated_at 2026-11-24T07:16:22Z —
unchanged since the 16:16 JST post read, body bytes unchanged). R221 was
NEVER posted: its first widget (`widget-56770776`, tapped ~15:12 JST)
died on the approval card expiring ~15:49 JST (10th expiry, connector
confirmed not performed), and its second widget (`widget-7a108c57`,
presented ~15:50 JST after the third payload refresh) was never tapped
before R222 superseded it. No new Codex/owner direction has been verified
on issue #116: the comments read SUCCEEDED this round (connector
`issue_read` ~16:40 JST: still 34 comments, updated_at
2026-11-13T19:24:49Z, latest ACK `6862732081` (CP5 + M-G CP10 + R2);
no new direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API PR read succeeded via the
connector (`pull_request_read`, ~16:40 JST, read-only — the `gh` CLI is
unauthenticated in this shell, so no direct curl read was available;
the connector is the sanctioned read path and returned the full PR
object). The issue read also succeeded via the connector (`issue_read`
method `get`: comments 34, updated_at 2026-11-13T19:24:49Z). Both read
paths clean. PR head `37ea7ad`, 635 commits / 3061 files / +298940 at the
current head `37ea7ad` (the `deletions` key is absent in the connector
response — git shows 0 deletions); mergeable_state clean at `37ea7ad`
(mergeable null in this read — GitHub computing — the honest wording is
state clean, not a repeated true/clean claim).

Fresh derivation at `37ea7ad` (~16:40 JST): `git rev-list --count
cf17178..37ea7ad` = 635 commits, `git diff --name-only` = 3061 files,
`--shortstat` = 298940 insertions, 0 deletions — agreeing exactly with
the connector PR read. `git merge-tree --write-tree` `37ea7ad` vs
integration `f3db6b3` exit 0, 0 conflicts, tree `8cf6d9b7…`. No re-fetch
was needed before applying: the run fetched at ~16:40 JST (the run start)
and the remote head was still `37ea7ad`, integration still `f3db6b3` — no
intervening push; the connector read ~16:40 JST independently confirmed
head `37ea7ad`.

R223 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `37ea7ad` (635 commits / 3061 files /
  298940 additions; the fresh git derivation at `37ea7ad`, the fresh
  connector PR read ~16:40 JST, and the merge-tree cross-check at
  `37ea7ad` are cited, with the honest live-read disclosure above —
  connector PR read clean, issue read SUCCEEDED this round (34 comments,
  latest ACK `6862732081`, no new direction); live body R222 (posted
  ~16:16 JST, read back byte-exact this round); delta `a38b714..37ea7ad`:
  5 paths, 878 insertions, 12 deletions); one row appended — PR119 BODY
  RESTRUCTURE R222 (`110aa76`/`37ea7ad`), recording that its payload was
  prepared after push ~15:58 JST (103.023 ký tự, sha `1dd61afd`; JSON
  118.329 byte < trần 131.072 — còn 12.743 byte, bản giữ tại
  `.bak-prepost-20261124` — sha256 `4b409872…`) and then POSTED LIVE
  ~16:16 JST (owner tapped widget `widget-d6b92d01` ~16:12 JST, approved
  at once; read-back byte-exact, updated_at 2026-11-24T07:16:22Z),
  replacing R140; no separate ACK for R222. ĐÍNH CHÍNH R223 on the R221
  row: the R221 payload has a THIRD version — refreshed ~15:50 JST by
  luồng chính (body 103.072 ký tự, sha `04eee785`, JSON 118.430 byte,
  mergeable unstable → clean; second widget `widget-7a108c57` presented
  ~15:50 JST, never tapped, superseded by R222; first widget
  `widget-56770776` tapped ~15:12 JST, card expired ~15:49 JST, 10th
  expiry, connector confirmed not performed) — R221 was NEVER POSTED;
  live body is now R222. The index now covers every block through
  `37ea7ad`; R223's own 2 commits fold in at the next index update
  (R224), disclosed in the index itself. The R223 note was appended after
  the R222 note line (not replacing it — the R140 replace-instead-of-append
  defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `37ea7ad` · 635 · 3061 (with the fresh git derivation at `37ea7ad`,
  the fresh connector PR read ~16:40 JST, and the fresh merge-tree
  cross-check at `37ea7ad`), plus the R222 paragraph in "Khối mới nhất"
  (254 ký tự, marked ĐÃ ĐĂNG LIVE ~16:16 JST — live body is now R222)
  and the R223 note. The stale index reference in "Về bản mô tả này"
  (head `a38b714`) is also fixed to `37ea7ad`, and the title line is
  extended to R222 (APPENDED, not replaced — see the R176 robustness
  note). Compaction (R222 warning — applied with a measured correction,
  DOUBLE): the R75 + R74 paragraphs (438 and 489 ký tự — measured this
  round) are collapsed to one 207-ký-tự compact line each (full detail
  stays in the delivery index; the R76–R80 template measures 208, the
  R75/R74 lines measure 207 — the checker asserts < 400, not an exact
  208) — the new R222 paragraph was 254 ký tự, so the body is 102.822
  ký tự — net −197 vs R222 despite the new R222 paragraph, headroom
  2.178 ký tự. The dry-run first projected 102.822 ký tự and the apply
  wrote exactly that on the first attempt — measure, then trim, then
  apply. The head line SHRANK 1.028 → 1.017 ký tự (−11, the live-body
  state is now the posted R222, shorter to state than the R140-era
  disclosure).
  Paragraph order: the R222 paragraph sits directly after R221
  (ascending full-paragraph order R166..R222), before the compact block
  — the new checker now asserts this ascending order explicitly. The
  live PR description is refreshed from this file in the posting round
  that follows R223 (owner tap) — the R222 body v2 now live is the base;
  only the R223 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r223_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R222 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R222 and R223 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R222 (92 compact lines R74–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 102.822 ký tự),
  a check that the R222 paragraph sits directly after R221
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R222 note clean).
  New this round: the R221-row regression guard (cumulative must be 3059,
  re-derived from git at `110aa76`), the R222-row guard (cumulative must
  cite 3062 — 3061 at `37ea7ad` + 1 new checker in the R223 content commit,
  verified in this report after the content commit), the R221-row
  ĐÍNH CHÍNH R223 guard (row must carry "ĐÍNH CHÍNH R223" and sha
  `04eee785`), and the body "Ghi chú" line correction guard
  (R158/R223, range R74–R165, list complete through R222, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 63/63**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R223_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R222) with the full COVER
  SHA verified intact (definition + docstring, both
  `37ea7ad5aba4cafc94701232c857bcf5b0d8c6e8` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `a38b714` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R221-row guard string citing "3058 at a38b714", legitimate; plus 3
  `c38a4dc` (docstring + R220-row guard citing "3055 at c38a4dc"), 3 `8f8b504` (docstring + R219-row guard citing "3052 at 8f8b504"), 3 `a74e9f4` (docstring + R218-row guard citing "3049 at a74e9f4"), 3 `0a4d05a` (docstring + R217-row guard citing "3046 at 0a4d05a"), 3 `0de54fb` (docstring + R216-row guard citing "3043 at 0de54fb"), 3 `1e564a2` (docstring + R215-row guard citing "3040 at 1e564a2"), 3 `3de99c9` (docstring + R214-row guard citing "3037 at 3de99c9"), legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 102.822 ký tự and the apply wrote on
  the first attempt at 102.822 ký tự with 2.178 ký tự of headroom; the idempotency re-run
  after apply reports already-applied changed: 0 — verified (after a
  script fix, see the lesson below).
  Correction caught before the report commit: the R222 row's cumulative figure was drafted as 3062 (3061 at
  `37ea7ad` + 1 new checker) and the true diff at the R223 content
  commit is 3062 — verified by `git diff --name-only cf17178..25f18d0` = 3062
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH on R222's committed content this round: R222's committed content verified correct —
  the committed index at `37ea7ad` carries the R220 row at cumulative 3056
  (re-derived by the new checker from git at `a19018c`) and the R221 row at 3059
  (re-derived from git at `110aa76`); no uncommitted
  working-tree fix was left behind by R222 (the working tree was clean at this
  run's start and the fetch found no intervening push). The R221-row
  ĐÍNH CHÍNH is a NEW fact (the third payload version, refreshed after
  the R222 report commit), not a correction of R222's content.

## R223 robustness note — headroom now 2.178 chars

The R222 warning left 1.981 ký tự of headroom, so this round compacted
TWO paragraphs (R75 + R74, 438 + 489 ký tự → 207 each) before adding the new R222 paragraph
(254 ký tự). The body is now 102.822 ký tự — net −197 vs R222 — with
2.178 ký tự of headroom. The double compaction bought back 513 ký tự against the
254-ký-tự new paragraph, and the head line shrank −11 ký tự (live body now the posted R222),
so the net recovery is −197. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R224 warning: headroom is 2.178 ký tự; compact R73 + R72 next (or the head line
grows again if a future round's reads hit the rate-limit — the honest disclosure
is the variable cost, not the compaction).
At the current net −197/round the margin is recovering well,
but only while the double compaction continues (full paragraphs remaining R166..R222 = 57;
compact block R74–R165 = 92 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (102.822 projected; apply wrote 102.822 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222 — the R222 row's 3062 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — the first re-run CRASHED because `replace_line` only recognised "already applied" when the OLD prefix still existed; after a successful apply the old prefix is gone (0 hits) and the assert failed. Fixed by checking whether the NEW line is already present before looking for the old prefix; the re-run then reports already-applied changed: 0, verified (R203/R207 lesson, now applied to all edits — the same class of defect as R207's, caught by the re-run itself, not by a failed commit). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two backup locations can hold
different versions of the same payload — the R221 payload was refreshed a third time ~15:50 JST after its report commit,
so the `.bak-prepost-20261124/` directory copy (as-prepared, sha 85d22094), the main file + suffixed copy as refreshed ~15:12 JST (sha ae8d1c56), and the third refresh ~15:50 JST (sha 04eee785) are three distinct versions; record each version with its sha in the index row instead of
claiming one backup is "the" payload (R221's report recorded the as-prepared version correctly for its time;
the second refresh was recorded by R222; the third is recorded here). (6) A payload backup the authoring
round made must be verified, not re-claimed — R222's payload `.bak` copy
existed when R223 started; R223 verified its body sha (`1dd61afd`) against the live body read this round (byte-exact match) and the R222 row records
it as posted live, not R223's.
(7) No execution-risk flag appeared on any git/script command this round
(unlike R211/R213 and the R219-blocked run ~11:40 JST); the flag itself has now appeared 4 times
(R211 ~01:40, R213 ~04:40, R213 ~05:44, R219 ~11:40) and the decision whether to keep running git/checker after it still awaits
luồng chính/chủ dự án — recorded here, not decided here.
(8) When the `gh` CLI is unauthenticated in a shell, the GitHub connector
(`pull_request_read` / `issue_read`) is the sanctioned read path — it
returned the full PR object and the issue comment count this round; do
not fall back to unauthenticated curl (403) and do not treat a failed
`gh` call as a failed read.

## Verification

- Merge-tree `37ea7ad` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `8cf6d9b7…`. Merge-tree at the R223
  content head `25f18d0` vs `f3db6b3`: exit 0,
  tree `f4c3f5d5…`.
- Live PR state: connector read this round (~16:40 JST) — direct read
  clean byte-exact (103.023 ký tự, sha `1dd61afd`, 0 U+FFFD, mergeable_state clean, mergeable null — GitHub computing) — PR title ends
  "+ R222" (R222 posted live ~16:16 JST 2026-11-24); head `37ea7ad`; live body
  R222 by structure (description head `37ea7ad` · 635 · 3061, tail lines match)
  and byte-exact body read (103.023 ký tự, sha `1dd61afd`,
  0 U+FFFD, updated_at 2026-11-24T07:16:22Z — unchanged since the 16:16 JST post read, body
  bytes unchanged); commits 635, changed_files 3061, additions 298940
  (connector agrees with the fresh git derivation; the `deletions` key is absent in
  the connector response — git shows 0 deletions); mergeable_state clean at
  `37ea7ad` (connector read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: comments read SUCCEEDED this round — connector `issue_read` ~16:40 JST: still 34
  comments, updated_at 2026-11-13T19:24:49Z, latest ACK `6862732081` (CP5 + M-G CP10 + R2); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R223 block (`37ea7ad..25f18d0`) 3 paths / 0 violations
  (index + body v2 + R223 checker); cumulative at the R223 content
  commit `25f18d0` 3062 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `25f18d0`). Merge-tree at the R223 content head `25f18d0` vs `f3db6b3`: exit 0,
  tree `f4c3f5d5…`.
- Transient notes: this round's `git fetch` at ~16:40 JST succeeded
  first try. The connector read path was used this round — both reads
  succeeded (PR + issue). No call-tool write approval was requested for a read. No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST). No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH; the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
- Ceiling discipline: the R222 payload JSON as-prepared measured 118.329 byte
  (POSTED LIVE ~16:16 JST — live body is R222, verified by this round's connector read),
  vs the 131.072-byte transport ceiling
  (12.743 byte headroom). The projected R223 payload JSON is ~121,000 byte
  (measured exactly at payload build, after push). Body v2 is now 102.822
  ký tự (< 105.000) — 2.178 ký tự of headroom. R223 warning:
  headroom is now 2.178 ký tự; the double compaction must continue next round
  (R73 + R72) or the head line must be trimmed if a future round's reads hit the rate-limit again.

## Next

Posting round (owner tap): PR #119 description refresh to the R223 body
v2 (R222 posting note + new head line are the only new parts vs the live R222 body). Payload `pr119_update_body_v2_r223.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R223 push (title
ending "+ R223", built by replacing the "+ R222" suffix — not appending;
body = body v2 R223 in repo, head line refreshed to head after R223 push).
This run started ~16:40 JST — INSIDE working hours (09:00–21:30 JST), so the
R223 payload is READY FOR WORKING HOURS (unlike R142/R164–R197/R207–R216,
which were held because they started before 09:00). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R222 payload as new — R222 is LIVE; do not present either R221 widget (`widget-56770776`, `widget-7a108c57`) — R221 was never posted and both are stale. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220 and R221 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R223: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
