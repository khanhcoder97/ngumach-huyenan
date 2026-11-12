# Ngũ Mạch: Huyền Ấn — bản viết lại gameplay v3

36 nhiệm vụ chính,40 nhiệm vụ phụ;229 node nội dung. Prose đã viết lại; runtime chỉ mở phần có quest/actor/checkpoint được hỗ trợ. Không đổi reward hoặc objective bằng văn bản.

Nguồn: campaign_rewrite_vi.json, side_stories_rewrite_vi.json và dialogue_expansions_vi.json; resource sinh bằng build_dialogue_text.py. CSV cũ giữ nguyên logic và bản biên tập lịch sử.

## P00-01 · Thư qua bến / AVAILABLE

`DLG_P00_01_OFFER` · `NPC_LYAN`

Nước mưa chảy qua các khe ván. Ly An ghì một sợi dây vào cọc, chặn kiện hàng vừa trượt tới mép bến.

Ly An: Khoan, giữ giúp tôi đầu kia!

Kiện hàng nằm yên. Qua khe vải hở là miệng một chiếc bát sứ bọc rơm. Ly An nhét lại lớp vải, thử nhấc kiện rồi mới thả tay.

Ly An: Còn nguyên. May thật.

Ly An lấy ra một lá thư bọc vải dầu. Trên niêm sáp có năm vạch chìm. Cô xoay mặt niêm lên trước khi đưa thư.

Ly An: Ba kiện bị nước đẩy dạt quanh đây. Ông Khanh trước kho đang nhận đồ thất lạc. Mang giúp tới đó, giữ nguyên niêm nhé.

Tìm ba kiện hàng quanh bến và giao thư còn niêm cho Tạ Vân Khanh trước kho.

Ly An: Kiện nào buộc dây đôi thì đỡ từ dưới, đừng nhấc bằng nút. Tôi xem còn ai dưới mép bến không.

Lựa chọn đọc: Trong thư có gì?

Ly An: Tôi chưa mở.

Cô giữ góc vải thêm một nhịp rồi mới buông. Mặt niêm vẫn quay lên.

Lựa chọn đọc: Cô không đi cùng sao?

Ly An: Tôi kiểm nốt phía dưới. Có người gọi bên đám lau từ nãy, nghe không rõ. Bạn tới kho trước đi.

## P00-01 · Thư qua bến / ACTIVE

`DLG_P00_01_CLUE` · `NPC_LYAN`

Ly An nhìn khoảng trống giữa những kiện đã gom, dò theo sợi dây mắc dưới ván.

Ly An: Vẫn còn đồ dạt ra xa. Quanh bến có ba kiện cần mang về; ông Khanh nhận ở chỗ khô trước kho. Thư thì để riêng, đừng tì lên niêm.

Nhật ký ghi các kiện đã tìm được. Đóng hội thoại để tiếp tục tìm quanh bến rồi tới chỗ ông Khanh.

## P00-01 · Thư qua bến / READY_TO_TURN_IN

`DLG_P00_01_TURN_IN` · `NPC_TA_VAN_KHANH`

Tạ Vân Khanh kê lại tấm ván dưới kiện bị lún. Ông chừa chỗ khô sát vách kho, đợi bạn đặt đồ xuống.

Tạ Vân Khanh: Có ai theo nhận hàng không?

Bạn đưa lá thư còn niêm. Ông xoay bì để đọc tên, rồi úp tay lên phần sáp. Ly An vừa tới dưới mái hiên.

Ly An: Thư vẫn nguyên chứ?
Tạ Vân Khanh: Còn nguyên.
Ly An: Cháu hỏi lúc bác nhận được.

Tạ Vân Khanh rút tay ra. Năm vạch sáp hiện lại dưới mái hiên.

Tạ Vân Khanh: Lúc ta nhận cũng vậy.

Ông đặt thư sang chỗ khô hơn. Ly An kiểm ba nút dây, đếm bằng đầu ngón tay.

Tạ Vân Khanh: Để ta ghi nhận đồ đã về đủ. Bạn chờ một chút, ta còn muốn hỏi về mặt nước ngoài kia.

Chọn Giao nhận để hoàn tất. Phần thưởng hiển thị sau khi xác nhận thành công.

Lựa chọn đọc: Tôi chỉ gặp Ly An.

Tạ Vân Khanh: Nó còn ngoài bến à?

Ông nhìn qua vai bạn. Ly An đang tới, vạt áo ướt ôm sát đầu gối.

Lựa chọn đọc: Cô ấy đang tìm xem còn ai dưới bến.

Tạ Vân Khanh: Ta đã dặn nó kiểm hàng trên bờ.

Ông kéo một kiện khỏi lối đi, chừa khoảng trống rộng hơn trước cửa kho.

Sau receipt đã xác nhận:

Tạ Vân Khanh ghi xong dòng nhận hàng, chừa ngòi bút trên đầu trang. Ngoài mái kho, tiếng giọt rơi từ hiên đã thưa dần.

Tạ Vân Khanh: Ban nãy ở bến, có nghe gì ngoài tiếng mưa không?

Ly An nhìn ra hàng cọc, nơi vòng sắt vẫn treo im.

Ly An: Tôi tưởng tiếng vòng sắt va cọc.

Ông Khanh khép sổ nhưng giữ một ngón tay giữa hai trang. Việc ở bến vẫn chưa xong.

## P00-02 · Chuông không người / AVAILABLE

`DLG_P00_02_OFFER` · `NPC_TA_VAN_KHANH`

Tạ Vân Khanh kẹp một ngón tay giữa hai trang sổ khi tiếng giọt rơi từ mái thưa dần.

Ở ngoài bến có nghe gì ngoài tiếng mưa không? Ta thấy ba chỗ nước cứ cuộn về tâm, Cá Linh tụ từ sáng. Đến xem ba chỗ ấy, đẩy lui bốn con rồi trở lại. Nếu chưa nghe thấy gì, cứ nói là chưa; đừng cố nhớ cho giống lời người khác.

## P00-02 · Chuông không người / ACTIVE

`DLG_P00_02_CLUE` · `NPC_TA_VAN_KHANH`

Ông đưa ngòi bút tới dòng trống nhưng chưa viết.

Nhìn một giọt mưa chạm nước, rồi nhìn chiếc lá trôi ngang. Cái gì đi theo dòng, cái gì quay vào? Tiếng ngân nếu có cũng phải đối được với điều nhìn thấy. Bạn không cần xuống sâu để tìm một chiếc chuông.

## P00-02 · Chuông không người / READY_TO_TURN_IN

`DLG_P00_02_TURN_IN` · `NPC_TA_VAN_KHANH`

Tạ Vân Khanh nghe hết lời kể mới đặt sổ xuống. Ly An nhìn ra những vòng sắt còn treo im trên cọc.

Ta chưa cho người xuống đó được. Bóng dưới nước và vật trên bờ không khớp, nhưng ta chưa biết phần nào đã đổi. Ly An, mang thư theo; ra xem người vừa hụt chân trước. Ta sẽ theo sau khi nhận xong đồ ở kho.

## P00-03 · Dưới mặt đầm / AVAILABLE

`DLG_P00_03_OFFER` · `NPC_LYAN`

Một bàn tay vỗ lên mặt nước giữa đám lau. Ly An nằm rạp trên ván, đầu dây trong tay cô bị giật lệch.

Có hai người! Đừng kéo vội, chân họ còn mắc rễ. Phá ba đám rễ trước, rồi đỡ từng người lên. Thấy nước lõm giữa chân lau thì tránh khỏi chỗ đó; tôi giữ dây.

## P00-03 · Dưới mặt đầm / ACTIVE

`DLG_P00_03_CLUE` · `NPC_LYAN`

Ly An thu một đoạn dây vừa chùng, cúi nhìn dưới mép ván.

Bạn hỏi tôi người dưới đó nói gì à? Tôi chỉ nghe họ gọi nhau. Để họ vịn chắc rồi hãy hỏi. Nếu lời kể khác nhau, cứ nhớ cả hai; lúc mắc dưới nước, họ đâu nhìn cùng một phía.

## P00-03 · Dưới mặt đầm / READY_TO_TURN_IN

`DLG_P00_03_TURN_IN` · `NPC_LYAN`

Người dân chài chỉ một khoảng sát rễ, nói đã thấy khuôn mặt bạn. Người chèo đò lắc đầu: bà nhìn thấy người quay lưng giữa dòng. Ông định cãi nhưng cơn ho làm câu nói đứt ngang.

Ly An: Lên chỗ khô trước. Bác vịn vào đây.

Cô đợi cả hai có chỗ ngồi rồi mới gỡ mảnh vải dầu ướt khỏi túi, kiểm niêm thư. Lần này cái móc nắp không ăn; cô phải thử lại.

## P00-04 · Người giữ bờ / AVAILABLE

`DLG_P00_04_OFFER` · `NPC_TA_VAN_KHANH`

Tạ Vân Khanh đã ra khỏi mái kho. Ông nhìn đường bờ về Đầm Chuông rồi hỏi cả bạn lẫn Ly An có đi được nữa không.

Những người vừa cứu ở lại bến. Ta cần xem chỗ nước lõm; hai người giữ đường cùng ta. Có hai chặng dễ bị ép sát nước. Qua được chặng nào thì giữ chỗ chắc ở đó, đừng vội chạy quá Ly An.

## P00-04 · Người giữ bờ / ACTIVE

`DLG_P00_04_CLUE` · `NPC_TA_VAN_KHANH`

Ly An quỳ gỡ nút túi đã ngấm nước. Cô kéo thử hai lần, dừng lại để nghe một tiếng gỗ gãy bên kia bờ.

Tạ Vân Khanh: Chờ đường yên rồi đi. Đợt này còn ba con; đừng rời người mình đang đưa qua. Nếu phải quay lại thì về chặng đã giữ được, không xuống ván trôi.

## P00-04 · Người giữ bờ / READY_TO_TURN_IN

`DLG_P00_04_TURN_IN` · `NPC_TA_VAN_KHANH`

Ly An nghiêng thư về ánh sáng. Giữa năm vạch sáp, một khe trắng mở ra dù bàn tay cô đã đứng yên.

Ly An: Bác xem lúc nó còn đang rạn.

Tạ Vân Khanh cúi gần nhưng không nhận thư.

Cất trong vải, để khe ấy hở. Đừng gỡ sáp.

Cô định hỏi tiếp. Mặt đầm nâng lên giữa các cọc chuông, khiến cả ba phải lùi khỏi mép ván.

## P00-05 · Mảnh ấn đầu tiên / AVAILABLE

`DLG_P00_05_OFFER` · `NPC_TA_VAN_KHANH`

Mãng Cốt trồi giữa các cọc, một mảng rễ ướt còn bám trên lưng. Nước dồn theo thân nó, phủ qua lối vừa đi.

Tạ Vân Khanh: Lối phía kho còn cao. Ta đưa người về đó. Giữ khoảng trống để lui, nhìn nước dưới chân trước khi ra đòn. Mảnh sáng dưới đầm để sau; lúc này đừng cúi tìm nó.

## P00-05 · Mảnh ấn đầu tiên / ACTIVE

`DLG_P00_05_CLUE` · `NPC_TA_VAN_KHANH`

Ông giữ người phía ngoài đường ván, không gọi bạn tiến sâu hơn.

Chưa yên thì chưa xuống tìm mảnh sáng. Sau trận còn phải xem nước đã trở lại chưa. Phần môn phái đã chọn cũng cần xác nhận đúng người; một câu gọi từ dưới đầm không thay việc ấy.

## P00-05 · Mảnh ấn đầu tiên / READY_TO_TURN_IN

`DLG_P00_05_TURN_IN` · `NPC_TA_VAN_KHANH`

Sau khi dòng nước lắng và mảnh ấn được kiểm tra, tiếng Huyền Ấn vang một lần rồi tắt. Ly An giữ thư cách mảnh kim, không thử ép hai vật lại.

Ly An: Bác đã nghe tên ấy bao giờ chưa?
Tạ Vân Khanh: Rồi. Trong một bản chép. Nó không có hình phần bị gãy này.
Ly An: Bác tìm lại thì gọi cả cháu.
Tạ Vân Khanh: Cả hai người.

Ngoài lau, người chèo đò thử kéo sợi neo; mạn đò nhúc nhích, vẫn còn đó.

## C1-01 · Cổng Thanh Lạc / AVAILABLE

`DLG_C1_01_OFFER` · `NPC_LYAN`

Ly An bước khỏi lối xe, vẫn ngoái về hướng bến dù cổng đã che mất mặt nước. Một đứa trẻ ôm bó cán cờ chạy qua, suýt quệt vào túi cô.

Tôi biết tìm nhà bằng dòng sông. Trong thành này chắc phải học lại. Bạn gặp ba người đại diện, đăng ký đài thử rồi xem bản đồ nhé. Tôi đợi ở cổng; nếu tìm được chỗ nghỉ thì chỉ tôi với.

## C1-01 · Cổng Thanh Lạc / ACTIVE

`DLG_C1_01_CLUE` · `NPC_LYAN`

Năm lá cờ trên quảng trường nghiêng về năm phía. Dưới chân cột, người bán hàng đang buộc chung hai tấm bạt để che quầy.

Ly An: Tôi hỏi đường tới đài, họ hỏi môn phái của tôi trước. Còn người chở hàng chỉ bảo đi theo xe bột. Bạn cứ xem bản đồ; tôi thử hỏi lại bằng tên phố.

## C1-01 · Cổng Thanh Lạc / READY_TO_TURN_IN

`DLG_C1_01_TURN_IN` · `NPC_LYAN`

Ly An ghi thêm một tên đường vào mặt sau tờ chỉ dẫn, gạch chỗ cô đã rẽ nhầm.

À, đài ở phía ấy. Tôi đi vòng mất một quãng. Bạn nghỉ trước đi, tôi còn phải báo đồ ở bến đã tới kho.

Cô nhìn chỗ niêm thư nằm dưới nắp túi rồi thôi. Lần này cô hỏi quán ăn gần nhất, không hỏi xem người trong thành đã nghe tiếng chuông chưa.

## C1-02 · Bài thử môn phái / AVAILABLE

`DLG_C1_02_OFFER` · `NPC_MASTER_BY_PLAYER_CLASS`

Người thầy đẩy chiếc bia về đúng vạch, nhặt một mảnh gỗ vỡ khỏi chỗ đứng thử.

Ta cần nhìn ba việc: ngươi đánh khi có khoảng trống, lui khi đòn tới, rồi dùng kỹ năng trước một đối thủ biết đổi nhịp. Vũ khí và môn phái ngươi đã chọn vẫn giữ nguyên. Bắt đầu bằng bia; đừng vội chứng minh điều gì với người đứng xem.

## C1-02 · Bài thử môn phái / ACTIVE

`DLG_C1_02_CLUE` · `NPC_MASTER_BY_PLAYER_CLASS`

Người thầy giơ tay để người đang tập bên cạnh dừng lại.

Chậm một lượt cũng được. Lúc bia đứng yên, ngươi có thể quyết định hết đòn của mình. Lúc đối thủ bước tới, phần ấy không còn thuộc riêng ngươi. Nhìn xem vừa rồi ngươi mất khoảng lui ở đâu rồi hãy thử lại.

## C1-02 · Bài thử môn phái / READY_TO_TURN_IN

`DLG_C1_02_TURN_IN` · `NPC_MASTER_BY_PLAYER_CLASS`

Người thầy nhận lại chiếc bia tập, xoay mặt đã sứt vào trong để người sau không vấp.

Lượt cuối ngươi có dừng. Ta thấy rồi.

Người thầy không hỏi ngươi có sợ không, chỉ yêu cầu chỉ lại vị trí đã chọn để lui. Phần đánh giá và trang bị được ghi riêng; tiếng vỗ tay từ hàng ghế chưa quyết định kết quả.

## C1-03 · Phù tín giả / AVAILABLE

