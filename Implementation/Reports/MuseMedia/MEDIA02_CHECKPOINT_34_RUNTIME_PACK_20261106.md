# MEDIA-02 CHECKPOINT 34 — Minimal runtime pack: prologue + CIN_001/002/004/006 (Gói 31 item 4) (2026-11-06)

## Trạng thái: DRAFT_NOT_FINAL, NOT_AUDITIONED

Pack runtime tối giản cho 5 cảnh: prologue CIN_000 + CIN_001/002/004/006.
Mỗi cảnh có OGV runtime (Theora 640×360 30fps + audio Vorbis 160 kbps)
+ MP4 review/master (H.264 640×360 30fps + AAC 192 kbps) + poster
640×360 PNG + SRT UTF-8/NFC + timing JSON. Runtime = video sạch +
subtitle overlay từ SRT sidecar; bản baked-subtitle chỉ để review.

## 1. Mix mới: CIN_006 draft mix v1

Lần đầu CIN_006 có scene mix, dựng theo đúng công thức P0 v3
(`build_cin006_mix_v1.py`): VO unity, nhạc về −30 LUFS, ambience về
−36 LUFS, ducking sidechaincompress (threshold 0.03, ratio 4,
attack 15 ms, release 350 ms), peak guard −1.0 dBTP.

| Hạng mục | Giá trị |
|---|---|
| Mix | `CIN_006_mix_draft_v1.wav`, 18.000 s, 48 kHz stereo pcm_s16le |
| Đo từ byte thật | −22.01 LUFS / −3.39 dBTP, peak trim 0.00 dB |
| Nhạc | MUSIC/thang_long (sáng tác, CP26), 0–18 s, ducked, đo lại −21.96 LUFS = bảng pack |
| Ambience | AMBIENCE/thang_long_crowd (sáng tác, CP30), 0–18 s, đo lại −30.59 LUFS = bảng pack |
| Stinger | SFX/CINEMA/reveal tại 6.0 s (đầu S02), PROPOSED |
| VO | VO_CIN_006_S03_HAMAC_draft_v1.wav tại 12.5 s (cửa sổ 12.5–17.5 s) |
| Ducking nhạc | −7.86 dB trong cửa sổ VO / 0.0 dB ngoài cửa sổ |
| Loop QA ambience | 1 mối nối tại 15.5 s, maxJump 0.00293, ratioToP999 0.678 |

**Phân bổ stem là MỚI và PROPOSED_CANDIDATE:** bảng stem CP02 không gán
stem nào cho CIN_006; timing manifest của cảnh chỉ liệt kê reveal là
candidate stem. Thang Long music + crowd ambience là cue bối cảnh
Thăng Long (sáng tác, CP26/CP30). Chưa khóa; Codex quyết ở review.

**Overrun giữ nguyên:** take VO 5.52 s chạy 12.5–18.02 s, vượt cuối
cảnh 0.02 s. Mix cắt đúng 18.00 s nên 0.02 s cuối của take bị cắt
trong fade 0.3 s ở biên cảnh — đã ghi trong manifest, không giấu;
cửa sổ, take và timing không đổi (quyết định của chủ dự án
2026-11-06, Codex quyết ở review PR). Alternate take CIN_006_ALT_T01
không có trong mix lẫn pack (DEC-MEDIA-P0 Q3).

## 2. Audio nhúng vào video (đo lại từ byte đã mã hóa)

Video stream copy bit-for-bit (`-c:v copy`): số stored frame trước/sau
mux bằng nhau ở cả 8 file (CIN_001 OGV 171 / MP4 1080; CIN_002 OGV 61 /
MP4 540; CIN_004 OGV 45 / MP4 540; CIN_006 OGV 480 / MP4 540). Mix
nguồn v3 đo: CIN_001 −21.06 / −1.66, CIN_002 −22.67 / −4.25,
CIN_004 −26.78 / −8.27 (CP31); lệch sau mã hóa ≤ 0.24 LUFS.

| Scene | Mix nhúng | OGV (Vorbis 160k) LUFS / dBTP | MP4 (AAC 192k) LUFS / dBTP |
|---|---|---|---|
| CIN_001 (36 s) | P0 v3 | −20.90 / −1.70 | −21.04 / −1.65 |
| CIN_002 (18 s) | P0 v3 | −22.43 / −4.46 | −22.50 / −4.27 |
| CIN_004 (18 s) | P0 v3 | −26.73 / −8.29 | −26.79 / −8.28 |
| CIN_006 (18 s) | CIN_006 v1 | −22.04 / −3.43 | −22.04 / −3.40 |
| CIN_000 (87.367 s) | prologue v1 (CP27) | đã có sẵn, xác minh không đổi | đã có sẵn, xác minh không đổi |

