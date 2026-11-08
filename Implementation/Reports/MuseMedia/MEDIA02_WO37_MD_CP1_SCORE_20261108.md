# MEDIA-02 — WO37 M-D Checkpoint 1: Whole-game score, batch 1 (7 missing core cues + 3 transitions)

- Ngày: 2026-11-08 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `6f79853`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (module M-D) · Audio Direction (`docs/production/Audio_Production_Direction_v1_vi.md` §1)
- Trạng thái: **COMPOSED_CANDIDATE** — nhạc sáng tác gốc, DRAFT, chưa thẩm âm; adoption là quyết định của Codex (presentation adapter).

## 1. Phạm vi khối

WO37 M-D yêu cầu score cho hub / explore / Bến Mưa / Thanh Lạc / Thăng Long / mưa / đầm / rừng / núi / sa mạc / dungeon / boss / arena / tragedy / resolution theo Audio Direction — giữ hệ leitmotif nhưng arrangement / instrumentation / density / rhythm / space phải có chức năng theo cảnh, "không chỉ đổi pitch / tempo một loop để đủ số cue".

Checkpoint 26 đã sáng tác 9 cue nhạc phủ 8/15 slot (ben_mua, thang_long, boss_mang_cot, quiet_discovery, lam_trieu, sa_hoa, tran_son, rift_finale) cộng bach_uyen (thành dưới nước, ngoài danh sách 15 slot M-D). **7 slot không hề có cue nhạc** — hub, Thanh Lạc, mưa, đầm, dungeon, arena, tragedy — và score chưa có transition giữa các trạng thái.

Checkpoint này đóng cả 7 khoảng trống + giao 3 cầu nối chuyển trạng thái. Sau khối này, **15/15 slot M-D có cue nhạc sáng tác, 0 gap**.

## 2. Sáng tác

Cùng hệ leitmotif checkpoint 26 (câu nhạc D major pentatonic bỏ lửng, dừng ở bậc 2 — nốt E; đuôi đầy đủ chỉ dành cho stinger `resolve` và `rift_finale`). Mỗi cue mới là một biến tấu có chức năng riêng, không phải đổi pitch/tempo của một loop:

| Cue | Slot | Thiết kế |
|---|---|---|
| `MUSIC/hub_lac_chau` — Lạc Châu · Nơi trở về | hub | Ấm, chậm (80 bpm): pad D/G/Bm, chuông mỗi nhịp, sáo nêu câu hỏi 2 lần; pluck trầm trả lời bằng tail ở bar 10–11 (tiền lệ thang_long — đáp án khẽ mà một "nhà" được phép đưa); kết bằng chuông D nhẹ trên pad tonic. |
| `MUSIC/thanh_lac` — Thanh Lạc · Chợ sáng | Thanh Lạc | Dạng phố bận nhất (96 bpm): arpeggio pluck mỗi bar + giọng pluck thứ hai off-beat thấp một quãng tám, chuông, shaker; sáo ở bar 0 và 8, tail pluck trầm bar 12. |
| `MUSIC/rain_veil` — Mưa · Màn nước mỏng | rain | Sáo thưa (head bar 0, nửa sau bar 8), pad dài, giọt mưa dày; toàn mix low-pass 1200 Hz để ambience mưa ngồi lên trên không tranh chấp. Kết vẫn treo ở E. |
| `MUSIC/swamp` — Đầm · Nước đứng | swamp | Motif thấp một quãng tám, mật độ một nửa, trên pad Bm/Em + drone B0; giọt chậm sâu, một chuông trầm mỗi cụm; không trống. Kết ở E trầm. |
| `MUSIC/dungeon` — Hầm · Đá lạnh | dungeon | D minor: mảnh motif pluck trầm, trống nhẹ mỗi bar, drone D1, chuông lạnh đánh dấu; motif không bao giờ hoàn tất — E là nốt cao duy nhất, một lần, ở bar cuối. |
| `MUSIC/arena` — Đấu trường · Hồi trống | arena | Trống dẫn (120 bpm): trống mỗi beat + offbeat, ostinato pluck nốt móc đơn, motif pluck sáng bar 0 và 8, chuông mỗi bar. Cue duy nhất "đáp đất": trống + chuông D khép loop. |
| `MUSIC/tragedy` — Bi kịch · Dây đứt | tragedy | D minor chậm (56 bpm): sáo solo từng mảnh, khoảng lặng dài giữa các mảnh, chuông đơn, một hình pluck trầm; không trống, không tail — nốt cuối là E treo một mình trên pad Dm. |

