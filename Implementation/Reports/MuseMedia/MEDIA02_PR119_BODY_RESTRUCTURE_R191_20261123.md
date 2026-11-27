# MEDIA-02 — PR #119 Body Restructure R191: delivery index + body v2 coverage to `6d65e75`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `6d65e75` (PR119 BODY RESTRUCTURE R190 report). Content commit: `d105f51`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R191 does

R190 left the disclosed gap: the delivery index covered 569 commits to
`4380848`; R190's own 2 commits were to fold in at R191. The R190 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~02:44 JST, first read byte-exact:
92.520 ký tự, 0 U+FFFD, sha `ddbe32ff` — no R175-style read-path artifact this round) show the live PR title ends
"+ R140", head `6d65e75`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-22T16:50:54Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R190 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~02:44 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `6d65e75` (~02:44 JST): `git rev-list --count
cf17178..6d65e75` = 571 commits, `git diff --name-only` = 2965 files,
`--shortstat` = 279547 insertions, 0 deletions. `git merge-tree
--write-tree` `6d65e75` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `1eccdf56…`. Like R190, this round DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `6d65e75` (CI finished since the R190 push at ~01:51 JST; the R190 payload's own head line had
recorded mergeable unstable at preparation time, when CI was still running on the new head — see Transient notes).

R191 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `6d65e75` (571 commits / 2965 files /
  279547 additions; the fresh git derivation at `6d65e75`, the fresh API
  read ~02:44 JST, and the merge-tree cross-check at `6d65e75` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `4380848..6d65e75`: 5 paths, 415 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R190
  (`ed21eb2`/`6d65e75`), recording that its payload was prepared after
  push ~01:51 JST (104.949 ký tự, sha `464cc46f`, mergeable_state unstable tại
  `6d65e75` lúc chuẩn bị, lần clean gần nhất tại `4380848`; JSON 122.286 byte < trần 131.072 — còn 8.786 byte, bản giữ tại
  `.bak-prepost-20261123`), that it was NOT refreshed by the main flow
  (cmp with its `.bak` byte-identical this round: payload sha `464cc46f`,
  104.949 ký tự), that it was NOT posted
  — live body still R140 (verified by this round's API read: first read byte-exact 92.520 ký tự, sha
  `ddbe32ff`, 0 U+FFFD) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; connector MCP get_comments page 1,
  perPage 100). The index now covers every block through `6d65e75`; R191's
  own 2 commits fold in at the next index update (R192), disclosed in the
  index itself. The R191 note was appended after the R190 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Row-convention verification** (done this round before writing the
  R190 row): a table row's "cumulative N paths" is the diff path count at
  the AUTHORING round's content commit — R187 row 2957 == `ea34c5a`
  (R188 content), R188 row 2960 == `45142ad` (R189 content), R189 row
  2963 == `ed21eb2` (R190 content), all re-derived from git this round.
  The R190 row therefore cites cumulative 2966 paths — the diff count at
  the R191 content commit `d105f51`, verified after the commit (not
  predicted blindly). No correction to any earlier row was needed.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `6d65e75` · 571 · 2965 (with the fresh git derivation at `6d65e75`,
  the fresh API read ~02:44 JST, and the fresh merge-tree cross-check at
  `6d65e75`), plus the R190 paragraph in "Khối mới nhất" (483 ký tự,
  marked chưa đăng — live body is R140) and the R191 note. The stale index
  reference in "Về bản mô tả này" (head `4380848`) is also fixed to
  `6d65e75`, and the title line is extended to R190 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R190 warning —
  applied with a margin): the R115 paragraph (735 ký tự — measured this
  round) is
  collapsed to one 247-ký-tự compact line (full detail stays in the
  delivery index) — the new R190 paragraph was 483 ký tự, so
  the body is 104.970 ký tự — net +56 vs R190 despite the new R190
  paragraph, headroom 30 ký tự.
  Paragraph order: the R190 paragraph sits directly after R189
  (ascending full-paragraph order R166..R190), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R191 (owner tap) — the R140 body v2 now live
  is the base; only the R190 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r191_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R190 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R190 and R191 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R190 (51 compact lines R115–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.970 ký tự),
  and a check that the R190 paragraph sits directly after R189
  (ascending full-paragraph order). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R191_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R190) with the full COVER
  SHA verified intact (2 occurrences) and a stale-reference grep (0 stale
  `4380848`/`5cf5000`/`2962`/`279143`/`048f8ee9`
  references in the checker — the R190 values; the single `45142ad` hit is
  an intentional citation inside the docstring's row-convention note,
  verified from git this round) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the simulation measured 104.970 ký tự with 30 ký tự of headroom and wrote on
  the first attempt; the idempotency re-run reported changed: 0. The content commit
  staged exactly the usual 3 files (index + body v2 + checker); the
  validation JSON rides with the report commit as in every prior round.

