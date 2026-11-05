# MoonGlass UI — nghiệm thu giao diện

Yêu cầu: làm lại HUD và toàn bộ panel theo hướng hiện đại, bán trong suốt; bảng màu dùng ảnh tham khảo2–3 (indigo/violet/silver). Nhánh codex/moonglass-ui-20261105, dựa trên f0859d0 của nhánh tích hợp.

## Đã thay đổi

- HUD mới: avatar chân dung, HP/MP gradient có số, utility bar, nhiệm vụ3tab, minimap dữ liệu thật, dock icon, nút đánh lớn và6kỹ năng vòng cung.
- Theme thống nhất13mục: nhân vật, túi, kỹ năng, nhật ký, bản đồ, rèn, bang, hoạt động, bách khoa, ngoại trang, bạn bè, thư và cài đặt.
- Tách HUD khỏi cửa sổ đang mở; sidebar tự cuộn tới mục chọn, nội dung có vùng cuộn riêng. Bộ lọc túi và chọn vật phẩm dùng inventory snapshot; không cấp đồ/tiền hoặc equip giả.
- Preview nhân vật xoay8hướng; avatar mới là ảnh gốc tạo bằng built-in image_gen. Biểu tượng giao diện là SVG code tự vẽ. Ảnh nguồn/runtime giữ nguyên byte, không xử lý bitmap sau sinh.
- Cài đặt VFX/camera/âm lượng thực, lưu theo user. Phím C/K/M/F10 bổ sung bên cạnh J/I/E.
- StyleBox dùng cache; không blur toàn viewport trên GPU820M. Chưa có benchmark FPS ổn định hay chứng nhận mobile.

## Kiểm tra

Native Godot4.7.2 .NET, Compatibility/OpenGL, GeForce820M trên máy hiện tại. Chạy Run_Playable_Alpha.ps1 -UiGallery với server loopback riêng, nhân vật mới và tuyến P00-01 thật. Log/screenshot nằm trong Evidence/MoonGlass_UI_20261106; marker native UI phải có125assertions và gallery13mục phải PASS.

- Client build SDK8: 0 lỗi, 0 cảnh báo.
- Source/DTO UI:30checks; điều hướng13mục, tab trang bị, tìm kiếm túi không phát mutation/cấp thưởng; đây không phải HTTP test.
- Camera48, scene9, visual15checks.
- Art/provenance/catalog kiểm tra bằng inspect_reboot.py, inspect_environment.py, inspect_combat.py, inspect_moonglass.py và export_native_catalog.py --check.
- Các ảnh là render native của game; thao tác nghiệm thu nhiệm vụ dùng tín hiệu nút Godot, không khẳng định đã tự động hóa chuột vật lý.

Lượt đầu có timeout di chuyển khi máy tải nặng. Một lượt khác dừng ở x38.97389 và chọn kiện hàng thay vì Ly An: đích test39.5 với sai số0.6 cắt qua trung điểm x39 của hai đối tượng. Đã chuyển đích test thành40, giữ nguyên khoảng nhận và điều kiện nhiệm vụ; không đổi gameplay để ép test qua. Kiểm scene từng đọc vị trí trước khi physics tick hoàn tất trên headless catch-up frames; helper nay đợi thêm ProcessFrame sau PhysicsFrame. Các thất bại không được coi là PASS; log cũ giữ ngoài evidence cuối trong NGUMACHHUYENAN-tools.

## Giới hạn chức năng

Đây là lớp trình bày, điều hướng và UI gameplay đang hỗ trợ. Equip12slot, forge, guild, activities, mail, social và cosmetic chưa có backend đã nghiệm thu: giao diện hiện empty/disabled state phù hợp. Không đổi contract/wire enum và không phát lệnh trang bị mới. Các ô trống không chứng nhận dung lượng túi. Minimap dựa art layout + snapshot, không thay thế navigation server; map server vẫn canonical như README. Không mở khóa P00-02..05 hay merge PR106/109/119 trong gói UI này.

Thiết kế chi tiết: docs/production/MoonGlass_UI_UX_vi.md. Prompt: Art_Source/MoonGlass_UI_20261105/Prompts/portrait.txt. Nguồn/runtime avatar và SHA256: Art_Source/MoonGlass_UI_20261105/source_inventory.json.
