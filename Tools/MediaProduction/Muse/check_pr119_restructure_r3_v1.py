#!/usr/bin/env python3
"""R3 validator: PR #119 delivery index + body v2 coverage through 08dd9d2.

Verifies the R3 restructure round: the delivery index now covers R2
(coverage head 08dd9d2), and the repo body v2 file is synced to the
live R2 body + the R2 block. All figures re-derived from git, never
copied from the documents.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "08dd9d2184d961940a54ef58a139ea0eafa90432"
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

    chk("index header coverage head == 08dd9d2", "(head `08dd9d2`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("1934fad", "08dd9d2"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 195/2401", "**195 commit / 2401 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R3 note", "Cập nhật R3" in index)
    chk("index R2 row label", "PR119 BODY RESTRUCTURE R2" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..08dd9d2 == 195", n_commits == 195, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..08dd9d2 == 2401", n_files == 2401, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 224717, deletions 0",
        "224717 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    chk("merge-tree 08dd9d2 vs integration exit 0", mt.returncode == 0,
        mt.stdout.splitlines()[0] if mt.stdout else "")

    chk("body head line 08dd9d2/195/2401",
        "**Head: `08dd9d2` · 195 commit · 2401 file**" in body)
    chk("body has R2 paragraph", "- **PR119 BODY RESTRUCTURE R2**" in body)
    chk("body title mentions R2", "PR119 BODY RESTRUCTURE R2" in body)
    chk("body index reference at 08dd9d2", "(head `08dd9d2`)" in body)
    chk("body R3 note", "R3 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R3",
           "validator": "check_pr119_restructure_r3_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