`DLG_C1_03_OFFER` · `NPC_HA_MAC`

Hạ Mặc dùng hai tờ giấy chèn mẫu phù xuống bàn vì gió ở quảng trường cứ lật mép.

Bốn tấm, hai người trông thấy chuyện xảy ra, một kẻ đang bị tìm. Ngươi soi các nét trước. Khi hỏi nhân chứng, đừng cho họ xem bản chép của người kia ngay. Ta muốn biết họ đã nhìn gì, trước khi biết mình nên nhớ điều gì.

## C1-03 · Phù tín giả / ACTIVE

`DLG_C1_03_CLUE` · `NPC_HA_MAC`

Ông đưa kính qua chỗ nét khắc dừng lại, chừa vòng giữa phù cho người chơi tự nhìn.

Nếu thấy hai vết giống nhau, ghi cả chỗ khác. Một người có thể nhận đúng hình mà nhận nhầm cách tạo ra nó. Người đứng cạnh quầy và người nhìn từ cổng cũng không đứng cùng một chỗ; hỏi vị trí của họ nữa.

## C1-03 · Phù tín giả / READY_TO_TURN_IN

`DLG_C1_03_TURN_IN` · `NPC_HA_MAC`

Hạ Mặc đặt bốn bản soi theo hàng. Các điểm dừng của nét gia công trùng nhau ở những chỗ tay người thường đổi lực.

Theo khuôn máy. Ta ghi được điều ấy. Chưa ghi được tên môn phái làm ra nó.

Ông giữ cả hai lời khai với vị trí người kể, để một tờ trống cạnh tang vật của kẻ bị bắt. Còn một quãng đường từ làm phù tới đưa nó qua cổng chưa ai kể hết.

## C1-04 · Tượng mở mắt / AVAILABLE

`DLG_C1_04_OFFER` · `NPC_GUARD_CAPTAIN`

Đội trưởng kéo một người khỏi lối tượng vừa quét qua. Phù đeo trước ngực người ấy lật mặt theo cú giật.

Sáu tượng đang ép đám đông vào cọc. Phá hai cọc theo biểu tượng, mở lối cho hộ vệ còn mắc trong đó. Đừng đuổi kẻ bỏ chạy trước khi người của ta có đường ra. Ai còn đi được thì dẫn họ rời quảng trường.

## C1-04 · Tượng mở mắt / ACTIVE

`DLG_C1_04_CLUE` · `NPC_GUARD_CAPTAIN`

Đội trưởng nhấc tay ngăn một người lính đang định lao tiếp.

Tượng vừa bỏ qua anh này rồi quay sang người đeo phù. Ta chưa chắc vì sao. Khi tới cọc, nhìn biểu tượng và giữ một lối lui; không cần đưa thêm người vào giữa chúng để thử lại điều ấy.

## C1-04 · Tượng mở mắt / READY_TO_TURN_IN

`DLG_C1_04_TURN_IN` · `NPC_GUARD_CAPTAIN`

Hộ vệ ngồi dưới bậc đá, tấm phù đã gỡ đặt cạnh chiếc găng rách. Đội trưởng cúi kiểm vai anh trước khi nhận tang vật.

Hai cọc dùng dấu trên phù để chọn người. Người đeo có thể chỉ tưởng nó cho phép qua cổng. Ta sẽ hỏi sau khi họ thở được.

Ông gọi người mang nước rồi mới quay lại sắp những mảnh cọc theo đúng chỗ chúng đã đứng.

## C1-05 · Năm lời thề / AVAILABLE

`DLG_C1_05_OFFER` · `NPC_HA_MAC`

Hạ Mặc xếp năm chỗ ngồi, để khoảng giữa rộng hơn cần thiết. Không ai chịu là người đầu tiên đặt phù xuống bàn.

Hãy nghe đủ năm trưởng phái rồi tới chỗ Tượng Hành Hỏa. Nếu người này nói đã thấy, hỏi họ ở đâu. Nếu chỉ nghe báo, xin giữ cả bản báo. Ta cần đưa họ tới cùng một mối nguy, chưa cần buộc họ kể cùng một câu chuyện.

## C1-05 · Năm lời thề / ACTIVE

`DLG_C1_05_CLUE` · `NPC_HA_MAC`

Một chiếc ghế vẫn lệch khỏi bàn sau lần đối thoại trước. Hạ Mặc kê lại, để tờ ghi người nói ở đúng chỗ cũ.

Có những câu mâu thuẫn nhau mà chưa ai nói dối. Ngươi giữ riêng điều mỗi người chứng kiến. Sau trận còn phải đối với hồ sơ tháp; ta không muốn câu của người nói sau sửa mất câu người nói trước.

## C1-05 · Năm lời thề / READY_TO_TURN_IN

`DLG_C1_05_TURN_IN` · `NPC_HA_MAC`

Sau khi Tượng Hành Hỏa ngừng, năm đại diện chịu ký một thỏa thuận tạm. Trong hồ sơ đem đối, một đoạn đã mất mà mép trang vẫn liền.

Hạ Mặc: Ta sẽ giữ bản đang thiếu này. Chép lại một bản đủ đẹp bây giờ chỉ khiến không ai nhìn ra chỗ bị xóa.

Tạ gửi tới bản chép đã hẹn ở Bến Mưa, cho cả Ly An xem. Nó giữ tên Huyền Ấn nhưng chưa giải thích niêm thư. Đường hàng trên những tờ phù dẫn tiếp tới Thăng Long.

## C1-06 · Con dấu qua phố / AVAILABLE

`DLG_C1_06_OFFER` · `NPC_HA_MAC`

Hạ Mặc nhích sang tránh vệt nước từ sọt cá, rồi nhận ra chân kia vẫn đứng trong vũng. Ông mượn một chiếc ghế từ quầy, kê dưới mái hiên mới mở bọc phù.

Sổ chợ, dấu lò, trang lưu trữ. Xem riêng từng thứ rồi hãy đặt cạnh nhau. Ta chờ báo cáo ở đây, kể cả khi chúng không khớp với điều ta nghi.

## C1-06 · Con dấu qua phố / ACTIVE

`DLG_C1_06_CLUE` · `NPC_HA_MAC`

Tờ nháp trước mặt ông có một cột chưa ghi tên ai.

Xin xem cả dòng bên lề, nhất là dòng khiến người giữ sổ phải giải thích lâu hơn. Dấu nhận hàng chỉ ghi một chặng đường. Nếu hỏi người thợ về loại cây cho nhựa mà họ không biết, cứ để nguyên câu không biết ấy.

## C1-06 · Con dấu qua phố / READY_TO_TURN_IN

`DLG_C1_06_TURN_IN` · `NPC_HA_MAC`

Ba nguồn đối được đường giấy và mẫu nhựa dẫn về Lâm Triều. Chặng gia công phù vẫn còn trống. Hạ Mặc giữ cả khoản ứng nước Sầm bị bên nhận từ chối trả.

Tới đây ta theo được. Chỗ trống này giữ nguyên.

Ông chép kết luận cùng điều chưa chứng minh, không chuyển người nhận hàng sang cột người làm giả. Xong việc, ông nhấc chiếc ghế đã mượn, đợi xe đi hết mới mang trả quầy.

## C2-01 · Đội đốn cây mất tích / AVAILABLE

`DLG_C2_01_OFFER` · `NPC_FOREMAN_MOC`

Quản đốc Mộc đặt thêm một bát cơm bên rìa bàn, rồi kéo vào vì mưa hắt. Cơm của đội đốn cây đã nguội mà chưa ai về.

Họ biết đường này. Nếu chỉ gãy xe thì phải có người quay lại. Tìm ba dấu chân và hai chiếc rìu; có bốn đám Rễ Mộng ở lối ấy. Thấy dụng cụ thì nhìn quanh trước khi nhấc, đừng coi chỗ có rìu là chỗ người đã chết.

## C2-01 · Đội đốn cây mất tích / ACTIVE

`DLG_C2_01_CLUE` · `NPC_FOREMAN_MOC`

Ông thử lưỡi chiếc rìu mẫu bằng một sợi gỗ, không dùng ngón tay.

Đội ấy luôn cắm rìu ở bờ chắc khi xuống khe. Dấu chân dẫn tới đâu, nhánh cây bị gãy về phía nào, ghi cho ta. Nếu rìu còn sạch, điều đó cũng đáng mang về. Có người ở đây đã chuẩn bị lời báo tang quá sớm.

## C2-01 · Đội đốn cây mất tích / READY_TO_TURN_IN

`DLG_C2_01_TURN_IN` · `NPC_FOREMAN_MOC`

Quản đốc Mộc lau hết đất quanh cán rìu trước khi đặt lên bàn ăn. Không có máu. Rễ giữ những tiếng gọi đứt quãng ở nơi nhóm thợ biến mất.

Vậy đừng dọn bát của họ.

Ông nói với người đang thu bàn rồi nhấc áo mưa. Muốn đưa người về, phải lần tiếp phần ký ức mắc trong cây, không chỉ chặt một lối rộng hơn.

## C2-02 · Tên trên vỏ cây / AVAILABLE

`DLG_C2_02_OFFER` · `NPC_HA_MAC`

Hạ Mặc đặt bản đồ cạnh một mẩu vỏ rụng, giữ tay không cho nó cong lại. Các nét trên vỏ ngừng ở giữa một cái tên.

Tìm đủ bốn tên theo những dấu đã ghi trên bản đồ. Đừng thử bằng lưỡi kiếm lên cây khác. Nếu một nét chưa hiện, xem nước đi qua gốc nó thế nào. Ly An đang chờ đối tên; ta sẽ mang cả bản chép đọc không trọn tới cô ấy.

## C2-02 · Tên trên vỏ cây / ACTIVE

`DLG_C2_02_CLUE` · `NPC_HA_MAC`

Ông đưa giấy rời cho người chơi, không viết hộ phần cuối.

Khoảng trống cứ để trống. Cây giữ một âm nghe được không có nghĩa nó biết cả tên người. Có thể xem mô tả nét và nhịp thay vì nghe; ta cần đối điều được giữ lại, không thử tai của ngươi.

## C2-02 · Tên trên vỏ cây / READY_TO_TURN_IN

`DLG_C2_02_TURN_IN` · `NPC_HA_MAC`

Ly An đọc tên cuối rồi dừng, đem so với dòng tử trận đã lưu ba mươi năm. Chữ trên vỏ và chữ trong sổ trùng, nhưng sổ chỉ ghi người ấy đã chết.

Hạ Mặc: Ta chưa biết người trong cây còn sống hay rừng giữ tiếng của họ. Không sửa sổ bằng một điều ta muốn tin.

Ông giữ hai bản cạnh nhau, viết một câu hỏi về người đã ghi tên vào danh sách tử trận.

## C2-03 · Đường nước khóa / AVAILABLE

`DLG_C2_03_OFFER` · `NPC_WATER_KEEPER`

Người giữ nước gõ lên mặt van; tiếng kim loại bên trong không trả lại cùng nhịp.

Ba van A, B, C. Mở lần lượt rồi đưa người thợ qua, cho anh ấy đủ thời gian nối đường. Hai đợt quái có thể ép vào chỗ đang làm. Đừng kéo thợ rời vị trí mỗi khi nghe động; giữ đường cho anh ấy lui khi cần.

## C2-03 · Đường nước khóa / ACTIVE

`DLG_C2_03_CLUE` · `NPC_WATER_KEEPER`

Người giữ nước chỉ phía tay quay, rồi phía trục đã khuất sau đá.

Nếu van chịu xoay mà nước không tới, đừng thêm lực ngay. Có phần khóa ở bên trong. Đèn, biểu tượng và bản ghi nhịp cùng chỉ một việc; không nghe rõ vẫn xem được đường nước đang đi.

## C2-03 · Đường nước khóa / READY_TO_TURN_IN

`DLG_C2_03_TURN_IN` · `NPC_WATER_KEEPER`

Nước qua được ba van, để lộ dấu tay trên phần khóa phía trong. Ký hiệu cạnh đó trùng bản vẽ tháp, không trùng dấu sửa của nhóm thợ.

Người giữ nước: Ta đã kiểm phía ngoài bao lần.

Ông tự mở lại sổ bảo dưỡng, đánh dấu những lần chỉ kiểm tay quay. Người thợ ngồi xuống rửa bùn khỏi khớp ngón tay, chờ họ nhìn xong mới xin phần nước sạch đầu tiên.

## C2-04 · Ký ức người lạ / AVAILABLE

`DLG_C2_04_OFFER` · `NPC_TA_VAN_KHANH`

Tạ Vân Khanh đặt bản chép đã tìm lại lên gốc cây khô, cùng bản đối tên ở Bến Mưa. Ly An giữ một bản sao.

Ta không mang tới để hai người thôi hỏi. Chỗ này giữ nhiều phần của một buổi ký; có Rễ Mộng Tinh Anh chắn lối. Dẹp nó rồi xem đủ ba dấu ký ức. Nếu trong đó có ta, hãy hỏi ta sau khi đã nhìn hết.

## C2-04 · Ký ức người lạ / ACTIVE

`DLG_C2_04_CLUE` · `NPC_TA_VAN_KHANH`

Ông đứng ngoài chỗ rễ còn chuyển, không vội chỉ người chơi nhìn vào đâu.

Một bàn tay trên bàn chưa kể được người đứng ngoài cửa. Cũng đừng lấy hình ta khi trẻ làm lời khai thay ta. Ba dấu có thể xem lại; hai người không cần nhận lời giải thích đầu tiên ta đưa ra.

## C2-04 · Ký ức người lạ / READY_TO_TURN_IN

`DLG_C2_04_TURN_IN` · `NPC_TA_VAN_KHANH`

Ba góc của buổi ký nằm cạnh nhau: ngòi bút, cánh cửa khép, người bên ngoài chờ mà không được gọi tên. Tạ đặt tay lên bản sao hiện tại, để mọi người nhìn rõ.

Là chữ ký của ta. Ta nghĩ phong tỏa sẽ ngăn chiến tranh. Không ai ép tay ta ký. Sau đó ta đã chọn không hỏi những người ngoài cửa đi đâu.

Ly An kéo bản sao về phía mình. Cô không nói tha thứ; cô hỏi ai còn giữ danh sách để họ tới đối.

## C2-05 · Mạch suối trở lại / AVAILABLE

`DLG_C2_05_OFFER` · `NPC_FOREMAN_MOC`

Quản đốc Mộc buộc áo mưa trên vai thay vì cất, chừa hai tay để đỡ người trở về.

Cổ thụ vẫn chặn nguồn. Hạ được nó thì phá ba rễ phát sáng theo thứ tự, rồi chạm lại suối. Đừng đưa đội thợ băng qua trước khi nước thông; ta sẽ đón họ ở phần bờ đã chắc.

## C2-05 · Mạch suối trở lại / ACTIVE

`DLG_C2_05_CLUE` · `NPC_FOREMAN_MOC`

Ông đưa một bát nước đục ra chỗ sáng, nhìn lớp cặn rơi.

Khi nước tới gốc nào, nghe hoặc đọc lại tên ở gốc ấy. Rễ đã ngừng đánh chưa có nghĩa người trong đó đã tự tìm được lối ra. Ta đợi tín hiệu từ nguồn, không đợi tiếng hò thắng trận.

## C2-05 · Mạch suối trở lại / READY_TO_TURN_IN

`DLG_C2_05_TURN_IN` · `NPC_FOREMAN_MOC`

Nước sạch đi qua chân cây, những tiếng gọi rời khỏi rễ từng quãng. Một gốc vẫn im vì chưa ai đọc được tên. Trong bản nhật ký tìm thấy, Cơ Vô Tướng ghi đã rút mạch để cứu một vùng khác.

Quản đốc Mộc: Vùng ấy ở đâu?

Ông không gấp áo của người còn thiếu vào cùng đồ tìm được. Đường tới Sa Hỏa mở, nhưng người ở rừng vẫn cần được tìm và được gọi đúng tên.

