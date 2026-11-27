# MEDIA-02 — PR #119 Body Restructure R212: delivery index + body v2 coverage to `3a4c8f8`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `3a4c8f8` (PR119 BODY RESTRUCTURE R211 report). Content commit: `dd853fe`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R212 does

R211 left the disclosed gap: the delivery index covered 611 commits to
`48a1cd8`; R211's own 2 commits were to fold in at R212. The R211 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh direct-API read ~03:45 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T17:49:26Z — bumped by the R211 push updating the PR head, body bytes
unchanged). The R211 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~03:45 JST, read-only —
`issue_read get_comments` pages 1+2 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read with curl as cross-check): the MCP read path returned the clean body
this round and the direct read agreed — issue #116 34 comments, PR #119 head
`3a4c8f8`, 613 commits / 3028 files / +290,387, mergeable_state clean at
`3a4c8f8`, live body R140 92.520 ký tự sha `ddbe32ff`.

Fresh derivation at `3a4c8f8` (~03:40 JST): `git rev-list --count
cf17178..3a4c8f8` = 613 commits, `git diff --name-only` = 3028 files,
`--shortstat` = 290387 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `3a4c8f8` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `ffda2863…`. No re-fetch was needed before applying: the run fetched at ~03:40 JST
(the run start) and the remote head was still `3a4c8f8`, integration still `f3db6b3` — no
intervening push; the API read ~03:45 JST independently confirmed head `3a4c8f8`.

