# MEDIA-02 — PR #119 Body Restructure R289 (2026-11-28)

## Tóm tắt

- Vòng R289: gọn ĐƠN R196 (gọn đơn thứ HAI MƯƠI CHÍN); index + body v2 + checker đồng bộ tới head `6b035ad` (767 commit / 3259 file / +415797 từ merge-base `cf17178`); merge-tree tại `6b035ad` vs integration `f3db6b3` exit 0, tree `3f098c81…`.
- Vòng này là lượt định kỳ 05:40 JST 2026-11-28: fetch thành công lần đầu; đọc live FRESH (HTTP 200 cả hai, public API); transform 1 sửa (history-reference assert — bài học 84a) rồi chạy sạch; gen_pairs chạy sạch lần đầu; build_fill 1 sửa (comparison vars — bài học 84c); build_checker 1 sửa (note-date pair — bài học 84b); fill bắt 2 lỗi (literal SHA trong lesson — bài học 84d; 8cb82a1 mất anchor — bài học 84f) rồi chạy sạch (153 dòng / 123 entry); checker FAIL 169/170 một lần (row-convention tuple sha — bài học 84e) rồi PASS 170/170 sau khi sửa builder; content commit `e3b1a28`. Không có sự kiện đăng bài giữa các vòng: payload R288 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R288 bị R289 thay thế.
- CẢNH BÁO STALE (hai phiên bản payload R288): bản chính (main) payload R288 đã làm tươi sau push báo cáo (Head `6b035ad`, 96.231 ký tự, sha `2f676955`, JSON 107.469 byte, sha256 `2308f938`, head line 1374, mergeable true/clean) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (96.181 ký tự, sha `cadb5281`, JSON 107.413 byte, sha256 `4abc5d85`, head line 1324, Head `5fdc769`); cả hai phiên bản đã xác minh lại từ đĩa lượt 05:40; main != .bak. Title 765 ký tự kết "+ R288".
- Content commit `e3b1a28` (~06:11 JST): 3 file, 1451 insertions, 11 deletions; scope audit cumulative 3260 path / 1 violation — artifact `.gitattributes` đã biết (block 3 path / 0 violation mới).
- Số đếm tại `e3b1a28`: 768 commit / 3260 file / +417237 — số đếm git, KHỚP ĐÚNG số API sau push (xem dưới). Additions: 415797 + (1451 − 11) = 417237.
- Merge-tree tại `e3b1a28` vs `f3db6b3`: exit 0, tree `6856fb7e…`.
- Push: `6b035ad..e3b1a28`; ls-remote xác nhận remote head `e3b1a28` VÀ integration `f3db6b3` (~06:13 JST).
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (public API qua curl, bản đọc lượt này ~05:40 JST, HTTP 200): head `6b035ad`, API 767 commit / 3259 file / +415797 / 0 — KHỚP ĐÚNG số git; mergeable true/clean (CI đã xong trên head mới); tiêu đề kết thúc "+ R263"; live body R263 băm lại byte-exact (94.825 ký tự, sha `07316552`, 0 U+FFFD); updated_at 2026-11-27T19:12:57Z.
- Issue #116 (public API qua curl, bản đọc ~05:40 JST, HTTP 200): đúng 34 comment, mới nhất ACK `6862732081` (2026-11-13); không chỉ đạo mới kể từ Gói 39.
- PR read xác minh lại lượt này `base.sha f3832338` LÀ ancestor của integration `f3db6b3` (20 commit sau — merge PR #118 ngày 2026-11-05); merge-tree vẫn chạy trên `f3db6b3` live như mọi vòng.
- Đọc sau push nội dung (public API qua curl, ~06:13 JST, HTTP 200 cả hai, file `hidden_files/pr119_read_r289_after_content.json` + `issue116_read_r289_after_content.json`): PR head `e3b1a28`, API 768/3260/+417237/0 — KHỚP ĐÚNG số git tại content commit; mergeable true/unstable (CI đang chạy trên head mới); live body vẫn R263 (94.825 ký tự, sha `07316552` — push không đổi body). Issue #116 đọc lại sau push: vẫn 34 comment, mới nhất 6862732081.

## Mốc giờ

- ~05:40 JST 2026-11-28: lượt định kỳ bắt đầu R289 — fetch thành công lần đầu; đọc live (PR + issue HTTP 200).
- ~05:47–06:10 JST: transform (1 sửa history-reference assert) + edit (changed 18, idempotent 0) + gen_pairs (62 cặp, chạy sạch lần đầu) + build_fill (1 sửa comparison vars) + build_checker (1 sửa note-date pair) + fill (2 lỗi: literal SHA lesson + 8cb82a1 mất anchor, rồi chạy sạch 153 dòng / 123 entry) + checker FAIL 169/170 (row-convention tuple sha) rồi PASS 170/170 sau khi sửa builder.
- ~06:11 JST: scope audit + merge-tree; content commit `e3b1a28`; push ~06:12 JST; đọc sau push; báo cáo này ~06:14 JST.

## R289 đóng khoảng trống

- Body v2: 96.509 ký tự (net −64 so với R288: +271 đoạn R288 mới −182 gọn R196 + 28 trail + 30 tiêu đề + 5 Ghi-chú "/R288" + 0 range R3–R195→R3–R196 − 216 head line), headroom 8.491 so với 105.000; head line 1.500 ký tự (−216 — đo từ đĩa, giảm do bỏ verbiage rate-limit); R196 gọn 396 → 214 (gọn đơn thứ hai mươi chín); đoạn R288 đúng 270 ký tự (theo checker).
- Checker `check_pr119_restructure_r289_v1.py`: PASS 170/170 (169 + 1 check row-convention mới cho tuple R287 `("R287", "5fdc769", 3257)`); validation JSON status PASS, failures [].
- ĐÍNH CHÍNH từ lượt chạy payload R288 (bài học 84): (a) head line soạn sẵn 1.449 ký tự / NET −115 / body 96.458 chỉ là BẢN NHÁP — head line thực tế 1.500 ký tự, NET −64, body 96.509; mọi số liệu vòng này đo từ chuỗi thật, không mang từ bản nháp; (b) SHA `218f0fa`/`eb54d4d` ghi trong memory cho R289 là SHA LỊCH SỬ của R196 (dòng index R196), KHÔNG phải SHA của R289 — R289 chưa có SHA nội dung/báo cáo cho tới khi commit; không viết hai SHA đó vào dòng R289.
- Build fill + fill: lần đầu báo extra-token set đổi (`218f0fa` + `eb54d4d` — bài học 84d: lesson (59) nháp trích literal SHA lịch sử) → bỏ literal SHA khỏi lesson → fill chạy lại báo `8cb82a1` 0 lần ngoài đoạn (bài học 84f — lesson (54) R289 trích source cover mới `07e13a0`, làm mất anchor duy nhất của `8cb82a1`) → thêm anchor giữ `8cb82a1` vào lesson (54) → fill chạy lại sạch (153 dòng / 123 entry — 121 sha của R288 + `6b035ad` cover + `5fdc769` content R288, KHÔNG retire sha nào; extra-token khớp R288, 43 = 43; chạy lại idempotent); `daf9540` vẫn 15 lần ngoài đoạn; `8cb82a1` giữ 1 lần (anchor lesson (54)); không sha nào retire vòng này. Số dòng đoạn SHA-hits là 153, không phải 152 như lesson nháp dự đoán (150 + 2 entry) — số dòng do fill đo, không suy từ số entry (bài học 84d).
- Số đếm API sau push khớp đúng số git (768/3260/+417237/0 tại `e3b1a28` cả hai nguồn).

## Kiểm chứng sau commit nội dung

- Content commit `e3b1a28` đã push: `6b035ad..e3b1a28`, ls-remote xác nhận remote head `e3b1a28`, integration `f3db6b3`.
- Đọc API sau push (~06:13 JST, HTTP 200): PR head `e3b1a28`; số API 768/3260/+417237/0 khớp đúng số git tại `e3b1a28`; mergeable true/unstable (CI đang chạy); live body vẫn R263. Issue #116 đọc lại sau push: vẫn 34 comment, ACK `6862732081`.
- Scope audit cumulative tại head: 3260 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`, sha256 `23352e4c…`; khác merge-base `cf17178` sha256 `54ee7996…`); block R289: 3 path / 0 violation mới.

## Payload R289

- Dựng sau push báo cáo bằng `make_r289_payload.py` (adapt từ `make_r288_payload.py`) từ body v2 + Head làm tươi tới head báo cáo (đọc API mới sau push báo cáo); .bak + 2 bản sao prepost giữ nguyên bản chuẩn bị; số đo v2 ghi trong nhật ký `~/memory/2026-11-28.md` + tin cuối lượt chạy, và hàng R289 trong index (vòng sau) ghi cả hai phiên bản.
- Payload SẴN SÀNG TRÌNH BÀY (đã qua 01:30 JST — luồng chính trình vào sáng mai theo lệnh); CHƯA ĐĂNG — cần thẻ duyệt của chủ dự án. Thẻ sống ~30 phút — bấm khi còn ngồi máy.
- Widget R288 giờ stale, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 96.509 ký tự, headroom 8.491 so với 105.000. Gọn đơn tiếp theo R197 ở R290. Đoạn đầy còn lại R197..R288 = 92 đoạn; khối gọn R2–R196 = 195 dòng.
- Net vòng này −64 khi head line giảm 216; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(83) xem báo cáo các vòng trước. Bài học (84) + (84a)–(84f) MỚI VÒNG NÀY (R289):

(a) TRANSFORM R289 MANG MỘT LỖI, BỊ ASSERTION BẮT TRƯỚC KHI GHI (lesson 84a): assert cuối transform ghi `"75eedfc" in text` (history reference) — nhưng edit script R289 trích source cover mới `07e13a0`, không còn `75eedfc` nào; sửa assert thành `"07e13a0" in text`, chạy lại sạch. Quy tắc: assert history-reference phải nêu tên source cover MỚI của vòng này, không phải PREV7 cũ.
(b) GEN_PAIRS MANG NGÀY CŨ VÀO NOTE-DATE PAIR (lesson 84b, cùng lớp với lesson 82a): gen_pairs chạy lại transform_pair của R288 (không có sửa ngày) nên cặp note-date mang ngày 2026-11-27 của note R286 sang guard note R287, trong khi checker R288 (sau sửa skeleton của chính nó) guard note R287 ngày 2026-11-28 — pairs loop FAIL ở `o2 in skeleton`; sửa bằng special case trong transform_pair của build_checker (chuẩn hoá ngày cũ → 2026-11-28 cho cả old/new side), chạy lại sạch. Quy tắc: ngày trong guard note KHÔNG nằm trong shift map — mỗi vòng kiểm tra ngày note mới từ index trước khi build checker; và sửa ngày phải ở transform_pair (nơi pairs sinh ra), không chỉ ở skeleton rep sau vòng lặp.
(c) FILL COMPARISON VARS MANG TÊN VÒNG SAI (lesson 84c): build_fill_r289.py đổi `r287_*` → `r289_*`, nhưng các biến so sánh mang tên CHECKER ĐƯỢC SO SÁNH (vòng trước, R288), không phải vòng này — fill lỗi `NameError: r289_lines` (định nghĩa là `r288_lines` từ PAIRS); sửa bulk rename thành `r287_*` → `r288_*` (cả base set `r288_entry`, nhãn extra `R288 extra:`, `only-R288=`), chạy lại sạch. Quy tắc: build_fill đổi tên theo checker nguồn (vòng trước), giống build_fill_r288.py đổi `r285_*` → `r287_*`.
(d) LESSON KHÔNG TRÍCH LITERAL SHA LỊCH SỬ + SỐ DÒNG ĐOẠN DO FILL ĐO (lesson 84d): (i) lesson (59) nháp trích literal `218f0fa`/`eb54d4d` (SHA R196) → hai token mới lọt vào extra-token set của checker (43 → 45), fill FAIL ở assert extra == r288_extra; bỏ literal SHA khỏi lesson, fill chạy lại sạch. Quy tắc: lesson chỉ nêu tên vòng/SHA bằng lời, không trích literal SHA không nằm trong entry set. (ii) Lesson nháp ghi đoạn SHA-hits 152 dòng (150 + 2 entry) — fill đo thực tế 153 dòng; sửa lesson thành 153. Quy tắc: số dòng đoạn do fill đo, không suy từ số entry (wrap/label làm lệch).
(e) ROW-CONVENTION TUPLE MANG SHA SAI (lesson 84e): tuple mới ghi `("R287", "07e13a0", 3257)` — 07e13a0 là report head của chính dòng R287; checker FAIL 169/170 vì diff tại 07e13a0 là 3256, không phải 3257. Đúng là `("R287", "5fdc769", 3257)` — SHA là CONTENT commit của vòng TÁC GIẢ (R288), nơi dòng R287 được viết (diff tại 5fdc769 = 3257, đã kiểm bằng git); sửa builder, checker PASS 170/170. Quy tắc: tuple row-convention = (dòng, content-sha của vòng tác giả, cumulative) — kiểm diff bằng git trước khi ghi tuple.
(f) ENTRY MẤT ANCHOR CUỐI PHẢI ĐƯỢC NEO LẠI (lesson 84f): fill assert mọi entry sha xuất hiện ≥1 lần ngoài đoạn; `8cb82a1` (R285 report head) về 0 lần vì lesson (54) R289 trích source cover mới `07e13a0` thay cho `8cb82a1` — anchor duy nhất của nó ở R288 đã mất; thêm câu neo giữ `8cb82a1` vào lesson (54) R289 (nêu rõ nó từng là source cover của fill R287/R288), fill chạy lại sạch. Quy tắc: khi source cover đổi, kiểm tra entry sha cũ còn anchor nào không — nếu không, neo lại trong lesson hoặc retire khỏi entry set một cách có chủ đích, không để fill assert bắt.
