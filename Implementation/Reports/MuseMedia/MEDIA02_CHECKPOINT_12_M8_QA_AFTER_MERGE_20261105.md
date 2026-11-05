# MEDIA-02 CHECKPOINT 12 — M8 QA liên tục sau merge integration f383233 (PR #118) (2026-11-05)

## Khối vừa hoàn thiện

M8 continuous QA sau lần merge integration đầu tiên kể từ checkpoint 11:
re-baseline lên integration HEAD mới + kiểm chứng lại toàn bộ deliverable
MEDIA-02 đối chiếu byte thật. Không sản xuất asset mới, không sửa
timing/SRT/audio — chỉ kiểm chứng lại và ghi nhận baseline mới.

## Re-baseline: integration cf17178 → f383233

- Integration HEAD mới: `f383233` — merge PR #118
  (`codex/benmua-combat-visuals-20261105`), 5 commit: `f31461a`,
  `80989d5`, `798c7ec`, `a75b538`, `8d627c6`. Tổng 81 file đổi.
- Phát hiện kỹ thuật (ghi lại để các lượt sau không tưởng baseline cũ):
  clone local có `remote.origin.fetch` chỉ theo dõi nhánh media nên
  `git fetch origin` thuần KHÔNG cập nhật ref integration — ref local
  tưởng vẫn `cf17178` trong khi `git ls-remote` đã là `f383233`. Đã fetch
  tường minh bằng refspec đầy đủ
  (`refs/heads/codex/story-gameplay-integration-20261031:refs/remotes/origin/...`)
  mới thấy merge. Các lượt sau phải fetch integration bằng refspec tường
  minh, không dựa vào `git fetch origin` thuần.
