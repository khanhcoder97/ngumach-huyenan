# Gameplay nhìn từ trên — đặc tả thay thế DEC-016

Ngày 2026-10-28, chủ dự án xác nhận game di chuyển nhìn từ trên. Tài liệu này thay các quy định side-scroll, nhảy/rơi và chiều cao collider cũ trong toàn bộ đặc tả. Đây là quy định cần triển khai; không phải tuyên bố engine/network đã đáp ứng.

## 1. Không gian và điều khiển

- Dùng camera orthographic cố định, artwork nhìn từ trên chếch để thấy mặt/thân nhân vật và mái nhà. Không xoay camera, không projection isometric. Tọa độ Unity XY chính là tọa độ server; +X Đông, +Y Bắc; Z dành render.
- 1 WU = 0,5 m; 20 source px/WU. Input vector trong [-1,1]; normalize khi độ dài >1 để đường chéo không nhanh hơn. Analog giữ độ lớn nhỏ hơn 1. Facing quantize 8 hướng, hướng cũ được giữ khi đứng yên.
- DirIndex: N=0, NE=1, E=2, SE=3, S=4, SW=5, W=6, NW=7. Click/aim dùng tọa độ mặt đất; không dùng đỉnh sprite làm điểm aim.
- Không có gravity/jump/rơi kiểu platformer. Né, đẩy lùi, lao và truy đuổi đều trên mặt phẳng XY; bật khỏi mặt đất chỉ là VFX/animation, không bỏ collision.
- Tốc độ runtime lấy cấu hình server đang version hóa. 3,2 WU/s trong scene Muse là tốc độ demo, không được dùng làm giá trị server mặc định. Client gửi ý định, server trả vị trí thực.
- WASD/mũi tên di chuyển; F tương tác; J/chuột trái đánh thường; 1–6 kỹ năng; Space hoặc Shift né; Q/E thuốc HP/MP; Tab đổi mục tiêu. Input UI/chat chiếm focus thì dừng phát input gameplay. Mobile joystick tự do và nút né, không nút nhảy.

## 2. Actor, collision và camera

- Hero cell 48×64 px = vùng vẽ 2,4×3,2 WU tối đa. Pivot (0,5;0) tại chân; không scale sprite lên chiều cao cũ 5 WU. Capsule footprint ngang 1,2×0,6 WU, offset (0;0,3), independent of hair/cape/weapon.
- Collider combat tách collider đi bộ và khai báo trong entity definition. NPC thường dùng cùng footprint hero cho blockout; mob/boss phải có footprint riêng và không suy ra từ bounds ảnh.
- P1 không chặn đường bằng actor khác; terrain chặn actor, combat vẫn dùng hit shapes. Hub không cho crowd/NPC cosmetic khóa lối đi. Vật cản mở rộng theo footprint khi kiểm tra đường; normalize và sweep trước khi cập nhật vị trí. Diagonal không xuyên góc hai tường.
- Renderer sorting theo foot Y giảm dần: actor ở phía Nam vẽ trước mắt camera; cùng Y dùng entity ID để tie-break ổn định. Cây/nhà tách chân và tán/mái. Khi mái che nhân vật điều khiển, thay mái bằng dither thưa và giữ outline; telegraph luôn đọc được. Không blend blur alpha phá pixel art.
- Camera 640×360 logical, vùng cơ sở 32×18 WU; integer scale, vị trí render snap 0,05 WU, simulation không snap. PvP dùng cùng vùng nhìn 32×18 WU cho mọi tỷ lệ, phần dư dành bars/HUD. PvE có thể mở ngang tối đa 40 WU. Camera clamp map, map nhỏ thì center và padding.
- Ground actor ở floorId OVERWORLD. Cầu vượt/tầng trong nhà dùng floorId khác và link có hai đầu; không tự di chuyển giữa tầng chỉ vì cùng XY. Khi chưa có floor contract, P1 chỉ dùng OVERWORLD và không làm cầu chồng đường.

## 3. Map và migration

