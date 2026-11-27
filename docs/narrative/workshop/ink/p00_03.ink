// P00-03. Roots3/rescue2/dodge1 are unchanged; rescue availability mismatch remains a proposal.
=== p03_call ===
# scene:BM03_CALL
# quest:P00-03
# kind:SCENE
~ heard_first = false
Một bàn tay vỗ vào mặt nước giữa đám lau. Ly An nằm rạp trên ván, giơ một đoạn dây xuống. Đầu dây vừa chạm tay người dưới đầm đã bị kéo lệch sang bên.
Dân chài: Đừng giật! Chân tôi vẫn mắc!
Ly An thu bớt dây, lùi khỏi mép ván để nhường chỗ cho bạn.
Ly An: Có hai người. Rễ quấn ở dưới, nhìn lá trên mặt nước sẽ không thấy đâu.
+ [Tôi giữ dây. Cô nhìn giúp chỗ mắc.]
    Ly An: Chờ tôi chỉ rồi hãy kéo.
    Cô cúi hẳn xuống, một tay ghì mép ván. Từ đám lau xa hơn, tiếng người chèo đò lại gọi, lần này khản đặc.
    -> p03_roots
+ [Sóng đang dồn về đây.]
    Ly An ngẩng lên. Nước giữa các chân lau lõm xuống, để lộ một vệt bùn sẫm.
    Ly An: Lên chỗ đất khô trước! Tôi giữ dây, bạn tránh sang bên đó.
    -> p03_roots

=== p03_roots ===
# scene:BM03_ROOTS
# kind:CHECKPOINT
# guard:SERVER_P00_03_ROOTS_3_RESCUES_2_DODGE_1
TRACKER · Phá ba đám Rễ Nước, tương tác cứu hai người và tránh một đợt sóng. Credit và vị trí an toàn cần server xác nhận. Bản đọc không chốt loại KILL/INTERACT của rễ đang còn mâu thuẫn trong source.
BẢN ĐỌC · Tiếng sóng có mô tả hình tương đương. Đoạn sau đặt ở trạng thái đã cứu được người; không chạy thoại khi actor còn bị đánh.
+ [Mô phỏng: đã hoàn thành các bước cứu và lên bờ] -> p03_first
+ [Về bàn đọc] -> reading_room

=== p03_first ===
# scene:BM03_FIRST_WITNESS
# cinema:CIN_003
# kind:SCENE
# guard:SERVER_P00_03_RESCUE_01_CONFIRMED
Người dân chài ngồi tựa lên khuỷu tay. Ông kéo ống quần khỏi cổ chân, nhăn mặt khi vải chạm da. Ly An đặt đầu dây vừa dùng xuống cạnh ông.
Dân chài: Người kia đâu rồi?
Ly An: Đang lên. Bác chờ, đừng đứng.
Dân chài nhìn bạn lâu hơn một cái nhìn cảm ơn.
Dân chài: Ban nãy tôi thấy bạn ở dưới ấy.
+ [Tôi vừa từ trên bờ xuống.]
    Dân chài: Tôi biết. Bây giờ tôi thấy rồi.
    Ông xoa nước khỏi mắt, quay lại nhìn đúng chỗ bạn đã đứng.
    -> p03_second
+ [Tôi ở phía nào?]
    ~ heard_first = true
    Dân chài chỉ vào một khoảng nước sát rễ.
    Dân chài: Bên đó. Cứ đứng, không đưa tay. Tôi gọi mấy lần.
    Ly An nhấc đoạn dây lên, cuộn nó để ông khỏi nhìn mãi vào phần đã mắc dưới nước.
    -> p03_second
+ [Bác có bị đau ở đâu nữa không?]
    Dân chài: Chân phải. Tay vẫn được. Để tôi vịn cái cọc một lúc.
    Ông vịn vào chỗ gỗ khô, thử nhấc bàn chân khỏi bùn rồi lại đặt xuống.
    -> p03_second

