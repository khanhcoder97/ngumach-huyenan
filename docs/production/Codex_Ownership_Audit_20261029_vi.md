# Phần việc Codex nhận — rà soát 2026-10-29

Baseline đọc source: `18caf223476308cbdabd97d9ee83c90944c87100`. GitHub được kiểm tra trong phiên này; agent có thể tiếp tục commit sau baseline. Đây là phân định và bằng chứng công việc, không là nghiệm thu game hoàn chỉnh.

## Kết luận

Ba agent đang bao phủ server slice, dây chuyền asset và sản xuất hình ảnh/video. Vẫn thiếu chủ thực hiện rõ cho client gameplay kết nối server, biên tập thoại thực tế, audio gameplay, nghiệm thu sản phẩm trên thiết bị và xử lý các quyết định liên ngành. Codex nhận thiết kế/biên tập, review tích hợp và client integration; không lấy lại module server/tooling/art mà agent khác đang làm.

| ID | Phần còn trống / bằng chứng | Codex làm | Đầu ra và điều kiện đóng | Trạng thái đợt này |
|---|---|---|---|---|
| CX-01 | PR #31/#43 và hàng đợi Qoder cần owner review theo head mới nhất; CI xanh chưa chứng minh semantics | Review diff, tests âm tính, compatibility, thay đổi ngoài scope; quyết định merge/sửa | Review gắn exact head SHA, findings cụ thể, kiểm tra liên quan rồi merge | OPEN; không nhận là đã review chỉ vì liệt kê PR |
| CX-02 | QOD-12 report nói không có số HP/ATK/DEF, nhưng Art Bible §12 đã có công thức; MK03 range4,4WU đã có trong DEC-017 baseline nhưng example thiếu | Phân xử nguồn và các câu hỏi cast/VFX; cung cấp bảng đối chiếu và phép tính tham khảo | `P1_Design_Resolution_20261029_vi.md`; Qoder tự mở migration, tests, giữ rollout gate | Đã chỉ rõ nguồn và chốt semantic presentation; runtime còn thuộc Qoder |
| CX-03 | 230 dòng dialogue có câu mẫu, ID máy/tọa độ trong lời NPC, lời kể khẳng định thưởng trước commit | Line-edit tiếng Việt, giọng từng NPC, spoiler, tách hướng dẫn khỏi thoại | Giữ keys/graph/guards/events; 15 dòng P00-01..05 được biên tập, không gọi 76 quest đã polished | 15/230 dòng đã sửa; phần còn lại OPEN |
| CX-04 | Combat spec chỉ mô tả SFX; không có catalog clip gameplay/ambience/music hoặc owner sản xuất audio riêng | Thiết kế soundscape, cue inventory, mixing/accessibility, brief và nghiệm thu nguồn âm | Catalogue cue→trigger→bus→priority→loop/cancel/voice limit, clip/license/source và evidence; thiếu clip ghi missing | OPEN; soundKey trong VFX card chưa là audio asset |
| CX-05 | `TitleBootstrap` chỉ health polling; `PlayerController2D` tự đặt velocity3,2, server default6WU/s; camera chỉ640×360 | Client authoritative integration: transport/session/state reconciliation, HUD actions/quest/inventory, camera profile và reconnect UX | Một đường chơi dùng kết quả server, pending/reject/resync đúng, build Unity từ máy có Editor | Nhận ownership code client; chưa triển khai/compile trong đợt audit |
| CX-06 | Có UI spec nhưng chưa có nghiệm thu đọc chữ tiếng Việt/touch/safe area/subtitle thực tế | UX copy, localization/context/font glyph brief, checklist và review screenshot/device | HUD skill arc, bag/forge/quest/modal ở16:9/20:9, chữ125/150%, nền sáng/tối; bằng chứng build/device | OPEN; Muse vẽ UI, Codex kiểm UX và nối code |
| CX-07 | 349 placement còn review top-down; v2 Thăng Long chưa active | Quyết định tuyến chơi, review footprint/nav/portal và ký gate sau bằng chứng | Bến Mưa đường spawn→quest→boss→portal có path; sign-off riêng từng map | BLOCKED_EVIDENCE; không tự sửa349tọa độ hoặc gắn REVIEWED |
| CX-08 | Có công thức progression/economy nhưng chưa playtest | Thiết kế test build, pacing/TTK/faucet-sink, đo và đề xuất tuning có version | Kịch bản chơi15/30/60phút, số đo và change note; không suy từ công thức ra balance PASS | OPEN |
| CX-09 | Muse sở hữu video/asset nhưng cần review trước nhân rộng | Art direction, contact-sheet/storyboard/native pose review, consistency và defect list | Một vòng sửa rõ theo từng delivery SHA; approved art không đồng nghĩa engine/device verified | CONTINUOUS; giữ #1/#29/#39 |
| CX-10 | Board triển khai cũ nói chưa có server/asset, Codex tiếp quản toàn code | Sửa nguồn điều phối và thứ tự ưu tiên tài liệu | Board mới theo #40/#41 và gói liên tục, ghi runtime/design/evidence tách biệt | Đã cập nhật board và index |
| CX-11 | Qoder scope hiện tại là in-memory P1; auth/durable save/ops chưa nằm trong gói đang chạy | Lập backlog phase sau, contracts/security/persistence acceptance và rollout dependency | Proposal production riêng sau slice, chủ ngân sách/vận hành được chỉ định | OPEN_FUTURE; không âm thầm giao thêm DB/payment vào #41 |
| CX-12 | Hosting/CCU/thị trường/license/voice/monetization cần quyết định sản phẩm | Chuẩn bị phương án và evidence cho chủ dự án; kiểm provenance của gói được giao | Owner thật xác nhận khi có quyết định; không tự ký legal/capacity sign-off | OWNER_DECISION_PENDING; không chặn authoring/local prototype |