## C3-01 · Đoàn xe cạn nước / AVAILABLE

`DLG_C3_01_OFFER` · `NPC_SAM_CHU_QUY`

Sầm Chủ Quỹ nhấc nắp bồn, nghiêng tới khi một vệt nước mỏng chạm đáy gáo. Ông nhìn đoàn xe rồi đậy lại, không mời ai uống thử.

Lấy ba bồn còn dùng được. Qua Sa Khô thì nhanh nhưng có tinh anh; qua Hẻm Tro xa hơn, dọc đường có chỗ lấy vật liệu. Chọn đường nào cũng phải đưa xe qua hai đợt. Ta đi cùng xe, không chờ các vị ở đầu kia.

## C3-01 · Đoàn xe cạn nước / ACTIVE

`DLG_C3_01_CLUE` · `NPC_SAM_CHU_QUY`

Ông vạch hai đường lên cát rồi chèn nắp bồn để gió khỏi xóa ngã rẽ.

Đừng đổi đường giữa lúc người sau chưa nghe. Đi nhanh mà một xe rẽ lạc thì tới nơi vẫn thiếu nước. Người dẫn cuối đoàn cũng phải biết quyết định vừa rồi.

## C3-01 · Đoàn xe cạn nước / READY_TO_TURN_IN

`DLG_C3_01_TURN_IN` · `NPC_SAM_CHU_QUY`

Sầm đếm người xuống xe trước, rồi mới đếm bồn. Một người giơ gáo trả; ông bảo giữ lại tới khi được chia nước.

Chuyến này đủ người. Phần bồn sứt để riêng, đừng ghi như đã giao nguyên.

Ông lấy cuốn sổ có khoản ứng từ Thăng Long, mở thêm một dòng. Bên nhận vẫn có thể từ chối trả khoản nước của người quay lại, nhưng ông đã để cột ấy sẵn.

## C3-02 · Tro trong phổi / AVAILABLE

`DLG_C3_02_OFFER` · `NPC_MEDIC_SA_HOA`

Dược sư Sa Hỏa giũ một mặt nạ trên tấm vải trắng. Tro rơi xuống thành vệt, vẫn còn lọt qua đường may.

Tìm năm mặt nạ còn dùng được và đưa bốn thợ ra theo vùng thông gió. Ai hụt hơi thì ngồi ở đó trước, đừng kéo chạy qua đoạn độc. Tôi còn phải sửa những cái này, không thể phát cho họ một tấm vải rồi coi như đã bảo vệ được.

## C3-02 · Tro trong phổi / ACTIVE

`DLG_C3_02_CLUE` · `NPC_MEDIC_SA_HOA`

Dược sư kéo rèm về phía luồng gió sạch.

Hỏi họ trước khi tháo mặt nạ. Có người vẫn muốn quay vào vì đường nước khu nhà họ chạy qua lò. Họ cần biết lối ra còn mở; mắng họ tham việc không giúp ai thở được hơn.

## C3-02 · Tro trong phổi / READY_TO_TURN_IN

`DLG_C3_02_TURN_IN` · `NPC_MEDIC_SA_HOA`

Bốn người có chỗ ngồi trong luồng gió sạch. Một người hỏi ca sau ai giữ nước, chưa hỏi tiền công. Dược sư đặt cốc xuống đủ gần để anh không phải đứng dậy.

Họ ở lại vì nhà vẫn chờ nước từ lò. Tôi ghi việc ấy vào báo cáo, cùng chỗ mặt nạ hở. Đừng chỉ ghi rằng đã cứu được bốn người rồi dọn chỗ này đi.

## C3-03 · Bản khắc dưới lò / AVAILABLE

`DLG_C3_03_OFFER` · `NPC_HA_MAC`

Hạ Mặc đặt ba miếng gỗ trống cạnh nhau để thử chỗ ghép, còn để nguyên giấy bọc quanh bàn.

Người Canh Lò giữ phía dưới. Qua được chỗ ấy, mang ba bản khắc về đây ghép. Ta muốn đọc phần cấp nước và phần sửa sau đó trên cùng một mặt, trước khi ai tách chúng thành hai câu chuyện dễ kể hơn.

## C3-03 · Bản khắc dưới lò / ACTIVE

`DLG_C3_03_CLUE` · `NPC_HA_MAC`

Ông kiểm mép một bản chép cũ, để ngón tay ngoài đường chữ.

Nếu lớp khắc sau đè lên lớp trước, hãy chép cả hai và ghi thứ tự. Phần được sửa có thể chỉ là số giao nhận. Ta chưa biết nó đổi điều gì, cũng chưa được phép làm cho mặt bàn phẳng bằng cách gọt mất một lớp.

## C3-03 · Bản khắc dưới lò / READY_TO_TURN_IN

`DLG_C3_03_TURN_IN` · `NPC_HA_MAC`

Ba bản ghép thành lời ghi công Cơ Vô Tướng đã cho nước miễn phí. Bên cạnh là vết sửa hạn mức về sau, sâu hơn nét cũ.

Hạ Mặc: Những người nhận nước nhớ đúng chuyện ông ấy đã làm. Phần sửa này cũng có thật.

Ông giữ hai lớp trong cùng bản chép, chừa phần người đã ký để tiếp tục đối. Không cần xóa một việc tốt để bắt đầu hỏi cái giá người khác đang trả.

## C3-04 · Ba van lửa / AVAILABLE

`DLG_C3_04_OFFER` · `NPC_FORGE_MASTER`

Lò chủ thử tay quay bằng chiếc kẹp dài, lùi khỏi hơi nóng trước khi đưa người khác tới.

Ba van, mỗi van cần được giữ đủ hai mươi giây khi đợt quái tới. Chia người trước. Ai giữ van phải có người nhìn lối lui; ta không muốn họ buông vì cả nhóm chạy theo một mục tiêu bên ngoài.

## C3-04 · Ba van lửa / ACTIVE

`DLG_C3_04_CLUE` · `NPC_FORGE_MASTER`

Ông gõ ba tiếng trên ống, chờ tiếng trả lại rồi mới chỉ vào đèn báo.

Nghe không rõ thì xem biểu tượng ấy. Nó ghi cùng nhịp. Trước khi đổi người giữ, gọi người tới thay và đợi tay họ vào đúng chỗ. Một van đã xong không có nghĩa hai van còn lại tự biết việc của nhau.

## C3-04 · Ba van lửa / READY_TO_TURN_IN

`DLG_C3_04_TURN_IN` · `NPC_FORGE_MASTER`

Ba van giữ được nhịp. Lò chủ không quay thêm nấc nào; ông để người đang giữ rút tay lần lượt rồi mới đóng chốt.

Được rồi. Gọi đủ người ra đây.

Ông đếm những chiếc kẹp đặt vào khay, dừng ở chiếc còn thiếu. Đường tới Lò Trời đã mở nhưng ông vẫn chờ người cuối qua lối nóng mới bước tiếp.

## C3-05 · Lò Trời / AVAILABLE

`DLG_C3_05_OFFER` · `NPC_FORGE_MASTER`

Lò chủ vạch ba vùng trên mặt bàn đầy tro: giáp, van, dòng lửa. Ông phủ tay lên phần đường rút đang bị một dụng cụ che.

Qua giáp rồi tới van, cuối cùng mới có chỗ tránh dòng lửa. Ba pha, đừng lấy cách qua pha đầu dùng suốt trận. Lõi giữ đường nước ở phía trong; người của khu nhà vẫn cần nó hoạt động khi chúng ta rời đi.

## C3-05 · Lò Trời / ACTIVE

`DLG_C3_05_CLUE` · `NPC_FORGE_MASTER`

Ông giữ bản nhật ký trong bọc, chưa mở trước những người vẫn đang làm cạnh lò.

Đường làm việc chưa yên thì để giấy ở đây. Muốn đọc lại nhịp van hay hướng tránh, dùng cả dấu hình. Chưa phải lúc bảo người đang giữ vị trí quay lại nghe hết một câu chuyện.

## C3-05 · Lò Trời / ACTIVE

`DLG_C3_05_CHOICE` · `NPC_FORGE_MASTER`

Nhật ký có phần được công bố và tên người cần bảo vệ. Công bố phải giữ danh tính theo lời người kể; giao hội đồng phải có biên nhận và một bản sao ở nơi khác. Lựa chọn cần được ghi nhận cùng tiến độ, không đổi chiến lợi phẩm.

## C3-05 · Lò Trời / READY_TO_TURN_IN

`DLG_C3_05_TURN_IN` · `NPC_FORGE_MASTER`

Sau trận, hơi nóng rút khỏi bàn ghép. Nhật ký có cả trang người ta muốn công bố lẫn tên những người vẫn sống gần lò. Lò chủ đưa hai bìa giữ giấy.

Công bố thì giữ tên người làm chứng an toàn. Giao hội đồng thì lấy biên nhận và giữ một bản sao. Chọn cách nào cũng đừng để chỉ một nơi còn giữ được giấy.

Ngoài lối nóng, tiếng gọi chia nước đã trở lại.

## C4-01 · Dân qua cổng / AVAILABLE

`DLG_C4_01_OFFER` · `NPC_REFUGEE_LEADER`

Người dẫn dân buộc một dải vải lên xe cuối, để người phía sau còn thấy chỗ đoàn rẽ.

Ba nhóm còn ở ngoài. Đưa từng nhóm tới cổng trú, mở đường khi phục kích tới. Tôi đếm ở cửa; nếu thiếu người, báo từ nhóm nào trước khi đi tìm. Đừng gọi mọi người là một đoàn rồi chỉ nhìn người tới đầu tiên.

## C4-01 · Dân qua cổng / ACTIVE

`DLG_C4_01_CLUE` · `NPC_REFUGEE_LEADER`

Người dẫn dân giữ hai tờ lệnh do lính hai phía đưa, mép giấy đã nhàu vì bị giằng xem.

Họ đều bảo mình chấp hành lệnh. Tôi chỉ cần biết nhóm nào được qua cửa tiếp. Muốn hỏi lính, hỏi cả giờ nhận giấy và ai còn đứng đó; đừng đưa chuyện ấy vào lúc người sau đang mắc ngoài đường.

## C4-01 · Dân qua cổng / READY_TO_TURN_IN

`DLG_C4_01_TURN_IN` · `NPC_REFUGEE_LEADER`

Ba nhóm vào được chỗ trú. Người dẫn dân còn giữ dải vải của xe cuối trong tay, kiểm tên những người ngồi khuất sau thùng.

Lệnh bên này và bên kia có những câu giống hệt, cả chỗ viết lặp. Tôi giữ cả hai. Người đưa chúng đang ở hai chỗ khác nhau; họ chưa từng gặp nhau lúc nhận.

Ly An ở lại cửa, gạch thêm một người đã qua trước khi khép sổ.

## C4-02 · Mệnh lệnh không dấu / AVAILABLE

`DLG_C4_02_OFFER` · `NPC_TA_VAN_KHANH`

Tạ Vân Khanh để ba bản lệnh dưới những hòn chặn giấy khác nhau. Ông viết giờ đóng cổng lên một tờ rời, không chèn vào bản gốc.

Hỏi hai sứ giả riêng, đối ba bản với dấu sáp gốc. Ta sẽ ghi tên người nhận lời khai. Nếu có chỗ sửa, phải nhìn được ai sửa lúc nào; ta không muốn mang thêm một tờ lệnh không ai chịu nhận đã ký.

## C4-02 · Mệnh lệnh không dấu / ACTIVE

`DLG_C4_02_CLUE` · `NPC_TA_VAN_KHANH`

Ông đặt một tờ sao trước người chơi nhưng giữ cả phần bị gạch của mình.

Đừng chỉ hỏi họ có biết giấy giả không. Hỏi lúc nhận, dấu còn mềm hay đã khô; cửa đã đóng hay chưa. Hai người có thể đều tưởng mình mang lệnh thật. Ta cần đối được giờ trước khi hỏi điều họ không thể biết.

## C4-02 · Mệnh lệnh không dấu / READY_TO_TURN_IN

`DLG_C4_02_TURN_IN` · `NPC_TA_VAN_KHANH`

Giờ đóng cổng và vết bụi kim loại trong sáp đưa đường dấu về phòng chỉ huy. Ba bản lệnh không chỉ giống nhau ở câu chữ; chúng cùng lệch với dấu gốc.

Tạ Vân Khanh: Ta sẽ giữ nguyên hai lời khai ban đầu. Người chuyển giấy chưa phải người đặt lệnh.

Ông viết tên mình vào phần nhận trách nhiệm đối chứng, rồi mới cho sao bản tiếp theo.

## C4-03 · Ba cổng thành / AVAILABLE

`DLG_C4_03_OFFER` · `NPC_GUILD_SCOUT`

Trinh sát bang hội vẽ Đông, Tây, Nam lên mặt nắp thùng, kê hai mũi tên gãy vào chỗ ụ nỏ cần sửa.

Năm người, chia trước khi chạy. Giữ được cổng nào thì báo cổng ấy, đừng để cả nhóm cùng đuổi theo một lời gọi. Bốn phút, hai ụ nỏ. Ta dẫn qua đường tiếp tế, không cần các vị có cùng tên bang mới đứng được cạnh nhau.

## C4-03 · Ba cổng thành / ACTIVE

`DLG_C4_03_CLUE` · `NPC_GUILD_SCOUT`

Trinh sát đẩy chiếc thùng tránh lối người khiêng thương.

Mất một cổng thì gọi hướng còn đi được, rồi vòng lại. Người sửa nỏ phải nghe được người giữ đường. Đừng chỉ báo còn bao nhiêu địch; báo cả chỗ người mình có thể tới thay.

## C4-03 · Ba cổng thành / READY_TO_TURN_IN

`DLG_C4_03_TURN_IN` · `NPC_GUILD_SCOUT`

Trinh sát xóa một đường cũ trên nắp thùng, vẽ lại lối đã dùng để vòng qua cổng mất.

Đường này giữ được vì phía Nam gọi kịp. Ta ghi lại cho nhóm sau, cả lần ta dẫn nhầm vào lối đã khóa.

Hai ụ nỏ hoạt động, nhưng người khiêng thương vẫn đi qua trước xe tiếp tế. Những người giữ ba hướng có tên riêng trong bản báo.

## C4-04 · Cờ trên tường / AVAILABLE

`DLG_C4_04_OFFER` · `NPC_CAPTAIN_TRAN_SON`

Đội trưởng Trấn Sơn nhặt chiếc cán cờ đang chắn cửa kho, dựng nó tựa vào vách thay vì giương ngay.

Lấy lại kho tiếp tế, phá cổng để người bên trong ra, rồi đưa cờ lên tháp. Việc hôm nay không cần một bang đứng tên. Tôi sẽ nhận người ở dưới; ai còn mắc trong kho thì phải biết cửa mở về phía nào.

## C4-04 · Cờ trên tường / ACTIVE

`DLG_C4_04_CLUE` · `NPC_CAPTAIN_TRAN_SON`

Ông kéo tấm bạt che lối cáng, chỉ vào những thùng có thể chèn giữ cổng.

Cờ chưa lên thì cứ báo kho đã thông. Đừng chờ đủ một cảnh đẹp mới cho người ra. Người ở tháp cần nghe tình hình dưới chân tường, không chỉ nhìn tín hiệu trên đầu mình.

## C4-04 · Cờ trên tường / READY_TO_TURN_IN

`DLG_C4_04_TURN_IN` · `NPC_CAPTAIN_TRAN_SON`

Cờ đã lên. Đội trưởng đứng ở cửa kho đợi chiếc cáng cuối, tay vẫn giữ cánh cổng bị lệch.

Tôi nghe người ngoài đường bảo thành đã có chủ. Trong kho còn người chờ phần nước tối nay. Ta làm xong việc ấy trước.

