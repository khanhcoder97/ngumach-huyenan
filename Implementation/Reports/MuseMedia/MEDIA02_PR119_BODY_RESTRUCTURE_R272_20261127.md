# MEDIA-02 — PR #119 Body Restructure R272 (2026-11-27)

## Tóm tắt

- Khối: body restructure R272 — gọn ĐƠN R179 (gọn đơn thứ MƯỜI HAI; gọn đơn bắt đầu ở R168); index + body v2 + checker đồng bộ tới head `ce57ceb` (733 commit / 3208 file / +379411 từ merge-base `cf17178`); merge-tree tại `ce57ceb` vs integration `f3db6b3` exit 0, tree `c24e0cf2…`.
- SỰ KIỆN ĐĂNG GIỮA HAI VÒNG: không có — payload R271 CHƯA ĐĂNG, live body vẫn R263 (94.825 ký tự, sha `07316552`); payload R271 sẵn sàng trình từ vòng trước, bị R272 supersede trước khi đăng.
- Vòng này chạy MỘT PHA (~04:40–04:55 JST): fetch ~04:40 JST, đọc live, áp edit index + body v2, dựng chuỗi checker tới `check_pr119_restructure_r272_v1.py` + fill SHA-hits, checker chạy sạch **PASS 153/153** ngay lần đầu, scope audit block **3 path / 0 violation**, commit nội dung `312d680` + push (ls-remote xác minh), đọc live post-push (2 lần), viết báo cáo này + payload R272.
- Đọc live post-push (~04:52 + ~04:53 JST, connector, 2 lần): PR head `312d680`, 734 commit / 3209 file / +380804 — khớp đếm git tại commit nội dung; mergeable **null / state unstable** tại head mới (CI đang chạy — cả 2 lần đọc); live body vẫn R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề kết thúc "+ R263", updated_at 2026-11-26T19:52:35Z (đổi do push R272 cập nhật head, body không đổi). Issue #116: **34 comment**, updated_at 2026-11-13T19:24:49Z, mới nhất ACK `6862732081`, **không chỉ đạo mới kể từ Gói 39 (`6815238814`)**.
- Body v2: **94.410 ký tự** (net +76 so với R271), headroom **10.590** so với 105.000; head line 1.228 ký tự (không đổi — lần thứ sáu liên tiếp); R179 gọn 472 → 214 (gọn đơn thứ mười hai); đoạn R271 đúng 270 ký tự (theo checker).
- Commit nội dung `312d680` (~04:52 JST): 3 file, 1404 insertions, 11 deletions; scope audit block (`ce57ceb..312d680`) **3 path / 0 violation**; cumulative tại `312d680` = 3209 path / 1 violation — artifact `.gitattributes` ở merge-base đã biết.
- Payload R272 chuẩn bị sau push (dựng từ body v2 + đoạn Head làm tươi theo head sau push): body 94.303 ký tự, sha `b6ac34b3` (xem mục Payload), **GIỮ LẠI** — ngoài giờ làm việc (lượt chạy bắt đầu ~04:40 JST), KHÔNG trình; chưa đăng — cần thẻ duyệt của chủ dự án. Lưu ý: mergeable_state trong payload là **unstable** (CI đang chạy lúc đọc post-push) — luồng chính làm tươi Head lúc trình nếu CI đã xong (bài học 39).

## Đọc live

