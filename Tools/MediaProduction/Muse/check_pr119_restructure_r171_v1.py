#!/usr/bin/env python3
"""R171 validator: PR #119 delivery index + body v2 coverage through f1fa774.

Verifies the R171 restructure round: the delivery index now covers R170
(coverage head f1fa774), and the repo body v2 file is synced to the
R169 body v2 file + the R170 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R170 run is present in the title line.
It also guards the R140 update-note defect (a content commit replaced the
previous "Cập nhật" note line instead of appending after it) by asserting
both the R170 and R171 note lines are present in the index.
The compaction window extends in R171: the "Khối mới nhất" paragraphs
R136-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 30 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R137 paragraph (1,248 chars -> 382) and the
R136 paragraph (918 chars -> 333) plus trimming the new R170 paragraph to
746 chars is what keeps the body under the ceiling this round (R170 warning:
collapsing R137 alone with an untrimmed paragraph would have left the body
~104,992 chars; two compactions follow the R164/R165/R167 precedent).
The R171 payload should be ~123,500 bytes, well under the 131,072
transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "f1fa77479b088c2aa7c6cf66eaf4186b58536499"
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

    chk("index header coverage head == f1fa774", "(head `f1fa774`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("bc371ed", "f1fa774"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 531/2905", "**531 commit / 2905 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R171 note", "Cập nhật R171" in index)
    chk("index R170 note kept", "Cập nhật R170" in index)
    chk("index R170 row label", "PR119 BODY RESTRUCTURE R170" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..f1fa774 == 531", n_commits == 531, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..f1fa774 == 2905", n_files == 2905, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 271956, deletions 0",
        "271956 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree f1fa774 vs integration exit 0, tree d30adc95",
        mt.returncode == 0 and tree.startswith("d30adc95"), tree)

    chk("body head line f1fa774/531/2905",
        "**Head: `f1fa774` · 531 commit · 2905 file**" in body)
    chk("body has R170 paragraph", "- **PR119 BODY RESTRUCTURE R170**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R170",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R170" in title_line, title_line[-60:])
    chk("body title has full R93..R170 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 171)),
        "R94 restored, R170 added")
    chk("body index reference at f1fa774", "(head `f1fa774`)" in body)

    # R171 note + compaction: 30 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R171 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(136, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    chk("body R171 note + R136-R165 compacted (30 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 30 and per_round_ok
        and len(body) < 105000, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R170",
           "validator": "check_pr119_restructure_r171_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
