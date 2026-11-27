# MEDIA-02 — PR #119 Body Restructure R275 (2026-11-27)

## Tóm tắt

- Khối: body restructure R275 — gọn ĐƠN R182 (gọn đơn thứ MƯỜI LĂM; gọn đơn bắt đầu ở R168); index + body v2 + checker đồng bộ tới head `2de586d` (739 commit / 3217 file / +385669 từ merge-base `cf17178`); merge-tree tại `2de586d` vs integration `f3db6b3` exit 0, tree `d00b393c…`.
- SỰ KIỆN ĐĂNG GIỮA HAI VÒNG: không có — payload R274 CHƯA ĐĂNG, live body vẫn R263 (94.825 ký tự, sha `07316552`); payload R274 sẵn sàng trình từ vòng trước, bị R275 supersede trước khi đăng.
- Vòng này chạy MỘT PHA (~07:40–07:53 JST): fetch ~07:40 JST, đọc live, áp edit index + body v2, dựng chuỗi checker tới `check_pr119_restructure_r275_v1.py` + fill SHA-hits, checker chạy sạch **PASS 156/156** ngay lần đầu, scope audit block **3 path / 0 violation**, commit nội dung `c7117ef` + push (ls-remote xác minh), đọc live post-push (2 lần), viết báo cáo này + payload R275.
- Đọc live post-push (~07:51 + ~07:52 JST, connector, 2 lần): PR head `c7117ef`, 740 commit / 3218 file / +387079 — khớp đếm git tại commit nội dung; mergeable **null / state unstable** tại head mới (CI đang chạy — cả 2 lần đọc); live body vẫn R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề kết thúc "+ R263", updated_at 2026-11-26T22:51:47Z (đổi do push R275 cập nhật head, body không đổi). Issue #116: **34 comment**, updated_at 2026-11-13T19:24:49Z, mới nhất ACK `6862732081`, **không chỉ đạo mới kể từ Gói 39 (`6815238814`)**.
- Body v2: **94.790 ký tự** (net +133 so với R274), headroom **10.210** so với 105.000; head line 1.228 ký tự (không đổi — lần thứ chín liên tiếp); R182 gọn 415 → 214 (gọn đơn thứ mười lăm); đoạn R274 đúng 270 ký tự (theo checker).
- Commit nội dung `c7117ef` (~07:51 JST): 3 file, 1421 insertions, 11 deletions; scope audit block (`2de586d..c7117ef`) **3 path / 0 violation**; cumulative tại `c7117ef` = 3218 path / 1 violation — artifact `.gitattributes` ở merge-base đã biết.
- Payload R275 chuẩn bị sau push (dựng từ body v2 + đoạn Head làm tươi theo head sau push): body 94.683 ký tự, sha `b172a58d` (xem mục Payload), **SẴN SÀNG TRÌNH** — lượt chạy bắt đầu ~07:40 JST, kết thúc ~07:54 JST trong giờ làm việc; chưa đăng — cần thẻ duyệt của chủ dự án. Lưu ý: mergeable_state trong payload là **unstable** (CI đang chạy lúc đọc post-push) — luồng chính làm tươi Head lúc trình nếu CI đã xong (bài học 39).

## Đọc live

