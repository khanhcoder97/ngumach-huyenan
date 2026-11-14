# MEDIA-02 CHECKPOINT 14 — Gói 30 fix (a): dialogueCues sai bằng 0 (2026-11-05)

## Khối vừa hoàn thiện

Sửa finding 1 của review PR #119 (Gói 30 item 1): runtime manifest báo
`dialogueCues = 0` cho CIN_001/002/004/006 dù mỗi SRT có 1 cue. Nguyên nhân
gốc: `build_runtime_delivery.py` lấy `len(s.get("cues", []))` từ ba manifest
nguồn có hình dạng khác nhau — manifest P0 và CIN_006 không có key `"cues"`.
Sửa: builder suy số cue từ timing JSON đã parse (`shots[].dialogue`) và
đối chiếu với số cue SRT đã parse, cộng với `"cues"` của manifest nguồn khi
có; lệch nhau thì build FAIL (exit 1). Validator thêm bước kiểm chéo
`check_runtime_cine_manifest()` đối chiếu cả bốn lớp: runtime manifest ==
timing == SRT == manifest nguồn (khi có key `"cues"`).

## Trạng thái GitHub (đọc qua public API + connector read-only, 2026-11-05 19:40 JST)

- Issue #116: vẫn OPEN, nay 8 comment. MỚI: comment `6655412688`
  (2026-11-05 10:15:43Z, khanhcoder97) — **Gói 30**: sửa nghiệm thu, khép
  tutorial, tiếp MMORPG; Muse M1–M8 sửa gói bàn giao + sản xuất media còn
  thiếu. Đây là chỉ đạo mới nhất, lượt này áp dụng.
- PR #119: OPEN, head `7891265`, base `f383233`, mergeable clean,
  19 commit, 699 file. MỚI: review comment `6655312858`
  (2026-11-05 10:10:45Z, khanhcoder97) — **HOLD toàn PR** ở head
  `3f34f0d` (691 path); timing/reel storyboard/TTS nháp chỉ là checkpoint,
  chưa hoàn M1–M8. 5 findings (xem dưới).
- Integration HEAD không đổi: `f383233` (không có merge mới kể từ
  checkpoint 12).
- Lưu ý: đường dẫn review `Implementation/Reports/Review_20261105/Muse_PR119.md`
  mà Gói 30 nêu **không tồn tại** trên main lẫn integration (đã kiểm bằng
  contents API + code search, 0 kết quả). Bản review thực tế là comment PR
  #119 `6655312858` — lượt này đọc toàn văn comment đó làm căn cứ.
- ACK comment checkpoint 14 trên issue #116: CẦN thẻ duyệt của chủ dự án
  qua GitHub connector — ghi rõ để luồng chính xử lý, lượt chạy này không
  treo chờ. Viết lại mô tả PR #119 theo số lượng thực (Gói 30 item 8) cũng
  cần thẻ duyệt — ghi rõ để luồng chính xử lý.

## Quyết định D1 (từ review + Gói 30 item 5) — ĐÃ DUYỆT CHO VO NHÁP

D1 được duyệt **chỉ cho sản xuất VO nháp** với 21 cửa sổ thoại hiện tại
(chưa khóa hình/mix cuối): CIN_001_S05 giữ 24.8–28.5s; CIN_002 7–11s;
CIN_004 7.5–9.5s, Ly An nói ngoài khung; CIN_006 12.5–17.5s. Không sửa câu
canon, không tự tăng tốc giọng để ép vừa thời lượng. → VO campaign 17 cue
còn lại nay ĐÃ MỞ (khối tiếp theo sau khi xong các fix Gói 30).

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Thêm `count_srt_cues()` (đếm block SRT đúng dạng index + timestamp). `dialogueCues` = số `shots[].dialogue` trong timing JSON đã parse; check bằng SRT đã parse và `"cues"` manifest nguồn khi có — lệch thì FAIL, exit 1. `campaignTotals` thêm `"dialogueCues"` (tính tổng, = 21). Nhãn checkpoint 14 + note ghi rõ cách suy số cue. Notes animatic đồng bộ lại đúng nội dung checkpoint 13 (trước đây script giữ note cũ của checkpoint 10 trong khi manifest đã sửa tay ở checkpoint 13 — gộp 2 note "No final picture" trùng nhau thành 1). |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Thêm `check_runtime_cine_manifest()`: với mỗi cảnh, runtime `dialogueCues` == timing dialogue == SRT cue == manifest nguồn `"cues"` (khi có); `campaignTotals.dialogueCues` == tổng suy ra. Nhãn checkpoint 14. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Chỉ cập nhật nhãn checkpoint 14 (theo đúng mẫu checkpoint 13). Không đổi logic kiểm. |
| `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` | Tái sinh bằng builder: CIN_001/002/004/006 `0 → 1`; `campaignTotals.dialogueCues = 21`; các SHA/size khác không đổi. Audio manifest tái sinh byte-identical (không nằm trong diff). |

