# Thư viện asset — đợt 20261113a

Đợt này tạo **20 sheet chọn / 320 ô nguồn mới**: 15 sheet vận động Rễ Nước và 5 sheet động tác Phản Quang của Minh Kiếm. Mỗi action có N/NE/E/SE/S × 16 khung nguồn. Giữ phong cách chibi nguyên khối đã chốt, không quay lại paper-doll. Ảnh tạo bằng `image_gen` tích hợp; PNG nguồn và prompt thực lưu trong thư viện, runtime nhận bản sao nguyên byte.

## Rễ Nước: bò chậm, bò nhanh và chuyển trọng tâm

| Action | Thiết kế chuyển động | Nguồn | Nhịp xem |
|---|---|---:|---:|
| walk | Các bó rễ ngắn luân phiên với, bám, kéo thân, đi qua dưới thân rồi đặt lại | 5 × 16 | 0,80s, vòng |
| run | Thân hạ thấp, bó rễ với xa hơn, chuyển tải nhanh hơn, lá/chạc rễ theo đà | 5 × 16 | 0,64s, vòng |
| turn | Rễ một bên bám, bên kia nhả và đặt lại; thân/chạc rễ xoắn nhẹ, trở về thế sẵn sàng | 5 × 16 | 0,50s, một lần |

`walk`/`run` là chuyển động bằng rễ, không thêm tay/chân người. Một số rễ vẫn chạm đất; không có động tác bay, nhảy hoặc roi đánh dài. Nhịp tiếp xúc đối bên nằm giữa chu kỳ. Giữ rễ gỗ ướt, rêu, lá xanh lam, hai chạc cuộn và hạt sáng trước thân. Hạt khuất ở N/NE, lộ mép ở E và lộ theo góc trước ở SE/S.

`turn` là **nhịp chuẩn bị đổi hướng**, đúng yêu cầu giữ góc khai báo của mỗi block: chuyển trọng tâm nhẹ rồi ổn định. Nó không phải một vòng xoay vẽ sẵn nối N sang NE. Renderer/gameplay vẫn quyết định heading và khi nào sử dụng từng hướng. Walk/run cũng không cấp quyền dịch chuyển hoặc đổi tốc độ truy đuổi của AI; cơ chế area-denial của quái vẫn theo thiết kế combat.

Ba action dùng `FOOT` và chiều cao tham chiếu cố định từ ba pose đầu của page/hướng. Chiều cao nguồn khác nhau giữa các lần sinh không làm thay kích thước ở từng khung. Không chỉnh raster hoặc collider. SW/W/NW lật từ SE/E/NE khi policy cho phép; không cộng thành ảnh nguồn mới.

Rễ Nước hiện có **9/12 action đủ nguồn và đã kiểm source**: idle, walk, run, turn, hurt, death, telegraph_01, attack_01, recovery_01. Còn ba pha chồi đất số 02. Đủ nguồn không đồng nghĩa đã nghiệm thu AI, tốc độ, collision hoặc toàn encounter.

## Minh Kiếm: động tác Phản Quang

`class_minh_kiem_skill_01_{n|ne|e|se|s}` có tổng **80 khung nguồn**. Giữ đúng nhân vật cũ: búi tóc đen cài vàng, áo giao lĩnh ngà, áo choàng ngắn xanh trầm viền vàng, giáp vai, quần tối và ủng nâu; giữ tỷ lệ đầu/thân và nét chibi từ Motion16 đã chốt.

Động tác gồm hạ trọng tâm/đưa kiếm lên ở 0–3, lập thế kiếm chéo trước ngực ở 4–7, giữ/điều chỉnh thế đỡ ở 8–11, thu về ở 12–15. Tay phải của hướng nguồn cầm một chuôi kiếm, tay còn lại giữ gần thế thủ, không nắm lưỡi. Hướng lật theo policy đảo hình tương ứng; không được gọi là góc vẽ riêng. Góc N để thân che giữa lưỡi kiếm ở phía trước, không vẽ kiếm đè trên lưng/cổ; các góc bên giữ kiếm phía trước thân và gắn với bàn tay.

Nguồn này là **động tác thủ**, không chứa sẵn phản công hoặc cung phép. Cung lục giác vàng `sk_mk_01_parry_component` đã có ở đợt f, chỉ sử dụng khi sự kiện đỡ thành công được xác nhận. Không mặc định phát hiệu ứng thành công ở mọi lần bấm skill. Viền thép mảnh ở phần đầu động tác không phải một lớp VFX rời.

Nhịp xem toàn động tác là **0,80s**, gồm cả đưa kiếm lên và thu thế. Cửa đỡ **0,40s** trong thiết kế kỹ năng vẫn là hợp đồng combat riêng; không suy cửa hit/parry từ toàn bộ thời lượng clip art. Actor Library và raw sheet trong Studio dùng cùng profile xem 0,80s, one-shot giữ cuối. Không đổi damage, MP, cooldown, Kiếm Ý hoặc logic server.

## Studio: chèn component nguồn để chỉnh tay

Studio có thêm danh sách component VFX từ thư viện và nút **“+ Component 16 khung nguồn”**, cùng tham số launcher `-Component`. Danh sách ghi trạng thái kiểm của từng nguồn. Nguồn chờ kiểm vẫn có thể mở/chèn trong công cụ review; thao tác này không tự cấp approval hoặc thay client gameplay.

