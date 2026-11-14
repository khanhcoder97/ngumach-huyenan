# MEDIA-02 — WO37 M-D Checkpoint 3: Intro/outro + stems + phase layers for the checkpoint-26 score cues

- Ngày: 2026-11-08 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `6f79853`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (module M-D) · Audio Direction (`docs/production/Audio_Production_Direction_v1_vi.md` §1)
- Trạng thái: **COMPOSED_CANDIDATE** — nhạc sáng tác gốc, DRAFT, chưa thẩm âm; adoption là quyết định của Codex (presentation adapter).

## 1. Phạm vi khối

Coverage matrix (`MUSIC_SCORE_MD_COVERAGE_v1.json`) liệt kê khối này là `openForMdCp3` của checkpoint 2 (MD2: 7 cue MD1, 15/15 slot đã phủ). Khối này đóng cả ba mục:

- **Intro/outro** cho từng cue checkpoint-26 (2 bar mỗi đoạn, one-shot, target −22 LUFS như nhạc nền): intro kết bằng chuông handoff đúng downbeat đầu loop, outro đóng trên pad tonic + chuông với fade 0,5 s.
- **Stems** lead / pad-bass / percussion cho từng cue checkpoint-26 — regrouping của đúng arrangement checkpoint-26, không sáng tác lại.
- **Phase layers** cộng thêm (additive loops, target −25 LUFS): `boss_mang_cot_layer_phase3` (giai đoạn 3 boss Mãng Cốt), `tragedy_layer_intensity` (tăng cường cho tragedy) và `arena_layer_low` (lớp trầm cho đấu trường).

Không cue nào được sáng tác lại; không file ported nào bị đụng; không file MD1/MD2 nào bị đụng.

## 2. Khôi phục lịch sử render của checkpoint-26 (điểm chính của khối)

Checkpoint-26 (2026-11-05) được build trong nhiều lần render riêng, không phải một lần chạy tuần tự — nên một lần render lại tuần tự KHÔNG tái tạo được master đã ship (cả 9 cue đều DIFFERS ở lần thử đầu, dù LUFS/TP khớp tới 2 chữ số thập phân). Builder đã khôi phục lịch sử render của từng cue bằng tìm kiếm có kiểm chứng (so least-squares gain fit với master đã ship; một "match" là dư sau fit đúng bằng bước lượng tử 24-bit, 1,19e-07):

- 5 cue render từ RNG tươi (không render trước): ben_mua, thang_long, quiet_discovery, sa_hoa, bach_uyen.
- 4 cue render sau đúng một cue khác: rift_finale sau ben_mua, boss_mang_cot sau thang_long, lam_trieu sau quiet_discovery, tran_son sau sa_hoa.

Phiên gốc được build theo cặp — mỗi lần chạy `--only` hai cue theo đúng thứ tự piece: (ben_mua, rift_finale), (thang_long, boss_mang_cot), (quiet_discovery, lam_trieu), (sa_hoa, tran_son), (bach_uyen một mình). Bộ khung xác định (deterministic skeleton) của mọi cue đều khớp arrangement hiện tại: phần dư ở các cue chưa khớp tập trung ở các thành phần nhiễu (shaker/drum/breath), không phải ở mức nốt nhạc.

Gain cũng được khôi phục theo từng cue: thử multipliers của gain_stage trước (tái tạo bit-exact ở 8/9 cue); riêng ben_mua, gain_stage cho gain lệch ~0,01 dB so với master đã ship, nên gain được fit bằng least squares với master đã ship (0,16050922567019998) — pre-gain track bit-identical với bản gốc (dư sau fit đúng 1,19e-07, bằng bước lượng tử 24-bit), nên gain fit là gain gốc với sai số ~1e-9.

Hai lỗi đã gặp và sửa đúng nguồn trong lượt này (không giấu):

