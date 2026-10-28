# Qoder — Vòng chơi authoritative QOD-11 → QOD-15

Tiếp nối QOD-10 đã merge, nhận cả gói và làm liên tục theo `04_CONTINUOUS_DELIVERY_20261029.md`. Đích là một lát cắt đầu game chạy headless, không phải thêm endpoint stub rồi dừng. Sử dụng dữ liệu canonical và báo rõ nơi chỉ có fixture/dev mode. In-memory P1 chưa là backend MMORPG production.

## QOD-11 — World state, tick và di chuyển đúng topology

- Inventory những phần hiện có, ghi dependency graph/contract delta trước khi mở rộng. Không viết lại các service đã đạt nếu không cần.
- World entity registry có instance/map/floor/position/alive/state revision; NPC/spawn lấy record canonical, tách template khỏi spawn instance. Bắt đầu Bến Mưa và mob/node thực sự cần cho quest slice, không cần activate 46 map cùng lúc.
- Movement kiểm cả đoạn đường, không chỉ điểm cuối: XY/floor/map bounds, blocked/walkable, non-finite, speed/tick/sequence. Chống đi xuyên tường bằng bước dài; rejection không tiêu sequence/revision/cost. Query cho actor footprint phải ghi radius/inset explicit, không tự co map bằng con số đoán.
- Clock/tick inject được để test không sleep. Chuẩn simulation hướng 20 Hz theo production spec; cadence snapshot không được tự đổi wire khi chưa có proposal. In-memory lifecycle cleanup tránh giữ cooldown/entity của session hết hạn.
- Topology policy cho mốc này: corner-touch coi blocked theo conservative query hiện có; actor footprint là tham số riêng, không double-inset. Chưa có bundle reviewed thì chạy fixture dev và giữ production gate OFF. Không gọi synthetic Bến Mưa là bản đồ đã được duyệt.
- Có tests timestep lớn, góc tường, lỗ, floor khác, despawn, stale sequence và state nguyên vẹn sau reject.

## QOD-12 — Combat và quái có vòng đời thực

- Bắt đầu 3 skill definitions đã có; trước khi triển khai ghi bảng supported/unsupported so với mechanics canonical. Không mặc định skill nào cũng direct damage hoặc tự đổi MP/CD/range để dễ code. Bộ30 skill VFX mới là design-only.
- Quái có idle/patrol/aggro/chase/attack/return/dead/respawn; giới hạn home/leash, LOS, target alive/map/floor và reset rõ. Hành vi chưa có dữ liệu phải dùng config fixture có nhãn, không ngầm thêm thông số canonical.
- Damage/heal/status/shield/counter thực hiện theo đúng subset skill được hỗ trợ. Hp/death/cooldown/resource do server quyết định; chặn double kill, double loot, target despawn và dead target. Không cho client gửi amount/reward đáng tin.
- Cast lifecycle, hit/status/end semantic đủ làm adapter VFX: castId/eventId, map instance, source/target hoặc ground point, thời điểm/revision. Proposal schema/version/examples trước code wire; không nhét enum tự do vào `CombatEvent` cũ. Giữ client cũ được từ chối version rõ hoặc tương thích theo migration đã review.
- Idempotency: replay request được trả cùng kết quả trước stale sequence guard khi đó là cùng accepted command; body khác cùng key là conflict. Race không trừ MP hai lần hoặc phát nhiều hit/reward. Rejected cast không phát impact/loot giả.
- Tests deterministic cover guard thành công/thất bại nếu subset có Phản Quang, miss/LOS, cancel/death, refresh/end status, duplicate/out-of-order và hai người đánh cùng mục tiêu. Không gọi mọi mechanics đã done nếu mới hỗ trợ một phần.

## QOD-13 — Nhiệm vụ, khám phá, tương tác và thu thập

