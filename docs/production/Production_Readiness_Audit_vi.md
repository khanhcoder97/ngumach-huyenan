# RÀ SOÁT MỨC SẴN SÀNG SẢN XUẤT
## Ngũ Mạch: Huyền Ấn — audit cập nhật 28-10-2026

> Lịch sử baseline 28/10. Dùng [audit 30/10](Production_Content_Audit_20261030_vi.md) cho tình trạng hiện tại:230lời đã biên tập, gói âm thanh đã render, catalog đã đồng bộ và PR server đã tiến thêm. Các backlog/đếm NEW_PROPOSED bên dưới không thay inventory mới hoặc quyết định DEC-023.

### 1. Kết luận

**Chưa đủ để AI triển khai và hoàn thiện toàn game chỉ từ gói hiện tại mà không có thêm dữ liệu/thiết kế.** Tài liệu bao phủ phạm vi rộng nhưng runtime definitions mới có 1 class, 3 skill, 1 quest, 1 item, 1 map, 1 spawn và 1 node. Các catalogue mô tả không thay schema/data executable.

Đọc `Production_Completion_Addendum_vi.md` và `Top_Down_Gameplay_World_Spec_vi.md` trước khi triển khai. DEC-016 chốt góc nhìn từ trên theo chủ dự án; 349 placements giữ ID nhưng chờ review top-down. Báo cáo bằng chứng và backlog tại `Production_Audit_20261028_vi.md`. Các bảng bên dưới là lịch sử baseline, không phải chứng nhận content lock hiện tại.

### 2. Đầu vào production đã được bổ sung

| Miền | Đầu ra hiện có |
|---|---|
| Quyết định chuẩn | DEC-001…014 trong Production_Decision_Register_vi.md; GDD, pixel-art standard, activities, functional spec và data được đồng bộ theo các quyết định này |
| Map/spawn | 349 manifest rows trên 46 map ID: 104 NPC placement, 163 mob groups, 29 boss encounter placements, 35 gather nodes, 18 interactable; gồm 10 anchor BG10 và 6 bãi câu cá |
| Nội tại | 40 passive IDs, 5 lớp × 2 nhánh × 4 node; cấp mở, prerequisite, effect key/value, cap PvP/boss và equip policy |
| Nhiệm vụ/thoại | 76 quest IDs; 230 graph rows: offer/clue/turn-in cho toàn bộ quest và hai lựa chọn C3-05 có flag/next node |
| Boss tuần | 6 slot trỏ tới 6 boss canonical, spawn map/zone/tọa độ, scale, modifier, reward table và weekly cap; altar là interactable, không có boss placeholder runtime |
| Quái/NPC | 9 elite variant profiles dùng sprite-set gốc; 83 NPC canonical có role archetype, prefab/sprite-set/frame animation/palette/portrait/dialogue/service refs |
| Pet/mount/life sim | 5 companion + 5 mount; 5 crop + 6 fish records, farm pocket 5 luống và 6 anchor; level/cooldown/yield/quota/anti-exploit |
| Economy data | Currency registry 16 ID; 221 loot/recipe/reward rows có item/currency ref, group chance, quantity, recipe cost/success, pity/cap/source; mọi currency có ID cấp/tiêu thụ; vé Mạch Triều là item |
| Kỹ thuật/QA | API/event/persistence/idempotency/security/SLO baseline; test matrix và release gates P0–P6 |
| Compendium | Counter được cập nhật tới 2.532 record duy nhất, gồm NPC, pet/mount/fish, passive và hoạt động 10v10 |

**Kiểm tra tính toàn vẹn dữ liệu:** 0 record_id trùng; tất cả map IDs trong Life Sim tồn tại; NPC registry khớp đủ 83 entity canonical; loot-table IDs từ manifest đều có runtime row; item/currency refs hợp lệ; cả 6 weekly boss source IDs đều là boss canonical và có reward table; mọi 16 currency ID có policy và reward/transaction rows; 76 quest có dialogue graph. Bảng tính manifest đã được tái xuất theo 349 hàng.

