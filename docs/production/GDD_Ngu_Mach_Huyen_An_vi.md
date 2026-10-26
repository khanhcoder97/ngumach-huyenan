# NGŨ MẠCH: HUYỀN ẤN

**Tài liệu thiết kế game (GDD) — bản nền v1.0**  
Ngày lập: 22/10/2026  
Tên hiện tại: **Ngũ Mạch: Huyền Ấn** (working title; chưa tra cứu/đăng ký nhãn hiệu)  
Thể loại: MMORPG hành động 2D nhìn ngang, giả tưởng võ hiệp – huyền thuật  
Nền tảng: PC và điện thoại, dùng chung máy chủ/tài khoản  
Ngôn ngữ phát hành đầu tiên: tiếng Việt

> Mục tiêu là giữ nhịp MMORPG 2D cổ điển — tạo nhân vật, luyện cấp, săn quái, kiếm đồ, học kỹ năng, lập đội và bang hội — nhưng xây thế giới, nhân vật, lời thoại, hình ảnh và dữ liệu mới. Đồ họa pixel art hiện đại, không phụ thuộc công nghệ J2ME cũ.

**Bộ tài liệu sản xuất chi tiết:** xem Production_Index_vi.md và Production_Decision_Register_vi.md để tìm nguồn chuẩn, đặc tả nhiệm vụ, kỹ năng/VFX, UI/UX, trang bị/túi, map, bang hội, dungeon, raid, PvP, API, QA và data import.

## 1. Tầm nhìn và quyết định nền

### 1.1 Mô tả trong một câu

Một MMORPG hành động 2D pixel art, nơi người chơi chọn một trong năm môn phái, khám phá Lạc Châu đang rối loạn bởi năm mạch nguyên tố, săn quái và chế tạo trang bị, rồi hợp sức ngăn kẻ muốn ép thế giới vào một mạch duy nhất.

### 1.2 Quyết định mặc định

| Hạng mục | Quyết định |
|---|---|
| Góc nhìn | Đi cảnh ngang 2D; di chuyển trái/phải, nhảy qua địa hình đơn giản, nhiều lớp nền |
| Chiến đấu | Thời gian thực; đánh thường, né, khóa mục tiêu và kỹ năng |
| Nền tảng | PC + Android/iOS, một tài khoản dùng nhân vật chung |
| Cấp tối đa bản đầu | 100 |
| Môn phái | 5; chọn lúc tạo nhân vật, không đổi giữa trận |
| Nhóm | 5 người; raid tối đa 10 người |
| Bang hội | 40 thành viên lúc mở đầu; tăng qua tiến trình chơi |
| Mỹ thuật | Pixel art 2D frame-based; 640×360 logical, 20 PPU, scale nguyên; spritesheets nhân vật/quái/VFX và tilemap; không raster HD/rig deformation |
| Kinh tế | Đồng trong game; phân biệt rõ đồ khóa/không khóa; cửa hàng tiền thật chỉ bán mỹ phẩm và tiện ích không tăng sức mạnh |
| Máy chủ | Server-authoritative: máy chủ quyết định vị trí hợp lệ, sát thương, loot, giao dịch và tiền |

Số liệu chiến đấu bên dưới là điểm bắt đầu cho prototype, cần cân bằng qua dữ liệu chơi thử. Luật hệ thống và luồng chơi là yêu cầu mặc định.

### 1.3 Phạm vi rút ra từ JAR KPAH đã giải mã

JAR là client đã biên dịch; dữ liệu nhiệm vụ, lớp nhân vật và nhiều bảng nội dung được nạp từ máy chủ. JAR cho thấy rõ hệ thống và kiểu dữ liệu, nhưng không lưu đầy đủ cốt truyện gốc, toàn bộ tên/vị trí vật phẩm hay cân bằng máy chủ.

| Tham chiếu xác nhận trong mã client | Cách dùng trong game mới |
|---|---|
| 5 mã lớp KIEM, DAO, PS, DS, CUNG; tên/lớp được nạp từ server | Dùng 5 vai trò tương ứng về nhịp chơi, đặt tên và lore mới |
| Các chỉ số strength, spirit, agility, health, luck; HP/MP, né, chính xác, chí mạng | Chuẩn hóa thành bộ chỉ số rõ nghĩa và có công thức máy chủ |
| Kim, Thủy, Mộc, Hỏa, Thổ | Giữ vòng tương khắc như lớp chiến thuật tùy chọn |
| Nhiều nhóm đồ: áo, quần, nón, kiếm/đao/bút/búa/cung, nhẫn, dây chuyền, giày, găng, ngọc bội, cuốc, đồ linh thú, yên, phi phong | Chuyển thành slot nhân vật, công cụ nghề và trang bị thú |
| Đồ có cấp, hệ, lớp, độ bền, thuộc tính, cộng cấp, khóa, hạn dùng, lỗ khảm | Tạo item system dễ kiểm tra và cân bằng |
| Học/nâng kỹ năng, buff, hồi chiêu, phạm vi, MP; đánh đơn/nhiều mục tiêu và PvP | Chiến đấu server-authoritative, lớp có bản sắc riêng |
| Quest/NPC/bản đồ/quái/nhà buôn trong client nhưng dữ liệu nhận từ server | Xây nhiệm vụ và cốt truyện mới theo tài liệu này |
| Đăng nhập/tạo nhân vật, dịch chuyển, chat, bạn bè, nhóm, bang, xếp hạng, giao dịch | Giữ chức năng xã hội MMORPG cốt lõi |
| Cửa hàng, rao bán/tìm kiếm/trả giá, mua bán người chơi | Chợ có ký quỹ và lịch sử giao dịch |
| Sửa/cường hóa/khảm/chế tạo/tách nguyên liệu/đổi thuộc tính/tự cường hóa | Hợp nhất thành xưởng chế tác có chi phí và xác suất minh bạch |
| Thú cưỡi/thú nuôi, trồng/thu hoạch, khoáng vật, mini game, vé, auto, nhiệm vụ bang và công thành | Có hệ đời sống/sự kiện tương ứng, với giới hạn chống lạm dụng |

