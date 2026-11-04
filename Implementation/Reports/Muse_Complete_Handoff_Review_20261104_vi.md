# Review hoàn chỉnh bàn giao Muse — 04/11/2026

## Kết luận và phạm vi được nhận

**Nhận M-A ở mức source prototype có thể build/import/render; yêu cầu sửa trước khi approve merge PR111 hoặc nghiệm thu alpha. PR112 cần chỉnh tài liệu trước merge.** Không phủ nhận phần Muse đã làm: source thật, assets LFS thật, camera top-down, HUD vòng cung, tilemap và animation legacy chạy được trên máy yếu. Chưa đạt giao game online đầy đủ hoặc gói Windows portable đã kiểm máy không SDK.

Đã review exact heads #111 `765a0d62ac597b8b9fbc07ae2a5a89a8a1f60b46` và #112 `bf75cc784123292657458ccc867738a4f8d06b9e`; kiểm source/scenes/tooling/assets/engine docs và chạy độc lập Windows. Không sửa source runtime của Muse. Godot tự bổ sung các trường mặc định trong .import ở checkout review; không commit thay đổi phát sinh đó lên nhánh Muse.

## Bằng chứng độc lập

| Mục | Kết quả và giới hạn |
|---|---|
| .NET build | SDK8.0.404, cache NuGet mới, local LFS feed, locked restore:0error/7obsoletewarnings; SDK10 cũng build được |
| Import | Cold Windows99,9s; warm SDK8 14,19s; exit0 nhưng có EditorSettings shutdown error, chưa log sạch |
| Native offline | 8/8suite PASS theo exitcode+marker; SELFTEST có8resourceERROR do4NPC placeholder thiếu |
| Online v1 | Server riêng Qoder42a4491: NETTEST PASS; ONLINETEST FAIL hai lần ở hai ngưỡng thời gian khác nhau |
| Renderer Windows | Godot4.7.2 Compatibility/OpenGL3.3 chạy trên GeForce820M; frame1280×720 đã xem. Không phải nghiệm thu export hoặc FPS tải MMO |
| Assets | 71PNG/52.847.262byte hydrate; sprite khớp frame48×64 hiện tại; không nhận đây là bộ64×64 mới |
| Map/evidence | 450×60cell/360×48WU hiện thực, blocked5069unique;306ô nước có nguồn delta rõ,37ô bờ giữ đi được; chưa chứng nhận mọi đường/anchor |

Raw logs, JSON, capture và helper tái lập: `Implementation/Reports/Evidence/Muse_20261104/README_vi.md`. Bộ test10/10 Muse báo trên VM không được tái lập trọn vẹn trên Windows; kết quả đầu9/10 và retest online thất bại vẫn được giữ.

## Phát hiện cần sửa

### F1 — P1: bàn phím bị khóa sau khi dùng joystick

`Main.cs:126/131` gọi SetMoveInput khi kéo và thả joystick. `PlayerController2D.cs:32/68` giữ `_inputInjected=true` tới khi ClearInjectedInput được gọi; Main không gọi nó khi trả quyền cho keyboard. Producer diagnostic trên engine: D sau trạng thái release di chuyển0px, sau ClearInjectedInput di chuyển21,33px. Sửa ownership input khi release/focus loss và test chuyển touch→keyboard→touch, không chỉ test injected controller riêng.

### F2 — P1 đối với alpha: entry scene không có world collision/online journey

`project.godot` chạy Main.tscn. Main đặt map Sprite2D, không BenMuaTilemapBuilder/TileMapLayer; producer đếm0TileMapLayer. Health poll không tạo session; movement offline, NPC4placeholder bị thiếu, chưa có quest/inventory/combat/portal thực. Không thay TileMap bằng một ảnh để nghiệm thu map. Được giữ scene này làm diagnostic offline có nhãn rõ; entry sản phẩm phải dùng map collision thật và cùng authoritative flow.

### F3 — P1: “online combat” hiện chỉ animation và cooldown local

`OnlineMain.cs:107..121` chỉ PlayAction; GameServerClient chỉ health/session/world/move, không gửi cast/skill/quest/inventory. `Hud.cs:389/467` tự bắt đầu cooldown4/6/8/10/12/15s trước khi server xác nhận; BagPresses chỉ tăng counter, quest/sample EXP35% hard-code. Những điều này hợp lệ trong demo có nhãn, chưa phải game online. Nối Shared client/API thật; rejected/uncertain cast không được tự tiêu cooldown/MP hoặc granthit/reward.

### F4 — P1: online test phụ thuộc thời gian và chưa portable

Lần đầu wall-slide dx8,35/dy−1,06 vượt|dy|≤0,9; retest wall-slide đạt nhưng north dy6,65 vượt≤6,6. Code dùng Task.Delay + khoảng kỳ vọng cố định trong khi server tích phân elapsed time, queue và render phụ thuộc lịch chạy. Cần assertions theo intent/snapshot/tick/hình học và điều kiện hoàn thành có timeout, không chỉ nới ngưỡng để PASS. Đây là vấn đề test chưa ổn định; chưa kết luận server/physics sai chỉ từ các chênh lệch này.

### F5 — P1: runner có thể dừng server không thuộc mình và che lỗi

