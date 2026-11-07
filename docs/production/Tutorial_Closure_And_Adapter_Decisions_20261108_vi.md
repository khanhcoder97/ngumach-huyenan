# Khép tutorial và đồng bộ adapter — 08/11/2026

Quyết định `DEC-TUTORIAL-CLOSURE-20261108`, tiếp work31. Source máy đọc được: `Implementation/Content/DesignBaselines/tutorial_closure_20261108.json`. Đây là approval nội dung/transport private-alpha; chưa có loader/route/native nào được nhận chỉ vì file này tồn tại. Production OFF, không đổi canonical placement/topology hoặc cân bằng combat.

## Node xác nhận nhập môn

Duyệt node `DLG_P00_05_CLASS_CONFIRM` và text trong JSON, speaker `NPC_CLASS_TRIAL`, map Bến Mưa/floor OVERWORLD, trước turn-in. Nguồn spec đã yêu cầu xác nhận môn phái ở NPC này và quyết định alpha đã sửa spawn window sau boss+fragment, trước COMPLETED. Không cần hỏi lại quyền thêm node.

Qoder nhận overlay narrative riêng cùng AlphaProfile: baseline229 node không bị gọi thành thiếu hoặc thay toàn bộ; alpha có thêm node được duyệt và source textKey/textVi. Graph CLUE→CLASS_CONFIRM→TURN_IN; đổi order của TURN_IN trong overlay, giữ ID/text cũ. Node tồn tại trong graph không đủ để grant: TALK fresh phải thấy hai counter boss+fragment đã commit và đúng owner/attempt/step/NPC/map/floor/range. Chỉ credit đúng `OBJ_P00_05_CLASS_CONFIRM`; giữ class server đã tạo, không respec/chọn lại và không auto-turn-in. Dedupe/receipt đã duyệt tiếp tục áp dụng.

Codex đã đọc voice guide và tuyến P00-05 trước khi viết câu này. Quan sát viên chỉ xác nhận việc ghi môn phái và bảo người chơi về gặp Tạ; không biết thay người chơi bí mật của mảnh ấn. Presentation có thể bỏ qua đọc, nhưng progression phải là server TALK acknowledgement. Không dùng video ended/đóng panel để hoàn quest.

## MAP_VIEWED: duyệt QOD-28 với binding cụ thể

Duyệt payload questId-only, response scoped trong QOD-28 và gate `P1:QuestMapViewed:Enabled` cộng AlphaProfile, default OFF. Nội dung alpha bổ sung objective `OBJ_C1_01_MAP_VIEWED`, type `MAP_VIEWED`, target/map Thanh Lạc, floor OVERWORLD, count1; append sau hai TALK objectives đang có, required trước READY_TO_TURN_IN. Type này là content/internal progression mới có schema+validator; không sửa enum CombatEventV2 hoặc kiểu world entity đóng.

Attempt `"1"` chỉ hợp lệ cho one-shot chưa hỗ trợ reaccept; revision không là attempt. Receipt/event tuple đầy đủ theo JSON. Fresh request cần ACTIVE, đúng map/floor/owner/content version; request replay dùng receipt trước fresh guards. GET, portal và TALK không credit MAP_VIEWED. Không cấp item/XP hoặc tự unlock qua acknowledgement.

Migration phải có content-version boundary: ACTIVE giữ counter cũ, thêm counter mới0; READY và COMPLETED giữ objective set/state cũ, không bị relock hoặc nhận reward lại. Runtime chưa có migration store thì chỉ activate bundle mới cho process private-alpha sạch và công bố rõ; không âm thầm áp giữa phiên hoặc nhận receipt version cũ như lệnh mới. Native flow mở map gửi intent thật; UI không tự sửa counter.

Level11 vẫn là điều kiện C1-01. Portal permission sau P00-05 không bỏ qua cấp. Positive Bến Mưa→Thanh Lạc có thể kiểm ngay sau tutorial; C1-01 ở level thấp phải LOCKED. Positive level11 fixture/domain conformance ghi nhãn rõ, không gọi là nhân vật tự lên11 qua tutorial. Giao nguồn progression tới cấp11 riêng nếu đường tự chơi còn thiếu.

## Hộ tống: duyệt QOD-29 có sửa cách lấy sample

Route read additive `GET /p1/quests/escort/current`, schema `EscortProjectionV1`, gate `P1:EscortProjection:Enabled` cộng AlphaProfile, release OFF. Bắt buộc provenance theo packet: ownerCharacterId/ownerLifeVersion, questId/questAttemptId/escortInstanceId, actorNpcId/actorEntityId/actorEntityLifeId, mapId/mapInstanceId/floorId, xWu/yWu và serverTick. Dùng envelope hiện hành; không có sample khi quest ended/off-AOI, và không trả tọa độ ẩn.

Đọc một sample domain nhất quán, dùng chính sample đó cho AOI và response; không gọi source vị trí lần hai. Capture owner life/map/floor cùng phiên hợp lệ; stale sample không là movement/credit mới. One-shot attempt1, không thêm generation/movementRevision chưa cần. Giữ identity NPC canonical và escort instance riêng; wipe/revive giữ checkpoint theo policy, không tự reset entity life. Kiểm floor cả tick/read/credit, không chỉ map.

## Những câu hỏi ngoài đường tutorial

`NPC_MASTER_BY_PLAYER_CLASS` là token nguồn: duyệt server resolve từ class authoritative qua năm `NPC_MASTER_<CLASS>` đang có registry/anchor, trên đúng map/floor của node. Không để client chọn class/NPC thay thế, không mint NPC mới. Class chưa executable vẫn unsupported, không gọi đủ năm lớp chỉ từ catalog.

Journal ba trạng thái quan sát/giả thuyết/đã đối chiếu là trình bày: observation ref/server receipt là bằng chứng; chỉ phần server-confirmed được gọi đã đối chiếu. Hint30/60s thuộc client idle/help timing, không là reward timer. Cinema receipt/seen là presentation với content version, không đổi quest/loot. Không có nguồn Trust numeric thì giữ lựa chọn narrative flag, không biến flag thành điểm Trust bịa.

Đối với QOD-27: giữ số elite REFERENCE_L5 hiện có dưới nhãn legacy private-alpha fixture; chưa chuyển toàn production sang CSV hoặc sửa CSV để giấu xung đột. Duyệt B1 cấu trúc hóa passive cap có provenance/units/scope/ICD, nhưng activation của effect không parse được phải bị từ chối; catalog nguồn khác vẫn được đọc và báo unsupported, không làm toàn Health fail chỉ vì module chưa active. B2 display-only tiếp tục cho phần chưa executable; B3 đổi cân bằng cần packet riêng. Không mở pet/mount wire hoặc áp skill mới trong gói này. Display identity item theo canonical item ID, giữ alias source, không dùng khác tên để tạo thêm vật phẩm. Required owner level và companion level cap là hai miền khác nhau, không so trực tiếp để kết luận mount bất khả thi.

Ledger retention30ngày, durable receipt và 10.000 replay vẫn là acceptance chưa đạt cho tới module Remote được kiểm. Duyệt lookup global key/owner/hash và full historical return DTO ở QOD-25 §7 làm input thiết kế adapter; tombstone luôn từ chối thực hiện lại, chưa có expiry approved thì không reclaim nghĩa vụ. Library không tham chiếu ngược executable Health; tách DTO để review dependency một chiều. Không ghép writer sau domain mutation rồi gọi atomic/crash-safe.
