#!/usr/bin/env python3
"""R165 validator: PR #119 delivery index + body v2 coverage through 878815d.

Verifies the R165 restructure round: the delivery index now covers R164
(coverage head 878815d), and the repo body v2 file is synced to the
R163 body v2 file + the R164 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R164 run is present in the title line.
It also guards the R140 update-note defect (a content commit replaced the
previous "Cập nhật" note line instead of appending after it) by asserting
both the R164 and R165 note lines are present in the index.
The compaction window extends in R165: the "Khối mới nhất" paragraphs
R142-R163 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 22 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Compacting R162 alone would have left the body at ~105,181
chars, so R163 is compacted too this round (R164 precedent: second
compaction required, not optional). The R165 payload should be ~123,500
bytes, well under the 131,072 transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "878815dbf0d3d940205181bb3ad7cae947e0d8db"
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

    chk("index header coverage head == 878815d", "(head `878815d`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("759833f", "878815d"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 519/2887", "**519 commit / 2887 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R165 note", "Cập nhật R165" in index)
    chk("index R164 note kept", "Cập nhật R164" in index)
    chk("index R164 row label", "PR119 BODY RESTRUCTURE R164" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..878815d == 519", n_commits == 519, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..878815d == 2887", n_files == 2887, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 269802, deletions 0",
        "269802 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 878815d vs integration exit 0, tree 2b2f7bca",
        mt.returncode == 0 and tree.startswith("2b2f7bca"), tree)

    chk("body head line 878815d/519/2887",
        "**Head: `878815d` · 519 commit · 2887 file**" in body)
    chk("body has R164 paragraph", "- **PR119 BODY RESTRUCTURE R164**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R164",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R164" in title_line, title_line[-60:])
    chk("body title has full R93..R164 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 165)),
        "R94 restored, R164 added")
    chk("body index reference at 878815d", "(head `878815d`)" in body)

    # R165 note + compaction: 22 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R165 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(142, 164):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    chk("body R165 note + R142-R163 compacted (22 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 22 and per_round_ok
        and len(body) < 105000, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R164",
           "validator": "check_pr119_restructure_r165_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
