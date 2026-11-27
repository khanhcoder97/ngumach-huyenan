# MEDIA-02 — PR #119 Body Restructure R285 (2026-11-27)

## Tóm tắt

- Vòng R285: gọn ĐƠN R192 (gọn đơn thứ HAI MƯƠI LĂM); index + body v2 + checker đồng bộ tới head `43b2464` (759 commit / 3247 file / +407089 từ merge-base `cf17178`); merge-tree tại `43b2464` vs integration `f3db6b3` exit 0, tree `ad8feab7…`.
- Vòng này chạy HAI phase: lượt 20:40 JST dừng sau fetch vì cờ execution-risk (lần thứ 11 — không lệnh git nào sau đó trong lượt đó); main agent resume ~21:41 JST với fetch mới + đọc live + edit (không cờ ở phase đó); lượt 22:40 JST này tiếp tục checker/commit/push/báo cáo. Không có cờ execution-risk trong lượt 22:40 này.
- Transform trên đĩa đã xác minh (không chạy lại transform — chỉ sửa phần checker bắt lỗi): body v2 96.042 ký tự, net +287; checker PASS 166/166; content commit `1e45131`. Không có sự kiện đăng bài giữa các vòng: payload R284 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R284 bị R285 thay thế.
- CẢNH BÁO STALE (ba phiên bản payload R284): bản chính (main) payload R284 đã làm tươi HAI lần — sau push báo cáo ~20:26 JST (Head `43b2464`, 95.506 ký tự, sha `55fb21bf`, JSON 106.662 byte, sha256 `389021d4`, head line 1257 ký tự, mergeable true/unstable) + ở bước trình ~20:30 JST (Head `43b2464`, 95.479 ký tự, sha `69ee3754`, JSON 106.601 byte, sha256 `641ef547`, head line 1230 ký tự, mergeable true/clean) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (95.517 ký tự, sha `0234140d`, JSON 106.681 byte, sha256 `3d1e6bed`); cả ba phiên bản đã xác minh lại từ đĩa lượt này; hàng R284 trong index ghi cả ba phiên bản. Khuyết điểm: head line bản v3 trùng lặp mệnh đề merge-tree (đã ghi).
- Content commit `1e45131` (~23:13 JST): 3 file, 1439 insertions, 11 deletions; scope audit cumulative 3248 path / 1 violation — artifact `.gitattributes` đã biết (block 3 path / 0 violation mới).
- Số đếm tại `1e45131`: 760 commit / 3248 file / +408517 — số đếm git (đọc API sau push lỗi 403 rate-limit, chưa đối chiếu được với API lượt này). Additions: 407089 + (1439 − 11) = 408517.
- Merge-tree tại `1e45131` vs `f3db6b3`: exit 0, tree `cd712fba…`.
- Push: `43b2464..1e45131`; ls-remote xác nhận remote head `1e45131` VÀ integration `f3db6b3` (~23:16 JST).
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (public API qua curl — lượt này đọc mới 2 lần đều lỗi 403 rate-limit, ~22:46 và ~22:56 JST, file lỗi lưu `hidden_files/pr119_read_r285_2246.json` + `pr119_read_r285_2256.json`, KHÔNG ghi đè bản đọc tốt): dùng lại bản đọc tốt ~22:40 JST (`hidden_files/pr119_read_r285_2240.json`, mtime 13:44 UTC): head `43b2464`, 759/3247/+407089/0, mergeable_state clean (mergeable true — GitHub đã tính lại cờ, CI đã chạy xong), updated_at 2026-11-27T11:26:59Z, live body R263 băm lại byte-exact (94.825 ký tự, sha `07316552`, 0 U+FFFD); head xác minh không đổi qua fetch ~22:45 JST (local head = remote head = `43b2464`, integration `f3db6b3`).
- Issue #116 (public API qua curl, bản đọc tốt ~22:40 JST, `hidden_files/issue116_read_r285_2240.json`; đọc mới ~22:46 JST cũng 403, file lỗi `hidden_files/issue116_read_r285_2246.json`): đúng 34 comment, mới nhất ACK `6862732081` (2026-11-13); không chỉ đạo mới kể từ Gói 39.
- PR read xác minh lại lượt này `base.sha f3832338` LÀ ancestor của integration `f3db6b3` (20 commit sau — merge PR #118 ngày 2026-11-05); merge-tree vẫn chạy trên `f3db6b3` live như mọi vòng.
- Đọc sau push (public API qua curl, ~23:17 JST): PR read LỖI 403 rate-limit (file `hidden_files/pr119_read_r285_after.json`) — KHÔNG có số API sau push; head xác minh qua ls-remote (`1e45131`); số đếm git tại `1e45131` là 760/3248/+408517 (số git, không phải số API); live body chưa đọc lại được lượt này — bản đọc tốt gần nhất (~22:40 JST) vẫn R263, push không đổi body. Issue #116 đọc LẠI sau push (~23:17 JST): vẫn 34 comment, mới nhất 6862732081.
- Hai cách đếm vẫn khác nhau như đã ghi: số liệu API live (759/3247/407089) là số đếm PR-diff; số liệu trong dòng Head của body (759/3247/407089) là số đếm bằng diff từ merge-base `cf17178` — hai số này trùng nhau lượt này vì head line ghi đúng diff từ merge-base; số API live và số Head-line có thể khác nhau ở các vòng khác — không phải lỗi đọc.

## Mốc giờ

- ~20:40 JST: lượt định kỳ dừng sau fetch vì cờ execution-risk lần thứ 11 (không lệnh git sau đó trong lượt đó).
- ~21:41 JST: main agent resume — fetch mới (sạch, không cờ) + đọc live public API + edit index/body v2 (transform chạy sạch lần đầu).
- ~22:40 JST: lượt này bắt đầu — xác minh transform trên đĩa + fetch lại (~22:45 JST, remote head `43b2464` không đổi) + đọc live (PR 403 ×2, issue 403 ×1 — dùng lại bản đọc tốt ~22:40 JST).
- ~22:47–23:10 JST: chuỗi checker — shift_checker_r285.py thiếu tail (chỉ in "extracted pairs: 62", không ghi gì); dựng builder trực tiếp `build_checker_r285.py` + `build_fill_r285.py`; builder bắt 3 lỗi thật (xem Bài học 79); fill chạy sạch lần đầu (145 dòng / 116 entry); checker PASS 166/166.
- ~23:13 JST: scope audit + merge-tree; content commit `1e45131` 23:13:54 JST; push ~23:16 JST; đọc sau push; báo cáo này ~23:16 JST.

## R285 đóng khoảng trống

- Body v2: 96.042 ký tự (net +287 so với R284: +271 đoạn R284 mới −182 gọn R192 + 28 trail + 30 tiêu đề + 5 Ghi-chú "/R284" + 0 range R3–R191→R3–R192 + 135 head line), headroom 8.958 so với 105.000; head line 1.641 ký tự (+135 — head line mới ghi cả hai lần làm tươi payload R284 + đường đọc public API với băm lại byte-exact); R192 gọn 396 → 214 (gọn đơn thứ hai mươi lăm); đoạn R284 đúng 270 ký tự (theo checker).
- Checker `check_pr119_restructure_r285_v1.py`: PASS 166/166 (165 + 1 check row-convention mới cho tuple R283 `("R283", "0ad0e59", 3245)`); validation JSON status PASS, failures [].
- ĐÍNH CHÍNH báo cáo R284: dòng push của nó ghi `4002095..0ad0e59` và dòng đọc sau push ghi head `0ad0e59` — KHÔNG đúng: push thực tế gộp `4002095..43b2464` (content `0ad0e59` + report `43b2464`), đọc API sau push là head `43b2464`. Hàng R284 trong index (vòng này) ghi đúng; các số liệu khác của báo cáo R284 đã xác minh lại sạch (xem dưới).
- Build fill + fill sạch lần đầu (đoạn SHA-hits 145 dòng / 116 entry — 114 sha của R284 + `43b2464` cover + `0ad0e59` content R284, KHÔNG retire sha nào; extra-token khớp R284, 43 = 43; chạy lại idempotent); `daf9540` vẫn 15 lần ngoài đoạn; `cac9c07` đo được 2 lần ngoài đoạn (lesson (53) ghi 1 lần — số liệu cũ, xem Bài học 79).
- R284 figures re-verified sạch (759/3247/+407089 tại `43b2464` = 758/3245/+406353 tại `0ad0e59` + 1 commit, 2 files, 736 insertions) NGOẠI TRỪ dòng push/post-push của nó (đính chính ở trên); hàng R284 trong index ghi đủ 3 phiên bản payload R284.

## Kiểm chứng sau commit nội dung

- Content commit `1e45131` đã push: `43b2464..1e45131`, ls-remote xác nhận remote head `1e45131`, integration `f3db6b3`.
- Đọc API sau push: PR read lỗi 403 rate-limit (file `hidden_files/pr119_read_r285_after.json`) — không có số API sau push; head xác minh qua ls-remote; số đếm git tại `1e45131`: 760/3248/+408517/0. Issue #116 đọc lại sau push (~23:17 JST): vẫn 34 comment, ACK `6862732081`.
- Scope audit cumulative tại head: 3248 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`); block R285: 3 path / 0 violation mới.

## Payload R285

- Dựng sau push báo cáo bằng `r285_payload.py` từ body v2 + Head làm tươi tới head báo cáo (đọc API mới sau push báo cáo); .bak + 2 bản sao prepost giữ nguyên bản chuẩn bị; số đo v2 ghi trong nhật ký `~/memory/2026-11-27.md` + tin cuối lượt chạy, và hàng R285 trong index (vòng sau) ghi cả hai phiên bản.
- Payload SẴN SÀNG TRÌNH BÀY (đã qua 21:30 JST — luồng chính trình vào sáng mai theo lệnh); CHƯA ĐĂNG — cần thẻ duyệt của chủ dự án. Thẻ sống ~30 phút — bấm khi còn ngồi máy.
- Widget R284 giờ stale, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 96.042 ký tự, headroom 8.958 so với 105.000. Gọn đơn tiếp theo R193 ở R286. Đoạn đầy còn lại R193..R284 = 92 đoạn; khối gọn R2–R192 = 191 dòng.
- Net vòng này +287 khi head line tăng 135; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(78) xem báo cáo các vòng trước. Bài học (79) MỚI VÒNG NÀY (R285):

(a) SHIFT SCRIPT THIẾU TAIL (lesson 79): `shift_checker_r285.py` để lại từ lượt 21:40 chỉ có trích xuất pair + shift() + override, KHÔNG có code áp dụng — chạy chỉ in "extracted pairs: 62", diff 0, không ghi gì. Đừng tin mù file script "đã sửa lần cuối 22:39" — kiểm chứng bằng cách chạy + diff trước khi dùng. Sửa: dựng builder trực tiếp `build_checker_r285.py` (áp 62 pair đã transform lên checker R284 + skeleton reps), tái dùng được cho R286 bằng cách shift.
(b) SHIFT() KHÔNG MAP IDENTIFIER LOWERCASE (lesson 79a): `shift()` chỉ map `R284` hoa — tên file `check_pr119_restructure_r284_v1.py` (chữ `r284` thường) và biến `r283_note`/`r283note` KHÔNG được shift, gây lỗi stale-sweep rồi `NameError: r284_note_ok` ở lần chạy checker đầu. Sửa: builder rep riêng `r284_v1` → `r285_v1` và `r283_note_ok`/`r283_note`/`r283note` → `r284_*` sau shift. Cùng họ lỗi với tên file — kiểm tra mọi identifier lowercase mang số vòng khi shift.
(c) LESSON54 THIẾU DẤU ĐÓNG DOCSTRING (lesson 79b): hằng `LESSON54` chỉ mang nội dung lesson, không mang `"""` đóng docstring — builder đầu viết checker lỗi `SyntaxError: unterminated triple-quoted string literal`. Sửa: pair lesson append `LESSON54 + '"""'` (đúng như gen R284 đã làm với LESSON53_PASS1).
(d) TUPLE-LIST ANCHOR + GIÁ TRỊ SAI (lesson 79c): bản nháp `_tuple_list_append` neo sai tuple R282 (`("R282", "c2f9283", 3242)):` không tồn tại — pair rơi về generic shift, mislabel toàn bộ đuôi tuple (R279→R280, R280→R281, R281→R282, R282→R283) + ghi sai tuple mới `("R283", "4002095", 3245)`. Checker run bắt lỗi thật: `row-convention R283 cumulative 3242 == diff at 0ad0e59` (đo được 3245). Quy ước đúng (xác minh từ git): tuple (vòng N, content sha của vòng N+1, số file tại sha đó) — tuple R283 đúng là `("R283", "0ad0e59", 3245)`, chèn trước tuple CUỐI R281 (giữ nguyên mẫu R284 chèn R282 trước R281). Sửa anchor thành `("R281", "b948d93", 3239)):` + tuple đúng → checker PASS.
(e) CAC9C07 ĐO 2 LẦN, KHÔNG PHẢI 1 (lesson 79d): lesson (53) ghi cover R281 `cac9c07` "1 lần ngoài đoạn" — fill đo được 2 lần (lesson (52) nhắc 1 + lesson (53) nhắc 1 trong câu sửa cover nguồn). Entry vẫn giữ (≥1) nên fill sạch; chỉ số liệu trong câu lesson là cũ. Quy tắc: số lần xuất hiện trong lesson text phải đo từ đĩa sau khi fill, không ghi từ bản nháp.
(f) ĐÍNH CHÍNH BÁO CÁO R284 (lesson 79e): báo cáo R284 ghi push `4002095..0ad0e59` + đọc sau push head `0ad0e59` — nhầm content sha thành head sha. Quy tắc: push line luôn ghi `coverage-head..report-head` (report head = head sau push báo cáo), đọc sau push ghi head đó; số đếm git trong hàng R284 phải là số tại content (`758/3245/+406353` tại `0ad0e59`), KHÔNG ghi nhầm thành số đọc API của head (`759/3247/+407089` tại `43b2464`) — chính lỗi này của báo cáo R284.
(g) API 403 RATE-LIMIT KÉO DÀI (lesson 79f): đọc mới PR + issue qua public API lỗi 403 cả 3 lần lượt này (~22:46, ~22:56 JST) — dùng lại bản đọc tốt ~22:40 JST (head/counts/mergeable/body-hash khớp), head xác minh không đổi qua fetch. Quy tắc: lưu body lỗi dưới tên riêng theo giờ, không ghi đè bản đọc tốt; thử lại sau push báo cáo (rate-limit thường reset trong giờ).
