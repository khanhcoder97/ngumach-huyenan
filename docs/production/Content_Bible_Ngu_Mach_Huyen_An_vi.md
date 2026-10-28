# Ngũ Mạch: Huyền Ấn — Content Bible v1

Tài liệu bổ sung các nội dung và thông số đủ cụ thể để đưa vào data sau khi GDD được chốt. Tên/thoại/kỹ năng/vật phẩm bên dưới là thiết kế mới, không trích từ máy chủ KPAH. Số liệu chiến đấu là cấu hình khởi điểm, phải chỉnh được server-side.

## 1. Cinematic mở đầu và giọng kể

Mưa trút xuống Bến Mưa. Người chơi gặp Ly An đang giữ một kiện hàng bên bến, giúp cô rồi mới nhận phong thư còn niêm sáp. Tiếng chuông chỉ trọn khi nhìn xuống nước; không có cảnh giết boss hay nhận mảnh ấn trước khi vào gameplay. Niêm thư rạn dần trong P00-04; sau encounter Mãng Cốt và tương tác nguồn ở P00-05, mảnh Huyền Ấn mới phản ứng. Tạ Vân Khanh nhận ra dấu hiệu nhưng chưa kể lịch sử. Storyboard/prompt mở đầu xem CIN_001 trong Cinema_Muse_Directors_Pack_vi.md; tuyến truyện sâu theo Narrative_Depth_and_Discovery_vi.md.

Lời thoại ngắn, chia đoạn dưới 12 dòng trên mobile. NPC không giải thích toàn bộ lịch sử cùng lúc; người chơi ghép manh mối từ thư, vật chứng và lời khai. Mỗi lựa chọn thoại chỉ thay lời thoại, danh vọng hoặc mỹ phẩm; kết thúc chiến dịch là chung cho mọi người.

## 2. Nhiệm vụ cốt truyện chi tiết

Mỗi quest có ID cố định, bước, mục tiêu, vùng/NPC, điều kiện mở, reset, rewardID và cờ lưu. Server ghi tiến độ/thưởng. Quest chính thường thưởng 20–25% EXP cần cho cấp hiện tại; boss chương 50–60%; quest phụ khoảng 12%. Quái/vùng bổ sung phần EXP còn lại. Không cấp thưởng từ client.

### Mở đầu — Bến Mưa (cấp 1–10)

| ID / tên | Mục tiêu | Câu chuyện / mở khóa |
|---|---|---|
| P00-01 Thư qua bến | Nói Ly An, nhặt 3 kiện, giao Tạ Vân Khanh | Dạy di chuyển/tương tác; áo Thường |
| P00-02 Chuông không người | Tìm 3 dấu nước, hạ 4 cá linh | Dạy khóa mục tiêu/đánh thường; mở minimap |
| P00-03 Dưới mặt đầm | Phá 3 ổ rễ, cứu dân mắc kẹt | Dạy né vùng đánh; Ly An thấy dấu niêm sáp |
| P00-04 Người giữ bờ | Hộ tống Ly An qua 2 điểm, bảo vệ khỏi 2 đợt quái | Dạy party nhỏ/đòn xa; thuốc và giày |
| P00-05 Mảnh ấn đầu tiên | Hạ Mãng Cốt, tương tác mảnh ấn, chọn môn phái | Boss hướng dẫn; vũ khí lớp cấp 1; mở Thanh Lạc |

### Chương I — Năm lời thề (cấp 11–20)

| ID / tên | Mục tiêu | Câu chuyện / mở khóa |
|---|---|---|
| C1-01 Cổng Thanh Lạc | Tới thành, gặp 3 đại diện, đăng ký lễ thử | Mở thành, dịch chuyển và bản đồ |
| C1-02 Bài thử môn phái | Hoàn thành 3 bước thử riêng cho lớp | Mở kỹ năng thứ hai; huy hiệu lớp |
| C1-03 Phù tín giả | Soi 4 phù tín, truy dấu kẻ giả qua 2 phố | Dạy quest điều tra; mở danh vọng |
| C1-04 Tượng mở mắt | Hạ 6 tượng nhỏ, phá 2 nguồn điều khiển | Dạy cảnh báo diện rộng; rương chọn áo/quần |
| C1-05 Năm lời thề | Nói với 5 đại diện, hạ Tượng Hành Hỏa | Hạ Mặc thấy dữ liệu tháp bị xóa; mở Thăng Long Thành và C1-06 |
| C1-06 Con dấu qua phố | Đối chiếu hóa đơn Đại Chợ, dấu lò và trang Lưu trữ tại Thăng Long Thành | Bản lệnh giả đi qua tuyến thương mại; resin trên giấy chỉ về Lâm Triều; mở C2-01 và route Lâm Triều |

