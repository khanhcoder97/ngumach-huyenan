# QOD-26 — Portal registry alpha, đối chiếu atlas, và những gì chưa chứng minh được

Gói 31 Q3, head `97de143`, ngày 07/11/2026. `DEC-TUTORIAL-TRANSPORT-20261106` đã duyệt
`POST /p1/world/portal` (chỉ nhận `portalId`, gate `P1:Portal:Enabled` + `AlphaProfile`, mặc
định OFF, `portal_locked` là mã hợp lệ, không nhận tọa độ/map/reason từ client) và yêu cầu
**packet registry là checkpoint tiếp theo**. Packet này không đổi code, không bật gate, không
sửa anchor chết `[18,0]`, không đổi 349 placement hay topology reviewState.

## 1. Records đọc trực tiếp từ atlas ở head này

`docs/production/Map_Production_Atlas_vi.md:89` — Bến Mưa:

    TP_BM_HUB=(24,0), SP_BM=(24,0), TP_BM_THANH_LAC=(348,0), TP_BM_THANG_LONG=(348,0)
    "mở sau C1-06"; "các điểm cùng tọa độ dùng một route selector";
    "nhân vật không thể đi quá x=150..195 trừ lối cầu"

`docs/production/Map_Production_Atlas_vi.md:106` — Thanh Lạc:

    TP_TL_WEST=(8,0), TP_TL_EAST=(350,0), TP_TL_BEN_MUA=(20,0),
    TP_TL_THANG_LONG=(350,0) sau C1-05, TP_TL_LAM_TRIEU=(350,0) sau C1-06

