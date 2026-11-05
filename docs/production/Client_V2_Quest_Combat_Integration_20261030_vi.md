# Client v2 — tương tác, trả nhiệm vụ và tick combat

Codex · 2026-10-30 · tiếp tục PR51. v1 vẫn là mặc định, v2 **opt-in** bằng `Client/Assets/Resources/client-config.json: onlineV2Enabled=true`; server cũng phải bật đúng profile DEV. Nếu dùng cổng15085 như bài test, đặt apiBaseUrl=http://127.0.0.1:15085 và healthUrl=http://127.0.0.1:15085/health; hai giá trị mặc định5000 không tự đổi theo mode. Không tự fallback sang v1 rồi giả có quái/damage khi route v2 chưa mở. PR51 vẫn draft đến khi có Unity evidence.

## Phần đã viết

- Vào phiên qua endpoint v1 hiện hữu, sau đó đọc `GET /p1/v2/world/{sessionId}`. Kiểm required fields, identity, instance/floor/phase, HP/state/targetable và duplicate entity trước khi thay snapshot; NPC/node HP0 là INVULNERABLE, không bị coi là quái chết. Client không đổ349placements vào scene để bù world snapshot rỗng.
- Move giữ cùng lane/sequence với combat; route move v1 không được xóa entity projection v2. Nếu refresh v2 lỗi, giữ snapshot v2 cuối và yêu cầu đồng bộ.
- `POST /p1/v2/combat` gửi BASIC_ATTACK hoặc SKILL theo schema2. ACK chỉ tạo presentation event đã xảy ra; HP/MP/vị trí hiển thị lấy từ snapshot mới. `nextInputSequence` là last accepted sequence theo server/self-check hiện hành, map nội bộ thành `acceptedInputSequence`; lệnh kế tiếp dùng số lớn hơn. Không tự sửa giá trị wire.
- `GET /p1/v2/events/{sessionId}?cursor&max=100`: validate nguyên page trước apply, dedupe CAST_START xuất hiện cả ACK và poll, monotonic cursor, đúng instance/floor. Resync lấy snapshot thành công rồi bỏ lịch sử presentation một cách im lặng; snapshot lỗi không advance cursor qua phần bị mất. Command ACK không tự advance polling cursor làm mất event xen giữa.
- `POST /p1/world/interact`: giữ nguyên body/key khi mất response; quest counters chỉ từ `questUpdates` đã xác thực. Node availability thuộc snapshot per-caller; không tiêu node riêng của người khác bằng trạng thái client.
- `POST /p1/quests/turnin` (không có dấu gạch giữa turn và in): xác thực quest receipt và đồng bộ world/inventory. Không tự tạo item instance, cộng20Đồng hoặc áp EXP từ tên reward. `xp.applied=false` được giữ và hiển thị rõ. Nếu receipt đã commit nhưng đọc túi lỗi, UI báo thưởng đã ghi nhận/cần đồng bộ; không tạo grant mới.
- Mutation không rõ kết quả khóa input mới, giữ requestId/idempotency/body/sequence; response sai request/session/quest/cast không xóa pending. Inventory_full giữ READY và không grant local.

## UI/input đã nối ở source

HUD giữ6ô vòng cung DEC-019. Bản v2 hiện mở đánh thường và Kiếm Trận (MK03) có tick effects được kiểm; Phản Quang/đột kích giữ khóa với lý do chưa khả dụng cho đến khi mechanics được tích hợp, không dùng CAST_START để giả guard/counter/dash. API core vẫn hỗ trợ gửi cast subset để test contracts, không chứng nhận mechanics tương ứng đã có.

Space/nút đánh gửi basic; Tab/nút đổi mục tiêu chỉ chọn MOB/BOSS sống và targetable. E/nút tương tác lấy node/interactable AVAILABLE gần nhất trong5WU; server kiểm lại khoảng cách/quyền. F/nút nhật ký nhận P00-01 tại Ly An hoặc trả tại Tạ Vân Khanh tùy state server. NPC IDs lấy QuestDefinition P00-01 đã có; chưa đoán NPC cho quest chưa có executable record.

Journal/túi có receipt state và EXP-unapplied, target có HP thực. Modal/editor/focus/pause vẫn chặn gameplay; phải thả cả1–3/F/E/Space/Tab/touch/mouse trước điều khiển lại. Server không pause khi mở panel. UI/presenter/transport Unity chưa được Editor compile hoặc test touch/font/safe area; syntax parse không thay các gate đó.

## Cách chạy kiểm tra

```text
dotnet run --project Client/Tests/P1CoreChecks/P1CoreChecks.csproj -c Release
dotnet run --project Client/Tests/UnitySyntaxCheck/UnitySyntaxCheck.csproj -c Release
dotnet run --project Client/Tests/P1CoreChecks/P1CoreChecks.csproj -c Release -- --http-v2-default http://127.0.0.1:15084
dotnet run --project Client/Tests/P1CoreChecks/P1CoreChecks.csproj -c Release -- --http-v2-dev http://127.0.0.1:15085
dotnet run --project Client/Tests/P1CoreChecks/P1CoreChecks.csproj -c Release -- --http-v2-tick http://127.0.0.1:15085
```

`--http-v2-dev` là compatibility với dependency accept-only d1ce792. `--http-v2-tick` thêm kiểm server impact/death/MK03 và replay sau END; phải dùng bản sửa replay, không dùng head32d57bcc chưa sửa. CI pin immutable server SHA để không đổi bằng chứng khi agent cập nhật nhánh. Dependency hiện pin514c3f20 (server fix PR76, basePR75); đây là dependency review chưa tự thành main.

Hai client đi bằng move intent, cùng nhặt đủ ba kiện theo quyền riêng, trả nhiệm vụ, làm mất response sau server commit rồi retry; kiểm mỗi người đúng20Đồng/1áo. Tick test đi tới quái, gửi basic/MK03, đọc hitIndex0/1/2 và HP từ server, đợi END rồi replay body cũ, kiểm không damage/event mới, đánh đến death đúng một lần. Không teleport hoặc tự set quest/damage để làm xanh test.

Report source/binary fingerprints và kết quả tại `Implementation/Reports/Client_V2_Integration_20261030.json`. Các checks cũ vẫn chạy để phát hiện regression v1/audio/input. Syntax checker dùng Roslyn của SDK, parse C#9 với ba symbol profiles, không import Unity assemblies.

## Chưa phải P1 online hoàn chỉnh

Mới chứng minh P00-01 + shared world interact + basic/MK03 và mob death trong DEV synthetic topology/in-memory. Chưa P00-02..05/boss/portal/equip/durable save/auth/relogin; chưa hiển thị avatar người chơi khác vì wire v2 hiện chưa có PLAYER kind; không gọi hai HTTP session là multiplayer presentation hoàn chỉnh. Chưa group spawn đúng manifest, guild/PvP/46map/5class/fullVFX/cinema.

Client không chữa lỗi server bằng cách giấu impact trùng theo castId: report trước sửa đã tái hiện duplicate END khi replay32d57bcc. Server fix giữ idempotency qua receipt replay, atomize command cache+costs và cancel source chết/đổi map/floor. Cần review/merge stack theo thứ tự, rồi Muse chạy exact client SHA trên Unity VM; production gates tiếp tục BLOCKED khi các bằng chứng đó chưa có.
