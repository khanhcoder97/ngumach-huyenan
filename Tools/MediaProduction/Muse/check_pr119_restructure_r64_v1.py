#!/usr/bin/env python3
"""R64 validator: PR #119 delivery index + body v2 coverage through 5bebb91.

Verifies the R64 restructure round: the delivery index now covers R63
(coverage head 5bebb91), and the repo body v2 file is synced to the
R63 body v2 file + the R63 block. All figures re-derived from git, never
copied from the documents.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "5bebb919d46cfff5c08a73ccc81747c7e87b73ff"
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

    chk("index header coverage head == 5bebb91", "(head `5bebb91`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("eafa429", "5bebb91"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 317/2584", "**317 commit / 2584 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R64 note", "Cập nhật R64" in index)
    chk("index R63 row label", "PR119 BODY RESTRUCTURE R63" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..5bebb91 == 317", n_commits == 317, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..5bebb91 == 2584", n_files == 2584, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 239767, deletions 0",
        "239767 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree 5bebb91 vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line 5bebb91/317/2584",
        "**Head: `5bebb91` · 317 commit · 2584 file**" in body)
    chk("body has R63 paragraph", "- **PR119 BODY RESTRUCTURE R63**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R36 and R63",
        "PR119 BODY RESTRUCTURE R36" in title_line
        and "PR119 BODY RESTRUCTURE R63" in title_line, title_line[-60:])
    chk("body index reference at 5bebb91", "(head `5bebb91`)" in body)
    chk("body R64 note", "R64 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R63",
           "validator": "check_pr119_restructure_r64_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
