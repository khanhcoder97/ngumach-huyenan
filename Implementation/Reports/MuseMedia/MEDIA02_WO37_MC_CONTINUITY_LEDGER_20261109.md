# MEDIA-02 WO37 M-C CP4 — Continuity ledger v1 (63 campaign shots)

Ngày: 2026-11-09 · Nhánh: `muse/media-production-20261104` · Baseline integration: `9ac73dc`
(Gói 38, item 4: tiếp motion/continuity bằng thay đổi asset thật — không phải
checkpoint hash lặp; đây là phân tích liên tục mới, không giao lại metadata/mix đã xong.)

## 0. Bối cảnh / chỉ đạo

- Issue #116 vẫn 25 comment; mới nhất vẫn là ACK M-G CP6 + M38-A của Muse
  (comment `6733544286`, đăng ~15:13 JST). KHÔNG có chỉ đạo mới của Codex/chủ
  dự án kể từ Gói 38 (comment `6733227370`, 14:46 JST).
- M38-B đã xong và đã push (head `4c53683`, 148 commit / 2138 file); payload
  đăng M38-B đã soạn, đang chờ chủ dự án duyệt thẻ — lượt này KHÔNG đăng gì
  (cần thẻ duyệt, thuộc luồng chính).
- M-F CP2 (re-mix theo voice palette) và M-E CP2 (composed SFX) vẫn chờ quyết
  định của director/Codex — lượt này không làm hai khối đó.
- Khối này làm tiếp nửa "continuity" của WO37 M-C: đối chiếu chéo 63 shot
  campaign từ file thật, không render hình mới, không sửa audio, không quyết
  định thiết kế nhân vật.

## 1. Khối hoàn thiện

Continuity ledger v1 cho toàn bộ 63 shot campaign (CIN_001–CIN_020; prologue
CIN_000 là phim độc lập, không nằm trong 63) — kiểm tra tính liên tục qua
6 luật K1–K6, mỗi luật suy ra lại từ nguồn gốc (xem mục 2), không tin bản
tóm tắt cũ.

- `Tools/MediaProduction/Muse/build_continuity_ledger_v1.py` (mới): builder.
- `Tools/MediaProduction/Muse/check_continuity_ledger_v1.py` (mới): validator
  độc lập — đọc lại toàn bộ nguồn bằng code parse riêng, suy ra lại từng
  trường, so khớp từng dòng với ledger.
