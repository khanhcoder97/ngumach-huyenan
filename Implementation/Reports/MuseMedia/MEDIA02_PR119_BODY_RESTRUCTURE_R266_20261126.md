# MEDIA-02 — PR #119 Body Restructure R266 (2026-11-26)

## Tóm tắt

- Khối: body restructure R266 — gọn ĐƠN R173 (gọn đơn thứ SÁU; gọn đơn bắt đầu ở R168); index + body v2 + checker đồng bộ tới head `5584a8f` (721 commit / 3190 file / +367162 từ merge-base `cf17178`); merge-tree tại `5584a8f` vs integration `f3db6b3` exit 0, tree `83b74af6…`.
- SỰ KIỆN ĐĂNG GIỮA HAI VÒNG: không có — payload R265 CHƯA ĐĂNG, live body vẫn R263 (94.825 ký tự, sha `07316552`); payload R265 sẵn sàng trình từ vòng trước, bị R266 supersede trước khi đăng.
- Vòng này chạy MỘT PHA (~23:33–23:50 JST): fetch ~23:33 JST, đọc live, áp edit index + body v2, dựng chuỗi checker tới `check_pr119_restructure_r266_v1.py` + fill SHA-hits, checker chạy sạch **PASS 147/147** ngay lần đầu, scope audit block **3 path / 0 violation**, commit nội dung `e444f0c` + push (ls-remote xác minh), đọc live post-push (2 lần), viết báo cáo này + payload R266.
- Đọc live post-push (~23:48 + ~23:49 JST, connector, 2 lần): PR head `e444f0c`, 722 commit / 3191 file / +368519 — khớp đếm git tại commit nội dung; mergeable **null / state unstable** tại head mới (CI đang chạy — cả 2 lần đọc); live body vẫn R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề kết thúc "+ R263", updated_at 2026-11-26T14:48:13Z (đổi do push R266 cập nhật head, body không đổi). Issue #116: **34 comment**, updated_at 2026-11-13T19:24:49Z, mới nhất ACK `6862732081`, **không chỉ đạo mới kể từ Gói 39 (`6815238814`)**.
- Body v2: **94.269 ký tự** (net −181 so với R265), headroom **10.731** so với 105.000; head line 1.228 ký tự; R173 gọn 713 → 214 (gọn đơn thứ sáu); đoạn R265 đúng 270 ký tự (theo checker).
- Commit nội dung `e444f0c` (~23:47 JST): 3 file, 1368 insertions, 11 deletions; scope audit block (`5584a8f..e444f0c`) **3 path / 0 violation**; cumulative tại `e444f0c` = 3191 path / 1 violation — artifact `.gitattributes` ở merge-base đã biết.
- Payload R266 chuẩn bị sau push (dựng từ body v2 + đoạn Head làm tươi theo head sau push): body 94.135 ký tự, sha `8319c8dd` (xem mục Payload), **GIỮ LẠI** — ngoài giờ làm việc (lượt chạy bắt đầu ~23:33 JST), KHÔNG trình; chưa đăng — cần thẻ duyệt của chủ dự án. Lưu ý: mergeable_state trong payload là **unstable** (CI đang chạy lúc đọc post-push) — luồng chính làm tươi Head lúc trình nếu CI đã xong (bài học 39).

## Đọc live

- Lượt này, đọc trước push (connector): live body R263 (94.825 ký tự, sha `07316552`, byte-exact với file JSON R263 trên đĩa, 0 U+FFFD — một lần đọc sạch, không cần đọc lại); mergeable_state clean tại `5584a8f` (mergeable null — GitHub chưa tính lại cờ, state clean là giá trị vận hành); tiêu đề kết thúc "+ R263"; updated_at 2026-11-26T13:22:12Z. Issue read (call-read-tool, method get, ~23:35 JST): 34 comment, updated_at 2026-11-13T19:24:49Z — không chỉ đạo mới. Không thử call-tool get_comments lượt này (count + updated_at không đổi so với lần get_comments đã xác minh ở R265).
- Sau push (~23:48 JST + ~23:49 JST, connector, 2 lần đọc): API — head `e444f0c`, 722/3191, mergeable null, mergeable_state **unstable** (CI đang chạy), live body R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD), tiêu đề 765 ký tự kết thúc "+ R263", updated_at 2026-11-26T14:48:13Z; issue #116 không đọc lại sau push (ghi rõ trong head line của payload).
- Suy ra từ git tại `e444f0c`: rev-list `cf17178..e444f0c` = 722; diff `--name-only` = 3191 file; `--shortstat` = 368519 insertions, 0 deletions — khớp đọc API; merge-tree `e444f0c` vs `f3db6b3` exit 0, tree `4a756f88…`; tại `5584a8f`: 721/3190/+367162 (khớp dòng cumulative của index R266).

## Mốc giờ

