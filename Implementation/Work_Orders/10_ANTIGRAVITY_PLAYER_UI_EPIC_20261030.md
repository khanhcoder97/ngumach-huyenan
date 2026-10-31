# Antigravity — AG-01: bộ giao diện người chơi Bến Mưa

Issue nhận việc và bàn giao: https://github.com/khanhcoder97/ngumach-huyenan/issues/80 . PR milestone dùng `Refs #80`; epic chỉ đóng sau khi toàn bộ phạm vi đã nghiệm thu.

Nhận toàn bộ AG1→AG6, triển khai code liên tục và bàn giao qua GitHub. Branch: `antigravity/ag-01-player-ui-20261030`. Code baseline `92adee098fcb58acb5b280dcb167db9beecb8932`, PR #51 còn draft, native Unity/device chưa nghiệm thu. Đọc work order09 trước.

## 1. Mục tiêu và phạm vi file

Thay các khối hiển thị chẩn đoán bằng panel người chơi dùng được: túi, nhân vật, quest journal, đối thoại NPC, settings và bản đồ. Dùng `P1Client` hiện có để đọc/ra lệnh; không tạo một client HTTP hoặc gameplay state cạnh tranh. Core nguồn ở `Client/Assets/Scripts/Online/Core/`, Unity shell ở `Online/Unity/`; đừng đoán đường dẫn `Scripts/Core`.

Được tạo:

- `Client/Assets/Scripts/Online/Presentation/**`: view-model/presenter/data binding không phụ thuộc Unity.
- `Client/Assets/Scripts/Online/Unity/PlayerUI/**` và `Online/Editor/PlayerUI/**`: panel, input focus, prefab builder, binding; mỗi asset/thư mục Unity có `.meta` hợp lệ, GUID duy nhất.
- `Client/Tests/PlayerUIChecks/**`: test project độc lập tham chiếu các core cần thiết; không sửa test runner/core do Codex đang giữ.
- `Client/Assets/Resources/PlayerUI/**`: config localization/presentation có provenance, không chứa fake gameplay data.
- `Implementation/Reports/AG01_*`, `docs/production/Antigravity_Player_UI_Handoff_vi.md`; workflow riêng `.github/workflows/antigravity-player-ui.yml` chỉ chạy test thuộc gói.

Chỉ được sửa **`Client/Assets/Scripts/Online/Unity/P1OnlinePanel.cs`** nếu cần composition hook mở/đóng panel và chuyển focus; giữ thay đổi nhỏ, bàn giao diff riêng, không viết lại HUD/combat/polling/audio/input pump. Không sửa `Online/Core/**`, `P1ActorPresenter`, `P1UnityTransport`, `P1Audio*`, contract/server/tooling, scene/asset art Muse, global ProjectSettings/package versions hoặc workflows có owner khác. API thiếu thì gửi proposal; tiếp tục phần trình bày/test độc lập. Codex có thể review hook trước khi nối engine.

Nguồn phải đọc: `UI_UX_Spec_vi.md`, `Character_Equipment_Inventory_Spec_vi.md`, `Settings_Overlay_Spec_vi.md`, `Gameplay_HUD_Overlay_Spec_vi.md`, `HUD_Skill_Arc_Layout_vi.md`, `Hub_Wide_Camera_Profile_vi.md`, `Runtime_State_and_Catalog_Precision_vi.md`, `Narrative_Depth_and_Discovery_vi.md`, work order09 và tài liệu client v2 trong PR #51. CSV chuẩn chỉ đọc; lấy textKey/sourceRef, không rewrite canonical thoại.

## AG1 — presentation architecture và modal/input

Xây panel router, immutable view state, selection/scroll state, loading/empty/error/stale/retry/unsupported, focus return và modal stack. Một thao tác khi pending không gửi đôi; khi đóng modal/cancel chỉ đóng presentation, không hủy transaction đã server commit. UI mở phải nhả phím/joystick đang giữ qua input gate hiện có; mất focus, Escape, click xuyên nền và touch second finger có test. Không pause world nhiều người khi mở cửa sổ.

Adapter bọc read-only `P1Client.World/WorldV2`, `Quests`, `Inventory`, `State`, `HasPendingMutation`, `LastTurnIn`, `LastError/LastCorrelationId`; command dùng `ReadQuestsAsync`, `ReadInventoryAsync`, `AcceptQuestAsync`, `InteractAsync`, `TurnInQuestAsync`, `RetryPendingAsync`. Các DTO có field public, không tự giả định property/event không tồn tại. Giữ nguyên retry payload/idempotency của core, không tạo retry mới khi trạng thái uncertain.

## AG2 — túi100 ô và bảng nhân vật/trang bị

