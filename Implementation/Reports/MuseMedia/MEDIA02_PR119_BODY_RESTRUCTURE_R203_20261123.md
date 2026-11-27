# MEDIA-02 — PR #119 Body Restructure R203: delivery index + body v2 coverage to `bda1fd7`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `bda1fd7` (PR119 BODY RESTRUCTURE R202 report). Content commit: `549b8b0`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R203 does

R202 left the disclosed gap: the delivery index covered 593 commits to
`003f1bb`; R202's own 2 commits were to fold in at R203. The R202 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API read ~17:42 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T07:47:21Z — bumped by the R202 push updating the PR head, body bytes
unchanged). The R202 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub MCP read path WORKED
(`call-read-tool`, no stall, no rate-limit 403) — `issue_read get_comments`
(both pages: 30 + 4) and `pull_request_read get` both returned cleanly
~17:42 JST, so every live figure this round is a fresh API byte-exact read,
not a browser fallback and not carried from an earlier round: issue #116 34 comments,
PR #119 head `bda1fd7`, 595 commits / 3001 files / +285,051, mergeable_state
clean at `bda1fd7`, live body R140 92.520 ký tự sha `ddbe32ff`.
One recovery note: the first `pull_request_read` call failed fast with
"missing required parameter: pullNumber" — the tool takes `pullNumber`,
not `pull_number` (the `issue_read` calls accept `issue_number`); the
retry with `pullNumber` returned cleanly. Pagination note (kept from
R202): `issue_read get_comments` paginates at 30 comments per page — the
first page alone returns 30 comments (latest `6819808977`) and looks
complete, but is not; page 2 returns the remaining 4 (`6831053345`,
`6832706291`, `6833806995`, `6862732081`), for the 34 total. Always fetch
page 2 before stating the comment total.

Fresh derivation at `bda1fd7` (~17:42 JST): `git rev-list --count
cf17178..bda1fd7` = 595 commits, `git diff --name-only` = 3001 files,
`--shortstat` = 285051 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `bda1fd7` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `a873b01f…`. No re-fetch was needed before applying: the run fetched at ~17:40 JST
(the run start) and the remote head was still `bda1fd7`, integration still `f3db6b3` — no
intervening push; the API read ~17:42 JST independently confirmed head `bda1fd7`.

R203 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `bda1fd7` (595 commits / 3001 files /
  285051 additions; the fresh git derivation at `bda1fd7`, the fresh API
  read ~17:42 JST, and the merge-tree cross-check at `bda1fd7` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `003f1bb..bda1fd7`: 5 paths, 526 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R202
  (`e50ba30`/`bda1fd7`), recording that its payload was prepared after
  push ~16:47 JST (104.902 ký tự, sha `2b542365`, mergeable_state clean tại
  `bda1fd7` lúc chuẩn bị; JSON 121.614 byte < trần 131.072 — còn 9.458 byte, bản giữ tại
  `.bak-prepost-20261123` — thư mục tồn tại, bản R202 lưu tại đó,
  byte-identical với `pr_comments/` — sha256 `a079db52…` cả hai),
  that it was NOT posted
  — live body still R140 (verified by this round's API read: description
  structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này, 0 U+FFFD, updated_at 2026-11-23T07:47:21Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~17:42 JST).
  The index now covers every block through `bda1fd7`; R203's
  own 2 commits fold in at the next index update (R204), disclosed in the
  index itself. The R203 note was appended after the R202 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `bda1fd7` · 595 · 3001 (with the fresh git derivation at `bda1fd7`,
  the fresh API read ~17:42 JST, and the fresh merge-tree cross-check at
  `bda1fd7`), plus the R202 paragraph in "Khối mới nhất" (369 ký tự,
  marked chưa đăng — live body is R140) and the R203 note. The stale index
  reference in "Về bản mô tả này" (head `003f1bb`) is also fixed to
  `bda1fd7`, and the title line is extended to R202 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R202 warning —
  applied with a margin): the R103 paragraph (694 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R202 paragraph was 369 ký tự, so
  the body is 104.825 ký tự — net −29 vs R202 despite the new R202
  paragraph, headroom 175 ký tự.
  Paragraph order: the R202 paragraph sits directly after R201
  (ascending full-paragraph order R166..R202), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R203 (owner tap) — the R140 body v2 now live
  is the base; only the R202 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r203_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R202 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R202 and R203 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R202 (63 compact lines R103–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.825 ký tự),
  a check that the R202 paragraph sits directly after R201
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R199/R200/R201 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R202 note clean).
  **PASS 24/24**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R203_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R202) with the full COVER
  SHA verified intact (definition + docstring, both
  `bda1fd702f6a1284bc5ee0be761de4c020c014fc` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `003f1bb` references in the checker — the R202 cover value)
  before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.825 ký tự and the apply wrote on
  the first attempt at 104.825 ký tự with 175 ký tự of headroom; the idempotency re-run
  after apply failed loudly on its own pre-condition assert (it expects
  the OLD head `003f1bb` in the index header, already replaced by the
  apply) instead of reporting already-applied — the apply itself was
  clean on the first attempt and the files were re-verified after
  (body 104.825 ký tự, checker 24/24); the re-run guard needs its
  asserts relaxed to accept the already-applied state (R204 lesson —
  same class as the R200 guard crash, but on the re-run path only,
  not on the apply path).

