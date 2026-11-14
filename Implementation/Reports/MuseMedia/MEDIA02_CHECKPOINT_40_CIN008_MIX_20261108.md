# MEDIA-02 CHECKPOINT 40 — Mix nháp CIN_008 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `f3884c7`, checkpoint 39. Issue #116 đầu lượt: vẫn 13
comment, không có chỉ đạo mới của Codex/chủ dự án sau ACK Gói 31; integration
không đổi ở `6f2b465`; PR #119 vẫn OPEN/HOLD, head `f3884c7`, 71 commit / 1236 file.)

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_008 ("Bàn tay đã ký", 18 s) — mix cảnh thứ năm sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1
(checkpoint 38) và CIN_007 v1 (checkpoint 39), cùng công thức P0 v3 — và
nhúng vào runtime OGV + review MP4 của cảnh. Cả 9 cảnh có mix nhúng nay là
P0 (CIN_001/002/004) + CIN_006 + CIN_003 + CIN_005 + CIN_007 + CIN_008.

- `Tools/MediaProduction/Muse/build_cin008_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_008; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/tran_son` + ambience `AMBIENCE/river_shore` (nhạc/nền cổng
  và bờ nước — S01: bàn tay cầm bút ký lên tờ lệnh trong tông chàm; S02:
  cổng đôi gỗ cao khép gần kín, khe sáng đèn lồng, người áo dài chờ với
  bình nước đất; S03: Tạ Vân Khanh thú nhận bên ao rừng tre, theo đúng shot
  prompt của pack S01/S02/S03; `tran_son` là dạng bell-led gate form trong
  bộ sáng tác — khớp hình ảnh cổng trung tâm của cảnh; `river_shore` là nền
  bờ nước cho ao tre) + stinger `SFX/CINEMA/reveal` tại 6,0 s (đầu S02,
  PROPOSED chờ picture lock, theo mẫu CIN_004/CIN_006/CIN_007) + VO take
  CP17 `VO_CIN_008_S03_TAVANKHANH_draft_v1.wav` tại 12,5 s. Tất cả stem đều
  composed (CP26/CP30), không còn stem ported nào trong mix.
- Điểm khác CIN_005/CIN_006 (nói thẳng): take VO CIN_008 KHỚP cửa sổ —
  3,552 s, chạy 12,5–16,052 s, kết thúc 1,448 s TRƯỚC cuối cửa sổ 17,5 s
  và 1,948 s trước cuối cảnh 18,00 s. Không overrun, không tail trim.
  Cửa sổ, take và timing không bị sửa để che giấu gì.
- Bằng chứng ducking đo theo cửa sổ VO ĐẦY ĐỦ (phương pháp CP39 giữ nguyên
  để các mix CIN_003/CIN_005/CIN_007/CIN_008 so sánh được với nhau):
  `tran_son` −7,22 dB trong cửa sổ, 0,0 dB ngoài cửa sổ.
- `Art_Source/Audio/Muse/MIX/CIN008_DRAFT_V1/CIN_008_mix_draft_v1.wav` +
  `CIN008_MIX_V1_manifest_v1.json`: mix 18,000 s, −24,58 LUFS / −1,61 dBTP,
  peak trim 0,00 dB; ducking nhạc −7,22 dB trong cửa sổ VO, 0,0 dB ngoài
  cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 = 0,58. Ba stem đo
  lại từ byte thật khớp đúng bảng pack (tran_son −21,95; river_shore
  −29,69; reveal −24,96 LUFS). Mix yên hơn mix CIN_007 (−18,05 LUFS) vì
  chính take CP17 yên hơn (−23,10 LUFS theo checkpoint 17, so với
  −17,9 dB mean của CIN_007); VO giữ unity theo công thức, không đổi
  gain — ghi rõ, không chuẩn hóa lén.
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin008_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_008 mux lại với audio nhúng (video copy bit-for-bit:
  MP4 540 frame, OGV 509 frame stored, không đổi; OGV Vorbis 160k −24,61
  LUFS / −1,85 dBTP; MP4 AAC 192k −24,58 LUFS / −1,53 dBTP — đo lại từ byte
  đã encode, lệch ≤0,03 LUFS so với mix nguồn). Các cảnh CP34/CP37/CP38/
  CP39 (CIN_001/002/004/006/003/005/007) chỉ được verify lại, không mux lại
  (LUFS khớp đúng bản ghi CP34/CP37/CP38/CP39).
- `RUNTIME_PACK_GOI31_v1.json` nay có 9 cảnh (thêm CIN_008); manifest
  audio runtime 614 → 615 file (mix 17 → 18); manifest cinematics cập nhật
  checkpoint 40; export manifest CIN_008 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Tool mở rộng theo đúng tiền lệ CP39: `build_runtime_pack_goi31.py` (thêm
  CIN_008 + sha manifest mix, checkpoint note riêng CP40 cho cảnh này),
  `build_runtime_delivery.py` (mục 3k4: copy mix runtime; nhãn checkpoint
  hai manifest), `validate_media_deliveries.py` (`check_cin008_mix()` mới +
  tổng audio 614 → 615), `verify_runtime_delivery.py` (nhãn checkpoint 40).

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_40_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin008_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; shortlist 12 ô mix, 44 dòng seam, 6 playlist / 145 mục,
  VO 21 + 1 alternate tách riêng).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_40_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **615** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 18 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit
  nội dung `3c79856`): **1242 paths, 0 violations**.
- Commit nội dung: `3c79856` (16 file: 1 tool mix mới + 4 tool mở rộng +
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
  `eaaaf4a1…` và mọi manifest đều ghi đúng SHA đó — kiểm chứng sha-vs-file
  PASS; build lại sau này phải re-verify manifest, không copy SHA cũ).
- Gói 31 item 5 (`.gitattributes`) vẫn chờ merge commit của chủ dự án từ
  integration `6f2b465` — không đổi tại checkpoint này.
- Mô tả PR #119 vẫn ở checkpoint 01–36; cập nhật lên CP37 + CP38 + CP39 +
  CP40 cần thẻ duyệt của chủ dự án qua luồng chính (không tự ghi qua
  connector). Payload CP37 (`pr119_update_cp37.json`), CP38
  (`pr119_update_cp38.json`) và CP39 (`pr119_update_cp39.json`, gộp
  CP37–39) vẫn đang chờ duyệt; payload CP40 chuẩn bị gộp cả bốn.
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo theo cùng công thức (ứng viên gần nhất CIN_009: take VO
CP17 đã có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo
setting của cảnh tại thời điểm làm) — hoặc M8 QA khi integration di chuyển /
PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
