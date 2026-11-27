# MEDIA-02 — PR #119 Body Restructure R171: delivery index + body v2 coverage to `f1fa774`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `f1fa774` (PR119 BODY RESTRUCTURE R170 report). Content commit: `a3c4e6a`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R171 does

R170 left the disclosed gap: the delivery index covered 529 commits to
`9756ec0`; R170's own 2 commits were to fold in at R171. The R170 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~06:45 JST) shows the
live PR title ends "+ R140", head `f1fa774`, mergeable_state **unstable**
(CI running on the new head; the MCP read returns
mergeable_state unstable with the `mergeable` field null), updated_at
2026-11-21T20:48:37Z, and the live body is still R140. Read-path note:
like R169/R170, this round's FIRST MCP read returned the live body
byte-exact at once — 92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD, no
transient read-path corruption this round. The R170 payload is therefore
superseded, not posted — do not post it. No new Codex/owner direction has
landed on issue #116: this round's fresh read of the comments API via
connector MCP (`issue_read` get_comments, page 1 with perPage 100 = all 34
comments in one page, ~06:45 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `f1fa774` (~06:45 JST): `git rev-list --count
cf17178..f1fa774` = 531 commits, `git diff --name-only` = 2905 files,
`--shortstat` = 271956 insertions, 0 deletions. `git merge-tree
--write-tree` `f1fa774` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `d30adc958aaca46d4e268b62ac16c238b80cea23`. Unlike R170, this round
did NOT get a fresh clean mergeable read at the new head — mergeable_state
is unstable because CI is still running on `f1fa774`, so the clean verdict
cited at `9756ec0` is R170's own fresh read (~05:45 JST), carried forward
and disclosed as such, not this round's. (The R170 payload, prepared
~05:49 JST, cited unstable at `f1fa774` for the same reason; the head has
not finished CI since. The R170 payload was NOT refreshed by the main flow
— `cmp` against its `.bak-prepost-20261122` is byte-identical this round.)

