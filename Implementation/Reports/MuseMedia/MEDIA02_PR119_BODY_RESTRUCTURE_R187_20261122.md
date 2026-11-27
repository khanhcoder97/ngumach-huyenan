# MEDIA-02 — PR #119 Body Restructure R187: delivery index + body v2 coverage to `c7b732f`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `c7b732f` (PR119 BODY RESTRUCTURE R186 report). Content commit: `a24a3b6`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R187 does

R186 left the disclosed gap: the delivery index covered 561 commits to
`ebe432e`; R186's own 2 commits were to fold in at R187. The R186 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~22:44 JST, first read byte-exact:
92.520 ký tự, 0 U+FFFD, sha `ddbe32ff` — no R175-style read-path artifact this round) show the live PR title ends
"+ R140", head `c7b732f`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-22T12:48:33Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R186 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~22:44 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `c7b732f` (~22:44 JST): `git rev-list --count
cf17178..c7b732f` = 563 commits, `git diff --name-only` = 2953 files,
`--shortstat` = 277990 insertions, 0 deletions. `git merge-tree
--write-tree` `c7b732f` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `a6e2b4e1…`. Like R186, this round DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `c7b732f` (CI finished since the R186 push at ~21:48 JST; the R186 payload's own head line had
recorded mergeable unstable at preparation time, when CI was still running on the new head — see Transient notes).

R187 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `c7b732f` (563 commits / 2953 files /
  277990 additions; the fresh git derivation at `c7b732f`, the fresh API
  read ~22:44 JST, and the merge-tree cross-check at `c7b732f` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `ebe432e..c7b732f`: 5 paths, 394 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R186
  (`bb9dc34`/`c7b732f`), recording that its payload was prepared after
  push ~21:49 JST (104.844 ký tự, sha `fab473a7`, mergeable_state unstable tại
  `c7b732f` lúc chuẩn bị, lần clean gần nhất tại `ebe432e`; JSON 122.371 byte < trần 131.072 — còn 8.701 byte, bản giữ tại
  `.bak-prepost-20261122`), that it was NOT refreshed by the main flow
  (cmp with its `.bak` byte-identical this round: payload sha `fab473a7`,
  104.844 ký tự), that it was NOT posted
  — live body still R140 (verified by this round's API read: first read byte-exact 92.520 ký tự, sha
  `ddbe32ff`, 0 U+FFFD) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; connector MCP get_comments page 1,
  perPage 100). The index now covers every block through `c7b732f`; R187's
  own 2 commits fold in at the next index update (R188), disclosed in the
  index itself. The R187 note was appended after the R186 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `c7b732f` · 563 · 2953 (with the fresh git derivation at `c7b732f`,
  the fresh API read ~22:44 JST, and the fresh merge-tree cross-check at
  `c7b732f`), plus the R186 paragraph in "Khối mới nhất" (486 ký tự,
  marked chưa đăng — live body is R140) and the R187 note. The stale index
  reference in "Về bản mô tả này" (head `ebe432e`) is also fixed to
  `c7b732f`, and the title line is extended to R186 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R186 warning —
  applied with a margin): the R119 paragraph (739 ký tự — measured this
  round, not the ~900 estimated in the R186 warning) is
  collapsed to one 252-ký-tự compact line (full detail stays in the
  delivery index) — the new R186 paragraph was 486 ký tự, so
  the body is 104.869 ký tự — net +60 vs R186 despite the new R186
  paragraph, headroom 131 ký tự.
  Paragraph order: the R186 paragraph sits directly after R185
  (ascending full-paragraph order R166..R186), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R187 (owner tap) — the R140 body v2 now live
  is the base; only the R186 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r187_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R186 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R186 and R187 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R186 (47 compact lines R119–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.869 ký tự),
  and a check that the R186 paragraph sits directly after R185
  (ascending full-paragraph order). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R187_VALIDATION_20261122.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R186) with the full COVER
  SHA verified intact (2 occurrences) and a stale-reference grep (0 stale
  `39fdce6`/`3e201e2`/`2ca7461`/`ebd3c1d`/`561 commit`/`2950 file`/`277607`/`36a4f6de` references in the checker — the R186 values) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The `bb9dc34`/`c7b732f` hits in the checker are the
  intended assertions that the index row carries the R186 content/report
  SHAs. The edit script's budget check ran before any write (R166 lesson):
  the projection was 104.869 ký tự with 131 ký tự of headroom and wrote on
  the first attempt; the idempotency re-run reported changed: 0. The content commit
  staged exactly the usual 3 files (index + body v2 + checker); the
  validation JSON rides with the report commit as in every prior round.

