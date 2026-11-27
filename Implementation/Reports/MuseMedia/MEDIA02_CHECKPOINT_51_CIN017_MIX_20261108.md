# MEDIA-02 CHECKPOINT 51 — Mix nháp CIN_017 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f79853`
(trước checkpoint: head `973d5a2`, checkpoint 50. Đầu lượt: issue #116 vẫn 18 comment,
mới nhất vẫn là comment Codex 6716052477 (2026-11-08 11:14 JST, giao MEDIA-03→05
theo Work Order 37) — KHÔNG có chỉ đạo mới kể từ checkpoint 50; integration vẫn
`6f79853`, không di chuyển; PR #119 OPEN, head trước push lượt này `973d5a2`,
mergeable true, mergeable_state `clean`, 97 commit / 1310 file, mô tả live vẫn
CP01–45 (18214 ký tự, xác minh qua API lượt này);
cập nhật mô tả lên CP01–51 + ACK CP51 đã soạn trong lượt này, chờ chủ dự án duyệt,
KHÔNG đăng trong lượt này. Payload CP46 + CP47 + CP48 + CP49 + CP50 chưa từng được
bấm, nay bị thay thế — không đăng. Lưu ý: API PR #119 báo base sha `f383233`
trong khi `git ls-remote` đo tip integration là `6f79853` (merge PR #128) —
base sha của API là giá trị cache/cũ, không ảnh hưởng mergeable; audit scope
vẫn chạy trên `6f79853` như các checkpoint 47–50.)

## 0. Chỉ đạo / baseline

- Không có chỉ đạo mới trên issue #116 kể từ checkpoint 50. Tiếp tục WO37
  checkpoint lớn 1 (M-B): hoàn soundtrack cho các cảnh còn im lặng — sau
  checkpoint này còn 3 cảnh: CIN_018–020.
- Baseline integration không đổi `6f79853` (PR #128 đã merge). PR #119 vẫn
  **MERGEABLE** — xác minh qua GitHub API trong lượt này trước push:
  state open, mergeable true, mergeable_state `clean`, head `973d5a2`,
  97 commit / 1310 file; mô tả live vẫn CP01–45 (18214 ký tự).
- Scope audit vs baseline `6f79853`: **1314 paths, 1 violation**
  (`.gitattributes`) — vẫn chỉ là artifact merge-base như CP50:
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner). Audit riêng nội dung CP51 (base `973d5a2`, head
  `67d8478`): **18 paths, 0 violations**.

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_017 ("Lõi và dòng triều", 18 s) — mix cảnh thứ mười bốn sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1 (checkpoint 38),
CIN_007 v1 (checkpoint 39), CIN_008 v1 (checkpoint 40), CIN_009 v1 (checkpoint 41),
CIN_010 v1 (checkpoint 42), CIN_011 v1 (checkpoint 45), CIN_012 v1 (checkpoint 46),
CIN_013 v1 (checkpoint 47), CIN_014 v1 (checkpoint 48), CIN_015 v1 (checkpoint 49)
và CIN_016 v1 (checkpoint 50), cùng công thức P0 v3 — và nhúng vào runtime OGV +
review MP4 của cảnh. Cả 18 cảnh campaign có mix nhúng nay là P0 (CIN_001/002/004) +
CIN_006 + CIN_003 + CIN_005 + CIN_007 + CIN_008 + CIN_009 + CIN_010 + CIN_011 +
CIN_012 + CIN_013 + CIN_014 + CIN_015 + CIN_016 + CIN_017 (prologue CIN_000 tính
riêng; pack runtime nay 18 cảnh gồm prologue).

- `Tools/MediaProduction/Muse/build_cin017_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_017; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/bach_uyen` + ambience `AMBIENCE/underwater` + stinger
  `SFX/CINEMA/reveal` tại 6,0 s (đầu S02, PROPOSED chờ picture lock, theo mẫu
  CIN_004/CIN_006/CIN_015) + VO take CP17
  `VO_CIN_017_S03_DIVERLEAD_draft_v1.wav` tại 12,5 s. Tất cả stem đều
  composed (CP26/CP30), không còn stem ported nào trong mix.
  `bach_uyen` là dạng low-pass dưới nước (850 Hz) của bộ nhạc sáng tác —
  cue đúng setting cho cảnh rắn triều quấn quanh lõi pha lê trong nước
  (S01: sân đền đổ ngập nước ban đêm, rắn triều màu ngọc lam quấn quanh
  lõi pha lê giữa nước, WIDE_STATIC; S02: chi tiết rắn quấn quanh viên
  pha lê phát sáng trên trụ đá, bọt khí nổi lên, DETAIL_LOCKED; S03:
  hẻm sông mù, đồ nghề đánh cá trên bờ và dòng nước tối hình rắn uốn
  xuống sông, WIDE_STATIC; theo đúng keyframe CIN_017 S01/S02/S03).
  `underwater` là giường nước cho mặt nước bao cả ba shot. Cả hai đều là
  lần dùng thứ hai trong mix cảnh — cùng cặp đã dùng cho CIN_015 (thành
  phố chìm), cảnh nước ngay trước đó; việc tái dùng được ghi rõ, không
  giấu, vì hai cảnh cùng một chương nước và bộ cue chỉ có một dạng nước.
  Khác CIN_015 ở chủ thể, không ở nước: CIN_015 là thị trấn chìm có thợ
  lặn ở S03; CIN_017 là rắn triều giữ lõi, và người nói ở S03 là
  off-screen (xem ghi chú staging). `boss_mang_cot` đã bỏ qua: nhạc boss
  của SAI boss (Mãng Cốt, không phải Rắn Triều) — và nhịp này là một câu
  thoại yên tĩnh, không phải trận boss. `quiet_discovery` đã bỏ qua:
  khoảng lặng khám phá, vừa dùng cho CIN_016 (nội thất yên, sai setting
  cho cảnh rắn/triều). `lam_trieu` đã bỏ qua: sáo đồng quê, dùng cho
  CIN_013. `tran_son` đã bỏ qua: dạng chuông-cổng, dùng cho CIN_008 và
  CIN_012. `ben_mua` đã bỏ qua: leitmotif bến mưa, dùng cho CIN_014.
  `thang_long` là dạng kinh thành (sai setting); `sa_hoa` là dạng sa mạc
  khô (sai setting); `rift_finale` là cái kết đầy đủ duy nhất của bộ
  (finale, sai cho nhịp giữa chapter). Ambience: `river_shore` đã bỏ
  qua: giường mép nước, dùng cho CIN_003/CIN_008 — S01/S02 đặt con rắn
  TRONG nước, không phải ở mép nước; riêng bờ sông S03 không gánh được
  cảnh. `waterfall` dùng cho CIN_009; `mountain_wind` dùng cho CIN_013;
  `forge` dùng cho CIN_012; `rain_light`/`rain_heavy` là giường mưa,
  nhưng không có mưa trong cả ba keyframe (đền ngập ban đêm, pha lê
  trong nước, hẻm mù — không vệt mưa); `cave_drips` là hang;
  `desert_wind`, `city_night`, `thang_long_crowd`, `rift` đều sai setting.
- Điểm khác CIN_016 (nói thẳng): take VO CIN_017 KHỚP cửa sổ với dư 1,832 s —
  take 3,168 s, chạy 12,5–15,668 s, kết thúc 1,832 s TRƯỚC cuối cửa sổ 17,5 s
  và 2,332 s trước cuối cảnh 18,00 s. Không overrun, không tail trim. Cửa sổ
  là uniform 12,5–17,5 s, KHÔNG nới; take và timing không bị sửa để che giấu
  gì. (Câu thoại 44 ký tự, 8,80 ký tự/giây trên cửa sổ 5 s — thời lượng take
  đo từ byte thật, CP17 ghi windowFit FITS, không tăng tốc.)
- Ducking −4,85 dB trong cửa sổ VO (0,0 dB ngoài cửa sổ) — là mức dìm thật,
  không phải số 0,0 dB kiểu CIN_016: `bach_uyen` KHÔNG im lặng trong cửa sổ
  này (ở CIN_015 nó cũng cho mức dìm −6,87 dB); mức −4,85 dB nông hơn
  CIN_015 vì cue yên hơn trong cửa sổ này — cùng tham số compressor, đo từ
  byte thật, không chỉnh lại. Validator khẳng định độ sâu trong cửa sổ < 0
  (mức dìm thật bắt buộc, theo mẫu `check_cin015_mix`, không áp dụng
  assert im lặng của `check_cin016_mix` cho cue này).
- `Art_Source/Audio/Muse/MIX/CIN017_DRAFT_V1/CIN_017_mix_draft_v1.wav` +
  `CIN017_MIX_V1_manifest_v1.json`: mix 18,000 s, −24,63 LUFS / −2,44 dBTP,
  LRA 10,30 LU, peak trim 0,00 dB; ducking nhạc −4,85 dB trong cửa sổ VO,
  0,0 dB ngoài cửa sổ; loop join ambience tại 15,5 s, tỉ lệ jump/P999 =
  0,593. Ba stem đo lại từ byte thật khớp đúng bảng pack (bach_uyen −21,96;
  underwater −33,11; reveal −24,96 LUFS). Take VO CP17 đo lại −22,33 LUFS;
  VO giữ unity theo công thức, không đổi gain — ghi rõ, không chuẩn hóa lén
  (cùng lý do như CIN_007/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/
  CIN_015/CIN_016).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin017_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_017 mux lại bằng `build_runtime_pack_goi31.py` (đã mở
  rộng cho CIN_017) với audio nhúng (video copy bit-for-bit: MP4 540 frame,
  OGV 506 frame stored, không đổi; MD5 video stream khớp đúng bản gốc —
  MP4 aedbd686… / OGV 84f9f411…, đo độc lập từ file pre-mux trong git;
  OGV Vorbis 160k −24,64 LUFS / −2,70 dBTP; MP4 AAC 192k −24,64 LUFS /
  −2,42 dBTP — đo lại từ byte đã encode, lệch ≤0,01 LUFS so với mix nguồn;
  metadata comment CP51 trong cả hai file). Các cảnh CP34/CP37/CP38/CP39/
  CP40/CP41/CP42/CP45/CP46/CP47/CP48/CP49/CP50 (CIN_001/002/004/006/003/005/
  007/008/009/010/011/012/013/014/015/016) chỉ được verify lại, không mux lại
  (LUFS khớp đúng bản ghi CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/
  CP48/CP49/CP50).
- `RUNTIME_PACK_GOI31_v1.json` nay có 18 cảnh (thêm CIN_017); manifest
  audio runtime 623 → 624 file (mix 26 → 27); manifest cinematics cập nhật
  checkpoint 51; export manifest CIN_017 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Playback metadata + bảng phát âm CHẠY LẠI cho mix nhúng mới (theo đúng ghi
  chú CP44: khi một cảnh được nhúng mix, chạy lại builder để fallback cập
  nhật): `PLAYBACK_METADATA_v1.json` nay 18 embedded / 3 silent
  (CIN_018–020), builder PASS 0 mismatches; `PRONUNCIATION_TABLE_v1.json`
  nay 24 playback cue rows (18 embedded + 6 P0 v1/v2 alternates), 22 seam
  rows (1 flagged, không đổi — MUSIC/sa_hoa 0,016015; KHÔNG có hàng seam
  MỚI — MUSIC/bach_uyen + AMBIENCE/underwater đã có trong bảng từ mix cảnh
  CIN_015), 21 fallback rows, 160 file kiểm chứng (tăng từ 155); cue
  CIN_017: head/tail 0,0 s, slack +1,832 s, ducking −4,85 dB; fallback
  CIN_017: EMBEDDED_SOUNDTRACK → mix WAV → stems+VO → VO+SRT → SRT-only.
  Ba builder được mở rộng theo đúng tiền lệ CP50
  (`build_playback_metadata_v1.py`: nhãn checkpoint 51;
  `build_pronunciation_table_v1.py`: map `cin017` + `CIN_017` ở cả 4 bảng
  tra, chuỗi "CIN_017-020" → "CIN_018-020", nhãn checkpoint 51) và
  validator mở rộng theo tiền lệ (`check_cin017_mix` mới theo mẫu
  `check_cin015_mix` — khẳng định mức dìm thật < 0, không assert im lặng —
  + assert playbackCueRows 23 → 24, assert runtime total 623 → 624,
  chuỗi checkpoint 51, mục CIN_017 trong notes). Tool
  `verify_runtime_delivery.py` cũng mở rộng theo tiền lệ (chuỗi "verifies"
  thêm mục checkpoint 51).
- Staging (KHÔNG phải khuyết điểm của mix, không chặn mix): giống CIN_015,
  người nói KHÔNG NHẬN DIỆN ĐƯỢC ở đây — và lần này timing manifest tự
  nói rõ: thoại S03 `onscreen: null` cho Đội trưởng thợ lặn
  (NPC_DIVER_LEAD). Keyframe S03 chỉ cho thấy hẻm sông mù — tre, giỏ và
  sào đánh cá trên bờ, dòng nước tối hình rắn uốn xuống sông — không có
  bóng thợ lặn nào trong khung. S01 cho thấy rắn triều (BOSS_TIDE_SERPENT)
  không có người; S02 chỉ có rắn và pha lê. Câu thoại "Mang lõi đi thì
  phải giữ đường nước còn lại." được đọc off-screen, như giọng Ly An
  trong CIN_004 (DEC-MEDIA-P0 Q2) — việc của final picture/character
  lock, không phải lỗi mix; mix không dời VO để che. (Ghi chú staging
  trong script mix đã viết đúng sự thật này TRƯỚC khi mux.)

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_51_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin017_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; playback metadata 18 embedded / 3 silent; pronunciation
  cue rows 24 / seam rows 22 / fallback files 160; counts khác chỉ đúng 7
  thay đổi kỳ vọng so với CP50: cin017 files checked, embedded 17→18,
  silent 4→3, cue rows 23→24, fallback files 155→160, runtime audio
  total 623→624, mix 26→27; seam rows giữ 22).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_51_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **624** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 27 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file. (Chuỗi "checkpoint" trong JSON này vẫn mang nhãn CP44 cũ —
  quirk có sẵn của tool, giống file CP50; verdict PASS và các số đếm mới
  là bằng chứng kiểm chứng.)
