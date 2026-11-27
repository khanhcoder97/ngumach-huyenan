# Thăng Long — Con dấu qua phố — kịch bản đầy đủ, bản biên tập 2026-10-31

Bản thảo để đọc và biên tập; giữ mọi nhánh, gồm lựa chọn khác nhau nên đây không phải một lượt chơi tuyến tính. Mở reading room để đọc theo nhánh. Runtime activation OFF; không thay CSV/quest graph hoặc cinema source.

## C1-06


### tl_arrival

> scene:TL06_ARRIVAL

> quest:C1-06

> kind:SCENE

> guard:SERVER_C1_05_COMMITTED_AND_C1_06_AVAILABLE

Một xe hàng dừng ngang đường khi người đánh xe xuống kê lại bánh. Dòng người tách thành hai nhánh, vòng qua xe rồi nhập lại trước mái chợ. Từ đây vẫn nhìn thấy tầng trên của khán đài; tiếng thử trống tới chậm hơn động tác dùi hạ xuống.

Hạ Mặc nép cuốn sổ vào ngực để một sọt cá đi qua. Người bán nhắc ông tránh vệt nước. Ông nhích sang, phát hiện mình vẫn đứng trên đúng vệt ấy.

Hạ Mặc: Ta tưởng vũng này ngắn hơn.

Ông mượn một chiếc ghế từ quầy gần đó, kê dưới mái hiên để mở bọc giấy mang từ Thanh Lạc. Mẫu phù nằm giữa hai tờ lót, mép có một vết lõm đôi.

Hạ Mặc: Bốn người có thể kể bốn chuyện về tờ này. Ta cần biết nó đã đi qua những tay nào.


- Lựa chọn: Bắt đầu từ người bán phù?
    Hạ Mặc: Bắt đầu từ hóa đơn. Nếu người bán không còn ở đây, giấy vẫn chỉ được một chặng đường.

    -> tl_brief


- Lựa chọn: Sao lại mang mẫu ra giữa chợ?
    Hạ Mặc khép bọc giấy khi một giọt nước từ mái rơi sát mép.

    Hạ Mặc: Vì người giữ sổ chưa chịu bỏ quầy. Và ta đã hẹn sẽ mang tới.

    -> tl_brief


- Lựa chọn: Tôi muốn đi xem thành trước.
    Hạ Mặc cất mẫu, chỉ vào mái vải sẫm bên kia dòng xe.

    Hạ Mặc: Cứ đi. Quay lại tìm ta ở đây. Chưa có ai bị giữ vì tờ giấy này.

    -> tl_pause




### tl_pause

> scene:TL06_PAUSE

> kind:SCENE

Trên tầng khán đài, người thợ căng lại một dải vải. Dưới đường, khách vừa dừng xem đã phải nhấc chân tránh xe. Bạn có thể rời cuộc trao đổi; người giữ quầy vẫn tiếp tục việc của họ.


- Lựa chọn: Trở lại nghe Hạ Mặc -> tl_brief

- Lựa chọn: Về bàn đọc -> reading_room



### tl_brief

> scene:TL06_BRIEF

> kind:SCENE

Hạ Mặc: Sổ chợ, dấu lò, trang lưu trữ. Xem riêng từng thứ rồi hãy đặt cạnh nhau. Ta sẽ chờ báo cáo, kể cả khi chúng không khớp với điều ta nghi.

BẢN ĐỌC · Nhiệm vụ có năm bước nguồn: hóa đơn → dấu lò → lưu trữ → đối chiếu → báo cáo. Bản đọc sau đây vào đúng các checkpoint mô phỏng; xem hoặc chọn câu thoại không cấp tiến độ live. Hạ Mặc và Sầm ở Thăng Long là staging cần phase/anchor adapter: registry hiện đặt họ ở Thanh Lạc/Sa Hỏa, không tự dịch chuyển actor canonical.


Chuyển cảnh: tl_route.




### tl_route

> scene:TL06_ROUTE

