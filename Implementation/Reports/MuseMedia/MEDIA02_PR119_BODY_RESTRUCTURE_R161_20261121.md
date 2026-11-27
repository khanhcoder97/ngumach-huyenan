# MEDIA-02 — PR #119 Body Restructure R161: delivery index + body v2 coverage to `285d257`

Date: 2026-11-21 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `285d257` (PR119 BODY RESTRUCTURE R160 report). Content commit: `b296b8b`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R161 does

R160 left the disclosed gap: the delivery index covered 509 commits to
`cc98913`; R160's own 2 commits were to fold in at R161. The R160 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~18:40 JST) shows the
live PR title ends "+ R140", head `285d257`, mergeable_state **clean**
(fresh read at the new head this round; the MCP read returns
mergeable_state clean with the `mergeable` field null), updated_at
2026-11-21T08:46:29Z, and the live body is still R140. This round's MCP read returned
the live body at 92.520 ký tự, sha256 `ddbe32ff` — byte-exact R140 this
round. The R160 payload is therefore
superseded, not posted — do not post it.
No new Codex/owner direction has landed on issue #116: this round's fresh
read of the comments API via connector MCP (`issue_read` get_comments,
perPage=100, ~18:40 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `285d257` (~18:40 JST): `git rev-list --count
cf17178..285d257` = 511 commits, `git diff --name-only` = 2875 files,
`--shortstat` = 268376 insertions, 0 deletions. `git merge-tree
--write-tree` `285d257` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `ff3a6dee4e97b80f419b43aa51b1e89f1fb81ef71`. Like R160, this round
DID get a fresh API mergeable read at the new head — mergeable_state clean
— so the clean verdict at `285d257` is this round's own read, not a carried
forward one. (The R160 payload, prepared ~17:47 JST, cited unstable at
`285d257` with CI still running; CI has since finished and this round's
fresh read agrees the head is clean. The R160 payload was NOT refreshed by
the main flow — `cmp` against its `.bak-prepost-20261121` is byte-identical
this round.)

R161 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `285d257` (511 commits / 2875 files /
  268376 additions; the fresh git derivation at `285d257`, the fresh API
  read ~18:40 JST, and the merge-tree cross-check at `285d257` are cited,
  with the fresh clean mergeable read at the new head disclosed
  above; live body R140; delta `cc98913..285d257`: 5 paths, 374
  insertions, 9 deletions); one row appended — PR119 BODY RESTRUCTURE
  R160 (`ed3e535`/`285d257`), recording that its payload was prepared
  after push ~17:47 JST (103.959 ký tự, sha `2c88cba7`,
  mergeable_state unstable tại `285d257` — API ~17:47 JST, CI đang chạy,
  lần clean gần nhất tại `cc98913` + merge-tree tại `285d257`; JSON
  122.323 byte < trần 131.072 — còn 8.749 byte, bản giữ tại
  `.bak-prepost-20261121`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read, byte-exact,
  sha `ddbe32ff`) — superseded, not posted; issue line re-read fresh
  this round (34 comments, latest ACK `6862732081`, no new direction;
  connector MCP get_comments perPage=100). The index now covers every
  block through `285d257`; R161's own 2 commits fold in at the next index
  update (R162), disclosed in the index itself. The R161 note was
  appended after the R160 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `285d257` · 511 · 2875 (with the fresh git derivation at `285d257`,
  the fresh API read ~18:40 JST, and the fresh merge-tree cross-check at
  `285d257`), plus the R160 paragraph in "Khối mới nhất" (911 ký tự,
  marked chưa đăng — live body is R140) and the R161 note. The stale index
  reference in "Về bản mô tả này" (head `cc98913`) is also fixed to
  `285d257`, and the title line is extended to R160 (appended before the
  closing paren — the R120 append-vs-replace defect concerns the live PR
  title suffix, not this title list; the R161 checker passed on the first
  run, no title defect this round). Compaction extended (R160 warning):
  the R156 (762 ký tự) and R157 (838 ký tự) paragraphs are collapsed to
  one 294-ký-tự compact line each (full detail stays in the delivery
  index), so the body is 103.835 ký tự — net +35 vs R160 despite the new
  R160 paragraph. The live PR description is refreshed from this file in
  the posting round that follows R161 (owner tap) — the R140 body v2 now
  live is the base; only the R160 paragraph (posting note) + new head line
  are new vs live.
- **Checker** `check_pr119_restructure_r161_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R160 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R160 and R161 update notes are present
  (guarding the R140 replace-instead-of-append defect), and the
  compaction check extended from R158 (16 compact lines R142–R157
  present, each < 400 ký tự, body total < 105.000 ký tự — body is now
  103.835 ký tự). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R161_VALIDATION_20261121.json`).
  First checker run PASS 19/19 — no defect this round. The checker was
  written fresh (not sed-copied from R160) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `cc98913`/`63aa3a5`/`c1bd8fcd`/`268011` references in
  the checker — the R160 values) before the run — the R69 sed-order
  copy defect (mangled full COVER SHA) was avoided by construction. The
  `ed3e535`/`285d257` hits in the checker are the intended assertions
  that the index row carries the R160 content/report SHAs.

