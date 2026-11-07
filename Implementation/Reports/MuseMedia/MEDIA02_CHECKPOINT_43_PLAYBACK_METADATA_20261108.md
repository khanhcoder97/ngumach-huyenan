# MEDIA-02 CHECKPOINT 43 — Bảng playback metadata cho các mix nhúng (Codex WO32 mục 4)

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `f4cfa9f`, checkpoint 42. Đầu lượt: mô tả PR #119 đã ở CP01–42
(đăng 08:20 JST); ACK CP42 đã đăng trên issue #116, comment 6714410531 (đọc lại khớp
nguyên văn, issue 16 comment) — không có chỉ đạo mới sau comment Codex 6713518554
(PR #128 + Work Order 32); integration không đổi ở `6f2b465`; PR #119 OPEN/HOLD.)

## 1. Khối hoàn thiện

Thực hiện **mục 4 của chỉ đạo Codex 08/11 (WO32)**: runtime OGV/MP4 nay có soundtrack
nhúng — adapter trình diễn của Codex cần metadata phát lại rõ ràng về
embeddedMix / voice / subtitle source và **audio ownership**, để không bao giờ bật
đồng thời soundtrack nhúng + mix/VO ngoài.

- `Tools/MediaProduction/Muse/build_playback_metadata_v1.py` (mới): sinh metadata
  từ pack runtime Gói 31 + manifest cinematics + các manifest mix, và **kiểm chứng
  mọi khẳng định bằng byte thật trước khi ghi** (ffprobe cấu trúc stream của từng
  file OGV/MP4, loudnorm của audio nhúng so với WAV mix nguồn và số pack đã ghi —
  dung sai 0,40 LUFS; sha256 từng file runtime so với manifest; đếm cue SRT từ file
  thật). Có mismatch là tool thoát 1 và không ghi file.
- `ClientGodot/assets/cinematics/PLAYBACK_METADATA_v1.json` (mới, manifestId
  `NGM_PLAYBACK_METADATA_V1`): đủ **21 mục** — prologue CIN_000 + 20 cảnh campaign:
  - **11 cảnh có soundtrack nhúng**: CIN_000 (prologue_mix_v1) + CIN_001/002/004
    (v3_fully_composed) + CIN_003/005/006/007/008/009/010 (mix v1 từng cảnh). Mỗi
    mục ghi: file video + stream audio đo thật, mixVersion, WAV mix nguồn + sha256,
    loudness nguồn đo lại, stem (cue/role/provenance), VO take + cửa sổ, phụ đề
    dạng OVERLAY_SRT (không đốt vào video runtime), audioOwnership =
    `EMBEDDED_SOUNDTRACK_ONLY`. Riêng P0 ghi thêm 2 bản mix độc lập v1/v2 là
    alternate KHÔNG nhúng; riêng CIN_000 ghi bản phụ đề đốt cứng là REVIEW_ONLY.
  - **10 cảnh im lặng** CIN_011–CIN_020: đã kiểm chứng không có audio stream;
    audioOwnership = `NO_EMBEDDED_SOUNDTRACK` (chưa có mix cảnh; adapter không
    được tự chế từ stem).
  - Khối `audioOwnershipPolicy` toàn cục: soundtrack nhúng là audio duy nhất của
    cảnh; file mix độc lập dưới `assets/audio/mix/**` là bản alternate/review của
    cùng mix đó, không phải lớp chồng; VO take là thành phần đã nằm trong mix;
    phụ đề runtime = video sạch + overlay SRT, bản đốt cứng chỉ để review, cấm
    double caption; **rewatch/skip/seen/fallback không grant quest** (ghi theo
    WO32 mục 4; thực thi thuộc runtime của Codex).
  - Khối `alphaCandidate`: candidate mix runtime alpha theo WO32 = P0 v3
    fully-composed + CIN_006 v1 — đúng những gì đang nhúng; **final audible
    approval vẫn pending**.
  - Reel review P0 72 s cũng được probe và ghi đúng sự thật: **không có audio
    stream** (mix review 72 s là file WAV độc lập, không nhúng trong reel).

### Số đo nhúng (OGV, LUFS) so với WAV mix nguồn

| Cảnh | Mix nhúng | Nhúng (đo lại) | Nguồn (đo lại) | Lệch |
|---|---|---|---|---|
| CIN_000 | prologue_mix_v1 | −20,76 | −20,81 | 0,05 |
| CIN_001 | v3_fully_composed | −20,90 | −21,06 | 0,16 |
| CIN_002 | v3_fully_composed | −22,43 | −22,67 | 0,24 |
| CIN_003 | v1_cin003_proposed | −21,12 | −21,16 | 0,04 |
| CIN_004 | v3_fully_composed | −26,73 | −26,78 | 0,05 |
| CIN_005 | v1_cin005_proposed | −20,99 | −21,03 | 0,04 |
| CIN_006 | v1_cin006_proposed | −22,04 | −22,01 | 0,03 |
| CIN_007 | v1_cin007_proposed | −17,98 | −18,05 | 0,07 |
| CIN_008 | v1_cin008_proposed | −24,61 | −24,58 | 0,03 |
| CIN_009 | v1_cin009_proposed | −17,72 | −17,84 | 0,12 |
| CIN_010 | v1_cin010_proposed | −24,63 | −24,60 | 0,03 |

## 2. Kiểm chứng

- Builder `build_playback_metadata_v1.py`: **PASS, 0 mismatches** — 21 cảnh
  (11 nhúng / 10 im lặng), mọi sha256 khớp manifest, mọi loudness nhúng trong
  dung sai 0,40 LUFS so với cả số pack đã ghi và WAV nguồn, cue SRT khớp.
- Source re-validation (`validate_media_deliveries.py`, thêm
  `check_playback_metadata()` + nhãn checkpoint 43): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_43_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  playback_metadata 21 cảnh / 11 nhúng / 10 im lặng).
