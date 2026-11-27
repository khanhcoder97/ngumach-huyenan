# MEDIA-02 — PR #119 Body Restructure R290 (2026-11-28)

## Tóm tắt

- Vòng R290: gọn ĐƠN R197 (gọn đơn thứ BA MƯƠI); index + body v2 + checker đồng bộ tới head `592b4f1` (769 commit / 3262 file / +417991 từ merge-base `cf17178`); merge-tree tại `93ac0f0` vs integration `f3db6b3` exit 0, tree `e8875338…`.
- **PR #119 ĐÃ MERGED (06:54:45 JST, merge commit `a9a4677`) — phát hiện sau push nội dung qua ls-remote + đọc API tươi (HTTP 200).** Content commit R290 `93ac0f0` nằm trên nhánh media SAU merge, KHÔNG nằm trong integration; live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R290 CHUẨN BỊ XONG nhưng GIỮ LẠI (HOLD) — KHÔNG TRÌNH / KHÔNG BẤM cho tới khi chủ dự án quyết bước tiếp theo (PR mới cho các commit sau merge? tiếp tục vòng? dừng?).
- Vòng này là lượt định kỳ 06:40 JST 2026-11-28: fetch thành công lần đầu; đọc live 06:40 RATE-LIMITED (HTTP 403 cả hai, public API); transform chạy sạch lần đầu; gen_pairs chạy sạch lần đầu; build_checker cần 3 sửa (bài học 86b) rồi chạy sạch; fill lỗi lần đầu (`75eedfc` 0 lần ngoài đoạn — bài học 86c) rồi chạy sạch ở lần retry (156 dòng / 125 entry, chạy lại idempotent); checker PASS 171/171 ngay lần đầu sau fill. Không có sự kiện đăng bài giữa các vòng: payload R289 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263; payload R289 bị R290 thay thế (nhưng R290 cũng HOLD vì PR đã merged).
- CẢNH BÁO STALE (hai phiên bản payload R289): bản chính (main) payload R289 đã làm tươi sau push báo cáo (Head `592b4f1`, 96.405 ký tự, sha `60360723`, JSON 107.671 byte, sha256 `ff840254`, head line 1396, mergeable true/unstable) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (96.333 ký tự, sha `2f965022`, JSON 107.586 byte, sha256 `e2d9ec9a`, head line 1324, Head `e3b1a28`); cả hai phiên bản đã xác minh lại từ đĩa lượt 06:40; main != .bak. Title 765 ký tự kết "+ R289".
- Content commit `93ac0f0` (~07:17 JST): 3 file, 1456 insertions, 11 deletions; scope audit cumulative 3263 path / 1 violation — artifact `.gitattributes` đã biết (block 3 path / 0 violation mới).
- Số đếm tại `93ac0f0`: 770 commit / 3263 file / +419436 — số đếm git. Additions: 417991 + (1456 − 11) = 419436.
- Merge-tree tại `93ac0f0` vs `f3db6b3` (integration tip lúc bắt đầu vòng): exit 0, tree `e8875338…`.
- Push: `592b4f1..93ac0f0`; ls-remote xác nhận remote head `93ac0f0` VÀ integration đã thành `a9a4677` (merge PR #119).
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (public API qua curl, bản đọc lượt này ~06:40 JST, HTTP 403 cả hai lần thử): KHÔNG đọc được head/counts/mergeable/live-body mới; các giá trị trích là lần xác minh cuối (đọc sau báo cáo ~06:14 JST: head `592b4f1`, 769/3262/+417991, mergeable true/unstable, live body R263 sha `07316552`, updated_at 2026-11-27T21:14:26Z).
- Issue #116 (connector `issue_read`, ~06:40 JST, thành công): đúng 34 comment, mới nhất ACK `6862732081` (2026-11-13); không chỉ đạo mới kể từ Gói 39.
- PR read xác minh lại lượt này `base.sha f3832338` LÀ ancestor của integration `f3db6b3` (20 commit sau — merge PR #118 ngày 2026-11-05); merge-tree chạy trên `f3db6b3` như mọi vòng.
- Đọc sau push nội dung (public API qua curl, ~07:23 JST, HTTP 200 cả hai, file `hidden_files/pr119_read_r290_after_content.json` + `issue116_read_r290_after_content.json`): **PR #119 state closed, merged true, merged_at 2026-11-27T21:54:45Z (= 06:54:45 JST), merge_commit_sha `a9a46770c01df7802a816bd9d9b7f4f3ec92d0b7`; head `592b4f1`, API 769/3262/+417991/0 — KHỚP ĐÚNG số git tại `592b4f1`; mergeable null / mergeable_state unknown (PR đã merged); tiêu đề kết thúc "+ R263"; live body vẫn R263 (94.825 ký tự, sha `07316552`, 0 U+FFFD); updated_at 2026-11-27T21:54:45Z (= merged_at).** Issue #116 đọc lại sau push: vẫn 34 comment, mới nhất 6862732081 — không có comment mới về merge.

## Mốc giờ

- ~06:40 JST 2026-11-28: lượt định kỳ bắt đầu R290 — fetch thành công lần đầu; đọc live PR 403 (rate-limited), issue #116 qua connector thành công (34 comment).
- ~06:47–07:15 JST: transform (chạy sạch lần đầu) + edit (changed 18, idempotent 0) + gen_pairs (62 cặp, chạy sạch lần đầu) + build_fill (chạy sạch) + build_checker (3 sửa, bài học 86b) + fill (lỗi lần đầu `75eedfc`, bài học 86c; chạy sạch ở retry, 156 dòng / 125 entry, idempotent) + checker PASS 171/171.
- ~06:54:45 JST: PR #119 được merged (merge commit `a9a4677`) — diễn ra GIỮA vòng, khi vòng đang build; vòng chỉ phát hiện sau push nội dung.
- ~07:17 JST: scope audit + merge-tree; content commit `93ac0f0`; push ~07:17 JST; ls-remote phát hiện integration thành `a9a4677`; đọc API tươi xác nhận merged; báo cáo này ~07:25 JST.

## R290 đóng khoảng trống

- Body v2: 96.882 ký tự (net +373 so với R289: +271 đoạn R289 mới −182 gọn R197 + 28 trail + 30 tiêu đề + 5 Ghi-chú "/R289" + 0 range R3–R196→R3–R197 + 221 head line), headroom 8.118 so với 105.000; head line 1.721 ký tự (+221 — đo từ đĩa, tăng do ghi chú rate-limit + merge); R197 gọn 396 → 214 (gọn đơn thứ ba mươi); đoạn R289 đúng 270 ký tự (theo checker).
- Checker `check_pr119_restructure_r290_v1.py`: PASS 171/171 (170 + 1 check row-convention mới cho tuple R288 `("R288", "e3b1a28", 3260)`); validation JSON status PASS, failures [].
- Build checker + fill: transform chạy sạch lần đầu (derived R289_ROW, edit changed 18, idempotency 0); gen_pairs chạy sạch lần đầu (62 cặp); build_checker cần 3 sửa trước khi chạy sạch — (1) assert kết cặp R253/R254/ ghi `/R288` trong khi text R289 kết `/R287`; (2) sáu special-case condition ghi text R290 thay vì text R289 (nguồn); (3) hai return ghi dòng/đoạn R290 thay vì R289 (dòng R289 cites 3263; đoạn R289 96.333 ký tự sha 2f965022) — bài học 86b. Fill lỗi lần đầu: entry sha `75eedfc` 0 lần ngoài đoạn (bài học 86c) — lesson (54)–(60) viết tay đã bỏ cả ba lần nhắc R289; sửa bằng một lần nhắc `75eedfc` trong lesson (54); fill chạy sạch ở retry (156 dòng / 125 entry — 123 sha của R289 + `592b4f1` cover + `e3b1a28` content R289, KHÔNG retire sha nào; extra-token khớp R289, 43 = 43; chạy lại idempotent); `daf9540` vẫn 15 lần ngoài đoạn; `8cb82a1` giữ 1 lần (anchor lesson (54)); không sha nào retire vòng này. Số dòng đoạn SHA-hits là 156, đúng như lesson dự đoán (153 + 3 dòng mới).
- Số đếm API sau push khớp đúng số git (769/3262/+417991/0 tại `592b4f1` cả hai nguồn — API đọc head PR, là head lúc merge).

## Kiểm chứng sau commit nội dung

- Content commit `93ac0f0` đã push: `592b4f1..93ac0f0`, ls-remote xác nhận remote head `93ac0f0`; integration `a9a4677` (merge PR #119).
- Đọc API sau push (~07:23 JST, HTTP 200): PR closed/merged (merged_at 2026-11-27T21:54:45Z, merge commit `a9a4677`); số API 769/3262/+417991/0 khớp đúng số git tại `592b4f1`; mergeable null/unknown; live body vẫn R263. Issue #116 đọc lại sau push: vẫn 34 comment, ACK `6862732081`.
- Scope audit cumulative tại head: 3263 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`, sha256 `23352e4c…`; khác merge-base `cf17178` sha256 `54ee7996…`); block R290: 3 path / 0 violation mới.
- Merge-tree tại `93ac0f0` vs `f3db6b3` (tip integration lúc bắt đầu vòng): exit 0, tree `e8875338…`. KHÔNG chạy merge-tree với tip mới `a9a4677` — merge phát hiện sau khi đo; vòng sau kiểm tra lại trước khi trích merge-tree mới.

## Payload R290

- Dựng sau push báo cáo bằng `make_r290_payload.py` (adapt từ `make_r289_payload.py`) từ body v2 + Head làm tươi tới head báo cáo (đọc API tươi sau push báo cáo — PR đã merged nên Head ghi mergeable null/unknown + merge `a9a4677`); .bak + 2 bản sao prepost giữ nguyên bản chuẩn bị; số đo v2 ghi trong nhật ký `~/memory/2026-11-28.md` + tin cuối lượt chạy, và hàng R290 trong index (vòng sau) ghi cả hai phiên bản.
- Payload R290 GIỮ LẠI (HOLD) — CHƯA ĐĂNG và KHÔNG TRÌNH BÀY ĐỂ BẤM: PR #119 đã merged (closed) lúc 06:54:45 JST; cập nhật body của PR đã merged không còn phục vụ review. Cần quyết định của chủ dự án/Codex trước khi làm gì với payload này (mở PR mới cho các commit sau merge, hay dừng vòng body-restructure). Thẻ duyệt ~30 phút không còn ý nghĩa cho vòng này.
- Widget R289 giờ stale, KHÔNG bấm. Widget R290 cũng HOLD, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 96.882 ký tự, headroom 8.118 so với 105.000. Gọn đơn tiếp theo R198 ở R291 — NHƯNG tiền đề vòng đã đổi (PR #119 merged): R291 không nên tự động dựng thêm một payload body-update nữa; vòng sau kiểm tra trước xem chủ dự án/Codex có mở PR mới hay có chỉ đạo mới không, rồi mới quyết khối tiếp theo. Đoạn đầy còn lại R198..R289 = 92 đoạn; khối gọn R2–R197 = 196 dòng.
- Net vòng này +373 khi head line tăng 221; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(85) xem báo cáo các vòng trước. Bài học (86) + (86a)–(86e) MỚI VÒNG NÀY (R290):

(a) NOTE-DATE GUARD VẪN GIỮ (lesson 86a): cả hai note R288/R289 đều ngày 2026-11-28 nên không phát sinh ngày cũ; special case note-date trong transform_pair của build_checker giữ nguyên làm guard (giống lesson 84b). Quy tắc: ngày trong guard note KHÔNG nằm trong shift map — mỗi vòng kiểm tra ngày note mới từ index trước khi build checker.
(b) BUILDER CẦN BA SỬA TRƯỚC KHI CHẠY SẠCH (lesson 86b): (1) special case cặp R253/R254/ assert text kết `/R288` trong khi text R289 (nguồn) kết `/R287`; (2) sáu special-case condition ghi text ĐÍCH (R290) thay vì text NGUỒN (R289) — các condition phải khớp phía new của pairs (text R289); (3) hai return ghi dòng/đoạn R290 thay vì R289 (dòng R289 cites 3263; đoạn R289 96.333 ký tự sha 2f965022). Quy tắc: special case trong builder luôn viết theo text NGUỒN (vòng trước), kiểm tra phía new của pair trước khi ghi condition/return — lỗi này lặp lại lớp của lesson 84b (viết từ prose kỳ vọng thay vì text thực tế).
(c) ENTRY SHA MẤT ANCHOR KHI LESSON VIẾT TAY BỎ HẾT LẦN NHẮC (lesson 86c): fill assert mọi entry sha xuất hiện ≥1 lần ngoài đoạn; `75eedfc` về 0 lần vì lesson (54)–(60) viết tay cho R290 đã bỏ cả ba lần nhắc của R289 (LESSON58 block + lesson 54/59) mà không nhắc lại ở đâu; sửa bằng một lần nhắc `75eedfc` trong lesson (54) (nêu rõ nó là PREV7 cũ, tiền lệ cho assert history-reference của transform). Quy tắc: khi viết tay lesson mới, kiểm tra mọi entry sha còn ≥1 anchor ngoài đoạn — sha chỉ xuất hiện trong các lesson block bị thay thế sẽ mất anchor; neo lại trong lesson hoặc retire khỏi entry set một cách có chủ đích.
(d) PR MERGED GIỮA VÒNG — ĐÓNG BĂNG PAYLOAD, GHI RÕ TRONG BÁO CÁO (lesson 86d): PR #119 merged lúc 06:54:45 JST trong khi vòng R290 đang build; vòng chỉ phát hiện sau push nội dung qua ls-remote + đọc API tươi. Quy tắc: tiền đề "PR đang mở / mergeable" có thể đổi giữa vòng — đọc API tươi sau push nội dung là điểm bắt buộc để xác nhận; khi PR đã merged, payload chuyển sang HOLD (không trình, không bấm) và báo cáo + tin cuối phải nêu rõ, không dựng vòng tiếp theo theo quán tính.
(e) REPORT COMMIT THÊM 2 FILE, KHÔNG PHẢI 4 (lesson 86e): đo bằng git — report commit R288 (`6b035ad`) và R289 (`592b4f1`) mỗi cái thêm đúng 2 file (report MD + validation JSON), 751/754 insertions. Quy tắc: số file của report commit đo từ `git show --numstat` mỗi vòng; hàng index R291 cites cumulative = files tại head báo cáo R290 + 1 checker mới — kiểm chứng từ đĩa, không mang số "4 file" từ memory.
