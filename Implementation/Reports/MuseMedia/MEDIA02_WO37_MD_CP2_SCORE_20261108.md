# MEDIA-02 — WO37 M-D Checkpoint 2: Intro/outro + stems + phase layers for the MD1 score cues

- Ngày: 2026-11-08 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `6f79853`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (module M-D) · Audio Direction (`docs/production/Audio_Production_Direction_v1_vi.md` §1)
- Trạng thái: **COMPOSED_CANDIDATE** — nhạc sáng tác gốc, DRAFT, chưa thẩm âm; adoption là quyết định của Codex (presentation adapter).

## 1. Phạm vi khối

Coverage matrix (`MUSIC_SCORE_MD_COVERAGE_v1.json`) liệt kê khối này là `openForMdCp2` của checkpoint 1 (MD1: 7 cue nhạc lõi + 3 cầu nối, 15/15 slot đã phủ). Khối này đóng cả ba mục:

- **Intro/outro** cho từng cue MD1 (2 bar mỗi đoạn, one-shot, target −22 LUFS như nhạc nền): intro kết bằng chuông handoff đúng downbeat đầu loop, outro đóng trên pad tonic + chuông với fade 0,5 s.
- **Stems** lead / pad-bass / percussion cho từng cue MD1 — regrouping của đúng arrangement MD1, không sáng tác lại.
- **Phase layers** cộng thêm (additive loops, target −25 LUFS): `arena_layer_high` (cao trào đấu trường) và `boss_mang_cot_layer_phase2` (giai đoạn 2 boss Mãng Cốt).

Không cue nào được sáng tác lại; không file ported nào bị đụng; intro/outro/stems cho 9 cue checkpoint 26 vẫn mở (nếu director muốn) — xem `openForMdCp3`.

## 2. Tính chất stem-sum (điểm chính của khối)

Engine checkpoint 26 (`room` / `tail_wrap` / `end_landing` / `lowpass`) hoàn toàn tuyến tính, và mọi lần rút ngẫu nhiên đều đến từ một RNG toàn cục gieo hạt 26. Builder đã:

1. Render lại 7 mix tham chiếu MD1 theo đúng thứ tự MD1, từ một import mới — **cả 7 đều khớp bit-exact với master MD1 đã ship (cùng sha256)**.
2. Lưu trạng thái RNG tại đầu mỗi lần render tham chiếu và khôi phục trước mỗi lần render stem.
3. Chạy lại các piece builder với primitive được định tuyến: mỗi lần tổng hợp vẫn chạy (tiêu thụ RNG giống hệt), nhưng tín hiệu chỉ trộn vào stem đúng nhóm của nó, còn lại vào track bỏ đi.

Hệ quả, đo lại từ byte thật: **lead + padbass + percussion cộng đúng bằng master MD1 đã ship, trong giới hạn lượng tử hóa 24-bit** (max abs diff ≤ 3,58e-07, khoảng 2 LSB).

Hai lỗi đã gặp và sửa đúng nguồn trong lượt này (không giấu):

- **Lỗi instance engine kép:** lượt render đầu dùng một bản copy `build_composed_music.py` tải riêng, trong khi builder MD1 dùng instance `md1.cm` của chính nó — RNG tách đôi và các hàm nội bộ `melody`/`bass_line`/`drops` không được patch, nên mỗi stem chứa gần như cả mix (stem-sum lệch 0,59). Đã sửa: builder chỉ dùng `md1.cm` làm engine duy nhất; quy tắc này được ghi trong docstring của builder.
- **Lỗi `bright` cho flute:** `build_intro` truyền `bright=1.0` cho cả flute (chỉ pluck mới nhận `bright`). Đã sửa: chỉ truyền `bright` khi voice là pluck.
- **Loudness của stem câm:** loudnorm của file câm là −inf, không phải JSON hợp lệ. Stem percussion của tragedy (cue không có bộ gõ theo thiết kế) được ghi loudness `null` + cờ `silence`, validator kiểm tra độ câm từ byte thật thay vì so số.

## 3. Đo đạc (từ byte thật, ffmpeg loudnorm — phương pháp checkpoint 07/26)

Master WAV 48 kHz / 24-bit stereo; runtime OGG Vorbis q5.

### Stems (mỗi cue: lead / padbass / percussion; tổng cộng đúng bằng master MD1)

