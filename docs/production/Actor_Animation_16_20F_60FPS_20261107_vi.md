# Chuẩn animation 16–20 khung / render 60 FPS

Quyết định chủ dự án được nhắc lại ngày 07/11/2026. Áp dụng cho toàn bộ asset class, quái, boss và NPC được tạo hoặc thay mới. Thay các hướng dẫn cũ cho phép sprite 4–8 khung hoặc mặc định 6–12 FPS như chuẩn hoàn thiện.

## Khung hình và hướng

- Mỗi clip cho mỗi hướng cần 16–20 frame nguồn thực. Mặc định 16; dùng20 khi động tác phức tạp cần thêm pha. Không lặp4/8pose, nội suy ảnh AI hoặc kéo dài frame để báo đủ16.
- Actor di chuyển dùng8hướng N/NE/E/SE/S/SW/W/NW. Có thể dùng5hướng nguồn +3hướng lật SE/E/NE nếu silhouette/đạo cụ cho phép; khai báo trong manifest. NPC/đối tượng cố định hoặc VFX vô hướng phải khai báo directionPolicy và không được báo thành8hướng vẽ riêng.
- Atlas mỗi clip có thể gộp5hướng nguồn ×16frame =80sprite; bố cục8cột×10hàng, mỗi hướng2hàng8frame. Chỉ dùng khi đủ80ô, không chạm biên hoặc mất hàng/cột. Page4×4 cho một hướng là phương án tách nếu atlas dày không đạt chất lượng.
- Mỗi sprite cần frame rect, alpha bounds, pivot mặt đất, referenceHeight thống nhất giữa các state, hướng/flip, thứ tự frame và thời lượng. Không tự đổi collision hoặc vị trí server bằng animation.

## Timeline và FPS

- Game render mục tiêu60FPS, physics60Hz; network/server tick là đồng hồ riêng. 16frame nguồn không có nghĩa game chỉ render16FPS, cũng không có nghĩa mọi clip đều kéo dài16/60giây.
- Idle mẫu1,0s; walk0,8s; basic0,6s; hurt0,3s; death1,2s. Cast/skill/telegraph/recovery theo timeline được chốt, không thay đổi thời gian nguy hiểm để ép animation. Mọi frame phải có thời lượng dương; ngân sách thời gian được phân bổ qua16–20frame.
- Sprite đổi pose theo delta thời gian; transform render được nội suy khi phù hợp. Không coi tăng số frame nguồn là bằng chứng đạt60FPS. Phải đo native và lưu GPU, viewport, số mẫu, median/p95.
- Điểm sát thương, heal, buff, knockback, death và quest credit chỉ do event/receipt server quyết định. Clip preview không cấp chúng.

## Bộ clip tối thiểu

| Nhóm | Bộ bắt buộc |
|---|---|
| Mỗi class | idle, walk, basic_attack, skill_01..06 riêng, hurt, death; guard/dodge khi gameplay có |
| Quái | idle, move, telegraph, attack theo từng đòn đặc trưng, recovery, hurt, death |
| Boss | idle/move nếu di chuyển, telegraph và attack riêng cho từng cơ chế, recovery, hurt, death; phase/additional layer theo Bible |
| NPC | idle, interact/work/talk theo nghề, walk cho di chuyển/hộ tống; diễn xuất rescue/trial theo vai. Mỗi clip vẫn16–20frame |
| VFX | 16–20frame cho timeline hoặc mỗi thành phần cast/projectile/impact/loop/end được tách; không báo16nếu chỉ có6hình |

## Cổng nghiệm thu

REQUESTED → GENERATED → STRUCTURE_PASS → VISUAL_REVIEW → ENGINE_IMPORTED → DEVICE_QA. Mỗi trạng thái phải có bằng chứng. Check SHA/frame count chỉ chứng minh cấu trúc, không tự chứng minh đẹp/mượt. Chặn atlas cắt mép, thiếu hàng/cột, alpha nền giả, body/weapon nhảy, foot sliding quá mức, đổi danh tính hoặc đảo tay/đạo cụ. Ghi rõ asset dùng chung/archetype/palette; NPC unique_face=true cần khuôn mặt riêng.

Ảnh nguồn giữ nguyên từ imagegen tích hợp; không dùng Python vẽ/sửa bitmap để cứu lỗi ảnh sinh. Công cụ đọc ảnh chỉ phân tích bounds/grid/hash và xuất metadata. Sửa hình qua imagegen rồi nghiệm thu lại. Lazy load/chia page cho máy yếu; không nạp toàn catalogue cùng lúc. LowFX giữ silhouette/timeline/geometry của cue bắt buộc.

Runtime hiện hành là Godot .NET Compatibility, viewport1280×720, camera64×36WU (F2:48×27), nearest pixel. Các đoạn cũ640×360/camera18WU là lịch sử blockout, không được tự áp lại làm game thu hẹp tầm nhìn.