Ông giao lại danh sách tiếp tế, giữ cả những dòng người ký lệnh cũ đã bỏ qua. Đường tới phòng chỉ huy giờ không còn bị khóa.

## C4-05 · Thiết Giáp Tướng / AVAILABLE

`DLG_C4_05_OFFER` · `NPC_TONG_BANH`

Tống Bành đặt tay lên mặt giáp, nhìn con đường người tị nạn vừa đi qua rồi quay lại phòng chỉ huy.

Các ngươi đã mở cổng. Giờ ai sẽ bảo được người ở ba cổng cùng dừng tay? Phá được hai bẫy giáp thì tới đây. Ta không trốn sau một tờ lệnh khác.

## C4-05 · Thiết Giáp Tướng / ACTIVE

`DLG_C4_05_CLUE` · `NPC_TONG_BANH`

Ông giữ vị trí phía sau hai cơ cấu giáp, không gọi thêm lính dưới cửa lên chịu đòn.

Nếu định hỏi con dấu, giữ nó nguyên sau trận. Đừng đập mất rồi xin những kẻ đã chạy qua cổng kể lại cho vừa điều các ngươi cần chứng minh.

## C4-05 · Thiết Giáp Tướng / READY_TO_TURN_IN

`DLG_C4_05_TURN_IN` · `NPC_TONG_BANH`

Tống tháo găng trước khi đặt con dấu xuống. Ông nhận đã dùng lệnh giả để gom quân cho Cơ, rồi vẫn nói chỉ một mệnh lệnh mới chấm dứt được cảnh lính chết ở các cổng.

Người chơi có thể đối lại bằng những đoàn dân đã bị chặn và lời hai sứ giả. Ông chưa có câu đáp cho số người mất vì chính lệnh ấy.

Bản đồ năm tháp được giữ cùng thư lệnh; Tống không bước sang hàng người đồng hành.

## C5-01 · Đài Lặn / AVAILABLE

`DLG_C5_01_OFFER` · `NPC_DIVER_LEAD`

Đội trưởng thợ lặn thử khóa bình khí, đưa mặt khóa lên để người mới nhìn thấy chỗ đã kiểm.

Tìm đủ ba người, nhận bình rồi mới mở cửa phế tích. Ai nghe tiếng lạ thì chỉ cả hướng và độ sâu, đừng tách nhóm đi theo. Có người bảo dưới đó ngân như chuông ở Bến Mưa; tôi muốn nghe họ kể khi đã lên chỗ thở được.

## C5-01 · Đài Lặn / ACTIVE

`DLG_C5_01_CLUE` · `NPC_DIVER_LEAD`

Ông lần tay theo dây phơi cũ được người lặn dùng làm đường dẫn, ngừng ở chỗ nút đã sờn.

Bình có thể cấp lại. Người lạc khỏi đường thì khó hơn. Theo dấu hình và mô tả độ sâu, không cần nghe được đúng nốt ngân. Thấy đồ đang buộc xuống sàn, cứ để nó yên trước khi biết nó giữ lối nào.

## C5-01 · Đài Lặn / READY_TO_TURN_IN

`DLG_C5_01_TURN_IN` · `NPC_DIVER_LEAD`

Ba người và bình khí được ghi nhận trước cửa phế tích. Sau lớp nước, những dây phơi chạy ngang qua chỗ từng là hiên nhà.

Đội trưởng: Họ đã dùng thứ còn có trong nhà để giữ đường. Đánh dấu lại, đừng gọi tất cả là đống đổ nát.

Tiếng ngân giống ở bến trở lại trong bản kể, nhưng lần này có vị trí và người nghe cụ thể để đối.

## C5-02 · Ba buồng áp suất / AVAILABLE

`DLG_C5_02_OFFER` · `NPC_DIVER_LEAD`

Đội trưởng thợ lặn đặt ba mẫu ký hiệu trên bàn, lật sang mặt nổi để người đeo găng vẫn phân biệt được.

Ba trạm áp suất, hai đợt triều phải trú. Nhìn cả đèn lẫn biểu tượng; chúng báo cùng một hướng. Đừng lấy việc nghe đúng tiếng van làm điều kiện cho người khác được đi tiếp.

## C5-02 · Ba buồng áp suất / ACTIVE

`DLG_C5_02_CLUE` · `NPC_DIVER_LEAD`

Ông kiểm khoảng cách giữa hai dấu trú trên sơ đồ.

Qua trạm nào thì xác nhận trạm ấy. Nước sắp đổi mà người sau chưa tới, báo họ chỗ trú gần nhất. Một căn phòng đã mở không có nghĩa triều sẽ đợi cả nhóm đi qua.

## C5-02 · Ba buồng áp suất / READY_TO_TURN_IN

`DLG_C5_02_TURN_IN` · `NPC_DIVER_LEAD`

Ba trạm giữ được áp. Ánh đèn trong buồng đủ để thấy bàn ăn vẫn buộc xuống sàn, một chiếc ghế nghiêng theo dây.

Đội trưởng: Chừa chỗ này trong bản vẽ. Người từng sống ở đây còn cần nhận ra nhà mình.

Ông cho đội nghỉ trong buồng đã ổn định, không giục họ bơi thẳng qua những dấu sinh hoạt vừa nhìn thấy.

## C5-03 · Người viết nhật ký / AVAILABLE

`DLG_C5_03_OFFER` · `NPC_HA_MAC`

Hạ Mặc đặt bút xuống khi người giữ nhật ký chưa chịu đưa trang cuối.

Ta muốn ghép bốn trang và đối ngăn cất phía trong. Nhưng ngươi có quyền nói phần nào không được chép tên. Ta sẽ ghi điều ấy trước, rồi mới nhờ người chơi tìm những mảnh còn thiếu.

## C5-03 · Người viết nhật ký / ACTIVE

`DLG_C5_03_CLUE` · `NPC_HA_MAC`

Ông dùng giấy rời thử vị trí hai mảnh, không dán lên bản gốc.

Có chỗ chữ mất vì nước, có chỗ dòng bị cắt trước khi ngấm. Phải phân biệt hai việc. Người sống sót không cần mở hết ký ức để chứng minh mình có quyền ở đây; hỏi lại trước khi mang lời họ sang người khác.

## C5-03 · Người viết nhật ký / READY_TO_TURN_IN

`DLG_C5_03_TURN_IN` · `NPC_HA_MAC`

Bốn trang và phần cất riêng cho thấy người sống sót đã bị ghi thành người chết để che lỗi thí nghiệm. Người giữ lời kể nhận lá thư đương thời Ly An đã mang: họ gửi cho Tạ, đòi đối danh sách có chữ ký ông. Niêm năm vạch được lấy theo dấu trên giấy xác nhận cũ, để người nhận chịu mở cuộc đối chứng.

Ly An: Vậy tên nào tôi được ghi ở bản gửi lại?

Hạ Mặc đặt bút xuống chờ câu trả lời, không lấy việc nhận thư làm sự đồng ý công khai danh tính. Một bản hồi đáp được giữ cho người gửi, bản chứng cứ đi tiếp cùng sự chấp thuận rõ về phần được chép.

## C5-04 · Lời khai năm môn phái / AVAILABLE

`DLG_C5_04_OFFER` · `NPC_HA_MAC`

Hạ Mặc tách năm bộ sao, giữ cùng một danh mục những phần đã được người kể cho phép dùng.

Mang tới từng trưởng phái. Nghe hết câu trả lời riêng của họ trước khi cho người sau biết. Ta cần năm cuộc đối chứng, không cần một buổi họp mà người nói đầu quyết định ai còn được nhớ gì.

## C5-04 · Lời khai năm môn phái / ACTIVE

`DLG_C5_04_CLUE` · `NPC_HA_MAC`

Ông đặt cạnh mỗi bộ sao một tờ trống để ghi lời đáp.

Họ được quyền sửa điều mình nhớ sai, nhưng phải nhìn thấy phần trước khi sửa. Đừng đổi một lời xin lỗi lấy việc gỡ trang chứng cứ. Ai hứa tới làm chứng thì ghi cả nơi và người sẽ nhận họ.

## C5-04 · Lời khai năm môn phái / READY_TO_TURN_IN

`DLG_C5_04_TURN_IN` · `NPC_HA_MAC`

Năm lời đáp có phần nhận lỗi khác nhau, có câu vẫn tránh chủ ngữ. Hạ Mặc giữ chúng nguyên, đặt cạnh những chứng cứ tương ứng.

Họ đã chịu đối chứng. Việc sửa sổ, gọi lại người sống và giữ lời ra làm chứng còn ở phía trước.

Bộ sao được chuyển tiếp với danh mục người giữ; không trưởng phái nào mang hết bản duy nhất về tháp mình.

## C5-05 · Mẫu Xà Thủy / AVAILABLE

`DLG_C5_05_OFFER` · `NPC_DIVER_LEAD`

Đội trưởng thợ lặn đứng ngoài vùng triều đổi, chờ dải sáng nằm ổn định mới chỉ đường.

Mẫu Xà giữ lõi Thủy phía trong. Nước rút thì vào vùng sáng; nó cắm đầu mới có chỗ phá vảy. Đừng đuổi theo thân nó qua phần không còn đường thở. Chúng ta cần đưa dòng trở lại, không mang một thân linh thú lên làm chiến tích.

## C5-05 · Mẫu Xà Thủy / ACTIVE

`DLG_C5_05_CLUE` · `NPC_DIVER_LEAD`

Ông giữ bàn tay trên ký hiệu trú thay vì vẽ mũi tên lao vào.

Đối nhịp nước bằng đèn, hình hoặc mô tả. Lõi đang giữ cho một phần buồng không sập; khi trận chưa xong, đừng coi mọi vật sáng đều đã được phép lấy đi.

## C5-05 · Mẫu Xà Thủy / READY_TO_TURN_IN

`DLG_C5_05_TURN_IN` · `NPC_DIVER_LEAD`

Khi dòng đã được điều hòa và lõi Thủy được nhận, một lớp ký ức cho thấy linh thú từng cuộn quanh chỗ nước yếu để giữ nó. Hình ấy rời đi theo triều, không biến trận vừa qua thành lỗi lầm cần xóa.

Đội trưởng: Ta sẽ chép nó đã giữ chỗ này. Và chép cách chúng ta đổi dòng, để người sau không tháo lõi mà không biết mình đang tháo gì.

## C6-01 · Năm đội, năm tháp / AVAILABLE

`DLG_C6_01_OFFER` · `NPC_LYAN`

Ly An trải năm chỗ trống trên bàn nhận tin, mỗi chỗ giữ giấy từ một hướng tháp. Có nơi đã có hai người ký, có nơi mới gửi được một dấu nhận.

Bạn làm phần trụ của mình, tôi đưa tin sang những lối khác. Đừng chờ tất cả phải đứng cùng một chỗ mới tính là có mặt. Tôi cần biết cả trạm nào chưa nhận được hồi đáp.

## C6-01 · Năm đội, năm tháp / ACTIVE

`DLG_C6_01_CLUE` · `NPC_LYAN`

Cô buộc lại xấp giấy theo nơi đến, bỏ cách xếp người gửi từ lâu đã quen tay.

Đã có người tới trước ở hướng khác. Phần của bạn vẫn cần. Nếu một dấu chưa tới, tôi sẽ đi hỏi; bạn đừng tự bỏ trụ chạy theo nơi đông nhất. Người ở đó cũng chưa biết bên này đang thiếu ai.

## C6-01 · Năm đội, năm tháp / READY_TO_TURN_IN

`DLG_C6_01_TURN_IN` · `NPC_LYAN`

Năm trụ đã nhận đủ đóng góp cho chặng hiện tại. Ly An vẫn chừa một xấp hồi đáp, không trộn vào giấy báo đã gửi.

Tôi mang kết quả sang từng hướng rồi mới khép sổ. Người không đứng cạnh cổng cũng phải biết phần việc của họ đã được nhận.

Cô đưa bạn xem dấu trả lời đầu tiên, để cả mặt sau nơi người giữ trạm đã sửa một tên bị chép thiếu.

## C6-02 · Cửa mạch mở / AVAILABLE

`DLG_C6_02_OFFER` · `NPC_TA_VAN_KHANH`

Tạ Vân Khanh nhận vị trí bên người giữ cửa, đặt bản lệnh có tên mình xuống trong tầm nhìn của họ.

Ba đợt, giữ ít nhất hai trong ba cột đủ một phút. Ta nhận phần cứu hộ ở đây. Khi có lệnh đổi vị trí, người nghe phải biết ai phát và vì sao; ta không ký thay một hội đồng vắng mặt nữa.

## C6-02 · Cửa mạch mở / ACTIVE

`DLG_C6_02_CLUE` · `NPC_TA_VAN_KHANH`

Ông đỡ một thanh chèn cửa cho người bên cạnh đổi tay.

Đường lui phải còn ngay cả khi cột gần nhất mất. Gọi cột nào đang giữ, cột nào cần thay. Đừng chuyển cả nhóm theo một tiếng hô không có người nhận trách nhiệm.

## C6-02 · Cửa mạch mở / READY_TO_TURN_IN

`DLG_C6_02_TURN_IN` · `NPC_TA_VAN_KHANH`

Cửa mạch mở sau khi các cột giữ được nhịp. Tạ không thu bản ghi cứu hộ về riêng; ông trao cho người cùng giữ cửa đối lại.

Ta ở đây những lúc này. Nếu có đoạn không đúng, sửa trước khi ký.

Đường vào trong đã thông, còn bản lệnh mới phải ghi được những người đã làm nó thành thật.

## C6-03 · Lõi môn phái / AVAILABLE

`DLG_C6_03_OFFER` · `NPC_MASTER_BY_PLAYER_CLASS`

Người thầy đặt mảnh lõi cạnh dụng cụ đã sứt từ những lần tập.

Ba việc của lớp ngươi phải được làm đúng bằng điều đã học. Khi dùng sức mạnh để giữ người khác qua đường, ngươi sẽ phải chừa phần mình từng quen giữ cho một đòn riêng. Mảnh lõi không đổi môn phái đã chọn; nó cần cách ngươi dùng môn phái ấy.

## C6-03 · Lõi môn phái / ACTIVE

`DLG_C6_03_CLUE` · `NPC_MASTER_BY_PLAYER_CLASS`

Người thầy kiểm lại một dấu chỉ vị trí dân đang trú, rồi để người chơi tự nhìn những đường còn đi được.

Ta có thể nhắc động tác. Ta không thể đứng ở cả ba chỗ cho ngươi. Làm xong việc nào thì xác nhận việc ấy; đừng mang một lần ra tay đúng làm câu trả lời cho mọi tình huống.

## C6-03 · Lõi môn phái / READY_TO_TURN_IN

`DLG_C6_03_TURN_IN` · `NPC_MASTER_BY_PLAYER_CLASS`

Ba mục tiêu của lớp đã hoàn thành. Người thầy đưa mảnh lõi bằng hai tay, chờ người giữ đường bên cạnh có chỗ đặt xuống trước.

Ngươi đã chọn để người qua trước. Ta ghi việc đó, không ghi rằng từ nay ngươi không bao giờ chọn sai.

Mỹ phẩm được nhận theo kết quả riêng; phần lõi đi tiếp cùng những người từ các lớp khác.

## C6-04 · Người muốn cứu thế giới / AVAILABLE

`DLG_C6_04_OFFER` · `NPC_CO_VO_TUONG`

Cơ Vô Tướng đứng cạnh đường mạch đang bị kéo về một tâm. Trên bàn tay ông còn vết giữ van, cũ hơn những dấu vừa có trong trận.

Các ngươi đã tới những nơi từng chờ nước. Ta cũng đã đứng ở đó khi chẳng ai trả lời. Nếu muốn ta dừng, hãy bước qua phần lực ta đang giữ. Ta không nhường nó chỉ vì thêm một lời hứa.

## C6-04 · Người muốn cứu thế giới / ACTIVE

