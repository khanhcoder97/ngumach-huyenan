# Gói33 — chương trình lớn sau review gói32

Chủ dự án yêu cầu tiếp tục review và giao các gói việc lớn tiếp theo. Gói này giao toàn chuỗi, không thay các mốc32 chưa xong bằng lời báo hoàn tất. Baseline integration đã nhận PR128 tại `6f79853172578d755b29033997150d79bf4c4f7d`: node/binding approval và policy owner hiện có ngay trên nhánh tích hợp. Không chờ merge tài liệu mới bắt đầu feature branch.

| Owner | Epic mới | Mốc đầu và đích cả gói |
|---|---|---|
| OpenCode LOCAL | work34 / OPC-17→20 | đóng conformance32 → client portable đủ vòng chơi, state lifecycle, presenters, typed services, media bridge, adoption/CI |
| Qoder local | work35 / QOD-30→36 | finale32 → cấp11 thật, capacity/consume/stat, combat5class, economy/discovery/social có nguồn và acceptance nhiều owner |
| Qoder Remote | work36 / QR-01→03 | R1 project build/test → atomic persistence, two-process fencing/crash/recovery/outbox, adapters và restart proof |
| Muse | work37 / MEDIA-03→05 | mixed campaign21entry, motion/continuity, music/SFX/VO toàn gói, reproducible runtime/media QA |
| Codex | review/integration | nhận subset có pin, ghép Godot/native, giữ graphics/UI/UX/VFX/camera/input và kiểm gameplay thật |

Các work order34–37 là nhiệm vụ đang giao trọn gói, không chỉ backlog đề xuất. Giao checkpoint đủ review theo artifact; chờ một approval/module thì tiếp phần độc lập. Không tạo đường code giả hoặc route trả cứng để đổi trạng thái bảng tiến độ. Không tự mở production, merge PR gameplay/media, đổi model/auth, reset/stash/clean worktree khác. Muse chỉ media, Antigravity không nhận việc. Scope compiler/content-pipeline đã thu hồi trước đây không tự trả OpenCode.

## Thứ tự và tích hợp

1. P0 trước: OpenCode wire/confirmed refusals/paired runner; Qoder finale→portal, MAP_VIEWED/escort đã duyệt; Remote buildable source; Muse soundtrack metadata/clean runtime. Chỉ đóng mốc đã có bằng chứng. Review mới ở `Implementation/Reports/Review_20261108_Next/Agent_Review_vi.md` ghi exact heads và phạm vi.
2. Trong lúc P0 được review, triển khai domain/parser/typed read models/fixtures độc lập của các mốc sau, không dừng cả gói. Public route mới cần schema/example/refusal/validator trước handler, rồi consumer tests. Content/runtime mới có provenance/version và đúng vocabulary; old frozen world/combat enums không mở lén.
3. `Inventory_And_Progression_Execution_Decisions_20261108_vi.md` + JSON source duyệt capacity100stack-slots, inventory_full, consumeHP/MP và source-backed effective stats private-alpha. Đây là quyết định kỹ thuật/luật có nguồn, không phải thông báo đã chạy được. Các packet liên quan không còn chờ owner cho những điểm đã trả lời.
4. Paired checkpoint phải nêu clientHead/serverHead/contentVersion và SDK, logs/TRX/assertion>0. Giao payload capture có consent source, không secret. Unit console không là native; in-memory không là durable; byte/codec không là nghe hoặc final picture.
5. Không yêu cầu merge cả PR103→109, server stack cũ hoặc media1250file một lượt. Codex chọn patch/package/source closure đã review. Mỗi epic phải có dependency graph và khả năng tái tạo từ clone sạch, kèm feature/capability matrix thực.

## Nhịp giao nhận

ACK issue owner với branch/head/checkpoint đang code, rồi push artifact đầu. Sau mỗi checkpoint cập nhật actual changes, command/output/CI, module còn blocked và nguồn cần; tiếp milestone kế. Không chỉ đăng lại cùng ACK hoặc tăng số report/cue/catalog. “Đã đăng assignment” và “agent đang chạy” là hai trạng thái khác nhau.

Issue nhận việc giữ nguyên: OpenCode#85, Qoder#87 đồng bộ#41, Remote#79, Muse#116, điều phối#4. Không cần mở chat/sidebar hoặc phục hồi agent bị thu hồi. Nếu tool/môi trường không có, gửi lệnh/lỗi cụ thể để điều phối, không claim test đã chạy.
