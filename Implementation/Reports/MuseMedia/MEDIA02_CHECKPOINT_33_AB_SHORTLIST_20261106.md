# MEDIA-02 CHECKPOINT 33 — A/B review shortlist: P0 mix v1/v2/v3, nhạc/ambience, VO, loop seam (Gói 31 item 3) (2026-11-06)

## Trạng thái nghe: NOT_AUDITIONED

Môi trường này **không nghe được**. Mọi số loudness / true peak / seam trong báo cáo này đều đo từ byte thật (ffprobe / ffmpeg loudnorm / decode seam), **không phải PASS nghe tai**. Shortlist này giao cho người nghe: 6 playlist M3U + bảng A/B + bảng VO + bảng seam + bảng khuyết điểm có câu hỏi nghe cụ thể cho từng mục.

Quy tắc provenance giữ nguyên: alternate take CIN_006_ALT_T01 có takeId/version riêng, nằm trong playlist riêng, **không thay** dialogue canonical và không có trong playlist VO chính. Ba bản mix v1/v2/v3 giao song song; chọn bản nào là quyết định adapter của Codex tại review PR #119.

## Playlist (file .txt chứa nội dung M3U hợp lệ — đổi tên bản sao thành .m3u để mở trực tiếp trong trình phát; mở file từ trong repo để đường dẫn tương đối đúng; nghe theo thứ tự trong file)