## Verification

- Merge-tree `285d257` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `ff3a6dee4e97b80f419b43aa51b1e89f1fb81ef71`. Merge-tree at the R161
  content head `b296b8b` vs `f3db6b3`: exit 0, tree
  `642615d82f7c9b29af0ebca831c154e17260185e`.
- Live PR state: API connector MCP read ~18:40 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `285d257`; live body
  R140 (92.520 ký tự, sha `ddbe32ff` byte-exact this round, updated_at
  2026-11-21T08:46:29Z — unchanged since the R160 push); mergeable_state
  **clean** at the new head (fresh read this round; `mergeable` field null via MCP).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, perPage=100, ~18:40 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R161 block 3 paths / 0 violations; cumulative at the R161
  content commit `b296b8b` 2876 paths / 1 violation — the known
  `.gitattributes` merge-base artifact only (byte-identical with
  integration `f3db6b3`, sha256 `23352e4c…` on both sides, re-verified
  at `b296b8b`). Merge-tree at the R161 content head `b296b8b` vs
  `f3db6b3`: exit 0, tree `642615d8…`.
- Transient notes: no rate-limit 403 on either MCP read this round
  (pulls + issue comments both 200 first try). Edit-script re-run
  idempotent (`changed: 0`) — no duplicated paragraph or row.
  Observation (not a defect, method unchanged): the API
  `pull_request_read` returns base sha `f383233` (Merge PR #118) while
  `git ls-remote` / FETCH_HEAD still show the integration branch tip at
  `f3db6b3` (Merge PR #131) — the PR's base sha lags the branch tip;
  merge-tree and scope audit keep using the live tip `f3db6b3`, as in all
  prior rounds.
- Ceiling discipline: the R160 payload JSON measured 122.323 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (8.749 byte headroom). The projected R161 payload JSON is ~123.300 byte
  (measured exactly at payload build, after push). Body v2 is now 103.835
  ký tự (< 105.000) — the R156/R157 compaction bought back ~900 ký tự
  this round, so the net growth is only +35/round while one old paragraph
  is compacted per round; R162 should compact R158 (837 ký tự) next to
  keep the same headroom. No further compaction is scheduled in this
  round: the older full paragraphs (R141 and below, R158–R160) are left
  untouched unless the ceiling tightens again.

## Next

Posting round (owner tap): PR #119 description refresh to the R161 body
v2 (R160 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r161.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R161 push (title
ending "+ R161", built by replacing the "+ R140" suffix — not appending;
body = body v2 R161 in repo, head line refreshed to head after R161 push).
This run started ~18:40 JST — working hours (09:00–21:30 JST), so the
R161 payload is READY for in-hours presentation by the main flow; do not
present the superseded R160 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159 and R160 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R161: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
