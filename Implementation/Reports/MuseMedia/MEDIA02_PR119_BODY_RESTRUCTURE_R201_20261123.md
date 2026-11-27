# MEDIA-02 — PR #119 Body Restructure R201: delivery index + body v2 coverage to `5e5fbba`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `5e5fbba` (PR119 BODY RESTRUCTURE R200 report). Content commit: `409c2f2`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R201 does

R200 left the disclosed gap: the delivery index covered 589 commits to
`cd6db28`; R200's own 2 commits were to fold in at R201. The R200 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API read ~15:42 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T06:07:15Z — bumped by the R200 push updating the PR head, body bytes
unchanged). The R200 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, improved this round: the GitHub MCP read path WORKED
(`call-read-tool`, no stall, no rate-limit 403) — `issue_read get_comments`
and `pull_request_read get` both returned cleanly ~15:42 JST, so every
live figure this round is a fresh API byte-exact read, not a browser
fallback and not carried from an earlier round: issue #116 34 comments,
PR #119 head `5e5fbba`, 591 commits / 2995 files / +284.019, mergeable_state
clean at `5e5fbba`, live body R140 92.520 ký tự sha `ddbe32ff`. (R199
stalled on `call-tool` and R200 fell back to the public-web browser read;
this round the read path is healthy again.)

Fresh derivation at `5e5fbba` (~15:42 JST): `git rev-list --count
cf17178..5e5fbba` = 591 commits, `git diff --name-only` = 2995 files,
`--shortstat` = 284019 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `5e5fbba` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `929a6fd5…`. No re-fetch was needed before applying: the run fetched at ~15:40 JST
(the run start) and the remote head was still `5e5fbba`, integration still `f3db6b3` — no
intervening push; the API read ~15:42 JST independently confirmed head `5e5fbba`.

R201 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `5e5fbba` (591 commits / 2995 files /
  284019 additions; the fresh git derivation at `5e5fbba`, the fresh API
  read ~15:42 JST, and the merge-tree cross-check at `5e5fbba` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `cd6db28..5e5fbba`: 5 paths, 553 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R200
  (`01dd796`/`5e5fbba`), recording that its payload was prepared after
  push ~15:08 JST (104.957 ký tự, sha `16c7bf7f`, mergeable_state tại
  `5e5fbba` chưa đọc được lúc chuẩn bị — MCP stall, trình duyệt chỉ xác minh
  tới head `cd6db28`; lần clean API gần nhất lúc đó tại `280307b`; JSON 121.812 byte < trần 131.072 — còn 9.260 byte, bản giữ tại
  `.bak-prepost-20261123` — thư mục tồn tại, bản R200 lưu tại đó,
  byte-identical với `pr_comments/`),
  that it was NOT posted
  — live body still R140 (verified by this round's API read: description
  structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này, 0 U+FFFD, updated_at 2026-11-23T06:07:15Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~15:42 JST).
  The index now covers every block through `5e5fbba`; R201's
  own 2 commits fold in at the next index update (R202), disclosed in the
  index itself. The R201 note was appended after the R200 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `5e5fbba` · 591 · 2995 (with the fresh git derivation at `5e5fbba`,
  the fresh API read ~15:42 JST, and the fresh merge-tree cross-check at
  `5e5fbba`), plus the R200 paragraph in "Khối mới nhất" (394 ký tự,
  marked chưa đăng — live body is R140) and the R201 note. The stale index
  reference in "Về bản mô tả này" (head `cd6db28`) is also fixed to
  `5e5fbba`, and the title line is extended to R200 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R200 warning —
  applied with a margin): the R105 paragraph (694 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R200 paragraph was 394 ký tự, so
  the body is 104.879 ký tự — net −18 vs R200 despite the new R200
  paragraph, headroom 121 ký tự.
  Paragraph order: the R200 paragraph sits directly after R199
  (ascending full-paragraph order R166..R200), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R201 (owner tap) — the R140 body v2 now live
  is the base; only the R200 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r201_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R200 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R200 and R201 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R200 (61 compact lines R105–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.879 ký tự),
  a check that the R200 paragraph sits directly after R199
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R197/R198/R199 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R200 note clean).
  **PASS 24/24**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R201_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R200) with the full COVER
  SHA verified intact (definition + docstring, both
  `5e5fbba53c948c7a0c8032c9ff8e4b1547bdac83` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `cd6db28` references in the checker — the R200 cover value)
  before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.879 ký tự and the apply wrote on
  the first attempt at 104.879 ký tự with 121 ký tự of headroom; the idempotency re-run
  after apply reported already-applied (changed: 0) cleanly, exit 0 — the R200 lesson is
  fixed (the old guard crashed with an AssertionError on the title check instead).

