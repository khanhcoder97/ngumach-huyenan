# MEDIA-02 — PR #119 Body Restructure R217: delivery index + body v2 coverage to `0de54fb`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `0de54fb` (PR119 BODY RESTRUCTURE R216 report). Content commit: `af6e949`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R217 does

R216 left the disclosed gap: the delivery index covered 621 commits to
`1e564a2`; R216's own 2 commits were to fold in at R217. The R216 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API read ~09:40 JST, MCP + direct curl agreeing:
PR title still ends "+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T23:47:25Z — bumped by the R216 push updating the PR head, body bytes
unchanged). The R216 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~09:40 JST, read-only —
`issue_read get_comments` page 1 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read of the issue comments and of the PR with curl as cross-check): the MCP read
returned the clean body on the FIRST read (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD — no mangle
this round, as in R216) and the direct read AGREED on every field (92.520 ký tự, sha
`ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — a real cross-check this round,
as in R216. The issue-comments direct read also
succeeded (34 comments, latest `6862732081`) and agrees with the MCP read
(MCP returns page 1 only, 30 comments — the remaining 4 are paginated, as
in earlier rounds). PR head `0de54fb`,
623 commits / 3043 files / +293.999, mergeable_state clean at `0de54fb` (mergeable null via MCP,
true via direct read).

Fresh derivation at `0de54fb` (~09:40 JST): `git rev-list --count
cf17178..0de54fb` = 623 commits, `git diff --name-only` = 3043 files,
`--shortstat` = 293999 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `0de54fb` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `c64c01fa…`. No re-fetch was needed before applying: the run fetched at ~09:40 JST
(the run start) and the remote head was still `0de54fb`, integration still `f3db6b3` — no
intervening push; the API read ~09:40 JST independently confirmed head `0de54fb`.

R217 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `0de54fb` (623 commits / 3043 files /
  293999 additions; the fresh git derivation at `0de54fb`, the fresh API
  read ~09:40 JST, and the merge-tree cross-check at `0de54fb` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `1e564a2..0de54fb`: 5 paths, 779 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R216
  (`dd19bba`/`0de54fb`), recording that its payload was prepared after
  push ~08:50 JST (104.755 ký tự, sha `1ab34453`; JSON 120.767 byte < trần 131.072 — còn 10.305 byte, bản giữ tại
  `.bak-prepost-20261124` — R216 made its own backup, sha256 `ac5b0cf9…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's MCP + direct reads, both clean:
  description structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc byte-exact lượt này qua MCP lần 1
  và đọc trực tiếp cross-check khớp, 0 U+FFFD, updated_at 2026-11-23T23:47:25Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~09:40 JST).
  The index now covers every block through `0de54fb`; R217's
  own 2 commits fold in at the next index update (R218), disclosed in the
  index itself. The R217 note was appended after the R216 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `0de54fb` · 623 · 3043 (with the fresh git derivation at `0de54fb`,
  the fresh API read ~09:40 JST, and the fresh merge-tree cross-check at
  `0de54fb`), plus the R216 paragraph in "Khối mới nhất" (254 ký tự,
  marked chưa đăng — live body is R140) and the R217 note. The stale index
  reference in "Về bản mô tả này" (head `1e564a2`) is also fixed to
  `0de54fb`, and the title line is extended to R216 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R216 warning —
  applied with a measured correction, DOUBLE): the R87 + R86 paragraphs (494 ký tự each — measured this
  round) are
  collapsed to one 208-ký-tự compact line each (full detail stays in the
  delivery index) — the new R216 paragraph was 254 ký tự, so
  the body is 104.549 ký tự — net −245 vs R216 despite the new R216 paragraph, headroom 451 ký tự. The dry-run first projected 104.549 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  Paragraph order: the R216 paragraph sits directly after R215
  (ascending full-paragraph order R166..R216), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R217 (owner tap) — the R140 body v2 now live
  is the base; only the R216 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r217_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R216 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R216 and R217 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R216 (80 compact lines R86–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.549 ký tự),
  a check that the R216 paragraph sits directly after R215
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R216 note clean).
  New this round: the R215-row regression guard (cumulative must be 3041,
  re-derived from git at `dd19bba`), the R216-row guard (cumulative must
  cite 3044 — 3043 at `0de54fb` + 1 new checker in the R217 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R216, range R86–R165, list complete through R216, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 50/50**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R217_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R216) with the full COVER
  SHA verified intact (definition + docstring, both
  `0de54fb4cdd6cbc2b18e8f5debdd7cea80d10d8c` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `1e564a2` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R215-row guard string citing "3040 at 1e564a2", legitimate; plus 1
  `3de99c9` in the R214-row guard, legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.549 ký tự and the apply wrote on
  the first attempt at 104.549 ký tự with 451 ký tự of headroom; the idempotency re-run
  after apply reported already-applied changed: 0 — verified, after the
  R203/R207 lesson (check NEW state first) was applied in the script from
  the start this round. The edit script itself hit one defect before
  apply and was fixed before any write: three lambdas evaluated their
  replacement expression eagerly at tuple-construction time
  (`UnboundLocalError` on `l`), fixed by making the replacement a
  callable passed to `apply_lines`.
  Correction caught before the report commit: the R216 row's cumulative figure was drafted as 3044 (3043 at
  `0de54fb` + 1 new checker) and the true diff at the R217 content
  commit is 3044 — verified by `git diff --name-only cf17178..af6e949` = 3044
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH this round: R216's committed content verified correct —
  the committed index at `0de54fb` carries the R214 row at cumulative 3038
  (re-derived by the new checker from git at `6127a16`) and the R215 row at 3041
  (re-derived from git at `dd19bba`); no uncommitted
  working-tree fix was left behind by R216 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R217 robustness note — headroom now 451 chars

