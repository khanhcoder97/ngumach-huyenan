# MEDIA-02 — PR #119 Body Restructure R170: delivery index + body v2 coverage to `9756ec0`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `9756ec0` (PR119 BODY RESTRUCTURE R169 report). Content commit: `bc371ed`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R170 does

R169 left the disclosed gap: the delivery index covered 527 commits to
`9c76981`; R169's own 2 commits were to fold in at R170. The R169 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~05:45 JST) shows the
live PR title ends "+ R140", head `9756ec0`, mergeable_state **clean**
(fresh read at the new head this round; the MCP read returns
mergeable_state clean with the `mergeable` field null), updated_at
2026-11-21T19:56:09Z, and the live body is still R140. Read-path note:
like R169, this round's FIRST MCP read returned the live body
byte-exact at once — 92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD, no
transient read-path corruption this round. The R169 payload is therefore
superseded, not posted — do not post it. No new Codex/owner direction has
landed on issue #116: this round's fresh read of the comments API via
connector MCP (`issue_read` get_comments, page 1+2, ~05:45 JST) agrees:
still 34 comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2,
updated_at 2026-11-13T19:24:48Z); no new direction since Gói 39
(`6815238814`).

Fresh derivation at `9756ec0` (~05:45 JST): `git rev-list --count
cf17178..9756ec0` = 529 commits, `git diff --name-only` = 2902 files,
`--shortstat` = 271591 insertions, 0 deletions. `git merge-tree
--write-tree` `9756ec0` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `3414e4a1d641b67c829e859a12db62aefe3cd4bc`. Like R169, this round
DID get a fresh API mergeable read at the new head — mergeable_state clean
— so the clean verdict at `9756ec0` is this round's own read, not a carried
forward one. (The R169 payload, prepared ~04:57 JST, cited unstable at
`9756ec0` because CI was still running; the head has since finished CI and
this round's fresh read agrees the head is clean. The R169 payload was NOT refreshed by
the main flow — `cmp` against its `.bak-prepost-20261122` is byte-identical
this round.)

