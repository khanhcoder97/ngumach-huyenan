# MEDIA-02 — PR #119 Body Restructure R222: delivery index + body v2 coverage to `a38b714`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `a38b714` (PR119 BODY RESTRUCTURE R221 report). Content commit: `110aa76`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R222 does

R221 left the disclosed gap: the delivery index covered 631 commits to
`c38a4dc`; R221's own 2 commits were to fold in at R222. The R221 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh direct-API read ~15:40 JST, curl: PR title still ends "+ R140",
head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD on the direct read, updated_at 2026-11-24T06:05:02Z — unchanged since the R221 post-push read, body bytes
unchanged; mergeable true / mergeable_state clean at `a38b714`). The R221 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has been verified on issue #116:
the comments read SUCCEEDED this round (direct curl ~15:40 JST, HTTP 200: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`) — the R221 rate-limit (403 ×3) has cleared.
A 403 is not evidence of a new comment — R221 recorded the last verified
state honestly, and this round's successful read confirms nothing changed.

Live-read method, this round: the GitHub API PR read succeeded via direct curl (~15:40 JST, read-only —
`pulls/119`): title ends "+ R140", head `a38b714`, 633 commits / 3058 files / +298074 / 0 deletions,
mergeable true, mergeable_state clean at `a38b714`, live body 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD,
updated_at 2026-11-24T06:05:02Z. The issue-comments direct read also succeeded this round
(HTTP 200, 34 comments) — both read paths clean, unlike R221 (MCP refused,
comments 403). PR head `a38b714`,
633 commits / 3058 files / +298074 at the previous head `c38a4dc` 631 / 3055 / +297227,
mergeable_state clean at `a38b714` (mergeable true via direct read; CI has finished on the new head,
unlike the unstable read at ~15:05 JST).

Fresh derivation at `a38b714` (~15:40 JST): `git rev-list --count
cf17178..a38b714` = 633 commits, `git diff --name-only` = 3058 files,
`--shortstat` = 298074 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `a38b714` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `5de20e11…`. No re-fetch was needed before applying: the run fetched at ~15:40 JST
(the run start) and the remote head was still `a38b714`, integration still `f3db6b3` — no
intervening push; the API read ~15:40 JST independently confirmed head `a38b714`.

R222 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `a38b714` (633 commits / 3058 files /
  298074 additions; the fresh git derivation at `a38b714`, the fresh API
  PR read ~15:40 JST, and the merge-tree cross-check at `a38b714` are cited,
  with the honest live-read disclosure above — direct PR read clean, issue-comments read
  SUCCEEDED this round (34 comments, latest ACK `6862732081`, no new direction);
  live body R140; delta `c38a4dc..a38b714`: 5 paths, 859 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R221
  (`a19018c`/`a38b714`), recording that its payload was prepared after
  push ~15:05 JST (103.233 ký tự, sha `85d22094`; JSON 118.623 byte < trần 131.072 — còn 12.449 byte, bản giữ tại
  `.bak-prepost-20261124` — R221 made its own backup, sha256 `cdfcbc37…` cả hai lúc chuẩn bị),
  then REFRESHED ~15:12 JST (after the R221 report commit) to 103.124 ký tự, sha `ae8d1c56`
  (JSON 118.495 byte; file chính + bản giữ có hậu tố `.bak-prepost-20261124` byte-identical, sha256 `11455063…`;
  bản trong thư mục `.bak-prepost-20261124/` vẫn giữ bản chuẩn bị đầu — the two backup locations now hold
  DIFFERENT versions of the R221 payload, recorded here, not smoothed over; the only differing line is the
  head line, 1.107 → 998 ký tự, refreshed with the ~15:12 JST read),
  that it was NOT posted
  — live body still R140 (verified by this round's direct PR read: description structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc trực tiếp byte-exact khớp, 0 U+FFFD, updated_at 2026-11-24T06:05:02Z) — superseded, not
  posted; issue line re-read this round SUCCEEDED (34 comments, latest ACK `6862732081`, no new direction;
  the R221 rate-limit has cleared).
  The index now covers every block through `a38b714`; R222's
  own 2 commits fold in at the next index update (R223), disclosed in the
  index itself. The R222 note was appended after the R221 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `a38b714` · 633 · 3058 (with the fresh git derivation at `a38b714`,
  the fresh API PR read ~15:40 JST, and the fresh merge-tree cross-check at
  `a38b714`), plus the R221 paragraph in "Khối mới nhất" (254 ký tự,
  marked chưa đăng — live body is R140) and the R222 note. The stale index
  reference in "Về bản mô tả này" (head `c38a4dc`) is also fixed to
  `a38b714`, and the title line is extended to R221 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R221 warning —
  applied with a measured correction, DOUBLE): the R77 + R76 paragraphs (439 and 439 ký tự — measured this
  round) are
  collapsed to one 208-ký-tự compact line each (full detail stays in the
  delivery index) — the new R221 paragraph was 254 ký tự, so
  the body is 103.019 ký tự — net −355 vs R221 despite the new R221 paragraph, headroom 1.981 ký tự. The dry-run first projected 103.019 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  The head line SHRANK 1.248 → 1.028 ký tự (−220, the rate-limit disclosure dropped because the comments read
  succeeded this round) — it is no longer the main variable cost; keep it short by disclosing only what this
  round's reads actually needed.
  Paragraph order: the R221 paragraph sits directly after R220
  (ascending full-paragraph order R166..R221), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R222 (owner tap) — the R140 body v2 now live
  is the base; only the R221 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r222_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R221 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R221 and R222 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R221 (90 compact lines R76–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 103.019 ký tự),
  a check that the R221 paragraph sits directly after R220
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R221 note clean).
  New this round: the R220-row regression guard (cumulative must be 3056,
  re-derived from git at `a19018c`), the R221-row guard (cumulative must
  cite 3059 — 3058 at `a38b714` + 1 new checker in the R222 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R222, range R76–R165, list complete through R221, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 60/60**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R222_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R221) with the full COVER
  SHA verified intact (definition + docstring, both
  `a38b7147fbdfd4e52144495b1018ccbdfd4d7545` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `c38a4dc` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R219-row guard string citing "3052 at c38a4dc", legitimate; plus 3
  `8f8b504` (docstring + R218-row guard citing "3049 at 8f8b504"), 3 `a74e9f4` (docstring + R217-row guard citing "3046 at a74e9f4"), 3 `0a4d05a` (docstring + R216-row guard citing "3043 at 0a4d05a"), 3 `0de54fb` (docstring + R215-row guard citing "3040 at 0de54fb"), 3 `1e564a2` (docstring + R214-row guard citing "3037 at 1e564a2"), 3 `3de99c9` (docstring + R213-row guard citing "3034 at 3de99c9"), legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 103.019 ký tự and the apply wrote on
  the first attempt at 103.019 ký tự with 1.981 ký tự of headroom; the idempotency re-run
  after apply reports already-applied changed: 0 — verified. No content was changed by the re-run;
  the first apply had already written the correct bytes.
  Correction caught before the report commit: the R221 row's cumulative figure was drafted as 3059 (3058 at
  `a38b714` + 1 new checker) and the true diff at the R222 content
  commit is 3059 — verified by `git diff --name-only cf17178..110aa76` = 3059
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH this round: R221's committed content verified correct —
  the committed index at `a38b714` carries the R219 row at cumulative 3053
  (re-derived by the new checker from git at `f0051bd`) and the R220 row at 3056
  (re-derived from git at `a19018c`); no uncommitted
  working-tree fix was left behind by R221 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R222 robustness note — headroom now 1.981 chars

The R221 warning left 1.626 ký tự of headroom, so this round compacted
TWO paragraphs (R77 + R76, 439 + 439 ký tự → 208 each) before adding the new R221 paragraph
(254 ký tự). The body is now 103.019 ký tự — net −355 vs R221 — with
1.981 ký tự of headroom. The double compaction bought back 462 ký tự against the
254-ký-tự new paragraph, and the head line shrank −220 ký tự (rate-limit clause gone),
so the net recovery is −355. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R223 warning: headroom is 1.981 ký tự; compact R75 + R74 next (or the head line
grows again if a future round's reads hit the rate-limit — the honest disclosure
is the variable cost, not the compaction).
At the current net −355/round the margin is recovering well,
but only while the double compaction continues (full paragraphs remaining R166..R221 = 56;
compact block R76–R165 = 90 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (103.019 projected; apply wrote 103.019 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221 — the R221 row's 3059 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — the replace_line prefix crashed because its lookup prefix itself carried the OLD value,
and the Ghi-chú label edit crashed the same way (R203/R207 lesson, now applied to all edits; re-run reports
already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two backup locations can hold
different versions of the same payload — the R221 payload was refreshed ~15:12 JST after its report commit,
so the `.bak-prepost-20261124/` directory copy (as-prepared, sha 85d22094) and the main file + suffixed copy
(refreshed, sha ae8d1c56) now disagree; record both versions with their shas in the index row instead of
claiming one backup is "the" payload (R221's report recorded the as-prepared version correctly for its time;
the refresh is a post-report fact, disclosed here). (6) A payload backup the authoring
round made must be verified, not re-claimed — R221's payload `.bak` copies
existed when R222 started; R222 verified each copy's sha256 separately
(`cdfcbc37…` as-prepared in the directory, `11455063…` refreshed main + suffixed copy) and the R221 row records
each as its own version, not R222's.
(7) No execution-risk flag appeared on any git/script command this round
(unlike R211/R213 and the R219-blocked run ~11:40 JST); the flag itself has now appeared 4 times
(R211 ~01:40, R213 ~04:40, R213 ~05:44, R219 ~11:40) and the decision whether to keep running git/checker after it still awaits
luồng chính/chủ dự án — recorded here, not decided here.

## Verification

- Merge-tree `a38b714` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `5de20e11…`. Merge-tree at the R222
  content head `110aa76` vs `f3db6b3`: exit 0,
  tree `73ec889b…`.
- Live PR state: API read this round (~15:40 JST) — direct curl read
  clean byte-exact (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `a38b714`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-24T06:05:02Z — unchanged since the R221 post-push read, body
  bytes unchanged); commits 633, changed_files 3058, additions 298074
  (API agrees with the fresh git derivation; the `deletions` key is 0 in
  the direct API response — git shows 0 deletions); mergeable_state clean at
  `a38b714` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: comments read SUCCEEDED this round — direct curl 200 at ~15:40 JST: still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction. The R221 rate-limit (403 ×3) has cleared.
- Scope audit: R222 block (`a38b714..110aa76`) 3 paths / 0 violations
  (index + body v2 + R222 checker); cumulative at the R222 content
  commit `110aa76` 3059 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `110aa76`). Merge-tree at the R222 content head `110aa76` vs `f3db6b3`: exit 0,
  tree `73ec889b…`.
- Transient notes: this round's `git fetch` at ~15:40 JST succeeded
  first try. No MCP read path was needed this round — both direct curl reads
  succeeded (PR 200, comments 200). No call-tool write approval was requested for a read. No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST). The R221 payload's own head line recorded
  mergeable unstable at `a38b714` at its preparation (~15:05 JST, CI running); this round's API read confirms clean at `a38b714` (CI finished). No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH; the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
- Ceiling discipline: the R221 payload JSON as-prepared measured 118.623 byte
  (NOT posted — live body still R140, verified by this round's API read),
  refreshed after the report to 118.495 byte — both vs the 131.072-byte transport ceiling
  (12.449 / 12.577 byte headroom). The projected R222 payload JSON is ~121,000 byte
  (measured exactly at payload build, after push). Body v2 is now 103.019
  ký tự (< 105.000) — 1.981 ký tự of headroom. R222 warning:
  headroom is now 1.981 ký tự; the double compaction must continue next round
  (R75 + R74) or the head line must be trimmed if a future round's reads hit the rate-limit again.

## Next

Posting round (owner tap): PR #119 description refresh to the R222 body
v2 (R221 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r222.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R222 push (title
ending "+ R222", built by replacing the "+ R140" suffix — not appending;
body = body v2 R222 in repo, head line refreshed to head after R222 push).
This run started ~15:40 JST — INSIDE working hours (09:00–21:30 JST), so the
R222 payload is READY FOR WORKING HOURS (unlike R142/R164–R197/R207–R216,
which were held because they started before 09:00). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R221 payload. The R140 payload is DONE (posted) — do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148, R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217, R218, R219, R220 and R221 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R222: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
