# MEDIA-02 — WO37 M-D Checkpoint 4: Phase layers (boss phase 4, swamp intensity, dungeon intensity)

- Ngày: 2026-11-09 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `6f79853`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (module M-D) · Audio Direction (`docs/production/Audio_Production_Direction_v1_vi.md` §1)
- Trạng thái: **COMPOSED_CANDIDATE** — nhạc sáng tác gốc, DRAFT, chưa thẩm âm; adoption là quyết định của Codex (presentation adapter).

## 1. Phạm vi khối

Coverage matrix (`MUSIC_SCORE_MD_COVERAGE_v1.json`) liệt kê khối này là mục thứ hai của `openForMdCp4` (mục thứ nhất — ear audition toàn bộ cue MD1/MD2/MD3 — vẫn mở, vì không thể thẩm âm bằng tai trong lượt chạy tự động). Khối này đóng 3 phase layer cộng thêm:

- **`MUSIC/boss_mang_cot_layer_phase4`** — giai đoạn cuối trên cue boss checkpoint-26 (10 bar @ 66 bpm, Dm).
- **`MUSIC/swamp_layer_intensity`** — lớp tăng cường trên cue đầm MD1 (16 bar @ 58 bpm, Bm/Em, không trống theo thiết kế).
- **`MUSIC/dungeon_layer_intensity`** — lớp tăng cường trên cue hầm MD1 (12 bar @ 70 bpm, Dm, chỉ có trống mềm ở đầu bar theo thiết kế).

Không cue nào được sáng tác lại; không file ported nào bị đụng; không file MD1/MD2/MD3 nào bị đụng.

## 2. Thiết kế layer (mỗi layer chỉ thêm thứ base và các layer trước chưa có)

- **Boss phase 4:** phase 2 đã lấp beat 1/2/3 + bass 8th D1 + chuông F4 mỗi 2 bar; phase 3 đã lấp cả 4 beat + bass 16th D1 + chuông F4 mỗi bar. Phase 4 vì vậy đi double-time (trống cả beat lẫn offbeat), bass luân phiên quãng 8 D1/D2 (8th), chuông CAO D6 mỗi 2 bar, và nhân đôi fragment pluck minor-head của chính base lên một quãng 8 ở bar 2 và 7 (base tự nêu fragment ở bar 2/5/7/8; phase 2/3 đã phủ hết các bar còn lại nên không còn bar trống cho fragment mới — nhân đôi quãng 8 chính là cách tăng cường của giai đoạn cuối). Không pad, không flute.
- **Swamp intensity:** base không có trống, drone B0, một chuông trầm mỗi phrase, một figure pluck trầm duy nhất ở bar 6. Layer thêm trống mềm beat 0 và 2, bass pedal nốt đen theo đúng root progression của base, chuông E3 mỗi 4 bar (E là nốt treo của cue), và figure (D4, A4) của chính base ở bar 3 và 11 (bar mà base không có flute lẫn pluck). Không pad, không flute.
- **Dungeon intensity:** base chỉ có trống mềm ở đầu bar, drone D1 cả bar, fragment pluck ở bar 1/5/9 (+ biến thể bar 7). Layer lấp beat 1/2/3 quanh trống đầu bar, thêm bass pulse 8th D1, chuông lạnh F4 mỗi 2 bar ở các bar chẵn base để trống (0/2/6/10; chuông của base là D4 bar 4 và F4 bar 8), và fragment minor-head ở bar 3 và 10. Không pad, không flute.

## 3. Đo đạc (từ byte thật, ffmpeg loudnorm — phương pháp checkpoint 07/26)

Master WAV 48 kHz / 24-bit stereo; runtime OGG Vorbis q5.

| Layer | Dur (s) | Layer LUFS / TP | Cộng với base LUFS / TP | Seam wrapJump / raw |
|---|---|---|---|---|
| `MUSIC/boss_mang_cot_layer_phase4` | 36,3636 | −25,00 / −12,36 | −20,04 / −4,60 | 7e-06 / 0,142624 |
| `MUSIC/swamp_layer_intensity` | 66,2069 | −24,99 / −11,16 | −18,81 / −5,34 | 1e-05 / 0,227719 |
| `MUSIC/dungeon_layer_intensity` | 41,1429 | −25,00 / −8,68 | −20,32 / −5,88 | 1,7e-05 / 0,3068 |

Mỗi layer đúng target −25 LUFS (±0,5); cộng gộp với base đều dưới giới hạn −3,0 dBTP. Lưu ý cho adapter: cộng gộp của swamp là −18,81 LUFS — nóng nhất trong các layer đã giao (arena low −19,52, boss phase 3 −20,29, tragedy −20,21) vì base swamp vốn dày (pad + bass pattern + drone B0); adapter nên ride gain của layer khi fade vào thay vì cộng ở unity, giống ghi chú arena low ở checkpoint 3.

## 4. Delivery và validation

