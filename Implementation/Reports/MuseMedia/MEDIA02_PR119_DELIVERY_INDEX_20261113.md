# MEDIA-02 — PR #119 Delivery Index (head `fad0994`)

Chi tiết đầy đủ từng khối bàn giao của PR #119, chuyển ra khỏi mô tả PR
khi mô tả cũ (114.929 ký tự tại head `be9ccb8`) chạm trần truyền của connector
(131.072 byte cho một tham số). Mô tả PR hiện tại là bản tóm tắt gọn
(`MEDIA02_PR119_BODY_V2_20261113.md`); mọi SHA trong mô tả đều có ở bảng dưới.

## Mốc xác minh

- Head nhánh `muse/media-production-20261104`: `fad09944c040d5e546e5ca1d23435c5d5a8df14f`
- Commit trên nhánh (diff từ merge-base `cf17178`): **227 commit / 2449 file** (khớp API PR: commits 227, changed_files 2449, additions 228299, deletions 0)
- Integration: `f3db6b3` (fetch 2026-11-14 ~21:45 JST, không đổi)
- Mergeable: true (API đọc 2026-11-14 ~21:45 JST tại head `fad0994`, mergeable_state clean — CI đã chạy xong trên head mới; `git merge-tree --write-tree` vs `f3db6b3` exit 0, 0 conflict, tree `a27da0a5…`)
- Issue #116: 34 comment, mới nhất ACK `6862732081` (CP5 + M-G CP10 + R2, đăng 2026-11-14 ~04:24 JST); trước đó Gói 39 của Codex `6815238814`, không chỉ đạo mới.
- Scope audit toàn nhánh: 1 violation duy nhất là `.gitattributes` — artifact của cách tính diff từ merge-base `cf17178` (chưa có các dòng LF); file này byte-identical với integration, không phải lệch nội dung thật.

## Tổng quan bàn giao (số thật tại head `e13e3f5`)

| Hạng mục | Số liệu |
|---|---|
| Campaign | 20 scene / 63 shot / 378 s; timing JSON + SRT UTF-8/NFC; dialogueCues = 21 |
| Video | animatic P0 v3 72 s + clip riêng 20/20 scene; motion 38/38 action shot; 26/26 hold slice; B take 20/20 scene |
| VO | 21/21 cửa sổ có VO dự thảo; palette 11 vai / 11 giọng; 20 pickup; mix v2 14 mix (Art_Source) |
| Nhạc sáng tác gốc | 13 cue + 4 stinger; 13 ambience + 26 variant; score 15/15 slot, 16 cue có intensity layer |
| SFX | coverage 63/63 key; 18/18 draft variant đã duyệt (source-only, binding UNSUPPORTED) |
| Runtime audio | 783 file (composed 162, ported 541) |
| Standard 720p | 21 MP4, tổng 148.002.469 B (integer 2× NN, không phải 720p native); 14 entry mang soundtrack v2 |
| Prologue CIN_000 | film 87,367 s + bản phụ đề + bản 720p phụ đề + bản phụ đề v2 theo narration History (M-B CP5, 640 + 720p) |
| Ear-audition pack | v1 196 item + v2 delta 58 item = 254 item; NOT_AUDITIONED |
| QA | `validate_media_deliveries` PASS 0 mismatch; `verify_runtime_delivery` PASS; fresh-checkout baseline `14b588c` + verification scoped cho delta M-B CP4 + prologue fix (M-G CP9) và delta M-B CP5 (M-G CP10) |

Mốc quyết định DEC-MEDIA-P0-20261105: Q1 CIN_001_S05 bản B “Đầu kia! Giữ giúp tôi đầu kia!”, VO 24.8–28.5 s; Q2 Ly An voice off-screen trong CIN_004, characters chỉ `BOSS_MANG_COT`; Q3 alternate CIN006 có takeId/version riêng, không thay canon; Q4 Hạ Mặc/Sầm cinematic-only staging, không nhân đôi persistent ID. Tên canonical “Tạ Vân Khanh”.


## Bảng khối bàn giao (theo thứ tự thời gian)

Cột Nội dung = commit chứa asset/tool; cột Báo cáo/Head = commit báo cáo (cũng là head nhánh tại thời điểm khối đó xong).

