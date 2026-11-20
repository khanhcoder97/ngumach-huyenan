# Paper-doll: phòng thử và asset ghép lớp — 07/11/2026

Tiếp nối commit 1effba5. Đã triển khai công cụ authoring có render thật; chưa bật nhân vật modular trong gameplay.

## Kết quả

- Phòng thử Minh Kiếm nam/nữ, so sánh base và look ghép lớp, thử tóc/mắt/outfit/kiếm/mũ/cape.
- Một clock cho mỗi actor; preview đối chiếu được đồng bộ frame. Timeline 16 pose, bước từng frame, zoom nguyên 2×/4×/6×, hiển thị anchor.
- Sửa anchor hoặc offset từng part theo pose; chọn áp cùng giá trị cho 16 placement; lưu/mở/reset draft.
- Draft gắn fingerprint nguồn/catalog, kiểm đầy đủ trước commit và giữ state khi lỗi.
- Một atlas sinh mới chứa 16 phần tĩnh rời: 2 tóc, 2 mắt, 2 áo, 2 quần, 2 giày, 2 kiếm, 2 mũ, 2 cape. Giữ PNG nguyên byte và prompt imagegen tích hợp.
- Exporter read-only đưa hai body candidate cũ và atlas part vào runtime lab; kiểm SHA và đồng bộ byte.
- Mẫu không native dùng hiệu chuẩn cố định theo atlas trong review. Gate production yêu cầu native scale=1 và approval như cũ.
- Launcher dùng Godot .NET portable + SDK 8, không cần Unity.

## Kiểm chứng và giới hạn

Build 0 warning/0 error; model 53 assertion; lab 146 assertion; legacy 10421 assertion đều đạt. Cảnh hai actor preview trên GeForce 820M đạt mean 60,06 FPS, median 16,651 ms và p95 16,748 ms sau warmup 2 giây, đo khoảng 12 giây. Số đo không đại diện world crowd/combat. Xem evidence PaperDoll_Lab_20261107. Screenshot nam/nữ đã xem trực tiếp, chỉnh lại face/collar/hip/weapon anchors. Ảnh vẫn có lỗi nguồn và thiếu skin-pass; không phê duyệt wardrobe production.

Giữ 0 native modular clip approved. Dữ liệu mới chỉ S/idle; 16 ô body candidate chưa phải chứng nhận motion; mỗi part là 1 artwork tĩnh với 16 placement, không phải 16 artwork trang phục.

Chưa sửa hero, world camera/collision, backend enum, combat/stats/rewards, account hoặc creation UI. Chưa có full action, tám hướng, native master, split tay, mask, dye, under-cap hair, item visual resolver, persistence và world crowd QA.

## Tệp

- ClientGodot/PaperDollLab.tscn, Run_PaperDoll_Lab.ps1.
- ClientGodot/scripts/PaperDollLab.cs, PaperDollLabData.cs.
- ClientGodot/assets/paperdoll_lab/catalog.json + ba PNG nguồn nguyên byte.
- Tools/ArtProduction/export_paperdoll_lab.py.
- Art_Source/Modular_Characters_20261107/Wardrobe_Study và Prompts/mk_s_parts_v1.txt.
- docs/production/PaperDoll_Fit_Lab_20261107_vi.md.
