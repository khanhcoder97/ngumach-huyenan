# 20261113j — Chạy, combo và tương tác của Ảnh Đao

Đợt này giao **21 sheet / 336 pose nguồn**, gồm chạy, combo nhát 2, combo nhát 3 và tương tác ở năm góc nguồn; thêm bản sửa đi ngang E. Đã xem toàn bộ sheet gốc và ảnh mẫu thời gian xuất trực tiếp từ Godot, duyệt **21 nguồn** theo SHA PNG và binding. Kiểm nguồn khép lại ngày 14/11/2026. Giữ kiểu chibi nguyên khối đã chốt; Studio tiếp tục phục vụ chỉnh tay.

| Action | Góc nguồn | Pose/góc | Nhịp xem nguồn |
|---|---|---|---|
| run | N, NE, E, SE, S | 16 | 0,64 s; 40 ms/pose |
| basic_attack_02 | N, NE, E, SE, S | 16 | 0,60 s; 37,5 ms/pose |
| basic_attack_03 | N, NE, E, SE, S | 16 | 0,60 s; 37,5 ms/pose |
| interact | N, NE, E, SE, S | 16 | 1,60 s; 100 ms/pose |
| walk, bản sửa | E | 16 | 0,80 s; 50 ms/pose |

SW/W/NW tham chiếu lật SE/E/NE theo chính sách class hiện hành; không tính là góc vẽ riêng. Thời gian trên phục vụ trình bày và authoring, không tự quyết hit window, vận tốc server, hồi chiêu, nhặt đồ hoặc sát thương.

## Nội dung và các bản sửa

Chạy có hai pha tiếp xúc đối chân 0/8, chân co/vươn và pha bay; tay phải giữ một thanh đao thấp. Hai nhát combo bổ sung là một lần đảo cổ tay và một lần chém ngược, mỗi clip có lấy đà, ra đòn, hồi thế. Góc sau có thể che khuất lưỡi đao phía trước thân khi lấy đà; tay trái trống vẫn đọc được. Tương tác gồm một lần đưa tay trái, cúi/nghiêng và thu về; không vẽ sẵn vật nhặt vào tay.

Chọn run SE v2, combo nhát 3 SE/N v2. Ba bản trước giữ trong lịch sử: chạy SE chưa rõ đảo chân, nhát 3 SE sai đường chém/thêm sáng, nhát 3 N dễ đọc nhầm đao sang tay trái. Tổng **24 PNG đã sinh**, 21 trang chọn, ba trang bị thay; PNG/prompt đều được giữ. Không nối hoặc nhân bản tám pose thành mười sáu.

Bản walk E mới đã kiểm pha chân gần/xa 0/8 và đi qua 4/12. Dữ liệu căn ảnh mới gỡ hiện tượng root đổi ngang theo chiếc giày thấp hơn. E và W lật được gỡ HOLD sau review; nguồn E đợt I và hồ sơ lỗi cũ vẫn giữ nguyên trong lịch sử.

## Căn ảnh và giới hạn của phép đo

PNG gốc và bản runtime khớp byte. Công cụ chỉ đọc ảnh, ghi chiều cao tham chiếu cố định và mốc gắn cho từng frame. Chạy/đi ngang dùng mốc đầu để loại trừ lệch đóng gói trong atlas, kết hợp đường mốc chân ảo giữa hai pha tiếp xúc; chân đang co trên không không kéo root lên. Mốc vàng trong phòng xem là root ảnh, không phải mặt phẳng vật lý của mọi điểm trên sprite.

Hai nhát combo và tương tác dùng vùng giày nâu tím của cả hai chân để căn ngang, giữ chuyển động cúi đầu/nghiêng thân đã vẽ. Bộ lọc loại màu thép ấm của lưỡi đao; không ép đầu đứng yên trong clip tương tác. Kiểm vùng tóc liên thông còn giúp tránh lấy tay/đao giơ cao làm sai số đo đầu. Sau sửa, walk E có độ đổi mốc tóc ngang tối đa khoảng **0,65 px giữa hai pose**, ở cỡ thân tham chiếu 100 px; trước sửa khoảng **16,22 px** với cùng cách đo. Đây là chẩn đoán căn ảnh, không đo độ mượt toàn thân hoặc FPS gameplay.

