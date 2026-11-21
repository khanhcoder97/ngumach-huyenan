# MEDIA-02 — PR #119 Body Restructure R168: delivery index + body v2 coverage to `8367e34`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `8367e34` (PR119 BODY RESTRUCTURE R167 report). Content commit: `7eeb790`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R168 does

R167 left the disclosed gap: the delivery index covered 523 commits to
`ec66d5b`; R167's own 2 commits were to fold in at R168. The R167 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~03:45 JST) shows the
live PR title ends "+ R140", head `8367e34`, mergeable_state **clean**
(fresh read at the new head this round; the MCP read returns
mergeable_state clean with the `mergeable` field null), updated_at
2026-11-21T17:48:35Z, and the live body is still R140. Read-path note:
unlike R164/R166/R167, this round's FIRST MCP read returned the live body
byte-exact at once — 92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD, no
transient read-path corruption this round. The R167 payload is therefore
superseded, not posted — do not post it. No new Codex/owner direction has
landed on issue #116: this round's fresh read of the comments API via
connector MCP (`issue_read` get_comments, page 1+2, ~03:45 JST) agrees:
still 34 comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2,
updated_at 2026-11-13T19:24:48Z); no new direction since Gói 39
(`6815238814`).

Fresh derivation at `8367e34` (~03:45 JST): `git rev-list --count
cf17178..8367e34` = 525 commits, `git diff --name-only` = 2896 files,
`--shortstat` = 270874 insertions, 0 deletions. `git merge-tree
--write-tree` `8367e34` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `eb1e03d111de662b7c0b3fc4f05ec6eded7c246a`. Like R167, this round
DID get a fresh API mergeable read at the new head — mergeable_state clean
— so the clean verdict at `8367e34` is this round's own read, not a carried
forward one. (The R167 payload, prepared ~02:50 JST, cited unstable at
`8367e34` because CI was still running; the head has since finished CI and
this round's fresh read agrees the head is clean. The R167 payload was NOT refreshed by
the main flow — `cmp` against its `.bak-prepost-20261122` is byte-identical
this round.)

R168 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `8367e34` (525 commits / 2896 files /
  270874 additions; the fresh git derivation at `8367e34`, the fresh API
  read ~03:45 JST, and the merge-tree cross-check at `8367e34` are cited,
  with the fresh clean mergeable read at the new head disclosed
  above; live body R140; delta `ec66d5b..8367e34`: 5 paths, 369
  insertions, 12 deletions); one row appended — PR119 BODY RESTRUCTURE
  R167 (`961604b`/`8367e34`), recording that its payload was prepared
  after push ~02:50 JST (104.739 ký tự, sha `b5182750`,
  mergeable_state unstable tại `8367e34` lúc chuẩn bị — CI đang chạy, clean tại `ec66d5b`;
  JSON 123.157 byte < trần 131.072 — còn 7.915 byte, bản giữ tại
  `.bak-prepost-20261122`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read: byte-exact on the first
  read, 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — superseded, not posted; issue line re-read fresh
  this round (34 comments, latest ACK `6862732081`, no new direction;
  connector MCP get_comments page 1+2). The index now covers every
  block through `8367e34`; R168's own 2 commits fold in at the next index
  update (R169), disclosed in the index itself. The R168 note was
  appended after the R167 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `8367e34` · 525 · 2896 (with the fresh git derivation at `8367e34`,
  the fresh API read ~03:45 JST, and the fresh merge-tree cross-check at
  `8367e34`), plus the R167 paragraph in "Khối mới nhất" (914 ký tự,
  marked chưa đăng — live body is R140) and the R168 note. The stale index
  reference in "Về bản mô tả này" (head `ec66d5b`) is also fixed to
  `8367e34`, and the title line is extended to R167. Compaction (R167
  warning): the R140 paragraph (1.189 ký tự) is collapsed to one 350-ký-tự
  compact line (full detail stays in the delivery index), so the body is
  104.817 ký tự — net +121 vs R167 despite the new R167 paragraph. The live PR description is refreshed from this file in
  the posting round that follows R168 (owner tap) — the R140 body v2 now
  live is the base; only the R167 paragraph (posting note) + new head line
  are new vs live.
- **Checker** `check_pr119_restructure_r168_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R167 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R167 and R168 update notes are present
  (guarding the R140 replace-instead-of-append defect), and the
  compaction check extended from R167 (26 compact lines R140–R165
  present, each < 400 ký tự, body total < 105.000 ký tự — body is now
  104.817 ký tự). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R168_VALIDATION_20261122.json`).
  The checker passed 19/19 on its first run. The checker was
  written fresh (not sed-copied from R167) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `ec66d5b`/`9113594`/`270517`/`2893`/`f85dd45` references in
  the checker — the R167 values) before the run — the R69 sed-order
  copy defect (mangled full COVER SHA) was avoided by construction. The
  `961604b`/`8367e34` hits in the checker are the intended assertions
  that the index row carries the R167 content/report SHAs. The edit
  script's budget check ran before any write (R166 lesson) and passed on
  its first run — no file was restored from git this round.

