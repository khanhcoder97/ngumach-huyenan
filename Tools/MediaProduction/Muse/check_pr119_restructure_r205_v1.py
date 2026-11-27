#!/usr/bin/env python3
"""R205 validator: PR #119 delivery index + body v2 coverage through 2be4074.

Verifies the R205 restructure round: the delivery index now covers R204
(coverage head 2be4074, full SHA 2be4074e781d6894bfcf440ede39e2bd09d194ab),
and the repo body v2 file is synced to the R203 body v2 file + the R204
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R204 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R204 and
R205 note lines are present in the index.
The compaction window extends in R205: the "Khối mới nhất" paragraphs
R101-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 65 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R101 paragraph (616 chars -> 239) plus
the new R204 paragraph at 388 chars is what holds headroom this round
(R204 warning: headroom was 162 chars; the R204 payload body ran
104,890 chars). R206 warning: headroom after R205 is 94 chars; the
next round must collapse R100 (616 chars -> ~240) and keep the new
paragraph tight.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R204), with
the new paragraph after R203 and before the compact block.
The R205 payload should be ~121,500 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R201 row 2999 == e50ba30,
R202 row 3002 == 549b8b0, R203 row 3005 == 818f027 -- all re-derived from
git by THIS checker). The R204 row therefore cites 3008 paths: 3007 at
2be4074 + 1 new checker file in the R205 content commit. That figure is
verified in the R205 report after the content commit, not by this
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
R205 script-defect repair (new regression guard in the edit script):
the R205 edit script's idempotency re-run crashed on its OLD-state
pre-condition asserts for the mergeable line, head line, and "Ghi chú"
line after a successful apply; fixed this round by accepting the NEW
state as well (re-run reports already-applied changed: 0, verified).
Live-body read note: this round the GitHub API was read via a browser
task (~19:42 JST, read-only): issue #116 still 34 comments (30 + 4
paginated), latest ACK 6862732081, no new direction since Gói 39; PR
#119 read ~19:42 JST: head 2be4074, 599 commits / 3007 files /
+286,093, mergeable true, mergeable_state clean at 2be4074; live body
still R140 (title ends "+ R140", head inside the description 78ccd85 ·
471 · 2815, body 92,520 chars, sha ddbe32ff, 0 U+FFFD, updated_at
2026-11-23T09:44:31Z -- bumped by the R204 push updating the PR head,
body bytes unchanged). The .bak directory lives at
pr_comments/.bak-prepost-20261123 (NOT directly under godot-prototype);
R203 and R204 payloads verified byte-identical there this round
(sha256 ad64c9ec / bce286af).
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "2be4074e781d6894bfcf440ede39e2bd09d194ab"
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

    chk("index header coverage head == 2be4074", "(head `2be4074`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("818f027", "2be4074"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 599/3007", "**599 commit / 3007 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R205 note", "Cập nhật R205" in index)
    chk("index R204 note kept", "Cập nhật R204" in index)
    chk("index R204 row label", "PR119 BODY RESTRUCTURE R204" in index)

    # R196 script-defect repairs, kept as regression guards: milestone 6
    # separate lines, heading own line, R167 note own line in ascending
    # position, R204 note clean.
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
    r204_note = [l for l in il if l.startswith("- Cập nhật R204 (2026-11-23):")]
    r204_note_ok = len(r204_note) == 1 and "- Cập nhật R167 " not in r204_note[0]
    repair_detail = (f"milestone6={milestone_ok} heading={heading_ok} "
                     f"r196clean={r196_clean} r167ascending={r167_ok} r204note={r204_note_ok}")
    chk("index R196-defect repairs (milestone 6 lines, heading, R167 ascending, R204 note)",
        milestone_ok and heading_ok and r196_clean and r167_ok and r204_note_ok,
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
                                         ("R203", "818f027", 3005)):
        n = len(git("diff", "--name-only", BASE, content_sha).splitlines())
        chk(f"row-convention {row_n} cumulative {expected} == diff at {content_sha}",
            n == expected, str(n))

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..2be4074 == 599", n_commits == 599, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..2be4074 == 3007", n_files == 3007, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 286093, deletions 0",
        "286093 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 2be4074 vs integration exit 0, tree 1c1adecd",
        mt.returncode == 0 and tree.startswith("1c1adecd"), tree)

    chk("body head line 2be4074/599/3007",
        "**Head: `2be4074` · 599 commit · 3007 file**" in body)
    chk("body has R204 paragraph", "- **PR119 BODY RESTRUCTURE R204**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R204",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R204" in title_line, title_line[-60:])
    chk("body title has full R93..R204 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 205)),
        "R94 restored, R204 added")
    chk("body index reference at 2be4074", "(head `2be4074`)" in body)

    # R205 note + compaction: 65 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R205 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(101, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R204 after R203, before the compact block.
    bl = body.splitlines()
    i204 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R204**"))
    i203 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R203**"))
    order_ok = i204 == i203 + 1
    chk("body R205 note + R101-R165 compacted (65 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 65 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R204",
           "validator": "check_pr119_restructure_r205_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