`DLG_C6_04_CLUE` · `NPC_CO_VO_TUONG`

Một hình ký ức mở ra với khoảng nhìn bị chắn: bàn chia nước, một người đứng đợi, tờ đơn được đẩy qua rồi giữ dưới tay. Chưa đủ để biết tất cả ai đã nói gì.

Cơ Vô Tướng: Xem cho hết phần các ngươi được thấy. Đừng chỉ giữ cảnh ta đưa gáo nước rồi gọi mọi điều sau đó là cùng một việc.

## C6-04 · Người muốn cứu thế giới / READY_TO_TURN_IN

`DLG_C6_04_TURN_IN` · `NPC_CO_VO_TUONG`

Sau pha giao chiến và những mảnh ký ức, lời xin dừng thí nghiệm vẫn nằm dưới bàn tay Cơ. Ông đã biết có người từ chối và đã giữ quyền quyết định cho mình.

Người chơi có thể đối bằng nguồn nước Sa Hỏa và dòng bị rút ở Lâm Triều. Việc cứu được một nơi không làm người ở nơi khác biến mất khỏi phép tính.

Cơ đặt tay lên đường mạch cuối. Ông còn phải giúp ổn định nó, rồi ra làm chứng về những điều đã làm.

## C6-05 · Huyền Ấn mới / AVAILABLE

`DLG_C6_05_OFFER` · `NPC_LYAN`

Ly An đặt năm bộ tin nhận cạnh sơ đồ trụ, để những người giữ mỗi hướng tự kiểm phần mình.

Mười người chia nhóm trước khi vào. Ba kẻ đục mạch phải bị ngắt, rồi mới qua được ba pha của cơ chế cuối. Tôi nhận tin ở sảnh; nếu một nhóm không nghe được nhóm kia, báo về đây, đừng cứ nộp thêm lực vào chỗ đang khóa.

## C6-05 · Huyền Ấn mới / ACTIVE

`DLG_C6_05_CLUE` · `NPC_LYAN`

Cô giữ bút trên mặt giấy có hai chiều mũi tên.

Bạn không cần ôm hết lõi chạy về một tâm. Người giữ bên kia phải được biết bên này đã đổi gì. Sau trận còn có sổ người sống sót phải sửa và những lời khai phải nhận. Cứ giữ đường trao đổi ấy mở cho tới khi tất cả ra được.

## C6-05 · Huyền Ấn mới / READY_TO_TURN_IN

`DLG_C6_05_TURN_IN` · `NPC_LYAN`

Sau xác nhận trận cuối, các dòng bắt đầu trao đổi thay vì dồn vào một chủ nhân. Ly An ghi những người đã ra sảnh, chừa chỗ cho người rời trước được xem lại câu chuyện. Cơ được đưa đi làm chứng và chịu xét xử; Tạ còn sống để đối danh sách đã ký.

Ly An: Tôi có thư gửi đi. Lần này có cả giấy để họ trả lời.

Nước ở các vùng chưa hồi ngay. Một người sửa lại tên mình trong sổ, mực mới còn chưa khô.

## SQ-BM-01 · Lưới rách / AVAILABLE

`DLG_SQ_BM_01_OFFER` · `NPC_FISHER_01`

Ngư phủ trải tấm lưới lên hai đầu gối, để riêng những mắt còn nối được.

Năm mảnh trôi dọc bờ tây là đủ vá chỗ này. Đừng gom cả lau vào giỏ; dây lưới mắc thì gỡ từ chỗ nút. Tôi còn chiếc đò, nhưng thiếu lưới thì ngày mai cũng phải đứng nhìn nước.

## SQ-BM-01 · Lưới rách / ACTIVE

`DLG_SQ_BM_01_CLUE` · `NPC_FISHER_01`

Ông luồn thử ngón tay qua một mắt đã sờn rồi buông ra.

Mảnh ngắn cũng giữ lại. Có chỗ chỉ cần nối một gang tay. Thứ nhìn từ xa tưởng rác có khi là đầu dây cả tấm còn đang bám.

## SQ-BM-01 · Lưới rách / READY_TO_TURN_IN

`DLG_SQ_BM_01_TURN_IN` · `NPC_FISHER_01`

Ngư phủ so năm mảnh theo độ giãn, dành mảnh còn chắc cho chỗ kéo nặng.

Đủ để vá. Tôi không thả tối nay đâu, nước còn lạ.

Ông treo lưới lên chỗ cao cho khô, để người chèo đò đi qua mà không phải cúi tránh như trước.

## SQ-BM-02 · Đèn cho người lạc / AVAILABLE

`DLG_SQ_BM_02_OFFER` · `NPC_FISHER_01`

Ngư phủ che ngọn đèn trong hai bàn tay trước khi đưa ra hiên.

Từ bến tới đầm còn ba đèn chưa cháy, có ba Cá Linh cứ ép sát lối. Giúp thắp lại cho người về muộn nhìn thấy bờ. Đừng châm rồi bỏ ngay; gió bên nước có thể tắt nó trước khi người sau tới.

## SQ-BM-02 · Đèn cho người lạc / ACTIVE

`DLG_SQ_BM_02_CLUE` · `NPC_FISHER_01`

Ông chỉ khoảng tối giữa hai cọc, nơi ánh từ kho không tới được.

Đứng từ phía người đang trở về mà xem. Đèn sáng mặt bến chưa chắc soi được lối lên. Nếu thấy mưa hắt vào bấc, khép lại phần chắn trước.

## SQ-BM-02 · Đèn cho người lạc / READY_TO_TURN_IN

`DLG_SQ_BM_02_TURN_IN` · `NPC_FISHER_01`

Ba đốm sáng nối được từ đầm tới kho. Ngư phủ đứng xa hiên, đưa tay làm dấu cho một chiếc đò thử tìm lối.

Người ta nhìn thấy rồi. Để phần dầu còn lại ở đây, tôi thay ca giữ đèn.

Ông không gọi người ngoài đầm phải lên tiếng giữa mưa nữa.

## SQ-BM-03 · Mầm lau lạ / AVAILABLE

`DLG_SQ_BM_03_OFFER` · `NPC_FISHER_01`

Ngư phủ giữ một mầm lau trong chén có nắp; ánh mỏng từ thân hắt lên mặt nước chứ không soi sáng cả bàn.

Dược sư nhờ bốn mầm như thế, phải còn chân rễ. Tôi hái đứt một cái rồi, ngâm lại không chịu đứng. Bạn mang tới giúp, hỏi hộ xem người qua đầm có dùng được không.

## SQ-BM-03 · Mầm lau lạ / ACTIVE

`DLG_SQ_BM_03_CLUE` · `NPC_FISHER_01`

Ông đưa cả mầm đã héo để đối.

Đừng chỉ tìm chỗ xanh sáng. Xem mô tả lá và gốc nữa, ban ngày ánh ấy khó nhận. Cây vừa bị rễ quấn thì chừa ra, không cần giẫm sâu để hái cho đủ.

## SQ-BM-03 · Mầm lau lạ / READY_TO_TURN_IN

`DLG_SQ_BM_03_TURN_IN` · `NPC_FISHER_01`

Bốn mầm được giao để dược sư kiểm. Ngư phủ xếp lại chén của mầm đã héo, không trộn nó vào số mới.

Cái này là tôi làm hỏng. Cứ giữ để họ biết khác nhau ở đâu.

Ông xin nhận phần hướng dẫn ngâm cây trước khi mang chén trở lại bờ.

## SQ-BM-04 · Dấu chân thứ sáu / AVAILABLE

`DLG_SQ_BM_04_OFFER` · `NPC_FISHER_01`

Ngư phủ chống đầu cán lên bốn vệt giày còn thấy được, giữ người đi qua tránh giẫm.

Tôi đếm thừa một hướng chân khi thu đồ. Theo bốn dấu còn rõ, xem túi mắc ở đâu. Nếu trong ấy có thư thì giữ nguyên. Người mất túi có thể nhận bằng thứ khác, không cần mở hết chuyện của họ cho cả bến biết.

## SQ-BM-04 · Dấu chân thứ sáu / ACTIVE

`DLG_SQ_BM_04_CLUE` · `NPC_FISHER_01`

Ông đặt một mảnh ván chắn chỗ dấu cuối bị nước liếm tới.

Một dấu quay về không nhất thiết là thêm một người. Xem mũi giày, độ lún và thứ kéo sau gót. Ta đang tìm đồ, chưa phải bắt ai thú nhận đã đi đâu.

## SQ-BM-04 · Dấu chân thứ sáu / READY_TO_TURN_IN

`DLG_SQ_BM_04_TURN_IN` · `NPC_FISHER_01`

Chiếc túi về nguyên. Ngư phủ lật mặt khóa và đường vá cho người chờ nhận đối, để phong thư nằm kín dưới lớp vải.

Đúng túi thì họ nhận được. Số hướng chân tôi đếm lại vẫn có chỗ chưa chắc.

Ông xóa một nét trong bản phác, không thêm một người mất tích để làm phép đếm của mình vừa.

## SQ-BM-05 · Bữa cơm sau mưa / AVAILABLE

`DLG_SQ_BM_05_OFFER` · `NPC_FISHER_01`

Ngư phủ nhấc nồi khỏi chỗ mưa hắt, nhìn phần gạo đã nở mà bếp chưa đủ đồ ăn.

Ba cá, hai rau là đủ cho bữa này. Đưa tới bếp nhé, đừng đợi nước yên hẳn mới gọi người lên ăn. Mấy người vừa thoát đầm vẫn còn ngồi ngoài hiên vì tưởng trong kho không có chỗ.

## SQ-BM-05 · Bữa cơm sau mưa / ACTIVE

`DLG_SQ_BM_05_CLUE` · `NPC_FISHER_01`

Ông đặt thêm hai chiếc bát, không xếp cả chồng lên lối đi.

Rau dập thì báo bếp lựa lại. Người vừa bị lạnh ăn chậm, đừng múc hết ngay rồi giục họ. Tôi đi gọi người ngoài hiên.

## SQ-BM-05 · Bữa cơm sau mưa / READY_TO_TURN_IN

`DLG_SQ_BM_05_TURN_IN` · `NPC_FISHER_01`

Cá và rau được nhận ở bếp. Ngư phủ nhường chỗ sát nồi cho người tay còn run, tự ngồi gần cửa.

Ai muốn học cách nấu thì đứng bên này, đừng chen chỗ người đang ăn.

Một chiếc bát sứ đã được lấy khỏi rơm gói, đặt lên bàn còn dấu nước mưa.

## SQ-TL-01 · Bảng tin trống / AVAILABLE

`DLG_SQ_TL_01_OFFER` · `NPC_GUARD_CAPTAIN`

Đội trưởng Thanh Lạc giữ tấm bảng khỏi đập vào tường, xếp lại những tờ nhờ việc đã rơi.

Ba yêu cầu của dân vẫn chưa có người nhận. Tôi không cho bóc chúng vì bảng trông xấu. Đọc kỹ người nhờ ở đâu rồi tới hỏi lại; có việc ghi từ hôm qua, hôm nay có thể cần làm cách khác.

## SQ-TL-01 · Bảng tin trống / ACTIVE

`DLG_SQ_TL_01_CLUE` · `NPC_GUARD_CAPTAIN`

Ông lật mặt sau một tờ có dòng sửa bằng nét nhỏ hơn.

Nhận xong nhớ hỏi ai sẽ xác nhận. Đừng chỉ quay về bảo tôi đã đi qua ba nhà. Người chờ sửa việc mới biết nó có dùng được chưa.

## SQ-TL-01 · Bảng tin trống / READY_TO_TURN_IN

`DLG_SQ_TL_01_TURN_IN` · `NPC_GUARD_CAPTAIN`

Ba yêu cầu được đối lại với người nhờ. Đội trưởng treo tờ đã xong sang bên, chừa cả phần người dân sửa lời nhờ.

Bảng bây giờ vẫn có giấy. Thế mới biết người ta tới đây sẽ được nghe.

Ông đóng lại chiếc móc lỏng trước khi rời tường.

## SQ-TL-02 · Năm lá cờ / AVAILABLE

`DLG_SQ_TL_02_OFFER` · `NPC_GUARD_CAPTAIN`

Đội trưởng chặn một cán cờ đang nghiêng ra đường xe.

Năm cột quanh quảng trường cần sửa. Đừng kéo cho năm lá chỉ cùng một hướng; sửa chân cột và dây giữ trước. Người bán phía dưới cần biết nó sẽ không rơi lên mái quầy.

## SQ-TL-02 · Năm lá cờ / ACTIVE

`DLG_SQ_TL_02_CLUE` · `NPC_GUARD_CAPTAIN`

Ông đứng ở chỗ dân thường đi qua để nhìn lên.

Chắc ở trên chưa đủ, dây chùng xuống cũng có thể quệt người. Thử lại từ dưới đường, đợi người qua hết rồi hãy kéo.

## SQ-TL-02 · Năm lá cờ / READY_TO_TURN_IN

`DLG_SQ_TL_02_TURN_IN` · `NPC_GUARD_CAPTAIN`

Năm cột đã chắc, lá cờ vẫn nghiêng khác nhau giữa cùng luồng gió. Đội trưởng kiểm lối xe trước khi thôi giữ rào.

Chuyện gió để người biết mạch xem. Chân cột thì ta vừa sửa được.

Người bán bỏ chiếc chậu từng hứng nước dưới cột, mở lại tấm bạt quầy.

## SQ-TL-03 · Món đồ thất lạc / AVAILABLE

`DLG_SQ_TL_03_OFFER` · `NPC_GUARD_CAPTAIN`

Đội trưởng nhận một hình vẽ chiếc nhẫn, xoay đúng chiều để người mất chỉ chỗ sứt.

Ba gian hàng họ đã ghé. Hỏi chủ trước khi lục dưới quầy. Nhẫn ấy không quý hơn mọi thứ ở đây, nhưng người mất cần nó để về nói đã tìm lại được.

## SQ-TL-03 · Món đồ thất lạc / ACTIVE

`DLG_SQ_TL_03_CLUE` · `NPC_GUARD_CAPTAIN`

Ông giữ hình vẽ ở mặt trống của sổ, không vẽ thêm theo trí mình.

Nếu ai tìm thấy một chiếc khác, cứ đối vết sứt trước. Đừng để người ta phải mang cả đời tư ra kể chỉ để chứng minh một món là của mình.

## SQ-TL-03 · Món đồ thất lạc / READY_TO_TURN_IN

`DLG_SQ_TL_03_TURN_IN` · `NPC_GUARD_CAPTAIN`

Vết sứt khớp. Đội trưởng chờ người mất tự nhận nhẫn, ghi nơi tìm thấy để trả lời chủ quầy đã cho tìm.

Ta sẽ tới cảm ơn họ. Không cần treo tên người mất lên bảng.

Người ấy cất nhẫn rồi quay lại giúp dựng gian hàng đã bị xê dịch lúc tìm.

## SQ-TL-04 · Người mới nhập môn / AVAILABLE

`DLG_SQ_TL_04_OFFER` · `NPC_GUARD_CAPTAIN`

Đội trưởng đưa ba người tập về phần sân trống, tháo mũ giáp đặt ngoài vạch.

Ba lượt đấu tập, không gây thương tích thật. Tôi muốn người mới biết cách dừng khi đối phương đã mất chỗ đứng. Nếu ai xin nghỉ, lùi lại; đây không phải lối để chứng minh họ có chịu đau được không.

## SQ-TL-04 · Người mới nhập môn / ACTIVE

`DLG_SQ_TL_04_CLUE` · `NPC_GUARD_CAPTAIN`

Ông nhặt vũ khí tập rơi, trả bằng phía cán.

Hỏi người tập cùng đã sẵn sàng rồi mới vào lượt nữa. Chưa ai nhìn trộm bảng thắng đâu; họ đang nhìn xem ngươi có nghe được lời dừng không.

