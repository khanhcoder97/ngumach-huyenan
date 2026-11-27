# MEDIA-02 WO37 M-C — Motion / final-picture ledger v1 (63 campaign shots)

Ngày: 2026-11-08 · Nhánh: `muse/media-production-20261104` · Baseline integration: `6f79853`
(KHÔNG phải checkpoint 53/54: hai số đó thuộc về mix CIN_019/CIN_020 của
luồng chính — xem mục 0. Khối này cố tình không lấy số checkpoint để
không đụng hàng đánh số của luồng chính.)

## 0. Chỉ đạo / baseline

- Đầu lượt (18:40 JST) khối tiếp theo theo MEMORY là mix CIN_019 v1. Nhưng
  nhật ký `ngumach-dev-queue.md` ghi lúc 18:44 JST: chủ dự án lệnh trực
  tiếp "hãy làm đi" lúc 18:42 JST, luồng chính ĐANG LÀM CP53 + CP54
  (mix CIN_019 v1 và CIN_020 v1, khép WO37 checkpoint lớn 1); lượt định
  kỳ KHÔNG làm lại hai khối này mà chọn khối khác (WO37 M-C ledger 63
  shot / M-D / M-E / M-F hoặc M8 QA chỉ-đọc). Lượt này làm theo đúng
  ghi chú đó: khối M-C ledger.
- Issue #116 vẫn 19 comment; mới nhất vẫn là ACK CP52 (comment
  6719915595, 2026-11-08 09:39:31Z / 18:39 JST, đã đăng bởi luồng chính
  sau lệnh "gộp hết vào" của chủ dự án: mô tả PR #119 lên CP01–52 +
  ACK CP52, cả hai đọc lại byte-exact). KHÔNG có chỉ đạo mới của
  Codex/chủ dự án kể từ comment 6716052477 (WO37, 2026-11-08 11:14 JST).
- Integration vẫn `6f79853` (xác minh qua `git ls-remote` lượt này);
  PR #119 OPEN, head trước lượt này `0492f0a`, 101 commit / 1324 file,
  mô tả live CP01–52.
- Bằng chứng luồng chính đang làm CP53 trong cùng clone này: trong lúc
  lượt này chạy, cây làm việc xuất hiện file chưa commit của CP53
  (`Tools/MediaProduction/Muse/build_cin019_mix_v1.py`,
  `Art_Source/Audio/Muse/MIX/CIN019_DRAFT_V1/`,
  `ClientGodot/assets/audio/mix/cin019_v1/`, các manifest runtime và
  tool pack/metadata đã sửa,
  `MEDIA02_CHECKPOINT_53_SOURCE_REVALIDATION_20261108.json`). Lượt này
  KHÔNG chạm bất kỳ file nào trong số đó: commit nội dung chỉ gồm 4
  file mới của riêng ledger (xem mục 2), không sửa file chung nào, nên
  không xung đột merge với CP53/CP54.
- Scope audit vs baseline `6f79853`: **1328 paths, 1 violation**
  (`.gitattributes`) — vẫn chỉ là artifact merge-base như CP47–52:
  `git diff 6f79853 da1b7d5 -- .gitattributes` rỗng (file byte-identical
  với baseline owner). Audit riêng nội dung khối này (base `0492f0a`,
  head `da1b7d5`): **4 paths, 0 violations**.

## 1. Khối hoàn thiện

Ledger motion/final-picture v1 cho toàn bộ 63 shot campaign
(CIN_001–CIN_020; 12 shot prologue CIN_000 là phim độc lập, không nằm
trong 63) — kế hoạch làm việc cho nửa motion của WO37 M-C, xếp 63 shot
thành thứ tự thực thi từ file thật duy nhất (timing manifest, keyframe
manifest P0 + campaign, scene export manifest với motion Ken Burns
hiện tại + frameCheck, bảng sửa shot CP32, runtime cinematics manifest
để đối chiếu tổng 20 cảnh / 63 shot / 378 s / 21 cue thoại). Không
render hình mới, không quyết định gì về thiết kế nhân vật.

- `Tools/MediaProduction/Muse/build_motion_ledger_v1.py` (mới): builder
  ledger, luật R1–R6 ghi trong docstring + trong ledger.
- `Tools/MediaProduction/Muse/check_motion_ledger.py` (mới): validator
  độc lập — đọc lại toàn bộ nguồn, hash lại 63 keyframe PNG từ đĩa,
  suy ra lại từng phân loại, so khớp từng trường với ledger.
- `Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json`
  (mới): ledger — 1 dòng/shot, kèm bằng chứng chữ đằng sau mỗi quyết
  định (framing/defect trích, SHA keyframe, motion hiện tại).
- `Implementation/Reports/MuseMedia/MEDIA02_WO37_MC_MOTION_LEDGER_VALIDATION_20261108.json`
  (mới): kết quả validator (xem mục 2).

