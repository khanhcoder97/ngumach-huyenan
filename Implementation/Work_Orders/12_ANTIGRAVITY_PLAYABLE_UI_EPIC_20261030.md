# Antigravity — AG-02: UI chơi được, hành trình và khám phá

Issue nhận việc mới: https://github.com/khanhcoder97/ngumach-huyenan/issues/85 . Giữ #80 mở cho AG-01 và sửa PR #83; milestone AG02 ghi `Refs #85`, không tự đóng hai epic bằng một PR scaffold.

Ngày giao2026-10-30 theo yêu cầu chủ dự án tiếp tục sau commit AG-01. **Nhận trọn AG2-A→F; không dừng sau ACK, một file hoặc một PR.** Review exact head AG01 `6e8394dc540a18b8a87cce07c94e9c4e8dbde06c` ở `Implementation/Reports/Antigravity_UI_Review_20261030.md/.json`: CHANGES_REQUIRED, original build fail, diagnostic37tests29pass/8fail. Không coi AG-01 đã nghiệm thu.

Nhánh tiếp theo: `antigravity/ag-02-playable-ui-20261030`. Code baseline là AG01 head trên, cộng commit dispatch chứa work order này. AG01 fixes vẫn push đúng nhánh PR #83 trước; đưa các commit fix sang AG02 bằng merge/cherry-pick có kiểm tra, không force-push hoặc bỏ WIP. PR AG02 đầu base `antigravity/ag-01-player-ui-20261030` nếu #83 chưa merge; ghi #83→#51, retarget có kiểm chứng khi dependencies đã merge.

## 1. Phạm vi và quy trình

Giữ quyền AG01: `Online/Presentation/**`, `Online/Unity/PlayerUI/**`, `Online/Editor/PlayerUI/**`, `Client/Tests/PlayerUIChecks/**`, `Client/Assets/Resources/PlayerUI/**`, workflow riêng, handoff và reports `AG02_*`. Cho phép thêm prefab/bootstrap/presentation assets **trong `Client/Assets/Resources/PlayerUI/**` và editor builder thuộc PlayerUI**, metadata hợp lệ; không sửa scene/asset Muse hoặc TitleBootstrap.

`P1OnlinePanel.cs` được sửa composition/input hook nhỏ để init bằng client+UIDocument thật, biết player modal, xử lý Escape/close/dispose và refresh binding. Không rewrite polling/combat/transport/audio; không sửa `Online/Core/**`, Qoder server/contracts, QODER Remote persistence, OpenCode tools/compiler, global packages/ProjectSettings, canonical IDs/349XY. Proposal rõ khi cần vượt quyền; phần độc lập tiếp tục ngay. Codex giữ ownership `Tools/ProducerReview/**`; muốn thêm regression thì thêm vào test suite riêng, không sửa runner lịch sử để xóa finding.

Nguồn bắt buộc: work order09/10, review AG01, DEC019/021/023, UI/Inventory/Settings/Map/Narrative/Cinema specs hiện có trên main, cùng core client baseline thực. Không tự đồng nhất code main với full server stack. Chỉ P00-01/basic/MK03 có bằng chứng client HTTP ở baseline #51; các tính năng server mới phải pin exact review head, ghi feature gates rõ, không tự bật guard hoặc five-quest chain vì thấy PR mới.

## AG2-A — sửa toàn bộ finding AG01 và CI thật

Sửa AGREV01–11 trên #83: missing includes, real adapter coverage, asmdef GUID/dependency, plain-store FindObject constraint, inline styles, valid optional-slot BAG vs equipped/bank, stale guard, cancel/error/close lifecycle, NPC binding/action/association, integration/input, map/layout/settings và evidence. Không bỏ tests, dùng slot số trái schema, sửa expected revision5 hoặc biến lỗi thành silent pass.

Tests tối thiểu: rev10→5 giữ10; BAG slot omitted hiện được; EQUIPPED MAIN_HAND tách đúng; duplicate/out-of-range giữ diagnostics+item view; cancel/exception không loading mãi; close→open lại và late completion không ghi session mới; map fake Self đúng và concrete P1ClientAdapter thực; NPC unrelated không bật turn-in; typed choices chỉ gửi command tương ứng một lần; unknown capability disable có lý do. CI phải thực sự build/test all pure sources và không `|| true`. Cập nhật report historical→current chính xác, không sửa report producer baseline.

## AG2-B — composition và hành trình đầu game qua UI thực

Một composition root inject đúng UIDocument, adapter và stores, có editor builder/prefab hoặc runtime factory tái tạo được. Kết nối P1OnlinePanel bằng hook nhỏ; không yêu cầu người nhận tự đoán hàng chục Inspector refs. Không tìm UIDocument đầu tiên rồi gắn vào panel người khác. Init/dispose/idempotent/rebind đúng, remove visual roots và callbacks, session expired/log-out/reconnect không trộn actor.

Luồng từ gameplay: mở túi/journal/map/settings bằng click/touch/hotkey→NPC đúng mục tiêu→nhận P00-01→counters từ server→trả quest một lần→receipt→inventory refresh. Client đã có `AcceptQuestAsync/InteractAsync/TurnInQuestAsync/RetryPendingAsync`: dùng cùng client và pending command, không API mới hoặc reward local. Khi chưa có cho quest tiếp theo, disable có text nguồn, không giả unlock. Giữ modal mở không pause shared world, chặn move/cast khi UI chiếm focus, Escape close-top, quay focus đúng và chờ nhả phím/pointer trước gameplay. Kiểm input thật qua adapter, không chỉ test Stack<T>.

