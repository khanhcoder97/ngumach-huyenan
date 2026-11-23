# MEDIA-02 — PR #119 Body Restructure R215: delivery index + body v2 coverage to `3de99c9`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `3de99c9` (PR119 BODY RESTRUCTURE R214 report). Content commit: `6127a16`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R215 does

R214 left the disclosed gap: the delivery index covered 617 commits to
`1afb41e`; R214's own 2 commits were to fold in at R215. The R214 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh MCP read ~07:40 JST, second read clean: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T21:46:41Z — bumped by the R214 push updating the PR head, body bytes
unchanged). The R214 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~07:40 JST, read-only —
`issue_read get_comments` page 1 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read of the issue comments with curl as cross-check): the first MCP read
of the PR mangled 1 character ("Ă" → 2 U+FFFD, body 92.521 ký tự, sha `ced29e00` — the same
transport artifact as R209) and the retry returned the clean body (92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD); the direct public-API read of the PR was rate-limited this round (unauthenticated
shared IP), so there is no direct cross-check of the PR body this round — disclosed, not
claimed. The issue-comments direct read succeeded (34 comments, latest `6862732081`) and agrees
with the MCP read. PR head `3de99c9`, 619 commits / 3037 files / +292.490,
mergeable_state clean at `3de99c9` (mergeable null via MCP).

Fresh derivation at `3de99c9` (~07:40 JST): `git rev-list --count
cf17178..3de99c9` = 619 commits, `git diff --name-only` = 3037 files,
`--shortstat` = 292490 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `3de99c9` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `b3ec0776…`. No re-fetch was needed before applying: the run fetched at ~07:40 JST
(the run start) and the remote head was still `3de99c9`, integration still `f3db6b3` — no
intervening push; the API read ~07:40 JST independently confirmed head `3de99c9`.

