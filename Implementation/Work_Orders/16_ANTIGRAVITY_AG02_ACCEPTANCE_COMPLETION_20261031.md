# Antigravity — hoàn thiện và nghiệm thu AG-02, ngày 2026-10-31

Theo lệnh chủ dự án, nhận **trọn gói R0–R6** dưới đây và triển khai liên tục. Không dừng sau ACK, một lỗi, một panel hoặc một PR. Đây là phần còn thiếu của AG-02; không mở AG-03 để bỏ việc chưa hoàn thành.

## Baseline và quyền sửa

Giữ nhánh `antigravity/ag-02-playable-ui-20261030`, PR #89, issue #85/#80. Head đã review: `a0bb0aba7953ae9181390d27e4c2386d20a453dd`; dependency: #89 → #83 → #51. Nếu HEAD đã tiến, báo SHA mới và diff; không reset, force-push hoặc tự merge. Sửa trên #89; chỉ backport #83 khi shared base thực sự cần sửa.

Đọc `Implementation/Reports/Antigravity_AG02_Review_20261031.md/.json` và ba JSON bằng chứng. Đã xác minh 71 author tests, 5 hồi quy cũ và 159 core assertions đạt. Kiểm tra bổ sung: **84 ca, 73 đạt, 11 lỗi**. Probe binding factory có CS0246 hai lần và CS1501. Syntax 47 file × 3 profile đạt nhưng không thay cho kiểm tra kiểu Unity. Các fix NPC canonical và presenter.Clear đã đạt; không làm lại như chưa có.

Quyền sửa giữ work order 12/14: `Presentation/**`, `Unity/PlayerUI/**`, builder thuộc `Online/Editor/**`, `Resources/PlayerUI/**`, `PlayerUIChecks/**`, workflow và báo cáo riêng. `P1OnlinePanel.cs` chỉ được thêm hook nhỏ cho composition, selected NPC và input/lifecycle. Không sửa Core/transport/audio DSP, server/DB/contracts, artwork/scene/Animator của Muse, 349 tọa độ canonical hoặc `Tools/ProducerReview/**` của Codex. Thêm regression vào suite riêng; không sửa bằng chứng cũ để làm xanh.