## AG2-C — nhân vật, equipment và túi đạt UX

Thêm Character panel thực từ authoritative Self/inventory equipped; phần profile/stat chưa có field phải ghi thiếu, không tự tính ATK/DEF từ tên/ảnh. Equipment slot view, tooltip item có source/display/rarity/stack/durability/location/version; compare chỉ khi vector source đã resolve và alias không double-count. Equip/use/sort/split/salvage chưa có endpoint phải disabled rõ, không làm fake mutation.

Grid100ô4×25 có selection bằng pointer/keyboard, focus/tooltip, search/filter đúng projection (ẩn/mờ theo policy rõ mà không reindex slot), diagnostics/overflow view, unknown templates không biến mất. Snapshot giữ readonly/copy cần thiết, item selection theo instanceId qua refresh/page/filter. Fullbag questREADY, committed+refresh_failure không gửi thưởng lại. Currency không làm tròn hoặc mất precision khi format. Có empty/loading/error/stale/offline states phân biệt.

Nối metadata trình bày qua read-only resource catalog có sourceRef/version; dùng OpenCode candidate khi available hoặc lookup giới hạn có provenance từ nguồn chuẩn. Không viết compiler/canonical source thứ hai, không regex thoại thành quest graph và không gọi UNRESOLVED là completed UX.

## AG2-D — journal khám phá, NPC và bản đồ theo fantasy

Journal cho người chơi hiểu mục tiêu/cốt truyện đang biết: active/completed, objective text/counter, chọn/pin tracker, đọc lại đoạn đã mở nếu có authoritative flags, giữ reveal gates. Những clue/choice không có server contract thì preview có nhãn/unsupported, không tự mở lore/quest/reward. Nối ít nhất lời chào, stage P00-01 và lỗi/retry từ textKey/source chuẩn; không hardcode tất cả NPC dùng cùng lời/cho mọi quest.

Map dùng extent/units/projection versioned; pan/zoom UI, clipping, player/camera rectangle, landmark/NPC/quest icons từ audience/metadata hợp lệ, waypoint local có nhãn rõ. Cập nhật theo snapshot revision khi đang mở, reset khi map/floor/session đổi. Candidate topology vẫn candidate; không tạo auto-navigation hoặc portal giả. Hồ sơ HUB_WIDE và combat giữ nguyên; zoom mapUI không zoom camera gameplay. Settings/UI text không dùng thông tin implementation trong flow người chơi trừ trạng thái dev có nhãn.

## AG2-E — cinema presentation và accessibility/settings có tác dụng

Trong phạm vi PlayerUI, triển khai state machine video overlay có manifest binding/source/capability rõ: loading→playing→paused(local presentation nếu cho phép)→skip/ended→disposed; missing/failed media dùng text/still fallback có source. Skip/ended/replay không phát reward hoặc quest event, không pause shared world. Trigger là event/story flag có contract đã review; nếu chưa có thì harness preview riêng có nhãn, không tự trigger cinematic bằng quest name. Muse giữ video/subtitle/stems; không tạo/crop asset thay Muse hoặc báo clip chưa có đã chạy. Đi tiếp phần settings/journal nếu media chưa bàn giao.

Settings: versioned local prefs + apply adapters thực cho UI scale/text size và audio volume hiện có khi được hook; unsupported toggle disable rõ. ReducedFX không che telegraph, reduced flash/motion không sửa mechanics. Áp dụng safe area desktop/mobile landscape16:9/20:9, text Việt dài/cỡ lớn, keyboard focus và touch targets; overlay không che skill arc6ô hoặc joystick ngoài lúc modal cần block. Không đổi engine/aspect logical render/PPU hoặc DSP.

## AG2-F — kiểm thử từ clone sạch và nghiệm thu

1. CI xanh **đúng HEAD**, đủ test discover/count/output, build cả concrete adapter; regression cho toàn finding. Giữ test baseline core/audio/input và syntax checks hiện có; syntax pass không thay Unity type compile.
2. Fault tests qua actual P1Client transport với delayed/lost/duplicate response, stale revision, expired/reconnect/cancel/late completion, retry cùng payload/idempotency; tách fixtures khỏi live HTTP. Có scenario hỗ trợ P00-01 thật với exact server SHA khi môi trường cho phép; không gọi fake adapter tests là online acceptance.
3. Native Unity6000.3.17f1 import/type compile/playmode khi có máy: UIDocument init, input/modal/focus/touch,200lần mở/đóng/reconnect không nhân roots/callbacks; PC+mobile layout screenshots/video/log. Nếu máy không có Unity thì giao code/builder/tests đầy đủ, ghi UNVERIFIED và gửi packet exactSHA cho Muse VM ở #1; không dừng cả epic để chờ Editor.
4. Báo cáo `AG02_*`: SHA/base/dependency, feature matrix live/fixture/preview/unsupported/unverified, lệnh/output/exit, hướng dẫn setup dưới10bước, missing Muse assets/API và proposal. Không ghi “Live tested” cho file chỉ viết xong.

Milestones PR: (A) correctness #83; (B+C) composition/character/bag; (D) journal/NPC/map; (E+F) cinema/settings/accessibility/fault+native handoff. Chờ review milestone trước thì làm phần độc lập tiếp, không tự merge hoặc đóng #80. Update issue AG02 mới sau mỗi mốc và khi blocker cần quyết định; không mở thêm hệ thống market/guild/crafting khi vòng UI này chưa có evidence.
