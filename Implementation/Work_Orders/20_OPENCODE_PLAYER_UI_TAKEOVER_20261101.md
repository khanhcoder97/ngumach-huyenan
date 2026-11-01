# OpenCode local — OPC-13: tiếp nhận toàn bộ UI từ Antigravity

## Hiệu lực và nguồn lệnh

Ngày 01/11/2026, chủ dự án yêu cầu: “thu hồi quyền của antigravity và bàn giao về cho opencode trên máy”. Đây là chuyển quyền công việc có hiệu lực ngay, thay các work order09/10/12/14/17 và các comment cũ giao Antigravity. Antigravity dừng mọi sửa/commit/push/PR/merge hoặc điều phối; chỉ giữ nguyên trạng để tra cứu, gửi danh mục WIP nếu có. Không xóa nhánh/commit/WIP và không thu hồi quyền tài khoản GitHub chung của các agent.

OpenCode local nhận **toàn bộ phần code/presentation/UI integration còn lại**, không chỉ một lỗi hoặc một popup. Asset pixel/UI art/map/VFX/video và native Unity VM vẫn Muse; Codex giữ quản lý, narrative prose/Core/provider, producer tests/review và tích hợp. Không cài Unity trên máy yếu để bắt đầu gói này. Native không chạy được đánh dấu UNVERIFIED và gửi packet Muse, trong khi tiếp code/headless/CI.

## Baseline và nơi làm

- Repo: https://github.com/khanhcoder97/ngumach-huyenan . PR tích hợp #96, baseline `3e5089f543e2cc831de26b070bf23f867df95958`, CI16/16 đã xác minh.
- #89 đã merge vào AG01 tại418dc14, **chưa vào main**; PR96 chứa AG89 + narrative v3 + Qoder reviewed server. Không quay lại AG94fb hoặc cherry-pick toàn stack lần nữa.
- Nhánh triển khai: `opencode/opc-13-player-ui-takeover-20261101`, PR stacked target `codex/story-gameplay-integration-20261031`, `Refs #85, #80`; link work order/issue nhận việc mới của Codex. Không tự merge PR96/#83/#51/main.
- Worktree riêng do Codex chuẩn bị: `D:/Project/NGUMACHHUYENAN-opencode-player-ui-20261101`. **Không code/switch/reset/stash/clean trong root `D:/Project/NGUMACHHUYENAN`**: root thuộc Qoder và có temp_rgba.png/test.png của user. Không động D:/opc05b-wt-11/-12 hoặc các worktree agent khác.
- Checkout ban đầu có thể sparse, chỉ source/docs/tests; đây không là native import proof. Mở rộng sparse/LFS có kiểm chứng khi cần, không tự thay asset bằng placeholder hoặc đổi hash để validator xanh.

## Phạm vi code được chuyển

Được sửa `Client/Assets/Scripts/Online/Presentation/**`, `Client/Assets/Scripts/Online/Unity/PlayerUI/**`, builder `Client/Assets/Scripts/Online/Editor/PlayerUIBuilder.cs`, `Client/Assets/Resources/PlayerUI/**`, `Client/Tests/PlayerUIChecks/**` và workflow UI liên quan. Hook nhỏ có review ở P1OnlinePanel được mở quyền để nối UI lifecycle/input/narrative, không rewrite cả HUD/transport. Ghi PR diff phần hook riêng để Codex review.

Không sửa server/DB/Health, contracts/canonical ID/XY/balance; Core/P1Client/P1Narrative, narrative resource/prose/exporter, audio DSP, ProducerReview tools, Muse art/animation/tilemap, OpenCode compiler cũ đã bàn Codex. Nếu interface thiếu, gửi proposal API cụ thể, không tạo lớp client/transport/prose song song. Không sửa report/tool lịch sử để xóa finding.

## Trạng thái đã nhận — không làm lại mù

Đọc `Implementation/Reports/AG89_Producer_Merge_Review_20261031_vi.md`, integration README `docs/narrative/gameplay/README.md`, reports AG02 và work order12. Producer đã chạy104/104 (91author+13regression),49 Unity files×3 symbol profiles0syntax errors; đây không là native types/import/playmode.

Factory giữ UIDocument được inject và tracker callback Close/rebind đã được Codex sửa trong e48e148. Giữ các sửa này. 200cycles tác giả chỉ presenter/router, không phải native VisualElement lifecycle. Scripted transport là fixture, không phải live HTTP; fixture weapon/100CUR_GOLD không là canonical P00-01 reward20COIN+onechest. Matrix phải phản ánh đúng sự khác nhau.

## Gói A — Composition, lifecycle và input (làm trước)

