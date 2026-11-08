# Muse — MEDIA-03→05: toàn campaign, âm thanh và gói runtime

Owner Muse, issue #116/PR #119, tiếp nhánh media hiện có. Nhận toàn M-A→H, không dừng sau một mix/ACK. Pin review694ddb6 (CP45):618audio,12soundtrack nhúng/9scene im lặng, metadata playback và pronunciation đã có. Ba shot lớn trước đã sửa; giữ cải thiện đó. Final picture/mix vẫn DRAFT, NOT_AUDITIONED, chưa native.

Trong lượt review đã có successor b14d7de/CP46 thêm mixCIN012: tác giả báo619audio,13embedded/8silent. Đã đọc delta source, chưa kiểm byte lại ở head đó. Không yêu cầu làm lại checkpoint đã giao; xác định danh sách còn lại từ manifest mới và giữ pin của từng phép đo.

Chỉ cinematic/video/audio và tools/reports trong media roots được giao. Không game sprites, actor animation, map, UI, VFX hoặc Godot runtime; Codex giữ visual/gameplay runtime. Antigravity không nhận việc. Không self-merge, giữ source/stems/provenance và production OFF.

## M-A — delivery và baseline policy

PR127 đã nhận vào nhánh media, PR128 đã vào integration6f79853; hai LF roots mới nay là owner policy trên integration. Fetch/reconcile baseline mới, scope audit phần Muse so với baseline owner. Giữ lịch sử report ghi known policy violation, không sửa để xóa evidence. Không reset/clean/force-push hoặc sửa game files để resolve conflict. PR mergeable chỉ là git state, chưa là final-media approval.

Giao fresh checkout Windows/Linux, LFS bytes/hash/size/UTF-8 NFC/LF, codec/duration/fps và source→runtime manifest. Paths/IDs/hash/version khớp; validator phải bắt mismatch và LFS pointer. Cập nhật head/title/body/handoff theo thực tế trong phạm vi giao việc, không chờ final-media approval mới báo metadata.

## M-B — hoàn soundtrack cho toàn21entry

Hoàn9scene CIN012–020 còn im lặng ở CP45; giữ20campaign scene/63shot/378s, prologue CIN000 riêng. P0v3 fully-composed/CIN006v1 là alpha candidate, không xóa alternate v1/v2. Mix assignment có source, tone/pacing, stinger, ducking, loop/head-tail và voice ownership; không chỉ áp cùng gain cho mọi cảnh rồi gọi final.

Sau mỗi batch cập nhật PLAYBACK_METADATA/runtime pack: embedded soundtrack là một nguồn audio duy nhất, không phát thêm standalone mix/VO; clean video+overlay SRT, không double caption. MP4 master/review riêng, OGV Theora640×360/30fps runtime+poster/SRT/timing. Standard720p cần file và budget đo thật. Rewatch/skip/seen/fallback không grant quest.

21cửa sổ đã duyệt cho draft VO, chưa khóa final picture/mix/autoplay. Giữ3overrun CIN005S03/CIN018S03/CIN006S03 theo chỉ đạo trước; không tự tăng tốc giọng, nới cửa hoặc cắt canon. Tail trim phải có byte/timecode và pickup đề xuất. CIN011 dư8ms là margin mỏng cần priority QA, không chỉ đánh dấu FITS.

## M-C — motion và final picture theo shot

Giao ledger63shot với ref/status/dependency/known defect. Ken Burns trên still chưa là pose animation cuối. P0 và shot đủ ref tiếp animation hành động, nhịp, độ trễ có chủ ý theo Art Bible/cadence8–12posefps trong video30fps. Camera/nước/dây/phản chiếu phải có diễn biến đọc được; không optical-flow morph làm đổi mặt/chi.

Giữ nhận diện NPC, băng tay trái, sừng gãy, đạo cụ và góc nhìn; không thêm mascot hoặc nhân vật ngoài brief. Không trả UI chữ Anh vào CIN012, sai subject CIN017 hoặc sân khô CIN015. Mỗi revision có before/after/director ref/contact sheet và export/hash mới. Character lock chỉ chặn shot phụ thuộc; môi trường, nhịp, nước/dây, audio và metadata tiếp tục. Thiếu ref thì giao bảng exact character/shot/reference cần, không khóa cả campaign bằng một câu chờ lock.

