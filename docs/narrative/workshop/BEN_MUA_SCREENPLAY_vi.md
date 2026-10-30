# Bến Mưa — kịch bản đầy đủ, bản biên tập 2026-10-31

Bản thảo để đọc và biên tập; giữ mọi nhánh, gồm lựa chọn khác nhau nên đây không phải một lượt chơi tuyến tính. Mở reading room để đọc theo nhánh. Runtime activation OFF; không thay CSV/quest graph hoặc cinema source.

## P00-01


### p01_rope

> scene:BM01_ROPE

> quest:P00-01

> kind:SCENE

> cinema:CIN_001

Nước mưa chảy qua các khe ván. Một sợi dây căng ngang bến rồi tuột khỏi cọc, quất vào chiếc giỏ tre bên chân Ly An. Cô giữ được đầu dây còn lại, nhưng kiện hàng ngoài mép đã xoay nửa vòng.

Ly An: Đầu kia! Giữ giúp tôi đầu kia!

Cô nhích gót giày lên một thanh ván. Nước ngập qua mũi giày, kiện hàng dừng lại. Ly An vẫn chưa nhìn người vừa tới.


- Lựa chọn: Giữ dây và kéo kiện vào -> p01_help

- Lựa chọn: Chỉ chỗ quấn dây quanh cọc -> p01_post

- Lựa chọn: Tôi đang đi vội. -> p01_hurry



### p01_help

Bạn kéo đầu dây về phía cọc. Ly An tranh thủ chèn giỏ tre dưới kiện hàng, rồi mới thả tay.

Ly An: Khoan, đừng kéo nữa. Mép dưới sắp bung.

Cô quỳ xuống, nhét lại lớp vải gói đang hở. Qua khe vải là miệng một chiếc bát sứ bọc rơm. Cô thử nhấc kiện, nghe bên trong một tiếng chạm rất khẽ.

Ly An: Còn nguyên. May thật.


Chuyển cảnh: p01_letter.




### p01_post

Ly An liếc theo tay bạn, vắt dây thêm một vòng quanh cọc. Kiện hàng nghiêng hẳn sang bên, nằm yên.

Ly An: Ừ, cọc này còn chắc. Tôi cứ tưởng nó cũng mục rồi.

Cô thử kéo lại sợi dây trước khi đứng lên. Đốt ngón tay đã trắng bệch vì siết lâu.


Chuyển cảnh: p01_letter.




### p01_hurry

Ly An: Vậy giữ một lúc thôi. Đủ để tôi buộc lại.

Cô ghì dây bằng khuỷu tay, cúi nhặt chiếc giỏ đã đổ. Cái giỏ cứ trượt khỏi tầm với. Khi cô ngẩng lên lần nữa, lời tiếp theo nhỏ hơn.

Ly An: Làm ơn.


- Lựa chọn: Quay lại giữ đầu dây -> p01_help

- Lựa chọn: Bỏ qua cảnh này để đọc nhiệm vụ khác -> reading_room



### p01_letter

> scene:BM01_LETTER

> kind:SCENE

Ly An phủi rơm khỏi tay áo. Cô lấy trong túi một lá thư bọc vải dầu. Niêm sáp có năm vạch chìm; vạch ở rìa mất dưới một giọt nước chưa khô.

Ly An: Ba kiện bị dòng nước đẩy dạt quanh đây. Chưa thấy ai tới nhận. Ông Khanh ở trước kho đang nhận đồ thất lạc. Bạn mang giúp tới đó được không?


- Lựa chọn: Cô không đi cùng sao?
    Ly An nhìn dọc mép bến. Cô vừa gom dây, vừa tìm một đầu dây khác trong đám lau.

    Ly An: Tôi xem còn kiện nào mắc bên dưới không. Mang nguyên niêm giúp tôi. Có ai hỏi người gửi thì bảo họ hỏi ông Khanh.

    -> p01_accept


- Lựa chọn: Trong thư có gì?
    Ngón tay cô dừng ở mép vải dầu.

    Ly An: Tôi chưa mở.

    Cô đưa lá thư ra, mặt niêm quay lên. Khi bạn nhận, cô vẫn giữ góc vải thêm một nhịp rồi mới buông.

    -> p01_accept


- Lựa chọn: Được, tôi mang tới kho.
    Ly An: Cảm ơn. Kiện nào buộc dây đôi thì đỡ từ dưới, đừng nhấc bằng nút.

    -> p01_accept




### p01_accept

> scene:BM01_PACKAGES

> kind:CHECKPOINT

> guard:SERVER_P00_01_ACTIVE_AND_PACKAGES_3

TRACKER · Nhặt đủ ba kiện hàng rồi mang thư còn niêm tới Tạ Vân Khanh. Trong game, tương tác và tiến độ do server xác nhận.