Mã tham chiếu: outputs/KPAH_276_decompiled/src/game/model/Char.java, ItemTemplate.java, ItemInInventory.java, MainChar.java, Quest.java, Party.java, ClanInfo.java, CongThanh.java, MyTree.java, game/networklogic/GameService.java, MessageHandler.java, game/render/screen/GameScr.java, ShopOnline.java, BangAuto.java.

## 2. Trải nghiệm cốt lõi

### 2.1 Ba trụ cột

1. **Đánh có phản hồi:** né đòn, căn hướng, chọn kỹ năng và phối hợp; quái có báo hiệu, không đứng yên nhận sát thương.
2. **Mỗi chuyến đi tạo tiến triển:** nhiệm vụ, vật liệu, trang bị, kỹ năng hoặc quan hệ xã hội mở thêm lựa chọn.
3. **Thế giới có người:** thành thị là nơi gặp gỡ, bang hội có mục tiêu chung, hoạt động nhóm không buộc cày liên tục.

Vòng chơi: **nhận mục tiêu → đi vùng → đánh/né/giải cơ chế → nhận EXP/vật liệu/đồ → nâng cấp/chế tạo/giao dịch → mở nội dung khó hơn → chơi cùng nhóm/bang**. Phiên 10 phút vẫn có mục tiêu hoàn tất được.

## 3. Cốt truyện và thế giới

### 3.1 Thế giới và xung đột

Lạc Châu được nuôi bởi năm **Mạch Nguyên**: Kim, Mộc, Thủy, Hỏa và Thổ. Khi cân bằng, mùa màng và linh thú tồn tại hài hòa. Khi một mạch bị rút cạn, vùng đất biến dạng: nước chảy ngược lên trời, rừng ăn ký ức, kim loại mọc như gai, lò lửa không tắt, núi đá biết thở.

Ba trăm năm trước, địa chấn làm vỡ **Huyền Ấn**, cơ chế cổ giúp năm mạch trao đổi năng lượng. Các môn phái đổ lỗi cho nhau và dựng năm tháp canh riêng. **Cơ Vô Tướng**, khi còn là quan trắc sư, mất quê hương trong nạn hạn – lũ nối tiếp. Ông tin tranh chấp sẽ chấm dứt nếu gộp năm mạch thành một dòng duy nhất. Thí nghiệm đầu làm Huyền Ấn rạn thêm, tạo ra Nghịch Mạch. Ông âm thầm hút năng lượng từ các vùng để hoàn tất phép hợp nhất.

Cơ Vô Tướng không muốn hủy diệt thế giới; ông muốn xóa khác biệt và kiểm soát rủi ro bằng một trật tự tuyệt đối. Mâu thuẫn trung tâm: **cân bằng có chấp nhận hỗn loạn và lựa chọn cá nhân hay không?**

### 3.2 Nhân vật chính và NPC

- **Người Dẫn Mạch:** nhân vật người chơi; không phải anh hùng được chọn từ đầu. Một mảnh Huyền Ấn phản ứng với họ, cho phép cảm nhận mất cân bằng nhưng không tự ban sức mạnh.
- **Ly An:** người đưa thư ở Bến Mưa; nhanh trí, thực tế, dẫn người chơi qua các vùng.
- **Tạ Vân Khanh:** cựu hộ ấn sư, huấn luyện người chơi; từng dự cuộc họp khiến năm môn phái đoạn giao.
- **Hạ Mặc:** học giả khảo cổ; muốn công bố lịch sử dù việc đó làm các trưởng môn phái mất chính danh.
- **Sầm Chủ Quỹ:** thương nhân trung lập, điều hành tuyến vận tải và kho chung; giao nhiệm vụ kinh tế.
- **Tống Bành:** tướng giữ biên thành; ban đầu là đồng minh, sau lộ ra đã gây chiến giả theo lệnh Cơ Vô Tướng.
- **Cơ Vô Tướng:** phản diện chính; có lý do đáng hiểu nhưng chọn cưỡng ép toàn thế giới.

### 3.3 Chiến dịch chính

