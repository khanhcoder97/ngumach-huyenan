# MEDIA-02 · WO37 M-D checkpoint 10 — Ear-audition pack v2 (delta)

- **Checkpoint:** MEDIA-02 WO37 M-D CP10 (ear-audition pack v2, delta), 2026-11-12.
  Branch `muse/media-production-20261104`, content commit `3614d87`.
- **Trạng thái nghe: NOT_AUDITIONED.** Checkpoint này *chuẩn bị* buổi nghe cho
  toàn bộ audio mới giao kể từ pack v1 (M-D CP9, 2026-11-09, 196 item).
  Không mục nào trong pack được coi là PASS nghe — PASS/FAIL chỉ có khi
  người nghe ghi verdict theo từng item id.
- **Deliverable:** `EAR_AUDITION_PACK_v2_DELTA.json` (58 item mới) + 2 playlist
  mới (`ear_audition_08_v2mixes_playlist.txt`, `ear_audition_09_ambience_variants_playlist.txt`).
  Tổng thời lượng mới: **745,497 s (~12,4 phút)**.

## Vì sao là delta, không phải pack mới toàn bộ

Theo kỷ luật delta của Codex (Gói 38): 196 item của pack v1 **không hash lại
và không giao lại**. Pack v2 chỉ chứa 58 item mới, trỏ về pack v1 bằng id
(`supersedes` / `variantOf`). Nghe v1 + delta này gộp lại = **254 item**.
18 SFX draft đã có playlist nghe riêng giao trong M39-A và 40 render A/B
voice-palette đã có playlist riêng trong M39-B CP1 — pack này chỉ tham chiếu,
không nhân bản.

## Nội dung 58 item (đo mới từ byte thật)

| Nhóm | Số item | Nguồn | Tổng thời lượng |
|---|---|---|---|
| Mixes v2 | 14 | M-F CP2 (13 scene v2 + CIN_002 P0 v4) | 321,367 s |
| Ambience variants | 26 | M-E CP1 (13 cue × v02/v03) | 416,0 s |
| SFX drafts | 18 | WO39 M39-A CP1+CP2 (guard/grass + 4 weapon) | 8,13 s |

- **Mixes v2** (LUFS −26,28…−21,75; TP −9,61…−1,98 dBTP; 18,0 s/scene,
  prologue 87,367 s): tất cả 14 file đều là **PCM 16-bit / 48 kHz** (ghi rõ
  `codec` từng item trong pack) — khác 24-bit của ambience/SFX, nhưng đúng
  byte M-F CP2 đã giao, không render lại.
- **Ambience variants** (LUFS −33,02…−27,47; 16,0 s/cue): v02/v03 của từng
  cue, nghe đối chiếu với v01 master trong pack v1 (AMB-001…AMB-013).
- **SFX drafts** (LUFS −28,03…−23,45, trừ 3 file cỏ; TP −10,96…−8,0 dBTP):
  guard_expire, step_grass, dao_swing, brush_stroke, mace_swing, bow_string,
  mỗi cue 3 variant.

## Core pass v2 (nghe trước, ~3 phút)

| v1 (pack cũ) | v2 (pack này) | Thay đổi |
|---|---|---|
| MIX-030 PROLOGUE_mix_v1 | MIX2-001 CIN_000 v2 | Narration Helio → History; plumbing đã sửa — **điểm kiểm chính: narration có nghe rõ toàn bộ 87 s không** (v1 mất narration do lỗi plumbing) |
| MIX-027 P0 CIN_002 v3 | MIX2-002 CIN_002 v4 | Giọng palette; 3 câu thoại có vừa cửa sổ khóa không |
| MIX-003 CIN_006 v1 | MIX2-003 CIN_006 v2 | Overrun v1 +0,520 s — bản v2 có vừa cửa sổ không |
| MIX-015 CIN_018 v1 | MIX2-013 CIN_018 v2 | Overrun v1 S03 +0,280 s — bản v2 có vừa cửa sổ không; take người chơi vẫn VOICE_PLACEHOLDER_ONLY |
| MIX-002 CIN_005 v1 | — (không có v2) | Ly An, không đổi palette — v1 vẫn là bản nghe, overrun +0,160 s giữ nguyên chờ Codex |
| MIX-008 CIN_011 v1 | MIX2-006 CIN_011 v2 | Cửa sổ VO v1 chỉ thừa 8 ms — nghe đuôi câu v2 có bị cắt không |

