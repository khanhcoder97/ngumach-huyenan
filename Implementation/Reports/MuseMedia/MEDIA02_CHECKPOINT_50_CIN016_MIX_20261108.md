# MEDIA-02 CHECKPOINT 50 — Mix nháp CIN_016 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f79853`
(trước checkpoint: head `22afdab`, checkpoint 49. Đầu lượt: issue #116 vẫn 18 comment,
mới nhất vẫn là comment Codex 6716052477 (2026-11-08 11:14 JST, giao MEDIA-03→05
theo Work Order 37) — KHÔNG có chỉ đạo mới kể từ checkpoint 49; integration vẫn
`6f79853`, không di chuyển; PR #119 OPEN, head sau push lượt này `38b91b0`
(commit nội dung; commit báo cáo push sau, riêng), mô tả live vẫn ở CP01–45
(18214 ký tự, xác minh qua API lượt này);
cập nhật mô tả lên CP01–50 + ACK CP50 đã soạn trong lượt này, chờ chủ dự án duyệt,
KHÔNG đăng trong lượt này. Payload CP46 + CP47 + CP48 + CP49 chưa từng được bấm,
nay bị thay thế — không đăng.)

## 0. Chỉ đạo / baseline

- Không có chỉ đạo mới trên issue #116 kể từ checkpoint 49. Tiếp tục WO37
  checkpoint lớn 1 (M-B): hoàn soundtrack cho các cảnh còn im lặng — sau
  checkpoint này còn 4 cảnh: CIN_017–020.
- Baseline integration không đổi `6f79853` (PR #128 đã merge). PR #119 vẫn
  **MERGEABLE** — xác minh qua GitHub API trong lượt này trước push:
  state open, mergeable true, mergeable_state `clean`, head `22afdab`,
  95 commit / 1303 file; mô tả live vẫn CP01–45 (18214 ký tự).
- Scope audit vs baseline `6f79853`: **1307 paths, 1 violation**
  (`.gitattributes`) — vẫn chỉ là artifact merge-base như CP49:
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner). Audit riêng nội dung CP50 (base `22afdab`, head
  `38b91b0`): **18 paths, 0 violations**.

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_016 ("Quyền được kể lại", 18 s) — mix cảnh thứ mười ba sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1 (checkpoint 38),
CIN_007 v1 (checkpoint 39), CIN_008 v1 (checkpoint 40), CIN_009 v1 (checkpoint 41),
CIN_010 v1 (checkpoint 42), CIN_011 v1 (checkpoint 45), CIN_012 v1 (checkpoint 46),
CIN_013 v1 (checkpoint 47), CIN_014 v1 (checkpoint 48) và CIN_015 v1 (checkpoint 49),
cùng công thức P0 v3 — và nhúng vào runtime OGV + review MP4 của cảnh. Cả 17 cảnh
campaign có mix nhúng nay là P0 (CIN_001/002/004) + CIN_006 + CIN_003 + CIN_005 +
CIN_007 + CIN_008 + CIN_009 + CIN_010 + CIN_011 + CIN_012 + CIN_013 + CIN_014 +
CIN_015 + CIN_016 (prologue CIN_000 tính riêng; pack runtime nay 17 cảnh gồm prologue).

