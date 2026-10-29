# Biên tập thoại Chương I — dấu và người ký

Codex line-edit18lời OFFER/CLUE/TURN_IN của C1-01..06 trong `Quest_Dialogue_Production_Data_vi.csv`. Status `VI_EDITED_C1` là bản biên tập ứng viên, chưa voice/owner sign-off/Unity subtitle approval. Kết hợp15lời P00 đã biên tập, hiện33/230lời có edit;197lời còn VI_BASELINE. Không đánh dấu cả campaign đã có thoại final.

Nguồn: Quest Production Spec Chương I và `Narrative_Depth_and_Discovery_vi.md` §2–6. Giữ36main/40side quest, tên/ID canonical và timeline300năm/30năm. Không đổi NPC, node, choice, condition, event, flag, objective/count, reward hoặc unlock bằng cách sửa câu nói.

## Mục đích của từng đoạn

| Quest | Trải nghiệm trong lời thoại | Điểm tiết lộ giữ lại đến TURN_IN/READY |
|---|---|---|
| C1-01 Cổng Thanh Lạc | Ly An nhìn thành qua thói quen người đưa thư; người chơi có chỗ nghỉ và việc tự tìm đường | Không kết luận vì sao năm cờ khác hướng hoặc ai giữ thư |
| C1-02 Bài thử môn phái | Người thầy hỏi người chơi đọc tình thế, không chỉ lặp một nút đánh | Không tự nhận đã mở skill/cấp vũ khí trước reward commit; không suy người chơi đã chọn class mới |
| C1-03 Phù tín giả | So dấu dừng nét, hỏi hai lời khai riêng; vật chứng và người làm chứng đều có giá trị | Phù có nét gia công theo khuôn máy chỉ được kết luận khi READY, không nói nguyên nhân trước lúc soi/hỏi/bắt |
| C1-04 Tượng mở mắt | Đội trưởng lo mở đường cứu hộ vệ, giữ tang vật sau trận | Giữ giả thuyết/quan sát theo phù; không tự quy cả người mang phù là đồng phạm hoặc đổi quest thành giết dân |
| C1-05 Năm lời thề | Nghe riêng năm lời kể, nhận một thỏa thuận đình chiến còn mong manh | Hồ sơ tháp bị xóa chỉ xuất hiện ở READY; không lộ Cơ/Tống/trách nhiệm Tạ của chương sau |
| C1-06 Con dấu qua phố | Điều tra không combat: hóa đơn→dấu lò→lưu trữ→đối chiếu→báo cáo; giữ cả chứng cứ không buộc tội ai | Nhựa dẫn về Lâm Triều sau đối chiếu; giao thương không tự chứng minh Sầm/merchant/môn phái phạm tội |

Không biến TURN_IN thành bài thuyết minh toàn tri: nhân vật chỉ nói điều có từ quest hiện tại và kiến thức được phép biết. Các CLUE có guard QUEST_ACTIVE nên không khẳng định mọi bằng chứng đã tìm được; nhật ký vẫn là chỗ giữ counts và objective chính xác.

## Giọng nhân vật

- **Ly An:** tôi/bạn, câu gần đời sống thư và địa chỉ, có khoảng lặng sau Bến Mưa. Không nói thay suy nghĩ Tạ, không biến thành nhân chứng30năm trước hoặc đặt giới tính cho avatar.
- **Thầy môn phái:** ta/ngươi, nhắc nhịp ra tay/lui lại, dùng được cho dynamic speaker `NPC_MASTER_BY_PLAYER_CLASS`. Đây vẫn là lời chung; chưa có5biến thể class-specific hoặc runtime resolver mới. Không gọi template macro này là NPC prefab cụ thể đã tích hợp.
- **Hạ Mặc:** ta/ngươi, chú ý chỗ không khớp và giữ lời kể ban đầu. Ở Chương I đã biết chưa đủ bằng chứng kết tội; còn bài học bảo vệ danh tính và hỏi sự đồng ý thuộc các chương sau, không kể trước.
- **Đội trưởng:** câu ngắn hướng cứu người và giữ đường. Người mang phù có thể bị lừa; không nhập nhằng thứ game đánh dấu là quái với đạo đức của dân thường.

## Hướng dựng cho Muse

Thành vẫn có tiếng mua bán và người tự làm việc giữa các câu thoại. C1-01 chừa khoảng nhìn cờ/bản đồ; C1-03 cận nét phù có mô tả chữ/icon tương đương; C1-04 trở lại hộ vệ trước khi dựng shot tang vật. Sau boss C1-05 cho đoạn yên để người chơi chủ động đọc, không bắt chờ timer. C1-06 dùng tay cân, giấy và dấu lò dẫn nhịp; không nhạc giật gân biến Sầm thành kẻ có tội.

Chỉ dùng lời ở node đã được guard authoritative mở. Cận nhựa Lâm Triều và cảnh hồ sơ xóa không chen vào clip/thumbnail công khai hoặc CLUE trước khám phá. Không gán tóc/mặt/giọng/môn phái cố định cho avatar. Bản này cung cấp copy cho subtitle/storyboard; chưa phải yêu cầu render mọi câu thành video hoặc lồng voice cả campaign.

## Ranh giới runtime và QA

Ba node baseline/quest vẫn chưa biểu diễn đủ accepted/objective/ready/commit/error. `on_enter_event` hiện có được giữ nguyên để không sửa wire bằng CSV; adapter không được coi việc hiển thị CLUE hoặc hết video là objective/reward server. Nếu muốn nhánh theo từng bằng chứng phải có graph/guard proposal riêng. Client hiện #51 chỉ hỗ trợ P00-01 và chưa phát/hiển thị các thoại Chương I; copy mới không chứng minh quest đã chơi được.

Không câu nào khẳng định tiền/đồ đã vào túi khi guard mới READY. Reward success panel và audio chỉ phản hồi sau commit thật. Cho người chơi đọc lại/skip; tracker giữ đủ mục tiêu nếu bỏ thoại. Chưa đo font metrics nên không cam kết một lời vừa2dòng ở640×360, không đặt auto-advance theo số ký tự.

Báo cáo dữ liệu: `Implementation/Reports/Chapter_One_Dialogue_Editorial_20261029.json`. So baseline theo từng hàng và header: chỉ18text_vi +18localization_status thay đổi; toàn bộ field logic và thứ tự230hàng giữ nguyên, gồm hai choice row C3-05 cùng node_id hợp lệ ở baseline. Kiểm UTF-8/NFC, không ID/tọa độ kỹ thuật trong18lời mới, narrative/content/contracts validation. Việc kiểm này không thay review diễn xuất, subtitle readability hoặc runtime reveal guards.