| Chặng | Cấp | Vùng | Nhiệm vụ/cốt truyện | Trùm |
|---|---:|---|---|---|
| Mở đầu: Nước không soi bóng | 1–10 | Bến Mưa, Đầm Chuông | Giao thư; điều tra cá chết/chuông dưới nước; tìm dân mất tích; hộ tống Ly An; chọn môn phái. Mảnh ấn phát sáng nhưng chưa rõ lý do. | **Mãng Cốt**, linh thú bị Nghịch Mạch xâm thực |
| I: Năm lời thề | 11–20 | Thành Thanh Lạc, Thăng Long Thành | Dự lễ nhập môn; thử thách môn phái; tìm kẻ giả phù tín; phá tượng đá; thuyết phục năm môn phái ngừng giao chiến. C1-06 đưa bằng chứng tới thủ phủ; Hạ Mặc lần theo dấu resin về Lâm Triều. | **Tượng Hành Hỏa**, máy canh cổ |
| II: Rừng nhớ tên người | 21–35 | Lâm Triều, Rễ Ngủ | Tìm đội đốn cây; thu hồi ký ức bị rễ hút; hộ tống thuốc giải; tìm đường nước bị khóa; mở lại mạch suối. Nhật ký cho thấy Cơ Vô Tướng đã tới trước khủng hoảng. | **Cổ Thụ Trăm Mắt**, rễ/ảo ảnh/vùng an toàn di chuyển |
| III: Lò không tắt | 36–50 | Sa Hỏa, Trạm Tro | Hộ tống đoàn xe nước; điều tra lò rèn; giải cứu thợ mỏ bị cưỡng ép; ngăn lò phun lửa; quyết định công bố bằng chứng hay giao các trưởng môn. Quyết định chỉ đổi hội thoại/danh vọng, không tách máy chủ. | **Lò Trời**, tắt ba van mạch |
| IV: Thành không có chủ | 51–65 | Trấn Sơn, Ải Cờ | Sơ tán dân; ngăn hai đoàn quân; điều tra lệnh giả; bang hội giữ ba cổng trong công thành cốt truyện; đối đầu Tống Bành và lấy bản đồ năm tháp. | **Tống Bành – Thiết Giáp Tướng**, phá khiên bằng mục tiêu môi trường |
| V: Thành phố dưới Bạch Uyên | 66–80 | Bạch Uyên, Đài Quan Trắc | Lặn xuống di tích; sửa ba trạm áp suất; ghép nhật ký; đối mặt ký ức người chết trong thí nghiệm đầu; đưa sự thật về Thanh Lạc. Không môn phái nào vô can, nhưng không phe nào một mình gây tai họa. | **Mẫu Xà Thủy**, đổi nhịp theo thủy triều |
| VI: Nghịch Mạch | 81–100 | Vực Nghịch Mạch, Năm Tháp | Khôi phục năm tháp; chặn quái; lấy lõi ấn; đánh Cơ Vô Tướng ba pha; raid 10 người kích hoạt năm trụ và chia đội phòng thủ/gây sát thương. Kết cục chung là sửa Huyền Ấn để năm mạch trao đổi nhưng không bị một người điều khiển. | **Cơ Vô Tướng / Hợp Mạch** |

Sau chiến dịch, tuyến **Mạch Triều** tạo biến cố luân phiên hằng tuần. Không xóa tiến độ cũ.

### 3.4 Nhiệm vụ/hội thoại

- Nhiệm vụ chính theo cấp/chương; tối đa 5 mục tiêu theo dõi.
- Nhiệm vụ phụ mở công thức, điểm dịch chuyển, thú, mỹ phẩm và chuyện NPC.
- Ngày: chọn 3 việc từ truy nã/thu thập/hộ tống; bỏ và thay một lần.
- Tuần: dungeon, trùm vùng, đóng góp bang, thử thách chế tác.
- Bang: vật liệu, đoàn xe, truy quét trùm; giới hạn phần thưởng cá nhân, có thanh tiến độ chung.
- Hội thoại 1–3 lựa chọn ngắn; có thể đổi lời thoại/danh vọng/mỹ phẩm, không khóa cốt truyện hoặc sức mạnh.
- Mỗi quest có ID cố định, điều kiện mở, bước, vùng/NPC, mục tiêu, reset, phần thưởng, cờ lưu và văn bản bản địa hóa. Server ghi nhận hoàn tất.

## 4. Nhân vật, môn phái, kỹ năng

### 4.1 Tạo nhân vật

Tối đa 4 nhân vật mỗi tài khoản lúc mở đầu; tên không trùng; chọn kiểu cơ thể/giới tính trình bày, tông da, tóc, khuôn mặt và môn phái. Ngoại hình đầu game là mỹ phẩm. Mỗi môn phái có chuỗi 5 nhiệm vụ nhập môn.

### 4.2 Năm môn phái mới

Tên lớp dưới đây được thiết kế mới để đại diện cho năm nhịp vũ khí quan sát thấy trong mã tham chiếu; không khẳng định đó là tên chính thức trong server KPAH.

