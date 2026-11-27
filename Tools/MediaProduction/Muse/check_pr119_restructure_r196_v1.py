#!/usr/bin/env python3
"""R196 validator: PR #119 delivery index + body v2 coverage through bf5c258.

Verifies the R196 restructure round: the delivery index now covers R195
(coverage head bf5c258, full SHA bf5c2587accce92fe67618c5070134556a91ed34),
and the repo body v2 file is synced to the R194 body v2 file + the R195
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R195 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R195 and
R196 note lines are present in the index.
The compaction window extends in R196: the "Khối mới nhất" paragraphs
R110-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 56 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R110 paragraph (694 chars -> 239) plus
the new R195 paragraph at 396 chars is what holds headroom this round
(R195 warning: headroom was 119 chars; the R195 payload body ran
104,916 chars). Body is now 104,883 chars -- headroom 117, and the
R196 payload should stay at or under 105,000.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R195), with
the new paragraph after R194 and before the compact block.
The R196 payload should be ~122,200 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R192 row 2972 == 11a935f,
R193 row 2975 == f2d3fae, R194 row 2978 == 6b67985 -- all verified from
git this round). The R195 row therefore cites 2981 paths: 2980 at
bf5c258 + 1 new checker file in the R196 content commit. That figure is
verified in the R196 report after the content commit, not by this
checker (it runs on the working tree before the commit exists).
Live-body read note: this round's first MCP pull read was byte-exact at
once (92,520 chars, sha ddbe32ff, 0 U+FFFD) -- no R175/R182-style
read-path artifact this round. Mergeable_state reads clean at the new
head bf5c258 (CI finished); the R195 payload's own head line had
recorded mergeable unstable at preparation time, when CI was still
running on the new head.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "bf5c2587accce92fe67618c5070134556a91ed34"
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

    chk("index header coverage head == bf5c258", "(head `bf5c258`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("6b67985", "bf5c258"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 581/2980", "**581 commit / 2980 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R196 note", "Cập nhật R196" in index)
    chk("index R195 note kept", "Cập nhật R195" in index)
    chk("index R195 row label", "PR119 BODY RESTRUCTURE R195" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..bf5c258 == 581", n_commits == 581, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..bf5c258 == 2980", n_files == 2980, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 281623, deletions 0",
        "281623 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree bf5c258 vs integration exit 0, tree de530277",
        mt.returncode == 0 and tree.startswith("de530277"), tree)

    chk("body head line bf5c258/581/2980",
        "**Head: `bf5c258` · 581 commit · 2980 file**" in body)
    chk("body has R195 paragraph", "- **PR119 BODY RESTRUCTURE R195**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R195",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R195" in title_line, title_line[-60:])
    chk("body title has full R93..R195 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 196)),
        "R94 restored, R195 added")
    chk("body index reference at bf5c258", "(head `bf5c258`)" in body)

    # R196 note + compaction: 56 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R196 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(110, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R195 after R194, before the compact block.
    bl = body.splitlines()
    i195 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R195**"))
    i194 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R194**"))
    order_ok = i195 == i194 + 1
    chk("body R196 note + R110-R165 compacted (56 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 56 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R195",
           "validator": "check_pr119_restructure_r196_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
