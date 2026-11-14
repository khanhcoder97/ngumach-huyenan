# Thư viện asset — đợt 20261112e

Tiếp tục thư viện toàn game theo sprite chibi nguyên khối đã chốt. Đợt này có **16 sheet được chọn / 256 ô nguồn mới**: 15 sheet roi rễ và một component vòng gợn. Dùng `image_gen` tích hợp; giữ nguyên byte PNG nguồn và prompt thực, không vẽ bitmap bằng code, không lặp pose để bù 16 khung.

## Bộ roi rễ của MOB_WATERROOT

| Action | Nguồn vẽ | Nội dung | Nhịp review |
|---|---:|---|---:|
| telegraph_01 | N/NE/E/SE/S × 16 | Hạ thân, cuộn một nhánh rễ, giữ thế lấy đà; chưa đánh | 0,70 s |
| attack_01 | N/NE/E/SE/S × 16 | Nhánh rễ mở cuộn, quật theo hướng nhìn, giữ đà ở cuối | 0,35 s |
| recovery_01 | N/NE/E/SE/S × 16 | Thu ngọn rễ đã duỗi, trở về thế nghỉ | 0,55 s |

Tổng **240 ô vẽ thật** cho ba action. SW/W/NW tham chiếu ảnh lật SE/E/NE theo policy của quái, thành tám hướng xem; không tính thêm thành ảnh nguồn mới. Giữ khối rễ gỗ ướt, hai chạc cuộn trên đỉnh, rêu, lá xanh lam và hạt sáng phía trước. N/NE che hạt; E chỉ lộ ở mép trước; SE/S lộ hạt theo mặt trước. Không thêm mặt người hoặc tay/chân người.

Nhịp 0,70 s lấy từ mô tả cue của Rễ Nước trong visual bible. **0,35 s đánh và 0,55 s hồi là giả định trình bày có thể chỉnh**, không phải cửa sổ hit, cooldown hay quyền gây damage. Chuỗi xem thử nối ba pha rồi giữ idle 0,75 s. Năm sheet idle đã có được kiểm lại với đăng ký điểm neo mới, không tính thành ảnh mới.

## Neo thân và giữ tỷ lệ

Ngọn roi đổi độ dài không được dùng để định nghĩa bàn chân hoặc chiều cao của cả thân. `pivotMode=MOSS_CORE_ROOT` đọc lõi rêu/lá từ pixel alpha ≥200, G≥60, G>1,05R và G≥0,9B, rồi cộng offset chân của thế idle cùng hướng. Không sửa raster.

`bodyReferenceHeight` đo từ ba khung trung tính: đầu clip cho idle/báo/đánh, cuối clip cho recovery vì đầu recovery còn roi duỗi. Chiều cao này cố định trong clip. Cả bốn action dùng **chung offset chân idle theo từng góc**, tránh tự căn lại vị trí ở mỗi pha. Dữ liệu và phương pháp nằm trong `body_registration_20261112e.json`; có tool đọc nguồn để tái tạo đăng ký.

Trước khi dùng chung offset, độ chênh điểm lõi suy ra từ metadata ở kích thước review 88px lên tới 18,53px theo X ở NE và 6,53px theo Y. Sau đổi, điểm đăng ký lõi giữa các clip cùng hướng trùng nhau theo metadata. Đây là số đo đăng ký, **không chứng minh giải phẫu, bàn chân thật hoặc silhouette đã khớp tuyệt đối**; các chuỗi native được xem riêng. Việc nối đầy đủ với AI/địa hình vẫn chưa nghiệm thu.

Một ngọn roi N mảnh vượt ngoài vùng projection chính. Page này dùng `SOLID_CORE_GUTTER`: chọn đường cắt trong dải rộng ít nhất 4px không có pixel lõi alpha ≥200. Vẫn kiểm mép lõi tối thiểu 2px để giữ ngọn roi và viền; không nới kiểm tra để chấp nhận ảnh bị cắt. Đây không phải kiểm chứng rằng mọi pixel alpha thấp trong gutter đều bằng 0. Không ghép atlas hoặc vẽ lại ngọn roi bằng code.

## VFX vòng gợn báo lấy đà

