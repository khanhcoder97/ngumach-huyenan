# Bàn giao thư viện asset — 20261112c

Tiếp tục mục tiêu thư viện đầy đủ; mục tiêu vẫn active. Gói này có **23 sheet được chọn / 368 ô nguồn**: 20 sheet góc combat Cá Linh, revision NE Rễ Nước và walk/interact S Người Giữ Thuyền. PNG dùng `image_gen` tích hợp; prompt, tham chiếu, bản thử bị loại và hash được lưu. Không vẽ bitmap bằng code, không chép pose cho đủ 16.

Năm action Cá Linh có 5 góc nguồn/8 hướng xem khi ghép S đã có: telegraph_01, attack_01, recovery_01, hurt, death. Tổng riêng năm action là 400 ảnh nguồn. NPC mới chỉ S, không được tính đủ hướng. Source Rễ Nước NE mới thay binding cũ nhưng giữ nguyên PNG cũ trong lịch sử. Inventory b hiện là 12 page do revision chuyển sang c; báo cáo b ban đầu vẫn mô tả đúng lần giao 13 sheet khi đó.

Các lỗi đã sửa gồm atlas nhiều góc xoay sai/attack mở hàm thay vì khép, miệng mở ở frame đầu hurt NE, đuôi cuộn lại khi nối recovery N, chân NPC lặp cùng bên, nền trắng, và neo ở đuôi làm thân cá trượt. Cá Linh dùng đăng ký tâm thân bạc và scale trục dài; PNG không bị thay đổi. Tâm thân trước sửa lệch khoảng 9,70×14,63px ở review 88px; attack→recovery N sau sửa lệch kích thước thân khoảng 2%. Số đo không thay thế nghiệm thu pose.

32 source page được xem sheet gốc và native: 25 combat Cá Linh, 5 idle Rễ Nước, 2 NPC S. Quyết định pin cả PNG SHA256 và binding SHA256. Scope là source/clip hình ảnh, không phải actor, encounter, gameplay hoặc shipping. Native source evidence cụ thể được liệt kê trong `visual_decisions.json`.

| Kiểm tra | Kết quả |
|---|---|
| .NET 8 build | 0 warning / 0 error |
| Godot import | Thành công |
| Native actor library | 11.934 assertions; 16 frame × 8 hướng × 5 action, one-shot, texture, gate |
| Native Studio | 49.990 assertions / 126 entry-group |
| Python regressions | 20 test: coverage, scale, core registration, approval pin |
| Runtime VFX component | 14 assertions đạt; giữ ba nhịp cung cũ |
| Movie/benchmark guard | Từ chối kết hợp; không xuất benchmark JSON giả |
| PNG baseline | 46/46 SHA256 không đổi |
| Runtime selected source | 81/81 khớp byte PNG gốc |
| Batch inventories | Cả a/b/c tái lập được; chưa coi library đầy đủ |

CarplingCombatReview thêm selector/CLI tám hướng và vừa viewport 1280×720. Header thư viện đếm clip đầy đủ hướng, tránh nguồn S-only bị ghi như hoàn chỉnh. Video offline nhận theo `Engine.GetWriteMoviePath()` và ghi rõ không đo FPS; không cho dùng Movie Maker cùng benchmark thực. Studio vẫn chỉnh pivot/tọa độ/timing/layer và xuất JSON riêng.

Video native N/NE/E/SE/S, hurt/death tám hướng, idle Rễ Nước và NPC được xuất 120 frame/time step 60 FPS rồi ffmpeg mã hóa H.264. Đây không phải benchmark 60 FPS gameplay. Ảnh concept không được dùng thay screenshot engine.

Coverage actor/skill catalogue: **84 structure page; 45/1008 job đủ góc nguồn; 9 job toàn góc có nghiệm thu nguồn**. Còn 963 job thiếu nguồn và 19 active HOLD; chưa tính hết các bộ map/tile/UI/icon/audio khác. NPC còn bốn góc walk/interact, Cá Linh còn locomotion/turn/đòn thứ hai và nghiệm thu actor, Rễ Nước còn các action khác, full VFX atlas cũ còn lỗi hàng. Shipping/PCK và việc thay toàn bộ actor renderer trong gameplay chưa nghiệm thu. Không đánh dấu mục tiêu đầy đủ thư viện hoàn tất.

Chi tiết: `docs/production/Actor_Batch_20261112c_vi.md`. Manifest: `Art_Source/Actor_Library_20261107/batch_20261112c.json`. Bằng chứng: `Implementation/Reports/Evidence/Actor_Batch_20261112c/`.
