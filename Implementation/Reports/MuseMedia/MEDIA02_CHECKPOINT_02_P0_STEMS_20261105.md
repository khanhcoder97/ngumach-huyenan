# MEDIA-02 — Checkpoint 02: đo loudness/true peak đủ pool stem P0 + bảng stem theo shot

- Ngày: 2026-11-05 (JST). Agent: Muse (chỉ media, theo policy `agent_scope_v2.json` / work 28 + work 29).
- Nhánh: `muse/media-production-20261104`. Base: integration `cf17178` (không đổi so với checkpoint 01; fetch đầu lượt không thấy HEAD mới).
- Khối này: (a) trong thứ tự sẵn sàng — đo nốt 8 file còn lại của pool stem P0 và lập bảng stem theo shot.
- Issue #116 đầu lượt: vẫn OPEN, 5 comment (tăng từ 4). Comment mới nhất (id 6644480512, khanhcoder97, 2026-11-04T23:06:26Z) là ACK của chủ dự án cho checkpoint 01 — commit 440791e đã push, scope audit 9 paths / 0 violations, không có chỉ đạo mới thay đổi DEC-MEDIA-P0. ACK + media PR vì vậy không còn là việc chờ của lượt này; media PR vẫn chờ luồng chính xử lý (worker không tự mở PR khi chưa có thẻ duyệt mới cho thao tác ghi GitHub).

## 1. Đo byte thật — đủ 11/11 file pool P0

Phương pháp: file đã là byte thật trong clone (đã `git lfs pull` chọn lọc ở checkpoint 01; không suy từ pointer). Đo bằng `ffprobe` (codec/duration) và `ffmpeg -af loudnorm` (integrated loudness / true peak / LRA, một lượt đo, không normalize). Đo lại 3 file của checkpoint 01 trong cùng lượt: kết quả khớp tuyệt đối (reveal −25,69/−12,28; ben_mua −21,92/−10,77; rain_light −27,48/−18,60) nên bảng dưới là một lần đo thống nhất.

| File | Codec | Kênh | Thời lượng | Cỡ (byte) | Integrated (LUFS) | True peak (dBTP) | LRA (LU) | SHA-256 (8 ký tự đầu) |
|---|---|---|---|---|---|---|---|---|
| sfx/cinema/reveal_v01.wav | pcm_s16le 48 kHz | mono | 2,9915 s | 287228 | −25,69 | −12,28 | 0,00 | 78291377 |
| sfx/cinema/tension_v01.wav | pcm_s16le 48 kHz | mono | 2,9915 s | 287228 | −25,67 | −12,11 | 0,00 | 779f17e3 |
| sfx/cinema/resolve_v01.wav | pcm_s16le 48 kHz | mono | 2,9915 s | 287228 | −25,68 | −14,09 | 0,00 | 1a9e1df7 |
| sfx/cinema/transition_v01.wav | pcm_s16le 48 kHz | mono | 2,9915 s | 287228 | −25,68 | −13,27 | 0,00 | b00e25bd |
| music/ben_mua.ogg | vorbis 48 kHz | stereo | 56,4706 s | 542912 | −21,92 | −10,77 | 1,90 | ad93ae03 |
| music/boss_mang_cot.ogg | vorbis 48 kHz | stereo | 36,9231 s | 392833 | −23,34 | −10,30 | 1,60 | 9c8a4d88 |
| music/quiet_discovery.ogg | vorbis 48 kHz | stereo | 64,0000 s | 465121 | −21,58 | −9,27 | 6,30 | 015e2494 |
| ambience/rain_light.ogg | vorbis 48 kHz | stereo | 16,0000 s | 216305 | −27,48 | −18,60 | 1,40 | 8bbf3398 |
| ambience/river_shore.ogg | vorbis 48 kHz | stereo | 16,0000 s | 187736 | −29,53 | −17,96 | 1,40 | 42e7983d |
| ambience/underwater.ogg | vorbis 48 kHz | stereo | 16,0000 s | 91898 | −33,02 | −19,12 | 1,50 | 18eb65c7 |
| ambience/rain_heavy.ogg | vorbis 48 kHz | stereo | 16,0000 s | 216345 | −27,47 | −17,35 | 1,30 | 7f9dbb6e |

SHA-256 đầy đủ trong file JSON cùng tên. Nhận xét chỉ từ số đo:

