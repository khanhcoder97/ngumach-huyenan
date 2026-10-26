# OpenCode — Unity Client và Gameplay Runtime

## Phạm vi sở hữu

Bạn sở hữu runtime Unity và chỉ sửa các khu vực:

- `Client/Assets/Scripts/`
- `Client/Assets/Prefabs/`
- `Client/Assets/Scenes/`
- `Client/Assets/UI/UXML/`
- `Client/Assets/UI/USS/`
- `Client/Assets/Resources/` (trừ art assets)
- `Client/Assets/Tests/`

Không sửa art PNG, Tilemap art, Animation art, VFX art, server, canonical content/schema hoặc production docs.

## Mục tiêu P1

Tạo vertical slice client có thể mở một scene thử nghiệm, kết nối API local, tạo session, di chuyển nhân vật, nhận snapshot và hiển thị HUD bằng asset placeholder hoặc asset Muse đã bàn giao.

## Backlog ưu tiên

### OPC-01: Runtime foundation

1. Tạo scene `Bootstrap` và `P1_LangMoi` additive hoặc load flow rõ ràng.
2. Giữ `PixelArtCameraBootstrap` đang có; camera orthographic phải pixel-snap và không tạo texture filtering sai chuẩn.
3. Tạo `GameBootstrap`, `ClientConfig`, `ServiceLocator` tối giản; không dùng package ngoài nếu không cần.
4. Tạo `NetworkApiClient` cho `POST /p1/sessions`, `POST /p1/move`, `GET /p1/world/{sessionId}`. Base URL lấy từ `client-config.json`.

### OPC-02: Điều khiển và di chuyển

1. `PlayerInputController`: WASD/mũi tên; kiến trúc sẵn cho mobile joystick, chưa cần asset joystick cuối.
2. `PlayerPresentation`: đọc `WorldSnapshot`, nội suy hợp lý, giữ render trong pixel grid.
3. Gửi move intent theo sequence tăng dần; không để client tự quyết trạng thái cuối.
4. Hiển thị trạng thái lỗi server, map id, tọa độ và ping/dev overlay.
5. Dựng một `P1_LangMoi` Tilemap bằng placeholder an toàn; khi Muse giao assets, chỉ cần thay Tile Palette/tile assets.

### OPC-03: Combat presentation prototype

1. Input thường: target gần nhất, attack/cast theo state machine cục bộ để trình diễn.
2. State, cooldown, hit flash, VFX spawn đọc từ animation manifest Muse.
3. Tách interface combat transport để Qoder tích hợp combat authoritative ở đợt sau.
4. Không khóa logic damage/economy ở client.

### OPC-04: UI logic

1. Chuyển title từ “Sắp ra mắt” sang Start chỉ khi session creation thành công.
2. HUD gameplay: HP/MP, name/level, EXP, skill hotbar, quest tracker, minimap shell, inventory/equipment shell.
3. Inventory, forge, compendium, appearance, settings mở/đóng bằng panel controller và dữ liệu mock rõ ràng.
4. Chỉ dùng texture Muse hoặc placeholders gắn nhãn; không tự tạo final pixel art bằng code/CSS.

## Bàn giao

- `Client/README_P1.md`: cách mở scene, cấu hình API và chạy manual test.
- Danh sách prefab/component public để Muse gắn assets, tại `Client/Assets/ArtManifests/opencode_asset_requests.json`.
- Không sửa endpoint contract; yêu cầu thay đổi gửi vào `Implementation/Work_Orders/Integration_Notes.md`.