## M-D — nhạc toàn game và transitions

Tiếp score cho hub/explore/Bến Mưa/Thanh Lạc/Thăng Long/mưa/đầm/rừng/núi/sa mạc/dungeon/boss/arena/tragedy/resolution theo Audio Direction. Giữ hệ leitmotif nhưng arrangement/instrumentation/density/rhythm/space có chức năng theo cảnh, không chỉ đổi pitch/tempo một loop để đủ số cue.

Giao scores/stems/intro-loop-outro/transitions/phase-layer candidates, cue ID/source/provenance/hash và hướng mix. Loop click/true peak/loudness/codec đo bằng byte; thẩm âm báo riêng.541file ported PackV1 không tính là sáng tác mới. Giữ candidates cũ, adoption/mixer do Codex; không tự thay canonical bằng alternate.

## M-E — SFX/ambience có biến thể thực

Phủ vật liệu bước chân,5weapon/30skill cast-impact-miss, guard-counter, boss warning, loot/equip/consume/inventory-full, quest/NPC/craft/forge/market/water/weather/cinema. Dùng cue/skill ID đã có nguồn; thiếu ID gửi proposal, không hardcode runtime key mới. Variants/minGap/voiceCaps/priority/distance/ducking metadata đủ consumer đọc, audio không quyết định hit hoặc reward.

Ambience có phân tần, phối cảnh, event layers và motion chất liệu; không chỉ filtered noise để đủ file. Sample/license/voice/procedural composition ghi đúng nguồn. Làm cue độc lập khi character lock hoặc VO casting chưa final.

## M-F — VO và pronunciation review pack

Giao voice palette hư cấu phân biệt Ly An/Tạ/Hạ Mặc/Sầm/narrator/player placeholder, pickups/alternate/take purpose/clean stems và subtitle mapping. Không clone giọng thật. DRAFT TTS chưa là casting hoặc diễn xuất final.

Pronunciation table16name/4spoken cần source form thống nhất; Tạ Vân Khanh là spelling đã chốt. Approximate IPA không là audible PASS hoặc yêu cầu đổi cả cast sang giọng Bắc. Giao playlist/timecode/A-B/name occurrences và câu hỏi nghe cụ thể; giữ3overrun, không sửa thoại canon. Không thu hàng đọc vô ích cho tên chưa xuất hiện chỉ để tăng count.

## M-G — QA và device handoff

Automated QA kiểm source/runtime/hash/pointers/LF/codec/resolution/fps/duration/mux ownership/subtitle text/cues/safe area/peak/loop/trim. Visual QA xem shots trước/sau và continuity cả scene. Theora có repeat frames: stored-frame count không tự bằng duration×fps, không kết luận mất motion chỉ từ con số ấy.

Nếu môi trường nghe được, thẩm âm theo playlist và ghi người/thiết bị/phát hiện thật. Nếu không, giữ NOT_AUDITIONED, giao timecodes và lỗi ưu tiên cho reviewer; không lặp LUFS thành bằng chứng nghe. Native Godot playback/CPU/export do Codex kiểm; Muse giao low/standard files và profiling input. Missing file hoặc manifest sai phải có failure/fallback contract rõ, không nhét debug text vào cinematic.

## M-H — bốn checkpoint lớn, làm liên tục

1. Hoàn9mix còn thiếu,21entry metadata/pronunciation/fallback và source pack.
2. P0 motion/final-picture revisions cho shot đủ ref, soundtrack A/B.
3. Campaign motion batches, score/SFX palette và VO review/pickups.
4. Full campaign exports/stems/provenance/QA, clean checkout và device pack.

Mỗi checkpoint có source/media thật, exact SHA/version/commands/raw output, phần đã xem/nghe và phần còn NOT_AUDITIONED. Push rồi tiếp module độc lập, không dừng sau một mix/report hoặc chờ merge PR119. Cập nhật issue116 theo checkpoint và PR body theo head thật; file đã nằm trong ClientGodot/assets chưa chứng minh game đã tích hợp.
