# Thư viện asset — đợt 20261112f

Đợt này bổ sung **15 sheet được chọn / 240 ô nguồn**: 10 sheet bị thương, gục ngã của Rễ Nước và 5 component VFX cho năm lớp. Mỗi sheet có 16 khung nguồn, giữ sprite chibi nguyên khối đã chốt. Dùng `image_gen` tích hợp, giữ nguyên byte PNG và prompt thực; không vẽ bitmap bằng code hoặc lặp 8 pose để bù 16. Đợt bắt đầu ngày 12/11, kiểm bản cuối ngày 13/11/2026.

## Rễ Nước: bị thương và gục ngã

| Action | Hướng vẽ nguồn | Ô nguồn | Nhịp xem |
|---|---|---:|---:|
| hurt | N, NE, E, SE, S × 16 | 80 | 0,30 s, một lần |
| death | N, NE, E, SE, S × 16 | 80 | 1,20 s, giữ khung cuối |

SW/W/NW dùng lật SE/E/NE theo policy của quái, thành tám hướng xem. Không cộng hướng lật thành ảnh vẽ mới. N/NE không lộ hạt sáng mặt trước; E chỉ lộ mép phải; SE/S thấy hạt theo góc trước. Giữ rễ gỗ ướt, chạc cuộn, rêu và lá xanh lam; không thêm tay/chân người.

`hurt` là một nhịp chạc rễ và lá oằn lại, rồi trở về trung tính. `death` hạ dần thành búi gỗ/rêu thấp, không đứng dậy ở cuối và không biến mất. Năm bản gục có chiều cao ảnh ở khung thấp nhất khoảng 77–82px nguồn, so với chiều cao đứng tham chiếu 154–168px. Tỷ lệ hiển thị cố định từ ba pose đứng đầu; không phóng xác lên bằng chiều cao thân đứng.

Hai action dùng đăng ký `FOOT`, không khóa lõi rêu đang oằn hoặc sụp xuống. Bộ idle/báo/đánh/hồi trước đó vẫn dùng `MOSS_CORE_ROOT` và offset chân idle chung. Không sửa pixel nguồn, collider hoặc sát thương. Các clip mới đã có trong nhóm hướng của Actor Library, Studio và ô hurt/death của cảnh combat review.

Generator kế hoạch cũng được sửa: prompt quái không còn mặc định động tác “khụy gối/chống tay” của người khi gục. Rễ Nước có chỉ dẫn sụp rễ riêng; quái khác yêu cầu chuyển động theo giải phẫu thật. Đây là sửa yêu cầu sinh ảnh cho các đợt sau, không phải ảnh mới hoặc bằng chứng quái khác đã hoàn tất.

## Năm component kỹ năng

| ID nguồn | Kỹ năng | Thiết kế đã kiểm | Thời lượng preview |
|---|---|---|---:|
| `sk_mk_01_parry_component` | Phản Quang / Minh Kiếm | Cung đỡ hình học vàng, một lần lóe ở viền rồi vỡ thành tia nhỏ; tâm hở | 0,40 s, một lần |
| `sk_ad_01_cut_component` | Huyết Nguyệt / Ảnh Đao | Lưỡi liềm đỏ sẫm, cam tại mép cắt; tan thành vệt nhỏ, không máu me | 0,32 s, một lần |
| `sk_hb_01_ink_hit_component` | Mực Triều / Huyền Bút | Vệt mực lam chàm mép rách, bắn thành đốm; không phải đạn cầu | 0,32 s, một lần |
| `sk_tc_01_dust_component` | Trấn Sơn / Thạch Chùy | Bụi đá vàng xám thấp và mảnh đá nhỏ; neo tại chân | 0,35 s, một lần |
| `sk_lc_01_mark_component` | Khóa Mạch / Linh Cung | Hai nhánh ngọc ôm khoảng rỗng quanh mục tiêu; lá mở rồi khép gần dáng đầu | 1,00 s, phát vòng |

Mỗi component có 16 ô nguồn riêng, tổng 80 ô. Đây là **thành phần hình ảnh**, chưa thay thế toàn bộ cast/projectile/hit/loop/end của kỹ năng. Dấu Khóa Mạch có thời gian đánh dấu 5s theo thiết kế kỹ năng; vòng preview 1s không cấp hoặc gia hạn trạng thái gameplay. Bụi Trấn Sơn không phải decal nứt đất, vật cản hoặc hitbox. Hướng/cỡ component vẫn cần gắn theo actor/skill khi tích hợp gameplay.

Thời lượng ở bảng là giả định trình bày có thể chỉnh. `previewDurationSeconds` / `previewLoop` xuất vào metadata và được Studio đọc trực tiếp. Pipeline chỉ cho component khai báo cặp trường này, từ chối thời lượng không hữu hạn, flag sai kiểu và clip ngắn hơn 16/60s khiến review 60 bước/s bỏ pose. Đổi timing hoặc chế độ vòng làm thay binding SHA256 và yêu cầu kiểm lại. Không đổi pin của nguồn cũ không có profile.

