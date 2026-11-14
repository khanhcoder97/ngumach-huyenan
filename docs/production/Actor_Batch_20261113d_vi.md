# Asset 20261113d — Bạch Hồng và Vạn Tượng Quy Nhất

Trạng thái: đã duyệt13 nguồn/clip/component sau kiểm native; chưa nghiệm thu toàn class hoặc gameplay. Giữ sprite chibi nguyên khối đã chốt, không paperdoll.

Phạm vi đợt: hai động tác × N/NE/E/SE/S ×16 khung nguồn; ba hướng lật khai báo riêng. Thêm component vệt Bạch Hồng, nét tụ lực và đường kiếm Vạn Tượng, mỗi nguồn16 khung. PNG và prompt thực được lưu trước khi chọn đăng ký.

Timing body dùng để xem/biên tập, không thay server: Bạch Hồng0,48s =0,08 chuẩn bị/0,16 né/0,24 hồi (giả định trình bày). Vạn Tượng1,55s =0,70 tụ lực/0,35 phát/0,50 hồi;0,50 hồi là giả định trình bày. Giữ luật thiết kế xóa Chậm, không xuyên chướng ngại, Bạch Hồng không damage; tuyệt kỹ tiêu Kiếm Ý khi server chấp nhận.

Vệt Bạch Hồng theo thiết kế hiện0,16s; preview16 nguồn ở0,32s chỉ là nhịp editor để kiểm đủ pose. Khi chạy0,16s tại60Hz một số source pose sẽ được lấy mẫu bỏ qua, không kéo dài cửa né chỉ để xem đủ ảnh. Mốc0,16s vệt không phải quyền i-frame.

13 nguồn chọn đăng ký ở generation_records.json, pin PNG SHA/binding ở visual_review.json và visual_decisions.json. Skill01–04 đợt trước không đổi.

## Đăng ký và kích thước xem

BOOT_CORE_FOOT và chiều cao trung tính frame0 cố định trên mười sheet body. Trail/cut dùng tâm ô; charge dùng SYMMETRIC_BOUNDS_CENTER theo hình hội tụ đã kiểm; trail/cut khai báo LONGEST_AXIS để kích thước xem đo theo span dài nhất trên toàn16 ô, không phóng một đường mảnh thành thanh quá lớn. Các nguồn VFX HEIGHT cũ giữ nguyên binding. Đây là kích thước editor, không phải tầm7m hoặc rộng0,8m của hitbox.

Inspector đếm chiếu alpha nhị phân bằng histogram Pillow tương đương vòng pixel cũ, không thay ảnh/threshold/tọa độ. Kiểm tương đương mask rỗng/đặc/mỏng/alpha quanh ngưỡng199–200 và kiểm lại binding cũ.

## Nguồn và lịch sử chọn

Bạch Hồng: class_minh_kiem_skill_05_{n,ne,e,se,s}; Vạn Tượng: class_minh_kiem_skill_06_{n,ne,e,se,s}. Mỗi ID có16 nguồn thật, ba góc SW/W/NW dùng mirror của SE/E/NE theo policy. Không gọi mirror là góc vẽ riêng. Giữ búi tóc đen cài vàng, giao lĩnh ngà, khoác xanh trầm viền vàng, giáp vai và giày nâu từ Motion16. Không đưa paperdoll trở lại.

Vạn Tượng E v1 đọc thành đâm thẳng nên chọn v2 đổi góc kiếm/cổ tay qua nhịp chém. NE v1 mở ngực như góc Đông; v2 giữ lưng áo chiếm mặt thân chính suốt clip. SE v1 có bàn tay dư sau silhouette ở pha phát; v2 bỏ tay dư. Cả ba bản cũ giữ PNG/prompt trong lịch sử, không được pin approval của bản chọn.

## VFX độc lập

| Component | Nội dung | Nhịp xem |
|---|---|---:|
| sk_mk_05_trail_component | Vệt trắng xanh mảnh hướng nguồn Đông, fray rồi tan |0,32s |
| sk_mk_06_charge_component | Nét kim loại bạc hội vào điểm sáng, cuối giữ kết tụ |0,70s |
| sk_mk_06_cut_component | Đường kiếm trắng vàng phân lớp, vỡ thành nét nhỏ rồi tan |0,35s |

