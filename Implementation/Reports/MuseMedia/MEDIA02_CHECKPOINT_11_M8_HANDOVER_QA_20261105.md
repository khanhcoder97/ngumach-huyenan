# MEDIA-02 CHECKPOINT 11 — M8 handover/QA (2026-11-05)

## Khối vừa hoàn thiện

M8 handover/QA: bàn giao hợp nhất toàn bộ MEDIA-02 (checkpoint 01–10) cho
Codex/chủ dự án + kiểm chứng lại liên tục (continuous QA) toàn bộ deliverable
đối chiếu byte thật. Không sản xuất asset mới, không sửa timing/SRT/audio —
chỉ kiểm chứng lại và đóng gói bàn giao.

## Kết quả kiểm chứng lại (byte thật, không PASS giả)

### 1. Runtime delivery kiểm chứng lại — PASS, 0 mismatch

Tool mới: `Tools/MediaProduction/Muse/verify_runtime_delivery.py`
(sha `dc53d6c04f9ff6544003d66b56038fed9187cb867cc3628d8df5e1ab58755709`).
Đối chiếu từng file runtime với 2 manifest checkpoint 10 (tồn tại, không
phải con trỏ LFS, size, sha256; audio thêm ffprobe codec/sample rate/kênh/
thời lượng ±0,02 s). Kết quả trong
`MEDIA02_CHECKPOINT_11_RUNTIME_REVERIFY_20261105.json`:

| Nhóm | Số file kiểm | Kết quả |
|---|---|---|
| Audio runtime (22 nhạc/ambience + 519 SFX/UI + 4 VO P0) | 545 | khớp manifest, 0 mismatch |
| Animatic P0 (MP4 + OGV + poster) | 3 | khớp sha checkpoint 03, 0 mismatch |
| Timing JSON 20 cảnh | 20 | khớp sha manifest, 0 mismatch |
| SRT 20 cảnh | 20 | khớp sha manifest, 0 mismatch |

### 2. Source pack kiểm chứng lại — PASS, 0 mismatch

Chạy lại nguyên vẹn tool checkpoint 09
(`Tools/MediaProduction/Muse/validate_media_deliveries.py`, không sửa tool)
với đầu ra mới
`MEDIA02_CHECKPOINT_11_SOURCE_REVALIDATION_20261105.json`:

- Audio nguồn: 1093 file (44 nhạc/ambience + 1038 SFX/UI + 11 stem P0)
  khớp byte/sha/codec/48 kHz/kênh/thời lượng, 0 con trỏ LFS.
- Timing + SRT: 20/20 cảnh (63 shot × 6 s = 378 s), 21 thoại = 21 cue SRT,
  UTF-8 strict + NFC, khớp từng ký tự.
- Animatic: 12/12 panel khớp sha, MP4/OGV 640×360 72 s; VO P0: 3/3 take
  khớp sha/thời lượng và vừa cửa sổ.
- Ghi chú duy nhất (đã biết từ checkpoint 03): OGV `avg_frame_rate 0/0`
  do Theora gộp frame giữ nguyên — thời lượng vẫn 72 s, không phải lỗi.

## Kho bàn giao MEDIA-02 — checkpoint 01–10

Tất cả trên nhánh `muse/media-production-20261104`, base integration
`cf17178` (không đổi). PR bàn giao: **#119 — OPEN, 13 commit, 682 file,
head `5d8cc70`, chưa merge**.

| Checkpoint | Commit | Nội dung bàn giao |
|---|---|---|
| 01 | `440791e` | Re-baseline tại cf17178; P0 timing 12 shot/72 s + SRT (CIN_001_S05 DECIDED bản B 24.8–28.5 s) |
| 02 | `37c940c` | Loudness/true peak 11/11 stem P0 + bảng stem theo shot (PROPOSED_CANDIDATE) |
| 03 | `8be1af2` | Animatic P0 72 s/12 shot: MP4 + OGV + poster + 12 panel (storyboard, chưa final picture) |
| 04 | `8d25207` | VO dự thảo 3 câu P0 (TTS giọng hư cấu) + timeline 72 s |
| 05 | `5571537` | CIN_006 timing 18 s/3 shot + SRT (Q3/Q4 DEC-MEDIA-P0) |
| 06 | `5725caf` | Campaign timing 16 cảnh còn lại: 48 shot/288 s, 17 cue (tất cả PROPOSED) |
| 07 | `1db3f23` | Pack nhạc + ambience 22/22 cue đo từ byte thật (runtime OGG + master FLAC) |
| 08 | `0ea00b1` | Pack SFX/UI 173 cue × 3 variant = 1038 file đo từ byte thật |
| 09 | `18e5887` | Cross-validation toàn bộ deliverable vs byte thật — PASS, 0 mismatch |
| 10 | `e1e558b` | Runtime delivery: 545 audio + 40 timing/SRT + animatic vào `ClientGodot/assets/` + 2 manifest runtime |
| 11 (lượt này) | — | M8 handover/QA: kiểm chứng lại runtime + nguồn (PASS) + tài liệu bàn giao này |

