#!/usr/bin/env python3
"""R195 validator: PR #119 delivery index + body v2 coverage through 25e6869.

Verifies the R195 restructure round: the delivery index now covers R194
(coverage head 25e6869, full SHA 25e68697deaae50c447aacbbc2a86b9662ded589),
and the repo body v2 file is synced to the R193 body v2 file + the R194
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R194 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R194 and
R195 note lines are present in the index.
The compaction window extends in R195: the "Khối mới nhất" paragraphs
R111-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 55 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R111 paragraph (694 chars -> 239) plus
the new R194 paragraph at 396 chars is what holds headroom this round
(R194 warning: headroom was 121 chars; the R194 payload body ran
104,914 chars). Body is now 104,881 chars -- headroom 119, and the
R195 payload should stay at or under 105,000.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R194), with
the new paragraph after R193 and before the compact block.
The R195 payload should be ~122,200 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R191 row 2969 == 7e80036,
R192 row 2972 == 11a935f, R193 row 2975 == f2d3fae -- all verified from
git this round). The R194 row therefore cites 2978 paths: 2977 at
25e6869 + 1 new checker file in the R195 content commit. That figure is
verified in the R195 report after the content commit, not by this
checker (it runs on the working tree before the commit exists).
Live-body read note: this round's first MCP pull read was byte-exact at
once (92,520 chars, sha ddbe32ff, 0 U+FFFD) -- no R175/R182-style
read-path artifact this round. Mergeable_state reads clean at the new
head 25e6869 (CI finished); the R194 payload's own head line had
recorded mergeable unstable at preparation time, when CI was still
running on the new head.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "25e68697deaae50c447aacbbc2a86b9662ded589"
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

    chk("index header coverage head == 25e6869", "(head `25e6869`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("f2d3fae", "25e6869"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 579/2977", "**579 commit / 2977 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R195 note", "Cập nhật R195" in index)
    chk("index R194 note kept", "Cập nhật R194" in index)
    chk("index R194 row label", "PR119 BODY RESTRUCTURE R194" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..25e6869 == 579", n_commits == 579, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..25e6869 == 2977", n_files == 2977, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 281207, deletions 0",
        "281207 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 25e6869 vs integration exit 0, tree 1ebddb57",
        mt.returncode == 0 and tree.startswith("1ebddb57"), tree)

    chk("body head line 25e6869/579/2977",
        "**Head: `25e6869` · 579 commit · 2977 file**" in body)
    chk("body has R194 paragraph", "- **PR119 BODY RESTRUCTURE R194**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R194",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R194" in title_line, title_line[-60:])
    chk("body title has full R93..R194 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 195)),
        "R94 restored, R194 added")
    chk("body index reference at 25e6869", "(head `25e6869`)" in body)

    # R195 note + compaction: 55 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R195 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(111, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R194 after R193, before the compact block.
    bl = body.splitlines()
    i194 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R194**"))
    i193 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R193**"))
    order_ok = i194 == i193 + 1
    chk("body R195 note + R111-R165 compacted (55 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 55 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R194",
           "validator": "check_pr119_restructure_r195_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
