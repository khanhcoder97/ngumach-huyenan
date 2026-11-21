# MEDIA-02 CHECKPOINT 35 — Công cụ kiểm chứng fresh-checkout cho Gói 31 item 5 (.gitattributes)

Ngày: 2026-11-06 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f2b465`
(trước checkpoint: head `ea1a3ee`, checkpoint 34; Gói 31 mục 1–4 đã xong, mục 5 chờ
merge commit của chủ dự án — checkpoint này KHÔNG merge, KHÔNG tự viết policy.)

## 1. Khối hoàn thiện

Chuẩn bị sẵn công cụ kiểm chứng cho Gói 31 item 5, kèm kiểm chứng đối chứng âm
(negative control) trên một fresh clone thật của nhánh media — để ngay khi chủ dự
án merge policy từ integration, chỉ cần chạy lại tool này trên fresh checkout
(Windows + Linux) là biết PASS/FAIL, không phải kiểm bằng tay.

- Công cụ mới: `Tools/MediaProduction/Muse/verify_fresh_checkout_item5.py`
  (v1.0.0, chỉ đọc, không mạng, đo từ byte thật; exit 0 = PASS, 1 = FAIL;
  ghi JSON ra `--out` và in JSON ra stdout).
- 5 kiểm tra trong tool:
  1. `policy_ogv_lfs` — root `.gitattributes` có dòng
     `*.ogv filter=lfs diff=lfs merge=lfs -text`.
  2. `policy_lf_rules` — đủ 7 dòng LF cho JSON/SRT media delivery
     (theo policy owner trên integration 6f2b465).
  3. `policy_matches_reference` — khi có `--reference-policy` (file
     `.gitattributes` trích từ integration hiện tại), mọi dòng rule
     không-comment của reference đều phải có mặt trong `.gitattributes`
     của checkout. Tool chỉ so sánh, không bao giờ viết policy.
  4. `ogv_real_bytes` — mọi `*.ogv` dưới các root media bắt đầu bằng
     magic `OggS` (byte Theora thật), không phải pointer LFS
     (`version https://git-lfs.github.com/spec/v1`).
  5. `text_lf_endings` — mọi `*.json`/`*.srt` dưới các root media không
     chứa byte CR. Ghi rõ trong tool: PASS trên Linux chỉ là bằng chứng
     Linux (git không đổi ending ở đây); các dòng LF có ý nghĩa cho
     checkout Windows — PASS ở đây không bao giờ được đọc là "policy đã đủ".

## 2. Kiểm chứng đối chứng âm (negative control) — fresh clone thật

- Fresh clone: `/tmp/ngumach-fresh-item5`, `--depth 1 --single-branch`,
  nhánh `muse/media-production-20261104`, `GIT_LFS_SKIP_SMUDGE=1`,
  head `ea1a3eec34bd5a23cb75c86c0afcab0788fca44d` (= CP34).
- Reference policy: `.gitattributes` trích từ integration `6f2b465`
  (`git show origin/codex/story-gameplay-integration-20261031:.gitattributes`,
  34 dòng, 27 dòng rule).
- Kết quả — verdict **FAIL**, đúng như lỗ hổng đã ghi của item 5:
  - `policy_ogv_lfs`: FAIL — thiếu dòng `*.ogv` LFS.
  - `policy_lf_rules`: FAIL — thiếu cả 7 dòng LF.
  - `policy_matches_reference`: FAIL — thiếu đúng 8 dòng so với reference
    (1 OGV LFS + 7 LF), không thiếu dòng nào khác.
  - `ogv_real_bytes`: FAIL — **22/22 file OGV là LFS pointer** (0 byte thật),
    gồm 20 scene CIN_000–CIN_020 + P0 animatic. Đây chính là lỗi "fresh
    checkout nhận OGV pointer" đã nêu ở Gói 31 mục 5.
  - `text_lf_endings`: PASS — 253 file, 0 file chứa CR (bằng chứng Linux-only,
    xem mục 1.5).
- Chạy đối chứng trên worktree hiện tại (cùng head, cùng reference):
  verdict **FAIL chỉ ở policy** — `ogv_real_bytes` PASS (22/22 byte thật,
  nhờ mirror local-only `.git/info/attributes`), `text_lf_endings` PASS
  (254 file, 0 CR — file thứ 254 là JSON fresh-checkout vừa ghi).
  Hai lần chạy này chứng minh tool phân biệt được "byte trên đĩa OK" với
  "policy trong nhánh còn thiếu" — đúng điều item 5 cần kiểm sau merge.

## 3. Trạng thái repo / GitHub lúc kiểm (2026-11-06 ~13:45 JST)

- Integration vẫn `6f2b465` (không đổi từ CP34); media branch local = remote
  = `ea1a3ee`; working tree sạch trước khi làm checkpoint này.
- Issue #116: vẫn 13 comment, mới nhất 6671599404 (ACK Gói 31, 2026-11-05
  22:50 JST) — KHÔNG có chỉ đạo mới, không quyết định tên "Tạ Vân Khanh"
  (D-12), không trả lời .gitattributes, không có Gói 32.
