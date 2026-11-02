# OPC-13 Muse Native Packet — Player UI takeover verification handoff 20261101

Packet chuyển gói kiểm chứng native từ OpenCode LOCAL (không có Unity trên máy) sang Muse VM.
Đây là packet YÊU CẦU để chuyển các mục `UNVERIFIED_NATIVE` về trạng thái đã-verify; hiện KHÔNG phải bằng chứng native. Không mục nào được coi "native-pass" trước khi Muse trả lại theo template capture ở mục 10.

## 1. Identity — exact branch / SHA / toolchain

| Mục | Giá trị |
|---|---|
| Repo | https://github.com/khanhcoder97/ngumach-huyenan |
| Branch kiểm chứng | `opencode/opc-13-player-ui-takeover-20261101` |
| Base của PR #101 | `codex/story-gameplay-integration-20261031` |
| Head tại thời điểm tạo packet | `6070292` (commit trước packet-file này; packet là docs-only) |
| Chuỗi commits phải hiện diện | `defee37` A1 → `9355e32` B1 → `e7e4352` B2+B3 → `209faeb` C → `6070292` D1 |
| Unity | **6000.3.17f1** (đúng phiên bản dự án) |
| Worktree sparse từ phía OpenCode | KHÔNG đủ để đối chứng: thư mục `Client/Assets/Resources/PlayerUI` rỗng trong worktree — Muse phải chạy trong full checkout, không đổi asset/hash, không thay placeholder. |

Baseline mà Muse phải thấy trước các case: headless suite local **140/140 PASS**
(`dotnet test Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj -c Release`);
UnitySyntaxCheck **52 files × 3 symbol profiles, 0 errors**. Hai run này là headless — KHÔNG phải bằng chứng Unity compile/render; vai trò của Muse là phần native cho mọi mục còn lại.

## 2. Chuẩn bị (Builder / Menu / Setup / Hierarchy)

### 2.1 Builder quality-gate
File: `Client/Assets/Scripts/Online/Editor/PlayerUIBuilder.cs` (Editor-only, `#if UNITY_EDITOR`)
- Menu: `Tools/Ngu Mach/Setup PlayerUI in Scene` **hoặc** `Ngu Mach/UI/Setup PlayerUI in Scene`.

Steps:
1. Mở scene gameplay mặc định (không mở scene khác kèm UI cũ).
2. Chạy menu Setup ở trên; xác nhận host được tạo mới hoặc reuse đúng `PlayerUI_Host` (hoặc reuse GameObject của `P1OnlinePanel` đã tồn tại).
3. Kiểm tra Inspector `PlayerUI_Host`: `UIDocument` có mặt; `panelSettings` KHÔNG null (builder resolve `Resources/PlayerUI/DefaultPanelSettings` — asset trong worktree sparse có thể rỗng, Muse chạy full checkout phải thấy asset thật; nếu log null thì lấy PanelSettings duy nhất trong scene).
4. Compile project (lần 1 sau checkout): 0 errors; KHÔNG có CS0111/CS0103 (các lỗi latent cũ đã fix: MapPanel/QuestJournalPanel `OnDestroy` đôi, `Math` thiếu `using System;`).
5. Chạy Setup lần 2 và lần 3 (idempotent): không sinh `PlayerUI_Host` mới, không sinh thêm `PlayerUI_Root`, không có duplicate components.

**PASS**: 3 lần setup idempotent; log `[PlayerUIBuilder] PlayerUI successfully setup on host: <name>`; 0 compile errors; status bar không trôi.
**FAIL**: bất kỳ compile error; panel/host phát sinh mỗi lần Setup; `panelSettings` null mà builder không giải quyết/thông báo.

### 2.2 Hierarchy yêu cầu
```
PlayerUI_Host                       (GameObject + UIDocument + P1PlayerUIHook; nếu scene đã có P1OnlinePanel cùng host — host được reuse)
└── PlayerUI_Root                   (PlayerUIRoot + 8 components dưới, không khác)
    ├── InventoryPanel
    ├── CharacterPanel
    ├── QuestJournalPanel
    ├── NpcDialoguePanel
    ├── SettingsPanel
    ├── MapPanel
    ├── PlayerUIButtonBar
    └── CinemaOverlay
PlayerUI_Host → PlayerPrefsSettingsStore (1 component duy nhất)
```
(fallback: nếu scene đã có `P1OnlinePanel` — builder dùng chính GameObject đó làm host, không tạo host thứ hai.)

