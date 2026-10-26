# ĐẶC TẢ CHIẾN ĐẤU, KỸ NĂNG VÀ HIỆU ỨNG
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.0

### Mục đích và quy ước

Tài liệu này chốt biểu hiện hình ảnh, hoạt ảnh, vùng va chạm và tín hiệu đọc được cho 30 kỹ năng chủ động của năm môn phái. Số liệu cân bằng cấp 1 kế thừa Content Bible; giá trị cuối cùng phải lấy từ bảng cấu hình server, không hardcode trong animation hoặc VFX. Kỹ năng không sao chép tên, nhân vật, hiệu ứng nhận diện hay nội dung cốt truyện của KPAH.

Game dùng đồ họa pixel art 2D ngang theo `Pixel_Art_Production_Standard_vi.md`: 640×360 logical, 20 PPU, frame-based spritesheets, point filter và integer scale. 1 WU=0,5m; nhân vật 5 WU. Hoạt ảnh có thể hiển thị 6–12 fps bằng frame hold trong khi client chạy 60 FPS; gameplay vẫn do server mô phỏng tick 20 Hz. Thời điểm gây sát thương do server xác nhận, không khóa vào nhịp frame art.

### Nguyên tắc chung cho người dựng

- Mỗi kỹ năng cần ba mức đọc: báo trước hình dáng/đường đi, khoảnh khắc trúng, trạng thái sau trúng. Quái nhỏ được phép bị hất nhẹ; boss không bị khóa hoạt ảnh dài mà nhận tích lũy Choáng Mạch.
- Silhouette nhân vật phải còn nhìn thấy khi VFX chồng nhau. Không phủ kín mặt, vũ khí hoặc telegraph đỏ của boss. Đồng minh dùng tông xanh ngọc/trắng; nguy hiểm dùng cam đỏ/tím; màu sắc không phải tín hiệu duy nhất, luôn kèm hình dáng và âm thanh.
- Độ sáng kỹ năng thường 1.0, cơ động 1.1, tuyệt kỹ 1.35 theo dải pixel/palette; không lóe trắng toàn khung. Không bloom/blur; có tùy chọn giảm flash, rung và hạt bay.
- VFX kỹ năng người chơi không che vạch cảnh báo boss. Khi có trên 12 hiệu ứng chiến đấu trong cùng vùng 8m, giảm hạt phụ và bóng; không giảm outline vùng nguy hiểm.
- Số liệu dưới đây là thời gian hình ảnh ở 60 FPS. Server có thể xác nhận hit lệch tối đa 100ms; client dự đoán animation, rồi hòa giải vị trí/sát thương khi phản hồi. Không trình diễn trúng đòn nếu lệnh bị server từ chối.
- Hitbox theo đơn vị mét trong mô tả thiết kế; khi chuyển sang world unit nhân đôi. Tầm bắt đầu đo từ tâm nhân vật tới rìa hitbox địch. Các đòn đánh không xuyên vật cản trừ khi ghi rõ.
- Cấp kỹ năng tăng tối đa 8% sát thương hoặc giảm 4% tiêu hao theo Content Bible. Không dùng nâng cấp để tăng kích thước vùng báo nguy hiểm hay thời gian bất tử.

### Bảng thời gian hoạt ảnh chuẩn

| Loại | Chuẩn thời gian | Quy tắc |
|---|---:|---|
| Đòn thường | 0.10–0.18s chuẩn bị; 0.10–0.16s hit; 0.18–0.28s hồi | Cho phép hủy sang né sau frame hit + 4f |
| Kỹ năng nhanh | 0.12–0.22s chuẩn bị; 0.08–0.18s hit; 0.18–0.30s hồi | Hủy sang né ở 70% thời gian hồi |
| Đòn có báo trước | 0.35–0.75s báo; 0.10–0.25s hit; 0.25–0.40s hồi | Báo trước vẫn hiện đủ dù giảm hiệu ứng |
| Tuyệt kỹ | 0.50–0.90s chuẩn bị; 0.20–0.45s hit; 0.45–0.70s hồi | Camera không khóa người chơi; tối đa rung nhẹ 0.12s |
| Né | 0.08s khởi động; 0.18s tránh; 0.20s hồi | i-frame 0.18s; né dùng chung hồi chiêu 7s |