- Scope audit (`check_agent_scope.py`, base integration `6f79853`, head commit
  nội dung `67d8478`): **1314 paths, 1 violation** — `.gitattributes`, nhưng
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner sau PR #128); tool vẫn liệt kê vì nó diff từ merge-base
  `cf17178` (merge PR #117), nơi file chưa có 12 dòng LF của PR #127. Audit
  riêng nội dung CP51 (base `973d5a2`, head `67d8478`): **18 paths, 0 violations**.
- Commit nội dung: `67d8478` (18 file: 1 tool mix mới + 6 tool mở rộng +
  2 file mix nguồn + 1 file mix runtime + 2 file video mux lại + 4 manifest
  runtime (audio, playback metadata, cinematics, pack) + 1 export manifest
  + 1 bảng phát âm).
  File WAV/OGV/MP4 commit dưới dạng LFS pointer (quy tắc `.gitattributes` đã
  merge qua PR #127; mix runtime trùng SHA với mix nguồn nên LFS chỉ thêm
  1 object). Push đã xác minh qua `git ls-remote`: remote head `67d8478`,
  3 object LFS upload (mix WAV 1 object dùng chung 2 path + OGV + MP4).
- PR #119 sau push: remote head `67d8478`, 98 commit / 1314 file (đếm ba
  chấm từ merge-base `cf17178`, khớp đúng số audit 1314 paths). Trạng thái
  mergeable sau push CHƯA đọc tươi được qua API trong lượt này: trang API
  PR #119 vẫn phục vụ bản crawl 08:04 UTC (trước push ~08:06 UTC) với head
  cũ `973d5a2`; mergeable trước push đã xác minh là true / `clean`. Push
  này chỉ thêm file media, không đụng `.gitattributes`, nên không tạo thêm
  xung đột mới — nhưng con số mergeable_state mới cần luồng chính đọc lại
  sau khi cache API làm mới. Mô tả live vẫn CP01–45 (18214 ký tự).
  Commit báo cáo checkpoint này được push sau, riêng.
