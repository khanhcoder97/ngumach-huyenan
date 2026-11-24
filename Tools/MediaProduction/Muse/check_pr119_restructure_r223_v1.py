#!/usr/bin/env python3
"""R223 validator: PR #119 delivery index + body v2 coverage through 37ea7ad.

Verifies the R223 restructure round: the delivery index now covers R222
(coverage head 37ea7ad, full SHA 37ea7ad5aba4cafc94701232c857bcf5b0d8c6e8),
and the repo body v2 file is synced to the R221 body v2 file + the R222
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R222 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R222 and
R223 note lines are present in the index.
The compaction window extends in R223: the "Khối mới nhất" paragraphs
R74-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 92 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R75 + R74 paragraphs (438 and 489 chars ->
207 each -- the R76-R80 template measures 208, the R75/R74 lines measure
207; the checker asserts < 400, not an exact 208) plus the new R222
paragraph at 254 chars is what holds headroom this round (R222 warning:
headroom was 1,981 chars; this round's body is 102,822 chars, headroom
2,178). The head line shrank 1,028 -> 1,017 chars this round because the
live-body state is now the posted R222 (shorter to state than the
R140-era disclosure). The DOUBLE compaction continues (R223 compacts
R75 + R74 per the R222 warning).
The R222 paragraph records the live post -- the live-body state is already
recorded in the head line and in the R222 index row -- so the post-push
payload refresh (+~35 chars, R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222 lesson) still lands under the ceiling.
R224 warning: headroom after R223 is 2,178 chars; the double compaction
bought back 511 chars against a 254-char new paragraph; keep compacting
two paragraphs a round (R73 + R72 next) or the body crosses 105,000
within a few rounds if the head line grows again with honest live-read
disclosures.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R222), with
the new paragraph after R221 and before the compact block.
The R223 payload should be ~121,000 bytes, well under the 131,072
transport ceiling.
Row-convention note: a table row's "cumulative N paths" is the diff path
count at the AUTHORING round's content commit (R201 row 2999 == e50ba30,
R202 row 3002 == 549b8b0, R203 row 3005 == 818f027, R204 row 3008 ==
df30756, R205 row 3011 == 004cf47, R206 row 3014 == 0db08af, R207 row 3017
== a89a1cf, R208 row 3020 == c663140, R209 row 3023 == a10f9f5, R210 row
3026 == a96f796, R211 row 3029 == dd853fe, R212 row 3032 == c77587a,
R213 row 3035 == 2ce013b, R214 row 3038 == 6127a16, R215 row 3041 ==
dd19bba, R216 row 3044 == af6e949, R217 row 3047 == a24895e, R218 row
3050 == a82ca70, R219 row 3053 == f0051bd, R220 row 3056 == a19018c,
R221 row 3059 == 110aa76 -- all re-derived from git by THIS checker).
The R222 row therefore cites 3062 paths: 3061 at 37ea7ad + 1 new checker
file in the R223 content commit. That figure is verified in the R223
report after the content commit, not by this checker (it runs on the
working tree before the commit exists); this checker asserts only that
the row text cites 3062 and that the git diff at 37ea7ad is 3061.
(The `37ea7ad` hits in this file are the cover value, intentional -- in
this docstring and in the R222-row guard string citing "3061 at
37ea7ad", legitimate. The `a38b714` hit is likewise legitimate -- in the
R221-row guard string citing "3058 at a38b714". The `c38a4dc` hit is
likewise legitimate -- in the R220-row guard string citing "3055 at
c38a4dc". The `8f8b504` hit is likewise legitimate -- in the R219-row
guard string citing "3052 at 8f8b504". The `a74e9f4` hit is likewise
legitimate -- in the R218-row guard string citing "3049 at a74e9f4".
The `0a4d05a` hit is likewise legitimate -- in the R217-row guard string
citing "3046 at 0a4d05a". The `0de54fb` hit is likewise legitimate -- in
the R216-row guard string citing "3043 at 0de54fb". The `1e564a2` hit is
likewise legitimate -- in the R215-row guard string citing "3040 at
1e564a2". The `3de99c9` hit is likewise legitimate -- in the R214-row
guard string citing "3037 at 3de99c9".)
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
changed: 0, verified). R223 also corrects the body "Ghi chú" line: it
read "R158/R222 ... R76–R165 ... R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221" -- the range is
stale after R223 compacted R75 + R74; it now reads "R158/R223 ... R74–R165 ...
R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222".
R223 also corrects the R221 index row: it recorded only two versions of
the R221 payload (as-prepared 103,233 chars sha 85d22094; refreshed
~15:12 JST 103,124 chars sha ae8d1c56), but the main agent refreshed it
a third time ~15:50 JST (103,072 chars, sha 04eee785, mergeable
unstable -> clean) and presented a second widget (widget-7a108c57) that
was never tapped before R222 superseded it; the first widget
(widget-56770776) was tapped ~15:12 JST but its approval card expired
~15:49 JST (10th expiry), so R221 was NEVER POSTED. This checker
asserts the R221 row now carries the ĐÍNH CHÍNH R223 note with sha
04eee785.
Live-body read note: this round the GitHub API PR read succeeded via
the connector (pull_request_read, ~16:40 JST, read-only): title ends
"+ R222", head 37ea7ad, 635 commits / 3061 files / +298940, mergeable
null (GitHub computing at read time), mergeable_state clean at 37ea7ad,
live body 103,023 chars sha 1dd61afd, 0 U+FFFD, updated_at
2026-11-24T07:16:22Z -- R222 WAS POSTED LIVE ~16:16 JST (owner tapped
widget-d6b92d01 ~16:12 JST, approved at once), replacing R140 (live
since 2026-11-20). The issue read ALSO succeeded this round (connector
issue_read, 34 comments, updated_at 2026-11-13T19:24:49Z, latest ACK
6862732081) -- no new Codex/owner direction since Gói 39 (6815238814).
The R222 payload file was verified this round: its body sha 1dd61afd
matches the live body byte-exact.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "37ea7ad5aba4cafc94701232c857bcf5b0d8c6e8"
INTEGRATION = "f3db6b384886a59128328b8daa8c9eefc2d8f3ce"
CHECKER_NAME = "check_pr119_restructure_r223_v1.py"

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

    chk("index header coverage head == 37ea7ad", "(head `37ea7ad`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("110aa76", "37ea7ad"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 635/3061", "**635 commit / 3061 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R223 note", "Cập nhật R223" in index)
    chk("index R222 note kept", "Cập nhật R222" in index)
    chk("index R222 row label", "PR119 BODY RESTRUCTURE R222" in index)

    # R196 script-defect repairs, kept as regression guards: milestone 6
    # separate lines, heading own line, R167 note own line in ascending
    # position, R222 note clean.
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
    r222_note = [l for l in il if l.startswith("- Cập nhật R222 (2026-11-24):")]
    r222_note_ok = len(r222_note) == 1 and "- Cập nhật R167 " not in r222_note[0]
    repair_detail = (f"milestone6={milestone_ok} heading={heading_ok} "
                     f"r196clean={r196_clean} r167ascending={r167_ok} r222note={r222_note_ok}")
    chk("index R196-defect repairs (milestone 6 lines, heading, R167 ascending, R222 note)",
        milestone_ok and heading_ok and r196_clean and r167_ok and r222_note_ok,
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

    # R216 correction (carried from R216): the R215 row must cite cumulative 3041.
    r215_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R215 |")]
    r215_row_ok = (len(r215_row) == 1 and "cumulative 3041 paths" in r215_row[0])
    chk("index R215 row cumulative == 3041 (3040 at 1e564a2 + 1 checker)", r215_row_ok)

    # R217 correction (carried from R217): the R216 row must cite cumulative 3044.
    r216_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R216 |")]
    r216_row_ok = (len(r216_row) == 1 and "cumulative 3044 paths" in r216_row[0])
    chk("index R216 row cumulative == 3044 (3043 at 0de54fb + 1 checker)", r216_row_ok)

    # R218 correction (carried from R218): the R217 row must cite cumulative 3047.
    r217_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R217 |")]
    r217_row_ok = (len(r217_row) == 1 and "cumulative 3047 paths" in r217_row[0])
    chk("index R217 row cumulative == 3047 (3046 at 0a4d05a + 1 checker)", r217_row_ok)

    # R219 correction (carried from R219): the R218 row must cite cumulative 3050.
    r218_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R218 |")]
    r218_row_ok = (len(r218_row) == 1 and "cumulative 3050 paths" in r218_row[0])
    chk("index R218 row cumulative == 3050 (3049 at a74e9f4 + 1 checker)", r218_row_ok)

    # R220 correction (carried from R220): the R219 row must cite cumulative 3053.
    r219_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R219 |")]
    r219_row_ok = (len(r219_row) == 1 and "cumulative 3053 paths" in r219_row[0])
    chk("index R219 row cumulative == 3053 (3052 at 8f8b504 + 1 checker)", r219_row_ok)

    # R221 correction (carried from R221): the R220 row must cite cumulative 3056.
    r220_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R220 |")]
    r220_row_ok = (len(r220_row) == 1 and "cumulative 3056 paths" in r220_row[0])
    chk("index R220 row cumulative == 3056 (3055 at c38a4dc + 1 checker)", r220_row_ok)

    # R222 correction (carried from R222): the R221 row must cite cumulative 3059.
    r221_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R221 |")]
    r221_row_ok = (len(r221_row) == 1 and "cumulative 3059 paths" in r221_row[0])
    chk("index R221 row cumulative == 3059 (3058 at a38b714 + 1 checker)", r221_row_ok)

    # R223 correction (new this round): the R221 row must carry the
    # ĐÍNH CHÍNH R223 note with the third R221 payload version (sha 04eee785).
    r221_dc_ok = (len(r221_row) == 1 and "ĐÍNH CHÍNH R223" in r221_row[0]
                 and "04eee785" in r221_row[0]
                 and "KHÔNG BAO GIỜ ĐƯỢC ĐĂNG" in r221_row[0])
    chk("index R221 row carries ĐÍNH CHÍNH R223 (payload v3 sha 04eee785)", r221_dc_ok)

    # R223 row: must cite cumulative 3062 (3061 at 37ea7ad + 1 new checker
    # in the R223 content commit); the git figure is re-derived below.
    r222_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R222 |")]
    r222_row_ok = (len(r222_row) == 1 and "cumulative 3062 paths" in r222_row[0])
    chk("index R222 row cumulative == 3062 (3061 at 37ea7ad + 1 checker)", r222_row_ok)

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
                                         ("R214", "6127a16", 3038),
                                         ("R215", "dd19bba", 3041),
                                         ("R216", "af6e949", 3044),
                                         ("R217", "a24895e", 3047),
                                         ("R218", "a82ca70", 3050),
                                         ("R219", "f0051bd", 3053),
                                         ("R220", "a19018c", 3056),
                                         ("R221", "110aa76", 3059)):
        n = len(git("diff", "--name-only", BASE, content_sha).splitlines())
        chk(f"row-convention {row_n} cumulative {expected} == diff at {content_sha}",
            n == expected, str(n))

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..37ea7ad == 635", n_commits == 635, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..37ea7ad == 3061", n_files == 3061, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 298940, deletions 0",
        "298940 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 37ea7ad vs integration exit 0, tree 8cf6d9b7",
        mt.returncode == 0 and tree.startswith("8cf6d9b7"), tree)

    chk("body head line 37ea7ad/635/3061",
        "**Head: `37ea7ad` · 635 commit · 3061 file**" in body)
    chk("body has R222 paragraph", "- **PR119 BODY RESTRUCTURE R222**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R222",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R222" in title_line, title_line[-60:])
    chk("body title has full R93..R222 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 223)),
        "R94 restored, R222 added")
    chk("body index reference at 37ea7ad", "(head `37ea7ad`)" in body)
    chk("body R223 update note", "R223 (lượt cập nhật này)" in body)

    # Body "Ghi chú" line corrected this round: R158/R223, range R74-R165,
    # report list complete through R222, no double slash.
    note23 = [l for l in body.splitlines() if l.startswith("Ghi chú R158/")]
    note23_ok = (len(note23) == 1 and note23[0].startswith("Ghi chú R158/R223:")
                 and "R74–R165" in note23[0] and "R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222" in note23[0]
                 and "//" not in note23[0])
    chk("body Ghi-chú line corrected (R158/R223, R74-R165, list complete)", note23_ok)

    # R223 note + compaction: 92 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R223 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(74, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R222 after R221, before the compact block.
    bl = body.splitlines()
    i222 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R222**"))
    i221 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R221**"))
    order_ok = i222 == i221 + 1
    chk("body R223 note + R74-R165 compacted (92 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 92 and per_round_ok
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
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R222",
           "validator": "check_pr119_restructure_r223_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