BẢN ĐỌC · Ba kiện có dấu buộc khác nhau: sợi chỉ sẫm cài trong nút, một miếng vải vá, hai vòng dây bẹ. Các dấu chỉ là trang trí candidate của những kiện đã có, không phải ba item mới.


- Lựa chọn: Mô phỏng: đã tìm đủ ba kiện và tới kho -> p01_khanh

- Lựa chọn: Đọc lại lời nhờ của Ly An -> p01_letter

- Lựa chọn: Về bàn đọc -> reading_room



### p01_khanh

> scene:BM01_RECEIPT

> kind:SCENE

> guard:SERVER_P00_01_READY_TO_TURN_IN

Tạ Vân Khanh đang kê một tấm ván dưới chân kiện hàng bị lún. Ông chỉ chỗ khô sát vách kho, chờ bạn đặt đồ xuống rồi mới hỏi.

Tạ Vân Khanh: Có ai theo nhận hàng không?


- Lựa chọn: Tôi chỉ gặp Ly An.
    Tạ Vân Khanh: Nó còn ngoài bến à?

    Ông nhìn qua vai bạn. Ly An đang tới, vạt áo ôm sát đầu gối.

    -> p01_seal


- Lựa chọn: Cô ấy đang tìm xem còn ai dưới bến.
    Tạ Vân Khanh: Ta đã dặn nó kiểm hàng trên bờ.

    Ông kéo một kiện ra khỏi lối đi, để chừa khoảng trống rộng hơn trước cửa kho.

    -> p01_seal




### p01_seal

Bạn đặt lá thư lên mặt kiện. Tạ Vân Khanh xoay nó để đọc tên ngoài bì, rồi úp tay lên phần niêm.

Ly An: Thư vẫn nguyên chứ?

Tạ Vân Khanh: Còn nguyên.

Ly An: Cháu hỏi lúc bác nhận được.

Tạ Vân Khanh rút tay ra. Năm vạch sáp hiện lại dưới mái hiên.

Tạ Vân Khanh: Lúc ta nhận cũng vậy.

Ông nhấc lá thư sang một bên khô hơn, không mở. Ly An bước tới xem ba nút dây, đếm bằng đầu ngón tay. Đến nút thứ ba cô mới thở ra.

{kept_distance:

    Ly An: Ban nãy tôi nói hơi gắt. Tay trơn quá, cứ giữ không nổi.

}

Tạ Vân Khanh: Để ta ghi nhận đồ đã về đủ. Bạn chờ một chút, ta còn muốn hỏi về mặt nước ngoài kia.

BẢN ĐỌC · Cảnh dừng trước kết quả trả nhiệm vụ. Thưởng và mở khóa chỉ hiển thị sau receipt server trong game; câu nói của NPC không xác nhận đã nhận tiền hay áo.


- Lựa chọn: Đọc tiếp Chuông không người -> p02_bank

- Lựa chọn: Về bàn đọc -> reading_room


## P00-02


### p02_bank

> scene:BM02_BANK

> quest:P00-02

> kind:SCENE

Ngoài mái kho, Ly An vắt nước khỏi tay áo. Tạ Vân Khanh ngừng ghi sổ khi tiếng giọt rơi từ mái thưa dần.

Tạ Vân Khanh: Ban nãy ở bến, có nghe gì ngoài tiếng mưa không?


- Lựa chọn: Có tiếng như chuông.
    Ly An: Tôi tưởng tiếng vòng sắt va cọc.

    Tạ Vân Khanh: Vòng sắt còn treo trên cọc chứ?

    Ly An quay đầu nhìn ra. Cọc ở quá xa để thấy rõ. Cô không trả lời.

    -> p02_request


- Lựa chọn: Tôi chưa để ý.
    Tạ Vân Khanh: Vậy đừng cố nhớ cho giống điều người khác kể. Đến chỗ đầm nông mà nghe lại.

    -> p02_request


- Lựa chọn: Bác đã nghe thấy gì?
    Ông khép cuốn sổ, kẹp ngón tay giữa hai trang.

    Tạ Vân Khanh: Ta muốn nghe bạn nói trước.

    -> p02_request




### p02_request

Tạ Vân Khanh: Có ba chỗ nước cứ cuộn về một điểm. Cá Linh tụ ở đó từ sớm. Giữ cho chúng không áp sát, rồi nhìn xem vòng nước chạy thế nào. Đừng xuống quá đầu gối.

Ly An: Cháu ở trên bờ trông người.

Tạ Vân Khanh gật đầu. Ông mở sổ lại, nhưng ngòi bút chưa chạm giấy.


Chuyển cảnh: p02_ripples.




### p02_ripples

> scene:BM02_RIPPLES

> kind:CHECKPOINT

