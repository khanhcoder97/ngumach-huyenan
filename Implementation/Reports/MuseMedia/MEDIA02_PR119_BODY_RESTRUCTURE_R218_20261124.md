# MEDIA-02 — PR #119 Body Restructure R218: delivery index + body v2 coverage to `0a4d05a`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `0a4d05a` (PR119 BODY RESTRUCTURE R217 report). Content commit: `a24895e`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R218 does

R217 left the disclosed gap: the delivery index covered 623 commits to
`0de54fb`; R217's own 2 commits were to fold in at R218. The R217 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API reads ~10:40 JST, MCP + direct curl: PR title still ends "+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD on the direct read, updated_at 2026-11-24T00:50:49Z — bumped by the R217 push updating the PR head, body bytes
unchanged). The R217 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh reads agree: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~10:40 JST, read-only —
`issue_read get_comments` page 1 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read of the issue comments and of the PR with curl as cross-check): the MCP read
returned the body with 1 character "Ă" mangled into 2 U+FFFD (92.521 ký tự — the same transport
mangle as R209/R215, NOT a body change) and the direct read returned the CLEAN body (92.520 ký tự, sha
`ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — the direct read is authoritative
when the two disagree by exactly the mangled character, as in R209/R215. The issue-comments direct read also
succeeded (34 comments, latest `6862732081`) and agrees with the MCP read
(MCP returns page 1 only, 30 comments — the remaining 4 are paginated, as
in earlier rounds). PR head `0a4d05a`,
625 commits / 3046 files / +294.785, mergeable_state clean at `0a4d05a` (mergeable true via direct read,
mergeable key absent via MCP — recorded honestly, not papered over).

Fresh derivation at `0a4d05a` (~10:40 JST): `git rev-list --count
cf17178..0a4d05a` = 625 commits, `git diff --name-only` = 3046 files,
`--shortstat` = 294785 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `0a4d05a` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `fd5eba7a…`. No re-fetch was needed before applying: the run fetched at ~10:40 JST
(the run start) and the remote head was still `0a4d05a`, integration still `f3db6b3` — no
intervening push; the API read ~10:40 JST independently confirmed head `0a4d05a`.

R218 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `0a4d05a` (625 commits / 3046 files /
  294785 additions; the fresh git derivation at `0a4d05a`, the fresh API
  reads ~10:40 JST, and the merge-tree cross-check at `0a4d05a` are cited,
  with the honest mergeable reading disclosed above — MCP mangled 1 ký tự, direct read clean;
  live body R140; delta `0de54fb..0a4d05a`: 5 paths, 798 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R217
  (`af6e949`/`0a4d05a`), recording that its payload was prepared after
  push ~09:52 JST (104.510 ký tự, sha `f12748fe`; JSON 120.421 byte < trần 131.072 — còn 10.651 byte, bản giữ tại
  `.bak-prepost-20261124` — R217 made its own backup, sha256 `978f3e22…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's MCP + direct reads: description structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — lần đọc MCP đầu méo 1 ký tự "Ă" thành 2 U+FFFD như R209/R215, đọc trực tiếp byte-exact khớp, 0 U+FFFD, updated_at 2026-11-24T00:50:49Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API reads ~10:40 JST).
  The index now covers every block through `0a4d05a`; R218's
  own 2 commits fold in at the next index update (R219), disclosed in the
  index itself. The R218 note was appended after the R217 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `0a4d05a` · 625 · 3046 (with the fresh git derivation at `0a4d05a`,
  the fresh API reads ~10:40 JST, and the fresh merge-tree cross-check at
  `0a4d05a`), plus the R217 paragraph in "Khối mới nhất" (254 ký tự,
  marked chưa đăng — live body is R140) and the R218 note. The stale index
  reference in "Về bản mô tả này" (head `0de54fb`) is also fixed to
  `0a4d05a`, and the title line is extended to R217 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R217 warning —
  applied with a measured correction, DOUBLE): the R85 + R84 paragraphs (494 and 530 ký tự — measured this
  round) are
  collapsed to one 208-ký-tự compact line each (full detail stays in the
  delivery index) — the new R217 paragraph was 254 ký tự, so
  the body is 104.362 ký tự — net −187 vs R217 despite the new R217 paragraph, headroom 638 ký tự. The dry-run first projected 104.362 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  Paragraph order: the R217 paragraph sits directly after R216
  (ascending full-paragraph order R166..R217), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R218 (owner tap) — the R140 body v2 now live
  is the base; only the R217 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r218_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R217 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R217 and R218 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R217 (82 compact lines R84–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.362 ký tự),
  a check that the R217 paragraph sits directly after R216
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R217 note clean).
  New this round: the R216-row regression guard (cumulative must be 3044,
  re-derived from git at `af6e949`), the R217-row guard (cumulative must
  cite 3047 — 3046 at `0a4d05a` + 1 new checker in the R218 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R217, range R84–R165, list complete through R217, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 52/52**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R218_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R217) with the full COVER
  SHA verified intact (definition + docstring, both
  `0a4d05acb74083f0177a8c04bcb71d8664ab9d48` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `0de54fb` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R216-row guard string citing "3043 at 0de54fb", legitimate; plus 1
  `1e564a2` in the R215-row guard and 1 `3de99c9` in the R214-row guard, legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.362 ký tự and the apply wrote on
  the first attempt at 104.362 ký tự with 638 ký tự of headroom; the idempotency re-run
  after apply initially crashed on TWO of its own checks — the head-line replace looked for the OLD
  prefix (which carries the old head value and no longer exists after apply) and the Ghi-chú
  already-applied check forgot the trailing period (line ends "/R217.", not "/R217") — both fixed
  in the script (check NEW state first, R203/R207 lesson applied to every edit, not just some),
  re-run reports already-applied changed: 0 — verified. No content was changed by those two fixes;
  the first apply had already written the correct bytes.
  Correction caught before the report commit: the R217 row's cumulative figure was drafted as 3047 (3046 at
  `0a4d05a` + 1 new checker) and the true diff at the R218 content
  commit is 3047 — verified by `git diff --name-only cf17178..a24895e` = 3047
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH this round: R217's committed content verified correct —
  the committed index at `0a4d05a` carries the R215 row at cumulative 3041
  (re-derived by the new checker from git at `dd19bba`) and the R216 row at 3044
  (re-derived from git at `af6e949`); no uncommitted
  working-tree fix was left behind by R217 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R218 robustness note — headroom now 638 chars

