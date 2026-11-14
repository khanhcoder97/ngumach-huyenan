# MEDIA-02 — WO37 M-C Checkpoint 2: P0 Motion / A-B (12 shot P0)

- Ngày: 2026-11-08 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `6f79853`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (M-C) · Motion ledger `MOTION_LEDGER_v1.json`
- Trạng thái: **DRAFT_POSE_ANIMATION** — bản nháp chuyển động ở mức storyboard; final picture vẫn chờ character lock; A/B là review pack, file runtime KHÔNG bị thay.

## 1. Phạm vi khối

Checkpoint 2 = 12 shot P0 theo motion ledger (priority 1): CIN_001 S01–S06, CIN_002 S01–S03, CIN_004 S01–S03. Checkpoint 3 = 51 shot còn lại (26 ref-sufficient priority 2 + 25 Ken Burns hold priority 3).

Mô hình chuyển động (áp cho cả 12 shot):

- Mỗi shot 6 s có **một action beat 5 pose, 10 pose/s** (mỗi pose giữ 3 frame ở 30 fps = beat 0,5 s); giữ keyframe trước beat, giữ pose cuối sau beat.
- Shot thoại bắt đầu beat đúng tại đầu cửa sổ thoại: CIN_001_S05 beat 0,8–1,3 s shot-local (= 24,8 s scene, cửa sổ đã khóa DECIDED bản B); CIN_002_S02 beat 1,0–1,5 s (= 7,0 s scene); CIN_004_S02 beat 1,5–2,0 s (= 7,5 s scene). Các shot còn lại beat 2,0–2,5 s.
- Take B của mỗi scene ghép 3 shot + mix v3 (AAC 192k); video A/B xếp dọc 640×720, cùng audio v3 cả hai nửa — **A/B lần này chỉ so video, chưa so soundtrack** (soundtrack A/B là phần còn lại của big checkpoint 2).

## 2. Kết luận lớn: tuyến strip sinh bằng ảnh (generated) BỊ HỦY

7 strip đã sinh (4 lần đầu + 3 sinh lại) đều là **panorama với chủ thể lặp lại, không phải 8 frame riêng**, kiểm chứng ở độ phân giải đầy đủ: cắt đều 740 px vẫn giữ mảnh của lần lặp kề — pose 5 của CIN_002_S02 v3 giữ hình người đang tan của lần lặp sau; pose 5 của CIN_004_S01 v2 giữ một cổ rắn thứ hai ở mép phải; pose 5 của CIN_004_S02 v1 là một lát panorama khác (đầu bị cắt ở mép phải). Các lỗi trước đó: S05 v1 panorama; S05 v2 tracking close-up (camera lia, framing nhảy); CIN_002_S02 v1 mặt tan chảy ở panel 6–8 + panel 5 đã chạm nước có gợn tiếp xúc (vi phạm guardrail, kiểm chứng ở zoom 2×); v2 ô vuông 560×560 + tay chạm nước ở panel 7–8; CIN_004_S01 v1 panel 1 đầu thấp (đứt liên tục với keyframe) + đầu thoát khỏi mép phải ở panel 6–8. Diff liên-pose trung bình của panel sinh ~50–70 (vẽ lại toàn bộ; riêng dải nền trên ~38 = "redraw boil").

**Quyết định: cả 12 shot đều procedural** (render bằng code từ keyframe storyboard; không còn pixel sinh nào). 3 strip đã dùng đã chuyển sang PNG rồi **xóa khỏi repo**; SHA + lý do loại ghi trong spec/manifest (`rejectedStrips`, 8 mục, xem §6). Build đầu (3 shot sinh) cho validator PASS 288/288 nhưng **kết quả đó VÔ HIỆU với 3 shot sinh** vì kiểm tra hình ảnh sau đó chứng minh pose lỗi; pack đã build lại hoàn toàn procedural.

D-MC-01 (lịch sử): panel sinh là vẽ lại toàn bộ, nền bị "boil"; không còn áp dụng vì không còn pixel sinh nào.

