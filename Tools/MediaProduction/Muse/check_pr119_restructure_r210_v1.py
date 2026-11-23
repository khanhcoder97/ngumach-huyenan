#!/usr/bin/env python3
"""R210 validator: PR #119 delivery index + body v2 coverage through e7eacae.

Verifies the R210 restructure round: the delivery index now covers R209
(coverage head e7eacae, full SHA e7eacae83861e7e135c4328ed52e67721cb17cd4),
and the repo body v2 file is synced to the R208 body v2 file + the R209
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R209 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R209 and
R210 note lines are present in the index.
The compaction window extends in R210: the "Khối mới nhất" paragraphs
R96-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 70 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R96 paragraph (483 chars -> 219) plus
the new R209 paragraph at 248 chars is what holds headroom this round
(R209 warning: headroom was 28 chars; this round's body is 104,957 chars,
headroom 43). The R209 paragraph drops the "live vẫn R140" clause the
R207/R208 paragraphs carried -- the live-body state is already recorded
in the head line and in the R209 index row -- so the post-push payload
refresh (+~39 chars, R209 lesson) still lands under the ceiling.
R211 warning: headroom after R210 is 43 chars; the next round must
collapse R95 (full paragraph, measure first) and keep the new paragraph
tight (<= ~300 chars).
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R209), with
the new paragraph after R208 and before the compact block.
The R210 payload should be ~121,500 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R201 row 2999 == e50ba30,
R202 row 3002 == 549b8b0, R203 row 3005 == 818f027, R204 row 3008 ==
df30756, R205 row 3011 == 004cf47, R206 row 3014 == 0db08af, R207 row 3017
== a89a1cf, R208 row 3020 == c663140 -- all re-derived from git by THIS
checker). The R209 row therefore cites 3023 paths: 3022 at e7eacae + 1
new checker file in the R210 content commit. That figure is verified in
the R210 report after the content commit, not by this checker (it runs on
the working tree before the commit exists); this checker asserts only that
the row text cites 3023 and that the git diff at e7eacae is 3022. (The
`6cac9da` hits in this file are the previous cover value, intentional --
in this docstring and in the R208-row guard string citing "3019 at
6cac9da", legitimate.)
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
R207 script-defect repair (kept as a regression guard in the edit
script): the R207 edit script's idempotency re-run initially crashed on
its OLD-state pre-condition assert (the body head-line replace looked for
the old head line after a successful apply); fixed that round by
checking the NEW state first (re-run reports already-applied
changed: 0, verified). R210 also corrects the body "Ghi chú" line: it
read "R158/R208 ... R97–R165 ... R203/R204/R205/R206/R207/R208" -- the range is
stale after R210 compacted R96; it now reads "R158/R209 ... R96–R165 ...
R203/R204/R205/R206/R207/R208/R209".
Live-body read note: this round the GitHub API was read twice (~00:45 JST,
read-only): the MCP read path returned the clean body this round (no
mangled character, unlike R209) and the direct public-API read
(curl api.github.com) agreed: live body still R140
(title ends "+ R140", head inside the description 78ccd85 · 471 · 2815,
body 92,520 chars, sha ddbe32ff, 0 U+FFFD, updated_at
2026-11-23T14:49:57Z -- bumped by the R209 push updating the PR head,
body bytes unchanged), head e7eacae, 609 commits / 3022 files / +289,058,
mergeable true + mergeable_state clean at e7eacae (the MCP `mergeable`
field returned null at read time -- mergeable_state is the operative
field). Issue #116 still 34 comments (30 + 4 paginated), latest ACK
6862732081, no new direction since Gói 39. The .bak directory lives at
pr_comments/.bak-prepost-20261123 (NOT directly under godot-prototype).
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "e7eacae83861e7e135c4328ed52e67721cb17cd4"
INTEGRATION = "f3db6b384886a59128328b8daa8c9eefc2d8f3ce"
CHECKER_NAME = "check_pr119_restructure_r210_v1.py"

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

    chk("index header coverage head == e7eacae", "(head `e7eacae`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("c663140", "e7eacae"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 609/3022", "**609 commit / 3022 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R210 note", "Cập nhật R210" in index)
    chk("index R209 note kept", "Cập nhật R209" in index)
    chk("index R209 row label", "PR119 BODY RESTRUCTURE R209" in index)

    # R196 script-defect repairs, kept as regression guards: milestone 6
    # separate lines, heading own line, R167 note own line in ascending
    # position, R209 note clean.
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
    r209_note = [l for l in il if l.startswith("- Cập nhật R209 (2026-11-23):")]
    r209_note_ok = len(r209_note) == 1 and "- Cập nhật R167 " not in r209_note[0]
    repair_detail = (f"milestone6={milestone_ok} heading={heading_ok} "
                     f"r196clean={r196_clean} r167ascending={r167_ok} r209note={r209_note_ok}")
    chk("index R196-defect repairs (milestone 6 lines, heading, R167 ascending, R209 note)",
        milestone_ok and heading_ok and r196_clean and r167_ok and r209_note_ok,
        repair_detail)

    # R198 .bak correction: the R198 row must carry the ĐÍNH CHÍNH R200 note.
    r198_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R198 |")]
    bak_ok = (len(r198_row) == 1 and "ĐÍNH CHÍNH R200" in r198_row[0]
              and "KHÔNG tồn tại trên đĩa khi R199 kiểm tra" in r198_row[0])
    chk("index R198 row carries ĐÍNH CHÍNH R200 (.bak claim corrected)", bak_ok)

    # R207 correction (carried from R207): the R205 row must cite cumulative 3011.
    r205_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R205 |")]
    r205_ok = (len(r205_row) == 1 and "cumulative 3011 paths" in r205_row[0]
               and "cumulative 3009 paths" not in r205_row[0])
    chk("index R205 row cumulative == 3011 (ĐÍNH CHÍNH R207)", r205_ok)

    # R208 correction (carried from R208): the R207 row must cite cumulative 3017.
    r207_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R207 |")]
    r207_row_ok = (len(r207_row) == 1 and "cumulative 3017 paths" in r207_row[0])
    chk("index R207 row cumulative == 3017 (3016 at d37a385 + 1 checker)", r207_row_ok)

    # R209 correction (carried from R209): the R208 row must cite cumulative 3020.
    r208_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R208 |")]
    r208_row_ok = (len(r208_row) == 1 and "cumulative 3020 paths" in r208_row[0])
    chk("index R208 row cumulative == 3020 (3019 at 6cac9da + 1 checker)", r208_row_ok)

    # R210 row: must cite cumulative 3023 (3022 at e7eacae + 1 new checker
    # in the R210 content commit); the git figure is re-derived below.
    r209_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R209 |")]
    r209_row_ok = (len(r209_row) == 1 and "cumulative 3023 paths" in r209_row[0])
    chk("index R209 row cumulative == 3023 (3022 at e7eacae + 1 checker)", r209_row_ok)

    # Row-convention verification, re-derived from git: a row's cumulative
    # N paths is the diff path count at the AUTHORING round's content commit.
    for row_n, content_sha, expected in (("R201", "e50ba30", 2999),
                                         ("R202", "549b8b0", 3002),
                                         ("R203", "818f027", 3005),
                                         ("R204", "df30756", 3008),
                                         ("R205", "004cf47", 3011),
                                         ("R206", "0db08af", 3014),
                                         ("R207", "a89a1cf", 3017),
                                         ("R208", "c663140", 3020)):
        n = len(git("diff", "--name-only", BASE, content_sha).splitlines())
        chk(f"row-convention {row_n} cumulative {expected} == diff at {content_sha}",
            n == expected, str(n))

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..e7eacae == 609", n_commits == 609, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..e7eacae == 3022", n_files == 3022, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 289058, deletions 0",
        "289058 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree e7eacae vs integration exit 0, tree c0ebfb8c",
        mt.returncode == 0 and tree.startswith("c0ebfb8c"), tree)

    chk("body head line e7eacae/609/3022",
        "**Head: `e7eacae` · 609 commit · 3022 file**" in body)
    chk("body has R209 paragraph", "- **PR119 BODY RESTRUCTURE R209**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R209",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R209" in title_line, title_line[-60:])
    chk("body title has full R93..R209 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 210)),
        "R94 restored, R209 added")
    chk("body index reference at e7eacae", "(head `e7eacae`)" in body)
    chk("body R210 update note", "R210 (lượt cập nhật này)" in body)

    # Body "Ghi chú" line corrected this round: R158/R209, range R96-R165,
    # report list complete through R209, no double slash.
    note23 = [l for l in body.splitlines() if l.startswith("Ghi chú R158/")]
    note23_ok = (len(note23) == 1 and note23[0].startswith("Ghi chú R158/R209:")
                 and "R96–R165" in note23[0] and "R203/R204/R205/R206/R207/R208/R209" in note23[0]
                 and "//" not in note23[0])
    chk("body Ghi-chú line corrected (R158/R209, R96-R165, list complete)", note23_ok)

    # R210 note + compaction: 70 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R210 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(96, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R209 after R208, before the compact block.
    bl = body.splitlines()
    i209 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R209**"))
    i208 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R208**"))
    order_ok = i209 == i208 + 1
    chk("body R210 note + R96-R165 compacted (70 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 70 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    # Working tree must contain exactly the 3 intended paths (the R206
    # failure mode: a fix left uncommitted past the report commit).
    status = git("status", "--porcelain")
    status_lines = sorted(l for l in status.splitlines() if l.strip())
    expected_status = sorted([
        " M Implementation/Reports/MuseMedia/MEDIA02_PR119_BODY_V2_20261113.md",
        " M Implementation/Reports/MuseMedia/MEDIA02_PR119_DELIVERY_INDEX_20261113.md",
        f"?? Tools/MediaProduction/Muse/{CHECKER_NAME}"])
    chk("git status shows only index + body + this checker",
        status_lines == expected_status, "; ".join(status_lines))

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R209",
           "validator": "check_pr119_restructure_r210_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