| Môn phái | Vũ khí/hệ | Vai trò/vòng chơi | Kỹ năng tiêu biểu |
|---|---|---|---|
| **Minh Kiếm** | Kiếm / Kim | Đấu sĩ cận chiến; tích Kiếm Ý bằng combo, đỡ đúng nhịp rồi phản kích | Phản Quang (đỡ/phản kích); Tầm Long (áp sát); Kiếm Trận (quạt); Thiết Y (phòng thủ); Bạch Hồng (lướt); tuyệt kỹ Vạn Tượng Quy Nhất |
| **Ảnh Đao** | Đao / Hỏa | Sát thủ cơ động; tích Nhiệt, gây chảy máu, tiêu Nhiệt kết liễu mục tiêu yếu | Huyết Nguyệt; Tàn Hỏa; Xích Ảnh; Tước Mạch; Ảnh Bộ; tuyệt kỹ Tử Diệm |
| **Huyền Bút** | Bút / Thủy | Pháp sư hỗ trợ; đánh xa, khống chế, khiên nhỏ, hồi phục có điều kiện | Mực Triều; Thủy Kính; Hàn Châm; Mưa Tinh; Lưu Thủy Bộ; tuyệt kỹ Long Mạch Hồi Nguyên |
| **Thạch Chùy** | Búa / Thổ | Đỡ đòn/khống chế; tích Thế, kéo chú ý quái, tạo cửa sổ an toàn | Trấn Sơn; Chấn Địa; Thiết Bích; Khiêu Chiến; Phá Nham; tuyệt kỹ Sơn Thần Giáng Thế |
| **Linh Cung** | Cung / Mộc | Xạ thủ; đánh dấu, giữ vị trí, đặt bẫy | Liên Châu; Khóa Mạch; Dây Gai; Tán Hoa; Phi Diệp; tuyệt kỹ Bách Tiễn Quy Tông |

Mỗi lớp có 6 kỹ năng chủ động và 8 node nội tại (2 nhánh × 4 node). Người chơi trang bị 4 kỹ năng chủ động, 1 kỹ năng cơ động/phòng thủ, 1 tuyệt kỹ và tối đa 2 passive cùng lúc; đòn thường không chiếm ô. Có 2 cấu hình đổi tại thành phố/nơi nghỉ, không đổi giữa boss. Hiệu ứng từng node và class caps nằm trong `Class_Passive_Production_Data_vi.csv`.

### 4.3 Học kỹ năng

- Đòn cơ bản từ cấp 1; sáu ô kỹ năng chủ động mở ở cấp 1/4/8/12/16/30, trong đó ô cấp 30 dành cho tuyệt kỹ.
- Mỗi kỹ năng 5 bậc; điểm từ lên cấp/nhiệm vụ môn phái, không bán bằng tiền thật.
- Nội tại: hai nhánh × bốn node ở cấp 20/40/60/80; trang bị tối đa hai node đã mở. Hoàn lại bằng Đồng theo bảng giá trong data pack, hiện chi phí trước xác nhận.
- Kỹ năng có loại sát thương, hệ, phạm vi, thi triển, hồi chiêu, MP, hiệu ứng và điều kiện mục tiêu trong data.
- Boss kháng khống chế dài; khống chế tích “choáng mạch”, không cho khóa trùm liên tục.

### 4.4 Chỉ số và tương khắc

Chỉ số: **Sức mạnh** (vật lý), **Linh lực** (phép/MP), **Nhanh nhẹn** (chính xác/né/tốc độ), **Thể chất** (HP/phòng thủ), **Vận khí** (chí mạng/kháng chí mạng). Người chơi tự phân bổ điểm mỗi cấp; gợi ý không tự tiêu.

Vòng khắc: **Kim khắc Mộc → Mộc khắc Thổ → Thổ khắc Thủy → Thủy khắc Hỏa → Hỏa khắc Kim**. Khắc hệ tối đa ±10% PvE; tối đa ±4% PvP; không áp dụng lên hồi máu. Hiển thị biểu tượng hệ trước trận.

### 4.5 Công thức prototype

Server tính sát thương; client chỉ hiển thị. Điểm khởi đầu:

- HP tối đa = HP nền + 28 × cấp + 14 × Thể chất + HP trang bị.
- MP tối đa = MP nền + 12 × cấp + 8 × Linh lực + MP trang bị.
- Sát thương vật lý = vũ khí + 3 × Sức mạnh + Nhanh nhẹn + hệ số kỹ năng.
- Sát thương phép = vũ khí phép + 3 × Linh lực + Vận khí + hệ số kỹ năng.
- Sát thương nhận = sát thương gốc × 100 / (100 + phòng thủ mục tiêu); phòng thủ chuẩn hóa theo cấp.
- Trúng = 90% + chính xác − né, chặn 5–98%; chí mạng cơ sở 150%; khống chế PvP tối đa 1.2 giây mỗi hiệu ứng.
- Hệ số sát thương PvP ban đầu 0.65, chỉnh server-side, không hard-code client.

## 5. Cấp độ, trang bị và vật phẩm

### 5.1 Tiến trình

| Cấp | Mở khóa |
|---:|---|
| 1–10 | hướng dẫn, môn phái, đánh thường, né, đồ cơ bản |
| 11–20 | kỹ năng lớp, nghề thu thập, chế tạo, nhóm 5 |
| 21–35 | khảm, bang hội, dungeon đầu, thú đồng hành |
| 36–50 | cường hóa, chợ, phụ bản nâng cao, đoàn xe |
| 51–65 | chiến trường bang, công thành, trùm vùng |
| 66–80 | raid 10 người, cổ vật, nhiệm vụ tuần |
| 81–100 | chiến dịch cuối, thử thách đỉnh mạch, đồ cuối bản đầu |

EXP từ nhiệm vụ, chiến đấu, hoạt động nhóm và khám phá. Phụ bản có giới hạn phần thưởng lớn theo ngày nhưng vẫn cho vật liệu nhỏ khi chơi thêm.

### 5.2 Slot và phẩm chất

Nhân vật có 12 slot: **nón, áo, quần, vũ khí, găng, giày, dây chuyền, nhẫn trái, nhẫn phải, ngọc bội, phi phong, ấn hộ mệnh**. Công cụ khai khoáng/hái thuốc có slot riêng; tủ mỹ phẩm không có chỉ số. Thú đồng hành có mũ, giáp, vòng cổ, yên/đai.

