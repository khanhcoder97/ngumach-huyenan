# Gói 31 — nghiệm thu delta, khép tutorial và bàn giao dùng được

Ngày 06/11/2026 (Asia/Tokyo), theo yêu cầu chủ dự án kiểm tra bàn giao và giao tiếp nhiệm vụ. Tiếp toàn gói 29/30, không thay bằng ACK hoặc chỉ tăng catalog. Baseline tích hợp `abcf25408f1b8b5a8a40e32ad3759f5b50c45669`; giữ branch/worktree riêng. Codex giữ graphics/UI/UX/VFX/Godot và tích hợp. Muse chỉ media. Antigravity tiếp tục không nhận việc. Production OFF, không tự merge.

Đọc report `Implementation/Reports/Review_20261106/Agent_Handoff_Review_vi.md` và quyết định `docs/production/Tutorial_Transport_Review_Decisions_20261106_vi.md` ở cùng PR. Các phần được duyệt trong quyết định có hiệu lực ngay; không chờ PR tài liệu merge mới code nhánh agent.

## OpenCode — PR109 / issue85

Pin `a3a639b769a21508658c1e0c50799a9336902d51`. Các probe queued-success-before-dispose/relogin và failed-relogin callback đã qua; giữ regression này. Tiếp O1–O8, checkpoint kế tiếp phải chuyển từ HTTP server cũ sang consumer thật của Qoder:

1. Cập nhật dependency lên Qoder `eb79389856aacfe5df9e5fcf24862ca863e065e7` hoặc successor pin rõ. Bỏ claim “inventory v2/death-return chưa có handler”; chúng đã tồn tại dưới gate. Muse không còn owner native Godot. Sửa body/report theo hiện trạng và phân biệt self-reported/đã kiểm.
2. Giao runner kết hợp hai head, SDK8 client + SDK10 server, private process/port/health identity/cleanup, gate OFF negatives và alpha positives. Inventory v2 12slot/equip/unequip/replay/conflict; encounter owner/current/detail/geometry/cast/life; death thật → return → fresh world → replay không hồi lần hai. Hai owner độc lập. Profile cũ dừng P00-01 không thay kiểm tutorial alpha.
3. Đóng CI đỏ `PlayerUIChecks (.NET 10)`: CS0246 thiếu `IP1InventoryV2Adapter`/`IP1DeathReturnAdapter` trong project closure. Unit suite cũng chưa đạt: lượt full phải dừng sau khi treo (226 test đã qua), riêng `ReturnFromDeath_QueuedSuccessBeforeDispose_DoesNotMutateState` treo và bị blame timeout20s abort. Sửa điều khiển SynchronizationContext/pump để test kết thúc và vẫn bắt regression, không bỏ test/assertion. Giao TRX đầy đủ có termination; sửa warning CS1998 nếu delta của mình.
4. Nối typed TALK/portal/MAP_VIEWED theo packet/schema Qoder mới; có thể chuẩn bị transport/fixtures/presenter trong lúc chờ handler. Giao immutable read model/commands, version/capability/error; không client grant tiến độ. Duy trì epoch cho mọi read/mutation và queued callback.
5. Tiếp O4–O8: journal/dialogue/target/cooldown/equipment/map/service availability, VFX dedupe/cancel theo cast/life/tick, package net8 có dependency/lock/license. Route chưa có trả unsupported. Giao core subset và dependency closure cho Codex; không nhập cả PR103/109 stack vào integration.

ACK SHA/checkpoint trên #85; push checkpoint API+HTTP sớm rồi tiếp phần độc lập. Native do Codex kiểm, console PASS không gọi native PASS.

## Qoder local — PR106 / issue87

Pin `eb79389856aacfe5df9e5fcf24862ca863e065e7`. Build sạch 0 warning/error, nhưng life identity vẫn lỗi ở nhánh nhân vật đã hồi sinh. Ưu tiên Q1 rồi khép Q2/Q6, tiếp toàn Q3–Q8:

1. Repro nguyên public `PlayerLifeLedger`: chết revision7 → hồi → lifeVersion2 → 256 character khác chết → lifeVersion1, LatestDeath mất. `IsClosable` coi nhân vật đã hồi là reclaimable trong khi character vẫn còn sống trong session/store. Giữ số đời đơn điệu và death identity cho toàn character active/reconnect; chỉ reclaim theo expiry/ownership đã chứng minh, không unrelated churn. Thêm churn >300 cho cả alive-returned/downed/reconnect, old death/receipt và lần chết kế. Audit receipt sau superseded life: key cũ không thành command mới heal đời sau. Không chỉ sửa test downed.
2. Hoàn route TALK theo quyết định mới; đây là approval phương án A có sửa, không còn chờ owner cho sáu câu trong packet. Chốt schema/examples/tests rồi public HTTP boss+fragment→class-confirm→turn-in→chapter permission. C1 gate level11 giữ thật.
3. Giao portal registry alpha từ atlas và route, hai chiều Bến Mưa/Thanh Lạc, server-owned destination, no arbitrary teleport. Sau đó packet MAP_VIEWED riêng, TALK ở map đích, C1 arrival. Không mở Thăng Long sớm. Không đổi anchor chết/topology/canonical placements.
4. Hộ tống: wiring x/y đã có, tiếp life/attempt/instance/floor/actor provenance theo hợp đồng additive nếu cần; kiểm hai owner đồng thời và mất AOI. Negative control chỉ bỏ wiring phải làm assertion HTTP fail. Giữ readiness healthState/targetable/availability và symmetric impact diagnostics, không báo nguyên nhân stall lịch sử khi log chưa chứng minh.
5. Technical contract: mapping error có ngữ nghĩa, retention/audit/capacity và rate-limit packet theo quyết định; không rename hàng loạt hoặc giảm 30 ngày. Gửi DTO adapter life/receipt cho Remote tại artifact/interface, không viết persistence thứ hai.
6. Tiếp navigation 349-anchor delta, combat/status/class resources và stats/economy/social có source. Các bảng pet/elite/passive còn xung đột: một packet chọn lựa với exact source/ảnh hưởng/test migration, không code cân bằng tự đoán, không gọi catalog là service đã bật. Phần không phụ thuộc tiếp tục làm.

