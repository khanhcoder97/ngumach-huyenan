# Asset 20261113e — phản ứng có kiếm và phòng kiểm nối hoạt ảnh

17 sheet chọn, 272 khung nguồn: Minh Kiếm bị đánh/ngã/né × năm góc × 16; Người Giữ Thuyền đi bộ E/NE × 16. Giữ nét chibi nguyên khối đã chốt. Dùng trình imagegen tích hợp; PNG gốc và prompt thực nằm trong `Art_Source/Actor_Library_20261107/Sheets/` và `Prompts/`. PNG runtime là bản sao nguyên byte, không vẽ lại bằng code, không nhân đôi chu kỳ tám khung.

## Nguồn chọn và các lần sửa

Minh Kiếm giữ tóc búi đen, áo trong ngà, áo khoác xanh ngọc viền vàng, giáp vai và một thanh kiếm thẳng cầm ở tay phải. Mỗi action có nguồn N/NE/E/SE/S; SW/W/NW dùng lật theo policy, không tính là ba hướng vẽ mới.

| Action | Tổng thời gian | Phân khung | Phạm vi |
|---|---:|---|---|
| Hurt | 0,30 s | 16 × 18,75 ms | Một nhịp bị đánh, lùi thân và hồi |
| Death | 1,20 s | 16 × 75 ms | Đứng → khuỵu → chống tay → ngã → giữ nằm |
| Dodge | 0,48 s | 0–3: 20 ms; 4–9: 30 ms; 10–15: 36,6667 ms | Co thế 0,08 / né thấp 0,18 / hồi 0,22 s |
| NPC walk E/NE | 0,80 s | 16 × 50 ms | Hai tiếp xúc chân đối nhau, pass ở 4/12 |

Timing là profile trình bày. Dodge có thêm 0,02 s hồi so với bảng combat 0,46 s; không tăng i-frame, quyền dịch chuyển hoặc khả năng xuyên địa hình. Death không phát sự kiện chết/hồi sinh. World root, hit, collision, AI và server không do source art quyết định.

Giữ bốn biến thể cùng đợt trong lịch sử: death S v1 có kiếm gập ở khung 10; NPC walk NE v1 có bóng/nền nâu; dodge E/SE v1 hồi còn thấp. Chọn v2 tương ứng, các trang khác chọn v1. Tổng cộng 21 PNG mới được lưu nhưng chỉ 17 trang/272 khung được tính vào lựa chọn. Bảy record hoạt động cũ được lưu vào `generation_history.json`; PNG cũ không bị sửa hoặc xóa. `replacement_history.json` ghi phạm vi thay thế.

## Neo chân và tỉ lệ

Hurt/dodge dùng `BOOT_CORE_FOOT`, chọn lõi giày/quần nâu và loại màu thép/vàng của kiếm khỏi neo. Death dùng `FOOT` để tư thế nằm tựa đất, không neo vào giày đang nhấc khỏi đất. Chiều cao trung tính cố định trong toàn clip, không phóng từng khung lên/xuống.

Hiệu chỉnh 15 trang bằng `calibrate_minh_kiem_weapon_registration.py --batch 20261113e --apply`. Khung trung tính mặc định là 0. Riêng dodge SE chọn `neutralSourceFrame: 15` vì khung đầu hơi chùng gối, khung cuối đứng thẳng; chiều cao đăng ký 262 pixel nguồn. Lưu bằng chứng ở `body_registration_20261113e.json`. Chỉ thay metadata, giữ nguyên raster.

Kiểm cao độ đỉnh alpha ở 15 mối nối, render cao 110 px: chênh tuyệt đối lớn nhất còn 4,1985 px, so với 6,6059 px ở bản cũ được giữ trong `Superseded_Dodge_EndHeight/`. Đây là phép sàng lọc cao độ; chưa phải nghiệm thu toàn silhouette hay mọi mối nối. Idle/walk kế thừa vẫn là tư thế cũ không cầm kiếm; nối đổi thế có kiếm/chưa rút kiếm còn phải làm.

