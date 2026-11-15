# Huyền Bút: hành động còn thiếu, VFX cơ động/tuyệt kỹ và sửa nguồn HOLD

Ngày kiểm 15/11/2026: **36 nguồn chọn, 33 nguồn đạt kiểm riêng và ba HOLD**. Đây là đợt tiếp theo của thư viện baked chibi, không khôi phục paperdoll. Studio chỉnh tay vẫn giữ. Mục tiêu toàn thư viện còn nhiều hạng mục chưa làm.

## Phạm vi nguồn

Chọn 36 PNG gốc, mỗi sheet 4 × 4 gồm 16 tư thế: **576 pose nguồn**. Có 41 phiên bản PNG được lưu, trong đó năm bản thay thế nội bộ không được binding runtime. Hai lần tạo tương tác Đông Nam trước đó không lưu được tệp mặc định do ổ C đầy; không tính các tệp 0 byte là sheet hoặc pose bàn giao.

| Nguồn | Số sheet | Nhịp xem nguồn | Trạng thái |
|---|---:|---|---|
| Chạy N/NE/E/SE/S | 5 | 16 × 40 ms = 0,64 s, vòng lặp | NE/SE/S đạt; N/E HOLD vì contact đối nhau chưa rõ |
| Đánh thường 2 N/NE/E/SE/S | 5 | 16 × 40 ms = 0,64 s | Hất bút chéo lên; đạt năm góc nguồn |
| Đánh thường 3 N/NE/E/SE/S | 5 | 16 × 50 ms = 0,80 s | Bổ bút chéo xuống; đạt năm góc nguồn |
| Né N/NE/E/SE/S | 5 | 16 × 37,5 ms = 0,60 s | Đạt nguồn tại chỗ; chưa kiểm đường di chuyển/collision |
| Tương tác N/NE/E/SE/S | 5 | 16 × 62,5 ms = 1 s | N/E/SE/S đạt; NE HOLD vì thừa bàn tay pha giữa |
| Thủy Kính N, Mưa Tinh N | 2 | 0,80 s và 0,90 s | Đã sửa đạt hai nguồn F HOLD |
| Mưa Tinh: lớp mưa | 1 | 16 × 50 ms = 0,80 s, lặp | Đạt độ rõ giọt và nối vòng nguồn |
| Lưu Thủy Bộ: khởi động/vệt bước/tan | 3 | 0,32 / 0,30 / 0,30 s | Đạt từng module; chưa ràng buộc đường đi server |
| Long Mạch: chuẩn bị/sóng/hồi đồng đội/giải trạng thái/tan | 5 | 0,55 / 0,45 / 0,48 / 0,32 / 0,40 s | Đạt từng component; chưa nghiệm thu ghép skill |

SW/W/NW là mirror của SE/E/NE theo chính sách nhân vật hiện hành; phải hiển thị nhãn mirror, không tính là ba bộ hình vẽ độc lập. NE tiếp tục dùng guide AI của F để phân biệt góc nhìn sau chéo với N/E; guide không phải nguồn được chủ dự án duyệt. Dáng, trang phục và bảng màu gốc tham chiếu `class_huyen_but_idle_v2.png` vẫn được giữ, không tự chứng nhận action cũ đã đạt.

## Sửa trong quá trình làm

- Vệt tan Lưu Thủy Bộ v1 có nhịp phình lên; chọn v2 bắt đầu bằng hai nét hoàn chỉnh rồi rã nhỏ dần.
- Vệt tan tuyệt kỹ v1 có lớp nền màu alpha thấp phủ sheet; v2 bỏ nền nhưng đổi sang nhiều nút. Chọn v3 theo đúng ba nút của ấn chuẩn bị. Các phiên bản cũ lưu lịch sử, không trộn ô hoặc cắt bỏ pose để che lỗi.
- Khởi động cơ động ban đầu dự kiến 0,24 s: 16 pose không thể cùng xuất hiện trên đồng hồ xem 60 Hz ở thời lượng đó. Nhịp **xem nguồn** đổi sang 0,32 s; không đổi quãng lùi, cooldown, tốc chạy hoặc thời gian server. Cần adapter/timeline riêng khi ghép kỹ năng.
- Một số sheet có lề ngoài không đều. Metadata chọn đường cắt trong các gutter trống ở alpha core; không sửa/resize PNG. Kiểm ô rỗng, trùng và cắt biên vẫn được giữ.
- Tư thế né thấp cần tìm giày theo chiều cao hiện tại của thân và vùng chân rộng hơn tư thế đứng. Có kiểm hồi quy bằng fixture tổng hợp; chưa dùng kết quả tính toán làm duyệt chất lượng.
- Chạy S v1 chưa rõ contact; v2 bị lẫn giáp vàng từ ảnh tham khảo. Bản v3 phục hồi giày tối/trang phục đã chốt, kiểm 16 pha và nối vòng thực. Bản v1/v2 giữ lịch sử, không trộn ô vào nguồn chọn.
- Long Mạch tan v3 sửa biên hàng `[0,397,633,876,1246]` để nút trên không bị cắt sang ô trước; ấn chuẩn bị sửa biên `[0,383,636,888,1246]`, neo vào tâm ba nút ngọc cố định thay vì bounding box nét đang vẽ. PNG nguyên vẹn.
- Hồi đồng đội sửa neo chân theo hai hàng đầu và bước emitter cố định để tránh nhảy khi padding khác nhau. Mưa Tinh N có đồng hồ xem nguồn riêng, chưa coi đó là bằng chứng khớp timing mọi góc của đợt F.

