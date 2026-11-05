# MEDIA-02 — Checkpoint 08: pack SFX + UI đã đo từ byte thật (M5)

- Ngày: 2026-11-05 (JST). Agent: Muse (chỉ media, theo policy `agent_scope_v2.json` / work 28 + work 29).
- Nhánh: `muse/media-production-20261104`. Base đồng bộ: integration HEAD `cf17178` (không đổi so với checkpoint 01–07; `git fetch` lượt này không có commit mới trên integration).
- Khối hoàn thiện trong lượt này: **(e) tiếp — pack SFX/UI còn lại theo cue ID (M5)**: toàn bộ 146 cue SFX + 27 cue UI của manifest `NGM_ORIGINAL_AUDIO_V1`, mỗi cue đủ 3 variant, cả bản runtime WAV lẫn bản master FLAC — tổng 1038 file variant đã đo từ byte thật.
- Bối cảnh bàn giao: PR #119 đã mở trước lượt này (head `1db3f23` → base integration, 7 commit, chưa merge, xác minh qua API công khai); commit checkpoint 08 này đẩy lên cùng nhánh media nên sẽ thành commit thứ 8 của PR #119 — KHÔNG mở PR mới. ACK checkpoint 08 trên issue #116 vẫn cần thẻ duyệt của luồng chính (lượt chạy định kỳ không treo chờ).

## 1. Nguồn đọc (không bịa)

- `Client/Assets/AudioManifests/game_audio_v1.json`: 195 cue, trong đó SFX 146 + UI 27 = 173 cue; tất cả `loop=False` (one-shot), `assetState=RENDERED_CANDIDATE`, `wireStatus=REQUIRES_PRESENTATION_ADAPTER`, license `original_procedural_synthesis_no_external_samples` (tổng hợp gốc, không sample ngoài, không clone giọng).
- Phân loại theo cueKey: BOSS 38, SKILL 30, MONSTER 24, UI 15, WORLD 9, LIFE 8, PVP 8, COMBAT 7, FORGE 7, TRADE 5, GUILD 4, QUEST 4, ACCOUNT 3, PET 3, CINEMA 4, COSMETIC 2, CRAFT 2 (cộng = 173; các cue bus UI nằm dưới `SFX/UI/`, `SFX/TRADE/`, `SFX/ACCOUNT/`, `SFX/COSMETIC/`, `SFX/QUEST/`).
- Trước lượt này, trong clone chỉ 12/1038 file SFX/UI là byte thật (các stinger cinema từ checkpoint 01/02); 1026 file còn lại là con trỏ LFS. Lượt này đã `git lfs pull` chọn lọc đủ 1038 file (WAV runtime + FLAC master). LFS pull hai lần đầu bị proxy reset (lỗi kex/connection reset qua proxy 3128), lần thứ ba với `GIT_SSH_COMMAND='ssh -F /home/hatch/.ssh/config'` thành công; `git status` vẫn sạch với các file đó — LFS pull chỉ thay con trỏ bằng byte thật, không sửa nội dung track.

## 2. Deliverable

| Đường dẫn | Nội dung |
|---|---|
| `Implementation/Content/Audio/Deliveries/SFX_UI_pack_v1.json` | Pack 173 cue: mỗi cue có cueKey, category, tên tiếng Việt, bus, gain/priority/voiceGroup, trigger/skill/class (khi có), license, sourceRef, tóm tắt theo cue, và đủ 3 variant — mỗi variant có số đo runtime WAV + master FLAC (codec, 48 kHz, mono, thời lượng, byte, LUFS, true peak, LRA, sha256) kèm cờ khớp manifest (sha/byte/thời lượng) và chênh lệch thời lượng master−runtime |
| `Tools/MediaProduction/Muse/measure_sfx_ui.py` | Công cụ tái lập: assert đúng 173 cue (146 + 27), mỗi cue 3 variant, từ chối con trỏ LFS thay vì đo giả, đo bằng ffprobe + ffmpeg loudnorm, đối chiếu sha/byte/thời lượng với manifest |
| Báo cáo này | `Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_08_SFX_UI_20261105.md` |

## 3. Kết quả đo (byte thật, không phải mix PASS)

