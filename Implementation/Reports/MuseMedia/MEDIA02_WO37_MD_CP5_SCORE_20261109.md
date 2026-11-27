# MEDIA-02 — WO37 M-D Checkpoint 5: Phase layers (boss phase 5, hub intensity, rain intensity)

- Ngày: 2026-11-09 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `6f79853`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (module M-D) · Audio Direction (`docs/production/Audio_Production_Direction_v1_vi.md` §1)
- Trạng thái: **COMPOSED_CANDIDATE** — nhạc sáng tác gốc, DRAFT, chưa thẩm âm; adoption là quyết định của Codex (presentation adapter).

## 1. Phạm vi khối

Coverage matrix (`MUSIC_SCORE_MD_COVERAGE_v1.json`) liệt kê khối này là mục thứ hai của `openForMdCp5` (mục thứ nhất — ear audition toàn bộ cue MD1/MD2/MD3/MD4 — vẫn mở, vì không thể thẩm âm bằng tai trong lượt chạy tự động). Khối này đóng 3 phase layer cộng thêm:

- **`MUSIC/boss_mang_cot_layer_phase5`** — giai đoạn cuối trên cue boss checkpoint-26 (10 bar @ 66 bpm, Dm).
- **`MUSIC/hub_layer_intensity`** — lớp tăng cường trên cue hub MD1 (16 bar @ 80 bpm, D major, không trống theo thiết kế).
- **`MUSIC/rain_layer_intensity`** — lớp tăng cường trên cue mưa MD1 (16 bar @ 66 bpm, D major, không trống theo thiết kế, low-pass 1200 Hz).

Không cue nào được sáng tác lại; không file ported nào bị đụng; không file MD1/MD2/MD3/MD4 nào bị đụng.

## 2. Thiết kế layer (mỗi layer chỉ thêm thứ base và các layer trước chưa có)

- **Boss phase 5:** nhịp tim base ở beat 0/1.5; phase 2 lấp beat 1/2/3; phase 3 lấp cả 4 beat; phase 4 lấp beat lẫn offbeat. Phase 5 vì vậy hoàn thiện lưới 16th bằng tick trống ở các subdivision "e"/"a", bass 16th luân phiên quãng 8 D1/D2 (phase 2/3 là bass 8th D1, phase 4 là bass 8th D1/D2), chuông CAO D6 mỗi bar (phase 4 mỗi 2 bar), và fragment minor-head bằng FLUTE ở bar 0 và 8 — chủ đề boss được nâng lên thanh vực cao. Flute là sự phá lệ có chủ đích với quy ước "không flute" của các layer trước: base boss hoàn toàn không có flute, và không layer nào trước đó dùng nó, nên đây là giọng mới chứ không phải trùng lặp. Bar 0 nhân đôi fragment pluck của phase 3 bằng giọng mới; bar 8 đáp lại chuông FS5 lạ (foreign bell) và fragment biến thể của chính base. Không pad.
- **Hub intensity:** base không có trống, bass chỉ ở beat 0/2, chuông ở mọi bar line, flute ở bar 0/8/14 với pluck trầm đáp ở bar 4 và tail ở bar 10–11. Layer thêm trống mềm beat 0 và 2, bass fill beat 1 và 3 theo đúng root của từng bar, shaker ở offbeat, và echo pluck trầm của motif head ở bar 2 và 12 (bar mà base không có giai điệu). Không chuông (base đã gõ mọi bar), không flute (flute của base giữ vai trò giọng chính).
- **Rain intensity:** base không có trống, bass chỉ ở beat 0, flute thưa (head bar 0, nửa sau bar 8), chuông ở bar 4/12, và màn low-pass 1200 Hz. Layer thêm trống mềm ở bar line, bass fill beat 2 theo root của bar, shaker ở offbeat (tiếng mưa dày hơn), echo pluck trầm của motif head ở bar 2 và 10, và chuông E5 ở bar 6 và 14 (E là nốt treo của cue). Layer được low-pass ở cùng 1200 Hz như base để nằm trong cùng một màn mưa. Không flute (flute của base giữ vai trò giọng chính).

