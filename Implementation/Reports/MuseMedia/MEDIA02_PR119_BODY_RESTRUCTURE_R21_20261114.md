# MEDIA-02 — PR #119 Body Restructure R21: delivery index + body v2 coverage to `dbc099d`

Date: 2026-11-14 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `dbc099d` (PR119 BODY RESTRUCTURE R20 report). Content commit: `e117a71`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R21 does

R20 left a disclosed gap: the delivery index covered 229 commits to
`ec019ff`; R20's own 2 commits were to fold in at R21. Since then the
R20 body v2 was NOT posted — the live PR description is still the R8 body
(head `f2ba478` · 207 · 2419, title 763 ký tự kết thúc "+ R8", body_len
11.793, verified by API read 2026-11-14 ~23:40 JST; PR `updated_at`
2026-11-14T13:44:42Z reflects the R20 push to the head branch, not a body
change). The R20 payload (`pr119_update_body_v2_r20.json`, 17.317 ký tự)
is now SUPERSEDED by the R21 body v2 before any tap, following the same
pattern as R3/R4/R5/R7/R9–R20. No new Codex/owner direction has landed on
issue #116. Note: 23:40 JST is past the 21:30 quiet-hours cutoff, so the
R21 payload is prepared but NOT presented tonight; it will be presented
in-hours tomorrow, or superseded by R22.

Fresh read at `dbc099d` (~23:40 JST): mergeable true, mergeable_state
clean — CI has finished on the R20 head. The R20 payload's "unstable"
sentence (CI 5/11 success at ~22:45 JST) is therefore outdated in the
conservative direction; the R21 payload carries the clean read.

R21 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `dbc099d` (231 commits / 2455 files /
  228,775 additions, matching the PR API); one row appended —
  PR119 BODY RESTRUCTURE R20 (`1349bfe`/`dbc099d`), including the note
  that its body payload was superseded by the R21 body v2 before posting;
  issue line still 34 comments. The index now covers every block through
  `dbc099d`; R21's own 2 commits fold in at the next index update (R22),
  disclosed in the index itself.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `dbc099d` · 231 · 2455, plus the R20 paragraph in "Khối mới nhất" and
  the R21 note. The live PR description is refreshed from this file in the
  posting round that follows R21 (owner tap) — the R8 body v2 already live
  is the base; only the R20 paragraph + new head line are new.
- **Checker** `check_pr119_restructure_r21_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims. **PASS 17/17**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R21_VALIDATION_20261114.json`).
  Note: this checker also fixes an inherited copy-paste bug — the R20
  checker template's validator output string still named `r20`; the R21
  checker names itself correctly.

## Verification

- Merge-tree `dbc099d` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `c485aeab451786fe89da2f2c9fd99819df4162b2`.
- PR API at `dbc099d` (2026-11-14 ~23:40 JST, direct read of the public
  API): commits 231, changed_files 2455, additions 228775,
  deletions 0, mergeable true, mergeable_state clean. Live body is the R8
  body v2 (head `f2ba478` · 207 · 2419, title 763 ký tự kết thúc "+ R8",
  first line lists blocks through R7). `updated_at` predates any body
  post, and no new body post has happened since the R8 posting ~11:19 JST.
- Issue #116: 34 comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2,
  posted 2026-11-14 ~04:24 JST); no new Codex/owner direction since Gói 39
  (`6815238814`).
- Scope audit: R21 block 3 paths / 0 violations; cumulative at the R21
  content commit 2456 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `e117a71`).

## Next

Posting round (owner tap, in-hours): PR #119 description refresh to the
R21 body v2 (R20 paragraph + new head line are the only new parts vs the
live R8 body). Payload `pr119_update_body_v2_r21.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R21 push (title 764
ký tự, kết thúc "+ R21"; body = body v2 R21 trong repo, head line làm tươi
tới head sau khi R21 push). Do NOT tap the R20 widget
(`pr119_update_body_v2_r20.json`) — it is superseded by R21. No separate
ACK comment for R21: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's ears;
full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
