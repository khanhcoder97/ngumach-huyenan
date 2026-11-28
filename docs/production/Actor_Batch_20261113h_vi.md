# Asset 20261113h — phản ứng có đao của Ảnh Đao

10 sheet chọn /160 khung nguồn: trúng đòn và ngã, mỗi động tác có năm góc vẽ N/NE/E/SE/S ×16. SW/W/NW dùng lật theo policy và có nhãn; không cộng thành ba góc vẽ riêng. Giữ nhân vật chibi nguyên khối đã chốt, tóc đen/lọn cam đồng, áo ngắn đỏ rượu/than, đai vàng đất, quần tối/giày tím nâu, một đao cong ở tay phải. PNG do imagegen tích hợp tạo, giữ nguyên RGBA, không ghép paperdoll hoặc nhân ảnh để đủ khung.

## Hai chuyển động

| Clip | Nhịp trình bày | Nội dung |
|---|---|---|
| hurt | 0,30 s;16×18,75 ms | Một phản ứng lùi ngực/co gối, cực điểm quanh frame5, thả lực rồi trở về đứng; không có lần trúng thứ hai ở frame8 |
| death | 1,20 s;16×75 ms | Mất lực, khuỵu gối, chống tay trống, hạ thân xuống đất và nằm yên; frame8 tiếp tục ngã, không đứng lại; đao theo tay phải rồi nằm cạnh cẳng tay |

Nhịp giữ giá trị hiện hành của thư viện. Đây là trình bày nguồn, không cấp stun, damage, i-frame hoặc hồi sinh. Giữ frame15 của death ở chế độ một lần. Muốn cho nhân vật đứng dậy phải có trạng thái/clip riêng; không lặp ngã trong gameplay.

Góc N/NE ngã xa người xem, lưng/tóc sau vẫn hướng camera; E/SE ngã sang phải/chếch phải; S ngã về phía người xem, chân nằm sau đầu ở tư thế cuối. Mỗi góc có16 bản vẽ riêng, không quay một ảnh đứng bằng code. Choreography không phải phép đo góc chính xác hoặc bản thân logic chọn hướng của server.

## Điểm neo khi ngã

`SOURCE_FOOT_PIVOTS` lưu16 gốc trình bày của actor kèm chiều cao đứng cố định. Mỗi cặp phải hữu hạn, nằm trong ô gốc; chỉ dùng cho actor có `bodyReferenceHeight` và scale HEIGHT. VFX giữ hợp đồng `SOURCE_PIVOTS` riêng. Đổi gốc/nhịp làm đổi binding SHA và phải duyệt lại. Kiểm ô rỗng, mép/cắt và pixel trùng vẫn giữ.

`calibrate_anh_dao_reactions.py --apply` chỉ đọc PNG và ghi tọa độ vào `body_registration_20261113h.json` cùng record. Dùng khối đế giày tối đủ dày, giữ cả giày tối thiên tím lẫn nâu; viền thép mảnh không quyết định điểm neo. Khi nằm N/NE/E/SE, cửa sổ đọc chuyển về vùng giày phía sau/trái, tránh đầu và tay chống. Với S, giày nằm **phía trên tóc**; không lấy tóc/bàn tay thấp nhất làm chân.

Trong khoảng chân bị che, gốc trình bày được trace giữa hai mốc còn nhìn thấy trong hệ tọa độ bounds của từng tư thế: frame6–7 ở N/NE/E/SE, frame6–11 ở S. Đây là giả định gắn hình để xem native và chỉnh tay, không phải đo physics chính xác. Chỉ nội suy tọa độ neo; không nội suy/biến dạng ảnh nguồn hoặc tạo thêm pose. Chiều cao đứng cố định suốt clip, không phóng ảnh nằm bằng chiều cao ảnh đứng. Tọa độ/world root, collision và trạng thái chết của gameplay xử lý riêng.

## Công cụ kiểm chuyển tiếp

Phòng `ActorReactionReview` nhận `--reaction-actor CLASS_ANH_DAO`, vẫn hỗ trợ Minh Kiếm. Chuỗi Ảnh Đao: Tước Mạch0,68 → trúng0,30 → né0,48 → ngã1,20 → giữ nằm0,40 s; tổng3,06 s. Kiểm mọi hướng xem, nguyên16frame, ranh pha và giữ tư thế cuối. Vòng lặp của phòng kiểm chỉ để xem nối clip, không tạo hồi sinh hoặc i-frame.

