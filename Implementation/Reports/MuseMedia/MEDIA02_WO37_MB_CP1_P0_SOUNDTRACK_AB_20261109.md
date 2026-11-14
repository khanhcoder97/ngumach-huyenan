# MEDIA-02 WO37 M-B CP1 — P0 soundtrack A/B (v1 vs v2 vs v3) (2026-11-09)

Đóng phần còn lại của WO37 big checkpoint 2 (xem M-C CP2 §8 và CP54 "Next":
"soundtrack A/B for P0 (v1 vs v2 vs v3)"). Big checkpoint 1 (21/21 soundtrack
nhúng) đã xong ở CP54; checkpoint 2 còn lại đúng khối này.

## Thiết kế A/B

Cùng một hình candidate-B trong cả ba reel — video stream copy y nguyên từ
reel M38-A (`P0_candidate_review_72s_640x360_30fps.mp4`, sha
`a9ae424cd95d…`), chỉ soundtrack khác nhau:

| Version | Soundtrack | Nguồn |
|---|---|---|
| v1 | Ported PackV1 music + ambience + stinger | Checkpoint 20 |
| v2 | Composed music + stinger, ambience ported | Checkpoint 29 |
| v3 | Fully composed music + stinger + ambience | Checkpoint 31 |

VO giống hệt nhau ở cả ba bản (cùng take draft CP04, cùng cửa sổ, cùng
gain/ducking theo verdict mix v2/v3) nên A/B cô lập đúng tính cách
nhạc/ambience: v1↔v2 = thay nhạc + stinger; v2↔v3 = thay ambience.

## Deliverable

`Art_Source/Cinematics/P0_Motion/soundtrack_ab/`:

| Reel | Bytes | SHA256 | Dur | Loudness |
|---|---|---|---|---|
| `P0_soundtrack_v1_72s_640x360_30fps.mp4` | 2.996.738 | `311d83c7625f…` | 72,021 s | −22,55 LUFS / −1,49 dBTP |
| `P0_soundtrack_v2_72s_640x360_30fps.mp4` | 2.996.180 | `1cdac5293a09…` | 72,021 s | −22,65 LUFS / −1,52 dBTP |
| `P0_soundtrack_v3_72s_640x360_30fps.mp4` | 2.990.234 | `f96c7811872e…` | 72,021 s | −22,39 LUFS / −1,65 dBTP |

- Video cả ba reel: H.264 640×360 30 fps, stream MD5 đồng nhất
  `1fec5523e481d2279d3a8dc8a2957e2c` (copy từ reel candidate M38-A).
- Audio: AAC 192k 48 kHz stereo, encode từ 3 master WAV 72 s (SHA khớp
  manifest v1/v2/v3; đo lại master khớp CP9 đúng từng số: v1 −22,66/−1,46,
  v2 −22,72/−1,51, v3 −22,49/−1,66).
- Manifest so sánh: `P0_SOUNDTRACK_AB_v1.json` (cùng thư mục).
- Playlist nghe: `Implementation/Reports/MuseMedia/p0_soundtrack_ab_playlist.txt`
  (M3U, 3 mục, đường dẫn tương đối).

## So sánh đo từ byte thật

Loudness từng scene (LUFS tích hợp / true peak dBTP):

| Scene | v1 | v2 | v3 |
|---|---|---|---|
| CIN_001 (36 s) | −22,30 / −1,49 | −21,07 / −1,52 | −21,04 / −1,65 |
| CIN_002 (18 s) | −21,21 / −3,95 | −22,72 / −4,27 | −22,50 / −4,26 |
| CIN_004 (18 s) | −25,52 / −7,94 | −26,62 / −8,34 | −26,79 / −8,27 |

Đọc được: nhạc sáng tác nóng hơn ported ~1,2 LUFS ở CIN_001 nhưng lặng hơn
~1,1–1,5 LUFS ở CIN_002/CIN_004 — chênh lệch có hướng theo scene, không
phải một bản to hơn toàn cục. Đây là số đo, không phải verdict nghe.

RMS cửa sổ thoại (dBFS, đo trên reel — VO có nghe rõ trên nền không):

| Cửa sổ khóa | v1 | v2 | v3 |
|---|---|---|---|
| CIN_001_S05 [24,8–28,5] | −37,42 / peak −27,19 | −38,67 / −28,62 | −38,72 / −30,56 |
| CIN_002_S02 [43,0–47,0] | −39,71 / −31,52 | −39,72 / −31,52 | −37,04 / −32,01 |
| CIN_004_S02 [61,5–63,5] | −29,52 / −23,02 | −29,79 / −21,74 | −28,96 / −20,98 |