## Verification

- Merge-tree `8367e34` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `eb1e03d111de662b7c0b3fc4f05ec6eded7c246a`. Merge-tree at the R168
  content head `7eeb790` vs `f3db6b3`: exit 0, tree
  `23a46180c1936c23e61f013d4b1f614d725d8f6b`.
- Live PR state: API connector MCP read ~03:45 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `8367e34`; live body
  R140 (92.520 ký tự, sha `ddbe32ff` byte-exact on the first read this round, 0 U+FFFD —
  no transient corruption this time, unlike R164/R166/R167;
  updated_at 2026-11-21T17:48:35Z — changed since the R167 push, head moved); mergeable_state
  **clean** at the new head (fresh read this round; `mergeable` field null via MCP).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1+2, ~03:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R168 block (`ec66d5b..7eeb790`) 6 paths / 0 violations
  (R167 report 2 files + R167 checker 1 + R168 content 3); cumulative at the R168
  content commit `7eeb790` 2897 paths / 1 violation — the known
  `.gitattributes` merge-base artifact only (byte-identical with
  integration `f3db6b3`, sha256 `23352e4c…` on both sides, re-verified
  at `7eeb790`). Merge-tree at the R168 content head `7eeb790` vs
  `f3db6b3`: exit 0, tree `23a46180…`.
- Transient notes: no rate-limit 403 on any MCP read this round (pulls +
  issue comments both 200 first try). The first `pull_request_read` attempt
  failed fast on a wrong parameter name (`pull_number` instead of
  `pullNumber`) — retried with the correct name and succeeded; no
  data was misread. Edit-script re-run guard was not triggered (no
  duplicate paragraph or row).
- Ceiling discipline: the R167 payload JSON measured 123.157 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (7.915 byte headroom). The projected R168 payload JSON is ~123,700 byte
  (measured exactly at payload build, after push). Body v2 is now 104.817
  ký tự (< 105.000) — 183 ký tự of headroom. R169 warning:
  headroom is now only 183 ký tự; the next round must collapse R139 AND
  trim the new paragraph by ≥ 50 ký tự — collapsing R139 alone leaves the
  body ~105.030 ký tự, still past the ceiling.

## Next

Posting round (owner tap): PR #119 description refresh to the R168 body
v2 (R167 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r168.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R168 push (title
ending "+ R168", built by replacing the "+ R140" suffix — not appending;
body = body v2 R168 in repo, head line refreshed to head after R168 push).
This run started ~03:40 JST — PAST working hours (09:00–21:30 JST), so the
R168 payload is HELD for working hours, not presented (like R142/R164/R165/R166/R167) — trình bày thuộc về luồng chính
khi giờ làm việc trở lại, hoặc R169 supersede. Do not present the superseded R167 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166 and R167 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R168: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
