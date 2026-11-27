# Review checkpoint OPC-15 và QOD-21 — 03/11/2026

Theo yêu cầu giao tiếp nhiệm vụ cho OpenCode và song song Qoder. Đây là review phạm vi tích hợp, không nghiệm thu toàn game hoặc native Godot.

## OpenCode #109

Exact head `18e5fe5fe2eb1bff764df4353e17a4cd2035c916`, branch `opencode/opc-15-godot-client-core-20261103`. Worktree sạch trước kiểm tra. Codex chạy `dotnet test Shared/ClientCore.Tests/ClientCore.Tests.csproj -c Release` bằng SDK portable10 với DOTNET_ROLL_FORWARD=LatestMajor: **56 passed, 0 failed, 0 skipped**. TRX: `D:/Project/NGUMACHHUYENAN-tools/dispatch/review-latest-20261103/opc15-tests/clientcore-review.trx`. Đây là net8-target test chạy roll-forward, không chứng minh Godot native hoặc toàn bộ export.

Nhận foundation portable library và tests. **Chưa nhận tuyên bố hoàn O-A..D** vì:

- **P1 — DTO/fixture sai hợp đồng:** EncounterSnapshot dùng phase chuỗi, bossLifeId chuỗi, hp/maxHp/revision và shape type/range thay numeric phase/life, bossHp/bossMaxHp/bossRevision và kind/rangeWu. Thiếu trường quan trọng từ packet. Fixture dùng ID `enc-fixture-001`, góc60 và các field generation/lifeScope tự thêm, không đại diện server contract đã duyệt. Tests tự xác nhận DTO của mình, không kiểm compatibility với schema/server.
- **P1 — helper chưa nối runtime:** StaleResponseGuard/ReceiptReplayGuard/TimeoutTransport được kiểm riêng; chưa có composition dùng chúng trong luồng public P1Client/P1ClientAdapter. Sample Muse còn transport TODO và ReadEncounterAsync comment vì API chưa tồn tại. Không coi đây là integration flow sử dụng được.
- **P1 — HTTP chưa chạy CI:** job shared-http-runner chỉ dotnet build rồi echo ghi build-only. Không có evidence HTTP mới cho library này. Program.cs có receipt `k/h` dựng tay; sau repeat-reject kiểm coin từ cached Inventory, chưa đọc lại server nên chưa chứng minh không double grant ở thời điểm đó.
- **P2 — shape/state validation:** unknown shape mặc định cone; nhiều giá trị NaN/Infinity có thể qua so sánh range/radius; facing không kiểm normalized; phase lạ về Idle. View gán LastCastId trong Apply trước khi consumer kiểm new cast; chưa có emitted transition/reset lifecycle chứng minh qua consumer.
- **P2 — capability không phải server handshake:** hard-code supported routes có encounter dù alpha disabled; không gắn server source/profile và không phân biệt client biết route với server đang hỗ trợ. Có thể bật UI cho endpoint chưa có.

Phân công sửa và tích hợp thành gói lớn O1..O6 tại work order25; tiếp PR109, không merge vội hoặc mở một protocol khác. Native Godot vẫn Muse; fullbag và encounter HTTP khi thiếu upstream vẫn UNVERIFIED đúng phạm vi.

## Qoder #106

Head mới `42a44914f0f3e8c9bfedcde6aa36a9581f59f5af`. So với 3ed4ef6 đã review, thêm ICombatBossBridge và đường combat tick đánh quest boss, source thay đổi sáu file. CI8 job xanh. Qoder báo 462 self-check, test67 basic casts giết boss và credit qua verified kill; đây là chứng minh in-process, **chưa phải HTTP/Godot full-fight** và Codex chưa chạy lại head này trong lượt giao việc.

Read-model gap chính Qoder ghi nhận: boss trong v2 AOI vẫn targetable:false dù bridge cho owner đánh, snapshot route còn chưa map. Ba câu hỏi packet vẫn ghi chờ owner trong issue41 dù quyết định đã được merge PR108 và gửi issue87. Work order25 chuyển lại đầy đủ approval qua #41/#87, không để đội client chờ vô hạn. Vấn đề owner-instance/shared actor/escort credit trong review trước chưa có bằng chứng đóng ở commit mới; giữ trong cửa nghiệm thu, không khẳng định đã sửa chỉ vì combat bridge CI xanh.

Qoder nhận Q1..Q6: publish schema+wire/read-model đúng, instance isolation, escort, inventory12slot/loot, death-return và trọn quest/unlock bằng private HTTP; gửi fixture sớm để OpenCode/Muse làm song song. Phần SQLite remote và native client không đổi owner. Production vẫn OFF, không tự merge.
