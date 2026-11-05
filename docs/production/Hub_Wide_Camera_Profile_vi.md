# Camera rộng hiện hành — cập nhật05/11/2026

**Nguồn có hiệu lực:** [TopDown_Wide_Camera_20261105_vi.md](TopDown_Wide_Camera_20261105_vi.md), decision CAM-TOPDOWN-WIDE-20261105 và camera_topdown_wide_20261105.json. Chủ dự án yêu cầu cả góc vẽ map từ trên xuống lẫn tầm nhìn rộng hơn.

- Default toàn thế giới64×36WU, viewport1280×720,20PPU. Gấp4 diện tích32×18WU.
- Tùy chọn Gọn48×27WU; HUD tách CanvasLayer, không thu nhỏ theo camera.
- Camera2D không xoay; asset kiến trúc gần nhìn thẳng từ trên, mái chiếm ưu thế.
- Scene Godot art staging đã có source; server visibility, geometry canonical và instance rules chưa tự thay.
- Hub Thăng Long vẫn có mục tiêu2048×1536WU/12phường; camera chỉ thấy một phần, không là toàn thành.
- Doc2026-10-29 và ảnh so sánh v2 dùng48×27WU là lịch sử, không còn default hay chỉ thị giao Muse. Những yêu cầu chỉ hub mới nhìn rộng, máy nhỏ tự về32×18WU và Muse sở hữu runtime được thay bởi quyết định mới.

Chạy scene ClientGodot/Preview.tscn để kiểm tra camera Rộng/Gọn cùng một map/position. Ảnh concept không chứng minh runtime/geometry hoặc performance.