- Media inputs KHÔNG đổi: diff `cf17178..f383233` trên
  `Implementation/Content/`, `Implementation/Coordination/`,
  `Tools/MediaProduction/`, `Art_Source/Cinematics/`,
  `Art_Source/Audio/`, `ClientGodot/assets/cinematics/`,
  `ClientGodot/assets/audio/` = rỗng. Policy `agent_scope_v2.json`
  không đổi; pack/DirectorsPack/AudioDirection/cue manifest không đổi.
  Baseline của nhánh media vẫn `cf17178` (không rebase nhánh media;
  PR #119 vẫn mergeable clean).

## Nội dung merge mới — Codex, chỉ đọc, không sửa

- `Art_Source/Combat_Visuals_20261105/`: questkit (Ly An / Tạ Vân Khanh /
  thầy thuốc, top 608 px + đồ y608..1024), mobs Cá Linh + Rễ Nước
  (idle/attack/dead, 512 px/cell), Minh Kiếm walk v1 (8 hướng × 4 pha,
  32 frame) + attack v2 (thay v1 REJECTED), nodes, skill icons, VFX,
  prompts, `source_manifest.json`, README. Trạng thái
  `NATIVE_REVIEW_CANDIDATE`, chưa phải final art.
- `ClientGodot/assets/combat_v1/`: runtime combat assets +
  `dialogue_vi.json` (229 entry thoại quest, 0 chuỗi `CIN_` — không chạm
  thoại cinema; NPC IDs khớp staging cinematic-only Q4, không nhân đôi
  persistent ID).
- D4 cập nhật: reference character lock cho video nay gồm questkit +
  Minh Kiếm walk/attack + mobs. README ghi rõ: "Các reference NPC chỉ
  dùng làm character lock cho video; Muse không được sửa
  graphics/runtime." 4 khuyết điểm panel animatic checkpoint 03 vẫn
  nguyên — chưa sửa panel trong lượt này (đó là khối animatic revision
  riêng, không phải QA).

## Trạng thái GitHub (đọc qua public API, 2026-11-05 17:40 JST)

- Issue #116: vẫn OPEN, 7 comment, mới nhất `6649909991`
  (2026-11-05 04:45 UTC, ACK checkpoint 03–07 + PR #119). Không có chỉ
  đạo mới; D1 (xác nhận cửa sổ PROPOSED) vẫn chưa được xác nhận → VO
  dự thảo campaign (D5) vẫn chờ.
- PR #119: OPEN, chưa merge, head `7a94037`, 15 commit, 687 file,
  mergeable clean, cập nhật 2026-11-05 07:44:08Z; 0 review, 0 comment
  mới trên PR.

## Kết quả kiểm chứng lại (byte thật, không PASS giả)

### 1. Runtime delivery kiểm chứng lại — PASS, 0 mismatch

Chạy lại nguyên vẹn tool checkpoint 11
(`Tools/MediaProduction/Muse/verify_runtime_delivery.py`), đầu ra mới
`MEDIA02_CHECKPOINT_12_RUNTIME_REVERIFY_20261105.json`
(sha `79f7a4cafb3cca49b4e00ccb6f40900d58a83d46adeca5d2f96191de8efc7087`):

| Nhóm | Số file kiểm | Kết quả |
|---|---|---|
| Audio runtime (22 nhạc/ambience + 519 SFX/UI + 4 VO P0) | 545 | khớp manifest, 0 mismatch |
| Animatic P0 (MP4 + OGV + poster) | 3 | khớp sha checkpoint 03, 0 mismatch |
| Timing JSON 20 cảnh | 20 | khớp sha manifest, 0 mismatch |
| SRT 20 cảnh | 20 | khớp sha manifest, 0 mismatch |

### 2. Source pack kiểm chứng lại — PASS, 0 mismatch

Chạy lại nguyên vẹn tool checkpoint 09
(`Tools/MediaProduction/Muse/validate_media_deliveries.py`), đầu ra mới
`MEDIA02_CHECKPOINT_12_SOURCE_REVALIDATION_20261105.json`
(sha `80c4b819ed697ab491c5b62338f04408f445ef9d6e34fbe347f644b2ddde1288`):

- Audio nguồn: 1093 file (44 nhạc/ambience + 1038 SFX/UI + 11 stem P0)
  khớp byte/sha/codec/48 kHz/kênh/thời lượng, 0 con trỏ LFS.
- Timing + SRT: 20/20 cảnh (63 shot × 6 s = 378 s), 21 thoại = 21 cue SRT,
  UTF-8 strict + NFC, khớp từng ký tự.
- Animatic: 12/12 panel khớp sha, MP4/OGV 640×360 72 s; VO P0: 3/3 take
  khớp sha/thời lượng và vừa cửa sổ.
- Ghi chú duy nhất (đã biết từ checkpoint 03/11): OGV `avg_frame_rate 0/0`
  do Theora gộp frame giữ nguyên — thời lượng vẫn 72 s, không phải lỗi.

## Trạng thái repo

- Nhánh media: head `7a94037` trước checkpoint này; commit checkpoint 12
  `a242af3` ĐÃ PUSH (ls-remote xác nhận; scope audit 691 paths,
  0 violations, base integration HEAD `f383233`). PR #119 nay có
  16 commit.
- PR #119 vẫn OPEN, chưa merge; ACK comment checkpoint 12 trên issue
  #116: CẦN thẻ duyệt của chủ dự án qua GitHub connector — ghi rõ để
  luồng chính xử lý, lượt chạy này không treo chờ.

## Giới hạn / khuyết điểm (ghi rõ, không giấu)

- Loudness/true-peak KHÔNG đo lại ở lượt này (lấy từ checkpoint
  02/04/07/08, đo từ byte thật). Không phải mix PASS, không nghe thử
  bằng tai (D2).
- Cửa sổ campaign vẫn PROPOSED (D1); VO campaign chưa làm (D5, chờ D1).
- Animatic vẫn mức storyboard, 4 khuyết điểm panel còn nguyên (D4).
- File runtime vẫn chưa nối vào Godot (D3, presentation adapter của Codex).

## Khối tiếp theo

VO dự thảo campaign (17 cue) ngay khi D1 được xác nhận; nếu chưa có xác
nhận, M8 QA liên tục sau mỗi lần integration merge hoặc review mới trên
PR #119. Lưu ý vận hành: fetch integration bằng refspec tường minh
(xem mục re-baseline).
