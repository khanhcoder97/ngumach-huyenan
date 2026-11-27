# MEDIA-02 — PR #119 Body Restructure R164: delivery index + body v2 coverage to `a23e090`

Date: 2026-11-21 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `a23e090` (PR119 BODY RESTRUCTURE R163 report). Content commit: `759833f`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R164 does

R163 left the disclosed gap: the delivery index covered 515 commits to
`1b206fc`; R163's own 2 commits were to fold in at R164. The R163 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~21:45 JST) shows the
live PR title ends "+ R140", head `a23e090`, mergeable_state **clean**
(fresh read at the new head this round; the MCP read returns
mergeable_state clean with the `mergeable` field null), updated_at
2026-11-21T11:43:54Z, and the live body is still R140. Read-path note:
this round's FIRST MCP read returned the live body at 92.521 ký tự,
sha256 `ced29e00`, with one character corrupted — "Ă" in "ĐÃ ĐĂNG"
(R97 paragraph, offset 41698) read as two U+FFFD replacement
characters. The IMMEDIATE re-read returned 92.520 ký tự, sha256
`ddbe32ff`, 0 U+FFFD — byte-exact R140. The corruption was transient
read-path noise in the MCP transport, NOT stored corruption on GitHub:
the posted body is intact, and the earlier rounds' byte-exact claims
stand. Lesson carried forward: a single MCP body read can corrupt one
UTF-8 character in transit — re-read before concluding the live body
changed. The R163 payload is therefore
superseded, not posted — do not post it.
No new Codex/owner direction has landed on issue #116: this round's fresh
read of the comments API via connector MCP (`issue_read` get_comments,
page 1+2, ~21:45 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `a23e090` (~21:45 JST): `git rev-list --count
cf17178..a23e090` = 517 commits, `git diff --name-only` = 2884 files,
`--shortstat` = 269440 insertions, 0 deletions. `git merge-tree
--write-tree` `a23e090` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `9bc639d3796f5f3fd213fd31f4b01eee0ad8dad8`. Like R163, this round
DID get a fresh API mergeable read at the new head — mergeable_state clean
— so the clean verdict at `a23e090` is this round's own read, not a carried
forward one. (The R163 payload, prepared ~20:45 JST, cited unstable at
`a23e090` with CI still running; CI has since finished and this round's
fresh read agrees the head is clean. The R163 payload was NOT refreshed by
the main flow — `cmp` against its `.bak-prepost-20261121` is byte-identical
this round.)

R164 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `a23e090` (517 commits / 2884 files /
  269440 additions; the fresh git derivation at `a23e090`, the fresh API
  read ~21:45 JST, and the merge-tree cross-check at `a23e090` are cited,
  with the fresh clean mergeable read at the new head disclosed
  above; live body R140; delta `1b206fc..a23e090`: 5 paths, 364
  insertions, 11 deletions); one row appended — PR119 BODY RESTRUCTURE
  R163 (`826a7df`/`a23e090`), recording that its payload was prepared
  after push ~20:45 JST (104.833 ký tự, sha `2827d9f8`,
  mergeable_state unstable tại `a23e090` — API ~20:45 JST, CI đang chạy,
  lần clean gần nhất tại `1b206fc` + merge-tree tại `a23e090`; JSON
  123.323 byte < trần 131.072 — còn 7.749 byte, bản giữ tại
  `.bak-prepost-20261121`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read, byte-exact
  on re-read, sha `ddbe32ff`) — superseded, not posted; issue line re-read fresh
  this round (34 comments, latest ACK `6862732081`, no new direction;
  connector MCP get_comments page 1+2). The index now covers every
  block through `a23e090`; R164's own 2 commits fold in at the next index
  update (R165), disclosed in the index itself. The R164 note was
  appended after the R163 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `a23e090` · 517 · 2884 (with the fresh git derivation at `a23e090`,
  the fresh API read ~21:45 JST, and the fresh merge-tree cross-check at
  `a23e090`), plus the R163 paragraph in "Khối mới nhất" (919 ký tự,
  marked chưa đăng — live body is R140) and the R164 note. The stale index
  reference in "Về bản mô tả này" (head `1b206fc`) is also fixed to
  `a23e090`, and the title line is extended to R163 (appended before the
  closing paren — the R120 append-vs-replace defect concerns the live PR
  title suffix, not this title list; the R164 checker passed on the first
  run, no title defect this round). Compaction extended (R163 warning):
  the R160 AND R161 paragraphs (911 ký tự each) are collapsed to one
  365-ký-tự compact line each (full detail stays in the delivery index),
  so the body is 104.687 ký tự — net +17 vs R163 despite the new R163 paragraph.
  Compacting only R160 would have pushed the body to ~105.150 ký tự, past the
  105.000 ceiling, so the second compaction was required this round, not
  optional. The live PR description is refreshed from this file in
  the posting round that follows R164 (owner tap) — the R140 body v2 now
  live is the base; only the R163 paragraph (posting note) + new head line
  are new vs live.
- **Checker** `check_pr119_restructure_r164_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R163 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R163 and R164 update notes are present
  (guarding the R140 replace-instead-of-append defect), and the
  compaction check extended from R163 (20 compact lines R142–R161
  present, each < 400 ký tự, body total < 105.000 ký tự — body is now
  104.687 ký tự). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R164_VALIDATION_20261121.json`).
  First checker run PASS 19/19 — no defect this round. The checker was
  written fresh (not sed-copied from R163) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `1b206fc`/`731eb39`/`269087`/`ece6c1cf` references in
  the checker — the R163 values) before the run — the R69 sed-order
  copy defect (mangled full COVER SHA) was avoided by construction. The
  `826a7df`/`a23e090` hits in the checker are the intended assertions
  that the index row carries the R163 content/report SHAs.

