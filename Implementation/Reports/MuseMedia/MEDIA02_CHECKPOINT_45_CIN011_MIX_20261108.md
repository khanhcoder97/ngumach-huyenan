# MEDIA-02 CHECKPOINT 45 — Mix nháp CIN_011 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `aaba7c4`, checkpoint 44. Đầu lượt: issue #116 vẫn 16 comment,
mới nhất 6714410531 (ACK CP42) — KHÔNG có chỉ đạo mới sau comment Codex 6713518554
(WO32); integration không đổi ở `6f2b465`; PR #119 OPEN/HOLD, head `aaba7c4`,
mô tả ở CP01–42 — payload cập nhật lên CP01–44 + ACK CP43/CP44 đã soạn từ lượt
trước, vẫn chờ chủ dự án duyệt, KHÔNG đăng trong lượt này; ACK CP45 gộp vào
payload đó khi chủ dự án duyệt.)

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_011 ("Chữ khắc bị sửa", 18 s) — mix cảnh thứ tám sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1
(checkpoint 38), CIN_007 v1 (checkpoint 39), CIN_008 v1 (checkpoint 40),
CIN_009 v1 (checkpoint 41) và CIN_010 v1 (checkpoint 42), cùng công thức P0 v3 —
và nhúng vào runtime OGV + review MP4 của cảnh. Cả 12 cảnh có mix nhúng nay là P0
(CIN_001/002/004) + CIN_006 + CIN_003 + CIN_005 + CIN_007 + CIN_008 +
CIN_009 + CIN_010 + CIN_011 (prologue CIN_000 tính riêng).

