# Antigravity — tiếp tục trọn AG-02 sau recheck18fc5b5

Issue vẫn **#85**, PR **#89**, nhánh `antigravity/ag-02-playable-ui-20261030`. Giữ #80/#83 để review nền tảng. Đây là phần triển khai tiếp của work order12, không thay bằng một epic mới hoặc reset công việc. **Nhận trọn M2→M4 dưới đây, không dừng sau ACK, sửa test, một panel hoặc một PR.**

## 1. Baseline mới và phần đã xác minh

#83 head `18fc5b5e0a1790c9c9614f8ea683c68012a1ced9` đã sửa original build, stale revision, BAG thiếu slot và cancellation-loading; local39/39tests và159core/audio/input/v2assertions đạt, syntax37files×3profiles0errors. NativeUnity/type/import/device vẫn UNVERIFIED. Không tiếp tục mô tả các lỗi này như chưa có fix.

#89 head `b30b2f5efe3be553b3542c76882b1735a5ce5c9b` đã merge nền tảng fixes, diff Client so với #83 rỗng ở snapshot. M2B/C và D/E/F vẫn cần implementation. Đọc `Implementation/Reports/Antigravity_UI_Recheck_20261030.md/.json`: diagnostic44tests41pass/3fail mới, cùng6findings AGR2. Mang branch hiện tại tiếp tục; nếu đã có commit sau snapshot, báo SHA và diff mới, không lùi lại baseline cũ.

Quyền file giữ work order12: Presentation, Unity/PlayerUI, Editor/PlayerUI, Resources/PlayerUI, PlayerUIChecks, own workflow/reports; `P1OnlinePanel.cs` chỉ composition/input hook nhỏ. Không sửa Online/Core, audio DSP/manifest, Server, OpenCode compiler/tools, Muse art/maps, canonical IDs/349XY. Tools/ProducerReview thuộc Codex; thêm regression trong suite riêng, không sửa evidence/runner lịch sử để làm xanh.

## M2 — hoàn chỉnh identity/lifetime, composition và Character/bag

### A. NPC context đúng wire và giới hạn asynchronous

Một context rõ `interactionTargetEntityId`, `sourceRecordId`, `npcTemplateId`, map/floor và viewGeneration/sourceRef. Runtime Bến Mưa có entity `ENT_MAN_BM_NPC_LYAN` / record `MAN-BM-NPC_LYAN` / template `NPC_LYAN`; Tạ Vân Khanh có cấu trúc IDs tương ứng. **Interact gửi entityID, accept/turnin gửi canonical npcID**, không gán recordId=entityId. Resolve qua read-only source mapping/catalog đúng version; không strip prefix/đoán từ label và không nhét NPC_TEST/Q-prefix handling vào code production để test pass.

Nếu context thiếu nguồn thì disable action và báo rõ; đừng hiện mỗi Tạm biệt như thể NPC không có quest. Giữ unknown/unrelated NPC không cho nhận/trả quest. Nối selected NPC từ world action vào `OpenWithNpcAsync` thật; nút nhận/trả gửi đúng command đúng một lần, goodbye chỉ close. Error/pending/retry phản ánh core đang có, không tạo transport/state/reward mới.

Clear/close/switch NPC/session đổi phải invalidate **presentation generation**. Callback đến muộn không ghi view mới/đã đóng, không làm sống lại panel; pending transaction/receipt ở Core vẫn giữ nguyên để retry/resync. Inventory/quest/NPC presenters cùng policy; cancellation xử lý bình thường, tránh async-void exception và fire-and-forget fault không ai quan sát. Test delayed response sau Clear, cancel, close/reopen và đổi actor, không chỉ exception ngay lập tức.

### B. Composition root chạy được và một input owner

Có editor builder/runtime factory/prefab trong Resources/PlayerUI tái tạo được, tạo đủ root/panels/buttonbar/store và chỉ một UIDocument được inject từ gameplay. Gắn hook đúng lifecycle, không phụ thuộc GetComponent trả ra component chưa bao giờ được tạo hoặc tự tìm document đầu tiên. Không chỉnh TitleBootstrap/scene Muse/global packages; hook nhỏ trong P1OnlinePanel được quyền như work order12. Builder manual phải có một thao tác editor và README rõ, không yêu cầu đoán Inspector refs.

Chỉ **một** nơi consume Escape; một phím pop đúng một modal ngay cả2stacked panels. Return-focus và neutral/release gate chặn click-through/hold-attack/joystick khi mở/đóng; parent HUD và child root không tự poll cùng key độc lập. Không pause shared world. Parent close/logout/expired phải dispose root lifetime, unregister callbacks, remove visual roots, release adapter/context; hide tạm thời khác dispose. Rebind không nhân callback/roots/GameObjects hoặc giữ actor cũ.

