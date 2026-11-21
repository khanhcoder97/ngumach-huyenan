#!/usr/bin/env python3
"""R154 validator: PR #119 delivery index + body v2 coverage through 4dc1599.

Verifies the R154 restructure round: the delivery index now covers R153
(coverage head 4dc1599), and the repo body v2 file is synced to the
R153 body v2 file + the R153 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R153 run is present in the title line.
It also guards the R140 update-note defect (a content commit replaced the
previous "Cập nhật" note line instead of appending after it) by asserting
both the R153 and R154 note lines are present in the index.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "4dc159965d656b603fdbca36cab70851c071a3fe"
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

    chk("index header coverage head == 4dc1599", "(head `4dc1599`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("d51e2f3", "4dc1599"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 497/2854", "**497 commit / 2854 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R154 note", "Cập nhật R154" in index)
    chk("index R153 note kept", "Cập nhật R153" in index)
    chk("index R153 row label", "PR119 BODY RESTRUCTURE R153" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..4dc1599 == 497", n_commits == 497, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..4dc1599 == 2854", n_files == 2854, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 265982, deletions 0",
        "265982 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 4dc1599 vs integration exit 0, tree 94adb25e",
        mt.returncode == 0 and tree.startswith("94adb25e"), tree)

    chk("body head line 4dc1599/497/2854",
        "**Head: `4dc1599` · 497 commit · 2854 file**" in body)
    chk("body has R153 paragraph", "- **PR119 BODY RESTRUCTURE R153**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R153",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R153" in title_line, title_line[-60:])
    chk("body title has full R93..R153 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 154)),
        "R94 restored, R153 added")
    chk("body index reference at 4dc1599", "(head `4dc1599`)" in body)
    chk("body R154 note", "R154 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R153",
           "validator": "check_pr119_restructure_r154_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
