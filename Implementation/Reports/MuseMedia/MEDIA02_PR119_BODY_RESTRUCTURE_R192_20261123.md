# MEDIA-02 — PR #119 Body Restructure R192: delivery index + body v2 coverage to `77e5df1`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `77e5df1` (PR119 BODY RESTRUCTURE R191 report). Content commit: `7e80036`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R192 does

R191 left the disclosed gap: the delivery index covered 571 commits to
`6d65e75`; R191's own 2 commits were to fold in at R192. The R191 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~03:44 JST, first read byte-exact:
92.520 ký tự, 0 U+FFFD, sha `ddbe32ff` — no R175-style read-path artifact this round) show the live PR title ends
"+ R140", head `77e5df1`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-22T17:48:10Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R191 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~03:44 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `77e5df1` (~03:44 JST): `git rev-list --count
cf17178..77e5df1` = 573 commits, `git diff --name-only` = 2968 files,
`--shortstat` = 279949 insertions, 0 deletions. `git merge-tree
--write-tree` `77e5df1` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `9d863db7…`. Like R191, this round DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `77e5df1` (CI finished since the R191 push at ~02:48 JST; the R191 payload's own head line had
recorded mergeable unstable at preparation time, when CI was still running on the new head — see Transient notes).

R192 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `77e5df1` (573 commits / 2968 files /
  279949 additions; the fresh git derivation at `77e5df1`, the fresh API
  read ~03:44 JST, and the merge-tree cross-check at `77e5df1` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `6d65e75..77e5df1`: 5 paths, 413 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R191
  (`d105f51`/`77e5df1`), recording that its payload was prepared after
  push ~02:49 JST (105.005 ký tự, sha `21207822`, mergeable_state unstable tại
  `77e5df1` lúc chuẩn bị, lần clean gần nhất tại `6d65e75`; JSON 122.297 byte < trần 131.072 — còn 8.775 byte, bản giữ tại
  `.bak-prepost-20261123`), that it was NOT refreshed by the main flow
  (cmp with its `.bak` byte-identical this round: payload sha `21207822`,
  105.005 ký tự), that it was NOT posted
  — live body still R140 (verified by this round's API read: first read byte-exact 92.520 ký tự, sha
  `ddbe32ff`, 0 U+FFFD) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; connector MCP get_comments page 1,
  perPage 100). The index now covers every block through `77e5df1`; R192's
  own 2 commits fold in at the next index update (R193), disclosed in the
  index itself. The R192 note was appended after the R191 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Row-convention verification** (done this round before writing the
  R191 row): a table row's "cumulative N paths" is the diff path count at
  the AUTHORING round's content commit — R188 row 2960 == `45142ad`
  (R189 content), R189 row 2963 == `ed21eb2` (R190 content), R190 row
  2966 == `d105f51` (R191 content), all re-derived from git this round.
  The R191 row therefore cites cumulative 2969 paths — the diff count at
  the R192 content commit `7e80036`, verified after the commit (not
  predicted blindly). No correction to any earlier row was needed.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `77e5df1` · 573 · 2968 (with the fresh git derivation at `77e5df1`,
  the fresh API read ~03:44 JST, and the fresh merge-tree cross-check at
  `77e5df1`), plus the R191 paragraph in "Khối mới nhất" (422 ký tự,
  marked chưa đăng — live body is R140) and the R192 note. The stale index
  reference in "Về bản mô tả này" (head `6d65e75`) is also fixed to
  `77e5df1`, and the title line is extended to R191 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R191 warning —
  applied with a margin): the R114 paragraph (735 ký tự — measured this
  round) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R191 paragraph was 422 ký tự, so
  the body is 104.957 ký tự — net −13 vs R191 despite the new R191
  paragraph, headroom 43 ký tự.
  Paragraph order: the R191 paragraph sits directly after R190
  (ascending full-paragraph order R166..R191), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R192 (owner tap) — the R140 body v2 now live
  is the base; only the R191 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r192_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R191 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R191 and R192 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R191 (52 compact lines R114–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.957 ký tự),
  and a check that the R191 paragraph sits directly after R190
  (ascending full-paragraph order). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R192_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R191) with the full COVER
  SHA verified intact (12 occurrences) and a stale-reference grep (0 stale
  `6d65e75`/`571`/`2965`/`279547`/`1eccdf56`/`4380848`/`5cf5000`
  references in the checker — the R191 values; the `45142ad`/`ed21eb2`/`d105f51` hits are
  intentional citations inside the docstring's row-convention note,
  verified from git this round) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation measured 104.957 ký tự with 43 ký tự of headroom and the apply wrote on
  the first attempt; the idempotency re-run reported changed: 0 after a
  guard fix (see lesson below). The content commit
  staged exactly the usual 3 files (index + body v2 + checker); the
  validation JSON rides with the report commit as in every prior round.

