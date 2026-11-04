# Nghiệm thu Bến Mưa native và đồ họa mới — 05/11/2026

## Kết quả có thể tái hiện

Godot 4.7.2 .NET, Compatibility/OpenGL3.3, GeForce820M; SDK8 client, SDK10 Health. Từ integration cf171786baebb10c3f17d3060d47429faf3e4026, Codex nối scene Godot với HTTP server loopback thật. P00-01 đã chạy nhận từ Ly An → đi nhặt3kiện → trả Tạ Vân Khanh → đọc túi20COIN+1EQ-MK-CHEST-T1-R-COMMON. Đây là áo trang bị, không phải chest/container. Không Unity, không local grant/teleport/private store fixture.

| Kiểm tra | Kết quả | Bằng chứng |
|---|---:|---|
| Native API scenario, mất reply sau commit + same-body/key retry, duplicate rejection, hai character isolation |25assertion, exit0|Evidence/Playable_Alpha_20261105/godot.stdout.log + run.json|
| Native UI scene, signal của button visible/enabled, bốn trang offer/hai reply/bốn trang turn-in/hai committed, authoritative reward |114assertion, exit0|ui.godot.stdout.log + ui.run.json|
| Camera/FOV/arc/map routes/atlas bounds |48assertion|camera.stdout.log|
| Input/physics/focus release/pier collision/canopy occlusion |9assertion|scene.stdout.log|
| Eight-direction walk/attack lifetime, cast dedupe,24/8VFXbudget, cancel clear |15assertion|visual.stdout.log|
| Reboot/environment/combat art validation |PASS|inspect_reboot.py / inspect_environment.py / inspect_combat.py|
| Catalog/source consistency,2656itemlabels |PASS|export_native_catalog.py --check|
| Muse scope gate |4tests PASS|python -m unittest discover -s Tools/Coordination -p test_*.py -v|

UI test phát Godot Button.Pressed, không physical mouse/pointer; movement đi qua public client/server và production panel handlers. API scenario không thay thế UI test. Camera/physics test ở offline authored staging, không chứng minh canonical online nav migration. Local rootclient build0warning/0error. Clean/incremental Health baseline khác nhau: full rebuild đã thấy4CS8602 warning có sẵn ở ServiceSelfCheck; không tuyên bố server sạchwarning.

## Runtime mới

NativeOnlineSession giữ một worker tuần tự, HttpClient timeout8s, lifetime epoch, command queue và detached DTO publication về mainthread. Không nhập ClientSession/TimeoutTransport đang review tại PR109. Portable/P1NativeCore.csproj link current tracked Core, Newtonsoft13.0.1 pin; HttpClientTransport vendored nguyên byte từ OpenCode685b888ae1ac42a314569602e1a4370a783f250c, SHA2565816b63e1eae5eaebd9122b42f9f23f7a4f6d9453b1716547a32fb9dddef9ea9.

Dialogue byte-copy nguồn v3, final action đợi server commit; inventory dùng item/currency thực, không fake level/XP/equip. NativeActorsView dùng entity positions/HP/life/AOI nguồn thực và tên từ canonical manifest. Gather sprites bind exacttypes; enemy healthbar4px bằng polygon tránh Control minimumheight làm khốiđỏ. Chỉ hiện sốHP cho target, tênmob/node theo proximity/selection để giảm chồng chữ.

Combat/VFX chỉ presentation: basic/accepted action body animation; TầmLong/KiếmTrận release dùng validatedCAST_START castId để dedupe; PhảnQuang chỉ release sau COUNTER_CONFIRMED (event không cần result). Counter cast không tự tạo counter success. Cancel/death/session change dọn VFX. Con sốdamage chỉ từ event.result. Full servertick geometry/timeline/reconnectlateimpact presenter còn thuộc O6, chưa nghiệm thu ở slice này.

## Đồ họa và hình thực

Art_Source/Combat_Visuals_20261105 chứa nguồn/prompt/metadata; dùng image_gen tích hợp. Không sửa PNG pixels bằng script. Runtime copies byte-identical, JSON vùng và footpivot theo ảnh thực:

