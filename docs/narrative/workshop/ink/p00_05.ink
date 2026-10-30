// P00-05. Boss clear ->seal interact ->existingclass confirm. HuyenAn only after seal checkpoint.
=== p05_before ===
# scene:BM05_BEFORE
# quest:P00-05
# kind:SCENE
# cinema:CIN_004
# guard:SERVER_PRIVATE_ARENA_READY_NO_TIMER
Mãng Cốt trồi lên giữa các cọc. Một mảng rễ ướt vẫn bám trên lưng nó. Thân linh thú quật ngang, làm nước văng qua lối ván vừa đi; khi đầu nó hạ xuống, những vòng nước lại kéo về cùng một chỗ.
Ly An níu nắp túi trước ngực, mắt theo chỗ ván đã bị nước phủ.
Ly An: Người ở ngoài bến còn lối lên không?
Tạ Vân Khanh: Lối phía kho chưa ngập. Ta giữ người ở đó.
Ông nhìn bạn, lần này không chờ hỏi.
Tạ Vân Khanh: Nếu nó quay đầu về bờ, kéo nó ra xa lối ván. Thấy nước rút dưới chân thì rời chỗ đó ngay.
BẢN ĐỌC · Chỉ dẫn này là lời cảnh báo diegetic; telegraph/AI/targeting và thông số đòn phải theo encounter nguồn, không tạo lệnh kéo boss hoặc thêm mechanic từ kịch bản.
-> p05_battle

=== p05_battle ===
# scene:BM05_ENCOUNTER
# kind:CHECKPOINT
# guard:SERVER_P00_05_BOSS_CLEAR
TRACKER · Vào vòng boss và hạ Mãng Cốt theo encounter đã có. Bản đọc không phát damage/death/loot event. Team ready, wipe/retry và credit dùng server.
+ [Mô phỏng: server đã xác nhận encounter clear] -> p05_still
+ [Về bàn đọc] -> reading_room

=== p05_still ===
# scene:BM05_STILL
# kind:SCENE
# guard:SERVER_P00_05_BOSS_CLEAR
Nước rơi khỏi các cọc chuông thành những sợi mảnh. Một chiếc lá bị cuốn sát bờ rồi chậm lại. Lần này nó đi tiếp, qua chỗ vòng nước từng co vào.
Ly An tháo dây túi ra khỏi cánh tay. Vải hằn một vệt đỏ ngang cổ tay; cô xoa lên đó, rồi thả tay xuống khi nhìn mặt nước.
Ly An: Bây giờ thấy cả mái kho.
Bóng mái kho nằm đúng dưới chân cọc. Bầu trời sáng hơn một chút, nhưng một vệt ánh kim dưới đầm vẫn giữ nguyên dù đám mây bên trên đã trôi qua.
Tạ Vân Khanh ngồi xuống ở chỗ bờ chắc. Ông đưa tay ngăn Ly An khi cô định tới gần vệt sáng.
+ [Hỏi có thể nhìn nó từ đây không.]
    Tạ Vân Khanh: Ta cũng đang nhìn. Chờ bùn lắng đã.
    Ông hạ bàn tay đang ngăn, chống xuống đầu gối để đứng lên.
    -> p05_seal_gate
+ [Đứng yên, theo dõi vệt ánh kim.]
    Qua lớp nước đục mỏng dần, vệt kim có một cạnh đứt. Ly An xoay lá thư trong vải dầu, đối cạnh niêm còn nguyên với nó.
    Ly An: Bác Khanh.
    Tạ Vân Khanh: Ta thấy.
    -> p05_seal_gate

=== p05_seal_gate ===
# scene:BM05_SEAL_INTERACTION
# kind:CHECKPOINT
# guard:SERVER_P00_05_SEAL_INTERACT_CONFIRMED
TRACKER · Tương tác mảnh ấn đã có sau encounter clear. Trong game cần kiểm tra khoảng cách và trạng thái objective; client không tự tạo item hoặc gán flag.
+ [Mô phỏng: tương tác mảnh ấn đã được xác nhận] -> p05_name
+ [Về bàn đọc] -> reading_room

