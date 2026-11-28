# Huyền Bút: sửa nguồn chạy và tương tác — đợt H

Ngày kiểm 15/11/2026. **Ba nguồn sửa/48 tư thế chọn đã đạt kiểm riêng.** Có sáu PNG nguyên gốc được lưu: chạy N, tương tác NE và bốn lần sửa chạy E. Ba phiên bản E trước giữ lịch sử, không đếm thành tư thế chọn mới. Đây là sprite chibi nguyên khối; Studio chỉnh tay và mọi PNG cũ đã chốt vẫn giữ.

## Sửa lỗi đã quan sát

- Chạy N: vẽ lại chân đối nhau tại contact0/8; giữ mặt sau, một bút ở tay phải và điểm gốc đo từ nguồn. Đã kiểm đủ 16 pha cùng đoạn nối thực14/15/0/1.
- Chạy E: v1 vẫn lặp nhịp hai nửa; v2 đổi nhịp tay nhưng bút bật ở15→0; v3 sửa tay bốn pha cuối nhưng pha12 thiếu đầu bút rõ. Bản v4 giữ bút liên tục tại pha12, tay về sau trước15→0. Đã xem lại cả16pha, không chỉ ô được sửa; W lật được đối chiếu trong thư viện.
- Tương tác NE: bỏ bàn tay idle thừa khi bàn tay trái đưa ra. Hai tay gắn đúng cánh tay, bút vẫn ở tay phải; góc sau chéo và NW lật được kiểm riêng.

Nguồn, prompt và các bản thử nằm ở `Art_Source/Actor_Library_20261107/Sheets` và `Prompts`, hậu tố `20261115h`. Mirror SW/W/NW vẫn mang nhãn, không tính là bộ vẽ riêng. Tham khảo AI không phải approval của chủ dự án.

## Kiểm native và lỗi import

Có **năm video hiện hành**, mỗi video giải mã sạch đủ180frame: ba project nguồn riêng và hai bảng tám hướng chạy/tương tác. Trace xác nhận đủ16pha nguồn; hai dải nối vòng lấy từ vòng lặp thật. Ba video E cũ lưu riêng. Hai video đối chiếu đầu tiên bị thiếu tài nguyên do PNG mới chưa import cũng được giữ trong `Failed_Import`, không tính là bằng chứng đạt.

Lỗi Godot có thể ghi `ERROR:` nhưng trả exitcode0. Hai script capture H hiện kiểm cả nhật ký và dừng khi có lỗi tài nguyên/render; sau import đã ghi lại hai bảng tám hướng, kiểm đủ ô hiển thị. Các header HOLD trong video là trạng thái trước khi áp ledger, không phải số HOLD cuối.

Portable project Studio ở `Implementation/Reports/Evidence/Actor_Batch_20261115h/Candidate_Studio` chứa PNG nguyên byte trong `textures/`, có16vùng ảnh/pivot/timing để mở và chỉnh tay. Các crop từ video chỉ là bằng chứng, không dùng làm asset game. Không ghép ô, chỉnh alpha hoặc vẽ lại pixel bằng script.

## Bảo toàn và giới hạn

`delivery_audit.json` xác nhận **362 pin cũ,404payload page không liên quan và46PNG chủ dự án chọn không đổi**. Toàn catalogue vẫn407page,404PNG runtime đang binding byte giống nguồn. Pin hiện365; 90/1028job đủ cấu trúc,61job đủ hướng duyệt,938job thiếu nguồn,20pageHOLD.

Huyền Bút hiện **11/16 action đủ góc đã duyệt nguồn**. Năm action kế thừa idle/walk/basic_attack/hurt/death đang được kiểm và thay nguồn trong đợt I; không tự chứng nhận từ tên action có sẵn. Inventory G hiện chọn33sheet sau khi ba nguồn HOLD chuyển sang H; báo cáo G giữ mốc36sheet lúc bàn giao.

Source approval không nghiệm thu toàn class, đường di chuyển/collision, chuyển action, skill assembly hoặc gameplay. Bàn assembly hiện12profile/20tình huống cho các class trước, chưa chấp nhận assembly Huyền Bút. Video offline60bước/giây không chứng minh game chạy ổn định60FPS trên máy người chơi. Còn các class khác, quái/boss/NPC, biến thể, map/UI và toàn bộ phần tích hợp phải tiếp tục.

## Kiểm hồi quy

Build0lỗi/0cảnh báo;108bài kiểm Python đạt. Godot Library19.688kiểm tra;Studio105.581kiểm tra/492entry;Skill Assembly13.311kiểm tra,12profile/20tình huống/tám hướng. Đã build và kiểm24inventory hiện hành. Không dùng các số này thay nghiệm thu ảnh hoặc FPS gameplay.