Phẩm chất: **Thường, Tinh, Linh, Huyền, Cổ Vật**. Bậc đồ theo dải cấp 1–15, 16–30, 31–45, 46–60, 61–75, 76–90, 91–100. Mỗi món có cấp yêu cầu, lớp, hệ, độ bền, chỉ số nền, tối đa 4 dòng phụ và 0–3 lỗ khảm. Pool phụ gồm công, phép, HP/MP, giáp, kháng phép, chính xác, né, chí mạng, kháng chí mạng, hồi phục, hồi chiêu. Bộ 2/4 món cho hiệu ứng nhỏ; không bắt buộc đủ bộ.

### 5.3 Cường hóa/chế tác

- Cường hóa +0 đến +15; +1–5 chắc chắn; +6–10 thất bại không mất cấp/đồ; +11–15 cần vật liệu bảo hộ nhưng không phá trang bị. Luôn hiển thị tỷ lệ và chi phí.
- Khảm 1–3 lỗ; ngọc 5 cấp; ghép 3 viên cùng cấp thành cấp sau; rút ngọc luôn trả lại viên.
- Tinh luyện: chọn dòng đổi, khóa dòng giữ, xem pool/chi phí và kết quả trước khi xác nhận.
- Công thức từ quest, nghề, bang, boss; nguyên liệu quặng/gỗ/dược thảo/linh phách/vật liệu boss.
- Phân giải trả vật liệu theo bậc; đồ khóa trả vật liệu khóa; có xác nhận khi phân giải nhiều.
- Độ bền giảm theo thời gian chiến đấu, không giảm khi chết; 0 độ bền giảm 10% chỉ số cho đến khi sửa, không mất đồ.
- Đổi loại chỉ cho món tương thích; không đổi đồ sang lớp khác.
- Auto-cường hóa dừng ở ngưỡng người chơi đặt, khi đạt cấp/hết đồ/thay đổi tỷ lệ/mất kết nối/cảnh báo.
  
### 5.4 Túi và nhóm vật phẩm

Túi 100 ô, kho cá nhân 120 ô, có kho bang. Vật phẩm gắn trạng thái **khóa nhân vật / khóa khi nhặt / giao dịch được / hạn dùng**; đồ khóa không được rao hoặc đưa giao dịch.

Nhóm vật phẩm: trang bị; ngọc/đá; thuốc HP/MP/giải hiệu ứng; thức ăn buff PvE; nguyên liệu; công thức; nhiệm vụ; vé hoạt động; hạt giống/trái cây; thú/cưỡi; mỹ phẩm; dịch chuyển; sửa đồ. Thuốc HP/MP dùng chung hồi chiêu 8 giây. Hòm hiển thị nội dung/xác suất; hòm tiền thật không chứa sức mạnh, ưu tiên cửa hàng chọn trực tiếp.

### 5.5 Thú, cưỡi, nghề và nông trại

- Mỗi nhân vật có 1 thú hoạt động; đổi ngoài giao tranh. Ba vai trò: hồi phục nhỏ, đánh dấu mục tiêu hoặc nhặt đồ. Ba kỹ năng chọn từ hai hướng; thú không vượt vai trò người chơi.
- Thú lên cấp qua hoạt động; không bán thú chỉ số cao bằng tiền thật.
- Cưỡi mở qua quest/sự kiện; tốc độ theo cấp, không tăng sát thương; tắt trong dungeon/PvP.
- Nông trại cấp 20: 6 luống, trồng hạt/thu hoạch theo giờ, tối đa 24 giờ offline; thu thức ăn/nguyên liệu, không mua thời gian để tăng sức mạnh.
- Ba nghề: khai khoáng, hái dược, đốn gỗ; node hồi chu kỳ, vật liệu vùng dùng trong công thức vùng.

## 6. Bản đồ và hoạt động

### 6.1 Vùng

| Vùng | Cấp | Chủ đề | Điểm dịch chuyển |
|---|---:|---|---|
| Bến Mưa | 1–10 | bến nước/đầm lau/Mãng Cốt nhỏ | Bến Gỗ |
| Thanh Lạc | 10–20 | thành an toàn, chợ, môn phái | Quảng Trường |
| Thăng Long Thành | 11+ | thủ phủ, chợ lớn, PvP tuần và dịch chuyển liên vùng | Cửa Tây / Trạm Dịch Chuyển Đông |
| Lâm Triều | 21–35 | rừng rễ, ký ức, linh thú | Cầu Rễ |
| Sa Hỏa | 36–50 | sa mạc, lò rèn, đoàn xe | Trạm Tro |
| Trấn Sơn | 51–65 | tường thành, hẻm núi, chiến trường | Cổng Bắc |
| Bạch Uyên | 66–80 | thành chìm, thủy triều, phế tích | Đài Lặn |
| Vực Nghịch Mạch | 81–100 | méo không gian, năm tháp | Trại Hợp Mạch |
| Đài Ngũ Mạch | 100 | raid cuối | Sảnh Ấn |

