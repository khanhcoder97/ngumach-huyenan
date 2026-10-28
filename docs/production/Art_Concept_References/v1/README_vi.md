# Concept reference v1 — chỉ đạo mỹ thuật cho Muse

Ngày2026-10-29. Theo yêu cầu chủ dự án, Codex tạo năm board raster bằng công cụ built-in image_gen.imagegen; prompt đầy đủ ở generation_prompts.json. Đây là hình tham chiếu mỹ thuật có kiểm tra bằng mắt, **không phải texture/sprite sheet runtime, không phải topology map và chưa là phê duyệt cuối của chủ dự án**. Không crop/thu nhỏ hàng loạt board thành asset rồi báo đã hoàn tất.

## Năm mẫu và phần cần học

| File | Dùng làm mẫu | Phần không được chép thành luật |
|---|---|---|
| 01_minh_kiem_model_sheet.png | silhouette, tóc xanh, tương phản choàng đỏ/áo teal, kim loại gọn, kiếm vàng | board có ngọc guard chưa rõ lục giác, thêm băng đầu, tỷ lệ phóng lớn và swatch không phải palette khóa; phải sửa theo DEC-015 |
| 02_ben_mua_thang_long_environment.png | mood mưa xanh và thành phố ấm, vật liệu mái/gỗ/nước/đá, sự sống quán chợ | phối cảnh có chiều sâu và ground quá nhiều chi tiết; không dùng làm tọa độ/collision/nav; dựng lại top-down, giảm texture noise |
| 03_npc_creature_board.png | Ly An dễ gần, Tạ trầm, Hạ Mặc tò mò; cá/rễ/rắn có silhouette khác nhau | tay băng của Tạ trong board có thể sai bên: phải tay trái nhân vật; tuổi Hạ Mặc cần30–40; số rễ/sừng/hoa văn theo brief, không theo lỗi ảnh sinh |
| 04_pixel_hud_components_vfx.png | phân cấp UI, brass mảnh/nền tối, component states, cú chém có ba pha | text quest/rarity trên ảnh là minh họa, không canon; hero trong mockup có thể cầm kiếm sai màu; không tự đổi item rarity schema hoặc skill icons theo ảnh |
| 05_five_classes_lineup.png | năm silhouette/weapon role, palette tương ứng, cùng họ thẩm mỹ | giới tính/ngoại hình là variant mẫu, không khóa lớp; arccher pose phải kiểm draw-hand/string, brush/hammer phải gọn khi vẽ48×64 |

Ảnh được sinh ở độ phân giải board lớn nên không đảm bảo từng ô pixel48×64 hoặc palette<=40. Muse cần vẽ lại theo grid, không tự nhận board là ảnh đạt chuẩn pixel runtime chỉ vì có cạnh răng cưa.

## Quyết định hình ảnh cụ thể

1. Hero/npc gameplay cell48×64,20PPU, pivot(0,5;0), foot contact ổn định. Dùng chung đầu/thân/hông giữa tám hướng; không để góc khác biến thành người khác. Nhân vật mẫu khoảng2,7đầu là đích blockout; board phóng lớn chỉ hướng tạo hình, không áp pixel đo trực tiếp.
2. Outline ngoài1px nguồn; vùng tối sâu nhất dùng outline, tránh viền2px mọi chi tiết làm bết. Mỗi vật liệu3–4tone chính, highlight thành cụm>=2px; không dải highlight rải đều như kim tuyến.
3. Tóc xanh có3mảng lớn: đỉnh, mái, gáy; không thêm từng gai mới ở từng hướng. Choàng chỉ1mảng chính+2nếp lớn, không nuốt tay/chân. Gem kiếm đúng một ngọc lục giác xanh; giữ cùng màu/vị trí trên mọi pose.
4. Weapon/silhouette tách rõ: Minh Kiếm broad straight sword, Ảnh Đao một dao cong, Huyền Bút bút lớn, Thạch Chùy chùy đá, Linh Cung cung gỗ. Không đổi thành dual katana/staff axe/khẩu súng để dễ sinh ảnh.
5. Màu gợi ý chung: outline #1D2233; navy #28344C; slate #52616B; parchment #E7D8B5; ivory #FFF0CD; brass #B78543; gold #E8BB63; teal #28747A; jade #68B8A4; cape #A93E40; cape shadow #652938; hair blue #3D6AC2. Đây là seed palette đề xuất cho mẫu, không ép mọi biome dùng cùng12màu.
6. Bến Mưa: ground tối trung tính, nước lam xám, lá rêu, đèn vàng chấm nhỏ. Thăng Long: đá ấm ít noise, mái gạch, vải indigo/ochre. Đường đi ít chi tiết hơn prop, không phủ cỏ/hạt đá tương phản mọi ô. Mỗi tile đất chỉ một điểm nhấn mạnh, không white speckle toàn map.
7. HUD tối giản để giữ tầm nhìn: HP đỏ, MP xanh; Kiếm Ý5pips. Viền brass1px/2px theo component, không giant filigree. Icon32px nguồn có silhouette rõ ở native; text thật do localization/font game, không lấy chữ ảnh sinh.
8. VFX đọc ba pha startup/impact/resolve, không bloom/blur; cue nguy hiểm đỏ-cam có shape riêng, hit effect vàng-trắng không lẫn boss telegraph. Quái Cá Linh mềm/tròn, Rễ Nước chạc gốc, Mãng Cốt đường cong dài; không dùng cùng hình blob recolor.

