# MEDIA-02 — WO37 M-D Checkpoint 6: Phase layers (ben_mua, lam_trieu, sa_hoa intensity)

- Ngày: 2026-11-09 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `6f79853`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (module M-D) · Audio Direction (`docs/production/Audio_Production_Direction_v1_vi.md` §1)
- Trạng thái: **COMPOSED_CANDIDATE** — nhạc sáng tác gốc, DRAFT, chưa thẩm âm; adoption là quyết định của Codex (presentation adapter).

## 1. Phạm vi khối

Coverage matrix (`MUSIC_SCORE_MD_COVERAGE_v1.json`) liệt kê khối này là mục thứ hai của `openForMdCp6` (mục thứ nhất — ear audition toàn bộ cue MD1/MD2/MD3/MD4/MD5 — vẫn mở, vì không thể thẩm âm bằng tai trong lượt chạy tự động). Khối này đóng 3 phase layer cộng thêm:

- **`MUSIC/ben_mua_layer_intensity`** — nhịp bến mưa trên cue Bến Mưa checkpoint-26 (17 bar @ 72 bpm, D major).
- **`MUSIC/lam_trieu_layer_intensity`** — nhịp rừng trên cue Lâm Triều checkpoint-26 (20 bar @ 90 bpm, G major pentatonic).
- **`MUSIC/sa_hoa_layer_intensity`** — sức nặng lò cát trên cue Sa Hỏa checkpoint-26 (20 bar @ 110 bpm, A minor pentatonic).

Không cue nào được sáng tác lại; không file ported nào bị đụng; không file MD1/MD2/MD3/MD4/MD5 nào bị đụng.

## 2. Thiết kế layer (mỗi layer chỉ thêm thứ base và các layer trước chưa có)

- **Ben Mua intensity:** base là chính câu nhạc chủ đề — pad mọi bar, bass chỉ ở beat 0/2, flute nêu câu hỏi ở bar 0/4/10, pluck đáp ở bar 2/6/12, fragment flute ở bar 14, và bar cuối để nốt E5 treo trên pad tonic với đúng một chuông D5; giọt nước rơi thưa. Không trống, không shaker, không chuông trước bar cuối. Layer thêm nhịp bến mưa mà theme giữ lại — trống mềm ở bar line, bass fill beat 1 và 3 theo đúng root của từng bar, shaker ở offbeat (tiếng mưa trên bến), echo pluck trầm của motif head ở bar 8 và 15 (bar mà base không có giai điệu), và chuông E5 ở bar 5 và 11 (E là nốt treo của cue). Không flute (flute của base giữ vai trò giọng chính), không drops (base đã có), không pad.
- **Lam Trieu intensity:** base chuyển motif sang G major pentatonic — pad mọi bar, bass chỉ ở beat 0/2, flute ở bar 0/14, echo pluck trầm ở bar 4, flute trang trí ở bar 8, và shaker lá chỉ ở các bar CHẴN (beat 1.5/3.5), giọt nước thưa. Không trống, không chuông. Layer thêm nhịp rừng — trống mềm ở bar line, bass fill beat 1 và 3 theo root, shaker ở các bar LẺ tại 1.5/3.5 (hoàn thiện lưới leaf-tick mà base để trống một nửa), echo pluck trầm của motif head chuyển sang G ở bar 6 và 12 (bar mà base không có giai điệu), và chuông G5 ở bar 10 và 18 (chuông tonic; base hoàn toàn không có chuông). Không flute (flute của base giữ vai trò giọng chính).
- **Sa Hoa intensity:** base chuyển motif sang A minor pentatonic — pad chỉ ở bar chẵn, bass ở beat 0/1.5/3, pluck khô sáng ở bar 0/6 (lệch +0.5 beat)/12, trống mềm ở beat 2 mỗi bar và shaker ở beat 3.5 mỗi bar. Không chuông, không flute. Layer thêm sức nặng lò cát mà cue khô giữ lại — trống mềm ở bar line (trống của base chỉ ở beat 2, nên nhịp hai phách giờ mới đủ), bass fill beat 1 và 2 theo root (beat 2 nhân đôi nhịp trống, beat 1 lấp khoảng trống), shaker ở 0.5/1.5/2.5 (hoàn thiện lưới offbeat mà base để lại ở 3.5), echo pluck trầm của motif head A-minor ở bar 9 và 16 (bar mà base không có giai điệu), và chuông A5 ở bar 4 và 14 (chuông tonic; base hoàn toàn không có chuông). Không flute (pluck là giọng chính), không pad (pad giữ thưa theo thiết kế).