## Kiểm chứng

- **Builder** `build_ear_audition_pack_cp10_v1.py`: đo mới toàn bộ 58 file
  từ đĩa (ffprobe + ffmpeg loudnorm, cùng cách gọi như
  `measure_music_ambience.py`), cross-check với checkpoint gốc của từng file:
  mixes ↔ M-F CP2 validation, ambience ↔ `AMBIENCE_COMPOSED_VARIANTS_pack_v1.json`,
  SFX ↔ M39-A CP1/CP2 validation + pack JSON. **0 mismatch.**
- **Validator độc lập** `check_ear_audition_pack_cp10_v1.py` (đo lại bằng
  code probe riêng, không dùng builder): **PASS 633/633**, 0 failure.
  Kiểm: sha256/size/duration/codec/48 kHz/LUFS/TP từng item; playlist 08/09
  đúng tập file + đúng thứ tự + đúng id; 18 SFX item đều có trong 2 playlist
  SFX đã giao (chỉ đọc, không sửa); mọi `supersedes`/`variantOf` đều tồn tại
  trong pack v1; core-pass update trỏ đúng id; không file `ClientGodot/` nào
  đổi. Kết quả: `MEDIA02_WO37_MD_CP10_VALIDATION_20261112.json`.
- **Scope audit** (`Tools/Coordination/check_agent_scope.py`, base =
  integration `f3db6b3`, head = content `3614d87`): khối này **5 paths /
  0 violations**; toàn nhánh **2360 paths / 1 violation `.gitattributes`** —
  artifact merge-base đã biết (2355 tại head 8e311aa + 5 file khối này).
  Commit báo cáo này thêm 2 file (báo cáo + validation JSON, đều trong root
  Reports cho phép) nên head count = 2362.

## Ghi chú đo lường (không phải lỗi audio)

- **step_grass v01–v03 (0,21 s): integrated LUFS KHÔNG xác định** — file ngắn
  hơn cửa sổ gating 400 ms của loudnorm nên ffmpeg trả `-inf`. Pack ghi
  `lufs: null` (không ghi số giả, không ghi `-Infinity` — JSON phải strict)
  và ghi mức bằng **pooled stereo RMS đo thật: −22,00 / −22,32 / −22,25 dBFS**
  (phương pháp: decode f32, RMS trên toàn bộ sample 2 kênh). Con số RMS này
  khác RMS −25,0 dBFS trong báo cáo M39-A CP1 vì phương pháp khác nhau;
  không so sánh chéo. TP vẫn đo được: −8,86 / −8,00 / −9,17 dBTP.
- Trong lúc build, builder từng dừng vì check codec chỉ cho phép 24-bit
  (prologue/mixes v2 là 16-bit) — đã sửa thành chấp nhận 16/24-bit và ghi
  codec từng item; đo lại toàn bộ, không file nào đổi.

## Giới hạn / bước tiếp theo

- Pack là *chuẩn bị* nghe, không phải kết quả nghe: toàn bộ vẫn
  **DRAFT_NOT_FINAL / NOT_AUDITIONED**. Verdict của người nghe (chủ dự án
  hoặc Codex) sẽ quyết định item nào thành khối sửa; ba overrun VO v1 vẫn
  giữ nguyên chờ Codex quyết khi review PR.
- M-F CP2 (14 mix v2) đã xong + kiểm chứng (M-G CP8) nhưng **payload đăng
  PR #119 / issue #116 vẫn chờ chủ dự án bấm duyệt** — không thuộc lượt chạy
  này, luồng chính xử lý.
- Không có chỉ đạo mới của Codex kể từ Gói 39 (issue #116 comment 6815238814);
  issue vẫn 30 comment, mới nhất là ACK 6819808977.
- Khối tiếp theo: 32 shot motion chờ character lock cho final picture;
  prologue v1 re-render (plumbing-fixed, narration Helio) chờ quyết
  owner/Codex; SFX skill chưa có phê duyệt sáng tác mới (DEC-MEDIA-SFX-DRAFT
  chỉ duyệt 18 variant, đã đủ 18/18).

Commits: nội dung `3614d87` (5 files) + commit báo cáo này. PR #119 vẫn HOLD;
Muse không tự merge.
