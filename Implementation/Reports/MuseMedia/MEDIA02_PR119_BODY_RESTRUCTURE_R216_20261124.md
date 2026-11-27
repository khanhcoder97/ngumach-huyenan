# MEDIA-02 — PR #119 Body Restructure R216: delivery index + body v2 coverage to `1e564a2`

Date: 2026-11-24 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `1e564a2` (PR119 BODY RESTRUCTURE R215 report). Content commit: `dd19bba`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R216 does

R215 left the disclosed gap: the delivery index covered 619 commits to
`3de99c9`; R215's own 2 commits were to fold in at R216. The R215 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API read ~08:40 JST, MCP + direct curl agreeing:
PR title still ends "+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T22:47:25Z — bumped by the R215 push updating the PR head, body bytes
unchanged). The R215 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read twice (~08:40 JST, read-only —
`issue_read get_comments` page 1 and `pull_request_read get` via `call-read-tool`, plus a
direct public-API read of the issue comments and of the PR with curl as cross-check): the MCP read
returned the clean body on the FIRST read (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD — no mangle
this round, unlike R209/R215) and the direct read AGREED on every field (92.520 ký tự, sha
`ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — a real cross-check this round,
unlike R215 where the direct read was rate-limited. The issue-comments direct read also
succeeded (34 comments, latest `6862732081`) and agrees with the MCP read. PR head `1e564a2`,
621 commits / 3040 files / +293.232, mergeable_state clean at `1e564a2` (mergeable null via MCP,
true via direct read).

Fresh derivation at `1e564a2` (~08:40 JST): `git rev-list --count
cf17178..1e564a2` = 621 commits, `git diff --name-only` = 3040 files,
`--shortstat` = 293232 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `1e564a2` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `4e13aa58…`. No re-fetch was needed before applying: the run fetched at ~08:40 JST
(the run start) and the remote head was still `1e564a2`, integration still `f3db6b3` — no
intervening push; the API read ~08:40 JST independently confirmed head `1e564a2`.

R216 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `1e564a2` (621 commits / 3040 files /
  293232 additions; the fresh git derivation at `1e564a2`, the fresh API
  read ~08:40 JST, and the merge-tree cross-check at `1e564a2` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `3de99c9..1e564a2`: 5 paths, 753 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R215
  (`6127a16`/`1e564a2`), recording that its payload was prepared after
  push ~07:47 JST (104.851 ký tự, sha `3c51e664`; JSON 120.968 byte < trần 131.072 — còn 10.104 byte, bản giữ tại
  `.bak-prepost-20261124` — R216 sao lưu, sha256 `84645084…` cả hai, kiểm chứng lại lượt này),
  that it was NOT posted
  — live body still R140 (verified by this round's MCP + direct reads, both clean:
  description structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc byte-exact lượt này qua MCP lần 1
  và đọc trực tiếp cross-check khớp, 0 U+FFFD, updated_at 2026-11-23T22:47:25Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~08:40 JST).
  The index now covers every block through `1e564a2`; R216's
  own 2 commits fold in at the next index update (R217), disclosed in the
  index itself. The R216 note was appended after the R215 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `1e564a2` · 621 · 3040 (with the fresh git derivation at `1e564a2`,
  the fresh API read ~08:40 JST, and the fresh merge-tree cross-check at
  `1e564a2`), plus the R215 paragraph in "Khối mới nhất" (248 ký tự,
  marked chưa đăng — live body is R140) and the R216 note. The stale index
  reference in "Về bản mô tả này" (head `3de99c9`) is also fixed to
  `1e564a2`, and the title line is extended to R215 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R215 warning —
  applied with a measured correction, DOUBLE): the R89 + R88 paragraphs (494 ký tự each — measured this
  round) are
  collapsed to one 208-ký-tự compact line each (full detail stays in the
  delivery index) — the new R215 paragraph was 248 ký tự, so
  the body is 104.794 ký tự — net −116 vs R215 despite the new R215 paragraph, headroom 206 ký tự. The dry-run first projected 104.794 ký tự
  and the apply wrote exactly that on the first attempt — measure, then trim, then apply.
  Paragraph order: the R215 paragraph sits directly after R214
  (ascending full-paragraph order R166..R215), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R216 (owner tap) — the R140 body v2 now live
  is the base; only the R215 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r216_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R215 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R215 and R216 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R215 (78 compact lines R88–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.794 ký tự),
  a check that the R215 paragraph sits directly after R214
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R215 note clean).
  New this round: the R214-row regression guard (cumulative must be 3038,
  re-derived from git at `6127a16`), the R215-row guard (cumulative must
  cite 3041 — 3040 at `1e564a2` + 1 new checker in the R216 content commit,
  verified in this report after the content commit), the body "Ghi chú" line correction guard
  (R158/R215, range R88–R165, list complete through R215, no double slash),
  and the working-tree guard (`git status --porcelain` lists exactly the 3
  intended paths — index + body + this checker — no stray modification may
  survive past the report commit).
  **PASS 48/48**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R216_VALIDATION_20261124.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R215) with the full COVER
  SHA verified intact (definition + docstring, both
  `1e564a2520fca2d856b351a97c3d3359d7fa9cc5` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (3 stale
  `3de99c9` references in the checker — the docstring explaining the previous cover value, intentional,
  and the R214-row guard string citing "3037 at 3de99c9", legitimate) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.794 ký tự and the apply wrote on
  the first attempt at 104.794 ký tự with 206 ký tự of headroom; the idempotency re-run
  after apply reported already-applied changed: 0 — verified, after the
  R203/R207 lesson recurred once this round (see below) and was fixed in
  the script before the report commit.
  Correction caught before the report commit: the R215 row's cumulative figure was drafted as 3041 (3040 at
  `1e564a2` + 1 new checker) and the true diff at the R216 content
  commit is 3041 — verified by `git diff --name-only cf17178..dd19bba` = 3041
  before the report commit. `git status --porcelain` after the content
  commit showed only the intended validation JSON untracked — no leftover
  edit (the R206 failure mode did not recur).
  Idempotency defect caught and fixed in the edit script this round (R203/R207 lesson
  recurred): the first idempotency re-run crashed on the line-7 OLD-state
  assert (`assert new7 != old7`) after a successful apply — the script now
  checks the NEW state first for both the line-7 and "Ghi chú" replacements,
  and the re-run reports already-applied changed: 0. The committed content
  was verified correct after the fix (body 104.794 ký tự, R215 paragraph +
  78 compact lines present in the committed files).

## R216 robustness note — headroom now 206 chars

The R215 warning left 90 ký tự of headroom, so this round compacted
TWO paragraphs (R89 + R88, 494 ký tự → 208 each) before adding the new R215 paragraph
(248 ký tự). The body is now 104.794 ký tự — net −116 vs R215 — with
206 ký tự of headroom. The double compaction bought back 572 ký tự against the
248-ký-tự new paragraph, so the margin now holds while two paragraphs are
compacted per round; the head line is the variable cost (its honest
live-read disclosure grew ~+110 ký tự this round as the cross-check wording
was added). The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact old paragraphs and keep the new
paragraph tight, or the body outgrows the margin within a round.
R217 warning: headroom is 206 ký tự; compact R87 + R86 next (or trim the
head line hard). At the current net −116/round the margin is recovering,
but only while the double compaction continues (full paragraphs remaining R166..R215 = 50;
compact block R88–R165 = 78 lines).
No ĐÍNH CHÍNH this round: R215's committed content verified correct —
the committed index at `1e564a2` carries the R213 row at cumulative 3035
(verified via `git show 1e564a2:...` this round) and the R214 row at 3038
(re-derived by the new checker from git at `6127a16`); no uncommitted
working-tree fix was left behind by R215 (the working tree was clean at this
run's start and the fetch found no intervening push).
Lesson this round: (1) the dry-run projection caught the exact final size
BEFORE any write (104.794 projected; apply wrote 104.794 — measure, don't hand-count; same lesson as
R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215).
(2) A row's "cumulative N paths" counts the diff at the AUTHORING round's content commit — which includes
the previous round's 2 report files, not just its content commit (same
lesson as R206/R207/R208/R209/R210/R211/R212/R213/R214/R215 — the R215 row's 3041 was verified post-commit by git
diff, not assumed from the coverage head). (3) An edit script's idempotency re-run must check the NEW state first, not only
assert the OLD state — otherwise the re-run crashes on its own
pre-condition after a successful apply (R203/R207 lesson — recurred this
round on the line-7 assert and was fixed in the script before the report
commit; re-run now reports already-applied changed: 0, verified). (4) After the report commit, `git status
--porcelain` must be EMPTY before push — a fix that lives only in the
working tree is not delivered (R206 lesson, now a checker guard + a
runbook step: this round's post-content-commit status showed only the
intended validation JSON untracked). (5) Two agreeing read paths settle
the live body faster than one mangled read did in R209 — the MCP path returned
the clean body on the first read this round (92.520, sha `ddbe32ff`) and the
direct curl read AGREED on every field including mergeable true — a real
cross-check, unlike R215 where the direct read was rate-limited; when two
read paths agree first try, record both, not one. (6) A payload backup the authoring
round did not make must be disclosed as made by the folding round, not claimed as the author's — R215's
payload had no `.bak` copy when R216 started; R216 copied it and verified sha256 identical
(`84645084…` both), and the R215 row records the copy as R216's, not R215's.

## Verification

- Merge-tree `1e564a2` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `4e13aa58…`. Merge-tree at the R216
  content head `dd19bba` vs `f3db6b3`: exit 0,
  tree `a3b38425…`.
- Live PR state: API read twice this round (~08:40 JST) — MCP read
  clean on the first read (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) and direct curl read
  agreeing (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, mergeable true, mergeable_state clean) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `1e564a2`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T22:47:25Z — bumped by the R215 push updating the PR head, body
  bytes unchanged); commits 621, changed_files 3040, additions 293232
  (API agrees with the fresh git derivation; the `deletions` key is absent in
  the direct API response — git shows 0 deletions; the MCP response returns
  `mergeable: null` while the direct read returns `mergeable: true`; mergeable_state clean is the operative field); mergeable_state clean at
  `1e564a2` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the MCP API + direct curl of comments — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R216 block (`1e564a2..dd19bba`) 3 paths / 0 violations
  (index + body v2 + R216 checker); cumulative at the R216 content
  commit `dd19bba` 3041 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `dd19bba`).
  Merge-tree at the R216 content head `dd19bba` vs `f3db6b3`: exit 0,
  tree `a3b38425…`.
- Transient notes: this round's `git fetch` at ~08:40 JST succeeded
  first try. MCP `call-read-tool` accepted `issue_read`/`pull_request_read` this round
  (first PR read clean — see live-read note; `pull_request_read` takes `pullNumber`, not
  `pull_number` — parameter-name lesson carried from R211; `issue_read`
  takes `issue_number`, not `issueNumber`). No execution-risk flag on any
  git/script command this round (unlike R211/R213). The R215 payload's own head line recorded
  mergeable clean at `3de99c9` at its preparation and clean at
  `1e564a2`; this round's API read confirms clean at `1e564a2`.
- Ceiling discipline: the R215 payload JSON measured 120.968 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (10.104 byte headroom). The projected R216 payload JSON is ~121,000 byte
  (measured exactly at payload build, after push). Body v2 is now 104.794
  ký tự (< 105.000) — 206 ký tự of headroom. R216 warning:
  headroom is now 206 ký tự; the double compaction must continue next round
  (R87 + R86) or the head line must be trimmed.

## Next

Posting round (owner tap): PR #119 description refresh to the R216 body
v2 (R215 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r216.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R216 push (title
ending "+ R216", built by replacing the "+ R140" suffix — not appending;
body = body v2 R216 in repo, head line refreshed to head after R216 push).
This run started ~08:40 JST — BEFORE working hours (09:00–21:30 JST), so the
R216 payload is HELD FOR WORKING HOURS (not presented, like R142/R164–R197/R207–R215). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R215 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203, R204, R205, R206, R207, R208, R209, R210, R211, R212, R213, R214 and R215 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R216: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
