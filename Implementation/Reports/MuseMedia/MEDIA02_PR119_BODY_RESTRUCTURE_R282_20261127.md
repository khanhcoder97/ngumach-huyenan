# MEDIA-02 — PR #119 Body Restructure R282 (2026-11-27)

## Tóm tắt

- Vòng R282: gọn ĐƠN R189 (gọn đơn thứ HAI MƯƠI HAI); index + body v2 + checker đồng bộ tới head `cac9c07` (753 commit / 3238 file / +400604 từ merge-base `cf17178`); merge-tree tại `cac9c07` vs integration `f3db6b3` exit 0, tree `814f9f0d…`.
- Vòng này chạy MỘT GIAI ĐOẠN (lượt 15:40 JST, không timeout): fetch ~15:58 JST; đọc live PR/issue ~15:59–16:00 JST; transform + edit + gen/shift/fill + checker ~16:00–16:47 JST (kẹt hai lần ở chuỗi generator — bài học 76a/76b/76d); content commit `b948d93` 16:55:52 JST; đọc sau push ~16:56–16:57 JST; payload R282 build ~16:59 JST; báo cáo này ~17:00 JST.
- Không có sự kiện đăng bài giữa các vòng: payload R281 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R281 bị R282 thay thế.
- CẢNH BÁO STALE (hai phiên bản payload R281): bản chính (main) payload R281 ĐÃ ĐƯỢC làm tươi sau push báo cáo ~15:52 + ~15:54–15:55 JST (Head `cac9c07`, 95.336 ký tự, sha `39ac6038`, JSON 106.477 byte, sha256 `2ff94537`, head line 1340 ký tự, mergeable true/clean) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (95.432 ký tự, sha `4f47ec8c`, JSON 106.597 byte, sha256 `40c883cb`); cả hai phiên bản đã xác minh lại từ đĩa lượt này; hàng R281 trong index ghi cả hai phiên bản.
- Content commit `b948d93` (~16:55 JST): 3 file, 1457 insertions, 11 deletions; scope audit block (`cac9c07..b948d93`) 3 path / 0 violation; cumulative tại `b948d93` = 3239 path / 1 violation — artifact `.gitattributes` đã biết.
- Số đếm tại `b948d93`: 754 commit / 3239 file / +402050 — khớp API đọc sau push. Additions: 400604 + (1457 − 11) = 402050.
- Merge-tree tại `b948d93` vs `f3db6b3`: exit 0, tree `6ef53f32…`.
- Push: `cac9c07..b948d93`; ls-remote xác nhận remote head `b948d93` VÀ integration `f3db6b3`.
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- Đọc live lượt này KHÔNG qua connector (đường đọc connector gãy giữa vòng — bài học 75a): đọc trước push qua public API (browser) ~15:59/~16:00 JST, đọc sau push qua browser task ~16:56–16:57 JST (PR + issue, mỗi cái một task riêng); đọc sau push xác nhận head `b948d93`, 754/3239/+402050/0, mergeable true, state unstable (CI đang chạy trên head mới).
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (public API qua browser, ~15:59 JST): head `cac9c07`, 753/3238/+400604, mergeable true / state clean, updated_at 2026-11-27T06:51:19Z, live body R263 (Head `daf9540`, 717/3184), tiêu đề kết thúc "+ R263" — khớp git tại head báo cáo.
- Issue #116 (public API qua browser, ~16:00 JST): đúng 34 comment, mới nhất ACK `6862732081` (2026-11-13T19:24:48Z); không chỉ đạo mới kể từ Gói 39.
- Đọc sau push (browser task, public API, ~16:56–16:57 JST): head `b948d9327fce5c6d30e938b9f15d058cfecb1bc7`, 754/3239/+402050/0 — khớp git tại content commit; mergeable true; state unstable (CI đang chạy trên head mới — giá trị này ghi trong head line payload, main làm tươi ở bước trình nếu CI xong); live body vẫn R263, tiêu đề kết thúc "+ R263", updated_at 2026-11-27T07:55:57Z (đổi do push R282 cập nhật head, body không đổi). Issue #116 đọc LẠI sau push (~16:56 JST): vẫn 34 comment, mới nhất 6862732081 — khác R281 (không đọc lại sau push).
- GIỚI HẠN ĐỌC LƯỢT NÀY (ghi trung thực): trình duyệt xác minh được head/tiêu đề/số đếm/mergeable/updated_at, nhưng KHÔNG băm lại được độ dài/sha của live body (không có cách chạy mã/băm trên chuỗi ~95 nghìn ký tự trong trang JSON) — nên giá trị 94.825 ký tự / sha `07316552` trong head line của payload R282 được ghi rõ là giá trị R263 đã đọc trực tiếp byte-exact lúc đăng R263 (2026-11-26 ~16:08 JST), không phải hash mới lượt này. Head line payload nói rõ điểm này (bài học 75e).
- GHI CHÚ CỦA TRÌNH DUYỆT (không phải lỗi đọc): đoạn ghi chú nhúng trong live body R263 vẫn mô tả trạng thái TRƯỚC khi đăng R263 (tiêu đề kết thúc "+ R262", live body R262, 94.873 ký tự, sha `891f0c91`, updated_at 2026-11-26T07:06:26Z) — đó là bản ghi thời điểm chuẩn bị payload R263 nhúng trong head line của nó, không phải tuyên bố về trạng thái live hiện tại; trạng thái live đã xác minh độc lập bằng tiêu đề +R263, đoạn mở đầu body và các đoạn R263 trong body. Tương tự, số liệu trong dòng Head của body (717/3184/363157) là số đếm bằng diff từ merge-base `cf17178`, khác số liệu API live (754/3239/402050) — hai cách đếm khác nhau, không phải lỗi đọc.