- Không file nào clip: true peak cao nhất là −9,27 dBTP (quiet_discovery), tức headroom tối thiểu 9,27 dB.
- 4 stinger cinema cùng mức integrated (−25,67…−25,68 LUFS, trừ reveal −25,69) — cùng tầng master, chỉ khác true peak; không phải 4 bản mix khác nhau về độ lớn.
- Ambience loop đúng 16,0000 s cả 4 file; underwater là file yên nhất pool (−33,02 LUFS / −19,12 dBTP), phù hợp vai trò nền dưới nước, không phải lỗi.
- Đây là đo từng cue riêng lẻ, KHÔNG phải PASS mix: chưa có VO, chưa có mix cảnh, nên không có con số −16 LUFS nào của cảnh để đối chiếu.

## 2. Bảng stem theo shot (PROPOSED_CANDIDATE — chưa khóa)

Bảng này chỉ dùng `candidateStems` đã ghi trong timing JSON P0 của từng cảnh, gán theo nội dung shot trong pack. Trạng thái stem của cả 3 cảnh vẫn là `CANDIDATE_POOL_NOT_LOCKED`; bảng này không đổi trạng thái đó và không thay timing JSON. Vị trí stinger chính xác trong shot chờ picture lock.

### CIN_001 — Nước không soi bóng (36 s)

| Shot | Thời gian | Vai trò đề xuất |
|---|---|---|
| S01 WIDE_STATIC | 0–6 s | rain_light (nền mưa) + river_shore (nền bờ nước) |
| S02 DETAIL_LOCKED | 6–12 s | river_shore + quiet_discovery ở mức thấp |
| S03 DETAIL_LOCKED | 12–18 s | river_shore + quiet_discovery ở mức thấp |
| S04 DETAIL_LOCKED | 18–24 s | river_shore + quiet_discovery ở mức thấp |
| S05 MEDIUM_STATIC, thoại DECIDED 24,8–28,5 s | 24–30 s | quiet_discovery ducked dưới VO + river_shore; VO chưa thu |
| S06 TOPDOWN_MATCH | 30–36 s | river_shore calm, quiet_discovery rút; reveal_v01 là stinger cấp cảnh, vị trí trong shot chờ picture lock |

### CIN_002 — Âm cuối dưới nước (18 s)

| Shot | Thời gian | Vai trò đề xuất |
|---|---|---|
| S01 GROUND_DETAIL (gợn nước) | 0–6 s | underwater + river_shore |
| S02 MEDIUM_STATIC, thoại PROPOSED 7,0–11,0 s | 6–12 s | river_shore ducked dưới VO + tension làm nền căng (đề xuất) |
| S03 TOPDOWN_MATCH (mặt nước lặng) | 12–18 s | river_shore only; tension out |

### CIN_004 — Vết đau của linh thú (18 s)

| Shot | Thời gian | Vai trò đề xuất |
|---|---|---|
| S01 WIDE_STATIC (boss) | 0–6 s | boss_mang_cot + river_shore |
| S02 DETAIL_LOCKED, VO off-screen PROPOSED 7,5–9,5 s | 6–12 s | boss_mang_cot ducked dưới VO off-screen + river_shore; reveal_v01 đề xuất tại nhịp dòng nước lệch, chờ picture lock |
| S03 TOPDOWN_MATCH | 12–18 s | river_shore calm; boss_mang_cot out |

### File pool chưa gán vào shot P0 nào (giữ nguyên, không ép gán)

- `music/ben_mua.ogg`: nhạc nền cấp chương Bến Mưa, không nằm trong candidateStems của cảnh P0 nào — không gán ép vào shot.
- `ambience/rain_heavy.ogg`: biến thể mưa nặng; mưa trong P0 là mưa nhẹ (rain_light) nên chưa dùng.
- `sfx/cinema/transition_v01.wav`, `sfx/cinema/resolve_v01.wav`: stinger liên cảnh, không gán trong shot; vị trí dùng chờ edit liên cảnh.

## 3. Giới hạn còn mở

- VO chưa thu (3 câu P0) nên mọi vị trí "ducked dưới VO" chỉ là kế hoạch mix, chưa phải mix thật.
- 2 vị trí thoại PROPOSED (CIN_002, CIN_004) vẫn chờ đạo diễn/Codex xác nhận; bảng stem của 2 shot đó đi theo vị trí đề xuất, sẽ sửa khi vị trí được chốt.
- Final picture vẫn chờ keyframe/character lock; bảng này chỉ chặn ở mức đó, không chặn timing/audio/subtitle.
- Công cụ tái lập: `Tools/MediaProduction/Muse/measure_p0_stems.py` (chạy ffprobe + loudnorm, xuất JSON cùng cấu trúc với file JSON kèm theo).

## 4. Khối tiếp theo

- (b) animatic P0 cho các shot không cần character lock, bám reference `Art_Source/BenMua_Concept_Rebuild_20261105`.
- (c) VO dự thảo 3 câu P0 theo cửa sổ đã khóa + VOICE_GUIDE (giọng hư cấu, không clone giọng người thật, không sample không license).
