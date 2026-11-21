# MEDIA-02 CHECKPOINT 36 — Sửa nhãn tên nhân vật D-12: chốt canonical "Tạ Vân Khanh"

Ngày: 2026-11-07 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `de92bce`, checkpoint 35. Checkpoint này chỉ sửa nhãn/metadata
theo quyết định của chủ dự án — không đụng byte media nào.)

## 1. Quyết định và nguồn gốc lỗi

- Chủ dự án chốt trong main chat 2026-11-07 (widget quyết định D-12): cách viết
  canonical của `NPC_TA_VAN_KHANH` là **"Tạ Vân Khanh"**.
- Đối chiếu nguồn thật trước khi sửa: `docs/production` dùng "Tạ Vân Khanh" 176 lần,
  "Tạ Văn Khánh" 0 lần; campaign VO manifest (CIN_008_S03), Cinema Production Pack v1,
  campaign timing manifest và questkit PR #118 đều đã ghi "Tạ Vân Khanh".
- Nguồn gốc lỗi (nói thẳng): cách viết sai **không nằm trong manifest nào**. P0 VO
  manifest chỉ lưu speaker ID `NPC_TA_VAN_KHANH`; nhãn hiển thị của take CIN_002_S02
  do ánh xạ `SPEAKER_DISPLAY` dự phòng trong chính tool shortlist CP33
  (`build_ab_shortlist_goi31.py`) sinh ra, và `PROPER_NAMES` của tool liệt kê cả hai
  cách viết nên D-10 đếm nhân vật này thành hai người nói. Evidence của D-12 ở CP33
  ghi "P0 manifest ghi 'Tạ Văn Khánh'" là không chính xác — đã sửa lại trong chính
  mục D-12 (xem mục 2).

## 2. Khối hoàn thiện

- `Tools/MediaProduction/Muse/build_ab_shortlist_goi31.py`:
  - `SPEAKER_DISPLAY["NPC_TA_VAN_KHANH"]`: "Tạ Văn Khánh" → "Tạ Vân Khanh".
  - `PROPER_NAMES`: bỏ "Tạ Văn Khánh", giữ một cách viết canonical duy nhất.
  - Câu hỏi D-02 dùng tên canonical.
  - Mục D-12 viết lại: area thêm "— ĐÃ CHỐT", evidence ghi quyết định của chủ dự án
    + nguồn gốc lỗi đúng (ánh xạ dự phòng của tool), status
    `RESOLVED_OWNER_DECISION_20261107`.
  - Docstring của tool ghi thêm ghi chú sửa nhãn checkpoint 36.
- Sinh lại bằng chính tool (đo lại từ byte thật): CP33 shortlist JSON + MD và 2
  playlist bị ảnh hưởng (`ab_shortlist_vo_playlist.txt`,
  `ab_shortlist_all_playlist.txt`). Diff kiểm từng dòng: **chỉ đổi nhãn tên** —
  speakerDisplay/listenFor của CIN_002_S02, danh sách người nói ở D-10 (không còn
  trùng hai cách viết), câu hỏi D-02, mục D-12, dòng EXTINF của CIN_002_S02 trong
  2 playlist. Mọi số đo loudness/duration/seam **giữ nguyên từng chữ số**.
  Chuỗi "Văn Khánh" còn lại duy nhất trong evidence của D-12, nơi nó được trích
  dẫn như cách viết sai đã bị thay — có chủ đích.
- `Tools/MediaProduction/Muse/validate_media_deliveries.py`: ghi chú phạm vi của
  mục kiểm shortlist cập nhật từ "(D-12, director to resolve)" thành đã chốt theo
  quyết định 2026-11-07; nhãn checkpoint trong output làm mới lên checkpoint 36.
  `verify_runtime_delivery.py`: nhãn checkpoint trong output làm mới tương tự.
- Không thu lại VO: hai câu thoại của nhân vật (CIN_002_S02, CIN_008_S03) đều không
  đọc tên nhân vật; không file audio/video/SRT/timing nào thay đổi. Báo cáo lịch sử
  CP03/CP13/CP32 giữ nguyên (chúng ghi trạng thái tại thời điểm viết); các JSON
  re-validation CP33–CP35 cũng giữ nguyên như bằng chứng của các checkpoint đó.

## 3. Kiểm chứng

- Source re-validation (`validate_media_deliveries.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_36_SOURCE_REVALIDATION_20261107.json` (audio 1151 file;
  campaign 20 scene / 63 shot / 378 s / 21 dialogue; shortlist kiểm đủ 12 ô mix,
  44 dòng seam, 6 playlist / 145 mục, VO 21 + 1 alternate tách riêng).
- Runtime re-verify (`verify_runtime_delivery.py`): **PASS, 0 mismatches** —
  `MEDIA02_CHECKPOINT_36_RUNTIME_REVERIFY_20261107.json`; runtime audio vẫn **611**
  (22 nhạc/ambience + 519 SFX/UI + 30 VO + 14 mix + 26 composed).
- Scope audit (`check_agent_scope.py`, base integration `6f2b465`, head commit nội
  dung `50da8d1`): **1214 paths, 0 violations**.
- Commit nội dung: `50da8d1bc0faaff1526c928b2d6e63c0a4b9a9e8` (9 file: 3 tool +
  4 output shortlist/playlist + 2 JSON kiểm chứng).

## 4. Giới hạn còn mở

- Trạng thái nghe vẫn **NOT_AUDITIONED** cho toàn bộ shortlist; D-12 đóng chỉ khép
  lỗi nhãn tên, các mục D-01..D-11 vẫn chờ người nghe/Codex như cũ.
- Mô tả PR #119 (bản checkpoint 01–35 vừa cập nhật 2026-11-07) còn một dòng ghi
  D-12 "đang chờ chủ dự án chốt" — đã lỗi thời sau checkpoint này; cập nhật mô tả
  PR cần thẻ duyệt riêng của chủ dự án qua luồng chính.
- Gói 31 item 5 (`.gitattributes`) vẫn chờ merge commit của chủ dự án từ
  integration `6f2b465` — không đổi tại checkpoint này.
