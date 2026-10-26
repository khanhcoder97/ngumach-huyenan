# Ngũ Mạch: Huyền Ấn — kịch bản nhiệm vụ và truyện v1

Tài liệu sản xuất cho narrative, quest scripting, localization và quest UI. ID/trigger là chuẩn tham chiếu. Mọi nhiệm vụ chính phải hoàn tất một lần; lỗi mạng không thể làm mất bước hoặc phát thưởng hai lần. Quest phụ không chặn cốt truyện.

## 1. Quy ước triển khai nhiệm vụ

- Một quest có: ID, tên, level range, prereq, map/NPC start, tối đa 5 step, success event, fail/retry, rewardID, dialogue keys, tracking icon.
- Trong nhiệm vụ dùng token NPC_MASTER_[CLASS], server/narrative compiler thay token bằng NPC_MASTER_MINH_KIEM, NPC_MASTER_ANH_DAO, NPC_MASTER_HUYEN_BUT, NPC_MASTER_THACH_CHUY hoặc NPC_MASTER_LINH_CUNG theo nhân vật.
- Step có loại TALK, INTERACT, KILL, COLLECT, ESCORT, DEFEND, BOSS_PHASE, INSTANCE_CLEAR.
- NPC có thể đi cùng nhiều quest; mỗi quest chỉ dùng objective marker riêng để không nhân bản NPC.
- Khi chết, objective giết/nhặt được giữ; escort reset tại checkpoint; boss encounter khởi động lại từ phase 1 hoặc checkpoint được GDD định nghĩa.
- Quest reward commit bằng transaction idempotent. Quest chính không reset. Quest phụ reset chỉ khi ghi rõ.
- Người chơi không cần đọc toàn bộ thoại để hoàn thành; mọi mục tiêu chính có tracker, marker thế giới và nhật ký.

## 2. Chiến dịch chính: 36 quest

### Mở đầu — Bến Mưa (cấp 1–10)

| ID | Bắt đầu | Các bước chính | Cảnh thoại/ý nghĩa | Thất bại, thưởng, mở khóa |
|---|---|---|---|---|
| P00-01 Thư qua bến | NPC_LYAN, Bến Mưa | nhận thư; nhặt 3 kiện ở x=36/44/52; giao NPC_TA_VAN_KHANH | Ly An cấm mở thư; Tạ Vân Khanh nhận ra sáp có dấu năm vạch | kiện respawn; thưởng XP, 20 Đồng, áo Thường; mở P00-02 |
| P00-02 Chuông không người | NPC_TA_VAN_KHANH | kiểm 3 gợn nước; hạ 4 Cá Linh; quay lại báo cáo | chuông vang từ dưới hồ, không có âm thanh trên bờ | quái respawn; thưởng XP/thuốc; mở khóa minimap/target |
| P00-03 Dưới mặt đầm | NPC_LYAN | phá 3 Rễ Nước; tương tác 2 dân mắc kẹt; né một đợt sóng | một dân nói bóng dưới hồ giống nhân vật | chết hồi tại Bến Gỗ; dân được cứu giữ trạng thái; giày/thuốc; mở P00-04 |
| P00-04 Người giữ bờ | NPC_TA_VAN_KHANH | hộ tống Ly An qua checkpoint x=80 và x=120; hạ 2 đợt 3 quái | Ly An thấy phù sáp trong thư tự rạn; người chơi học đánh khi bảo vệ NPC | escort reset về checkpoint gần nhất; XP, 30 Đồng, thuốc; mở boss |
| P00-05 Mảnh ấn đầu tiên | NPC_TA_VAN_KHANH tại Đầm Chuông | vào boss ring; hạ Mãng Cốt; tương tác mảnh ấn; chọn môn phái ở NPC_CLASS_TRIAL | mảnh ấn gọi tên “Huyền Ấn”; Tạ Vân Khanh che giấu một ký ức | boss reset khi cả đội rời; vũ khí lớp EQ-[CLASS]-WEAPON-T1-R-COMMON, mở Thanh Lạc/Chương I |

