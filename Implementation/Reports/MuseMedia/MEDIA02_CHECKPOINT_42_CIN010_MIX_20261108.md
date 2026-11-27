# MEDIA-02 CHECKPOINT 42 — Mix nháp CIN_010 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `9f264ef`, checkpoint 41 + merge PR #127. Issue #116 đầu lượt: vẫn 14
comment, mới nhất 6713518554 (chỉ đạo Codex 2026-11-08, PR #128 + Work Order 32) — không có chỉ
đạo mới sau đó; integration không đổi ở `6f2b465`; PR #119 vẫn OPEN/HOLD, head `9f264ef`, 79 commit /
1251 file, mô tả vẫn ở checkpoint 01–40 (payload CP41 đã soạn, chưa được bấm).)

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_010 ("Bình nước cuối xe", 18 s) — mix cảnh thứ bảy sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1
(checkpoint 38), CIN_007 v1 (checkpoint 39), CIN_008 v1 (checkpoint 40)
và CIN_009 v1 (checkpoint 41), cùng công thức P0 v3 — và nhúng vào
runtime OGV + review MP4 của cảnh. Cả 11 cảnh có mix nhúng nay là P0
(CIN_001/002/004) + CIN_006 + CIN_003 + CIN_005 + CIN_007 + CIN_008 +
CIN_009 + CIN_010 (prologue CIN_000 tính riêng).

- `Tools/MediaProduction/Muse/build_cin010_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_010; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/sa_hoa` + ambience `AMBIENCE/desert_wind` (cặp cue sa mạc
  của bộ sáng tác — S01: đoàn xe dừng dưới mái vải rách, bánh xe gỗ lớn
  và thùng nước chung gần cạn ở tiền cảnh, cồn cát vàng tro + mesa đá,
  WIDE_STATIC; S02: Sầm Chủ Quỹ rót dòng nước mỏng từ bình đất vào thùng
  chung có nắp, DETAIL_LOCKED; S03: Sầm quỳ đặt bình đất lên tấm vải bản
  đồ trải trên cát, dây lộ trình vắt ngang, MEDIUM_STATIC; theo đúng
  keyframe CIN_010 S01/S02/S03; `sa_hoa` là dạng sa mạc của bộ sáng tác
  ("Sa Hỏa — Lò và cát", A minor pentatonic, pluck khô sáng, 110 BPM) —
  cái khô nóng của tên cảnh "Bình nước cuối xe"; `desert_wind` là nền gió
  sa mạc ("Gió Sa Hỏa": dải hẹp khô hơn, gust nhanh hơn, tiếng cát) cho
  cồn cát chạy xuyên cả ba shot) + stinger `SFX/CINEMA/reveal` tại 6,0 s
  (đầu S02, PROPOSED chờ picture lock, theo mẫu CIN_004/CIN_006/CIN_007)
  + VO take CP17 `VO_CIN_010_S03_SAMCHUQUY_draft_v1.wav` tại 12,5 s. Tất
  cả stem đều composed (CP26/CP30), không còn stem ported nào trong mix.
- Điểm khác CIN_005/CIN_006 (nói thẳng): take VO CIN_010 KHỚP cửa sổ —
  2,808 s, chạy 12,5–15,308 s, kết thúc 2,192 s TRƯỚC cuối cửa sổ 17,5 s
  và 2,692 s trước cuối cảnh 18,00 s. Không overrun, không tail trim.
  Cửa sổ, take và timing không bị sửa để che giấu gì.
- Bằng chứng ducking đo theo cửa sổ VO ĐẦY ĐỦ (phương pháp CP39 giữ nguyên
  để các mix CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010 so sánh được
  với nhau): `sa_hoa` −7,94 dB trong cửa sổ, 0,0 dB ngoài cửa sổ.
- `Art_Source/Audio/Muse/MIX/CIN010_DRAFT_V1/CIN_010_mix_draft_v1.wav` +
  `CIN010_MIX_V1_manifest_v1.json`: mix 18,000 s, −24,60 LUFS / −4,86 dBTP,
  LRA 8,60 LU, peak trim 0,00 dB; ducking nhạc −7,94 dB trong cửa sổ VO,
  0,0 dB ngoài cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 =
  0,603. Ba stem đo lại từ byte thật khớp đúng bảng pack (sa_hoa −21,96;
  desert_wind −29,93; reveal −24,96 LUFS). Mix yên gần bằng mix CIN_008
  (−24,58 LUFS) vì chính take CP17 yên (−22,01 LUFS theo checkpoint 17,
  đo lại từ byte thật lượt này khớp đúng, so với −17,23 LUFS của CIN_009);
  VO giữ unity theo công thức, không đổi gain — ghi rõ, không chuẩn hóa
  lén (cùng lý do như CIN_007/CIN_009).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin010_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_010 mux lại với audio nhúng (video copy bit-for-bit:
  MP4 540 frame, OGV 376 frame stored, không đổi; OGV Vorbis 160k −24,63
  LUFS / −5,42 dBTP; MP4 AAC 192k −24,62 LUFS / −4,97 dBTP — đo lại từ byte
  đã encode, lệch ≤0,03 LUFS so với mix nguồn). Các cảnh CP34/CP37/CP38/
  CP39/CP40/CP41 (CIN_001/002/004/006/003/005/007/008/009) chỉ được verify
  lại, không mux lại (LUFS khớp đúng bản ghi CP34/CP37/CP38/CP39/CP40/
  CP41).
