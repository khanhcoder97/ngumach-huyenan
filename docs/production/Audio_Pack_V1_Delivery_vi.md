# Bàn giao âm thanh gốc v1 — Ngũ Mạch: Huyền Ấn

Ngày 2026-10-29 · Codex · NGM_ORIGINAL_AUDIO_V1 · trạng thái RENDERED_CANDIDATE.

## 1. Sản phẩm thật và phạm vi

195 cue tạo thành 541 file runtime, phủ đủ 63 soundKey của baseline thiết kế. 173 cue ngắn có ba biến thể; 9 nhạc nền và 13 môi trường có một loop mỗi cue. Runtime khoảng 39,87 MiB; 541 master khoảng 89,86 MiB. Không cộng master vào build. Đây là nhạc/âm hiệu tổng hợp DSP và score nguyên bản, không phải bản thu nhạc cụ hay diễn viên chuyên nghiệp.

| Hạng mục | Sản phẩm | Điều còn cần duyệt |
|---|---|---|
| Năm lớp nhân vật | 30 cue kỹ năng, 90 clip | Khớp marker animation và event server; cân âm từng skill |
| Quái | 8 họ âm × tấn công/bị thương/chết × 3 biến thể | 30 ID quái dùng lại họ âm minh bạch, không phải 30 bộ tiếng riêng |
| Boss | 12 ID có intro/warning/success; Mãng Cốt giữ 3 cảnh báo riêng | Cảnh báo generic của boss khác chưa thay thiết kế đòn/telegraph |
| Thế giới và chức năng | Bước chân, thu hái, rèn, giao dịch, bang, PvP, nhiệm vụ, pet/mount, UI và các cue khác trong catalog | Adapter theo kết quả thật, không phát thành công khi request mới gửi |
| Map | 46 binding ứng viên, dùng chung 9 nhạc / 13 môi trường | Duyệt theo khu/mode/giờ/thời tiết; không 46 bản nhạc độc lập |
| NPC | 83 ID có cue mở/đóng dịch vụ | spokenVoice=null; chưa lồng tiếng có lời |
| Đồng hành/tọa kỵ | 10 ID có cue triệu hồi dùng chung | Không gọi đây là tiếng thu riêng từng loài |
| Cinema | 20 scene ID có stinger binding và revealTier | Chưa dựng theo hình, chưa có thoại/stem final |

Danh sách chính xác ở `Client/Assets/AudioManifests/game_audio_v1.json`; không suy phạm vi hoàn thiện game từ số lượng file âm thanh.

## 2. Nhạc nền và chất liệu

| Track / score | Ý đồ |
|---|---|
| ben_mua — Thư chưa gửi | Giai điệu thưa, mưa và khoảng trống cho mở đầu/câu chuyện |
| thang_long — Dòng người qua phố | Nhịp ngũ cung ấm, chuyển động mua bán, tránh kèn chiến trận liên tục |
| boss_mang_cot — Chuông dưới đầm | Trầm và căng nhịp, nhường dải trung cho cảnh báo |
| quiet_discovery — Điều nước giữ lại | Khám phá chậm, có khoảng nghỉ để người chơi quan sát |
| lam_trieu — Rừng nhớ tên | Dây gảy và hơi sáo tổng hợp, nhịp nhẹ |
| sa_hoa — Lò và cát | Gõ khô, sắc thái nóng, nhịp rõ |
| tran_son — Người qua cửa | Trầm chắc, bước tiến miền biên ải |
| bach_uyen — Thành dưới triều | Dải âm mềm và ngân ngắn, cảm giác chìm dưới nước |
| rift_finale — Năm dòng cùng chảy | Motif hội tụ, mở rộng hòa âm ở điểm cốt truyện |

Mỗi bài là đoạn loop 16 ô nhịp 4/4, có nốt/velocity/instrument/thời điểm trong score JSON; không phải bản soundtrack nhiều phút đã mastering. Minh Kiếm dùng kim loại khô; Ảnh Đao gió/lửa ngắn; Huyền Bút nước/pha lê; Thạch Chùy đá/trầm có trung âm; Linh Cung dây/gió/lá. Synthesis không khẳng định mô phỏng trung thực nhạc cụ dân tộc.

## 3. Nguồn và quyền sử dụng

Toàn bộ tín hiệu tạo từ oscillator, noise có seed, envelope, bộ lọc và score mới trong `Tools/AudioProduction/`. Không đọc audio mẫu bên ngoài, không dùng âm thanh từ KPAH/JAR, không clone giọng, không gắn nhãn sample bên thứ ba là original. `sourceLicense=original_procedural_synthesis_no_external_samples` mô tả nguồn tạo. Bộ file được tạo cho dự án để sửa, dựng và tích hợp vào game.