- Fetch lượt này chạy đúng giờ hẹn: `.git/FETCH_HEAD` mtime 23:33:21 JST; các số đếm git (721/3190/+367162) đo ~23:34 JST.
- Đọc PR chạy ~23:35 JST (file `pr119_read_r266.json` mtime 23:35:19 JST); đọc issue chạy ~23:35 JST (file `issue116_read_r266.json` mtime 23:35:22 JST).
- Transform/edit/shift/fill/checker/commit/push chạy 23:40–23:48 JST (mtime file: transform 23:40:58, edit 23:41:02, shift 23:45:42, fill 23:46:20, validation JSON 23:46:35; commit nội dung 23:47:27 JST; push xong ~23:48 JST). Đọc post-push 23:48:22 + 23:49:09 JST; payload 23:49:38 JST.

## R266 đóng khoảng trống

- Delivery index: tiêu đề head → `5584a8f`; dòng milestone → 721/3190/367162; delta `ecee5f7..5584a8f`: 2 path, 652 insertions, 0 deletions; một dòng được thêm — R265 (`ecee5f7`/`5584a8f`), ghi payload R265 (94.300 ký tự, sha `dd56f4ea`, CHƯA ĐĂNG — bị R266 supersede) + đính chính số đếm head báo cáo (dòng dev-queue R265 ghi 720/3188/+366510 của head nội dung cho head báo cáo — số thật 721/3190/+367162, đo từ git + xác nhận qua API lượt này) + đính chính lesson (34) của checker R265 + row-convention (dòng R264 = 3188) + sửa dòng Ghi chú + sửa câu "lượt cập nhật này" (chính R265); không có ACK riêng cho R265. Index bao quát mọi khối tới `5584a8f`; 2 commit của R266 gộp vào ở R267.
- Body v2: head line đồng bộ tới `5584a8f` · 721 · 3190 (additions 367162, Gói 39 ID 6815238814, tree `83b74af6…`, mergeable_state clean tại `5584a8f` theo đọc lượt này), cộng đoạn R265 và ghi chú R266. Gọn: đoạn R173 (713 → 214) — gọn ĐƠN thứ sáu. Body 94.269 ký tự — net −181 so với R265 (−499 R173 + 271 đoạn mới + 28 trail + 30 tiêu đề + 5 Ghi-chú list "/R265" + 0 Ghi-chú range "R3–R172"→"R3–R173" − 16 head line — các thành phần theo projection của chuỗi edit; tổng net −181 đo trực tiếp từ đĩa: 94.450 → 94.269).
- Checker `check_pr119_restructure_r266_v1.py`: PASS **147/147** ngay lần đầu (`--out` ghi validation JSON của vòng này; trường "checkpoint" trong JSON mang nhãn vòng trước "PR119 BODY RESTRUCTURE R265" — quy ước đặt tên mang sang của chuỗi shift, không phải lỗi số liệu; checks 147/147, failures []). 147 = 146 + đúng 1 check row-convention mới (tuple R264), khớp bài học vòng R264 mục 6 ("mỗi vòng chỉ thêm đúng 1 check row-convention").
- Fill SHA-hits: `fill_sha_hits_r266.py` đã chạy thành công — đoạn SHA-hits 98 dòng / 80 entry đã điền đầy vào checker. Entry set: 78 entry của R265 + 2 entry mới `5584a8f` (cover) + `ecee5f7` (nội dung R265) lên đầu (80 entry — KHÔNG trừ `daf9540`: xem Đính chính dưới). Extra-token khớp hoàn toàn với R265 (43 token, cùng số lần xuất hiện).
- ĐÍNH CHÍNH FILL (bài học 59b): bản nháp đầu của lesson (35) viết "entry set retires daf9540 (0 occurrences)" — SAI. `daf9540` vẫn còn 2 lần xuất hiện ngoài đoạn SHA-hits: lesson (33) lịch sử ("Head e373cb5 -> daf9540") + chính câu lesson (35) viết về nó. Fill assertion `extra == r265_extra` bắt ngay lần chạy đầu (only-R266=['daf9540']); đã sửa trước commit: lesson (35) ghi đúng "`daf9540` does NOT retire ... keeps it at 2 occurrences, so it stays an entry", entry set giữ 80 (78 + 2 mới), không trừ. Sửa tay danh sách ENTRY_ORDER trong fill script suýt làm rơi `a8fb12d` rồi `aa0eef6` (2 lỗi off-by-one khi sửa 2 dòng) — đã sửa bằng cách tái tạo danh sách bằng code từ ENTRY_ORDER của R265 (78 + 2 mới = 80, 0 trùng). Bài học: không sửa tay danh sách SHA dài; tái tạo bằng code từ danh sách vòng trước.

## Kiểm chứng sau commit nội dung