- `Tools/MediaProduction/Muse/build_cin011_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_011; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/quiet_discovery` + ambience `AMBIENCE/wind_canopy` (cặp cue lặng
  của bộ sáng tác — S01: bàn làm việc với các tấm khắc (motif bàn tay/vạch đếm)
  và dụng cụ khắc (búa, đục, cọ), DETAIL_LOCKED; S02: hai người đàn ông trong
  lán tre mở, người trẻ đưa bát nhỏ cho người lớn tuổi có râu, đèn lồng/giỏ/
  chum xung quanh, MEMORY_MEDIUM; S03: Hạ Mặc cúi trên tấm khắc cảnh núi-sóng-
  mây, tay cầm cọ, DETAIL_LOCKED; theo đúng keyframe CIN_011 S01/S02/S03;
  `quiet_discovery` là khoảng lặng khám phá của bộ sáng tác ("Khoảng lặng khám
  phá": mảnh sáo solo, chuông đơn, khoảng gần-im lặng dài, giọt nước, 60 BPM)
  — cái lặng thưa của xưởng khắc và của một suy ngẫm đạo đức ("Nét sau không
  xóa được điều tốt trước đó"); `wind_canopy` là nền gió qua tán cây (gusted
  band noise + lá xào xạc) cho lán tre mở và cây xanh sau S02) + stinger
  `SFX/CINEMA/reveal` tại 6,0 s (đầu S02, PROPOSED chờ picture lock, theo mẫu
  CIN_004/CIN_006/CIN_007) + VO take CP17 `VO_CIN_011_S03_HAMAC_draft_v1.wav`
  tại 12,2 s. Tất cả stem đều composed (CP26/CP30), không còn stem ported nào
  trong mix.
- Điểm khác CIN_005/CIN_006 (nói thẳng): take VO CIN_011 KHỚP cửa sổ — nhưng
  chỉ vừa đủ: take 5,592 s, chạy 12,2–17,792 s, kết thúc 0,008 s TRƯỚC cuối
  cửa sổ 17,8 s và 0,208 s trước cuối cảnh 18,00 s. Không overrun, không tail
  trim. Cửa sổ (nới 12,2–17,8 s cho tốc độ đọc: 87 ký tự ở 15,54 ký tự/giây),
  take và timing không bị sửa để che giấu gì.
- Bằng chứng ducking đo theo cửa sổ VO ĐẦY ĐỦ (phương pháp CP39 giữ nguyên
  để các mix CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011 so sánh
  được với nhau): `quiet_discovery` −10,79 dB trong cửa sổ, 0,0 dB ngoài cửa sổ.
- `Art_Source/Audio/Muse/MIX/CIN011_DRAFT_V1/CIN_011_mix_draft_v1.wav` +
  `CIN011_MIX_V1_manifest_v1.json`: mix 18,000 s, −20,34 LUFS / −3,30 dBTP,
  LRA 10,90 LU, peak trim 0,00 dB; ducking nhạc −10,79 dB trong cửa sổ VO,
  0,0 dB ngoài cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 =
  0,765. Ba stem đo lại từ byte thật khớp đúng bảng pack (quiet_discovery
  −21,72; wind_canopy −29,70; reveal −24,96 LUFS). Mix yên hơn mix CIN_009
  (−17,84 LUFS) vì take CP17 yên (−21,50 LUFS theo checkpoint 17, đo lại từ
  byte thật lượt này khớp đúng, so với −22,01 LUFS của CIN_010); VO giữ unity
  theo công thức, không đổi gain — ghi rõ, không chuẩn hóa lén (cùng lý do
  như CIN_007/CIN_009/CIN_010).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin011_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_011 mux lại với audio nhúng (video copy bit-for-bit:
  MP4 540 frame, OGV 486 frame stored, không đổi; OGV Vorbis 160k −20,38
  LUFS / −3,44 dBTP; MP4 AAC 192k −20,37 LUFS / −3,34 dBTP — đo lại từ byte
  đã encode, lệch ≤0,04 LUFS so với mix nguồn). Các cảnh CP34/CP37/CP38/
  CP39/CP40/CP41/CP42 (CIN_001/002/004/006/003/005/007/008/009/010) chỉ được
  verify lại, không mux lại (LUFS khớp đúng bản ghi CP34/CP37/CP38/CP39/CP40/
  CP41/CP42).
- `RUNTIME_PACK_GOI31_v1.json` nay có 12 cảnh (thêm CIN_011); manifest
  audio runtime 617 → 618 file (mix 20 → 21); manifest cinematics cập nhật
  checkpoint 45; export manifest CIN_011 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Playback metadata + bảng phát âm CHẠY LẠI cho mix nhúng mới (theo đúng ghi
  chú CP44: khi một cảnh được nhúng mix, chạy lại builder để fallback cập
  nhật): `PLAYBACK_METADATA_v1.json` nay 12 embedded / 9 silent
  (CIN_012–020), builder PASS 0 mismatches; `PRONUNCIATION_TABLE_v1.json`
  nay 18 playback cue rows (12 embedded + 6 P0 v1/v2 alternates), 19 seam
  rows (1 flagged, không đổi), 21 fallback rows, 130 file kiểm chứng (tăng
  từ 125); cue CIN_011: head/tail 0,0 s, slack +0,008 s, ducking −10,79 dB;
  fallback CIN_011: EMBEDDED_SOUNDTRACK → mix WAV → stems+VO → VO+SRT →
  SRT-only. Hai builder được mở rộng theo đúng tiền lệ CP42/CP44
  (`build_playback_metadata_v1.py`: nhãn checkpoint 45;
  `build_pronunciation_table_v1.py`: map `cin011` + `CIN_011` ở cả 4 bảng
  tra, chuỗi "CIN_011-020" → "CIN_012-020", nhãn checkpoint 45).
- Tool mở rộng theo đúng tiền lệ CP42: `build_cin011_mix_v1.py` (mới),
  `build_runtime_pack_goi31.py` (thêm CIN_011 + sha manifest mix, checkpoint
  note riêng CP45 cho cảnh này), `build_runtime_delivery.py` (mục 3k7: copy
  mix runtime; nhãn checkpoint hai manifest; tổng audio 617 → 618),
  `validate_media_deliveries.py` (`check_cin011_mix()` mới + tổng audio
  617 → 618 + nhãn checkpoint + mục giới hạn CIN_011),
  `verify_runtime_delivery.py` (nhãn checkpoint 45).

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_45_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin011_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; playback metadata 12 embedded / 9 silent; pronunciation
  fallback files 130).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_45_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **618** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 21 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit
  nội dung `2209047`): **1272 paths, 1 violation** — vi phạm duy nhất là
  `.gitattributes`, file policy gốc của Codex do chủ dự án merge qua PR #127
  (commit `9f264ef`), KHÔNG phải nội dung CP45. Audit riêng nội dung CP45
  (base `aaba7c4`, head `2209047`): **18 paths, 0 violations**.
