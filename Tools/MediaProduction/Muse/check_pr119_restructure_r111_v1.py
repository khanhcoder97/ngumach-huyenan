#!/usr/bin/env python3
"""R111 validator: PR #119 delivery index + body v2 coverage through 2140e20.

Verifies the R111 restructure round: the delivery index now covers R110
(coverage head 2140e20), and the repo body v2 file is synced to the
R110 body v2 file + the R110 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R110 run is present in the title line.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "2140e20978eb0c6a5b0ac5f22f6104a391309434"
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

    chk("index header coverage head == 2140e20", "(head `2140e20`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("cbfa9dd", "2140e20"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 411/2725", "**411 commit / 2725 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R111 note", "Cập nhật R111" in index)
    chk("index R110 row label", "PR119 BODY RESTRUCTURE R110" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..2140e20 == 411", n_commits == 411, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..2140e20 == 2725", n_files == 2725, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 253000, deletions 0",
        "253000 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree 2140e20 vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line 2140e20/411/2725",
        "**Head: `2140e20` · 411 commit · 2725 file**" in body)
    chk("body has R110 paragraph", "- **PR119 BODY RESTRUCTURE R110**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R110",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R110" in title_line, title_line[-60:])
    chk("body title has full R93..R110 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in (93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110)),
        "R94 restored, R110 added")
    chk("body index reference at 2140e20", "(head `2140e20`)" in body)
    chk("body R111 note", "R111 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R110",
           "validator": "check_pr119_restructure_r111_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
