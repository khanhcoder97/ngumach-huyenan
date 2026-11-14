# MEDIA-02 Checkpoint — WO37 M-G CP1: fresh-checkout QA at head 41a6faa

Date: 2026-11-09 (JST). Branch: `muse/media-production-20261104`.
Integration baseline: `6f79853`. PR #119 stays HOLD; Muse does not
self-merge. Production OFF.

## What was delivered

WO37 M-G checkpoint 1 is the first full fresh-checkout verification
of the media branch since the M-D/M-F/M-E checkpoint wave (CP43–54,
M-C motion, M-D CP1–CP9, M-F CP1, M-E CP1 — 60+ commits since the
Gói 31 item-5 fresh check). A plain `git clone` of
`muse/media-production-20261104` was made into scratch
(`~/workspace/projects/media02-scratch/mg_cp1_fresh`, kept for
re-checks, not part of the repo), then verified byte-for-byte
against the working clone at the same HEAD, **41a6faa**
(M-E CP1 report):

- Fresh HEAD = `41a6faacfdc628d064b48b40a365bc941f5f8f80`, branch
  `muse/media-production-20261104` — matches the working clone.
- `git lfs ls-files`: 2709 tracked files / **2013 distinct OIDs**;
  **2013 objects on disk** after pull — complete, no missing object.
- **0 LFS pointer files** under the 7 media roots (2013 files
  header-checked). `git lfs fsck`: OK.
- Per-root file counts + byte totals match the working clone exactly
  (measured before this report's own files were written):
  Cinematics 451 files / 219,733,487 B; Audio/Muse 315 /
  1,626,163,856 B; cinematics runtime 174 / 107,755,934 B; audio
  runtime 784 / 304,098,533 B; Narrative Deliveries 50 / 343,200 B;
  Audio Deliveries 18 / 1,450,104 B; Reports/MuseMedia 221 /
  2,630,402 B.
- OGV: 22/22 real Theora bytes (`OggS` magic), 0 pointers.
- Runtime manifest: 783 entries, sha256 identical on both sides
  (`f0e3a015…9806c`).
- Text endings: 367 JSON/SRT files checked, 0 CR bytes.
- Gói 31 item-5 verifier re-run on the fresh checkout with the
  reference policy extracted from integration `6f79853`: **PASS** —
  OGV LFS rule present, all 7 LF rules present, all 29 reference
  rules present, 0 missing. The item-5 policy gap stays closed at
  this head (it was closed by the owner's PR #127 merge on
  2026-11-08; this run re-confirms it, it does not re-close it).
- Runtime re-verify run **inside the fresh checkout**: **PASS, 0
  mismatches** — 783 runtime audio files, 7 prologue files, 3
  animatic files, 20 scenes / 20 timing / 20 SRT / 20 scene clips /
  100 clip files. Manifest counts: music/ambience 22, SFX/UI 519,
  VO 50, mix 30, composed 162. Campaign totals unchanged: 20 scenes
  / 63 shots / 378 s / 21 dialogue cues.

## Onboarding finding: a plain clone leaves pointers

The first fresh clone checked out **2147 LFS pointer files** and 0
LFS objects (working tree 55 MB). Cause: this machine has no global
`git lfs install` — the LFS filters live only in the working
clone's **local** git config, so a new clone has no smudge filter
and git silently leaves pointers. The checkout was repaired with
`git lfs install --local` + `git lfs pull` (2709 files, ~4.4 GB,
all objects fetched, exit 0). The M-G validator now checks
`filter.lfs.smudge` explicitly so a future fresh checkout fails
loudly instead of silently verifying pointers. The repo's own
`.gitattributes` already says "requires `git lfs install` before
adding files" — the same requirement applies before *cloning* for
a usable checkout. No repo file was changed for this; it is a
machine-setup note, not a policy change.

A crude whole-tree `grep` for the LFS spec URL returns 7 files —
these are **not** pointer files: 5 `.py` sources + 1 test quote the
pointer prefix as a constant, and the CP35 item-5 report quotes it
as text. The validator checks the first 64 bytes (`startswith`),
which is the authoritative test: 0 pointers.

## Tables and runtime state

- Runtime audio unchanged: **783** (composed 162, ported 541
  unchanged, music/ambience 22, SFX/UI 519, VO 50, mix 30).
  Campaign totals unchanged: 20/63/378/21. Playback metadata
  unchanged (21 embedded / 0 silent); pronunciation table
  unchanged. Prologue unchanged.
- PR #119 at this head: open, head `41a6faa`, mergeable True /
  clean (API read 2026-11-09 ~09:40 JST); 11/11 CI check-runs on
  head `41a6faa` completed success (legacy combined status still
  shows pending — check-runs are the authoritative signal).
- Issue #116: still 22 comments, latest 6728634496 (ACK M-D CP9 +
  M-F CP1) — no new Codex/owner direction; M-F CP2 (voice choice)
  and M-E CP2 (composed SFX decision) stay blocked on decisions
  that have not arrived.

## Validators

- `check_fresh_checkout_mg_cp1_v1.py` (new tool):
  **PASS, 0 mismatches**
  (`MEDIA02_WO37_MG_CP1_VALIDATION_20261109.json` — 8 checks:
  head, LFS filters, no pointers, objects complete, per-root
  counts, OGV bytes, runtime manifest, LF endings). One bug was
  found and fixed during this run: the tool first read the OID
  from field 1 of `git lfs ls-files --long` (`<oid> * <path>`)
  and got the constant `*` marker; it now reads field 0 and the
  distinct-OID count (2013) matches objects on disk exactly.
- `verify_fresh_checkout_item5.py` on the fresh checkout:
  **PASS** (`MEDIA02_WO37_MG_CP1_ITEM5_20261109.json` — 5/5
  checks, reference policy 29 rules from integration `6f79853`).
- `verify_runtime_delivery.py` inside the fresh checkout:
  **PASS, 0 mismatches**
  (`MEDIA02_WO37_MG_CP1_RUNTIME_REVERIFY_20261109.json`).
- Scope audit: content-only **1 path / 0 violations** (base
  `41a6faa` → head `6405d3a`); cumulative **2096 paths / 1
  known `.gitattributes` merge-base artifact** (base integration
  `6f79853` → head `6405d3a`; the 1 violation is the checker
  diffing from cf17178, NOT a real divergence — same artifact as
  all prior checkpoints).

## Limits

- Linux-only evidence: LF endings pass on Linux even without the
  policy; the policy-presence proof is the item-5 verifier's
  `policy_matches_reference` check (PASS, 29/29 rules), not the
  endings scan. No Windows checkout was available in this run —
  the Windows/device pack part of M-G is still open.
- No ear audition: every number here is a byte/hash/count check
  from real files; nothing was listened to.
- The fresh checkout lives in scratch outside the repo; it is not
  a deliverable and will be removed on the next fresh-checkout run.
- PR #119 description + ACK for M-G CP1 are prepared for the main
  thread (GitHub writes need the owner's approval card) — NOT
  posted by this run. The prepared payload supersedes the unposted
  M-E CP1-only payload pair.

## Next

M-F CP2 (palette-adoption re-mixes — blocked on the director/Codex
voice choice) or M-E CP2 (composed SFX — blocked on the Codex
decision) or M-G CP2 (Windows/device pack — needs a Windows
checkout). Nothing in this checkpoint unblocks them; the next run
re-checks issue #116 first.
