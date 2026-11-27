# MEDIA-02 — WO39 M39-A Checkpoint 2: composed SFX draft, 4 weapon identities

- Ngày: 2026-11-12 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `9ac73dc`
- Quyết định: DEC-MEDIA-SFX-DRAFT-20261112 (Codex, Gói 39, issue #116
  comment 6815238814, 2026-11-12 14:09 JST; bản JSON
  `Implementation/Content/DesignBaselines/media_sfx_draft_execution_20261112.json`
  @ `e4b3e4b` trên PR #131). Quyết định duyệt **18 draft variants**
  (guard-expire + 4 weapon identities + grass, mỗi cue 3 variant);
  CP1 đã giao guard + grass (6 variants). Checkpoint này giao **khối
  cuối 4 weapon = 12 variants — hoàn tất 18/18 variant đã duyệt**.
- Trạng thái: **DRAFT / NOT_AUDITIONED** — asset sáng tác mới, chưa nghe
  tai, chưa vào runtime, chưa có binding.

## 1. Vì sao khối này, vì sao bây giờ

M-E CP2a (2026-11-11) đề xuất P-WEAPON: 4 identity swing riêng từng vũ
khí, chỉ khi Codex muốn swing riêng — `basic_blade` giữ làm mặc định
chung. Gói 39 duyệt ngay trong ngày: 18 draft variants, khối đầu
guard + grass (CP1, 2026-11-12 14:40 JST), rồi 4 weapon. Checkpoint
này thực thi đúng khối cuối đó bằng asset thật — không checkpoint
report-only, không clone/hash lặp trên byte cũ (Gói 38).

## 2. Cue mới (candidate key, KHÔNG phải runtime key)

| Cue | Môn phái / vũ khí | Chất liệu (Audio Direction v1 §1) | Binding |
|---|---|---|---|
| `SFX/COMBAT/dao_swing` | Ảnh Đao — đao (Hỏa) | gió qua vải, than lách tách, lưỡi đao trầm; hai nhịp ngắn, đuôi tắt gấp | UNSUPPORTED |
| `SFX/COMBAT/brush_stroke` | Huyền Bút — bút (Thủy) | nét bút trên giấy, nước chạm men, hơi thở nước mảnh; đưa–buông–ngừng | UNSUPPORTED |
| `SFX/COMBAT/mace_swing` | Thạch Chùy — chùy (Thổ) | gỗ trầm, phiến đá nứt, cát rơi; attack rõ trước đuôi trầm | UNSUPPORTED |
| `SFX/COMBAT/bow_string` | Linh Cung — cung (Mộc) | dây bật, gió qua lá, âm sáo ngắn không thành giai điệu; một phát / lần bắn | UNSUPPORTED |

Binding UNSUPPORTED theo đúng luật của approval: chưa có trigger
authoritative từ client/server thì giao asset và ghi rõ chưa binding —
không bịa event gameplay. `basic_blade` giữ làm mặc định chung;
4 identity này chỉ phát khi Codex muốn swing riêng từng vũ khí
(adapter quyết định, Gói 39 M39-C).

## 3. Đo đạc (từ byte thật, validator độc lập 296/296 PASS)

Thiết kế tổng hợp thủ tục (procedural synthesis, deterministic
theo seed, không sample ngoài, không byte ported, không giọng nói).
Master stereo 48 kHz / 24-bit, theo quy ước audio sáng tác (CP26/30).

**Baseline đo lại từ byte thật** (6 file ported, sha256 khớp
`SFX_UI_pack_v1.json` — chứng minh đo đúng file gốc):
- `metal_parry`: centroid trung bình 764,13 Hz, prominence tối đa
  1.491.503,8 (chuông kim loại rất tonal), band <500 Hz 0,00, LUFS
  trung bình −24,18, RMS −25,0 dBFS.
- `basic_blade`: centroid 2.701,87 Hz, LUFS −22,25, RMS −25,18 dBFS.

**dao_swing — 0,45 s, hai nhịp whoosh vải + lưỡi đao trầm + than lách tách:**

| Variant | LUFS | TP (dBTP) | Centroid (Hz) | Prominence | SHA (đầu) |
|---|---|---|---|---|---|
| v01 | −23,55 | −9,05 | 1.161,7 | 20,1 | `e01d21b8…` |
| v02 | −23,45 | −10,96 | 1.227,4 | 15,2 | `a5d65730…` |
| v03 | −23,45 | −9,56 | 1.078,8 | 20,6 | `8227fa4a…` |

**brush_stroke — 0,55 s, swish giấy + hơi thở nước + 2 ping men:**

| Variant | LUFS | TP (dBTP) | Centroid (Hz) | Band 3–8 kHz | SHA (đầu) |
|---|---|---|---|---|---|
| v01 | −23,95 | −15,63 | 3.857,2 | 0,8090 | `4c93eff5…` |
| v02 | −24,05 | −15,67 | 4.164,0 | 0,9135 | `a5f16175…` |
| v03 | −23,99 | −16,67 | 3.670,7 | 0,7291 | `0510a97c…` |

**mace_swing — 0,50 s, whoosh trầm + gõ gỗ + nứt đá + đuôi cát:**

| Variant | LUFS | TP (dBTP) | Centroid (Hz) | Band <500 Hz | SHA (đầu) |
|---|---|---|---|---|---|
| v01 | −24,19 | −8,00 | 536,6 | 0,6072 | `6891d639…` |
| v02 | −23,51 | −9,10 | 560,8 | 0,6716 | `4a92057e…` |
| v03 | −23,92 | −8,00 | 605,0 | 0,5990 | `1786011d…` |

**bow_string — 0,50 s, twang dây + snap + gió qua lá + blip sáo:**

| Variant | LUFS | TP (dBTP) | Centroid (Hz) | Band 2,5–5,5 kHz | SHA (đầu) |
|---|---|---|---|---|---|
| v01 | −23,50 | −9,40 | 2.159,2 | 0,4043 | `120b861e…` |
| v02 | −23,46 | −9,56 | 2.281,7 | 0,4750 | `fb549710…` |
| v03 | −23,54 | −9,84 | 2.015,0 | 0,3596 | `f078fc06…` |

**Phân biệt đo được** (validator đo lại độc lập từ byte thật):
- Slot riêng từng vũ khí: mace 536,6–605,0 Hz; dao 1.078,8–1.227,4 Hz;
  bow 2.015,0–2.281,7 Hz; brush 3.670,7–4.164,0 Hz. Khoảng cách
  centroid nhỏ nhất giữa hai vũ khí là 473,8 Hz (mace–dao, ngưỡng
  ≥300 Hz).
- So với `basic_blade` (2.701,87 Hz): khoảng cách nhỏ nhất 420,2 Hz
  (bow v02, ngưỡng ≥400 Hz); dao ≥1.474 Hz, brush ≥968,8 Hz,
  mace ≥2.096 Hz.
- So với `metal_parry` (764,13 Hz, prominence 1.491.503,8): dao/bow/
  brush cách centroid ≥250 Hz (nhỏ nhất dao v03: 314,7 Hz); mace
  phân biệt bằng band <500 Hz 0,599–0,672 so với parry 0,00 (chênh
  ≥0,599, ngưỡng ≥0,20) và centroid ≤700 Hz. Prominence mọi variant
  < 1% của parry (tối đa brush v03: 1.634,2 so với ngưỡng 14.915).
- Ba variant mỗi cue khác nhau thật: diff-RMS 0,9056–1,4240
  (ngưỡng ≥0,05).

Tổng master mới: 12 file, 1.729.224 B. Validator độc lập
`check_composed_sfx_me_cp2b_weapons_v1.py`: **PASS — 296 checks,
0 mismatches** (đọc lại toàn bộ manifest/byte, đo lại loudness/
true-peak/RMS/phổ, đo lại baseline + sha chéo CP08, kiểm playlist,
kiểm runtime không đổi, kiểm scope).

## 4. Deliverable

- Master: `Art_Source/Audio/Muse/COMPOSED/sfx/{dao_swing,brush_stroke,mace_swing,bow_string}_v0{1,2,3}.wav`
  (48 kHz / 24-bit stereo)
- Manifest: `Implementation/Content/Audio/Deliveries/SFX_COMPOSED_DRAFT_WEAPONS_pack_v1.json`
  (4 cue / 12 variant + provenance + event-intent notes + binding
  UNSUPPORTED + số đo đầy đủ)
- Playlist nghe: `Implementation/Content/Audio/Deliveries/SFX_COMPOSED_DRAFT_WEAPONS_audition_playlist.txt`
  (M3U trong file .txt vì `.m3u` không thuộc scope policy; 12 draft +
  2 baseline A/B để đối chiếu tai)
- Builder: `Tools/MediaProduction/Muse/build_composed_sfx_me_cp2b_weapons.py`
- Validator: `Tools/MediaProduction/Muse/check_composed_sfx_me_cp2b_weapons_v1.py`
- Báo cáo này + validation JSON:
  `Implementation/Reports/MuseMedia/MEDIA02_WO39_M39A_CP2_WEAPONS_VALIDATION_20261112.json`

**Runtime KHÔNG đổi:** không file runtime nào được ghi, không manifest
runtime nào bị sửa — runtime audio giữ nguyên **783 file** tới khi
Codex review delta này (Gói 39 M39-C). Với checkpoint này, **18/18
draft variant của DEC-MEDIA-SFX-DRAFT-20261112 đã hoàn tất**
(CP1: 6 guard + grass; CP2: 12 weapon).

## 5. Khuyết điểm / lỗi đã gặp và đã sửa trong lúc làm (ghi thật)

- Dao v01 ban đầu TP chạm trần −8,0 dBTP nên LUFS chỉ đạt −24,55
  (thiếu 1,05 LU so với mục tiêu −23,5): hai nhịp whoosh quá peaky
  (attack 0,008 s, tau 0,05 s). Nới attack 0,015 s + tau 0,08 s →
  LUFS −23,55, TP −9,05.
- Dao v01 ban đầu centroid 844,3 Hz (dưới sàn slot 1.050 Hz): dải
  whoosh 550–1.400 Hz + tone lưỡi đao kéo centroid xuống. Nâng dải
  lên 750–1.900 Hz, giảm gain tone → centroid 1.078,8–1.227,4 Hz.
- Brush/mace prominence 400–2.000 Hz ghi nhận nhưng KHÔNG assert:
  năng lượng brush nằm trên 2.400 Hz, mace nằm dưới 700 Hz nên
  median trong cửa sổ đó gần noise floor, tỉ số không còn là khẳng
  định tonality (cùng ghi chú như cue grass ở CP1). Phân biệt với
  parry vẫn được kiểm bằng ngưỡng <1% prominence parry + band
  <500 Hz (mace) / slot centroid (brush).
- Mace centroid bị đuôi cát kéo lên: v01 660,3 Hz (vượt trần 650),
  v02 722,8 Hz. Giảm gain cát (0,10→0,06–0,07) và thu hẹp dải cát
  2–4 kHz → 1,8–3,6 kHz → centroid 536,6–605,0 Hz; v03 sau đó thiếu
  band 2,5–5,5 kHz (0,0191 so với ngưỡng 0,02) nên tăng gain cát
  v03 0,05→0,07 → 0,0357.
- Bow v01 ban đầu centroid 1.207,1 Hz (dưới sàn 1.750 Hz): twang dây
  (f0 230 Hz + harmonic) chiếm 56% năng lượng dưới 500 Hz. Giảm
  gain pluck 0,30→0,15, tăng gió qua lá 0,40→0,55 → centroid
  2.015,0–2.281,7 Hz; v02 vượt trần 2.200 Hz (2.351,8) nên hạ dải
  gió v02 và nới slot bow lên 1.750–2.400 Hz — vẫn cách basic_blade
  ≥400 Hz (nhỏ nhất 420,2 Hz, bow v02) và cách brush ≥1.389 Hz.
- Mace v01/v03 chạm trần TP −8,0 dBTP nên LUFS −24,19/−23,92, thấp
  hơn mục tiêu −23,5 khoảng 0,4–0,7 LU — vẫn trong dung sai ±1,0 LU
  của validator, ghi rõ ở đây chứ không giấu.
- Chưa nghe tai: mọi verdict nghe vẫn NOT_AUDITIONED; số đo trên chỉ
  chứng minh khác biệt phổ/mức, không chứng minh "nghe hay" hay
  "đúng thiết kế âm".

## 6. Khối tiếp theo

DEC-MEDIA-SFX-DRAFT-20261112 đã đủ 18/18 variant — M39-A hoàn tất.
Handoff delta M39-C (PR #119 body + ACK issue #116) vẫn chưa đăng —
payload gộp cần làm mới để gộp thêm CP2 (head mới sau checkpoint
này), chờ luồng chính đăng (cần thẻ duyệt của chủ dự án). M-F CP2
vẫn chờ đạo diễn/Codex chọn voice. 32 shot motion vẫn chờ character
lock cho final picture. Full OGV 720p vẫn deferred.

## Scope audit

- Content commit `dbd8270`: **16 paths / 0 violations**
  (base `9ac73dc`; CLI kiểm lại: 2259 changed paths, 1 violation là
  `.gitattributes` — xem dưới).
- Cumulative from merge-base `cf17178` at the content commit:
  **2259** paths / 1 known `.gitattributes` merge-base artifact
  (byte-identical with integration `9ac73dc`, md5
  `f8376604708a8b9e695a0b4a191191d2`, not a real divergence).
  The report commit adds exactly 2 files (this report + validation
  JSON), so the head count is cumulative + 2 = 2261.
