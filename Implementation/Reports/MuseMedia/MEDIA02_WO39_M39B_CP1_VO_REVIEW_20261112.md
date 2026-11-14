# MEDIA-02 Checkpoint — WO39 M39-B CP1: level-matched A/B review comparison of the voice palette

Date: 2026-11-12 (JST). Branch: `muse/media-production-20261104`.
Integration baseline: `f3db6b3` (PR #131 merged; was `9ac73dc`).
PR #119 stays HOLD; Muse does not self-merge. Production OFF.

## 1. Vì sao khối này, vì sao bây giờ

Gói 39 M39-B (Codex, issue #116 comment 6815238814; disposition
`Implementation/Work_Orders/39_HANDOFF_DISPOSITION_AND_NEXT_DELIVERIES_20261112.md`,
merged to integration as PR #131 @ `f3db6b3`) giao đúng một việc trong
phạm vi: "được làm level-matched review comparison trên palette hiện
có, không thay runtime/commit final voice". Chưa có lựa chọn casting
nên originals vẫn giữ; M-F CP2 (re-mix theo palette) vẫn chờ quyết
chọn giọng. Khối này làm cho lựa chọn đó nghe được: cùng một câu,
hai giọng, cùng một mức loudness — đạo diễn so giọng, không so volume.

## 2. Deliverable

20 cặp A/B, 40 render gain-only, tổng 23.433.376 B:

| | |
|---|---|
| A — canonical | take đã nhúng trong mix (Helio/Aria) |
| B — palette | pickup M-F CP1, giọng hư cấu riêng theo vai |
| Render | `Art_Source/Audio/Muse/VO/PALETTE_REVIEW_M39B_v1/` — 40 WAV pcm_s16le 48 kHz mono, cùng số mẫu với nguồn |
| Manifest | `Implementation/Content/Audio/Deliveries/VO_PALETTE_REVIEW_M39B_v1.json` |
| Playlist | `Implementation/Reports/MuseMedia/vo_palette_review_m39b_playlist.txt` (M3U, 40 entry) |
| Builder | `Tools/MediaProduction/Muse/build_vo_palette_review_m39b_cp1.py` |
| Validator | `Tools/MediaProduction/Muse/check_vo_palette_review_m39b_cp1_v1.py` |

14 cặp dialogue + 1 alternate (CIN006_ALT_T01, Q3) + 5 narration
(CIN000 SEG01–05). Ly An KHÔNG có cặp: giọng Aria giữ nguyên ở
M-F CP1, không có pickup để so.

## 3. Phương pháp (đo từ byte thật, cùng cách đo M-F CP1)

- Nguồn re-hash 40/40 khớp manifest M-F CP1
  (`VO_PALETTE_PICKUPS_pack_v1.json`); pre LUFS/TP đo lại bằng
  ffprobe + ffmpeg loudnorm, khớp manifest trong ±0,15.
- Chỉnh gain-only bằng ffmpeg `volume` (không EQ/compression/
  limiting/tổng hợp lại). Mục tiêu cặp: −23,00 LUFS integrated,
  trần true peak −1,00 dBTP.
- Hai cặp chạm trần nên mức cặp thấp hơn −23,00 (quy tắc
  min(−23,00; mức cao nhất cả hai phía đạt được không vượt trần)):
  CIN000_SEG02 → −23,62 (B pickup cần +5,17 dB, TP sau −1,00) và
  CIN000_SEG03 → −23,23 (A canonical TP −0,26, chỉ chịu được −0,74 dB).

## 4. Đo đạc (từ byte thật, validator độc lập 788/788 PASS)

- Trước chỉnh: canonical −19,59…−25,38 LUFS; palette −20,17…−30,13
  LUFS (narrator History chênh tới −8,41 LU so với canonical Helio
  cùng đoạn — đúng vấn đề M39-B yêu cầu gỡ).
- Sau chỉnh: mọi render trong ±0,02 LU so với mức cặp; chênh A/B
  trong cặp tối đa 0,02 LU; TP sau cao nhất −1,00 dBTP (đúng trần,
  2 render: SEG02 B, SEG03 A), render còn lại ≤ −1,45 dBTP.
- Duration giữ nguyên từng mẫu (sai số 0,000 s); format giữ nguyên
  pcm_s16le/48 kHz/mono; gain áp dụng khác 0 trên cả 40 render.
- Gain lớn nhất: +7,13 dB (SEG01 B, −30,13 → −23,00); gain âm lớn
  nhất: −3,41 dB (CIN020_S03 A, −19,59 → −23,00).
- Validator kiểm lại độc lập: re-hash 40 nguồn + 40 render, đo lại
  pre/post, số học gain, quy tắc mức cặp + cờ ceiling-limited,
  trần TP, duration, format, playlist đủ 40 entry duy nhất —
  **788/788 PASS, 0 failure**.

## 5. Giới hạn / khuyết điểm (ghi thật)

- DRAFT / NOT_AUDITIONED — chưa ai nghe tai; pass/fail thuộc về
  người nghe (đạo diễn/Codex), không phải con số.
- Không thay runtime, mix, timing, SRT hay pronunciation table;
  runtime audio giữ 783 file. Không commit final voice.
- CIN018_S03 (người chơi) vẫn VOICE_PLACEHOLDER_ONLY; CIN020_S03
  (người nhận thư) vẫn placeholder trung tính ElvenWizard — không
  phải quyết định casting/giới tính.
- Ba overrun canonical giữ nguyên (CIN_005_S03 +0,160 s,
  CIN_018_S03 +0,280 s, CIN_006_S03 +0,520 s); pack này không re-mix.
- Hai render chạm đúng trần −1,00 dBTP (SEG02 B, SEG03 A): đúng luật
  đã đặt, không clip, nhưng không còn headroom TP — ghi rõ để đạo
  diễn biết khi nghe to.
- Integration đã chuyển `9ac73dc` → `f3db6b3` (PR #131 merged) trong
  lúc làm khối này; cặp payload gộp 6 khối chuẩn bị trước đó phải
  làm mới theo head mới trước khi đăng (xem mục 6).

## 6. Sau khối này

- Cặp payload gộp (M-B CP3 + M-C CP3b + M-E CP2a + M-C CP3c +
  M39-A CP1 + M39-A CP2) cần làm mới thành 7 khối, gồm khối này:
  integration mới `f3db6b3`, merge-tree mới, mergeable đọc lại tại
  head mới, PR #131 đã merged (không còn "open"). Chưa đăng — chờ
  thẻ duyệt của chủ dự án ở luồng chính.
- Khối tiếp theo: M-F CP2 khi có quyết chọn giọng; 32 shot chờ
  character lock; full OGV 720p deferred (Gói 39).
