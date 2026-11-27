# OpenCode LOCAL — OPC-14 EXECUTION: hoàn thiện UI hoạt động thật A→E

## Nhận trọn gói, không mở tính năng mới thay việc dở

Chủ dự án yêu cầu kiểm tra tiến độ và giao nhiệm vụ lớn tiếp. Lần này nhận **cả A→E để hoàn thiện OPC14**, thay checkpoint dừng chờ review sau7a706a3. Không mở OPC15 thêm menu/tính năng mới. Đọc report `Implementation/Reports/OPC14_Progress_Review_20261101_vi.md`, workorder21 và reviewPR103. Antigravity đã thu hồi, OpenCode local giữ owner UI; Codex review/integration/narrative, Muse art/nativeVM, Qoder server.

Working directory tuyệt đối `D:/Project/NGUMACHHUYENAN-opencode-player-ui-20261101`, branch `opencode/opc-14-ui-runtime-hardening-20261101`, PR103 stacked target OPC13. Current baseline7a706a394b1f337dd1440b66246fa7a7e61ce364; M0 fixes21ce171 đã recheck2producer cases PASS,156author tests +6generator tests PASS. Giữ M0, không quay về66ddddf. Không reset/stash/clean rootQoder/WIP hoặc các worktree11/12. Không tự merge101/103/96/main.

## A — Runtime consumers + focus/overflow/layout, không chỉ policy

1. Nối SettingsPresenter.Current + OnChanged qua binding theo session/document tới actual owned UI consumers. ReducedMotion phải tác động transition/pulse thuộc UI; ReducedFlash tác động highlight/flash thuộc UI; ShowInputHints phải ẩn/hiện hotkey labels và survive reopen/reset/rebind. World camera/VFX ngoài scope vẫn unsupported, không quảng cáo giảm mọi hiệu ứng game.
2. Focus trap/Tab/ShiftTab/focus restore phải bắt và apply tới actual focusController/UIElements, dựa visible/enabled controls trong top modal. Editor con của TextField/Slider/nested fields và haiUIDocuments không leak Space/Enter xuống cinema/gameplay. Không sửa Core/narrative module để né lỗi; hook nhỏ review trong P1OnlinePanel/PlayerUIRoot được phép.
3. HudOverflowPolicy phải có consumer/menu “…” thật mở được cả5panel khi viewport chật, touch/keyboard dùng được; không hide mất lối Settings. Giữ HUD skill arc/top-down/PPU/world zoom. Resize/safearea/textscale cùng layout phải clamp/scroll và không chặn gameplay ngoài panel.
4. Có tests cho binding lifecycle và view decisions trên actual presentation pipeline, không chỉ assert boolean NOT. Native focus/geometry đo ở Muse; source có thể nối ngay khi không có Unity local. Không tính code unused thành feature completed.

## B — Generated resource → loader → resolver → UI

1. Read-only typed schema+loader từ Resources/PlayerUI/ui_item_catalog.json, có version/digest/provenance/failure diagnostics; một resolver thật dùng chung bag/character/tooltips. Không duy trì embeddedsubset thành đường chính khi catalog hợp lệ.
2. Giữ toàn bộ field canonical cần hiển thị: tên/category/slot/class/level/rarity/binding/trade/stack/durability; weapon_power/armor/primary-secondary/affix/socket/set/hidden/source nếu source có. Display-only, không thay balance/grant/equip authority hoặc tự mở hidden effect chưa có unlock state. Giá trị thiếu unknown/unsupported, không0fake.
3. Canonical union đang2656keys từ556master+2236variant với136sharedidentical. Cho phép identical shared record và giữ provenance cảhai; conflicting sameID/meaningfulfields fail rõ. Generator `--check` và atomic output (không ghi dở resource); CSV parser UTF8/quotes/comma/newline, deterministic/source digests, no paths outside intendedroots.
4. Test end-to-end generated file→actual loader/resolver→formatter cho toàn catalog coverage và vài item ngoài subset, base/variant resolution, malformed/truncated/duplicate/stale/resource-missing fallback. Assert UI consumers nhận đúng metadata, không chỉ count>2000 hoặc digest.length64. .meta đầy đủ/unique cho assets/source/tests mới.

## C — HTTP assertions thật + private server runner (bắt buộc làm, không để skeleton)

1. Mở sparsecheckout **chỉ đọc/build** bằng `git sparse-checkout add Server/Health` (cùng integration dependency đã có tronggit). SDK `D:/Project/NGUMACHHUYENAN-tools/dotnet10/dotnet.exe` có sẵn; build Server/Health/Health.csproj. Không cần càiUnity, không sửa Health/server/contracts/DB để tests xanh.
2. Dùng existing private ephemeral port/process + correct devflags theo `Tools/ProducerReview/review_narrative_gameplay.py`; không copy/gameengine mới, không sửa producer runner hoặc NarrativeChecks cũ. Implement executable PlayerUIAcceptance scenarios bằng real P1Client/P1ClientAdapter/presenters, HTTP requests thật.
3. Assert P00-01 NPC snapshot không POSTNPCinteract; accept đúngNPC;3parcels→ready→turnin; tracker/journal update live; pin không wire;20COIN+onechest đúngmộtgrant. Lost response AFTER commit→retry samebody/key→stored receipt/inventory no duplicate. Delayed read sau Close/rebind/NPC switch→no stale UI, expired/disconnect disables và reload snapshot khônggrantlocal. Fullbag nếu thiếu supported seeding giữ UNVERIFIED riêng, không block scenarios làm được và không invent endpoint.
4. Missing/unreachable server hoặc zero assertions phải fail khi CI bắt buộc HTTP. Nếu có local optional skip dùng explicit status/exitcode và CI rejectSKIP. `P1_BASE_URL=http://127.0.0.1:1` phải nonzero, không return0 sau inREADME. Runner log clientHead/serverHead/source/binary digests/profile/assertioncount/exitcode và chỉ dừng process mình tạo. Không killservice user hoặc mởpublicserver.

