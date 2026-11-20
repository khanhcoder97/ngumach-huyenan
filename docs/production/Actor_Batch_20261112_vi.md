# Đợt asset chibi, animation và VFX — 12/11/2026

## Hướng đã chốt

Chủ dự án chốt quay lại sprite sheet chibi nguyên khối và yêu cầu tiếp tục phần asset/animation/VFX còn thiếu. Giữ nét của các sheet trước, không quay lại nhân vật base/paper-doll mới. 46 PNG cũ vẫn nguyên byte theo snapshot đã đối chiếu; bản sửa dùng tên version mới. Chuẩn 16–20 hình nguồn/hành động/hướng, renderer mục tiêu 60 FPS giữ nguyên.

## Bàn giao đợt này

14 sheet được chọn, 568 ô nguồn: **560 ô được gắn thành 35 chuỗi nguồn × 16 khung**, 8 ô dư của Người Giữ Thuyền được giữ trong PNG nhưng không đưa vào chuỗi hoặc lặp cho đủ 16. Các con số ô/hash không tự chứng nhận giải phẫu hoặc mọi pose đều tốt.

| Nhóm | Nguồn mới | Trạng thái |
|---|---:|---|
| Minh Kiếm — trúng đòn | 80 ô / 5 góc vẽ | 8 hướng xem; 3 góc lật theo policy cũ |
| Minh Kiếm — né | 64 ô + S 16 ô | Ghép đủ 5 góc vẽ / 8 hướng xem; không chép pose bù hướng |
| Minh Kiếm — gục | 64 ô + NE 16 ô | Ghép đủ 5 góc vẽ / 8 hướng xem; cuối chuỗi nằm yên |
| Thạch Chùy — đánh thường | 80 ô | Thay candidate bị cắt/đè khung; giữ bản cũ trong lịch sử |
| Cá Linh — di chuyển | 80 ô | 5 góc nguồn / 8 hướng xem, tiếp tục kiểm nhịp và viền |
| Rễ Nước — idle S | 16 ô | Pilot hướng S; các hướng khác vẫn thiếu |
| Kẻ Rình Bờ — idle S | 16 ô | Pilot hướng S; các hướng khác vẫn thiếu |
| Người Giữ Thuyền — idle | 72 ô + S 16 ô | 80 ô gắn chuỗi, 8 ô dư không dùng; 8 hướng xem |
| Cung kiếm Kiếm Trận | 16 ô | Thành phần đã kiểm trong Godot, dùng vào runtime Kiếm Trận |
| Mũi tên lá Khóa Mạch | 16 ô | Thành phần projectile để chỉnh trong Studio; chưa gồm dấu rễ/buff |
| Vết nứt Trấn Sơn | 16 ô | Thành phần decal để chỉnh trong Studio; chưa là toàn bộ kỹ năng |

Danh mục chính xác gồm tên PNG, prompt thực, hash, file runtime, hướng vẽ/lật và số ô: `Art_Source/Actor_Library_20261107/batch_20261112.json`. Ảnh gốc ở `Sheets`, prompt ở `Prompts`; dùng **image_gen tích hợp**, không dùng script để vẽ lại bitmap hoặc nhân pose. Các bản thử nền giả/cung lỗi vừa bị thay được chuyển sang `Rejections` và ghi `generation_history.json`.

## Runtime Kiếm Trận

`SkillVfxPlayer` chỉ chọn cung mới khi page `sk_mk_03_arc_component` được approved. Đã xem silhouette/alpha/pivot trong Godot và ghi nghiệm thu **thành phần hình ảnh**, không approve toàn bộ body animation của kỹ năng hoặc atlas Kiếm Trận cũ bị lỗi.

