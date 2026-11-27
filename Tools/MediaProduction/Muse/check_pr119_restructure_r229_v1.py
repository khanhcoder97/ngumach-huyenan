#!/usr/bin/env python3
"""R229 validator: PR #119 delivery index + body v2 coverage through 9890c75.

Verifies the R229 restructure round: the delivery index now covers R228
(coverage head 9890c75, full SHA 9890c756b3acb39d7c314940485861116460b4f3),
and the repo body v2 file is synced to the R222 body v2 file + the R228
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R228 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R228 and
R229 note lines are present in the index.
The compaction window extends in R229: the "Khối mới nhất" paragraphs
R62-R165 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 104 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Collapsing the R63 + R62 paragraphs (493 and 493 chars ->
207 each -- the R76-R80 template measures 208, the R67/R66 lines measure
207; the checker asserts < 400, not an exact 208) plus the new R228
paragraph at 271 chars is what holds headroom this round (R228 warning:
headroom was 3,265 chars; this round's body is 101,507 chars, headroom
3,493). The DOUBLE compaction continues (R229 compacts R63 + R62 per
the R228 warning).
The R228 paragraph records that its payload was prepared but NOT posted
-- the live-body state is already recorded in the head line and in the
R228 index row -- so the post-push payload refresh (+~60 chars,
R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228
lesson) still lands under the ceiling.
R230 warning: headroom after R229 is 3,493 chars; the double compaction
bought back 572 chars against a 271-char new paragraph; keep compacting
two paragraphs a round (R61 + R60 next) or the body crosses 105,000
within a few rounds if the head line grows again with honest live-read
disclosures.
The full paragraphs in "Khối mới nhất" stay in ascending order (R166..R228), with
the new paragraph after R227 and before the compact block.
The R229 payload should be ~117,000 bytes, well under the 131,072
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
R221 row 3059 == 110aa76, R222 row 3062 == 25f18d0, R223 row 3065 ==
e14c586, R224 row 3068 == 8678714, R225 row 3071 == 8a5f422, R226 row
3074 == ba9e702, R227 row 3077 == 2938722 -- all re-derived from git by THIS checker).
The R228 row therefore cites 3080 paths: 3079 at 9890c75 + 1 new checker
file in the R229 content commit. That figure is verified in the R229
report after the content commit, not by this checker (it runs on the
working tree before the commit exists); this checker asserts only that
the row text cites 3080 and that the git diff at 9890c75 is 3079.
(The `9890c75` hits in this file are the cover value, intentional -- in
this docstring and in the R228-row guard string citing "3079 at
9890c75", legitimate. The `dbee5c5` hits are likewise legitimate -- in
the docstring explaining the previous cover value, intentional, and the
R227-row guard string citing "3076 at dbee5c5". The `556d3ec` hits are
likewise legitimate -- in the docstring explaining the previous cover
value, intentional, and the R226-row guard string citing "3073 at
556d3ec". The `2861100` hits are likewise legitimate -- in the docstring
explaining the previous cover value, intentional, and the R225-row guard
string citing "3070 at 2861100". The `1700859` hits are likewise
legitimate -- in the docstring explaining the previous cover value,
intentional, and the R224-row guard string citing "3067 at 1700859".
The `e07fe1e` hits are likewise legitimate -- in the docstring
explaining the previous cover value, intentional, and the R223-row guard
string citing "3064 at e07fe1e". The `37ea7ad` hit is likewise
legitimate -- in the R222-row guard string citing "3061 at 37ea7ad".
The `a38b714` hit is likewise legitimate -- in the R221-row guard
string citing "3058 at a38b714". The `c38a4dc` hit is likewise
legitimate -- in the R220-row guard string citing "3055 at c38a4dc".
The `8f8b504` hit is likewise legitimate -- in the R219-row guard
string citing "3052 at 8f8b504". The `a74e9f4` hit is likewise
legitimate -- in the R218-row guard string citing "3049 at a74e9f4".
The `0a4d05a` hit is likewise legitimate -- in the R217-row guard
string citing "3046 at 0a4d05a". The `0de54fb` hit is likewise
legitimate -- in the R216-row guard string citing "3043 at 0de54fb".
The `1e564a2` hit is likewise legitimate -- in the R215-row guard
string citing "3040 at 1e564a2". The `3de99c9` hit is likewise
legitimate -- in the R214-row guard string citing "3037 at 3de99c9".)
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
changed: 0, verified). R229 also corrects the body "Ghi chú" line: it
read "R158/R228 ... R65–R165 ... R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227"
-- the range is stale after R229 compacted R63 + R62; it now reads
"R158/R229 ... R63–R165 ...
R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228".
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
the connector (pull_request_read, ~22:44 JST, read-only): title ends
"+ R222", head 9890c75, 647 commits / 3079 files / +304692, mergeable
null (GitHub computing at read time), mergeable_state clean at 9890c75,
live body 103,023 chars sha 1dd61afd, 0 U+FFFD, updated_at
2026-11-24T12:52:04Z -- changed vs the R228 read (R228 push updated the
head; the body bytes are unchanged, still R222, posted live ~16:16 JST,
replacing R140). The issue read ALSO succeeded this round (connector
issue_read, 34 comments, updated_at 2026-11-13T19:24:49Z, latest ACK
6862732081) -- no new Codex/owner direction since Gói 39 (6815238814).
The R228 payload file was verified this round: main + .bak
byte-identical (sha256 7be53401), body sha b09c03ce, 101,795 chars, JSON
116,454 bytes; it is NOT posted -- the live body is still R222. Note:
the R228 payload's own head line (read ~21:52 JST) said mergeable_state
clean at 9890c75; this round's fresh read ~22:44 JST agrees (clean) --
the honest wording is the fresh read, not the payload's older one.
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "9890c756b3acb39d7c314940485861116460b4f3"
INTEGRATION = "f3db6b384886a59128328b8daa8c9eefc2d8f3ce"
CHECKER_NAME = "check_pr119_restructure_r229_v1.py"

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

    chk("index header coverage head == 9890c75", "(head `9890c75`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("2938722", "9890c75"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 647/3079", "**647 commit / 3079 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R229 note", "Cập nhật R229" in index)
    chk("index R228 note kept", "Cập nhật R228" in index)
    chk("index R228 row label", "PR119 BODY RESTRUCTURE R228" in index)

    # R196 script-defect repairs, kept as regression guards: milestone 6
    # separate lines, heading own line, R167 note own line in ascending
    # position, R228 note clean.
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
    r228_note = [l for l in il if l.startswith("- Cập nhật R228 (2026-11-24):")]
    r228_note_ok = len(r228_note) == 1 and "- Cập nhật R167 " not in r228_note[0]
    repair_detail = (f"milestone6={milestone_ok} heading={heading_ok} "
                     f"r196clean={r196_clean} r167ascending={r167_ok} r228note={r228_note_ok}")
    chk("index R196-defect repairs (milestone 6 lines, heading, R167 ascending, R228 note)",
        milestone_ok and heading_ok and r196_clean and r167_ok and r228_note_ok,
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

    # R223 correction (carried from R223): the R221 row must carry the
    # ĐÍNH CHÍNH R223 note with the third R221 payload version (sha 04eee785).
    r221_dc_ok = (len(r221_row) == 1 and "ĐÍNH CHÍNH R223" in r221_row[0]
                 and "04eee785" in r221_row[0]
                 and "KHÔNG BAO GIỜ ĐƯỢC ĐĂNG" in r221_row[0])
    chk("index R221 row carries ĐÍNH CHÍNH R223 (payload v3 sha 04eee785)", r221_dc_ok)

    # R223 row: must cite cumulative 3062 (3061 at 37ea7ad + 1 new checker
    # in the R223 content commit).
    r222_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R222 |")]
    r222_row_ok = (len(r222_row) == 1 and "cumulative 3062 paths" in r222_row[0])
    chk("index R222 row cumulative == 3062 (3061 at 37ea7ad + 1 checker)", r222_row_ok)

    # R224 row: must cite cumulative 3065 (3064 at e07fe1e + 1 new checker
    # in the R224 content commit).
    r223_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R223 |")]
    r223_row_ok = (len(r223_row) == 1 and "cumulative 3065 paths" in r223_row[0])
    chk("index R223 row cumulative == 3065 (3064 at e07fe1e + 1 checker)", r223_row_ok)

    # R225 row: must cite cumulative 3068 (3067 at 1700859 + 1 new checker
    # in the R225 content commit).
    r224_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R224 |")]
    r224_row_ok = (len(r224_row) == 1 and "cumulative 3068 paths" in r224_row[0])
    chk("index R224 row cumulative == 3068 (3067 at 1700859 + 1 checker)", r224_row_ok)

    # R226 row: must cite cumulative 3071 (3070 at 2861100 + 1 new checker
    # in the R226 content commit).
    r225_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R225 |")]
    r225_row_ok = (len(r225_row) == 1 and "cumulative 3071 paths" in r225_row[0])
    chk("index R225 row cumulative == 3071 (3070 at 2861100 + 1 checker)", r225_row_ok)

    # R227 row: must cite cumulative 3074 (3073 at 556d3ec + 1 new checker
    # in the R227 content commit).
    r226_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R226 |")]
    r226_row_ok = (len(r226_row) == 1 and "cumulative 3074 paths" in r226_row[0])
    chk("index R226 row cumulative == 3074 (3073 at 556d3ec + 1 checker)", r226_row_ok)

    # R228 row: must cite cumulative 3077 (3076 at dbee5c5 + 1 new checker
    # in the R228 content commit).
    r227_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R227 |")]
    r227_row_ok = (len(r227_row) == 1 and "cumulative 3077 paths" in r227_row[0])
    chk("index R227 row cumulative == 3077 (3076 at dbee5c5 + 1 checker)", r227_row_ok)

    # R229 row (new this round): must cite cumulative 3080 (3079 at 9890c75
    # + 1 new checker in the R229 content commit); the git figure is
    # re-derived below.
    r228_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R228 |")]
    r228_row_ok = (len(r228_row) == 1 and "cumulative 3080 paths" in r228_row[0])
    chk("index R228 row cumulative == 3080 (3079 at 9890c75 + 1 checker)", r228_row_ok)

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
                                         ("R221", "110aa76", 3059),
                                         ("R222", "25f18d0", 3062),
                                         ("R223", "e14c586", 3065),
                                         ("R224", "8678714", 3068),
                                         ("R225", "8a5f422", 3071),
                                         ("R226", "ba9e702", 3074),
                                         ("R227", "2938722", 3077)):
        n = len(git("diff", "--name-only", BASE, content_sha).splitlines())
        chk(f"row-convention {row_n} cumulative {expected} == diff at {content_sha}",
            n == expected, str(n))

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..9890c75 == 647", n_commits == 647, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..9890c75 == 3079", n_files == 3079, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 304692, deletions 0",
        "304692 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 9890c75 vs integration exit 0, tree 7c87f4db",
        mt.returncode == 0 and tree.startswith("7c87f4db"), tree)

    chk("body head line 9890c75/647/3079",
        "**Head: `9890c75` · 647 commit · 3079 file**" in body)
    chk("body has R228 paragraph", "- **PR119 BODY RESTRUCTURE R228**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R228",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R228" in title_line, title_line[-60:])
    chk("body title has full R93..R228 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 229)),
        "R94 restored, R228 added")
    chk("body index reference at 9890c75", "(head `9890c75`)" in body)
    chk("body R229 update note", "R229 (lượt cập nhật này)" in body)

    # Body "Ghi chú" line corrected this round: R158/R229, range R63-R165,
    # report list complete through R228, no double slash.
    note25 = [l for l in body.splitlines() if l.startswith("Ghi chú R158/")]
    note25_ok = (len(note25) == 1 and note25[0].startswith("Ghi chú R158/R229:")
                 and "R63–R165" in note25[0] and "R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228" in note25[0]
                 and "//" not in note25[0])
    chk("body Ghi-chú line corrected (R158/R229, R63-R165, list complete)", note25_ok)

    # R229 note + compaction: 104 compact lines, each < 400 chars, body < 105k chars.
    compact_ok = "R229 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(62, 166):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R228 after R227, before the compact block.
    bl = body.splitlines()
    i228 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R228**"))
    i227 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R227**"))
    order_ok = i228 == i227 + 1
    chk("body R229 note + R62-R165 compacted (104 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 104 and per_round_ok
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
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R228",
           "validator": "check_pr119_restructure_r229_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
