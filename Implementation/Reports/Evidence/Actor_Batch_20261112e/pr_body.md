Thư viện còn thiếu nhiều góc/action và điểm neo theo bounding box có thể kéo thân khi ngọn roi duỗi. PR tiếp tục sprite chibi nguyên khối 16 khung nguồn/hướng: combat Cá Linh đủ hướng, idle/interact Người Giữ Thuyền, và idle + ba pha roi rễ của Rễ Nước. Walk NPC E/NE còn HOLD, không tính là job source đã duyệt đủ.

Đợt mới nhất e: 16 sheet chọn /256 ô nguồn (15 roi rễ +1 vòng gợn). Rễ Nước dùng chiều cao thân trung tính và cùng offset lõi rêu/idle theo góc; source PNG không đổi. Vòng gợn rỗng 16 khung chỉ ghép trong cảnh review, hiện 0,70s báo đòn rồi tắt, không biểu diễn vùng hit. Cung Kiếm Trận 16-frame đã tích hợp trình bày từ các đợt trước; không đổi damage/CD/MP/server/AI.

Studio giữ chỉnh tay pivot/layer/socket/timing/VFX, xuất JSON/bundle và PNG gốc. Tool thư viện mở được combat review theo actor/hướng; ô thiếu giữ thiếu. Source approval pin cả PNG SHA256 và binding SHA256, lưu lịch sử khi đổi đăng ký. Capture đồng bộ nhãn/khung thực và Movie Maker không được coi như benchmark FPS.

Trạng thái: 46 PNG baseline không đổi, 105/105 nguồn runtime chọn khớp byte. Catalogue có 108 page structure, 50/1008 job đủ góc nguồn, 14 job đủ góc kiểm source; còn 958 job thiếu, 21 HOLD và full VFX atlas cũ sai hàng. Tổng này chưa bao phủ hết map/UI/icon/audio. Chưa nghiệm thu toàn actor, gameplay renderer, collision/hit, LowFX gameplay hoặc PCK/shipping.

Validation: .NET 8 build 0 warning/error; Godot import; 26 Python tests; native library 12,495 assertions; Studio 55,963 assertions/153 entries; cue phase guard 6 assertions; VFX component cũ 14 assertions. Đợt e có 10 MP4 native cùng ảnh tám hướng/dải mẫu thời gian và hash. Video 60 bước/s xuất offline, không chứng nhận gameplay 60 FPS thực.

Chi tiết mới nhất: docs/production/Actor_Batch_20261112e_vi.md; inventory Art_Source/Actor_Library_20261107/batch_20261112e.json; evidence Implementation/Reports/Evidence/Actor_Batch_20261112e/. Các gói a/b/c/d và lịch sử riêng vẫn giữ trong PR. Mục tiêu thư viện toàn game tiếp tục thực hiện.
