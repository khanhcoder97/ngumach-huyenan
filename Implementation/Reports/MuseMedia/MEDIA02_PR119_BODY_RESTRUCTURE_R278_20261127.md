# MEDIA-02 — PR #119 Body Restructure R278 (2026-11-27)

## Tóm tắt

- Vòng R278: gọn ĐƠN R185 (gọn đơn thứ MƯỜI TÁM); index + body v2 + checker đồng bộ tới head `707170c` (745 commit / 3226 file / +392009 từ merge-base `cf17178`); merge-tree tại `707170c` vs integration `f3db6b3` exit 0, tree `80cab76a…`.
- Không có sự kiện đăng bài giữa các vòng: payload R277 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R277 bị R278 thay thế.
- CẢNH BÁO STALE: bản chính (main) payload R277 ĐÃ ĐƯỢC làm tươi tại lúc trình bày ~10:02 JST (Head `707170c`, body 94.850 ký tự, sha `b212da28`) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (94.869 ký tự, sha `e4668320`, sha256 `5293547d`); dòng "main == .bak" trong báo cáo R277 đã lỗi thời — hàng R277 trong index ghi cả hai phiên bản, đo từ đĩa.
- Một giai đoạn (~10:40–~11:00 JST): fetch ~10:40 JST, đọc live, sửa index + body v2, chuỗi checker tới `check_pr119_restructure_r278_v1.py` + điền SHA-hits, checker PASS 159/159 ngay lần đầu, scope audit block 3 path / 0 violation, content commit `afc8d92` + push, đọc live sau push (2 lần), báo cáo + payload R278.
- Content commit `afc8d92` (~10:57 JST): 3 file, 1436 insertions, 11 deletions; scope audit block (`707170c..afc8d92`) 3 path / 0 violation; cumulative tại `afc8d92` = 3227 path / 1 violation — artifact `.gitattributes` đã biết.
- Số đếm tại `afc8d92`: 746 commit / 3227 file / +393434 — khớp API đọc sau push. Additions: 392009 + (1436 − 11) = 393434.
- Merge-tree tại `afc8d92` vs `f3db6b3`: exit 0, tree `6a8a4ef9…`.
- Push: `707170c..afc8d92`; ls-remote xác nhận remote head `afc8d92` VÀ integration `f3db6b3` (ls-remote chạy được vòng này, khác R277 bị proxy reset).
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- Không có cờ execution-risk vòng này.
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (connector, ~10:41 JST theo mtime file — xem ĐÍNH CHÍNH (a) dưới đây): head `707170c`, 745/3226/+392009, mergeable null / state clean, updated_at 2026-11-27T00:58:50Z, live body R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề kết thúc "+ R263".
- Issue #116 (connector, ~10:41 JST theo mtime file): 34 comment, updated_at 2026-11-13T19:24:49Z, không chỉ đạo mới.
- Đọc sau push (connector, 2 lần, ~10:57 + ~10:58 JST): PR head `afc8d92`, 746/3227/+393434 — khớp git tại content commit; mergeable null, state clean ở lần đọc đầu rồi unstable ở lần đọc thứ hai (CI đang chạy — trạng thái dao động; payload ghi lần đọc sau, unstable); live body vẫn R263 (94.825, sha `07316552`, 0 U+FFFD), tiêu đề kết thúc "+ R263", updated_at 2026-11-27T01:57:31Z (đổi do push R278 cập nhật head, body không đổi). Issue #116 không đọc lại sau push (ghi rõ trong head line của payload).

## Mốc giờ

- Fetch: ~10:40 JST (FETCH_HEAD mtime 10:40:32 JST). Đọc live PR/issue: ~10:41 JST (mtime file 10:41:19 / 10:41:27 JST). Đếm git: ~10:44 JST tại `707170c`.
- Checker chạy: ~10:57 JST (validation JSON mtime 10:57:05 JST). Content commit `afc8d92`: ~10:57 JST (10:57:20 JST). Push: ~10:57 JST. Đọc sau push: ~10:57:37 + ~10:58:32 JST (mtime file). Báo cáo này: ~11:00 JST.

## R278 đóng khoảng trống

