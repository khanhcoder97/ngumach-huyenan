# MEDIA-02 — PR #119 Body Restructure R271 (2026-11-27)

## Tóm tắt

- Khối: body restructure R271 — gọn ĐƠN R178 (gọn đơn thứ MƯỜI MỘT; gọn đơn bắt đầu ở R168); index + body v2 + checker đồng bộ tới head `2482e3b` (731 commit / 3205 file / +377345 từ merge-base `cf17178`); merge-tree tại `2482e3b` vs integration `f3db6b3` exit 0, tree `84239f10…`.
- SỰ KIỆN ĐĂNG GIỮA HAI VÒNG: không có — payload R270 CHƯA ĐĂNG, live body vẫn R263 (94.825 ký tự, sha `07316552`); payload R270 sẵn sàng trình từ vòng trước, bị R271 supersede trước khi đăng.
- Vòng này chạy MỘT PHA (~03:40–04:10 JST): fetch ~03:40 JST, đọc live, áp edit index + body v2, dựng chuỗi checker tới `check_pr119_restructure_r271_v1.py` + fill SHA-hits, checker chạy sạch **PASS 152/152** ngay lần đầu, scope audit block **3 path / 0 violation**, commit nội dung `16dfcfe` + push (ls-remote xác minh), đọc live post-push (2 lần), viết báo cáo này + payload R271.
- Đọc live post-push (~04:06 + ~04:07 JST, connector, 2 lần): PR head `16dfcfe`, 732 commit / 3206 file / +378733 — khớp đếm git tại commit nội dung; mergeable **null / state unstable** tại head mới (CI đang chạy — cả 2 lần đọc); live body vẫn R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề kết thúc "+ R263", updated_at 2026-11-26T19:06:46Z (đổi do push R271 cập nhật head, body không đổi). Issue #116: **34 comment**, updated_at 2026-11-13T19:24:49Z, mới nhất ACK `6862732081`, **không chỉ đạo mới kể từ Gói 39 (`6815238814`)**.
- Body v2: **94.334 ký tự** (net +76 so với R270), headroom **10.666** so với 105.000; head line 1.228 ký tự (không đổi — lần thứ năm liên tiếp); R178 gọn 472 → 214 (gọn đơn thứ mười một); đoạn R270 đúng 270 ký tự (theo checker).
- Commit nội dung `16dfcfe` (~04:06 JST): 3 file, 1399 insertions, 11 deletions; scope audit block (`2482e3b..16dfcfe`) **3 path / 0 violation**; cumulative tại `16dfcfe` = 3206 path / 1 violation — artifact `.gitattributes` ở merge-base đã biết.
- Payload R271 chuẩn bị sau push (dựng từ body v2 + đoạn Head làm tươi theo head sau push): body 94.227 ký tự, sha `73925dd5` (xem mục Payload), **GIỮ LẠI** — ngoài giờ làm việc (lượt chạy bắt đầu ~03:40 JST), KHÔNG trình; chưa đăng — cần thẻ duyệt của chủ dự án. Lưu ý: mergeable_state trong payload là **unstable** (CI đang chạy lúc đọc post-push) — luồng chính làm tươi Head lúc trình nếu CI đã xong (bài học 39).

## Đọc live