## Verification

- Merge-tree `a23e090` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `9bc639d3796f5f3fd213fd31f4b01eee0ad8dad8`. Merge-tree at the R164
  content head `759833f` vs `f3db6b3`: exit 0, tree
  `145cf1222ebd5fa95c80967edb907ec05e5204b6`.
- Live PR state: API connector MCP read ~21:45 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `a23e090`; live body
  R140 (92.520 ký tự, sha `ddbe32ff` byte-exact on immediate re-read this round, updated_at
  2026-11-21T11:43:54Z — unchanged since the R163 push; first read this round transiently returned
  92.521 ký tự / sha `ced29e00` with one "Ă" as two U+FFFD — read-path noise, see above); mergeable_state
  **clean** at the new head (fresh read this round; `mergeable` field null via MCP).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1+2, ~21:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R164 block 3 paths / 0 violations; cumulative at the R164
  content commit `759833f` 2885 paths / 1 violation — the known
  `.gitattributes` merge-base artifact only (byte-identical with
  integration `f3db6b3`, sha256 `23352e4c…` on both sides, re-verified
  at `759833f`). Merge-tree at the R164 content head `759833f` vs
  `f3db6b3`: exit 0, tree `145cf122…`.
- Transient notes: no rate-limit 403 on any MCP read this round (pulls +
  issue comments both 200 first try). Edit-script re-run guard refused
  correctly (R163 row already present — the guard asserts absence before
  insert, so the second run exits 1 with no file change, no duplicated
  paragraph or row; files were already correct from the first run).
- Ceiling discipline: the R163 payload JSON measured 123.323 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (7.749 byte headroom). The projected R164 payload JSON is ~123,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.687
  ký tự (< 105.000) — the R160+R161 compaction bought back ~1.102 ký tự
  this round, so the net growth is only +17/round while two old paragraphs
  are compacted per round; R165 should compact R162 (919 ký tự) next to
  keep the same headroom. No further compaction is scheduled in this
  round: the older full paragraphs (R141 and below, R162–R163) are left
  untouched unless the ceiling tightens again.

## Next

Posting round (owner tap): PR #119 description refresh to the R164 body
v2 (R163 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r164.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R164 push (title
ending "+ R164", built by replacing the "+ R140" suffix — not appending;
body = body v2 R164 in repo, head line refreshed to head after R164 push).
This run started ~21:40 JST — PAST working hours (09:00–21:30 JST), so the
R164 payload is HELD for working hours, not presented (like R142) — trình bày thuộc về luồng chính
khi giờ làm việc trở lại, hoặc R165 supersede. Do not present the superseded R163 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162 and R163 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R164: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
