# MEDIA-02 CHECKPOINT 38 — Mix nháp CIN_005 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `a1e1e72`, checkpoint 37. Issue #116 đầu lượt: vẫn 13
comment, không có chỉ đạo mới của Codex/chủ dự án sau ACK Gói 31; integration
không đổi ở `6f2b465`; PR #119 vẫn OPEN/HOLD, head `a1e1e72`, 67 commit / 1222 file.)

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_005 ("Một thành phố vẫn sống", 18 s) — mix cảnh thứ ba sau
CIN_006 v1 (checkpoint 34) và CIN_003 v1 (checkpoint 37), cùng công thức P0 v3 —
và nhúng vào runtime OGV + review MP4 của cảnh. Cả 5 cảnh có mix nhúng nay là
P0 (CIN_001/002/004) + CIN_006 + CIN_003 + CIN_005.

- `Tools/MediaProduction/Muse/build_cin005_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_005; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/thang_long` + ambience `AMBIENCE/thang_long_crowd` (nhạc/nền
  thành phố Thanh Lạc — cảnh quay ở sân đình buổi sáng muộn, tiểu thương mở
  cửa, quán trà bày bát, năm cờ môn phái trong một cơn gió, theo đúng shot
  prompt của pack S01/S02; `city_night` bị loại vì cảnh là ban ngày) +
  stinger `SFX/CINEMA/reveal` tại 6,0 s (đầu S02, PROPOSED chờ picture lock,
  theo mẫu CIN_004/CIN_006) + VO take CP17
  `VO_CIN_005_S03_LYAN_draft_v1.wav` tại 12,5 s. Tất cả stem đều composed
  (CP26/CP30), không còn stem ported nào trong mix.
- Điểm khác CIN_003 (nói thẳng): take VO CIN_005 VƯỢT cửa sổ 0,160 s — 5,160 s,
  chạy 12,5–17,660 s, qua cuối cửa sổ 17,5 s là 0,160 s. Overrun được GIỮ
  NGUYÊN, không cắt, không giấu, theo quyết định của chủ dự án (Gói 30 D1:
  3 overrun campaign — CIN_005_S03 +0,160 s, CIN_018_S03 +0,280 s,
  CIN_006_S03 +0,520 s — giữ nguyên để Codex quyết ở PR review). Take kết
  thúc 0,340 s trước cuối cảnh 18,00 s nên không cắt đuôi ở mép cảnh
  (tail trim 0,0 s). Cửa sổ, take và timing không bị sửa để che giấu gì.
- `Art_Source/Audio/Muse/MIX/CIN005_DRAFT_V1/CIN_005_mix_draft_v1.wav` +
  `CIN005_MIX_V1_manifest_v1.json`: mix 18,000 s, −21,03 LUFS / −6,11 dBTP,
  peak trim 0,00 dB; ducking nhạc −7,89 dB trong cửa sổ VO, 0,0 dB ngoài
  cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 = 0,678. Ba stem đo
  lại từ byte thật khớp đúng bảng pack (thang_long −21,96;
  thang_long_crowd −30,59; reveal −24,96 LUFS).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin005_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_005 mux lại với audio nhúng (video copy bit-for-bit:
  MP4 540 frame, OGV 371 frame stored, không đổi; OGV Vorbis 160k −20,99
  LUFS / −6,17 dBTP; MP4 AAC 192k −21,05 LUFS / −6,16 dBTP — đo lại từ byte
  đã encode, lệch ≤0,06 LUFS so với mix nguồn). Các cảnh CP34/CP37
  (CIN_001/002/004/006/003) chỉ được verify lại, không mux lại (LUFS khớp
  đúng bản ghi CP34/CP37).
- `RUNTIME_PACK_GOI31_v1.json` nay có 7 cảnh (thêm CIN_005); manifest
  audio runtime 612 → 613 file (mix 15 → 16); manifest cinematics cập nhật
  checkpoint 38; export manifest CIN_005 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Tool mở rộng theo đúng tiền lệ CP37: `build_runtime_pack_goi31.py` (thêm
  CIN_005 + sha manifest mix, checkpoint note riêng CP38 cho cảnh này),
  `build_runtime_delivery.py` (mục 3k2: copy mix runtime; nhãn checkpoint
  hai manifest), `validate_media_deliveries.py` (`check_cin005_mix()` mới +
  tổng audio 612 → 613), `verify_runtime_delivery.py` (nhãn checkpoint 38).

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_38_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin005_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; shortlist 12 ô mix, 44 dòng seam, 6 playlist / 145 mục,
  VO 21 + 1 alternate tách riêng).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_38_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **613** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 16 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit
  nội dung `b46420a`): **1228 paths, 0 violations**.
- Commit nội dung: `b46420a` (16 file: 1 tool mix mới + 4 tool mở rộng +
  2 file mix nguồn + 1 file mix runtime + 2 file video mux lại + 3 manifest
  runtime + 1 export manifest + 2 JSON kiểm chứng). File WAV/OGV/MP4 commit
  dưới dạng LFS pointer qua mirror `.git/info/attributes` local-only
  (như các checkpoint trước; mix runtime trùng SHA với mix nguồn nên LFS
  chỉ thêm 3 object).

## 3. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho mix này và toàn bộ shortlist;
  mọi số LUFS/TP là đo từ byte, không phải PASS nghe tai. Mix vẫn
  DRAFT_MIX_NOT_FINAL; stem assignment PROPOSED; vị trí stinger PROPOSED
  chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; clip vẫn là Ken Burns trên
  still storyboard, không phải final pose animation. Defect đã biết của
  CIN_005 (S02 lệch palette mái so với S01) không đổi ở checkpoint này.
- Gói 31 item 5 (`.gitattributes`) vẫn chờ merge commit của chủ dự án từ
  integration `6f2b465` — không đổi tại checkpoint này.
- Mô tả PR #119 vẫn ở checkpoint 01–36; cập nhật lên CP37 + CP38 cần thẻ
  duyệt của chủ dự án qua luồng chính (không tự ghi qua connector).
  Payload CP37 (`pr119_update_cp37.json`) vẫn đang chờ duyệt.
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo theo cùng công thức (ứng viên gần nhất CIN_007: take VO
CP17 đã có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo
setting của cảnh tại thời điểm làm) — hoặc M8 QA khi integration di chuyển /
PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
