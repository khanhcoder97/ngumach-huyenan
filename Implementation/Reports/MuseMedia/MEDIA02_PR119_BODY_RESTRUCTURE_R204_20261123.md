# MEDIA-02 — PR #119 Body Restructure R204: delivery index + body v2 coverage to `1cb0f67`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `1cb0f67` (PR119 BODY RESTRUCTURE R203 report). Content commit: `818f027`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R204 does

R203 left the disclosed gap: the delivery index covered 595 commits to
`bda1fd7`; R203's own 2 commits were to fold in at R204. The R203 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API read ~18:42 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T08:48:03Z — bumped by the R203 push updating the PR head, body bytes
unchanged). The R203 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub MCP read path WORKED
(`call-read-tool`, no stall, no rate-limit 403) — `issue_read get_comments`
(both pages: 30 + 4) and `pull_request_read get` both returned cleanly
~18:42 JST, so every live figure this round is a fresh API byte-exact read,
not a browser fallback and not carried from an earlier round: issue #116 34 comments,
PR #119 head `1cb0f67`, 597 commits / 3004 files / +285,576, mergeable_state
clean at `1cb0f67`, live body R140 92.520 ký tự sha `ddbe32ff`.
Parameter names (kept from R202/R203): `pull_request_read` takes
`pullNumber`, not `pull_number`; `issue_read` takes `issue_number`.
Pagination note (kept from R202): `issue_read get_comments` paginates at 30 comments per page — the
first page alone returns 30 comments (latest `6819808977`) and looks
complete, but is not; page 2 returns the remaining 4 (`6831053345`,
`6832706291`, `6833806995`, `6862732081`), for the 34 total. Always fetch
page 2 before stating the comment total.

Fresh derivation at `1cb0f67` (~18:42 JST): `git rev-list --count
cf17178..1cb0f67` = 597 commits, `git diff --name-only` = 3004 files,
`--shortstat` = 285576 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `1cb0f67` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `3ee4d1ad…`. No re-fetch was needed before applying: the run fetched at ~18:40 JST
(the run start) and the remote head was still `1cb0f67`, integration still `f3db6b3` — no
intervening push; the API read ~18:42 JST independently confirmed head `1cb0f67`.

R204 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `1cb0f67` (597 commits / 3004 files /
  285576 additions; the fresh git derivation at `1cb0f67`, the fresh API
  read ~18:42 JST, and the merge-tree cross-check at `1cb0f67` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `bda1fd7..1cb0f67`: 5 paths, 536 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R203
  (`549b8b0`/`1cb0f67`), recording that its payload was prepared after
  push ~17:48 JST (104.873 ký tự, sha `bdbdbae5`, mergeable unstable tại
  `1cb0f67` lúc chuẩn bị — lần clean gần nhất tại `bda1fd7`; JSON 121.531 byte < trần 131.072 — còn 9.541 byte, bản giữ tại
  `.bak-prepost-20261123` — thư mục tồn tại, bản R203 lưu tại đó,
  byte-identical với `pr_comments/` — sha256 `ad64c9ec…` cả hai),
  that it was NOT posted
  — live body still R140 (verified by this round's API read: description
  structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này, 0 U+FFFD, updated_at 2026-11-23T08:48:03Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~18:42 JST).
  The index now covers every block through `1cb0f67`; R204's
  own 2 commits fold in at the next index update (R205), disclosed in the
  index itself. The R204 note was appended after the R203 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `1cb0f67` · 597 · 3004 (with the fresh git derivation at `1cb0f67`,
  the fresh API read ~18:42 JST, and the fresh merge-tree cross-check at
  `1cb0f67`), plus the R203 paragraph in "Khối mới nhất" (407 ký tự,
  marked chưa đăng — live body is R140) and the R204 note. The stale index
  reference in "Về bản mô tả này" (head `bda1fd7`) is also fixed to
  `1cb0f67`, and the title line is extended to R203 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R203 warning —
  applied with a margin): the R102 paragraph (694 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R203 paragraph was 407 ký tự, so
  the body is 104.838 ký tự — net +13 vs R203 despite the new R203
  paragraph, headroom 162 ký tự.
  Paragraph order: the R203 paragraph sits directly after R202
  (ascending full-paragraph order R166..R203), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R204 (owner tap) — the R140 body v2 now live
  is the base; only the R203 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r204_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R203 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R203 and R204 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R203 (64 compact lines R102–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.838 ký tự),
  a check that the R203 paragraph sits directly after R202
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R200/R201/R202 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R203 note clean).
  **PASS 24/24**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R204_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R203) with the full COVER
  SHA verified intact (definition + docstring, both
  `1cb0f67a227723eaee33866b6066932ae99083ad` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `bda1fd7` references in the checker — the R203 cover value)
  before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.838 ký tự and the apply wrote on
  the first attempt at 104.838 ký tự with 162 ký tự of headroom; the idempotency re-run
  after apply reported already-applied changed: 0 — the R203 lesson is
  FIXED and verified this round (the guard now accepts the
  already-applied state instead of crashing on its OLD-state pre-condition
  assert).

