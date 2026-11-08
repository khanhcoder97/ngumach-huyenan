# MEDIA-02 CHECKPOINT 48 — Mix nháp CIN_014 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f79853`
(trước checkpoint: head `2c2a5d0`, checkpoint 47. Đầu lượt: issue #116 vẫn 18 comment,
mới nhất vẫn là comment Codex 6716052477 (2026-11-08 11:14 JST, giao MEDIA-03→05
theo Work Order 37) — KHÔNG có chỉ đạo mới kể từ checkpoint 47; integration vẫn
`6f79853`, không di chuyển; PR #119 OPEN, head sau push lượt này `7954116`,
mô tả live vẫn ở CP01–45 (18214 ký tự, xác minh qua API lượt này); cập nhật mô
tả lên CP01–48 + ACK CP48 đã soạn trong lượt này, chờ chủ dự án duyệt, KHÔNG
đăng trong lượt này. Payload CP46 + CP47 chưa từng được bấm, nay bị thay thế —
không đăng.)

## 0. Chỉ đạo / baseline

- Không có chỉ đạo mới trên issue #116 kể từ checkpoint 47. Tiếp tục WO37
  checkpoint lớn 1 (M-B): hoàn soundtrack cho các cảnh còn im lặng — sau
  checkpoint này còn 6 cảnh: CIN_015–020.
- Baseline integration không đổi `6f79853` (PR #128 đã merge). PR #119 vẫn
  **MERGEABLE/CLEAN** — xác minh qua GitHub API trong lượt này sau push:
  state open, mergeable true, mergeable_state clean, head `7954116`,
  92 commit / 1293 file (khớp đúng số audit). API public có lúc rate-limit
  thoáng qua như ở CP46/CP47; đã đọc lại thành công sau 60 s.
- Scope audit vs baseline `6f79853`: **1293 paths, 1 violation**
  (`.gitattributes`) — vẫn chỉ là artifact merge-base như CP47:
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner). Audit riêng nội dung CP48 (base `2c2a5d0`, head
  `7954116`): **18 paths, 0 violations**.

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_014 ("Dấu lệnh đặt xuống", 18 s) — mix cảnh thứ mười một sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1 (checkpoint 38),
CIN_007 v1 (checkpoint 39), CIN_008 v1 (checkpoint 40), CIN_009 v1 (checkpoint 41),
CIN_010 v1 (checkpoint 42), CIN_011 v1 (checkpoint 45), CIN_012 v1 (checkpoint 46)
và CIN_013 v1 (checkpoint 47), cùng công thức P0 v3 — và nhúng vào runtime OGV +
review MP4 của cảnh. Cả 15 cảnh campaign có mix nhúng nay là P0 (CIN_001/002/004) +
CIN_006 + CIN_003 + CIN_005 + CIN_007 + CIN_008 + CIN_009 + CIN_010 + CIN_011 +
CIN_012 + CIN_013 + CIN_014 (prologue CIN_000 tính riêng; pack runtime nay 15 cảnh
gồm prologue).