`sk_mob_waterroot_01_ripple_component` là **16 khung nguồn OMNI** riêng. Vòng đỏ/cam có dấu rễ nhọn, tâm rỗng, mở rộng trong 0,70 s; cuối chuỗi vẫn rõ. Mẫu alpha tại tâm của cả 16 ô đều bằng 0; ảnh/video native xác nhận không có mảng nền cam che map. Bản tách nền v2 được chọn, các bản trước được giữ trong lịch sử.

Vòng chỉ **báo quái đang lấy đà**, không biểu diễn biên vùng sát thương. Không dùng bán kính của hình vòng làm hitbox roi 2,6m hoặc line chồi đất 4m. Các vùng hit thật phải theo hợp đồng combat riêng.

Component được ghép thử dưới chân quái ở ô nối ba pha trong cảnh review. Nó chỉ hiện khi `telegraph_01`, tắt từ đầu attack và không hiện trong recovery/idle. Có sáu kiểm tra tại ranh giới pha, kể cả khi chuỗi quay vòng. Đây là tích hợp **cảnh xem nguồn**, chưa phải tích hợp encounter/gameplay. Component không khép một job kỹ năng hoàn chỉnh trong catalogue.

## Mở xem và chỉnh tay

```powershell
.\ClientGodot\Run_Actor_Library.ps1 -SkipBuild -Actor MOB_WATERROOT -Clip attack_01
.\ClientGodot\Run_Actor_Library.ps1 -SkipBuild -CombatReview -Actor MOB_WATERROOT -Direction NE
.\ClientGodot\Run_Actor_Library.ps1 -SkipBuild -CombatReview -Test
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_WATERROOT:attack_01 -Direction E -Play
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_WATERROOT:recovery_01 -Direction S -Frame 15
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry sk_mob_waterroot_01_ripple_component -Play
```

Bỏ `-SkipBuild` để build/import trước khi mở trên checkout mới. Studio vẫn chỉnh pivot/tọa độ/layer/socket/timing/VFX và lưu JSON/bundle riêng, không ghi đè PNG gốc. Cảnh review giữ các ô hurt/death đang thiếu và ghi rõ thiếu; không lấy idle để giả làm action đó. Cảnh Cá Linh cũ vẫn mở qua `-CombatReview -Actor MOB_CARPLING`.

## Kiểm tra và phạm vi bàn giao

- 21 quyết định source/clip: 15 sheet roi rễ mới, 5 idle kiểm lại đăng ký và một VFX component. Pin SHA256 nguồn cùng binding SHA256; năm pin idle cũ được giữ ở `sourceApprovalHistory`.
- 46 PNG baseline chủ dự án chọn vẫn nguyên SHA256; 105 nguồn runtime được chọn khớp byte PNG gốc.
- .NET 8 build và Godot import đạt; 26 Python regression tests; native library 12.495 assertions; Studio 55.963 assertions / 153 entries; cue review 6 assertions; VFX Kiếm Trận cũ 14 assertions không đổi.
- 10 video native: bốn action ở tám hướng, năm chuỗi theo góc nguồn và một vòng gợn. Video xuất offline ở 60 bước/s, không chứng nhận game chạy 60 FPS thực. Dải ảnh là mẫu thời gian trích từ video, không thay thế sheet 16 khung gốc.

Catalogue actor/skill hiện có **108 page qua structure, 50/1008 job đủ góc nguồn, 14 job đủ góc được kiểm source**. Còn 958 job thiếu nguồn, 21 active HOLD và atlas VFX cũ sai số hàng. Ba job mới được khép về nguồn là ba pha roi rễ; idle đã có được kiểm lại, component không tính vào job full skill. Đây chưa tính hết khối lượng map/tile/UI/icon/audio.

Inventory: `Art_Source/Actor_Library_20261107/batch_20261112e.json`. Ảnh và prompt: `Sheets/`, `Prompts/` cùng thư viện. Bằng chứng: `Implementation/Reports/Evidence/Actor_Batch_20261112e/`, gồm video/ảnh native, pin quyết định, số đo đăng ký, kiểm hash và log.

Rễ Nước còn walk/run/turn, hurt/death và bộ đòn chồi đất; hai hướng walk Người Giữ Thuyền còn HOLD. Body/VFX các class, quái/boss/NPC còn lại và thư viện môi trường/UI vẫn phải tiếp tục. Chưa nghiệm thu toàn actor, AI, collision/hit, LowFX gameplay, thay renderer trong game hoặc PCK/shipping. Mục tiêu toàn thư viện vẫn đang thực hiện.
