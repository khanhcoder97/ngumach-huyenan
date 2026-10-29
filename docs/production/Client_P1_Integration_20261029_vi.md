# Client online P1 — đợt triển khai đầu của Codex

Đợt audio tiếp theo: xem [Client_Audio_Integration_P1_vi.md](Client_Audio_Integration_P1_vi.md). Đã viết mixer/policy/Unity bridge và mapping UI/accept; chưa có Unity compile/playback evidence, PR vẫn draft.

## Phần đã viết

- Nút vào bản online từ title; config `apiBaseUrl`/timeout, HTTP transport UnityWebRequest, không follow redirect mang session header.
- Core C# không phụ thuộc Unity: create session, world/quest/inventory read, move, quest accept, ba skill Minh Kiếm hiện có. Serialize một lane để move/combat dùng chung sequence, không queue movement cũ sau timeout.
- State Disconnected/Connecting/Ready/NeedsResync/UncertainMutation/Expired; snapshot thấp revision không ghi đè mới. Command fail không tự trừ MP, không tự thưởng hay tiến triển quest.
- Move không tự retry sau mất phản hồi; đọc world rồi gửi sequence mới. Quest/cast không rõ kết quả giữ nguyên body/requestId/idempotencyKey để retry; readback không âm thầm bỏ pending. Không tạo session mới để né pending. Session hết hạn xóa cache.
- HUD chức năng, sáu ô theo góc200/174/148/122/96/70 quanh nút đánh; slot4–6 và đánh thường chưa có API nên disabled có lý do. Cooldown lấy timestamp đã được server xác nhận; không bake CD vào icon. World camera không scale HUD.
- Joystick dạng8phím giữ/nhả và WASD/arrow; input tạm dừng khi panel đang mở/command pending. UI đọc quest counters dạng dictionary và inventory từ server. Copy tiếng Việt tập trung trong Resources/Localization/p1_vi.json, chưa là localization toàn game.
- Presenter nối actor duy nhất trong scene bằng cách tạm tắt controller/animator driver local; không sửa prefab/Animator/builder/asset Muse. Khi không có đúng1actor, dùng proxy hình chữ nhật có tên PLACEHOLDER. Thoát khôi phục component/pose/camera. Proxy không được tính là art production.

## Cách tích hợp trên máy Unity

1. Kéo main/branch đã review và LFS. Mở `Client` bằng Editor version trong ProjectVersion.txt; resolve package Json.NET chính thức. Không import DLL NuGet thủ công.
2. Chạy server localhost theo README của Server/Health. Giữ flag quest OFF để kiểm default; bật dev flag riêng chỉ theo hướng dẫn server, không sửa reviewed topology để giả production gate.
3. Chỉnh config origin API nếu server ở máy khác; trên Android127.0.0.1 là điện thoại, không phải PC. Hosting/auth/Android cleartext/network-security policy chưa được gói này thiết lập.
4. Play và chọn vào online. Kiểm HP/MP/XY bằng world endpoint; thử chặn mạng rồi đồng bộ; nhận nhiệm vụ khi endpoint OFF phải báo chưa mở (404 hoặc405 do route GET /quests/{sessionId} chồng đoạn “accept”). Với dev profile được bật, tới gần Ly An rồi thử nhận, không gọi từ xa thành success.
5. Gửi log exact SHA/Editor/package resolution, video di chuyển/thoát/nhập lại và screenshot720p/1080p/20:9. Không nâng trạng thái engine-imported trước bằng chứng.

## Giới hạn tích hợp thật

WorldSnapshotFactory ở baseline `0f78707` vẫn trả `entities=[]`: server registry chưa được chiếu vào snapshot. Client không dựng quái/NPC bằng cách suy đoán từ349placement; Tầm Long/Kiếm Trận không có target từ snapshot thì disabled. HP/damage, objective collection/turn-in, teleport, authentication/durable save và30skill đầy đủ vẫn phụ thuộc Qoder/mốc sau.

Đây là đường client P1 dùng HTTP polling/snapshot; chưa có interpolation/prediction/real-time transport hoặc reconnect durable120s. Mất phiên cần explicit tạo phiên mới; không hiển thị “đã phục hồi nhân vật” từ local cache. `combat.effect` chưa là hit/counter/status lifecycle, nên không trigger VFX counter mỗi lần cast.

HUD hiện là controls thay thế để thử luồng mạng, chưa phải pixel skin/font final. Chưa có minimap art, skill icon/cooldown radial, bag/equipment interactions, camera HUB_WIDE/map-mode transition hoặc map streaming. Không suy camera wide từ map name khi chưa có mode policy. Cần Muse skin và Codex UX/device QA tiếp.

## Kiểm tra

Core+HTTP suite/CI ở `Client/Tests/P1CoreChecks`; Unity-specific source chưa compile trong môi trường local không có Unity/.NET. Kết quả CI phải đọc theo exact head; không dùng pass của server để chứng nhận client Unity. Các ca lỗi quan trọng kiểm bằng fake transport nhưng chạy code thật, không chỉ đối chiếu text implementation.
