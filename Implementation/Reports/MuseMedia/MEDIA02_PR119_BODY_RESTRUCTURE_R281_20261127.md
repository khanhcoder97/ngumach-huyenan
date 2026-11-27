# MEDIA-02 — PR #119 Body Restructure R281 (2026-11-27)

## Tóm tắt

- Vòng R281: gọn ĐƠN R188 (gọn đơn thứ HAI MƯƠI MỐT); index + body v2 + checker đồng bộ tới head `47057dd` (751 commit / 3235 file / +398438 từ merge-base `cf17178`); merge-tree tại `47057dd` vs integration `f3db6b3` exit 0, tree `5e1079f3…`.
- Vòng này chạy HAI GIAI ĐOẠN: lượt 13:40 JST bắt đầu R281 (fetch ~13:42, đọc PR/issue ~13:40, transform + edit ~14:25, `gen_shift_checker_r281.py` ~14:32) rồi timeout trước khi chạy shift generator; lượt 14:40 JST này tiếp tục bằng tay — tiền lệ R263 (cũng hoàn thiện bằng tay sau hai lượt timeout).
- Không có sự kiện đăng bài giữa các vòng: payload R280 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R280 bị R281 thay thế.
- CẢNH BÁO STALE (ba phiên bản payload R280): bản chính (main) payload R280 ĐÃ ĐƯỢC làm tươi ở bước build sau push báo cáo ~13:08 JST (Head `47057dd`, 95.117 ký tự, sha `8942c0cf`, JSON 106.210 byte, sha256 `13ccc14b`) + làm tươi LẠI lúc trình ~13:13 JST (Head `47057dd`, 95.026 ký tự, sha `c61b69b7`, JSON 106.097 byte, sha256 `7f4abcb7`, head line 1092 ký tự, mergeable true/clean) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (95.101 ký tự, sha `72155d8d`, JSON 106.190 byte, sha256 `a5101733`); cả ba phiên bản đã xác minh lại từ đĩa lượt này (main + `.bak` + 2 bản prepost); hàng R280 trong index ghi cả ba phiên bản.
- Content commit `53d7ff0` (~15:39 JST): 3 file, 1452 insertions, 11 deletions; scope audit block (`47057dd..53d7ff0`) 3 path / 0 violation; cumulative tại `53d7ff0` = 3236 path / 1 violation — artifact `.gitattributes` đã biết.
- Số đếm tại `53d7ff0`: 752 commit / 3236 file / +399879 — khớp API đọc sau push. Additions: 398438 + (1452 − 11) = 399879.
- Merge-tree tại `53d7ff0` vs `f3db6b3`: exit 0, tree `319434b3…`.
- Push: `47057dd..53d7ff0`; ls-remote xác nhận remote head `53d7ff0` VÀ integration `f3db6b3`.
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- Đọc live lượt này KHÔNG qua connector (đường đọc connector gãy giữa vòng — bài học 75a): đọc trước push qua public API (browser) ~15:15 JST, đọc sau push qua browser task 15:40–15:43 JST; hai lần đọc sau push xác nhận head `53d7ff0`, 752/3236/+399879, mergeable true, state unstable ~15:40 → clean ~15:42–15:43 JST (CI chạy xong giữa hai lần đọc).
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (public API qua browser, ~15:15 JST, crawled 06:15 UTC): head `47057dd0a1c1ac407d167426ae0e43a813fc207c`, 751/3235/+398438, mergeable true / state clean, updated_at 2026-11-27T04:07:01Z, live body R263 (Head `daf9540`, 717/3184), tiêu đề kết thúc "+ R263" — khớp đúng bản đọc của lượt 13:40.
- Issue #116 (public API qua browser, ~15:16 JST, crawled 06:16 UTC): đúng 34 comment, mới nhất ACK `6862732081` (2026-11-13T19:24:48Z); không chỉ đạo mới kể từ Gói 39.
- Đọc sau push (browser task, public API, 2 lần, ~15:40 + ~15:42–15:43 JST): head `53d7ff0bd7abbe6063c92421cbd3243fa17162fe`, 752/3236/+399879/0 — khớp git tại content commit; mergeable true; state unstable ở lần đầu, clean ở lần tải lại (giá trị mới nhất clean); live body vẫn R263 (Head `daf9540` 717/3184), tiêu đề kết thúc "+ R263", updated_at 2026-11-27T06:39:40Z (đổi do push R281 cập nhật head, body không đổi). Issue #116 không đọc lại sau push (ghi rõ trong head line của payload).
- GIỚI HẠN ĐỌC LƯỢT NÀY (ghi trung thực): trình duyệt xác minh được head/tiêu đề/số đếm/mergeable/updated_at, nhưng KHÔNG băm lại được độ dài/sha của live body (không có cách chạy mã/băm trên chuỗi ~95 nghìn ký tự trong trang JSON) — nên giá trị 94.825 ký tự / sha `07316552` trong head line của payload R281 được ghi rõ là giá trị R263 đã đọc trực tiếp byte-exact lúc đăng R263 (2026-11-26 ~16:08 JST), không phải hash mới lượt này. Head line payload nói rõ điểm này (bài học 75e).
- GHI CHÚ CỦA TRÌNH DUYỆT (không phải lỗi đọc): đoạn ghi chú nhúng trong live body R263 vẫn mô tả trạng thái TRƯỚC khi đăng R263 (tiêu đề kết thúc "+ R262", live body R262, 94.873 ký tự, sha `891f0c91`, updated_at 2026-11-26T07:06:26Z) — đó là bản ghi thời điểm chuẩn bị payload R263 nhúng trong head line của nó, không phải tuyên bố về trạng thái live hiện tại; trạng thái live đã xác minh độc lập bằng tiêu đề +R263, đoạn mở đầu body và các đoạn R263 trong body. Tương tự, số liệu trong dòng Head của body (717/3184/363157) là số đếm bằng diff từ merge-base `cf17178`, khác số liệu API live (752/3236/399879) — hai cách đếm khác nhau, không phải lỗi đọc.