## 3. Đo đạc (từ byte thật, ffmpeg loudnorm — phương pháp checkpoint 07/26)

Master WAV 48 kHz / 24-bit stereo; runtime OGG Vorbis q5.

| Layer | Dur (s) | Layer LUFS / TP | Cộng với base LUFS / TP | Seam wrapJump / raw |
|---|---|---|---|---|
| `MUSIC/ben_mua_layer_intensity` | 56,6667 | −24,99 / −9,96 | −20,65 / −9,34 | 2e-06 / 0,048126 |
| `MUSIC/lam_trieu_layer_intensity` | 53,3333 | −24,99 / −8,51 | −20,79 / −9,02 | 1e-06 / 0,021516 |
| `MUSIC/sa_hoa_layer_intensity` | 43,6364 | −25,00 / −10,20 | −20,03 / −6,87 | 1e-06 / 0,024692 |

Mỗi layer đúng target −25 LUFS (±0,5); cộng gộp với base đều dưới giới hạn −3,0 dBTP. Lưu ý cho adapter: cộng gộp của sa_hoa là −20,03 LUFS / −6,87 dBTP — **nóng nhất trong tất cả các layer đã giao** (vượt boss phase 5 ở checkpoint 5, −20,33 LUFS) — vì base sa_hoa vốn đã khô và dày ở dải giữa (trống beat 2 + pluck sáng + bass syncopation); adapter nên ride gain của layer khi fade vào thay vì cộng ở unity, giống ghi chú boss phase 5 ở checkpoint 5.

## 4. Delivery và validation

- Runtime audio manifest: 728 → **731 file** (composed 127 → 130; ported 541 file không đổi byte nào). Campaign 20 scene / 63 shot / 378 s / 21 dialogue cue không đổi; 21 embedded soundtrack không đổi.
- Validator độc lập `check_composed_score_md6_v1.py`: **PASS — 0 mismatches** (6 file hash lại + probe lại + đo lại loudnorm trong ±0,5 so với pack; 3 layer đo lại độ lớn cộng gộp trong ±0,5; coverage 15/15 + md6 3 layers + openForMdCp7).
- Validator MD1 chạy lại: **PASS, 0 mismatches** (20 file, 15 coverage slot). Validator MD2 chạy lại: **PASS, 0 mismatches** (74 file, 7 stem group). Validator MD3 chạy lại: **PASS, 0 mismatches** (96 file, 9 stem group). Validator MD4 chạy lại: **PASS, 0 mismatches** (6 file). Validator MD5 chạy lại: **PASS, 0 mismatches** (6 file) — sửa coverage ở checkpoint này không phá MD1/MD2/MD3/MD4/MD5 (`openForMdCp2`/`openForMdCp3`/`openForMdCp4`/`openForMdCp5`/`openForMdCp6` được giữ nguyên).
- Source re-validation `validate_media_deliveries.py`: **PASS, 0 mismatches** (có thêm checker `check_composed_score_md6_pack()`; tổng runtime cập nhật 728→731; 1359 audio file đã kiểm).
- Runtime re-verification `verify_runtime_delivery.py`: **PASS, 0 mismatches** (manifest total 731; counts music_ambience 22 / sfx_ui 519 / vo 30 / mix 30 / composed 130).
- Scope audit `check_agent_scope.py` (base integration 6f79853, branch media): content-only **14 path / 0 violations**; cumulative **1923 path / 1 violation `.gitattributes` đã biết** — artifact của merge-base cf17178 (file này byte-identical giữa integration 6f79853 và nhánh media; commit này không đụng tới nó).

## 5. Deliverable