### Chương II — Rừng nhớ tên người (cấp 21–35)

| ID / tên | Mục tiêu | Câu chuyện / mở khóa |
|---|---|---|
| C2-01 Đội đốn cây mất tích | Tìm 3 dấu chân và 2 đồ nghề | Quái đang giữ ký ức chứ không săn người |
| C2-02 Tên trên vỏ cây | Tìm 4 cái tên; chọn thoại theo manh mối | Công thức thuốc giải |
| C2-03 Đường nước khóa | Mở 3 van, bảo vệ thợ sửa qua 2 đợt | Dạy phối hợp tank/hỗ trợ |
| C2-04 Ký ức người lạ | Hạ Rễ Mộng, xem ký ức Tạ Vân Khanh | Ông từng ký văn bản phong tỏa tháp |
| C2-05 Mạch suối trở lại | Hạ Cổ Thụ Trăm Mắt, phá rễ theo đèn báo | Mở chế tác/ngọc; nhật ký có dấu Cơ Vô Tướng |

### Chương III — Lò không tắt (cấp 36–50)

| ID / tên | Mục tiêu | Câu chuyện / mở khóa |
|---|---|---|
| C3-01 Đoàn xe cạn nước | Tìm 3 bồn, chọn đường nhanh nguy hiểm hoặc đường dài | Tuyến đổi số đợt quái/vật liệu, không đổi kết thúc |
| C3-02 Tro trong phổi | Thu 5 mặt nạ, cứu 4 thợ, tránh khí độc | Dạy độc và thuốc giải |
| C3-03 Bản khắc dưới lò | Hạ tinh anh, ghép 3 mảnh bản khắc | Thí nghiệm hợp mạch liên quan nạn đói cũ |
| C3-04 Ba van lửa | Nhóm tắt 3 van, mỗi van phải giữ vị trí qua đợt quái | Dạy cơ chế dungeon |
| C3-05 Lò Trời | Boss 3 pha, tắt từng van theo biểu tượng | Chọn công bố nhật ký hay giao hội đồng; mở Chương IV |

### Chương IV — Thành không có chủ (cấp 51–65)

| ID / tên | Mục tiêu | Câu chuyện / mở khóa |
|---|---|---|
| C4-01 Dân qua cổng | Hộ tống 3 nhóm dân tới vùng an toàn | Mở điểm hồi sinh Trấn Sơn |
| C4-02 Mệnh lệnh không dấu | So 3 lệnh, hỏi 2 sứ giả, lấy dấu sáp thật | Lộ dấu hiệu giả lệnh của Tống Bành |
| C4-03 Ba cổng thành | Party 5 người giữ 3 cổng trong 4 phút | Dạy điều phối vai trò; phù sửa đồ |
| C4-04 Cờ trên tường | Chiếm trạm tiếp tế rồi mở cổng trong công thành truyện | Dạy mục tiêu chiến trường; bản đồ năm tháp |
| C4-05 Thiết Giáp Tướng | Đánh Tống Bành, kích hoạt 2 bẫy để phá giáp | Tống Bành thú nhận; mở nhiệm vụ bang |

### Chương V — Thành phố dưới Bạch Uyên (cấp 66–80)

| ID / tên | Mục tiêu | Câu chuyện / mở khóa |
|---|---|---|
| C5-01 Đài Lặn | Tìm 3 thợ lặn, lấy bình khí, vào phế tích | Mở vùng nước sâu |
| C5-02 Ba buồng áp suất | Bật 3 trạm theo thứ tự đèn, sống sót qua triều | Puzzle có chỉ dẫn; không pixel-hunt |
| C5-03 Người viết nhật ký | Ghép 4 trang, hỏi Hạ Mặc về tên bị xóa | Xác nhận thí nghiệm có người sống sót |
| C5-04 Lời khai năm môn phái | Đưa bằng chứng tới 5 trưởng phái | Danh vọng/thoại đổi; mở raid |
| C5-05 Mẫu Xà Thủy | Boss theo thủy triều; trú vùng sáng khi triều rút | Nhận lõi Thủy và kế hoạch mở Vực |