- `Tools/MediaProduction/Muse/build_cin016_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_016; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/quiet_discovery` + ambience `AMBIENCE/wind_canopy` + stinger
  `SFX/CINEMA/reveal` tại 6,0 s (đầu S02, PROPOSED chờ picture lock, theo mẫu
  CIN_004/CIN_006/CIN_007) + VO take CP17
  `VO_CIN_016_S03_HAMAC_draft_v1.wav` tại 12,5 s. Tất cả stem đều
  composed (CP26/CP30), không còn stem ported nào trong mix.
  `quiet_discovery` là khoảng lặng khám phá của bộ nhạc sáng tác (solo flute
  fragments + single bells, long near-silences, water drops, 60 BPM) — cue
  đúng setting cho cuộc trò chuyện yên tĩnh trong phòng đọc về việc ghi lại
  câu chuyện của người khác ("Tôi có thể ghi lại phần ông muốn kể không?"):
  S01 chi tiết bản thảo cũ trên bàn dưới đèn treo, nghiên mực và bút,
  DETAIL_LOCKED; S02 người áo lam ở bàn và một bóng áo choàng có mũ trùm
  nhìn từ sau lưng, MEDIUM_STATIC; S03 Hạ Mặc áo lục, khăn đầu xanh lá,
  tay cầm bút viết vào sổ khi hỏi người lớn tuổi đối diện, DETAIL_LOCKED
  (theo đúng keyframe CIN_016 S01/S02/S03). `wind_canopy` là giường gió
  qua tán cây (gusted band noise + leaf rustle) cho cây xanh ngoài cửa sổ
  S03 và vách tre + thảo mộc treo trong phòng. Cả hai đều là lần dùng thứ
  ba trong mix cảnh (cùng cặp ở CIN_007 và CIN_011; wind_canopy thêm ở
  CIN_014) — không phải lần đầu. `ben_mua` đã bỏ qua: leitmotif bến mưa,
  dùng cho CIN_014. `lam_trieu` đã bỏ qua: sáo đồng quê, dùng cho CIN_013.
  `tran_son` đã bỏ qua: dạng chuông-cổng, dùng cho CIN_008 và CIN_012.
  `bach_uyen` đã bỏ qua: dạng low-pass dưới nước, vừa dùng cho CIN_015
  (sai setting — phòng này khô). `thang_long` là dạng kinh thành
  (sai setting); `sa_hoa` là dạng sa mạc khô (sai setting); `rift_finale`
  là cái kết đầy đủ duy nhất của bộ (finale, sai cho nhịp giữa chapter);
  `boss_mang_cot` là nhạc boss. Ambience: `underwater` vừa dùng cho
  CIN_015 (thành phố chìm, sai setting); `mountain_wind` dùng cho CIN_013;
  `forge` dùng cho CIN_012; `river_shore` dùng cho CIN_003/CIN_008
  (mép nước, không phải nội thất); `waterfall` dùng cho CIN_009;
  `rain_light`/`rain_heavy` là giường mưa, nhưng không có mưa trong cả ba
  keyframe (nội thất khô có đèn, cây xanh ngoài cửa sổ, không vệt mưa);
  `cave_drips` là hang; `desert_wind`, `city_night`, `thang_long_crowd`,
  `rift` đều sai setting.
- Điểm khác CIN_015 (nói thẳng): take VO CIN_016 KHỚP cửa sổ với dư 2,528 s —
  take 2,472 s, chạy 12,5–14,972 s, kết thúc 2,528 s TRƯỚC cuối cửa sổ 17,5 s
  và 3,028 s trước cuối cảnh 18,00 s. Không overrun, không tail trim. Cửa sổ
  là uniform 12,5–17,5 s, KHÔNG nới; take và timing không bị sửa để che giấu
  gì. (Câu thoại 42 ký tự, 8,40 ký tự/giây trên cửa sổ 5 s — thời lượng take
  đo từ byte thật, CP17 ghi windowFit FITS, không tăng tốc.)