### Chương I — Năm lời thề (cấp 11–20)

| ID | Bắt đầu | Các bước chính | Cảnh thoại/ý nghĩa | Thất bại, thưởng, mở khóa |
|---|---|---|---|---|
| C1-01 Cổng Thanh Lạc | NPC_LYAN ở cổng MAP_THANH_LAC | nói với 3 đại diện; đăng ký đài thử; mở bản đồ thành | Thanh Lạc bình yên nhưng năm cờ quay về năm hướng | không fail; 80 Đồng/XP; mở shop/điểm về |
| C1-02 Bài thử môn phái | NPC_MASTER_[CLASS] | hoàn thành lớp thử 3 bước: đánh bia, né đòn, dùng skill lên tinh anh | từng thầy giải thích bản sắc lớp, không giảng lore dài | có thể làm lại; skill #2, vũ khí lớp cấp 10 |
| C1-03 Phù tín giả | NPC_HA_MAC | soi 4 phù ở quảng trường; hỏi 2 nhân chứng; bắt Kẻ Giả Phù | một phù có vân khắc do máy móc, không phải dấu môn phái | mục tiêu có respawn; token Danh Vọng; mở nhiệm vụ phụ |
| C1-04 Tượng mở mắt | NPC_GUARD_CAPTAIN | hạ 6 Tượng Nhỏ; phá 2 Cọc Điều Khiển theo biểu tượng; cứu 1 hộ vệ | tượng chỉ tấn công người mang phù giả | hộ vệ hồi sau 30 giây; rương chọn áo/quần; mở boss |
| C1-05 Năm lời thề | NPC_HA_MAC | đối thoại 5 trưởng phái; hạ Tượng Hành Hỏa | các phái đồng ý đình chiến tạm, phát hiện dữ liệu tháp bị xóa | boss có reset; Huy hiệu Thanh Lạc; mở Thăng Long Thành và C1-06 |
| C1-06 Con dấu qua phố | NPC_HA_MAC tại MAP_THANG_LONG | đối chiếu hóa đơn chợ, dấu lò và trang lưu trữ; báo cáo Hạ Mặc | dấu giả được chuyển qua mạng thương mại nhưng resin trên giấy chỉ về Lâm Triều; không kết tội thương nhân hay phái nào khi chưa đủ bằng chứng | 5 bước điều tra không combat; 300 Đồng, EXP, Huy hiệu Thanh Lạc; mở C2-01 và route Lâm Triều |

### Chương II — Rừng nhớ tên người (cấp 21–35)

| ID | Bắt đầu | Các bước chính | Cảnh thoại/ý nghĩa | Thất bại, thưởng, mở khóa |
|---|---|---|---|---|
| C2-01 Đội đốn cây mất tích | NPC_FOREMAN_MOC | tìm 3 dấu chân; nhặt 2 rìu; hạ 4 Rễ Mộng | rìu không có máu, người mất tích bị cây giữ trí nhớ | rìu giữ khi chết; nguyên liệu gỗ; mở C2-02 |
| C2-02 Tên trên vỏ cây | NPC_HA_MAC | tìm 4 tên theo manh mối trên bản đồ; không đánh cây sai; trả lời Ly An | tên cuối là người đã được ghi tử trận 30 năm trước | sai lựa chọn chỉ cần tìm lại; công thức thuốc giải |
| C2-03 Đường nước khóa | NPC_WATER_KEEPER | bật van A/B/C; hộ tống Thợ Máy 90 giây; hạ 2 đợt quái | van bị đóng từ phía trong, dấu tay trùng ký hiệu tháp | checkpoint ở mỗi van; mở nghề hái thuốc/dungeon |
| C2-04 Ký ức người lạ | NPC_TA_VAN_KHANH | hạ Rễ Mộng Tinh Anh; tương tác ký ức 3 lần | Tạ Vân Khanh thú nhận từng ký lệnh phong tỏa tháp vì sợ chiến tranh | ký ức xem lại được; mảnh ký ức, mở C2-05 |
| C2-05 Mạch suối trở lại | NPC_FOREMAN_MOC | hạ Cổ Thụ Trăm Mắt; phá 3 rễ phát sáng theo thứ tự; chạm nguồn suối | nhật ký Cơ Vô Tướng ghi việc rút mạch “để cứu một vùng” | boss reset; ngọc Mộc và xưởng chế tác; mở Sa Hỏa |

