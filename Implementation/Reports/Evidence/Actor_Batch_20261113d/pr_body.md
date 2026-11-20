Thư viện sprite chibi nguyên khối còn thiếu action và VFX. PR bổ sung combat Cá Linh, idle/interact Người Giữ Thuyền,12 action Rễ Nước và sáu body skill Minh Kiếm. Mỗi hướng nguồn có16 khung; N/NE/E/SE/S vẽ nguồn, SW/W/NW lật theo policy. Walk NPC E/NE còn HOLD.

Đợt mới nhất20261113d thêm13 sheet chọn/208 khung nguồn: Bạch Hồng, Vạn Tượng Quy Nhất ×5 góc và ba component vệt né/tụ lực/đường kiếm. Ba bản sửa tuyệt kỹ E/NE/SE thay quỹ đạo giống đâm, góc lưng sai và tay dư; bản nguồn cũ giữ lịch sử. Đợt20261113c trước đó thêm20 sheet/320 khung cho Tầm Long, Kiếm Trận, Thiết Y và năm VFX.

Library/Studio đọc timing từng khung, giữ seek/resume, phase boundaries, loop/one-shot, mirror, JSON/bundle và chỉnh pivot/tọa độ/layer/socket. Bạch Hồng0,48s và tuyệt kỹ1,55s là profile trình bày có giả định ghi rõ; không suy damage/CD/MP/Kiếm Ý/root-motion từ art. Vệt0,16s gameplay không bị kéo dài bằng0,32s preview. BOOT_CORE_FOOT neo giày, neutral-height cố định; trail/cut dùng longest-axis span, charge dùng tâm bounds đối xứng sau kiểm native.

Validation20261113d: .NET8 build0 warning/error; Godot import;52 Python tests; library15.008 assertions; Studio73.426/253 entries.46 baseline PNG nguyên SHA256,191 runtime sources khớp byte,181 source/binding trước không đổi.7 MP4 native chọn và1 lịch sử, ảnh/dải mẫu/source pins/decode/hash audit. Video offline60 bước/s không chứng nhận gameplay60FPS.

Catalogue194 page structure;64/1008 job đủ góc nguồn;28 job đủ góc đã kiểm source, còn944 job thiếu.21 HOLD cũ và full VFX atlas Kiếm Trận sai hàng giữ nguyên. Minh Kiếm12/12 clip đủ dữ liệu xem chưa nghiệm thu cả class. Body+VFX assembly, server events, gameplay renderer/AI/hit/collision/LowFX/PCK và asset map/UI/icon/audio/biến thể tiếp tục.

Chi tiết: docs/production/Actor_Batch_20261113d_vi.md; inventory Art_Source/Actor_Library_20261107/batch_20261113d.json; evidence Implementation/Reports/Evidence/Actor_Batch_20261113d/. Các đợt cũ giữ tài liệu, nguồn và lịch sử riêng.
