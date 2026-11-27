# MEDIA-02 CHECKPOINT 49 — Mix nháp CIN_015 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f79853`
(trước checkpoint: head `40fabee`, checkpoint 48. Đầu lượt: issue #116 vẫn 18 comment,
mới nhất vẫn là comment Codex 6716052477 (2026-11-08 11:14 JST, giao MEDIA-03→05
theo Work Order 37) — KHÔNG có chỉ đạo mới kể từ checkpoint 48; integration vẫn
`6f79853`, không di chuyển; PR #119 OPEN, head sau push lượt này `74e741f`,
mô tả live vẫn ở CP01–45 (18214 ký tự, xác minh qua API lượt này); cập nhật mô
tả lên CP01–49 + ACK CP49 đã soạn trong lượt này, chờ chủ dự án duyệt, KHÔNG
đăng trong lượt này. Payload CP46 + CP47 + CP48 chưa từng được bấm, nay bị thay
thế — không đăng.)

## 0. Chỉ đạo / baseline

- Không có chỉ đạo mới trên issue #116 kể từ checkpoint 48. Tiếp tục WO37
  checkpoint lớn 1 (M-B): hoàn soundtrack cho các cảnh còn im lặng — sau
  checkpoint này còn 5 cảnh: CIN_016–020.
- Baseline integration không đổi `6f79853` (PR #128 đã merge). PR #119 vẫn
  **MERGEABLE** — xác minh qua GitHub API trong lượt này sau push:
  state open, mergeable true, head `74e741f`, 94 commit / 1300 file
  (khớp đúng số audit); mergeable_state là `unstable` thay vì `clean` như
  ở CP48 — trạng thái kiểm tra sau push mới, không phải xung đột
  (mergeable vẫn true; `.gitattributes` byte-identical với integration).
  API public có lúc rate-limit thoáng qua như ở CP46/CP47; đã đọc lại
  thành công trong lượt này (rate limit reset 06:03:53 UTC).
- Scope audit vs baseline `6f79853`: **1300 paths, 1 violation**
  (`.gitattributes`) — vẫn chỉ là artifact merge-base như CP48:
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner). Audit riêng nội dung CP49 (base `40fabee`, head
  `74e741f`): **18 paths, 0 violations**.

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_015 ("Thành phố dưới nước", 18 s) — mix cảnh thứ mười hai sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1 (checkpoint 38),
CIN_007 v1 (checkpoint 39), CIN_008 v1 (checkpoint 40), CIN_009 v1 (checkpoint 41),
CIN_010 v1 (checkpoint 42), CIN_011 v1 (checkpoint 45), CIN_012 v1 (checkpoint 46),
CIN_013 v1 (checkpoint 47) và CIN_014 v1 (checkpoint 48), cùng công thức P0 v3 — và
nhúng vào runtime OGV + review MP4 của cảnh. Cả 16 cảnh campaign có mix nhúng nay là
P0 (CIN_001/002/004) + CIN_006 + CIN_003 + CIN_005 + CIN_007 + CIN_008 + CIN_009 +
CIN_010 + CIN_011 + CIN_012 + CIN_013 + CIN_014 + CIN_015 (prologue CIN_000 tính
riêng; pack runtime nay 16 cảnh gồm prologue).

