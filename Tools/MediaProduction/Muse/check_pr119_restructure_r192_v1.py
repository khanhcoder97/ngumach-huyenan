#!/usr/bin/env python3
"""R192 validator: PR #119 delivery index + body v2 coverage through 77e5df1.

Verifies the R192 restructure round: the delivery index now covers R191
(coverage head 77e5df1, full SHA 77e5df103eba26808b454f0553089f5c0ce417ec),
and the repo body v2 file is synced to the R190 body v2 file + the R191
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R191 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R191 and
R192 note lines are present in the index.
The compaction window extends in R192: the "Khối mới nhất" paragraphs
R114-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 52 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R114 paragraph (735 chars -> ~240) plus
trimming the new R191 paragraph to ~420 chars is what holds headroom
this round (R191 warning: headroom was 30 chars; the R191 payload body
ran 105,005 chars, 5 over the self-set ceiling, because the post-push
head-line refresh added ~35 chars). Body is now ~104,957 chars --
headroom ~43, and the R192 payload should stay at or under 105,000.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R191), with
the new paragraph after R190 and before the compact block.
The R192 payload should be ~122,500 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R188 row 2960 == 45142ad,
R189 row 2963 == ed21eb2, R190 row 2966 == d105f51 -- all verified from
git this round). The R191 row therefore cites 2969 paths: 2968 at
77e5df1 + 1 new checker file in the R192 content commit. That figure is
verified in the R192 report after the content commit, not by this
checker (it runs on the working tree before the commit exists).
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "77e5df103eba26808b454f0553089f5c0ce417ec"
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

    chk("index header coverage head == 77e5df1", "(head `77e5df1`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("d105f51", "77e5df1"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 573/2968", "**573 commit / 2968 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R192 note", "Cập nhật R192" in index)
    chk("index R191 note kept", "Cập nhật R191" in index)
    chk("index R191 row label", "PR119 BODY RESTRUCTURE R191" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..77e5df1 == 573", n_commits == 573, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..77e5df1 == 2968", n_files == 2968, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 279949, deletions 0",
        "279949 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 77e5df1 vs integration exit 0, tree 9d863db7",
        mt.returncode == 0 and tree.startswith("9d863db7"), tree)

    chk("body head line 77e5df1/573/2968",
        "**Head: `77e5df1` · 573 commit · 2968 file**" in body)
    chk("body has R191 paragraph", "- **PR119 BODY RESTRUCTURE R191**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R191",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R191" in title_line, title_line[-60:])
    chk("body title has full R93..R191 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 192)),
        "R94 restored, R191 added")
    chk("body index reference at 77e5df1", "(head `77e5df1`)" in body)

    # R192 note + compaction: 52 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R192 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(114, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R191 after R190, before the compact block.
    bl = body.splitlines()
    i191 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R191**"))
    i190 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R190**"))
    order_ok = i191 == i190 + 1
    chk("body R192 note + R114-R165 compacted (52 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 52 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R191",
           "validator": "check_pr119_restructure_r192_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