## R187 robustness note — headroom now 131 chars

The R186 warning left only 191 ký tự of headroom, so this round compacted
the R119 paragraph (739 ký tự → 252) before adding the new R186 paragraph
(486 ký tự). The body is now 104.869 ký tự — net +60 vs R186 — with
131 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R188 warning: headroom is 131 ký tự; the next round must collapse R118
(846 ký tự → ~280) and keep the new paragraph tight (≤ ~470 ký tự) — the
R118 compaction alone frees ~566 ký tự, restoring comfortable headroom.

## Verification

- Merge-tree `c7b732f` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `a6e2b4e1…`. Merge-tree at the R187
  content head `a24a3b6` vs `f3db6b3`: exit 0, tree
  `7f790821…`.
- Live PR state: API connector MCP read ~22:44 JST (first read byte-exact, 92.520 ký tự,
  0 U+FFFD — no R175-style artifact this round) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `c7b732f`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-22T12:48:33Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~22:44 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R187 block (`c7b732f..a24a3b6`) 3 paths / 0 violations
  (index + body v2 + R187 checker); cumulative at the R187 content
  commit `a24a3b6` 2954 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `a24a3b6`).
  Merge-tree at the R187 content head `a24a3b6` vs `f3db6b3`: exit 0,
  tree `7f790821…`. (Note: an audit run with base `ebe432e` printed 6
  paths — it spanned the R186 report commit as well; the R187 block is
  `c7b732f..a24a3b6`, 3 paths, as in every prior round.)
- Transient notes: the first MCP pull read this round was byte-exact
  (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — no R175-style artifact, no
  re-read needed. The R186 payload's own head line recorded mergeable
  unstable at `c7b732f` at its preparation (CI still running on the new
  head); this round's fresh read shows clean at the same head after CI
  finished — the payload's unstable wording was correct at its
  preparation time, not a defect. No proxy failure on `git ls-remote` /
  fetch this round (R186 had one transient proxy close). No MCP parameter slip: both reads used
  the correct names first try (`pullNumber`, `issue_number`). No
  rate-limit 403 on any MCP read this round.
- Ceiling discipline: the R186 payload JSON measured 122.371 byte
  (as-prepared; cmp with its `.bak` byte-identical this round, so no
  main-flow refresh changed it) vs the 131.072-byte transport ceiling
  (8.701 byte headroom). The projected R187 payload JSON is ~123,000 byte
  (measured exactly at payload build, after push). Body v2 is now 104.869
  ký tự (< 105.000) — 131 ký tự of headroom. R188 warning:
  headroom is now 131 ký tự; the next round must collapse R118 (846 ký tự
  → ~280) and keep the new paragraph tight (≤ ~470 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R187 body
v2 (R186 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r187.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R187 push (title
ending "+ R187", built by replacing the "+ R140" suffix — not appending;
body = body v2 R187 in repo, head line refreshed to head after R187 push).
This run started ~22:40 JST — PAST working hours (09:00–21:30 JST), so the
R187 payload is HELD FOR WORKING HOURS by the main flow (not presented tonight — like R142/R164–R173/R186). Do not present the superseded R186 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185 and R186 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R187: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