Đối chiếu tên đúng như quyết định yêu cầu ("Giữ source ID `TP_BM_THANH_LAC` /
`TP_TL_BEN_MUA` nếu đúng ID atlas ở head triển khai"): **cả hai tên đều có thật trong atlas ở
head này**, nên registry dùng chính xác hai id đó, không dùng ví dụ `MAN-TL-PORTAL_C1` trong
packet cũ như thể đó là record chuẩn.

Registry đề xuất — hai route, hai chiều, server-owned destination:

| portalId | map | anchor | đích | điều kiện mở |
| --- | --- | --- | --- | --- |
| `TP_BM_THANH_LAC` | MAP_BEN_MUA | (348,0) | Thanh Lạc **arrival (8,0)** = `TP_TL_WEST` | `CHAPTER_C1_UNLOCKED` từ turn-in P00-05 |
| `TP_TL_BEN_MUA` | MAP_THANH_LAC | (20,0) | Bến Mưa (348,0) | như trên, hai chiều |

Ba điểm quyết định ghi thẳng vào registry vì atlas yêu cầu, không phải tôi tự gộp:

1. **Không gộp arrival 8 với return 20.** Atlas đặt cả `TP_TL_WEST=(8,0)` và
   `TP_TL_BEN_MUA=(20,0)`; quyết định nói rõ "Phân biệt arrival8 với return portal20".
2. **Hai id cùng tọa độ (348,0) là hai route, không phải hai hình học.** Atlas có
   `TP_BM_THANH_LAC` và `TP_BM_THANG_LONG` cùng ở (348,0) và cho phép "một route selector";
   Thăng Long **không mở** theo P00-05 (mở sau C1-06), nên server phát hành từng route id và
   client chọn id — không sao chép geometry, không suy ra đích từ tọa độ.
3. **Anchor (348,0) của chiều về không phải safe/death anchor.** Atlas mô tả nó là cổng;
   `[18,0]` của DEC-DEATH-RETURN-20261105 giữ nguyên, và packet cũ từng nêu `xWu` trong
   payload chết đã bị từ chối — không có ngoại lệ nào ở đây.

## 2. Những gì E2E chứng minh được ngay khi route tồn tại

* **Không tồn tại id**: 404 không route khi gate OFF; với gate ON, `portalId` lạ bị từ chối
  trước khi chạm world state.
* **`portal_locked`**: P00-05 chưa turn-in ⇒ quyền chương chưa có ⇒ route trả
  `portal_locked`, retryable false, không di chuyển.
* **Sai map/floor/chết/người khác**: cùng khuôn đã dùng cho interact/death-return; hai owner
  độc lập không kéo nhau đi.
* **Replay**: cùng key + cùng `portalId` trả lại receipt cũ, **không** dịch nhân vật từ map
  mới về map cũ; client phải fresh-read (đúng ý "Replay cũ trả receipt lịch sử").
* **Dọn trạng thái**: transition phải kèm cleanup cast/guard/counter/aggro/movement đang giữ
  theo policy hiện hành, có revision và actor/life identity — đây là phần tôi tái dùng
  nguyên tắc từ death-return, không tự đặt luật chờ mới.

## 3. Hai điều tôi CHỨA không tuyên bố, nói rõ vì sao

1. **Đứng được tại (348,0) hay không — chưa chứng minh.** Hình học server đi từ
   `MapTopologyBundle` với `WalkablePolygons`/`BlockedPolygons` và `PointInPolygon`
   (`WorldGeometryService.cs:382`). Trong `Implementation/Content/Runtime` **không có bundle
   topology nào** (chỉ có `combat_mob_stats_v1`, `loot_recipe_v1`, `narrative_nodes_v1`,
   `npc_anchors`, `world_entities_bm`, `world_records`), và quy tắc của gói này là không
   đánh dấu bundle nào là REVIEWED. Vì vậy tôi không đủ căn cứ để nói "anchor đứng được" hay
   "không đứng được". Quyết định đã liệu trước: *nếu geometry không cho đứng tại anchor thì
   fail activation với lỗi cụ thể và gửi delta, không clamp âm thầm* — delta này chính là
   dòng đó. Tôi sẽ trả lời bằng test khi có bundle, không bằng suy luận.
2. **Thử đo bằng HTTP của tôi hôm nay thất bại, và tôi báo là thất bại.** Tôi cho boot một
   server và đi dần từ x=18 về đông để xem chặn ở đâu; probe không đọc được vị trí (cả
   `result` lẫn `error` đều trống theo cách tôi parse), nên **nó không chứng minh gì** — kết
   quả `furthest x reached: None` là lỗi probe của tôi, không phải hành vi server. Không
   được suy ra "đi tới 348 được" từ đó. Probe đúng phải dùng `walk_to` của chính bộ E2E.

Hệ quả trung thực khác: **happy path của portal cần `CHAPTER_C1_UNLOCKED`, tức cần turn-in
P00-05, tức cần TALK của `NPC_CLASS_TRIAL` — thứ chưa có narrative node (#134)**. Nên trong
lần triển khai đầu, phần tôi verify được là toàn bộ mục 2; còn "đi thật" sẽ đỏ cho tới khi
content bổ sung node. Tôi thề không nới gate cấp 11 hay đánh dấu AVAILABLE giả để bài test
xanh.

## 4. Việc còn lại để route chạy được

1. Owner/content: thêm node cho `NPC_CLASS_TRIAL` (id + questId + speakerNpcId +
   conditionKey), hoặc chỉ định cách khác để objective class-confirm commit.
2. Owner: xác nhận bundle topology nào được dùng làm căn cứ walkability (hoặc cho tôi số
   polygon) để mục 3.1 trở thành test.
3. Sau hai thứ trên: schema/example/negative fixtures cho `PortalRequest`/`PortalResponse`,
   validator rules trước, rồi `P1:Portal:Enabled` OFF trong `appsettings.json`, service,
   endpoint map khi `AlphaProfile && Portal`, gate-one leg mới, và E2E hai chiều.

## 5. Lệnh tái lập các dòng trong packet

```bash
grep -n "TP_BM_THANH_LAC\|TP_TL_BEN_MUA" docs/production/Map_Production_Atlas_vi.md
ls Implementation/Content/Runtime
sed -n '382,412p' Server/Health/World/WorldGeometryService.cs
```

## 6. Bổ sung 07/11/2026 — mục 3.1 và 3.2 đã có số đo, không còn là suy luận

Không xoá hai mục trên; ghi thêm kết quả đo được bằng probe đọc đúng
`result.self.x/y` và `error.code` (đúng điều kiện mục 3.2 đặt ra — probe trước đây của tôi không parse cả vị trí lẫn lỗi,
nên vô giá trị, và nó vẫn là lỗi của tôi, không phải của server).

Boot 1: `Server/Health/bin/Release/net10.0/Health.dll --urls http://127.0.0.1:5097`,
KHÔNG gate nào (chỉ để đo riêng `/p1/move`), `CHR_PROBE_GEO`, mỗi bước cách nhau 0,31 s
vì `/p1/move` tính bước theo thời gian thực (`MoveSpeedWuPerSecond × elapsed`, chặn ở
`MaxStepDistanceWu`).

- từ spawn đi đông tới `x=120, y=0`: không bước nào bị từ chối;
- từ `(120,0)` lên bắc tới `(120,60)`: không bước nào bị từ chối;
- đi nam: dừng ở `y=-12` với **status 200**, tức đây là `Math.Clamp` theo `bounds.YMin`,
  không phải `movement_blocked`;
- từ `(120,-12)` đi đông tới `x=351`: không bước nào bị từ chối.

Boot 2: cùng DLL với bộ gate alpha (`AlphaProfile`, `DeathReturn`, `CombatV2`,
`CombatDamage`, `MobBehavior`, `QuestAccept`, `Interact`, `QuestTurnIn`,
`StartingHp/StartingMaxHp=4000`), `CHR_PROBE_PORTAL_LINE`, đi dọc đường `y=0`:
**tới `x=352,5`, `first refusal=None`** — tức `(348,0)` đi tới được bằng cách đi bộ, trên
cả hai boot.

Điều số đo này chứng minh: trên cấu hình đang ship, server **không từ chối toạ độ nào
trong bounds** của `MAP_BEN_MUA`; đoạn thẳng từ spawn tới `(352,5,0)` đi được hoàn toàn.

Điều nó KHÔNG chứng minh, và vẫn là quyết định của owner (mục 4.1): server trả lời "đi
được" vì **không có bundle topology nào được nạp** (`NotEnforced`), chứ không phải vì có
hình học đã review cho phép. Nếu sau này nạp một bundle có `BlockedPolygons` đè lên
`(348,0)`, câu trả lời đổi mà không dòng code nào sửa. Nên mục 3.1 vẫn mở, nhưng đã thu
từ "không biết" xuống "server hiện không enforce gì trong bounds — căn cứ phải là bundle
nào, không phải probe".

Tái lập:

```bash
# boot 1 (no gates)
dotnet Server/Health/bin/Release/net10.0/Health.dll --urls http://127.0.0.1:5097
python "$LOCALAPPDATA/Temp/probe_geo.py"           # line walk, YMin clamp
# boot 2 (alpha gates, same DLL)  — see the env list above
python "$LOCALAPPDATA/Temp/probe_portal_line.py"   # -> x=352.5, first refusal=None
```

Probe không được commit: cả hai là script đo một lần, không phải regression. Phần đã trở
thành regression nằm trong `alpha-p00` (đoạn AOI của hộ tống) và self-check
`alpha.escort_audience_*`.

## 7. Bổ sung — transition và combat phải cùng một thứ tự commit

Trạng thái mục 4.3 ở trên đã cũ: schema, validator, handler và hai gate đã tồn tại ở
parent `7696da28ecf92ad46e5d413183106d8cd017d07d`; không còn chờ tạo route. Happy path
HTTP cả tutorial vẫn thiếu narrative node của `NPC_CLASS_TRIAL`, không được thay bằng
fixture cấp quyền chương. `portal_locked` hiện trả `retryable: true` trong handler;
mô tả `false` ở mục 2 không phản ánh implementation hiện tại.

Delta server tiếp theo không đổi wire/anchor/gate. `CombatTickEngine.SerializeActor`
đặt thứ tự engine → actor cho acceptance + schedule, portal fresh validation + teleport
+ cleanup + receipt, và death-return fresh bounds check + restore + cleanup + receipt.
`Schedule` mở guard trước khi nhả hai khóa. HTTP combat gọi `AcceptAndSchedule`, không
còn khoảng trống giữa `Resolve` và `Schedule`. Historical receipt vẫn được trả như lịch
sử; replay cast đã bị portal hủy không được xếp lịch lại ở map đích.

Đây là serialisation trong một process, **không phải durability transaction**. Tick
không bị bọc thêm actor lock quanh boss callback: engine → boss và boss → actor đã tồn
tại, nên thêm actor → boss sẽ đảo thứ tự khóa. Packet không tuyên bố đã giải quyết toàn
bộ aggro/boss targeting hoặc biến snapshot nhiều aggregate thành atomic snapshot.

Self-check thêm sáu assertion cố định, không nằm trong vòng lặp có số lượng ngẫu nhiên:

- Quan sát cả lookup acceptance và lookup schedule: thread gọi đang giữ engine/actor,
  thread cạnh tranh `Monitor.TryEnter` engine thất bại.
- Quan sát trước/sau **teleport thật**, không thay kết quả teleport: cùng exclusion;
  sau transition không còn cast, guard đóng, reserved counter đã cancel.
- Replay source-map cast receipt không tạo cast/event/guard mới ở destination.
- Cast mới sau transition có audience map đích và được resolve, không bị cleanup cũ hủy.
- Giữ actor ở thread kiểm thử, cho schedule tiến tới trạng thái chờ actor: engine vẫn
  không lấy được; guard không thể mở ở ngoài vùng schedule đã khóa.
- Tương tự cho death-return: engine đã bị giữ trước khi chờ actor; sau khi nhả actor,
  return kết thúc, cleanup/receipt có cùng revision. Deadline chỉ là watchdog liveness,
  không dùng ngủ một khoảng rồi đoán một thread đã chạy tới đâu.

Lượt đầu: build Release 0 warning/error, self-check **614 passed / 0 failed / 614 total**.
Ba mutation độc lập đã chạy trên source, build lại và kiểm toàn bộ self-check:

| Mutation | Kết quả | Assertion thực sự bắt lỗi |
| --- | --- | --- |
| Bỏ engine lock trong `SerializeActor` | 611 / 3 / 614 | acceptance, teleport exclusion, death-return engine-before-actor |
| Trả `Schedule` về guard-open sau engine lock như trước | 613 / 1 / 614 | `alpha.portal_guard_open_cannot_outlive_engine_schedule_lock` |
| Bỏ điều kiện `Replayed: false` trước schedule | 613 / 1 / 614 | `alpha.portal_old_cast_receipt_cannot_schedule_on_destination` |

Mỗi mutation đã được khôi phục trước mutation sau. Không giữ mutation nào trong source.
Lượt verify sau khôi phục, raw HTTP và CI của **commit chứa delta** phải được công bố
riêng trên #87/#41/PR106; CI 30/30 của parent không chứng minh delta này.

Lệnh chạy từ repository root:

```bash
dotnet build Server/Health/Health.csproj -c Release --no-restore --nologo
dotnet Server/Health/bin/Release/net10.0/Health.dll --self-check
bash Server/Health/Smoke/run_e2e_p1.sh alpha-p00
bash Server/Health/Smoke/run_e2e_p1.sh death-return
bash Server/Health/Smoke/run_e2e_p1.sh dev
bash Server/Health/Smoke/run_e2e_p1.sh mob-combat
bash Server/Health/Smoke/run_e2e_p1.sh two-client
bash Server/Health/Smoke/run_e2e_p1.sh default
bash Server/Health/Smoke/run_e2e_p1.sh audience-gateoff
bash Server/Health/Smoke/run_e2e_p1.sh alpha-revive
```

## 8. Field `result.eventId` — mâu thuẫn semantic cần quyết định, không sửa wire lén

`PortalResponse.schema.json:77–80` đóng băng ý nghĩa deterministic theo
`character + portalId + destination map`. `AlphaPortals.cs`, hàm `EventId`, đang hash
đúng ba đầu vào đó. Vì không có operation key/revision/life trong hash, hai lần đi mới
cùng chiều của cùng character sẽ có cùng id; đây là kết luận từ công thức source,
**chưa phải số đo một hành trình HTTP lặp lại**.

Trong khi đó `Production_Technical_Contracts_vi.md:59` yêu cầu consumer lưu `eventId`
để dedupe server events. Nếu consumer coi mỗi receipt portal là một transition event,
chuyến mới có thể bị loại như replay. Khóa engine không sửa được mâu thuẫn này.

Owner cần chốt một trong hai ý nghĩa trước khi đổi field/consumer:

1. Giữ schema hiện tại: id là route identity per character, không là unique operation
   event; chỉ định khóa dedupe transition khác và contract cho consumer.
2. Duyệt semantic/version migration sang id per committed operation, vẫn ổn định khi
   replay; chọn đầu vào có ownership/idempotency rõ, quy tắc lịch sử và migration receipt.

Acceptance cần có fresh out → fresh back → fresh out (operation khác), replay từng key,
changed-body conflict, hai character, và dedupe consumer qua reconnect. Hiện **blocked**
ở `result.eventId` operation identity/migration; không tự thêm trường hay đổi hash trong
schema freeze. MAP_VIEWED, target-map TALK/C1 arrival và class-confirm content vẫn mở.

## 9. Bổ sung — movement chờ actor không được ghi lùi timing reset

`MoveAsync` trước delta lấy `clock.UtcNow` trước actor lock rồi ghi `LastMoveAtUtc`
trong lock. Nếu teleport/death-return reset timing trong lúc request chưa lấy được
actor, request có thể ghi đè bằng timestamp cũ. Delta chuyển phép đọc clock vào actor
lock, ngay trước phép tính elapsed; không đổi sequence, epoch, wire, geometry hay gate.

Assertion cố định thứ bảy gọi **handler MoveAsync thật** bằng context/JSON hợp lệ.
Logger factory cung cấp điểm xen kẽ trước lock; thread cạnh tranh gọi teleport thật,
không giả kết quả hay timestamp. Test đợi clock tick tiến theo trạng thái, dùng deadline
chỉ làm watchdog, sau đó so `LastMoveAtUtc >= transitionResetAtUtc`, response 200,
map/position đích và revision tăng đúng hai lần. Đây là endpoint-level in-process,
không phải một HTTP socket probe.

Trên runtime cũ, build thành công và toàn bộ suite cho **614 passed / 1 failed / 615 total**; đúng `movement.queued_handler_cannot_backdate_transition_timing_reset` thất
bại với `advanced=True teleported=True resetDeltaTicks=-406606` (.NET time ticks,
khoảng 40,6606 ms bị ghi lùi). Sau khi chuyển clock sampling vào lock, test qua.

Review còn sửa giả định tick-zero trong assertion destination cast ở mục 7:
`ServerClock.Tick` chạy theo stopwatch từ lúc tạo clock, không đợi test gọi Tick.
Test hiện resolve bằng `serializedClock.Tick + 4` lấy sau acceptance, thay vì tick 4
tuyệt đối; không dùng setup nhanh làm điều kiện pass.

Kết quả cuối cùng trên toàn bộ source đã khôi phục, không còn mutation:

| Lượt kiểm | Số đo thực tế |
| --- | --- |
| Release build | 0 warning, 0 error |
| Self-check, ba process mới liên tiếp | 615 / 0 / 615 ở cả ba lượt |
| CI-shaped smoke, cwd `Server/Health`, năm gate của workflow | 358 checks |
| HTTP `alpha-p00` | 132 checks |
| HTTP `death-return` | 17 checks |
| HTTP `dev` | 110 checks |
| HTTP `mob-combat` | 33 checks |
| HTTP `two-client` | 99 checks |
| HTTP `default` | 22 checks |
| HTTP `audience-gateoff` | 14 checks |
| HTTP `alpha-revive` | 7 checks |
| Frozen contracts | 35 schemas / 35 examples, pass |
| Combat/social source self-test | 364 independent drift cases rejected |

HTTP dùng runner ở mục 7 với `E2E_PORT=5107`. Smoke dùng server riêng tại 5108,
`P1__QuestAccept__Enabled`, `P1__Interact__Enabled`, `P1__QuestTurnIn__Enabled`,
`P1__CombatV2__Enabled`, `P1__CombatDamage__Enabled` đều `true` chỉ trong process test;
chạy `python Server/Health/Smoke/smoke_p1.py http://127.0.0.1:5108`. Không đổi default.
Logs cục bộ: `%TEMP%/wo31-final615-build.out`, `wo31-final615-selfcheck-{1,2,3}.out`,
`wo31-final615-e2e-{profile}.out`, `wo31-final615-smoke.out`; negative movement ở
`wo31-movement-before.out`. Exact commit/CI và raw HTTP được công bố trên #87/#41/PR106.

Raw HTTP cuối vẫn cho C1 accept `422 prerequisite_not_met`, `fieldErrors:["level"]`,
state `LOCKED`; TALK original/replay/conflict `200/200/409`, receipt revision 3.
P00-05 TALK có `credited:false`, `appliedFlag:null`, `eventId:null`; portal trả
`422 out_of_range` từ 281,1 WU. Kết thúc runner vẫn là
`talk=ROUTE_LIVE_NO_NODE_FOR_TRIAL_NPC c1_01=LOCKED`, không phải public chapter closure.
Ba negative serialization ở mục 7 được đo trước assertion movement thứ bảy; không đổi
các tổng lịch sử đó thành 615. CI parent 7696da2 không được dùng thay CI delta runtime.