- **Lỗi /tmp đầy (tmpfs 512M):** các file đo/tạm của MD2 và lượt chạy này tích lũy tới 100% /tmp, khiến ffmpeg ghi master lỗi "No space left on device" giữa chừng. Đã sửa: dọn scratch cũ và chuyển TMP của builder sang `~/workspace/tmp/composed_score_md3` (đĩa persistent). Không mất dữ liệu nào — lượt chạy lại từ đầu và tái tạo đủ.
- **Lỗi single-factor gain (phát hiện qua probe):** bản nháp đầu của builder dùng một factor nhân một lần thay vì đúng dãy phép nhân tuần tự của gain_stage; điều đó đủ làm lệch LSB 24-bit và phá tái tạo bit-exact. Đã sửa: builder dùng đúng dãy multipliers của gain_stage (ghi lại từng mult), áp cùng dãy cho từng stem.
- **Lỗi validator tự bắt:** bản validator đầu kiểm tra fitted gain trong [0,99, 1,01] — sai, vì fitted gain ánh xạ track pre-gain (mix thô, nóng) về master đã ship nên nằm quanh 0,16–0,32. Đã sửa: khoảng plausibility [0,05, 2,0]; bằng chứng exactness là maxAbsDiff và stem-sum đo lại từ byte thật.

## 3. Đo đạc (từ byte thật, ffmpeg loudnorm — phương pháp checkpoint 07/26)

Master WAV 48 kHz / 24-bit stereo; runtime OGG Vorbis q5.

### Tái tạo reference (master checkpoint-26)

| Cue | Prior renders | Kết quả |
|---|---|---|
| ben_mua | — (tươi) | tái tạo tới 1,19e-07 sau fitted gain 0,160509 (không bit-exact) |
| thang_long | — (tươi) | sha MATCHES |
| boss_mang_cot | thang_long | sha MATCHES |
| quiet_discovery | — (tươi) | sha MATCHES |
| lam_trieu | quiet_discovery | sha MATCHES |
| sa_hoa | — (tươi) | sha MATCHES |
| tran_son | sa_hoa | sha MATCHES |
| bach_uyen | — (tươi) | sha MATCHES |
| rift_finale | ben_mua | sha MATCHES |

8/9 master tái tạo bit-exact (cùng sha256); ben_mua tái tạo tới đúng bước lượng tử 24-bit sau fitted gain.

### Stems (mỗi cue: lead / padbass / percussion; tổng cộng đúng bằng master checkpoint-26 đã ship)

| Cue cha | Lead LUFS / TP | Pad-bass LUFS / TP | Percussion LUFS / TP | Stem-sum max diff |
|---|---|---|---|---|
| ben_mua | −21,62 / −13,36 | −29,21 / −17,99 | −50,24 / −38,37 | 3,58e-07 |
| thang_long | −23,67 / −12,22 | −26,93 / −17,38 | −59,59 / −39,80 | 3,58e-07 |
| boss_mang_cot | −20,54 / −10,08 | −26,03 / −14,90 | −33,58 / −16,12 | 2,38e-07 |
| quiet_discovery | −19,21 / −15,39 | −35,91 / −26,40 | −43,21 / −31,23 | 2,38e-07 |
| lam_trieu | −19,44 / −15,37 | −29,02 / −17,37 | −55,20 / −39,07 | 2,38e-07 |
| sa_hoa | −19,60 / −11,03 | −24,54 / −14,34 | −41,90 / −28,24 | 2,38e-07 |
| tran_son | −21,27 / −13,34 | −25,67 / −15,05 | −36,74 / −24,00 | 2,38e-07 |
| bach_uyen | −20,27 / −16,80 | −24,38 / −12,60 | −51,39 / −39,40 | 2,38e-07 |
| rift_finale | −20,13 / −12,45 | −27,48 / −16,30 | −37,94 / −25,50 | 2,38e-07 |

Stem percussion của thang_long (−59,59 LUFS) và lam_trieu (−55,20 LUFS) rất nhỏ vì arrangement gốc chỉ có shaker; đó là nội dung thật của arrangement, không phải file rỗng. Không stem nào câm.

### Intro / outro (2 bar, one-shot, target −22 LUFS)

| Cue | Intro (s / LUFS / TP) | Outro (s / LUFS / TP) |
|---|---|---|
| ben_mua | 6,67 / −22,00 / −15,04 | 6,67 / −22,00 / −12,13 |
| thang_long | 5,22 / −22,00 / −12,99 | 5,22 / −22,00 / −9,21 |
| boss_mang_cot | 7,27 / −21,88 / −7,88 | 7,27 / −21,99 / −7,37 |
| quiet_discovery | 8,00 / −22,01 / −14,49 | 8,00 / −22,10 / −12,37 |
| lam_trieu | 5,33 / −22,18 / −14,11 | 5,33 / −22,00 / −12,10 |
| sa_hoa | 4,36 / −21,99 / −11,12 | 4,36 / −22,00 / −10,45 |
| tran_son | 5,33 / −22,18 / −7,00 | 5,33 / −22,00 / −8,13 |
| bach_uyen | 7,74 / −21,91 / −13,57 | 7,74 / −22,01 / −11,28 |
| rift_finale | 4,80 / −22,00 / −14,05 | 4,80 / −21,99 / −12,37 |