- `Tools/MediaProduction/Muse/build_cin015_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_015; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/bach_uyen` + ambience `AMBIENCE/underwater` + stinger
  `SFX/CINEMA/reveal` tại 6,0 s (đầu S02, PROPOSED chờ picture lock, theo mẫu
  CIN_004/CIN_006/CIN_007) + VO take CP17
  `VO_CIN_015_S03_DIVERLEAD_draft_v1.wav` tại 12,5 s. Tất cả stem đều
  composed (CP26/CP30), không còn stem ported nào trong mix. `bach_uyen` là
  dạng low-pass dưới nước của bộ nhạc sáng tác (850 Hz) — cue đúng setting
  cho thành phố chìm ("Lần trước có người đã buộc dây này cho chúng ta."):
  S01 toàn cảnh thị trấn chìm (mái ngói đỏ dưới nước, vòm đá, bọt khí),
  WIDE_STATIC; S02 chi tiết bát ăn buộc vào bàn đá, dây dẫn và bàn tay
  trần của thợ lặn, DETAIL_LOCKED; S03 hành lang nhìn từ trên xuống với
  thợ lặn nhỏ đội nón ở cuối hành lang, TOPDOWN_MATCH (theo đúng keyframe
  CIN_015 S01/S02/S03, bản sửa checkpoint 32: S02 đã chìm hẳn dưới nước).
  `underwater` là giường tiếng nước chìm cho thành phố ôm cả ba shot.
  Cả hai đều là lần đầu dùng trong mix cảnh (trước đó chỉ ở reel review
  P0 v3). `ben_mua` đã bỏ qua: vừa dùng cho CIN_014 — cảnh ngay trước đó.
  `lam_trieu` đã bỏ qua: sáo đồng quê, dùng cho CIN_013. `tran_son` đã bỏ
  qua: dạng chuông-cổng, dùng cho CIN_008 và CIN_012. `quiet_discovery`
  đã bỏ qua: dùng cho CIN_007 và CIN_011. `thang_long` là dạng kinh thành
  (sai setting); `sa_hoa` là dạng sa mạc khô (sai setting); `rift_finale`
  là cái kết đầy đủ duy nhất của bộ (finale, sai cho nhịp giữa chapter);
  `boss_mang_cot` là nhạc boss. Ambience: `wind_canopy` vừa dùng cho
  CIN_014; `mountain_wind` dùng cho CIN_013; `forge` dùng cho CIN_012;
  `river_shore` dùng cho CIN_003/CIN_008 (mép nước, không phải chìm hẳn);
  `waterfall` dùng cho CIN_009; `rain_light`/`rain_heavy` là mưa trên mặt
  nước; `cave_drips` là hang, không phải thành phố chìm mở; `desert_wind`,
  `city_night`, `thang_long_crowd`, `rift` đều sai setting.
- Điểm khác CIN_014 (nói thẳng): take VO CIN_015 KHỚP cửa sổ với dư 2,120 s —
  take 2,880 s, chạy 12,5–15,380 s, kết thúc 2,120 s TRƯỚC cuối cửa sổ 17,5 s
  và 2,620 s trước cuối cảnh 18,00 s. Không overrun, không tail trim. Cửa sổ
  là uniform 12,5–17,5 s, KHÔNG nới; take và timing không bị sửa để che giấu
  gì. (Câu thoại 48 ký tự nên không ghi tỉ lệ ký tự/giây — thời lượng take đo
  từ byte thật, CP17 ghi windowFit FITS, không tăng tốc.)
- Bằng chứng ducking đo theo cửa sổ VO ĐẦY ĐỦ (phương pháp CP39 giữ nguyên
  để các mix CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/
  CIN_013/CIN_014/CIN_015 so sánh được với nhau): `bach_uyen` −6,87 dB trong
  cửa sổ, 0,0 dB ngoài cửa sổ — nông hơn −8,84 dB của CIN_014 vì `bach_uyen`
  yên hơn trong cửa sổ so với `ben_mua`; cùng tham số compressor, là số đo,
  không phải chỉnh lại.
- `Art_Source/Audio/Muse/MIX/CIN015_DRAFT_V1/CIN_015_mix_draft_v1.wav` +
  `CIN015_MIX_V1_manifest_v1.json`: mix 18,000 s, −25,30 LUFS / −3,89 dBTP,
  LRA 10,60 LU, peak trim 0,00 dB; ducking nhạc −6,87 dB trong cửa sổ VO,
  0,0 dB ngoài cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 =
  0,593. Ba stem đo lại từ byte thật khớp đúng bảng pack (bach_uyen
  −21,96; underwater −33,11; reveal −24,96 LUFS). Take VO CP17 đo lại
  −23,27 LUFS; VO giữ unity theo công thức, không đổi gain — ghi rõ,
  không chuẩn hóa lén (cùng lý do như CIN_007/CIN_009/CIN_010/CIN_011/
  CIN_012/CIN_013/CIN_014).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin015_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_015 mux lại bằng `build_runtime_pack_goi31.py` (đã mở
  rộng cho CIN_015) với audio nhúng (video copy bit-for-bit: MP4 540 frame,
  OGV 511 frame stored, không đổi; MD5 video stream khớp đúng bản gốc —
  MP4 6b0c024f… / OGV 05b36865…; OGV Vorbis 160k −25,31 LUFS / −3,91 dBTP;
  MP4 AAC 192k −25,30 LUFS / −3,89 dBTP — đo lại từ byte đã encode, lệch
  ≤0,01 LUFS so với mix nguồn; metadata comment CP49 trong cả hai file).
  Các cảnh CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/CP48
  (CIN_001/002/004/006/003/005/007/008/009/010/011/012/013/014) chỉ được
  verify lại, không mux lại (LUFS khớp đúng bản ghi
  CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/CP48).
