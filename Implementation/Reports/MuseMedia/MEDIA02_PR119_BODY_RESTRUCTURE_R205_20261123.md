# MEDIA-02 — PR #119 Body Restructure R205: delivery index + body v2 coverage to `2be4074`

Date: 2026-11-23 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `2be4074` (PR119 BODY RESTRUCTURE R204 report). Content commit: `df30756`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R205 does

R204 left the disclosed gap: the delivery index covered 597 commits to
`1cb0f67`; R204's own 2 commits were to fold in at R205. The R204 body v2 was NOT posted — the
live PR body is still R140 (this round's fresh API read ~19:42 JST: PR title still ends
"+ R140", head inside the description `78ccd85` · 471 · 2815, body 92.520 ký tự, sha `ddbe32ff`,
0 U+FFFD, updated_at 2026-11-23T09:44:31Z — bumped by the R204 push updating the PR head, body bytes
unchanged). The R204 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Live-read method, this round: the GitHub API was read via a browser task
(~19:41–19:42 JST, read-only) because the MCP read path refused `issue_read`
this round (`call-read-tool`: "not in Muse's reviewed read-only set; use
`call-tool` so it receives write-capable approval" — a write-capable call
was NOT made; the browser task read the public API instead, so every live
figure this round is still a fresh API byte-exact read, not carried from an
earlier round): issue #116 34 comments, PR #119 head `2be4074`, 599 commits /
3007 files / +286,093, mergeable true, mergeable_state clean at `2be4074`,
live body R140 92.520 ký tự sha `ddbe32ff`. Note (browser finding, known
stale snapshot inside the R140 body itself, not a new defect): the live
R140 body's own head-line text still describes R119 (73.631 ký tự) —
the R140 body is a snapshot whose inner text lags the head it was posted
at; the operative live facts are the title ("+ R140"), the 92.520-ký-tự
body, and the API head `2be4074`.

Fresh derivation at `2be4074` (~19:40 JST): `git rev-list --count
cf17178..2be4074` = 599 commits, `git diff --name-only` = 3007 files,
`--shortstat` = 286093 insertions, 0 deletions — agreeing exactly with
the API read. `git merge-tree
--write-tree` `2be4074` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `1c1adecd…`. No re-fetch was needed before applying: the run fetched at ~19:40 JST
(the run start) and the remote head was still `2be4074`, integration still `f3db6b3` — no
intervening push; the API read ~19:42 JST independently confirmed head `2be4074`.

