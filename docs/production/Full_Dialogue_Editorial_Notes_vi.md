# Biên tập hoàn tất bảng lời thoại nhiệm vụ — 2026-10-29

Đã line-edit đủ **230/230 dòng lời thoại trong bảng 76 nhiệm vụ**, gồm36main/40side và17vai nói (có macro thầy theo lớp). Đợt này sửa197dòng còn baseline:75lời OFFER/CLUE/TURN_IN C2..C6,2hàng lựa chọn C3-05 và120lời của40quest phụ. Hai hàng lựa chọn dùng chung một câu hỏi như graph gốc, tổng229prompt riêng. Giữ nguyên33lời P00/C1 đã biên tập trước. Không còn `VI_BASELINE` trong bảng.

Nguồn chính: `Quest_Dialogue_Production_Data_vi.csv`. Bản đọc dễ duyệt: `Dialogue_Readthrough_vi.md`. Tình trạng là **bản biên tập ứng viên đã hoàn tất lượt viết**, chưa owner final sign-off, chưa lồng tiếng hoặc nghiệm thu font/subtitle trong Unity. Đây là toàn bộ230lời của bảng hiện hành, không phải tuyên bố mọi NPC trong thế giới đã có hội thoại động ở mọi trạng thái.

## Phạm vi bất biến

Chỉ đổi `text_vi` và `localization_status` của197hàng. Giữ header/thứ tự230hàng và mọi field còn lại, gồm quest/title/graph/node/order/type/speaker, condition, text key, choice ID/group/label, next node, event, flag, voice reference và notes. Hai hàng CHOICE cùng node C3-05 vẫn có PUBLISH/COUNCIL riêng và flags cũ; không tạo kết thúc hoặc thưởng mới.

Source baseline bất biến: commit `04d352be1324ce0f132f9e4edcde86c7b83ef4dc`. Tool kiểm trực tiếp Git object này, không chỉ so số liệu tự ghi trong report. Source logic SHA và từng text hash trước edit được lưu ở `Tools/NarrativeReview/baseline_20261029.json`.

Có một sửa copy liên quan ngoài CSV: beat SQ-SH-05 đổi “Ba dụng cụ” thành “Bốn dụng cụ” để khớp objective4dụng cụ vốn có trong Quest Spec/CSV. Không đổi objective, recipe, gameplay count hoặc schema.

## Giọng và tiến trình tuyến chính

| Phần | Quyết định biên tập |
|---|---|
| Lâm Triều | Quản đốn Mộc muốn tìm người trong đội; rìu/thuốc/cầu là đời sống nghề. Hạ Mặc đối chiếu tên ghi tử trận với dấu rừng. Tạ nhận chữ ký của mình sau ba ký ức, không được một câu nói tự xóa trách nhiệm |
| Sa Hỏa | Sầm lo nước tới người chờ và nhận phần sổ của mình. Y sĩ đưa thợ ra trước khi hỏi họ ở lại vì gì. Nhật ký giữ cả việc Cơ từng giúp lẫn dấu sửa lượng nước, không ghép thành biện hộ |
| Trấn Sơn | Người dẫn dân lo đủ người qua cổng; trinh sát chia vị trí/cứu hộ; đội trưởng giữ lương/cửa/đường sơ tán. Tống nói như người tin vào một mệnh lệnh duy nhất rồi nhận mình biết lệnh giả, không nói kiểu NPC nhờ người chơi đánh chính mình |
| Bạch Uyên | Dẫn lặn giữ người và lối về; ký ức đời thường đi cùng phế tích. Hạ Mặc hỏi sự đồng ý trước khi chép, phân trách nhiệm năm phái sau đối chiếu. Mẫu Xà là linh thú giữ lõi, không gánh thay tội người ký và xóa hồ sơ |
| Đại Ngũ Mạch | Ly An giữ tin giữa nhiều đội, không quy hết công cho avatar. Tạ ở lại giữ đường và làm chứng. Cơ kể cả giúp nước lẫn điều mình giấu, vẫn giữ ý muốn kiểm soát để người chơi có lý do phản đối. Kết thúc giữ việc Cơ ổn định máy rồi chịu xét xử, Tạ sống và có trách nhiệm; đường thư có chiều hồi âm |

Ly An/y sĩ/dẫn lặn/quản đốn/ngư phủ dùng tôi/bạn; thầy, Hạ Mặc, Tạ, đội trưởng và các nhân vật quyền lực dùng ta/ngươi theo giọng hiện hành. Không gán giới tính/mặt/giọng cho avatar; không thêm quan hệ huyết thống, nguyên tố thứ sáu, tiên tri toàn tri hoặc du hành thời gian để giải thích điều chưa biết.

## Lời nhiệm vụ phụ

Mỗi quest phụ có mục tiêu và kết quả riêng, không còn ba câu mẫu chỉ nhắc lại tên quest. Bến Mưa có dấu vá lưới, niêm thư và chỗ bát chờ; Thanh Lạc có nhẫn sửa/cờ/bảng tin; Lâm Triều có chim, ký ức riêng và dây cầu; Sa Hỏa có đường nước, thợ học việc và nhịp nghỉ; Trấn Sơn có tên trên bia, thư xin lỗi và kèn sơ tán; Bạch Uyên có biển số nhà, đồ cứu hộ và người nghỉ nghề; Vực có dấu đo/đồng hồ/bản ghi; hậu truyện có người giữ trụ, bữa chung và thư hồi âm.

