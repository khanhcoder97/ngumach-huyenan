// P00-04. Escort checkpoints80/120;2waves×3. Pauses are safe presentation candidates.
=== p04_depart ===
# scene:BM04_DEPART
# quest:P00-04
# kind:SCENE
~ held_letter = false
Tạ Vân Khanh đã ra khỏi mái kho. Ông nhìn cuộn dây sũng nước trong tay Ly An, rồi nhìn đoạn bờ dẫn tới Đầm Chuông.
Tạ Vân Khanh: Ta cần xem chỗ nước lõm. Hai người đi được nữa không?
Ly An: Cháu đi được.
Tạ Vân Khanh: Ta hỏi cả bạn ấy.
+ [Tôi đi cùng Ly An.]
    Ly An chuyển cuộn dây sang tay bên kia, chừa một bên vai để luồn qua đám lau.
    Ly An: Tôi biết đoạn đầu. Tới chỗ cầu gỗ thì đi chậm thôi.
    -> p04_wave_one
+ [Có thể đợi người vừa cứu nghỉ thêm không?]
    Tạ Vân Khanh: Họ ở lại bến. Ta không đưa họ xuống lần nữa.
    Ông chỉ một lối bờ cao hơn. Ly An sửa lại quai túi, đợi bạn bước lên trước.
    -> p04_wave_one

=== p04_wave_one ===
# scene:BM04_FIRST_HOLD
# kind:CHECKPOINT
# guard:SERVER_P00_04_CHECKPOINT_80_WAVE_1_CLEAR
TRACKER · Hộ tống Ly An qua hai chặng, mỗi chặng có một đợt ba quái. Chết hoặc thất bại trở về checkpoint theo server; không phát lại credit/thưởng bằng lời thoại.
BẢN ĐỌC · Đọc cảnh nghỉ sau khi server xác nhận wave đầu đã sạch và không có nguy hiểm mới. Tọa độ checkpoint giữ source, không dời actor để diễn cảnh.
+ [Mô phỏng: giữ được chặng đầu] -> p04_knot
+ [Về bàn đọc] -> reading_room

=== p04_knot ===
# scene:BM04_KNOT
# kind:SCENE
Ly An quỳ một gối, tháo đầu dây buộc túi đã ngấm nước. Cô kéo mãi mà nút càng siết. Bên kia bờ, một tiếng gỗ gãy rơi xuống đầm.
Ly An dừng tay, nghe. Không còn tiếng nào tiếp theo.
+ [Tôi giữ túi. Cô gỡ đi.]
    ~ held_letter = true
    Cô đặt túi lên hai bàn tay bạn, lật đầu dây vòng qua nút. Mùi vải dầu ẩm và rơm ướt lẫn vào nhau. Lá thư nằm sát lớp lót, mặt có sáp quay vào trong.
    Ly An: Đừng nghiêng. Tôi buộc lại ngay.
    -> p04_talk
+ [Cắt nút rồi buộc đoạn khác được không?]
    Ly An kéo một nhánh dây, thử độ dài còn lại.
    Ly An: Được. Đầu này vẫn còn đủ.
    Cô đổi cách buộc, lần này để nút nằm ở ngoài nắp túi.
    -> p04_talk
+ [Đợi cô buộc xong, nhìn chừng bờ nước.]
    Mặt đầm gần bờ phẳng lại. Chỉ khi một con côn trùng chạm xuống, bạn mới thấy những vòng nước vẫn đang đi vào trong.
    -> p04_talk

=== p04_talk ===
Ly An: Hồi nãy người chèo đò hỏi tôi còn thấy đò của bà ấy không. Tôi cứ bảo bà lên bờ đã.
Cô kéo thử quai túi, lần đầu được một nút chắc.
+ [Cô có quay lại xem không?]
    Ly An: Có. Dây neo chưa đứt. Chỉ là tôi chưa nói được với bà ấy.
    Cô nhìn ngược về bến một lần, rồi đứng lên.
    -> p04_wave_two
