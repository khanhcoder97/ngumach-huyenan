# 20261114f — Huyền Bút: bốn động tác mới và hiệu ứng hỗ trợ

Tiếp tục **sprite chibi nguyên khối đã chốt**, giữ Studio chỉnh tay. Đợt này chọn **31 sheet / 496 tư thế nguồn**: 22 sheet thân và 9 component VFX, mỗi sheet 16 tư thế. Có 33 phiên bản sinh ảnh / 528 tư thế kể cả hai bản bị thay. Một ảnh hướng dẫn góc nhìn riêng không thuộc số tư thế bàn giao.

Sau xem ảnh gốc, đủ 16 pha native và bảng so tám hướng: **28 nguồn được duyệt riêng, 3 nguồn HOLD**. Đây là kiểm nguồn/clip; chưa nghiệm thu toàn class, kỹ năng ghép hoặc gameplay.

## Động tác và góc nhìn

| Nguồn thân | Nội dung | Đồng hồ xem nguồn | Kết quả |
|---|---|---|---|
| Mực Triều `skill_01` NE | Chuẩn bị → quét ngang → thu bút | 0,72 s như nguồn trước | Sửa góc NE đạt; NW vẫn ghi rõ là lật |
| Hàn Châm `skill_02` NE | Ba chấm cổ tay → phát bút gọn → hồi phục | 0,64 s như nguồn trước | Sửa góc NE đạt; NW là lật |
| Thủy Kính `skill_03` N/NE/E/SE/S | Vẽ vòng trước ngực → mở lòng bàn tay → thu tay | 16 × 50 ms = 0,80 s | NE/E/SE/S đạt; N HOLD |
| Mưa Tinh `skill_04` N/NE/E/SE/S | Cúi nhẹ, vẽ vòng thấp trước chân → nâng tay → đứng lại | 9 × 50 ms + 7 × 64²⁄₇ ms = 0,90 s | NE/E/SE/S đạt; N HOLD |
| Lưu Thủy Bộ `skill_05` N/NE/E/SE/S | Hạ trọng tâm → bước thu/chân theo sau → hồi tư thế | 4 × 40 ms + 6 × 30 ms + 6 × 43⅓ ms = 0,60 s | Năm nguồn đạt kiểm clip riêng |
| Long Mạch Hồi Nguyên `skill_06` N/NE/E/SE/S | Vòng bút thấp rộng → nâng bút và mở tay → hồi tư thế | 16 × 68,75 ms = 1,10 s | Năm nguồn đạt kiểm clip riêng |

N/NE/E/SE/S là năm nguồn vẽ riêng. SW/W/NW chỉ là tham chiếu lật có nhãn theo policy hiện hành, không cộng thành nguồn mới. Bản NE đầu tiên của Mực Triều nghiêng quá gần E nên được giữ trong lịch sử; bản chọn v2 dùng một ảnh hướng dẫn sau ba phần tư rõ hơn. Guide chỉ hướng dẫn góc, **không phải ảnh do chủ dự án đã duyệt**, không được đưa vào runtime hoặc tính là bộ animation. Hồ sơ tham chiếu phân biệt guide do AI tạo với ảnh nhận diện cũ đã chọn.

Giữ cùng nhân vật tóc đen tết dài/hoa ngọc, áo trắng–xanh băng, vai xanh, đai nâu và giày tối. Bút gỗ có đai vàng, đầu lông màu kem trong tay phải giải phẫu; tay còn lại trống. Không vẽ khiên, đạn, mưa hoặc ấn đất vào thân.

Lưu Thủy Bộ được xem như clip chuyển động tại chỗ. Khoảng lùi 4 m, hướng lùi, va chạm, tăng tốc và phản hồi cloth khi nhân vật thực sự dịch chuyển còn phải kiểm trong assembly/gameplay. Không dùng video pose tại chỗ để chứng nhận đường di chuyển hoặc cơ chế né.

## Chín thành phần hiệu ứng

