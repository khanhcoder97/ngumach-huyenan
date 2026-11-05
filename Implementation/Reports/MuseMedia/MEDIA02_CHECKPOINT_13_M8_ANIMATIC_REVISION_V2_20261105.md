# MEDIA-02 CHECKPOINT 13 — M8 animatic revision v2: sửa 4 khuyết điểm panel (D4) (2026-11-05)

## Khối vừa hoàn thiện

Sửa 4 khuyết điểm panel animatic P0 còn tồn từ checkpoint 03 (quyết định mở
D4), dựng lại animatic MP4/OGV/poster + sheet/spec/manifest v2, kiểm chứng
lại toàn bộ deliverable MEDIA-02 đối chiếu byte thật. Không sửa timing/SRT/
audio/VO — chỉ sửa hình panel và dựng lại video từ panel.

## Trạng thái GitHub (đọc qua public API, 2026-11-05 18:45 JST)

- Issue #116: vẫn OPEN, 7 comment, mới nhất `6649909991`
  (2026-11-05 04:45 UTC, ACK checkpoint 03–07 + PR #119). Không có chỉ
  đạo mới; D1 (xác nhận cửa sổ PROPOSED) vẫn chưa được xác nhận → VO dự
  thảo campaign (D5) vẫn chờ.
- PR #119: OPEN, chưa merge, head `3f34f0d`, base `f383233`, mergeable
  clean, 17 commit, 691 file, 0 review, 0 comment. Không có hoạt động mới
  ngoài commit checkpoint 12 đã push.
- Integration HEAD không đổi: `f383233` (không có merge mới kể từ
  checkpoint 12).
- Lưu ý vận hành: tên tool GitHub connector đã đổi (`get_issue` /
  `get_pull_request` không còn được quảng cáo; `issue_read` /
  `pull_request_read` mới chưa nằm trong tập read-only được duyệt nên
  `call-read-tool` từ chối, và một lần gọi `get_issue` trả 401). Lượt này
  đọc issue/PR qua public GitHub API (repo public, chỉ đọc) và đã xác minh
  số liệu khớp với checkpoint 12. Việc đăng comment ACK checkpoint 13 vẫn
  CẦN thẻ duyệt của chủ dự án qua luồng chính — ghi rõ để luồng chính xử
  lý, lượt chạy này không treo chờ.

## 4 panel đã sửa (xem trực tiếp từng panel, không PASS giả)

Reference Ly An lấy từ integration `f383233` (chỉ đọc):
`Art_Source/Combat_Visuals_20261105/Characters/ben_mua_questkit_v1.png`,
SHA-256 nội dung `cff1157896050a93947d3573424f1af1547265604e3d0e97599c053b91ba5f32`
khớp đúng ghi trong spec v1; KHÔNG copy file vào nhánh media, KHÔNG sửa.
Ly An theo questkit: tóc nâu đuôi ngựa thấp, áo choàng mưa xanh lam viền
vàng đất, áo kem, túi đưa thư nâu — không búi topknot, không áo chùng tối,
không kiếm.

| Shot | Khuyết điểm v1 | Sửa ở v2 (đã xem trực tiếp panel dựng lại) |
|---|---|---|
| CIN_001_S03 | Chuông vẽ DẠNG VẬT RẮN dưới cầu tàu kèm phản chiếu | Bỏ hẳn chuông rắn — chỉ còn bóng phản chiếu hình chuông gợn trên mặt nước dưới cầu, một gợn sóng cắt ngang bóng. Không còn chuông trên mặt nước. |
| CIN_001_S06 | Nhân vật đọc như Tạ Văn Khánh (búi tóc, áo chùng tối) | Ly An theo đúng questkit: đuôi ngựa thấp, áo choàng xanh lam viền vàng, áo kem, túi đưa thư nâu; đứng trên bến gỗ top-down, cọc buộc dây + kiện gỗ bên cạnh, vũng mưa. |
| CIN_004_S01 | Chi tiết "1 sừng gãy" đọc chưa rõ | Đầu rắn hiện đúng 1 sừng nguyên cong + 1 gốc sừng gãy ngắn, đầu gãy lởm chởm (canon: đúng 1 sừng gãy). Gai xương dọc cổ là chi tiết thân, không phải sừng. |
| CIN_004_S03 | Khung hình nghiêng thay vì strict top-down | Strict top-down trực giao phẳng: đấu trường kênh đá nhìn từ trên xuống, rắn rút về hồ phía bắc, khu vực đến phía nam trống, bến gỗ ở mép nam. |

Phương pháp: 4 panel v2 sinh bằng edit từ panel v1 (giữ bố cục/palette),
xem trực tiếp cả 4 trước khi lắp; script mới
`Tools/MediaProduction/Muse/revise_p0_animatic_panels.py` dán panel vào
đúng vùng crop mà `build_p0_animatic.py` trích (cùng công thức inset 3 px +
center-crop 16:9) nên panel dựng lại = đúng ảnh đã xem (sai lệch pixel do
resize 2 lần: trung bình tuyệt đối 1,3–6,4/255, không thấy bằng mắt).
8 panel còn lại và panel nghiên cứu thứ 13 giữ nguyên byte (SHA khớp v1).

## Deliverable v2

| File | Nội dung / SHA-256 |
|---|---|
| `Art_Source/Cinematics/P0_Animatic/P0_storyboard_sheet_v2.png` | Sheet 1920×1280 v2. SHA-256 `9a0a5419345504478a1b5b9264680321ded32170cd996440dc215700289e1224`. |
| `Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v2.json` | Spec v2: 4 shot bỏ `panelDefect`, thêm `panelFix` + xác nhận đã xem; `baseSha` = integration HEAD `f383233` (nhánh media không rebase, merge-base vẫn `cf17178`); reference questkit nay ghi ở integration `f383233`. SHA-256 `e60b17de16cbf712cd1d9f1c6a7c05564558bec49d46c25234fe610f9a0a0395`. |
| `Art_Source/Cinematics/P0_Animatic/P0_animatic_outputs_v2.json` | Manifest hash/output do tool sinh (ffprobe verify). SHA-256 `3752c3f749f88fc515da21b050366af2f11a09106eaecb45ce3d04a4b8c4ed30`. |
| `Art_Source/Cinematics/P0_Animatic/panels/panel_<SHOT>.png` (12 file) | 8 panel SHA khớp v1; 4 panel mới: S03 `c07ddc986650…`, S06 `0678aa59b4c8…`, CIN_004_S01 `e43df4ff0178…`, CIN_004_S03 `e7493991a218…`. |
| `ClientGodot/assets/cinematics/P0_animatic_640x360_30fps.mp4` | H.264, 640×360, 30 fps, 72,0 s, 2160 frame, 0 audio track. SHA-256 `872e7b0c8fbc0059c3adf58cf46e31fcb768ebc7a5d3311798812e6ff9a93e83`, 695.097 byte. |
| `ClientGodot/assets/cinematics/P0_animatic_640x360_30fps.ogv` | Theora, 640×360, 72,0 s, 263 stored frame (Theora gộp frame giữ nguyên — đã biết từ checkpoint 03). SHA-256 `7498a8f14970ad352869fda516fd42a188620fcab7cd6856c6a5001e77dc8d72`, 1.852.526 byte. |
| `ClientGodot/assets/cinematics/P0_animatic_poster.png` | Poster = panel CIN_001_S01, không đổi. SHA-256 `ea9d42287274d46c5b8c1cedb70c00a4d795f61d757484233fbbfd019ba9bce8`. |
| `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` | Mục animatic cập nhật SHA/size v2, trạng thái `VERIFIED_CHECKPOINT_13`; timing/SRT không đổi. |
| `Tools/MediaProduction/Muse/revise_p0_animatic_panels.py` | Tool mới: dán panel sửa vào sheet + sinh spec v2 (xác định, có kiểm tra). |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Cập nhật `ANIMATIC_EXPECTED` sang SHA v2 + nhãn checkpoint 13 (để lần chạy lại sau không fail sai). Không đổi logic copy/kiểm. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Đọc `P0_animatic_outputs_v2.json` thay cho v1; nhãn checkpoint 13, base `f383233`. Không đổi logic kiểm. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Chỉ cập nhật nhãn checkpoint 13 / base `f383233`. Không đổi logic kiểm. |

## Kết quả kiểm chứng lại (byte thật, không PASS giả)

### 1. Source pack kiểm chứng lại — PASS, 0 mismatch

Chạy tool checkpoint 09 đã cập nhật (đọc outputs v2),
`MEDIA02_CHECKPOINT_13_SOURCE_REVALIDATION_20261105.json`
(sha `08032e5282cdd93f9d0768c5f33ed22f612dfb8895e922f60e3128feac928b9e`):

- Audio nguồn: 1093 file (44 nhạc/ambience + 1038 SFX/UI + 11 stem P0)
  khớp byte/sha/codec/48 kHz/kênh/thời lượng, 0 con trỏ LFS.
- Timing + SRT: 20/20 cảnh (63 shot × 6 s = 378 s), 21 thoại = 21 cue SRT,
  UTF-8 strict + NFC, khớp từng ký tự (không đổi so với checkpoint 12).
- Animatic: 12/12 panel khớp sha manifest v2, MP4/OGV 640×360 72 s;
  VO P0: 3/3 take khớp sha/thời lượng và vừa cửa sổ.
- Ghi chú duy nhất (đã biết từ checkpoint 03/11/12): OGV
  `avg_frame_rate 0/0` do Theora gộp frame giữ nguyên — thời lượng vẫn
  72 s, không phải lỗi.

### 2. Runtime delivery kiểm chứng lại — PASS, 0 mismatch

Chạy tool checkpoint 11 (chỉ cập nhật nhãn),
`MEDIA02_CHECKPOINT_13_RUNTIME_REVERIFY_20261105.json`
(sha `1ba214c6a6f578bc842d61de827a3c28b9b5783466663b2b50724cff310f7e8e`):

| Nhóm | Số file kiểm | Kết quả |
|---|---|---|
| Audio runtime (22 nhạc/ambience + 519 SFX/UI + 4 VO P0) | 545 | khớp manifest, 0 mismatch |
| Animatic P0 v2 (MP4 + OGV + poster) | 3 | khớp sha manifest runtime đã cập nhật, 0 mismatch |
| Timing JSON 20 cảnh | 20 | khớp sha manifest, 0 mismatch |
| SRT 20 cảnh | 20 | khớp sha manifest, 0 mismatch |

## Trạng thái repo

- Nhánh media: head `3f34f0d` trước checkpoint này; commit checkpoint 13
  `3243c0c` ĐÃ PUSH (ls-remote xác nhận; scope audit 699 paths,
  0 violations, base integration HEAD `f383233`). PR #119 nay có
  18 commit, 699 file.
- Lưu ý lưu trữ (để các lượt sau không lặp lỗi): file animatic
  (panel/sheet/MP4/poster) lưu BYTE THẬT trong git từ checkpoint 03, dù
  `.gitattributes` khai `filter=lfs`; `git add` thường (có git-lfs trong
  PATH) sẽ đổi chúng thành con trỏ LFS 131 byte — lượt này đã add với
  filter lfs tắt (`-c filter.lfs.clean=` …) để giữ nguyên cách lưu trữ.
  Audio masters vẫn là con trỏ LFS như trước. OGV không thuộc filter lfs
  (không có `*.ogv` trong `.gitattributes`) nên luôn là byte thật.
- ACK comment checkpoint 13 trên issue #116: CẦN thẻ duyệt của chủ dự án
  qua GitHub connector — ghi rõ để luồng chính xử lý, lượt chạy này
  không treo chờ.

## Giới hạn / khuyết điểm (ghi rõ, không giấu)

- Vẫn là storyboard animatic, chưa phải final picture: sửa 4 panel là sửa
  storyboard theo D4, không phải take hoạt hình; final takes vẫn chờ
  Codex review.
- Panel S03 v2 còn một vệt mưa trắng mỏng dọc giữa khung (đọc như vệt mưa
  rơi trúng tâm gợn sóng) — chấp nhận được ở mức storyboard.
- Panel S06 v2 vẽ Ly An ở góc 3/4 top-down (không phẳng tuyệt đối) nhưng
  đúng bố cục bến top-down của shot và đọc rõ là Ly An theo questkit.
- Panel S01 v2: gai xương dọc cổ có thể thoáng nhìn nhầm thành gốc gãy,
  nhưng trên đầu rắn chỉ có đúng 1 sừng nguyên + 1 gốc gãy — đúng canon.
- Loudness/true-peak KHÔNG đo lại ở lượt này (lấy từ checkpoint
  02/04/07/08, đo từ byte thật). Không phải mix PASS, không nghe thử
  bằng tai (D2).
- Cửa sổ campaign vẫn PROPOSED (D1); VO campaign chưa làm (D5, chờ D1).
- File runtime vẫn chưa nối vào Godot (D3, presentation adapter của Codex).

## Khối tiếp theo

VO dự thảo campaign (17 cue) ngay khi D1 được xác nhận; nếu chưa có xác
nhận, M8 QA liên tục sau mỗi lần integration merge hoặc review mới trên
PR #119.
