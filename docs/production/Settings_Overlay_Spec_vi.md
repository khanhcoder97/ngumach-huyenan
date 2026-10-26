# ĐẶC TẢ MODAL CÀI ĐẶT — OVERLAY GAMEPLAY
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.0

### 1. Phạm vi và quy tắc trải nghiệm

Modal Cài đặt là lớp giao diện nổi cho phép chỉnh điều khiển, hình ảnh, hiệu năng, âm thanh, HUD và tài khoản mà không rời phiên chơi. Toàn bộ UI là pixel art theo `Pixel_Art_Production_Standard_vi.md`: nền slate/nâu gỗ dùng tile texture có chu kỳ, frame pixel 9-slice, bitmap font tiếng Việt; không blur/anti-aliasing/scale lẻ. Không dùng asset/icon lấy từ KPAH.

Đây là MMORPG trực tuyến nên **mở modal không dừng mô phỏng thế giới**. Nhân vật dừng nhận lệnh di chuyển/đánh khi modal có focus; server vẫn chạy combat và trạng thái nhóm. Nếu mở khi đang giao tranh, hiện nhãn nhỏ “Thế giới vẫn tiếp tục”; nút Tiếp Tục Hành Trình luôn là hành động lớn nhất để đóng nhanh. Không cho phép dùng modal để né đòn, ngắt boss hoặc giữ hoạt động khỏi timeout.

Modal chỉ quản lý cài đặt và điều hướng tới dịch vụ tài khoản. Không gửi mật khẩu, không thực hiện xóa tài khoản chỉ bằng một lần bấm, không đưa giao dịch tiền thật vào lớp này.

### 2. Khung modal, responsive và lớp phủ

Overlay dùng `position: fixed; inset: 0; z-index: 100`. Backdrop phủ toàn màn với slate đen opacity 60–68%, không blur. Dialog đặt giữa safe area, có focus trap, Escape/Back đóng, X đóng và khôi phục focus về nút đã mở modal. UI frame/bitmap font được vẽ theo logical pixel grid, không scale lẻ.

| Kích thước | Khung modal | Bố cục |
|---|---|---|
| PC 1920×1080 | rộng 1080–1180px, cao tối đa 780px, giới hạn 92vh | 2 cột `1fr 2fr`; trái 340–380px, phải 680–760px |
| PC 16:10 / 1366×768 | rộng 94vw, cao 92vh | 2 cột nếu content area ≥900px; cột cài đặt cuộn riêng |
| Mobile ngang 1280×720 trở lên | rộng 96vw, cao 94vh | 1 cột cuộn; CTA tiếp tục sticky ở đáy, account card gấp gọn |
| Cửa sổ nhỏ / tỷ lệ hẹp | rộng 100% safe area, cao 100% safe area | 1 cột; header và CTA cố định, nội dung cuộn |

Nền dialog gồm lớp `Ink-900`/gỗ gụ opacity 96%, viền đồng 1.5px, shadow 0 16px 48px rgba(0,0,0,.55), góc 14px. Ornament vàng chỉ đặt ở bốn góc; không đặt dưới label hoặc control. Nội dung trong modal cuộn mà header, nút đóng và CTA tiếp tục vẫn truy cập được.

**Breakpoints layout:** chuyển sang 1 cột khi chiều rộng hữu dụng <900px hoặc chiều cao <700px. Trên mobile, không ép người chơi vào portrait; `Bố cục dọc` bên dưới là mật độ/xếp chồng HUD, không phải xoay màn hình dọc. Game giữ ngang theo GDD.

### 3. Header và hành động đóng

Header cao 64–76px trên PC, 52–60dp mobile; trái có biểu tượng ấn/bánh răng và tiêu đề `CÀI ĐẶT`; phải có trạng thái lưu (`Đã lưu` / `Đang lưu…` / `Chưa đồng bộ`) và nút `X`. Dưới tiêu đề có thể hiện mô tả nhỏ `Tùy chỉnh trải nghiệm chơi`.

