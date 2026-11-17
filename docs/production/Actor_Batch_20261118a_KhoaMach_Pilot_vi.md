# Khóa Mạch hướng Đông

Ngày 18/11/2026. Linh Cung đã có sheet hướng Đông với 16 tư thế giương cung, kéo dây, thả một lần rồi hạ cung. Giữ tạo hình tóc đuôi ngựa, áo xanh ô liu, choàng ngắn và ống tên của atlas idle. Hai VFX mới là mũi tên lá và vệt lá vỡ tan. Mỗi sheet có 16 hình và được lưu cùng prompt gốc từ ImageGen.

Mũi tên bay được căn theo điểm đầu và trục thân tên trong từng ô. Vệt lá tan dùng cùng điểm tiếp xúc. Pha cuối giữ một đốm bán trong suốt nhỏ bằng ngưỡng alpha dành cho đuôi hiệu ứng. Dấu rễ dùng lại sheet `sk_lc_01_mark_component` đã có đánh giá nguồn, giữ nguyên PNG.

Mở `Implementation/Reports/Evidence/Actor_Assembly_20261117a/KhoaMach_E/project.json` trong Sprite & VFX Studio. Nhân vật đứng bên trái và Thủy Căn bên phải. Mũi tên bắt đầu ở trục mũi tên vẽ trên cung. Vệt lá và dấu xuất hiện ở pha chạm. Project có năm lớp chỉnh độc lập. Điểm chạm và khoảng cách trong demo được chọn để xem rõ ở Studio.

Đã xem ba atlas, 48 tư thế hoặc pha nguồn, tám mẫu của cú bắn ghép và đoạn nối 14 → 15 → 0 → 1 của mũi tên. Ba video nguồn và video ghép giải mã đủ 660 frame. Có thể xem lại thông số nguồn và các mã băm trong `native_audit.json`. Còn bốn hướng gốc, chuyển động vào và ra idle, bản kiểm ở camera rộng và kết nối dấu với xác nhận trúng từ gameplay.