> guard:SERVER_P00_02_RIPPLES_3_AND_CARPLING_4

TRACKER · Quan sát ba gợn nước, hạ bốn Cá Linh và quay lại báo cáo. Bản đọc không mô phỏng combat hoặc cấp credit.

BẢN ĐỌC · Tại mỗi điểm đã đặt trong map, người chơi có thể đọc mô tả hình/âm thay cho việc phải nghe đúng hoặc nhận ra pixel nhỏ. Lựa chọn dưới đây là điều bạn chú ý trong cùng hiện tượng, không đổi kết quả nhiệm vụ.


- Lựa chọn: Chú ý vòng nước
    ~ water_report = 1

    Một giọt mưa tạo những vòng tròn tản ra. Khi chạm chỗ nước sẫm, mép vòng dừng lại rồi lùi vào. Lá lau trôi ngang qua vẫn đi theo dòng bên ngoài.

    -> p02_bell


- Lựa chọn: Chú ý âm thanh
    ~ water_report = 2

    Trên bờ chỉ có tiếng cọc gỗ cọ vào dây. Khi bạn cúi gần mặt nước, tiếng ngân nối tiếp xuất hiện, mỏng và thấp. Bạn đứng thẳng. Phần ngân ấy mất đi.

    -> p02_bell


- Lựa chọn: Đọc mô tả đầy đủ, không dùng âm thanh
    ~ water_report = 3

    Vòng nước co về tâm. Bóng một vành chuông hiện dưới mép bến; phía trên không có vật tương ứng. Âm thanh nếu bật chỉ bổ sung tiếng ngân khi camera quan sát gần, không chứa manh mối độc quyền.

    -> p02_bell




### p02_bell

> scene:BM02_SOUND

> kind:SCENE

> cinema:CIN_002

> guard:SERVER_P00_02_RIPPLES_3

Một bóng tròn rung dưới nước. Khi vòng gợn đi qua, mép bóng vỡ thành những mảnh ngắn rồi liền lại. Ở trên, sợi dây treo cạnh cọc nằm im.

Ly An gọi từ bờ. Bạn quay lại; khi nhìn xuống lần nữa, chỗ đó chỉ còn bóng mái kho.

Ly An: Đừng đứng sát thêm. Có người vừa hụt chân ở đằng lau kia.

BẢN ĐỌC · Đoạn quan sát có thể là CIN_002 đã có trong pack, hoặc text/still fallback. Nó không thay số gợn nước hoặc combat objective.


- Lựa chọn: Mô phỏng: đã đủ objective, trở về trước kho -> p02_report

- Lựa chọn: Về bàn đọc -> reading_room



### p02_report

> scene:BM02_REPORT

> kind:SCENE

> guard:SERVER_P00_02_READY_TO_TURN_IN

Tạ Vân Khanh để sổ trên đầu gối, chừa một dòng trống.

{

- water_report == 1:

    Bạn kể lại vòng nước và chiếc lá lau.

    Tạ Vân Khanh: Chiếc lá vẫn trôi ra ngoài?

    Ông gạch một nét xuống dòng trống rồi dừng, chờ bạn nói hết.

- water_report == 2:

    Bạn kể âm thanh đổi khi cúi xuống.

    Tạ Vân Khanh: Cả ba chỗ đều thế?

    Ông nhìn ra đầm. Lần này, khi bạn gật, ông không ghi ngay.

- else:

    Bạn kể lại bóng vành chuông cùng những vòng nước co vào.

    Tạ Vân Khanh: Cái bóng ở sát bờ hay sâu hơn các chân cọc?

    Ông đặt bút xuống để nghe tiếp.

}

Ly An: Dưới đó có chuông thật à?

Tạ Vân Khanh: Ta chưa cho người xuống được.

Ly An: Vậy cháu ra chỗ người hụt chân trước. Họ vừa gọi thêm một người nữa.

Cô kéo lại quai túi. Tạ Vân Khanh cầm lá thư trên khay, luồn nó trở vào vải dầu rồi đưa cho cô.

Tạ Vân Khanh: Mang theo. Đừng để ướt niêm. Ta sẽ ra sau khi xong việc ở kho.

Ly An nhìn lá thư, nhìn ông, rồi cất vào túi mà không hỏi.

BẢN ĐỌC · Việc đổi người giữ thư là staging candidate nối tới P00-04; không tạo inventory command hoặc spawn/di chuyển NPC mới. Bảng custody và proposal ghi riêng trong gói tích hợp.


- Lựa chọn: Đọc tiếp Dưới mặt đầm -> p03_call

- Lựa chọn: Về bàn đọc -> reading_room


## P00-03


### p03_call

> scene:BM03_CALL

> quest:P00-03

> kind:SCENE