- `RUNTIME_PACK_GOI31_v1.json` nay có 11 cảnh (thêm CIN_010); manifest
  audio runtime 616 → 617 file (mix 19 → 20); manifest cinematics cập nhật
  checkpoint 42; export manifest CIN_010 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Tool mở rộng theo đúng tiền lệ CP41: `build_runtime_pack_goi31.py` (thêm
  CIN_010 + sha manifest mix, checkpoint note riêng CP42 cho cảnh này),
  `build_runtime_delivery.py` (mục 3k6: copy mix runtime; nhãn checkpoint
  hai manifest), `validate_media_deliveries.py` (`check_cin010_mix()` mới +
  tổng audio 616 → 617 + nhãn checkpoint + mục giới hạn CIN_009/CIN_010),
  `verify_runtime_delivery.py` (nhãn checkpoint 42).

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_42_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin010_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; shortlist 12 ô mix, 44 dòng seam, 6 playlist / 145 mục,
  VO 21 + 1 alternate tách riêng).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_42_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **617** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 20 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit
  nội dung `c4ceb3f`): **1257 paths, 1 violation** — vi phạm duy nhất là
  `.gitattributes`, file policy gốc của Codex do chủ dự án merge qua PR #127
  (commit `9f264ef`), KHÔNG phải nội dung CP42. Audit riêng nội dung CP42
  (base `9f264ef`, head `c4ceb3f`): **16 paths, 0 violations**.
- Commit nội dung: `c4ceb3f` (16 file: 1 tool mix mới + 4 tool mở rộng +
  2 file mix nguồn + 1 file mix runtime + 2 file video mux lại + 3 manifest
  runtime + 1 export manifest + 2 JSON kiểm chứng). File WAV/OGV/MP4 commit
  dưới dạng LFS pointer (quy tắc `.gitattributes` đã merge qua PR #127;
  mix runtime trùng SHA với mix nguồn nên LFS chỉ thêm 3 object).

## 3. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho mix này và toàn bộ shortlist;
  mọi số LUFS/TP là đo từ byte, không phải PASS nghe tai. Mix vẫn
  DRAFT_MIX_NOT_FINAL; stem assignment PROPOSED; vị trí stinger PROPOSED
  chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; clip vẫn là Ken Burns trên
  still storyboard, không phải final pose animation. NPC_SAM_CHU_QUY trên màn
  hình chưa có character lock đã duyệt nên mặt/trang phục vẫn là placeholder
  storyboard (staging cinematic-only theo DEC-MEDIA-P0 Q4, không nhân đôi
  persistent ID).
- Build mix KHÔNG bit-deterministic giữa các lần chạy (ghi nhận ở checkpoint
  39: cùng công thức, cùng code, hai lần chạy liên tiếp cho hai SHA khác
  nhau trong khi LUFS/TP đo được giống hệt — chưa điều tra sâu vì không ảnh
  hưởng deliverable; lần này chỉ build một lần, file giao là
  `6a3f9d21…` và mọi manifest đều ghi đúng SHA đó — kiểm chứng sha-vs-file
  PASS; build lại sau này phải re-verify manifest, không copy SHA cũ).
- Sự cố môi trường lượt này (đã xử lý, không ảnh hưởng deliverable): lần chạy
  đầu `build_runtime_pack_goi31.py` chết ở bước verify CIN_009/MP4 vì
  `/tmp` (tmpfs 512M) đầy — các thư mục tạm của checkpoint 37–41 (mỗi mix
  ~24M, mỗi lần pack 40–66M) không được dọn. Đã xóa các thư mục tạm cũ đó
  (chỉ là intermediate, deliverable đã nằm trong repo) và chạy lại với
  `TMPDIR` trên đĩa workspace; lần chạy thứ hai PASS toàn bộ, 10 cảnh cũ
  verify khớp đúng số liệu các checkpoint trước. Ghi chú cho các lượt sau:
  đặt `TMPDIR` ngoài `/tmp` khi chạy pack/delivery/validation, và dọn
  `/tmp/cin*_mix_*` + `/tmp/runtime_pack_goi31_*` sau mỗi lượt.
- Validator có một kỳ vọng cứng đã lỗi thời: `check_prologue()` còn ghi tổng
  audio 616 (checkpoint 41) nên lần chạy validation đầu báo 1 mismatch
  "PROLOGUE: runtime audio total 617 != 616" — đó là số đúng sau khi thêm
  mix CIN_010, không phải lỗi deliverable. Đã sửa kỳ vọng thành 617 trong
  validator và chạy lại: PASS 0 mismatch. (Validator cũng giữ nhãn checkpoint
  40 ở trường `checkpoint` của JSON từ CP41 — đã sửa thành checkpoint 42
  trong lượt này; các mục giới hạn CIN_009 còn thiếu từ CP41 cũng được bổ
  sung cùng lúc.)
- Mô tả PR #119 vẫn ở checkpoint 01–40; cập nhật lên CP01–42 cần thẻ duyệt của
  chủ dự án qua luồng chính (không tự ghi qua connector). Payload CP42 đã
  soạn (`pr119_update_cp42.json`, gộp CP41 + CP42 vào bản CP01–40).
- PR #119 mergeable FALSE — xung đột duy nhất `.gitattributes` (media thêm
  2 dòng LF so với integration); chờ Codex/chủ dự án giải quyết, Muse không
  tự sửa policy.
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Bảng playback metadata cho mix nhúng (mục 4 chỉ đạo Codex 2026-11-08, Work
Order 32: embeddedMix/voice/subtitle source + audio ownership để Codex
không bật đồng thời embedded soundtrack + external mix/VO) — tổng hợp
alignment mới xếp khối này trước bảng phát âm/tên riêng (mục 3) — hoặc mix
cảnh tiếp theo cùng công thức (ứng viên gần nhất CIN_011: take VO CP17 đã
có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo setting của
cảnh tại thời điểm làm), hoặc M8 QA khi integration di chuyển / PR có review
mới. Không quay sang game sprite/UI/map/VFX/Godot.
