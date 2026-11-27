# MEDIA-02 — PR #119 Body Restructure R214: delivery index + body v2 coverage to `1afb41e`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `1afb41e` (PR119 BODY RESTRUCTURE R213 report). Content commit: `2ce013b`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R214 does

R213 left the disclosed gap: the delivery index covered 615 commits to
`381865f`; R213's own 2 commits were to fold in at R214. The R213 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh direct-API read ~06:40 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T20:50:57Z — bumped by the R213 push updating the PR head, body bytes
unchanged). The R213 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~06:40 JST, read-only —
`issue_read get_comments` pages 1+2 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read with curl as cross-check): the MCP read path returned the clean body
this round and the direct read agreed — issue #116 34 comments, PR #119 head
`1afb41e`, 617 commits / 3034 files / +291,773, mergeable_state clean at
`1afb41e`, live body R140 92.520 ký tự sha `ddbe32ff`.

Fresh derivation at `1afb41e` (~06:40 JST): `git rev-list --count
cf17178..1afb41e` = 617 commits, `git diff --name-only` = 3034 files,
`--shortstat` = 291773 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `1afb41e` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `767b3396…`. No re-fetch was needed before applying: the run fetched at ~06:40 JST
(the run start) and the remote head was still `1afb41e`, integration still `f3db6b3` — no
intervening push; the API read ~06:40 JST independently confirmed head `1afb41e`.

