# MEDIA-02 — PR #119 Body Restructure R167: delivery index + body v2 coverage to `ec66d5b`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `ec66d5b` (PR119 BODY RESTRUCTURE R166 report). Content commit: `961604b`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R167 does

R166 left the disclosed gap: the delivery index covered 521 commits to
`9113594`; R166's own 2 commits were to fold in at R167. The R166 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~02:45 JST) shows the
live PR title ends "+ R140", head `ec66d5b`, mergeable_state **clean**
(fresh read at the new head this round; the MCP read returns
mergeable_state clean with the `mergeable` field null), updated_at
2026-11-21T16:52:07Z, and the live body is still R140. Read-path note:
like R164/R166, this round's FIRST MCP read returned the live body at
92.521 ký tự with 2 U+FFFD (1 ký tự "Ă" became 2 U+FFFD — the known
transient read-path corruption); the immediate re-read
returned it byte-exact at once — 92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD.
The R166 payload is therefore superseded, not posted — do not post it.
No new Codex/owner direction has landed on issue #116: this round's fresh
read of the comments API via connector MCP (`issue_read` get_comments,
page 1+2, ~02:45 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `ec66d5b` (~02:45 JST): `git rev-list --count
cf17178..ec66d5b` = 523 commits, `git diff --name-only` = 2893 files,
`--shortstat` = 270517 insertions, 0 deletions. `git merge-tree
--write-tree` `ec66d5b` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `bb86ab53c65793c96b4602534588a33d03081278`. Like R166, this round
DID get a fresh API mergeable read at the new head — mergeable_state clean
— so the clean verdict at `ec66d5b` is this round's own read, not a carried
forward one. (The R166 payload, prepared ~01:52 JST, cited unstable at
`ec66d5b` because CI was still running; the head has since finished CI and
this round's fresh read agrees the head is clean. The R166 payload was NOT refreshed by
the main flow — `cmp` against its `.bak-prepost-20261122` is byte-identical
this round.)

R167 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `ec66d5b` (523 commits / 2893 files /
  270517 additions; the fresh git derivation at `ec66d5b`, the fresh API
  read ~02:45 JST, and the merge-tree cross-check at `ec66d5b` are cited,
  with the fresh clean mergeable read at the new head disclosed
  above; live body R140; delta `9113594..ec66d5b`: 5 paths, 372
  insertions, 11 deletions); one row appended — PR119 BODY RESTRUCTURE
  R166 (`f85dd45`/`ec66d5b`), recording that its payload was prepared
  after push ~01:52 JST (104.973 ký tự, sha `99d0e671`,
  mergeable_state unstable tại `ec66d5b` lúc chuẩn bị — CI đang chạy, clean tại `9113594`;
  JSON 123.476 byte < trần 131.072 — còn 7.596 byte, bản giữ tại
  `.bak-prepost-20261122`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read: first read
  92.521 ký tự / 2 U+FFFD, immediate re-read byte-exact sha `ddbe32ff`) — superseded, not posted; issue line re-read fresh
  this round (34 comments, latest ACK `6862732081`, no new direction;
  connector MCP get_comments page 1+2). The index now covers every
  block through `ec66d5b`; R167's own 2 commits fold in at the next index
  update (R168), disclosed in the index itself. The R167 note was
  appended after the R166 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `ec66d5b` · 523 · 2893 (with the fresh git derivation at `ec66d5b`,
  the fresh API read ~02:45 JST, and the fresh merge-tree cross-check at
  `ec66d5b`), plus the R166 paragraph in "Khối mới nhất" (825 ký tự,
  marked chưa đăng — live body is R140) and the R167 note. The stale index
  reference in "Về bản mô tả này" (head `9113594`) is also fixed to
  `ec66d5b`, and the title line is extended to R166. Compaction (R166
  warning): compacting R165 alone would have left the body at ~105.350 ký tự, past
  the 105.000 ceiling, so the R165 paragraph (825 ký tự) is collapsed to one 365-ký-tự compact line
  AND the R141 paragraph (1.023 ký tự) is collapsed to one 326-ký-tự compact line
  (full detail stays in the delivery index), so the body is 104.696 ký tự — net −234 vs R166
  despite the new R166 paragraph. The live PR description is refreshed from this file in
  the posting round that follows R167 (owner tap) — the R140 body v2 now
  live is the base; only the R166 paragraph (posting note) + new head line
  are new vs live.
- **Checker** `check_pr119_restructure_r167_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R166 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R166 and R167 update notes are present
  (guarding the R140 replace-instead-of-append defect), and the
  compaction check extended from R166 (25 compact lines R141–R165
  present, each < 400 ký tự, body total < 105.000 ký tự — body is now
  104.696 ký tự). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R167_VALIDATION_20261122.json`).
  The checker passed 19/19 on its first run. The checker was
  written fresh (not sed-copied from R166) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `878815d`/`759833f`/`270156`/`6dbe5ecc` references in
  the checker — the R166 values) before the run — the R69 sed-order
  copy defect (mangled full COVER SHA) was avoided by construction. The
  `f85dd45`/`ec66d5b` hits in the checker are the intended assertions
  that the index row carries the R166 content/report SHAs. The edit
  script's budget check ran before any write (R166 lesson); its first
  run died on an off-by-one line index before writing anything, was
  fixed, and re-ran clean — no file was restored from git this round.