- Body v2: 95.103 ký tự (net +29 so với R277), headroom 9.897 so với 105.000; head line 1.293 ký tự (delta −33 — lần đầu head line THU NHỎ); R185 gọn 486 → 214 (gọn đơn thứ mười tám); đoạn R277 đúng 270 ký tự (theo checker).
- Checker `check_pr119_restructure_r278_v1.py`: PASS 159/159 (159 = 158 + 1 check row-convention mới cho tuple R276).
- Transform edit chạy sạch ngay lần đầu (không assertion nào nổ); shift checker 62/62 cặp sạch ngay lần đầu; build fill + fill sạch ngay lần đầu (đoạn SHA-hits 129 dòng / 104 entry; extra-token khớp R277); `daf9540` vẫn 15 lần ngoài đoạn; không cần sửa gì trong chuỗi fill/build vòng này.
- R277 figures re-verified sạch (745/3226/+392009 tại `707170c` = 744/3224/+391307 tại `170cae0` + 1 commit, 2 file, 702 insertions) NGOẠI TRỪ dòng "main == .bak" của nó (main đã làm tươi ~10:02 JST).

## Kiểm chứng sau commit nội dung

- Content commit `afc8d92` đã push: `707170c..afc8d92`, ls-remote xác nhận remote head `afc8d92`, integration `f3db6b3`.
- Hai lần đọc API sau push đều: head `afc8d92`, 746/3227/+393434, live body R263.
- Scope audit block (`707170c..afc8d92`): 3 path / 0 violation. Cumulative tại head: 3227 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`).

## Payload R278

- Dựng sau push bằng `r278_payload.py` từ body v2 + Head làm tươi tới `afc8d92`.
- Body payload: 94.992 ký tự, sha `edbcc5c4`; JSON 106.061 byte (headroom 25.011 byte so với trần 131.072); tiêu đề 765 ký tự, kết thúc "+ R278"; main == .bak == 2 bản sao prepost, sha256 `48f46f41`.
- Payload SẴN SÀNG TRÌNH BÀY (lượt chạy bắt đầu ~10:40 JST, giờ làm việc); CHƯA ĐĂNG — cần thẻ duyệt của chủ dự án. Thẻ sống ~30 phút — bấm khi còn ngồi máy.
- Widget R277 giờ stale, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 95.103 ký tự, headroom 9.897 so với 105.000. Gọn đơn tiếp theo R186 ở R279. Đoạn đầy còn lại R186..R277 = 92 đoạn; khối gọn R2–R185 = 184 dòng.
- Net vòng này +29 khi head line thu nhỏ 33 ký tự; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(70) xem báo cáo các vòng trước. Bài học (71) MỚI VÒNG NÀY (R278):

(a) ĐÍNH CHÍNH NHÃN GIỜ — nhãn giờ đọc PR/issue trước push trong index/body v2 đã commit ("~10:42/~10:43 JST") chậm ~1–2 phút so với mtime file thật (file đọc PR 10:41:19 JST, file đọc issue 10:41:27 JST) — mọi SỐ ĐO đều đúng, chỉ nhãn sai; từ vòng này mọi nhãn giờ đều lấy từ mtime (head line của payload đã ghi ~10:41 JST); R279 mang đính chính vào dòng của nó. (Cùng dạng lỗi đã gặp ở R267: nhãn chậm ~2–3 phút, số đo đúng.)
(b) Mergeable_state DAO ĐỘNG giữa hai lần đọc sau push (clean ~10:57, unstable ~10:58) — payload ghi lần đọc sau (unstable); luồng chính làm tươi ở lúc trình bày nếu CI đã xong (bài học 39).
(c) Transform chạy sạch ngay lần đầu; shift checker 62/62 sạch ngay lần đầu; fill sạch (129 dòng / 104 entry); R277 figures re-verified sạch NGOẠI TRỪ dòng "main == .bak" (main làm tươi ~10:02 JST); `daf9540` vẫn 15; không cờ execution-risk; gọn đơn R185 thứ mười tám; trail 28; net +29; head line THU 1.326 → 1.293 (−33); nhãn giờ tách riêng từng bước; ls-remote KHÔNG bị proxy reset vòng này — remote head + integration tip xác nhận qua ls-remote.
