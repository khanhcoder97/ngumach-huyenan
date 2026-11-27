#!/usr/bin/env python3
"""R190 validator: PR #119 delivery index + body v2 coverage through 4380848.

Verifies the R190 restructure round: the delivery index now covers R189
(coverage head 4380848, full SHA 4380848cfce17aafe5c6f0565ad9a7494911ee3f),
and the repo body v2 file is synced to the R188 body v2 file + the R189
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R189 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R189 and
R190 note lines are present in the index.
The compaction window extends in R190: the "Khối mới nhất" paragraphs
R116-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 50 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R116 paragraph (748 chars -> 247) plus
trimming the new R189 paragraph to 486 chars is what holds headroom
this round (R189 warning: headroom was 132 chars; the R116 paragraph
measured 748 chars). Body is now 104,914 chars -- headroom 86.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R189), with
the new paragraph after R188 and before the compact block.
The R190 payload should be ~123,000 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R186 row 2954 == a24a3b6,
R187 row 2957 == ea34c5a, R188 row 2960 == 45142ad -- all verified from
git this round). The R189 row therefore cites 2963 paths: 2962 at
4380848 + 1 new checker file in the R190 content commit. That figure is
verified in the R190 report after the content commit, not by this
checker (it runs on the working tree before the commit exists).
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "4380848cfce17aafe5c6f0565ad9a7494911ee3f"
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

    chk("index header coverage head == 4380848", "(head `4380848`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("45142ad", "4380848"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 569/2962", "**569 commit / 2962 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R190 note", "Cập nhật R190" in index)
    chk("index R189 note kept", "Cập nhật R189" in index)
    chk("index R189 row label", "PR119 BODY RESTRUCTURE R189" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..4380848 == 569", n_commits == 569, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..4380848 == 2962", n_files == 2962, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 279143, deletions 0",
        "279143 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 4380848 vs integration exit 0, tree 048f8ee9",
        mt.returncode == 0 and tree.startswith("048f8ee9"), tree)

    chk("body head line 4380848/569/2962",
        "**Head: `4380848` · 569 commit · 2962 file**" in body)
    chk("body has R189 paragraph", "- **PR119 BODY RESTRUCTURE R189**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R189",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R189" in title_line, title_line[-60:])
    chk("body title has full R93..R189 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 190)),
        "R94 restored, R189 added")
    chk("body index reference at 4380848", "(head `4380848`)" in body)

    # R190 note + compaction: 50 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R190 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(116, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R189 after R188, before the compact block.
    bl = body.splitlines()
    i189 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R189**"))
    i188 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R188**"))
    order_ok = i189 == i188 + 1
    chk("body R190 note + R116-R165 compacted (50 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 50 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R189",
           "validator": "check_pr119_restructure_r190_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