- `Tools/MediaProduction/Muse/build_cin014_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_014; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/ben_mua` + ambience `AMBIENCE/wind_canopy` + stinger
  `SFX/CINEMA/reveal` tại 6,0 s (đầu S02, PROPOSED chờ picture lock, theo mẫu
  CIN_004/CIN_006/CIN_007) + VO take CP17
  `VO_CIN_014_S03_TONGBANH_draft_v1.wav` tại 12,5 s. Tất cả stem đều
  composed (CP26/CP30), không còn stem ported nào trong mix. `ben_mua` là
  câu nhạc leitmotif chính của campaign ("Bến Mưa", bến mưa): cụm hỏi D major
  pentatonic treo ở bậc 2, đuôi bỏ lửng — cụm hỏi chưa có lời đáp cho hành
  động đạo đức chưa khép ("Ta biết lệnh ấy là giả. Ta vẫn cho đóng dấu.");
  lần dùng trước trong mix cảnh là CIN_003, cách đây 10 cảnh. `wind_canopy`
  là nền gió qua tán tre với tiếng lá xào xạc cho tre ôm cả ba shot (S01:
  Tống Bành quỳ giữa đống giáp bỏ lại và cờ rách trước tường đá đổ, tre và
  núi sau lưng, MEDIUM_STATIC; S02: Tống Bành cận cảnh đặt con dấu xuống
  tấm ấn vuông trên nền đá, DETAIL_LOCKED; S03: Tống Bành áo lam đứng ở cổng
  làng gỗ mở đối diện dân làng tụ tập, tre và mái tranh xung quanh,
  WIDE_STATIC; theo đúng keyframe CIN_014 S01/S02/S03).
  `lam_trieu` đã bỏ qua: sáo đồng quê vừa dùng cho CIN_013 — cảnh ngay
  trước đó. `tran_son` đã bỏ qua: dạng chuông-cổng đúng tên gọi, nhưng đã
  dùng cho CIN_008 và CIN_012 — dùng lần thứ ba trong bốn cảnh sẽ làm nhòe
  các cảnh kề nhau. `sa_hoa` là dạng sa mạc khô (sai setting);
  `quiet_discovery` vừa dùng cho CIN_011; `bach_uyen` là dạng low-pass dưới
  nước (sai setting); `rift_finale` là cái kết đầy đủ duy nhất của bộ
  (finale, sai cho nhịp quyết định giữa campaign); `boss_mang_cot` là nhạc boss.
- Điểm khác CIN_013 (nói thẳng): take VO CIN_014 KHỚP cửa sổ với dư 1,928 s —
  take 3,072 s, chạy 12,5–15,572 s, kết thúc 1,928 s TRƯỚC cuối cửa sổ 17,5 s
  và 2,428 s trước cuối cảnh 18,00 s. Không overrun, không tail trim. Cửa sổ
  là uniform 12,5–17,5 s (35 ký tự ở 7,00 ký tự/giây), KHÔNG nới; take và
  timing không bị sửa để che giấu gì.
- Bằng chứng ducking đo theo cửa sổ VO ĐẦY ĐỦ (phương pháp CP39 giữ nguyên
  để các mix CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/
  CIN_013/CIN_014 so sánh được với nhau): `ben_mua` −8,84 dB trong cửa sổ,
  0,0 dB ngoài cửa sổ — sâu hơn −5,19 dB của CIN_013 vì `ben_mua` to hơn
  trong cửa sổ so với `lam_trieu`; cùng tham số compressor, là số đo, không
  phải chỉnh lại.
- `Art_Source/Audio/Muse/MIX/CIN014_DRAFT_V1/CIN_014_mix_draft_v1.wav` +
  `CIN014_MIX_V1_manifest_v1.json`: mix 18,000 s, −24,42 LUFS / −1,95 dBTP,
  LRA 7,20 LU, peak trim 0,00 dB; ducking nhạc −8,84 dB trong cửa sổ VO,
  0,0 dB ngoài cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 =
  0,765. Ba stem đo lại từ byte thật khớp đúng bảng pack (ben_mua
  −21,93; wind_canopy −29,70; reveal −24,96 LUFS). Take VO CP17 đo lại
  −22,05 LUFS; VO giữ unity theo công thức, không đổi gain — ghi rõ,
  không chuẩn hóa lén (cùng lý do như CIN_007/CIN_009/CIN_010/CIN_011/
  CIN_012/CIN_013).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin014_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_014 mux lại bằng `build_runtime_pack_goi31.py` (đã mở
  rộng cho CIN_014) với audio nhúng (video copy bit-for-bit: MP4 540 frame,
  OGV 508 frame stored, không đổi; MD5 video stream khớp đúng bản gốc;
  OGV Vorbis 160k −24,44 LUFS / −2,14 dBTP; MP4 AAC 192k −24,43 LUFS /
  −1,94 dBTP — đo lại từ byte đã encode, lệch ≤0,02 LUFS so với mix nguồn;
  metadata comment CP48 trong cả hai file). Các cảnh CP34/CP37/CP38/CP39/
  CP40/CP41/CP42/CP45/CP46/CP47 (CIN_001/002/004/006/003/005/007/008/009/
  010/011/012/013) chỉ được verify lại, không mux lại (LUFS khớp đúng bản ghi
  CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47).