- PR #119: open, head `ea1a3ee`, 61 commit / 1206 file, `mergeable: true`,
  `mergeable_state: clean`, không review mới. Mô tả PR vẫn ở checkpoint
  01–31 (ghi head cũ 0f2678f — lỗi thời); payload cập nhật lên CP32–CP34 đã
  chuẩn bị sẵn tại `~/workspace/godot-prototype/pr_comments/
  pr119_update_cp32_34.json`, cập nhật cần thẻ duyệt của chủ dự án qua luồng
  chính — checkpoint này không tự ghi qua connector.

## 4. Kiểm toán / đo đạc (chạy lại tại checkpoint này, nội dung không đổi từ CP34)

| Kiểm tra | Kết quả |
|---|---|
| Source re-validation (`validate_media_deliveries.py`) | **PASS, 0 mismatch** (mismatches: []; audio 1151 file, timing 20 cảnh / 21 cue, keyframe batch 39 + 12 P0, VO 21 take, mix P0 v1/v2/v3 4+4+4, CIN_006 mix v1 1/1, shortlist CP33 145 entry, clip 20/20, prologue 45 file) |
| Runtime re-verify (`verify_runtime_delivery.py`) | **PASS, 0 mismatch** (mismatches: []; audio 611 file — 22 nhạc/ambience + 519 SFX/UI + 30 VO + 14 mix + 26 composed; clip 20 cảnh / 100 file, timing 20 + SRT 20, prologue 7 file, animatic 3 file) |
| Scope audit (`check_agent_scope.py`, base integration 6f2b465) | **0 vi phạm** (1211 changed paths tại head nội dung 3f59b9a; chạy lại sau commit báo cáo: xem nhật ký chạy) |
| Fresh-checkout item 5 (tool mới, clone thật) | **FAIL như kỳ vọng** (thiếu 8 dòng policy; 22/22 OGV pointer) |
| Worktree item 5 (tool mới) | **FAIL chỉ ở policy** (OGV 22/22 byte thật) |

Ghi chú: chuỗi validator ghi nhãn nội bộ "checkpoint 34" vì nội dung media
không đổi từ CP34; lần chạy này chỉ re-validation tại CP35.

## 5. Scope audit

Chạy sau commit nội dung `3f59b9a`, base integration `6f2b465`, nhánh
`muse/media-production-20261104`: **1211 changed paths, 0 violations**.
Chạy lại sau commit báo cáo (head mới) để xác nhận toàn nhánh vẫn 0 vi phạm;
số liệu lần chạy lại ghi trong nhật ký chạy, không sửa ngược báo cáo này.

## 6. Giới hạn còn lại

- **Item 5 vẫn CHƯA xong:** policy `.gitattributes` vẫn chờ merge commit của
  chủ dự án từ integration 6f2b465. Tool này không thay thế merge đó và không
  tự viết policy — root file là Codex-owned. Sau merge, chạy lại tool trên
  fresh checkout (kỳ vọng PASS: đủ 8 dòng, OGV byte thật, LF 0 CR) rồi mới
  coi item 5 xong.
- **NOT_AUDITIONED:** chưa nghe thẩm định mix/mux nào; mọi số LUFS/TP là đo
  từ byte, không phải PASS nghe tai.
- Mix vẫn DRAFT_MIX_NOT_FINAL; phân bổ stem CIN_006 PROPOSED; VO vẫn bản
  nháp TTS; final picture chờ keyframe/character lock (clip vẫn Ken Burns
  trên still storyboard, không phải final pose animation).
- Quyết định tên D-12 ("Tạ Vân Khanh" vs "Tạ Văn Khanh") vẫn chờ chủ dự án.
- Mô tả PR #119 vẫn ở CP01–31; cập nhật lên CP32–CP35 cần thẻ duyệt.

## 7. File giao

- `Tools/MediaProduction/Muse/verify_fresh_checkout_item5.py` (mới, v1.0.0)
- Báo cáo này + `MEDIA02_CHECKPOINT_35_FRESH_CHECKOUT_ITEM5_20261106.json`
  (fresh clone: FAIL) + `MEDIA02_CHECKPOINT_35_WORKTREE_ITEM5_20261106.json`
  (worktree: FAIL chỉ policy)
- `MEDIA02_CHECKPOINT_35_SOURCE_REVALIDATION_20261106.json`
  + `MEDIA02_CHECKPOINT_35_RUNTIME_REVERIFY_20261106.json`
- Reference policy dùng khi kiểm (không commit vào repo, chỉ dùng lúc chạy):
  `.gitattributes` trích từ integration 6f2b465.

## 8. Khối tiếp theo

Gói 31 item 5 sau merge commit của chủ dự án (chạy lại tool này trên fresh
checkout Windows/Linux + scope re-audit + cập nhật metadata). Sau đó: các pack
còn thiếu của M3/M4/M5 (campaign motion/VO/music/SFX còn thiếu, final media
QA) — không quay sang game sprite/UI/map/VFX/Godot.
