# MEDIA-02 — PR #119 Body Restructure R198: delivery index + body v2 coverage to `280307b`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `280307b` (PR119 BODY RESTRUCTURE R197 report). Content commit: `285ade4`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R198 does

R197 left the disclosed gap: the delivery index covered 583 commits to
`eb54d4d`; R197's own 2 commits were to fold in at R198. The R197 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~09:44 JST; the FIRST read carried the
R175/R182-style read-path artifact — 92.521 ký tự, sha `ced29e00`, 2 U+FFFD — and the immediate
re-read was byte-exact: 92.520 ký tự, 0 U+FFFD, sha `ddbe32ff`) show the live PR title ends
"+ R140", head `280307b`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-22T23:50:59Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R197 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~09:44 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `280307b` (~09:44 JST): `git rev-list --count
cf17178..280307b` = 585 commits, `git diff --name-only` = 2986 files,
`--shortstat` = 282533 insertions, 0 deletions. `git merge-tree
--write-tree` `280307b` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `f7db540a…`. Like R197, this round DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `280307b` (CI finished since the R197 push at ~08:51 JST; the R197 payload's own head line had
recorded mergeable unstable at preparation time, when CI was still running on the new head — see Transient notes).

R198 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `280307b` (585 commits / 2986 files /
  282533 additions; the fresh git derivation at `280307b`, the fresh API
  read ~09:44 JST, and the merge-tree cross-check at `280307b` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `eb54d4d..280307b`: 5 paths, 509 insertions, 9
  deletions); one row appended — PR119 BODY RESTRUCTURE R197
  (`41f9110`/`280307b`), recording that its payload was prepared after
  push ~08:51 JST (104.920 ký tự, sha `d7822f59`, mergeable_state unstable tại
  `280307b` lúc chuẩn bị, lần clean gần nhất tại `eb54d4d`; JSON 121.892 byte < trần 131.072 — còn 9.180 byte, bản giữ tại
  `.bak-prepost-20261123`), that it was NOT refreshed by the main flow
  (cmp with its `.bak` byte-identical this round: payload sha `d7822f59`,
  104.920 ký tự), that it was NOT posted
  — live body still R140 (verified by this round's API read: first read carried the 2-U+FFFD artifact,
  92.521 ký tự sha `ced29e00`; immediate re-read byte-exact, 92.520 ký tự, sha
  `ddbe32ff`, 0 U+FFFD) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; connector MCP get_comments page 1,
  perPage 100). The index now covers every block through `280307b`; R198's
  own 2 commits fold in at the next index update (R199), disclosed in the
  index itself. The R198 note was appended after the R197 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Row-convention verification** (done this round before writing the
  R197 row): a table row's "cumulative N paths" is the diff path count at
  the AUTHORING round's content commit — R194 row 2978 == `6b67985`
  (R195 content), R195 row 2981 == `218f0fa` (R196 content), R196 row
  2984 == `41f9110` (R197 content), all re-derived from git this round.
  The R197 row therefore cites cumulative 2987 paths — the diff count at
  the R198 content commit `285ade4`, verified after the commit (not
  predicted blindly). No correction to any earlier row was needed.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `280307b` · 585 · 2986 (with the fresh git derivation at `280307b`,
  the fresh API read ~09:44 JST, and the fresh merge-tree cross-check at
  `280307b`), plus the R197 paragraph in "Khối mới nhất" (396 ký tự,
  marked chưa đăng — live body is R140) and the R198 note. The stale index
  reference in "Về bản mô tả này" (head `eb54d4d`) is also fixed to
  `280307b`, and the title line is extended to R197 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R197 warning —
  applied with a margin): the R108 paragraph (694 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R197 paragraph was 396 ký tự, so
  the body is 104.946 ký tự — net +2 vs R197 despite the new R197
  paragraph, headroom 54 ký tự.
  Paragraph order: the R197 paragraph sits directly after R196
  (ascending full-paragraph order R166..R197), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R198 (owner tap) — the R140 body v2 now live
  is the base; only the R197 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r198_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R197 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R197 and R198 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R197 (58 compact lines R108–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.946 ký tự),
  a check that the R197 paragraph sits directly after R196
  (ascending full-paragraph order), and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R197 note clean).
  **PASS 20/20**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R198_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R197) with the full COVER
  SHA verified intact (definition + docstring, both
  `280307b27b02493d41b13ce7a6f497f270edcfb2` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `eb54d4d`/`131a24b0` references in the checker — the R197 values)
  before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.946 ký tự and the apply wrote on
  the first attempt at 104.946 ký tự with 54 ký tự of headroom; the idempotency re-run
  reports already-applied (changed: 0) via the new guard (R193/R194 lesson).

