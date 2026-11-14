# MEDIA-02 — WO37 M-C Checkpoint 3a: Campaign Motion, priority-2 (26 shots)

- Ngày: 2026-11-08 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `6f79853`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (M-C) · Motion ledger `MOTION_LEDGER_v1.json`
- Trạng thái: **DRAFT_POSE_ANIMATION** — bản nháp chuyển động ở mức storyboard; final picture vẫn chờ character lock; A/B là review pack, file runtime KHÔNG bị thay.

## 1. Phạm vi khối

Checkpoint 3a = 26 shot ưu tiên 2 theo motion ledger (ACTION_ANIMATION, đủ reference, không cần character lock), trải 15 cảnh: CIN_003 (S01–S02), CIN_005 (S01–S03), CIN_006 S02, CIN_007 S01, CIN_008 (S01–S02), CIN_009 (S01–S03), CIN_010 S01, CIN_011 (S01–S02), CIN_012 S01, CIN_013 S01, CIN_015 (S01–S02), CIN_016 S01, CIN_018 S01, CIN_019 (S01–S02), CIN_020 (S01–S03).

Mô hình chuyển động (giống checkpoint 2 P0): mỗi shot 6 s có **một action beat 5 pose, 10 pose/s** (mỗi pose giữ 3 frame ở 30 fps = beat 0,5 s); giữ keyframe trước beat, giữ pose cuối sau beat. 3 shot thoại bắt đầu beat đúng tại đầu cửa sổ thoại: CIN_005_S03, CIN_009_S03, CIN_020_S03 đều beat 0,5–1,0 s shot-local (cửa sổ 12,5–17,5 s scene). Các shot còn lại beat 2,0–2,5 s.

**Tất cả 26 shot đều procedural** (render bằng code từ keyframe storyboard; không còn pixel sinh nào — tuyến strip sinh đã bị hủy ở checkpoint 2). Layer mới duy nhất so với checkpoint 2: `bubbles` (cột bọt khí dâng, dùng cho 2 shot dưới nước CIN_015_S01/S02). Các layer khác tái dùng từ checkpoint 2: rain, ripples, drops, drip, bob, sway, swayX.

Scene B take = ghép đủ 3 shot của cảnh theo thứ tự ledger: shot pose-animation cho shot ưu tiên 2, **hold slice Ken Burns** (cắt chính xác 6 s từ video runtime A, encode lại cùng tham số) cho shot ưu tiên 3 — để B take vẫn là bản cắt review đủ cảnh, đồng bộ mix v1. 6 shot ưu tiên 3 còn lại (CIN_014 S01–S03, CIN_017 S01–S03) thuộc cảnh không có shot ưu tiên 2 nên không có scene B take trong pack này; chúng giữ Ken Burns hold theo luật R4 của ledger.

## 2. Đo đạc (từ byte thật, validator độc lập)

Ngưỡng procedural: inter-pose diff (0,15; 30), pose1-vs-keyframe < 10. Tất cả 26 shot PASS.

