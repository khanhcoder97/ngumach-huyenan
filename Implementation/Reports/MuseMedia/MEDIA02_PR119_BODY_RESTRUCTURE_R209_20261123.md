# MEDIA-02 — PR #119 Body Restructure R209: delivery index + body v2 coverage to `6cac9da`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `6cac9da` (PR119 BODY RESTRUCTURE R208 report). Content commit: `c663140`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R209 does

R208 left the disclosed gap: the delivery index covered 605 commits to
`d37a385`; R208's own 2 commits were to fold in at R209. The R208 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh direct-API read ~23:42 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T13:49:26Z — bumped by the R208 push updating the PR head, body bytes
unchanged). The R208 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~23:42 JST, read-only —
`issue_read get_comments` pages 1+2 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read with curl as cross-check): issue #116 34 comments, PR #119 head
`6cac9da`, 607 commits / 3019 files / +288,410, mergeable_state clean at
`6cac9da`, live body R140 92.520 ký tự sha `ddbe32ff`. Note: the MCP read path mangled one
character this round — "ĐĂNG" came back as "Đ��NG" (one "Ă" became 2 U+FFFD, body 92.521
ký tự, sha `ced29e00`) — a transport artifact, not a body change; the direct API read returned
the clean body byte-exact (0 U+FFFD, sha `ddbe32ff`), so the R140 live-body claim below rests
on the direct read, not the mangled MCP copy.

Fresh derivation at `6cac9da` (~23:40 JST): `git rev-list --count
cf17178..6cac9da` = 607 commits, `git diff --name-only` = 3019 files,
`--shortstat` = 288410 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `6cac9da` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `5ca33484…`. No re-fetch was needed before applying: the run fetched at ~23:40 JST
(the run start) and the remote head was still `6cac9da`, integration still `f3db6b3` — no
intervening push; the API read ~23:42 JST independently confirmed head `6cac9da`.

R209 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `6cac9da` (607 commits / 3019 files /
  288410 additions; the fresh git derivation at `6cac9da`, the fresh API
  read ~23:42 JST, and the merge-tree cross-check at `6cac9da` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `d37a385..6cac9da`: 5 paths, 634 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R208
  (`a89a1cf`/`6cac9da`), recording that its payload was prepared after
  push ~22:49 JST (104.968 ký tự, sha `b0762873`; JSON 121.410 byte < trần 131.072 — còn 9.662 byte, bản giữ tại
  `.bak-prepost-20261123` — thư mục tồn tại, bản R208 lưu tại đó,
  byte-identical với `pr_comments/` — sha256 `9bca5752…` cả hai, kiểm chứng lại lượt R206 — xem báo cáo R207),
  that it was NOT posted
  — live body still R140 (verified by this round's direct API read: description
  structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này qua API trực tiếp, 0 U+FFFD, updated_at 2026-11-23T13:49:26Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~23:42 JST).
  The index now covers every block through `6cac9da`; R209's
  own 2 commits fold in at the next index update (R210), disclosed in the
  index itself. The R209 note was appended after the R208 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `6cac9da` · 607 · 3019 (with the fresh git derivation at `6cac9da`,
  the fresh API read ~23:42 JST, and the fresh merge-tree cross-check at
  `6cac9da`), plus the R208 paragraph in "Khối mới nhất" (280 ký tự,
  marked chưa đăng — live body is R140) and the R209 note. The stale index
  reference in "Về bản mô tả này" (head `d37a385`) is also fixed to
  `6cac9da`, and the title line is extended to R208 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R208 warning —
  applied with a measured correction): the R97 paragraph (515 ký tự — measured this
  round) is
  collapsed to one 236-ký-tự compact line (full detail stays in the
  delivery index) — the new R208 paragraph was 280 ký tự, so
  the body is 104.972 ký tự — net +6 vs R208 despite the new R208 paragraph, headroom 28 ký tự. The dry-run first projected 105.163 ký tự
  (163 over the 105.000 ceiling) with the R208 paragraph at 319 ký tự and the head line at
  1056 ký tự (carrying the full MCP-mangling note); the paragraph was tightened by 39 ký tự (dropping
  "đồng bộ", the live-body char count and the "không ACK riêng" tail) and the head line by 145 ký tự
  (the MCP note moved to this report + the index row only, "của Codex"/"kể từ đó" dropped,
  "đổi do push R208 cập nhật head" shortened) before any write —
  measure, then trim, then apply.
  Paragraph order: the R208 paragraph sits directly after R207
  (ascending full-paragraph order R166..R208), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R209 (owner tap) — the R140 body v2 now live
  is the base; only the R208 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r209_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R208 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R208 and R209 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R208 (69 compact lines R97–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.972 ký tự),
  a check that the R208 paragraph sits directly after R207
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R208 note clean).
  New this round: the R207-row regression guard (cumulative must be 3017,
  re-derived from git at `a89a1cf`), the R208-row guard (cumulative must
  cite 3020 — 3019 at `6cac9da` + 1 new checker in the R209 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R208, range R97–R165, list complete through R208, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 34/34**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R209_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R208) with the full COVER
  SHA verified intact (definition + docstring, both
  `6cac9da0c970984d9b7f8f34d6b1e823c8c655ac` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (2 stale
  `d37a385` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R207-row guard string citing "3016 at d37a385", legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 105.163 ký tự and the apply wrote on
  the first attempt at 104.972 ký tự with 28 ký tự of headroom after the
  paragraph was tightened (see above); the idempotency re-run
  after apply reported already-applied changed: 0 — verified.
  Correction caught before the report commit: the R208 row's cumulative figure was drafted as 3020 (3019 at
  `6cac9da` + 1 new checker) and the true diff at the R209 content
  commit is 3020 — verified by `git diff --name-only cf17178..c663140` = 3020
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).