## Mốc giờ

- Lượt 13:40 JST: fetch ~13:42 JST; đọc live PR/issue ~13:40 JST; transform + edit ~14:25 JST; `gen_shift_checker_r281.py` ~14:32 JST; timeout trước khi chạy shift generator.
- Lượt 14:40 JST (tiếp tục bằng tay): fetch 14:42:14 JST (FETCH_HEAD mtime); lỗi connector 14:43:22/14:43:41 JST; đọc public API ~15:15/~15:16 JST; build fill 15:28:43 JST; gen/shift rebuild 15:37:41/15:37:52 JST; checker PASS 162/162 + validation JSON 15:38:42 JST; content commit `53d7ff0` 15:39:23 JST; push ~15:40 JST; đọc sau push 15:40–15:43 JST; payload R281 build 15:49:06 JST (mtime file); báo cáo này ~15:50 JST.

## R281 đóng khoảng trống

- Body v2: 95.415 ký tự (net +62 so với R280: −272 gọn R188 + 271 đoạn R280 mới + 28 trail + 30 tiêu đề + 5 Ghi-chú "/R281" + 0 range R3–R187→R3–R188 + 0 head line), headroom 9.585 so với 105.000; head line 1.419 ký tự (không đổi); R188 gọn 486 → 214 (gọn đơn thứ hai mươi mốt); đoạn R280 đúng 271 ký tự (theo checker).
- Checker `check_pr119_restructure_r281_v1.py`: PASS 162/162 (162 = 161 + 1 check row-convention mới cho tuple R279) — SAU 2 SỬA OVERRIDE (lần đầu FAIL 159/161, bài học 75c); validation JSON status PASS, failures [].
- Generator sửa 6 lỗi trước khi chạy sạch (bài học 75b); shift checker 62/62 cặp sạch; build fill + fill sạch (đoạn SHA-hits 136 dòng / 110 entry = 108 sha của R280 + `47057dd` cover + `114347b` content R280; extra-token khớp R279/R280, 43 = 43); `daf9540` vẫn 15 lần ngoài đoạn.
- R280 figures re-verified sạch (751/3235/+398438 tại `47057dd` = 750/3233/+397722 tại `114347b` + 1 commit, 2 files, 716 insertions) NGOẠI TRỪ dòng "main == .bak" của nó (main đã làm tươi ở bước build ~13:08 JST + lúc trình ~13:13 JST).