The R217 warning left 451 ký tự of headroom, so this round compacted
TWO paragraphs (R85 + R84, 494 + 530 ký tự → 208 each) before adding the new R217 paragraph
(254 ký tự). The body is now 104.362 ký tự — net −187 vs R217 — with
638 ký tự of headroom. The double compaction bought back 608 ký tự against the
254-ký-tự new paragraph, so the margin now holds while two paragraphs are
compacted per round; the head line is the variable cost (it grew to 1.168 ký tự this round
as the MCP-mangle disclosure was added — trim it if it keeps growing). The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R219 warning: headroom is 638 ký tự; compact R83 + R82 next (or trim the
head line hard). At the current net −187/round the margin is recovering,
but only while the double compaction continues (full paragraphs remaining R166..R217 = 52;
compact block R84–R165 = 82 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (104.362 projected; apply wrote 104.362 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217 — the R217 row's 3047 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — the head-line replace crashed because its lookup prefix itself carried the OLD head value,
and the Ghi-chú check failed on a trailing period (R203/R207 lesson, now applied to all edits; re-run reports
already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two read paths settle
the live body faster than one mangled read did in R209 — the MCP path mangled 1 ký tự "Ă" into 2 U+FFFD
this round (92.521 chars) and the direct curl read returned the clean body (92.520, sha `ddbe32ff`) — the direct
read is authoritative when the two disagree by exactly the mangled character; record both, not one.
(6) A payload backup the authoring
round made must be verified, not re-claimed — R217's payload `.bak` copy
existed when R218 started; R218 verified sha256 identical
(`978f3e22…` both) and the R217 row records the copy as R217's, not R218's.

## Verification

- Merge-tree `0a4d05a` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `fd5eba7a…`. Merge-tree at the R218
  content head `a24895e` vs `f3db6b3`: exit 0,
  tree `81a5c92d…`.
- Live PR state: API read twice this round (~10:40 JST) — MCP read
  mangled 1 ký tự "Ă" into 2 U+FFFD (92.521 ký tự — transport mangle, NOT a body change) and direct curl read
  clean byte-exact (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `0a4d05a`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-24T00:50:49Z — bumped by the R217 push updating the PR head, body
  bytes unchanged); commits 625, changed_files 3046, additions 294785
  (API agrees with the fresh git derivation; the `deletions` key is absent in
  the direct API response — git shows 0 deletions; the MCP response has no
  `mergeable` key this round while the direct read returns `mergeable: true`; mergeable_state clean is the operative field); mergeable_state clean at
  `0a4d05a` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API + direct curl of comments — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R218 block (`0a4d05a..a24895e`) 3 paths / 0 violations
  (index + body v2 + R218 checker); cumulative at the R218 content
  commit `a24895e` 3047 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `a24895e`).
  Merge-tree at the R218 content head `a24895e` vs `f3db6b3`: exit 0,
  tree `81a5c92d…`.
- Transient notes: this round's `git fetch` at ~10:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (first PR read mangled 1 ký tự — see live-read note; `pull_request_read` takes `pullNumber`, not
  `pull_number` — parameter-name lesson carried from R211; `issue_read`
  takes `issue_number`, not `issueNumber`). No execution-risk flag on any
  git/script command this round (unlike R211/R213). The R217 payload's own head line recorded
  mergeable clean at `0de54fb` at its preparation and clean at
  `0a4d05a`; this round's API read confirms clean at `0a4d05a`. One benign
  warning: the `post-commit` git-lfs hook printed "git-lfs was not found on
  your path" at the content commit (this shell lacked `~/workspace/tools-bin`
  on PATH); the commit itself succeeded and the files are text-only, so no
  LFS smudge was involved — the push below uses the documented env.
- Ceiling discipline: the R217 payload JSON measured 120.421 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API reads)
  vs the 131.072-byte transport ceiling
  (10.651 byte headroom). The projected R218 payload JSON is ~121,000 byte
  (measured exactly at payload build, after push). Body v2 is now 104.362
  ký tự (< 105.000) — 638 ký tự of headroom. R218 warning:
  headroom is now 638 ký tự; the double compaction must continue next round
  (R83 + R82) or the head line must be trimmed.

## Next

Posting round (owner tap): PR #119 description refresh to the R218 body
v2 (R217 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r218.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R218 push (title
ending "+ R218", built by replacing the "+ R140" suffix — not appending;
body = body v2 R218 in repo, head line refreshed to head after R218 push).
This run started ~10:40 JST — INSIDE working hours (09:00–21:30 JST), so the
R218 payload is READY FOR WORKING HOURS (unlike R142/R164–R197/R207–R216,
which were held because they started before 09:00). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R217 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216 and R217 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R218: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
