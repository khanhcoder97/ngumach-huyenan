# MEDIA-02 — PR #119 Body Restructure R158: delivery index + body v2 coverage to `cd1158c` + gọn R142–R155

Date: 2026-11-21 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `cd1158c` (PR119 BODY RESTRUCTURE R157 report). Content commit: `3a93b21`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R158 does

R157 left the disclosed gap: the delivery index covered 503 commits to
`228440e`; R157's own 2 commits were to fold in at R158. The R157 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~15:45 JST) shows the
live PR title ends "+ R140", head `cd1158c`, mergeable_state **clean**
(fresh read at the new head this round; the MCP read returns
mergeable_state clean with the `mergeable` field null), updated_at
2026-11-21T05:48:21Z, and the live body is still R140. This round's MCP read returned
the live body at 92.520 ký tự, sha256 `ddbe32ff` — byte-exact R140 this
round. The R157 payload is therefore
superseded, not posted — do not post it.
No new Codex/owner direction has landed on issue #116: this round's fresh
read of the comments API via connector MCP (`issue_read` get_comments,
perPage=100, ~15:45 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `cd1158c` (~15:45 JST): `git rev-list --count
cf17178..cd1158c` = 505 commits, `git diff --name-only` = 2866 files,
`--shortstat` = 267282 insertions, 0 deletions. `git merge-tree
--write-tree` `cd1158c` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `f3931105933d65e610a48bc417e083d1b6bd476e`. Like R157, this round
DID get a fresh API mergeable read at the new head — mergeable_state clean
— so the clean verdict at `cd1158c` is this round's own read, not a carried
forward one. (The R157 payload, prepared ~14:48 JST, cited unstable at
`cd1158c` with CI still running; CI has since finished and this round's
fresh read agrees the head is clean.)

R158 closes the gap and executes the compaction the R157 report flagged
as mandatory:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `cd1158c` (505 commits / 2866 files /
  267282 additions; the fresh git derivation at `cd1158c`, the fresh API
  read ~15:45 JST, and the merge-tree cross-check at `cd1158c` are cited,
  with the fresh clean mergeable read at the new head disclosed
  above; live body R140; delta `228440e..cd1158c`: 5 paths, 344
  insertions, 9 deletions); one row appended — PR119 BODY RESTRUCTURE
  R157 (`fcceee5`/`cd1158c`), recording that its payload was prepared
  after push ~14:48 JST (111.128 ký tự, sha `ac3b6e44`,
  mergeable_state unstable tại `cd1158c` — API ~14:48 JST, CI đang chạy,
  lần clean gần nhất tại `228440e` + merge-tree tại `cd1158c`; JSON
  130.851 byte < trần 131.072 — chỉ còn 221 byte, bản giữ tại
  `.bak-prepost-20261121`), that it was NOT refreshed by the main
  flow (verified by `cmp` of the live payload file against its `.bak`
  copy this round: byte-identical), that it was NOT posted — live body
  still R140 (verified by this round's API read, byte-exact, sha
  `ddbe32ff`) — superseded, not posted; issue line re-read fresh this
  round (34 comments, latest ACK `6862732081`, no new direction;
  connector MCP get_comments perPage=100). The index now covers every
  block through `cd1158c`; R158's own 2 commits fold in at the next
  index update (R159), disclosed in the index itself. The R158 note was
  appended after the R157 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `cd1158c` · 505 · 2866 (with the fresh git derivation at `cd1158c`,
  the fresh API read ~15:45 JST, and the fresh merge-tree cross-check at
  `cd1158c`), plus the R157 paragraph in "Khối mới nhất" (838 ký tự,
  marked chưa đăng — live body is R140) and the R158 note. The stale index
  reference in "Về bản mô tả này" (head `228440e`) is also fixed to
  `cd1158c`, and the title line is extended to R157 (appended before the
  closing paren — the R120 append-vs-replace defect concerns the live PR
  title suffix, not this title list; the R158 checker passed on the first
  run, no title defect this round). The live PR description is refreshed
  from this file in the posting round that follows R158 (owner tap) — the
  R140 body v2 now live is the base; only the R157 paragraph (posting
  note) + new head line + the compaction below are new vs live.
- **Compaction (gọn body, bắt buộc theo cảnh báo trần ở R157):** the
  "Khối mới nhất" paragraphs R142–R155 (14 đoạn, 14.887 ký tự) are
  collapsed to one compact line each (294–374 ký tự/đoạn, tổng 4.572 ký
  tự — tiết kiệm 10.315 ký tự trong mục này). Each compact line keeps the
  audit facts: content SHA, report/head SHA, coverage head, checker
  PASS 19/19, payload size + sha, mergeable state, superseded status,
  live body still R140 — plus the round-specific note where one existed
  (R152 main-flow refresh `afa35914`; R151/R148 MCP "Ă" decoding
  artifact, 92.521 ký tự; quiet-hours non-presentation for R142–R151).
  Full detail stays in the delivery index table rows, which the body
  already cites as the source of truth; a "Ghi chú R158" line under the
  section header records the compaction in place. Net effect on the body
  v2 file: 111.062 → 101.850 ký tự (tiết kiệm 9.212 ký tự sau khi cộng
  đoạn R157 838 ký tự + dòng ghi chú + làm tươi dòng head), 129.508 →
  118.688 byte trên đĩa. Projected R158 payload JSON ~120.000 byte —
  under the 131.072-byte ceiling by ~11.000 byte (measured exactly at
  payload build, after push). At ~+1.000 byte/round this restores ~10
  rounds of headroom; the title line (R2–R157 list, ~4.900 ký tự,
  +31/round) needs no trimming yet.
- **Checker** `check_pr119_restructure_r158_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R157 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R157 and R158 update notes are present
  (guarding the R140 replace-instead-of-append defect), and a new
  compaction check (14 compact lines present, each < 400 ký tự, body
  total < 105.000 ký tự). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R158_VALIDATION_20261121.json`).
  First checker run PASS 19/19 — no defect this round. The checker was
  written fresh (not sed-copied from R157) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `228440e`/`a36d89a`/`266947`/`92d59c16`/`0cfe29c`/`ca5e1e3` references in
  the checker — the R157 values) before the run — the R69 sed-order
  copy defect (mangled full COVER SHA) was avoided by construction. The
  `fcceee5`/`cd1158c` hits in the checker are the intended assertions
  that the index row carries the R157 content/report SHAs.

