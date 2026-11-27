# Khóa mục tiêu và phản hồi chiến đấu — 06/11/2026

## Phạm vi bàn giao

Tiếp PR123, hoàn thiện phần Godot do Codex sở hữu: thao tác khóa mục tiêu, bảng trạng thái, trình bày chuyển động quái và phản hồi combat theo dữ liệu server. Không đổi Core OpenCode, backend Qoder, vị trí spawn, phần thưởng hay hợp đồng wire. Tutorial/boss/portal đầy đủ vẫn ở checkpoint review riêng.

## Chức năng

- Đóng panel khôi phục HUD và vùng bấm ngay, vẫn tôn trọng chế độ ẩn HUD. Pointer runner đợi control hiện trước khi bấm.
- Nhấp hình quái sống để khóa; Tab đổi lần lượt các quái hợp lệ trong viewport, Shift+Tab đổi ngược. Chuột phải trên map hoặc × trên bảng bỏ khóa. Vùng HUD/panel chặn xuyên click; HUD ẩn không chiếm vùng bấm. Không tự chọn NPC, quái chết, hình chưa được ánh xạ hoặc quái ngoài màn hình. Khóa tay đã có được giữ khi đi xa trong AOI, đến khi không còn hợp lệ.
- Bảng giữa trên màn hình có tên, HP hiện tại/tối đa, khoảng cách canonical và trạng thái thực. Minimap có viền hình thoi; marker chân đi cùng vị trí nội suy. Không tự đi vào tầm hoặc tự đánh liên tục. Đòn đánh/skill có mục tiêu xoay aim về tọa độ mục tiêu trong snapshot.
- Khóa được xóa khi chết, mất khỏi snapshot, lifeId thay đổi, đổi session/instance/floor/phase. Snapshot cũ cùng context không rollback actor. Quái/NPC nội suy vị trí đã nhận, reset khi đổi life/context hoặc warp lớn; không ngoại suy AI.
- Tên và thanh máu gần nhau ưu tiên mục tiêu đang khóa. Không dời tọa độ hoặc giãn quái tại client để che spawn chồng nhau. Các hình unresolved vẫn là việc art/catalog cần tiếp tục, không tự gán sai loài.
- Flash, số damage/chí mạng, trượt, miễn nhiễm và hấp thụ chỉ xuất hiện từ event hợp lệ cho đúng map/floor/life. Cache event giữ cửa sổ 1024 cursor, cho phép đến lệch thứ tự trong cửa sổ, không phát lại event cũ sau khi dọn cache. Context/cancel dọn cả cue guard và feedback tạm; số feedback có giới hạn 24, chế độ ít hiệu ứng 8.
- Cast gây damage kết thúc không có impact/miss báo không trúng mục tiêu; cancel báo chiêu bị ngắt. Guard/dash không bị gán là đòn hụt. Không giả geometry/telegraph, damage hoặc giảm HP tại client.

## Kiểm thử

| Kiểm tra | Kết quả | Nguồn bằng chứng |
|---|---|---|
| Godot .NET build | PASS, 0 warning/error | client_build.log |
| Target fixture headless | PASS 29 assertion | target_self_test.log |
| Target fixture renderer native + PNG | PASS 30 assertion | target_native_fixture.log, target_fixture.png |
| Real native combat + HTTP | PASS 19 assertion | combat.godot.stdout.log, combat.run.json |
| Camera/scene/visual/quest UI/motion regression | PASS 48/9/15/30/538 | client_regressions.log |
| P00-01/guard native regression | PASS 134 assertion | ui.run.json, ui.godot.stdout.log |

Tất cả đường dẫn bằng chứng trong Implementation/Reports/Evidence/Target_Combat_20261106. Fixture có nhãn rõ, dùng DTO/source và pointer injection, không HTTP/grant; ảnh fixture không phải combat đã chạy.

Combat native dùng session bình thường spawn x18, đi qua public move tới bờ khô gần x84,y3 theo địa hình authored, không teleport hay spawn fixture. Pointer event đi qua handler thật để chọn Cá Linh; Tab đổi member; basic có CAST_START, IMPACT/END và HP giảm từ server; Kiếm Trận tiêu MP, có cooldown và nhiều event trúng/trượt thật. Bấm lặp lúc hồi không tiêu thêm tài nguyên. Bỏ khóa xóa cả bảng; inventory không được thêm loot/quest reward. Test không ép RNG: basic có thể trượt, runner đợi END và thử lại tối đa 5 lần.

Backend chọn mục tiêu trong cone theo khoảng cách/ID và giới hạn số mục tiêu, không bảo đảm targetId khóa là con duy nhất trúng nếu spawn đứng chồng. Runner có kiểm Tab rồi chọn lại member gần nhất để đối chiếu HP; không sửa cơ chế backend hay hạ assertion để giả thành exact-target damage. Hiệu ứng hiện ở targetId của event thực.

## Hiệu năng

Native online, session HTTP thật, target HUD bật tại khu Cá Linh, nhân vật đứng yên, MobBehavior OFF, Compatibility/OpenGL 3.3/1280×720, GeForce820M. Stopwatch warmup3s + lấy mẫu12s:

- 713 frame / 12.0241s: **59.30 FPS** trung bình.
- Median 16.650ms, p95 19.030ms.
- 163.9 draw call/frame, texture 321.2 MiB, 942 node.

Số gốc: performance_combat.json, ảnh chụp sau phép đo: performance_combat.json.png. Actor đứng yên không ghi lại transform/color/ring mỗi physics tick. Đây không phải phép đo chiến trường đông người, AI truy đuổi hoặc mọi hiệu ứng cùng lúc. Mục tiêu vẫn60FPS, không cam kết mọi frame luôn60. Các ảnh PNG chụp liên tiếp có thể hiện FPS HUD thấp vì encode/lưu đồng bộ; không dùng counter trong gallery làm benchmark.

## Chạy lại

- ClientGodot/Choi_Ben_Mua.cmd: chơi thường, điều khiển mới có sẵn.
- ClientGodot/Run_Playable_Alpha.ps1 -CombatTest -EvidenceDirectory <thư mục riêng>: native combat + profile, server riêng do launcher sở hữu và dọn đúng PID.
- Godot --headless --path ClientGodot -- --target-self-test
- Godot --path ClientGodot -- --target-self-test --capture <đường dẫn PNG tuyệt đối>
- ClientGodot/Run_Playable_Alpha.ps1 -MotionTest -EvidenceDirectory <thư mục riêng>: luồng nhiệm vụ/guard hiện hành.

## Các phần tiếp tục thuộc gói khác

Mob AI và death-return vẫn OFF trong launcher. Chưa có geometry/telegraph authoritatively mô tả trong P1ModelsV2 hiện dùng; không tự vẽ vùng nguy hiểm giả. Bộ quái hiện giữ source idle/attack/dead trước đó, chưa nâng mọi quái lên8 hướng16frame. Tự động nhặt đồ, loot/XP mới, toàn tutorial/boss, portal và campaign phải tích hợp sau khi checkpoint backend/Core tương ứng vượt review.
