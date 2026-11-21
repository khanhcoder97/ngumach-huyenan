#!/usr/bin/env python3
"""R161 validator: PR #119 delivery index + body v2 coverage through 285d257.

Verifies the R161 restructure round: the delivery index now covers R160
(coverage head 285d257), and the repo body v2 file is synced to the
R159 body v2 file + the R160 block. All figures re-derived from git, never
copied from the documents. Also guards the title-line sequence: the R97
round dropped "R94" from the body v2 title when editing by hand, so this
checker asserts the full R93..R160 run is present in the title line.
It also guards the R140 update-note defect (a content commit replaced the
previous "Cập nhật" note line instead of appending after it) by asserting
both the R160 and R161 note lines are present in the index.
The compaction window extends in R161: the "Khối mới nhất" paragraphs
R142-R157 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 16 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. The R161 payload should be ~123,000 bytes, well under the
131,072 transport ceiling.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "285d257a70ba073dd4964bb53c0b12454e63a8fb"
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

    chk("index header coverage head == 285d257", "(head `285d257`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("ed3e535", "285d257"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 511/2875", "**511 commit / 2875 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R161 note", "Cập nhật R161" in index)
    chk("index R160 note kept", "Cập nhật R160" in index)
    chk("index R160 row label", "PR119 BODY RESTRUCTURE R160" in index)

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..285d257 == 511", n_commits == 511, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..285d257 == 2875", n_files == 2875, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 268376, deletions 0",
        "268376 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 285d257 vs integration exit 0, tree ff3a6dee",
        mt.returncode == 0 and tree.startswith("ff3a6dee"), tree)

    chk("body head line 285d257/511/2875",
        "**Head: `285d257` · 511 commit · 2875 file**" in body)
    chk("body has R160 paragraph", "- **PR119 BODY RESTRUCTURE R160**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R160",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R160" in title_line, title_line[-60:])
    chk("body title has full R93..R160 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 161)),
        "R94 restored, R160 added")
    chk("body index reference at 285d257", "(head `285d257`)" in body)

    # R161 note + compaction: 16 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R161 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(142, 158):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    chk("body R161 note + R142-R157 compacted (16 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 16 and per_round_ok
        and len(body) < 105000, compact_detail)

    failures = [k for k, v in checks.items() if not v["pass"]]
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R160",
           "validator": "check_pr119_restructure_r161_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
