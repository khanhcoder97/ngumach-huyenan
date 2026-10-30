# Review AG-02 Antigravity — 2026-10-31

**CHANGES_REQUIRED**, không merge #89 hoặc đóng #80/#85 tại checkpoint này. Reviewed exact head `a0bb0aba7953ae9181390d27e4c2386d20a453dd`, base #83 `18fc5b5e0a1790c9c9614f8ea683c68012a1ced9`; dependencies #89→#83→#51 chưa được nghiệm thu/merge. Diff đã có implementation thực; không còn báo AG02 chỉ ACK.

## Bằng chứng thực thi

| Phép kiểm | Kết quả | Giới hạn |
|---|---|---|
| Original PlayerUIChecks.csproj |71pass/0fail/0skip|Local net8 target chạy trên portable.NET10 với DOTNET_ROLL_FORWARD=Major; lần chạy không cấu hình đầu bị abort vì thiếu runtime8, không là source defect. CI riêng9/9SUCCESS ở exact head.|
| Prior followthrough runner không đổi |76pass/0fail =71author+5prior|NPC canonical/template controls và Clear→late interact đã sửa; không native/HTTP.|
| New acceptance runner |84total/73pass/11fail =71author+13new|Fake delayed-read isolates presentation lifetime; canonical variant expectations chép từ rarity CSV;2controls PASS. Không sửa checkout/author tests.|
| Factory source-API binding probe |CS0246×2 +CS1501|Compile actual factory với root signature trích từ actual source và synthetic Unity stubs; không gọi là full Unity compile.|
| Core/audio/input/v2 |55+43+15+46=159assertions PASS|Giữ core; diff AG02 không đổi Online/Core/server/art.|
| C#9 syntax |47files×3symbol profiles/0errors|Syntax không bắt unresolved names/overload, không thay type/import/device.|

Có tiến bộ thật: Character panel/authoritative HP-MP, canonical NPC wire mapping cho P00-01, generation Clear của NPC, UI scale lên document, map live refresh và cinema preview có nhãn. Các cải tiến này vẫn chưa là một luồng UI online được nghiệm thu. Test `Journey_FullP0001ProgressionFlow` là scripted **fake adapter**, tự gán trạng thái và gọi cinema.Play; không có chứng cứ actual wire/HTTP/reward receipt từ test đó.

## Findings và việc cần sửa

### AGR3-01 — P1: Factory không khớp API, bị bỏ ngoài test project

Nguồn: `Client/Assets/Scripts/Online/Unity/PlayerUI/PlayerUIFactory.cs:33/35/38; PlayerUIRoot.cs:47`.

Factory thiếu namespace NguMach.Client.Presentation cho PlayerPrefsSettingsStore, truyền8args trong khi SetPanelReferences có7. Probe compiler với signature trích từ source trả CS0246×2/CS1501. Đây là narrow API binding, không là native Unity compile.

Yêu cầu: Sửa namespace/signature và gán cinemaOverlay thật; compile inventory gồm factory/root/editor, chạy native khi có môi trường.

### AGR3-02 — P1: Builder/factory chưa nối đúng host và document

Nguồn: `Client/Assets/Scripts/Online/Editor/PlayerUIBuilder.cs:13; P1OnlinePanel.cs:55; Unity/PlayerUI/PlayerUIRoot.cs:42`.

Builder tạo PlayerUI_Host riêng; HUD chỉ GetComponent hook trên host của chính HUD. UIDocument mới chưa có PanelSettings/binding, factory bỏ document argument; nhiều panel FindFirstObjectByType thay injected doc. Menu thật Ngu Mach/UI/Setup khác README Tools/Ngu Mach.

Yêu cầu: Một thao tác setup xác định host/doc/PanelSettings; inject document/store vào mọi panel, giữ idempotence, không tìm doc bất kỳ. Không sửa scene Muse.

### AGR3-03 — P1: Selected-NPC journey chưa được gọi trong gameplay

