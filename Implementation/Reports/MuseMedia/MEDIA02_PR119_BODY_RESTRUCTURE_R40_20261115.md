# MEDIA-02 — PR #119 Body Restructure R40: delivery index + body v2 coverage to `45776d1`

Date: 2026-11-15 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `45776d1` (PR119 BODY RESTRUCTURE R39 report). Content commit: `6ef10cf`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R40 does

R39 left a disclosed gap: the delivery index covered 267 commits to
`36f8ce2`; R39's own 2 commits were to fold in at R40. Since then the
R39 body v2 was NOT posted — the live PR description is still the R8 body
(head `f2ba478` · 207 · 2419, title 763 ký tự kết thúc "+ R8", body_len
11.793, verified by connector list endpoint 2026-11-15 ~18:45 JST this
round: PR `updated_at` 2026-11-15T08:46:19Z, reflecting the R39 push; the
list endpoint returns null for `head_sha`/`mergeable`, so no head claim
is made from it — the branch tip `45776d1` is verified separately by
ls-remote). The R39 payload (`pr119_update_body_v2_r39.json`, 27.839 ký
tự) is now SUPERSEDED by the R40 body v2 before any tap, following the
same pattern as R3/R4/R5/R7/R9–R39. No new Codex/owner direction has
landed on issue #116. Note: this is a detached scheduled run (18:40 JST,
in-hours), so the R40 payload is prepared here for the main agent to
present — the approval card lives ~30 minutes, tap while at the machine.

Fresh derivation at `45776d1` (~18:45 JST): `git rev-list --count
cf17178..45776d1` = 269 commits, `git diff --name-only` = 2512 files,
`--shortstat` = 233498 insertions, 0 deletions — exactly matching the
R39 report's remote-tip figures. The structural cross-check stands:
`git merge-tree --write-tree` `45776d1` vs integration `f3db6b3`
exit 0, 0 conflicts, tree `741b4da4ea0d22da5c3a3b8d2868d258f7ee9729`.

R40 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `45776d1` (269 commits / 2512 files /
  233498 additions; API figures cited are the last verified read at
  `f891e40`, ~13:41 JST — no fresh PR read this round, see Verification);
  one row appended — PR119 BODY RESTRUCTURE R39 (`90a8335`/`45776d1`),
  including the note that its body payload was superseded by the R40 body
  v2 before posting; issue line still 34 comments. The index now covers
  every block through `45776d1`; R40's own 2 commits fold in at the next
  index update (R41), disclosed in the index itself.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `45776d1` · 269 · 2512 (with the last verified mergeable true/clean
  read at `f891e40` plus the true/unstable read at `03b0a8a`), plus the
  R39 paragraph in "Khối mới nhất" and the R40 note. The live PR
  description is refreshed from this file in the posting round that
  follows R40 (owner tap) — the R8 body v2 already live is the base;
  only the R39 paragraph + new head line are new.
- **Checker** `check_pr119_restructure_r40_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims. **PASS 17/17**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R40_VALIDATION_20261115.json`),
  first run — no fix round needed this time.

## Verification

- Merge-tree `45776d1` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `741b4da4ea0d22da5c3a3b8d2868d258f7ee9729`. Merge-tree at the R40
  content head `6ef10cf` vs `f3db6b3`: exit 0, tree
  `b32b0d8ab169f54cd51b5a5e08da8b1327d8ce1c`.
- PR API single-PR read: NOT re-read this round — `get_pull_request`
  is not advertised by the live MCP server (verified in the tool
  catalog this round; only `list_issues`/`list_pull_requests`/
  `list_commits` are readable), and the list endpoint returns null for
  `mergeable`/`mergeable_state`. The public REST API was not attempted
  this round (previous rounds hit its 403 rate limit; no retry loop).
  Last verified reads stand: mergeable true / clean at head `f891e40`
  (~13:41 JST), and mergeable true / mergeable_state unstable at head
  `03b0a8a` (~13:44 JST, CI running on the new head — not a review
  failure).
- Issue #116: 34 comments, `updated_at` 2026-11-13T19:24:49Z (unchanged
  since the ACK `6862732081` posting), latest ACK `6862732081` (CP5 + M-G
  CP10 + R2, posted 2026-11-14 ~04:24 JST); no new Codex/owner direction
  since Gói 39 (`6815238814`). Read via the connector `list_issues`
  endpoint (~18:45 JST).
- Scope audit: R40 block 3 paths / 0 violations; cumulative at the R40
  content commit 2513 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `6ef10cf`).
  Merge-tree at the R40 content head `6ef10cf` vs `f3db6b3`: exit 0,
  tree `b32b0d8a…`.

## Next

Posting round (owner tap, in-hours): PR #119 description refresh to the
R40 body v2 (R39 paragraph + new head line are the only new parts vs the
live R8 body). Payload `pr119_update_body_v2_r40.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R40 push
(title 764 ký tự, kết thúc "+ R40"; body = body v2 R40 trong repo, head
line làm tươi tới head sau khi R40 push). Do NOT tap the R39 widget
(`pr119_update_body_v2_r39.json`) — it is superseded by R40. No separate
ACK comment for R40: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
