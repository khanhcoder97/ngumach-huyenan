"""Verify a checkout for Goi 31 item 5 (.gitattributes policy gap).

Checks, all from real bytes on disk (no network, no ear audition):

1. policy_ogv_lfs -- root .gitattributes contains the owner-approved
   `*.ogv filter=lfs diff=lfs merge=lfs -text` rule.
2. policy_lf_rules -- root .gitattributes contains the 7 LF rules for
   media delivery JSON/SRT paths (owner policy, integration 6f2b465).
3. policy_matches_reference -- when --reference-policy is given (a
   .gitattributes extracted from the current integration branch), every
   non-blank, non-comment rule line of the reference is present in the
   checkout's root .gitattributes. The reference is the source of truth;
   this tool never writes policy, it only reports the gap.
4. ogv_real_bytes -- every *.ogv under the media roots starts with the
   OggS magic (real Theora bytes), not a Git LFS pointer
   (`version https://git-lfs.github.com/spec/v1`).
5. text_lf_endings -- every *.json / *.srt under the media roots has
   LF-only line endings (no CR byte). NOTE: on a Linux checkout this
   passes even without the policy, because git does not convert endings
   here; the policy gap matters for Windows checkouts, so a PASS here is
   recorded as Linux-only evidence, never as proof the policy is present.

Exit 0 when every check passes, 1 otherwise. Writes a JSON report to
--out when given, and always prints the JSON to stdout.

Usage:
  python3 verify_fresh_checkout_item5.py --checkout <path>
      [--out <report.json>] [--reference-policy <gitattributes file>]
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOL_VERSION = "1.0.0"

# Owner-approved policy rules for media delivery, as present on the
# integration branch codex/story-gameplay-integration-20261031 at
# 6f2b465 (PR #123 merged). The root .gitattributes file is Codex-owned;
# Muse must not author its own policy -- this list is only the expected
# state the checker compares against.
EXPECTED_OGV_RULE = "*.ogv filter=lfs diff=lfs merge=lfs -text"
EXPECTED_LF_RULES = [
    "Art_Source/Cinematics/**/*.json text eol=lf",
    "Art_Source/Audio/Muse/**/*.json text eol=lf",
    "Implementation/Content/Narrative/Deliveries/**/*.json text eol=lf",
    "Implementation/Content/Narrative/Deliveries/**/*.srt text eol=lf",
    "ClientGodot/assets/cinematics/**/*.json text eol=lf",
    "ClientGodot/assets/cinematics/**/*.srt text eol=lf",
    "ClientGodot/assets/audio/**/*.json text eol=lf",
]

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


def read_attributes_lines(checkout: Path):
    path = checkout / ".gitattributes"
    if not path.is_file():
        return None
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
    ]


def git_head(checkout: Path):
    try:
        out = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            text=True, stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except Exception:
        return None


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
    passed = len(pointer) == 0 and len(other) == 0 and len(real) > 0
    return {
        "passed": passed,
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", required=True)
    parser.add_argument("--out", default=None)
    parser.add_argument("--reference-policy", default=None)
    args = parser.parse_args()

    checkout = Path(args.checkout)
    if not checkout.is_dir():
        print(f"checkout not found: {checkout}", file=sys.stderr)
        return 2

    attr_lines = read_attributes_lines(checkout)
    attr_set = set(attr_lines) if attr_lines is not None else set()

    ogv_check = {
        "passed": EXPECTED_OGV_RULE in attr_set,
        "expected": EXPECTED_OGV_RULE,
        "present": EXPECTED_OGV_RULE in attr_set,
    }
    missing_lf = [r for r in EXPECTED_LF_RULES if r not in attr_set]
    lf_check = {
        "passed": len(missing_lf) == 0,
        "expected_count": len(EXPECTED_LF_RULES),
        "missing": missing_lf,
    }

    ref_check = None
    if args.reference_policy:
        ref_lines = [
            line.strip()
            for line in Path(args.reference_policy).read_text(
                encoding="utf-8", errors="replace").splitlines()
        ]
        ref_rules = [l for l in ref_lines if l and not l.startswith("#")]
        missing_ref = [l for l in ref_rules if l not in attr_set]
        ref_check = {
            "passed": len(missing_ref) == 0,
            "reference": str(args.reference_policy),
            "reference_rules": len(ref_rules),
            "missing": missing_ref,
        }

    ogv_bytes = check_ogv(checkout)
    endings = check_text_endings(checkout)

    checks = {
        "policy_ogv_lfs": ogv_check,
        "policy_lf_rules": lf_check,
        "ogv_real_bytes": ogv_bytes,
        "text_lf_endings": endings,
    }
    if ref_check is not None:
        checks["policy_matches_reference"] = ref_check

    verdict = all(c["passed"] for c in checks.values())
    report = {
        "tool": "verify_fresh_checkout_item5.py",
        "tool_version": TOOL_VERSION,
        "checkout": str(checkout),
        "checkout_head": git_head(checkout),
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy_source": "integration codex/story-gameplay-integration-20261031 @ 6f2b465",
        "attributes_file_present": attr_lines is not None,
        "checks": checks,
        "verdict": "PASS" if verdict else "FAIL",
    }
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
