# Thạch Chùy C — mốc 25 nguồn, cập nhật 17/11/2026

Đã tạo và đăng ký riêng 25 sheet, tổng 400 pose nguồn: ba kỹ năng Trấn Sơn, Chấn Địa, Thiết Bích ở năm hướng gốc cùng 10 component VFX. Đây là một mốc đang phát triển của gói 50 sheet Thạch Chùy. Thư viện đầy đủ của game còn các hành động khác, lớp nhân vật khác, quái, boss, NPC, bản đồ và UI.

## Nguồn và các sửa đổi đã kiểm tra

Ảnh dùng nét chibi nguyên khối đã chọn, mỗi sheet 4×4 với 16 pose. Công cụ tạo ảnh tích hợp tạo artwork; công cụ Python chỉ đọc ảnh, sao chép nguyên byte và ghi metadata. Không sinh pose bằng biến dạng hay nhân đôi chu kỳ tám frame.

Chấn Địa Bắc v2 sửa tư thế tay/chùy xuất hiện sai ở lưng. Chấn Địa Nam v2 giữ đầu chùy bên trái màn hình ở tư thế đầu/cuối, khớp Trấn Sơn và Thiết Bích. Bụi lắng Trấn Sơn v2 thay cụm đá lớn bằng bụi mỏng. Bốn phiên bản đã thay thế vẫn nằm trong lịch sử nguồn.

Đăng ký chân tách khỏi đầu chùy khi chùy nằm thấp hơn giày. Các trường hợp màu giày tối hoặc thắt lưng bị che dùng pivot riêng gắn SHA của đúng phiên bản PNG. Vết nứt dùng tâm giao sáng; bụi dùng baseline footprint; phiến giáp gain/sustain dùng tâm hình. Mỗi thay đổi đăng ký được kiểm tra lại bằng bản quay Godot.

## Bằng chứng hiện tại

| Kiểm tra | Kết quả |
| --- | --- |
| Nguồn được chọn / lịch sử | 25 / 4 phiên bản cũ |
| Pose nguồn đã xem trong native | 400 |
| Project Studio / video native | 25 / 25 |
| Video giải mã | 25 × 180 frame |
| Mối nối loop thực tế | sustain, 14 → 15 → 0 → 1 |
| Test công cụ | 119 qua |
| Phê duyệt nguồn C đưa vào runtime | 0 |

Ghi chú thủ công gắn mã băm PNG, project, video và ảnh 16 pose. Đổi PNG, pivot, timing hoặc project sẽ làm bằng chứng cũ không còn khớp. Công cụ chuẩn bị kiểm tra các nguồn trước khi ghi project; chế độ xử lý từng nguồn chỉ giữ cache còn khớp metadata hiện hành. Test đã bắt và sửa trường hợp cache giữ timing cũ.

`checkpoint_audit.json` kiểm tra lại cấu trúc và liên kết artifact. `native_media_audit.pilot.json` kiểm tra nhận dạng video, trace pose và giải mã. Hai loại kiểm tra này hỗ trợ ghi chú hình ảnh; việc duyệt toàn bộ gameplay vẫn còn mở. Catalogue và thư viện runtime hiện hành không thay đổi trong mốc này.

## Công việc đang tiếp tục

Giáp Thiết Bích dùng một component phiến giáp tại ba socket độc lập: vai, lưng, gối. Cần ghép bốn pha trên nhân vật, căn footprint lớp nứt và căn end với sustain; hiện đã ghi rõ hai điểm chờ này. Tiếp tục kiểm tra che khuất theo tám hướng, chuyển động tác với idle và tỷ lệ ở camera rộng. Studio hiện tự fit từng project nên chiều cao trên hai ảnh chụp khác project không đủ để kết luận chúng đã khớp tỷ lệ gameplay.

Còn 15 sheet nhân vật của ba kỹ năng sau và 10 VFX trong gói 50 nguồn. Video xuất bằng clock 60 FPS phục vụ kiểm tra; FPS gameplay thực tế, va chạm và cue server cần kiểm tra ở bản tích hợp.

Nguồn, prompt và 50 job portable: `Art_Source/Actor_Library_20261107/Candidates_20261116c/`. Project và bằng chứng: `Implementation/Reports/Evidence/Actor_Batch_20261116c/`. Các bản thử đăng ký trước được giữ tại máy làm việc để đối chiếu; gói Git chứa nguồn/lịch sử, project hiện hành và bằng chứng hiện hành.