| Cue cha | Lead LUFS / TP | Pad-bass LUFS / TP | Percussion LUFS / TP | Stem-sum max diff |
|---|---|---|---|---|
| hub_lac_chau | −21,86 / −10,03 | −22,10 / −10,81 | −21,92 / −10,61 | 2,38e-07 |
| thanh_lac | −23,69 / −12,37 | −26,87 / −17,51 | −58,83 / −38,73 | 2,38e-07 |
| rain_veil | −19,05 / −10,27 | −25,61 / −13,77 | −43,13 / −30,77 | 2,38e-07 |
| swamp | −21,39 / −17,71 | −24,66 / −10,10 | −47,84 / −35,97 | 2,38e-07 |
| dungeon | −21,04 / −11,21 | −26,29 / −14,28 | −40,59 / −27,31 | 3,58e-07 |
| arena | −24,58 / −12,09 | −25,66 / −13,12 | −39,04 / −19,43 | 2,38e-07 |
| tragedy | −19,40 / −11,02 | −27,17 / −15,86 | câm (null) | 2,38e-07 |

Stem percussion của tragedy là digital silence theo thiết kế (cue không có trống/shaker/drops/noise) — đã xác minh max abs = 0,0 từ byte thật. Stem percussion của thanh_lac chỉ có shaker nên rất nhỏ (−58,83 LUFS); đó là nội dung thật của arrangement, không phải file rỗng.

### Intro / outro (2 bar, one-shot, target −22 LUFS)

| Cue | Intro (s / LUFS / TP) | Outro (s / LUFS / TP) |
|---|---|---|
| hub_lac_chau | 6,00 / −22,01 / −14,00 | 6,00 / −22,02 / −7,68 |
| thanh_lac | 5,00 / −21,89 / −13,70 | 5,00 / −21,99 / −9,13 |
| rain_veil | 7,27 / −21,85 / −12,85 | 7,27 / −22,00 / −11,70 |
| swamp | 8,28 / −22,00 / −12,97 | 8,28 / −22,00 / −12,09 |
| dungeon | 6,86 / −21,99 / −8,59 | 6,86 / −22,04 / −7,00 |
| arena | 4,00 / −21,98 / −10,77 | 4,00 / −22,00 / −11,86 |
| tragedy | 8,57 / −21,93 / −14,80 | 8,57 / −22,00 / −12,88 |

