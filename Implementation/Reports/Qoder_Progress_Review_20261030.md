# Qoder — kiểm tra tiến độ và correctness, 2026-10-30

**Kết luận: có tiến triển code/CI thực, nhưng CHANGES_REQUIRED trước nghiệm thu QOD-17 và mở vòng chơi hoàn chỉnh.** Không merge cả stack chỉ vì CI xanh. Giao tiếp work order13 để sửa correctness rồi triển khai trọn vòng Bến Mưa.

## 1. Snapshot đã kiểm trên GitHub

| Nhánh/PR | Exact HEAD | Kết quả thực tế |
|---|---|---|
| #77 `qoder/qod-17-loot` | `f3b37ddbb04caae29bbbb9202f510806d9f6d136` | Loot recipe/RNG/ledger **dry-run**, chưa đồng nghĩa item/currency được grant |
| #78 `qoder/qod-17-spawn-groups` | `ed4898be621bd5e4e8603c0e5560ba239ef4d9b4` | Group members/respawn, mob telegraph/impact/recovery và mob damage; #82 nằm trong nhánh này, **chưa merge main** |
| #84 `qoder/qod-17-guard-runtime` | `4d959dd0473435c3bf7feea2877e1d5076d186d5` | Có guard/whiff/confirmation/counter runtime và tests mới,6/6checks success; base #78 |
| #76 Codex replay-safety | `514c3f20c077175c7752706d845d11d78d464eda` | Vẫn nhánh riêng, không phải ancestor của #84; chưa thể mặc định đã có fix |
| QODER Remote #79 | `0bac9af4cb0cff208165896989cf1b02b9efe557` | Nhánh vẫn ở commit dispatch, chưa có ACK hoặc implementation PR được xác minh |
| main | `8298c61058e5016f8a0fe86d3dd4a9b815596a49` | Chưa chứa full stack server/client đang review |

Đã đọc source GuardRuntime/MobAttackService/CombatTickEngine/InMemoryCombatV2Service, endpoint scheduling, clock/background loop, smoke/self-check, PR/checks và comments #41/#79. Checkout root của Qoder được giữ nguyên, gồm hai ảnh untracked `temp_rgba.png`/`test.png`; build/review chạy trong worktree tách biệt.

## 2. Kiểm tra đã chạy

- Local SDK10.0.403: `dotnet build Server/Health/Health.csproj -c Release` **exit0**,0errors/3nullable warnings kế thừa; `dotnet ...Health.dll --self-check` **exit0**. Log local không flush hết summary trước process exit, nên không đếm số log PASS thành tổng assertions.
- Đã kiểm [CI smoke exact HEAD4d959dd](https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41056155892): **301passed/0failed**,440HTTPsmoke, run success. Smoke không bật MobBehavior nên không chứng minh guard trước đòn quái qua HTTP.
- Negative HTTP chạy server riêng trên loopback/port tự cấp, MobBehavior OFF, cast BASIC_ATTACK tại spawn rồi đợi END, replay cùng body/key: **FAIL**. Cùng castId nhưng thêm END cursor3 sau CAST_START1/END2. `Qoder_Replay_Review_20261030.json` lưu binary SHA/source/evidence; server riêng đã dừng bằng chính process handle đã tạo, không tác động service người dùng.
- Probe dùng **GuardWindowStore thật** với reservation synthetic CounterTick102: `PendingCounters(102)=1`, `PendingCounters(103)=0` trong khi CounterResolved=false: **FAIL**. `Qoder_Guard_Queue_Review_20261030.json`. Đây là queue-level probe, không giả là full guard encounter HTTP.

Tái tạo sau khi build reviewed checkout:

```sh
python Tools/ProducerReview/review_qoder_replay.py --root <checkout> --dotnet <dotnet> --output <replay.json>
python Tools/ProducerReview/review_qoder_guard_queue.py --root <checkout> --dotnet <dotnet> --output <queue.json>
```

Tools chỉ tạo server private và project tạm, không patch source gameplay. Exit1 khi có finding,2 khi blocked. Không biến report FAIL lịch sử thành PASS bằng chỉnh expectation.

## 3. Findings và giới hạn còn lại