### Chương VI — Nghịch Mạch (cấp 81–100)

| ID / tên | Mục tiêu | Câu chuyện / mở khóa |
|---|---|---|
| C6-01 Năm đội, năm tháp | Cùng server chia đóng góp vào 5 tháp | Người khác instance vẫn đóng góp cùng tiến độ thế giới |
| C6-02 Cửa mạch mở | Hạ 3 đợt, giữ 2/3 cột sáng | Mở điểm dịch chuyển cuối |
| C6-03 Lõi môn phái | Hoàn thành nhiệm vụ riêng để lấy mảnh lõi | Mỹ phẩm vũ khí, không tăng chỉ số |
| C6-04 Người muốn cứu thế giới | Đánh Cơ Vô Tướng pha 1, xem ký ức quê nhà | Động cơ được hiểu nhưng không xóa hậu quả |
| C6-05 Huyền Ấn mới | Raid 10 người giữ 5 trụ, xử lý quái, đánh boss | Kết thúc chung; cấp 100; mở Mạch Triều |

Cờ chính duy nhất là MAIN_CAMPAIGN_COMPLETE. Cờ phụ: ThanhLacTrust, MocVanTrust, SaHoaTrust, TranSonTrust, BachUyenTrust. Chúng mở thoại/quest/mỹ phẩm phụ, không tạo nhánh máy chủ.

## 3. Kỹ năng khởi điểm

### Quy tắc dùng chung

Đánh thường không chiếm ô kỹ năng. Mỗi lớp có 6 kỹ năng trang bị: 4 kỹ năng thường, 1 kỹ năng cơ động, 1 tuyệt kỹ; cộng 8 node nội tại (hai nhánh × bốn node, mở ở cấp 20/40/60/80); người chơi chỉ equip tối đa 2 node cùng lúc. Bốn mươi node có ID và số liệu trong `Class_Passive_Production_Data_vi.csv`. Né chung hồi chiêu 7 giây, tầm 5.5m, tránh sát thương 0.18 giây; không né mọi chiêu khóa vùng.

Hồi chiêu bắt đầu khi server xử lý lệnh. Sát thương là hệ số của sát thương vũ khí, cấp 1. Ô mở ở cấp 1/4/8/12/16/30. Bậc kỹ năng tối đa +8% sát thương hoặc giảm 4% cost; PvP có hệ số riêng. Boss tích choáng mạch thay vì bị khóa dài.

### Minh Kiếm — Kiếm Ý 0–5

Đánh thường hoàn tất chuỗi 3 nhát cho +1 Kiếm Ý; đỡ hoàn hảo cho +2. Ultimate tiêu Kiếm Ý.

| Kỹ năng | CD / MP | Hiệu lực cấp 1 |
|---|---|---|
| Phản Quang | 10s / 12 | Giảm 70% sát thương 0.4s; đỡ trúng phản kích 180% và +2 Kiếm Ý; hụt chỉ giảm 20% |
| Tầm Long | 8s / 16 | Lao 5.5m, gây 150% lên mục tiêu đầu; không xuyên vật cản; +1 Kiếm Ý |
| Kiếm Trận | 10s / 22 | Quạt 100°, tổng 190%, tối đa 5 mục tiêu |
| Thiết Y | 16s / 24 | Khiên 12% HP tối đa trong 4s, không cộng dồn |
| Bạch Hồng (cơ động) | 9s / 10 | Lướt ngang 6m, xóa chậm; không gây sát thương |
| Vạn Tượng Quy Nhất (tuyệt kỹ) | 60s / 40 | Đường kiếm 7m: 260% + 60% mỗi Kiếm Ý, tối đa 5 |