Một bàn tay vỗ vào mặt nước giữa đám lau. Ly An nằm rạp trên ván, giơ một đoạn dây xuống. Đầu dây vừa chạm tay người dưới đầm đã bị kéo lệch sang bên.

Dân chài: Đừng giật! Chân tôi vẫn mắc!

Ly An thu bớt dây, lùi khỏi mép ván để nhường chỗ cho bạn.

Ly An: Có hai người. Rễ quấn ở dưới, nhìn lá trên mặt nước sẽ không thấy đâu.


- Lựa chọn: Tôi giữ dây. Cô nhìn giúp chỗ mắc.
    Ly An: Chờ tôi chỉ rồi hãy kéo.

    Cô cúi hẳn xuống, một tay ghì mép ván. Từ đám lau xa hơn, tiếng người chèo đò lại gọi, lần này khản đặc.

    -> p03_roots


- Lựa chọn: Sóng đang dồn về đây.
    Ly An ngẩng lên. Nước giữa các chân lau lõm xuống, để lộ một vệt bùn sẫm.

    Ly An: Lên chỗ đất khô trước! Tôi giữ dây, bạn tránh sang bên đó.

    -> p03_roots




### p03_roots

> scene:BM03_ROOTS

> kind:CHECKPOINT

> guard:SERVER_P00_03_ROOTS_3_RESCUES_2_DODGE_1

TRACKER · Phá ba đám Rễ Nước, tương tác cứu hai người và tránh một đợt sóng. Credit và vị trí an toàn cần server xác nhận. Bản đọc không chốt loại KILL/INTERACT của rễ đang còn mâu thuẫn trong source.

BẢN ĐỌC · Tiếng sóng có mô tả hình tương đương. Đoạn sau đặt ở trạng thái đã cứu được người; không chạy thoại khi actor còn bị đánh.


- Lựa chọn: Mô phỏng: đã hoàn thành các bước cứu và lên bờ -> p03_first

- Lựa chọn: Về bàn đọc -> reading_room



### p03_first

> scene:BM03_FIRST_WITNESS

> cinema:CIN_003

> kind:SCENE

> guard:SERVER_P00_03_RESCUE_01_CONFIRMED

Người dân chài ngồi tựa lên khuỷu tay. Ông kéo ống quần khỏi cổ chân, nhăn mặt khi vải chạm da. Ly An đặt đầu dây vừa dùng xuống cạnh ông.

Dân chài: Người kia đâu rồi?

Ly An: Đang lên. Bác chờ, đừng đứng.

Dân chài nhìn bạn lâu hơn một cái nhìn cảm ơn.

Dân chài: Ban nãy tôi thấy bạn ở dưới ấy.


- Lựa chọn: Tôi vừa từ trên bờ xuống.
    Dân chài: Tôi biết. Bây giờ tôi thấy rồi.

    Ông xoa nước khỏi mắt, quay lại nhìn đúng chỗ bạn đã đứng.

    -> p03_second


- Lựa chọn: Tôi ở phía nào?
    ~ heard_first = true

    Dân chài chỉ vào một khoảng nước sát rễ.

    Dân chài: Bên đó. Cứ đứng, không đưa tay. Tôi gọi mấy lần.

    Ly An nhấc đoạn dây lên, cuộn nó để ông khỏi nhìn mãi vào phần đã mắc dưới nước.

    -> p03_second


- Lựa chọn: Bác có bị đau ở đâu nữa không?
    Dân chài: Chân phải. Tay vẫn được. Để tôi vịn cái cọc một lúc.

    Ông vịn vào chỗ gỗ khô, thử nhấc bàn chân khỏi bùn rồi lại đặt xuống.

    -> p03_second




### p03_second

> scene:BM03_SECOND_WITNESS

> kind:SCENE

> guard:SERVER_P00_03_RESCUE_02_CONFIRMED

Người chèo đò bò thêm một đoạn mới chịu ngồi. Bà giũ từng bàn tay, nhìn những vết rễ hằn đỏ quanh cổ tay áo.

Người chèo đò: Ai đứng dưới nước? Tôi chỉ thấy một người quay lưng ở giữa dòng.

Dân chài: Tôi nhìn rõ mặt.

Người chèo đò: Ông úp mặt vào bờ còn tôi nhìn ra ngoài. Chỗ ông chỉ là mạn đò của tôi.

Dân chài chực đáp, nhưng cơn ho làm ông gập người. Ly An đỡ khuỷu tay để ông khỏi chống xuống vết bùn trơn.


- Lựa chọn: Để từng người kể lại từ lúc trượt chân.
    Người chèo đò: Tôi xuống tháo dây neo. Nước chỉ tới đây.

    Bà chỉ một vệt trên ống chân, thấp hơn vết bùn mới.

    Người chèo đò: Bước tiếp theo thì chân đã không chạm đáy.

    {heard_first:

        Dân chài: Tôi nghe bà gọi. Đến lúc với tay ra, cái mặt ấy đã ở dưới chân tôi.

    - else:

        Dân chài: Tôi xuống sau. Tôi còn tưởng kéo được bà lên ngay.

    }

    -> p03_after