## R203 robustness note — headroom now 175 chars

The R202 warning left 146 ký tự of headroom, so this round compacted
the R103 paragraph (694 ký tự → 239) before adding the new R202 paragraph
(369 ký tự). The body is now 104.825 ký tự — net −29 vs R202 — with
175 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R204 warning: headroom is 175 ký tự; the next round must collapse R102
(694 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R102 compaction alone frees ~454 ký tự, restoring comfortable headroom.
At the current net −29/round the margin holds with compaction; one full-paragraph compaction per round (~−454) keeps
the discipline sustainable (full paragraphs remaining R166..R202 = 37;
compact block R103–R165 = 63 lines).
Lesson this round: (1) the dry-run projection matched the apply exactly
(104.825 ký tự); measure, don't hand-count (same lesson as R186/R190/R195/R197/R198/R199/R200/R201/R202).
(2) `pull_request_read` takes `pullNumber`, not `pull_number` — the
first call failed fast with "missing required parameter: pullNumber";
`issue_read` takes `issue_number`. Use the right parameter name per
tool; a fast failure is cheap, a wrong guess retried is not.
(3) An edit script's idempotency re-run must assert the NEW state as
acceptable, not only the OLD state — otherwise the re-run crashes on
its own pre-condition after a successful apply (see the checker
paragraph above).

## Verification

- Merge-tree `bda1fd7` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `a873b01f…`. Merge-tree at the R203
  content head `549b8b0` vs `f3db6b3`: exit 0, tree
  `2e7ded42…`.
- Live PR state: API read via MCP `call-read-tool` ~17:42 JST (read path
  healthy) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `bda1fd7`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T07:47:21Z — bumped by the R202 push, body
  bytes unchanged); commits 595, changed_files 3001, additions 285051
  (API agrees with the fresh git derivation; the `deletions` key is absent
  in this API response — git shows 0 deletions; the raw API payload also
  returns `mergeable: null` — mergeable_state clean is the operative
  field); mergeable_state clean at
  `bda1fd7` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — browser task
  no longer needed: still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R203 block (`bda1fd7..549b8b0`) 3 paths / 0 violations
  (index + body v2 + R203 checker); cumulative at the R203 content
  commit `549b8b0` 3002 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `549b8b0`).
  Merge-tree at the R203 content head `549b8b0` vs `f3db6b3`: exit 0,
  tree `2e7ded42…`.
- Transient notes: this round's `git fetch` at ~17:40 JST succeeded
  first try. MCP `call-read-tool` worked for all reads this round (no
  stall, no rate-limit 403) except the one fast parameter-name failure
  above, recovered by retry. The R202 payload's own head line recorded
  mergeable clean at `bda1fd7` at its preparation; this round's API read
  confirms clean at the same head.
- Ceiling discipline: the R202 payload JSON measured 121.614 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.458 byte headroom). The projected R203 payload JSON is ~121,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.825
  ký tự (< 105.000) — 175 ký tự of headroom. R204 warning:
  headroom is now 175 ký tự; the next round must collapse R102 (694 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R203 body
v2 (R202 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r203.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R203 push (title
ending "+ R203", built by replacing the "+ R140" suffix — not appending;
body = body v2 R203 in repo, head line refreshed to head after R203 push).
This run started ~17:40 JST — WITHIN working hours (09:00–21:30 JST), so the
R203 payload is READY FOR PRESENTATION by the main flow (not held like R142/R164–R197). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R202 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201 and R202 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R203: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