Transitions (one-shot 6,0 s, target −25 LUFS, không loop, không replay intro của cue đích — theo luật Audio Direction cho encounter chưa reset):

| Cue | Dùng khi |
|---|---|
| `MUSIC/transition_calm_danger` — Chuyển · Yên sang hiểm | Bắt đầu encounter: đầu sáo → mảnh pluck dồn dập → nhịp trống trầm vào ở 4 s, kết ở E treo trên pad minor. |
| `MUSIC/transition_danger_calm` — Chuyển · Hiểm về yên | Kết thúc encounter / về vùng an toàn: nhịp tim tắt dần trước 2,5 s, pad minor nâng lên D major, đầu sáo trở lại khẽ; kết pad D + chuông. |
| `MUSIC/transition_area` — Chuyển · Qua miền khác | Đổi map/biome: arpeggio pluck vượt nước dâng D5→D6 trên nền wash, pad G ở 3 s, chuông D ở 4,5 s. Đầy hơn stinger transition 3 s của checkpoint 26 (stinger đó vẫn chỉ dùng cho trình diễn cinematic). |

Render bằng procedural synthesis (engine checkpoint 26 tái dùng từ `build_composed_music.py`: pluck/flute/bell/pad/bass + noise percussion, hai feedback-comb "river hall"). Không sample ngoài, không byte ported, không giọng nói.

## 3. Đo đạc (từ byte thật, ffmpeg loudnorm — phương pháp checkpoint 07/26)

Master WAV 48 kHz / 24-bit stereo; runtime OGG Vorbis q5. Nhạc target −22 LUFS / TP ≤ −7 dBTP; transition target −25 LUFS / TP ≤ −6 dBTP.

| Cue | Dur (s) | Master LUFS / TP | Runtime LUFS / TP | wrapJumpRaw |
|---|---|---|---|---|
| MUSIC/hub_lac_chau | 48.00 | −22.01 / −10.37 | −21.95 / −10.29 | 0.116 |
| MUSIC/thanh_lac | 40.00 | −22.00 / −10.47 | −21.96 / −10.45 | 0.377 |
| MUSIC/rain_veil | 58.18 | −22.00 / −7.63 | −21.94 / −7.56 | 0.040 |
| MUSIC/swamp | 66.21 | −22.00 / −7.96 | −21.97 / −7.96 | 0.120 |
| MUSIC/dungeon | 41.14 | −22.00 / −9.14 | −21.98 / −9.02 | 0.173 |
| MUSIC/arena | 32.00 | −22.00 / −7.37 | −21.97 / −7.38 | 0.056 |
| MUSIC/tragedy | 51.43 | −22.00 / −7.93 | −21.95 / −7.87 | 0.003 |
| MUSIC/transition_calm_danger | 6.00 | −25.00 / −17.37 | −24.94 / −17.49 | — |
| MUSIC/transition_danger_calm | 6.00 | −25.00 / −17.39 | −24.93 / −17.20 | — |
| MUSIC/transition_area | 6.00 | −25.00 / −16.22 | −24.94 / −16.35 | — |

Loop construction, nói rõ như checkpoint 26: 1,5 s ring-out cuối được wrap lên đầu bằng crossfade equal-power, 0,25 s cuối blend về sample đầu; `wrapJump` sau xử lý ≈ 0, `wrapJumpRaw` là bước nhảy trước xử lý — lớn nhất ở thanh_lac (0,377, bar cuối còn chuông + arpeggio) và dungeon (0,173). Cả hai số đều ghi trong manifest từng cue; seam nghe bằng tai vẫn chưa kiểm (NOT_AUDITIONED).

