# MEDIA-02 — PR #119 Body Restructure R208: delivery index + body v2 coverage to `d37a385`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `d37a385` (PR119 BODY RESTRUCTURE R207 report). Content commit: `a89a1cf`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R208 does

R207 left the disclosed gap: the delivery index covered 603 commits to
`5a1ec4c`; R207's own 2 commits were to fold in at R208. The R207 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API read ~22:42 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T12:49:11Z — bumped by the R207 push updating the PR head, body bytes
unchanged). The R207 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read via the MCP read
path (~22:41–22:42 JST, read-only — `issue_read get_comments` pages 1+2 and
`pull_request_read get` via `call-read-tool`, no stall this round, so no
browser fallback was needed): issue #116 34 comments, PR #119 head
`d37a385`, 605 commits / 3016 files / +287,787, mergeable_state clean at
`d37a385`, live body R140 92.520 ký tự sha `ddbe32ff`. Note: the API
`mergeable` field itself returned null at read time — mergeable_state
clean is the operative field (see Verification).

Fresh derivation at `d37a385` (~22:40 JST): `git rev-list --count
cf17178..d37a385` = 605 commits, `git diff --name-only` = 3016 files,
`--shortstat` = 287787 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `d37a385` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `9dfb470b…`. No re-fetch was needed before applying: the run fetched at ~22:40 JST
(the run start) and the remote head was still `d37a385`, integration still `f3db6b3` — no
intervening push; the API read ~22:42 JST independently confirmed head `d37a385`.

R208 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `d37a385` (605 commits / 3016 files /
  287787 additions; the fresh git derivation at `d37a385`, the fresh API
  read ~22:42 JST, and the merge-tree cross-check at `d37a385` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `5a1ec4c..d37a385`: 5 paths, 637 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R207
  (`0db08af`/`d37a385`), recording that its payload was prepared after
  push ~21:49 JST (104.979 ký tự, sha `d602f6c6`; JSON 121.475 byte < trần 131.072 — còn 9.597 byte, bản giữ tại
  `.bak-prepost-20261123` — thư mục tồn tại, bản R207 lưu tại đó,
  byte-identical với `pr_comments/` — sha256 `9bca5752…` cả hai, kiểm chứng lại lượt R206 — xem báo cáo R207),
  that it was NOT posted
  — live body still R140 (verified by this round's API read: description
  structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này, 0 U+FFFD, updated_at 2026-11-23T12:49:11Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~22:42 JST).
  The index now covers every block through `d37a385`; R208's
  own 2 commits fold in at the next index update (R209), disclosed in the
  index itself. The R208 note was appended after the R207 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `d37a385` · 605 · 3016 (with the fresh git derivation at `d37a385`,
  the fresh API read ~22:42 JST, and the fresh merge-tree cross-check at
  `d37a385`), plus the R207 paragraph in "Khối mới nhất" (302 ký tự,
  marked chưa đăng — live body is R140) and the R208 note. The stale index
  reference in "Về bản mô tả này" (head `5a1ec4c`) is also fixed to
  `d37a385`, and the title line is extended to R207 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R207 warning —
  applied with a measured correction): the R98 paragraph (609 ký tự — measured this
  round) is
  collapsed to one 236-ký-tự compact line (full detail stays in the
  delivery index) — the new R207 paragraph was 302 ký tự, so
  the body is 104.966 ký tự — net −11 vs R207 despite the new R207
  paragraph, headroom 34 ký tự. The dry-run first projected 105.029 ký tự
  (29 over the 105.000 ceiling) with the R207 paragraph at 350 ký tự and the R98
  compact line at 251 ký tự; the paragraph was tightened by 48 ký tự (dropping the
  mergeable clause already carried by the head line, and the "không ACK riêng" tail
  carried by the index row) and the compact line by 15 ký tự before any write —
  measure, then trim, then apply.
  Paragraph order: the R207 paragraph sits directly after R206
  (ascending full-paragraph order R166..R207), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R208 (owner tap) — the R140 body v2 now live
  is the base; only the R207 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r208_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R207 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R207 and R208 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R207 (68 compact lines R98–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.966 ký tự),
  a check that the R207 paragraph sits directly after R206
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R207 note clean).
  New this round: the R206-row regression guard (cumulative must be 3014,
  re-derived from git at `0db08af`), the R207-row guard (cumulative must
  cite 3017 — 3016 at `d37a385` + 1 new checker in the R208 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R207, range R98–R165, list complete through R207, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 32/32**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R208_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R207) with the full COVER
  SHA verified intact (definition + docstring, both
  `d37a3850a2f434a3a76129215e6a9ffc2d3e3da8` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `5a1ec4c` references in the checker — the one `5a1ec4c` hit is the
  docstring explaining the previous cover value, intentional — the R207 cover value)
  before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 105.029 ký tự and the apply wrote on
  the first attempt at 104.966 ký tự with 34 ký tự of headroom after the
  paragraph was tightened (see above); the idempotency re-run
  after apply reported already-applied changed: 0 — verified.
  Correction caught before the report commit: the R207 row's cumulative figure was drafted as 3017 (3016 at
  `d37a385` + 1 new checker) and the true diff at the R208 content
  commit is 3017 — verified by `git diff --name-only cf17178..a89a1cf` = 3017
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).

