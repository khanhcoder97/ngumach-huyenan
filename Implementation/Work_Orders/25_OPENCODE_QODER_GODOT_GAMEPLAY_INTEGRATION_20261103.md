# Gói song song: lõi client dùng thật và server alpha chơi được

Ngày 03/11/2026, Codex giao theo yêu cầu mới của chủ dự án cho cả OpenCode và Qoder. Tiếp work order 24, không thay engine hoặc JSON design alpha đã duyệt. Nhận trọn gói, gửi checkpoint sớm rồi làm tiếp phần độc lập; không dừng sau ACK/một fix hoặc đợi merge toàn stack. Production gates OFF; không tự merge.

Nguồn bắt buộc:

- `docs/production/Godot_Client_Execution_Decision_20261103_vi.md`.
- `docs/production/Encounter_Snapshot_Review_Decisions_20261103_vi.md` — **đã duyệt hướng triển khai và trả lời đủ ba câu hỏi của Qoder**.
- `Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json`.
- `Implementation/Reports/OPC15_QOD21_Integration_Checkpoint_Review_20261103_vi.md`.

## 1. OpenCode — OPC-15 tiếp và gói tích hợp gameplay cho Muse

Baseline `18e5fe5fe2eb1bff764df4353e17a4cd2035c916`, PR #109. Codex đã chạy lại **56/56 tests, 0 skipped**, nhưng chưa nghiệm thu tương thích wire hoặc tích hợp online. Giữ worktree `D:/Project/NGUMACHHUYENAN-opencode-godot-core-20261103`, branch `opencode/opc-15-godot-client-core-20261103`; sửa các lỗi O1..O4 trên PR #109 trước. Không tạo nhánh mới chỉ để bỏ lại lỗi. O5..O6 có thể triển khai nối tiếp cùng nhánh hoặc branch stacked sau checkpoint đã công bố.

### O1 — đồng bộ wire thật, không dùng fixture tự định nghĩa thay hợp đồng

DTO/fixture hiện sai nguồn: `phase` chuỗi Telegraph thay vì số 1..3; `bossLifeId` chuỗi thay vì integer; `hp/maxHp/revision` thay `bossHp/bossMaxHp/bossRevision`; shape `type/range/radius` thay `kind/rangeWu/radiusWu`; thiếu center, status, registration, arena, safe pads, NPC, cooldown; tự thêm nhiều field wire chưa duyệt. Sửa theo packet Qoder cộng các sửa đã được Codex duyệt, rồi đối chiếu schema/fixture Qoder commit. Đừng yêu cầu server đổi tên cho khớp DTO tự tạo.

Phân biệt **boss phase 1/2/3**, encounter `status` OPEN/DEFEATED/RESET và `activeMove.state` TELEGRAPH/IMPACT/RECOVERY. Life/generation nội bộ client không được tự thêm vào wire đóng. Có typed methods current/detail và parser envelope P1 thực; giữ bossLifeId là số, opaque ID pattern đúng. Parse required/unknown/type/null/enum, finite geometry, normalized cone facing và units theo contract; không silently map shape lạ thành cone hoặc phase lạ thành Idle. Test phải dùng JSON được server/schema chấp nhận, cùng fixture âm tính sai tên/type/field thiếu/field dư/NaN/Infinity/non-unit facing/out-of-range/ID không hợp lệ. Chưa có schema trên branch Qoder thì dùng packet đã duyệt với nhãn pending server fixture; không gọi đó là server-exported.

### O2 — nối lifecycle và bảo vệ bất đồng bộ vào luồng sử dụng thật

Các guard đang là helper rời, chưa chứng minh P1Client/P1ClientAdapter sử dụng. Tạo composition/facade portable sở hữu session epoch, transport, adapter, subscriptions và cancellation lifecycle. Được sửa nguồn Core/Presentation portable trong `Client/Assets/Scripts/Online/` khi cần, giữ API tương thích và chạy regression; không sửa Unity presentation hoặc scene Godot của Muse. Không làm hai bản logic copy cạnh tranh.