## R204 robustness note — headroom now 162 chars

The R203 warning left 175 ký tự of headroom, so this round compacted
the R102 paragraph (694 ký tự → 239) before adding the new R203 paragraph
(407 ký tự). The body is now 104.838 ký tự — net +13 vs R203 — with
162 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R205 warning: headroom is 162 ký tự; the next round must collapse R101
(694 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R101 compaction alone frees ~454 ký tự, restoring comfortable headroom.
At the current net +13/round the margin holds with compaction; one full-paragraph compaction per round (~−454) keeps
the discipline sustainable (full paragraphs remaining R166..R203 = 38;
compact block R102–R165 = 64 lines).
Lesson this round: (1) the dry-run projection matched the apply exactly
(104.838 ký tự); measure, don't hand-count (same lesson as R186/R190/R195/R197/R198/R199/R200/R201/R202/R203).
(2) `pull_request_read` takes `pullNumber`, not `pull_number` — the
first call failed fast with "missing required parameter: pullNumber" in R203;
`issue_read` takes `issue_number`. Use the right parameter name per
tool; a fast failure is cheap, a wrong guess retried is not.
(3) An edit script's idempotency re-run must assert the NEW state as
acceptable, not only the OLD state — otherwise the re-run crashes on
its own pre-condition after a successful apply (R203 lesson — FIXED this
round: re-run reports already-applied changed: 0, verified).

## Verification

- Merge-tree `1cb0f67` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `3ee4d1ad…`. Merge-tree at the R204
  content head `818f027` vs `f3db6b3`: exit 0, tree
  `8e7d9c06…`.
- Live PR state: API read via MCP `call-read-tool` ~18:42 JST (read path
  healthy) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `1cb0f67`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T08:48:03Z — bumped by the R203 push updating the PR head, body
  bytes unchanged); commits 597, changed_files 3004, additions 285576
  (API agrees with the fresh git derivation; the `deletions` key is absent
  in this API response — git shows 0 deletions; the raw API payload also
  returns `mergeable: null` — mergeable_state clean is the operative
  field); mergeable_state clean at
  `1cb0f67` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — browser task
  no longer needed: still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R204 block (`1cb0f67..818f027`) 3 paths / 0 violations
  (index + body v2 + R204 checker); cumulative at the R204 content
  commit `818f027` 3005 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `818f027`).
  Merge-tree at the R204 content head `818f027` vs `f3db6b3`: exit 0,
  tree `8e7d9c06…`.
- Transient notes: this round's `git fetch` at ~18:40 JST succeeded
  first try. MCP `call-read-tool` worked for all reads this round (no
  stall, no rate-limit 403). The R203 payload's own head line recorded
  mergeable clean at `bda1fd7` at its preparation and unstable at
  `1cb0f67`; this round's API read confirms clean at `1cb0f67`.
- Ceiling discipline: the R203 payload JSON measured 121.531 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.541 byte headroom). The projected R204 payload JSON is ~121,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.838
  ký tự (< 105.000) — 162 ký tự of headroom. R204 warning:
  headroom is now 162 ký tự; the next round must collapse R101 (694 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R204 body
v2 (R203 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r204.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R204 push (title
ending "+ R204", built by replacing the "+ R140" suffix — not appending;
body = body v2 R204 in repo, head line refreshed to head after R204 push).
This run started ~18:40 JST — WITHIN working hours (09:00–21:30 JST), so the
R204 payload is READY FOR PRESENTATION by the main flow (not held like R142/R164–R197). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R203 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202 and R203 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R204: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