## Thư viện 30 kỹ năng

Mỗi dòng gồm mô tả người chơi, thiết kế hoạt ảnh/VFX, cách đọc hit và thông số chuẩn cấp 1. Mã kỹ năng là mã dữ liệu, có thể đổi tên hiển thị mà không đổi khóa lưu.

### Minh Kiếm — hệ Kim, cơ chế Kiếm Ý 0–5

**SK-MK-01 — Phản Quang**  
Vai trò: đỡ phản công. CD 10s, 12 MP. Nhấn tạo thế thủ 0,4s, giảm 70% sát thương; nếu đòn cận chiến trúng trong cửa đỡ, phản 180% sát thương vũ khí và nhận 2 Kiếm Ý. Nếu không có đòn chạm, kết thúc với giảm sát thương hụt 20%. Hoạt ảnh: hạ trọng tâm, đưa kiếm chéo trước ngực; 6 frame đầu viền bạc mảnh báo thế đỡ. Khi đỡ thành công, kiếm phát một vòng cung lục giác màu vàng nhạt, âm thanh kim loại khô; không tạo flash màn hình. Boss không bị choáng, người chơi nhận thông báo “Đỡ chuẩn” cạnh thanh tài nguyên. Vùng đỡ 120 độ phía trước, cự ly 2,2m.

**SK-MK-02 — Tầm Long**  
Vai trò: áp sát/đánh mục tiêu đầu. CD 8s, 16 MP, lao 5,5m, 150%, +1 Kiếm Ý. Chuẩn bị 0,15s, lướt 0,20s, hồi 0,24s. Mũi kiếm kéo vệt trắng bạc có lõi vàng; nhân vật không biến mất. Hit là một hình thoi mảnh trước người, không xuyên tường; nếu va chướng ngại thì dừng ở mép. Tạo vạch bụi nhỏ ở điểm dừng. Quái thường bị lùi 0,25m, boss tích Choáng Mạch.

**SK-MK-03 — Kiếm Trận**  
Vai trò: quét nhóm. CD 10s, 22 MP, hình quạt 100 độ, tổng 190%, tối đa 5 mục tiêu. Ba nhát có nhịp 0,10/0,12/0,14s: ngang, chéo lên, chém xuống; trọng số sát thương 45/55/90%. VFX ba cung kiếm vàng trắng lệch nhau, cung thứ ba dày nhất; mỗi cung tồn tại dưới 0,22s. Đánh trúng nhiều mục tiêu có số sát thương tách riêng, không cộng dồn một con số che mục tiêu. Ưu tiên trúng địch gần nhất trong quạt.

**SK-MK-04 — Thiết Y**  
Vai trò: phòng thủ cá nhân. CD 16s, 24 MP, khiên bằng 12% HP tối đa trong 4s, không cộng dồn. Động tác cắm kiếm cạnh thân rồi kéo vòng sáng kim loại mờ quanh vai và ngực. Khiên hiển thị một viền lục giác xanh bạc ở chân thanh HP, không phủ toàn thân. Khi bị đánh, viền nứt theo lượng khiên mất; hết thời gian tự tan thành bụi sáng. Nội tại Thủ Nhất cộng thêm 4% giá trị khiên theo quy tắc Bible.

**SK-MK-05 — Bạch Hồng (cơ động)**  
Vai trò: vượt ngang, xóa chậm. CD 9s, 10 MP, lướt 6m ngang, không gây sát thương. Vệt kiếm mảnh trắng xanh chạy sau nhân vật trong 0,16s; nhân vật luôn thấy rõ tại đầu/cuối pha. Xóa trạng thái Chậm khi khởi động, không xóa choáng, trói, độc hoặc vùng khóa. Không cho đi xuyên tường/địch lớn; va chạm dừng lướt. Không có hitbox sát thương.

