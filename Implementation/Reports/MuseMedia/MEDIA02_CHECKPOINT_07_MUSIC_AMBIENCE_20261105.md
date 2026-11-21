# MEDIA-02 — Checkpoint 07: pack nhạc + ambience đã đo từ byte thật (M4/M5)

- Ngày: 2026-11-05 (JST). Agent: Muse (chỉ media, theo policy `agent_scope_v2.json` / work 28 + work 29).
- Nhánh: `muse/media-production-20261104`. Base đồng bộ: integration HEAD `cf17178` (không đổi so với checkpoint 01–06; `git fetch` lượt này không có commit mới).
- Khối hoàn thiện trong lượt này: **(e) tiếp — pack nhạc + ambience theo cue ID (M4/M5)**: toàn bộ 9 cue Music + 13 cue Ambience của manifest `NGM_ORIGINAL_AUDIO_V1` đã được đo từ byte thật, cả bản runtime OGG lẫn bản master FLAC.

## 1. Nguồn đọc (không bịa)

- `Client/Assets/AudioManifests/game_audio_v1.json`: 195 cue, trong đó Music 9 + Ambience 13; tất cả 22 cue đều `loop=True`, `assetState=RENDERED_CANDIDATE`, `wireStatus=REQUIRES_PRESENTATION_ADAPTER`, license `original_procedural_synthesis_no_external_samples` (nhạc/ambience tổng hợp gốc, không sample ngoài, không clone giọng).
- Trước lượt này, trong clone chỉ 7/22 file runtime là byte thật (ben_mua, boss_mang_cot, quiet_discovery, rain_light, rain_heavy, river_shore, underwater — từ checkpoint 01/02); 15 file còn lại và toàn bộ 22 master đều là con trỏ LFS 131–132 byte. Lượt này đã `git lfs pull` chọn lọc đủ 22 runtime OGG + 22 master FLAC (44 file) sau khi `git lfs install --local` cho clone (LFS trước đó chưa được cài nên pull bị bỏ qua). LFS pull chỉ thay con trỏ bằng byte thật, `git status` vẫn sạch với các file đó — không có file nào ngoài phạm vi bị sửa.

## 2. Deliverable

| Đường dẫn | Nội dung |
|---|---|
| `Implementation/Content/Audio/Deliveries/MUSIC_AMBIENCE_pack_v1.json` | Pack 22 cue: mỗi cue có cueKey, tên tiếng Việt, bus, loop/gain/priority, license, sourceRef, số đo runtime + master (codec, 48 kHz, stereo, thời lượng, byte, LUFS, true peak, LRA, sha256), chênh lệch thời lượng master−runtime, chỉ số seam vòng lặp, danh sách map bind và trạng thái binding |
| `Tools/MediaProduction/Muse/measure_music_ambience.py` | Công cụ tái lập: đọc manifest, assert đúng 22 cue (9 + 13), từ chối con trỏ LFS thay vì đo giả, đo bằng ffprobe + ffmpeg loudnorm + decode f32 cho seam |
| Báo cáo này | `Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_07_MUSIC_AMBIENCE_20261105.md` |

## 3. Kết quả đo (byte thật, không phải mix PASS)

- **Đo đủ 22/22 cue, cả runtime lẫn master.** Runtime: Vorbis OGG, 48 kHz, stereo. Master: FLAC, 48 kHz, stereo. Thời lượng master − runtime = **0.0 giây ở cả 22 cue** — runtime là bản encode đúng độ dài của master, không bị cắt/ngắn.
- **Nhạc (9):** thời lượng 36.92–64.0 giây (ben_mua 56.47s, boss_mang_cot 36.92s, quiet_discovery 64.0s khớp đúng số checkpoint 01/02 đo lại — tái lập được). Loudness runtime −23.34…−21.58 LUFS; true peak cao nhất −9.27 dBTP (quiet_discovery, runtime) / −9.21 dBTP (master). Không có cue nào clip (true peak đều dưới 0 dBTP với headroom ≥ 9 dB).
- **Ambience (13):** tất cả đúng 16.0 giây. Loudness runtime −33.02…−27.47 LUFS — thấp hơn nhạc khoảng 6–10 LU theo từng cue (quan sát từng cue, chưa phải phán quyết mix: chưa có VO, chưa có mix tổng). True peak cao nhất −17.35 dBTP (rain_heavy). Underwater là quiet nhất (−33.02 LUFS / −19.12 dBTP, khớp checkpoint 02).
- **Vòng lặp:** cả 22 cue đều loop=True. Chỉ số seam (wrap jump, decode mono 48 kHz, head/tail 100 ms) phần lớn ≤ 0.015; ngoại lệ duy nhất đáng chú ý là **rain_heavy 0.0538** (gấp ~3.5 lần cue cao thứ hai là waterfall 0.0152), dù RMS đầu/cuối của nó gần bằng nhau (0.0302 / 0.0305). Đây là chỉ số đo, KHÔNG phải kết luận "không seamless" — cần nghe tai kiểm chứng trước khi gọi là lỗi.
- **Map binding:** 92 lượt bind map ↔ cue trên 18/22 cue, trạng thái `DESIGN_BINDING_CANDIDATE_REQUIRES_MODE_ZONE_REVIEW` (server mode/zone thắng, không tự kích hoạt theo tên map). 4 ambience không có bind map nào trong `bindings.maps`: rain_light, forge, rain_heavy, waterfall — rain_light/rain_heavy vốn là ambience của pool stem P0, không phải nhạc nền map.

## 4. Kiểm chứng đã chạy

- Tool assert 22 cue (9 Music + 13 Ambience) rồi mới đo; file con trỏ LFS sẽ làm tool dừng lỗi thay vì cho số giả — lượt này 44/44 file đều là byte thật trước khi đo.
- Số đo checkpoint 01/02 tái lập đúng: ben_mua −21.92 LUFS / −10.77 dBTP, rain_light −27.48 / −18.60, underwater −33.02 / −19.12 (runtime).
- Scope: `Tools/Coordination/check_agent_scope.py --base cf17178 --head HEAD --branch muse/media-production-20261104` → 86 changed paths (tích lũy từ base), 0 violations.

## 5. Giới hạn còn mở

- Đây là pack đo từng cue, KHÔNG phải mix PASS: chưa có VO lồng vào nhạc/ambience, chưa có mix tổng, chưa nghe tai kiểm chứng vòng lặp (đặc biệt rain_heavy).
- Tất cả 22 cue vẫn `RENDERED_CANDIDATE` + `REQUIRES_PRESENTATION_ADAPTER` trong manifest — chưa nối runtime, chưa phải final.
- Issue #116 lượt này: đọc được nội dung issue (body, qua trang công khai) — không có chỉ đạo mới trong body so với DEC-MEDIA-P0; phần comment không render qua bản text và connector `issue_read` vẫn nằm ngoài tập read-only đã duyệt (cần thẻ duyệt write-capable) nên không treo chờ trong lượt chạy định kỳ. Trạng thái cuối đã biết vẫn là 6 comment (từ checkpoint 06); ACK checkpoint 07 + media PR vẫn chờ thẻ duyệt của luồng chính.
- Khối tiếp theo: (e) tiếp — pack SFX/UI còn lại theo cue ID (146 SFX + 27 UI), hoặc VO dự thảo campaign khi cửa sổ được xác nhận. KHÔNG mở lại hàng đợi đồ họa cũ.