=== p05_name ===
# scene:BM05_NAME
# kind:SCENE
# guard:SERVER_P00_05_SEAL_INTERACT_CONFIRMED
Ánh sáng chạy dọc cạnh mảnh ấn, ngừng ở chỗ đứt. Cùng lúc, khe rạn trên niêm thư rộng thêm một đường tóc. Ly An giữ hai vật cách nhau, không thử ráp chúng lại.
Tiếng Huyền Ấn vang lên một lần. Không nhìn thấy ai nói. Khi tiếng ngân dứt, bạn lại nghe nước chảy qua chân cọc.
Ly An: Bác đã nghe tên ấy bao giờ chưa?
Tạ Vân Khanh nhìn lá thư trước, rồi mới nhìn mảnh ấn.
Tạ Vân Khanh: Rồi.
Ly An chờ ông nói tiếp. Một giọt nước rơi từ góc bì thư lên vạt áo cô.
+ [Ở đâu?]
    Tạ Vân Khanh: Ta cần đối lại vài thứ trước khi kể với hai người.
    Ly An: Thư của cháu vẫn ở đây.
    Ông gật, không đưa tay lấy nó.
    -> p05_after
+ [Lá thư có liên quan đến nó không?]
    Tạ Vân Khanh: Bạn cũng thấy sáp rạn cùng lúc. Đừng thử ép chúng lại.
    Ly An gấp vải dầu giữa hai vật, đặt lá thư trở vào túi riêng của mình.
    -> p05_after
+ [Để ông tự nói tiếp.]
    Tạ Vân Khanh nhìn dọc các cọc chuông, như tìm chỗ bắt đầu một câu. Cuối cùng ông chỉ xuống đường bờ đang rút nước.
    Tạ Vân Khanh: Ta đưa người về bến trước.
    -> p05_after

=== p05_after ===
# scene:BM05_RETURN
# kind:SCENE
Ly An nhặt đầu dây đã tuột khỏi túi. Lần này cô đưa nó cho bạn giữ mà không dặn tránh mặt niêm. Cô buộc lại nút, đẩy túi ra sau vai cho khỏi vướng lối.
Ly An: Về báo bà chèo đò nhé. Nhìn từ đây còn thấy dây neo.
Ngoài bến, một cánh cửa kho mở rộng hơn. Người đứng trong cửa kéo kiện hàng đầu tiên vào chỗ khô. Phía Thanh Lạc, đường bờ vẫn còn một đoạn chìm dưới nước; chưa ai bước lên đó.
-> p05_class

=== p05_class ===
# scene:BM05_CLASS_CONFIRM
# kind:CHECKPOINT
# guard:SERVER_P00_05_CLASS_CONFIRM_AVAILABLE
TRACKER · Xác nhận môn phái đã chọn ở NPC_CLASS_TRIAL. Đây không phải chọn lại lớp. Thưởng vũ khí theo lớp và mở Thanh Lạc/Chương I cần receipt authoritative.
BẢN ĐỌC · Không giả tên lớp hoặc thông số nhân vật. Chuyển tới xác nhận chỉ sau khi visibility/availability của NPC đã được chốt; source hiện có dependency cần review.
+ [Mô phỏng: đã xác nhận lớp và nhận receipt kết thúc tuyến] -> p05_end
+ [Về bàn đọc] -> reading_room

=== p05_end ===
# scene:BM05_END
# kind:SCENE
Ở chỗ nước vừa rút, một đầu dây neo mắc dưới ván. Ly An cúi gỡ nó, gọi người chèo đò ngoài bến. Lần đầu tiên từ lúc gặp, cô gọi đủ lớn để người ở bên kia nghe được.
KẾT TUYẾN BẢN ĐỌC · Người viết thư, lý do Tạ nhận ra niêm và sự khác nhau trong hai lời kể vẫn chưa có lời giải. Bản đọc dừng ở đây; không tự mở Chương I hoặc phát cinema trong game.
+ [Đọc lại từ đầu] -> p01_rope
+ [Về bàn đọc] -> reading_room
+ [Đóng bản đọc] -> END
