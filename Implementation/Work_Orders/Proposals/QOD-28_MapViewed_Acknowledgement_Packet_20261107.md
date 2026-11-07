# QOD-28 — MAP_VIEWED acknowledgement riêng

Ngày 2026-11-07. Work order 31 Q3; source head `1af85783b13fc8508a4744078168f72bc5a70830`. **Packet chờ duyệt; chưa thêm schema, gate hoặc handler.**

## 1. Phạm vi đã giao và chỗ dữ liệu còn thiếu

`DEC-TUTORIAL-TRANSPORT-20261106`, trên `origin/codex/agent-handoff-dispatch-20261106`, mục MAP_VIEWED, yêu cầu `POST /p1/quests/map-viewed` riêng với questId/idempotency/owner/attempt/map guards. Chỉ acknowledgement khi C1-01 ACTIVE và character thực ở Thanh Lạc; GET world/map và portal không credit. Đây không phải đề xuất tự mở thêm gameplay.

Nguồn chạy `Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json:216–237` ghi `mapViewedAction`, một credit/quest, không thưởng khi đọc map. Nhưng `Implementation/Content/Examples/QuestDefinitionAlpha/C1-01.json:17–37` chỉ có hai objective TALK: `OBJ_C1_01_REPRESENTATIVES` (3 người) và `OBJ_C1_01_TRIAL_REGISTRATION` (1 người). **Không có objective MAP_VIEWED hoặc ID để bind.** Không dùng lại một counter TALK, không đặt tên mới rồi gọi canonical.

C1-01 có band 11–20 và prerequisite P00-05 (`C1-01.json:8–16`). Quyền chương không bỏ qua cấp 11. Accept kiểm cấp ở `Server/Health/Gameplay/Quests/InMemoryQuestAcceptService.cs:120–129`; availability read hiện chỉ kiểm prerequisite ở `InMemoryQuestService.cs:378–427`. Vì vậy chưa được gọi toàn bộ read surface là đã giữ LOCKED-with-level-reason; sửa guard đọc là delta riêng của luật đã duyệt, không đổi schema ở packet này.

## 2. Hợp đồng nhỏ nhất đề nghị

- `POST /p1/quests/map-viewed`, envelope v1 hiện hành gồm schemaVersion/requestId/idempotencyKey/sentAtUtc/characterId/payload. Payload **chỉ** `{ "questId": "C1-01" }`, additionalProperties false. Không nhận map/coordinate/counter/eventId/reward từ client.
- Owner từ session header `X-Session-ID`; body characterId phải khớp. Server lấy map/floor/attempt từ state, không tin client.
- Gate riêng đề nghị `P1:QuestMapViewed:Enabled` **AND** AlphaProfile; release OFF. Tên gate chưa là cấu hình đã tồn tại.
- Fresh command chỉ được credit khi quest ACTIVE, đúng owner, map `MAP_THANH_LAC`, floor đã duyệt, objective bind hợp lệ. Không dùng khoảng cách tới NPC cho hành động mở bản đồ.
- Receipt đề nghị: questId/objectiveId/questAttemptId/mapId/credited/replayed/eventId/questRevision, trong envelope response hiện hành. Không XP/item/currency/turn-in/chapter/teleport.
- Same character/key/body trả receipt lịch sử trước fresh-state/map guards; khác body conflict. Key mới vẫn không credit lần hai cho cùng character/quest/attempt/objective. Event deterministic từ tuple đó; requestId không là identity progression.
- Không mở `CombatEventV2`; acknowledgement thuộc response verb này. Không sửa nghĩa GET world, portal hoặc TALK.

## 3. Attempt và migration không được giả định

`QuestStateStore.cs:29–52,69–85` chỉ key character+quest, counters/contributions/revision; không có attempt lifecycle/reset. `QuestTalk.cs` dùng attempt `"1"` cho lifecycle một lần hiện tại. Revision không phải attempt. Đề nghị cùng first-attempt identity **chỉ khi owner duyệt**, và trước reaccept phải có allocator/server precondition do Remote/local thống nhất; key cũ không thành command cho attempt sau.

