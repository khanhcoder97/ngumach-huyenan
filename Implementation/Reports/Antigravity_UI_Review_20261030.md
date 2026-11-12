# Review bàn giao Antigravity AG-01 — 2026-10-30

**Kết luận: CHANGES_REQUIRED; chưa nghiệm thu AG-01, chưa merge PR #83.** Có source presenters và Unity panels thực, không chỉ tài liệu; tuy nhiên build/test, wire shape và runtime integration còn lỗi. Tiếp tục công việc theo work order12, không coi comment “HOÀN THÀNH” là bằng chứng nghiệm thu.

- PR: https://github.com/khanhcoder97/ngumach-huyenan/pull/83 . Head được review: `6e8394dc540a18b8a87cce07c94e9c4e8dbde06c`, base client `92adee098fcb58acb5b280dcb167db9beecb8932` (#51).
- Đã đọc diff, source presentation/Unity/test/workflow/handoff, issue #80 và CI exact head. Không sửa source nhánh agent trong lần review này.
- Local dùng SDK .NET10.0.403 riêng; không có Unity Editor. Các nhận định assembly/API Unity dưới đây là **static review đối chiếu API**, không phải native Unity compile/import/device evidence.

## 1. Bằng chứng thực thi

Lệnh gốc `dotnet test Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj -c Release` trên HEAD trên **exit1**, bốn CS0246 ở `PlayerUIChecksTests2.cs:37/48/59/74` vì csproj bỏ `NpcDialoguePresenter.cs`. [CI cùng lỗi](https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41054058580/job/124057003340). Suite chưa chạy được bằng project gốc; không được ghi “tests passed”.

Để tìm lỗi bị compile failure che, producer tạo project tạm **ngoài checkout**, đưa đủ Core/Presentation, giữ nguyên toàn bộ author tests và thêm4negative checks. Không chỉnh `.csproj`/source agent. Kết quả: **37 tests:29pass/8fail/0skip**. Trong33author tests có4fail (stale revision và3Map fixtures); cả4negative tests cũng fail. Đây là kết quả diagnostic project, không là sửa/pass của original csproj. JSON đính kèm có source fingerprints, counters và lỗi.

Tái tạo từ clone có report/tool này, `--root` trỏ checkout exact head cần review:

```sh
python Tools/ProducerReview/review_antigravity_ui.py --root <checkout-AG01> --dotnet <dotnet-executable> --output <report.json>
```

Runner build/test trong temporary directory, không sửa source checkout, exit1 khi có finding. `AntigravityNegativeChecks.cs` dùng FakeAdapter của author suite tại baseline này. Không gắn runner lịch sử này vào mọi PR rồi sửa expectation để báo xanh; agent bổ sung regression tests thực trong suite của mình.

## 2. Findings cần xử lý

