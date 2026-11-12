# Thư viện asset — đợt 20261112d

Tiếp tục sprite chibi nguyên khối do chủ dự án chốt. Tạo bằng `image_gen` tích hợp, lưu PNG nguyên byte và prompt thực; không quay lại paperdoll và không dùng code vẽ hoặc chép pose để bù khung.

## Người Giữ Thuyền

Đợt này chọn **8 sheet / 128 ô nguồn**: walk và interact, mỗi action bổ sung N/NE/E/SE × 16. Kết hợp S của đợt c, mỗi action có 5 góc vẽ × 16 = 80 ô nguồn, tham chiếu thành 8 hướng xem bằng chính sách mirror của NPC. SW/W/NW không tính thêm thành ảnh vẽ mới.

| Action | Nguồn và timing | Kết quả kiểm hình ảnh |
|---|---|---|
| idle | N/NE/E/SE cũ + S riêng; 1,00s/16 | Duyệt source/clip đủ hướng sau khi xem trong Godot |
| walk | N/NE/E/SE mới + S cũ; 0,80s/16 | N/S/SE được duyệt; E/NE còn HOLD về nhịp hai chân |
| interact | N/NE/E/SE mới + S cũ; 1,60s/16 | Duyệt source/clip đủ hướng; một lần kéo dây rồi giữ khung cuối |

Nón lá, tóc gáy, ria nhỏ, áo phao vải vàng, áo nâu, đai xanh, quần sẫm, giày nâu, còi, cuộn dây và sào theo identity đã có. Hướng sau che mặt/ngực; tay và dây kéo nằm trước thân, được che theo góc nhìn. Động tác tương tác đặt sào tựa vai/hông, lấy dây, chùng gối, kéo về ngực rồi trả tay về sào/cuộn dây. Không thêm thuyền, mặt đất hoặc neo thế giới vào sprite.

E/SE walk được sửa v2 để làm rõ chân đối ứng; PNG v1 và prompt vẫn được giữ trong lịch sử. SE v2 đạt mức review nguồn. E v2 và NE v1 vẫn khó đọc nhịp chân gần/xa ở kích thước native, nên **không duyệt production**. 16 ô có hash khác nhau chỉ chứng minh không trùng bitmap, không chứng minh dáng đi đúng. Không dùng trạng thái đủ dữ liệu 3/3 trong thư viện để nói cả NPC đã nghiệm thu.

Idle gốc có 72 ô, chỉ 64 ô N/NE/E/SE được binding; hàng 8 ô cuối không được kéo dài hoặc lặp để thành 16. S lấy sheet riêng 16 khung. 8 ô thừa không được tính vào khối lượng hoạt ảnh đã kiểm.

## Studio và kiểm thử

- Giữ chỉnh pivot, tọa độ, tỷ lệ, layer, socket, timing, mốc VFX và xuất JSON/bundle riêng. PNG gốc không bị ghi đè.
- Nhóm walk/interact có 8 clip hướng. Walk lặp; interact mặc định một lần. Có thể bật Loop thủ công để review.
- Native Studio kiểm raw/grouped timing, loop và giữ khung cuối cho toàn bộ 8 hướng của NPC.
- Native actor library kiểm resolve, policy mirror, đi qua 16 pose ở clock 60 bước/s và tương tác không tự phát lại.
- Sửa nhãn frame khi chụp ảnh: trước đây UI cập nhật theo nhịp 0,1s có thể lưu số cũ. Giờ seek khung yêu cầu, xác nhận các sprite đã hiển thị đúng khung, cập nhật timeline/readout rồi mới lưu viewport. Có regression cho readout ảnh tĩnh.
- Video Movie Maker 120 frame ở 60 bước/s là bằng chứng trình bày, **không phải benchmark FPS gameplay**. Thực tế quay offline chậm hơn thời gian thực trên máy này; không dùng để khẳng định game đã đạt 60 FPS.

```powershell
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:NPC_BOAT_KEEPER:idle -Direction N -Play
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:NPC_BOAT_KEEPER:walk -Direction NE -Play -Loop
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:NPC_BOAT_KEEPER:interact -Direction E -Play
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:NPC_BOAT_KEEPER:interact -Direction SE -Frame 15
```

## Phạm vi nghiệm thu và bàn giao

Đợt này thêm 8 quyết định duyệt source: 2 page idle cũ, 2 page walk N/SE mới và 4 page interact mới. S walk/interact đã có quyết định ở đợt c. Hai page walk E/NE có HOLD riêng. Quyết định pin SHA256 PNG và binding SHA256; thay ảnh, rect, hướng, điểm neo hoặc scale qua pipeline sẽ làm mất duyệt và yêu cầu xem lại.

Catalogue actor/skill sau đợt: **92 page qua structure; 47/1008 job đủ nguồn góc; 11 job có đủ góc nguồn đã được kiểm hình ảnh**. Còn 961 job thiếu nguồn, 21 active HOLD và một atlas VFX cũ sai số hàng. Số job được duyệt tăng từ 9 lên 11 nhờ idle/interact Người Giữ Thuyền; walk vẫn chưa được tính là job đã duyệt đủ. Đây không phải toàn bộ khối lượng map/tile/UI/icon/audio.

46 PNG baseline chủ dự án chọn vẫn nguyên SHA256. 89 nguồn runtime đang được chọn khớp byte PNG gốc. Các revision bỏ chọn vẫn giữ nguyên trong lịch sử; không cộng chúng vào 128 ô được chọn của đợt này.

Đường dẫn:

- `Art_Source/Actor_Library_20261107/batch_20261112d.json`: inventory chọn hiện hành.
- `Art_Source/Actor_Library_20261107/Sheets/`: ảnh gốc, gồm cả revision lưu lại.
- `Art_Source/Actor_Library_20261107/Prompts/`: prompt thực và đường dẫn reference trong generation records.
- `Implementation/Reports/Evidence/Actor_Batch_20261112d/`: ảnh tám hướng, 9 video native, 8 dải khung trích từ video, kiểm tra hash, quyết định duyệt/HOLD và log kiểm thử.

Đây là bàn giao nguồn/clip trong thư viện và Studio. Chưa nghiệm thu thay renderer NPC trong gameplay, chuyển tiếp idle→walk/interact, neo dây vào thuyền thật, AI/lịch NPC, PCK/shipping hoặc toàn bộ game. Tiếp tục sửa walk E/NE và độ khớp chuyển clip, rồi hoàn thiện locomotion/đòn thứ hai Cá Linh, action Rễ Nước/Kẻ Rình Bờ và body/VFX kỹ năng. Mục tiêu thư viện đầy đủ vẫn đang thực hiện.
