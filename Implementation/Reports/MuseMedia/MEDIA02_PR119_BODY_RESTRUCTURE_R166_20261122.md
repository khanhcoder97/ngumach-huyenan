# MEDIA-02 — PR #119 Body Restructure R166: delivery index + body v2 coverage to `9113594`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `9113594` (PR119 BODY RESTRUCTURE R165 report). Content commit: `f85dd45`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R166 does

R165 left the disclosed gap: the delivery index covered 519 commits to
`878815d`; R165's own 2 commits were to fold in at R166. The R165 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~01:45 JST) shows the
live PR title ends "+ R140", head `9113594`, mergeable_state **clean**
(fresh read at the new head this round; the MCP read returns
mergeable_state clean with the `mergeable` field null), updated_at
2026-11-21T15:48:00Z, and the live body is still R140. Read-path note:
unlike R165, this round's FIRST MCP read returned the live body at
92.521 ký tự with 2 U+FFFD (1 ký tự "Ă" became 2 U+FFFD — the known
transient read-path corruption, same as R164); the immediate re-read
returned it byte-exact at once — 92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD.
The R165 payload is therefore superseded, not posted — do not post it.
No new Codex/owner direction has landed on issue #116: this round's fresh
read of the comments API via connector MCP (`issue_read` get_comments,
page 1+2, ~01:45 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `9113594` (~01:45 JST): `git rev-list --count
cf17178..9113594` = 521 commits, `git diff --name-only` = 2890 files,
`--shortstat` = 270156 insertions, 0 deletions. `git merge-tree
--write-tree` `9113594` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `6dbe5eccc5400d3f1824f9e31d06303b1a987276`. Like R165, this round
DID get a fresh API mergeable read at the new head — mergeable_state clean
— so the clean verdict at `9113594` is this round's own read, not a carried
forward one. (The R165 payload, prepared ~00:50 JST, cited unstable at
`9113594` because CI was still running; the head has since finished CI and
this round's fresh read agrees the head is clean. The R165 payload was NOT refreshed by
the main flow — `cmp` against its `.bak-prepost-20261122` is byte-identical
this round.)

R166 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `9113594` (521 commits / 2890 files /
  270156 additions; the fresh git derivation at `9113594`, the fresh API
  read ~01:45 JST, and the merge-tree cross-check at `9113594` are cited,
  with the fresh clean mergeable read at the new head disclosed
  above; live body R140; delta `878815d..9113594`: 5 paths, 366
  insertions, 12 deletions); one row appended — PR119 BODY RESTRUCTURE
  R165 (`a5da73e`/`9113594`), recording that its payload was prepared
  after push ~00:50 JST (104.644 ký tự, sha `82d8ebc8`,
  mergeable_state unstable tại `9113594` lúc chuẩn bị — CI đang chạy, clean tại `878815d`;
  JSON 123.094 byte < trần 131.072 — còn 7.978 byte, bản giữ tại
  `.bak-prepost-20261122`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read: first read
  92.521 ký tự / 2 U+FFFD, immediate re-read byte-exact sha `ddbe32ff`) — superseded, not posted; issue line re-read fresh
  this round (34 comments, latest ACK `6862732081`, no new direction;
  connector MCP get_comments page 1+2). The index now covers every
  block through `9113594`; R166's own 2 commits fold in at the next index
  update (R167), disclosed in the index itself. The R166 note was
  appended after the R165 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `9113594` · 521 · 2890 (with the fresh git derivation at `9113594`,
  the fresh API read ~01:45 JST, and the fresh merge-tree cross-check at
  `9113594`), plus the R165 paragraph in "Khối mới nhất" (825 ký tự,
  marked chưa đăng — live body is R140) and the R166 note. The stale index
  reference in "Về bản mô tả này" (head `878815d`) is also fixed to
  `9113594`, and the title line is extended to R165. Compaction (R165
  warning): compacting R164 alone would have left the body at ~105.091 ký tự, past
  the 105.000 ceiling, so the R165 paragraph is trimmed to 825 ký tự
  (from a 913-ký-tự draft) and the head line is trimmed ~50 ký tự, and the
  R164 paragraph (894 ký tự) is collapsed to one 362-ký-tự compact line
  (full detail stays in the delivery index), so the body is 104.930 ký tự — net +361 vs R165
  despite the new R165 paragraph. The live PR description is refreshed from this file in
  the posting round that follows R166 (owner tap) — the R140 body v2 now
  live is the base; only the R165 paragraph (posting note) + new head line
  are new vs live.
- **Checker** `check_pr119_restructure_r166_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R165 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R165 and R166 update notes are present
  (guarding the R140 replace-instead-of-append defect), and the
  compaction check extended from R165 (23 compact lines R142–R164
  present, each < 400 ký tự, body total < 105.000 ký tự — body is now
  104.930 ký tự). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R166_VALIDATION_20261122.json`).
  The checker caught a real defect on its first run: the edit script's
  title append used `[:-5]` and dropped "R164" from the title line
  (the R120 append-vs-replace defect family) — fixed before commit, and
  the checker passed 19/19 on re-run. The checker was
  written fresh (not sed-copied from R165) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `878815d`/`759833f`/`269802`/`2b2f7bca` references in
  the checker — the R165 values) before the run — the R69 sed-order
  copy defect (mangled full COVER SHA) was avoided by construction. The
  `a5da73e`/`9113594` hits in the checker are the intended assertions
  that the index row carries the R165 content/report SHAs.

