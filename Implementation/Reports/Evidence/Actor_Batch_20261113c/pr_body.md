Thư viện sprite chibi nguyên khối còn thiếu action và VFX. PR bổ sung combat Cá Linh, idle/interact Người Giữ Thuyền, 12 action Rễ Nước và bốn kỹ năng Minh Kiếm. Mỗi hướng nguồn có16 khung; N/NE/E/SE/S vẽ nguồn, ba hướng còn lại lật theo policy. Walk NPC E/NE còn HOLD.

Đợt mới nhất20261113c thêm20 sheet chọn/320 khung nguồn: Tầm Long, Kiếm Trận, Thiết Y ×5 hướng và5 VFX component (trail, bụi dừng, gain/break/expire khiên). BOOT_CORE_FOOT neo vào giày nâu, bỏ mũi kiếm thấp; neutral-height cố định và solid-core gutter giữ độ dài vũ khí. N thrust và shield break có bản sửa, bản cũ giữ trong lịch sử.

Timing nguồn tùy chọn được pin cùng binding, đọc thống nhất trong Actor Library và Studio: Tầm Long0,15/0,20/0,24s; Kiếm Trận ba nhịp0,10/0,12/0,14s cộng0,24s hồi trình bày. Thiết Y0,80s trình bày độc lập thời gian khiên4s. Seek/resume, one-shot và readout offline theo đúng pose; Studio giữ chỉnh tay/chèn component, undo/redo, socket/timing, JSON/bundle. Không suy damage, MP, CD, collision hoặc root-motion từ art.

Validation20261113c: .NET8 build0 warning/error; Godot import;44 Python tests; native library14.424 assertions; Studio70.890/238 entries; root cue12+20 và existing Kiếm Trận VFX14. Baseline46 PNG nguyên SHA256;178 runtime sources khớp byte.10 MP4 native chọn,3 lịch sử, ảnh/dải mẫu, source/binding pins và decode/hash audit. Video offline60 bước/s không chứng nhận gameplay60FPS.

Catalogue181 page structure;62/1008 job đủ nguồn;26 job đủ nguồn đã kiểm source, còn946 job thiếu.21 HOLD cũ và full VFX atlas sai hàng giữ nguyên. Minh Kiếm10/12 clip đủ dữ liệu xem, skill_05/06 còn thiếu; chưa nghiệm thu toàn class hoặc encounter. Ghép body+VFX, gameplay renderer/AI/hit/collision/LowFX/PCK và asset map/UI/icon/audio/biến thể tiếp tục.

Chi tiết: docs/production/Actor_Batch_20261113c_vi.md; inventory Art_Source/Actor_Library_20261107/batch_20261113c.json; evidence Implementation/Reports/Evidence/Actor_Batch_20261113c/. Các đợt trước giữ tài liệu, nguồn và lịch sử riêng.
