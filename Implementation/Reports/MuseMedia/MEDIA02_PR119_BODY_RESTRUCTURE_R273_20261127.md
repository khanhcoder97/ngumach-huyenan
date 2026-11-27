# MEDIA-02 — PR #119 Body Restructure R273 (2026-11-27)

## Tóm tắt

- Khối: body restructure R273 — gọn ĐƠN R180 (gọn đơn thứ MƯỜI BA; gọn đơn bắt đầu ở R168); index + body v2 + checker đồng bộ tới head `e71bce5` (735 commit / 3211 file / +381486 từ merge-base `cf17178`); merge-tree tại `e71bce5` vs integration `f3db6b3` exit 0, tree `13ffa6d7…`.
- SỰ KIỆN ĐĂNG GIỮA HAI VÒNG: không có — payload R272 CHƯA ĐĂNG, live body vẫn R263 (94.825 ký tự, sha `07316552`); payload R272 sẵn sàng trình từ vòng trước, bị R273 supersede trước khi đăng.
- Vòng này chạy MỘT PHA (~05:41–05:58 JST): fetch ~05:41 JST, đọc live, áp edit index + body v2, dựng chuỗi checker tới `check_pr119_restructure_r273_v1.py` + fill SHA-hits, checker chạy sạch **PASS 154/154** ngay lần đầu, scope audit block **3 path / 0 violation**, commit nội dung `5dc1302` + push (ls-remote xác minh), đọc live post-push (2 lần), viết báo cáo này + payload R273.
- Đọc live post-push (~05:56 + ~05:57 JST, connector, 2 lần): PR head `5dc1302`, 736 commit / 3212 file / +382888 — khớp đếm git tại commit nội dung; mergeable **null / state unstable** tại head mới (CI đang chạy — cả 2 lần đọc); live body vẫn R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề kết thúc "+ R263", updated_at 2026-11-26T20:56:22Z (đổi do push R273 cập nhật head, body không đổi). Issue #116: **34 comment**, updated_at 2026-11-13T19:24:49Z, mới nhất ACK `6862732081`, **không chỉ đạo mới kể từ Gói 39 (`6815238814`)**.
- Body v2: **94.524 ký tự** (net +114 so với R272), headroom **10.476** so với 105.000; head line 1.228 ký tự (không đổi — lần thứ bảy liên tiếp); R180 gọn 434 → 214 (gọn đơn thứ mười ba); đoạn R272 đúng 270 ký tự (theo checker).
- Commit nội dung `5dc1302` (~05:56 JST): 3 file, 1413 insertions, 11 deletions; scope audit block (`e71bce5..5dc1302`) **3 path / 0 violation**; cumulative tại `5dc1302` = 3212 path / 1 violation — artifact `.gitattributes` ở merge-base đã biết.
- Payload R273 chuẩn bị sau push (dựng từ body v2 + đoạn Head làm tươi theo head sau push): body 94.417 ký tự, sha `092f8ef5` (xem mục Payload), **GIỮ LẠI** — ngoài giờ làm việc (lượt chạy bắt đầu ~05:40 JST), KHÔNG trình; chưa đăng — cần thẻ duyệt của chủ dự án. Lưu ý: mergeable_state trong payload là **unstable** (CI đang chạy lúc đọc post-push) — luồng chính làm tươi Head lúc trình nếu CI đã xong (bài học 39).

## Đọc live

