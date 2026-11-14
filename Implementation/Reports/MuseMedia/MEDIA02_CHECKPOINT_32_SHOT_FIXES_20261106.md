# MEDIA-02 CHECKPOINT 32 — Sửa lỗi nội dung shot + dọn mascot/nhân vật/băng/bối cảnh (Gói 31 item 2 + sửa phrasing trạng thái item 1) (2026-11-06)

## Khối vừa hoàn thiện

Codex review (issue #116 comment 6670983075, Work Order 31, PR #124
head 2fc895d) chỉ ra ba lỗi nội dung shot không cần character lock,
cộng dọn mascot/nhân vật không có trong prompt, băng trái/phải và
continuity môi trường. Checkpoint 32 **sửa cả 14 shot trong 8 scene**
bằng keyframe sinh lại (pack prompt nguyên văn + hậu tố sửa tường
minh — prompt nguyên văn vốn thiếu chi tiết nên generator mới bịa ra
UI/mascot/máy móc), xuất lại video 8 scene với cùng motion model
từng shot, kèm contact sheet trước/sau cho từng shot sửa.

**Ba lỗi chính — ĐÃ SỬA (kiểm bằng mắt trên contact sheet trước/sau):**

| Shot | Trước (CP25/CP22/CP23) | Sau (CP32) | Keyframe SHA cũ → mới |
|---|---|---|---|
| CIN_012_S03 | Thanh UI chọn game chữ Anh "WAIT IN SILENCE" / "OFFER THE PAPERS" nướng vào khung | Khung sạch hoàn toàn, không UI/chữ — Hạ Mặc sau bàn, 2 tờ giấy sáng đều, sảnh đèn lồng, núi qua cửa sổ, 1/3 dưới là bàn + sàn trống | 39ba784c → 84837005 |
| CIN_017_S02 | Máy ống tre + hàng bi phát sáng + người áo dài khoanh tay; không lõi, không rắn | Lõi pha lê trắng-xanh phát sáng ở trung tâm, 3 kênh đá nâng đỡ, rắn nước vảy gương cuộn quanh lõi, nền teal dưới nước | 6e747e26 → 710c1941 |
| CIN_015_S02 | Sân khô trên mặt nước, nắng xám + mascot trắng + chậu đất + tay găng quá khổ có dây khóa hiện đại + dây phơi | Hoàn toàn dưới nước teal đậm: bàn đá chìm + BÁT ĂN buộc dây cũ + dây dẫn tới cửa vòm đá + tay trần thợ lặn nắm dây, bong bóng cụm nhỏ | fc4e92eb → 11847adf |

**Dọn dẹp kèm theo (cùng item 2) — ĐÃ SỬA, kiểm bằng mắt:**