- Commit nội dung `e444f0c10a327c086c6705dc02ae6ab417e26895` (~23:47 JST): 3 file (body v2, delivery index, checker.py), 1368 insertions, 11 deletions; scope audit block (`5584a8f..e444f0c`): **3 path / 0 violation**; cumulative tại `e444f0c`: 3191 path / 1 violation — artifact `.gitattributes` đã biết.
- Đếm tại `e444f0c`: **722 commit / 3191 file / +368519** — khớp đọc API post-push. Dòng R265 trong index ghi cumulative 3191 — đã xác minh sau commit (diff tại `e444f0c` = 3191, gồm 3190 tại `5584a8f` + 1 checker mới).
- Merge-tree tại `e444f0c` vs `f3db6b3`: exit 0, tree `4a756f88…`.
- Push: `5584a8f..e444f0c` lên `muse/media-production-20261104` (deploy key, không force-push); ls-remote xác minh remote head = `e444f0c10a327c086c6705dc02ae6ab417e26895`.
- Working tree sau commit nội dung: sạch (chỉ còn báo cáo + validation JSON của vòng này, commit ở commit báo cáo).
- Không có execution-risk flag nào chạm luồng chính vòng này.
- Cảnh báo SyntaxWarning `invalid escape sequence '\`'` khi chạy checker: ĐÃ CÓ từ checker R265 (chạy lại R265 cùng cảnh báo) — không phải khuyết điểm vòng này, không ảnh hưởng PASS.

## Payload R266

- Dựng bởi vòng này sau push (script `r266_payload.py` trong goal hidden_files) từ body v2 của vòng + đoạn Head làm tươi DUY NHẤT sang head sau push: head `e444f0c` · 722 · 3191, additions 368519, mergeable **null / unstable** tại `e444f0c` (đọc API tươi post-push ~23:48 + ~23:49 JST — CI đang chạy trên head mới; luồng chính làm tươi Head lúc trình nếu CI đã xong), live body R263 (94.825 ký tự, sha `07316552`, updated_at 2026-11-26T14:48:13Z), merge-tree tree `4a756f88…`, issue #116 34 comment (đọc trước push lượt này ~23:35 JST, không đọc lại sau push — ghi rõ trong head line).
- Body **94.135 ký tự, sha `8319c8dd`**; JSON 105.146 byte < trần 131.072 (còn 25.926 byte); tiêu đề 765 ký tự kết thúc "+ R266" (hậu tố THAY, không nối — bài học R120); envelope đủ (owner `khanhcoder97`, repo `ngumach-huyenan`, pullNumber 119); file `~/workspace/godot-prototype/pr_comments/pr119_update_body_v2_r266.json` + `.bak` byte-identical (sha256 `e7792d4b`) + bản sao byte-identical trong `.bak-prepost-20261124/` và `.bak-prepost-20261126/`.
- **CHƯA ĐĂNG** — cần thẻ duyệt của chủ dự án; **GIỮ LẠI** (ngoài giờ làm việc — lượt chạy bắt đầu ~23:33 JST), luồng chính trình widget trong giờ làm việc. Lưu ý: thẻ duyệt hết hạn sau ~30 phút chờ (đã 10 lần) — nên bấm khi còn ngồi máy. Lưu ý thêm: payload R265 nay ĐÃ LỖI THỜI (head đã sang `e444f0c`) — KHÔNG bấm widget R265.

## Cảnh báo headroom

Body v2 hiện 94.269 ký tự, headroom 10.731. Gọn ĐƠN tiếp theo là R174 ở vòng R267. Đoạn đầy đủ còn lại R174..R265 = 92 đoạn; khối gọn R2–R173 = 172 dòng. Ước tính net mỗi vòng gọn đơn ≈ −100..−250 — headroom an toàn dài hạn.

## Bài học

Lessons carried: toàn bộ danh sách bài học (1)–(58) trong báo cáo R262 + R263 + R264 + R265 cùng thư mục giữ nguyên hiệu lực. Mới vòng này:

(59) NEW THIS ROUND (R266) — ba điều: (a) SỐ ĐẾM HEAD BÁO CÁO ≠ HEAD NỘI DUNG: dòng dev-queue R265 ghi "(720 commit / 3188 file / +366510)" cho head báo cáo `5584a8f` — đó là số của head nội dung `ecee5f7`; commit báo cáo tự nó cộng 1 commit, 2 file, 652 insertions nên số thật tại `5584a8f` là 721/3190/+367162 (đo từ git, khớp API 721/3190/+367162). Quy tắc: số đếm gắn với HEAD NÀO phải đo tại HEAD ĐÓ — không sao chép số của commit trước sang commit sau. (b) FILL: bản nháp lesson (35) viết "`daf9540` retires (0 occurrences)" — sai; lesson (33) lịch sử giữ `daf9540` ở 2 lần xuất hiện nên nó không thể về 0; assertion extra-token của fill bắt ngay lần đầu — sửa lesson trước commit, entry set 80 (78 + 2 mới). Sửa tay danh sách SHA dài gây 2 lỗi off-by-one (`a8fb12d`, `aa0eef6` suýt rơi) — tái tạo danh sách bằng code từ vòng trước. (c) SyntaxWarning `\`` khi chạy checker đã có từ R265 — không phải khuyết điểm mới.
