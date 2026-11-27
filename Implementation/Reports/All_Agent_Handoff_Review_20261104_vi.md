# Review tất cả nhân sự — 04/11/2026

## Kết quả theo source đã nhận

| Nhân sự | Bàn giao đã kiểm | Kết luận |
|---|---|---|
| OpenCode | #109 e351e81d58168b3df85a378f7956d1c32efbe782 | Chạy lại **61/61 unit tests, 0 skipped**; có composition/sample/runner mới. HTTP CI **FAIL**, wire encounter vẫn lệch packet; chưa nhận O1..O6 complete |
| Muse | #111 765a0d62ac597b8b9fbc07ae2a5a89a8a1f60b46 | Đã có source ClientGodot/project/scenes/scripts/lockfile và assets LFS thật; nhận bàn giao source từng phần. HUD Main và thẻ class disabled có code. Full gameplay chưa nối; native 10/10/export là Muse báo cáo, Codex chưa chạy engine |
| Muse docs | #112 bf75cc784123292657458ccc867738a4f8d06b9e | DEC024 đổi engine đúng hướng; cần sửa bảng vai trò theo phân công hiện tại và ngoại lệ portable source trong Client; chưa tự merge main |
| Qoder local | #106 42a44914f0f3e8c9bfedcde6aa36a9581f59f5af | Không có commit mới so lượt trước; snapshot/instance/inventory/death-return/full chain chưa nghiệm thu. Blocker XP/loot/v2 đã được trả lời bằng quyết định mới |
| Qoder remote | #98 5371a4675fbd8fc4b41b4748f2b1732ef2d81824 | Không có bàn giao mới; tracked csproj vẫn chỉ Health. Workflow QR thiếu project và needs deploy-preview; chưa nghiệm thu persistence |

Antigravity vẫn thu hồi theo yêu cầu trước; không nằm trong danh sách được giao trở lại. Không thay root branch của Qoder hoặc file temp_rgba.png/test.png.

## Các lỗi tiếp tục chặn nghiệm thu

**OpenCode P1:** `run_http.py` dùng ROOT lên ba parent trong khi Shared/ClientCore.HttpRunner chỉ cách repo root hai cấp. CI run41622410580 thất bại MSB1009 trỏ `/home/runner/work/ngumach-huyenan/Server/Health/Health.csproj` (thiếu thư mục repo lồng). Sau sửa root, job còn cần SDK10 cho Health net10 thay vì chỉ setup8. Nguồn log: https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/41622410580 .

**OpenCode P1:** DTO/parser vẫn dùng shape.center, registration, arena rectangle, cooldowns/npcId khác packet. Parser từ chối top-level questId/bossRecordId của reference đúng. ClientSession tạo Guard nhưng chưa nối nó vào mọi đường áp state; Relogin reset SessionGeneration về0, không hủy CTS epoch cũ và không xử lý ambiguous mutation trước khi thay client. Sample vẫn StubTransport và chưa có typed encounter HTTP API cho Muse. Không merge chỉ vì 61 tests tự viết qua.

**Muse P1:** `test.sh` khởi động server cổng cố định5000 rồi `fuser -k 5000/tcp` có thể giết process không thuộc runner; không chạy script này trên máy người dùng. Pipeline build/suite chỉ grep RESULT và có thể qua khi online suites bị skip; cần kiểm exit code, mode online-required và child PID riêng. Android workflow chỉ bootstrap5 package khác danh sách16, không checkout LFS đầy đủ ở bước checkout hiện tại, có import `|| true`; chưa có APK run proof. Source scripts chỉ shell Linux, chưa đủ gói Windows chạy máy yếu.

**Muse P2:** Main là scene offline với HUD mặc định; OnlineTest có snapshot riêng nhưng chưa có quest/inventory/combat journey tích hợp Shared. Không tính việc gắn HUD vào Main là full online gameplay. Review default Compatibility/nearest là đúng hướng. Code còn 48×64 cũ; 64px, NPC/quái/boss/VFX/style2/cinema còn checklist.

**Muse docs P2:** PR112 board vẫn ghi Codex trực tiếp sở hữu toàn client gameplay, OpenCode chỉ asset pipeline. Điều này trái phân công work24/25: Muse Godot runtime, OpenCode portable core, Codex review/tích hợp. Câu giữ nguyên Client/ không phát triển tiếp cần giới hạn Unity presentation, cho phép duy trì portable Core/Presentation đang được Shared link trong thời kỳ chuyển tiếp.

## Quyết định để gỡ chờ

- XP floor tại accept, loot opt-in private alpha và inventory v2 enum riêng đã ghi `Qoder_Q3_Blocker_Resolution_20261104_vi.md` + JSON decision, đã gửi trực tiếp Qoder #41/#87/PR106.
- Reference payload encounter chung và quyết định chặn306ô có điều kiện nav/hash/path được ghi `Integration_Reference_And_Water_Decisions_20261104_vi.md`. Ảnh evidence đã được xem, không auto gắn topology reviewed.
- PR110 (work25) đã merge vào nhánh tích hợp sau8checks xanh, merge dbaa6e7. Các PR code109/106/111 chưa merge; PR112 cần sửa ownership trước. Work26 giao tiếp trọn gói cho bốn vai trò.

TRX độc lập OpenCode ở `D:/Project/NGUMACHHUYENAN-tools/dispatch/review-20261104/opc15-tests/opc15-e351e81.trx`, chạy target net8 qua SDK10 roll-forward; không chứng minh native Godot. Không chạy lại tests của source Qoder/remote không đổi để tạo cảm giác có tiến độ mới.
