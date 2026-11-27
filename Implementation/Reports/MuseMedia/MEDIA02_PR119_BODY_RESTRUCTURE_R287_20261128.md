# MEDIA-02 — PR #119 Body Restructure R287 (2026-11-28)

## Tóm tắt

- Vòng R287: gọn ĐƠN R194 (gọn đơn thứ HAI MƯƠI BẢY); index + body v2 + checker đồng bộ tới head `75eedfc` (763 commit / 3253 file / +411433 từ merge-base `cf17178`); merge-tree tại `75eedfc` vs integration `f3db6b3` exit 0, tree `84b7ae5c…`.
- Vòng này là lượt định kỳ 02:40 JST 2026-11-28 làm tiếp R287: lượt 01:40 JST đã fetch + đọc live + áp edit (body v2 96.234 ký tự, changed 18, idempotent 0) rồi timeout trước khi build checker; lượt này làm tiếp từ đĩa — sửa 3 lỗi builder (xem Bài học 81), fill chạy sạch lần đầu, checker PASS 168/168; content commit `9383178`. Không có sự kiện đăng bài giữa các vòng: payload R286 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R286 bị R287 thay thế.
- CẢNH BÁO STALE (hai phiên bản payload R286): bản chính (main) payload R286 đã làm tươi sau push báo cáo (Head `75eedfc`, 95.901 ký tự, sha `5bf30ea7`, JSON 107.097 byte, sha256 `21c01b7b`, head line 1348, mergeable true/unstable) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (95.877 ký tự, sha `4c898b68`, JSON 107.067 byte, sha256 `495c0b02`, head line 1324, Head `692a033`); cả hai phiên bản đã xác minh lại từ đĩa lượt 01:40; main != .bak. Title 765 ký tự kết "+ R286".
- Content commit `9383178` (~03:05 JST): 3 file, 1444 insertions, 11 deletions; scope audit cumulative 3254 path / 1 violation — artifact `.gitattributes` đã biết (block 3 path / 0 violation mới).
- Số đếm tại `9383178`: 764 commit / 3254 file / +412866 — số đếm git, KHỚP ĐÚNG số API sau push (xem dưới). Additions: 411433 + (1444 − 11) = 412866.
- Merge-tree tại `9383178` vs `f3db6b3`: exit 0, tree `3861309f…`.
- Push: `75eedfc..9383178`; ls-remote xác nhận remote head `9383178` VÀ integration `f3db6b3` (~03:06 JST).
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (public API qua curl, bản đọc lượt 01:40 JST dùng lại + đọc lại ~02:45 JST lượt này, giá trị giống hệt, file `hidden_files/pr119_read_r287_0140.json`; đọc lại ~02:45 JST chỉ kiểm tra inline, không lưu file riêng): head `75eedfc`, API 763 commit / 3253 file / +411433 / 0, mergeable true/clean, updated_at 2026-11-27T16:36:38Z, live body R263 băm lại byte-exact (94.825 ký tự, sha `07316552`, 0 U+FFFD); head xác minh không đổi qua fetch (local head = remote head = `75eedfc`, integration `f3db6b3`).
- Issue #116 (public API qua curl, bản đọc ~01:40 JST + đọc lại ~02:45 JST, file `hidden_files/issue116_read_r287_0140.json`): đúng 34 comment, mới nhất ACK `6862732081` (2026-11-13); không chỉ đạo mới kể từ Gói 39.
- PR read xác minh lại lượt này `base.sha f3832338` LÀ ancestor của integration `f3db6b3` (20 commit sau — merge PR #118 ngày 2026-11-05); merge-tree vẫn chạy trên `f3db6b3` live như mọi vòng.
- Đọc sau push nội dung (public API qua curl, ~03:06 JST, HTTP 200 cả hai, file `hidden_files/pr119_read_r287_after_content.json` + `issue116_read_r287_after_content.json`): PR head `9383178`, API 764/3254/+412866/0 — KHỚP ĐÚNG số git tại content commit; mergeable true/unstable (CI đang chạy trên head mới — lần clean gần nhất tại `75eedfc`), updated_at 2026-11-27T17:56:19Z; live body vẫn R263 (94.825 ký tự, sha `07316552` — push không đổi body). Issue #116 đọc lại sau push: vẫn 34 comment, mới nhất 6862732081.

## Mốc giờ

- ~01:40 JST 2026-11-28: lượt định kỳ bắt đầu R287 — fetch + đọc live + áp edit (changed 18, idempotent 0) rồi timeout trước khi build checker; head đứng yên `75eedfc`, không commit gì.
- ~02:40 JST: lượt này bắt đầu — fetch lại (remote head `75eedfc` không đổi, integration `f3db6b3` không đổi), đọc live lại ~02:45 JST (giá trị giống hệt bản 01:40).
- ~02:50–03:00 JST: chuỗi checker — builder lỗi 2 lần trước khi chạy sạch (xem Bài học 81: old-side shift + SHA-map collision, rồi milestone rep sai dấu ngoặc); fill chạy sạch lần đầu (148 dòng / 119 entry, đúng dự đoán); checker PASS 168/168.
- ~03:05 JST: scope audit + merge-tree; content commit `9383178`; push ~03:06 JST; đọc sau push; báo cáo này ~03:07 JST.

## R287 đóng khoảng trống

- Body v2: 96.234 ký tự (net +159 so với R286: +271 đoạn R286 mới −182 gọn R194 + 28 trail + 30 tiêu đề + 5 Ghi-chú "/R286" + 0 range R3–R193→R3–R194 + 7 head line), headroom 8.766 so với 105.000; head line 1.529 ký tự (+7 — đo từ đĩa); R194 gọn 396 → 214 (gọn đơn thứ hai mươi bảy); đoạn R286 đúng 270 ký tự (theo checker).
- Checker `check_pr119_restructure_r287_v1.py`: PASS 168/168 (167 + 1 check row-convention mới cho tuple R285 `("R285", "692a033", 3251)`); validation JSON status PASS, failures [].
- ĐÍNH CHÍNH checker R286 (lesson 81, xem Bài học): không có lỗi đếm trong checker R286 — các số của nó (763/3253/+411433 tại `75eedfc` = 762/3251/+410689 tại `692a033` + 1 commit, 2 file, 744 insertions) đã xác minh lại sạch; chỉ builder R287 (chuỗi checker) mang 3 lỗi, đã sửa trước khi transform chạy sạch (xem Bài học 81).
- Build fill + fill sạch lần đầu (đoạn SHA-hits 148 dòng / 119 entry — 117 sha của R286 + `75eedfc` cover + `692a033` content R286, KHÔNG retire sha nào; extra-token khớp R286, 43 = 43; chạy lại idempotent); `daf9540` vẫn 15 lần ngoài đoạn; không sha nào retire vòng này.
- Số đếm API sau push khớp đúng số git (764/3254/+412866/0 tại `9383178` cả hai nguồn).

## Kiểm chứng sau commit nội dung

- Content commit `9383178` đã push: `75eedfc..9383178`, ls-remote xác nhận remote head `9383178`, integration `f3db6b3`.
- Đọc API sau push (~03:06 JST, HTTP 200): PR head `9383178`; số API 764/3254/+412866/0 khớp đúng số git tại `9383178`; mergeable true/unstable (CI đang chạy); live body vẫn R263. Issue #116 đọc lại sau push: vẫn 34 comment, ACK `6862732081`.
- Scope audit cumulative tại head: 3254 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`, sha256 `23352e4c…`; khác merge-base `cf17178` sha256 `54ee7996…`); block R287: 3 path / 0 violation mới.

## Payload R287

- Dựng sau push báo cáo bằng `make_r287_payload.py` (adapt từ `make_r286_payload.py`) từ body v2 + Head làm tươi tới head báo cáo (đọc API mới sau push báo cáo); .bak + 2 bản sao prepost giữ nguyên bản chuẩn bị; số đo v2 ghi trong nhật ký `~/memory/2026-11-28.md` + tin cuối lượt chạy, và hàng R287 trong index (vòng sau) ghi cả hai phiên bản.
- Payload SẴN SÀNG TRÌNH BÀY (đã qua 01:30 JST — luồng chính trình vào sáng mai theo lệnh); CHƯA ĐĂNG — cần thẻ duyệt của chủ dự án. Thẻ sống ~30 phút — bấm khi còn ngồi máy.
- Widget R286 giờ stale, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 96.234 ký tự, headroom 8.766 so với 105.000. Gọn đơn tiếp theo R195 ở R288. Đoạn đầy còn lại R195..R286 = 92 đoạn; khối gọn R2–R194 = 193 dòng.
- Net vòng này +159 khi head line tăng 7; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(80) xem báo cáo các vòng trước. Bài học (81) MỚI VÒNG NÀY (R287):

(a) BUILDER R287 MANG BA LỖI, ĐỀU BỊ ASSERTION BẮT TRƯỚC KHI GHI (lesson 81): (1) `transform_pair` làm `out_old = shift(old)` — SAI: theo tiền lệ R286, old side phải là new side của cặp trước NGUYÊN VĂN (`out_old = new`); shift(old) biến dạng cả SHA đầy đủ lẫn SHA ngắn. (2) `shift()` dùng `str.replace` tuần tự cho SHA_MAP — SAI: lượt thay SHA ngắn `"8cb82a1" → "75eedfc"` viết đè lên SHA đầy đủ `"8cb82a146d…"` vừa chèn ở lượt trước, thành `"75eedfc46d…"`; sửa bằng placeholder-protected shift (longest-first, theo `shift_checker_r286.py`). (3) Hai assert trong builder sai: assert SHA đầy đủ MỚI (`75eedfc0b80…`) vắng mặt — đúng ra phải assert SHA đầy đủ CŨ (`8cb82a146d…`) vắng mặt (tiền lệ stale-sweep của R286); cặp assert `"R286 (lượt cập nhật này)" in skeleton` / `"R287 …" not in skeleton` bị ĐẢO — body sau edit chỉ còn `"R287 (lượt cập nhật này)"`, checker phải kiểm R287; thêm skeleton rep cho dòng `compact_ok = …` (dòng này không nằm trong cặp nào — tiền lệ rep của R286). Quy tắc: builder vòng N phải đối chiếu từng assert với checker vòng N−1 ĐÃ ÁP DỤNG (không chép từ báo cáo), và mọi lượt `str.replace` trên SHA phải dùng placeholder.
(b) LỖI RENAME SÓT TÁI DIỄN — LẦN THỨ TƯ (lesson 81a, cùng lớp với R259/R260): sau khi builder chạy sạch, checker lỗi `NameError: r285_note_ok` ở dòng 875 — skeleton rep cho milestone line mang dấu `"` thừa ở đầu (`'"milestone_ok …"'` thay vì 8-space indent không ngoặc), nên `str.replace` lặng lẽ không thay gì. Sửa rep (kèm `assert count == 1`), build lại + fill lại, checker PASS 168/168. Quy tắc: mọi `skeleton.replace` không-assert trong builder phải có `assert count` — replace lặng lẽ là lỗi chờ sẵn.
(c) FILL ĐÚNG DỰ ĐOÁN LẦN ĐẦU (lesson 81b): fill chạy sạch lần đầu (148 dòng / 119 entry; extra-token 43 = 43, chạy lại idempotent) — các câu LESSON56 trong checker về fill ("first try") do đó đúng sự thật, không cần sửa. Ngược lại, các câu LESSON56 về builder ("needed NO fixes") là SAI (viết trước khi builder chạy) và đã sửa trong builder TRƯỚC khi transform chạy sạch — không để văn bản checker mang lời sai về chính chuỗi của nó.
(d) ĐỌC LIVE LẶP LẠI GIỐNG HỆT (lesson 81c): đọc lại ~02:45 JST cho đúng giá trị bản 01:40 JST (head `75eedfc`, mergeable true/clean, live body R263 sha `07316552`, issue 34 comment) — khi head không đổi, đọc lặp là kiểm chứng rẻ, không phải lãng phí; số API sau push khớp git đúng (764/3254/+412866/0).
