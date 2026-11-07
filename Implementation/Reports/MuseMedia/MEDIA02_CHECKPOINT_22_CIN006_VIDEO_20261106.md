# MEDIA-02 CHECKPOINT 22 — CIN_006 có video: panel storyboard + animated take (Gói 30 item 7) (2026-11-06)

## Khối vừa hoàn thiện

Từ checkpoint 18 đến nay, CIN_006 là scene duy nhất trong 5 scene đã
export **chưa có video** — trạng thái `PENDING_PANELS_NO_STORYBOARD`
vì không có panel nào để dựng clip, và không được bịa video. Checkpoint
22 đóng khoảng trống đó theo đúng quy trình của checkpoint 21
(CIN_005):

1. **Sinh 3 keyframe 16:9 mức storyboard** từ prompt shot của
   Cinema Production Pack **nguyên văn** (một khung cho mỗi shot,
   không crop từ collage), lưu staging WebP 2048×1152 kèm SHA +
   snapshot và bản ghi bàn giao
   (`cin006_keyframes_handover_20261106.md`).
2. **Dựng animated take 18 s / 3 shot** bằng Ken Burns (zoompan) trên
   3 keyframe: MP4 H.264 `d263ddf9…` (540 frame) + OGV Theora
   `8c10c78c…` + poster `53859a19…`, không track âm thanh, không
   subtitle bake-in. Export manifest chuyển trạng thái sang
   `VIDEO_ANIMATED_TAKE_KEN_BURNS`; CIN_006 rời trạng thái PENDING.

## Về character lock của Hạ Mặc / Sầm

