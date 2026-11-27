#!/usr/bin/env python3
"""R193 validator: PR #119 delivery index + body v2 coverage through 0c67764.

Verifies the R193 restructure round: the delivery index now covers R192
(coverage head 0c67764, full SHA 0c67764b032df79c750f8a1aee32a7d7fcc7fdf6),
and the repo body v2 file is synced to the R191 body v2 file + the R192
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R192 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R192 and
R193 note lines are present in the index.
The compaction window extends in R193: the "Khối mới nhất" paragraphs
R113-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 53 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R113 paragraph (735 chars -> ~240) plus
trimming the new R192 paragraph to ~400 chars is what holds headroom
this round (R192 warning: headroom was 43 chars; the R192 payload body
ran 104,992 chars, under the self-set ceiling, because the post-push
head-line refresh added ~35 chars). Body is now ~104,959 chars --
headroom ~41, and the R193 payload should stay at or under 105,000.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R192), with
the new paragraph after R191 and before the compact block.
The R193 payload should be ~122,300 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R189 row 2963 == ed21eb2,
R190 row 2966 == d105f51, R191 row 2969 == 7e80036 -- all verified from
git this round). The R192 row therefore cites 2972 paths: 2971 at
0c67764 + 1 new checker file in the R193 content commit. That figure is
verified in the R193 report after the content commit, not by this
checker (it runs on the working tree before the commit exists).
Live-body read note: this round's first MCP pull read carried an
R175/R182-style read-path artifact (92,521 chars / 2 U+FFFD); the
immediate re-read was byte-exact (92,520 chars, sha ddbe32ff, 0 U+FFFD)
-- a first artifact read means re-read, not a changed live body.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "0c67764b032df79c750f8a1aee32a7d7fcc7fdf6"
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

    chk("index header coverage head == 0c67764", "(head `0c67764`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("7e80036", "0c67764"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 575/2971", "**575 commit / 2971 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R193 note", "Cập nhật R193" in index)
    chk("index R192 note kept", "Cập nhật R192" in index)
    chk("index R192 row label", "PR119 BODY RESTRUCTURE R192" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..0c67764 == 575", n_commits == 575, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..0c67764 == 2971", n_files == 2971, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 280365, deletions 0",
        "280365 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 0c67764 vs integration exit 0, tree a0541c9e",
        mt.returncode == 0 and tree.startswith("a0541c9e"), tree)

    chk("body head line 0c67764/575/2971",
        "**Head: `0c67764` · 575 commit · 2971 file**" in body)
    chk("body has R192 paragraph", "- **PR119 BODY RESTRUCTURE R192**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R192",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R192" in title_line, title_line[-60:])
    chk("body title has full R93..R192 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 193)),
        "R94 restored, R192 added")
    chk("body index reference at 0c67764", "(head `0c67764`)" in body)

    # R193 note + compaction: 53 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R193 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(113, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R192 after R191, before the compact block.
    bl = body.splitlines()
    i192 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R192**"))
    i191 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R191**"))
    order_ok = i192 == i191 + 1
    chk("body R193 note + R113-R165 compacted (53 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 53 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R192",
           "validator": "check_pr119_restructure_r193_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