- `RUNTIME_PACK_GOI31_v1.json` nay có 16 cảnh (thêm CIN_015); manifest
  audio runtime 621 → 622 file (mix 24 → 25); manifest cinematics cập nhật
  checkpoint 49; export manifest CIN_015 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Playback metadata + bảng phát âm CHẠY LẠI cho mix nhúng mới (theo đúng ghi
  chú CP44: khi một cảnh được nhúng mix, chạy lại builder để fallback cập
  nhật): `PLAYBACK_METADATA_v1.json` nay 16 embedded / 5 silent
  (CIN_016–020), builder PASS 0 mismatches; `PRONUNCIATION_TABLE_v1.json`
  nay 22 playback cue rows (16 embedded + 6 P0 v1/v2 alternates), 22 seam
  rows (1 flagged, không đổi — MUSIC/sa_hoa 0,016015; hàng seam MỚI duy
  nhất: MUSIC/bach_uyen composed 0,000568, không flag — khớp đúng số CP33;
  AMBIENCE/underwater composed đã có trong bảng từ P0 v3 CIN_002 nên không
  thêm hàng), 21 fallback rows, 150 file kiểm chứng (tăng từ 145);
  cue CIN_015: head/tail 0,0 s, slack +2,120 s, ducking −6,87 dB, VO take
  lead silence 0,115 s / tail silence 0,253 s; fallback CIN_015:
  EMBEDDED_SOUNDTRACK → mix WAV → stems+VO → VO+SRT → SRT-only. Ba builder
  được mở rộng theo đúng tiền lệ CP48 (`build_playback_metadata_v1.py`:
  nhãn checkpoint 49; `build_pronunciation_table_v1.py`: map `cin015` +
  `CIN_015` ở cả 4 bảng tra, chuỗi "CIN_015-020" → "CIN_016-020", nhãn
  checkpoint 49) và validator mở rộng theo tiền lệ (`check_cin015_mix`
  mới, assert playbackCueRows 21 → 22, seamRows 21 → 22, assert runtime
  total 621 → 622, chuỗi checkpoint 49, mục CIN_015 trong notes).
