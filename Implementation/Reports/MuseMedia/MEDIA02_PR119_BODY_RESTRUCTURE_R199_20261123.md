# MEDIA-02 — PR #119 Body Restructure R199: delivery index + body v2 coverage to `389a85b`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `389a85b` (PR119 BODY RESTRUCTURE R198 report). Content commit: `4513812`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R199 does

R198 left the disclosed gap: the delivery index covered 585 commits to
`280307b`; R198's own 2 commits were to fold in at R199. The R198 body v2 was NOT posted — the
main-flow handoff at ~09:52 JST ended `nothing_to_do`, so the R198 widget/payload was never
presented to the owner. This round's fresh live read shows the live PR title still ends
"+ R140" and the live body is still R140. The R198 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method change this round: the GitHub MCP read path was unavailable — `call-tool`
for `issue_read` stalled twice with a service restart (the approval never returned in this
detached run), and the `gh` CLI needs auth it does not have. The live state was instead read
from the public web UI by a browser task (~14:47 JST, no sign-in, read-only). That read
CONFIRMED: issue #116 still 34 comments (counted 34 "khanhcoder97 commented", author labels
to 34/34, no "remaining items"); the last 3 comments are the CP4/PROLOGUE ACK, the SCENE-CLIPS
ACK, and the folded CP5 + M-G CP10 ACK `6862732081` (2026-11-14 ~04:24 JST); PR #119 is Open
with head `389a85b` (R198 report commit; previous commit in the pair is R198 content
`285ade4`), 587 commits, 2989 files changed, +282,989, 11/11 checks OK at the head; the
description structure matches live R140 (PR title ends "+ R140", head inside the description
`78ccd85` · 471 · 2815, tail lines match). It could NOT read the exact live-body char
count/sha, the PR `updated_at`, or `mergeable_state` from the public web UI without sign-in.
So this round records those figures honestly as carried from the last API byte-exact read
(R198 round ~09:44 JST: 92,520 chars, sha `ddbe32ff`, updated_at 2026-11-22T23:50:59Z) and
records `mergeable_state` at `389a85b` as UNVERIFIABLE via the public web UI — with checks
11/11 OK at the new head and the merge-tree cross-check (exit 0, 0 conflicts, tree
`6cc7da83…`) as the evidence, and the last API-clean read at `280307b`. The body v2 head
line and the index milestone lines say exactly this; nothing here claims an API read
that did not happen.

Fresh derivation at `389a85b` (~14:50 JST): `git rev-list --count
cf17178..389a85b` = 587 commits, `git diff --name-only` = 2989 files,
`--shortstat` = 282989 insertions, 0 deletions. `git merge-tree
--write-tree` `389a85b` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `6cc7da83…`. This round re-fetched at ~14:50 JST before applying (the
run stretched from its 10:40 JST start across the browser handoff at ~14:47 JST):
remote head was still `389a85b`, integration still `f3db6b3` — no intervening push.

R199 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `389a85b` (587 commits / 2989 files /
  282989 additions; the fresh git derivation at `389a85b`, the fresh browser
  read ~14:47 JST, and the merge-tree cross-check at `389a85b` are cited,
  with the honest mergeable limitation disclosed above;
  live body R140; delta `280307b..389a85b`: 5 paths, 467 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R198
  (`285ade4`/`389a85b`), recording that its payload was prepared after
  push ~09:50 JST (104.922 ký tự, sha `fc01e3ce`, mergeable_state unstable tại
  `389a85b` lúc chuẩn bị, lần clean gần nhất tại `280307b`; JSON 121.842 byte < trần 131.072 — còn 9.230 byte, bản giữ tại
  `.bak-prepost-20261123`), that it was NOT presented by the main flow
  (handoff ~09:52 JST ended nothing_to_do), that it was NOT posted
  — live body still R140 (verified by this round's browser read: description
  structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; exact char count/sha carried from the R198 API
  byte-exact read, 92.520 ký tự, sha `ddbe32ff`) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; browser read ~14:47 JST, no sign-in).
  The index now covers every block through `389a85b`; R199's
  own 2 commits fold in at the next index update (R200), disclosed in the
  index itself. The R199 note was appended after the R198 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Row-convention verification** (done this round before writing the
  R198 row): a table row's "cumulative N paths" is the diff path count at
  the AUTHORING round's content commit — R195 row 2981 == `218f0fa`
  (R196 content), R196 row 2984 == `41f9110` (R197 content), R197 row
  2987 == `285ade4` (R198 content), all re-derived from git this round.
  The R198 row therefore cites cumulative 2990 paths — the diff count at
  the R199 content commit `4513812`, verified after the commit (not
  predicted blindly). No correction to any earlier row was needed.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `389a85b` · 587 · 2989 (with the fresh git derivation at `389a85b`,
  the fresh browser read ~14:47 JST, and the fresh merge-tree cross-check at
  `389a85b`), plus the R198 paragraph in "Khối mới nhất" (404 ký tự,
  marked chưa đăng — live body is R140) and the R199 note. The stale index
  reference in "Về bản mô tả này" (head `280307b`) is also fixed to
  `389a85b`, and the title line is extended to R198 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R198 warning —
  applied with a margin): the R107 paragraph (694 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R198 paragraph was 404 ký tự, so
  the body is 104.922 ký tự — net −24 vs R198 despite the new R198
  paragraph, headroom 78 ký tự.
  Paragraph order: the R198 paragraph sits directly after R197
  (ascending full-paragraph order R166..R198), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R199 (owner tap) — the R140 body v2 now live
  is the base; only the R198 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r199_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R198 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R198 and R199 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R198 (59 compact lines R107–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.922 ký tự),
  a check that the R198 paragraph sits directly after R197
  (ascending full-paragraph order), and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R198 note clean).
  **PASS 20/20**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R199_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R198) with the full COVER
  SHA verified intact (definition + docstring, both
  `389a85ba6835d55fd9b44e8436faf639138d833e` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `280307b`/`f7db540a`/`eb54d4d` references in the checker — the R198 values)
  before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.922 ký tự and the apply wrote on
  the first attempt at 104.922 ký tự with 78 ký tự of headroom; the idempotency re-run
  crashed on the title guard instead of reporting already-applied (changed: 0) — see
  Lesson below; no file was touched by the failed re-run (asserts run before any write).

