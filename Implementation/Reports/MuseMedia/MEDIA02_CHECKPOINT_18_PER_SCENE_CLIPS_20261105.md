# MEDIA-02 CHECKPOINT 18 — Xuất clip riêng từng scene P0 (Gói 30 item 6) (2026-11-05)

## Khối vừa hoàn thiện

Xuất mỗi scene P0 thành clip riêng, thay cho việc chỉ có reel 72 s duy nhất.
Reel 72 s từ nay chỉ là bản review/gallery — **không** tự chạy làm opening;
đơn vị runtime là clip từng scene (Gói 30 item 6 / review PR #119).

| Scene | Video | Thời lượng | MP4 (H.264) | OGV (Theora) | Poster |
|---|---|---|---|---|---|
| CIN_001 "Nước không soi bóng" | có | 36,0 s / 1080 frame | `fb9cbaf4…` (330.742 B) | `020d3b69…` (915.569 B, 171 stored frame) | S01 |
| CIN_002 "Âm cuối dưới nước" | có | 18,0 s / 540 frame | `5eca0abd…` (156.427 B) | xem manifest | S01 |
| CIN_004 "Vết đau của linh thú" | có | 18,0 s / 540 frame | `f491a39c…` (209.135 B) | xem manifest | S01 |
| CIN_006 "Con dấu qua phố" | **không** — chưa có panel storyboard | 18,0 s (timing + SRT) | — | — | — |

Mỗi thư mục scene `ClientGodot/assets/cinematics/<SCENE>/` chứa MP4 + OGV +
poster + timing JSON + SRT + `scene_export_manifest_v1.json` (SHA/size/
duration/frames + reel offset + shot list rebased về 0). CIN_006 chỉ có
timing + SRT + manifest ghi `PENDING_PANELS_NO_STORYBOARD` — không bịa
video từ frame rỗng hay tone-generator. Thời gian scene-local bắt đầu từ 0;
SRT đã là scene-local từ checkpoint 01/05 nên chỉ copy, không rebase.

## Trạng thái GitHub (đọc qua connector read-only, 2026-11-05 23:40 JST)

- Issue #116: vẫn OPEN. Không đọc được comment mới qua connector read-only
  trong lượt này (`issue_read`/`pull_request_read` không nằm trong tập read
  được duyệt — cần `call-tool` kèm thẻ duyệt; không treo chờ). Nội dung
  issue body không đổi; chỉ đạo mới nhất đã biết vẫn là comment
  `6657227288` (chủ dự án, 2026-11-05 11:49:15Z): sau 17 VO nháp thì làm
  "clip riêng từng scene và video/audio còn thiếu" — đúng khối này.
- PR #119: OPEN, head `b96cff3` (checkpoint 17). Base nay là `f0859d0`
  (PR #121 đã merge). Mô tả PR vẫn cũ (ghi head `1db3f23`, chỉ tới CP07) —
  **viết lại mô tả PR cần ghi qua GitHub connector kèm thẻ duyệt của chủ dự
  án, để luồng chính xử lý; lượt chạy này không tự ghi.**
- Integration HEAD `f0859d0` không đổi kể từ CP16; media input không đổi.

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_p0_scene_clips.py` (mới) | Builder xuất clip từng scene từ panel v3 + copy timing/SRT + manifest từng scene; kiểm ffprobe + frame-identity (frame đầu/cuối giải mã so panel). |
| `ClientGodot/assets/cinematics/CIN_001/` (mới, 6 file) | MP4 36 s/1080f + OGV + poster + timing + SRT + export manifest. Reel offset 0–36 s. |
| `ClientGodot/assets/cinematics/CIN_002/` (mới, 6 file) | MP4 18 s/540f + OGV + poster + timing + SRT + export manifest. Reel offset 36–54 s. |
| `ClientGodot/assets/cinematics/CIN_004/` (mới, 6 file) | MP4 18 s/540f + OGV + poster + timing + SRT + export manifest. Reel offset 54–72 s. |
| `ClientGodot/assets/cinematics/CIN_006/` (mới, 3 file) | Timing + SRT + export manifest (`PENDING_PANELS_NO_STORYBOARD`, không video). |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Thêm mục 6: kiểm sceneClips theo export manifest + ghi `sceneClips` vào `RUNTIME_CINEMATICS_manifest_v1.json`; nhãn checkpoint 18. |
| `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` | Thêm `sceneClips` (4 scene); animatic/timing/audio không đổi. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Thêm `check_scene_clips()` (4/4 scene; reel tile 0–72 đúng; runtime manifest phải khớp export manifest từng file); nhãn checkpoint 18. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Kiểm thêm `sceneClips` trong runtime manifest (4 clip, 17 file); nhãn checkpoint 18. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build clip — PASS
`build_p0_scene_clips.py` exit 0: 3 clip video + 1 export timing/SRT.
Frame-identity (frame đầu/cuối giải mã so panel gốc): CIN_001 2,46/2,46;
CIN_002/CIN_004 đều < 10 (ngưỡng; nhiễu lossy ~1–3, sai panel sẽ ~30+).
Theora: stored frame 171/61/45 (panel hold collapse — đúng quy tắc CP03,
không phải lỗi; duration mới là kiểm chuẩn, avg_frame_rate 0/0 như reel).

### 2. Source pack kiểm chứng lại — PASS, 0 mismatch
`MEDIA02_CHECKPOINT_18_SOURCE_REVALIDATION_20261105.json`: audio 1093 file,
timing 20 scene / 21 dialogue / 21 SRT cue, panel 12/12, keyframe 12/12,
VO P0 3 take, VO campaign 17 take (15 FITS / 2 OVERRUN — finding của đạo
diễn, không phải mismatch byte), **scene clip 4/4 (3 có video)**.

### 3. Runtime re-verify — PASS, 0 mismatch
`MEDIA02_CHECKPOINT_18_RUNTIME_REVERIFY_20261105.json`: audio runtime
563/563, animatic 3, timing 20, SRT 20, **scene clip 4 clip / 17 file**.

### 4. Scope audit
`Tools/Coordination/check_agent_scope.py` (base `f0859d0`, head `385d615`,
branch `muse/media-production-20261104`): **812 changed paths, 0 violations**.

## Giới hạn / khuyết điểm

- CIN_006 chưa có clip video: chưa từng được storyboard vào reel P0
  (checkpoint 05 chỉ timing). Clip video CIN_006 chờ panel — timing/audio/
  subtitle không bị chặn.
- Clip vẫn là storyboard panel-hold (mức STORYBOARD, chưa phải final
  picture); character keyframe vẫn chờ lock như các checkpoint trước.
- Chỉ CIN_001_S05 (24,8–28,5 s, bản B) là DECIDED; các cửa sổ thoại còn
  lại vẫn PROPOSED.
- PR #119 mô tả vẫn cũ (tới CP07) — cần chủ dự án duyệt thẻ ghi connector
  để viết lại; lượt này chưa ghi.
- Không nghe tai, không mix PASS; không kiểm wiring Godot (việc của Codex).

## Khối tiếp theo

Viết lại mô tả PR #119 (cần thẻ duyệt chủ dự án — luồng chính xử lý) +
M8 QA liên tục sau mỗi lần integration merge; sau đó video campaign với
motion thật cho các scene còn lại (M3) theo thứ tự sẵn sàng.