- Lượt này, đọc trước push (connector): live body R263 (94.825 ký tự, sha `07316552`, byte-exact với file JSON R263 trên đĩa, 0 U+FFFD — một lần đọc sạch, không cần đọc lại); mergeable_state clean tại `2de586d` (mergeable không có trong trả lời — khóa vắng, như ở R272/R273/R274; state clean là giá trị vận hành); tiêu đề kết thúc "+ R263"; updated_at 2026-11-26T22:06:20Z. Issue read: connector (call-read-tool, method get, `issue_number`, ~07:41 JST): 34 comment, updated_at 2026-11-13T19:24:49Z — không chỉ đạo mới. Không thử call-tool get_comments lượt này (count + updated_at không đổi so với lần get_comments đã xác minh ở R265).
- Sau push (~07:51 JST + ~07:52 JST, connector, 2 lần đọc): API — head `c7117ef`, 740/3218, mergeable null, mergeable_state **unstable** (CI đang chạy), live body R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề 765 ký tự kết thúc "+ R263", updated_at 2026-11-26T22:51:47Z; issue #116 không đọc lại sau push (ghi rõ trong head line của payload).
- Suy ra từ git tại `c7117ef`: rev-list `cf17178..c7117ef` = 740; diff `--name-only` = 3218 file; `--shortstat` = 387079 insertions, 0 deletions — khớp đọc API; merge-tree `c7117ef` vs `f3db6b3` exit 0, tree `4efeebfa…`; tại `2de586d`: 739/3217/+385669 (khớp dòng cumulative của index R275).
- PR read base.sha `f3832338` là stale cache (ancestor của tip integration `f3db6b3` — merge PR #118 ngày 2026-11-05); ls-remote xác minh tip integration vẫn `f3db6b3`, không đổi; merge-tree chạy với `f3db6b3` như mọi vòng.

## Mốc giờ

- Fetch lượt này chạy đúng giờ hẹn: lần fetch đầu ~07:40 JST (lượt chạy bắt đầu 07:40:16 JST; `.git/FETCH_HEAD` mtime 07:40:32 JST); các số đếm git (739/3217/+385669) đo ~07:42 JST.
- Đọc PR chạy ~07:41 JST (file `pr119_read_r275.json` mtime 07:41:16 JST); đọc issue chạy ~07:41 JST (file `issue116_read_r275.json` mtime 07:41:25 JST — truyền `issue_number` ngay lần đầu, không lỗi).
- Transform/edit chạy 07:47 JST (mtime file: transform 07:47:46, edit 07:47:51). Shift checker chạy sạch 62/62 cặp ngay lần đầu (viết shift 07:50:16, fill ~07:50, validation JSON 07:51:05); commit nội dung 07:51:27 JST; push xong ~07:51 JST. Đọc post-push 07:51:56 + 07:52:44 JST; payload ~07:53 JST.

## R275 đóng khoảng trống

- Delivery index: tiêu đề head → `2de586d`; dòng milestone → 739/3217/385669; delta `56926f3..2de586d`: 2 path, 690 insertions, 0 deletions; một dòng được thêm — R274 (`56926f3`/`2de586d`), ghi payload R274 (94.550 ký tự, sha `c241a8ef`, CHƯA ĐĂNG — bị R275 supersede) + đính chính lesson (43) của checker R274 + row-convention (dòng R273 = 3215) + sửa dòng Ghi chú + sửa câu "lượt cập nhật này" (chính R274); không có ACK riêng cho R274. Index bao quát mọi khối tới `2de586d`; 2 commit của R275 gộp vào ở R276.
- Body v2: head line đồng bộ tới `2de586d` · 739 · 3217 (additions 385669, Gói 39 ID 6815238814, tree `d00b393c…`, mergeable_state clean tại `2de586d` theo đọc lượt này), cộng đoạn R274 và ghi chú R275. Gọn: đoạn R182 (415 → 214) — gọn ĐƠN thứ mười lăm. Body 94.790 ký tự — net +133 so với R274 (−201 R182 + 271 đoạn mới + 28 trail + 30 tiêu đề + 5 Ghi-chú list "/R274" + 0 Ghi-chú range "R3–R181"→"R3–R182" + 0 head line — các thành phần theo projection của chuỗi edit; tổng net +133 đo trực tiếp từ đĩa: 94.657 → 94.790).
- Checker `check_pr119_restructure_r275_v1.py`: PASS **156/156** ngay lần đầu (`--out` ghi validation JSON của vòng này; trường "checkpoint" trong JSON mang nhãn vòng trước "PR119 BODY RESTRUCTURE R274" — quy ước đặt tên mang sang của chuỗi shift, không phải lỗi số liệu; checks 156/156, failures []). 156 = 155 + đúng 1 check row-convention mới (tuple R273), khớp bài học vòng R264 mục 6 ("mỗi vòng chỉ thêm đúng 1 check row-convention").
- Fill SHA-hits: `fill_sha_hits_r275.py` đã chạy thành công — đoạn SHA-hits 122 dòng / 98 entry đã điền đầy vào checker. Entry set: 96 entry của R274 + 2 entry mới `2de586d` (cover) + `56926f3` (nội dung R274) lên đầu (98 entry — KHÔNG trừ `daf9540`). Extra-token khớp hoàn toàn với R274 (43 token, cùng số lần xuất hiện). daf9540 giữ 15 lần ngoài đoạn (lesson 44 — không nhắc sha theo nghĩa đen nên số lần không đổi).

## Kiểm chứng sau commit nội dung

- Commit nội dung `c7117ef14779c0bbfa3971629c4e205ebab29bcc` (~07:51 JST): 3 file (body v2, delivery index, checker.py), 1421 insertions, 11 deletions; scope audit block (`2de586d..c7117ef`): **3 path / 0 violation**; cumulative tại `c7117ef`: 3218 path / 1 violation — artifact `.gitattributes` đã biết (byte-identical với integration `f3db6b3`, sha256 `23352e4c…`; khác merge-base `cf17178` sha256 `54ee7996…` — đúng bản chất artifact merge-base, không phải lệch thật; cả hai sha đo lại từ git lượt này).
- Đếm tại `c7117ef`: **740 commit / 3218 file / +387079** — khớp đọc API post-push. Dòng R274 trong index ghi cumulative 3218 — đã xác minh sau commit (diff tại `c7117ef` = 3218, gồm 3217 tại `2de586d` + 1 checker mới).
- Merge-tree tại `c7117ef` vs `f3db6b3`: exit 0, tree `4efeebfa…`.
- Push: `2de586d..c7117ef` lên `muse/media-production-20261104` (deploy key, không force-push); ls-remote xác minh remote head = `c7117ef14779c0bbfa3971629c4e205ebab29bcc`.
- Working tree sau commit nội dung: sạch (chỉ còn báo cáo + validation JSON của vòng này, commit ở commit báo cáo).
- Không có execution-risk flag lượt này; không có hành động nào của vòng bị chặn.
- Cảnh báo SyntaxWarning `invalid escape sequence '\`'` khi chạy checker: ĐÃ CÓ từ checker R265 — không phải khuyết điểm vòng này, không ảnh hưởng PASS.
- Transform edit: chạy sạch ngay lần đầu (không assertion nào bắt lỗi — quy tắc anchor/identifier bài học (41) đã giữ); shift checker chạy sạch 62/62 cặp ngay lần đầu; fill chạy sạch ngay lần đầu (122 dòng / 98 entry; extra-token 43 khớp R274). Không có đính chính nào cần sửa trong chuỗi fill/build lượt này (khác R274 — không dùng replace toàn cục cho biến đếm vòng; bài học 67 đã ngấm).

## Payload R275

- Dựng bởi vòng này sau push (script `r275_payload.py` trong goal hidden_files) từ body v2 của vòng + đoạn Head làm tươi DUY NHẤT sang head sau push: head `c7117ef` · 740 · 3218, additions 387079, mergeable **null / unstable** tại `c7117ef` (đọc API tươi post-push ~07:51 + ~07:52 JST — CI đang chạy trên head mới; luồng chính làm tươi Head lúc trình nếu CI đã xong), live body R263 (94.825 ký tự, sha `07316552`, updated_at 2026-11-26T22:51:47Z), merge-tree tree `4efeebfa…`, issue #116 34 comment (đọc trước push lượt này ~07:41 JST, không đọc lại sau push — ghi rõ trong head line).
- Body **94.683 ký tự, sha `b172a58d`**; JSON 105.713 byte < trần 131.072 (còn 25.359 byte); tiêu đề 765 ký tự kết thúc "+ R275" (hậu tố THAY, không nối — bài học R120); envelope đủ (owner `khanhcoder97`, repo `ngumach-huyenan`, pullNumber 119); file `~/workspace/godot-prototype/pr_comments/pr119_update_body_v2_r275.json` + `.bak` byte-identical (sha256 `fb0d5958`) + bản sao byte-identical trong `.bak-prepost-20261124/` và `.bak-prepost-20261126/`.
- **CHƯA ĐĂNG** — cần thẻ duyệt của chủ dự án; **SẴN SÀNG TRÌNH** (lượt chạy bắt đầu ~07:40 JST, kết thúc ~07:54 JST trong giờ làm việc). Lưu ý: thẻ duyệt hết hạn sau ~30 phút chờ (đã 10 lần) — nên bấm khi còn ngồi máy. Lưu ý thêm: payload R274 nay ĐÃ LỖI THỜI (head đã sang `c7117ef`) — KHÔNG bấm widget R274.

## Cảnh báo headroom

Body v2 hiện 94.790 ký tự, headroom 10.210. Gọn ĐƠN tiếp theo là R183 ở vòng R276. Đoạn đầy đủ còn lại R183..R274 = 92 đoạn; khối gọn R2–R182 = 181 dòng. Ước tính net mỗi vòng gọn đơn ≈ −100..−250 — nhưng vòng này net +133 vì đoạn R182 ngắn (415 ký tự thay vì ~472); headroom vẫn an toàn dài hạn. Lưu ý: độ dài đoạn đầy đủ không cố định (~415–472 đã thấy) — không giả định net +76 cho vòng sau; đo từ đĩa mỗi vòng.

## Bài học

Lessons carried: toàn bộ danh sách bài học (1)–(67) trong báo cáo R262 + R263 + R264 + R265 + R266 + R267 + R268 + R269 + R270 + R271 + R272 + R273 + R274 cùng thư mục giữ nguyên hiệu lực. Mới vòng này:

(68) NEW THIS ROUND (R275) — ba điều: (a) MERGE-TREE SAI DẠNG IN DUMP KHỔNG LỒ: lệnh `git merge-tree <base> <branch1> <branch2>` (dạng 3 đối số cũ) in toàn bộ nội dung file thêm mới (~5,8 MB) dù merge sạch — chỉ dùng dạng `git merge-tree --write-tree <head> <integration>` như mọi báo cáo đã ghi (in đúng 1 dòng tree OID, exit 0); vòng này đã dùng nhầm dạng cũ 1 lần trước khi chạy lại dạng đúng (tree `d00b393c…` tại `2de586d`, `4efeebfa…` tại `c7117ef`). (b) JSON ĐO BẰNG BYTE, KHÔNG PHẢI KÝ TỰ: file payload R274 dài 105.567 byte nhưng Python len(text) chỉ 95.787 ký tự do tiếng Việt đa byte — mọi con số "JSON … byte" trong hàng/báo cáo đều phải là len(bytes trên đĩa), đã đo lại lượt này (R275: 105.713 byte, sha256 `fb0d5958`). (c) CHUỖI CHẠY SẠCH NGAY LẦN ĐẦU CẢ BA TẦNG: transform edit, shift checker 62/62 cặp, build fill + fill (122 dòng / 98 entry) đều không assertion nào bắt lỗi — chuỗi đã ổn định hai vòng liên tiếp (R274 + R275); R182 lại 415 ký tự như R181 nên net +133 lặp lại — đo từ đĩa mỗi vòng, không giả định.