## R199 robustness note — headroom now 78 chars

The R198 warning left 54 ký tự of headroom, so this round compacted
the R107 paragraph (694 ký tự → 239) before adding the new R198 paragraph
(404 ký tự). The body is now 104.922 ký tự — net −24 vs R198 — with
78 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R200 warning: headroom is 78 ký tự; the next round must collapse R106
(694 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R106 compaction alone frees ~454 ký tự, restoring comfortable headroom.
At the current net −24/round the margin holds with compaction; one full-paragraph compaction per round (~−454) keeps
the discipline sustainable (full paragraphs remaining R166..R198 = 33;
compact block R107–R165 = 59 lines).
Lesson this round: (1) the dry-run projection matched the apply exactly
(104.922 ký tự); measure, don't hand-count (same lesson as R186/R190/R195/R197/R198).
(2) The edit script's idempotency guard is incomplete: the re-run after apply crashed
with an AssertionError on the title check instead of reporting already-applied
(changed: 0). The crash is safe — every guard asserts before any write, and the
working tree showed only the 2 intended modifications — but the next round should
make the guard return changed: 0 cleanly instead of crashing. (3) When the MCP read
path stalls, the public-web browser read is a usable fallback for structure and
counts, but it cannot establish exact live-body bytes, updated_at, or mergeable_state
— record those as carried/unverifiable, never as freshly read.

## Verification

- Merge-tree `389a85b` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `6cc7da83…`. Merge-tree at the R199
  content head `4513812` vs `f3db6b3`: exit 0, tree
  `64b77aa9…`.
- Live PR state: browser read of the public web UI ~14:47 JST (no sign-in; MCP
  `call-tool` stalled twice with a service restart, `gh` CLI needs auth) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `389a85b`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match);
  exact figures carried from the R198 API byte-exact read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-22T23:50:59Z); checks 11/11 OK at `389a85b`;
  mergeable_state at `389a85b` NOT verifiable from the public web UI — last API-clean
  read at `280307b`. Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, R197 round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the public web UI — browser task
  (~14:47 JST, no sign-in): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R199 block (`389a85b..4513812`) 3 paths / 0 violations
  (index + body v2 + R199 checker); cumulative at the R199 content
  commit `4513812` 2990 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `4513812`).
  Merge-tree at the R199 content head `4513812` vs `f3db6b3`: exit 0,
  tree `64b77aa9…`.
- Transient notes: one proxy reset on the first `ls-remote` of the day was retried
  successfully in the R194 round; this round's `git fetch` at ~14:50 JST succeeded
  first try. MCP `call-tool` stalled twice (service restart) — fell back to the
  browser read; no rate-limit 403 on any read this round. The R198 payload's own head line recorded mergeable
  unstable at `389a85b` at its preparation (CI still running on the new
  head); this round's browser read shows checks 11/11 OK at the same head after CI
  finished — the payload's unstable wording was correct at its
  preparation time, not a defect.
- Ceiling discipline: the R198 payload JSON measured 121.842 byte
  (as-prepared; NOT presented — main-flow handoff ~09:52 JST ended nothing_to_do, so no
  main-flow refresh changed it) vs the 131.072-byte transport ceiling
  (9.230 byte headroom). The projected R199 payload JSON is ~122,300 byte
  (measured exactly at payload build, after push). Body v2 is now 104.922
  ký tự (< 105.000) — 78 ký tự of headroom. R199 warning:
  headroom is now 78 ký tự; the next round must collapse R106 (694 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R199 body
v2 (R198 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r199.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R199 push (title
ending "+ R199", built by replacing the "+ R140" suffix — not appending;
body = body v2 R199 in repo, head line refreshed to head after R199 push).
This run started ~10:40 JST and finished ~14:52 JST — WITHIN working hours (09:00–21:30 JST), so the
R199 payload is READY FOR PRESENTATION by the main flow (not held like R142/R164–R197). Do not present the superseded R198 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197 and R198 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R199: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
