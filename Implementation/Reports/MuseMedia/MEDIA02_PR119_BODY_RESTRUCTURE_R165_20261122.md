# MEDIA-02 — PR #119 Body Restructure R165: delivery index + body v2 coverage to `878815d`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `878815d` (PR119 BODY RESTRUCTURE R164 report). Content commit: `a5da73e`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R165 does

R164 left the disclosed gap: the delivery index covered 517 commits to
`a23e090`; R164's own 2 commits were to fold in at R165. The R164 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~00:45 JST) shows the
live PR title ends "+ R140", head `878815d`, mergeable_state **clean**
(fresh read at the new head this round; the MCP read returns
mergeable_state clean with the `mergeable` field null), updated_at
2026-11-21T12:48:33Z, and the live body is still R140. Read-path note:
unlike R164, this round's FIRST MCP read returned the live body byte-exact
at once — 92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD — no transient
corruption this round. The R164 payload is therefore
superseded, not posted — do not post it.
No new Codex/owner direction has landed on issue #116: this round's fresh
read of the comments API via connector MCP (`issue_read` get_comments,
page 1+2, ~00:45 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `878815d` (~00:45 JST): `git rev-list --count
cf17178..878815d` = 519 commits, `git diff --name-only` = 2887 files,
`--shortstat` = 269802 insertions, 0 deletions. `git merge-tree
--write-tree` `878815d` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `2b2f7bcad73fde9ddfc6e700b62a293bf71e19f1`. Like R164, this round
DID get a fresh API mergeable read at the new head — mergeable_state clean
— so the clean verdict at `878815d` is this round's own read, not a carried
forward one. (The R164 payload, prepared ~21:48 JST, cited clean at
`a23e090`; the head has since moved to `878815d` and this round's fresh read
agrees the new head is clean. The R164 payload was NOT refreshed by
the main flow — `cmp` against its `.bak-prepost-20261121` is byte-identical
this round.)

R165 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `878815d` (519 commits / 2887 files /
  269802 additions; the fresh git derivation at `878815d`, the fresh API
  read ~00:45 JST, and the merge-tree cross-check at `878815d` are cited,
  with the fresh clean mergeable read at the new head disclosed
  above; live body R140; delta `a23e090..878815d`: 5 paths, 374
  insertions, 12 deletions); one row appended — PR119 BODY RESTRUCTURE
  R164 (`759833f`/`878815d`), recording that its payload was prepared
  after push ~21:48 JST (104.753 ký tự, sha `1bfbe5f4`,
  mergeable_state clean tại `a23e090` — API ~21:45 JST, CI đã chạy xong
  + merge-tree tại `a23e090`; JSON 123.227 byte < trần 131.072 — còn 7.845 byte, bản giữ tại
  `.bak-prepost-20261121`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read, byte-exact
  on the FIRST read, sha `ddbe32ff`) — superseded, not posted; issue line re-read fresh
  this round (34 comments, latest ACK `6862732081`, no new direction;
  connector MCP get_comments page 1+2). The index now covers every
  block through `878815d`; R165's own 2 commits fold in at the next index
  update (R166), disclosed in the index itself. The R165 note was
  appended after the R164 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `878815d` · 519 · 2887 (with the fresh git derivation at `878815d`,
  the fresh API read ~00:45 JST, and the fresh merge-tree cross-check at
  `878815d`), plus the R164 paragraph in "Khối mới nhất" (894 ký tự,
  marked chưa đăng — live body is R140) and the R165 note. The stale index
  reference in "Về bản mô tả này" (head `a23e090`) is also fixed to
  `878815d`, and the title line is extended to R164 (appended before the
  closing paren — the R120 append-vs-replace defect concerns the live PR
  title suffix, not this title list; the R165 checker passed on the first
  run, no title defect this round). Compaction extended (R164 warning):
  compacting R162 alone would have left the body at ~105.181 ký tự, past
  the 105.000 ceiling, so the R162 AND R163 paragraphs (911 and 919 ký tự)
  are collapsed to one 365-ký-tự compact line each (full detail stays in
  the delivery index), so the body is 104.569 ký tự — net −118 vs R164
  despite the new R164 paragraph. The live PR description is refreshed from this file in
  the posting round that follows R165 (owner tap) — the R140 body v2 now
  live is the base; only the R164 paragraph (posting note) + new head line
  are new vs live.
- **Checker** `check_pr119_restructure_r165_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R164 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R164 and R165 update notes are present
  (guarding the R140 replace-instead-of-append defect), and the
  compaction check extended from R164 (22 compact lines R142–R163
  present, each < 400 ký tự, body total < 105.000 ký tự — body is now
  104.569 ký tự). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R165_VALIDATION_20261122.json`).
  First checker run PASS 19/19 — no defect this round. The checker was
  written fresh (not sed-copied from R164) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `a23e090`/`826a7df`/`269440`/`9bc639d3` references in
  the checker — the R164 values) before the run — the R69 sed-order
  copy defect (mangled full COVER SHA) was avoided by construction. The
  `759833f`/`878815d` hits in the checker are the intended assertions
  that the index row carries the R164 content/report SHAs.

## Verification

- Merge-tree `878815d` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `2b2f7bcad73fde9ddfc6e700b62a293bf71e19f1`. Merge-tree at the R165
  content head `a5da73e` vs `f3db6b3`: exit 0, tree
  `38384570d8e23565f5988b4c25cb323f537d1cfb`.
- Live PR state: API connector MCP read ~00:45 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `878815d`; live body
  R140 (92.520 ký tự, sha `ddbe32ff` byte-exact on the FIRST read this round, 0 U+FFFD,
  updated_at 2026-11-21T12:48:33Z — unchanged since the R164 push); mergeable_state
  **clean** at the new head (fresh read this round; `mergeable` field null via MCP).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1+2, ~00:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R165 block 3 paths / 0 violations; cumulative at the R165
  content commit `a5da73e` 2888 paths / 1 violation — the known
  `.gitattributes` merge-base artifact only (byte-identical with
  integration `f3db6b3`, sha256 `23352e4c…` on both sides, re-verified
  at `a5da73e`). Merge-tree at the R165 content head `a5da73e` vs
  `f3db6b3`: exit 0, tree `38384570…`.
- Transient notes: no rate-limit 403 on any MCP read this round (pulls +
  issue comments both 200 first try). Edit-script re-run guard refused
  correctly (R165 note already present — the guard asserts absence before
  insert, so the second run exits 1 with no file change, no duplicated
  paragraph or row; files were already correct from the first run).
- Ceiling discipline: the R164 payload JSON measured 123.227 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (7.845 byte headroom). The projected R165 payload JSON is ~123,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.569
  ký tự (< 105.000) — the R162+R163 compaction bought back ~1.100 ký tự
  this round, so the net change is −118/round while two old paragraphs
  are compacted per round; R166 warning: compacting only R164 at R166
  leaves the body at ~105.060 ký tự — the R165 paragraph or the head line
  must be trimmed ~60+ ký tự at R166, or a second compaction considered;
  do not let the body cross 105.000.

## Next

Posting round (owner tap): PR #119 description refresh to the R165 body
v2 (R164 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r165.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R165 push (title
ending "+ R165", built by replacing the "+ R140" suffix — not appending;
body = body v2 R165 in repo, head line refreshed to head after R165 push).
This run started ~00:40 JST — PAST working hours (09:00–21:30 JST), so the
R165 payload is HELD for working hours, not presented (like R142/R164) — trình bày thuộc về luồng chính
khi giờ làm việc trở lại, hoặc R166 supersede. Do not present the superseded R164 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163 and R164 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R165: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