> kind:CHECKPOINT

> guard:SERVER_C1_06_ACTIVE

TRACKER · Chọn điểm đang đọc. Có thể quay lại xem vật chứng; các lựa chọn không tạo vật phẩm mới hoặc thưởng. Trong game phải tới anchor đã review và nhận xác nhận tương tác.


- Lựa chọn: {tl_step == 0} Mô phỏng: tới quầy và xin xem hóa đơn chợ -> tl_ledger

- Lựa chọn: {tl_step == 1} Mô phỏng: mang bản đối chiếu tới dấu lò -> tl_forge

- Lựa chọn: {tl_step == 2} Mô phỏng: xin tra trang lưu trữ -> tl_archive

- Lựa chọn: {tl_step == 3} Mô phỏng: đủ ba nguồn, đặt cạnh nhau để đối chiếu -> tl_compare

- Lựa chọn: {tl_step == 4} Mô phỏng: server đã xác nhận đối chiếu, trở lại báo Hạ Mặc -> tl_report

- Lựa chọn: {tl_step > 0} Đọc lại hóa đơn và dòng bên lề -> tl_ledger

- Lựa chọn: Tạm rời bản đọc -> reading_room



### tl_ledger

> scene:TL06_LEDGER

> kind:SCENE

> guard:SERVER_C1_06_LEDGER_INTERACT_AVAILABLE

Sầm Chủ Quỹ giữ chiếc cân bằng một đầu ngón tay. Đĩa bên phải chưa ngừng lắc, người mua đã đưa thêm một đồng; ông đẩy đồng ấy trở lại bằng cạnh cuốn sổ.

Sầm Chủ Quỹ: Chờ nó đứng đã. Cân đang múa mà trả tiền thì hôm nay tôi bán được cả gió.

Người khách mang hàng đi. Sầm kéo ghế ra nhưng không ngồi, đặt sổ vào khoảng trống vừa có trên quầy.

Sầm Chủ Quỹ: Các vị tìm lô giấy. Tôi giữ cả hóa đơn lẫn khoản phải bù. Muốn xem cái nào trước?


- Lựa chọn: Hóa đơn của chuyến hàng.
    Ông đặt ngón tay bên cạnh một dòng, chừa đủ chỗ để bạn đọc. Tiền hàng và phí chở nằm ở hai cột. Dòng xác nhận giao chỉ có một dấu lò, không có chữ ký người làm phù.

    Sầm Chủ Quỹ: Giao giấy, không giao phù. Lúc xe rời quầy, những tờ ấy còn trắng.

    -> tl_ledger_question


- Lựa chọn: Khoản phải bù là gì?
    ~ tl_margin_seen = true

    Sầm lật ngược một góc trang. Ở bên lề có khoản nước cho đoàn xe, viết chen tới sát đường đóng chỉ. Cột thu không có dòng tương ứng.

    Sầm Chủ Quỹ: Phía nhận trả tiền giấy. Nước dọc đường tôi ứng. Họ đang cãi khoản ấy, nên sổ chưa khép được.

    -> tl_ledger_question




### tl_ledger_question

Hạ Mặc đã dặn giữ cả những dòng khó giải thích. Mép trang bên lề dày lên vì từng được gấp riêng.


- Lựa chọn: Cho tôi chép cả phần bên lề.
    ~ tl_margin_seen = true

    Sầm Chủ Quỹ: Chép đủ thì tốt. Nhất là chỗ họ còn nợ tôi.

    Ông vuốt mép giấy ra, để lộ cả khoản không được bên nhận chấp thuận. Ông không xin bạn bỏ dòng ấy.

    -> tl_ledger_close


- Lựa chọn: Ông ứng nước để chuyến hàng được đi?
    Sầm Chủ Quỹ: Để người đi cùng xe có nước. Có một người quay về trước xe, tôi vẫn tính phần của anh ta trong khoản ứng.

    Ông chấm vào tổng tiền.

    Sầm Chủ Quỹ: Thế mới sinh chuyện. Bên nhận chỉ đếm người tới nơi.

    -> tl_ledger_close