| ID | Mức/bằng chứng | Vị trí và yêu cầu |
|---|---|---|
| QREV-01 | P1 / HTTP tái hiện | `P1Endpoints.cs:615–627` luôn Schedule receipt cached; `_casts` chỉ giữ cast active nên replay sau END lại được schedule. Mang fix #76 hoặc giải pháp tương đương, giữ guard mới; cached replay không thêm END/hit/death/confirmation hoặc refresh guard. |
| QREV-02 | P1 / actual queue probe + source | `GuardRuntime.cs:99–111` so CounterTick==tick; `CombatTickEngine.cs:314–319`; ServerClock.Tick tính từ wall elapsed; PeriodicTimer có thể coalesce/processing muộn. Nếu tick102 không được xử lý, counter treo mãi. Làm deadline/catch-up ordering có giới hạn, overdue resolve/cancel đúng một lần, giữ intended/application tick semantics; không chỉ đổi == thành<= rồi bỏ ordering tests. |
| QREV-03 | P1 / static source, fix #76 chưa có | `InMemoryCombatV2Service.cs:91–101` lookup trước actor lock, không recheck atomic bên trong; actor chết chưa được reject tại accept. `ResolveHit` không kiểm nguồn còn sống/cùng map/floor trước impact. Bảo toàn atomic key/hash/cost/revision/seq/receipt và cancel source invalid; test race thực và delayed ticks, không chỉ replay ngay sau accept. |
| QREV-04 | P1 / static source, cần regression | `CombatTickEngine.SelectTargets/ResolveHit` lọc range/cone/map/floor nhưng chưa gọi LOS cho basic/MK03, trong khi counter có LOS. Thêm impact LOS theo geometry policy, test REVIEWED fixture riêng; production topology vẫn chưa reviewed. Không đổi349XY hoặc dùng NotEnforced để gọi wall blocking pass. |
| QREV-05 | P1 / static race risk, chưa tái hiện race riêng | MobAttackService tách EvaluateIncoming→HP commit→CommitConfirmation thành các actor critical sections khác nhau; window có thể refresh/cancel/move giữa DR decision và confirm. Pin window/cast/life token hoặc serialize cả impact phù hợp, kiểm resource/revision/event transaction consistency. Thêm barrier test, không gọi risk này là race đã đo được. |
| QREV-06 | P2 / feature/evidence gap | Guard window/whiff không có snapshot recovery; chưa enemy cast/status contract; smoke MobBehavior OFF; death-return chưa endpoint; MK02 accepted chưa có swept movement. Cần proposal/version/gates và test thực, không gọi accept là mechanics đã chạy. |
| QREV-07 | P1 / scope gap | Chỉ1quest definition được load,44entity không chứng minh toàn campaign; loot mới dry-run, XP/level/equip/boss P00-05 và relog durable chưa đủ. Mở QOD18→19 theo nguồn chuẩn, giữ unresolved fields và activation gates, không báo fullP1. |

QREV04/05 là source review cần agent chứng minh bằng test mới; không tính vào hai negative probes đã thực thi. Actor baseline hiện dùng ATK20/armor10, mob referenceL5 với nguồn fixture rõ; những thông số này vẫn là prototype, chưa chứng minh balance production. Quyền DB mới vẫn ở QODER Remote; agent local nối adapter sau review.

## 4. Giao tiếp

Local nhận work order13: sửa QREV01–05→combat recovery/status/dash/death-return→quest P00-01..05 và XP/stat→loot/equip→Mãng Cốt→hai client/fault handoff. Mỗi PR đủ scope review và tiếp phần độc lập khi chờ duyệt, không tự merge. QODER Remote tiếp tục QR1→QR6 tại #79, trước tiên ACK + DB schema/repos/migration/tests; chưa có bằng chứng làm xong để giao QR02 mới.

Epic local mới tại [#87](https://github.com/khanhcoder97/ngumach-huyenan/issues/87), nhánh `qoder/qod-18-ben-mua-completion-20261030`; issue #41 giữ queue gameplay. Branch/issue mới chỉ là dispatch, cần ACK/commit agent để xác nhận bắt đầu.

Đợt này không chạy Unity/device/MMO load hoặc full guard mob HTTP, không chứng nhận auth/DB/persistence đã hoạt động. Canonical placements/topology gates không thay đổi.
