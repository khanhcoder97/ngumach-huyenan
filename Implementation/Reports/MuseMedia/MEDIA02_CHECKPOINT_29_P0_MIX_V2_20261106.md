# MEDIA-02 CHECKPOINT 29 — Mix nháp P0 v2: cùng 3 scene, mix lại từ stem sáng tác (Gói 30 item 7 follow-up) (2026-11-06)

## Khối vừa hoàn thiện

Checkpoint 20 đã mix P0 lần đầu từ stem **ported** PackV1; checkpoint 26
đã sáng tác 13 cue gốc (nhạc + stinger) nhưng chưa mix lại. Checkpoint 29
**mix lại cả 3 scene P0 từ stem sáng tác** — nhạc + stinger composed thay
cho ported, ambience ported + VO nháp CP04 giữ nguyên, cùng vị trí, cùng
công thức gain, cùng ducking, cùng peak guard như v1 — để Codex có hai
bản mix song song mà chọn ở review. **v1 không bị thay thế.**

| Scene | Stem đổi (v1 → v2) | Mix v2 đo thật | Mix v1 (CP20) |
|---|---|---|---|
| CIN_001 (36 s) | quiet_discovery ported → composed; reveal_v01 → composed reveal | −21,24 LUFS / −1,51 dBTP; duck nhạc −3,92 dB / 0,0 dB | −22,46 / −1,46; duck −14,32 / 0,0 |
| CIN_002 (18 s) | tension_v01 → composed tension (ambience không đổi) | −22,81 LUFS / −4,26 dBTP; duck ambience −6,48 dB / 0,0 dB | −21,55 / −3,98; duck −6,48 / 0,0 |
| CIN_004 (18 s) | boss_mang_cot ported → composed; reveal_v01 → composed reveal | −26,62 LUFS / −8,33 dBTP; duck nhạc −5,16 dB / 0,0 dB | −25,51 / −7,94; duck −4,99 / 0,0 |
| Review 72 s | nối 3 mix v2 theo thứ tự reel | −22,72 LUFS / −1,51 dBTP | −22,66 / −1,46 |

- **Bảng thay thế (chỉ đổi byte stem):** MUSIC/quiet_discovery −21,58 →
  composed −21,72 LUFS (runtime OGG, đo lại 2026-11-06 khớp bảng CP26);
  MUSIC/boss_mang_cot −23,34 → composed −21,98; SFX/CINEMA/reveal_v01
  −25,69 → composed reveal −24,96 (stereo OGG 3,0 s); tension_v01 −25,67
  → composed tension −24,93 (stereo OGG 3,0 s). Ambience river_shore /
  rain_light / underwater giữ ported vì checkpoint 26 không sáng tác
  ambience. Gain theo công thức: nhạc về đích −30 LUFS (quiet −8,28 dB,
  boss −8,02 dB), ambience chính −36 / phụ −38 LUFS, stinger unity, VO
  unity làm neo. Không scene nào cần peak trim (true peak cao nhất
  −1,51 dBTP, dưới trần −1,0).
- **Duck CIN_001 nông hơn v1 là tính chất thật của stem, không phải lỗi
  tool:** đo bằng volumedetect trên đúng đoạn cửa sổ VO (cue 18,8–20,8 s),
  composed quiet_discovery là đoạn thưa gần như lặng (mean −45,8 dB, max
  −35,9 dB) trong khi ported cùng đoạn là −23,5 dB (max −9,6 dB) — bed
  yên hơn ~22 dB nên độ sâu duck đo được chỉ −3,92 dB so với −14,32 dB
  của v1. Cùng phương pháp đo, cùng take VO, cùng tham số sidechain
  (threshold 0,03, ratio 4, attack 15 ms, release 350 ms). CIN_002 duck
  **giống hệt v1** (−6,48 dB) vì ambience không đổi — kiểm chéo cho thấy
  pipeline ổn định; CIN_004 duck −5,16 dB ≈ v1 −4,99 dB.
- **Stinger stereo được giữ nguyên:** composed reveal/tension là OGG
  stereo, đặt vào mix không qua pan mono-to-stereo (v1 dùng pan vì
  stinger ported là WAV mono). Nếu dùng pan sẽ mất kênh phải — đã sửa
  trong tool v2 và ghi rõ.
- **Loop QA:** ambience river_shore nối acrossfade 1 s, tỉ lệ nhảy mẫu
  tại mối nối 0,694–0,701× p99.9 của chính bed (như v1), không dấu hiệu
  click theo số đo (nghe tai vẫn còn nợ).
- **Runtime:** audio manifest 589 → **593 file** (mix 5 → 9); 4 entry v2
  (`MIX/V2/CIN_001`, `MIX/V2/CIN_002`, `MIX/V2/CIN_004`,
  `MIX/V2/P0_REVIEW_72S`, `mixVersion: v2_composed_stems`) tại
  `ClientGodot/assets/audio/mix/p0_v2/`; 5 entry mix cũ (4 v1 + 1 mix
  phim CIN_000) còn nguyên, byte-identical. Campaign totals không đổi
  (20 scene / 63 shot / 378 s / 21 cue).

## Trạng thái GitHub