- **Đo đủ 173/173 cue, 519 variant, 1038 file (WAV + FLAC).** Runtime: WAV PCM 16-bit (`pcm_s16le`), 48 kHz, mono. Master: FLAC, 48 kHz, mono. Thời lượng master − runtime = **0.0 giây ở cả 519 variant** — runtime là bản encode đúng độ dài của master, không bị cắt/ngắn.
- **Đối chiếu manifest: 0 lệch.** 1038/1038 sha256 khớp manifest (`sha256`/`masterSha256`), 519/519 byte WAV khớp, 519/519 thời lượng khớp trong 1 ms. Pack này vì vậy vừa là pack đo, vừa là kiểm chứng toàn vẹn của manifest SFX/UI.
- **Thời lượng:** runtime 0.1737–3.2085 giây (trung bình ~0.71 s); dài nhất là `SFX/CINEMA/transition` v03 (3.2085 s); UI 0.1737–1.1903 giây.
- **Loudness:** 333 variant có LUFS tích hợp hữu hạn, −27.95…−21.85 LUFS; lớn nhất là `SFX/COMBAT/miss` v03 (−21.85 LUFS). True peak cao nhất toàn pack là −5.85 dBTP (`SFX/COMBAT/projectile_hit` v03) — **không có file nào clip** (tất cả true peak dưới 0 dBTP với headroom ≥ 5.85 dB); UI cao nhất −9.14 dBTP.
- **186 variant ngắn hơn 400 ms không có LUFS tích hợp — đây là giới hạn của phép đo, không phải file câm.** ffmpeg loudnorm trả `-inf` vì cửa sổ gating EBU R128 cần 400 ms (đã kiểm chứng: mọi variant `-inf` đều 0.1737–0.3726 s, mọi variant hữu hạn đều ≥ 0.4632 s). 62 cue × 3 variant rơi vào nhóm này. Tool đã sửa để ghi `integrated_lufs=null` + mức RMS giải mã trực tiếp (`short_clip_level_dbfs_rms`, −28.0…−25.0 dBFS — trùng đúng `rmsDb` manifest −25/−28) và peak dBFS, kèm ghi chú rõ ràng; true peak của nhóm này vẫn hợp lệ (ví dụ `metal_thrust` v01: TP −12.49 dBTP khớp peak mẫu 0.236 → −12.54 dBFS). File JSON tái tạo đã qua parse strict (không còn token `-Infinity`).
- **LRA:** 0.0–1.0 LU ở các variant hữu hạn — bình thường với one-shot ngắn, không phải chỉ số mix.

## 4. Kiểm chứng đã chạy

- Tool assert 173 cue (146 SFX + 27 UI), mỗi cue 3 variant, tất cả `loop=False` rồi mới đo; file con trỏ LFS sẽ làm tool dừng lỗi thay vì cho số giả — lượt này 1038/1038 file đều là byte thật trước khi đo (đã đếm lại sau pull).
- Số đo checkpoint 01/02 cho các stinger cinema đã nằm trong pack này vẫn nhất quán (cùng file, cùng phương pháp).
- Scope: `Tools/Coordination/check_agent_scope.py --base cf17178 --head HEAD --branch muse/media-production-20261104` → **89 changed paths (tích lũy từ base), 0 violations**; commit checkpoint 08 là `0ea00b1` (đã push, xác minh bằng ls-remote: `0ea00b1dac77912200791f9d275c6c95f4b87187`).

## 5. Giới hạn còn mở

- Đây là pack đo từng cue/variant, KHÔNG phải mix PASS: chưa có mix tổng, chưa có VO lồng vào SFX, chưa có ducking nhạc/ambience, chưa nghe tai kiểm chứng.
- Tất cả 173 cue vẫn `RENDERED_CANDIDATE` + `REQUIRES_PRESENTATION_ADAPTER` trong manifest — đã đo, chưa nối runtime, chưa phải final.
- Issue #116 lượt này: 7 comment (mới nhất là ACK checkpoint 03–07 + PR #119, 13:45 JST); không có chỉ đạo mới so với DEC-MEDIA-P0/Q1–Q4. ACK checkpoint 08 + việc PR #119 nhận thêm commit vẫn chờ luồng chính xử lý thẻ duyệt/kiểm chứng.
- Khối tiếp theo: (e) tiếp — VO dự thảo campaign cho 17 cue dialogue của pack M3 khi cửa sổ timing được xác nhận, hoặc M6/M7 runtime delivery + QA (adapter trình bày, kiểm tra thiết bị) khi có hướng từ Codex/chủ dự án. KHÔNG mở lại hàng đợi đồ họa cũ.