| Shot | Beat (s) | Layer | Mean inter-pose diff | Pose1 vs keyframe | Pose cuối vs keyframe |
|---|---|---|---|---|---|
| CIN_003_S01 | 2.0–2.5 | rain, ripples, swayX | 0.876 | 0.186 | 0.287 |
| CIN_003_S02 | 2.0–2.5 | ripples, swayX | 1.748 | 0.049 | 0.181 |
| CIN_005_S01 | 2.0–2.5 | swayX | 1.203 | 0.0 | 0.0 |
| CIN_005_S02 | 2.0–2.5 | swayX | 2.599 | 0.0 | 0.0 |
| CIN_005_S03 | 0.5–1.0 | swayX | 3.846 | 0.0 | 0.0 |
| CIN_006_S02 | 2.0–2.5 | bob, swayX | 0.441 | 0.0 | 0.597 |
| CIN_007_S01 | 2.0–2.5 | ripples, swayX | 2.625 | 0.035 | 0.156 |
| CIN_008_S01 | 2.0–2.5 | bob, swayX | 1.985 | 0.0 | 3.689 |
| CIN_008_S02 | 2.0–2.5 | bob, swayX | 0.193 | 0.0 | 0.0 |
| CIN_009_S01 | 2.0–2.5 | ripples, swayX | 3.085 | 0.055 | 0.271 |
| CIN_009_S02 | 2.0–2.5 | drops, swayX | 4.022 | 0.008 | 0.109 |
| CIN_009_S03 | 0.5–1.0 | ripples, swayX | 3.619 | 0.052 | 0.254 |
| CIN_010_S01 | 2.0–2.5 | bob, drops, swayX | 2.778 | 0.01 | 0.117 |
| CIN_011_S01 | 2.0–2.5 | drops, swayX | 0.498 | 0.009 | 0.146 |
| CIN_011_S02 | 2.0–2.5 | bob, swayX | 1.071 | 0.0 | 0.0 |
| CIN_012_S01 | 2.0–2.5 | drops, swayX | 0.743 | 0.023 | 0.372 |
| CIN_013_S01 | 2.0–2.5 | swayX | 2.079 | 0.0 | 0.0 |
| CIN_015_S01 | 2.0–2.5 | bubbles, swayX | 1.369 | 0.054 | 0.058 |
| CIN_015_S02 | 2.0–2.5 | bob, bubbles, swayX | 0.92 | 0.045 | 0.044 |
| CIN_016_S01 | 2.0–2.5 | bob, swayX | 0.461 | 0.0 | 0.0 |
| CIN_018_S01 | 2.0–2.5 | bob, swayX | 4.816 | 0.0 | 0.0 |
| CIN_019_S01 | 2.0–2.5 | drops, swayX | 1.332 | 0.024 | 0.425 |
| CIN_019_S02 | 2.0–2.5 | drops, swayX | 0.758 | 0.011 | 0.4 |
| CIN_020_S01 | 2.0–2.5 | bob, ripples, swayX | 1.517 | 0.033 | 0.143 |
| CIN_020_S02 | 2.0–2.5 | swayX | 1.068 | 0.0 | 1.649 |
| CIN_020_S03 | 0.5–1.0 | bob, swayX | 2.483 | 0.0 | 0.0 |

- Mean inter-pose diff toàn pack: min 0,193 (CIN_008_S02) — max 4,816 (CIN_018_S01); pose1-vs-keyframe max 0,186; pose cuối-vs-keyframe max 3,689 (CIN_008_S01, nét bút dịch phải 4 px).
- CIN_008_S02 suýt dưới ngưỡng ở lần build đầu (diff 0,113 < 0,15): đã tăng biên độ bob/sway từ 2 px lên 4 px, diff lên 0,191–0,195, PASS. Không shot nào khác dưới 0,4.

Kiểm chứng hình ảnh (đã xem trực tiếp contact sheet 8 shot rủi ro nhất): CIN_008_S01 tay/bút dịch phải, con dấu nhấp, không xé hình; CIN_006_S02 con dấu ấn xuống rõ, bút lay; CIN_020_S02 nét bút dịch phải, ớt khô lay; CIN_019_S02 tia lửa lớn dần, đèn/cần gạt lay; CIN_015_S01/S02 cột bọt khí dâng thấy được qua các pose, vẫn giữ tông teal dưới nước (guardrail UNDERWATER_NOT_DRY); CIN_005_S03/CIN_009_S03 cây bụi lay ở góc, beat đúng đầu cửa sổ thoại. Không có bóng ma panorama, không xé box.

Validator độc lập `check_campaign_motion_p2_v1.py`: **PASS — 777 checks, 0 mismatches** (hash lại toàn bộ file, render lại pose, re-đo diff tới 0,001, probe toàn bộ video, hold slice so với runtime A tại cùng thời điểm scene, B take đúng thứ tự segment pose/hold, AB so nửa A/B với take A/B dưới dải nhãn).