- Lựa chọn: Dấu lò chứng minh người ở lò làm phù giả?
    Sầm Chủ Quỹ: Nó chứng minh xe đã ghé lò. Lò còn sửa vành bánh, cân lại hàng. Muốn hỏi họ nhận cái gì, cứ mang cả trang đi hỏi.

    Ông đẩy sổ ra thêm một chút. Chiếc cân đứng yên sau lưng tay ông.

    -> tl_ledger_close




### tl_ledger_close

Sầm giữ lại sổ gốc, cho bạn xem chỗ ghi chuyến hàng lần nữa. Một người chở hàng ghé vai qua quầy, hỏi còn phải đợi bao lâu. Sầm nhìn thùng nước trên xe trước khi trả lời.

Sầm Chủ Quỹ: Đổ thêm nửa thùng. Ghi vào phần tôi.

{tl_step == 0:

    ~ tl_step = 1

}

BẢN ĐỌC · Bản sao, khoản nước và bút tích là đạo cụ kể chuyện ứng viên, không phải inventory item, khoản nợ kinh tế hoặc nhân vật quest mới. Người chở hàng dùng archetype NPC_TL_CIVILIAN_01; không tạo tên/placement mới. Dòng bên lề không chứng minh Sầm vô tội, cũng không chứng minh ông tổ chức phù giả.


Chuyển cảnh: tl_route.




### tl_forge

> scene:TL06_FORGE

> kind:SCENE

> guard:SERVER_C1_06_FORGE_INTERACT_AVAILABLE

Thợ phụ Bách Công hơ mũi kẹp ở rìa lò, gạt một mẩu kim loại đang dính vào đầu. Khi nhìn dấu trên bản chép, người thợ lật bàn tay làm động tác đợi, đưa nốt mẩu ấy vào khay mới nói.

Thợ phụ Bách Công: Để nguội rồi hãy đặt giấy ở đây. Bàn vẫn ăn lửa.

Trên mặt dấu mẫu có một rãnh nhỏ. Bên cạnh, mẫu phù từ Thanh Lạc có hai vết lõm nông nằm đều nhau. Hai hình giống nhau ở vòng ngoài, khác ở chỗ nét kết thúc.


- Lựa chọn: Đặt hai dấu cạnh nhau dưới ánh sáng.
    Người thợ nghiêng tấm chắn lửa để ánh sáng rọi ngang. Vết sứt của dấu mẫu kéo thành một gờ; ở phù, hai vết lõm kết thúc phẳng.

    Thợ phụ Bách Công: Cái sứt này kéo giấy khi nhấc. Hai chỗ kia ép xuống cùng lúc. Tôi nói được tới đó thôi.

    -> tl_forge_after


- Lựa chọn: Chỉ cần biết có giống hay không.
    Thợ phụ Bách Công: Vòng ngoài thì giống. Muốn lấy một chữ giống mang về, tôi không ký.

    Người thợ quay dấu lại cho bạn nhìn rãnh nhỏ, rồi chỉ hai vết trên phù.

    -> tl_forge_after


- Lựa chọn: Đọc mô tả chi tiết thay cho nhìn dấu nhỏ.
    TRACKER · Dấu lò: một gờ xước kéo ra mép. Mẫu phù: hai vết ép đều, đáy phẳng. Vòng ngoài tương tự; phương thức tạo nét khác. Mô tả bằng chữ/icon phải có cùng thông tin với ảnh phóng đại, không cần phân biệt màu hoặc nghe âm.

    -> tl_forge_after




### tl_forge_after

Người thợ chỉ lớp giấy sát vết ép. Một sợi xanh mỏng mắc vào thớ thô. Khi bạn dịch tờ giấy, sợi ấy đi theo; nó không nằm trên mặt bàn.

