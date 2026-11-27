# MEDIA-02 — PR #119 Body Restructure R193: delivery index + body v2 coverage to `0c67764`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `0c67764` (PR119 BODY RESTRUCTURE R192 report). Content commit: `11a935f`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R193 does

R192 left the disclosed gap: the delivery index covered 573 commits to
`77e5df1`; R192's own 2 commits were to fold in at R193. The R192 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~04:44 JST, first read carried an
R175/R182-style read-path artifact: 92.521 ký tự, 2 U+FFFD; the immediate re-read was byte-exact:
92.520 ký tự, 0 U+FFFD, sha `ddbe32ff` — no live-body change, the first read was the artifact) show the live PR title ends
"+ R140", head `0c67764`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-22T18:49:16Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R192 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~04:44 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `0c67764` (~04:44 JST): `git rev-list --count
cf17178..0c67764` = 575 commits, `git diff --name-only` = 2971 files,
`--shortstat` = 280365 insertions, 0 deletions. `git merge-tree
--write-tree` `0c67764` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `a0541c9e…`. Like R192, this round DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `0c67764` (CI finished since the R192 push at ~03:44 JST; the R192 payload's own head line had
recorded mergeable unstable at preparation time, when CI was still running on the new head — see Transient notes).

R193 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `0c67764` (575 commits / 2971 files /
  280365 additions; the fresh git derivation at `0c67764`, the fresh API
  read ~04:44 JST, and the merge-tree cross-check at `0c67764` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `77e5df1..0c67764`: 5 paths, 427 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R192
  (`7e80036`/`0c67764`), recording that its payload was prepared after
  push ~03:49 JST (104.992 ký tự, sha `595d4eea`, mergeable_state unstable tại
  `0c67764` lúc chuẩn bị, lần clean gần nhất tại `77e5df1`; JSON 122.235 byte < trần 131.072 — còn 8.837 byte, bản giữ tại
  `.bak-prepost-20261123`), that it was NOT refreshed by the main flow
  (cmp with its `.bak` byte-identical this round: payload sha `595d4eea`,
  104.992 ký tự), that it was NOT posted
  — live body still R140 (verified by this round's API read: first read artifact 92.521 ký tự / 2 U+FFFD, re-read byte-exact 92.520 ký tự, sha
  `ddbe32ff`, 0 U+FFFD) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; connector MCP get_comments page 1,
  perPage 100). The index now covers every block through `0c67764`; R193's
  own 2 commits fold in at the next index update (R194), disclosed in the
  index itself. The R193 note was appended after the R192 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Row-convention verification** (done this round before writing the
  R192 row): a table row's "cumulative N paths" is the diff path count at
  the AUTHORING round's content commit — R189 row 2963 == `ed21eb2`
  (R190 content), R190 row 2966 == `d105f51` (R191 content), R191 row
  2969 == `7e80036` (R192 content), all re-derived from git this round.
  The R192 row therefore cites cumulative 2972 paths — the diff count at
  the R193 content commit `11a935f`, verified after the commit (not
  predicted blindly). No correction to any earlier row was needed.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `0c67764` · 575 · 2971 (with the fresh git derivation at `0c67764`,
  the fresh API read ~04:44 JST, and the fresh merge-tree cross-check at
  `0c67764`), plus the R192 paragraph in "Khối mới nhất" (396 ký tự,
  marked chưa đăng — live body is R140) and the R193 note. The stale index
  reference in "Về bản mô tả này" (head `77e5df1`) is also fixed to
  `0c67764`, and the title line is extended to R192 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R192 warning —
  applied with a margin): the R113 paragraph (735 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R192 paragraph was 396 ký tự, so
  the body is 104.959 ký tự — net +2 vs R192 despite the new R192
  paragraph, headroom 41 ký tự.
  Paragraph order: the R192 paragraph sits directly after R191
  (ascending full-paragraph order R166..R192), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R193 (owner tap) — the R140 body v2 now live
  is the base; only the R192 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r193_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R192 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R192 and R193 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R192 (53 compact lines R113–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.959 ký tự),
  and a check that the R192 paragraph sits directly after R191
  (ascending full-paragraph order). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R193_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R192) with the full COVER
  SHA verified intact (definition + docstring, both
  `0c67764b032df79c750f8a1aee32a7d7fcc7fdf6` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `77e5df1`/`573`/`2968`/`279949`/`9d863db7`/`6d65e75`/`4380848`/`5cf5000`/`1eccdf56`
  references in the checker — the R192 values) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation first projected exactly 105.000 ký tự and tripped the
  assert — files untouched — then the R192 paragraph was trimmed 422 → 396 ký tự
  and the head-line artifact wording shortened, and the apply wrote on
  the first attempt at 104.959 ký tự with 41 ký tự of headroom; the idempotency re-run reported changed: 0 after a
  guard fix (see lesson below). The content commit
  staged exactly the usual 3 files (index + body v2 + checker); the
  validation JSON rides with the report commit as in every prior round.