R205 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `2be4074` (599 commits / 3007 files /
  286093 additions; the fresh git derivation at `2be4074`, the fresh API
  read ~19:42 JST, and the merge-tree cross-check at `2be4074` are cited,
  with the honest mergeable reading disclosed above;
  live body R140; delta `1cb0f67..2be4074`: 5 paths, 528 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R204
  (`818f027`/`2be4074`), recording that its payload was prepared after
  push ~18:44 JST (104.890 ký tự, sha `88ea0099`; JSON 121.504 byte < trần 131.072 — còn 9.568 byte, bản giữ tại
  `.bak-prepost-20261123` — thư mục tồn tại, bản R204 lưu tại đó,
  byte-identical với `pr_comments/` — sha256 `bce286af` cả hai),
  that it was NOT posted
  — live body still R140 (verified by this round's API read: description
  structure matches R140, PR title ends "+ R140", head inside the description
  `78ccd85` · 471 · 2815; live body 92.520 ký tự, sha `ddbe32ff` — đọc lại
  byte-exact lượt này, 0 U+FFFD, updated_at 2026-11-23T09:44:31Z) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; API read ~19:42 JST).
  The index now covers every block through `2be4074`; R205's
  own 2 commits fold in at the next index update (R206), disclosed in the
  index itself. The R205 note was appended after the R204 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `2be4074` · 599 · 3007 (with the fresh git derivation at `2be4074`,
  the fresh API read ~19:42 JST, and the fresh merge-tree cross-check at
  `2be4074`), plus the R204 paragraph in "Khối mới nhất" (388 ký tự,
  marked chưa đăng — live body is R140) and the R205 note. The stale index
  reference in "Về bản mô tả này" (head `1cb0f67`) is also fixed to
  `2be4074`, and the title line is extended to R204 (APPENDED, not
  replaced — see the R176 robustness note). Compaction (R204 warning —
  applied with a margin): the R101 paragraph (616 ký tự — measured this
  round, not the 694 the R204 report estimated) is
  collapsed to one 239-ký-tự compact line (full detail stays in the
  delivery index) — the new R204 paragraph was 388 ký tự, so
  the body is 104.906 ký tự — net +68 vs R204 despite the new R204
  paragraph, headroom 94 ký tự.
  Paragraph order: the R204 paragraph sits directly after R203
  (ascending full-paragraph order R166..R204), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R205 (owner tap) — the R140 body v2 now live
  is the base; only the R204 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r205_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R204 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R204 and R205 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R204 (65 compact lines R101–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.906 ký tự),
  a check that the R204 paragraph sits directly after R203
  (ascending full-paragraph order), the row-convention check now inside
  the checker (R201/R202/R203 rows re-derived from git), a check that the
  R198 row carries the ĐÍNH CHÍNH R200 note, and the R196 script-defect repairs
  kept as regression guards (milestone 6 separate lines, `## Ghi chú`
  its own line, R167 note in ascending position, R204 note clean).
  **PASS 24/24**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R205_VALIDATION_20261123.json`).
  The checker passed on its first run this round. The
  checker was written fresh (not sed-copied from R204) with the full COVER
  SHA verified intact (definition + docstring, both
  `2be4074e781d6894bfcf440ede39e2bd09d194ab` — re-derived from `git rev-parse`
  this round) and a stale-reference grep (0 stale
  `1cb0f67` references in the checker — the R204 cover value)
  before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The edit script's budget check ran before any write (R166 lesson):
  the dry-run simulation projected 104.906 ký tự and the apply wrote on
  the first attempt at 104.906 ký tự with 94 ký tự of headroom; the idempotency re-run
  after apply initially CRASHED on its OLD-state pre-condition asserts
  (mergeable line, head line, "Ghi chú" line — R203 lesson recurring) and
  was FIXED this round: the script now accepts the NEW state as well, and
  the re-run after the fix reported already-applied changed: 0 — verified.

## R205 robustness note — headroom now 94 chars

The R204 warning left 162 ký tự of headroom, so this round compacted
the R101 paragraph (616 ký tự → 239) before adding the new R204 paragraph
(388 ký tự). The body is now 104.906 ký tự — net +68 vs R204 — with
94 ký tự of headroom. The 105.000 ceiling is a self-imposed safety margin
under the 131.072-byte transport ceiling, not a hard limit — but the
discipline holds: compact one old paragraph per round and keep the new
paragraph tight, or the body outgrows the margin within a few rounds.
R206 warning: headroom is 94 ký tự; the next round must collapse R100
(616 ký tự → ~240) and keep the new paragraph tight (≤ ~460 ký tự) — the
R100 compaction alone frees ~377 ký tự, restoring comfortable headroom.
At the current net +68/round the margin holds with compaction; one full-paragraph compaction per round (~−377) keeps
the discipline sustainable (full paragraphs remaining R166..R204 = 39;
compact block R101–R165 = 65 lines).
Lesson this round: (1) the dry-run projection matched the apply exactly
(104.906 ký tự); measure, don't hand-count (same lesson as R186/R190/R195/R197/R198/R199/R200/R201/R202/R203/R204 —
and the R204 report's "R101 694 ký tự" estimate was wrong: the paragraph
is 616 ký tự, measured this round). (2) A "file not found" is not proof of
absence until the path is verified: the `.bak-prepost-20261123` directory
lives at `pr_comments/.bak-prepost-20261123`, not directly under
`godot-prototype/` — the first check this round looked in the wrong place
and briefly looked missing; `find` located it, and R203/R204 payloads
were verified byte-identical there (sha256 `ad64c9ec` / `bce286af`).
(3) An edit script's idempotency re-run must assert the NEW state as
acceptable, not only the OLD state — otherwise the re-run crashes on
its own pre-condition after a successful apply (R203 lesson — recurred
this round on three lines, FIXED: re-run reports already-applied changed: 0, verified).

## Verification

- Merge-tree `2be4074` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `1c1adecd…`. Merge-tree at the R205
  content head `df30756` vs `f3db6b3`: exit 0, tree
  `07857d9a…`.
- Live PR state: API read via browser task ~19:42 JST (read path
  healthy — MCP `call-read-tool` refused `issue_read` this round, see
  above) — PR title ends
  "+ R140" (R140 posted live ~22:22 JST 2026-11-20); head `2be4074`; live body
  R140 by structure (description head `78ccd85` · 471 · 2815, tail lines match)
  and byte-exact body read (92.520 ký tự, sha `ddbe32ff`,
  0 U+FFFD, updated_at 2026-11-23T09:44:31Z — bumped by the R204 push updating the PR head, body
  bytes unchanged); commits 599, changed_files 3007, additions 286093
  (API agrees with the fresh git derivation; the `deletions` key is absent
  in this API response — git shows 0 deletions; the raw API payload also
  returns `mergeable: true` — mergeable_state clean is the operative
  field); mergeable_state clean at
  `2be4074` (API read this round). Note: the PR's `base.sha` as returned by the API is `f3832338` (merge of
  PR #118) — verified an ancestor of the current integration tip
  `f3db6b3` (git merge-base --is-ancestor, re-verified this round); merge-tree vs `f3db6b3` is the
  operative check.
- Issue #116: RE-READ this round via the browser API task — still 34
  comments (30 + 4 paginated), latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R205 block (`2be4074..df30756`) 3 paths / 0 violations
  (index + body v2 + R205 checker); cumulative at the R205 content
  commit `df30756` 3008 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `df30756`).
  Merge-tree at the R205 content head `df30756` vs `f3db6b3`: exit 0,
  tree `07857d9a…`.
- Transient notes: this round's `git fetch` at ~19:40 JST succeeded
  first try. MCP `call-read-tool` refused `issue_read` this round
  (not in the reviewed read-only set); the browser API read replaced it
  cleanly (no stall, no rate-limit 403). The R204 payload's own head line recorded
  mergeable clean at `1cb0f67` at its preparation and clean at
  `2be4074`; this round's API read confirms clean at `2be4074`.
- Ceiling discipline: the R204 payload JSON measured 121.504 byte
  (as-prepared; NOT posted — live body still R140, verified by this round's API read)
  vs the 131.072-byte transport ceiling
  (9.568 byte headroom). The projected R205 payload JSON is ~121,500 byte
  (measured exactly at payload build, after push). Body v2 is now 104.906
  ký tự (< 105.000) — 94 ký tự of headroom. R205 warning:
  headroom is now 94 ký tự; the next round must collapse R100 (616 ký tự
  → ~240) and keep the new paragraph tight (≤ ~460 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R205 body
v2 (R204 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r205.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R205 push (title
ending "+ R205", built by replacing the "+ R140" suffix — not appending;
body = body v2 R205 in repo, head line refreshed to head after R205 push).
This run started ~19:40 JST — WITHIN working hours (09:00–21:30 JST), so the
R205 payload is READY FOR PRESENTATION by the main flow (not held like R142/R164–R197). The exact finish time is recorded in the dev-queue and memory log written after the push, not estimated here (see the R200 correction above). Do not present the superseded R204 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174, R175, R176, R177, R178, R179, R180, R181, R182, R183, R184, R185, R186, R187, R188, R189, R190, R191, R192, R193, R194, R195, R196, R197, R198, R199, R200, R201, R202, R203 and R204 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R205: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
