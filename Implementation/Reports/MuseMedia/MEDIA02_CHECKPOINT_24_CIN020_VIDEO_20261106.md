# MEDIA-02 CHECKPOINT 24 — CIN_020 có video: scene kết campaign + sửa lỗi title CIN_009 (Gói 30 item 7) (2026-11-06)

## Khối vừa hoàn thiện

Theo lệnh của chủ dự án ("hãy tiếp tục hoàn thiện sản xuất các khối
tiếp theo"), checkpoint này làm **CIN_020 "Thư có hồi âm"** — scene
kết của campaign, danh sách nhân vật của pack rỗng nên không bị chặn
character lock — theo đúng quy trình CP21/22/23:

1. **Sinh 3 keyframe 16:9 mức storyboard** từ prompt shot của
   Cinema Production Pack **nguyên văn**, lưu staging WebP 2048×1152
   kèm SHA + snapshot và bản ghi bàn giao
   (`cin020_keyframes_handover_20261106.md`).
2. **Dựng animated take 18 s / 3 shot** bằng Ken Burns (zoompan):
   MP4 H.264 `e358b499…` (540 frame) + OGV Theora `96035eed…`
   (502 stored frame) + poster `f8a2b447…`, không track âm thanh,
   không subtitle bake-in. Cả **7 scene đã export giờ đều có video**.

Chứng minh chuyển động đo trên MP4 (mean abs channel diff so với
keyframe): identity 5,03 / 3,72 / 6,48 (ngưỡng < 10); motion 40,98 /
41,89 / 35,25 (ngưỡng > 1,5); liên tục mid↔end 35,44 / 33,30 / 30,95
(ngưỡng > 0,5).

## Sửa lỗi phát hiện ở checkpoint 23

Khi dựng builder cho checkpoint này, phát hiện manifest keyframe
của **CIN_009 mang title sai** — "Con dấu qua phố" (title của
CIN_006) thay vì "Tiếng rừng được đáp" — do copy-paste khi nhân bản
builder ở CP23 (sceneId và export manifest vẫn đúng). Đã sửa cả ba
nơi: `build_cin009_video.py`, manifest keyframe CIN_009 trên đĩa, và
ghi chú trong runtime manifest. Validator từ nay có thêm checker
keyframe cho CIN_020; checker CIN_009 không đối chiếu title nên lỗi
này lọt lưới — đã rõ giới hạn đó.

## Keyframe theo shot (đã soi bằng mắt, khuyết điểm ghi thật)

| Shot | Nội dung khung | Khuyết điểm đã ghi |
|---|---|---|
| S01 (MEDIUM_STATIC) | Dân làng ngồi ở bàn ván đã sửa trên bến sông đọc thư đã mở; thư còn niêm phong và chiếc bát sờn trên bàn; đèn giấy mới buộc treo ở cột tre bên trái; nhà sàn bên kia sông trong nắng yên | Bát sờn đựng rau xanh nên đọc như bát ăn thay vì đồ vật trống; đèn mới buộc hơi vuông và không thắp (đúng ban ngày nhưng dễ gây hiểu nhầm). Không có chữ đọc được — đúng yêu cầu |
| S02 (DETAIL_LOCKED) | Trong nhà: dân làng ngồi bàn gỗ cạnh cửa sổ mở, tay cầm bút trên tờ giấy mới có vài nét trừu tượng đầu tiên; nghiên mực, ống bút, chồng giấy trên bàn; làng bên sông qua khung cửa | **Lệch framing:** medium shot nội thất thay vì cận cảnh chi tiết tờ giấy + bút ở bàn bờ sông. Nhân vật đội nón lá + áo xanh, khác hẳn S01 (khăn đầu + áo nâu) — đứt liên tục cùng-một-người |
| S03 (TOPDOWN_MATCH) | Nhìn thẳng từ trên xuống: bàn (bát ăn, thư hồi âm đã gấp, đũa, túi vải), dân làng ngồi bên trái quay lưng; đường làng sau hàng rào với người gánh hàng, quầy chợ, luống rau đang làm việc | Nhân vật là **biến thể ngoại hình thứ ba** (áo xanh lá, khăn trùm sẫm) — lệch liên tục xuyên shot; thư hồi âm đọc giống phong bì hiện đại; một vệt trắng mờ như hơi nước lơ lửng giữa đường |

Khuyết điểm chính của scene là **liên tục ngoại hình nhân vật**:
cùng một dân làng không tên nhưng ba shot là ba bộ trang phục/khăn
khác nhau. Đây là mục đầu tiên của đợt sửa final picture (cần
art-direction lock cho nhân vật quần chúng), đã ghi từng shot trong
keyframe manifest.

## Trạng thái GitHub

- Nhánh `muse/media-production-20261104`: nội dung ở commit ngay
  trước báo cáo này; PR #119 vẫn OPEN và HOLD theo Gói 30.

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_cin020_video.py` (mới) | Builder take CIN_020 theo mẫu CP21–23: kiểm SHA staging, keyframe 640×360 + manifest, render zoompan, kiểm frame identity/motion, export manifest. |
| `Art_Source/Cinematics/Campaign/CIN_020/keyframes_16x9/` (mới, 3 file) + `CIN020_keyframes_manifest_v1.json` | 3 keyframe storyboard + manifest framing/khuyết điểm + SHA nguồn staging. |
| `ClientGodot/assets/cinematics/CIN_020/` (mới, 6 file) | MP4 + OGV + poster + timing + SRT + export manifest. |
| `Art_Source/Cinematics/Campaign/CIN_009/CIN009_keyframes_manifest_v1.json` + `Tools/MediaProduction/Muse/build_cin009_video.py` | Sửa title sai của CP23 ("Con dấu qua phố" → "Tiếng rừng được đáp"). |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Thêm CIN_020 vào danh sách scene clip (6 → 7, cả hằng số kiểm lẫn nhãn); nhãn checkpoint 24; ghi chú runtime. |
| `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` | sceneClips 6 → 7. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Thêm `check_cin020_keyframes()`; danh sách scene + kỳ vọng số lượng 6 → 7; nhãn checkpoint 24. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Kỳ vọng sceneClips 6 → 7; nhãn checkpoint 24. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build take — PASS
`build_cin020_video.py` exit 0, ALL VERIFIED: staging SHA 3/3 khớp,
MP4 540 frame / 18,000 s, OGV đúng thời lượng, poster = keyframe
S01, frame identity/motion đạt ngưỡng (số ở trên).

### 2. Runtime delivery — PASS
`build_runtime_delivery.py` exit 0 sau khi sửa đúng hằng số đếm
scene (bản nháp đầu của lượt này chỉ đổi nhãn mà chưa đổi hằng số
`== 6` → builder tự bắt lỗi "expected 7, got 7" và đã sửa trước khi
giao): sceneClips = 7, audio giữ nguyên 570 file.

### 3. Source re-validation — PASS, 0 mismatch
`validate_media_deliveries.py` verdict PASS: keyframe CIN_020 3/3,
per-scene clips 7/7 (cả 7 có video), reel vẫn lát đúng 0–72.
JSON: `MEDIA02_CHECKPOINT_24_SOURCE_REVALIDATION_20261106.json`.

### 4. Runtime re-verify — PASS, 0 mismatch
`verify_runtime_delivery.py` verdict PASS (kỳ vọng sceneClips đã
nâng 6 → 7; lần chạy đầu bắt đúng 1 mismatch do kỳ vọng cũ).
JSON: `MEDIA02_CHECKPOINT_24_RUNTIME_REVERIFY_20261106.json`.

### 5. Scope audit — 0 vi phạm
Diff 3 chấm từ merge-base `cf17178` so với integration `f0859d0`: 892 path, tất cả nằm trong các root media policy cho phép (`Art_Source/Cinematics/`, `ClientGodot/assets/cinematics/`, `Implementation/Reports/MuseMedia/`, `Tools/MediaProduction/Muse/`…). Nội dung ở commit `bd53640`.

## Giới hạn còn lại

- Vẫn mức STORYBOARD + motion animatic Ken Burns — chưa phải final
  take diễn pose 8–12 fps.
- Đứt liên tục ngoại hình dân làng xuyên 3 shot + lệch framing S02
  là các mục đầu của đợt sửa final picture.
- Cửa sổ thoại S03 (12,5–17,5 s) giữ nguyên PROPOSED; VO nháp
  (CP17, giọng placeholder VOICE_LETTER_RECIPIENT) dài 3,000 s —
  vừa cửa sổ ở tốc độ tự nhiên.
- Checker keyframe chưa đối chiếu field title với timing JSON —
  lỗi title kiểu CP23 vẫn có thể lọt nếu tái diễn ở scene khác;
  cần nâng cấp checker ở một checkpoint QA sau.
- Sau checkpoint này, các scene campaign còn lại đều có nhân vật có
  tên trên hình (cần character lock cho final picture ở mức
  storyboard vẫn làm được từng shot) hoặc thuộc cụm P0 đã xong;
  khối lớn còn lại của Gói 30 item 7 là nhạc/SFX sáng tác thật.