Mỗi vùng chiến đấu: 1 tuyến chính, 6–10 quest phụ, 3 quái thường, 2 tinh anh, 1 boss vùng, 3–5 node thu thập, 1 bí mật và 1 điểm dịch chuyển. Thăng Long Thành là map đô thị an toàn 900×96 WU, không có spawn quái/PvP tự do; chi tiết blockout ở `Thang_Long_Thanh_Capital_Map_Spec_vi.md`.

### 6.2 PvE

- Săn quái: cụm quái theo vùng, đòn có báo trước.
- Truy nã: chọn 1 trong 3 mục tiêu ngày; quái tinh anh/dấu vết; thưởng Đồng/nguyên liệu.
- Đoàn xe: nhóm 5 người, 3 chặng, chọn đường nhanh nguy hiểm hoặc dài an toàn.
- 4 dungeon 5 người lúc ra mắt; 15–25 phút, 2 boss + cơ chế cuối; loot cá nhân.
- 2 raid 10 người; mỗi raid 3 encounter (2 encounter mục tiêu/add và 1 boss cuối), hiện có 1 boss canonical mỗi raid.
- Boss vùng theo lịch công bố; thưởng cá nhân, không cướp đồ.
- Tháp thử thách 30 tầng, 1–5 người; mỗi 5 tầng chọn hiệu ứng, bảng theo mùa.
- Mini game bắn bia/vượt chướng ngại/ghép mạch; thưởng vật liệu/cosmetic token.
- Auto PvE: đánh thường, tối đa 2 kỹ năng, nhặt đồ phổ thông, đi tuyến đã đặt; tự tắt ở boss/PvP/túi đầy/mất kết nối/nguy hiểm. Không vào xếp hạng, giao dịch hay tự chế đồ.

### 6.3 PvP/công thành

- Đấu tay đôi có đồng ý, không rơi đồ.
- Đấu trường 1v1/3v3, trận 3 phút, chuẩn hóa trang bị theo ngưỡng mùa; thưởng danh hiệu/khung/mỹ phẩm.
- Giải Đấu Trường Long Môn 3v3 mỗi tuần tại Thăng Long Thành: vòng bảng → knock-out → chung kết; leaderboard tuần/mùa và danh hiệu mùa top 3, toàn bộ reward là vanity.
- Chiến trường Trấn Sơn 10v10 là queue/instance riêng, dùng art/geometry MAP_TRAN_SON_SIEGE trong zone `BG10`; objective ba điểm và chuyển cờ, chuẩn hóa chỉ số, không dùng chung roster/reward/rating với công thành 20v20. Luật đầy đủ ở `Battleground_10v10_Production_Spec_vi.md`.
- Công thành bang 20v20 mỗi tuần; ghép theo sức mạnh/số người; mục tiêu cổng, trạm tiếp tế, cờ ấn. Thưởng trang trí/cờ bang, không tạo lợi thế kinh tế vô hạn.
- Không PvP mở với người không đồng ý; vùng giao chiến đặc biệt phải được đánh dấu và có cửa thoát.
- Hệ số PvP độc lập; trang bị cường hóa không quyết định tuyệt đối kết quả.

## 7. Xã hội và kinh tế

### 7.1 Nhóm, bạn bè, chat

Nhóm 5 người; mời theo tên/ID, chuyển chủ, chia loot mặc định cá nhân hoặc luân phiên khi cả nhóm đồng ý. EXP theo đóng góp và khoảng cách; không phạt người hồi máu/khống chế. Có bạn bè, online status, chặn, tìm nhóm theo dungeon/hoạt động. Chat gồm thế giới (giới hạn tốc độ), khu vực, nhóm, bang, riêng; có lọc spam, báo cáo, mute, kiểm duyệt. Thư chỉ nhận hoàn giao dịch/tiền bán chợ, không làm kho né giới hạn.

### 7.2 Bang hội

Tạo bang bằng Đồng + nguyên liệu nhiệm vụ từ cấp 10; tên/icon/khẩu hiệu qua kiểm duyệt. Vai trò Bang chủ/Phó/Trưởng lão/Thành viên; quyền mời, kick, kho, công thành tách riêng. Bang có cấp, XP, quỹ, nhiệm vụ tuần, sảnh. Đóng góp có giới hạn ngày. Nghiên cứu mở mỹ phẩm sảnh/dịch vụ xã hội, không tăng sát thương ngoài bang. Công thành có luật, lịch, điều kiện, thưởng công khai.

### 7.3 Tiền, giao dịch, chợ

| Tiền | Nguồn | Sử dụng |
|---|---|---|
| Đồng | quest, quái, bán nguyên liệu, hoạt động | sửa đồ, kỹ năng, chế tác, chợ |
| Linh Ngọc khóa | quest/sự kiện, không giao dịch | tiện ích/mỹ phẩm |
| Ấn Mùa | hoạt động mùa/PvP | cửa hàng mùa/danh hiệu/trang trí |
| Ấn Long Môn | trận giải PvP hàng tuần | chỉ đổi ngoại trang/động tác tại Thăng Long Thành; khóa tài khoản |

Nếu bán tiền thật, chỉ bán mỹ phẩm và tiện ích không ảnh hưởng tốc độ tăng sức mạnh/loot; không bán Đồng/Linh Ngọc chuyển nhượng, vũ khí hay cấp kỹ năng.