| ID / mức | Vị trí source tại HEAD review | Hành vi và yêu cầu |
|---|---|---|
| AGREV-01 / P1 | `Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj:16–25` | Bỏ NpcDialoguePresenter; cũng không compile concrete P1ClientAdapter/real P1Client nên adapter không được test. Include đúng toàn bộ code pure C# cần thiết, không bỏ tests để xanh. |
| AGREV-02 / P1 | `Online/Presentation/NguMach.Client.Presentation.asmdef:5`; `Unity/PlayerUI/NguMach.Client.PlayerUI.asmdef` | GUID toàn0 không có target. Core/P1OnlinePanel đang ở predefined Assembly-CSharp, không có core asmdef; named assemblies mới dùng những type này không thể giả tham chiếu predefined assembly. Fix trong phạm vi own asmdef (ví dụ bỏ hai candidate asmdef cùng meta) hoặc proposal migration có dependency đầy đủ; không âm thầm di chuyển toàn core. |
| AGREV-03 / P1 | `SettingsPanel.cs:46–54`, `PlayerPrefsSettingsStore.cs:13`, `InventoryPanel.cs:97` | `FindFirstObjectByType<PlayerPrefsSettingsStore>()` dùng T là plain class, không kế thừa UnityEngine.Object; không thể attach class này như component. `IStyle.margin` cũng không là property API6.3. Dùng constructor/DI cho store hoặc component đúng thiết kế; dùng margin từng cạnh. Cần native type compile sau sửa. |
| AGREV-04 / P1 | `InventoryPresenter.cs:98–133` | Contract cho phép BAG không có slot; `slot` khi có dùng pattern chữ/underscore, không phải string số0..99. Code chỉ hiện item slot số và bỏ BAG hợp lệ khỏi grid; negative1 tái hiện. EQUIPPED slot MAIN_HAND bị báo out_of_range; negative2 tái hiện. Tách BAG/EQUIPPED/BANK; presentation indexing có nguồn/nhãn không sửa server slot, giữ item lỗi trong overflow/diagnostic view thay vì làm biến mất. |
| AGREV-05 / P1 | `InventoryPresenter.cs:36–57` | Với rev10→rev5: WithLoading làm IsLoaded=false, guard bị vô hiệu; author test StaleRevision_NotApplied thực tế nhận5 thay10. So snapshot đã giữ trước loading, bảo toàn state và notify đúng. |
| AGREV-06 / P1 | `InventoryPresenter.LoadAsync`, `QuestJournalPresenter.LoadAsync`; `PlayerUIRoot.cs:85–107` | Read throw/cancel khiến phase Loading mãi; negative3 tái hiện. Root Close đặt _closing=true, Open không reset, nên không mở lại được trên cùng component; callback/visual roots cũ không được teardown/rebind đầy đủ. Thêm finally/cancellation/generation ownership và test close/reopen/late result. |
| AGREV-07 / P1 | `NpcDialoguePresenter.cs:133–151`; `NpcDialoguePanel.cs:181–186` | npcId bị bỏ qua khi tạo choices, mọi quest READY được bật ở mọi NPC; negative4 tái hiện. Mọi nút choice lại chỉ gửi InteractAsync, kể cả nhãn Nhận/Nộp/Tạm biệt. Choice cần typed action+questId+npcId/source, binding có điều kiện; chỉ goodbye là close local, unsupported phải disable. `SetDialogue` không có caller trong source bàn giao, presenter chưa nối panel. |
| AGREV-08 / P1 | `P1OnlinePanel.cs:44–73/143–150`; `P1PlayerUIHook.cs`; `PlayerUIRoot.cs` | Hook/adapter chưa được gọi từ gameplay; không có bootstrap/prefab/UIDocument wiring chạy được. ModalOpen không biết PlayerUI, nên input vẫn có thể đi/đánh khi mở panel sau nối sơ sài; Escape hiện chỉ đóng details/audio. Dùng document được inject, composition hook thật, một input gate, close-top/focus-return/held-control release; không tìm document tùy ý hoặc dựng thêm HUD trùng. |
| AGREV-09 / P2 | `SettingsPresenter.cs:24–33`, `SettingsPanel.cs:99–121` | Sliders chỉ lưu preferences; chưa có apply hook volume/UI scale/text/reducedFX. UI không được trình bày setting đã áp dụng khi chưa có adapter thật; unsupported disable có lý do. Không sửa DSP/audio manifest. |
| AGREV-10 / P2 | `MapPanel.cs:48–52/130–148`; `InventoryPanel.cs:60–103`; `PlayerUIRoot.cs:109–117` | Map chỉ Refresh lúc Show, extent/projection thiếu, dùng cố định4px/WU và không pan/waypoint/clipping theo bounds. Panels fixed left/top/width; inventory cells không có selection callbacks, Character enum chưa có panel/binding. Đây là scaffolding chưa đạt responsive/accessibility/character scope của AG-01. |
| AGREV-11 / P2 | `PlayerUIChecksTests2.cs:98–129`; `.github/workflows/antigravity-player-ui.yml:56`; handoff/final report | Ba Map tests FakeAdapter.World đã có self nhưng property Self không được set, nên trả null/NRE: sửa fixture/adapter contract, không đổi assertion cho pass. Docs-check dùng `|| true` luôn xanh, không kiểm UTF8 như tên job; handoff gọi Live(tested) trong khi chưa chạy suite và còn failure. Bỏ swallow, cập nhật evidence theo exact SHA/feature state, không dùng số tests source làm số tests đã pass. |

Đường dẫn `Online/...` trong bảng thuộc `Client/Assets/Scripts/`. Negative test EQUIPPED ở đây kiểm phân loại slot hợp lệ, không chứng minh gear/equip command đã tồn tại. Map fixture failures không tự chứng minh adapter thật mất Self: concrete P1ClientAdapter đọc projection World.self; cần test qua adapter thật để phân biệt.

## 3. Tham chiếu Unity cho static review

- [Unity6.3 FindFirstObjectByType](https://docs.unity.com/en-us/engine/6000.3/script-reference/unityengine/object/findfirstobjectbytype): generic constraint T:Object; plain settings store không thỏa.
- [Unity6.3 IStyle](https://docs.unity3d.com/6000.3/Documentation/ScriptReference/UIElements.IStyle.html): margins là các cạnh riêng.
- [Unity6.3 assembly references](https://docs.unity.com/en-us/engine/6000.3/manual/programming-environment/script-compilation/assembly-definition-files/assembly-definitions-referencing): không dùng named asmdef như thể nó truy cập được predefined core.

## 4. Điều phối sau review

Antigravity sửa P0/P1 đúng PR #83 trước, lưu report cũ như lịch sử và cập nhật trạng thái, không tự merge/đóng #80. Work order12 giao tiếp **AG-02: hoàn thiện client UI có thể chơi và narrative UX**, gồm sửa finding→integration→character/tooltips→exploration/cinema presentation→fault/engine handoff. Nếu làm nhánh AG-02 riêng, phải mang fixes #83 sang và ghi dependency; không tạo hai bản presenter cạnh tranh. Không thay việc của Qoder server, QODER Remote DB, OpenCode tooling hay Muse art.

Issue AG02: https://github.com/khanhcoder97/ngumach-huyenan/issues/85 . Nhánh mới `antigravity/ag-02-playable-ui-20261030`; tạo nhánh/issue chỉ là dispatch, cần agent ACK/commit mới để xác nhận đã tiếp tục.
