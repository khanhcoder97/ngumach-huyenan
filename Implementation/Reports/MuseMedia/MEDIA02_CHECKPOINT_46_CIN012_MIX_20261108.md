# MEDIA-02 CHECKPOINT 46 — Mix nháp CIN_012 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `694ddb6`, checkpoint 45. Đầu lượt: issue #116 có 17 comment
sau khi ACK CP43–CP45 đăng 10:42 JST (comment 6715782450) — KHÔNG có chỉ đạo mới
sau comment Codex 6713518554 (WO32); integration không đổi ở `6f2b465`; PR #119
OPEN/HOLD, head `694ddb6`, mô tả ở CP01–45 (đăng 10:41 JST, đã xác minh
read-back); cập nhật mô tả lên CP01–46 + ACK CP46 đã soạn trong lượt này, chờ
chủ dự án duyệt, KHÔNG đăng trong lượt này.)

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_012 ("Giữ tên người sống", 18 s) — mix cảnh thứ chín sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1 (checkpoint 38),
CIN_007 v1 (checkpoint 39), CIN_008 v1 (checkpoint 40), CIN_009 v1 (checkpoint 41),
CIN_010 v1 (checkpoint 42) và CIN_011 v1 (checkpoint 45), cùng công thức P0 v3 —
và nhúng vào runtime OGV + review MP4 của cảnh. Cả 12 cảnh campaign có mix nhúng
nay là P0 (CIN_001/002/004) + CIN_006 + CIN_003 + CIN_005 + CIN_007 + CIN_008 +
CIN_009 + CIN_010 + CIN_011 + CIN_012 (prologue CIN_000 tính riêng; pack runtime
nay 13 cảnh gồm prologue).

- `Tools/MediaProduction/Muse/build_cin012_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_012; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/tran_son` + ambience `AMBIENCE/forge` (cặp cue lò rèn — S01: lò
  đá lớn ở giữa, hai người thợ ngồi trên bệ gỗ trước lò, than, giỏ tre và
  dụng cụ rèn hai bên, ánh cam ấm, WIDE_STATIC; S02: Hạ Mặc ở bàn lưu trữ,
  đặt dải giấy hẹp ngang dòng nhật ký đã khôi phục đang mở, bản sao công khai
  bên trái và hồ sơ niêm phong buộc dây bên phải, kệ cuộn phía sau,
  DETAIL_LOCKED; S03: Hạ Mặc áo lam đậm sau bàn gỗ dài, hai tờ giấy trắng,
  sảnh đèn lồng với núi và thông qua cửa sổ lớn, MEDIUM_STATIC; theo đúng
  keyframe CIN_012 S01/S02/S03; `tran_son` là dạng chuông trang nghiêm của bộ
  sáng tác ("Trấn Sơn — Người qua cửa": chuông nêu motif, sáo trầm đáp, trống
  điểm từng nhịp, 90 BPM) — sức nặng điềm tĩnh của một quyết định trong sảnh
  đèn lồng ("Có thể đưa chuyện này ra ánh sáng mà không đẩy người làm chứng
  vào lửa"); `forge` là nền lửa (gầm lửa + 180 tiếng nổ lách tách + 5 tiếng
  kim loại) cho lò đá và dụng cụ rèn của S01) + stinger `SFX/CINEMA/reveal`
  tại 6,0 s (đầu S02, PROPOSED chờ picture lock, theo mẫu
  CIN_004/CIN_006/CIN_007) + VO take CP17 `VO_CIN_012_S03_HAMAC_draft_v1.wav`
  tại 12,5 s. Tất cả stem đều composed (CP26/CP30), không còn stem ported nào
  trong mix. `sa_hoa` ("Lò và cát") đã bỏ qua: vừa dùng cho CIN_010 và nhịp
  110 BPM của nó hợp cảnh sa mạc hơn câu thoại đạo đức lặng này.