**SK-MK-06 — Vạn Tượng Quy Nhất (tuyệt kỹ)**  
Vai trò: đường kiếm dồn sát thương. CD 60s, 40 MP. Tấn công đường thẳng 7m, 260% + 60% mỗi Kiếm Ý, tối đa 5 mục tiêu; tiêu Kiếm Ý khi server chấp nhận. 0,70s kết tụ: các nét kim loại nhỏ hội về mũi kiếm, nhân vật giữ dáng ngang vững. Sau báo trước là đường chém ngang rộng 0,8m, vệt vàng trắng phân lớp, tồn tại 0,35s. Camera rung tối đa 0,12s tại hit, không cắt cảnh; số Kiếm Ý được hiển thị thành năm vạch sáng tắt theo số đã dùng. Boss nhận sát thương và Choáng Mạch, không bị đứng im.

### Ảnh Đao — hệ Hỏa, cơ chế Nhiệt 0–5

**SK-AD-01 — Huyết Nguyệt**  
Vai trò: chảy máu đơn mục tiêu. CD 8s, 14 MP, đòn 140% và chảy máu 3 lần ×25% trong 4s. Chém vòng cung đỏ sẫm, rìa cam chỉ sáng lúc cắt; tránh máu bắn hoặc hình ảnh bạo lực. Dấu chảy máu là ba vệt đỏ nhỏ chạy dọc viền thanh máu mục tiêu, mỗi tick có âm thanh rất nhẹ. Nhận Nhiệt theo quy tắc lớp: đòn trúng cho 1 Nhiệt tối đa một lần mỗi 1,5s.

**SK-AD-02 — Tàn Hỏa**  
Vai trò: gài nổ. CD 12s, 18 MP. Gắn dấu 5s; đòn tiếp theo của người chơi lên mục tiêu kích nổ 120% vùng nhỏ, hoặc 180% nếu có đủ 5 Nhiệt tại lúc kích hoạt. Dấu là một vòng than đỏ quanh chân địch với năm khe sáng; đồng đội nhìn thấy biểu tượng nhỏ, không phải vòng sàn. Nổ bán kính 1,5m, VFX bụi than hướng ra ngoài và tia lửa ngắn. Nếu dấu hết hạn thì tắt, không tự nổ. Mỗi mục tiêu chỉ mang một dấu từ cùng người chơi.

**SK-AD-03 — Xích Ảnh**  
Vai trò: hai nhát, thưởng vị trí sau lưng quái. CD 10s, 20 MP, hai hit ×85%. Nhát đầu lướt chéo ngắn 1m, nhát sau đảo cổ tay chém ngược. Mỗi nhát có cửa hitbox riêng 0,10s, tổng góc 80 độ. Nếu nhát hai chạm phía sau quái thường, tăng theo nội tại Bóng Sát (+8%); boss dùng hướng vị trí của người chơi khi lệnh được xác nhận. Vệt lửa tối, không dùng ảnh phân thân gây nhầm với nhân vật thật.

**SK-AD-04 — Tước Mạch**  
Vai trò: làm chậm/tích Choáng Mạch. CD 14s, 22 MP, 160%, chậm 25% trong 2,5s; boss nhận Choáng Mạch thay hiệu ứng khống chế. Hoạt ảnh chém dọc từ vai xuống, thanh lửa mỏng dừng ở vị trí hit. Quái thường có dấu ba vệt xích đỏ trên chân; boss có biểu tượng mạch bị nứt cạnh tên hiệu ứng. Không khóa hoạt ảnh mục tiêu; không cộng dồn thời gian làm chậm.

**SK-AD-05 — Ảnh Bộ (cơ động)**  
Vai trò: đổi vị trí. CD 8s, 10 MP, lướt 6m, xóa khóa mục tiêu của quái thường; không tàng hình. Nhân vật thu thấp người và trượt qua làn khói than trong 0,22s; silhouette được viền màu cam để đồng đội không mất dấu. Khóa mục tiêu boss không bị xóa. Không tạo ảo ảnh có thể bị nhắm.

**SK-AD-06 — Tử Diệm (tuyệt kỹ)**  
Vai trò: nổ diện nhỏ, tiêu Nhiệt. CD 60s, 35 MP, 230% vùng nhỏ +45% mỗi Nhiệt, tiêu sạch Nhiệt. 0,55s tích lực: lưỡi đao hút các hạt than vào sống đao; vòng cảnh báo cá nhân 1,7m tông đỏ đen chỉ báo vùng gây sát thương, không phải vùng nguy hiểm cho chính người chơi. Chém xoay một vòng thấp, lửa bùng 0,25s, tắt nhanh để thấy boss. Mỗi tầng Nhiệt thêm một vòng nhỏ ở điểm hit, tối đa 5 vòng; số vòng đồng bộ biểu tượng Nhiệt.