- Hoàn thiện vòng `AVAILABLE → ACTIVE → objective progress → READY_TO_TURN_IN → COMPLETED` theo state names của contract sau review, không tự thêm state vào wire cũ.
- P00-01 là acceptance slice tối thiểu; sau đó chọn các quest mở đầu tiếp theo có đủ dữ liệu từ canonical/narrative. Có cả nói chuyện/khám phá/thu thập, không chỉ kill count. Bảng mapping objective→event→recordId rõ và compile validation bắt dangling IDs.
- Progress chỉ từ server-owned event/interaction đã kiểm chứng, chống client cộng counters/kill giả. Mỗi event chỉ đóng góp một lần, theo map/floor/range/LOS/prerequisite. Cinematic ended không tự cấp tiến triển/thưởng; video skip không khóa cốt truyện.
- Gathering kiểm node available/range/LOS, giữ quyền claim và respawn; disconnect/cancel không tạo vật phẩm hai lần. Không tự biến mọi placement thành asset mới.
- DTO/proposal/examples và readback snapshots phải khớp validator. Chưa có topology/level profile reviewed giữ guard OFF, vẫn kiểm bằng scenario fixture gắn nhãn.

## QOD-14 — Turn-in và thưởng nguyên tử

- Bổ sung reward definition/reference theo số liệu canonical; thiếu con số thì đề xuất rõ, không tự điền theo ước lượng. Không nhập reward chỉ từ lore text không có quy tắc.
- Một transaction boundary in-memory cho quest state + item/currency + reward ledger/idempotency; nếu túi đầy, revision conflict, thiếu quest item hoặc validation fail thì không commit một phần. Có rollback/failure injection trong test.
- Turn-in cần NPC/map/floor/range/LOS/quest state hợp lệ; item amount/currency không âm/overflow, kiểm stack/unique rules từ runtime definitions. Không tự thêm endpoint grant tùy ý cho public client.
- Retry/parallel turn-in chỉ thưởng một lần; duplicate command trả kết quả ổn định; quest revision/inventory revision tăng đúng policy. Multi-player reward ownership phải explicit, không biến kill chung thành quyền nhận vô hạn.
- Repository interfaces và persistence boundary đủ thay store về sau. Ghi rõ reward ledger in-memory mất sau restart; không gọi đó là durable/exactly-once production. Auth, DB, market/guild/PvP vẫn backlog tách biệt.

## QOD-15 — Headless E2E, demo và hợp đồng bàn giao client

- Một command chạy server và scenario: create session → move hợp lệ → bị tường chặn → tương tác nhận quest → talk/explore/collect hoặc combat theo quest canonical thực → progress → turn-in → read inventory/quest → retry không nhân thưởng.
- Khi chưa có reviewed Bến Mưa, có hai profile tách biệt: default gate OFF và dev synthetic scenario. Không sửa `reviewState` chỉ để demo chạy. Có expected blocked output của profile default.
- Bổ sung meaningful self-check/HTTP smoke và CI server, fake clock không đợi respawn thật. Kiểm duplicate/concurrency, invalid ownership/session, wrong map/floor, chết/respawn, inventory full và failure giữa reward transaction.
- Bàn giao OpenCode/Muse bảng event lifecycle→VFX semantic, request/response examples và feature matrix implemented/fixture-only/missing. Không bắt Muse thêm damage collider từ animation frame.
- Report exact SHA, lệnh/output thật, supported subset, gate và giới hạn restart/auth/persistence. Không ghi FULL MMORPG hoàn thành. Tài liệu run phải giúp người khác tái tạo scenario từ clone mới.

## Cách tiếp tục

Mốc đầu mở PR contract delta hoặc world core nhỏ đủ review; trong lúc chờ tiếp tục tests/domain của mốc sau. Có thể stacked PR, ghi base rõ và không tự merge. Thiếu art không chặn headless; thiếu schema thì chuẩn bị proposal/fixtures và làm phần domain không phụ thuộc wire. Không tự nới production gate hoặc sửa tài liệu thiết kế để hợp thức hóa implementation. Ghi checklist tiến độ toàn gói và mốc kế tiếp sau mỗi PR.
