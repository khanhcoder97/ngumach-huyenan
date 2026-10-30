// P00-02. Preserve3ripples/4Carpling/report. No truth claim beyond witnessed phenomenon.
=== p02_bank ===
# scene:BM02_BANK
# quest:P00-02
# kind:SCENE
~ water_report = 0
Ngoài mái kho, Ly An vắt nước khỏi tay áo. Tạ Vân Khanh ngừng ghi sổ khi tiếng giọt rơi từ mái thưa dần.
Tạ Vân Khanh: Ban nãy ở bến, có nghe gì ngoài tiếng mưa không?
+ [Có tiếng như chuông.]
    Ly An: Tôi tưởng tiếng vòng sắt va cọc.
    Tạ Vân Khanh: Vòng sắt còn treo trên cọc chứ?
    Ly An quay đầu nhìn ra. Cọc ở quá xa để thấy rõ. Cô không trả lời.
    -> p02_request
+ [Tôi chưa để ý.]
    Tạ Vân Khanh: Vậy đừng cố nhớ cho giống điều người khác kể. Đến chỗ đầm nông mà nghe lại.
    -> p02_request
+ [Bác đã nghe thấy gì?]
    Ông khép cuốn sổ, kẹp ngón tay giữa hai trang.
    Tạ Vân Khanh: Ta muốn nghe bạn nói trước.
    -> p02_request

=== p02_request ===
Tạ Vân Khanh: Có ba chỗ nước cứ cuộn về một điểm. Cá Linh tụ ở đó từ sớm. Giữ cho chúng không áp sát, rồi nhìn xem vòng nước chạy thế nào. Đừng xuống quá đầu gối.
Ly An: Cháu ở trên bờ trông người.
Tạ Vân Khanh gật đầu. Ông mở sổ lại, nhưng ngòi bút chưa chạm giấy.
-> p02_ripples

=== p02_ripples ===
# scene:BM02_RIPPLES
# kind:CHECKPOINT
# guard:SERVER_P00_02_RIPPLES_3_AND_CARPLING_4
TRACKER · Quan sát ba gợn nước, hạ bốn Cá Linh và quay lại báo cáo. Bản đọc không mô phỏng combat hoặc cấp credit.
BẢN ĐỌC · Tại mỗi điểm đã đặt trong map, người chơi có thể đọc mô tả hình/âm thay cho việc phải nghe đúng hoặc nhận ra pixel nhỏ. Lựa chọn dưới đây là điều bạn chú ý trong cùng hiện tượng, không đổi kết quả nhiệm vụ.
+ [Chú ý vòng nước]
    ~ water_report = 1
    Một giọt mưa tạo những vòng tròn tản ra. Khi chạm chỗ nước sẫm, mép vòng dừng lại rồi lùi vào. Lá lau trôi ngang qua vẫn đi theo dòng bên ngoài.
    -> p02_bell
+ [Chú ý âm thanh]
    ~ water_report = 2
    Trên bờ chỉ có tiếng cọc gỗ cọ vào dây. Khi bạn cúi gần mặt nước, tiếng ngân nối tiếp xuất hiện, mỏng và thấp. Bạn đứng thẳng. Phần ngân ấy mất đi.
    -> p02_bell
+ [Đọc mô tả đầy đủ, không dùng âm thanh]
    ~ water_report = 3
    Vòng nước co về tâm. Bóng một vành chuông hiện dưới mép bến; phía trên không có vật tương ứng. Âm thanh nếu bật chỉ bổ sung tiếng ngân khi camera quan sát gần, không chứa manh mối độc quyền.
    -> p02_bell

=== p02_bell ===
# scene:BM02_SOUND
# kind:SCENE
# cinema:CIN_002
# guard:SERVER_P00_02_RIPPLES_3
Một bóng tròn rung dưới nước. Khi vòng gợn đi qua, mép bóng vỡ thành những mảnh ngắn rồi liền lại. Ở trên, sợi dây treo cạnh cọc nằm im.
Ly An gọi từ bờ. Bạn quay lại; khi nhìn xuống lần nữa, chỗ đó chỉ còn bóng mái kho.
Ly An: Đừng đứng sát thêm. Có người vừa hụt chân ở đằng lau kia.
BẢN ĐỌC · Đoạn quan sát có thể là CIN_002 đã có trong pack, hoặc text/still fallback. Nó không thay số gợn nước hoặc combat objective.
+ [Mô phỏng: đã đủ objective, trở về trước kho] -> p02_report
+ [Về bàn đọc] -> reading_room

=== p02_report ===
# scene:BM02_REPORT
# kind:SCENE
# guard:SERVER_P00_02_READY_TO_TURN_IN
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
+ [Đọc tiếp Dưới mặt đầm] -> p03_call
+ [Về bàn đọc] -> reading_room