### Huyền Bút — hệ Thủy, cơ chế Thủy Ấn 0–5

**SK-HB-01 — Mực Triều**  
Vai trò: đạn sóng xuyên quái thường. CD 6s, 12 MP, 130%, đường thẳng 5m, xuyên tối đa 3 quái thường. Vẽ nét ngang bằng bút; nét mực xanh lam chuyển thành sóng có rìa giấy loang, không giống đạn phép tròn. Đầu sóng cao 0,8m, bay 0,25s; mỗi mục tiêu trúng có dấu chấm mực nhỏ. Boss chặn đường đạn; không xuyên tường. Nội tại Nét Mực giảm 1s CD sau tổng ba lần trúng hợp lệ.

**SK-HB-02 — Hàn Châm**  
Vai trò: làm chậm/khống chế nhẹ. CD 12s, 18 MP, 110%, chậm 35% trong 2s; quái nhỏ đóng băng 0,6s. Bút chấm ba điểm sáng xanh trước khi một kim băng mảnh bay đi. Trúng tạo hình băng dạng cánh hoa trên chân, không phủ thân. Boss nhận làm chậm theo giới hạn PvE hoặc tích Choáng Mạch tùy bảng kháng; không đóng băng boss. Cửa báo trước 0,18s, tốc độ đạn đủ để đọc và né ở cự ly xa.

**SK-HB-03 — Thủy Kính**  
Vai trò: khiên đồng đội. CD 16s, 22 MP, khiên 10% HP tối đa trong 4s; chỉ giữ khiên lớn nhất. Chọn mục tiêu đồng minh theo hướng con trỏ/joystick hỗ trợ: ưu tiên đồng minh gần tâm nút, nếu không chọn thì người gần nhất trong 6m có HP thấp nhất. Một nét tròn xanh ngọc khép quanh mục tiêu, mặt kính mỏng nghiêng 15 độ; khiên không che nhân vật. Nội tại Tĩnh Thủy thêm phần khiên theo bảng nội tại khi mục tiêu thấp HP; quy tắc không cộng dồn bắt buộc.

**SK-HB-04 — Mưa Tinh**  
Vai trò: hồi máu vùng. CD 18s, 28 MP, bán kính 3m; hồi 8% HP +2% mỗi giây trong 3s; tiêu 2 Thủy Ấn tăng tổng hồi 30%. Vẽ một vòng tròn xanh nhạt trên mặt đất, báo trước 0,45s; giọt sáng rơi thẳng trong vùng, không làm giảm tương phản nền. Hồi tick ở 0/1/2/3s; người rời vùng sau khi nhận tick vẫn giữ lượng đã hồi. Tối đa 5 người theo nội tại Chia Dòng; thứ tự ưu tiên: người chơi, thành viên nhóm trong vùng theo % HP thấp nhất. Không hồi mục tiêu ngoài party/guild.

**SK-HB-05 — Lưu Thủy Bộ (cơ động)**  
Vai trò: lùi giữ khoảng cách. CD 10s, 10 MP, lùi 4m và tăng 20% tốc chạy trong 1,5s. Nhân vật xoay vai, bước trượt ngược, để lại hai nét nước mỏng. Hướng lùi theo vector ngược hướng mặt; có thể chỉnh bằng joystick, không xuyên địch/tường. Vệt nước không gây sát thương và tan sau 0,3s.

**SK-HB-06 — Long Mạch Hồi Nguyên (tuyệt kỹ)**  
Vai trò: hồi nhóm và giải trạng thái. CD 70s, 45 MP; hồi 12% HP cho nhóm và giải một Chậm hoặc Độc, chịu giới hạn raid. Nhân vật viết một vòng ấn lớn dưới chân; nét chữ cách điệu là hình học hư cấu, không dùng ký tự giả Hán sai nghĩa. Sóng xanh lam tràn ra bán kính 8m trong 0,45s, đồng minh nhận một dải sáng từ chân lên vai. Chỉ mục tiêu party trong cùng encounter được hồi; raid áp dụng hệ số cấu hình (mặc định 70% từ ngoài party), tránh vượt ngân sách hồi. Không xóa stun/khóa cơ chế boss.

