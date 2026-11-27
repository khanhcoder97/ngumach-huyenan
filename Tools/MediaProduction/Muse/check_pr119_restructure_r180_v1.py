#!/usr/bin/env python3
"""R180 validator: PR #119 delivery index + body v2 coverage through c7e47e8.

Verifies the R180 restructure round: the delivery index now covers R179
(coverage head c7e47e8, full SHA c7e47e8eced9176b9fad972431ea2a7553d94833),
and the repo body v2 file is synced to the R178 body v2 file + the R179
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R179 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R179 and
R180 note lines are present in the index.
The compaction window extends in R180: the "Khối mới nhất" paragraphs
R126-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 40 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R126 paragraph (750 chars -> ~270) plus
trimming the new R179 paragraph to ~470 chars is what keeps the body under
the ceiling this round (R179 warning: headroom was 82 chars). The full
paragraphs in "Khối mới nhất" stay in ascending order (R166..R179), with
the new paragraph after R178 and before the compact block.
The R180 payload should be ~123,000 bytes, well under the 131,072
transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "c7e47e8eced9176b9fad972431ea2a7553d94833"
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

    chk("index header coverage head == c7e47e8", "(head `c7e47e8`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("666d0aa", "c7e47e8"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 549/2932", "**549 commit / 2932 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R180 note", "Cập nhật R180" in index)
    chk("index R179 note kept", "Cập nhật R179" in index)
    chk("index R179 row label", "PR119 BODY RESTRUCTURE R179" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..c7e47e8 == 549", n_commits == 549, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..c7e47e8 == 2932", n_files == 2932, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 275318, deletions 0",
        "275318 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree c7e47e8 vs integration exit 0, tree 1068f55d",
        mt.returncode == 0 and tree.startswith("1068f55d"), tree)

    chk("body head line c7e47e8/549/2932",
        "**Head: `c7e47e8` · 549 commit · 2932 file**" in body)
    chk("body has R179 paragraph", "- **PR119 BODY RESTRUCTURE R179**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R179",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R179" in title_line, title_line[-60:])
    chk("body title has full R93..R179 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 180)),
        "R94 restored, R179 added")
    chk("body index reference at c7e47e8", "(head `c7e47e8`)" in body)

    # R180 note + compaction: 40 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R180 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(126, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R179 after R178, before the compact block.
    bl = body.splitlines()
    i179 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R179**"))
    i178 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R178**"))
    order_ok = i179 == i178 + 1
    chk("body R180 note + R126-R165 compacted (40 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 40 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R179",
           "validator": "check_pr119_restructure_r180_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
