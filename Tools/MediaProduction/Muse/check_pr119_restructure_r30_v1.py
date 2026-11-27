#!/usr/bin/env python3
"""R30 validator: PR #119 delivery index + body v2 coverage through 8ed54cd.

Verifies the R30 restructure round: the delivery index now covers R29
(coverage head 8ed54cd), and the repo body v2 file is synced to the
R29 body v2 file + the R29 block. All figures re-derived from git, never
copied from the documents.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "8ed54cded7a82c2635c4c20c4a29cdb22a5db69e"
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

    chk("index header coverage head == 8ed54cd", "(head `8ed54cd`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("406f12f", "8ed54cd"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 249/2482", "**249 commit / 2482 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R29 note", "Cập nhật R29" in index)
    chk("index R29 row label", "PR119 BODY RESTRUCTURE R29" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..8ed54cd == 249", n_commits == 249, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..8ed54cd == 2482", n_files == 2482, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 230972, deletions 0",
        "230972 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree 8ed54cd vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line 8ed54cd/249/2482",
        "**Head: `8ed54cd` · 249 commit · 2482 file**" in body)
    chk("body has R29 paragraph", "- **PR119 BODY RESTRUCTURE R29**" in body)
    chk("body title mentions R29", "PR119 BODY RESTRUCTURE R29" in body)
    chk("body index reference at 8ed54cd", "(head `8ed54cd`)" in body)
    chk("body R29 note", "R30 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R30",
           "validator": "check_pr119_restructure_r30_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
