# MEDIA-02 CHECKPOINT 19 — VO nháp CIN_006: đủ 21/21 cửa sổ thoại D1 (2026-11-06)

## Khối vừa hoàn thiện

Tổng hợp VO nháp cho CIN_006 "Con dấu qua phố" — cửa sổ thoại cuối cùng
trong 21 cửa sổ được D1 duyệt sản xuất VO nháp (checkpoint 04 làm 3 cue P0,
checkpoint 17 làm 17 cue campaign; CIN_006 là cue thứ 21 còn thiếu).

| Take | Loại | Thời lượng đo thật | Cửa sổ | Kết quả |
|---|---|---|---|---|
| CIN_006_S03 (Hạ Mặc, canonical) | canonical, trong SRT | 5,520 s | 12,5–17,5 s (5,0 s) | **OVERRUN +0,520 s** |
| CIN_006_ALT_T01 (v1-alt) | alternate take riêng takeId | 3,000 s | không gán cửa sổ | NO_WINDOW_ASSIGNED |
| Timeline VO scene | chỉ take canonical @12,5 s | 18,020 s | scene 18,0 s | đuôi tràn 0,020 s, không cắt take |

- Canonical: WAV 48 kHz mono, −21,96 LUFS / −3,42 dBTP. Đọc tốc độ 100%
  (D1 cấm tăng tốc giọng để vừa cửa sổ) — tràn 0,520 s là **phát hiện cho
  đạo diễn** giống hai ca campaign: nới cửa sổ hoặc rút gọn lời thoại,
  không tự ý sửa canon. Toàn game hiện có 3 take OVERRUN chờ quyết định:
  CIN_005_S03 +0,160 s, CIN_018_S03 +0,280 s, CIN_006_S03 +0,520 s.
- Alternate take giữ đúng DEC-MEDIA-P0 Q3: takeId/version riêng
  (`CIN_006_ALT_T01` / `v1-alt`), **không** thay canonical, **không** nằm
  trong SRT (validator kiểm chứng chiều này), **không** đặt lên timeline.
  Nguồn đạo diễn không cast riêng bản đọc alternate; S03 là beat của
  Hạ Mặc nên bản nháp đọc cùng giọng hư cấu (Helio) — ghi rõ trong
  manifest là giả định nháp, không phải quyết định casting.
- Giọng: `avocado_v2:MAI_03` (Helio, giọng hệ thống hư cấu) — nhất quán
  casting Hạ Mặc ở checkpoint 17 (CIN_011/012/016). Giới hạn cũ giữ
  nguyên: các nhân vật nam dùng chung một giọng sản xuất trong bản nháp,
  chưa phân giọng; casting phân giọng là quyết định của đạo diễn.
- Timeline 18,020 s: chỉ chứa take canonical đặt tại 12,5 s; phần tràn
  0,020 s qua cuối scene được giữ nguyên, không cắt cụt câu (manifest
  ghi `sceneSeconds` vs `durationSeconds` + `overrunTailSeconds`).

## Trạng thái GitHub

- Nhánh `muse/media-production-20261104`: nội dung ở commit `2681b4b`;
  báo cáo này ở commit ngay sau. PR #119 vẫn OPEN và HOLD theo Gói 30.
