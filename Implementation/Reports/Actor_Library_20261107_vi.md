# Actor Library — nghiệm thu đợt ứng viên07/11/2026

Đã áp dụng quyết định16–20khung nguồn thực/clip/hướng và60FPS render vào chuẩn pixel, Art Bible, Combat/VFX, production queue và DEC-024. Mức idle4–6/walk6–8/hit2–4 cũ đã bị thay trong chuẩn hiện hành. CameraGodot1280×720/64×36WU, UI MoonGlass và authority server giữ theo hướng hiện hành.

## Sản phẩm đã tạo

- Catalogue130actor (5class/30quái/12boss/83NPC),30skill và hàng đợi1008page **base animation/timeline**, không phải thư viện đã hoàn thành; chưa bao gồm mọi biến thể/trang bị/portrait/icon hoặc VFX split bổ sung.
-36record ảnh ứng viên hiện hành, kèm PNG nguyên gốc, prompt thực, lịch sử sửa, alpha/bounds/pivot/direction/flip/SHA256 và cổng nghiệm thu.
-35page qua cấu trúc:32mới+3legacy Motion16. Chỉ32job bắt buộc có dữ liệu cấu trúc;3page khác là pilot/override. Còn976job chưa qua cấu trúc. Ảnh mới production-approved:0. Toàn gói complete=false.
-4ảnh bị chặn cấu trúc: Kiếm Trận5hàng; Thạch Chùy basic_attack chạm biên giữa hàng; Kẻ Rình Bờ7cột; Rễ Nước9hàng. Không ép chia lưới để nhận chúng.
- SceneGodot ActorLibrary: nhóm/tìm actor/chọn clip,8hướng có nhãn nguồn/lật/thiếu, tua từng khung, play/pause, one-shot giữ khung cuối, lazy cache8texture. Hướng bất đối xứng không mượn mirror. Separate16frame SE death sửa continuity và được dùng cho SW mirror khi được phép.
- ActorLibraryData mặc định chặn ảnh chưa duyệt; reviewMode mới được xem ứng viên. Không fallback sprite khi thiếu, không fake gameplay/server support.

## Kiểm chứng

- Build .NET8:0warning/0error.
- Godot headless:10421assertion qua; bao gồm texture/rect/frame count, thiếu actor/clip không fallback, chặn ảnh chưa duyệt, hướng bất đối xứng, one-shot cuối, scrub/resume và đủ16pose với delta1/60.
- Planner --check và inspector --export --check qua; ảnh runtime được so nguyên byte với nguồn. CI visual-reboot thêm hai kiểm tra này và LFS đúng phạm vi.
- --require-complete bị chặn đúng dự kiến; giữ nguyên pending/HOLD. Đây không phải lỗi bị bỏ qua để gọi asset hoàn tất.
- Native benchmark trong Evidence/Actor_Library_20261107/native_performance.json: GeForce820M,1280×720, warmup2s+lấy mẫu12s, khoảng60FPS, median16,648ms/p9518,365ms. Chỉ đo scene8hướng Ảnh Đao walk, không chứng nhận gameplay đông quái/crowd/combat.
-Ảnh native trong cùng thư mục là khung09/16 đóng băng, có nhãn ảnh tĩnh; không dùng FPS của ảnh làm bằng chứng.

## Phần chưa hoàn thành

Chưa đủ bộ hành động cho bất kỳ class mới, quái/boss/NPC; chưa đủ sáu cast riêng/class, đầy đủ đa thành phần VFX hoặc các biến thể. Các ảnh qua cấu trúc vẫn cần review chuyển động/đổi state/foot sliding/weapon continuity ở kích thước chơi. Metadata kích thước là khởi tạo cần hiệu chỉnh native, chưa phải calibration cuối.

Asset mới **chưa nối gameplay**. HeroAnimator/NativeActorsView/SkillVfxPlayer và gameplay online vẫn dùng baseline đã bàn giao; Mob AI/death-return tiếp tục OFF,3skill Minh Kiếm có backend. Thư viện không tự mở khóa class/skill/giao dịch hay cấp damage/thưởng.

Tiếp theo: sửa4atlas bị chặn; nghiệm thu đủ16pose/chuyển state5class; hoàn thành bộ Bến Mưa; các roster còn lại; chỉ bind actor đủ clip qua gate. Gói nguồn/prompt/hướng dẫn ở Art_Source/Actor_Library_20261107/README_vi.md. Mở ClientGodot/Xem_Thu_Vien_Asset.cmd để xem trực tiếp. Dùng imagegen tích hợp, khôngCLI/API; không dùngPython chỉnh bitmap.


## Tương thích pipeline sau cập nhật chuẩn

CI phát hiện audit lịch sử còn parse cứng Walk6frame và khóa source cũ. Đã chuyển bộ đọc sang khối JSON chính sách trong chuẩn pixel, phân biệt16–20pose nguồn/renderer60FPS; giữ cell48×64 chỉ là reference legacy, không áp cho atlas trim. Sáu regression test kiểm chuẩn thực, chấp nhận20pose, từ chối6pose/thiếu policy/sai hướng/nhầm FPS. 28test compiler qua. Đã đối chiếu bảng Art Bible và DEC-001..023 không đổi, review lại hai source lock rồi tái xuất candidate/audit. Bằng chứng21candidate giữ nguyên definition, ID, status, activation và blocker; chỉ provenance/sourceVersion/digest cập nhật. Các thiếu hụt gameplay vẫn bị chặn, không bật runtime.