- Commit nội dung: `2209047` (18 file: 1 tool mix mới + 6 tool mở rộng +
  2 file mix nguồn + 1 file mix runtime + 2 file video mux lại + 4 manifest
  runtime + 1 export manifest + 1 bảng phát âm). File WAV/OGV/MP4 commit
  dưới dạng LFS pointer (quy tắc `.gitattributes` đã merge qua PR #127;
  mix runtime trùng SHA với mix nguồn nên LFS chỉ thêm 3 object).

## 3. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho mix này và toàn bộ shortlist;
  mọi số LUFS/TP là đo từ byte, không phải PASS nghe tai. Mix vẫn
  DRAFT_MIX_NOT_FINAL; stem assignment PROPOSED; vị trí stinger PROPOSED
  chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; clip vẫn là Ken Burns trên
  still storyboard, không phải final pose animation. NPC_HA_MAC trên màn
  hình chưa có character lock đã duyệt nên mặt/trang phục vẫn là placeholder
  storyboard (staging cinematic-only theo DEC-MEDIA-P0 Q4, không nhân đôi
  persistent ID).
- Build mix KHÔNG bit-deterministic giữa các lần chạy (ghi nhận ở checkpoint
  39: cùng công thức, cùng code, hai lần chạy liên tiếp cho hai SHA khác
  nhau trong khi LUFS/TP đo được giống hệt — chưa điều tra sâu vì không ảnh
  hưởng deliverable; lần này chỉ build một lần, file giao là
  `aa89602b…` và mọi manifest đều ghi đúng SHA đó — kiểm chứng sha-vs-file
  PASS; build lại sau này phải re-verify manifest, không copy SHA cũ).
- Sự cố môi trường lượt này (đã xử lý, không ảnh hưởng deliverable): lần chạy
  đầu `build_pronunciation_table_v1.py` chết ở `MIX_MANIFEST_BY_SCENE`
  (KeyError `CIN_011`) vì map tra cứu mix manifest chưa có mục CIN_011 —
  builder này (CP44) liệt kê cứng từng cảnh có mix nhúng, không suy ra từ
  playback metadata. Đã bổ sung `cin011`/`CIN_011` vào cả 4 map
  (`MIX_MANIFESTS`, danh sách tuple mix, `EMBEDDED_RUNTIME_MIX`,
  `MIX_MANIFEST_BY_SCENE`) và chạy lại: PASS 0 mismatches. Ghi chú cho các
  lượt sau: khi thêm mix cảnh mới, cập nhật cả 4 map này cùng lúc với
  `build_playback_metadata_v1.py` (suy ra động từ pack) — nếu không builder
  phát âm sẽ chết KeyError trước khi ghi file.
- Mô tả PR #119 vẫn ở checkpoint 01–42; cập nhật lên CP01–45 + ACK
  CP43/CP44/CP45 cần thẻ duyệt của chủ dự án qua luồng chính (không tự ghi
  qua connector). Payload CP45 đã soạn (gộp CP43 + CP44 + CP45 vào bản
  CP01–42).
- PR #119 mergeable FALSE — xung đột duy nhất `.gitattributes` (media thêm
  2 dòng LF so với integration); chờ Codex/chủ dự án giải quyết, Muse không
  tự sửa policy.
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo cùng công thức (ứng viên gần nhất CIN_012: take VO CP17 đã
có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo setting của
cảnh tại thời điểm làm — khi thêm mix, nhớ cập nhật cả 4 map trong
`build_pronunciation_table_v1.py`), hoặc cập nhật mô tả PR #119 lên CP01–45
+ ACK CP43/CP44/CP45 (khi chủ dự án duyệt), hoặc M8 QA khi integration di
chuyển / PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
