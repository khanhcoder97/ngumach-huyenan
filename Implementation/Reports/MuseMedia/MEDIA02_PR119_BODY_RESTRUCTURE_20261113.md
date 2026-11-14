# MEDIA-02 — PR #119 Body Restructure R1 (2026-11-13)

## Vấn đề

Mô tả PR #119 dài 114.929 ký tự tại head `be9ccb8` (bản M-B CP4 + PROLOGUE V1 FIX,
đăng ~03:40 JST) đã chạm trần truyền của connector (131.072 byte cho một tham số),
nên 2 khối mới nhất — SCENE-CLIPS MANIFEST FIX + WO37 M-G CP9 (ACK `6833806995`
đã đăng ~04:32 JST) — không gộp được vào mô tả. ACK đó đã hẹn “các section sẽ gộp
vào lượt tái cấu trúc mô tả sau”. Khối này làm đúng việc đó: tách chi tiết ra khỏi
mô tả, giữ mô tả thành bản tóm tắt gọn.

## Đã làm (không đổi bất kỳ byte media nào)

1. **`MEDIA02_PR119_BODY_V2_20261113.md`** — mô tả PR mới, **8.454 byte / 7.594 ký tự**
   (cũ 114.929 ký tự, giảm ~13,6×): head/commit/file, mergeable, integration, trạng
   thái bàn giao theo số thật, 7 khối mới nhất (mỗi khối 1 đoạn + SHA), mốc
   DEC-MEDIA-P0 Q1–Q4, giới hạn/chặn. Mọi con số khớp API + git tại head `443d3e4`.
2. **`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`** — index đầy đủ: **100 dòng bảng,
   bao phủ toàn bộ 187 commit** của nhánh (CP01–54, WO37 M-B/M-C/M-D/M-E/M-F/M-G,
   WO38 M38-A/B, WO39 M39-A/B, PROLOGUE V1 FIX, SCENE-CLIPS FIX, M-G CP9, merge/fix/
   erratum), mỗi khối có SHA nội dung + SHA báo cáo/head + tóm tắt + kết quả kiểm
   chứng. Sinh từ `git log cf17178..HEAD` bằng builder, không gõ tay.
3. **`Tools/MediaProduction/Muse/build_pr119_body_restructure_v1.py`** — builder +
   validator: sinh index từ git log, kiểm chứng body (xem dưới).
4. **`MEDIA02_PR119_BODY_RESTRUCTURE_VALIDATION_20261113.json`** — kết quả kiểm chứng.

## Kiểm chứng (validator PASS 9/9)

- Body 8.454 byte ≤ trần 60.000 tự đặt (trần connector 131.072) — còn dư chỗ cho
  nhiều khối sau mới chạm lại trần.
- Head `443d3e4`, 187 commit / 2381 file khớp git (`rev-list --count`, `diff
  --name-only`) và khớp API PR (commits 187, changed_files 2381, additions 221756).
- Merge-tree vs integration `f3db6b3`: exit 0, 0 conflict,
  tree `11f94b94cc932c00cb191f85788180672fc687c3`. API: mergeable true / clean
  (đọc ~04:44 JST tại head `443d3e4`).
- Mọi identifier trong body đều phân giải được: 18 git commit + 1 git tree +
  1 file-sha (mix prologue đã vá, đối chiếu manifest
  `PROLOGUE_MIX_V1_FIXED_manifest_v1.json`: sha256 `4f8224e1…`, 16.774.542 B) +
  2 ID comment GitHub (đã đọc qua API issue #116).
- Cả 7 khối mới nhất trong body đều có trong index; index bao phủ 187/187 commit.
- Issue #116 vẫn 33 comment, mới nhất ACK `6833806995`, không chỉ đạo mới
  (Gói 39 vẫn mới nhất). Integration `f3db6b3` không đổi (ls-remote ~04:44 JST).
- Lưu ý kỹ thuật ghi trong body v2: trường `base.sha` mà API pull trả về
  (`f383233…`) là giá trị cũ (merge PR #118), không phải integration hiện tại —
  đã xác minh `f383233` là commit có thật trong repo (merge PR #118, nhắc trong
  commit CP12 `a242af3`); integration hiện tại xác minh bằng ls-remote là `f3db6b3`.

## Scope audit

- Block: 5 paths / 0 violations (xem validation JSON).
- Cumulative toàn nhánh tại head mới: 2386 paths / 1 violation `.gitattributes`
  đã biết (artifact merge-base, byte-identical với integration).

## CHƯA LÀM — cần chủ dự án duyệt ở luồng chính

- **Mô tả PR #119 trên GitHub CHƯA cập nhật** (vẫn bản 114.929 ký tự tại head
  `be9ccb8`). Việc cập nhật cần thẻ duyệt ghi GitHub — file payload đã chuẩn bị:
  body v2 tại `Implementation/Reports/MuseMedia/MEDIA02_PR119_BODY_V2_20261113.md`
  + ghi chú payload tại
  `~/workspace/goals/ng-m-ch-continuous-development/hidden_files/payload_pr119_body_v2_20261113_0440.md`.
  Tiêu đề đề xuất (thêm 2 khối vào tiêu đề hiện tại, trước dấu “ — timing/SRT…”):
  `… + PROLOGUE V1 FIX + SCENE-CLIPS FIX + WO37 M-G CP9 — timing/SRT 20 scene, …`.
- Không đăng ACK mới: ACK cho SCENE-CLIPS FIX + M-G CP9 đã đăng (`6833806995`),
  khối này chỉ chuẩn bị cập nhật mô tả PR.

## Giới hạn

- Body v2 là tóm tắt có chủ ý: chi tiết từng checkpoint cũ chỉ còn trong index doc
  (đường dẫn trong repo, Codex đọc được) — không còn inline trong mô tả PR.
- Các mốc API trong body v2 (mergeable, issue) đọc lúc ~04:44 JST; nếu head nhánh
  đổi trước khi chủ dự án bấm duyệt, cần làm mới 1–2 câu mốc như các cặp payload
  trước (không sửa nội dung khối).
- File mix prologue đã vá trong working clone là LFS pointer (133 B); byte thật
  đã được M-G CP9 kiểm chứng qua fresh clone (validator 126/126) — không hash lại
  ở đây theo Gói 38 rule 1.

## Khối tiếp theo

Nghe thử prologue đã vá (điểm nghe ưu tiên); re-time phụ đề CIN_000 theo narration
v2; 32 shot motion chờ character lock; full OGV 720p chờ quyết ngân sách.