+ [Tôi cũng không nhìn rõ ngoài đó.]
    Ly An: Vậy lát nữa đứng ở bờ cao thử xem. Đừng xuống nữa.
    {held_letter:
        Cô nhận lại túi từ tay bạn bằng cả hai tay, đeo lên vai rồi chừa một khoảng cho bạn đi qua.
    }
    -> p04_wave_two
+ [Đi tiếp thôi.]
    Ly An gật, nhặt cuộn dây. Có một vòng cô để tuột xuống cỏ, phải cúi lấy thêm lần nữa.
    -> p04_wave_two

=== p04_wave_two ===
# scene:BM04_SECOND_HOLD
# kind:CHECKPOINT
# guard:SERVER_P00_04_CHECKPOINT_120_WAVE_2_CLEAR
TRACKER · Giữ chặng thứ hai trước khi tới Đầm Chuông. Bản đọc chuyển cảnh sau xác nhận wave thứ hai đã sạch; không mô phỏng đường đi hoặc boss activation.
+ [Mô phỏng: đã tới chặng nghỉ thứ hai an toàn] -> p04_wax
+ [Về bàn đọc] -> reading_room

=== p04_wax ===
# scene:BM04_CRACK
# kind:SCENE
# guard:SERVER_P00_04_CHECKPOINT_120_CONFIRMED
Ly An mở nắp túi để kiểm tra lại vải dầu. Cô nghiêng lá thư về phía có ánh sáng. Giữa năm vạch, một khe nhỏ trắng ra. Cô chạm nhẹ quanh mép, tránh đúng chỗ vừa rạn.
Ly An: Bạn có làm rơi túi lúc tôi buộc dây không?
{held_letter:
    Bạn có thể nhắc lại việc mình đã giữ túi. Cô nhìn bạn rồi nhìn vết rạn, bàn tay thôi tìm chỗ móp trên bì thư.
- else:
    Cô tự lật góc túi, tìm chỗ va đập. Trên lớp vải dầu không có vết rách.
}
+ [Vết rạn vừa mở thêm.]
    Cả hai chờ. Một hạt sáp rời khỏi mép niêm, lăn trên ngón tay cô rồi dính lại ở đường chỉ áo.
    Ly An: Tôi thấy rồi.
    -> p04_khanh
+ [Có lẽ sáp ngấm lạnh.]
    Ly An: Tôi cũng mong thế.
    Cô gấp vải lại mà không ép lên niêm, giữ nguyên lá thư trong lòng bàn tay.
    -> p04_khanh
+ [Gọi ông Khanh lại xem.]
    Ly An đưa tay định che niêm rồi hạ xuống.
    Ly An: Bác ấy cần nhìn lúc nó đang rạn.
    -> p04_khanh

=== p04_khanh ===
Tạ Vân Khanh đến cạnh mép bờ. Ly An đưa thư ngay trước khi ông kịp hỏi về đường đi.
Ly An: Nó rạn khi cháu đứng yên.
Tạ Vân Khanh cúi gần. Ông không đưa tay nhận như lúc ở kho.
Tạ Vân Khanh: Cất trong vải, để khe này hở. Đừng gỡ sáp.
Ly An: Bác định chờ nó mở đến đâu?
Tiếng động dưới đầm làm ông quay đi. Mặt nước giữa các cọc chuông nâng lên, chậm hơn một con sóng thông thường. Ông lùi nửa bước, ra hiệu cho cả hai tránh mép bờ.
Tạ Vân Khanh: Ra khỏi ván trước đã.
BẢN ĐỌC · Sáp rạn là mốc nhìn thấy của P00-04, không có lời giải nguyên nhân. Không thêm video bắt buộc hoặc free-roam vào vùng còn combat. Cảnh nghỉ có thể bỏ qua mà tracker vẫn giữ mục tiêu.
+ [Đọc tiếp Mảnh ấn đầu tiên] -> p05_before
+ [Về bàn đọc] -> reading_room