## Lưu ảnh và khả năng tiếp tục

Ổ C hết dung lượng trong lúc tạo nguồn. Khi công cụ không ghi được PNG mặc định nhưng còn trả payload ảnh, payload được chép nguyên byte sang D, kiểm chữ ký PNG và SHA-256 rồi mới đưa vào thư mục dự án. Không vẽ lại/chỉnh alpha bằng Python, không xóa tệp cá nhân. Prompt, phiên bản, đường dẫn đầu vào và hash được giữ riêng từng nguồn. Tệp tạm và userdata của lượt ghi Godot đợt này đặt trên D bằng biến môi trường chỉ trong tiến trình ghi kiểm.

## Bảo toàn và giới hạn nghiệm thu

Migration chỉ thay ba ID đang HOLD của F và thêm 33 ID mới; không thay nguồn đã duyệt. Baseline giữ 329 pin nguồn, 371 payload page không thuộc ba nguồn được sửa và 46 PNG cũ chủ dự án đã chọn. Catalogue sau migration có 407 page cấu trúc, trong đó 404 page PNG đang được tham chiếu; các PNG lịch sử nằm riêng và không được tính là nguồn đang chạy.

`Implementation/Reports/Evidence/Actor_Batch_20261114g` có ledger `source_native_review.json`, `delivery_audit.json` và trace lấy mẫu. Có **43 video hiện hành**, mỗi video giải mã đủ 180 frame: 36 nguồn riêng và bảy bảng tám hướng. Đã xem 16 pose native của từng nguồn, bảy bảng hướng và bốn dải nối vòng thực 14/15/0/1. Lưu riêng năm video thử bị thay và một snapshot SE byte giống video hiện hành; snapshot không tính thành bản lỗi. Header HOLD trong video là mốc trước khi áp ledger, không phải trạng thái catalogue cuối.

Audit xác nhận 329 pin cũ, 371 payload page và 46 PNG chủ dự án chọn không đổi; 404 PNG runtime đang được binding byte giống nguồn. Có 362 pin hiện hành, 90/1028 job đủ cấu trúc, 59 job đủ hướng đã duyệt, 938 job thiếu nguồn và 23 page HOLD. Huyền Bút đủ binding 16/16 nhưng mới **9/16 action đủ góc đã duyệt nguồn**: sáu skill, combo2/combo3 và né. Nguồn chạy N/E cần vẽ contact/passing đối nhau; tương tác NE phải bỏ bàn tay idle còn sót khi bàn tay mới đưa ra. Hướng W/NW phụ thuộc nguồn HOLD cũng bị chặn.

Năm action kế thừa Huyền Bút chưa được kiểm nguồn đầy đủ; toàn bộ skill assembly Huyền Bút, VFX theo trạng thái máy chủ, phần di chuyển thực và gameplay chưa được nghiệm thu từ đợt này. Các class khác, quái, boss, NPC, biến thể, map và UI vẫn thuộc mục tiêu thư viện cần tiếp tục. Không đánh dấu hoàn thành game hoặc thư viện dựa trên số sheet của một đợt.

## Kiểm hồi quy cục bộ

108 bài kiểm Python đạt; build 0 lỗi/0 cảnh báo. Godot Library đạt 19.688 kiểm tra; Studio đạt 105.581 kiểm tra/492 entry; Skill Assembly đạt 13.311 kiểm tra, 12 profile/20 tình huống/tám hướng. Đã build và kiểm lại 23 inventory. Đây là kiểm hồi quy công cụ và dữ liệu, không chứng nhận toàn bộ gameplay hoặc FPS thực trên máy người chơi.