Nguồn: `Client/Assets/Scripts/Online/P1OnlinePanel.cs:180; Unity/PlayerUI/NpcDialoguePanel.cs:54`.

HUD Interact gọi client trực tiếp, không gọi OpenWithNpcAsync; tìm reference chỉ có declaration. Root chỉ Show dialogue rỗng. Journey test dùng JourneyAdapter, tự thay Quests và gọi cinema.Play; chưa qua P1ClientAdapter/transport/receipt/inventory hay UI binding.

Yêu cầu: Nối NPC entity selection→hook/root/dialogue→command qua cùng client, node vẫn route đúng; thêm scripted transport + actual wire assertions và baseline HTTP nếu có.

### AGR3-04 — P1: Lifecycle chưa ngăn late reads hoặc dọn full UI

Nguồn: `Client/Assets/Scripts/Online/Presentation/InventoryPresenter.cs:43; QuestJournalPresenter.cs:36; Unity/PlayerUI/PlayerUIRoot.cs:104`.

Hai read presenter vẫn áp dụng success sau token lifetime đã cancel (2negative FAIL). Root.Close chỉ cancel/hide/null root fields; children giữ adapter/presenter/visual roots. Initialize lại BuildUI thêm roots/callbacks; hide NPC không Clear generation dù presenter.Clear đã sửa.

Yêu cầu: Lifetime/generation đúng cho mọi presenter; teardown child subscriptions/visuals/adapter/cinema; rebind session/actor;200cycles với oracle root/callback/command counts, không xóa pending core.

### AGR3-05 — P1: Item metadata prefix fallback làm sai phẩm chất và provenance

Nguồn: `Client/Assets/Scripts/Online/Presentation/ItemMetadataResolver.cs:104`.

4canonical variants REFINED/SPIRIT/ARCANE/RELIC thành base Kiếm/Thường; unknown lookalike ID thừa kế CLASS_MINH_KIEM/slot (5negative FAIL). Chỉ gắn sourceRef v1.0 không chứng minh hardcoded subset khớp rarity CSV.

Yêu cầu: Exact lookup Master+Rarity theo ID/version/source hash, unknown truthful; không StartsWith để suy ra stats/class/rarity, không dựng compiler thứ hai.

### AGR3-06 — P1: Character coi BAG/BANK là EQUIPPED

Nguồn: `Client/Assets/Scripts/Online/Presentation/CharacterPresenter.cs:48`.

OR non-numeric slot vượt location authoritative. BAG hoặc BANK với MAIN_HAND xuất hiện đang mặc (2negative FAIL); EQUIPPED control PASS.

Yêu cầu: Chỉ location EQUIPPED được vào equipment; slot validation riêng; duplicate/unknown có diagnostics, không tự overwrite hoặc suy ra đồ đang mặc.

### AGR3-07 — P2: NPC mapping giả identity và chứa test IDs production

Nguồn: `Client/Assets/Scripts/Online/Presentation/NpcContextMapping.cs:42/57/68`.

Unknown entity được gán record/template cùng input; registry còn Q1/QUEST_TEST/NPC_TEST mặc dù work order14 cấm.2negative FAIL. Mapping NPC canonical đã sửa và5prior regression PASS.

Yêu cầu: Unknown trả unresolved context không giả canonical IDs; map/floor/version/source rõ. Test catalog inject fixture trong tests, không thêm test IDs vào catalog production hoặc làm yếu assertion.

### AGR3-08 — P2: Túi đồ chưa đủ UX/diagnostics theo gói đã giao

Nguồn: `Client/Assets/Scripts/Online/Presentation/InventoryPresenter.cs:149/159/193; Unity/PlayerUI/InventoryPanel.cs:174`.

Duplicate/out-of-range/overflow chỉ còn warning string, mất ItemSlotView để xem; panel không render diagnostics tray. FilterText chưa lọc PageSlots/panel, không có tooltip đầy đủ hoặc selection keyboard như claim handoff.