- Dùng một owner điều phối Escape/Space cho player panels + cinema + narrative; một lần bấm chỉ thực thi một hành vi ưu tiên top modal. Không để CinemaOverlay tự poll và cùng lúc skip/close modal khác. Text field focus/cancel/pause/expired không lọt movement/cast/interaction xuống gameplay. Không pause server world.
- Document/settings được inject thật, không global FindFirst. Hai document độc lập không chồng visual tree, scale, callbacks hoặc panel routing. Initialize/Close/Dispose/rebind lặp được và không giữ view/pin/session cũ.
- Fault/lifecycle: kết quả async trễ sau đóng panel/đổi NPC/đổi session phải bị bỏ; pending mutation và lost response vẫn dùng đường retry hiện có, không phát command mới. Hủy UI không xóa receipt hoặc tự grant.
- Bổ sung tests có ý nghĩa trên real presenters/adapter và lifecycle abstraction nếu cần. Không dùng synthetic Unity stubs làm bằng chứng native; packet native phải đo tree/callback thật200cycles/two-doc trên Muse VM.

## Gói B — NPC/journal/character/bag và hành trình

- Giữ NPC route ưu tiên narrative v3 của PR96, đọc world/quest snapshot; không POST NPC vào endpoint world/interact (endpoint hiện chỉ parcel/node). Accept/turn-in dùng canonical NPC ID qua P1Client hiện có, không tự cấp flag/counter/reward khi đọc/skip/reply/video.
- UI NPC/journal/quick access dùng cùng narrative provider; không giữ catalog prose hardcoded thứ hai. Xử lý unknown/unsupported NPC/checkpoint đúng trạng thái, không mở khóa cảnh blocked hoặc post-bossCHOICE từ CSVACTIVE chung.
- Character/equipment/bag tooltips/rarity/requirements/slot diagnostics dựa catalog/schema thật. Thiếu field ghi unknown/unsupported, không điền balance giả. Giữ first-wins duplicate-slot diagnostics, full bag không mất vật phẩm.
- Tracker pin/unpin/completion/session reset/live objective update khớp journal. P00-01 flow đi LyAn→accept→3parcels→Ta turn-in→20COIN+chest; thao tác đọc không grant. Harness giả phải ghi SYNTHETIC; HTTP/live evidence tách riêng.

## Gói C — Map, settings và accessibility

- Map live refresh cả world v1/v2, bounds theo map_bounds.json và floor/map thực; pan/clamp/zoom, camera rectangle và waypoint UI chỉ hiển thị nếu có authority contract. Không tự phê duyệt topology/camera gameplay/tọa độ mới. Waypoint chưa có server support ghi rõ read-only/unsupported; không invent portal/pathfinding authority.
- UI/HUD giữ góc nhìn từ trên và ô skill vòng cung quanh attack; không đổi logical render/PPU hoặc zoom world để chữa UI scale. Quá tải HUD phải co/ẩn có kiểm soát theo safe area.
- Settings UiScale/text size/audio/reduced motion/reduced flash/input hints áp dụng trên document đúng và sống qua reopen/reset; không thay graphics preset giả hoặc quảng cáo nút có tác dụng khi chỉ lưu prefs. Keyboard/tab focus/labels và viewport landscape/mobile phải kiểm tra.
- Cinema skip/fallback/missing-video/timeout/close route an toàn, không grant story flags và không auto input vào gameplay. Video/art nội dung do Muse/Codex; OpenCode chỉ player/UI behavior.

## Gói D — Verification, bàn giao liên tục và native packet

- Sau mỗi checkpoint có actual source/test diff, commit/push vào nhánh riêng, PR vào96 với exactSHA, lệnh/output/CI links và giới hạn. Tiếp phần độc lập của cả A→D, không dừng sau ACK/plan/one fix hoặc đợi chủ dự án giao từng việc.
- .NET10 portable có sẵn `D:/Project/NGUMACHHUYENAN-tools/dotnet10/dotnet.exe`; Python sẵn. Giữ existing tests và regression fixtures, chạy UI/core/input/narrative checks phù hợp; syntaxcheck không được gọi là compile Unity. Dùng CI nếu thiếu runtime/provider, không thay test runner bằng stub để báo PASS.
- Feature matrix từng chức năng: IMPLEMENTED / TESTED_HEADLESS / TESTED_HTTP / PREVIEW / UNSUPPORTED / UNVERIFIED_NATIVE; không gộp “done all” khi có placeholder.
- Muse packet: exact branch/SHA, Unity6000.3.17f1, builder/menu/setup/hierarchy, profiles/safe-area/two-document/200lifecycle/cinema/narrative/input test steps, expected results, capture/log template và tiêu chí pass/fail. Có tên case và bằng chứng, không chỉ “nhờ Muse test”.
- Codex review/merge; giữ issue80/85 và epic mới mở tới khi scope/native được nghiệm thu. Không đăng production-ready hoặc metrics chưa đo. Không tự cài tool/model mới, đổi credentials/permissions hoặc dùng auto-approve mới.

## Nhận việc ngay

Đọc các comment cuối issue85/80 và work order này trước sửa code. ACK issue nhận việc với agent OpenCode LOCAL, worktree/branch/currentHEAD/toolchain và checkpoint A đang code. Đây là scope MỚI được chủ dự án cho phép; quyền cũ OPC05b→12 đã thu hồi về Codex vẫn giữ nguyên, không phục hồi PR99/branch compiler cũ. Bắt đầu triển khai A, rồi B/C/D liên tục.
