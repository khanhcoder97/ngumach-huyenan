# MEDIA-02 CHECKPOINT 15 — Gói 30 fix (b): LF + LFS (2026-11-05)

## Khối vừa hoàn thiện

Sửa finding 2 (LF/CRLF) và finding 4 (22 binary raw → LFS) của review PR #119
(Gói 30 item 2), sau khi chủ dự án gỡ chặn bằng comment mới trên issue #116.
24 file binary từng lưu raw nay là LFS pointer; text delivery đã LF từ trước
(renormalize là no-op về nội dung); manifest tái sinh, kiểm chứng lại PASS.

## Trạng thái GitHub (đọc qua public API + connector read-only, 2026-11-05 21:xx JST)

- Issue #116: vẫn OPEN, nay 9 comment. MỚI: comment `6656610885`
  (2026-11-05 11:16:36Z, khanhcoder97) — **PR #120 đã merge vào integration
  `a84ce590`, 10 CI check xanh; đây là nguồn owner mới cho Muse.**
  - `Implementation/Content/DesignBaselines/media_draft_timing_decisions_20261105.json`
    (`DEC-MEDIA-DRAFT-WINDOWS-20261105`, `APPROVED_FOR_DRAFT_VO_ONLY`): 21 cửa
    sổ đã duyệt cho sản xuất VO nháp; text đối chiếu dialogueLines canon, mọi
    cửa sổ nằm trong shot. Chưa duyệt final picture, mix, autoplay. CIN004 Ly
    An offscreen giữ nguyên. **CIN020 dùng `VOICE_LETTER_RECIPIENT` cho Người
    nhận thư vô danh — chỉ là vai giọng cinematic, không sinh NPC gameplay,
    không gán lời cho nhân vật có tên khác.**
  - `.gitattributes` nay có LF cho timing JSON/SRT/manifest nguồn và runtime,
    đồng thời OGV thuộc LFS. Lệnh: fetch integration mới, renormalize đúng
    media paths trong phạm vi, regenerate manifest/SHA, kiểm fresh checkout
    Windows/Linux. Không sửa/bỏ qua hash để nhận file hỏng.
  - Gói 30 + review PR119 đã công bố. Sửa cuecount, 5 lỗi hình, xuất clip
    riêng từng scene; tiếp 17 VO nháp và video/audio còn thiếu. Không dùng
    reel 72s làm opening. 541 audio port giữ provenance cũ; không báo là
    sáng tác mới.
  - Push checkpoint có media/source thật rồi tiếp phần độc lập M3–M8. Không chờ
    duyệt cửa sổ cũ hoặc final character lock để dừng mọi VO/timing/shot môi
    trường. Quyền game graphics/UI/VFX/map/runtime vẫn thuộc Codex.