Nội tại riêng: Tâm Tĩnh (đỡ chuẩn giảm 1s Tầm Long CD); Kiếm Khí (mục tiêu chịu thêm 3% từ lớp này trong 4s); Thủ Nhất (Thiết Y thêm 4% khiên). Năm node còn lại tăng công/thủ/MP nhẹ.

### Ảnh Đao — Nhiệt 0–5

Đòn trúng cho +1 Nhiệt tối đa mỗi 1.5s; né thành công +1.

| Kỹ năng | CD / MP | Hiệu lực cấp 1 |
|---|---|---|
| Huyết Nguyệt | 8s / 14 | 140%, chảy máu 3 lần × 25% trong 4s |
| Tàn Hỏa | 12s / 18 | Dấu 5s; đòn sau nổ 120% vùng nhỏ; đủ 5 Nhiệt thì 180% |
| Xích Ảnh | 10s / 20 | Hai nhát × 85%; nhát sau mạnh hơn khi đánh sau lưng quái |
| Tước Mạch | 14s / 22 | 160%, chậm 25% trong 2.5s; boss chỉ tích choáng mạch |
| Ảnh Bộ (cơ động) | 8s / 10 | Lướt 6m, xóa khóa quái thường; không tàng hình |
| Tử Diệm (tuyệt kỹ) | 60s / 35 | 230% vùng nhỏ +45% mỗi Nhiệt, tiêu sạch Nhiệt |

Nội tại: Hỏa Tức (chảy máu tăng theo Nhiệt); Bóng Sát (sau lưng quái +8%); Thu Liễm (hạ quái giảm 1s Ảnh Bộ, tối đa 1/5s); 5 node tăng chí mạng/kháng/MP nhẹ.

### Huyền Bút — Thủy Ấn 0–5

Mỗi chuỗi 3 đòn thường tạo 1 Thủy Ấn; kỹ năng hồi phục tiêu 2 ấn để tăng hồi.

| Kỹ năng | CD / MP | Hiệu lực cấp 1 |
|---|---|---|
| Mực Triều | 6s / 12 | Sóng thẳng 5m gây 130%, xuyên tối đa 3 quái thường |
| Hàn Châm | 12s / 18 | 110%, chậm 35% trong 2s; quái nhỏ đóng băng 0.6s |
| Thủy Kính | 16s / 22 | Khiên 10% HP cho đồng đội 4s; chỉ giữ khiên lớn nhất |
| Mưa Tinh | 18s / 28 | Bán kính 3m hồi 8% HP +2%/s trong 3s; tiêu 2 ấn tăng tổng hồi 30% |
| Lưu Thủy Bộ (cơ động) | 10s / 10 | Lùi 4m, +20% tốc chạy 1.5s |
| Long Mạch Hồi Nguyên (tuyệt kỹ) | 70s / 45 | Hồi 12% HP nhóm, giải một chậm/độc; không vượt giới hạn raid |

Nội tại: Nét Mực (Mực Triều giảm 1s sau 3 lần trúng); Tĩnh Thủy (Thủy Kính thêm khiên khi mục tiêu thấp HP); Chia Dòng (Mưa Tinh tối đa 5 người); 5 node tăng MP/hồi/kháng nhẹ.

### Thạch Chùy — Thế 0–5

Đánh thường trúng hoặc chặn sát thương cho +1 Thế, tối đa một lần mỗi 2s.

| Kỹ năng | CD / MP | Hiệu lực cấp 1 |
|---|---|---|
| Trấn Sơn | 8s / 14 | 170%, giảm tốc chạy 20% trong 2s |
| Chấn Địa | 14s / 20 | Vòng 3m gây 120%; quái thường hất 0.5s |
| Thiết Bích | 18s / 24 | Giảm 25% sát thương nhận 4s; tiêu 2 Thế tăng lên 35% |
| Khiêu Chiến | 20s / 16 | Quái thường tập trung vào mình 4s; boss không bị ép đổi mục tiêu |
| Phá Nham (cơ động) | 10s / 12 | Lao 4m, gây 100%, ngắt hoạt ảnh quái thường |
| Sơn Thần Giáng Thế (tuyệt kỹ) | 70s / 40 | Vùng chắn 4m trong 5s, gây 180%; tiêu Thế thêm tối đa 2s |

