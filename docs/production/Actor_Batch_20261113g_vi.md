# Asset 20261113g — Tước Mạch, Ảnh Bộ, Tử Diệm và né

26 sheet chọn /416 khung nguồn mới, tạo bằng imagegen tích hợp, có prompt thực tại `Art_Source/Actor_Library_20261107/Prompts/` và PNG nguyên gốc trong `Sheets/`. Nhân vật giữ phong cách chibi nguyên khối đã chốt, một đao cong ở tay phải, tay trái trống; không chuyển lại paperdoll. Studio vẫn giữ các công cụ chỉnh tay.

## Chuyển động

20 sheet thân: bốn action × năm góc nguồn N/NE/E/SE/S ×16 tư thế. SW/W/NW dùng policy lật; không tính là ba góc vẽ riêng. Mỗi clip dùng một chiều cao đứng và neo giày tối `DARK_BOOT_CORE_FOOT`; không kéo giãn từng tư thế. `body_registration_20261113g.json` ghi nguồn, SHA và phép đo.

| Action | Nhịp xem | Các pha nguồn | Nội dung |
|---|---|---|---|
| skill_04 / Tước Mạch | 0,68 s | 0–5:0,20;6–9:0,16;10–15:0,32 s | Một lần nâng đao, bổ xuống và hồi thấp; không nâng lại thành đòn thứ hai |
| skill_05 / Ảnh Bộ | 0,50 s | 0–3:0,08;4–11:0,22;12–15:0,20 s | Co chân, lao thấp, hãm rồi đứng lại; đao thu thấp, không tự chém |
| skill_06 / Tử Diệm | 1,10 s | 0–3:0,55;4–11:0,25;12–15:0,30 s | Nạp thế rồi xoay thân một vòng thấp theo chiều kim đồng hồ, hồi về hướng ban đầu |
| dodge / né | 0,48 s | 0–3:0,08;4–9:0,18;10–15:0,22 s | Nghiêng trọng tâm và bước tránh ngang; đao gần thân, không dùng lại thế lao trước |

Thời lượng là profile trình bày, không sửa CD/MP/sát thương/Nhiệt/collision. Ảnh Bộ giữ cửa lướt0,22 s; source đứng tại chỗ, dịch chuyển6m phải do gameplay/server kiểm địa hình. Tử Diệm giữ nạp0,55 và bùng0,25 s. Không cấp i-frame bằng frame art. Raw Studio và nhóm actor dùng cùng `sourceFrameDurationsMs`; kiểm ranh pha, seek/resume, giữ khung cuối, lặp về0 và JSON roundtrip riêng.

**Hướng của Tử Diệm là hướng bắt đầu/kết thúc**, không phải khóa cả16 tư thế vào cùng một góc. Các frame4–11 thực sự đổi hướng:

| Bắt đầu | Frame4→11 |
|---|---|
| N | NE,E,SE,S,SW,W,NW,N |
| NE | E,SE,S,SW,W,NW,N,NE |
| E | SE,S,SW,W,NW,N,NE,E |
| SE | S,SW,W,NW,N,NE,E,SE |
| S | SW,W,NW,N,NE,E,SE,S |

Đây là choreography nguồn được xem thủ công, không phải đo góc chính xác từng pixel. Renderer không quay một hình đứng bằng code để giả đủ góc. Các hướng lật vẫn phải có nhãn lật và không được coi là vẽ tay độc lập.

## Sáu VFX component

Mỗi component có16 frame riêng, RGBA nguyên gốc. `OMNI` là texture cục bộ dùng ghép, không phải tám góc VFX đã vẽ hoặc toàn kỹ năng đã nghiệm thu. Scale xem dùng `LONGEST_AXIS`.

| Component | Lifetime xem | Gắn / nội dung |
|---|---|---|
| sk_ad_04_down_cut_component | 0,32 s, một lần | Vết bổ dọc mảnh; neo đầu nóng thấp vào điểm trúng, không thành cột lửa kín |
| sk_ad_04_slow_mark_component | 0,80 s, lặp | Đúng ba vệt đỏ cố định thành cung nông; tâm dưới mục tiêu, không biểu thị số stack |
| sk_ad_05_smoke_component | 0,46 s, một lần | Khói kéo phía sau đầu nóng;0,06 mở/0,22 kéo/0,18 tan; không có bóng nhân vật |
| sk_ad_06_charge_component | 0,55 s, một lần | Than hội tụ nhẹ quanh sống đao tưởng tượng; không vẽ thêm đao hoặc thân |
| sk_ad_06_sweep_component | 0,48 s, một lần | Vòng quét dẹt rỗng giữa, quay theo chiều kim đồng hồ;0,08 mở/0,25 bùng/0,15 tan |
| sk_ad_06_heat_petal_component | 0,40 s, một lần | Một cánh than cong tan thành vụn; chỉ là một đơn vị biểu diễn, không tự cấp năm Nhiệt |