- Ducking 0,0 dB — KHÔNG phải compressor hỏng, đã chứng minh bằng byte thật
  (phương pháp CP39 giữ nguyên để các mix so sánh được với nhau):
  `quiet_discovery` im lặng số (digital silence) từ 12 s đến 15 s
  (RMS −120 dB floor, đo từ stem thật), nên cửa sổ VO 12,5–14,972 s nằm
  trọn trong khoảng lặng giữa hai fragment của cue; sidechain compressor
  (cùng tham số mọi mix: threshold 0,03, ratio 4, attack 15 ms, release
  350 ms) không có tín hiệu để dìm, bus đã duck giống hệt bus chưa duck
  trong cửa sổ. Hai mix `quiet_discovery` trước cho thấy mức dìm thật
  (CIN_007 −9,43 dB, CIN_011 −10,79 dB) vì cửa sổ dài hơn, kéo qua 15 s
  tới fragment tiếp theo. VO nằm trong túi lặng theo đúng thiết kế của
  cue — không đổi công thức, không đổi stem, không đổi gain để tạo số.
  Validator đã mở rộng cho trường hợp này (`check_cin016_mix`): ngoài việc
  khẳng định depth ghi trong manifest đúng 0,0, nó còn đo lại độc lập RMS
  của stem nhạc trong cửa sổ từ byte thật và bắt buộc im lặng
  (≤ −110 dBFS) — đo được −120,00 dBFS; nếu bed không lặng thì 0,0 dB sẽ
  là lỗi và check fail.
- `Art_Source/Audio/Muse/MIX/CIN016_DRAFT_V1/CIN_016_mix_draft_v1.wav` +
  `CIN016_MIX_V1_manifest_v1.json`: mix 18,000 s, −25,07 LUFS / −4,36 dBTP,
  LRA 13,30 LU, peak trim 0,00 dB; ducking nhạc 0,0 dB trong cửa sổ VO
  (khoảng lặng, xem trên), 0,0 dB ngoài cửa sổ; loop join ambience tại
  15,5 s, tỉ lệ jump/P999 = 0,765. Ba stem đo lại từ byte thật khớp đúng
  bảng pack (quiet_discovery −21,72; wind_canopy −29,70; reveal −24,96 LUFS).
  Take VO CP17 đo lại −21,92 LUFS; VO giữ unity theo công thức, không đổi
  gain — ghi rõ, không chuẩn hóa lén (cùng lý do như CIN_007/CIN_009/
  CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015).
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin016_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_016 mux lại bằng `build_runtime_pack_goi31.py` (đã mở
  rộng cho CIN_016) với audio nhúng (video copy bit-for-bit: MP4 540 frame,
  OGV 521 frame stored, không đổi; MD5 video stream khớp đúng bản gốc —
  MP4 65658541… / OGV 5725886c…, đo độc lập từ file pre-mux trong git;
  OGV Vorbis 160k −25,07 LUFS / −4,50 dBTP; MP4 AAC 192k −25,08 LUFS /
  −4,38 dBTP — đo lại từ byte đã encode, lệch ≤0,01 LUFS so với mix nguồn;
  metadata comment CP50 trong cả hai file). Các cảnh CP34/CP37/CP38/CP39/
  CP40/CP41/CP42/CP45/CP46/CP47/CP48/CP49 (CIN_001/002/004/006/003/005/007/
  008/009/010/011/012/013/014/015) chỉ được verify lại, không mux lại
  (LUFS khớp đúng bản ghi CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/
  CP47/CP48/CP49).
- `RUNTIME_PACK_GOI31_v1.json` nay có 17 cảnh (thêm CIN_016); manifest
  audio runtime 622 → 623 file (mix 25 → 26); manifest cinematics cập nhật
  checkpoint 50; export manifest CIN_016 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Playback metadata + bảng phát âm CHẠY LẠI cho mix nhúng mới (theo đúng ghi
  chú CP44: khi một cảnh được nhúng mix, chạy lại builder để fallback cập
  nhật): `PLAYBACK_METADATA_v1.json` nay 17 embedded / 4 silent
  (CIN_017–020), builder PASS 0 mismatches; `PRONUNCIATION_TABLE_v1.json`
  nay 23 playback cue rows (17 embedded + 6 P0 v1/v2 alternates), 22 seam
  rows (1 flagged, không đổi — MUSIC/sa_hoa 0,016015; KHÔNG có hàng seam
  MỚI — MUSIC/quiet_discovery + AMBIENCE/wind_canopy đã có trong bảng từ
  các mix cảnh CIN_007/CIN_011/CIN_014), 21 fallback rows, 155 file kiểm
  chứng (tăng từ 150); cue CIN_016: head/tail 0,0 s, slack +2,528 s,
  ducking 0,0 dB, VO take lead silence 0,165 s / tail silence 0,255 s;
  fallback CIN_016: EMBEDDED_SOUNDTRACK → mix WAV → stems+VO → VO+SRT →
  SRT-only. Ba builder được mở rộng theo đúng tiền lệ CP49
  (`build_playback_metadata_v1.py`: nhãn checkpoint 50;
  `build_pronunciation_table_v1.py`: map `cin016` + `CIN_016` ở cả 4 bảng
  tra, chuỗi "CIN_016-020" → "CIN_017-020", nhãn checkpoint 50) và
  validator mở rộng theo tiền lệ (`check_cin016_mix` mới + helper đo RMS
  đoạn `_segment_rms_db`, assert playbackCueRows 22 → 23, assert runtime
  total 622 → 623, chuỗi checkpoint 50, mục CIN_016 trong notes).
