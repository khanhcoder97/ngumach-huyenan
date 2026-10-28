# ĐẶC TẢ HUD GAMEPLAY — OVERLAY TRÊN GAME VIEWPORT
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.0

### 1. Phạm vi và nguyên tắc

Đặc tả này khóa bố cục HUD khi nhân vật đang ở trong bản đồ khám phá, chiến đấu thường, đánh boss hoặc tham gia hoạt động nhóm. HUD pixel art phủ trên game viewport pixel-art 2D nhìn từ trên, theo `Pixel_Art_Production_Standard_vi.md`. Icon/frame/font dùng pixel asset point-filtered, pixel snap và scale nguyên; không trộn vector/HD icon hoặc blur vào bộ UI.

Ưu tiên theo thứ tự: **nhìn được nhân vật và telegraph → đọc nhanh HP/MP và cơ chế lớp → thao tác chiến đấu → đọc nhiệm vụ/vị trí → mở tiện ích**. Các góc màn hình chứa nhóm thông tin bền; vùng trung tâm và dải giữa phía dưới được giữ thoáng để đọc combat. HUD không che toàn thân boss, vòng telegraph, lối thoát, tương tác nhiệm vụ hoặc chữ thoại quan trọng.

Tài liệu này là nguồn chuẩn chi tiết cho HUD trong trận. UI_UX_Spec_vi.md vẫn là nguồn chuẩn cho các panel ngoài trận như nhân vật, túi đồ, kỹ năng, nghề, bang hội và cài đặt.

### 2. Viewport, safe area và bố cục neo

Gốc tọa độ là góc trái trên của **safe area** sau khi trừ notch, tai thỏ, góc bo, thanh hệ thống và viền thiết bị. HUD root phủ viewport nhưng không chặn input của game ở vùng trống: root dùng `pointer-events: none`; từng control tương tác bật `pointer-events: auto`. Tọa độ neo theo góc/điểm neo, không hardcode theo độ phân giải thiết bị.

| Vùng | Mobile ngang 16:9–20:9 | PC 16:9/16:10 | Chức năng |
|---|---|---|---|
| Lề an toàn | 16–24 dp cộng safe inset | 24 px ở 1080p; scale theo UI scale | khoảng cách tối thiểu tới mép |
| Cụm nhân vật | trái trên; tối đa 46% chiều rộng | trái trên; rộng 360–410 px | avatar, tên, cấp/cảnh giới, tiền, bốn thanh |
| Bản đồ nhỏ | phải trên; 176–208 dp | phải trên; 210–240 px | pixel map, mục tiêu, vùng hiện tại |
| Theo dõi nhiệm vụ | trái giữa, nằm dưới cụm nhân vật | trái giữa, rộng 300–360 px | chương, mục tiêu, tiến độ |
| Di chuyển | trái dưới, vùng ngón cái | ẩn; dùng bàn phím/tay cầm | joystick, chế độ đi/chạy |
| Kỹ năng/hành động | phải dưới, vùng ngón cái | phải dưới; phím tắt nhìn thấy | đánh thường, 6 kỹ năng, khóa mục tiêu |
| Telemetry | sát mép dưới trái, mặc định thu gọn | sát mép dưới trái, mặc định bật dòng gọn | tọa độ, giờ máy chủ, FPS/ping |

**Vùng gameplay không bị che:** mặc định dành 54% chiều rộng trung tâm và 58% chiều cao trung tâm cho nhân vật, quái và cơ chế. HUD có thể chiếm thêm vùng này khi người chơi mở tooltip/panel; khi đóng thì tự trả lại vùng nhìn. Không đặt thông báo nổi cố định trên tâm camera.

**Responsive rules:**
- 16:9 mobile (viewport tham chiếu 1280×720): giữ kích thước nút tối thiểu, thu gọn khoảng cách giữa các control; minimap 168 dp; quest hiển thị tối đa 2 objective.
- 19.5:9–20:9: không kéo giãn widget. Phần ngang dư tăng khoảng thở hai bên và minimap có thể lên 208 dp; skill hub giữ nguyên bán kính để ngón cái với tới.
- PC 1920×1080: dùng kích thước bảng dưới đây. 16:10 dùng cùng kích thước, thêm khoảng thở dọc; không scale HUD thành quá lớn.
- Tỷ lệ dưới 1.6 hoặc chiều cao logic dưới 640: ưu tiên chế độ **HUD gọn**, minimap giảm 15%, quest tự thu gọn, chat và telemetry chỉ còn icon/dòng ngắn.
- Nếu thiết bị đang portrait, hiện yêu cầu xoay ngang trước khi vào gameplay; không render HUD xoay dọc.

