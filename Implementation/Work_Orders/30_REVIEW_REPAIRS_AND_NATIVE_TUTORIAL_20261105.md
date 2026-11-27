# Gói 30 — sửa nghiệm thu, khép tutorial và tiếp tục MMORPG

Ngày 05/11/2026. Tiếp gói 29: OpenCode O1–O8, Qoder local Q1–Q8, Qoder remote R1–R8, Muse M1–M8. Mỗi người push checkpoint có mã nguồn hoặc media thật, sau đó tiếp phần độc lập; không dừng sau ACK hoặc một bản sửa.

Baseline tích hợp: f383233. Codex sở hữu Godot, đồ họa, UI/UX, VFX và tích hợp. Muse chỉ video, cinematic và âm thanh; Antigravity không nhận việc. Giữ production OFF. Không đổi model, tài khoản hoặc thông tin xác thực.

## OpenCode — hoàn vòng đời phiên và toàn bộ client

Nguồn đã review: c3c8a12. Đọc Implementation/Reports/Review_20261105/OpenCode_PR109_vi.md. 221 unit test PASS và hai sửa timeout/alpha ID được ghi nhận. Ba lỗi sau vẫn chặn việc nhận toàn bộ ClientSession:

1. ReturnFromDeathAsync phải liên kết token của phiên và kiểm epoch. Dispose giữa request phải hủy request; phản hồi muộn không được đổi receipt, HP hoặc khởi động world read mới. Giữ nguyên key của thao tác chưa rõ kết quả.
2. Closure trong dispatcher phải kiểm epoch, trạng thái disposed và subscription khi thực thi. Callback đã xếp hàng trước Dispose/relogin không được gọi consumer cũ.
3. Bỏ Thread.Sleep/spin wait trên UI thread. Dùng hủy không chặn và cleanup sau khi read kết thúc, hoặc shutdown bất đồng bộ được await. Kiểm bằng SynchronizationContext một luồng, queued dispatcher và transport không tuân cancellation.
4. Sau checkpoint sửa lỗi, tiếp API inventory v2/death-return, strict parser và negative fixtures; full tutorial/boss HTTP với hai owner; toàn bộ presenter; dịch vụ MMORPG; VFX theo geometry/cast/life/server tick; gói portable và regression. Runner chỉ qua P00-01 chưa chứng minh toàn tutorial.

Codex có thể tiêu thụ riêng bốn file Core đã review qua worker của mình. Việc đó không nghiệm thu lớp Composition còn lỗi và không chuyển quyền sửa Godot cho OpenCode.

## Qoder local — sửa lifetime/hộ tống, khép tutorial rồi tiếp backend

Nguồn đã review: cb4f475. Đọc Implementation/Reports/Review_20261105/Qoder_PR106_vi.md. Có 556 self-check và 17 kiểm tra death HTTP PASS; bài full alpha HTTP thất bại ở P00-04.

1. Giữ lifeVersion, death identity và receipt theo vòng đời nhân vật. Không xóa vì 256 nhân vật khác chết. Test churn ít nhất 300 nhân vật, reconnect và replay key cũ. Audit cả cache receipt của DeathReturn; chỉ dọn theo quy tắc hết hạn/persistence đã công bố.
2. Sửa đường P00-04 qua public HTTP và điều kiện sẵn sàng trong runner. Dùng healthState ALIVE, targetable và availability thực; state khác DEAD chưa đủ. Chứng minh movement → checkpoint → wave activation → owner kills → credit → completion, không private grant. Nguyên nhân chính xác của lượt thất bại vẫn cần truy ra; không giảm assertion để làm test xanh.
3. Đưa vị trí hộ tống từ domain ra world/read model theo owner. Client không tự suy đường cho Ly An. Giữ actor, instance, floor, life và attempt; hai owner không lẫn NPC, wave hoặc credit.
4. Giao packet hợp đồng bổ sung và route NPC TALK để P00-05 xác nhận nhập môn thật sau boss + fragment. Guard owner, map, khoảng cách, thứ tự quest và receipt/replay. Giữ enum event/kind đã đóng băng. Sau đó hoàn packet C1/portal; không hoàn thành nhiệm vụ qua client hoặc video callback.
5. Sửa nullable warning mới, gửi checkpoint Q1/Q2 rồi tiếp gói lớn: navigation và 349 anchor, năm lớp/30 kỹ năng, progression/economy, khám phá, social và vận hành/persistence. Bảng catalog/policy không được báo thành dịch vụ đã bật.

