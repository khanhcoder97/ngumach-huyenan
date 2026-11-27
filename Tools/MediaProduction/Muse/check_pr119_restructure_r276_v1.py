#!/usr/bin/env python3
"""R276 validator: PR #119 delivery index + body v2 coverage through 7e44e0c.

Verifies the R276 restructure round: the delivery index now covers R275
(coverage head 7e44e0c, full SHA 7e44e0c06bb4bb05eaabcc8368e95982c5a287a4),
and the repo body v2 file is synced to the R263 body v2 file + the R275
block. All figures re-derived from git, never copied from the documents.
Also guards the title-line sequence: the R97 round dropped "R94" from the
body v2 title when editing by hand, so this checker asserts the full
R93..R275 run is present in the title line. It also guards the R140
update-note defect (a content commit replaced the previous "Cập nhật"
note line instead of appending after it) by asserting both the R275 and
R276 note lines are present in the index.
The compaction window extends in R276: the "Khối mới nhất" paragraphs
R2-R183 remain collapsed to one compact line each (full detail stays in
the delivery index table rows); this checker asserts all 182 compact lines
still exist, each under 400 chars, and the body total stays under
105,000 chars. Compacting the R183 paragraph (440 chars -> 214) plus the new R275 paragraph at 270
chars (+1 line break = 271) is what holds headroom this round (R275
warning: headroom was 10,210 chars; this round's body is 94,898 chars,
headroom 10,102). The SINGLE compaction continues (R276 compacts R183
per the R275 warning; single compaction from R261 -- R166 + R167 were
the last pair). The head line is UNCHANGED at 1,228 chars this round
(delta 0, measured -- the tenth round in a row; the fresh connector read returns mergeable_state
clean directly, mergeable null -- GitHub has not recomputed the flag;
the head line now cites the new coverage head + counts).
The net body delta is +108: -226 (R183 compaction)
+ 271 (new paragraph) + 28 (trail append) + 30 (title
append) + 5 (Ghi-chú list append "/R275") + 0 (Ghi-chú range
"R3–R182" -> "R3–R183", same length) + 0 (head line) = +108,
measured by the dry-run projection, not hand-counted.
The R274 paragraph records that its payload was prepared after the R274
push (94,550 chars, sha c241a8ef; JSON 105,567 bytes) -- the live-body
state is already recorded in the head line and in the R246 index row --
so the post-push payload refresh (+23 chars measured at R238, R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237/R238/R239/R240/R241/R242/R243/R244/R245/R246/R247/R248/R249/R250/R251/R252/R253/R254/R255/R256/R257/R258/R259/R260/R261/R262/R263/R264/R265/R266/R267/R268/R269/R270/R271/R272/R273/R274
lesson) still lands under the ceiling.
R276 warning: headroom after R276 is 10,102 chars; the single compaction
continues (R183, -226 against the 271 new paragraph); from R277
compact ONE paragraph a round (R184 next -- single compaction) or the body crosses 105,000
within a few rounds if the head line grows again with honest live-read
disclosures.
The full paragraphs in "Khối mới nhất" stay in ascending order (R184..R275), with
the new paragraph after R274 and before the compact block.
The R276 payload should be ~108,000 bytes, well under the 131,072
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
3074 == ba9e702, R227 row 3077 == 2938722, R228 row 3080 == 7aa25a8,
R229 row 3083 == 644d4ab, R230 row 3086 == 9482f4d, R231 row 3089 ==
c3a4eec, R232 row 3092 == 233f0b5, R233 row 3095 == b50891a, R234 row
3098 == db681a3, R235 row 3101 == 539feb0, R236 row 3104 == 5b80666,
R237 row 3107 == e79db7b, R238 row 3110 == 08dd58b, R239 row 3113 ==
928a525, R240 row 3116 == dc9331a, R241 row 3119 == 91a543e, R242 row 3122 == e61a658, R243 row 3125 == 44f1017, R244 row 3128 == ff7f373, R245 row 3131 == 6869aa1, R246 row 3134 == c919f88, R247 row 3137 == cf24619, R248 row 3140 == aa0eef6, R249 row 3143 == 8bebd8a, R250 row 3146 == a6319ed, R251 row 3149 == fa41682, R252 row 3152 == cec686f, R253 row 3155 == a8fb12d, R254 row 3158 == c15258e, R255 row 3161 == e53b835, R256 row 3164 == e41cfda, R257 row 3167 == 134ebaa, R258 row 3170 == 15ad480, R259 row 3173 == f4f9255, R260 row 3176 == 2beeb78, R261 row 3179 == ffaaf3b, R262 row 3182 == e373cb5, R263 row 3185 == 7ac9433, R264 row 3188 == ecee5f7, R265 row 3191 == e444f0c, R266 row 3194 == 9ce3e24, R267 row 3197 == b062dd1, R268 row 3200 == 75e1d55, R269 row 3203 == 3ae052f, R270 row 3206 == 16dfcfe, R271 row 3209 == 312d680, R272 row 3212 == 5dc1302, R273 row 3215 == 56926f3, R274 row 3218 == c7117ef -- all
re-derived from git by THIS checker).
The R275 row therefore cites 3221 paths: 3220 at 7e44e0c + 1 new checker
file in the R276 content commit. That figure is verified in the R276
report after the content commit, not by this checker (it runs on the
working tree before the commit exists); this checker asserts only that
the row text cites 3221 and that the git diff at 7e44e0c is 3220.
(The `7e44e0c` hits in this file are the cover value, intentional -- in the docstring (the cover
line, the coverage-head line, the R275-row note (2 lines), the live-body note (3 lines), the
lesson-11 text, the lesson-45 text), the definition, the checks, the R275-row guard comment, the
check name and the body head-line string. The `c7117ef` hits are likewise legitimate -- in the
docstring (the row-convention list, the live-body note (2 lines), the lesson-11 text, the lesson-45
text), the checks and the code row-convention tuple R274. The `2de586d` hits are likewise legitimate
-- in the docstring (the live-body note, the lesson-44 text), the R274-row guard comment and the
check name. The `56926f3` hits are likewise legitimate -- in the docstring (the row-convention list,
the lesson-44 text) and the code row-convention tuple R273. The `a7c0ae5` hits are likewise
legitimate -- in the docstring (the lesson-43 text). The `5dc1302` hits are likewise legitimate --
in the docstring (the row-convention list, the lesson-43 text) and the code row-convention tuple
R272. The `e71bce5` hits are likewise legitimate -- in the docstring (the lesson-42 text). The
`312d680` hits are likewise legitimate -- in the docstring (the row-convention list, the lesson-42
text) and the code row-convention tuple R271. The `ce57ceb` hits are likewise legitimate -- in the
docstring (the lesson-41 text). The `16dfcfe` hits are likewise legitimate -- in the docstring (the
row-convention list, the lesson-41 text) and the code row-convention tuple R270. The `2482e3b` hits
are likewise legitimate -- in the docstring (the lesson-40 text). The `3ae052f` hits are likewise
legitimate -- in the docstring (the row-convention list, the lesson-40 text) and the code
row-convention tuple R269. The `6b040c7` hits are likewise legitimate -- in the docstring (the
lesson-39 text). The `75e1d55` hits are likewise legitimate -- in the docstring (the row-convention
list, the lesson-39 text, the lesson-40 text) and the code row-convention tuple R268. The `2718ea5`
hits are likewise legitimate -- in the docstring (the lesson-38 text). The `b062dd1` hits are
likewise legitimate -- in the docstring (the row-convention list, the lesson-38 text) and the code
row-convention tuple R267. The `1bf2318` hits are likewise legitimate -- in the docstring (the
lesson-37 text). The `9ce3e24` hits are likewise legitimate -- in the docstring (the row-convention
list, the lesson-37 text) and the code row-convention tuple R266. The `7db0fc8` hits are likewise
legitimate -- in the docstring (the lesson-36 text). The `e444f0c` hits are likewise legitimate --
in the docstring (the row-convention list, the lesson-36 text) and the code row-convention tuple
R265. The `5584a8f` hits are likewise legitimate -- in the docstring (the lesson-35 text). The
`ecee5f7` hits are likewise legitimate -- in the docstring (the row-convention list, the lesson-35
text) and the code row-convention tuple R264. The `451147b` hit is likewise legitimate -- in the
docstring (the lesson-35 text). The `7ac9433` hits are likewise legitimate -- in the docstring (the
row-convention list) and the code row-convention tuple R263. The `daf9540` hits are likewise
legitimate -- in the docstring (the lesson-33 text, the lesson-35 text, the lesson-36 text, the
lesson-37 text, the lesson-38 text, the lesson-39 text, the lesson-40 text, the lesson-41 text). The
`e373cb5` hits are likewise legitimate -- in the docstring (the row-convention list, the lesson-33
text, the lesson-35 text, the lesson-36 text, the lesson-37 text, the lesson-38 text, the lesson-39
text, the lesson-40 text, the lesson-41 text) and the code row-convention tuple R262. The `ffaaf3b`
hits are likewise legitimate -- in the docstring (the row-convention list) and the code
row-convention tuple R261. The `2beeb78` hits are likewise legitimate -- in the docstring (the
row-convention list) and the code row-convention tuple R260. The `f4f9255` hits are likewise
legitimate -- in the docstring (the row-convention list) and the code row-convention tuple R259. The
`34f70c2` hit is likewise legitimate -- in the docstring (the lesson-30 text). The `15ad480` hits
are likewise legitimate -- in the docstring (the row-convention list) and the code row-convention
tuple R258. The `713b3dc` hits are likewise legitimate -- in the docstring (the lesson-30 text). The
`134ebaa` hits are likewise legitimate -- in the docstring (the row-convention list) and the code
row-convention tuple R257. The `34ed40f` hits are likewise legitimate -- in the docstring (the
lesson-27 text (2 lines)). The `e41cfda` hits are likewise legitimate -- in the docstring (the
row-convention list, the lesson-27 text) and the code row-convention tuple R256. The `46fde45` hits
are likewise legitimate -- in the docstring (the lesson-26 text), the R256-row guard comment and the
check name. The `e53b835` hits are likewise legitimate -- in the docstring (the row-convention list)
and the code row-convention tuple R255. The `855d6f0` hits are likewise legitimate -- in the
docstring (the lesson-24 text (3 lines)), the R255-row guard comment and the check name. The
`c15258e` hits are likewise legitimate -- in the docstring (the row-convention list, the lesson-24
text) and the code row-convention tuple R254. The `0877855` hits are likewise legitimate -- in the
docstring (the lesson-22 text (3 lines)), the R254-row guard comment and the check name. The
`a8fb12d` hits are likewise legitimate -- in the docstring (the row-convention list, the lesson-22
text) and the code row-convention tuple R253. The `041c185` hits are likewise legitimate -- in the
docstring (the lesson-21 text), the R253-row guard comment and the check name. The `cec686f` hits
are likewise legitimate -- in the docstring (the row-convention list) and the code row-convention
tuple R252. The `8e4d8ac` hits are likewise legitimate -- in the docstring (the lesson-21 text), the
R252-row guard comment and the check name. The `fa41682` hits are likewise legitimate -- in the
docstring (the row-convention list) and the code row-convention tuple R251. The `7ca1f05` hits are
likewise legitimate -- in the R251-row guard comment and the check name. The `a6319ed` hits are
likewise legitimate -- in the docstring (the row-convention list) and the code row-convention tuple
R250. The `1281cde` hits are likewise legitimate -- in the R250-row guard comment and the check
name. The `8bebd8a` hits are likewise legitimate -- in the docstring (the row-convention list) and
the code row-convention tuple R249. The `4ad9429` hits are likewise legitimate -- in the docstring
(the lesson-17 text), the R249-row guard comment and the check name. The `aa0eef6` hits are likewise
legitimate -- in the docstring (the row-convention list) and the code row-convention tuple R248. The
`24037b7` hits are likewise legitimate -- in the docstring (the lesson-16 text), the R248-row guard
comment and the check name. The `cf24619` hits are likewise legitimate -- in the docstring (the
row-convention list) and the code row-convention tuple R247. The `cd4f7b0` hits are likewise
legitimate -- in the docstring (the lesson-16 text), the R247-row guard comment and the check name.
The `c919f88` hits are likewise legitimate -- in the docstring (the row-convention list, the
lesson-6 text) and the code row-convention tuple R246. The `1240497` hits are likewise legitimate --
in the docstring (the lesson-6 text, the lesson-15 text), the R246-row guard comment and the check
name. The `6869aa1` hits are likewise legitimate -- in the docstring (the row-convention list) and
the code row-convention tuple R245. The `4fc20b6` hits are likewise legitimate -- in the docstring
(the lesson-15 text), the R245-row guard comment and the check name. The `ff7f373` hits are likewise
legitimate -- in the docstring (the row-convention list) and the code row-convention tuple R244. The
`bbddba5` hits are likewise legitimate -- in the R244-row guard comment and the check name. The
`44f1017` hits are likewise legitimate -- in the docstring (the row-convention list) and the code
row-convention tuple R243. The `214eb99` hits are likewise legitimate -- in the R243-row guard
comment and the check name. The `e61a658` hits are likewise legitimate -- in the docstring (the
row-convention list) and the code row-convention tuple R242. The `26c0cc1` hits are likewise
legitimate -- in the R242-row guard comment and the check name. The `91a543e` hits are likewise
legitimate -- in the docstring (the row-convention list) and the code row-convention tuple R241. The
`f021c08` hits are likewise legitimate -- in the docstring (the R243 correction), the R242-row guard
comment and the check name. The `dc9331a` hits are likewise legitimate -- in the docstring (the
row-convention list) and the code row-convention tuple R240. The `66cea79` hits are likewise
legitimate -- in the R241-row guard comment and the check name. The `928a525` hits are likewise
legitimate -- in the docstring (the row-convention list) and the code row-convention tuple R239. The
`3c076bf` hits are likewise legitimate -- in the docstring (the R241 correction, the lesson-8 text),
the R240-row guard comment and the check name. The `10eebd3` hits are likewise legitimate -- in the
R239-row guard comment and the check name. The `08dd58b` hits are likewise legitimate -- in the
docstring (the row-convention list) and the code row-convention tuple R238. The `e79db7b` hits are
likewise legitimate -- in the docstring (the row-convention list) and the code row-convention tuple
R237. The `5b80666` hits are likewise legitimate -- in the docstring (the row-convention list) and
the code row-convention tuple R236. The `6db62e0` hits are likewise legitimate -- in the R237-row
guard comment and the check name. The `d5f1db3` hits are likewise legitimate -- in the R236-row
guard comment and the check name. The `539feb0` hits are likewise legitimate -- in the docstring
(the row-convention list) and the code row-convention tuple R235. The `db681a3` hits are likewise
legitimate -- in the docstring (the row-convention list) and the code row-convention tuple R234. The
`b50891a` hits are likewise legitimate -- in the docstring (the row-convention list) and the code
row-convention tuple R233. The `233f0b5` hits are likewise legitimate -- in the docstring (the
row-convention list), the code, the check name and the code row-convention tuple R232. The `33962fd`
hits are likewise legitimate -- in the docstring (the lesson-5 text (2 lines)), the R234-row guard
comment and the check name. The `29727d4` hits are likewise legitimate -- in the docstring (the
edit-script lessons), the code and the check name. The `9861875` hits are likewise legitimate -- in
the code and the check name. The `8310e5d` hits are likewise legitimate -- in the code and the check
name. The `9890c75` hits are likewise legitimate -- in the code and the check name. The `dbee5c5`
hits are likewise legitimate -- in the R228-row guard comment and the check name. The `556d3ec` hits
are likewise legitimate -- in the R227-row guard comment and the check name. The `2861100` hits are
likewise legitimate -- in the R226-row guard comment and the check name. The `1700859` hits are
likewise legitimate -- in the R225-row guard comment and the check name. The `e07fe1e` hits are
likewise legitimate -- in the R224-row guard comment and the check name. The `37ea7ad` hits are
likewise legitimate -- in the R223-row guard comment and the check name. The `a38b714` hit is
likewise legitimate -- in the check name. The `c38a4dc` hit is likewise legitimate -- in the check
name. The `8f8b504` hit is likewise legitimate -- in the check name. The `a74e9f4` hit is likewise
legitimate -- in the check name. The `0a4d05a` hit is likewise legitimate -- in the check name. The
`0de54fb` hit is likewise legitimate -- in the check name. The `1e564a2` hit is likewise legitimate
-- in the check name. The `3de99c9` hit is likewise legitimate -- in the check name. The `7bf9212`
hits are likewise legitimate -- in the R238-row guard comment and the check name.)
R198 .bak correction (kept as a regression guard): the R198 index
row carries the ĐÍNH CHÍNH R200 note (the `.bak-prepost-20261123`
directory did NOT exist on disk when R199 checked; R199 created it).
The same unverifiable claim also appears in rows R137-R197; those
historical rows are left as-is (disclosed in the R200 report), only the
R198 row (the round folded in at R200) is corrected.
R196 script-defect repairs (kept as regression guards by this checker):
the R196 edit script dropped trailing "\n" on whole-line replacements
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
changed: 0, verified). R276 also corrects the body "Ghi chú" line: it
read "R158/R275 ... R3–R182 ...
R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237/R238/R239/R240/R241/R242/R243/R244/R245/R246/R247/R248/R249/R250/R251/R252/R253/R254/R255/R256/R257/R258/R259/R260/R261/R262/R263/R264/R265/R266/R267/R268/R269/R270/R271/R272/R273/R274"
-- the range is stale after R276 compacted R183;
it now reads "R158/R276 ... R3–R183 ...
R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237/R238/R239/R240/R241/R242/R243/R244/R245/R246/R247/R248/R249/R250/R251/R252/R253/R254/R255/R256/R257/R258/R259/R260/R261/R262/R263/R264/R265/R266/R267/R268/R269/R270/R271/R272/R273/R274/R275".
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
R241 correction (carried from R241): the R239 index row now carries the
ĐÍNH CHÍNH R241 note: the main R239 payload was refreshed by the main
agent ~09:56 JST (mergeable unstable -> clean at 3c076bf), so main
(99,073 chars, sha 1e38e781) differs from its .bak as-built copy
(99,138 chars, sha 8ef82135) in exactly the head line. The R239 row
keeps its as-built figures; this checker asserts the row carries the
ĐÍNH CHÍNH R241 note with sha 1e38e781 (R221->R223 precedent).
R242 correction (carried from R242): the R36 full paragraph was silently
deleted at the R47 content commit (1a601be) -- verified from git: the
paragraph exists at 9d45aae (R37 content, 493 chars, content 386216b,
report/head 9ec1fd9, checker R36 PASS 17/17) and is gone at 1a601be,
with no correction note in any later round; no checker ever asserted it,
because the compact loop only covers R38+ and the title sequence only
covers R93+. R242 restores it directly in compact form (207 chars, same
template as the R37-R165 compact lines) right after the R37 compact
line; the compact block is now R36-R165 (130 lines). This checker
asserts the restored R36 compact line exists with content sha 386216b
and head 9ec1fd9, and the per-round compact loop covers R34-R165.
R243 correction (carried from R243): the R241 index row now carries the
ĐÍNH CHÍNH R242 note: the main R241 payload was refreshed by the main
agent ~11:54 JST (mergeable unstable -> clean at f021c08), so main
(98,615 chars, sha 83d221b8) differs from its .bak as-built copy
(98,680 chars, sha 48ee3a19) in exactly the head line -- verified from
disk this round (both payload files re-read, body lines differ in
exactly line 5), not from the R242 report alone. The R241 row keeps its
as-built figures; this checker asserts the row carries the ĐÍNH CHÍNH
R242 note with sha 83d221b8 (R221->R223 precedent).
R275 correction (carried from R275): the R274 body v2 "lượt cập nhật này"
sentence was advanced cleanly to R275 ("chính R275"); R276 advances it
cleanly to R276 ("chính R276"); this checker asserts the full corrected
sentence is present and the defective "chính R275" form is absent. (The
R238-defect history: R238's sentence read "2 commit của chính R237 sẽ
gộp" -- wrong, R237's commits were already folded by R238; R239 fixed
it, and the sentence has advanced cleanly every round since.)
Live-body read note: this round ran in ONE phase -- the live reads and
the index + body v2 edit, checker, commits, push and report all ran in
one pass (~08:40 JST fetch, ~08:42 JST PR read, ~08:42 JST issue read).
The fetch succeeded first try; remote head 7e44e0c, integration f3db6b3,
both unchanged.
The live reads used the GitHub connector (call-read-tool for both the PR
and the issue, HTTP 200): title ends "+ R263", head 7e44e0c,
741 commits / 3220 files / +387773, mergeable null (the `mergeable` key
was absent from the MCP response again, as in R275 -- "mergeable null"
is the established convention for this response shape), mergeable_state
clean at 7e44e0c (the R275 payload's post-push reads ~07:51 + ~07:52 JST
said unstable at c7117ef; its main was NOT refreshed -- main == .bak ==
2 .bak-prepost copies, verified from disk ~08:42 JST -- lesson 54a),
live body 94,825 chars sha 07316552, 0 U+FFFD -- byte-exact
with the R263 payload, updated_at 2026-11-26T22:54:48Z -- changed
from 22:06:20Z by the R275 report push, body unchanged, still R263.
The issue read ALSO used the connector (~08:42 JST, 34 comments, updated_at
2026-11-13T19:24:49Z, latest ACK 6862732081) -- no new Codex/owner
direction since Gói 39 (6815238814). Time labels are separated per step
this round (lesson 57a); no correction was needed this round -- the R275
report's figures re-verified clean (lesson 59).
The issue read passed `issue_number` first try this round (lesson 66
recorded in R273; no retry needed).
The R275 payload's post-push reads (~07:51 + ~07:52 JST) said unstable at
c7117ef (CI running on the new head, last clean 2de586d); its main was NOT
refreshed (main == .bak == 2 .bak-prepost copies, sha256 fb0d5958 -- the
.bak write was restored by r275_payload.py; lesson 39: refresh at
presentation; lesson 54a: measure main vs .bak from disk right before
writing the row).
The public API was not attempted this round (connector reads straight, as
in R275); the read path is recorded as actually used, not as the usual one.
The PR read's base.sha f3832338 is stale (an ancestor of the live
integration tip f3db6b3 per ls-remote -- the 2026-11-05 merge of PR #118);
the merge-tree check still runs against f3db6b3, as in every round.
The R275 payload was prepared after the R275 push (~07:53 JST, during
R275): main NOT refreshed (main == .bak == 2 .bak-prepost copies, body
94,683 chars, sha b172a58d, JSON 105,713 bytes, sha256 fb0d5958 -- .bak
write restored by r275_payload.py, verified from disk ~08:42 JST), title
765 chars ending "+ R275"; it is NOT posted -- the live body is still
R263. The R263 payload was verified in the R275 round and re-verified
this round (main REFRESHED at post time, posted body 94,825 chars, sha
07316552, JSON 105,986 bytes, sha256 57dcd516; main == .bak, all 3 copies
on disk = posted version), title 765 chars ending "+ R263"; it IS posted
-- the live body is now R263 (posted 16:08:41 JST, see above; the latest
refresh before R263 was the R260 main ~11:55 JST, recorded in the R260
index row with the R261 note).
Edit-script lessons this round (R242, kept as regression guards in the
edit script): (1) line_replace must check the NEW state first AND must
not treat a line sharing the old prefix as "both states" -- the counts
and mergeable lines share their prefix with the new line, so the guard
compares against the new line itself; (2) sub_once must check the NEW
string first for append-style edits where the new string contains the
old one -- the title append, the compaction trail and the Ghi-chu list
append all re-run to changed: 0 after the fix; (3) the dry-run
projection must be measured from the exact file bytes (trailing newline
included) -- the R243 dry-run projected 98,704 chars and the apply
wrote exactly that; (4) every edit must target the structure that is
written back -- the R233 edit script first applied the index title-head
edit via sub_once on a separate `index_text` string that is never joined
back, silently losing the edit (the file kept head `29727d4` in its
title); the idempotency re-run exposed it (changed: 1), and the fix
routes the title edit through `il` like every other index edit. The
checker is the backstop for this defect class (its "index header
coverage head" check would have failed the content commit).
(5) `find` prefixes must not contain the OLD state -- the R235 edit
script's first idempotency re-run crashed on the body head-line find
(`**Head: \`33962fd\``) because the applied line now starts with
`**Head: \`19e8f7c\``; the index title find had the same defect
(`(head \`33962fd\``). Fixed by finding on state-stable prefixes
(`**Head: \`` and `# MEDIA-02 — PR #119 Delivery Index (head`). And
`sub_line`'s new-state guard must be `if new in line: return 0` ALONE --
the first version (`new in line and old not in line`) let append-style
edits re-apply, because the new string contains the old one. After both
fixes the re-run reported changed: 0 on the first re-run.
(6) The R236 lesson held end to end, and the R237 edit script applied
cleanly on its first run (dry-run 99,606 = apply 99,606; idempotency
re-run changed: 0 on the first re-run after apply). The head-line delta
was measured +33 chars (1,028 -> 1,061), not hand-counted -- trust the
measured projection, never the hand-count. The R238 edit script applied
cleanly on its first run too (dry-run 99,355 = apply 99,355; idempotency
re-run changed: 0 on the first re-run after apply). The R239 edit script
applied cleanly on its first run too (dry-run 99,115 = apply 99,115;
idempotency re-run changed: 0 on the first re-run after apply). The
R239 checker passed 96/96 on its first run against the applied tree
(expected; verified below). The R240 edit script applied cleanly on its
first run too (dry-run 98,886 = apply 98,886; idempotency re-run changed:
0 on the first re-run after apply). The R240 checker passed 98/98 on its
first run against the applied tree (expected; verified below). The R241
edit script applied cleanly on its first run too (dry-run 98,668 = apply
98,668; idempotency re-run changed: 0 on the first re-run after apply).
The R241 checker passed 101/101 on its first run against the applied
tree (expected; verified below). The R242 edit script applied cleanly on
its first run too (dry-run 98,933 = apply 98,933; idempotency re-run
changed: 0 on the first re-run after apply). The R242 checker passed
104/104 on its first run against the applied tree (expected; verified
below). The R243 edit script applied cleanly on its first run too
(dry-run 98,704 = apply 98,704; idempotency re-run changed: 0 on the
first re-run after apply). The R243 checker passed 107/107 on its first run against the applied tree (verified below). The R245 edit script applied cleanly on its first run too
(dry-run 98,187 = apply 98,187; idempotency re-run changed: 0 on the
first re-run after apply). The R245 checker passed 111/111 on its first
run against the applied tree (verified below). The R246 edit script
applied cleanly on its first run too (dry-run 97,888 = apply 97,888;
idempotency re-run changed: 0 on the first re-run after apply). The R246
The R246 checker passed 113/113 on its first run against the applied
tree (verified below). The R247 edit script applied cleanly on its
first run too (dry-run 97,637 = apply 97,637; idempotency re-run
changed: 0 on the first re-run after apply, after three guard fixes
caught by the re-run itself: the title append's new-state check, the
chained timestamp sub made atomic, and the append-style guard reduced
The R247 checker passed 115/115 on its second run against the applied
tree (verified below) -- the first run failed 113/115 on the title-
sequence checks (the edit script had appended R247 to the body title
instead of R246; fixed, validation JSON deleted, re-run passed). The
R248 edit script applied cleanly on its first run too (dry-run 97,386
= apply 97,386; idempotency re-run changed: 0 on the first re-run after
apply). The R248 checker passed 118/118 on its second run against the
applied tree (verified below) -- the first run failed 117/118 on the
row-convention R246 check (the generator had cited the coverage head
1240497 instead of the content commit c919f88; fixed, validation JSON
deleted, re-run passed). The R249 edit script applied cleanly on its
first run too (dry-run 97,186 = apply 97,186; idempotency re-run changed:
0 on the first re-run after apply). The R249 checker passed 120/120 on its
first run against the applied tree (verified below). The R250 edit script
applied cleanly on its first run too (dry-run 96,847 = apply 96,847;
idempotency re-run changed: 0 on the first re-run after apply). The R250
checker is expected to pass 122/122 on its first run against the applied
tree (verified below). The R251 edit script applied cleanly on its first run too (dry-run 96,696 = apply 96,696; idempotency re-run changed: 0 on the first re-run after apply). The R251 checker is expected to pass 124/124 on its first run against the applied tree (verified below). The R252 edit script applied cleanly on its first run too (dry-run 96,456 = apply 96,456; idempotency re-run changed: 0 on the first re-run after apply). The R252 checker is expected to pass 126/126 on its first run against the applied tree (verified below). The R253 edit script applied cleanly on its first run too (dry-run 96,441 = apply 96,441; idempotency re-run changed: 0 on the first re-run after apply). The R253 checker is expected to pass 128/128 on its first run against the applied tree (verified below). The R254 edit script applied cleanly on its first run too (dry-run 96,548 = apply 96,548; idempotency re-run changed: 0 on the first re-run after apply). The R254 checker is expected to pass 130/130 on its first run against the applied tree (verified below). The R255 edit script was applied by the first phase (dry-run 96,378 = apply 96,378); the retry phase re-ran it for idempotency (changed: 0). The R255 checker is expected to pass 132/132 on its first run against the applied tree (verified below). The R256 edit script was applied by the first phase (dry-run 96,326 = apply 96,326); the retry phase re-ran it for idempotency (changed: 0). The R256 checker is expected to pass 134/134 on its first run against the applied tree (verified below). The R276 edit script was applied in a single phase (dry-run 94,898 = apply 94,898, idempotency re-run changed: 0). The R275 edit chain survived in goal hidden_files and the R276 round reused it (transform_edit_r276.py built directly from transform_edit_r275.py, hand-shifted with asserted pairs -- the R275_ROW block is derived from the source R274_ROW by asserted replacements instead of retyping; lesson 52) -- the lesson (44) correction of the R274 checker docstring stands (the R275 chain reused the R274 chain via transform_edit_r275.py; the R276 chain was hand-shifted from transform_edit_r275.py with asserted pairs, and the transform ran clean on the first try -- no assertion fired; see lesson (45)). The R276 checker is expected to pass 157/157 on its first run against the applied tree (verified below).
(7) NEW THIS ROUND (R237): the hand-count of the body delta was off by one
(-219 hand-counted vs -218 measured): inserting a paragraph adds its
line break too (+271 for a 270-char paragraph). The R236 report's "271
ký tự" paragraph figure already counts the line break the same way, so
the convention is consistent -- record the paragraph as 271 ký tự and
the line-break accounting in the report, not as a defect. R238's net
-251 was likewise measured, not hand-counted: the +5 Ghi-chú list
append ("/R237") is the term a hand-count would most likely miss.
R239's net -240 was likewise measured, not hand-counted. R240's net
-229 and R241's net -218 were likewise measured, not hand-counted.
R242's net +265 was likewise measured, not hand-counted: the +208
restored-line term (207 chars + its line break) is the term a
hand-count would most likely miss. R243's net -229 was likewise
measured, not hand-counted: the double compaction (-286 x2) against the
271 new paragraph, +37 trail, +30 title, +5 Ghi-chú list append, +0
head line. R244's net -229 was likewise measured, not hand-counted: the
double compaction (-286 x2) against the 271 new paragraph, +37 trail,
+30 title, +5 Ghi-chú list append, +0 head line. R245's net -288 was
likewise measured, not hand-counted: the double compaction (-286 -
345) against the 271 new paragraph, +37 trail, +30 title, +5 Ghi-chú
list append, +0 head line.
(8) NEW THIS ROUND (R241): the main agent may refresh a payload's head
line after the authoring round (mergeable state changes when CI
finishes): the R239 main payload was refreshed ~09:56 JST (unstable ->
clean at 3c076bf), so main no longer equals its .bak. A round that
notices a refresh must record BOTH versions with shas, sizes and read
time in its report and queue log, verify the refreshed body still
differs from the repo body v2 only in the head line, and must NOT claim
main == .bak after a refresh. The index-row correction belongs to the
next index update (R241), per the R221->R223 precedent -- the authoring
row keeps its as-built figures and is not silently rewritten. This
checker guards the correction with the ĐÍNH CHÍNH R241 check below.
(9) NEW THIS ROUND (R242): the brief's compaction pair (R37 + R36)
assumed both full paragraphs exist -- the R36 paragraph had been
deleted at 1a601be (R47 content) and no checker ever asserted it,
because the compact loop only covers R38+ and the title sequence only
covers R93+. Verify a compaction pair exists in the file before
assuming its lengths (R37 measured 493, R36 measured ABSENT); restore
a lost paragraph from git in compact form with its real content/report
shas rather than silently compacting one. This checker guards the
restoration with the R36 compact-line check below.
(10) NEW THIS ROUND (R242): the new-paragraph first draft measured 269
chars, not 270 -- fixed with a "checker: PASS" colon (+1); the edit
script asserts the exact 270 before writing, so a hand-count error
fails loudly instead of shipping a 1-char-short paragraph. Trust the
script's assert, never the hand-count.
(11) (carried from R243): the index row's "delta" cites the authoring
round's own content..report diff (c7117ef..7e44e0c: 2 paths, 694
insertions) -- NOT the difference between coverage-head insertion
totals (387773 - 385669 = 2104 is the wrong number; the report commit
adds only its own report md + validation json). The R274 report's
delta line already used the right figure; this round re-verified it
from git before writing the R275 row.
(12) (carried from R245): the compaction pair (R31 + R30) was verified
present before assuming its lengths -- R31 measured 493 chars but R30
measured 552 chars, NOT 493: the two paragraphs are NOT the same length
(R30 carries the longer quiet-hours payload sentence), so the double
compaction saved -286 + -345 = -631, not -572; never assume a pair shares
a length, measure both (R242 lesson 9 held proactively). The R244
payload was NOT built by the R244 round (its report promised it after
the push, but the round ended at the report commit + push); R245 built it
late (~14:47 JST, body 98,475 chars, sha 4a3befc6, JSON 111,339 bytes,
main == .bak sha256 4d89565d) so the R244 index row could cite real
figures -- a promised payload is a deliverable, not a footnote. No
payload refresh happened this round (main == .bak for R244, verified
from disk), so no ĐÍNH CHÍNH is needed -- unlike R241 (refreshed
~11:54 JST, corrected at R242/R243).
(13) NEW THIS ROUND (R246): the compaction pair (R29 + R28) was verified
present before assuming its lengths -- R29 measured 552 chars but R28
measured 504 chars, NOT 552: the two paragraphs are NOT the same length
(R29 carries the longer quiet-hours payload sentence), so the double
compaction saved -345 + -297 = -642, not -572; never assume a pair shares
a length, measure both (R242 lesson 9 held proactively). The R245
payload WAS built by its own round (after the R245 push ~14:58 JST,
body 98,199 chars, sha fa884493, JSON 110,933 bytes, main == .bak
sha256 a3135317) -- no late build needed this round, unlike R244. No
payload refresh happened this round (main == .bak for R245, verified
from disk), so no ĐÍNH CHÍNH is needed -- unlike R241 (refreshed
~11:54 JST, corrected at R242/R243).
(14) NEW THIS ROUND (R247): a live-body read that returns U+FFFD is a
transport artifact, not a body change -- the first PR read this round
returned 103,026 chars, sha 14e4afea, 5 U+FFFD, while the immediate
re-read returned 103,023 chars, sha 1dd61afd, 0 U+FFFD, byte-exact with
the R222 payload. The mangling hits multi-byte Vietnamese chars at
transport chunk boundaries ("ă" U+0103 decodes as 2 U+FFFD, "ủ" U+1EE7
as 3 U+FFFD); the same artifact appears in exec stdout display (the
index R246 note displayed three replacement characters after "đ" on
screen while the file on disk has 0 U+FFFD). Never conclude a file is
corrupt from displayed output -- verify from bytes (sha256, codepoints)
and re-read immediately; a first imperfect read is a transport
artifact, like the R98 replication-lag precedent.
(15) NEW THIS ROUND (R248): a head line can carry wrong figures that no
length assert catches -- the R247 body v2 head line shipped additions
327963 (stale, from head 4fc20b6) instead of 329707 at head 1240497,
because the edit script replaced head/commits/files but never the
additions figure, and Gói 39 ID 6835238814 instead of 6815238814,
because a scoped sub "681"->"683" (expect=3) consumed its third match
inside the ID. Both defects were confined to the head line (one
occurrence each, line 5); the R247 payload was built with the correct
figures, so the posted description would have been right, but the repo
file was wrong. Fix: replace additions explicitly with the full token
"additions 327963"->"additions 331522", fix the ID FIRST with the full
token "6835238814"->"6815238814", never use a bare 3-digit sub, and
this checker now asserts additions 331522 and ID 6815238814 in the head
line and the absence of 6835238814 and 327963 from the body.
(16) NEW THIS ROUND (R249): a round blocked by the execution-risk flag
leaves its payload to the retry run -- the R248 round stopped after the
pre-push fetch (flag #8), so its 2 commits stayed local and no R248
payload existed; the R249 retry run verified the remote head unchanged
(ls-remote + API read, cd4f7b0), pushed cd4f7b0..24037b7, then built the
R248 payload from the post-push head (97,398 chars, sha ae047027, JSON
109,761 bytes, main == .bak sha256 d9bf8543) before starting R249's own
round. A blocked round's payload is the retry run's first deliverable,
not the blocked round's footnote (R244 precedent: its payload was built
late by R245). The R248 index row records the flag + the retry with the
real push figures; this checker guards the row with the R248-row check
below.
Execution-risk flag note: the flag has appeared 10 times (R211, R213 x2,
R219, R231, R239, R240, R248, R253, R268) -- the 8th blocked the R248 round
after the pre-push fetch (its 2 commits stayed local; the R249 retry run
pushed them cleanly and built the R248 payload before starting R249) --
and the 10th appeared in the R268 round after the investigative fetch of
f3832338 (the PR read's stale base.sha, resolved as an old ancestor of
f3db6b3); no content from that fetch was checked out or used, and no R268
action was blocked -- the fetch itself completed and returned its output;
and none has appeared in the R276 round through the checker-generation
step; the decision whether to keep running
git/checker after the flag still awaits luồng chính/chủ dự án --
recorded here, not decided here. This R276 round proceeds on the queue's
explicit next-block assignment (R276) and the R219-blocked precedent (a
blocked run stops; the next scheduled run retries cleanly).
(17) NEW THIS ROUND (R250): a payload's head-line mergeable_state goes
stale the moment CI finishes after the build -- the R249 payload (built
~19:05 JST) honestly said unstable at 4ad9429, but this round's fresh API
read ~19:41 JST says clean at the same head (mergeable null in both reads
-- GitHub was still computing the mergeable flag; only mergeable_state
moved). The R250 head line drops the "CI đang chạy, lần clean gần nhất"
clause (delta -88, measured). A posted description's mergeable_state is
the build read's, not the tap read's -- refresh it at presentation if CI
has since finished (lesson 8/R241 refresh precedent), and record both
reads in the report.
(18) NEW THIS ROUND (R251): the PR's updated_at moves on every push
even when the body bytes are unchanged -- the R250 push moved updated_at
10:04:03Z -> 10:51:26Z while the body stayed sha 1dd61afd (still R222,
103,023 chars, 0 U+FFFD). Never read an updated_at change as a body
change; verify by body sha and length, and record both updated_at values
in the report so the next round can tell a push from a post.
(19) NEW THIS ROUND (R252): the R17 + R16 compaction pair does NOT
share a length -- R17 measured 453 chars but R16 measured 488 chars
(the R16 paragraph carries the longer card-expiry payload sentence),
so the double compaction saved -246 + -281 = -527, not -492; never
assume a pair shares a length, measure both (lesson 31, re-proven
this round). The connector read path changed this round:
call-read-tool rejected issue_read and pull_request_read (not in the
reviewed read-only set), so the live reads used the public GitHub API
(curl, HTTP 200, repo public) -- record the actual read path, not the
usual one.
(20) NEW THIS ROUND (R253): the R252 report projected the R252 payload
JSON at ~112,000 bytes "measured exactly at payload build", but the file
on disk is 108,402 bytes (sha256 b597575d, main == .bak byte-identical)
-- the projection was ~3,600 bytes high. The R252 index row now cites the
disk-measured 108,402 bytes. Never cite a projected payload size as
measured; the payload JSON is written after the report commit, so the
report can only project it -- the next round's row must re-measure from
disk. The connector read path worked again this round (call-read-tool
accepted issue_read and pull_request_read, unlike R252 where it rejected
them) -- record the actual read path each round, not the previous
round's.
(21) NEW THIS ROUND (R254): list_pull_requests returns no mergeable
fields -- when pull_request_read is rejected AND the public API is
rate-limited, the live read can still verify title/head/body bytes
but NOT mergeable_state. The head line must then carry the latest
point-in-time mergeable_state read (here the R253 post-push read
~00:23 JST: unstable at 041c185, last clean 8e4d8ac) with its read
time stated, plus the disclosure that this round's endpoint returns
no mergeable fields -- never present the carried value as a fresh
read, and never drop the mergeable clause to save head-line length
(the R250 precedent drops a stale clause only when a fresher read
exists).
(22) NEW THIS ROUND (R255): this round ran in two phases -- the first
phase (~01:40-02:20 JST) did the live reads and applied the index + body
v2 edit, then stopped without a checker, commit, push, queue entry or
report, leaving a dirty working tree; the retry phase (~02:40 JST)
re-derived every figure from git (699/3157/+345869 at 0877855,
merge-tree 99d65444, delta a8fb12d..0877855 2 paths / 1134 insertions)
and re-read the live PR + issue fresh (~02:44 JST, same values:
unstable at 0877855, updated_at 16:12:00Z, body sha 1dd61afd, 34
comments) before trusting the inherited edit, and re-ran the edit
script to confirm idempotency (changed: 0). Never adopt an uncommitted
working tree on its own evidence -- re-derive from git + live reads,
and record both phases in the report. The three "R253 builder" strings
the R254 round fixed by hand are now covered by explicit pairs in this
round's meta-transform (lesson 46), so the generated R255 maker cites
"R254 builder" throughout.
(23) NEW THIS ROUND (R255): a blind round shift does not advance DATES --
the generated R255 checker first failed 131/132 on the R196-defect
repair check because its r254_note find prefix carried the R253 note's
date (2026-11-25) while the R254 note is dated 2026-11-26 (the round
crossed midnight). The document was correct; the checker was wrong.
Fixed in the R255 maker's shift() (a targeted date replacement after
the filename chain) before any commit; the checker then passed 132/132.
Check every date-carrying find prefix when a round crosses midnight,
and never "fix" the document to match a failing checker without
checking which side is wrong first.
(24) NEW THIS ROUND (R256): this round ran in two phases again (see
lesson (22) for the R255 precedent) -- the first phase (~03:40-04:00
JST) did the live reads (connector, ~03:44 JST: clean at 855d6f0) and
applied the index + body v2 edit, then stopped without a checker,
commit, push, queue entry or report, leaving a dirty working tree; the
retry phase (~04:40 JST) re-derived every figure from git (701/3160/
+348177 at 855d6f0, merge-tree dd469bd9, delta c15258e..855d6f0 2 paths
/ 1208 insertions) and re-read the live PR + issue fresh via the public
API (~04:44 JST, same values: clean at 855d6f0, updated_at 18:24:58Z,
body sha 1dd61afd, 34 comments) before trusting the inherited edit, and
re-ran the edit script to confirm idempotency (changed: 0). The
connector refused issue_read and pull_request_read in the retry phase
(as in R252), so the retry read used curl against the public API (HTTP
200) -- record the actual read path each round, not the usual one.
Never adopt an uncommitted working tree on its own evidence -- re-derive
from git + live reads, and record both phases in the report.
(25) NEW THIS ROUND (R256): the net-delta components are NOT constants
-- the trail append is +35 this round, not +37: the sentence "R256 đã
gọn thêm các đoạn R9 + R8." is 2 chars shorter than the R255 sentence
because R9/R8 are 2-char labels vs R11/R10 3-char labels; and the
Ghi-chú range change costs -1 ("R11–R165" -> "R9–R165"). The R255
formula (+37 trail, no range term) copied blindly would give -49, but
the measured net is -52. Measure every component from the dry-run
projection (and from grep on the old lengths) each round; never copy
the previous round's formula.
(26) NEW THIS ROUND (R257): a fetch that fails once with a proxy
connection reset is transient until proven otherwise -- the first fetch
this round failed ("kex_exchange_identification: read: Connection reset
by peer", proxy 198.19.0.1:3128) and the immediate retry with the
documented env (GIT_SSH_COMMAND + tools-bin PATH + GIT_LFS_SKIP_SMUDGE=1)
succeeded, remote head unchanged (46fde45). Do not conclude the remote
is unreachable from one failed fetch, and do not skip the fetch step --
re-derive the head from ls-remote after the retry before trusting the
local clone.
(27) NEW THIS ROUND (R258): this round ran in two phases a third time
(see lessons 22/24) -- and the meta-transform chain (make_make, maker,
build script, generator, fill script) was GONE: /tmp is wiped between
runs, so the R258 checker was rebuilt by a fresh shift script written
from the committed R257 checker, with every pair asserted unique before
writing and the SHA-hits paragraph re-filled by grep (lesson 34).
The retry re-derived every figure from git + fresh live reads before
trusting the inherited edit (705/3166/+351778 at 34ed40f, merge-tree
c2ab4e44, delta e41cfda..34ed40f 2 paths / 651 insertions; live body
still R222, sha 1dd61afd, 34 comments, no new direction) and verified
the net body delta -35 from measured components (-174 R5, -190 R4,
+271 paragraph, +35 trail, +30 title, +5 Ghi-chú list, 0 range,
-12 head line): the head line SHRANK because the connector-refusal
clause was dropped (phase 1 read the public API straight) while
"không đổi" added 7 chars. The compaction pair (R5 + R4) does NOT
share a length again: R5 measured 376 chars but R4 measured 392 chars
(the R4 paragraph carries the longer quiet-hours payload sentence), so
the double compaction saved -174 + -190 = -364, not -410; never assume
a pair shares a length, measure both (lessons 31/44, re-proven this
round). If the chain is to survive the next /tmp wipe, the shift +
fill scripts should be kept outside /tmp (see the R258 report).
(28) CARRIED (R259): the R258 checker docstring carried a false
sentence in its edit-script note: "the edit script itself was lost with
/tmp between runs, so no literal idempotency re-run exists this round"
-- the phase-1 EDIT chain (build_transform_edit_r258.py /
transform_edit_r258.py / edit_pr119_r258.py) had in fact survived in
goal hidden_files, and the R258 retry phase found it after the content
commit and re-ran it (dry-run changed: 0, apply changed: 0, idempotency
re-run changed: 0; sha256 of both files unchanged). What was GONE was
the CHECKER meta-transform chain (make_make/maker/generator/fill), which
the R258 round rebuilt fresh (lesson 27 is true about the checker chain
only). The correction is applied here, in the edit-script note above,
not by editing the committed R258 checker (precedent: R254 prose-slip
corrections live in the next round's report + checker, never by
rewriting pushed history). The R259 edit chain is saved the same way
(build_transform_edit_r259.py / transform_edit_r259.py /
edit_pr119_r259.py in goal hidden_files) plus the checker shift + fill
scripts (shift_checker_r259.py / fill_sha_hits_r259.py), so the next
round reuses them instead of rebuilding from scratch (lesson 52).
The double compaction ends its run below R166 this round: R3 + R2 were
the last pair below R166 (no R1 paragraph exists in the body -- R1's
content lives in the delivery index only), so R260 compacts R166 + R167,
the oldest full paragraphs. The R2 compact is 265 chars, not 202: its
paragraph carries the posted-live sentence + ACK id, so the pair does
NOT share a length (392/430 full, 202/265 compact); measure both, never
assume (lessons 31/44, re-proven this round)
(29) CARRIED (R260): the R260 edit chain reused the R259 chain
via patch_maker_r260.py (a patch script that transforms
build_transform_edit_r259.py into build_transform_edit_r260.py; the
patch script itself is kept in goal hidden_files). Three patch bugs were
caught by assertions before any deliverable was touched: a missing
tuple-closing paren in a wholesale pattern, a renamed-constant reference
(COVERS_R259 -> COVERS_R260) in the new_tuple code, and a trail fix-up
anchor that wrongly assumed a quote before R260 (the trail text has no
quote there). A fourth fix-up class was dropped: the transform file has
no standalone main() asserts -- the edit script's asserts are shifted by
the PAIRS, not by standalone lines. The R260 edit chain is saved the
same way (patch_maker_r260.py / build_transform_edit_r260.py /
transform_edit_r260.py / edit_pr119_r260.py in goal hidden_files) plus
the checker shift + fill scripts (shift_checker_r260.py /
fill_sha_hits_r260.py), so the next round reuses them (lesson 52).
The DOUBLE compaction is DONE: R166 + R167 were the last pair below
R166; from R261 only single-paragraph compaction (R168, R169, ...).
The R166/R167 compacts DO share a length (214/214) while the full
paragraphs do NOT (825/914); the trail append is 39 chars (space +
38-char sentence), not 38 -- the net body delta is -894, measured by
the dry-run projection, not hand-counted (lessons 31/44, re-proven)
(30) CARRIED (R261): the R261 edit chain reused the R260 chain
via patch_maker_r261.py (a patch script that transforms
build_transform_edit_r260.py into build_transform_edit_r261.py; the
patch script itself is kept in goal hidden_files). The 11:43 JST
forward draft for R261 (authored during the R260 run) carried three
stale assumptions, each caught by an assertion before any deliverable
was touched: the mergeable extraction regex assumed the R259 MERGE
paragraph said "clean at 713b3dc" (it said "unstable at 713b3dc"); the
wholesale mergeable pattern assumed the same "clean" state word (the
shifted old side is "unstable at 34f70c2"); and the tail-fix assert
named the NEW constants R260_ROW/R260_PARA as absent (they must be
present) and the retired R3/R2 names (already renamed in R260) instead
of the old names R259_ROW/R259_PARA/R166_COMPACT/R167_COMPACT. Two
more single-compaction transition gaps followed: the Ghi-chú range
fix-up kept the old side "R3–R165" (the body already reads "R3–R167";
the new side must be "R3–R167" -> "R3–R168"), and the R167 artifacts
(block, line_replace call, len assert) passed through the transform
untouched because deleting the PAIR only stops creating a new call --
a one-off delete_r167_artifacts_r261.py removes them from the edit
script (single-compaction transition only; from R262 the shift is
regular). The R260 payload main was refreshed ~11:55 JST (unstable ->
true/clean) AFTER the forward draft was authored, so the draft's
"main == .bak" claim was already wrong when R261 re-measured from disk
-- the R260 index row carries the correction as ĐÍNH CHÍNH R261 with
both versions (lesson 54a, re-proven). The R261 edit chain is saved
the same way (patch_maker_r261.py / build_transform_edit_r261.py /
transform_edit_r261.py / edit_pr119_r261.py in goal hidden_files) plus
the checker shift + fill scripts (shift_checker_r261.py /
fill_sha_hits_r261.py), so the next round reuses them (lesson 52).
The SINGLE compaction continues: R168 (811 -> 214) is the first single
compaction; from R262 the same single-paragraph step repeats (R169,
R170, ...). The trail append is 28 chars this round (the single-
compaction sentence is shorter than the pair sentence); the net body
delta is -298, measured by the dry-run projection, not hand-counted
(lessons 31/44, re-proven)
(31) CARRIED (R262): the R262 edit chain reused the R261 chain
via patch_maker_r262.py (a patch script that transforms
build_transform_edit_r261.py into build_transform_edit_r262.py; the
patch script itself is kept in goal hidden_files). Three stale
assumptions, each caught by an assertion before any deliverable was
touched: the authored-assert rep assumed 'assert len(R168_COMPACT)...'
was unique (it occurs 3x -- the authored assert + twice inside the tail
fix-up len-assert pair; the fix replaces the whole 3-line authored
block at once); the trail fix-up assumed the pair's strings carry real
newlines (they carry an escaped newline -- the transform's pair strings
are single-line literals with 
 escapes, so the fix is substring on
the sentences, and the NEW side's old-string must be the sentence the
R261 edit actually appended, "R261 đã gọn thêm đoạn R168.", not "R261
đã gọn thêm các đoạn R166 + R167."); and the NEW_ENTRIES compact key
assumed "R168_COMPACT" (the shifted transform's NEW_BLOCKS key is
"R166_COMPACT" -- the global shift never touches it; the fix is a key
RENAME fix-up '"R166_COMPACT":' -> '"R168_COMPACT":' before the
NEW_ENTRIES loop, mirroring R261's R3 -> R166 rename; the intermediate
"R167_COMPACT" guess was also wrong). The R261 payload main was NOT
refreshed this round (main == .bak, verified from disk twice) -- the
first round where the payload needed no refresh, because CI had already
finished and mergeable was clean at the new head by the time of the
fresh read. The R262 edit chain is saved the same way
(patch_maker_r262.py / build_transform_edit_r262.py /
transform_edit_r262.py / edit_pr119_r262.py in goal hidden_files) plus
the checker shift + fill scripts (shift_checker_r262.py /
fill_sha_hits_r262.py), so the next round reuses them (lesson 52).
The SINGLE compaction continues: R169 (743 -> 214) is the second single
compaction; from R263 the same single-paragraph step repeats (R170,
R171, ...). The trail append is 28 chars this round; the net body
delta is -173, measured by the dry-run projection, not hand-counted
(lessons 31/44, re-proven)
(32) NEW THIS ROUND (R263): the R263 edit chain reused the R262 chain
via patch_build_transform_r263.py (a patch script that builds
build_transform_edit_r263.py directly from build_transform_edit_r262.py --
no make_patch_maker_r262.py was carried from R262, so the patch-maker
level is skipped this round; the patch script itself is kept in goal
hidden_files). Three stale assumptions, each caught by an assertion or
by re-measurement before any deliverable was touched: the builder
docstring still cited 'R258 values' and 'R258 and R259 notes' (four
rounds stale; fixed to R262 values and R261/R262 notes); the R262
checker's headroom 'was' value (10,062) was wrong for R261 (actual
headroom after R261 was 9,889 -- the R262 author copied the new headroom
into both slots; the R263 text carries the correct 'was', 10,062, actual
after R262); and the R263 fix-up block initially advanced the Ghi-chú
range, len-assert, print and structural-assert pairs one round too far
(R170/R171 instead of R169/R170 -- caught on review before running,
fixed in the patch script). The R262 payload main was NOT refreshed
this round either (main == .bak, verified from disk ~14:52 JST) -- the
second round where the payload needed no refresh. The R263 edit chain
is saved the same way (patch_build_transform_r263.py /
build_transform_edit_r263.py / transform_edit_r263.py / edit_pr119_r263.py
in goal hidden_files) plus the checker shift + fill scripts
(shift_checker_r263.py / fill_sha_hits_r263.py), so the next round
reuses them (lesson 52). The SINGLE compaction continues: R170 (746 ->
214) is the third single compaction; from R264 the same single-paragraph
step repeats (R171, R172, ...). The trail append is 28 chars this round;
the net body delta is -144, measured by the dry-run projection, not
hand-counted (lessons 31/44, re-proven). The checker shift chain hit the
second recurrence of lesson 53d: the R262 checker's f-string was corrected
by the R262 tail fix-up ({r168_ok} -> {r167_ok}), so the mech-shifted R263
pair's old side ({r168_ok}) no longer matches the R262 checker --
patch_shift_checker_r263.py corrects the pair's old side in its non-PAIRS
reps (the one exception to the splice-exact verification), and the tail
f-string fix-up advances to {r169_ok} -> {r167_ok} (label r169ascending).
(33) NEW THIS ROUND (R264): the R264 edit chain reused the R263 chain directly (transform_edit_r264.py hand-shifted from transform_edit_r263.py with asserted pairs -- no patch_build_transform step this round; the chain files are saved the same way). The R263 payload was REFRESHED at post time by the main thread (prepared 94,733 chars sha 8d9b0d2f -> posted 94,825 chars sha 07316552, Head e373cb5 -> daf9540) -- the first posted payload since R222 and the first refresh since the R260 main ~11:55 JST; all 3 on-disk copies (main + .bak + 2 .bak-prepost dirs) now equal the POSTED body, so the R264 row records both versions and the R263 paragraph records the posted one. The R263 checker carried an unfilled SHA-hits placeholder (@@SHA_HITS_R263@@ -- the fill step was skipped in the two-timeout R263 round); the R264 shift renames the placeholder instead of excising a filled paragraph, and the fill is attempted again this round (fill_sha_hits_r264.py). The SINGLE compaction continues: R171 (743 -> 214) is the fourth single compaction; from R265 the same single-paragraph step repeats (R172, R173, ...). The trail append is 28 chars this round; the net body delta is -237, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line SHRANK this round (1,222 -> 1,180, delta -42) -- the live-body sentence got shorter because the posted R263 body needs no "still R222" clause; a shrinking head line is normal when the live body advances.
(34) NEW THIS ROUND (R265): the R265 edit chain reused the R264 chain directly (transform_edit_r265.py hand-shifted from transform_edit_r264.py with asserted pairs -- the R264_ROW block is derived from the source R263_ROW by asserted span/pair replacements, not retyped; the chain files are saved the same way). The R264 report overstated the R264 payload backup state ("main == .bak byte-identical") -- no standalone .bak file exists for R264 (r264_payload.py writes only main + 2 .bak-prepost copies); main == both prepost copies (sha256 19422e8d), measured from disk this round, and the R265 row records the measured state. The issue read used call-read-tool method get (issue_number) -- the call-tool get_comments attempt stayed pending approval and was not needed (count + updated_at unchanged from the last verified get_comments). Time labels are separated per step this round (fetch ~22:01 JST, git counts ~22:02 JST, PR read ~22:03 JST, issue read ~22:06 JST) -- lesson 57a applied to R265's own writing; R264's locked "~16:47 JST" labels stay as written. The SINGLE compaction continues: R172 (719 -> 214) is the fifth single compaction; from R266 the same single-paragraph step repeats (R173, R174, ...). The trail append is 28 chars this round; the net body delta is -107, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line GREW this round (1,180 -> 1,244, delta +64) -- the .bak-correction clause and the separated time labels lengthen it; a growing head line is normal when the live-body sentence gains a correction.
(35) NEW THIS ROUND (R266): the R266 edit chain reused the R265 chain directly (transform_edit_r266.py hand-shifted from transform_edit_r265.py with asserted pairs -- the R265_ROW block is derived from the source R264_ROW by asserted span/pair replacements, not retyped; the chain files are saved the same way). The R265 dev-queue line cited the R265 content-head counts (720/3188/+366510) for the report head 5584a8f -- the report commit itself adds 1 commit, 2 files and 652 insertions, so the true report-head figures are 721/3190/+367162, re-derived from git and confirmed by the fresh connector read (721/3190/+367162, deletions null); the R266 row records the measured figures (lesson 59). The SHA-hits entry set adds 5584a8f + ecee5f7 at the front (80 entries); daf9540 does NOT retire -- its R263-row guard and last-clean references shifted to 451147b, but the lesson-33 history ('Head e373cb5 -> daf9540') keeps it at 2 occurrences, so it stays an entry (the first draft of this lesson claimed a retirement; the fill's extra-token assertion disproved it before commit). The issue read used call-read-tool method get (issue_number) -- no call-tool get_comments attempt this round (count + updated_at unchanged from the last verified get_comments). Time labels are separated per step this round (fetch ~23:33 JST, git counts ~23:34 JST, PR read ~23:35 JST, issue read ~23:35 JST) -- lesson 57a applied to R266's own writing; R265's locked labels stay as written. The SINGLE compaction continues: R173 (713 -> 214) is the sixth single compaction; from R267 the same single-paragraph step repeats (R174, R175, ...). The trail append is 28 chars this round; the net body delta is -181, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line SHRANK this round (1,244 -> 1,228, delta -16) -- the shorter mergeable clause and the dropped get_comments sentence shorten it; a shrinking head line is normal when the live-body sentence loses a clause.
(36) NEW THIS ROUND (R267): the R267 edit chain reused the R266 chain directly (transform_edit_r267.py hand-shifted from transform_edit_r266.py with asserted pairs -- the R266_ROW block is derived from the source R265_ROW by asserted span/pair replacements, not retyped; the chain files are saved the same way). No correction was needed this round -- the R266 report's figures re-verified clean (723/3193/+369176 at 7db0fc8 = 722/3191/+368519 at e444f0c + 1 commit, 2 files, 657 insertions; payload R266 main == .bak == 2 prepost, sha256 e7792d4b). The SHA-hits entry set adds 7db0fc8 + e444f0c at the front (82 entries); daf9540 still does NOT retire -- the lesson-33 history ('Head e373cb5 -> daf9540') keeps it at 5 occurrences outside the paragraph, so it stays an entry. The issue read used call-read-tool method get (issue_number) -- no call-tool get_comments attempt this round (count + updated_at unchanged from the last verified get_comments). Time labels are separated per step this round (fetch ~23:53 JST, git counts ~23:53 JST, PR read ~23:56 JST, issue read ~23:57 JST) -- lesson 57a applied to R267's own writing; R266's locked labels stay as written. The SINGLE compaction continues: R174 (691 -> 214) is the seventh single compaction; from R268 the same single-paragraph step repeats (R175, R176, ...). The trail append is 28 chars this round; the net body delta is -143, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line is UNCHANGED this round (1,228 -> 1,228, delta 0) -- an unchanged head line is normal when the live-body sentence keeps the same clauses and only the head/counts change.
(37) NEW THIS ROUND (R268): the R268 edit chain reused the R267 chain directly (transform_edit_r268.py hand-shifted from transform_edit_r267.py with asserted pairs -- the R267_ROW block is derived from the source R266_ROW by asserted span/pair replacements, not retyped; the chain files are saved the same way). The R267 report's figures re-verified clean (725/3196/+371199 at 1bf2318 = 724/3194/+370537 at 9ce3e24 + 1 commit, 2 files, 662 insertions; payload R267 main == .bak == 2 prepost, sha256 79509e40). The SHA-hits entry set adds 1bf2318 + 9ce3e24 at the front (84 entries); daf9540 still does NOT retire -- the lesson-33 history ('Head e373cb5 -> daf9540') keeps it at 7 occurrences outside the paragraph, so it stays an entry. The PR read's base.sha f3832338 is a stale cache (an ancestor of the live integration tip f3db6b3 per ls-remote); the execution-risk flag appeared a 10th time after the investigative fetch that resolved it -- no content from that fetch was checked out or used, and no R268 action was blocked. Time labels are separated per step this round (fetch ~00:40 JST, git counts ~00:41 JST, PR read ~00:42 JST, issue read ~00:42 JST) -- lesson 57a applied to R268's own writing; R267's locked labels stay as written. The SINGLE compaction continues: R175 (568 -> 214) is the eighth single compaction; from R269 the same single-paragraph step repeats (R176, R177, ...). The trail append is 28 chars this round; the net body delta is -20, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line is UNCHANGED this round (1,228 -> 1,228, delta 0) -- the second round in a row at the same length.
(38) NEW THIS ROUND (R269): the R269 edit chain reused the R268 chain directly (transform_edit_r269.py hand-shifted from transform_edit_r268.py with asserted pairs -- the R268_ROW block is derived from the source R267_ROW by asserted replacements, not retyped; the chain files are saved the same way). The R268 report's figures re-verified clean (727/3199/+373240 at 2718ea5 = 726/3197/+372573 at b062dd1 + 1 commit, 2 files, 667 insertions; payload R268 main == .bak == 2 prepost, sha256 4d198f3d). The SHA-hits entry set adds 2718ea5 + b062dd1 at the front (86 entries); daf9540 still does NOT retire -- the lesson-33 history ('Head e373cb5 -> daf9540') keeps it at 9 occurrences outside the paragraph, so it stays an entry. The PR read's base.sha f3832338 is a stale cache (an ancestor of the live integration tip f3db6b3 per ls-remote); no execution-risk flag appeared this round. Time labels are separated per step this round (fetch ~01:40 JST, git counts ~01:41 JST, PR read ~01:41 JST, issue read ~01:41 JST) -- lesson 57a applied to R269's own writing; R268's locked labels stay as written. The SINGLE compaction continues: R176 (472 -> 214) is the ninth single compaction; from R270 the same single-paragraph step repeats (R177, R178, ...). The trail append is 28 chars this round; the net body delta is +76, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line is UNCHANGED this round (1,228 -> 1,228, delta 0) -- the third round in a row at the same length.
(39) NEW THIS ROUND (R270): the R270 edit chain reused the R269 chain directly (transform_edit_r270.py hand-shifted from transform_edit_r269.py with asserted pairs -- the R269_ROW block is derived from the source R268_ROW by asserted replacements, not retyped; the chain files are saved the same way). The R269 report's figures re-verified clean (729/3202/+375288 at 6b040c7 = 728/3200/+374618 at 75e1d55 + 1 commit, 2 files, 670 insertions; payload R269 main == .bak == 2 prepost, sha256 18775c06). The SHA-hits entry set adds 6b040c7 + 75e1d55 at the front (88 entries); daf9540 still does NOT retire -- the lesson-33 history ('Head e373cb5 -> daf9540') keeps it at 11 occurrences outside the paragraph, so it stays an entry. The PR read's base.sha f3832338 is a stale cache (an ancestor of the live integration tip f3db6b3 per ls-remote); no execution-risk flag appeared this round. Time labels are separated per step this round (fetch ~02:40 JST, git counts ~02:41 JST, PR read ~02:42 JST, issue read ~02:42 JST) -- lesson 57a applied to R270's own writing; R269's locked labels stay as written. The SINGLE compaction continues: R177 (472 -> 214) is the tenth single compaction; from R271 the same single-paragraph step repeats (R178, R179, ...). The trail append is 28 chars this round; the net body delta is +76, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line is UNCHANGED this round (1,228 -> 1,228, delta 0) -- the fourth round in a row at the same length.
(40) NEW THIS ROUND (R271): the R271 edit chain reused the R270 chain directly (transform_edit_r271.py hand-shifted from transform_edit_r270.py with asserted pairs -- the R270_ROW block is derived from the source R269_ROW by asserted replacements, not retyped; the chain files are saved the same way). One assertion caught a real error before any write: the lesson-39 draft text reintroduced the retired content sha 75e1d55 (the SHA-hits entry note); reworded to cite the cover sha only. The R270 report's figures re-verified clean (731/3205/+377345 at 2482e3b = 730/3203/+376671 at 3ae052f + 1 commit, 2 files, 674 insertions; payload R270 main == .bak == 2 prepost, sha256 2b5a3164). The SHA-hits entry set adds 2482e3b + 3ae052f at the front (90 entries); daf9540 still does NOT retire -- the lesson-33 history ('Head e373cb5 -> daf9540') keeps it at 13 occurrences outside the paragraph, so it stays an entry. The PR read's base.sha f3832338 is a stale cache (an ancestor of the live integration tip f3db6b3 per ls-remote); no execution-risk flag appeared this round. Time labels are separated per step this round (fetch ~03:40 JST, git counts ~03:41 JST, PR read ~03:42 JST, issue read ~03:42 JST) -- lesson 57a applied to R271's own writing; R270's locked labels stay as written. The SINGLE compaction continues: R178 (472 -> 214) is the eleventh single compaction; from R272 the same single-paragraph step repeats (R179, R180, ...). The trail append is 28 chars this round; the net body delta is +76, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line is UNCHANGED this round (1,228 -> 1,228, delta 0) -- the fifth round in a row at the same length.
(41) NEW THIS ROUND (R272): the R272 edit chain reused the R271 chain directly (transform_edit_r272.py hand-shifted from transform_edit_r271.py with asserted pairs -- the R271_ROW block is derived from the source R270_ROW by asserted replacements, not retyped; the chain files are saved the same way). The transform's pair assertions caught a real slip before any write: the first draft of the apply_edits pairs mixed the anchor round (find R269 / Ghi-chú R270 / trail R270) with the identifier round (R270_ROW / R271_NOTE / R270_PARA) -- off by one in both directions across two fix passes; the assertion "pair not unique (0)" stopped the run, and the corrected pairs ran clean (dry-run 94,410 = apply 94,410, idempotency 0). Rule: anchor strings come from the SOURCE script's find/sub_once calls, identifier names from its NEW blocks -- never shift both from the same base. The R271 report's figures re-verified clean (733/3208/+379411 at ce57ceb = 732/3206/+378733 at 16dfcfe + 1 commit, 2 files, 678 insertions; payload R271 main == .bak == 2 prepost, sha256 ebe83ebd). The SHA-hits entry set adds ce57ceb + 16dfcfe at the front (92 entries); daf9540 still does NOT retire -- the lesson-33 history ('Head e373cb5 -> daf9540') keeps it at 15 occurrences outside the paragraph, so it stays an entry. The PR read's base.sha f3832338 is a stale cache (an ancestor of the live integration tip f3db6b3 per ls-remote); no execution-risk flag appeared this round. Time labels are separated per step this round (fetch ~04:40 JST, git counts ~04:41 JST, PR read ~04:41 JST, issue read ~04:41 JST) -- lesson 57a applied to R272's own writing; R271's locked labels stay as written. The SINGLE compaction continues: R179 (472 -> 214) is the twelfth single compaction; from R273 the same single-paragraph step repeats (R180, R181, ...). The trail append is 28 chars this round; the net body delta is +76, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line is UNCHANGED this round (1,228 -> 1,228, delta 0) -- the sixth round in a row at the same length.
(42) NEW THIS ROUND (R273): the R273 edit chain reused the R272 chain directly (transform_edit_r273.py hand-shifted from transform_edit_r272.py with asserted pairs -- the R272_ROW block is derived from the source R271_ROW by asserted replacements, not retyped; the chain files are saved the same way). The transform ran clean on the FIRST try -- no assertion fired -- the anchor/identifier rule from lesson (41) held (anchors from the source script's find/sub_once calls, identifiers from its NEW blocks). The R272 report's figures re-verified clean (735/3211/+381486 at e71bce5 = 734/3209/+380804 at 312d680 + 1 commit, 2 files, 682 insertions; payload R272 main == .bak == 2 prepost, sha256 f6fc2589). The SHA-hits entry set adds e71bce5 + 312d680 at the front (94 entries); the lesson-41 retired-sha entry stays an entry at 15 occurrences outside the paragraph, so it is NOT retired. The PR read's `mergeable` key was absent from the MCP response again (as in R272) -- "mergeable null" in the head line and index is the established convention for this response shape; mergeable_state clean is the operational value. The issue read's first attempt passed `issueNumber` and errored (missing required parameter: issue_number); the retry with `issue_number` succeeded -- lesson 8 stands, and the parameter name is recorded in the R273 report as lesson (66). R180 is 434 chars, not the usual ~472 -- the single compaction is -220 this round and the net body delta is +114, not +76; measure the paragraph from disk, never assume its length (the edit script asserts 270 for the new paragraph and 214 for the compact). The SINGLE compaction continues: R180 (434 -> 214) is the thirteenth single compaction; from R274 the same single-paragraph step repeats (R181, R182, ...). The trail append is 28 chars this round; the net body delta is +114, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line is UNCHANGED this round (1,228 -> 1,228, delta 0) -- the seventh round in a row at the same length.
(43) NEW THIS ROUND (R274): the R274 edit chain reused the R273 chain directly (transform_edit_r274.py hand-shifted from transform_edit_r273.py with asserted pairs -- the R273_ROW block is derived from the source R272_ROW by asserted replacements, not retyped; the chain files are saved the same way). The transform ran clean on the FIRST try -- no assertion fired -- the anchor/identifier rule from lesson (41) held (anchors from the source script's find/sub_once calls, identifiers from its NEW blocks). The R273 report's figures re-verified clean (737/3214/+383574 at a7c0ae5 = 736/3212/+382888 at 5dc1302 + 1 commit, 2 files, 686 insertions; payload R273 main == .bak == 2 prepost, sha256 85881075). The SHA-hits entry set adds a7c0ae5 + 5dc1302 at the front (96 entries); the lesson-41 retired-sha entry stays an entry at 15 occurrences outside the paragraph, so it is NOT retired. The PR read's `mergeable` key was absent from the MCP response again (as in R273) -- "mergeable null" in the head line and index is the established convention for this response shape; mergeable_state clean is the operational value. The issue read passed `issue_number` first try this round (lesson 66 recorded in R273; no retry needed). R181 is 415 chars, not the usual ~472 -- the single compaction is -201 this round and the net body delta is +133, not +76; measure the paragraph from disk, never assume its length (the edit script asserts 270 for the new paragraph and 214 for the compact). The SINGLE compaction continues: R181 (415 -> 214) is the fourteenth single compaction; from R275 the same single-paragraph step repeats (R182, R183, ...). The trail append is 28 chars this round; the net body delta is +133, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line is UNCHANGED this round (1,228 -> 1,228, delta 0) -- the eighth round in a row at the same length.
(44) NEW THIS ROUND (R275): the R275 edit chain reused the R274 chain directly (transform_edit_r275.py hand-shifted from transform_edit_r274.py with asserted pairs -- the R274_ROW block is derived from the source R273_ROW by asserted replacements, not retyped; the chain files are saved the same way). The transform ran clean on the FIRST try -- no assertion fired -- the anchor/identifier rule from lesson (41) held (anchors from the source script's find/sub_once calls, identifiers from its NEW blocks). The R274 report's figures re-verified clean (739/3217/+385669 at 2de586d = 738/3215/+384979 at 56926f3 + 1 commit, 2 files, 690 insertions; payload R274 main == .bak == 2 prepost, sha256 dc3fe056). The SHA-hits entry set adds 2de586d + 56926f3 at the front (98 entries); the lesson-41 retired-sha entry stays an entry at 15 occurrences outside the paragraph, so it is NOT retired. The PR read's `mergeable` key was absent from the MCP response again (as in R274) -- "mergeable null" in the head line and index is the established convention for this response shape; mergeable_state clean is the operational value. The issue read passed `issue_number` first try this round (lesson 66 recorded in R273; no retry needed). R182 is 415 chars, not the usual ~472 -- the single compaction is -201 this round and the net body delta is +133, not +76; measure the paragraph from disk, never assume its length (the edit script asserts 270 for the new paragraph and 214 for the compact). The SINGLE compaction continues: R182 (415 -> 214) is the fifteenth single compaction; from R276 the same single-paragraph step repeats (R183, R184, ...). The trail append is 28 chars this round; the net body delta is +133, measured by the dry-run projection, not hand-counted (lessons 31/44, re-proven). The head line is UNCHANGED this round (1,228 -> 1,228, delta 0) -- the ninth round in a row at the same length.
(45) NEW THIS ROUND (R276): the R276 edit chain reused the R275 chain directly (transform_edit_r276.py hand-shifted from transform_edit_r275.py with asserted pairs -- the R275_ROW block is derived from the source R274_ROW by asserted replacements, not retyped; the chain files are saved the same way). The transform ran clean on the FIRST try -- no assertion fired -- the anchor/identifier rule from lesson (41) held (anchors from the source script's find/sub_once calls, identifiers from its NEW blocks). The R275 report's figures re-verified clean (741/3220/+387773 at 7e44e0c = 740/3218/+387079 at c7117ef + 1 commit, 2 files, 694 insertions; payload R275 main == .bak == 2 prepost, sha256 fb0d5958). The SHA-hits entry set adds 7e44e0c + c7117ef at the front (100 entries); the lesson-41 retired-sha entry stays an entry at 15 occurrences outside the paragraph, so it is NOT retired. The PR read's `mergeable` key was absent from the MCP response again (as in R275) -- "mergeable null" in the head line and index is the established convention for this response shape; mergeable_state clean is the operational value. The issue read passed `issue_number` first try this round (lesson 66 recorded in R273; no retry needed). R183 is 440 chars, not the usual ~472 -- the single compaction is -226 this round and the net body delta is +108, not +133; measure the paragraph from disk, never assume its length (the edit script asserts 270 for the new paragraph and 214 for the compact). The SINGLE compaction continues: R183 (440 -> 214) is the sixteenth single compaction; from R277 the same single-paragraph step repeats (R184, R185, ...). The trail append is 28 chars this round; the net body delta is +108, measured by the dry-run projection, not hand-counted (lessons 31/45, re-proven). The head line is UNCHANGED this round (1,228 -> 1,228, delta 0) -- the tenth round in a row at the same length."""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
COVER = "7e44e0c06bb4bb05eaabcc8368e95982c5a287a4"
INTEGRATION = "f3db6b384886a59128328b8daa8c9eefc2d8f3ce"
CHECKER_NAME = "check_pr119_restructure_r276_v1.py"

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

    chk("index header coverage head == 7e44e0c", "(head `7e44e0c`)" in index)
    chk("index milestone full head sha", f"`{COVER}`" in index)
    for sha in ("c7117ef", "7e44e0c"):
        chk(f"index has row sha {sha}", f"`{sha}`" in index)
    chk("index counts line 741/3220", "**741 commit / 3220 file**" in index)
    chk("index issue line 34 comments ACK 6862732081",
        "34 comment" in index and "`6862732081`" in index)
    chk("index R276 note", "Cập nhật R276" in index)
    chk("index R275 note kept", "Cập nhật R275" in index)
    chk("index R275 row label", "PR119 BODY RESTRUCTURE R275" in index)

    # R196 script-defect repairs, kept as regression guards: milestone 6
    # separate lines, heading own line, R167 note own line in ascending
    # position, R236 note clean.
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
    r275_note = [l for l in il if l.startswith("- Cập nhật R275 (2026-11-27):")]
    r275_note_ok = len(r275_note) == 1 and "- Cập nhật R182 " not in r275_note[0]
    repair_detail = (f"milestone6={milestone_ok} heading={heading_ok} "
                     f"r196clean={r196_clean} r169ascending={r167_ok} r275note={r275_note_ok}")
    chk("index R196-defect repairs (milestone 6 lines, heading, R169 ascending, R275 note)",
        milestone_ok and heading_ok and r196_clean and r167_ok and r275_note_ok,
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

    # R229 row (carried from R229): must cite cumulative 3080 (3079 at
    # 9890c75 + 1 new checker in the R229 content commit).
    r228_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R228 |")]
    r228_row_ok = (len(r228_row) == 1 and "cumulative 3080 paths" in r228_row[0])
    chk("index R228 row cumulative == 3080 (3079 at 9890c75 + 1 checker)", r228_row_ok)

    # R230 row (carried from R230): must cite cumulative 3083 (3082 at
    # 8310e5d + 1 new checker in the R230 content commit).
    r229_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R229 |")]
    r229_row_ok = (len(r229_row) == 1 and "cumulative 3083 paths" in r229_row[0])
    chk("index R229 row cumulative == 3083 (3082 at 8310e5d + 1 checker)", r229_row_ok)

    # R231 row (carried from R231): must cite cumulative 3086 (3085 at
    # 9861875 + 1 new checker in the R231 content commit).
    r230_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R230 |")]
    r230_row_ok = (len(r230_row) == 1 and "cumulative 3086 paths" in r230_row[0])
    chk("index R230 row cumulative == 3086 (3085 at 9861875 + 1 checker)", r230_row_ok)

    # R232 row (carried from R232): must cite cumulative 3089 (3088 at
    # 29727d4 + 1 new checker in the R232 content commit).
    r231_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R231 |")]
    r231_row_ok = (len(r231_row) == 1 and "cumulative 3089 paths" in r231_row[0])
    chk("index R231 row cumulative == 3089 (3088 at 29727d4 + 1 checker)", r231_row_ok)

    # R233 row (carried from R233): must cite cumulative 3092 (3092 at
    # 233f0b5, re-derived from git at the R233 content commit).
    r232_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R232 |")]
    r232_row_ok = (len(r232_row) == 1 and "cumulative 3092 paths" in r232_row[0])
    chk("index R232 row cumulative == 3092 (3092 at 233f0b5)", r232_row_ok)

    # R234 row (carried from R234): must cite cumulative 3095 (3094 at 33962fd
    # + 1 new checker in the R234 content commit); the git figure is
    # re-derived below.
    r233_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R233 |")]
    r233_row_ok = (len(r233_row) == 1 and "cumulative 3095 paths" in r233_row[0])
    chk("index R233 row cumulative == 3095 (3094 at 33962fd + 1 checker)", r233_row_ok)

    # R235 row (carried from R235): must cite cumulative 3098 (3097 at 19e8f7c
    # + 1 new checker in the R235 content commit); the git figure is
    # re-derived below.
    r234_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R234 |")]
    r234_row_ok = (len(r234_row) == 1 and "cumulative 3098 paths" in r234_row[0])
    chk("index R234 row cumulative == 3098 (3097 at 19e8f7c + 1 checker)", r234_row_ok)

    # R236 row (carried from R236): must cite cumulative 3101 (3100 at d5f1db3
    # + 1 new checker in the R236 content commit); the git figure is
    # re-derived below.
    r235_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R235 |")]
    r235_row_ok = (len(r235_row) == 1 and "cumulative 3101 paths" in r235_row[0])
    chk("index R235 row cumulative == 3101 (3100 at d5f1db3 + 1 checker)", r235_row_ok)

    # R237 row (carried from R237): must cite cumulative 3104 (3103 at 6db62e0
    # + 1 new checker in the R237 content commit); the git figure is
    # re-derived below.
    r236_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R236 |")]
    r236_row_ok = (len(r236_row) == 1 and "cumulative 3104 paths" in r236_row[0])
    chk("index R236 row cumulative == 3104 (3103 at 6db62e0 + 1 checker)", r236_row_ok)

    # R238 row (carried from R238): must cite cumulative 3107 (3106 at 7bf9212
    # + 1 new checker in the R238 content commit); the git figure is
    # re-derived below.
    r237_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R237 |")]
    r237_row_ok = (len(r237_row) == 1 and "cumulative 3107 paths" in r237_row[0])
    chk("index R237 row cumulative == 3107 (3106 at 7bf9212 + 1 checker)", r237_row_ok)

    # R239 row (carried from R239): must cite cumulative 3110 (3109 at 10eebd3
    # + 1 new checker in the R239 content commit); the git figure is
    # re-derived below.
    r238_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R238 |")]
    r238_row_ok = (len(r238_row) == 1 and "cumulative 3110 paths" in r238_row[0])
    chk("index R238 row cumulative == 3110 (3109 at 10eebd3 + 1 checker)", r238_row_ok)

    # R240 row (carried from R240): must cite cumulative 3113 (3112 at 3c076bf
    # + 1 new checker in the R240 content commit); the git figure is
    # re-derived below.
    r239_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R239 |")]
    r239_row_ok = (len(r239_row) == 1 and "cumulative 3113 paths" in r239_row[0])
    chk("index R239 row cumulative == 3113 (3112 at 3c076bf + 1 checker)", r239_row_ok)

    # R241 row (carried from R241): must cite cumulative 3116 (3115 at 66cea79
    # + 1 new checker in the R241 content commit); the git figure is
    # re-derived below.
    r240_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R240 |")]
    r240_row_ok = (len(r240_row) == 1 and "cumulative 3116 paths" in r240_row[0])
    chk("index R240 row cumulative == 3116 (3115 at 66cea79 + 1 checker)", r240_row_ok)

    # R242 row (carried from R242): must cite cumulative 3119 (3118 at f021c08
    # + 1 new checker in the R242 content commit); the git figure is
    # re-derived below.
    r241_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R241 |")]
    r241_row_ok = (len(r241_row) == 1 and "cumulative 3119 paths" in r241_row[0])
    chk("index R241 row cumulative == 3119 (3118 at f021c08 + 1 checker)", r241_row_ok)

    # R242 row (carried from R242): must cite cumulative 3122 (3121 at 26c0cc1
    # + 1 new checker in the R243 content commit); the git figure is
    # re-derived below.
    r242_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R242 |")]
    r242_row_ok = (len(r242_row) == 1 and "cumulative 3122 paths" in r242_row[0])
    chk("index R242 row cumulative == 3122 (3121 at 26c0cc1 + 1 checker)", r242_row_ok)

    # R243 row (carried from R245): must cite cumulative 3125 (3124 at 214eb99
    # + 1 new checker in the R245 content commit); the git figure is
    # re-derived below.
    r243_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R243 |")]
    r243_row_ok = (len(r243_row) == 1 and "cumulative 3125 paths" in r243_row[0])
    chk("index R243 row cumulative == 3125 (3124 at 214eb99 + 1 checker)", r243_row_ok)

    # R244 row (carried from R246): must cite cumulative 3128 (3127 at bbddba5
    # + 1 new checker in the R245 content commit); the git figure is
    # re-derived below.
    r244_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R244 |")]
    r244_row_ok = (len(r244_row) == 1 and "cumulative 3128 paths" in r244_row[0])
    chk("index R244 row cumulative == 3128 (3127 at bbddba5 + 1 checker)", r244_row_ok)

    # R245 row (carried from R246): must cite cumulative 3131 (3130 at 4fc20b6
    # + 1 new checker in the R246 content commit); the git figure is
    # re-derived below.
    r245_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R245 |")]
    r245_row_ok = (len(r245_row) == 1 and "cumulative 3131 paths" in r245_row[0])
    chk("index R245 row cumulative == 3131 (3130 at 4fc20b6 + 1 checker)", r245_row_ok)

    # R246 row (carried from R248): must cite cumulative 3134 (3133 at 1240497
    # + 1 new checker in the R247 content commit); the git figure is
    # re-derived below.
    r246_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R246 |")]
    r246_row_ok = (len(r246_row) == 1 and "cumulative 3134 paths" in r246_row[0])
    chk("index R246 row cumulative == 3134 (3133 at 1240497 + 1 checker)", r246_row_ok)

    # R247 row (carried from R249): must cite cumulative 3137 (3136 at cd4f7b0
    # + 1 new checker in the R248 content commit); the git figure is
    # re-derived below.
    r247_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R247 |")]
    r247_row_ok = (len(r247_row) == 1 and "cumulative 3137 paths" in r247_row[0])
    chk("index R247 row cumulative == 3137 (3136 at cd4f7b0 + 1 checker)", r247_row_ok)

    # R248 row (carried from R250): must cite cumulative 3140 (3139 at 24037b7
    # + 1 new checker in the R249 content commit); the git figure is
    # re-derived below.
    r248_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R248 |")]
    r248_row_ok = (len(r248_row) == 1 and "cumulative 3140 paths" in r248_row[0])
    chk("index R248 row cumulative == 3140 (3139 at 24037b7 + 1 checker)", r248_row_ok)

    # R249 row (carried from R251): must cite cumulative 3143 (3142 at 4ad9429
    # + 1 new checker in the R250 content commit); the git figure is
    # re-derived below.
    r249_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R249 |")]
    r249_row_ok = (len(r249_row) == 1 and "cumulative 3143 paths" in r249_row[0])
    chk("index R249 row cumulative == 3143 (3142 at 4ad9429 + 1 checker)", r249_row_ok)

    # R250 row (carried from R252): must cite cumulative 3146 (3145 at 1281cde
    # + 1 new checker in the R251 content commit); the git figure is
    # re-derived below.
    r250_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R250 |")]
    r250_row_ok = (len(r250_row) == 1 and "cumulative 3146 paths" in r250_row[0])
    chk("index R250 row cumulative == 3146 (3145 at 1281cde + 1 checker)", r250_row_ok)

    # R251 row (carried from R253): must cite cumulative 3149 (3148 at 7ca1f05
    # + 1 new checker in the R252 content commit); the git figure is
    # re-derived below.
    r251_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R251 |")]
    r251_row_ok = (len(r251_row) == 1 and "cumulative 3149 paths" in r251_row[0])
    chk("index R251 row cumulative == 3149 (3148 at 7ca1f05 + 1 checker)", r251_row_ok)

    # R252 row (carried from R254): must cite cumulative 3152 (3151 at 8e4d8ac
    # + 1 new checker in the R253 content commit); the git figure is
    # re-derived below.
    r252_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R252 |")]
    r252_row_ok = (len(r252_row) == 1 and "cumulative 3152 paths" in r252_row[0])
    chk("index R252 row cumulative == 3152 (3151 at 8e4d8ac + 1 checker)", r252_row_ok)

    # R253 row (carried from R255): must cite cumulative 3155 (3154 at 041c185
    # + 1 new checker in the R254 content commit); the git figure is
    # re-derived below.
    r253_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R253 |")]
    r253_row_ok = (len(r253_row) == 1 and "cumulative 3155 paths" in r253_row[0])
    chk("index R253 row cumulative == 3155 (3154 at 041c185 + 1 checker)", r253_row_ok)

    # R254 row (carried from R256): must cite cumulative 3158 (3157 at 0877855
    # + 1 new checker in the R255 content commit); the git figure is
    # re-derived below.
    r254_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R254 |")]
    r254_row_ok = (len(r254_row) == 1 and "cumulative 3158 paths" in r254_row[0])
    chk("index R254 row cumulative == 3158 (3157 at 0877855 + 1 checker)", r254_row_ok)

    # R255 row (carried from R257): must cite cumulative 3161 (3160 at 855d6f0
    # + 1 new checker in the R256 content commit); the git figure is
    # re-derived below.
    r255_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R255 |")]
    r255_row_ok = (len(r255_row) == 1 and "cumulative 3161 paths" in r255_row[0])
    chk("index R255 row cumulative == 3161 (3160 at 855d6f0 + 1 checker)", r255_row_ok)

    # R256 row (carried from R258): must cite cumulative 3164 (3163 at 46fde45
    # + 1 new checker in the R257 content commit); the git figure is
    # re-derived below.
    r256_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R256 |")]
    r256_row_ok = (len(r256_row) == 1 and "cumulative 3164 paths" in r256_row[0])
    chk("index R256 row cumulative == 3164 (3163 at 46fde45 + 1 checker)", r256_row_ok)

    # R274 row (carried from R276): must cite cumulative 3218 (3217 at 2de586d
    # + 1 new checker in the R275 content commit); the git figure is
    # re-derived below.
    r257_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R274 |")]
    r257_row_ok = (len(r257_row) == 1 and "cumulative 3218 paths" in r257_row[0])
    chk("index R274 row cumulative == 3218 (3217 at 2de586d + 1 checker)", r257_row_ok)

    # R275 row (new this round): must cite cumulative 3221 (3220 at 7e44e0c
    # + 1 new checker in the R276 content commit); the git figure is
    # re-derived below.
    r275_row = [l for l in il if l.startswith("| PR119 BODY RESTRUCTURE R275 |")]
    r275_row_ok = (len(r275_row) == 1 and "cumulative 3221 paths" in r275_row[0])
    chk("index R275 row cumulative == 3221 (3220 at 7e44e0c + 1 checker)", r275_row_ok)

    # R244 correction (carried from R245): the R241 row must carry the
    # ĐÍNH CHÍNH R242 note with the refreshed R241 payload version (sha 83d221b8).
    r241_dc_ok = (len(r241_row) == 1 and "ĐÍNH CHÍNH R242" in r241_row[0]
                 and "83d221b8" in r241_row[0]
                 and "KHÔNG ĐƯỢC ĐĂNG" in r241_row[0])
    chk("index R241 row carries ĐÍNH CHÍNH R242 (payload refresh sha 83d221b8)", r241_dc_ok)

    # R241 correction (carried from R241): the R239 row must carry the
    # ĐÍNH CHÍNH R241 note with the refreshed R239 payload version (sha 1e38e781).
    r239_dc_ok = (len(r239_row) == 1 and "ĐÍNH CHÍNH R241" in r239_row[0]
                 and "1e38e781" in r239_row[0]
                 and "KHÔNG ĐƯỢC ĐĂNG" in r239_row[0])
    chk("index R239 row carries ĐÍNH CHÍNH R241 (payload refresh sha 1e38e781)", r239_dc_ok)

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
                                         ("R227", "2938722", 3077),
                                         ("R228", "7aa25a8", 3080),
                                         ("R229", "644d4ab", 3083),
                                         ("R230", "9482f4d", 3086),
                                         ("R231", "c3a4eec", 3089),
                                         ("R232", "233f0b5", 3092),
                                         ("R233", "b50891a", 3095),
                                         ("R234", "db681a3", 3098),
                                         ("R235", "539feb0", 3101),
                                         ("R236", "5b80666", 3104),
                                         ("R237", "e79db7b", 3107),
                                         ("R238", "08dd58b", 3110),
                                         ("R239", "928a525", 3113),
                                         ("R240", "dc9331a", 3116),
                                         ("R241", "91a543e", 3119),
                                         ("R242", "e61a658", 3122),
                                         ("R243", "44f1017", 3125),
                                         ("R244", "ff7f373", 3128),
                                         ("R245", "6869aa1", 3131),
                                         ("R246", "c919f88", 3134),
                                         ("R247", "cf24619", 3137),
                                         ("R248", "aa0eef6", 3140),
                                         ("R249", "8bebd8a", 3143),
                                         ("R250", "a6319ed", 3146),
                                         ("R251", "fa41682", 3149),
                                         ("R252", "cec686f", 3152),
                                         ("R253", "a8fb12d", 3155),
                                         ("R254", "c15258e", 3158),
                                         ("R255", "e53b835", 3161),
                                         ("R256", "e41cfda", 3164),
                                         ("R257", "134ebaa", 3167),
                                         ("R258", "15ad480", 3170),
                                         ("R259", "f4f9255", 3173),
                                         ("R260", "2beeb78", 3176),
                                         ("R261", "ffaaf3b", 3179),
                                         ("R262", "e373cb5", 3182),
                                         ("R263", "7ac9433", 3185),
                                         ("R264", "ecee5f7", 3188),
                                         ("R265", "e444f0c", 3191),
                                         ("R266", "9ce3e24", 3194),
                                         ("R267", "b062dd1", 3197),
                                         ("R268", "75e1d55", 3200),
                                         ("R269", "3ae052f", 3203),
                                         ("R270", "16dfcfe", 3206),
                                         ("R271", "312d680", 3209),
                                         ("R272", "5dc1302", 3212),
                                         ("R273", "56926f3", 3215),
                                         ("R274", "c7117ef", 3218)):
        n = len(git("diff", "--name-only", BASE, content_sha).splitlines())
        chk(f"row-convention {row_n} cumulative {expected} == diff at {content_sha}",
            n == expected, str(n))

    n_commits = int(git("rev-list", "--count", f"{BASE}..{COVER}").strip())
    chk("git commits cf17178..7e44e0c == 741", n_commits == 741, str(n_commits))
    n_files = len(git("diff", "--name-only", BASE, COVER).splitlines())
    chk("git files cf17178..7e44e0c == 3220", n_files == 3220, str(n_files))
    stat = git("diff", "--shortstat", BASE, COVER)
    chk("git additions == 387773, deletions 0",
        "387773 insertions(+)" in stat and "deletion" not in stat, stat.strip())

    mt = subprocess.run(["git", "merge-tree", "--write-tree", COVER, INTEGRATION],
                        cwd=ROOT, capture_output=True, text=True)
    tree = mt.stdout.splitlines()[0] if mt.stdout else ""
    chk("merge-tree 7e44e0c vs integration exit 0, tree 13026b07",
        mt.returncode == 0 and tree.startswith("13026b07"), tree)

    chk("body head line 7e44e0c/741/3220",
        "**Head: `7e44e0c` · 741 commit · 3220 file**" in body)
    head_line = body.splitlines()[4]
    chk("body head line additions 387773 + Gói 39 ID 6815238814 (lesson 36)",
        "additions 387773" in head_line and "6815238814" in head_line
        and "6835238814" not in body and "385669" not in body,
        head_line[:60])
    chk("body has R275 paragraph", "- **PR119 BODY RESTRUCTURE R275**" in body)
    title_line = body.splitlines()[0]
    chk("body title mentions R37 and R275",
        "PR119 BODY RESTRUCTURE R37" in title_line
        and "PR119 BODY RESTRUCTURE R275" in title_line, title_line[-60:])
    chk("body title has full R93..R275 sequence (R94 restored)",
        all(f"PR119 BODY RESTRUCTURE R{n}" in title_line for n in range(93, 276)),
        "R94 restored, R275 added")
    chk("body index reference at 7e44e0c", "(head `7e44e0c`)" in body)
    chk("body R276 update note", "R276 (lượt cập nhật này)" in body)

    # R243 correction: the "lượt cập nhật này" sentence must carry the
    # correct own-round reference (R243), and the defective R242 form
    # ("chính R242 sẽ gộp" -- R242's own commits fold at R243, not R242's
    # predecessor) must be gone.
    sentence_ok = ("R276 (lượt cập nhật này) đã gộp 2 commit của R275 vào index; "
                   "2 commit của chính R276 sẽ gộp ở lần cập nhật index tiếp theo." in body
                   and "2 commit của chính R275 sẽ gộp" not in body
                   and "2 commit của chính R274 sẽ gộp" not in body)
    chk("body 'lượt cập nhật này' sentence corrected (chính R276, no chính R274/R275)",
        sentence_ok)

    # Body "Ghi chú" line corrected this round: R158/R276, range R3-R183,
    # report list complete through R275, no double slash.
    note25 = [l for l in body.splitlines() if l.startswith("Ghi chú R158/")]
    note25_ok = (len(note25) == 1 and note25[0].startswith("Ghi chú R158/R276:")
                 and "R3–R183" in note25[0] and "R203/R204/R205/R206/R207/R208/R209/R210/R211/R212/R213/R214/R215/R216/R217/R218/R219/R220/R221/R222/R223/R224/R225/R226/R227/R228/R229/R230/R231/R232/R233/R234/R235/R236/R237/R238/R239/R240/R241/R242/R243/R244/R245/R246/R247/R248/R249/R250/R251/R252/R253/R254/R255/R256/R257/R258/R259/R260/R261/R262/R263/R264/R265/R266/R267/R268/R269/R270/R271/R272/R273/R274/R275" in note25[0]
                 and "//" not in note25[0])
    chk("body Ghi-chú line corrected (R179/R276, R3-R183, list complete)", note25_ok)

    # R275 note + compaction: 182 compact lines (R2-R183; the per-round
    # loop covers R2-R183),
    # each < 400 chars, body < 105k chars.
    compact_ok = "R276 (lượt cập nhật này)" in body
    compact_lines = [l for l in body.splitlines() if "(gọn — chi tiết trong index)" in l]
    compact_detail = f"compact lines: {len(compact_lines)}, body chars: {len(body)}"
    per_round_ok = True
    for n in range(2, 184):
        cand = [l for l in body.splitlines()
                if l.startswith(f"- **PR119 BODY RESTRUCTURE R{n}**")]
        if len(cand) != 1 or len(cand[0]) >= 400 or "(gọn" not in cand[0]:
            per_round_ok = False
            compact_detail += f"; R{n} FAIL"
    # Full paragraphs stay ascending: R275 after R274, before the compact block.
    bl = body.splitlines()
    i258 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R275**"))
    i257 = next(i for i, l in enumerate(bl) if l.startswith("- **PR119 BODY RESTRUCTURE R274**"))
    order_ok = i258 == i257 + 1
    chk("body R276 note + R2-R183 compacted (182 lines <400ch, body <105k)",
        compact_ok and len(compact_lines) == 182 and per_round_ok
        and len(body) < 105000 and order_ok, compact_detail)

    # R36 restoration (carried from R242): the R36 full paragraph was
    # silently deleted at the R47 content commit (1a601be); R242 restores
    # it directly in compact form (content 386216b, report/head 9ec1fd9).
    r36_line = [l for l in bl if l.startswith("- **PR119 BODY RESTRUCTURE R36**")]
    r36_ok = (len(r36_line) == 1 and "386216b" in r36_line[0]
              and "9ec1fd9" in r36_line[0]
              and "(gọn — chi tiết trong index)" in r36_line[0])
    chk("body R36 compact line restored (content 386216b, head 9ec1fd9)", r36_ok)

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
    out = {"checkpoint": "PR119 BODY RESTRUCTURE R275",
           "validator": "check_pr119_restructure_r276_v1.py",
           "checks": {"total": len(checks), "passed": len(checks) - len(failures)},
           "failures": failures, "details": checks,
           "status": "PASS" if not failures else "FAIL"}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['status']} {out['checks']['passed']}/{out['checks']['total']}")
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
