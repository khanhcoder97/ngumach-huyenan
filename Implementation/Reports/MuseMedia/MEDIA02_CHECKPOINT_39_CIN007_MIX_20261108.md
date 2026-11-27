# MEDIA-02 CHECKPOINT 39 — Mix nháp CIN_007 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `3973654`, checkpoint 38. Issue #116 đầu lượt: vẫn 13
comment, không có chỉ đạo mới của Codex/chủ dự án sau ACK Gói 31; integration
không đổi ở `6f2b465`; PR #119 vẫn OPEN/HOLD, head `3973654`, 69 commit / 1229 file.)

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_007 ("Tên trong vỏ cây", 18 s) — mix cảnh thứ tư sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37) và CIN_005 v1
(checkpoint 38), cùng công thức P0 v3 — và nhúng vào runtime OGV + review
MP4 của cảnh. Cả 6 cảnh có mix nhúng nay là P0 (CIN_001/002/004) + CIN_006
+ CIN_003 + CIN_005 + CIN_007.

- `Tools/MediaProduction/Muse/build_cin007_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_007; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/quiet_discovery` + ambience `AMBIENCE/wind_canopy` (nhạc/nền
  rừng — cảnh quay trong rừng mưa xanh cổ thụ, nước nhỏ giọt chảy qua vỏ
  cây, bốn rãnh khắc sáng dần như nét chữ, bóng lá lướt qua, theo đúng shot
  prompt của pack S01/S02; `ben_mua`/`river_shore` bị loại vì cảnh không ở
  Bến Mưa) + stinger `SFX/CINEMA/reveal` tại 6,0 s (đầu S02, PROPOSED chờ
  picture lock, theo mẫu CIN_004/CIN_006) + VO take CP17
  `VO_CIN_007_S03_LYAN_draft_v1.wav` tại 12,5 s. Tất cả stem đều composed
  (CP26/CP30), không còn stem ported nào trong mix.
- Điểm khác CIN_005/CIN_006 (nói thẳng): take VO CIN_007 KHỚP cửa sổ —
  3,912 s, chạy 12,5–16,412 s, kết thúc 1,088 s TRƯỚC cuối cửa sổ 17,5 s
  và 1,588 s trước cuối cảnh 18,00 s. Không overrun, không tail trim.
  Cửa sổ, take và timing không bị sửa để che giấu gì.
- Bằng chứng ducking đo theo cửa sổ VO ĐẦY ĐỦ (thay vì 2 s đầu như các mix
  trước): `quiet_discovery` thưa theo thiết kế (sáo solo xen kẽ khoảng lặng
  dài) nên 2 s đầu của cửa sổ chỉ đo −91 dB mean — gần như im lặng — và
  lát cắt 2 s cho ra 0,0 dB dù compressor vẫn chạy. Đo đủ cửa sổ cho
  −9,43 dB trong cửa sổ, 0,0 dB ngoài cửa sổ. Lý do và số đo ghi rõ trong
  tool và manifest, không giấu.
- `Art_Source/Audio/Muse/MIX/CIN007_DRAFT_V1/CIN_007_mix_draft_v1.wav` +
  `CIN007_MIX_V1_manifest_v1.json`: mix 18,000 s, −18,05 LUFS / −1,43 dBTP,
  peak trim 0,00 dB; ducking nhạc −9,43 dB trong cửa sổ VO, 0,0 dB ngoài
  cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 = 0,765. Ba stem đo
  lại từ byte thật khớp đúng bảng pack (quiet_discovery −21,72;
  wind_canopy −29,70; reveal −24,96 LUFS). Mix to hơn các mix cảnh trước
  (−21,03 CIN_005, −21,16 CIN_003) vì chính take CP17 to hơn (mean
  −17,9 dB, max −1,4 dB so với −19,9/−6,3 dB của CIN_005); VO giữ unity
  theo công thức, không đổi gain — ghi rõ, không chuẩn hóa lén.
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin007_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_007 mux lại với audio nhúng (video copy bit-for-bit:
  MP4 540 frame, OGV 503 frame stored, không đổi; OGV Vorbis 160k −17,98
  LUFS / −1,54 dBTP; MP4 AAC 192k −18,02 LUFS / −1,46 dBTP — đo lại từ byte
  đã encode, lệch ≤0,07 LUFS so với mix nguồn). Các cảnh CP34/CP37/CP38
  (CIN_001/002/004/006/003/005) chỉ được verify lại, không mux lại (LUFS
  khớp đúng bản ghi CP34/CP37/CP38).
- `RUNTIME_PACK_GOI31_v1.json` nay có 8 cảnh (thêm CIN_007); manifest
  audio runtime 613 → 614 file (mix 16 → 17); manifest cinematics cập nhật
  checkpoint 39; export manifest CIN_007 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Tool mở rộng theo đúng tiền lệ CP38: `build_runtime_pack_goi31.py` (thêm
  CIN_007 + sha manifest mix, checkpoint note riêng CP39 cho cảnh này),
  `build_runtime_delivery.py` (mục 3k3: copy mix runtime; nhãn checkpoint
  hai manifest), `validate_media_deliveries.py` (`check_cin007_mix()` mới +
  tổng audio 613 → 614), `verify_runtime_delivery.py` (nhãn checkpoint 39).

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_39_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin007_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; shortlist 12 ô mix, 44 dòng seam, 6 playlist / 145 mục,
  VO 21 + 1 alternate tách riêng).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_39_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **614** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 17 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit
  nội dung `36610dc`): **1235 paths, 0 violations**.
- Commit nội dung: `36610dc` (16 file: 1 tool mix mới + 4 tool mở rộng +
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
  still storyboard, không phải final pose animation.
- Build mix KHÔNG bit-deterministic giữa các lần chạy: cùng công thức, cùng
  code, hai lần chạy liên tiếp cho hai SHA khác nhau (`ee9f4c0a…` /
  `313bbad8…`) trong khi LUFS/TP đo được giống hệt (−18,05/−1,43). File
  giao trong checkpoint này là `ee9f4c0a…` và mọi manifest (nguồn, runtime,
  pack) đều ghi đúng SHA đó — kiểm chứng sha-vs-file PASS. Nguyên nhân
  nhiều khả năng là thread timing trong filter ffmpeg (sidechain/amix);
  chưa điều tra sâu vì không ảnh hưởng deliverable, nhưng lần build lại
  sau này có thể cho SHA khác — phải re-verify manifest sau mỗi lần build
  lại, không copy SHA cũ.
- Gói 31 item 5 (`.gitattributes`) vẫn chờ merge commit của chủ dự án từ
  integration `6f2b465` — không đổi tại checkpoint này.
- Mô tả PR #119 vẫn ở checkpoint 01–36; cập nhật lên CP37 + CP38 + CP39 cần
  thẻ duyệt của chủ dự án qua luồng chính (không tự ghi qua connector).
  Payload CP37 (`pr119_update_cp37.json`) và CP38 (`pr119_update_cp38.json`)
  vẫn đang chờ duyệt; payload CP39 chuẩn bị gộp cả ba.
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo theo cùng công thức (ứng viên gần nhất CIN_008: take VO
CP17 đã có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo
setting của cảnh tại thời điểm làm) — hoặc M8 QA khi integration di chuyển /
PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