R170 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `9756ec0` (529 commits / 2902 files /
  271591 additions; the fresh git derivation at `9756ec0`, the fresh API
  read ~05:45 JST, and the merge-tree cross-check at `9756ec0` are cited,
  with the fresh clean mergeable read at the new head disclosed
  above; live body R140; delta `9c76981..9756ec0`: 5 paths, 375
  insertions, 11 deletions); one row appended — PR119 BODY RESTRUCTURE
  R169 (`a99d985`/`9756ec0`), recording that its payload was prepared
  after push ~04:57 JST (105.030 ký tự, sha `3a158903`,
  mergeable_state unstable tại `9756ec0` lúc chuẩn bị — CI đang chạy, clean tại `9c76981`;
  JSON 123.400 byte < trần 131.072 — còn 7.672 byte, bản giữ tại
  `.bak-prepost-20261122`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read: byte-exact on the first
  read, 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — superseded, not posted; issue line re-read fresh
  this round (34 comments, latest ACK `6862732081`, no new direction;
  connector MCP get_comments page 1+2). The index now covers every
  block through `9756ec0`; R170's own 2 commits fold in at the next index
  update (R171), disclosed in the index itself. The R170 note was
  appended after the R169 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `9756ec0` · 529 · 2902 (with the fresh git derivation at `9756ec0`,
  the fresh API read ~05:45 JST, and the fresh merge-tree cross-check at
  `9756ec0`), plus the R169 paragraph in "Khối mới nhất" (743 ký tự,
  marked chưa đăng — live body is R140) and the R170 note. The stale index
  reference in "Về bản mô tả này" (head `9c76981`) is also fixed to
  `9756ec0`, and the title line is extended to R169. Compaction (R169
  warning): the R138 paragraph (1.188 ký tự) is collapsed to one 377-ký-tự
  compact line (full detail stays in the delivery index), AND the new R169
  paragraph was trimmed to 743 ký tự (R168 was 811 — trim 68 ký tự, above
  the ≥ 60 required), so the body is 104.965 ký tự — net +19 vs R169 despite the new R169 paragraph. The live PR description is refreshed from this file in
  the posting round that follows R170 (owner tap) — the R140 body v2 now
  live is the base; only the R169 paragraph (posting note) + new head line
  are new vs live.
- **Checker** `check_pr119_restructure_r170_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R169 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R169 and R170 update notes are present
  (guarding the R140 replace-instead-of-append defect), and the
  compaction check extended from R169 (28 compact lines R138–R165
  present, each < 400 ký tự, body total < 105.000 ký tự — body is now
  104.965 ký tự). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R170_VALIDATION_20261122.json`).
  The checker passed 19/19 on its FIRST run this round. The checker was
  written fresh (not sed-copied from R169) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `9c76981`/`7eeb790`/`271227`/`2899`/`241e7a4c` references in
  the checker — the R169 values) before the run — the R69 sed-order
  copy defect (mangled full COVER SHA) was avoided by construction. The
  `a99d985`/`9756ec0` hits in the checker are the intended assertions
  that the index row carries the R169 content/report SHAs. The edit
  script's budget check ran before any write (R166 lesson): the first run
  aborted before writing when the R169 paragraph measured 811 ký tự (61
  over the ≤ 750 target); after trimming the paragraph by 68 ký tự the
  second run caught a projection error (+49 ký tự from the "Về bản mô tả
  này" append the projection had missed) and aborted before writing; the
  projection was fixed and the third run passed with 35 ký tự of headroom
  and wrote.

## Verification

- Merge-tree `9756ec0` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `3414e4a1d641b67c829e859a12db62aefe3cd4bc`. Merge-tree at the R170
  content head `bc371ed` vs `f3db6b3`: exit 0, tree
  `83b25f3cf764e0190338fd9220102acd5adc486e`.
- Live PR state: API connector MCP read ~05:45 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `9756ec0`; live body
  R140 (92.520 ký tự, sha `ddbe32ff` byte-exact on the first read this round, 0 U+FFFD —
  no transient corruption this time, like R169;
  updated_at 2026-11-21T19:56:09Z — changed since the R169 push, head moved); mergeable_state
  **clean** at the new head (fresh read this round; `mergeable` field null via MCP).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1+2, ~05:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R170 block (`9c76981..bc371ed`) 6 paths / 0 violations
  (R169 report 2 files + R169 checker 1 + R170 content 3); content-only
  block (`9756ec0..bc371ed`) 3 paths / 0 violations; cumulative at the R170
  content commit `bc371ed` 2903 paths / 1 violation — the known
  `.gitattributes` merge-base artifact only (byte-identical with
  integration `f3db6b3`, sha256 `23352e4c…` on both sides, re-verified
  at `bc371ed`). Merge-tree at the R170 content head `bc371ed` vs
  `f3db6b3`: exit 0, tree `83b25f3c…`.
- Transient notes: no rate-limit 403 on any MCP read this round (pulls +
  issue comments both 200 first try). The first `issue_read` attempt
  failed fast on a wrong method name (`get_issue_comments` instead of
  `get_comments`) — retried with the correct name and succeeded; no
  data was misread. The first `pull_request_read` attempt failed fast on
  a wrong parameter name (`pull_number` instead of `pullNumber`) —
  retried with the correct name and succeeded; no data was misread.
  Edit-script re-run guard was triggered twice (paragraph budget +
  projection error, see above) — files untouched until the clean run.
- Ceiling discipline: the R169 payload JSON measured 123.400 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (7.672 byte headroom). The projected R170 payload JSON is ~123,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.965
  ký tự (< 105.000) — 35 ký tự of headroom. R171 warning:
  headroom is now only 35 ký tự; the next round must collapse R137 (1.248
  ký tự → ~377) AND keep the new paragraph ≤ 750 ký tự — an untrimmed
  ~811-ký-tự paragraph with the R137 collapse alone leaves the body
  ~104.992 ký tự, only 8 ký tự from the ceiling.

## Next

Posting round (owner tap): PR #119 description refresh to the R170 body
v2 (R169 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r170.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R170 push (title
ending "+ R170", built by replacing the "+ R140" suffix — not appending;
body = body v2 R170 in repo, head line refreshed to head after R170 push).
This run started ~05:40 JST — PAST working hours (09:00–21:30 JST), so the
R170 payload is HELD for working hours, not presented (like R142/R164/R165/R166/R167/R168/R169) — trình bày thuộc về luồng chính
khi giờ làm việc trở lại, hoặc R171 supersede. Do not present the superseded R169 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168 and R169 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R170: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