### Chương III — Lò không tắt (cấp 36–50)

| ID | Bắt đầu | Các bước chính | Cảnh thoại/ý nghĩa | Thất bại, thưởng, mở khóa |
|---|---|---|---|---|
| C3-01 Đoàn xe cạn nước | NPC_SAM_CHU_QUY | lấy 3 bồn; chọn đường Sa Khô hoặc Hẻm Tro; giữ xe qua 2 đợt | chọn đường nhanh thêm tinh anh, đường dài thêm node nguyên liệu | xe có checkpoint; XP/Đồng; mở C3-02 |
| C3-02 Tro trong phổi | NPC_MEDIC_SA_HOA | thu 5 mặt nạ; cứu 4 thợ; đi qua khí độc bằng vùng thông gió | thợ không bị ép làm cho Cơ; họ ở lại vì nợ nước | thợ miễn nhiễm khi cứu; Trà Thanh Tâm, mở C3-03 |
| C3-03 Bản khắc dưới lò | NPC_HA_MAC | hạ Người Canh Lò; nhặt 3 bản khắc; ghép tại bàn | dòng chữ cho thấy Cơ Vô Tướng từng cấp nước miễn phí | boss respawn; MAT-SOUL; mở C3-04 |
| C3-04 Ba van lửa | NPC_FORGE_MASTER | nhóm chạm 3 van; mỗi van giữ 20 giây; hạ đợt quái | mỗi van đòi người giữ vị trí, dạy chia vai | mỗi van là checkpoint; vật liệu cường hóa; mở C3-05 |
| C3-05 Lò Trời | NPC_FORGE_MASTER | boss 3 pha; pha 1 phá giáp, pha 2 tắt van, pha 3 tránh dòng lửa | sau trận, người chơi chọn công bố nhật ký hoặc giao hội đồng | lựa chọn đổi Trust/thoại, không đổi loot; lõi Hỏa, mở Trấn Sơn |

### Chương IV — Thành không có chủ (cấp 51–65)

| ID | Bắt đầu | Các bước chính | Cảnh thoại/ý nghĩa | Thất bại, thưởng, mở khóa |
|---|---|---|---|---|
| C4-01 Dân qua cổng | NPC_REFUGEE_LEADER | hộ tống 3 nhóm; bật cổng trú ẩn; hạ phục kích | quân hai phía đều nhận lệnh giả giống nhau | nhóm chết hồi checkpoint; mở Trấn Sơn |
| C4-02 Mệnh lệnh không dấu | NPC_TA_VAN_KHANH | so 3 bản lệnh; hỏi 2 sứ giả; lấy dấu sáp gốc | con dấu có bụi kim loại từ phòng chỉ huy | có thể lặp điều tra; Danh Vọng, mở C4-03 |
| C4-03 Ba cổng thành | NPC_GUILD_SCOUT | nhóm 5 giữ cổng Đông/Tây/Nam tổng 4 phút; sửa 2 ụ nỏ | NPC hướng dẫn phân người, không yêu cầu DPS check | mất cổng thì vòng lại; phù sửa đồ/XP |
| C4-04 Cờ trên tường | NPC_CAPTAIN_TRAN_SON | chiếm kho tiếp tế; phá cổng; kéo cờ lên tháp | đây là công thành truyện, không yêu cầu bang thật | respawn ở trại; mở hoạt động công thành |
| C4-05 Thiết Giáp Tướng | NPC_TONG_BANH | phá 2 bẫy giáp; đánh Tống Bành; đọc thư lệnh sau trận | Tống Bành thú nhận gây chiến giả để gom quân cho Cơ | boss reset; bản đồ năm tháp, mở Bạch Uyên |

