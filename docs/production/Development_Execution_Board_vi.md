# Bảng điều phối triển khai — Ngũ Mạch: Huyền Ấn

Cập nhật 2026-10-29. Đọc `Codex_Ownership_Audit_20261029_vi.md` và `Implementation/Work_Orders/04_CONTINUOUS_DELIVERY_20261029.md` trước các report cũ. Đây là board hiện hành; các audit có ngày trước là bằng chứng tại thời điểm đó.

## Phân vai hiện hành

| Luồng | Chủ thực hiện | Đầu ra / ranh giới |
|---|---|---|
| Authoritative server | Qoder, issue #41 | QOD-11→15: world/movement/combat/quái/quest/reward/headless; không art hoặc asset validator |
| Dây chuyền asset không Unity | OpenCode, issue #40 | OPC-06→10: schema/PNG/meta/preview/pack/CI; không gameplay client/server |
| Art/source/video | Muse, #1/#29/#39 | nhân vật, map, UI art, VFX, animation, cinema; Unity demo/builder trên máy của Muse |
| Client gameplay integration | Codex | code transport/state/UI presentation/camera flow, không ghi đè art/Animator/builder Muse; compile/playback phải có môi trường Unity |
| Thiết kế/biên tập/QA tích hợp | Codex | nguồn chuẩn, thoại, audio direction, UX, review PR/art, quyết định liên ngành và evidence gates |
| Quyết định phát hành | Chủ dự án | thị trường, budget/hosting/CCU, vận hành, monetization, clearance/đối tác; không ghi giả owner sign-off |

Quyền sửa chi tiết theo work order04 và audit ownership; ba agent không bị giao lại nhiệm vụ nhỏ sau mỗi PR. Agent mở PR rồi tiếp mốc độc lập/stacked hoặc tests, giữ review gate và báo blocker cụ thể.

## Bằng chứng hiện có và giới hạn

- Đã có server session/move/world, quest accept có flag, topology/LOS/swept geometry, world entity registry và combat target binding. Baseline đọc đợt này `18caf22` (PR #47); code và PR sau đó phải xem head mới nhất, không dùng board làm chứng nhận test tự động.
- Đã có asset validator và Muse walk delivery; vẫn cần review metadata/visual/Unity evidence. PR #22 có full-animation proposal không có nghĩa128clip đã đạt nghiệm thu.
- Có concept nhân vật/environment/HUD, Thăng Long macro và5board30skill. Đây là references/design handoff, không phải runtime assets hoàn chỉnh.
- 76 quest có narrative beats;20cinema/63shot có prompt. Video và quest executable không tự tồn tại vì có prompt/ID.
- 349placements/46map chờ mức review khác nhau; không có bằng chứng đủ toàn bộ topology/collision/route. Thăng Long2048×1536WU là target design-only.
- PC local không chạy Unity Editor; không gọi static source review là client build PASS. Server CI build/smoke không là mobile or full-game acceptance.

## Hàng đợi Codex

1. Chốt source/semantic P1 và sửa thoại mở đầu; xem `P1_Design_Resolution_20261029_vi.md`, `Opening_Dialogue_Editorial_Notes_vi.md`.
2. Review PR #31/#43 và các PR Qoder đang chờ theo head mới; merge/sửa theo diff và bằng chứng, không theo tên workflow xanh đơn thuần.
3. Audio cue catalogue, biên tập tiếp các chương, UX/localization/font/accessibility review; những phần này chưa có agent sản xuất riêng.
4. Client session/state/transport adapter → HUD/quest/inventory actions → binding animation/VFX → camera profile/reconnect presentation; mỗi bước có review và integration request nếu liên quan Muse/Qoder.
5. Nghiệm thu Bến Mưa trên Unity/device khi có build, đo pacing/TTK/UX; chưa chuyển sản xuất đại trà46map khi slice chưa qua.

## Chuẩn và gate

Top-down XY; actor48×64/8hướng/20PPU; tile16×16; Point/no mipmap. Combat640×360logical, HUB_WIDE960×540logical theo DEC-021; HUD giữ size,6ô kỹ năng vòng cung quanh nút đánh. Không đổi speed/range/hitbox theo sprite frame.

Exit slice: tạo nhân vật → P00-01..05 (talk/explore/collect/combat/escort/boss) → thưởng không nhân đôi → cổng Thanh Lạc; client đọc authoritative state, không mất tiến trình khi reconnect, telegraph rõ ở LowFX, UI dùng được16:9/20:9. In-memory P1 không đạt durable reconnect chỉ bằng retry test; persistence phải được xây và kiểm riêng trước khi ký gate đó.

P2–P6 vẫn theo `Production_QA_Release_Gates_vi.md`. Audio, reviewed topology, client runtime, durable save/auth, activity systems và device QA còn thiếu; không gọi game hoàn chỉnh từ số trang đặc tả.