Ba instance dùng cùng nguồn 16 khung, xoay tương đối 0/−35/+35 độ; bắt đầu 0/0,12/0,26 giây, mỗi cung sống 0,20 giây, đỉnh hình ảnh ở 0,10/0,22/0,36 giây. Cung cuối scale 1,25. Nguyên tắc mỗi cung dưới 0,22 giây giữ nguyên. Cổng cast token, duplicate suppression, cancel và ngân sách 24/8 sprite vẫn hoạt động. Không gọi hoặc đổi damage/CD/MP/hitbox/quest/server grant.

Nguồn 16 khung không có nghĩa mọi khung đều xuất hiện trên từng màn hình khi hiệu ứng chỉ dài 0,20 giây; renderer lấy mẫu theo thời gian thực, không tạo pose giả hoặc sửa FPS đếm. Hai thành phần còn lại chưa được đưa tự động vào class gameplay.

## Xem và chỉnh tay

Studio thêm nhóm actor/action ghép các sheet hướng vào một project. Các page nguồn đơn vẫn mở riêng được. Nhãn `[Nhóm hướng]` không có nghĩa entity đã đủ mọi action. Hướng lật vẫn hiện nhãn rõ; hướng thiếu không được tự lấy ảnh hướng khác. Nguồn VFX dùng pivot cố định tại tâm ô để không giật khi hình co/dãn/fade.

```powershell
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:CLASS_MINH_KIEM:dodge
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:CLASS_MINH_KIEM:death -Direction S -Frame 15
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:NPC_BOAT_KEEPER:idle
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry demo:kiem_tran -Play -Loop
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry sk_lc_01_projectile_component
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry sk_tc_01_crack_component
```

Các clip hurt/death/dodge/attack mặc định one-shot trong Studio, có thể bật loop để soi chuyển tiếp. Demo Kiếm Trận có 3 layer, 20 ô timing tham chiếu một sheet cung 16 hình; không được tính thành 20 pose nhân vật hoặc 48 ảnh cung mới. JSON xuất từ Studio vẫn `PRESENTATION_AUTHORING_ONLY`, không tự thay actor trong client. Đóng/mở lại Studio bằng launcher để nạp danh sách mới nếu cửa sổ cũ còn đang chạy; bản chỉnh người dùng không bị ghi đè.

## Kiểm tra và phạm vi còn lại

Pipeline biết xử lý các block hướng khai báo riêng. Một atlas 4 hướng không được tính hoàn chỉnh khi còn thiếu hướng S; chỉ khi có sheet S thật mới khép được job. VFX có nhiều cụm hạt rời được dùng lưới 4×4 đã xem xác nhận, vẫn kiểm frame không rỗng, khoảng cách mép và hash; không nới quy tắc để nhận atlas sai số người/quái. Có 8 test hồi quy về coverage hướng, mirror, repair và component.

Qua structure: 35 → 49 page; **job có đủ góc nguồn yêu cầu: 32 → 38**. Toàn game vẫn còn **970/1008 job thiếu cấu trúc/nguồn**. Ba atlas cũ lỗi và 15 HOLD về chất lượng vẫn ghi đúng; không gọi việc chọn phong cách là duyệt toàn bộ thư viện. 13/14 nguồn mới chưa tự mở cổng production; cung kiếm được approve ở phạm vi component, không khép job full skill.

Ưu tiên tiếp theo: hoàn chỉnh các hướng Rễ Nước/Kẻ Rình Bờ; chuỗi combat Cá Linh (báo đòn–đánh–hồi–bị thương–gục); walk/interact Người Giữ Thuyền; body choreography và VFX thành phần của 30 kỹ năng. Không dùng ảnh idle đổi tên thành attack, không lặp 8 pose cho đủ 16, không thay source bị thiếu bằng scale/tween.

Bằng chứng native và log: `Implementation/Reports/Evidence/Actor_Batch_20261112`. Video né là bản dựng review 120 khung/60 FPS xuất offline từ Godot, **không phải benchmark FPS gameplay**. Ảnh VFX runtime đứng khung được ghi rõ không đo FPS.
