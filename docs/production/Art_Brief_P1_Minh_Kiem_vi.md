# Art Brief P1 — Nhân vật Minh Kiếm


> DEC-016 (2026-10-28): áp dụng `Top_Down_Gameplay_World_Spec_vi.md`. Các bảng kích thước/placement cũ là blockout chưa nghiệm thu top-down. Y luôn là Bắc–Nam trên mặt đất. “Platform” là bệ/cầu/vùng an toàn có đường đi hoặc floor link, không yêu cầu nhảy; chiều cao silhouette/capsule cũ không dùng làm collider. ID được giữ; không tự chuyển tọa độ cũ thành độ cao.

**Trạng thái:** brief sản xuất, chưa phải concept đã duyệt hay asset production.  
**Gói liên quan:** `ART-P1-002` character sheet, `ART-P1-003` combat clips, `ART-P1-017` skill VFX trong `Art_Production_Queue_P1_vi.md`.

**Tạo hình đã chốt (chủ dự án, 2026-10-27, DEC-015):** chibi kiếm sĩ tóc xanh gai; kiếm vàng bản lớn, guard gắn ngọc lục giác; áo choàng đỏ; áo teal viền trắng; khóa thắt lưng lục giác vàng; giáp thép đen (gunmetal) viền vàng ấm ở vai, găng tay, ống chân và ủng. Hai SVG concept cũ đã chuyển khỏi Unity Assets vào `docs/production/Art_Concepts_History/`, chỉ lưu lịch sử và không được dùng làm runtime/nguồn hình để upscale. Sheet đi bộ draft v2 đã được Muse dựng theo tạo hình này và qua audit (48/48 cell, 6 frame khác nhau mỗi hàng, không tái dùng frame giữa các hàng, SW là gương khớp tuyệt đối của SE); đang chờ duyệt cuối trước khi vào repo.

## 1. Nguồn chuẩn và ranh giới

- Art direction: pixel art frame-based cho fantasy võ hiệp huyền thuật Lạc Châu; dùng cụm pixel sạch, palette giới hạn, silhouette rõ; không vector/HD render hay bone-warp. Tuân thủ `Pixel_Art_Production_Standard_vi.md`; không dùng lại asset/nhân vật/hoa văn nhận diện từ KPAH/JAR.
- Gameplay role: cận chiến hệ Kim; combo tích Kiếm Ý, đỡ nhịp chuẩn rồi phản kích. Nguồn: GDD và `Combat_Skills_VFX_Animation_Spec_vi.md`.
- Tạo hình class master trong Art Bible (`NPC_MASTER_MINH_KIEM`) là áo dài chéo vạt, kiếm bản mảnh, khóa kim loại lục giác, tư thế thẳng tay gần chuôi, vàng nhạt/xám bạc. Dùng như motif của môn phái; người chơi phải có silhouette và trang phục riêng, không phải bản sao NPC master.
- Những chi tiết đề xuất bên dưới là quyết định mỹ thuật cần duyệt; không tạo luật gameplay, chỉ số hoặc ID content mới.

## 2. Silhouette và model sheet

**Kích thước chuẩn:** cell hiển thị 2,4×3,2 WU; footprint capsule ngang 1,2×0,6 WU, offset (0;0,3). Sheet gameplay dùng cell 48×64 source px ở 20 PPU, lưới 8 hướng × 6 frame = 288×512, pivot bottom-center; hiển thị 192 px tại 1080p scale 3×. Turnaround front/side/back, portrait, swatches, props, năm biểu cảm và scale figure cạnh NPC/quái chuẩn vẫn là deliverable thiết kế bổ sung bằng pixel art.

**Silhouette đã chốt:** chibi đầu lớn/thân gọn, tóc xanh gai dựng, vai giáp thép đen góc cạnh, tay chân ngắn, ủng chắc. Kiếm vàng bản lớn là điểm nhấn silhouette chính; áo choàng đỏ bay sau vai tạo mảng tương phản. Tư thế sẵn sàng chiến đấu, biểu cảm lạnh và quyết tâm (hướng NGẦU đã chốt, không mềm/dễ thương). Mỗi frame dùng pixel cluster gọn, outline 1–2 pixel nguồn, không anti-aliasing.

**Trang phục đã chốt:** giáp thép đen (gunmetal) ở vai, găng tay, ống chân và ủng, viền vàng ấm; áo teal viền trắng; thắt lưng có khóa lục giác vàng; áo choàng đỏ. Sprite sheet có thể tách layer nhưng từng layer phải giữ pixel grid và không làm thay đổi collision/hitbox.

**Vũ khí:** kiếm vàng bản lớn (broad sword), guard gắn ngọc lục giác, không phát sáng ở trạng thái thường. Đây là tạo hình thị giác đã chốt; thông số gameplay của class (kiếm thẳng hệ Kim) giữ nguyên theo combat spec. Phân lớp sprite hoặc vẽ variant riêng để thay ngoại trang `COS-WP-01` mà không đổi anchor, hitbox hoặc timing.

**Palette key:** đỏ cho choàng; vàng cho kiếm và khóa thắt lưng; thép đen (gunmetal) cho giáp; vàng ấm cho viền giáp; xanh dương cho tóc; teal cho áo; da ấm. Tối đa 24–40 màu cho bộ nhân vật; dùng palette ramp pixel và highlight theo cụm. Trên nền mưa xanh Bến Mưa, mảng đỏ của choàng và vàng của kiếm phải giữ silhouette; LowFX giữ palette và cue.

## 3. Sprite sheet, layer và anchor