- Điểm khác CIN_011 (nói thẳng): take VO CIN_012 KHỚP cửa sổ với dư dả — take
  4,320 s, chạy 12,5–16,820 s, kết thúc 0,680 s TRƯỚC cuối cửa sổ 17,5 s và
  1,180 s trước cuối cảnh 18,00 s. Không overrun, không tail trim. Cửa sổ là
  uniform 12,5–17,5 s (71 ký tự ở 14,20 ký tự/giây), KHÔNG nới; take và timing
  không bị sửa để che giấu gì.
- Bằng chứng ducking đo theo cửa sổ VO ĐẦY ĐỦ (phương pháp CP39 giữ nguyên
  để các mix CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012
  so sánh được với nhau): `tran_son` −7,39 dB trong cửa sổ, 0,0 dB ngoài cửa sổ.
- `Art_Source/Audio/Muse/MIX/CIN012_DRAFT_V1/CIN_012_mix_draft_v1.wav` +
  `CIN012_MIX_V1_manifest_v1.json`: mix 18,000 s, −25,60 LUFS / −5,13 dBTP,
  LRA 8,50 LU, peak trim 0,00 dB; ducking nhạc −7,39 dB trong cửa sổ VO,
  0,0 dB ngoài cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 =
  0,78. Ba stem đo lại từ byte thật khớp đúng bảng pack (tran_son
  −21,95; forge −29,49; reveal −24,96 LUFS). Mix yên nhất trong các mix
  cảnh từ trước tới nay vì take CP17 yên (−25,38 LUFS theo checkpoint 17,
  đo lại từ byte thật lượt này khớp đúng, so với −21,50 LUFS của CIN_011);
  VO giữ unity theo công thức, không đổi gain — ghi rõ, không chuẩn hóa lén
  (cùng lý do như CIN_007/CIN_009/CIN_010/CIN_011).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin012_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_012 mux lại với audio nhúng (video copy bit-for-bit:
  MP4 540 frame, OGV 521 frame stored, không đổi; OGV Vorbis 160k −25,62
  LUFS / −5,70 dBTP; MP4 AAC 192k −25,62 LUFS / −5,15 dBTP — đo lại từ byte
  đã encode, lệch ≤0,02 LUFS so với mix nguồn). Các cảnh CP34/CP37/CP38/
  CP39/CP40/CP41/CP42/CP45 (CIN_001/002/004/006/003/005/007/008/009/010/011)
  chỉ được verify lại, không mux lại (LUFS khớp đúng bản ghi
  CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45).
- `RUNTIME_PACK_GOI31_v1.json` nay có 13 cảnh (thêm CIN_012); manifest
  audio runtime 618 → 619 file (mix 21 → 22); manifest cinematics cập nhật
  checkpoint 46; export manifest CIN_012 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Playback metadata + bảng phát âm CHẠY LẠI cho mix nhúng mới (theo đúng ghi
  chú CP44: khi một cảnh được nhúng mix, chạy lại builder để fallback cập
  nhật): `PLAYBACK_METADATA_v1.json` nay 13 embedded / 8 silent
  (CIN_013–020), builder PASS 0 mismatches; `PRONUNCIATION_TABLE_v1.json`
  nay 19 playback cue rows (13 embedded + 6 P0 v1/v2 alternates), 20 seam
  rows (1 flagged, không đổi — MUSIC/sa_hoa 0,016015; hàng mới
  AMBIENCE/forge 0,000533, không flag), 21 fallback rows, 135 file kiểm
  chứng (tăng từ 130); cue CIN_012: head/tail 0,0 s, slack +0,680 s,
  ducking −7,39 dB; fallback CIN_012: EMBEDDED_SOUNDTRACK → mix WAV →
  stems+VO → VO+SRT → SRT-only. Hai builder được mở rộng theo đúng tiền lệ
  CP45 (`build_playback_metadata_v1.py`: nhãn checkpoint 46;
  `build_pronunciation_table_v1.py`: map `cin012` + `CIN_012` ở cả 4 bảng
  tra, chuỗi "CIN_012-020" → "CIN_013-020", nhãn checkpoint 46).
