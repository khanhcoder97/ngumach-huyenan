# MEDIA-02 — PR #119 Body Restructure R202: delivery index + body v2 coverage to `003f1bb`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `003f1bb` (PR119 BODY RESTRUCTURE R201 report). Content commit: `e50ba30`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R202 does

R201 left the disclosed gap: the delivery index covered 591 commits to
`5e5fbba`; R201's own 2 commits were to fold in at R202. The R201 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API read ~16:42 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T06:46:04Z — bumped by the R201 push updating the PR head, body bytes
unchanged). The R201 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub MCP read path WORKED
(`call-read-tool`, no stall, no rate-limit 403) — `issue_read get_comments`
and `pull_request_read get` both returned cleanly ~16:42 JST, so every
live figure this round is a fresh API byte-exact read, not a browser
fallback and not carried from an earlier round: issue #116 34 comments,
PR #119 head `003f1bb`, 593 commits / 2998 files / +284,536, mergeable_state
clean at `003f1bb`, live body R140 92.520 ký tự sha `ddbe32ff`.
Pagination note (new this round): `issue_read get_comments` paginates
at 30 comments per page — the first page alone returns 30 comments
(latest `6819808977`) and looks complete, but is not; page 2 returns
the remaining 4 (`6831053345`, `6832706291`, `6833806995`,
`6862732081`), for the 34 total. Always fetch page 2 before stating
the comment total.

Fresh derivation at `003f1bb` (~16:42 JST): `git rev-list --count
cf17178..003f1bb` = 593 commits, `git diff --name-only` = 2998 files,
`--shortstat` = 284536 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `003f1bb` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `c89b0ff4…`. No re-fetch was needed before applying: the run fetched at ~16:40 JST
(the run start) and the remote head was still `003f1bb`, integration still `f3db6b3` — no
intervening push; the API read ~16:42 JST independently confirmed head `003f1bb`.

R202 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `003f1bb` (593 commits / 2998 files /
  284536 additions; the fresh git derivation at `003f1bb`, the fresh API
  read ~16:42 JST, and the merge-tree cross-check at `003f1bb` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `5e5fbba..003f1bb`: 5 paths, 528 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R201
  (`409c2f2`/`003f1bb`), recording that its payload was prepared after
  push ~15:47 JST (104.858 ký tự, sha `0af8d809`, mergeable_state clean tại
  `003f1bb` lúc chuẩn bị; JSON 121.612 byte < trần 131.072 — còn 9.460 byte, bản giữ tại
  `.bak-prepost-20261123` — thư mục tồn tại, bản R201 lưu tại đó,
  byte-identical với `pr_comments/`),
  that it was NOT posted
  — live body still R140 (verified by this round's API read: description
  structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này, 0 U+FFFD, updated_at 2026-11-23T06:46:04Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~16:42 JST).
  The index now covers every block through `003f1bb`; R202's
  own 2 commits fold in at the next index update (R203), disclosed in the
  index itself. The R202 note was appended after the R201 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `003f1bb` · 593 · 2998 (with the fresh git derivation at `003f1bb`,
  the fresh API read ~16:42 JST, and the fresh merge-tree cross-check at
  `003f1bb`), plus the R201 paragraph in "Khối mới nhất" (369 ký tự,
  marked chưa đăng — live body is R140) and the R202 note. The stale index
  reference in "Về bản mô tả này" (head `5e5fbba`) is also fixed to
  `003f1bb`, and the title line is extended to R201 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R201 warning —
  applied with a margin): the R104 paragraph (694 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R201 paragraph was 369 ký tự, so
  the body is 104.854 ký tự — net −25 vs R201 despite the new R201
  paragraph, headroom 146 ký tự.
  Paragraph order: the R201 paragraph sits directly after R200
  (ascending full-paragraph order R166..R201), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R202 (owner tap) — the R140 body v2 now live
  is the base; only the R201 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r202_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R201 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R201 and R202 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R201 (62 compact lines R104–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.854 ký tự),
  a check that the R201 paragraph sits directly after R200
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R198/R199/R200 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R201 note clean).
  **PASS 24/24**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R202_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R201) with the full COVER
  SHA verified intact (definition + docstring, both
  `003f1bb22e3bd70e93177cf83e5b603a42df7f83` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `5e5fbba` references in the checker — the R201 cover value)
  before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.854 ký tự and the apply wrote on
  the first attempt at 104.854 ký tự with 146 ký tự of headroom; the idempotency re-run
  after apply reported already-applied (changed: 0) cleanly, exit 0 — the R200 lesson is
  fixed (the old guard crashed with an AssertionError on the title check instead).

