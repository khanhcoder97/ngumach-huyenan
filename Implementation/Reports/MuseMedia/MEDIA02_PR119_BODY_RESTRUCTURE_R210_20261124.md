# MEDIA-02 — PR #119 Body Restructure R210: delivery index + body v2 coverage to `e7eacae`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `e7eacae` (PR119 BODY RESTRUCTURE R209 report). Content commit: `a10f9f5`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R210 does

R209 left the disclosed gap: the delivery index covered 607 commits to
`6cac9da`; R209's own 2 commits were to fold in at R210. The R209 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh direct-API read ~00:45 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T14:49:57Z — bumped by the R209 push updating the PR head, body bytes
unchanged). The R209 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~00:45 JST, read-only —
`issue_read get_comments` pages 1+2 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read with curl as cross-check): the MCP read path returned the clean body
this round (no mangled character, unlike R209, when one "Ă" came back as 2 U+FFFD) and the
direct read agreed — issue #116 34 comments, PR #119 head
`e7eacae`, 609 commits / 3022 files / +289,058, mergeable_state clean at
`e7eacae`, live body R140 92.520 ký tự sha `ddbe32ff`.

Fresh derivation at `e7eacae` (~00:40 JST): `git rev-list --count
cf17178..e7eacae` = 609 commits, `git diff --name-only` = 3022 files,
`--shortstat` = 289058 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `e7eacae` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `c0ebfb8c…`. No re-fetch was needed before applying: the run fetched at ~00:40 JST
(the run start) and the remote head was still `e7eacae`, integration still `f3db6b3` — no
intervening push; the API read ~00:45 JST independently confirmed head `e7eacae`.