Đuôi .m3u không nằm trong `mediaExtensions` của policy scope hiện hành (`agent_scope_v2.json`, do Codex sở hữu) nên playlist giao dưới dạng .txt; nội dung là M3U chuẩn (#EXTM3U/#EXTINF), không đổi gì khác.


| Playlist | Mục | Tổng thời lượng |
|---|---|---|
| `ab_shortlist_p0_mixes_playlist.txt` | 12 | 432.0 s |
| `ab_shortlist_music_playlist.txt` | 13 | 444.204 s |
| `ab_shortlist_ambience_playlist.txt` | 26 | 416.0 s |
| `ab_shortlist_vo_playlist.txt` | 21 | 75.192 s |
| `ab_shortlist_vo_alt_playlist.txt` | 1 | 3.0 s |
| `ab_shortlist_all_playlist.txt` | 72 | 1367.396 s |

## 1. A/B mix P0 v1 / v2 / v3 (đo lại từ byte thật)

- **v1:** stem ported PackV1 (nhạc + ambience + stinger).
- **v2:** nhạc + stinger sáng tác (CP26), ambience vẫn ported.
- **v3:** stem hoàn toàn sáng tác — nhạc + stinger (CP26) + ambience (CP30).
- Cùng bảng stem CP02, cùng VO nháp CP04, cùng công thức gain và ducking; v1/v2 không bị thay thế.

| Scene | v1 LUFS / dBTP | v2 LUFS / dBTP | v3 LUFS / dBTP | Δ v2−v1 | Δ v3−v1 | Δ v3−v2 |
|---|---|---|---|---|---|---|
| CIN_001 | -22.46 / -1.46 | -21.24 / -1.51 | -21.06 / -1.66 | +1.22 | +1.4 | +0.18 |
| CIN_002 | -21.55 / -3.98 | -22.81 / -4.26 | -22.67 / -4.25 | -1.26 | -1.12 | +0.14 |
| CIN_004 | -25.51 / -7.94 | -26.62 / -8.33 | -26.78 / -8.27 | -1.11 | -1.27 | -0.16 |
| REVIEW_72S | -22.66 / -1.46 | -22.72 / -1.51 | -22.49 / -1.66 | -0.06 | +0.17 | +0.23 |

Ducking đo được (depth trong cửa sổ VO / ngoài cửa sổ):

- v1 CIN_001 bus music: -14.32 dB / 0.0 dB, cửa sổ 24.8–27.368 s.
- v1 CIN_002 bus ambience: -6.48 dB / 0.0 dB, cửa sổ 7.0–10.792 s.
- v1 CIN_004 bus music: -4.99 dB / 0.0 dB, cửa sổ 7.5–9.252 s.
- v2 CIN_001 bus music: -3.92 dB / 0.0 dB, cửa sổ 24.8–27.368 s.
- v2 CIN_002 bus ambience: -6.48 dB / 0.0 dB, cửa sổ 7.0–10.792 s.
- v2 CIN_004 bus music: -5.16 dB / 0.0 dB, cửa sổ 7.5–9.252 s.
- v3 CIN_001 bus music: -3.92 dB / 0.0 dB, cửa sổ 24.8–27.368 s.
- v3 CIN_002 bus ambience: -7.32 dB / 0.0 dB, cửa sổ 7.0–10.792 s.
- v3 CIN_004 bus music: -5.16 dB / 0.0 dB, cửa sổ 7.5–9.252 s.

Loop QA trong mix (river_shore, acrossfade 1 s): tỉ lệ nhảy mẫu tại mối nối 0,58–0,60× p99.9 của chính bed ở cả ba version — không dấu hiệu click theo số đo; nghe tai vẫn còn nợ.

## 2. Nhạc sáng tác (9 cue) + stinger (4)

| Cue | Thời lượng | Đo lại LUFS / dBTP | Pack LUFS / dBTP | wrapJumpRaw (trước landing) |
|---|---|---|---|---|
| MUSIC/ben_mua | 56.6667 s | -21.93 / -10.33 | -21.93 / -10.33 | 0.138464 |
| MUSIC/thang_long | 41.7391 s | -21.96 / -10.55 | -21.96 / -10.55 | 0.14585 |
| MUSIC/boss_mang_cot | 36.3636 s | -21.98 / -7.35 | -21.98 / -7.35 | 0.039379 |
| MUSIC/quiet_discovery | 64.0 s | -21.72 / -13.09 | -21.72 / -13.09 | 0.064427 |
| MUSIC/lam_trieu | 53.3333 s | -21.93 / -10.98 | -21.93 / -10.98 | 0.043153 |
| MUSIC/sa_hoa | 43.6364 s | -21.96 / -8.58 | -21.96 / -8.58 | 0.005716 |
| MUSIC/tran_son | 40.0 s | -21.95 / -8.32 | -21.95 / -8.32 | 0.404087 |
| MUSIC/bach_uyen | 58.0645 s | -21.96 / -10.77 | -21.96 / -10.77 | 0.295172 |
| MUSIC/rift_finale | 38.4 s | -21.95 / -9.91 | -21.95 / -9.91 | 0.091384 |
| SFX/CINEMA/reveal (stinger, one-shot) | 3.0 s | -24.96 / -15.5 | -24.96 / -15.5 | — |
| SFX/CINEMA/tension (stinger, one-shot) | 3.0 s | -24.93 / -17.04 | -24.93 / -17.04 | — |
| SFX/CINEMA/resolve (stinger, one-shot) | 3.0 s | -24.93 / -18.3 | -24.93 / -18.3 | — |
| SFX/CINEMA/transition (stinger, one-shot) | 3.0 s | -24.97 / -16.16 | -24.97 / -16.16 | — |

Leitmotif 'câu nhạc bỏ lửng' (CP26): đuôi trả lời chỉ xuất hiện ở `resolve` và `rift_finale`. Chất lượng giai điệu và độ liền vòng lặp là nhận định nghe tai — chưa có.

## 3. Ambience: sáng tác (13) vs ported (13)

| Cue | Composed LUFS / dBTP (đo lại) | Ported LUFS / dBTP (đo lại) | Seam composed | Seam ported |
|---|---|---|---|---|
| AMBIENCE/rain_light | -27.8 / -16.59 | -27.48 / -18.6 | 0.000181 | 0.005862 |
| AMBIENCE/rain_heavy | -27.85 / -17.35 | -27.47 / -17.35 | 0.001097 | 0.053787 |
| AMBIENCE/river_shore | -29.69 / -17.08 | -29.53 / -17.96 | 0.000188 | 0.004403 |
| AMBIENCE/underwater | -33.11 / -20.68 | -33.02 / -19.12 | 9e-06 | 0.002945 |
| AMBIENCE/waterfall | -29.53 / -16.02 | -29.31 / -17.87 | 0.002209 | 0.015198 |
| AMBIENCE/wind_canopy | -29.7 / -16.06 | -29.55 / -19.23 | 0.000222 | 0.00519 |
| AMBIENCE/desert_wind | -29.93 / -17.26 | -29.57 / -18.69 | 0.000514 | 0.003816 |
| AMBIENCE/mountain_wind | -29.55 / -16.18 | -29.56 / -18.34 | 0.000734 | 0.004983 |
| AMBIENCE/cave_drips | -29.56 / -13.08 | -29.54 / -19.4 | 0.000362 | 0.003115 |
| AMBIENCE/forge | -29.49 / -15.85 | -29.5 / -17.74 | 0.000533 | 0.01175 |
| AMBIENCE/thang_long_crowd | -30.59 / -17.81 | -30.34 / -18.08 | 0.000286 | 0.001995 |
| AMBIENCE/city_night | -30.4 / -16.66 | -30.34 / -17.75 | 4.2e-05 | 0.004276 |
| AMBIENCE/rift | -30.46 / -21.3 | -30.48 / -18.05 | 0.000382 | 0.00095 |

Đích loudness của bed sáng tác là LUFS ported tương ứng ở CP07 (khớp trong 0,01 LUFS ở master; runtime OGG lệch tối đa 0,36 LUFS do mã hóa Vorbis). Bed sáng tác: nhiễu lọc + gust/swell + sự kiện rời rạc xác định; không sample, không giọng nói.

## 4. Loop seam — toàn bộ cue loop (xếp theo wrap jump đo lại)

Phương pháp CP07: decode mono 48 kHz f32; head/tail = 100 ms đầu/cuối; wrap jump = |mẫu cuối − mẫu đầu|. Chỉ số đo, không phải kết luận seamless. Ngưỡng gắn cờ nghe tai: > 0,015.

Lưu ý cơ sở đo: seam của nhạc sáng tác trong pack CP26 đo trên master WAV (sau landing), còn shortlist này đo lại trên runtime OGG — Vorbis mã hóa lại làm lệch điểm nối tới ~0,02 ở mức nhạc nên số runtime cao hơn số pack; đó không phải lỗi mới, mà là đúng số tai người nghe sẽ nghe từ file runtime. Seam của ambience sáng tác (CP30) và toàn bộ pack ported (CP07) đều đo trên runtime OGG nên so khớp trực tiếp.

| Cue | Bản | Wrap jump đo lại | Ghi trong pack | Cờ nghe |
|---|---|---|---|---|
| AMBIENCE/rain_heavy | ported | 0.053787 | 0.053787 | CỜ — nghe điểm nối |
| MUSIC/sa_hoa | composed | 0.016015 | 0.0 | CỜ — nghe điểm nối |
| AMBIENCE/waterfall | ported | 0.015198 | 0.015198 | CỜ — nghe điểm nối |
| AMBIENCE/forge | ported | 0.01175 | 0.01175 | — |
| MUSIC/tran_son | composed | 0.008203 | 2.1e-05 | — |
| AMBIENCE/rain_light | ported | 0.005862 | 0.005862 | — |
| AMBIENCE/wind_canopy | ported | 0.00519 | 0.00519 | — |
| AMBIENCE/mountain_wind | ported | 0.004983 | 0.004983 | — |
| AMBIENCE/river_shore | ported | 0.004403 | 0.004403 | — |
| AMBIENCE/city_night | ported | 0.004276 | 0.004276 | — |
| AMBIENCE/desert_wind | ported | 0.003816 | 0.003816 | — |
| AMBIENCE/cave_drips | ported | 0.003115 | 0.003115 | — |
| AMBIENCE/underwater | ported | 0.002945 | 0.002945 | — |
| MUSIC/lam_trieu | ported | 0.002703 | 0.002703 | — |
| MUSIC/boss_mang_cot | composed | 0.002311 | 2e-06 | — |
| AMBIENCE/waterfall | composed | 0.002209 | 0.0 | — |
| AMBIENCE/thang_long_crowd | ported | 0.001995 | 0.001995 | — |
| MUSIC/ben_mua | ported | 0.001742 | 0.001742 | — |
| MUSIC/rift_finale | ported | 0.001645 | 0.001645 | — |
| MUSIC/tran_son | ported | 0.001479 | 0.001479 | — |
| MUSIC/sa_hoa | ported | 0.001461 | 0.001461 | — |
| MUSIC/ben_mua | composed | 0.00144 | 4e-06 | — |
| MUSIC/thang_long | composed | 0.00141 | 4e-06 | — |
| AMBIENCE/rain_heavy | composed | 0.001097 | 1e-06 | — |
| AMBIENCE/rift | ported | 0.00095 | 0.00095 | — |
| AMBIENCE/mountain_wind | composed | 0.000734 | 4e-06 | — |
| MUSIC/quiet_discovery | ported | 0.000724 | 0.000724 | — |
| MUSIC/bach_uyen | composed | 0.000568 | 1.3e-05 | — |
| AMBIENCE/forge | composed | 0.000533 | 4e-06 | — |
| MUSIC/boss_mang_cot | ported | 0.000533 | 0.000533 | — |
| AMBIENCE/desert_wind | composed | 0.000514 | 5e-06 | — |
| AMBIENCE/rift | composed | 0.000382 | 2e-06 | — |
| AMBIENCE/cave_drips | composed | 0.000362 | 3e-06 | — |
| MUSIC/rift_finale | composed | 0.00036 | 3e-06 | — |
| AMBIENCE/thang_long_crowd | composed | 0.000286 | 1e-06 | — |
| MUSIC/bach_uyen | ported | 0.000263 | 0.000263 | — |
| AMBIENCE/wind_canopy | composed | 0.000222 | 1e-06 | — |
| MUSIC/quiet_discovery | composed | 0.000194 | 3e-06 | — |
| AMBIENCE/river_shore | composed | 0.000188 | 3e-06 | — |
| AMBIENCE/rain_light | composed | 0.000181 | 2e-06 | — |
| MUSIC/thang_long | ported | 0.000161 | 0.000161 | — |
| MUSIC/lam_trieu | composed | 5.9e-05 | 1e-06 | — |
| AMBIENCE/city_night | composed | 4.2e-05 | 4e-06 | — |
| AMBIENCE/underwater | composed | 9e-06 | 1e-06 | — |

## 5. VO dự thảo — 21 cửa sổ canonical (phát âm / tên riêng)

Giọng hư cấu, không clone giọng người thật, không sample không license. Nam dùng chung một production voice Helio trong bản nháp (xem D-02). 3 overrun giữ nguyên cửa sổ chờ Codex quyết.

| Shot | Người nói / giọng | Cửa sổ (s) | Take (s) | Khớp | LUFS đo lại | Tên riêng trong câu |
|---|---|---|---|---|---|---|
| CIN_001_S05 | Ly An / Aria (fictional system voice) | 24.8–28.5 (3.7 s) | 2.568 | FITS | -16.01 | — |
| CIN_002_S02 | Tạ Vân Khanh / Helio (fictional system voice) | 7.0–11.0 (4.0 s) | 3.792 | FITS | -21.61 | — |
| CIN_003_S03 | Ly An / Aria (fictional system voice) | 12.5–17.5 (5.0 s) | 4.032 | FITS | -19.32 | — |
| CIN_004_S02 | Ly An / Aria (fictional system voice) | 7.5–9.5 (2.0 s) | 1.752 | FITS | -21.41 | — |
| CIN_005_S03 | Ly An / Aria (fictional system voice) | 12.5–17.5 (5.0 s) | 5.16 | OVERRUN +0.16 s | -20.5 | — |
| CIN_006_S03 | Hạ Mặc / Helio (fictional system voice) | 12.5–17.5 (5.0 s) | 5.52 | OVERRUN +0.52 s | -21.96 | — |
| CIN_007_S03 | Ly An / Aria (fictional system voice) | 12.5–17.5 (5.0 s) | 3.912 | FITS | -18.1 | — |
| CIN_008_S03 | Tạ Vân Khanh / Helio (fictional system voice) | 12.5–17.5 (5.0 s) | 3.552 | FITS | -23.1 | — |
| CIN_009_S03 | Ly An / Aria (fictional system voice) | 12.5–17.5 (5.0 s) | 4.08 | FITS | -17.23 | — |
| CIN_010_S03 | Sầm Chủ Quỹ / Helio (fictional system voice) | 12.5–17.5 (5.0 s) | 2.808 | FITS | -22.01 | — |
| CIN_011_S03 | Hạ Mặc / Helio (fictional system voice) | 12.2–17.8 (5.6 s) | 5.592 | FITS | -21.5 | — |
| CIN_012_S03 | Hạ Mặc / Helio (fictional system voice) | 12.5–17.5 (5.0 s) | 4.32 | FITS | -25.38 | — |
| CIN_013_S03 | Trưởng đoàn / Helio (fictional system voice) | 12.5–17.5 (5.0 s) | 2.472 | FITS | -22.51 | — |
| CIN_014_S03 | Tống Bành / Helio (fictional system voice) | 12.5–17.5 (5.0 s) | 3.072 | FITS | -22.05 | — |
| CIN_015_S03 | Đội trưởng thợ lặn / Helio (fictional system voice) | 12.5–17.5 (5.0 s) | 2.88 | FITS | -23.27 | — |
| CIN_016_S03 | Hạ Mặc / Helio (fictional system voice) | 12.5–17.5 (5.0 s) | 2.472 | FITS | -21.92 | — |
| CIN_017_S03 | Đội trưởng thợ lặn / Helio (fictional system voice) | 12.5–17.5 (5.0 s) | 3.168 | FITS | -22.33 | — |
| CIN_018_S02 | Cơ Vô Tướng / Helio (fictional system voice) | 6.5–11.5 (5.0 s) | 2.88 | FITS | -23.77 | — |
| CIN_018_S03 | Người chơi / Helio (fictional system voice) | 12.5–17.5 (5.0 s) | 5.28 | OVERRUN +0.28 s | -22.54 | Sa Hỏa |
| CIN_019_S03 | Ly An / Aria (fictional system voice) | 12.5–17.5 (5.0 s) | 2.88 | FITS | -25.52 | — |
| CIN_020_S03 | Người nhận thư / Aria (fictional system voice) | 12.5–17.5 (5.0 s) | 3.0 | FITS | -19.59 | — |

Alternate take riêng (không trong playlist VO chính): CIN_006_ALT_T01 v1-alt — Hạ Mặc: “Tới đây ta theo được. Chỗ trống này giữ nguyên.” — playlist `ab_shortlist_vo_alt_playlist.txt`.

## 6. Bảng khuyết điểm cần người nghe trả lời

| ID | Mục | Bằng chứng đo được | Nghe ở đâu | Câu hỏi |
|---|---|---|---|---|
| D-01 | VO overrun (3 windows) | CIN_005_S03 +0.16 s (take 5.16 s vs window 5.0 s); CIN_006_S03 +0.52 s (take 5.52 s vs window 5.0 s); CIN_018_S03 +0.28 s (take 5.28 s vs window 5.0 s) | ab_shortlist_vo_playlist.txt — CIN_005_S03, CIN_006_S03, CIN_018_S03 | Câu thoại có bị cắt/nghe vội ở cuối cửa sổ không? Cửa sổ giữ nguyên chờ Codex quyết — không cắt thoại, không nới cửa sổ, không tăng tốc. |
| D-02 | VO male voices not distinct | Mọi nhân vật nam dùng chung một production voice Helio trong bản nháp (ghi trong VO manifest CP17/CP19). | ab_shortlist_vo_playlist.txt — CIN_008_S03, CIN_010_S03, CIN_011_S03, CIN_012_S03, CIN_014_S03, CIN_016_S03 | Có phân biệt được Tạ Vân Khanh / Sầm / Hạ Mặc / Tống Bành qua giọng không, hay nghe như một người? |
| D-03 | P0 VO loudness imbalance | CIN001_S05 take đo lại -16.01 LUFS, cao hơn trung bình 2 take P0 còn lại 5.5 LUFS (ghi chú CP04: ~5,5 LUFS). VO giữ unity trong mix nên chênh này đi thẳng vào mix. | ab_shortlist_vo_playlist.txt — CIN_001_S05 vs CIN_002_S02 / CIN_004_S02; ab_shortlist_p0_mixes_playlist.txt — CIN_001 | Câu S05 có to hẳn lên so với 2 câu P0 còn lại không? Cần gain-stage lại take hay giữ nguyên làm neo? |
| D-04 | Loop seam — rain_heavy (ported) | wrap jump đo lại 0.053787 (CP07 ghi 0.053787), cao nhất trong 22 cue ported; RMS đầu/cuối gần bằng nhau (0.030238 / 0.030504). | ab_shortlist_ambience_playlist.txt — AMBIENCE/rain_heavy PORTED | Có nghe tiếng click/nấc ở điểm nối vòng lặp 16 s không? |
| D-05 | Loop seam — composed music wrapJumpRaw | tran_son wrapJumpRaw 0.404, bach_uyen 0.295 (trước landing 0,25 s, CP26); wrap jump sau landing trên master ≈ 0, nhưng trên runtime OGG đo lại tran_son 0.008203 / bach_uyen 0.000568 (lệch do Vorbis mã hóa lại). Nghe tai vẫn còn nợ. | ab_shortlist_music_playlist.txt — MUSIC/tran_son, MUSIC/bach_uyen | Vòng lặp nhạc có liền mạch không, hay nghe rõ điểm nối? |
| D-06 | Ducking — CIN_002 v3 deeper than v2 | Duck ambience CIN_002: v3 −7,32 dB vs v2 −6,48 dB (cùng tham số sidechain; chênh do RMS bed composed trên cửa sổ 2 s, CP31). | ab_shortlist_p0_mixes_playlist.txt — CIN_002 v2 rồi v3 (cửa sổ VO 7,0–11,0 s) | Ở v3, ambience có bị dìm quá sâu dưới VO trong cửa sổ 7–11 s không? |
| D-07 | Crowd beds are filtered noise, not speech | thang_long_crowd / city_night composed là nhiễu qua dải formant trôi chậm — theo cấu trúc không thể tạo lời nói có nghĩa (CP30). Độ 'giống đám đông' là nhận định nghe tai. | ab_shortlist_ambience_playlist.txt — AMBIENCE/thang_long_crowd COMPOSED, AMBIENCE/city_night COMPOSED | Bed có đọc như đám đông thật không, hay nghe như nhiễu trắng lọc? |
| D-08 | Stinger placements PROPOSED | reveal @30,0 s CIN_001; tension trong CIN_004 — vị trí PROPOSED chờ picture lock (CP20/CP29/CP31). | ab_shortlist_p0_mixes_playlist.txt — CIN_001 v1/v2/v3 (30 s), CIN_004 v1/v2/v3 | Stinger có rơi đúng nhịp hình không, hay lệch/thừa? |
| D-09 | P0 mixes are DRAFT, never auditioned | v1/v2/v3 đều DRAFT_MIX_NOT_FINAL; cân bằng VO/nhạc/ambience chưa nghiệm thu bằng tai. Chênh LUFS giữa các version ≤ 1,4 LUFS/scene theo bảng A/B. | ab_shortlist_p0_mixes_playlist.txt — toàn bộ 12 file | Version nào nghe cân bằng nhất (VO rõ, nhạc không lấn, ambience không rỗng)? Ghi lựa chọn v1/v2/v3 theo scene. |
| D-10 | VO proper-name pronunciation | Tên riêng nói ra trong câu thoại: Sa Hỏa — chỉ 'Sa Hỏa' (CIN_018_S03). Tên người nói mà mỗi giọng phải đóng vai: Cơ Vô Tướng, Hạ Mặc, Ly An, Người chơi, Người nhận thư, Sầm Chủ Quỹ, Trưởng đoàn, Tạ Vân Khanh, Tống Bành, Đội trưởng thợ lặn. TTS hư cấu, chưa nghe tai. | ab_shortlist_vo_playlist.txt — toàn bộ 21 take | Tên riêng có phát âm đúng và thống nhất qua các take không? Giọng có hợp với nhân vật mình đóng vai không? Ghi lại tên nào nghe sai. |
| D-11 | Placeholder voices (cinematic-only) | CIN_020 dùng VOICE_LETTER_RECIPIENT cho Người nhận thư vô danh (vai giọng cinematic, không phải NPC gameplay); CIN_018_S03 PLAYER là timing-only placeholder, VOICE_GUIDE không gán giọng nói cho player. | ab_shortlist_vo_playlist.txt — CIN_020_S03, CIN_018_S03 | Giọng placeholder có chấp nhận được cho bản nháp không, hay cần casting riêng? |
| D-12 | Tên nhân vật viết không thống nhất — ĐÃ CHỐT | Chủ dự án chốt 2026-11-07: cách viết canonical là 'Tạ Vân Khanh' — khớp docs/production (176 lần; 'Văn Khánh' 0 lần), campaign VO manifest (CIN_008_S03), Cinema Production Pack và questkit PR #118. Cách viết sai 'Tạ Văn Khánh' không nằm trong manifest nào: P0 VO manifest chỉ lưu speaker ID NPC_TA_VAN_KHANH, nhãn hiển thị của take CIN_002_S02 do ánh xạ SPEAKER_DISPLAY dự phòng trong chính tool shortlist này sinh ra. Đã sửa ánh xạ và sinh lại nhãn tại checkpoint 36. Không thu lại VO: cả hai câu thoại đều không đọc tên nhân vật. | ab_shortlist_vo_playlist.txt — CIN_002_S02 vs CIN_008_S03 | Đã chốt — không còn câu hỏi mở về cách viết. Khi nghe hai take, kiểm tra giọng có đọc như cùng một nhân vật không (xem thêm D-02). |

## Giới hạn còn lại

- **NOT_AUDITIONED:** chưa có lần nghe thẩm định nào cho mix/nhạc/ambience/VO/seam trong checkpoint này; mọi kết luận nghe phải chờ người nghe làm việc với playlist trên.
- Mix vẫn DRAFT_MIX_NOT_FINAL; bảng stem PROPOSED_CANDIDATE chưa khóa; vị trí stinger PROPOSED chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; checkpoint này không chặn ở mức đó.
- Gói 31 item 4 (minimal runtime pack) là khối tiếp theo; item 5 (.gitattributes) vẫn chờ merge commit của chủ dự án từ integration.
