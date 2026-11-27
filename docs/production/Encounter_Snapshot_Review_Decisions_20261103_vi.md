# Duyệt hợp đồng encounter alpha — 03/11/2026

Phạm vi: phản hồi packet QOD-21 tại PR #106, head `3ed4ef6c7b5e5686dd96543c2ac270c3c028091a`. **Duyệt hướng triển khai, kèm các sửa bắt buộc dưới đây; chưa duyệt merge runtime hiện tại.** Nguồn gameplay vẫn là DESIGN-BM-ALPHA-20261103, không mở party hoặc production gate.

## Trả lời ba câu hỏi

1. `encounterId` opaque, server cấp theo `(characterId, questAttemptId)` và giữ qua wipe. Mỗi lần đánh lại có `bossLifeId`/generation mới; kết thúc hoặc bỏ quest attempt không tái dùng encounter ID cũ. Ràng buộc quyền bằng identity phía server, không tin characterId client gửi.
2. **Không late join, không nhận credit nhờ vào muộn.** Một owner đăng ký lúc mở; reconnect của cùng character đã xác thực được khôi phục đăng ký cũ, không phải late join. Packet §6.2 đề xuất nhận credit ở life hiện tại bị bác vì trái nguồn đã duyệt.
3. Owner-only, danh sách registeredCharacterIds đúng một phần tử. Chưa có party reader/scaling. Session khác của chủ thể khác nhận 404 `encounter_not_found`; không tiết lộ tồn tại. Chưa cần enum `character_not_registered` lộ qua endpoint này.

## Wire được phép triển khai

- `GET /p1/encounters/{encounterId}` và **`GET /p1/encounters/current`** để owner tìm encounter đang hoạt động mà không đoán opaque ID. Endpoint current trả cùng snapshot khi có, 404 khi không có; route literal phải được chọn đúng, không bị validator ID bắt nhầm. Cả hai dùng `X-Session-ID` theo P1 hiện hành, không tạo cơ chế auth mới; session này chưa được quảng cáo là account authentication production.
- Schema `EncounterSnapshotV1`, additionalProperties:false ở mọi object; giữ các field nguồn trong packet và bổ sung field rõ nghĩa bên dưới. Qoder commit schema, DTO, fixtures, contract validator và HTTP examples cùng một checkpoint; consumer chỉ bind version được duyệt. HTTP status/error envelope theo P1; tên lỗi mới nếu có phải vào enum/example/validator, không tự tạo tùy ý.
- Gate alpha OFF: không map route mới, GET URL này thường trả **404**, không mặc định 405. 405 chỉ dành cho method mismatch trên route đã map. Test kết quả pipeline thật; không sửa middleware để ép khớp một dự đoán sai trong packet.
- Snapshot bất biến được copy trong cùng lock/tick của encounter. HP, phase, life, revision, activeMove và deadline phải thuộc cùng generation, không ghép các field đọc ngoài lock. `bossRevision` tăng khi snapshot state đổi; không dùng cache toàn cục có thể trả data owner khác.

### Bổ sung cần cho render Godot

`activeMove` khi có gồm thêm `castId` opaque ổn định suốt một lần tung đòn, `stateEndsAtTick` integer >= serverTick cho trạng thái đang chạy, và `shape.facingX`, `shape.facingY` cho cone. Vector hướng phải finite, normalized trong tolerance validator; snapshot aim được khóa từ telegraph. `angleDegrees` chỉ độ rộng cone, không thay vector hướng. Các hình circle/annulus không được consumer suy ra hướng từ vị trí owner hiện tại.

Shape validate theo loại: cone có góc/phạm vi/hướng hợp lệ; circle có radius > 0; annulus có 0 <= innerRadius < outerRadius. Dùng schema discriminated union hoặc semantic validation tương đương với fixture âm tính. Các giá trị không áp dụng phải theo một quy tắc null/omitted thống nhất đã khai báo, không nhét số tùy tiện. `ticksRemaining` nếu giữ phải khớp deadline và serverTick. `castId` cộng life/generation dùng để không phát lại VFX khi poll; không thêm type vào CombatEventV2. Client không được lấy thời gian máy hoặc animation callback để quyết định damage/credit.

HP 1200 và hình học của alpha được kiểm trong validator/profile alpha, **không hard-code 1200 vào schema tổng quát** khiến boss khác không dùng được. Arena/safepads/NPC phải có bounds/finite checks; chỉ active phase-3 mới áp dụng safepad và không tạo bất tử. Danh tính Tạ và Trial NPC phải khớp quest source, không chỉ chuỗi tên hiển thị.

## Sửa runtime trước nghiệm thu

1. `AlphaBossEncounterService` hiện có per-owner dictionary nhưng gọi `DespawnBoss()`/`ForceRespawn()` lên một world entity chung. Owner A wipe/end/defeat có thể làm biến đổi entity/life của B. Chuyển encounter actor/life và wave actor sang owner/quest-attempt instance thật; cùng record template không đồng nghĩa dùng chung entity mutable. World event boss không được despawn toàn thế giới chỉ vì một quest instance mở. World snapshot, targeting, damage và credit đều phải lọc instance.
2. `AlphaEscortService.ObserveWave` hiện nhìn trạng thái dead của shared members rồi tăng credit, chưa chứng minh death thuộc owner. Key thêm Guid mới không tạo idempotency. Credit phải dựa trên authoritative kill/death/life/instance đã xác nhận, deterministic key; B không đi theo mà vẫn nhận wave credit của A là sai. A reset không được respawn wave B.
3. Thiếu wave members đang đi qua `CompleteIfAtEnd`, có thể bỏ objective mà vẫn hoàn tất. Profile thiếu required group/actor phải fail activation rõ ràng; runtime mất actor thì giữ pending/recover hoặc báo lỗi có cấu trúc, không auto complete. Validate đúng 3+3 actor theo design.
4. `ApplyBossDamage` là domain method, chưa phải người chơi đánh được boss qua combat HTTP. Nối ordinary combat pipeline, kiểm owner/instance/life/range/LOS/floor/alive/phaseguard tại thời điểm server resolve; không thêm debug damage endpoint để giả lập thắng boss. Quest boss và world event boss không được lẫn target.

## Bằng chứng tối thiểu của checkpoint tiếp

Hai client cùng mở P00-04/P00-05: A kill/wipe/disconnect/retry không đổi B HP/life/actor/credit; B không nhận credit hoặc snapshot của A; late event và replay không double credit. Session reconnect hợp lệ giữ đúng owner/attempt, invalid session bị từ chối. HTTP current → snapshot → telegraph/impact → damage thật → phase2/3 → wipe/new life → defeat → fragment → Trial visible → turnin/unlock; test phần chưa có ghi FAIL hoặc UNVERIFIED, không thay bằng gọi service trực tiếp. Giữ gates production OFF và no self-merge.
