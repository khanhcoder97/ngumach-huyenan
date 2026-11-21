#!/usr/bin/env python3
"""R44 validator: PR #119 delivery index + body v2 coverage through e9f50ca.

Verifies the R44 restructure round: the delivery index now covers R43
(coverage head e9f50ca), and the repo body v2 file is synced to the
R43 body v2 file + the R43 block. All figures re-derived from git, never
copied from the documents.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "e9f50cacfee3c6a2351fbdaae9680df183f4cce0"
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

    chk("index header coverage head == e9f50ca", "(head `e9f50ca`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("8fa2728", "e9f50ca"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 277/2524", "**277 commit / 2524 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R44 note", "Cập nhật R44" in index)
    chk("index R43 row label", "PR119 BODY RESTRUCTURE R43" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..e9f50ca == 277", n_commits == 277, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..e9f50ca == 2524", n_files == 2524, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 234537, deletions 0",
        "234537 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree e9f50ca vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line e9f50ca/277/2524",
        "**Head: `e9f50ca` · 277 commit · 2524 file**" in body)
    chk("body has R43 paragraph", "- **PR119 BODY RESTRUCTURE R43**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R35 and R43",
        "PR119 BODY RESTRUCTURE R35" in title_line
        and "PR119 BODY RESTRUCTURE R43" in title_line, title_line[-60:])
    chk("body index reference at e9f50ca", "(head `e9f50ca`)" in body)
    chk("body R44 note", "R44 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R43",
           "validator": "check_pr119_restructure_r44_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