Response login cũ/read cũ/poll cũ không ghi đè state mới; revision/tick phải xét đúng stream/owner/encounter/life, không so một số revision chung cho mọi resource. Context epoch là giá trị local capture lúc gửi, không đòi server echo field chưa có. Không fail-open vì generation=0 hoặc thiếu correlation trong đường áp state yêu cầu xác thực. Test bằng controllable delayed transport qua **client/facade thực**, không chỉ gọi `IsApplicable` trực tiếp.

Cancellation/timeout phải giữ uncertain mutation khi đã có thể commit; không tự resend với key mới. `TimeoutTransport` hiện chỉ truyền token: kiểm cả transport trả muộn/không hợp tác cancel, late result không được áp sau timeout/logout. Thu hồi CTS/subscriptions, đóng owned HttpClient đúng vòng đời, không giữ event từ session cũ. Không gọi client-side receipt demo là server authority; server receipt và inventory mới là nguồn grant.

### O3 — encounter view và VFX lifecycle dùng được

Có update result/event phân biệt new cast, same cast state transition, reset/cancel và terminal state. Cùng cast không phát lại telegraph qua poll; impact chỉ phát một lần theo cast+life; life/encounter/session mới hủy effect cũ. `Apply()` hiện cập nhật LastCastId trước khi consumer kiểm `IsNewCast`, dễ mất thông báo new cast; thay bằng API có thứ tự rõ ràng và test consumer thật. Không rollback snapshot mới bởi HTTP cũ. Deadline dựa `activeMove.stateEndsAtTick` và serverTick; countdown clamp ở 0, không dùng clock hệ thống để quyết định hit. Vector khóa từ telegraph, không quay cone theo owner hiện tại. Muse chỉ render, server tính sát thương.

### O4 — HTTP runner và CI phải chạy thật

Thêm script private-server lifecycle cho `Shared/ClientCore.HttpRunner/`, dùng port loopback riêng, SDK/runtime .NET 8+10 phù hợp project, bật các gate đúng profile, timeout, dừng đúng process. CI hiện mới build HTTP runner: đổi job thành thực thi runner thật và upload raw logs/TRX/summary có test/assertion count >0; exit2/zero assertions không được pass. Không dùng server người chơi hoặc fixture HTTP giả.

Chạy baseline ngay không đợi encounter: P00-01 nhận/nhặt/trả, lost response sau commit, retry **cùng key và cùng payload**, đọc inventory trước/sau từng replay/reject bằng HTTP mới, kiểm coin/item/revision không grant hai lần. Hiện câu kiểm `no double grant` chỉ nhìn cache sau reject, phải đọc mới. 2 session khác character, replay key cross-session bị chặn, expiry/relogin, stale response và logout lifecycle phải đi qua composition thực. Bỏ các demo receipt `k/h` khỏi mục bằng chứng HTTP hoặc chuyển nhãn unit test.

Encounter/inventory-v2/death-return chưa có thì suite đó ghi UNVERIFIED riêng; baseline vẫn phải chạy. Khi Qoder gửi fixture/route SHA, nối actual current/detail/phase/wipe/owner isolation. Không bật production hoặc bypass quest để có test xanh. Fullbag chưa có seed/capacity contract thì tiếp tục UNVERIFIED, không tự sửa server.

### O5 — API tích hợp gameplay đủ cho Muse

Giao factory/composition entry point có thể compile, provider stream/catalog injection, HttpClient transport implementation, dispatcher interface cho main thread, typed immutable view state và event subscription/dispose. Có example app hoặc headless consumer project build được dùng API public thật; không để `/* implement transport */` hoặc lời gọi `ReadEncounterAsync` chưa tồn tại làm mẫu chính.

API bao phủ capability, connect/expiry/reconnect, world snapshot/move, target/basic attack/skill/cooldown, NPC accept/interact/turnin, journal, inventory/equip, encounter, death-return khi server hỗ trợ. Route chưa có thì capability disabled có lý do và clear pending; không tạo success giả. Không viết gameplay authority ở client. Chỉ Muse sửa ClientGodot scene/input/render; cung cấp manifest API và mapping UI state/error/localization IDs cho Muse nối trực tiếp.

