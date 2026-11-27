# MEDIA-02 — PR #119 Body Restructure R280 (2026-11-27)

## Tóm tắt

- Vòng R280: gọn ĐƠN R187 (gọn đơn thứ HAI MƯƠI); index + body v2 + checker đồng bộ tới head `d2eb9b5` (749 commit / 3232 file / +396284 từ merge-base `cf17178`); merge-tree tại `d2eb9b5` vs integration `f3db6b3` exit 0, tree `4f30a12d…`.
- Không có sự kiện đăng bài giữa các vòng: payload R279 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R279 bị R280 thay thế.
- CẢNH BÁO STALE (ba phiên bản payload): bản chính (main) payload R279 ĐÃ ĐƯỢC làm tươi ở bước build sau push báo cáo ~11:57 JST (Head `d2eb9b5`, 95.055 ký tự, sha `f3c4787a`, JSON 106.140 byte, sha256 `e0facfab`) + làm tươi LẠI lúc trình ~12:01 JST (Head `d2eb9b5`, 94.964 ký tự, sha `6c6a5c38`, JSON 106.027 byte, sha256 `5d4e44c2`, head line 1092 ký tự, mergeable true/clean) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (95.021 ký tự, sha `c3a35f50`, JSON 106.102 byte, sha256 `512bea04`); hàng R279 trong index ghi cả ba phiên bản, đo từ đĩa.
- Một giai đoạn (~12:40–~13:05 JST): fetch ~12:40 JST, đọc live, sửa index + body v2, chuỗi checker tới `check_pr119_restructure_r280_v1.py` + điền SHA-hits, checker PASS 161/161 ngay lần đầu, scope audit block 3 path / 0 violation, content commit `114347b` + push, đọc live sau push (2 lần), báo cáo + payload R280.
- Content commit `114347b` (~13:03 JST): 3 file, 1449 insertions, 11 deletions; scope audit block (`d2eb9b5..114347b`) 3 path / 0 violation; cumulative tại `114347b` = 3233 path / 1 violation — artifact `.gitattributes` đã biết.
- Số đếm tại `114347b`: 750 commit / 3233 file / +397722 — khớp API đọc sau push. Additions: 396284 + (1449 − 11) = 397722.
- Merge-tree tại `114347b` vs `f3db6b3`: exit 0, tree `9acb6abe…`.
- Push: `d2eb9b5..114347b`; ls-remote xác nhận remote head `114347b` VÀ integration `f3db6b3` (ls-remote chạy được vòng này).
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- Không có cờ execution-risk vòng này.
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (connector, ~12:42 JST theo mtime file 12:41:52 JST): head `d2eb9b5`, 749/3232/+396284, mergeable null / state clean, updated_at 2026-11-27T02:56:26Z, live body R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề kết thúc "+ R263".
- Issue #116 (connector, ~12:42 JST theo mtime file 12:41:59 JST): 34 comment, updated_at 2026-11-13T19:24:49Z, không chỉ đạo mới.
- Đọc sau push (connector, 2 lần, ~13:03 + ~13:04 JST): PR head `114347b`, 750/3233/+397722 — khớp git tại content commit; mergeable null, state unstable ở cả hai lần đọc (CI đang chạy — không dao động lượt này, khác R278 clean → unstable); live body vẫn R263 (94.825, sha `07316552`, 0 U+FFFD), tiêu đề kết thúc "+ R263", updated_at 2026-11-27T04:03:10Z (đổi do push R280 cập nhật head, body không đổi). Issue #116 không đọc lại sau push (ghi rõ trong head line của payload).

## Mốc giờ

- Fetch: ~12:40 JST (FETCH_HEAD mtime 12:40:57 JST). Đọc live PR/issue: ~12:42 JST (mtime file 12:41:52 / 12:41:59 JST). Đếm git: ~12:41 JST tại `d2eb9b5`.
- Checker chạy: ~13:02 JST (validation JSON mtime 13:02:19 JST). Content commit `114347b`: ~13:03 JST (13:02:48 JST). Push: ~13:03 JST. Đọc sau push: ~13:03:25 + ~13:04:12 JST (mtime file). Báo cáo này: ~13:05 JST.

## R280 đóng khoảng trống