## R191 robustness note — headroom now 30 chars

The R190 warning left 86 ký tự of headroom, so this round compacted
the R115 paragraph (735 ký tự → 247) before adding the new R190 paragraph
(483 ký tự). The body is now 104.970 ký tự — net +56 vs R190 — with
30 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R192 warning: headroom is 30 ký tự; the next round must collapse R114
(735 ký tự → ~250) and keep the new paragraph tight (≤ ~460 ký tự) — the
R114 compaction alone frees ~485 ký tự, restoring comfortable headroom.
At the current net +56/round the margin would hit zero in ~1 round
without compaction; one full-paragraph compaction per round (~−485) keeps
the discipline sustainable (full paragraphs remaining R166..R190 = 25;
compact block R115–R165 = 51 lines).

## Verification

- Merge-tree `6d65e75` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `1eccdf56…`. Merge-tree at the R191
  content head `d105f51` vs `f3db6b3`: exit 0, tree
  `f36fb98c…`.
- Live PR state: API connector MCP read ~02:44 JST (first read byte-exact, 92.520 ký tự,
  0 U+FFFD — no R175-style artifact this round) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `6d65e75`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-22T16:50:54Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~02:44 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R191 block (`6d65e75..d105f51`) 3 paths / 0 violations
  (index + body v2 + R191 checker); cumulative at the R191 content
  commit `d105f51` 2966 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `d105f51`).
  Merge-tree at the R191 content head `d105f51` vs `f3db6b3`: exit 0,
  tree `f36fb98c…`.
- Transient notes: the first MCP pull read this round was byte-exact
  (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — no R175-style artifact, no
  re-read needed. The R190 payload's own head line recorded mergeable
  unstable at `6d65e75` at its preparation (CI still running on the new
  head); this round's fresh read shows clean at the same head after CI
  finished — the payload's unstable wording was correct at its
  preparation time, not a defect. No proxy failure on `git ls-remote` /
  fetch this round. No MCP parameter slip: both reads used
  the correct names first try (`pullNumber`, `issue_number`). No
  rate-limit 403 on any MCP read this round.
- Ceiling discipline: the R190 payload JSON measured 122.286 byte
  (as-prepared; cmp with its `.bak` byte-identical this round, so no
  main-flow refresh changed it) vs the 131.072-byte transport ceiling
  (8.786 byte headroom). The projected R191 payload JSON is ~123,000 byte
  (measured exactly at payload build, after push). Body v2 is now 104.970
  ký tự (< 105.000) — 30 ký tự of headroom. R191 warning:
  headroom is now 30 ký tự; the next round must collapse R114 (735 ký tự
  → ~250) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R191 body
v2 (R190 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r191.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R191 push (title
ending "+ R191", built by replacing the "+ R140" suffix — not appending;
body = body v2 R191 in repo, head line refreshed to head after R191 push).
This run started ~02:40 JST — PAST working hours (09:00–21:30 JST), so the
R191 payload is HELD FOR WORKING HOURS by the main flow (not presented tonight — like R142/R164–R173/R186/R187/R188/R189/R190). Do not present the superseded R190 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189 and R190 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R191: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