Một chi tiết kiểm chứng: so nửa AB với take A/B ở khung giữa cảnh, CIN_010 cho diff 6,225 (vượt ngưỡng 5) — đã truy tới đúng nguồn: khung giữa là shot hold S02 (Ken Burns) nên B take tại 9,0 s trùng khớp 0,0 với hold slice, hold slice khác runtime A chỉ 1,482 (nhiễu re-encode); phần chênh lệch nằm ở **dải nhãn drawtext** (chữ trắng/nền đen trên nền sa mạc sáng). Validator đã sửa: so sánh phần dưới dải nhãn 40 px, CIN_010 còn 1,62/1,59. Video AB không lỗi; đây là sửa phương pháp kiểm, không phải sửa số liệu.

Re-validation hiện có: `validate_media_deliveries.py` **PASS**; `verify_runtime_delivery.py` **PASS, 0 mismatches** — runtime audio 627 file không đổi; campaign 20 scene / 63 shot / 378 s / 21 dialogue cue. File runtime KHÔNG bị thay.

## 3. Deliverable

- Spec: `Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2_SPEC_v1.json`
- Manifest: `Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2_v1.json` (26 shot, 130 pose, 0 generated / 26 procedural)
- Builder: `Tools/MediaProduction/Muse/build_campaign_motion_p2_v1.py` · Validator: `Tools/MediaProduction/Muse/check_campaign_motion_p2_v1.py`
- Báo cáo này + validation JSON: `Implementation/Reports/MuseMedia/MEDIA02_WO37_MC_CP3A_CAMPAIGN_MOTION_P2_20261108.md` · `MEDIA02_WO37_MC_CP3A_VALIDATION_20261108.json`
- Pose: `Art_Source/Cinematics/Campaign_Motion/pose_frames/<SHOT>/pose_01..05.png` (130 file)
- Take shot (silent, 640×360, 30 fps, libx264 crf 18): `Art_Source/Cinematics/Campaign_Motion/takes/<SHOT>_pose_640x360_30fps.mp4` (26 file)
- Hold slice (Ken Burns, 640×360, 30 fps, libx264 crf 18): `Art_Source/Cinematics/Campaign_Motion/takes/<SHOT>_hold_640x360_30fps.mp4` (19 file)
- Take scene B (audio mix draft v1): `Art_Source/Cinematics/Campaign_Motion/takes/<SCENE>_pose_640x360_30fps.mp4` (15 file, 18,0 s mỗi cảnh)

| Scene | B take SHA (đầu) | Thời lượng | Segment (S01/S02/S03) |
|---|---|---|---|
| CIN_003 | `08a17999d803` | 18.0 s | POSE/POSE/KEN_ |
| CIN_005 | `3ef19d4244b9` | 18.0 s | POSE/POSE/POSE |
| CIN_006 | `82f4dda2576a` | 18.0 s | KEN_/POSE/KEN_ |
| CIN_007 | `a51431388e7a` | 18.0 s | POSE/KEN_/KEN_ |
| CIN_008 | `aeb28788ead7` | 18.0 s | POSE/POSE/KEN_ |
| CIN_009 | `c22c55520da3` | 18.0 s | POSE/POSE/POSE |
| CIN_010 | `e599aeff8b7b` | 18.0 s | POSE/KEN_/KEN_ |
| CIN_011 | `ce7caf3e4d18` | 18.0 s | POSE/POSE/KEN_ |
| CIN_012 | `655acf054584` | 18.0 s | POSE/KEN_/KEN_ |
| CIN_013 | `3ee82577b2e7` | 18.0 s | POSE/KEN_/KEN_ |
| CIN_015 | `c20ed21861f9` | 18.0 s | POSE/POSE/KEN_ |
| CIN_016 | `c47710a19615` | 18.0 s | POSE/KEN_/KEN_ |
| CIN_018 | `0804447a7e1e` | 18.0 s | POSE/KEN_/KEN_ |
| CIN_019 | `d39f7a986226` | 18.0 s | POSE/POSE/KEN_ |
| CIN_020 | `7ae22522831b` | 18.0 s | POSE/POSE/POSE |