- Nhánh `muse/media-production-20261104`: nội dung ở commit ngay trước
  báo cáo này; PR #119 vẫn OPEN và HOLD. Issue #116 không có
  comment mới kể từ ACK checkpoint 08–26 (6665950785); PR #119 chưa có
  review nào của Codex; integration vẫn ở f0859d0 (không có merge mới
  kể từ baseline CP28) nên không cần re-baseline M8.
- Mô tả PR #119 vẫn ghi checkpoint 01–26 — **cần luồng chính cập nhật
  mô tả PR (thêm checkpoint 27–29) qua GitHub connector**; lượt chạy
  định kỳ này không tự ghi qua connector vì cần thẻ duyệt của chủ dự án.

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_p0_mix_v2.py` (mới) | Builder mix P0 v2: sao từ build_p0_mix.py (CP20), đổi STEM_FILES nhạc/stinger sang composed runtime OGG, MEASURED_LUFS theo số đo lại 2026-11-06, stinger đặt stereo (không pan), manifest ghi provenance từng stem + bảng thay thế + `mixVersion: v2_composed_stems`. |
| `Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/` (mới, 5 file) | 3 WAV mix scene v2 + WAV review 72 s v2 (48 kHz stereo) + `P0_MIX_V2_manifest_v1.json`. |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Thêm mục 3g: copy 4 file mix v2 vào `ClientGodot/assets/audio/mix/p0_v2/` kèm kiểm chứng, entry `mixVersion: v2_composed_stems`; nhãn checkpoint 29 + ghi chú v2 trong manifest audio. |
| `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json` | 593 file (589 → 593); mix 5 → 9. |
| `ClientGodot/assets/audio/mix/p0_v2/` (mới, 4 file) | 3 mix scene v2 + review 72 s v2, SHA khớp manifest nguồn (cùng blob LFS với file nguồn). |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Thêm `check_p0_mix_v2()` (byte + format + bằng chứng ducking/loop + khẳng định provenance composed cho nhạc/stinger, ported cho ambience); cập nhật totalFiles kỳ vọng 589 → 593 trong check_prologue; nhãn checkpoint 29. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Nhãn checkpoint 29; kiểm lại toàn bộ runtime theo manifest mới. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build mix v2 — PASS
`build_p0_mix_v2.py` exit 0: 3 mix đúng thời lượng scene (36,000 /
18,000 / 18,000 s), review đúng 72,000 s, không scene nào cần peak
trim, ducking đo được cả 3 scene (âm trong cửa sổ, 0,0 dB ngoài cửa sổ).

### 2. Runtime delivery — PASS
`build_runtime_delivery.py` exit 0: audio manifest `totalFiles` 593
(22 + 519 + 30 VO + 9 mix + 13 composed), 4 file mix v2 qua đủ các cổng
kiểm chứng; v1 không đổi.

### 3. Source re-validation — PASS, 0 mismatch
`validate_media_deliveries.py` verdict PASS, gồm mục mới: P0 draft
mixes v2 4/4 file (byte, format, provenance, bằng chứng ducking/loop
nhất quán). JSON:
`MEDIA02_CHECKPOINT_29_SOURCE_REVALIDATION_20261106.json` (audio files
checked 1125, p0_mix_v2_files_checked 4).

### 4. Runtime re-verify — PASS, 0 mismatch
`verify_runtime_delivery.py` verdict PASS: 593 file runtime khớp
manifest (runtime_audio_files_checked 593 = totalFiles 593). JSON:
`MEDIA02_CHECKPOINT_29_RUNTIME_REVERIFY_20261106.json`.

### 5. Scope audit — 0 vi phạm
Diff 3 chấm từ merge-base so với integration `f0859d0`: **1122 path,
0 violations** (CP28: 1110 path; +12 path mới của checkpoint này: 5 file
`MIX/P0_DRAFT_V2/` + 4 file `mix/p0_v2/` + `build_p0_mix_v2.py` + 2 JSON
kiểm chứng). Tất cả nằm trong các root media policy cho phép
(`Art_Source/Audio/Muse/`, `ClientGodot/assets/audio/`,
`Implementation/Reports/MuseMedia/`, `Tools/MediaProduction/Muse/`).
Nội dung ở commit `e9d1ce1`.

## Giới hạn còn lại

- DRAFT_MIX_NOT_FINAL: chưa nghe tai, chưa nghiệm thu cân bằng bằng tai
  người; bảng stem vẫn PROPOSED_CANDIDATE chưa khóa; vị trí stinger
  PROPOSED chờ picture lock; VO vẫn bản nháp TTS. Việc chọn v1 hay v2
  là quyết định adapter của Codex tại review PR #119.
- Duck CIN_001 v2 nông (−3,92 dB) phản ánh đúng đoạn nhạc thưa của cue
  composed trong cửa sổ VO; cân bằng thực tế giữa VO và nhạc ở scene
  này chỉ mới được kiểm chứng ở mức toàn scene, chưa nghe tai.
- Ambience vẫn là bản ported PackV1 (không có ambience sáng tác);
  541 file ported không bị tính là audio mới, giữ nguyên provenance.
- Không có OGV/subtitle thay đổi; campaign video 20/20 không đổi;
  prologue CIN_000 không đổi.
