# MEDIA-02 CHECKPOINT 04 — VO dự thảo P0 (3 câu)

- Ngày: 2026-11-05 (lượt chạy định kỳ ~09:40 JST)
- Nhánh: `muse/media-production-20261104`, base integration `cf17178`
  (không có merge mới: media branch vẫn ở `8be1af2`, integration vẫn `cf17178`)
- Quyết định áp dụng: DEC-MEDIA-P0-20261105 (Q1–Q4, xem checkpoint 01)
- Khối: (c) VO dự thảo 3 câu P0 theo cửa sổ đã khóa + VOICE_GUIDE
- Trạng thái: DRAFT_NOT_FINAL_VO — bản dự thảo để đạo diễn/Codex nghe thử,
  KHÔNG phải VO final, KHÔNG mix với nhạc/ambience.

## 1. Ba take (giọng hư cấu hệ thống, không clone giọng người thật)

Tất cả đo từ byte thật bằng ffprobe + ffmpeg loudnorm. WAV 48 kHz mono
pcm_s16le; file MP3 gốc của TTS giữ kèm để đối chiếu provenance.

| Shot | Người nói | Giọng | Câu thoại | Cửa sổ | Dài | Dư | LUFS | True peak |
|---|---|---|---|---|---|---|---|---|
| CIN_001_S05 | NPC_LYAN (onscreen) | Aria | Đầu kia! Giữ giúp tôi đầu kia! | 24.8–28.5s | 2.568s | +1.132s | −16.01 | −1.85 dBTP |
| CIN_002_S02 | NPC_TA_VAN_KHANH (onscreen) | Helio | Trên bờ chỉ nghe nửa tiếng. Phần còn lại ở dưới ấy. | 7.0–11.0s | 3.792s | +0.208s | −21.61 | −4.24 dBTP |
| CIN_004_S02 | NPC_LYAN (off-screen) | Aria | Nó cứ tránh chỗ nước ấy. | 7.5–9.5s | 1.752s | +0.248s | −21.41 | −8.56 dBTP |

Cả 3 take đều VỪA cửa sổ (tool tự fail nếu tràn cửa sổ). Không clip
(true peak cao nhất −1.85 dBTP).

## 2. Deliverable

- `Art_Source/Audio/Muse/VO/P0_DRAFT/VO_CIN001_S05_LYAN_draft_v1.wav`
- `Art_Source/Audio/Muse/VO/P0_DRAFT/VO_CIN002_S02_TAVANKHANH_draft_v1.wav`
- `Art_Source/Audio/Muse/VO/P0_DRAFT/VO_CIN004_S02_LYAN_OFFSCREEN_draft_v1.wav`
- `Art_Source/Audio/Muse/VO/P0_DRAFT/P0_VO_timeline_draft_v1.wav`
  (72.0s, VO-only: take đặt tại 24.8s / 43.0s / 61.5s theo offset scene
  0s / 36s / 54s; đã xác minh bằng volumedetect: 3 cửa sổ có tiếng
  (max −1.8 / −4.3 / −8.6 dB), các đoạn còn lại im −91 dB)
- `Art_Source/Audio/Muse/VO/P0_DRAFT/P0_VO_manifest_v1.json`
  (sha256 từng file, loudness, trạng thái từng take)
- Tool: `Tools/MediaProduction/Muse/build_p0_vo.py`
  (lệnh TTS tái tạo MP3 ghi trong docstring; tool làm convert + đo +
  kiểm vừa cửa sổ + ghép timeline; tool fail nếu take tràn cửa sổ)

Chưa copy sang `ClientGodot/assets/audio/`: VO còn là draft, delivery
runtime chờ chốt VO + Codex review.

## 3. Giới hạn / khuyết điểm (đọc kỹ trước khi duyệt)

- Đây là giọng TTS hệ thống, tiếng Việt có thể chưa tự nhiên hoàn hảo;
  worker không nghe thử bằng tai được — bản này cần chủ dự án/đạo diễn
  nghe thử và chốt diễn xuất, nhịp, phát âm tên riêng.
- CIN_002_S02 và CIN_004_S02 chỉ dư 0.208s / 0.248s: diễn xuất final
  nhanh hơn một chút vẫn vừa, nhưng đọc chậm hơn sẽ tràn cửa sổ.
  Vị trí thoại của 2 shot này vẫn là PROPOSED (chỉ CIN_001_S05 là
  DECIDED, và CIN_004 off-screen là DECIDED về hình thức).
- Mức loudness chưa cân bằng giữa các take: S05 −16.01 LUFS to hơn
  rõ 2 take còn lại (−21.6 / −21.4 LUFS) và to hơn pool stem P0
  (~−25 LUFS, checkpoint 02). Đây là số đo từng take, KHÔNG phải mix
  PASS; final cần gain staging chung trước khi trộn với stem.
- Không trộn nhạc/ambience, không chuẩn hóa loudness trong draft này.
- Issue #116: trang issue đọc lại tươi lúc 09:42 JST nhưng bản text
  không hiện comment; connector read cần thẻ duyệt mà lượt chạy detached
  không có chủ dự án bấm — vì vậy chưa xác nhận được comment mới sau
  comment 6 của chủ dự án (08:35 JST). Trạng thái cuối đã biết vẫn là
  OPEN, 6 comment. ACK checkpoint 03/04 + media PR vẫn chờ thẻ duyệt
  của chủ dự án ở luồng chính; worker không tự đăng comment/mở PR.

## 4. Khối tiếp theo

- (d) timing CIN006 (P1) theo Q3 (alternate take có takeId/version riêng)
  và Q4 (Hạ Mặc/Sầm cinematic-only staging).
- Sau đó: (e) các pack M3/M4/M5 (video campaign, nhạc, SFX/ambience
  theo cue ID).