**PASS**: đúng cây ở trên, 1 UIDocument, 1 PlayerPrefsSettingsStore, không dupe.
**FAIL**: bất kỳ phần tử thừa/thiếu; UIDocument thứ hai dưới host.

## 3. Device Profiles + Safe-area (Package C HUD)

PanelSettings: `referenceResolution` 1920×1080, scaling mode theo project default — không có native runtime record nào từ phía OpenCode, Muse ghi lại panelSettings thực thi trong scene làm baseline.

Profiles chạy (Device Simulator):
1. iPhone 13 Pro Max (portrait + landscape với Dynamic Island).
2. iPhone X (notch edges).
3. Pixel 5 (punch-hole).
4. iPad Pro 11 (safety margin lớn).
5. Desktop 1920×1080 không inset.

Steps mỗi profile:
1. Kết nối P1 (session hoạt động, HUD hiển thị).
2. Ghim một quest đang làm (journal → nút ★) — tracker hiển thị nhãn "★ <tên quest>".
3. Quan sát HUD theo policy:
   - Desktop 1920×1080, iPad, landscape iPad → **Full** (bar + tracker cùng hiển thị, scale 1).
   - iPhone landscape (usableW < bar + tracker) → **Compact** (tracker ẩn, bar scale 0.85).
   - iPhone portrait → Compact cùng điều kiện; viewport cực nhỏ (simulation) → **Hidden** (bar tự ẩn, theo policy).
4. Xoay orientation nhiều lần: HUD re-evaluate đúng; không dupe bar/tracker; không item tràn qua notch/edge.
5. Ghim quest trong Compact mode vẫn được ghi (nhãn "★" trong journal), tracker hiện lại khi Full trở lại.

**PASS**: mode đúng từng profile; scale ≥ 0.6 (chữ còn đọc); tracker chỉ ẩn đúng tier; không spill qua safe area; pin không mất.
**FAIL**: bar/tracker tràn qua notch; tracker vẫn hiện trong Compact; HUD biến mất ở landscape iPad (Full profile); chữ scale < 0.6 không đọc được.

## 4. Hai document độc lập (Package A/C requirement)

Steps:
1. Tạo 2 GameObject host (A, B), mỗi host `AddComponent<UIDocument>` và gọi `PlayerUIFactory.Create(host, doc)` — hai `PlayerUIRoot` độc lập.
2. Chạy runtime đồng thời với cùng một session adapter (mỗi document một PlayerUIRoot, chung adapter).
3. Trên doc A: pan/zoom map — chỉ doc A đổi; doc B không đổi.
4. Trên doc A: đổi UiScale trong Settings — chỉ rootVisualElement của doc A scale; doc B giữ nguyên.
5. Close toàn bộ doc A (rebind hoặc dispose): doc B vẫn hoạt động không lỗi.

**PASS**: state không dính giữa hai doc; console không in event cho doc B khi thao tác doc A; không có panel của doc A còn trong visual tree sau close.
**FAIL**: scale seeping sang doc B; panel trùng hiển thị ở doc B; event chạy hai lần.

## 5. 200-cycle Player UI lifecycle (native)

Steps:
1. Editor script PlayMode chạy 200 vòng: ghim quest → mở Túi → đổi tab items → mở quest journal → ghim quest khác (hoặc bỏ ghim xen kẽ) → mở map → zoom 1→2 → pan → close từng panel theo thứ tự trộn lẫn giữa các vòng.
2. Mỗi cycle: capture `doc.rootVisualElement.panel.QueryAll<VisualElement>` đếm instances mỗi panel type.
3. Cuối mỗi 25 cycles: `Resources.UnloadUnusedAssets` + ghi GC memory.

**PASS**: 200 vòng chạy không exception; mỗi panel type chỉ còn 1 instance cuối; GC memory không tăng unbounded; hành vi mỗi cycle giống cycle đầu.
**FAIL**: instance panel tăng mỗi vòng; exception bất kỳ; memory tăng không kiểm soát; hành vi diverge sau N cycles.

## 6. Cinema overlay (Package A/C)

Steps:
1. Play `CIN_001` (đăng ký có sẵn): state Playing + nhãn Preview Harness.
2. Escape để skip — chỉ qua orchestrator (overlay không poll keys).
3. Scene không tồn tại → Fallback với note trung thực; không gán quest, không grant.
4. Tự kết thúc theo duration → Ended; canSkip false.
5. Skip trong journey P00-01: quest state trên server KHÔNG đổi (không grant, không tự cấp).

**PASS**: states và labels chính xác; skip chỉ 1 hành vi; server quest state không đổi sau skip.
**FAIL**: skip hành vi khác spec; skip grant hay đổi quest state; `Time.timeScale` bị đổi (pause server world).

