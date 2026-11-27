# MEDIA-02 — PR #119 Body Restructure R175: delivery index + body v2 coverage to `987cdb5`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `987cdb5` (PR119 BODY RESTRUCTURE R174 report). Content commit: `e07441d`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R175 does

R174 left the disclosed gap: the delivery index covered 537 commits to
`2bdd78d`; R174's own 2 commits were to fold in at R175. The R174 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~10:40 JST, first read 92.521 ký tự / 2 U+FFFD
from the transient read-path artifact, immediate re-read byte-exact) show the live PR title ends "+ R140", head
`987cdb5`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-22T00:49:32Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R174 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~10:40 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `987cdb5` (~10:40 JST): `git rev-list --count
cf17178..987cdb5` = 539 commits, `git diff --name-only` = 2917 files,
`--shortstat` = 273441 insertions, 0 deletions. `git merge-tree
--write-tree` `987cdb5` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `d63bce9c4cc7a9ebc4c7b8dda63af5474578c5f0`. Like R174, this round
DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `987cdb5` (CI finished since the R174 push), so no carried-forward
clean verdict is needed this round.

R175 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `987cdb5` (539 commits / 2917 files /
  273441 additions; the fresh git derivation at `987cdb5`, the fresh API
  read ~10:40 JST, and the merge-tree cross-check at `987cdb5` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `2bdd78d..987cdb5`: 5 paths, 378 insertions, 10
  deletions); one row appended — PR119 BODY RESTRUCTURE R174
  (`947b043`/`987cdb5`), recording that its payload was prepared after
  push ~09:50 JST (104.629 ký tự, sha `1d1584f2`, mergeable unstable tại
  `987cdb5`; JSON 122.656 byte < trần 131.072 — còn 8.416 byte, bản giữ tại
  `.bak-prepost-20261122`), that it WAS refreshed by the main flow
  (additions 273195 → 273441, body sha `1d1584f2` → `8e7e6c3b`, 104.629 ký tự
  không đổi — verified by diffing the payload against its `.bak` this
  round: the only differing line is the head line), that it was NOT posted
  — live body still R140 (verified by this round's API read: re-read
  byte-exact, 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; connector MCP get_comments page 1,
  perPage 100). The index now covers every block through `987cdb5`; R175's
  own 2 commits fold in at the next index update (R176), disclosed in the
  index itself. The R175 note was appended after the R174 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `987cdb5` · 539 · 2917 (with the fresh git derivation at `987cdb5`,
  the fresh API read ~10:40 JST, and the fresh merge-tree cross-check at
  `987cdb5`), plus the R174 paragraph in "Khối mới nhất" (691 ký tự,
  marked chưa đăng — live body is R140) and the R175 note. The stale index
  reference in "Về bản mô tả này" (head `2bdd78d`) is also fixed to
  `987cdb5`, and the title line is extended to R174. Compaction (R174
  warning — applied with a margin): the R131 paragraph (809 ký tự) is
  collapsed to one 287-ký-tự compact line (full detail stays in the
  delivery index) — the new R174 paragraph was trimmed to 691 ký tự, so
  the body is 104.879 ký tự — net +287 vs R174 despite the new R174
  paragraph, headroom 121 ký tự.
  Paragraph order: the R174 paragraph sits directly after R173
  (ascending full-paragraph order R166..R174), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R175 (owner tap) — the R140 body v2 now live
  is the base; only the R174 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r175_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R174 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R174 and R175 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R174 (35 compact lines R131–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.879 ký tự),
  and a check that the R174 paragraph sits directly after R173
  (ascending full-paragraph order). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R175_VALIDATION_20261122.json`).
  The checker passed 19/19 on its FIRST run this round. The checker was
  written fresh (not sed-copied from R174) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `2bdd78d`/`ffa11993`/`537 commit`/`2914 file`/`273073`/`e4fe1f6`/`852e267`
  references in the checker — the R174 values) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The `947b043`/`987cdb5` hits in the checker are the
  intended assertions that the index row carries the R174 content/report
  SHAs. The edit script's budget check ran before any write (R166 lesson):
  the run projected the body at 104.879 ký tự with 121 ký tự of headroom
  and wrote; the idempotency re-run reported changed: 0. One edit-script
  defect was caught by the idempotency check before any commit this round
  (files restored from git, script fixed, re-run clean): `replace_once`
  checked the old anchor before the new text, so the appended R175
  sentence — which contains the old anchor as a substring — was duplicated
  on re-run (+51 ký tự); the script now checks the new text first (R175
  robustness note, fixed).

## Verification

- Merge-tree `987cdb5` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `d63bce9c4cc7a9ebc4c7b8dda63af5474578c5f0`. Merge-tree at the R175
  content head `e07441d` vs `f3db6b3`: exit 0, tree
  `76bfde78102fcf1c0ce70730859ee5c0fd28a76a`.
- Live PR state: API connector MCP read ~10:40 JST (first read 92.521 ký tự / 2 U+FFFD,
  immediate re-read byte-exact) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `987cdb5`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-22T00:49:32Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~10:40 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R175 block (`987cdb5..e07441d`) 3 paths / 0 violations
  (index + body v2 + R175 checker); cumulative at the R175 content
  commit `e07441d` 2918 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `e07441d`).
  Merge-tree at the R175 content head `e07441d` vs `f3db6b3`: exit 0,
  tree `76bfde78…`.
- Transient notes: the first MCP pull read this round returned 92.521 ký tự
  with 2 U+FFFD (the known transient read-path artifact, also seen at
  R166/R167/R172); the immediate re-read was byte-exact (92.520 ký tự,
  sha `ddbe32ff`, 0 U+FFFD) — a first stale read means lag, not a failed
  post. No rate-limit 403 on any MCP read this round.
- Ceiling discipline: the R174 payload JSON measured 122.656 byte
  (as-prepared and after the main-flow refresh — the refresh changed only
  head-line digits, same byte length) vs the 131.072-byte transport ceiling
  (8.416 byte headroom). The projected R175 payload JSON is ~122,900 byte
  (measured exactly at payload build, after push). Body v2 is now 104.879
  ký tự (< 105.000) — 121 ký tự of headroom. R176 warning:
  headroom is now 121 ký tự; the next round must collapse R130 (809 ký tự
  → ~287) and keep the new paragraph tight (≤ ~650 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R175 body
v2 (R174 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r175.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R175 push (title
ending "+ R175", built by replacing the "+ R140" suffix — not appending;
body = body v2 R175 in repo, head line refreshed to head after R175 push).
This run started ~10:40 JST — WITHIN working hours (09:00–21:30 JST), so the
R175 payload is READY FOR PRESENTATION by the main flow (not held for quiet hours — unlike R142/R164–R173). Do not present the superseded R174 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173 and R174 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R175: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
