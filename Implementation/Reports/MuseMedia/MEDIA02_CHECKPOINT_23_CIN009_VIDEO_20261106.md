# MEDIA-02 CHECKPOINT 23 — CIN_009 animated take: cảnh Chapter 2 đầu tiên có video (2026-11-06)

## Khối vừa hoàn thiện

Cảnh campaign thứ ba có video: **CIN_009 "Tiếng rừng được đáp" (Chương 2, quest C2-05, 18 s / 3 shot)** —
3 keyframe storyboard + clip 18 s có chuyển động camera thật (Ken Burns), MP4 review + OGV
runtime + poster + timing/SRT + manifest. Đây là cảnh campaign đầu tiên của Chapter 2 có video
và là cảnh tiếp theo trong hàng đợi sau CIN_005/CIN_006 vì pack ghi `characters: []` nên không
có character lock nào chặn hình. Clip KHÔNG có track audio (VO/nhạc/ambience thêm riêng khi
edit, theo dialoguePolicy của pack) và KHÔNG có phụ đề cháy hình.

| Shot | Camera | Motion (Ken Burns) | Identity (khung zoom 1.0 ≈ keyframe) | Motion (khung zoom ≈ keyframe) | Liên tục |
|---|---|---|---|---|---|
| CIN_009_S01 | DETAIL_LOCKED | push-in 1.00→1.08, giữa suối | t=0.0 s: 4,65 (< 10) | t=5.9 s: 34,58 (> 1,5) | 29,56 (> 0,5) |
| CIN_009_S02 | WIDE_STATIC | push-in 1.00→1.10, giữa nhóm thợ | t=6.0 s: 3,76 (< 10) | t=11.9 s: 36,27 (> 1,5) | 31,28 (> 0,5) |
| CIN_009_S03 | TOPDOWN_MATCH | zoom-out 1.08→1.00, giữa khung | frame 539 (cuối): 7,30 (< 10) | t=12.0 s: 32,27 (> 1,5) | 28,44 (> 0,5) |

(Số là mean abs channel diff; ngưỡng identity < 10 theo chuẩn CP18, ngưỡng motion > 1,5 và
liên tục > 0,5 chứng minh clip chuyển động chứ không giữ still.)

- MP4: `CIN_009_640x360_30fps.mp4`, H.264, 640×360, 30 fps, **540 frame**, 18,0 s,
  sha `c67ffcfdfd52…` (1.490.541 B).
- OGV: `CIN_009_640x360_30fps.ogv`, Theora, 640×360, **495 stored frame** (< 540, đúng quy
  tắc CP03: Theora gộp frame gần trùng), 18,0 s,
  sha `4997e04f4a5d…` (459.402 B).
- Poster: `CIN_009_poster.png` = keyframe S01,
  sha `d38c7ad8e4ef…` (410.897 B).

## Keyframe (mức STORYBOARD, đã xem trực tiếp)

Prompt nguyên văn từng shot trong `Cinema_Production_Pack_v1.json`
(sha `09e8685f42bcbd4f…`). Ảnh gốc WebP 2048×1152, resize LANCZOS về PNG 640×360.

| Shot | Keyframe PNG sha (12 ký tự đầu) | Nguồn staging WebP sha |
|---|---|---|
| CIN_009_S01 | `d38c7ad8e4ef…` | `9fbc26675694…` |
| CIN_009_S02 | `fd0051fc7904…` | `ae4022d04d39…` |
| CIN_009_S03 | `d3abc86cd30b…` | `92c363090c1c…` |

- S01: suối được giải thoát chảy giữa rễ chẻ đôi, đốm sáng nhỏ tách khỏi vỏ cây trôi theo
  dòng nước — đúng prompt.
- S02: khoảng rừng sáng dần, ba thợ đội nón lá lắng nghe tiếng quen từ xa, một cây lớn tối
  lặng ở phía phải — đúng prompt ("One tree remains dark and quiet").
- S03: nhìn từ trên xuống, kênh nước có kè đá chảy về lối ra phía nam, rễ chưa sáng nằm lệch
  một bên làm cue khám phá — đúng prompt.
- Khuyết điểm đã ghi vào manifest (không giấu): **S01 có một nhân vật nhỏ áo trùm trắng
  không tên, không có trong prompt**, đứng ở góc trái dưới bên suối; S01 đọc tối/xanh hơn
  payoff ban ngày; **S03 không hoàn toàn top-down** (hơi nghiêng 3/4 ở đá và đền nhỏ) và có
  thêm một đền nhỏ ở trái không có trong prompt; S02 ba thợ là mặt sinh ảnh chung chung
  (không tên, không cần lock vì pack ghi characters []).

## Trạng thái GitHub

- Nhánh `muse/media-production-20261104`: nội dung checkpoint ở commit `b3f99c3` (đã push);
  báo cáo này ở commit ngay sau. PR #119 vẫn OPEN và HOLD theo Gói 30.
- **Issue #116 — kiểm tra lượt này (connector read-only, tính đến 01:40 JST 06/11/2026):**
  issue vẫn `updated: 2026-11-05T11:49:15Z` (= 20:49 JST 05/11), 10 comments — **không có
  bình luận mới** sau lần kiểm tra của checkpoint 21 (00:44 JST 06/11). Không có chỉ đạo
  mới của Codex hay chủ dự án; 3 take VO OVERRUN vẫn chờ Codex quyết ở review PR #119 theo
  verdict chủ dự án 2026-11-06 00:42 JST (giữ nguyên cửa sổ, không nới, không cắt).
