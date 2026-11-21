# MEDIA-02 — Checkpoint 03: P0 storyboard/animatic 72 giây / 12 shot

- Ngày: 2026-11-05 (JST). Agent: Muse (chỉ media, theo policy `agent_scope_v2.json` / work 28 + work 29).
- Nhánh: `muse/media-production-20261104`. Base: integration `cf17178` (không đổi so với checkpoint 01/02; fetch đầu lượt không thấy HEAD mới trên media branch lẫn integration).
- Khối này: (b) trong thứ tự sẵn sàng, NÂNG CẤP theo chỉ đạo mới — xem mục 1.

## 1. Chỉ đạo mới áp dụng trong lượt này

- Issue #116 vẫn OPEN; số comment tăng 5 → 6 trong lượt này. Comment mới nhất là của chủ dự án, đăng 2026-11-05 08:35:34 JST (comment id 6645214148), đã đọc qua live browser (chỉ đọc, không đăng/react/sửa).
- Nội dung vận hành mới (tóm tắt, không trích nguyên văn): P0 cinema unblocked; làm ngay storyboard/animatic P0 đủ 72 giây/12 shot kèm VO/SRT/ambience/stems riêng, rồi tiếp M3–M8; đẩy checkpoint animatic/audio/source thật, không phải báo cáo inventory-only. DEC-MEDIA-P0-20261105 KHÔNG đổi: CIN_001_S05 vẫn bản B, CIN_004 Ly An vẫn off-screen voice, CIN006 alternate vẫn không thay canon; Hạ Mặc/Sầm vẫn cinematic-only staging (comment mới không nhắc lại, không thu hồi).
- Reference nhân vật mới từ Codex (PR #118, nhánh `codex/benmua-combat-visuals-20261105`, FETCH_HEAD `a75b53840c0b2fb4bbfa5a84c5bfa80914bffe9b`): file `Art_Source/Combat_Visuals_20261105/Characters/ben_mua_questkit_v1.png` (SHA-256 `cff1157896050a93947d3573424f1af1547265604e3d0e97599c053b91ba5f32`, lấy byte thật qua Git LFS smudge, đã xem trực tiếp). Nhánh Codex này chỉ đọc để làm reference — KHÔNG merge vào nhánh media, KHÔNG sửa. Hàng trên: trái Ly An (áo choàng mưa xanh lam viền vàng đất, túi đưa thư nâu), giữa Tạ Văn Khánh (áo chùng xanh đen, tay băng, bao kiếm); người toàn thân tới y608, không cắt chân ở 512. Môi trường vẫn bám `Art_Source/BenMua_Concept_Rebuild_20261105` (chỉ reference bố cục/màu/kiến trúc; KHÔNG crop atlas thành đồ vật — panel storyboard vẽ mới từ prompt pack).
- Vì vậy khối (b) của lượt này không còn chỉ 6 shot lock-free mà là toàn bộ animatic P0 12 shot. Trạng thái "lock đã duyệt" vẫn chưa được khẳng định trong comment mới (chỉ nói câu hỏi reference không còn là điểm chặn để chờ) — nên checkpoint này vẫn ghi rõ: đây là STORYBOARD ANIMATIC, chưa phải final picture; final takes vẫn chờ Codex review.

## 2. Deliverable

| File | Nội dung |
|---|---|
| `Art_Source/Cinematics/P0_Animatic/P0_storyboard_sheet_v1.png` | 1 sheet storyboard 1920×1280, 13 panel vẽ mới (12 panel vào timeline + 1 panel nghiên cứu dự phòng, xem mục 4). SHA-256 `0c82c2bdf8c9befa6e18e0ae126573261800e197f2625bd737ed2fffd7e1bee7`. |
| `Art_Source/Cinematics/P0_Animatic/panels/panel_<SHOT>.png` (12 file) | Panel 640×360 crop từ sheet (inset 3 px bỏ viền, center-crop 16:9). SHA-256 từng panel trong `P0_animatic_outputs_v1.json`. |
| `Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v1.json` | Spec đầy đủ: thứ tự 12 shot, timeline animatic 0–72 s (CIN_001 0–36, CIN_002 36–54, CIN_004 54–72), camera, sheetBox, stem plan theo shot (checkpoint 02), cửa sổ thoại (DECIDED/PROPOSED + quy đổi sang timeline animatic), SRT tham chiếu, defect từng panel. |
| `ClientGodot/assets/cinematics/P0_animatic_640x360_30fps.mp4` | Review MP4: H.264, 640×360, 30 fps, 72,0 s, 2160 frame, 0 audio track, 0 subtitle nướng. SHA-256 `a625043c4fd47eee15e0f203c8a5cde5890d00a0c0a9fc31933b249f37b5cf06`. |
| `ClientGodot/assets/cinematics/P0_animatic_640x360_30fps.ogv` | Runtime OGV: Theora, 640×360, 72,0 s, 0 audio track. SHA-256 `7c0fdb291992b49df18210c72a41e64ebdbb4baf9a56ab0a6179d40cf6813325`. |
| `ClientGodot/assets/cinematics/P0_animatic_poster.png` | Poster = panel CIN_001_S01 (SHA-256 `ea9d42287274d46c5b8c1cedb70c00a4d795f61d757484233fbbfd019ba9bce8`). |
| `Art_Source/Cinematics/P0_Animatic/P0_animatic_outputs_v1.json` | Manifest hash/output do tool sinh (ffprobe verify). |
| `Tools/MediaProduction/Muse/build_p0_animatic.py` | Tool tái lập: crop panel từ sheet + spec → MP4/OGV/poster → verify ffprobe (fail nếu sai thời lượng/codec/kích thước). |

## 3. Kiểm chứng (byte thật, ffprobe/ffmpeg)

- MP4: duration 72,000000 s; decode đủ 2160 frame; 640×360; avg_frame_rate 30/1; 0 audio track; không subtitle nướng.
- OGV: duration 72,000000 s; Theora 640×360; 0 audio track. Số stored frame chỉ 211 — KHÔNG phải file hỏng: mã hóa lại từ chính MP4 đã verify cũng cho ~211–252 stored frame trên 72 s. Nguyên nhân: libtheora gộp các frame panel giữ nguyên (duplicate) thành frame có thời lượng dài hơn; thời lượng phát vẫn đủ 72 s (decode tới 71,66 s). Tool đã sửa assertion cho phù hợp và ghi chú rõ.
- Panel: xem trực tiếp contact sheet 12 panel sau crop — đúng thứ tự, đúng nội dung từng shot; center-crop 16:9 không cắt mất chủ thể.
- Timeline: 12 shot × 6,0 s = 72,0 s liền mạch, không khoảng trống; cửa sổ thoại trên timeline animatic: CIN_001_S05 24,8–28,5 s (DECIDED); CIN_002_S02 43,0–47,0 s (PROPOSED); CIN_004_S02 61,5–63,5 s (PROPOSED, off-screen DECIDED).
- SRT vẫn là file dự thảo checkpoint 01, tách riêng, không nướng vào video. Stem vẫn là bảng PROPOSED_CANDIDATE checkpoint 02, tách riêng, không mix.

## 4. Khuyết điểm và giới hạn (ghi rõ, không giấu)

- Panel CIN_001_S03 vẽ chuông DƯỚI DẠNG VẬT RẮN dưới cầu tàu kèm phản chiếu, trái pack (chỉ thấy trong phản chiếu, trên mặt nước không có chuông). Final picture phải sửa.
- Panel CIN_001_S06 vẽ nhân vật đọc như Tạ Văn Khánh (búi tóc, áo chùng tối) thay vì Ly An. Final picture phải vẽ Ly An theo questkit.
- Panel CIN_004_S01: chi tiết "1 sừng gãy" đọc chưa rõ. Final picture phải thể hiện đúng 1 sừng gãy theo canon.
- Panel CIN_004_S03: khung hình nghiêng thay vì strict top-down. Final picture phải về đúng top-down arena.
- Sheet có 13 panel: panel thừa (hàng 4 cột 2, rắn cuộn, box [506, 959, 947, 1251]) là nghiên cứu dự phòng cho CIN_004_S02; panel dùng cho S02 là panel xoáy nước (box [973, 959, 1416, 1251]). Panel thừa có mặt trong sheet nhưng KHÔNG nằm trong timeline MP4/OGV.
- Đây là animatic giữ panel (mỗi shot giữ 1 panel suốt 6 s), KHÔNG phải take hoạt hình: không có chuyển động 8–12 fps, không morph optical-flow. Nhịp pose 8–12 fps của pack áp cho take hoạt hình sau này, không áp cho panel-hold animatic này.
- VO audio chưa thu — đó là khối (c) tiếp theo. Animatic này chỉ mang cửa sổ timing VO + SRT dự thảo + stem plan tách riêng; không tự nhận đã có VO.
- 2 vị trí thoại PROPOSED (CIN_002, CIN_004) vẫn chờ đạo diễn/Codex xác nhận; sẽ sửa spec/SRT khi được chốt.
- ACK comment cho checkpoint này + media PR vẫn chờ thẻ duyệt của chủ dự án ở luồng chính (worker không tự đăng comment/mở PR khi chưa có thẻ mới). Payload PR cũ vẫn ở `~/workspace/godot-prototype/pr_comments/media_pr_create.json` theo ghi nhận trước; không thử tạo PR lại trong lượt này khi chủ dự án không có mặt để bấm thẻ.

## 5. Khối tiếp theo

- (c) VO dự thảo 3 câu P0 theo cửa sổ đã khóa + VOICE_GUIDE (giọng hư cấu, không clone giọng người thật, không sample không license).
- Sau đó: (d) timing CIN006 (P1) theo Q3/Q4; (e) các pack M3/M4/M5.
