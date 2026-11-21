# MEDIA-02 — PR #119 Body Restructure R172: delivery index + body v2 coverage to `a9e8475`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `a9e8475` (PR119 BODY RESTRUCTURE R171 report). Content commit: `3c40d93`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R172 does

R171 left the disclosed gap: the delivery index covered 531 commits to
`f1fa774`; R171's own 2 commits were to fold in at R172. The R171 body v2 was NOT posted — this
round's fresh API read (connector MCP `pull_request_read` get ~07:45 JST) shows the
live PR title ends "+ R140", head `a9e8475`, mergeable_state **clean**
(CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at
2026-11-21T21:47:55Z, and the live body is still R140. Read-path note:
unlike R169/R170/R171, this round's FIRST MCP read (truncated at 3.000
ký tự) showed the live title ending "+ R171" — inconsistent with the
unchanged body (R140, sha `ddbe32ff`) and updated_at; two full re-reads
immediately after returned byte-identical responses showing the title ends
"+ R140", body 92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD. The first read
was a transient read-path glitch of the same family as the U+FFFD
corruptions in R164/R167/R171 — a first anomalous read means re-read, not
a changed live body. The R171 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~07:45 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `a9e8475` (~07:45 JST): `git rev-list --count
cf17178..a9e8475` = 533 commits, `git diff --name-only` = 2908 files,
`--shortstat` = 272324 insertions, 0 deletions. `git merge-tree
--write-tree` `a9e8475` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `eb84118514fdcd1865ec79c0e02d51fba22cd367`. Unlike R171, this round
DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `a9e8475` (CI finished since the R171 push), so no carried-forward
clean verdict is needed this round. (The R171 payload, prepared ~06:52
JST, cited unstable at `a9e8475` for the same reason; the head has
finished CI since. The R171 payload was NOT refreshed by the main flow
— `cmp` against its `.bak-prepost-20261122` is byte-identical this round.)

R172 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `a9e8475` (533 commits / 2908 files /
  272324 additions; the fresh git derivation at `a9e8475`, the fresh API
  read ~07:45 JST, and the merge-tree cross-check at `a9e8475` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `f1fa774..a9e8475`: 5 paths, 380 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R171
  (`a3c4e6a`/`a9e8475`), recording that its payload was prepared after
  push ~06:52 JST (104.424 ký tự, sha `c5f137ec`, mergeable_state
  unstable tại `a9e8475` lúc chuẩn bị — CI đang chạy, clean tại `9756ec0`;
  JSON 122.570 byte < trần 131.072 — còn 8.502 byte, bản giữ tại
  `.bak-prepost-20261122`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read: two full
  re-reads byte-identical, 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) —
  superseded, not posted; issue line re-read fresh this round (34
  comments, latest ACK `6862732081`, no new direction; connector MCP
  get_comments page 1, perPage 100). The index now covers every block
  through `a9e8475`; R172's own 2 commits fold in at the next index
  update (R173), disclosed in the index itself. The R172 note was
  appended after the R171 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `a9e8475` · 533 · 2908 (with the fresh git derivation at `a9e8475`,
  the fresh API read ~07:45 JST, and the fresh merge-tree cross-check at
  `a9e8475`), plus the R171 paragraph in "Khối mới nhất" (743 ký tự,
  marked chưa đăng — live body is R140) and the R172 note. The stale index
  reference in "Về bản mô tả này" (head `f1fa774`) is also fixed to
  `a9e8475`, and the title line is extended to R171. Compaction (R171
  warning — applied with a margin): the R135 paragraph (857 ký tự) is
  collapsed to one 290-ký-tự compact line (full detail stays in the
  delivery index) — the new R171 paragraph was trimmed to 743 ký tự, so
  the body is 104.671 ký tự — net +247 vs R171 despite the new R171
  paragraph, headroom 329 ký tự. Paragraph order: the first edit-script
  run inserted the R171 paragraph BEFORE the R170 paragraph (insert_before
  — wrong for this section, which lists full paragraphs in ascending
  order R166..R170); caught by reading the file before commit, the
  paragraph was moved to AFTER R170, before the compact block — the new
  checker now asserts this ascending order explicitly. The live PR
  description is refreshed from this file in the posting round that
  follows R172 (owner tap) — the R140 body v2 now live is the base; only
  the R171 paragraph (posting note) + new head line are new vs live.
- **Checker** `check_pr119_restructure_r172_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R171 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R171 and R172 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R171 (31 compact lines R135–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.671 ký tự),
  and a new check that the R171 paragraph sits directly after R170
  (ascending full-paragraph order). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R172_VALIDATION_20261122.json`).
  The checker passed 19/19 on its FIRST run this round. The checker was
  written fresh (not sed-copied from R171) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `f1fa774`/`bc371ed`/`271956`/`d30adc95`/`531 commit`/`2905 file`
  references in the checker — the R171 values) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The `a3c4e6a`/`a9e8475` hits in the checker are the
  intended assertions that the index row carries the R171 content/report
  SHAs. The edit script's budget check ran before any write (R166 lesson):
  the run projected the body at 104.672 ký tự with 329 ký tự of headroom
  and wrote; the idempotency re-run aborted at the budget check
  (StopIteration — the old head line no longer exists after run 1) before
  any write, files already correct — the script should report changed: 0
  instead of crashing on re-run (R173 robustness note).