Kiểm độc lập bằng `volumedetect` trên 3 file mẫu: tragedy mean −24,6 dB / max −7,9 dB; arena mean −23,4 dB / max −7,4 dB; transition_area mean −27,9 dB / max −16,2 dB — file có tín hiệu thật, không rỗng, không phải tone-generator.

## 4. Coverage M-D sau khối này

`MUSIC_SCORE_MD_COVERAGE_v1.json`: **15/15 slot COVERED_COMPOSED, 0 gap**.

| Slot | Cue sáng tác | Pack |
|---|---|---|
| hub | MUSIC/hub_lac_chau | MD1 (mới) |
| explore | MUSIC/quiet_discovery | CP26 |
| ben_mua | MUSIC/ben_mua | CP26 |
| thanh_lac | MUSIC/thanh_lac | MD1 (mới) |
| thang_long | MUSIC/thang_long | CP26 |
| rain | MUSIC/rain_veil | MD1 (mới) |
| swamp | MUSIC/swamp | MD1 (mới) |
| forest | MUSIC/lam_trieu | CP26 |
| mountain | MUSIC/tran_son | CP26 |
| desert | MUSIC/sa_hoa | CP26 |
| dungeon | MUSIC/dungeon | MD1 (mới) |
| boss | MUSIC/boss_mang_cot | CP26 |
| arena | MUSIC/arena | MD1 (mới) |
| tragedy | MUSIC/tragedy | MD1 (mới) |
| resolution | MUSIC/rift_finale | CP26 |

Trước MD1, rain chỉ có ambience (rain_light / rain_heavy), swamp/dungeon chỉ có ambience kề (river_shore / cave_drips), còn hub / Thanh Lạc / arena / tragedy không có gì cả — kể cả trong pack ported. `MUSIC/bach_uyen` (CP26) vẫn là cue ngoài 15 slot (thành dưới nước), được giữ nguyên và không tính vào coverage.

## 5. Delivery và validation

- Runtime audio manifest: 627 → **637 file** (composed 26 → 36; ported 541 file không đổi byte nào). Campaign 20 scene / 63 shot / 378 s / 21 dialogue cue không đổi; 21 embedded soundtrack không đổi.
- Validator độc lập `check_composed_score_md1_v1.py`: **PASS — 0 mismatches** (20 file hash lại + probe lại + đo lại loudnorm trong ±0,5 so với pack; 15 slot coverage kiểm lại; không trùng cueKey/stem với pack CP26/ambience).
- Source re-validation `validate_media_deliveries.py`: **PASS, 0 mismatches** (1171 file audio kiểm; MD1 cues 10; có thêm checker `check_composed_score_md1_pack()` trong tool). Một mismatch đã gặp và sửa đúng nguồn trong lượt này: checker prologue còn hard-code tổng runtime 627 (từ checkpoint 54) — đã cập nhật thành 637 trong tool, chạy lại PASS.
- Runtime re-verification `verify_runtime_delivery.py`: **PASS, 0 mismatches** (manifest total 637; counts music_ambience 22 / sfx_ui 519 / vo 30 / mix 30 / composed 36).
- Masters tổng 97,5 MB (WAV, Git LFS); runtime OGGs 2,86 MB.
- Nhãn "checkpoint" của runtime manifest đã bắt kịp: trước đây còn dừng ở checkpoint 52 trong khi file đã ở 627 (checkpoint 53/54 không cập nhật nhãn); nhãn nay ghi MD1 + CIN_019/CIN_020. Tổng file là số đếm từ danh sách thật, không phải từ nhãn.

## 6. Deliverable