- `Esc / Quay lại`: đóng modal; nếu có thao tác chưa đồng bộ thì lưu thay đổi an toàn trước khi đóng hoặc hỏi xác nhận nếu thay đổi cần preview.
- Nút `X`: cùng hành vi với Esc; có tooltip và vùng chạm tối thiểu 48×48dp.
- `Tiếp Tục Hành Trình`: CTA chính ở đầu panel trái trên desktop; trên mobile là sticky bottom button. Đóng modal và về game, không mở cửa hàng.
- Gamepad: B/Back đóng; focus ban đầu ở nút Tiếp tục; focus trap không cho tab thoát ra viewport.

### 4. Cột trái — CTA và tài khoản

#### 4.1 CTA Tiếp Tục Hành Trình

Banner rộng toàn cột, cao 76–92 CSS px PC/68–80dp mobile; nền ramp vàng đồng theo dải pixel, icon cổng mạch ở trái, bitmap title 18–20px và mô tả `Đóng cài đặt, trở lại thế giới`. Hover/focus đổi frame/icon; pressed đổi ramp; disabled chỉ khi đang xử lý lưu bắt buộc. Có thể hiện phím `ESC` như hint nhỏ, không thay label.

#### 4.2 Thẻ hồ sơ

Thẻ Slate opacity 92%, viền Paper-200 mảnh; hiện tên nhân vật, ID rút gọn (ví dụ `NM-•••-4821`), máy chủ/khu vực, loại tài khoản `Khách` hoặc `Đã liên kết email`. Email nếu đã liên kết phải che một phần (ví dụ `l***@mail.com`). Không hiển thị token, mật khẩu hoặc thông tin thanh toán.

| Hành động | Kiểu nút | Hành vi |
|---|---|---|
| Liên kết email | primary/bronze-gold | mở luồng Account Service bảo mật; giữ trạng thái game, không nhập mật khẩu ngay trong modal; sau hoàn tất trả về và cập nhật badge |
| Đăng xuất | secondary warning/maroon | mở confirm nêu nhân vật/khu vực; trạng thái đã lưu được xác nhận trước khi kết thúc session; với tài khoản khách, nhắc liên kết trước khi rời nhưng vẫn cho chọn tiếp tục |
| Xóa tài khoản | danger outline, chữ đỏ muted | mở trang/quy trình riêng, yêu cầu xác thực lại và xác nhận rõ hậu quả; không xóa ngay từ click đầu; không nằm cạnh CTA tiếp tục |

Các thao tác đăng xuất/xóa/liên kết cần keyboard confirmation, screen-reader label và trạng thái lỗi mạng. Dịch vụ account trả kết quả; client không tự giả định tài khoản đã liên kết/xóa thành công.

### 5. Cột phải — lưới cài đặt

Cột chính dùng 2 cột tile đồng nhất. Mỗi tile có icon line 20–24px, tên mục, giá trị hiện tại, control và trợ giúp một câu. Tile cao tối thiểu 94px, bo 10px, nền slate sáng hơn panel 4–6%, border bronze ở trạng thái focus/active. Các lựa chọn chọn được dùng pill/segmented control; slider có số cụ thể và nút reset.

#### 5.1 Điều khiển và input

| Setting | Giá trị/UI | Quy tắc |
|---|---|---|
| Chế độ input | Tự động / Cảm ứng / Bàn phím + chuột / Tay cầm | chỉ hiển thị phương thức tương thích thiết bị; `Tự động` ưu tiên input hoạt động gần nhất; trên cảm ứng, D-pad/joystick được chọn ở `Kiểu di chuyển` |
| Kiểu di chuyển | D-pad / Joystick tự do | mobile only; D-pad có 4/8 hướng; joystick tự do có dead zone 12% và tùy chọn vị trí trái/phải |
| Bố cục nút | Mặc định / Chỉnh sửa… | `Chỉnh sửa` mở HUD layout editor; preview hitbox, reset, hoàn tác, lưu preset; nút combat phải giữ khoảng chạm tối thiểu 48dp |
| Rung phản hồi | Tắt / Nhẹ / Chuẩn | mobile/tay cầm; preview chỉ rung ngắn, không rung mạnh bất ngờ |

PC hỗ trợ remap toàn bộ phím. Không có click-to-move mặc định; mapping không ghi đè OS shortcut phổ biến nếu có xung đột. Khi người chơi đang nhập chat, phím skill không gửi command.

#### 5.2 Chủ đề và khung nhìn