- Video A/B (640×720, audio mix v1): `Art_Source/Cinematics/Campaign_Motion/ab/<SCENE>_ab_kenburns_vs_pose_640x720_30fps.mp4` (15 file, 18,0 s mỗi cảnh)

| Scene | AB SHA (đầu) | Thời lượng |
|---|---|---|
| CIN_003 | `e26f6716ec0c` | 18.0 s |
| CIN_005 | `ea5bff4c4236` | 18.0 s |
| CIN_006 | `0d1bc5e04938` | 18.0 s |
| CIN_007 | `3db13157fa58` | 18.0 s |
| CIN_008 | `a68a33de96f1` | 18.0 s |
| CIN_009 | `4122ab028bdd` | 18.0 s |
| CIN_010 | `4cb27d268f58` | 18.0 s |
| CIN_011 | `079526a30516` | 18.0 s |
| CIN_012 | `896d6992cd02` | 18.0 s |
| CIN_013 | `daad3b5996c9` | 18.0 s |
| CIN_015 | `404b6ab12b7b` | 18.0 s |
| CIN_016 | `be9ff6b49d0d` | 18.0 s |
| CIN_018 | `c5b9ab2bc864` | 18.0 s |
| CIN_019 | `d2d6f2992c62` | 18.0 s |
| CIN_020 | `686a63020b2f` | 18.0 s |

- Contact sheet: `Art_Source/Cinematics/Campaign_Motion/contact/<SHOT>_contact.png` (26 file)

## 4. Ghi chú kỹ thuật

- Builder có resume guard mới: output đã tồn tại và probe đúng (kích thước / số frame / thời lượng / audio) được tái dùng thay vì encode lại. Lần build đầu của lượt này bị dừng giữa chừng (tiến trình nền kết thúc sau khi xong 26 take + 19 hold slice + 2 scene take + 2 AB); lần build thứ hai tái dùng toàn bộ phần đã xong và chỉ encode 13 scene take + 13 AB còn lại, hoàn tất trong ~3 phút. Pose frame luôn render lại và hash lại, nên resume không làm sai lệch manifest.
- Không có strip sinh nào trong pack này; trường `rejectedStrips` rỗng theo đúng nghĩa (không thử tuyến sinh).
- Guardrail CIN_015_S02 (UNDERWATER_NOT_DRY) giữ nguyên: chỉ thêm bọt khí + lay rong + nhấp bát, không đổi palette.

## 5. Giới hạn / khuyết điểm

- DRAFT_POSE_ANIMATION: chuyển động ở mức storyboard (box shift 0–4 px + lớp môi trường), chưa phải final pose animation với keyframe nhân vật thật; final picture của 26 shot này không cần character lock (theo ledger), nhưng vẫn chờ art-direction lock ở vòng final.
- Chuyển động cố tình nhỏ (diff trung bình 0,2–4,8): đọc như chuyển động nhẹ/ambient, không phải diễn xuất mạnh. Shot nào cần beat mạnh hơn (vd. CIN_019_S02 cần gạt kẹt) sẽ cần pose vẽ thêm ở vòng sau.
- 3 shot thoại Ly An / người nhận thư (CIN_005_S03, CIN_009_S03, CIN_020_S03) có beat đúng đầu cửa sổ thoại nhưng người nói không hiện rõ trong khung (onscreen: null) — giống CIN_004, thoại đọc off-screen; không phải lỗi mix.
- 25 shot ưu tiên 3 vẫn là Ken Burns hold; 6 shot CIN_014/CIN_017 chưa có B take. Checkpoint 3 coi như xong phần motion làm được (26/26 shot ưu tiên 2); phần còn lại chờ character lock / sửa final-picture theo ledger.

## 6. Khối tiếp theo

WO37 M-D (whole-game score + transitions) hoặc M-E (SFX/ambience biến thể thật) hoặc M-F (VO palette/pickups/pronunciation review pack) — theo thứ tự Codex đã giao; checkpoint 3 motion đã khép phần làm được ngay. PR #119 mô tả + ACK CP3a cần luồng chính đăng (cần thẻ duyệt của chủ dự án).
