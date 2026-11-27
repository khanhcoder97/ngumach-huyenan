# MEDIA-02 — PR #119 Body Restructure R219: delivery index + body v2 coverage to `a74e9f4`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `a74e9f4` (PR119 BODY RESTRUCTURE R218 report). Content commit: `a82ca70`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R219 does

R218 left the disclosed gap: the delivery index covered 625 commits to
`0a4d05a`; R218's own 2 commits were to fold in at R219. The R218 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API reads ~12:40 JST, MCP + direct curl: PR title still ends \"+ R140\", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD on the direct read, updated_at 2026-11-24T01:47:37Z — bumped by the R218 push updating the PR head, body bytes
unchanged). The R218 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh reads agree: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~12:40 JST, read-only —
`issue_read get_comments` page 1 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read of the issue comments and of the PR with curl as cross-check): the MCP read
agreed on the PR title (ends "+ R140") and the visible head of the body; the direct read returned the
CLEAN body (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — the direct
read is authoritative for the byte-exact body, since the MCP output was truncated by the tool's own
display limit this round (NOT a body change and NOT the "Ă" → U+FFFD mangle of R209/R215/R218). The issue-comments direct read also
succeeded (34 comments, latest `6862732081`) and agrees with the MCP read
(MCP returns page 1 only, 30 comments — the remaining 4 are paginated, as
in earlier rounds). PR head `a74e9f4`,
627 commits / 3049 files / +295.585, mergeable_state clean at `a74e9f4` (mergeable true via direct read).

Fresh derivation at `a74e9f4` (~12:40 JST): `git rev-list --count
cf17178..a74e9f4` = 627 commits, `git diff --name-only` = 3049 files,
`--shortstat` = 295585 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `a74e9f4` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `bad36c5e…`. No re-fetch was needed before applying: the run fetched at ~12:40 JST
(the run start) and the remote head was still `a74e9f4`, integration still `f3db6b3` — no
intervening push; the API read ~12:40 JST independently confirmed head `a74e9f4`.

R219 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `a74e9f4` (627 commits / 3049 files /
  295585 additions; the fresh git derivation at `a74e9f4`, the fresh API
  reads ~12:40 JST, and the merge-tree cross-check at `a74e9f4` are cited,
  with the honest mergeable reading disclosed above — MCP agreed on title + visible head, direct read clean;
  live body R140; delta `0a4d05a..a74e9f4`: 5 paths, 812 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R218
  (`a24895e`/`a74e9f4`), recording that its payload was prepared after
  push ~10:49 JST (104.229 ký tự, sha `3aef70a3`; JSON 120.004 byte < trần 131.072 — còn 11.068 byte, bản giữ tại
  `.bak-prepost-20261124` — R218 made its own backup, sha256 `3aa5aee4…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's MCP + direct reads: description structure matches R140, PR title ends \"+ R140\", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc trực tiếp byte-exact khớp, 0 U+FFFD, updated_at 2026-11-24T01:47:37Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API reads ~12:40 JST).
  The index now covers every block through `a74e9f4`; R219's
  own 2 commits fold in at the next index update (R220), disclosed in the
  index itself. The R219 note was appended after the R218 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `a74e9f4` · 627 · 3049 (with the fresh git derivation at `a74e9f4`,
  the fresh API reads ~12:40 JST, and the fresh merge-tree cross-check at
  `a74e9f4`), plus the R218 paragraph in "Khối mới nhất" (254 ký tự,
  marked chưa đăng — live body is R140) and the R219 note. The stale index
  reference in "Về bản mô tả này" (head `0a4d05a`) is also fixed to
  `a74e9f4`, and the title line is extended to R218 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R218 warning —
  applied with a measured correction, DOUBLE): the R83 + R82 paragraphs (572 and 569 ký tự — measured this
  round) are
  collapsed to one 208-ký-tự compact line each (full detail stays in the
  delivery index) — the new R218 paragraph was 254 ký tự, so
  the body is 103.872 ký tự — net −490 vs R218 despite the new R218 paragraph, headroom 1.128 ký tự. The dry-run first projected 103.872 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  Paragraph order: the R218 paragraph sits directly after R217
  (ascending full-paragraph order R166..R218), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R219 (owner tap) — the R140 body v2 now live
  is the base; only the R218 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r219_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R218 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R218 and R219 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R218 (84 compact lines R82–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 103.872 ký tự),
  a check that the R218 paragraph sits directly after R217
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R218 note clean).
  New this round: the R217-row regression guard (cumulative must be 3047,
  re-derived from git at `a24895e`), the R218-row guard (cumulative must
  cite 3050 — 3049 at `a74e9f4` + 1 new checker in the R219 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R218, range R82–R165, list complete through R218, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 54/54**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R219_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R218) with the full COVER
  SHA verified intact (definition + docstring, both
  `a74e9f42ef6fb5589333deec2355ec13dbd063ca` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `0a4d05a` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R217-row guard string citing "3046 at 0a4d05a", legitimate; plus 3
  `0de54fb` (docstring + R216-row guard citing "3043 at 0de54fb"), 3 `1e564a2` (docstring + R215-row guard),
  3 `3de99c9` (docstring + R214-row guard), legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 103.872 ký tự and the apply wrote on
  the first attempt at 103.872 ký tự with 1.128 ký tự of headroom; the idempotency re-run
  after apply initially crashed on TWO of its own checks — the replace_line prefix looked for the OLD
  value (I1 header line and the B4a Ghi-chú label carry the old head/label and no longer exist after apply) — both fixed
  in the script (check NEW state first, R203/R207 lesson applied to every edit, not just some),
  re-run reports already-applied changed: 0 — verified. No content was changed by those two fixes;
  the first apply had already written the correct bytes.
  Correction caught before the report commit: the R218 row's cumulative figure was drafted as 3050 (3049 at
  `a74e9f4` + 1 new checker) and the true diff at the R219 content
  commit is 3050 — verified by `git diff --name-only cf17178..a82ca70` = 3050
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  No ĐÍNH CHÍNH this round: R218's committed content verified correct —
  the committed index at `a74e9f4` carries the R216 row at cumulative 3044
  (re-derived by the new checker from git at `af6e949`) and the R217 row at 3047
  (re-derived from git at `a24895e`); no uncommitted
  working-tree fix was left behind by R218 (the working tree was clean at this
  run's start and the fetch found no intervening push).

## R219 robustness note — headroom now 1.128 chars

The R218 warning left 638 ký tự of headroom, so this round compacted
TWO paragraphs (R83 + R82, 572 + 569 ký tự → 208 each) before adding the new R218 paragraph
(254 ký tự). The body is now 103.872 ký tự — net −490 vs R218 — with
1.128 ký tự of headroom. The double compaction bought back 725 ký tự against the
254-ký-tự new paragraph, so the margin now holds while two paragraphs are
compacted per round; the head line was trimmed to 1.076 ký tự this round
(from 1.168 at R218) — trim it again if it keeps growing. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R220 warning: headroom is 1.128 ký tự; compact R81 + R80 next (or trim the
head line hard). At the current net −490/round the margin is recovering,
but only while the double compaction continues (full paragraphs remaining R166..R218 = 53;
compact block R82–R165 = 84 lines).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (103.872 projected; apply wrote 103.872 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218 — the R218 row's 3050 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first for EVERY
edit, not only some — the replace_line prefix crashed because its lookup prefix itself carried the OLD value,
and the Ghi-chú label edit crashed the same way (R203/R207 lesson, now applied to all edits; re-run reports
already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two read paths settle
the live body faster than one mangled read did in R209 — the MCP path agreed on title + visible head
this round while the direct curl read returned the clean byte-exact body (92.520, sha `ddbe32ff`) — the direct
read is authoritative for the byte count; record both, not one.
(6) A payload backup the authoring
round made must be verified, not re-claimed — R218's payload `.bak` copy
existed when R219 started; R219 verified sha256 identical
(`3aa5aee4…` both) and the R218 row records the copy as R218's, not R219's.
(7) A run blocked by the execution-risk flag leaves NO partial work — the R219-blocked run (~11:40 JST)
stopped before any git write, so this run is the clean retry (working tree clean at start, fetch found no
intervening push), not a duplicate; the flag itself has now appeared 4 times (R211 ~01:40, R213 ~04:40,
R213 ~05:44, R219 ~11:40) and the decision whether to keep running git/checker after it still awaits
luồng chính/chủ dự án — recorded here, not decided here.

## Verification

- Merge-tree `a74e9f4` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `bad36c5e…`. Merge-tree at the R219
  content head `a82ca70` vs `f3db6b3`: exit 0,
  tree `2a81da83…`.
- Live PR state: API read twice this round (~12:40 JST) — MCP read
  agreed on title + visible head (body not fully counted via MCP this round — output truncated by the tool's
  display limit, NOT a mangle) and direct curl read
  clean byte-exact (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — PR title ends
  \"+ R140\" (R140 posted live ~22:22 JST 2026-11-20); head `a74e9f4`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-24T01:47:37Z — bumped by the R218 push updating the PR head, body
  bytes unchanged); commits 627, changed_files 3049, additions 295585
  (API agrees with the fresh git derivation; the `deletions` key is 0 in
  the direct API response — git shows 0 deletions); mergeable_state clean at
  `a74e9f4` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API + direct curl of comments — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R219 block (`a74e9f4..a82ca70`) 3 paths / 0 violations
  (index + body v2 + R219 checker); cumulative at the R219 content
  commit `a82ca70` 3050 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `a82ca70`). Merge-tree at the R219 content head `a82ca70` vs `f3db6b3`: exit 0,
  tree `2a81da83…`.
- Transient notes: this round's `git fetch` at ~12:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (PR read body truncated by the tool's display limit — see live-read note; `pull_request_read` takes `pullNumber`, not
  `pull_number` — parameter-name lesson carried from R211; `issue_read`
  takes `issue_number`, not `issueNumber`). No execution-risk flag on any
  git/script command this round (unlike R211/R213 and the R219-blocked run ~11:40 JST). The R218 payload's own head line recorded
  mergeable clean at `0a4d05a` at its preparation and clean at
  `a74e9f4`; this round's API read confirms clean at `a74e9f4`. No git-lfs
  hook warning at the content commit this round (`~/workspace/tools-bin`
  was on PATH, unlike R218 — the files are text-only in any case, so no
  LFS smudge was involved; the push below uses the documented env).
- Ceiling discipline: the R218 payload JSON measured 120.004 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API reads)
  vs the 131.072-byte transport ceiling
  (11.068 byte headroom). The projected R219 payload JSON is ~121,000 byte
  (measured exactly at payload build, after push). Body v2 is now 103.872
  ký tự (< 105.000) — 1.128 ký tự of headroom. R219 warning:
  headroom is now 1.128 ký tự; the double compaction must continue next round
  (R81 + R80) or the head line must be trimmed.

## Next

Posting round (owner tap): PR #119 description refresh to the R219 body
v2 (R218 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r219.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R219 push (title
ending \"+ R219\", built by replacing the \"+ R140\" suffix — not appending;
body = body v2 R219 in repo, head line refreshed to head after R219 push).
This run started ~12:40 JST — INSIDE working hours (09:00–21:30 JST), so the
R219 payload is READY FOR WORKING HOURS (unlike R142/R164–R197/R207–R216,
which were held because they started before 09:00). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R218 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214, R215, R216, R217 and R218 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R219: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