## Verification

- Merge-tree `a9e8475` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `eb84118514fdcd1865ec79c0e02d51fba22cd367`. Merge-tree at the R172
  content head `3c40d93` vs `f3db6b3`: exit 0, tree
  `f44c5712404fac0b6a05388ba59582ea74dbf029`.
- Live PR state: API connector MCP read ~07:45 JST — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `a9e8475`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, two full re-reads byte-identical,
  0 U+FFFD — first truncated read showed a different title suffix, see
  read-path note above; updated_at 2026-11-21T21:47:55Z — unchanged since
  the R171 push); mergeable_state **clean** at the new head (fresh read
  this round; `mergeable` field null via MCP; CI finished).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~07:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R172 block (`a9e8475..3c40d93`) 3 paths / 0 violations
  (index + body v2 + R172 checker); cumulative at the R172 content
  commit `3c40d93` 2909 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `3c40d93`).
  Merge-tree at the R172 content head `3c40d93` vs `f3db6b3`: exit 0,
  tree `f44c5712…`.
- Transient notes: no rate-limit 403 on any MCP read this round (pulls +
  issue comments both 200 first try). First truncated `pull_request_read`
  showed a wrong title suffix (see above) — resolved by two full
  byte-identical re-reads; do not treat a first anomalous read as a live
  change. Edit-script re-run guard crashed on the budget check (see
  above) — files untouched, no data lost.
- Ceiling discipline: the R171 payload JSON measured 122.570 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (8.502 byte headroom). The projected R172 payload JSON is ~123,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.671
  ký tự (< 105.000) — 329 ký tự of headroom. R173 warning:
  headroom is now 329 ký tự; the next round must collapse R134 and keep
  the new paragraph tight (≤ ~700 ký tự) — compacting R134 alone may not
  suffice, be ready to compact a second paragraph (R133) or trim harder.

## Next

Posting round (owner tap): PR #119 description refresh to the R172 body
v2 (R171 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r172.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R172 push (title
ending "+ R172", built by replacing the "+ R140" suffix — not appending;
body = body v2 R172 in repo, head line refreshed to head after R172 push).
This run started ~07:40 JST — OUTSIDE working hours (09:00–21:30 JST), so the
R172 payload is HELD for working hours, not presented (like R142/R164–R171) — trình bày thuộc về luồng chính
khi giờ làm việc trở lại, hoặc R173 supersede. Do not present the superseded R171 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170 and R171 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R172: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