## Verification

- Merge-tree `cd1158c` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `f3931105933d65e610a48bc417e083d1b6bd476e`. Merge-tree at the R158
  content head `3a93b21` vs `f3db6b3`: exit 0, tree
  `a72d522a9ed7437d0a545663f5fbff864d8829c7`.
- Live PR state: API connector MCP read ~15:45 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `cd1158c`; live body
  R140 (92.520 ký tự, sha `ddbe32ff` byte-exact this round, updated_at
  2026-11-21T05:48:21Z — the head moved when the R157 report commit was
  pushed ~14:48 JST); mergeable_state **clean** at the new head (fresh
  read this round; `mergeable` field null via MCP).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, perPage=100, ~15:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R158 block 3 paths / 0 violations; cumulative at the R158
  content commit `3a93b21` 2867 paths / 1 violation — the known
  `.gitattributes` merge-base artifact only (byte-identical with
  integration `f3db6b3`, sha256 `23352e4c…` on both sides, re-verified
  at `3a93b21`). Merge-tree at the R158 content head `3a93b21` vs
  `f3db6b3`: exit 0, tree `a72d522a…`.
- Transient notes: no rate-limit 403 on either MCP read this round
  (pulls + issue comments both 200 first try). Edit-script idempotency:
  the first re-run printed `changed: 2` — the line-prefix guard
  re-fired on the two lines whose new text shares the old line's prefix
  (index milestone counts line, index mergeable line), replacing each
  with byte-identical content (a no-op, verified by `git diff`
  afterwards); the guard was fixed (check the exact new line first),
  and the next re-run printed `changed: 0`, no duplicated paragraph
  or row. Observation (not a defect, method unchanged): the API
  `pull_request_read` returns base sha `f383233` (Merge PR #118) while
  `git ls-remote` / FETCH_HEAD still show the integration branch tip at
  `f3db6b3` (Merge PR #131) — the PR's base sha lags the branch tip;
  merge-tree and scope audit keep using the live tip `f3db6b3`, as in all
  prior rounds.
- Ceiling discipline (acted on this round): the R157 payload JSON
  measured 130.851 byte vs the 131.072-byte transport ceiling (221 byte
  headroom). The R142–R155 compaction above restores ~11.000 byte
  headroom; the projected R158 payload JSON is ~120.000 byte (measured
  exactly at payload build, after push). No further compaction is
  scheduled: the next rounds add ~1.000 byte each, and the older full
  paragraphs (R141 and below) are left untouched unless the ceiling
  tightens again.

## Next

Posting round (owner tap): PR #119 description refresh to the R158 body
v2 (R157 posting note + new head line + R142–R155 compaction are the only
new parts vs the live R140 body). Payload `pr119_update_body_v2_r158.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R158 push (title
ending "+ R158", built by replacing the "+ R140" suffix — not appending;
body = body v2 R158 in repo, head line refreshed to head after R158 push).
This run started ~15:40 JST — working hours (09:00–21:30 JST), so the
R158 payload is READY for in-hours presentation by the main flow; do not
present the superseded R157 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156 and R157 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R158: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