## R202 robustness note — headroom now 146 chars

The R201 warning left 121 ký tự of headroom, so this round compacted
the R104 paragraph (694 ký tự → 239) before adding the new R201 paragraph
(369 ký tự). The body is now 104.854 ký tự — net −25 vs R201 — with
146 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R203 warning: headroom is 146 ký tự; the next round must collapse R103
(694 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R103 compaction alone frees ~454 ký tự, restoring comfortable headroom.
At the current net −25/round the margin holds with compaction; one full-paragraph compaction per round (~−454) keeps
the discipline sustainable (full paragraphs remaining R166..R201 = 36;
compact block R104–R165 = 62 lines).
Lesson this round: (1) the dry-run projection matched the apply exactly
(104.854 ký tự); measure, don't hand-count (same lesson as R186/R190/R195/R197/R198/R199/R200/R201).
(2) A blanket `sed` timestamp fix across a file can hit a historical row
that legitimately cites the same clock time on a previous day: the first
timestamp fix this round (16:45 → 16:42, for this round's own read time)
also rewrote the R180 row's "đọc API lượt R181 ~16:45 JST" — R181's own
read on 2026-11-22, not this round's — caught by reviewing the amend diff
(6 changed lines where 5 were expected) and restored before push; scope
timestamp edits to the lines this round owns, never a global replace.
(3) `issue_read get_comments` paginates at 30/page: the first page alone
(30 comments, latest `6819808977`) looks like a complete read but is not
— always fetch page 2 (4 more, latest `6862732081`) before stating the
34-comment total.

## Verification

- Merge-tree `003f1bb` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `c89b0ff4…`. Merge-tree at the R202
  content head `e50ba30` vs `f3db6b3`: exit 0, tree
  `352bf4d5…`.
- Live PR state: API read via MCP `call-read-tool` ~16:42 JST (read path
  healthy) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `003f1bb`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T06:46:04Z — bumped by the R201 push, body
  bytes unchanged); commits 593, changed_files 2998, additions 284536
  (API agrees with the fresh git derivation; the `deletions` key is absent
  in this API response — git shows 0 deletions); mergeable_state clean at
  `003f1bb` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — browser task
  no longer needed: still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R202 block (`003f1bb..e50ba30`) 3 paths / 0 violations
  (index + body v2 + R202 checker); cumulative at the R202 content
  commit `e50ba30` 2999 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `e50ba30`).
  Merge-tree at the R202 content head `e50ba30` vs `f3db6b3`: exit 0,
  tree `352bf4d5…`.
- Transient notes: this round's `git fetch` at ~16:40 JST succeeded
  first try. MCP `call-read-tool` worked for all reads this round (no
  stall, no rate-limit 403). The R201 payload's own head line recorded
  mergeable clean at `003f1bb` at its preparation; this round's API read
  confirms clean at the same head.
- Ceiling discipline: the R201 payload JSON measured 121.612 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.460 byte headroom). The projected R202 payload JSON is ~121,800 byte
  (measured exactly at payload build, after push). Body v2 is now 104.854
  ký tự (< 105.000) — 146 ký tự of headroom. R203 warning:
  headroom is now 146 ký tự; the next round must collapse R103 (694 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R202 body
v2 (R201 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r202.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R202 push (title
ending "+ R202", built by replacing the "+ R140" suffix — not appending;
body = body v2 R202 in repo, head line refreshed to head after R202 push).
This run started ~16:40 JST — WITHIN working hours (09:00–21:30 JST), so the
R202 payload is READY FOR PRESENTATION by the main flow (not held like R142/R164–R197). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R201 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200 and R201 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R202: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
