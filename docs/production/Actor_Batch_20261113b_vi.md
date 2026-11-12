# Thư viện asset — đợt 20261113b: Chồi Đất

Đợt này bổ sung **18 sheet chọn / 288 ô nguồn** theo sprite chibi nguyên khối đã chốt: 15 sheet động tác Rễ Nước và ba component VFX. Mỗi hướng/action hoặc component có 16 khung nguồn. Ảnh và lần sửa tạo bằng image_gen tích hợp, PNG nguồn và prompt thực giữ trong thư viện; runtime sao chép nguyên byte. Không quay lại paper-doll hoặc nhân đôi tám pose để đủ số lượng.

## Ba pha của Rễ Nước

| Pha | Chuyển động nguồn | Hướng vẽ | Nhịp xem |
|---|---|---|---|
| telegraph_02 | Đứng sẵn sàng → bó rễ bám đất → thân ép thấp/rộng, chạc rễ cuộn lại | N/NE/E/SE/S ×16 | 0,70s |
| attack_02 | Bắt đầu thấp → ép rễ xuống → một nhịp truyền lực/bật thân → trở về thấp | N/NE/E/SE/S ×16 | 0,40s |
| recovery_02 | Bắt đầu thấp → rễ nhả lực → thân và chạc rễ mở dần → idle đứng | N/NE/E/SE/S ×16 | 0,60s |

Giữ gỗ nâu ướt, rêu, lá xanh lam, chạc cuộn và hạt xanh trước thân. Hạt khuất ở N/NE, lộ mép ở E và hiện theo góc trước SE/S. Không thêm tay/chân người hoặc bake chồi đất vào thân. SW/W/NW lật từ SE/E/NE theo policy, không tính thành góc vẽ mới. Ba pha là one-shot giữ cuối trong Studio; Actor Library cho phát lặp để soi pose.

Nguồn thiết kế: Art_Entity_Weather_UI_Visual_Bible_vi.md, hàng MOB_WATERROOT. Chồi đất có sát thương 1,5×, đường 4m và báo 0,70s. **0,40s đánh / 0,60s hồi ở đây là giả định trình bày**, không tự thay cửa sổ damage, thời gian AI hoặc server. Không suy chiều rộng hitbox từ viền hình.

Attack S v1 bắt đầu quá cao sau windup thấp, được giữ trong lịch sử; v2 sửa đầu clip và là bản chọn. Cảnh báo đường v2 là phương án không chọn; v1 giữ ở runtime sau kiểm trong suốt/native. Không ghi đè PNG gốc.

## Chiều cao cho clip bắt đầu thấp

FOOT theo từng khung giữ điểm tiếp đất; không dùng lõi rêu để khóa thân đang oằn. Chiều cao chuẩn cố định cho toàn clip:

- Windup lấy trung vị chiều cao nguồn 0–2 ở tư thế đứng.
- Recovery lấy trung vị 13–15 sau khi trở lại đứng.
- Attack dùng một hệ số cố định, giải bình phương tối thiểu để giảm chênh chiều cao ở cả hai điểm nối với windup/recovery.

Không có scale theo khung hoặc chỉnh pixel. Công cụ đọc nguồn ghi body_registration_20261113b.json; generation_records.json lưu bodyReferenceHeight. Inspector hỗ trợ chiều cao đứng tường minh cho actor HEIGHT, từ chối số không hữu hạn, boolean, vượt ô, VFX hoặc LONGEST_AXIS. Nguồn cũ không khai báo giữ cách tính cũ; pin MOSS cũ được bảo toàn.

Ở cỡ 88px, hai điểm nối còn chênh chiều cao khoảng 1,82–6,54px, lớn nhất tại NE. Đây chưa phải nối silhouette hoàn hảo; cần tinh chỉnh tiếp trong camera và chuyển trạng thái gameplay thực. Duyệt source/clip không phải nghiệm thu toàn encounter.

## Ba component VFX

| ID | Nội dung | Neo / nhịp xem |
|---|---|---|
| sk_mob_waterroot_02_line_component | Viền cảnh báo đỏ/cam dạng đường có đầu chỉ hướng; lòng rỗng để đọc địa hình | CELL_CENTER; 0,70s, một lần |
| sk_mob_waterroot_02_spike_component | Ba chồi rễ gỗ móc trồi từ khe nhỏ, vân xanh, chút rêu/lá; ổn định ở đỉnh | FOOT; 0,40s, một lần |
| sk_mob_waterroot_02_retract_component | Chồi cùng kiểu cuộn và rút xuống khe nhỏ, không mọc lại | FOOT; 0,60s, một lần |