### 3. Tokens đồ họa và chữ

| Token | Giá trị gợi ý | Quy tắc dùng |
|---|---|---|
| Nền Slate | `#101820` | panel chính bằng mảng màu pixel; không backdrop blur |
| Viền Đồng | `#B88B4A` | viền pixel 1–2 source px, phản sáng dạng cụm |
| Vàng Nhấn | `#E8C878` | cấp, focus, EXP, trạng thái sẵn sàng |
| HP Crimson | ramp 2–3 màu `#A91F32` / `#D93442` / `#F04A50` | HP dạng pixel segments; dưới 25% nhấn viền/icon chậm, không nháy toàn thanh |
| MP Azure | ramp 2–3 màu `#145BA8` / `#287FC2` / `#55B7F1` | MP pixel bar |
| Tài nguyên lớp Amethyst | ramp 2–3 màu `#633A9B` / `#8552BE` / `#B178E8` | Thủy Ấn, Kiếm Ý, Nhiệt, Thế hoặc Mộc Tiêu |
| Hộ Thể Amber | ramp 2–3 màu `#A95A18` / `#D98226` / `#F5B646` | khiên/hộ thể tạm thời, không đại diện giáp cơ bản |
| EXP Gold | `#F0D27D` | đường tiến độ mảnh ở đáy panel |
| Chữ chính | `#FFF9EB` | tên, số quan trọng; tương phản ≥4.5:1 trên nền panel |
| Chữ phụ | `#C7D0D3` | vị trí, nhãn, mô tả ngắn |
| Nguy hiểm | `#F06455` + pattern chéo | telegraph/đang nguy cấp; luôn có shape/icon kèm theo |

Panel dùng mặt kính tối có lớp nền mực, viền đồng đánh sáng ở góc, shadow mềm 0 6px 20px. Bo góc panel 10–12 px, button 8–10 px, khung portrait dạng tròn hoặc lục giác. Hoạ tiết võ hiệp chỉ dùng ở góc/đường phân cách; không đặt hoa văn dưới text hoặc số liệu. Font sans-serif hỗ trợ tiếng Việt đầy đủ; số dùng tabular figures để thanh stat không nhảy chiều rộng.

**Không dựa vào màu đơn lẻ:** mỗi tài nguyên có nhãn viết tắt và glyph riêng; trạng thái cần icon/hình dạng, pattern hoặc số. Ví dụ HP có dấu thập khiên, MP có giọt lam, tài nguyên lớp có biểu trưng lớp, Hộ Thể có viền khiên.

### 4. Cụm nhân vật và thanh trạng thái — trái trên

**Kích thước tham chiếu:** PC 390×158 px; mobile 400×154 dp tối đa, có thể co còn 336×146 dp. Avatar 64 px/64 dp, vòng kim loại dày 3 px; viền thứ hai báo trạng thái party target/online. Dùng portrait nhân vật hiện tại với crop cố định; không tự phóng to theo rarity trang bị.

| Thứ tự | Thành phần | Cách hiển thị và tương tác |
|---|---|---|
| 1 | Avatar | ảnh bán thân; chấm trạng thái combat/AFK nhỏ; nhấn mở nhân vật, giữ chuột/nhấn giữ để xem tóm tắt |
| 2 | Tên và lớp | tên 1 dòng, lớp dưới hoặc biểu trưng hệ; tên dài ellipsis, không đẩy thanh ra khỏi panel |
| 3 | Cấp/cảnh giới | pill `Cấp {level}`; nếu progression service trả `realm_label` thì hiện `Cấp {level} · {realm_label}`; HUD không tự suy diễn cảnh giới từ cấp |
| 4 | Tiền cao cấp | icon tinh thể + số `Ngọc Tịnh`; tap/click mở ví/cửa hàng mỹ phẩm, không hiện nút mua ngay trong combat |
| 5 | HP | nhãn HP, current/max căn phải; phần trăm chỉ thay số khi cỡ hẹp; tooltip cho biết trạng thái đang làm giảm HP |
| 6 | MP | current/max; khi không đủ MP cho skill vừa nhấn, thanh rung nhẹ một lần và hiện số MP thiếu cạnh skill |
| 7 | Tài nguyên lớp | thanh tím phân thành 5 nấc với `current/5`; tên theo môn phái: Kiếm Ý, Nhiệt, Thủy Ấn, Thế, Mộc Tiêu; số nấc cập nhật ngay khi server xác nhận |
| 8 | Hộ Thể | thanh hổ phách chỉ xuất hiện khi có khiên/hộ thể đang hoạt động; số `còn/lúc nhận` và thời gian còn lại. Khi không có shield thì ẩn thanh và hiện giáp cơ bản dạng icon + số trong quick-stat, không giả lập giáp thành tài nguyên tiêu hao |
| 9 | EXP | đường vàng mảnh sát đáy, tỷ lệ 0–100%; hover/tap cho EXP hiện tại/cần để lên cấp |