## Kiểm chứng sau commit nội dung

- Content commit `53d7ff0` đã push: `47057dd..53d7ff0`, ls-remote xác nhận remote head `53d7ff0`, integration `f3db6b3`.
- Hai lần đọc API sau push đều: head `53d7ff0`, 752/3236/+399879, live body R263.
- Scope audit block (`47057dd..53d7ff0`): 3 path / 0 violation. Cumulative tại head: 3236 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`).

## Payload R281

- Dựng sau push bằng `r281_payload.py` từ body v2 + Head làm tươi tới `53d7ff0` (đã sửa 2 điểm trước khi build: điền POSTPUSH từ handoff trình duyệt + sửa câu chữ head line cho trung thực về body hash — bài học 75e; sửa bug env ls-remote — bài học 75d).
- Body payload: 95.432 ký tự, sha `4f47ec8c`; JSON 106.597 byte (headroom 24.475 byte so với trần 131.072); tiêu đề 765 ký tự, kết thúc "+ R281"; head line 1.436 ký tự (1.419 → 1.436, +17); main == .bak == 2 bản sao prepost, sha256 `40c883cb`.
- ĐÍNH CHÍNH HEAD (bài học 72): payload chuẩn bị trên ghi head nội dung `53d7ff0` — sau khi commit báo cáo này + push, main sẽ được làm tươi sang head báo cáo (đọc API mới sau push báo cáo); .bak + 2 bản sao prepost giữ nguyên bản chuẩn bị; số đo v2 ghi trong nhật ký `~/memory/2026-11-27.md` + tin cuối lượt chạy, và hàng R281 trong index (vòng sau) ghi cả hai phiên bản.
- Payload SẴN SÀNG TRÌNH BÀY (lượt chạy bắt đầu ~14:40 JST, giờ làm việc); CHƯA ĐĂNG — cần thẻ duyệt của chủ dự án. Thẻ sống ~30 phút — bấm khi còn ngồi máy.
- Widget R280 giờ stale, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 95.415 ký tự, headroom 9.585 so với 105.000. Gọn đơn tiếp theo R189 ở R282. Đoạn đầy còn lại R189..R280 = 92 đoạn; khối gọn R2–R188 = 187 dòng.
- Net vòng này +62 khi head line không đổi; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(74) xem báo cáo các vòng trước. Bài học (75) MỚI VÒNG NÀY (R281):

(a) ĐƯỜNG ĐỌC CONNECTOR GÃY GIỮA VÒNG: `call-read-tool` cho `pull_request_read` / `issue_read` giờ lỗi "GitHub MCP tool `pull_request_read` is not in Muse's reviewed read-only set; use `call-tool` so it receives write-capable approval" (file `.err` mtime 14:43:22/14:43:41 JST); `call-tool` cho đọc PR kẹt ở thẻ duyệt — session biến mất, không output; thẻ duyệt còn treo (approval_id `connector-attempt-b080cd14e83a7f99a1bb8192a300501a43ae4e1eeb19df8580550f9d972bf236`, yêu cầu 2026-11-27T05:43:41Z = 14:43:41 JST, còn pending lúc kiểm ~15:42 JST) — không cần nữa, trạng thái live đã xác minh qua public API; KHÔNG thử lại call-tool. Bài học (73) (`pullNumber` camelCase) giờ stale đối với đường đọc. Đọc live vòng này dùng public GitHub API qua trình duyệt; builder/refresh payload assert trên git + ls-remote + giá trị đọc live đã ghi, thay vì file JSON connector.
(b) GENERATOR SỬA 6 LỖI TRƯỚC KHI CHẠY SẠCH: (1) assert PAIRS = 4 (checker R280 có khối PAIRS thứ 4 COVER/CHECKER_NAME/checks), không phải 3; (2) PAIRS là 3-tuple `(old, new, 1)`, không phải 2-tuple — vòng lặp giữ nguyên count, node `append` xử lý bằng `ast.literal_eval(list_node)`; (3) skeleton dùng `ROOT /`, không phải `BASE /`; (4) assert file refs R280 = 4 (SRC + cặp CHECKER_NAME + validator out-dict + danh sách stale `for bad in (...)`); (5) skeleton sau cặp PAIRS vẫn ghi R279 ở dòng `compact_ok` / `r279_note_ok` — generator lượt trước không shift phần này, đã thêm rep shift sang R280→R281; (6) override `_ghichu_chk_name` thiếu range R3–R187→R3–R188. Sau sửa: shift 62/62 cặp OK, compact_ok shift OK, r280_note_ok shift OK, stale sweep OK.
(c) CHECKER LẦN ĐẦU FAIL 159/161 — HAI BUG QUY ƯỚC HÀNG TỪ SHIFT GENERIC: (i) cặp block hàng R279: comment ghi base `3229` (đúng `3232` tại `d2eb9b5`), check ghi cumulative `3235` (đúng `3233`); block hàng R280 cùng cặp ghi nhầm comment/tên là 3235 (đúng 3236; check 3236 đã đúng). (ii) cặp tuple-list: shift generic làm rơi tuple R276, đẩy nhãn/sha lên trước nhưng giữ cumulative cũ — tuple R278 ghi 3227 so với diff thật 3230 tại `3d51a26`, tổng check 161 không phải 162. Sửa bằng hai override mới ở đầu OVERRIDES trong `gen_shift_checker_r281.py`: `_row_blocks_279_280` (text R281 viết tay, assert với cặp R280) và `_tuple_list_append` (append verbatim `("R279", "114347b", 3233)`, indent suy từ file). Chạy lại gen → shift → fill → checker: PASS 162/162.
(d) FILL NHÃN SỬA: `build_fill_r281.py` sửa LABEL_PATTERNS theo đúng dòng docstring của checker R281 (đã grep xác minh); hai pattern stale trong fill_r280 được sửa: 'The R279 payload should' không bao giờ khớp checker R280 (dòng đó ghi R280); dòng đoạn trích dẫn vòng lùi hai (R280 trích R278, R281 trích R280). `daf9540` vẫn 15 lần ngoài đoạn (bài học 33 ×1 + bài học 35–41 ×2 mỗi bài; bài học 42–50 nhắc tới 0 lần — đã đo).
(e) BUG ENV LS-REMOTE TRONG BUILDER PAYLOAD: `r281_payload.py` truyền `env` trần (chỉ GIT_SSH_COMMAND + PATH) cho `ls-remote`, làm mất `https_proxy` nên SSH ProxyCommand (`proxy_connect.py`) gãy ("no https_proxy in env / Connection closed by UNKNOWN port 65535"). Sửa: kế thừa `os.environ` rồi override (ghi chú trong code). Payload build sau đó chạy sạch, ls-remote xác nhận remote head + integration.
(f) GIỚI HẠN BĂM BODY CỦA TRÌNH DUYỆT + GHI CHÚ NHÚNG: đọc post-push qua trình duyệt không băm lại được live body (~95 nghìn ký tự) — head line payload R281 ghi rõ 94.825 ký tự / sha `07316552` là giá trị R263 đọc byte-exact lúc đăng R263, không phải hash mới lượt này; ghi chú R262 còn nhúng trong live body R263 là bản ghi thời điểm chuẩn bị payload, không phải tuyên bố live — xem mục "Đọc live". Cùng mẫu này, head line mỗi vòng ghi lại trạng thái live lúc chuẩn bị payload; khi trình bày widget cần nói rõ điểm này nếu chủ dự án hỏi.