- Sự cố thao tác trong lượt này (đã sửa, không ảnh hưởng kết quả):
  (1) Lần chạy đầu của `build_runtime_delivery.py` làm rớt CIN_016 khỏi
  manifest audio runtime: anchor thay thế trong script đã nuốt mất 2 dòng
  `audio_entries.append(entry)` + `counts["mix"] += 1` của block CIN_016,
  nên tổng vẫn 623 (CIN_016 ra, CIN_017 vào) và manifest thiếu CIN_016.
  Phát hiện vì tổng không tăng và kiểm trực tiếp thấy CIN_016 vắng trong
  manifest; đã khôi phục đúng 2 dòng, chạy lại builder, manifest cuối
  624 file với cả CIN_016 và CIN_017 hiện diện, 0 FAIL. Bài học: khi chèn
  block mới vào builder bằng thay thế anchor, anchor phải KHÔNG chứa code
  của block cũ — chỉ chứa tiêu đề section tiếp theo.
  (2) Kiểm MD5 video stream độc lập lần đầu thất bại vì `git show HEAD:`
  trả về LFS pointer (132/131 byte, "moov atom not found") khi
  `GIT_LFS_SKIP_SMUDGE=1`; đã fetch chọn lọc 2 object LFS của CIN_017
  rồi smudge ra /tmp — MD5 khớp cả hai file. Không file working tree nào
  bị ghi đè trong quá trình này.

