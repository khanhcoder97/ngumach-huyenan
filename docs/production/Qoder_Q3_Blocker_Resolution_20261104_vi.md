# Trả lời Qoder: XP, loot, inventory v2 và encounter

Ngày 04/11/2026. Chủ dự án yêu cầu Codex trả lời trực tiếp các blocker Qoder vừa nêu. Quyết định này **có hiệu lực triển khai ngay**, không chờ một lần owner approval khác. Đây là bổ sung mới cho phần làm tròn XP; không tuyên bố văn bản cũ đã quy định chi tiết đó. Nguồn máy đọc: `Implementation/Content/DesignBaselines/ben_mua_q3_decisions_20261104.json`.

## 1. XP — chốt làm tròn xuống

Với level nguyên L được chụp tại accept commit: `N(L) = 100 + 50*L + 25*L*L`; `normalXP = floor(N(L)*25/100)`, `bossXP = floor(N(L)*55/100)`. N(L) là tổng XP cần cho bước level đó, **không phải phần XP còn thiếu của người chơi**. Dùng số nguyên checked/64-bit theo range đã validate, không floating-point rounding/banker's rounding.

Chụp acceptedLevel, base, tỷ lệ và kết quả trong quest attempt khi accept thành công; turnin/retry sau level-up vẫn dùng cùng kết quả, chỉ grant một lần theo receipt. Reward tuyệt đối đã có trong source thắng công thức, giữ nguyên reward=0; không tự thêm mức XP tối thiểu. Ví dụ level1 N175 → thường43/boss96; level2 N300 →75/165; level3 N475 →118/261. Thiếu snapshot trong dữ liệu cũ phải xử lý migration rõ ràng hoặc từ chối trường hợp không đủ dữ liệu, không lặng tính lại tại turnin.

## 2. Loot — default OFF là yêu cầu vận hành, không cấm implement grant

Giữ `defaultGrantEnabled=false` và mọi default production OFF. **Duyệt triển khai grant path**, chỉ cho phép chạy thực khi cả ba điều kiện thỏa: AlphaProfile.Enabled, explicit private alpha profile, và flag mới `P1:AlphaLoot:GrantEnabled=true`. Flag mới mặc định false. Test private CI được bật có chủ đích; profile/default public không bị thay đổi.

Khi tắt: dry-run receipt không trả coin/item và không trở thành khoản chờ cấp. Khi bật: dùng band/recipe/rule đã duyệt trong DESIGN-BM-ALPHA, roll-once key hiện hành theo owner/death/life/group, inventory+receipt/ledger phải commit atomically trong authoritative runtime. Retry cùng kill không reroll hoặc nhân thưởng. Bật flag sau một dry-run **không backfill** cái chết cũ; phải có eligible death mới. Nếu provider durable chưa được review, nói rõ in-memory alpha; không tự nối SQLite chưa nghiệm thu.

## 3. Inventory v2 — đã chọn migration song song, không mở enum v1

**Giữ nguyên enum đóng 5 token của wire v1. Duyệt tạo DTO/schema/enum v2 riêng với đúng 12 slot** HAT, CHEST, LEGS, WEAPON, GLOVES, BOOTS, NECK, RING_L, RING_R, PENDANT, CLOAK, SEAL; bag100. Các route đã duyệt: GET `/p1/inventory/v2/{sessionId}`, POST `/p1/inventory/v2/equip`, POST `/p1/inventory/v2/unequip`. Không sửa enum của schema v1 và không nhét token mới vào response v1.

Cùng inventory aggregate authoritative, revision/replay nhất quán; v1 vẫn chạy trên dữ liệu biểu diễn được theo hợp đồng cũ. Nếu trạng thái v2 không biểu diễn được ở v1, trả lỗi/version capability rõ ràng theo contract P1 được công bố, không silently bỏ bảy slot. Không downgrade/copy inventory thành hai kho riêng. Keep-current-absolute HP/MP rồi clamp, không heal, không auto-swap và không mất item khi túi đầy. Qoder được implement schema/examples v2, gửi fixture/error/field map sớm cho OpenCode/Muse; không cần xin duyệt lại số slot hoặc lựa chọn side-by-side.

## 4. Encounter — packet đã được duyệt kèm sửa

`Encounter_Snapshot_Review_Decisions_20261103_vi.md` đã merge PR #108; work order25 đã nhắc lại. Ba câu hỏi trả lời rõ: ID server cấp cho character+questAttempt giữ qua wipe, **không late join**, **owner-only**. Được implement current/detail GET, bổ sung castId/stateEndsAtTick/locked facing, atomic snapshot, giữ CombatEventV2 đóng. Gate OFF không map route; kiểm HTTP status thật, thông thường404. Đọc toàn văn để sửa instance isolation/escort credit và typed fields; không đánh dấu còn chờ owner duyệt packet này.

## 5. Cách làm tiếp

Qoder nhận trọn work order25 Q1..Q6: publish encounter+v2 schema/fixtures đầu tiên, đồng thời implement XP/grant/inventory/death-return/full quest; chờ review một checkpoint thì tiếp phần độc lập. Gửi ACK và artifact tại #41/#87/PR106. Các số task nội bộ #93/#94 trong tin nhắn của Qoder không được dùng để suy ra GitHub issue cùng số: GitHub #94 hiện là PR review Antigravity cũ, nên phản hồi được gửi đúng các đầu mối Qoder đang làm.