- Body v2: 95.353 ký tự (net +187 so với R279), headroom 9.647 so với 105.000; head line 1.419 ký tự (delta +125 — lần đầu tăng mạnh, do ghi cả hai lần làm tươi payload R279); R187 gọn 486 → 214 (gọn đơn thứ hai mươi); đoạn R279 đúng 270 ký tự (theo checker).
- Checker `check_pr119_restructure_r280_v1.py`: PASS 161/161 (161 = 160 + 1 check row-convention mới cho tuple R278).
- Transform edit chạy sạch ngay lần đầu (không assertion nào nổ); shift checker 62/62 cặp sạch SAU 1 SỬA (assert cover excision SHA-hits dùng nhầm cover mới `d2eb9b5` thay vì cover của source `3b34e1a` — bài học 35, đã sửa trước khi chạy lại sạch); build fill + fill sạch ngay lần đầu (đoạn SHA-hits 134 dòng / 108 entry; extra-token khớp R279); `daf9540` vẫn 15 lần ngoài đoạn; không cần sửa gì khác trong chuỗi fill/build vòng này.
- R279 figures re-verified sạch (749/3232/+396284 tại `d2eb9b5` = 748/3230/+395572 tại `3d51a26` + 1 commit, 2 files, 712 insertions) NGOẠI TRỪ dòng "main == .bak" của nó (main đã làm tươi ở bước build ~11:57 JST + lúc trình ~12:01 JST).

## Kiểm chứng sau commit nội dung

- Content commit `114347b` đã push: `d2eb9b5..114347b`, ls-remote xác nhận remote head `114347b`, integration `f3db6b3`.
- Hai lần đọc API sau push đều: head `114347b`, 750/3233/+397722, live body R263.
- Scope audit block (`d2eb9b5..114347b`): 3 path / 0 violation. Cumulative tại head: 3233 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`).

## Payload R280

- Dựng sau push bằng `r280_payload.py` từ body v2 + Head làm tươi tới `114347b`.
- Body payload: 95.101 ký tự, sha `72155d8d`; JSON 106.190 byte (headroom 24.882 byte so với trần 131.072); tiêu đề 765 ký tự, kết thúc "+ R280"; main == .bak == 2 bản sao prepost, sha256 `a5101733`.
- ĐÍNH CHÍNH HEAD (bài học 72): payload chuẩn bị trên ghi head nội dung `114347b` — sau khi commit báo cáo này + push, main sẽ được làm tươi sang head báo cáo (đọc API mới sau push báo cáo); .bak + 2 bản sao prepost giữ nguyên bản chuẩn bị; số đo v2 ghi trong nhật ký `~/memory/2026-11-27.md` + tin cuối lượt chạy, và hàng R280 trong index (vòng sau) ghi cả hai phiên bản.
- Payload SẴN SÀNG TRÌNH BÀY (lượt chạy bắt đầu ~12:40 JST, giờ làm việc); CHƯA ĐĂNG — cần thẻ duyệt của chủ dự án. Thẻ sống ~30 phút — bấm khi còn ngồi máy.
- Widget R279 giờ stale, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 95.353 ký tự, headroom 9.647 so với 105.000. Gọn đơn tiếp theo R188 ở R281. Đoạn đầy còn lại R188..R279 = 92 đoạn; khối gọn R2–R187 = 186 dòng.
- Net vòng này +187 khi head line tăng 125 ký tự; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(72) xem báo cáo các vòng trước. Bài học (73) MỚI VÒNG NÀY (R280):

(a) `pull_request_read` cần `pullNumber` (camelCase) — lần đầu truyền `pull_number` lỗi "missing required parameter: pullNumber", thử lại với `pullNumber` thành công ngay; `issue_read` vẫn dùng `issue_number` (bài học 66a).
(b) Payload R279 có BA phiên bản — hàng R279 trong index ghi cả ba, đo từ đĩa (chuẩn bị 95.021 ký tự / sha `c3a35f50` / JSON 106.102 byte / sha256 `512bea04`; build ~11:57 JST 95.055 / `f3c4787a` / JSON 106.140 byte / sha256 `e0facfab`; trình ~12:01 JST 94.964 / `6c6a5c38` / JSON 106.027 byte / sha256 `5d4e44c2`, head line 1092 ký tự, mergeable true/clean); lần làm tươi lúc trình chỉ đổi cụm mergeable (unstable → true/clean) và rút ngắn head line 1183 → 1092.
(c) Transform chạy sạch ngay lần đầu; shift checker 62/62 sạch sau 1 sửa (assert cover excision SHA-hits — bài học 35: cover phải là của source `3b34e1a`, không phải cover mới `d2eb9b5`); fill sạch (134 dòng / 108 entry); R279 figures re-verified sạch NGOẠI TRỪ dòng "main == .bak" (main làm tươi ở build + trình); `daf9540` vẫn 15; không cờ execution-risk; gọn đơn R187 thứ hai mươi; trail 28 ký tự; net +187; head line TĂNG 1.294 → 1.419 (+125, lần đầu tăng mạnh — ghi cả hai lần làm tươi payload R279); nhãn giờ tách riêng từng bước (lấy từ mtime, bài học 71); ls-remote CHẠY ĐƯỢC vòng này — remote head + integration tip xác nhận qua ls-remote.