## 3. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho mix này và toàn bộ shortlist;
  mọi số LUFS/TP là đo từ byte, không phải PASS nghe tai. Mix vẫn
  DRAFT_MIX_NOT_FINAL; stem assignment PROPOSED; vị trí stinger PROPOSED
  chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; clip vẫn là Ken Burns trên
  still storyboard, không phải final pose animation. Người nói S03
  off-screen (onscreen: null, không có bóng thợ lặn trong keyframe) chờ
  character lock / đạo diễn — không dời VO, không sửa timing trong
  checkpoint này.
- Cặp stem bach_uyen + underwater nay dùng lần thứ hai (CIN_015 rồi
  CIN_017): hai cảnh cùng chương nước nên tái dùng là có lý, nhưng nếu
  Codex/đạo diễn muốn phân biệt rõ hơn hai cảnh nước kề nhau, quyết định
  thuộc về adapter ở PR review (đổi stem là thay đổi công thức, không tự
  làm trong checkpoint này).
- Build mix KHÔNG bit-deterministic giữa các lần chạy (ghi nhận ở checkpoint
  39 và xác nhận lại ở checkpoint 48/50: cùng công thức, cùng code, hai lần
  chạy liên tiếp cho hai SHA khác nhau trong khi LUFS/TP đo được giống hệt —
  build lại sau này phải re-verify manifest, không copy SHA cũ).
- Mô tả PR #119 vẫn ở checkpoint 01–45; cập nhật lên CP01–51 + ACK
  CP51 cần thẻ duyệt của chủ dự án qua luồng chính (không tự ghi
  qua connector). Payload CP51 đã soạn (gộp CP51 vào bản CP01–50, kèm
  chỉnh số runtime 623 → 624 file và trạng thái mergeable mới).
- PR #119 mergeable TRUE (mergeable_state `clean`) — nhưng Muse không tự
  merge; Codex review/merge. 3 cảnh còn im lặng: CIN_018–020 (WO37
  checkpoint lớn 1: còn 3 mix).
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo cùng công thức (ứng viên gần nhất CIN_018: take VO CP17 đã
có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo setting của
cảnh tại thời điểm làm — khi thêm mix, nhớ cập nhật cả 4 map trong
`build_pronunciation_table_v1.py` VÀ các assert đếm trong
`validate_media_deliveries.py`), hoặc cập nhật mô tả PR #119 lên CP01–51
+ ACK CP51 (khi chủ dự án duyệt), hoặc M8 QA khi integration di
chuyển / PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
