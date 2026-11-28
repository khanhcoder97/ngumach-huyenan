# Asset 20261113c — Tầm Long, Kiếm Trận và Thiết Y

Bổ sung **20 sheet chọn / 320 khung nguồn**: ba động tác Minh Kiếm × năm hướng ×16 khung, cùng năm component VFX ×16. Giữ nhân vật chibi nguyên khối từ Motion16 đã chốt. Ảnh sinh/sửa bằng image_gen tích hợp, PNG và prompt thực lưu trong thư viện; runtime sao chép nguyên byte. Không dùng paper-doll hoặc lặp tám ảnh để đủ số khung.

## Bộ động tác

Mỗi động tác có N/NE/E/SE/S vẽ nguồn; SW/W/NW lật từ SE/E/NE theo policy. Không gọi ba hướng lật là ba góc vẽ mới.

| ID | Hành động | Phân bổ 16 khung | Thời lượng xem |
|---|---|---|---:|
| skill_02 / Tầm Long | Lấy đà chân sau, đưa kiếm ra trước, đâm/lướt, hãm và thu thế | 0–3 chuẩn bị;4–9 lướt;10–15 hồi | 0,59s |
| skill_03 / Kiếm Trận | Chém ngang → chéo lên → từ trên bổ xuống → thu thế | Bốn khung cho mỗi nhát, bốn khung hồi | 0,60s |
| skill_04 / Thiết Y | Cắm kiếm cạnh giày, nhún vai/gối, kéo kiếm về và đưa bàn tay còn lại qua trước ngực | Bốn nhóm bốn khung | 0,80s |

Giữ búi tóc đen cài vàng, áo giao lĩnh ngà, áo khoác ngắn xanh trầm viền vàng, giáp vai, quần tối và giày nâu. Một tay nắm chuôi của một thanh kiếm; tay còn lại giữ thăng bằng hoặc làm động tác hộ thể. Góc sau để thân che phần vũ khí/bàn tay ở phía trước; không vẽ lưỡi kiếm xuyên lưng. Tầm Long N v1 có mũi kiếm lệch Đông Bắc, được giữ lịch sử; bản N v2 đã sửa trục hướng Bắc.

Các sheet là động tác tại chỗ. Di chuyển root trong thế giới, dừng ở chướng ngại, mục tiêu và sát thương vẫn cần gameplay thực thi theo hợp đồng. Chưa nghiệm thu mọi chuyển tiếp idle/đổi trang bị hoặc toàn nhân vật.

## Timing từng khung

sourceFrameDurationsMs là metadata tùy chọn, được xuất và pin cùng binding:

- Tầm Long: 4×37,5ms →0,15s lấy đà;6×33,333…ms →0,20s lướt;6×40ms →0,24s hồi. Tổng0,59s theo đặc tả.
- Kiếm Trận: 4×25ms,4×30ms,4×35ms →ba nhịp0,10/0,12/0,14s. Thêm4×60ms hồi là giả định trình bày0,24s; tổng0,60s không phải một cửa hit kéo dài.
- Thiết Y: 16×50ms →0,80s trình bày. Khiên tồn tại4s theo thiết kế độc lập, không suy từ độ dài clip.

Inspector từ chối sai số lượng, boolean, số không hữu hạn, khung ngắn hơn1000/60ms, quá dài hoặc tổng lệch với profile component. Thiết kế này dành cho nguồn16 khung hiện hành. Trang không có timing tùy chọn giữ cách phát cũ.

Actor Library và Studio cùng đọc timing nguồn. Seek dùng thời điểm tích lũy của khung; phát tiếp giữ đúng pose. Hướng lật giữ cùng lịch khung. JSON/bundle bảo toàn DurationsMs; chỉnh trong Studio vẫn tạo bản cần kiểm riêng. Mỗi pose có đủ thời gian để xuất hiện ở đồng hồ60 bước/s, không tạo thêm pose bằng nội suy.

Video offline cập nhật số khung sau khi sprite con đã sample, ở cùng tick render; không dùng nhịp readout0,1s của xem thời gian thực. Ảnh tĩnh đại diện lấy gần giữa chu kỳ, dải mẫu là mẫu thời gian, chưa bảo đảm từng ô tương ứng đúng một source frame.

## Neo giày, không neo mũi kiếm

Đòn hướng Nam có thể đặt mũi kiếm thấp hơn giày. BOOT_CORE_FOOT nhận cụm màu giày/quần nâu ở phần dưới ô, bỏ thép bạc/chuôi vàng và đảo pixel nhỏ. Chỉ áp dụng palette Minh Kiếm được khai báo rõ, không tự gán cho lớp khác.

Nguồn giữ điểm neo theo giày, cộng khoảng đế2px cố định. Chiều cao đứng lấy từ pose trung tính số0, từ đỉnh hình đến giày và cố định suốt clip. body_registration_20261113c.json ghi số đo/source SHA/method; metadata không kéo giãn bitmap hoặc thay collider. Mode này bắt buộc có chiều cao chuẩn tường minh.