- Lượt này, đọc trước push (connector): live body R263 (94.825 ký tự, sha `07316552`, byte-exact với file JSON R263 trên đĩa, 0 U+FFFD — một lần đọc sạch, không cần đọc lại); mergeable_state clean tại `ce57ceb` (mergeable null — GitHub chưa tính lại cờ, state clean là giá trị vận hành); tiêu đề kết thúc "+ R263"; updated_at 2026-11-26T19:10:56Z. Issue read (call-read-tool, method get, ~04:41 JST): 34 comment, updated_at 2026-11-13T19:24:49Z — không chỉ đạo mới. Không thử call-tool get_comments lượt này (count + updated_at không đổi so với lần get_comments đã xác minh ở R265).
- Sau push (~04:52 JST + ~04:53 JST, connector, 2 lần đọc): API — head `312d680`, 734/3209, mergeable null, mergeable_state **unstable** (CI đang chạy), live body R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề 765 ký tự kết thúc "+ R263", updated_at 2026-11-26T19:52:35Z; issue #116 không đọc lại sau push (ghi rõ trong head line của payload).
- Suy ra từ git tại `312d680`: rev-list `cf17178..312d680` = 734; diff `--name-only` = 3209 file; `--shortstat` = 380804 insertions, 0 deletions — khớp đọc API; merge-tree `312d680` vs `f3db6b3` exit 0, tree `cad4cc88…`; tại `ce57ceb`: 733/3208/+379411 (khớp dòng cumulative của index R272).
- PR read base.sha `f3832338` là stale cache (ancestor của tip integration `f3db6b3` — merge PR #118 ngày 2026-11-05); ls-remote xác minh tip integration vẫn `f3db6b3`, không đổi; merge-tree chạy với `f3db6b3` như mọi vòng.

## Mốc giờ

- Fetch lượt này chạy đúng giờ hẹn: lần fetch đầu ~04:40 JST (lượt chạy bắt đầu 04:40:16 JST; `.git/FETCH_HEAD` mtime 04:40:37 JST); các số đếm git (733/3208/+379411) đo ~04:41 JST.
- Đọc PR chạy ~04:41 JST (file `pr119_read_r272.json` mtime 04:41:17 JST); đọc issue chạy ~04:41 JST (file `issue116_read_r272.json` mtime 04:41:27 JST; `issue116_get_r272.json` mtime 04:41:35 JST).
- Transform/edit chạy 04:47 JST (mtime file: transform 04:47:37, edit 04:47:40, body/index 04:47:40). Shift checker chạy sạch 62/62 cặp ngay lần đầu (mtime shift 04:50:21, checker 04:51:56); fill 04:51 (validation JSON 04:51:56); commit nội dung 04:52:21 JST; push xong ~04:52 JST. Đọc post-push 04:52:45 + 04:53:38 JST; payload ~04:54 JST.

## R272 đóng khoảng trống

- Delivery index: tiêu đề head → `ce57ceb`; dòng milestone → 733/3208/379411; delta `16dfcfe..ce57ceb`: 2 path, 678 insertions, 0 deletions; một dòng được thêm — R271 (`16dfcfe`/`ce57ceb`), ghi payload R271 (94.227 ký tự, sha `73925dd5`, CHƯA ĐĂNG — bị R272 supersede) + đính chính lesson (40) của checker R271 + row-convention (dòng R270 = 3206) + sửa dòng Ghi chú + sửa câu "lượt cập nhật này" (chính R271); không có ACK riêng cho R271. Index bao quát mọi khối tới `ce57ceb`; 2 commit của R272 gộp vào ở R273.
- Body v2: head line đồng bộ tới `ce57ceb` · 733 · 3208 (additions 379411, Gói 39 ID 6815238814, tree `c24e0cf2…`, mergeable_state clean tại `ce57ceb` theo đọc lượt này), cộng đoạn R271 và ghi chú R272. Gọn: đoạn R179 (472 → 214) — gọn ĐƠN thứ mười hai. Body 94.410 ký tự — net +76 so với R271 (−258 R179 + 271 đoạn mới + 28 trail + 30 tiêu đề + 5 Ghi-chú list "/R271" + 0 Ghi-chú range "R3–R178"→"R3–R179" + 0 head line — các thành phần theo projection của chuỗi edit; tổng net +76 đo trực tiếp từ đĩa: 94.334 → 94.410).
- Checker `check_pr119_restructure_r272_v1.py`: PASS **153/153** ngay lần đầu (`--out` ghi validation JSON của vòng này; trường "checkpoint" trong JSON mang nhãn vòng trước "PR119 BODY RESTRUCTURE R271" — quy ước đặt tên mang sang của chuỗi shift, không phải lỗi số liệu; checks 153/153, failures []). 153 = 152 + đúng 1 check row-convention mới (tuple R270), khớp bài học vòng R264 mục 6 ("mỗi vòng chỉ thêm đúng 1 check row-convention").
- Fill SHA-hits: `fill_sha_hits_r272.py` đã chạy thành công — đoạn SHA-hits 115 dòng / 92 entry đã điền đầy vào checker. Entry set: 90 entry của R271 + 2 entry mới `ce57ceb` (cover) + `16dfcfe` (nội dung R271) lên đầu (92 entry — KHÔNG trừ `daf9540`). Extra-token khớp hoàn toàn với R271 (43 token, cùng số lần xuất hiện). daf9540 giữ 15 lần ngoài đoạn (lesson 41 — tăng 2 do lesson (41) nhắc sha hai lần).

## Kiểm chứng sau commit nội dung

- Commit nội dung `312d6800a4b56052be180cc6c0422e3ef5f45924` (~04:52 JST): 3 file (body v2, delivery index, checker.py), 1404 insertions, 11 deletions; scope audit block (`ce57ceb..312d680`): **3 path / 0 violation**; cumulative tại `312d680`: 3209 path / 1 violation — artifact `.gitattributes` đã biết (byte-identical với integration `f3db6b3`, sha256 `23352e4c…`; khác merge-base `cf17178` sha256 `54ee7996…` — đúng bản chất artifact merge-base, không phải lệch thật).
- Đếm tại `312d680`: **734 commit / 3209 file / +380804** — khớp đọc API post-push. Dòng R271 trong index ghi cumulative 3209 — đã xác minh sau commit (diff tại `312d680` = 3209, gồm 3208 tại `ce57ceb` + 1 checker mới).
- Merge-tree tại `312d680` vs `f3db6b3`: exit 0, tree `cad4cc88…`.
- Push: `ce57ceb..312d680` lên `muse/media-production-20261104` (deploy key, không force-push); ls-remote xác minh remote head = `312d6800a4b56052be180cc6c0422e3ef5f45924`.
- Working tree sau commit nội dung: sạch (chỉ còn báo cáo + validation JSON của vòng này, commit ở commit báo cáo).
- Không có execution-risk flag lượt này; không có hành động nào của vòng bị chặn.
- Cảnh báo SyntaxWarning `invalid escape sequence '\`'` khi chạy checker: ĐÃ CÓ từ checker R265 — không phải khuyết điểm vòng này, không ảnh hưởng PASS.
- Transform edit: assertion bắt 1 lỗi chép cặp apply_edits trước khi ghi (xem Bài học (65)) — đã sửa, chạy lại sạch; shift checker chạy sạch 62/62 cặp ngay lần đầu; fill chạy sạch ngay lần đầu (115 dòng / 92 entry; extra-token 43 khớp R271).

## Payload R272

- Dựng bởi vòng này sau push (script `r272_payload.py` trong goal hidden_files) từ body v2 của vòng + đoạn Head làm tươi DUY NHẤT sang head sau push: head `312d680` · 734 · 3209, additions 380804, mergeable **null / unstable** tại `312d680` (đọc API tươi post-push ~04:52 + ~04:53 JST — CI đang chạy trên head mới; luồng chính làm tươi Head lúc trình nếu CI đã xong), live body R263 (94.825 ký tự, sha `07316552`, updated_at 2026-11-26T19:52:35Z), merge-tree tree `cad4cc88…`, issue #116 34 comment (đọc trước push lượt này ~04:41 JST, không đọc lại sau push — ghi rõ trong head line).
- Body **94.303 ký tự, sha `b6ac34b3`**; JSON 105.294 byte < trần 131.072 (còn 25.778 byte); tiêu đề 765 ký tự kết thúc "+ R272" (hậu tố THAY, không nối — bài học R120); envelope đủ (owner `khanhcoder97`, repo `ngumach-huyenan`, pullNumber 119); file `~/workspace/godot-prototype/pr_comments/pr119_update_body_v2_r272.json` + `.bak` byte-identical (sha256 `f6fc2589`) + bản sao byte-identical trong `.bak-prepost-20261124/` và `.bak-prepost-20261126/`.
- **CHƯA ĐĂNG** — cần thẻ duyệt của chủ dự án; **GIỮ LẠI** (ngoài giờ làm việc — lượt chạy bắt đầu ~04:40 JST), luồng chính trình widget trong giờ làm việc. Lưu ý: thẻ duyệt hết hạn sau ~30 phút chờ (đã 10 lần) — nên bấm khi còn ngồi máy. Lưu ý thêm: payload R271 nay ĐÃ LỖI THỜI (head đã sang `312d680`) — KHÔNG bấm widget R271.

## Cảnh báo headroom

Body v2 hiện 94.410 ký tự, headroom 10.590. Gọn ĐƠN tiếp theo là R180 ở vòng R273. Đoạn đầy đủ còn lại R180..R271 = 92 đoạn; khối gọn R2–R179 = 178 dòng. Ước tính net mỗi vòng gọn đơn ≈ −100..−250 — nhưng vòng này net +76 vì đoạn R179 ngắn (472 ký tự thay vì ~690); headroom vẫn an toàn dài hạn.

## Bài học

Lessons carried: toàn bộ danh sách bài học (1)–(64) trong báo cáo R262 + R263 + R264 + R265 + R266 + R267 + R268 + R269 + R270 + R271 cùng thư mục giữ nguyên hiệu lực. Mới vòng này:

(65) NEW THIS ROUND (R272) — ba điều: (a) TRANSFORM ANCHOR/IDENTIFIER OFF-BY-ONE: bản nháp đầu của transform_edit_r272.py chép sai cặp apply_edits theo hai chiều — cặp find/Ghi-chú/trail/range/list lấy nhầm giá trị ĐÍCH làm phía CŨ, cặp ROW/NOTE/PARA/COMPACT lấy nhầm giá trị NGUỒN CŨ làm phía CŨ — assertion "pair not unique (0)" bắt ngay ở cặp `if il[i + 1] != R269_ROW:` trước khi ghi file nào; đã sửa hai lượt rồi chạy lại sạch (dry-run 94.410 = apply 94.410, idempotency 0). Quy tắc: anchor (find/sub_once) lấy từ lệnh của script NGUỒN, identifier (ROW/NOTE/PARA/COMPACT) lấy từ block MỚI của script nguồn — không bao giờ dịch cả hai từ cùng một gốc. Cùng họ lỗi với bài học (64a). (b) DAF9540 TĂNG 2: lesson (41) nhắc sha hai lần ("still does NOT retire" + history 'Head e373cb5 -> daf9540') nên số lần ngoài đoạn lên 15 (từ 13 ở R271) — fill đo đúng 15, khớp lesson; khi viết lesson mới phải đếm lại, không mang số vòng trước. (c) SHIFT + FILL SẠCH NGAY LẦN ĐẦU: shift checker 62/62 cặp, fill 115 dòng / 92 entry, extra-token 43 khớp hoàn toàn R271 — chuỗi ba tầng (transform → shift → fill) vẫn là lưới bắt lỗi hiệu quả khi mỗi tầng assert độc lập.