Luật phân loại (R1–R6, ghi đầy đủ trong ledger):
- R1: 12 shot P0 (CIN_001/002/004) → ACTION_ANIMATION ưu tiên 1
  (Codex: ưu tiên P0).
- R2: shot cần character lock cho final picture khi final picture
  phải cho thấy một nhân vật có tên nhận diện được: người nói khi
  dialogue onscreen là true, hoặc nhân vật có tên trong framing /
  knownDefects (cả khi defect ghi "không nhận diện được" — storyboard
  không cho thấy họ không xóa yêu cầu; đó chính là defect). PLAYER
  không bao giờ cần lock (VOICE_PLACEHOLDER_ONLY).
- R3: shot ngoài P0, không cần lock, không defect nhận diện người
  nói → ACTION_ANIMATION ưu tiên 2 (đủ reference: chủ thể motion là
  môi trường / đạo cụ / đám đông / nước, làm được từ storyboard mà
  không chờ lock).
- R4: shot ngoài P0 bị lock chặn, hoặc người nói không nhận diện được
  trong keyframe storyboard → KEN_BURNS_HOLD ưu tiên 3, giữ motion
  Ken Burns animatic cho tới khi có character lock / sửa final-picture.
  Ken Burns KHÔNG BAO GIỜ được gọi là final pose animation.
- R5: guardrails — sừng gãy CIN_004_S01 (đúng 1 sừng gãy + 1 sừng
  nguyên, canon, fix checkpoint 13); băng TAY TRÁI CIN_008_S03
  (fix CP32); không UI tiếng Anh CIN_012_S03; lõi pha lê + rắn thủy
  triều là chủ thể CIN_017_S02; dưới nước không phải sân khô
  CIN_015_S02 (cả ba fix CP32); không mascot ở đâu (assert: không
  framing hiện tại nào nhắc mascot — ghi chú defect "no mascot" được
  tính là bằng chứng vắng mặt, không phải vi phạm).
- R6: nhắc tới người chung chung ("a young warden", "workers", ...)
  chỉ ghi để kiểm toán, không đổi phân loại; lượt motion phải xác nhận
  trên hình rằng không có nhân vật có tên là chủ thể motion.

Kết quả phân loại (đo từ file thật):
- **38 shot ACTION_ANIMATION** (ưu tiên 1: 12 shot P0; ưu tiên 2: 26
  shot đủ reference) — làm được ngay khi lượt motion bắt đầu, không
  chờ character lock.
- **25 shot KEN_BURNS_HOLD** (ưu tiên 3) — chờ character lock /
  sửa final-picture.
- **31 shot cần character lock** cho final picture (tên nhân vật phải
  nhận diện được).
- **4 defect nhận diện người nói** (người nói onscreen: true nhưng
  storyboard không cho thấy họ nhận diện được):
  - CIN_013_S03 — Trưởng đoàn nói onscreen: true nhưng keyframe chỉ
    có Ly An (câu hỏi staging CP47, chưa có trả lời; `speakerNotInFrame`).
  - CIN_014_S03 — "Tong Banh is not identifiable" (hai ứng viên không
    mặc giáp khớp S01/S02).
  - CIN_015_S03 — thợ lặn "very small and seen only from behind
    (placeholder, awaiting character lock)".
  - CIN_019_S03 — "Ly An ... is not individually identifiable among
    the small distant figures".
  Cả 4 đều là việc của final-picture revision, không phải lỗi mix;
  ledger không dời VO, không sửa timing.
- **14 shot fix CP32** đã kiểm lại: SHA keyframe hiện tại khớp đúng
  SHA mới của CP32 cho cả 14 shot.
- **63/63 keyframe SHA** đã hash lại từ PNG trên đĩa và khớp manifest.
- 21 cue thoại khớp tổng campaign (20 cảnh / 63 shot / 378 s / 21 cue).
- Mốc M-C: checkpoint 2 (P0 motion/AB) = 12 shot P0; checkpoint 3
  (campaign motion) = 51 shot còn lại, theo đúng thứ tự
  `executionOrder` trong ledger.

Điểm cần lưu ý khi lượt motion bắt đầu (đã ghi trong ledger, luật R6):
- CIN_019_S02 (ưu tiên 2): "a grey-bearded elder in dark blue robes
  supervises" — elder này chưa được đặt tên trong framing; scene
  CIN_019 liệt kê NPC_CO_VO_TUONG trong charactersOnScreen nên lượt
  motion phải xác nhận trên hình elder có phải Cơ Vô Tướng không
  trước khi animate.
- CIN_020_S01/S02 (ưu tiên 2): "the villager" đọc thư / viết thư —
  người nhận thư chưa có identity/giới tính chốt (CP17:
  VOICE_LETTER_RECIPIENT placeholder), nên không tồn tại lock để chờ;
  motion animate một dân làng chung chung.
- CIN_005_S02: defect tự ghi rõ figure nón lá giữa sân là "not a
  named character, no canon conflict" — phân loại ưu tiên 2 là đúng,
  có bằng chứng trong defect.
