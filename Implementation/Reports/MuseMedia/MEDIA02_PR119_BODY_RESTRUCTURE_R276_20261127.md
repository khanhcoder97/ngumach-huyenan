# MEDIA-02 — PR #119 Body Restructure R276 (2026-11-27)

## Tóm tắt

- Khối: body restructure R276 — gọn ĐƠN R183 (gọn đơn thứ MƯỜI SÁU; gọn đơn bắt đầu ở R168); index + body v2 + checker đồng bộ tới head `7e44e0c` (741 commit / 3220 file / +387773 từ merge-base `cf17178`); merge-tree tại `7e44e0c` vs integration `f3db6b3` exit 0, tree `13026b07…`.
- SỰ KIỆN ĐĂNG GIỮA HAI VÒNG: không có — payload R275 CHƯA ĐĂNG, live body vẫn R263 (94.825 ký tự, sha `07316552`); payload R275 sẵn sàng trình từ vòng trước, bị R276 supersede trước khi đăng.
- Vòng này chạy MỘT PHA (~08:40–09:04 JST): fetch ~08:40 JST, đọc live, áp edit index + body v2, dựng chuỗi checker tới `check_pr119_restructure_r276_v1.py` + fill SHA-hits, checker chạy sạch **PASS 157/157** ngay lần đầu, scope audit block **3 path / 0 violation**, commit nội dung `5a51e58` + push (ls-remote xác minh), đọc live post-push (2 lần), viết báo cáo này + payload R276.
- Đọc live post-push (~09:01 + ~09:02 JST, connector, 2 lần): PR head `5a51e58`, 742 commit / 3221 file / +389187 — khớp đếm git tại commit nội dung; mergeable **null / state unstable** tại head mới (CI đang chạy — cả 2 lần đọc); live body vẫn R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề kết thúc "+ R263", updated_at 2026-11-27T00:01:21Z (đổi do push R276 cập nhật head, body không đổi). Issue #116: **34 comment**, updated_at 2026-11-13T19:24:49Z, mới nhất ACK `6862732081`, **không chỉ đạo mới kể từ Gói 39 (`6815238814`)**.
- Body v2: **94.898 ký tự** (net +108 so với R275), headroom **10.102** so với 105.000; head line 1.228 ký tự (không đổi — lần thứ mười liên tiếp); R183 gọn 440 → 214 (gọn đơn thứ mười sáu); đoạn R275 đúng 270 ký tự (theo checker).
- Commit nội dung `5a51e58` (~09:00 JST): 3 file, 1425 insertions, 11 deletions; scope audit block (`7e44e0c..5a51e58`) **3 path / 0 violation**; cumulative tại `5a51e58` = 3221 path / 1 violation — artifact `.gitattributes` ở merge-base đã biết.
- Payload R276 chuẩn bị sau push (dựng từ body v2 + đoạn Head làm tươi theo head sau push): body 94.791 ký tự, sha `473262ea` (xem mục Payload), **SẴN SÀNG TRÌNH** — lượt chạy bắt đầu ~08:40 JST, kết thúc ~09:04 JST trong giờ làm việc; chưa đăng — cần thẻ duyệt của chủ dự án. Lưu ý: mergeable_state trong payload là **unstable** (CI đang chạy lúc đọc post-push) — luồng chính làm tươi Head lúc trình nếu CI đã xong (bài học 39).

## Đọc live