| Setting | Giá trị/UI | Quy tắc |
|---|---|---|
| Chủ đề môi trường | Thủy Mặc / Chuẩn / Rực Rỡ | thay color grading/palette môi trường ở client; không đổi màu telegraph, màu UI trạng thái, hitbox hay nội dung gameplay |
| Tỷ lệ HUD | Nhỏ 80% – Chuẩn 100% – Lớn 125% | preview trực tiếp; clamp để button không lọt ngoài safe area |
| Khung nhìn | Chuẩn / Rộng / Siêu rộng | điều chỉnh camera trong giới hạn map và GDD (32 WU ở 16:9, tối đa khoảng 40 WU ở 20:9); ở tỷ lệ trên 20:9, phần dư dùng cho nền parallax/biên UI, không mở thêm tầm nhìn gameplay; PvP/raid chuẩn hóa camera |
| Bố cục ngang | Gọn / Chuẩn | nén khoảng cách/ẩn widget phụ nhưng không đổi hướng thiết bị; gameplay vẫn nằm ngang |

#### 5.3 Đồ họa và hiệu năng

| Setting | Giá trị/UI | Quy tắc |
|---|---|---|
| Chất lượng đồ họa | Tự động / Thấp / Trung bình / Cao / Siêu cao | preset điều khiển texture, bóng, hậu kỳ và số hạt; không làm telegraph biến mất |
| Hiệu ứng thời tiết | Bật / Tắt | tắt hạt mưa/tuyết/bụi trang trí và lớp mờ; hazard/telegraph sự kiện vẫn còn nguyên |
| Hiển thị người chơi | Tất cả / Bang hội + party / Ẩn người chơi khác | chỉ giảm actor không thuộc party; đồng đội, NPC quest, boss, telegraph và vùng tương tác luôn hiện |
| Giới hạn FPS | Tự động / 30 / 60 | tùy khả năng thiết bị; 30 fps là fallback mobile thấp, 60 fps mặc định ở thiết bị đạt cấu hình; không ép FPS vượt refresh rate |
| Tự hạ chất lượng | Bật / Tắt | khi FPS dưới mục tiêu liên tục 5s, hạ theo nấc particle → shadow → post-process; không tự đổi cỡ chữ/telegraph; hiện toast có nút hoàn tác |
| Giảm hiệu ứng chiến đấu | Bật / Tắt | rút gọn hạt/flash/rung; giữ silhouette, màu/pattern nguy hiểm và thời gian báo đòn |

Nếu preset Low được chọn, thời tiết trang trí có thể tự chuyển Off và hiện badge `Tắt bởi preset Thấp`; người chơi vẫn được bật lại nếu máy giữ FPS ổn định. Tắt người chơi khác không được ẩn chat lời mời/raid member hoặc tác nhân gameplay quan trọng.

#### 5.4 Âm thanh và chỉ dẫn

| Setting | Giá trị/UI | Quy tắc |
|---|---|---|
| Âm lượng tổng | slider 0–100%, icon mute và nhãn Mute/Thấp/Vừa/Cao | cập nhật trực tiếp, có nút nghe thử an toàn; không tự phát âm thanh lớn khi mở modal |
| Nhạc / Hiệu ứng / Thoại | ba slider riêng 0–100% | mỗi slider có số %, nút reset; thoại có ưu tiên ducking khi hội thoại mở |
| Hướng dẫn đường | Bật / Tắt | mũi tên mép màn hình chỉ xuất hiện khi objective có world target hợp lệ; không tự dẫn vào khu chưa mở |
| Âm báo boss | Bật / Tắt / slider | độc lập với âm lượng tổng; tắt tiếng không xóa icon/shape cảnh báo |

#### 5.5 Bố cục và khả năng tiếp cận