- `Implementation/Content/Narrative/Deliveries/CONTINUITY_LEDGER_v1.json`
  (mới, 91.099 B, sha256
  `cd1c2d56f24b66fa61a0dffa13af895e1d30e0936f64b7b84363c496667f2ab6`): ledger —
  20 dòng scene, 63 dòng shot, 24 dòng character-continuity, 5 dòng
  guardrail-continuity, 58 finding (F001–F058).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MC_CONTINUITY_LEDGER_VALIDATION_20261109.json`
  (mới): kết quả validator — **326/326 PASS, verdict PASS**.

Luật kiểm tra (ghi đầy đủ trong ledger, mục `rules`):

- K1 — Timing tiling từ timing manifest: các shot lát liên tục không khe/hở
  (end[n] == start[n+1] ±0,001), shot đầu bắt đầu 0,0, shot cuối kết thúc đúng
  duration scene; timing trong motion ledger phải khớp timing manifest;
  duration phải khớp nhau giữa timing / scene export / mix / runtime manifest;
  tổng campaign 20 scene / 63 shot / 378 s / 21 cue thoại.
- K2 — SRT/dialogue: SRT theo runtime manifest (đã verify sha) phải UTF-8,
  NFC, LF-only, số cue == export manifest `dialogueCues`, các cue xếp thứ tự
  không chồng nhau; mỗi shot thoại có đúng 1 cue, cửa sổ nằm trong shot,
  text (NFC) == text thoại trong ledger.
- K3 — Character continuity: theo scene, theo nhân vật có tên (visible hoặc
  required): dãy shot xuất hiện; BLINK = xuất hiện → vắng ≥1 shot → xuất hiện
  lại trong cùng scene; REQUIRED_NOT_VISIBLE; người nói không thấy trong shot
  thoại của mình là NOTE khi `onscreen=false` (off-screen đã quyết) hoặc
  ledger đã ghi staging off-screen, còn lại là FLAG; người nói không có
  canonical ID là FLAG.
- K4 — Guardrail continuity: mỗi guardrail R5 được truy vết qua cả scene:
  mọi shot khác có cùng subject xuất hiện nên khẳng định lại guardrail đó;
  shot chưa khẳng định là NOTE (độ phủ tài liệu, không phải verdict về hình).
- K5 — Audio coverage theo shot: từ mix manifest hiện hành của từng scene
  (P0 → P0_MIX_V3, các scene còn lại → CINxxx_DRAFT_V1); stem
  `segmentSceneSeconds` phủ các shot chồng lấn, stinger phủ shot bắt đầu tại
  `atSeconds`, VO phủ các shot chồng lấn cửa sổ. DRY_SHOT (không
  music/ambience/stinger/vo) là FLAG; biên segment nằm giữa shot và stinger
  đúng ranh giới shot là NOTE; seam vòng lặp ambience đính kèm từ bảng seam
  của pronunciation table (ưu tiên bản composed).
- K6 — Mix VO take extent so với cửa sổ đã khóa/SRT, khớp theo shotId
  (mix `voices` list, nếu không có thì `vo` đơn): take end là
  `takeEndSeconds` nếu có, không thì `windowSeconds[1]`; take kết thúc trước
  cuối cửa sổ là NOTE, vượt cửa sổ là NOTE kèm `overrunVsWindowSeconds` đã
  ghi; cửa sổ mix lệch cửa sổ khóa là FLAG.

## 2. Kết quả đo từ byte thật

- Tổng: 20 scene / 63 shot / 378,0 s / 21 cue thoại / 21 shot thoại — khớp
  runtime manifest và motion ledger.
- K1: tiling PASS 20/20 scene (không khe, không chồng); timing ledger khớp
  timing manifest 63/63 shot; duration khớp 4 nguồn (timing/export/mix/
  runtime) 20/20 scene; timing sha + SRT sha khớp runtime manifest 20/20.
- K2: SRT UTF-8 + NFC + LF-only 20/20 file; số cue == `dialogueCues` 20/20;
  cue xếp thứ tự không chồng 20/20; 21/21 shot thoại có đúng 1 cue, cửa sổ
  nằm trong shot, text khớp ledger (NFC).
- K3: 0 character blink trong toàn campaign (không nhân vật nào xuất hiện →
  vắng → xuất hiện lại trong cùng một scene). 4 shot REQUIRED_NOT_VISIBLE đã
  có staging note trong ledger (xem mục 3).
- K4: 5 guardrail R5 truy vết; LEFT_BANDAGE khẳng định đủ 1/1 shot có
  subject; 4 guardrail còn lại chỉ khẳng định trên 1 shot (NOTE, xem mục 3).
- K5: 0 dry shot (mọi shot đều có ít nhất một role music/ambience/stinger/
  vo); 0 segment boundary nằm giữa shot; 0 ambience seam > 0,005 trong các
  cue đang dùng.
- K6: 21/21 VO entry khớp đúng shotId; không có cửa sổ mix lệch cửa sổ khóa.

## 3. Findings: 58 (4 FLAG + 54 NOTE)

### FLAG — cần quyết định của director/Codex (4)

| ID | Shot | Nội dung |
|----|------|----------|
| F047 | CIN_005_S03 | Người nói NPC_LYAN không thấy trong shot thoại; `onscreen=null` ở cả timing manifest lẫn ledger, ledger không ghi staging off-screen — cần quyết: đánh dấu off-screen hay sửa picture. |
| F048 | CIN_009_S03 | Như trên, NPC_LYAN, shot thoại CIN_009_S03. |
| F052 | CIN_017_S03 | Người nói NPC_DIVER_LEAD không thấy trong shot; `onscreen=null`, không staging note trong ledger/timing manifest. (Báo cáo CP51 đã ghi nhận "no diver in frame, dive leader's line reads off-screen" nhưng trạng thái đó chưa được ghi vào timing/ledger — flag này là về nguồn, không phải về mix.) |
| F054 | CIN_020_S03 | Người nói không có canonical ID (speaker null, speakerDisplay "Người nhận thư") ở cả timing manifest lẫn ledger. Take đã có (VO_CIN_020_S03_LETTERRECIPIENT, placeholder role voice); cần ghi một ID người nói — kể cả ID placeholder — để continuity final-picture/VO không bị trống. |

Không FLAG nào chặn mix/audio: cả 4 đều là quyết định staging/dữ liệu, mix
hiện tại không bị ảnh hưởng.

### NOTE (54)

- K6 VO take extent — 21 dòng: 18 take kết thúc trước cuối cửa sổ khóa
  (fits sớm nhất −2,528 s: CIN_013_S03, CIN_016_S03), 3 take vượt cửa sổ —
  đúng 3 overrun đã biết theo verdict của chủ dự án, giữ nguyên chờ Codex
  quyết ở PR review: CIN_005_S03 +0,160 s, CIN_006_S03 +0,520 s,
  CIN_018_S03 +0,280 s. Không overrun mới.
- K5 stinger đúng ranh giới shot — 20 dòng: reveal/tension đặt đúng đầu shot
  (6,0 s mở S02 ở 18 scene; CIN_001 reveal 30,0 s mở S06; CIN_018 reveal
  0,0 s mở S01). Đây là cách đặt có chủ ý (mở shot), ghi nhận để tránh đọc
  nhầm thành lệch placement.
- K3 REQUIRED_NOT_VISIBLE — 4 dòng, đều đã có staging note trong ledger:
  CIN_013_S03 (NPC_REFUGEE_LEAD), CIN_014_S03 (NPC_TONG_BANH), CIN_015_S03
  (NPC_DIVER_LEAD), CIN_019_S03 (NPC_LYAN).
- K3 speaker off-screen — 5 dòng: CIN_004_S02 off-screen ĐÃ QUYẾT
  (DEC-MEDIA-P0 Q2, `onscreen=false` + take tên `..._LYAN_OFFSCREEN_...`);
  CIN_013_S03 / CIN_014_S03 / CIN_015_S03 / CIN_019_S03 staging note trong
  ledger (không phải mix defect).
- K4 guardrail chưa khẳng định lại — 4 dòng (độ phủ tài liệu, không phải
  verdict về hình — keyframe vẫn có thể đang thể hiện đúng): BROKEN_HORN
  chỉ khẳng định ở CIN_004_S01 trong khi BOSS_MANG_COT xuất hiện 3 shot
  CIN_004; NO_ENGLISH_UI chỉ ở CIN_012_S03 (3 shot CIN_012);
  UNDERWATER_NOT_DRY chỉ ở CIN_015_S02 (3 shot CIN_015);
  SUBJECT_CORE_SERPENT chỉ ở CIN_017_S02 (BOSS_TIDE_SERPENT xuất hiện
  3 shot CIN_017). LEFT_BANDAGE khẳng định đủ (NPC_TA_VAN_KHANH chỉ xuất
  hiện CIN_008_S03).

## 4. Kiểm toán scope

- Audit riêng nội dung khối này (base = head trước khối `4c53683`, head
  nội dung `4e22cf8`): **3 paths, 0 violations**. Commit báo cáo thêm 2 file
  (MD này + validation JSON) → khối này tổng cộng 5 file mới.
- Tích lũy (base = integration HEAD `9ac73dc`, head `4e22cf8`):
  **2141 paths, 1 violation** — chỉ `.gitattributes` đã biết (merge-base
  artifact; `git diff 9ac73dc 4e22cf8 -- .gitattributes` rỗng, file
  byte-identical với baseline owner), như các checkpoint trước; không sửa
  các report lịch sử để xóa ghi nhận đó.

## 5. Giới hạn / khuyết điểm

- Ledger là DRAFT: 4 FLAG cần director/Codex quyết (F047/F048/F052/F054);
  các NOTE K4 chỉ đo độ phủ khẳng định trong ledger, không xác minh bằng mắt
  rằng keyframe các shot còn lại có thể hiện đúng guardrail hay không —
  final picture vẫn character-lock-blocked ở 31 shot như trước.
- Không thay đổi bất kỳ file hình/audio/runtime nào; không nghe bằng tai
  (NOT_AUDITIONED giữ nguyên); không re-hash keyframe (đã verify ở motion
  ledger validator 2026-11-08, không có delta kể từ đó — theo Gói 38 rule 1).
- Stinger "đúng ranh giới shot" được quy về shot mở đầu tại giây đó theo
  quy ước đã ghi trong builder (reveal 6,0 s mở S02); nếu Codex muốn quy
  ước khác (stinger thuộc shot kết thúc tại đó), 20 NOTE K5 đổi shot chủ
  nhưng không đổi kết luận.

## 6. Khối tiếp theo

- M-F CP2 (re-mix áp voice palette) và M-E CP2 (composed SFX) vẫn chờ quyết
  định của director/Codex — không tự làm.
- 4 FLAG continuity (F047/F048/F052/F054) chờ director quyết rồi mới sửa
  timing/ledger; sau khi quyết, ledger này cập nhật v2 với `onscreen` /
  speaker ID đã chốt.
- P0 candidate B (M38-A) + ingest guide (M38-B) chờ review của Codex/chủ
  dự án; payload đăng M38-B đang chờ chủ dự án duyệt thẻ (luồng chính).
