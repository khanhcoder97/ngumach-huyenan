# MEDIA-02 — PR #119 Body Restructure R200: delivery index + body v2 coverage to `cd6db28`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `cd6db28` (PR119 BODY RESTRUCTURE R199 report). Content commit: `01dd796`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R200 does

R199 left the disclosed gap: the delivery index covered 587 commits to
`389a85b`; R199's own 2 commits were to fold in at R200. The R199 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh browser read ~15:00 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, tail lines match). The R199 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, same as R199: the GitHub MCP read path was unavailable — `call-tool`
stalled twice with a service restart in the R199 round (the approval never returned in a
detached run), and the `gh` CLI needs auth it does not have (verified again this round:
`gh auth status` — not logged into any GitHub hosts). The live state was instead read
from the public web UI by a browser task (~15:00 JST, no sign-in, read-only). That read
CONFIRMED: issue #116 still 34 comments (counted 34 "khanhcoder97 commented", anchors to
34/34 after "Load more"); the last 3 comments are the CP4/PROLOGUE ACK `6832706291`
(2026-11-13 03:44 JST), the SCENE-CLIPS ACK `6833806995` (2026-11-13 04:30 JST), and the
folded CP5 + M-G CP10 ACK `6862732081` (2026-11-14 ~04:24 JST); PR #119 is Open
with head `cd6db28` (R199 report commit; previous commit in the pair is R199 content
`4513812`), 589 commits, 2992 files changed, +283,478, 11/11 checks OK at the head; the
description structure matches live R140 (PR title ends "+ R140", head inside the description
`78ccd85` · 471 · 2815, tail lines match). It could NOT read the exact live-body char
count/sha, the PR `updated_at`, or `mergeable_state` from the public web UI without sign-in.
So this round records those figures honestly as carried from the last API byte-exact read
(R198 round ~09:44 JST: 92,520 chars, sha `ddbe32ff`, updated_at 2026-11-22T23:50:59Z) and
records `mergeable_state` at `cd6db28` as UNVERIFIABLE via the public web UI — with checks
11/11 OK at the new head and the merge-tree cross-check (exit 0, 0 conflicts, tree
`36225e9f…`) as the evidence, and the last API-clean read at `280307b`. The body v2 head
line and the index milestone lines say exactly this; nothing here claims an API read
that did not happen.

Fresh derivation at `cd6db28` (~15:05 JST): `git rev-list --count
cf17178..cd6db28` = 589 commits, `git diff --name-only` = 2992 files,
`--shortstat` = 283478 insertions, 0 deletions. `git merge-tree
--write-tree` `cd6db28` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `36225e9f…`. No re-fetch was needed before applying: the run fetched at ~14:56 JST
(the run start) and the remote head was still `cd6db28`, integration still `f3db6b3` — no
intervening push; the browser read ~15:00 JST independently confirmed head `cd6db28`.

R200 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `cd6db28` (589 commits / 2992 files /
  283478 additions; the fresh git derivation at `cd6db28`, the fresh browser
  read ~15:00 JST, and the merge-tree cross-check at `cd6db28` are cited,
  with the honest mergeable limitation disclosed above;
  live body R140; delta `389a85b..cd6db28`: 5 paths, 500 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R199
  (`4513812`/`cd6db28`), recording that its payload was prepared after
  push ~14:52 JST (104.982 ký tự, sha `483b3a6a`, mergeable_state unstable tại
  `cd6db28` lúc chuẩn bị — lần clean gần nhất tại `280307b`; JSON 121.879 byte < trần 131.072 — còn 9.193 byte, bản giữ tại
  `.bak-prepost-20261123` — thư mục được R199 tạo mới vì trước đó không tồn tại trên đĩa),
  that it was NOT posted
  — live body still R140 (verified by this round's browser read: description
  structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; exact char count/sha carried from the R198 API
  byte-exact read, 92.520 ký tự, sha `ddbe32ff`) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; browser read ~15:00 JST, no sign-in).
  The index now covers every block through `cd6db28`; R200's
  own 2 commits fold in at the next index update (R201), disclosed in the
  index itself. The R200 note was appended after the R199 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **R198 .bak correction** (R199 finding, applied this round): the R198 index row claimed its
  payload backup at `.bak-prepost-20261123`, but that directory did NOT exist on disk when R199
  checked (only the payload JSON at `pr_comments/pr119_update_body_v2_r198.json`); R199 created
  the directory and saved the R199 copy there (verified on disk this round: the directory now
  exists and holds only `pr119_update_body_v2_r199.json`, 121.879 byte). The R198 row now carries
  a ĐÍNH CHÍNH R200 note stating exactly this. The same unverifiable claim also appears in rows
  R137–R197; those historical rows are left as-is (per the R199 instruction to fix the R198 row
  only — it is the round being folded in) and the fact is disclosed here, not hidden. The R199
  row's own `.bak` claim IS true (directory created by R199, copy saved there).