Giá trị sau sửa (đo từ byte thật): 20 cảnh, 21 cue — CIN_018 = 2, 19 cảnh
còn lại = 1. Khớp: timing dialogue 21 == SRT cue 21 == runtime manifest
21 == manifest nguồn `"cues"` (17 cue campaign, P0/CIN_006 không có key).

## Kết quả kiểm chứng lại (byte thật, không PASS giả)

### 1. Source pack kiểm chứng lại — PASS, 0 mismatch

`MEDIA02_CHECKPOINT_14_SOURCE_REVALIDATION_20261105.json`
(sha `0b767a6f3e7aec76…`):

- Audio nguồn: 1093 file (22 nhạc/ambience + 173 SFX/UI × 3 variant × 2 +
  11 stem P0) khớp byte/sha/codec/48 kHz/kênh/thời lượng, 0 con trỏ LFS.
- Timing + SRT: 20/20 cảnh, timing dialogues 21 == SRT cues 21, UTF-8
  strict + NFC, khớp từng ký tự.
- **Mới:** runtime cine scenes 20, runtime dialogue cues total 21 —
  timing == SRT == runtime manifest, 0 lệch.
- Animatic: 12/12 panel khớp sha v2, MP4/OGV 640×360 72 s; VO P0: 3/3
  take khớp sha/thời lượng và vừa cửa sổ.
- Ghi chú duy nhất (đã biết): OGV `avg_frame_rate 0/0` do Theora gộp
  frame giữ nguyên — thời lượng vẫn 72 s, không phải lỗi.

### 2. Runtime delivery kiểm chứng lại — PASS, 0 mismatch

`MEDIA02_CHECKPOINT_14_RUNTIME_REVERIFY_20261105.json`
(sha `5937ce8259dd5bd1…`):

| Nhóm | Số file kiểm | Kết quả |
|---|---|---|
| Audio runtime (22 nhạc/ambience + 519 SFX/UI + 4 VO P0) | 545 | khớp manifest, 0 mismatch |
| Animatic P0 v2 (MP4 + OGV + poster) | 3 | khớp sha, 0 mismatch |
| Timing JSON 20 cảnh | 20 | khớp sha, 0 mismatch |
| SRT 20 cảnh | 20 | khớp sha, 0 mismatch |

### 3. Kiểm thử phủ định — cả hai check mới đều bắt được lỗi cố ý

- Validator: sửa tạm runtime `dialogueCues` CIN_001 `1 → 0` → check mới
  báo đúng 2 lỗi (`!= timing dialogues 1`, `!= SRT cues 1`); khôi phục
  manifest về SHA `0afb8876…` (khớp trước test).
- Builder: sửa tạm manifest nguồn CAMPAIGN, `cues` CIN_003 `→ []` →
  builder in `FAIL: CIN_003: source manifest cues 0 != timing dialogues 1`,
  exit 1; khôi phục manifest nguồn, `git status` sạch ở đường đó.
  (Manifest runtime viết ra trong lần chạy lỗi này byte-identical với bản
  đúng, vì số cue ghi vẫn lấy từ timing/SRT — lỗi chỉ làm build FAIL.)

