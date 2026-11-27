#!/usr/bin/env python3
"""R157 validator: PR #119 delivery index + body v2 coverage through 228440e.

Verifies the R157 restructure round: the delivery index now covers R156
(coverage head 228440e), and the repo body v2 file is synced to the
R156 body v2 file + the R156 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R156 run is present in the title line.
It also guards the R140 update-note defect (a content commit replaced the
previous "Cập nhật" note line instead of appending after it) by asserting
both the R156 and R157 note lines are present in the index.
Ceiling note: the R156 body paragraph is intentionally compact (762 chars)
because the R156 payload JSON reached 129,955 bytes vs the 131,072
transport ceiling; the checker does not assert paragraph length.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "228440e36d96a2e201394107b6238aeb14786c00"
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

    chk("index header coverage head == 228440e", "(head `228440e`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("a36d89a", "228440e"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 503/2863", "**503 commit / 2863 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R157 note", "Cập nhật R157" in index)
    chk("index R156 note kept", "Cập nhật R156" in index)
    chk("index R156 row label", "PR119 BODY RESTRUCTURE R156" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..228440e == 503", n_commits == 503, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..228440e == 2863", n_files == 2863, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 266947, deletions 0",
        "266947 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 228440e vs integration exit 0, tree 92d59c16",
        mt.returncode == 0 and tree.startswith("92d59c16"), tree)

    chk("body head line 228440e/503/2863",
        "**Head: `228440e` · 503 commit · 2863 file**" in body)
    chk("body has R156 paragraph", "- **PR119 BODY RESTRUCTURE R156**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R156",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R156" in title_line, title_line[-60:])
    chk("body title has full R93..R156 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 157)),
        "R94 restored, R156 added")
    chk("body index reference at 228440e", "(head `228440e`)" in body)
    chk("body R157 note", "R157 (lượt cập nhật này)" in body)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R156",
           "validator": "check_pr119_restructure_r157_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
