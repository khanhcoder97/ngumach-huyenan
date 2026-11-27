#!/usr/bin/env python3
"""R206 validator: PR #119 delivery index + body v2 coverage through c31c7ec.

Verifies the R206 restructure round: the delivery index now covers R205
(coverage head c31c7ec, full SHA c31c7ec1b8b9a805829d1c00b38224fe615e410b),
and the repo body v2 file is synced to the R204 body v2 file + the R205
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R205 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R205 and
R206 note lines are present in the index.
The compaction window extends in R206: the "Khối mới nhất" paragraphs
R100-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 66 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R100 paragraph (594 chars -> 253) plus
the new R205 paragraph at 350 chars is what holds headroom this round
(R205 warning: headroom was 94 chars; the R205 payload body ran
104,846 chars; this round's body is 104,927 chars, headroom 73).
R207 warning: headroom after R206 is 73 chars; the next round must
collapse R99 (570 chars -> ~240) and keep the new paragraph tight.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R205), with
the new paragraph after R204 and before the compact block.
The R206 payload should be ~121,500 bytes, well under the 131,072
transport ceiling.
ĐÍNH CHÍNH R205 (carried into the R206 report): the R100 paragraph
measures 594 chars, NOT the 616 the R205 report stated in its R206
warning -- the compaction still frees ~341 chars, the warning's
substance is unchanged.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R201 row 2999 == e50ba30,
R202 row 3002 == 549b8b0, R203 row 3005 == 818f027, R204 row 3008 ==
df30756 -- all re-derived from git by THIS checker). The R205 row
therefore cites 3009 paths: 3008 at df30756 + 1 new checker file in the
R206 content commit. That figure is verified in the R206 report after
the content commit, not by this checker (it runs on the working tree
before the commit exists).
R198 .bak correction (kept as a regression guard): the R198 index
row carries the ĐÍNH CHÍNH R200 note (the `.bak-prepost-20261123`
directory did NOT exist on disk when R199 checked; R199 created it).
The same unverifiable claim also appears in rows R137-R197; those
historical rows are left as-is (disclosed in the R200 report), only the
R198 row (the round folded in at R200) is corrected.
R196 script-defect repairs (kept as regression guards by this checker):
the R196 edit script dropped trailing "\\n" on whole-line replacements
and inserts, joining the 6 "Moc xac minh" bullets into one line,
swallowing the "## Ghi chu" heading into the R195 row, and gluing the
trailing duplicate R167 note onto the R196 note line. R197 repaired all
three: milestone bullets are 6 separate lines again, "## Ghi chu" is its
own line after the R196 row, and the R167 note is its own line in
ascending position (after R166, before R168).
R206 script-defect repair (new regression guard in the edit script):
the R206 edit script's idempotency re-run initially crashed on its
OLD-state pre-condition asserts (the index header replace looked for the
old head line after a successful apply); fixed this round by checking
the NEW state first (re-run reports already-applied changed: 0, verified).
Live-body read note: this round the GitHub API was read via the MCP
read path (~20:41 JST, read-only, no stall this round): issue #116 still
34 comments (30 + 4 paginated), latest ACK 6862732081, no new direction
since Gói 39; PR #119 read ~20:41 JST: head c31c7ec, 601 commits / 3010
files / +286,620, mergeable_state clean at c31c7ec (the `mergeable` field
itself returned null at read time -- mergeable_state is the operative
field); live body still R140 (title ends "+ R140", head inside the
description 78ccd85 · 471 · 2815, body 92,520 chars, sha ddbe32ff,
0 U+FFFD, updated_at 2026-11-23T10:47:02Z -- bumped by the R205 push
updating the PR head, body bytes unchanged). The .bak directory lives at
pr_comments/.bak-prepost-20261123 (NOT directly under godot-prototype).
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "c31c7ec1b8b9a805829d1c00b38224fe615e410b"
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

    chk("index header coverage head == c31c7ec", "(head `c31c7ec`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("df30756", "c31c7ec"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 601/3010", "**601 commit / 3010 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R206 note", "Cập nhật R206" in index)
    chk("index R205 note kept", "Cập nhật R205" in index)
    chk("index R205 row label", "PR119 BODY RESTRUCTURE R205" in index)

    # R196 script-defect repairs, kept as regression guards: milestone 6
    # separate lines, heading own line, R167 note own line in ascending
    # position, R205 note clean.
    il = index.splitlines()
    milestone_ok = all(
        sum(1 for l in il if l.startswith(m)) == 1
        for m in ("- Head nhánh `muse/media-production-20261104`:",
                  "- Commit trên nhánh (diff từ merge-base `cf17178`):",
                  "- Integration: `f3db6b3`",
                  "- Mergeable:",
                  "- Issue #116: 34 comment",
                  "- Scope audit"))
    heading_ok = sum(1 for l in il if l == "## Ghi chú") == 1
    r196_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R196 |")]
    r196_clean = len(r196_row) == 1 and "## Ghi chú" not in r196_row[0]
    r167_lines = [i for i, l in enumerate(il) if l.startswith("- Cập nhật R167 ")]
    r166_i = next((i for i, l in enumerate(il) if l.startswith("- Cập nhật R166 ")), -1)
    r168_i = next((i for i, l in enumerate(il) if l.startswith("- Cập nhật R168 ")), -1)
    r167_ok = len(r167_lines) == 1 and r166_i >= 0 and r167_lines[0] == r166_i + 1 and r168_i == r166_i + 2
    r205_note = [l for l in il if l.startswith("- Cập nhật R205 (2026-11-23):")]
    r205_note_ok = len(r205_note) == 1 and "- Cập nhật R167 " not in r205_note[0]
    repair_detail = (f"milestone6={milestone_ok} heading={heading_ok} "
                     f"r196clean={r196_clean} r167ascending={r167_ok} r205note={r205_note_ok}")
    chk("index R196-defect repairs (milestone 6 lines, heading, R167 ascending, R205 note)",
        milestone_ok and heading_ok and r196_clean and r167_ok and r205_note_ok,
        repair_detail)

    # R198 .bak correction: the R198 row must carry the ĐÍNH CHÍNH R200 note.
    r198_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R198 |")]
    bak_ok = (len(r198_row) == 1 and "ĐÍNH CHÍNH R200" in r198_row[0]
              and "KHÔNG tồn tại trên đĩa khi R199 kiểm tra" in r198_row[0])
    chk("index R198 row carries ĐÍNH CHÍNH R200 (.bak claim corrected)", bak_ok)

    # Row-convention verification, re-derived from git: a row's cumulative
    # N paths is the diff path count at the AUTHORING round's content commit.
    for row_n, content_sha, expected in (("R201", "e50ba30", 2999),
                                         ("R202", "549b8b0", 3002),
                                         ("R203", "818f027", 3005),
                                         ("R204", "df30756", 3008)):
        n = len(git("diff", "--name-only", BASE, content_sha).splitlines())
        chk(f"row-convention {row_n} cumulative {expected} == diff at {content_sha}",
            n == expected, str(n))

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..c31c7ec == 601", n_commits == 601, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..c31c7ec == 3010", n_files == 3010, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 286620, deletions 0",
        "286620 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree c31c7ec vs integration exit 0, tree 25e23198",
        mt.returncode == 0 and tree.startswith("25e23198"), tree)

    chk("body head line c31c7ec/601/3010",
        "**Head: `c31c7ec` · 601 commit · 3010 file**" in body)
    chk("body has R205 paragraph", "- **PR119 BODY RESTRUCTURE R205**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R205",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R205" in title_line, title_line[-60:])
    chk("body title has full R93..R205 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 206)),
        "R94 restored, R205 added")
    chk("body index reference at c31c7ec", "(head `c31c7ec`)" in body)

    # R206 note + compaction: 66 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R206 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(100, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R205 after R204, before the compact block.
    bl = body.splitlines()
    i205 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R205**"))
    i204 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R204**"))
    order_ok = i205 == i204 + 1
    chk("body R206 note + R100-R165 compacted (66 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 66 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R205",
           "validator": "check_pr119_restructure_r206_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
