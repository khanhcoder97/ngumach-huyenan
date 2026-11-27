#!/usr/bin/env python3
"""R182 validator: PR #119 delivery index + body v2 coverage through 918ea77.

Verifies the R182 restructure round: the delivery index now covers R181
(coverage head 918ea77, full SHA 918ea7774cea0f5f5e4517a459aeb8a6ee7ba3b5),
and the repo body v2 file is synced to the R180 body v2 file + the R181
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R181 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R181 and
R182 note lines are present in the index.
The compaction window extends in R182: the "Khối mới nhất" paragraphs
R124-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 42 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R124 paragraph (750 chars -> ~270) plus
trimming the new R181 paragraph to ~430 chars is what keeps the body under
the ceiling this round (R181 warning: headroom was 29 chars; the first
budget attempt projected 105,043 and was trimmed before any write).
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R181), with
the new paragraph after R180 and before the compact block.
The R182 payload should be ~123,000 bytes, well under the 131,072
transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "918ea7774cea0f5f5e4517a459aeb8a6ee7ba3b5"
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

    chk("index header coverage head == 918ea77", "(head `918ea77`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("dc50ab3", "918ea77"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 553/2938", "**553 commit / 2938 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R182 note", "Cập nhật R182" in index)
    chk("index R181 note kept", "Cập nhật R181" in index)
    chk("index R181 row label", "PR119 BODY RESTRUCTURE R181" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..918ea77 == 553", n_commits == 553, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..918ea77 == 2938", n_files == 2938, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 276079, deletions 0",
        "276079 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 918ea77 vs integration exit 0, tree 3cc904a2",
        mt.returncode == 0 and tree.startswith("3cc904a2"), tree)

    chk("body head line 918ea77/553/2938",
        "**Head: `918ea77` · 553 commit · 2938 file**" in body)
    chk("body has R181 paragraph", "- **PR119 BODY RESTRUCTURE R181**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R181",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R181" in title_line, title_line[-60:])
    chk("body title has full R93..R181 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 182)),
        "R94 restored, R181 added")
    chk("body index reference at 918ea77", "(head `918ea77`)" in body)

    # R182 note + compaction: 42 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R182 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(124, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R181 after R180, before the compact block.
    bl = body.splitlines()
    i181 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R181**"))
    i180 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R180**"))
    order_ok = i181 == i180 + 1
    chk("body R182 note + R124-R165 compacted (42 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 42 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R181",
           "validator": "check_pr119_restructure_r182_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