- `RUNTIME_PACK_GOI31_v1.json` nay có 15 cảnh (thêm CIN_014); manifest
  audio runtime 620 → 621 file (mix 23 → 24); manifest cinematics cập nhật
  checkpoint 48; export manifest CIN_014 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Playback metadata + bảng phát âm CHẠY LẠI cho mix nhúng mới (theo đúng ghi
  chú CP44: khi một cảnh được nhúng mix, chạy lại builder để fallback cập
  nhật): `PLAYBACK_METADATA_v1.json` nay 15 embedded / 6 silent
  (CIN_015–020), builder PASS 0 mismatches; `PRONUNCIATION_TABLE_v1.json`
  nay 21 playback cue rows (15 embedded + 6 P0 v1/v2 alternates), 21 seam
  rows (1 flagged, không đổi — MUSIC/sa_hoa 0,016015; không có hàng seam mới
  — seam ben_mua + wind_canopy đã đo ở CP37/CP39), 21 fallback rows, 145 file
  kiểm chứng (tăng từ 140); cue CIN_014: head/tail 0,0 s, slack +1,928 s,
  ducking −8,84 dB, VO take lead silence 0,182 s / tail silence 0,162 s;
  fallback CIN_014: EMBEDDED_SOUNDTRACK → mix WAV → stems+VO → VO+SRT →
  SRT-only. Ba builder được mở rộng theo đúng tiền lệ CP47
  (`build_playback_metadata_v1.py`: nhãn checkpoint 48;
  `build_pronunciation_table_v1.py`: map `cin014` + `CIN_014` ở cả 4 bảng
  tra, chuỗi "CIN_014-020" → "CIN_015-020", nhãn checkpoint 48) và
  validator mở rộng theo tiền lệ (`check_cin014_mix` mới, assert
  playbackCueRows 20 → 21, assert runtime total 620 → 621, chuỗi checkpoint
  48, mục CIN_014 trong notes).
