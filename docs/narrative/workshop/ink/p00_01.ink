// P00-01. Canon:3packages + sealed letter -> NPC_TA_VAN_KHANH. New staging is candidate.
=== p01_rope ===
# scene:BM01_ROPE
# quest:P00-01
# kind:SCENE
# cinema:CIN_001
~ kept_distance = false
Nước mưa chảy qua các khe ván. Một sợi dây căng ngang bến rồi tuột khỏi cọc, quất vào chiếc giỏ tre bên chân Ly An. Cô giữ được đầu dây còn lại, nhưng kiện hàng ngoài mép đã xoay nửa vòng.
Ly An: Đầu kia! Giữ giúp tôi đầu kia!
Cô nhích gót giày lên một thanh ván. Nước ngập qua mũi giày, kiện hàng dừng lại. Ly An vẫn chưa nhìn người vừa tới.
+ [Giữ dây và kéo kiện vào] -> p01_help
+ [Chỉ chỗ quấn dây quanh cọc] -> p01_post
+ [Tôi đang đi vội.] -> p01_hurry

=== p01_help ===
Bạn kéo đầu dây về phía cọc. Ly An tranh thủ chèn giỏ tre dưới kiện hàng, rồi mới thả tay.
Ly An: Khoan, đừng kéo nữa. Mép dưới sắp bung.
Cô quỳ xuống, nhét lại lớp vải gói đang hở. Qua khe vải là miệng một chiếc bát sứ bọc rơm. Cô thử nhấc kiện, nghe bên trong một tiếng chạm rất khẽ.
Ly An: Còn nguyên. May thật.
-> p01_letter

=== p01_post ===
Ly An liếc theo tay bạn, vắt dây thêm một vòng quanh cọc. Kiện hàng nghiêng hẳn sang bên, nằm yên.
Ly An: Ừ, cọc này còn chắc. Tôi cứ tưởng nó cũng mục rồi.
Cô thử kéo lại sợi dây trước khi đứng lên. Đốt ngón tay đã trắng bệch vì siết lâu.
-> p01_letter

=== p01_hurry ===
~ kept_distance = true
Ly An: Vậy giữ một lúc thôi. Đủ để tôi buộc lại.
Cô ghì dây bằng khuỷu tay, cúi nhặt chiếc giỏ đã đổ. Cái giỏ cứ trượt khỏi tầm với. Khi cô ngẩng lên lần nữa, lời tiếp theo nhỏ hơn.
Ly An: Làm ơn.
+ [Quay lại giữ đầu dây] -> p01_help
+ [Bỏ qua cảnh này để đọc nhiệm vụ khác] -> reading_room

=== p01_letter ===
# scene:BM01_LETTER
# kind:SCENE
Ly An phủi rơm khỏi tay áo. Cô lấy trong túi một lá thư bọc vải dầu. Niêm sáp có năm vạch chìm; vạch ở rìa mất dưới một giọt nước chưa khô.
Ly An: Ba kiện bị dòng nước đẩy dạt quanh đây. Chưa thấy ai tới nhận. Ông Khanh ở trước kho đang nhận đồ thất lạc. Bạn mang giúp tới đó được không?
+ [Cô không đi cùng sao?]
    Ly An nhìn dọc mép bến. Cô vừa gom dây, vừa tìm một đầu dây khác trong đám lau.
    Ly An: Tôi xem còn kiện nào mắc bên dưới không. Mang nguyên niêm giúp tôi. Có ai hỏi người gửi thì bảo họ hỏi ông Khanh.
    -> p01_accept
+ [Trong thư có gì?]
    Ngón tay cô dừng ở mép vải dầu.
    Ly An: Tôi chưa mở.
    Cô đưa lá thư ra, mặt niêm quay lên. Khi bạn nhận, cô vẫn giữ góc vải thêm một nhịp rồi mới buông.
    -> p01_accept
+ [Được, tôi mang tới kho.]
    Ly An: Cảm ơn. Kiện nào buộc dây đôi thì đỡ từ dưới, đừng nhấc bằng nút.
    -> p01_accept

=== p01_accept ===
# scene:BM01_PACKAGES
# kind:CHECKPOINT
# guard:SERVER_P00_01_ACTIVE_AND_PACKAGES_3
TRACKER · Nhặt đủ ba kiện hàng rồi mang thư còn niêm tới Tạ Vân Khanh. Trong game, tương tác và tiến độ do server xác nhận.
BẢN ĐỌC · Ba kiện có dấu buộc khác nhau: sợi chỉ sẫm cài trong nút, một miếng vải vá, hai vòng dây bẹ. Các dấu chỉ là trang trí candidate của những kiện đã có, không phải ba item mới.
+ [Mô phỏng: đã tìm đủ ba kiện và tới kho] -> p01_khanh
+ [Đọc lại lời nhờ của Ly An] -> p01_letter
+ [Về bàn đọc] -> reading_room

=== p01_khanh ===
# scene:BM01_RECEIPT
# kind:SCENE
# guard:SERVER_P00_01_READY_TO_TURN_IN
Tạ Vân Khanh đang kê một tấm ván dưới chân kiện hàng bị lún. Ông chỉ chỗ khô sát vách kho, chờ bạn đặt đồ xuống rồi mới hỏi.
Tạ Vân Khanh: Có ai theo nhận hàng không?
+ [Tôi chỉ gặp Ly An.]
    Tạ Vân Khanh: Nó còn ngoài bến à?
    Ông nhìn qua vai bạn. Ly An đang tới, vạt áo ôm sát đầu gối.
    -> p01_seal
+ [Cô ấy đang tìm xem còn ai dưới bến.]
    Tạ Vân Khanh: Ta đã dặn nó kiểm hàng trên bờ.
    Ông kéo một kiện ra khỏi lối đi, để chừa khoảng trống rộng hơn trước cửa kho.
    -> p01_seal

=== p01_seal ===
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
+ [Đọc tiếp Chuông không người] -> p02_bank
+ [Về bàn đọc] -> reading_room