- Review `Implementation/Reports/Review_20261105/Muse_PR119.md` nay ĐÃ CÓ trên
  integration (PR #120, 39 dòng) — CP14 không tìm thấy vì lúc đó chưa merge.
  Nội dung khớp Gói 30: HOLD toàn PR ở head `3f34f0d`; 5 findings; D1 duyệt VO
  nháp 21 cửa sổ; CIN020 `VOICE_LETTER_RECIPIENT`.
- PR #119: OPEN, base nay là `a84ce590` (nhánh integration đã tiến). Head trước
  lượt này `67f0d92`.
- Integration HEAD mới: `a84ce590` (PR #120, tutorial expansion + media
  decisions + `.gitattributes` mới). Không còn ở `f383233`.

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| 24 file binary (xem dưới) | Raw blob → LFS pointer (`git add --renormalize` với quy tắc mới). OID pointer == SHA256 byte thật của file. |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Nhãn checkpoint 14 → 15 trong `RUNTIME_CINEMATICS_manifest_v1.json` (chỉ đổi nhãn; SHA/size nội dung không đổi). |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Nhãn checkpoint 15 + `base_integration` `f383233` → `a84ce590`. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Nhãn checkpoint 15 + base `a84ce590` + dòng `verifies` ghi thêm checkpoint 15. |
| `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` | Tái sinh bằng builder: chỉ đổi trường `checkpoint`; mọi SHA/size giữ nguyên. |
| `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json` | Tái sinh bằng builder sau sự cố (xem dưới): trở về đúng vo=4, totalFiles=545, byte-identical với bản CP14. |

### Quy tắc LF/LFS mới (từ integration `a84ce590`, PR #120)

`.gitattributes` trên integration thêm `*.ogv filter=lfs diff=lfs merge=lfs
-text` và 7 quy tắc `text eol=lf` cho:
`Art_Source/Cinematics/**/*.json`, `Art_Source/Audio/Muse/**/*.json`,
`Implementation/Content/Narrative/Deliveries/**/*.json|.srt`,
`ClientGodot/assets/cinematics/**/*.json|.srt`,
`ClientGodot/assets/audio/**/*.json`.
Ghi chú trong file: "Media delivery SHA256 is over UTF-8 LF bytes on every
checkout/platform."

**`.gitattributes` KHÔNG sửa trên nhánh media** (file ở repo root, ngoài root
policy `agent_scope_v2` — commit nó sẽ fail scope audit). Quy tắc được áp
dụng cục bộ qua `.git/info/attributes` (không commit) để renormalize/add,
và sẽ về nhánh media khi PR #119 merge vào integration (base đã có quy tắc).

### 24 file raw → LFS (đối chiếu con số 22 của review)

Review chốt ở `3f34f0d`: 22 file khớp pattern LFS nhưng lưu raw (7 VO + 1 sheet
v1 + 12 panel + MP4 + poster; OGV không tính vì chưa có pattern). CP13 thêm
`P0_storyboard_sheet_v2.png` → **23 file pattern-LFS + 1 OGV = 24 file**.
Lượt này chuyển cả 24 theo đúng quy tắc (file nào khớp pattern thì phải là
pointer), không tự đoán sheet v2 có nằm trong 22 hay không — báo cáo ghi rõ
con số 24 để chủ dự án/Codex đối chiếu:

- VO (7): 3 `*_tts_raw.mp3` + `P0_VO_timeline_draft_v1.wav` + 3 take
  `VO_CIN*_draft_v1.wav` — `Art_Source/Audio/Muse/VO/P0_DRAFT/`.
- Hình (15): `P0_storyboard_sheet_v1.png`, `P0_storyboard_sheet_v2.png`,
  12 panel `panel_CIN_*.png` — `Art_Source/Cinematics/P0_Animatic/`.
- Runtime (3): `P0_animatic_640x360_30fps.mp4`,
  `P0_animatic_640x360_30fps.ogv` (mới có pattern nhờ PR #120),
  `P0_animatic_poster.png` — `ClientGodot/assets/cinematics/`.
- Tổng LFS trong index: 1690 → **1714**.

### Renormalize text: 0 thay đổi nội dung

`git ls-files --eol` trên toàn bộ media roots trước sửa: 673 file `i/lf`,
24 file `i/-text` (chính 24 binary trên), 6 file `i/none` (JSON báo cáo
checkpoint, không thuộc quy tắc eol nào), **0 file CRLF** ở index lẫn
worktree. Renormalize theo quy tắc mới không đổi byte nào của text — LF đã
đúng từ trước, lỗi finding 2 chỉ bộc lộ ở checkout Windows (thiếu attribute),
nay đã có attribute trên integration.

## Kết quả kiểm chứng lại (byte thật, không PASS giả)

### 1. Timing LF-SHA đối chiếu quyết định owner — 21/21 khớp

SHA256 (LF bytes) của 20 timing JSON trong nhánh media khớp toàn bộ
`sourceSha256LF` trong `media_draft_timing_decisions_20261105.json`
(`DEC-MEDIA-DRAFT-WINDOWS-20261105`): 21/21 cửa sổ, 0 CRLF trong file.

### 2. Source pack kiểm chứng lại — PASS, 0 mismatch

`MEDIA02_CHECKPOINT_15_SOURCE_REVALIDATION_20261105.json`:

- Audio nguồn: 1093 file (22 nhạc/ambience + 173 SFX/UI × 3 variant × 2 +
  11 stem P0) khớp byte/sha/codec/48 kHz/kênh/thời lượng.
- Timing + SRT: 20/20 cảnh, timing dialogues 21 == SRT cues 21 ==
  runtime manifest 21.
- Animatic: 12/12 panel khớp sha, MP4/OGV 640×360 72 s; VO P0: 3/3 take
  khớp sha/thời lượng và vừa cửa sổ.
- Ghi chú duy nhất (đã biết): OGV `avg_frame_rate 0/0` do Theora gộp frame
  giữ nguyên — thời lượng vẫn 72 s, không phải lỗi.

### 3. Runtime delivery kiểm chứng lại — PASS, 0 mismatch

`MEDIA02_CHECKPOINT_15_RUNTIME_REVERIFY_20261105.json`:

| Nhóm | Số file kiểm | Kết quả |
|---|---|---|
| Audio runtime (22 nhạc/ambience + 519 SFX/UI + 4 VO P0) | 545 | khớp manifest, 0 mismatch |
| Animatic P0 (MP4 + OGV + poster) | 3 | khớp sha, 0 mismatch |
| Timing JSON 20 cảnh | 20 | khớp sha, 0 mismatch |
| SRT 20 cảnh | 20 | khớp sha, 0 mismatch |

### 4. Test-merge cục bộ vào integration mới — CLEAN

Nhánh tạm `tmp/merge-check-20261105` tại `a84ce590` + merge commit fix này:
merge sạch, 0 conflict (commit merge `2f0f605`, đã xóa nhánh sau khi kiểm
xong, chỉ giữ lại để đối chiếu). Scope audit với base `a84ce590`:
**705 changed paths, 0 violations**.

### 5. Fresh checkout — Linux + mô phỏng Windows — PASS

- **Linux** (fresh clone `file://` của test-merge, `git lfs install`
  local): pull chọn lọc OGV + panel + VO wav → byte thật, SHA khớp OID
  pointer (OGV `7498a8f1…`, panel `ea9d4228…`). Lưu ý: `git lfs pull`
  toàn bộ thất bại ở vài object cũ do clone local thiếu object (không
  thuộc khối này) — kiểm toàn bộ bằng clone từ GitHub sau push (xem dưới).
- **Windows mô phỏng** (fresh clone với `core.autocrlf=true`): 633 file
  `i/lf w/lf`; **0/85** file text delivery chứa CR; timing LF-SHA 21/21
  khớp quyết định owner; runtime manifest timing/SRT SHA **40/40** khớp.
  Đây chính là bài kiểm của review finding 2 — nay PASS trên checkout
  kiểu Windows.

## Sự cố trong lượt và cách khắc phục (ghi rõ, không giấu)

Clone làm việc dùng `GIT_LFS_SKIP_SMUDGE=1` nên checkout thay file LFS bằng
pointer text. Lượt này chuyển nhánh tạm để test-merge rồi quay lại — checkout
đã viết đè 24 file vừa chuyển thành pointer trong worktree. Lần chạy builder
đầu tiên sau đó (khi nhãn script vừa đổi sang checkpoint 15) đã FAIL
(exit 1, 21 lỗi): builder từ chối source là pointer, copy pointer text đè
lên 4 file VO runtime + 3 file animatic runtime, và viết lại
`RUNTIME_AUDIO_manifest_v1.json` thành vo=0/totalFiles=541 (mất 4 entry VO)
cùng `RUNTIME_CINEMATICS_manifest_v1.json` với SHA/size của pointer.

Khắc phục, không giấu lỗi:
1. `git lfs checkout` tường minh 28 file (24 nguồn + 4 VO runtime) từ object
   store local — 30 MB, 0 file còn pointer; SHA sau khôi phục khớp OID.
   (Bài học: `git lfs checkout -- <thư mục>/` không mở rộng đủ — phải liệt
   kê file tường minh.)
2. Chạy lại builder: `ALL VERIFIED`, vo=4/totalFiles=545, manifest audio
   byte-identical với bản CP14; manifest cine chỉ đổi nhãn checkpoint 15.
3. Chạy lại cả hai validator: PASS, 0 mismatch (xem mục 2–3 trên).
4. `git add` trên thư mục SFX chỉ refresh stat cache (cached diff 0) — 541
   file SFX builder copy lại chỉ lệch stat, nội dung byte-identical
   (`git hash-object` == blob trong index).
5. Commit fix được amend (chưa push) để gồm đủ: 24 conversion + 3 script
   nhãn + manifest cine + 2 JSON kiểm chứng mới. Không commit file nào
   trong trạng thái pointer.

## Giới hạn / khuyết điểm (ghi rõ, không giấu)

- **OGV trên nhánh media (trước merge) vẫn checkout ra pointer.** Quy tắc
  `*.ogv` chỉ có trên integration (`a84ce590`); nhánh media không sửa
  `.gitattributes` vì ngoài scope. Ai clone riêng nhánh media sẽ thấy OGV
  là pointer text cho tới khi PR #119 merge. Sau merge, attribute có hiệu
  lực và OGV resolve bình thường (đã chứng minh bằng test-merge + pull).
- **Fresh clone toàn bộ từ GitHub (remote) chưa chạy ở lượt này** — cần sau
  push, khi 24 object LFS mới đã lên server. Ghi vào report commit sau push.
- **Chưa sửa finding 3 (CIN_002_S02):** tay băng chạm nước + crop cắt
  đầu/mặt, và yêu cầu keyframe 16:9 riêng từng shot — khối tiếp theo
  (Gói 30 item 3).
- **Chưa xuất clip riêng từng scene** (Gói 30 item 6) và **chưa viết lại mô
  tả PR #119** (item 8) — mô tả PR cần thẻ duyệt của chủ dự án; ghi rõ để
  luồng chính xử lý, lượt này không treo chờ. ACK comment checkpoint 15
  trên issue #116 cũng cần thẻ duyệt — ghi rõ để luồng chính xử lý.
- Số lượng thực tế giữ nguyên: 541/545 audio runtime là port Codex PackV1,
  chỉ 4 file VO mới; campaign có timing/SRT chứ chưa có 20 video hoàn
  chỉnh; video duy nhất vẫn là reel 72 s review/gallery, không tự chạy
  làm opening. Loudness/true-peak không đo lại lượt này (lấy CP02/04/07/08).
  Không mix PASS, không nghe thử bằng tai (D2). Cửa sổ campaign vẫn
  PROPOSED cho final (D1 chỉ mở VO nháp).

## Khối tiếp theo

1. Gói 30 fix (c) — item 3: keyframe CIN_002_S02 đúng (tay lành dừng trước
   mặt nước, không crop đầu/mặt) + keyframe 16:9 riêng từng shot.
2. VO nháp campaign 17 cue (D1 đã mở; lưu ý CIN020 dùng
   `VOICE_LETTER_RECIPIENT`, vai giọng cinematic, không NPC gameplay).
3. Xuất clip riêng từng scene (MP4/OGV/poster/SRT/timing/hash) + viết lại
   mô tả PR #119 theo số thực (cần thẻ duyệt).
