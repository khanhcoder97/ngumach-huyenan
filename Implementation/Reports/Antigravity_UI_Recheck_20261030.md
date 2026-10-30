# Antigravity — tái kiểm bản sửa và tiếp tục AG-02

**Tiến triển được xác nhận: original suite39/39pass; chưa nghiệm thu toàn AG-01/AG-02.** Giữ #80/#85 mở và chưa merge #83/#89 vào client/main. Những lỗi cũ đã có fix không bị gọi là chưa sửa; các thiếu sót luồng thật bên dưới phải hoàn thành trong AG-02 hiện có.

## 1. Exact heads và phạm vi

- #83: `18fc5b5e0a1790c9c9614f8ea683c68012a1ced9`, base client #51 `92adee098fcb58acb5b280dcb167db9beecb8932`. Đã đọc source/diff22files và CI checks success.
- #89: `b30b2f5efe3be553b3542c76882b1735a5ce5c9b`, base #83. Diff `Client/**` so với #83 **rỗng** tại snapshot; thay đổi PR này hiện là report/work order/producer tools. ACK AG-02 có thật, B–F trong PR body vẫn chưa checked; chưa có triển khai M2 mới được bàn giao.
- Main vẫn `8298c61058e5016f8a0fe86d3dd4a9b815596a49`; không mặc định đã chứa client/server stack.

Review ở detached worktree riêng; không sửa code Antigravity hoặc worktree đang có owner. Phần test bổ sung chỉ dùng code presenter/core thật với adapter fixture có nhãn, không giả là native Unity hoặc online journey.

## 2. Kết quả đã chạy lại

| Kiểm tra | Kết quả thực tế |
|---|---|
| `dotnet test Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj -c Release` | **39pass/0fail/0skip**, project gốc đã build/test được |
| Bốn producer negative cũ đã đưa vào author suite | Cả4pass: BAG thiếu slot, EQUIPPED slot, cancel-loading, unrelated NPC |
| `dotnet run --project Client/Tests/P1CoreChecks/P1CoreChecks.csproj -c Release` | **55core+43audio+15input+46v2 =159assertions PASS**; lần đầu thiếu audio manifest trong sparse checkout đã bổ sung đúng input, rồi chạy lại đạt |
| UnitySyntaxCheck | **37files ×3profiles,0syntax errors**; không kiểm Unity type/import/playmode/device |
| Diagnostic project ngoài checkout:39author tests +5follow-through cases | **44total/41pass/3fail**, source fingerprints và failures trong JSON cùng tên |

Hai control dùng template IDs đạt, hai ca dùng entity IDs thật của NPC thất bại; ca response đến sau Clear cũng thất bại. Không bỏ/sửa author tests hoặc thay expected cũ. Năm ca bổ sung thuộc `Tools/ProducerReview/AntigravityFollowthroughChecks.cs`, dùng namespace riêng để không trùng class producer tests đã được agent đưa vào suite.

Tái tạo phần bổ sung:

```sh
python Tools/ProducerReview/review_antigravity_followthrough.py --root <checkout-18fc5b5> --dotnet <dotnet-executable> --output <recheck.json>
```

Exit1 hiện là finding, không là lỗi môi trường. Không đổi report37tests FAIL của baseline6e8394d thành report hiện tại; đây là đợt recheck riêng.

## 3. Đối chiếu findings cũ

| AGREV | Trạng thái tại18fc5b5 |
|---|---|
| 01 | **Đã xác minh sửa**: compile include đủ Core/Presentation, original39tests chạy đạt |
| 02 | Hai asmdef candidate/GUID0 đã bỏ; native assembly/type vẫn UNVERIFIED |
| 03 | Store nay là MonoBehaviour, margin từng cạnh đã sửa source; native type compile vẫn UNVERIFIED |
| 04 | BAG thiếu slot và tách EQUIPPED đã pass; overflow/duplicate item còn chỉ warning, UI chưa render diagnostics/overflow đầy đủ |
| 05 | **Đã xác minh sửa** rev10→5 giữ10; không lặp lại finding stale cũ |
| 06 | Cancel-loading và reset_closing đã có sửa; lifecycle/generation/dispose còn thiếu, late completion test mới fail |
| 07 | Có typed action và chặn unrelated NPC; entity/template/record IDs chưa nối đúng, hai ca mới fail |
| 08 | P1OnlinePanel có hook/ModalOpen/Escape/button diff thật; chưa bootstrap PlayerUI đầy đủ, document/lifecycle/input ownership còn thiếu |
| 09 | Có AudioListener.volume và scale settings panel; chưa áp dụng toàn bộ UX/preferences lúc startup, nhiều toggle còn preview |
| 10 | Có selection/detail label và marker clipping; Character, extent/pan/live refresh/layout/safe-area còn thiếu |
| 11 | Self fallback, actual build/test và bỏ swallow đã sửa; UTF8/diff workflow chỉ cover subset paths, không thay engine evidence |