## Mốc giờ

- Lượt 15:40 JST: fetch ~15:58 JST; đọc live PR/issue ~15:59/~16:00 JST; transform + edit (2 lần sửa generator) ~16:00–16:20 JST; gen/shift checker (6+ sửa meta-script) ~16:20–16:43 JST; build fill + fill ~16:43–16:47 JST; checker file 16:47:23 JST; checker lần 1 FAIL 162/163 ~16:47 JST (lỗi Ghi-chú); sửa transform + chạy lại edit ~16:50 JST; checker lần 2 FAIL 162/163 (validation JSON ô nhiễm git status); xóa validation JSON, checker lần 3 PASS 163/163 16:55:08 JST; content commit `b948d93` 16:55:52 JST; push ~16:56 JST; đọc sau push 16:56–16:57 JST; payload R282 build 16:59:48 JST (mtime file); báo cáo này ~17:00 JST.

## R282 đóng khoảng trống

- Body v2: 95.603 ký tự (net +188 so với R281: −272 gọn R189 + 271 đoạn R281 mới + 28 trail + 30 tiêu đề + 5 Ghi-chú "/R281" + 0 range R3–R188→R3–R189 + 126 head line), headroom 9.397 so với 105.000; head line 1.545 ký tự (+126 — head line mới ghi cả hai phiên bản payload R281 + đường đọc public API); R189 gọn 486 → 214 (gọn đơn thứ hai mươi hai); đoạn R281 đúng 271 ký tự (theo checker).
- Checker `check_pr119_restructure_r282_v1.py`: PASS 163/163 (163 = 162 + 1 check row-convention mới cho tuple R280) — SAU 2 LẦN FAIL 162/163 + 1 LẦN CHẠY LẠI EDIT (bài học 76a/76c); validation JSON status PASS, failures [].
- Generator sửa nhiều lỗi trước khi chạy sạch (bài học 76b/76d); shift checker 62/62 cặp sạch; build fill + fill sạch (đoạn SHA-hits 139 dòng / 112 entry = 110 sha của R281 + `cac9c07` cover + `53d7ff0` content R281; extra-token khớp R280/R281, 43 = 43); `daf9540` vẫn 15 lần ngoài đoạn.
- R281 figures re-verified sạch (753/3238/+400604 tại `cac9c07` = 752/3236/+399879 tại `53d7ff0` + 1 commit, 2 files, 725 insertions) NGOẠI TRỪ dòng "main == .bak" của nó (main đã làm tươi sau push báo cáo ~15:52 + ~15:54–15:55 JST).

## Kiểm chứng sau commit nội dung