Capability phải phân biệt **client biết protocol** với **server triển khai và bật gate**. Danh sách route hard-code hiện tại không phải handshake; alpha boss OFF thì không được advertise usable encounter. Nếu server chưa có capability endpoint, dùng explicit versioned deployment/profile descriptor gắn source SHA, hoặc proposal Qoder duyệt; không tự tạo endpoint. 404 current có thể là chưa có encounter hoặc route OFF, không tự suy diễn backend hỗ trợ.

### O6 — bàn giao và chạy liên tục

Checkpoint 1: DTO/parser tương thích + regression + factory session thật. Checkpoint 2: HTTP runner/CI bắt buộc và raw evidence. Checkpoint 3: complete Muse integration API/sample và boss/inventory alpha khi upstream có. Cập nhật PR title/body/README/packet từ 40 tests cũ, ghi exact SHA/Qoder dependency/verified versus fixture/native UNVERIFIED. Push checkpoint và báo #85/#80, gửi Muse #1 API/source SHA; chờ schema thì làm O2/O4/O5, không dừng cả gói.

## 2. Qoder local — QOD-21 tiếp: read model, cô lập và trọn vòng chơi

Baseline `42a44914f0f3e8c9bfedcde6aa36a9581f59f5af`, PR #106. Đã xem source bridge và CI 8 job xanh; 462 self-check/67 casts là báo cáo in-process của Qoder, chưa phải HTTP/Godot fight nghiệm thu. Giữ branch `qoder/qod-21-ben-mua-playable-alpha-20261103`, worktree riêng hiện có. Không sửa Shared/ClientCore hoặc ClientGodot; remote persistence giữ phạm vi riêng.

### Q1 — không chờ lại ba câu hỏi đã duyệt

Quyết định đã merge trong PR #108 và gửi issue #87; gửi lại rõ tại #41 để không bỏ sót:

1. Encounter ID server cấp theo character+questAttempt, giữ qua wipe; life/generation mới khi retry; không tái dùng ID sau quest attempt đã kết thúc/bỏ.
2. **Không late join và không credit cho người vào muộn**; cùng character đã xác thực reconnect giữ đăng ký cũ. Không party reader/scaling.
3. Owner-only, registration đúng một character; người khác 404 encounter_not_found. Current/detail GET được phép; bổ sung locked facing/castId/stateEndsAtTick, snapshot atomic. Gate OFF route unmapped trả đúng pipeline thực, thường 404.

Đây là duyệt triển khai, không phải câu hỏi cần chủ dự án xác nhận lần nữa. Áp đúng toàn văn `Encounter_Snapshot_Review_Decisions_20261103_vi.md`; không giữ trạng thái blocked owner approval trong PR khi đã có quyết định này.

### Q2 — publish contract và đồng bộ read model trước khi mở rộng domain

Commit schema DTO/example/negative fixtures/version trước để OpenCode/Muse làm song song; báo ngay #85/#1 với exact SHA, route/error envelope, gate/profile. Giữ numeric boss phase riêng move state; status/life/revision/geometry/registration/cooldown/NPC đủ packet, không theo DTO sai của OPC-15. Không thêm event type CombatEventV2.

Nối current/detail GET và world-v2/AOI: boss owner đang được đánh phải hiển thị targetable đúng điều kiện; không để bridge cho đánh nhưng snapshot luôn false khiến UI không chọn được. Boss record template chung được dùng, actor mutable/life/HP/visibility/target selection/credit phải instance owner+attempt. A wipe/despawn/defeat/abandon không làm đổi B; world event boss không bị despawn toàn thế giới vì một owner mở quest. Validate lại owner/life/map/floor/range/LOS/alive/phaseguard tại server resolve. Snapshot copy atomic, không stale cache owner chéo.

### Q3 — hoàn hộ tống và chứng minh không nhận credit chéo

