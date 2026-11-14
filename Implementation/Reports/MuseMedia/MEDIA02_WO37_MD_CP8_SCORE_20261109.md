# MEDIA-02 — WO37 M-D Checkpoint 8: Phase layer (thanh_lac intensity)

- Ngày: 2026-11-09 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `6f79853`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (module M-D) · Audio Direction (`docs/production/Audio_Production_Direction_v1_vi.md` §1)
- Trạng thái: **COMPOSED_CANDIDATE** — nhạc sáng tác gốc, DRAFT, chưa thẩm âm; adoption là quyết định của Codex (presentation adapter).

## 1. Phạm vi khối

Coverage matrix (`MUSIC_SCORE_MD_COVERAGE_v1.json`) liệt kê khối này là mục thứ hai của `openForMdCp8` (mục thứ nhất — ear audition toàn bộ cue MD1/MD2/MD3/MD4/MD5/MD6/MD7 — vẫn mở, vì không thể thẩm âm bằng tai trong lượt chạy tự động). Khối này đóng **phase layer cuối cùng còn thiếu cho một score cue**:

- **`MUSIC/thanh_lac_layer_intensity`** — nhịp chợ mà bản phối đường phố bận rộn nhất giữ lại (cue MD1, 16 bar @ 96 bpm, D major).

Sau checkpoint này **mọi cue nhạc sáng tác đều có intensity layer**: cả 9 cue nhạc checkpoint-26 (ben_mua, thang_long, boss_mang_cot, quiet_discovery, lam_trieu, sa_hoa, tran_son, bach_uyen, rift_finale) và cả 7 cue MD1 (hub_lac_chau, thanh_lac, rain_veil, swamp, dungeon, arena, tragedy) — qua các layer MD2/MD3/MD4/MD5/MD6/MD7 và layer này. Không còn intensity layer nào đang chờ cho một score cue.

Không cue nào được sáng tác lại; không file ported nào bị đụng; không file MD1/MD2/MD3/MD4/MD5/MD6/MD7 nào bị đụng.

## 2. Thiết kế layer (layer chỉ thêm thứ base và các layer trước chưa có)

- **Thanh Lac intensity:** base là bản phối đường phố bận rộn nhất — pad mọi bar, chuông tonic của hợp âm ở mọi bar line, bass ở CẢ BỐN beat, arpeggio pluck mọi bar cộng thêm một giọng pluck thứ hai off-beat thấp hơn một quãng tám, flute motif ở bar 0/8, tail bằng low pluck ở bar 12, và shaker ở mọi offbeat. Không trống. Layer thêm thứ duy nhất chợ giữ lại — trống mềm ở bar line và beat 2 (nhịp hai phách của chợ) — cộng echo pluck trầm của motif head ở bar 4 và 13 (bar mà base không có giai điệu; arpeggio là texture, không phải giai điệu). Không chuông (base đã rung mọi bar), không shaker (base đã giữ toàn bộ lưới offbeat), không bass fill (bass đã chơi cả bốn beat), không pad, không flute.

## 3. Đo đạc (từ byte thật, ffmpeg loudnorm — phương pháp checkpoint 07/26)

Master WAV 48 kHz / 24-bit stereo; runtime OGG Vorbis q5.

| Layer | Dur (s) | Layer LUFS / TP | Cộng với base LUFS / TP | Seam wrapJump / raw |
|---|---|---|---|---|
| `MUSIC/thanh_lac_layer_intensity` | 40,0000 | −25,00 / −15,21 | −21,66 / −10,58 | 0,0 / 0,001976 |

Layer đúng target −25 LUFS (±0,5); cộng gộp với base dưới giới hạn −3,0 dBTP. Lưu ý: số cộng gộp (−21,66 / −10,58) gần như trùng thang_long (−21,65 / −10,55) — cùng thiết kế layer trên một base gần như giống hệt (bận rộn nhất, không trống), nên đây là kiểm chứng chéo tự nhiên chứ không phải trùng lặp. WrapJumpRaw nhỏ (0,001976) vì layer gần như chỉ có trống mềm + hai echo pluck — tín hiệu cuối bar gần như im trước khi blend end-landing 0,25 s; wrapJump sau blend là 0,0.

## 4. Delivery và validation

- Runtime audio manifest: 736 → **737 file** (composed 135 → 136; ported 541 file không đổi byte nào). Campaign 20 scene / 63 shot / 378 s / 21 dialogue cue không đổi; 21 embedded soundtrack không đổi.
- Validator độc lập `check_composed_score_md8_v1.py`: **PASS — 0 mismatches** (2 file hash lại + probe lại + đo lại loudnorm trong ±0,5 so với pack; 1 layer đo lại độ lớn cộng gộp trong ±0,5; coverage 15/15 + md8 1 layer + openForMdCp9).
- Validator MD1 chạy lại: **PASS, 0 mismatches** (20 file, 15 coverage slot). Validator MD2 chạy lại: **PASS, 0 mismatches** (74 file, 7 stem group). Validator MD3 chạy lại: **PASS, 0 mismatches** (96 file, 9 stem group). Validator MD4 chạy lại: **PASS, 0 mismatches** (6 file). Validator MD5 chạy lại: **PASS, 0 mismatches** (6 file). Validator MD6 chạy lại: **PASS, 0 mismatches** (6 file). Validator MD7 chạy lại: **PASS, 0 mismatches** (10 file) — sửa coverage ở checkpoint này không phá MD1/MD2/MD3/MD4/MD5/MD6/MD7 (`openForMdCp2`…`openForMdCp8` được giữ nguyên).
- Source re-validation `validate_media_deliveries.py`: **PASS, 0 mismatches** (có thêm checker `check_composed_score_md8_pack()`; tổng runtime cập nhật 736→737; 1371 audio file đã kiểm).
- Runtime re-verification `verify_runtime_delivery.py`: **PASS, 0 mismatches** (manifest total 737; counts music_ambience 22 / sfx_ui 519 / vo 30 / mix 30 / composed 136).
- Scope audit `check_agent_scope.py` (base integration 6f79853, branch media): content-only **10 path / 0 violations**; cumulative **1949 path / 1 violation `.gitattributes` đã biết** — artifact của merge-base cf17178 (file này byte-identical giữa integration 6f79853 và nhánh media — cùng blob `7fea2800`; commit này không đụng tới nó).

