# MEDIA-02 — PR #119 Body Restructure R174: delivery index + body v2 coverage to `2bdd78d`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `2bdd78d` (PR119 BODY RESTRUCTURE R173 report). Content commit: `947b043`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R174 does

R173 left the disclosed gap: the delivery index covered 535 commits to
`852e267`; R173's own 2 commits were to fold in at R174. The R173 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~09:45 JST, byte-exact on the
first read) show the live PR title ends "+ R140", head
`2bdd78d`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-21T23:55:09Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R173 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~09:45 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `2bdd78d` (~09:45 JST): `git rev-list --count
cf17178..2bdd78d` = 537 commits, `git diff --name-only` = 2914 files,
`--shortstat` = 273073 insertions, 0 deletions. `git merge-tree
--write-tree` `2bdd78d` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `ffa11993accab4147eb99499a5effbc0fd0d3020`. Like R173, this round
DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `2bdd78d` (CI finished since the R173 push), so no carried-forward
clean verdict is needed this round.

R174 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `2bdd78d` (537 commits / 2914 files /
  273073 additions; the fresh git derivation at `2bdd78d`, the fresh API
  read ~09:45 JST, and the merge-tree cross-check at `2bdd78d` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `852e267..2bdd78d`: 5 paths, 382 insertions, 12
  deletions); one row appended — PR119 BODY RESTRUCTURE R173
  (`e4fe1f6`/`2bdd78d`), recording that its payload was prepared after
  push ~08:56 JST (104.376 ký tự, sha `cf5ce217`, mergeable unstable tại
  `2bdd78d`; JSON 122.418 byte < trần 131.072 — còn 8.654 byte, bản giữ tại
  `.bak-prepost-20261122`), that it was NOT refreshed by the main flow
  (`cmp` with `.bak` byte-identical this round), that it was NOT posted
  — live body still R140 (verified by this round's API read: byte-exact on
  the first read, 92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD) — superseded, not posted; issue line re-read fresh this round
  (34 comments, latest ACK `6862732081`, no new direction; connector MCP
  get_comments page 1, perPage 100). The index now covers every block
  through `2bdd78d`; R174's own 2 commits fold in at the next index
  update (R175), disclosed in the index itself. The R174 note was
  appended after the R173 note line (not replacing it — the R140
  replace-instead-of-append defect is guarded by the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `2bdd78d` · 537 · 2914 (with the fresh git derivation at `2bdd78d`,
  the fresh API read ~09:45 JST, and the fresh merge-tree cross-check at
  `2bdd78d`), plus the R173 paragraph in "Khối mới nhất" (713 ký tự,
  marked chưa đăng — live body is R140) and the R174 note. The stale index
  reference in "Về bản mô tả này" (head `852e267`) is also fixed to
  `2bdd78d`, and the title line is extended to R173. Compaction (R173
  warning — applied with a margin): the R132 paragraph (809 ký tự) is
  collapsed to one 287-ký-tự compact line (full detail stays in the
  delivery index) — the new R173 paragraph was trimmed to 713 ký tự, so
  the body is 104.592 ký tự — net +253 vs R173 despite the new R173
  paragraph, headroom 408 ký tự.
  Paragraph order: the R173 paragraph sits directly after R172
  (ascending full-paragraph order R166..R173), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R174 (owner tap) — the R140 body v2 now live
  is the base; only the R173 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r174_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R173 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R173 and R174 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R173 (34 compact lines R132–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.592 ký tự),
  and a check that the R173 paragraph sits directly after R172
  (ascending full-paragraph order). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R174_VALIDATION_20261122.json`).
  The checker passed 19/19 on its FIRST run this round. The checker was
  written fresh (not sed-copied from R173) with the full COVER SHA
  verified intact and a stale-reference grep (0 stale
  `852e267`/`3c40d93`/`aa33de7b`/`535 commit`/`2911 file`/`272703`
  references in the checker — the R173 values) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The `e4fe1f6`/`2bdd78d` hits in the checker are the
  intended assertions that the index row carries the R173 content/report
  SHAs. The edit script's budget check ran before any write (R166 lesson):
  the run projected the body at 104.592 ký tự with 408 ký tự of headroom
  and wrote; the idempotency re-run reported changed: 0. Two edit-script
  defects were caught by the budget/idempotency checks before any commit
  this round (files restored from git, script fixed, re-run clean): the
  R173 paragraph measured 722 ký tự against the ≤ 720 target (trimmed to
  713) and the idempotency re-run duplicated the R174 sentence in line 7
  (+51 ký tự — the line-7 append anchor still matched after the first
  run); the script now guards the append and treats old == new as
  changed: 0 (R174 robustness note, fixed).

## Verification

- Merge-tree `2bdd78d` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `ffa11993accab4147eb99499a5effbc0fd0d3020`. Merge-tree at the R174
  content head `947b043` vs `f3db6b3`: exit 0, tree
  `b6c20534ed1dd26068e96aed473515e33e18049b`.
- Live PR state: API connector MCP read ~09:45 JST (first read,
  byte-exact) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `2bdd78d`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-21T23:55:09Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~09:45 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R174 block (`2bdd78d..947b043`) 3 paths / 0 violations
  (index + body v2 + R174 checker); cumulative at the R174 content
  commit `947b043` 2915 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `947b043`).
  Merge-tree at the R174 content head `947b043` vs `f3db6b3`: exit 0,
  tree `b6c20534…`.
- Transient notes: no rate-limit 403 on any MCP read this round (pulls +
  issue comments both 200 first try; PR read byte-exact on the first
  read). The post-checkout LFS hook warned `git-lfs` was not on PATH
  during a `git checkout` without tools-bin on PATH (checkout did not
  complete in that shell); restored the file with `~/workspace/tools-bin`
  on PATH per the task body, then re-ran the edit script clean.
- Ceiling discipline: the R173 payload JSON measured 122.418 byte
  (as-prepared, not refreshed) vs the 131.072-byte transport ceiling
  (8.654 byte headroom). The projected R174 payload JSON is ~122.600 byte
  (measured exactly at payload build, after push). Body v2 is now 104.592
  ký tự (< 105.000) — 408 ký tự of headroom. R175 warning:
  headroom is now 408 ký tự; the next round must collapse R131 and keep
  the new paragraph tight (≤ ~700 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R174 body
v2 (R173 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r174.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R174 push (title
ending "+ R174", built by replacing the "+ R140" suffix — not appending;
body = body v2 R174 in repo, head line refreshed to head after R174 push).
This run started ~09:40 JST — WITHIN working hours (09:00–21:30 JST), so the
R174 payload is READY FOR PRESENTATION by the main flow (not held for quiet hours — unlike R142/R164–R173). Do not present the superseded R173 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172 and R173 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R174: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