### Chương V — Thành phố dưới Bạch Uyên (cấp 66–80)

| ID | Bắt đầu | Các bước chính | Cảnh thoại/ý nghĩa | Thất bại, thưởng, mở khóa |
|---|---|---|---|---|
| C5-01 Đài Lặn | NPC_DIVER_LEAD | tìm 3 thợ lặn; lấy bình khí; mở cửa phế tích | một thợ lặn nghe tiếng chuông giống Bến Mưa | bình khí được cấp lại; mở khu nước |
| C5-02 Ba buồng áp suất | NPC_DIVER_LEAD | bật 3 trạm theo đèn; trú khỏi 2 đợt thủy triều | màu/biểu tượng chỉ hướng, không cần pixel-hunt | checkpoint mỗi trạm; vật liệu Thủy |
| C5-03 Người viết nhật ký | NPC_HA_MAC | ghép 4 trang; hỏi Hạ Mặc; tìm ngăn bí mật ở x=246 | người sống sót bị xóa tên để che lỗi thí nghiệm | có marker gợi ý; nhật ký, mở C5-04 |
| C5-04 Lời khai năm môn phái | NPC_HA_MAC | đưa bản sao cho 5 trưởng phái; hoàn tất 5 hội thoại | không môn phái nào hoàn toàn vô tội; hòa giải không phải tha bổng | đổi danh vọng/thoại; mở raid/quest bang |
| C5-05 Mẫu Xà Thủy | NPC_DIVER_LEAD | boss theo triều; đứng vùng sáng khi nước rút; phá vảy khi nó cắm đầu | boss canh lõi Thủy, không phải kẻ gây khủng hoảng | boss reset; lõi Thủy, mở Vực |

### Chương VI — Nghịch Mạch (cấp 81–100)

| ID | Bắt đầu | Các bước chính | Cảnh thoại/ý nghĩa | Thất bại, thưởng, mở khóa |
|---|---|---|---|---|
| C6-01 Năm đội, năm tháp | NPC_LYAN tại trại | hoàn thành 5 tương tác trụ; đóng góp cộng dồn toàn server | người chơi khác instance vẫn tiến độ cùng sự kiện | tương tác retry; cờ thế giới, mở C6-02 |
| C6-02 Cửa mạch mở | NPC_TA_VAN_KHANH | hạ 3 đợt; giữ ít nhất 2/3 cột trong 60 giây | Cơ phát thanh cảnh báo sắp mở Hợp Mạch | vòng lặp nếu thất bại; mở điểm dịch chuyển |
| C6-03 Lõi môn phái | NPC_MASTER_[CLASS] | lớp riêng hoàn tất 3 mục tiêu; nhận mảnh lõi | mỗi lớp chọn dùng sức mạnh để cứu dân thay vì giữ riêng | quest riêng mỗi nhân vật; mỹ phẩm vũ khí |
| C6-04 Người muốn cứu thế giới | NPC_CO_VO_TUONG | đánh Cơ pha 1; xem ký ức quê hương; nói chuyện tại cutscene | động cơ được hiểu nhưng nhân vật phản đối quyền cưỡng ép | không có lựa chọn bỏ qua boss; mở raid cuối |
| C6-05 Huyền Ấn mới | NPC_LYAN tại Sảnh Ấn | raid 10: chia nhóm trụ; ngắt 3 kẻ đục mạch; boss 3 pha | năm phái cùng sửa cơ chế để nó không còn chủ nhân duy nhất | raid reset theo tuần; cấp 100, cosmetic, mở Mạch Triều |