## R209 robustness note — headroom now 28 chars

The R208 warning left 34 ký tự of headroom, so this round compacted
the R97 paragraph (515 ký tự → 236) before adding the new R208 paragraph
(280 ký tự). The body is now 104.972 ký tự — net +6 vs R208 — with
28 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R210 warning: headroom is 28 ký tự; the next round must collapse R96
(full paragraph — measure first) and keep the new paragraph tight (≤ ~300 ký tự) — the
R96 compaction alone frees ~275 ký tự, restoring comfortable headroom.
At the current net +6/round the margin holds with compaction; one full-paragraph compaction per round (~−275) keeps
the discipline sustainable (full paragraphs remaining R166..R208 = 43;
compact block R97–R165 = 69 lines).
No ĐÍNH CHÍNH this round: R208's committed content verified correct —
the committed index at `6cac9da` carries the R206 row at cumulative 3014
(verified via `git show 6cac9da:...` this round) and the R207 row at 3017
(re-derived by the new checker from git at `a89a1cf`); no uncommitted
working-tree fix was left behind by R208 (status was EMPTY after its
report commit — see the R208 report — and this round's fetch found no
intervening push).
Lesson this round: (1) the dry-run projection caught a 163-char ceiling
overrun BEFORE any write (105.163 projected; paragraph tightened to 280
chars, head line to 911, apply wrote 104.972 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208 — the R208 row's 3020 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first, not only
assert the OLD state — otherwise the re-run crashes on its own
pre-condition after a successful apply (R203/R207 lesson — re-run this
round reports already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) A mangled read is not a changed
body: the MCP path turned one "Ă" into 2 U+FFFD this round (body 92.521
chars, sha `ced29e00`); the direct API read returned the clean body
byte-exact (92.520, sha `ddbe32ff`) — when two read paths disagree on
one character, cross-check with a second path before claiming the live
body changed.

## Verification

- Merge-tree `6cac9da` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `5ca33484…`. Merge-tree at the R209
  content head `c663140` vs `f3db6b3`: exit 0, tree
  `ff19c516…`.
- Live PR state: API read twice this round (~23:42 JST) — MCP read path
  mangled one "Ă" (see above; transport artifact only) and the direct
  public-API read (curl) returned the clean body — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `6cac9da`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T13:49:26Z — bumped by the R208 push updating the PR head, body
  bytes unchanged); commits 607, changed_files 3019, additions 288410
  (API agrees with the fresh git derivation; the `deletions` key is absent
  in this API response — git shows 0 deletions; the MCP response also
  returns `mergeable: null` — the direct read returns `mergeable: true`,
  mergeable_state clean is the operative field); mergeable_state clean at
  `6cac9da` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R209 block (`6cac9da..c663140`) 3 paths / 0 violations
  (index + body v2 + R209 checker); cumulative at the R209 content
  commit `c663140` 3020 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `c663140`).
  Merge-tree at the R209 content head `c663140` vs `f3db6b3`: exit 0,
  tree `ff19c516…`.
- Transient notes: this round's `git fetch` at ~23:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (but mangled one character in the PR body — see the live-read method note above;
  the direct curl cross-check settled it).
  The R208 payload's own head line recorded
  mergeable clean at `d37a385` at its preparation and clean at
  `6cac9da`; this round's API read confirms clean at `6cac9da`.
- Ceiling discipline: the R208 payload JSON measured 121.410 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.662 byte headroom). The projected R209 payload JSON is ~121,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.972
  ký tự (< 105.000) — 28 ký tự of headroom. R209 warning:
  headroom is now 28 ký tự; the next round must collapse R96 (full paragraph
  — measure first) and keep the new paragraph tight (≤ ~300 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R209 body
v2 (R208 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r209.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R209 push (title
ending "+ R209", built by replacing the "+ R140" suffix — not appending;
body = body v2 R209 in repo, head line refreshed to head after R209 push).
This run started ~23:40 JST — AFTER working hours (09:00–21:30 JST), so the
R209 payload is HELD FOR WORKING HOURS (not presented tonight, like R142/R164–R197/R207/R208). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R208 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207 and R208 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R209: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