| ID | Hình và vai trò | Thời lượng nguồn / kiểu phát | Kết quả |
|---|---|---|---|
| `sk_hb_02_frost_sustain_component` | Sáu cánh băng rời quanh tâm rỗng, ánh lướt nhỏ | 0,80 s / lặp | Đạt nguồn và đường nối 14→15→0→1 |
| `sk_hb_03_gain_component` | Nét ngọc khép thành viền oval khiên, mặt giữa trong suốt | 0,40 s / một lượt | Đạt nguồn |
| `sk_hb_03_sustain_component` | Viền khiên giữ hình, hai ánh nhỏ chạy quanh mép | 0,80 s / lặp | Đạt nguồn và đường nối vòng |
| `sk_hb_03_expire_component` | Viền khiên tan thành giọt nhỏ, hết hạn tự nhiên | 0,40 s / một lượt | Đạt nguồn |
| `sk_hb_03_break_component` | Viền bị ngắt/nứt thành đoạn ngắn rồi tan | 0,32 s / một lượt | Đạt nguồn |
| `sk_hb_04_tell_component` | Nét ellipse thấp tạo vùng báo trước, tâm rỗng | 0,45 s / một lượt | Đạt nguồn |
| `sk_hb_04_rain_component` | Các vệt mưa thẳng rơi thưa trong vùng | 0,80 s / lặp | HOLD: lõi sáng quá yếu ở native |
| `sk_hb_04_heal_tick_component` | Hai dải sáng mảnh rời nhau đi lên, tan thành giọt | 0,32 s / một lượt | Chọn v2, đạt nguồn |
| `sk_hb_04_expire_component` | Viền vùng đất rã thành giọt quanh chu vi rồi mất | 0,40 s / một lượt | Đạt nguồn |

Bản hồi máu v1 giống biểu tượng nên giữ ngoài selection. V2 dùng hai dải riêng, không có mặt nền đục hoặc hình huy hiệu ở render native. Màu RGB nổi trong vùng alpha rất thấp khi xem PNG nguồn không đồng nghĩa có khối sáng đục trong Godot; không dùng script xóa RGB/alpha. Mọi bản runtime giữ nguyên byte PNG nguồn.

Các component chưa được nghiệm thu là một bộ kỹ năng hoàn chỉnh. Cần ghép và kiểm tỉ lệ, độ nghiêng, điểm gắn caster/target/đất, lớp che khuất và camera rộng. Khiên gain/sustain/expire/break là các trường hợp riêng; thời gian nguồn 0,8 s không phải thời gian khiên 4 s. Mưa/tick không tự cấp hồi máu, chọn mục tiêu hoặc quyết định thời gian sự kiện server. VFX riêng cho Lưu Thủy Bộ và Long Mạch Hồi Nguyên còn cần sản xuất.

## Ba nguồn chưa đạt

1. **Thủy Kính N:** khi bút đi qua phía xa và ló cạnh tay áo trái, đường nối tay phải chưa đủ rõ để xác nhận giữ tay cầm. Cần vẽ lại với tay trái trống được giữ rõ, cẳng tay phải bị thân che đúng chỗ.
2. **Mưa Tinh N:** pha nguồn 9, tức tư thế thứ mười, hiện hai đầu bút ở hai bên; các pha 6–8 cũng gây hiểu thành đổi tay. Giữ HOLD, không sửa bằng ẩn một lớp raster hay bỏ khung.
3. **Mưa duy trì:** vệt/lõi quá yếu ở kích thước native, cần vẽ lõi trắng ngà/xanh rõ hơn rồi kiểm lại mật độ và vòng lặp. Việc có đủ 16 ô không giải quyết độ đọc của hiệu ứng.

Renderer mặc định chặn nguồn HOLD. Studio/browser review được xem để sửa, vì vậy các ảnh capture trước ledger vẫn có thể hiển thị ứng viên và nhãn trạng thái cũ. Ledger nguồn sau kiểm mới là quyết định hiện hành.

## Đăng ký ảnh và các lỗi đã sửa qua native

Ba nguồn cần biên ô đo theo khoảng trống thực: Thủy Kính NE, Mưa Tinh N và viền Mưa Tinh khi hết. Mũi bút/giọt nằm sát đường chia đều không bị cắt bỏ; metadata vùng chọn thay đổi, PNG không đổi. Kiểm ô rỗng, cắt biên và trùng nguồn vẫn được giữ.

Lượt native đầu cho thấy điểm neo X theo đai áo có thể nhảy khi tay/tóc che đai. Các động tác đứng dùng gốc giày tối. Động tác lùi dùng X chiếu từ đầu với offset của tư thế trung tính và Y theo nền giày, tránh đổi sang một nửa đai áo giữa clip. Đây là mốc trình bày nguồn, chưa xác nhận mốc collider hoặc root motion trong thế giới.