## 3. 40 nhiệm vụ phụ bản đầu

Mỗi dòng là một quest nhỏ độc lập; mục tiêu có checkpoint, thưởng là EXP phụ + Đồng/nguyên liệu/mỹ phẩm nhỏ. Quest phụ không dùng đồ Cổ Vật làm thưởng chính.

### Bến Mưa

| ID | Tên / mục tiêu |
|---|---|
| SQ-BM-01 | Lưới rách: nhặt 5 mảnh lưới ở bờ tây, đưa Ngư Phủ |
| SQ-BM-02 | Đèn cho người lạc: thắp 3 đèn từ bến tới đầm, hạ 3 Cá Linh |
| SQ-BM-03 | Mầm lau lạ: lấy 4 mầm phát sáng, trao Dược Sư |
| SQ-BM-04 | Dấu chân thứ sáu: lần theo 4 dấu giày, tìm túi đồ nhưng không mở phong thư |
| SQ-BM-05 | Bữa cơm sau mưa: thu 3 cá và 2 rau, giao bếp; mở công thức thức ăn |

### Thanh Lạc

| ID | Tên / mục tiêu |
|---|---|
| SQ-TL-01 | Bảng tin trống: hoàn thành 3 yêu cầu dân cư |
| SQ-TL-02 | Năm lá cờ: sửa 5 cột cờ quanh quảng trường |
| SQ-TL-03 | Món đồ thất lạc: tìm nhẫn trong 3 gian hàng theo lời chủ |
| SQ-TL-04 | Người mới nhập môn: đấu tập 3 NPC không gây sát thương thật |
| SQ-TL-05 | Sổ kho Sầm Quỹ: kiểm 4 kiện hàng, phát hiện một hóa đơn sai |

### Lâm Triều

| ID | Tên / mục tiêu |
|---|---|
| SQ-LT-01 | Thuốc cho tiều phu: hái 5 dược thảo ở bìa rừng |
| SQ-LT-02 | Tổ chim rơi: cứu 3 chim con khỏi rễ, không đánh cây non |
| SQ-LT-03 | Nấm biết hát: tìm 4 nấm theo âm thanh, chế thuốc ở trạm |
| SQ-LT-04 | Người nhớ nhầm: ghép 3 ký ức của một tiều phu |
| SQ-LT-05 | Cầu dây mục: thay 4 dây cầu rồi dẫn đoàn qua |

### Sa Hỏa

| ID | Tên / mục tiêu |
|---|---|
| SQ-SH-01 | Bản đồ nước: đặt 4 cọc chỉ đường tới giếng |
| SQ-SH-02 | Lưỡi búa nguội: tìm búa bị cuốn vào cát, hạ 5 bọ cát |
| SQ-SH-03 | Gió mang tro: bật 3 quạt thông gió trong hầm |
| SQ-SH-04 | Đoàn xe lạc: tìm xe phụ ở hai ngã, dẫn về đường chính |
| SQ-SH-05 | Bản nhạc lò rèn: tương tác 4 dụng cụ theo nhịp để mở công thức |

### Trấn Sơn

| ID | Tên / mục tiêu |
|---|---|
| SQ-TS-01 | Tên trên bia: khắc lại 5 tên dân đã mất |
| SQ-TS-02 | Thùng tiếp tế: giao 4 thùng cho lính ở 3 cổng |
| SQ-TS-03 | Mũi tên mắc tường: thu 6 tên, sửa ụ nỏ |
| SQ-TS-04 | Lời xin lỗi của người lính: tìm đồng đội và chuyển thư |
| SQ-TS-05 | Kèn báo động: kích hoạt 3 kèn theo thứ tự khi có tập kích |

### Bạch Uyên

