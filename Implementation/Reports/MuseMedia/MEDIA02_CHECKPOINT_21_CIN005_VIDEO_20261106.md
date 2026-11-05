# MEDIA-02 CHECKPOINT 21 — CIN_005 animated take: video campaign đầu tiên có chuyển động thật (2026-11-06)

## Khối vừa hoàn thiện

Cảnh campaign đầu tiên có video: **CIN_005 "Một thành phố vẫn sống" (Chương 1, 18 s / 3 shot)** —
3 keyframe storyboard + clip 18 s có chuyển động camera thật (Ken Burns), MP4 review + OGV
runtime + poster + timing/SRT + manifest. Đây là cảnh campaign đầu tiên trong pack có
`characters: []` nên không có character lock nào chặn hình; clip KHÔNG có track audio
(VO/nhạc/ambience thêm riêng khi edit, theo dialoguePolicy của pack) và KHÔNG có phụ đề
cháy hình.

| Shot | Camera | Motion (Ken Burns) | Identity (khung zoom 1.0 ≈ keyframe) | Motion (khung zoom ≈ keyframe) | Liên tục |
|---|---|---|---|---|---|
| CIN_005_S01 | WIDE_STATIC | push-in 1.00→1.08, giữa khung | t=0.0 s: 6,06 (< 10) | t=5.9 s: 43,34 (> 1,5) | 37,92 (> 0,5) |
| CIN_005_S02 | DETAIL_LOCKED | push-in 1.00→1.10, lệch lên phía cờ | t=6.0 s: 4,17 (< 10) | t=11.9 s: 39,40 (> 1,5) | 35,58 (> 0,5) |
| CIN_005_S03 | TOPDOWN_MATCH | zoom-out 1.08→1.00, giữa khung | frame 539 (cuối): 8,88 (< 10) | t=12.0 s: 40,14 (> 1,5) | 35,20 (> 0,5) |

(Số là mean abs channel diff; ngưỡng identity < 10 theo chuẩn CP18, ngưỡng motion > 1,5 và
liên tục > 0,5 chứng minh clip chuyển động chứ không giữ still.)

- MP4: `CIN_005_640x360_30fps.mp4`, H.264, 640×360, 30 fps, **540 frame**, 18,0 s,
  sha `4ea8365ee35f63427bf4e4f7dfc0a6e17849e740356903b5995c1cf8beaa6d12` (1.809.621 B).
- OGV: `CIN_005_640x360_30fps.ogv`, Theora, 640×360, **371 stored frame** (< 540, đúng quy
  tắc CP03: Theora gộp frame gần trùng), 18,0 s,
  sha `922000754adedf3b4a191040323ce191991d43f9d5c89d390912da3424874d5c` (497.253 B).
- Poster: `CIN_005_poster.png` = keyframe S01,
  sha `949c7f07cbbafeddf1e5f6fefd46db8c2531964e31c7ca879786d3a970d32e88` (451.999 B).

## Keyframe (mức STORYBOARD, đã xem trực tiếp)

Prompt nguyên văn từng shot trong `Cinema_Production_Pack_v1.json`
(sha `09e8685f42bcbd4f…`). Ảnh gốc WebP 2048×1152, resize LANCZOS về PNG 640×360.

| Shot | Keyframe PNG sha (12 ký tự đầu) | Nguồn staging WebP sha |
|---|---|---|
| CIN_005_S01 | `949c7f07cbba…` | `aa892df52ee8…` |
| CIN_005_S02 | `7c47e5c88f1b…` | `3b649c91cae1…` |
| CIN_005_S03 | `f2db67721c4c…` | `81ea5bdfe4f1…` |

- S01: sân Thanh Lạc buổi muộn, mái ngói đỏ, đường đá xanh lam, người mở cửa chớp, người
  trên thang sửa cờ, sạp trà bày bát — đúng prompt.
- S02: đủ 5 cờ với motif hình học nguyên tố khác nhau, bay lệch hướng — đúng prompt.
- S03: top-down nghiêm ngặt, các lối đi hội tụ quanh bục thông báo trống, dân làm việc nhỏ,
  lối vào người chơi phía nam để trống — đúng prompt.
- Khuyết điểm đã ghi vào manifest (không giấu): **S02 mái ngói xám xanh, lệch palette mái
  đỏ của S01** (cần khóa art-direction ở final); S01/S03 có dấu giống chữ rất nhỏ trên biển
  hiệu; S02 có thêm một nhân vật đội nón lá không tên, không có trong prompt (không phải
  nhân vật có tên, không xung đột canon).

