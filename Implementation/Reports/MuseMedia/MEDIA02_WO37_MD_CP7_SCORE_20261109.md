# MEDIA-02 — WO37 M-D Checkpoint 7: Phase layers (thang_long, tran_son, bach_uyen, rift_finale, quiet_discovery intensity)

- Ngày: 2026-11-09 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `6f79853`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (module M-D) · Audio Direction (`docs/production/Audio_Production_Direction_v1_vi.md` §1)
- Trạng thái: **COMPOSED_CANDIDATE** — nhạc sáng tác gốc, DRAFT, chưa thẩm âm; adoption là quyết định của Codex (presentation adapter).

## 1. Phạm vi khối

Coverage matrix (`MUSIC_SCORE_MD_COVERAGE_v1.json`) liệt kê khối này là mục thứ hai của `openForMdCp7` (mục thứ nhất — ear audition toàn bộ cue MD1/MD2/MD3/MD4/MD5/MD6 — vẫn mở, vì không thể thẩm âm bằng tai trong lượt chạy tự động). Khối này đóng 5 phase layer cộng thêm — **năm layer cuối cho các cue checkpoint-26**:

- **`MUSIC/thang_long_layer_intensity`** — nhịp phố mà bản phối đường phố giữ lại (checkpoint-26 cue, 16 bar @ 92 bpm, D major).
- **`MUSIC/tran_son_layer_intensity`** — nhịp cổng mà bản bell-led trang nghiêm giữ lại (checkpoint-26 cue, 15 bar @ 90 bpm, D major).
- **`MUSIC/bach_uyen_layer_intensity`** — dòng sâu mà thành phố dưới nước giữ lại (checkpoint-26 cue, 15 bar @ 62 bpm, B minor, low-pass 850 Hz như parent).
- **`MUSIC/rift_finale_layer_intensity`** — nhịp quyết mà bản finale năm dòng giữ lại (checkpoint-26 cue, 16 bar @ 100 bpm, D major).
- **`MUSIC/quiet_discovery_layer_intensity`** — chiều sâu mà khoảng lặng khám phá giữ lại (checkpoint-26 cue, 16 bar @ 60 bpm, D major).

Sau checkpoint này **mọi cue nhạc checkpoint-26 đều có intensity layer** (ben_mua, thang_long, quiet_discovery, lam_trieu, sa_hoa, tran_son, bach_uyen, rift_finale); cue nhạc duy nhất còn chưa có layer là Thanh Lac của MD1 (ghi trong `openForMdCp8`).

Không cue nào được sáng tác lại; không file ported nào bị đụng; không file MD1/MD2/MD3/MD4/MD5/MD6 nào bị đụng.

## 2. Thiết kế layer (mỗi layer chỉ thêm thứ base và các layer trước chưa có)