- Staging (KHÔNG phải khuyết điểm của mix, không chặn mix): timing manifest
  ghi thoại S03 `onscreen: true` cho Tống Bành, và keyframe S03 đặt một nhân
  vật áo lam ở cổng mở đối diện dân làng — đúng vị trí người nói theo ý đồ.
  Nhưng khuyết điểm keyframe đã ghi (export manifest) lưu ý Tống Bành KHÔNG
  nhận diện được bằng hình ở S03: giáp của ông khác nhau giữa S01/S02 và
  không nhân vật nào ở S03 khớp giáp đó, nên việc nhận diện chỉ từ hình là
  không chắc chắn. Đây là việc của final picture/character lock, không phải
  lỗi mix; mix không dời VO để che. (Ghi chú staging trong script mix đã
  sửa cho đúng sự thật này TRƯỚC khi mux — xem mục 2.)

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_48_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin014_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; playback metadata 15 embedded / 6 silent; pronunciation
  fallback files 145; counts khác chỉ đúng 5 thay đổi kỳ vọng so với CP47:
  cin014 files checked, embedded 14→15, silent 7→6, cue rows 20→21,
  fallback files 140→145).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_48_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **621** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 24 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f79853`, head commit
  nội dung `7954116`): **1293 paths, 1 violation** — `.gitattributes`, nhưng
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner sau PR #128); tool vẫn liệt kê vì nó diff từ merge-base
  `cf17178` (merge PR #117), nơi file chưa có 12 dòng LF của PR #127. Audit
  riêng nội dung CP48 (base `2c2a5d0`, head `7954116`): **18 paths, 0 violations**.
- Commit nội dung: `7954116` (18 file: 1 tool mix mới + 6 tool mở rộng +
  2 file mix nguồn + 1 file mix runtime + 2 file video mux lại + 4 manifest
  runtime + 1 export manifest + 1 bảng phát âm). File WAV/OGV/MP4 commit
  dưới dạng LFS pointer (quy tắc `.gitattributes` đã merge qua PR #127;
  mix runtime trùng SHA với mix nguồn nên LFS chỉ thêm 1 object). Push đã
  xác minh qua `git ls-remote`: remote head `7954116`, 3 object LFS upload.
- Sự cố thao tác trong lượt này (đã xử lý, không ảnh hưởng deliverable):
  sau lần build mix đầu (SHA `f129e9c4…`), ghi chú staging trong script mix
  được sửa cho đúng (xem mục 1) nên phải build lại mix; khi khôi phục file
  video gốc để mux lại bằng tool, lệnh `git checkout` trong một exec quên
  export PATH chứa git-lfs nên fail SAU KHI `rm` đã xóa 2 file video runtime
  của CIN_014. Hai file đã được khôi phục byte-identical từ git ngay sau đó
  (SHA khớp đúng manifest gốc 53498bf6… / 08bbe2b0…), rồi mux lại bằng
  `build_runtime_pack_goi31.py` — file giao cuối có metadata comment CP48 và
  số đo khớp đúng bản build tay trước đó. Bài học: không `rm` file LFS trước
  khi `git checkout` được xác minh có git-lfs trong PATH; dùng tool mux thay
  vì mux tay ngay từ đầu. Mix giao cuối là SHA `b63e51bf…` (build lại có cùng
  LUFS/TP với bản đầu — đúng ghi nhận không-bit-deterministic ở checkpoint 39).

## 3. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho mix này và toàn bộ shortlist;
  mọi số LUFS/TP là đo từ byte, không phải PASS nghe tai. Mix vẫn
  DRAFT_MIX_NOT_FINAL; stem assignment PROPOSED; vị trí stinger PROPOSED
  chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; clip vẫn là Ken Burns trên
  still storyboard, không phải final pose animation. Staging S03 (Tống Bành
  không nhận diện chắc bằng hình) chờ character lock / đạo diễn — không dời
  VO, không sửa timing trong checkpoint này.
- Ducking −8,84 dB sâu hơn hẳn các mix gần đây (−5,19 dB CIN_013, −7,39 dB
  CIN_012): cùng tham số compressor, `ben_mua` to hơn trong cửa sổ VO; là số
  đo, không phải chỉnh lại. Nếu Codex thấy nhạc bị dìm quá sâu ở cảnh này,
  quyết định thuộc về adapter ở PR review — không tự đổi công thức trong
  checkpoint này.
- Build mix KHÔNG bit-deterministic giữa các lần chạy (ghi nhận ở checkpoint
  39: cùng công thức, cùng code, hai lần chạy liên tiếp cho hai SHA khác
  nhau trong khi LUFS/TP đo được giống hệt — lượt này xác nhận lại: bản đầu
  `f129e9c4…` và bản giao `b63e51bf…` cùng −24,42/−1,95; build lại sau này
  phải re-verify manifest, không copy SHA cũ).
- Mô tả PR #119 vẫn ở checkpoint 01–45; cập nhật lên CP01–48 + ACK
  CP48 cần thẻ duyệt của chủ dự án qua luồng chính (không tự ghi
  qua connector). Payload CP48 đã soạn (gộp CP48 vào bản CP01–47, kèm
  chỉnh số runtime 620 → 621 file và trạng thái mergeable mới).
- PR #119 mergeable TRUE/CLEAN — nhưng Muse không tự merge; Codex
  review/merge. 6 cảnh còn im lặng: CIN_015–020 (WO37 checkpoint lớn 1:
  còn 6 mix).
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo cùng công thức (ứng viên gần nhất CIN_015: take VO CP17 đã
có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo setting của
cảnh tại thời điểm làm — khi thêm mix, nhớ cập nhật cả 4 map trong
`build_pronunciation_table_v1.py` VÀ các assert đếm trong
`validate_media_deliveries.py`), hoặc cập nhật mô tả PR #119 lên CP01–48
+ ACK CP48 (khi chủ dự án duyệt), hoặc M8 QA khi integration di
chuyển / PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