| ID | Tên / mục tiêu |
|---|---|
| SQ-BU-01 | Đèn đáy biển: thay lõi 4 đèn đường |
| SQ-BU-02 | Bản đồ rong: lấy 5 mảnh bản đồ không giết cá hiếm |
| SQ-BU-03 | Khoang kín: xả nước 2 khoang, mở rương cứu hộ |
| SQ-BU-04 | Tiếng hát trong vỏ ốc: tìm 3 vỏ ốc và phát lại ký ức |
| SQ-BU-05 | Thợ lặn nghỉ hưu: thu dụng cụ nghề và chế một bộ sửa |

### Vực Nghịch Mạch

| ID | Tên / mục tiêu |
|---|---|
| SQ-VN-01 | Bóng đi trước: theo bóng qua 5 mốc, né vùng lặp |
| SQ-VN-02 | Ba chiếc đồng hồ: chỉnh đồng hồ về cùng nhịp |
| SQ-VN-03 | Mảnh trời cũ: thu 4 mảnh, trao Ly An |
| SQ-VN-04 | Cửa không có bản lề: kích hoạt 3 nút theo màu/biểu tượng |
| SQ-VN-05 | Lời nhắn của Cơ: tìm 5 bản ghi, xem thứ tự thời gian |

### Đài Ngũ Mạch / endgame

| ID | Tên / mục tiêu |
|---|---|
| SQ-DM-01 | Người canh trụ: nói chuyện 5 người sau raid |
| SQ-DM-02 | Năm món ăn: thu nguyên liệu 5 hệ, nấu tại sảnh |
| SQ-DM-03 | Vết nứt còn lại: đóng 3 khe nhỏ trong vùng thường |
| SQ-DM-04 | Tấm bia không tên: chọn ghi 5 nhân chứng lên bia |
| SQ-DM-05 | Chuyến thư mới: chuyển thư của Ly An tới từng vùng |

## 4. Cảnh truyện và lời thoại chuẩn

### P00-01 — khi nhận thư
- Ly An: “Nếu họ hỏi, cô chưa từng giữ lá thư này.”
- Người chơi: “Cô đang sợ ai?”
- Ly An: “Người biết tên cô trước khi được giới thiệu.”
- Khi giao: Tạ Vân Khanh nhìn dấu sáp, cất vào tay áo: “Dấu này không nên còn tồn tại.”

### Sau Mãng Cốt
- Tạ Vân Khanh: “Huyền Ấn đã chết ba trăm năm.”
- Ly An: “Vậy thứ vừa gọi tên anh là gì?”
- Tạ Vân Khanh: “Một câu hỏi mà năm môn phái đều tránh trả lời.”

### Cơ Vô Tướng trước raid cuối
- Cơ Vô Tướng: “Ta đã nhìn thấy một ngôi làng chết vì nước không tới. Các người gọi đó là tự do của năm mạch.”
- Người chơi: “Cứu người không cho ông quyền chọn thay họ.”
- Cơ: “Nếu ta dừng lại, những cái chết cũ chẳng có ý nghĩa gì.”
- Kết thúc: người chơi không tha thứ; họ buộc ông giúp giữ trụ cuối cùng, sau đó hội đồng xét xử ông.

## 5. Quest acceptance / failure

- Escort NPC không thể đi xa hơn camera + 12m; khi rơi khỏi đường, snap tới checkpoint có animation.
- Quái quest có icon riêng và respawn 20s sau khi chết; người chơi cùng party chia tiến độ nếu ở trong 35m.
- Item quest nằm trong quest pouch, không chiếm túi và không thể bán/phân giải.
- Boss solo/party có vùng báo đòn rõ; nếu người chơi rời encounter quá 60s, tiến độ boss reset nhưng quest không mất.
- Raid quest progress tính theo clear; người disconnect có thể nhận clear nếu reconnect trước khi boss chết + 60s và đã tham gia encounter tối thiểu 30%.
- Thưởng one-time quest dùng unique transaction id. Quest daily/weekly dùng reset bucket server-side.