Giữ mọi objective/count trong nguồn chuẩn. Lời thoại không cho phép mở thư trái yêu cầu, giết cá hiếm, đánh cây non, thiếu hàng vẫn nhận đủ, ép tha thứ hoặc bắt NPC nghỉ hưu quay lại lao động. Nhịp/âm thanh có mô tả hoặc dấu nhìn tương đương. Không biến thú cứu được thành pet mới, bữa ăn thành buff quyền lực hoặc side quest thành thưởng Cổ Vật.

## Thời điểm tiết lộ và ranh giới cần giữ khi tích hợp

| Nhóm | Giới hạn của copy/adapter |
|---|---|
| C2-02/04/05 | Tên tử trận, chữ ký Tạ và nhật ký Cơ được kết luận ở READY sau mục tiêu tương ứng; CLUE chỉ gợi điều cần quan sát |
| C3-02/03 | Tình thế thợ và bản khắc được nói theo điều đã thấy; không lấy lòng tốt cũ làm kết luận Cơ vô tội |
| C3-05 lựa chọn | Lời hỏi có dạng “Nếu chọn…”, không khẳng định đã công bố/đã giao khi guard hiện chỉ QUEST_ACTIVE. Giữ preference/flag không đồng nghĩa đã thực hiện công bố. Khi dựng scene sau trận, runtime phải kiểm đã tới checkpoint/bằng chứng phù hợp trước phát cảnh công bố; copy không tự thêm guard hoặc callback |
| C4-02/05 | Dấu sáp, thời điểm và thư lệnh dẫn tới người ra lệnh. Tống nhận biết lệnh giả ở READY; không gọi hai sứ giả là đồng phạm chỉ vì họ cầm giấy |
| C5-03/04 | Hồ sơ xóa người sống sót và trách nhiệm các phái chỉ nói sau đối chiếu. Không ép phát lại mọi ký ức; không coi hòa giải là tha bổng |
| SQ-BU-04/SQ-VN-05 | Vỏ ốc giữ sinh hoạt, bản ghi Cơ giữ đúng cả lượt im lặng; không nhét lời thú tội/C6-04 vào side quest có guard sớm hơn |
| SQ-DM | Lời sau raid phải dùng availability/phase hậu truyện đúng của C6-05; một cell QUEST_AVAILABLE không tự chứng minh dependency đã được cài trong runtime |
| Tống/Cơ và thầy macro | Tách đối thoại/encounter phase đúng lúc; giữ vai NPC hiện có, không nói với một actor đã despawn hoặc tự đổi macro thành class cụ thể |

Graph baseline3node/quest vẫn là hợp đồng dữ liệu cũ. Đọc CLUE, chọn thoại, skip/replay/hết video không được tự cấp progress/reward. Lời ở READY tránh báo tiền/đồ đã vào túi; UI/audio thành công lấy từ commit authoritative. Những guard/phase này là yêu cầu tích hợp theo nguồn truyện, không được gọi là đã chạy chỉ vì copy đã sửa.

## Dùng cho Muse và client

Muse lấy câu từ CSV hoặc bản đọc mới theo đúng text_key/speaker/condition; giữ2choice label/cờ hiện có. Phần thoại mới không yêu cầu render197video. Storyboard/cinema chỉ lấy đoạn đã mở theo revealTier, có skip/đọc lại và bản recap; actor avatar giữ tùy chỉnh. Không công bố trailer với lời kết thúc C5/C6.

Voice_asset_id vẫn nguyên trạng; không tự điền voice ID hoặc coi bộ DSP #55 là thoại có lời. Chuẩn bị casting/thu âm sau review copy, ghi source/take/độ dài/subtitle thật. Lời không có giới hạn2dòng được chứng minh: UI phải wrap/scroll/chuyển khối theo font và safe area thật, không ép auto-advance dựa duy nhất vào số ký tự.

## Kiểm tra và tái tạo

```powershell
python Tools/NarrativeReview/validate_full_editorial.py --write
python Tools/NarrativeReview/validate_full_editorial.py
python Implementation/Tools/validate_narrative.py
python Implementation/Tools/validate_content.py
python Implementation/Tools/validate_contracts.py
```

Tool đầu xuất report/readthrough sau khi đối chiếu baseline Git; lệnh không --write kiểm drift. CI checkout đủ lịch sử, không cần Unity/LFS media để kiểm lời. Nếu shallow clone chưa có commit baseline, fetch lịch sử trước. Thay đổi logic/ID có chủ ý về sau cần một baseline/review mới, không cập nhật hash để che edit ngoài phạm vi.

Kiểm230hàng/76quest,197copy mới,33copy cũ bất biến, mọi field logic/order/choice label/flag, NFC, template và ID kỹ thuật trong lời, trùng nguyên đoạn và hash export. Câu hỏi chung của2hàng CHOICE được phép lặp đúng node/group; bản đọc hiển thị một câu hỏi cùng2lựa chọn, không biến thành hai node mới. Report ở `Implementation/Reports/Dialogue_Editorial_Full_20261029.json`. Các phép kiểm không chứng nhận chất lượng diễn xuất, font metrics hoặc runtime quest/reveal guards.