## R201 robustness note — headroom now 121 chars

The R200 warning left 103 ký tự of headroom, so this round compacted
the R105 paragraph (694 ký tự → 239) before adding the new R200 paragraph
(394 ký tự). The body is now 104.879 ký tự — net −18 vs R200 — with
121 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R202 warning: headroom is 121 ký tự; the next round must collapse R104
(694 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R104 compaction alone frees ~454 ký tự, restoring comfortable headroom.
At the current net −18/round the margin holds with compaction; one full-paragraph compaction per round (~−454) keeps
the discipline sustainable (full paragraphs remaining R166..R200 = 35;
compact block R105–R165 = 61 lines).
Lesson this round: (1) the dry-run projection matched the apply exactly
(104.879 ký tự); measure, don't hand-count (same lesson as R186/R190/R195/R197/R198/R199/R200).
(2) When the MCP read path works, use it: this round's live figures are
fresh API byte-exact reads (body sha `ddbe32ff`, mergeable_state clean at
`5e5fbba`), not browser-fallback structure or carried figures — and the
R200 payload's "mergeable chưa đọc được" wording is now resolved by a
clean API read at the same head, confirming it was a read-path limit at
preparation time, not a PR-state defect.

## Đính chính — giờ kết thúc thực của R200

The pushed R200 report says the run "finished ~15:20 JST". That was an
estimate written into the report before the run ended. The actual finish
was ~15:12 JST (payload rebuilt with the correct time ~15:08 JST, queue
and memory entries written after the push). The R200 report file itself is
pushed history and is NOT edited; the correction is recorded here and in
this round's queue/memory entries. Lesson: write the finish time only
after the run ends, or mark an estimate as an estimate.

## Verification

- Merge-tree `5e5fbba` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `929a6fd5…`. Merge-tree at the R201
  content head `409c2f2` vs `f3db6b3`: exit 0, tree
  `ed847b69…`.
- Live PR state: API read via MCP `call-read-tool` ~15:42 JST (read path
  healthy again after the R199 stall) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `5e5fbba`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T06:07:15Z — bumped by the R200 push, body
  bytes unchanged); commits 591, changed_files 2995, additions 284019
  (API agrees with the fresh git derivation); mergeable_state clean at
  `5e5fbba` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — browser task
  no longer needed: still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R201 block (`5e5fbba..409c2f2`) 3 paths / 0 violations
  (index + body v2 + R201 checker); cumulative at the R201 content
  commit `409c2f2` 2996 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `409c2f2`).
  Merge-tree at the R201 content head `409c2f2` vs `f3db6b3`: exit 0,
  tree `ed847b69…`.
- Transient notes: this round's `git fetch` at ~15:40 JST succeeded
  first try. MCP `call-read-tool` worked for both reads this round (no
  stall, no rate-limit 403). The R200 payload's own head line recorded
  mergeable "chưa đọc được" at `5e5fbba` at its preparation (MCP stall;
  browser could only verify to `cd6db28`); this round's API read shows
  mergeable_state clean at the same head — the payload's wording was
  correct at its preparation time, not a defect.
- Ceiling discipline: the R200 payload JSON measured 121.812 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.260 byte headroom). The projected R201 payload JSON is ~121,900 byte
  (measured exactly at payload build, after push). Body v2 is now 104.879
  ký tự (< 105.000) — 121 ký tự of headroom. R202 warning:
  headroom is now 121 ký tự; the next round must collapse R104 (694 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R201 body
v2 (R200 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r201.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R201 push (title
ending "+ R201", built by replacing the "+ R140" suffix — not appending;
body = body v2 R201 in repo, head line refreshed to head after R201 push).
This run started ~15:40 JST — WITHIN working hours (09:00–21:30 JST), so the
R201 payload is READY FOR PRESENTATION by the main flow (not held like R142/R164–R197). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R200 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199 and R200 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R201: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