- **Row-convention verification** (now also asserted by the R200 checker, not only in this
  report): a table row's "cumulative N paths" is the diff path count at the AUTHORING round's
  content commit — R196 row 2984 == `41f9110` (R197 content), R197 row 2987 == `285ade4` (R198
  content), R198 row 2990 == `4513812` (R199 content), all re-derived from git this round.
  The R199 row therefore cites cumulative 2993 paths — the diff count at the R200 content commit
  `01dd796`, verified after the commit (not predicted blindly). No correction to any earlier row
  was needed.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `cd6db28` · 589 · 2992 (with the fresh git derivation at `cd6db28`,
  the fresh browser read ~15:00 JST, and the fresh merge-tree cross-check at
  `cd6db28`), plus the R199 paragraph in "Khối mới nhất" (369 ký tự,
  marked chưa đăng — live body is R140) and the R200 note. The stale index
  reference in "Về bản mô tả này" (head `389a85b`) is also fixed to
  `cd6db28`, and the title line is extended to R199 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R199 warning —
  applied with a margin): the R106 paragraph (694 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R199 paragraph was 369 ký tự, so
  the body is 104.897 ký tự — net −25 vs R199 despite the new R199
  paragraph, headroom 103 ký tự.
  Paragraph order: the R199 paragraph sits directly after R198
  (ascending full-paragraph order R166..R199), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R200 (owner tap) — the R140 body v2 now live
  is the base; only the R199 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r200_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R199 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R199 and R200 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R199 (60 compact lines R106–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.897 ký tự),
  a check that the R199 paragraph sits directly after R198
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R196/R197/R198 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R199 note clean).
  **PASS 24/24**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R200_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R199) with the full COVER
  SHA verified intact (definition + docstring, both
  `cd6db28ce3a4972472a4d4151c7cceb0b30a244f` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `389a85b` references in the checker — the R199 cover value)
  before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.897 ký tự and the apply wrote on
  the first attempt at 104.897 ký tự with 103 ký tự of headroom; the idempotency re-run
  after apply reported already-applied (changed: 0) cleanly, exit 0 — the R199 lesson is
  fixed (the old guard crashed with an AssertionError on the title check instead).

## R200 robustness note — headroom now 103 chars

The R199 warning left 78 ký tự of headroom, so this round compacted
the R106 paragraph (694 ký tự → 239) before adding the new R199 paragraph
(369 ký tự). The body is now 104.897 ký tự — net −25 vs R199 — with
103 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R201 warning: headroom is 103 ký tự; the next round must collapse R105
(694 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R105 compaction alone frees ~454 ký tự, restoring comfortable headroom.
At the current net −25/round the margin holds with compaction; one full-paragraph compaction per round (~−454) keeps
the discipline sustainable (full paragraphs remaining R166..R199 = 34;
compact block R106–R165 = 60 lines).
Lesson this round: (1) the dry-run projection matched the apply exactly
(104.897 ký tự); measure, don't hand-count (same lesson as R186/R190/R195/R197/R198/R199).
(2) The edit script's idempotency guard now returns changed: 0 cleanly on re-run instead of
crashing — the R199 lesson is fixed and verified this round. (3) A claim repeated across
many index rows (the `.bak` backup location in R137–R198) can be wrong in all of them at once
when the directory never existed — a single-row fix plus an honest disclosure beats silently
repeating the claim; the R199 row's claim is true because R199 created the directory.
(4) When the MCP read path stalls, the public-web browser read is a usable fallback for structure and
counts, but it cannot establish exact live-body bytes, updated_at, or mergeable_state
— record those as carried/unverifiable, never as freshly read.

## Verification

- Merge-tree `cd6db28` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `36225e9f…`. Merge-tree at the R200
  content head `01dd796` vs `f3db6b3`: exit 0, tree
  `eb458341…`.
- Live PR state: browser read of the public web UI ~15:00 JST (no sign-in; MCP
  `call-tool` stalled twice with a service restart in the R199 round, `gh` CLI needs auth) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `cd6db28`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match);
  exact figures carried from the R198 API byte-exact read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-22T23:50:59Z); checks 11/11 OK at `cd6db28`;
  mergeable_state at `cd6db28` NOT verifiable from the public web UI — last API-clean
  read at `280307b`. Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, R197 round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the public web UI — browser task
  (~15:00 JST, no sign-in): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R200 block (`cd6db28..01dd796`) 3 paths / 0 violations
  (index + body v2 + R200 checker); cumulative at the R200 content
  commit `01dd796` 2993 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `01dd796`).
  Merge-tree at the R200 content head `01dd796` vs `f3db6b3`: exit 0,
  tree `eb458341…`.
- Transient notes: this round's `git fetch` at ~14:56 JST succeeded
  first try. MCP `call-tool` stalled twice (service restart) in the R199 round — fell back to the
  browser read; no rate-limit 403 on any read this round. The R199 payload's own head line recorded mergeable
  unstable at `cd6db28` at its preparation (CI still running on the new
  head); this round's browser read shows checks 11/11 OK at the same head after CI
  finished — the payload's unstable wording was correct at its
  preparation time, not a defect.
- Ceiling discipline: the R199 payload JSON measured 121.879 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's browser read)
  vs the 131.072-byte transport ceiling
  (9.193 byte headroom). The projected R200 payload JSON is ~122,000 byte
  (measured exactly at payload build, after push). Body v2 is now 104.897
  ký tự (< 105.000) — 103 ký tự of headroom. R200 warning:
  headroom is now 103 ký tự; the next round must collapse R105 (694 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R200 body
v2 (R199 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r200.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R200 push (title
ending "+ R200", built by replacing the "+ R140" suffix — not appending;
body = body v2 R200 in repo, head line refreshed to head after R200 push).
This run started ~14:40 JST and finished ~15:20 JST — WITHIN working hours (09:00–21:30 JST), so the
R200 payload is READY FOR PRESENTATION by the main flow (not held like R142/R164–R197). Do not present the superseded R199 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198 and R199 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R200: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
