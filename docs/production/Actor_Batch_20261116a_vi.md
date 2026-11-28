# Đợt A — sửa chu kỳ đi bộ Huyền Bút

Đã vẽ lại năm hướng N/NE/E/SE/S thành **năm sheet nguyên khối / 80 tư thế nguồn**. Sau xem atlas gốc, 16 pha native từng hướng, năm đường nối vòng thật và bảng tám hướng, **duyệt riêng hướng Nam**. N/NE/E/SE tiếp tục HOLD; các hướng lật phụ thuộc nguồn HOLD vẫn bị chặn ở renderer production.

| Nguồn | Kết quả kiểm hình |
|---|---|
| N | Contact 0/8 đã rõ hơn, nhưng 14/15 còn giữ thứ tự chân của nửa chu kỳ đối diện rồi đổi đột ngột ở 0. Cần sửa passing và tiếp cận contact cuối vòng. |
| NE | Góc lưng chéo và đường nối yên; chân gần/xa còn bị vạt áo che, chưa xác nhận đổi chân từ pha tay. |
| E | Thân đứng thẳng, đường nối bớt bật; vẫn khó phân biệt sở hữu chân dẫn tại 0/8. |
| SE | Giữ mặt, bút và đường nối; dáng chân dưới phải còn giống nhau ở hai contact, chưa duyệt đổi chân. |
| S | Hai lượt chân tách rõ: chân phải cơ thể/bên trái màn hình dẫn ở 0, chân trái/bên phải dẫn ở 8; có passing và đường nối nhỏ, liền mạch. Duyệt source/clip riêng. |

Giữ nguyên mẫu chibi tóc đen tết, hoa ngọc, áo trắng/xanh nhạt và một bút tay phải. Mọi PNG do `image_gen` tích hợp tạo; prompt chính xác lưu cùng tên. Nguồn cũ không bị sửa pixel. Năm ID chưa được duyệt được thay selection và đưa record cũ vào lịch sử; inventory I hiện chọn 20 sheet, báo cáo I giữ mốc 25 sheet tại lúc giao.

S có ranh ô cần hiệu chỉnh theo dải alpha trống thật; chỉ đổi metadata. Cả năm project Studio di động giữ texture nguyên byte, 16 nguồn riêng, neo và thời lượng chỉnh tay được. Walk dùng 16 × 60 ms = 0,96 giây cho mục đích xem nguồn. Không sửa tốc độ server, collider, sát thương hoặc hit window.

Có sáu video native, mỗi video giải mã sạch 180 frame: năm nguồn riêng và một bảng tám hướng. Trace xác nhận đủ 80 pha; năm dải 14/15/0/1 lấy từ nối vòng thực. Có receipt SHA texture/project/video và nhật ký import/render. Ba hướng lật được ghi nhãn, không đếm là tư thế vẽ riêng. Các header video ghi trạng thái trước áp ledger.

Kiểm hồi quy: 111 bài kiểm Python đạt; Godot Library 20.072 kiểm tra đạt. Inspector `--export --check` và 26 inventory hiện hành được đối chiếu. Không có thay đổi C# từ build đợt I 0 lỗi/0 cảnh báo. Không lặp hoặc gọi kết quả Studio/Assembly đợt I là nghiệm thu chuyển động gameplay của A.

`delivery_audit.json` kiểm giữ nguyên **385 pin trước, 426 payload page ngoài phạm vi thay và 46 PNG chủ dự án chọn**; 428 PNG runtime đang chọn nguyên byte. Hiện **386 pin**, 431 page cấu trúc gồm ba legacy, **65/1028 job đủ góc duyệt, 938 job thiếu nguồn, 24 page HOLD**. Huyền Bút vẫn **15/16 action đủ hướng duyệt** vì walk còn bốn hướng chưa đạt.

Bằng chứng ở `Implementation/Reports/Evidence/Actor_Batch_20261116a`, PNG ở `Art_Source/Actor_Library_20261107/Sheets`, prompt ở `Prompts`. Tiếp tục sửa bốn hướng, sau đó kiểm chuyển thế/độ lớn thân, neo chân khi đi thật, ghép VFX và camera rộng. Một hướng đi đạt không chứng nhận toàn class, gameplay 60 FPS hoặc toàn thư viện.
