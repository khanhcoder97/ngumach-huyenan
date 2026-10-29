# Chương trình phát triển liên tục — 2026-10-29

Qoder cập nhật ngày2026-10-30: đọc `08_QODER_PLAYABLE_SLICE_20261030.md` cho quyết định sáu câu hỏi QOD-16 và gói QOD-16pha2→20. Các giới hạn ownership/review/production gate của chương trình vẫn giữ nguyên.

Cập nhật thứ tự và các gói lớn sau kiểm tiến độ: đọc `07_NEXT_LARGE_MILESTONES_20261029.md` cùng work order này. Review transaction Qoder, migration OpenCode và gate art/Unity Muse vẫn có hiệu lực; chưa có evidence thì chưa được gọi là hoàn tất.

Yêu cầu chủ dự án: giao tác vụ lớn, không kết thúc công việc sau một nhiệm vụ nhỏ. Văn bản này bổ sung và ưu tiên hơn backlog P1 cũ trong work order 00–03; không chứng nhận game đã hoàn thiện.

## Trách nhiệm và đích bàn giao

| Người phụ trách | Gói công việc | Kết quả cần chạy được |
|---|---|---|
| OpenCode | OPC-06 → OPC-10, công cụ và dây chuyền asset | Từ bundle Muse đến kiểm tra, xem trước và gói bàn giao tái tạo được, không cần Unity |
| Qoder | QOD-11 → QOD-15, vòng chơi authoritative | Headless scenario tạo phiên → di chuyển → tương tác/chiến đấu → tiến triển nhiệm vụ → nhận thưởng đúng một lần |
| Muse | ART-REV-01, MAP-01, UI-01, VFX-01, CINEMA-01 | Bộ hình ảnh đầu game nhất quán, native pixel và preview engine khi có; từng gate được review trước nhân rộng |
| Codex | Review, concept, quy chuẩn, điều phối và merge | Quyết định tích hợp cụ thể, kiểm chứng báo cáo, gỡ phụ thuộc và review từng PR |

## Cách làm không dừng sau mỗi PR

1. Mỗi agent comment nhận cả gói, branch/worktree riêng, thứ tự các mốc và phần đang làm. Ghi một checklist duy nhất tại issue gói việc.
2. Đọc main mới nhất và review cũ trước khi sửa. Giữ thay đổi dở và PR đang mở; không reset checkout chung. Không dùng cùng working directory với agent khác.
3. Chia một gói lớn thành các PR có thể review. Khi mở PR, tiếp tục mốc độc lập kế tiếp hoặc tests/docs/fixtures của mốc sau; không trả lời “xong, chờ giao tiếp” nếu còn việc được giao.
4. Khi mốc sau phụ thuộc code chưa merge, dùng nhánh stacked từ PR trước và ghi rõ base/dependency. Không sao chép file thủ công giữa các agent, không tự merge. Rebase lên main sau merge bằng thao tác giữ được thay đổi.
5. Nếu schema/contract/art approval chặn một phần: mở proposal kèm ví dụ pass/fail và câu hỏi cụ thể; tiếp tục phần độc lập. Không bỏ guard, giả asset hoặc tự đánh dấu REVIEWED để vượt blocker. Nếu tất cả mốc thực sự bị chặn, báo từng blocker và bằng chứng; không bịa tiến độ.
6. Cập nhật issue khi có PR, mốc hoàn tất, thay đổi kế hoạch hoặc blocker. Mỗi cập nhật ghi SHA, lệnh kiểm tra và mốc tiếp theo. Nếu phiên agent bị kết thúc/giới hạn công cụ, để lại checkpoint và lệnh tiếp tục; giao việc không bảo đảm agent tự chạy nền mãi.
7. Không tự mở rộng thành auth/payment/market live hoặc thay gameplay balance. P1 in-memory, fixture và concept phải giữ nhãn tương ứng. Mọi owner review/CI gate vẫn áp dụng.

## Quyền sửa được mở rộng cho chương trình này

- OpenCode: `Implementation/Asset_Handoff/**` (gồm schema migration có proposal và fixtures), `Implementation/Tools/AssetPipeline/**`, `Tools/AssetPreview/**`, `.github/workflows/asset-handoff-validation.yml` và workflow mới `asset-pipeline-*`. Có thể ghi proposal `OPC-*` và report `OPC-*`. Không sửa runtime asset của Muse, `Server/`, P1 network contract hay loader gameplay. Schema migration phải được review trước khi yêu cầu Muse chuyển version.
- Qoder: phạm vi server/contracts/runtime/tools hiện có. Thêm report/proposal `QOD-*`, test và CI server liên quan. Không sửa art, asset schema/validator của OpenCode hoặc thiết kế production. Không ghi đè script của agent khác; request tích hợp qua issue.
- Muse: phạm vi art/source/Unity builder đã giao, cộng cinema sidecar theo #29. Không sửa authoritative gameplay hoặc schema thay OpenCode. Báo yêu cầu metadata qua issue.
- Codex duy trì các work order điều phối và tài liệu thiết kế. Các bảng ownership cũ được hiểu cùng phần mở rộng này, không dùng bảng cũ để dừng các việc đã giao mới.

### Phần Codex nhận sau rà soát ownership

Theo `docs/production/Codex_Ownership_Audit_20261029_vi.md`, Codex nhận client gameplay integration (transport/session/snapshot/UI controllers/camera flow), biên tập thoại, audio direction và QA/review tích hợp. Không ghi đè art/Animator/manifest/builder Muse hoặc lấy lại module server/tooling đã giao. Trước sửa scene/builder của Muse phải chia file và integration request rõ. Thiếu Unity local thì source chưa được gọi là compile/playback PASS; dùng build evidence trên máy phù hợp khi có. Các câu hỏi cast/VFX và nguồn numeric P1 đọc `P1_Design_Resolution_20261029_vi.md`; Qoder vẫn thực hiện migration/implementation qua PR riêng.

## Chuẩn chung hiện hành

Top-down XY, foot pivot, actor 48×64 native, 20 PPU, tile 16×16, Point/no mipmaps. Combat camera 640×360 logical; HUB_WIDE 960×540 logical theo `Hub_Wide_Camera_Profile_vi.md`, không thu nhỏ nút cảm ứng. Thăng Long 2048×1536 WU là quy hoạch design-only; không tự thay bounds runtime trước migration. Sáu ô kỹ năng bố trí vòng cung quanh nút đánh.

Không gọi static metadata PASS là Unity playback PASS; không gọi HTTP smoke PASS là MMORPG production-ready. Mốc cuối mỗi gói cần báo phần chạy được, phần fixture và phần còn thiếu.

## Thứ tự phối hợp

Issue giao cả gói: OpenCode #40, Qoder #41; Muse duy trì #1 (umbrella), #29 (cinema), #39 (VFX). Các issue là thông báo công việc thực tế, không chỉ file local.

OpenCode hoàn thiện PR #31 trước, rồi OPC-06/07/08/09/10 theo work order mới. Schema #33 phải sửa công thức sai trước khi triển khai. Qoder tiếp nối QOD-10 đã merge; ưu tiên vòng chơi đầu game, không bắt đầu từ full 30 skill hay toàn bộ 46 map.

Muse giữ gate 3 pose nhân vật trước khi nhân rộng animation; song song phần độc lập là blockout Bến Mưa, UI, storyboard và mẫu VFX. Qoder không chờ hình hoàn thiện để viết domain tests; OpenCode không chờ Unity để làm preview và kiểm tra metadata. Thiếu topology REVIEWED thì chỉ chạy scenario dev/synthetic và giữ quest accept production OFF.