R212 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `3a4c8f8` (613 commits / 3028 files /
  290387 additions; the fresh git derivation at `3a4c8f8`, the fresh API
  read ~03:45 JST, and the merge-tree cross-check at `3a4c8f8` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `48a1cd8..3a4c8f8`: 5 paths, 681 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R211
  (`a96f796`/`3a4c8f8`), recording that its payload was prepared after
  push ~02:50 JST (104.927 ký tự, sha `ac0b0f91`; JSON 121.241 byte < trần 131.072 — còn 9.831 byte, bản giữ tại
  `.bak-prepost-20261123` — R212 sao lưu, sha256 `65b06188…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's direct API read and MCP read, both clean:
  description structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này qua API trực tiếp, 0 U+FFFD, updated_at 2026-11-23T17:49:26Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~03:45 JST).
  The index now covers every block through `3a4c8f8`; R212's
  own 2 commits fold in at the next index update (R213), disclosed in the
  index itself. The R212 note was appended after the R211 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `3a4c8f8` · 613 · 3028 (with the fresh git derivation at `3a4c8f8`,
  the fresh API read ~03:45 JST, and the fresh merge-tree cross-check at
  `3a4c8f8`), plus the R211 paragraph in "Khối mới nhất" (248 ký tự,
  marked chưa đăng — live body is R140) and the R212 note. The stale index
  reference in "Về bản mô tả này" (head `48a1cd8`) is also fixed to
  `3a4c8f8`, and the title line is extended to R211 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R211 warning —
  applied with a measured correction): the R94 paragraph (494 ký tự — measured this
  round) is
  collapsed to one 215-ký-tự compact line (full detail stays in the
  delivery index) — the new R211 paragraph was 248 ký tự, so
  the body is 104.994 ký tự — net +32 vs R211 despite the new R211 paragraph, headroom 6 ký tự. The dry-run first projected 104.994 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  Paragraph order: the R211 paragraph sits directly after R210
  (ascending full-paragraph order R166..R211), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R212 (owner tap) — the R140 body v2 now live
  is the base; only the R211 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r212_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R211 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R211 and R212 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R211 (72 compact lines R94–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.994 ký tự),
  a check that the R211 paragraph sits directly after R210
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R211 note clean).
  New this round: the R210-row regression guard (cumulative must be 3026,
  re-derived from git at `a96f796`), the R211-row guard (cumulative must
  cite 3029 — 3028 at `3a4c8f8` + 1 new checker in the R212 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R211, range R94–R165, list complete through R211, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 40/40**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R212_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R211) with the full COVER
  SHA verified intact (definition + docstring, both
  `3a4c8f88d3c9472e121e65b99d6ddbf3a9aabb51` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (2 stale
  `48a1cd8` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R210-row guard string citing "3025 at 48a1cd8", legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.994 ký tự and the apply wrote on
  the first attempt at 104.994 ký tự with 6 ký tự of headroom; the idempotency re-run
  after apply reported already-applied changed: 0 — verified.
  Correction caught before the report commit: the R211 row's cumulative figure was drafted as 3029 (3028 at
  `3a4c8f8` + 1 new checker) and the true diff at the R212 content
  commit is 3029 — verified by `git diff --name-only cf17178..dd853fe` = 3029
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).

## R212 robustness note — headroom now 6 chars

The R211 warning left 38 ký tự of headroom, so this round compacted
the R94 paragraph (494 ký tự → 215) before adding the new R211 paragraph
(248 ký tự). The body is now 104.994 ký tự — net +32 vs R211 — with
6 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R213 warning: headroom is 6 ký tự; single compaction NO LONGER suffices
at the current +32/round growth — the next round must collapse R93 AND
compact a second paragraph (R92), or trim the new paragraph hard, or the
body crosses 105.000. At the current net +32/round the margin holds only
with a double compaction; one full-paragraph compaction per round (~−250)
is no longer sustainable on its own (full paragraphs remaining R166..R211 = 46;
compact block R94–R165 = 72 lines).
No ĐÍNH CHÍNH this round: R211's committed content verified correct —
the committed index at `3a4c8f8` carries the R209 row at cumulative 3023
(verified via `git show 3a4c8f8:...` this round) and the R210 row at 3026
(re-derived by the new checker from git at `a96f796`); no uncommitted
working-tree fix was left behind by R211 (the working tree was clean at this
run's start and the fetch found no intervening push).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (104.994 projected; apply wrote 104.994 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211 — the R211 row's 3029 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first, not only
assert the OLD state — otherwise the re-run crashes on its own
pre-condition after a successful apply (R203/R207 lesson — re-run this
round reports already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two agreeing read paths settle
the live body faster than one mangled read did in R209 — the MCP path returned
the clean body this round and the direct curl read agreed byte-exact
(92.520, sha `ddbe32ff`); when two read paths disagree on one character,
cross-check with a second path before claiming the live body changed. (6) A payload backup the authoring
round did not make must be disclosed as made by the folding round, not claimed as the author's — R211's
payload had no `.bak` copy when R212 started; R212 copied it and verified sha256 identical
(`65b06188…` both), and the R211 row records the copy as R212's, not R211's.

## Verification

- Merge-tree `3a4c8f8` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `ffda2863…`. Merge-tree at the R212
  content head `dd853fe` vs `f3db6b3`: exit 0, tree
  `d091a2c4…`.
- Live PR state: API read twice this round (~03:45 JST) — MCP read path
  returned the clean body this round and the direct
  public-API read (curl) agreed — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `3a4c8f8`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T17:49:26Z — bumped by the R211 push updating the PR head, body
  bytes unchanged); commits 613, changed_files 3028, additions 290387
  (API agrees with the fresh git derivation; the `deletions` key is absent
  in this API response — git shows 0 deletions; the MCP response also
  returns `mergeable: null` — the direct read returns `mergeable: true`,
  mergeable_state clean is the operative field); mergeable_state clean at
  `3a4c8f8` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R212 block (`3a4c8f8..dd853fe`) 3 paths / 0 violations
  (index + body v2 + R212 checker); cumulative at the R212 content
  commit `dd853fe` 3029 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `dd853fe`).
  Merge-tree at the R212 content head `dd853fe` vs `f3db6b3`: exit 0,
  tree `d091a2c4…`.
- Transient notes: this round's `git fetch` at ~03:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (clean read, no mangling — `pull_request_read` takes `pullNumber`, not
  `pull_number` — parameter-name lesson carried from R211).
  The R211 payload's own head line recorded
  mergeable clean at `48a1cd8` at its preparation and clean at
  `3a4c8f8`; this round's API read confirms clean at `3a4c8f8`.
- Ceiling discipline: the R211 payload JSON measured 121.241 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.831 byte headroom). The projected R212 payload JSON is ~121,300 byte
  (measured exactly at payload build, after push). Body v2 is now 104.994
  ký tự (< 105.000) — 6 ký tự of headroom. R212 warning:
  headroom is now 6 ký tự; the next round must collapse R93 AND compact a
  second paragraph (R92), or trim the new paragraph hard.

## Next

Posting round (owner tap): PR #119 description refresh to the R212 body
v2 (R211 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r212.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R212 push (title
ending "+ R212", built by replacing the "+ R140" suffix — not appending;
body = body v2 R212 in repo, head line refreshed to head after R212 push).
This run started ~03:40 JST — AFTER working hours (09:00–21:30 JST), so the
R212 payload is HELD FOR WORKING HOURS (not presented tonight, like R142/R164–R197/R207–R211). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R211 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210 and R211 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R212: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
