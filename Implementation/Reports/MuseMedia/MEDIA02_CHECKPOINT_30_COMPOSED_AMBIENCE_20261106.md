# MEDIA-02 CHECKPOINT 30 — Original composed ambience: all 13 AMBIENCE/* cues (2026-11-06)

## Khối vừa hoàn thiện

Checkpoint 26 đã sáng tác 9 cue nhạc + 4 stinger; ambience vẫn là bản
ported PackV1 (checkpoint 07 chỉ đo, không sáng tác). Checkpoint 30
**sáng tác nốt toàn bộ 13 cue ambience** — giường tiếng (bed) bằng
nhiễu lọc + bao biên gust/swell chậm + sự kiện rời rạc xác định
(giọt nước, crackle, clink kim loại, tiếng dế, tiếng gõ gỗ) — **không
sample ngoài, không byte ported, không giọng nói**. Bed đám đông
(thang_long_crowd, city_night) chỉ là nhiễu qua dải formant trôi chậm
nên theo cấu trúc không thể tạo thành lời nói có nghĩa.

Mục tiêu loudness của từng cue là **LUFS tích hợp đã đo của chính bản
ported tương ứng ở checkpoint 07**, để bed sáng tác ngồi đúng mức mix
mà các mix nháp P0 đã thiết kế quanh đó. Ported pack không đổi.

| Cue | Đích (ported CP07) | Master đo thật | Runtime OGG đo thật | Wrap jump |
|---|---|---|---|---|
| rain_light | −27,48 | −27,48 / −16,11 | −27,80 / −16,59 | 2e-06 |
| rain_heavy | −27,47 | −27,46 / −16,81 | −27,85 / −17,35 | 1e-06 |
| river_shore | −29,53 | −29,54 / −16,92 | −29,69 / −17,08 | 3e-06 |
| underwater | −33,02 | −33,02 / −20,21 | −33,11 / −20,68 | 1e-06 |
| waterfall | −29,31 | −29,31 / −16,02 | −29,53 / −16,02 | 0,0 |
| wind_canopy | −29,55 | −29,55 / −15,69 | −29,70 / −16,06 | 1e-06 |
| desert_wind | −29,57 | −29,57 / −17,85 | −29,93 / −17,26 | 5e-06 |
| mountain_wind | −29,56 | −29,56 / −16,19 | −29,55 / −16,18 | 4e-06 |
| cave_drips | −29,54 | −29,54 / −13,01 | −29,56 / −13,08 | 3e-06 |
| forge | −29,50 | −29,51 / −15,77 | −29,49 / −15,85 | 4e-06 |
| thang_long_crowd | −30,34 | −30,34 / −17,47 | −30,59 / −17,81 | 1e-06 |
| city_night | −30,34 | −30,34 / −16,55 | −30,40 / −16,66 | 4e-06 |
| rift | −30,48 | −30,49 / −21,29 | −30,46 / −21,30 | 2e-06 |

(LUFS / dBTP; master = WAV 48 kHz / 24-bit stereo, 16,0000 s; runtime
= OGG Vorbis q5. Wrap jump đo sau cấu trúc loop crossfade 0,25 s
của checkpoint 26; giá trị trước landing ghi trong pack JSON.)

- **Không file nào clip:** true peak cao nhất −13,01 dBTP (cave_drips),
  headroom tối thiểu 13 dB.
- **Độ lệch đích:** master khớp đích trong 0,01 LUFS ở cả 13 cue
  (runtime OGG lệch tối đa 0,36 LUFS do mã hóa Vorbis, trong dung sai
  của tool).
- **Vòng lặp:** mỗi cue 16,0000 s đúng; tail wrap 1,5 s + end-landing
  0,25 s như checkpoint 26; sự kiện rời rạc chỉ đặt trong [0,5–14,0] s
  để đuôi wrap giữ nguyên bed. Seam chỉ là chỉ số đo, không phải PASS
  nghe tai.
- **Runtime:** audio manifest 593 → **606 file** (composed 13 → 26);
  13 entry mới `category: composed_ambience`,
  `provenance: ORIGINAL_COMPOSED_BY_MUSE`,
  `assetState: COMPOSED_CANDIDATE` tại
  `ClientGodot/assets/audio/composed/ambience/`. Campaign totals
  không đổi (20 scene / 63 shot / 378 s / 21 cue).
- **Tổng audio gốc tới nay:** 26 cue composed (9 nhạc + 4 stinger +
  13 ambience); 541 file ported vẫn giữ provenance riêng, không tính
  là audio mới.

## Trạng thái GitHub

- Nhánh `muse/media-production-20261104`: nội dung ở commit ngay trước
  báo cáo này; PR #119 vẫn OPEN và HOLD, head b279182 (CP29). Issue
  #116 vẫn OPEN, 11 comment, cập nhật lần cuối 2026-11-05T18:30:17Z —
  không có chỉ đạo mới kể từ ACK checkpoint 08–26; integration vẫn ở
  f0859d0 (không có merge mới kể từ baseline CP28) nên không cần
  re-baseline M8.