### Thạch Chùy — hệ Thổ, cơ chế Thế 0–5

**SK-TC-01 — Trấn Sơn**  
Vai trò: đánh đơn mục tiêu, giảm tốc. CD 8s, 14 MP, 170%, giảm tốc 20% trong 2s. Nâng chùy qua vai, nện chéo xuống; chuẩn bị 0,25s cho tiếng rít đá. Hitbox hình quạt 60 độ, sâu 2,6m. Vết nứt đất chỉ là decal ngắn 0,35s, không tồn tại như chướng ngại. Quái hiện bụi vàng xám ở chân; boss nhận Choáng Mạch.

**SK-TC-02 — Chấn Địa**  
Vai trò: sát thương quanh thân/hất quái nhỏ. CD 14s, 20 MP, vòng bán kính 3m gây 120%; quái thường hất 0,5s. Nâng chùy thẳng, vòng bụi mỏng hiện trên đất 0,35s, sau đó sóng đá thấp lan ra. Đường kính tối đa 6m; mép ngoài dùng mảnh đá nhỏ, không dựng khối có thể hiểu là platform. Boss không hất, có thanh tích lũy Choáng Mạch.

**SK-TC-03 — Thiết Bích**  
Vai trò: giảm sát thương nhận. CD 18s, 24 MP, giảm 25% sát thương trong 4s; tiêu 2 Thế tăng lên 35%. Hạ chùy làm trụ, hiện ba mảng giáp đá trên vai/lưng/đầu gối, không biến nhân vật thành khối đá. Viền buff màu đất sáng quanh thanh HP; khi bị đánh, mảng nứt theo thời gian còn lại. Không cộng dồn, lần dùng mới chỉ làm mới thời lượng.

**SK-TC-04 — Khiêu Chiến**  
Vai trò: điều hướng quái thường. CD 20s, 16 MP; quái thường trong 6m ưu tiên tấn công người dùng trong 4s; boss không bị ép đổi mục tiêu. Nhân vật gõ chùy xuống đất, phát vòng âm thanh dạng đường gợn màu đất. Quái thường có mũi tên nhỏ hướng về người chơi, chỉ hiển thị trong 0,7s; biểu tượng khiêu chiến cạnh tên quái giữ 4s. Thủ lĩnh có miễn nhiễm nhưng vẫn nhận sát thương nếu kỹ năng có cấu hình sát thương riêng (mặc định không gây damage).

**SK-TC-05 — Phá Nham (cơ động)**  
Vai trò: lao ngắn/ngắt hoạt ảnh quái nhỏ. CD 10s, 12 MP, lao 4m gây 100%, ngắt hoạt ảnh quái thường. Chuẩn bị 0,22s, người chơi ghì vai sau chùy, sau đó lao thẳng với một dải bụi sát mặt đất. Va mục tiêu thường tạo vòng đá nhỏ và ngắt động tác không phải boss; không xuyên tường. Boss không bị interrupt, chỉ nhận sát thương và Choáng Mạch.

**SK-TC-06 — Sơn Thần Giáng Thế (tuyệt kỹ)**  
Vai trò: vùng chắn ngắn và sát thương. CD 70s, 40 MP, vùng 4m tồn tại 5s, gây 180%; tiêu Thế tăng tối đa 2s. Cắm chùy, tạo một vòng chắn bằng các phiến đá thấp cao 0,55m; khoảng mở hướng camera giúp người chơi nhìn thấy bên trong. Vùng tấn công đánh một lần khi tạo, sau đó không tick damage. Đá mờ dần từ giây cuối; không chặn di chuyển đồng minh, đạn đồng minh hoặc telegraph boss. Mỗi Thế làm một phiến sáng và thêm tối đa 2s.

### Linh Cung — hệ Mộc, cơ chế Mộc Tiêu 0–5