- Staging (KHÔNG phải khuyết điểm của mix, không chặn mix): khác CIN_015,
  người nói NHẬN DIỆN ĐƯỢC rõ ở đây — timing manifest ghi thoại S03
  `onscreen: true` cho Hạ Mặc (NPC_HA_MAC) và keyframe S03 cho thấy ông rõ
  ràng: mặt nghiêng, khăn đầu xanh lá, áo lục, tay cầm bút viết vào sổ,
  đang hỏi người áo lam đối diện. S01 là chi tiết bản thảo dưới đèn, không
  có nhân vật. S02 cho thấy người áo lam ở bàn cùng một bóng áo choàng có
  mũ trùm nhìn từ sau lưng, đeo ba lô — bóng đó có phải Hạ Mặc đang đến
  hay không là câu hỏi continuity cho final picture (S03 Hạ Mặc đeo nón
  lá đan tròn sau lưng; nhân vật S02 đeo ba lô chữ nhật) — việc của
  final picture/character lock, không phải lỗi mix; mix không dời VO để
  che. (Ghi chú staging trong script mix đã viết đúng sự thật này TRƯỚC
  khi mux.)

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_50_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin016_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; playback metadata 17 embedded / 4 silent; pronunciation
  cue rows 23 / seam rows 22 / fallback files 155; counts khác chỉ đúng 7
  thay đổi kỳ vọng so với CP49: cin016 files checked, embedded 16→17,
  silent 5→4, cue rows 22→23, fallback files 150→155, runtime audio
  total 622→623, mix 25→26; seam rows giữ 22). Lần chạy đầu của validator
  báo 1 mismatch (`SCENE-CLIPS CIN_016: runtime manifest files != export
  manifest files`) vì `build_runtime_delivery.py` đã chạy TRƯỚC pack builder
  nên manifest cinematics còn SHA video pre-mux; đã chạy lại delivery sau
  pack theo đúng thứ tự CP34 (`mix -> pack -> delivery`) rồi chạy lại
  validator — PASS. Đây là lỗi thứ tự chạy, không phải lỗi dữ liệu.
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_50_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **623** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 26 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file.
- Scope audit (`check_agent_scope.py`, base integration `6f79853`, head commit
  nội dung `38b91b0`): **1307 paths, 1 violation** — `.gitattributes`, nhưng
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner sau PR #128); tool vẫn liệt kê vì nó diff từ merge-base
  `cf17178` (merge PR #117), nơi file chưa có 12 dòng LF của PR #127. Audit
  riêng nội dung CP50 (base `22afdab`, head `38b91b0`): **18 paths, 0 violations**.
- Commit nội dung: `38b91b0` (18 file: 1 tool mix mới + 6 tool mở rộng +
  2 file mix nguồn + 1 file mix runtime + 2 file video mux lại + 4 manifest
  runtime + 1 export manifest + 1 bảng phát âm). File WAV/OGV/MP4 commit
  dưới dạng LFS pointer (quy tắc `.gitattributes` đã merge qua PR #127;
  mix runtime trùng SHA với mix nguồn nên LFS chỉ thêm 1 object). Push đã
  xác minh qua `git ls-remote`: remote head `38b91b0`, 3 object LFS upload
  (mix WAV 1 object dùng chung 2 path + OGV + MP4).
- PR #119 sau push (xác minh qua GitHub API trong lượt này): state open,
  mergeable true, mergeable_state `unstable` (trạng thái kiểm tra sau push
  mới, không phải xung đột — giống CP49; mergeable vẫn true), head `38b91b0`,
  96 commit / 1307 file (khớp đúng số audit); mô tả live vẫn CP01–45
  (18214 ký tự). Commit báo cáo checkpoint này được push sau, riêng.
- Không có sự cố thao tác trong lượt này ngoài lỗi thứ tự chạy delivery/pack
  đã sửa ở trên: không rm file LFS trước khi `git checkout` (bài học CP48
  đã áp dụng — mux bằng tool ngay từ đầu); mix giao là bản build thứ hai
  sau khi bổ sung ghi chú ducking vào script (build lại cho manifest mang
  đúng ghi chú; SHA đổi theo đúng tính không-bit-deterministic đã ghi ở
  checkpoint 39/48, LUFS/TP đo được giống hệt: −25,07/−4,36).

## 3. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho mix này và toàn bộ shortlist;
  mọi số LUFS/TP là đo từ byte, không phải PASS nghe tai. Mix vẫn
  DRAFT_MIX_NOT_FINAL; stem assignment PROPOSED; vị trí stinger PROPOSED
  chờ picture lock; VO vẫn bản nháp TTS.
- Final picture vẫn chờ keyframe/character lock; clip vẫn là Ken Burns trên
  still storyboard, không phải final pose animation. Continuity S02→S03
  (bóng áo choàng đeo ba lô có phải Hạ Mặc với nón lá đan hay không) chờ
  character lock / đạo diễn — không dời VO, không sửa timing trong
  checkpoint này.
- Ducking 0,0 dB là số đo đúng của khoảng lặng trong cue, không phải lỗi
  compressor — nhưng nếu Codex/đạo diễn muốn nhạc hiện diện rõ hơn trong
  cửa sổ VO của cảnh này, quyết định thuộc về adapter ở PR review (đổi stem
  hoặc đổi offset nhạc là thay đổi công thức, không tự làm trong checkpoint
  này).
- Build mix KHÔNG bit-deterministic giữa các lần chạy (ghi nhận ở checkpoint
  39 và xác nhận lại ở checkpoint 48/50: cùng công thức, cùng code, hai lần
  chạy liên tiếp cho hai SHA khác nhau trong khi LUFS/TP đo được giống hệt —
  build lại sau này phải re-verify manifest, không copy SHA cũ).
- Mô tả PR #119 vẫn ở checkpoint 01–45; cập nhật lên CP01–50 + ACK
  CP50 cần thẻ duyệt của chủ dự án qua luồng chính (không tự ghi
  qua connector). Payload CP50 đã soạn (gộp CP50 vào bản CP01–49, kèm
  chỉnh số runtime 622 → 623 file và trạng thái mergeable mới).
- PR #119 mergeable TRUE (mergeable_state `clean`) — nhưng Muse không tự
  merge; Codex review/merge. 4 cảnh còn im lặng: CIN_017–020 (WO37
  checkpoint lớn 1: còn 4 mix).
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo cùng công thức (ứng viên gần nhất CIN_017: take VO CP17 đã
có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo setting của
cảnh tại thời điểm làm — khi thêm mix, nhớ cập nhật cả 4 map trong
`build_pronunciation_table_v1.py` VÀ các assert đếm trong
`validate_media_deliveries.py`), hoặc cập nhật mô tả PR #119 lên CP01–50
+ ACK CP50 (khi chủ dự án duyệt), hoặc M8 QA khi integration di
chuyển / PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