Quy tắc tail được giữ: chỉ outro của rift_finale chơi full flute tail (đó là lần khép đầy đủ duy nhất của cả bộ); outro của thang_long dùng low pluck tail (tiền lệ thang_long: chính cue này trả tail bằng low pluck ở bar 10–11); outro của boss dùng minor-head pluck fragment, outro của sa_hoa dùng motif head ánh xạ sang A minor. Intro/outro của bach_uyen giữ low-pass 850 Hz như cue cha.

### Phase layers (additive loop, target −25 LUFS; độ lớn cộng gộp đo từ byte thật)

| Layer | Dur (s) | Layer LUFS / TP | Cộng với base LUFS / TP |
|---|---|---|---|
| `MUSIC/boss_mang_cot_layer_phase3` | 36,36 | −25,00 / −7,87 | −20,29 / −4,77 |
| `MUSIC/tragedy_layer_intensity` | 51,43 | −24,98 / −10,82 | −20,21 / −6,40 |
| `MUSIC/arena_layer_low` | 32,00 | −25,00 / −12,40 | −19,52 / −3,80 |

Layer chỉ cộng thêm mật độ lên base cue, không thay thế base: phase 3 của boss thêm trống đủ 4 beat + bass pulse 16 nốt + chuông lạnh F4 mỗi bar + fragment pluck ở bar 0/3 (bar mà base và phase 2 đều không dùng); tragedy intensity thêm pulse trống beat 0/2 + bass pedal D2 + chuông D4 mỗi 2 bar + figure pluck ở bar 2/6/10 (base không có trống theo thiết kế); arena low là bed thưa — trống beat 0 + bass whole-note theo root progression của base + chuông D6 mỗi 4 bar — để adapter fade xuống khi cường độ thấp. Lưu ý: arena low cộng gộp khá nóng (−3,80 dBTP, sát giới hạn −3,0) — adapter nên ride gain của layer khi fade vào thay vì cộng ở unity; đã ghi trong pack (`combinedWithBase`).

## 4. Delivery và validation

- Runtime audio manifest: 674 → **722 file** (composed 73 → 121; ported 541 file không đổi byte nào). Campaign 20 scene / 63 shot / 378 s / 21 dialogue cue không đổi; 21 embedded soundtrack không đổi.
- Validator độc lập `check_composed_score_md3_v1.py`: **PASS — 0 mismatches** (96 file hash lại + probe lại + đo lại loudnorm trong ±0,5 so với pack; 9 nhóm stem cộng lại kiểm lại; 3 layer đo lại độ lớn cộng gộp trong ±0,5; 9/9 reference reproduction — 8 bit-exact, 1 tới 1,19e-07 sau fitted gain; coverage 15/15 + md3 9/9/27/3).
- Source re-validation `validate_media_deliveries.py`: **PASS, 0 mismatches** (có thêm checker `check_composed_score_md3_pack()`; tổng runtime cập nhật 674→722).
- Runtime re-verification `verify_runtime_delivery.py`: **PASS, 0 mismatches** (manifest total 722; counts music_ambience 22 / sfx_ui 519 / vo 30 / mix 30 / composed 121).
- Validator MD1 chạy lại: **PASS, 0 mismatches** (20 file, 15 coverage slot). Validator MD2 chạy lại: **PASS, 0 mismatches** (74 file, 7 stem group) — sửa coverage ở checkpoint này không phá MD1/MD2 (`openForMdCp2`/`openForMdCp3` được giữ nguyên, `reproHistories` ghi thêm trong block md3).
- Scope audit `check_agent_scope.py` (base integration 6f79853, branch media): content-only **104 path / 0 violations**; cumulative 1884 path / 1 violation `.gitattributes` đã biết — artifact của merge-base cf17178 (file này byte-identical giữa integration 6f79853 và nhánh media; commit này không đụng tới nó).
- Masters tổng 439,5 MB (WAV, Git LFS); runtime OGGs 6,86 MB.

## 5. Deliverable

