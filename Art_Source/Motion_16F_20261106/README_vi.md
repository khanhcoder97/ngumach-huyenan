# Motion16 — nguồn chuyển động Minh Kiếm

Tạo bằng công cụ imagegen tích hợp (built-in image_gen) theo prompt và ảnh tham chiếu trong phiên làm việc ngày 06/11/2026. Không cần API key. Đây là bộ thay thế chuyển động cho nhân vật playable hiện tại, không phải bộ mọi lớp nhân vật/quái/NPC.

- generation_records.json ánh xạ 20 bản nguồn được chấp nhận, prompt thực tế và bản runtime byte-identical.
- Mỗi PNG là lưới 4×4 gồm 16 pose, đọc theo hàng. Bốn hành động: idle 1,6 giây, walk 0,8 giây, attack 0,6 giây, cast 0,64 giây.
- N/NE/E/SE/S có sheet riêng; SW/W/NW lật SE/E/NE trong metadata của renderer. Tổng 320 pose nguồn, 512 tham chiếu khi tính đủ 8 hướng.
- source_history.json giữ lịch sử các bản nguồn được chỉnh lại bằng imagegen vì alpha/cắt khung. Các bản không đạt không được nạp vào runtime.
- Không kéo dài 4 pose bằng lặp để giả thành 16. Không dùng Python chỉnh ảnh. Công cụ inspect_motion16.py chỉ kiểm ảnh và xuất rect/pivot/SHA256, Godot đọc region lúc chạy.
- Ảnh review 8 hàng ×16 cột được chụp từ renderer Godot; đây là bảng kiểm tư thế tĩnh, không chứng minh FPS hay độ mượt của timeline.

Chạy python Tools/ArtProduction/inspect_motion16.py từ repo để kiểm nguồn/runtime và manifest. Khi chủ ý đổi sheet, chạy với --write-manifest rồi review lại trong Godot.