Bản Khóa Mạch v1 có nhịp lớn lên lần hai ở hàng cuối, gây nhảy kích thước khi quay vòng; v2 được chọn sau kiểm native. PNG/prompt v1 và bằng chứng được giữ trong lịch sử. Bụi Trấn Sơn chuyển metadata từ `CELL_CENTER` sang `FOOT` để không nằm dưới neo mặt đất; PNG không đổi. Các component khác dùng tâm ô cố định để không kéo hiệu ứng theo bounding box đang tan. Mẫu alpha ở tâm Phản Quang và Khóa Mạch là 0–1/255; ảnh native xác nhận khoảng hở vẫn nhìn xuyên được.

## Mở xem và chỉnh tay

```powershell
.\ClientGodot\Run_Actor_Library.ps1 -SkipBuild -Actor MOB_WATERROOT -Clip hurt
.\ClientGodot\Run_Actor_Library.ps1 -SkipBuild -Actor MOB_WATERROOT -Clip death -Frame 15
.\ClientGodot\Run_Actor_Library.ps1 -SkipBuild -CombatReview -Actor MOB_WATERROOT -Direction SE
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_WATERROOT:death -Direction N -Frame 15
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry sk_ad_01_cut_component -Play
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry sk_lc_01_mark_component -Play
```

Bỏ `-SkipBuild` trên checkout mới để build/import. Studio giữ pivot/tọa độ/layer/socket, timeline, tốc độ, onion skin, undo/redo và xuất JSON/bundle riêng. PNG gốc không bị ghi đè. Actor Library phát vòng cả action một lần để xem lặp; Studio dùng one-shot mặc định, giữ khung cuối. Video review bốn VFX một lần dùng override vòng chỉ để quan sát nhiều chu kỳ.

## Kiểm tra và phạm vi bàn giao

- 15 quyết định kiểm source/component pin PNG SHA256 và binding SHA256. Không tự duyệt toàn actor, kỹ năng hoặc encounter.
- 46 PNG baseline chủ dự án chọn giữ đúng SHA256; 120/120 nguồn runtime đang được chọn khớp byte PNG gốc.
- .NET 8 build: 0 warning/error; Godot import đạt; 33 Python tests; native library 12.799 assertions; Studio 58.476 assertions / 170 entries. Cue pha Rễ Nước 6 assertions và component Kiếm Trận cũ 14 assertions đạt.
- Kiểm native mở rộng sang hai action mới ở tám hướng: đủ 16 frame, nhịp raw/group trùng, không lặp action one-shot. Năm profile component được kiểm đủ 16 pose khi lấy mẫu đồng hồ 60 bước/s và đúng ranh giới vòng/giữ cuối.
- 9 MP4 native đang được chọn: hai action tám hướng, năm component, hai cảnh combat N/SE. Có ảnh tĩnh, dải mẫu thời gian, log và kiểm giải mã/hash. Video xuất offline ở 60 bước/s; **không chứng nhận gameplay đạt 60 FPS thực**. Dải mẫu lấy theo thời gian, không phải sheet nguồn hoặc bảo đảm mỗi ô trùng đúng một source frame.

Catalogue hiện có 123 page qua structure, **52/1008 job đủ góc nguồn, 16 job đủ góc đã kiểm source**, còn 956 job thiếu. Vẫn có 21 active HOLD và atlas full VFX cũ sai số hàng. Component tách không làm tăng số full skill job đã khép. Rễ Nước có 6/12 action đủ nguồn và đã kiểm: idle, ba pha roi rễ, hurt, death. Còn walk/run/turn và ba pha chồi đất. Walk NPC Người Giữ Thuyền E/NE còn HOLD; các phần class/quái/boss/NPC, map/tile/UI/icon/audio khác tiếp tục theo catalogue.

Nguồn/prompt: `Art_Source/Actor_Library_20261107/Sheets/`, `Prompts/`, `generation_records.json`, `generation_history.json`. Inventory lựa chọn: `batch_20261112f.json`; inventory a–f cập nhật snapshot catalogue hiện hành. Bằng chứng: `Implementation/Reports/Evidence/Actor_Batch_20261112f/`, gồm `visual_decisions.json`; bản sửa cũ ở `Superseded_Registration_Or_Loop_v1/`.

Đợt này bàn giao nguồn và khả năng xem/chỉnh trong tool. Chưa nghiệm thu thay renderer gameplay, AI, collision/hit, LowFX trong chiến đấu hoặc PCK/shipping; chưa hoàn tất thư viện toàn game.