## SQ-TL-04 · Người mới nhập môn / READY_TO_TURN_IN

`DLG_SQ_TL_04_TURN_IN` · `NPC_GUARD_CAPTAIN`

Ba lượt kết thúc. Đội trưởng để những người tập đổi vai nhận xét, đứng ngoài nghe cả phần họ không đồng ý với ông.

Được, lượt ấy ta đã ra hiệu chậm. Ta sửa.

Một người mới ở lại nhặt dụng cụ, hỏi khi nào sân mở lần nữa.

## SQ-TL-05 · Sổ kho Sầm Quỹ / AVAILABLE

`DLG_SQ_TL_05_OFFER` · `NPC_GUARD_CAPTAIN`

Đội trưởng giữ cửa kho để xe ra, nhận bản kê Sầm gửi mà không mang cả kiện xuống đường.

Bốn kiện cần đối. Có một hóa đơn chưa khớp, nhưng ta chưa biết số sai ở lúc cân hay lúc chép. Xem dấu từng kiện, hỏi người nhận trước khi ghi ai đã lấy thiếu.

## SQ-TL-05 · Sổ kho Sầm Quỹ / ACTIVE

`DLG_SQ_TL_05_CLUE` · `NPC_GUARD_CAPTAIN`

Ông đặt phần giấy đã sửa cạnh bản đầu, không úp xuống.

Mang cả dòng sửa về. Một phép cộng sai và một chuyến hàng mất là hai việc khác nhau. Ta không muốn dùng chuyện này để bắt người mở những kiện không nằm trong bản kê.

## SQ-TL-05 · Sổ kho Sầm Quỹ / READY_TO_TURN_IN

`DLG_SQ_TL_05_TURN_IN` · `NPC_GUARD_CAPTAIN`

Bốn kiện đối được với một dòng hóa đơn sai. Đội trưởng ghi kết quả kiểm, giữ bản sai cùng bản sửa cho Sầm nhận lại.

Ai làm tiếp phải thấy vì sao con số đổi. Ta không xé tờ trước cho cuốn sổ trông sạch.

Xe được ra khỏi cửa, người nhận cầm phần xác nhận riêng của mình.

## SQ-LT-01 · Thuốc cho tiều phu / AVAILABLE

`DLG_SQ_LT_01_OFFER` · `NPC_FOREMAN_MOC`

Quản đốc Mộc gỡ vỏ bám trên tay áo người thợ, tránh đúng chỗ da đang sưng.

Dược sư cần năm phần dược thảo ở bìa rừng. Người này cứ bảo còn cầm rìu được. Ta giữ rìu ở đây; ngươi mang thuốc về trước khi anh ấy tìm được cái khác.

## SQ-LT-01 · Thuốc cho tiều phu / ACTIVE

`DLG_SQ_LT_01_CLUE` · `NPC_FOREMAN_MOC`

Ông đưa bản mô tả lá có răng nhỏ ở mép, không chỉ một vệt màu.

Hái ở bìa thôi. Dùng đúng mô tả, đừng thử thứ lạ lên vết thương để xem có dịu không. Ta đã hứa để người thợ nghỉ hết lượt này.

## SQ-LT-01 · Thuốc cho tiều phu / READY_TO_TURN_IN

`DLG_SQ_LT_01_TURN_IN` · `NPC_FOREMAN_MOC`

Dược thảo được nhận, người thợ chịu tháo hẳn găng. Quản đốc đặt cán rìu ở chỗ anh nhìn thấy nhưng không với tới.

Mai ta chia lại phần việc. Hôm nay anh không cần giữ cả đoạn rừng trên bàn tay ấy.

Bữa nghỉ có thêm người ngồi, không ai phải giả vờ chỉ đang chờ mài dụng cụ.

## SQ-LT-02 · Tổ chim rơi / AVAILABLE

`DLG_SQ_LT_02_OFFER` · `NPC_FOREMAN_MOC`

Quản đốc Mộc ngăn tay người đang định đốn cây non để lấy tổ.

Có ba chim con mắc rễ. Gỡ rễ quanh chúng, chừa thân cây lại. Nhìn cái tổ nghiêng thì dễ muốn hạ cả thứ đang đỡ nó, nhưng rễ còn bám ở dưới.

## SQ-LT-02 · Tổ chim rơi / ACTIVE

`DLG_SQ_LT_02_CLUE` · `NPC_FOREMAN_MOC`

Ông đặt chiếc giỏ lót lá ngoài đường thợ đi.

Mang từng con ra chỗ đỡ chắc rồi mới gỡ tiếp. Cây non không phải mục tiêu; đừng chém rộng chỉ để khỏi phải nhìn một sợi rễ nhỏ.

## SQ-LT-02 · Tổ chim rơi / READY_TO_TURN_IN

`DLG_SQ_LT_02_TURN_IN` · `NPC_FOREMAN_MOC`

Ba chim con có chỗ đỡ mới, cây non vẫn đứng ở cạnh tổ cũ. Quản đốc Mộc dịch đường kéo gỗ tránh khu ấy.

Chừa thêm một đoạn cho chim lớn tìm thấy.

Ông cắm dấu vòng ngoài bằng vật đang có, không đóng bảng tuyên bố đã cứu cả khu rừng.

## SQ-LT-03 · Nấm biết hát / AVAILABLE

`DLG_SQ_LT_03_OFFER` · `NPC_FOREMAN_MOC`

Quản đốc Mộc đặt bốn chén rỗng theo nhịp nghe được cạnh trạm chế thuốc.

Có nấm giữ tiếng ở các lối này. Tìm bốn phần đúng rồi đem về trạm. Nếu không nghe được thì xem vòng rung và bản mô tả; ta đã nhờ ghi cùng một nhịp lên đó.

## SQ-LT-03 · Nấm biết hát / ACTIVE

`DLG_SQ_LT_03_CLUE` · `NPC_FOREMAN_MOC`

Ông gõ lại một lần trên cán rìu rồi ngừng để người chơi tự đối.

Không cần nhanh hơn bản nhịp. Thử sai thì nghe hoặc xem lại; đừng hái hết một cụm chỉ vì nó lớn tiếng hơn.

## SQ-LT-03 · Nấm biết hát / READY_TO_TURN_IN

`DLG_SQ_LT_03_TURN_IN` · `NPC_FOREMAN_MOC`

Bốn phần nấm được chế ở trạm. Quản đốc thử nhắc người đang làm không gõ thêm lên bàn, rồi tự nhận ra cán rìu mình vẫn đang gõ.

À, cả ta nữa.

Ông đặt cán xuống, để phần nhịp trong nấm được nghe rõ trước khi người chế khép nắp.

## SQ-LT-04 · Người nhớ nhầm / AVAILABLE

`DLG_SQ_LT_04_OFFER` · `NPC_FOREMAN_MOC`

Quản đốc Mộc đưa ba mảnh ký ức người thợ vừa kể, để riêng câu anh không chắc.

Anh ấy nhớ đã qua cầu nhưng lại chỉ đường chưa từng tới. Ghép ba mảnh rồi hỏi lại, đừng ép anh nhận một bản kể cho chúng ta dễ tìm đường. Ta còn nhớ đường mình dẫn hôm ấy cũng có chỗ sai.

## SQ-LT-04 · Người nhớ nhầm / ACTIVE

`DLG_SQ_LT_04_CLUE` · `NPC_FOREMAN_MOC`

Ông thử gọi người thợ kể từ vật đầu tiên còn nhớ, bỏ câu hỏi về thời gian sang sau.

Mùi gỗ, mặt nước hay tiếng rìu cũng được. Cứ để chỗ chưa nhớ trống. Anh ấy không nợ chúng ta một câu chuyện liền mạch ngay bây giờ.

## SQ-LT-04 · Người nhớ nhầm / READY_TO_TURN_IN

`DLG_SQ_LT_04_TURN_IN` · `NPC_FOREMAN_MOC`

Ba mảnh ghép được một quãng đường, còn đoạn qua cầu vẫn chưa rõ. Quản đốc ghi bằng hai nét khác nhau: điều đã đối và điều người thợ đang nhớ.

Hôm khác hỏi tiếp nếu anh ấy muốn.

Người thợ cầm bản sao của mình, không phải xin quản đốc kể lại hộ điều vừa nói.

## SQ-LT-05 · Cầu dây mục / AVAILABLE

`DLG_SQ_LT_05_OFFER` · `NPC_FOREMAN_MOC`

Quản đốc Mộc giữ đầu dây cầu đã xơ, không cho đoàn thử bước thêm.

Bốn đoạn phải thay. Sửa xong rồi ta dẫn người qua, từng tốp đủ chỗ đứng. Đừng lấy việc một người nhẹ đã qua được làm phép thử cho cả xe dụng cụ.

## SQ-LT-05 · Cầu dây mục / ACTIVE

`DLG_SQ_LT_05_CLUE` · `NPC_FOREMAN_MOC`

Ông nhìn những nút mới từ phía dưới mép ván, tìm chỗ dây chạm cạnh đá.

Căng chưa đủ, còn phải đừng cọ vào chỗ ấy. Gọi ta trước khi cho đoàn đi. Người cuối sẽ chịu phần cầu võng mà người đầu chưa cảm thấy.

## SQ-LT-05 · Cầu dây mục / READY_TO_TURN_IN

`DLG_SQ_LT_05_TURN_IN` · `NPC_FOREMAN_MOC`

Bốn dây thay xong, đoàn qua đủ người. Quản đốc về sau cùng, nhấc chiếc giỏ từng chắn lối cầu.

Giữ bản ghi chỗ cọ đá ở đầu bên kia nữa. Lần sau họ sửa từ phía ấy.

Dòng người không còn phải chờ một tiếng hô từ riêng bờ này.

## SQ-SH-01 · Bản đồ nước / AVAILABLE

`DLG_SQ_SH_01_OFFER` · `NPC_MEDIC_SA_HOA`

Dược sư Sa Hỏa vẽ lại đường giếng trên mặt sau một giấy gói thuốc, để người mới tới không phải trả tiền hỏi đường.

Đặt bốn cọc ở những ngã dễ nhầm. Người khát nhìn thấy mái nhà tưởng đã tới, rẽ vào thì phải quay cả quãng. Tôi cần dấu có cả hình giếng, không chỉ một màu vải.

## SQ-SH-01 · Bản đồ nước / ACTIVE

`DLG_SQ_SH_01_CLUE` · `NPC_MEDIC_SA_HOA`

Dược sư đối tờ vẽ từ phía người đang rời đường lớn.

Đừng để cọc chỉ đúng khi nhìn từ chỗ mình vừa đứng. Đi ngược lại thử một đoạn. Người tới giếng hiếm khi còn sức chạy vòng để hiểu một mũi tên.

## SQ-SH-01 · Bản đồ nước / READY_TO_TURN_IN

`DLG_SQ_SH_01_TURN_IN` · `NPC_MEDIC_SA_HOA`

Bốn cọc được đặt và đối đường. Dược sư giao tờ vẽ cho người chở nước giữ một bản, không cất hết vào hòm thuốc.

Hôm nay đường này đi được. Đổi lối thì sửa dấu trước.

Một người dừng hỏi đường nhận được câu trả lời ngay ở ngã rẽ, chưa phải tới trạm mới biết.

## SQ-SH-02 · Lưỡi búa nguội / AVAILABLE

`DLG_SQ_SH_02_OFFER` · `NPC_MEDIC_SA_HOA`

Dược sư nghe người thợ kể về chiếc búa lạc lâu hơn về vết phỏng.

Tôi đã rửa tay cho anh ấy, nhưng anh cứ định quay vào cát tìm búa. Mang nó về giúp, đẩy lui năm bọ cát ở đường ấy. Đừng thử cầm đầu búa trần để xem còn nóng không.

## SQ-SH-02 · Lưỡi búa nguội / ACTIVE

`DLG_SQ_SH_02_CLUE` · `NPC_MEDIC_SA_HOA`

Dược sư chuẩn bị một miếng vải khô thay cho lời dặn giữ tay sạch lần nữa.

Dấu trên cán giúp nhận đúng dụng cụ. Nếu cán nứt thì mang nguyên về, đừng đưa một chiếc có thể gãy giữa lượt rồi bảo đã tìm lại được.

## SQ-SH-02 · Lưỡi búa nguội / READY_TO_TURN_IN

`DLG_SQ_SH_02_TURN_IN` · `NPC_MEDIC_SA_HOA`

Chiếc búa về, vết nứt trên cán được chỉ rõ. Người thợ nhìn tay đang băng rồi để nó trên bàn, chịu nhờ người khác thay cán.

Dược sư: Giờ anh ngồi yên cho tôi làm nốt.

Đồ nghề ở trong tầm nhìn khiến lời đề nghị nghỉ cuối cùng có chỗ để đặt xuống.

## SQ-SH-03 · Gió mang tro / AVAILABLE

`DLG_SQ_SH_03_OFFER` · `NPC_MEDIC_SA_HOA`

Dược sư kéo miếng vải lọc khỏi cửa trạm, lớp tro mới dày lên ngay nơi vừa giũ.

Ba quạt trong hầm cần bật lại. Tôi có thể thay vải, không thay được khí cho cả đường. Tới từng chỗ xem cánh có quay và luồng có thoát, đừng chỉ nhìn tay gạt đã hạ.

## SQ-SH-03 · Gió mang tro / ACTIVE

`DLG_SQ_SH_03_CLUE` · `NPC_MEDIC_SA_HOA`

Dược sư thử mở cửa một khe để đối chiều gió, rồi đóng ngay khi tro cuộn vào.

Cánh quay ngược cũng có tiếng. Xem ký hiệu luồng và bản mô tả. Bật sai thì chỉnh lại, đừng đứng thử hít để chứng minh chỗ ấy đã sạch.

## SQ-SH-03 · Gió mang tro / READY_TO_TURN_IN

`DLG_SQ_SH_03_TURN_IN` · `NPC_MEDIC_SA_HOA`

Ba quạt hoạt động. Dược sư giũ lần nữa, lần này mặt vải giữ được màu sáng lâu hơn.

Tôi ghi giờ kiểm ở cửa hầm. Ca sau phải xem lại, không lấy hôm nay làm lời bảo đảm mãi.

Cửa trạm mở thêm một khoảng đủ cho người chờ ngồi tránh nhau.

## SQ-SH-04 · Đoàn xe lạc / AVAILABLE

`DLG_SQ_SH_04_OFFER` · `NPC_MEDIC_SA_HOA`

Dược sư giữ hai phần thuốc chưa giao vì xe phụ không tới.

Có hai ngã họ có thể rẽ nhầm. Tìm xe rồi dẫn về đường chính; người trên ấy có thể đã chia nước để ở lại với hàng. Báo họ có chỗ nhận, không cần cố chở đủ rồi mới được quay về.

## SQ-SH-04 · Đoàn xe lạc / ACTIVE

`DLG_SQ_SH_04_CLUE` · `NPC_MEDIC_SA_HOA`

Dược sư đặt phần thuốc gần cửa hơn để người đưa tin không phải vào sâu.

Gặp xe thì hỏi ai đi bộ tìm đường trước. Dẫn xe về mà để người đó tiếp tục tìm một đoàn đã rời chỗ cũng chưa xong việc.

## SQ-SH-04 · Đoàn xe lạc / READY_TO_TURN_IN

`DLG_SQ_SH_04_TURN_IN` · `NPC_MEDIC_SA_HOA`

Xe phụ trở lại đường chính. Dược sư đối cả người từng rời xe, để hai phần thuốc đúng chỗ có người nhận.

Tôi sẽ sửa giờ hẹn trên giấy. Chỗ này giao muộn vì lạc đường, không phải họ bỏ chuyến.

Người đánh xe nhận thêm bản chỉ hai ngã đã nhầm trước khi đi tiếp.

## SQ-SH-05 · Bản nhạc lò rèn / AVAILABLE