- Runtime re-verify (`verify_runtime_delivery.py`, nhãn checkpoint 43): **PASS,
  0 mismatches** — `MEDIA02_CHECKPOINT_43_RUNTIME_REVERIFY_20261108.json`;
  runtime audio giữ nguyên **617** (22 + 519 + 30 VO + 20 mix + 26 composed);
  checkpoint này không thêm/sửa file media runtime nào — chỉ thêm file metadata
  JSON cạnh các manifest cinematics.
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit
  nội dung `4e0e5b3`): **1262 paths, 1 violation** — vi phạm duy nhất vẫn là
  `.gitattributes`, file policy gốc của Codex do chủ dự án merge qua PR #127
  (commit `9f264ef`), KHÔNG phải nội dung CP43. Audit riêng nội dung CP43
  (base `f4cfa9f`, head `4e0e5b3`): **6 paths, 0 violations**.

## 3. Giới hạn

- Metadata là bản giao CHO adapter của Codex — Muse không nối playback vào
  Godot; việc thực thi audio ownership / quest semantics thuộc runtime của Codex.
- Mọi mix vẫn **DRAFT_MIX_NOT_FINAL** và **NOT_AUDITIONED**; final audible
  approval pending theo WO32. Bảng này không phải nghe PASS và không lặp lại đo
  loudness thành checkpoint sáng tác — số đo ở đây là bằng chứng đối chiếu
  nhúng/nguồn phục vụ ownership, lấy từ byte thật tại thời điểm build.
- 10 cảnh CIN_011–CIN_020 chưa có mix cảnh (video im lặng) — các khối mix tiếp
  theo sẽ lấp dần; khi một cảnh được nhúng mix, chạy lại builder này để metadata
  cập nhật (nó sẽ FAIL nếu pack và byte thật lệch nhau).
- PR #119 mergeable vẫn FALSE — xung đột duy nhất `.gitattributes` (nhánh media
  thêm 2 dòng LF so với integration), chờ Codex/chủ dự án giải quyết; Muse
  không tự sửa policy, không tự merge.

## 4. Khối tiếp theo ứng viên

- Bảng phát âm/tên riêng + gap/head-tail/ducking/seam cues + fallback playback
  (WO32 mục 3), hoặc mix CIN_011 v1 (cùng công thức P0 v3) để lấp cảnh im lặng
  đầu tiên trong nhóm CIN_011–CIN_020.