- Mô tả PR #119 vẫn ghi checkpoint 01–26 — **cần luồng chính cập nhật
  mô tả PR (thêm checkpoint 27–30) qua GitHub connector**; lượt chạy
  định kỳ này không tự ghi qua connector vì cần thẻ duyệt của chủ dự án.

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/build_composed_ambience.py` (mới) | Composer ambience gốc: 13 cue, tổng hợp thủ tục bằng numpy/scipy (nhiễu lọc Butterworth, bao biên gust/swell, sự kiện rời rạc xác định, seed cố định 3000+idx); đo loudnorm + gain-stage tối đa 3 lượt; lưu manifest sau mỗi cue. |
| `Art_Source/Audio/Muse/COMPOSED/ambience/` (mới, 13 file) | Master WAV 48 kHz / 24-bit stereo, mỗi file 4.608.102 byte (58 MB qua Git LFS). |
| `ClientGodot/assets/audio/composed/ambience/` (mới, 13 file) | Runtime OGG Vorbis q5 (2,7 MB). |
| `Implementation/Content/Audio/Deliveries/AMBIENCE_COMPOSED_pack_v1.json` (mới) | Pack 13 cue: provenance, cấu trúc từng cue, master/runtime (SHA/size/codec/duration/LUFS/TP), seam stats. |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Thêm mục 3h: kiểm chứng 13 runtime OGG tại chỗ (SHA/size/duration) + đăng ký vào manifest audio; nhãn checkpoint 30 + ghi chú ambience. |
| `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json` | 606 file (593 → 606); composed 13 → 26. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Thêm `check_composed_ambience_pack()` (counts {ambience: 13}, provenance, kind, loop, duration 16,0 s, cả 2 mặt byte); tổng runtime kỳ vọng 593 → 606; nhãn checkpoint 30 + ghi chú. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Nhãn checkpoint 30. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build ambience — PASS
`build_composed_ambience.py` exit 0: 13/13 cue đúng 16,0000 s, master
khớp đích LUFS trong 0,01, true peak ≤ −13,01 dBTP, wrap jump ≤ 5e-06.

### 2. Runtime delivery — PASS
`build_runtime_delivery.py` exit 0: audio manifest `totalFiles` 606
(22 + 519 + 30 VO + 9 mix + 26 composed), 13 file ambience qua đủ các
cổng kiểm chứng; ported + composed cũ không đổi.

### 3. Source re-validation — PASS, 0 mismatch
`validate_media_deliveries.py` verdict PASS, gồm mục mới: composed
ambience pack 13/13 cue (26 file). JSON:
`MEDIA02_CHECKPOINT_30_SOURCE_REVALIDATION_20261106.json` (audio files
checked 1151, composed ambience cues 13).

### 4. Runtime re-verify — PASS, 0 mismatch
`verify_runtime_delivery.py` verdict PASS: 606 file runtime khớp
manifest (runtime_audio_files_checked 606 = totalFiles 606). JSON:
`MEDIA02_CHECKPOINT_30_RUNTIME_REVERIFY_20261106.json`.

### 5. Scope audit — 0 vi phạm
Diff 3 chấm từ merge-base so với integration `f0859d0`: **1153 path,
0 violations** (CP29: 1122 path ở commit nội dung e9d1ce1, 1123 path ở
head b279182 sau commit báo cáo; +30 path mới của checkpoint này: 13
master WAV + 13 runtime OGG + pack JSON + tool composer + 2 JSON kiểm
chứng; manifest audio + 3 tool sửa trong diff cũ nên không tăng số
đếm). Tất cả nằm trong các root media policy cho phép
(`Art_Source/Audio/Muse/`, `ClientGodot/assets/audio/`,
`Implementation/Content/Audio/Deliveries/`,
`Implementation/Reports/MuseMedia/`,
`Tools/MediaProduction/Muse/`). Nội dung ở commit `ad71e89`.

## Giới hạn còn lại

- DRAFT_NOT_FINAL / COMPOSED_CANDIDATE: chưa nghe tai — chất lượng
  bed, độ liền mạch vòng lặp và cân bằng mix chưa được nghiệm thu bằng
  tai người; loudness/true-peak đã đo từ byte thật. Việc nhận bed
  sáng tác (thay ported) là quyết định adapter của Codex tại review
  PR #119.
- Bed đám đông là nhiễu lọc, không chứa giọng nói thật hay lời nói có
  nghĩa — nhưng độ "giống đám đông" vẫn là nhận định nghe tai, chưa
  kiểm chứng.
- P0 mix v1/v2 vẫn dùng ambience ported (CP20/CP29); mix lại từ
  ambience sáng tác là follow-up, chưa làm ở checkpoint này.
- Final picture vẫn chờ keyframe/character lock; checkpoint này chỉ
  chặn ở mức đó, không chặn timing/audio/subtitle.
