# Đợt thư viện 20261112c — combat tám hướng và Người Giữ Thuyền

Tiếp tục mục tiêu hoàn thiện toàn bộ thư viện asset. Đợt này giữ sprite chibi nguyên khối đã chốt, tạo ảnh bằng `image_gen` tích hợp, giữ PNG nguyên byte, có prompt/tham chiếu và xem trong Godot. Đây là một phần của mục tiêu đang tiếp tục, không phải nghiệm thu toàn game hoặc toàn bộ thư viện.

## 23 sheet được chọn, 368 ô nguồn

| Phần | Nguồn trong đợt | Kết quả |
|---|---:|---|
| Cá Linh: telegraph_01 | N/NE/E/SE × 16 | Ghép S cũ thành 5 góc vẽ / 8 hướng xem |
| Cá Linh: attack_01 | N/NE/E/SE × 16 | Một cú khép hàm; không lấy nhầm windup làm attack |
| Cá Linh: recovery_01 | N/NE/E/SE × 16 | N v2 sửa đuôi cuộn đột ngột khi nối từ attack |
| Cá Linh: hurt | N/NE/E/SE × 16 | NE v2 sửa khung đầu miệng mở; một lần co giật rồi hồi |
| Cá Linh: death | N/NE/E/SE × 16 | Một lần gục; cuối chuỗi giữ nằm, không bật dậy |
| Rễ Nước: idle NE v2 | 16 | Sườn chéo sau bất đối xứng, seed trước khuất; thay binding NE cũ |
| Người Giữ Thuyền: walk S v3 | 16 | Hai chân đổi lượt; sào/áo phao/còi/cuộn dây giữ đúng identity |
| Người Giữ Thuyền: interact S | 16 | Đặt sào tựa vai, hai tay kéo dây, trả về thế đứng |

20 sheet Cá Linh là 320 ô nguồn mới. Kết hợp 5 sheet S đợt trước, năm action trên có **400 ô vẽ nguồn = 5 action × 5 góc × 16**, tham chiếu thành 8 hướng xem bằng policy mirror cũ. SW/W/NW không được tính thêm thành ô vẽ mới. Hai action Người Giữ Thuyền **chỉ có S**, bốn góc nguồn còn thiếu vẫn để thiếu.

Danh mục chính xác: `Art_Source/Actor_Library_20261107/batch_20261112c.json`; PNG ở `Sheets/`, prompt thực ở `Prompts/`. Các bản thử sai được giữ ở `Rejections/` cùng `generation_history.json`: ba atlas nhiều góc sai hướng/nhịp đớp, hai lần sửa Cá Linh và hai bản walk NPC sai chân/nền. Không dùng hoặc chép chúng để bù 16 khung.

NE Rễ Nước là revision cùng ID, giữ nguyên PNG v1 trong lịch sử. Do inventory phản ánh **selection hiện hành**, đợt b hiện còn 12 page/192 ô được chọn; revision NE mới thuộc đợt c. Gói giao ban đầu b có 13 sheet vẫn là sự kiện lịch sử đúng, không xóa ảnh cũ. 46 PNG theo baseline chủ dự án đã chọn vẫn nguyên SHA256.

## Căn điểm neo và tỷ lệ Cá Linh

Neo chân cũ lấy điểm thấp nhất gần đuôi làm thân cá dịch khi đuôi cuộn. Đọc raster hướng N ở kích thước review 88px đo được dao động tương đối của tâm thân bạc khoảng 9,70px theo X và 14,63px theo Y. Đây là chẩn đoán metadata, không phải đo FPS.

Các page Cá Linh dùng `pivotMode=SILVER_CORE_CENTER`: đọc pixel alpha ≥200, R≥110, R≥0,82G và B≥0,95G để lấy tâm vùng thân bạc, loại phần đuôi/vây xanh khỏi ảnh hưởng chính. Cần ít nhất 8 pixel phù hợp; thiếu vùng thân phải đăng ký tay, không đoán pivot. Chỉ cho phép mode này với ID Cá Linh. Không sửa, resample hoặc vẽ lại PNG bằng code. Đây là heuristic đăng ký riêng cho palette hiện tại, không phải bộ nhận dạng dùng cho mọi quái.

`scaleMode=LONGEST_AXIS` lấy trung vị trục dài ba pose đầu, giữ scale suốt clip. Nguồn đứng/ngồi/ngã không bị co giãn theo bbox từng khung. Đo thân bạc ba pose đầu góc N sau sửa: telegraph 32,79px, attack 31,85px, recovery 31,18px, hurt 33,11px, death 33,92px. Attack→recovery lệch khoảng 2%; vẫn cần kiểm hình ảnh, không coi số đo là chứng minh giải phẫu đẹp.

