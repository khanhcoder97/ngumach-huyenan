# MEDIA-02 — PR #119 Body Restructure R196: delivery index + body v2 coverage to `bf5c258`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `bf5c258` (PR119 BODY RESTRUCTURE R195 report). Content commit: `218f0fa`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R196 does

R195 left the disclosed gap: the delivery index covered 579 commits to
`25e6869`; R195's own 2 commits were to fold in at R196. The R195 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~07:44 JST, byte-exact at the
first read: 92.520 ký tự, 0 U+FFFD, sha `ddbe32ff` — no R175/R182-style read-path artifact this
round) show the live PR title ends
"+ R140", head `bf5c258`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-22T21:51:58Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R195 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~07:44 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `bf5c258` (~07:44 JST): `git rev-list --count
cf17178..bf5c258` = 581 commits, `git diff --name-only` = 2980 files,
`--shortstat` = 281623 insertions, 0 deletions. `git merge-tree
--write-tree` `bf5c258` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `de530277…`. Like R195, this round DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `bf5c258` (CI finished since the R195 push at ~06:51 JST; the R195 payload's own head line had
recorded mergeable unstable at preparation time, when CI was still running on the new head — see Transient notes).

R196 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `bf5c258` (581 commits / 2980 files /
  281623 additions; the fresh git derivation at `bf5c258`, the fresh API
  read ~07:44 JST, and the merge-tree cross-check at `bf5c258` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `25e6869..bf5c258`: 5 paths, 427 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R195
  (`6b67985`/`bf5c258`), recording that its payload was prepared after
  push ~06:52 JST (104.916 ký tự, sha `64309331`, mergeable_state unstable tại
  `bf5c258` lúc chuẩn bị, lần clean gần nhất tại `25e6869`; JSON 121.999 byte < trần 131.072 — còn 9.073 byte, bản giữ tại
  `.bak-prepost-20261123`), that it was NOT refreshed by the main flow
  (cmp with its `.bak` byte-identical this round: payload sha `64309331`,
  104.916 ký tự), that it was NOT posted
  — live body still R140 (verified by this round's API read: byte-exact at the first read, 92.520 ký tự, sha
  `ddbe32ff`, 0 U+FFFD) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; connector MCP get_comments page 1,
  perPage 100). The index now covers every block through `bf5c258`; R196's
  own 2 commits fold in at the next index update (R197), disclosed in the
  index itself. The R196 note was appended after the R195 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Row-convention verification** (done this round before writing the
  R195 row): a table row's "cumulative N paths" is the diff path count at
  the AUTHORING round's content commit — R192 row 2972 == `11a935f`
  (R193 content), R193 row 2975 == `f2d3fae` (R194 content), R194 row
  2978 == `6b67985` (R195 content), all re-derived from git this round.
  The R195 row therefore cites cumulative 2981 paths — the diff count at
  the R196 content commit `218f0fa`, verified after the commit (not
  predicted blindly). No correction to any earlier row was needed.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `bf5c258` · 581 · 2980 (with the fresh git derivation at `bf5c258`,
  the fresh API read ~07:44 JST, and the fresh merge-tree cross-check at
  `bf5c258`), plus the R195 paragraph in "Khối mới nhất" (396 ký tự,
  marked chưa đăng — live body is R140) and the R196 note. The stale index
  reference in "Về bản mô tả này" (head `25e6869`) is also fixed to
  `bf5c258`, and the title line is extended to R195 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R195 warning —
  applied with a margin): the R110 paragraph (694 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R195 paragraph was 396 ký tự, so
  the body is 104.883 ký tự — net +2 vs R195 despite the new R195
  paragraph, headroom 117 ký tự.
  Paragraph order: the R195 paragraph sits directly after R194
  (ascending full-paragraph order R166..R195), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R196 (owner tap) — the R140 body v2 now live
  is the base; only the R195 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r196_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R195 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R195 and R196 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R195 (56 compact lines R110–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.883 ký tự),
  and a check that the R195 paragraph sits directly after R194
  (ascending full-paragraph order). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R196_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R195) with the full COVER
  SHA verified intact (definition + docstring, both
  `bf5c2587accce92fe67618c5070134556a91ed34` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `25e6869`/`579`/`2977`/`281207`/`1ebddb57` references in the checker — the R195 values;
  `f2d3fae` appears in the docstring's verified
  row-convention history, as in R195) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.883 ký tự and the apply wrote on
  the first attempt at 104.883 ký tự with 117 ký tự of headroom; the idempotency re-run tripped the
  already-applied guard at the first anchor (changed: 0).
  The content commit
  staged exactly the usual 3 files (index + body v2 + checker); the
  validation JSON rides with the report commit as in every prior round.