The R216 warning left 206 ký tự of headroom, so this round compacted
TWO paragraphs (R87 + R86, 494 ký tự → 208 each) before adding the new R216 paragraph
(254 ký tự). The body is now 104.549 ký tự — net −245 vs R216 — with
451 ký tự of headroom. The double compaction bought back 572 ký tự against the
254-ký-tự new paragraph, so the margin now holds while two paragraphs are
compacted per round; the head line is the variable cost (its honest
live-read disclosure grew ~+110 ký tự in R215/R216 as the cross-check wording
was added). The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R218 warning: headroom is 451 ký tự; compact R85 + R84 next (or trim the
head line hard). At the current net −245/round the margin is recovering,
but only while the double compaction continues (full paragraphs remaining R166..R216 = 51;
compact block R86–R165 = 80 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (104.549 projected; apply wrote 104.549 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216 — the R216 row's 3044 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first, not only
assert the OLD state — otherwise the re-run crashes on its own
pre-condition after a successful apply (R203/R207 lesson — applied from
the start this round; re-run reports already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two agreeing read paths settle
the live body faster than one mangled read did in R209 — the MCP path returned
the clean body on the first read this round (92.520, sha `ddbe32ff`) and the
direct curl read AGREED on every field including mergeable true — a real
cross-check, as in R216; when two
read paths agree first try, record both, not one. (6) A payload backup the authoring
round made must be verified, not re-claimed — R216's payload `.bak` copy
existed when R217 started; R217 verified sha256 identical
(`ac5b0cf9…` both) and the R216 row records the copy as R216's, not R217's.

## Verification

- Merge-tree `0de54fb` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `c64c01fa…`. Merge-tree at the R217
  content head `af6e949` vs `f3db6b3`: exit 0,
  tree `5f96c683…`.
- Live PR state: API read twice this round (~09:40 JST) — MCP read
  clean on the first read (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) and direct curl read
  agreeing (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `0de54fb`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T23:47:25Z — bumped by the R216 push updating the PR head, body
  bytes unchanged); commits 623, changed_files 3043, additions 293999
  (API agrees with the fresh git derivation; the `deletions` key is absent in
  the direct API response — git shows 0 deletions; the MCP response returns
  `mergeable: null` while the direct read returns `mergeable: true`; mergeable_state clean is the operative field); mergeable_state clean at
  `0de54fb` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API + direct curl of comments — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R217 block (`0de54fb..af6e949`) 3 paths / 0 violations
  (index + body v2 + R217 checker); cumulative at the R217 content
  commit `af6e949` 3044 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `af6e949`).
  Merge-tree at the R217 content head `af6e949` vs `f3db6b3`: exit 0,
  tree `5f96c683…`.
- Transient notes: this round's `git fetch` at ~09:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (first PR read clean — see live-read note; `pull_request_read` takes `pullNumber`, not
  `pull_number` — parameter-name lesson carried from R211; `issue_read`
  takes `issue_number`, not `issueNumber`). No execution-risk flag on any
  git/script command this round (unlike R211/R213). The R216 payload's own head line recorded
  mergeable clean at `1e564a2` at its preparation and clean at
  `0de54fb`; this round's API read confirms clean at `0de54fb`. One benign
  warning: the `post-commit` git-lfs hook printed "git-lfs was not found on
  your path" at the content commit (this shell lacked `~/workspace/tools-bin`
  on PATH); the commit itself succeeded and the files are text-only, so no
  LFS smudge was involved — the push below uses the documented env.
- Ceiling discipline: the R216 payload JSON measured 120.767 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (10.305 byte headroom). The projected R217 payload JSON is ~121,000 byte
  (measured exactly at payload build, after push). Body v2 is now 104.549
  ký tự (< 105.000) — 451 ký tự of headroom. R217 warning:
  headroom is now 451 ký tự; the double compaction must continue next round
  (R85 + R84) or the head line must be trimmed.

## Next

Posting round (owner tap): PR #119 description refresh to the R217 body
v2 (R216 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r217.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R217 push (title
ending "+ R217", built by replacing the "+ R140" suffix — not appending;
body = body v2 R217 in repo, head line refreshed to head after R217 push).
This run started ~09:40 JST — INSIDE working hours (09:00–21:30 JST), so the
R217 payload is READY FOR WORKING HOURS (unlike R142/R164–R197/R207–R216,
which were held because they started before 09:00). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R216 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215 and R216 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R217: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