## Trạng thái GitHub

- Nhánh `muse/media-production-20261104`: nội dung ở commit `cbb4c7e`; báo cáo này ở commit
  ngay sau. PR #119 vẫn OPEN và HOLD theo Gói 30 (33 commit / 840 file, head `27a7966`
  sau CP20; sau lượt này sẽ là 35 commit).
- **Lưu ý chạy song song:** đầu lượt này (00:44–00:47 JST) một worker khác đang làm
  checkpoint 20 (P0 draft mix) trong cùng clone, chưa commit. Lượt này KHÔNG đụng vào clone
  cho tới khi CP20 được worker kia push xong (`7652195`/`27a7966`, scope audit 839 paths
  0 violations); keyframe được sinh ra thư mục staging ngoài repo trong lúc chờ, rồi mới
  lắp clip + commit sau khi clone sạch ở `27a7966`.

## Issue #116 — kiểm tra lượt này (trình duyệt, tính đến 00:44 JST 06/11/2026)

- Có 2 bình luận mới của chủ dự án sau Gói 30 (19:15 JST 05/11), cả hai đều của khanhcoder97:
  - 20:16 JST 05/11: PR #120 đã merge vào integration a84ce59, 10 CI xanh; duyệt 21 cửa sổ
    sản xuất VO nháp; chưa duyệt final picture/mix/autoplay; **CIN_020 dùng
    VOICE_LETTER_RECIPIENT** cho Người nhận thư vô danh (vai giọng cinematic-only, không sinh
    NPC gameplay, không gán lời cho nhân vật có tên khác); tiếp 17 VO nháp + video/audio còn
    thiếu; không dùng reel 72 s làm opening.
  - 20:49 JST 05/11: nghiệm thu bổ sung tại 67f0d92 (CP14): cuecount 20 cảnh/21 cue đúng;
    4 panel sửa được nhận ở mức storyboard; CIN_002_S02 phải dùng file sửa (tay lành dừng
    trước mặt nước, đủ đầu/mặt trong khung 16:9 — đã làm ở CP16); "Không cần xin xác nhận
    lại số 22 hay 23"; 21 cửa sổ VO nháp + vai VOICE_LETTER_RECIPIENT đã duyệt trong decision
    JSON trên integration; reel 72 s vẫn chỉ review/gallery.
- Đã đối chiếu: CP17 dùng đúng `avocado_v2:MAI_01 (Aria, role VOICE_LETTER_RECIPIENT)` cho
  CIN_020 — không cần sửa casting. CP16 đã sửa xong panel thứ 5 (CIN_002_S02).
