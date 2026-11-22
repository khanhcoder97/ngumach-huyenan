#!/usr/bin/env python3
"""R197 validator: PR #119 delivery index + body v2 coverage through eb54d4d.

Verifies the R197 restructure round: the delivery index now covers R196
(coverage head eb54d4d, full SHA eb54d4d6b606ca55a80d41bd45e992c34a414225),
and the repo body v2 file is synced to the R195 body v2 file + the R196
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R196 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R196 and
R197 note lines are present in the index.
The compaction window extends in R197: the "Khối mới nhất" paragraphs
R109-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 57 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R109 paragraph (694 chars -> 239) plus
the new R196 paragraph at 396 chars is what holds headroom this round
(R196 warning: headroom was 117 chars; the R196 payload body ran
104,918 chars). Body is now 104,944 chars -- headroom 56, and the
R197 payload should stay at or under 105,000. R198 warning: headroom
is only 56 chars; the next round must collapse R108 (694 chars ->
~240) and keep the new paragraph tight.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R196), with
the new paragraph after R195 and before the compact block.
The R197 payload should be ~122,300 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R193 row 2975 == f2d3fae,
R194 row 2978 == 6b67985, R195 row 2981 == 218f0fa -- all verified from
git this round). The R196 row therefore cites 2984 paths: 2983 at
eb54d4d + 1 new checker file in the R197 content commit. That figure is
verified in the R197 report after the content commit, not by this
checker (it runs on the working tree before the commit exists).
R196 script-defect repairs (verified by this checker): the R196 edit
script dropped trailing "\\n" on whole-line replacements and inserts,
joining the 6 "Moc xac minh" bullets into one line, swallowing the
"## Ghi chu" heading into the R195 row, and gluing the trailing
duplicate R167 note onto the R196 note line. R197 repairs all three:
milestone bullets are 6 separate lines again, "## Ghi chu" is its own
line after the R196 row, and the R167 note is its own line in ascending
position (after R166, before R168).
Live-body read note: this round's first MCP pull read carried the
R175/R182-style read-path artifact (92,521 chars, sha ced29e00,
2 U+FFFD); the immediate re-read was byte-exact (92,520 chars, sha
ddbe32ff, 0 U+FFFD). Mergeable_state reads clean at the new head
eb54d4d (CI finished); the R196 payload's own head line had recorded
mergeable unstable at preparation time, when CI was still running on
the new head.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "eb54d4d6b606ca55a80d41bd45e992c34a414225"
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

    chk("index header coverage head == eb54d4d", "(head `eb54d4d`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("218f0fa", "eb54d4d"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 583/2983", "**583 commit / 2983 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R197 note", "Cập nhật R197" in index)
    chk("index R196 note kept", "Cập nhật R196" in index)
    chk("index R196 row label", "PR119 BODY RESTRUCTURE R196" in index)

    # R196 script-defect repairs: milestone 6 separate lines, heading own
    # line, R167 note own line in ascending position, R196 note clean.
    il = index.splitlines()
    milestone_ok = all(
        sum(1 for l in il if l.startswith(m)) == 1
        for m in ("- Head nhánh `muse/media-production-20261104`:",
                  "- Commit trên nhánh (diff từ merge-base `cf17178`):",
                  "- Integration: `f3db6b3`",
                  "- Mergeable: API trả mergeable_state",
                  "- Issue #116: 34 comment",
                  "- Scope audit"))
    heading_ok = sum(1 for l in il if l == "## Ghi chú") == 1
    r195_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R195 |")]
    r195_clean = len(r195_row) == 1 and "## Ghi chú" not in r195_row[0]
    r167_lines = [i for i, l in enumerate(il) if l.startswith("- Cập nhật R167 ")]
    r166_i = next((i for i, l in enumerate(il) if l.startswith("- Cập nhật R166 ")), -1)
    r168_i = next((i for i, l in enumerate(il) if l.startswith("- Cập nhật R168 ")), -1)
    r167_ok = len(r167_lines) == 1 and r166_i >= 0 and r167_lines[0] == r166_i + 1 and r168_i == r166_i + 2
    r196_note = [l for l in il if l.startswith("- Cập nhật R196 (2026-11-23):")]
    r196_note_ok = len(r196_note) == 1 and "- Cập nhật R167 " not in r196_note[0]
    repair_detail = (f"milestone6={milestone_ok} heading={heading_ok} "
                     f"r195clean={r195_clean} r167ascending={r167_ok} r196note={r196_note_ok}")
    chk("index R196-defect repairs (milestone 6 lines, heading, R167 ascending, R196 note)",
        milestone_ok and heading_ok and r195_clean and r167_ok and r196_note_ok,
        repair_detail)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..eb54d4d == 583", n_commits == 583, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..eb54d4d == 2983", n_files == 2983, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 282033, deletions 0",
        "282033 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree eb54d4d vs integration exit 0, tree 131a24b0",
        mt.returncode == 0 and tree.startswith("131a24b0"), tree)

    chk("body head line eb54d4d/583/2983",
        "**Head: `eb54d4d` · 583 commit · 2983 file**" in body)
    chk("body has R196 paragraph", "- **PR119 BODY RESTRUCTURE R196**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R196",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R196" in title_line, title_line[-60:])
    chk("body title has full R93..R196 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 197)),
        "R94 restored, R196 added")
    chk("body index reference at eb54d4d", "(head `eb54d4d`)" in body)

    # R197 note + compaction: 57 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R197 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(109, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R196 after R195, before the compact block.
    bl = body.splitlines()
    i196 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R196**"))
    i195 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R195**"))
    order_ok = i196 == i195 + 1
    chk("body R197 note + R109-R165 compacted (57 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 57 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R196",
           "validator": "check_pr119_restructure_r197_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
