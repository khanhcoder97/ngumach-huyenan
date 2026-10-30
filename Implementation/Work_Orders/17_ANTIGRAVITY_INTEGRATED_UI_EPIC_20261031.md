# Antigravity — AG-02, từ panel riêng sang vòng chơi tích hợp

Theo yêu cầu chủ dự án, nhận **trọn gói A→E** và tiếp tục liên tục. Baseline #89 head94fb60578add1b8a92d0039f69e2843d6bd44ff3; đọc report Agent_Reacceptance_20261031_vi. 97/97 diagnostic và binding đã đạt, không quay lại sửa những ca đã xanh. Giữ issue85/80, branch/stack hiện tại; không tự merge hoặc đóng epic.

Quyền sửa giữ work order16: Presentation, Unity/PlayerUI, builder/resources/tests/workflow của mình; P1OnlinePanel chỉ composition/input/NPC hook. Không sửa Core/server/closed contracts/producer probes, art/Animator/scene của Muse hoặc canonical XY. Chờ API/media thì gửi packet cụ thể và tiếp phần không phụ thuộc.

## A. Composition và lifecycle hoàn chỉnh

Factory phải thật sự dùng UIDocument argument; inject doc và settings store vào mọi panel. Builder phải setup đúng HUD host, PanelSettings hợp lệ có ownership, lỗi thiếu dependency rõ và undo/idempotence. Không FindFirstObjectByType cho global document/store. Test hai document để chứng minh không gắn/scale nhầm.

Thiết kế Close/Dispose/Rebind thống nhất: hủy pending work, Clear NPC context, detach visual tree/callback, dispose presenters/adapters đúng ownership. Initialize sau Close không tạo UI/callback trùng. Có 200 open/close/rebind cycles, late success/error sau cancel, NPC switch A→B, expiry và disconnect. Không chỉ assert IsVisible=false; đo attached element/listener counts và command dispatch.

## B. Hành trình qua adapter thật

Thêm integration harness dùng concrete P1ClientAdapter/P1Client và scripted transport của closed contract, không thay adapter bằng fake state machine. Chạy P00-01 selectedNPC→accept→package read/progress→READY→turn-in receipt→inventory/journal readback; lost response/replay/revision/expiry không nhân reward. Sau đó chạy HTTP profile với server reviewed và ghi exact client/server SHA. Native Unity là gate riêng; không mạo nhận fake hoặc syntax thành engine pass. Hook NPC vừa thêm chỉ là điểm bắt đầu.

## C. Túi/nhân vật/nhật ký/map hoàn thiện

Hiển thị diagnostics item duplicate/out-of-range/overflow thay vì bỏ mất dữ liệu; giữ vị trí100slot, full tooltip/source/class/rarity, filters/keyboard/touch hoạt động, trạng thái unsupported có lý do. Exact catalog có provenance; unknown phải unknown.

Nối PinnedQuestId với HUD tracker thật, chọn/unpin/resync có semantics rõ. Map lấy bounds/content version được cấp, project corners đúng, pan/zoom/camera rectangle/legend/NPC quest audience; waypoint reset map/floor/session. Bỏ hệ số4px/WU không nguồn; không phê duyệt candidate topology thay producer.

## D. Cinema/settings/accessibility

Giữ reading-room PR95 là bản thảo ngoại tuyến; không dùng lựa chọn Ink cấp objective/reward. Cinema adapter có source manifest và state loading/playing/ended/skip/failure/fallback/disposed, guard callback cũ; live trigger chỉ từ contract được duyệt. Media thiếu dùng fallback có nguồn và nhãn. Input Escape/Space đi qua một owner cùng modal stack, không rơi xuống movement/combat. Settings apply ngay khi init trên đúng document, text size/input hints có hiệu lực hoặc disable rõ. Scale/safe-area tiếng Việt dài ở640×360,960×540,16:9/20:9, touch/keyboard; tránh dựng toàn UI mỗi frame nếu revision không đổi.

## E. Bàn giao toàn gói, không dừng sau một fix

Commit/push theo checkpoint đủ review rồi tiếp module kế tiếp. Feature matrix phải phân biệt source/pure fake/concrete transport/HTTP/native/preview/unsupported. Báo cáo chưa đạt không đổi thành Completed. Gửi Muse VM packet exactSHA, Unity6000.3.17f1, setup menu/scene/PanelSettings/profile, expected assertions và layout list để chạy import/playmode/screenshot; không yêu cầu máy chủ dự án cài Unity. Native thiếu vẫn tiếp A–D và tests ngoài engine. Chỉ Codex nghiệm thu và merge sau review.
