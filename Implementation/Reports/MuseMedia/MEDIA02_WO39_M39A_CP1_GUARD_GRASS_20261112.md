# MEDIA-02 — WO39 M39-A Checkpoint 1: composed SFX draft, guard + grass

- Ngày: 2026-11-12 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `9ac73dc`
- Quyết định: DEC-MEDIA-SFX-DRAFT-20261112 (Codex, Gói 39, issue #116
  comment 6815238814, 2026-11-12 14:09 JST; bản JSON
  `Implementation/Content/DesignBaselines/media_sfx_draft_execution_20261112.json`
  @ `e4b3e4b` trên PR #131). Quyết định duyệt **18 draft variants**
  (guard-expire + 4 weapon identities + grass, mỗi cue 3 variant);
  checkpoint này giao **khối đầu guard + grass = 6 variants**. 4 weapon
  là khối tiếp theo (M39-A CP2).
- Trạng thái: **DRAFT / NOT_AUDITIONED** — asset sáng tác mới, chưa nghe
  tai, chưa vào runtime, chưa có binding.

## 1. Vì sao khối này, vì sao bây giờ

M-E CP2a (2026-11-11) đã đo phủ sóng SFX và gửi Codex 3 đề xuất ID
(P-GUARD / P-WEAPON / P-GRASS) + 2 câu hỏi (Q-PHASES / Q-GRASS); việc
sáng tác chờ quyết định Codex. Gói 39 quyết ngay trong ngày: duyệt
18 draft variants, khối đầu guard + grass, rồi 4 weapon; giữ catalogue
1 cue/skill + shared miss/impact theo event thật, không tự tạo 60 phase
key; guard-expire không được giả metal_parry/counter confirmed; giữ
original draft VO; giữ 640 runtime candidate; full 246 MB OGV 720p
deferred. Checkpoint này thực thi đúng khối đầu đó bằng asset thật —
không checkpoint report-only, không clone/hash lặp trên byte cũ (Gói 38).

## 2. Cue mới (candidate key, KHÔNG phải runtime key)

| Cue | Đề xuất | Trigger đề xuất | Binding |
|---|---|---|---|
| `SFX/COMBAT/guard_expire` | P-GUARD | `GUARD_WINDOW_EXPIRED_UNHIT` | UNSUPPORTED |
| `SFX/WORLD/step_grass` | P-GRASS | `FOOT_CONTACT_GRASS` | UNSUPPORTED |

Binding UNSUPPORTED theo đúng luật của approval: chưa có trigger
authoritative từ client/server thì giao asset và ghi rõ chưa binding —
không bịa event gameplay, không tổng hợp counter thành công.
`guard_expire` CHỈ phát khi cửa guard hết mà không bị đánh; khi
counter confirmed thì `metal_parry` (trigger `COUNTER_CONFIRMED`) mới
phát. `step_grass` chỉ phát trên mặt cỏ có flag authoritative; đá/gỗ/
bùn ướt giữ cue ported của chúng.

## 3. Đo đạc (từ byte thật, validator độc lập 186/186 PASS)

Thiết kế tổng hợp thủ tục (procedural synthesis, deterministic
theo seed, không sample ngoài, không byte ported, không giọng nói).
Master stereo 48 kHz / 24-bit, theo quy ước audio sáng tác (CP26/30).

**Baseline đo lại từ byte thật** (15 file ported, sha256 khớp
`SFX_UI_pack_v1.json` — chứng minh đo đúng file gốc):
- `metal_parry`: centroid trung bình 764,13 Hz, prominence tối đa
  1.491.503,8 (chuông kim loại rất tonal), LUFS trung bình −24,18,
  RMS −25,0 dBFS.
- `basic_blade`: centroid 2.701,87 Hz, LUFS −22,25, RMS −25,18 dBFS.
- `step_stone`: centroid 1.258,2 Hz, band 2,5–5,5 kHz 0,19, RMS −25,0.
- `step_wood`: centroid 503,53 Hz, band 0,07, RMS −25,0.
- `step_mud`: centroid 497,47 Hz, band 0,07, RMS −25,0.

**guard_expire — 0,50 s, hơi thở + thump lắng + sột soạt vải, KHÔNG
partial kim loại, KHÔNG attack sắc:**

| Variant | LUFS | TP (dBTP) | Centroid (Hz) | Prominence | SHA (đầu) |
|---|---|---|---|---|---|
| v01 | −28,03 | −10,00 | 1.151,3 | 25,3 | `8b7673db…` |
| v02 | −27,50 | −10,81 | 1.070,4 | 45,4 | `deb17650…` |
| v03 | −27,76 | −10,00 | 1.173,1 | 14,3 | `c6eed65c…` |

Khác biệt đo được so với baseline: centroid cách `metal_parry`
306–409 Hz (ngưỡng ≥250); prominence < 1% của parry (tối đa 45,4 so
với ngưỡng 14.915); êm hơn parry 3,32–3,85 LU (ngưỡng ≥2 LU — và còn
thận trọng hơn vì stereo đo cao hơn mono ~3 LU theo BS.1770);
centroid cách `basic_blade` 1.529–1.631 Hz (ngưỡng ≥1.000). Ba variant
khác nhau thật: diff-RMS 1,1478–1,2328 (ngưỡng ≥0,05).

**step_grass — 0,21 s, sột soạt khô + thud đất + tiếng lá gãy,
LUFS không đo được (<400 ms, cùng ghi chú như các footstep ported):**

| Variant | RMS (dBFS) | TP (dBTP) | Centroid (Hz) | Band 2,5–5,5 kHz | SHA (đầu) |
|---|---|---|---|---|---|
| v01 | −25,00 | −8,86 | 2.809,5 | 0,6333 | `a8f5aca9…` |
| v02 | −25,08 | −8,00 | 2.540,2 | 0,4968 | `ec3f5a9f…` |
| v03 | −25,00 | −9,17 | 2.867,6 | 0,6411 | `b0e7bccd…` |

RMS khớp đúng mức staging của họ footstep (−25,0 dBFS). Khác biệt đo
được: centroid cách `step_stone` 1.282–1.609 Hz, cách wood/mud
~2.040–2.370 Hz (ngưỡng ≥400); band 2,5–5,5 kHz cao hơn mỗi sibling
ít nhất 0,30 (ngưỡng ≥0,10). Ba variant khác nhau thật: diff-RMS
1,3926–1,4259.

Tổng master mới: 6 file, 614.052 B (3 × 144.102 B guard + 3 × 60.582 B
grass). Validator độc lập
`check_composed_sfx_me_cp2b_guard_grass_v1.py`: **PASS — 186 checks,
0 mismatches** (đọc lại toàn bộ manifest/byte, đo lại loudness/
true-peak/RMS/phổ, đo lại baseline + sha chéo CP08, kiểm playlist,
kiểm runtime không đổi, kiểm scope).

## 4. Deliverable

- Master: `Art_Source/Audio/Muse/COMPOSED/sfx/guard_expire_v0{1,2,3}.wav`
  + `step_grass_v0{1,2,3}.wav` (48 kHz / 24-bit stereo)
- Manifest: `Implementation/Content/Audio/Deliveries/SFX_COMPOSED_DRAFT_GUARD_GRASS_pack_v1.json`
  (2 cue / 6 variant + provenance + event-intent notes + binding
  UNSUPPORTED + số đo đầy đủ)
- Playlist nghe: `Implementation/Content/Audio/Deliveries/SFX_COMPOSED_DRAFT_GUARD_GRASS_audition_playlist.txt`
  (M3U trong file .txt vì `.m3u` không thuộc scope policy; 6 draft +
  4 baseline A/B để đối chiếu tai)
- Builder: `Tools/MediaProduction/Muse/build_composed_sfx_me_cp2b_guard_grass.py`
- Validator: `Tools/MediaProduction/Muse/check_composed_sfx_me_cp2b_guard_grass_v1.py`
- Báo cáo này + validation JSON:
  `Implementation/Reports/MuseMedia/MEDIA02_WO39_M39A_CP1_GUARD_GRASS_VALIDATION_20261112.json`

**Runtime KHÔNG đổi:** không file runtime nào được ghi, không manifest
runtime nào bị sửa — runtime audio giữ nguyên **783 file** tới khi
Codex review delta này (Gói 39 M39-C).

## 5. Khuyết điểm / lỗi đã gặp và đã sửa trong lúc làm (ghi thật)

- Playlist sai độ sâu đường dẫn: builder ghi `../../../` trong khi
  playlist nằm sâu 4 cấp (`Implementation/Content/Audio/Deliveries/`)
  nên đường dẫn trỏ nhầm `Implementation/Art_Source/...`. Validator
  bắt được cả 10 kiểm tra tồn tại file; đã sửa thành `../../../../`,
  render lại, validator về 186/186.
- Grass quá peaky ở bản thiết kế đầu (decay hàm mũ tau 0,03 s → crest
  ~18,7 dB, RMS staging không đạt −25 dBFS dưới trần TP). Đổi sang
  envelope attack/sustain/decay (sustain 0,12 s) để tiếng crush có
  body năng lượng.
- Grass thump ban đầu quá lớn (gain 0,30) kéo centroid xuống 1.085 Hz
  — rơi đúng slot wood/mud. Giảm thump còn 0,06–0,10 và hạ band
  rustle về 1,5–3,9 kHz → centroid 2.540–2.868 Hz.
- Guard v02 ban đầu band 600–1.400 Hz cho centroid 974 Hz (dưới sàn
  1.000 Hz đã đặt để giữ khoảng cách với parry). Nâng band lên
  700–1.500 Hz → 1.070,4 Hz.
- Hiệu chỉnh đo: ffmpeg upmix mono→stereo giảm mỗi kênh 0,707
  (−3,01 dB) nên RMS baseline đo bằng đường `-ac 2` sai 3 dB. Đã đo
  lại baseline bằng decode mono thật (`-ac 1`): cả 4 họ đều đúng
  −25,0 dBFS, khớp staging CP08. So sánh LUFS guard (stereo) với
  parry (mono) là phía thận trọng: stereo đo cao hơn mono ~3 LU
  theo BS.1770 nên khoảng cách êm thật còn rộng hơn con số headline.
- Grass prominence 400–2.000 Hz ghi nhận nhưng KHÔNG assert: năng
  lượng cue nằm trên 1.800 Hz nên median trong cửa sổ đó gần noise
  floor, tỉ số không còn là khẳng định tonality.
- Chưa nghe tai: mọi verdict nghe vẫn NOT_AUDITIONED; số đo trên chỉ
  chứng minh khác biệt phổ/mức, không chứng minh "nghe hay" hay
  "đúng thiết kế âm".

## 6. Khối tiếp theo

M39-A CP2 — 4 weapon identities (`dao_swing`, `brush_stroke`,
`mace_swing`, `bow_string`, mỗi cue 3 variant = 12 variant) theo đúng
approval DEC-MEDIA-SFX-DRAFT-20261112; `basic_blade` giữ làm mặc định
chung. M-F CP2 vẫn chờ đạo diễn/Codex chọn voice. 32 shot motion vẫn
chờ character lock cho final picture. Full OGV 720p vẫn deferred.
Handoff delta M39-C (PR #119 body + ACK issue #116 cho head `b1472f2`)
vẫn chờ luồng chính đăng (cần thẻ duyệt của chủ dự án) — payload đã
chuẩn bị cần thêm 1 dòng link approval Gói 39 + xác nhận Codex đã
review pin `b1472f2` (comment 6815238814) trước khi đăng.

## Scope audit

- Content commit `78ecd26`: **10 paths / 0 violations**
  (base `9ac73dc`).
- Cumulative from merge-base `cf17178` at the content commit:
  **2241** paths / 1 known `.gitattributes` merge-base artifact
  (byte-identical with integration `9ac73dc`, md5
  `f8376604708a8b9e695a0b4a191191d2`, not a real divergence).
  The report commit adds exactly 2 files (this report + validation
  JSON), so the head count is cumulative + 2 = 2243.
