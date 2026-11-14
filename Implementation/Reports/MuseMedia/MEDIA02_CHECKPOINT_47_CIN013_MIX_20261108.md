# MEDIA-02 CHECKPOINT 47 — Mix nháp CIN_013 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f79853`
(trước checkpoint: head `b14d7de`, checkpoint 46. Đầu lượt: issue #116 có 18 comment
sau ACK CP43–CP45 đăng 10:42 JST (comment 6715782450) — có chỉ đạo mới: comment
Codex 6716052477 (2026-11-08 11:14 JST, giao MEDIA-03→05 theo Work Order 37);
integration đã đổi `6f2b465` → `6f79853` (PR #128 merge); PR #119 OPEN,
head `b14d7de`, mô tả ở CP01–46 (đăng 10:41 JST, đã xác minh read-back);
cập nhật mô tả lên CP01–47 + ACK CP47 đã soạn trong lượt này, chờ
chủ dự án duyệt, KHÔNG đăng trong lượt này.)

## 0. Chỉ đạo mới — MEDIA-03→05 (WO37) + re-baseline

- Codex comment 6716052477 (đăng bởi khanhcoder97, 2026-11-08 11:14 JST): Muse
  nhận **MEDIA-03→05, toàn campaign và media runtime** theo Work Order 37
  (`Implementation/Work_Orders/37_MUSE_FULL_CAMPAIGN_MEDIA_20261108.md`,
  PR #129 head `2c1a09c`, đã đọc trong lượt này). Chuỗi bốn checkpoint lớn:
  (1) hoàn mix còn thiếu + metadata, (2) P0 motion/AB, (3) campaign motion/
  score/SFX/VO, (4) full exports/stems/provenance/QA/device pack. Mốc 32 chưa
  đạt vẫn là P0, không bị xóa bởi assignment mới; push media thật rồi tiếp
  phần độc lập, không dừng sau một mix/report hoặc chờ merge PR #119.
- **Owner blocker đã gỡ:** PR #128 merge vào integration `6f79853`; hai LF roots
  nay có trên integration; PR #119 **MERGEABLE/CLEAN** — xác minh qua GitHub API
  trong lượt này: state open, mergeable true, mergeable_state clean,
  head `b14d7de`, 89 commit / 1282 file. (API public có lúc trả về lỗi rate-limit
  thoáng qua như ở CP46; đã đọc lại thành công và khớp `git ls-remote`.)
- Scope audit vs baseline mới `6f79853`: **1286 paths, 1 violation**
  (`.gitattributes`). Vi phạm này nay chỉ còn là artifact của cách tính
  merge-base: tool diff từ merge-base `cf17178` (merge PR #117) → head nên vẫn
  liệt kê 12 dòng LF do PR #127 (owner merge) thêm trên nhánh media; nhưng
  `git diff 6f79853 HEAD -- .gitattributes` **rỗng — file byte-identical với
  baseline owner mới**. Không còn lệch nội dung thật. Audit riêng nội dung CP47
  (base `b14d7de`, head `33a4811`): **18 paths, 0 violations**. Lịch sử report
  giữ nguyên ghi nhận violation cũ theo WO37 M-A (không sửa để xóa evidence).
- Review 2026-11-08 của Codex (PR #129) đã đọc: pin `694ddb6`/CP45 được auditor
  read-only kiểm hash/size 618 audio + 107 cinematic references khớp; delta
  CP46 `b14d7de` chỉ đọc source, chưa kiểm byte lại — không yêu cầu làm lại
  CIN_012; danh sách còn lại lấy từ manifest mới (lượt này làm đúng vậy).

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_013 ("Qua cổng, còn người đợi", 18 s) — mix cảnh thứ mười sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1 (checkpoint 38),
CIN_007 v1 (checkpoint 39), CIN_008 v1 (checkpoint 40), CIN_009 v1 (checkpoint 41),
CIN_010 v1 (checkpoint 42), CIN_011 v1 (checkpoint 45) và CIN_012 v1
(checkpoint 46), cùng công thức P0 v3 — và nhúng vào runtime OGV + review MP4
của cảnh. Cả 14 cảnh campaign có mix nhúng nay là P0 (CIN_001/002/004) + CIN_006 +
CIN_003 + CIN_005 + CIN_007 + CIN_008 + CIN_009 + CIN_010 + CIN_011 + CIN_012 +
CIN_013 (prologue CIN_000 tính riêng; pack runtime nay 14 cảnh gồm prologue).

- `Tools/MediaProduction/Muse/build_cin013_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_013; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/lam_trieu` + ambience `AMBIENCE/mountain_wind` (lần đầu dùng
  trong mix nhúng) + stinger `SFX/CINEMA/reveal` tại 6,0 s (đầu S02, PROPOSED
  chờ picture lock, theo mẫu CIN_004/CIN_006/CIN_007) + VO take CP17
  `VO_CIN_013_S03_REFUGEELEADER_draft_v1.wav` tại 12,5 s. Tất cả stem đều
  composed (CP26/CP30), không còn stem ported nào trong mix. `lam_trieu` là
  dạng G-major với sáo trang trí của bộ sáng tác ("Lâm Triều") — giọng sáo
  đồng quê cho đường làng, ruộng lúa và câu thoại chờ đợi ("Chưa đóng cổng.
  Còn một người đi sau."); `mountain_wind` là nền gió núi cho cổng đá, đèo
  mở và ruộng bậc của cả ba shot (S01: cổng đá mái ngói trên tường thành,
  đoàn người tị nạn mang gói đi qua, núi phía sau, WIDE_STATIC; S02: Trưởng
  đoàn áo vá, khăn đầu, cầm bản đồ gấp, giơ một ngón tay, bìa làng nhà tranh,
  tre, giỏ, núi, MEDIUM_STATIC; S03: Ly An áo lam, nón trên lưng, đứng ở
  cổng gỗ mở nhìn ra ruộng lúa và đường làng, dải ruy băng trắng buộc ở cột
  cổng, MEDIUM_STATIC; theo đúng keyframe CIN_013 S01/S02/S03).
  `tran_son` đã bỏ qua: dạng chuông-cổng đúng tên gọi, nhưng vừa dùng cho
  CIN_012 — cảnh ngay trước đó — và CIN_008; dùng lần thứ ba liên tiếp sẽ
  làm nhòe hai cảnh kề nhau. `bach_uyen` là dạng low-pass dưới nước (sai
  setting); `rift_finale` là cái kết đầy đủ duy nhất của bộ (finale, sai
  cho nhịp chờ giữa campaign); `boss_mang_cot` là nhạc boss.
- Điểm khác CIN_012 (nói thẳng): take VO CIN_013 KHỚP cửa sổ với dư rất lớn —
  take 2,472 s, chạy 12,5–14,972 s, kết thúc 2,528 s TRƯỚC cuối cửa sổ 17,5 s
  và 3,028 s trước cuối cảnh 18,00 s. Không overrun, không tail trim. Cửa sổ
  là uniform 12,5–17,5 s (37 ký tự ở 7,40 ký tự/giây), KHÔNG nới; take và
  timing không bị sửa để che giấu gì.
- Bằng chứng ducking đo theo cửa sổ VO ĐẦY ĐỦ (phương pháp CP39 giữ nguyên
  để các mix CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/
  CIN_013 so sánh được với nhau): `lam_trieu` −5,19 dB trong cửa sổ, 0,0 dB
  ngoài cửa sổ.
- `Art_Source/Audio/Muse/MIX/CIN013_DRAFT_V1/CIN_013_mix_draft_v1.wav` +
  `CIN013_MIX_V1_manifest_v1.json`: mix 18,000 s, −25,87 LUFS / −5,17 dBTP,
  LRA 11,80 LU, peak trim 0,00 dB; ducking nhạc −5,19 dB trong cửa sổ VO,
  0,0 dB ngoài cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 =
  0,73. Ba stem đo lại từ byte thật khớp đúng bảng pack (lam_trieu
  −21,93; mountain_wind −29,55; reveal −24,96 LUFS). Mix yên nhất trong các
  mix cảnh từ trước tới nay (−25,87 LUFS, so với −25,60 LUFS của CIN_012)
  vì take CP17 yên (−22,51 LUFS theo checkpoint 17, đo lại từ byte thật
  lượt này khớp đúng); VO giữ unity theo công thức, không đổi gain — ghi
  rõ, không chuẩn hóa lén (cùng lý do như CIN_007/CIN_009/CIN_010/CIN_011/
  CIN_012).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin013_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_013 mux lại với audio nhúng (video copy bit-for-bit:
  MP4 540 frame, OGV 513 frame stored, không đổi; OGV Vorbis 160k −25,86
  LUFS / −5,07 dBTP; MP4 AAC 192k −25,88 LUFS / −5,29 dBTP — đo lại từ byte
  đã encode, lệch ≤0,02 LUFS so với mix nguồn). Các cảnh CP34/CP37/CP38/
  CP39/CP40/CP41/CP42/CP45/CP46 (CIN_001/002/004/006/003/005/007/008/009/
  010/011/012) chỉ được verify lại, không mux lại (LUFS khớp đúng bản ghi
  CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46).
- `RUNTIME_PACK_GOI31_v1.json` nay có 14 cảnh (thêm CIN_013); manifest
  audio runtime 619 → 620 file (mix 22 → 23); manifest cinematics cập nhật
  checkpoint 47; export manifest CIN_013 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Playback metadata + bảng phát âm CHẠY LẠI cho mix nhúng mới (theo đúng ghi
  chú CP44: khi một cảnh được nhúng mix, chạy lại builder để fallback cập
  nhật): `PLAYBACK_METADATA_v1.json` nay 14 embedded / 7 silent
  (CIN_014–020), builder PASS 0 mismatches; `PRONUNCIATION_TABLE_v1.json`
  nay 20 playback cue rows (14 embedded + 6 P0 v1/v2 alternates), 21 seam
  rows (1 flagged, không đổi — MUSIC/sa_hoa 0,016015; hàng mới
  AMBIENCE/mountain_wind 0,000734, không flag), 21 fallback rows, 140 file
  kiểm chứng (tăng từ 135); cue CIN_013: head/tail 0,0 s, slack +2,528 s,
  ducking −5,19 dB, VO take lead silence 0,207 s / tail silence 0,242 s;
  fallback CIN_013: EMBEDDED_SOUNDTRACK → mix WAV → stems+VO → VO+SRT →
  SRT-only. Hai builder được mở rộng theo đúng tiền lệ CP46
  (`build_playback_metadata_v1.py`: nhãn checkpoint 47;
  `build_pronunciation_table_v1.py`: map `cin013` + `CIN_013` ở cả 4 bảng
  tra, chuỗi "CIN_013-020" → "CIN_014-020", nhãn checkpoint 47) và bảng
  phát âm re-pin `baseSha` 6f2b465 → 6f79853 theo baseline owner mới.
- Câu hỏi staging (KHÔNG phải khuyết điểm của mix, không chặn mix): timing
  manifest ghi thoại S03 `onscreen: true` cho Trưởng đoàn, nhưng keyframe
  S03 và clip runtime tại 15 s chỉ có Ly An ở cổng mở; Trưởng đoàn chỉ xuất
  hiện trong S02. Câu thoại vì vậy phát trên shot Ly An đang đợi ở cổng —
  đọc như voice-over hay lệch staging là quyết định của đạo diễn/Codex, đã
  ghi trong manifest mix + báo cáo này, không dời VO để che.

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_47_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin013_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; playback metadata 14 embedded / 7 silent; pronunciation
  fallback files 140; counts khác chỉ đúng 6 thay đổi kỳ vọng so với CP46).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_47_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **620** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 23 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f79853`, head commit
  nội dung `33a4811`): **1286 paths, 1 violation** — `.gitattributes`, nhưng
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner mới sau PR #128); tool vẫn liệt kê vì nó diff từ merge-base
  `cf17178` (merge PR #117), nơi file chưa có 12 dòng LF của PR #127. Audit
  riêng nội dung CP47 (base `b14d7de`, head `33a4811`): **18 paths, 0 violations**.
- Commit nội dung: `33a4811` (18 file: 1 tool mix mới + 6 tool mở rộng +
  2 file mix nguồn + 1 file mix runtime + 2 file video mux lại + 4 manifest
  runtime + 1 export manifest + 1 bảng phát âm). File WAV/OGV/MP4 commit
  dưới dạng LFS pointer (quy tắc `.gitattributes` đã merge qua PR #127;
  mix runtime trùng SHA với mix nguồn nên LFS chỉ thêm 1 object).

## 3. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho mix này và toàn bộ shortlist;
  mọi số LUFS/TP là đo từ byte, không phải PASS nghe tai. Mix vẫn
  DRAFT_MIX_NOT_FINAL; stem assignment PROPOSED; vị trí stinger PROPOSED
  chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; clip vẫn là Ken Burns trên
  still storyboard, không phải final pose animation. Câu hỏi staging S03
  (Trưởng đoàn `onscreen: true` nhưng keyframe chỉ có Ly An) chờ đạo
  diễn/Codex — không dời VO, không sửa timing trong checkpoint này.
- Mix này là mix yên nhất trong các mix cảnh từ trước tới nay (−25,87 LUFS,
  so với −25,60 LUFS của CIN_012): take VO CP17 yên (−22,51 LUFS) kéo cả
  mix xuống; VO giữ unity theo công thức, không chuẩn hóa. Nếu Codex thấy
  mix quá yên so với các cảnh khác, quyết định chuẩn hóa thuộc về
  adapter/Codex ở PR review — không tự đổi công thức trong checkpoint này.
- Build mix KHÔNG bit-deterministic giữa các lần chạy (ghi nhận ở checkpoint
  39: cùng công thức, cùng code, hai lần chạy liên tiếp cho hai SHA khác
  nhau trong khi LUFS/TP đo được giống hệt — chưa điều tra sâu vì không ảnh
  hưởng deliverable; lần này chỉ build một lần, file giao là
  `9851c8e3…` và mọi manifest đều ghi đúng SHA đó — kiểm chứng sha-vs-file
  PASS; build lại sau này phải re-verify manifest, không copy SHA cũ).
- Sự cố API lượt này (đã xử lý, không ảnh hưởng deliverable): lần đọc đầu
  PR #119 qua public API trả về JSON lỗi rate-limit thoáng qua nên parser
  đọc được `state: None`; đã đọc lại thành công và khớp `git ls-remote`
  (head `b14d7de`, 89 commit / 1282 file, mergeable true / clean). Ghi chú
  cho các lượt sau: khi API public trả về lỗi, đọc lại thay vì kết luận
  trạng thái PR đã đổi.
- Mô tả PR #119 vẫn ở checkpoint 01–46; cập nhật lên CP01–47 + ACK
  CP47 cần thẻ duyệt của chủ dự án qua luồng chính (không tự ghi
  qua connector). Payload CP47 đã soạn (gộp CP47 vào bản CP01–46, kèm
  chỉnh số runtime 617 → 620 file và trạng thái mergeable mới).
- PR #119 mergeable TRUE/CLEAN — nhưng Muse không tự merge; Codex
  review/merge. 7 cảnh còn im lặng: CIN_014–020 (WO37 checkpoint lớn 1:
  còn 7 mix).
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo cùng công thức (ứng viên gần nhất CIN_014: take VO CP17 đã
có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo setting của
cảnh tại thời điểm làm — khi thêm mix, nhớ cập nhật cả 4 map trong
`build_pronunciation_table_v1.py` VÀ các assert đếm trong
`validate_media_deliveries.py`), hoặc cập nhật mô tả PR #119 lên CP01–47
+ ACK CP47 (khi chủ dự án duyệt), hoặc M8 QA khi integration di
chuyển / PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
