# Triển khai phòng biên kịch và bản mẫu Bến Mưa — 2026-10-31

Theo yêu cầu dùng bộ công cụ viết/biên tập để cải thiện cốt truyện. Đã cài4community skills qua helper chính thức, pin commit; tạo skill riêng ngumach-narrative trong repo và local Codex. Cả5đều qua skill validation. Bỏ đúng field model-invocable không hỗ trợ trong2skill; bản gốc và SOURCE giữ tại skill folder. Không chạy bootstrap/hook hoặc đổi credential/model/global AGENTS. Skill khả dụng từ lượt tiếp theo.

Đã cài portable Ink1.2.1 và Inky0.15.2 ngoài repo, kiểm release SHA256 đúng GitHub. Inky GUI chưa được mở/kiểm; compiler chính thức đã compile bản mẫu. npm inkjs2.4.0 được pin/integrity lock, compiler/runtime browser hoạt động không cần Unity hoặc API model. Clone khác dùng scripts/README để tái tạo; không commit binary editor.

## Nội dung đã viết

P00-01–P00-05 có18cảnh truyện và8checkpoint mô phỏng, không còn giới hạn bản thảo ở3node. Các nhánh phản hồi hội tụ theo quest đã chốt. Bản thảo tạo nhịp giữa giữ hàng, quan sát nước, hai lời kể, hộ tống và mảnh ấn. Có cử chỉ/đạo cụ/quan hệ được diễn trong cảnh, giọng Ly An/Tạ riêng và journal knowledge/custody ledger. Không tăng quota chữ để chứng nhận chất lượng.

Nguồn `.ink` và bản screenplay đầy đủ ở `docs/narrative/workshop/`. Trong reader, note kỹ thuật ẩn mặc định, lựa chọn mô phỏng có nhãn, có thể đổi tuyến/đọc lại/xuất feedback kèm source digest. Không gọi server game, không tạo reward/Trust/unlock.15shot/4cinema giữ source IDs/timing, có chỉ đạo performance/sound cho Muse. CIN_004 ở pre-combat, không gán sai cho cảnh tên mảnh ấn sau boss.

## Kiểm tra thực thi

- inkjs build/check không warnings; source NFC và generated/canon drift có kiểm.
- Node runtime:26scene/checkpoint nodes reachable;2280choice edges trên947decision states,28explicit ends; read lại và gate tên Huyền Ấn PASS. Đây là state merging trong một prototype sticky-choice, không tuyên bố bao phủ vô hạn vòng đọc.
- Official inklecate1.2.1 build và cùng branch assertions PASS; compiler output được lưu scratch ngoài source.
- Chrome thật: load story và click một choice qua Ink runtime PASS; route ngoài allowlist/traversal404. Screenshot `Narrative_Workshop_Preview_20261031.png`. Server smoke tự dừng; reader dành người dùng riêng đang ở http://127.0.0.1:8126 với PID thuộc tool này.
- Canonical content8schemas và P1contracts11schemas PASS; CSV/349placements/runtime source không sửa.
-5skills quick validation PASS. Bản thảo được Codex tự đọc/sửa hai lượt; chưa có independent/human editorial approval, nativeUnity/livegame/video playback chưa nghiệm thu.

## Bàn giao và phần cần nối

`INTEGRATION_AND_CANON_vi.md` phân biệt staging mới với canon: luân chuyển thư, pose người cứu, optional replies, pause sau clear, seal interaction và class confirmation. Những guard này chưa là code server. Consumer cần mapping localization/line IDs và contract events riêng; không thay dialogue CSV bằng file Ink. Bản thảo chưa tự mở rộng cả76quest. Mẫu này đặt giọng và quy trình cho phần tiếp theo, phải đánh giá bằng đọc cảnh chứ không bằng AI score.

Lệnh và hashes nằm ở README/tool lock/JSON report. Đầu vào không cần Unity hoặc LFS art/audio để viết; dependencies vẫn độc lập game client. Báo cáo này xác nhận công cụ và bản thảo có thể đọc/chạy thử, không chứng nhận game hoàn thiện hay văn chương được người chơi duyệt.