Đường dẫn deliverable chính (trên nhánh media):

- Timing/SRT: `Implementation/Content/Narrative/Deliveries/CIN_001…CIN_020/`
  + `CAMPAIGN_timing_manifest_v1.json`
- Pack audio: `Implementation/Content/Audio/Deliveries/MUSIC_AMBIENCE_pack_v1.json`,
  `SFX_UI_pack_v1.json`
- Animatic: `Art_Source/Cinematics/P0_Animatic/` + `ClientGodot/assets/cinematics/`
- VO P0: `Art_Source/Audio/Muse/VO/P0_DRAFT/`
- Runtime: `ClientGodot/assets/audio/` + `ClientGodot/assets/cinematics/`
  + `RUNTIME_AUDIO_manifest_v1.json` / `RUNTIME_CINEMATICS_manifest_v1.json`
- Báo cáo: `Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_*.md`
- Tool: `Tools/MediaProduction/Muse/*.py` (build/measure/validate/verify)

## Quyết định còn mở — cần director/Codex (không tự chốt)

- **D1 — Xác nhận cửa sổ thoại PROPOSED:** CIN_002 7.0–11.0 s, CIN_004
  7.5–9.5 s, CIN_006 12.5–17.5 s, campaign 17 cue (CIN_003/005/007–020).
  Chỉ CIN_001_S05 (24.8–28.5 s, bản B) là DECIDED. Chưa xác nhận thì VO
  dự thảo campaign (17 cue còn lại) vẫn bị chặn.
- **D2 — Nghe thử bằng tai:** vòng lặp rain_heavy (seam indicator 0.0538,
  checkpoint 07); VO S05 nóng hơn 2 take kia ~5,5 LUFS — cần gain staging
  trước khi chốt mix.
- **D3 — Presentation adapter (Codex):** nối 545 file audio runtime +
  20 timing/SRT + animatic vào scene/code Godot. Manifest runtime chỉ là
  dữ liệu cho adapter, không phải code.
- **D4 — Character lock / final picture:** 4 khuyết điểm panel animatic
  còn nguyên (CIN_001_S03 chuông vẽ rắn; CIN_001_S06 đọc như warden thay
  vì Ly An; CIN_004_S01 sừng gãy chưa rõ; CIN_004_S03 nghiêng thay vì
  strict top-down). Shot cần lock vẫn chỉ chặn final picture, không chặn
  timing/audio/subtitle.
- **D5 — VO dự thảo campaign:** chờ D1 xác nhận cửa sổ.
- **D6 — Review/merge PR #119:** quyết của chủ dự án/Codex. Muse không
  tự merge.

## Checklist bàn giao

Muse đã xong (MEDIA-02 M1–M8): inventory → P0 animatic → campaign video
timing → nhạc → SFX/ambience → VO P0 → runtime delivery → QA/handover.
Codex cần làm: review PR #119, trả lời D1–D4, làm presentation adapter
(D3), chốt VO campaign sau D1.

## Trạng thái repo

- Issue #116 vẫn 7 comment, không có chỉ đạo mới kể từ comment 6649909991
  (ACK checkpoint 03–07 + PR #119, 2026-11-05 04:45 UTC). DEC-MEDIA-P0
  không đổi.
- Integration HEAD không đổi: `cf17178`. Nhánh media: head `5d8cc70`
  trước checkpoint này; commit checkpoint 11 sẽ push sau scope audit.
- ACK comment checkpoint 11 trên issue #116: CẦN thẻ duyệt của chủ dự án
  qua GitHub connector — ghi rõ để luồng chính xử lý, lượt chạy này không
  treo chờ.

## Giới hạn / khuyết điểm (ghi rõ, không giấu)

- Tất cả cue vẫn `RENDERED_CANDIDATE` / VO vẫn `DRAFT_NOT_FINAL_VO`:
  file đã trong cây runtime nhưng chưa nối vào Godot (D3, việc của Codex).
- Không phải mix PASS: chỉ đo/kiểm từng cue/file riêng lẻ, không đo mix
  phối hợp, không đo ducking; chưa nghe thử bằng tai (D2).
- Cửa sổ campaign vẫn PROPOSED (D1); VO campaign chưa làm (D5, chờ D1).
- Animatic vẫn mức storyboard, chưa final picture (D4).

## Khối tiếp theo

VO dự thảo campaign (17 cue) ngay khi D1 được xác nhận; nếu chưa có xác
nhận, M8 QA liên tục: kiểm chứng lại sau mỗi lần integration merge hoặc
khi PR #119 có review mới.
