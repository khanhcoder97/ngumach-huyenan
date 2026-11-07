# MEDIA-02 — Checkpoint 01: re-baseline + khóa timing/SRT dự thảo P0

- Ngày: 2026-11-05 (JST). Agent: Muse (chỉ media, theo policy `agent_scope_v2.json` / work 28 + work 29).
- Nhánh: `muse/media-production-20261104`. Base sau đồng bộ: `cf171786baebb10c3f17d3060d47429faf3e4026` (integration đã gồm merge PR #115 `8bab575` và merge PR #117).
- Đồng bộ: nhánh media fast-forward thường tới integration HEAD (7a85494 là tổ tiên của integration), giữ nguyên WIP, không force-push/reset. Git fetch đã khôi phục trong lượt này (các lượt trước lỗi proxy `Connection reset by 198.19.0.1 port 3128`).
- Quyết định áp dụng: `DEC-MEDIA-P0-20261105` (`Implementation/Content/DesignBaselines/media_p0_decisions_20261105.json`).

## 1. Re-baseline inventory (M1) tại cf17178

- Cinema: **20 cảnh / 63 shot / 378 giây** — tính lại từ `Cinema_Production_Pack_v1.json` trên cây mới, khớp DEC-MEDIA-P0.
- Khác biệt so với snapshot tạm 3557959: pack canonical và Directors Pack đã được đồng bộ câu Q1 (PR #117) — thoại CIN_001 trong pack hiện là bản B (xem mục 2). Kiểm chứng: `scenes[0].dialogueLines[0] = "Ly An: Đầu kia! Giữ giúp tôi đầu kia!"`; CIN_006 canonical = câu Hạ Mặc theo DEC Q3.
- Audio: manifest `game_audio_v1.json` có **195 entry**, bindings skills 30 / monsters 30 / bosses 12 / maps 46 / npcs 83 / companions 10 / cinema 20 — không đổi so với bản tạm. 541 master FLAC vẫn là LFS pointer trong clone skip-smudge; chỉ các file ở mục 3 được pull byte thật.

## 2. Timing + SRT dự thảo P0 (M2) — đã khóa theo quyết định

Deliveries tại `Implementation/Content/Narrative/Deliveries/` (mỗi cảnh: `<ID>_timing_v1.json` + `<ID>_vi.srt`, và `P0_timing_manifest_v1.json` có hash nguồn + hash SRT):

| Cảnh | Thoại | Cửa sổ | Trạng thái |
|---|---|---|---|
| CIN_001_S05 | Ly An: "Đầu kia! Giữ giúp tôi đầu kia!" (30 ký tự) | **24.8–28.5s** (8,11 ký tự/giây) | DECIDED theo DEC-MEDIA-P0 Q1; cửa sổ do quyết định ấn định nên giữ nguyên dù thấp hơn gợi ý đọc 12–17 ký tự/giây |
| CIN_002_S02 | Tạ Vân Khanh: "Trên bờ chỉ nghe nửa tiếng. Phần còn lại ở dưới ấy." (51 ký tự) | 7.0–11.0s (12,75 ký tự/giây) | PROPOSED — vị trí shot/timecode chưa có trong nguồn, đặt dự thảo ở shot MEDIUM_STATIC, chờ đạo diễn/Codex xác nhận |
| CIN_004_S02 | Ly An: "Nó cứ tránh chỗ nước ấy." (24 ký tự) | 7.5–9.5s (12,0 ký tự/giây) | Speaker OFF-SCREEN đã DECIDED theo Q2 (`characters` vẫn chỉ `BOSS_MANG_COT`); vị trí shot/timecode là PROPOSED |

- SRT đã kiểm: UTF-8, NFC, 1 cue/cảnh, timecode hợp lệ. Tên speaker nằm trong timing JSON (tách ngoài thoại), SRT chỉ chứa lời thoại.
- Công cụ tái lập: `Tools/MediaProduction/Muse/build_p0_timing.py` (đọc pack + decisions, sinh timing/SRT/manifest kèm sha256).

## 3. Đo byte thật của pool stem ứng viên P0 (V4/M8, một phần)

Đã `git lfs pull` chọn lọc 11 file tại `Client/Assets/Audio/PackV1/` và đo bằng ffprobe (không suy từ pointer nữa):

| File | Codec | Kênh | Thời lượng | Cỡ |
|---|---|---|---|---|
| sfx/cinema/reveal_v01.wav | pcm_s16le 48 kHz | mono | 2,9915s | 287.228 B |
| sfx/cinema/tension_v01.wav | pcm_s16le 48 kHz | mono | 2,9915s | 287.228 B |
| sfx/cinema/resolve_v01.wav | pcm_s16le 48 kHz | mono | 2,9915s | 287.228 B |
| sfx/cinema/transition_v01.wav | pcm_s16le 48 kHz | mono | 2,9915s | 287.228 B |
| music/ben_mua.ogg | vorbis 48 kHz | stereo | 56,4706s | 542.912 B |
| music/boss_mang_cot.ogg | vorbis 48 kHz | stereo | 36,9231s | 392.833 B |
| music/quiet_discovery.ogg | vorbis 48 kHz | stereo | 64,0000s | 465.121 B |
| ambience/rain_light.ogg | vorbis 48 kHz | stereo | 16,0000s | 216.305 B |
| ambience/river_shore.ogg | vorbis 48 kHz | stereo | 16,0000s | 187.736 B |
| ambience/underwater.ogg | vorbis 48 kHz | stereo | 16,0000s | 91.898 B |
| ambience/rain_heavy.ogg | vorbis 48 kHz | stereo | 16,0000s | 216.345 B |

- Loudness mẫu (ffmpeg loudnorm, integrated / true peak): reveal_v01 = −25,69 LUFS / −12,28 dBTP; ben_mua = −21,92 / −10,77; rain_light = −27,48 / −18,60. Đây là đo từng cue riêng lẻ, KHÔNG phải mix −16 LUFS của cảnh — không ghi PASS mix.
- Pool stem theo cảnh ghi trong timing JSON ở trạng thái `CANDIDATE_POOL_NOT_LOCKED`; manifest audio vẫn chỉ bind 1 stinger chung `SFX/CINEMA/reveal` với `REQUIRES_PICTURE_LOCK_NOT_SYNCED`, VO và picture-locked sound edit vẫn nằm trong `scopeExclusions`.

## 4. Giới hạn còn mở

- Chưa có keyframe/character lock đã duyệt cho shot có nhân vật được đặt tên: chỉ chặn final picture của shot đó (theo DEC Q5/visualLock), không chặn timing/SRT/audio.
- Reference môi trường cho storyboard/animatic: `Art_Source/BenMua_Concept_Rebuild_20261105` (đã vào integration qua PR #115).
- VO chưa thu (giọng hư cấu theo VOICE_GUIDE, không clone giọng thật); đây là checkpoint timing/SRT/audio-đo, chưa phải bản xem video.
- Hai vị trí thoại PROPOSED (CIN_002, CIN_004) chờ xác nhận trước khi coi là SRT final.

## 5. Khối tiếp theo

- M2 tiếp: storyboard/animatic P0 trên reference môi trường mới cho các shot không cần character lock (nước/dây/kiện), và thu VO dự thảo cho 3 câu P0 theo cửa sổ đã khóa.
- Song song: đo nốt loudness/peak cho 8 file pool còn lại và lập bảng stem theo shot sau khi có xác nhận vị trí thoại PROPOSED.