Mỗi component có 4×4 / 16 nguồn riêng, chưa là full skill. Grid được xem và khai báo tường minh; inspector vẫn kiểm ô rỗng, tràn mép và pixel lặp. Studio giữ texture, vùng cắt, pivot, thứ tự và profile. Có thể dùng -Component để chèn rồi chỉnh layer/timing/alpha/vị trí. Bản chèn mặc định trải theo timeline host, chưa phải timeline ghép đúng kỹ năng.

Đường báo chỉ ghép trong cảnh review ở telegraph_02, xoay tám hướng và tắt khi qua attack/recovery/idle. Đây là minh họa theo pixel cửa sổ, chưa đổi 4m ra world units. Spike/retract được kiểm độc lập; chưa tự rải dọc hit lane hoặc gắn event combat.

## Màn kiểm và Studio

Combat review thêm -CombatVariant 2 riêng cho MOB_WATERROOT; biến thể 1 giữ chức năng cũ, tham số sai bị từ chối. Biến thể 2 dùng bốn ô lớn báo/đánh/hồi/chuỗi. Vị trí thân chừa khoảng theo hướng để cảnh báo Bắc không bị che hết. Cue nằm dưới actor; không phải overlay hitbox trên thân.

Studio --studio-play chờ căn bố cục hai tick rồi mới phát để giữ pose đầu trong khung đã fit. Dải mẫu component bắt đầu sau ba tick; video gốc vẫn gồm thời điểm dựng bố cục. Các ô mẫu thời gian chưa chứng minh từng ô ứng một source frame.

~~~powershell
./ClientGodot/Run_Actor_Library.ps1 -SkipBuild -Actor MOB_WATERROOT -Clip attack_02
./ClientGodot/Run_Actor_Library.ps1 -SkipBuild -CombatReview -Actor MOB_WATERROOT -CombatVariant 2 -Direction N
./ClientGodot/Run_Actor_Library.ps1 -SkipBuild -CombatReview -Actor MOB_WATERROOT -CombatVariant 2 -Test
./ClientGodot/Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_WATERROOT:recovery_02 -Direction SE -Play
./ClientGodot/Run_Art_Studio.ps1 -SkipBuild -Entry sk_mob_waterroot_02_spike_component -Play
~~~

Checkout mới bỏ -SkipBuild để build/import. Undo/redo, pivot/tọa độ/layer/socket/timing, JSON và bundle giữ nguyên. Bản chỉnh tay không thừa hưởng approval của nguồn.

## Kiểm tra và phần còn lại

- .NET8 build 0 warning/error; Godot import. 37 Python tests; native library 13.599 assertions; Studio 67.078 assertions / 215 entries; cue biến thể 1: 12, biến thể 2: 20.
- Pin PNG SHA256 và binding cho 18 nguồn, giới hạn source/clip hoặc component. 46 PNG baseline nguyên SHA256; 158 runtime sources chọn khớp byte.
- Tám MP4 native chọn: ba clip tám hướng, chuỗi N/E, ba component trong Studio; có ảnh, dải mẫu, log, decode/hash audit. Hai video bố cục combat cũ và ba video Studio trước sửa startup giữ trong thư mục lịch sử.
- Mỗi video 180 bước / 3s tại 60 bước/s offline. Đây không chứng nhận gameplay đạt 60FPS hoặc chạy ổn định khi đông người/quái.
- Catalogue: 161 page qua cấu trúc; 59/1008 job đủ góc nguồn; 23 job đủ nguồn đã kiểm source; còn 949 job thiếu. 21 HOLD cũ và atlas full VFX sai hàng vẫn giữ. Component không đóng job full skill.

Rễ Nước có 12/12 action đủ nguồn và kiểm source; chưa nghiệm thu AI, tốc độ, collision, LowFX, renderer gameplay hoặc PCK. Catalogue actor/skill chưa bao phủ hết map/UI/icon/audio/biến thể. Mục tiêu toàn thư viện game vẫn tiếp tục.

Nguồn/prompt: Art_Source/Actor_Library_20261107/Sheets và Prompts; lựa chọn ở generation_records.json, bản cũ ở generation_history.json. Inventory batch_20261113b.json. Evidence Implementation/Reports/Evidence/Actor_Batch_20261113b gồm visual_decisions.json, sprite_integrity.json, offline_media_integrity.json và log. Công cụ review_actor_batch_20261113b.ps1 ghi video native; --fixed-fps là xuất offline.
