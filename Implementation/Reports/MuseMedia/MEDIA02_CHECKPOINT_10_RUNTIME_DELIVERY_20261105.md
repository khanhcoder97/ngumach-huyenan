# MEDIA-02 CHECKPOINT 10 — M6 runtime delivery (2026-11-05)

## Khối vừa hoàn thiện

M6 runtime delivery: copy có kiểm chứng toàn bộ deliverable media đã đo/kiểm
chứng ở checkpoint 01–09 sang cây runtime Godot (`ClientGodot/assets/`),
kèm 2 manifest runtime để Codex dùng làm dữ liệu cho presentation adapter.
Không viết code Godot (.gd/.tscn/.cs) — phần nối vào scene/code thuộc Codex.

## Kết quả đo đạc / kiểm chứng (byte thật, không PASS giả)

Tool: `Tools/MediaProduction/Muse/build_runtime_delivery.py`
(sha `3b975c5b887d0f1817f471b422b2b937e0608d4403c0c718da577de110d5a7a4`).
Mỗi file copy đều phải qua 4 cửa kiểm tra, lỗi nào cũng dừng tool
(exit != 0): nguồn là byte thật (không phải con trỏ LFS) → sha256 khớp
bản ghi checkpoint 04/07/08 → size khớp `size_bytes` → ffprobe duration
khớp `duration_s` (±0,02 s). Kết quả: **0 lỗi**.

| Nhóm | Số file | Nguồn kiểm chứng |
|---|---|---|
| Nhạc + ambience runtime OGG | 22 | checkpoint 07 (`MUSIC_AMBIENCE_pack_v1.json`) |
| SFX + UI runtime WAV (173 cue × 3 variant) | 519 | checkpoint 08 (`SFX_UI_pack_v1.json`) |
| VO P0 dự thảo (3 take + timeline 72 s) | 4 | checkpoint 04 (`P0_VO_manifest_v1.json`) |
| **Tổng audio runtime** | **545** | **49,5 MB** |
| Timing JSON + SRT, 20 cảnh | 40 | checkpoint 01/05/06 (SRT sha khớp manifest) |
| P0 animatic MP4 + OGV + poster | 3 | đã có từ checkpoint 03; xác minh lại sha, khớp |

- Tổng file mới vào runtime: 585 audio/timing + 2 manifest runtime.
- Animatic MP4 `a625043c…`, OGV `7c0fdb29…`, poster `ea9d4228…` — khớp
  checkpoint 03, không copy lại.
- SRT: 20/20 sha khớp manifest; timing JSON sha ghi mới vào manifest runtime.

## Deliverable

- `ClientGodot/assets/audio/` — `music/*.ogg` (9), `ambience/*.ogg` (13),
  `sfx/**/*.wav` (519), `vo/p0/*.wav` (4) + manifest runtime.
- `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json`
  (sha `eb4461ae1a1fc9f4ec176cd641f785bccf58d117dd835fc8df1abcf4a1e00d95`):
  545 entry, mỗi entry có cueKey/variantId, đường dẫn runtime + nguồn,
  sha256, size, codec, duration, loudness/true-peak từ pack.
- `ClientGodot/assets/cinematics/timing/` — `CIN_001…CIN_020_timing_v1.json`
  + `CIN_001…CIN_020_vi.srt` (40 file).
- `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json`
  (sha `5d24e12f4b0ecc2cdca6c939b7e03630401520270e93807d0ebd5ec99cebab06`):
  animatic đã xác minh + 20 cảnh (63 shot / 378 s).

## Giới hạn / khuyết điểm (ghi rõ, không giấu)

- Tất cả cue vẫn `RENDERED_CANDIDATE` / VO vẫn `DRAFT_NOT_FINAL_VO`:
  file đã nằm trong cây runtime nhưng **chưa nối vào Godot** — việc wiring
  scene/code là presentation adapter của Codex; manifest này chỉ là dữ liệu
  cho adapter, không phải code runtime.
- Chỉ có `CIN_001_S05` (24.8–28.5 s, bản B) là DECIDED; mọi cửa sổ thoại
  khác vẫn `PROPOSED_ANIMATIC_PLACEMENT`, chờ director/Codex xác nhận.
- VO là bản dự thảo TTS (giọng hư cấu hệ thống, không clone giọng thật),
  chưa nghe thử bằng tai; S05 nóng hơn 2 take kia ~5,5 LUFS (ghi từ cp04).
- Không phải mix PASS: chỉ đo từng cue/file riêng lẻ, không đo mix phối hợp,
  không đo ducking; vòng lặp rain_heavy (seam indicator 0,0538, cp07) vẫn
  cần nghe thử bằng tai trước khi kết luận.
- Animatic vẫn ở mức storyboard, chưa phải final picture; shot cần
  character lock vẫn chờ keyframe.

## Trạng thái repo

- Issue #116 vẫn 7 comment, không có chỉ đạo mới từ chủ dự án/Codex kể từ
  comment 6649909991 (ACK cp03–07 + PR #119).
- Integration HEAD không đổi: `cf17178`. Nhánh media: head `e3e9800`
  trước checkpoint này; commit checkpoint 10 `e1e558b` ĐÃ PUSH
  (ls-remote xác nhận; scope audit 682 paths, 0 violations;
  chỉ 4 object LFS mới upload — 7,7 MB — vì phần lớn blob audio đã có
  trên remote từ nguồn PackV1). PR #119 nay có 12 commit.
- ACK comment checkpoint 10 trên issue #116 + cập nhật PR: CẦN thẻ duyệt
  của chủ dự án qua GitHub connector — ghi rõ để luồng chính xử lý,
  lượt chạy này không treo chờ.

## Khối tiếp theo

VO dự thảo campaign (M3) khi cửa sổ thoại được xác nhận, hoặc M8 handover/
QA liên tục. PR #119 đang mở — commit checkpoint 10 sẽ vào PR khi push.