## 7. Narrative / NPC dialogue (Package B)

Steps:
1. Open dialog với NPC gần nhất trên map (ví dụ NPC_LYAN ở Bến Mưa): compose từ snapshot — câu thoại từ narrative provider, KHÔNG POST nào trong lúc compose (xem network profiler).
2. Hoàn thành Accept → thu đủ 3 parcels (gặp node đóng gói qua `/p1/world/interact` — CHỈ node, không NPC) → turn-in với NPC_TAVANKHANH: dùng đúng template id server; transport log KHÔNG chứa `/p1/world/interact` cho bất kỳ NPC nào.
3. NPC vắng khỏi world snapshot: dialog mở kèm lý do unavailable — Accept/TurnIn disabled, "Tạm biệt" vẫn bấm được.
4. NPC không trong catalog (templateId lạ): nhãn UNRESOLVED hiển thị chính xác, không fabricated dialogue.

**PASS**: không POST NPC interact; accept/turn-in dùng template id đúng; state unavailable/unresolved hiển thị đúng; snapshot compose không crash.
**FAIL**: bất kỳ POST `/p1/world/interact` cho NPC; fabricated dialog; Accept bấm được khi NPC absent.

## 8. Gameplay input qua modal orchestrator (Package A)

Steps:
1. Không modal mở: Escape không có hành vi (không có panel nào đóng); Space hoạt động như gameplay.
2. Cinema đang mở: Escape → skip cinema; Space → cũng chỉ skip cinema (KHÔNG tấn công).
3. Panel (Túi) đang mở ngoài cinema: Escape → đóng panel; KHÔNG skip cinema; Space KHÔNG tấn công.
4. HUD details mở chồng nhiều modal: Escape đóng HUD detail trước tiên.
5. Text-field đang focus (nếu có): Escape trong text field không lọt ra đóng panel; focus phải consumer trước orchestrator.
6. Lặp 200 lần mở/đóng qua bar buttons: mỗi bấm chỉ 1 hành vi (khớp 200-cycle unit test ModalOrchestration).

**PASS**: thứ tự ưu tiên narrative > cinema > player panels > audio > HUD details đúng; Space chỉ tiêu thụ ở cinema-skip; không "attack khi modal đang mở".
**FAIL**: một lần bấm có ≥2 hành vi; gameplay attack leak khi panel mở; focus state bị leak.

## 9. Map pan/zoom native feel (Package C)

Steps:
1. Open Map: player marker chính giữa khi vừa mở; cảnh báo topology "⚠ Topology chưa được xét duyệt" hiển thị thật.
2. Drag map theo nhiều hướng: view di chuyển theo drag; clamp khít bounds (rìa phải/trái/dưới/trên đều không vượt); sau khi thả tay window vẫn nằm trong bounds.
3. Nút "Về vị trí của bạn": view recenter về vị trí player; zoom giữ nguyên.
4. Zoom slider extremes 0.25–4; thao tác pan vẫn sống khi mutation đang pending (giữ zoom slider disable đúng policy).

**PASS**: drag mượt không sốc; clamp khít; recenter đúng; pan available cùng mutation pending.
**FAIL**: drag trôi ngoài bounds; recenter không đúng hiện player ở giữa; pan bị khóa cùng pending mutation.

## 10. Capture / log template per case (muse trả lại)

```yaml
case_id: <2.x / 3.1 / 5 / 6.3 / ...>
branch: opencode/opc-13-player-ui-takeover-20261101
unity: 6000.3.17f1
unity_build: <build metadata id>
result: PASS | FAIL
evidence:
  - trace/logs/<case>.log        (Editor.log snippet, full path)
  - screenshots/<case>.png       (bắt buộc với pan/safe-area/scale)
  - unity_profiler.txt           (HUD details, FPS thực tế và snip Tool UIElements debugger)
metrics:
  compile_errors: 0
  panel_instances_after_200_cycles: {inventory: 1, character: 1, quest_journal: 1, settings: 1, map: 1, bar: 1, cinema: 1}
notes: |
  <chi tiết bất kỳ ngoại lệ>
```

NHẮC NHỞ CRITICAL: nếu một case FAIL — không đánh dấu UNVERIFIED→done. Reply packet này với case_id FAIL + reason, OpenCode sẽ kiểm pre-check lại headless và chưa merge PR #101 vào main (mọi merge là quyền của Codex).

## 11. OPC-14 M4 — Executable Unity native tests (new)

