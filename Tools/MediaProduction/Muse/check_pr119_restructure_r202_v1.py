#!/usr/bin/env python3
"""R202 validator: PR #119 delivery index + body v2 coverage through 003f1bb.

Verifies the R202 restructure round: the delivery index now covers R201
(coverage head 003f1bb, full SHA 003f1bb22e3bd70e93177cf83e5b603a42df7f83),
and the repo body v2 file is synced to the R200 body v2 file + the R201
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R201 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R201 and
R202 note lines are present in the index.
The compaction window extends in R202: the "Khối mới nhất" paragraphs
R104-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 62 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R104 paragraph (694 chars -> 239) plus
the new R201 paragraph at 369 chars is what holds headroom this round
(R201 warning: headroom was 121 chars; the R201 payload body ran
104,858 chars). Body is now 104,854 chars -- headroom 146, and the
R202 payload should stay at or under 105,000. R203 warning: headroom
is 146 chars; the next round must collapse R103 (694 chars ->
~240) and keep the new paragraph tight.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R201), with
the new paragraph after R200 and before the compact block.
The R202 payload should be ~121,800 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R198 row 2990 == 4513812,
R199 row 2993 == 01dd796, R200 row 2996 == 409c2f2 -- all re-derived from
git by THIS checker). The R201 row therefore cites 2999 paths: 2998 at
003f1bb + 1 new checker file in the R202 content commit. That figure is
verified in the R202 report after the content commit, not by this
checker (it runs on the working tree before the commit exists).
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
Live-body read note: this round the GitHub MCP read path WORKED
(call-read-tool, no stall): issue #116 read ~16:45 JST still 34
comments (30 + 4 paginated), latest ACK 6862732081, no new direction
since Gói 39; PR #119 read ~16:45 JST: head 003f1bb, 593 commits /
2998 files / +284,536, mergeable_state clean at 003f1bb; live body
still R140 (title ends "+ R140", head inside the description 78ccd85 ·
471 · 2815, body 92,520 chars, sha ddbe32ff, 0 U+FFFD, updated_at
2026-11-23T06:46:04Z -- bumped by the R201 push updating the PR head,
body bytes unchanged).
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "003f1bb22e3bd70e93177cf83e5b603a42df7f83"
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

    chk("index header coverage head == 003f1bb", "(head `003f1bb`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("409c2f2", "003f1bb"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 593/2998", "**593 commit / 2998 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R202 note", "Cập nhật R202" in index)
    chk("index R201 note kept", "Cập nhật R201" in index)
    chk("index R201 row label", "PR119 BODY RESTRUCTURE R201" in index)

    # R196 script-defect repairs, kept as regression guards: milestone 6
    # separate lines, heading own line, R167 note own line in ascending
    # position, R201 note clean.
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
    r201_note = [l for l in il if l.startswith("- Cập nhật R201 (2026-11-23):")]
    r201_note_ok = len(r201_note) == 1 and "- Cập nhật R167 " not in r201_note[0]
    repair_detail = (f"milestone6={milestone_ok} heading={heading_ok} "
                     f"r196clean={r196_clean} r167ascending={r167_ok} r201note={r201_note_ok}")
    chk("index R196-defect repairs (milestone 6 lines, heading, R167 ascending, R201 note)",
        milestone_ok and heading_ok and r196_clean and r167_ok and r201_note_ok,
        repair_detail)

    # R198 .bak correction: the R198 row must carry the ĐÍNH CHÍNH R200 note.
    r198_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R198 |")]
    bak_ok = (len(r198_row) == 1 and "ĐÍNH CHÍNH R200" in r198_row[0]
              and "KHÔNG tồn tại trên đĩa khi R199 kiểm tra" in r198_row[0])
    chk("index R198 row carries ĐÍNH CHÍNH R200 (.bak claim corrected)", bak_ok)

    # Row-convention verification, re-derived from git: a row's cumulative
    # N paths is the diff path count at the AUTHORING round's content commit.
    for row_n, content_sha, expected in (("R198", "4513812", 2990),
                                         ("R199", "01dd796", 2993),
                                         ("R200", "409c2f2", 2996)):
        n = len(git("diff", "--name-only", BASE, content_sha).splitlines())
        chk(f"row-convention {row_n} cumulative {expected} == diff at {content_sha}",
            n == expected, str(n))

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..003f1bb == 593", n_commits == 593, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..003f1bb == 2998", n_files == 2998, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 284536, deletions 0",
        "284536 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 003f1bb vs integration exit 0, tree c89b0ff4",
        mt.returncode == 0 and tree.startswith("c89b0ff4"), tree)

    chk("body head line 003f1bb/593/2998",
        "**Head: `003f1bb` · 593 commit · 2998 file**" in body)
    chk("body has R201 paragraph", "- **PR119 BODY RESTRUCTURE R201**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R201",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R201" in title_line, title_line[-60:])
    chk("body title has full R93..R201 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 202)),
        "R94 restored, R201 added")
    chk("body index reference at 003f1bb", "(head `003f1bb`)" in body)

    # R202 note + compaction: 62 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R202 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(104, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R201 after R200, before the compact block.
    bl = body.splitlines()
    i201 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R201**"))
    i200 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R200**"))
    order_ok = i201 == i200 + 1
    chk("body R202 note + R104-R165 compacted (62 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 62 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R201",
           "validator": "check_pr119_restructure_r202_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