- Lượt này, đọc trước push (connector): live body R263 (94.825 ký tự, sha `07316552`, byte-exact với file JSON R263 trên đĩa, 0 U+FFFD — một lần đọc sạch, không cần đọc lại); mergeable_state clean tại `7e44e0c` (mergeable không có trong trả lời — khóa vắng, như ở R272/R273/R274/R275; state clean là giá trị vận hành); tiêu đề kết thúc "+ R263"; updated_at 2026-11-26T22:54:48Z. Issue read: connector (call-read-tool, method get, `issue_number`, ~08:42 JST): 34 comment, updated_at 2026-11-13T19:24:49Z — không chỉ đạo mới. Không thử call-tool get_comments lượt này (count + updated_at không đổi so với lần get_comments đã xác minh ở R265).
- Sau push (~09:01 JST + ~09:02 JST, connector, 2 lần đọc): API — head `5a51e58`, 742/3221, mergeable null, mergeable_state **unstable** (CI đang chạy), live body R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề 765 ký tự kết thúc "+ R263", updated_at 2026-11-27T00:01:21Z; issue #116 không đọc lại sau push (ghi rõ trong head line của payload).
- Suy ra từ git tại `5a51e58`: rev-list `cf17178..5a51e58` = 742; diff `--name-only` = 3221 file; `--shortstat` = 389187 insertions, 0 deletions — khớp đọc API; merge-tree `5a51e58` vs `f3db6b3` exit 0, tree `acadbd55…`; tại `7e44e0c`: 741/3220/+387773 (khớp dòng cumulative của index R276).
- PR read base.sha `f3832338` là stale cache (ancestor của tip integration `f3db6b3` — merge PR #118 ngày 2026-11-05); ls-remote xác minh tip integration vẫn `f3db6b3`, không đổi; merge-tree chạy với `f3db6b3` như mọi vòng.

## Mốc giờ

- Fetch lượt này chạy đúng giờ hẹn: lần fetch đầu ~08:40 JST (lượt chạy bắt đầu 08:40:16 JST; `.git/FETCH_HEAD` mtime 08:40:32 JST); các số đếm git (741/3220/+387773) đo ~08:43 JST.
- Đọc PR chạy ~08:42 JST (file `pr119_read_r276.json` mtime 08:41:41 JST); đọc issue chạy ~08:42 JST (file `issue116_read_r276.json` mtime 08:41:43 JST — truyền `issue_number` ngay lần đầu, không lỗi).
- Transform/edit chạy 08:50 JST (mtime file: transform 08:50:18, edit 08:50:29). Shift checker: lần chạy đầu dừng ở cặp 21 (assertion bắt old-string sai — xem bài học 69), sửa xong chạy sạch 62/62 cặp (viết shift 08:56:55); build fill + fill chạy sạch ngay lần đầu (124 dòng / 100 entry; extra-token 43 khớp R275); validation JSON 09:00:11; commit nội dung 09:00:44 JST; push xong ~09:01 JST. Đọc post-push 09:01:31 + 09:02:31 JST; payload ~09:03 JST.

## R276 đóng khoảng trống

- Delivery index: tiêu đề head → `7e44e0c`; dòng milestone → 741/3220/387773; delta `c7117ef..7e44e0c`: 2 path, 694 insertions, 0 deletions; một dòng được thêm — R275 (`c7117ef`/`7e44e0c`), ghi payload R275 (94.683 ký tự, sha `b172a58d`, CHƯA ĐĂNG — bị R276 supersede) + đính chính lesson (44) của checker R275 + row-convention (dòng R274 = 3218) + sửa dòng Ghi chú + sửa câu "lượt cập nhật này" (chính R275); không có ACK riêng cho R275. Index bao quát mọi khối tới `7e44e0c`; 2 commit của R276 gộp vào ở R277.
- Body v2: head line đồng bộ tới `7e44e0c` · 741 · 3220 (additions 387773, Gói 39 ID 6815238814, tree `13026b07…`, mergeable_state clean tại `7e44e0c` theo đọc lượt này), cộng đoạn R275 và ghi chú R276. Gọn: đoạn R183 (440 → 214) — gọn ĐƠN thứ mười sáu. Body 94.898 ký tự — net +108 so với R275 (−226 R183 + 271 đoạn mới + 28 trail + 30 tiêu đề + 5 Ghi-chú list "/R275" + 0 Ghi-chú range "R3–R182"→"R3–R183" + 0 head line — các thành phần theo projection của chuỗi edit; tổng net +108 đo trực tiếp từ đĩa: 94.790 → 94.898).
- Checker `check_pr119_restructure_r276_v1.py`: PASS **157/157** ngay lần đầu (`--out` ghi validation JSON của vòng này; trường "checkpoint" trong JSON mang nhãn vòng trước "PR119 BODY RESTRUCTURE R275" — quy ước đặt tên mang sang của chuỗi shift, không phải lỗi số liệu; checks 157/157, failures []). 157 = 156 + đúng 1 check row-convention mới (tuple R274), khớp bài học vòng R264 mục 6 ("mỗi vòng chỉ thêm đúng 1 check row-convention").
- Fill SHA-hits: `fill_sha_hits_r276.py` đã chạy thành công — đoạn SHA-hits 124 dòng / 100 entry đã điền đầy vào checker. Entry set: 98 entry của R275 + 2 entry mới `7e44e0c` (cover) + `c7117ef` (nội dung R275) lên đầu (100 entry — KHÔNG trừ `daf9540`). Extra-token khớp hoàn toàn với R275 (43 token, cùng số lần xuất hiện). daf9540 giữ 15 lần ngoài đoạn (lesson 45 — không nhắc sha theo nghĩa đen nên số lần không đổi).

## Kiểm chứng sau commit nội dung

- Commit nội dung `5a51e5837c987ef8b00427e212880631996fa500` (~09:00 JST): 3 file (body v2, delivery index, checker.py), 1425 insertions, 11 deletions; scope audit block (`7e44e0c..5a51e58`): **3 path / 0 violation**; cumulative tại `5a51e58`: 3221 path / 1 violation — artifact `.gitattributes` đã biết (byte-identical với integration `f3db6b3`, sha256 `23352e4c…`; khác merge-base `cf17178` sha256 `54ee7996…` — đúng bản chất artifact merge-base, không phải lệch thật; cả hai sha đo lại từ git lượt này).
- Đếm tại `5a51e58`: **742 commit / 3221 file / +389187** — khớp đọc API post-push. Dòng R275 trong index ghi cumulative 3221 — đã xác minh sau commit (diff tại `5a51e58` = 3221, gồm 3220 tại `7e44e0c` + 1 checker mới). Lưu ý số học: additions tích lũy = 387773 + (1425 − 11) = 389187 — commit nội dung có 11 deletions nên không cộng thẳng 1425 (xem bài học 69).
- Merge-tree tại `5a51e58` vs `f3db6b3`: exit 0, tree `acadbd55…`.
- Push: `7e44e0c..5a51e58` lên `muse/media-production-20261104` (deploy key, không force-push); ls-remote xác minh remote head = `5a51e5837c987ef8b00427e212880631996fa500`.
- Working tree sau commit nội dung: sạch (chỉ còn báo cáo + validation JSON của vòng này, commit ở commit báo cáo).
- Không có execution-risk flag lượt này; không có hành động nào của vòng bị chặn.
- Cảnh báo SyntaxWarning `invalid escape sequence '\`'` khi chạy checker: ĐÃ CÓ từ checker R265 — không phải khuyết điểm vòng này, không ảnh hưởng PASS.
- Transform edit: chạy sạch ngay lần đầu (không assertion nào bắt lỗi — quy tắc anchor/identifier bài học (41) đã giữ); shift checker: lần đầu dừng ở cặp 21 (assertion bắt old-string sai — xem bài học 69), sửa xong chạy sạch 62/62 cặp; build fill + fill chạy sạch ngay lần đầu (124 dòng / 100 entry; extra-token 43 khớp R275). Không có đính chính nào cần sửa trong chuỗi fill/build lượt này.

## Payload R276

- Dựng bởi vòng này sau push (script `r276_payload.py` trong goal hidden_files) từ body v2 của vòng + đoạn Head làm tươi DUY NHẤT sang head sau push: head `5a51e58` · 742 · 3221, additions 389187, mergeable **null / unstable** tại `5a51e58` (đọc API tươi post-push ~09:01 + ~09:02 JST — CI đang chạy trên head mới; luồng chính làm tươi Head lúc trình nếu CI đã xong), live body R263 (94.825 ký tự, sha `07316552`, updated_at 2026-11-27T00:01:21Z), merge-tree tree `acadbd55…`, issue #116 34 comment (đọc trước push lượt này ~08:42 JST, không đọc lại sau push — ghi rõ trong head line).
- Body **94.791 ký tự, sha `473262ea`**; JSON 105.833 byte < trần 131.072 (còn 25.239 byte); tiêu đề 765 ký tự kết thúc "+ R276" (hậu tố THAY, không nối — bài học R120); envelope đủ (owner `khanhcoder97`, repo `ngumach-huyenan`, pullNumber 119); file `~/workspace/godot-prototype/pr_comments/pr119_update_body_v2_r276.json` + `.bak` byte-identical (sha256 `8d024817`) + bản sao byte-identical trong `.bak-prepost-20261124/` và `.bak-prepost-20261126/`.
- **CHƯA ĐĂNG** — cần thẻ duyệt của chủ dự án; **SẴN SÀNG TRÌNH** (lượt chạy bắt đầu ~08:40 JST, kết thúc ~09:04 JST trong giờ làm việc). Lưu ý: thẻ duyệt hết hạn sau ~30 phút chờ (đã 10 lần) — nên bấm khi còn ngồi máy. Lưu ý thêm: payload R275 nay ĐÃ LỖI THỜI (head đã sang `5a51e58`) — KHÔNG bấm widget R275.

## Cảnh báo headroom

Body v2 hiện 94.898 ký tự, headroom 10.102. Gọn ĐƠN tiếp theo là R184 ở vòng R277. Đoạn đầy đủ còn lại R184..R275 = 92 đoạn; khối gọn R2–R183 = 182 dòng. Ước tính net mỗi vòng gọn đơn ≈ −100..−250 — nhưng vòng này net +108 vì đoạn R183 dài 440 ký tự (gọn −226 thay vì −201); headroom vẫn an toàn dài hạn. Lưu ý: độ dài đoạn đầy đủ không cố định (~415–472 đã thấy, nay 440) — không giả định net +133 cho vòng sau; đo từ đĩa mỗi vòng.

## Bài học

Lessons carried: toàn bộ danh sách bài học (1)–(68) trong báo cáo R262 + R263 + R264 + R265 + R266 + R267 + R268 + R269 + R270 + R271 + R272 + R273 + R274 + R275 cùng thư mục giữ nguyên hiệu lực. Mới vòng này:

(69) NEW THIS ROUND (R276) — ba điều: (a) SHIFT PAIR OLD PHẢI LÀ TEXT THẬT TRONG SOURCE CHECKER: cặp 21 của shift_checker_r276.py lần đầu dùng old-string từ cặp tương ứng của shift trước (bản R274) thay vì text thật trong checker R275 (bản R275, dry-run 94.790) — assertion bắt ngay (found 0), sửa xong chạy sạch 62/62; quy tắc: old của mỗi cặp shift = NEW của shift vòng trước, không phải OLD của nó. (b) ASSERT COVER TRONG EXCISION PHẢI LÀ COVER CỦA SOURCE: đoạn SHA-hits trong checker nguồn bắt đầu bằng cover cũ (`2de586d`), cover mới (`7e44e0c`) chỉ xuất hiện sau fill — đã sửa assert trước khi chạy lần đầu. (c) ADDITIONS TÍCH LŨY TRỪ DELETIONS: commit nội dung có 11 deletions nên additions tại head mới = 387773 + (1425 − 11) = 389187, không phải 387773 + 1425; mọi con số additions đều đo từ git (`--shortstat`), không cộng tay từ stat của commit.
