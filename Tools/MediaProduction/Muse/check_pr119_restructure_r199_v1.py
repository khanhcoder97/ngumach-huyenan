#!/usr/bin/env python3
"""R199 validator: PR #119 delivery index + body v2 coverage through 389a85b.

Verifies the R199 restructure round: the delivery index now covers R198
(coverage head 389a85b, full SHA 389a85ba6835d55fd9b44e8436faf639138d833e),
and the repo body v2 file is synced to the R197 body v2 file + the R198
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R198 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R198 and
R199 note lines are present in the index.
The compaction window extends in R199: the "Khối mới nhất" paragraphs
R107-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 59 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R107 paragraph (694 chars -> 239) plus
the new R198 paragraph at 404 chars is what holds headroom this round
(R198 warning: headroom was 54 chars; the R198 payload body ran
104,922 chars). Body is now 104,922 chars -- headroom 78, and the
R199 payload should stay at or under 105,000. R200 warning: headroom
is only 78 chars; the next round must collapse R106 (694 chars ->
~240) and keep the new paragraph tight.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R198), with
the new paragraph after R197 and before the compact block.
The R199 payload should be ~122,300 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R195 row 2981 == 218f0fa,
R196 row 2984 == 41f9110, R197 row 2987 == 285ade4 -- all verified from
git this round). The R198 row therefore cites 2990 paths: 2989 at
389a85b + 1 new checker file in the R199 content commit. That figure is
verified in the R199 report after the content commit, not by this
checker (it runs on the working tree before the commit exists).
R196 script-defect repairs (kept as regression guards by this checker):
the R196 edit script dropped trailing "\\n" on whole-line replacements
and inserts, joining the 6 "Moc xac minh" bullets into one line,
swallowing the "## Ghi chu" heading into the R195 row, and gluing the
trailing duplicate R167 note onto the R196 note line. R197 repaired all
three: milestone bullets are 6 separate lines again, "## Ghi chu" is its
own line after the R196 row, and the R167 note is its own line in
ascending position (after R166, before R168).
Live-body read note: this round the GitHub MCP read path was unavailable
(call-tool stalled twice with a service restart; gh CLI needs auth), so
the live state was read from the public web UI by a browser task
(~14:47 JST, no sign-in): issue #116 still 34 comments, latest ACK
6862732081, no new direction since Gói 39; PR #119 head 389a85b,
587 commits / 2989 files / +282,989, checks 11/11 OK; the description
structure matches live R140 (PR title ends "+ R140", head inside the
description 78ccd85 · 471 · 2815, tail lines match). The exact live-body
char count/sha (92,520 / ddbe32ff) and updated_at (2026-11-22T23:50:59Z)
are carried from the last API byte-exact read (R198 round ~09:44 JST),
not re-read this round; mergeable_state at 389a85b could NOT be read
from the public web UI -- recorded honestly as unverifiable, with checks
11/11 OK and the merge-tree cross-check as the evidence.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "389a85ba6835d55fd9b44e8436faf639138d833e"
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

    chk("index header coverage head == 389a85b", "(head `389a85b`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("285ade4", "389a85b"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 587/2989", "**587 commit / 2989 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R199 note", "Cập nhật R199" in index)
    chk("index R198 note kept", "Cập nhật R198" in index)
    chk("index R198 row label", "PR119 BODY RESTRUCTURE R198" in index)

    # R196 script-defect repairs, kept as regression guards: milestone 6
    # separate lines, heading own line, R167 note own line in ascending
    # position, R198 note clean.
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
    r198_note = [l for l in il if l.startswith("- Cập nhật R198 (2026-11-23):")]
    r198_note_ok = len(r198_note) == 1 and "- Cập nhật R167 " not in r198_note[0]
    repair_detail = (f"milestone6={milestone_ok} heading={heading_ok} "
                     f"r196clean={r196_clean} r167ascending={r167_ok} r198note={r198_note_ok}")
    chk("index R196-defect repairs (milestone 6 lines, heading, R167 ascending, R198 note)",
        milestone_ok and heading_ok and r196_clean and r167_ok and r198_note_ok,
        repair_detail)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..389a85b == 587", n_commits == 587, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..389a85b == 2989", n_files == 2989, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 282989, deletions 0",
        "282989 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 389a85b vs integration exit 0, tree 6cc7da83",
        mt.returncode == 0 and tree.startswith("6cc7da83"), tree)

    chk("body head line 389a85b/587/2989",
        "**Head: `389a85b` · 587 commit · 2989 file**" in body)
    chk("body has R198 paragraph", "- **PR119 BODY RESTRUCTURE R198**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R198",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R198" in title_line, title_line[-60:])
    chk("body title has full R93..R198 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 199)),
        "R94 restored, R198 added")
    chk("body index reference at 389a85b", "(head `389a85b`)" in body)

    # R199 note + compaction: 59 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R199 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(107, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R198 after R197, before the compact block.
    bl = body.splitlines()
    i198 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R198**"))
    i197 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R197**"))
    order_ok = i198 == i197 + 1
    chk("body R199 note + R107-R165 compacted (59 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 59 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R198",
           "validator": "check_pr119_restructure_r199_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
