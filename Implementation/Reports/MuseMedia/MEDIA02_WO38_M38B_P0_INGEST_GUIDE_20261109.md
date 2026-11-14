# MEDIA-02 WO38 M38-B — Hướng dẫn ingest chọn lọc P0 vào runtime (selective P0 runtime ingest guide)

Ngày: 2026-11-09 · Nhánh: `muse/media-production-20261104` · Parent head: `67a9c74` (WO38 M38-A)
Work Order: Gói 38 / WO38 mục M38-B (issue #116 comment 6733227370; PR #130) · Quyết định nền: DEC-MEDIA-P0-20261105
Subset manifest máy đọc được: `Implementation/Content/Narrative/Deliveries/P0_INGEST_M38B_SUBSET_v1.json`
Tool: `Tools/MediaProduction/Muse/build_p0_ingest_m38b.py` + `check_p0_ingest_m38b_v1.py` — checker **PASS 27/27** (`MEDIA02_WO38_M38B_VALIDATION_20261109.json`)

## 1. Mục đích và trạng thái

Tài liệu này cho Codex một đường ingest **chọn lọc** cho P0 (CIN_001 36 s, CIN_002 18 s, CIN_004 18 s — tổng 72 s): chỉ thay **hình** của 3 scene bằng candidate B (pose animation, M38-A) khi Codex chấp thuận sau review, trong khi **âm thanh không đổi** — cả runtime hiện tại (bản A) lẫn candidate B đều nhúng cùng một mix v3 fully composed. M38-B **không tự sửa runtime**: mọi file candidate nằm ở `Art_Source/`, cây `ClientGodot/` giữ nguyên byte (checker đối chiếu hash với bộ runtime-proof của M38-A: khớp 9/9).

Trạng thái trung thực: **DRAFT, NOT_AUDITIONED** — chưa ai nghe bằng tai, không có mix PASS, Muse không tự PASS. Hình B là pose animation procedural (5 pose/shot, 10 pose/s), chưa phải final acting; final picture vẫn chờ character lock ở 6/12 shot P0.

## 2. Subset: file nào đi đâu

| Scene | Candidate B (nguồn, trong Art_Source) | Đích runtime (giữ nguyên tên/path) | Giữ nguyên byte |
|---|---|---|---|
| CIN_001 | `Art_Source/Cinematics/P0_Motion/candidate_m38a/CIN_001_candidateB_640x360_30fps.ogv` — 3.319.028 B, sha256 `30f36b5dc743…` (Theora + Vorbis 160 kbps) · bản MP4 review: `Art_Source/Cinematics/P0_Motion/takes/CIN_001_pose_640x360_30fps.mp4` | `ClientGodot/assets/cinematics/CIN_001/CIN_001_640x360_30fps.ogv` (A hiện tại 1.483.364 B) | poster, SRT, timing |
| CIN_002 | `…/candidate_m38a/CIN_002_candidateB_640x360_30fps.ogv` — 1.635.327 B, sha256 `d70d970e05dd…` · MP4: `…/takes/CIN_002_pose_640x360_30fps.mp4` | `ClientGodot/assets/cinematics/CIN_002/CIN_002_640x360_30fps.ogv` (A: 749.277 B) | poster, SRT, timing |
| CIN_004 | `…/candidate_m38a/CIN_004_candidateB_640x360_30fps.ogv` — 2.538.804 B, sha256 `4ca2374637c8…` · MP4: `…/takes/CIN_004_pose_640x360_30fps.mp4` | `ClientGodot/assets/cinematics/CIN_004/CIN_004_640x360_30fps.ogv` (A: 768.058 B) | poster, SRT, timing |

Hash đầy đủ của cả 29 file trong subset (candidate, runtime hiện tại, WAV master, poster/SRT/timing, reel + contact sheet) nằm trong subset manifest; checker xác minh lại toàn bộ từ byte thật.

**Ngân sách dung lượng:** bộ OGV candidate B = 7.493.159 B so với bộ A = 3.000.699 B → **+4.492.460 B (+150 %)** cho P0. Pose animation nén kém hơn panel-hold tĩnh ở cùng mức chất lượng Theora (q:v 6, cùng công thức encode với runtime hiện hành); đây là chi phí hình chuyển động thật, không phải phình encode. Nếu cần ghìm dung lượng, hạ q:v là quyết định của Codex — Muse giữ q:v 6 để review hình đúng chất lượng dự kiến phát hành.

**Playback metadata:** `PLAYBACK_METADATA_v1.json` tham chiếu scene theo path + duration + `audioOwnership`, không ghim hash theo file; thay file tại cùng path, cùng duration (36/18/18 s) thì metadata vẫn đúng, **không cần sửa metadata**.

## 3. Các bước ingest (khi Codex chấp thuận B)

1. Chép 3 file OGV candidate đè lên 3 path runtime ở bảng §2 (hoặc thay cả MP4 nếu môi trường review dùng MP4 — cùng hình, cùng mix, khác codec).
2. Không đụng poster/SRT/timing. Không đổi tên file.
3. Chạy lại bộ kiểm phía Codex (decode + playback trong Godot) — phía Muse không chạy Godot.
4. Nếu bác B ở review: không làm gì cả — runtime vẫn là A, candidate ở Art_Source chỉ là hồ sơ review.

## 4. Quy tắc âm thanh: đúng MỘT đường duy nhất

- **Khuyến nghị — EMBEDDED_SOUNDTRACK_ONLY** (khớp `audioOwnershipPolicy` đã ghi trong PLAYBACK_METADATA): phát stream audio nằm trong chính file video (mix v3). Vì A và B nhúng **cùng** mix v3 (master WAV `ClientGodot/assets/audio/mix/p0_v3/CIN_00X_mix_draft_v3.wav`, hash trong manifest), ingest B **không** thay đổi âm thanh — không cần re-route, không cần đồng bộ lại.
- **Phương án external (chỉ khi adapter chủ động chọn):** tắt/bỏ qua stream nhúng và phát file mix v3 độc lập làm nguồn duy nhất. Không bao giờ phát đồng thời stream nhúng + file mix rời, và không bao giờ chồng VO take / palette pickup / stem lên soundtrack nhúng — đó là các bản alternate/thành phần để review, không phải lớp phát. Phát hai đường cùng lúc = tiếng đôi (double audio).
- Độ vang sau encode (đo loudnorm từ byte thật): OGV candidate lệch WAV master **0,16 / 0,24 / 0,05 LUFS** (CIN_001/002/004) — nằm trong dung sai 0,6 LUFS của checker; MP4 candidate dùng AAC 192 kbps từ cùng master.

## 5. Cue trong soundtrack nhúng (mix v3, fully composed — 0 file PackV1)

| Scene | Cue | Vai trò | Đoạn (giây scene) | Ghi chú |
|---|---|---|---|---|
| CIN_001 | MUSIC/quiet_discovery | nhạc nền | 6,0–30,0 | duck theo VO; seam wrap jump 0,000194 |
| CIN_001 | AMBIENCE/river_shore | ambience chính | 0–36 | không duck; seam 0,000188 |
| CIN_001 | AMBIENCE/rain_light | ambience phụ | 0–6,0 | không duck; seam 0,000181 |
| CIN_001 | SFX/CINEMA/reveal | stinger | tại 30,0 s, gain unity | placement PROPOSED |
| CIN_002 | AMBIENCE/river_shore | ambience chính | 0–18 | duck theo VO; seam 0,000188 |
| CIN_002 | AMBIENCE/underwater | ambience phụ | 0–6,0 | không duck; seam 0,000009 |
| CIN_002 | SFX/CINEMA/tension | stinger | tại 6,0 s, gain unity | placement PROPOSED |
| CIN_004 | MUSIC/boss_mang_cot | nhạc nền | 0–12,0 | duck theo VO; seam 0,002311 |
| CIN_004 | AMBIENCE/river_shore | ambience chính | 0–18 | không duck; seam 0,000188 |
| CIN_004 | SFX/CINEMA/reveal | stinger | tại 6,0 s, gain unity | placement PROPOSED |

Seam: các runtime OGG composed loop trong mix bằng mối nối acrossfade 1 s (công thức CP31). Số wrap jump trên là độ gián đoạn thô đo ở CP44 trên file runtime composed — cả 5 cue P0 đều ≤ 0,002311 và **không cue nào bị gắn cờ ear-check** (cue bị cờ là MUSIC/sa_hoa, không thuộc P0). VO trong mix: CIN_001 Ly An cửa sổ **24,8–28,5 s DECIDED** (bản B "Đầu kia! Giữ giúp tôi đầu kia!"); CIN_002 Tạ Vân Khanh 7,0–11,0 s; CIN_004 Ly An **off-screen** 7,5–9,5 s (DEC-MEDIA-P0 Q2 — scene chỉ có BOSS_MANG_COT trên hình).

## 6. Phụ đề

Một file SRT ngoài cho mỗi scene (`ClientGodot/assets/cinematics/<SCENE>/<SCENE>_vi.srt`), UTF-8 **không BOM**, chuẩn hoá **NFC**, LF, đúng **1 cue/scene** trùng cửa sổ thoại ở §5. Phụ đề **không** burn-in vào candidate B — player hiển thị SRT; không bật thêm nguồn caption thứ hai (tránh double caption). Ingest B không thay SRT.

## 7. Fallback

- **Hình:** bản A hiện tại chính là fallback — giữ nguyên tại chỗ cho tới khi B được chấp thuận; poster là frame tĩnh fallback.
- **Định dạng:** OGV lỗi decode trong môi trường review → dùng MP4 candidate B (cùng hình, cùng mix dạng AAC). Phát hành runtime vẫn theo chuẩn OGV của dự án.
- **Âm thanh:** nếu stream nhúng bị bác ở review, file mix v3 WAV độc lập là nguồn external duy nhất theo §4. Mix v1/v2 là alternate để so sánh A/B, không phát kèm.
- **Lưu ý Theora:** số frame lưu trữ (stored frames) của OGV **không** bằng duration × fps và không dùng làm bằng chứng chuyển động (đúng cảnh báo WO37/Gói 38). Bằng chứng hình B nằm ở contact sheet + checker spot-check frame tại 27,0 s: frame OGV lệch frame MP4 B 3,11 (gần) và lệch frame runtime A 8,14 (khác rõ) trong beat thoại S05.

## 8. Provenance / license

- Nhạc, ambience, stinger trong mix v3: **ORIGINAL_COMPOSED_BY_MUSE** — tổng hợp procedural, không sample (CP26/CP30). Candidate chứa **0 file ported PackV1**.
- VO: giọng TTS hư cấu bản draft (Ly An = Aria; câu nam CIN_002 vẫn là giọng nam draft dùng chung của CP04 — bản palette M-F CP1 là alternate, **chưa** nhúng vào candidate này). Không clone giọng người thật.
- Hình: pose animation procedural dựng từ keyframe storyboard (prompt của Cinema Production Pack v1) — M-C CP2; 8 strip sinh tự động đã bị loại và ghi lý do trong manifest M-C CP2.

## 9. Nghe kiểm / thiết bị

- Toàn bộ vẫn **NOT_AUDITIONED**. Bộ nghe kiểm: CP9 ear-audition pack (`EAR_AUDITION_PACK_v1.json`, 196 mục, 7 playlist; 10 mục ưu tiên P0) — verdict nghe thuộc về người nghe, Muse không tự chấm PASS cho mục chưa nghe.
- Phía Muse **không có thiết bị phát vật lý** và không chạy Godot playback (runtime là phía Codex). Bằng chứng thiết bị hiện có: Codex audit trên Windows tại `14b588c` — subset runtime khớp byte/size/hash, 21/21 soundtrack nhúng decode 50 ms đầu PASS. Nếu Codex phát trên thiết bị thật khi ingest, ghi device/output/vấn đề vào review của PR — Muse sẽ đối chiếu ở checkpoint sau.

## 10. Kiểm chứng (chạy lại được)

```
python3 Tools/MediaProduction/Muse/check_p0_ingest_m38b_v1.py \
  --out Implementation/Reports/MuseMedia/MEDIA02_WO38_M38B_VALIDATION_20261109.json
```
27 kiểm tra: hash/size 29 file; stream shape 12 file media (đúng 1 video + 1 audio, codec, 640×360@30, 48 kHz stereo, duration); SRT encoding + cửa sổ khóa; runtime không đổi so với proof M38-A; loudness OGV↔WAV ≤ 0,6 LUFS; spot-check frame B; quy tắc một đường audio; trạng thái NOT_AUDITIONED; file mới chỉ trong Art_Source; git sạch phía ClientGodot. Kết quả lần chạy này: **27/27 PASS**.

## 11. Giới hạn còn mở

- Hình B là draft pose animation; 6/12 shot P0 vẫn chờ character lock cho final picture (CIN_001_S05, CIN_001_S06, CIN_002_S02, cả 3 shot CIN_004).
- Giọng CIN_002 trong candidate vẫn là giọng draft dùng chung; muốn dùng palette M-F CP1 phải re-mix — quyết định của đạo diễn/Codex (khối M-F CP2), không tự áp.
- Chưa có bản 720p cho candidate B (chuẩn low 640×360 trước; bản standard thuộc M-B khi Codex yêu cầu).
- Mọi con số loudness/seam là đo từ byte, không thay cho nghe kiểm.
