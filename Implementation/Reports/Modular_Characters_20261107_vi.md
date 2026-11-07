# Nhân vật modular — bàn giao nghiên cứu/prototype 07/11/2026

Yêu cầu của chủ dự án đã chuyển thành pipeline base nam/nữ + các phần diện mạo/trang bị tách lớp. Không có giao dịch, account hoặc endpoint mới được bật.

## Đã thực hiện

- Đặc tả kỹ thuật/UX/sản xuất/hiệu năng trong docs/production/Modular_Character_Appearance_20261107_vi.md; có nguồn Godot/Aseprite/LPC chính thức và phân biệt phần nghiên cứu với phần đã code.
- Registry 2 rig dùng chung,10 profile cho 5 class×2 giới tính; không khóa ngoại hình/giới tính theo class. Đòn và skill vẫn theo class.
- Hai PNG ứng viên base nam/nữ hướng S, mỗi sheet 16 ô idle, tóc/mắt/trang bị chưa vẽ liền; coverage trung tính. Có PNG gốc/prompt/SHA/bounds, chưa native-grid hoặc layer-fit approved.
- Bảng concept BASE → PARTS → LOOK A/B/C, ghi rõ DESIGN STUDY–NOT GAMEPLAY; không dùng như atlas hoặc cắt concept thành bộ phận production.
- Prototype C# kiểm frame 16–20, shared canvas/ground, rig/poseSet/fingerprint, đủ bản ghi từng layer, occlusion, weapon family; một clock; atomic appearance swap và chặn stale revision/action/resource.
- Renderer prototype vẽ các pass bằng một CanvasItem, giữ nhóm trong world Y-sort, không độc lập scale/pivot từng mảnh. Chưa gắn vào hero.
- 60 job vẽ class mới đã liền trang bị chuyển HOLD_MODULAR_MIGRATION. 19 page ứng viên baked class chỉ reference;3 clip legacy còn giữ fallback. Không thay nhân vật đang chơi bằng pack nửa chừng.

## Kiểm chứng

- .NET 8/Godot build 0 warning/0 error.
- Native ModularCharacterTest:48 assertion qua, **fixture metadata**, không chứng nhận hình đẹp/fit/GPU.
- ActorLibrary regression:10421 assertion qua; giữ gate ảnh chưa duyệt và legacy fallback.
- Kiểm plan/candidate và export metadata đồng bộ; source PNG giữ nguyên byte từ imagegen tích hợp.
- productionReady=false:0/112 common direction-clip native master đạt; chưa có layer_pack_registry. Không được diễn giải 10 profile thành 10 nhân vật đã làm xong.
- Không dùng benchmark 60 FPS của cảnh art cũ làm bằng chứng crowd/paper-doll mới.

## Còn thiếu trước khi bật gameplay

Khóa master pose đúng grid/anchor/mask hai rig; đủ 8 hướng và pose class; garment/hair/face/weapon parts được fit vào chính master và kiểm theo fingerprint; exporter/loader/registry approved gắn SHA; palette/dye/under-hat variants; UI tạo nhân vật; adapter lưu appearance/equip/ownership server; migration save; stress test từng tổ hợp và crowd trên máy yếu.

Prototype không phải hệ đăng nhập/tạo nhân vật/đổi đồ online hoàn chỉnh. Các part trong test là metadata giả, không có spritesheet đồ thật được chứng nhận. Source base mới mới là ứng viên; chưa đủ 8 hướng và không được dùng làm giấy chứng nhận 16 pose cơ thể khác nhau bằng kiểm hash.

## Tệp chính

- Art_Source/Modular_Characters_20261107/README_vi.md, modular_character_plan.json, generation_records.json, structure_report.json.
- Sheets/body_human_male_idle_s_v 1.png và body_human_female_idle_s_v 1.png.
- Concepts/modular_system_study_v 1.png; prompt thực ở Prompts.
- ClientGodot/scripts/ModularCharacterModel.cs, ModularCharacterRenderer.cs, ModularCharacterSelfTest.cs.
- ClientGodot/ModularCharacterTest.tscn và Run_Modular_Character_Test.ps 1.
- Tools/ArtProduction/inspect_modular_candidates.py.

Không nhập code/asset LPC, không cài engine mới, không sửa wire enum hoặc dữ liệu chiến đấu. Nghiên cứu giữ hướng pixel 2D Godot.NET và quyết định 16–20 khung/60 FPS.
