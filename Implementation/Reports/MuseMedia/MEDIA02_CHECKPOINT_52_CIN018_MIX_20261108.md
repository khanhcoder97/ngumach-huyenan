# MEDIA-02 CHECKPOINT 52 — Mix nháp CIN_018 v1 + nhúng vào runtime OGV/MP4

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f79853`
(trước checkpoint: head `d51e727`, checkpoint 51. Đầu lượt: issue #116 vẫn 18 comment,
mới nhất vẫn là comment Codex 6716052477 (2026-11-08 11:14 JST, giao MEDIA-03→05
theo Work Order 37) — KHÔNG có chỉ đạo mới kể từ checkpoint 51; integration vẫn
`6f79853`, không di chuyển; PR #119 OPEN, head trước push lượt này `d51e727`,
mergeable true, mergeable_state `clean`, 99 commit / 1317 file, mô tả live vẫn
CP01–45 (18214 ký tự, xác minh qua API lượt này);
cập nhật mô tả lên CP01–52 + ACK CP52 đã soạn trong lượt này, chờ chủ dự án duyệt,
KHÔNG đăng trong lượt này. Payload CP46 + CP47 + CP48 + CP49 + CP50 + CP51 chưa
từng được bấm, nay bị thay thế — không đăng. Lưu ý: API PR #119 lần này đã phục
vụ đúng head mới `d51e727` (cache đã làm mới sau push CP51); base sha API vẫn
`f383233` trong khi `git ls-remote` đo tip integration là `6f79853` — base sha
của API là giá trị cache/cũ, không ảnh hưởng mergeable; audit scope vẫn chạy
trên `6f79853` như các checkpoint 47–51.)

## 0. Chỉ đạo / baseline

- Không có chỉ đạo mới trên issue #116 kể từ checkpoint 51. Tiếp tục WO37
  checkpoint lớn 1 (M-B): hoàn soundtrack cho các cảnh còn im lặng — sau
  checkpoint này còn 2 cảnh: CIN_019–020.
- Baseline integration không đổi `6f79853` (PR #128 đã merge). PR #119 vẫn
  **MERGEABLE** — xác minh qua GitHub API trong lượt này trước push:
  state open, mergeable true, mergeable_state `clean`, head `d51e727`,
  99 commit / 1317 file; mô tả live vẫn CP01–45 (18214 ký tự).
- Scope audit vs baseline `6f79853`: **1321 paths, 1 violation**
  (`.gitattributes`) — vẫn chỉ là artifact merge-base như CP51:
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner). Audit riêng nội dung CP52 (base `d51e727`, head
  `9bdfb17`): **18 paths, 0 violations**. (Tổng full tăng 1314 → 1321
  đúng 7 path kỳ vọng: 3 file báo cáo CP51 + 4 file mới của CP52 —
  script mix mới, manifest + WAV mix nguồn, WAV mix runtime.)

## 1. Khối hoàn thiện

Mix nháp v1 cho CIN_018 ("Điều ông không cho ai từ chối", 18 s) — mix cảnh thứ mười lăm sau
CIN_006 v1 (checkpoint 34), CIN_003 v1 (checkpoint 37), CIN_005 v1 (checkpoint 38),
CIN_007 v1 (checkpoint 39), CIN_008 v1 (checkpoint 40), CIN_009 v1 (checkpoint 41),
CIN_010 v1 (checkpoint 42), CIN_011 v1 (checkpoint 45), CIN_012 v1 (checkpoint 46),
CIN_013 v1 (checkpoint 47), CIN_014 v1 (checkpoint 48), CIN_015 v1 (checkpoint 49),
CIN_016 v1 (checkpoint 50) và CIN_017 v1 (checkpoint 51), cùng công thức P0 v3 — và nhúng vào runtime OGV +
review MP4 của cảnh. Cả 19 cảnh campaign có mix nhúng nay là P0 (CIN_001/002/004) +
CIN_006 + CIN_003 + CIN_005 + CIN_007 + CIN_008 + CIN_009 + CIN_010 + CIN_011 +
CIN_012 + CIN_013 + CIN_014 + CIN_015 + CIN_016 + CIN_017 + CIN_018 (prologue CIN_000 tính
riêng; pack runtime nay 19 cảnh gồm prologue).

- `Tools/MediaProduction/Muse/build_cin018_mix_v1.py` (mới): công thức P0 v3
  nguyên văn (music target −30 LUFS ducked, ambience chính −36 LUFS loop
  acrossfade 1 s, peak ceiling −1,0 dBTP, fade đầu/cuối 0,3 s).
- Stem assignment MỚI, PROPOSED_CANDIDATE (bảng stem CP02 không gán gì cho
  CIN_018; timing manifest của cảnh chỉ liệt kê reveal làm candidate stem):
  music `MUSIC/sa_hoa` + ambience `AMBIENCE/desert_wind` + stinger
  `SFX/CINEMA/reveal` tại 0,0 s (xem ghi chú stinger bên dưới) + HAI take VO
  CP17: `VO_CIN_018_S02_COVOTUONG_draft_v1.wav` tại 6,5 s và
  `VO_CIN_018_S03_PLAYER_draft_v1.wav` tại 12,5 s. Tất cả stem đều
  composed (CP26/CP30), không còn stem ported nào trong mix.
  `sa_hoa` là dạng sa mạc của bộ nhạc sáng tác ("Sa Hỏa — Lò và cát":
  kiln and sand, A minor pentatonic, dry bright plucks, 110 BPM) — cue
  đúng setting cho cảnh hạn hán xoay quanh việc nước BỊ GIỮ LẠI, không
  phải nước hiện diện (S01: ruộng nứt nẻ, một người rót nước cuối cùng
  từ bầu vào chén, thư niêm phong và cọc đo, MEMORY_MEDIUM; S02: Cơ Vô
  Tướng ngồi bàn với cuộn sách và ấn, MEMORY_DETAIL; S03: nhân vật trùm
  đầu đeo mặt nạ bên cỗ máy nước bằng đồng ban đêm, MEDIUM_STATIC; theo
  đúng keyframe CIN_018 S01/S02/S03). `desert_wind` là giường gió sa mạc
  cho ruộng khô và rặng tre ban đêm của cả ba shot. Cả hai đều là lần
  dùng thứ hai trong mix cảnh — cùng cặp đã dùng cho CIN_010 (trạm nghỉ
  đoàn lữ hành vàng tro), cảnh sa mạc ngay trước đó trong cùng chương;
  việc tái dùng được ghi rõ, không giấu, vì hai cảnh cùng setting Sa Hỏa
  và bộ cue chỉ có một dạng sa mạc. Khác CIN_010 ở chủ thể, không ở sa
  mạc: CIN_010 là trạm nghỉ đoàn lữ hành với bình nước cuối cùng; CIN_018
  là cuộc đối chất về ai đã cho nước ở Sa Hỏa và ai không được hỏi vì sao
  nước mất. `bach_uyen` đã bỏ qua: dạng low-pass dưới nước, dùng cho
  CIN_015/CIN_017 — ngược hẳn cảnh này (nước hiện diện ở đó, nước bị giữ
  lại ở đây). `ben_mua` đã bỏ qua: leitmotif bến mưa, sai setting cho cảnh
  hạn hán về nước không có. `thang_long` là dạng kinh thành (sai setting);
  `tran_son` là dạng chuông-cổng, dùng cho CIN_008 và CIN_012;
  `lam_trieu` là sáo đồng quê, dùng cho CIN_013; `quiet_discovery` là
  khoảng lặng khám phá, dùng cho CIN_007/CIN_011/CIN_016 — sai cho cảnh
  đối chất; `rift_finale` là cái kết đầy đủ duy nhất của bộ (finale, sai
  cho nhịp giữa chapter); `boss_mang_cot` là nhạc boss của SAI boss (Mãng
  Cốt, không phải Cơ Vô Tướng) — và nhịp này là đối chất lặng, không phải
  trận boss. Ambience: `river_shore` đã bỏ qua: giường mép nước, dùng
  cho CIN_003/CIN_008 — ruộng S01 là đất nứt khô, không phải bờ nước;
  `rain_light`/`rain_heavy` là giường mưa, nhưng không có mưa trong cả ba
  keyframe (ruộng hạn, phòng bàn, sân đêm — không vệt mưa); `mountain_wind`
  dùng cho CIN_013; `forge` dùng cho CIN_012; `waterfall` dùng cho CIN_009;
  `wind_canopy` là giường rừng; `underwater` là giường nước (sai ở đây);
  `cave_drips` là hang; `city_night`, `thang_long_crowd`, `rift` đều sai setting.
- CIN_018 là cảnh campaign DUY NHẤT có HAI cửa sổ thoại (ghi rõ trong
  scene export manifest của cảnh) — đây là mix cảnh đầu tiên có hai take
  VO. Cả hai take đều đặt tại đầu cửa sổ của mình và cùng dìm music bus
  qua MỘT bus VO gộp (sidechain key mang cả hai take), nên nhạc hạ xuống
  dưới từng câu và hồi lại trong khoảng trống 3,12 s giữa hai take
  (9,38–12,5 s; compressor release 350 ms). Ducking được đo riêng trên
  TỪNG cửa sổ đầy đủ (phương pháp CP39 theo từng cửa sổ), để mỗi mức dìm
  so sánh được với các mix một cửa sổ.
  - S02 Cơ Vô Tướng "Ta không còn chấp nhận phần ta không biết.":
    take 2,880 s, chạy 6,5–9,380 s, KHỚP cửa sổ 6,5–11,5 s với dư 2,120 s.
    Không overrun, không tail trim. (Câu thoại 33 ký tự, 6,60 ký tự/giây
    trên cửa sổ 5 s — thời lượng take đo từ byte thật, CP17 ghi windowFit
    FITS, không tăng tốc.)
  - S03 Người chơi "Ở Sa Hỏa ông đã cho nước. Ở nơi khác, người ta không
    được hỏi vì sao nước mất.": take 5,280 s, chạy 12,5–17,780 s, OVERRUN
    cửa sổ 12,5–17,5 s đúng 0,280 s — overrun được GIỮ NGUYÊN, không cắt,
    không tăng tốc, theo verdict của chủ dự án về ba overrun campaign
    (CIN_005_S03 +0,160 s, CIN_018_S03 +0,280 s, CIN_006_S03 +0,520 s —
    cửa sổ giữ nguyên, quyết định thuộc về Codex ở PR review). Take kết
    thúc 0,220 s TRƯỚC cuối cảnh 18,00 s nên không tail trim ở mép cảnh.
    (Câu thoại 70 ký tự, 14,00 ký tự/giây trên cửa sổ 5 s — CP17 ghi
    windowFit OVERRUN.) Take S03 là VOICE_PLACEHOLDER_ONLY (CP17):
    VOICE_GUIDE không gán giọng nói/giới tính cho người chơi; take tồn
    tại để canh nhịp, đạo diễn phải thay bằng giọng đã chốt hoặc bỏ lời
    nói thành tiếng — mix đưa vào nguyên vẹn để nghe được nhịp, không
    phải quyết định casting.
- Lệch stinger so với công thức (ghi rõ, không giấu): công thức đặt reveal
  tại 6,0 s (đầu S02), như cả 14 mix cảnh trước. Ở đây cue reveal dài
  3,000 s, nên đặt tại 6,0 s nó sẽ chạy 6,0–9,0 s và đè lên 2,5 s trong
  2,880 s của câu S02 (6,5–9,380 s) — câu từ chối then chốt của cảnh, nói
  trên màn hình bởi Cơ Vô Tướng. Stinger do đó đặt tại 0,0 s (đầu S01 —
  reveal mở đầu của ký ức: ruộng hạn, thư niêm phong, cọc đo), chạy
  0,0–3,0 s, không chạm cả hai cửa sổ VO. Vị trí vẫn PROPOSED chờ picture
  lock; đạo diễn có thể dời về 6,0 s (sting đè lên câu thoại) hoặc 12,0 s
  (đầu S03). Validator khẳng định vị trí ghi trong manifest là 0,0 s.
- Ducking −6,05 dB trong cửa sổ S02 và −7,44 dB trong cửa sổ S03 (0,0 dB
  ngoài cả hai cửa sổ) — đều là mức dìm thật, không phải số 0,0 dB kiểu
  CIN_016: `sa_hoa` KHÔNG im lặng trong cả hai cửa sổ (ở CIN_010 nó cũng
  cho mức dìm −7,94 dB); hai mức khác nhau vì cue to/nhỏ khác nhau trong
  từng cửa sổ — cùng tham số compressor, đo từ byte thật, không chỉnh lại.
  Validator khẳng định mức dìm thật < 0 ở CẢ HAI cửa sổ.
- `Art_Source/Audio/Muse/MIX/CIN018_DRAFT_V1/CIN_018_mix_draft_v1.wav` +
  `CIN018_MIX_V1_manifest_v1.json`: mix 18,000 s, −21,51 LUFS / −2,51 dBTP,
  LRA 8,30 LU, peak trim 0,00 dB; loop join ambience tại 15,5 s, tỉ lệ
  jump/P999 = 0,603. Ba stem đo lại từ byte thật khớp đúng bảng pack
  (sa_hoa −21,96; desert_wind −29,93; reveal −24,96 LUFS). Hai take VO đo
  lại −23,77 LUFS (S02) / −22,54 LUFS (S03) — khớp đúng CP17; VO giữ
  unity theo công thức, không đổi gain — ghi rõ, không chuẩn hóa lén
  (cùng lý do như các mix trước). Manifest giữ trường `vo` là take S03
  (hình dạng một take như mọi mix trước) và thêm danh sách `voices` với
  cả hai take (cửa sổ, thời lượng, fit/overrun từng take). Mix to hơn
  các mix trước (−21,51 so với khoảng −24,6…−25,9 LUFS) vì mang HAI take
  VO cùng lúc cộng stinger ở đầu cảnh — đo được, không phải khuyết điểm;
  VO vẫn unity theo công thức.
- Runtime: bản sao mix tại `ClientGodot/assets/audio/mix/cin018_v1/` (sha
  khớp manifest nguồn, cùng SHA với mix nguồn nên LFS chỉ thêm 1 object);
  OGV + MP4 của CIN_018 mux lại bằng `build_runtime_pack_goi31.py` (đã mở
  rộng cho CIN_018) với audio nhúng (video copy bit-for-bit: MP4 540 frame,
  OGV 515 frame stored, không đổi; MD5 video stream khớp đúng bản gốc —
  MP4 2e2cee26… / OGV 75793735…, đo độc lập từ file pre-mux trong git;
  OGV Vorbis 160k −21,57 LUFS / −2,62 dBTP; MP4 AAC 192k −21,53 LUFS /
  −2,48 dBTP — đo lại từ byte đã encode, khớp đúng số pack builder ghi;
  metadata comment CP52 trong cả hai file). Các cảnh CP34/CP37/CP38/CP39/
  CP40/CP41/CP42/CP45/CP46/CP47/CP48/CP49/CP50/CP51 (CIN_001/002/004/006/003/005/
  007/008/009/010/011/012/013/014/015/016/017) chỉ được verify lại, không mux lại
  (LUFS khớp đúng bản ghi CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/
  CP48/CP49/CP50/CP51).
- `RUNTIME_PACK_GOI31_v1.json` nay có 19 cảnh (thêm CIN_018); manifest
  audio runtime 624 → 625 file (mix 27 → 28); manifest cinematics cập nhật
  checkpoint 52; export manifest CIN_018 ghi `hasAudioTrack: true` + audio
  block cho cả hai file.
- Playback metadata + bảng phát âm CHẠY LẠI cho mix nhúng mới (theo đúng ghi
  chú CP44: khi một cảnh được nhúng mix, chạy lại builder để fallback cập
  nhật): `PLAYBACK_METADATA_v1.json` nay 19 embedded / 2 silent
  (CIN_019–020), builder PASS 0 mismatches; `PRONUNCIATION_TABLE_v1.json`
  nay 25 playback cue rows (19 embedded + 6 P0 v1/v2 alternates), 22 seam
  rows (1 flagged, không đổi — MUSIC/sa_hoa 0,016015; KHÔNG có hàng seam
  MỚI — MUSIC/sa_hoa + AMBIENCE/desert_wind đã có trong bảng từ mix cảnh
  CIN_010), 21 fallback rows, 166 file kiểm chứng (tăng từ 160: +5 cho
  cảnh mới nhúng như mọi checkpoint trước +1 take VO thứ hai của CIN_018);
  cue CIN_018 mang cả hai take trong trường `voices` (S02 slack +2,120 s,
  lead/tail 0,165/0,251 s; S03 slack −0,280 s, lead/tail 0,185/0,169 s),
  ducking [−6,05, −7,44] dB; fallback CIN_018: EMBEDDED_SOUNDTRACK → mix
  WAV → stems+VO (cả hai take) → VO+SRT → SRT-only. Playback metadata
  cũng ghi `voices` cho CIN_018. Ba builder được mở rộng theo đúng tiền lệ
  CP51 (`build_playback_metadata_v1.py`: nhãn checkpoint 52 + trường
  `voices`; `build_pronunciation_table_v1.py`: map `cin018` + `CIN_018`
  ở cả 4 bảng tra, chuỗi "CIN_018-020" → "CIN_019-020", nhãn checkpoint
  52, cue row ghi `voices`, fallback liệt kê cả hai take) và validator mở
  rộng theo tiền lệ (`check_cin018_mix` mới — khẳng định 2 mục ducking
  đều < 0, `voices` đủ 2 take với overrun −2,12/+0,28 và cửa sổ đúng,
  stinger tại 0,0 s — + assert playbackCueRows 24 → 25, assert runtime
  total 624 → 625, chuỗi checkpoint 52, mục CIN_018 trong notes). Tool
  `verify_runtime_delivery.py` cũng mở rộng theo tiền lệ (chuỗi "verifies"
  thêm mục checkpoint 52).
- Staging (KHÔNG phải khuyết điểm của mix, không chặn mix): lần này người
  nói S02 NHẬN DIỆN ĐƯỢC — timing manifest ghi S02 dialogue onscreen:
  true cho Cơ Vô Tướng (NPC_CO_VO_TUONG), keyframe S02 cho thấy ông ngồi
  bàn, mặt nhìn rõ. Hai khuyết điểm keyframe đã ghi chạm tới shot này:
  S02 là medium shot thay vì detail close view mà timing gọi MEMORY_DETAIL,
  và tóc ông khác S01 dù cả hai shot cùng một thời kỳ ký ức. Ngược lại,
  câu S03 KHÔNG nhận diện được trong hình — timing manifest ghi S03 dialogue
  onscreen: null cho NGƯỜI CHƠI, nên câu thoại được đọc off-screen, như
  giọng Ly An trong CIN_004 (DEC-MEDIA-P0 Q2); keyframe S03 cho thấy nhân
  vật trùm đầu đeo mặt nạ bên cỗ máy nước bằng đồng, nhưng nhân vật đó
  KHÔNG được xác định là người nói, và khuyết điểm keyframe ghi rõ mặt nạ
  sứ che kín toàn mặt thay vì nửa mặt nứt theo thiết kế, còn cỗ máy đồng
  phủ kín cả thân, đọc như người máy hơn là người đeo lõi ngực và khung
  lưng. S01: tờ thỉnh nguyện vẽ thành phong bì niêm sáp hiện đại thay vì
  tờ đơn gấp. Tất cả là việc của final picture/character lock, không phải
  lỗi mix; mix không dời VO để che. (Ghi chú staging trong script mix đã
  viết đúng sự thật này TRƯỚC khi mux.)

## 2. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_52_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  `cin018_mix_v1_files_checked: 1`; campaign 20 scene / 63 shot / 378 s /
  21 dialogue; playback metadata 19 embedded / 2 silent; pronunciation
  cue rows 25 / seam rows 22 / fallback files 166; counts khác chỉ đúng 5
  thay đổi kỳ vọng so với CP51: cin018 files checked, embedded 18→19,
  silent 3→2, cue rows 24→25, fallback files 160→166; seam rows giữ 22).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_52_RUNTIME_REVERIFY_20261108.json`; runtime audio
  **625** (22 nhạc/ambience + 519 SFX/UI + 30 VO + 28 mix + 26 composed);
  clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic
  3 file. (Counts khác chỉ đúng 2 thay đổi kỳ vọng so với CP51: runtime
  audio files 624→625, manifest total 624→625.)
