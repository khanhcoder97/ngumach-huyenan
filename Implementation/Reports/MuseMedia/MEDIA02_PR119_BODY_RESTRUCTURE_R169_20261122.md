# MEDIA-02 — PR #119 Body Restructure R169: delivery index + body v2 coverage to `9c76981`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `9c76981` (PR119 BODY RESTRUCTURE R168 report). Content commit: `a99d985`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R169 does

R168 left the disclosed gap: the delivery index covered 525 commits to
`8367e34`; R168's own 2 commits were to fold in at R169. The R168 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~04:45 JST) shows the
live PR title ends "+ R140", head `9c76981`, mergeable_state **clean**
(fresh read at the new head this round; the MCP read returns
mergeable_state clean with the `mergeable` field null), updated_at
2026-11-21T18:46:31Z, and the live body is still R140. Read-path note:
like R168, this round's FIRST MCP read returned the live body
byte-exact at once — 92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD, no
transient read-path corruption this round. The R168 payload is therefore
superseded, not posted — do not post it. No new Codex/owner direction has
landed on issue #116: this round's fresh read of the comments API via
connector MCP (`issue_read` get_comments, page 1+2, ~04:45 JST) agrees:
still 34 comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2,
updated_at 2026-11-13T19:24:48Z); no new direction since Gói 39
(`6815238814`).

Fresh derivation at `9c76981` (~04:45 JST): `git rev-list --count
cf17178..9c76981` = 527 commits, `git diff --name-only` = 2899 files,
`--shortstat` = 271227 insertions, 0 deletions. `git merge-tree
--write-tree` `9c76981` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `241e7a4cc1d6b1a7ea85517c5caf1bb816868ded`. Like R168, this round
DID get a fresh API mergeable read at the new head — mergeable_state clean
— so the clean verdict at `9c76981` is this round's own read, not a carried
forward one. (The R168 payload, prepared ~03:55 JST, cited unstable at
`9c76981` because CI was still running; the head has since finished CI and
this round's fresh read agrees the head is clean. The R168 payload was NOT refreshed by
the main flow — `cmp` against its `.bak-prepost-20261122` is byte-identical
this round.)

R169 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `9c76981` (527 commits / 2899 files /
  271227 additions; the fresh git derivation at `9c76981`, the fresh API
  read ~04:45 JST, and the merge-tree cross-check at `9c76981` are cited,
  with the fresh clean mergeable read at the new head disclosed
  above; live body R140; delta `8367e34..9c76981`: 5 paths, 364
  insertions, 11 deletions); one row appended — PR119 BODY RESTRUCTURE
  R168 (`7eeb790`/`9c76981`), recording that its payload was prepared
  after push ~03:55 JST (104.901 ký tự, sha `961611c2`,
  mergeable_state unstable tại `9c76981` lúc chuẩn bị — CI đang chạy, clean tại `8367e34`;
  JSON 123.295 byte < trần 131.072 — còn 7.777 byte, bản giữ tại
  `.bak-prepost-20261122`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read: byte-exact on the first
  read, 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — superseded, not posted; issue line re-read fresh
  this round (34 comments, latest ACK `6862732081`, no new direction;
  connector MCP get_comments page 1+2). The index now covers every
  block through `9c76981`; R169's own 2 commits fold in at the next index
  update (R170), disclosed in the index itself. The R169 note was
  appended after the R168 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `9c76981` · 527 · 2899 (with the fresh git derivation at `9c76981`,
  the fresh API read ~04:45 JST, and the fresh merge-tree cross-check at
  `9c76981`), plus the R168 paragraph in "Khối mới nhất" (811 ký tự,
  marked chưa đăng — live body is R140) and the R169 note. The stale index
  reference in "Về bản mô tả này" (head `8367e34`) is also fixed to
  `9c76981`, and the title line is extended to R168. Compaction (R168
  warning): the R139 paragraph (1.141 ký tự) is collapsed to one 377-ký-tự
  compact line (full detail stays in the delivery index), AND the new R168
  paragraph was trimmed to 811 ký tự (R167 was 914 — trim 103 ký tự, above
  the ≥ 50 required), so the body is 104.946 ký tự — net +129 vs R168 despite the new R168 paragraph. The live PR description is refreshed from this file in
  the posting round that follows R169 (owner tap) — the R140 body v2 now
  live is the base; only the R168 paragraph (posting note) + new head line
  are new vs live.
- **Checker** `check_pr119_restructure_r169_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R168 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R168 and R169 update notes are present
  (guarding the R140 replace-instead-of-append defect), and the
  compaction check extended from R168 (27 compact lines R139–R165
  present, each < 400 ký tự, body total < 105.000 ký tự — body is now
  104.946 ký tự). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R169_VALIDATION_20261122.json`).
  The checker passed 19/19 on its second run — the first run caught a real
  defect: the edit script's insertion glued the new R168 paragraph to the
  following R165 compact line (missing trailing newline), so R165 failed the
  per-round check; both files were restored from git, the script fixed
  (trailing newline on all three insertions), and re-run clean. The checker was
  written fresh (not sed-copied from R168) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `8367e34`/`ec66d5b`/`270874`/`2896`/`961604b`/`f85dd45` references in
  the checker — the R168 values) before the run — the R69 sed-order
  copy defect (mangled full COVER SHA) was avoided by construction. The
  `7eeb790`/`9c76981` hits in the checker are the intended assertions
  that the index row carries the R168 content/report SHAs. The edit
  script's budget check ran before any write (R166 lesson) and passed on
  its second run — the first run aborted before writing when the body
  projected 105.049 ký tự (49 over the ceiling), the R168 paragraph was
  trimmed by 104 ký tự, and the re-run passed with 54 ký tự of headroom.

