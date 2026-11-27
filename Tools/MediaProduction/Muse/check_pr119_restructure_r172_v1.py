#!/usr/bin/env python3
"""R172 validator: PR #119 delivery index + body v2 coverage through a9e8475.

Verifies the R172 restructure round: the delivery index now covers R171
(coverage head a9e8475), and the repo body v2 file is synced to the
R170 body v2 file + the R171 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R171 run is present in the title line.
It also guards the R140 update-note defect (a content commit replaced the
previous "Cập nhật" note line instead of appending after it) by asserting
both the R171 and R172 note lines are present in the index.
The compaction window extends in R172: the "Khối mới nhất" paragraphs
R135-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 31 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R135 paragraph (857 chars -> 290) plus
trimming the new R171 paragraph to 743 chars is what keeps the body under
the ceiling this round (R171 warning: collapse R135 and keep the new
paragraph <= 750 chars). The full paragraphs in "Khối mới nhất" stay in
ascending order (R166..R171), with the new paragraph after R170 and
before the compact block.
The R172 payload should be ~123,500 bytes, well under the 131,072
transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "a9e8475ae3bc5c25d0204f7b36d054a2254f58ca"
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

    chk("index header coverage head == a9e8475", "(head `a9e8475`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("a3c4e6a", "a9e8475"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 533/2908", "**533 commit / 2908 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R172 note", "Cập nhật R172" in index)
    chk("index R171 note kept", "Cập nhật R171" in index)
    chk("index R171 row label", "PR119 BODY RESTRUCTURE R171" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..a9e8475 == 533", n_commits == 533, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..a9e8475 == 2908", n_files == 2908, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 272324, deletions 0",
        "272324 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree a9e8475 vs integration exit 0, tree eb841185",
        mt.returncode == 0 and tree.startswith("eb841185"), tree)

    chk("body head line a9e8475/533/2908",
        "**Head: `a9e8475` · 533 commit · 2908 file**" in body)
    chk("body has R171 paragraph", "- **PR119 BODY RESTRUCTURE R171**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R171",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R171" in title_line, title_line[-60:])
    chk("body title has full R93..R171 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 172)),
        "R94 restored, R171 added")
    chk("body index reference at a9e8475", "(head `a9e8475`)" in body)

    # R172 note + compaction: 31 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R172 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(135, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R171 after R170, before the compact block.
    bl = body.splitlines()
    i171 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R171**"))
    i170 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R170**"))
    order_ok = i171 == i170 + 1
    chk("body R172 note + R135-R165 compacted (31 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 31 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R171",
           "validator": "check_pr119_restructure_r172_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
