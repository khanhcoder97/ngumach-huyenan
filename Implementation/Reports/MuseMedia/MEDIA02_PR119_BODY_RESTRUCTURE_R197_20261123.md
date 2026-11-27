# MEDIA-02 — PR #119 Body Restructure R197: delivery index + body v2 coverage to `eb54d4d`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `eb54d4d` (PR119 BODY RESTRUCTURE R196 report). Content commit: `41f9110`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R197 does

R196 left the disclosed gap: the delivery index covered 583 commits to
`eb54d4d`; R196's own 2 commits were to fold in at R197. The R196 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~08:44 JST; the FIRST read carried the
R175/R182-style read-path artifact — 92.521 ký tự, sha `ced29e00`, 2 U+FFFD — and the immediate
re-read was byte-exact: 92.520 ký tự, 0 U+FFFD, sha `ddbe32ff`) show the live PR title ends
"+ R140", head `eb54d4d`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-22T22:48:58Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R196 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~08:44 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `eb54d4d` (~08:44 JST): `git rev-list --count
cf17178..eb54d4d` = 583 commits, `git diff --name-only` = 2983 files,
`--shortstat` = 282033 insertions, 0 deletions. `git merge-tree
--write-tree` `eb54d4d` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `131a24b0…`. Like R196, this round DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `eb54d4d` (CI finished since the R196 push at ~07:50 JST; the R196 payload's own head line had
recorded mergeable unstable at preparation time, when CI was still running on the new head — see Transient notes).

R197 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `eb54d4d` (583 commits / 2983 files /
  282033 additions; the fresh git derivation at `eb54d4d`, the fresh API
  read ~08:44 JST, and the merge-tree cross-check at `eb54d4d` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `bf5c258..eb54d4d`: 5 paths, 424 insertions, 14
  deletions); one row appended — PR119 BODY RESTRUCTURE R196
  (`218f0fa`/`eb54d4d`), recording that its payload was prepared after
  push ~07:50 JST (104.918 ký tự, sha `bcc2f6d4`, mergeable_state unstable tại
  `eb54d4d` lúc chuẩn bị, lần clean gần nhất tại `bf5c258`; JSON 121.942 byte < trần 131.072 — còn 9.130 byte, bản giữ tại
  `.bak-prepost-20261123`), that it was NOT refreshed by the main flow
  (cmp with its `.bak` byte-identical this round: payload sha `bcc2f6d4`,
  104.918 ký tự), that it was NOT posted
  — live body still R140 (verified by this round's API read: first read carried the 2-U+FFFD artifact,
  92.521 ký tự sha `ced29e00`; immediate re-read byte-exact, 92.520 ký tự, sha
  `ddbe32ff`, 0 U+FFFD) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; connector MCP get_comments page 1,
  perPage 100). The index now covers every block through `eb54d4d`; R197's
  own 2 commits fold in at the next index update (R198), disclosed in the
  index itself. The R197 note was appended after the R196 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Row-convention verification** (done this round before writing the
  R196 row): a table row's "cumulative N paths" is the diff path count at
  the AUTHORING round's content commit — R193 row 2975 == `f2d3fae`
  (R194 content), R194 row 2978 == `6b67985` (R195 content), R195 row
  2981 == `218f0fa` (R196 content), all re-derived from git this round.
  The R196 row therefore cites cumulative 2984 paths — the diff count at
  the R197 content commit `41f9110`, verified after the commit (not
  predicted blindly). No correction to any earlier row was needed.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `eb54d4d` · 583 · 2983 (with the fresh git derivation at `eb54d4d`,
  the fresh API read ~08:44 JST, and the fresh merge-tree cross-check at
  `eb54d4d`), plus the R196 paragraph in "Khối mới nhất" (396 ký tự,
  marked chưa đăng — live body is R140) and the R197 note. The stale index
  reference in "Về bản mô tả này" (head `bf5c258`) is also fixed to
  `eb54d4d`, and the title line is extended to R196 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R196 warning —
  applied with a margin): the R109 paragraph (694 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R196 paragraph was 396 ký tự, so
  the body is 104.944 ký tự — net +61 vs R196 despite the new R196
  paragraph, headroom 56 ký tự. The +61 net (not +2 as in R195/R196) is
  honest: the head line grew ~59 ký tự because it now records the
  first-read U+FFFD artifact and its re-read explicitly.
  Paragraph order: the R196 paragraph sits directly after R195
  (ascending full-paragraph order R166..R196), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R197 (owner tap) — the R140 body v2 now live
  is the base; only the R196 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r197_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R196 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R196 and R197 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R196 (57 compact lines R109–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.944 ký tự),
  a check that the R196 paragraph sits directly after R195
  (ascending full-paragraph order), and a new check for the R196
  script-defect repairs below (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R196 note clean).
  **PASS 20/20**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R197_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R196) with the full COVER
  SHA verified intact (definition + docstring, both
  `eb54d4d6b606ca55a80d41bd45e992c34a414225` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `25e6869`/`281207`/`1ebddb57` references in the checker — the R195 values;
  no `bf5c258` reference at all) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.944 ký tự and the apply wrote on
  the first attempt at 104.944 ký tự with 56 ký tự of headroom; the idempotency re-run
  reports already-applied (changed: 0) via the new guard (R193/R194 lesson).

