#!/usr/bin/env python3
"""MEDIA-02 WO37 M-G checkpoint 4: Windows-compatibility static audit.

A Windows checkout / Godot-on-Windows import of the media branch
cannot be run on this Linux machine, so this checkpoint audits the
properties of the tracked tree that break a Windows checkout, from
real bytes in the working clone at a given HEAD (never trusts claims):

  1. head_matches -- HEAD equals the expected HEAD and the branch is
     the media branch.
  2. no_illegal_chars -- no path component contains a Windows-illegal
     character (< > : " | ? * or a control char) and no component
     ends with a space or a period (Windows strips / rejects those).
  3. no_reserved_names -- no basename stem (upper-cased, before the
     first dot) is a Windows reserved device name (CON, PRN, AUX,
     NUL, COM1-9, LPT1-9).
  4. no_case_collisions -- no two distinct tracked paths under the
     media roots are equal after casefold (a case-insensitive NTFS
     checkout would collapse them).
  5. path_length_ok -- no tracked path under the media roots is
     longer than 260 chars (MAX_PATH, relative path as checked out;
     the longest paths are listed so a deep Windows base dir can be
     judged). Paths over 200 chars are reported as info, not failure.
  6. no_symlinks -- no tracked entry under the media roots is a
     symlink (mode 120000).
  7. lfs_coverage -- every tracked file under the media roots with a
     binary media extension is listed by `git lfs ls-files` (so a
     Windows clone with git-lfs receives real bytes, not pointers).
  8. text_lf_endings -- every *.json / *.srt / *.md / *.txt under the
     media roots has LF-only endings (0 CR bytes). Extends the M-G
     CP1-3 JSON/SRT check to md/txt.

Non-ASCII filenames are counted as info only: Godot and Windows
handle UTF-8 names, but the count is recorded for the audit trail.

Writes one JSON report to --out and exits 0 on PASS, 1 on any
mismatch.

Usage: python3 Tools/MediaProduction/Muse/check_windows_compat_mg_cp4_v1.py
           [--expected-head <sha>] [--out <report.json>]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TOOL_VERSION = "1.0.0"
TOOL_NAME = "check_windows_compat_mg_cp4_v1.py"

ROOT = Path(__file__).resolve().parents[3]

MEDIA_ROOTS = [
    "Art_Source/Cinematics",
    "Art_Source/Audio/Muse",
    "ClientGodot/assets/cinematics",
    "ClientGodot/assets/audio",
    "Implementation/Content/Narrative/Deliveries",
    "Implementation/Content/Audio/Deliveries",
    "Implementation/Reports/MuseMedia",
]

BINARY_EXTS = {
    ".png", ".aseprite", ".psd", ".kra", ".wav", ".ogg", ".mp3",
    ".mp4", ".webm", ".ogv", ".flac",
}

TEXT_EXTS = {".json", ".srt", ".md", ".txt"}

ILLEGAL_CHARS = set('<>:"|?*')
RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}


def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expected-head", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    checks = {}
    details = {}

    head = run(["git", "rev-parse", "HEAD"]).strip()
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()
    expected = args.expected_head or head
    checks["head_matches"] = (head == expected and branch == "muse/media-production-20261104")
    details["head"] = head
    details["branch"] = branch
    details["expected_head"] = expected

    # Tracked files under the media roots.
    files = []
    for root in MEDIA_ROOTS:
        out = run(["git", "ls-files", "--", root])
        files.extend(p for p in out.splitlines() if p)
    files = sorted(set(files))
    details["tracked_under_media_roots"] = len(files)

    # 2. Illegal chars / trailing space-or-dot per component.
    bad_chars = []
    for p in files:
        for comp in p.split("/"):
            if any(c in ILLEGAL_CHARS or ord(c) < 32 for c in comp) or comp.endswith((" ", ".")):
                bad_chars.append(p)
                break
    checks["no_illegal_chars"] = not bad_chars
    details["illegal_char_paths"] = bad_chars

    # 3. Reserved device names.
    reserved = []
    for p in files:
        stem = Path(p).name.split(".")[0].upper()
        if stem in RESERVED:
            reserved.append(p)
    checks["no_reserved_names"] = not reserved
    details["reserved_name_paths"] = reserved

    # 4. Case-insensitive collisions.
    seen = {}
    collisions = []
    for p in files:
        key = p.casefold()
        if key in seen and seen[key] != p:
            collisions.append(sorted([seen[key], p]))
        else:
            seen[key] = p
    checks["no_case_collisions"] = not collisions
    details["case_collisions"] = collisions

    # 5. Path length.
    lengths = sorted(((len(p), p) for p in files), reverse=True)
    over_260 = [p for n, p in lengths if n > 260]
    over_200 = [p for n, p in lengths if n > 200]
    checks["path_length_ok"] = not over_260
    details["longest_paths"] = [{"path": p, "length": n} for n, p in lengths[:10]]
    details["paths_over_260"] = over_260
    details["paths_over_200_count"] = len(over_200)
    details["max_length"] = lengths[0][0] if lengths else 0

    # Non-ASCII names: info only.
    non_ascii = [p for p in files if any(ord(c) > 127 for c in p)]
    details["non_ascii_paths"] = non_ascii
    details["non_ascii_count"] = len(non_ascii)

    # 6. Symlinks (mode 120000) under media roots.
    symlinks = []
    for root in MEDIA_ROOTS:
        out = run(["git", "ls-files", "-s", "--", root])
        for line in out.splitlines():
            mode = line.split()[0]
            if mode == "120000":
                symlinks.append(line.split("\t", 1)[1])
    checks["no_symlinks"] = not symlinks
    details["symlink_paths"] = sorted(symlinks)

    # 7. LFS coverage for binary media extensions.
    lfs_out = run(["git", "lfs", "ls-files"])
    lfs_set = set()
    for line in lfs_out.splitlines():
        # Format: "<oid> * <path>" (object present) or "<oid> - <path>"
        # (pointer only); maxsplit=2 keeps paths with spaces intact.
        parts = line.split(" ", 2)
        if len(parts) == 3 and parts[1] in ("*", "-"):
            lfs_set.add(parts[2].strip())
        elif len(parts) == 3:
            lfs_set.add(parts[2].strip())
    binary_files = [p for p in files if Path(p).suffix.lower() in BINARY_EXTS]
    uncovered = [p for p in binary_files if p not in lfs_set]
    checks["lfs_coverage"] = not uncovered
    details["binary_files_under_media_roots"] = len(binary_files)
    details["lfs_tracked_under_media_roots"] = len([p for p in lfs_set if p in set(files)])
    details["binary_not_in_lfs"] = uncovered

    # 8. LF endings for text files under media roots.
    cr_files = []
    for p in files:
        if Path(p).suffix.lower() in TEXT_EXTS:
            data = (ROOT / p).read_bytes()
            if b"\r" in data:
                cr_files.append(p)
    checks["text_lf_endings"] = not cr_files
    details["text_files_checked"] = sum(1 for p in files if Path(p).suffix.lower() in TEXT_EXTS)
    details["cr_files"] = cr_files

    passed = all(checks.values())
    report = {
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "checkpoint": "MEDIA-02 WO37 M-G CP4",
        "head": head,
        "branch": branch,
        "checks": checks,
        "details": details,
        "result": "PASS" if passed else "FAIL",
        "mismatches": sum(1 for v in checks.values() if not v),
    }
    out_path = Path(args.out) if args.out else ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO37_MG_CP4_VALIDATION_20261109.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