- Builder: `Tools/MediaProduction/Muse/build_composed_score_md3.py` · Validator: `Tools/MediaProduction/Muse/check_composed_score_md3_v1.py`
- Pack: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD3_pack_v1.json` (48 cue) · Coverage: `Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json` (nhãn checkpoint 3 + khối md3 + `reproHistories` + `openForMdCp4`; `openForMdCp2`/`openForMdCp3` giữ nguyên để validator MD1/MD2 còn PASS)
- Master: `Art_Source/Audio/Muse/COMPOSED/intros/<stem>_intro.wav` (9) + `outros/<stem>_outro.wav` (9) + `stems/<stem>_stem_<group>.wav` (27) + `layers/<stem>.wav` (3)
- Runtime: `ClientGodot/assets/audio/composed/intros|outros|stems|layers/*.ogg` (48), đã đăng ký trong `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json`
- Tool cập nhật: `Tools/MediaProduction/Muse/build_runtime_delivery.py` (§3m đăng ký MD3 + nhãn checkpoint + ghi chú MD3), `Tools/MediaProduction/Muse/validate_media_deliveries.py` (checker MD3 + cập nhật tổng 674→722 + checkpoint string + ghi chú MD3), `Tools/MediaProduction/Muse/verify_runtime_delivery.py` (chuỗi checkpoint/verifies + tổng 674→722)
- Báo cáo này + validation JSON: `Implementation/Reports/MuseMedia/MEDIA02_WO37_MD_CP3_SCORE_20261108.md` · `MEDIA02_WO37_MD_CP3_VALIDATION_20261108.json` · `MEDIA02_WO37_MD_CP3_SOURCE_REVALIDATION_20261108.json` · `MEDIA02_WO37_MD_CP3_RUNTIME_REVERIFY_20261108.json`

## 6. Ghi chú kỹ thuật

- Single-engine rule (từ checkpoint 2, vẫn giữ): builder chỉ load `build_composed_music.py` một lần làm engine duy nhất; không load bản copy thứ hai (sẽ tách RNG và làm stems chứa cả mix).
- Gain recovery: gain_stage cho bit-exact ở 8/9 cue; ben_mua dùng fitted gain (least squares với master đã ship). Stems áp đúng gain của reference (cùng dãy multipliers, cùng thứ tự) nên tổng 3 stem bằng master đã ship trong giới hạn lượng tử hóa 24-bit.
- Stems được loop-process giống hệt master (lowpass cho bach_uyen, room, tail wrap 1,5 s, end landing 0,25 s) và nhân cùng gain với mix tham chiếu, nên từng stem loop được độc lập và tổng ba stem bằng master đã loop.
- Reference reproduction là bằng chứng tái tạo: render lại từ import mới cho cùng sha256 với master checkpoint-26 đã ship ở 8/9 cue — không phải chỉ "nghe giống". Cue còn lại (ben_mua) tái tạo tới đúng bước lượng tử 24-bit sau fitted gain.
- Stem percussion của thang_long (−59,59 LUFS) và lam_trieu (−55,20 LUFS) rất nhỏ vì arrangement gốc chỉ có shaker; không phải lỗi render.

## 7. Giới hạn / khuyết điểm

- COMPOSED_CANDIDATE, NOT_AUDITIONED: chưa nghe bằng tai — chất lượng intro/outro, stem balance, layer cộng gộp và loop seam đều chưa thẩm âm; loudness/true-peak/stem-sum đã đo từ byte thật.
- M-D chưa xong toàn bộ: ear audition của toàn bộ cue MD1/MD2/MD3 + loop seam, và thêm phase layer (boss phase 4, swamp/dungeon intensity) vẫn mở cho checkpoint M-D 4 — đã liệt kê trong `openForMdCp4` của coverage matrix.
- Arena low cộng gộp −3,80 dBTP, sát giới hạn −3,0: adapter nên ride gain khi fade vào.
- Final picture / mix / autoplay không thuộc khối này; các file là candidate song song, Codex quyết định adoption.

## 8. Khối tiếp theo

WO37 M-D checkpoint 4 (ear-audition prep hoặc thêm phase layer) hoặc M-E (SFX/ambience biến thể thật) hoặc M-F (VO palette/pickups/pronunciation review pack) — theo thứ tự Codex đã giao. PR #119 mô tả + ACK M-D CP3 cần luồng chính đăng (cần thẻ duyệt của chủ dự án).
