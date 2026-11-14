#!/usr/bin/env python3
"""R12 validator: PR #119 delivery index + body v2 coverage through 755c5da.

Verifies the R12 restructure round: the delivery index now covers R11
(coverage head 755c5da), and the repo body v2 file is synced to the
R11 body v2 file + the R11 block. All figures re-derived from git, never
copied from the documents.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "755c5da35433e6ac84cbeb81f6fdbe17e7dfaf24"
INTEGRATION = "f3db6b384886a59128328b8daa8c9eefc2d8f3ce"

def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    checks = {}
    def chk(name, ok, detail=""):
        checks[name] = {"pass": bool(ok), "detail": detail}

    index = (ROOT / "Implementation/Reports/MuseMedia/MEDIA02_PR119_DELIVERY_INDEX_20261113.md").read_text(encoding="utf-8")
    body = (ROOT / "Implementation/Reports/MuseMedia/MEDIA02_PR119_BODY_V2_20261113.md").read_text(encoding="utf-8")

    chk("index header coverage head == 755c5da", "(head `755c5da`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("e19616b", "755c5da"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 213/2428", "**213 commit / 2428 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R12 note", "Cập nhật R12" in index)
    chk("index R11 row label", "PR119 BODY RESTRUCTURE R11" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..755c5da == 213", n_commits == 213, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..755c5da == 2428", n_files == 2428, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 226693, deletions 0",
        "226693 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree 755c5da vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line 755c5da/213/2428",
        "**Head: `755c5da` · 213 commit · 2428 file**" in body)
    chk("body has R11 paragraph", "- **PR119 BODY RESTRUCTURE R11**" in body)
    chk("body title mentions R11", "PR119 BODY RESTRUCTURE R11" in body)
    chk("body index reference at 755c5da", "(head `755c5da`)" in body)
    chk("body R12 note", "R12 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R12",
           "validator": "check_pr119_restructure_r12_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