Escort cùng Ly An actor theo owner/attempt, checkpoint80/120, đúng wave3+3, range12/speed3 nguồn JSON. Credit deterministic từ authoritative kill/death/life/instance; không nhìn shared dead state rồi cộng cho mọi owner hoặc thêm Guid để gọi dedupe. Thiếu required wave/entity fail activation với diagnostic, không auto complete cuối waypoint. Test 2 owner active: A kill/reset/wipe/disconnect không credit/reset wave B; oldlife duplicate/late event không cộng. Nếu runtime hỏng actor thì recover/pending/error rõ, không lặng bỏ objective.

### Q4 — hoàn Q3/Q4 work order cũ: hệ thống thực, không chỉ validator

Inventory v2 bag100/12slot + equip/unequip/read routes side-by-side v1, server ownership, expected revision, atomic swap/replay/conflict/capacity, effective HP/MP clamp không hồi máu. XP/reward công thức accept snapshot và alpha loot có nguồn, grant gate default OFF, roll-once key scope đúng owner/life/group. Không tự thêm seed/admin HTTP public để demo.

Death-return POST empty intent tới(18,0), HP ceil50% current effectiveMax >=1, MP clamp, cooldown3s, receipt/retry cùng death/life, clear pending cast/guard/counter; không return sống, không double restore ở replay. Qoder remote chưa nghiệm thu thì giữ authoritative in-memory atomic lifecycle và nêu rõ không durable; không tự lấy phần SQLite của remote làm nửa vời.

### Q5 — chuỗi P00-02..05 và unlock có thể đi bằng HTTP

Collect ripples → kill đúng loài → cứu dân → dodge trainingwave có tham gia warning và né hit → escort → boss phase60/30 → fragment → Trial visible trước COMPLETED → class talk → Tạ turnin → CHAPTER_C1/Thanh Lạc portal. Nhiệm vụ C1-01 có record thật và minlevel11 giữ nguyên. Không turnin từ video, không bỏ objective, không grant giả để qua gate. NPC override vị trí/visibility phải ra wire để client tới được đúng actor, tránh vòng khóa NPC.

Private alpha runner thực qua HTTP: session/move/combat/interact/turnin/snapshot/inventory/death-return, 2 client owner isolation, phase thresholds/wipe/new life/late cast/replay/failed revision. In-process test bổ sung nhưng không thay HTTP. Ghi bước không chạy được là FAIL/UNVERIFIED kèm blocker cụ thể. Regression default/mob/guard/replay/contract/content vẫn giữ.

### Q6 — package khởi chạy và bàn giao liên tục

Gửi script Windows chạy private server loopback, chọn profile/gates bằng explicit args/env, health/log version, thời gian startup có timeout, dừng đúng child PID và không xóa DB/file khác. Gửi sample HTTP/typed fixture, read-only source manifest schema hash, exact SHA/CI/run logs cho #87/#41/#85/#1. Không cần chờ Q4/Q5 xong mới gửi Q2; chờ một contract review thì làm inventory/death-return/test độc lập. PR body hiện còn mô tả ce10281/400 tests cũ, cập nhật theo source cuối cùng và bỏ lời blocked approval đã được giải quyết.

## 3. Hợp tác và nghiệm thu

OpenCode sở hữu client portable composition/transport/presenters/tests; Qoder sở hữu gameplay và wire schema. Không sửa chéo schema/scene/server cho nhau. Khi contract khác nhau, giữ packet đã duyệt làm gốc và gửi fixture chung, không tạo protocol song song. Muse nhận API/fixtures/version, không phải tự dịch hai định nghĩa boss khác nhau.

GitHub: OpenCode ACK #85, Qoder ACK #87/#41, cross-reference PR #109/#106; có thể commit từng phần trong nhánh đang làm, không chờ task nhỏ tiếp theo. Không reset/clean/stash worktree khác. Mọi status PASS cần command/evidence; test unit, HTTP và native là ba phạm vi riêng. Codex review/merge; không tự gắn production-ready hoặc REVIEWED topology/asset.