## 3. Lớp procedural từng shot (cuối cùng)

| Shot | Lớp | Beat shot-local |
|---|---|---|
| CIN_001_S01 | rain (90, seed 101) + ripples (3 tâm) | 2,0–2,5 s |
| CIN_001_S02 | parcel bob box [348,212,478,332] dy [0,1,2,1,0] + ripples + rain | 2,0–2,5 s |
| CIN_001_S03 | ripples (3 tâm) + drip x=320 | 2,0–2,5 s |
| CIN_001_S04 | drops (3 tâm, growth 2.0) + rain (70) | 2,0–2,5 s |
| CIN_001_S05 | pull — parcel box [425,225,565,335] dx [0,-2,-4,-6,-8], arm box [270,175,420,295] dx [0,1,2,3,4] + ripples + rain | 0,8–1,3 s |
| CIN_001_S06 | idle sway box [170,55,330,325] dy [0,1,2,1,0] | 2,0–2,5 s |
| CIN_002_S01 | rain + ripples (4 tâm) | 2,0–2,5 s |
| CIN_002_S02 | arm-lower — box [300,165,470,335] dy [0,1,2,3,4] + rain; đầu ngón tay hạ 4 px, vẫn trên mặt nước (guardrail) | 1,0–1,5 s |
| CIN_002_S03 | reeds swayX boxes [0,215,130,360] + [515,195,640,360], dx [0,1,2,1,0] + ripples | 2,0–2,5 s |
| CIN_004_S01 | jaw box [300,150,425,210] dy [0,1,2,3,4] trước, rồi rise box [280,15,430,230] dy [0,-2,-4,-6,-8] + rain (thứ tự quan trọng: hàm trên ảnh gốc, rồi toàn đầu nhô lên) | 2,0–2,5 s |
| CIN_004_S02 | maskSweep — flood fill theo colour-mask từ seed [[300,180],[200,200],[250,150],[350,200],[450,200],[500,200]], dx [0,-2,-4,-6,-8]; splash 3 tâm seed 402; debris 4 mảnh; rain | 1,5–2,0 s |
| CIN_004_S03 | advance — flood fill mask rắn từ seed (320,150), dy [0,3,6,9,12], fillBelow 16 + rain + ripples | 2,0–2,5 s |

Guardrail giữ nguyên: sừng gãy CIN_004_S01 (1 sừng gãy ngắn + 1 sừng nguyên); tay lành KHÔNG chạm nước ở CIN_002_S02 (khe hở nhìn thấy được, không gợn tiếp xúc); thiết kế Ly An = keyframe; không có chữ tiếng Anh.

## 4. Đo đạc (từ byte thật, validator độc lập)

Ngưỡng procedural: inter-pose diff (0,15; 30), pose1-vs-keyframe < 10. Tất cả 12 shot PASS.

| Shot | mean inter-pose diff | pose1 vs keyframe | pose cuối vs keyframe |
|---|---|---|---|
| CIN_001_S01 | 0,734 | 0,301 | 0,438 |
| CIN_001_S02 | 1,502 | 0,255 | 0,388 |
| CIN_001_S03 | 0,498 | 0,099 | 0,473 |
| CIN_001_S04 | 0,503 | 0,235 | 0,486 |
| CIN_001_S05 | 2,493 | 0,284 | 5,534 |
| CIN_001_S06 | 1,813 | 0,000 | 0,000 |
| CIN_002_S01 | 1,054 | 0,394 | 0,691 |
| CIN_002_S02 | 1,611 | 0,249 | 3,388 |
| CIN_002_S03 | 1,487 | 0,034 | 0,129 |
| CIN_004_S01 | 2,896 | 0,238 | 6,391 |
| CIN_004_S02 | 10,890 | 0,295 | 25,588 |
| CIN_004_S03 | 7,718 | 0,260 | 9,701 |