`DLG_SQ_SH_05_OFFER` · `NPC_MEDIC_SA_HOA`

Dược sư để bốn dụng cụ gõ lên tấm đệm, tránh tiếng vang làm người đang nghỉ giật mình.

Lò chủ dùng nhịp này để truyền cách làm. Thử bốn dụng cụ theo bản hình và âm, công thức ở trạm sẽ mở khi đối đúng. Không cần gõ to; người trong lò phải nghe được tín hiệu giữa những tiếng khác.

## SQ-SH-05 · Bản nhạc lò rèn / ACTIVE

`DLG_SQ_SH_05_CLUE` · `NPC_MEDIC_SA_HOA`

Dược sư chỉ phần ngắt giữa hai nhịp, lâu hơn một khoảng người mới thường chờ.

Để yên cũng là một phần của nhịp. Nghe không rõ thì theo dấu sáng và mô tả; đừng bắt người không nghe được đứng ngoài việc học.

## SQ-SH-05 · Bản nhạc lò rèn / READY_TO_TURN_IN

`DLG_SQ_SH_05_TURN_IN` · `NPC_MEDIC_SA_HOA`

Nhịp được đối, công thức có thể xem lại ở trạm. Dược sư cất riêng tấm mô tả, giữ cạnh dụng cụ thay vì giấu trong sổ.

Lần sau người tới muộn vẫn học được.

Trước khi gõ lại cho người mới, dược sư liếc sang giường nghỉ và hạ lực bàn tay.

## SQ-TS-01 · Tên trên bia / AVAILABLE

`DLG_SQ_TS_01_OFFER` · `NPC_CAPTAIN_TRAN_SON`

Đội trưởng Trấn Sơn phủi bụi bia, dừng trước một tên chỉ còn nửa nét.

Năm tên cần khắc lại. Đối bản còn giữ và hỏi người biết họ trước. Đừng điền theo tên nghe quen hơn; người mất không còn tới đây sửa cho ta.

## SQ-TS-01 · Tên trên bia / ACTIVE

`DLG_SQ_TS_01_CLUE` · `NPC_CAPTAIN_TRAN_SON`

Ông để một dòng trống cạnh tên chưa đối chắc, không chèn cái tên thứ sáu vào cho kín mặt đá.

Nếu có hai cách đọc, giữ cả hai trong bản hỏi. Bia chờ được thêm một hôm. Khắc sai rồi bảo gần giống thì người sống vẫn phải mang phần sai ấy về.

## SQ-TS-01 · Tên trên bia / READY_TO_TURN_IN

`DLG_SQ_TS_01_TURN_IN` · `NPC_CAPTAIN_TRAN_SON`

Năm tên được đối và khắc lại. Đội trưởng mời người đã xác nhận xem từng nét trước khi phủi lớp bụi cuối.

Còn tên chưa biết, tôi để chỗ.

Ông đổi vị trí tấm che để người đứng thấp cũng đọc được hàng cuối, không chỉ người tới nghi lễ.

## SQ-TS-02 · Thùng tiếp tế / AVAILABLE

`DLG_SQ_TS_02_OFFER` · `NPC_CAPTAIN_TRAN_SON`

Đội trưởng kê bốn thùng tiếp tế ngoài đường cáng, kiểm bản chia ở ba cổng.

Mang đúng nơi nhận và ghi ai đã cầm. Người ở cổng xa hay nhường phần mình vì không muốn phiền đoàn xe. Đừng coi im lặng là đủ đồ.

## SQ-TS-02 · Thùng tiếp tế / ACTIVE

`DLG_SQ_TS_02_CLUE` · `NPC_CAPTAIN_TRAN_SON`

Ông mở thùng mẫu cho người chuyển nhìn những phần cần giữ khô.

Tới nơi thì hỏi cả thứ không có trong bản chia. Tôi chưa hứa cấp được ngay, nhưng phải biết đang thiếu trước khi ký rằng cổng đã được tiếp tế.

## SQ-TS-02 · Thùng tiếp tế / READY_TO_TURN_IN

`DLG_SQ_TS_02_TURN_IN` · `NPC_CAPTAIN_TRAN_SON`

Bốn thùng có người nhận tại ba cổng. Đội trưởng giữ phần ghi thiếu tách khỏi giấy đã giao, không để chữ đủ che lên nó.

Chuyến sau bắt đầu từ đây.

Ông đưa bản sao cho người trực ở cổng xa, để họ không phải đợi chính ông trở lại mới hỏi được.

## SQ-TS-03 · Mũi tên mắc tường / AVAILABLE

`DLG_SQ_TS_03_OFFER` · `NPC_CAPTAIN_TRAN_SON`

Đội trưởng giữ một mũi tên bằng kẹp, để đầu cong hướng khỏi người đứng cạnh.

Thu sáu mũi mắc tường, rồi sửa ụ nỏ. Dân đang đi dưới đó; đừng giật cho gạch rơi cùng tên. Cái còn thẳng để riêng, cái hỏng cũng phải mang về kiểm.

## SQ-TS-03 · Mũi tên mắc tường / ACTIVE

`DLG_SQ_TS_03_CLUE` · `NPC_CAPTAIN_TRAN_SON`

Ông thử độ chắc bệ trước khi nhìn dây nỏ.

Đừng chỉ làm nó bắn được một lần. Người lên thay có biết chỗ nào đang chèn tạm không? Ghi ra cho họ thấy, đừng giữ mẹo sửa trong đầu một người.

## SQ-TS-03 · Mũi tên mắc tường / READY_TO_TURN_IN

`DLG_SQ_TS_03_TURN_IN` · `NPC_CAPTAIN_TRAN_SON`

Sáu mũi tên được lấy khỏi tường, ụ nỏ sửa xong có bản ghi phần đã thay. Đội trưởng thử bệ rồi nhường cho người trực lượt sau kiểm lại.

Chưa ổn thì nói ngay. Họ sống với cái ụ này lâu hơn lúc ta đứng nghiệm.

Đường dưới tường được dọn mở trước khi ông cho mang dụng cụ đi.

## SQ-TS-04 · Lời xin lỗi của người lính / AVAILABLE

`DLG_SQ_TS_04_OFFER` · `NPC_CAPTAIN_TRAN_SON`

Đội trưởng nhận phong thư của người lính, chờ anh viết xong tên người cần gặp mới gấp lại.

Tìm đồng đội anh ấy, đưa tận tay nếu người nhận muốn nhận. Đây là lời xin lỗi, không phải giấy lệnh. Đừng gọi người ta ra giữa đám đông để người gửi được thấy mình đã làm xong.

## SQ-TS-04 · Lời xin lỗi của người lính / ACTIVE

`DLG_SQ_TS_04_CLUE` · `NPC_CAPTAIN_TRAN_SON`

Ông giữ thư trong bọc khô, không hỏi người chuyển kể lại nội dung.

Người nhận có thể chưa trả lời. Báo rõ đã trao hay còn giữ, thế là đủ. Ta không viết một câu tha thứ thay họ để người bên này dễ ngủ.

## SQ-TS-04 · Lời xin lỗi của người lính / READY_TO_TURN_IN

`DLG_SQ_TS_04_TURN_IN` · `NPC_CAPTAIN_TRAN_SON`

Việc chuyển thư được xác nhận. Đội trưởng báo lại đúng phần người nhận cho phép nói, để khoảng còn lại nguyên.

Anh ấy đã có lời của mình. Giờ chờ câu trả lời, nếu có.

Người lính không bị dẫn tới bắt tay trước hàng quân; anh trở lại phần việc vẫn phải làm ở cổng.

## SQ-TS-05 · Kèn báo động / AVAILABLE

`DLG_SQ_TS_05_OFFER` · `NPC_CAPTAIN_TRAN_SON`

Đội trưởng đặt ba tín hiệu cạnh lối lên kèn, gạch nét cũ đã gây nhầm hôm trước.

Khi tập kích tới, kích ba kèn đúng thứ tự. Bản hình đi cùng âm; người ở cổng không nghe rõ vẫn phải biết hướng gọi. Ta không muốn một tiếng báo động khiến cả ba cổng cùng bỏ vị trí.

## SQ-TS-05 · Kèn báo động / ACTIVE

`DLG_SQ_TS_05_CLUE` · `NPC_CAPTAIN_TRAN_SON`

Ông chỉ phần xác nhận sau mỗi tín hiệu.

Thấy người bên kia đã nhận rồi mới sang kèn tiếp. Nếu phải lặp, lặp đúng tín hiệu, đừng kéo dài cho lớn hơn rồi hy vọng ai cũng hiểu.

## SQ-TS-05 · Kèn báo động / READY_TO_TURN_IN

`DLG_SQ_TS_05_TURN_IN` · `NPC_CAPTAIN_TRAN_SON`

Ba kèn được nhận đúng thứ tự trong đợt tập kích. Đội trưởng kiểm bản hình ở cổng xa nhất trước khi cho dừng báo.

Bên ấy nhận đủ. Ta sửa được phần đã làm họ chậm hôm qua.

Người trực mới được đối bản tín hiệu ngay tại chỗ, không chỉ nghe truyền miệng qua một lượt gác.

## SQ-BU-01 · Đèn đáy biển / AVAILABLE

`DLG_SQ_BU_01_OFFER` · `NPC_DIVER_LEAD`

Đội trưởng thợ lặn đặt bốn lõi đèn trong khay có vạch giữ, thử khóa khay trước khi đưa xuống.

Thay ở bốn đèn đường. Giữ sáng lối về, không chỉ chỗ có nhà dễ nhìn. Dưới nước, ai đi sau cũng cần nhận được chặng người trước vừa qua.

## SQ-BU-01 · Đèn đáy biển / ACTIVE

`DLG_SQ_BU_01_CLUE` · `NPC_DIVER_LEAD`

Ông xoay sơ đồ theo hướng người lặn trở lên.

Kiểm đèn từ phía ấy nữa. Lõi sáng mà bị rong che cửa thì người đang hết khí vẫn có thể bỏ lỡ. Dùng mô tả ký hiệu nếu màu bị nước làm lệch.

## SQ-BU-01 · Đèn đáy biển / READY_TO_TURN_IN

`DLG_SQ_BU_01_TURN_IN` · `NPC_DIVER_LEAD`

Bốn đèn hoạt động, đường trở lại hiện thành những chặng rõ. Đội trưởng ghi cả đèn cần kiểm rong thường hơn.

Ai từng sống ở phố này sẽ nhận ra lối. Chúng ta không cần đổi hết tên ngõ theo đoàn vừa tới.

Bản sơ đồ được để ở cả đầu lên và đầu xuống.

## SQ-BU-02 · Bản đồ rong / AVAILABLE

`DLG_SQ_BU_02_OFFER` · `NPC_DIVER_LEAD`

Đội trưởng thợ lặn giữ bản đồ rong dưới tấm lưới mỏng để nó khỏi cuộn.

Năm mảnh còn lại ở đường cá hiếm qua. Lấy bản đồ, không săn cá để đường trống. Chúng có thể tới gần vì chính rong đang giữ mảnh; chờ một quãng rồi mới nhấc.

## SQ-BU-02 · Bản đồ rong / ACTIVE

`DLG_SQ_BU_02_CLUE` · `NPC_DIVER_LEAD`

Ông chỉ lối đi vòng đã được ghi thay cho một mũi tên thẳng qua vùng cá tụ.

Bản đồ cần đường người khác cũng dùng lại được. Đi vòng mà giữ được chỗ ấy thì ghi vòng, đừng sửa trên giấy cho nó trông ngắn hơn việc vừa làm.

## SQ-BU-02 · Bản đồ rong / READY_TO_TURN_IN

`DLG_SQ_BU_02_TURN_IN` · `NPC_DIVER_LEAD`

Năm mảnh ghép được tuyến dưới nước, đàn cá vẫn còn qua vùng rong. Đội trưởng thêm dấu chờ ở chặng phải nhường đường.

Ta phát bản này cùng lời dặn. Người tới sau không cần bắt đầu bằng việc dọn sạch mọi thứ đang sống.

## SQ-BU-03 · Khoang kín / AVAILABLE

`DLG_SQ_BU_03_OFFER` · `NPC_DIVER_LEAD`

Đội trưởng thợ lặn thử tiếng ở vách hai khoang kín, chờ nó trả lại mới chỉ chỗ xả.

Xả nước hai khoang trước khi mở rương cứu hộ. Có thứ được giữ kín để còn dùng được; đừng bẩy nắp vì nhìn thấy đồ bên trong. Ta muốn rương mở xong vẫn còn là đồ cứu người.

## SQ-BU-03 · Khoang kín / ACTIVE

`DLG_SQ_BU_03_CLUE` · `NPC_DIVER_LEAD`

Ông đặt bản áp suất cạnh ký hiệu rương, tách hai việc bằng một đường rõ.

Khoang nào chưa ổn thì chờ ở chỗ trú. Mở được một cửa không phải tín hiệu mở mọi thứ. Cứ kiểm lại đèn và mô tả, không cần thử bằng hơi thở của mình.

## SQ-BU-03 · Khoang kín / READY_TO_TURN_IN

`DLG_SQ_BU_03_TURN_IN` · `NPC_DIVER_LEAD`

Hai khoang xả được nước, rương cứu hộ mở ở áp suất phù hợp. Đội trưởng kiểm vật còn dùng trước khi ghi phần tìm thấy.

Để một bộ ở trạm. Mang hết đi thì người xuống sau lại phải quay lên xin thứ vừa có ở đây.

Phần chia được ghi trong bản nhận, không để đồ biến mất giữa một dòng chiến lợi phẩm.

## SQ-BU-04 · Tiếng hát trong vỏ ốc / AVAILABLE

`DLG_SQ_BU_04_OFFER` · `NPC_DIVER_LEAD`

Đội trưởng thợ lặn giữ ba chỗ trống trong khay vỏ ốc, lót vải để chúng không chạm nhau.

Tìm ba vỏ giữ tiếng và phát lại ở chỗ yên. Có đoạn nghe như hát, có đoạn chỉ là một hơi hụt. Xem cả bản mô tả; ta không muốn chỉ người nghe rõ mới được biết ký ức đang kể gì.

## SQ-BU-04 · Tiếng hát trong vỏ ốc / ACTIVE

`DLG_SQ_BU_04_CLUE` · `NPC_DIVER_LEAD`

Ông ngăn một vỏ vừa xoay miệng về phía người đang nghỉ.

Xin trước khi phát. Người ở đây có thể nhận ra tiếng ấy, hoặc không muốn nghe giữa ca lặn. Chúng ta còn cách đọc lại bằng chữ, không phải giữ họ đứng nghe cho hết.

## SQ-BU-04 · Tiếng hát trong vỏ ốc / READY_TO_TURN_IN

`DLG_SQ_BU_04_TURN_IN` · `NPC_DIVER_LEAD`

Ba ký ức được phát và đối mô tả. Đội trưởng ghi riêng phần người nghe nhận ra với phần họ chỉ đoán.

Không ai chịu nhận giọng cuối, cứ để nguyên.

Ông bọc vỏ ốc lại từng cái; căn phòng trở về tiếng nước và tiếng người đang chuẩn bị lượt lặn tiếp.

## SQ-BU-05 · Thợ lặn nghỉ hưu / AVAILABLE

`DLG_SQ_BU_05_OFFER` · `NPC_DIVER_LEAD`

Đội trưởng thợ lặn nhận danh sách dụng cụ của người đã nghỉ nghề, hỏi lại món có dấu sửa ở cán.

Thu đúng đồ rồi chế một bộ sửa. Người ấy bảo không xuống nữa nhưng vẫn giữ cách làm trong đầu. Tôi muốn xin lại cách dùng, không xin họ chứng minh còn lặn được.

## SQ-BU-05 · Thợ lặn nghỉ hưu / ACTIVE

`DLG_SQ_BU_05_CLUE` · `NPC_DIVER_LEAD`

