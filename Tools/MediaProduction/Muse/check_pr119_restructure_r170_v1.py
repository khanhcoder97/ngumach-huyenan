#!/usr/bin/env python3
"""R170 validator: PR #119 delivery index + body v2 coverage through 9756ec0.

Verifies the R170 restructure round: the delivery index now covers R169
(coverage head 9756ec0), and the repo body v2 file is synced to the
R168 body v2 file + the R169 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R169 run is present in the title line.
It also guards the R140 update-note defect (a content commit replaced the
previous "Cập nhật" note line instead of appending after it) by asserting
both the R169 and R170 note lines are present in the index.
The compaction window extends in R170: the "Khối mới nhất" paragraphs
R138-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 28 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R138 paragraph (1,188 chars -> 377) plus
trimming the new R169 paragraph to 743 chars (R168 was 811) is what keeps
the body under the ceiling this round (R169 warning: collapsing R138 alone
would have left the body ~105,002 chars).
The R170 payload should be ~123,500 bytes, well under the 131,072
transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "9756ec084e54531533219f5a850e0cbf6548836e"
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

    chk("index header coverage head == 9756ec0", "(head `9756ec0`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("a99d985", "9756ec0"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 529/2902", "**529 commit / 2902 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R170 note", "Cập nhật R170" in index)
    chk("index R169 note kept", "Cập nhật R169" in index)
    chk("index R169 row label", "PR119 BODY RESTRUCTURE R169" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..9756ec0 == 529", n_commits == 529, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..9756ec0 == 2902", n_files == 2902, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 271591, deletions 0",
        "271591 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 9756ec0 vs integration exit 0, tree 3414e4a1",
        mt.returncode == 0 and tree.startswith("3414e4a1"), tree)

    chk("body head line 9756ec0/529/2902",
        "**Head: `9756ec0` · 529 commit · 2902 file**" in body)
    chk("body has R169 paragraph", "- **PR119 BODY RESTRUCTURE R169**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R169",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R169" in title_line, title_line[-60:])
    chk("body title has full R93..R169 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 170)),
        "R94 restored, R169 added")
    chk("body index reference at 9756ec0", "(head `9756ec0`)" in body)

    # R170 note + compaction: 28 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R170 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(138, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    chk("body R170 note + R138-R165 compacted (28 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 28 and per_round_ok
        and len(body) < 105000, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R169",
           "validator": "check_pr119_restructure_r170_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