- Lựa chọn: Có thể nhìn hai người khác nhau.
    Người chèo đò lắc đầu, không hẳn đồng ý cũng không bác.

    Người chèo đò: Đò của tôi vẫn ngoài ấy. Tôi nhìn nó mỗi ngày, tôi biết hướng.

    Dân chài cúi xuống chỉnh lại ống quần. Lần này ông không tranh nói.

    -> p03_after


- Lựa chọn: Lên chỗ khô rồi hãy nói tiếp.
    Ly An đứng dậy, đưa tay cho người gần mình hơn. Người chèo đò vẫn ngoái về bến, đếm những cọc neo còn nhô trên nước.

    -> p03_after




### p03_after

> scene:BM03_SHORE

> kind:SCENE

> guard:SERVER_P00_03_READY_TO_TURN_IN

Ly An đợi hai người có chỗ vịn chắc rồi mới nhấc túi lên khỏi ván. Một góc vải dầu ướt dính vào tay cô. Cô gỡ ra thật chậm, xem phần niêm còn được che kín.


- Lựa chọn: Cô vẫn giữ lá thư.
    Ly An: Ông Khanh bảo mang theo.

    Cô kéo nắp túi xuống. Cái móc không ăn, cô phải thử lại.

    Ly An: Giúp tôi xem còn ai gọi không.

    -> p03_close


- Lựa chọn: Tôi sẽ kể cả hai lời với ông Khanh.
    Ly An: Để họ nghỉ rồi hỏi lại. Bác ấy vừa trượt lần nữa lúc tôi đỡ lên.

    Cô nhìn bàn tay dính bùn của mình, lau lên mảng áo vốn đã ướt.

    -> p03_close


- Lựa chọn: Im lặng, giúp cuộn dây.
    Hai người cuộn từ hai đầu. Đến đoạn giữa bị rễ siết, Ly An thử gỡ nút, rồi để nguyên vết thắt trong cuộn dây.

    -> p03_close




### p03_close

Từ phía kho có người gọi Ly An. Cô giơ tay đáp, chờ người dân chài thử đứng được rồi mới bước khỏi ván.

Ly An: Tôi sang báo chỗ này đã kéo được người lên. Bạn đừng xuống tìm cái bóng một mình nhé.

BẢN ĐỌC · Kết quả trả quest chỉ xuất hiện sau receipt. Lời kể không tạo xác nhận avatar từng ở đây, huyết thống hoặc ký ức tiền kiếp. Hai rescue actors vẫn dùng ID hiện có; visibility source đang mâu thuẫn P00-03/P00-04 cần adapter review.


- Lựa chọn: Đọc tiếp Người giữ bờ -> p04_depart

- Lựa chọn: Về bàn đọc -> reading_room


## P00-04


### p04_depart

> scene:BM04_DEPART

> quest:P00-04

> kind:SCENE

Tạ Vân Khanh đã ra khỏi mái kho. Ông nhìn cuộn dây sũng nước trong tay Ly An, rồi nhìn đoạn bờ dẫn tới Đầm Chuông.

Tạ Vân Khanh: Ta cần xem chỗ nước lõm. Hai người đi được nữa không?

Ly An: Cháu đi được.

Tạ Vân Khanh: Ta hỏi cả bạn ấy.


- Lựa chọn: Tôi đi cùng Ly An.
    Ly An chuyển cuộn dây sang tay bên kia, chừa một bên vai để luồn qua đám lau.

    Ly An: Tôi biết đoạn đầu. Tới chỗ cầu gỗ thì đi chậm thôi.

    -> p04_wave_one


- Lựa chọn: Có thể đợi người vừa cứu nghỉ thêm không?
    Tạ Vân Khanh: Họ ở lại bến. Ta không đưa họ xuống lần nữa.

    Ông chỉ một lối bờ cao hơn. Ly An sửa lại quai túi, đợi bạn bước lên trước.

    -> p04_wave_one




### p04_wave_one

> scene:BM04_FIRST_HOLD

> kind:CHECKPOINT

> guard:SERVER_P00_04_CHECKPOINT_80_WAVE_1_CLEAR

TRACKER · Hộ tống Ly An qua hai chặng, mỗi chặng có một đợt ba quái. Chết hoặc thất bại trở về checkpoint theo server; không phát lại credit/thưởng bằng lời thoại.

BẢN ĐỌC · Đọc cảnh nghỉ sau khi server xác nhận wave đầu đã sạch và không có nguy hiểm mới. Tọa độ checkpoint giữ source, không dời actor để diễn cảnh.


