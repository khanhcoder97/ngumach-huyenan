# Review bàn giao agent — 06/11/2026

Kết luận: có tiến bộ source/media thật; chưa nhận toàn bộ các PR code hoặc final media. Đã đo lại các đường lỗi chính ở worktree review riêng; không sửa root Qoder hay source của agent. Baseline tích hợp `abcf25408f1b8b5a8a40e32ad3759f5b50c45669` (PR123 đã merge vào integration, không phải main).

| Agent / PR | Head kiểm | Kết quả | Việc ưu tiên |
|---|---|---|---|
| OpenCode #109 | `a3a639b769a21508658c1e0c50799a9336902d51` | Các probe lifecycle cũ PASS; full unit suite treo, CI UI compile FAIL | Sửa termination của test/closure project, consumer HTTP đúng server mới |
| Qoder local #106 | `eb79389856aacfe5df9e5fcf24862ca863e065e7` | Build sạch,566 self-check,112 HTTP alpha PASS; lifeVersion vẫn regress sau hồi | Sửa lifetime đủ nhánh alive-returned; TALK→turn-in→portal/C1 |
| Qoder Remote #98 | `5371a4675fbd8fc4b41b4748f2b1732ef2d81824` | Không có commit mới; chưa có project Persistence/test/harness tracked | Giao R1 clone/build/test được trước khi gọi durable |
| Muse #119 | `0f2678f481a98dd5b909dc845f570026d084564e` | Audio610 hash/size khớp;20scene storyboard video; ba shot lỗi thấy trực tiếp; branch thiếu checkout policy | Đồng bộ policy owner, sửa shot, QA nghe/mix và delivery runtime |

Trong lúc review, Qoder push `7950ba17b291e1a0c4a045d8813aa6e1841b7c00`: compare từ eb79389 chỉ đổi `Server/Health/README.md` và `Smoke/e2e_p1.py` (pacing theo server tick). API GitHub báo26 checks SUCCESS ở head mới. Lượt build/self-check/HTTP tại đây vẫn pin eb79389; không gán số đo đó cho head7950. PlayerLifeLedger không đổi trong delta nên finding đời nhân vật còn áp dụng.

## OpenCode: sửa hành vi đạt nhưng bộ kiểm và package chưa đạt

Chạy lại harness public API đã dùng để bắt lỗi ở060b876, chuyển reference sang checkout a3a639b. `Evidence/opc-probes.txt`:

- UI-context Dispose0ms; timeout transport bỏ cancellation vẫn trả timeout có bound.
- Dispose trước successful reply continuation: old HP0, pending key giữ, late world reads0, receipt không bị áp.
- Relogin và same-key retry mới: old HP0, current HP50, cooldown phiên mới2900 giữ2900, old reply không read/mutate.
- Callback đã queue trước failed relogin: deliveredAfterEpochEnded0.
- Sáu ALPHA IDs canonical còn đúng; ID ngoài allowlist không gửi HTTP.

Những finding hành vi cũ này được đóng ở head pin, không phải còn nguyên vì review trước FAIL. Tuy nhiên lệnh full `dotnet test Shared/ClientCore.Tests/ClientCore.Tests.csproj -c Release` không kết thúc. Sau nhiều phút không tiến triển, chỉ testhost của lượt review được dừng; TRX ghi226 passed và run ABORTED. **Không phải236 PASS.** Lượt riêng với `--filter FullyQualifiedName~ReturnFromDeath_QueuedSuccessBeforeDispose_DoesNotMutateState --blame-hang-timeout 20s --blame-hang-dump-type none` cũng bị inactivity timeout20s abort. Log và sequence/TRX ở Evidence. Test tự đặt SingleThreadSyncContext nhưng pump/await không đảm bảo mọi continuation được drain; cần sửa fixture điều khiển được và giữ assertions, không bỏ test để xanh.

CI `PlayerUIChecks (.NET 10)` [run42082109595](https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/42082109595/job/127437563489) FAIL CS0246: `P1ClientAdapter.cs` implement `IP1InventoryV2Adapter`/`IP1DeathReturnAdapter` nhưng PlayerUIChecks project không có dependency closure. Raw CI log lưu Evidence/opc-ui-ci.txt. `shared-core` vẫn IN_PROGRESS lúc đọc snapshot; không gọi toàn CI xanh. Build library có CS1998 ở P1ClientV2.cs409.

Handoff #85 còn nói inventory v2/death-return chỉ có schemas, handler thiếu, và Muse sở hữu native: đã lỗi thời. Runner hiện dựng server trong chính nhánh OpenCode cũ, không phải Qoder hiện hành. Vì thế87 assertion agent báo không nghiệm thu inventory/death/boss/fullalpha của server mới. Cần paired-head runner. Không merge cả PR103/109 stack.

## Qoder: loop alpha hiện chạy, đời nhân vật vẫn có lỗi

Ở checkout sạch eb79389:

```text
dotnet10 build Server/Health/Health.csproj -c Release: 0 warning / 0 error
Health.dll --self-check: 566 passed, 0 failed, 566 total
validate_contracts.py: 31 schemas / 31 examples PASS
validate_content.py: PASS
alpha-p00 public HTTP: 112 checks PASS
```