RMS các cửa sổ chênh nhau ≤ ~1,3 dB giữa các bản — nhất quán với VO giống
hệt + ducking giống hệt; khác biệt còn lại là nền nhạc/ambience dưới VO.

Chênh lệch sóng giữa các master (tỉ lệ diff-RMS / tương quan Pearson):

| Cặp | Toàn 72 s | CIN_001 | CIN_002 | CIN_004 |
|---|---|---|---|---|
| v1–v2 | 0,671 / 0,761 | 0,591 / 0,815 | 0,611 / 0,806 | 0,906 / 0,548 |
| v1–v3 | 0,732 / 0,713 | 0,655 / 0,771 | 0,682 / 0,757 | 0,959 / 0,492 |
| v2–v3 | 0,318 / 0,949 | 0,305 / 0,953 | 0,314 / 0,951 | 0,357 / 0,936 |

Đúng như thiết kế thay thế: v1↔v2 và v1↔v3 khác nhiều (thay nhạc/stinger),
v2↔v3 khác ít (chỉ thay ambience, tương quan 0,95). Trong cửa sổ thoại,
tương quan v1↔v2 ở CIN_001_S05 là 0,9978 (VO gần như đồng nhất, nền chênh
rất ít); ở CIN_002_S02/CIN_004_S02 tương quan ~0,86–0,89 (nền dưới VO khác
rõ hơn). Toàn bộ 21 hàng diff (3 cặp × 7 phạm vi) có trong manifest.

Đối chiếu v3: reel v3 của khối này đo −22,39 LUFS so với reel candidate
M38-A −22,47 LUFS (lệch +0,08 LUFS, true peak 0,0 dB) — cùng master WAV v3,
cùng thông số AAC 192k; lệch nhỏ là phương sai lần encode so với bản CP2/
M38-A, không phải khác nguồn.

## Kiểm chứng

- Checker độc lập `Tools/MediaProduction/Muse/check_p0_soundtrack_ab_v1.py`:
  **PASS 32/32** — hash lại nguồn (reel candidate + 3 master WAV) + 3 reel,
  probe hình/tiếng từng reel, MD5 video stream đồng nhất cả ba, đo lại
  loudness toàn reel + 9 đoạn scene + RMS cửa sổ CIN_001_S05, đối chiếu
  candidate reel, bảng diff 21 hàng, playlist resolve đủ 3 mục, runtime
  không đổi (ClientGodot/ 0 dòng thay đổi). Kết quả:
  `MEDIA02_WO37_MB_CP1_VALIDATION_20261109.json`.
- Builder: `Tools/MediaProduction/Muse/build_p0_soundtrack_ab.py`.

Hai lỗi đã sửa trong lúc chạy (không giấu):
1. `-shortest` khi mux video copy + audio encode mới làm rớt 3 frame cuối
   (2157/2160 frame, video còn 71,9 s) — đổi sang `apad + -t 72.021333`
   (21 ms đuôi là silence số, video giữ đủ 2160 frame, MD5 khớp candidate).
2. Playlist ghi sai độ sâu đường dẫn (`../../` thay vì `../../../`) nên
   3 mục không resolve — đã sửa builder, chạy lại, checker PASS.

## Giới hạn / bước tiếp theo

- **DRAFT / NOT_AUDITIONED**: gói này là công cụ để nghe và chọn, không phải
  verdict — không bản mix nào được chọn làm canonical ở đây; quyết chọn
  v1/v2/v3 thuộc Codex/director. Loudness/RMS/diff là số đo, không phải
  mix PASS.
- Runtime không đổi: không file nào dưới `ClientGodot/` bị chạm; reel v3
  trong gói này KHÔNG thay reel candidate M38-A, càng không thay runtime A.
- Khối tiếp theo: M-F CP2 (re-mix theo palette) và M-E CP2 (composed SFX)
  vẫn chờ quyết director/Codex; motion 32 shot lock-required vẫn chờ
  character lock. Mô tả PR #119 + ACK khối này cần luồng chính (thẻ duyệt
  của chủ dự án cho GitHub writes).
- PR #119 vẫn HOLD (Muse không tự merge; Codex review/merge).