Gốc hiển thị của Ảnh Đao chừa khoảng dưới cho tư thế S nằm về phía camera. Studio có `Fit khung` và `Fit clip`: nút thứ hai lấy vùng của tất cả source-frame trong clip. Khi mở bằng `--studio-play`, tự fit toàn clip trước khi phát, tránh fit ảnh đứng rồi cắt mất thân/người nằm ở các frame sau. Bounds fit gồm vùng ô nguồn và layer còn hiện; không sửa PNG. Bản JSON người dùng chỉnh vẫn cần kiểm riêng trước khi đưa vào gameplay.

```powershell
ClientGodot/Run_Actor_Library.ps1 -Actor CLASS_ANH_DAO -Clip hurt
ClientGodot/Run_Actor_Library.ps1 -Actor CLASS_ANH_DAO -Clip death
ClientGodot/Run_Actor_Library.ps1 -ReactionReview -Actor CLASS_ANH_DAO
ClientGodot/Run_Art_Studio.ps1 -Entry class_anh_dao_death_s -Play
Tools/ArtProduction/review_actor_batch_20261113h.ps1 -Resume
```

## Thay nguồn cũ

Hai atlas80frame cũ hurt/death và bản sửa death SE không cầm đao chuyển vào lịch sử record. PNG/prompt cũ vẫn giữ nguyên; chúng không bị xóa, cắt hoặc ghi đè. Hurt cũ có nghi vấn hai phản ứng8frame; death atlas có đoạn SE khởi động lại khi sang hàng thứ hai, bản SE sửa trước đây vẫn không khớp tay cầm đao. Năm nguồn mới mỗi clip thay lựa chọn runtime. Hai HOLD chỉ được chuyển lịch sử sau khi đủ năm góc mới đã xem source/native; không dùng thay nguồn như cách tự duyệt chất lượng.

Nguồn mới nằm trong `Art_Source/Actor_Library_20261107/Sheets/`, prompt thực trong `Prompts/`; inventory `batch_20261113h.json`; evidence `Implementation/Reports/Evidence/Actor_Batch_20261113h/`. Video Movie Maker là xuất offline60 bước/s để soi chuyển động, không chứng nhận gameplay60FPS. Nguồn/clip được duyệt không đồng nghĩa toàn class, thế rút/tra đao, skill assembly hoặc gameplay đã hoàn thiện. Các class/quái/boss/NPC còn thiếu, VFX, biến thể, map, UI, icon và âm thanh tiếp tục sản xuất.

Kết quả:69 Python tests đạt, build0 warning/error và import. Native Library17.464 assertions, Studio82.239/323 entries. Phòng nối phản ứng: Ảnh Đao3.034 assertions, Minh Kiếm3.146.10video chọn decode sạch, chín video180frame/3s và chuỗi phản ứng240frame/4s; không có video bị thay sau capture.10source pin mới sau xem toàn sheet/native,205pin trước giữ nguyên; tổng215.247page cũ giữ source/binding, ba page chưa được duyệt chuyển lịch sử.46 PNG baseline nguyên SHA và254 nguồn đang tham chiếu runtime khớp byte; các PNG runtime cũ vẫn được lưu.

Hai HOLD hurt/death cũ đã chuyển vào `historicalHolds` cùng nguồn thay, SHA và evidence;18hồ sơ HOLD còn lại,17source HOLD nằm trong catalogue và một full VFX Kiếm Trận vẫn bị từ chối do5hàng thay vì4. Catalogue257page qua cấu trúc,71/1008job đủ nguồn,41job đủ nguồn đã kiểm source;937job còn thiếu. Số job cấu trúc không tăng vì đây là thay hai clip đã có nguồn nhưng chưa đạt chất lượng. Ảnh Đao9/12action đủ góc đã kiểm source; idle/walk/basic cũ và thế chưa rút/rút đao vẫn cần sản xuất/duyệt. Không đóng mục tiêu toàn thư viện.