Kiểu neo của class/human/NPC và VFX giữ nguyên. Nhãn hướng cá được dời xuống để không đè sprite khi root nằm tại tâm thân. Studio vẫn chỉnh tay từng pivot/transform/timing và xuất JSON riêng.

## Timing và công cụ

- Cá Linh: báo 0,45s / đánh thử 0,30s / hồi 0,50s; hurt 0,30s, death 1,20s. Hai số báo/hồi từ visual bible; 0,30s attack vẫn là timing trình bày, không đổi authoritative hit window.
- Người Giữ Thuyền: walk 0,80s/16, interact 1,60s/16. Walk lặp; interact một lần. Hai chân đổi lượt và hai tay kéo dây đã xem trong native Studio.
- `CarplingCombatReview.tscn` thêm selector 8 hướng và CLI `--combat-direction N|NE|E|SE|S|SW|W|NW`. Mỗi hướng có 5 action và ô nối ba pha. Bố cục được thu gọn để vừa 1280×720.
- Bộ đếm bên trái thư viện nay tính clip đủ hướng xem, tránh NPC có mỗi S bị ghi như hoàn chỉnh. Tooltip nhắc rõ đây không phải nghiệm thu actor.
- Movie Maker được nhận bằng `Engine.GetWriteMoviePath()`, không suy đoán từ command-line đã bị engine lọc. Video thư viện ghi “Video offline · không đo FPS”; ghép movie và benchmark thực bị từ chối. FPS trong dropdown Studio là mức giới hạn, không phải kết quả benchmark.

```powershell
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_CARPLING:attack_01 -Direction NE -Play
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_CARPLING:death -Direction S -Frame 15
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_WATERROOT:idle -Direction NE -Play -Loop
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:NPC_BOAT_KEEPER:walk -Direction S -Play -Loop
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:NPC_BOAT_KEEPER:interact -Direction S -Play
```

## Nghiệm thu nguồn có phạm vi

32 page được kiểm nguồn: 25 page combat Cá Linh (bao gồm S đã có), 5 page idle Rễ Nước và 2 page S Người Giữ Thuyền. `sourceApprovals` pin cả SHA256 PNG và `bindingSha256` của rect/pivot/scale/direction. Thay ảnh, đổi pivot/scale hoặc đổi nhãn hướng qua pipeline đều làm nguồn mất duyệt cho tới khi kiểm lại. Studio không tự cấp production approval cho bản chỉnh riêng.

Review scope là **source/clip hình ảnh**; không nghiệm thu toàn actor, encounter, AI, damage hoặc game. Bộ kiểm native đi qua 16 khung ở clock 60 bước/s cho cả 8 hướng của năm action Cá Linh, kiểm one-shot giữ cuối và raw/grouped timing. Source sheet và video/PNG native vẫn cần xem, hash khác nhau không chứng minh pose đúng. Rễ Nước còn các action khác; Người Giữ Thuyền còn bốn góc mỗi action mới; locomotion cũ Cá Linh chưa được tự duyệt theo combat mới.

Sau đợt này catalogue actor/skill: **84 page qua structure, 45/1008 job đủ góc nguồn, 9 job đầy đủ góc có nghiệm thu hình ảnh**; 963 job còn thiếu nguồn, 19 page active còn HOLD. 9 job gồm 3 Minh Kiếm kế thừa, idle Rễ Nước và 5 action Cá Linh. Component cung Kiếm Trận vẫn có duyệt riêng, không khép full-skill job. Một atlas full VFX cũ vẫn sai hàng. Catalogue này không phải toàn bộ khối lượng map/tile/UI/icon/audio của game.

Bằng chứng: `Implementation/Reports/Evidence/Actor_Batch_20261112c/` gồm source integrity, quyết định pin, ảnh 8 hướng, video native N/NE/E/SE/S, hurt/death và NPC. Movie Maker xuất 120 frame/time step 60 FPS, không chứng nhận FPS gameplay thực. PCK/shipping, thay renderer actor trong gameplay và toàn bộ thư viện vẫn chưa hoàn tất.

Ưu tiên tiếp tục: bốn góc walk/interact Người Giữ Thuyền; locomotion/turn/đòn thứ hai Cá Linh; hành động Rễ Nước/Kẻ Rình Bờ; body choreography/VFX 30 kỹ năng; đồng thời giữ hàng đợi map/UI/icon theo asset plan chung. Mục tiêu đầy đủ thư viện vẫn active.
