#!/usr/bin/env python3
"""R101 validator: PR #119 delivery index + body v2 coverage through b32e7a2.

Verifies the R101 restructure round: the delivery index now covers R100
(coverage head b32e7a2), and the repo body v2 file is synced to the
R100 body v2 file + the R100 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R100 run is present in the title line.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "b32e7a2f41001d28d8d2566f8236b15b62e8ee18"
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

    chk("index header coverage head == b32e7a2", "(head `b32e7a2`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("a2a1f57", "b32e7a2"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 391/2695", "**391 commit / 2695 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R101 note", "Cập nhật R101" in index)
    chk("index R100 row label", "PR119 BODY RESTRUCTURE R100" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..b32e7a2 == 391", n_commits == 391, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..b32e7a2 == 2695", n_files == 2695, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 250051, deletions 0",
        "250051 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree b32e7a2 vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line b32e7a2/391/2695",
        "**Head: `b32e7a2` · 391 commit · 2695 file**" in body)
    chk("body has R100 paragraph", "- **PR119 BODY RESTRUCTURE R100**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R100",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R100" in title_line, title_line[-60:])
    chk("body title has full R93..R100 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in (93, 94, 95, 96, 97, 98, 99, 100)),
        "R94 restored, R100 added")
    chk("body index reference at b32e7a2", "(head `b32e7a2`)" in body)
    chk("body R101 note", "R101 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R100",
           "validator": "check_pr119_restructure_r101_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
