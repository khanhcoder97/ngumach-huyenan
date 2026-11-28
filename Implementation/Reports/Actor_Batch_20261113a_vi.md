# Bàn giao asset 20261113a

**20 sheet chọn / 320 ô nguồn** theo chibi nguyên khối đã chốt: Rễ Nước walk/run/turn và Minh Kiếm skill_01 Phản Quang, mỗi action N/NE/E/SE/S × 16. SW/W/NW dùng lật theo policy, không tính thêm ảnh vẽ. PNG nguồn, prompt thực và bản sao runtime giữ nguyên byte.

Rễ Nước dùng nhịp bò bằng bó rễ ngắn, không thêm chân tay người. Turn là chuyển trọng tâm chuẩn bị đổi heading, giữ góc khai báo. Phản Quang là động tác kiếm chéo thủ trước ngực, không bake cung phép hoặc phản công. Profile toàn động tác xem 0,80s không thay cửa đỡ combat 0,40s.

Studio thêm chèn component 16 khung từ thư viện vào layer/track, giữ texture/regions/pivot/order; hỗ trợ launcher `-Component`. Host dưới 16 ô bị từ chối. Bản chèn trải đều theo timeline host để chỉnh tay, không tự ghép đúng cửa đỡ hoặc giữ thời lượng riêng của component. Danh sách cuộn tới layer mới; nhãn dài không làm tràn panel, ghi chú đầy đủ có trong tooltip/tab Xuất. JSON/bundle, undo/redo, pivot/layer/socket/timing giữ nguyên.

Kiểm tra: .NET8 build0 warning/error, Godot import; 34 Python tests; library13.215 assertions; Studio63.370 assertions/194 entries. Baseline46 PNG nguyên SHA256; 140 runtime sources chọn khớp byte. Có 6 MP4 native, ảnh/dải mẫu, source/binding pins và decode/hash audit. Video offline60 bước/s không chứng nhận gameplay60FPS.

Catalogue: 143 page structure, 56/1008 job đủ nguồn, 20 job đủ nguồn kiểm source; còn952 job thiếu,21 HOLD và atlas VFX cũ sai hàng. Rễ Nước9/12 action đủ nguồn; còn ba pha chồi đất. Chưa nghiệm thu toàn actor/skill/gameplay, AI, collision/hit, LowFX hoặc PCK.

Chi tiết và lệnh mở: [đặc tả đợt a ngày13/11](../../docs/production/Actor_Batch_20261113a_vi.md). Inventory `Art_Source/Actor_Library_20261107/batch_20261113a.json`; evidence `Implementation/Reports/Evidence/Actor_Batch_20261113a/`.
