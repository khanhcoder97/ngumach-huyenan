# MEDIA-02 — PR #119 Body Restructure R27: delivery index + body v2 coverage to `393379f`

Date: 2026-11-15 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `393379f` (PR119 BODY RESTRUCTURE R26 report). Content commit: `d441a7f`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R27 does

R26 left a disclosed gap: the delivery index covered 241 commits to
`e55050f`; R26's own 2 commits were to fold in at R27. Since then the
R26 body v2 was NOT posted — the live PR description is still the R8 body
(head `f2ba478` · 207 · 2419, title 763 ký tự kết thúc "+ R8", body_len
11.793, verified by API list read 2026-11-15 ~05:40 JST; PR `updated_at`
2026-11-14T19:46:04Z reflects the R26 push to the head branch, not a body
change). The R26 payload (`pr119_update_body_v2_r26.json`, 20.716 ký tự)
is now SUPERSEDED by the R27 body v2 before any tap, following the same
pattern as R3/R4/R5/R7/R9–R26. No new Codex/owner direction has landed on
issue #116. Note: 05:40 JST is past the 21:30 quiet-hours cutoff, so the
R27 payload is prepared but NOT presented tonight; it will be presented
in-hours tomorrow, or superseded by R28.

Fresh read at `393379f` (~05:40 JST): the API mergeable state could NOT
be re-read this round — the connector's `get_pull_request` is no longer
advertised by the live MCP server (the reviewed read set still lists the
old name), and the list endpoint returns null for the mergeable fields.
The structural check stands instead: `git merge-tree --write-tree`
`393379f` vs integration `f3db6b3` exit 0, 0 conflicts, tree
`ad1c0d45f7c3d75e6b9a9e382bf6db065f064bcf`. The last API mergeable read
(true/clean) was at head `dbc099d` (2026-11-14 ~23:40 JST). The R27
payload therefore does NOT claim a fresh mergeable true; it records the
merge-tree result and the last API read honestly.

R27 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `393379f` (243 commits / 2473 files /
  230,233 additions; API list confirms head `393379f`); one row
  appended — PR119 BODY RESTRUCTURE R26 (`e4f84b2`/`393379f`), including
  the note that its body payload was superseded by the R27 body v2 before
  posting; issue line still 34 comments. The index now covers every block
  through `393379f`; R27's own 2 commits fold in at the next index update
  (R28), disclosed in the index itself.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `393379f` · 243 · 2473, plus the R26 paragraph in "Khối mới nhất" and
  the R27 note. The live PR description is refreshed from this file in the
  posting round that follows R27 (owner tap) — the R8 body v2 already live
  is the base; only the R26 paragraph + new head line are new.
- **Checker** `check_pr119_restructure_r27_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims. **PASS 17/17**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R27_VALIDATION_20261115.json`).
  Note: the first checker run scored 16/17 — the generated check string
  for the body round note still carried the previous round number; fixed
  to R27 and re-run to 17/17 before committing.

## Verification

- Merge-tree `393379f` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `ad1c0d45f7c3d75e6b9a9e382bf6db065f064bcf`.
- PR API list read (2026-11-15 ~05:40 JST): head branch sha `393379f`,
  live body is the R8 body v2 (head `f2ba478` · 207 · 2419, title 763 ký tự
  kết thúc "+ R8", body_len 11.793 = the R8 payload-as-prepared).
  `updated_at` 2026-11-14T19:46:04Z predates any body post, and no new
  body post has happened since the R8 posting ~11:19 JST on 2026-11-14.
  Mergeable fields are null from this endpoint (see above).
- Issue #116: 34 comments, `updated_at` 2026-11-13T19:24:49Z (unchanged
  since the ACK `6862732081` posting), latest ACK `6862732081` (CP5 + M-G
  CP10 + R2, posted 2026-11-14 ~04:24 JST); no new Codex/owner direction
  since Gói 39 (`6815238814`). Read via the reviewed read tools
  (`list_issues` + `list_pull_requests`); `get_issue`/`get_pull_request`
  are not advertised by the live MCP server, so the list endpoints were used.
- Scope audit: R27 block 3 paths / 0 violations; cumulative at the R27
  content commit 2474 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `d441a7f`).

## Next

Posting round (owner tap, in-hours): PR #119 description refresh to the
R27 body v2 (R26 paragraph + new head line are the only new parts vs the
live R8 body). Payload `pr119_update_body_v2_r27.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R27 push (title 764
ký tự, kết thúc "+ R27"; body = body v2 R27 trong repo, head line làm tươi
tới head sau khi R27 push). Do NOT tap the R26 widget
(`pr119_update_body_v2_r26.json`) — it is superseded by R27. No separate
ACK comment for R27: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's ears;
full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
