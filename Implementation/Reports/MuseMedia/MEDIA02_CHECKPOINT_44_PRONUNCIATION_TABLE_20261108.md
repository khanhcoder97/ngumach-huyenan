# MEDIA-02 CHECKPOINT 44 — Bảng phát âm/tên riêng + gap/head-tail/ducking/seam cues + fallback playback (Codex WO32 mục 3)

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `8af4d37`, checkpoint 43. Đầu lượt: issue #116 vẫn 16 comment,
mới nhất 6714410531 (ACK CP42) — KHÔNG có chỉ đạo mới sau comment Codex 6713518554
(WO32); integration không đổi ở `6f2b465`; PR #119 OPEN/HOLD, head `8af4d37`,
mô tả ở CP01–42 — payload cập nhật lên CP01–43 + ACK CP43 đã soạn từ lượt trước,
vẫn chờ chủ dự án duyệt, KHÔNG đăng trong lượt này.)

## 1. Khối hoàn thiện

Thực hiện **mục 3 của chỉ đạo Codex 08/11 (WO32)** — phần việc Muse còn lại sau
khi mục 4 (playback metadata, CP43) đã xong: bảng phát âm/tên riêng, các cue
gap/head-tail/ducking/seam và fallback playback, giữ NOT_AUDITIONED, không lặp
đo loudness thành checkpoint sáng tác.

- `Tools/MediaProduction/Muse/build_pronunciation_table_v1.py` (mới): sinh bảng
  từ các manifest VO, SRT prologue, các manifest mix, CP33 shortlist,
  PLAYBACK_METADATA_v1.json, và **kiểm chứng mọi khẳng định bằng byte thật /
  nguồn thật trước khi ghi** (sha256 mix + take, ffprobe duration, silencedetect
  head/tail, decode f32 đo wrap jump, đếm docs/production). Có mismatch là
  tool thoát 1 và không ghi file.
- `Implementation/Content/Audio/Deliveries/PRONUNCIATION_TABLE_v1.json` (mới,
  manifestId `NGM_PRONUNCIATION_TABLE_V1`):
  - **16 tên riêng** với âm tiết + thanh điệu + IPA xấp xỉ giọng Bắc + câu hỏi
    cho người nghe. Chỉ **4 tên thực sự được nói ra** trong audio hiện tại:
    Lạc Châu, Huyền Ấn, Bến Mưa (narration prologue, SRT cue 1/4/5) và Sa Hỏa
    (CIN_018_S03 — tên riêng duy nhất trong 21 cửa sổ thoại campaign). 10 tên
    người nói/vai (Ly An, Tạ Vân Khanh, Hạ Mặc, Sầm Chủ Quỹ, Tống Bành,
    Cơ Vô Tướng, Trưởng đoàn, Đội trưởng thợ lặn, Người chơi, Người nhận thư)
    KHÔNG được nói ra trong bất kỳ câu thoại nào — người nghe kiểm tra giọng
    có hợp vai / có đọc như cùng một nhân vật, không kiểm tra phát âm tên
    (D-10). Mãng Cốt (boss, không thoại) + Ngũ Mạch (tên game, không nói ra).
    Chỉ 1 tên DECIDED: **Tạ Vân Khanh** (quyết định chủ dự án 2026-11-07,
    D-12) — builder đếm lại docs/production (`**/*.md`): “Tạ Vân Khanh” 37,
    “Tạ Văn Khánh” 0. (CP36 đếm 176 trên cây rộng hơn; cả hai cách đếm đều
    khẳng định cách viết chuẩn có mặt và cách viết sai vắng mặt.)
  - **17 hàng playback cue**: 11 mix nhúng + 6 mix P0 v1/v2 alternate.
    Head silence = 0,0 s ở mọi mix (mở đầu đã có tiếng); tail silence
    0,0–0,165 s. Lead silence trong take VO 0,07–0,423 s — đáng chú ý nhất
    take CIN_001_S05: lời nói thực bắt đầu 0,423 s sau đầu cửa sổ 24,8 s.
    Slack cửa sổ: 2 overrun trong nhóm mix (CIN_005 −0,16 s, CIN_006 −0,52 s,
    giữ nguyên theo lệnh chủ dự án). Ducking nhạc theo manifest evidence:
    −3,92 đến −14,32 dB (sâu nhất CIN_001 v1 −14,32 dB; v3 −3,92 dB).
    Loop join: bed ambience vòng 16,0 s + crossfade 1,0 s → join tại 15,5 s
    (cảnh 18 s) và 15,5/31,5 s (CIN_001 36 s); prologue: ben_mua hard join
    tại 56,667 s, hai bed ported hard join mỗi 16,0 s.
  - **19 hàng seam**: wrap jump đo lại từ byte OGG runtime của bed (file
    adapter thực sự loop — đo từ master WAV sẽ ra ~0 vì master có end-landing
    0,25 s, che mất seam thật). Khớp CP33 trong dung sai 0,002 ở cả 19 hàng.
    Chỉ **1 hàng flag ear-check**: MUSIC/sa_hoa composed 0,016015 (> 0,015).
  - **21 hàng fallback** (FB-0..FB-7): embedded → mix WAV độc lập → stems +
    VO → VO + SRT → SRT-only. 125 file đã kiểm chứng tồn tại (mix WAV khớp
    sha256 manifest ở cảnh nhúng). 10 cảnh im lặng CIN_011–020 KHÔNG có
    fallback audio: adapter không được tự chế mix từ stem hay bật VO trên
    video im lặng (FB-6).
- Validators cập nhật: `validate_media_deliveries.py` thêm
  `check_pronunciation_table()` (đo lại head/tail silence + wrap jump,
  đối chiếu ducking/loop join với manifest mix, kiểm chứng fallback);
  `verify_runtime_delivery.py` cập nhật nhãn checkpoint 44.

