# Sửa paper-doll và master đăng ký — 10/11/2026

Chủ dự án bác bỏ body/trang phục sinh riêng vì không cùng tỉ lệ, cổ và chân tay ngắn, phần nối không khớp. Hướng hiện hành chuyển sang một master hình học/pose native cho cả body và outfit. Các PNG sửa thử đầu phiên được giữ ở trạng thái không đạt, không làm nguồn mặc định.

## Đã triển khai

- Tỉ lệ master đứng 54 px/đầu 12 px; canvas 96×96, gốc chân (48,72). Cổ/tay/chân rõ hơn; 16 pose dùng chung.
- Body và sleeves/pants lấy cùng khớp; outfit là một lựa chọn liền áo/quần, có biến thể nam/nữ. Trang bị và chỉ số gameplay giữ nguyên.
- Nón giữ tóc/mái/hai bên; mask phần crown dưới nón, tháo nón khôi phục nguồn tóc.
- Kiếm chéo ngắn, pivot ở cán, bàn tay trước phủ cán.
- Studio chỉnh local/master/viewport, attachment, pivot, góc, scale, mirror, hidden, painter order, drag/pick, undo/redo và draft ràng buộc nguồn.
- Hai master .aseprite thực sự có layer/frame, nguồn native authoring và bộ đọc kiểm độc lập.

## Kiểm chứng

Build 0 warning/0 error; studio 175 assertion; model 58; legacy 10421 đều đạt. 64 composite có 0 pixel lệch và 0 pixel coverage nền thò ra. Bộ đọc độc lập xác minh hai .aseprite, mỗi file 20 layer/16 frame, body và cả hai outfit có 16 cel khác nhau. Benchmark hai preview trên GeForce 820M: mean 60,06 FPS, p95 16,735 ms. Xem Evidence/Registered_Master_20261110. Phép so sánh layer/monolithic và kiểm coverage chỉ là nghiệm thu đăng ký kỹ thuật; chưa phải phê duyệt art.

## Giới hạn

Mẫu mới là master kỹ thuật S/idle, chưa phải tạo hình cuối. Chưa đủ 8 hướng/action hoặc gameplay. Source .aseprite xuất để retouch; importer cho bản retouch chưa hoàn tất. Nguồn PNG legacy không được nâng cấp thành asset approved. Không dùng kết quả scene hai actor để tuyên bố world crowd/combat đạt 60 FPS.