Lượt alpha dùng gate private tách process, HP2000/MP500 endurance fixture giống runner, port5198. Log cuối xác nhận boss KILLED, fragment OK, wave_trial OK, escort A+B, loot PAID, v2_inventory OK, second_client ISOLATED; **talk=NO_HTTP_ROUTE, c1_01=LOCKED**. Runner/report ở thư mục này, process sở hữu đã dừng. Đây là HTTP console, chưa phải native full tutorial. So với lượt cb4f475 từng fail waveA, head hiện vượt được escort; không suy từ một lượt PASS thành nguyên nhân lịch sử đã xác định.

`WorldAoiProjectionService` hiện dùng source vị trí NPC theo owner cho cả AOI và x/y. Handoff tự nêu chưa có negative-control bỏ wiring và identity life/attempt ngoài x/y; tiếp yêu cầu kiểm đó.

Finding P1 còn tái hiện nguyên bằng public PlayerLifeLedger:

```text
before_churn=2
after_256_other_deaths=1
old_death_retained=False
```

Nhân vật kiểm vừa chết revision7 rồi đã hồi sinh, vẫn là character đang hoạt động. `IsClosable` cho reclaim vì LastDeath.LifeVersion < LifeVersion;256 character khác chết làm Track xóa entry, lần đọc mới tạo lại life1. Bản sửa chỉ pin downed-and-unreturned chưa bảo vệ monotonic life của alive-returned. Không cần giả định double grant để xác nhận lỗi: regression2→1 và mất death identity đã đủ. Harness link đúng source pin, lệnh/source/output nằm Harness/Life và Evidence/qod-life.txt. Receipt cleanup theo superseded life cũng cần thử key cũ qua nhiều đời; không được coi “đời cũ” là quyền thực hiện command cũ lần nữa.

Quyết định TALK/portal/MAP_VIEWED ở tài liệu mới chốt những phần transport trong quyền điều phối, không chọn số cân bằng skill/pet/elite. C1 minLevel11 phải được giữ; unlock chapter không tự làm quest AVAILABLE nếu thiếu cấp.

## Qoder Remote: chưa có checkpoint để nhận

Đối chiếu remote PR head và `git ls-tree`: dưới Server/Persistence chỉ có DatabaseRepository.cs và FeatureGate.cs; không có csproj library/tests/harness. QR workflow có nhưng CI server/content chung không chứng minh DB transaction/recovery. Không có ACK/source checkpoint mới trên #79 kể từ lệnh gói30. Giữ R1–R8, đòi checkpoint build/test >0 từ clone sạch; chưa nối Health hay gọi durable/restart-safe.

## Muse: byte nguồn, checkout và chất lượng là ba kiểm khác nhau

Pin checkpoint31. Manifest khai báo runtime audio610 =22 music/ambience port +519SFX variants port +30VO entries +13mix +26composed; không gọi541 file port là sáng tác mới. Campaign20scene/63shot/378s/21dialogue; prologue CIN000 riêng. Still/Ken Burns là storyboard animatic, không phải final pose animation.

LFS fetch/read tại review checkout:610 audio file thực, zero pointer, mọi hash/size khớp.103 tham chiếu cinematic (100 file scene +3 animatic) cũng khớp blob Git/object LFS, nhưng61 lệch tại working tree Windows (21OGV pointer +40timing/SRT CRLF). Decode trực tiếp object LFS CIN001OGV/CIN006OGV và CIN001mixv3 WAV bằng FFmpeg7.1 đều exit0, không lỗi decode; không phải native playback. Audit độc lập ở Evidence/media-independent.json; không thay hash để vượt lỗi. Đã xem ba keyframe:

- CIN012S03 có thanh lựa chọn game tiếng Anh baked vào hình, là lỗi clean frame rõ ràng.
- CIN017S02 là cơ cấu/cáp và người đứng cạnh, không có core/rắn như brief/handoff đã ghi.
- CIN015S02 là sân khô và mascot trắng ngoài brief, không phải tàn tích chìm.

Nhánh Muse **không chứa** `.gitattributes` policy hiện có ở integration: thiếu `*.ogv filter=lfs ... -text` và LF cho runtime timing/SRT. Sau `git lfs fetch`/`checkout`, OGV vẫn là pointer do không có filter attribute; timing/SRT chuyển CRLF và lệch hash. Đây là lỗi tái tạo bàn giao tại chính head, phân biệt với blob nguồn. Không kết luận LFS object mất hoặc media corrupt chỉ từ pointer checkout. Nhận owner policy từ integration rồi kiểm fresh checkout cả Windows/Linux. Report CP31 PASS của tác giả không chứng minh checkout này PASS.

Tool gốc verify_runtime_delivery cần ffprobe, Windows PATH hiện thiếu ffprobe; lần gọi dừng FileNotFoundError, không báo validator PASS. Dùng audit byte độc lập và FFmpeg7.1 có sẵn cho mẫu decode; phạm vi/kết quả cụ thể nằm JSON. Không thẩm âm, không đo lại loudness, không native Godot playback và không revalidate toàn source pack trong lượt này. Các báo cáo1151 source files của Muse vẫn là số tác giả, không phải số độc lập đo lại ở đây.

## Phân công

Gói31 tại Implementation/Work_Orders nêu checkpoint và acceptance cho cả bốn agent; gói29/30 vẫn tiếp tục. Codex giữ native/visual integration; không giao lại Muse runtime hay phục hồi Antigravity. Giao việc qua issue85/87/79/116 và cập nhật issue4; comment đăng thành công mới tính là đã giao, chưa ACK không gọi đang chạy. Không tự merge PR code, bật production hay thay thoại v3 bằng baseline cũ.