## R196 robustness note — headroom now 117 chars

The R195 warning left 119 ký tự of headroom, so this round compacted
the R110 paragraph (694 ký tự → 239) before adding the new R195 paragraph
(396 ký tự). The body is now 104.883 ký tự — net +2 vs R195 — with
117 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R197 warning: headroom is 117 ký tự; the next round must collapse R109
(694 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R109 compaction alone frees ~454 ký tự, restoring comfortable headroom.
At the current net +2/round the margin would hold for several rounds
even without compaction; one full-paragraph compaction per round (~−454) keeps
the discipline sustainable (full paragraphs remaining R166..R195 = 30;
compact block R110–R165 = 56 lines).
Lesson this round: the dry-run projection matched the apply exactly
(104.883 ký tự), and the net +2 vs R195 repeated the R195 pattern — the
budget discipline is now stable (same lesson as R186/R190/R195: measure,
don't hand-count).

## Verification

- Merge-tree `bf5c258` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `de530277…`. Merge-tree at the R196
  content head `218f0fa` vs `f3db6b3`: exit 0, tree
  `7518240a…`.
- Live PR state: API connector MCP read ~07:44 JST (byte-exact at the first read: 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD — no read-path artifact this round) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `bf5c258`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-22T21:51:58Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
  Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor ~07:44 JST); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~07:44 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R196 block (`bf5c258..218f0fa`) 3 paths / 0 violations
  (index + body v2 + R196 checker); cumulative at the R196 content
  commit `218f0fa` 2981 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `218f0fa`).
  Merge-tree at the R196 content head `218f0fa` vs `f3db6b3`: exit 0,
  tree `7518240a…`.
- Transient notes: no proxy failure on `git fetch` / `ls-remote` this round.
  No MCP parameter slip: both reads used the correct names first try
  (`pullNumber`, `issue_number`). No rate-limit 403 on any MCP read this round. The R195 payload's own head line recorded mergeable
  unstable at `bf5c258` at its preparation (CI still running on the new
  head); this round's fresh read shows clean at the same head after CI
  finished — the payload's unstable wording was correct at its
  preparation time, not a defect.
- Ceiling discipline: the R195 payload JSON measured 121.999 byte
  (as-prepared; cmp with its `.bak` byte-identical this round, so no
  main-flow refresh changed it) vs the 131.072-byte transport ceiling
  (9.073 byte headroom). The projected R196 payload JSON is ~122,200 byte
  (measured exactly at payload build, after push). Body v2 is now 104.883
  ký tự (< 105.000) — 117 ký tự of headroom. R196 warning:
  headroom is now 117 ký tự; the next round must collapse R109 (694 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R196 body
v2 (R195 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r196.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R196 push (title
ending "+ R196", built by replacing the "+ R140" suffix — not appending;
body = body v2 R196 in repo, head line refreshed to head after R196 push).
This run started ~07:40 JST — OUTSIDE working hours (09:00–21:30 JST), so the
R196 payload is HELD FOR WORKING HOURS by the main flow (not presented now — like R142/R164–R173/R186/R187/R188/R189/R190/R191/R192/R193/R194/R195). Do not present the superseded R195 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194 and R195 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R196: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