Nội tại: Cốt Thạch (+3% Thể chất); Giữ Trận (đỡ chuẩn giảm 1s Thiết Bích, tối đa 1/5s); Dội Chấn (đánh trúng 3+ mục tiêu hồi 4 MP); 5 node tăng HP/giáp/kháng nhẹ.

### Linh Cung — Mộc Tiêu 0–5

Đánh thường bắn 3 tên; trúng cùng mục tiêu tích 1 Mộc Tiêu mỗi 2s, đổi mục tiêu đặt lại chuỗi.

| Kỹ năng | CD / MP | Hiệu lực cấp 1 |
|---|---|---|
| Khóa Mạch | 10s / 16 | 130%, dấu 5s khiến nhóm gây thêm 3%; không cộng dồn |
| Dây Gai | 14s / 18 | Bẫy bán kính 2m gây 90%, chậm quái 40% trong 2.5s |
| Liên Châu | 8s / 18 | 5 tên ×45%, tối đa 3 tên trên một mục tiêu |
| Tán Hoa | 12s / 20 | Hình nón 100°, tổng 150%; giảm 30% nếu quá gần |
| Phi Diệp (cơ động) | 9s / 12 | Lùi 5m và bắn 80%, giữ khoảng cách |
| Bách Tiễn Quy Tông (tuyệt kỹ) | 65s / 40 | Báo vùng 1.2s, mưa tên 6m tổng 300%; tiêu 3 Mộc Tiêu tăng 20% |

Nội tại: Mắt Rừng (+4% chính xác); Ghim Dấu (Khóa Mạch +1s); Cung Nhẹ (giảm MP Liên Châu theo chuỗi); 5 node tăng tốc/crit/kháng nhẹ.

## 4. Mẫu vật phẩm và công thức

ID là ví dụ; server tạo vật phẩm bằng ID + thuộc tính hợp lệ, không dùng tên hiển thị làm khóa.

### Vũ khí khởi đầu cấp 1

| ID | Tên | Lớp | Công | Dòng phụ |
|---|---|---|---:|---|
| EQ-MK-WEAPON-T1-R-COMMON | Thường Kiếm Mưa Khởi Minh Kiếm | Minh Kiếm | 12 | +2 Sức mạnh |
| EQ-AD-WEAPON-T1-R-COMMON | Thường Đao Mưa Khởi Ảnh Đao | Ảnh Đao | 12 | +2 Nhanh nhẹn |
| EQ-HB-WEAPON-T1-R-COMMON | Thường Bút Mưa Khởi Huyền Bút | Huyền Bút | 12 phép | +2 Linh lực |
| EQ-TC-WEAPON-T1-R-COMMON | Thường Chùy Mưa Khởi Thạch Chùy | Thạch Chùy | 12 | +2 Thể chất |
| EQ-LC-WEAPON-T1-R-COMMON | Thường Cung Mưa Khởi Linh Cung | Linh Cung | 12 | +2 Nhanh nhẹn |

Công nền mẫu: cấp 10: 35–40; cấp 20: 80–90; cấp 50: 320–360; cấp 100: 1,000–1,100. Cùng cấp/phẩm chất, chênh lớp tối đa 5%; lưu data để chỉnh được.

### Ngọc/nguyên liệu

| ID mẫu | Tác dụng/nguồn |
|---|---|
| GEM-KIM-01 | +1% chính xác; quặng vùng Kim/boss |
| GEM-MOC-01 | +1% né; rừng Lâm Triều |
| GEM-THUY-01 | +1% MP tối đa; Bạch Uyên |
| GEM-HOA-01 | +1% chí mạng; Sa Hỏa |
| GEM-THO-01 | +1% giáp; Trấn Sơn |
| MAT-ORE-01 | quặng thô; khai khoáng |
| MAT-WOOD-01 | gỗ linh; đốn gỗ |
| MAT-HERB-01 | dược thảo; hái thuốc |
| MAT-SOUL-01 | linh phách; tinh anh/boss |
| MAT-CORE-01 | lõi mạch; boss chương, khóa giao dịch |
| MAT-SEAL-01 | Mảnh Huyền Ấn; nhiệm vụ/node; tiêu hao khi đúc lại một affix |
| MAT-GUARD-01 | Phù Bảo Hộ; thử thách tuần/đổi thưởng bang/tinh anh Sa Hỏa; dùng cho +11..+15 |
| MAT-RELIC-01 | Cổ Linh Phách; tạo từ RCP-SOUL-01, giới hạn tuần; dùng cho Ấn Hộ Mệnh T5 |