- Lượt này, đọc trước push (connector): live body R263 (94.825 ký tự, sha `07316552`, byte-exact với file JSON R263 trên đĩa, 0 U+FFFD — một lần đọc sạch, không cần đọc lại); mergeable_state clean tại `2482e3b` (mergeable null — GitHub chưa tính lại cờ, state clean là giá trị vận hành); tiêu đề kết thúc "+ R263"; updated_at 2026-11-26T18:01:35Z. Issue read (call-read-tool, method get, ~03:42 JST): 34 comment, updated_at 2026-11-13T19:24:49Z — không chỉ đạo mới. Không thử call-tool get_comments lượt này (count + updated_at không đổi so với lần get_comments đã xác minh ở R265).
- Sau push (~04:06 JST + ~04:07 JST, connector, 2 lần đọc): API — head `16dfcfe`, 732/3206, mergeable null, mergeable_state **unstable** (CI đang chạy), live body R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề 765 ký tự kết thúc "+ R263", updated_at 2026-11-26T19:06:46Z; issue #116 không đọc lại sau push (ghi rõ trong head line của payload).
- Suy ra từ git tại `16dfcfe`: rev-list `cf17178..16dfcfe` = 732; diff `--name-only` = 3206 file; `--shortstat` = 378733 insertions, 0 deletions — khớp đọc API; merge-tree `16dfcfe` vs `f3db6b3` exit 0, tree `f1fa98d7…`; tại `2482e3b`: 731/3205/+377345 (khớp dòng cumulative của index R271).
- PR read base.sha `f3832338` là stale cache (ancestor của tip integration `f3db6b3` — merge PR #118 ngày 2026-11-05); ls-remote xác minh tip integration vẫn `f3db6b3`, không đổi; merge-tree chạy với `f3db6b3` như mọi vòng.

## Mốc giờ

- Fetch lượt này chạy đúng giờ hẹn: lần fetch đầu ~03:40 JST (lượt chạy bắt đầu 03:40:16 JST; `.git/FETCH_HEAD` mtime 03:40:51 JST); các số đếm git (731/3205/+377345) đo ~03:41 JST.
- Đọc PR chạy ~03:42 JST (file `pr119_read_r271.json` mtime 03:42:10 JST); đọc issue chạy ~03:42 JST (file `issue116_read_r271.json` mtime 03:42:10 JST).
- Transform/edit chạy 03:52 JST (mtime file: transform 03:52:26, edit 03:52:28, body/index 03:52:28). Shift checker lần đầu fail pair 11 (lessons-list old sai R269 thay vì R268 — xem Bài học (64a)), viết lại + chạy sạch 62/62 cặp (mtime shift 04:04:05, checker 04:05:26); fill 04:05 (validation JSON 04:05:43); commit nội dung 04:06:20 JST; push xong ~04:06 JST. Đọc post-push 04:06:59 + 04:07 JST; payload ~04:08 JST.

## R271 đóng khoảng trống

- Delivery index: tiêu đề head → `2482e3b`; dòng milestone → 731/3205/377345; delta `3ae052f..2482e3b`: 2 path, 674 insertions, 0 deletions; một dòng được thêm — R270 (`3ae052f`/`2482e3b`), ghi payload R270 (94.151 ký tự, sha `b2be30be`, CHƯA ĐĂNG — bị R271 supersede) + đính chính lesson (39) của checker R270 + row-convention (dòng R269 = 3203) + sửa dòng Ghi chú + sửa câu "lượt cập nhật này" (chính R270); không có ACK riêng cho R270. Index bao quát mọi khối tới `2482e3b`; 2 commit của R271 gộp vào ở R272.
- Body v2: head line đồng bộ tới `2482e3b` · 731 · 3205 (additions 377345, Gói 39 ID 6815238814, tree `84239f10…`, mergeable_state clean tại `2482e3b` theo đọc lượt này), cộng đoạn R270 và ghi chú R271. Gọn: đoạn R178 (472 → 214) — gọn ĐƠN thứ mười một. Body 94.334 ký tự — net +76 so với R270 (−258 R178 + 271 đoạn mới + 28 trail + 30 tiêu đề + 5 Ghi-chú list "/R270" + 0 Ghi-chú range "R3–R177"→"R3–R178" + 0 head line — các thành phần theo projection của chuỗi edit; tổng net +76 đo trực tiếp từ đĩa: 94.258 → 94.334).
- Checker `check_pr119_restructure_r271_v1.py`: PASS **152/152** ngay lần đầu (`--out` ghi validation JSON của vòng này; trường "checkpoint" trong JSON mang nhãn vòng trước "PR119 BODY RESTRUCTURE R270" — quy ước đặt tên mang sang của chuỗi shift, không phải lỗi số liệu; checks 152/152, failures []). 152 = 151 + đúng 1 check row-convention mới (tuple R269), khớp bài học vòng R264 mục 6 ("mỗi vòng chỉ thêm đúng 1 check row-convention").
- Fill SHA-hits: `fill_sha_hits_r271.py` đã chạy thành công — đoạn SHA-hits 112 dòng / 90 entry đã điền đầy vào checker. Entry set: 88 entry của R270 + 2 entry mới `2482e3b` (cover) + `3ae052f` (nội dung R270) lên đầu (90 entry — KHÔNG trừ `daf9540`). Extra-token khớp hoàn toàn với R270 (43 token, cùng số lần xuất hiện). daf9540 giữ 13 lần ngoài đoạn (lesson 40).

## Kiểm chứng sau commit nội dung

- Commit nội dung `16dfcfe11ccd1057fab0459617ea3e487255ffca` (~04:06 JST): 3 file (body v2, delivery index, checker.py), 1399 insertions, 11 deletions; scope audit block (`2482e3b..16dfcfe`): **3 path / 0 violation**; cumulative tại `16dfcfe`: 3206 path / 1 violation — artifact `.gitattributes` đã biết.
- Đếm tại `16dfcfe`: **732 commit / 3206 file / +378733** — khớp đọc API post-push. Dòng R270 trong index ghi cumulative 3206 — đã xác minh sau commit (diff tại `16dfcfe` = 3206, gồm 3205 tại `2482e3b` + 1 checker mới).
- Merge-tree tại `16dfcfe` vs `f3db6b3`: exit 0, tree `f1fa98d7…`.
- Push: `2482e3b..16dfcfe` lên `muse/media-production-20261104` (deploy key, không force-push); ls-remote xác minh remote head = `16dfcfe11ccd1057fab0459617ea3e487255ffca`.
- Working tree sau commit nội dung: sạch (chỉ còn báo cáo + validation JSON của vòng này, commit ở commit báo cáo).
- Không có execution-risk flag lượt này; không có hành động nào của vòng bị chặn.
- Cảnh báo SyntaxWarning `invalid escape sequence '\`'` khi chạy checker: ĐÃ CÓ từ checker R265 — không phải khuyết điểm vòng này, không ảnh hưởng PASS.
- Shift checker chạy sạch 62/62 cặp sau 1 sửa (pair 11 lessons-list old sai — bắt bởi assertion trước khi ghi checker); transform edit chạy sạch ngay lần đầu sau 1 sửa (assertion bắt chuỗi lesson (39) nháp nhắc lại sha nội dung R269 đã nghỉ hưu — xem Bài học (64)); fill chạy sạch ngay lần đầu (112 dòng / 90 entry; chạy lại idempotent — cùng kết quả).

## Payload R271

- Dựng bởi vòng này sau push (script `r271_payload.py` trong goal hidden_files) từ body v2 của vòng + đoạn Head làm tươi DUY NHẤT sang head sau push: head `16dfcfe` · 732 · 3206, additions 378733, mergeable **null / unstable** tại `16dfcfe` (đọc API tươi post-push ~04:06 + ~04:07 JST — CI đang chạy trên head mới; luồng chính làm tươi Head lúc trình nếu CI đã xong), live body R263 (94.825 ký tự, sha `07316552`, updated_at 2026-11-26T19:06:46Z), merge-tree tree `f1fa98d7…`, issue #116 34 comment (đọc trước push lượt này ~03:42 JST, không đọc lại sau push — ghi rõ trong head line).
- Body **94.227 ký tự, sha `73925dd5`**; JSON 105.214 byte < trần 131.072 (còn 25.858 byte); tiêu đề 765 ký tự kết thúc "+ R271" (hậu tố THAY, không nối — bài học R120); envelope đủ (owner `khanhcoder97`, repo `ngumach-huyenan`, pullNumber 119); file `~/workspace/godot-prototype/pr_comments/pr119_update_body_v2_r271.json` + `.bak` byte-identical (sha256 `ebe83ebd`) + bản sao byte-identical trong `.bak-prepost-20261124/` và `.bak-prepost-20261126/`.
- **CHƯA ĐĂNG** — cần thẻ duyệt của chủ dự án; **GIỮ LẠI** (ngoài giờ làm việc — lượt chạy bắt đầu ~03:40 JST), luồng chính trình widget trong giờ làm việc. Lưu ý: thẻ duyệt hết hạn sau ~30 phút chờ (đã 10 lần) — nên bấm khi còn ngồi máy. Lưu ý thêm: payload R270 nay ĐÃ LỖI THỜI (head đã sang `16dfcfe`) — KHÔNG bấm widget R270.

## Cảnh báo headroom

Body v2 hiện 94.334 ký tự, headroom 10.666. Gọn ĐƠN tiếp theo là R179 ở vòng R272. Đoạn đầy đủ còn lại R179..R270 = 92 đoạn; khối gọn R2–R178 = 177 dòng. Ước tính net mỗi vòng gọn đơn ≈ −100..−250 — nhưng vòng này net +76 vì đoạn R178 ngắn (472 ký tự thay vì ~690); headroom vẫn an toàn dài hạn.

## Bài học

Lessons carried: toàn bộ danh sách bài học (1)–(63) trong báo cáo R262 + R263 + R264 + R265 + R266 + R267 + R268 + R269 + R270 cùng thư mục giữ nguyên hiệu lực. Mới vòng này:

(64) NEW THIS ROUND (R271) — ba điều: (a) SHIFT-SCRIPT OLD-STRING SLIP: bản nháp đầu của shift_checker_r271.py chép nhầm chuỗi MỚI (R271) vào phía CŨ của 14 cặp docstring + cặp lessons-list ghi sai vòng (R269 thay vì R268) — assertion của script bắt ngay ở pair 11 trước khi ghi checker; đã viết lại file từ đầu với old = chuỗi thật trong checker R270 (tức chuỗi NEW của shift R270), sau đó 62/62 cặp chạy sạch ngay lần đầu. Quy tắc: old-string luôn lấy từ text thật của source checker, không gõ lại từ trí nhớ vòng đích. (b) TRANSFORM ASSERTION BẮT LỖI THẬT: chuỗi lesson (39) nháp trong transform_edit_r271.py nhắc lại sha nội dung R269 đã nghỉ hưu `75e1d55` (ghi chú entry SHA-hits) — assertion "`75e1d55` not in row" bắt trước khi ghi; đã diễn đạt lại chỉ nhắc cover sha. Cùng họ lỗi với (a): prose mới không được đưa lại sha đã nghỉ hưu. (c) HEAD LINE KHÔNG ĐỔI LẦN THỨ NĂM: 1.228 ký tự, delta 0; net +76 lần thứ ba liên tiếp (R178 cũng chỉ 472 ký tự); payload head ngắn hơn 107 ký tự như R270 (1.121).