## Trạng thái repo

- Nhánh media: head `7891265` trước checkpoint này; commit checkpoint 14
  `94d7a99` ĐÃ PUSH (ls-remote xác nhận; scope audit 699 paths,
  0 violations, base integration HEAD `f383233`). PR #119 nay có
  20 commit.
- Chỉ 4 file sửa + 2 JSON báo cáo mới trong commit này; không đụng audio,
  timing, SRT, panel hay animatic.

## Giới hạn / khuyết điểm (ghi rõ, không giấu)

- **Chưa sửa finding 2 (LF/CRLF) và finding 4 (22 binary raw → LFS)** —
  đó là Gói 30 item 2, khối tiếp theo. Trạng thái đã đo: `.gitattributes`
  trên cả integration lẫn nhánh media đều CHƯA có quy tắc `text eol=lf`
  cho file delivery JSON/SRT mới (chỉ có quy tắc cũ cho
  `Tools/AudioProduction`, `Art_Source/Audio`, `BuildCandidates`…); "quy
  tắc LF của Codex" mà Gói 30 nêu chưa tồn tại — cần Codex bổ sung, hoặc
  chủ dự án quyết cho Muse thêm theo đúng mẫu hiện có trong media roots.
- **Đếm 22 binary raw: có lệch 1 file so với review.** Review chốt ở
  `3f34f0d`: đúng 22 file khớp pattern LFS nhưng lưu raw (7 VO + 1 sheet
  v1 + 12 panel + MP4 + poster; OGV không tính vì chưa có pattern LFS).
  Checkpoint 13 thêm `P0_storyboard_sheet_v2.png` → nay là **23 file
  pattern-LFS raw + 1 OGV = 24 file raw mới**. Gói 30 item 2 nói "chuyển
  đúng 22 binary raw sang LFS; OGV cũng thuộc LFS" — chưa rõ sheet v2 có
  tính vào 22 hay là file thứ 23; cần chủ dự án/Codex xác nhận 1 dòng
  trước khi làm khối LFS (không tự đoán).
- **Chưa sửa finding 3 phần còn lại (CIN_002_S02):** 4/5 lỗi hình đã sửa
  ở checkpoint 13; còn CIN_002_S02 — tay băng chạm nước (phải là tay lành
  dừng trước mặt nước), crop cắt đầu/mặt — và yêu cầu "tạo từng keyframe
  16:9 riêng, không dùng crop tự động từ collage làm khung final". Đây là
  khối hình tiếp theo (Gói 30 item 3).
- **Số lượng thực tế (review finding 5) — ghi rõ, không phóng đại:**
  541/545 file audio runtime là port nguyên vẹn từ Codex PackV1 cũ, chỉ
  4 file VO mới (3 take TTS + timeline); campaign mới có timing/SRT chứ
  chưa có 20 video hoàn chỉnh; video duy nhất là reel 72 s, 12 still,
  chỉ dùng review/gallery, không tự chạy làm opening. Báo cáo này viết
  theo số thực; việc viết lại mô tả PR #119 (Gói 30 item 8) chờ thẻ duyệt.
- Loudness/true-peak KHÔNG đo lại ở lượt này (lấy từ checkpoint
  02/04/07/08, đo từ byte thật). Không phải mix PASS, không nghe thử
  bằng tai (D2). Cửa sổ campaign vẫn PROPOSED (D1 chỉ mở VO nháp, chưa
  khóa hình/mix). File runtime vẫn chưa nối vào Godot (D3, presentation
  adapter của Codex).

## Khối tiếp theo

1. Gói 30 fix (b) — item 2: LF + LFS (sau khi chủ dự án/Codex xác nhận
   quy tắc LF và con số 22 vs 23 + OGV).
2. Gói 30 fix (c) — item 3: keyframe CIN_002_S02 đúng (tay lành dừng
   trước mặt nước, không crop đầu/mặt) + keyframe 16:9 riêng từng shot.
3. VO nháp campaign 17 cue (D1 đã mở, chỉ VO nháp, không sửa câu canon,
   không tăng tốc giọng).
