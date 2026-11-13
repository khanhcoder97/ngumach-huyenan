# Asset 20261113f — Huyết Nguyệt, Tàn Hỏa và Xích Ảnh

20 sheet chọn / 320 khung nguồn mới, tạo bằng imagegen tích hợp. Giữ nhân vật chibi nguyên khối đã chốt: tóc đen có lọn cam đồng, áo ngắn đỏ rượu/than, đai vàng đất, quần tối và đao cong một lưỡi. Không quay lại paperdoll. PNG và prompt thực: `Art_Source/Actor_Library_20261107/Sheets/` và `Prompts/`; inventory: `batch_20261113f.json`.

## Bộ chuyển động thân

Mỗi action có năm góc vẽ nguồn N/NE/E/SE/S × 16 tư thế. SW/W/NW dùng lật theo policy; đây là hướng xem bổ sung, không phải ba góc vẽ mới. Tổng phần thân 15 sheet / 240 khung. Nhân vật và đao nằm chung trong mỗi source; VFX tách riêng.

| Action | Nhịp trình bày | Phân khung nguồn | Choreography |
|---|---|---|---|
| skill_01 / Huyết Nguyệt | 0,64 s | 0–3:30 ms; 4–9:33,3333 ms; 10–15:53,3333 ms | Nạp thế, một cung chém ngang thấp, theo đà rồi hồi; không lặp hai đòn |
| skill_02 / Tàn Hỏa | 0,72 s | 0–3:40 ms; 4–9:40 ms; 10–15:53,3333 ms | Tay trái đặt dấu về mục tiêu, tay phải vẫn giữ đao thấp; không tự chém hoặc nổ |
| skill_03 / Xích Ảnh | 0,66 s | 0–3:35 ms; 4–6:33,3333 ms; 7–8:40 ms; 9–11:33,3333 ms; 12–15:60 ms | Co thế 0,14; chém thuận 0,10; đổi cổ tay 0,08; chém ngược 0,10; hồi 0,24 s |

Profile là giả định trình bày phục vụ art review. Cửa hit của Xích Ảnh giữ hai nhịp 0,10 s theo mô tả combat; các mốc pose không phải wire event và không cấp damage, Nhiệt, i-frame hoặc quyền dịch chuyển. Tàn Hỏa 0,72 s chỉ là thao tác đặt dấu; không thay thời gian dấu 5 s, CD, MP hay điều kiện kích nổ. Root nguồn đứng tại chỗ; lướt ngắn do gameplay/collision xử lý riêng.

Library và raw/grouped Studio đọc cùng `sourceFrameDurationsMs`. Mốc skill_01:0,12/0,32; skill_02:0,16/0,40; skill_03:0,14/0,24/0,32/0,42 s. Kiểm giữ khung cuối, seek/resume, lặp về0 và JSON roundtrip; lấy mẫu 60 bước/s phải thăm đủ16 khung ở mọi hướng.

## Năm VFX component

| ID | Nhịp xem | Neo / scale tham chiếu | Chức năng hình ảnh |
|---|---|---|---|
| sk_ad_02_mark_component | 0,80 s, lặp | SYMMETRIC_BOUNDS_CENTER / LONGEST_AXIS | Vòng than dẹt có đúng năm khe sáng cố định, pulse nhẹ; không tự nổ |
| sk_ad_02_pop_component | 0,40 s, một lần | CELL_CENTER / LONGEST_AXIS | Một đợt bụi than/tia lửa ngắn hướng ra ngoài khi có trigger hợp lệ |
| sk_ad_02_expire_component | 0,32 s, một lần | SYMMETRIC_BOUNDS_CENTER / LONGEST_AXIS | Vòng rạn rồi tắt thành vụn nhỏ; không nổ khi hết hạn |
| sk_ad_03_first_cut_component | 0,32 s, một lần | CELL_CENTER / LONGEST_AXIS | Cung thuận với mép cam ở phía dưới và mũi dưới-phải |
| sk_ad_03_reverse_cut_component | 0,32 s, một lần | CELL_CENTER / LONGEST_AXIS | Cung ngược với mép cam ở phía trên và mũi trên-phải |

Mỗi component có16 source frame riêng. Vệt Huyết Nguyệt `sk_ad_01_cut_component` đã có từ đợt20261112f, không cộng lại vào320 nguồn mới. Lifetime vệt0,32 s có đuôi tan; không biến cửa gây damage0,10 s thành0,32 s. Editor span160 px hoặc chiều cao thân140 px là thước xem, không suy bán kính hit/world units từ texture.

Studio giữ frame cuối của clip một lần để kiểm nguồn. Khi ghép gameplay, hết lifetime/nhánh expire phải tháo component; không giữ các vụn than hoặc vệt cuối vĩnh viễn. Vòng mark chỉ được lặp trong lúc trạng thái dấu còn hiệu lực và phải dừng trước khi chuyển sang pop/expire.

Dấu Tàn Hỏa gắn TARGET_FOOT theo đặc tả, không gắn nhầm dưới caster. Hết hạn chọn expire; chỉ trigger đã được xác nhận mới chọn pop. Năm khe không phải biểu diễn số Nhiệt đang có. Adapter server, LowFX, chọn mục tiêu và ghép body/status/impact thành toàn kỹ năng vẫn cần tích hợp; các file nguồn không tự tạo logic đó. Xích Ảnh có hai nhịp riêng và không dùng ảnh phân thân.

