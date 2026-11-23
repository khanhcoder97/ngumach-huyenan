#!/usr/bin/env python3
"""R216 validator: PR #119 delivery index + body v2 coverage through 1e564a2.

Verifies the R216 restructure round: the delivery index now covers R215
(coverage head 1e564a2, full SHA 1e564a2520fca2d856b351a97c3d3359d7fa9cc5),
and the repo body v2 file is synced to the R214 body v2 file + the R215
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R215 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R215 and
R216 note lines are present in the index.
The compaction window extends in R216: the "Khối mới nhất" paragraphs
R88-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 78 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R89 + R88 paragraphs (494 chars each ->
208) plus the new R215 paragraph at 248 chars is what holds headroom
this round (R215 warning: headroom was 90 chars; this round's body is
104,794 chars, headroom 206). The DOUBLE compaction follows the R215
warning exactly (collapse R89 + R88); a single compaction no longer
holds at +115/round growth.
The R215 paragraph drops the "live vẫn R140" clause the R207/R208
paragraphs carried -- the live-body state is already recorded in the
head line and in the R215 index row -- so the post-push payload refresh
(+~35 chars, R209/R210/R211/R212/R213/R214/R215 lesson) still lands under the ceiling.
R217 warning: headroom after R216 is 206 chars; the double compaction
bought back 572 chars against a 248-char new paragraph, so the margin
holds while two paragraphs are compacted per round -- R217 must compact
R87 + R86 (or trim the head line hard), or the body crosses 105,000
within a few rounds as the head line keeps growing with honest
live-read disclosures.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R215), with
the new paragraph after R214 and before the compact block.
The R216 payload should be ~121,000 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R201 row 2999 == e50ba30,
R202 row 3002 == 549b8b0, R203 row 3005 == 818f027, R204 row 3008 ==
df30756, R205 row 3011 == 004cf47, R206 row 3014 == 0db08af, R207 row 3017
== a89a1cf, R208 row 3020 == c663140, R209 row 3023 == a10f9f5, R210 row
3026 == a96f796, R211 row 3029 == dd853fe, R212 row 3032 == c77587a,
R213 row 3035 == 2ce013b, R214 row 3038 == 6127a16 -- all re-derived from
git by THIS checker).
The R215 row therefore cites 3041 paths: 3040 at 1e564a2 + 1 new checker
file in the R216 content commit. That figure is verified in the R216
report after the content commit, not by this checker (it runs on the
working tree before the commit exists); this checker asserts only that
the row text cites 3041 and that the git diff at 1e564a2 is 3040.
(The `3de99c9` hits in this file are the previous cover value,
intentional -- in this docstring and in the R214-row guard string citing
"3037 at 3de99c9", legitimate.)
R198 .bak correction (kept as a regression guard): the R198 index
row carries the ĐÍNH CHÍNH R200 note (the `.bak-prepost-20261123`
directory did NOT exist on disk when R199 checked; R199 created it).
The same unverifiable claim also appears in rows R137-R197; those
historical rows are left as-is (disclosed in the R200 report), only the
R198 row (the round folded in at R200) is corrected.
R196 script-defect repairs (kept as regression guards by this checker):
the R196 edit script dropped trailing "\\n" on whole-line replacements
and inserts, gluing the 6 "Moc xac minh" bullets into one line,
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
changed: 0, verified). R216 also corrects the body "Ghi chú" line: it
read "R158/R214 ... R90–R165 ... R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214" -- the range is
stale after R216 compacted R89 + R88; it now reads "R158/R215 ... R88–R165 ...
R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215".
Live-body read note: this round the GitHub API was read twice (~08:40 JST,
read-only): the MCP read path returned the clean body on the first read
(92,520 chars, sha ddbe32ff, 0 U+FFFD) and the direct public-API read
(curl api.github.com) AGREED (92,520 chars, sha ddbe32ff, 0 U+FFFD,
mergeable true, mergeable_state clean) -- a real cross-check this round,
unlike R215 where the direct read was rate-limited. Live body still R140
(title ends "+ R140", head inside the description 78ccd85 · 471 · 2815,
updated_at 2026-11-23T22:47:25Z -- bumped by the R215 push updating the
PR head, body bytes unchanged), head 1e564a2, 621 commits / 3040 files /
+293,232, mergeable_state clean at 1e564a2 (mergeable null via MCP, true
via direct read). Issue #116 still 34 comments (MCP read + direct curl
read agree: 34, latest ACK 6862732081), no new direction since Gói 39.
The R215 payload was backed up to pr_comments/.bak-prepost-20261124 by
R216 (sha256 84645084… both copies); R215 itself had not made the copy --
disclosed in the R216 report, not claimed as R215's.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "1e564a2520fca2d856b351a97c3d3359d7fa9cc5"
INTEGRATION = "f3db6b384886a59128328b8daa8c9eefc2d8f3ce"
CHECKER_NAME = "check_pr119_restructure_r216_v1.py"

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

    chk("index header coverage head == 1e564a2", "(head `1e564a2`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("6127a16", "1e564a2"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 621/3040", "**621 commit / 3040 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R216 note", "Cập nhật R216" in index)
    chk("index R215 note kept", "Cập nhật R215" in index)
    chk("index R215 row label", "PR119 BODY RESTRUCTURE R215" in index)

    # R196 script-defect repairs, kept as regression guards: milestone 6
    # separate lines, heading own line, R167 note own line in ascending
    # position, R215 note clean.
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
    r215_note = [l for l in il if l.startswith("- Cập nhật R215 (2026-11-24):")]
    r215_note_ok = len(r215_note) == 1 and "- Cập nhật R167 " not in r215_note[0]
    repair_detail = (f"milestone6={milestone_ok} heading={heading_ok} "
                     f"r196clean={r196_clean} r167ascending={r167_ok} r215note={r215_note_ok}")
    chk("index R196-defect repairs (milestone 6 lines, heading, R167 ascending, R215 note)",
        milestone_ok and heading_ok and r196_clean and r167_ok and r215_note_ok,
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

    # R210 correction (carried from R210): the R209 row must cite cumulative 3023.
    r209_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R209 |")]
    r209_row_ok = (len(r209_row) == 1 and "cumulative 3023 paths" in r209_row[0])
    chk("index R209 row cumulative == 3023 (3022 at e7eacae + 1 checker)", r209_row_ok)

    # R211 correction (carried from R211): the R210 row must cite cumulative 3026.
    r210_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R210 |")]
    r210_row_ok = (len(r210_row) == 1 and "cumulative 3026 paths" in r210_row[0])
    chk("index R210 row cumulative == 3026 (3025 at 48a1cd8 + 1 checker)", r210_row_ok)

    # R212 correction (carried from R212): the R211 row must cite cumulative 3029.
    r211_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R211 |")]
    r211_row_ok = (len(r211_row) == 1 and "cumulative 3029 paths" in r211_row[0])
    chk("index R211 row cumulative == 3029 (3028 at 3a4c8f8 + 1 checker)", r211_row_ok)

    # R213 correction (carried from R213): the R212 row must cite cumulative 3032.
    r212_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R212 |")]
    r212_row_ok = (len(r212_row) == 1 and "cumulative 3032 paths" in r212_row[0])
    chk("index R212 row cumulative == 3032 (3031 at 381865f + 1 checker)", r212_row_ok)

    # R214 correction (carried from R214): the R213 row must cite cumulative 3035.
    r213_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R213 |")]
    r213_row_ok = (len(r213_row) == 1 and "cumulative 3035 paths" in r213_row[0])
    chk("index R213 row cumulative == 3035 (3034 at 1afb41e + 1 checker)", r213_row_ok)

    # R215 correction (carried from R215): the R214 row must cite cumulative 3038.
    r214_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R214 |")]
    r214_row_ok = (len(r214_row) == 1 and "cumulative 3038 paths" in r214_row[0])
    chk("index R214 row cumulative == 3038 (3037 at 3de99c9 + 1 checker)", r214_row_ok)

    # R216 row: must cite cumulative 3041 (3040 at 1e564a2 + 1 new checker
    # in the R216 content commit); the git figure is re-derived below.
    r215_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R215 |")]
    r215_row_ok = (len(r215_row) == 1 and "cumulative 3041 paths" in r215_row[0])
    chk("index R215 row cumulative == 3041 (3040 at 1e564a2 + 1 checker)", r215_row_ok)

    # Row-convention verification, re-derived from git: a row's cumulative
    # N paths is the diff path count at the AUTHORING round's content commit.
    for row_n, content_sha, expected in (("R201", "e50ba30", 2999),
                                         ("R202", "549b8b0", 3002),
                                         ("R203", "818f027", 3005),
                                         ("R204", "df30756", 3008),
                                         ("R205", "004cf47", 3011),
                                         ("R206", "0db08af", 3014),
                                         ("R207", "a89a1cf", 3017),
                                         ("R208", "c663140", 3020),
                                         ("R209", "a10f9f5", 3023),
                                         ("R210", "a96f796", 3026),
                                         ("R211", "dd853fe", 3029),
                                         ("R212", "c77587a", 3032),
                                         ("R213", "2ce013b", 3035),
                                         ("R214", "6127a16", 3038)):
        n = len(git("diff", "--name-only", BASE, content_sha).splitlines())
        chk(f"row-convention {row_n} cumulative {expected} == diff at {content_sha}",
            n == expected, str(n))

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..1e564a2 == 621", n_commits == 621, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..1e564a2 == 3040", n_files == 3040, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 293232, deletions 0",
        "293232 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 1e564a2 vs integration exit 0, tree 4e13aa58",
        mt.returncode == 0 and tree.startswith("4e13aa58"), tree)

    chk("body head line 1e564a2/621/3040",
        "**Head: `1e564a2` · 621 commit · 3040 file**" in body)
    chk("body has R215 paragraph", "- **PR119 BODY RESTRUCTURE R215**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R215",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R215" in title_line, title_line[-60:])
    chk("body title has full R93..R215 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 216)),
        "R94 restored, R215 added")
    chk("body index reference at 1e564a2", "(head `1e564a2`)" in body)
    chk("body R216 update note", "R216 (lượt cập nhật này)" in body)

    # Body "Ghi chú" line corrected this round: R158/R215, range R88-R165,
    # report list complete through R215, no double slash.
    note23 = [l for l in body.splitlines() if l.startswith("Ghi chú R158/")]
    note23_ok = (len(note23) == 1 and note23[0].startswith("Ghi chú R158/R215:")
                 and "R88–R165" in note23[0] and "R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215" in note23[0]
                 and "//" not in note23[0])
    chk("body Ghi-chú line corrected (R158/R215, R88-R165, list complete)", note23_ok)

    # R216 note + compaction: 78 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R216 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(88, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R215 after R214, before the compact block.
    bl = body.splitlines()
    i215 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R215**"))
    i214 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R214**"))
    order_ok = i215 == i214 + 1
    chk("body R216 note + R88-R165 compacted (78 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 78 and per_round_ok
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
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R215",
           "validator": "check_pr119_restructure_r216_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