- Runtime audio manifest: 722 → **725 file** (composed 121 → 124; ported 541 file không đổi byte nào). Campaign 20 scene / 63 shot / 378 s / 21 dialogue cue không đổi; 21 embedded soundtrack không đổi.
- Validator độc lập `check_composed_score_md4_v1.py`: **PASS — 0 mismatches** (6 file hash lại + probe lại + đo lại loudnorm trong ±0,5 so với pack; 3 layer đo lại độ lớn cộng gộp trong ±0,5; coverage 15/15 + md4 3 layers + openForMdCp5).
- Validator MD1 chạy lại: **PASS, 0 mismatches** (20 file, 15 coverage slot). Validator MD2 chạy lại: **PASS, 0 mismatches** (74 file, 7 stem group). Validator MD3 chạy lại: **PASS, 0 mismatches** (96 file, 9 stem group) — sửa coverage ở checkpoint này không phá MD1/MD2/MD3 (`openForMdCp2`/`openForMdCp3`/`openForMdCp4` được giữ nguyên).
- Source re-validation `validate_media_deliveries.py`: **PASS, 0 mismatches** (có thêm checker `check_composed_score_md4_pack()`; tổng runtime cập nhật 722→725).
- Runtime re-verification `verify_runtime_delivery.py`: **PASS, 0 mismatches** (manifest total 725; counts music_ambience 22 / sfx_ui 519 / vo 30 / mix 30 / composed 124).
- Scope audit `check_agent_scope.py` (base integration 6f79853, branch media): content-only **14 path / 0 violations**; cumulative **1897 path / 1 violation `.gitattributes` đã biết** — artifact của merge-base cf17178 (file này byte-identical giữa integration 6f79853 và nhánh media; commit này không đụng tới nó).

## 5. Deliverable

- Builder: `Tools/MediaProduction/Muse/build_composed_score_md4.py` · Validator: `Tools/MediaProduction/Muse/check_composed_score_md4_v1.py`
- Pack: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD4_pack_v1.json` (3 cue) · Coverage: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json` (nhãn checkpoint 4 + khối md4 + `openForMdCp5`; `openForMdCp2`/`openForMdCp3`/`openForMdCp4` giữ nguyên để validator MD1/MD2/MD3 còn PASS)
- Master: `Art_Source/Audio/Muse/COMPOSED/layers/boss_mang_cot_layer_phase4.wav` (10,47 MB) + `layers/swamp_layer_intensity.wav` (19,07 MB) + `layers/dungeon_layer_intensity.wav` (11,85 MB) — tổng 41,39 MB (WAV, Git LFS)
- Runtime: `ClientGodot/assets/audio/composed/layers/*.ogg` (3), đã đăng ký trong `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json`
- Tool cập nhật: `Tools/MediaProduction/Muse/build_runtime_delivery.py` (§3n đăng ký MD4 + nhãn checkpoint + ghi chú MD4), `Tools/MediaProduction/Muse/validate_media_deliveries.py` (checker MD4 + cập nhật tổng 722→725 + checkpoint string + ghi chú MD4), `Tools/MediaProduction/Muse/verify_runtime_delivery.py` (chuỗi checkpoint/verifies + tổng 722→725)
- Báo cáo này + validation JSON: `Implementation/Reports/MuseMedia/MEDIA02_WO37_MD_CP4_SCORE_20261109.md` · `MEDIA02_WO37_MD_CP4_VALIDATION_20261109.json` · `MEDIA02_WO37_MD_CP4_SOURCE_REVALIDATION_20261109.json` · `MEDIA02_WO37_MD_CP4_RUNTIME_REVERIFY_20261109.json`

## 6. Ghi chú kỹ thuật

- Single-engine rule (từ checkpoint 2, vẫn giữ): builder chỉ load `build_composed_music.py` một lần làm engine duy nhất; không load bản copy thứ hai.
- Layer được loop-process giống hệt master (room, tail wrap 1,5 s, end landing 0,25 s) và gain-stage về target −25 LUFS bằng đúng dãy phép nhân tuần tự của gain_stage (MD3 helper), nên từng layer loop được độc lập.
- Không cue nào được render lại từ đầu: các layer là segment mới trên arrangement checkpoint-26 / MD1 đã ship; không cần khôi phục RNG history như stem ở MD2/MD3.

## 7. Giới hạn / khuyết điểm

- COMPOSED_CANDIDATE, NOT_AUDITIONED: chưa nghe bằng tai — chất lượng layer cộng gộp và loop seam đều chưa thẩm âm; loudness/true-peak đã đo từ byte thật.
- M-D chưa xong toàn bộ: ear audition của toàn bộ cue MD1/MD2/MD3/MD4 + loop seam, và thêm phase layer (hub/rain intensity, boss phase 5) vẫn mở cho checkpoint M-D 5 — đã liệt kê trong `openForMdCp5` của coverage matrix.
- Swamp cộng gộp −18,81 LUFS (nóng nhất trong các layer đã giao): adapter nên ride gain khi fade vào.
- Final picture / mix / autoplay không thuộc khối này; các file là candidate song song, Codex quyết định adoption.

## 8. Khối tiếp theo

WO37 M-D checkpoint 5 (ear-audition prep hoặc thêm phase layer: hub/rain intensity) hoặc M-E (SFX/ambience biến thể thật) hoặc M-F (VO palette/pickups/pronunciation review pack) — theo thứ tự Codex đã giao. PR #119 mô tả + ACK M-D CP4 cần luồng chính đăng (cần thẻ duyệt của chủ dự án).