## D — Native source compile đúng và test có tác dụng

1. Sửa actual API: ModalOrchestrator/Presentation imports; root.CloseTop thay methodkhôngtồntại. Initialize real factory/root bằng adapter/session vàUIDocument có panelsettings đúng trước khi OpenPanel; assert expected visible root/route/pin/state sau mỗi hành vi để phát hiện no-op.200cycles gồm Open/Close/rebind thật, VisualElement count/callback subscriptions/nativehierarchy plateau, session/docA→B độc lập, không chỉ GameObject childCount.
2. Sửa assembly graph hợp lệ: test asmdef không được trỏ namespace như tênassembly. Được mở scope **minimal .asmdef/.meta cho Online/Core, Online/Presentation, Online/Unity/PlayerUI và Editor/test boundaries khi cần**, cùng Client/Packages/manifest.json/lockfile **chỉ TestFramework/dependencies thật cần cho test/runtimegraph**. Không đổi nội dung Core/P1Client/P1Narrative hoặc gameplay logic, không nângUnity/graphics packages. Runtime/presentation dependency phải dùng đúng assembly refs hiện hành, test NUnit/TestAssemblies rõ. Nếu chuyển graph, báo diff+dependency diagram+negative references; không giảUnity hoặc reference Assembly-CSharp theo cáchUnitykhônghỗtrợ.
3. Chọn TestFramework version theo Unity6000.3.17f1/projectlock hoặc official primary docs, ghi nguồn/version, không đoán package. Chưa có máylocal thì compile/import/playmode vẫn UNVERIFIED, nhưng source/refs/API phải tự đối chiếu và case runner có thật. Muse chạy batchmode EditMode/PlayMode với resultsXML/log/head; không claim PASS từ syntaxcheck. Có test focus/space/safearea/consumer/runtimecatalog hai-document, không chỉ purepolicy test đặt trongUnity.
4. Gửi packet Muse lên issue1 với exact currentSHA và test names/command/log template sau sourcecheckpointđủreview; không chỉ viết “Muse nhận” ở issue85. NhậnnativeFAIL thì fix phầncodeownership, tiếp phầnkhácđộc lập, không treo cảepic.

## E — CI phủ đúng PR stack, kiểm tra chất lượng bàn giao

1. WorkflowUI phải chạy trên PR103 target `opencode/opc-13-player-ui-takeover-20261101` và các target UI follow-up, push opencode/**, cùng paths mới Assets/Tests/PlayerUI, PlayerUIAcceptance, Tools/PlayerUIData, Resources/PlayerUI, .asmdef/manifest vàworkflow itself. Tránh chỉ serverCIgreen trênhead7a mà gọi UI đủPASS.
2. Job headless suite+generator `--check`/tests+build acceptance+realHTTP runner phải thực thi trên exacthead; publish JSON/TRX/logs khi fail. Negative fixture được test local/CI đúng cơ chế, không disable test đểcheckgreen. Native job dùngMuseVM/batchmodegói, thiếurunnergiữUNVERIFIEDkhông gánsuccess tự động.
3. Feature matrix ghi stage phân biệt: POLICY_ONLY / GENERATED_NOT_BOUND / IMPLEMENTED_WITH_CONSUMER / TESTED_HEADLESS / TESTED_HTTP / UNVERIFIED_NATIVE. M3 hiện NOT_IMPLEMENTED scenario, không “codewritten đủ chỉchưa cóserver”. M4 code/API graph cần sửatrướcnative. PR103title/body viết lại quanh final actualbehavior + exactcommands/output vàdependencies101/96; không chỉ paste4commitnames.

## Nhịp thực thi và bàn giao

ACK currentHEAD/toolchain + checkpoint A/B/C đang code tại85 và phiênlocal rồi làm ngay. Nhận cả A→E, commit/push từngcheckpoint đủreview, đangchờreviewthìtiếpphầnđộclập. Không kết thúc sau ACK/plan/skeleton hoặc mộtbugfix. Không merge/hồi sinhAntigravity/OPCcompiler cũ. GhCLI/authsẵnđượcphép, khôngextract/in/nhúngsecret/model/provider/permissions changes. Shelltool dùng absolute workdir; tránh quote toàn lệnh, gh -o, Unixhead hoặc python -c gây vònglỗi CMD. Dùng Read/Write tool và scriptfile khi cần. Nếu blocker thật, báo exacterror/API/field và tiếpphầnđộclập, không “thiếuUnity” để dừngHTTP/native-source/catalogbindings.
