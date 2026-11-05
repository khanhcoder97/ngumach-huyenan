# OPC-14 review và phần việc thực thi còn thiếu — 01/11/2026

PR101 M0 head21ce1712f; PR103 reviewed head `7a706a394b1f337dd1440b66246fa7a7e61ce364`, stacked target OPC13. OpenCode đã có5commit kể từ66ddddf: M0 sửa lỗi +4commit trên103. Phiên đang idle sau checkpoint, chưa có bằng chứng tiếp tục code. Antigravity không trở lại.

## Kết quả đã xác minh độc lập

Original `PlayerUIChecks` **156/156PASS**, generator **6/6PASS**, syntax runner **55files×3profiles,0errors**, không Unity types/import/playmode. Producer re-test dùng actual compiled class trên7a: Space khi narrative+cinema open không còn skip cinema sau; map centerY đúng30 tại bounds360×84/zoom4/pan20;2case PASS. Source HUD đã gộp display writer, không return trước apply Hidden. Native visibility chưa xác minh. Giữ bằng chứng cũ không sửa.

PR101 current CI15SUCCESS; PR103 head7a CI11SUCCESS nhưng **không có PlayerUIChecks/native/catalog/acceptance gate trên head này**. Workflow UI không nhận PR target `opencode/opc-13-player-ui-takeover-20261101`, và chưa bao phủ các path mới. Không lấy11green thay bằng chứng tất cả phần mới đã kiểm tra.

Catalog JSON có2656ID chuẩn =556master+2236variant−136shared. Cả136shared rows hiện giống nhau; không phải lỗi duplicate canonical. Generator read_csv đang bỏ duplicate cross-source mà không đối chiếu nội dung; cần allow identical shared row có provenance, fail khi cùngID khác dữ liệu. Đã dùng csv parser thật, không thấy tên bị rỗng ở dữ liệu hiện hành.

## OPC14REV-01 [P1] M1 policy chưa có runtime consumers

`rg AccessibilityPolicy|FocusNavigationPolicy|HudOverflowPolicy` chỉ thấy definitions/tests/csproj, không consumer trong Unity source. Reduced motion/flash/hints, focus trap/restore, overflow menu chưa nối với view;14policy tests không chứng minh các chức năng tác động UI. Diff103 không thay Unity player panels/HUD. Cần actual consumers trong SettingsPanel/CinemaOverlay/PlayerUIButtonBar/PlayerUIRoot/P1OnlinePanel với lifecycle và two-document binding; không dùng wrapper hoặc thêm test của hàm NOT như bằng chứng runtime.

## OPC14REV-02 [P1] Generated catalog chưa được resolver/UI sử dụng

Không có loader hoặc callsite `ui_item_catalog` trong client runtime; ItemMetadataResolver vẫn embedded subset. 2656entries trên đĩa chưa làm tooltip/character đầy đủ. Output FIELDS hiện bỏ weapon_power/armor/primary-secondary stats/affix/socket/set/hidden-effect/source fields đã có trong CSV. Cần typed read-only loader/schema/provenance/digest + resolver dùng chung, inject vào bag/character, không invent balance; preserve source fields đủ hiển thị. Tests phải đi từ generatedresource→realresolver→formatter, including base/variant/malformed/stale digest/fallback. Cross-source overlap136identical được phép; conflicting duplicate phải fail.

## OPC14REV-03 [P1] HTTP harness chưa có scenario/assertion, luôn exit0

Program.cs:18/22 chỉ in hướng dẫn, không transport request/assertion. Với `P1_BASE_URL=http://127.0.0.1:1` (không có server), chương trình vẫn exit0 và in “executable assertions land with M3 follow-up”. Đây là skeleton chưa triển khai, không chỉ thiếu máy chạy. Lệnh producer `dotnet run --project Client/Tests/PlayerUIAcceptance/PlayerUIAcceptance.csproj -c Release` với env trên; log `D:/Project/NGUMACHHUYENAN-tools/dispatch/opc103-review-20261101/unreachable-server.log`.

Không có server trong sparsecheckout không phải blocker source: `git sparse-checkout add Server/Health`, build/read existing server từ cùng branch với .NET10 đã có, **không sửa Health**. Có sẵn reference `Tools/ProducerReview/review_narrative_gameplay.py` và `Client/Tests/NarrativeChecks` dùng real HTTP + private process; đọc để dùng đúng profile, không sửa producer runner. Missing/unreachable server phải nonzero khi bắt buộc chạy, hoặc code SKIP riêng có CI check >0assertions, không xanh im lặng.

## OPC14REV-04 [P1] Native test source hiện không khớp API/assembly và cycle no-op

- PlayerUIInputFocusTests.cs:14 tạo `ModalOrchestration` không tồn tại; class đúng ModalOrchestrator trong namespace Presentation, ModalLayer cũng chưa import.
- CompositionTests.cs:60–62 gọi `rootA.CloseTopPanel()` không tồn tại (root có CloseTop, hook mới có CloseTopPanel).
- Factory chỉ tạo/bind refs; tests không Initialize(adapter,doc). OpenPanel() return ngay khi adapter null, nên dù đổi tên method, vòng200 hiện chưa mở panel/rebind phiên; chỉ đếm child GameObject không đo visual elements/callback leak.
- `PlayerUI.Tests.asmdef` reference NguMach.Client.P1 không tồn tại. `rg --files Client -g '*.asmdef'` hiện chỉ test asmdef mới; runtime ở predefined assembly. Test-framework dependency/TestAssemblies/NUnit wiring và .meta cần rõ. Syntax runner chỉ Scripts, không compile Assets/Tests;55syntaxPASS không phát hiện các lỗi semantic này.

Cần sửa graph/actual API, real initialized UI tree và assertions hoạt động, đúng native EditMode/PlayMode strategy. Chưa chạy Unity trên máylocal, chưa gọi nativePASS. Thêm minimal runtime/test asmdefs và declared TestFramework theo scope workorder22; giữ UI/source ownership, không làm game/transport clone hoặc fake Unity để xanh.

## Quyết định

M0 nhận ở mức headless/source đã recheck, native chưa xác minh. M1 mới policy, M2 mới data artifact, M3 skeleton, M4 có source cần sửa; **không nghiệm thu OPC14 toàn bộ và chưa merge101/103/main**. Tiếp gói lớn execution22 A→E để hoàn thành các phần trên và CI/runtime evidence. Không mở OPC15/features mới để bỏ dở21. Agent báo đúng IMPLEMENTED/POLICY_ONLY/GENERATED_NOT_BOUND/NOT_IMPLEMENTED/UNVERIFIED thay “M0→M4 hoàn tất”.
