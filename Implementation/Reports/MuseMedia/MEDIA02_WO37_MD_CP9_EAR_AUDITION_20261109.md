# MEDIA-02 · WO37 M-D checkpoint 9 — Ear-audition preparation pack

- **Checkpoint:** MEDIA-02 WO37 M-D CP9 (ear-audition prep), 2026-11-09. Branch `muse/media-production-20261104`, baseline `6f79853`.
- **Trạng thái nghe: NOT_AUDITIONED.** Checkpoint này *chuẩn bị* buổi nghe tai cho toàn bộ audio đã giao (score sáng tác, ambience sáng tác, mix nháp, VO nháp). Không mục nào trong pack được coi là PASS nghe — PASS/FAIL chỉ có khi người nghe ghi verdict theo từng item id.
- **Deliverable:** `EAR_AUDITION_PACK_v1.json` (196 item, mỗi item có file + sha256 + loudness/peak + câu hỏi nghe + độ ưu tiên) và 7 playlist (nội dung M3U trong file `.txt`, vì `.m3u` không nằm trong policy extensions; đổi tên bản copy thành `.m3u` để mở trong player).

## Cách nghe

1. **Core pass** = 10 item P0 trong bảng dưới (khoảng 15 phút). **Full pass** = nghe hết 7 playlist theo thứ tự (tổng thời lượng đã biết 5.047,3 s ≈ 84 phút, chưa tính 30 file mix ≈ 13 phút → khoảng 97 phút).
2. **Layer phải nghe dạng base + layer cộng gộp** (đúng ca sử dụng của adapter): playlist 03 xếp master của cue cha ngay trước layer của nó. Số combined trong pack là số đo từ byte thật ở các checkpoint MD2–MD8.
3. Ghi verdict theo item id: `PASS` / `FAIL` / ghi chú. Item FAIL quay lại thành khối sửa riêng, không sửa lặng lẽ trong pack này.

## Hàng ưu tiên P0 (core pass)

| ID | Mục | Lý do nghe trước |
|---|---|---|
| VO-023 | VO/CIN001_S05 — Ly An "Đầu kia! Giữ giúp tôi đầu kia!" | Take nóng nhất nhóm P0: −16,01 LUFS (khớp độc lập số CP33), hơn các take khác ~5,5 LUFS — nghe có chói trên nền không |
| MIX-008 | Mix CIN_011 v1 (−20,34 LUFS) | Cửa sổ VO chỉ thừa 8 ms (CP45) — nghe câu thoại có bị cắt đuôi không |
| MIX-002 | Mix CIN_005 v1 (−21,03 LUFS) | Overrun VO +0,160 s giữ nguyên cho Codex quyết — nghe mức độ lấn sang shot sau |
| MIX-003 | Mix CIN_006 v1 (−22,01 LUFS) | Overrun VO +0,520 s giữ nguyên; bản canonical — alternate take riêng, không thay canon (DEC Q3) |
| MIX-015 | Mix CIN_018 v1 (−21,51 LUFS) | Overrun S03 +0,280 s giữ nguyên; take người chơi là VOICE_PLACEHOLDER_ONLY |
| LAY-007 | swamp_layer_intensity (combined −18,81 / −5,34) | Layer cộng gộp nóng nhất đã giao — nghe fade-in, adapter có cần ride gain không |
| LAY-001 | arena_layer_high (combined −19,33 / −4,00) | Top-3 nóng nhất |
| LAY-005 | arena_layer_low (combined −19,52 / −3,80) | Top-3 nóng nhất + true peak cộng gộp sát giới hạn −3,0 dBTP |
| SCR-006 | MUSIC/sa_hoa (master) | Cờ ear-check seam trong PRONUNCIATION_TABLE_v1 (indicator 0,016015) — nghe đúng điểm loop |
| AMB-007 | AMBIENCE/desert_wind | Seam wrapJumpRaw cao nhất trong ambience sáng tác (0,201266) — nghe điểm loop 16 s |

## Nội dung pack theo nhóm

| Nhóm | Số item | Nguồn số liệu |
|---|---|---|
| Score masters | 16 | MUSIC_COMPOSED_pack_v1 (CP26) + MUSIC_SCORE_MD1_pack_v1 |
| Stingers | 4 | MUSIC_COMPOSED_pack_v1 (CP26) |
| Transitions | 3 | MUSIC_SCORE_MD1_pack_v1 |
| Intro + outro | 32 | MUSIC_SCORE_MD2/MD3_pack_v1 |
| Stems (lead/pad-bass/percussion) | 48 | MUSIC_SCORE_MD2/MD3_pack_v1 |
| Layers (phase/intensity) | 20 | MUSIC_SCORE_MD2..MD8_pack_v1, kèm combined base+layer |
| Ambience sáng tác | 13 | AMBIENCE_COMPOSED_pack_v1 (CP30), kèm seam wrapJump/wrapJumpRaw |
| Mix nháp | 30 | Đo mới tại CP9 từ byte WAV thật (ffmpeg loudnorm): P0 v1/v2/v3 + review 72 s, 17 mix cảnh v1, prologue |
| VO nháp | 30 | RUNTIME_AUDIO_manifest_v1 (loudness đã ghi lúc giao) |

Playlist: `ear_audition_01_score_playlist.txt`, `02_intro_outro`, `03_layers`, `04_stems`, `05_ambience`, `06_mixes`, `07_vo` — cùng thư mục `Implementation/Reports/MuseMedia/`.

## Kiểm chứng

- Validator độc lập `check_ear_audition_pack_cp9_v1.py`: **PASS, 0 mismatch** — 196/196 item được hash lại từ đĩa và khớp sha256 trong pack; 7 playlist khớp đúng tập file của nhóm; mọi item P0 đều có cờ + câu hỏi nghe. Kết quả: `MEDIA02_WO37_MD_CP9_VALIDATION_20261109.json`.
- Kiểm chứng chéo: loudness mix đo mới tại CP9 khớp các báo cáo checkpoint gốc (CIN_005 −21,03; CIN_006 −22,01; CIN_011 −20,34; CIN_018 −21,51) và take Ly An S05 khớp CP33 (−16,01 LUFS ở cả hai lần đo độc lập).
- Source re-validation: **PASS** (ghi chú thường lệ: 2 overrun campaign VO là finding của đạo diễn theo D1, không phải lỗi byte). Runtime re-verify: **PASS** — checkpoint này không đổi file runtime nào; runtime audio giữ nguyên **737 file** (composed 136, ported 541 không đổi).
- Scope audit: xem commit message của checkpoint (nội dung chỉ gồm tools + reports, đúng policy roots).

## Giới hạn / bước tiếp theo

- Pack là *chuẩn bị* nghe, không phải kết quả nghe: toàn bộ vẫn **COMPOSED_CANDIDATE / DRAFT_NOT_FINAL / NOT_AUDITIONED**.
- Verdict của người nghe (chủ dự án hoặc Codex) sẽ quyết định item nào thành khối sửa; ba overrun VO vẫn giữ nguyên chờ Codex quyết khi review PR.
- Hàng chờ tiếp theo: M-E (SFX/ambience biến thể thật) và M-F (VO palette/pickups + pronunciation review) — không phụ thuộc buổi nghe, vẫn chạy song song được.