SOLID_CORE_GUTTER cắt ở khoảng trống lõi alpha của các ô, giữ mũi kiếm mảnh thay vì đặt mép cắt theo trung điểm phép chiếu thô. Kiểm ô tràn, rỗng và pixel lặp vẫn giữ. PNG không bị cắt lại, resize hoặc vẽ đè.

## VFX tách rời

| Component | Hình ảnh / nhịp xem | Giới hạn tích hợp |
|---|---|---|
| sk_mk_02_trail_component | Vệt trắng bạc lõi vàng, hướng nguồn Đông;0,32s |0,20s chuyển động +0,12s đuôi tan; không kéo dài quãng lướt |
| sk_mk_02_stop_dust_component | Hai cuộn bụi đất thấp và hạt tan;0,32s | Phát ở điểm dừng thật; neo tâm ô với offsetY64px nguồn |
| sk_mk_04_gain_component | Ánh kim xanh bạc dạng vành hở, lòng trong suốt;0,40s | Dấu thi triển, không phải bong bóng che toàn thân |
| sk_mk_04_break_component | Vành đã đủ cỡ nứt rồi tách mảnh;0,32s | Dùng khi khiên thực sự bị phá; v2 thay bản v1 có nhịp mọc lại |
| sk_mk_04_expire_component | Các mảnh sáng nhỏ tan nhẹ, không nổ;0,40s | Dùng khi hết hạn tự nhiên |

Tất cả4×4 /16 nguồn, one-shot giữ cuối khi xem trong Studio. Các khung cuối còn ít pixel để kiểm nguồn; controller gameplay phải gỡ hiệu ứng khi hết thời lượng, không giữ mãi mảnh cuối.

Kiếm Trận tái sử dụng sk_mk_03_arc_component đã kiểm ở đợt trước, bố trí ba cung theo thiết kế. Không tính thành ảnh mới. Đợt này chưa ghép hoàn chỉnh body +ba cung hoặc gắn gain/break/expire với sự kiện khiên thật. Viền HP, crack theo lượng khiên, damage/MP/CD/Kiếm Ý, khoảng lướt5,5m và collision vẫn theo hệ thống riêng.

Có thể mở/chèn component để chỉnh tay bằng Studio. Chèn mặc định trải theo timeline host, chưa tự giữ nhịp riêng hoặc gắn event. Không tự cấp approval cho project chỉnh tay.

## Mở xem

~~~powershell
./ClientGodot/Run_Actor_Library.ps1 -SkipBuild -Actor CLASS_MINH_KIEM -Clip skill_02
./ClientGodot/Run_Actor_Library.ps1 -SkipBuild -Actor CLASS_MINH_KIEM -Clip skill_03
./ClientGodot/Run_Actor_Library.ps1 -SkipBuild -Actor CLASS_MINH_KIEM -Clip skill_04
./ClientGodot/Run_Art_Studio.ps1 -SkipBuild -Entry actor:CLASS_MINH_KIEM:skill_02 -Direction S -Play
./ClientGodot/Run_Art_Studio.ps1 -SkipBuild -Entry class_minh_kiem_skill_03_n -Play
./ClientGodot/Run_Art_Studio.ps1 -SkipBuild -Entry sk_mk_04_break_component -Play
~~~

Checkout mới bỏ -SkipBuild để build/import. PNG chưa import hoặc mất tài nguyên được báo rõ, không lưu texture null vào cache. Studio giữ chỉnh pivot/tọa độ/layer/socket/timing, undo/redo, JSON và bundle.

## Bằng chứng và phần tiếp tục

44 Python tests; .NET8 build0 warning/error, Godot import; native library14.424 assertions, Studio70.890 assertions/238 entries. Kiểm tám hướng,16 nguồn, clock60 bước, raw/group timing, mốc pha, seek/resume, loop/one-shot, JSON và chèn component.46 PNG baseline nguyên SHA256,178 runtime sources khớp byte.

Có10 MP4 native chọn, ảnh/dải mẫu/log/pin/decode audit. Ba video trước sửa readout ở thư mục lịch sử. Mỗi MP4180 bước/3s xuất offline60 bước/s, không chứng nhận gameplay đạt60FPS.

Catalogue181 page structure;62/1008 job đủ góc nguồn;26 job đủ góc đã kiểm source; còn946 job thiếu.21 HOLD cũ và full VFX atlas sai hàng vẫn giữ. Minh Kiếm10/12 clip đủ dữ liệu xem, còn skill_05/06; điều này không nghiệm thu toàn class hoặc các nguồn cũ còn HOLD.

Nguồn/prompt ở Art_Source/Actor_Library_20261107/Sheets và Prompts; bản chọn ở generation_records.json, bản sửa cũ ở generation_history.json. Inventory batch_20261113c.json; evidence Implementation/Reports/Evidence/Actor_Batch_20261113c/. Công cụ review_actor_batch_20261113c.ps1 ghi lại video trên máy này.

Tiếp tục các kỹ năng còn thiếu, class/quái/boss/NPC, VFX hoàn chỉnh và phần môi trường/UI/icon/audio/biến thể. Các source mới chưa tự thay renderer gameplay hoặc nghiệm thu LowFX/AI/collision/PCK. Mục tiêu toàn thư viện vẫn đang thực hiện.