Ví dụ ghép thời gian: smoke bắt đầu ở body0,02 để pha kéo trùng0,08–0,30; sweep bắt đầu ở body0,47 để pha bùng trùng0,55–0,80 và tan đến0,95. Đây là recipe hình ảnh đề xuất, không phải hit event hoặc tích hợp server đã xong. Số cánh0–5 phải đọc số Nhiệt đã tiêu được server xác nhận; không vẽ cố định năm cánh hoặc suy từ màu texture.

Studio giữ frame cuối clip một lần để kiểm nguồn. Gameplay phải tháo component khi hết lifetime/trạng thái. Mark dừng khi trạng thái chậm hết; không để vụn than, khói hoặc dấu còn mãi. LowFX và full-skill assembly vẫn cần kiểm riêng.

## Đăng ký điểm gắn và lịch sử sửa

`calibrate_anh_dao_components.py --apply` chỉ đọc PNG, ghi tọa độ vào `component_registration_20261113g.json` và record. Mark/charge dùng tâm bounds đối xứng. Vết bổ neo đầu nóng thấp, smoke neo đầu nóng bên phải, có fallback bounds cho frame khói tối. Vòng quét/cánh than dùng tâm lưới suy từ frame đỉnh5–9, giữ điểm xuất phát vô hình khi chỉ còn cung/vụn nhỏ. Các phép đo không thay thế xem chuyển động native.

`SOURCE_PIVOTS` chỉ cho component khai báo rõ, đúng16 cặp tọa độ hữu hạn nằm trong từng ô nguồn. Sửa pivot làm đổi binding SHA và cần duyệt lại. Kiểm ô rỗng, mép cắt, pixel trùng và số khung vẫn giữ. Bốn component có phần tan đọc bounds alpha64 từ frame12, không đổi RGBA hoặc bỏ kiểm hình rỗng; actor không dùng ngoại lệ này.

31 PNG mới lưu, chỉ26 bản chọn/416 khung được tính. Năm bản v1 được giữ cùng prompt trong lịch sử:

- Tước Mạch NE: sửa hồi thế nâng vai lần hai thành hồi dưới thắt lưng.
- Tước Mạch SE: sửa góc mặt trôi về E thành góc chéo trước-phải.
- Tử Diệm SE: sửa frame6/7 từ nhìn phải sang W/NW.
- Tử Diệm S: sửa chuỗi SW/W/NW ở frame4–6.
- Vòng quét Tử Diệm: xếp lại khoảng trống giữa các ô để phần lõi không chạm biên chia. Không hạ kiểm mép để nhận bản lỗi.

## Mở trong công cụ

```powershell
ClientGodot/Run_Actor_Library.ps1 -Actor CLASS_ANH_DAO -Clip skill_04
ClientGodot/Run_Actor_Library.ps1 -Actor CLASS_ANH_DAO -Clip skill_05
ClientGodot/Run_Actor_Library.ps1 -Actor CLASS_ANH_DAO -Clip skill_06
ClientGodot/Run_Actor_Library.ps1 -Actor CLASS_ANH_DAO -Clip dodge
ClientGodot/Run_Art_Studio.ps1 -Entry sk_ad_06_sweep_component
Tools/ArtProduction/review_actor_batch_20261113g.ps1 -Resume
```

Evidence tại `Implementation/Reports/Evidence/Actor_Batch_20261113g/`; inventory `Art_Source/Actor_Library_20261107/batch_20261113g.json`. Movie Maker xuất offline60 bước/s phục vụ xem chuyển động, không phải kết quả đo gameplay60FPS. Nguồn mới được duyệt riêng; không tự thay renderer gameplay hoặc duyệt các source cũ đang HOLD. Toàn thư viện, biến thể, map, UI, icon, audio và tích hợp gameplay tiếp tục sản xuất.

Kết quả kiểm:65 Python tests đạt; .NET build0 warning/error, Godot import thành công. Native Library17.272 assertions, Studio82.266/316 entries.12 MP4 chọn decode sạch,180frame/3s mỗi video, không có video bị thay sau capture.26 source được pin SHA nguồn/binding sau xem source/native;179 pin và224 source/binding trước giữ nguyên.46 PNG baseline nguyên SHA,247 runtime copy đúng byte.20 hồ sơ HOLD giữ nguyên,19 source HOLD hiện nằm trong catalogue cấu trúc; một full VFX Kiếm Trận vẫn bị từ chối do5hàng thay vì4.

Catalogue250page qua cấu trúc (gồm3legacy),71/1008job đủ nguồn,39job đủ nguồn đã kiểm source;937job còn thiếu. Component không tính thành full-timeline VFX job. Ảnh Đao đủ12 action về cấu trúc nhưng chỉ bảy action có đủ góc đã kiểm source; idle/walk/basic/hurt/death cũ và chuyển thế chưa được nghiệm thu ở đợt này. Viền cam hỗ trợ nhận diện khi lướt, ghép VFX theo server, LowFX, world renderer và gameplay60FPS còn cần tích hợp/đo riêng.