- Giữ 46 map ID và bounds trong `Implementation/Content/map_bounds.json` để không làm hỏng API hiện hành. Bounds là giới hạn tổng thể, không chứng minh ô bên trong đi được. Bến Mưa tiếp tục spawn (18,0); Y âm là phía Nam, không đồng nghĩa chìm/rơi.
- Manifest 349 hàng hiện có giữ nguyên recordId/entityId/mapId/loot/quest refs. Đọc x,y như ground anchors tạm thời. Mọi hàng mang trạng thái TOPDOWN_REVIEW_REQUIRED ở hồ sơ migration đi kèm, kể cả trước đây ATLAS_ANCHOR. Không ghi đè CSV gốc bằng phép đổi trục hàng loạt.
- Những dòng platform y=4/8/12 là ground anchors kế thừa chờ layout, không tầng cao 4/8/12. Chuyển nền nổi thành đảo/bệ an toàn nối bằng đường/cầu; không yêu cầu nhảy. Khe vực/nước sâu là blocked polygon; qua cầu hoặc portal/floor link được duyệt.
- Bundle map v2 phải có `coordinateSystem=TOP_DOWN_XY`, `mapId`, `layoutVersion`, `bounds`, `floors`, `walkablePolygons`, `blockedPolygons`, `floorLinks`, `portals`, `placements`, `safeZones`, `cameraBounds`, `sourceRefs` và `reviewState`. Polygon gồm >=3 đỉnh hữu hạn, không tự cắt; mọi placement có floorId.
- Placement mới lưu originalRecordId, originalXY, newXY, floorId, lý do và reviewer; recordId runtime không đổi. Bản v1 còn phục vụ server thử nghiệm, v2 chỉ active khi client/server cùng hỗ trợ bundleVersion.
- Lối chính >=8 WU, đường phố Thăng Long >=10 WU, đường xe hàng >=14 WU; khoảng tương tác NPC <=5 WU đo từ chân, phải cùng tầng và đường không bị tường chặn. Bến spawn/portal có lối ra >=2 WU.
- Bố cục top-down của từng map phải có: tuyến chính từ spawn đến portal, nhánh phụ nối được, vòng boss có ít nhất hai vùng thoát, node không nằm trong footprint nhà/cây/nước blocked, điểm tuần tra trong nav polygon. Thuật toán đường đi phải trả lỗi reachable/unreachable rõ, không teleport khi kẹt.
- Thăng Long dùng các khu phố đã chốt nhưng bố trí ngõ Bắc–Nam nối trục Đông–Tây, quảng trường nhìn từ trên, khán đài quanh arena và lối spectator tách đấu sĩ. Safe-zone chặn damage vào khán giả. Bốn cửa theo compass hướng ra route đã mở; destination vẫn dùng canonical portal table, không tự thêm route.
- Cổng chỉ kích hoạt bằng F/tap và điều kiện server, không đổi map liên tục khi actor đi qua trigger. Arrival có 2s chống retrigger cổng; không ban bất tử combat.

## 4. Combat và đơn vị

- Tất cả range/radius/distance trên wire là WU; mô tả bằng mét nhân 2 đúng một lần khi export. SK-MK-01 2,2m => 4,4 WU; SK-MK-02 5,5m => 11 WU. JSON cũ 2,2/5,5 gắn `rangeWu` là lỗi export cần PR migration, không chỉnh lén client.
- SELF chỉ xác định actor nhận trạng thái, không có nghĩa phản công gây damage vào bản thân. CONE/DASH tính từ facing/aim XY, góc giữa vector hướng và vector đến target; range/line-of-sight cùng floor. Kiếm Trận chưa có range chính xác nên damage rollout giữ blocked cho tới khi config được chốt.
- Né theo vector input, nếu đứng yên dùng facing; sweep tránh xuyên tường, không tự đẩy đến vị trí bên kia. Telegraph circle/cone/line chiếu mặt đất, giữ đúng kích thước server, không co theo độ dài frame ảnh.
- Đòn thứ ba Mãng Cốt, bảng level/stat đầy đủ, rank skill và quy tắc multi-hit còn cần bảng numeric được version trước khi mở damage toàn bộ; endpoint hiện tại chỉ chứng minh gating, không chứng minh chiến đấu hoàn thiện.

## 5. Nghiệm thu và thứ tự thực hiện

1. Qoder bổ sung metadata đơn vị và migration range theo decision; server kiểm tra terrain/floor, sequence và diagonal.
2. Muse bàn giao Bến Mưa top-down blockout trước khi nhân rộng Thăng Long; sheet 8 hướng DEC-015 tiếp tục dùng. Dựng Unity trên máy ảo nếu khả dụng; log ghi exact commit, Editor version, command, output và video gameplay.
3. OpenCode chạy validator/preview nhẹ và inventory coverage trên máy local; không bắt cài Unity.
4. Hai client phải thấy cùng XY; đi 8 hướng có cùng tốc độ tối đa, không xuyên góc, không bay khỏi mặt đất; portal/interaction theo khoảng cách và floor; cây/mái không che telegraph. Kiểm camera 720p/1080p và PvP 16:9/20:9.
5. Mỗi map ký riêng gate topology/collision/placement. Sheet đủ hướng, compile thành công hoặc validator xanh không thay gate này.
