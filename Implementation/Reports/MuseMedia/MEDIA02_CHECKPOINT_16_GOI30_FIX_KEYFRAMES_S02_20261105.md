# MEDIA-02 CHECKPOINT 16 — Gói 30 fix (c): keyframe CIN_002_S02 đúng + keyframe 16:9 riêng từng shot (2026-11-05)

## Khối vừa hoàn thiện

Sửa finding 3 (lỗi hình thứ 5, P2) của review PR #119 + yêu cầu keyframe 16:9
riêng từng shot (Gói 30 item 3). Panel CIN_002_S02 cũ (tay BĂNG chạm nước,
đầu bị crop) đã được thay bằng keyframe 16:9 sinh mới độc lập: tay LÀNH
(trần, không băng) hạ xuống và DỪNG TRƯỚC mặt nước, tay băng tựa lại trên
bến, đủ đầu/mặt trong khung. Animatic rebuild v3 (MP4/OGV/poster) + bộ
keyframe 16:9 riêng 12 shot + manifest + validator mở rộng kiểm keyframe.

## Trạng thái GitHub (đọc qua public API read-only, 2026-11-05 21:40 JST)

- Issue #116: vẫn OPEN, nay 10 comment. MỚI so với CP15: comment `6657227288`
  (2026-11-05 11:49:15Z, khanhcoder97) — nghiệm thu bổ sung tại `67f0d92`:
  cuecount 20 cảnh/21 cue đã đúng; bốn panel sửa được nhận ở mức storyboard;
  chưa duyệt final picture hoặc autoplay. **CIN002S02 vẫn dùng file cũ: phải
  dùng tay lành dừng trước mặt nước, không chạm nước và giữ đủ đầu/mặt
  trong khung 16:9.** Chủ dự án cho phép chuẩn hóa TOÀN BỘ binary hiện hành
  trong đúng media roots theo `.gitattributes` owner (snapshot 24 nếu tính
  OGV — con số cũ chỉ là kết quả kiểm tại một SHA, không giới hạn quyền sửa
  lỗi). Sau đó tiếp 17 VO nháp, clip riêng từng scene và video/audio còn
  thiếu; không dừng sau việc rehash hoặc chờ xác nhận cũ.
- PR #121 đã merge vào integration `f0859d0` (2026-11-05 21:00 JST,
  `review-30-followups`): chỉ thêm 3 file review doc
  (`Muse_PR119_67f_followup.md` + OpenCode WORK30 followup) — KHÔNG đổi
  media input, timing, cue hay policy. Integration HEAD nay là `f0859d0`
  (trước là `a84ce590`). Followup review xác nhận: 4 panel CP13 "materially
  improved at storyboard level"; S02 "Unchanged… byte-identical to old
  version"; khuyến nghị HOLD toàn PR cho tới khi sửa xong shot thứ 5 +
  keyframe 16:9/clip riêng/17 VO.
