# Quyết định tích hợp và va chạm sông Bến Mưa — 04/11/2026

## Một hợp đồng encounter chung

`Implementation/Content/DesignBaselines/encounter_snapshot_v1_reference_20261104.json` là **payload mẫu tổng hợp do Codex biên soạn từ packet Qoder + quyết định duyệt**, không phải snapshot capture từ server đang chạy, không phải bằng chứng HTTP PASS. Dùng làm reference chung để Qoder xuất schema/fixture và OpenCode parse đúng cùng dữ liệu. Nó mô tả `result` của response P1; HTTP envelope/status/error giữ pattern P1, không tự thêm session/generation field vào payload đóng.

Tên trường theo packet: top-level `registeredCharacterIds`, `moveCooldownRemainingTicks`, `phaseNpc`, `trialNpcVisible`; shape dùng uppercase CONE/CIRCLE/ANNULUS, `centerXWu/centerYWu`; arena hình tròn. **Không duyệt** các thay thế `registration`, `center:{x,y}`, arena min/max, `npcId` đơn hoặc `cooldowns` trong DTO OPC-15 e351e81. Đổi numeric phase/life mới chỉ sửa một phần; không đổi tiếp server theo DTO client tự tạo. `activeMove.stateEndsAtTick`, castId và facing cone là bổ sung đã duyệt. Giá trị nullable theo hình và các trạng thái reset/dead/null-move phải vào schema + fixtures do Qoder công bố; không tự coi missing field bằng0 hoặc empty list.

ID trong mẫu là dữ liệu test. Không dùng bossEntityId mẫu để tạo một actor mutable chung giữa mọi owner. Client render theo actor ID trong response đã xác thực; server thực thi instance/life/credit isolation. Nếu cần đổi wire sau reference này phải gửi field diff chung trước, không tạo hai schema v1 cùng tên.

## Chặn nước sông Nam: duyệt triển khai có kiểm chứng đường đi

Đã đọc gói `ClientGodot/docs/evidence_water_block_20261104/` tại PR111 head765a0d6, hydrate và xem ảnh crop sông. Kiểm JSON: **306 ô nước duy nhất, 306/306 ground=null/path=null/blocked0→1**; ảnh chú thích đặt chúng trên nước. Đây là nguồn để sửa lỗ collision nước, không đủ chứng nhận toàn bộ navigation map.

**Duyệt triển khai chặn đúng 306 ô** theo tọa độ trong evidence, giữ **37 ô bờ đi được** và giữ nguyên sàn cầu/path. Tổng blocked mục tiêu 5.069→5.375. Không chặn cả hàng, không thêm ô thứ307, không sửa canonical349placements hoặc nâng topology lên REVIEWED. Hai ô dưới cầu là nước ở layer dưới, không phải sàn cầu; collision phải xét layer/floor thực tế và không bịt tuyến cầu trên.

Trước khi đưa delta vào profile dùng chung: Muse và Qoder cần một navigation delta version/hash chung, cell0.8WU/originY36/450×60, test phạm vi chính xác, world↔tile round-trip, seams, footprint24×12px và swept movement. Spawn→kiện→ripples→dân→80/120→boss/fragment/Tạ→portal348 phải đi được, không cheat teleport. Test điểm bờ/cầu kề nước và rollback-safe startup khi source hash không khớp. Nếu có anchor/path hợp lệ bị chặn, dừng kích hoạt delta và gửi đúng cell/path, không tự di chuyển NPC/objective.

Chỉ client clamp là chưa đủ authoritative: Qoder cần cùng delta trong private alpha nav validation. Bàn giao source delta có version trước, activate sau khi hai phía dùng cùng hash. Giữ baseline5069 của checkpoint cũ tới khi delta được kiểm; không sửa ngầm baseline dưới cùng version hoặc bật riêng client rồi tuyên bố online collision đúng. Review asset style2 là cửa riêng, phê duyệt collision không tự phê duyệt mọi sprite/VFX còn DRAFT.