- **Không có quyết định mới về 3 take VO OVERRUN** (CIN_005_S03 +0,160 s, CIN_018_S03
  +0,280 s, CIN_006_S03 +0,520 s) — vẫn chờ đạo diễn, giữ nguyên cửa sổ theo verdict chủ
  dự án 2026-11-06 00:42 JST (không nới, không cắt, để Codex quyết ở review PR #119).
- Không có bình luận mới nào của Codex trên issue #116 sau 19:15 JST 05/11.
- Viết lại mô tả PR #119 (Gói 30 item 8) vẫn chờ thẻ duyệt của chủ dự án ở luồng chính;
  mô tả hiện vẫn ghi head cũ 1db3f23 (checkpoint 07).

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_cin005_video.py` (mới) | Builder CIN_005: verify SHA staging WebP → resize keyframe 640×360 → lắp clip 18 s bằng một lệnh ffmpeg filter_complex (3 zoompan, concat) → MP4 + OGV + poster + copy timing/SRT + export manifest; kiểm chứng ffprobe + identity/motion/continuous bằng frame giải mã thật; lỗi nào cũng exit 1. Hai lỗi đã sửa trong lúc làm: input zoompan phải là 1 frame duy nhất (input loop `-t 6` làm shot đầu lấp cả clip); identity S03 lấy theo số frame 539 thay vì timestamp 17,9 s (zoom-out còn 1.0009 ở frame 537, diff 14,6). |
| `Art_Source/Cinematics/Campaign/CIN_005/keyframes_16x9/` (mới, 3 file) | 3 keyframe PNG 640×360 + `CIN005_keyframes_manifest_v1.json` (SHA nguồn WebP + SHA PNG + framing + knownDefects, status STORYBOARD). |
| `ClientGodot/assets/cinematics/CIN_005/` (mới, 6 file) | MP4 + OGV + poster + timing + SRT + `scene_export_manifest_v1.json` (`videoStatus` mới `VIDEO_ANIMATED_TAKE_KEN_BURNS`, motionModel, frameCheck từng shot; `reelOffsetSeconds: null` — CIN_005 không thuộc reel 72 s). |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Mục 6 nhận thêm CIN_005 (5 scene clip); nhãn checkpoint 21 + ghi chú CIN_005. |
| `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` | `sceneClips` 4 → 5 (thêm CIN_005, files khớp export manifest); nhãn checkpoint 21. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | `check_scene_clips()` nhận 5 clip + trạng thái `VIDEO_ANIMATED_TAKE_KEN_BURNS` (không reel offset; poster đối chiếu keyframe Campaign thay vì panel P0); thêm `check_cin005_keyframes()` (3 keyframe + SHA staging + framing/defects + khớp shot timing); nhãn checkpoint 21. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | `sceneClips` 4 → 5; nhãn checkpoint 21. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build clip CIN_005 — PASS
`build_cin005_video.py` exit 0: MP4 540 frame / 18,0 s; OGV 371 stored frame / 18,0 s;
identity 6,06 / 4,17 / 8,88; motion 43,34 / 39,40 / 40,14; continuous 37,92 / 35,58 /
35,20. Poster SHA = keyframe S01. Timing/SRT SHA khớp campaign manifest; dialogueCues = 1
(timing ↔ SRT).

### 2. Runtime delivery — PASS
`build_runtime_delivery.py` exit 0: audio 570 file (22 music/ambience + 519 SFX/UI + 25 VO +
4 mix, không đổi so với CP20); cinematics animatic 3 file verified, sceneClips 5, scenes 20
(timing+SRT 40 file).

### 3. Source re-validation — PASS, 0 mismatch
`validate_media_deliveries.py` verdict PASS: 1093 audio file; timing 20 cảnh / 21 cue;
keyframes P0 12/12; CIN_005 keyframes 3/3 (staging SHA-verified); campaign VO 17/17
(15 FITS / 2 OVERRUN cũ, là finding đạo diễn, không phải mismatch byte); CIN_006 VO 2/2;
P0 mix 4/4; scene clips 5/5 (4 có video). JSON:
`MEDIA02_CHECKPOINT_21_SOURCE_REVALIDATION_20261106.json`.

### 4. Runtime re-verify — PASS, 0 mismatch
`verify_runtime_delivery.py` verdict PASS: audio 570/570, animatic 3, scenes 20, timing 20,
SRT 20, scene clips 5, scene clip files 22. JSON:
`MEDIA02_CHECKPOINT_21_RUNTIME_REVERIFY_20261106.json`.

### 5. Scope audit — 0 vi phạm
Diff từ merge-base so với integration `f0859d0`: **853 path, 0 violations**
(`Tools/Coordination/check_agent_scope.py --base f0859d0 --head HEAD
--branch muse/media-production-20261104`).

## Giới hạn còn lại

- Vẫn STORYBOARD / RENDERED_CANDIDATE: keyframe + motion Ken Burns là mức animatic, KHÔNG
  phải final take có pose animation (pack yêu cầu pose 8–12 fps + reference nhân vật đã
  duyệt). Prompt pack ghi "Fixed shot camera" cho ảnh tĩnh; motion nằm ở khâu edit theo
  lệnh Gói 30 item 7 ("campaign videos with real motion"), ghi rõ là `ANIMATIC_MOTION_KEN_BURNS`
  trong manifest, không nhận là final.
- S02 lệch palette mái (xám xanh vs đỏ ở S01) — cần khóa art-direction ở final.
- Cửa sổ thoại S03 (12,5–17,5 s) vẫn PROPOSED; VO nháp overrun +0,160 s (không ảnh hưởng
  clip vì clip không có audio).
- CIN_006 vẫn chưa có video (chưa có panel storyboard). Các cảnh campaign còn lại chưa có
  video: 15 cảnh / 45 shot (trong đó CIN_009, CIN_020 cũng có `characters: []` như CIN_005).
- Viết lại mô tả PR #119 vẫn chờ thẻ duyệt của chủ dự án.
