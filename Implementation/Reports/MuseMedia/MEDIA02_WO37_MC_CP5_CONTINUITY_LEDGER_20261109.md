# MEDIA-02 WO37 M-C CP5 — Continuity ledger v2: đóng 4 FLAG của CP4

Ngày: 2026-11-09 · Nhánh: `muse/media-production-20261104` · Baseline integration: `9ac73dc`
(Gói 38, item 4: tiếp motion/continuity bằng thay đổi asset thật — không phải
checkpoint hash lặp; khối này sửa nguồn dữ liệu rồi suy ra lại toàn bộ ledger,
không giao lại metadata/mix đã xong.)

## 0. Bối cảnh / chỉ đạo

- Issue #116 vẫn 26 comment; mới nhất vẫn là ACK M38-B + M-C CP4 của Muse
  (comment `6734370022`, đăng ~16:10 JST). KHÔNG có chỉ đạo mới của Codex/chủ
  dự án kể từ Gói 38 (comment `6733227370`, 14:46 JST).
- M-F CP2 (re-mix theo voice palette) và M-E CP2 (composed SFX) vẫn chờ quyết
  định của director/Codex — lượt này không làm hai khối đó.
- Khối này đóng 4 FLAG của continuity ledger v1 (CP4) bằng cách ghi trạng thái
  đã quan sát được từ nguồn có sẵn vào đúng nguồn dữ liệu (timing manifest,
  motion ledger, campaign timing manifest, runtime manifest), rồi suy ra lại
  ledger v2 bằng builder + checker độc lập.

## 1. Khối hoàn thiện — 4 FLAG đóng như dữ liệu, quyết định final picture vẫn mở

Ranh giới ghi rõ: lượt này KHÔNG quyết final picture. Những gì ghi vào nguồn
chỉ là trạng thái của hình storyboard + mix dự thảo hiện tại (đo được từ file
thật, có trích dẫn nguồn từng shot bên dưới). Quyết định "giữ voice-over hay
thêm người nói vào khung hình" vẫn thuộc director/Codex; nếu hình sửa, field
`onscreen` / `speaker` đổi theo bản sửa đó và ledger lên v3. Không có quyết
định sáng tạo nào được đưa ra thay director.

### F047 — CIN_005_S03 (Ly An) → NOTE F048 K3_SPEAKER_OFFSCREEN_DECIDED

- Bằng chứng: keyframe S03 là sân thượng nhìn thẳng từ trên xuống, chỉ có
  "people continue small daily tasks" (quần chúng nhỏ, không nhân vật tên);
  motion ledger `namedCharactersVisible=[]`,
  `speakerIdentifiableInStoryboard=false`, `characterLockRequired=false`
  (shot môi trường/khán chúng, đủ reference). Câu thoại đã được mix dự thảo
  đưa như voice-over.
- Ghi vào timing: `dialogue.onscreen: null → false` + `stagingNote` (M-C CP5,
  trích dẫn keyframe + motion ledger, ghi rõ quyết định final picture còn mở).

### F048 — CIN_009_S03 (Ly An) → NOTE F049 K3_SPEAKER_OFFSCREEN_DECIDED

- Bằng chứng: keyframe S03 là đường suối/mạch nước + rễ cây + miếu nhỏ — không
  có người trong khung; motion ledger `namedCharactersVisible=[]`,
  `speakerIdentifiableInStoryboard=false`. Câu thoại đã được mix dự thảo đưa
  như voice-over.
- Ghi vào timing: `dialogue.onscreen: null → false` + `stagingNote` (M-C CP5).

### F052 — CIN_017_S03 (Đội trưởng thợ lặn) → NOTE F053 K3_SPEAKER_OFFSCREEN_DECIDED

- Bằng chứng: keyframe S03 + knownDefects ghi "No person, no armed figure";
  motion ledger `namedCharactersVisible=[BOSS_TIDE_SERPENT]`; mix manifest
  CIN_017 (CP51) đã ghi sẵn "the line is delivered off-screen, like Ly An's
  voice in CIN_004 (DEC-MEDIA-P0 Q2)". Trạng thái off-screen này đã có từ
  CP51 — FLAG CP4 chỉ là vì nó chưa được ghi vào timing/ledger.
- Ghi vào timing: `dialogue.onscreen: null → false` + `stagingNote` (M-C CP5,
  trích dẫn CP51).

### F054 — CIN_020_S03 (người nói không có ID) → NOTE F055 K3_SPEAKER_OFFSCREEN_STAGING + NOTE F046 K3_REQUIRED_NOT_VISIBLE

- Bằng chứng: voice palette M-F CP1 đã định nghĩa role `LETTER_RECIPIENT`
  (giọng neutral placeholder `avocado_v2:ElvenWizard`, identity/gender
  UNDECIDED theo hướng của chủ dự án, CP54 — KHÔNG phải quyết định casting);
  take đã có tên `VO_CIN_020_S03_LETTERRECIPIENT_draft_v1.wav`; mix manifest
  CIN_020 (CP54) ghi "the speaker is present in the frame but his face is
  not visible and the line reads as an on-set voice from behind" (dân làng
  ngồi quay lưng ở mép trái khung).