`InMemoryQuestService.cs:111–267` hiện fan-out verified event qua mọi quest ACTIVE, map/type/target rồi dedupe; không có MAP_VIEWED dispatch hoặc quest/attempt parameter. Implementation sau approval cần writer scoped đúng quest/attempt/objective, không nhét event vào TALK fan-out. Không tạo persistence writer thứ hai.

Việc thêm objective không được silently backfill cho quest READY/COMPLETED. Migration phải pin content version, bảo toàn counter hiện có, và chỉ rõ trạng thái nào được thêm counter zero. Already completed không bị relock hoặc cấp lại reward nếu chưa có quyết định migration riêng.

## 4. Các câu cần duyệt

1. Objective ID chính thức, type nội dung và vị trí trong C1-01; acknowledgement có bắt buộc trước READY_TO_TURN_IN không? Mặc định: không sửa pack/counters.
2. Floor được phép: đề nghị OVERWORLD theo world hiện tại, nhưng nguồn MAP_VIEWED chưa ghi floor. Mặc định: không mở handler trước binding.
3. Duyệt payload/receipt/gate ở mục 2 và attempt `"1"` cho lifecycle hiện tại; error mapping giữ code đang có (`invalid_payload`, `session_not_found`, `quest_not_found`, `invalid_transition`, `idempotency_conflict`, `out_of_range` nếu được chọn cho wrong map), không tự thêm enum. Mặc định: unsupported.
4. Migration cho ACTIVE/READY/COMPLETED tại content-version boundary; không dùng revision làm attempt hoặc backfill reward.

## 5. Tests và thứ tự bàn giao sau duyệt

Schema/examples/negative fixtures/validator trước handler. Bốn gate combinations; missing/foreign session owner; unknown/wrong quest; inactive/ready/completed; wrong map/floor; actual Thanh Lạc ACTIVE; same-key replay sau rời map/turn-in; changed-body conflict; different-key dedupe; simultaneous same/different keys; hai owner và reconnect. Fresh commands không tăng counter/revision khi bị từ chối.

Control: GET world nhiều lần và portal thành công vẫn zero MAP_VIEWED; bỏ acknowledgement wiring thì assertion HTTP credit phải fail. Content validator phải fail nếu mất ID/map/type/count binding; TALK-only không được READY khi MAP_VIEWED đã được duyệt là required. Level10 reject/LOCKED, level11 vẫn cần prerequisite; không ép AVAILABLE để E2E xanh. Giữ old world/event schemas byte-for-byte; packet này chưa tăng số wire schema.

## 6. Đính chính runtime 2026-11-07

Nhận xét availability ở mục 1 là trạng thái trước delta C1 trong checkpoint này. Read có actor nay lấy cấp authoritative, chỉ đổi LOCKED/AVAILABLE, giữ revision khi không đổi trạng thái. Read theo character ID không tự mở availability; core và HTTP accept đều từ chối ngoài band bằng code hiện có `prerequisite_not_met`, field `level`. GET vẫn chỉ có QuestState schema cũ, **không có field reason**; chưa được gọi GET là LOCKED-with-level-reason. Không thêm field để che khoảng trống hợp đồng. Release candidate đã đo ba lượt 600/600 self-check, gồm prerequisite thực COMPLETED ở level10, threshold11, upper band, passive read và ACTIVE/terminal invariance. Không biến packet MAP_VIEWED thành approval handler.

Bổ sung cùng ngày sau portal/snapshot regression: restored final candidate đo ba lượt608/608 với log aggregate đầy đủ; alpha HTTP132checks đo C1accept422 `prerequisite_not_met`/false/["level"], QuestStateLOCKED revision1 giữ nguyên. Mốc600 phía trên là lịch sử trước tám check mới. GET vẫn không có reason field; canonical MAP_VIEWED binding và approval packet vẫn thiếu, chưa có handler. RawHTTP/commands ở `Implementation/Reports/QOD-18_handoff_vi.md` §8.
