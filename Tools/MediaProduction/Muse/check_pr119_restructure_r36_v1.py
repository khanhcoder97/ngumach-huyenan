#!/usr/bin/env python3
"""R36 validator: PR #119 delivery index + body v2 coverage through 03b0a8a.

Verifies the R36 restructure round: the delivery index now covers R35
(coverage head 03b0a8a), and the repo body v2 file is synced to the
R34 body v2 file + the R34 block. All figures re-derived from git, never
copied from the documents.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "03b0a8a2c63a107018155e034cfe73f5e2fd4cfa"
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

    chk("index header coverage head == 03b0a8a", "(head `03b0a8a`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("6bad562", "03b0a8a"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 261/2500", "**261 commit / 2500 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R35 note", "Cập nhật R35" in index)
    chk("index R35 row label", "PR119 BODY RESTRUCTURE R35" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..03b0a8a == 261", n_commits == 261, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..03b0a8a == 2500", n_files == 2500, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 232462, deletions 0",
        "232462 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree 03b0a8a vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line 03b0a8a/261/2500",
        "**Head: `03b0a8a` · 261 commit · 2500 file**" in body)
    chk("body has R35 paragraph", "- **PR119 BODY RESTRUCTURE R35**" in body)
    chk("body title mentions R35", "PR119 BODY RESTRUCTURE R35" in body)
    chk("body index reference at 03b0a8a", "(head `03b0a8a`)" in body)
    chk("body R35 note", "R36 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R35",
           "validator": "check_pr119_restructure_r36_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