=== p03_second ===
# scene:BM03_SECOND_WITNESS
# kind:SCENE
# guard:SERVER_P00_03_RESCUE_02_CONFIRMED
Người chèo đò bò thêm một đoạn mới chịu ngồi. Bà giũ từng bàn tay, nhìn những vết rễ hằn đỏ quanh cổ tay áo.
Người chèo đò: Ai đứng dưới nước? Tôi chỉ thấy một người quay lưng ở giữa dòng.
Dân chài: Tôi nhìn rõ mặt.
Người chèo đò: Ông úp mặt vào bờ còn tôi nhìn ra ngoài. Chỗ ông chỉ là mạn đò của tôi.
Dân chài chực đáp, nhưng cơn ho làm ông gập người. Ly An đỡ khuỷu tay để ông khỏi chống xuống vết bùn trơn.
+ [Để từng người kể lại từ lúc trượt chân.]
    Người chèo đò: Tôi xuống tháo dây neo. Nước chỉ tới đây.
    Bà chỉ một vệt trên ống chân, thấp hơn vết bùn mới.
    Người chèo đò: Bước tiếp theo thì chân đã không chạm đáy.
    {heard_first:
        Dân chài: Tôi nghe bà gọi. Đến lúc với tay ra, cái mặt ấy đã ở dưới chân tôi.
    - else:
        Dân chài: Tôi xuống sau. Tôi còn tưởng kéo được bà lên ngay.
    }
    -> p03_after
+ [Có thể nhìn hai người khác nhau.]
    Người chèo đò lắc đầu, không hẳn đồng ý cũng không bác.
    Người chèo đò: Đò của tôi vẫn ngoài ấy. Tôi nhìn nó mỗi ngày, tôi biết hướng.
    Dân chài cúi xuống chỉnh lại ống quần. Lần này ông không tranh nói.
    -> p03_after
+ [Lên chỗ khô rồi hãy nói tiếp.]
    Ly An đứng dậy, đưa tay cho người gần mình hơn. Người chèo đò vẫn ngoái về bến, đếm những cọc neo còn nhô trên nước.
    -> p03_after

=== p03_after ===
# scene:BM03_SHORE
# kind:SCENE
# guard:SERVER_P00_03_READY_TO_TURN_IN
Ly An đợi hai người có chỗ vịn chắc rồi mới nhấc túi lên khỏi ván. Một góc vải dầu ướt dính vào tay cô. Cô gỡ ra thật chậm, xem phần niêm còn được che kín.
+ [Cô vẫn giữ lá thư.]
    Ly An: Ông Khanh bảo mang theo.
    Cô kéo nắp túi xuống. Cái móc không ăn, cô phải thử lại.
    Ly An: Giúp tôi xem còn ai gọi không.
    -> p03_close
+ [Tôi sẽ kể cả hai lời với ông Khanh.]
    Ly An: Để họ nghỉ rồi hỏi lại. Bác ấy vừa trượt lần nữa lúc tôi đỡ lên.
    Cô nhìn bàn tay dính bùn của mình, lau lên mảng áo vốn đã ướt.
    -> p03_close
+ [Im lặng, giúp cuộn dây.]
    Hai người cuộn từ hai đầu. Đến đoạn giữa bị rễ siết, Ly An thử gỡ nút, rồi để nguyên vết thắt trong cuộn dây.
    -> p03_close

=== p03_close ===
Từ phía kho có người gọi Ly An. Cô giơ tay đáp, chờ người dân chài thử đứng được rồi mới bước khỏi ván.
Ly An: Tôi sang báo chỗ này đã kéo được người lên. Bạn đừng xuống tìm cái bóng một mình nhé.
BẢN ĐỌC · Kết quả trả quest chỉ xuất hiện sau receipt. Lời kể không tạo xác nhận avatar từng ở đây, huyết thống hoặc ký ức tiền kiếp. Hai rescue actors vẫn dùng ID hiện có; visibility source đang mâu thuẫn P00-03/P00-04 cần adapter review.
+ [Đọc tiếp Người giữ bờ] -> p04_depart
+ [Về bàn đọc] -> reading_room
