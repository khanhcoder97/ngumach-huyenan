# MEDIA-02 — PR #119 Body Restructure R29: delivery index + body v2 coverage to `a7fe307`

Date: 2026-11-15 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `a7fe307` (PR119 BODY RESTRUCTURE R28 report). Content commit: `406f12f`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R29 does

R28 left a disclosed gap: the delivery index covered 245 commits to
`6963d5a`; R28's own 2 commits were to fold in at R29. Since then the
R28 body v2 was NOT posted — the live PR description is still the R8 body
(head `f2ba478` · 207 · 2419, title 763 ký tự kết thúc "+ R8", body_len
11.793, verified by API list read 2026-11-15 ~07:45 JST; PR `updated_at`
2026-11-14T21:45:02Z reflects the R28 push to the head branch, not a body
change). The R28 payload (`pr119_update_body_v2_r28.json`, 21.784 ký tự)
is now SUPERSEDED by the R29 body v2 before any tap, following the same
pattern as R3/R4/R5/R7/R9–R28. No new Codex/owner direction has landed on
issue #116. Note: this is a detached scheduled run (07:40 JST), so the
R29 payload is prepared but NOT presented here; presentation stays with
the main agent in-hours, or it will be superseded by R30.

Fresh read at `a7fe307` (~07:45 JST): the API mergeable state could NOT
be re-read this round — the connector's `get_pull_request` is no longer
advertised by the live MCP server (the reviewed read set still lists the
old name), and the list endpoint returns null for the mergeable fields.
The structural check stands instead: `git merge-tree --write-tree`
`a7fe307` vs integration `f3db6b3` exit 0, 0 conflicts, tree
`ff56c1b350019a169ea5a820e90364a24546ed2c`. The last API mergeable read
(true/clean) was at head `dbc099d` (2026-11-14 ~23:40 JST). The R29
payload therefore does NOT claim a fresh mergeable true; it records the
merge-tree result and the last API read honestly.

R29 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `a7fe307` (247 commits / 2479 files /
  230,725 additions; API list confirms head `a7fe307`); one row
  appended — PR119 BODY RESTRUCTURE R28 (`4d59b39`/`a7fe307`), including
  the note that its body payload was superseded by the R29 body v2 before
  posting; issue line still 34 comments. The index now covers every block
  through `a7fe307`; R29's own 2 commits fold in at the next index update
  (R30), disclosed in the index itself.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `a7fe307` · 247 · 2479, plus the R28 paragraph in "Khối mới nhất" and
  the R29 note. The live PR description is refreshed from this file in the
  posting round that follows R29 (owner tap) — the R8 body v2 already live
  is the base; only the R28 paragraph + new head line are new.
- **Checker** `check_pr119_restructure_r29_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims. **PASS 17/17**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R29_VALIDATION_20261115.json`),
  first run — no fix round needed this time.

## Verification

- Merge-tree `a7fe307` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `ff56c1b350019a169ea5a820e90364a24546ed2c`.
- PR API list read (2026-11-15 ~07:45 JST): head branch sha `a7fe307`,
  live body is the R8 body v2 (head `f2ba478` · 207 · 2419, title 763 ký tự
  kết thúc "+ R8", body_len 11.793 = the R8 payload-as-prepared).
  `updated_at` 2026-11-14T21:45:02Z predates any body post, and no new
  body post has happened since the R8 posting ~11:19 JST on 2026-11-14.
  Mergeable fields are null from this endpoint (see above).
- Issue #116: 34 comments, `updated_at` 2026-11-13T19:24:49Z (unchanged
  since the ACK `6862732081` posting), latest ACK `6862732081` (CP5 + M-G
  CP10 + R2, posted 2026-11-14 ~04:24 JST); no new Codex/owner direction
  since Gói 39 (`6815238814`). Read via the reviewed read tools
  (`list_issues` + `list_pull_requests`); `get_issue`/`get_pull_request`
  are not advertised by the live MCP server, so the list endpoints were used.
- Scope audit: R29 block 3 paths / 0 violations; cumulative at the R29
  content commit 2480 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `406f12f`).
  Merge-tree at the R29 content head `406f12f` vs `f3db6b3`: exit 0,
  tree `65e3afe8…`.

## Next

Posting round (owner tap, in-hours): PR #119 description refresh to the
R29 body v2 (R28 paragraph + new head line are the only new parts vs the
live R8 body). Payload `pr119_update_body_v2_r29.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R29 push (title 764
ký tự, kết thúc "+ R29"; body = body v2 R29 trong repo, head line làm tươi
tới head sau khi R29 push). Do NOT tap the R28 widget
(`pr119_update_body_v2_r28.json`) — it is superseded by R29. No separate
ACK comment for R29: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's ears;
full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
