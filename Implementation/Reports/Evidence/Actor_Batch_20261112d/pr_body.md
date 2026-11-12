Thư viện vẫn thiếu nhiều hướng/action và các ảnh chưa kiểm cần được chặn khỏi runtime. PR tiếp tục sprite chibi nguyên khối 16 khung nguồn/hướng, giữ 46 PNG baseline nguyên SHA256, bổ sung combat Cá Linh đủ tám hướng, idle Rễ Nước và idle/interact Người Giữ Thuyền đủ hướng nguồn đã kiểm. Walk NPC đã có nguồn nhưng E/NE còn HOLD về nhịp chân; không tính là action production hoàn chỉnh.

Studio giữ chỉnh tay pivot/tọa độ/layer/socket/timing/VFX và xuất JSON cùng PNG gốc. Duyệt nguồn pin cả ảnh và binding, thay đăng ký làm mất duyệt. Cá Linh neo tâm thân thay đuôi; cung Kiếm Trận 16-frame được tích hợp trình bày, không đổi damage/CD/MP. Capture nay xác nhận khung thực và đồng bộ nhãn trước khi lưu; Movie Maker không được dùng như benchmark FPS.

Đợt mới nhất d: 8 sheet chọn /128 ô nguồn; E/SE walk có revision, ảnh cũ được giữ. 8 quyết định duyệt source (gồm 2 idle cũ), 2 walk HOLD. Toàn catalogue: 92 page structure, 47/1008 job đủ nguồn, 11 job đủ hướng được kiểm, 961 job thiếu, 21 HOLD. Nguồn runtime chọn 89/89 khớp byte. Chưa nghiệm thu toàn actor/game, gameplay renderer, PCK/shipping hoặc thư viện map/UI/icon/audio đầy đủ.

Validation: .NET 8 build 0 warning/error; Godot import; 20 Python tests; native Studio 52,314 assertions/134 entries; library 12,119 assertions; VFX component 14 assertions. Bằng chứng gồm ảnh tám hướng, dải pose, 9 video native offline 120 frame/60 bước/s và hash. Đây không phải chứng nhận gameplay 60 FPS.

Chi tiết: docs/production/Actor_Batch_20261112d_vi.md; inventory Art_Source/Actor_Library_20261107/batch_20261112d.json; evidence Implementation/Reports/Evidence/Actor_Batch_20261112d/. Các gói a/b/c có báo cáo và lịch sử riêng trong cùng PR. Mục tiêu thư viện toàn game tiếp tục thực hiện.
