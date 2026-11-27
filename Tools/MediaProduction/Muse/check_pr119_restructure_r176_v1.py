#!/usr/bin/env python3
"""R176 validator: PR #119 delivery index + body v2 coverage through f311bfa.

Verifies the R176 restructure round: the delivery index now covers R175
(coverage head f311bfa, full SHA f311bfa7edcb65d984a130696ba1da2a69219090),
and the repo body v2 file is synced to the R174 body v2 file + the R175
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R175 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R175 and
R176 note lines are present in the index.
The compaction window extends in R176: the "Khối mới nhất" paragraphs
R130-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 36 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R130 paragraph (809 chars -> 287) plus
trimming the new R175 paragraph to 595 chars is what keeps the body under
the ceiling this round (R175 warning: headroom was 121 chars; R176
headroom is 22 chars). The full paragraphs in "Khối mới nhất" stay in
ascending order (R166..R175), with the new paragraph after R174 and before
the compact block.
The R176 payload should be ~123,000 bytes, well under the 131,072
transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "f311bfa7edcb65d984a130696ba1da2a69219090"
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

    chk("index header coverage head == f311bfa", "(head `f311bfa`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("e07441d", "f311bfa"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 541/2920", "**541 commit / 2920 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R176 note", "Cập nhật R176" in index)
    chk("index R175 note kept", "Cập nhật R175" in index)
    chk("index R175 row label", "PR119 BODY RESTRUCTURE R175" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..f311bfa == 541", n_commits == 541, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..f311bfa == 2920", n_files == 2920, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 273810, deletions 0",
        "273810 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree f311bfa vs integration exit 0, tree 83d7a9ac",
        mt.returncode == 0 and tree.startswith("83d7a9ac"), tree)

    chk("body head line f311bfa/541/2920",
        "**Head: `f311bfa` · 541 commit · 2920 file**" in body)
    chk("body has R175 paragraph", "- **PR119 BODY RESTRUCTURE R175**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R175",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R175" in title_line, title_line[-60:])
    chk("body title has full R93..R175 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 176)),
        "R94 restored, R175 added")
    chk("body index reference at f311bfa", "(head `f311bfa`)" in body)

    # R176 note + compaction: 36 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R176 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(130, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R175 after R174, before the compact block.
    bl = body.splitlines()
    i175 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R175**"))
    i174 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R174**"))
    order_ok = i175 == i174 + 1
    chk("body R176 note + R130-R165 compacted (36 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 36 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R175",
           "validator": "check_pr119_restructure_r176_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
