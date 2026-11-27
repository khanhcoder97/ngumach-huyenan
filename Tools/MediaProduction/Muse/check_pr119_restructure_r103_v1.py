#!/usr/bin/env python3
"""R103 validator: PR #119 delivery index + body v2 coverage through 1a0a826.

Verifies the R103 restructure round: the delivery index now covers R102
(coverage head 1a0a826), and the repo body v2 file is synced to the
R102 body v2 file + the R102 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R102 run is present in the title line.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "1a0a826999b8f46198b28d2e0bfcea45493fb3f8"
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

    chk("index header coverage head == 1a0a826", "(head `1a0a826`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("5908bcf", "1a0a826"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 395/2701", "**395 commit / 2701 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R103 note", "Cập nhật R103" in index)
    chk("index R102 row label", "PR119 BODY RESTRUCTURE R102" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..1a0a826 == 395", n_commits == 395, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..1a0a826 == 2701", n_files == 2701, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 250646, deletions 0",
        "250646 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree 1a0a826 vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line 1a0a826/395/2701",
        "**Head: `1a0a826` · 395 commit · 2701 file**" in body)
    chk("body has R102 paragraph", "- **PR119 BODY RESTRUCTURE R102**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R102",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R102" in title_line, title_line[-60:])
    chk("body title has full R93..R102 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in (93, 94, 95, 96, 97, 98, 99, 100, 101, 102)),
        "R94 restored, R102 added")
    chk("body index reference at 1a0a826", "(head `1a0a826`)" in body)
    chk("body R103 note", "R103 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R102",
           "validator": "check_pr119_restructure_r103_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
