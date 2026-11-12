Thư viện sprite chibi nguyên khối còn thiếu nhiều action và VFX. PR bổ sung combat Cá Linh đủ hướng, idle/interact Người Giữ Thuyền, và sáu action của Rễ Nước: idle, ba pha roi rễ, hurt, death. Mỗi hướng nguồn có16 khung; SW/W/NW dùng mirror khi policy cho phép, không tính thành ảnh vẽ mới. Walk NPC E/NE vẫn HOLD.

Đợt mới nhất f có15 sheet chọn/240 ô nguồn:10 sheet hurt/death Rễ Nước và5 component VFX riêng cho Minh Kiếm, Ảnh Đao, Huyền Bút, Thạch Chùy, Linh Cung. Khóa Mạch đã sửa điểm nối vòng bằng nguồn v2; bụi Trấn Sơn neo tại chân. Các bản trước sửa/nguồn/prompt được giữ. Đây là thành phần hình ảnh, chưa khép toàn timeline kỹ năng hoặc tích hợp gameplay.

Studio giữ pivot/layer/socket/timing/VFX, undo và xuất JSON/bundle với PNG gốc. Profile preview mới nằm trong metadata, được pin cùng binding SHA256; đổi timing/loop phải kiểm lại. Prompt quái bỏ động tác gục/di chuyển người không phù hợp giải phẫu. Cảnh review có đủ hurt/death và vẫn giữ action thiếu ở trạng thái thiếu.

Validation: .NET8 build0 warning/error; Godot import;33 Python tests; library12,799 assertions; Studio58,476 assertions/170 entries; cue6 và component Kiếm Trận cũ14 assertions.46 PNG baseline nguyên SHA256,120 nguồn runtime chọn khớp byte. Đợt f có9 video native chọn cùng ảnh/dải mẫu và decode/hash audit; video60 bước/s offline không chứng nhận gameplay60FPS.

Catalogue hiện123 page structure,52/1008 job đủ nguồn,16 job đủ nguồn kiểm source; còn956 job thiếu,21 HOLD và atlas full VFX cũ sai hàng. Component không tính thành full skill. Chưa nghiệm thu toàn actor, gameplay renderer/AI/hit/collision/LowFX/PCK. Map/UI/icon/audio và các phần thiếu khác tiếp tục.

Chi tiết: docs/production/Actor_Batch_20261112f_vi.md; inventory Art_Source/Actor_Library_20261107/batch_20261112f.json; evidence Implementation/Reports/Evidence/Actor_Batch_20261112f/. Các đợt a–e và lịch sử kiểm riêng giữ nguyên.
