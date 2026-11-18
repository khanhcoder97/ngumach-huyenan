# Thạch Chùy · Hoạt ảnh tám hướng

Đã bổ sung hướng Tây, Tây Nam và Tây Bắc cho sáu kỹ năng Thạch Chùy. Mỗi hướng dùng một sprite sheet 4×4 riêng với 16 tư thế. Tóc, giáp, tay và chùy nằm trên cùng sprite. Mỗi sheet có điểm đặt chân riêng cho từng tư thế. Với các góc chùy che giày, điểm neo dùng thắt lưng làm mốc ngang và đế giày làm mốc cao độ để hạn chế trượt thân khi chuyển khung.

| Ô | Kỹ năng | Nhịp động tác | Thời lượng sheet |
| --- | --- | --- | ---: |
| 1 | Trấn Sơn | Lấy đà qua vai, nện chéo, thu chùy | 960 ms |
| 2 | Chấn Địa | Nâng chùy qua đầu, nện xuống, đứng dậy | 1.120 ms |
| 3 | Thiết Bích | Chống chùy, hạ trọng tâm, trở lại tư thế thủ | 960 ms |
| 4 | Khiêu Chiến | Gồng người, hô, hồi thế | 800 ms |
| 5 | Phá Nham | Ghì vai, lao thấp, ghìm chân | 800 ms |
| 6 | Sơn Thần Giáng Thế | Gồng chùy, chống xuống, nhấc chùy | 1.280 ms |

Các sheet Tây của Thiết Bích và Khiêu Chiến dùng bản v2. Lịch sử v1, PNG gốc và prompt ở `Art_Source/Actor_Library_20261107/Candidates_20261119b/`. Năm hướng đã có của mỗi kỹ năng lấy từ gói `20261116c`. Tổng cộng có 48 sheet thân riêng với 768 tư thế, gồm 18 sheet mới với 288 tư thế. Clock 60 FPS dùng để quay và kiểm trình tự phát trong Godot. Thời lượng từng tư thế vẫn lấy từ manifest.

## Mở trong Sprite & VFX Studio

Mở `Implementation/Reports/Evidence/Actor_Batch_20261119b/Candidate_Studio/<ID>/project.json` để chỉnh điểm neo và thời lượng từng tư thế. ID theo mẫu `class_thach_chuy_skill_06_sw`. Video và ảnh 16 tư thế cùng ID nằm ngay trong thư mục bằng chứng.

Mở `Sanctuary_TC06_v3/project.json` trong thư mục bằng chứng để chỉnh Sơn Thần Giáng Thế. Chọn hướng trên timeline. Thân nhân vật, vòng báo, ba phiến đá, vòng duy trì và pha tan là các lớp riêng. Điểm neo của ba phiến đá chỉnh được độc lập. Vòng mở hướng về cạnh dưới màn hình ở cả tám hướng, để người chơi luôn thấy khoảng trống trước nhân vật.

| Mốc trong clip Studio | Thời điểm |
| --- | ---: |
| Bắt đầu vòng báo | 0 ms |
| Ba phiến đá xuất hiện | 560 ms |
| Vòng duy trì bắt đầu đậm lên | 920 ms |
| Hoàn tất chuyển lớp phiến đá sang vòng | 1.040 ms |
| Vòng bắt đầu sụp và tan | 4.120 ms |
| Hết hiệu ứng | 4.760 ms |

## Kiểm chứng và phạm vi

- `native_source_audit.json` đối chiếu 48 sheet thân và 18 video mới. Mỗi video giải mã 180 khung và trace chạy đủ 16 tư thế theo thứ tự.
- `Sanctuary_TC06_v3/native_audit.json` kiểm tám hướng ghép. Mỗi video giải mã 324 khung ở 60 FPS. Trace ghi đủ 16 tư thế của lớp thân đang hiện, đủ 16 tư thế từng lớp hiệu ứng, và hai chu kỳ vòng duy trì.
- Đây là gói nguồn và trình diễn Studio. Năm kỹ năng đầu có hoạt ảnh đã đăng ký và thư viện VFX riêng. Sơn Thần Giáng Thế có bản ghép tám hướng. Các kỹ năng Thạch Chùy trong gói này đang chờ tích hợp vào trận đấu và kiểm tra nhịp hit, phản hồi HUD, cue âm thanh cùng hiệu năng trong bản đồ chơi.