Yêu cầu: Giữ overflow/diagnostic item views, render tray, projection filter không reindex, keyboard/focus/tooltip/durability/location/version/source; selection instanceId qua refresh/page.

### AGR3-09 — P2: Journal/map mới có phần cơ bản

Nguồn: `Client/Assets/Scripts/Online/Presentation/QuestJournalPresenter.cs:71; Unity/PlayerUI/MapPanel.cs:133`.

TogglePin bỏ qua questId, chỉ bool và panel chưa nối pin/ObjectiveDesc tracker. Map có live Refresh và dot clipping, nhưng dùng factor4px/WU tự đặt; chưa extent/version/pan/camera rectangle/waypoint reset.

Yêu cầu: Pin đúng quest có tracker và reveal gates; map projection từ source extent/units/version, pan/zoom/clipping/viewport rectangle/local waypoint, reset map/floor/session.

### AGR3-10 — P1: Cinema preview chưa có lifetime/modal/input binding đầy đủ

Nguồn: `Client/Assets/Scripts/Online/Unity/PlayerUI/CinemaOverlay.cs:136/140; PlayerUIRoot.cs:35/124`.

Known scene chỉ subtitle timer/placeholder; preview được ghi nhãn (đúng). Fallback hiện nhưng Update bỏ qua vì IsPlaying=false; Escape/Space poll riêng, cinema không nằm modal IsAnyOpen/input gate. Không có live story trigger hay media adapter; PlayCinema chưa có caller.

Yêu cầu: Giữ harness preview explicit khi contract/media thiếu; state machine+fallback/skip/failed/dispose, unified input/neutral release, không pause world/reward/auto-trigger theo quest name; packet Muse refs/SRT/still có nguồn.

### AGR3-11 — P2: Settings/accessibility chưa apply đầy đủ

Nguồn: `Client/Assets/Scripts/Online/Unity/PlayerUI/SettingsPanel.cs:200`.

UI scale có apply (ghi nhận); text size/input hints chưa có apply adapter; prefs chỉ apply trong Render visible, không từ startup. FindFirst doc có thể scale UI khác; chưa có safe area/large text/touch/focus evidence.

Yêu cầu: Apply scoped prefs từ init/reload qua đúng doc/audio adapters; unsupported disable rõ; safe area16:9/20:9/text Việt/cỡ lớn, giữ telegraph và input bounds; native evidence riêng.

## Tái lập

```powershell
$env:DOTNET_ROLL_FORWARD='Major' # local portable.NET10 only; không cần trên máy có.NET8
D:/Project/NGUMACHHUYENAN-tools/dotnet10/dotnet.exe test <checkout>/Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj -c Release
python Tools/ProducerReview/review_antigravity_acceptance.py --root <AG02-checkout> --dotnet <dotnet> --output <acceptance.json>
python Tools/ProducerReview/review_playerui_factory_binding.py --root <AG02-checkout> --dotnet <dotnet> --output <binding.json>
```

Hai producer commands hiện exit1 là finding thật, không phải PASS. Runner lịch sử giữ nguyên tại nhánh report #90; không sửa evidence cũ. Bốn JSON kèm báo cáo pin source hashes/exact head/counters/diagnostics. Native Unity6000.3.17f1/import/playmode/device/liveHTTP vẫn UNVERIFIED; thiếu Editor không cản sửa các lỗi source/presenter/setup độc lập.

Đọc work order16 để nhận cả gói sửa/hoàn thiện/acceptance liên tục trên nhánh hiện hành. Cập nhật PR body và báo cáo AG02_*: đánh dấu phần implemented-source / fake-adapter / preview / unsupported / unverified; bỏ claim toàn M1→M4 đã hoàn tất cho tới evidence phù hợp. Không tự tạo reward/flags/reviewed topology hoặc mở market/guild/crafting thay phần còn thiếu.
