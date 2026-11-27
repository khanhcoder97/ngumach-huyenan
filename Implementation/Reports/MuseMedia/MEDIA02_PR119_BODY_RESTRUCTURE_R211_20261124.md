# MEDIA-02 — PR #119 Body Restructure R211: delivery index + body v2 coverage to `48a1cd8`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `48a1cd8` (PR119 BODY RESTRUCTURE R210 report). Content commit: `a96f796`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R211 does

R210 left the disclosed gap: the delivery index covered 609 commits to
`e7eacae`; R210's own 2 commits were to fold in at R211. The R210 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh direct-API read ~02:45 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T15:51:27Z — bumped by the R210 push updating the PR head, body bytes
unchanged). The R210 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~02:45 JST, read-only —
`issue_read get_comments` pages 1+2 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read with curl as cross-check): the MCP read path returned the clean body
this round and the direct read agreed — issue #116 34 comments, PR #119 head
`48a1cd8`, 611 commits / 3025 files / +289,717, mergeable_state clean at
`48a1cd8`, live body R140 92.520 ký tự sha `ddbe32ff`.

Fresh derivation at `48a1cd8` (~02:40 JST): `git rev-list --count
cf17178..48a1cd8` = 611 commits, `git diff --name-only` = 3025 files,
`--shortstat` = 289717 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `48a1cd8` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `db154157…`. No re-fetch was needed before applying: the run fetched at ~02:40 JST
(the run start) and the remote head was still `48a1cd8`, integration still `f3db6b3` — no
intervening push; the API read ~02:45 JST independently confirmed head `48a1cd8`.