- **Thang Long intensity:** base là bản phối đường phố bận rộn — pad mọi bar, chuông tonic của hợp âm ở mọi bar line, bass ở CẢ BỐN beat, arpeggio pluck mọi bar, flute ở bar 0/8, đáp tail bằng low pluck ở bar 10, flute ở bar 14, và shaker ở mọi offbeat. Không trống. Layer thêm thứ duy nhất phố giữ lại — trống mềm ở bar line và beat 2 (nhịp hai phách của thành phố) — cộng echo pluck trầm của motif head ở bar 4 và 12 (bar mà base không có giai điệu; arpeggio là texture, không phải giai điệu). Không chuông (base đã rung mọi bar), không shaker (base đã giữ toàn bộ lưới offbeat), không bass fill (bass đã chơi cả bốn beat), không pad, không flute.
- **Tran Son intensity:** base là bản bell-led trang nghiêm — pad mọi bar, bass chỉ ở beat 0, chuông nêu motif ở bar 0/9, flute trầm đáp ở bar 5, trống đánh dấu mọi bar line, bar cuối để E5 treo mềm dưới chuông cổng. Không shaker, không pluck. Layer thêm nhịp cổng — trống mềm ở beat 2 (trống của base chỉ ở bar line, nên nhịp hai phách giờ mới đủ), bass fill beat 1 và 3 theo root, shaker ở offbeat, và echo pluck trầm của motif head ở bar 3 và 11 (bar mà base không có giai điệu). Không chuông (chuông là giọng chính).
- **Bach Uyen intensity:** base là theme dưới nước — pad mọi bar, bass ở beat 0/2, motif hạ một quãng tám trong flute ở bar 1/9, chuông chậm (D4 ở bar 5, A4 ở bar 12), giọt nước thưa, toàn bộ mix low-pass 850 Hz. Không trống, không shaker, không pluck. Layer thêm dòng sâu — trống mềm ở bar line, bass fill beat 1 và 3 theo root, shaker ở offbeat (bị cùng low-pass 850 Hz làm nghẹt, nên đọc như tiếng tích tắc mềm dưới nước), echo pluck trầm của motif head ở bar 6 và 13 (bar mà base không có giai điệu), và chuông D5 ở bar 14 (chuông tonic ở bar cuối; base không có chuông ở đó). Không flute (flute của base giữ vai trò giọng chính), không drops (base đã có), không pad. Toàn bộ layer được low-pass 850 Hz như parent, TRƯỚC gain stage, nên target −25 LUFS đo trên layer đã lọc.
- **Rift Finale intensity:** base truyền motif qua năm thanh vực — pad mọi bar, bass ở beat 0/2, pluck trầm ở bar 0, pluck giữa ở bar 3, flute ở bar 6, chuông ở bar 9, câu hỏi đầy đủ bằng flute + chuông ở bar 11, tail bị giữ lại trong flute ở bar 14, và cú khép D major duy nhất của cả bộ (chuông D6 + D5, một trống) ở bar 15. Không shaker. Layer thêm nhịp quyết — trống mềm ở bar line của các bar 0–14 (bar 15 đã có trống khép, nên để nguyên), bass fill beat 1 và 3 theo root, shaker ở offbeat, và echo pluck trầm của motif head ở bar 5 và 13 (bar mà base không có giai điệu). Không chuông (chuông ở 9/11/15 chính là cú khép), không flute (các dòng là giọng chính).
- **Quiet Discovery intensity:** base là khoảng lặng khám phá — hợp âm thưa (D bar 0–1, G bar 10–11, D bar 14–15), mảnh flute solo ở bar 0/8, chuông đơn ở bar 4/6/12, pluck trầm ở bar 13, giọt nước và tiếng nước xa. Không bass, không trống, không shaker, không pad. Layer thêm chiều sâu mà khoảng lặng giữ lại — bass nhẹ ở beat 0 và 2 (bass ĐẦU TIÊN cue này có; D bar 0–9, G bar 10–13, D bar 14–15), shaker ở offbeat CHỈ ở nửa sau (bar 8–15; khám phá sâu dần), và echo pluck trầm của motif head ở bar 2 và 10 (bar mà base không có giai điệu). KHÔNG trống, có chủ ý: trống ở bar line sẽ phá bản sắc của cue — nhịp ở đây là bass và shaker muộn, không phải trống. Không chuông (chuông của base là giọng chính), không pad (hợp âm giữ thưa theo thiết kế).

## 3. Đo đạc (từ byte thật, ffmpeg loudnorm — phương pháp checkpoint 07/26)

Master WAV 48 kHz / 24-bit stereo; runtime OGG Vorbis q5.

| Layer | Dur (s) | Layer LUFS / TP | Cộng với base LUFS / TP | Seam wrapJump / raw |
|---|---|---|---|---|
| `MUSIC/thang_long_layer_intensity` | 41,7391 | −25,00 / −15,20 | −21,65 / −10,55 | 0,0 / 0,002137 |
| `MUSIC/tran_son_layer_intensity` | 40,0000 | −25,01 / −9,73 | −20,51 / −8,07 | 6e-06 / 0,125192 |
| `MUSIC/bach_uyen_layer_intensity` | 58,0645 | −25,00 / −10,95 | −20,59 / −9,54 | 1e-06 / 0,017025 |
| `MUSIC/rift_finale_layer_intensity` | 38,4000 | −25,00 / −8,97 | −20,31 / −7,91 | 0,0 / 0,005044 |
| `MUSIC/quiet_discovery_layer_intensity` | 64,0000 | −25,00 / −9,66 | −22,48 / −9,28 | 7e-06 / 0,131574 |

