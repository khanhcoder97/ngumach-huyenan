# MEDIA-02 — WO37 M-E Checkpoint 2a: SFX coverage audit + proposal

- Ngày: 2026-11-11 (JST)
- Nhánh: `muse/media-production-20261104` — base integration `9ac73dc`
- Quyết định: DEC-MEDIA-P0-20261105 · Work Order 37 (M-E) · Gói 38 mục 4
  ("Tiếp motion/continuity, score/stems/transitions/intensity/SFX/VO/
  ambience còn lại bằng thay đổi asset thật")
- Trạng thái: **COVERAGE_AUDIT** — kiểm toán phủ sóng + bảng đề xuất, KHÔNG
  phải audio mới. Không file audio nào được render, không file runtime
  nào bị sửa; runtime audio giữ nguyên 783 file.

## 1. Vì sao khối này, vì sao bây giờ

M-E CP1 (2026-11-09) đã đóng ambience variants và ghi rõ: phần SFX còn
lại là M-E CP2 (composed SFX) — chờ quyết định của Codex. Checkpoint
này là bước chuẩn bị mà WO37 M-E quy định sẵn ("Dùng cue/skill ID đã
có nguồn; thiếu ID gửi proposal, không hardcode runtime key mới"): đo
chính xác bộ SFX đã giao phủ được bao nhiêu trong hai baseline yêu cầu
— catalogue thiết kế 63 soundKey của Codex và danh sách yêu cầu M-E
của WO37 — rồi gửi bảng thiếu + đề xuất ID cho Codex quyết, thay vì
để Codex quyết trong tối. Không tự sáng tác SFX, không tự thay cue
ported bằng cue composed.

## 2. Đo đạc (từ byte thật, validator độc lập)

Baseline thiết kế: `Implementation/Content/DesignBaselines/audio_cues_v1.json`
(63 soundKey: 54 SFX + 5 AMBIENCE + 4 MUSIC, owner Codex, trạng thái
DESIGN_ONLY). Bộ đã giao: `SFX_UI_pack_v1.json` (173 cue) +
`MUSIC_AMBIENCE_pack_v1.json` (22 cue, ported) +
`MUSIC_COMPOSED_pack_v1.json` (13) + `AMBIENCE_COMPOSED_pack_v1.json` (13),
đối chiếu với `Client/Assets/AudioManifests/game_audio_v1.json` (195 cue).

- **63/63 catalogue key COVERED_VERIFIED**: 54 key SFX khớp
  `SFX_UI_pack_v1` (file runtime v01 WAV kiểm sha256 + size +
  ffprobe codec pcm_s16le 48 kHz + duration khớp pack); 9 key
  MUSIC/AMBIENCE khớp cả bản ported (`MUSIC_AMBIENCE_pack_v1`, OGG
  Vorbis 48 kHz stereo, 16,0 s) lẫn bản composed
  (`MUSIC_COMPOSED`/`AMBIENCE_COMPOSED_pack_v1`). Tổng **72 file
  kiểm lại từ byte thật**, 0 mismatch, 0 LFS pointer.
- **Hợp nhất đúng:** tập cueKey của hai pack SFX/UI + music/ambience
  == đúng tập 195 cue của game manifest (kiểm bằng tập hợp, không
  chỉ đếm số). Bindings: skills 30, monsters 30, bosses 12, maps 46,
  NPCs 83, companions 10, cinema 20.
- **Mở rộng ngoài catalogue: 119 cue SFX/UI** (không tính 22
  music/ambience): BOSS +35, MONSTER 24, UI +10, WORLD +2, LIFE 8,
  PVP 8, FORGE 7, TRADE 5, QUEST +2, GUILD 4, CINEMA 4, PET 3,
  ACCOUNT 3, COSMETIC 2, CRAFT 2. Trong đó: BOSS = 12 intro +
  14 warning + 12 success; MONSTER = 8 họ × (attack/hurt/death).

## 3. Đối chiếu yêu cầu WO37 M-E (12 mục)

| Yêu cầu | Kết luận | Bằng chứng |
|---|---|---|
| Vật liệu bước chân | COVERED | step_stone / step_wood / step_mud + water_splash + mount_step |
| 5 weapon | QUESTION | Chỉ có basic_blade (1 cue chung cho cả 5 vũ khí) |
| 30 skill cast-impact-miss | COVERED_PER_CATALOGUE | 30/30 cue skill (1/skill, đúng skillId) + miss / projectile_hit / heavy_hit chung |
| guard-counter | PARTIAL | Counter có (metal_parry, SK-MK-01); guard-expire THIẾU |
| boss warning | COVERED | 14 warning; 12 boss đủ intro/warning/success; 3 cảnh báo Mãng Cốt khớp §4 |
| loot/equip/consume/inventory-full | COVERED | pickup ×3, equip ×2, potion_use, inventory_full |
| quest | COVERED | discovery / completed / accepted / journal_update |
| NPC | COVERED_BY_SHARED_CUE | 83 NPC → panel_open/panel_close; spokenVoice=null |
| craft/forge | COVERED | CRAFT 2 + FORGE 7 |
| market | COVERED | TRADE 5 (request/offer_locked/complete/buy/sell) |
| water/weather | COVERED | 6 cue nước + 13 ambience (mưa/nước/gió…) |
| cinema | COVERED | 4 stinger + 20 scene binding |

Tổng: 8 COVERED, 1 COVERED_PER_CATALOGUE, 1 COVERED_BY_SHARED_CUE,
1 PARTIAL, 1 QUESTION.

## 4. Đề xuất + câu hỏi gửi Codex (ID đề xuất, KHÔNG phải runtime key)

- **P-GUARD (GAP duy nhất có nguồn trích dẫn):**
  `SFX/COMBAT/guard_expire`, trigger đề xuất
  `GUARD_WINDOW_EXPIRED_UNHIT`. Nguồn: Audio Direction §2 —
  "guard có tiếng chuyển thế nhỏ nếu sau này bổ sung cue;
  metal_parry chỉ phát khi counter confirmed. Cửa guard hết mà
  không bị đánh không có tiếng đỡ chuẩn." Lưu ý: cue này không được
  phát khi counter confirmed (đó là việc của metal_parry).
- **P-WEAPON (QUESTION):** ứng viên `SFX/COMBAT/dao_swing`,
  `SFX/COMBAT/brush_stroke`, `SFX/COMBAT/mace_swing`,
  `SFX/COMBAT/bow_string` — chỉ khi Codex muốn swing riêng từng vũ
  khí; basic_blade giữ làm mặc định chung. Cơ sở: Audio Direction §1
  cho identity vật liệu riêng từng class.
- **P-GRASS (QUESTION):** ứng viên `SFX/WORLD/step_grass` — map
  production có cỏ, catalogue chỉ định nghĩa stone/wood/mud; đi trên
  cỏ hiện không có tiếng bước chân.
- **Q-PHASES (QUESTION, không đề xuất ID):** "30 skill
  cast-impact-miss" nghĩa là 1 cue/skill (thiết kế catalogue hiện
  tại) hay 3 pha/skill (+60 cue)? Không bịa 60 ID trước khi cách đọc
  được chốt.
- **Q-GRASS:** cỏ cần cue bước chân riêng, hay đi cỏ giữ im / tái dùng
  mud? (gắn P-GRASS).
- Không đề xuất thoại NPC: spoken dialogue là scope exclusion trong
  game manifest ("Spoken NPC dialogue/voice acting").

Validator độc lập `check_sfx_coverage_me_cp2a_v1.py`: **PASS — 700 checks,
0 mismatches** (đọc lại toàn bộ nguồn, hash + ffprobe lại 72 file,
tính lại mọi số đếm, kiểm evidence từng yêu cầu, kiểm proposal ID
không trùng cueKey hiện hữu và không mang runtime path/binding).

## 5. Deliverable

- Manifest: `Implementation/Content/Audio/Deliveries/SFX_COVERAGE_ME_CP2A_v1.json`
  (63 coverage entries + 12 requirements + 3 proposals + 2 questions)
- Builder: `Tools/MediaProduction/Muse/build_sfx_coverage_me_cp2a_v1.py`
- Validator: `Tools/MediaProduction/Muse/check_sfx_coverage_me_cp2a_v1.py`
- Báo cáo này + validation JSON:
  `Implementation/Reports/MuseMedia/MEDIA02_WO37_ME_CP2A_VALIDATION_20261111.json`

## 6. Giới hạn / khuyết điểm

- Đây là kiểm toán phủ sóng, KHÔNG phải nghiệm thu nghe:
  NOT_AUDITIONED vẫn giữ cho mọi cue; verdict COVERED nghĩa là
  "có cue + file thật đúng sha", không nghĩa là "nghe hay" hay "đúng
  thiết kế âm".
- Phạm vi kiểm byte ở đây giới hạn 72 file đại diện cho 63 key
  catalogue (bằng chứng cho claim phủ sóng mới). Không đo lại
  loudness, không kiểm toán lại pack CP08 — theo Gói 38 (không lặp
  checkpoint trên byte không đổi khi không có binary/policy/tool delta).
- P-GUARD / P-WEAPON / P-GRASS chỉ là ID + trigger đề xuất; chưa có
  audio, chưa có binding, chưa vào runtime. Sáng tác chúng là M-E CP2
  và vẫn chờ quyết định Codex.
- R-WEAPON và Q-PHASES là cách đọc mơ hồ trong câu chữ WO37, không
  phải lỗi của bộ đã giao: catalogue của Codex chỉ định nghĩa 1 cue
  vũ khí và 1 cue/skill, và bộ đã giao khớp đúng catalogue đó.

## 7. Khối tiếp theo

M-F CP2 (palette-adoption re-mix) vẫn chờ đạo diễn/Codex chọn voice;
M-E CP2 (composed SFX) chờ Codex quyết trên bảng đề xuất của
checkpoint này (P-GUARD / P-WEAPON / P-GRASS / Q-PHASES). 32 shot
motion vẫn chờ character lock cho final picture. Full 720p OGV set
vẫn chờ quyết định ngân sách của Codex. Không checkpoint
fresh-clone/hash lặp lại trên byte không đổi (Gói 38).

## Scope audit

- Content commit `f1b77e1`: **3 paths / 0 violations**
  (base `9ac73dc`).
- Cumulative from merge-base `cf17178` at the content commit:
  **2222** paths / 1 known `.gitattributes` merge-base artifact
  (byte-identical with integration `9ac73dc`, md5
  `f8376604708a8b9e695a0b4a191191d2`, not a real divergence).
  The report commit adds exactly 2 files (this report + validation
  JSON), so the head count is cumulative + 2.