R171 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `f1fa774` (531 commits / 2905 files /
  271956 additions; the fresh git derivation at `f1fa774`, the fresh API
  read ~06:45 JST, and the merge-tree cross-check at `f1fa774` are cited,
  with the fresh unstable mergeable read at the new head disclosed
  above; live body R140; delta `9756ec0..f1fa774`: 5 paths, 376
  insertions, 11 deletions); one row appended — PR119 BODY RESTRUCTURE
  R170 (`bc371ed`/`f1fa774`), recording that its payload was prepared
  after push ~05:49 JST (105.049 ký tự, sha `4f91bd4c`,
  mergeable_state unstable tại `f1fa774` lúc chuẩn bị — CI đang chạy, clean tại `9756ec0`;
  JSON 123.378 byte < trần 131.072 — còn 7.694 byte, bản giữ tại
  `.bak-prepost-20261122`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read: byte-exact on the first
  read, 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — superseded, not posted; issue line re-read fresh
  this round (34 comments, latest ACK `6862732081`, no new direction;
  connector MCP get_comments page 1, perPage 100). The index now covers every
  block through `f1fa774`; R171's own 2 commits fold in at the next index
  update (R172), disclosed in the index itself. The R171 note was
  appended after the R170 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `f1fa774` · 531 · 2905 (with the fresh git derivation at `f1fa774`,
  the fresh API read ~06:45 JST, and the fresh merge-tree cross-check at
  `f1fa774`), plus the R170 paragraph in "Khối mới nhất" (746 ký tự,
  marked chưa đăng — live body is R140) and the R171 note. The stale index
  reference in "Về bản mô tả này" (head `9756ec0`) is also fixed to
  `f1fa774`, and the title line is extended to R170. Compaction (R170
  warning — applied with a margin): the R137 paragraph (1.248 ký tự) is
  collapsed to one 382-ký-tự compact line AND the R136 paragraph (918 ký
  tự) is collapsed to one 333-ký-tự compact line (full detail stays in the
  delivery index) — two compactions in one round follow the R164/R165/R167
  precedent; the R170 warning's minimum (R137 alone + paragraph ≤ 750) would
  have left the body at ~104,99x, only a few chars under the ceiling, while
  the second compaction leaves 576 chars of headroom. The new R170
  paragraph was trimmed to 746 ký tự (R169 was 743), so the body is
  104.424 ký tự — net −541 vs R170 despite the new R170 paragraph. The live
  PR description is refreshed from this file in the posting round that
  follows R171 (owner tap) — the R140 body v2 now live is the base; only
  the R170 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r171_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R170 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R170 and R171 update notes are present
  (guarding the R140 replace-instead-of-append defect), and the
  compaction check extended from R170 (30 compact lines R136–R165
  present, each < 400 ký tự, body total < 105.000 ký tự — body is now
  104.424 ký tự). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R171_VALIDATION_20261122.json`).
  The checker passed 19/19 on its FIRST run this round. The checker was
  written fresh (not sed-copied from R170) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `9756ec0`/`a99d985`/`271591`/`3414e4a1`/`529 commit`/`2902 file`
  references in the checker — the R170 values) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The `bc371ed`/`f1fa774` hits in the checker are the
  intended assertions that the index row carries the R170 content/report
  SHAs. The edit script's budget check ran before any write (R166 lesson):
  the first run aborted before writing when the R170 paragraph measured
  756 ký tự (6 over the ≤ 750 target); after trimming the paragraph by
  10 ký tự the second run passed with 576 ký tự of headroom and wrote.

## Verification

- Merge-tree `f1fa774` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `d30adc958aaca46d4e268b62ac16c238b80cea23`. Merge-tree at the R171
  content head `a3c4e6a` vs `f3db6b3`: exit 0, tree
  `88ac58574b92ca959fc7e369a61a42b7a4e1f067`.
- Live PR state: API connector MCP read ~06:45 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `f1fa774`; live body
  R140 (92.520 ký tự, sha `ddbe32ff` byte-exact on the first read this round, 0 U+FFFD —
  no transient corruption this time, like R169/R170;
  updated_at 2026-11-21T20:48:37Z — changed since the R170 push, head moved); mergeable_state
  **unstable** at the new head (fresh read this round; `mergeable` field null via MCP; CI running);
  last clean at `9756ec0` (R170's fresh read ~05:45 JST).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~06:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R171 block (`9756ec0..a3c4e6a`) 6 paths / 0 violations
  (R170 report 2 files + R170 checker 1 + R171 content 3); content-only
  block (`f1fa774..a3c4e6a`) 3 paths / 0 violations; cumulative at the R171
  content commit `a3c4e6a` 2906 paths / 1 violation — the known
  `.gitattributes` merge-base artifact only (byte-identical with
  integration `f3db6b3`, sha256 `23352e4c…` on both sides, re-verified
  at `a3c4e6a`). Merge-tree at the R171 content head `a3c4e6a` vs
  `f3db6b3`: exit 0, tree `88ac5857…`.
- Transient notes: no rate-limit 403 on any MCP read this round (pulls +
  issue comments both 200 first try). The first `pull_request_read`
  attempt failed fast on a wrong method name (`get_pull_request` instead
  of `get`) — retried with the correct name and succeeded; no data was
  misread. `git ls-remote` for `refs/pull/119/head` failed once with a
  connection reset via the proxy — retried later; the PR head was verified
  via the API read instead (`f1fa774`, matching local/origin). Edit-script
  re-run guard was triggered once (paragraph budget, see above) — files
  untouched until the clean run.
- Ceiling discipline: the R170 payload JSON measured 123.378 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (7.694 byte headroom). The projected R171 payload JSON is ~123,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.424
  ký tự (< 105.000) — 576 ký tự of headroom. R172 warning:
  headroom is now 576 ký tự; the next round should collapse R135 (857
  ký tự → ~377) and keep the new paragraph ≤ 750 ký tự — that leaves the
  body ~104,7xx, comfortably under the ceiling.

## Next

Posting round (owner tap): PR #119 description refresh to the R171 body
v2 (R170 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r171.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R171 push (title
ending "+ R171", built by replacing the "+ R140" suffix — not appending;
body = body v2 R171 in repo, head line refreshed to head after R171 push).
This run started ~06:40 JST — OUTSIDE working hours (09:00–21:30 JST), so the
R171 payload is HELD for working hours, not presented (like R142/R164–R170) — trình bày thuộc về luồng chính
khi giờ làm việc trở lại, hoặc R172 supersede. Do not present the superseded R170 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169 and R170 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R171: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
