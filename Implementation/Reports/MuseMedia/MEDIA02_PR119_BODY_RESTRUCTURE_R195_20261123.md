# MEDIA-02 — PR #119 Body Restructure R195: delivery index + body v2 coverage to `25e6869`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `25e6869` (PR119 BODY RESTRUCTURE R194 report). Content commit: `6b67985`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R195 does

R194 left the disclosed gap: the delivery index covered 577 commits to
`6dd9d03`; R194's own 2 commits were to fold in at R195. The R194 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~06:44 JST, byte-exact at the
first read: 92.520 ký tự, 0 U+FFFD, sha `ddbe32ff` — no R175/R182-style read-path artifact this
round) show the live PR title ends
"+ R140", head `25e6869`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-22T20:45:56Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R194 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~06:44 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `25e6869` (~06:44 JST): `git rev-list --count
cf17178..25e6869` = 579 commits, `git diff --name-only` = 2977 files,
`--shortstat` = 281207 insertions, 0 deletions. `git merge-tree
--write-tree` `25e6869` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `1ebddb57…`. Like R194, this round DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `25e6869` (CI finished since the R194 push at ~05:46 JST; the R194 payload's own head line had
recorded mergeable unstable at preparation time, when CI was still running on the new head — see Transient notes).

R195 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `25e6869` (579 commits / 2977 files /
  281207 additions; the fresh git derivation at `25e6869`, the fresh API
  read ~06:44 JST, and the merge-tree cross-check at `25e6869` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `6dd9d03..25e6869`: 5 paths, 432 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R194
  (`f2d3fae`/`25e6869`), recording that its payload was prepared after
  push ~05:46 JST (104.914 ký tự, sha `36e44028`, mergeable_state unstable tại
  `25e6869` lúc chuẩn bị, lần clean gần nhất tại `6dd9d03`; JSON 122.049 byte < trần 131.072 — còn 9.023 byte, bản giữ tại
  `.bak-prepost-20261123`), that it was NOT refreshed by the main flow
  (cmp with its `.bak` byte-identical this round: payload sha `36e44028`,
  104.914 ký tự), that it was NOT posted
  — live body still R140 (verified by this round's API read: byte-exact at the first read, 92.520 ký tự, sha
  `ddbe32ff`, 0 U+FFFD) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; connector MCP get_comments page 1,
  perPage 100). The index now covers every block through `25e6869`; R195's
  own 2 commits fold in at the next index update (R196), disclosed in the
  index itself. The R195 note was appended after the R194 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Row-convention verification** (done this round before writing the
  R194 row): a table row's "cumulative N paths" is the diff path count at
  the AUTHORING round's content commit — R191 row 2969 == `7e80036`
  (R192 content), R192 row 2972 == `11a935f` (R193 content), R193 row
  2975 == `f2d3fae` (R194 content), all re-derived from git this round.
  The R194 row therefore cites cumulative 2978 paths — the diff count at
  the R195 content commit `6b67985`, verified after the commit (not
  predicted blindly). No correction to any earlier row was needed.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `25e6869` · 579 · 2977 (with the fresh git derivation at `25e6869`,
  the fresh API read ~06:44 JST, and the fresh merge-tree cross-check at
  `25e6869`), plus the R194 paragraph in "Khối mới nhất" (396 ký tự,
  marked chưa đăng — live body is R140) and the R195 note. The stale index
  reference in "Về bản mô tả này" (head `6dd9d03`) is also fixed to
  `25e6869`, and the title line is extended to R194 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R194 warning —
  applied with a margin): the R111 paragraph (694 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R194 paragraph was 396 ký tự, so
  the body is 104.881 ký tự — net +2 vs R194 despite the new R194
  paragraph, headroom 119 ký tự.
  Paragraph order: the R194 paragraph sits directly after R193
  (ascending full-paragraph order R166..R194), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R195 (owner tap) — the R140 body v2 now live
  is the base; only the R194 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r195_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R194 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R194 and R195 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R194 (55 compact lines R111–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.881 ký tự),
  and a check that the R194 paragraph sits directly after R193
  (ascending full-paragraph order). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R195_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R194) with the full COVER
  SHA verified intact (definition + docstring, both
  `25e68697deaae50c447aacbbc2a86b9662ded589` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `6dd9d03`/`577`/`2974`/`280786`/`689237bd` references in the checker — the R194 values;
  `f2d3fae` appears in the docstring's verified
  row-convention history and as the R194 content-sha check, as in R194) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.881 ký tự and the apply wrote on
  the first attempt at 104.881 ký tự with 119 ký tự of headroom; the idempotency re-run reported changed: 0.
  The content commit
  staged exactly the usual 3 files (index + body v2 + checker); the
  validation JSON rides with the report commit as in every prior round.