## 4. Finding và handoff tiếp theo

| ID / bằng chứng | Vị trí | Yêu cầu |
|---|---|---|
| AGR2-01 /2tests FAIL | `NpcDialoguePresenter.cs:225–250` so IDs; `InteractAsync:51–55`; runtime `world_entities_bm.json` | Source entity `ENT_MAN_BM_NPC_LYAN` và `ENT_MAN_BM_NPC_TA_VAN_KHANH` cần Interact targetId dạngENT_; Accept/TurnIn lại dùng canonicalNPC_ IDs. Presenter chỉ so aliases NPC_ và gán recordId=targetId. Cần explicit context mapping có source, không một string dùng cho3loại ID. |
| AGR2-02 /1test FAIL | `NpcDialoguePresenter.Clear:169–173`, completion ở61/104/149 | Request bắt đầu→Clear→late success làm Idle thành Loaded lại. Dùng view generation/lifetime token để bỏ kết quả UI lỗi thời; không hủy pending transaction/receipt authoritative sau commit. |
| AGR2-03 /source review | `P1OnlinePanel.Update:121–124`; `PlayerUIRoot.Update:143–147` | Hai component cùng poll GetKeyDown(Escape) và CloseTop. Với2modal, một keypress có thể đóng2lần theo execution order. Chọn một dispatcher/consume event và test một Escape chỉ pop1, giữ input release gate. Chưa gọi đây là native input test đã chạy. |
| AGR2-04 /source review | `P1OnlinePanel.Open:55–56`; Hook21–35; Root36–40; panels AttachToDocument | Chỉ GetComponent hook; chưa có factory/builder/prefab/bootstrap tạo bộ PlayerUI. UIDocument field không được dùng, child panels tự FindFirstObjectByType. Cần inject đúng document và tạo/rebind đủ refs; default scene phải đi được bằng setup tái tạo. |
| AGR2-05 /source review | `P1OnlinePanel.Close:450`; Hook.CloseAllPanels/OnDestroy; Root.CloseAll/Close | Parent close chỉ hide panel, chưa dispose UI lifetime/adapter/roots; Close không remove visual tree/callbacks. Anonymous OnChanged subscription khó detach. Session mới/reopen có thể giữ refs/roots cũ; thêm teardown + late-callback tests. |
| AGR2-06 /remaining scope | PR#89 diff Client rỗng; Resource PlayerUI chỉ meta; Root switch chưa có Character | B–F chưa là code bàn giao mới. Hoàn composition+Character/equipment+bag/tooltips, journal/NPC/map, cinema/settings/accessibility và fault/native packet như work order12/14, không chỉ merge baseline rồi dừng. |

NPC source IDs được đối chiếu runtime world entities và server Interact validation, không lấy tên NPC từ hình. Các điều khiển template-ID trong diagnostic dùng fake accepted outcome để tách lỗi mapping; **không** chứng minh Interact(NPC_) là request hợp lệ trên server. Tests fake không thay HTTP/native acceptance.

## 5. Quyết định điều phối

Tiếp tục **AG-02 tại #85 / PR #89**, không mở AG-03 hoặc tạo thêm nhánh làm trùng PlayerUI. Work order14 là hướng dẫn thực thi cụ thể bổ sung work order12, ưu tiên AGR2-01..05 rồi nối cả gói B–F. Fix thuộc nền tảng #83 cần checkpoint đúng branch và đưa sang #89 có dependency, không tự merge. #80 chưa đóng cho tới khi đủ evidence.

Không thay canonical349XY, schema server, Core transport/audio hoặc artwork Muse. Source syntax/.NET tests không chứng minh UI đẹp, Unity compile hoặc thiết bị đã nghiệm thu. Tạo3PR reviewable milestones tiếp và làm phần độc lập trong khi chờ review; không dừng sau một fix nhỏ.
