# Biên tập thoại mở đầu — P00-01 đến P00-05

Codex biên tập15dòng trong `Quest_Dialogue_Production_Data_vi.csv`: OFFER/CLUE/TURN_IN của5quest đầu. Giữ nguyên quest ID, node ID, speaker, condition, text key, next node, event và flag. Trạng thái copy `VI_EDITED_P1`; chưa voice-recorded, chưa UI/owner sign-off. 215dòng còn lại trong tổng230 vẫn chờ line-edit, không đổi thành approved hàng loạt.

## Giọng nói và thông tin

- Ly An xưng tôi, nói ngắn/gần việc đang làm, quan tâm người gửi/người nhận; không giảng lore hoặc tự nhận biết suy nghĩ Tạ.
- Tạ Vân Khanh xưng ta, kiệm lời, chú ý dấu vật; gợi điều đang giấu nhưng không thú nhận chuyện30năm từ mở đầu.
- Không đưa ID máy, tọa độ/checkpoint kỹ thuật hoặc lời hứa lưu mạng vào miệng NPC. Counts quan trọng vẫn rõ trong tracker/quest spec; thoại không thay objective.
- P00-05 chỉ xác nhận môn phái đã chọn, không giới thiệu cơ chế đổi class. Từ “Huyền Ấn” chỉ xuất hiện ở turn-in sau khi đã tương tác mảnh ấn, không nhét vào clue đang ACTIVE trước khám phá.
- TURN_IN đang có guard READY và event COMMIT_REWARD; lời nói tránh khẳng định vật phẩm đã vào túi trước server commit. UI success/reward riêng chỉ mở khi nhận kết quả authoritative. Không đổi callback hoặc state server bằng sửa copy.

## Các chỗ graph còn cần tích hợp, không che bằng văn hay

Graph baseline3node/quest chưa là đủ nhánh accepted/objective/ready/commit/error của runtime. P00-03 lời kể hai người được cứu không thay phase visibility; P00-04 dấu sáp rạn phải đúng checkpoint; P00-05 cảnh mảnh ấn không tự đánh dấu quest complete. Nếu copy cần guard sâu hơn, thêm proposal, không tự nối event mới trong CSV.

Mỗi đoạn hiển thị từng câu/khối và cho cuộn hoặc chuyển trang. Không hứa vừa2dòng ở640×360 khi chưa có font metrics. Subtitle có speaker label, skip/đọc lại; người dùng bỏ thoại vẫn hiểu mục tiêu qua tracker. Không lồng voice cuối khi215dòng và các điều kiện reveal còn chưa line-edit.

## Kiểm tra gói

Đối chiếu CSV với baseline git: cùng230hàng/thứ tự/header, chỉ15 `text_vi` và15 `localization_status` đổi; các field logic phải bất biến. Kiểm UTF-8/NFC, không ID/tọa độ lộ trong15lời thoại; validate narrative/content/contracts liên quan. Đây là kiểm dữ liệu và nội dung bằng đọc, không là kiểm subtitle trong Unity hoặc chất lượng diễn xuất.