### 3. Các mâu thuẫn trước đây đã khóa

| Chủ đề | Giá trị chuẩn |
|---|---|
| Engine/art | Unity 6.3 LTS, C#, URP 2D, Pixel Perfect Camera, Tilemap; pixel-art standard 640×360 logical/20 PPU/integer scale |
| Raid | 2 raid × 3 encounter; 2 encounter objective/add và 1 boss cuối mỗi raid |
| PvP 10v10 | BG10 riêng trên geometry Trấn Sơn; mở cấp 36 sau C3-01; 120s reconnect; PvP template thống nhất; cosmetic-only rewards |
| Reconnect | Session/encounter 120s; Long Môn tournament riêng 1 lần/90s |
| Reset | Daily 05:00; weekly thứ Hai 05:00 Asia/Ho_Chi_Minh; UTC scheduler |
| Escort C2-03 | 90s; checkpoint/resume tại từng van |
| Passive | 8 node/lớp; mở tự động cấp 20/40/60/80; không có passive point; equip tối đa 2 |
| Boss Tháp tuần | sourceBossId canonical từ roster sáu boss; schedule lưu boss thực |
| Farm/fishing | farm pocket 5 luống, 12 output/day; 6 fishing spots, 20 catches/day; cap theo account |

### 4. Còn phải hoàn thành trước content lock/release

1. **Duyệt blockout:** 130 vị trí trong manifest vẫn mang trạng thái NEW_PROPOSED. Level design phải kiểm camera, collision, nav/path, độ đọc telegraph và thời gian chạy trên scene thực rồi ký duyệt.
2. **Tạo asset:** 83 dòng NPC registry và 9 elite profiles là chỉ dẫn cho archetype/sprite set, không phải sprite sheets, tilemaps, animation frames hoặc VFX đã hoàn tất. Cần sản xuất pixel concepts, spritesheets, tiles, frame tables, VFX/SFX, icon, portrait và kiểm quyền sử dụng.
3. **Narrative copy:** dialogue graph có toàn bộ quest IDs, state và bản thoại tiếng Việt baseline. Narrative owner cần line-edit, pacing, lựa chọn, subtitle/voice localization và kiểm tra chiều dài text trên UI.
4. **Cân bằng:** loot/recipe/reward tables có initial numeric config để import; cần mô phỏng economy faucets/sinks, XP/cost curve, class parity, drop/pity và playtest rồi mới khóa tuning.
5. **Phê duyệt sản phẩm/ops/legal:** region hosting và CCU target; retention/privacy theo thị trường; moderation staffing; monetization/store/payment; ngôn ngữ/voice; trademark/title và license media. Baseline không pay-to-win, Vietnamese-only prototype, không dùng asset chưa clearance.
6. **Triển khai và nghiệm thu:** dựng Unity/backend/CI, importer, scene, API thật, bảo mật, load/soak/recovery, migration và ký các gate P0–P6. QA matrix là kế hoạch; chưa thể được coi là test đã chạy.

### 5. Handoff đề nghị

Bắt đầu/hoàn thiện P0 theo AI_Agent_Implementation_Plan_vi.md, gồm Pixel Perfect camera/import preset/smoke scene; sau đó làm vertical slice Bến Mưa. Dùng Production_Technical_Contracts_vi.md và CSV làm schema/import source. Trước khi mở rộng nội dung, ký duyệt map placements trong slice và đo performance trên PC/mobile mục tiêu. Sau đó triển khai P2–P5 theo release gates; khóa các phê duyệt bên ngoài trước alpha/release.

**Phán định cập nhật:** tiếp tục vertical slice có kiểm soát; chưa đạt content lock/P1 end-to-end/release. Các gate chờ nằm trong báo cáo 2026-10-28.