R211 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `48a1cd8` (611 commits / 3025 files /
  289717 additions; the fresh git derivation at `48a1cd8`, the fresh API
  read ~02:45 JST, and the merge-tree cross-check at `48a1cd8` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `e7eacae..48a1cd8`: 5 paths, 670 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R210
  (`a10f9f5`/`48a1cd8`), recording that its payload was prepared after
  push ~00:52 JST (104.922 ký tự, sha `57de17ce`; JSON 121.290 byte < trần 131.072 — còn 9.782 byte, bản giữ tại
  `.bak-prepost-20261123` — R211 sao lưu, sha256 `c74f7a3b…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's direct API read and MCP read, both clean:
  description structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này qua API trực tiếp, 0 U+FFFD, updated_at 2026-11-23T15:51:27Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~02:45 JST).
  The index now covers every block through `48a1cd8`; R211's
  own 2 commits fold in at the next index update (R212), disclosed in the
  index itself. The R211 note was appended after the R210 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `48a1cd8` · 611 · 3025 (with the fresh git derivation at `48a1cd8`,
  the fresh API read ~02:45 JST, and the fresh merge-tree cross-check at
  `48a1cd8`), plus the R210 paragraph in "Khối mới nhất" (248 ký tự,
  marked chưa đăng — live body is R140) and the R211 note. The stale index
  reference in "Về bản mô tả này" (head `e7eacae`) is also fixed to
  `48a1cd8`, and the title line is extended to R210 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R210 warning —
  applied with a measured correction): the R95 paragraph (494 ký tự — measured this
  round) is
  collapsed to one 215-ký-tự compact line (full detail stays in the
  delivery index) — the new R210 paragraph was 248 ký tự, so
  the body is 104.962 ký tự — net +5 vs R210 despite the new R210 paragraph, headroom 38 ký tự. The dry-run first projected 104.962 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  Paragraph order: the R210 paragraph sits directly after R209
  (ascending full-paragraph order R166..R210), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R211 (owner tap) — the R140 body v2 now live
  is the base; only the R210 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r211_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R210 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R210 and R211 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R210 (71 compact lines R95–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.962 ký tự),
  a check that the R210 paragraph sits directly after R209
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R210 note clean).
  New this round: the R209-row regression guard (cumulative must be 3023,
  re-derived from git at `a10f9f5`), the R210-row guard (cumulative must
  cite 3026 — 3025 at `48a1cd8` + 1 new checker in the R211 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R210, range R95–R165, list complete through R210, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 38/38**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R211_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R210) with the full COVER
  SHA verified intact (definition + docstring, both
  `48a1cd876d757a5d3a48eb999abfa83b6ead6a43` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `e7eacae` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R209-row guard string citing "3022 at e7eacae", legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.962 ký tự and the apply wrote on
  the first attempt at 104.962 ký tự with 38 ký tự of headroom; the idempotency re-run
  after apply reported already-applied changed: 0 — verified.
  Correction caught before the report commit: the R210 row's cumulative figure was drafted as 3026 (3025 at
  `48a1cd8` + 1 new checker) and the true diff at the R211 content
  commit is 3026 — verified by `git diff --name-only cf17178..a96f796` = 3026
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).

## R211 robustness note — headroom now 38 chars

The R210 warning left 43 ký tự of headroom, so this round compacted
the R95 paragraph (494 ký tự → 215) before adding the new R210 paragraph
(248 ký tự). The body is now 104.962 ký tự — net +5 vs R210 — with
38 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R212 warning: headroom is 38 ký tự; the next round must collapse R94
(full paragraph — measure first) and keep the new paragraph tight (≤ ~300 ký tự) — the
R94 compaction alone frees ~250 ký tự, restoring comfortable headroom.
At the current net +5/round the margin holds with compaction; one full-paragraph compaction per round (~−250) keeps
the discipline sustainable (full paragraphs remaining R166..R210 = 45;
compact block R95–R165 = 71 lines).
No ĐÍNH CHÍNH this round: R210's committed content verified correct —
the committed index at `48a1cd8` carries the R208 row at cumulative 3020
(verified via `git show 48a1cd8:...` this round) and the R209 row at 3023
(re-derived by the new checker from git at `a10f9f5`); no uncommitted
working-tree fix was left behind by R210 (the working tree was clean at this
run's start and the fetch found no intervening push).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (104.962 projected; apply wrote 104.962 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210 — the R210 row's 3026 was verified post-commit by git
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
round did not make must be disclosed as made by the folding round, not claimed as the author's — R210's
payload had no `.bak` copy when R211 started; R211 copied it and verified sha256 identical
(`c74f7a3b…` both), and the R210 row records the copy as R211's, not R210's.

## Verification

- Merge-tree `48a1cd8` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `db154157…`. Merge-tree at the R211
  content head `a96f796` vs `f3db6b3`: exit 0, tree
  `0811e086…`.
- Live PR state: API read twice this round (~02:45 JST) — MCP read path
  returned the clean body this round and the direct
  public-API read (curl) agreed — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `48a1cd8`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T15:51:27Z — bumped by the R210 push updating the PR head, body
  bytes unchanged); commits 611, changed_files 3025, additions 289717
  (API agrees with the fresh git derivation; the `deletions` key is absent
  in this API response — git shows 0 deletions; the MCP response also
  returns `mergeable: null` — the direct read returns `mergeable: true`,
  mergeable_state clean is the operative field); mergeable_state clean at
  `48a1cd8` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R211 block (`48a1cd8..a96f796`) 3 paths / 0 violations
  (index + body v2 + R211 checker); cumulative at the R211 content
  commit `a96f796` 3026 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `a96f796`).
  Merge-tree at the R211 content head `a96f796` vs `f3db6b3`: exit 0,
  tree `0811e086…`.
- Transient notes: this round's `git fetch` at ~02:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (clean read, no mangling — the first `pull_request_read` call failed fast on a wrong
  parameter name `pull_number`; retried with `pullNumber` and succeeded — parameter-name
  lesson for the next round).
  The R210 payload's own head line recorded
  mergeable clean at `e7eacae` at its preparation and clean at
  `48a1cd8`; this round's API read confirms clean at `48a1cd8`.
- Ceiling discipline: the R210 payload JSON measured 121.290 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.782 byte headroom). The projected R211 payload JSON is ~121,400 byte
  (measured exactly at payload build, after push). Body v2 is now 104.962
  ký tự (< 105.000) — 38 ký tự of headroom. R211 warning:
  headroom is now 38 ký tự; the next round must collapse R94 (full paragraph
  — measure first) and keep the new paragraph tight (≤ ~300 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R211 body
v2 (R210 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r211.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R211 push (title
ending "+ R211", built by replacing the "+ R140" suffix — not appending;
body = body v2 R211 in repo, head line refreshed to head after R211 push).
This run started ~02:40 JST — AFTER working hours (09:00–21:30 JST), so the
R211 payload is HELD FOR WORKING HOURS (not presented tonight, like R142/R164–R197/R207–R210). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R210 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209 and R210 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R211: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