- ACK các checkpoint trên issue #116 và viết lại mô tả PR #119 (Gói 30
  item 8) vẫn chờ thẻ duyệt của chủ dự án ở luồng chính; lượt này không
  tự ghi GitHub ngoài việc push nhánh media theo quy trình đã duyệt.

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_cin006_vo.py` (mới) | Builder VO CIN_006: parse cue canonical + alternate take từ timing JSON, đối chiếu SRT hai chiều (canonical phải có trong SRT, alt tuyệt đối không), convert WAV 48 kHz mono, đo duration/loudness byte thật, lắp timeline chỉ chứa canonical, tràn thì kéo dài timeline đúng phần đuôi thay vì cắt take. |
| `Art_Source/Audio/Muse/VO/CIN006_DRAFT/` (mới, 6 file) | 2 WAV take + 2 MP3 raw TTS + timeline WAV + `CIN006_VO_manifest_v1.json` (WAV/MP3 qua LFS theo `.gitattributes`). |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Thêm mục 3c: copy 3 file VO CIN_006 vào `ClientGodot/assets/audio/vo/cin006/` kèm kiểm chứng sha/size/duration; nhãn checkpoint 19 + ghi chú Q3 trong manifest runtime. |
| `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json` | 566 file (563 → 566; VO 22 → 25); thêm 3 entry VO CIN_006. |
| `ClientGodot/assets/audio/vo/cin006/` (mới, 3 file) | 2 WAV take + timeline WAV, SHA khớp manifest nguồn. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Thêm `check_cin006_vo()` (byte thật + SRT hai chiều + takeId/cửa sổ của alt take + timeline theo manifest); nhãn checkpoint 19. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Nhãn checkpoint 19; kiểm lại toàn bộ runtime theo manifest mới. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build VO CIN_006 — PASS
`build_cin006_vo.py` exit 0: canonical 5,5200 s / OVERRUN (slack −0,5200 s)
−21,96 LUFS / −3,42 dBTP; alt 3,0000 s −22,37 LUFS / −5,54 dBTP;
timeline 18,0200 s (đuôi tràn 0,0200 s). Kiểm silence: WAV canonical có
khoảng lặng giữa hai câu tại 1,98–2,37 s (đúng dấu chấm), tiếng nói chạy
tới cuối file — không bị cắt cụt.

### 2. Runtime delivery — PASS
`build_runtime_delivery.py` exit 0: audio manifest `totalFiles` 566
(22 music/ambience + 519 SFX/UI variants + 25 VO), 3 file CIN_006 qua đủ
4 cổng kiểm chứng (byte thật, sha256, size, duration ±0,02 s);
cinematics không đổi (CIN_006 vẫn `PENDING_PANELS_NO_STORYBOARD`).

### 3. Source re-validation — PASS, 0 mismatch
`validate_media_deliveries.py` verdict PASS: CIN_006 VO 2/2 take
(canonical fit OVERRUN ghi ở `windowFit`, không phải mismatch byte);
campaign VO 17/17 (15 FITS / 2 OVERRUN cũ); 21 cue timing == SRT ==
runtime manifest. JSON: `MEDIA02_CHECKPOINT_19_SOURCE_REVALIDATION_20261106.json`.

### 4. Runtime re-verify — PASS, 0 mismatch
`verify_runtime_delivery.py` verdict PASS: counts khớp manifest
(22/519/25), campaign totals 20 scene / 63 shot / 378 s / 21 cue.
JSON: `MEDIA02_CHECKPOINT_19_RUNTIME_REVERIFY_20261106.json`.

### 5. Scope audit — 0 vi phạm
Diff 3 chấm từ merge-base `cf17178` so với integration `f0859d0`:
826 path, tất cả nằm trong các root media policy cho phép
(`Art_Source/Audio/Muse/`, `ClientGodot/assets/audio/`,
`Implementation/Reports/MuseMedia/`, `Tools/MediaProduction/Muse/`…).

## Giới hạn còn lại

- Vẫn DRAFT_NOT_FINAL_VO: TTS hư cấu, chưa nghe tai, chưa kiểm phát âm
  bằng người bản ngữ, chưa phải mix PASS; stem VO tách riêng.
- Cửa sổ CIN_006_S03 vẫn PROPOSED_ANIMATIC_PLACEMENT (D1 chỉ duyệt cho
  sản xuất VO nháp, không phải khóa hình/mix).
- 3 take OVERRUN (CIN_005_S03 +0,160 s, CIN_018_S03 +0,280 s,
  CIN_006_S03 +0,520 s) chờ quyết định đạo diễn: nới cửa sổ hoặc rút
  gọn lời thoại.
- CIN_006 vẫn chưa có video (chưa có panel storyboard) — khối video
  campaign thuộc Gói 30 item 7 / M3, làm tiếp sau.