## Đăng ký nguồn và các bản sửa

`DARK_BOOT_CORE_FOOT` dành riêng palette Ảnh Đao: chọn khối giày/quần tím nâu tối có phần ruột đủ dày, loại màu thép/vàng và viền đao mảnh. Bộ lọc giày nâu Minh Kiếm không phù hợp, có thể neo lên ống chân. `calibrate_anh_dao_registration.py --apply` lưu15 chiều cao trung tính vào `body_registration_20261113f.json`; cùng một chiều cao dùng suốt clip, không kéo giãn từng frame, không sửa PNG. Neo và body/weapon contact vẫn phải xem native.

Huyết Nguyệt E có mũi đao mảnh tách thành đảo trong projection, dùng grid4×4 đã xem toàn sheet. S dùng các đường cắt grid tường minh trong khoảng trống thật vì vệt theo đà vượt ô chia đều lý tưởng. `VISUALLY_VERIFIED_DIRECTIONAL_GRID` chỉ nhận class có một facing khai báo và16 ô. Explicit edges phải là số nguyên tăng dần, bắt đầu0 và kết thúc đúng biên ảnh. Kiểm ô rỗng, cắt sát mép/đè ô và pixel trùng vẫn giữ.

Ba biến thể cùng đợt được giữ nguyên trong lịch sử:

- Huyết Nguyệt SE v1 có mảnh matte đậm nối khoảng trống giữa cột2/3. Chọn v2 sạch, giữ choreography; không cố cắt bỏ đầu đao hoặc hạ kiểm mép để nhận v1.
- Xích Ảnh first-cut v1 có hướng mép sáng giống cung ngược. Chọn v2 vẽ mép dưới/mũi dưới-phải, phân biệt chiều chém.
- Tàn Hỏa expire v1 có đuôi RGBA rất mờ; bộ đo alpha200 báo thiếu ô. V2 tăng phần vụn cuối và giữ bốn tư thế tan khác nhau. Frame15 vẫn có alpha tối đa199, không phải ô trắng/rỗng. Cho phép đọc bounds alpha64 **chỉ từ frame12** bằng `translucentTailFromFrame`; vẫn cần ít nhất4pixel alpha64, kiểm mép và hash đầy đủ. Không bật cho actor, giữa clip hay ô hoàn toàn trong suốt. Render giữ nguyên RGBA nguồn, không nâng opacity hoặc nhân khung bằng code.

Tổng23 PNG mới lưu, chỉ20 bản chọn/320 khung được tính. Prompt thực và record nguồn cũ nằm trong `generation_history.json`. Các phần alpha200 của nguồn cũ và mọi nguồn/binding trước đợt này giữ nguyên.

## Xem và kiểm tra

```powershell
ClientGodot/Run_Actor_Library.ps1 -Actor CLASS_ANH_DAO -Clip skill_01
ClientGodot/Run_Actor_Library.ps1 -Actor CLASS_ANH_DAO -Clip skill_02
ClientGodot/Run_Actor_Library.ps1 -Actor CLASS_ANH_DAO -Clip skill_03
ClientGodot/Run_Art_Studio.ps1 -Entry sk_ad_02_mark_component
Tools/ArtProduction/review_actor_batch_20261113f.ps1 -Resume
```

Studio giữ chỉnh tay source frame, timing, vị trí/pivot, layer/socket và chèn component. Nguồn mới chưa thay renderer gameplay. Approval nguồn không tự duyệt bản người dùng chỉnh trong Studio.

Evidence: `Implementation/Reports/Evidence/Actor_Batch_20261113f/`. Chín MP4 chọn, ảnh tĩnh/dải mẫu; Movie Maker180frame/3s mỗi video là xuất offline60 bước/s, không chứng nhận gameplay chạy thực60FPS. Whole-sheet source và native temporal samples được xem riêng. Native timing assertions, build/import, Python tests, inventory/export, SHA source/binding và baseline audit là các gate khác nhau.

Trạng thái nghiệm thu đợt: **20 source/clip/component đã kiểm whole-sheet và native, pin SHA source/binding riêng**. Giữ nguyên159 source pins trước đó. 62 Python tests đạt; .NET build0 warning/error; Godot import; native Library16.248 assertions, Studio77.212 assertions/286 entries.46 baseline PNG nguyên SHA,221 nguồn runtime khớp byte,204 source/binding trước không đổi.9 MP4 chọn decode sạch,180frame/3s mỗi video; không có video lịch sử vì ba lần sửa nguồn xảy ra trước native capture.

Catalogue224 page qua cấu trúc (gồm3 clip kế thừa),67/1008 job đủ góc nguồn,35 job đủ góc đã kiểm source; còn941 job thiếu.19 HOLD cũ và full `sk_mk_03_vfx` sai số hàng giữ nguyên. Component không được tính thành full-timeline VFX job. Không đóng mục tiêu toàn thư viện.

Ba body mới chưa làm Ảnh Đao đủ12 action; còn skill_04/05/06, né, các phản ứng HOLD và kiểm source cũ. Ghép toàn kỹ năng, đổi thế chưa rút/rút đao, VFX đa góc, world renderer/AI/collision, class/quái/boss/NPC/map/UI/icon/audio/biến thể tiếp tục. Source acceptance không phải nghiệm thu toàn class hoặc game.