Thợ phụ Bách Công: Đừng phủi. Tra nơi giữ mẫu giấy trước. Tôi không biết cái cây nào cho thứ này.

Tiếng búa từ gian bên dừng một nhịp, rồi tiếp bằng hai tiếng ngắn. Người thợ nhấc lại chiếc kẹp, đợi bạn gấp giấy xong mới mở tấm chắn lửa.

BẢN ĐỌC · Thợ phụ dùng NPC_TL_CIVILIAN_06 trong khu Bách Công, không gán NPC_BLACKSMITH của Thanh Lạc sang đây. So dấu chỉ củng cố dấu gia công đã được phép biết ở C1-03; chưa nêu Lâm Triều từ một sợi xanh.


Chuyển cảnh: tl_route.




### tl_archive

> scene:TL06_ARCHIVE

> kind:SCENE

> guard:SERVER_C1_06_ARCHIVE_INTERACT_AVAILABLE

Quan thư lầu đặt một thanh gỗ lên mép trang trước khi buông tay. Người ngồi bàn bên đang chờ; chồng giấy cạnh khuỷu tay họ có vết nước tròn từ một chiếc chén đã được nhấc đi.

Quan thư lầu: Xem bản lưu ở bàn này. Đừng mang ra hiên, gió lật lẫn thứ tự.

Trên trang lưu có ô ghi nhận vật liệu và ô người chuyển. Một đường sửa chạy qua phần ngày giao; nét cũ còn thấy dưới lớp mực mới.


- Lựa chọn: Ngày này đã bị sửa.
    Quan thư lầu: Đúng. Dưới mép trang có ghi lý do nộp bổ sung. Ta sẽ giữ mở cả phần ấy cho bạn đọc.

    Người giữ sổ không che nét cũ. Hai lần ghi nhận cách nhau một chuyến xe; tên người nhận trong hai ô không đổi.

    -> tl_archive_after


- Lựa chọn: Ai đã cho phép chuyến hàng đi?
    Quan thư lầu dò tới cột cuối, dừng trước khi đưa ngón tay qua tên người.

    Quan thư lầu: Đây là người tiếp nhận bản kê. Cột này không ghi người cho phép làm phù. Cần tra đúng câu hỏi trước.

    -> tl_archive_after


- Lựa chọn: Xin phần mô tả vật liệu trước.
    Quan thư lầu đẩy thanh gỗ sang, giữ ô vật liệu phẳng dưới ánh cửa. Bên cạnh có mẫu sợi đã khô, mép gãy xơ ra giống phần đang mắc trong giấy của bạn.

    -> tl_archive_after




### tl_archive_after

Quan thư lầu: Có thể chép mẫu và lời ghi nhận. Đừng xé mẫu ra để thử lửa. Tờ này chỉ còn một bản lưu.

Mùi giấy khô lẫn mùi áo vừa đi mưa vào. Khi bạn cúi ghi, tiếng người hỏi đường ngoài hiên kéo dài qua khung cửa. Trong lầu, người chờ bàn bên đã bắt đầu xếp lại giấy của mình.

BẢN ĐỌC · Trang lưu và mô tả mẫu là staging evidence candidate. Không suy ngày sửa thành tẩy hồ sơ tháp ở C1-05 hoặc phong tỏa ba mươi năm. Actor dùng NPC_COURT_ARCHIVIST hiện có; bàn/giấy là set dressing, chưa tạo world node riêng.


Chuyển cảnh: tl_route.




### tl_compare

> scene:TL06_COMPARE

> kind:SCENE

> guard:SERVER_C1_06_LEDGER_FORGE_ARCHIVE_CONFIRMED

Bạn đặt bản chép hóa đơn cạnh bản ghi dấu lò, rồi tới phần mô tả mẫu giấy. Ba dòng giao nhận nối được các chặng của cùng lô. Chúng chưa nối được bàn tay làm phù với một người cụ thể.