Main `a793aed89e8c5fc152f60e8ead30c7cf25280978` có tooling nội dung/map của Codex (#92/#93). Fetch/read có bảo toàn stack; không kích hoạt candidate còn blocked. Master/Rarity catalog là nguồn tên và phẩm chất. Nếu cần export metadata, gửi Codex yêu cầu field/ID cụ thể; không xây compiler hoặc registry cạnh tranh.

## R0 — dựng được UI đúng host/document

Đóng AGR3-01/02 trước:

- Sửa namespace của `PlayerPrefsSettingsStore`, số tham số `SetPanelReferences` và gán `cinemaOverlay` thực. Compile inventory phải bao gồm factory, root và editor builder. Probe API dùng synthetic Unity stubs chỉ là kiểm tra hẹp, không được báo native Unity PASS.
- Một thao tác setup phải xác định host thật của `P1OnlinePanel`, UIDocument có PanelSettings hợp lệ và settings store. Builder hiện tạo host rời trong khi HUD chỉ tìm hook trên chính host của HUD. Nối hai đầu rõ ràng.
- Inject cùng document/store vào tất cả panel. Không `FindFirstObjectByType` để gắn/scale UI bất kỳ. Factory phải sử dụng document argument, chạy lại không tạo root/hook/store/document trùng. Menu thực và README phải khớp.
- Thiếu reference phải báo lỗi cụ thể và dọn phần đã tạo. Không sửa scene Muse, TitleBootstrap hoặc global ProjectSettings. Có thể tạo harness thuộc PlayerUI. Thiếu Editor vẫn sửa source và giao packet ngay; native ghi UNVERIFIED.

## R1 — vòng đời phiên và tương tác NPC qua giao diện

Đóng AGR3-03/04 và phần input của AGR3-10:

- Nối selected NPC từ authoritative world → HUD interact → hook/root → `OpenWithNpcAsync`. Interact gửi entity ID, accept/turn-in gửi template ID qua **cùng P1Client**. Không gửi Interact hai lần. Node/gather giữ route riêng đúng chức năng; mapping thiếu phải có trạng thái không hỗ trợ.
- Close, switch NPC, rebind và đổi phiên phải vô hiệu hóa generation của presentation. Inventory/Journal không nhận success đến muộn sau lifetime đã hủy. Không xóa pending mutation hoặc receipt của Core; giữ dữ liệu cũ có nhãn khi phù hợp. Tránh loading vô hạn và lỗi async không được quan sát.
- Root teardown phải gọi từng panel: unsubscribe presenter/callback, remove visual roots, clear adapter/context/cinema/settings bindings và giải phóng token. Phân biệt hide tạm với dispose. NPC hide/close phải dùng đúng generation policy.
- Một nơi điều phối input cho HUD/root/cinema. Một Escape chỉ đóng hoặc skip lớp trên cùng; Space skip không đồng thời attack. Modal/text focus chặn move/cast và chờ nhả controls trước khi trả gameplay, không pause shared world.
- Kiểm tra 200 vòng mở/đóng/reconnect bằng số root, callback và request thực. Dùng hai UIDocument để chứng minh UI chỉ gắn vào document được inject, không giữ actor cũ.

## R2 — catalog, Character và túi đồ đúng dữ liệu

Đóng AGR3-05/06/07/08:

- Lookup metadata bằng exact ID từ Master/Rarity, có sourceRef/version/hash hoặc read-only resource snapshot có nguồn. Không dùng `StartsWith` suy ra class, rarity, tên hoặc slot. REFINED/SPIRIT/ARCANE/RELIC phải hiện đúng Tinh/Linh/Huyền/Cổ Vật. Unknown lookalike không thừa kế metadata của món khác. Base template chưa chốt rarity không được giả thành Thường.
- Chỉ `location == EQUIPPED` được hiện đang mặc. Không dùng slot không phải số để kéo món trong BAG/BANK vào equipment. Kiểm slot alias riêng; duplicate/unknown giữ diagnostics thay vì overwrite im lặng. Không tự tính stats/HP refill hoặc bật endpoint equip/use/salvage chưa có.
- Unknown NPC không được tự gán entity = record = template. Chuyển Q1/QUEST_TEST/NPC_TEST sang fixture catalog inject từ tests. Bảo toàn assertions bằng dependency injection; không thêm test IDs vào catalog production hoặc nới expected để che lỗi.
- Túi 100 ô/4 trang phải có diagnostics/overflow tray giữ item view, gồm duplicate/out-of-range/fullbag. Filter chỉ đổi projection, không đánh lại số slot. Hoàn pointer/keyboard selection, focus, tooltip rarity/source/location/durability/version/stack và selection theo instanceId qua refresh/page/filter. Currency không mất precision; unknown item không biến mất.

## R3 — hành trình qua adapter thật và fault coverage

- Giữ 71 author assertions và 5 hồi quy cũ, thêm regression cho 13 producer acceptance cases. Dùng **P1ClientAdapter + P1Client + scripted IP1Transport** với assertions trên request thực. Không dùng DummyTransport không được gọi hoặc JourneyAdapter tự gán completed để chứng nhận integration.
- Kiểm tra selected NPC → interact entity → accept template → ba package interactions → READY → turn-in template → receipt → inventory/journal refresh. Assert command count, request ID/body/correlation theo contract. Refresh thất bại sau commit không gửi thưởng lại; retry giữ payload/idempotency.
- Bao phủ mất/trễ/trùng response, fullbag READY, stale revision, cancellation, đổi actor, expired/reconnect, close/reopen, unknown item/NPC và response cũ sau dispose. Dùng điều kiện và timeout có oracle; không chỉ sleep cố định.
- Khi chạy HTTP, pin exact client/server/content SHA và profile/gates. Dùng baseline P00-01 đã được hỗ trợ hoặc reviewed Qoder head, không tự merge server stack. Thiếu HTTP/native ghi đúng mức fixture/UNVERIFIED và tiếp phần độc lập. Không tự kích CIN_001 theo quest name hoặc completed state khi chưa có trigger contract.

## R4 — journal và bản đồ khám phá

Đóng AGR3-09:

- Pin phải gắn với quest ID cụ thể và có tracker hiện trên HUD, không chỉ một boolean. Nối objective text/counters, active/completed, lựa chọn và thông tin đã mở từ nguồn. Lore/đối thoại cần authoritative flags; thiếu flags/endpoint thì preview hoặc disabled rõ. Không regex lời thoại thành quest graph.
- Map có extent/origin/units/projection versioned theo nguồn, pan/zoom/clipping, camera rectangle và landmark/NPC/quest icons đúng audience. Local waypoint có nhãn; reset map/floor/session. Không dùng hệ số 4px/WU không nguồn hoặc biến candidate topology thành navigation/portal đã duyệt.
- Refresh theo revision/state, tránh dựng lại toàn bộ UI mỗi frame khi dữ liệu không đổi. Không sửa 349 placements; quy hoạch Thăng Long và migration bounds runtime vẫn tách rõ. Test projection tại corners/bounds và thao tác input khi có Unity.

## R5 — cinema, settings và accessibility có tác dụng

Đóng AGR3-10/11:

- Cinema cần manifest/source/capability và media adapter: loading, playing, pause nếu cho phép, ended, skip, failed, fallback, disposed. Missing media có text/still fallback có nguồn và nhãn preview; fallback phải tiến/skip được, không kẹt vì IsPlaying=false. Guard callback cũ và dispose/rebind.
- Preview chỉ mở từ entry có nhãn; live trigger cần event/story flag contract đã review. Không tự trigger theo tên nhiệm vụ. Subtitle/timecode lấy đúng nguồn; skip/replay không cấp reward/flag hoặc pause world. Input đi qua R1; không poll Escape/Space độc lập. Muse giữ video/still/SRT/stems.
- Settings load và apply từ init/reload trên đúng document/store/audio adapter, không chờ mở bảng Settings. Text size/input hints phải có tác dụng hoặc disable rõ. Reduced flash/motion không che telegraph hoặc đổi mechanics; không sửa DSP.
- Hoàn safe area desktop/mobile landscape 16:9/20:9, combat 640×360 và HUB_WIDE 960×540, tiếng Việt dài/cỡ lớn, scroll/focus/touch targets. UI scale không đẩy controls ngoài màn hoặc làm lệch hit bounds. Test prefs restart, hai document, text/scale lớn nhất. Chỉ giao screenshot/video native khi thực sự chạy engine.

## R6 — bàn giao toàn gói và tiêu chí hoàn tất

Commit/push sau mỗi milestone đủ review, giữ #89 → #83 → #51. Có thể tách PR stacked cho phần độc lập nhưng không bỏ R0–R3. Mở PR xong tiếp phần khác, không chờ giao lại từng panel.

PR body và AG02_* reports phải có feature matrix: source implemented / pure fake / scripted concrete transport / HTTP verified / preview / unsupported / native unverified. Bỏ claim toàn M1–M4 hoàn tất tới khi có evidence phù hợp; giữ report producer lịch sử và hashes.

CI đúng HEAD phải build/test pure sources và concrete adapter, công bố count/cases/output, chạy khi đổi editor/root/factory/hook. Hướng dẫn clone → tests → setup → scenario dưới 10 bước. Không `|| true`, bỏ test âm thầm hoặc lấy syntax pass thay type compile.

Sau khi sửa source, gửi packet exact SHA/builder/menu/scene/settings/profile và known gaps cho Muse VM tại issue #1. Nghiệm thu Unity 6000.3.17f1 gồm import/type compile/playmode, hai document, nested modal, 200 cycles và layout desktop/mobile. Không yêu cầu máy yếu của chủ dự án cài Unity hoặc dừng implementation vì thiếu Editor.

Chỉ Codex review/merge/đóng #80/#85 sau nghiệm thu. Thiếu API/art gửi integration request có ID/field/source cụ thể rồi tiếp phần độc lập; không mở thêm market/guild/crafting ngoài epic này.

**ACK tại #85 với current HEAD, toolchain, phần đang code và checkpoint đầu; sau đó bắt đầu R0/R1 và tiếp toàn R2–R6 trong phiên làm việc.** Không trả lời chỉ kế hoạch hoặc chờ lệnh sau một fix.