Scene có hai nhân vật có tên (`NPC_HA_MAC`, `NPC_SAM_CHU_QUY`) nhưng
**chưa có character lock/model sheet được duyệt cho ai cả**. Theo
direction doc của chính scene ("create storyboard first, do not
guess final design") và DEC-MEDIA-P0 Q4 (chỉ cinematic-only staging),
keyframe ở đây là **storyboard**: mặt và trang phục do sinh ảnh dựng
từ mô tả trong prompt của pack, là placeholder — không tạo canon
thiết kế, không đụng spawn/ID bền của NPC. Thiếu lock chỉ chặn final
picture của các shot này, đúng quy tắc đã chốt.

## Keyframe theo shot (đã soi bằng mắt, khuyết điểm ghi thật)

| Shot | Nội dung khung | Khuyết điểm đã ghi |
|---|---|---|
| S01 (MEDIUM_STATIC) | Sầm ở quầy dưới mái hiên hổ phách: cân gỗ bên trái bàn, ba phiếu gấp có ký hiệu trừu tượng ở giữa, tay đặt trên phiếu giữa; chợ đèn lồng phía sau | Khung đọc như ban đêm (đèn lồng sáng, nền xanh đậm) trong khi mạch truyện là chợ ban ngày; ký tự mờ khó đọc trên biển treo sau quầy. Mặt/trang phục là sinh ảnh dựng, chưa có lock của Sầm |
| S02 (DETAIL_LOCKED) | Cận cảnh bàn làm việc: con dấu đồng đứng bên trái, mặt dấu tròn lớn ở giữa được tay đeo găng căn chỉnh, nhựa xanh trên giấy thô | **Lỗi bố cục:** một bàn tay đeo găng mờ quá khổ và một hình giống mặt nhạt chỉ có một mắt đen tràn vào từ mép phải, chiếm ưu thế khung hình; nhựa xanh đọc như vệt tinh thể bắn trên giấy thay vì sợi kẹt trong giấy. Mục đầu tiên của đợt sửa final picture |
| S03 (MEDIUM_STATIC) | Hạ Mặc ở bàn chợ: tay phải đưa tờ giấy trắng về phía trái khung, tay trái đặt trên tờ che xám phủ sổ mở; túi giấy + ống cuộn trên áo; phố chợ yên bình phía sau | Trang sổ có nét nguệch ngoạc giống chữ nhưng không đọc được; tờ che đọc như tấm bảng xám cứng thay vì tờ giấy; kính lúp gấp không thấy rõ. Ánh sáng ngày lạnh, lệch tông so với S01 ấm đèn lồng (lệch sáng xuyên shot) |

Chứng minh chuyển động đo trên MP4 (mean abs channel diff so với
keyframe): identity 5,64 / 3,30 / 7,04 (ngưỡng < 10); motion 38,22 /
40,69 / 43,12 (ngưỡng > 1,5); liên tục mid↔end 33,18 / 34,27 / 36,53
(ngưỡng > 0,5) — clip chuyển động thật, không phải giữ hình tĩnh.

## Trạng thái GitHub

- Nhánh `muse/media-production-20261104`: nội dung ở commit ngay
  trước báo cáo này; PR #119 vẫn OPEN và HOLD theo Gói 30.

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_cin006_video.py` (mới) | Builder take CIN_006 theo mẫu CP21: kiểm SHA staging, dựng keyframe 640×360 + manifest, render zoompan 3 shot, kiểm frame identity/motion, xuất export manifest. |
| `Art_Source/Cinematics/Campaign/CIN_006/keyframes_16x9/` (mới, 3 file) + `CIN006_keyframes_manifest_v1.json` | 3 keyframe storyboard + manifest có framing/khuyết điểm từng shot và SHA nguồn staging. |
| `ClientGodot/assets/cinematics/CIN_006/` | Thêm MP4 + OGV + poster; `scene_export_manifest_v1.json` viết lại (PENDING → VIDEO_ANIMATED_TAKE_KEN_BURNS); timing/SRT giữ nguyên byte. |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Nhãn checkpoint 22; ghi chú manifest runtime cập nhật trạng thái CIN_006. |
| `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` | sceneClips: CIN_006 chuyển sang bản export có video; cả 5 scene đã export đều có video. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Thêm `check_cin006_keyframes()`; `check_scene_clips()` bỏ nhánh PENDING của CIN_006 và tổng quát hoá nguồn poster (theo videoStatus thay vì hard-code CIN_005 — bản trước crash khi CIN_006 có video vì đi tìm panel P0 không tồn tại). |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Nhãn checkpoint 22. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build take — PASS
`build_cin006_video.py` exit 0, ALL VERIFIED: staging SHA 3/3 khớp,
MP4 540 frame / 18,000 s, OGV đúng thời lượng, poster = keyframe S01,
frame identity/motion đều đạt ngưỡng (số ở trên).

### 2. Runtime delivery — PASS
`build_runtime_delivery.py` exit 0: sceneClips = 5, audio giữ nguyên
570 file; manifest runtime khớp export manifest từng file.

### 3. Source re-validation — PASS, 0 mismatch
`validate_media_deliveries.py` verdict PASS: keyframe CIN_006 3/3,
per-scene clips 5/5 (cả 5 có video), reel vẫn lát đúng 0–72.
JSON: `MEDIA02_CHECKPOINT_22_SOURCE_REVALIDATION_20261106.json`.

### 4. Runtime re-verify — PASS, 0 mismatch
`verify_runtime_delivery.py` verdict PASS.
JSON: `MEDIA02_CHECKPOINT_22_RUNTIME_REVERIFY_20261106.json`.

### 5. Scope audit — 0 vi phạm
Diff 3 chấm từ merge-base `cf17178` so với integration `f0859d0`: 864 path, tất cả nằm trong các root media policy cho phép (`Art_Source/Cinematics/`, `ClientGodot/assets/cinematics/`, `Implementation/Reports/MuseMedia/`, `Tools/MediaProduction/Muse/`…). Nội dung ở commit `ebef39f`.

## Giới hạn còn lại

- Toàn bộ vẫn mức STORYBOARD + motion animatic Ken Burns — không
  phải final take diễn pose 8–12 fps; chờ character lock của Hạ Mặc
  và Sầm (việc của hướng thiết kế/Codex) mới làm final picture.
- S02 cần sửa bố cục ở đợt revision final picture (đã ghi là mục đầu
  tiên); lệch sáng xuyên 3 shot cần art-direction lock.
- Cửa sổ thoại canonical 12,5–17,5 s giữ nguyên PROPOSED; bản VO
  nháp (CP19) tràn +0,520 s — theo quyết định chủ dự án 2026-11-06,
  giữ nguyên để Codex quyết khi review PR #119. Take alternate
  CIN_006_ALT_T01 vẫn tách riêng, không nằm trong SRT/clip này.
- Clip không có track âm thanh: VO/nhạc/ambience của CIN_006 chỉ có
  stem ứng viên đã đo ở CP02/CP05 (SFX/CINEMA/reveal), chưa có bản
  mix cho scene này.
