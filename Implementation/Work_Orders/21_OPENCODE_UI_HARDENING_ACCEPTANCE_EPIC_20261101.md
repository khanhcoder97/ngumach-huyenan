# OpenCode LOCAL — OPC-14: UI correctness, accessibility và nghiệm thu gameplay

## Lệnh tiếp sau review OPC-13

Chủ dự án yêu cầu kiểm tra tiến độ và giao việc tiếp. Nhận **cả M0→M4**, không dừng sau ACK, một fix hoặc PR đóng gói. Owner vẫn OpenCode local theo work order20; Antigravity đã thu hồi. Codex review/integration/narrative, Muse art/nativeVM, Qoder server; giữ ranh giới.

Đầu vào: PR101 head `66ddddf1e26a98c316f4ef8e02a0a071b53b703e`;140/140 original tests và13/13CI xanh nhưng producer đã phát hiện3finding. Đọc `Implementation/Reports/OPC13_Producer_Review_20261101_vi.md` và comment mới issue85/PR101 trước code. Gói20 chưa hoàn tất chỉ vì D3 report nói đóng gói.

## Nhánh/worktree và scope

Tiếp worktree `D:/Project/NGUMACHHUYENAN-opencode-player-ui-20261101`, root Qoder không chạm. **M0 sửa ngay branch/PR101 hiện tại**, mỗi fix có source+regression tests, không rewrite history hoặc sửa test cũ để xóa finding. Sau checkpoint M0 đã push, tiếp M1→M4 trên nhánh `opencode/opc-14-ui-runtime-hardening-20261101` từ head đã sửa, PR stacked target `opencode/opc-13-player-ui-takeover-20261101` nếu101 còn mở; nếu101 đã merge, fetch và target integration96 đúng dependency. Không tự merge main/#96/#101. Không reset/stash/clean WIP của user/agent khác.

Phạm vi chuyển giao20 giữ nguyên. Mở thêm: read-only generated catalog/runtime data **trong Resources/PlayerUI**, generator+tests riêng `Tools/PlayerUIData/**`, UI acceptance client/harness riêng `Client/Tests/PlayerUIAcceptance/**`, và test runner native `Client/Assets/Tests/PlayerUI/**` + asmdefs có review (không chỉnh gameplay assembly hoặc giả Unity). Chỉ hook nhỏ có review vào P1OnlinePanel để nối focus/narrative/settings. Không sửa Core/P1Client/P1Narrative, CSV canonical/XY/balance, server/DB/contracts, Muse asset/video, ProducerReview runner hoặc compiler OPC05b→12 đã bàn Codex.

## M0 — sửa3finding, giữ đúng yêu cầu

1. **OPCREV-01:** topmost modal chặn Space xuống lower layer; focused editor không skip cinema hoặc cast; blocked/consumed/no-modal tách rõ. Các layer có identity explicit, không dựa index nếu registry thay đổi; exception probe fail có hành vi an toàn và diagnostics, không tự cho phép gameplay. Input rearm khi thả phím, modal/pause/session transitions khớp P1GameplayInputGate. Một physical press chỉ một hành vi, không double-dispatch UI Toolkit và legacy Input.
2. **OPCREV-02:** dùng cùng projection/view transform cho renderer, gesture và clamp với actual viewport/aspect; halfY theo cùng uniform scale. Bounds360×84 zoom4 Y phải center30. MapId/floor generation thay đổi cùng bounds cũng reset stale pan/markers; disconnect/null state không giữ pan cũ. Chỉ dùng field đã có, không tự tạo topology/portal authority.
3. **OPCREV-03:** thống nhất HUD visibility từ connection+safe-area+pin, tránh cached policy bị RefreshVisibility writer ghi đè. Hidden liên tiếp, resize/full, rebind/two-doc và tracker transitions đều đúng. Trên viewport khả dụng phải có đường mở menu/settings (overflow/compact), không biến hide thành mất mọi quyền điều khiển.

Producer repro hai FAIL dùng actual pure-C# code ở `D:/Project/NGUMACHHUYENAN-tools/dispatch/opc101-review-20261101`; đọc được, không sửa runner/log của Codex để giấu lỗi. Bổ sung regression test trong suite của bạn rồi báo exactSHA/output trên101/85, tiếp phần độc lập chứ không dừng chờ.

## M1 — Settings/accessibility có consumer thật và layout dùng được

- Reduced motion/flash/input hints cần consumer trên **UI do bạn sở hữu** (cinema transitions/loading pulse/highlight/hotkey labels/tooltip), reset/reopen/rebind/two-document áp dụng nhất quán. Chức năng world VFX/camera shake ngoài scope vẫn unsupported rõ; không quảng cáo giảm mọi hiệu ứng thế giới.
- Text scaling phải có thể đọc, không clip nút/hộp thoại/list ở viewport nhỏ; ảnh hưởng labels/hardcoded sizes có chính sách nhất quán, không chỉ đặt root.fontSize rồi gọi hoàn tất. Scale tách document, không đổi PPU/logical camera/world zoom.
- Keyboard/tab focus order, focus trap và restore focus khi đóng modal, Escape/Space/Enter đúng text editing, labels/tooltips accessible; touch target hợp lý, scroll dài/multi-line và safe-area. Có fallback menu/overflow khi thiếu chỗ thay vì ẩn toàn bộ access. Desktop + landscape/portrait profiles có expected geometry, native measurements để Muse xác nhận.
- Không thêm toggle giả hoặc vòng xác nhận thừa vào user flow. Option chưa có consumer giữ disabled/preview kèm lý do ngắn, không ghi implementation vào UI người chơi.