| Khối | Nội dung | Báo cáo/Head | Kết quả (tóm tắt) | Kiểm chứng |
|---|---|---|---|---|
| CP01 | `440791e` | `—` | checkpoint 01 - re-baseline, P0 timing lock + SRT drafts (DEC-MEDIA-P0) | — |
| CP02 | `37c940c` | `—` | checkpoint 02 - P0 stem loudness complete (11/11) + stem-per-shot table | — |
| CP03 | `8be1af2` | `—` | checkpoint 03 - P0 storyboard/animatic 72s/12 shots (MP4 review + OGV runtime + poster) | — |
| CP04 | `8d25207` | `—` | checkpoint 04 - P0 VO drafts 3 lines (fit windows, 72s VO timeline) | — |
| CP05 | `5571537` | `—` | checkpoint 05 - CIN_006 (P1) timing 18s/3 shots + SRT draft (DEC Q3/Q4) | — |
| CP06 | `5725caf` | `—` | checkpoint 06 - M3 campaign timing pack 16 scenes / 48 shots / 288s + SRT drafts (all windows PROPOSED) | — |
| CP07 | `1db3f23` | `—` | checkpoint 07 - M4/M5 music+ambience pack 22 cues measured from real bytes (runtime OGG + master FLAC) | — |
| CP08 | `0ea00b1` | `279f7ef` | checkpoint 08 - M5 SFX+UI pack 173 cues measured from real bytes (all variants, runtime WAV + master FLAC) | — |
| CP09 | `18e5887` | `e3e9800` | checkpoint 09 - M7/V4 cross-validation of all media deliverables against real bytes (1093 audio files, 20 scenes timing+SRT, P0 animatic, P0 VO drafts; 0 mismatches) | — |
| CP10 | `e1e558b` | `5d8cc70` | checkpoint 10 - M6 runtime delivery (545 audio files + 20 scenes timing/SRT verified from real bytes, runtime manifests) | — |
| CP11 | `f6df4b2` | `7a94037` | checkpoint 11 - M8 handover/QA (runtime + source re-validation PASS, consolidated handover) | — |
| CP12 | `a242af3` | `3f34f0d` | checkpoint 12 - M8 continuous QA after integration merge f383233 (PR #118), runtime + source re-validation PASS, re-baseline | — |
| CP13 | `3243c0c` | `7891265` | checkpoint 13 - M8 animatic revision v2 (D4 panel fixes), P0 sheet/spec/outputs v2, runtime + source re-validation PASS | — |
| CP14 | `94d7a99` | `67f0d92` | checkpoint 14 - Gói 30 fix (a) dialogueCues from parsed timing/SRT + cross-manifest validator | — |
| CP15 | `68d6e52` | `509246d` | checkpoint 15 - Gói 30 fix (b) LF + LFS (24 raw binaries to pointers) | — |
| CP16 | `b7d83f0` | `7d7c986` | checkpoint 16 - Gói 30 fix (c) CIN_002_S02 corrected keyframe + separate 16:9 keyframes (animatic v3) | — |
| CP17 | `37da3b1` | `b96cff3` | checkpoint 17 - campaign VO drafts (17 cues, 378 s timeline) + runtime delivery | — |
| CP18 | `385d615` | `f9ecf8b` | checkpoint 18 - per-scene clip export (Goi 30 item 6) | — |
| CP19 | `2681b4b` | `1bf63b8` | checkpoint 19 - CIN_006 VO drafts (canonical + alternate take) + runtime delivery (21/21 dialogue windows) | — |
| CP20 | `7652195` | `27a7966` | checkpoint 20 - P0 draft mix (3 scenes + 72 s review, ducking + loop QA) + runtime delivery | — |
| CP21 | `cbb4c7e` | `0c2cf9a` | checkpoint 21 - CIN_005 animated take (18 s, 3 keyframes + Ken Burns clip) + runtime delivery | — |
| CP22 | `ebef39f` | `f36543e` | checkpoint 22 - CIN_006 animated take (3 storyboard keyframes + 18 s Ken Burns clip) + runtime delivery | — |
| CP23 | `b3f99c3` | `44ec23e` | checkpoint 23 - CIN_009 animated take (3 storyboard keyframes + 18 s Ken Burns clip) + runtime delivery | — |
| CP24 | `bd53640` | `030da0d` | checkpoint 24 - CIN_020 animated take (3 storyboard keyframes + 18 s Ken Burns clip) + CIN_009 manifest title fix + runtime delivery | — |
| CP25 | `68850d1` | `5ef9451` | checkpoint 25 - campaign video batch: animated takes for the remaining 13 campaign scenes (CIN_003, CIN_007, CIN_008, CIN_010-CIN_019), 3 storyboard keyframes + 18 s Ken Burns clip each; all 20 scenes now carry video; ge… | — |
| CP26 | `eb44767` | `2936280` | composed music pack | — |
| CP26 (erratum) | `532924b` | `—` | checkpoint 26 report erratum: scope audit is 1058 paths (not 1062) | — |
| CP27 | `4b05bcc` | `34a05d5` | prologue film CIN_000 - source re-validation PASS 0 mismatches (audio files checked 1125, prologue files 42, campaign 20 scenes / 21 dialogues unchanged), runtime re-verify PASS 0 mismatches (589 audio files, prologue fi… | PASS 0 mismatches |
| CP28 | `a662218` | `9a19464` | prologue subtitled variant - source re-validation PASS 0 mismatches (audio files checked 1125, prologue files 45), runtime re-verify PASS 0 mismatches (589 audio files, prologue files 7); scope audit 1110 paths 0 violati… | PASS 0 mismatches |
| CP29 | `e9d1ce1` | `b279182` | P0 draft mix v2 - source re-validation PASS 0 mismatches (audio files checked 1125, p0_mix_v2 4/4), runtime re-verify PASS 0 mismatches (593 audio files); scope audit 1122 paths 0 violations vs integration f0859d0 | PASS 0 mismatches |
| CP30 | `ad71e89` | `e08b1be` | original composed ambience - source re-validation PASS 0 mismatches (audio files checked 1151, composed ambience 13 cues / 26 files), runtime re-verify PASS 0 mismatches (606 audio files); scope audit 1153 paths 0 violat… | PASS 0 mismatches |
| CP31 | `05b4cab` | `0f2678f` | P0 draft mix v3 - source re-validation PASS 0 mismatches (audio files checked 1151, p0_mix_v3 4/4), runtime re-verify PASS 0 mismatches (610 audio files); scope audit 1164 paths 0 violations vs integration f0859d0 | PASS 0 mismatches |
| CP32 | `6ec41d7` | `f2975c5` | Goi 31 item 2 shot fixes + status phrasing - source re-validation PASS 0 mismatches (audio files checked 1151, campaign batch keyframes 39/39), runtime re-verify PASS 0 mismatches (610 audio files); scope audit 1182 path… | PASS 0 mismatches |
| CP33 | `fa7ab60` | `—` | Goi 31 item 3 A/B review shortlist - P0 mixes v1/v2/v3, music/ambience, VO pronunciation/proper names, loop seams; 6 M3U-content playlists (.txt per scope policy: .m3u not in mediaExtensions) + defect table D-01..D-12; N… | PASS 0 mismatches |
| CP34 | `bd5a2e8` | `ea1a3ee` | Goi 31 item 4 minimal runtime pack - source re-validation PASS 0 mismatches (audio files checked 1151, CIN_006 mix v1 1/1), runtime re-verify PASS 0 mismatches (610 -> 611 audio files); scope audit 1202 paths 0 violation… | PASS 0 mismatches |
| CP35 | `3f59b9a` | `de92bce` | Goi 31 item 5 fresh-checkout verification tool + negative control - fresh clone FAIL as expected (8 policy lines missing vs integration 6f2b465, 22/22 OGV LFS pointers); worktree FAIL only on policy (OGV 22/22 real bytes… | PASS 0 mismatches |
| CP36 | `50da8d1` | `46b3d84` | D-12 name-label fix (scope audit at content head 1214 paths / 0 violations vs 6f2b465) | — |
| CP37 | `eea3c46` | `a1e1e72` | CIN_003 draft mix v1 + runtime mux (scope audit 1221 paths / 0 violations vs 6f2b465) | PASS 0 mismatches |
| CP38 | `b46420a` | `3973654` | CIN_005 draft mix v1 + runtime mux (scope audit 1228 paths / 0 violations vs 6f2b465) | PASS 0 mismatches |
| CP39 | `36610dc` | `f3884c7` | CIN_007 draft mix v1 + runtime mux (scope audit 1235 paths / 0 violations vs 6f2b465) | PASS 0 mismatches |
| CP40 | `3c79856` | `3b9fa57` | CIN_008 draft mix v1 + runtime mux (scope audit 1242 paths / 0 violations vs 6f2b465) | PASS 0 mismatches |
| — (fix) | `9deb06c` | `—` | apply owner OGV and LF checkout policy | — |
| — (fix) | `103c63c` | `—` | keep delivery manifests and QA JSON LF in fresh checkouts | — |
| — (merge) | `23ac4fb` | `—` | Merge pull request #127 from khanhcoder97/codex/muse-checkout-policy-20261108 | — |
| CP41 | `4a39bc4` | `e61dd4a` | CIN_009 draft mix v1 + runtime mux (scope audit 1249 paths / 0 violations vs 6f2b465) | PASS 0 mismatches |
| — (merge) | `9f264ef` | `—` | Merge remote muse/media-production-20261104 (PR #127 owner checkout policy OGV/LF) into checkpoint 41 | — |
| CP42 | `c4ceb3f` | `f4cfa9f` | CIN_010 draft mix v1 + runtime mux (scope audit 1257 paths / 1 known .gitattributes violation from owner-merged PR #127; content-only 16 paths / 0 violations) | PASS 0 mismatches |
| CP43 | `4e0e5b3` | `8af4d37` | playback metadata WO32 item 4 (scope audit 1262 paths / 1 known .gitattributes violation from owner-merged PR #127; content-only 6 paths / 0 violations) | — |
| CP44 | `c797856` | `aaba7c4` | pronunciation table WO32 item 3 (scope audit 1265 paths / 1 known .gitattributes violation from owner-merged PR #127; content-only 4 paths / 0 violations) | — |
| CP45 | `2209047` | `694ddb6` | CIN_011 draft mix v1 + runtime mux (scope audit 1272 paths / 1 known .gitattributes violation from owner-merged PR #127; content-only 18 paths / 0 violations) | — |
| CP46 | `c561933` | `b14d7de` | CIN_012 draft mix v1 + runtime mux (scope audit 1279 paths / 1 known .gitattributes violation from owner-merged PR #127; content-only 18 paths / 0 violations) | — |
| CP47 | `33a4811` | `2c2a5d0` | CIN_013 draft mix v1 + runtime mux (scope audit 1286 paths / 1 known .gitattributes violation — byte-identical to new integration 6f79853, merge-base artifact; content-only 18 paths / 0 violations) | — |
| CP48 | `7954116` | `40fabee` | CIN_014 draft mix v1 + runtime mux (scope audit 1293 paths / 1 known .gitattributes violation — byte-identical to new integration 6f79853, merge-base artifact; content-only 18 paths / 0 violations) | — |
| CP49 | `74e741f` | `22afdab` | CIN_015 draft mix v1 + runtime mux (scope audit 1300 paths / 1 known .gitattributes violation — byte-identical to new integration 6f79853, merge-base artifact; content-only 18 paths / 0 violations) | — |
| CP50 | `38b91b0` | `973d5a2` | CIN_016 draft mix v1 + runtime mux (scope audit 1307 paths / 1 known .gitattributes violation — byte-identical to new integration 6f79853, merge-base artifact; content-only 18 paths / 0 violations) | — |
| CP51 | `67d8478` | `d51e727` | CIN_017 draft mix v1 + runtime mux (scope audit 1314 paths / 1 known .gitattributes violation — byte-identical to new integration 6f79853, merge-base artifact; content-only 18 paths / 0 violations) | — |
| CP52 | `9bdfb17` | `0492f0a` | CIN_018 draft mix v1 + runtime mux (scope audit 1321 paths / 1 known .gitattributes violation — byte-identical to new integration 6f79853, merge-base artifact; content-only 18 paths / 0 violations) | — |
| WO37 M-C | `da1b7d5` | `6d882b9` | motion/final-picture ledger v1 (63 shots; validator PASS 0 mismatches; scope audit content-only 4 paths / 0 violations; push deferred -- main thread CP53 in flight in this clone) | PASS 0 mismatches |
| CP53 | `e465fd8` | `717625b` | CIN_019 draft mix v1 (validations PASS 0 mismatches; cumulative scope audit vs integration 6f79853 carries the 1 known .gitattributes merge-base artifact) | PASS 0 mismatches |
| CP54 | `2f2e407` | `2ea538a` | CIN_020 draft mix v1 (scope audit content-only 18 paths / 0 violations; validations PASS 0 mismatches; WO37 M-B big checkpoint 1 complete - all 21 entries carry embedded soundtracks) | PASS 0 mismatches |
| WO37 M-C CP2 | `ae7cb68` | `—` | P0 motion/AB — 12 P0 shots procedural pose animation (5 poses, 10 pose/s), 3 scene B takes + 3 A/B videos; generated-strip route abandoned (8 rejected strips, panorama defect); validator 282/282 PASS | — |
| WO37 M-C CP3a | `f69d374` | `57a6610` | campaign motion priority-2 (validator 777/777 PASS; scope audit content-only 235 paths / 0 violations) | — |
| WO37 M-D CP1 | `ef924ec` | `9997c03` | whole-game score batch 1 (MD1 validator PASS 0 mismatches; source re-validation PASS 0 mismatches; runtime re-verify PASS 0 mismatches; scope audit content-only 28 paths / 0 violations; cumulative 1700 paths / 1 known .g… | PASS 0 mismatches |
| WO37 M-D CP2 | `f2f2d7f` | `063c98b` | intro/outro + stems + phase layers (MD2 validator PASS 0 mismatches; source re-validation PASS 0 mismatches; runtime re-verify PASS 0 mismatches; scope audit content-only 82 paths / 0 violations; cumulative 1781 paths / … | PASS 0 mismatches |
| WO37 M-D CP3 | `6c487a7` | `765bb18` | intro/outro + stems + phase layers (MD3 validator PASS 0 mismatches; source re-validation PASS 0 mismatches; runtime re-verify PASS 0 mismatches; MD1/MD2 validators re-run PASS; scope audit content-only 104 paths / 0 vio… | PASS 0 mismatches |
| WO37 M-D CP4 | `3d31c4a` | `e228e44` | phase layers (MD4 validator PASS 0 mismatches; source re-validation PASS 0 mismatches; runtime re-verify PASS 0 mismatches; MD1/MD2/MD3 validators re-run PASS; scope audit content-only 14 paths / 0 violations; cumulative… | PASS 0 mismatches |
| WO37 M-D CP5 | `eb98069` | `4a2f9a6` | phase layers (MD5 validator PASS 0 mismatches; source re-validation PASS 0 mismatches; runtime re-verify PASS 0 mismatches; MD1/MD2/MD3/MD4 validators re-run PASS; scope audit content-only 14 paths / 0 violations; cumula… | PASS 0 mismatches |
| WO37 M-D CP6 | `3a573a0` | `bf3b1e0` | phase layers (MD6 validator PASS 0 mismatches; source re-validation PASS 0 mismatches; runtime re-verify PASS 0 mismatches; MD1/MD2/MD3/MD4/MD5 validators re-run PASS; scope audit content-only 14 paths / 0 violations; cu… | PASS 0 mismatches |
| WO37 M-D CP7 | `955eb52` | `184e1a8` | phase layers (MD7 validator PASS 0 mismatches; source re-validation PASS 0 mismatches; runtime re-verify PASS 0 mismatches; MD1/MD2/MD3/MD4/MD5/MD6 validators re-run PASS; scope audit content-only 18 paths / 0 violations… | PASS 0 mismatches |
| WO37 M-D CP8 | `b2b2bda` | `aef0a33` | phase layer (MD8 validator PASS 0 mismatches; source re-validation PASS 0 mismatches; runtime re-verify PASS 0 mismatches; MD1/MD2/MD3/MD4/MD5/MD6/MD7 validators re-run PASS; scope audit content-only 10 paths / 0 violati… | PASS 0 mismatches |
| WO37 M-D CP9 | `b760197` | `e2676a3` | ear-audition pack (CP9 validator PASS 0 mismatches, 196 items hashed; source re-validation PASS; runtime re-verify PASS; runtime audio unchanged 737; scope audit content-only 11 paths / 0 violations; cumulative 1964 path… | PASS 0 mismatches |
| WO37 M-F CP1 | `da7e22b` | `f2cff6e` | voice palette + pickups + pronunciation review pack (MF CP1 validator PASS 0 mismatches, source re-validation PASS 0 mismatches, runtime re-verify PASS 0 mismatches; scope audit content-only 71 paths / 0 violations; cumu… | PASS 0 mismatches |
| WO37 M-E CP1 | `48474c3` | `41a6faa` | real variants for composed ambience (ME CP1 validator PASS 0 mismatches, source re-validation PASS 0 mismatches, runtime re-verify PASS 0 mismatches; scope audit content-only 57 paths / 0 violations; cumulative 2091 path… | PASS 0 mismatches |
| WO37 M-G CP1 | `6405d3a` | `c60088c` | fresh-checkout QA at 41a6faa (MG CP1 validator PASS 0 mismatches, item5 PASS 5/5, runtime re-verify PASS 0 mismatches; scope audit content-only 1 path / 0 violations; cumulative 2096 paths / 1 known .gitattributes merge-… | PASS 0 mismatches |
| WO37 M-G CP2 | `eb74100` | `14504fb` | fresh-checkout QA at c60088c (MG CP2 validator PASS 0 mismatches, item5 PASS 5/5, runtime re-verify PASS 0 mismatches; scope audit content-only 1 path / 0 violations; cumulative 2101 paths / 1 known .gitattributes merge-… | PASS 0 mismatches |
| WO37 M-G CP3 | `5b03559` | `e7cb9e4` | fresh-checkout QA at 14504fb (MG CP3 validator PASS 0 mismatches, item5 PASS 5/5, runtime re-verify PASS 0 mismatches; scope audit content-only 1 path / 0 violations; cumulative 2106 paths / 1 known .gitattributes merge-… | PASS 0 mismatches |
| WO37 M-G CP4 | `a4d383e` | `b09d718` | Windows-compatibility static audit at e7cb9e4 (validator PASS 0 mismatches; scope audit content-only 2 paths / 0 violations; cumulative 2112 paths / 1 known .gitattributes merge-base artifact) | PASS 0 mismatches |
| WO37 M-G CP5 | `a764b7d` | `14b588c` | fresh-checkout QA at b09d718 (validator PASS 0 mismatches, item5 PASS 5/5, runtime re-verify PASS 0 mismatches; LFS batch API failing at proxy — objects seeded from local stores + fsck 0 errors; cumulative 2118 paths / 1… | PASS 0 mismatches |
| WO37 M-G CP6 | `8c66712` | `cdbab7c` | fresh-checkout QA at 14b588c (pure network git lfs pull exit 0 in 13m06s, 2013/2013 objects, no seeding — network path re-proven; validator PASS 0 mismatches, item5 PASS 5/5, runtime re-verify PASS 0 mismatches; cumulati… | PASS 0 mismatches |
| WO38 M38-A | `9a77227` | `67a9c74` | P0 candidate for real review (builder hash re-verification all match, checker 11/11 PASS 0 failures; scope audit 7 paths total / 0 violations; cumulative 2130 paths / 1 known .gitattributes merge-base artifact) | — |
| WO38 M38-B | `0d1c073` | `4c53683` | selective P0 runtime ingest guide (exactly-one-audio-path rule EMBEDDED_SOUNDTRACK_ONLY, cues/subtitles/seams/fallback, license/provenance, size budget +4,492,460 B; checker 27/27 PASS; scope audit block 6 paths / 0 viol… | — |
| WO37 M-C CP4 | `4e22cf8` | `9ab006f` | continuity ledger v1 (checker 326/326 PASS; scope audit block 3 paths / 0 violations; cumulative 2141 paths / 1 known .gitattributes merge-base artifact) | — |
| WO37 M-C CP5 | `ed1691d` | `818cd95` | continuity ledger v2 (checker 389/389 PASS; scope audit block 14 paths / 0 violations; cumulative 2146 paths / 1 known .gitattributes merge-base artifact) | — |
| WO37 M-B CP1 | `1f21952` | `8f8282c` | P0 soundtrack A/B (checker 32/32 PASS; scope audit block 7 paths / 0 violations; cumulative 2155 paths / 1 known .gitattributes merge-base artifact) | — |
| WO37 M-G CP7 | `27b4bcf` + `9cd5808` | `aa1cd97` | fresh-checkout QA at head 9cd5808 (validator 8/8 PASS; item-5 5/5 PASS; runtime re-verify PASS; D1 4 pointer files restored + D2 per-scene timing sync; scope audit block 1+4 paths / 0 violations; cumulative 2158 paths / … | — |
| WO37 M-B CP2 | `563eb0d` | `c0caf22` | standard 720p versions (checker 237/237 PASS; scope audit block 27 paths / 0 violations; cumulative 2189 paths / 1 known .gitattributes merge-base artifact) | — |
| WO37 M-B CP3 | `d2bff12` | `d9e8e90` | standard 720p subtitled variant (checker 18/18 PASS; scope audit block 4 paths / 0 violations; cumulative 2195 paths / 1 known .gitattributes merge-base artifact) | — |
| WO37 M-C CP3b | `1039b12` | `f0b9ed5` | Ken Burns holds for CIN_014/CIN_017 (checker 123/123 PASS; scope audit block 20 paths / 0 violations; cumulative 2217 paths / 1 known .gitattributes merge-base artifact) | — |
| WO37 M-E CP2a | `f1b77e1` | `5afc76b` | SFX coverage audit + proposal (checker 700/700 PASS; scope audit block 3 paths / 0 violations; cumulative 2222 paths / 1 known .gitattributes merge-base artifact) | — |
| WO37 M-C CP3c | `94ea91d` | `b1472f2` | Ken Burns hold slice for CIN_020_S03 (checker 49/49 PASS; scope audit block 8 paths / 0 violations; cumulative 2229 paths / 1 known .gitattributes merge-base artifact) | — |
| WO39 M39-A CP1 | `78ecd26` | `64d6d70` | guard+grass SFX draft (validator 186/186 PASS; scope audit block 10 paths / 0 violations; cumulative 2241 paths / 1 known .gitattributes merge-base artifact) | — |
| WO39 M39-A CP2 | `dbd8270` | `4e2abcd` | 4 weapon identities SFX draft (validator 296/296 PASS; scope audit block 16 paths / 0 violations; cumulative 2259 paths / 1 known .gitattributes merge-base artifact) | — |
| WO39 M39-B CP1 | `777421e` | `129b363` | level-matched A/B voice palette review (validator 788/788 PASS; scope audit block 44 paths / 0 violations; cumulative 2305 paths / 1 known .gitattributes merge-base artifact) | — |
| WO37 M-F CP2 | `2d7f02a` | `81f33e6` | checker PASS 369/369, scope audit block 43 paths / 0 violations (cumulative 2350 / 1 known .gitattributes artifact) | PASS 369/369 |
| WO37 M-G CP8 | `5550d61` | `8e311aa` | fresh-checkout verification of M-F CP2 delta (validator PASS 117/117, 0 defects, scope audit block 2 paths / 0 violations, cumulative 2354 paths / 1 known .gitattributes artifact) | PASS 117/117 |
| WO37 M-D CP10 | `3614d87` | `7f461da` | ear-audition pack v2 delta (validator PASS 633/633, scope audit block 5 paths / 0 violations, cumulative 2360 paths / 1 known .gitattributes artifact) | PASS 633/633 |
| WO37 M-B CP4 | `21bc9ef` | `41bfbae` | standard 720p re-rendered with v2 mixes (validator PASS 271/271, scope audit block 17 paths / 0 violations, cumulative 2365 paths / 1 known .gitattributes artifact) | PASS 271/271 |
| PROLOGUE V1 FIX | `962b6df` | `be9ccb8` | narration restored in the CP27 mix (plumbing-only fix, reproducible render), runtime CIN_000 + variants re-derived; checker 50/50 PASS, runtime verify PASS, validate_media prologue clean (8 pre-existing SCENE-CLIPS misma… | PASS 0 mismatches |
| SCENE-CLIPS MANIFEST FIX | `53472cf` | `6df7e24` | 8 pre-existing validator mismatches closed ; scope audit block 5 paths / 0 violations, Scope audit: 2376 changed paths, 1 violations | — |
| WO37 M-G CP9 | `923b5ba` | `443d3e4` | fresh-checkout verification of the M-B CP4 + prologue-fix delta (validator PASS 126/126, scope audit block 2 paths / 0 violations, cumulative 2380 / 1 known artifact) | PASS 126/126 |
| PR119 BODY RESTRUCTURE R1 | `50cc042` | `5dece1f` | compact PR body v2 (8.454 B / 7.594 ký tự) + delivery index này; validator PASS 9/9; mô tả v2 đã đăng 2026-11-13 ~05:50 JST, đọc lại byte-exact; scope audit block 5 paths / 0 violations, cumulative 2386 / 1 known artifact | PASS 9/9 |
| WO37 M-B CP5 | `257c985` | `8f7120a` | bản phụ đề v2 prologue CIN_000 theo narration History: SRT v2 26 chunk (text giống v1, chỉ dời thời gian), 640 sha f8d6ac32… / 11.927.191 B (−20,87 LUFS / −1,24 dBTP), 720p sha 472c1167… / 32.342.539 B, SRT sha b4495c25…; checker PASS 55/55, validate_media_deliveries PASS 0 mismatch; runtime không đổi; scope audit block 7 paths / 0 violations, cumulative 2392 / 1 known artifact | PASS 55/55 |
| WO37 M-G CP10 | `7bba119` | `286787b` | fresh-checkout verification của delta M-B CP5 (fresh clone tại 8f7120a, pull LFS thuần mạng, sha/size khớp tuyệt đối); validator độc lập PASS 40/40 + checker CP5 chạy lại 55/55 (JSON giống hệt bản commit), 0 defect; scope audit block 4 paths / 0 violations, cumulative 2395 / 1 known artifact | PASS 40/40 + 55/55 |
| PR119 BODY RESTRUCTURE R2 | `1934fad` | `08dd9d2` | compact body v2 + delivery index coverage to 286787b (rows R1 + M-B CP5 + M-G CP10); validator PASS 17/17; mô tả PR đã đăng lại từ bản này 2026-11-14 ~02:02 JST (head 08dd9d2 · 195 · 2401, mergeable true/clean); ACK gộp CP5 + M-G CP10 + R2 đã đăng trên issue #116 (`6862732081`, 2026-11-14 ~04:24 JST); scope audit block 5 paths / 0 violations, cumulative 2399 / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R3 | `5bb3975` | `82c8ef6` | delivery index đã gộp đủ dòng cho R2 (bao phủ tới `08dd9d2`); body v2 trong repo đã đồng bộ với bản live R2 + đoạn R2; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đang chờ owner tap (payload `pr119_update_body_v2_r3.json` tại `godot-prototype/pr_comments/`); scope audit block 5 paths / 0 violations, cumulative 2402 / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R4 | `cc0885e` | `56c2ceb` | delivery index đã gộp đủ dòng cho R3 (bao phủ tới `82c8ef6`); body v2 trong repo đã đồng bộ với bản live R2 + đoạn R3; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đang chờ owner tap (payload `pr119_update_body_v2_r4.json` tại `godot-prototype/pr_comments/`); scope audit block 3 paths / 0 violations, cumulative 2405 / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R5 | `a9730c0` | `b70fd56` | delivery index đã gộp đủ dòng cho R4 (bao phủ tới `56c2ceb`); body v2 trong repo đã đồng bộ với bản live R2 + đoạn R4; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 R5 đã chuẩn bị xong, chờ owner tap — bị bản v2 R6 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2408 / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R6 | `19b8c06` | `fd27b6f` | delivery index đã gộp đủ dòng cho R5 (bao phủ tới `b70fd56`); body v2 trong repo đã đồng bộ với bản live R2 + đoạn R5; checker PASS 17/17; mô tả PR đã đăng lại từ bản v2 này 2026-11-14 ~09:29 JST (head `fd27b6f` · 203 · 2413, mergeable true/clean); không cần ACK riêng cho R6; scope audit block 3 paths / 0 violations, cumulative 2411 / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R7 | `fa45858` | `22117a7` | delivery index đã gộp đủ dòng cho R6 (bao phủ tới `fd27b6f`); body v2 trong repo đã đồng bộ với bản live R2 + đoạn R6; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong, chờ owner tap — bị bản v2 R8 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2414 / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R8 | `4e4ebad` | `f2ba478` | delivery index đã gộp đủ dòng cho R7 (bao phủ tới `22117a7`); body v2 trong repo đã đồng bộ với bản live R6 + đoạn R7; checker PASS 17/17; mô tả PR đã đăng lại từ bản v2 này 2026-11-14 ~11:19 JST (head `f2ba478` · 207 · 2419, mergeable true/clean); không cần ACK riêng cho R8; scope audit block 3 paths / 0 violations, cumulative 2417 / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R9 | `a079b00` | `e13e3f5` | delivery index đã gộp đủ dòng cho R8 (bao phủ tới `f2ba478`); body v2 trong repo đã đồng bộ với bản live R8 + đoạn R8; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong, chờ owner tap — bị bản v2 R10 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2420 / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R10 | `5fe1314` | `22907b5` | delivery index đã gộp đủ dòng cho R9 (bao phủ tới `e13e3f5`); body v2 trong repo đã đồng bộ với bản live R8 + đoạn R9; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong, chờ owner tap — bị bản v2 R11 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2423 paths / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R11 | `e19616b` | `755c5da` | delivery index đã gộp đủ dòng cho R10 (bao phủ tới `22907b5`); body v2 trong repo đã đồng bộ với bản live R8 + đoạn R10; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong, chờ owner tap — bị bản v2 R12 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2426 paths / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R12 | `ae5d57b` | `db71acb` | delivery index đã gộp đủ dòng cho R11 (bao phủ tới `755c5da`); body v2 trong repo đã đồng bộ với bản live R8 + đoạn R11; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong, chờ owner tap — bị bản v2 R13 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2429 paths / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R13 | `91d6f0d` | `d12b8fb` | delivery index đã gộp đủ dòng cho R12 (bao phủ tới `db71acb`); body v2 trong repo đã đồng bộ với bản live R8 + đoạn R12; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong, chờ owner tap — bị bản v2 R14 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2432 paths / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R14 | `10b6a70` | `18a8e6f` | delivery index đã gộp đủ dòng cho R13 (bao phủ tới `d12b8fb`); body v2 trong repo đã đồng bộ với bản live R8 + đoạn R13; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong, chờ owner tap — bị bản v2 R15 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2435 paths / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R15 | `92daf95` | `406bc86` | delivery index đã gộp đủ dòng cho R14 (bao phủ tới `18a8e6f`); body v2 trong repo đã đồng bộ với bản live R8 + đoạn R14; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong, chờ owner tap — bị bản v2 R16 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2438 paths / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R16 | `57fa2db` | `43fd714` | delivery index đã gộp đủ dòng cho R15 (bao phủ tới `406bc86`); body v2 trong repo đã đồng bộ với bản live R8 + đoạn R15; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong (payload `pr119_update_body_v2_r16.json`), lượt đăng ~19:15 JST hết hạn thẻ duyệt nên chưa đăng (connector xác nhận không thực hiện) — bị bản v2 R17 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2441 paths / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R17 | `20d234d` | `246ac37` | delivery index đã gộp đủ dòng cho R16 (bao phủ tới `43fd714`); body v2 trong repo đã đồng bộ với bản live R8 + đoạn R16; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong (payload `pr119_update_body_v2_r17.json`), chờ owner tap — bị bản v2 R18 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2444 paths / 1 known artifact | PASS 17/17 |
| PR119 BODY RESTRUCTURE R18 | `d85b85a` | `fad0994` | delivery index đã gộp đủ dòng cho R17 (bao phủ tới `246ac37`); body v2 trong repo đã đồng bộ với bản live R8 + đoạn R17; checker PASS 17/17; bản cập nhật mô tả PR từ bản v2 này đã chuẩn bị xong (payload `pr119_update_body_v2_r18.json`), chờ owner tap — bị bản v2 R19 supersede trước khi đăng; scope audit block 3 paths / 0 violations, cumulative 2447 paths / 1 known artifact | PASS 17/17 |

## Ghi chú

- Cập nhật R2 (2026-11-13): index bao phủ tới head `286787b` (193 commit) — đã gộp 2 commit của R1, khối M-B CP5 và khối M-G CP10; 2 commit của chính R2 sẽ gộp vào index ở lần cập nhật tiếp theo (R3).
- Cập nhật R3 (2026-11-14): index bao phủ tới head `08dd9d2` (195 commit) — đã gộp 2 commit của R2; 2 commit của chính R3 sẽ gộp vào index ở lần cập nhật tiếp theo (R4).
- Cập nhật R4 (2026-11-14): index bao phủ tới head `82c8ef6` (197 commit) — đã gộp 2 commit của R3; 2 commit của chính R4 sẽ gộp vào index ở lần cập nhật tiếp theo (R5).
- Cập nhật R5 (2026-11-14): index bao phủ tới head `56c2ceb` (199 commit) — đã gộp 2 commit của R4; 2 commit của chính R5 sẽ gộp vào index ở lần cập nhật tiếp theo (R6).
- Cập nhật R6 (2026-11-14): index bao phủ tới head `b70fd56` (201 commit) — đã gộp 2 commit của R5; 2 commit của chính R6 sẽ gộp vào index ở lần cập nhật tiếp theo (R7).
- Cập nhật R7 (2026-11-14): index bao phủ tới head `fd27b6f` (203 commit) — đã gộp 2 commit của R6; 2 commit của chính R7 sẽ gộp vào index ở lần cập nhật tiếp theo (R8).
- Cập nhật R8 (2026-11-14): index bao phủ tới head `22117a7` (205 commit) — đã gộp 2 commit của R7; 2 commit của chính R8 sẽ gộp vào index ở lần cập nhật tiếp theo (R9).
- Cập nhật R9 (2026-11-14): index bao phủ tới head `f2ba478` (207 commit) — đã gộp 2 commit của R8; 2 commit của chính R9 sẽ gộp vào index ở lần cập nhật tiếp theo (R10).
- Cập nhật R10 (2026-11-14): index bao phủ tới head `e13e3f5` (209 commit) — đã gộp 2 commit của R9; 2 commit của chính R10 sẽ gộp vào index ở lần cập nhật tiếp theo (R11).
- Cập nhật R11 (2026-11-14): index bao phủ tới head `22907b5` (211 commit) — đã gộp 2 commit của R10; 2 commit của chính R11 sẽ gộp vào index ở lần cập nhật tiếp theo (R12).
- Cập nhật R12 (2026-11-14): index bao phủ tới head `755c5da` (213 commit) — đã gộp 2 commit của R11; 2 commit của chính R12 sẽ gộp vào index ở lần cập nhật tiếp theo (R13).
- Cập nhật R13 (2026-11-14): index bao phủ tới head `db71acb` (215 commit) — đã gộp 2 commit của R12; 2 commit của chính R13 sẽ gộp vào index ở lần cập nhật tiếp theo (R14).
- Cập nhật R14 (2026-11-14): index bao phủ tới head `d12b8fb` (217 commit) — đã gộp 2 commit của R13; 2 commit của chính R14 sẽ gộp vào index ở lần cập nhật tiếp theo (R15).
- Cập nhật R15 (2026-11-14): index bao phủ tới head `18a8e6f` (219 commit) — đã gộp 2 commit của R14; 2 commit của chính R15 sẽ gộp vào index ở lần cập nhật tiếp theo (R16).
- Cập nhật R16 (2026-11-14): index bao phủ tới head `406bc86` (221 commit) — đã gộp 2 commit của R15; 2 commit của chính R16 sẽ gộp vào index ở lần cập nhật tiếp theo (R17). Đính chính: dòng R14 trong bảng trên ghi cumulative 2438 là sai (số của R15) — cumulative đúng tại content commit R14 (`10b6a70`) là 2435, đã sửa ở lượt này.
- Cập nhật R17 (2026-11-14): index bao phủ tới head `43fd714` (223 commit) — đã gộp 2 commit của R16; 2 commit của chính R17 sẽ gộp vào index ở lần cập nhật tiếp theo (R18).
- Cập nhật R18 (2026-11-14): index bao phủ tới head `246ac37` (225 commit) — đã gộp 2 commit của R17; 2 commit của chính R18 sẽ gộp vào index ở lần cập nhật tiếp theo (R19).
- Cập nhật R19 (2026-11-14): index bao phủ tới head `fad0994` (227 commit) — đã gộp 2 commit của R18; 2 commit của chính R19 sẽ gộp vào index ở lần cập nhật tiếp theo (R20).
- Cách đếm commit/file: `git rev-list --count cf17178..HEAD` và `git diff --name-only cf17178 HEAD | wc -l` (cách đếm của mọi payload trước). Một commit báo cáo (vòng R) làm head tăng thêm 2 file so với con số 'cumulative' trong chính báo cáo đó (báo cáo md + validation JSON) — luôn dùng head count cho payload. (Đính chính R19: câu cũ ghi 4 file là sai với mẫu vòng R; đã kiểm chứng tại `fad0994`: commit báo cáo thêm đúng 2 file, cumulative 2447 → head 2449.)
- Trường `base.sha` mà API pull trả về (`f383233…`) là giá trị cũ (merge PR #118), không phải integration hiện tại; integration hiện tại xác minh bằng ls-remote.
- Trạng thái: mọi VO/mix DRAFT_NOT_FINAL, NOT_AUDITIONED; final picture 32 shot chờ character lock; 3 VO overrun để Codex quyết ở review; full OGV 720p deferred (Gói 39).