Mỗi layer đúng target −25 LUFS (±0,5); cộng gộp với base đều dưới giới hạn −3,0 dBTP. Lưu ý cho adapter: cộng gộp của rift_finale là −20,31 LUFS / −7,91 dBTP — **nóng thứ hai trong tất cả các layer đã giao** (sau sa_hoa ở checkpoint 6, −20,03 LUFS / −6,87 dBTP) — vì base finale vốn đã dày ở dải giữa (năm dòng chồng nhau + cú khép chuông đôi); adapter nên ride gain của layer khi fade vào, giống ghi chú sa_hoa ở checkpoint 6. Thang_long layer có true peak rất thấp (−15,20 dBTP) vì layer này gần như chỉ là trống mềm + hai echo pluck — trống ngắn nên peak thấp dù loudness đã về −25 LUFS. Hai wrapJumpRaw lớn (tran_son 0,125192, quiet_discovery 0,131574) là bước nhảy TRƯỚC khi blend end-landing 0,25 s; wrapJump sau blend đều ≈ 0 (6e-06 / 7e-06), cùng cách ghi như các checkpoint trước — không phải seam PASS.

## 4. Delivery và validation

- Runtime audio manifest: 731 → **736 file** (composed 130 → 135; ported 541 file không đổi byte nào). Campaign 20 scene / 63 shot / 378 s / 21 dialogue cue không đổi; 21 embedded soundtrack không đổi.
- Validator độc lập `check_composed_score_md7_v1.py`: **PASS — 0 mismatches** (10 file hash lại + probe lại + đo lại loudnorm trong ±0,5 so với pack; 5 layer đo lại độ lớn cộng gộp trong ±0,5; coverage 15/15 + md7 5 layers + openForMdCp8).
- Validator MD1 chạy lại: **PASS, 0 mismatches** (20 file, 15 coverage slot). Validator MD2 chạy lại: **PASS, 0 mismatches** (74 file, 7 stem group). Validator MD3 chạy lại: **PASS, 0 mismatches** (96 file, 9 stem group). Validator MD4 chạy lại: **PASS, 0 mismatches** (6 file). Validator MD5 chạy lại: **PASS, 0 mismatches** (6 file). Validator MD6 chạy lại: **PASS, 0 mismatches** (6 file) — sửa coverage ở checkpoint này không phá MD1/MD2/MD3/MD4/MD5/MD6 (`openForMdCp2`/`openForMdCp3`/`openForMdCp4`/`openForMdCp5`/`openForMdCp6`/`openForMdCp7` được giữ nguyên).
- Source re-validation `validate_media_deliveries.py`: **PASS, 0 mismatches** (có thêm checker `check_composed_score_md7_pack()`; tổng runtime cập nhật 731→736; 1369 audio file đã kiểm).
- Runtime re-verification `verify_runtime_delivery.py`: **PASS, 0 mismatches** (manifest total 736; counts music_ambience 22 / sfx_ui 519 / vo 30 / mix 30 / composed 135).
- Scope audit `check_agent_scope.py` (base integration 6f79853, branch media): content-only **18 path / 0 violations**; cumulative **1940 path / 1 violation `.gitattributes` đã biết** — artifact của merge-base cf17178 (file này byte-identical giữa integration 6f79853 và nhánh media — cùng blob `7fea2800`; commit này không đụng tới nó).

## 5. Deliverable