Layer chèn giữ nguyên texture, 16 vùng cắt, pivot và thứ tự nguồn. Mỗi clip nhận track riêng, đưa toàn bộ 16 nguồn vào timeline host; layer mới chọn tự động và danh sách cuộn tới layer đó. Timeline dưới 16 ô bị từ chối để không bỏ source pose. Khi host có hơn 16 ô, một số ô giữ lại pose theo thời lượng; không tạo hoặc tuyên bố có thêm pose vẽ mới.

**Đây là điểm bắt đầu chỉnh tay.** Mặc định hiệu ứng trải đều trên thời lượng clip host, tại X=45/Y=-75, Z=20 và cỡ preview giảm một nửa so với bản component mở riêng. Với host Phản Quang 0,80s, việc chèn không tự bảo toàn thời lượng riêng 0,40s của component hay tạo cửa đỡ đúng. Người biên tập phải chỉnh key/timing/alpha, vị trí, hướng và sự kiện theo mục đích, rồi kiểm lại bản xuất. Component độc lập vẫn có profile gốc, không bị sửa PNG hoặc metadata nguồn.

Undo/redo, pivot, layer/Z, scale, socket, mốc VFX/hit, onion skin, tốc độ, JSON và bundle vẫn giữ. Nhãn component dài không còn ép panel tràn ngang; ghi chú nguồn giới hạn ba dòng dưới viewport, toàn bộ nội dung có ở tooltip và tab Xuất. Cảnh review không gây damage hoặc cấp thưởng.

## Mở xem

```powershell
.\ClientGodot\Run_Actor_Library.ps1 -SkipBuild -Actor MOB_WATERROOT -Clip walk
.\ClientGodot\Run_Actor_Library.ps1 -SkipBuild -Actor MOB_WATERROOT -Clip run
.\ClientGodot\Run_Actor_Library.ps1 -SkipBuild -Actor MOB_WATERROOT -Clip turn
.\ClientGodot\Run_Actor_Library.ps1 -SkipBuild -Actor CLASS_MINH_KIEM -Clip skill_01
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_WATERROOT:run -Direction NE -Play
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:CLASS_MINH_KIEM:skill_01 -Direction E -Play
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:CLASS_MINH_KIEM:skill_01 -Direction E -Component sk_mk_01_parry_component -Frame 7
```

Bỏ `-SkipBuild` trên checkout mới để build/import. Actor Library phát vòng cả action một lần để xem lặp; Studio giữ one-shot mặc định cho turn và Phản Quang. `-Loop` là override xem, không phải cơ chế cast lặp của game.

## Kiểm tra và phạm vi

- 20 quyết định source/clip, pin PNG SHA256 và binding SHA256; chưa nghiệm thu toàn actor hoặc kỹ năng gameplay.
- 46 PNG baseline giữ nguyên SHA256; 140/140 bản runtime được chọn khớp byte nguồn.
- .NET 8 build 0 warning/error, Godot import; 34 Python tests; native library 13.215 assertions; Studio 63.370 assertions / 194 entries. Các kiểm source/clip và chèn component không thay bằng chứng thực nghiệm về gameplay.
- Kiểm đủ 16 nguồn ở tám hướng, clock 60 bước/s, raw/group cùng nhịp, chế độ vòng/giữ cuối, thứ tự vùng nguồn khi chèn component, roundtrip JSON và từ chối nguồn sai hoặc host quá ngắn.
- 6 video native: ba action Rễ Nước tám hướng, Phản Quang tám hướng, raw N và ghép component thủ công E. Ảnh/dải mẫu/log/hash kèm theo. Video 60 bước/s xuất offline, không chứng nhận game đạt 60 FPS thực. Dải mẫu thời gian không phải sheet nguồn hoặc bảo đảm mỗi ô ứng một source frame.

Catalogue hiện có **143 page structure, 56/1008 job đủ góc nguồn, 20 job đủ góc đã kiểm source**, còn 952 job thiếu. Vẫn giữ 21 HOLD chất lượng trước đó và atlas VFX cũ sai số hàng. Các con số chỉ bao phủ actor/skill trong catalogue, chưa bao phủ hết tilemap/UI/icon/audio/biến thể. Không tự nâng trạng thái các nguồn cũ hoặc tính component thành kỹ năng hoàn chỉnh.

Nguồn/prompt: `Art_Source/Actor_Library_20261107/Sheets/`, `Prompts/`, `generation_records.json`. Inventory: `batch_20261113a.json`; inventory các đợt trước cập nhật snapshot hiện hành. Bằng chứng: `Implementation/Reports/Evidence/Actor_Batch_20261113a/`, gồm `visual_decisions.json`, `sprite_integrity.json`, `offline_media_integrity.json`.

Tiếp tục ba pha chồi đất, động tác các lớp còn thiếu, quái/boss/NPC và thư viện môi trường/UI/icon/audio. Các bản mới ở thư viện/Studio chưa tự thay renderer gameplay, chưa nghiệm thu LowFX chiến đấu, AI, hit/collision hoặc PCK/shipping. Mục tiêu thư viện toàn game vẫn đang thực hiện.
