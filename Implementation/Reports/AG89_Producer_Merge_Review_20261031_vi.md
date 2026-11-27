# Review và merge AG-02 theo yêu cầu chủ dự án

Đầu vào Antigravity: PR89, head99e7998d2f0708c11efeb7e197ccf54141004124, base AG-01/PR83. Chủ dự án yêu cầu rõ “review bàn giao và merge #89”; merge lần này nhận checkpoint code vào đúng base, không xác nhận toàn epic đã hoàn tất hoặc tự merge #83/#51 vào main.

## Đã đối chiếu

Head bàn giao có9/9CI SUCCESS. Producer runner nguyên bản chạy91author tests và13ca hồi quy, tổng104/104PASS. Đã đọc diff17files từ94fb605, report work order17, composition/root/panels, tracker, map projection và scripted journey.

Document được truyền tới các panel thay cho global FindFirst; panel có Teardown, NPC Hide gọi Clear; tracker có consumer thật. Map bounds hardcoded hiện khớp map_bounds.json: default360×84, Thăng Long900×108. Đây là bounds hiện hành của runtime, không phủ nhận quy hoạch kinh thành lớn đang chờ migration. Không sửa XY hoặc tự phê duyệt topology.

## Sửa trước merge

Factory vẫn tính targetDoc rồi bỏ, khiến caller khởi tạo root không truyền lại document có thể gắn sai host. Bổ sung BindDocument, giữ document đã inject qua Initialize/rebind, từ chối đổi document khi phiên đang mở và báo lỗi sớm nếu không có document. Chạy lại factory vẫn dùng cùng root.

Callback nối QuestJournalPresenter với HUD tracker trước đây là lambda không tháo ở Close. Chuyển thành callback có tên, tháo trước teardown và đồng bộ tracker ngay sau khởi tạo để không giữ pin của phiên trước. Không sửa Core/transport/server/narrative v3 hoặc art.

## Giới hạn của nghiệm thu

- Test200cycles của tác giả chạy presenter/router, không dựng VisualElement hoặc Unity tree thật. Không chứng minh không rò UI/native.
- Scripted journey dùng P1Client/P1ClientAdapter thật nhưng trả response giả từ IP1Transport; chưa là HTTP. Fixture trả weapon/100CUR_GOLD, không phải phần thưởngP00-01 live (20COIN+chest). Giữ đúng nhãn synthetic, không chuyển các giá trị ấy vào game.
- NpcDialoguePresenter cũ còn gọi InteractAsync với NPC trong khi endpoint hiện tại chỉ nhận parcel/node. PR96 đã có đường narrative đọc snapshots và command thật; khi ghép AG-02 mới vào96 phải giữ đường đó. Không lấy scripted route thành bằng chứng endpoint NPC đã có.
- CinemaOverlay vẫn tự đọc Space/Escape; media chỉ preview/fallback. Pan/camera rectangle/waypoint, exact catalog đầy đủ, accessibility/text-size/settings và native safe-area còn việc. Các report tự xưng hoàn tất A→E không được dùng để đóng toàn bộ80/85.
- Native Unity6000.3.17f1 import/type/playmode/layout chưa có bằng chứng từ Muse VM. User đã yêu cầu merge checkpoint; giữ native UNVERIFIED và epic mở, không xin lại quyền merge.

Kết quả các lần chạy sau sửa, SHA được merge và việc ghép vàoPR96 sẽ ghi tại review/commentPR89. Không đụng checkout rootQoder hoặc dữ liệu chưa commit của người dùng.
