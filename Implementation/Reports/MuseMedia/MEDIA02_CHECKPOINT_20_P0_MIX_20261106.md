# MEDIA-02 CHECKPOINT 20 — Mix nháp P0: bản mix scene đầu tiên (Gói 30 item 7) (2026-11-06)

## Quyết định chủ dự án ghi nhận trong lượt này

Về 3 take VO tràn cửa sổ (CIN_005_S03 +0,160 s, CIN_018_S03 +0,280 s,
CIN_006_S03 +0,520 s): chủ dự án chốt **giữ nguyên các cửa sổ hiện tại,
để Codex quyết khi review PR #119**. Không nới cửa sổ, không rút gọn
lời thoại, không hỏi lại việc này.

## Khối vừa hoàn thiện

Trước checkpoint này, mọi stem P0 mới chỉ được *đo* từng cue
(checkpoint 02/04/07/08) — chưa từng có bản mix scene nào. Checkpoint
20 dựng **bản mix nháp đầu tiên cho 3 scene P0** từ đúng bảng stem
theo shot PROPOSED_CANDIDATE của checkpoint 02 và VO nháp checkpoint
04, dùng byte stem runtime đã giao (`ClientGodot/assets/audio/`):

| Scene | Lớp âm thanh | Mix đo thật |
|---|---|---|
| CIN_001 (36 s) | VO @24,8 s (cửa sổ DECIDED); quiet_discovery 6–30 s duck theo VO; river_shore xuyên suốt + rain_light 0–6 s; reveal_v01 @30,0 s | −22,46 LUFS / −1,46 dBTP |
| CIN_002 (18 s) | VO @7,0 s; river_shore duck theo VO + underwater 0–6 s; tension_v01 @6,0 s | −21,55 LUFS / −3,98 dBTP |
| CIN_004 (18 s) | VO ngoài khung @7,5 s; boss_mang_cot 0–12 s duck theo VO; river_shore xuyên suốt; reveal_v01 @6,0 s | −25,51 LUFS / −7,94 dBTP |
| Review 72 s | nối 3 mix theo thứ tự reel | −22,66 LUFS / −1,46 dBTP |

- **Gain staging (công thức, ghi trong manifest):** VO giữ unity làm
  neo; music về đích −30 LUFS, ambience chính −36 LUFS, ambience phụ
  −38 LUFS (gain = đích − LUFS đã đo ở CP02); stinger unity. Không
  stem nào bị normalize đè lên số đo gốc.
- **Ducking đo được, không khẳng định suông:** sidechaincompress
  (threshold 0,03, ratio 4, attack 15 ms, release 350 ms, key = bus
  VO). Độ sâu đo trên bus đã duck so với bản chưa duck: CIN_001 music
  **−14,32 dB** trong cửa sổ / **0,0 dB** ngoài cửa sổ; CIN_002
  ambience **−6,48 / 0,0 dB**; CIN_004 music **−4,99 / 0,0 dB**.
  CIN_001 duck sâu nhất vì take VO S05 nóng hơn hẳn (−16,01 LUFS so
  với −21,6/−21,4 LUFS hai take kia — giới hạn đã ghi từ CP04); chỉnh
  duck riêng từng scene là việc của bản mix cuối. Bản render đầu với
  threshold 0,015/ratio 6 cho độ sâu −18,78 dB (gần như tắt nhạc) nên
  đã nới đường cong trước khi giao — manifest ghi rõ cả việc này.
- **Loop QA:** ambience 16 s được kéo dài bằng acrossfade 1 s; độ
  nhảy mẫu tối đa tại các mối nối là 0,00543, bằng **0,69–0,70×** mức
  p99.9 của chính bed — mối nối mượt hơn cả dao động thường của bed,
  không có dấu hiệu click theo số đo (nghe tai vẫn còn nợ).
- **Vị trí stinger là PROPOSED**, chờ picture lock: reveal ở đầu S06
  (CIN_001) và đầu S02 (CIN_004 — beat "dòng nước méo" không có
  timecode trong bất kỳ nguồn nào), tension ở đầu S02 (CIN_002).
