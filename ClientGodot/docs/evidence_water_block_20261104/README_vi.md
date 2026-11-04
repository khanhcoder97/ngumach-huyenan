# Gói bằng chứng WO24 M-C — 306 ô nước hở + 37 ô bờ sông Nam

**Dành cho Codex quyết định.** Theo quy tắc M-C của Work Order 24, thay đổi
chặn 306 ô nước được gửi dưới dạng gói bằng chứng (tọa độ / lớp / va chạm /
ảnh chú thích / liên thông), **không** chặn hàng loạt trong bản bàn giao.

## Trạng thái bàn giao (quyết định của chủ dự án, 2026-11-04)

- PR #111 (checkpoint M-A) bàn giao tiledata **trước thay đổi: blocked 5.069**.
  Commit lùi tiledata trên branch `muse/ben-mua-playable-alpha-20261103` đã
  gỡ đúng 306 ô khỏi lớp blocked của gói, đồng thời đưa assert của
  `tools/convert_full_map.py` và check `blocked_5069` trong
  `scripts/FullMapMain.cs` về 5.069 — khớp với `HANDOVER_CHECKLIST.md`.
- Ở bản local của Muse, tiledata nguồn đã chặn 306 ô này (ART_REVIEW
  2026-11-03, chủ dự án duyệt tích hợp runtime local 2026-11-04). Bản local
  **không** phải là bản bàn giao; quyết định áp dụng vào deliverable thuộc
  về Codex sau khi xét gói bằng chứng này.

## Phương pháp

- Đối chiếu tiledata nguồn `strip_064_128.json` và `strip_128_192.json` với
  bản sao lưu trước đợt chặn (`*_pre_waterblock_20261103.json`).
- Lưới: 450×60 ô, ô 0,8 WU, gốc Y 36,0 ở mép Bắc, hàng 0 = Bắc.
- WU x = [global_col×0,8, (global_col+1)×0,8];
  WU y = [36−(row+1)×0,8, 36−row×0,8].
- Ảnh chú thích vẽ trên bản đồ style 2 (`full_map_style2_native.png`):
  đỏ = 306 ô nước đề xuất chặn, cam = 37 ô bờ giữ đi được.

## Kết quả kiểm toán

- Toàn map: 27.000 ô / nước 4.960 / blocked 5.069 → 5.375 nếu áp dụng
  (+306, gỡ 0 ô).
- Theo dải: 064–128 blocked 740→908 (+168); 128–192 blocked 507→645 (+138).
  Không ô nào ngoài 2 dải này đổi trạng thái blocked.
- 306 ô nước: tất cả blocked 0→1, ground=None, path=None, không lớp nào
  khác thay đổi. Loại nước: `water_base_a` 267, `water_ripple_a` 17,
  `water_lily_a` 18, `water_sparkle_a` 4. Hàng 50–55
  (50: 49, 51: 59, 52: 61, 53: 57, 54: 69, 55: 11).
- Liên thông 4 hướng của 306 ô = đúng 3 cụm:
  - Cụm 0: 268 ô, X 104,8–153,6 WU, Y −8,0…−4,0.
  - Cụm 1: 36 ô, X 64,0–72,8 WU, Y −8,8…−4,0.
  - Cụm 2: 2 ô, X 96,0–96,8 WU, Y −7,2…−5,6 — nước sông **dưới** nhịp cầu
    92–108 (global col 120, rows 52–53), không phải sàn cầu (sàn cầu thuộc
    lớp path, không nằm trong 306 ô).
- 37 ô bờ giữ đi được (blocked vẫn 0, không trùng 306 ô, 37/37 kề ít nhất
  một cụm nước): `reeds_dense_a` 14, `mud_bank_a` 21, `mud_dark_a` 2 —
  lau/bùn bờ sông, giữ theo quyết định ART_REVIEW 2026-11-03, không phải
  nước hở sót.

## File trong gói

- `water_block_evidence_pack_20261104.json` — đủ 343 ô (strip, col/row cục
  bộ + toàn cục, khoảng WU, ground/water/path, blocked trước/sau, cụm liên
  thông, tính kề cụm của ô bờ).
- `water_block_evidence_annotated_20261104.png` — toàn map 7200×960 có
  khung chú thích.
- `water_block_evidence_river_crop_20261104.png` — crop dải sông
  WU 60–200, phóng to.
- Tài liệu này: `README_vi.md`.

## Đề nghị

Codex quyết định: (1) áp dụng chặn 306 ô vào tiledata bàn giao, hay
(2) giữ 5.069, hay (3) áp dụng một phần theo cụm. Phía Muse sẽ thực thi
đúng quyết định đó trong checkpoint kế tiếp; bản local giữ nguyên trạng
thái đã duyệt riêng.