## R192 robustness note — headroom now 43 chars

The R191 warning left 30 ký tự of headroom, so this round compacted
the R114 paragraph (735 ký tự → 239) before adding the new R191 paragraph
(422 ký tự). The body is now 104.957 ký tự — net −13 vs R191 — with
43 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R193 warning: headroom is 43 ký tự; the next round must collapse R113
(735 ký tự → ~250) and keep the new paragraph tight (≤ ~460 ký tự) — the
R113 compaction alone frees ~485 ký tự, restoring comfortable headroom.
At the current net −13/round the margin would hold for several rounds
even without compaction; one full-paragraph compaction per round (~−485) keeps
the discipline sustainable (full paragraphs remaining R166..R191 = 26;
compact block R114–R165 = 52 lines).
Lesson this round: the edit script's idempotency guard (`replace_once`
returning 0 when the NEW text is already present) checked `new in text
and old not in text` — that fails for insert/append patterns, where the
new text CONTAINS the old anchor as a substring, so the first re-run
re-inserted the R191 paragraph and tripped the budget assert (projected
105.405) before any write — files untouched. The guard now checks
`new in text` first, unconditionally; the re-run then reported changed: 0.
The R191 payload body ran 105.005 ký tự — 5 over the self-set ceiling —
because its post-push head-line refresh added ~35 chars; this round's
repo body (104.957) leaves 43 chars, so the R192 payload should land at
or under 105.000 after its own refresh — verified at payload build.

## Verification

- Merge-tree `77e5df1` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `9d863db7…`. Merge-tree at the R192
  content head `7e80036` vs `f3db6b3`: exit 0, tree
  `6693865c…`.
- Live PR state: API connector MCP read ~03:44 JST (first read byte-exact, 92.520 ký tự,
  0 U+FFFD — no R175-style artifact this round) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `77e5df1`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-22T17:48:10Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~03:44 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R192 block (`77e5df1..7e80036`) 3 paths / 0 violations
  (index + body v2 + R192 checker); cumulative at the R192 content
  commit `7e80036` 2969 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `7e80036`).
  Merge-tree at the R192 content head `7e80036` vs `f3db6b3`: exit 0,
  tree `6693865c…`.
- Transient notes: the first MCP pull read this round was byte-exact
  (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — no R175-style artifact, no
  re-read needed. The R191 payload's own head line recorded mergeable
  unstable at `77e5df1` at its preparation (CI still running on the new
  head); this round's fresh read shows clean at the same head after CI
  finished — the payload's unstable wording was correct at its
  preparation time, not a defect. No proxy failure on `git ls-remote` /
  fetch this round. No MCP parameter slip: both reads used
  the correct names first try (`pullNumber`, `issue_number`). No
  rate-limit 403 on any MCP read this round.
- Ceiling discipline: the R191 payload JSON measured 122.297 byte
  (as-prepared; cmp with its `.bak` byte-identical this round, so no
  main-flow refresh changed it) vs the 131.072-byte transport ceiling
  (8.775 byte headroom). The projected R192 payload JSON is ~122,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.957
  ký tự (< 105.000) — 43 ký tự of headroom. R192 warning:
  headroom is now 43 ký tự; the next round must collapse R113 (735 ký tự
  → ~250) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R192 body
v2 (R191 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r192.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R192 push (title
ending "+ R192", built by replacing the "+ R140" suffix — not appending;
body = body v2 R192 in repo, head line refreshed to head after R192 push).
This run started ~03:40 JST — PAST working hours (09:00–21:30 JST), so the
R192 payload is HELD FOR WORKING HOURS by the main flow (not presented tonight — like R142/R164–R173/R186/R187/R188/R189/R190/R191). Do not present the superseded R191 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190 and R191 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R192: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
