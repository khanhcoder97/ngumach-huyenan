# MEDIA-02 CHECKPOINT 17 — VO dự thảo campaign (17 câu)

- Ngày: 2026-11-05 (lượt chạy định kỳ ~22:40 JST)
- Nhánh: `muse/media-production-20261104`, base integration `f0859d0`
  (PR #121 đã merge; kiểm lại bằng API công khai + `git fetch` trong lượt này)
- Quyết định áp dụng: DEC-MEDIA-P0-20261105 + D1 (Gói 30 item 5: 21 cửa sổ
  thoại được duyệt sản xuất VO NHÁP; không đổi canon, không tăng tốc giọng
  để vừa cửa sổ); CIN_020 dùng giọng vai `VOICE_LETTER_RECIPIENT`.
- Khối: VO dự thảo campaign 17 cue (pack timing CP06) — khối tiếp theo đã
  ghi ở checkpoint 16.
- Trạng thái: DRAFT_NOT_FINAL_VO — bản dự thảo để đạo diễn/Codex nghe thử,
  KHÔNG phải VO final, KHÔNG mix với nhạc/ambience.

## Trạng thái GitHub (đọc qua API công khai read-only, 2026-11-05 ~22:45 JST)

- Issue #116: vẫn OPEN, vẫn 10 comment; mới nhất vẫn là `6657227288`
  (2026-11-05 11:49:15Z, khanhcoder97) — KHÔNG có chỉ đạo mới kể từ CP16.
- PR #119: OPEN, head `7d7c986` (= nhánh media trước lượt này), base
  `f383233` trên API (nhánh integration đã tiến tới `f0859d0`), 25 commit,
  729 file, 0 review comment mới.
- Integration HEAD xác nhận `f0859d0` (merge PR #121); ref local đã đồng bộ
  lại trong lượt này (lần fetch đầu chưa cập nhật ref do chỉ fetch tên
  nhánh; đã fetch lại bằng refspec đầy đủ, khớp API).

## 1. Mười bảy take (giọng hư cấu hệ thống, không clone giọng người thật)

Tất cả đo từ byte thật bằng ffprobe + ffmpeg loudnorm. WAV 48 kHz mono
pcm_s16le; file MP3 gốc của TTS giữ kèm để đối chiếu provenance. Tốc độ
nói giữ 100 (D1 cấm tăng tốc để vừa cửa sổ). Cửa sổ lấy từ timing JSON
(nguồn thật), văn bản đối chiếu từng ký tự với SRT của cảnh.

| Shot | Người nói | Giọng | Dài | Cửa sổ | Dư | LUFS | True peak |
|---|---|---|---|---|---|---|---|
| CIN_003_S03 | Ly An | Aria | 4.032s | 12.5–17.5s | +0.968s | −19.32 | −4.36 dBTP |
| CIN_005_S03 | Ly An | Aria | 5.160s | 12.5–17.5s | −0.160s | −20.50 | −6.31 dBTP |
| CIN_007_S03 | Ly An | Aria | 3.912s | 12.5–17.5s | +1.088s | −18.10 | −1.38 dBTP |
| CIN_008_S03 | Tạ Vân Khanh | Helio | 3.552s | 12.5–17.5s | +1.448s | −23.10 | −1.94 dBTP |
| CIN_009_S03 | Ly An | Aria | 4.080s | 12.5–17.5s | +0.920s | −17.23 | −3.13 dBTP |
| CIN_010_S03 | Sầm Chủ Quỹ | Helio | 2.808s | 12.5–17.5s | +2.192s | −22.01 | −4.71 dBTP |
| CIN_011_S03 | Hạ Mặc | Helio | 5.592s | 12.2–17.8s | +0.008s | −21.50 | −3.42 dBTP |
| CIN_012_S03 | Hạ Mặc | Helio | 4.320s | 12.5–17.5s | +0.680s | −25.38 | −5.33 dBTP |
| CIN_013_S03 | Trưởng đoàn | Helio | 2.472s | 12.5–17.5s | +2.528s | −22.51 | −5.33 dBTP |
| CIN_014_S03 | Tống Bành | Helio | 3.072s | 12.5–17.5s | +1.928s | −22.05 | −2.01 dBTP |
| CIN_015_S03 | Đội trưởng thợ lặn | Helio | 2.880s | 12.5–17.5s | +2.120s | −23.27 | −4.01 dBTP |
| CIN_016_S03 | Hạ Mặc | Helio | 2.472s | 12.5–17.5s | +2.528s | −21.92 | −4.40 dBTP |
| CIN_017_S03 | Đội trưởng thợ lặn | Helio | 3.168s | 12.5–17.5s | +1.832s | −22.33 | −2.63 dBTP |
| CIN_018_S02 | Cơ Vô Tướng | Helio | 2.880s | 6.5–11.5s | +2.120s | −23.77 | −2.35 dBTP |
| CIN_018_S03 | Người chơi | Helio | 5.280s | 12.5–17.5s | −0.280s | −22.54 | −3.91 dBTP |
| CIN_019_S03 | Ly An | Aria | 2.880s | 12.5–17.5s | +2.120s | −25.52 | −8.76 dBTP |
| CIN_020_S03 | Người nhận thư | Aria | 3.000s | 12.5–17.5s | +2.000s | −19.59 | −5.29 dBTP |

**Kết quả vừa cửa sổ: 15/17 FITS, 2 OVERRUN** — CIN_005_S03 (−0.160s)
và CIN_018_S03 (−0.280s). Cả hai đều được giao NGUYÊN VẸN (không cắt,
không tăng tốc) và ghi OVERRUN trong manifest; đây là finding cho đạo
diễn (nới cửa sổ hoặc rút câu), KHÔNG phải lỗi build giấu đi. CIN_011_S03
vừa đúng +0.008s — diễn xuất final chậm hơn một nhịp là tràn cửa sổ.

Không clip (true peak cao nhất −1.38 dBTP).

## 2. Deliverable

- `Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/` — 17 WAV take +
  17 MP3 TTS gốc + `CAMPAIGN_VO_timeline_draft_v1.wav` (378.0s, VO-only:
  take đặt tại offset tuyệt đối của campaign: CIN_003 66.5s, CIN_005
  102.5s, CIN_007 138.5s, CIN_008 156.5s, CIN_009 174.5s, CIN_010 192.5s,
  CIN_011 210.2s, CIN_012 228.5s, CIN_013 246.5s, CIN_014 264.5s,
  CIN_015 282.5s, CIN_016 300.5s, CIN_017 318.5s, CIN_018_S02 330.5s,
  CIN_018_S03 336.5s, CIN_019 354.5s, CIN_020 372.5s) +
  `CAMPAIGN_VO_manifest_v1.json` (sha256 từng file, loudness, fit từng take)
- Timeline đã xác minh bằng volumedetect: 17/17 cửa sổ có tiếng
  (max −1.4…−8.8 dB, khớp true peak từng take); 5/5 khoảng trống kiểm
  (0–12.5s, 76–90s, 180–185s, 250–255s, 376–378s) im −91.0 dB.
- Tool: `Tools/MediaProduction/Muse/build_campaign_vo.py` (đọc cue từ
  timing JSON + đối chiếu SRT, tool fail nếu thiếu input/sai văn bản;
  overrun chỉ ghi nhận, không fail build — theo D1).
- Runtime: `ClientGodot/assets/audio/vo/campaign/` — 17 WAV + timeline;
  `RUNTIME_AUDIO_manifest_v1.json` tái sinh: tổng 563 file (22 nhạc/
  ambience + 519 SFX/UI + 22 VO: 4 P0 + 18 campaign).

## 3. Giới hạn / khuyết điểm (đọc kỹ trước khi duyệt)

- Đây là giọng TTS hệ thống, tiếng Việt có thể chưa tự nhiên hoàn hảo;
  worker không nghe thử bằng tai được — bản này cần chủ dự án/đạo diễn
  nghe thử và chốt diễn xuất, nhịp, phát âm tên riêng.
- **2 take OVERRUN** (CIN_005_S03, CIN_018_S03): cần đạo diễn quyết nới
  cửa sổ hay rút câu. Không tự tăng tốc, không tự sửa câu (canon).
- **CIN_011_S03 chỉ vừa +0.008s** — coi như sát giới hạn, cần đạo diễn
  lưu ý khi chốt diễn xuất final.
- **Tất cả nhân vật nam dùng chung một giọng Helio** trong bản nháp này
  (chỉ có Aria/Helio là giọng production theo skill; các giọng catalog
  khác chưa kiểm chứng chất lượng tiếng Việt). Các nhân vật nam KHÔNG
  phân biệt được bằng giọng trong bản nháp — casting riêng là quyết định
  của đạo diễn, bản nháp không tự bịa giọng mới.
- **Take Người chơi (CIN_018_S03) chỉ là placeholder đo nhịp**: VOICE_GUIDE
  không gán giọng nói/giới tính cho người chơi; take này tồn tại để nghe
  nhịp, đạo diễn phải thay bằng giọng đã chốt hoặc bỏ lời nói thành tiếng.
  Tương tự, CIN_020 dùng giọng vai placeholder `VOICE_LETTER_RECIPIENT`
  (người nhận thư chưa rõ danh tính/giới tính).
- Mức loudness chưa cân bằng giữa các take (−17.23…−25.52 LUFS) và chưa
  cân với pool stem P0 (~−25 LUFS). Đây là số đo từng take, KHÔNG phải
  mix PASS; final cần gain staging chung trước khi trộn với stem.
- Không trộn nhạc/ambience, không chuẩn hóa loudness trong draft này.
- Mọi cửa sổ campaign vẫn là PROPOSED_ANIMATIC_PLACEMENT (chỉ CIN_001_S05
  là DECIDED); D1 chỉ mở sản xuất VO nháp, không chốt cửa sổ làm canon.
- VO của CIN_006 (1 cue, đã có timing từ CP05) CHƯA làm — không thuộc
  pack 17 cue của CP06; là việc lẻ còn lại của VO campaign.

## 4. Kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Source pack kiểm chứng lại — PASS, 0 mismatch

`MEDIA02_CHECKPOINT_17_SOURCE_REVALIDATION_20261105.json`
(base `f0859d0`):

- Audio nguồn: 1093 file khớp byte/sha/codec/48 kHz/kênh/thời lượng.
- Timing + SRT: 20/20 cảnh, timing dialogues 21 == SRT cues 21 ==
  runtime manifest 21.
- Animatic: 12/12 panel khớp sha, MP4/OGV 640×360 72 s; VO P0: 3/3 take
  khớp sha/thời lượng và vừa cửa sổ; keyframes 16:9: 12/12.
- **Campaign VO: 17/17 take khớp sha/thời lượng/format, văn bản khớp
  từng ký tự với SRT; timeline 378.0s. Window fit: 15 FITS / 2 OVERRUN
  (ghi trong `windowFit`, là finding cho đạo diễn, không tính là byte
  mismatch).**

### 2. Runtime delivery kiểm chứng lại — PASS, 0 mismatch

`MEDIA02_CHECKPOINT_17_RUNTIME_REVERIFY_20261105.json`:

| Nhóm | Số file kiểm | Kết quả |
|---|---|---|
| Audio runtime (22 nhạc/ambience + 519 SFX/UI + 22 VO) | 563 | khớp manifest, 0 mismatch |
| Animatic P0 v3 (MP4 + OGV + poster) | 3 | khớp sha, 0 mismatch |
| Timing JSON 20 cảnh | 20 | khớp sha, 0 mismatch |
| SRT 20 cảnh | 20 | khớp sha, 0 mismatch |

### 3. Runtime builder — ALL VERIFIED

`build_runtime_delivery.py`: audio 563 (music/ambience 22, SFX/UI 519,
VO 22), cinematics 3 animatic + 20 scene (40 timing+SRT). Audio manifest
tái sinh (checkpoint 17, +18 entry campaign VO + ghi chú overrun).

## Trạng thái repo

- Nhánh media: commit fix `37da3b1` ĐÃ PUSH (ls-remote xác nhận; scope audit
  729 paths, 0 violations, base integration HEAD `f0859d0`). Commit này 61
  file: 17 WAV take + 17 MP3 TTS gốc + manifest + timeline 378s (source),
  17 WAV + timeline (runtime), runtime audio manifest tái sinh (563 file),
  tool mới build_campaign_vo.py + 3 tool delivery/validate/verify cập nhật,
  2 JSON kiểm chứng lại. 35 object LFS mới đã upload (43 MB). PR #119 nay
  có 26 commit, vẫn mở/chưa merge (HOLD).
- ACK comment checkpoint 17 trên issue #116 cần thẻ duyệt của chủ dự án —
  ghi rõ để luồng chính xử lý, lượt này không treo chờ.

## Khối tiếp theo

1. Xuất clip riêng từng scene (Gói 30 item 6: MP4/OGV/poster/SRT/timing/
   hash) + viết lại mô tả PR #119 theo số thực (item 8, cần thẻ duyệt).
2. VO CIN_006 (1 cue còn lại) + campaign video: animated takes thật
   (không còn là reel panel-hold).
3. Quyết định của đạo diễn cho 2 take OVERRUN + take Người chơi
   placeholder + casting giọng nam riêng từng nhân vật.
