# MEDIA-02 — PR #119 Body Restructure R288 (2026-11-28)

## Tóm tắt

- Vòng R288: gọn ĐƠN R195 (gọn đơn thứ HAI MƯƠI TÁM); index + body v2 + checker đồng bộ tới head `07e13a0` (765 commit / 3256 file / +413611 từ merge-base `cf17178`); merge-tree tại `07e13a0` vs integration `f3db6b3` exit 0, tree `7dc887db…`.
- Vòng này là lượt định kỳ 03:40 JST 2026-11-28: fetch lần đầu lỗi (kex_exchange_identification reset qua proxy) rồi retry thành công; đọc live PR rate-limited (HTTP 403 hai lần) nên head line + index ghi rõ giá trị live là lần xác minh ~03:07 JST; áp edit (body v2 96.573 ký tự, changed 18, idempotent 0); transform cần 1 sửa (PREV7); builder checker chạy sạch lần đầu; fill lần đầu báo `8cb82a1` retire (bài học 82b) → thêm anchor cover-excision → fill chạy lại sạch (150 dòng / 121 entry); checker FAIL 168/169 hai lần (note-date R287 — bài học 82a; rồi validation JSON trong repo — bài học 82c) rồi PASS 169/169 sau khi sửa builder + chạy --out ra ngoài repo; content commit `5fdc769`. Không có sự kiện đăng bài giữa các vòng: payload R287 KHÔNG ĐƯỢC ĐĂNG, live body vẫn là R263 (94.825 ký tự, sha `07316552`); payload R287 bị R288 thay thế.
- CẢNH BÁO STALE (hai phiên bản payload R287): bản chính (main) payload R287 đã làm tươi sau push báo cáo (Head `07e13a0`, 96.053 ký tự, sha `fea1baea`, JSON 107.270 byte, sha256 `57c2020f`, head line 1348, mergeable true/unstable) — `.bak` + 2 bản sao prepost giữ nguyên bản như đã chuẩn bị (96.029 ký tự, sha `f1e7ea71`, JSON 107.240 byte, sha256 `53ccda3c`, head line 1324, Head `9383178`); cả hai phiên bản đã xác minh lại từ đĩa lượt 03:40; main != .bak. Title 765 ký tự kết "+ R287".
- Content commit `5fdc769` (~04:10 JST): 3 file, 1446 insertions, 11 deletions; scope audit cumulative 3257 path / 1 violation — artifact `.gitattributes` đã biết (block 3 path / 0 violation mới).
- Số đếm tại `5fdc769`: 766 commit / 3257 file / +415046 — số đếm git, KHỚP ĐÚNG số API sau push (xem dưới). Additions: 413611 + (1446 − 11) = 415046.
- Merge-tree tại `5fdc769` vs `f3db6b3`: exit 0, tree `6e9aac04…`.
- Push: `07e13a0..5fdc769`; ls-remote xác nhận remote head `5fdc769` VÀ integration `f3db6b3` (~04:10 JST).
- Working tree sau content commit: sạch trừ báo cáo + validation JSON (commit báo cáo này).
- SyntaxWarning `invalid escape sequence '\`'` vẫn còn — có từ R265, chỉ thẩm mỹ.

## Đọc live