- 32walk +32attack whole-body frame, tám hướng. Attackv1 bị loại vì sword vượt cell; v2 dùng4×8grid riêng, không ghép mảnh sai.
- 36phase VFX cho sáu skill Minh Kiếm; pool24/LowFX8, không collision/damage. Gallery đóng băng keyframe chỉ để review.
- Ly An/Tạ/thầy thuốc +kiện/áo/túi tiền; NPCtopregion608px giữ nguyên chân.
- Cá Linh/Rễ Nước mỗi loại3pose idle/attack/dead; năm loại node thực +mảnhấn decorative chưa bind gameplay.
- Sáu iconpixel kỹ năng đúng silhouette nguồn, đưa vào vòngcung46px quanhĐÁNH; có hotkey/tooltip và dim cho slotonline chưa hỗtrợ. native_hud_skill_arc.png là Godotcapture thực.

native_vfx_gallery.png là Godot render của environment và hiệu ứng; native_ui_p00_01_inventory.png là inventory sau completedquest. Chưa nghiệm thu tất cả gait/direction/equipmentlayers, nămclass/30skill/boss/fullNPC. Unknown mixedspawn không tự gán species.

## Map và giới hạn bản chơi

Camera64×36WU rộng, compact48×27 do người chơi chọn. ART_BM_STAGING_A2 authored128×96WU/113placement/14tuyến. Canonical online bounds vẫn360×84WU, x0..360,y−12..72; render=(560+20*x,896−20*y). Extendedgrass chỉ backdrop, không migrationnav/map. Server đang bố trí nhiều entity trên một trục; không tự dời NPC/quest để khớp concept. Qoder phải giao packetnav/transform/placement toàn map được review.

Launcher Run_Playable_Alpha.ps1 build/healthidentity/ownedPID/loopback; finally dừng đúng process nó tạo. MobBehavior và DeathReturnOFF, nên chưa là combat survive/boss/deathloop. Không sửa production config. Các bước ngoàiP00-01, v2equip12slot, forge/guild/trade/persistence/reconnect/campaign/mobile/export chưa được native nghiệm thu; **không gọi là MMORPG hoàn thiện**.

## Nhân sự tiếp tục gói29

Work29 đã merge qua PR117. Đã post góiO1–O8 tới85, Q1–Q8 tới87, R1–R8 tới79, M1–M8 tới116. OpenCodeCLI đã ACK trực tiếp rồi được resume, nhưng chưa có checkpoint SHA mới được review tại thời điểm báo cáo. Qoder/Muse/remote được giao quaGitHub; chưa suy ra đã hoàn thành từ việc giao task. Antigravity không nhận việc; Muse chỉvideo/cinematic/audio.

Hai lỗi portable đã tái hiện và gửiOpenCode: timeout40ms vẫn không kết thúc sau316ms nếu inner bỏquaCT; Dispose trong encounterread gây ObjectDisposedException ởSemaphoreSlim.Release. AlphaobjectIDs sáu giá trị exact được quyết định và gửi cảclient/server; không tự đổi ENT contract hoặc enumv1. Các lỗi này chưa được gói nativebridge tuyên bố đã sửa trong PR109.

Muse dùng NPCreference mới làm characterlock choP0video, không sửagraphics. DEC-MEDIA-P0/DEC-DEATH-RETURN/DEC-ALPHA-INTERACT-IDS đã chốt, không còn approvalcũ làm lý do dừng các phần độc lập.

Presentation origin sau QA được căn từx920 sangx560 để canonicalfirstquest18..64 nằm trong khu làng authored; vẫn20px/WU, servercoords/nav/IDs không đổi. Đây là translationrender, không migration.

QA native bổ sung: tán cây/nhà xét giao hình với body32×42px của player và NPC gần7WU, mờ28% khi che, khôi phục khi rời. Không chỉ xét một điểm đầu; screenshotworld thể hiện người chơi và Tạ tách nhau trong khu làng. UItest đứng cạnh NPC39.5/61.5 thay vì chồng đúng footpoint42/64, vẫn114assertion thực. Scenephysics/occlusion9assertion đã chạy lạiPASS.