## R208 robustness note — headroom now 34 chars

The R207 warning left 23 ký tự of headroom, so this round compacted
the R98 paragraph (609 ký tự → 236) before adding the new R207 paragraph
(302 ký tự). The body is now 104.966 ký tự — net −11 vs R207 — with
34 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R209 warning: headroom is 34 ký tự; the next round must collapse R97
(515 ký tự — measured this round → ~240) and keep the new paragraph tight (≤ ~310 ký tự) — the
R97 compaction alone frees ~275 ký tự, restoring comfortable headroom.
At the current net −11/round the margin holds with compaction; one full-paragraph compaction per round (~−275) keeps
the discipline sustainable (full paragraphs remaining R166..R207 = 42;
compact block R98–R165 = 68 lines).
No ĐÍNH CHÍNH this round: R207's committed content verified correct —
the committed index at `d37a385` carries the R205 row at cumulative 3011
(verified via `git show HEAD:...` this round) and the R206 row at 3014
(re-derived by the new checker from git at `0db08af`); no uncommitted
working-tree fix was left behind by R207 (status was EMPTY after its
report commit — see the R207 report — and this round's fetch found no
intervening push).
Lesson this round: (1) the dry-run projection caught a 29-char ceiling
overrun BEFORE any write (105.029 projected; paragraph tightened to 302
chars, compact line to 236, apply wrote 104.966 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207 — the R207 row's 3017 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first, not only
assert the OLD state — otherwise the re-run crashes on its own
pre-condition after a successful apply (R203/R207 lesson — re-run this
round reports already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked).

## Verification

- Merge-tree `d37a385` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `9dfb470b…`. Merge-tree at the R208
  content head `a89a1cf` vs `f3db6b3`: exit 0, tree
  `0a1ce660…`.
- Live PR state: API read via MCP ~22:42 JST (read path
  healthy — `call-read-tool` accepted `issue_read`/`pull_request_read`
  this round) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `d37a385`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T12:49:11Z — bumped by the R207 push updating the PR head, body
  bytes unchanged); commits 605, changed_files 3016, additions 287787
  (API agrees with the fresh git derivation; the `deletions` key is absent
  in this API response — git shows 0 deletions; the raw API payload also
  returns `mergeable: null` — mergeable_state clean is the operative
  field); mergeable_state clean at
  `d37a385` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R208 block (`d37a385..a89a1cf`) 3 paths / 0 violations
  (index + body v2 + R208 checker); cumulative at the R208 content
  commit `a89a1cf` 3017 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `a89a1cf`).
  Merge-tree at the R208 content head `a89a1cf` vs `f3db6b3`: exit 0,
  tree `0a1ce660…`.
- Transient notes: this round's `git fetch` at ~22:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round.
  The R207 payload's own head line recorded
  mergeable clean at `5a1ec4c` at its preparation and clean at
  `d37a385`; this round's API read confirms clean at `d37a385`.
- Ceiling discipline: the R207 payload JSON measured 121.475 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.597 byte headroom). The projected R208 payload JSON is ~121,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.966
  ký tự (< 105.000) — 34 ký tự of headroom. R208 warning:
  headroom is now 34 ký tự; the next round must collapse R97 (515 ký tự
  → ~240) and keep the new paragraph tight (≤ ~310 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R208 body
v2 (R207 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r208.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R208 push (title
ending "+ R208", built by replacing the "+ R140" suffix — not appending;
body = body v2 R208 in repo, head line refreshed to head after R208 push).
This run started ~22:40 JST — AFTER working hours (09:00–21:30 JST), so the
R208 payload is HELD FOR WORKING HOURS (not presented tonight, like R142/R164–R197/R207). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R207 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206 and R207 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R208: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
