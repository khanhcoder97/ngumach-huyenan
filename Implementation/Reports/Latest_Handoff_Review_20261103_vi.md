# Review bàn giao mới và chuyển tiếp Godot — 03/11/2026

Reviewer: Codex. Phạm vi là exact heads bên dưới; không coi trạng thái CI chung hay lời báo hoàn thành là bằng chứng mọi hệ thống đã tích hợp. Máy reviewer không có Unity/Godot native runtime được kiểm ở lượt này.

| Bàn giao | Head đã xem | Kết luận |
|---|---|---|
| Qoder local #106 | 3ed4ef6c7b5e5686dd96543c2ac270c3c028091a | 461 self-check chạy lại: 461 qua, 0 lỗi; CI 8 job xanh. Nhận checkpoint domain, chưa duyệt merge: còn instance isolation, wave credit và combat HTTP boss |
| OpenCode #103 | 974139f299f57af512c53e8eab78ddc8f767f385 | 73 assertions HTTP chạy lại từ checkout sạch, exit0; 171 portable tests và 9 generator tests đã chạy qua; generator --check qua. Native Unity chưa nghiệm thu; chuyển tiếp portable logic sang Godot, không mở rộng Unity |
| Muse #107 | ed512492b2c8ca34bc5177f50442c459b2eb3256 | Chỉ một report, không có source Godot/assets mới/export; toàn bộ kết quả VM chưa kiểm độc lập. Hướng Godot được tiếp tục theo xác nhận của chủ dự án và đánh giá máy |
| Qoder remote #98 | 5371a4675fbd8fc4b41b4748f2b1732ef2d81824 | Có commit mới, nhưng vẫn không có csproj module/test/harness được tracked. Workflow QR run 41538867743 thất bại; không nhận completion, giữ QR-01 |

## Các phát hiện cần sửa

- **P1 — Qoder boss chưa cô lập:** `AlphaBossEncounterService.StartAttempt`, `Wipe`, `ResolveDefeat` và `DespawnBoss` tác động entity chung từ registry dù có dictionary theo character. Một owner wipe/end/defeat có thể thay life/state của owner khác. Chưa được mở alpha multiplayer trước test 2 instance độc lập.
- **P1 — Qoder escort credit/nguồn:** `ObserveWave` đếm dead state của shared members mà không đối chiếu authoritative killer/instance; `Guid.NewGuid()` trong credit key không giải quyết dedupe. `CommitWaypoint` khi thiếu members đi tiếp, `CompleteIfAtEnd` chỉ kiểm cuối waypoint. Thiếu required wave phải fail activation, không hoàn quest im lặng.
- **P1 — Qoder chưa có đòn người chơi qua HTTP đánh boss:** `ApplyBossDamage` hiện domain-only. Snapshot chưa map; packet được duyệt có sửa trong văn bản riêng. Không gọi domain fixture là end-to-end gameplay.
- **P1 — Remote chưa buildable:** `git ls-tree` ở exact head chỉ có `Server/Health/Health.csproj`; workflow QR tham chiếu `Server/Tests/PersistenceTests/Server.Tests.csproj` thiếu và job `deploy-preview` không tồn tại. Module chưa được biên dịch, các tests trong report chưa được xác minh.
- **P1 — Remote recovery placeholder:** `CrashRecovery.cs` vẫn có integrity trả true, batch mô phỏng và copy primary DB không có quy trình snapshot WAL được chứng minh. Chưa đủ nghiệm thu durability/recovery.
- **P1 — Muse source chưa giao:** #107 không chứa project.godot, scene, source hay actual artifact. HUD Main.tscn, import lạnh, Android và migration 64px còn mở theo chính report. Không gọi client production-ready.
- **P2 — Unity graph của OPC-14 chưa đúng:** asmdef mới bao `Scripts/Online`, nhưng `P1ActorPresenter` dùng `PlayerController2D`/`DirectionalAnimator2D` ở `Scripts/Player` không có asmdef; named assembly không thể dựa vào predefined Assembly-CSharp. Portable tests không biên dịch các Unity types này. Ghi nhận hạn chế lịch sử, không đầu tư thêm native Unity khi hướng đã sang Godot.

## Bằng chứng và giới hạn

- Qoder self-check chạy tại detached checkout 3ed4ef6, log ngoài repo `D:/Project/NGUMACHHUYENAN-tools/dispatch/review-latest-20261103/qoder-self.log`; báo 461 passed, 0 failed. Không đồng nghĩa các lỗi isolation ở trên đã có test.
- 171/171 portable và 9/9 generator kiểm tại worktree OPC-14; ở thời điểm xem worktree có file catalog resource sửa sẵn nên không coi kết quả đó là chứng nhận mọi byte của committed resource. Sau đó tạo checkout sạch riêng exact974139f, chạy `python Client/Tests/PlayerUIAcceptance/run_acceptance.py` với `DOTNET=D:/Project/NGUMACHHUYENAN-tools/dotnet10/dotnet.exe`: server riêng ở loopback/port ngẫu nhiên, **73 HTTP assertions PASS, exit0**, 167 requests/79 POST/3 turnins. Runner dừng server do mình mở. Log tại `D:/Project/NGUMACHHUYENAN-tools/dispatch/review-latest-20261103/opencode-http-runner.log`, artifact chi tiết trong checkout review `TestResults/player-ui-http/`. Fullbag vẫn **UNVERIFIED** vì chưa có seed/capacity contract, không tính 73 là kiểm thử fullbag; đây là HTTP baseline PR103, không phải boss alpha mới hoặc Godot scene.
- PR #106 CI: https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41577227075 ; #103 CI: https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41549668344 ; QR failed: https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41538867743 . Các job xanh server/content của #98/#107 không chạy Godot/persistence mới.
- Không thay root branch của Qoder, không đụng `temp_rgba.png`/`test.png`, không merge các PR code. Nhánh điều phối mới chỉ thêm quyết định/review/work order và cập nhật đầu mối, gửi GitHub và terminal sau khi lưu.

## Quyết định và gói tiếp

Tiếp tục Godot .NET, Compatibility, Windows trước; Android cần build/run thật, C# web chưa được cam kết. Giữ source Unity như lịch sử. Phân vai mới: Muse runtime/scene/art, OpenCode lõi portable/HTTP/integration API, Qoder gameplay, remote persistence. Work order 24 và duyệt encounter gỡ các câu hỏi kỹ thuật đang chờ; không cần đợi thêm một kế hoạch nhỏ mới bắt tay làm. Các cửa production vẫn OFF.
