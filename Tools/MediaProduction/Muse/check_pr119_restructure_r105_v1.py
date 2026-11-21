#!/usr/bin/env python3
"""R105 validator: PR #119 delivery index + body v2 coverage through 9654c7f.

Verifies the R105 restructure round: the delivery index now covers R104
(coverage head 9654c7f), and the repo body v2 file is synced to the
R104 body v2 file + the R104 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R104 run is present in the title line.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "9654c7fcc5915fc032674e9fc7bc25084faf773e"
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

    chk("index header coverage head == 9654c7f", "(head `9654c7f`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("7d0854b", "9654c7f"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 399/2707", "**399 commit / 2707 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R105 note", "Cập nhật R105" in index)
    chk("index R104 row label", "PR119 BODY RESTRUCTURE R104" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..9654c7f == 399", n_commits == 399, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..9654c7f == 2707", n_files == 2707, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 251235, deletions 0",
        "251235 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree 9654c7f vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line 9654c7f/399/2707",
        "**Head: `9654c7f` · 399 commit · 2707 file**" in body)
    chk("body has R104 paragraph", "- **PR119 BODY RESTRUCTURE R104**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R104",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R104" in title_line, title_line[-60:])
    chk("body title has full R93..R104 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in (93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104)),
        "R94 restored, R104 added")
    chk("body index reference at 9654c7f", "(head `9654c7f`)" in body)
    chk("body R105 note", "R105 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R104",
           "validator": "check_pr119_restructure_r105_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