**SK-LC-01 — Khóa Mạch**  
Vai trò: đánh dấu tăng sát thương nhóm. CD 10s, 16 MP, 130%, dấu 5s khiến nhóm gây thêm 3%, không cộng dồn. Bắn một mũi tên lá dài, quỹ đạo dễ đọc; khi trúng hiện dây rễ xanh ngọc nhỏ quấn quanh viền mục tiêu. Biểu tượng dấu hiện cạnh HP quái; nếu nhiều cung thủ, ưu tiên dấu có thời lượng còn lại dài nhất hoặc từ người chơi có đóng góp gần nhất theo cấu hình, không cộng nhiều buff. Nội tại Ghim Dấu tăng thời lượng 1s.

**SK-LC-02 — Dây Gai**  
Vai trò: bẫy làm chậm. CD 14s, 18 MP, bán kính 2m gây 90%, làm chậm quái thường 40% trong 2,5s. Bắn hạt giống xuống điểm chọn, vòng rễ xanh lục hiện 0,45s báo vùng; dây gai mọc thấp từ đất. Bẫy tồn tại tối đa 4s nếu không trúng; chỉ kích hoạt một lần. Boss không bị root/chậm nếu có kháng, vẫn có thể tích Choáng Mạch. VFX không che texture đất cảnh báo.

**SK-LC-03 — Liên Châu**  
Vai trò: sát thương nhiều hit. CD 8s, 18 MP, 5 mũi ×45%, tối đa 3 mũi trên cùng một mục tiêu. Loạt tên bắn trong 0,55s với khoảng 0,11s; độ lệch quạt tối đa 12 độ; mục tiêu khóa gần con trỏ đầu tiên. Mỗi tên có trail lá 0,12s và va chạm riêng để đọc số hit. Hệ thống mục tiêu giới hạn 3 tên vào một mục tiêu nhằm giữ vai trò đa mục tiêu, không cho bắn tự động nhân damage lên boss.

**SK-LC-04 — Tán Hoa**  
Vai trò: hình nón gần. CD 12s, 20 MP, góc 100 độ, tổng 150%, giảm 30% nếu mục tiêu ở quá gần. Bắn loạt cánh gỗ/hoa mảnh theo hình quạt, không phát nổ. Ranh giới gần là 0,8m; mục tiêu trong đó nhận 70% tổng hệ số để tránh chồng hitbox cận cảnh. Tông xanh non/vàng kem, không dùng cánh quá lớn. Có số lượng 5–7 cánh chính và hạt phụ giới hạn.

**SK-LC-05 — Phi Diệp (cơ động)**  
Vai trò: lùi đồng thời phản kích. CD 9s, 12 MP, lùi 5m và bắn 80%. Hoạt ảnh kéo cung trong lúc trượt lùi, hitbox tên đi sau 0,12s; nếu lùi bị vật cản thì dừng và vẫn bắn theo hướng ban đầu. Vệt lá chỉ theo đường bay, không tạo hit nếu phát bắn bị server từ chối. Dùng cho điều khiển chuột và joystick; không tự tìm đường vòng.

**SK-LC-06 — Bách Tiễn Quy Tông (tuyệt kỹ)**  
Vai trò: vùng sát thương có báo trước. CD 65s, 40 MP; báo vùng 1,2s, mưa tên bán kính 6m tổng 300%; tiêu 3 Mộc Tiêu tăng 20%. Người chơi chọn điểm trong tầm 12m; hình tròn xanh rêu viền vàng hiện đủ 1,2s, tâm có ba vòng mũi tên để người chơi phân biệt mình tạo và boss cảnh báo. Mưa tên rơi theo 4 đợt trong 0,8s, tổng 300% chia đều; tối đa 8 mục tiêu thường, boss nhận damage theo hệ số. Khi tiêu 3 Mộc Tiêu, vòng tâm sáng thêm ba vạch, không thay đổi vùng/timing để tránh nhầm telegraph.

## Thiết kế combo đánh thường