| Shot | Lỗi cũ | Sau (CP32) | Keyframe SHA cũ → mới |
|---|---|---|---|
| CIN_012_S01 | Mascot trắng đội mũ trùm ở frame trái + palette dusk xanh đậm | Không mascot, đúng 2 worker trước lò đá, palette cam nóng phủ toàn cảnh | 8c2efbd4 → 489eb56b |
| CIN_015_S01 | Nhân vật đội nón lá cầm đèn đứng khô trên tường tàn tích + cột bong bóng dày | Không còn nhân vật nào, tàn tích chìm teal, bong bóng cụm nhỏ, cá nhỏ ở rìa | 6dd170f8 → 6b067bab |
| CIN_015_S03 | Đọc như tàn tích khô trong nhà, palette tím đá | Rõ ràng dưới nước: tint teal toàn khung + bong bóng, đèn ấm tường trái, 3 motif đồng đầu xa, thợ lặn nhỏ ở lối vào | eb8af0fd → e7db810d |
| CIN_017_S03 | Nhân vật vũ trang đội nón lá đứng frame trái + hàng chấm sáng trên nước | Chỉ còn bóng rắn chữ S khuất dần xuống hẻm sông mù sương, tre gãy + đá ở bờ gần, không chấm sáng | decd8051 → fe4a603b |
| CIN_008_S03 | Băng đọc như cẳng tay PHẢI + tay băng cầm 2 dải trắng | Băng quấn cẳng tay TRÁI (phía ngoài, xa hồ), tay phải lành mở rõ, tay băng không cầm gì | ac807d2e → e41232c9 |
| CIN_011_S01 | Phụ nữ áo teal ngồi cạnh + phù điêu đĩa tròn đơn | Không người; phù điêu là 3 mảnh đồng ghép có bản lề, ký hiệu tay/nước dưới hàng vạch đếm | 81d4d3c0 → 5762cd16 |
| CIN_011_S03 | Medium two-shot + phụ nữ + phù điêu đá nứt | Detail close-up: chỉ một mình Hạ Mặc, bút dừng trên vết đục phù điêu ĐỒNG, sổ mở có lề trống | 316a9435 → 6f167581 |
| CIN_010_S02 | Rừng tre + miếu; Sầm thanh niên gầy; chậu đá | Sa mạc tro vàng khớp S01 (cồn cát, mesa, lều rách, xe gỗ); Sầm trung niên chắc nịch râu ria; rót từ bình đất vào thùng gỗ lớn có nắp | 318ffd4e → b89f2848 |
| CIN_010_S03 | Đất đá xanh rêu; Sầm thanh niên gầy; chai thủy tinh | Sa mạc tro vàng khớp S01; Sầm trung niên chắc nịch; vải bản đồ + 2 dây lộ trình + bình đất, không chai thủy tinh | 856aa420 → d998bf59 |
| CIN_006_S02 | Tay găng quá khổ bị nhòe + mặt nhợt nhạt một mắt đen chen từ mép phải; nhựa xanh như vệt tinh thể | Toàn bộ bàn làm việc: dấu đồng trên chồng giấy thô, sợi nhựa xanh mảnh lộ giữa các lớp giấy, 1 tay găng nhỏ góc dưới-phải trọn trong khung (lần 3, đổi bố cục sau khi 2 lần sinh đầu vẫn tay quá khổ) | 0f8c4f10 → ef1a9a09 |
| CIN_009_S01 | Nhân vật nhỏ đội mũ trùm trắng ở góc dưới-trái; tối/xanh hơn daylight | Không còn nhân vật nào; suối teal ban ngày sáng giữa hai bờ rễ nứt, đốm sáng trôi dọc nước | d38c7ad8 → 5d64d3e2 |

