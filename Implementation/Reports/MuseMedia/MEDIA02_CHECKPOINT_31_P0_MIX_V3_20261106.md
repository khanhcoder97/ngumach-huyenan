# MEDIA-02 CHECKPOINT 31 — Mix nháp P0 v3: cùng 3 scene, mix lại từ stem hoàn toàn sáng tác (Gói 30 item 7 follow-up, phần 2) (2026-11-06)

## Khối vừa hoàn thiện

Checkpoint 29 đã mix P0 lần hai từ stem sáng tác (nhạc + stinger
checkpoint 26) nhưng ambience vẫn là bản ported PackV1; checkpoint 30
đã sáng tác nốt 13 cue ambience nhưng chưa mix lại. Checkpoint 31
**mix lại cả 3 scene P0 từ stem HOÀN TOÀN SÁNG TÁC** — nhạc + stinger
composed (như v2) + ambience composed (checkpoint 30) thay cho ported,
cùng vị trí, cùng công thức gain, cùng ducking, cùng peak guard như
v1/v2 — để Codex có ba bản mix song song mà chọn ở review. **v1 và
v2 không bị thay thế; không còn stem ported nào trong mix P0.**

| Scene | Mix v3 đo thật | Mix v2 (CP29) | Mix v1 (CP20) |
|---|---|---|---|
| CIN_001 (36 s) | −21,06 LUFS / −1,66 dBTP; duck nhạc −3,92 dB / 0,0 dB | −21,24 / −1,51; duck −3,92 / 0,0 | −22,46 / −1,46; duck −14,32 / 0,0 |
| CIN_002 (18 s) | −22,67 LUFS / −4,25 dBTP; duck ambience −7,32 dB / 0,0 dB | −22,81 / −4,26; duck −6,48 / 0,0 | −21,55 / −3,98; duck −6,48 / 0,0 |
| CIN_004 (18 s) | −26,78 LUFS / −8,27 dBTP; duck nhạc −5,16 dB / 0,0 dB | −26,62 / −8,33; duck −5,16 / 0,0 | −25,51 / −7,94; duck −4,99 / 0,0 |
| Review 72 s | −22,49 LUFS / −1,66 dBTP | −22,72 / −1,51 | −22,66 / −1,46 |

- **Bảng thay thế so với v2 (chỉ đổi byte ambience):**
  rain_light ported −27,48 → composed −27,80 LUFS; river_shore
  ported −29,53 → composed −29,69; underwater ported −33,02 →
  composed −33,11 (runtime OGG, đo lại lượt này khớp bảng pack
  checkpoint 30 tới 0,01 LUFS). Nhạc/stinger giữ nguyên v2.
  Gain theo công thức: nhạc về đích −30 LUFS (quiet −8,28 dB,
  boss −8,02 dB), ambience chính −36 LUFS (river_shore −6,31 dB),
  phụ −38 LUFS (rain_light −10,20 dB, underwater −4,89 dB),
  stinger unity, VO unity làm neo. Không scene nào cần peak trim
  (true peak cao nhất −1,66 dBTP, dưới trần −1,0).
- **Duck CIN_001/CIN_004 giống hệt v2** (−3,92 / −5,16 dB) vì bus
  bị duck là nhạc, không đổi — kiểm chéo cho thấy pipeline ổn
  định. **Duck CIN_002 sâu hơn v2** (−7,32 so với −6,48 dB):
  tham số sidechain không đổi (threshold 0,03, ratio 4, attack
  15 ms, release 350 ms) và take VO giống hệt, nên chênh lệch là
  tính chất đo RMS trên cửa sổ 2 s của bed composed (bao biên
  trong cửa sổ khác bed ported: đo trực tiếp river_shore,
  composed −34,10/−34,12 dB ở 7–8/8–9 s so với ported
  −33,26/−34,69 dB, cùng mốc tham chiếu 4,5–6,5 s), không phải đổi
  tham số. Cân bằng thực tế vẫn chưa nghe tai.
- **Loop QA:** river_shore nối acrossfade 1 s, tỉ lệ nhảy mẫu tại
  mối nối 0,58–0,60× p99.9 của chính bed (như v1/v2), không dấu
  hiệu click theo số đo (nghe tai vẫn còn nợ). Bed composed mang
  cấu trúc loop end-landing 0,25 s của checkpoint 30; mixer vẫn
  nối bằng acrossfade 1 s riêng như với bed ported — số loop QA
  trong manifest đo trên đầu ra mixer, không phải seam của cue.
- **Runtime:** audio manifest 606 → **610 file** (mix 9 → 13);
  4 entry v3 (`MIX/V3/CIN_001`, `MIX/V3/CIN_002`, `MIX/V3/CIN_004`,
  `MIX/V3/P0_REVIEW_72S`, `mixVersion: v3_fully_composed`) tại
  `ClientGodot/assets/audio/mix/p0_v3/`; 9 entry mix cũ (5 v1 + 4
  v2) còn nguyên, byte-identical. Campaign totals không đổi
  (20 scene / 63 shot / 378 s / 21 cue).

## Trạng thái GitHub

