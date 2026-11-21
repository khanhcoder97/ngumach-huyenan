#!/usr/bin/env python3
"""R159 validator: PR #119 delivery index + body v2 coverage through c7100b1.

Verifies the R159 restructure round: the delivery index now covers R158
(coverage head c7100b1), and the repo body v2 file is synced to the
R158 body v2 file + the R158 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R158 run is present in the title line.
It also guards the R140 update-note defect (a content commit replaced the
previous "Cập nhật" note line instead of appending after it) by asserting
both the R158 and R159 note lines are present in the index.
The R158 compaction stays in place: the "Khối mới nhất" paragraphs
R142-R155 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 14 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. The R159 payload should be ~122,000 bytes, well under the
131,072 transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "c7100b1d9b8d33429217ad09e5b268dd4e8ce46b"
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

    chk("index header coverage head == c7100b1", "(head `c7100b1`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("3a93b21", "c7100b1"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 507/2869", "**507 commit / 2869 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R159 note", "Cập nhật R159" in index)
    chk("index R158 note kept", "Cập nhật R158" in index)
    chk("index R158 row label", "PR119 BODY RESTRUCTURE R158" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..c7100b1 == 507", n_commits == 507, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..c7100b1 == 2869", n_files == 2869, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 267659, deletions 0",
        "267659 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree c7100b1 vs integration exit 0, tree 2fee6f63",
        mt.returncode == 0 and tree.startswith("2fee6f63"), tree)

    chk("body head line c7100b1/507/2869",
        "**Head: `c7100b1` · 507 commit · 2869 file**" in body)
    chk("body has R158 paragraph", "- **PR119 BODY RESTRUCTURE R158**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R158",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R158" in title_line, title_line[-60:])
    chk("body title has full R93..R158 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 159)),
        "R94 restored, R158 added")
    chk("body index reference at c7100b1", "(head `c7100b1`)" in body)

    # R159 note + compaction: 14 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R159 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(142, 156):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    chk("body R159 note + R142-R155 compacted (14 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 14 and per_round_ok
        and len(body) < 105000, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R158",
           "validator": "check_pr119_restructure_r159_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