- Giao dịch trực tiếp hai bước; thay món/tiền yêu cầu hai bên xác nhận lại; chống đổi món lúc chốt.
- Chợ hỗ trợ bán/mua ngay/trả giá/tìm theo tên/bậc/phẩm chất/hệ/thuộc tính/cấp; ký quỹ khi mua; đồ khóa không rao.
- Thuế 5%, hiện trước niêm yết; cảnh báo giá bất thường; lịch sử 30 ngày.
- NPC bán thuốc/công cụ/công thức khởi đầu; shop mùa bán mỹ phẩm.
- Vé quay chỉ kiếm trong game; quà là mỹ phẩm/vật liệu phổ thông/token; công bố xác suất và đổi chắc chắn sau 20 lượt. Không bán vé tiền thật, không quay trang bị chiến đấu.

## 8. UI và phong cách hình ảnh pixel art

### 8.1 Mỹ thuật

Toàn bộ game art dùng pixel art nguyên bản: nhân vật, quái, nền, tilemap, portrait, icon, UI, thời tiết và VFX. Tuân thủ `Pixel_Art_Production_Standard_vi.md`: logical canvas 640×360, 20 PPU, lưới render 0,05 WU, pixel camera snap, scale nguyên, point filter, no mipmap và texture lossless. Game nhìn ngang; nhân vật/quái/VFX dùng sprite sheet vẽ từng frame, không dùng bone deformation để làm cong pixel. Tách hoặc vẽ variant đầu/tóc/thân/chân/vũ khí/áo choàng để ghép trang bị nhưng mọi layer phải cùng grid/pivot. Môi trường 3–5 lớp parallax lượng tử hóa theo pixel; tiền cảnh không che tương tác, actor hay telegraph.

Chuẩn tham chiếu: logical 640×360; 20 PPU và camera 32×18 WU; hero 5 WU tương ứng khoảng 100 source px/300 output px ở 1080p. Dùng integer scale (720p=2×, 1080p=3×, 1440p=4×); tỉ lệ lẻ letterbox/pillarbox, không kéo phân số. Actor atlas đóng trang 512²–1024², boss/environment 1024²–2048²/page theo chuẩn pixel-art; icon 32²–64². Mục tiêu 60 FPS PC/máy cao; 30 FPS ổn định trên máy thấp; LowFX giảm hạt/rung/layer weather nhưng giữ telegraph và silhouette.

### 8.2 UI và điều khiển

- Mobile: joystick trái; đánh/né/kỹ năng phải; chạm chọn mục tiêu; chat thu gọn; safe area cho camera notch.
- PC: WASD, Space né/nhảy theo cấu hình, chuột khóa mục tiêu, J đánh thường, Q/E/R/F kỹ năng, 1–2 thuốc, Tab đổi mục tiêu; remap được.
- HUD: HP/MP/Thanh Mạch, cấp, quest, minimap, nhóm/bang, hồi chiêu; không che báo đòn boss.
- Màn riêng: tạo nhân vật, túi, đồ, kỹ năng, quest, bản đồ, nhóm, bang, chợ, chế tạo, thú, nông trại, thư, cài đặt, báo cáo.
- Cỡ chữ điều chỉnh, phụ đề đầy đủ, icon có nhãn; không chỉ dùng màu để báo trạng thái.

### 8.3 Engine hình ảnh đề xuất

Khởi đầu bằng **Unity 6.3 LTS + C#**, URP 2D, Pixel Perfect Camera và Tilemap. Sprite import: PPU=20, Filter=Point, Compression=None, Mip Maps=Off; Animator điều khiển frame sprite, không bone-warp. Phiên bản engine được khóa theo DEC-001; thay package/render preset qua change review. Khóa phiên bản editor/package trước khi tạo project; không tự nâng giữa sprint.

## 9. Kiến trúc online

### 9.1 Thành phần

- **Client Unity:** render, điều khiển, UI, dự đoán chuyển động nhẹ/interpolation, tải cấu hình; không quyết định sát thương, loot, tiền.
- **Gateway/API:** đăng nhập, nhân vật, phiên, định tuyến tới máy chủ vùng.
- **Máy chủ vùng:** bản đồ/instance, vị trí, va chạm, quái, quest, chiến đấu, loot, chat khu vực.
- **Dịch vụ tài khoản/nhân vật:** xác thực, khóa nhân vật, lưu trạng thái/khôi phục phiên.
- **Dịch vụ kinh tế:** túi/kho, giao dịch/chợ/thư ký quỹ, sổ cái.
- **Lưu trữ:** PostgreSQL dữ liệu bền vững; Redis hoặc cache tương đương cho phiên/tìm nhóm/bảng tạm. Nội dung là dữ liệu versioned, không hard-code client.
- Bản đầu dùng modular monolith + tiến trình zone riêng; chỉ tách dịch vụ khi số liệu tải chứng minh cần. API có version.

### 9.2 Đồng bộ/chống gian lận

- Máy chủ vùng mục tiêu 20 tick/giây; trạng thái gửi 5–10 lần/giây; client nội suy người khác, dự đoán input của mình và hòa giải khi server sửa vị trí.
- Server kiểm tốc độ, va chạm, hồi chiêu, MP, tầm đánh, line-of-sight, mục tiêu, sát thương, rơi đồ và nhặt.
- Client gửi useSkill(skillId, targetId, aim, clientSequence), không gửi sát thương cuối.
- Lệnh kinh tế có idempotency key; giao dịch/chợ ghi ledger bất biến.
- Session reconnect grace 120 giây; giữ slot encounter theo timeout 120 giây nếu phase chưa đóng. Giải đấu Long Môn có một lần reconnect 90 giây theo luật trận riêng.
- Log lỗi, giao dịch, cường hóa/chợ; không log mật khẩu/token thô.