- **Video xuất lại (8 scene, 18 s / 3 shot, Ken Burns, không audio, không phụ đề nướng):** motion giữ nguyên từng shot theo export manifest cũ (S03 zoom-out vẫn zoom-out). MP4 SHA cũ → mới / OGV SHA cũ → mới (stored frames): CIN_006 d263ddf9 → a8225efb / 8c10c78c → fa183c19 (480); CIN_008 2ed5fc71 → c367c263 / 963352ee → ffeabb38 (509); CIN_009 c67ffcfd → f7cfd85d / 4997e04f → ca620680 (503); CIN_010 9b88d2bd → 6408d511 / 77046c23 → bcc9618e (376); CIN_011 37984cfc → e15a930c / 45d3f748 → b6d6c8a9 (486); CIN_012 52feb6e3 → e2a1833e / b20560cd → 943fab25 (521); CIN_015 c7e0afa6 → 2901a88a / b86abcd4 → fb7936c7 (511); CIN_017 f29928e4 → 001ee554 / aa8674c8 → 3278b262 (506). Poster đổi theo S01 mới ở CIN_009/011/012/015; poster CIN_006/008/010/017 không đổi (S01 không sửa). Identity diff mọi shot < 10 (cao nhất 7,305 ở CIN_009_S03 zoom-out, frame 539), motion diff mọi shot > 1,5 (thấp nhất 14,69 ở CIN_017_S03).
- **Contact sheet trước/sau:** 14 file `Art_Source/Cinematics/Campaign/<SCENE>/keyframes_16x9/before_after_<SHOT>_cp32.png` (1280×360, trái = keyframe cũ, phải = keyframe mới), SHA ghi trong bảng trên (đủ 14 SHA trong báo cáo này, mục "Sửa cụ thể").
- **Staging:** 14 WebP 2048×1152 mới tại `~/workspace/goals/ng-m-ch-continuous-development/hidden_files/cin<NNN>_keyframes_staging/` (8 staging agent song song + 1 lần sinh lại CIN_006_S02 do luồng chính sau khi 2 lần đầu FAIL tay quá khổ), SHA staging đã kiểm độc lập 14/14 khớp; handover từng scene đã thêm mục revision CP32.
- **Sửa phrasing trạng thái (Gói 31 item 1, phần báo cáo/manifest):** câu "chỉ CIN_001_S05 được duyệt" đã lỗi thời — nay ghi đúng: **CIN_001_S05 (24.8–28.5 s, bản B) là cửa sổ DECIDED duy nhất; cả 21 cửa sổ đã được duyệt để sản xuất DRAFT VO theo quyết định D1 Gói 30 (PR #120, `media_draft_timing_decisions_20261105.json`)**; 3 overrun VO (CIN_005_S03 +0,160 s, CIN_018_S03 +0,280 s, CIN_006_S03 +0,520 s) giữ nguyên cửa sổ chờ Codex quyết ở review PR. Phrasing đã sửa trong: runtime audio manifest, runtime cinematics manifest, validator limits, và báo cáo này. **Cập nhật mô tả PR #119 vẫn cần thẻ duyệt của chủ dự án — luồng chính xử lý, văn bản đề xuất ở mục "Trạng thái GitHub".**
- **Không đổi:** timing/SRT/dialogue của cả 8 scene; audio 610 file; campaign totals 20 scene / 63 shot / 378 s / 21 cue; 12 scene còn lại không đụng tới.

## Trạng thái GitHub

- Nhánh `muse/media-production-20261104`: nội dung ở commit ngay trước báo cáo này; PR #119 vẫn OPEN và HOLD, head 0f2678f (CP31). Issue #116 vẫn OPEN, **13 comment** — ACK Gói 31 đã được chủ dự án duyệt và đăng bởi luồng chính (comment 6671599404, đọc lại byte-exact).
- Integration baseline mới: **`abcf254`** (PR #123 đã merge). Checkpoint này re-baseline theo abcf254 (scope audit + manifest baseSha); policy `.gitattributes` vẫn chưa về nhánh media — **Gói 31 item 5 vẫn chờ merge commit của chủ dự án** (file gốc thuộc Codex; Muse không tự viết policy), sau đó mới kiểm fresh checkout + re-audit.
- **Cần luồng chính cập nhật mô tả PR #119** (qua GitHub connector, cần thẻ duyệt): đổi trạng thái "chỉ CIN_001_S05 được duyệt" thành "21 cửa sổ đã được duyệt để sản xuất DRAFT VO theo Gói 30 (PR #120); chỉ CIN_001_S05 là DECIDED (bản B, 24.8–28.5 s); giữ 3 overrun để review", và thêm checkpoint 32 (14 shot sửa trong 8 scene, video xuất lại, runtime audio vẫn 610, campaign 20/63/378 s không đổi).

## Sửa cụ thể (file nào, đổi gì)

| File | Đổi |
|---|---|
| `Tools/MediaProduction/Muse/revise_campaign_shots_goi31.py` (mới) | Builder revision CP32: nhận staging mới qua JSON, giữ motion từng shot theo export manifest cũ, kiểm unchanged-shot byte-identical, xuất contact sheet trước/sau, viết lại keyframe manifest + export manifest với checkpoint 32 / base abcf254. (Lỗi CIN_006 không có trong campaign timing manifest đã sửa trong lượt: fallback sang `CIN_006_timing_manifest_v1.json`.) |
| `Art_Source/Cinematics/Campaign/<8 scene>/keyframes_16x9/keyframe_<SHOT>.png` (14 file) | Keyframe mới 640×360 downscale từ staging WebP 2048×1152 (SHA mới trong bảng trên). |
| `Art_Source/Cinematics/Campaign/<8 scene>/keyframes_16x9/before_after_<SHOT>_cp32.png` (14 file mới) | Contact sheet trước/sau 1280×360. SHA: CIN_006_S02 c72a6556; CIN_008_S03 07979e65; CIN_009_S01 a8a34817; CIN_010_S02 47a07a5a; CIN_010_S03 712d5612; CIN_011_S01 5182b366; CIN_011_S03 9c1f8e92; CIN_012_S01 0504092c; CIN_012_S03 9fdef02a; CIN_015_S01 e905f2da; CIN_015_S02 72df7b36; CIN_015_S03 f9562ef1; CIN_017_S02 10a9e290; CIN_017_S03 3a5cb816. |
| `Art_Source/Cinematics/Campaign/<8 scene>/<SCENE>_keyframes_manifest_v1.json` (8 file) | Checkpoint 32 / base abcf254; staging mới (file/SHA/snapshot) + framing/knownDefects mới cho 14 shot; shot không sửa giữ nguyên staging + SHA keyframe cũ (kiểm byte-identical). |
| `ClientGodot/assets/cinematics/<8 scene>/<SCENE>_640x360_30fps.mp4` + `.ogv` (16 file) | Video xuất lại (SHA mới trong bảng trên). |
| `ClientGodot/assets/cinematics/<8 scene>/<SCENE>_poster.png` (4 file: CIN_009/011/012/015) | Poster = keyframe S01 mới. |
| `ClientGodot/assets/cinematics/<8 scene>/scene_export_manifest_v1.json` (8 file) | Checkpoint 32 / base abcf254; SHA/size/duration mới; frameCheck mới; motion giữ nguyên nhãn cũ; notes sửa lỗi + dialogue note giữ nguyên. |
| `ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json` | Checkpoint 32; sceneClips 8 scene cập nhật SHA; notes sửa phrasing trạng thái (21 cửa sổ DRAFT VO) + ghi fix CP32; campaignTotals không đổi. |
| `ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json` | Chỉ nhãn checkpoint 32 + sửa phrasing trạng thái (21 cửa sổ DRAFT VO); **không file audio nào đổi** (total vẫn 610). |
| `Tools/MediaProduction/Muse/build_runtime_delivery.py` | Nhãn checkpoint 32 cho cả 2 manifest; notes cinematics sửa 3 mô tả lỗi cũ (CIN_006_S02, CIN_009_S01, batch CP25) + thêm note CP32; notes audio sửa phrasing trạng thái. |
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Nhãn checkpoint 32 / base abcf254; limits note: batch CP25 + CIN_006/CIN_009 defects đã FIX ở CP32; dialogue windows: 21 cửa sổ duyệt DRAFT VO theo D1. |
| `Tools/MediaProduction/Muse/verify_runtime_delivery.py` | Nhãn checkpoint 32 / base abcf254; chuỗi "verifies" thêm checkpoint 32. |

## Kết quả kiểm chứng lại (byte thật, ffprobe/ffmpeg)

### 1. Build revision — PASS 8/8 scene
`revise_campaign_shots_goi31.py` exit 0: 8/8 scene (CIN_006 cần sửa fallback manifest riêng; các scene khác PASS ngay lượt đầu). Unchanged-shot keyframes tái tạo byte-identical (guard trong builder, không lỗi nào). Frame identity < 10 và motion > 1,5 ở mọi shot; OGV stored frames 376–521 (< 540, đúng quy tắc Theora gộp frame gần giống).

### 2. Negative check bằng mắt — PASS 14/14 shot
Luồng chính đọc trực tiếp 14 contact sheet trước/sau: lỗi nhắm tới đã hết ở cả 14 shot (không còn UI/chữ Anh, có lõi + rắn, chìm dưới nước, không mascot, không phụ nữ teal, băng tay trái, sa mạc tro vàng, dấu + sợi trong giấy, suối ban ngày không figure); không xuất hiện chữ đọc được / UI / mascot / nhân vật mới nào trong khung sau. Chi tiết còn sót ghi trung thực trong từng keyframe manifest (mục "Giới hạn còn lại").

### 3. Runtime delivery — PASS
`build_runtime_delivery.py` exit 0: audio copied 610 (22 + 519 + 30 VO + 13 mix + 26 composed), cinematics sceneClips=20, scenes=20, timing+srt=40; M6 ALL VERIFIED.

### 4. Source re-validation — PASS, 0 mismatch
`validate_media_deliveries.py` verdict PASS. JSON: `MEDIA02_CHECKPOINT_32_SOURCE_REVALIDATION_20261106.json` (audio files checked 1151, campaign batch keyframes 39/39, CIN_006/009 keyframes 3/3, scene clips 20/20).

### 5. Runtime re-verify — PASS, 0 mismatch
`verify_runtime_delivery.py` verdict PASS: runtime audio 610 = totalFiles 610, scene clips 20, scene-clip files 100. JSON: `MEDIA02_CHECKPOINT_32_RUNTIME_REVERIFY_20261106.json`.

### 6. Scope audit — 0 vi phạm
`Tools/Coordination/check_agent_scope.py` (base = integration `abcf254`, branch `muse/media-production-20261104`): **1182 changed paths, 0 violations** (nội dung ở commit `6ec41d7`) — tất cả nằm trong root media policy cho phép (`Art_Source/Cinematics/`, `ClientGodot/assets/cinematics/`, `ClientGodot/assets/audio/`, `Implementation/Reports/MuseMedia/`, `Tools/MediaProduction/Muse/`).

## Giới hạn còn lại

- STORYBOARD, không phải final picture: mọi nhân vật trên màn hình vẫn chưa có character lock (Hạ Mặc, Sầm, Tạ Văn Khánh, thợ lặn, rắn thủy triều đều là placeholder do generator vẽ); motion vẫn là Ken Burns trên still, KHÔNG phải pose animation cuối (cần reference + pose animation đã khóa). Không gọi Ken Burns là final pose animation.
- Khuyết điểm còn sót sau sửa (đã ghi từng shot trong keyframe manifest): CIN_012_S03 tay Hạ Mặc khuất sau bàn nên vị trí "withdrawn" không thấy rõ; CIN_015_S02 tay thợ lặn tiền cảnh vẫn lớn và bị cắt ở mép phải (đã bỏ dây đeo/găng); CIN_010_S02/S03 trang phục Sầm chưa khớp nhau (gi-lê nâu + khăn quấn vs áo xanh + khăn băng đô); CIN_011_S03 phù điêu là tấm đồng chữ nhật có khung, khác dạng 3 mảnh ghép rời ở S01; CIN_017_S02 kênh đá đọc như kết cấu đá chạm khắc, rắn quấn đá nhiều hơn quấn lõi; CIN_015_S01/S03 bong bóng vẫn hơi dày, S03 hơi nghiêng thay vì top-down thuần; CIN_006_S02 tay giữ mép giấy thay vì căn dấu trực tiếp.
- 3 overrun VO giữ nguyên cửa sổ chờ Codex quyết ở review PR (CIN_005_S03 +0,160 s, CIN_018_S03 +0,280 s, CIN_006_S03 +0,520 s).
- Gói 31 item 5 (`.gitattributes` policy) vẫn chờ merge commit của chủ dự án từ integration abcf254; sau merge mới kiểm fresh checkout + re-audit. Native playback là việc của Codex — không báo game đã tích hợp.
- Gói 31 item 3 (A/B review shortlist) và item 4 (minimal runtime pack) là khối tiếp theo.
