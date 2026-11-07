# QOD-29 — provenance cho vị trí hộ tống theo owner

Ngày 2026-11-07. Work order 31 Q4; source head `1af85783b13fc8508a4744078168f72bc5a70830`. **Packet chờ duyệt; không mở wire v2 hoặc thêm handler.**

## 1. Delta thực tế

`Server/Health/Gameplay/Alpha/AlphaEscortService.cs:153–215` giữ vị trí/instance theo character, tick kiểm map và HP. `:224–258` chỉ credit death đúng killer owner, wave active, entity member và life; dedupe instance/attempt/wave/life/death. Instance dùng `ESCORT-P00-04-1-{character}` và attempt `"1"` (`:632–660`). Không có owner-life hoặc floor trong instance, và map guard không là floor guard.

`Server/Health/World/NpcEscortPosition.cs:9–19` chỉ trả entityId+x/y. `WorldEntityAoiProjection.cs:37–52` có mapInstanceId/floor/phase/revision/lifeId nhưng đó là canonical world actor, không phải escort movement revision hoặc owner life. `:86–100,129–136` lấy owner override cho AOI rồi `Map` lại lấy vị trí; hai lượt đọc không chứng minh một sample atomic trong lúc tick đi tiếp. Không được gọi canonical actor life là owner life, hoặc `mapId#1` là escort instance.

HTTP wiring, hai owner và AOI leave/reenter đã có checks tại `Smoke/e2e_p1.py` và `Smoke/ServiceSelfCheck.cs`; negative control trước đó chỉ tháo position-source wiring làm x42→42 fail. Không đổi healthState/targetable/availability hoặc quy trách nhiệm stall lịch sử từ log chưa đủ.

## 2. Bề mặt additive đề nghị

Đề nghị một read response `EscortProjectionV1` trên route riêng (tên chưa chốt), owner-only theo session. Không thêm field vào `WorldSnapshotV2`: `Implementation/Contracts/P1/WorldSnapshotV2.schema.json:123–143` khóa additionalProperties của entity. Không thêm type vào CombatEventV2.

Sample tối thiểu gồm schemaVersion/serverTick, ownerCharacterId/ownerLifeVersion, questId/questAttemptId/escortInstanceId, actorNpcId/actorEntityId/actorEntityLifeId, mapId/mapInstanceId/floorId, xWu/yWu. Identity lấy server-side; coordinate và provenance cùng sample dưới lock của domain. Nếu cần movementRevision/escortGenerationId, owner phải định nghĩa semantics; không mượn entity revision để giả như đó là movement revision.

- Owner hiện tại đọc vị trí domain của chính họ trong AOI 40/48 WU hiện hành; observer không đọc override của người khác.
- Off-AOI không trả tọa độ ẩn qua read route mới. Non-owner world row vẫn canonical anchor.
- Escort instance và open-world map instance là hai identity riêng. Không đổi floor/map canon hoặc tạo nhân bản geometry.
- Wipe/revive không tự tạo NPC respawn life. Owner life từ PlayerLifeLedger; actor entity life từ registry. Quest checkpoint và attempt giữ theo luật source, không reset bằng suy đoán.
- Gate/capability riêng đề nghị, default OFF cộng AlphaProfile; chưa chọn tên route/gate khi chưa duyệt. Không bắt wire cũ nhận thêm field.

## 3. Câu cần duyệt

1. Route read additive + schema/capability/version; shape ở mục 2 có đủ không? Mặc định: wire mới unsupported.
2. Floor binding OVERWORLD theo actor canonical, và guard phải áp cả tick/read/credit; không có numeric mới. Mặc định: không cho provenance claim ở floor chưa bind.
3. Owner-life snapshot từ ledger ở checkpoint nào và xử lý sample stale lúc tick/death/revive? Đề nghị validate cùng owner/map/floor/life khi sample commit; stale sample không được thành fresh movement/credit.
4. Attempt hiện chỉ `"1"`; duyệt phạm vi one-shot hoặc giao attempt allocator/reset policy. Không dùng revision làm attempt; không invent generation.
5. Có cần movement revision hoặc escort generation không? Nếu có, quy tắc bump/reset/receipt migration; nếu không, serverTick+identity sample, không gọi tọa độ khác là revision world khác.

## 4. Tests/migration

Schema/examples/negative validator trước handler. Hai owner cùng canonical actor phải nhận hai sample khác nhau đúng provenance; third observer không lấy sample A/B; wrong owner/map/floor/life; wipe/revive; stale death/memberLife; quest ended; AOI leave/reenter; concurrent tick/read cho một sample coherent.

Bỏ **chỉ** position wiring: assertion HTTP x/y tiến theo domain phải fail. Đổi **chỉ** owner/instance/attempt/floor/life trong fixture: provenance assertion tương ứng phải fail dù x/y vẫn đúng. Không lấy readiness subset chung để bỏ healthState/targetable/availability. Existing V2 schema unchanged và consumer không hỗ trợ route mới phải báo unsupported; không gọi console PASS là native PASS.

Migration giữ canonical entityLifeId/revision và checkpoints, không backfill một owner-life giả cho receipt cũ. Remote nhận adapter identity/sample đã duyệt, không thêm DB writer trong Health. Capacity/retention của source read không được gọi production durability trước R1–R8.
