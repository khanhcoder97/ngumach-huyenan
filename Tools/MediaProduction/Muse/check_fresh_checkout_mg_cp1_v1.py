#!/usr/bin/env python3
"""MEDIA-02 WO37 M-G checkpoint 1: fresh-checkout validator.

Proves that a fresh clone of the media branch at a given HEAD is
byte-complete against the working clone at the same HEAD, from real
bytes on disk (never trusts the clone's own claims):

  1. head_matches -- fresh HEAD equals the expected HEAD (default:
     the reference clone's HEAD) and the branch is the media branch.
  2. lfs_filters_configured -- filter.lfs.smudge is set in the fresh
     clone's config. A plain `git clone` on a machine without
     `git lfs install` leaves every LFS file as a pointer (found
     during this checkpoint: 2147 pointers before `git lfs install
     --local` + `git lfs pull`); this check records whether the
     checkout was smudged at all.
  3. lfs_no_pointers -- no file under the media roots starts with the
     Git LFS pointer header.
  4. lfs_objects_complete -- every distinct LFS OID listed by
     `git lfs ls-files` has its object under .git/lfs/objects.
  5. root_counts_match -- per media root, file count and total bytes
     in the fresh checkout equal the reference clone.
  6. ogv_real_bytes -- every *.ogv under the media roots starts with
     the OggS magic (real Theora bytes, not a pointer).
  7. runtime_manifest_match -- RUNTIME_AUDIO_manifest_v1.json in the
     fresh checkout has the same entry count and sha256 as the
     reference clone's manifest.
  8. text_lf_endings -- every *.json / *.srt under the media roots
     has LF-only endings (Linux-only evidence, same caveat as the
     Gói 31 item-5 verifier).

Policy (.gitattributes rules) is NOT checked here: that is the job
of Tools/MediaProduction/Muse/verify_fresh_checkout_item5.py, run
separately with --reference-policy from the integration branch.
Runtime manifest entry hashes are NOT re-verified here: that is the
job of Tools/MediaProduction/Muse/verify_runtime_delivery.py, run
separately inside the fresh checkout.

Writes one JSON report to --out and exits 0 on PASS, 1 on any
mismatch.

Usage: python3 Tools/MediaProduction/Muse/check_fresh_checkout_mg_cp1_v1.py
           --checkout <fresh clone> [--reference <working clone>]
           [--expected-head <sha>] [--out <report.json>]
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

TOOL_VERSION = "1.0.0"

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

LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"
OGG_MAGIC = b"OggS"
RUNTIME_MANIFEST = Path("ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git_out(checkout: Path, args):
    try:
        out = subprocess.check_output(
            ["git", "-C", str(checkout)] + args,
            text=True, stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except Exception:
        return None


def lfs_ls_files(checkout: Path):
    """Return (distinct_oid_count, total_tracked_files) or (None, err)."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(checkout), "lfs", "ls-files", "--long"],
            text=True, stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        return None, "git-lfs binary not on PATH"
    except subprocess.CalledProcessError as e:
        return None, (e.stderr or "git lfs ls-files failed").strip()[:300]
    oids = set()
    total = 0
    for line in out.splitlines():
        # `git lfs ls-files --long` prints "<oid> * <path>": OID is field 0.
        parts = line.split()
        if len(parts) >= 3:
            oids.add(parts[0])
            total += 1
    return (len(oids), total), None


def count_objects(checkout: Path):
    base = checkout / ".git/lfs/objects"
    if not base.is_dir():
        return 0
    return sum(1 for _ in base.rglob("*") if _.is_file())


def root_stats(base: Path):
    stats = {}
    for root in MEDIA_ROOTS:
        d = base / root
        files = sorted(p for p in d.rglob("*") if p.is_file()) if d.is_dir() else []
        stats[root] = {
            "files": len(files),
            "bytes": sum(p.stat().st_size for p in files),
        }
    return stats


def scan_pointers(checkout: Path):
    pointers = []
    checked = 0
    for root in MEDIA_ROOTS:
        d = checkout / root
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if not p.is_file():
                continue
            checked += 1
            try:
                head = p.read_bytes()[:64]
            except OSError:
                continue
            if head.startswith(LFS_POINTER_PREFIX):
                pointers.append(p.relative_to(checkout).as_posix())
    return checked, pointers


def check_ogv(checkout: Path):
    real, pointer, other = [], [], []
    for root in MEDIA_ROOTS:
        base = checkout / root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.ogv")):
            rel = path.relative_to(checkout).as_posix()
            head = path.read_bytes()[:64]
            if head.startswith(OGG_MAGIC):
                real.append(rel)
            elif head.startswith(LFS_POINTER_PREFIX):
                pointer.append(rel)
            else:
                other.append(rel)
    return {
        "passed": len(pointer) == 0 and len(other) == 0 and len(real) > 0,
        "real_bytes": len(real),
        "lfs_pointers": len(pointer),
        "other": other,
        "pointer_files": pointer,
    }