## M2 — Catalog UI đầy đủ theo dữ liệu chuẩn

- Thay embedded hand-maintained subset bằng read-only catalog build **từ các CSV/schema đã có**, output version/digest/provenance dưới Resources/PlayerUI, không sửa canonical hoặc invent ID/stat/rarity/level.
- ItemTooltip/character/bag dùng một resolver; variant instance/base template resolution, requirements, binding/trade/durability/stack/slot/set effects chỉ hiển thị khi source có field. Unknown/unsupported tách rõ, không điền0 giả hoặc từ khóa UNRESOLVED cho người chơi.
- Generator deterministic, UTF-8, parser CSV đúng quoted comma/newline/escaping; duplicate canonical key phải fail, no path escape; tests against full canonical coverage, empty/malformed/unknown variants, stale digest và reproducibility. Catalog load fail không khiến UI mất túi đồ; fallback rõ và diagnostics không lộ secrets.
- Tôn trọng scope: đây là read-only UI projection, không thay ContentPipeline/BuildCandidates/quest activation hoặc gameplay balance. Data thật chưa đủ field thì report thiếu field, tiếp phần khác.

## M3 — Nghiệm thu client qua HTTP thật và fault/reconnect

- Viết acceptance harness client dùng P1Client+P1ClientAdapter+presenters thực (không fake transport) với server hiện có từ cùng integration checkout/commit phụ thuộc, không sửa Health/Core/endpoint để suite xanh. Có private ephemeral port/flags rõ, chỉ dừng process do harness tạo.
- P00-01: NPC snapshot reads không POST NPC interact; accept đúng NPC,3parcels→ready→turn-in; inventory/server receipts20COIN+onechest đúng một grant; journal/tracker update live, pin không wire.
- Faults có ý nghĩa: mất response turn-in sau commit→retry cùng pending request→no double grant, delayed snapshot sau close/rebind/NPC switch→no stale view, expired/disconnected→disable+recover snapshot không grant local, fullbag theo fixture/harness server hỗ trợ (thiếu seed API thì giữ UNVERIFIED, không invent endpoint).
- Không claimHTTP các route vẫn scripted. Không mutate database/server global hoặc mở public service. CI đúng dependency/source heads, tests >0 và artifacts failure rõ; mấtSDK dùng CI nhưng báo kết quả thực. Producer/narrative tests cũ giữ nguyên; thêm tests của bạn, không copy game engine thứ hai.

## M4 — Native tests chạy được trên Muse VM, không chỉ checklist

- Bổ sung actual Unity EditMode/PlayMode tests cho composition+twoUIDocuments+200Open/Close/rebind, callbacks/visual count plateau, input focus/modal priority, safe-area visibility và settings consumers. Dùng Unity APIs thật, không fake/stub Unity rồi gọi native PASS.
- Runner/menu/setup và command batchmode cho Unity6000.3.17f1; TestAssemblies/packages config chỉ review tối thiểu cần thiết, không nângUnity/model/package vô cớ hoặc cài engine trên máy yếu. Muse clone branch đầy đủ và hydrateLFS, không lấy sparsecheckout hiện tại làm native import proof.
- Packet Muse phải link executable test assembly/test names, branch/head, exact invocation, test-results XML/log/capture paths và expected metrics; thiếu máy giữ UNVERIFIED_NATIVE nhưng source/test có thể chuẩn bị ngay. Không treo toàn epic chờ Muse.

## Bàn giao liên tục

ACK current branch/HEAD/toolchain/checkpoint M0 tại85 rồi code. Commit/push từng checkpoint đủ review, PR title/body theo code cuối, Refs85/80/101 và workorder21. Từng tính năng gắn IMPLEMENTED/TESTED_HEADLESS/TESTED_HTTP/UNSUPPORTED/PREVIEW/UNVERIFIED_NATIVE. Run appropriate suite sau thay đổi; original baseline140+newregressions, syntax52 không bị gọi nativecompile. Metrics/coverage phải đo thật, không ghi expected24/24 hoặc nativecycles thayheadless.

`D:/Project/NGUMACHHUYENAN-tools/dotnet10/dotnet.exe` và Python đã có; `gh` dùng auth configured chuẩn, không trích xuất/in/nhúng secret. CLI phiên đang ở D:/opc05b-wt: **mọi shell/edit/test/git phải dùng workdir/absolute path tới worktree UI mới**, không tin cwd mặc định của session hoặc quote cả command sai shell. Dùng tool đúng định dạng để tránh lặp quoting lỗi. Quyền compiler cũ vẫn Codex; Antigravity không trở lại. Không dừng sau1fix hoặc gửi plan; nếu một phần blocked, ghi lỗi cụ thể và tiếp cả gói độc lập.
