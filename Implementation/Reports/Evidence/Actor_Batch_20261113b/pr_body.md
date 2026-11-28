Thư viện sprite chibi nguyên khối còn thiếu nhiều action và VFX. PR bổ sung combat Cá Linh đủ hướng, idle/interact Người Giữ Thuyền, 12 action của Rễ Nước và Phản Quang Minh Kiếm. Mỗi hướng nguồn có 16 khung, hướng lật khai báo riêng; walk NPC E/NE còn HOLD.

Đợt mới nhất 20261113b có 18 sheet chọn / 288 ô nguồn: ba pha Chồi Đất × N/NE/E/SE/S và ba component cảnh báo đường, chồi trồi, thu chồi. Low-start clip dùng chiều cao đứng cố định được pin; không phóng tư thế ép thấp về chiều cao đứng. Chênh chiều cao hai điểm nối còn tối đa 6,54px ở cỡ88px; chưa coi là nối silhouette hoàn hảo. Windup0,70s theo thiết kế;0,40/0,60s đánh/hồi là timing review, không đổi4m/1,5×/hitbox.

Combat review thêm biến thể2 với bốn ô lớn, cue xoay tám hướng chỉ trong báo đòn. Spike/retract mới kiểm độc lập, chưa rải dọc hit lane thật. Studio phát sau fit bố cục; giữ chức năng chỉnh tay/chèn component, undo/redo, socket/timing, JSON/bundle. Các đợt trước giữ source, lịch sử kiểm và cơ chế chèn component.

Validation: .NET8 build0 warning/error; Godot import;37 Python tests; native library13.599 assertions; Studio67.078/215 entries. Cue12+20 kiểm phase/frame/region/texture/scale và hướng. Baseline46 PNG nguyên SHA256;158 nguồn runtime khớp byte. Có8 MP4 native chọn,5 lịch sử, ảnh/dải mẫu, pin và decode/hash audit. Video60 bước/s offline không chứng nhận gameplay60FPS.

Catalogue:161 page structure,59/1008 job đủ nguồn,23 job đủ nguồn kiểm source; còn949 job thiếu,21 HOLD cũ và full VFX atlas sai hàng. Rễ Nước12/12 action đủ nguồn chưa nghiệm thu toàn encounter. Component không đóng full skill; map/UI/icon/audio, gameplay renderer/AI/hit/collision/LowFX/PCK tiếp tục.

Chi tiết: docs/production/Actor_Batch_20261113b_vi.md; inventory Art_Source/Actor_Library_20261107/batch_20261113b.json; evidence Implementation/Reports/Evidence/Actor_Batch_20261113b/. Các đợt cũ giữ tài liệu lịch sử.
