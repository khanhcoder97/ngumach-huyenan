# Gói 50 sheet kỹ năng Thạch Chùy

Ngày 18/11/2026. Gói đủ 30 sheet nhân vật từ sáu kỹ năng ở năm hướng gốc và 20 sheet VFX tách riêng. Mỗi sheet có 16 hình. Studio đã phát đủ 800 tư thế hoặc pha từ PNG nguồn. Manifest giữ chín phiên bản trước, gồm bản Sơn Thần Giáng Thế hướng Bắc có hình đầu chùy thứ hai tại pha tiếp đất. Phiên bản Bắc hiện tại đã sửa hình này.

## Sơn Thần Giáng Thế

Năm hướng cùng có một nhịp nâng chùy, đặt chùy xuống, trụ người và hồi thế. Các bản Nam, Đông Nam và Đông Bắc dùng điểm đặt chân theo hình vẽ của từng hướng. Ở hai hướng chéo, chùy và tư thế thấp có thể che một giày. Pivot giữ điểm giữa thế đứng thay vì kéo nhân vật về phía giày còn thấy.

Bốn VFX gồm đế báo vùng, phiến đá mọc, vòng duy trì và vòng tan. Pha báo dùng dấu nhỏ dọc mép và để trống tâm. Một sheet phiến đá được đặt tại ba neo. Vòng duy trì xuất hiện dần trong 120 ms khi ba phiến dựng kết thúc. Pha tan bắt đầu trên cùng mép rồi để lại ít bụi. Nhìn từ camera, khoảng mở trước mặt luôn thông thoáng.

Mở `Implementation/Reports/Evidence/Actor_Assembly_20261117a/Sanctuary_TC06_v2/project.json` trong Sprite & VFX Studio. Chọn một trong năm hướng để chỉnh vị trí, neo, tỷ lệ và thời điểm chuyển pha. Ba neo cố định trong khung camera khi hướng nhân vật thay đổi. Bản ghép giữ tư thế cuối cho thời gian xem vòng duy trì. Bản gameplay cần chuyển về idle và dùng trạng thái vùng do máy chủ xác nhận.

## Kết quả kiểm tra

- 50 video nguồn Godot giải mã đủ 9.000 frame. Nhật ký xác nhận đủ 16 chỉ số ảnh ở mỗi nguồn.
- Đã xem đoạn vòng lặp 14 → 15 → 0 → 1 của Thiết Bích, Khiêu Chiến và vòng duy trì Sơn Thần Giáng Thế.
- Năm video ghép v2 giải mã đủ 1.620 frame. Nhật ký từng hướng xác nhận một lần báo vùng, dựng phiến, hai vòng duy trì và một lần tan. Đã xem chín mẫu pha trên mỗi hướng.
- 119 bài kiểm thử công cụ đều đạt. PNG gốc và prompt đi kèm nằm trong `Art_Source/Actor_Library_20261107/Candidates_20261116c/`.

Gói đang ở bước xem nguồn và ghép Studio. Cần căn thêm tư thế trụ pha 11 hướng Bắc, kiểm nối động tác với idle, ba hướng đối diện, camera rộng trên map và thời điểm nhận sự kiện gameplay. Các lỗi hướng và điểm đặt chân của Phá Nham vẫn nằm trong danh sách sửa. Video xuất theo đồng hồ 60 FPS. Hiệu năng gameplay trên map cần được đo riêng.
