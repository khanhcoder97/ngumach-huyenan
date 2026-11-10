> Quyết định 10/11/2026 thay phần hình học/presentation: dùng registered master chung, bộ outfit phủ áo + quần, nón giữ tóc. Các PNG sinh riêng bị bác bỏ. Xem Registered_PaperDoll_Master_20261110_vi.md; không đổi trang bị/stat.

# Nhân vật ghép lớp và tạo diện mạo — quyết định 07/11/2026

Trạng thái: thiết kế triển khai + prototype hợp đồng, **chưa phải hệ tạo nhân vật/trang bị online hoàn chỉnh**. Theo yêu cầu trực tiếp của chủ dự án, dừng tạo mới nhân vật người chơi dưới dạng một sprite đã vẽ cố định tóc, giáp và vũ khí. Quyết định này bổ sung chuẩn 16–20 khung/60 FPS, không đổi engine, tọa độ, hitbox, class balance hoặc wire enum đang dùng.

## 1. Kết luận nghiên cứu

Dùng **paper-doll 2D theo pose**: thân người là animation vẽ từng khung; các bộ phận được ghép trên cùng pose, cùng canvas và cùng đồng hồ. Đây không phải việc dán vài PNG tĩnh lên nhân vật bất kỳ.

Tham khảo kỹ thuật đã đọc ngày 07/11:
- [Godot Sprite2D](https://docs.godotengine.org/en/stable/classes/class_sprite2d.html): atlas region, frame và offset; chỉ đồng bộ frame là chưa đủ nếu các phần không cùng hệ tọa độ.
- [Godot CanvasItem](https://docs.godotengine.org/en/stable/classes/class_canvasitem.html): actor root có thể được Y-sort trong khi các con giữ nguyên nhóm. Prototype dùng một CanvasItem tự vẽ theo thứ tự, không đưa tay/tóc ra Y-sort riêng.
- [Godot CanvasGroup](https://docs.godotengine.org/en/stable/classes/class_canvasgroup.html): có đọc backbuffer và chi phí theo vùng; không mặc định tạo CanvasGroup/SubViewport cho từng người trong thành phố.
- [Aseprite CLI](https://www.aseprite.org/docs/cli/): xuất layer/tag/sheet/JSON; giữ offset gốc khi pack trim.
- [Universal LPC Generator](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator), [architecture](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/blob/master/ARCHITECTURE.md): học cách tổ chức body, phần mặc và preset. Chưa nhập code/asset từ repo này; không tự áp lịch frame/góc của họ thay chuẩn của game.

| Cách làm | Đánh giá cho dự án |
|---|---|
| Vẽ sẵn mọi tổ hợp tóc/giáp/vũ khí | Số tổ hợp tăng theo tích; khó sửa và không đáp ứng đổi đồ linh hoạt |
| Sprite ghép lớp, chung pose master | Chọn: dễ kiểm từng phần, tái dùng đúng chỗ, runtime vẫn 2D |
| Bone-warp runtime cho toàn thân | Không chọn làm đường chính: dễ kéo giãn cụm pixel, khác yêu cầu frame-based |
| Dựng 3D rồi render offline | Có thể nghiên cứu sau; không cần buộc máy người chơi chạy 3D, nhưng hiện tăng việc dựng/rig nên chưa chọn cho MVP |

## 2. Hai rig chung, mười profile class/giới tính

Tài liệu Character_Equipment_Inventory đã quy định class không khóa giới tính. Cho phép nam/nữ ở cả 5 class. V1 dùng hai hình thể nền HUMAN_M/HUMAN_F; mỗi class/giới tính có baseId và poseSet riêng khi động tác khác nhau.

| Class | Base nam | Base nữ | Vũ khí hợp lệ |
|---|---|---|---|
| Minh Kiếm | BASE_MK_M_V1 | BASE_MK_F_V1 | JIAN |
| Ảnh Đao | BASE_AD_M_V1 | BASE_AD_F_V1 | DAO |
| Huyền Bút | BASE_HB_M_V1 | BASE_HB_F_V1 | BRUSH |
| Thạch Chùy | BASE_TC_M_V1 | BASE_TC_F_V1 | HAMMER |
| Linh Cung | BASE_LC_M_V1 | BASE_LC_F_V1 | BOW |

“Mười profile” không có nghĩa đã vẽ xong mười bộ animation. Idle/walk và các pose tương thích dùng chung nguồn theo rig. Basic attack và sáu skill phải có choreography riêng theo class; không thay một cây kiếm bằng cung rồi dùng động tác chém.

Thạch Chùy có silhouette nặng qua giáp, tư thế và vũ khí. Nếu cần cơ thể đô khác hình học thật, thêm rig/version và fit lại trang phục; không scale ngang một body hiện có. Ba silhouette ở tài liệu tiền sản xuất trước đây là phạm vi mở rộng, chưa phải ba body đã có asset. MVP chỉ bật lựa chọn đã có rig/đồ tương thích, không hiện preset giả.

Base là người trưởng thành cách điệu, đầu trọc, chưa có mắt/tóc/mũ/giáp/vũ khí. Có lớp áo lót/quần lót kín trung tính là phần coverage mặc định; không cần vẽ giải phẫu trần. Mặt, mắt, lông mày, miệng, dấu mặt là các phần độc lập hoặc biến thể head tương thích. Face preset V1 giữ silhouette/hairline chung, thay nét mặt; đổi hình học đầu cần head-fit variant riêng cho tóc/mũ, không scale méo một lớp.

## 3. Hệ tọa độ master

Thông số V1 để làm file authoring:
- Canvas chung 96×96 source pixel; gốc mặt đất (48,72); chiều cao cơ thể trung tính 36 pixel, phù hợp runtime hiện tại 20 pixel/WU.
- Toàn actor chỉ có một transform, một scale và một điểm chân. Không scale từng item theo alpha bounds hoặc chiều cao riêng.
- Mỗi pose có poseSetId/version, direction, frame index, fingerprint, anchors và paintOrder. Anchor tối thiểu: ground, head, face, chest, hip, hand_near, hand_far, foot_near, foot_far. Trang sức dùng thêm hand_l/hand_r theo giải phẫu; near/far chỉ điều khiển che khuất, không đảo nhẫn sang tay khác khi quay.
- Anchor là tọa độ integer của từng pose, được tác giả đặt theo hình thật; không lấy heuristic “70% chiều cao ảnh” làm dữ liệu cuối.
- Fingerprint production phải gắn cả source pose và guide/mask/anchor/paintOrder, xuất theo canonical bytes. Mỗi binding lưu ExpectedBodyPoses tương ứng từng frame; nếu sửa body/guide mà giữ tên poseSet, đồ cũ vẫn bị chặn vì fingerprint đổi. Thay palette bằng shader không đổi source pose. Không dùng tên frame thay SHA trong pack production.
- Source layer có thể untrimmed 96×96 khi authoring. Atlas xuất bản được trim/pack để tiết kiệm VRAM, nhưng bắt buộc lưu sourceSize và spriteSourceSize/offset để khôi phục đúng vị trí.
- Source rect trên atlas có thể khác nhau giữa các layer; **tọa độ trên canvas master không được khác hệ**. Không crop xong rồi quên offset.
- Nếu chiêu/áo choàng không vừa canvas, nâng version cho toàn rig/pack và retarget; không kéo/cắt riêng một layer.

Hai PNG base mới trong Art_Source/Modular_Characters_20261107 chỉ là ứng viên tạo hình/chuyển động hướng S. Chúng chưa được retouch/xuất đúng grid 96×96, chưa có mặt nạ tay trước/sau và chưa được dùng làm master fit đồ đã nghiệm thu.

## 4. Lớp hiển thị và che khuất

Các pass cơ bản: cape_back, hair_back, weapon_far, arm_far, body, legs, boots, chest_back, chest_front, gloves_far, face, eyes, brows, mouth, face_mark, hair_under_hat, hat_back, hat_front, hair_front, weapon_near, arm_near, gloves_near, cape_front, accessory, neck_accessory, ring_l, ring_r, pendant, seal_cosmetic.

Đây là tập token, **không phải một z-order cố định cho mọi frame**:
- Quay lưng: mặt/mắt có bản ghi hidden rõ ràng; không vẽ mắt xuyên đầu.
- Kiếm đi sau lưng phải ở weapon_far; tới trước người chuyển weapon_near. Bàn tay nắm cán phải đè đúng cán, không phủ toàn lưỡi.
- Giơ tay qua mặt: paintOrder của pose đưa tay trước lớp cần che. Không dùng một z-index toàn cục cho mọi người.
- Giáp/áo dài cần pass trước/sau để không nuốt tay hoặc chân. Váy/vạt áo theo pose chân, không dịch một ảnh quần áo tĩnh để giả chuyển động.
- Áo choàng dùng pass sau và pass trước khi bay ngang; không lấy áo choàng làm collider.
- Một actor được sort với cây/NPC/nhà bằng root chân; không để từng mảnh quần áo chen qua một actor khác.

Mũ có chính sách FULL_HAIR / UNDER_CAP_VARIANT / HIDE_HAIR / HOOD_VARIANT. Mũ trùm dùng biến thể tóc đã vẽ cho họ mũ; không cắt tóc theo hình chữ nhật tùy ý. Tháo mũ khôi phục hairStyle gốc. Tùy chọn ẩn mũ chỉ đổi hiển thị, không tháo stat item. Prototype hiện kiểm Hides token; việc chọn biến thể tóc/mask đầy đủ còn cần triển khai.

## 5. Quy tắc animation 16–20 khung

Thân người vẫn có 16–20 pose nguồn thực cho mỗi action/hướng. Mặc định 16, đủ 8 hướng; mirror chỉ khi đã chứng minh tương thích cho cả body/đồ/anchor/handedness và khai báo. Không dùng mirror cho chi tiết bất đối xứng có ý nghĩa.

Có hai loại phần mặc:
1. **Deformable:** áo/quần/vạt/áo choàng/giày mềm… có bản ghi tương ứng từng pose và artwork phù hợp pose. Tất cả binding phải cùng poseSetId và số frame với body.
2. **Anchored rigid:** mắt, phụ kiện nhỏ, mũ cứng, một số bộ phận vũ khí… được dùng lại hình nếu hợp phối cảnh, nhưng vẫn có 16–20 bản ghi đặt hình/variant theo pose. Ghi số hình nguồn duy nhất riêng; không báo một mũ tĩnh là “16 hình đã vẽ”. Không bone-warp hoặc xoay góc tùy ý làm nhòe pixel; dùng variant góc đã vẽ.

Một đồng hồ actor chọn clip/direction/frame; mọi phần lấy đúng key đó. Đổi đồ không reset động tác. Đổi hướng trong walk giữ phase, không khởi động lại ở frame 0 mỗi packet. One-shot giữ khung cuối; thay state gameplay theo event thật.

Render 60 FPS không đồng nghĩa có 60 pose nguồn. Clip 16 pose dài 0,8 s đổi pose 20 lần/s trong 60 lần render/s. Một pha VFX 0,16 s chỉ có khoảng 9–10 render frame ở 60 FPS nên không thể trình đủ 16 source frame trong pha đó; giữ timing server, lấy mẫu theo thời gian hoặc cho phần tan hiệu ứng kéo dài nếu thiết kế cho phép. Không kéo dài hit window để ép xem đủ pose. Toàn body action cần được xem trên timeline đầy đủ, không đếm riêng một pha quá ngắn thành hoạt ảnh hoàn chỉnh.

## 6. Trang bị, skin và màu

| Slot thiết kế | Pass đổi trên nhân vật |
|---|---|
| EQUIP_HAT | hat_back/front + chính sách tóc |
| EQUIP_CHEST | outfit đồng bộ áo + quần và sleeve fit |
| EQUIP_LEGS | giữ gameplay; không có visual riêng khi outfit đang mặc |
| EQUIP_WEAPON | weapon_far/near + grip family |
| EQUIP_GLOVES | gloves_far/near |
| EQUIP_BOOTS | boots |
| EQUIP_CLOAK | cape_back/front |
| EQUIP_SEAL | hiệu ứng nhỏ nếu có asset được duyệt |
| EQUIP_NECK / RING_L / RING_R / PENDANT | chi tiết trang sức tại ngực/tay/hông theo anchor giải phẫu; ở 36 px có thể chỉ 1–2 pixel, xem rõ hơn trong preview phóng nguyên |

Đây là render mapping của 12 slot thiết kế, không tự mở rộng enum/protocol backend. Current client/server chưa có đủ equip/appearance/create-character end-to-end; giữ hợp đồng đang dùng. Adapter backend chỉ chuyển ID item được server xác nhận sang visualFamilyId.

Thứ tự phân giải: coverage nền → diện mạo gốc → gear thật → cosmetic hợp lệ phủ những slot được khai báo → tùy chọn ẩn mũ/áo choàng → màu/palette → hiệu ứng trang trí được phép. Cosmetic không cộng stat, không đổi tầm đánh/hitbox/skill family. Skin kiếm không làm cung thủ sử dụng pose kiếm. Item full outfit phải khai báo coverageSlots; thay outfit không âm thầm tháo item gameplay.

Nhuộm theo palette ramp/mask của từng kênh, giữ highlight/shadow/outline. Không nhân màu RGB lên cả actor làm da, mắt, vũ khí đổi màu cùng áo. Skin tone đồng bộ body/tay/chân/đầu; hairColor không nhuộm lông mày trừ khi preset chỉ định.

Mục tiêu art hiện có:8 tông da,6 mặt,10 tóc,13 palette tóc,6 dấu mặt. Đề xuất bổ sung 6 kiểu mắt/8 palette mắt là mục tiêu sản xuất mới, chưa phải entitlement server. Chỉ bật UI preset có asset và quyền sử dụng thật.

## 7. Tạo nhân vật và thay đồ trong UX

Luồng mục tiêu: đăng nhập → chọn ô nhân vật → chọn class/vai trò → nam/nữ → da/mặt/mắt/tóc/màu/dấu → xem 8 hướng + idle/walk/đòn mẫu → tên 3–16 ký tự → xác nhận server → vào thế giới.

Preview dùng đúng renderer và resolver như gameplay, phóng nguyên 4× hoặc 6×; không dùng một portrait đẹp không khớp sprite chơi. Tùy chọn class thay pose/vũ khí thử mặc định; lựa chọn mặt/tóc còn tương thích được giữ khi đổi class/giới tính. Preset không hợp rig bị thông báo và trở về lựa chọn hợp lệ trong draft, không xóa quyền sở hữu.

Hai trạng thái tách rõ:
- previewDraft: thay tức thì khi thử, undo/reset; không equip, không mua, không trừ tiền.
- committedAppearance: chỉ đổi sau xác nhận server; gear/stat đọc riêng từ authority.

Mặc đồ hiện tại: chọn item → xem so sánh/thử nếu có asset → gửi equip → pending → receipt/snapshot → áp toàn bộ look cùng revision. Khi asset chưa sẵn sàng, không đổi vài mảnh rồi để phần còn lại cũ. Stat mới vẫn áp theo server; không chờ art để trì hoãn combat. Cần preload trước hoặc giữ một presentation dự phòng rõ trạng thái; PvP phải giới hạn vào các pack đã được tải/duyệt.

Salon Vân Như giữ quote/chi phí ở spec hiện hành. Mục tiêu bước này không tạo shop mới, không cấp cosmetic miễn phí ngoài quy tắc hiện có. Đăng nhập/tạo nhân vật và lưu diện mạo thật hiện **chưa có trong packet prototype này**; không giả “đã lưu tài khoản” bằng file local.

## 8. Dữ liệu và đồng bộ

Một visualFamilyId phân giải variant theo classId + rigId + poseSet; prototype Part là thành phần đã phân giải cho class/rig hiện tại, không phải một bảng binding dùng chung mơ hồ cho mọi class. Giáp dùng chung phải có các binding tương thích riêng khi class có pose khác.

Dữ liệu lưu/đồng bộ mục tiêu gồm: characterId, appearanceSchemaVersion, classId, bodyFrame/sex, facePreset, eyePreset/eyePalette, skinTone, hairStyle/hairPalette, faceMark, equippedVisualFamilies, cosmeticLoadout, hideHat/hideCloak, dyePaletteIds, equipmentRevision, appearanceRevision, catalogVersion.

Server chỉ chấp nhận ID allowlist/quyền sở hữu; không nhận đường dẫn texture, URL, shader hoặc stat từ client. Validate class/weapon/rig tương thích, đủ quyền và idempotency. DTO/endpoint mới cần packet riêng; đây chưa phải đường API đã chạy.

Remote actor bỏ revision cũ, reset theo character/life/session khi đổi người. Thay appearance không đổi entityId/HP/collider/position. Tải bất đồng bộ phải kiểm token/revision lần nữa trước commit. Mất kết nối khi lưu giữ trạng thái chưa rõ kết quả và retry cùng key, không trừ salon hai lần.

Migration avatar cũ không có lựa chọn giới tính: giữ sprite fallback, không đoán giới tính từ class. Khi mở pipeline mới cần màn chọn diện mạo một lần và migration được review, không âm thầm reset tên/đồ/quyền sở hữu.

## 9. Sản xuất asset

1. Khóa tỷ lệ/camera/master pose hai rig bằng base đơn giản.
2. Vẽ đủ common clips, rồi pose class/weapon riêng,16–20 khung/hướng.
3. Đặt anchor/paintOrder/mask trên source master có layer. Giữ tay trước/sau thành pass phù hợp.
4. Fit áo/quần/giày/mũ/tóc/vũ khí lên chính master đó. Mỗi item mới phải hỗ trợ mọi rig/class/action mà nó cho phép.
5. Xuất layer/tag thành atlas+JSON, trim/pack kèm offsets; kiểm khôi phục canvas khớp từng pixel.
6. Test bộ stress: mũ rộng+tóc dài, hood, giáp vai lớn, áo dài+boots, cloak+bow, vũ khí hai tay,8 hướng+đòn chéo/death.
7. Khi đạt fit/motion/native/device QA mới đưa pack vào registry production.

Imagegen tạo concept/base/ứng viên; không kỳ vọng sinh áo và body độc lập sẽ khớp từng pixel. PNG phẳng không tự có layer ẩn; phần bị giáp che không thể được khôi phục chính xác chỉ bằng cắt ảnh. Chưa có file master layer được nghiệm thu, nên chưa tự nhận đã tách được toàn bộ sprite cũ.

Tham khảo lệnh export Aseprite (chưa chạy trên master production):
```text
aseprite.exe -b --all-layers --split-layers master.aseprite --sheet parts.png --data parts.json --format json-array --border-padding 2 --shape-padding 2
```
Lệnh minh họa xuất mọi layer, kể cả layer ẩn. Với master thật, whitelist layer render hoặc đặt --ignore-layer cho GUIDES/COLLISION/NOTES trước input; không phát hành các lớp chỉ dẫn. Chỉ export sau khi layer/tag được đặt tên đúng; không dùng merge-duplicates để giả đủ pose body. Rigid part reuse phải có mapping rõ.

Pilot trước khi mở rộng: Minh Kiếm nam/nữ, idle/walk/basic/skill 01,8 hướng,2 bộ đồ/2 tóc/2 vũ khí/1 mũ. Pilot chỉ dùng phòng thử fit; không bật gameplay với bộ clip còn khuyết hoặc đổi sang avatar liền đồ giữa chiêu. Khi đạt quy tắc master, mới nhân rộng cả 5 class và wardrobe.

## 10. Khối lượng và hiệu năng

V1 có 7 common action và 7 action riêng/class (basic+6 skill). Hai rig ×8 hướng×16 pose:
- common:1.792 pose cơ thể;
- class-specific:8.960 pose;
- tổng 10.752 pose cơ thể nếu vẽ đủ 8 hướng, chưa gồm layer trang phục.
Nếu 5 hướng nguồn+3 mirror được phép cho từng pack, tổng còn 6.720 pose nguồn; không gọi là 10.752 hình vẽ riêng. Dùng 20 pose tăng 25%. Outfit cost tăng theo số phần×pose tương thích, không theo mọi tổ hợp màu/tóc/giáp.

Thông số là phép đếm scope, không phải cam kết đã tạo hoặc thời gian hoàn thành. Các part rigid, palette, pose dùng chung giúp giảm việc nhưng không xóa công việc fit/deform thực.

Runtime:
- Một actor root, một clock, painter-order cục bộ; queue redraw khi pose/look đổi, transform render vẫn 60 FPS.
- Dùng atlas trim, dùng chung Texture2D; không tạo bản texture riêng cho mỗi tổ hợp màu.
- Không bake giữ toàn bộ 128 frame RGBA cho mỗi appearance của mọi người. Cache draw-command theo pose; cache texture có ngân sách chung/refcount.
- Prototype renderer giới hạn 16 texture/clip và 32 MiBước lượng texture được giữ/actor; đây là guard thử nghiệm, chưa phải ngân sách crowd cuối.
- Mục tiêu cần đo:10/25/50/100 người, nhiều outfit/đổi đồ, mưa/combat, cold/warm cache; median/p 95 frame time, texture memory và draw calls.
- Benchmark 60 FPS của scene ActorLibrary cũ không được dùng làm bằng chứng paper-doll đông người đạt 60 FPS.

## 11. Nghiệm thu và phạm vi code hiện có

Model prototype: kiểm rig/poseSet/frame count, nguồn body khác nhau, canvas/origin/anchor, layer order, tương thích vũ khí, record hidden và stale revision. Cùng một đồng hồ, gear swap không reset action; chuẩn bị đủ nguồn trước atomic swap. Renderer Godot dùng draw commands trong một CanvasItem; chưa gắn vào HeroAnimator đang chơi.

Test logic dùng fixture metadata, không chứng nhận hình đẹp, đủ pose đã vẽ, fit quần áo hoặc tốc độ GPU. Production cần approved manifest gắn SHA, loader và catalog hợp lệ, item visual bindings, server appearance/create-character/equip adapter, UI và device QA; các phần này không được coi là đã xong nhờ có prototype.

Đường dẫn:
- Art_Source/Modular_Characters_20261107/modular_character_plan.json:2 rig/10 profile, layer tokens, slot mapping và blocker.
- Sheets/Prompts/generation_records/structure_report:ảnh base ứng viên và prompt thật.
- ClientGodot/scripts/ModularCharacterModel.cs, ModularCharacterRenderer.cs, ModularCharacterSelfTest.cs.
- ClientGodot/ModularCharacterTest.tscn:chỉ chạy test contract, không tạo account hoặc equip item.
- Các job class full-body baked trong queue trước chuyển HOLD_MODULAR_MIGRATION; source cũ giữ tham khảo và fallback. Quái/NPC/VFX không thuộc yêu cầu thay đồ người chơi vẫn theo pipeline của chúng.

## 12. Phòng thử authoring đã triển khai

PaperDollLab.tscn đã có preview ghép lớp thật, chọn base nam/nữ, thử 16 phần tĩnh và chỉnh/lưu fit draft theo pose. Đường review cho phép hiệu chuẩn nguồn cố định theo atlas; đường production vẫn bắt buộc native pixel scale=1. Công cụ chưa hoàn thành pilot 8 hướng/action hoặc tạo nhân vật online. Chi tiết: [PaperDoll_Fit_Lab_20261107_vi.md](PaperDoll_Fit_Lab_20261107_vi.md).