## 3. Đo đạc (từ byte thật, ffmpeg loudnorm — phương pháp checkpoint 07/26)

Master WAV 48 kHz / 24-bit stereo; runtime OGG Vorbis q5.

| Layer | Dur (s) | Layer LUFS / TP | Cộng với base LUFS / TP | Seam wrapJump / raw |
|---|---|---|---|---|
| `MUSIC/boss_mang_cot_layer_phase5` | 36,3636 | −25,00 / −10,39 | −20,33 / −4,86 | 8e-06 / 0,231748 |
| `MUSIC/hub_layer_intensity` | 48,0000 | −24,99 / −9,96 | −20,56 / −8,62 | 5e-06 / 0,096677 |
| `MUSIC/rain_layer_intensity` | 58,1818 | −24,93 / −10,74 | −21,09 / −7,89 | 9e-06 / 0,133476 |

Mỗi layer đúng target −25 LUFS (±0,5); cộng gộp với base đều dưới giới hạn −3,0 dBTP. Lưu ý cho adapter: cộng gộp của boss phase 5 là −20,33 LUFS / −4,86 dBTP — nóng thứ hai trong các layer đã giao sau swamp (−18,81) — vì base boss vốn đã dày (heartbeat + drone D1 + fragment); adapter nên ride gain của layer khi fade vào thay vì cộng ở unity, giống ghi chú swamp ở checkpoint 4.

## 4. Delivery và validation

- Runtime audio manifest: 725 → **728 file** (composed 124 → 127; ported 541 file không đổi byte nào). Campaign 20 scene / 63 shot / 378 s / 21 dialogue cue không đổi; 21 embedded soundtrack không đổi.
- Validator độc lập `check_composed_score_md5_v1.py`: **PASS — 0 mismatches** (6 file hash lại + probe lại + đo lại loudnorm trong ±0,5 so với pack; 3 layer đo lại độ lớn cộng gộp trong ±0,5; coverage 15/15 + md5 3 layers + openForMdCp6).
- Validator MD1 chạy lại: **PASS, 0 mismatches** (20 file, 15 coverage slot). Validator MD2 chạy lại: **PASS, 0 mismatches** (74 file, 7 stem group). Validator MD3 chạy lại: **PASS, 0 mismatches** (96 file, 9 stem group). Validator MD4 chạy lại: **PASS, 0 mismatches** (6 file) — sửa coverage ở checkpoint này không phá MD1/MD2/MD3/MD4 (`openForMdCp2`/`openForMdCp3`/`openForMdCp4`/`openForMdCp5` được giữ nguyên).
- Source re-validation `validate_media_deliveries.py`: **PASS, 0 mismatches** (có thêm checker `check_composed_score_md5_pack()`; tổng runtime cập nhật 725→728).
- Runtime re-verification `verify_runtime_delivery.py`: **PASS, 0 mismatches** (manifest total 728; counts music_ambience 22 / sfx_ui 519 / vo 30 / mix 30 / composed 127).
- Scope audit `check_agent_scope.py` (base integration 6f79853, branch media): content-only **14 path / 0 violations**; cumulative **1910 path / 1 violation `.gitattributes` đã biết** — artifact của merge-base cf17178 (file này byte-identical giữa integration 6f79853 và nhánh media; commit này không đụng tới nó).

## 5. Deliverable