| Setting | Giá trị/UI | Quy tắc |
|---|---|---|
| Chỉnh D-pad/joystick | nút `Mở chỉnh sửa` | mở HUD layout editor; có preset mặc định, tay trái, ít che màn; lưu theo nhân vật/thiết bị |
| Bố cục giao diện | Gọn / Chuẩn | điều chỉnh xếp chồng và mật độ HUD ngang; không cung cấp portrait mode vì game thiết kế landscape |
| Cỡ chữ HUD | 90–140% | preview ngay; tooltip/quest wrap text, không cắt tên kỹ năng |
| Tương phản cao | Bật / Tắt | tăng nền panel, outline và tương phản icon mà vẫn giữ màu hệ |
| Mù màu | Mặc định / Protanopia / Deuteranopia / Tritanopia | đổi palette phụ và pattern; không chỉ recolor telegraph |
| Chuyển động giảm | Bật / Tắt | giảm parallax, pulse và camera shake UI; không giảm độ dài telegraph |

### 6. Chân modal — trợ giúp và tiện ích

Các nút tiện ích xếp thành ba tile trên desktop, xếp dọc/mobile theo thứ tự Tutorial, Góp ý, Thoát kẹt. Link Privacy, Điều khoản, Hỗ trợ nằm dưới cùng, cỡ 12–14px và đủ tương phản; mở trang an toàn trong browser/app panel, quay lại không mất thiết lập đang chỉnh.

| Tiện ích | Hành vi |
|---|---|
| Xem lại hướng dẫn | mở danh sách tutorial đã mở khóa, resume từ chương đã chọn; không reset quest hay phát lại nội dung thưởng |
| Góp ý | mở form có loại lỗi/ý tưởng, map/build/device metadata tùy opt-in; preview nội dung trước khi gửi; lỗi gửi không xóa text |
| Thoát kẹt | gửi request đến server để kiểm tra vị trí và trạng thái; chỉ teleport tới safe point gần nhất nếu ngoài combat/boss/raid/siege, không có giao dịch/quest escort đang khóa vị trí và server chấp thuận; có confirm, cooldown, thông báo đích và không mất item/quest |
| Privacy / Điều khoản / Hỗ trợ | link versioned, có phiên bản ngôn ngữ phù hợp; nút Back quay về modal |

Nếu `Thoát kẹt` không hợp lệ, giải thích lý do cụ thể (ví dụ `Không dùng được trong raid đang diễn ra`) và mở shortcut báo lỗi. Client không tự dịch chuyển nếu mất kết nối hoặc chưa nhận xác nhận server.

### 7. Quy tắc áp dụng, lưu và khôi phục

- Âm lượng, chủ đề, HUD scale, accessibility, minimap và UI density là live preview, lưu debounce 500ms vào preferences; nhãn header chuyển `Đang lưu…` rồi `Đã lưu`.
- Đồ họa/chất lượng/FPS áp dụng dưới dạng preview 15 giây; hộp xác nhận đếm ngược `Giữ thay đổi` / `Hoàn tác`. Hết giờ hoặc mất focus/mất kết nối thì tự trở về config gần nhất đã xác nhận.
- Input/layout preview có nút `Lưu bố cục` và `Khôi phục`; nếu đóng khi còn preview chưa xác nhận, hỏi `Giữ hay hoàn tác`.
- Cài đặt cá nhân lưu theo account + thiết bị; keybind, d-pad placement, FPS cap ưu tiên lưu per-device. Server-authoritative gameplay state không bị ghi bởi UI settings.
- Có nút `Khôi phục mặc định` trong phần cuối; confirm một lần, chỉ reset local preferences, không reset account/nhân vật.
- Nếu save lỗi, giữ local pending, hiện retry và không báo thành công giả. Khi đã lưu server/local xong, thoát modal bằng Esc không hỏi thêm.

### 8. Component states và tương tác

| Thành phần | States tối thiểu |
|---|---|
| Modal | opening, open, saving, error, closing; focus-trapped; safe area |
| Tile/option | idle, hover, focus, selected, disabled, busy, preview-pending |
| Slider | min/max, keyboard adjustment, readout, mute, reset-to-default |
| CTA | default, hover, pressed, focus, saving, disabled |
| Account action | ready, confirm, authenticating, pending, success, error, offline |
| Utility | ready, request, server validation, cooldown, rejected, success |

Mouse hover/focus có giải thích; click/Enter chọn; Space toggle; slider dùng phím mũi tên và Home/End. Mobile chạm một lần, vùng chạm ≥48dp, không yêu cầu hover. Gamepad điều hướng theo hàng: CTA → account → grid trái sang phải → tiện ích → legal. Tooltip có accessible description và không che control đang focus.