ACK #87 (đồng bộ #41 khi checkpoint). Giao source+commands+raw HTTP+CI theo exactSHA; giữ appsettings OFF và schema freeze cho wire cũ.

## Qoder Remote — PR98 / issue79

Pin `5371a4675fbd8fc4b41b4748f2b1732ef2d81824`, không có bàn giao mới so với lần review trước. Tree vẫn chỉ có DatabaseRepository.cs/FeatureGate.cs dưới Persistence, không có csproj library/test/harness được tracked. CI server chung xanh không chứng minh QR build/test.

R1 là checkpoint bắt buộc kế tiếp: commit project library/test/harness, dependency/version/lock/license/ignore whitelist và workflow thật; clean clone restore/build/test với TRX count >0 + exact commands + CI URL. Gửi source sớm, không thêm chat dump hoặc đổi scope. Tiếp R2–R8 theo gói29: transaction state+revision+receipt(payload hash/result)+ledger+outbox; fencing hai process; crash trước/sau commit; recovery/replay; SQLite backup API/WAL integrity; migration; domain adapters gồm life/death/return. Không tự nối Health trước review; library PASS chưa là Health durable. Thiếu môi trường/runner thì ACK blocker cụ thể với lệnh/lỗi, không im lặng hoặc báo đã chạy.

## Muse — PR119 / issue116

Pin `0f2678f481a98dd5b909dc845f570026d084564e` (checkpoint31). Ghi nhận toàn campaign có video storyboard/animatic, draft VO và nhạc/ambience sáng tác; vẫn HOLD final picture/mix. Tiếp M1–M8 trong media scope:

1. Cập nhật body/report tới checkpoint31: runtime audio610, campaign20scene/63shot/378s/21dialogue; CIN000 riêng, không cộng vào20. Sửa status “chỉ CIN001S05 được duyệt” đã lỗi thời: 21 cửa sổ đã được duyệt cho DRAFT VO theo gói30. Giữ ba overrun để review, không cắt thoại/nới cửa sổ/tăng tốc để giấu.
2. Sửa ngay ba lỗi nội dung không cần character lock: CIN012S03 có UI chữ Anh; CIN017S02 thiếu subject lõi/rắn; CIN015S02 sai bối cảnh chìm. Tiếp dọn nhân vật/mascot không có trong prompt, bandage trái/phải và continuity môi trường. Character lock chỉ chặn shot thật sự phụ thuộc, không chặn sửa UI/bối cảnh/chủ thể. Giao keyframe trước/sau, video xuất lại, hash/manifest/negative check. Không gọi Ken Burns trên still là final pose animation.
3. Tạo review shortlist A/B của mix P0 v1/v2/v3, nhạc/ambience, pronunciation VO/tên riêng và loop seam. Phân biệt đo loudness/codec với nghe thực tế. Nếu môi trường không nghe được, ghi NOT_AUDITIONED và giao playlist/timecode/defect table cho người nghe; không xin lại quyền sản xuất cả gói. Giữ cả stems/takes có provenance, không thay canonical bằng alternate.
4. Giao pack runtime tối giản 640x360 OGV/Theora30fps+poster+SRT+timing cho prologue và CIN001/002/004/006, separate review/master MP4. Subtitle viewing variant baked chỉ review; runtime clean video + subtitle overlay. Tiếp campaign motion/VO/music/SFX còn thiếu và final media QA; không quay sang game sprite/UI/map/VFX/Godot.
5. Nhánh media hiện thiếu chính policy `.gitattributes` đã duyệt: không có `*.ogv` LFS và LF cho timing/SRT runtime. Checkout Windows mới còn OGV pointer và hash text lệch, dù audio610 khớp. Nhận policy từ integration hiện tại (đã có đúng rules), giữ root file do Codex sở hữu bằng merge commit owner; không tự viết policy khác. Kiểm fresh checkout sau merge, không chỉ worktree đã renormalize thủ công. Audit scope với baseline mới và cập nhật metadata. Native playback do Codex nối/đo, không tự báo game đã tích hợp.

## Codex và cách bàn giao

Codex nhận review/integration: ưu tiên public tutorial/TALK/portal rồi consumer native, journal/dialogue/escort authoritative, media player/mixer sau byte/codec review. Chưa nhập whole agent stack. Không cần chờ toàn MMO để giao từng source packet có thể kiểm. Không giao thêm cho Antigravity.

Mỗi agent ACK issue với branch/currentSHA/checkpoint đang làm, push artifact thật rồi tiếp phần độc lập trong gói lớn. Chỉ ghi “đã giao” khi comment issue đăng thành công; chưa ACK không gọi “đang chạy”. PR metadata phải phản ánh current head và measured limits. Giữ file người dùng và worktree khác.