Quy tắc tail được giữ: không outro nào dùng full flute tail (F#–E–D) — tail đầy đủ vẫn chỉ dành cho stinger `resolve` và `rift_finale`. Outro của hub / Thanh Lạc dùng low pluck tail theo tiền lệ thang_long (đã có trong loop của hai cue này).

### Phase layers (additive loop, target −25 LUFS; độ lớn cộng gộp đo từ byte thật)

| Layer | Dur (s) | Layer LUFS / TP | Cộng với base LUFS / TP |
|---|---|---|---|
| `MUSIC/arena_layer_high` | 32,00 | −25,00 / −12,58 | −19,33 / −4,00 |
| `MUSIC/boss_mang_cot_layer_phase2` | 36,36 | −25,00 / −11,40 | −20,38 / −5,64 |

Layer chỉ cộng thêm mật độ lên base cue, không thay thế base: arena thêm shaker móc đơn + bass ostinato + trống ở beat 1/3 + chuông mỗi 2 bar; boss phase 2 thêm trống lấp beat 1/2/3 quanh nhịp tim của base, bass D1 móc đơn, chuông lạnh F4 mỗi 2 bar, mảnh pluck thứ ở bar 1/4/6/9 (base dùng 2/5/7/8). Không pad, không sáo trong layer — hai nhóm đó ở lại base.

## 4. Delivery và validation

- Runtime audio manifest: 637 → **674 file** (composed 36 → 73; ported 541 file không đổi byte nào). Campaign 20 scene / 63 shot / 378 s / 21 dialogue cue không đổi; 21 embedded soundtrack không đổi.
- Validator độc lập `check_composed_score_md2_v1.py`: **PASS — 0 mismatches** (74 file hash lại + probe lại + đo lại loudnorm trong ±0,5 so với pack; 7 nhóm stem cộng lại kiểm lại; 2 layer đo lại độ lớn cộng gộp trong ±0,5; 7/7 reference reproduction khớp sha MD1; coverage 15/15 + md2 7/7/21/2).
- Source re-validation `validate_media_deliveries.py`: **PASS, 0 mismatches** (có thêm checker `check_composed_score_md2_pack()`; tổng runtime cập nhật 637→674).
- Runtime re-verification `verify_runtime_delivery.py`: **PASS, 0 mismatches** (manifest total 674; counts music_ambience 22 / sfx_ui 519 / vo 30 / mix 30 / composed 73).
- Validator MD1 chạy lại: **PASS, 0 mismatches** (20 file, 15 coverage slot) — sửa coverage ở checkpoint này không phá MD1 (`openForMdCp2` được giữ nguyên).
- Scope audit `check_agent_scope.py` (base integration 6f79853, branch media): content-only **82 path / 0 violations**; cumulative 1781 path / 1 violation `.gitattributes` đã biết — artifact của merge-base cf17178 (file này byte-identical giữa integration 6f79853 và nhánh media; commit này không đụng tới nó).
- Masters tổng 321,7 MB (WAV, Git LFS); runtime OGGs 5,80 MB.

## 5. Deliverable

- Builder: `Tools/MediaProduction/Muse/build_composed_score_md2.py` · Validator: `Tools/MediaProduction/Muse/check_composed_score_md2_v1.py`
- Pack: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD2_pack_v1.json` (37 cue) · Coverage: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json` (nhãn checkpoint 2 + khối md2 + `openForMdCp3`; `openForMdCp2` giữ nguyên để validator MD1 còn PASS)
- Master: `Art_Source/Audio/Muse/COMPOSED/intros/<stem>_intro.wav` (7) + `outros/<stem>_outro.wav` (7) + `stems/<stem>_stem_<group>.wav` (21) + `layers/<stem>.wav` (2)
- Runtime: `ClientGodot/assets/audio/composed/intros|outros|stems|layers/*.ogg` (37), đã đăng ký trong `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json`
- Tool cập nhật: `Tools/MediaProduction/Muse/build_runtime_delivery.py` (§3l đăng ký MD2 + nhãn checkpoint + ghi chú MD2), `Tools/MediaProduction/Muse/validate_media_deliveries.py` (checker MD2 + cập nhật tổng 637→674 + checkpoint string + ghi chú MD2), `Tools/MediaProduction/Muse/verify_runtime_delivery.py` (chuỗi checkpoint/verifies + tổng 637→674)
- Báo cáo này + validation JSON: `Implementation/Reports/MuseMedia/MEDIA02_WO37_MD_CP2_SCORE_20261108.md` · `MEDIA02_WO37_MD_CP2_VALIDATION_20261108.json` · `MEDIA02_WO37_MD_CP2_SOURCE_REVALIDATION_20261108.json` · `MEDIA02_WO37_MD_CP2_RUNTIME_REVERIFY_20261108.json`

## 6. Ghi chú kỹ thuật

- Stems được loop-process giống hệt master (lowpass cho rain, room, tail wrap 1,5 s, end landing 0,25 s) và nhân cùng gain factor với mix tham chiếu, nên từng stem loop được độc lập và tổng ba stem bằng master đã loop.
- Reference reproduction là bằng chứng tái tạo: render lại từ import mới cho cùng sha256 với master MD1 đã ship — không phải chỉ "nghe giống".
- Layer cộng gộp khá nóng: arena base (−22) + layer (−25) = −19,33 LUFS / −4,00 dBTP; boss base (−22) + layer (−25) = −20,38 LUFS / −5,64 dBTP. Adapter nên ride gain của layer khi fade vào thay vì cộng ở unity — đã ghi trong pack (`combinedWithBase`).
- Stem percussion của thanh_lac (−58,83 LUFS) và rain/swamp/dungeon (chỉ drops) rất nhỏ vì arrangement gốc ít bộ gõ; không phải lỗi render.

## 7. Giới hạn / khuyết điểm

- COMPOSED_CANDIDATE, NOT_AUDITIONED: chưa nghe bằng tai — chất lượng intro/outro, stem balance, layer cộng gộp và loop seam đều chưa thẩm âm; loudness/true-peak/stem-sum đã đo từ byte thật.
- M-D chưa xong toàn bộ: intro/outro + stems cho 9 cue checkpoint 26 (nếu director muốn), thêm phase layer (boss phase 3, tragedy intensity, arena low) và ear audition vẫn mở cho checkpoint M-D 3 — đã liệt kê trong `openForMdCp3` của coverage matrix.
- Final picture / mix / autoplay không thuộc khối này; các file là candidate song song, Codex quyết định adoption.

## 8. Khối tiếp theo

WO37 M-D checkpoint 3 (intro/outro + stems cho cue checkpoint 26 nếu director muốn, thêm phase layer, hoặc ear-audition prep) hoặc M-E (SFX/ambience biến thể thật) — theo thứ tự Codex đã giao. PR #119 mô tả + ACK M-D CP1/CP2 cần luồng chính đăng (cần thẻ duyệt của chủ dự án).