- Ghi vào timing: `dialogue.speaker: null → "LETTER_RECIPIENT"`,
  `dialogue.speakerStatus: "PLACEHOLDER"`, `dialogue.onscreen: null → true`
  (người nói có mặt trong khung, theo ghi nhận CP54) + `stagingNote`
  (M-C CP5). Cue CIN_020 trong `CAMPAIGN_timing_manifest_v1.json` cũng đổi
  `speakerId: null → "LETTER_RECIPIENT"` (+ `speakerStatus`).
- Hệ quả do builder suy ra (không sửa tay): motion ledger cho shot này thành
  `speakerIdentifiabilityDefect=true`, `speakerNotInFrame=true`,
  `namedCharactersRequired=[LETTER_RECIPIENT]`, `characterLockRequired=true`,
  `motionClass: ACTION_ANIMATION → KEN_BURNS_HOLD`, `priority: 2 → 3` —
  final picture của shot này chờ chốt identity/casting của người nhận thư,
  đúng như thực trạng (villager chưa có identity, mặt không thấy, ngoại hình
  trôi giữa 3 shot).

### File thay đổi (commit nội dung `ed1691d`, 14 paths)

- Timing manifest 4 scene, cả 2 bản mirror (byte-identical):
  `Implementation/Content/Narrative/Deliveries/CIN_XXX/CIN_XXX_timing_v1.json`
  và `ClientGodot/assets/cinematics/timing/CIN_XXX_timing_v1.json` —
  chỉ đổi field `dialogue` của shot S03, giữ nguyên window/status/text/timing.
  SHA mới: CIN_005 `4437df319bac…` (2.850 B), CIN_009 `c8a567d67168…`
  (2.836 B), CIN_017 `8ce15679c56e…` (2.745 B), CIN_020 `0e6667dcda9f…`
  (2.972 B).
- `Implementation/Content/Narrative/Deliveries/CAMPAIGN_timing_manifest_v1.json`
  — cue CIN_020_S03 `speakerId` + `speakerStatus` (sha `ae55e71f…` →
  `6bac0c2f…`, 16.444 → 16.500 B).
- `Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json` —
  chạy lại bằng chính builder v1 (`build_motion_ledger_v1.py`, không sửa
  builder): diff chỉ chạm 4 shot + tổng/lists; validator
  `check_motion_ledger.py` PASS, 0 mismatch, 63 shot / 21 thoại kiểm lại.
  Tổng mới: ACTION_ANIMATION 38 → 37, KEN_BURNS_HOLD 25 → 26,
  lock-required 31 → 32, ident-defects 4 → 5, speakerNotInFrame 1 → 2.
  (sha `6730ea5707c7…`, 115.121 B).
- `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` —
  chỉ refresh hash timing 4 scene (`scenes[].timingSha256` +
  `sceneClips[].files.timing.sha256/sizeBytes`); không đổi file hình/audio
  nào, không đổi field `checkpoint` (đăng ký delivery vẫn là CP51).
  (sha `d1e3ee635944…` → `a1a22f00d09d…`, 71.505 B, cùng size.)
- `Implementation/Content/Narrative/Deliveries/CONTINUITY_LEDGER_v2.json`
  (mới, 91.911 B, sha256
  `fbee87fc2009489b2a40bd513c48c2a3bd807f9e9522c7dc36a2309ecc5fd466`).
- `Tools/MediaProduction/Muse/build_continuity_ledger_v2.py` (mới) và
  `Tools/MediaProduction/Muse/check_continuity_ledger_v2.py` (mới): copy
  của bộ v1, chỉ đổi ID/checkpoint/headSha (`9ab006f`, head trước khối),
  tinh chỉnh câu chữ evidence K3 off-screen ("designed" →
  "as recorded in the current picture/mix; final-picture decision open"),
  và checker thêm 3 mục cross-check mới (xem mục 2).

## 2. Kết quả đo từ byte thật

- Tổng: 20 scene / 63 shot / 378,0 s / 21 cue thoại / 21 shot thoại — khớp
  runtime manifest và motion ledger (không đổi).
- K1: tiling PASS 20/20 scene; timing ledger khớp timing manifest 63/63
  shot; duration khớp 4 nguồn 20/20 scene; timing sha + SRT sha khớp
  runtime manifest 20/20 (sau khi refresh hash).
- K2: SRT UTF-8 + NFC + LF-only 20/20 file; số cue == `dialogueCues`
  20/20; cue xếp thứ tự không chồng 20/20; 21/21 shot thoại có đúng 1 cue,
  cửa sổ nằm trong shot, text khớp ledger (NFC).