## R198 robustness note — headroom now 54 chars

The R197 warning left 56 ký tự of headroom, so this round compacted
the R108 paragraph (694 ký tự → 239) before adding the new R197 paragraph
(396 ký tự). The body is now 104.946 ký tự — net +2 vs R197 — with
54 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R199 warning: headroom is 54 ký tự; the next round must collapse R107
(694 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R107 compaction alone frees ~454 ký tự, restoring comfortable headroom.
At the current net +2/round the margin holds with compaction; one full-paragraph compaction per round (~−454) keeps
the discipline sustainable (full paragraphs remaining R166..R197 = 32;
compact block R108–R165 = 58 lines).
Lesson this round: the dry-run projection matched the apply exactly
(104.946 ký tự); measure, don't hand-count (same lesson as R186/R190/R195/R197).

## Verification

- Merge-tree `280307b` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `f7db540a…`. Merge-tree at the R198
  content head `285ade4` vs `f3db6b3`: exit 0, tree
  `eba25dc0…`.
- Live PR state: API connector MCP read ~09:44 JST (first read carried the R175/R182-style artifact: 92.521 ký tự, sha `ced29e00`, 2 U+FFFD; immediate re-read byte-exact: 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `280307b`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-22T23:50:59Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
  Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, R197 round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~09:44 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R198 block (`280307b..285ade4`) 3 paths / 0 violations
  (index + body v2 + R198 checker); cumulative at the R198 content
  commit `285ade4` 2987 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `285ade4`).
  Merge-tree at the R198 content head `285ade4` vs `f3db6b3`: exit 0,
  tree `eba25dc0…`.
- Transient notes: no proxy failure on `git fetch` / `ls-remote` this round.
  No MCP parameter slip: both reads used the correct names first try
  (`pullNumber`, `issue_number`). No rate-limit 403 on any MCP read this round. The R197 payload's own head line recorded mergeable
  unstable at `280307b` at its preparation (CI still running on the new
  head); this round's fresh read shows clean at the same head after CI
  finished — the payload's unstable wording was correct at its
  preparation time, not a defect.
- Ceiling discipline: the R197 payload JSON measured 121.892 byte
  (as-prepared; cmp with its `.bak` byte-identical this round, so no
  main-flow refresh changed it) vs the 131.072-byte transport ceiling
  (9.180 byte headroom). The projected R198 payload JSON is ~122,300 byte
  (measured exactly at payload build, after push). Body v2 is now 104.946
  ký tự (< 105.000) — 54 ký tự of headroom. R198 warning:
  headroom is now 54 ký tự; the next round must collapse R107 (694 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R198 body
v2 (R197 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r198.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R198 push (title
ending "+ R198", built by replacing the "+ R140" suffix — not appending;
body = body v2 R198 in repo, head line refreshed to head after R198 push).
This run started ~09:40 JST — WITHIN working hours (09:00–21:30 JST), so the
R198 payload is READY FOR PRESENTATION by the main flow (not held like R142/R164–R197). Do not present the superseded R197 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196 and R197 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R198: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
