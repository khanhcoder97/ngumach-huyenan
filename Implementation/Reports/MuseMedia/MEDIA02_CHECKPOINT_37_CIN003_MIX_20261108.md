# MEDIA-02 CHECKPOINT 37 — Mix nháp CIN_003 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `46b3d84`, checkpoint 36. Issue #116 đầu lượt: vẫn 13
comment, không có chỉ đạo mới của Codex/chủ dự án sau ACK Gói 31; integration
không đổi ở `6f2b465`; PR #119 vẫn OPEN/HOLD, head `46b3d84`, 65 commit / 1215 file.)

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_003 ("Hai người, hai bóng", 18 s) — mix cảnh thứ hai sau
CIN_006 v1 (checkpoint 34), cùng công thức P0 v3 — và nhúng vào runtime OGV +
review MP4 của cảnh. Hoàn tất vòng mở đầu: cả 4 cảnh opening (CIN_001/002/003/
004) nay đều có mix nhúng trong clip runtime.

- `Tools/MediaProduction/Muse/build_cin003_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_003; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/ben_mua` + ambience `AMBIENCE/river_shore` (nhạc/nền Bến Mưa —
  cảnh quay ở hồ sen/bến gỗ, đúng setting) + stinger `SFX/CINEMA/reveal` tại
  6,0 s (đầu S02, PROPOSED chờ picture lock, theo mẫu CIN_004/CIN_006) + VO
  take CP17 `VO_CIN_003_S03_LYAN_draft_v1.wav` tại 12,5 s. Tất cả stem đều
  composed (CP26/CP30), không còn stem ported nào trong mix.
- Điểm khác CIN_006 (nói thẳng): take VO CIN_003 VỪA trong cửa sổ — 4,032 s,
  chạy 12,5–16,532 s, kết thúc trước cuối cửa sổ 17,5 s là 0,968 s. Không
  overrun, không cắt đuôi ở mép cảnh (tail trim 0,0 s). Cửa sổ, take và
  timing không bị sửa để che giấu gì.
- `Art_Source/Audio/Muse/MIX/CIN003_DRAFT_V1/CIN_003_mix_draft_v1.wav` +
  `CIN003_MIX_V1_manifest_v1.json`: mix 18,000 s, −21,16 LUFS / −4,63 dBTP,
  peak trim 0,00 dB; ducking nhạc −10,42 dB trong cửa sổ VO, 0,0 dB ngoài
  cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 = 0,58. Ba stem đo
  lại từ byte thật khớp đúng bảng pack (ben_mua −21,93; river_shore −29,69;
  reveal −24,96 LUFS).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin003_v1/` (sha
  khớp manifest nguồn); OGV + MP4 của CIN_003 mux lại với audio nhúng
  (video copy bit-for-bit: MP4 540 frame, OGV 502 frame stored, không đổi;
  OGV Vorbis 160k −21,12 LUFS / −4,52 dBTP; MP4 AAC 192k −21,18 LUFS /
  −4,67 dBTP — đo lại từ byte đã encode, lệch ≤0,06 LUFS so với mix nguồn).
  Các cảnh CP34 (CIN_001/002/004/006) chỉ được verify lại, không mux lại
  (LUFS khớp đúng bản ghi CP34).
- `RUNTIME_PACK_GOI31_v1.json` nay có 6 cảnh (thêm CIN_003); manifest
  audio runtime 611 → 612 file (mix 14 → 15); manifest cinematics cập nhật
  checkpoint 37; export manifest CIN_003 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Tool mở rộng theo đúng tiền lệ CP34: `build_runtime_pack_goi31.py` (thêm
  CIN_003 + sha manifest mix, checkpoint note riêng CP37 cho cảnh này),
  `build_runtime_delivery.py` (mục 3k: copy mix runtime; nhãn checkpoint
  hai manifest), `validate_media_deliveries.py` (`check_cin003_mix()` mới +
  tổng audio 611 → 612), `verify_runtime_delivery.py` (nhãn checkpoint 37).

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_37_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin003_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; shortlist 12 ô mix, 44 dòng seam, 6 playlist / 145 mục,
  VO 21 + 1 alternate tách riêng).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_37_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **612** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 15 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit
  nội dung `eea3c46`): **1221 paths, 0 violations**.
- Commit nội dung: `eea3c46` (16 file: 1 tool mix mới + 4 tool mở rộng +
  2 file mix nguồn + 1 file mix runtime + 2 file video mux lại + 3 manifest
  runtime + 1 export manifest + 2 JSON kiểm chứng). File WAV/OGV commit
  dưới dạng LFS pointer qua mirror `.git/info/attributes` local-only
  (như các checkpoint trước).

## 3. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho mix này và toàn bộ shortlist;
  mọi số LUFS/TP là đo từ byte, không phải PASS nghe tai. Mix vẫn
  DRAFT_MIX_NOT_FINAL; stem assignment PROPOSED; vị trí stinger PROPOSED
  chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; clip vẫn là Ken Burns trên
  still storyboard, không phải final pose animation.
- Gói 31 item 5 (`.gitattributes`) vẫn chờ merge commit của chủ dự án từ
  integration `6f2b465` — không đổi tại checkpoint này.
- Mô tả PR #119 vẫn ở checkpoint 01–36; cập nhật lên CP37 cần thẻ duyệt
  của chủ dự án qua luồng chính (không tự ghi qua connector).
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo theo cùng công thức (CIN_005 là ứng viên gần nhất: take
VO CP17 đã có, cửa sổ 12,5–17,5 s, overrun +0,160 s giữ nguyên theo quyết
định chủ dự án; stem assignment cần đề xuất riêng vì setting Thanh Lạc
không có cue composed đặt tên theo nó) — hoặc M8 QA khi integration di
chuyển / PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