- Lựa chọn: Đối chiếu sợi nhựa với mẫu lưu.
    TRACKER · Hai mẫu có cùng cấu trúc sợi và vết bám mô tả. Bản lưu ghi loại nhựa này dùng trong giấy từ Lâm Triều. Kết quả mở hướng tìm nguồn giấy; chưa xác định ai sửa phù hoặc ai ra lệnh.

    -> tl_compared


- Lựa chọn: Tổng hợp chỗ nào vẫn chưa có câu trả lời.
    TRACKER · Hóa đơn ghi giấy trắng; dấu lò ghi một điểm nhận; trang lưu nhận diện vật liệu. Khoảng sau khi giấy rời lò chưa có chứng cứ về người gia công phù. Đối chiếu mẫu nhựa dẫn về Lâm Triều; người ký các ô nhận hàng chưa được chứng minh biết nội dung cuối.

    -> tl_compared




### tl_compared

> scene:TL06_COMPARED

> kind:SCENE

> cinema:CIN_006

> guard:SERVER_C1_06_COMPARISON_CONFIRMED_BEFORE_REPORT

Hạ Mặc tới dưới mái hiên khi bạn đã gấp đủ ba bản chép. Ông không gom chúng thành một xấp ngay. Ông đặt từng tờ theo chiều chuyến hàng đã đi, chừa khoảng trống ở chặng chưa biết.

Hạ Mặc: Tới đây ta theo được. Chỗ trống này giữ nguyên.

Một chiếc xe lại đi ngang, che khuất quầy Sầm trong chốc lát. Qua khoảng giữa hai bánh xe, ông vẫn đang cân hàng cho một người khác.

BẢN ĐỌC · CIN_006 là đoạn dựng tùy chọn18giây sau đủ ba clue và đối chiếu, trước báo cáo; có thể bỏ qua hoặc đọc recap này. Bản dựng nhớ lại các điểm vừa xem, không bắt ba NPC đứng cùng nhau. Skip/ended không tự hoàn thành bước báo cáo.


Chuyển cảnh: tl_route.




### tl_report

> scene:TL06_REPORT

> kind:SCENE

> guard:SERVER_C1_06_READY_TO_TURN_IN

Hạ Mặc đặt một tờ trắng bên cạnh các bản chép.

Hạ Mặc: Ta sẽ viết theo lời bạn. Kết luận trước, rồi tới điều chưa biết.


- Lựa chọn: Vật liệu dẫn về Lâm Triều. Chưa rõ ai làm phù.
    ~ tl_report_style = 1

    Hạ Mặc viết hai câu vào hai dòng riêng. Ông gạch một nét dưới chữ chỉ nơi đến, để trống ô người chịu trách nhiệm.

    -> tl_report_margin


- Lựa chọn: Những người ghi trong sổ chưa chắc biết thứ họ chuyển.
    ~ tl_report_style = 2

    Hạ Mặc: Ta ghi là chưa có bằng chứng họ biết. Chữ ấy còn để được chỗ cho việc tra tiếp.

    Ông đọc lại câu vừa viết để bạn nghe, rồi chờ phần nguồn giấy.

    -> tl_report_margin


- Lựa chọn: Sầm đã bán lô giấy, nên ông ta phải là người làm giả.
    ~ tl_report_style = 3

    Hạ Mặc đặt bút ngang tờ trắng.

    Hạ Mặc: Chỉ cho ta dòng nào ghi ông ấy làm phù.

    Khi ba bản chép được mở lại, ô giao nhận vẫn chỉ ghi giấy. Khoảng trống sau chặng lò vẫn còn đó.

    Hạ Mặc: Ta giữ nghi vấn. Ta chưa viết nó vào chỗ kết luận.

    -> tl_report_margin




### tl_report_margin