Vòng đang hình thành neo theo cực dưới còn tồn tại của nét, hiệu chỉnh từ vòng khép ở hàng cuối; không đuổi theo tâm bounds của một cung chưa hoàn tất. Viền đầy đủ dùng tâm đối xứng. Viền đang tan dùng điểm gốc theo cột/hàng nguồn và ngoại suy vùng mảnh cuối, tránh chạy theo một hạt cuối hoặc làm lệch vòng ở lúc chuyển hàng. Đã ghi lại các clip chịu thay đổi và giữ 11 video cũ trong thư mục `Superseded_*` để truy vết.

Bộ ghi so tám hướng từng dừng sau các video nguồn vì hai source hướng S của skill 01/02 thuộc đợt E, nằm ngoài tập F đang lọc. Đã sửa để lấy selection hiện hành từ toàn registry, yêu cầu đúng một record và 16 thời lượng trước khi ghi. Các video hợp lệ giữ nguyên khi resume; các binding thay đổi được ghi lại riêng. Không mất PNG hoặc dựng lại toàn bộ do lỗi quan sát.

## Xem và tiếp tục chỉnh tay

```powershell
ClientGodot/Run_Actor_Library.ps1 -SkipBuild -Actor CLASS_HUYEN_BUT -Clip skill_06
ClientGodot/Run_Art_Studio.ps1 -SkipBuild -Entry class_huyen_but_skill_06_s
```

Studio vẫn cho dừng/tua từng khung, chỉnh tọa độ, tỉ lệ, lớp và nhịp; xuất bản chỉnh JSON riêng. Các script calibration/promotion/refinement của đợt là công cụ một lần trước duyệt, có guard chặn chạy lại lên nguồn đã chốt. Chỉnh tiếp sau duyệt cần dự án Studio/phiên bản nguồn mới và review lại binding, không ghi đè PNG gốc.

## Bằng chứng và phạm vi

`Implementation/Reports/Evidence/Actor_Batch_20261114f` chứa 31 video nguồn và sáu video so tám hướng; tổng 37 video chọn, mỗi video 180 khung, decode sạch. Ảnh `_poses.png` lấy đúng 16 tư thế native ở kích thước render, bỏ phần giao diện editor; `_source_samples.png` giữ ngữ cảnh rộng. Log `ART_STUDIO_SOURCE_TICK` và `capture_sample_plan.json` khóa thời điểm nguồn thực hiển thị, không ước lượng tư thế chỉ từ thời lượng. Ba strip vòng lặp lấy riêng nguồn 14/15/0/1. Không dùng movie offline 60 bước/giây làm chứng nhận FPS gameplay.

301 pin trước đợt được giữ nguyên; thêm 28 pin, tổng **329**. Giữ 343 payload page cũ không thuộc hai sửa NE, lưu lịch sử hai nguồn NE bị thay và bảo toàn 46 PNG cũ chủ dự án đã chọn. Catalogue hiện có **374 page cấu trúc, 371 PNG runtime**; **85/1028 job đủ cấu trúc, 54 job đủ hướng đã duyệt nguồn, 943 job thiếu nguồn**, 23 nguồn HOLD. Số “11/16” trên browser Huyền Bút là đủ binding, chưa phải 11 action đạt chất lượng; mới bốn body skill 01/02/05/06 đủ góc đã duyệt.

Build .NET không lỗi/cảnh báo. Kết quả kiểm Python, inspector/export, các inventory, native Library/Studio/assembly và LFS được ghi trong báo cáo kiểm cuối của đợt. Các kiểm cấu trúc/hash không thay thế ba kết luận HOLD ở trên.

Cần tiếp tục hai nguồn N và lớp mưa chưa đạt; sản xuất các lớp VFX cơ động/tuyệt kỹ; bổ sung năm action Huyền Bút chưa đủ nguồn và kiểm/làm lại năm action kế thừa chưa duyệt. Còn ba hướng vận động Minh Kiếm HOLD, các class khác, quái, boss, NPC, biến thể, môi trường và UI. Hàng đợi 1028 job chỉ là phần lõi actor/VFX; không được coi lấp hết con số này là hoàn thành toàn bộ asset game.

## Kết quả kiểm cuối

Python: 104 kiểm đạt. Native Library: 19160 assertion đạt; Studio: 99454 assertion, 454 entry; Skill Assembly: 13311 assertion, 12 profile và 20 scenario đạt. Bộ assembly này vẫn chỉ gồm Minh Kiếm/Ảnh Đao, chưa chứng nhận skill Huyền Bút hoàn chỉnh. 22 inventory cập nhật theo catalogue hiện hành. Build 0 lỗi, 0 cảnh báo. Xem verification_summary.json và log riêng trong Evidence.