### 9. Ngôn ngữ và visual tokens

- Header/title: gold `#E8C878`, 24–30px desktop/20–24sp mobile, trọng lượng 700.
- Nền modal: `#171A1C`/mahogany `#35241E`, opacity 96%; texture gỗ chỉ là noise/line cực nhẹ, không tạo pattern cạnh text.
- Bronze border: `#B88B4A`; active fill `#684C27`; danger `#8F3540`; muted `#899296`; body `#F1E8D5`.
- Tile 2 cột có gap 12–16px; label 15–17px; description 12–14px; control cao ≥40px desktop/44–48dp mobile.
- Selected option có viền vàng + check/glyph; inactive vẫn đạt contrast đọc được, không hạ opacity chữ dưới mức tiếp cận.
- Icon line 2px, đồng nhất stroke; không dùng icon chỉ dựa vào chữ Hán giả hoặc ký tự không rõ nghĩa.

### 10. Cấu trúc HTML/CSS tham chiếu

```html
<div class="settings-backdrop" data-open="true">
  <section class="settings-modal" role="dialog" aria-modal="true"
           aria-labelledby="settings-title" aria-describedby="settings-status">
    <header class="settings-header">
      <h1 id="settings-title">Cài đặt</h1>
      <button type="button" aria-label="Đóng cài đặt">×</button>
    </header>
    <div class="settings-layout">
      <aside class="settings-account">
        <button class="continue-journey">Tiếp Tục Hành Trình</button>
        <section class="account-card" aria-label="Tài khoản"></section>
      </aside>
      <main class="settings-grid" aria-label="Tùy chọn trò chơi"></main>
    </div>
    <footer class="settings-footer"></footer>
  </section>
</div>
```

Desktop `.settings-layout` dùng `grid-template-columns: minmax(280px,1fr) minmax(560px,2fr)`. Mobile breakpoint dùng một cột, `max-height: 94dvh`, body cuộn dọc, CTA sticky ở đáy. Dialog root dùng z-index 100 trên HUD gameplay; khi focus nằm trong modal, ngăn input bàn phím đi xuống canvas. Backdrop dùng `background: rgba(5,8,11,.64)` không `backdrop-filter`; icon/frame/font pixel art giữ sampling point và integer scale.

Mọi option dùng preference key machine-safe, tách khỏi text dịch: `input.mode`, `movement.layout`, `visual.theme`, `camera.viewScale`, `graphics.quality`, `graphics.weatherFx`, `graphics.playerVisibility`, `graphics.fpsCap`, `graphics.autoLower`, `audio.master`, `navigation.arrow`, `hud.density`, `accessibility.textScale`, `accessibility.colorMode`. Lưu schema có `value`, `deviceScope`, `updatedAt`, `schemaVersion`; migration không được reset keybind/layout khi thêm setting mới.

### 11. Tiêu chí bàn giao

- Có mockup PC 1920×1080, 1366×768, mobile ngang 1280×720 và 2400×1080; dark/light state không cần thiết vì game dùng dark theme.
- Chứng minh 2 cột chuyển đúng thành 1 cột ở breakpoint, legal footer và CTA vẫn truy cập khi nội dung cuộn.
- Có state sheet cho selected/inactive, hover, focus, disabled, saving, offline, confirm, preview timeout, error.
- Account card che email/ID nhạy cảm; logout, link, xóa tài khoản và thoát kẹt luôn chờ phản hồi dịch vụ tương ứng.
- Cài đặt thời tiết LowFX không xóa telegraph; ẩn actor không ẩn party/boss/NPC nhiệm vụ; camera không tạo lợi thế PvP.
- Kiểm tra keyboard-only, controller, screen reader labels, vùng chạm 48dp, scale HUD 80–125%, text lớn và giảm chuyển động.

### 12. Tài liệu liên quan

- HUD trong gameplay: `Gameplay_HUD_Overlay_Spec_vi.md`.
- UI/UX toàn game: `UI_UX_Spec_vi.md`.
- Chức năng tài khoản/session và tùy chọn: `MMORPG_Functional_Spec_vi.md`.
- Quy tắc hiệu ứng thời tiết và LowFX: `Art_Entity_Weather_UI_Visual_Bible_vi.md`.