| Môn phái | Chuỗi mặc định | Đọc hình / phản hồi |
|---|---|---|
| Minh Kiếm | 3 nhát kiếm ngang, chéo, đâm | nhát 3 có vệt kim loại sáng; hoàn tất nhận 1 Kiếm Ý |
| Ảnh Đao | 3 nhát thấp, xoay cổ tay, chém ngược | than rơi ngắn; nhận Nhiệt tối đa mỗi 1,5s |
| Huyền Bút | 3 nét bút thành đạn mực nhỏ | nét thứ 3 mở Thủy Ấn; không phải auto-aim xuyên tường |
| Thạch Chùy | bổ ngang chậm, nện thấp, giáng thẳng | bụi sát đất; mỗi đòn trúng/chặn cho 1 Thế tối đa 2s |
| Linh Cung | bắn 3 tên theo nhịp đều | giữ nút tạo chuỗi; cùng mục tiêu tích Mộc Tiêu mỗi 2s |

Đòn thường không khóa nút quá lâu: mỗi hit có thời gian phản hồi rõ, có thể hủy sang né sau thời điểm trúng +4 frame. Chạm giữ trên mobile tự lặp chuỗi sau 0,1s nghỉ; PC click/nhấn giữ áp dụng chung giới hạn tốc độ server.

## Hướng dẫn asset cho animator, VFX và audio

| Nhóm asset | Yêu cầu bàn giao |
|---|---|
| Actor sprite | frame-based sheet với pivot chân ổn định, anchor vũ khí/tay/chân/ngực/đầu khai báo pixel; layer/variant đổi giáp vẫn snap vào cùng grid; frame art không quyết định vị trí mạng |
| Animation | idle, chạy, nhảy, rơi, đáp, đánh thường 3 hit, hurt, chết, tương tác, 6 skill, né; clip có marker chuẩn bị/hit/recovery |
| VFX | file riêng cho cast, travel, impact, buff/debuff, miss; pivot và scale world-unit; bản low-VFX giảm hạt |
| Audio | cast ngắn, impact nhẹ/nặng, miss, buff, debuff, ultimate; không lấy sample gây giật mình hoặc âm lượng đột biến |
| UI icon | nền vuông 128×128, silhouette dễ đọc ở 48×48; lớp phủ cooldown do client vẽ, không bake vào hình |
| QA nội dung | clip showcase nền sáng/tối, ít nhất 1 mục tiêu thường và 1 boss; kiểm tra mù màu, giảm rung, giảm lóe, cấu hình VFX thấp |

### Danh mục trạng thái dùng chung

| Trạng thái | Biểu tượng | Quy tắc |
|---|---|---|
| Chậm | dấu chân có vòng gợn | không cộng dồn hệ số; lần mới refresh duration |
| Độc | giọt tím xanh | tick theo server; không bị giải bởi kỹ năng chỉ giải Chậm/Độc nếu boss đặt cờ miễn |
| Chảy máu | ba vệt đỏ | tick PvE/PvP khác nhau; hiển thị số giây còn lại khi chọn mục tiêu |
| Khiên | viền lục giác | mất trước HP theo thứ tự server; chỉ giữ giá trị lớn nhất cùng nguồn |
| Đánh dấu | vòng rễ/cơ chế | lợi ích nhóm tối đa một nguồn trên mục tiêu |
| Choáng Mạch | biểu tượng nứt hình mạch | thanh tích lũy riêng cho boss; không khóa hành vi boss lâu |
| Né | đường viền trắng ngắn | không có icon trạng thái lâu; tránh sát thương 0,18s |

### Checklist bàn giao cho triển khai

1. Mọi kỹ năng có ID ổn định, cost/CD/hệ số/target rule/PvP coefficient trong data table.
2. Animation marker và thông số server dùng cùng thời điểm chuẩn; client không tự quyết hit cuối.
3. Mọi vùng kỹ năng có shape, radius/range, duration, collision rule và telegraph rule được lưu tách biệt.
4. Mọi hiệu ứng khống chế khai báo PvE, boss, PvP riêng; không lấy mặc định của quái nhỏ áp vào boss.
5. Các nút tắt giảm rung/lóe/hạt và giới hạn hiệu ứng hoạt động cho toàn bộ skill, không chỉ tuyệt kỹ.
6. Số damage, buff, trạng thái và hiệu ứng âm thanh phải còn đọc được ở màn hình 16:9, 16:10 và 20:9.

