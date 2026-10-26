# Qoder — Authoritative Server, Gameplay Systems và Content Integration

## Phạm vi sở hữu

Bạn sở hữu backend, contract implementation, validation and data loading:

- `Server/`
- `Implementation/Contracts/`
- `Implementation/Tools/`
- `Implementation/Reports/`
- `Implementation/Content/Runtime/` (tạo mới nếu cần)

Không sửa Unity client, art assets, tilemap, animation, VFX, UI art hoặc production docs.

## Mục tiêu P1

Xây dựng authoritative server slice đủ để client tạo session, di chuyển an toàn trong map canonical và lấy snapshot. Tạo nền tảng mở rộng cho combat, quest và inventory mà không thêm phụ thuộc hạ tầng nặng.

## Backlog ưu tiên

### QOD-01: Session và movement authoritative

1. Giữ `GET /health` và correlation-ID middleware hiện có.
2. `POST /p1/sessions`: tạo server session, player state, spawn hợp lệ trong `MAP_LANG_MOI`.
3. `POST /p1/move`: kiểm tra session, sequence, map, movement distance/tick và map bounds; clamp/reject có mã lỗi rõ ràng.
4. `GET /p1/world/{sessionId}`: trả `WorldSnapshot` authoritative mới nhất.
5. Load map bounds từ `Implementation/Content/map_bounds.json`, không hard-code toàn bộ bounds.
6. In-memory store cho P1; tạo interface repository để thay persistence sau này.

### QOD-02: Contract và lỗi chuẩn

1. Dùng Envelope/MoveIntent/WorldSnapshot schemas hiện có làm nguồn hợp đồng.
2. Thêm DTO mapping rõ ràng, validation độc lập và error codes: `session_not_found`, `stale_sequence`, `invalid_map`, `movement_too_far`, `invalid_payload`.
3. Mọi response, cả lỗi, có `X-Correlation-ID`.
4. Không làm client tin vào damage, inventory amount, currency hay quest state.

### QOD-03: Gameplay service skeleton

Tạo service interface và in-memory implementation, chưa mở endpoint khi contract chưa sẵn:

- `ICombatService`: target validation, cooldown gate, combat event emission.
- `IQuestService`: quest state transition theo canonical quest ID.
- `IInventoryService`: snapshot read-only, add/remove transactional abstraction.
- `ITeleportService`: validate destination/map/condition.

Không tự đặt thông số cân bằng khác với canonical content.

### QOD-04: Chất lượng và bàn giao

1. Cập nhật `Server/Health/README.md`: run/build, curl create session, move hợp lệ, stale sequence, snapshot.
2. Thêm tests không cần database/package mới nếu môi trường cho phép; nếu không, ghi manual verification table.
3. Chạy `python Implementation/Tools/validate_contracts.py` và `python Implementation/Tools/validate_content.py`; lưu report mới nếu thay đổi input validation.
4. Báo rõ file đã sửa, endpoint, contract example và điều kiện cần để OpenCode tích hợp.

## Không làm trong P1

- Database production, Redis, authentication, payment, WebSocket production, shard, matchmaking, PvP ranking hoặc economy live.
- Thay đổi artwork và Unity scene/prefab.
