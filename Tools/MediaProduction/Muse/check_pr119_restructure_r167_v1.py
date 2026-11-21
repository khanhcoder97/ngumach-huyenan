#!/usr/bin/env python3
"""R167 validator: PR #119 delivery index + body v2 coverage through ec66d5b.

Verifies the R167 restructure round: the delivery index now covers R166
(coverage head ec66d5b), and the repo body v2 file is synced to the
R165 body v2 file + the R166 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R166 run is present in the title line.
It also guards the R140 update-note defect (a content commit replaced the
previous "Cập nhật" note line instead of appending after it) by asserting
both the R166 and R167 note lines are present in the index.
The compaction window extends in R167: the "Khối mới nhất" paragraphs
R141-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 25 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Compacting only R165 would have left the body at ~105,350
chars, past the ceiling, so the R141 paragraph is collapsed as well this
round (R166 precedent: second compaction or trim required, not optional).
The R167 payload should be ~123,500 bytes, well under the 131,072
transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "ec66d5be9e013cb92e1ee99f0226358883c1ef98"
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

    chk("index header coverage head == ec66d5b", "(head `ec66d5b`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("f85dd45", "ec66d5b"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 523/2893", "**523 commit / 2893 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R167 note", "Cập nhật R167" in index)
    chk("index R166 note kept", "Cập nhật R166" in index)
    chk("index R166 row label", "PR119 BODY RESTRUCTURE R166" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..ec66d5b == 523", n_commits == 523, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..ec66d5b == 2893", n_files == 2893, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 270517, deletions 0",
        "270517 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree ec66d5b vs integration exit 0, tree bb86ab53",
        mt.returncode == 0 and tree.startswith("bb86ab53"), tree)

    chk("body head line ec66d5b/523/2893",
        "**Head: `ec66d5b` · 523 commit · 2893 file**" in body)
    chk("body has R166 paragraph", "- **PR119 BODY RESTRUCTURE R166**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R166",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R166" in title_line, title_line[-60:])
    chk("body title has full R93..R166 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 167)),
        "R94 restored, R166 added")
    chk("body index reference at ec66d5b", "(head `ec66d5b`)" in body)

    # R167 note + compaction: 25 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R167 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(141, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    chk("body R167 note + R141-R165 compacted (25 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 25 and per_round_ok
        and len(body) < 105000, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R166",
           "validator": "check_pr119_restructure_r167_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