## 5. Deliverable

- Builder: `Tools/MediaProduction/Muse/build_composed_score_md8.py` · Validator: `Tools/MediaProduction/Muse/check_composed_score_md8_v1.py`
- Pack: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD8_pack_v1.json` (1 cue) · Coverage: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json` (nhãn checkpoint 8 + khối md8 + `openForMdCp9`; `openForMdCp2`…`openForMdCp8` giữ nguyên để validator MD1/MD2/MD3/MD4/MD5/MD6/MD7 còn PASS)
- Master: `Art_Source/Audio/Muse/COMPOSED/layers/thanh_lac_layer_intensity.wav` (11,52 MB) — WAV, Git LFS
- Runtime: `ClientGodot/assets/audio/composed/layers/thanh_lac_layer_intensity.ogg` (212.861 byte), đã đăng ký trong `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json`
- Tool cập nhật: `Tools/MediaProduction/Muse/build_runtime_delivery.py` (§3r đăng ký MD8 + nhãn checkpoint + ghi chú MD8), `Tools/MediaProduction/Muse/validate_media_deliveries.py` (checker MD8 + cập nhật tổng 736→737 + checkpoint string + ghi chú MD8), `Tools/MediaProduction/Muse/verify_runtime_delivery.py` (chuỗi checkpoint + tổng 736→737 + nhãn checkpoint 8)
- Báo cáo này + validation JSON: `Implementation/Reports/MuseMedia/MEDIA02_WO37_MD_CP8_SCORE_20261109.md` · `MEDIA02_WO37_MD_CP8_VALIDATION_20261109.json` · `MEDIA02_WO37_MD_CP8_SOURCE_REVALIDATION_20261109.json` · `MEDIA02_WO37_MD_CP8_RUNTIME_REVERIFY_20261109.json`

## 6. Ghi chú kỹ thuật

- Single-engine rule (từ checkpoint 2, vẫn giữ): builder chỉ load `build_composed_music.py` một lần làm engine duy nhất; không load bản copy thứ hai.
- Layer được loop-process giống hệt master (room, tail wrap 1,5 s, end landing 0,25 s) và gain-stage về target −25 LUFS bằng đúng dãy phép nhân tuần tự của gain_stage (MD3 helper), nên layer loop được độc lập. Không cần low-pass riêng (thanh_lac không low-pass như bach_uyen).
- Không cue nào được render lại từ đầu: layer là segment mới trên arrangement MD1 đã ship; không cần khôi phục RNG history như stem ở MD2/MD3.
- Đọc lại source MD1 trong lượt này để viết đúng thiết kế: thanh_lac bass đã chơi cả bốn beat (pattern (0,1,2,3)) nên layer không fill bass; shaker đã ở mọi offbeat nên layer không thêm shaker; giọng pluck thứ hai off-beat đã có sẵn nên echo motif chỉ thêm ở bar 4 và 13 (bar không có giai điệu).
- Sửa hai lỗi ghi chú trong lúc viết builder: CP26 có 9 cue nhạc gồm boss_mang_cot (không phải 8 như báo cáo MD7 liệt kê tắt), và MD1 có 7 cue gồm tragedy (không phải boss_mang_cot/arena như bản nháp đầu của builder); các ví dụ layer tiếp theo trong `openForMdCp9` đã sửa cho đúng (arena low và tragedy intensity đã có từ MD3, không còn là ứng viên).

## 7. Giới hạn / khuyết điểm

- COMPOSED_CANDIDATE, NOT_AUDITIONED: chưa nghe bằng tai — chất lượng layer cộng gộp và loop seam đều chưa thẩm âm; loudness/true-peak đã đo từ byte thật.
- M-D chưa xong toàn bộ: ear audition của toàn bộ cue MD1/MD2/MD3/MD4/MD5/MD6/MD7/MD8 + loop seam vẫn mở cho checkpoint M-D 9 — đã liệt kê trong `openForMdCp9` của coverage matrix. Không còn intensity layer nào đang chờ; layer pha thêm (vd. boss phase 6) chỉ làm khi director yêu cầu.
- Final picture / mix / autoplay không thuộc khối này; file là candidate song song, Codex quyết định adoption.

## 8. Khối tiếp theo

WO37 M-D checkpoint 9 (ear-audition prep — danh sách nghe + kiểm seam có hệ thống cho toàn bộ cue MD1–MD8) hoặc M-E (SFX/ambience biến thể thật) hoặc M-F (VO palette/pickups/pronunciation review pack) — theo thứ tự Codex đã giao. PR #119 mô tả + ACK M-D CP8 cần luồng chính đăng (cần thẻ duyệt của chủ dự án); payload MD7 (PR mô tả + ACK) vẫn chưa đăng — payload MD8 gộp chung sẽ thay thế.