- K3: 0 character blink; 5 shot REQUIRED_NOT_VISIBLE đều đã có staging note
  trong ledger (4 cũ + LETTER_RECIPIENT mới, F046); 0 speaker không có ID.
- K4: 5 guardrail R5 truy vết (không đổi); K5: 0 dry shot, 0 segment
  boundary nằm giữa shot, 0 ambience seam > 0,005 trong các cue đang dùng;
  K6: 21/21 VO entry khớp đúng shotId, không có cửa sổ mix lệch cửa sổ khóa.
- Findings: **59 (0 FLAG + 59 NOTE)** — v1 là 58 (4 FLAG + 54 NOTE).
  4 FLAG cũ thành 4 NOTE (F048/F049/F053/F055) + 1 NOTE mới F046
  (LETTER_RECIPIENT required-not-visible). 54 NOTE cũ giữ nguyên, kể cả
  3 overrun đã biết (CIN_005_S03 +0,160 s, CIN_006_S03 +0,520 s,
  CIN_018_S03 +0,280 s — giữ nguyên chờ Codex quyết ở PR review) và
  20 stinger đúng ranh giới shot.
- Validator độc lập `check_continuity_ledger_v2.py`: **389/389 PASS,
  verdict PASS** (v1 là 326; +63 check: 20 mirror byte-identical, 21
  dialogue motion-ledger == timing-manifest, 4 flagClosure, 17 cue
  aggregate-manifest == timing, 1 dòng character mới LETTER_RECIPIENT).
  Không có check nào được nới lỏng so với v1.

## 3. Findings: 59 (0 FLAG + 59 NOTE)

Không còn FLAG nào. 4 FLAG của CP4 nay là NOTE có nguồn trích dẫn; 1 NOTE
mới (F046) ghi nhận shot CIN_020_S03 chờ chốt identity/casting người nhận
thư mới khóa được final picture. Toàn bộ 59 NOTE đều là trạng thái đã ghi
nhận (staging note / take extent / stinger / guardrail coverage), không phải
lỗi mix/audio: không NOTE nào chặn mix hiện tại.

## 4. Kiểm toán scope

- Audit riêng nội dung khối này (base = head trước khối `9ab006f`, head
  nội dung `ed1691d`): **14 paths, 0 violations**.
- Tích lũy (base = integration HEAD `9ac73dc`, head `ed1691d`):
  **2146 paths, 1 violation** — chỉ `.gitattributes` đã biết (merge-base
  artifact; `git diff 9ac73dc ed1691d -- .gitattributes` rỗng, file
  byte-identical với baseline owner), như các checkpoint trước; không sửa
  các report lịch sử để xóa ghi nhận đó.

## 5. Giới hạn / khuyết điểm

- Ledger là DRAFT: việc ghi `onscreen=false` cho CIN_005/009/017 và
  `onscreen=true` cho CIN_020 chỉ mô tả hình storyboard + mix dự thảo hiện
  tại; quyết định final picture (thêm người nói vào khung hay giữ
  voice-over; chốt identity người nhận thư) vẫn thuộc director/Codex.
  `LETTER_RECIPIENT` là ID placeholder (voice palette M-F CP1), KHÔNG phải
  canonical ID hay quyết định casting/giới tính.
- Không thay đổi bất kỳ file hình/audio nào; không nghe bằng tai
  (NOT_AUDITIONED giữ nguyên); không re-hash keyframe (đã verify ở motion
  ledger validator 2026-11-08, không có delta kể từ đó — theo Gói 38 rule 1).
- P0 timing manifest (`P0_timing_manifest_v1.json`) không có danh sách cues
  nên mục cross-check 2e chỉ kiểm được 17 cue của campaign manifest; 4 cue
  P0 được kiểm qua SRT + timing trực tiếp (mục dialogue/srtCue), không qua
  aggregate manifest — tồn tại từ trước, không phải do khối này.
- Motion ledger vẫn tên file v1 (`MOTION_LEDGER_v1.json`) dù nội dung đã
  chạy lại sau CP5: file này là bản suy ra từ timing bằng builder v1, và
  continuity ledger v2 đã ghi SHA mới của nó (`6730ea5707c7…`); không đổi
  tên để tránh vỡ các tham chiếu đã có.

## 6. Khối tiếp theo

- M-F CP2 (re-mix áp voice palette) và M-E CP2 (composed SFX) vẫn chờ quyết
  định của director/Codex — không tự làm.
- P0 candidate B (M38-A) + ingest guide (M38-B) chờ review của Codex/chủ
  dự án; payload đăng M38-B + ACK CP4/M38-B vẫn chờ chủ dự án duyệt thẻ
  (luồng chính) — lượt định kỳ KHÔNG tự đăng; payload đăng cho CP5 (PR
  #119 + ACK issue #116) cũng chờ duyệt thẻ tương tự.
- Final picture 32 shot character-lock-blocked (trong đó có CIN_020_S03 mới
  thêm) chờ character lock / chốt identity — không render hình mới khi chưa
  có lock.