- Builder: `Tools/MediaProduction/Muse/build_composed_score_md1.py` · Validator: `Tools/MediaProduction/Muse/check_composed_score_md1_v1.py`
- Pack: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD1_pack_v1.json` (10 cue) · Coverage: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json` (15 slot)
- Master: `Art_Source/Audio/Muse/COMPOSED/music/<stem>.wav` (7) + `Art_Source/Audio/Muse/COMPOSED/transitions/<stem>.wav` (3)
- Runtime: `ClientGodot/assets/audio/composed/music/<stem>.ogg` (7) + `ClientGodot/assets/audio/composed/transitions/<stem>.ogg` (3), đã đăng ký trong `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json`
- Tool cập nhật: `Tools/MediaProduction/Muse/build_runtime_delivery.py` (§3k đăng ký MD1 + nhãn checkpoint + ghi chú MD1), `Tools/MediaProduction/Muse/validate_media_deliveries.py` (checker MD1 + cập nhật tổng 627→637 + limit MD1), `Tools/MediaProduction/Muse/verify_runtime_delivery.py` (chuỗi checkpoint/verifies + base 6f2b465→6f79853)
- Báo cáo này + validation JSON: `Implementation/Reports/MuseMedia/MEDIA02_WO37_MD_CP1_SCORE_20261108.md` · `MEDIA02_WO37_MD_CP1_VALIDATION_20261108.json` · `MEDIA02_WO37_MD_CP1_SOURCE_REVALIDATION_20261108.json` · `MEDIA02_WO37_MD_CP1_RUNTIME_REVERIFY_20261108.json`

## 7. Ghi chú kỹ thuật

- Engine checkpoint 26 được import lại (không copy 900 dòng): `build_composed_score_md1.py` import synth primitives từ `build_composed_music.py` qua importlib; mọi cue mới chỉ là dữ liệu sáng tác (melody/harmony/arrangement) trong tool MD1.
- Quy tắc tail: đuôi đầy đủ (flute tail F#–E–D) vẫn chỉ dành cho stinger `resolve` và `rift_finale`. Tail pluck trầm là đáp án khẽ mà cue "nhà/phố" được phép đưa — tiền lệ đã có ở `thang_long` (checkpoint 26, bar 10–11); `hub_lac_chau` và `thanh_lac` theo đúng tiền lệ đó.
- Pack manifest lưu sau mỗi cue (bài học checkpoint 26: lần render này chạy một mạch hết trong ~77 s, nhưng nếu bị ngắt giữa chừng thì manifest từng phần vẫn hợp lệ).
- Không cue nào trong pack ported bị đụng: 7 cueKey nhạc + 3 cueKey transition đều mới; stem file đều mới.

## 8. Giới hạn / khuyết điểm

- COMPOSED_CANDIDATE, NOT_AUDITIONED: chưa nghe bằng tai — chất lượng giai điệu, loop seam và cân bằng mix đều chưa thẩm âm; loudness/true-peak đã đo từ byte thật.
- M-D chưa xong toàn bộ: intro/outro từng cue, stems (lead / pad-bass / percussion), và phase-layer candidates (vd. arena 2 mức cường độ, boss theo phase) vẫn mở cho checkpoint M-D 2 — đã liệt kê trong `openForMdCp2` của coverage matrix.
- `wrapJumpRaw` lớn ở thanh_lac (0,377) và dungeon (0,173): bar cuối còn nội dung chuông/trống gần điểm nối loop; wrapJump sau xử lý ≈ 0 nhưng seam nghe bằng tai vẫn là việc của vòng thẩm âm.
- Final picture / mix / autoplay không thuộc khối này; các cue là candidate song song, Codex quyết định adoption.

## 9. Khối tiếp theo

WO37 M-D checkpoint 2 (intro/outro + stems + phase-layer candidates cho các cue MD1/CP26) hoặc M-E (SFX/ambience biến thể thật) — theo thứ tự Codex đã giao. PR #119 mô tả + ACK MD CP1 cần luồng chính đăng (cần thẻ duyệt của chủ dự án).