### Tiêu hao

| ID | Vật phẩm | Hiệu lực và giới hạn |
|---|---|---|
| POT-HP-01 | Dược Bến Mưa | hồi 25% HP; hồi dùng chung 8s |
| POT-MP-01 | Nước Tĩnh | hồi 20% MP; hồi dùng chung 8s |
| POT-CLEAN-01 | Trà Thanh Tâm | xóa một độc/chậm, không xóa raid stun |
| KIT-REPAIR-01 | Bộ Vá Giáp | sửa 25 độ bền; dùng ngoài combat |
| SCROLL-WAY-01 | Phù Về Thành | về hub đã mở; niệm 10s, bị ngắt khi bị đánh |
| FOOD-ATK-01 | Bánh Mạch Hỏa | +2% sát thương PvE 20 phút; không hiệu lực PvP |
| FOOD-DEF-01 | Canh Rễ Đá | +2% giáp PvE 20 phút; không cộng dồn món cùng nhóm |
| PET-FEED-01 | Hạt Linh Thú | XP thú, không tăng cấp nhân vật |
| TICKET-TIDE-01 | Vé Mạch Triều | một lượt Mạch Triều; không bán tiền thật, không dùng vào boss |
| TICKET-BOSS-01 | Lệnh Truy Mạch | vé khóa tài khoản, stack tối đa 3; cấp 81+ dùng cho một lượt Thí Luyện Hồi Ức/người, nhận tối đa 3/tài khoản/tuần từ nhiệm vụ Bảng Truy Nã đầu tiên mỗi ngày tại Thanh Lạc hoặc Thăng Long Thành; không bỏ qua quota loot thường |
| MAT-LOCK-01 | Phù Khóa | khóa món trước thao tác phân giải, dùng một lần |

### Công thức chế tạo

| Công thức | Đầu vào | Đầu ra/điều kiện |
|---|---|---|
| RCP-POTION-01 | 3 dược thảo + 1 nước sạch | 2 Dược Bến Mưa; nghề cấp 1 |
| RCP-GEM-02 | 3 ngọc cùng mạch/cùng cấp L1–L4 + 5 MAT-ORE-01 | 1 ngọc cùng mạch cấp tiếp theo; chắc chắn, L5 là trần |
| RCP-ARMOR-10 | 8 quặng + 4 gỗ + 1 linh phách | áo cấp 10 Thường/Tinh; chọn lớp |
| RCP-REPAIR-01 | 2 quặng + 1 gỗ | 1 Bộ Vá Giáp |
| RCP-SOUL-01 | 5 MAT-SOUL-02 + 1 MAT-CORE-01 | 1 MAT-RELIC-01 Cổ Linh Phách; giới hạn tuần 3 lần/nhân vật |
| RCP-CLOAK-31 | 5 MAT-WOOD-02 + 3 MAT-LEATHER-01 + 1 MAT-SOUL-01 | Phi Phong Rễ Nhớ T3 phẩm chất Thường theo lớp; nghề Chế tác bậc 3 |
| RCP-SEAL-61 | 6 MAT-ORE-05 + 3 MAT-CLOTH-01 + 2 MAT-RELIC-01 + 1 MAT-CORE-01 | Ấn Hộ Mệnh T5 phẩm chất Tinh theo lớp; cấp 61, nghề Chế tác bậc 5 |

## 5. Thú đồng hành và hoạt động

| ID / thú | Vai trò | Kỹ năng |
|---|---|---|
| PET-01 Cáo Tro | hỗ trợ công | đánh dấu quái thường; nhóm +2% sát thương 4s |
| PET-02 Rùa Rêu | phòng thủ | khiên 5% HP chủ mỗi 30s |
| PET-03 Chim Sương | thu thập | nhặt nguyên liệu thường trong bán kính |
| PET-04 Mèo Mưa | hồi phục | hồi 2% HP nếu chủ không nhận sát thương 5s |
| PET-05 Thằn Lằn Đá | khống chế | chậm quái thường 15%/2s, không tác dụng boss |