HP/MP bar cao 10–12 px PC, 8–10 dp mobile; class/Hộ Thể cao 6–8 px. Số nằm trong bar nếu chiều rộng đủ, nếu không thì đưa sang bên phải. Khi HP thấp, thêm icon `!`, viền pulse tối đa 1 lần/giây và âm cảnh báo tùy chọn; không nhấp nháy nền. Khi chết, HP giữ 0 và panel chuyển sang trạng thái hồi sinh, không giả lập người chơi vẫn hoạt động.

**Quick access dưới panel:** bốn nút Chat Log, Thư/Thông báo, Bang hội, Cài đặt; nút vuông bo 10 px, 40–44 px PC/48–52 dp mobile. Icon 24 px, badge đỏ chỉ có số chưa đọc tối đa `9+`. PC tooltip cho tên và phím; mobile mở panel tương ứng. Chạm icon không làm nhân vật tự dùng vật phẩm hoặc rời hoạt động.

### 5. Bản đồ nhỏ và điều hướng — phải trên

**Khung:** frame pixel 9-slice, góc theo tile grid, viền đồng 1–2 logical px; 210–240 CSS px PC, 176–208 dp mobile. Vùng bản đồ chiếm 100% trừ banner địa danh 30–34 px. Minimap pixel art; zoom dùng bậc integer 1×/2× hoặc render logical map markers cùng grid; pan không quá ranh giới vùng.

**Layer thông tin:**
1. Nền địa hình/đường/platform; nước, tường và cửa có icon/line style riêng.
2. Mũi tam giác người chơi chỉ hướng nhân vật; vòng ngoài thể hiện hướng camera nếu camera khác hướng nhân vật.
3. Quest marker: hình thoi vàng; mục tiêu đang chọn có vòng pulse chậm; hoàn thành thành dấu check mờ.
4. NPC/portal/điểm dịch chuyển: glyph riêng, tên hiện khi hover/nhấn giữ hoặc mở bản đồ lớn.
5. Đồng đội: mũi tên xanh ngọc và class glyph; boss/elite chỉ hiện trong combat/quest liên quan, không lộ toàn bộ spawn chưa khám phá.
6. Vùng nguy hiểm/hazard đã biết: viền sọc/chéo; không phủ đỏ đặc khiến bản đồ khó đọc.

Banner đáy hiện `Khu vực · Kênh`; nếu sự kiện chạy, thêm trạng thái sự kiện một dòng phía trên banner. Nhấn minimap mở bản đồ toàn màn; nút la bàn đổi giữa hướng Bắc cố định và map xoay theo người chơi; giữ minimap không nhận click-through vào game canvas.

### 6. Theo dõi nhiệm vụ — trái giữa

Panel mặc định rộng 320–360 px PC, 288–320 dp mobile; nền Slate opacity 90%, viền đồng mảnh. Neo dưới cụm nhân vật với khoảng hở 12 px; không đè joystick. Header cao 42 px: tên chương ở trái, nút danh sách nhiệm vụ, nút thu gọn. Có thể kéo panel trong vùng an toàn và reset về mặc định.

**Nội dung:**
- Tiêu đề: `Chương II · Rừng nhớ tên người` (1 dòng tối đa; ellipsis + tooltip).
- Tối đa 3 quest ghim trên PC, 2 trên mobile; mỗi quest 2 objective đang làm và 1 dòng trạng thái tổng.
- Objective hoàn thành: checkmark, màu xám sáng, opacity 60%, giữ lại tối đa 3 giây rồi chuyển vào lịch sử.
- Objective đang làm: chấm/glyph vàng, text rõ; tiến độ dạng `3/6`, `0/3`, hoặc timer. Không nhấp nháy text.
- Objective bị chặn: khóa + lý do ngắn (`Cần hoàn thành C2-03`), không chỉ tô xám.
- Nhấn objective ghim/bỏ ghim hoặc mở journal; giữ để định vị trên minimap. Marker mép màn hình dùng khi đích ngoài camera.