## Verification

- Merge-tree `ec66d5b` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `bb86ab53c65793c96b4602534588a33d03081278`. Merge-tree at the R167
  content head `961604b` vs `f3db6b3`: exit 0, tree
  `40b637bc03d3589aaee640049207e01bd8d26d55`.
- Live PR state: API connector MCP read ~02:45 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `ec66d5b`; live body
  R140 (92.520 ký tự, sha `ddbe32ff` byte-exact on the immediate re-read this round, 0 U+FFFD —
  first read 92.521 ký tự / 2 U+FFFD from the known transient read-path
  corruption, same as R164/R166;
  updated_at 2026-11-21T16:52:07Z — changed since the R166 push, head moved); mergeable_state
  **clean** at the new head (fresh read this round; `mergeable` field null via MCP).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1+2, ~02:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R167 block 3 paths / 0 violations; cumulative at the R167
  content commit `961604b` 2894 paths / 1 violation — the known
  `.gitattributes` merge-base artifact only (byte-identical with
  integration `f3db6b3`, sha256 `23352e4c…` on both sides, re-verified
  at `961604b`). Merge-tree at the R167 content head `961604b` vs
  `f3db6b3`: exit 0, tree `40b637bc…`.
- Transient notes: no rate-limit 403 on any MCP read this round (pulls +
  issue comments both 200 first try). The first `issue_read` attempt
  failed fast on a wrong parameter name (`issueNumber` instead of
  `issue_number`) — retried with the correct name and succeeded; no
  data was misread. Edit-script re-run guard was not triggered (no
  duplicate paragraph or row).
- Ceiling discipline: the R166 payload JSON measured 123.476 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (7.596 byte headroom). The projected R167 payload JSON is ~123,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.696
  ký tự (< 105.000) — 304 ký tự of headroom. R168 warning:
  the compaction window now reaches R141; the next round should collapse
  R140 as well (or trim the new paragraph) to stay under 105.000 —
  compacting only the newest paragraph again leaves the body ~105,150 ký tự.

## Next

Posting round (owner tap): PR #119 description refresh to the R167 body
v2 (R166 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r167.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R167 push (title
ending "+ R167", built by replacing the "+ R140" suffix — not appending;
body = body v2 R167 in repo, head line refreshed to head after R167 push).
This run started ~02:40 JST — PAST working hours (09:00–21:30 JST), so the
R167 payload is HELD for working hours, not presented (like R142/R164/R165/R166) — trình bày thuộc về luồng chính
khi giờ làm việc trở lại, hoặc R168 supersede. Do not present the superseded R166 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165 and R166 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R167: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