- ben_mua và rain_heavy giữ nguyên không gán vào P0 như CP02;
  resolve/transition là stinger liên scene, không dùng.

## Trạng thái GitHub

- Nhánh `muse/media-production-20261104`: nội dung ở commit ngay
  trước báo cáo này; PR #119 vẫn OPEN và HOLD theo Gói 30.

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_p0_mix.py` (mới) | Builder mix P0: dựng bed ambience loop acrossfade + QA mối nối, bus music/VO/stinger theo bảng CP02, ducking sidechain + đo độ sâu hai phía cửa sổ, peak guard −1,0 dBTP, xuất manifest. |
| `Art_Source/Audio/Muse/MIX/P0_DRAFT/` (mới, 5 file) | 3 WAV mix scene + WAV review 72 s (48 kHz stereo) + `P0_MIX_manifest_v1.json`. |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Thêm mục 3d: copy 4 file mix vào `ClientGodot/assets/audio/mix/p0/` kèm kiểm chứng 4 cổng; counts thêm `mix`; nhãn checkpoint 20. |
| `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json` | 570 file (566 → 570); thêm 4 entry category `mix`. |
| `ClientGodot/assets/audio/mix/p0/` (mới, 4 file) | 3 mix scene + review 72 s, SHA khớp manifest nguồn. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Thêm `check_p0_mix()` (byte thật + format + bằng chứng ducking/loop trong manifest); nhãn checkpoint 20. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Nhãn checkpoint 20; kiểm lại toàn bộ runtime theo manifest mới. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build mix — PASS
`build_p0_mix.py` exit 0: 3 mix đúng thời lượng scene (36,000 / 18,000
/ 18,000 s), review đúng 72,000 s, không scene nào cần peak trim
(true peak cao nhất −1,46 dBTP, dưới trần −1,0).

### 2. Runtime delivery — PASS
`build_runtime_delivery.py` exit 0: audio manifest `totalFiles` 570
(22 + 519 + 25 VO + 4 mix), 4 file mix qua đủ 4 cổng kiểm chứng.

### 3. Source re-validation — PASS, 0 mismatch
`validate_media_deliveries.py` verdict PASS, gồm mục mới: P0 draft
mixes 4/4 file (byte, format, bằng chứng ducking/loop nhất quán).
JSON: `MEDIA02_CHECKPOINT_20_SOURCE_REVALIDATION_20261106.json`.

### 4. Runtime re-verify — PASS, 0 mismatch
`verify_runtime_delivery.py` verdict PASS: counts khớp manifest
(22/519/25/4). JSON: `MEDIA02_CHECKPOINT_20_RUNTIME_REVERIFY_20261106.json`.

### 5. Scope audit — 0 vi phạm
Diff 3 chấm từ merge-base `cf17178` so với integration `f0859d0`: 839 path, tất cả nằm trong các root media policy cho phép (`Art_Source/Audio/Muse/`, `ClientGodot/assets/audio/`, `Implementation/Reports/MuseMedia/`, `Tools/MediaProduction/Muse/`…). Nội dung ở commit `7652195`.

## Giới hạn còn lại

- DRAFT_MIX_NOT_FINAL: chưa nghe tai, chưa nghiệm thu cân bằng bằng
  tai người; bảng stem vẫn PROPOSED_CANDIDATE chưa khóa; vị trí
  stinger PROPOSED chờ picture lock; VO vẫn bản nháp TTS.
- Gain là đích công thức theo LUFS tích lũy của stem — loudness
  trong từng đoạn stem dao động, nên cân bằng thực tế chỉ mới được
  kiểm chứng ở mức toàn scene.
- Khi scene có hai bed ambience, chúng được cộng trên một sub-bus
  mang fade mép scene 0,3 s trước bản mix cuối (không nghe thấy ở
  mức bed, đã ghi trong manifest để minh bạch).
- Mix dùng byte stem runtime (OGG) thay cho master FLAC — đúng bản
  game sẽ chạy; bản mix cuối có thể dựng lại từ master nếu đạo diễn
  yêu cầu.