Ghi chú: CIN_001_S06 pose cuối = keyframe (sway dy quay về 0 — vòng idle khép kín, đúng thiết kế). CIN_004_S02 là beat mạnh nhất (sweep 8 px + splash + debris); 25,588 vẫn trong ngưỡng 30. 9 shot procedural không đổi tái tạo diff byte-identical so với build trước.

Kiểm chứng hình ảnh (đã xem trực tiếp): contact sheet 3 shot chuyển đổi — CIN_002_S02 tay hạ dần, mặt nguyên vẹn, tay không chạm nước; CIN_004_S01 hàm mở dần + đầu nhô lên, sừng giữ canon; CIN_004_S02 cuộn rắn quét sang trái, splash/debris đọc được, không có bóng ma. Khung A/B CIN_002 tại 9 s sau build lại: nửa B tay thấp hơn rõ, vẫn trên mặt nước — blob panorama đã biến mất. Box debug overlay đã kiểm chứng vị trí cho cả 12 shot.

Validator độc lập `check_p0_motion_ab_v1.py`: **PASS — 282 checks, 0 mismatches** (re-hash toàn bộ file, re-render lại pose, re-đo diff tới 0,001, probe toàn bộ video, so nửa AB với take A/B < 5, kiểm beat thoại = đầu cửa sổ thoại).

Re-validation hiện có: `validate_media_deliveries.py` **PASS**; `verify_runtime_delivery.py` **PASS, 0 mismatches** — runtime audio 627 file không đổi (music_ambience 22, sfx_ui_variants 519, vo 30, mix 30, composed 26); campaign 20 scene / 63 shot / 378 s / 21 dialogue cue. File runtime KHÔNG bị thay.

## 5. Deliverable

- Spec: `Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_SPEC_v1.json`
- Manifest: `Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_v1.json` (12 shot, 60 pose, 0 generated / 12 procedural)
- Builder: `Tools/MediaProduction/Muse/build_p0_motion_ab_v1.py` · Validator: `Tools/MediaProduction/Muse/check_p0_motion_ab_v1.py`
- Báo cáo này + validation JSON: `Implementation/Reports/MuseMedia/MEDIA02_WO37_MC_CP2_P0_MOTION_AB_20261108.md` · `MEDIA02_WO37_MC_CP2_VALIDATION_20261108.json`
- Pose: `Art_Source/Cinematics/P0_Motion/pose_frames/<SHOT>/pose_01..05.png` (60 file)
- Take shot (silent, 640×360, 30 fps, libx264 crf 18): `Art_Source/Cinematics/P0_Motion/takes/<SHOT>_pose_640x360_30fps.mp4` (12 file)
- Take scene B (audio mix v3): `Art_Source/Cinematics/P0_Motion/takes/CIN_001_pose_640x360_30fps.mp4` sha `e244b152f778051990752e18f462a94f54eb037ff65075fd356b6b08e62624f1` (36,0 s) · `CIN_002` sha `822a32d7a9291e520d42e122a2e690d61a9d7c2a93ade9361d8e4c6897b104be` (18,0 s) · `CIN_004` sha `15e1b8d1d276b64660e019e75efe819ae34909bb210fa4b8830c4c8a79ef6fdd` (18,0 s)
- Video A/B (640×720, audio v3): `Art_Source/Cinematics/P0_Motion/ab/CIN_001_ab_kenburns_vs_pose_640x720_30fps.mp4` sha `827ad1d7a1d4651db425499a62282cc7e6dc061f556f97cf3cf6ca9e79bd28a4` · `CIN_002` sha `7621c008189cb64bb2072c3a49b70bb70349d8b1471b90d8e328903899e7906c` · `CIN_004` sha `66d5ae81504d71201a55d745ab8889708578e41f7f4714241111d2cc4e47e9f2`
- Contact sheet: `Art_Source/Cinematics/P0_Motion/contact/<SHOT>_contact.png` (12 file)
- `pose_strips_raw/` hiện TRỐNG (strip đã xóa).

## 6. Strip sinh bị loại (8 mục — SHA + lý do, ghi trong manifest)