- Bốn trang, mỗi trang5×5; hiển thị stack, rarity theo metadata có nguồn, khóa/bind/slot/durability chỉ khi có field thật. Map slot theo contract; out-of-range/duplicate-slot/unknown-template báo rõ, không làm biến mất item. Search/filter là view projection, không đổi slot inventory authoritative.
- Click/touch chọn, tooltip có compare khi stat đã resolve; hỗ trợ keyboard focus và văn bản Việt dài. Đổi trang/filter giữ selection theo instanceId nếu còn tồn tại. Empty/loading/error không bị hiểu là mất sạch túi.
- `inventoryRevision` cũ không ghi đè mới. Toast thưởng là receipt, không cộng thêm vào snapshot. Turn-in đã commit nhưng refresh lỗi hiển thị cần đồng bộ lại, không grant lại.
- Equipment view đọc dữ liệu thật đang có; các slot/actions equip/unequip/use/sort/split/salvage chưa có endpoint phải disabled kèm lý do và contract proposal. Không tự thêm API hoặc trừ đồ/đổi stat local. Phần kiến trúc phải cho phép nối endpoint về sau mà không viết lại panel.
- Full bag giữ quest READY. HP/MP/armor hiện nguồn authoritative; không cộng alias primary/weapon_power/armor hai lần, không báo heal từ equip. Không suy stats từ icon hoặc tên đồ.

## AG3 — quest journal và tương tác NPC

Journal có nhóm active/completed, objective counters, step/branch metadata đã resolve, tracker pin local và target hint có source. Chỉ coi quest unlocked/playable nếu server/catalog xác nhận; hiện client HTTP evidence mới P00-01. Text coverage76quest không biến thành76quest runtime.

NPC panel: greeting/line/choice/service theo record ID và condition; nhận quest/trả quest/gặp NPC dùng core hiện có. Chọn đáp án không ghi story flag hoặc reward local. Giao diện hiển thị lý do out-of-range/wrong-floor/unavailable/bag-full và correlationId khi cần. Retry uncertain quay lại cùng pending command, không tự nhận quest khác.

Binding text phải dùng IDs và stage flags rõ; chỉ bật nhánh có dữ liệu. Preview hội thoại khác hoặc quest P00-02..05 nếu chưa executable phải ghi preview/unavailable. Thiếu quest definition/choice contract thì lập danh sách field cần và tiếp tục journal/tooltip tests, không regex text rồi tạo progression.

## AG4 — settings thật và accessibility

Implement local preferences có version/default/reset, UI scale, master volume qua adapter hiện có, text size, reduced motion/flash và input hints. Áp dụng setting chỉ qua API hỗ trợ thật; chỗ chưa có hook thì ghi unsupported thay vì nút bấm xanh giả. Không sửa DSP/audio manifests. Settings persistence là preference local, không là save nhân vật hoặc offline MMO progression.

Tạo layout desktop và mobile landscape có safe area: focus order, slider keyboard, thumb targets, contrast, labels không chỉ dùng màu. Modal central và cuộn nội dung đúng. Đóng settings quay về focus trước, không kích hoạt đánh thường. Mute/low FX không tắt dấu báo vùng nguy hiểm bắt buộc. Giữ gameplay skill arc6ô, không thay bằng grid.

## AG5 — bản đồ/journal khám phá và nối UI

Map view dùng coordinates/world extent có version; player marker/camera viewport theo snapshot, icon NPC/quest theo audience và metadata hợp lệ. Cho pan/zoom map UI, legend, waypoint presentation local; không giả vờ đã có auto-path, fog/discovery server hoặc portal đi được. Topology chưa review hiển thị trạng thái candidate, không sửa349tọa độ. Giữ world camera profile tách UI zoom.

Nối các panel bằng composition hook nhỏ, một nơi sở hữu input/modal, không dựng hai HUD cạnh nhau. Không cần tạo mới artwork; dùng Muse assets hiện có khi mapping đúng, placeholder hình học ghi nhãn dành cho dev. Các biểu tượng thiếu gửi yêu cầu kích thước/state cho Muse qua issue.

## AG6 — nghiệm thu và bàn giao toàn epic

Từ clone sạch chạy test .NET10 cho presenter/view state với synthetic fixtures có nhãn: đủ100ô/4trang, stack/duplicate-slot/bad ref, stale revision, unknown item, full bag READY, committed receipt + refresh failure, uncertain retry không gửi đôi, session expired, long text/diacritics, input modal/focus loss. Test hành vi qua adapter thực, không chỉ so hằng số layout.

Chạy lại `Client/Tests/P1CoreChecks/P1CoreChecks.csproj` và `UnitySyntaxCheck` trên phần code phù hợp để phát hiện regression; C#9 cho code đi vào Unity. Nếu máy có Unity đúng baseline: compile/import, tạo scene/prefab test, PC keyboard và mobile touch landscape16:9/20:9, screenshot/video từ engine kèm logs. Không có Unity vẫn hoàn thành code/presenter tests và ghi UNVERIFIED cho compile/type/import/playback; không gọi syntax-only là Unity pass.

Bàn giao tối thiểu ba milestone PR: architecture+bag; journal/NPC+settings; map+integration+evidence. Mỗi PR đủ feature/test/docs để review; chờ review vẫn làm phần độc lập. Mốc hoàn tất: code thực + reproducible checks + integration guide + feature matrix live/preview/unsupported/unverified. Không tự merge và không tuyên bố game đã hoàn chỉnh.