### 9.3 API tối thiểu

auth.login; character.create/select; zone.enter/leave; player.move; combat.basicAttack/useSkill; inventory.equip/use/salvage; quest.accept/progress/turnIn; party.invite/leave; guild.create/contribute; chat.send; trade.offer/confirm/cancel; market.list/search/buy/settle; craft.preview/commit. Mỗi lệnh có mã lỗi ổn định, xác nhận, timeout, quyền, rate-limit và schema version. Chốt hợp đồng trước khi client/server làm song song.

## 10. Dữ liệu nội dung

Mọi nội dung có ID cố định, version, text localization và schema validation; tách definition khỏi trạng thái người chơi:

- ClassDefinition: môn phái/vũ khí/chỉ số/kỹ năng/sprite-set và animation-set refs.
- SkillDefinition: cấp mở/bậc/chi phí/hồi chiêu/phạm vi/hiệu ứng/hệ số PvE-PvP.
- ItemDefinition: slot/lớp/cấp/hệ/phẩm chất/chỉ số/lỗ/khóa/biểu tượng.
- MonsterDefinition: cấp/HP/giáp/hành vi/báo đòn/kháng/loot.
- MapDefinition: collider/spawn/NPC/node/vùng an toàn/sức chứa.
- QuestDefinition: điều kiện/bước/thoại/mục tiêu/thưởng/reset.
- LootTable, RecipeDefinition, EventSchedule, DialogueGraph, LocalizationText.

Không dùng tên hiển thị làm ID; không đổi ID đã phát hành. Số liệu chỉnh server-side, trừ khi đổi asset/UI.

## 11. Phạm vi bản đầu

### Bắt buộc phát hành

- 5 môn phái; cấp 1–100; 6 chương; 7 vùng chiến đấu + Thanh Lạc nhập môn + thủ phủ Thăng Long Thành.
- Tối thiểu 30 quest chính, 40 quest phụ, 3 tuyến quest bang/môn phái.
- Mỗi lớp 6 kỹ năng chủ động + 8 node nội tại; tối đa 2 passive đang trang bị; 2 bộ kỹ năng.
- 4 dungeon 5 người, 2 raid 10 người × 3 encounter, 6 boss thế giới và 1 raid boss cuối, Tháp Lạc Ấn 30 tầng.
- PvP gồm duel 1v1, arena 3v3, Trấn Sơn battleground 10v10 và công thành bang hội 20v20.
- 12 slot đồ, 4 slot thú, túi/kho, cường hóa, khảm, chế tạo, phân giải, sửa, chợ/giao dịch.
- Nhóm/bạn bè/chat/bang/quest bang/công thành 20v20/đấu tay đôi/đấu trường.
- Thú/cưỡi, 3 nghề, nông trại 6 luống, mini game, auto PvE giới hạn.
- Mạch Triều và lịch vận hành có thể cấu hình.

### Chưa làm bản nền

Chiến trường hàng trăm người, nhà tùy biến tự do, thú lai giống, đấu liên server, auction xuyên server, giao dịch tiền thật. Chỉ xem xét sau khi ổn định và có dữ liệu người chơi.

## 12. Tiêu chí hoàn thành

- **Di chuyển/bản đồ:** không xuyên collider; chuyển động người khác mượt; chỉ dịch chuyển tới điểm đã mở.
- **Chiến đấu:** kỹ năng có mô tả/tầm/hồi chiêu; server quyết định trúng; boss có báo trước và cách phản ứng.
- **Trang bị:** mặc/tháo/so sánh/khóa/ngọc/sửa đúng sau reconnect.
- **Quest:** tiến độ không mất khi đổi vùng/reconnect; thưởng chỉ cấp đúng theo reset.
- **Chợ/giao dịch:** không nhân đôi vật phẩm/tiền khi timeout/hủy/thao tác đồng thời.
- **Nhóm/bang:** quyền kiểm tra ở server; thay chủ/rời bang có log; chống nhân thưởng bằng tài khoản phụ.
- **Mỹ thuật:** asset có nguồn, kích thước pixel, cell/frame table, pivot, PPU, palette, atlas, import preset và provenance; phải theo pixel-art grid, point filtering và scale nguyên.
- **Mobile/PC:** UI đúng tỷ lệ, remap điều khiển, tùy chọn hiệu ứng vẫn giữ tín hiệu báo đòn.

## 13. Nguyên tắc thực hiện

1. GDD là quyết định thiết kế gốc; nếu code và tài liệu mâu thuẫn, mở quyết định thay vì âm thầm đổi luật.
2. Không sao chép nguyên văn nội dung/hình/nhạc/logo/server endpoint/dữ liệu độc quyền từ JAR. Dùng cấu trúc gameplay đã phân tích và nội dung dự án tự tạo/có quyền sử dụng.
3. Tất cả kinh tế/tiến trình có kiểm tra server; client chỉ là giao diện.
4. Làm prototype trước: một vùng, một lớp, một quest, một boss, túi và một món đồ nâng cấp được.
5. Sau prototype mới mở rộng đủ năm lớp; mỗi feature cần schema và tiêu chí hoàn thành trước khi sản xuất hàng loạt.
