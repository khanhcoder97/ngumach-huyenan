#!/usr/bin/env python3
"""R107 validator: PR #119 delivery index + body v2 coverage through 6a8561d.

Verifies the R107 restructure round: the delivery index now covers R106
(coverage head 6a8561d), and the repo body v2 file is synced to the
R106 body v2 file + the R106 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R106 run is present in the title line.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "6a8561d16e9ee634074b791ef57c908dd0556109"
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

    chk("index header coverage head == 6a8561d", "(head `6a8561d`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("c8c1154", "6a8561d"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 403/2713", "**403 commit / 2713 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R107 note", "Cập nhật R107" in index)
    chk("index R106 row label", "PR119 BODY RESTRUCTURE R106" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..6a8561d == 403", n_commits == 403, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..6a8561d == 2713", n_files == 2713, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 251822, deletions 0",
        "251822 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree 6a8561d vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line 6a8561d/403/2713",
        "**Head: `6a8561d` · 403 commit · 2713 file**" in body)
    chk("body has R106 paragraph", "- **PR119 BODY RESTRUCTURE R106**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R106",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R106" in title_line, title_line[-60:])
    chk("body title has full R93..R106 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in (93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106)),
        "R94 restored, R106 added")
    chk("body index reference at 6a8561d", "(head `6a8561d`)" in body)
    chk("body R107 note", "R107 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R106",
           "validator": "check_pr119_restructure_r107_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