Reset hoạt động: daily lúc 05:00, weekly thứ Hai lúc 05:00 theo Asia/Ho_Chi_Minh (DEC-005). Scheduler lưu UTC và kèm timezone; UI hiện giờ region của ledger. Không dùng “giờ server” nếu không định nghĩa timezone.

| Hoạt động | Lượt thưởng lớn | Thưởng | Nhóm |
|---|---:|---|---|
| Bảng truy nã | 3/ngày, đổi 1 | Đồng/EXP/vật liệu | solo/party |
| Dungeon | 3/ngày | rương đồ/vật liệu | 5 |
| Boss vùng | 1 rương/ngày/vùng | vật liệu/cosmetic token | công khai |
| Mini game | 3/ngày | token/mỹ phẩm nhỏ | solo |
| Quest bang | 5 mục tiêu/tuần | XP bang/quỹ/trang trí | bang |
| Công thành | 1 trận/tuần | cờ/danh hiệu | 20v20 |
| Tháp thử thách | phần thưởng tầng/tuần | token/bảng mùa | 1–5 |
| Raid | 2 raid/tuần | cổ vật/vật liệu cuối game | 10 |

Bỏ lỡ tuần không khóa cốt truyện hay đồ cơ bản.

## 6. Trạng thái hiệu ứng

| Hiệu ứng | Quy tắc |
|---|---|
| Chảy máu | sát thương theo thời gian, tối đa 3 stack; boss nhận 50% thời lượng; PvP 2 stack |
| Độc | sát thương nhỏ + giảm hồi phục 10%; boss không giảm hồi phục |
| Chậm | giảm tốc; boss chỉ 10%, PvP tối đa 25% |
| Đóng băng | quái nhỏ tối đa 0.6s; boss chỉ tăng thanh choáng mạch |
| Choáng mạch | đủ thanh thì ngắt chiêu boss 1.2s; hồi thanh sau 5s |
| Khiên | hấp thụ trước HP; không cộng dồn, lấy khiên lớn nhất |
| Đánh dấu | tăng sát thương/định vị; một dấu mỗi nguồn |
| Thiêu đốt | sát thương Hỏa theo thời gian; PvP tối đa 2 stack |

Mỗi effect có source, thời điểm, stack limit, luật refresh/replace, icon/text và kháng. Server gửi trạng thái, client phát hình ảnh.

## 7. Ví dụ schema và UI transaction

- Quest: ID C2-03; cấp tối thiểu 25; không lặp; bước mở van A, mở van B, hộ tống thợ 90 giây; checkpoint tại từng van, resume từ van gần nhất; thưởng 24% EXP level hiện tại + công thức thuốc.
- Item: ID EQ-MK-WEAPON-T1-R-COMMON; slot vũ khí; class Minh Kiếm; hệ Kim; Thường; cấp 1; không giao dịch; độ bền 100; +2 Sức mạnh.
- Skill: ID MK-ULT-01; mở cấp 30; hồi 60s; tốn 40 MP; mục tiêu dạng đường; hệ số 2.6; tiêu 0–5 Kiếm Ý.
- Loot boss: đảm bảo vật liệu cá nhân + một lượt từ pool đồ; cosmetic roll riêng; server ghi seed/kết quả.

Các UI state bắt buộc:
1. Túi → chọn → so sánh → mặc → server xác nhận → cập nhật stat.
2. NPC shop → chọn → xem giá/túi → xác nhận → trừ tiền và cấp đồ trong một transaction.
3. Cường hóa → chọn đồ/nguyên liệu → preview cấp/tỷ lệ/giá → xác nhận → server commit → animation.
4. Quest → bước cập nhật → đổi vùng/reconnect → turn-in → thưởng đúng một lần.
5. Trade → offer → lock → hai confirm → server kiểm tra quyền/số dư → commit nguyên tử hoặc rollback.
6. Chợ → ký quỹ listing → mua → settle → khi hết hạn/hủy hoàn item/tiền cùng số lượng.

Mỗi thao tác có loading, timeout, lỗi thử lại được, lỗi cần người chơi xử lý; bấm lặp không nhân item/tiền.