- Scope audit (`check_agent_scope.py`, base integration `6f79853`, head commit
  nội dung `9bdfb17`): **1321 paths, 1 violation** — `.gitattributes`, nhưng
  `git diff 6f79853 HEAD -- .gitattributes` rỗng (file byte-identical với
  baseline owner sau PR #128); tool vẫn liệt kê vì nó diff từ merge-base
  `cf17178` (merge PR #117), nơi file chưa có 12 dòng LF của PR #127. Audit
  riêng nội dung CP52 (base `d51e727`, head `9bdfb17`): **18 paths, 0 violations**.
- Commit nội dung: `9bdfb17` (18 file: 1 tool mix mới + 6 tool mở rộng +
  2 file mix nguồn + 1 file mix runtime + 2 file video mux lại + 4 manifest
  runtime (audio, playback metadata, cinematics, pack) + 1 export manifest
  + 1 bảng phát âm).
  File WAV/OGV/MP4 commit dưới dạng LFS pointer (quy tắc `.gitattributes` đã
  merge qua PR #127; mix runtime trùng SHA với mix nguồn nên LFS chỉ thêm
  1 object). Push đã xác minh qua `git ls-remote`: remote head `9bdfb17`,
  3 object LFS upload (mix WAV 1 object dùng chung 2 path + OGV + MP4).
- PR #119 sau push: remote head `9bdfb17`, 100 commit / 1321 file (đếm ba
  chấm từ merge-base `cf17178`, khớp đúng số audit 1321 paths). Trạng thái
  mergeable ĐỌC TƯƠI qua API sau push: mergeable true, mergeable_state
  `unstable` — KHÔNG phải xung đột: 8/11 check run trên head mới vẫn đang
  `in_progress` (pipeline, build, e2e, smoke...), 3 check đã xong đều
  `success` (guard-design-input, validate ×2), 0 failure tính tới lúc đọc;
  `unstable` ở đây nghĩa là check chưa chạy xong, không phải merge conflict
  (mergeable vẫn true). Trạng thái cuối sau khi CI chạy xong cần luồng chính
  đọc lại. Mô tả live vẫn CP01–45 (18214 ký tự).
  Commit báo cáo checkpoint này được push sau, riêng.
- Sự cố thao tác trong lượt này (đã sửa, không ảnh hưởng kết quả):
  (1) Script mix mới lỗi cú pháp ở lần chạy đầu (dấu ngoặc thừa trong
  `loudnorm` khi chép từ script CIN_017); đã sửa 1 ký tự, chạy lại đạt.
  (2) Lệnh đo lại loudness OGV/MP4 lần đầu thất bại vì dùng cờ `-v error`
  làm mất JSON loudnorm trên stderr; đã đo lại đúng cách như trong script
  (không cờ `-v error`, parse JSON từ stderr) — OGV −21,57 / MP4 −21,53
  LUFS khớp đúng số pack builder ghi. Không file working tree nào bị ghi
  đè trong quá trình này.

## 3. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho mix này và toàn bộ shortlist;
  mọi số LUFS/TP là đo từ byte, không phải PASS nghe tai. Mix vẫn
  DRAFT_MIX_NOT_FINAL; stem assignment PROPOSED; vị trí stinger PROPOSED
  chờ picture lock (đặt tại 0,0 s thay vì 6,0 s theo công thức — đạo diễn
  có thể dời); VO vẫn bản nháp TTS, take S03 chỉ là placeholder đo nhịp
  (VOICE_PLACEHOLDER_ONLY), chưa phải casting.
- Final picture vẫn chờ keyframe/character lock; clip vẫn là Ken Burns trên
  still storyboard, không phải final pose animation. Người nói S03
  off-screen (onscreen: null) chờ character lock / đạo diễn — không dời VO,
  không sửa timing trong checkpoint này. Overrun S03 +0,280 s giữ nguyên
  theo verdict của chủ dự án, chờ Codex quyết ở PR review.
- Cặp stem sa_hoa + desert_wind nay dùng lần thứ hai (CIN_010 rồi
  CIN_018): hai cảnh cùng setting Sa Hỏa nên tái dùng là có lý, nhưng nếu
  Codex/đạo diễn muốn phân biệt rõ hơn hai cảnh sa mạc kề nhau, quyết định
  thuộc về adapter ở PR review (đổi stem là thay đổi công thức, không tự
  làm trong checkpoint này).
- Build mix KHÔNG bit-deterministic giữa các lần chạy (ghi nhận ở checkpoint
  39 và xác nhận lại ở checkpoint 48/50: cùng công thức, cùng code, hai lần
  chạy liên tiếp cho hai SHA khác nhau trong khi LUFS/TP đo được giống hệt —
  build lại sau này phải re-verify manifest, không copy SHA cũ).
- Mô tả PR #119 vẫn ở checkpoint 01–45; cập nhật lên CP01–52 + ACK
  CP52 cần thẻ duyệt của chủ dự án qua luồng chính (không tự ghi
  qua connector). Payload CP52 đã soạn (gộp CP52 vào bản CP01–51, kèm
  chỉnh số runtime 624 → 625 file và trạng thái mergeable mới).
- PR #119 mergeable TRUE (mergeable_state `unstable` sau push vì CI đang
  chạy trên head mới — 8/11 check in progress, 3 success, 0 failure; không
  phải xung đột) — nhưng Muse không tự merge; Codex review/merge. 2 cảnh
  còn im lặng: CIN_019–020 (WO37 checkpoint lớn 1: còn 2 mix).
- 720p standard (spec V2/M7 ghi "low 640×360 và standard 720p") vẫn chưa
  giao: mọi keyframe nguồn đều 640×360 nên bản 720p chỉ là upscale, không
  thêm thông tin hình — chờ hướng của chủ dự án/Codex (upscale storyboard
  hay đợi final picture), không tự làm.

## 4. Khối tiếp theo

Mix cảnh tiếp theo cùng công thức (ứng viên gần nhất CIN_019: take VO CP17 đã
có, cửa sổ 12,5–17,5 s; stem assignment cần đề xuất riêng theo setting của
cảnh tại thời điểm làm — khi thêm mix, nhớ cập nhật cả 4 map trong
`build_pronunciation_table_v1.py` VÀ các assert đếm trong
`validate_media_deliveries.py`), hoặc cập nhật mô tả PR #119 lên CP01–52
+ ACK CP52 (khi chủ dự án duyệt), hoặc M8 QA khi integration di
chuyển / PR có review mới. Không quay sang game sprite/UI/map/VFX/Godot.