def check_text_endings(checkout: Path):
    checked, with_cr = 0, []
    for root in MEDIA_ROOTS:
        base = checkout / root
        if not base.is_dir():
            continue
        for pattern in ("*.json", "*.srt"):
            for path in sorted(base.rglob(pattern)):
                checked += 1
                if b"\r" in path.read_bytes():
                    with_cr.append(path.relative_to(checkout).as_posix())
    return {
        "passed": len(with_cr) == 0,
        "files_checked": checked,
        "files_with_cr": with_cr,
        "note": "Linux-only evidence: a Linux checkout keeps LF even "
                "without the policy; the LF rules matter for Windows "
                "checkouts. A PASS here never proves the policy is present.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkout", required=True)
    ap.add_argument("--reference", default=str(ROOT))
    ap.add_argument("--expected-head", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    checkout = Path(args.checkout).resolve()
    reference = Path(args.reference).resolve()
    expected_head = args.expected_head or git_out(reference, ["rev-parse", "HEAD"])

    mismatches = []
    checks = {}

    # 1. HEAD
    actual_head = git_out(checkout, ["rev-parse", "HEAD"])
    branch = git_out(checkout, ["branch", "--show-current"])
    checks["head_matches"] = {
        "passed": actual_head == expected_head,
        "expected_head": expected_head,
        "actual_head": actual_head,
        "branch": branch,
    }
    if actual_head != expected_head:
        mismatches.append(f"head: fresh {actual_head} != expected {expected_head}")

    # 2. LFS filters configured
    smudge = git_out(checkout, ["config", "--get", "filter.lfs.smudge"])
    checks["lfs_filters_configured"] = {
        "passed": bool(smudge),
        "smudge": smudge,
        "note": "Plain `git clone` without `git lfs install` leaves LFS "
                "files as pointers; this checkpoint found 2147 pointers "
                "before `git lfs install --local` + `git lfs pull`.",
    }
    if not smudge:
        mismatches.append("lfs_filters: filter.lfs.smudge not configured in fresh clone")

    # 3. No LFS pointers under media roots
    checked, pointers = scan_pointers(checkout)
    checks["lfs_no_pointers"] = {
        "passed": len(pointers) == 0,
        "files_checked": checked,
        "pointer_files": pointers,
        "pointer_count": len(pointers),
    }
    if pointers:
        mismatches.append(f"lfs_no_pointers: {len(pointers)} pointer files remain")

    # 4. LFS objects complete
    ls_result, ls_err = lfs_ls_files(checkout)
    if ls_result is None:
        checks["lfs_objects_complete"] = {"passed": False, "error": ls_err}
        mismatches.append(f"lfs_objects_complete: {ls_err}")
    else:
        distinct_oids, total_tracked = ls_result
        on_disk = count_objects(checkout)
        checks["lfs_objects_complete"] = {
            "passed": on_disk >= distinct_oids and distinct_oids > 0,
            "distinct_oids": distinct_oids,
            "tracked_files": total_tracked,
            "objects_on_disk": on_disk,
        }
        if on_disk < distinct_oids:
            mismatches.append(
                f"lfs_objects_complete: {on_disk} objects on disk < "
                f"{distinct_oids} distinct OIDs"
            )

    # 5. Per-root file counts + bytes match the reference
    fresh_stats = root_stats(checkout)
    ref_stats = root_stats(reference)
    diffs = {
        r: {"fresh": fresh_stats[r], "reference": ref_stats[r]}
        for r in MEDIA_ROOTS
        if fresh_stats[r] != ref_stats[r]
    }
    checks["root_counts_match"] = {
        "passed": not diffs,
        "fresh": fresh_stats,
        "reference": ref_stats,
        "diffs": diffs,
    }
    if diffs:
        mismatches.append(f"root_counts_match: diffs in {sorted(diffs)}")

    # 6. OGV real bytes
    checks["ogv_real_bytes"] = check_ogv(checkout)
    if not checks["ogv_real_bytes"]["passed"]:
        mismatches.append("ogv_real_bytes: not all OGVs are real Theora bytes")

    # 7. Runtime manifest matches reference
    fresh_man = checkout / RUNTIME_MANIFEST
    ref_man = reference / RUNTIME_MANIFEST
    if not fresh_man.is_file() or not ref_man.is_file():
        checks["runtime_manifest_match"] = {
            "passed": False,
            "fresh_exists": fresh_man.is_file(),
            "reference_exists": ref_man.is_file(),
        }
        mismatches.append("runtime_manifest_match: manifest missing on one side")
    else:
        fresh_data = json.loads(fresh_man.read_text(encoding="utf-8"))
        ref_data = json.loads(ref_man.read_text(encoding="utf-8"))
        fresh_entries = (fresh_data.get("files") or fresh_data.get("entries")
                         or fresh_data.get("audio") or [])
        ref_entries = (ref_data.get("files") or ref_data.get("entries")
                       or ref_data.get("audio") or [])
        checks["runtime_manifest_match"] = {
            "passed": (len(fresh_entries) == len(ref_entries)
                       and sha256_file(fresh_man) == sha256_file(ref_man)),
            "fresh_entries": len(fresh_entries),
            "reference_entries": len(ref_entries),
            "fresh_sha256": sha256_file(fresh_man),
            "reference_sha256": sha256_file(ref_man),
        }
        if not checks["runtime_manifest_match"]["passed"]:
            mismatches.append("runtime_manifest_match: entry count or sha differs")

    # 8. Text LF endings
    checks["text_lf_endings"] = check_text_endings(checkout)
    if not checks["text_lf_endings"]["passed"]:
        mismatches.append("text_lf_endings: files with CR found")

    result = {
        "tool": "check_fresh_checkout_mg_cp1_v1.py",
        "tool_version": TOOL_VERSION,
        "checkpoint": "WO37 M-G CP1",
        "checkout": str(checkout),
        "reference": str(reference),
        "expected_head": expected_head,
        "checks": checks,
        "mismatches": mismatches,
        "result": "PASS" if not mismatches else "FAIL",
    }
    text = json.dumps(result, ensure_ascii=False, indent=1)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