`test.sh:48..57` dùng cổng5000 cố định, health không xác minh instance, `fuser -k5000/tcp` dừng mọi process trên cổng. Pipeline build/scene lọc grep RESULT, online thiếu env có thể SKIPPED rồi trả0. Phải giữ exitcode, rawlog, mode online-required và child PID cleanup. Không chạy script gốc này trên máy người dùng; review đã dùng helper an toàn riêng.

### F6 — P1 của đường Android: LFS/feed/restore/import chưa được chứng minh

Workflow checkout không bật LFS; repo có nupkg LFS nhưng script dùng `-f` làm điều kiện sẵn sàng, pointer có tên đúng cũng bị coi là package. Bootstrap chỉ5gói khác manifest16; import có `||true`. Chưa có APK artifact và launch proof để nghiệm thu. Kiểm file ZIP/hash, locked dependency closure, build/import fail-fast và phân biệt BUILD_APK/INSTALL/LAUNCH/PLAYABLE. Windows test package cũng chưa có artifact được review; cross-export report không thay máy không SDK.

### F7 — P2: tools asset phụ thuộc đường dẫn VM và provenance chưa đúng

Converters/builders dùng Path.home()/workspace/your_files/godot-prototype. Người clone không có source art hoặc path đó để dựng lại atlas/portrait/detail; binaries chạy được không đồng nghĩa art pipeline tái lập. Chuyển sang args/repo-relative source manifest+hash hoặc ghi rõ step nào cần Art_Source chưa bàn giao. `PACKAGES.md` nói nupkg không ở Git nhưng16gói có LFS tracked; manifest gọi sprite64×64 trong khi native cắt và file thực tế48×64. Sửa đúng phiên bản/status, không tự nâng DRAFT/Geometry thành RELEASE/REVIEWED.

### F8 — P2: UI còn trạng thái demo và dữ liệu chờ nối

Ảnh native cho thấy arc quanh attack đúng hướng, world đọc được và tiếng Việt hiển thị. Quest/BAG/EXP còn sample/hard-code, skill4..6 không có gameplay, NPC không thấy vì loại art không license. Cần bind view state, hover/focus/touch và safe-area, numericHP/MP/EXP/localization; alpha có thể dùng font fallback đủ dấu. Không chờ một font pixel mới để dừng code, cũng không tuyên bố fallback là font mỹ thuật đã duyệt.

### F9 — P2: DEC024 còn quy định Unity mâu thuẫn

PR112 sửa engine đúng hướng nhưng AI_Agent_Implementation_Plan P0 vẫn yêu cầu URP17.3/PixelPerfectCamera và prompt cuối còn “Giữ Unity6.3”; audio spec còn meta/GUID/loadType như bắt buộc Godot. Bảng vai trò vẫn OpenCode chỉ asset pipeline và Codex toàn client. Cần đổi đúng các đoạn quy định hiện hành, giữ lịch sử không sửa hàng loạt. Duy trì portable Core/Presentation đang được Shared link là ngoại lệ rõ của việc đóng băng Unity presentation.

### F10 — P2: codec cinema phải có bản runtime Godot

MP4 H.264 vẫn dùng review/master, nhưng core Godot VideoStreamPlayer dùng Ogg Theora; không mặc định MP4 chơi được nếu không có extension. Quyết định runtime .ogv, đường dẫn và gate nằm trong work27; không cài plugin video mới chỉ để né dependency. Nguồn chính thức: https://docs.godotengine.org/en/stable/tutorials/animation/playing_videos.html .

## Quyết định tiếp theo cho Muse

1. Tiếp Godot4.7.2.NET/Compatibility, Windows trước; không đổi engine hoặc bỏ công đã làm. M-A nhận partial; M-B/M-C/M-D chưa hoàn.
2. Giữ PR111 làm dòng bàn giao runtime, sửa F1/F4/F5/F6 trước checkpoint tiếp. Cho phép pin source Shared/Qoder trên branch tích hợp thử, không phải chờ merge toàn stack; không tự merge production hoặc sửa server/schema.
3. Entry alpha phải online hoặc offline có nhãn rõ, dùng tilemap/collision thật. Nối P00-01 end-to-end trước, tiếp boss/equipment/deathreturn khi wire có; preview không cấp thưởng.
4. Duyệt chặn đúng306ô nước và giữ37ô bờ theo quyết định PR113, kích hoạt sau nav/hash/footbox/anchor-path kiểm đồng bộ Qoder; không mở lại câu hỏi đã trả lời hoặc tự sửa canonicalplacements.
5. Cho dùng bộ48×64 hiện tại chỉ làm bridge prototype;64×64 là migration có manifest/frame-count/pivot thật và gate art riêng. Không viết lại asset đã được khóa để sửa lỗi runtime.
6. PR112 sửa normative leftovers/ownership và codec delivery; nguồn engine đã chốt, không chờ owner quyết lại. Đường cinema runtime `ClientGodot/assets/cinematics/<cinemaId>/`, OGV+poster; master/source ở Art_Source, metadata/SRT ở Narrative/Deliveries.
7. Triển khai trọn work order27: runner/regression → main online+UI → map/assets/cinema → Windows package/device evidence. Không dừng sau một fix hoặc sau ACK.