{tl_margin_seen:

    Bạn đặt phần bên lề cạnh hóa đơn. Hạ Mặc dịch tờ trắng xuống để chép đủ khoản ứng nước và phần bên nhận không chấp thuận.

    Hạ Mặc: Dòng này làm sổ khó cân hơn. Ta vẫn giữ.

- else:

    Hạ Mặc nhìn mép bản chép, nơi phần giấy gấp chưa được mở ra.

    Hạ Mặc: Ở quầy còn một khoản ghi bên lề. Trước khi khép báo cáo, ta muốn nghe cả phần ấy.

    TRACKER · Bản đọc mở lại phần thiếu ngay dưới đây. Trong game, không lấy câu thoại này thay tương tác hoặc đặt lại quest credit; thiếu checkpoint phải hiển thị bước cần quay lại.

    Sầm Chủ Quỹ đã ghi phần nước ứng cho cả người quay về trước chuyến xe. Bên nhận không trả phần của người không tới nơi. Khoản ấy không được gộp vào giá giấy.

    ~ tl_margin_seen = true

}

{tl_report_style == 3:

    Hạ Mặc đặt bút lại giữa hai người, đầu ngòi quay về phía mình.

    Hạ Mặc: Bạn có muốn sửa câu vừa rồi không?

    + [Sửa: đã tìm được đường giấy đi, chưa tìm được người làm phù.]

        Hạ Mặc chép câu sửa, để nguyên câu đầu trong bản nháp và gạch một nét qua.

        -> tl_receipt

    + [Giữ nghi ngờ, ghi rõ đó là giả thuyết.]

        Hạ Mặc thêm một cột riêng, ghi điều cần xác minh bên dưới. Ông không đưa tên Sầm sang phần kết luận.

        -> tl_receipt

- else:

    Hạ Mặc đọc lại phần dẫn về Lâm Triều, rồi tới những người đã nhận giấy. Lần này, tên mỗi người nằm đúng cột việc họ được ghi là đã làm.

    -> tl_receipt

}




### tl_receipt

> scene:TL06_COMMIT

> kind:CHECKPOINT

> guard:SERVER_C1_06_TURN_IN_COMMITTED

TRACKER · Gửi báo cáo theo quest source;300Đồng, EXP, Huy hiệu Thanh Lạc và mở C2-01/route Lâm Triều chỉ hiện sau receipt authoritative. Không tự điền số EXP hoặc tạo reward item qua bản thảo. Pending/fullbag/error/replay thuộc gameplay adapter.


- Lựa chọn: Mô phỏng: đã nhận receipt báo cáo, đọc cảnh kết -> tl_end

- Lựa chọn: Về bàn đọc -> reading_room



### tl_end

> scene:TL06_END

> kind:SCENE

> guard:SERVER_C1_06_TURN_IN_COMMITTED

Hạ Mặc luồn ba bản chép vào hai bìa riêng. Một bìa để theo đường hàng, một bìa giữ những dòng phải quay lại hỏi. Ông đưa bạn xem dấu ghi nhận ở mặt ngoài trước khi cất.

Hạ Mặc: Lâm Triều. Ta sẽ xin tra nơi làm giấy trước. Bạn muốn về nghỉ thì cứ đi, ta còn phải trả lại một thứ.

Ông quay sang quầy Sầm. Chiếc ghế mượn từ lúc đầu vẫn ở dưới mái hiên, chân ngoài cùng dính một vệt nước. Ông nhấc ghế qua chỗ khô, chờ xe đi hết rồi mới băng đường.

Trên khán đài, dải vải đã được căng xong. Tiếng trống thử ngừng; từ quầy bên cạnh, một người gọi khách quay lại lấy tiền thừa.

KẾT TUYẾN BẢN ĐỌC · Giấy dẫn về Lâm Triều; kẻ làm phù và người điều phối chưa được nhận diện. Không cho xem Cơ, phong tỏa ba mươi năm hoặc lời thú nhận của Tạ trong cảnh kết/thumbnail.


- Lựa chọn: Đọc lại Con dấu qua phố -> tl_arrival

- Lựa chọn: Về bàn đọc -> reading_room

- Lựa chọn: Đóng bản đọc -> END
