#!/usr/bin/env python3
"""R2 validator: PR #119 delivery index + body v2 coverage through 286787b.

Verifies the R2 restructure round: the delivery index now covers R1,
WO37 M-B CP5 and WO37 M-G CP10 (coverage head 286787b), and the repo
body v2 file is synced to the live CP5 body + the M-G CP10 block.
All figures re-derived from git, never copied from the documents.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "286787bcb3624bc9218653cbb1162eb6ba1bb19c"
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

    chk("index header coverage head == 286787b", "(head `286787b`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("50cc042", "5dece1f", "257c985", "8f7120a", "7bba119", "286787b"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 193/2398", "**193 commit / 2398 file**" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..286787b == 193", n_commits == 193, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..286787b == 2398", n_files == 2398, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 224498, deletions 0",
        "224498 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree 286787b vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line 286787b/193/2398",
        "**Head: `286787b` · 193 commit · 2398 file**" in body)
    chk("body has M-G CP10 paragraph", "- **WO37 M-G CP10**" in body)
    chk("body has M-B CP5 paragraph", "- **WO37 M-B CP5**" in body)
    chk("body index reference at 286787b", "(head `286787b`)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R2",
           "validator": "check_pr119_restructure_r2_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