## R193 robustness note — headroom now 41 chars

The R192 warning left 43 ký tự of headroom, so this round compacted
the R113 paragraph (735 ký tự → 239) before adding the new R192 paragraph
(396 ký tự). The body is now 104.959 ký tự — net +2 vs R192 — with
41 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R194 warning: headroom is 41 ký tự; the next round must collapse R112
(735 ký tự → ~250) and keep the new paragraph tight (≤ ~460 ký tự) — the
R112 compaction alone frees ~485 ký tự, restoring comfortable headroom.
At the current net +2/round the margin would hold for several rounds
even without compaction; one full-paragraph compaction per round (~−485) keeps
the discipline sustainable (full paragraphs remaining R166..R192 = 27;
compact block R113–R165 = 53 lines).
Lesson this round: the edit script's first idempotency re-run CRASHED on
the head-line assert (`len(old_head) == 1` with an empty list) — after the
apply, the old `77e5df1` head line no longer exists, so the assert ran
before the idempotency check could skip it. The crash happened on the
third invocation, before any write — files untouched. The guard now checks
`HEAD_LINE_NEW in body` first and skips the replace when already applied;
the re-run then reported changed: 0. The dry-run budget assert also proved
its worth this round: the first projection landed exactly on 105.000 and
was refused before any write (R166 lesson working as designed).

## Verification

- Merge-tree `0c67764` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `a0541c9e…`. Merge-tree at the R193
  content head `11a935f` vs `f3db6b3`: exit 0, tree
  `0f587922…`.
- Live PR state: API connector MCP read ~04:44 JST (first read artifact 92.521 ký tự / 2 U+FFFD — R175/R182-style read-path artifact; immediate re-read byte-exact 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `0c67764`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-22T18:49:16Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~04:44 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R193 block (`0c67764..11a935f`) 3 paths / 0 violations
  (index + body v2 + R193 checker); cumulative at the R193 content
  commit `11a935f` 2972 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `11a935f`).
  Merge-tree at the R193 content head `11a935f` vs `f3db6b3`: exit 0,
  tree `0f587922…`.
- Transient notes: the first MCP pull read this round carried the
  R175/R182-style artifact (92.521 ký tự, 2 U+FFFD) — the immediate re-read
  was byte-exact (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD), so a first
  artifact read means re-read, not a changed live body. The R192 payload's own head line recorded mergeable
  unstable at `0c67764` at its preparation (CI still running on the new
  head); this round's fresh read shows clean at the same head after CI
  finished — the payload's unstable wording was correct at its
  preparation time, not a defect. No proxy failure on `git ls-remote` /
  fetch this round. No MCP parameter slip: both reads used
  the correct names first try (`pullNumber`, `issue_number`). No
  rate-limit 403 on any MCP read this round.
- Ceiling discipline: the R192 payload JSON measured 122.235 byte
  (as-prepared; cmp with its `.bak` byte-identical this round, so no
  main-flow refresh changed it) vs the 131.072-byte transport ceiling
  (8.837 byte headroom). The projected R193 payload JSON is ~122,300 byte
  (measured exactly at payload build, after push). Body v2 is now 104.959
  ký tự (< 105.000) — 41 ký tự of headroom. R193 warning:
  headroom is now 41 ký tự; the next round must collapse R112 (735 ký tự
  → ~250) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R193 body
v2 (R192 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r193.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R193 push (title
ending "+ R193", built by replacing the "+ R140" suffix — not appending;
body = body v2 R193 in repo, head line refreshed to head after R193 push).
This run started ~04:40 JST — PAST working hours (09:00–21:30 JST), so the
R193 payload is HELD FOR WORKING HOURS by the main flow (not presented tonight — like R142/R164–R173/R186/R187/R188/R189/R190/R191/R192). Do not present the superseded R192 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191 and R192 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R193: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