## Phòng kiểm phản ứng tám hướng

Scene mới `ClientGodot/ActorReactionReview.tscn` phát đồng thời tám hướng theo chuỗi Thiết Y 0,80 → hurt 0,30 → dodge 0,48 → death 1,20 → giữ nằm 0,40 s. Chu kỳ 3,18 s lặp chỉ để kiểm art. Cả bốn clip giữ một root tại từng ô. Đường đất và dấu cộng vàng có thể ẩn; có tạm dừng/phát tiếp, phát từ đầu, tốc độ 0,1–2× và ESC.

```powershell
ClientGodot/Run_Actor_Library.ps1 -ReactionReview
ClientGodot/Run_Actor_Library.ps1 -SkipBuild -ReactionReview -Test
ClientGodot/Run_Actor_Library.ps1
ClientGodot/Run_Art_Studio.ps1
```

Library vẫn cho chọn actor/action, xem tám hướng, tua từng khung. Studio giữ chỉnh tay timing, pivot/tọa độ/layer/socket và nguồn. Đã sửa lỗi raw source hurt/death/dodge trước đây lấy mặc định 1,60 s; nay raw và grouped dùng cùng timing Minh Kiếm. Kiểm cả boundary dodge 0,08/0,26 s, giữ khung cuối, seek/resume và JSON roundtrip.

## Kiểm nguồn và bằng chứng

Evidence ở `Implementation/Reports/Evidence/Actor_Batch_20261113e/`:

- Xem toàn sheet nguồn và native temporal samples trước khi pin 17 cặp SHA source/binding. Approval giới hạn ở source/clip. Hai HOLD gait NPC E/NE chuyển sang lịch sử sau khi thay nguồn; bốn ảnh native frame 3/15/27/39 tương ứng source 0/4/8/12 cho thấy hai tiếp xúc và pass/occlusion khác nhau. Chưa nhận AI escort/world footfall.
- .NET build: 0 warning, 0 error; Godot import xong. 52 Python tests; native Library 15.472 assertions; Studio 73.407 assertions/263 entries; ReactionReview 3.146 assertions. Chuỗi lấy mẫu 60 bước/s thăm đủ 16 source frame mỗi clip/hướng.
- 46 PNG baseline giữ SHA; 201 nguồn runtime đang được tham chiếu khớp byte. 187 source/binding ngoài bảy record thay có chủ đích giữ nguyên.
- Bảy MP4 chọn, hai MP4 cũ trong lịch sử. Sáu video chọn có 180 frame/3 s; chuỗi phản ứng 240 frame/4 s. Decode/hash audit không có chẩn đoán lỗi. Movie Maker xuất offline 60 bước/s, không chứng nhận gameplay chạy thực 60 FPS.

`visual_decisions.json`, `gait_contact_review.json`, `transition_geometry.json`, `previous_binding_integrity.json` và `offline_media_integrity.json` nêu rõ phạm vi. Inventory `batch_20261113e.json` chỉ tính nguồn chọn, không cộng mirror hoặc bản thử. CI kiểm lại export và inventory đợt này.

## Tình trạng toàn thư viện

204 page qua cấu trúc, gồm ba clip kế thừa. 64/1.008 job đủ góc nguồn; 32 job đủ góc đã kiểm source; còn 944 job thiếu. 19 HOLD còn lại và full VFX `sk_mk_03_vfx` sai số hàng vẫn chặn. Minh Kiếm có 12/12 clip đủ nguồn đã kiểm source; chưa nghiệm thu toàn class, mọi chuyển thế hoặc gameplay.

Tiếp tục các class khác, quái/boss/NPC, ghép body/VFX thành kỹ năng hoàn chỉnh, world renderer/AI/hit/collision/LowFX/PCK và thư viện map/UI/icon/audio/biến thể. `--require-complete` hiện phải thất bại; batch này không đóng mục tiêu toàn thư viện.