- Sprite sheet gameplay: lưới 8 hàng hướng (N, NE, E, SE, S, SW, W, NW) × 6 frame walk, cell 48×64, nền trong suốt; sản xuất theo quy trình strip từng hướng → ghép bằng code → audit đếm pixel (xem `Pixel_Art_Production_Standard_vi.md` §8). Variant đầu/tóc, thân, vai, tay, giáp hông, ống chân, choàng và phụ kiện chỉ tách layer khi composite giữ nguyên pixel grid/pivot. Choàng có 2–3 frame phụ để gợi chuyển động, không bone-warp. Tách kiếm/bao kiếm hoặc vẽ variant; anchor tọa độ pixel để đổi vũ khí.
- Bắt buộc có anchor tay cầm, đầu kiếm, hông/bao kiếm, chân và tâm thân để gắn VFX/đạo cụ. Tên socket kỹ thuật do engineering chốt trong prefab; không biến tên socket thành content ID.
- Collision capsule không đổi theo frame/ngoại trang. Sprite animation không quyết định vị trí mạng, trúng đòn, hướng tấn công hoặc reward.
- Sheet phải có silhouette trung tính, đồng minh và mục tiêu. Outline đội/target là layer UI/render riêng, không tô lại texture gốc.

## 4. Clip và nhịp diễn xuất

| Clip | Vận hành hình ảnh | Khóa gameplay |
|---|---|---|
| Idle / run / jump / fall / land | idle thở nhẹ, run giữ kiếm sát thân; chân/áo không kéo dài quá collision; landing nén gọn | loop không trôi root; tốc độ run do movement config |
| Hurt / death / interact | hurt ngắn, không quay lưng kéo dài; death không làm thân biến mất trước khi server state đổi; interact có pose đọc được | state và thời điểm do server/quest event |
| Basic combo 1–3 | đường kiếm ngang → chéo lên → chém xuống; tay và chuôi đọc rõ ở từng pose | thời gian hit lấy từ combat config; clip event chỉ phát cue |
| Dodge | nghiêng thân theo hướng di chuyển; lưỡi kiếm không che toàn nhân vật; kết thúc giữ hướng rõ | vị trí/thời lượng né do server; không xuyên tường |
| `SK-MK-01` Phản Quang | hạ trọng tâm, kiếm chéo trước ngực; 6 frame đầu có viền bạc mảnh; đỡ thành công mới phát cung lục giác vàng nhạt | cửa đỡ 0,4s; cung thành công không được hiện nhầm khi đỡ hụt |
| `SK-MK-02` Tầm Long | prep 0,15s, thân nghiêng và kiếm dẫn hướng; dash 0,20s, nhân vật luôn visible; recovery 0,24s | 5,5m, dừng tại tường; animation không kéo nhân vật qua blocker |
| `SK-MK-03` Kiếm Trận | ba pose rõ: chém ngang, chéo lên, chém xuống; không gộp silhouette thành blur | ba nhịp 0,10/0,12/0,14s; mỗi cung VFX <0,22s; quạt 100° do server tính |

## 5. VFX binding và hiệu năng

- Phản Quang: cue phòng thủ là viền bạc mảnh, cue thành công là cung lục giác vàng nhạt; không flash trắng toàn màn hình.
- Tầm Long: vệt trắng bạc lõi vàng và bụi nhỏ tại điểm dừng; giữ thân người chơi nhìn thấy suốt pha lướt.
- Kiếm Trận: ba cung vàng-trắng lệch nhịp; cung ba dày nhất. VFX tách cast/travel/impact/miss, nhưng không vẽ dấu trúng khi server không xác nhận.
- Tối đa hai FX tồn tại lâu trên một actor. Burst giới hạn theo Art Bible: mobile tối đa 40 primary particles, HighFX tối đa 120; LowFX giảm hạt/rung nhưng giữ nguyên cue gameplay và telegraph boss.
- Không để màu sắc là tín hiệu duy nhất; giữ hình dạng và tương phản cho người mù màu. Không che portrait/weapon, mục tiêu hoặc cảnh báo boss.

## 6. File bàn giao và nghiệm thu

**Đường dẫn đề xuất:** `Assets/Art/Characters/CLASS_MINH_KIEM/` với source pixel PNG/layers, atlas pages lossless ≤1024², palette, frame/pivot/anchor table, thumbnail, import preset và preview nền trong suốt; ID leaf giữ nguyên theo registry.

Nghiệm thu ART-P1-002/003 khi: tạo hình/palette đã chốt được duyệt; sheet đạt audit đếm pixel (đủ 48/48 cell, 6 frame khác nhau mỗi hàng, không tái dùng frame giữa các hàng, hàng gương khớp tuyệt đối); cạnh pixel sạch, không shimmer/bleed; kiếm thay được độc lập; 3 kỹ năng có pose/cue đúng spec; collision không bị frame art điều khiển; kiểm tra 16:9/20:9/mobile và integer scale; LowFX vẫn truyền đạt đỡ chuẩn, hướng lướt, ba nhát chém và telegraph boss.

## 7. Cần xử lý trước khi khóa clip

Combat Skills spec và art documents trước đây từng dùng hai chiều cao hero khác nhau; DEC-016 thay chiều cao collider cũ bằng footprint mặt đất 1,2×0,6 WU; sheet 48×64 px và 20 PPU. Hai SVG concept trước đây không phải pixel art, chỉ lưu lịch sử; concept sprite sheet mới sẽ tuân chuẩn art pipeline và cần duyệt trước export production.