- PR #119 (public API qua curl, bản đọc lượt này ~03:40 JST: PR trả HTTP 403 rate-limited hai lần, KHÔNG đọc mới được; issue HTTP 200): giá trị live trong head line + index là lần xác minh cuối ~03:07 JST (sau push báo cáo R287, file `hidden_files/pr119_read_r287_after_report.json`): head `07e13a0`, API 765 commit / 3256 file / +413611 / 0, mergeable true/unstable, updated_at 2026-11-27T17:58:49Z, live body R263 băm lại byte-exact (94.825 ký tự, sha `07316552`, 0 U+FFFD); head xác minh không đổi qua fetch (local head = remote head = `07e13a0`, integration `f3db6b3`).
- Issue #116 (public API qua curl, bản đọc ~03:40 JST + đọc lại sau push, file `hidden_files/issue116_read_r288_0340.json` + `issue116_read_r288_after_content.json`): đúng 34 comment, mới nhất ACK `6862732081` (2026-11-13); không chỉ đạo mới kể từ Gói 39.
- PR read xác minh lại lượt này `base.sha f3832338` LÀ ancestor của integration `f3db6b3` (20 commit sau — merge PR #118 ngày 2026-11-05); merge-tree vẫn chạy trên `f3db6b3` live như mọi vòng.
- Đọc sau push nội dung (public API qua curl, ~04:10 JST, HTTP 200 cả hai, file `hidden_files/pr119_read_r288_after_content.json` + `issue116_read_r288_after_content.json`): PR head `5fdc769`, API 766/3257/+415046/0 — KHỚP ĐÚNG số git tại content commit; mergeable true/unstable (CI đang chạy trên head mới — lần clean gần nhất tại `75eedfc`), updated_at 2026-11-27T19:10:01Z; live body vẫn R263 (94.825 ký tự, sha `07316552` — push không đổi body). Issue #116 đọc lại sau push: vẫn 34 comment, mới nhất 6862732081.

## Mốc giờ

- ~03:40 JST 2026-11-28: lượt định kỳ bắt đầu R288 — fetch lần đầu reset, retry thành công; đọc live (PR 403 ×2, issue 200, 34 comment).
- ~03:50–04:00 JST: transform (1 sửa PREV7) + edit (changed 18, idempotent 0) + gen_pairs (62 cặp, chạy sạch lần đầu) + builder checker chạy sạch lần đầu + fill lần đầu báo `8cb82a1` retire (bài học 82b) → thêm anchor cover-excision vào lesson (54) → builder + fill chạy lại sạch (150 dòng / 121 entry).
- ~04:00–04:08 JST: checker FAIL 168/169 lần đầu (note-date R287 — bài học 82a) → sửa builder + sửa 4 chỗ LESSON56 (từ "NO fixes" sang "ONE fix") → builder + fill chạy lại → checker FAIL 168/169 lần hai (validation JSON trong repo — bài học 82c) → xóa JSON khỏi repo, chạy checker với --out ra goal hidden_files → checker PASS 169/169.
- ~04:09 JST: scope audit + merge-tree; content commit `5fdc769`; push ~04:10 JST; đọc sau push; báo cáo này ~04:11 JST.

## R288 đóng khoảng trống

- Body v2: 96.573 ký tự (net +339 so với R287: +271 đoạn R287 mới −182 gọn R195 + 28 trail + 30 tiêu đề + 5 Ghi-chú "/R287" + 0 range R3–R194→R3–R195 + 187 head line), headroom 8.427 so với 105.000; head line 1.716 ký tự (+187 — đo từ đĩa, tăng do ghi rõ đường đọc rate-limited); R195 gọn 396 → 214 (gọn đơn thứ hai mươi tám); đoạn R287 đúng 270 ký tự (theo checker).
- Checker `check_pr119_restructure_r288_v1.py`: PASS 169/169 (168 + 1 check row-convention mới cho tuple R286 `("R286", "9383178", 3254)`); validation JSON status PASS, failures [].
- ĐÍNH CHÍNH nhỏ từ báo cáo R287 (lesson 82): nhãn giờ "~03:05/~03:06/~03:07 JST" của báo cáo R287 chạy trước ~10 phút so với timestamp commit git (content 02:55:58 JST, report 02:58:23 JST) — chỉ nhãn giờ, trình tự push + số liệu chính xác như đã viết.
- Build fill + fill: lần đầu báo `8cb82a1` 0 lần ngoài đoạn (bài học 82b — LESSON56 nháp thiếu anchor cover-excision) → thêm anchor vào lesson (54) → fill chạy lại sạch (đoạn SHA-hits 150 dòng / 121 entry — 119 sha của R287 + `07e13a0` cover + `9383178` content R287, KHÔNG retire sha nào; extra-token khớp R287, 43 = 43; chạy lại idempotent); `daf9540` vẫn 15 lần ngoài đoạn; `8cb82a1` giữ 1 lần (anchor cover-excision lesson 54); không sha nào retire vòng này.
- Số đếm API sau push khớp đúng số git (766/3257/+415046/0 tại `5fdc769` cả hai nguồn).

## Kiểm chứng sau commit nội dung

- Content commit `5fdc769` đã push: `07e13a0..5fdc769`, ls-remote xác nhận remote head `5fdc769`, integration `f3db6b3`.
- Đọc API sau push (~04:10 JST, HTTP 200): PR head `5fdc769`; số API 766/3257/+415046/0 khớp đúng số git tại `5fdc769`; mergeable true/unstable (CI đang chạy); live body vẫn R263. Issue #116 đọc lại sau push: vẫn 34 comment, ACK `6862732081`.
- Scope audit cumulative tại head: 3257 path / 1 violation (`.gitattributes` — artifact merge-base, byte-identical với integration `f3db6b3`, sha256 `23352e4c…`; khác merge-base `cf17178` sha256 `54ee7996…`); block R288: 3 path / 0 violation mới.

## Payload R288

- Dựng sau push báo cáo bằng `make_r288_payload.py` (adapt từ `make_r287_payload.py`) từ body v2 + Head làm tươi tới head báo cáo (đọc API mới sau push báo cáo); .bak + 2 bản sao prepost giữ nguyên bản chuẩn bị; số đo v2 ghi trong nhật ký `~/memory/2026-11-28.md` + tin cuối lượt chạy, và hàng R288 trong index (vòng sau) ghi cả hai phiên bản.
- Payload SẴN SÀNG TRÌNH BÀY (đã qua 01:30 JST — luồng chính trình vào sáng mai theo lệnh); CHƯA ĐĂNG — cần thẻ duyệt của chủ dự án. Thẻ sống ~30 phút — bấm khi còn ngồi máy.
- Widget R287 giờ stale, KHÔNG bấm.

## Cảnh báo headroom

- Body v2 96.573 ký tự, headroom 8.427 so với 105.000. Gọn đơn tiếp theo R196 ở R289. Đoạn đầy còn lại R196..R287 = 92 đoạn; khối gọn R2–R195 = 194 dòng.
- Net vòng này +339 khi head line tăng 187; độ dài head line không ổn định — đo từ đĩa mỗi vòng, không suy từ vòng trước.

## Bài học

Các bài học (1)–(81) xem báo cáo các vòng trước. Bài học (82) + (82a) MỚI VÒNG NÀY (R288):

(a) TRANSFORM R288 MANG MỘT LỖI, BỊ ASSERTION BẮT TRƯỚC KHI GHI (lesson 82): PREV7 mang sha nội dung R287 (`9383178`) thay vì head bao phủ trước (`75eedfc`) — edit script fail ở sub_once `(head \`9383178\`)` trước khi ghi gì; sửa trong transform, chạy lại sạch (derived R287_ROW, edit changed: 18, idempotency 0). Quy tắc: PREV7 luôn là COVER7 của vòng trước, không phải content sha — kiểm tra bằng mắt trước khi chạy transform.
(b) ĐỌC LIVE RATE-LIMITED (lesson 82): PR API trả HTTP 403 hai lần lượt này (~03:40 JST) — không đọc mới được head/counts/mergeable/live body; các giá trị live trong head line + index ghi rõ là "lần xác minh ~03:07 JST" (after-report R287), không giả vờ đọc mới. Sau push nội dung, API đọc lại được (HTTP 200) và số API khớp git đúng (766/3257/+415046/0) — rate limit là tạm thời theo IP, thử lại sau push thay vì kết luận PR không đọc được.
(c) ĐÍNH CHÍNH NHỎ (lesson 82): nhãn giờ của báo cáo R287 chạy trước ~10 phút so với timestamp commit git — chỉ nhãn giờ, không ảnh hưởng số liệu hay trình tự push; các vòng sau ghi giờ theo timestamp git khi có thể.
(d) LỖI NOTE-DATE TRONG BUILDER CHECKER — LẦN ĐẦU Ở CHUỖI CHECKER (lesson 82a, cùng lớp với lesson 81 của transform): shift generic mang ngày 2026-11-27 của note R286 sang guard note R287, nhưng note R287 ghi ngày 2026-11-28 — checker FAIL 168/169 ở check R196-defect repairs, bắt đúng lỗi; sửa bằng skeleton rep có assert count trong builder + sửa 4 chỗ LESSON56 (từ "NO fixes" sang "ONE fix", theo bài học 81b — không để văn bản checker mang lời sai về chính chuỗi của nó), chạy lại builder + fill, checker PASS 169/169. Quy tắc: ngày trong guard note KHÔNG nằm trong shift map — mỗi vòng kiểm tra ngày note mới từ index trước khi build checker; và khi builder cần sửa, sửa luôn LESSON56 trong builder trước khi build lại.
(e) FILL BẮT ĐÚNG LỖI RETIREMENT (lesson 82b): lần fill đầu báo `8cb82a1` 0 lần ngoài đoạn — LESSON56 nháp thiếu anchor cover-excision cho source cover (R287 (49) có câu đó, R288 (54) nháp thiếu); thêm anchor vào lesson (54), build lại + fill lại, `8cb82a1` giữ 1 lần, entry set đủ 121, không retire sha nào. Quy tắc: lesson (54) mỗi vòng phải nêu tên source cover trong câu cover-excision — đó là neo giữ sha đó sống.
(f) VALIDATION JSON KHÔNG NẰM TRONG REPO KHI CHẠY CHECKER (lesson 82c): checker lần đầu FAIL 168/169 ở check "git status shows only index + body + this checker" vì file validation JSON đã ghi vào repo trước — xóa JSON khỏi repo, chạy checker với --out ra goal hidden_files (`check_r288_validation.json`), PASS 169/169, rồi copy JSON vào repo ở bước báo cáo. Quy tắc: --out của checker luôn ra ngoài repo; file validation chỉ vào repo cùng commit báo cáo.