- Nhánh `muse/media-production-20261104`: nội dung ở commit ngay trước
  báo cáo này; PR #119 vẫn OPEN và HOLD, head e08b1be (CP30).
  Issue #116 vẫn OPEN, 11 comment, cập nhật lần cuối
  2026-11-05T18:30:17Z — không có chỉ đạo mới kể từ ACK checkpoint
  08–26; integration vẫn ở f0859d0 (không có merge mới kể từ
  baseline CP28) nên không cần re-baseline M8.
- Mô tả PR #119 vẫn ghi checkpoint 01–26 — **cần luồng chính cập nhật
  mô tả PR (thêm checkpoint 27–31) qua GitHub connector**; lượt chạy
  định kỳ này không tự ghi qua connector vì cần thẻ duyệt của chủ dự án.

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_p0_mix_v3.py` (mới) | Builder mix P0 v3: sao từ build_p0_mix_v2.py (CP29), đổi 3 STEM ambience sang runtime OGG composed (checkpoint 30), MEASURED_LUFS theo số đo lại lượt này, provenance composed cho mọi stem, manifest `P0_MIX_V3_manifest_v1.json`, `mixVersion: v3_fully_composed`. |
| `Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/` (mới, 5 file) | 3 WAV mix scene v3 + WAV review 72 s v3 (48 kHz stereo) + `P0_MIX_V3_manifest_v1.json`. |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Thêm mục 3i: copy 4 file mix v3 vào `ClientGodot/assets/audio/mix/p0_v3/` kèm kiểm chứng, entry `mixVersion: v3_fully_composed`; nhãn checkpoint 31 + ghi chú v3 trong manifest audio. |
| `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json` | 610 file (606 → 610); mix 9 → 13. |
| `ClientGodot/assets/audio/mix/p0_v3/` (mới, 4 file) | 3 mix scene v3 + review 72 s v3, SHA khớp manifest nguồn (cùng blob LFS với file nguồn). |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Thêm `check_p0_mix_v3()` (byte + format + provenance composed cho MỌI stem, không còn stem ported + bằng chứng ducking/loop); cập nhật totalFiles kỳ vọng 606 → 610; nhãn checkpoint 31 + ghi chú v3. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Nhãn checkpoint 31. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build mix v3 — PASS
`build_p0_mix_v3.py` exit 0: 3 mix đúng thời lượng scene (36,000 /
18,000 / 18,000 s), review đúng 72,000 s, không scene nào cần peak
trim, ducking đo được cả 3 scene (âm trong cửa sổ, 0,0 dB ngoài cửa sổ).

### 2. Runtime delivery — PASS
`build_runtime_delivery.py` exit 0: audio manifest `totalFiles` 610
(22 + 519 + 30 VO + 13 mix + 26 composed), 4 file mix v3 qua đủ các
cổng kiểm chứng; v1/v2 không đổi.

### 3. Source re-validation — PASS, 0 mismatch
`validate_media_deliveries.py` verdict PASS, gồm mục mới: P0 draft
mixes v3 4/4 file (byte, format, provenance composed toàn bộ stem,
bằng chứng ducking/loop nhất quán). JSON:
`MEDIA02_CHECKPOINT_31_SOURCE_REVALIDATION_20261106.json` (audio files
checked 1151, p0_mix_v3_files_checked 4).

### 4. Runtime re-verify — PASS, 0 mismatch
`verify_runtime_delivery.py` verdict PASS: 610 file runtime khớp
manifest (runtime_audio_files_checked 610 = totalFiles 610). JSON:
`MEDIA02_CHECKPOINT_31_RUNTIME_REVERIFY_20261106.json`.

### 5. Scope audit — 0 vi phạm
Diff 3 chấm từ merge-base so với integration `f0859d0`: **1164 path,
0 violations** (CP30: 1153 path ở commit nội dung ad71e89, +1 path
báo cáo CP30, +10 path mới của checkpoint này: 5 file
`MIX/P0_DRAFT_V3/` + 4 file `mix/p0_v3/` + `build_p0_mix_v3.py`;
manifest audio + 3 tool sửa trong diff cũ nên không tăng số
đếm). Tất cả nằm trong các root media policy cho phép
(`Art_Source/Audio/Muse/`, `ClientGodot/assets/audio/`,
`Implementation/Reports/MuseMedia/`,
`Tools/MediaProduction/Muse/`). Nội dung ở commit `05b4cab`.

## Giới hạn còn lại

- DRAFT_MIX_NOT_FINAL: chưa nghe tai, chưa nghiệm thu cân bằng bằng tai
  người; bảng stem vẫn PROPOSED_CANDIDATE chưa khóa; vị trí stinger
  PROPOSED chờ picture lock; VO vẫn bản nháp TTS. Việc chọn v1, v2 hay
  v3 là quyết định adapter của Codex tại review PR #119.
- Duck CIN_002 v3 sâu hơn v2 (−7,32 so với −6,48 dB) là số đo RMS trên
  cửa sổ của bed composed; cân bằng VO/ambience thực tế ở scene này
  chỉ mới được kiểm chứng ở mức toàn scene, chưa nghe tai.
- P0 mix v1/v2/v3 đều dùng cùng VO nháp CP04 và cùng bảng stem CP02;
  không có OGV/subtitle thay đổi; campaign video 20/20 không đổi;
  prologue CIN_000 không đổi.
- Final picture vẫn chờ keyframe/character lock; checkpoint này chỉ
  chặn ở mức đó, không chặn timing/audio/subtitle.
