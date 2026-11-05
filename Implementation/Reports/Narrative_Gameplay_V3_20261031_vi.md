# Gameplay narrative v3 — kết quả tích hợp ngày 2026-10-31

Branch `codex/story-gameplay-integration-20261031` ghép các dependency được ghim: Antigravity `94fb605`, workshop `28cee7a`, Qoder `f2649f3`. Hai merge conflict chỉ ở coordination/gitignore được giải bằng giữ cả cập nhật owner và quy tắc output. Không sửa checkout root của Qoder, không tự merge toàn stack vào main.

## Đã triển khai

- Viết lại prose cho đủ 36 main/40 side, xuất 229 node và 104 NPC bindings. Giữ CSV lịch sử, node IDs/conditions, objectives, rewards, flags và canonical XY. Nguồn v3 có digest/source hashes; resource và bản đọc Markdown cùng sinh từ exporter, kiểm drift trong CI.
- Core `P1NarrativeFlow` đọc world/quest qua P1Client thật, kiểm entity/map/instance/floor/range, phân trang và reply cục bộ. Nút nhận/nộp gọi API hiện có; không chạy event CSV hoặc Ink giả lập khi đọc. Cảnh sau nộp đợi receipt và inventory readback. Close, skip và reply không grant.
- HUD gắn overlay trên đúng document được inject, nối input gate/Esc và dispose subtree của mình. NPC không bị gửi vào endpoint interact dành cho parcel/node. TitleBootstrap hỗ trợ local config riêng cho profile DEV, default v1 được giữ để tương thích.
- Launcher `Tools/Gameplay/run_narrative.py --configure-client` build và chạy backend DEV, tạo local config nếu chưa có. Cổng đang dùng và profile đã có được giữ nguyên; không kill process hoặc sửa appsettings production. Profile bật quest/CombatV2/CombatDamage, MobBehavior OFF.
- Reading room thêm selector xem 76 nhiệm vụ v3 để biên tập, ghi rõ đang xem mọi giai đoạn, không là tiến độ tài khoản. Browser render/select C5-03 và screenshot đã kiểm.

## Bằng chứng thực chạy

| Kiểm tra | Kết quả |
|---|---|
| Narrative policy bằng core P1Client | 24 PASS |
| Concrete HTTP trong checkout tích hợp | 23 PASS |
| Core/audio/input/v2 assertions hiện có | 55 + 43 + 15 + 46 = 159 PASS |
| C# syntax Unity | 49 files × 3 profiles, 0 lỗi; không phải Unity type/import |
| Content / contracts | 8 definition schemas và 20 contract schemas/examples hợp lệ |
| Narrative production | 76 quest beats, 20 scenes/63 shots, references hợp lệ |
| CSV lịch sử | 197 mới + 33 giữ nguyên = 230 dòng; logic/order/choices không đổi |
| Workshop Ink cũ | 38 reachable nodes, 2398 edges, replay/reveal/evidence/reset PASS |
| Export | narrative_nodes v1 và dialogue v3 không drift |
| Browser v3 | load/select76/read C5-03 và unknown/traversal404 PASS |

HTTP đi bộ thật từ spawn tới Ly An, nhận qua overlay core, đi qua ba kiện và interact thật, tới Tạ khi READY. Transport cố ý làm mất phản hồi turn-in sau khi server đã xử lý; cảnh sau nộp chưa mở. Retry giữ nguyên request body/key; receipt được xác nhận, túi đọc lại có đúng 20 Đồng và một `EQ-MK-CHEST-T1-R-COMMON` stack1. Skip/close rồi đọc lại vẫn một grant và inventory revision không tăng. Server riêng cổng động, chỉ dừng process do runner tạo. JSON/log lưu cùng report; binary/resource hash đi kèm. Chạy ở integration HEAD trước commit nội dung; CI sẽ tái lập trên exact head được push.

## Giới hạn và blocker được giữ rõ

P00-01 đã qua HTTP; native Unity6000.3.17f1 import/playmode/layout/font/input chưa được chạy tại máy này, cần Muse VM. P00-02..05 còn source-blocked; chương sau mới có prose, chưa có toàn bộ graph/event/runtime. Không claim 76 quest đã executable. Hạ Mặc/Sầm ở Thăng Long và dynamic master cần phase binding; không tự clone actor hoặc dời placement.

CHOICE C3-05 có điều kiện CSV quá rộng (ACTIVE) so với yêu cầu sau boss. Export ghi requiredCheckpoint và catalog chưa cho chọn node ấy khi chưa có feed checkpoint được review; không cấp flag qua reply local. Video chưa được tạo/phát live bởi thay đổi này; bản thảo/cinema pack còn theo ownership Muse.

Probe ban đầu tìm ra hai yêu cầu tích hợp: v1 snapshot không có NPC; v2 cần bật route. Ở Qoderf2649f3, CombatDamageOFF còn trả mobALIVE/targetable vớiHP0 khi vàoAOI. Đã giao finding choQoder; giữ validationclient, profile nghiệm thu bật damage để cóHP projection hợp lệ nhưng tắt mobAI. Không coi OFF-profile đã sửa.

Mở thêm reader8127 bị automatic review chặn với lý do `blocked by policy`; không khởi chạy hoặc kill service để vượt chặn. Reader8126 của người dùng giữ nguyên. Bản Markdown đầy đủ và source v3 vẫn được bàn giao trong repository. Browser smoke dùng process tạm của riêng nó và đã hoàn tất.

Chưa có độc giả độc lập hoặc diễn viên duyệt văn. “Viết lại đủ nội dung” chỉ nói coverage của lượt prose v3, không chứng nhận mọi phân cảnh đã đạt chất lượng cuối cùng hoặc game hoàn chỉnh.

## Sửa lệch giữa các nhánh khi chạy CI tích hợp

CI headf881f65 đã qua narrative-client-HTTP và các kiểm tra client/server, nhưng pipeline nội dung báo transcription lock/coverage drift. Đã đọc diff hai nguồn thay đổi: QuestDefinition thêm activation bắt buộc và blockedSteps; exampleP00-01 chỉ thêm ACTIVE/formatting, toàn bộ targets/counts/rewards/unlocks giữ nguyên. Cập nhật hai hash sau đối chiếu, thêm bốn unresolved activation cho full-design candidates thay vì suy ACTIVE từ runtime subset. Gate ngoài tiếp tục OFF; snapshot21/4ready/17blocked/60unresolved. Candidate tests28PASS, gồm hai ca mới chống bỏ field/gate. Build/check generated candidates cùng coverage42evidencefiles được cập nhật, không sửa số liệu hoặc bật bốn quest blocked.

Checkout sparse ban đầu có ảnh fixture/art dưới dạng LFS pointer; đã hydrate bốn ảnh dùng để kiểm coverage/map/preview. Không thay asset hoặc ảnh bằng bản tự tạo để làm qua validator. Các lỗi local do pointer được phân biệt với drift thật trên GitHub (CI đã checkoutLFS). CI sau commit compatibility sẽ tái chạy toàn bộ pipeline; không lấy kết quả headf881 có một job đỏ để ghi tất cả PASS.