Ông tách dụng cụ đã mòn khỏi chiếc thay mới, giữ cả hai trên bàn.

Món cũ cho biết chỗ nào dễ hỏng. Đừng đánh bóng xong mất hết vết dùng rồi hỏi người chủ tại sao không nhận ra. Ghi lời dặn cạnh đồ thay, để không phải chỉ mình họ biết.

## SQ-BU-05 · Thợ lặn nghỉ hưu / READY_TO_TURN_IN

`DLG_SQ_BU_05_TURN_IN` · `NPC_DIVER_LEAD`

Bộ sửa được chế, người nghỉ nghề kiểm từng mối trước khi gật. Đội trưởng đưa bản hướng dẫn cho người mới đọc lại bằng lời của họ.

Nếu nói chưa đúng thì sửa ở đây.

Người chủ cũ giữ chiếc cán có dấu tay quen, không bị mời nhận lại một ca lặn thay cho lời cảm ơn.

## SQ-VN-01 · Bóng đi trước / AVAILABLE

`DLG_SQ_VN_01_OFFER` · `NPC_LYAN`

Ly An nhìn bóng đi trước bàn chân mình một quãng, thử dừng ở mép đá. Bóng tiếp tục tới một mốc rồi mới đứng.

Theo năm mốc của nó, tránh vùng đang lặp. Nếu đường chỉ nhìn qua bóng quá khó, đọc mô tả vệt đá và hướng dịch. Tôi không muốn ai phải bước vào chỗ ấy để chứng minh mình đã thấy.

## SQ-VN-01 · Bóng đi trước / ACTIVE

`DLG_SQ_VN_01_CLUE` · `NPC_LYAN`

Cô giữ chân ở phần nền không đổi, nhìn hai lần cùng một vết sứt đi qua.

Đợi hết lượt lặp rồi đối mốc tiếp. Bóng tới trước không có nghĩa nó biết ta sẽ chọn đi đâu. Bạn vẫn có thể dừng hoặc quay lại đường chắc.

## SQ-VN-01 · Bóng đi trước / READY_TO_TURN_IN

`DLG_SQ_VN_01_TURN_IN` · `NPC_LYAN`

Qua năm mốc, bóng trở lại dưới chân khi rời vùng lệch. Ly An thử giơ tay, chờ hình theo đúng động tác mới cất bản ghi.

Tôi ghi chỗ lệch, không ghi rằng đã nhìn thấy tương lai.

Cô trở lại đếm giấy trong túi; lần này bóng bàn tay nằm đúng trên mặt vải.

## SQ-VN-02 · Ba chiếc đồng hồ / AVAILABLE

`DLG_SQ_VN_02_OFFER` · `NPC_LYAN`

Ly An đặt ba bản nhịp cạnh đồng hồ, nghe đủ một vòng mới chạm nút đầu tiên.

Chỉnh chúng về cùng nhịp. Tôi đã ghi cả phần nhìn để không cần nghe kim. Đừng lấy chiếc chạy lớn tiếng nhất làm chuẩn; xem nhịp mạch ở dấu chỉ trước.

## SQ-VN-02 · Ba chiếc đồng hồ / ACTIVE

`DLG_SQ_VN_02_CLUE` · `NPC_LYAN`

Cô đếm một khoảng trống giữa hai lần kim nhích, ngừng khi thấy mình đếm vội.

Tôi làm lại từ đầu. Bạn xem bản nhịp của mình, không cần theo nhịp tôi vừa đọc sai. Chỉnh nhầm thì trả về vị trí trước, chúng ta còn lượt để đối.

## SQ-VN-02 · Ba chiếc đồng hồ / READY_TO_TURN_IN

`DLG_SQ_VN_02_TURN_IN` · `NPC_LYAN`

Ba đồng hồ giữ cùng nhịp với dấu mạch. Ly An gạch phần mình đọc sai nhưng để nó còn thấy.

Người sau hỏi vì sao số đổi thì có thứ để chỉ.

Cô không đổi ngày trên giấy đã nhận; việc chỉnh nhịp ở đây không viết lại ngày người khác đã sống.

## SQ-VN-03 · Mảnh trời cũ / AVAILABLE

`DLG_SQ_VN_03_OFFER` · `NPC_LYAN`

Ly An giữ một tấm vải hứng mảnh phản chiếu trời, để nó không trượt qua mép bàn.

Cần bốn mảnh ở những chỗ đã đánh dấu. Có mảnh chỉ giữ màu trước cơn mưa, nhìn như không có gì. Đối bằng mép hình và mô tả nữa, đừng chờ chúng đều sáng lên.

## SQ-VN-03 · Mảnh trời cũ / ACTIVE

`DLG_SQ_VN_03_CLUE` · `NPC_LYAN`

Cô đưa tấm lót trống ra trước khi người chơi tới gần vệt sáng.

Đặt mặt giữ hình lên trên. Nếu các mảnh không ghép thành một bầu trời liền, cứ giữ vậy; tôi chưa biết chúng có nhìn cùng một ngày không.

## SQ-VN-03 · Mảnh trời cũ / READY_TO_TURN_IN

`DLG_SQ_VN_03_TURN_IN` · `NPC_LYAN`

Bốn mảnh có nơi sáng, nơi còn mây; ghép mép không làm thời điểm trong chúng trùng lại. Ly An để khoảng nối hở trên bản chép.

Tôi thích cái màu này, nhưng không vì thế mà chọn nó làm màu của cả ngày.

Cô gấp tấm lót từ phía trống, tránh đè nếp lên vùng hình còn giữ.

## SQ-VN-04 · Cửa không có bản lề / AVAILABLE

`DLG_SQ_VN_04_OFFER` · `NPC_LYAN`

Ly An thử tìm bản lề ở cửa rồi rút tay, đặt bản ba biểu tượng lên nền trước mặt.

Tôi cứ tìm cái để đẩy. Ở đây phải kích ba nút theo dấu. Có cả hình nổi, không cần phân biệt màu. Bạn xem phần hướng trước; tôi giữ đường sau khỏi bị người khác tưởng đã mở.

## SQ-VN-04 · Cửa không có bản lề / ACTIVE

`DLG_SQ_VN_04_CLUE` · `NPC_LYAN`

Cô đứng lùi khỏi cánh cửa khi một đường sáng đổi chỗ.

Đợi xác nhận nút này rồi sang nút kia. Sai thì đối lại bản dấu, đừng dùng lực thêm. Tôi đã đẩy thử đủ để biết việc ấy không giúp gì.

## SQ-VN-04 · Cửa không có bản lề / READY_TO_TURN_IN

`DLG_SQ_VN_04_TURN_IN` · `NPC_LYAN`

Ba nút được kích đúng, cửa mở mà không có cánh nào quay. Ly An nhìn chỗ mình từng tìm bản lề, rồi đánh dấu đường đã thông.

Tôi sẽ sửa chỉ dẫn. Không thể cứ bảo người sau tới đây sẽ tự biết.

Cô đứng ở bên kia gọi lại để đối lối qua theo cả hai chiều.

## SQ-VN-05 · Lời nhắn của Cơ / AVAILABLE

`DLG_SQ_VN_05_OFFER` · `NPC_LYAN`

Ly An xếp năm chỗ trên bàn theo ngày ghi, chưa theo câu nào nghe dễ tin nhất.

Tìm năm bản ghi của Cơ rồi xem theo thời gian. Có điều ông ấy muốn người tới sau nghe. Tôi muốn giữ cả phần ông đã đổi ý hoặc không chịu đổi, không lấy đoạn cuối ghép lên mọi đoạn đầu.

## SQ-VN-05 · Lời nhắn của Cơ / ACTIVE

`DLG_SQ_VN_05_CLUE` · `NPC_LYAN`

Cô để một khoảng giấy trống giữa hai ngày không liền.

Khoảng này không có bản ghi. Đừng tự nối một câu cho trôi. Những lời ở đây phải đối với chuyện các vùng đã trải qua, không chỉ với lời ông ấy kể về mình.

## SQ-VN-05 · Lời nhắn của Cơ / READY_TO_TURN_IN

`DLG_SQ_VN_05_TURN_IN` · `NPC_LYAN`

Năm bản ghi có thứ tự, cả quãng không ai giữ được tiếng. Ly An ghi nơi tìm thấy từng bản, giữ riêng phần người sống đã đối lại.

Tôi sẽ đưa đủ. Ai nhận cũng phải thấy khoảng thiếu này.

Chúng không làm Cơ được tha, cũng không biến việc ông từng cứu nước thành chuyện chưa từng xảy ra.

## SQ-DM-01 · Người canh trụ / AVAILABLE

`DLG_SQ_DM_01_OFFER` · `NPC_LYAN`

Ly An chừa năm ghế quanh bàn nhận tin sau trận, có chiếc kê thấp hơn để người bị thương ngồi.

Hỏi năm người canh trụ đã qua đêm ấy thế nào. Tôi có bản trận kết thúc, chưa có lời của họ. Ai muốn kể sau thì ghi giờ họ chọn, đừng coi lời im lặng là không có chuyện gì.

## SQ-DM-01 · Người canh trụ / ACTIVE

`DLG_SQ_DM_01_CLUE` · `NPC_LYAN`

Cô xếp tờ đếm lực sang bên, lấy giấy trắng khác.

Không cần hỏi họ đã đánh được bao nhiêu trước. Có người chỉ giữ đường tới chỗ trú. Phần ấy không nằm gọn trong bản thành tích, tôi vẫn muốn nghe.

## SQ-DM-01 · Người canh trụ / READY_TO_TURN_IN

`DLG_SQ_DM_01_TURN_IN` · `NPC_LYAN`

Năm cuộc trao đổi được ghi theo phần người kể cho giữ. Ly An để các giọng không đồng ý nhau trên những tờ riêng.

Tôi không ghép thành một câu cảm ơn chung.

Chiếc ghế thấp vẫn ở bàn, cho người trở lại muộn hơn không phải đứng chờ tới lúc được gọi tên.

## SQ-DM-02 · Năm món ăn / AVAILABLE

`DLG_SQ_DM_02_OFFER` · `NPC_LYAN`

Ly An dọn giấy khỏi nửa bàn, để năm phần nguyên liệu có chỗ nằm riêng.

Nấu ở sảnh từ nguyên liệu năm hệ. Tôi biết giao đồ, chưa biết nêm hết những món này. Bạn hỏi người mang từng phần rồi hãy trộn; nếu ai không ăn được thứ nào thì chừa cho họ một phần trước.

## SQ-DM-02 · Năm món ăn / ACTIVE

`DLG_SQ_DM_02_CLUE` · `NPC_LYAN`

Cô giơ thìa lên định thử, rồi đặt xuống để người nấu chỉ cách.

Không phải cứ năm thứ vào một nồi là xong. Bạn giữ phần nào cần nấu riêng. Tôi đi gọi người canh trụ vào ăn, lần này không bắt họ đứng thành hàng để nhận giấy.

## SQ-DM-02 · Năm món ăn / READY_TO_TURN_IN

`DLG_SQ_DM_02_TURN_IN` · `NPC_LYAN`

Năm món có chỗ trên bàn. Có bát không thêm một thứ người ngồi cạnh không ăn được; không ai phải giải thích trước cả sảnh.

Ly An ngồi xuống giữa bữa mới nhận ra mình vẫn cầm bút. Cô cất nó, xin người bên cạnh đưa giúp phần món còn chưa nếm.

## SQ-DM-03 · Vết nứt còn lại / AVAILABLE

`DLG_SQ_DM_03_OFFER` · `NPC_LYAN`

Ly An đặt ba dấu báo khe nứt cạnh bản đường thường, không đưa chúng vào tập giấy đã ghi trận cuối.

Vẫn còn ba khe nhỏ cần khép. Người qua đường không thể đợi tới tuần hội mới được yên. Xem chỗ nào có người đang đi trước khi bắt tay vào, tôi sẽ giữ bản báo ở đây.

## SQ-DM-03 · Vết nứt còn lại / ACTIVE

`DLG_SQ_DM_03_CLUE` · `NPC_LYAN`

Cô sửa đường tới trạm nhận thay vì chỉ khoanh vùng nguy hiểm.

Báo được khe đã khép cũng phải báo lối mở lại. Nếu một khe khác còn hoạt động, giữ nó trên bản đồ. Ta không cần làm tờ giấy sau trận trông hoàn hảo.

## SQ-DM-03 · Vết nứt còn lại / READY_TO_TURN_IN

`DLG_SQ_DM_03_TURN_IN` · `NPC_LYAN`

Ba khe được đóng, Ly An đối giờ và đường đã trả lại cho dân.

Tôi ghi vào sổ chăm mạch, không ghi như chúng ta vừa phải thắng lại một người đã bị đưa đi xét xử.

Bản nhận nằm ở nơi người đi đường có thể xem lần kiểm gần nhất.

## SQ-DM-04 · Tấm bia không tên / AVAILABLE

`DLG_SQ_DM_04_OFFER` · `NPC_LYAN`

Ly An che tấm bia khỏi mưa bằng mảnh bạt dùng từ bàn nhận tin.

Chọn năm nhân chứng để ghi, nhưng hỏi họ trước về tên muốn để lại. Có người cần tên mình trở lại, có người chưa muốn ai tìm theo tên ấy. Chỗ trống chưa có phép thì cứ chừa.

## SQ-DM-04 · Tấm bia không tên / ACTIVE

`DLG_SQ_DM_04_CLUE` · `NPC_LYAN`

Cô viết thử tên trên giấy rời cho người được hỏi xem, không giục người khắc.

Một dấu sửa bây giờ dễ hơn trên đá. Nếu họ đổi ý, giữ bản chấp thuận cũ trong hồ sơ và dùng lựa chọn mới ở mặt công khai. Đừng bắt họ bảo vệ một cái tên ta đã tự quyết.

## SQ-DM-04 · Tấm bia không tên / READY_TO_TURN_IN

`DLG_SQ_DM_04_TURN_IN` · `NPC_LYAN`

Năm cách ghi được xác nhận theo người liên quan. Tấm bia còn chỗ trống, phần chú giải nói rõ có người chưa muốn để tên.

Ly An trả tấm bạt về bàn, kiểm bản sao ở tay người giữ hồ sơ. Bia không kể hết mọi chuyện; nó chỉ giữ đúng phần đã được trao.

## SQ-DM-05 · Chuyến thư mới / AVAILABLE

`DLG_SQ_DM_05_OFFER` · `NPC_LYAN`

Ly An đặt xấp thư mới cạnh giấy trắng chưa viết, đổi mặt địa chỉ về phía người sắp mang đi.

Chuyển tới từng vùng giúp tôi. Lần này mỗi nơi có chỗ gửi lại; đừng chỉ báo đã giao. Ai chưa viết được thì nhờ người họ chọn chép, không cần dùng lời của tôi.

## SQ-DM-05 · Chuyến thư mới / ACTIVE

`DLG_SQ_DM_05_CLUE` · `NPC_LYAN`

Cô đọc lại từng địa chỉ, dừng ở nơi một tên đã được sửa khỏi danh sách người chết.

Dùng tên mới ở bản gửi, giữ dấu sửa trong hồ sơ. Nếu người nhận đã chuyển nhà, hỏi nơi họ muốn được tìm. Chuyến thư này không cần làm họ quay lại chỗ đã rời.

## SQ-DM-05 · Chuyến thư mới / READY_TO_TURN_IN

`DLG_SQ_DM_05_TURN_IN` · `NPC_LYAN`

Các vùng đã nhận thư. Một tờ hồi âm tới sau xấp báo giao: nét chữ nghiêng, có chỗ chấm mực quá lâu. Người viết hỏi bao giờ có chuyến qua để gửi thêm.

Ly An lật tờ giấy trắng sang mặt địa chỉ, bắt đầu ghi một ngày hẹn. Lần này cô không cất bức thư trước khi đọc hết câu hỏi.