Khi boss xuất hiện, quest tracker tự rút thành 1–2 dòng và cho boss HP bar ở gần mép trên trung tâm, cách safe area 8%; không chồng lên minimap, nameplate hoặc telegraph. Chỉ boss/đối tượng encounter hiện thanh HP lớn; quái thường dùng nameplate nhỏ khi target/focus.

### 7. Điều khiển di chuyển — trái dưới

**Mobile joystick:** đĩa vùng chạm 136–152 dp, nút nổi 56–64 dp; vùng có alpha 20–28%, tăng tương phản khi ngón tay chạm. Vị trí mặc định cách trái 26 dp và cách đáy 34 dp (sau safe inset); có thể kéo tâm joystick tới 15% chiều rộng/chiều cao rồi lưu. Hướng input liên tục, dead-zone 12%; bù vùng ngón tay cái tùy chọn. Không có snap lưới.

Ở giữa joystick có nút chuyển `Đi / Chạy / Nước rút` dạng 3 trạng thái; trạng thái đang chọn có vòng sáng + nhãn. Nếu game mode hoặc combat không cho phép, nút disable và giải thích lý do; HUD không tự tạo stamina hoặc thay đổi tốc độ ngoài dữ liệu gameplay.

**PC/tay cầm:** joystick ẩn; WASD/mũi tên hoặc stick trái di chuyển XY 8 hướng; né/interact theo keybind DEC-016. Mọi keybind có thể remap; khi tay cầm được dùng, icon nút đổi sang glyph của controller. Không show cùng lúc hai bộ phím nếu không bật accessibility prompt.

**Telemetry sát mép dưới trái:** dòng gọn `X 128.4  Y 0.0 · 19:42 · 60 FPS`; tọa độ dùng WU và làm tròn 0.1, giờ là giờ máy chủ, FPS là client render rate. Mobile mặc định ẩn FPS/tọa độ sau tùy chọn `HUD → Hiện telemetry`; PC mặc định chỉ hiện ping và giờ, F10 bật tọa độ/FPS để debug. Dòng telemetry không nhận input và không hiện trong screenshot/cinematic nếu bật hide-overlay.

### 8. Cụm kỹ năng và hành động — phải dưới

**Nút chính đánh thường:** vòng kim loại 94–104 dp mobile/82–92 px PC, đặt trong góc phải dưới cách lề 28–36 dp; icon vũ khí/đòn đánh, nhãn `Đánh`, viền vàng mảnh. Tap/click phát một đòn; giữ chỉ tiếp tục combo nếu Combat Spec cho phép; nút không tự target qua tường. Khi đang cast/khóa hành động, hiện vòng trạng thái chứ không nhận nhấn giả.

**Vòng cung kỹ năng (cập nhật2026-10-29):** sáu slot tròn bao quanh nút đánh lớn ở góc phải dưới, vòng cung chạy từ trái-dưới lên phía trên, toàn cụm nằm trong safe area. Không dùng lưới2hàng hoặc bán cung tràn cạnh phải. Geometry/input/icon/QA lấy từ `HUD_Skill_Arc_Layout_vi.md`, concept `Art_Concept_References/v1/06_pixel_hud_skill_arc_v2.png`. Logical640×360: attack center(584,310), r26, skill orbit80/r13, góc[200,174,148,122,96,70], x=cx+r cos(theta), y=cy−r sin(theta). Touch target tối thiểu48dp và không overlap; cần dịch/tăng cả nhóm theo device thay vì scale phân số texture.

| Trạng thái skill | Hình ảnh | Input/âm thanh |
|---|---|---|
| Sẵn sàng | icon màu đủ, viền lớp mảnh | tap/click; âm confirm nhẹ tùy chọn |
| Đang hồi | mặt nạ tối + radial cooldown sweep + số giây còn lại | không gửi cast command; một lần rung ngắn khi vừa vào cooldown |
| Không đủ MP | icon giảm sáng, nhãn MP cost khi chọn | một âm trầm ngắn; không rung lặp khi giữ |
| Bị khóa/khống chế | khoá nhỏ + thời gian/lý do nếu server có | input bị chặn, mô tả ngắn |
| Đang thi triển | viền progress theo thời gian cast, haptic rất nhẹ | không gửi lệnh thứ hai nếu skill có cast lock |
| Tuyệt kỹ sẵn sàng | vòng vàng sáng tối đa 1 nhịp khi vừa đầy | không dùng flash màn hình hoặc âm thanh liên tục |