Branch/head: `opencode/opc-14-ui-runtime-hardening-20261101` (stacked on `opencode/opc-13-player-ui-takeover-20261101` @ `21ce171` + M1/M2 commits). Unity **6000.3.17f1**. Hydrate full checkout (LFS) — sparse checkout is NOT native import proof.

Test assembly: `NguMach.PlayerUI.Tests` (asmdef: `Client/Assets/Tests/PlayerUI/PlayerUI.Tests.asmdef`, Editor-only).
Test files:
- `Client/Assets/Tests/PlayerUI/PlayerUICompositionTests.cs` — two-UIDocument independence, 200 open/close/rebind, rebind idempotency.
- `Client/Assets/Tests/PlayerUI/PlayerUIInputFocusTests.cs` — modal priority / Space blocking.

Exact invocation (batchmode, EditMode):
```
Unity.exe -batchmode -nographics -projectPath <full-checkout> -runTests -testPlatform EditMode -testResults TestResults/playerui-editmode.xml -logFile Logs/playerui-editmode.log
```
PlayMode (if PlayMode tests added later):
```
... -testPlatform PlayMode -testResults TestResults/playerui-playmode.xml -logFile Logs/playerui-playmode.log
```

Expected metrics:
- EditMode: 0 compile errors, all tests pass, 0 failures.
- Composition: panel instance count stays 1/type after 200 cycles (no unbounded growth).
- Native still UNVERIFIED until Muse runs and returns template (section 10) with XML/log paths.

Note: these are source-level tests; they are NOT native PASS until executed on Muse VM. Headless 156/156 + syntax 55x3 are not Unity compile proof.

## 12. Update 2026-11-03 — OPC-14 O1–O4 landed (head 8f27d3a)

- Branch/head: `opencode/opc-14-ui-runtime-hardening-20261101` @ `8f27d3a` (PR #103), stacked on PR #101.
- Headless: `dotnet test PlayerUIChecks -c Release` = **171/171 PASS** (was 167); `UnitySyntaxCheck` = **58 files × 3 profiles, 0 errors**; generator tests **9/9 PASS**; `generate_ui_catalog.py --check` = up to date; HTTP acceptance = **73 assertions PASS, exit 0**.
- Native test graph: `PlayerUI.Tests.asmdef` now references `NguMach.Client` (not `Assembly-CSharp`) + TestRunner/NUnit; runtime/editor asmdefs added under `Client/Assets/Scripts/Online`. `PlayerUICompositionTests` calls `Initialize(real adapter, doc)` and asserts route + visible tree before the 200-cycle soak; `PlayerUIInputFocusTests` uses `ModalOrchestrator` from the `Presentation` namespace.
- Consumer wiring (O1): PlayerUIRoot loads `Resources/PlayerUI/ui_item_catalog` before panel init, injects a per-session `UiItemResolverSession` into bag/character, owns exactly one `SettingsConsumerBinder` per open session (created after SettingsPresenter, disposed before teardown), traps Tab/Shift+Tab on the top modal's real focusController, and restores focus on close. PlayerUIButtonBar adds hotkey labels + a real "..." overflow menu (HudOverflowPolicy) keeping Settings reachable. CinemaOverlay/panels observe reduced motion/flash/text scale with observable changes.
- Catalog (O1): generator entry digest = `sha256(json.dumps({field:value for FIELDS}, sort_keys=True, ensure_ascii=False))`; overall = `sha256(json.dumps(list of entry digests, ensure_ascii=False))` in Python list format `["a", "b"]`; cross-file identical shared rows kept once with first-file provenance (136 rows), conflicting duplicates fail; `UiCatalogLoader.VerifyDigest` recomputes every entry + overall + provenance; `--check` is read-only and fails on drift.
- HTTP (O2): 73 assertions against a private server — lost first turn-in -> `mutation_outcome_unknown` + pending; `RetryPendingAsync` reuses the same body/key and clears pending; receipt `COMPLETED` + 20 COIN + 1 `EQ-MK-CHEST-T1-R-COMMON`; repeat new key -> `invalid_transition` with no double-grant; delayed reread + rebind stable; real 404 `session_not_found` (legacy `useWorldV2:false`) moves to Expired. Full-bag remains **UNVERIFIED** (no server seed/capacity contract).
- CI (O4): `antigravity-player-ui.yml` runs the generator tests + read-only `--check`, the mandatory private-server HTTP runner, uploads `TestResults/`, no optional `P1_BASE_URL` skip.
- Native Unity stays **UNVERIFIED_NATIVE** until Muse runs the packet; full-bag stays **UNVERIFIED**. Do not claim native PASS.
