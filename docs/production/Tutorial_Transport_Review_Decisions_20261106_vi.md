# Quyết định tích hợp tutorial — 06/11/2026

ID: `DEC-TUTORIAL-TRANSPORT-20261106`. Codex quyết định trong phạm vi điều phối, review và tích hợp đã được giao. Tiếp các quyết định private-alpha trước; không đổi cân bằng production, geometry canonical hoặc enum wire hiện hữu.

## TALK: duyệt packet với các sửa bắt buộc

Duyệt phương án A của `QOD-21_TalkDialogue_Contract_Packet_20261104_vi.md`: `POST /p1/quests/talk`, hợp đồng mới additive, chỉ khi `AlphaProfile` và gate riêng `P1:QuestTalk:Enabled` cùng bật. Gate mới OFF trong cấu hình phát hành. Không dùng QuestTurnIn làm gate ngầm cho lời thoại.

- Payload bắt buộc `npcId` và `nodeId`; không tự chọn node đầu tiên. Client dùng catalog narrative đã pin cùng content version; server kiểm node tồn tại, speaker/NPC và quest/step phù hợp. Read route discovery có thể đề xuất riêng, không chặn finale hiện tại.
- P00-05 chỉ credit TALK khi boss + fragment và các objective đứng trước đã commit, đúng owner/quest attempt, map/floor và khoảng cách tối đa 5 WU tới anchor của NPC. Reveal gate chưa mở trả `409 invalid_transition`, field `revealGate`, không giả `quest_not_found`.
- `appliedFlag` chỉ mang flag narrative hợp lệ. TALK không cấp XP, turn-in, chapter unlock hoặc tự dịch map. CHOICE ngoài phạm vi verb này. Giữ text đã biên tập; không thay bằng thoại baseline cũ khi tích hợp.
- Dedupe theo character + quest attempt + objective/node; cùng node trên cùng attempt chỉ credit một lần dù key khác. Same key/body replay receipt, cùng key/body khác conflict. Event ID deterministic bao gồm attempt và node; tuple chỉ character/quest/NPC/key của packet chưa đủ để phân biệt node/attempt.
- Hoàn schema, example, negative fixtures và validator trước code HTTP. Không mở enum `CombatEventV2` hay sửa nghĩa world entity hiện có.
- E2E phải hoàn fragment → TALK đúng thầy → READY_TO_TURN_IN → turn-in một lần → quyền chương. Giữ level gate thật: nếu chưa đủ cấp 11, C1-01 vẫn LOCKED với lý do cấp; không ép AVAILABLE để làm bài xanh.

## Portal: duyệt registry/route; packet dữ liệu alpha là checkpoint tiếp theo

Duyệt `POST /p1/world/portal` nhận duy nhất `portalId`, gate riêng `P1:Portal:Enabled` cộng AlphaProfile, mặc định OFF. `portal_locked` là code hợp lệ cho quyền chưa mở. Không nhận tọa độ/map/reason từ client.

Giai đoạn này chỉ cặp Bến Mưa ↔ Thanh Lạc, hai chiều sau khi character có `CHAPTER_C1_UNLOCKED` từ turn-in P00-05. Không thêm yêu cầu quest ACTIVE/party hoặc phí/cooldown ngoài nguồn. Loading là presentation; không tạo luật chờ server. Thăng Long vẫn theo C1-06, không mở theo P00-05.

Qoder giao registry alpha riêng từ atlas đã đối chiếu: Bến Mưa `(348,0)` → Thanh Lạc `(8,0)` theo bảng tuyến §cổng cuối atlas; chiều về kích hoạt tại Thanh Lạc `(20,0)` (`TP_TL_BEN_MUA`) → Bến Mưa `(348,0)`. Phân biệt arrival8 với return portal20, không tự gộp hai điểm này. Arrival Bến Mưa348 của chiều về là quyết định private-alpha tại anchor cổng đã có; không công nhận là safe/death anchor. Không đổi `[18,0]` death return, 349 placement hay topology reviewState. Nếu geometry fixture không cho đứng tại anchor, fail activation có lỗi cụ thể và gửi delta; không clamp âm thầm vào chỗ khác.

Giữ source ID `TP_BM_THANH_LAC` / `TP_TL_BEN_MUA` nếu đúng ID atlas ở head triển khai; đối chiếu tên thực trước khi xuất. Không dùng ví dụ `MAN-TL-PORTAL_C1` như thể đó là canonical record. Cùng tọa độ có thể nhiều đích trong registry; mỗi request chọn route ID server phát hành, không nhân bản geometry.

Map transition cần transaction/receipt và cleanup cast/guard/counter/aggro/held movement theo policy, revision và actor/life identity đúng. Replay cũ trả receipt lịch sử, không kéo character từ map mới về; client fresh-read. Wrong map/floor/range/dead/locked/owner và hai owner phải có test. Thực thi TALK trước để khép P00-05; portal làm song song sau packet, không bắt TALK chờ portal.

## MAP_VIEWED và các hợp đồng nền

MAP_VIEWED phải là intent riêng có server acknowledgement khi C1-01 ACTIVE và character thực ở Thanh Lạc. GET world/map và portal response không cấp objective này. Qoder giao additive packet ngắn cho `POST /p1/quests/map-viewed` với questId, idempotency, owner/attempt/map guards; dùng gate private-alpha riêng. Không nhét action vào TALK hoặc death-return.

Giữ wire error hiện hành: không rename 62 mã sang 13 mã chung, không đồng nhất `session_not_found` với `CHARACTER_NOT_FOUND`. Packet mapping theo ngữ nghĩa và version/capability là đầu việc riêng; subsystem chưa có tiếp tục ghi unsupported. OAuth/auth edge ngoài Health P1 hiện tại.

Retention 30 ngày là yêu cầu production chưa đạt, không được sửa tài liệu thành 256 hay tuyên bố đạt bằng tăng cache. Qoder local giữ lifeVersion/death identity đơn điệu cho toàn bộ character còn sống trong store, kể cả đã hồi sinh; không reclaim vì unrelated churn. Receipt cũ không trở thành fresh command trên đời sau. Qoder Remote sở hữu durable receipt/state/revision/ledger/outbox và expiry/tombstone đã công bố. Trước khi có durability, không evict nghĩa vụ chưa thể chứng minh hết hạn; báo dung lượng và giới hạn private-alpha rõ ràng.

Rate limit economy/chat cần packet riêng thuộc server API boundary, auth edge cung cấp identity. Chưa chốt số quota thì chưa bật route economy/chat production; không dùng con số ngẫu nhiên. Các câu hỏi cân bằng skill/pet/elite không được giải quyết bằng tự đặt numeric trong work này; giao packet nguồn và tiếp phần không phụ thuộc.