### C. Character, equipment, bag và tooltip thực

Implement Character panel vào router/root/buttons, đọc authoritative Self và EQUIPPED inventory, slot metadata source và missing-stat state rõ. ATK/armor/primary aliases không cộng đôi; unsupported equip/use/sort/salvage vẫn disabled có lý do, không fake mutation hoặc HP refill. Item names/rarity/tooltips từ read-only presentation metadata có sourceRef/version; thiếu metadata hiện fallback hợp lệ, không gọi UNRESOLVED là bản UI hoàn tất.

Túi100ô/4trang có pointer+keyboard selection, tooltip, filter projection không reindex, currency formatting không mất precision. Duplicate/out-of-range/overflow giữ **item view** hoặc diagnostics tray hiển thị được, không chỉ string warnings không ai render. Empty/loading/error/stale/uncertain phân biệt, session mới reset snapshot/selection đúng ownership. Fullbag READY và receipt-refresh failure giữ core policy.

Giao M2 bằng code + tests + setup builder + report; PR #89 có actual Client diff, giữ dependencies #83→#51. Sửa nền tảng chung đúng #83 trước nếu cần, mang fixes sang #89 có kiểm chứng; không force-push hoặc merge hộ.

## M3 — hành trình khám phá, map, cinema và settings/accessibility

Hoàn toàn bộ AG2-D/E của work order12, không đợi lời giao lại:

- Journal active/completed/objective text/counters/pin, greetings/quest stage/error copy và reveal gates từ nguồn hiện có. Dữ liệu flag/clue chưa có contract thì preview/unsupported rõ, không tự cấp reward/flag. P00-01 là tuyến online đã có evidence; các quest sau chỉ mở khi server thật hỗ trợ.
- Map extent/units/source version, pan/zoom/clipping/live revision refresh, floor/map/session switch, viewport rectangle và NPC/quest markers theo audience; waypoint local có nhãn. Không đổi world camera hoặc tự coi topology đã reviewed.
- Cinema overlay state machine loading/playing/skip/ended/fallback/dispose, subtitle và media refs của Muse; skip/replay không phát reward, không pause shared world. Chưa có video/trigger contract thì harness preview có nhãn và fallback source, tiếp phần khác; không lấy concept làm video đã giao.
- Settings áp dụng qua adapters thật từ startup/reload (volume/UI scale/text), scope rõ cho toàn UI thay vì chỉ scale cửa sổ settings. Toggle chưa có implementation disabled/labeled đúng; reducedFX giữ telegraph. Safe area16:9/20:9, text Việt dài/cỡ lớn, keyboard/touch, contrast và HUD skill arc6ô giữ nguyên.

Giao M3 một hoặc nhiều PR stacked đủ review, có screenshots/video **nếu** thật sự chạy engine; chưa có Editor thì source tests/layout model và native packet, không fake screenshot.

## M4 — actual journey/fault coverage và native handoff

1. Giữ39author checks hiện đạt, thêm AGR2 identity/late-result/one-Escape/generation/rebind/overflow và tests qua concrete P1ClientAdapter bằng scripted transport có request assertions. Không chỉ dummy transport never-used rồi gọi adapter integration pass.
2. Scenario P00-01 từ selected NPC→accept→3packages→READY→turnin→receipt/inventory refresh qua UI presenter/command binding thật, có exact server/client/content SHA khi chạy HTTP. Template/entity/record assertions phải đi qua serializer đúng. Lost response/correlation/retry cùng payload/idempotency, fullbag, stale snapshot và session expiry đều có oracle.
3. Native Unity6000.3.17f1 khi có môi trường: compile/import/playmode, mộtUIDocument/visual roots, nested modal1Escape,200lần open/close/reconnect không leak/double callback, PC/mobile keyboard/touch safe area. Máy không có Unity thì đưa builder/checkpoint/hướng dẫn+known gaps cho Muse VM ở #1 sau khi code đã đủ, không yêu cầu PC chủ dự án cài Unity hoặc dừng cả epic.
4. Cập nhật reports `AG02_*` và PR body đúng actual state, dependency/head/test results/native unverified. Viết đủ clone→tests→setup→scenario→known limitations dưới10bước. Không đóng #80/#85 hoặc tự merge khi chưa Codex nghiệm thu.

## Nhịp làm việc

Comment nhận tiếp tại #85: exact currentHEAD, milestone đang code, phạm vi files, expected first handoff và blockers cụ thể. **Tiếp tục cả M2/M3/M4 trong phiên làm việc**, checkpoint/push/PR sau milestone rồi làm tiếp phần độc lập khi chờ review; không trả lời xong kế hoạch rồi dừng. Yêu cầu Muse/Qoder qua issue với ID/field/kích thước cụ thể, không sửa file owner khác để vượt gate.