## R195 robustness note — headroom now 119 chars

The R194 warning left 121 ký tự of headroom, so this round compacted
the R111 paragraph (694 ký tự → 239) before adding the new R194 paragraph
(396 ký tự). The body is now 104.881 ký tự — net +2 vs R194 — with
119 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R196 warning: headroom is 119 ký tự; the next round must collapse R110
(694 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R110 compaction alone frees ~454 ký tự, restoring comfortable headroom.
At the current net +2/round the margin would hold for several rounds
even without compaction; one full-paragraph compaction per round (~−454) keeps
the discipline sustainable (full paragraphs remaining R166..R194 = 29;
compact block R111–R165 = 55 lines).
Lesson this round: the dry-run projection matched the apply exactly
(104.881 ký tự), but the net +2 vs R194 was 2 ký tự above the hand
estimate (0) — the "Về bản mô tả này" append is 25 ký tự, not 24 as
counted by hand. Measure, don't hand-count (same lesson as R186/R190).

## Verification

- Merge-tree `25e6869` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `1ebddb57…`. Merge-tree at the R195
  content head `6b67985` vs `f3db6b3`: exit 0, tree
  `eaf02dbe…`.
- Live PR state: API connector MCP read ~06:44 JST (byte-exact at the first read: 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD — no read-path artifact this round) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `25e6869`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-22T20:45:56Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
  Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor ~06:44 JST); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~06:44 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R195 block (`25e6869..6b67985`) 3 paths / 0 violations
  (index + body v2 + R195 checker); cumulative at the R195 content
  commit `6b67985` 2978 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `6b67985`).
  Merge-tree at the R195 content head `6b67985` vs `f3db6b3`: exit 0,
  tree `eaf02dbe…`.
- Transient notes: no proxy failure on `git fetch` / `ls-remote` this round.
  No MCP parameter slip: both reads used the correct names first try
  (`pullNumber`, `issue_number`). No rate-limit 403 on any MCP read this round. The R194 payload's own head line recorded mergeable
  unstable at `25e6869` at its preparation (CI still running on the new
  head); this round's fresh read shows clean at the same head after CI
  finished — the payload's unstable wording was correct at its
  preparation time, not a defect.
- Ceiling discipline: the R194 payload JSON measured 122.049 byte
  (as-prepared; cmp with its `.bak` byte-identical this round, so no
  main-flow refresh changed it) vs the 131.072-byte transport ceiling
  (9.023 byte headroom). The projected R195 payload JSON is ~122,200 byte
  (measured exactly at payload build, after push). Body v2 is now 104.881
  ký tự (< 105.000) — 119 ký tự of headroom. R195 warning:
  headroom is now 119 ký tự; the next round must collapse R110 (694 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R195 body
v2 (R194 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r195.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R195 push (title
ending "+ R195", built by replacing the "+ R140" suffix — not appending;
body = body v2 R195 in repo, head line refreshed to head after R195 push).
This run started ~06:40 JST — OUTSIDE working hours (09:00–21:30 JST), so the
R195 payload is HELD FOR WORKING HOURS by the main flow (not presented now — like R142/R164–R173/R186/R187/R188/R189/R190/R191/R192/R193/R194). Do not present the superseded R194 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193 and R194 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R195: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