- Lựa chọn: Mô phỏng: giữ được chặng đầu -> p04_knot

- Lựa chọn: Về bàn đọc -> reading_room



### p04_knot

> scene:BM04_KNOT

> kind:SCENE

Ly An quỳ một gối, tháo đầu dây buộc túi đã ngấm nước. Cô kéo mãi mà nút càng siết. Bên kia bờ, một tiếng gỗ gãy rơi xuống đầm.

Ly An dừng tay, nghe. Không còn tiếng nào tiếp theo.


- Lựa chọn: Tôi giữ túi. Cô gỡ đi.
    ~ held_letter = true

    Cô đặt túi lên hai bàn tay bạn, lật đầu dây vòng qua nút. Mùi vải dầu ẩm và rơm ướt lẫn vào nhau. Lá thư nằm sát lớp lót, mặt có sáp quay vào trong.

    Ly An: Đừng nghiêng. Tôi buộc lại ngay.

    -> p04_talk


- Lựa chọn: Cắt nút rồi buộc đoạn khác được không?
    Ly An kéo một nhánh dây, thử độ dài còn lại.

    Ly An: Được. Đầu này vẫn còn đủ.

    Cô đổi cách buộc, lần này để nút nằm ở ngoài nắp túi.

    -> p04_talk


- Lựa chọn: Đợi cô buộc xong, nhìn chừng bờ nước.
    Mặt đầm gần bờ phẳng lại. Chỉ khi một con côn trùng chạm xuống, bạn mới thấy những vòng nước vẫn đang đi vào trong.

    -> p04_talk




### p04_talk

Ly An: Hồi nãy người chèo đò hỏi tôi còn thấy đò của bà ấy không. Tôi cứ bảo bà lên bờ đã.

Cô kéo thử quai túi, lần đầu được một nút chắc.


- Lựa chọn: Cô có quay lại xem không?
    Ly An: Có. Dây neo chưa đứt. Chỉ là tôi chưa nói được với bà ấy.

    Cô nhìn ngược về bến một lần, rồi đứng lên.

    -> p04_wave_two


- Lựa chọn: Tôi cũng không nhìn rõ ngoài đó.
    Ly An: Vậy lát nữa đứng ở bờ cao thử xem. Đừng xuống nữa.

    {held_letter:

        Cô nhận lại túi từ tay bạn bằng cả hai tay, đeo lên vai rồi chừa một khoảng cho bạn đi qua.

    }

    -> p04_wave_two


- Lựa chọn: Đi tiếp thôi.
    Ly An gật, nhặt cuộn dây. Có một vòng cô để tuột xuống cỏ, phải cúi lấy thêm lần nữa.

    -> p04_wave_two




### p04_wave_two

> scene:BM04_SECOND_HOLD

> kind:CHECKPOINT

> guard:SERVER_P00_04_CHECKPOINT_120_WAVE_2_CLEAR

TRACKER · Giữ chặng thứ hai trước khi tới Đầm Chuông. Bản đọc chuyển cảnh sau xác nhận wave thứ hai đã sạch; không mô phỏng đường đi hoặc boss activation.


- Lựa chọn: Mô phỏng: đã tới chặng nghỉ thứ hai an toàn -> p04_wax

- Lựa chọn: Về bàn đọc -> reading_room



### p04_wax

> scene:BM04_CRACK

> kind:SCENE

> guard:SERVER_P00_04_CHECKPOINT_120_CONFIRMED

Ly An mở nắp túi để kiểm tra lại vải dầu. Cô nghiêng lá thư về phía có ánh sáng. Giữa năm vạch, một khe nhỏ trắng ra. Cô chạm nhẹ quanh mép, tránh đúng chỗ vừa rạn.

Ly An: Bạn có làm rơi túi lúc tôi buộc dây không?

{held_letter:

    Bạn có thể nhắc lại việc mình đã giữ túi. Cô nhìn bạn rồi nhìn vết rạn, bàn tay thôi tìm chỗ móp trên bì thư.

- else:

    Cô tự lật góc túi, tìm chỗ va đập. Trên lớp vải dầu không có vết rách.

}


- Lựa chọn: Vết rạn vừa mở thêm.
    Cả hai chờ. Một hạt sáp rời khỏi mép niêm, lăn trên ngón tay cô rồi dính lại ở đường chỉ áo.

    Ly An: Tôi thấy rồi.

    -> p04_khanh


- Lựa chọn: Có lẽ sáp ngấm lạnh.
    Ly An: Tôi cũng mong thế.

    Cô gấp vải lại mà không ép lên niêm, giữ nguyên lá thư trong lòng bàn tay.

    -> p04_khanh


