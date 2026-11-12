# Bàn giao asset 20261112d

Bổ sung **8 sheet được chọn / 128 ô nguồn** cho walk và interact N/NE/E/SE của Người Giữ Thuyền, giữ sprite chibi nguyên khối và PNG gốc. `image_gen` tích hợp tạo ảnh; prompt, reference và các revision đều được lưu.

Ghép S cũ, hai action có 5 góc vẽ/8 hướng xem, mỗi góc 16 khung. Idle cũ cũng đã được xem native. Chỉ idle và interact được duyệt đủ góc nguồn; walk E/NE còn HOLD về nhịp chân gần/xa, không được lọt cổng source production. E/SE có revision v2, v1 vẫn nguyên byte trong lịch sử. Không coi đủ 16 ô/hash khác nhau là nghiệm thu dáng đi.

Thêm 8 source approval có pin PNG/binding SHA256, gồm 2 idle cũ, walk N/SE và 4 interact mới. Scope chỉ source/clip, chưa phải gameplay hay actor hoàn chỉnh. Studio giữ toàn bộ chỉnh tay và bundle, không ghi đè ảnh nguồn.

| Kiểm tra | Kết quả |
|---|---|
| .NET 8 build | 0 warning / 0 error |
| Godot import | Thành công |
| Native Studio | 52.314 assertions / 134 entries |
| Native actor library | 12.119 assertions; đủ hướng, 16 pose/clock 60, mirror, one-shot, readout ảnh tĩnh |
| Python | 20 regression tests đạt |
| Bảo toàn baseline | 46/46 SHA256 không đổi |
| Nguồn runtime được chọn | 89/89 khớp byte nguồn |
| Bằng chứng hình ảnh | 9 video native; 8 dải 16 mẫu từ video; ảnh idle/walk/interact tám hướng |

Sửa capture readout để nhãn frame và timeline khớp khung ảnh thực; capture cũng kiểm sprite đã seek đúng trước khi lưu. Video offline 60 bước/s không được coi là benchmark 60 FPS gameplay.

Coverage hiện hành: **92 structure page, 47/1008 job đủ góc nguồn, 11 job đủ góc được duyệt**, 961 job thiếu nguồn, 21 active HOLD; một VFX atlas cũ còn sai hàng. Map/tile/UI/icon/audio và nghiệm thu gameplay/shipping còn trong phạm vi tiếp tục. Mục tiêu đầy đủ thư viện chưa hoàn tất.

Chi tiết: `docs/production/Actor_Batch_20261112d_vi.md`. Inventory: `Art_Source/Actor_Library_20261107/batch_20261112d.json`. Bằng chứng: `Implementation/Reports/Evidence/Actor_Batch_20261112d/`.
