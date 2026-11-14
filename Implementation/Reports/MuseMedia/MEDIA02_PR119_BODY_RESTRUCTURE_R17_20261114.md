# MEDIA-02 — PR #119 Body Restructure R17: delivery index + body v2 coverage to `43fd714`

Date: 2026-11-14 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `43fd714` (PR119 BODY RESTRUCTURE R16 report). Content commit: `20d234d`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R17 does

R16 left a disclosed gap: the delivery index covered 221 commits to
`406bc86`; R16's own 2 commits were to fold in at R17. Since then the
R16 body v2 was NOT posted — the live PR description is still the R8 body
(head `f2ba478` · 207 · 2419, title 763 ký tự kết thúc "+ R8", verified by
API read 2026-11-14 ~19:41 JST; PR `updated_at` 2026-11-14T09:42:50Z
reflects the R16 push to the head branch, not a body change). The posting
attempt for the R16 body at ~19:15 JST expired unposted (the connector
approval card waited ~30 min and returned approval_expired; the connector
confirmed the update was not performed) — the refreshed R16 payload
(15.290 ký tự, mergeable clean, head line already at `43fd714`) was still
valid at head `43fd714`, but it is now SUPERSEDED by the R17 body v2
before any tap, following the same pattern as R3/R4/R5/R7/R9–R15. No new
Codex/owner direction has landed on issue #116.

R17 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `43fd714` (223 commits / 2443 files /
  227,838 additions, matching the PR API); one row appended —
  PR119 BODY RESTRUCTURE R16 (`57fa2db`/`43fd714`), including the note
  that its body payload was superseded by the R17 body v2 before posting
  and that its ~19:15 JST posting attempt expired unposted; issue line
  still 34 comments. The index now covers every block through `43fd714`;
  R17's own 2 commits fold in at the next index update (R18), disclosed
  in the index itself.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `43fd714` · 223 · 2443, plus the R16 paragraph in "Khối mới nhất" and
  the R17 note. The live PR description is refreshed from this file in the
  posting round that follows R17 (owner tap) — the R8 body v2 already live
  is the base; only the R15 + R16 paragraphs + new head line are new.
- **Checker** `check_pr119_restructure_r17_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims. **PASS 17/17**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R17_VALIDATION_20261114.json`).

## Verification

- Merge-tree `43fd714` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `66f7e031877680de1520b064c4e15cf3ff6f667b`.
- PR API at `43fd714` (2026-11-14 ~19:41 JST, direct read of the public
  API): commits 223, changed_files 2443, additions 227838,
  deletions 0, mergeable true, mergeable_state clean. Live body is the R8
  body v2 (head `f2ba478` · 207 · 2419, title 763 ký tự kết thúc "+ R8",
  first line lists blocks through R7). `updated_at` predates any body
  post, and no new body post has happened since the R8 posting ~11:19 JST.
- Issue #116: 34 comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2,
  posted 2026-11-14 ~04:24 JST); no new Codex/owner direction since Gói 39
  (`6815238814`).
- Scope audit: R17 block 3 paths / 0 violations; cumulative at the R17
  content commit 2444 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `20d234d`).

## Next

Posting round (owner tap): PR #119 description refresh to the R17 body v2
(R15 + R16 paragraphs + new head line are the only new parts vs the live R8
body). Payload `pr119_update_body_v2_r17.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R17 push (title 764
ký tự, kết thúc "+ R17"; body = body v2 R17 trong repo, head line làm tươi
tới head sau khi R17 push). Do NOT tap the R16 widget
(`pr119_update_body_v2_r16.json`, incl. the refreshed 15.290-char version)
— it is superseded by R17. No separate ACK comment for R17: its content
is pure bookkeeping. Standing blocks unchanged: 32 shots await character
lock; ear audition is the owner's ears; full OGV 720p deferred per Gói 39;
SFX binding awaits Codex.