- Lựa chọn: Gọi ông Khanh lại xem.
    Ly An đưa tay định che niêm rồi hạ xuống.

    Ly An: Bác ấy cần nhìn lúc nó đang rạn.

    -> p04_khanh




### p04_khanh

Tạ Vân Khanh đến cạnh mép bờ. Ly An đưa thư ngay trước khi ông kịp hỏi về đường đi.

Ly An: Nó rạn khi cháu đứng yên.

Tạ Vân Khanh cúi gần. Ông không đưa tay nhận như lúc ở kho.

Tạ Vân Khanh: Cất trong vải, để khe này hở. Đừng gỡ sáp.

Ly An: Bác định chờ nó mở đến đâu?

Tiếng động dưới đầm làm ông quay đi. Mặt nước giữa các cọc chuông nâng lên, chậm hơn một con sóng thông thường. Ông lùi nửa bước, ra hiệu cho cả hai tránh mép bờ.

Tạ Vân Khanh: Ra khỏi ván trước đã.

BẢN ĐỌC · Sáp rạn là mốc nhìn thấy của P00-04, không có lời giải nguyên nhân. Không thêm video bắt buộc hoặc free-roam vào vùng còn combat. Cảnh nghỉ có thể bỏ qua mà tracker vẫn giữ mục tiêu.


- Lựa chọn: Đọc tiếp Mảnh ấn đầu tiên -> p05_before

- Lựa chọn: Về bàn đọc -> reading_room


## P00-05


### p05_before

> scene:BM05_BEFORE

> quest:P00-05

> kind:SCENE

> cinema:CIN_004

> guard:SERVER_PRIVATE_ARENA_READY_NO_TIMER

Mãng Cốt trồi lên giữa các cọc. Một mảng rễ ướt vẫn bám trên lưng nó. Thân linh thú quật ngang, làm nước văng qua lối ván vừa đi; khi đầu nó hạ xuống, những vòng nước lại kéo về cùng một chỗ.

Ly An níu nắp túi trước ngực, mắt theo chỗ ván đã bị nước phủ.

Ly An: Người ở ngoài bến còn lối lên không?

Tạ Vân Khanh: Lối phía kho chưa ngập. Ta giữ người ở đó.

Ông nhìn bạn, lần này không chờ hỏi.

Tạ Vân Khanh: Nếu nó quay đầu về bờ, kéo nó ra xa lối ván. Thấy nước rút dưới chân thì rời chỗ đó ngay.

BẢN ĐỌC · Chỉ dẫn này là lời cảnh báo diegetic; telegraph/AI/targeting và thông số đòn phải theo encounter nguồn, không tạo lệnh kéo boss hoặc thêm mechanic từ kịch bản.


Chuyển cảnh: p05_battle.




### p05_battle

> scene:BM05_ENCOUNTER

> kind:CHECKPOINT

> guard:SERVER_P00_05_BOSS_CLEAR

TRACKER · Vào vòng boss và hạ Mãng Cốt theo encounter đã có. Bản đọc không phát damage/death/loot event. Team ready, wipe/retry và credit dùng server.


- Lựa chọn: Mô phỏng: server đã xác nhận encounter clear -> p05_still

- Lựa chọn: Về bàn đọc -> reading_room



### p05_still

> scene:BM05_STILL

> kind:SCENE

> guard:SERVER_P00_05_BOSS_CLEAR

Nước rơi khỏi các cọc chuông thành những sợi mảnh. Một chiếc lá bị cuốn sát bờ rồi chậm lại. Lần này nó đi tiếp, qua chỗ vòng nước từng co vào.

Ly An tháo dây túi ra khỏi cánh tay. Vải hằn một vệt đỏ ngang cổ tay; cô xoa lên đó, rồi thả tay xuống khi nhìn mặt nước.

Ly An: Bây giờ thấy cả mái kho.

Bóng mái kho nằm đúng dưới chân cọc. Bầu trời sáng hơn một chút, nhưng một vệt ánh kim dưới đầm vẫn giữ nguyên dù đám mây bên trên đã trôi qua.

Tạ Vân Khanh ngồi xuống ở chỗ bờ chắc. Ông đưa tay ngăn Ly An khi cô định tới gần vệt sáng.


- Lựa chọn: Hỏi có thể nhìn nó từ đây không.
    Tạ Vân Khanh: Ta cũng đang nhìn. Chờ bùn lắng đã.

    Ông hạ bàn tay đang ngăn, chống xuống đầu gối để đứng lên.

    -> p05_seal_gate


- Lựa chọn: Đứng yên, theo dõi vệt ánh kim.
    Qua lớp nước đục mỏng dần, vệt kim có một cạnh đứt. Ly An xoay lá thư trong vải dầu, đối cạnh niêm còn nguyên với nó.

    Ly An: Bác Khanh.

    Tạ Vân Khanh: Ta thấy.

    -> p05_seal_gate