## R196 script-defect repairs (found this round, in the committed index)

The R196 edit script (`r196_edit.py`) dropped trailing `"\n"` on
whole-line replacements and inserts, silently damaging the index file
at commit `218f0fa` (the R196 report did not notice). Three defects,
all repaired by this round's script — no text was lost:

1. **Milestone block joined**: the 6 "Mốc xác minh" bullets were collapsed
   into ONE 1787-character line (each whole-line replacement dropped its
   line's `"\n"`). Restored as 6 separate lines.
2. **`## Ghi chú` heading swallowed**: the R195 table-row insert had no
   trailing `"\n"`, so the row line ended `...| PASS 19/19 |## Ghi chú`
   and the heading vanished as its own line. Stripped from the row tail
   and restored as its own line after the R196 row (same layout as at
   `bf5c258`: row, heading, blank, notes).
3. **R167 note glued to the R196 note**: the R196-note insert had no
   trailing `"\n"`, so line 526 was `R196 note + R167 note` concatenated.
   The R167 note was already misplaced at the end of the list by an
   earlier round (at `bf5c258` it sat at line 531, after R195, instead of
   between R166 and R168). Its text survives intact; this round moved it
   to its ascending position (after R166, before R168).

The new checker asserts all three repairs explicitly, so a repeat is
caught at validation time. Own-round lesson: the first apply of this
round's own script had the mirror defect — the extracted R167 note
already carried its keepends `"\n"` and the insert added another,
leaving a spurious blank line between R167 and R168. Caught by the
line-count check (544 vs expected 543), fixed in the script
(`rstrip("\n")` on the extracted note), files checked out and cleanly
re-applied (543 lines, R166/R167/R168 consecutive, re-run guard
reports changed: 0). Rule restated for future rounds: every line
assignment/insert must carry exactly one trailing `"\n"` — never zero,
never two.

## R197 robustness note — headroom now 56 chars

The R196 warning left 117 ký tự of headroom, so this round compacted
the R109 paragraph (694 ký tự → 239) before adding the new R196 paragraph
(396 ký tự). The body is now 104.944 ký tự — net +61 vs R196 — with
56 ký tự of headroom, because the head line now honestly records the
first-read U+FFFD artifact and its re-read (+~59 ký tự vs R196). The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R198 warning: headroom is 56 ký tự; the next round must collapse R108
(694 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R108 compaction alone frees ~454 ký tự, restoring comfortable headroom.
At the current net +61/round the margin would NOT hold without
compaction; one full-paragraph compaction per round (~−454) keeps
the discipline sustainable (full paragraphs remaining R166..R196 = 31;
compact block R109–R165 = 57 lines).
Lesson this round: the dry-run projection matched the apply exactly
(104.944 ký tự); measure, don't hand-count (same lesson as R186/R190/R195).

## Verification

- Merge-tree `eb54d4d` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `131a24b0…`. Merge-tree at the R197
  content head `41f9110` vs `f3db6b3`: exit 0, tree
  `13b107bd…`.
- Live PR state: API connector MCP read ~08:44 JST (first read carried the R175/R182-style artifact: 92.521 ký tự, sha `ced29e00`, 2 U+FFFD; immediate re-read byte-exact: 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `eb54d4d`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-22T22:48:58Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
  Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor ~08:44 JST); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~08:44 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R197 block (`eb54d4d..41f9110`) 3 paths / 0 violations
  (index + body v2 + R197 checker); cumulative at the R197 content
  commit `41f9110` 2984 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `41f9110`).
  Merge-tree at the R197 content head `41f9110` vs `f3db6b3`: exit 0,
  tree `13b107bd…`.
- Transient notes: no proxy failure on `git fetch` / `ls-remote` this round.
  No MCP parameter slip: both reads used the correct names first try
  (`pullNumber`, `issue_number`). No rate-limit 403 on any MCP read this round. The R196 payload's own head line recorded mergeable
  unstable at `eb54d4d` at its preparation (CI still running on the new
  head); this round's fresh read shows clean at the same head after CI
  finished — the payload's unstable wording was correct at its
  preparation time, not a defect.
- Ceiling discipline: the R196 payload JSON measured 121.942 byte
  (as-prepared; cmp with its `.bak` byte-identical this round, so no
  main-flow refresh changed it) vs the 131.072-byte transport ceiling
  (9.130 byte headroom). The projected R197 payload JSON is ~122,300 byte
  (measured exactly at payload build, after push). Body v2 is now 104.944
  ký tự (< 105.000) — 56 ký tự of headroom. R197 warning:
  headroom is now 56 ký tự; the next round must collapse R108 (694 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R197 body
v2 (R196 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r197.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R197 push (title
ending "+ R197", built by replacing the "+ R140" suffix — not appending;
body = body v2 R197 in repo, head line refreshed to head after R197 push).
This run started ~08:40 JST — BEFORE working hours (09:00–21:30 JST), so the
R197 payload is HELD FOR WORKING HOURS by the main flow (not presented now — like R142/R164–R173/R186/R187/R188/R189/R190/R191/R192/R193/R194/R195/R196). Do not present the superseded R196 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195 and R196 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R197: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