- Staging (KHÔNG phải khuyết điểm của mix, không chặn mix): timing manifest
  ghi thoại S03 `onscreen: true` cho Đội trưởng thợ lặn, và keyframe S03
  đặt một thợ lặn nhỏ đội nón ở cuối hành lang nhìn từ trên xuống — đúng vị
  trí người nói theo ý đồ. Nhưng nhân vật quá nhỏ và chỉ thấy từ trên/sau
  lưng nên người nói không nhận diện được bằng mặt hay đồ nghề từ hình;
  S02 chỉ có một bàn tay trần ở dây dẫn (không mặt) và S01 không có nhân
  vật nào. Đây là việc của final picture/character lock, không phải lỗi
  mix; mix không dời VO để che. (Ghi chú staging trong script mix đã viết
  đúng sự thật này TRƯỚC khi mux.)

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_49_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin015_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; playback metadata 16 embedded / 5 silent; pronunciation
  cue rows 22 / seam rows 22 / fallback files 150; counts khác chỉ đúng 6
  thay đổi kỳ vọng so với CP48: cin015 files checked, embedded 15→16,
  silent 6→5, cue rows 21→22, seam rows 21→22, fallback files 145→150).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_49_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **622** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 25 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f79853`, head commit
  nội dung `74e741f`): **1300 paths, 1 violation** — `.gitattributes`, nhưng
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner sau PR #128); tool vẫn liệt kê vì nó diff từ merge-base
  `cf17178` (merge PR #117), nơi file chưa có 12 dòng LF của PR #127. Audit
  riêng nội dung CP49 (base `40fabee`, head `74e741f`): **18 paths, 0 violations**.
- Commit nội dung: `74e741f` (18 file: 1 tool mix mới + 6 tool mở rộng +
  2 file mix nguồn + 1 file mix runtime + 2 file video mux lại + 4 manifest
  runtime + 1 export manifest + 1 bảng phát âm). File WAV/OGV/MP4 commit
  dưới dạng LFS pointer (quy tắc `.gitattributes` đã merge qua PR #127;
  mix runtime trùng SHA với mix nguồn nên LFS chỉ thêm 1 object). Push đã
  xác minh qua `git ls-remote`: remote head `74e741f`, 3 object LFS upload.
- PR #119 sau push (xác minh qua GitHub API trong lượt này): state open,
  mergeable true, mergeable_state `unstable` (khác `clean` ở CP48 — trạng
  thái kiểm tra sau push mới, không phải xung đột), head `74e741f`,
  94 commit / 1300 file (khớp đúng số audit); mô tả live vẫn CP01–45
  (18214 ký tự). API public trả 403 rate-limit ở đầu lượt; đã thử lại và
  đọc thành công trong lượt này.
- Không có sự cố thao tác trong lượt này: không rm file LFS trước khi
  `git checkout` (bài học CP48 đã áp dụng — mux bằng tool ngay từ đầu);
  mix giao là bản build duy nhất, SHA `635afb8f…`, đo lại độc lập khớp
  manifest (−25,30/−3,89/LRA 10,60, 18,000 s).

## 3. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho mix này và toàn bộ shortlist;
  mọi số LUFS/TP là đo từ byte, không phải PASS nghe tai. Mix vẫn
  DRAFT_MIX_NOT_FINAL; stem assignment PROPOSED; vị trí stinger PROPOSED
  chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; clip vẫn là Ken Burns trên
  still storyboard, không phải final pose animation. Staging S03 (người nói
  chỉ là thợ lặn nhỏ nhìn từ trên xuống, không nhận diện được bằng mặt/đồ
  nghề) chờ character lock / đạo diễn — không dời VO, không sửa timing
  trong checkpoint này.
- Ducking −6,87 dB nông hơn hẳn mix gần nhất (−8,84 dB CIN_014): cùng tham
  số compressor, `bach_uyen` yên hơn trong cửa sổ VO; là số đo, không phải
  chỉnh lại. Nếu Codex thấy nhạc bị dìm chưa đủ ở cảnh này, quyết định
  thuộc về adapter ở PR review — không tự đổi công thức trong checkpoint này.
- Build mix KHÔNG bit-deterministic giữa các lần chạy (ghi nhận ở checkpoint
  39 và xác nhận lại ở checkpoint 48: cùng công thức, cùng code, hai lần
  chạy liên tiếp cho hai SHA khác nhau trong khi LUFS/TP đo được giống hệt —
  build lại sau này phải re-verify manifest, không copy SHA cũ).
- Mô tả PR #119 vẫn ở checkpoint 01–45; cập nhật lên CP01–49 + ACK
  CP49 cần thẻ duyệt của chủ dự án qua luồng chính (không tự ghi
  qua connector). Payload CP49 đã soạn (gộp CP49 vào bản CP01–48, kèm
  chỉnh số runtime 621 → 622 file và trạng thái mergeable mới).
- PR #119 mergeable TRUE (mergeable_state `unstable`, không phải conflict)
  — nhưng Muse không tự merge; Codex review/merge. 5 cảnh còn im lặng:
  CIN_016–020 (WO37 checkpoint lớn 1: còn 5 mix).
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo cùng công thức (ứng viên gần nhất CIN_016: take VO CP17 đã
có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo setting của
cảnh tại thời điểm làm — khi thêm mix, nhớ cập nhật cả 4 map trong
`build_pronunciation_table_v1.py` VÀ các assert đếm trong
`validate_media_deliveries.py`), hoặc cập nhật mô tả PR #119 lên CP01–49
+ ACK CP49 (khi chủ dự án duyệt), hoặc M8 QA khi integration di
chuyển / PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