- Viết lại mô tả PR #119 (Gói 30 item 8) vẫn chờ thẻ duyệt của chủ dự án ở luồng chính;
  mô tả hiện vẫn ghi head cũ 1db3f23 (checkpoint 07).

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_cin009_video.py` (mới) | Builder CIN_009 theo mẫu CP22: verify SHA staging WebP → resize keyframe 640×360 → lắp clip 18 s bằng một lệnh ffmpeg filter_complex (3 zoompan, concat) → MP4 + OGV + poster + copy timing/SRT + export manifest; kiểm chứng ffprobe + identity/motion/continuous bằng frame giải mã thật; lỗi nào cũng exit 1. Khác CP22: CIN_009 không có timing manifest riêng nên SHA SRT + dialogueWindowStatus lấy từ `CAMPAIGN_timing_manifest_v1.json`. |
| `Art_Source/Cinematics/Campaign/CIN_009/keyframes_16x9/` (mới, 3 file) | 3 keyframe PNG 640×360 + `CIN009_keyframes_manifest_v1.json` (SHA nguồn WebP + SHA PNG + framing + knownDefects, status STORYBOARD). |
| `ClientGodot/assets/cinematics/CIN_009/` (mới, 6 file) | MP4 + OGV + poster + timing + SRT + `scene_export_manifest_v1.json` (`videoStatus` `VIDEO_ANIMATED_TAKE_KEN_BURNS`, motionModel, frameCheck từng shot; `reelOffsetSeconds: null` — CIN_009 không thuộc reel 72 s). |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Mục 6 nhận thêm CIN_009 (sceneClips 5 → 6); nhãn checkpoint 23 + ghi chú CIN_009. |
| `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` | `sceneClips` 5 → 6 (thêm CIN_009, files khớp export manifest); nhãn checkpoint 23. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | `check_scene_clips()` nhận 6 clip; thêm `check_cin009_keyframes()` (3 keyframe + SHA staging + framing/defects + khớp shot timing); nhãn checkpoint 23. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | `sceneClips` 5 → 6; nhãn checkpoint 23. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build clip CIN_009 — PASS
`build_cin009_video.py` exit 0: MP4 540 frame / 18,0 s; OGV 18,0 s;
identity 4,65 / 3,76 / 7,30; motion 34,58 / 36,27 / 32,27; continuous 29,56 / 31,28 /
28,44. Poster SHA = keyframe S01. Timing/SRT SHA khớp campaign manifest; dialogueCues = 1
(timing ↔ SRT). VO draft CIN_009_S03 (checkpoint 17) dài 4,080 s trong cửa sổ 5,0 s — FITS.

### 2. Runtime delivery — PASS
`build_runtime_delivery.py` exit 0: audio 570 file (22 music/ambience + 519 SFX/UI + 25 VO +
4 mix, không đổi so với CP22); cinematics animatic 3 file verified, sceneClips 6, scenes 20
(timing+SRT 40 file).

### 3. Source re-validation — PASS, 0 mismatch
`validate_media_deliveries.py` verdict PASS: 1093 audio file; timing 20 cảnh / 21 cue;
keyframes P0 12/12; CIN_005 keyframes 3/3; CIN_006 keyframes 3/3; CIN_009 keyframes 3/3
(staging SHA-verified); campaign VO 17/17 (15 FITS / 2 OVERRUN cũ, là finding đạo diễn,
không phải mismatch byte); CIN_006 VO 2/2; P0 mix 4/4; scene clips 6/6 (cả 6 có video).
JSON: `MEDIA02_CHECKPOINT_23_SOURCE_REVALIDATION_20261106.json`.

### 4. Runtime re-verify — PASS, 0 mismatch
`verify_runtime_delivery.py` verdict PASS: audio 570/570, animatic 3, scenes 20, timing 20,
SRT 20, scene clips 6, scene clip files 30. JSON:
`MEDIA02_CHECKPOINT_23_RUNTIME_REVERIFY_20261106.json`.

### 5. Scope audit — 0 vi phạm
`Tools/Coordination/check_agent_scope.py --base f0859d0 --head b3f99c3
--branch muse/media-production-20261104`: **878 changed paths, 0 violations**.

## Giới hạn / khuyết điểm (ghi thật, không giấu)

- Keyframe ở mức STORYBOARD, không phải final picture: S01 có nhân vật áo trùm trắng
  sinh thêm (không tên, không trong prompt); S03 chưa hoàn toàn top-down và có đền nhỏ
  ngoài prompt; S02 thợ là mặt sinh ảnh chung chung. Tất cả ghi trong manifest từng shot,
  sửa ở đợt final-picture revision pass.
- Chuyển động clip là Ken Burns mức animatic trên keyframe tĩnh, không phải take pose
  animation final (pack cadence 8–12 fps cần reference nhân vật đã duyệt + pose animation).
- Clip không có track audio; VO draft CIN_009_S03 (4,080 s, FITS) và nhạc/ambience thêm
  riêng khi edit.
- Cửa sổ thoại 12.5–17.5 s vẫn PROPOSED_ANIMATIC_PLACEMENT (chỉ CIN_001_S05 là DECIDED).
- PR #119 vẫn HOLD; mô tả PR vẫn ghi head cũ, chờ thẻ duyệt của chủ dự án để viết lại.

## Khối tiếp theo

- CIN_020 animated take (18 s / 3 shots, characters [] — cảnh tiếp theo không cần
  character lock; VOICE_LETTER_RECIPIENT đã duyệt cho Người nhận thư vô danh, vai giọng
  cinematic-only, không sinh NPC gameplay).
- Viết lại mô tả PR #119 (Gói 30 item 8) khi có thẻ duyệt của chủ dự án.
- Nhạc/SFX sáng tác-remix thật (phần còn lại của Gói 30 item 7).
