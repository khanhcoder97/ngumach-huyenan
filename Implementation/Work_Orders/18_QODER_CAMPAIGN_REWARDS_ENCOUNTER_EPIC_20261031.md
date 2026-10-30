# Qoder — QOD-18/19, tiếp toàn bộ Q-C→G

Nhận cả chuỗi dưới đây, làm liên tục qua các milestone; không dừng sau ACK/proposal/một quest/một PR. Baseline PR91 `609a316a7c6e09f9265d39d6cffe97defa35dbc1`, base84 và stack server hiện tại. Nghiệm thu producer:338self-check, replay/queue probes, local mob HTTP85 đạt; CI7/7. Q-A và Q-B nhận theo report, không tự coi telegraph/DeathReturn domain-only đã là live wire. Giữ #87 và link điều phối #41. Không merge/reset/clean checkout chủ dự án; các thay đổi đang làm QuestCatalogLoader/QuestDefinition/Program giữ nguyên ownership của bạn.

Phạm vi: Server/Health gameplay, schema/examples/exporter/proposal/test/workflow tương ứng. Không client/UI/art, không Tools/ProducerReview/ContentPipeline/BuildCandidates của Codex, không Server/Persistence* của QODER Remote #79. Candidate compiler từ main là nguồn đầu vào, không tạo compiler song song hoặc biến blocked numeric thành production approved. Đọc work order13 đầy đủ cùng DEC016–023, rules/precision và narrative pack mới.

## C. Chuỗi nhiệm vụ có khám phá

Tiếp runtime objective graph P00-01→02→03 trước, rồi04/05; prereq/event source/checkpoint/read model/canonical class resolution và tests. C02 nghe/khảo sát, C03 cứu hai NPC, C04 escort2×3waves/80/120 theo nguồn: không thay mọi nhiệm vụ bằng kill counter. Tách accepted/objective-ready/turn-in-commit, reject event sai owner/life/map/floor/generation, late/duplicate/out-of-order. Reward/next quest chỉ sau transaction thật. Không credit từ việc xem thoại/skip video/Ink local.

Giao graph/export/schema proposals cụ thể cho các field thiếu và đồng thời làm domain/tests/quest đã đủ nguồn. Giữ chronology: thư nguyên→chuông/ripple→hai lời kể→niêm rạn→boss clear→tương tác mảnh ấn→tên Huyền Ấn→xác nhận lớp đã chọn→portal. Chưa lộ Cơ/trách nhiệm Tạ/ba mươi năm. Workshop PR95 là staging/dialogue candidate, không quest authority.

## D/E. XP/stat, thưởng, túi và trang bị

Một grant orchestration có idempotency/expected revision/source-life; replay/death/RETURN/wipe không roll hay grant hai lần. Xuất formula/provenance XP/stat/class/gear, phân biệt weapon_power với primary_stat để không cộng đôi. Level-up/maxHP/currentHP theo luật đã duyệt. Item100slot, stack, fullbag, quest-container, currency overflow/conflict có tests. Bất kỳ numeric chưa resolve phải unsupported/gateOFF kèm source request, không bịa roll/coin bands. Implement endpoints equip/unequip/use chỉ trong phạm vi luật có nguồn; closed schema phải proposal/version/capability/examples và compatibility tests trước khi map live. Handoff Antigravity fields, errors, revisions, replay semantics và exact serverSHA; không yêu cầu họ đoán từ template prefix.

## F. Mãng Cốt và kết thúc tuyến

Hoàn encounter state machine/config proposal từ nguồn Rules§4: ba đòn, ưu tiên C→B→A,60%/30%, không overlap. Arena/safe-pad/attempt/reset/contribution/credit rõ. Implement deterministic labelled fixtures trong lúc field còn chờ review, không giả approved balance. Telegraph/impact/cancel/wipe/reset không trùng damage/death/loot. Party chưa có giữ solo/unsupported; người rời không làm giảmHP exploit. Sau clear, seal interaction và class-confirm đúng thứ tự trước route unlock; reconnect không tạo attempt mới hoặc mở sớm. Bàn giao death-return/status/telegraph versioned contract proposal để producer review riêng, không lén thêm field vào v1/v2 đóng.

## G. E2E hai client và bàn giao

Một lệnh chạy defaultOFF, DEV có nhãn và2client trên chuỗi thật đã executable; báo coverage theo từng quest, không gọi P00-01 là campaign. Đối kháng package/node/kill/reward, đầy túi, lost receipt/retry, death/dash/guard/map/floor/cursor overflow. Timing unit dùng fakeclock/barrier; HTTP conditional boundedwait, không retry để che lỗi. Counter MISS assertion đã sửa count nhưng producer lần này chỉ quan sát IMPACT34: bổ sung deterministic MISS validation ngoài vòng retry, không dựa may rủi.

SelfCheck đang có4CS8602 warnings: sửa bằng explicit assertion/guard có chẩn đoán, không suppress global. QODER Remote giữ durable DB; chỉ nối reviewed interface, durable gatesOFF đến khi có crash/restore/outbox proof. Commit/push từng checkpoint, cập nhật #87 với feature matrix và exactSHA rồi tiếp phần khác; không chờ lệnh mới sau mỗi milestone. Không tự bật production hoặc merge stack.
