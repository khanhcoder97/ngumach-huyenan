#!/usr/bin/env python3
"""R194 validator: PR #119 delivery index + body v2 coverage through 6dd9d03.

Verifies the R194 restructure round: the delivery index now covers R193
(coverage head 6dd9d03, full SHA 6dd9d034e1ecceb29114e9e04b45ce1e6bc55f69),
and the repo body v2 file is synced to the R192 body v2 file + the R193
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R193 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R193 and
R194 note lines are present in the index.
The compaction window extends in R194: the "Khối mới nhất" paragraphs
R112-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 54 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R112 paragraph (735 chars -> 239) plus
the new R193 paragraph at 396 chars is what holds headroom this round
(R193 warning: headroom was 41 chars; the R193 payload body ran
104,953 chars). Body is now 104,879 chars -- headroom 121, and the
R194 payload should stay at or under 105,000.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R193), with
the new paragraph after R192 and before the compact block.
The R194 payload should be ~122,200 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R190 row 2966 == d105f51,
R191 row 2969 == 7e80036, R192 row 2972 == 11a935f -- all verified from
git this round). The R193 row therefore cites 2975 paths: 2974 at
6dd9d03 + 1 new checker file in the R194 content commit. That figure is
verified in the R194 report after the content commit, not by this
checker (it runs on the working tree before the commit exists).
Live-body read note: this round's first MCP pull read was byte-exact at
once (92,520 chars, sha ddbe32ff, 0 U+FFFD) -- no R175/R182-style
read-path artifact this round.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "6dd9d034e1ecceb29114e9e04b45ce1e6bc55f69"
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

    chk("index header coverage head == 6dd9d03", "(head `6dd9d03`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("11a935f", "6dd9d03"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 577/2974", "**577 commit / 2974 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R194 note", "Cập nhật R194" in index)
    chk("index R193 note kept", "Cập nhật R193" in index)
    chk("index R193 row label", "PR119 BODY RESTRUCTURE R193" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..6dd9d03 == 577", n_commits == 577, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..6dd9d03 == 2974", n_files == 2974, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 280786, deletions 0",
        "280786 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 6dd9d03 vs integration exit 0, tree 689237bd",
        mt.returncode == 0 and tree.startswith("689237bd"), tree)

    chk("body head line 6dd9d03/577/2974",
        "**Head: `6dd9d03` · 577 commit · 2974 file**" in body)
    chk("body has R193 paragraph", "- **PR119 BODY RESTRUCTURE R193**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R193",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R193" in title_line, title_line[-60:])
    chk("body title has full R93..R193 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 194)),
        "R94 restored, R193 added")
    chk("body index reference at 6dd9d03", "(head `6dd9d03`)" in body)

    # R194 note + compaction: 54 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R194 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(112, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R193 after R192, before the compact block.
    bl = body.splitlines()
    i193 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R193**"))
    i192 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R192**"))
    order_ok = i193 == i192 + 1
    chk("body R194 note + R112-R165 compacted (54 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 54 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R193",
           "validator": "check_pr119_restructure_r194_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