- PR #119: OPEN, base nay là `f0859d0`. Head trước lượt này `509246d`.

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Art_Source/Cinematics/P0_Animatic/keyframes_16x9/keyframe_<SHOT>.png` (12 file mới) | Keyframe 16:9 riêng từng shot, 640×360 mỗi file. S02 = sinh mới (checkpoint 16); 4 shot CP13 = panel 16:9 độc lập; 7 shot còn lại = panel v1 (sheet-crop) mang sang, đã kiểm framing lại trên contact sheet. |
| `Art_Source/Cinematics/P0_Animatic/P0_keyframes_16x9_manifest_v1.json` (mới) | Manifest keyframe: SHA/size/source/framingNote từng shot; ghi rõ provenance — 7 shot v1 KHÔNG tự nhận là frame độc lập sinh mới (chỉ mức STORYBOARD). |
| `Art_Source/Cinematics/P0_Animatic/panels/panel_CIN_002_S02.png` | Panel rebuild từ sheet v3: tay lành trần trên mặt nước, tay băng tựa bến, đủ đầu/mặt. SHA mới `c60405d6…` (khác keyframe `4c5b7b35…` do resample qua sheet — đã ghi trong manifest). |
| `Art_Source/Cinematics/P0_Animatic/P0_storyboard_sheet_v3.png` | Sheet v3: chỉ ô S02 thay bằng keyframe mới; 11 panel kia + panel nghiên cứu thứ 13 byte-identical v2. SHA `4554cebb…`. |
| `Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v3.json` (mới) | Spec v3: checkpoint 16, baseSha `f0859d0`, sheet/outputs v3, `keyframesDir` + manifest, revision note, S02 `panelFix` + `panelFixVerified`. |
| `Art_Source/Cinematics/P0_Animatic/P0_animatic_outputs_v3.json` (mới) | Manifest output v3: MP4 SHA `570c78ff…`, OGV SHA `06acf54e…`, poster không đổi `ea9d4228…`. |
| `ClientGodot/assets/cinematics/P0_animatic_640x360_30fps.mp4` / `.ogv` | Animatic v3 rebuild: 72,0 s / 12 shot, MP4 H.264 2160 frame, OGV Theora 271 stored frame. |
| `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` | Tái sinh bằng builder: checkpoint 16, animatic v3, 5 panel đã sửa (4 CP13 + S02), 7 panel giữ nguyên v1. Audio/timing không đổi. |
| `Tools/MediaProduction/Muse/build_p0_keyframes.py` (mới) | Tool dựng bộ keyframe + manifest (provenance từng shot). |
| `Tools/MediaProduction/Muse/revise_p0_animatic_s02.py` (mới) | Tool paste keyframe S02 vào sheet v3 + viết spec v3 (theo mẫu CP13). |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | `ANIMATIC_EXPECTED` SHA MP4/OGV v3; nhãn checkpoint 16; ghi chú animatic v3 + keyframes. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Đọc outputs v3; nhãn checkpoint 16; base `f0859d0`; thêm `check_keyframes()` (12 keyframe: tồn tại, 640×360, byte thật, SHA khớp manifest, source hợp lệ, đủ 12 shot). |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Nhãn checkpoint 16; base `f0859d0`; `verifies` thêm checkpoint 16 (animatic v3). |

## Kiểm chứng visual (xem trực tiếp, không đoán)

Keyframe S02 sinh mới (2096×1184, resize 640×360), kiểm 2 lần:

- **Lần 1 (thử đầu, LOẠI):** tay với xuống vẫn là tay BĂNG (cả hai cẳng tay đều
  quấn băng) + đầu ngón tay chạm mặt nước, vòng gợn đồng tâm ngay dưới đầu
  ngón tay — sai cả hai điểm của finding 3. Đã phóng to vùng tay để xác nhận
  trước khi loại.
- **Lần 2 (resume sửa, CHẤP NHẬN):** cẳng tay với xuống TRẦN hoàn toàn
  (không băng); chỉ tay băng tựa trên bến (khớp questkit: cẳng tay PHẢI băng,
  tay trái lành); tay lành hạ xuống và DỪNG TRÊN mặt nước — zoom xác nhận có
  dải nước tối giữa đầu ngón tay và vệt phản chiếu/gợn mưa bên dưới, đầu
  ngón tay không phá mặt nước, không còn vòng gợn chạm; cả búi tóc + mặt đầy
  đủ trong khung, có khoảng trống phía trên đầu; chuôi kiếm gãy sau lưng còn
  nguyên.
- **Panel rebuild** (qua sheet v3 → crop → 640×360): xem lại full frame +
  zoom tay — khoảng hở vẫn còn sau resample, tay trần, tay băng tựa bến, đủ
  đầu/mặt. Đây là frame trong MP4 v3.
- **Contact sheet 12 keyframe** (xem trực tiếp): cả 12 shot chủ thể/đầu đủ
  trong khung; S03 chuông chỉ phản chiếu; S06 Ly An đúng questkit; CIN_004_S01
  đúng 1 sừng gãy + 1 sừng nguyên; CIN_004_S03 strict top-down.

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Source pack kiểm chứng lại — PASS, 0 mismatch

`MEDIA02_CHECKPOINT_16_SOURCE_REVALIDATION_20261105.json`
(base `f0859d0`):

- Audio nguồn: 1093 file (22 nhạc/ambience + 173 SFX/UI × 3 variant × 2 +
  11 stem P0) khớp byte/sha/codec/48 kHz/kênh/thời lượng.
- Timing + SRT: 20/20 cảnh, timing dialogues 21 == SRT cues 21 ==
  runtime manifest 21.
- Animatic: 12/12 panel khớp sha, MP4/OGV 640×360 72 s; VO P0: 3/3 take
  khớp sha/thời lượng và vừa cửa sổ.
- **Keyframes: 12/12 khớp manifest** (tồn tại, 640×360, byte thật, SHA
  khớp, source hợp lệ, đủ 12 shot).
- Ghi chú duy nhất (đã biết): OGV `avg_frame_rate 0/0` do Theora gộp frame
  giữ nguyên — thời lượng vẫn 72 s, không phải lỗi.

### 2. Runtime delivery kiểm chứng lại — PASS, 0 mismatch

`MEDIA02_CHECKPOINT_16_RUNTIME_REVERIFY_20261105.json`:

| Nhóm | Số file kiểm | Kết quả |
|---|---|---|
| Audio runtime (22 nhạc/ambience + 519 SFX/UI + 4 VO P0) | 545 | khớp manifest, 0 mismatch |
| Animatic P0 v3 (MP4 + OGV + poster) | 3 | khớp sha, 0 mismatch |
| Timing JSON 20 cảnh | 20 | khớp sha, 0 mismatch |
| SRT 20 cảnh | 20 | khớp sha, 0 mismatch |

### 3. Runtime builder — ALL VERIFIED

`build_runtime_delivery.py`: audio 545, animatic 3 file verified,
20 scene (40 timing+SRT). Audio manifest tái sinh byte-identical
(không đổi nội dung); chỉ cine manifest đổi (checkpoint 16 + animatic v3).

## Sự cố trong lượt và cách khắc phục (ghi rõ, không giấu)

Lần sinh keyframe S02 đầu tiên sai cả hai điểm (tay băng với xuống + chạm
nước). Không dùng file đó: đã xem trực tiếp + zoom tay để xác nhận lỗi, rồi
sửa bằng 1 lần resume với chỉ dẫn tách bạch (tay với xuống phải TRẦN;
nâng tay lên khỏi mặt nước, bỏ vòng gợn dưới đầu ngón tay). Lần 2 đạt cả
hai điểm, giữ nguyên framing/đầu/kiếm/bến/mưa. Tổng 2 lần gọi sinh ảnh.

## Giới hạn / khuyết điểm (ghi rõ, không giấu)

- **Khoảng hở tay–nước hẹp:** ở 640×360 chỉ vài px — đọc rõ là "lơ lửng"
  khi zoom, nhưng ở cỡ thumbnail có thể đọc nhầm là chạm. Final take nên
  nới khoảng hở rõ hơn; ở mức storyboard hiện tại đã đủ phân biệt với bản
  v1 (tay phá mặt nước + vòng gợn chạm).
- **7/12 keyframe vẫn là panel sheet-crop v1** (center-crop từ sheet):
  manifest ghi rõ source `panel-sheet-crop-v1` và chỉ nhận mức STORYBOARD,
  KHÔNG tự nhận là frame độc lập sinh mới. Keyframe độc lập thật cho 7 shot
  này vẫn là việc tương lai (campaign animated takes).
- **Chưa xuất clip riêng từng scene** (Gói 30 item 6) và **chưa viết lại mô
  tả PR #119** (item 8) — mô tả PR cần thẻ duyệt của chủ dự án; ghi rõ để
  luồng chính xử lý, lượt này không treo chờ. ACK comment checkpoint 16
  trên issue #116 cũng cần thẻ duyệt — ghi rõ để luồng chính xử lý.
- Số lượng thực tế giữ nguyên: 541/545 audio runtime là port Codex PackV1,
  chỉ 4 file VO mới; campaign có timing/SRT chứ chưa có 20 video hoàn
  chỉnh; video duy nhất vẫn là reel 72 s review/gallery, không tự chạy
  làm opening. Loudness/true-peak không đo lại lượt này (lấy CP02/04/07/08).
  Không mix PASS, không nghe thử bằng tai (D2). Cửa sổ campaign vẫn
  PROPOSED cho final (D1 chỉ mở VO nháp).

## Trạng thái repo

- Nhánh media: commit fix `b7d83f0` ĐÃ PUSH (ls-remote xác nhận; scope audit
  727 paths, 0 violations, base integration HEAD `f0859d0`). PR #119 nay có
  24 commit.
- Commit này 27 file: 12 keyframe + manifest, sheet/spec/outputs v3, panel
  S02, MP4/OGV v3, cine manifest tái sinh, 2 script mới + 3 script cập nhật,
  2 JSON kiểm chứng. 5 object LFS mới đã upload (6,9 MB); 11 keyframe còn
  lại tái dùng blob đã có trên server. Không đụng audio, timing, SRT hay
  11 panel còn lại (byte-identical).

## Kiểm chứng remote sau push (fresh clone từ github.com)

- Clone mới nhánh media tại `b7d83f0`, `git lfs install` local,
  `reset --hard`: LFS tải 1726/1726 object (283,3 MB). OGV ngay sau checkout
  vẫn là pointer text (đúng caveat: nhánh media chưa có quy tắc `*.ogv`);
  keyframe S02 + panel PNG + MP4 là byte thật.
- `git lfs fetch --include` cho OGV: object `06acf54e…` (1.852.526 byte) CÓ
  trên server, tải về store thành công; smudge tay ra đúng SHA.
- Runtime verifier trên remote clone: lần đầu đúng 1 mismatch (OGV pointer);
  sau khi đặt byte OGV tải từ server vào worktree: **PASS, 0 mismatch**
  (545 audio, 3 animatic, 20 scene, 20 timing, 20 SRT).
- Source validator trên remote clone: lần đầu 1 mismatch (ffprobe OGV
  pointer); sau khi khôi phục OGV: **PASS, 0 mismatch** (1093 audio,
  20 scene, 21 cue, 12 panel, 12 keyframe, 3 VO take).
- Clone kiểm chứng đã xóa sau khi xong (`/home/hatch/.cp16-fresh-remote`).

## Khối tiếp theo

1. VO nháp campaign 17 cue (D1 đã mở; lưu ý CIN020 dùng
   `VOICE_LETTER_RECIPIENT`, vai giọng cinematic, không NPC gameplay).
2. Xuất clip riêng từng scene (MP4/OGV/poster/SRT/timing/hash) + viết lại
   mô tả PR #119 theo số thực (cần thẻ duyệt).
3. Campaign video: animated takes thật (không còn là reel panel-hold).
