# HUD v2 — vòng cung kỹ năng quanh nút đánh

Chủ dự án xác nhận bố cục vòng cung theo ảnh tham khảo ngày2026-10-29. Concept hiện hành: `Art_Concept_References/v1/06_pixel_hud_skill_arc_v2.png`; concept04 lưới hai hàng là lịch sử. Ảnh tham khảo chỉ dùng cách bố trí, không lấy UI/nhân vật/tên riêng từ game khác.

## Cấu trúc

Một nút `Đánh` lớn neo góc phải dưới; sáu nút skill tròn nhỏ cùng bán kính quỹ đạo, tạo vòng cung từ trái-dưới đi lên bên trái và vượt đỉnh nút đánh. Nút đánh là tâm bố cục. Không dàn sáu nút thành lưới, không đặt nửa cung ra ngoài cạnh phải/dưới. Số1..6 đi liên tiếp theo cung; ô tuyệt kỹ6 có viền đồng kép. Đánh thường không chiếm một ô skill.

## Geometry tham chiếu

Logical canvas640×360, gốc trái-trên, X tăng sang phải, Y tăng xuống. Attack center C=(584,310), visual radius26; skill visual radius13, orbit radius80. Sáu góc theo thứ tự [200,174,148,122,96,70] độ. Công thức `x=cx+r*cos(theta)`, `y=cy-r*sin(theta)`; làm tròn vị trí render cuối về pixel nguyên. Không dùng công thức dấu Y ngược dẫn cung rơi ra dưới màn.

| Slot | Góc | Tâm logical x,y (làm tròn) | Vai trò |
|---|---:|---|---|
|1|200|509,337|active1|
|2|174|504,302|active2|
|3|148|516,268|active3|
|4|122|542,242|active4|
|5|96|576,230|mobility|
|6|70|611,235|ultimate|

Kích thước trên là baseline layout, không đo ngược từng pixel ảnh sinh. Khi safe area thay đổi, dịch cả nhóm vào vùng hợp lệ; không clamp từng slot làm vỡ cung. PC và mobile giữ cùng thứ tự. Chế độ thuận tay trái mirror cả nhóm, giữ slotId và ánh xạ phím. EXP không đi xuyên vùng chạm hub; có thể chạy ở đáy dưới nhóm hoặc rút ngắn chiều dài.

## Input và khả năng chạm

Visual và hit target tách riêng. Hit targets không giao nhau; mục tiêu mobile tối thiểu48dp sau safe-area/device scaling. Nếu scale logical không đủ đạt48dp hoặc làm hit targets đè nhau, tăng orbit/diện tích nhóm rồi dời sang trái/lên; không thu nhỏ hit target để giữ bố cục đẹp. Giữ pixel scale nguyên cho texture, không áp scale phân số lên sprite. Preview phải có overlay hitboxes riêng để reviewer kiểm.

Touch-down có pressed frame; touch-up đúng target mới submit nếu skill là tap. Drag-to-aim mở preview và chỉ commit sau release hợp lệ; kéo ra cancel zone hủy preview, không tiêu MP/CD. UI captured pointer không đi xuống terrain click. Cooldown theo thời gian server, badge số1..6 không bị sweep che; unavailable có lock/reason chứ không chỉ màu xám.

Khóa mục tiêu/đổi preset nằm phía trên vùng cung, không chiếm slot. Tương tác NPC là nút riêng hoặc context action có trạng thái explicit; không âm thầm biến nút attack thành dấu hỏi giữa combat. PC J/chuột trái đánh thường,1–6 skill,Space/Shift né,F tương tác,Q/E thuốc theo DEC-016; badges cập nhật khi remap, không dùng Q/W/E/R cũ xung đột WASD.

## Icon và mỹ thuật

Concept v2 có icon minh họa; số slot đúng không có nghĩa glyph đã đúng môn phái. Muse phải vẽ icon theo skill canonical: Minh Kiếm1 Phản Quang (guard/phản),2 Tầm Long (lao kiếm),3 Kiếm Trận (ba cung),4 Thiết Y (khiên),5 Bạch Hồng (lướt),6 Vạn Tượng Quy Nhất (đường kiếm hội tụ). Không đổi skill mechanics để giống icon sinh.

Nền navy/charcoal, vòng brass pixel, focus teal, cooldown mặt nạ tối; không glow/bloom làm mất silhouette. Text trong board là minh họa, tên quest/rarity/icon cuối lấy từ registry/localization.

## Muse bàn giao

1. PNG mockup640×360 với sáu slot quanh attack và bảng tọa độ.
2. Component source: attack52px,skill26px native và icon variant; normal/pressed/focus/disabled/cooldown mask, tooltip anchor.
3. Preview720p/1080p/20:9 với safe-area và hitbox overlay; chứng minh không che character/telegraph.
4. Không đưa board lớn vào runtime manifest; asset tách riêng, đúng PPU/import/metadata và palette.