## Verification

- Merge-tree `9c76981` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `241e7a4cc1d6b1a7ea85517c5caf1bb816868ded`. Merge-tree at the R169
  content head `a99d985` vs `f3db6b3`: exit 0, tree
  `3d4e2ca16d845bda572794e1c12e338c4a0b0dea`.
- Live PR state: API connector MCP read ~04:45 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `9c76981`; live body
  R140 (92.520 ký tự, sha `ddbe32ff` byte-exact on the first read this round, 0 U+FFFD —
  no transient corruption this time, like R168;
  updated_at 2026-11-21T18:46:31Z — changed since the R168 push, head moved); mergeable_state
  **clean** at the new head (fresh read this round; `mergeable` field null via MCP).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1+2, ~04:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R169 block (`8367e34..a99d985`) 6 paths / 0 violations
  (R168 report 2 files + R168 checker 1 + R169 content 3); content-only
  block (`9c76981..a99d985`) 3 paths / 0 violations; cumulative at the R169
  content commit `a99d985` 2900 paths / 1 violation — the known
  `.gitattributes` merge-base artifact only (byte-identical with
  integration `f3db6b3`, sha256 `23352e4c…` on both sides, re-verified
  at `a99d985`). Merge-tree at the R169 content head `a99d985` vs
  `f3db6b3`: exit 0, tree `3d4e2ca1…`.
- Transient notes: no rate-limit 403 on any MCP read this round (pulls +
  issue comments both 200 first try). The first `issue_read` attempt
  failed fast on a wrong parameter name (`issueNumber` instead of
  `issue_number`) — retried with the correct name and succeeded; no
  data was misread. Edit-script re-run guard was triggered once (glued-line
  defect, see above) — files restored from git and the script fixed before
  the clean run.
- Ceiling discipline: the R168 payload JSON measured 123.295 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (7.777 byte headroom). The projected R169 payload JSON is ~123,400 byte
  (measured exactly at payload build, after push). Body v2 is now 104.946
  ký tự (< 105.000) — 54 ký tự of headroom. R170 warning:
  headroom is now only 54 ký tự; the next round must collapse R138 AND
  trim the new paragraph by ≥ 60 ký tự (target ≤ 750 ký tự for the R169
  paragraph) — collapsing R138 alone leaves the body ~105.002 ký tự, just
  past the ceiling.

## Next

Posting round (owner tap): PR #119 description refresh to the R169 body
v2 (R168 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r169.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R169 push (title
ending "+ R169", built by replacing the "+ R140" suffix — not appending;
body = body v2 R169 in repo, head line refreshed to head after R169 push).
This run started ~04:40 JST — PAST working hours (09:00–21:30 JST), so the
R169 payload is HELD for working hours, not presented (like R142/R164/R165/R166/R167/R168) — trình bày thuộc về luồng chính
khi giờ làm việc trở lại, hoặc R170 supersede. Do not present the superseded R168 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167 and R168 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R169: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