- Builder: `Tools/MediaProduction/Muse/build_composed_score_md5.py` · Validator: `Tools/MediaProduction/Muse/check_composed_score_md5_v1.py`
- Pack: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD5_pack_v1.json` (3 cue) · Coverage: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json` (nhãn checkpoint 5 + khối md5 + `openForMdCp6`; `openForMdCp2`/`openForMdCp3`/`openForMdCp4`/`openForMdCp5` giữ nguyên để validator MD1/MD2/MD3/MD4 còn PASS)
- Master: `Art_Source/Audio/Muse/COMPOSED/layers/boss_mang_cot_layer_phase5.wav` (9,99 MB) + `layers/hub_layer_intensity.wav` (13,18 MB) + `layers/rain_layer_intensity.wav` (15,98 MB) — tổng 39,15 MB (WAV, Git LFS)
- Runtime: `ClientGodot/assets/audio/composed/layers/*.ogg` (3), đã đăng ký trong `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json`
- Tool cập nhật: `Tools/MediaProduction/Muse/build_runtime_delivery.py` (§3o đăng ký MD5 + nhãn checkpoint + ghi chú MD5), `Tools/MediaProduction/Muse/validate_media_deliveries.py` (checker MD5 + cập nhật tổng 725→728 + checkpoint string + ghi chú MD5), `Tools/MediaProduction/Muse/verify_runtime_delivery.py` (chuỗi checkpoint/verifies + tổng 725→728)
- Báo cáo này + validation JSON: `Implementation/Reports/MuseMedia/MEDIA02_WO37_MD_CP5_SCORE_20261109.md` · `MEDIA02_WO37_MD_CP5_VALIDATION_20261109.json` · `MEDIA02_WO37_MD_CP5_SOURCE_REVALIDATION_20261109.json` · `MEDIA02_WO37_MD_CP5_RUNTIME_REVERIFY_20261109.json`

## 6. Ghi chú kỹ thuật

- Single-engine rule (từ checkpoint 2, vẫn giữ): builder chỉ load `build_composed_music.py` một lần làm engine duy nhất; không load bản copy thứ hai.
- Layer được loop-process giống hệt master (room, tail wrap 1,5 s, end landing 0,25 s) và gain-stage về target −25 LUFS bằng đúng dãy phép nhân tuần tự của gain_stage (MD3 helper), nên từng layer loop được độc lập. Rain layer low-pass 1200 Hz trước khi loop-process, giống hệt base.
- Không cue nào được render lại từ đầu: các layer là segment mới trên arrangement checkpoint-26 / MD1 đã ship; không cần khôi phục RNG history như stem ở MD2/MD3.
- Đính chính mô tả (đọc lại source MD3 trong lượt này): báo cáo checkpoint 4 mô tả bass của boss phase 3 là "16th-note D1" — thực tế code MD3 là 8th-note D1 (8 vị trí/bar, giống phase 2); bass 16th đầu tiên của chuỗi boss chính là phase 5 ở checkpoint này. Mô tả trong builder MD5 đã viết đúng (phase 2/3 là 8th-note D1).

## 7. Giới hạn / khuyết điểm

- COMPOSED_CANDIDATE, NOT_AUDITIONED: chưa nghe bằng tai — chất lượng layer cộng gộp và loop seam đều chưa thẩm âm; loudness/true-peak đã đo từ byte thật.
- M-D chưa xong toàn bộ: ear audition của toàn bộ cue MD1/MD2/MD3/MD4/MD5 + loop seam, và thêm phase layer (Ben Mua / Sa Hoa / Lam Trieu intensity) vẫn mở cho checkpoint M-D 6 — đã liệt kê trong `openForMdCp6` của coverage matrix.
- Boss phase 5 cộng gộp −20,33 LUFS / −4,86 dBTP (nóng thứ hai sau swamp): adapter nên ride gain khi fade vào.
- Final picture / mix / autoplay không thuộc khối này; các file là candidate song song, Codex quyết định adoption.

## 8. Khối tiếp theo

WO37 M-D checkpoint 6 (ear-audition prep hoặc thêm phase layer: Ben Mua / Sa Hoa / Lam Trieu intensity) hoặc M-E (SFX/ambience biến thể thật) hoặc M-F (VO palette/pickups/pronunciation review pack) — theo thứ tự Codex đã giao. PR #119 mô tả + ACK M-D CP5 cần luồng chính đăng (cần thẻ duyệt của chủ dự án).