## Ranh giới client Codex nhận

Codex phụ trách code transport/session/snapshot/presentation/UI controllers và camera-map flow trong `Client/Assets/Scripts/**` cùng UI code mới; không ghi đè art/manifest/Animator hoặc builder Muse đang sửa ở PR #22. Trước khi nối asset phải thống nhất binding/event manifest. Tốc độ dự đoán lấy server config/snapshot khi contract hỗ trợ, không đổi server6 thành3,2 để khớp demo.

OpenCode vẫn sở hữu #40 và preview tooling, không bị gọi lại làm Unity trên máy yếu. Qoder vẫn sở hữu #41 và contract implementation. Muse vẫn sản xuất asset/source/map/UI/video và Unity demo bằng môi trường của mình. Nếu cần đụng builder/scene của Muse, mở integration request và chia file rõ trước khi sửa.

## Hàng đợi thực hiện của Codex

1. Đợt này: cập nhật board; line-edit15dòng mở đầu; khóa cách diễn giải nguồn P1 và trả lời cast/VFX để giảm chờ.
2. Review các PR đang chờ theo exact head và thay đổi mới; không hứa merge trước khi đọc code/tests.
3. Lập audio cue catalogue và biên tập tiếp thoại các chương; chuẩn bị client adapter từ contract đã merge, không cần chờ art cuối.
4. Khi Muse có Unity build, nối client prototype và nghiệm thu end-to-end/UX. Không coi báo cáo headless hoặc sơ đồ UI là bằng chứng chơi được trên điện thoại.

## Những điều đợt này không chứng minh

Không có build Unity mới, clip audio mới, map reviewed mới, mobile benchmark hoặc full campaign đã chạy. 15dòng copy mới chưa lồng tiếng;230dòng vẫn giữ graph baseline cần exporter và authoritative quest implementation. Quyết định thiết kế không tự bật runtime feature flag.