Mix P0 v1/v2 giữ nguyên dạng file riêng trong `mix/p0/` và `mix/p0_v2/`;
v3 là default nhúng, Codex chọn version ở review — đổi mix nhúng chỉ
là re-mux, không đổi hình. Poster/SRT/timing của 4 cảnh không đổi
(SRT 1 cue mỗi cảnh, khớp timing; CIN_000 6 cue narration, khớp timing).

## 3. Pack manifest + runtime delivery

- Pack index: `ClientGodot/assets/cinematics/RUNTIME_PACK_GOI31_v1.json`
  (5 cảnh, hash/codec/thời lượng/audio nhúng từng file + hợp đồng
  runtime: clean video + subtitle overlay; baked-subtitle review-only).
- Runtime audio: 610 → **611 file** (mix 13 → 14: thêm
  `mix/cin006_v1/CIN_006_mix_draft_v1.wav`); các file khác không đổi.
- `build_runtime_delivery.py` mở rộng: mục 3j (CIN_006 mix v1),
  kiểm tra audio stream cho clip khai `hasAudioTrack` (như mục 6b
  prologue), chuỗi checkpoint cập nhật CP34. Chạy lại: ALL VERIFIED.
- `validate_media_deliveries.py` mở rộng: `check_cin006_mix()` +
  kỳ vọng tổng audio 611 (trước đó hardcode 610).

## 4. Kiểm toán / đo đạc

| Kiểm tra | Kết quả |
|---|---|
| Source re-validation (`validate_media_deliveries.py`) | **PASS, 0 mismatch** (audio 1151 file, timing 20 cảnh / 21 cue, keyframe 39 batch + 12 P0, VO 21 take, mix P0 v1/v2/v3 4+4+4, CIN_006 mix v1 1/1, shortlist CP33 145 entry, clip 20/20, prologue 45 file) |
| Runtime re-verify (`verify_runtime_delivery.py`) | **PASS, 0 mismatch** (audio 611 file, clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic 3 file) |
| Scope audit vs integration 6f2b465 | **0 vi phạm** (1202 changed paths) |
| SRT | UTF-8/NFC, cue == timing dialogue ở cả 5 cảnh |
| Poster | 640×360 PNG ở cả 5 cảnh |

## 5. Giới hạn còn lại

- **NOT_AUDITIONED:** chưa nghe thẩm định mix/mux nào; mọi số LUFS/TP
  là đo từ byte, không phải PASS nghe tai.
- Mix vẫn DRAFT_MIX_NOT_FINAL; phân bổ stem CIN_006 PROPOSED;
  vị trí stinger PROPOSED chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; checkpoint này
  không chặn ở mức đó. Clip vẫn là Ken Burns trên still storyboard,
  không phải final pose animation.
- Gói 31 item 5 (.gitattributes) vẫn chờ merge commit của chủ dự án
  từ integration 6f2b465 — không tự viết policy (file `.git/info/
  attributes` local-only vẫn là mirror dùng để commit OGV qua LFS).
- Mô tả PR #119 vẫn ở checkpoint 01–31; cập nhật lên CP32–CP34 cần
  thẻ duyệt của chủ dự án qua luồng chính (không tự ghi qua connector).

## 6. File giao

- `Art_Source/Audio/Muse/MIX/CIN006_DRAFT_V1/CIN_006_mix_draft_v1.wav`
  + `CIN006_MIX_V1_manifest_v1.json`
- `ClientGodot/assets/audio/mix/cin006_v1/CIN_006_mix_draft_v1.wav`
- `ClientGodot/assets/cinematics/{CIN_001,CIN_002,CIN_004,CIN_006}/
  {*_640x360_30fps.ogv,*_640x360_30fps.mp4,scene_export_manifest_v1.json}`
  (đã mux audio, manifest cập nhật sha/size/audio)
- `ClientGodot/assets/cinematics/RUNTIME_PACK_GOI31_v1.json`
- `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json` (611 file)
- `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json`
- Tools: `Tools/MediaProduction/Muse/build_cin006_mix_v1.py`,
  `build_runtime_pack_goi31.py`; mở rộng `build_runtime_delivery.py`
  (mục 3j + kiểm tra audio clip) và `validate_media_deliveries.py`
  (`check_cin006_mix()` + tổng audio 611)
- Báo cáo này + `MEDIA02_CHECKPOINT_34_SOURCE_REVALIDATION_20261106.json`
  + `MEDIA02_CHECKPOINT_34_RUNTIME_REVERIFY_20261106.json`

## 7. Khối tiếp theo

Gói 31 item 5 (.gitattributes) chờ merge commit của chủ dự án; sau đó
fresh-checkout verify + scope re-audit. Nội dung media tiếp theo: các
pack còn thiếu của M3/M4/M5 (campaign motion/VO/music/SFX còn thiếu,
final media QA) — không quay sang game sprite/UI/map/VFX/Godot.