- Builder: `Tools/MediaProduction/Muse/build_composed_score_md6.py` · Validator: `Tools/MediaProduction/Muse/check_composed_score_md6_v1.py`
- Pack: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD6_pack_v1.json` (3 cue) · Coverage: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json` (nhãn checkpoint 6 + khối md6 + `openForMdCp7`; `openForMdCp2`/`openForMdCp3`/`openForMdCp4`/`openForMdCp5`/`openForMdCp6` giữ nguyên để validator MD1/MD2/MD3/MD4/MD5 còn PASS)
- Master: `Art_Source/Audio/Muse/COMPOSED/layers/ben_mua_layer_intensity.wav` (16,32 MB) + `layers/lam_trieu_layer_intensity.wav` (15,36 MB) + `layers/sa_hoa_layer_intensity.wav` (12,57 MB) — tổng 44,25 MB (WAV, Git LFS)
- Runtime: `ClientGodot/assets/audio/composed/layers/*.ogg` (3), đã đăng ký trong `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json`
- Tool cập nhật: `Tools/MediaProduction/Muse/build_runtime_delivery.py` (§3p đăng ký MD6 + nhãn checkpoint + ghi chú MD6), `Tools/MediaProduction/Muse/validate_media_deliveries.py` (checker MD6 + cập nhật tổng 728→731 + checkpoint string + ghi chú MD6), `Tools/MediaProduction/Muse/verify_runtime_delivery.py` (chuỗi checkpoint + tổng 728→731)
- Báo cáo này + validation JSON: `Implementation/Reports/MuseMedia/MEDIA02_WO37_MD_CP6_SCORE_20261109.md` · `MEDIA02_WO37_MD_CP6_VALIDATION_20261109.json` · `MEDIA02_WO37_MD_CP6_SOURCE_REVALIDATION_20261109.json` · `MEDIA02_WO37_MD_CP6_RUNTIME_REVERIFY_20261109.json`

## 6. Ghi chú kỹ thuật

- Single-engine rule (từ checkpoint 2, vẫn giữ): builder chỉ load `build_composed_music.py` một lần làm engine duy nhất; không load bản copy thứ hai.
- Layer được loop-process giống hệt master (room, tail wrap 1,5 s, end landing 0,25 s) và gain-stage về target −25 LUFS bằng đúng dãy phép nhân tuần tự của gain_stage (MD3 helper), nên từng layer loop được độc lập. Không layer nào cần low-pass riêng (không base MD6 nào có màn low-pass).
- Không cue nào được render lại từ đầu: các layer là segment mới trên arrangement checkpoint-26 đã ship; không cần khôi phục RNG history như stem ở MD2/MD3.
- Đọc lại source CP26 trong lượt này để viết đúng thiết kế: lam_trieu shaker lá chỉ ở bar chẵn (range(0,20,2)) nên layer bổ sung đúng bar lẻ; sa_hoa trống chỉ ở beat 2 nên layer thêm đúng bar line; ben_mua bass chỉ ở beat 0/2 nên layer fill đúng beat 1/3.

## 7. Giới hạn / khuyết điểm

- COMPOSED_CANDIDATE, NOT_AUDITIONED: chưa nghe bằng tai — chất lượng layer cộng gộp và loop seam đều chưa thẩm âm; loudness/true-peak đã đo từ byte thật.
- M-D chưa xong toàn bộ: ear audition của toàn bộ cue MD1/MD2/MD3/MD4/MD5/MD6 + loop seam, và thêm phase layer (Thang Long / Tran Son / Bach Uyen / rift finale / quiet discovery intensity) vẫn mở cho checkpoint M-D 7 — đã liệt kê trong `openForMdCp7` của coverage matrix.
- Sa Hoa cộng gộp −20,03 LUFS / −6,87 dBTP (nóng nhất trong các layer đã giao): adapter nên ride gain khi fade vào.
- Final picture / mix / autoplay không thuộc khối này; các file là candidate song song, Codex quyết định adoption.

## 8. Khối tiếp theo

WO37 M-D checkpoint 7 (ear-audition prep hoặc thêm phase layer: Thang Long / Tran Son / Bach Uyen / rift finale / quiet discovery intensity) hoặc M-E (SFX/ambience biến thể thật) hoặc M-F (VO palette/pickups/pronunciation review pack) — theo thứ tự Codex đã giao. PR #119 mô tả + ACK M-D CP6 cần luồng chính đăng (cần thẻ duyệt của chủ dự án).