Cooldown là kết quả từ server; sweep vẽ theo thời gian còn lại đã đồng bộ, không xác nhận skill đã kích hoạt trước ACK. Damage, cost, target và resource vẫn do server authoritative xử lý. VFX skill không biến mất trong LowFX; chỉ giảm hạt phụ/flash.

**Nút tiện ích phía trên cung:** `Khóa mục tiêu` và `Đổi bộ kỹ năng`. Khóa mục tiêu có 3 state: chưa khóa, đã khóa (viền vàng), mục tiêu mất tầm/line-of-sight (viền đứt). Đổi bộ chỉ khả dụng ngoài combat/hub theo rule GDD; trong combat hiển thị lý do disable. Không có click-through vào nút đánh khi nhấn các tiện ích.

**Phím PC:** J/chuột trái đánh thường,1–6 kỹ năng,Space/Shift né,F tương tác,Q/E thuốc theo DEC-016; badge lấy keybind hiện hành. Input text/modal chặn gameplay hotkey.

### 9. Trạng thái gameplay và ưu tiên hiển thị

| Trạng thái | HUD cần đổi |
|---|---|
| Khám phá | tracker bình thường; minimap đủ marker đã mở; joystick/hub ở alpha thấp khi không chạm |
| Combat thường | nameplate target; số damage giới hạn mật độ; nút kỹ năng chuyển trạng thái ready/cooldown |
| Boss telegraph | ưu tiên contrast telegraph và edge warning; tự hạ alpha chat/toast; không tự ẩn minimap/quest objective cần cơ chế |
| HP dưới 25% | icon cảnh báo + viền HP pulse 1Hz; có tùy chọn tắt âm/rung nhưng không tắt biểu tượng |
| Thăng cấp | viền portrait và EXP hoàn tất; toast góc trái trên 3s; không che skill đang dùng |
| Nhận loot | toast tối đa 2 dòng, tự tắt 4s; nút chạm mở chi tiết, không tự trang bị |
| Tương tác NPC/đồ vật | nút `Tương tác` xuất hiện gần cụm hành động, gợi ý phím F trên PC; không chồng nút đánh |
| Chat nhập liệu | joystick vẫn hoạt động nếu người chơi bật; skill input bị khóa trong ô nhập để tránh gửi chiêu nhầm |
| Mất kết nối | ribbon trạng thái rõ, ping/đồng bộ; chặn cast/giao dịch khi server chưa xác nhận; không tự xóa thao tác pending |
| Cinematic/death/respawn | có thể ẩn joystick/hub; portrait và thông tin quan trọng vẫn nhìn được; nút bỏ qua/hồi sinh tách biệt |

### 10. Mô hình dữ liệu client cho HUD

HUD subscribe một snapshot đã xác thực cùng các delta sự kiện; animation nội suy giữa snapshot, không giữ logic game. Tối thiểu cần các field sau:

```json
{
  "player": {"id":"p-1024","name":"Lam","classId":"CLASS_HUYEN_BUT","level":24,"realmLabel":null,"portraitKey":"PORTRAIT_HB_01"},
  "vitals": {"hp":820,"hpMax":1200,"mp":240,"mpMax":380,"classResource":{"name":"Thủy Ấn","value":3,"max":5},"shield":{"value":0,"max":0,"expiresAt":null},"exp":{"value":4200,"toNext":6000}},
  "wallet": {"tinhNgoc":125},
  "world": {"mapId":"MAP_LAM_TRIEU","mapName":"Rừng Lâm Triều","channel":"Kênh 03","serverTime":"19:42:08","x":128.4,"y":0.0,"pingMs":42},
  "party": {"members":[],"targetId":null},
  "quests": [{"questId":"C2-03","chapter":"II · Rừng nhớ tên người","pinned":true,"objectives":[{"id":"valves","text":"Mở van nước","value":1,"target":3,"state":"active","worldTargetId":"OBJ_LT_VALVE_B"}]}],
  "skills": [{"skillId":"SK-HB-01","slot":1,"state":"ready","cooldownEndsAt":null,"mpCost":12,"keyHint":"Q"}],
  "client": {"fps":60,"lowFx":false,"hudScale":1.0}
}
```