### p05_seal_gate

> scene:BM05_SEAL_INTERACTION

> kind:CHECKPOINT

> guard:SERVER_P00_05_SEAL_INTERACT_CONFIRMED

TRACKER · Tương tác mảnh ấn đã có sau encounter clear. Trong game cần kiểm tra khoảng cách và trạng thái objective; client không tự tạo item hoặc gán flag.


- Lựa chọn: Mô phỏng: tương tác mảnh ấn đã được xác nhận -> p05_name

- Lựa chọn: Về bàn đọc -> reading_room



### p05_name

> scene:BM05_NAME

> kind:SCENE

> guard:SERVER_P00_05_SEAL_INTERACT_CONFIRMED

Ánh sáng chạy dọc cạnh mảnh ấn, ngừng ở chỗ đứt. Cùng lúc, khe rạn trên niêm thư rộng thêm một đường tóc. Ly An giữ hai vật cách nhau, không thử ráp chúng lại.

Tiếng Huyền Ấn vang lên một lần. Không nhìn thấy ai nói. Khi tiếng ngân dứt, bạn lại nghe nước chảy qua chân cọc.

Ly An: Bác đã nghe tên ấy bao giờ chưa?

Tạ Vân Khanh nhìn lá thư trước, rồi mới nhìn mảnh ấn.

Tạ Vân Khanh: Rồi.

Ly An chờ ông nói tiếp. Một giọt nước rơi từ góc bì thư lên vạt áo cô.


- Lựa chọn: Ở đâu?
    Tạ Vân Khanh: Ta cần đối lại vài thứ trước khi kể với hai người.

    Ly An: Thư của cháu vẫn ở đây.

    Ông gật, không đưa tay lấy nó.

    -> p05_after


- Lựa chọn: Lá thư có liên quan đến nó không?
    Tạ Vân Khanh: Bạn cũng thấy sáp rạn cùng lúc. Đừng thử ép chúng lại.

    Ly An gấp vải dầu giữa hai vật, đặt lá thư trở vào túi riêng của mình.

    -> p05_after


- Lựa chọn: Để ông tự nói tiếp.
    Tạ Vân Khanh nhìn dọc các cọc chuông, như tìm chỗ bắt đầu một câu. Cuối cùng ông chỉ xuống đường bờ đang rút nước.

    Tạ Vân Khanh: Ta đưa người về bến trước.

    -> p05_after




### p05_after

> scene:BM05_RETURN

> kind:SCENE

Ly An nhặt đầu dây đã tuột khỏi túi. Lần này cô đưa nó cho bạn giữ mà không dặn tránh mặt niêm. Cô buộc lại nút, đẩy túi ra sau vai cho khỏi vướng lối.

Ly An: Về báo bà chèo đò nhé. Nhìn từ đây còn thấy dây neo.

Ngoài bến, một cánh cửa kho mở rộng hơn. Người đứng trong cửa kéo kiện hàng đầu tiên vào chỗ khô. Phía Thanh Lạc, đường bờ vẫn còn một đoạn chìm dưới nước; chưa ai bước lên đó.


Chuyển cảnh: p05_class.




### p05_class

> scene:BM05_CLASS_CONFIRM

> kind:CHECKPOINT

> guard:SERVER_P00_05_CLASS_CONFIRM_AVAILABLE

TRACKER · Xác nhận môn phái đã chọn ở NPC_CLASS_TRIAL. Đây không phải chọn lại lớp. Thưởng vũ khí theo lớp và mở Thanh Lạc/Chương I cần receipt authoritative.

BẢN ĐỌC · Không giả tên lớp hoặc thông số nhân vật. Chuyển tới xác nhận chỉ sau khi visibility/availability của NPC đã được chốt; source hiện có dependency cần review.


- Lựa chọn: Mô phỏng: đã xác nhận lớp và nhận receipt kết thúc tuyến -> p05_end

- Lựa chọn: Về bàn đọc -> reading_room



### p05_end

> scene:BM05_END

> kind:SCENE

Ở chỗ nước vừa rút, một đầu dây neo mắc dưới ván. Ly An cúi gỡ nó, gọi người chèo đò ngoài bến. Lần đầu tiên từ lúc gặp, cô gọi đủ lớn để người ở bên kia nghe được.

KẾT TUYẾN BẢN ĐỌC · Người viết thư, lý do Tạ nhận ra niêm và sự khác nhau trong hai lời kể vẫn chưa có lời giải. Bản đọc dừng ở đây; không tự mở Chương I hoặc phát cinema trong game.


- Lựa chọn: Đọc lại từ đầu -> p01_rope

- Lựa chọn: Về bàn đọc -> reading_room

- Lựa chọn: Đóng bản đọc -> END
