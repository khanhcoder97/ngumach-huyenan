# MEDIA-02 CHECKPOINT 41 — Mix nháp CIN_009 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `3b9fa57`, checkpoint 40. Issue #116 đầu lượt: vẫn 13
comment, không có chỉ đạo mới của Codex/chủ dự án sau ACK Gói 31; integration
không đổi ở `6f2b465`; PR #119 vẫn OPEN/HOLD, head `3b9fa57`, 73 commit / 1243 file,
mô tả đã ở checkpoint 01–40 sau lần cập nhật 06:10 JST.)

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_009 ("Tiếng rừng được đáp", 18 s) — mix cảnh thứ sáu sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1
(checkpoint 38), CIN_007 v1 (checkpoint 39) và CIN_008 v1 (checkpoint 40),
cùng công thức P0 v3 — và nhúng vào runtime OGV + review MP4 của cảnh. Cả 10
cảnh có mix nhúng nay là P0 (CIN_001/002/004) + CIN_006 + CIN_003 + CIN_005 +
CIN_007 + CIN_008 + CIN_009.

- `Tools/MediaProduction/Muse/build_cin009_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_009; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/lam_trieu` + ambience `AMBIENCE/waterfall` (nhạc/nước rừng —
  S01: dòng suối giữa rễ cây phủ rêu, đom đóm, DETAIL_LOCKED; S02: ba người
  dân mang giỏ/rìu trên đường mòn trong rừng, WIDE_STATIC; S03: thác nước
  và dòng suối bên ngôi đền, tre và đường đất nhìn từ trên xuống,
  TOPDOWN_MATCH; theo đúng keyframe CIN_009 S01/S02/S03; `lam_trieu` là
  dạng G-major với sáo trang trí trong bộ sáng tác ("Lâm Triều" — triều
  rừng), sáo mang "tiếng" rừng đáp lại theo đúng tên cảnh; `waterfall` là
  nền nước cho dòng suối chạy xuyên cả ba shot) + stinger `SFX/CINEMA/reveal`
  tại 6,0 s (đầu S02, PROPOSED chờ picture lock, theo mẫu
  CIN_004/CIN_006/CIN_007) + VO take CP17
  `VO_CIN_009_S03_LYAN_draft_v1.wav` tại 12,5 s. Tất cả stem đều
  composed (CP26/CP30), không còn stem ported nào trong mix.
- Điểm khác CIN_005/CIN_006 (nói thẳng): take VO CIN_009 KHỚP cửa sổ —
  4,080 s, chạy 12,5–16,580 s, kết thúc 0,920 s TRƯỚC cuối cửa sổ 17,5 s
  và 1,420 s trước cuối cảnh 18,00 s. Không overrun, không tail trim.
  Cửa sổ, take và timing không bị sửa để che giấu gì.
- Bằng chứng ducking đo theo cửa sổ VO ĐẦY ĐỦ (phương pháp CP39 giữ nguyên
  để các mix CIN_003/CIN_005/CIN_007/CIN_008/CIN_009 so sánh được với nhau):
  `lam_trieu` −9,13 dB trong cửa sổ, 0,0 dB ngoài cửa sổ.
- `Art_Source/Audio/Muse/MIX/CIN009_DRAFT_V1/CIN_009_mix_draft_v1.wav` +
  `CIN009_MIX_V1_manifest_v1.json`: mix 18,000 s, −17,84 LUFS / −2,91 dBTP,
  LRA 12,60 LU, peak trim 0,00 dB; ducking nhạc −9,13 dB trong cửa sổ VO,
  0,0 dB ngoài cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 =
  0,75. Ba stem đo lại từ byte thật khớp đúng bảng pack (lam_trieu −21,93;
  waterfall −29,53; reveal −24,96 LUFS). Mix nóng hơn mix CIN_008
  (−24,58 LUFS) vì chính take CP17 nóng hơn (−17,23 LUFS theo checkpoint
  17, so với −23,10 LUFS của CIN_008); VO giữ unity theo công thức, không
  đổi gain — ghi rõ, không chuẩn hóa lén (cùng lý do như CIN_007).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin009_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_009 mux lại với audio nhúng (video copy bit-for-bit:
  MP4 540 frame, OGV 503 frame stored, không đổi; OGV Vorbis 160k −17,72
  LUFS / −3,03 dBTP; MP4 AAC 192k −17,76 LUFS / −3,22 dBTP — đo lại từ byte
  đã encode, lệch ≤0,12 LUFS so với mix nguồn). Các cảnh CP34/CP37/CP38/
  CP39/CP40 (CIN_001/002/004/006/003/005/007/008) chỉ được verify lại,
  không mux lại (LUFS khớp đúng bản ghi CP34/CP37/CP38/CP39/CP40).
- `RUNTIME_PACK_GOI31_v1.json` nay có 10 cảnh (thêm CIN_009); manifest
  audio runtime 615 → 616 file (mix 18 → 19); manifest cinematics cập nhật
  checkpoint 41; export manifest CIN_009 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Tool mở rộng theo đúng tiền lệ CP40: `build_runtime_pack_goi31.py` (thêm
  CIN_009 + sha manifest mix, checkpoint note riêng CP41 cho cảnh này),
  `build_runtime_delivery.py` (mục 3k5: copy mix runtime; nhãn checkpoint
  hai manifest), `validate_media_deliveries.py` (`check_cin009_mix()` mới +
  tổng audio 615 → 616), `verify_runtime_delivery.py` (nhãn checkpoint 41).

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_41_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin009_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; shortlist 12 ô mix, 44 dòng seam, 6 playlist / 145 mục,
  VO 21 + 1 alternate tách riêng).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_41_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **616** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 19 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit
  nội dung `4a39bc4`): **1249 paths, 0 violations**.
- Commit nội dung: `4a39bc4` (16 file: 1 tool mix mới + 4 tool mở rộng +
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
- Build mix KHÔNG bit-deterministic giữa các lần chạy (ghi nhận ở checkpoint
  39: cùng công thức, cùng code, hai lần chạy liên tiếp cho hai SHA khác
  nhau trong khi LUFS/TP đo được giống hệt — chưa điều tra sâu vì không ảnh
  hưởng deliverable; lần này chỉ build một lần, file giao là
  `196994e8…` và mọi manifest đều ghi đúng SHA đó — kiểm chứng sha-vs-file
  PASS; build lại sau này phải re-verify manifest, không copy SHA cũ).
- Gói 31 item 5 (`.gitattributes`) vẫn chờ merge commit của chủ dự án từ
  integration `6f2b465` — không đổi tại checkpoint này.
- Mô tả PR #119 vẫn ở checkpoint 01–40; cập nhật lên CP41 cần thẻ duyệt của
  chủ dự án qua luồng chính (không tự ghi qua connector). Payload CP41 đã
  soạn (`pr119_update_cp41.json`, gộp CP41 vào bản CP01–40).
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo theo cùng công thức (ứng viên gần nhất CIN_010: take VO
CP17 đã có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo
setting của cảnh tại thời điểm làm) — hoặc M8 QA khi integration di chuyển /
PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
