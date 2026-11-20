# Khôi phục phong cách pixel chi tiết — 10/11/2026

Theo yêu cầu mới nhất của chủ dự án: giữ cách vẽ pixel minh họa trước đây, chỉ chỉnh tỉ lệ thân/cổ/tay/chân dài hơn rồi vẽ trang phục theo tỉ lệ mới. Mẫu procedural hình khối V2 đã bị bác bỏ về mỹ thuật và không còn là màn xem mặc định.

## Ảnh master

- Sheets/body_base_mf_v3.png: base nam/nữ, underlayer sát thân, đầu/mặt để trống cho diện mạo.
- Sheets/outfit_ivory_mf_v3.png: bộ giao lĩnh ngà/ngọc vẽ bằng bước edit trực tiếp từ base.
- Sheets/appearance_ivory_mf_v3.png: bước edit tiếp thêm tóc, mắt và kiếm cầm chéo để xem tổng thể.

Ảnh gốc từ imagegen tích hợp được chép nguyên byte; prompt thực trong Prompts tương ứng cùng ID. Không dựng lại nhân vật bằng các khối pixel lập trình.

## Phạm vi

Đây là ba bản vẽ master hướng S, một pose mỗi nhân vật. Chưa tách thành layer trang bị, chưa có 16–20 pose/action/hướng, chưa đạt native grid hoặc animation/runtime approval. Cần kiểm viền alpha, độ đồng nhất pose, fit garment và source layer trước khi làm atlas. Không lấy các phép so pixel của mẫu procedural cũ để chứng nhận ảnh mới.

Phòng xem mặc định: ClientGodot/PaperDollArtReview.tscn, qua Run_PaperDoll_Lab.ps1. Có Base / Trang phục / Mẫu diện mạo và chồng base đối chiếu bằng mắt. Công cụ fit cũ giữ riêng cho kiểm kỹ thuật; không là mẫu mỹ thuật được chấp nhận.