- Builder: `Tools/MediaProduction/Muse/build_composed_score_md7.py` · Validator: `Tools/MediaProduction/Muse/check_composed_score_md7_v1.py`
- Pack: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD7_pack_v1.json` (5 cue) · Coverage: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json` (nhãn checkpoint 7 + khối md7 + `openForMdCp8`; `openForMdCp2`…`openForMdCp7` giữ nguyên để validator MD1/MD2/MD3/MD4/MD5/MD6 còn PASS)
- Master: `Art_Source/Audio/Muse/COMPOSED/layers/thang_long_layer_intensity.wav` (12,02 MB) + `layers/tran_son_layer_intensity.wav` (11,52 MB) + `layers/bach_uyen_layer_intensity.wav` (16,72 MB) + `layers/rift_finale_layer_intensity.wav` (11,06 MB) + `layers/quiet_discovery_layer_intensity.wav` (18,43 MB) — tổng 69,76 MB (WAV, Git LFS)
- Runtime: `ClientGodot/assets/audio/composed/layers/*.ogg` (5), đã đăng ký trong `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json`
- Tool cập nhật: `Tools/MediaProduction/Muse/build_runtime_delivery.py` (§3q đăng ký MD7 + nhãn checkpoint + ghi chú MD7), `Tools/MediaProduction/Muse/validate_media_deliveries.py` (checker MD7 + cập nhật tổng 731→736 + checkpoint string + ghi chú MD7), `Tools/MediaProduction/Muse/verify_runtime_delivery.py` (chuỗi checkpoint + tổng 731→736 + nhãn checkpoint 7)
- Báo cáo này + validation JSON: `Implementation/Reports/MuseMedia/MEDIA02_WO37_MD_CP7_SCORE_20261109.md` · `MEDIA02_WO37_MD_CP7_VALIDATION_20261109.json` · `MEDIA02_WO37_MD_CP7_SOURCE_REVALIDATION_20261109.json` · `MEDIA02_WO37_MD_CP7_RUNTIME_REVERIFY_20261109.json`

## 6. Ghi chú kỹ thuật

- Single-engine rule (từ checkpoint 2, vẫn giữ): builder chỉ load `build_composed_music.py` một lần làm engine duy nhất; không load bản copy thứ hai.
- Layer được loop-process giống hệt master (room, tail wrap 1,5 s, end landing 0,25 s) và gain-stage về target −25 LUFS bằng đúng dãy phép nhân tuần tự của gain_stage (MD3 helper), nên từng layer loop được độc lập. Chỉ bach_uyen cần low-pass riêng (850 Hz như parent, áp TRƯỚC gain stage).
- Không cue nào được render lại từ đầu: các layer là segment mới trên arrangement checkpoint-26 đã ship; không cần khôi phục RNG history như stem ở MD2/MD3.
- Đọc lại source CP26 trong lượt này để viết đúng thiết kế: thang_long bass đã chơi cả bốn beat (pattern (0,1,2,3)) nên layer không fill bass; tran_son trống chỉ ở bar line nên layer thêm beat 2; bach_uyen low-pass 850 Hz ghi trong PIECES; rift_finale đã có trống ở bar 15 nên layer chừa bar 15; quiet_discovery hoàn toàn không có bass nên layer mang bass đầu tiên của cue.
- Nhãn checkpoint trong `verify_runtime_delivery.py` đã sửa từ checkpoint 5 (còn sót từ MD5 — MD6 chỉ sửa chuỗi `verifies`) lên checkpoint 7 cho đúng checkpoint hiện hành.

## 7. Giới hạn / khuyết điểm

- COMPOSED_CANDIDATE, NOT_AUDITIONED: chưa nghe bằng tai — chất lượng layer cộng gộp và loop seam đều chưa thẩm âm; loudness/true-peak đã đo từ byte thật.
- M-D chưa xong toàn bộ: ear audition của toàn bộ cue MD1/MD2/MD3/MD4/MD5/MD6/MD7 + loop seam, và thêm phase layer (Thanh Lac intensity — cue duy nhất còn thiếu) vẫn mở cho checkpoint M-D 8 — đã liệt kê trong `openForMdCp8` của coverage matrix.
- Rift finale cộng gộp −20,31 LUFS / −7,91 dBTP (nóng thứ hai trong các layer đã giao): adapter nên ride gain khi fade vào.
- Quiet discovery KHÔNG có trống, có chủ ý — nếu adapter cần pulse mạnh hơn cho cảnh khám phá căng thẳng, đó là quyết định presentation, không phải thiếu sót của layer.
- Final picture / mix / autoplay không thuộc khối này; các file là candidate song song, Codex quyết định adoption.

## 8. Khối tiếp theo

WO37 M-D checkpoint 8 (Thanh Lac intensity layer — cue cuối cùng chưa có layer — hoặc ear-audition prep) hoặc M-E (SFX/ambience biến thể thật) hoặc M-F (VO palette/pickups/pronunciation review pack) — theo thứ tự Codex đã giao. PR #119 mô tả + ACK M-D CP7 cần luồng chính đăng (cần thẻ duyệt của chủ dự án); payload MD6 (PR mô tả + ACK) vẫn chưa đăng — payload MD7 gộp chung sẽ thay thế.