## Qoder remote — tiếp R1–R8

Chưa có checkpoint mới build được để nghiệm thu. Track đầy đủ csproj, lock, test fixture và workflow để clone/build/test thật. Sau đó tiếp transaction state + revision + receipt + ledger + outbox; fencing hai process; crash/replay; migration/backup và domain adapter. Life/death/return receipt cũng phải durable. Không nối Health trước review. Giao R1 sớm rồi tiếp phần độc lập, thay vì chỉ bổ sung báo cáo.

## Muse — sửa gói bàn giao và sản xuất media còn thiếu

Nguồn đã review: 3f34f0d. Đọc Implementation/Reports/Review_20261105/Muse_PR119.md. HOLD toàn PR hiện tại; timing, reel storyboard và TTS nháp là checkpoint, chưa hoàn M1–M8.

1. Sửa dialogueCues sai bằng 0 cho CIN001/002/004/006; đối chiếu số cue từ timing và SRT thực. Bổ sung validator bắt sai lệch giữa manifest.
2. Dùng quy tắc LF của Codex, tạo lại SHA rồi kiểm fresh checkout Windows/Linux. Chuyển đúng 22 binary raw sang LFS; OGV cũng thuộc LFS. Không bỏ qua kiểm hash.
3. Sửa cả năm lỗi hình: chuông chỉ xuất hiện qua phản chiếu; CIN001S06 đúng nhân vật; sừng gãy đọc rõ; CIN004S03 đúng góc; CIN002S02 dùng tay lành dừng trước mặt nước, không chạm nước và không crop đầu/mặt. Tạo từng keyframe 16:9 riêng; không dùng crop tự động từ collage làm khung final.
4. Bộ mẫu NPC và map Codex đã có tại PR118. Giữ nhận diện, quần áo, tay bị thương và đạo cụ qua các shot. Thiếu final character lock chỉ chặn shot liên quan. Không sửa game asset, UI, map, sprite, VFX hoặc Godot.
5. Chủ dự án/Codex duyệt 21 cửa sổ thoại hiện tại để sản xuất VO nháp. Đây chưa khóa hình hoặc mix cuối. CIN001S05 giữ 24.8–28.5s; CIN002 7–11s; CIN004 7.5–9.5s, Ly An nói ngoài khung; CIN006 12.5–17.5s. Không sửa câu canon hay tự tăng tốc giọng để ép vừa thời lượng.
6. Xuất riêng từng scene: MP4/OGV, poster, SRT, timing và hash. Reel 72 giây ghép CIN001/002/004 chỉ dùng review/gallery, không tự chạy làm opening vì tiết lộ nội dung về sau. Video không cấp thưởng hoặc hoàn thành quest.
7. Tiếp 17 VO nháp còn lại, các video campaign có chuyển động thực, bản P0 đã mix với stems/gain/ducking/loop QA, và nhạc/SFX được sáng tác hoặc chỉnh phối thực. Giữ provenance cho 541 file port từ pack Codex cũ; không tính chúng là audio mới. Báo riêng việc nghe thử, phát âm và native playback.
8. Viết lại mô tả PR/report theo số lượng video, VO và audio mới thực tế. Push checkpoint sửa lỗi rồi tiếp M3–M8; lặp đo hash không thay thế công việc sản xuất còn thiếu.

## Codex tiếp tục

Hoàn nhật ký năm nhiệm vụ, hội thoại theo trạng thái server, tracker động và hình gợn nước/cứu dân theo exact ID. Không cấp tiến độ giả khi backend còn thiếu. Giữ native P00-01 regression, phân biệt art gallery với gameplay đã chạy. Sửa launcher để việc chơi tay không ghi đè log kiểm thử đã lưu. Chỉ tích hợp phần nguồn đã review; các PR đang lỗi ở ngoài baseline.