- Lượt này, đọc trước push (connector): live body R263 (94.825 ký tự, sha `07316552`, byte-exact với file JSON R263 trên đĩa, 0 U+FFFD — một lần đọc sạch, không cần đọc lại); mergeable_state clean tại `e71bce5` (mergeable không có trong trả lời — khóa vắng, như ở R272; state clean là giá trị vận hành); tiêu đề kết thúc "+ R263"; updated_at 2026-11-26T19:54:58Z. Issue read: lần đầu truyền `issueNumber` nên lỗi (missing required parameter: issue_number); thử lại với `issue_number` thành công (call-read-tool, method get, ~05:42 JST): 34 comment, updated_at 2026-11-13T19:24:49Z — không chỉ đạo mới. Không thử call-tool get_comments lượt này (count + updated_at không đổi so với lần get_comments đã xác minh ở R265).
- Sau push (~05:56 JST + ~05:57 JST, connector, 2 lần đọc): API — head `5dc1302`, 736/3212, mergeable null, mergeable_state **unstable** (CI đang chạy), live body R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề 765 ký tự kết thúc "+ R263", updated_at 2026-11-26T20:56:22Z; issue #116 không đọc lại sau push (ghi rõ trong head line của payload).
- Suy ra từ git tại `5dc1302`: rev-list `cf17178..5dc1302` = 736; diff `--name-only` = 3212 file; `--shortstat` = 382888 insertions, 0 deletions — khớp đọc API; merge-tree `5dc1302` vs `f3db6b3` exit 0, tree `350b6024…`; tại `e71bce5`: 735/3211/+381486 (khớp dòng cumulative của index R273).
- PR read base.sha `f3832338` là stale cache (ancestor của tip integration `f3db6b3` — merge PR #118 ngày 2026-11-05); ls-remote xác minh tip integration vẫn `f3db6b3`, không đổi; merge-tree chạy với `f3db6b3` như mọi vòng.

## Mốc giờ

- Fetch lượt này chạy đúng giờ hẹn: lần fetch đầu ~05:41 JST (lượt chạy bắt đầu 05:40:16 JST; `.git/FETCH_HEAD` mtime 05:41:50 JST); các số đếm git (735/3211/+381486) đo ~05:42 JST.
- Đọc PR chạy ~05:42 JST (file `pr119_read_r273.json` mtime 05:42:09 JST); đọc issue chạy ~05:42 JST (file `issue116_read_r273.json` mtime 05:42:52 JST — lần thử đầu lỗi tên tham số, thử lại thành công cùng phút).
- Transform/edit chạy 05:50 JST (mtime file: transform 05:50:30, edit 05:50:33, body/index 05:50:38). Shift checker chạy sạch 62/62 cặp ngay lần đầu (mtime shift 05:53:58, checker 05:54:56); fill 05:54 (validation JSON 05:55:11); commit nội dung 05:56:03 JST; push xong ~05:56 JST. Đọc post-push 05:56:32 + 05:57:19 JST; payload ~05:58 JST.

## R273 đóng khoảng trống

- Delivery index: tiêu đề head → `e71bce5`; dòng milestone → 735/3211/381486; delta `312d680..e71bce5`: 2 path, 682 insertions, 0 deletions; một dòng được thêm — R272 (`312d680`/`e71bce5`), ghi payload R272 (94.303 ký tự, sha `b6ac34b3`, CHƯA ĐĂNG — bị R273 supersede) + đính chính lesson (41) của checker R272 + row-convention (dòng R271 = 3209) + sửa dòng Ghi chú + sửa câu "lượt cập nhật này" (chính R272); không có ACK riêng cho R272. Index bao quát mọi khối tới `e71bce5`; 2 commit của R273 gộp vào ở R274.
- Body v2: head line đồng bộ tới `e71bce5` · 735 · 3211 (additions 381486, Gói 39 ID 6815238814, tree `13ffa6d7…`, mergeable_state clean tại `e71bce5` theo đọc lượt này), cộng đoạn R272 và ghi chú R273. Gọn: đoạn R180 (434 → 214) — gọn ĐƠN thứ mười ba. Body 94.524 ký tự — net +114 so với R272 (−220 R180 + 271 đoạn mới + 28 trail + 30 tiêu đề + 5 Ghi-chú list "/R272" + 0 Ghi-chú range "R3–R179"→"R3–R180" + 0 head line — các thành phần theo projection của chuỗi edit; tổng net +114 đo trực tiếp từ đĩa: 94.410 → 94.524).
- Checker `check_pr119_restructure_r273_v1.py`: PASS **154/154** ngay lần đầu (`--out` ghi validation JSON của vòng này; trường "checkpoint" trong JSON mang nhãn vòng trước "PR119 BODY RESTRUCTURE R272" — quy ước đặt tên mang sang của chuỗi shift, không phải lỗi số liệu; checks 154/154, failures []). 154 = 153 + đúng 1 check row-convention mới (tuple R271), khớp bài học vòng R264 mục 6 ("mỗi vòng chỉ thêm đúng 1 check row-convention").
- Fill SHA-hits: `fill_sha_hits_r273.py` đã chạy thành công — đoạn SHA-hits 117 dòng / 94 entry đã điền đầy vào checker. Entry set: 92 entry của R272 + 2 entry mới `e71bce5` (cover) + `312d680` (nội dung R272) lên đầu (94 entry — KHÔNG trừ `daf9540`). Extra-token khớp hoàn toàn với R272 (43 token, cùng số lần xuất hiện). daf9540 giữ 15 lần ngoài đoạn (lesson 42 — không nhắc sha theo nghĩa đen nên số lần không đổi).

## Kiểm chứng sau commit nội dung

- Commit nội dung `5dc1302110c56d10acdc7b086423a7f89d33293e` (~05:56 JST): 3 file (body v2, delivery index, checker.py), 1413 insertions, 11 deletions; scope audit block (`e71bce5..5dc1302`): **3 path / 0 violation**; cumulative tại `5dc1302`: 3212 path / 1 violation — artifact `.gitattributes` đã biết (byte-identical với integration `f3db6b3`, sha256 `23352e4c…`; khác merge-base `cf17178` sha256 `54ee7996…` — đúng bản chất artifact merge-base, không phải lệch thật; cả hai sha đo lại từ git lượt này).
- Đếm tại `5dc1302`: **736 commit / 3212 file / +382888** — khớp đọc API post-push. Dòng R272 trong index ghi cumulative 3212 — đã xác minh sau commit (diff tại `5dc1302` = 3212, gồm 3211 tại `e71bce5` + 1 checker mới).
- Merge-tree tại `5dc1302` vs `f3db6b3`: exit 0, tree `350b6024…`.
- Push: `e71bce5..5dc1302` lên `muse/media-production-20261104` (deploy key, không force-push); ls-remote xác minh remote head = `5dc1302110c56d10acdc7b086423a7f89d33293e`.
- Working tree sau commit nội dung: sạch (chỉ còn báo cáo + validation JSON của vòng này, commit ở commit báo cáo).
- Không có execution-risk flag lượt này; không có hành động nào của vòng bị chặn.
- Cảnh báo SyntaxWarning `invalid escape sequence '\`'` khi chạy checker: ĐÃ CÓ từ checker R265 — không phải khuyết điểm vòng này, không ảnh hưởng PASS.
- Transform edit: chạy sạch ngay lần đầu (không assertion nào bắt lỗi — quy tắc anchor/identifier bài học (41) đã giữ); shift checker chạy sạch 62/62 cặp ngay lần đầu; fill chạy sạch ngay lần đầu (117 dòng / 94 entry; extra-token 43 khớp R272).

## Payload R273

- Dựng bởi vòng này sau push (script `r273_payload.py` trong goal hidden_files) từ body v2 của vòng + đoạn Head làm tươi DUY NHẤT sang head sau push: head `5dc1302` · 736 · 3212, additions 382888, mergeable **null / unstable** tại `5dc1302` (đọc API tươi post-push ~05:56 + ~05:57 JST — CI đang chạy trên head mới; luồng chính làm tươi Head lúc trình nếu CI đã xong), live body R263 (94.825 ký tự, sha `07316552`, updated_at 2026-11-26T20:56:22Z), merge-tree tree `350b6024…`, issue #116 34 comment (đọc trước push lượt này ~05:42 JST, không đọc lại sau push — ghi rõ trong head line).
- Body **94.417 ký tự, sha `092f8ef5`**; JSON 105.421 byte < trần 131.072 (còn 25.651 byte); tiêu đề 765 ký tự kết thúc "+ R273" (hậu tố THAY, không nối — bài học R120); envelope đủ (owner `khanhcoder97`, repo `ngumach-huyenan`, pullNumber 119); file `~/workspace/godot-prototype/pr_comments/pr119_update_body_v2_r273.json` + `.bak` byte-identical (sha256 `85881075`) + bản sao byte-identical trong `.bak-prepost-20261124/` và `.bak-prepost-20261126/`.
- **CHƯA ĐĂNG** — cần thẻ duyệt của chủ dự án; **GIỮ LẠI** (ngoài giờ làm việc — lượt chạy bắt đầu ~05:40 JST), luồng chính trình widget trong giờ làm việc. Lưu ý: thẻ duyệt hết hạn sau ~30 phút chờ (đã 10 lần) — nên bấm khi còn ngồi máy. Lưu ý thêm: payload R272 nay ĐÃ LỖI THỜI (head đã sang `5dc1302`) — KHÔNG bấm widget R272.

## Cảnh báo headroom

Body v2 hiện 94.524 ký tự, headroom 10.476. Gọn ĐƠN tiếp theo là R181 ở vòng R274. Đoạn đầy đủ còn lại R181..R272 = 92 đoạn; khối gọn R2–R180 = 179 dòng. Ước tính net mỗi vòng gọn đơn ≈ −100..−250 — nhưng vòng này net +114 vì đoạn R180 ngắn (434 ký tự thay vì ~472); headroom vẫn an toàn dài hạn. Lưu ý: độ dài đoạn đầy đủ không cố định (~434–472 đã thấy) — không giả định net +76 cho vòng sau; đo từ đĩa mỗi vòng.

## Bài học

Lessons carried: toàn bộ danh sách bài học (1)–(65) trong báo cáo R262 + R263 + R264 + R265 + R266 + R267 + R268 + R269 + R270 + R271 + R272 cùng thư mục giữ nguyên hiệu lực. Mới vòng này:

(66) NEW THIS ROUND (R273) — ba điều: (a) ISSUE_READ THAM SỐ SAI TÊN: lần đầu gọi issue_read với `issueNumber` (camelCase) và nhận lỗi "invalid arguments: normalize tool arguments: missing required parameter: issue_number"; thử lại với `issue_number` (snake_case) thành công ngay. Quy tắc bài học (8) đã ghi đúng tên tham số — lỗi này là do người chạy gõ sai, không phải do connector đổi API; khi gọi lại phải dùng đúng tên đã ghi trong bài học, không đoán tên khác. (b) R180 NGẮN HƠN CHUẨN: đoạn đầy đủ R180 chỉ 434 ký tự (các đoạn trước ~472) nên gọn đơn vòng này chỉ −220, net body +114 thay vì +76 ở R271/R272 — độ dài đoạn không cố định, phải đo từ đĩa mỗi vòng, không mang net vòng trước sang. (c) MERGEABLE KEY VẮNG LẦN THỨ HAI: bản đọc PR của R273 cũng không có khóa `mergeable` (như R272) — "mergeable null" trong head line/index là quy ước đã chốt cho dạng trả lời này của MCP, mergeable_state clean là giá trị vận hành; không đổi wording head line vì chuyện này, head line giữ 1228 ký tự lần thứ bảy liên tiếp.
