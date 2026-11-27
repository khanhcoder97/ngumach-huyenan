# MEDIA-02 — PR #119 Body Restructure R284 (2026-11-27)

## Tóm tắt

- Vòng R284: gọn ĐƠN R191 (gọn đơn thứ HAI MƯƠI TƯ); index + body v2 + checker đồng bộ tới head `4002095` (757 commit / 3244 file / +404927 từ merge-base `cf17178`); merge-tree tại `4002095` vs integration `f3db6b3` exit 0, tree `27d3cda5…`.
- Vòng này chạy MỘT lượt dài (~19:40–20:25 JST): fetch + đọc live + edit ~19:40–19:42 JST; chuỗi checker gặp lỗi skeleton rep (sửa 2 lần: `attempted again by` + literal `\n`) rồi chạy sạch; fill chạy 3 pass (pass 1 hồi sinh sha retire do nhắc tên literal trong lesson 53; pass 2 bỏ tên literal; pass 3 sửa số dòng 141 → 143); checker PASS 165/165 ~20:25 JST; content commit `0ad0e59` 20:25:50 JST. Không có sự kiện đăng bài giữa các vòng: payload R283 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R283 bị R284 thay thế.
- CẢNH BÁO STALE (ba phiên bản payload R283): bản chính (main) payload R283 đã làm tươi HAI lần — sau push báo cáo ~19:35 JST (Head `4002095`, 95.420 ký tự, sha `8c2a1095`, JSON 106.562 byte, sha256 `d68986a9`, head line 1297 ký tự, mergeable true/unstable) + ở bước trình ~19:38 JST (Head `4002095`, 95.393 ký tự, sha `1b1d57ca`, JSON 106.501 byte, sha256 `95089b6a`, head line 1270 ký tự, mergeable true/clean) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (95.410 ký tự, sha `46652850`, JSON 106.560 byte, sha256 `ac75be54`); cả ba phiên bản đã xác minh lại từ đĩa lượt này; hàng R283 trong index ghi cả ba phiên bản. Khuyết điểm: head line bản v3 trùng lặp mệnh đề merge-tree (đã ghi).
- Content commit `0ad0e59` (~20:25 JST): 3 file, 1437 insertions, 11 deletions; scope audit cumulative 3245 path / 1 violation — artifact `.gitattributes` đã biết (block 3 path / 0 violation mới).
- Số đếm tại `0ad0e59`: 758 commit / 3245 file / +406353 — khớp API đọc sau push (sẽ ghi). Additions: 404927 + (1437 − 11) = 406353.
- Merge-tree tại `0ad0e59` vs `f3db6b3`: exit 0, tree `b93d7e5f…`.
- Push: `4002095..0ad0e59`; ls-remote xác nhận remote head `0ad0e59` VÀ integration `f3db6b3` (sẽ ghi sau push).
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (public API qua curl, ~19:41 JST — đường đọc connector GÃY LẠI lượt này, bài học 78): head `4002095`, 757/3244/+404927, mergeable_state clean (mergeable true — GitHub đã tính lại cờ, CI đã chạy xong), updated_at 2026-11-27T10:34:05Z, live body R263 băm lại byte-exact (94.825 ký tự, sha `07316552`, 0 U+FFFD); file đọc lưu sẵn `hidden_files/pr119_read_r284.json` (mtime 10:41 UTC = 19:41 JST).
- Issue #116 (public API qua curl, ~19:41 JST): đúng 34 comment, mới nhất ACK `6862732081` (2026-11-13); không chỉ đạo mới kể từ Gói 39. File đọc lưu sẵn `hidden_files/issue116_read_r284.json` (mtime 10:41 UTC = 19:41 JST).
- PR read xác minh `base.sha f3832338` LÀ ancestor của integration `f3db6b3` (20 commit sau — merge PR #118 ngày 2026-11-05); merge-tree vẫn chạy trên `f3db6b3` live như mọi vòng.
- Đọc sau push (public API qua curl, ~20:26 JST): head `0ad0e59`, 758/3245/+406353/0 — khớp git tại content commit; mergeable true; live body vẫn R263 byte-exact (94.825 ký tự, sha `07316552`, 0 U+FFFD); updated_at đổi do push R284 cập nhật head, body không đổi. Issue #116 đọc LẠI sau push (~20:26 JST): vẫn 34 comment, mới nhất 6862732081.
- Hai cách đếm vẫn khác nhau như đã ghi: số liệu API live (758/3245/406353) là số đếm PR-diff; số liệu trong dòng Head của body (758/3245/406353) là số đếm bằng diff từ merge-base `cf17178` — hai số này trùng nhau lượt này vì head line ghi đúng diff từ merge-base; số API live và số Head-line có thể khác nhau ở các vòng khác — không phải lỗi đọc.

## Mốc giờ

- ~19:40 JST: fetch (sạch, không cờ execution-risk) + ls-remote xác nhận remote head `4002095`, integration `f3db6b3`.
- ~19:41 JST: đọc live PR/issue qua public API (file lưu sẵn, mtime 10:41 UTC).
- ~19:40–19:42 JST: edit (transform chain: shift/make/gen/transform/edit chạy sạch; body v2 95.755 ký tự, net +234).
- ~19:45–20:20 JST: chuỗi checker — skeleton rep lỗi 2 lần (sửa `attempted again by` + literal `\n`, bài học 78c/78d) rồi chạy sạch; build fill + fill pass 1 (144 dòng / 115 entry — hồi sinh sha retire); pass 2 (bỏ tên literal trong lesson 53, fill 143 dòng / 114 entry); pass 3 (sửa số dòng 141 → 143 trong lesson 53, fill lại 143 dòng / 114 entry).
- ~20:25 JST: checker PASS 165/165; scope audit + merge-tree; content commit `0ad0e59` 20:25:50 JST; push ~20:26 JST; đọc sau push ~20:26 JST; báo cáo này ~20:27 JST.

## R284 đóng khoảng trống

- Body v2: 95.755 ký tự (net +234 so với R283: +271 đoạn R283 mới −208 gọn R191 + 28 trail + 30 tiêu đề + 5 Ghi-chú "/R283" + 0 range R3–R190→R3–R191 + 108 head line), headroom 9.245 so với 105.000; head line 1.506 ký tự (+108 — head line mới ghi cả ba phiên bản payload R283 + đường đọc public API với băm lại byte-exact); R191 gọn 422 → 214 (gọn đơn thứ hai mươi tư — lưu ý: R191 dài 422 ký tự, không phải 486 như docstring edit script ghi sai); đoạn R283 đúng 270 ký tự (theo checker).
- Checker `check_pr119_restructure_r284_v1.py`: PASS 165/165 (165 = 164 + 1 check row-convention mới cho tuple R282 `("R282", "c2f9283", 3242)`); validation JSON status PASS, failures [].
- Đính chính dòng R282 off-by-one (bài học 78a): hàng R282 trong index ghi `dòng R282 = 3241` (sai — đúng 3242 = số file tại `c2f9283`, content commit R283); hàng R283 ghi đúng `dòng R282 = 3242` + `dòng R283 = 3245` (dự kiến); văn bản lịch sử của hàng R282 giữ nguyên, đính chính ghi ở đây + lesson 53 của checker.
- Build fill + fill sạch (đoạn SHA-hits 143 dòng / 114 entry — 113 sha của R283 + `4002095` cover + `c2f9283` content R283, TRỪ cover R280 retire; extra-token khớp R283, 43 = 43); `daf9540` vẫn 15 lần ngoài đoạn.
- R283 figures re-verified sạch (757/3244/+404927 tại `4002095` = 756/3242/+404197 tại `c2f9283` + 1 commit, 2 files, 730 insertions) NGOẠI TRỪ dòng "main == .bak" của nó (main đã làm tươi hai lần sau push báo cáo ~19:35 JST và ở bước trình ~19:38 JST).

## Kiểm chứng sau commit nội dung

- Content commit `0ad0e59` đã push: `4002095..0ad0e59`, ls-remote xác nhận remote head `0ad0e59`, integration `f3db6b3`.
- Đọc API sau push: head `0ad0e59`, 758/3245/+406353/0, live body R263; issue #116 vẫn 34 comment, ACK `6862732081`.
- Scope audit cumulative tại head: 3245 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`); block R284: 3 path / 0 violation mới.

## Payload R284

- Dựng sau push báo cáo bằng `r284_payload.py` từ body v2 + Head làm tươi tới head báo cáo (đọc API mới sau push báo cáo); .bak + 2 bản sao prepost giữ nguyên bản chuẩn bị; số đo v2 ghi trong nhật ký `~/memory/2026-11-27.md` + tin cuối lượt chạy, và hàng R284 trong index (vòng sau) ghi cả hai phiên bản.
- Payload SẴN SÀNG TRÌNH BÀY (lượt chạy bắt đầu ~19:40 JST, giờ làm việc); CHƯA ĐĂNG — cần thẻ duyệt của chủ dự án. Thẻ sống ~30 phút — bấm khi còn ngồi máy.
- Widget R283 giờ stale, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 95.755 ký tự, headroom 9.245 so với 105.000. Gọn đơn tiếp theo R192 ở R285. Đoạn đầy còn lại R192..R283 = 92 đoạn; khối gọn R2–R191 = 190 dòng.
- Net vòng này +234 khi head line tăng 108; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(77) xem báo cáo các vòng trước. Bài học (78) MỚI VÒNG NÀY (R284):

(a) ĐƯỜNG ĐỌC CONNECTOR GÃY LẠI (lesson 78 regressed): `pull_request_read` / `issue_read` bị từ chối "not in the reviewed read-only set" — giống lỗi đã gặp trước lesson 75a. Dùng public API qua curl (file đọc lưu sẵn, giờ lấy từ mtime file, không ước lượng). Ghi lại đường đọc đã dùng trong báo cáo + head line payload.
(b) DÒNG R282 OFF-BY-ONE (lesson 78a): hàng index R282 ghi `dòng R282 = 3241` nhưng đúng là 3242 (= số file tại `c2f9283`, content commit R283). Quy ước: dòng R_N = số file tại content commit của R_(N+1); vòng R283 đã dùng nhầm số coverage-head (3241). Checker không đọc giá trị dòng từ văn bản hàng nên lỗi lọt. Sửa: hàng R283 ghi đúng `dòng R282 = 3242`; checker R284 thêm tuple `("R282", "c2f9283", 3242)` để khóa quy ước.
(c) LESSON52 DEFECT BỊ TRANSFORM BẮT (lesson 78b): bản nháp LESSON52 trích literal sha content R282 (`b948d93`) + cover nguồn sai (`352c11c` thay vì `cac9c07`) — assert hàng bắt lỗi trước khi ghi. Quy tắc: lesson text trích cover của SOURCE, không trích literal sha content; assert cover dùng cover của source.
(d) PY_STR BACKSLASH (lesson 78c) + SKELETON "ATTEMPTED AGAIN BY" TIẾN HAI VÒNG: `py_str` dùng triple-quote làm literal `\n` thành newline thật — dùng `repr()` khi chuỗi chứa backslash. Skeleton rep: `new_v` giữ literal `\n` (backslash-n), nên replace phải khớp `"\\n"` chứ không phải newline thật. "Attempted again by" trong skeleton tiến HAI vòng (R282 skeleton: filled by r282, attempted by r283; R283 skeleton: filled by r283, attempted by r284) — blanket replace `fill_sha_hits_r28X.py` → r28(X+1) chỉ đúng cho "filled by", phải sửa riêng "attempted again by" sau đó.
(e) PASS-1 HỒI SINH SHA RETIRE (lesson 78d): bản nháp lesson 53 nhắc tên literal của sha retire (cover R280) trong câu claim retire — chính câu đó tạo 1 lần xuất hiện ngoài đoạn, khiến fill pass 1 viết 144 dòng / 115 entry (sha không retire). Pass 2 bỏ tên literal (chỉ nói "the R280 cover sha") → sha về 0 lần, retire thật, fill 143 dòng / 114 entry. Quy tắc: lesson text KHÔNG nhắc tên literal của sha đã retire — nhắc tên sẽ hồi sinh nó (đã ghi ở lesson 77d cho extra-token, nay chứng minh lại cho entry set). Số dòng đoạn fill (143, không phải 141 ước tính) do hai entry mới mang label dài — đo từ đĩa, không ước tính.
