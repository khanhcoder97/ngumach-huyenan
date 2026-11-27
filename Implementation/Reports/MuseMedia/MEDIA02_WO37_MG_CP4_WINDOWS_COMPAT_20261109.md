# MEDIA-02 Checkpoint — WO37 M-G CP4: Windows-compatibility static audit at head e7cb9e4

Date: 2026-11-09 (JST). Branch: `muse/media-production-20261104`.
Integration baseline: `6f79853`. PR #119 stays HOLD; Muse does not
self-merge. Production OFF.

## What was delivered

WO37 M-G checkpoint 4 is the feasible slice of the Windows/device
pack: a static audit of the tracked tree at head **e7cb9e4** for the
properties that break a Windows checkout or a Godot-on-Windows
import. No Windows machine is available to this run, so this is a
static audit of real bytes in the working clone — it does NOT claim
a live Windows checkout, which remains the open M-G item.

Validator: `Tools/MediaProduction/Muse/check_windows_compat_mg_cp4_v1.py`
— **PASS, 8/8 checks, 0 mismatches**, over 2025 tracked files under
the 7 media roots:

- HEAD matches `e7cb9e49111c3e9ef5b950bb8ba66f727c6910e7`, branch
  `muse/media-production-20261104`.
- **0 paths** with a Windows-illegal character (`< > : " | ? *`,
  control chars) or a component ending in space/period.
- **0 reserved device names** (CON, PRN, AUX, NUL, COM1–9, LPT1–9)
  as basename stems.
- **0 case-insensitive collisions** (no two tracked paths equal
  after casefold — an NTFS checkout would not collapse files).
- **Path length: max 92 chars**, 0 paths over 200, 0 over 260
  (MAX_PATH). Longest paths are report filenames under
  `Implementation/Reports/MuseMedia` (92 chars). A Windows checkout
  under any normal base directory stays far below MAX_PATH.
- **0 symlinks** under the media roots (no mode 120000 entries).
- **LFS coverage: 1564/1564 binary media files** under the media
  roots are listed by `git lfs ls-files` — a Windows clone with
  git-lfs receives real bytes for every binary, not pointers.
- **Text endings: 461 files checked** (*.json / *.srt / *.md /
  *.txt), **0 CR bytes** — LF-only, extending the M-G CP1–3
  JSON/SRT check to md/txt.
- Info only: **0 non-ASCII filenames** under the media roots.

## Run notes — one failed validator attempt before the PASS

The final PASS is the second validator run; the first failed on the
tool's own parsing, not on the branch, and the cause is recorded
here so the PASS is not read as a re-run-until-green:

1. First run: `lfs_coverage` failed with 1564/1564 binary files
   "not in LFS". The tool split `git lfs ls-files` lines on
   `" - "`, but the real format is `"<oid> * <path>"` (or
   `"<oid> - <path>"` for pointer-only files) — so no line matched
   and the LFS set came out empty. The parser now splits on the
   marker token with maxsplit=2 (paths with spaces stay intact).
   Every other check passed on the first run, and the branch was
   never at fault. The second run measured the same HEAD and passed
   8/8.

## Tables and runtime state

- Runtime audio unchanged: **783** (composed 162, ported 541
  unchanged, music/ambience 22, SFX/UI 519, VO 50, mix 30).
  Campaign totals unchanged: 20/63/378/21. Playback metadata
  unchanged (21 embedded / 0 silent); pronunciation table
  unchanged. Prologue unchanged.
- No media bytes changed in this checkpoint: the only new files are
  the validator tool and this report + validation JSON.
- PR #119 at this head: open, head `e7cb9e4`, mergeable True /
  clean (API read 2026-11-09 ~12:40 JST; head verified
  independently by `git ls-remote`).

## Limits

- Static audit only: no live Windows checkout, no Godot import on
  Windows, no NTFS case-folding behaviour actually exercised. The
  live Windows/device pack (M-G CP5 candidate) still needs a
  Windows machine.
- Path-length verdict is on the relative path as checked out; a
  Windows base directory deeper than ~168 chars would push the
  longest (92-char) path past MAX_PATH — the audit lists the
  longest paths so that case can be judged.

## Files

- Tool: `Tools/MediaProduction/Muse/check_windows_compat_mg_cp4_v1.py`
  (new validator, 8 checks).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP4_VALIDATION_20261109.json`
  (validator PASS, 0 mismatches).

## Next

M-F CP2 (palette-adoption re-mixes — blocked on the director/Codex
voice choice) or M-E CP2 (composed SFX — blocked on the Codex
decision) or M-G CP5 (live Windows checkout — needs a Windows
machine). Nothing in this checkpoint unblocks them; the next run
re-checks issue #116 first.