| # | Shot / lần | webp SHA256 (đầu) | Lý do |
|---|---|---|---|
| 1 | CIN_001_S05 v1 | `63797abf79cb…` | Panorama, không phải strip: một cảnh liên tục, cô gái lặp 8 lần; cắt đều gây nhảy nền (tre → cầu → nước). |
| 2 | CIN_001_S05 v2 | `bbd6fa6b17e3…` | Tracking close-up: camera lia phải qua các panel, cô gái lớn hơn nhiều so với framing keyframe; beat sẽ jump-cut ở ranh giới hold. |
| 3 | CIN_002_S02 v1 | `3765fbfd44f4…` | Panel 6–8: mặt tan chảy (mắt/mũi nhòe); panel 5 đã chạm nước có gợn tiếp xúc (vi phạm guardrail, kiểm chứng zoom 2×). |
| 4 | CIN_002_S02 v2 | `9d85271c98d6…` | Ô vuông 560×560 (không 16:9; không fit nếu không pad/crop nặng); panel 7–8 tay chạm nước. |
| 5 | CIN_004_S01 v1 | `90f3f403e4bb…` | Panel 1 đầu thấp (đứt liên tục với keyframe); panel 6–8 đầu thoát khỏi mép phải khung hình. |
| 6 | CIN_002_S02 v3 (đã dùng, rồi loại) | `dd5b6a1cb171…` (png `6a3cc142ac3f…`) | Panorama: người đàn ông lặp dọc một cảnh liên tục; cắt đều 740 px giữ mảnh của lần lặp kề (pose 5 giữ hình người đang tan của lần lặp sau; kiểm chứng độ phân giải đầy đủ). |
| 7 | CIN_004_S01 v2 (đã dùng, rồi loại) | `9a9cadcc8dac…` (png `0424bcde9acd…`) | Panorama: pose 5 giữ một cổ rắn thứ hai ở mép phải và đầu ở vị trí khác (kiểm chứng độ phân giải đầy đủ). |
| 8 | CIN_004_S02 v1 (đã dùng, rồi loại) | `21befa44c087…` (png `56d411a00e0b…`) | Panorama: pose 5 là một lát panorama khác (đầu bị cắt ở mép phải, cuộn ở vị trí khác; kiểm chứng độ phân giải đầy đủ). |

SHA đầy đủ trong manifest `P0_MOTION_AB_v1.json` → `rejectedStrips`.

## 7. Giới hạn / khuyết điểm

- **DRAFT_POSE_ANIMATION**: chuyển động procedural là bản nháp, KHÔNG phải final pose animation; final picture vẫn chờ character lock.
- CIN_002_S02: tay chỉ hạ 4 px — chuyển động tinh tế, có thể khó thấy ở tốc độ phát thường; guardrail (không chạm nước) buộc phải giữ biên độ nhỏ.
- CIN_001_S06: sway idle quay về vị trí nghỉ — tinh tế theo thiết kế.
- CIN_004_S02: beat mạnh nhất, last-vs-keyframe 25,588 gần ngưỡng 30 — chấp nhận được vì là sweep + splash + debris, nhưng cần xem lại khi có final picture.
- A/B lần này chỉ so video (cùng audio v3 hai bên); soundtrack A/B (v1 vs v2 vs v3) chưa làm — phần còn lại của WO37 big checkpoint 2.
- Không có ear audition; không có mix PASS. VO/mix vẫn DRAFT_NOT_FINAL.
- 2 bug đã sửa trong lượt: ffmpeg concat dùng path tương đối trong file concat ở /tmp; `build_color_mask` crash với seed point dạng list.

## 8. Khối tiếp theo

WO37 big checkpoint 2 (phần còn lại): soundtrack A/B cho P0 (v1 vs v2 vs v3) — hoặc checkpoint 3: motion 51 shot còn lại theo ledger (`executionOrder`). PR #119 vẫn HOLD, không tự merge; mô tả PR + ACK CP53–54 vẫn chờ thẻ duyệt của chủ dự án (không thuộc lượt này).
