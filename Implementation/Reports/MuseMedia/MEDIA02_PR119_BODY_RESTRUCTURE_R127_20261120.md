# MEDIA-02 — PR #119 Body Restructure R127: delivery index + body v2 coverage to `c0b65f6`

Date: 2026-11-20 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `c0b65f6` (PR119 BODY RESTRUCTURE R126 report). Content commit: `ec0d84f`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R127 does

R126 left the disclosed gap: the delivery index covered 441 commits to
`5c2b304`; R126's own 2 commits were to fold in at R127. The R126 body v2
was NOT posted — this round's fresh API read (curl `pulls/119`, ~08:41 JST)
shows the live PR title still ends "+ R119", head `c0b65f6`, mergeable
**true / clean** (fresh read at the new head this round), updated_at
2026-11-19T22:47:15Z, and the live body is still R119 (73.631 ký tự, sha256
`9dac3461`, read back byte-exact this round). The R126 payload is therefore
SUPERSEDED by R127 — do not post it. The R119 payload is DONE (posted) —
do not re-post it.
No new Codex/owner direction has landed on issue #116: this round's fresh
read of the comments API via curl (~08:41 JST, `per_page=100`) shows still
34 comments, latest ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at
2026-11-13T19:24:48Z); no new direction since Gói 39 (`6815238814`).

Fresh derivation at `c0b65f6` (~08:41 JST): `git rev-list --count
cf17178..c0b65f6` = 443 commits, `git diff --name-only` = 2773 files,
`--shortstat` = 257689 insertions, 0 deletions. `git merge-tree
--write-tree` `c0b65f6` vs integration `f3db6b3` exit 0, 0 conflicts,
tree `cbc4d5e5f1967e8c31672cafd60dce34e734ce39`. Like R126, this round
DID get a fresh API mergeable read at the new head — true/clean —
so the clean verdict at `c0b65f6` is this round's own read, not a carried
forward one.

R127 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `c0b65f6` (443 commits / 2773 files /
  257689 additions; the fresh git derivation at `c0b65f6`, the fresh API
  read ~08:41 JST, and the merge-tree cross-check at `c0b65f6` are cited,
  with the fresh true/clean mergeable read at the new head disclosed
  above; live body R119; delta `5c2b304..c0b65f6`: 5 paths, 301
  insertions, 9 deletions); one row appended — PR119 BODY RESTRUCTURE
  R126 (`4ea252d`/`c0b65f6`), recording that its payload was prepared
  ~07:47 JST and NOT posted (live body still R119, verified by this
  round's API read) — superseded by R127; issue line re-read fresh this
  round (34 comments, latest ACK `6862732081`, no new direction). The
  index now covers every block through `c0b65f6`; R127's own 2 commits
  fold in at the next index update (R128), disclosed in the index itself.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `c0b65f6` · 443 · 2773 (with the fresh git derivation at `c0b65f6`,
  the fresh API read ~08:41 JST, and the fresh merge-tree cross-check at
  `c0b65f6`), plus the R126 paragraph in "Khối mới nhất" (marked chưa
  đăng — live body is still R119) and the R127 note. The stale index
  reference in "Về bản mô tả này" (head `5c2b304`) is also fixed to
  `c0b65f6`. Small correction carried in the same head line: the API-read
  timestamp it cited (`~06:41 JST`, carried over from R125's edit into
  R126's line) is corrected to this round's fresh read (`~08:41 JST`).
  The live PR description is refreshed from this file in the
  posting round that follows R127 (owner tap) — the R119 body v2 now
  live is the base; only the R126 paragraph (posting note) + new head
  line are new vs live.
- **Checker** `check_pr119_restructure_r127_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, plus the title-sequence check (full
  R93–R126 run in the title line, guarding the R94 slip fixed by R98).
  **PASS 18/18**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R127_VALIDATION_20261120.json`).
  First run PASS 18/18 (no amend needed for the checker itself). The
  checker was written fresh (not sed-copied from R126) with the full
  COVER SHA verified intact and a stale-reference grep (0 stale
  `cac65bc`/`5c2b304`/`2770`/`257397`/`28423fc7`/`37fcb56f` references in the checker —
  the R125 values) before the run — the R69 sed-order
  copy defect (mangled full COVER SHA) was avoided by construction.
  The 11 `4ea252d`/`c0b65f6` hits in the checker are the intended
  assertions that the index row carries the R126 content/report SHAs.

## Verification

- Merge-tree `c0b65f6` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `cbc4d5e5f1967e8c31672cafd60dce34e734ce39`. Merge-tree at the R127
  content head `ec0d84f` vs `f3db6b3`: exit 0, tree
  `a019055d06ac20a7247f07277bb67f1c7d2e3e87`.
- Live PR state: API curl read ~08:41 JST — title ends "+ R119"
  (R126 NOT posted; R119 posted live ~01:18 JST); head `c0b65f6`; live
  body R119 (73.631 ký tự, sha256 `9dac3461`, read back byte-exact this
  round); mergeable **true / clean** at the new head (fresh read this
  round).
- Issue #116: RE-READ this round via the comments API with curl
  (~08:41 JST, `per_page=100`): still 34 comments, latest
  ACK `6862732081` (CP5 + M-G CP10 + R2, updated_at 2026-11-13T19:24:48Z);
  no new Codex/owner direction since Gói 39 (`6815238814`). The 5
  comments after Gói 39 are all Muse ACKs of completed work, not new
  direction.
- Scope audit: R127 block 3 paths / 0 violations; cumulative at the R127
  content commit `ec0d84f` 2774 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4cfa38` on both sides, re-verified at `ec0d84f`).
  Merge-tree at the R127 content head `ec0d84f` vs `f3db6b3`: exit 0,
  tree `a019055d…`.
- Transient note: both API reads this round (`pulls/119` and the issue
  comments) returned HTTP 200 on the first try — no transient 403
  rate-limit this round. The MCP read tools `pull_request_read` /
  `issue_read` are not in the connector's reviewed read-only set (they
  ask for write-capable approval), so this round used unauthenticated
  curl for the public PR endpoint (`pulls/119`) plus the public issue
  comments — both worked, no approval card was needed for the reads.

## Next

Posting round (owner tap): PR #119 description refresh to the R127 body
v2 (R126 posting note + new head line are the only new parts vs the
live R119 body). Payload `pr119_update_body_v2_r127.json` prepared at
`~/workspace/godot-prototype/pr_comments/` after the R127 push (title
ending "+ R127", built by replacing the "+ R126" suffix — not appending;
body = body v2 R127 in repo, head line refreshed to head after R127 push).
This run started ~08:40 JST, in quiet hours (before 09:00 JST) — NOT
presented; presentation belongs to the main agent in working hours
(09:00–21:30 JST), or R128 will supersede it — but the owner was awake
and active at 00:40–01:18 JST (tapped the stale R115 widget, then posted
R118 ~00:41 JST and R119 ~01:18 JST) and the R121 widget was presented
~02:52 JST, so the main agent may present early if he is still at the
machine. The R126 payload is NOT posted — do not post it. No separate ACK
comment for R127: its content is pure bookkeeping. Standing blocks
unchanged: 32 shots await character lock; ear audition is the owner's
ears; full OGV 720p deferred per Gói 39; SFX binding awaits Codex.