### Số đo cue chính (head/tail, giây; ducking, dB)

| Mix | Head | Tail | Take lead | Slack cửa sổ | Ducking nhạc |
|---|---|---|---|---|---|
| CIN_000 prologue | 0,0 | 0,0 | 0,423 (final line) | — (narration 6 cue) | sidechain, không ghi số |
| CIN_001 v1 / v2 / v3 | 0,0 | 0,055 | 0,423 | +1,132 | −14,32 / −3,92 / −3,92 |
| CIN_002 v1 / v2 / v3 | 0,0 | 0,165 / 0,06 / 0,057 | 0,18 | +0,208 | −6,48 / −6,48 / −7,32 |
| CIN_004 v1 / v2 / v3 | 0,0 | 0,0 | 0,07 | +0,248 | −4,99 / −5,16 / −5,16 |
| CIN_003 v1 | 0,0 | 0,0 | 0,07 | +0,968 | −10,42 |
| CIN_005 v1 | 0,0 | 0,0 | 0,183 | −0,16 (overrun, giữ) | −7,89 |
| CIN_006 v1 | 0,0 | 0,0 | 0,183 | −0,52 (overrun, giữ) | −7,86 |
| CIN_007 v1 | 0,0 | 0,0 | 0,07 | +1,088 | −9,43 |
| CIN_008 v1 | 0,0 | 0,0 | 0,187 | +1,448 | −7,22 |
| CIN_009 v1 | 0,0 | 0,0 | 0,07 | +0,92 | −9,13 |
| CIN_010 v1 | 0,0 | 0,0 | 0,167 | +2,192 | −7,94 |

## 2. Kiểm chứng

- Builder `build_pronunciation_table_v1.py`: **PASS, 0 mismatches** — 16 tên
  (4 spoken), 17 cue, 19 seam (1 flagged), 21 fallback, 125 file kiểm chứng.
  Hai lỗi builder gặp trong lúc làm đã sửa đúng nguyên nhân trước khi PASS:
  (a) CP33 đo wrap jump trên OGG runtime, không phải master WAV — builder
  ban đầu đo master nên lệch, đã đổi sang đo OGG runtime và khớp CP33
  chính xác cả 19 hàng; (b) manifest VO prologue nằm ở
  `Art_Source/Audio/Muse/VO/PROLOGUE_VO_manifest_v1.json`, không phải trong
  `PROLOGUE_DRAFT/`.
- Source re-validation (`validate_media_deliveries.py`, thêm
  `check_pronunciation_table()` + nhãn checkpoint 44): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_44_SOURCE_REVALIDATION_20261108.json` (audio 1151 file;
  pronunciation 16 tên / 4 spoken / 17 cue / 19 seam / 21 fallback).
- Runtime re-verify (`verify_runtime_delivery.py`, nhãn checkpoint 44): **PASS,
  0 mismatches** — `MEDIA02_CHECKPOINT_44_RUNTIME_REVERIFY_20261108.json`;
  runtime audio giữ nguyên **617** (22 + 519 + 30 VO + 20 mix + 26 composed);
  checkpoint này không thêm/sửa file media runtime nào — chỉ thêm file
  JSON dữ liệu + tool + báo cáo.
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit
  nội dung `c797856`): **1265 paths, 1 violation** — vi phạm duy nhất vẫn là
  `.gitattributes`, file policy gốc của Codex do chủ dự án merge qua PR #127
  (commit `9f264ef`), KHÔNG phải nội dung CP44. Audit riêng nội dung CP44
  (base `8af4d37`, head `c797856`): **4 paths, 0 violations**.

## 3. Giới hạn

- Bảng là bản giao CHO reviewer/người nghe và adapter của Codex — Muse không
  nối playback vào Godot; việc thực thi fallback / audio ownership thuộc
  runtime của Codex.
- Mọi mix vẫn **DRAFT_MIX_NOT_FINAL** và **NOT_AUDITIONED**; final audible
  approval pending theo WO32. Bảng này không phải nghe PASS và không lặp lại
  đo loudness thành checkpoint sáng tác — số loudness duy nhất được trích là
  giá trị manifest mix, ghi rõ nguồn.
- Hướng dẫn phát âm là IPA xấp xỉ giọng Bắc cho người nghe đối chiếu, không
  phải chuẩn ngữ âm của take TTS; chỉ 4/16 tên có mẫu nói thật để đối chiếu.
- 10 cảnh CIN_011–CIN_020 chưa có mix cảnh — bảng fallback ghi rõ không có
  fallback audio; khi một cảnh được nhúng mix, chạy lại builder này để bảng
  cập nhật (nó sẽ FAIL nếu pack và byte thật lệch nhau).
- PR #119 mergeable vẫn FALSE — xung đột duy nhất `.gitattributes` (nhánh media
  thêm 2 dòng LF so với integration), chờ Codex/chủ dự án giải quyết; Muse
  không tự sửa policy, không tự merge.
- Mô tả PR #119 (đang ở CP01–42) + ACK CP43/CP44 trên issue #116: payload đã
  soạn ở lượt trước (CP43) và cần gộp CP44 — **chưa đăng, chờ chủ dự án duyệt
  trong luồng chính** (ghi qua GitHub connector cần thẻ duyệt).

## 4. Khối tiếp theo ứng viên

- Mix CIN_011 v1 (cùng công thức P0 v3) — lấp cảnh im lặng đầu tiên trong nhóm
  CIN_011–CIN_020; khi xong, chạy lại builder CP44 để fallback của CIN_011
  cập nhật từ silent sang embedded.
- Hoặc cập nhật mô tả PR #119 lên CP01–44 + ACK CP43/CP44 (khi chủ dự án duyệt).
