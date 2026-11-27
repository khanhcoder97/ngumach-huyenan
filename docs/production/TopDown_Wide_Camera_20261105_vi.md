# CAM-TOPDOWN-WIDE-20261105 — góc nhìn từ trên và bao quát map

Lệnh trực tiếp của chủ dự án ngày05/11/2026: sửa góc nhìn lẫn map thành nhìn từ trên xuống, mở rộng vùng nhìn hơn nữa. Quyết định này thay mọi default640×360/32×18WU và giới hạn chỉ hub48×27WU trong các tài liệu cũ. Không thay engine: Godot4.7.2.NET, renderer Compatibility.

## Camera và tỷ lệ

| Thuộc tính | Giá trị hiện hành |
|---|---|
| Phép chiếu | 2D orthographic, north-up, camera không xoay hoặc có phối cảnh |
| Hướng vẽ kiến trúc | Gần nhìn thẳng từ trên: mục tiêu80–85° so với mặt đất; mái chiếm ưu thế, tường là dải ngắn |
| Vùng thế giới mặc định | **64×36WU**, gấp2 chiều ngang/dọc, gấp4 diện tích so với32×18WU |
| Viewport thế giới | 1280×720 nội bộ,20pixel/WU, Camera2D.Zoom=(1,1) |
| Tùy chọn người chơi | Gọn48×27WU; không tự ép map thường về32×18WU |
| Tỷ lệ khung | 16:9 cố định; letterbox/pillarbox, không kéo giãn và không lộ thêm bản đồ theo màn ultrawide |
| HUD | CanvasLayer riêng; giữ cỡ chữ/hit target, không scale theo camera world |
| Pixel | nearest, không mipmap; scale nguyên khi cửa sổ đủ lớn; kiểm riêng thiết bị nhỏ |
| Biên map | Clamp tâm theo nửa kích thước vùng nhìn; map bé hơn viewport thì căn giữa/padding, không tự zoom sát |

Góc80–85° là hướng vẽ của asset2D, không gán Rotation80° cho Camera2D. Nhân vật vẫn cần8hướng dễ đọc, tỷ lệ chibi và chân neo chính xác; không biến body thành dấu chấm. Mục tiêu hình nhân vật chính chiếm khoảng4–6% chiều cao world viewport ở preset rộng; chọn/định vị bằng vòng chân và tên có giới hạn mật độ.

Không thay PPU/collision để giả camera xa. Simulation/world coordinates giữ số thực, chỉ snap phần render vào pixel. Camera follows không smoothing phân số gây shimmer. Cấu hình máy đọc ở camera_topdown_wide_20261105.json; implementation đầu ở ClientGodot/scripts/TopDownCamera.cs.

## Map phải được dựng lại theo góc nhìn

1. Mái nhà nhìn được cả chiều sâu; không dùng mặt tiền chiếm nửa sprite rồi chỉ thu nhỏ camera. Nhà/cây/cầu/bến/đá cần cùng phép chiếu, cùng mật độ chi tiết và hướng sáng.
2. Bản vẽ Bến Mưa topdown_wide_v2 là **một khu phố nhìn thấy**, không là toàn bộ map. Không crop concept làm nền runtime hoặc đo tọa độ từ ảnh.
3. Thăng Long vẫn theo quy hoạch2048×1536WU/12phường của DEC-020. Tăng tầm nhìn không thu thành xuống kích thước màn hình. Streaming/culling theo chunk; không nạp cả thành làm một PNG.
4. Map mới giữ khu chức năng/đường đi/điểm mốc nhìn được từ trên, các tuyến dài vượt khung nhìn và các đường nối xuyên chunk. Giao điểm/chợ/bến tạo landmark để đọc phương hướng.
5. Không dịch NPC/portal/quái/node hoặc sửa nav chỉ vì thay hình. Mọi migration geometry/canonical placements phải bàn giao bundle đồng bộ và hash, giữ quyết định306ô nước/37ô bờ hiện hành.
6. Tán cây/mái che không được giấu toàn bộ nhân vật. Production cần occlusion/fade chỉ phần che và giữ dấu chân/quest marker; staging hiện chưa có fade, không coi là nghiệm thu đầy đủ.
7. Vùng nhìn rộng làm nhiều actor/VFX xuất hiện hơn: cull ngoài frustum, giới hạn decorative/weather trước; đo trên máy thật. Không báo mục tiêu30FPS là kết quả đã đạt.

## Gameplay và tính công bằng

64×36WU là default thế giới mới, gồm hub và field. Bản staging chỉ đổi camera, không đổi server AOI, reveal, interaction/attack ranges, aggro hay grants. Client chỉ vẽ entity được server cấp. Competitive instance phải dùng một profile thống nhất64×36WU cho mọi người, không dùng màn rộng để tăng vùng thấy; việc chuyển profile từ server cần tích hợp khi online client sẵn sàng. Không tự nới AOI từ32 lên64 bằng client-only patch.

## Bản thực thi đầu và cửa nghiệm thu

Scene ClientGodot/Preview.tscn dùng TileMapLayer, sprite độc lập, footprint và camera clamp. Map ART_BM_STAGING_A1 rộng128×96WU dùng để thử, **không** thayMAP_BEN_MUA canonical. F2 đổi Rộng/Gọn; H ẩn HUD. HUD6ô skill vòng cung là bố cục sống, chưa có combat binding.

Các kiểm tra cần tách rõ: cấu trúc ảnh/atlas, camera bounds và táchHUD có test; render native cần ảnh chụp thật; collision/8hướng và khả năng đọc phải xem ở kích thước chơi; server AOI/PvP/chunk streaming/crowd vẫn là việc tích hợp tiếp. Không gọi scene art staging là game online hoàn chỉnh.
