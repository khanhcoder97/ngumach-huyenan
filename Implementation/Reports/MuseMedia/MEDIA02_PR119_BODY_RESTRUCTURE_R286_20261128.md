# MEDIA-02 — PR #119 Body Restructure R286 (2026-11-28)

## Tóm tắt

- Vòng R286: gọn ĐƠN R193 (gọn đơn thứ HAI MƯƠI SÁU); index + body v2 + checker đồng bộ tới head `8cb82a1` (761 commit / 3250 file / +409260 từ merge-base `cf17178`); merge-tree tại `8cb82a1` vs integration `f3db6b3` exit 0, tree `59374920…`.
- Vòng này là lượt định kỳ 00:40 JST 2026-11-28 làm lại R286: lượt 23:40 JST 2026-11-27 đã thử R286 và lỗi ở builder (`build_gen_r286.py` sinh `gen_transform_r286.py` lỗi SyntaxError vì NEW_DOCSTRING mang `"""` mở đầu, py_compile lỗi dòng 5) — không commit gì. Lượt này sửa NEW_DOCSTRING thành plain text, sửa thêm các sai số trong bản nháp LESSON54 (xem Bài học 80), transform chạy sạch lần đầu.
- Transform trên đĩa đã xác minh: body v2 96.075 ký tự, net +33; checker PASS 167/167; content commit `692a033`. Không có sự kiện đăng bài giữa các vòng: payload R285 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R285 bị R286 thay thế.
- CẢNH BÁO STALE (hai phiên bản payload R285): bản chính (main) payload R285 đã làm tươi sau push báo cáo (Head `8cb82a1`, 95.834 ký tự, sha `3f6deda5`, JSON 107.043 byte, sha256 `7616a98b`, head line 1433, mergeable true/clean) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (95.810 ký tự, sha `0efa70f4`, JSON 107.013 byte, sha256 `3bedac01`, head line 1409, Head `1e45131`); cả hai phiên bản đã xác minh lại từ đĩa lượt này; main != .bak. Title 765 ký tự kết "+ R285".
- Content commit `692a033` (~01:32 JST): 3 file, 1440 insertions, 11 deletions; scope audit cumulative 3251 path / 1 violation — artifact `.gitattributes` đã biết (block 3 path / 0 violation mới).
- Số đếm tại `692a033`: 762 commit / 3251 file / +410689 — số đếm git, KHỚP ĐÚNG số API sau push (xem dưới). Additions: 409260 + (1440 − 11) = 410689.
- Merge-tree tại `692a033` vs `f3db6b3`: exit 0, tree `55505935…`.
- Push: `8cb82a1..692a033`; ls-remote xác nhận remote head `692a033` VÀ integration `f3db6b3` (~01:35 JST).
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (public API qua curl, HTTP 200 cả hai lần — bản đọc ~23:40 JST dùng lại + đọc lại ~00:45 JST, giá trị giống hệt, file `hidden_files/pr119_read_r286_2340.json` + `pr119_read_r286_0045.json`): head `8cb82a1`, 761/3250/+409260/0, mergeable true/clean, updated_at 2026-11-27T14:17:59Z, live body R263 băm lại byte-exact (94.825 ký tự, sha `07316552`, 0 U+FFFD); head xác minh không đổi qua fetch (local head = remote head = `8cb82a1`, integration `f3db6b3`).
- Issue #116 (public API qua curl, bản đọc ~23:40 JST + đọc lại ~00:45 JST, file `hidden_files/issue116_read_r286_2340.json` + `issue116_read_r286_0045.json`): đúng 34 comment, mới nhất ACK `6862732081` (2026-11-13); không chỉ đạo mới kể từ Gói 39.
- PR read xác minh lại lượt này `base.sha f3832338` LÀ ancestor của integration `f3db6b3` (20 commit sau — merge PR #118 ngày 2026-11-05); merge-tree vẫn chạy trên `f3db6b3` live như mọi vòng.
- Đọc sau push (public API qua curl, ~01:35 JST, HTTP 200 cả hai, file `hidden_files/pr119_read_r286_after.json` + `issue116_read_r286_after.json`): PR head `692a033`, API 762/3251/+410689/0 — KHỚP ĐÚNG số git tại content commit (không còn lệch như các vòng API lỗi); mergeable true/unstable (CI đang chạy trên head mới — lần clean gần nhất tại `8cb82a1`), updated_at 2026-11-27T16:34:57Z; live body vẫn R263 (94.825 ký tự, sha `07316552` — push không đổi body). Issue #116 đọc lại sau push: vẫn 34 comment, mới nhất 6862732081.

## Mốc giờ

- ~23:40 JST 2026-11-27: lượt định kỳ thử R286, lỗi builder (NEW_DOCSTRING mang `"""` mở đầu → SyntaxError ở gen_transform, dòng 5) — không commit gì.
- ~00:40 JST 2026-11-28: lượt này bắt đầu — sửa builder + LESSON54 nháp, transform chạy sạch lần đầu (body 96.075, net +33); fetch + đọc live (PR/issue đều 200, head `8cb82a1` không đổi).
- ~01:00–01:30 JST: chuỗi checker — `shift_checker_r285.py` thiếu tail (lesson 79a tái diễn ở R285); dựng `gen_pairs_r286.py` (tái tạo 62 pair R285 từ transform_pair của R285) + builder trực tiếp `build_checker_r286.py` + `build_fill_r286.py`; fill chạy sạch lần đầu (146 dòng / 117 entry, đúng dự đoán); checker PASS 167/167.
- ~01:32 JST: scope audit + merge-tree; content commit `692a033` 01:32:56 JST; push ~01:35 JST; đọc sau push; báo cáo này ~01:36 JST.

## R286 đóng khoảng trống

- Body v2: 96.075 ký tự (net +33 so với R285: +271 đoạn R285 mới −182 gọn R193 + 28 trail + 30 tiêu đề + 5 Ghi-chú "/R285" + 0 range R3–R192→R3–R193 −119 head line), headroom 8.925 so với 105.000; head line 1.641 ký tự (−119 — đo từ đĩa, nguyên nhân chưa phân tích); R193 gọn 396 → 214 (gọn đơn thứ hai mươi sáu); đoạn R285 đúng 270 ký tự (theo checker).
- Checker `check_pr119_restructure_r286_v1.py`: PASS 167/167 (166 + 1 check row-convention mới cho tuple R284 `("R284", "1e45131", 3248)`); validation JSON status PASS, failures [].
- ĐÍNH CHÍNH checker R285 (lesson 80, xem Bài học): hàng row-convention trong checker R285 ghi "R283 row 3245 == 4002095" — SAI: 3245 file là tại `0ad0e59` (content R284), `4002095` là 3244 file; câu "therefore" của nó ghi "cites 3250" — SAI 1: hàng R285 cites 3251 (3250 tại `8cb82a1` + 1 checker mới trong content commit R286 — đã xác minh: 3251 file tại `692a033`). Checker R286 ghi đúng cả hai.
- Build fill + fill sạch lần đầu (đoạn SHA-hits 146 dòng / 117 entry — 116 sha của R285 + `8cb82a1` cover + `1e45131` content R285, TRỪ `cac9c07` đã retire; extra-token khớp R285, 43 = 43; chạy lại idempotent); `daf9540` vẫn 15 lần ngoài đoạn; `cac9c07` đo được 0 lần ngoài đoạn (đã retire thật — LESSON55 không nhắc, hàng row-convention + tuple list chỉ cite `b948d93` cho R281).
- Số đếm API sau push khớp đúng số git lần đầu kể từ các vòng API lỗi: 762/3251/+410689/0 tại `692a033` cả hai nguồn.

## Kiểm chứng sau commit nội dung

- Content commit `692a033` đã push: `8cb82a1..692a033`, ls-remote xác nhận remote head `692a033`, integration `f3db6b3`.
- Đọc API sau push (~01:35 JST, HTTP 200): PR head `692a033`; số API 762/3251/+410689/0 khớp đúng số git tại `692a033`; mergeable true/unstable (CI đang chạy); live body vẫn R263. Issue #116 đọc lại sau push: vẫn 34 comment, ACK `6862732081`.
- Scope audit cumulative tại head: 3251 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`); block R286: 3 path / 0 violation mới.

## Payload R286

- Dựng sau push báo cáo bằng `r286_payload.py` từ body v2 + Head làm tươi tới head báo cáo (đọc API mới sau push báo cáo); .bak + 2 bản sao prepost giữ nguyên bản chuẩn bị; số đo v2 ghi trong nhật ký `~/memory/2026-11-28.md` + tin cuối lượt chạy, và hàng R286 trong index (vòng sau) ghi cả hai phiên bản.
- Payload SẴN SÀNG TRÌNH BÀY (đã qua 01:30 JST — luồng chính trình vào sáng mai theo lệnh); CHƯA ĐĂNG — cần thẻ duyệt của chủ dự án. Thẻ sống ~30 phút — bấm khi còn ngồi máy.
- Widget R285 giờ stale, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 96.075 ký tự, headroom 8.925 so với 105.000. Gọn đơn tiếp theo R194 ở R287. Đoạn đầy còn lại R194..R285 = 92 đoạn; khối gọn R2–R193 = 192 dòng.
- Net vòng này +33 khi head line giảm 119; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(79) xem báo cáo các vòng trước. Bài học (80) MỚI VÒNG NÀY (R286):

(a) CHECKER R285 MANG HAI LỖI VĂN BẢN (lesson 80): hàng row-convention ghi "R283 row 3245 == 4002095" (sai — 3245 tại `0ad0e59`, `4002095` là 3244) và câu "therefore" ghi "cites 3250" (sai 1 — hàng R285 cites 3251). Cả hai đều là lỗi chép tay trong văn bản checker, không phải lỗi đếm git (số git đúng: 3245 tại `0ad0e59`, 3250 tại `8cb82a1`). Checker R286 sửa đúng cả hai + thêm check row-convention mới cho tuple R284 bắt lỗi tương tự. Quy tắc: số file tại một sha phải đo từ `git diff --stat merge-base..sha` trước khi ghi vào câu văn, không suy từ vòng trước.
(b) BẢN NHÁP LESSON54 MANG SAI SỐ HỆ THỐNG (lesson 80a): bản nháp builder LESSON54 ghi source cover `8cb82a1` (đúng là `4002095` — head báo cáo R283), added cover `8cb82a1` (đúng là `43b2464` — head báo cáo R284), defect clause mang defect của LESSON52 (`b948d93`/`cac9c07`) thay vì defect thật của LESSON53 (draft cite cover nguồn R282 `352c11c` hai lần), fill "pass 2 (147 dòng)" thay vì lần đầu 145 dòng / 116 entry, "trừ cover R281 đã retire" (sai — R285 không retire sha nào), "net +234" (đó là net R284 — R285 net +287). Mẫu đúng: source cover = head báo cáo R(N−3), added cover = head báo cáo R(N−2); defect/fill/net phải lấy từ checker + báo cáo của vòng trước, không ghi từ trí nhớ vòng.
(c) BUILDER LỖI SYNTAXERROR Ở LƯỢT 23:40 (lesson 80b): `build_gen_r286.py` mang NEW_DOCSTRING có `"""` mở đầu → gen_transform sinh ra lỗi `SyntaxError` dòng 5, lượt 23:40 dừng không commit gì. Sửa NEW_DOCSTRING thành plain text. Quy tắc: docstring nhúng trong script sinh script phải là plain text, không bao giờ mang delimiter `"""`.
(d) TÁI TẠO PAIR KHI SHIFT SCRIPT THIẾU TAIL (lesson 80c): `shift_checker_r285.py` thiếu tail như lesson 79a đã ghi — `gen_pairs_r286.py` tái tạo 62 pair R285 bằng cách chạy lại `transform_pair` của `build_checker_r285.py` trên 62 pair R284, rồi ghi vào `shift_checker_r286.py`; đã xác minh PAIRS 62, `shift()` map R285→R286, `43b2464`→`8cb82a1`, 759→761. Cùng họ lỗi với lesson 79 — đừng tin file shift "đã sửa lần cuối", kiểm chứng bằng cách chạy + đếm pair.
(e) RETIREMENT PHẢI ĐO TỪ ĐĨA (lesson 80d): `cac9c07` retire ở R286 vì đo được 0 lần ngoài đoạn (LESSON55 không nhắc, row-convention + tuple list chỉ cite `b948d93` cho R281) — ngược với R285 khi nó còn 2 lần ngoài đoạn và phải giữ entry. Quy tắc: retire/không-retire quyết bằng đếm thực tế trên checker đã build (placeholder), không suy từ "cover đã cũ".
(f) API KHỚP GIT SAU PUSH (lesson 80e): lần đầu sau nhiều vòng, đọc API sau push (HTTP 200) cho số đếm 762/3251/+410689/0 khớp đúng số git — vì rate-limit đã hết và CI đã tính xong. Khi API lỗi 403 thì ghi rõ "số git, chưa đối chiếu API" như R285; khi API 200 thì đối chiếu và ghi khớp/lệch cụ thể.