`body_registration_20261113j.json` giữ recipe, landmarks, hash và toàn bộ pivot. Hai lần căn ảnh bị thay có video/metadata riêng ở `Superseded_Attachment_01/02`, không còn lẫn trong selection. Không chuyển kết quả định lượng của chúng thành duyệt chất lượng.

## Phòng xem và Studio

```powershell
ClientGodot/Run_Actor_Library.ps1 -MobilityReview
ClientGodot/Run_Actor_Library.ps1 -MobilityReview -Test -SkipBuild
ClientGodot/Run_Art_Studio.ps1 -Entry class_anh_dao_run_se -Play -Loop
```

Chuỗi tám hướng dài 8,84 giây: đứng → đi → chạy → đứng → ba nhát combo → đứng → tương tác → đứng. Có dừng/phát, phát lại, tốc độ và mốc chân. Nhãn chờ duyệt/HOLD lấy từ bản ghi nguồn hiện hành, không khóa cứng E/W. Profile cũ `-LocomotionReview` 4,4 giây vẫn giữ.

Studio có các entry của từng hướng để tua pose, chỉnh timing, layer, pivot/vị trí và xuất JSON riêng. Dữ liệu chỉnh tay không ghi đè PNG đã chốt. Mỗi nguồn đã xem cả trong Studio, lưới tám hướng và chuỗi nối; ảnh crop vùng canvas phục vụ soi ở tỷ lệ pixel native, không xuất thành asset thay thế.

## Kết quả bàn giao

- 229 pin nguồn/binding có trước và 268 payload page không bị thay giữ nguyên.
- Thêm 21 pin, tổng 250; 46 PNG cũ chủ dự án chọn giữ nguyên SHA.
- 289 page qua cấu trúc; 286 PNG runtime khớp nguồn. Một VFX Kiếm Trận cũ vẫn bị loại cấu trúc và giữ hồ sơ riêng.
- 27 video chọn, gồm chuỗi 600 frame và 26 video 180 frame; thêm 25 video căn ảnh cũ để đối chiếu. Giải mã được kiểm độc lập.
- 16 inventory cập nhật theo catalogue hiện hành. Inventory đợt I nay còn 14 nguồn đang chọn vì walk E đã được thay; báo cáo I vẫn giữ số 15 nguồn đã bàn giao tại thời điểm đó.
- 82 bài Python đạt; build Godot .NET không lỗi/cảnh báo. Native library đạt 17.800 phép kiểm; Studio 86.814 phép kiểm / 359 entry; chuỗi mobility 9.029, locomotion cũ 4.367, phản ứng Ảnh Đao 3.034.
- Log build, self-test, `source_native_review.json`, `native_media_audit.json`, `delivery_audit.json` và hồ sơ bảo toàn nằm trong `Implementation/Reports/Evidence/Actor_Batch_20261113j`.

Các movie xuất offline 60 bước/giây và kiểm việc đi qua pose nguồn; chúng **không chứng nhận gameplay đạt 60 FPS**. Đợt này không thêm component VFX mới hoặc tự thay toàn bộ renderer gameplay.

## Phần còn lại

Ảnh Đao hiện **16/16 action đủ hướng đã duyệt source**: đứng, đi, chạy, ba nhát thường, sáu skill, trúng đòn, ngã, né và tương tác. Đây là mốc đủ nguồn hoạt ảnh cơ bản, chưa phải nghiệm thu class hoàn chỉnh: còn ghép skill/VFX nhiều pha, chuyển thế, hướng mục tiêu, combat/network và kiểm hiệu năng trong gameplay.

Toàn thư viện hiện có **75/1028 job đủ nguồn cấu trúc**, **48 job đủ hướng đã duyệt source**, **953 job chưa đủ nguồn**. Còn 17 page HOLD nhận vào catalogue, cùng một bản Kiếm Trận bị loại cấu trúc. Các class khác, quái/boss/NPC, biến thể ngoại trang, môi trường và UI vẫn tiếp tục sản xuất. Không dùng số sheet hoặc số test để suy ra toàn game đã hoàn thành.