Trail/cut giữ tâm ô; charge neo tâm bounds đối xứng để bỏ lệch tâm giữa các ô nguồn, không bake vào body/target. Các nguồn đều one-shot; khi xem giữ khung cuối có ít pixel. Controller phải gỡ component ở mốc hết hiệu ứng; charge phải gỡ khi chuyển pha. Thiết kế7m/0,8m là vùng server, không suy từ bounds PNG hoặc kích thước editor. Chưa nghiệm thu ghép body+charge+release, MP/CD/Kiếm Ý, xóa Chậm, dash collision, LowFX hoặc PCK.

Bạch Hồng body0–3 chuẩn bị20ms/khung,4–9 né26,666…ms/khung,10–15 hồi40ms/khung. Tuyệt kỹ0–5 tụ lực116,666…ms,6–9 phát87,5ms,10–15 hồi83,333…ms. Mỗi body có16 pose đủ thời lượng xuất hiện với sampler60 bước/s. Vệt0,16s gameplay là trường hợp riêng đã nêu; không mở rộng thời gian né để chạy đủ nguồn.

## Mở xem và chỉnh tay

~~~powershell
./ClientGodot/Run_Actor_Library.ps1 -SkipBuild -Actor CLASS_MINH_KIEM -Clip skill_05
./ClientGodot/Run_Actor_Library.ps1 -SkipBuild -Actor CLASS_MINH_KIEM -Clip skill_06
./ClientGodot/Run_Art_Studio.ps1 -SkipBuild -Entry actor:CLASS_MINH_KIEM:skill_06 -Direction NE -Play
./ClientGodot/Run_Art_Studio.ps1 -SkipBuild -Entry sk_mk_06_cut_component -Play
~~~

Checkout mới bỏ -SkipBuild để build/import. Studio giữ pivot/tọa độ/layer/socket/timing, undo/redo và JSON/bundle. Chèn component vẫn trải nguồn trên timeline host để chỉnh tay; chưa tự giữ duration riêng hoặc bind event gameplay.

## Kiểm tra và giới hạn bàn giao

52 Python tests; .NET8 build0 warning/error; Godot import; library15.008 assertions và Studio73.426/253 entries. Phase timing, seek/resume, sampler60 bước, one-shot/mirror, raw/group timing, JSON/bundle và component được kiểm. Duyệt source không chứng nhận mọi chuyển tiếp idle/đổi trang bị, đồng bộ server hoặc một class hoàn chỉnh.

46 PNG baseline nguyên SHA256;191 runtime copies khớp byte nguồn.181 source/binding của đợt trước không đổi sau cách đếm alpha mới. Có7 MP4 native chọn và1 video tụ lực trước sửa điểm neo giữ trong Superseded_Charge_Registration; mọi MP4 giải mã/hash audit. Mỗi video180 bước/3s offline60 bước/s, không chứng nhận FPS gameplay. Dải mẫu là mẫu thời gian, không đại diện chính xác một source frame cho mỗi ô. Nguồn16 ô được kiểm riêng.

Tụ lực lúc đầu lệch tâm giữa các ô; SYMMETRIC_BOUNDS_CENTER chỉ bật cho nguồn đối xứng đã xem, không áp vào bụi lệch hoặc projectile di chuyển. Bản source vẫn nguyên byte; thay đổi metadata được ghi ở charge_registration_change.json, video trước sửa nằm trong thư mục lịch sử.

Nguồn/prompt: Art_Source/Actor_Library_20261107/Sheets và Prompts. Sinh/sửa bằng image_gen tích hợp; không dùng CLI/API hoặc vẽ bitmap bằng code. Cả ba bản nguồn bị thay giữ history; inventory batch_20261113d.json; evidence Implementation/Reports/Evidence/Actor_Batch_20261113d/.

## Coverage sau duyệt

Catalogue194 page structure;64/1008 job đủ góc nguồn,28 job đủ góc đã kiểm source, còn944 job thiếu.21 HOLD cũ và full VFX Kiếm Trận sai hàng vẫn giữ. Minh Kiếm12/12 clip đủ dữ liệu, sáu body skill có nguồn xem; điều này không duyệt các clip cũ còn HOLD hoặc cả nhân vật. Component không tự đóng full_timeline của kỹ năng.

Tiếp tục class/quái/boss/NPC, ghép VFX và chuyển tiếp, môi trường/map/UI/icon/audio/biến thể. Full art/gameplay chưa hoàn thành.