## Vòng sửa bắt buộc trước nhân rộng

**Gate A — một pose native.** Muse giao Minh Kiếm S,SE,N ở48×64 (3ảnh riêng), crop không scale và preview4× nearest. Kèm palette file, sword/cape/hair invariants, defects list; so với board01 và DEC-015. Không sinh full128clip ở bước này.

**Gate B — độ nhất quán hướng.** Sau review A mới đủ8hướng, mỗi hướng một idle pose; overlay pivot/foot baseline trên contact sheet riêng. Tay cầm đổi đúng theo góc chứ không tự mirror gem/bao kiếm sang vị trí vô lý. Hướng gương có thể reuse nếu art brief cho phép và kiểm hình thực, không chỉ hash.

**Gate C — animation.** Walk6frames/hướng@8fps, rồi idle/hurt/death/attack. Giữ foot slide thấp, không bóp méo thân/weapon. Mỗi lần giao1action trước khi làm action kế; gameplay hit/CD do server, không đổi timing theo clip.

**Gate D — scene.** Một hero+Ly An+Cá Linh+4×4tile ground/shore/water đặt trong mockup640×360. Kiểm silhouette và noise thực ở native, rồi720p/1080p; scene video không cần giả engine evidence nếu chỉ là animatic.

**Gate E — tích hợp.** Manifest/PNG/.meta/refs hợp lệ, Unity import/playback log exact SHA khi môi trường có; không có Unity thì ghi unverified và giao source cho máy build khác. ART_APPROVED không thay ENGINE_IMPORTED/DEVICE_QA.

## Scorecard review (nội bộ mỹ thuật)

| Miền | Điểm | Quan sát |
|---|---:|---|
| Silhouette/đọc ở native |25| tách tay/chân/weapon, thấy hướng và role |
| Nhất quán design/tỷ lệ |25| tóc/kiếm/gem/cape không drift, cùng nhân vật8hướng |
| Pixel clusters/palette |20| ít noise, không anti-alias/resample, cụm màu có chủ đích |
| Pose/animation/foot contact |15| weight và action đọc rõ, pivot ổn |
| Handoff/evidence |15| source/metadata/preview/license/defects thực |

Mục tiêu review>=85/100 để mở rộng. Sai ID, silhouette ngoài cell, thiếu tay/chân, sai sword/gem, palette drift lớn hoặc fake runtime evidence là fail dù tổng điểm cao. Không tự chấm board AI là100điểm; reviewer ghi nhận xét cụ thể và attachment.

## Cách Muse dùng mẫu

Reference board không phải edit target. Bắt đầu từ bố cục silhouette giản lược trên grid, chọn palette, làm một pose rồi mới tăng chi tiết. Prompt tiếp phải ghi rõ assetId, camera, native cell, pose, invariant và một thay đổi cần sửa; không dùng câu “make beautiful” thay yêu cầu.

Ví dụ Gate A: “Draw original Minh Kiếm native pixel sprite in a single48×64 transparent cell, facing S, foot pivot bottom center. Match approved blue hair/red cape/teal ivory tunic/gunmetal armor/gold sword with one GREEN HEXAGON guard gem. Three large hair clusters,2cape folds,3tones per material,1px outer contour. Feet separate, sword clear of torso. No headband unless design reviewer approves it, no blur/gradients/extra limbs. Deliver source native plus4×nearest preview; this is one pose, not a full sprite sheet.”

Nếu công cụ không tạo đúng48×64, Muse phải pixel-redraw/cleanup ở editor rồi export; không chỉ resize ảnh lớn và gọi là completed. Ghi phương pháp thật trong PR.
