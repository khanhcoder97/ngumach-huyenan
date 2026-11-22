# MEDIA-02 — PR #119 Body Restructure R176: delivery index + body v2 coverage to `f311bfa`

Date: 2026-11-22 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `f311bfa` (PR119 BODY RESTRUCTURE R175 report). Content commit: `d0fb193`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R176 does

R175 left the disclosed gap: the delivery index covered 539 commits to
`987cdb5`; R175's own 2 commits were to fold in at R176. The R175 body v2 was NOT posted — this
round's fresh API reads (connector MCP `pull_request_read` get ~11:41 JST, first read byte-exact:
92.520 ký tự, 0 U+FFFD, no transient read-path artifact this round) show the live PR title ends
"+ R140", head `f311bfa`, mergeable_state **clean** (CI finished on the new head; the MCP read returns mergeable_state clean
with the `mergeable` field null), updated_at 2026-11-22T01:48:10Z, and the live body is still R140
(92.520 ký tự, sha256 `ddbe32ff`, 0 U+FFFD). The R175 payload is therefore superseded, not posted
— do not post it. No new Codex/owner direction has landed on issue #116:
this round's fresh read of the comments API via connector MCP
(`issue_read` get_comments, page 1 with perPage 100 = all 34 comments in
one page, ~11:41 JST) agrees: still 34 comments, latest ACK
`6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z); no new
direction since Gói 39 (`6815238814`).

Fresh derivation at `f311bfa` (~11:41 JST): `git rev-list --count
cf17178..f311bfa` = 541 commits, `git diff --name-only` = 2920 files,
`--shortstat` = 273810 insertions, 0 deletions. `git merge-tree
--write-tree` `f311bfa` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `83d7a9acea3fa6a78899ea2286fc344692d50d2d`. Like R175, this round
DID get a fresh clean mergeable read at the new head — mergeable_state is
clean at `f311bfa` (CI finished since the R175 push), so no carried-forward
clean verdict is needed this round.

R176 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `f311bfa` (541 commits / 2920 files /
  273810 additions; the fresh git derivation at `f311bfa`, the fresh API
  read ~11:41 JST, and the merge-tree cross-check at `f311bfa` are cited,
  with the fresh clean mergeable read at the new head disclosed above;
  live body R140; delta `987cdb5..f311bfa`: 5 paths, 380 insertions, 11
  deletions); one row appended — PR119 BODY RESTRUCTURE R175
  (`e07441d`/`f311bfa`), recording that its payload was prepared after
  push ~10:55 JST (104.885 ký tự, sha `b0091067`, mergeable clean tại
  `f311bfa`; JSON 122.914 byte < trần 131.072 — còn 8.158 byte, bản giữ tại
  `.bak-prepost-20261122`), that it was NOT refreshed by the main flow
  (cmp with its `.bak` byte-identical this round: body sha `b0091067`,
  104.885 ký tự), that it was NOT posted
  — live body still R140 (verified by this round's API read: byte-exact
  first read, 92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD) — superseded, not
  posted; issue line re-read fresh this round (34 comments, latest ACK
  `6862732081`, no new direction; connector MCP get_comments page 1,
  perPage 100). The index now covers every block through `f311bfa`; R176's
  own 2 commits fold in at the next index update (R177), disclosed in the
  index itself. The R176 note was appended after the R175 note line (not
  replacing it — the R140 replace-instead-of-append defect is guarded by
  the new checker check).
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `f311bfa` · 541 · 2920 (with the fresh git derivation at `f311bfa`,
  the fresh API read ~11:41 JST, and the fresh merge-tree cross-check at
  `f311bfa`), plus the R175 paragraph in "Khối mới nhất" (568 ký tự,
  marked chưa đăng — live body is R140) and the R176 note. The stale index
  reference in "Về bản mô tả này" (head `987cdb5`) is also fixed to
  `f311bfa`, and the title line is extended to R175 (APPENDED, not
  replaced — see the R176 robustness note below). Compaction (R175
  warning — applied with a margin): the R130 paragraph (809 ký tự) is
  collapsed to one 287-ký-tự compact line (full detail stays in the
  delivery index) — the new R175 paragraph was trimmed to 568 ký tự, so
  the body is 104.981 ký tự — net +102 vs R175 despite the new R175
  paragraph, headroom 19 ký tự.
  Paragraph order: the R175 paragraph sits directly after R174
  (ascending full-paragraph order R166..R175), before the
  compact block — the new checker now asserts this ascending order
  explicitly. The live PR description is refreshed from this file in the
  posting round that follows R176 (owner tap) — the R140 body v2 now live
  is the base; only the R175 paragraph (posting note) + new head line are
  new vs live.
- **Checker** `check_pr119_restructure_r176_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R175 run in the title line, guarding the R94 slip fixed by R98),
  a check that both the R175 and R176 update notes are present
  (guarding the R140 replace-instead-of-append defect), the compaction
  check extended from R175 (36 compact lines R130–R165 present, each
  < 400 ký tự, body total < 105.000 ký tự — body is now 104.981 ký tự),
  and a check that the R175 paragraph sits directly after R174
  (ascending full-paragraph order). **PASS 19/19**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R176_VALIDATION_20261122.json`).
  The checker did NOT pass on its first run this round — it caught a real
  defect before any commit (see the R176 robustness note below). The
  checker was written fresh (not sed-copied from R175) with the full COVER
  SHA verified intact (2 occurrences) and a stale-reference grep (0 stale
  `987cdb5`/`2bdd78d`/`ffa11993`/`d63bce9c`/`852e267`/`947b043`/`273441`/`539 commit`/`2917 file`/`537 commit`/`2914 file`
  references in the checker — the R175 values) before the run — the R69
  sed-order copy defect (mangled full COVER SHA) was avoided by
  construction. The `e07441d`/`f311bfa` hits in the checker are the
  intended assertions that the index row carries the R175 content/report
  SHAs. The edit script's budget check ran before any write (R166 lesson):
  the run projected the body at 104.981 ký tự with 19 ký tự of headroom
  and wrote; the idempotency re-run reported changed: 0.

## R176 robustness note — title append, not replace (checker-caught defect)

The first edit-script draft replaced the file heading's trailing
" + PR119 BODY RESTRUCTURE R174" with " + PR119 BODY RESTRUCTURE R175".
That was wrong: the body v2 file heading is a CUMULATIVE list
(R2..R174), so each round APPENDS the new round — the R175 precedent
appended R174 after R173. Replacing consumed R174 from the list, and the
new checker caught it on its first run (FAIL 18/19, title-sequence check:
R174 missing). The files were restored from git, the script fixed
(append + R175 paragraph trimmed 595 → 568 ký tự to hold the budget),
and the re-run passed 19/19. The R120 replace rule applies to the
765-char PAYLOAD title (where the "+ R140" suffix IS replaced, never
appended) — not to this cumulative heading. Do not "fix" the heading by
replacing again.

## Verification

- Merge-tree `f311bfa` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `83d7a9acea3fa6a78899ea2286fc344692d50d2d`. Merge-tree at the R176
  content head `d0fb193` vs `f3db6b3`: exit 0, tree
  `c3aa3ad8ea70cc6105f6056231d34e12de22f535`.
- Live PR state: API connector MCP read ~11:41 JST (byte-exact first read, 92.520 ký tự,
  0 U+FFFD) — title ends "+ R140"
  (R140 posted live ~22:22 JST 2026-11-20); head `f311bfa`; live body
  R140 (92.520 ký tự, sha `ddbe32ff`, 0 U+FFFD, updated_at
  2026-11-22T01:48:10Z); mergeable_state **clean** at the new head
  (fresh read this round; `mergeable` field null via MCP; CI finished).
- Issue #116: RE-READ this round via the comments API — connector MCP
  (`issue_read` get_comments, page 1 perPage 100, ~11:41 JST): still 34
  comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
  2026-11-13T19:24:48Z); no new Codex/owner direction since Gói 39
  (`6815238814`). The 5 comments after Gói 39 are all Muse ACKs of
  completed work, not new direction.
- Scope audit: R176 block (`f311bfa..d0fb193`) 3 paths / 0 violations
  (index + body v2 + R176 checker); cumulative at the R176 content
  commit `d0fb193` 2921 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `d0fb193`).
  Merge-tree at the R176 content head `d0fb193` vs `f3db6b3`: exit 0,
  tree `c3aa3ad8…`.
- Transient notes: the first MCP pull read this round was byte-exact
  (92.520 ký tự, 0 U+FFFD) — no transient read-path artifact this round
  (unlike R175's first read at 92.521 ký tự/2 U+FFFD). No rate-limit 403
  on any MCP read this round.
- Ceiling discipline: the R175 payload JSON measured 122.914 byte
  (as-prepared; cmp with its `.bak` byte-identical this round, so no
  main-flow refresh changed it) vs the 131.072-byte transport ceiling
  (8.158 byte headroom). The projected R176 payload JSON is ~123,000 byte
  (measured exactly at payload build, after push). Body v2 is now 104.981
  ký tự (< 105.000) — 19 ký tự of headroom. R177 warning:
  headroom is now 19 ký tự; the next round must collapse R129 (809 ký tự
  → ~287) and keep the new paragraph tight (≤ ~600 ký tự).

## Next

Posting round (owner tap): PR #119 description refresh to the R176 body
v2 (R175 posting note + new head line are the only new parts vs the live R140 body). Payload `pr119_update_body_v2_r176.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R176 push (title
ending "+ R176", built by replacing the "+ R140" suffix — not appending;
body = body v2 R176 in repo, head line refreshed to head after R176 push).
This run started ~11:40 JST — WITHIN working hours (09:00–21:30 JST), so the
R176 payload is READY FOR PRESENTATION by the main flow (not held for quiet hours — unlike R142/R164–R173). Do not present the superseded R175 payload. The R140 payload is DONE (posted) —
do not re-post it. The R141, R142, R143, R144, R145, R146, R147, R148,
R149, R150, R151, R152, R153, R154, R155, R156, R157, R158, R159, R160, R161, R162, R163, R164, R165, R166, R167, R168, R169, R170, R171, R172, R173, R174 and R175 payloads are SUPERSEDED — do not post them. No separate
ACK comment for R176: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