R210 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `e7eacae` (609 commits / 3022 files /
  289058 additions; the fresh git derivation at `e7eacae`, the fresh API
  read ~00:45 JST, and the merge-tree cross-check at `e7eacae` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `6cac9da..e7eacae`: 5 paths, 659 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R209
  (`c663140`/`e7eacae`), recording that its payload was prepared after
  push ~23:50 JST (104.983 ký tự, sha `7a74d806`; JSON 121.382 byte < trần 131.072 — còn 9.690 byte, bản giữ tại
  `.bak-prepost-20261123` — thư mục tồn tại, bản R209 lưu tại đó,
  byte-identical với `pr_comments/` — sha256 `d89111fc…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's direct API read and MCP read, both clean:
  description structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này qua API trực tiếp, 0 U+FFFD, updated_at 2026-11-23T14:49:57Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~00:45 JST).
  The index now covers every block through `e7eacae`; R210's
  own 2 commits fold in at the next index update (R211), disclosed in the
  index itself. The R210 note was appended after the R209 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `e7eacae` · 609 · 3022 (with the fresh git derivation at `e7eacae`,
  the fresh API read ~00:45 JST, and the fresh merge-tree cross-check at
  `e7eacae`), plus the R209 paragraph in "Khối mới nhất" (248 ký tự,
  marked chưa đăng — live body is R140) and the R210 note. The stale index
  reference in "Về bản mô tả này" (head `6cac9da`) is also fixed to
  `e7eacae`, and the title line is extended to R209 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R209 warning —
  applied with a measured correction): the R96 paragraph (483 ký tự — measured this
  round) is
  collapsed to one 219-ký-tự compact line (full detail stays in the
  delivery index) — the new R209 paragraph was 248 ký tự (the "live vẫn R140" clause the
  R207/R208 paragraphs carried is dropped here — the live-body state is already recorded
  in the head line and in the R209 index row), so
  the body is 104.957 ký tự — net −15 vs R209 despite the new R209 paragraph, headroom 43 ký tự. The dry-run first projected 104.989 ký tự
  (headroom 11) with the clause kept; the clause was dropped before any write (saving 31 ký tự)
  and the head line was already 62 ký tự shorter than R209's (fetch parenthetical moved to the
  index/report only) — measure, then trim, then apply.
  Paragraph order: the R209 paragraph sits directly after R208
  (ascending full-paragraph order R166..R209), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R210 (owner tap) — the R140 body v2 now live
  is the base; only the R209 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r210_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R209 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R209 and R210 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R209 (70 compact lines R96–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.957 ký tự),
  a check that the R209 paragraph sits directly after R208
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R209 note clean).
  New this round: the R208-row regression guard (cumulative must be 3020,
  re-derived from git at `c663140`), the R209-row guard (cumulative must
  cite 3023 — 3022 at `e7eacae` + 1 new checker in the R210 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R209, range R96–R165, list complete through R209, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 36/36**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R210_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R209) with the full COVER
  SHA verified intact (definition + docstring, both
  `e7eacae83861e7e135c4328ed52e67721cb17cd4` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `6cac9da` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R208-row guard string citing "3019 at 6cac9da", legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.989 ký tự and the apply wrote on
  the first attempt at 104.957 ký tự with 43 ký tự of headroom after the
  paragraph was tightened (see above); the idempotency re-run
  after apply reported already-applied changed: 0 — verified.
  Correction caught before the report commit: the R209 row's cumulative figure was drafted as 3023 (3022 at
  `e7eacae` + 1 new checker) and the true diff at the R210 content
  commit is 3023 — verified by `git diff --name-only cf17178..a10f9f5` = 3023
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).

## R210 robustness note — headroom now 43 chars

The R209 warning left 28 ký tự of headroom, so this round compacted
the R96 paragraph (483 ký tự → 219) before adding the new R209 paragraph
(248 ký tự). The body is now 104.957 ký tự — net −15 vs R209 — with
43 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R211 warning: headroom is 43 ký tự; the next round must collapse R95
(full paragraph — measure first) and keep the new paragraph tight (≤ ~300 ký tự) — the
R95 compaction alone frees ~250 ký tự, restoring comfortable headroom.
At the current net −15/round the margin holds with compaction; one full-paragraph compaction per round (~−250) keeps
the discipline sustainable (full paragraphs remaining R166..R209 = 44;
compact block R96–R165 = 70 lines).
No ĐÍNH CHÍNH this round: R209's committed content verified correct —
the committed index at `e7eacae` carries the R207 row at cumulative 3017
(verified via `git show e7eacae:...` this round) and the R208 row at 3020
(re-derived by the new checker from git at `c663140`); no uncommitted
working-tree fix was left behind by R209 (the working tree was clean at this
run's start and the fetch found no intervening push).
Lesson this round: (1) the dry-run projection caught a thin headroom of 11 chars
BEFORE any write (104.989 projected; paragraph tightened by dropping one redundant
clause to 248 chars, apply wrote 104.957 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209 — the R209 row's 3023 was verified post-commit by git
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
cross-check with a second path before claiming the live body changed.

## Verification

- Merge-tree `e7eacae` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `c0ebfb8c…`. Merge-tree at the R210
  content head `a10f9f5` vs `f3db6b3`: exit 0, tree
  `c9446ff8…`.
- Live PR state: API read twice this round (~00:45 JST) — MCP read path
  returned the clean body this round (no mangling, unlike R209) and the direct
  public-API read (curl) agreed — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `e7eacae`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T14:49:57Z — bumped by the R209 push updating the PR head, body
  bytes unchanged); commits 609, changed_files 3022, additions 289058
  (API agrees with the fresh git derivation; the `deletions` key is absent
  in this API response — git shows 0 deletions; the MCP response also
  returns `mergeable: null` — the direct read returns `mergeable: true`,
  mergeable_state clean is the operative field); mergeable_state clean at
  `e7eacae` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R210 block (`e7eacae..a10f9f5`) 3 paths / 0 violations
  (index + body v2 + R210 checker); cumulative at the R210 content
  commit `a10f9f5` 3023 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `a10f9f5`).
  Merge-tree at the R210 content head `a10f9f5` vs `f3db6b3`: exit 0,
  tree `c9446ff8…`.
- Transient notes: this round's `git fetch` at ~00:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (clean read, no mangling — unlike R209).
  The R209 payload's own head line recorded
  mergeable clean at `6cac9da` at its preparation and clean at
  `e7eacae`; this round's API read confirms clean at `e7eacae`.
- Ceiling discipline: the R209 payload JSON measured 121.382 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.690 byte headroom). The projected R210 payload JSON is ~121,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.957
  ký tự (< 105.000) — 43 ký tự of headroom. R210 warning:
  headroom is now 43 ký tự; the next round must collapse R95 (full paragraph
  — measure first) and keep the new paragraph tight (≤ ~300 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R210 body
v2 (R209 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r210.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R210 push (title
ending "+ R210", built by replacing the "+ R140" suffix — not appending;
body = body v2 R210 in repo, head line refreshed to head after R210 push).
This run started ~00:40 JST — AFTER working hours (09:00–21:30 JST), so the
R210 payload is HELD FOR WORKING HOURS (not presented tonight, like R142/R164–R197/R207/R208/R209). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R209 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208 and R209 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R210: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
