# Bàn giao asset 20261112f

15 sheet chọn, 240 ô nguồn mới theo sprite chibi nguyên khối: Rễ Nước hurt/death N/NE/E/SE/S × 16, thêm 5 component VFX Phản Quang, Huyết Nguyệt, Mực Triều, Trấn Sơn và Khóa Mạch. Ba hướng đối xứng dùng lật theo policy, không tính thêm ảnh vẽ. PNG gốc và prompt thực được giữ.

Chi tiết sử dụng, thời lượng trình bày và phạm vi: [đặc tả đợt f](../../docs/production/Actor_Batch_20261112f_vi.md). Inventory: `Art_Source/Actor_Library_20261107/batch_20261112f.json`.

Sửa hai vấn đề qua kiểm native: Khóa Mạch v1 bị nhảy cỡ ở điểm nối vòng, đã chọn nguồn v2; bụi Trấn Sơn nằm dưới điểm neo, đổi metadata sang neo chân, không sửa PNG. Nguồn và bằng chứng trước sửa được giữ. Prompt kế hoạch quái cũng bỏ mẫu gục/chuyển động người khi không đúng giải phẫu.

Studio đọc profile preview có thời lượng và chế độ phát, pin binding bao gồm profile mới. Đổi profile cần kiểm lại; pin nguồn cũ không đổi. Tool tiếp tục chỉnh tay pivot, layer, tọa độ, socket, timing/VFX và xuất JSON/bundle. Không thay lại hướng paper-doll.

Kiểm tra: build .NET 8 0 warning/error; Godot import; 33 Python tests; native library 12.799 assertions; Studio 58.476 assertions/170 entries; cue guard 6, component Kiếm Trận cũ 14. Baseline 46 PNG giữ nguyên; 120 nguồn runtime chọn khớp byte. Bằng chứng ở `Implementation/Reports/Evidence/Actor_Batch_20261112f/`: 9 video native chọn, ảnh/dải mẫu, lịch sử sửa, quyết định/pin và log. Video offline 60 bước/s không phải chứng nhận gameplay 60 FPS.

Trạng thái catalogue: 123 page structure, 52/1008 job đủ nguồn, 16 job đủ nguồn kiểm source; 956 job thiếu, 21 HOLD, một atlas VFX cũ sai hàng. Rễ Nước hiện có 6/12 action đủ nguồn; component chưa khép toàn kỹ năng. Chưa nghiệm thu gameplay renderer/AI/hit/collision/LowFX/PCK hoặc toàn thư viện.