## Verification

- Merge-tree `9113594` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `6dbe5eccc5400d3f1824f9e31d06303b1a987276`. Merge-tree at the R166
  content head `f85dd45` vs `f3db6b3`: exit 0, tree
  `90790a151f169e09840d6d1da7331e4ffef55eaf`.
- Live PR state: API connector MCP read ~01:45 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `9113594`; live body
  R140 (92.520 ký tự, sha `ddbe32ff` byte-exact on the immediate re-read this round, 0 U+FFFD —
  first read 92.521 ký tự / 2 U+FFFD from the known transient read-path
  corruption, same as R164;
  updated_at 2026-11-21T15:48:00Z — changed since the R165 push, head moved); mergeable_state
  **clean** at the new head (fresh read this round; `mergeable` field null via MCP).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1+2, ~01:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R166 block 3 paths / 0 violations; cumulative at the R166
  content commit `f85dd45` 2891 paths / 1 violation — the known
  `.gitattributes` merge-base artifact only (byte-identical with
  integration `f3db6b3`, sha256 `23352e4c…` on both sides, re-verified
  at `f85dd45`). Merge-tree at the R166 content head `f85dd45` vs
  `f3db6b3`: exit 0, tree `90790a15…`.
- Transient notes: no rate-limit 403 on any MCP read this round (pulls +
  issue comments both 200 first try). Edit-script budget guard: the
  first edit-script run produced a 105.091-ký-tự body (91 over the
  ceiling) and exited 2; that version wrote files before checking, so
  both files were restored via `git checkout` and the script was fixed
  (budget check now runs before any write) and re-run with the trimmed
  R165 paragraph (913 → 825 ký tự) and trimmed head line, landing at
  104.926 ký tự (104.930 after the title fix). Edit-script re-run guard
  was not triggered (no duplicate paragraph or row).
- Ceiling discipline: the R165 payload JSON measured 123.094 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (7.978 byte headroom). The projected R166 payload JSON is ~123,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.930
  ký tự (< 105.000) — only 70 ký tự of headroom. R167 warning:
  compacting only R165 at R167 leaves the body at ~105.350 ký tự — the
  R166 paragraph or the head line must be trimmed ~350+ ký tự at R167,
  or a second compaction considered; do not let the body cross 105.000.

## Next

Posting round (owner tap): PR #119 description refresh to the R166 body
v2 (R165 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r166.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R166 push (title
ending "+ R166", built by replacing the "+ R140" suffix — not appending;
body = body v2 R166 in repo, head line refreshed to head after R166 push).
This run started ~01:40 JST — PAST working hours (09:00–21:30 JST), so the
R166 payload is HELD for working hours, not presented (like R142/R164/R165) — trình bày thuộc về luồng chính
khi giờ làm việc trở lại, hoặc R167 supersede. Do not present the superseded R165 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164 and R165 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R166: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