NumPy và python-soundfile/libsndfile là thư viện công cụ; giấy phép upstream vẫn áp dụng cho thư viện nếu phân phối chúng. Runtime game chỉ cần clip xuất ra, không cần kèm Python. Manifest lưu phiên bản môi trường, SHA nguồn và SHA từng runtime/master. `sourceGitBase` là commit nền trước khi viết renderer; các hash nguồn kèm theo mới xác định chính xác mã tạo lần bàn giao này.

## 4. Hợp đồng tích hợp cho Muse/client

1. Muse import và nghe trên Unity VM bằng một scene audition riêng; chưa gắn cả pack vào scene sản phẩm. `.meta` có GUID ổn định, loadType đề xuất streaming cho loop và giải nén khi nạp cho one-shot; đây là thiết lập tĩnh **chưa được Unity xác nhận**. Không đổi GUID tùy tiện. WAV đã mono, OGG stereo. Thử target build vì engine có thể transcode nguồn.
2. Client tạo lookup cueKey → các clip theo manifest audio riêng. Không trộn vào manifest sprite. Cache/pool có giới hạn, không preload 541 clip cùng lúc, không đưa master/MP3 preview vào build.
3. Chỉ nối skill/hit/hurt/boss/trade/forge theo event hoặc state được server xác nhận; packet yêu cầu và cast animation không chứng minh hit. Guard cast không phát parry; heal không phát hurt; đặt bẫy không phát trap hit; fail forge không phát success.
4. Kiếm Trận SK-MK-03: v01/v02/v03 lần lượt nhẹ/vừa/nặng theo hitIndex 0/1/2; mỗi clip chỉ một phần nhát đánh. Liên Châu phát theo từng projectile xác nhận. Các cue khác chọn không lặp ngay, seed presentation tách RNG gameplay.
5. Dedupe `(mapInstanceId,eventId,cueKey,hitIndex)`; kiểm visibility/audience và map instance trước khi phát. Reconnect chỉ khôi phục loop đang sống; không phát lại one-shot lịch sử. Phá actor/đổi map/cancel phải dừng loop và giải phóng voice.
6. Dùng voiceCaps/gain/minGapMs/priority/warningDucking của manifest. Nhạc tối đa hai voice để crossfade; tổng ambience tối đa bốn lớp. Cảnh báo boss dùng ngân sách skill ưu tiên cao, không vượt mute. Khoảng cách/pan trên XY, không worldZ. HUB_WIDE không tự tăng bán kính nghe.
7. Map binding ngoài vùng chính là fallback thiết kế chờ review; mode PvP, encounter, vùng an toàn và cinema có quyền ưu tiên. Không tự bật nhạc boss chỉ vì vào map chưa có profile riêng. Cinema stinger chưa picture-lock; giữ revealTier để tránh lộ nút thắt sớm.
8. NPC service open/close không phải thoại NPC. Không đóng việc voice acting bằng cue giao diện. Muse tiếp tục giao voice/subtitle/stem cinema theo kịch bản final và sidecar riêng khi có nguồn phù hợp.

## 5. Kiểm tra đã làm và cổng nghiệm thu còn lại

Local giải mã đủ 541 runtime clip, xác nhận frame/sample rate/channel/format, hash master/runtime/source, 63 cue gốc, binding, đường dẫn và GUID. Không có lỗi. Peak giải mã cao nhất 0,5; DC offset cao nhất khoảng 0,0000367; tỉ số bước nhảy seam / percentile 99,5 của bước nhảy nội bộ cao nhất 1,24219. Đây là **sample peak, RMS và kiểm seam**, chưa phải đo LUFS, true peak hoặc xác nhận không nghe tiếng nối. Không giả gọi mức RMS là loudness chuẩn phát hành.

8 bài kiểm validator bao gồm file hỏng/hash sai, clipping, im lặng, LFS pointer, traversal, CRLF source, WAV thật và OGG stereo dài với codec ghi theo chunk để tránh crash stack trên Windows. CI giải mã lại media đã checkout LFS; chỉ PASS kỹ thuật mới cho phép bàn giao ứng viên, không tự duyệt nghệ thuật.

Trước bật trong bản chơi cần báo cáo của Muse/client ghi Unity version, build/device, mixer settings và clip quay: mono/stereo/tai nghe/loa nhỏ; mute từng bus/master; 10 người spam skill vẫn nghe warning; đổi map và reconnect không sót loop/nhân tiếng; kiểm guard/trap/heal đúng ngữ nghĩa; profiler voice count/memory; nghe seam qua nhiều vòng; nghe nhạc khám phá 60–120s không gây mệt. Cân lại mức gain theo cảnh chơi thật và người dùng. Nghiệm thu này chưa thực hiện trong lần render.

Không đánh dấu toàn bộ CX-04 hoàn tất chỉ vì đã có asset. Phần đã xong: tạo nguồn, master, runtime, preview, manifest và kiểm kỹ thuật. Phần còn lại: nghe duyệt, import/mix, adapter runtime, QA thiết bị; thoại và cinema final là luồng riêng.