- CIN_018_S03: nhân vật mặt nạ trong keyframe LÀ Cơ Vô Tướng theo
  framing ("present-day Co Vo Tuong in an ink-black hooded cloak") —
  ông cần lock vì xuất hiện trong hình, dù người NÓI câu thoại là
  Người chơi (off-screen, onscreen: null, CP52). Ledger phân biệt
  đúng hai việc này.

## 2. Kiểm chứng

- Ledger validator (`check_motion_ledger.py`): **PASS, 0 mismatches** —
  `MEDIA02_WO37_MC_MOTION_LEDGER_VALIDATION_20261108.json` (63 shot
  kiểm lại, 21 shot thoại, 63 keyframe SHA hash lại từ đĩa, 14 shot
  CP32 kiểm lại, tổng campaign 20/63/378/21 khớp; thứ tự thực thi +
  hai mốc M-C khớp đúng luật sắp xếp).
- Scope audit (`check_agent_scope.py`, base integration `6f79853`,
  head commit nội dung `da1b7d5`): **1328 paths, 1 violation** —
  `.gitattributes`, nhưng `git diff 6f79853 da1b7d5 -- .gitattributes`
  rỗng (file byte-identical với baseline owner sau PR #128); tool vẫn
  liệt kê vì nó diff từ merge-base `cf17178` (merge PR #117). Audit
  riêng nội dung khối này (base `0492f0a`, head `da1b7d5`): **4 paths,
  0 violations**.
- Commit nội dung: `da1b7d5` (4 file mới: 2 tool + ledger JSON +
  validation JSON; 3742 dòng thêm, 0 dòng sửa file cũ).
- Ba lần sửa tool trong lượt này (đã sửa, không ảnh hưởng kết quả):
  (1) assert "không mascot" ban đầu quét cả defect — defect của
  CIN_009_S01 ghi "No person, no hooded figure, no mascot" là bằng
  chứng vắng mặt, không phải vi phạm; đã sửa thành chỉ assert trên
  framing; (2) regex "boss" trần match nhầm "no boss lock exists"
  trong CIN_017 thành BOSS_MANG_COT — đã bỏ pattern "boss" trần,
  chỉ match "Mang Cot" + "serpent" theo scene; (3) kiểm phủ định
  theo câu đã nhầm CIN_016_S02 (câu chứa cả "Ha Mac sits at the
  table" lẫn "the survivor ... seen only from behind") và tách câu
  theo dấu phẩy đã tách nhầm CIN_019_S03 tại dấu phẩy trong ngoặc
  đơn — đã chuyển sang tách theo mệnh đề (clause) có nhận biết
  ngoặc đơn, kiểm lại 4 defect đều đúng.

## 3. Giới hạn còn mở

- Ledger là KẾ HOẠCH, không phải final picture: mọi keyframe vẫn ở
  mức STORYBOARD, chưa có character lock cho bất kỳ nhân vật có tên
  nào; chưa có shot nào được làm motion thật trong khối này.
- Phân loại dựa trên chữ trong framing/defect + trường onscreen của
  timing; 14 shot ưu tiên 2 có nhắc người chung chung cần lượt motion
  xác nhận lại trên hình (đặc biệt CIN_019_S02 elder, xem mục 1).
- 4 defect nhận diện người nói chờ final-picture revision / đạo diễn /
  Codex; ledger không đề xuất đổi người nói hay dời VO.
- Khối này không lấy số checkpoint (CP53/CP54 thuộc mix CIN_019/020
  của luồng chính); khi luồng chính xong CP53/CP54, số checkpoint
  tiếp theo vẫn theo chuỗi mix của họ.
- Commit nội dung `da1b7d5` CHƯA PUSH (cố tình — xem mục 4): luồng
  chính đang commit CP53 trong cùng clone; push lúc này sẽ làm lệch
  các bước xác minh head của họ (họ đọc remote head/PR API theo
  SHA kỳ vọng 0492f0a). Commit local này là ancestor sạch (chỉ file
  mới) nên commit CP53 của họ sẽ nằm trên nó và push của họ sẽ mang
  ledger lên cùng — hoặc lượt định kỳ sau push sau khi CP53/CP54
  đã lên remote.
- Mô tả PR #119 + ACK issue #116: không có payload mới trong lượt
  này (khối ledger không phải checkpoint mix; mô tả live vẫn CP01–52
  sau lần đăng 18:38 JST). Nếu chủ dự án muốn ghi ledger vào mô tả
  PR, luồng chính soạn payload riêng.

## 4. Khối tiếp theo

M-C checkpoint 2 — P0 motion/AB (12 shot P0: action animation 8–12
pose fps trên storyboard reference, A/B Ken Burns vs pose animation;
final picture vẫn chờ character lock) — sau khi CP53/CP54 đã push và
commit `da1b7d5` đã lên remote; hoặc M-D score/transitions, hoặc M-E
SFX/ambience variants (không đụng pipeline mix của luồng chính).
Không quay sang game sprite/UI/map/VFX/Godot.