- Tool mở rộng theo đúng tiền lệ CP45: `build_cin012_mix_v1.py` (mới),
  `build_runtime_pack_goi31.py` (thêm CIN_012 + sha manifest mix, checkpoint
  note riêng CP46 cho cảnh này), `build_runtime_delivery.py` (mục 3k8: copy
  mix runtime; nhãn checkpoint hai manifest; tổng audio 618 → 619),
  `validate_media_deliveries.py` (`check_cin012_mix()` mới + tổng audio
  618 → 619 + nhãn checkpoint + mục giới hạn CIN_012; kiểm tra bảng phát âm
  cập nhật 19 cue / 20 seam), `verify_runtime_delivery.py` (nhãn checkpoint 46).

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_46_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin012_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; playback metadata 13 embedded / 8 silent; pronunciation
  fallback files 135).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_46_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **619** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 22 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit
  nội dung `c561933`): **1279 paths, 1 violation** — vi phạm duy nhất là
  `.gitattributes`, file policy gốc của Codex do chủ dự án merge qua PR #127
  (commit `9f264ef`), KHÔNG phải nội dung CP46. Audit riêng nội dung CP46
  (base `694ddb6`, head `c561933`): **18 paths, 0 violations**.
- Commit nội dung: `c561933` (18 file: 1 tool mix mới + 6 tool mở rộng +
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
- Mix này là mix yên nhất trong các mix cảnh từ trước tới nay (−25,60 LUFS,
  so với −17,72 đến −24,63 LUFS của các mix nhúng trước): take VO CP17 yên
  (−25,38 LUFS) kéo cả mix xuống; VO giữ unity theo công thức, không chuẩn
  hóa. Nếu Codex thấy mix quá yên so với các cảnh khác, quyết định chuẩn hóa
  thuộc về adapter/Codex ở PR review — không tự đổi công thức trong
  checkpoint này.
- Build mix KHÔNG bit-deterministic giữa các lần chạy (ghi nhận ở checkpoint
  39: cùng công thức, cùng code, hai lần chạy liên tiếp cho hai SHA khác
  nhau trong khi LUFS/TP đo được giống hệt — chưa điều tra sâu vì không ảnh
  hưởng deliverable; lần này chỉ build một lần, file giao là
  `63073ea6…` và mọi manifest đều ghi đúng SHA đó — kiểm chứng sha-vs-file
  PASS; build lại sau này phải re-verify manifest, không copy SHA cũ).
- Sự cố validator lượt này (đã xử lý, không ảnh hưởng deliverable): lần chạy
  đầu `validate_media_deliveries.py` báo MISMATCHES_FOUND ở hai kiểm tra
  bảng phát âm (`cue rows 19 != 18`, `seam rows 20 != 19`) vì các assert
  cứng trong `check_pronunciation_table()` vẫn giữ số của CP44, trong khi
  builder CP46 đã thêm đúng 1 cue row (CIN_012) và 1 seam row
  (AMBIENCE/forge, lần đầu dùng trong mix nhúng). Đã cập nhật assert +
  ghi chú trong validator lên 19 cue / 20 seam và chạy lại: PASS
  0 mismatches. Ghi chú cho các lượt sau: khi thêm mix cảnh mới, cập nhật
  luôn các assert đếm trong `check_pronunciation_table()` cùng lúc với
  4 map trong `build_pronunciation_table_v1.py`.
- Mô tả PR #119 vẫn ở checkpoint 01–45; cập nhật lên CP01–46 + ACK
  CP46 cần thẻ duyệt của chủ dự án qua luồng chính (không tự ghi
  qua connector). Payload CP46 đã soạn (gộp CP46 vào bản CP01–45).
- PR #119 mergeable FALSE — xung đột duy nhất `.gitattributes` (media thêm
  2 dòng LF so với integration); chờ Codex/chủ dự án giải quyết, Muse không
  tự sửa policy.
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo cùng công thức (ứng viên gần nhất CIN_013: take VO CP17 đã
có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo setting của
cảnh tại thời điểm làm — khi thêm mix, nhớ cập nhật cả 4 map trong
`build_pronunciation_table_v1.py` VÀ các assert đếm trong
`validate_media_deliveries.py`), hoặc cập nhật mô tả PR #119 lên CP01–46
+ ACK CP46 (khi chủ dự án duyệt), hoặc M8 QA khi integration di
chuyển / PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
