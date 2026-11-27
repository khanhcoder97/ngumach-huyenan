#!/usr/bin/env python3
"""R156 validator: PR #119 delivery index + body v2 coverage through 0cfe29c.

Verifies the R156 restructure round: the delivery index now covers R155
(coverage head 0cfe29c), and the repo body v2 file is synced to the
R155 body v2 file + the R155 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R155 run is present in the title line.
It also guards the R140 update-note defect (a content commit replaced the
previous "Cập nhật" note line instead of appending after it) by asserting
both the R155 and R156 note lines are present in the index.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "0cfe29cb109677b86e75ec9ea981602eb8701963"
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

    chk("index header coverage head == 0cfe29c", "(head `0cfe29c`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("ca5e1e3", "0cfe29c"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 501/2860", "**501 commit / 2860 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R156 note", "Cập nhật R156" in index)
    chk("index R155 note kept", "Cập nhật R155" in index)
    chk("index R155 row label", "PR119 BODY RESTRUCTURE R155" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..0cfe29c == 501", n_commits == 501, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..0cfe29c == 2860", n_files == 2860, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 266621, deletions 0",
        "266621 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 0cfe29c vs integration exit 0, tree b19b3280",
        mt.returncode == 0 and tree.startswith("b19b3280"), tree)

    chk("body head line 0cfe29c/501/2860",
        "**Head: `0cfe29c` · 501 commit · 2860 file**" in body)
    chk("body has R155 paragraph", "- **PR119 BODY RESTRUCTURE R155**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R155",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R155" in title_line, title_line[-60:])
    chk("body title has full R93..R155 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 156)),
        "R94 restored, R155 added")
    chk("body index reference at 0cfe29c", "(head `0cfe29c`)" in body)
    chk("body R156 note", "R156 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R155",
           "validator": "check_pr119_restructure_r156_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