`realmLabel` là optional; nếu null thì chỉ hiện cấp. `shield` trống/0 thì ẩn thanh Hộ Thể. `classResource.name` lấy từ class config, không hardcode theo tên nhân vật. `serverTime` do dịch vụ world gửi; `fps` chỉ là telemetry client. Text quest/NPC lấy localization key hoặc text đã localize; không ghép chuỗi tùy tiện từ ID. Mọi số phải có clamp/format fallback khi null, mất mạng hoặc dữ liệu cũ.

### 11. Hợp đồng dựng giao diện HTML/CSS hoặc native UI

```html
<main class="game-viewport">
  <canvas id="world" aria-label="Khung cảnh trò chơi"></canvas>
  <section class="game-hud" aria-label="Giao diện trong game">
    <header class="hud-player" data-widget="player-status"></header>
    <aside class="hud-minimap" data-widget="minimap"></aside>
    <aside class="hud-quest" data-widget="quest-tracker"></aside>
    <nav class="hud-movement" data-widget="movement-controls"></nav>
    <nav class="hud-actions" data-widget="combat-actions"></nav>
    <output class="hud-telemetry" data-widget="telemetry"></output>
  </section>
</main>
```

Root HUD phủ canvas (`position:absolute; inset:0; z-index:10`). Bản thân `.game-hud` đặt `pointer-events:none`; chỉ button, slider, minimap và panel được bật `pointer-events:auto`. Mỗi component có accessible name, focus outline, state `disabled/busy/selected`, label đọc màn hình và vùng chạm 48×48 dp tối thiểu. Native client phải giữ cùng token/neo/hành vi nếu không dùng DOM.

CSS tokens cốt lõi: `--hud-slate`, `--hud-brass`, `--hud-gold`, `--bar-hp`, `--bar-mp`, `--bar-class`, `--bar-guard`, `--safe-top/right/bottom/left`, `--hud-scale`. Dùng `env(safe-area-inset-*)` trên web wrapper; `clamp()` chỉ cho layout/spacing; sprite/icon/font render theo logical pixel grid với integer scale. Dùng `grid`/`flex` bên trong component, anchor ngoài theo góc. Animation UI ưu tiên đổi frame/opacity, không layout-thrash; không blur toàn màn hình.

### 12. Khả năng tiếp cận, hiệu năng và tiêu chí bàn giao

- Tối thiểu 4.5:1 cho chữ nhỏ, 3:1 cho glyph lớn/viền control; glyph HP/MP/class/shield không chỉ khác màu.
- Mọi thao tác skill có thể dùng touch, chuột, bàn phím và tay cầm; thứ tự focus đi từ status → quest/map → action.
- Hỗ trợ tay trái bằng mirror toàn bộ joystick/action hub, giữ nguyên icon nội dung và minimap; vị trí lưu theo thiết bị/tài khoản.
- Slider riêng cho UI scale 80–125%, chữ, LowFX, rung, camera shake, âm cảnh báo và telemetry. HUD giảm hiệu ứng vẫn giữ telegraph và trạng thái cooldown.
- Không phát ra particle nặng từ HUD; atlas icon được cache, minimap cập nhật theo event/10Hz tối đa, telemetry FPS lấy mẫu 1Hz, không render text mỗi frame.
- Khi mở panel lớn, world input bị chặn theo modal policy; HUD combat có thể ẩn trừ HP/party/boss telegraph khi setting cho phép.
- Bàn giao cần mockup 1280×720, 1920×1080, 1920×1200, 2400×1080; state bình thường, boss, HP thấp, cooldown, không đủ MP, Hộ Thể, mất kết nối, LowFX, tay trái.
- Bàn giao UI gồm source pixel-art PNG/layers, icon map, palette/bitmap font tokens, component state sheet, keybind map, localization keys, safe-area guide và import/scale nguyên preset.

### 13. Liên kết nguồn

- UI tổng thể và panel ngoài gameplay: `UI_UX_Spec_vi.md`.
- Quy tắc màu, asset, tỷ lệ nhân vật, LowFX: `Art_Entity_Weather_UI_Visual_Bible_vi.md`.
- Thời gian cast, hiệu lực, telegraph/VFX: `Combat_Skills_VFX_Animation_Spec_vi.md`.
- Tài nguyên lớp và cooldown cấp 1: `Content_Bible_Ngu_Mach_Huyen_An_vi.md`.
- Stat, slot trang bị, binding, ví và vật phẩm: `Character_Equipment_Inventory_Spec_vi.md`, `Item_Catalog_and_Set_Bible_vi.md`.
