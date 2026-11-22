#!/usr/bin/env python3
"""R175 validator: PR #119 delivery index + body v2 coverage through 987cdb5.

Verifies the R175 restructure round: the delivery index now covers R174
(coverage head 987cdb5, full SHA 987cdb5a7316d44cbb8166739a637acdf3befef4),
and the repo body v2 file is synced to the R173 body v2 file + the R174
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R174 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R174 and
R175 note lines are present in the index.
The compaction window extends in R175: the "Khối mới nhất" paragraphs
R131-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 35 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R131 paragraph (809 chars -> 287) plus
trimming the new R174 paragraph to 691 chars is what keeps the body under
the ceiling this round (R174 warning: headroom was 408 chars; R175
headroom is 121 chars). The full paragraphs in "Khối mới nhất" stay in
ascending order (R166..R174), with the new paragraph after R173 and before
the compact block.
The R175 payload should be ~122,900 bytes, well under the 131,072
transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "987cdb5a7316d44cbb8166739a637acdf3befef4"
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

    chk("index header coverage head == 987cdb5", "(head `987cdb5`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("947b043", "987cdb5"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 539/2917", "**539 commit / 2917 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R175 note", "Cập nhật R175" in index)
    chk("index R174 note kept", "Cập nhật R174" in index)
    chk("index R174 row label", "PR119 BODY RESTRUCTURE R174" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..987cdb5 == 539", n_commits == 539, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..987cdb5 == 2917", n_files == 2917, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 273441, deletions 0",
        "273441 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 987cdb5 vs integration exit 0, tree d63bce9c",
        mt.returncode == 0 and tree.startswith("d63bce9c"), tree)

    chk("body head line 987cdb5/539/2917",
        "**Head: `987cdb5` · 539 commit · 2917 file**" in body)
    chk("body has R174 paragraph", "- **PR119 BODY RESTRUCTURE R174**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R174",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R174" in title_line, title_line[-60:])
    chk("body title has full R93..R174 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 175)),
        "R94 restored, R174 added")
    chk("body index reference at 987cdb5", "(head `987cdb5`)" in body)

    # R175 note + compaction: 35 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R175 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(131, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R174 after R173, before the compact block.
    bl = body.splitlines()
    i174 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R174**"))
    i173 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R173**"))
    order_ok = i174 == i173 + 1
    chk("body R175 note + R131-R165 compacted (35 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 35 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R174",
           "validator": "check_pr119_restructure_r175_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