R215 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `3de99c9` (619 commits / 3037 files /
  292490 additions; the fresh git derivation at `3de99c9`, the fresh API
  read ~07:40 JST, and the merge-tree cross-check at `3de99c9` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `1afb41e..3de99c9`: 5 paths, 728 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R214
  (`2ce013b`/`3de99c9`), recording that its payload was prepared after
  push ~06:47 JST (104.760 ký tự, sha `12d3a200`; JSON 120.889 byte < trần 131.072 — còn 10.183 byte, bản giữ tại
  `.bak-prepost-20261124` — R215 sao lưu, sha256 `46d74935…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's MCP read, second read clean:
  description structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này qua MCP lần 2, 0 U+FFFD, updated_at 2026-11-23T21:46:41Z; đọc trực tiếp bị rate-limit lượt này) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~07:40 JST).
  The index now covers every block through `3de99c9`; R215's
  own 2 commits fold in at the next index update (R216), disclosed in the
  index itself. The R215 note was appended after the R214 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `3de99c9` · 619 · 3037 (with the fresh git derivation at `3de99c9`,
  the fresh API read ~07:40 JST, and the fresh merge-tree cross-check at
  `3de99c9`), plus the R214 paragraph in "Khối mới nhất" (248 ký tự,
  marked chưa đăng — live body is R140) and the R215 note. The stale index
  reference in "Về bản mô tả này" (head `1afb41e`) is also fixed to
  `3de99c9`, and the title line is extended to R214 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R214 warning —
  applied with a measured correction, SINGLE): the R90 paragraph (494 ký tự — measured this
  round) is
  collapsed to one 208-ký-tự compact line (full detail stays in the
  delivery index) — the new R214 paragraph was 248 ký tự, so
  the body is 104.910 ký tự — net +115 vs R214 despite the new R214 paragraph, headroom 90 ký tự. The dry-run first projected 104.910 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  Paragraph order: the R214 paragraph sits directly after R213
  (ascending full-paragraph order R166..R214), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R215 (owner tap) — the R140 body v2 now live
  is the base; only the R214 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r215_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R214 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R214 and R215 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R214 (76 compact lines R90–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.910 ký tự),
  a check that the R214 paragraph sits directly after R213
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R214 note clean).
  New this round: the R213-row regression guard (cumulative must be 3035,
  re-derived from git at `2ce013b`), the R214-row guard (cumulative must
  cite 3038 — 3037 at `3de99c9` + 1 new checker in the R215 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R214, range R90–R165, list complete through R214, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 46/46**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R215_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R214) with the full COVER
  SHA verified intact (definition + docstring, both
  `3de99c9616ed11be0c47af0441a7693068f3c567` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `1afb41e` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R213-row guard string citing "3034 at 1afb41e", legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.910 ký tự and the apply wrote on
  the first attempt at 104.910 ký tự with 90 ký tự of headroom; the idempotency re-run
  after apply reported already-applied changed: 0 — verified.
  Correction caught before the report commit: the R214 row's cumulative figure was drafted as 3038 (3037 at
  `3de99c9` + 1 new checker) and the true diff at the R215 content
  commit is 3038 — verified by `git diff --name-only cf17178..6127a16` = 3038
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).

## R215 robustness note — headroom now only 90 chars

The R214 warning left 205 ký tự of headroom, so this round compacted
the R90 paragraph (494 ký tự → 208) before adding the new R214 paragraph
(248 ký tự). The body is now 104.910 ký tự — net +115 vs R214 — with
only 90 ký tự of headroom. The +115 net (vs +38 last round) came from the
head-line refresh: the honest MCP-mangle + rate-limit disclosure in the
head-line parenthetical cost ~89 ký tự. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R216 warning: headroom is only 90 ký tự; at the current +115/round growth a
single compaction per round NO LONGER holds — R216 must compact TWO paragraphs
(next: R89 + R88) or trim the new paragraph hard, or the body crosses 105,000.
At the current net +115/round the margin holds only with a double compaction;
one full-paragraph compaction per round (~−286) is no longer sustainable alone
(full paragraphs remaining R166..R214 = 49; compact block R90–R165 = 76 lines).
No ĐÍNH CHÍNH this round: R214's committed content verified correct —
the committed index at `3de99c9` carries the R212 row at cumulative 3032
(verified via `git show 3de99c9:...` this round) and the R213 row at 3035
(re-derived by the new checker from git at `2ce013b`); no uncommitted
working-tree fix was left behind by R214 (the working tree was clean at this
run's start and the fetch found no intervening push).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (104.910 projected; apply wrote 104.910 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214 — the R214 row's 3038 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first, not only
assert the OLD state — otherwise the re-run crashes on its own
pre-condition after a successful apply (R203/R207 lesson — re-run this
round reports already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two agreeing read paths settle
the live body faster than one mangled read did in R209 — the MCP path mangled
the first read this round ("Ă" → 2 U+FFFD) and the retry returned the clean body
(92.520, sha `ddbe32ff`); the direct curl read was rate-limited, so the honest
wording this round is "MCP retry clean, no direct cross-check" — never claim a
cross-check that did not run. When two read paths disagree on one character,
cross-check with a second path before claiming the live body changed. (6) A payload backup the authoring
round did not make must be disclosed as made by the folding round, not claimed as the author's — R214's
payload had no `.bak` copy when R215 started; R215 copied it and verified sha256 identical
(`46d74935…` both), and the R214 row records the copy as R215's, not R214's.

## Verification

- Merge-tree `3de99c9` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `b3ec0776…`. Merge-tree at the R215
  content head `6127a16` vs `f3db6b3`: exit 0,
  tree `edee53b8…`.
- Live PR state: API read twice this round (~07:40 JST) — first MCP read
  mangled 1 character ("Ă" → 2 U+FFFD, 92.521 ký tự, sha `ced29e00`), retry clean
  (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `3de99c9`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T21:46:41Z — bumped by the R214 push updating the PR head, body
  bytes unchanged); commits 619, changed_files 3037, additions 292490
  (API agrees with the fresh git derivation; the `deletions` key is 0 in
  the direct API response — git shows 0 deletions; the MCP response also
  returns `mergeable: null` — the direct read was rate-limited this round so
  `mergeable: true` could not be re-confirmed; mergeable_state clean is the operative field); mergeable_state clean at
  `3de99c9` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API + direct curl of comments — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R215 block (`3de99c9..6127a16`) 3 paths / 0 violations
  (index + body v2 + R215 checker); cumulative at the R215 content
  commit `6127a16` 3038 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `6127a16`).
  Merge-tree at the R215 content head `6127a16` vs `f3db6b3`: exit 0,
  tree `edee53b8…`.
- Transient notes: this round's `git fetch` at ~07:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (first PR read mangled — see live-read note; `pull_request_read` takes `pullNumber`, not
  `pull_number` — parameter-name lesson carried from R211; `issue_read`
  takes `issue_number`, not `issueNumber`). No execution-risk flag on any
  git/script command this round (unlike R211/R213). The R214 payload's own head line recorded
  mergeable clean at `1afb41e` at its preparation and clean at
  `3de99c9`; this round's API read confirms clean at `3de99c9`.
- Ceiling discipline: the R214 payload JSON measured 120.889 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (10.183 byte headroom). The projected R215 payload JSON is ~121,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.910
  ký tự (< 105.000) — 90 ký tự of headroom. R215 warning:
  headroom is now only 90 ký tự; a single compaction per round no longer holds
  at +115/round; the next round compacts R89 + R88.

## Next

Posting round (owner tap): PR #119 description refresh to the R215 body
v2 (R214 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r215.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R215 push (title
ending "+ R215", built by replacing the "+ R140" suffix — not appending;
body = body v2 R215 in repo, head line refreshed to head after R215 push).
This run started ~07:40 JST — BEFORE working hours (09:00–21:30 JST), so the
R215 payload is HELD FOR WORKING HOURS (not presented, like R142/R164–R197/R207–R214). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R214 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213 and R214 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R215: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
