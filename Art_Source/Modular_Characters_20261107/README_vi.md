# Base nhân vật ghép lớp — 07/11/2026

Đã tạo hai ứng viên base nam/nữ hướng S, mỗi sheet 16 ô idle. PNG nguyên từ imagegen tích hợp, prompt trong Prompts. Chưa có tóc/mắt/vũ khí/giáp; base có coverage trung tính. Đây chưa phải bộ 8 hướng, chưa phải pose master đúng grid 96×96 hoặc pack layer đã fit. productionApproved=false.

Đặc tả: docs/production/Modular_Character_Appearance_20261107_vi.md. Registry 2 rig/10 profile trong modular_character_plan.json. structure_report chỉ kiểm alpha/grid/frame rect, không chứng nhận chuyển động/fit. Prototype renderer/test metadata ở ClientGodot; không gắn vào hero online, không có account/equip/appearance persistence mới.

Đã thêm Wardrobe_Study: atlas 16 phần tĩnh rời, prompt và inspection. Công cụ ClientGodot/PaperDollLab.tscn thử ghép trực tiếp và sửa anchor/offset theo pose. Mỗi part chỉ có 1 hình tĩnh; 16 placement không phải 16 hình animation. Nguồn còn viền thừa và chưa native/fit approved. Xem docs/production/PaperDoll_Fit_Lab_20261107_vi.md.