- Content commit `b948d93` đã push: `cac9c07..b948d93`, ls-remote xác nhận remote head `b948d93`, integration `f3db6b3`.
- Đọc API sau push: head `b948d93`, 754/3239/+402050/0, live body R263; issue #116 vẫn 34 comment, ACK `6862732081`.
- Scope audit block (`cac9c07..b948d93`): 3 path / 0 violation. Cumulative tại head: 3239 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`).

## Payload R282

- Dựng sau push bằng `r282_payload.py` từ body v2 + Head làm tươi tới `b948d93` (điền POSTPUSH từ handoff trình duyệt; sửa bug "JST JST" trong template head line — bài học 76e).
- Body payload: 95.477 ký tự, sha `49e800ca`; JSON 106.658 byte (headroom 24.414 byte so với trần 131.072); tiêu đề 765 ký tự, kết thúc "+ R282"; head line 1.419 ký tự (1.545 → 1.419, −126 — head line mới ngắn hơn vì chỉ ghi một lần đọc sau push, không còn hai điều khoản làm tươi payload R281); main == .bak == 2 bản sao prepost, sha256 `fc9bf092`.
- ĐÍNH CHÍNH HEAD (bài học 72): payload chuẩn bị trên ghi head nội dung `b948d93` — sau khi commit báo cáo này + push, main sẽ được làm tươi sang head báo cáo (đọc API mới sau push báo cáo); .bak + 2 bản sao prepost giữ nguyên bản chuẩn bị; số đo v2 ghi trong nhật ký `~/memory/2026-11-27.md` + tin cuối lượt chạy, và hàng R282 trong index (vòng sau) ghi cả hai phiên bản.
- Payload SẴN SÀNG TRÌNH BÀY (lượt chạy bắt đầu ~15:40 JST, giờ làm việc); CHƯA ĐĂNG — cần thẻ duyệt của chủ dự án. Thẻ sống ~30 phút — bấm khi còn ngồi máy.
- Widget R281 giờ stale, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 95.603 ký tự, headroom 9.397 so với 105.000. Gọn đơn tiếp theo R190 ở R283. Đoạn đầy còn lại R190..R281 = 92 đoạn; khối gọn R2–R189 = 188 dòng.
- Net vòng này +188 khi head line tăng 126; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(75) xem báo cáo các vòng trước. Bài học (76) MỚI VÒNG NÀY (R282):

(a) GHI-CHÚ LIST PAIR APPEND SAI VÒNG — CHECKER BẮT TRƯỚC COMMIT: `pair_new` trong `gen_transform_r282.py` append `/R280` thay vì `/R281` (meta-script `make_gen_transform_r282.py` shift các append khác ở cùng vùng nhưng SÓT override này — không có rep nào chạm tới nó); body v2 ra danh sách Ghi-chú ".../R279/R280/R280." thay vì ".../R280/R281."; checker lần 1 FAIL 162/163 đúng ở check đó. Sửa durable: thêm 2 rep vào meta-script (comment + code `l2_new`), chạy lại meta → gen → transform_edit → edit; restore index+body từ `cac9c07` rồi chạy lại edit (dry-run 18 = apply 18, idempotency 0); body 95.603, Ghi-chú đúng. Quy tắc: mọi append mang số vòng trong generator đều phải có rep shift — grep `/R28` trên file sinh ra trước khi chạy transform.
(b) SỬA TAY TRÊN FILE SINH RA BỊ MẤT KHI CHẠY LẠI META-SCRIPT: fix (1) lượt đầu (row-assert loop match cả `"row.count("`) chỉ sửa trên `gen_transform_r282.py` trực tiếp, không đưa vào meta-script; chạy lại `make_gen_transform_r282.py` đã ghi đè gen bằng bản chưa sửa → `transform_edit_r282.py` kẹt assert `row.count("3b34e1a") == 1`. Sửa durable: đưa fix vào meta-script (điều kiện loop thành `(" in row" in frag or "row.count(" in frag)`), chạy lại meta → gen → transform_edit sạch (assert đúng `row.count("d2eb9b5") == 1`, lesson 50). Quy tắc: mọi fix tay trên file sinh ra phải được đưa vào script tạo ra nó ngay trong lượt đó, nếu không lần chạy lại sẽ mất fix.
(c) VALIDATION JSON LÀM Ô NHIỄM GIT STATUS: checker assert "git status shows only index + body + this checker" — file validation JSON từ lần chạy FAIL trước còn nằm untracked nên check rớt lần 2 (162/163). Xóa file validation trước khi chạy lại checker (checker tự ghi lại ở cuối) → PASS 163/163. File validation thuộc commit báo cáo, không thuộc content commit — đừng commit nó chung với content.
(d) CHUỖI SHIFT CHECKER SỬA NHIỀU LỖI OFF-BY-ONE CÙNG LỚP: `make_gen_shift_checker_r282.py` cần 6+ sửa (merge-tree rep chuỗi phải thay cả khối; row-block assert và tuple assert phải chạy rep theo thứ tự NGƯỢC; `@@SHA_HITS@@` thừa một `@`; compact_ok phải thay cả khối; shift-docstring 2 dòng phải shift cả vế sau; milestone block phải thay cả khối). Cùng một lớp lỗi: rep 2 dòng chỉ shift vế đầu, vế sau stale một vòng; rep chuỗi (A→B rồi B→C) phải chạy ngược thứ tự. Quy tắc: rep nào có old/new là hai vế của cùng một cặp thì phải shift CẢ hai vế trong cùng một rep (dạng block), hoặc chạy rep theo thứ tự ngược (vế sau trước) — và luôn đọc file sinh ra để kiểm tra cả hai vế trước khi chạy.
(e) BUG "JST JST" TRONG BUILDER PAYLOAD: template HEAD_LINE của `r281_payload.py` thêm " JST" sau placeholder `{r1}`/`{r2}` trong khi giá trị đọc đã kết thúc bằng "JST" → head line payload R281 có "JST JST" (ghi trong lesson (51) của checker R282). Sửa ở `r282_payload.py`: template không còn " JST" sau placeholder (chỉ một lần đọc lượt này, `{r1}` = "~16:56–16:57 JST"); đã xác minh payload R282 không chứa "JST JST".