R214 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `1afb41e` (617 commits / 3034 files /
  291773 additions; the fresh git derivation at `1afb41e`, the fresh API
  read ~06:40 JST, and the merge-tree cross-check at `1afb41e` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `381865f..1afb41e`: 5 paths, 713 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R213
  (`c77587a`/`1afb41e`), recording that its payload was prepared after
  push ~05:51 JST (104.722 ký tự, sha `d8725150`; JSON 120.897 byte < trần 131.072 — còn 10.175 byte, bản giữ tại
  `.bak-prepost-20261124` — R214 sao lưu, sha256 `6118da78…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's direct API read and MCP read, both clean:
  description structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này qua API trực tiếp, 0 U+FFFD, updated_at 2026-11-23T20:50:57Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~06:40 JST).
  The index now covers every block through `1afb41e`; R214's
  own 2 commits fold in at the next index update (R215), disclosed in the
  index itself. The R214 note was appended after the R213 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `1afb41e` · 617 · 3034 (with the fresh git derivation at `1afb41e`,
  the fresh API read ~06:40 JST, and the fresh merge-tree cross-check at
  `1afb41e`), plus the R213 paragraph in "Khối mới nhất" (254 ký tự,
  marked chưa đăng — live body is R140) and the R214 note. The stale index
  reference in "Về bản mô tả này" (head `381865f`) is also fixed to
  `1afb41e`, and the title line is extended to R213 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R213 warning —
  applied with a measured correction, SINGLE): the R91 paragraph (494 ký tự — measured this
  round) is
  collapsed to one 215-ký-tự compact line (full detail stays in the
  delivery index) — the new R213 paragraph was 254 ký tự, so
  the body is 104.795 ký tự — net +38 vs R213 despite the new R213 paragraph, headroom 205 ký tự. The dry-run first projected 104.795 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  Paragraph order: the R213 paragraph sits directly after R212
  (ascending full-paragraph order R166..R213), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R214 (owner tap) — the R140 body v2 now live
  is the base; only the R213 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r214_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R213 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R213 and R214 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R213 (75 compact lines R91–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.795 ký tự),
  a check that the R213 paragraph sits directly after R212
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R213 note clean).
  New this round: the R212-row regression guard (cumulative must be 3032,
  re-derived from git at `c77587a`), the R213-row guard (cumulative must
  cite 3035 — 3034 at `1afb41e` + 1 new checker in the R214 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R213, range R91–R165, list complete through R213, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 44/44**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R214_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R213) with the full COVER
  SHA verified intact (definition + docstring, both
  `1afb41ecffa6bc62f81923e998a542f826197585` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `381865f` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R212-row guard string citing "3031 at 381865f", legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.795 ký tự and the apply wrote on
  the first attempt at 104.795 ký tự with 205 ký tự of headroom; the idempotency re-run
  after apply reported already-applied changed: 0 — verified.
  Correction caught before the report commit: the R213 row's cumulative figure was drafted as 3035 (3034 at
  `1afb41e` + 1 new checker) and the true diff at the R214 content
  commit is 3035 — verified by `git diff --name-only cf17178..2ce013b` = 3035
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).

## R214 robustness note — headroom now 205 chars

The R213 warning left 243 ký tự of headroom, so this round compacted
the R91 paragraph (494 ký tự → 215) before adding the new R213 paragraph
(254 ký tự). The body is now 104.795 ký tự — net +38 vs R213 — with
205 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R215 warning: headroom is 205 ký tự; at the current +38/round growth a
single compaction per round holds ~5 rounds — keep compacting one
paragraph per round (next: R90). At the current net +38/round the margin
holds only with a steady single compaction; one full-paragraph compaction
per round (~−279) is sustainable again (full paragraphs remaining R166..R213 = 48;
compact block R91–R165 = 75 lines).
No ĐÍNH CHÍNH this round: R213's committed content verified correct —
the committed index at `1afb41e` carries the R211 row at cumulative 3029
(verified via `git show 1afb41e:...` this round) and the R212 row at 3032
(re-derived by the new checker from git at `c77587a`); no uncommitted
working-tree fix was left behind by R213 (the working tree was clean at this
run's start and the fetch found no intervening push).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (104.795 projected; apply wrote 104.795 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213 — the R213 row's 3035 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first, not only
assert the OLD state — otherwise the re-run crashes on its own
pre-condition after a successful apply (R203/R207 lesson — re-run this
round reports already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two agreeing read paths settle
the live body faster than one mangled read did in R209 — the MCP path returned
the clean body this round and the direct curl read agreed byte-exact
(92.520, sha `ddbe32ff`); when two read paths disagree on one character,
cross-check with a second path before claiming the live body changed. (6) A payload backup the authoring
round did not make must be disclosed as made by the folding round, not claimed as the author's — R213's
payload had no `.bak` copy when R214 started; R214 copied it and verified sha256 identical
(`6118da78…` both), and the R213 row records the copy as R214's, not R213's.

## Verification

- Merge-tree `1afb41e` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `767b3396…`. Merge-tree at the R214
  content head `2ce013b` vs `f3db6b3`: exit 0, tree
  `8eacbc16…`.
- Live PR state: API read twice this round (~06:40 JST) — MCP read path
  returned the clean body this round and the direct
  public-API read (curl) agreed — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `1afb41e`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T20:50:57Z — bumped by the R213 push updating the PR head, body
  bytes unchanged); commits 617, changed_files 3034, additions 291773
  (API agrees with the fresh git derivation; the `deletions` key is 0 in
  the direct API response — git shows 0 deletions; the MCP response also
  returns `mergeable: null` — the direct read returns `mergeable: true`,
  mergeable_state clean is the operative field); mergeable_state clean at
  `1afb41e` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R214 block (`1afb41e..2ce013b`) 3 paths / 0 violations
  (index + body v2 + R214 checker); cumulative at the R214 content
  commit `2ce013b` 3035 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `2ce013b`).
  Merge-tree at the R214 content head `2ce013b` vs `f3db6b3`: exit 0,
  tree `8eacbc16…`.
- Transient notes: this round's `git fetch` at ~06:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (clean read, no mangling — `pull_request_read` takes `pullNumber`, not
  `pull_number` — parameter-name lesson carried from R211; `issue_read`
  takes `issue_number`, not `issueNumber` — the first attempt this round
  failed fast on the wrong name and the retry with `issue_number` worked).
  The R213 payload's own head line recorded
  mergeable clean at `381865f` at its preparation and clean at
  `1afb41e`; this round's API read confirms clean at `1afb41e`.
- Ceiling discipline: the R213 payload JSON measured 120.897 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (10.175 byte headroom). The projected R214 payload JSON is ~121,300 byte
  (measured exactly at payload build, after push). Body v2 is now 104.795
  ký tự (< 105.000) — 205 ký tự of headroom. R214 warning:
  headroom is now 205 ký tự; a single compaction per round holds ~5 rounds
  at +38/round; the next round compacts R90.

## Next

Posting round (owner tap): PR #119 description refresh to the R214 body
v2 (R213 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r214.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R214 push (title
ending "+ R214", built by replacing the "+ R140" suffix — not appending;
body = body v2 R214 in repo, head line refreshed to head after R214 push).
This run started ~06:40 JST — BEFORE working hours (09:00–21:30 JST), so the
R214 payload is HELD FOR WORKING HOURS (not presented, like R142/R164–R197/R207–R213). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R213 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212 and R213 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R214: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
